import struct
from struct import pack, unpack
from random import randint
from time import sleep
from defs import FJReadFjmException, FJWriteFjmException
from typing import BinaryIO, List, Tuple, Any

"""
struct {
    u16 fj_magic;   // 'F' + 'J'<<8  (0x4a46)
    u16 word_size;  // in bits
    u64 version;
    u64 segment_num;
    { // for versions > 0
        u64 flags;
        u32 reserved;   // 0
    }
    struct segment {
        u64 segment_start;  // in memory words (w-bits)
        u64 segment_length; // in memory words (w-bits)
        u64 data_start;     // in the outer-struct.data words (w-bits)
        u64 data_length;    // in the outer-struct.data words (w-bits)
    } *segments;            // segments[segment_num]
    u8* data;               // the data
} fjm_file;     // Flip-Jump Memory file
"""

fj_magic = ord('F') + (ord('J') << 8)
reserved_dict_threshold = 1000

header_base_format = '<HHQQ'
header_base_size = 2 + 2 + 8 + 8

header_extension_format = '<QL'
header_extension_size = 8 + 4

segment_format = '<QQQQ'
segment_size = 8 + 8 + 8 + 8

SUPPORTED_VERSIONS = {0: 'Normal', 1: 'Full'}
# TODO UPCOMING_VERSIONS = {2: 'Zipped', 3: 'RelativeZipped', 4: '7Zipped', 5: 'RelativeZipped'}


class Reader:
    def __init__(self, input_file, *, slow_garbage_read=True, stop_after_garbage=True):
        self.slow_garbage_read = slow_garbage_read
        self.stop_after_garbage = stop_after_garbage

        with open(input_file, 'rb') as fjm_file:
            try:
                self._init_header_fields(fjm_file)
                self._validate_header()
                segments = self._init_segments(fjm_file)
                data = self._read_data(fjm_file)
                self._init_memory(segments, data)
            except struct.error as se:
                raise FJReadFjmException(f"Bad file {input_file}, can't unpack. Maybe it's not a .fjm file?") from se

    def _init_header_fields(self, fjm_file: BinaryIO) -> None:
        self.magic, self.w, self.version, self.segment_num = \
            unpack(header_base_format, fjm_file.read(header_base_size))
        if self.version == 0:
            self.flags = self.reserved = 0
        else:
            self.flags = self.reserved = unpack(header_extension_format, fjm_file.read(header_extension_size))

    def _init_segments(self, fjm_file: BinaryIO) -> List[Tuple]:
        return [unpack(segment_format, fjm_file.read(segment_size)) for _ in range(self.segment_num)]

    def _validate_header(self):
        if self.magic != fj_magic:
            raise FJReadFjmException(f'Error: bad magic code ({hex(self.magic)}, should be {hex(fj_magic)}).')
        if self.version not in SUPPORTED_VERSIONS:
            raise FJReadFjmException(
                f'Error: unsupported version ({self.version}, this program supports {str(SUPPORTED_VERSIONS)}).')
        if self.reserved != 0:
            raise FJReadFjmException(f'Error: bad reserved value ({self.reserved}, should be 0).')

    def _read_data(self, fjm_file: BinaryIO) -> List[int]:
        read_tag = '<' + {8: 'B', 16: 'H', 32: 'L', 64: 'Q'}[self.w]
        word_bytes_size = self.w // 8

        # TODO read file once:
        # data = []
        # while True:
        #     word = fjm_file.read(word_bytes_size)
        #     if word == '':
        #         break
        #     data.append(unpack(read_tag, word)[0])

        file_data = fjm_file.read()
        data = [unpack(read_tag, file_data[i:i + word_bytes_size])[0]
                for i in range(0, len(file_data), word_bytes_size)]
        return data

    def _init_memory(self, segments: List[Tuple], data: List[int]):
        self.memory = {}
        self.zeros_boundaries = []

        for segment_start, segment_length, data_start, data_length in segments:
            for i in range(data_length):
                self.memory[segment_start + i] = data[data_start + i]
            if segment_length > data_length:
                if segment_length - data_length < reserved_dict_threshold:
                    for i in range(data_length, segment_length):
                        self.memory[segment_start + i] = 0
                else:
                    self.zeros_boundaries.append((segment_start + data_length, segment_start + segment_length))

    def __getitem__(self, address):
        address &= ((1 << self.w) - 1)
        if address not in self.memory:
            for start, end in self.zeros_boundaries:
                if start <= address < end:
                    self.memory[address] = 0
                    return 0
            garbage_val = randint(0, (1 << self.w) - 1)
            garbage_message = f'Reading garbage word at mem[{hex(address << self.w)[2:]}] = {hex(garbage_val)[2:]}'
            if self.stop_after_garbage:
                raise FJReadFjmException(garbage_message)
            print(f'\nWarning:  {garbage_message}')
            if self.slow_garbage_read:
                sleep(0.1)
            self.memory[address] = garbage_val
        return self.memory[address]

    def __setitem__(self, address, value):
        address &= ((1 << self.w) - 1)
        value &= ((1 << self.w) - 1)
        self.memory[address] = value

    def bit_address_decompose(self, bit_address):
        address = (bit_address >> (self.w.bit_length() - 1)) & ((1 << self.w) - 1)
        bit = bit_address & (self.w - 1)
        return address, bit

    def read_bit(self, bit_address):
        address, bit = self.bit_address_decompose(bit_address)
        return (self[address] >> bit) & 1

    def write_bit(self, bit_address, value):
        address, bit = self.bit_address_decompose(bit_address)
        if value:
            self[address] = self[address] | (1 << bit)
        else:
            self[address] = self[address] & ((1 << self.w) - 1 - (1 << bit))

    def get_word(self, bit_address):
        address, bit = self.bit_address_decompose(bit_address)
        if bit == 0:
            return self[address]
        if address == ((1 << self.w) - 1):
            raise FJReadFjmException(f'Accessed outside of memory (beyond the last bit).')
        l, m = self[address], self[address+1]
        return ((l >> bit) | (m << (self.w - bit))) & ((1 << self.w) - 1)


class Writer:
    def __init__(self, output_file, w, *, version=0, flags=0):
        if w not in (8, 16, 32, 64):
            raise FJWriteFjmException(f"Word size {w} is not in {{8, 16, 32, 64}}.")
        if version < 0 or version >= 1 << 64:
            raise FJWriteFjmException(f"version must be a 64bit positive number, not {version}")
        if flags < 0 or flags >= 1 << 64:
            raise FJWriteFjmException(f"flags must be a 64bit positive number, not {flags}")
        if version == 0 and flags != 0:
            raise FJWriteFjmException(f"version 0 does not support the flags option")

        self.output_file = output_file
        self.word_size = w
        self.version = version
        self.flags = flags
        self.reserved = 0

        self.segments = []
        self.data = []  # words array

    def write_to_file(self):
        write_tag = '<' + {8: 'B', 16: 'H', 32: 'L', 64: 'Q'}[self.word_size]

        with open(self.output_file, 'wb') as f:
            f.write(pack(header_base_format, fj_magic, self.word_size, self.version, len(self.segments)))
            if self.version > 0:
                f.write(pack(header_extension_format, self.flags, self.reserved))

            for segment in self.segments:
                f.write(pack(segment_format, *segment))

            for word in self.data:
                f.write(pack(write_tag, word))

    def add_segment(self, segment_start, segment_length, data_start, data_length):
        if segment_length < data_length:
            raise FJWriteFjmException(f"segment-length must be at-least data-length")
        self.segments.append((segment_start, segment_length, data_start, data_length))

    def add_data(self, data):
        start = len(self.data)
        self.data += data
        return start, len(data)

    def add_simple_segment_with_data(self, segment_start, data):
        data_start, data_length = self.add_data(data)
        self.add_segment(segment_start, data_length, data_start, data_length)

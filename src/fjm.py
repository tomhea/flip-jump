import struct
from enum import IntEnum
from pathlib import Path
from struct import pack, unpack
from time import sleep
from typing import BinaryIO, List, Tuple, Dict

import lzma

from exceptions import FJReadFjmException, FJWriteFjmException


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
    } *segments;        // segments[segment_num]
    u8* data;       // the data (might be compressed in some versions)
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

BaseVersion = 0
NormalVersion = 1
RelativeJumpVersion = 2     # compress-friendly
CompressedVersion = 3       # version 2 but data is lzma2-compressed
SUPPORTED_VERSIONS = {
    BaseVersion: 'Base',
    NormalVersion: 'Normal',
    RelativeJumpVersion: 'RelativeJump',
    CompressedVersion: 'Compressed',
}

_LZMA_FORMAT = lzma.FORMAT_RAW
_LZMA_DECOMPRESSION_FILTERS: List[Dict[str, int]] = [{"id": lzma.FILTER_LZMA2}]


def _LZMA_COMPRESSION_FILTERS(dw: int, preset: int) -> List[Dict[str, int]]:
    return [{"id": lzma.FILTER_LZMA2, "preset": preset, "nice_len": dw}]


class GarbageHandling(IntEnum):
    Stop = 0
    SlowRead = 1
    OnlyWarning = 2
    Continue = 3


class Reader:
    def __init__(self, input_file: Path, *, garbage_handling: GarbageHandling = GarbageHandling.Stop):
        """
        The .fjm-file reader
        @param input_file: the path to the .fjm file
        @param garbage_handling: how to handle access to memory not in any segment
        """
        self.garbage_handling = garbage_handling

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
        if BaseVersion == self.version:
            self.flags, self.reserved = 0, 0
        else:
            self.flags, self.reserved = unpack(header_extension_format, fjm_file.read(header_extension_size))

    def _init_segments(self, fjm_file: BinaryIO) -> List[Tuple]:
        return [unpack(segment_format, fjm_file.read(segment_size)) for _ in range(self.segment_num)]

    def _validate_header(self) -> None:
        if self.magic != fj_magic:
            raise FJReadFjmException(f'Error: bad magic code ({hex(self.magic)}, should be {hex(fj_magic)}).')
        if self.version not in SUPPORTED_VERSIONS:
            raise FJReadFjmException(
                f'Error: unsupported version ({self.version}, this program supports {str(SUPPORTED_VERSIONS)}).')
        if self.reserved != 0:
            raise FJReadFjmException(f'Error: bad reserved value ({self.reserved}, should be 0).')

    @staticmethod
    def _decompress_data(compressed_data: bytes) -> bytes:
        try:
            return lzma.decompress(compressed_data, format=_LZMA_FORMAT, filters=_LZMA_DECOMPRESSION_FILTERS)
        except lzma.LZMAError as e:
            raise FJReadFjmException(f'Error: The compressed data is damaged; Unable to decompress.') from e

    def _read_data(self, fjm_file: BinaryIO) -> List[int]:
        read_tag = '<' + {8: 'B', 16: 'H', 32: 'L', 64: 'Q'}[self.w]
        word_bytes_size = self.w // 8

        file_data = fjm_file.read()
        if CompressedVersion == self.version:
            file_data = self._decompress_data(file_data)

        data = [unpack(read_tag, file_data[i:i + word_bytes_size])[0]
                for i in range(0, len(file_data), word_bytes_size)]
        return data

    def _init_memory(self, segments: List[Tuple], data: List[int]) -> None:
        self.memory = {}
        self.zeros_boundaries = []

        for segment_start, segment_length, data_start, data_length in segments:
            if self.version in (RelativeJumpVersion, CompressedVersion):
                word = ((1 << self.w) - 1)
                for i in range(0, data_length, 2):
                    self.memory[segment_start + i] = data[data_start + i]
                    self.memory[segment_start + i+1] = (data[data_start + i+1] + (segment_start + i+1) * self.w) & word
            else:
                for i in range(data_length):
                    self.memory[segment_start + i] = data[data_start + i]
            if segment_length > data_length:
                if segment_length - data_length < reserved_dict_threshold:
                    for i in range(data_length, segment_length):
                        self.memory[segment_start + i] = 0
                else:
                    self.zeros_boundaries.append((segment_start + data_length, segment_start + segment_length))

    def __getitem__(self, address: int) -> int:
        address &= ((1 << self.w) - 1)
        if address not in self.memory:
            for start, end in self.zeros_boundaries:
                if start <= address < end:
                    self.memory[address] = 0
                    return 0

            garbage_val = 0
            garbage_message = f'Reading garbage word at mem[{hex(address << self.w)[2:]}] = {hex(garbage_val)[2:]}'

            if GarbageHandling.Stop == self.garbage_handling:
                raise FJReadFjmException(garbage_message)
            elif GarbageHandling.OnlyWarning == self.garbage_handling:
                print(f'\nWarning:  {garbage_message}')
            elif GarbageHandling.SlowRead == self.garbage_handling:
                print(f'\nWarning:  {garbage_message}')
                sleep(0.1)

            self.memory[address] = garbage_val

        return self.memory[address]

    def __setitem__(self, address: int, value: int) -> None:
        address &= ((1 << self.w) - 1)
        value &= ((1 << self.w) - 1)
        self.memory[address] = value

    def bit_address_decompose(self, bit_address: int) -> Tuple[int, int]:
        address = (bit_address >> (self.w.bit_length() - 1)) & ((1 << self.w) - 1)
        bit = bit_address & (self.w - 1)
        return address, bit

    def read_bit(self, bit_address) -> int:
        address, bit = self.bit_address_decompose(bit_address)
        return (self[address] >> bit) & 1

    def write_bit(self, bit_address, value) -> None:
        address, bit = self.bit_address_decompose(bit_address)
        if value:
            self[address] = self[address] | (1 << bit)
        else:
            self[address] = self[address] & ((1 << self.w) - 1 - (1 << bit))

    def get_word(self, bit_address) -> int:
        address, bit = self.bit_address_decompose(bit_address)
        if bit == 0:
            return self[address]
        if address == ((1 << self.w) - 1):
            raise FJReadFjmException(f'Accessed outside of memory (beyond the last bit).')
        lsw, msw = self[address], self[address+1]
        return ((lsw >> bit) | (msw << (self.w - bit))) & ((1 << self.w) - 1)


class Writer:
    def __init__(self, output_file, w, version, *, flags=0, lzma_preset=None):
        if w not in (8, 16, 32, 64):
            raise FJWriteFjmException(f"Word size {w} is not in {{8, 16, 32, 64}}.")
        if version not in SUPPORTED_VERSIONS:
            raise FJWriteFjmException(
                f'Error: unsupported version ({version}, this program supports {str(SUPPORTED_VERSIONS)}).')
        if flags < 0 or flags >= (1 << 64):
            raise FJWriteFjmException(f"flags must be a 64bit positive number, not {flags}")
        if BaseVersion == version and flags != 0:
            raise FJWriteFjmException(f"version 0 does not support the flags option")
        if CompressedVersion == version:
            if lzma_preset is None or lzma_preset not in range(10):
                raise FJWriteFjmException("version 3 requires an LZMA preset (0-9, faster->smaller).")
            else:
                self.lzma_preset = lzma_preset

        self.output_file = output_file
        self.word_size = w
        self.version = version
        self.flags = flags
        self.reserved = 0

        self.segments = []
        self.data = []  # words array

    def _compress_data(self, data: bytes) -> bytes:
        try:
            return lzma.compress(data, format=_LZMA_FORMAT,
                                 filters=_LZMA_COMPRESSION_FILTERS(2*self.word_size, self.lzma_preset))
        except lzma.LZMAError as e:
            raise FJWriteFjmException(f'Error: Unable to compress the data.') from e

    def write_to_file(self) -> None:
        write_tag = '<' + {8: 'B', 16: 'H', 32: 'L', 64: 'Q'}[self.word_size]

        with open(self.output_file, 'wb') as f:
            f.write(pack(header_base_format, fj_magic, self.word_size, self.version, len(self.segments)))
            if BaseVersion != self.version:
                f.write(pack(header_extension_format, self.flags, self.reserved))

            for segment in self.segments:
                f.write(pack(segment_format, *segment))

            fjm_data = b''.join(pack(write_tag, word) for word in self.data)
            if CompressedVersion == self.version:
                fjm_data = self._compress_data(fjm_data)

            f.write(fjm_data)

    @staticmethod
    def _is_segment_collision(start1: int, end1: int, start2: int, end2: int) -> bool:
        if any(start2 <= address <= end2 for address in (start1, end1)):
            return True
        if any(start1 <= address <= end1 for address in (start2, end2)):
            return True
        return False

    def _validate_segment_not_overlapping(self, new_start: int, new_length: int) -> None:
        new_end = new_start + new_length - 1
        for i, (start, length, _, _) in enumerate(self.segments):

            if self._is_segment_collision(start, start + length - 1, new_start, new_end):
                w = self.word_size

                bit_start = start * w
                bit_end = (start + length) * w - 1

                new_bit_start = new_start * w
                new_bit_end = (new_start + new_length) * w - 1

                raise FJWriteFjmException(f"Overlapping segments: "
                                          f"seg[{i}]=[{hex(bit_start)}, {hex(bit_end)}]"
                                          f" and "
                                          f"seg[{len(self.segments)}]=[{hex(new_bit_start)}, {hex(new_bit_end)}]")

    def add_segment(self, segment_start: int, segment_length: int, data_start: int, data_length: int) -> None:
        if segment_length < data_length:
            raise FJWriteFjmException(f"segment-length must be at-least data-length (in )")

        if segment_start % 2 == 1 or segment_length % 2 == 1:
            raise FJWriteFjmException(f"segment-start and segment-length must be 2*w aligned.")

        self._validate_segment_not_overlapping(segment_start, segment_length)
        # TODO add validate_segment_data_not_overloading
        #  (if self.version in (RelativeJumpVersion, RelativeCompressedVersion)) - maybe inside the above function

        if self.version in (RelativeJumpVersion, CompressedVersion):
            word = ((1 << self.word_size) - 1)
            for i in range(1, data_length, 2):
                self.data[data_start + i] = (self.data[data_start + i] - (segment_start + i) * self.word_size) & word

        self.segments.append((segment_start, segment_length, data_start, data_length))

    def add_data(self, data: List[int]) -> Tuple[int, int]:
        start = len(self.data)
        length = len(data)
        self.data += data
        return start, length

    def add_simple_segment_with_data(self, segment_start, data) -> None:
        data_start, data_length = self.add_data(data)
        self.add_segment(segment_start, data_length, data_start, data_length)

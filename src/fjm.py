import struct
from enum import IntEnum
from pathlib import Path
from struct import pack, unpack
from time import sleep
from typing import BinaryIO, List, Tuple, Dict, Optional

import lzma

from exceptions import FJReadFjmException, FJWriteFjmException, FJRuntimeMemoryException

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


FJ_MAGIC = ord('F') + (ord('J') << 8)

_reserved_dict_threshold = 1000

_header_base_format = '<HHQQ'
_header_base_size = 2 + 2 + 8 + 8

_header_extension_format = '<QL'
_header_extension_size = 8 + 4

_segment_format = '<QQQQ'
_segment_size = 8 + 8 + 8 + 8

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


def _lzma_compression_filters(dw: int, preset: int) -> List[Dict[str, int]]:
    return [{"id": lzma.FILTER_LZMA2, "preset": preset, "nice_len": dw}]


def _new_garbage_val() -> int:
    return 0        # The value read when reading a word outside any segment.


class GarbageHandling(IntEnum):
    """
    What to do when reading garbage memory (memory outside any segment).
    """
    Stop = 0            # Stop and finish
    SlowRead = 1        # Continue after a small waiting time, very slow and print a warning
    OnlyWarning = 2     # Continue and print a warning
    Continue = 3        # Continue normally


class Reader:
    """
    Used for reading a .fjm file from memory.
    """
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
                data = self._read_decompressed_data(fjm_file)
                self._init_memory(segments, data)
            except struct.error as se:
                raise FJReadFjmException(f"Bad file {input_file}, can't unpack. Maybe it's not a .fjm file?") from se

    def _init_header_fields(self, fjm_file: BinaryIO) -> None:
        self.magic, self.w, self.version, self.segment_num = \
            unpack(_header_base_format, fjm_file.read(_header_base_size))
        if BaseVersion == self.version:
            self.flags, self.reserved = 0, 0
        else:
            self.flags, self.reserved = unpack(_header_extension_format, fjm_file.read(_header_extension_size))

    def _init_segments(self, fjm_file: BinaryIO) -> List[Tuple]:
        return [unpack(_segment_format, fjm_file.read(_segment_size)) for _ in range(self.segment_num)]

    def _validate_header(self) -> None:
        if self.magic != FJ_MAGIC:
            raise FJReadFjmException(f'Error: bad magic code ({hex(self.magic)}, should be {hex(FJ_MAGIC)}).')
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

    def _read_decompressed_data(self, fjm_file: BinaryIO) -> List[int]:
        """
        @param fjm_file: [in]: read from this file the data words.
        @return: list of the data words (decompressed if it was compressed).
        """
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
                if segment_length - data_length < _reserved_dict_threshold:
                    for i in range(data_length, segment_length):
                        self.memory[segment_start + i] = 0
                else:
                    self.zeros_boundaries.append((segment_start + data_length, segment_start + segment_length))

    def _get_memory_word(self, word_address: int) -> int:
        word_address &= ((1 << self.w) - 1)
        if word_address not in self.memory:
            for start, end in self.zeros_boundaries:
                if start <= word_address < end:
                    self.memory[word_address] = 0
                    return 0

            garbage_val = _new_garbage_val()
            garbage_message = f'Reading garbage word at mem[{hex(word_address << self.w)[2:]}] = {hex(garbage_val)[2:]}'

            if GarbageHandling.Stop == self.garbage_handling:
                raise FJRuntimeMemoryException(garbage_message)
            elif GarbageHandling.OnlyWarning == self.garbage_handling:
                print(f'\nWarning:  {garbage_message}')
            elif GarbageHandling.SlowRead == self.garbage_handling:
                print(f'\nWarning:  {garbage_message}')
                sleep(0.1)

            self.memory[word_address] = garbage_val

        return self.memory[word_address]

    def _set_memory_word(self, word_address: int, value: int) -> None:
        word_address &= ((1 << self.w) - 1)
        value &= ((1 << self.w) - 1)
        self.memory[word_address] = value

    def _bit_address_decompose(self, bit_address: int) -> Tuple[int, int]:
        """
        @param bit_address: the address
        @return: tuple of the word address and the bit offset
        """
        word_address = (bit_address >> (self.w.bit_length() - 1)) & ((1 << self.w) - 1)
        bit_offset = bit_address & (self.w - 1)
        return word_address, bit_offset

    def read_bit(self, bit_address: int) -> bool:
        """
        read a bit from memory.
        @param bit_address: the address
        @return: True/False for 1/0
        """
        word_address, bit_offset = self._bit_address_decompose(bit_address)
        return (self._get_memory_word(word_address) >> bit_offset) & 1 == 1

    def write_bit(self, bit_address: int, bit_value: bool) -> None:
        """
        write a bit to memory.
        @param bit_address: the address
        @param bit_value: True/False for 1/0
        """
        word_address, bit_offset = self._bit_address_decompose(bit_address)
        word_value = self._get_memory_word(word_address)
        if bit_value:
            word_value |= (1 << bit_offset)
        else:
            word_value &= ((1 << self.w) - 1 - (1 << bit_offset))
        self._set_memory_word(word_address, word_value)

    def get_word(self, bit_address: int) -> int:
        """
        read a word from memory (can be unaligned).
        @param bit_address: the address
        @return: the word value
        """
        word_address, bit_offset = self._bit_address_decompose(bit_address)
        if bit_offset == 0:
            return self._get_memory_word(word_address)
        if word_address == ((1 << self.w) - 1):
            raise FJRuntimeMemoryException(f'Accessed outside of memory (beyond the last bit).')

        lsw = self._get_memory_word(word_address)
        msw = self._get_memory_word(word_address + 1)
        return ((lsw >> bit_offset) | (msw << (self.w - bit_offset))) & ((1 << self.w) - 1)


class Writer:
    """
    Used for creating a .fjm file in memory.
    The process is:
        1. add_data(..)
        2. add_segment(..)
        repeat steps 1-2 until you finished updating the fjm
        3. write_to_file()
    """
    def __init__(self, output_file: Path, w: int, version: int, *, flags: int = 0, lzma_preset: Optional[int] = None):
        """
        the .fjm-file writer
        @param output_file: [in,out]: the path to the .fjm file
        @param w: the memory-width
        @param version: the file's version
        @param flags: the file's flags
        @param lzma_preset: the preset to be used when compressing the .fjm data
        """
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
                                 filters=_lzma_compression_filters(2 * self.word_size, self.lzma_preset))
        except lzma.LZMAError as e:
            raise FJWriteFjmException(f'Error: Unable to compress the data.') from e

    def write_to_file(self) -> None:
        """
        writes the .fjm headers, segments and (might be compressed) data into the output_file.
        @note call this after finished adding data and segments and editing the Writer.
        """
        write_tag = '<' + {8: 'B', 16: 'H', 32: 'L', 64: 'Q'}[self.word_size]

        with open(self.output_file, 'wb') as f:
            f.write(pack(_header_base_format, FJ_MAGIC, self.word_size, self.version, len(self.segments)))
            if BaseVersion != self.version:
                f.write(pack(_header_extension_format, self.flags, self.reserved))

            for segment in self.segments:
                f.write(pack(_segment_format, *segment))

            fjm_data = b''.join(pack(write_tag, word) for word in self.data)
            if CompressedVersion == self.version:
                fjm_data = self._compress_data(fjm_data)

            f.write(fjm_data)

    def get_segment_addresses_repr(self, word_start_address: int, word_length: int) -> str:
        """
        @param word_start_address: the start address of the segment in memory (in words)
        @param word_length: the number of words the segment takes in memory
        @return: a nice looking segment-representation string by its addresses
        """
        return f'[{hex(self.word_size * word_start_address)}, ' \
               f'{hex(self.word_size * (word_start_address + word_length))})'

    @staticmethod
    def _is_collision(start1: int, end1: int, start2: int, end2: int) -> bool:
        if any(start2 <= address <= end2 for address in (start1, end1)):
            return True
        if any(start1 <= address <= end1 for address in (start2, end2)):
            return True
        return False

    def _validate_segment_addresses_not_overlapping(self, new_segment_start: int, new_segment_length: int) -> None:
        new_segment_end = new_segment_start + new_segment_length - 1
        for i, (segment_start, segment_length, _, _) in enumerate(self.segments):
            segment_end = segment_start + segment_length - 1

            if self._is_collision(segment_start, segment_end, new_segment_start, new_segment_end):
                raise FJWriteFjmException(
                    f"Overlapping segments addresses: "
                    f"seg[{i}]={self.get_segment_addresses_repr(segment_start, segment_length)}"
                    f" and "
                    f"seg[{len(self.segments)}]={self.get_segment_addresses_repr(new_segment_start, new_segment_length)}"
                )

    def _validate_segment_data_not_overlapping(self, new_data_start: int, new_data_length: int) -> None:
        if new_data_length == 0:
            return
        new_data_end = new_data_start + new_data_length - 1

        for i, (_, _, data_start, data_length) in enumerate(self.segments):
            if data_length == 0:
                continue
            data_end = data_start + data_length - 1

            if self._is_collision(data_start, data_end, new_data_start, new_data_end):
                raise FJWriteFjmException(
                    f"Overlapping segments data: "
                    f"seg[{i}]=data[{hex(data_start)}, {hex(data_end + 1)})"
                    f" and "
                    f"seg[{len(self.segments)}]=data[{hex(new_data_start)}, {hex(new_data_end + 1)})"
                )

    def _validate_segment_not_overlapping(self, segment_start: int, segment_length: int,
                                          data_start: int, data_length: int) -> None:
        self._validate_segment_addresses_not_overlapping(segment_start, segment_length)

        if self.version in (RelativeJumpVersion, CompressedVersion):
            self._validate_segment_data_not_overlapping(data_start, data_length)

    def _update_to_relative_jumps(self, segment_start: int, data_start: int, data_length: int) -> None:
        word = ((1 << self.word_size) - 1)
        for i in range(1, data_length, 2):
            self.data[data_start + i] = (self.data[data_start + i] - (segment_start + i) * self.word_size) & word

    def add_segment(self, segment_start: int, segment_length: int, data_start: int, data_length: int) -> None:
        """
        inserts a new segment to the fjm file. checks that it doesn't overlap with any previously inserted segments.
        @param segment_start: the start address of the segment in memory (in words)
        @param segment_length: the number of words the segment takes in memory (if bigger that the data_length,
         the segment is padded with zeros after the end of the data).
        @param data_start: the index of the data's start in the inner data array
        @param data_length: the number of words in the segment's data
        """
        segment_addresses_str = f'seg[{self.segments}]={self.get_segment_addresses_repr(segment_start, segment_length)}'

        if segment_length <= 0:
            raise FJWriteFjmException(f"segment-length must be positive (in {segment_addresses_str}).")

        if segment_length < data_length:
            raise FJWriteFjmException(f"segment-length must be at-least data-length (in {segment_addresses_str}).")

        if segment_start % 2 == 1 or segment_length % 2 == 1:
            raise FJWriteFjmException(f"segment-start and segment-length must be 2*w aligned "
                                      f"(in {segment_addresses_str}).")

        self._validate_segment_not_overlapping(segment_start, segment_length, data_start, data_length)

        if self.version in (RelativeJumpVersion, CompressedVersion):
            self._update_to_relative_jumps(segment_start, data_start, data_length)

        self.segments.append((segment_start, segment_length, data_start, data_length))

    def add_data(self, data: List[int]) -> int:
        """
        append the data to the current data
        @param data: [in]: a list of words
        @return: the data start index
        """
        data_start = len(self.data)
        self.data += data
        return data_start

    def add_simple_segment_with_data(self, segment_start: int, data: List[int]) -> None:
        """
        adds the data and a segment that contains exactly the data, to the fjm
        @param segment_start: the start address of the segment in memory (in words)
        @param data: [in]: a list of words
        """
        data_start = self.add_data(data)
        self.add_segment(segment_start, len(data), data_start, len(data))

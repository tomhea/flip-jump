from struct import pack, unpack
from random import randint
from time import sleep


"""
struct {
        u16 fj_magic;   // 'F' + 'J'<<8  (0x4a46)
        u16 mem_words;
        u64 word_size;  // in bits
        u64 flags;
        u64 segment_num;
        struct segment {
            u64 segment_start;  // in memory words (w-bits)
            u64 segment_length; // in memory words (w-bits)
            u64 data_start;     // in the outer-struct.data words (w-bits)
            u64 data_length;    // in the outer-struct.data words (w-bits)
        } *segments;             // segments[segment_num]
        u8* data;               // the data
    } blm_file;     // Bit-Level Memory file
"""

fj_magic = ord('F') + (ord('J') << 8)
reserved_dict_threshold = 1000


class Reader:
    def __init__(self, input_file, slow_garbage_read=True, stop_after_garbage=True):
        self.mem = {}   # memory words
        self.slow_garbage_read = slow_garbage_read
        self.stop_after_garbage = stop_after_garbage
        self.n = None
        self.w = None
        self.default_table = []
        self.zeros_boundaries = []

        self.segments = []
        self.data = []  # bytes

        with open(input_file, 'rb') as f:
            magic, self.w, self.n, self.flags, segment_num = unpack('<HHQQQ', f.read(2+2+8+8+8))
            if magic != fj_magic:
                print(f'Error: bad magic code ({magic}, should be {fj_magic}).')
                exit(1)
            self.segments = [unpack('<QQQQ', f.read(8+8+8+8)) for _ in range(segment_num)]
            self.data = [b for b in f.read()]
            for segment_start, segment_length, data_start, data_length in self.segments:
                for i in range(data_length):
                    self.mem[segment_start + i] = self.data_word(data_start + i)
                if segment_length > data_length:
                    if segment_length - data_length < reserved_dict_threshold:
                        for i in range(data_length, segment_length):
                            self.mem[segment_start + i] = 0
                    else:
                        self.zeros_boundaries.append((segment_start + data_length, segment_start + segment_length))

    def data_word(self, i):
        res = 0
        w_in_bytes = self.w >> 3
        for j in range(w_in_bytes):
            res |= self.data[i * w_in_bytes + j] << (j << 3)
        return res

    def __getitem__(self, address):
        address &= ((1 << self.n) - 1)
        if address not in self.mem:
            for start, end in self.zeros_boundaries:
                if start <= address < end:
                    self.mem[address] = 0
                    return 0
            garbage_val = randint(0, (1 << self.w) - 1)
            print(f'\nWarning:  Reading garbage word at mem[{hex(address << self.w)[2:]}] = {hex(garbage_val)[2:]}')
            if self.stop_after_garbage:
                exit(1)
            if self.slow_garbage_read:
                sleep(0.1)
            self.mem[address] = garbage_val
        return self.mem[address]

    def __setitem__(self, address, value):
        address &= ((1 << self.n) - 1)
        value &= ((1 << self.w) - 1)
        self.mem[address] = value

    def bit_address_decompose(self, bit_address):
        address = (bit_address >> (self.w.bit_length() - 1)) & ((1 << self.n) - 1)
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
        if address == ((1 << self.n) - 1):
            print(f'\nWarning:  Accessed outside of memory (beyond the last bit).')
            exit(1)
        l, m = self[address], self[address+1]
        return ((l >> bit) | (m << (self.w - bit))) & ((1 << self.w) - 1)


class Writer:
    def __init__(self, w, n, flags=0):
        self.mem_words = n
        self.word_size = w
        if self.word_size not in (8, 16, 32, 64):
            raise ValueError(f"Word size {w} is not in {{8, 16, 32, 64}}.")
        self.write_tag = '<' + {8: 'B', 16: 'H', 32: 'L', 64: 'Q'}[self.word_size]
        self.flags = flags & ((1 << 64) - 1)
        self.segments = []
        self.data = []  # words array

    def write_to_file(self, output_file):
        with open(output_file, 'wb') as f:
            f.write(pack('<HHQQQ', fj_magic, self.mem_words, self.word_size, self.flags, len(self.segments)))

            for segment in self.segments:
                f.write(pack('<QQQQ', *segment))

            for datum in self.data:
                f.write(pack(self.write_tag, datum))

    def add_segment(self, segment_start, segment_length, data_start, data_length):
        if segment_length < data_length:
            raise ValueError(f"segment-length must be at-least data-length")
        self.segments.append((segment_start, segment_length, data_start, data_length))

    def add_data(self, data):
        start = len(self.data)
        self.data += data
        return start, len(data)

    def add_simple_segment_with_data(self, segment_start, data):
        data_start, data_length = self.add_data(data)
        self.add_segment(segment_start, data_length, data_start, data_length)

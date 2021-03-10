from struct import pack, unpack
from random import randint
from time import sleep


"""
struct {
        u16 mem_words;
        u64 word_size;  // in bits
        u64 flags;
        u64 sector_num;
        struct sector {
            u64 sector_start;   // in memory words (w-bits)
            u64 data_start;     // in the outer-struct.data words (w-bits)
            u64 data_length;    // in the outer-struct.data words (w-bits)
        } *sectors;             // sectors[sector_num]
        u8* data;               // the data
    } blm_file;     // Bit-Level Memory file
"""


class Reader:
    def __init__(self, input_file, slow_garbage_read=True, stop_after_garbage=True):
        self.mem = {}   # memory words
        self.slow_garbage_read = slow_garbage_read
        self.stop_after_garbage = stop_after_garbage
        self.n = None
        self.w = None
        self.default_table = []

        self.sectors = []
        self.data = []  # bytes

        with open(input_file, 'rb') as f:
            self.w, self.n, self.flags, sector_num = unpack('<HQQQ', f.read(2+8+8+8))
            self.sectors = [unpack('<QQQ', f.read(8+8+8)) for _ in range(sector_num)]
            self.data = [b for b in f.read()]
            for sector_start, data_start, data_length in self.sectors:
                for i in range(data_length):
                    self.mem[sector_start + i] = self.data_word(data_start + i)

    def data_word(self, i):
        res = 0
        w_in_bytes = self.w >> 3
        for j in range(w_in_bytes):
            res |= self.data[i * w_in_bytes + j] << (j << 3)
        return res

    def __getitem__(self, address):
        address &= ((1 << self.n) - 1)
        if address not in self.mem:
            garbage_val = randint(0, (1 << self.w) - 1)
            print(f'Warning:  reading garbage word at mem[{hex(address << self.w)[2:]}] = {hex(garbage_val)[2:]}')
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
            print(f'Warning:  Accessed outside of memory (beyond the last bit).')
        l, m = self[address], self[address+1]
        return ((l >> bit) | (m << (self.w - bit))) & ((1 << self.w) - 1)


class Writer:
    def __init__(self, w, n, flags=0):
        self.mem_words = n
        self.word_size = w
        if self.word_size & 7 != 0:
            raise ValueError(f"Word size {w} doesn't divide by 8")
        if 1 << (self.word_size.bit_length() - 1) != self.word_size:
            raise ValueError(f"Word size {w} is not a power of 2")
        self.flags = flags & ((1 << 64) - 1)
        self.sectors = []
        self.data = []

    def write_to_file(self, output_file):
        with open(output_file, 'wb') as f:
            f.write(pack('<HQQQ', self.mem_words, self.word_size, self.flags, len(self.sectors)))

            for sector in self.sectors:
                f.write(pack('<QQQ', *sector))

            val, ind = 0, 0
            for datum in self.data:
                val, ind = val | (datum << ind), (ind+1) % 8
                if ind == 0:
                    f.write(pack('<B', val))
                    val = 0

    def add_sector(self, sector_start, data_start, data_length):
        self.sectors.append((sector_start, data_start, data_length))

    def add_data(self, data):
        if len(data) % self.word_size != 0:
            data += [0] * (self.word_size - (len(data) % self.word_size))
        start = len(self.data)
        self.data += data
        return start // self.word_size, len(data) // self.word_size

    def add_simple_sector_with_data(self, sector_start, data):
        data_start, data_length = self.add_data(data)
        self.add_sector(sector_start, data_start, data_length)

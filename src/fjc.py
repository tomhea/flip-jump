from struct import pack, unpack
from random import randint
from time import sleep


"""
struct {
        u8  mem_bits;
        u64 sector_num;
        u8  default_bit; // 0/1 is default 0/1, otherwise default garbage
        struct sector {
            u64 sector_start;   // in memory bits
            u64 sector_length;  // in memory bits
            u64 sector_pad;     // start writing at sector_start + sector_pad
            u8  default_sector_bit;     // 0/1 is default 0/1, otherwise default garbage
            u64 data_start;     // in the outer-struct.data bits
            u64 data_length;    // in the outer-struct.data bits
            u64 jumps;              // 0 for no jumps, 1 for 1 bit jump (writes data, advances 1 bit, write data again,..)
            u64 jump_granularity;   // how many bits to write between jumps
        } *sectors;             // sectors[sector_num]
        u8* data;               // the data
    } fjc_file;
"""

NO_DEFAULT_BIT = 2


class Reader:
    def __init__(self, input_file):
        self.mem = {}   # memory bits
        self.w = 64
        self.default_table = []
        with open(input_file, 'rb') as f:
            self.w, sector_num, def_bit = unpack('<BQB', f.read(1+8+1))
            self.default_append(0, 1<<self.w, def_bit)
            sectors = [unpack('<QQQBQQQQ', f.read(7*8+1)) for _ in range(sector_num)]
            data = [b for b in f.read()]
            for sector_start, sector_length, sector_pad, default_sector_bit, data_start, data_length, jumps, jump_granularity in sectors:
                self.default_append(sector_start, sector_length, default_sector_bit)
                sector_i, data_i = sector_start + sector_pad, data_start
                while data_i < data_start + data_length:
                    for _ in range(jump_granularity):
                        self.mem[sector_i] = Reader.data_bit(data, data_i)
                        sector_i, data_i = sector_i+1, data_i+1
                    sector_i += jumps

    @staticmethod
    def data_bit(data, i):
        return 1 if data[i >> 3] & (1 << (i & 7)) else 0

    def default_append(self, start, length, default_bit):
        if length > 0 and default_bit in (0, 1):
            self.default_table.append((start, start+length-1, default_bit))

    def default_lookup(self, address):
        for start, end, default_bit in self.default_table[::-1]:
            if start <= address <= end:
                return default_bit

        garbage_val = randint(0, 1)
        print(f'Warning:  reading garbage bit at mem[{address}] = {garbage_val}')
        sleep(0.1)
        return garbage_val

    def __getitem__(self, address):
        address &= ((1 << self.w) - 1)
        if address not in self.mem:
            self.mem[address] = self.default_lookup(address)
        return self.mem[address]

    def __setitem__(self, address, value):
        address &= ((1 << self.w) - 1)
        self.mem[address] = value

    def flip(self, address):
        address &= ((1 << self.w) - 1)
        self[address] = 1 - self[address]

    def get_word(self, address):
        out = 0
        for i in range(self.w):
            out |= self[address+i] << i
        return out


class Writer:
    def __init__(self, w, default_bit=NO_DEFAULT_BIT):
        self.mem_bits = w
        self.default_bit = default_bit
        self.sectors = []
        self.data = []

    def write_to_file(self, output_file):
        with open(output_file, 'wb') as f:
            f.write(pack('<BQB', self.mem_bits, len(self.sectors), self.default_bit))

            for sector in self.sectors:
                f.write(pack('<QQQBQQQQ', *sector))

            val, ind = 0, 0
            for datum in self.data:
                val, ind = val | (datum << ind), (ind+1) % 8
                if ind == 0:
                    f.write(pack('<B', val))
                    val = 0
            if ind != 0:
                f.write(pack('<B', val))

    def add_sector(self, sector_start, sector_length, data_start, data_length,
                   sector_pad=0, default_sector_bit=NO_DEFAULT_BIT, jumps=0, jump_granularity=1):
        self.sectors.append((sector_start, sector_length, sector_pad, default_sector_bit,
                             data_start, data_length, jumps, jump_granularity))

    def add_data(self, data):
        start = len(data)
        self.data += data
        return start

    def add_simple_sector_with_data(self, sector_start, data):
        data_start = self.add_data(data) - len(data)
        sector_length = data_length = len(data)
        self.add_sector(sector_start, sector_length, data_start, data_length)

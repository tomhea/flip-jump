from sys import stdin, stdout
from serial import Serial
from time import time

class BasicIO(Serial):
    class NoMoreInputException(Exception):
        pass

    def __init__(self, defined_input, output_verbose, verbose):
        self.output = bytes()
        self.output_anything_yet = False
        self.pause_time = 0

        self.defined_input = defined_input
        self.output_verbose = output_verbose
        self.verbose = verbose

        self.output_char, self.output_size = 0, 0
        self.input_char, self.input_size = 0, 0

    def hasBit(self) -> bool:
        return self.input_size > 0

    def readBit(self) -> bool:
        if self.input_size == 0:
            if self.defined_input is None:
                pause_time_start = time()
                self.input_char = stdin.buffer.read(1)[0]
                pause_time += time() - pause_time_start
            elif len(self.defined_input) > 0:
                self.input_char = self.defined_input[0]
                self.defined_input = self.defined_input[1:]
            else:
                if self.output_verbose and self.output_anything_yet:
                    print()
                raise NoMoreInputException()
            self.input_size = 8

        bit = self.input_char & 1

        self.input_char = self.input_char >> 1
        self.input_size -= 1

        return bit

    def canWriteBit(self) -> bool:
        return True

    def writeBit(self, bit):
        self.output_char |= bit << self.output_size
        self.output_byte = bytes([self.output_char])
        self.output_size += 1
        if self.output_size == 8:
            self.output += self.output_byte
            if self.output_verbose:
                if self.verbose:
                    for _ in range(3):
                        print()
                    print(f'Outputted Char:  ', end='')
                    stdout.buffer.write(bytes([self.output_char]))
                    stdout.flush()
                    for _ in range(3):
                        print()
                else:
                    stdout.buffer.write(bytes([self.output_char]))
                    stdout.flush()
            self.output_anything_yet = True
            self.output_char, self.output_size = 0, 0

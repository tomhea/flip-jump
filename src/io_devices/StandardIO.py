from IODevice import IODevice
from io_exceptions import IOReadOnEOF, IncompleteOutput


class FixedStandardIO(IODevice):
    def __init__(self, _input: bytes):
        self.remaining_input = _input
        self._output = b''

        self.current_input_byte = 0
        self.bits_to_read_in_input_byte = 0

        self.current_output_byte = 0
        self.bits_to_write_in_output_byte = 0

    def read_bit(self) -> bool:
        if 0 == self.bits_to_read_in_input_byte:
            if not self.remaining_input:
                raise IOReadOnEOF("Read an empty input on fixed standard IO (EOF)")

            self.current_input_byte = self.remaining_input[0]
            self.remaining_input = self.remaining_input[1:]
            self.bits_to_read_in_input_byte = 8

        bit = (self.current_input_byte & 1) == 1
        self.current_input_byte >>= 1
        self.bits_to_read_in_input_byte -= 1
        return bit

    def write_bit(self, bit: bool) -> None:
        self.current_output_byte = (self.current_output_byte << 1) | bit
        self.bits_to_write_in_output_byte += 1

        if 8 == self.bits_to_write_in_output_byte:
            self._output += self.current_output_byte.to_bytes(1, 'little')
            self.current_output_byte = 0
            self.bits_to_write_in_output_byte = 0

    def is_available_read(self) -> bool:
        return self.remaining_input or 0 < self.bits_to_read_in_input_byte

    def is_available_write(self) -> bool:
        return True

    def get_output(self) -> bytes:
        if 0 != self.bits_to_write_in_output_byte:
            raise IncompleteOutput("tries to get output when an unaligned number of bits was outputted "
                                   "(doesn't divide 8)")

        return self._output

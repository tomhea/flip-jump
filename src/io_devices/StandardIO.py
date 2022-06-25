from typing import IO

from IODevice import IODevice


class BrokenIO(IODevice):
    def __init__(self, input_file: IO, output_file: IO):
        self.input_file = input_file
        self.output_file = output_file
        raise NotImplemented

    def read_bit(self) -> bool:
        raise NotImplemented

    def write_bit(self, bit: bool) -> None:
        raise NotImplemented

    def is_available_read(self) -> bool:
        raise NotImplemented

    def is_available_write(self) -> bool:
        raise NotImplemented

    def is_eof(self) -> bool:
        raise NotImplemented

    def flush(self) -> None:
        self.output_file.flush()

    def __del__(self):
        self.flush()

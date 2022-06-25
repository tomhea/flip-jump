from IODevice import IODevice
from io_exceptions import BrokenIOUsed


class BrokenIO(IODevice):
    def read_bit(self) -> bool:
        raise BrokenIOUsed("program tried to read a bit from the BrokenIO device")

    def write_bit(self, bit: bool) -> None:
        raise BrokenIOUsed(f"program tried to write a bit ({int(bit)}) to the BrokenIO device")

    def is_available_read(self) -> bool:
        return False

    def is_available_write(self) -> bool:
        return False

    def is_eof(self) -> bool:
        return True

    # default __del__

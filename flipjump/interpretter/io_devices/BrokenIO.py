from flipjump.interpretter.io_devices.IODevice import IODevice
from flipjump.utils.exceptions import BrokenIOUsed


class BrokenIO(IODevice):
    """
    IO device that raises error on any IO action
    """
    def read_bit(self) -> bool:
        raise BrokenIOUsed("program tried to read a bit from the BrokenIO device")

    def write_bit(self, bit: bool) -> None:
        raise BrokenIOUsed(f"program tried to write a bit ({int(bit)}) to the BrokenIO device")

    # default __del__

"""
the abstract IO device interface.
defines the bit-level read/write contract every io-device implements, so the
interpreter can stay agnostic of where its input/output actually goes.
"""

from abc import ABC, abstractmethod


class IODevice(ABC):
    """
    abstract IO device
    """

    @abstractmethod
    def read_bit(self) -> bool:
        return False

    @abstractmethod
    def write_bit(self, bit: bool) -> None:
        pass

    @abstractmethod
    def get_output(self, *, allow_incomplete_output: bool = False) -> bytes:
        pass

    # Also, each class should implement a "__del__" to flush last changes before it gets deleted.

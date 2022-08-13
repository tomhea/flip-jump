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

    # Also, each class should implement a "__del__" to flush last changes before it gets deleted.

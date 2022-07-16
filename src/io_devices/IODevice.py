from abc import ABC, abstractmethod


class IODevice(ABC):
    @abstractmethod
    def read_bit(self) -> bool:
        return False

    @abstractmethod
    def write_bit(self, bit: bool) -> None:
        pass

    @abstractmethod
    def is_available_read(self) -> bool:
        return False

    @abstractmethod
    def is_available_write(self) -> bool:
        return False

    # Also, each class should implement a "__del__" to flush last changes before it gets deleted.

"""
the split io-device + the --di/--do device factory.
SplitIO routes read_bit to an input device and write_bit to an output device, attaching
both to the interpreter memory. create_io_device builds the io-device from the CLI specs:
  --di standard | keyboard=EVENTS_FILE
  --do standard | screen=FRAMES_DIR
"""

from pathlib import Path
from typing import Optional

from flipjump.interpreter.io_devices.IODevice import IODevice
from flipjump.interpreter.io_devices.KeyboardIO import KeyboardIO, ScriptedKeyEventSource
from flipjump.interpreter.io_devices.ScreenIO import InMemoryScreen256
from flipjump.interpreter.io_devices.StandardIO import StandardIO
from flipjump.interpreter.io_devices.device_memory import DeviceMemory
from flipjump.utils.exceptions import IODeviceException


class SplitIO(IODevice):
    """reads from the input device, writes to the output device."""

    def __init__(self, input_device: IODevice, output_device: IODevice):
        self.input_device = input_device
        self.output_device = output_device

    def attach_memory(self, device_memory: DeviceMemory) -> None:
        self.input_device.attach_memory(device_memory)
        self.output_device.attach_memory(device_memory)

    def read_bit(self) -> bool:
        return self.input_device.read_bit()

    def write_bit(self, bit: bool) -> None:
        self.output_device.write_bit(bit)

    def get_output(self, *, allow_incomplete_output: bool = False) -> bytes:
        return self.output_device.get_output(allow_incomplete_output=allow_incomplete_output)


def create_input_device(di_spec: str) -> IODevice:
    if di_spec == 'standard':
        return StandardIO(True)
    if di_spec.startswith('keyboard='):
        events_path = di_spec[len('keyboard=') :]  # noqa: E203
        if not Path(events_path).is_file():
            raise IODeviceException(f'keyboard events file does not exist: {events_path}')
        return KeyboardIO(ScriptedKeyEventSource.from_file(Path(events_path)))
    raise IODeviceException(f'unknown input device: {di_spec!r}. supported: standard, keyboard=EVENTS_FILE')


def create_output_device(do_spec: str) -> IODevice:
    if do_spec == 'standard':
        return StandardIO(True)
    if do_spec.startswith('screen='):
        return InMemoryScreen256(frames_dir=Path(do_spec[len('screen=') :]))  # noqa: E203
    raise IODeviceException(f'unknown output device: {do_spec!r}. supported: standard, screen=FRAMES_DIR')


def create_io_device(di_spec: Optional[str], do_spec: Optional[str]) -> IODevice:
    """build the io-device from the --di/--do CLI specs (None means standard)."""
    if (di_spec or 'standard') == 'standard' and (do_spec or 'standard') == 'standard':
        return StandardIO(True)
    return SplitIO(create_input_device(di_spec or 'standard'), create_output_device(do_spec or 'standard'))

"""
the split io-device + the --di/--do device factory.
SplitIO routes read_bit to an input device and write_bit to an output device, attaching
both to the interpreter memory. create_io_device builds the io-device from the CLI specs:
  --di standard | keyboard=EVENTS_FILE | keyboard
  --do standard | screen=FRAMES_DIR | screen
plain `--do screen` opens an interactive window and plain `--di keyboard` reads live key
presses (needs pygame: flipjump[screen]). The two interactive devices share one neutral
PygameWindow (created here, the composition root) - neither depends on the other; a live
keyboard with no interactive screen opens its own small input window.
"""

from pathlib import Path
from typing import TYPE_CHECKING, Optional

from flipjump.interpreter.io_devices.IODevice import IODevice
from flipjump.interpreter.io_devices.KeyboardIO import KeyboardIO, ScriptedKeyEventSource
from flipjump.interpreter.io_devices.ScreenIO import InMemoryScreen
from flipjump.interpreter.io_devices.StandardIO import StandardIO
from flipjump.interpreter.io_devices.device_memory import DeviceMemory
from flipjump.utils.exceptions import IODeviceException

if TYPE_CHECKING:
    from flipjump.interpreter.io_devices.pygame_window import PygameWindow


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


def create_input_device(di_spec: str, window: 'Optional[PygameWindow]') -> IODevice:
    if di_spec == 'standard':
        return StandardIO(True)
    if di_spec == 'keyboard':
        # live keys: whatever is pressed while the (shared) interactive window is focused
        from flipjump.interpreter.io_devices.pygame_window import WindowKeyEventSource

        assert window is not None  # create_io_device makes the window for a live keyboard
        return KeyboardIO(WindowKeyEventSource(window))
    if di_spec.startswith('keyboard='):
        events_path = di_spec[len('keyboard=') :]  # noqa: E203
        if not Path(events_path).is_file():
            raise IODeviceException(f'keyboard events file does not exist: {events_path}')
        return KeyboardIO(ScriptedKeyEventSource.from_file(Path(events_path)))
    raise IODeviceException(f'unknown input device: {di_spec!r}. supported: standard, keyboard=EVENTS_FILE, keyboard')


def create_output_device(do_spec: str, window: 'Optional[PygameWindow]') -> IODevice:
    if do_spec == 'standard':
        return StandardIO(True)
    if do_spec == 'screen':
        # an interactive window (scaled; F11 = fullscreen; closing it stops the run)
        from flipjump.interpreter.io_devices.pygame_window import InteractiveScreen

        return InteractiveScreen(window=window)
    if do_spec.startswith('screen='):
        return InMemoryScreen(frames_dir=Path(do_spec[len('screen=') :]))  # noqa: E203
    raise IODeviceException(f'unknown output device: {do_spec!r}. supported: standard, screen=FRAMES_DIR, screen')


def create_io_device(di_spec: Optional[str], do_spec: Optional[str]) -> IODevice:
    """build the io-device from the --di/--do CLI specs (None means standard)."""
    di_spec, do_spec = di_spec or 'standard', do_spec or 'standard'
    if di_spec == 'standard' and do_spec == 'standard':
        return StandardIO(True)

    # one neutral window, shared by the interactive screen and/or the live keyboard
    window: Optional['PygameWindow'] = None
    if di_spec == 'keyboard' or do_spec == 'screen':
        from flipjump.interpreter.io_devices.pygame_window import PygameWindow

        window = PygameWindow()

    input_device = create_input_device(di_spec, window)
    output_device = create_output_device(do_spec, window)

    # an interactive screen opens/sizes the shared window itself (on its init-screen command);
    # a live keyboard with no such screen needs its own small window for SDL to deliver keys.
    if di_spec == 'keyboard' and do_spec != 'screen':
        assert window is not None
        window.ensure_open_for_input()

    return SplitIO(input_device, output_device)

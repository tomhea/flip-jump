"""
the split io-device + the --di/--do device factory.

SplitIO routes read_bit to an input device and write_bit to an output device, attaching
both to the interpreter memory. The --di/--do specs are looked up in a small registry
(INPUT_DEVICES / OUTPUT_DEVICES): each device declares how to build itself from its optional
`=arg`, and whether it uses the shared interactive PygameWindow (needs it open / is the one
that opens+sizes it). create_io_device is the composition root - it makes ONE window when any
chosen device needs it, hands the same window to both, and opens a small input window when a
window-needing device has nobody to open it. Adding a new device (windowed or not) is one
registry entry; the composition logic never special-cases device names.

current specs:
  --di:  standard | keyboard | keyboard=EVENTS_FILE
  --do:  standard | console | screen | screen=FRAMES_DIR
"""

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Dict, Optional, Tuple

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


def _never(arg: Optional[str]) -> bool:
    return False


def _is_bare(arg: Optional[str]) -> bool:
    """the interactive (bare, no `=arg`) form of a device that also has a headless `=arg` form."""
    return arg is None


@dataclass(frozen=True)
class DeviceFactory:
    """one --di/--do device: how to build it from its optional `=arg`, and its relation to
    the shared interactive window. `needs_window`: the device reads/draws the window (so one
    must exist). `opens_window`: the device opens+sizes the window itself (e.g. the screen on
    its init command) - if a window is needed but nobody opens it, the composition root opens
    a small input window. `forms` is the human-readable spec spelling(s), for help/errors."""

    forms: str
    build: Callable[[Optional[str], 'Optional[PygameWindow]'], IODevice]
    needs_window: Callable[[Optional[str]], bool] = _never
    opens_window: Callable[[Optional[str]], bool] = _never


def _build_standard(arg: Optional[str], window: 'Optional[PygameWindow]') -> IODevice:
    return StandardIO(True)


def _build_keyboard(arg: Optional[str], window: 'Optional[PygameWindow]') -> IODevice:
    if arg is None:
        # live keys: whatever is pressed while the (shared) interactive window is focused
        from flipjump.interpreter.io_devices.pygame_window import WindowKeyEventSource

        assert window is not None  # a live keyboard needs_window, so the root made one
        return KeyboardIO(WindowKeyEventSource(window))
    if not Path(arg).is_file():
        raise IODeviceException(f'keyboard events file does not exist: {arg}')
    return KeyboardIO(ScriptedKeyEventSource.from_file(Path(arg)))


def _build_screen(arg: Optional[str], window: 'Optional[PygameWindow]') -> IODevice:
    if arg is None:
        # an interactive window (scaled; F11 = fullscreen; closing it stops the run)
        from flipjump.interpreter.io_devices.pygame_window import InteractiveScreen

        return InteractiveScreen(window=window)
    return InMemoryScreen(frames_dir=Path(arg))


# the device registries - extend these to add a new --di/--do device (one entry each).
INPUT_DEVICES: Dict[str, DeviceFactory] = {
    'standard': DeviceFactory(forms='standard', build=_build_standard),
    'keyboard': DeviceFactory(forms='keyboard | keyboard=EVENTS_FILE', build=_build_keyboard, needs_window=_is_bare),
}
OUTPUT_DEVICES: Dict[str, DeviceFactory] = {
    'standard': DeviceFactory(forms='standard', build=_build_standard),
    'console': DeviceFactory(forms='console', build=_build_standard),  # plain text to the terminal
    'screen': DeviceFactory(
        forms='screen | screen=FRAMES_DIR', build=_build_screen, needs_window=_is_bare, opens_window=_is_bare
    ),
}


def _parse_spec(spec: str) -> Tuple[str, Optional[str]]:
    """'keyboard=foo' -> ('keyboard', 'foo');  'keyboard' -> ('keyboard', None)."""
    name, separator, arg = spec.partition('=')
    return name, (arg if separator else None)


def _lookup(registry: Dict[str, DeviceFactory], kind: str, spec: str) -> Tuple[DeviceFactory, Optional[str]]:
    name, arg = _parse_spec(spec)
    factory = registry.get(name)
    if factory is None:
        supported = ', '.join(device.forms for device in registry.values())
        raise IODeviceException(f'unknown {kind} device: {spec!r}. supported: {supported}')
    return factory, arg


def create_io_device(di_spec: Optional[str], do_spec: Optional[str]) -> IODevice:
    """build the io-device from the --di/--do CLI specs (None means standard)."""
    di_spec, do_spec = di_spec or 'standard', do_spec or 'standard'
    if di_spec == 'standard' and do_spec == 'standard':
        return StandardIO(True)  # pure shortcut: the registry path would build an identical SplitIO

    in_factory, in_arg = _lookup(INPUT_DEVICES, 'input', di_spec)
    out_factory, out_arg = _lookup(OUTPUT_DEVICES, 'output', do_spec)

    # one neutral window, shared by whichever chosen devices use it
    window: Optional['PygameWindow'] = None
    if in_factory.needs_window(in_arg) or out_factory.needs_window(out_arg):
        from flipjump.interpreter.io_devices.pygame_window import PygameWindow

        window = PygameWindow()

    input_device = in_factory.build(in_arg, window)
    output_device = out_factory.build(out_arg, window)

    # a window is needed but no chosen device opens/sizes it (e.g. a live keyboard with no
    # interactive screen) - open a small input window so SDL can deliver its events.
    if window is not None and not (in_factory.opens_window(in_arg) or out_factory.opens_window(out_arg)):
        window.ensure_open_for_input()

    return SplitIO(input_device, output_device)

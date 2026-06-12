"""
the --io device selector.

The CLI picks ONE complete IODevice (a "mode"); each device owns its own channels (and its
window, if any) internally - there is no input/output splitting. Adding a new mode is one
IO_MODES entry plus its device class, with no shared-window/coupling logic, because nothing
is composed across devices.

modes:
  standard - terminal input/output (the default).
  pc       - an interactive window: live keyboard input + a scaled 256-color screen.

headless/scripted devices (e.g. scripted keys + PNG frames, or a plain InMemoryScreen) are
built programmatically and passed straight to fjm_run.run(io_device=...) - e.g.
PcIO.headless(events_file, frames_dir) - they are not --io modes.
"""

from typing import Callable, Dict

from flipjump.interpreter.io_devices.IODevice import IODevice
from flipjump.interpreter.io_devices.StandardIO import StandardIO
from flipjump.utils.exceptions import IODeviceException


def _make_standard() -> IODevice:
    return StandardIO(True)


def _make_pc() -> IODevice:
    # imported lazily: the interactive window needs pygame (the optional `screen` extra)
    from flipjump.interpreter.io_devices.pygame_window import PcIO

    return PcIO.interactive()


# the --io modes - extend with one entry (+ its device class) to add a new complete device.
IO_MODES: Dict[str, Callable[[], IODevice]] = {
    'standard': _make_standard,
    'pc': _make_pc,
}


def make_io_device(io_mode: str) -> IODevice:
    """build the complete io-device for the given --io mode."""
    factory = IO_MODES.get(io_mode)
    if factory is None:
        raise IODeviceException(f'unknown --io mode: {io_mode!r}. supported: {", ".join(IO_MODES)}')
    return factory()

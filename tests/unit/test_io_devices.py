"""
unit-tests for the IO devices (flipjump/interpreter/io_devices/).

covers FixedIO's LSB-first bit ordering, output assembly, EOF and incomplete-output
errors, BrokenIO raising on any access, and the --di/--do device registry/factory
(the non-windowed paths - the windowed wiring is in test_screen_window.py).
"""

from pathlib import Path

import pytest

from flipjump.interpreter.io_devices.BrokenIO import BrokenIO
from flipjump.interpreter.io_devices.FixedIO import FixedIO
from flipjump.interpreter.io_devices.StandardIO import StandardIO
from flipjump.interpreter.io_devices.cli_devices import SplitIO, create_io_device
from flipjump.utils.exceptions import BrokenIOUsed, IncompleteOutput, IODeviceException, IOReadOnEOF


def test_fixed_io_reads_lsb_first() -> None:
    device = FixedIO(b'\x01')
    assert device.read_bit() is True
    assert [device.read_bit() for _ in range(7)] == [False] * 7


def test_fixed_io_reads_msb_last() -> None:
    device = FixedIO(b'\x80')
    assert [device.read_bit() for _ in range(7)] == [False] * 7
    assert device.read_bit() is True


def test_fixed_io_output_round_trip() -> None:
    device = FixedIO(b'')
    for bit in [True, False, False, False, False, False, True, False]:  # 'A' == 0x41, LSB first
        device.write_bit(bit)
    assert device.get_output() == b'A'


def test_fixed_io_eof_on_empty_input() -> None:
    with pytest.raises(IOReadOnEOF):
        FixedIO(b'').read_bit()


def test_fixed_io_eof_after_exhausting_a_byte() -> None:
    device = FixedIO(b'\x00')
    for _ in range(8):
        device.read_bit()
    with pytest.raises(IOReadOnEOF):
        device.read_bit()


def test_fixed_io_incomplete_output_raises() -> None:
    device = FixedIO(b'')
    for _ in range(3):
        device.write_bit(True)
    with pytest.raises(IncompleteOutput):
        device.get_output()


def test_fixed_io_incomplete_output_allowed() -> None:
    device = FixedIO(b'')
    for _ in range(3):
        device.write_bit(True)
    assert device.get_output(allow_incomplete_output=True) == b''


def test_broken_io_raises_on_any_access() -> None:
    with pytest.raises(BrokenIOUsed):
        BrokenIO().read_bit()
    with pytest.raises(BrokenIOUsed):
        BrokenIO().write_bit(True)
    with pytest.raises(BrokenIOUsed):
        BrokenIO().get_output()


class TestDeviceRegistry:
    """the --di/--do factory for the devices that don't use the interactive window."""

    def test_standard_only_is_a_plain_standard_io(self) -> None:
        assert isinstance(create_io_device(None, None), StandardIO)
        assert isinstance(create_io_device('standard', 'standard'), StandardIO)

    def test_console_output_with_standard_input(self) -> None:
        # a non-windowed mix: standard input + console (terminal text) output
        io_device = create_io_device('standard', 'console')
        assert isinstance(io_device, SplitIO)
        assert isinstance(io_device.output_device, StandardIO)
        assert isinstance(io_device.input_device, StandardIO)

    def test_unknown_input_device_lists_the_supported_forms(self) -> None:
        with pytest.raises(IODeviceException) as error:
            create_io_device('joystick', 'standard')
        assert 'unknown input device' in str(error.value)
        assert 'keyboard' in str(error.value)  # the supported forms are listed

    def test_unknown_output_device_lists_the_supported_forms(self) -> None:
        with pytest.raises(IODeviceException) as error:
            create_io_device('standard', 'hologram')
        assert 'unknown output device' in str(error.value)
        assert 'screen' in str(error.value) and 'console' in str(error.value)

    def test_missing_scripted_keyboard_file_is_reported(self, tmp_path: Path) -> None:
        with pytest.raises(IODeviceException) as error:
            create_io_device(f'keyboard={tmp_path / "nope.txt"}', 'console')
        assert 'does not exist' in str(error.value)

"""
unit-tests for the IO devices (flipjump/interpreter/io_devices/).

covers FixedIO's LSB-first bit ordering, output assembly, EOF and incomplete-output
errors, BrokenIO raising on any access, and the --io mode selector (the non-windowed
paths - the windowed `pc` device is in test_screen_window.py).
"""

import pytest

from flipjump.interpreter.io_devices.BrokenIO import BrokenIO
from flipjump.interpreter.io_devices.FixedIO import FixedIO
from flipjump.interpreter.io_devices.StandardIO import StandardIO
from flipjump.interpreter.io_devices.cli_devices import make_io_device
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


class TestIoModes:
    """the --io mode selector (the windowed `pc` mode lives in test_screen_window.py)."""

    def test_standard_mode_is_a_plain_standard_io(self) -> None:
        assert isinstance(make_io_device('standard'), StandardIO)

    def test_unknown_mode_lists_the_supported_modes(self) -> None:
        with pytest.raises(IODeviceException) as error:
            make_io_device('hologram')
        assert 'unknown --io mode' in str(error.value)
        assert 'standard' in str(error.value) and 'pc' in str(error.value)

    def test_empty_mode_string_is_rejected(self) -> None:
        with pytest.raises(IODeviceException) as error:
            make_io_device('  ')
        assert 'empty --io mode' in str(error.value)

    def test_mode_string_is_split_into_name_and_parameters(self) -> None:
        # the first whitespace-separated part is the mode name; current modes take no parameters
        assert isinstance(make_io_device('  standard  '), StandardIO)
        with pytest.raises(IODeviceException) as error:
            make_io_device('standard loud')
        assert 'no parameters' in str(error.value)

    def test_pc_mode_rejects_parameters_before_importing_pygame(self) -> None:
        # the parameter check precedes the lazy pygame import, so it works without pygame
        with pytest.raises(IODeviceException) as error:
            make_io_device('pc fullscreen')
        assert 'no parameters' in str(error.value)

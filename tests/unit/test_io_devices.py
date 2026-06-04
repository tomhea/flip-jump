"""
unit-tests for the IO devices (flipjump/interpretter/io_devices/).

covers FixedIO's LSB-first bit ordering, output assembly, EOF and incomplete-output
errors, and BrokenIO raising on any access.
"""

import pytest

from flipjump.interpretter.io_devices.BrokenIO import BrokenIO
from flipjump.interpretter.io_devices.FixedIO import FixedIO
from flipjump.utils.exceptions import BrokenIOUsed, IncompleteOutput, IOReadOnEOF


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

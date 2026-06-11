"""
unit-tests for the host-side LUT generator (flipjump/lut_generator.py).

the generator emits .fj data tables (consecutive `hex.vec n, value` entries - the layout
hex.read_table indexes) from python value lists, with fixed-point encoding helpers.
byte-exactness of the emitted values is pinned against hand-computed references.
"""

import math

import pytest

from flipjump.lut_generator import (
    encode_fixed_point,
    generate_byte_lut_fj,
    generate_lut_fj,
    generate_reciprocal_lut_fj,
    generate_sine_lut_fj,
)


class TestEncodeFixedPoint:
    def test_positive_value(self) -> None:
        assert encode_fixed_point(1.0, fraction_bits=16, total_bits=32) == 0x10000
        assert encode_fixed_point(1.5, fraction_bits=16, total_bits=32) == 0x18000

    def test_negative_value_is_twos_complement(self) -> None:
        assert encode_fixed_point(-1.0, fraction_bits=16, total_bits=32) == 0xFFFF0000
        assert encode_fixed_point(-0.5, fraction_bits=16, total_bits=32) == 0xFFFF8000

    def test_8_8_format(self) -> None:
        assert encode_fixed_point(2.5, fraction_bits=8, total_bits=16) == 0x0280
        assert encode_fixed_point(-2.5, fraction_bits=8, total_bits=16) == 0xFD80

    def test_rounds_to_nearest(self) -> None:
        assert encode_fixed_point(0.3, fraction_bits=16, total_bits=32) == round(0.3 * (1 << 16))

    def test_out_of_range_raises(self) -> None:
        with pytest.raises(ValueError):
            encode_fixed_point(40000.0, fraction_bits=16, total_bits=32)
        with pytest.raises(ValueError):
            encode_fixed_point(-40000.0, fraction_bits=16, total_bits=32)


class TestGenerateLutFj:
    def test_emits_label_and_entries(self) -> None:
        fj_source = generate_lut_fj('my_table', [0x12, 0x3456, 0], entry_nibbles=4)
        assert 'my_table:' in fj_source
        assert fj_source.count('hex.vec 4,') == 3
        assert 'hex.vec 4, 0x12' in fj_source
        assert 'hex.vec 4, 0x3456' in fj_source

    def test_value_must_fit_entry(self) -> None:
        with pytest.raises(ValueError):
            generate_lut_fj('t', [0x12345], entry_nibbles=4)

    def test_negative_values_rejected_encode_first(self) -> None:
        # the table holds raw (already-encoded) unsigned words
        with pytest.raises(ValueError):
            generate_lut_fj('t', [-1], entry_nibbles=4)


class TestCannedGenerators:
    def test_reciprocal_lut_values(self) -> None:
        # recip[i] = round(2^16 / i), recip[0] = max entry value (DOOM convention: clamp)
        fj_source = generate_reciprocal_lut_fj('recip', count=4, fraction_bits=16, entry_nibbles=8)
        assert 'recip:' in fj_source
        assert f'hex.vec 8, {hex(0xFFFFFFFF)}' in fj_source  # i=0 clamps
        assert f'hex.vec 8, {hex(1 << 16)}' in fj_source  # i=1
        assert f'hex.vec 8, {hex(1 << 15)}' in fj_source  # i=2
        assert f'hex.vec 8, {hex(round((1 << 16) / 3))}' in fj_source  # i=3

    def test_sine_lut_values(self) -> None:
        fj_source = generate_sine_lut_fj('finesine', count=8, fraction_bits=16, entry_nibbles=8)
        expected_sin_1 = encode_fixed_point(math.sin(2 * math.pi * 1 / 8), 16, 32)
        assert f'hex.vec 8, {hex(expected_sin_1)}' in fj_source
        # sin(3/4 * 2pi) is negative - must appear two's-complement encoded
        expected_sin_6 = encode_fixed_point(math.sin(2 * math.pi * 6 / 8), 16, 32)
        assert expected_sin_6 > 0x80000000
        assert f'hex.vec 8, {hex(expected_sin_6)}' in fj_source


class TestGenerateByteLutFj:
    def test_emits_packed_byte_ops(self) -> None:
        fj_source = generate_byte_lut_fj("colormap", [0, 0x41, 255])
        assert "colormap:" in fj_source
        assert fj_source.count("* dw") == 3
        assert ";0x41 * dw" in fj_source
        assert ";0xff * dw" in fj_source

    def test_non_byte_values_rejected(self) -> None:
        with pytest.raises(ValueError):
            generate_byte_lut_fj("t", [256])
        with pytest.raises(ValueError):
            generate_byte_lut_fj("t", [-1])

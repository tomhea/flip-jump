"""Phase 3 batch 11: bits — basics (12 programs).

popcount_byte, parity_byte, high_nibble, low_nibble, swap_nibbles,
reverse_bits_byte, xor_two_bytes, and_two_bytes, or_two_bytes,
shift_left_one, shift_right_one, is_power_of_two.

Bytes are bit.vec 8; bit i lives at ch+i*dw. Per-bit work uses rep(8, i).
Runtime-bit-position programs (bit_at_position, set/clear/toggle) need a
shift loop and are a later bits batch.

Run from the repo root:  python scripts/batch11_bits.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog_arith import emit  # noqa: E402

ADD_BIT = """
// Add 1 to count[:16] if the bit at b is set.
def add_bit_into count, b @ end {
    bit.if0 b, end
    bit.inc 16, count
  end:
}
""".strip()

TOGGLE_IF_SET = """
// Toggle the bit p if the bit at b is set (used to accumulate parity).
def toggle_if_set p, b @ end {
    bit.if0 b, end
    bit.not p
  end:
}
""".strip()

PRINT_HEX_NIBBLE = """
// Print the low 4 bits at nib as a single lowercase hex digit (0-9, a-f).
def print_hex_nibble nib @ small, big, done < hexout, ten, off_small, off_big {
    bit.zero 8, hexout
    bit.mov 4, hexout, nib
    bit.cmp 4, nib, ten, small, big, big
  small:
    bit.add 8, hexout, off_small
    ;done
  big:
    bit.add 8, hexout, off_big
  done:
    bit.print hexout
}
""".strip()

D_HEXNIB = ["hexout: bit.vec 8, 0", "ten: bit.vec 4, 10", "off_small: bit.vec 8, 0x30", "off_big: bit.vec 8, 0x57"]


def B(nnnn, slug, name, **kw):
    emit("bits", nnnn, slug, name, **kw)


# 0076 popcount_byte
B(
    "0076",
    "popcount_byte",
    "Popcount Byte",
    extra_helpers=[ADD_BIT],
    value_data=["ch: bit.vec 8, 0", "count: bit.vec 16, 0"],
    main_body="""
def main < ch, count {
    stl.startup
    bit.input ch
    bit.zero 16, count
    rep(8, i) add_bit_into count, ch + i*dw
    bit.print_dec_uint 16, count
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"\x0b",
    out_bytes=b"3\n",
)

# 0077 parity_byte
B(
    "0077",
    "parity_byte",
    "Parity Byte",
    extra_helpers=[TOGGLE_IF_SET],
    value_data=["ch: bit.vec 8, 0", "parity: bit.bit"],
    main_body="""
def main @ odd, even, done < ch, parity {
    stl.startup
    bit.input ch
    bit.zero parity
    rep(8, i) toggle_if_set parity, ch + i*dw
    bit.if0 parity, even
  odd:
    stl.output "1\\n"
    ;done
  even:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"\x0b",
    out_bytes=b"1\n",
)

# 0078 high_nibble
B(
    "0078",
    "high_nibble",
    "High Nibble",
    extra_helpers=[PRINT_HEX_NIBBLE],
    value_data=["ch: bit.vec 8, 0"],
    extra_data=D_HEXNIB,
    main_body="""
def main < ch {
    stl.startup
    bit.input ch
    print_hex_nibble ch + 4*dw
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"\x4a",
    out_bytes=b"4\n",
)

# 0079 low_nibble
B(
    "0079",
    "low_nibble",
    "Low Nibble",
    extra_helpers=[PRINT_HEX_NIBBLE],
    value_data=["ch: bit.vec 8, 0"],
    extra_data=D_HEXNIB,
    main_body="""
def main < ch {
    stl.startup
    bit.input ch
    print_hex_nibble ch
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"\x4a",
    out_bytes=b"a\n",
)

# 0080 swap_nibbles
B(
    "0080",
    "swap_nibbles",
    "Swap Nibbles",
    value_data=["ch: bit.vec 8, 0", "out: bit.vec 8, 0"],
    main_body="""
def main < ch, out {
    stl.startup
    bit.input ch
    bit.zero 8, out
    bit.mov 4, out, ch + 4*dw
    bit.mov 4, out + 4*dw, ch
    bit.print out
    stl.loop
}
""",
    in_bytes=b"\x4a",
    out_bytes=b"\xa4",
)

# 0081 reverse_bits_byte
B(
    "0081",
    "reverse_bits_byte",
    "Reverse Bits Byte",
    value_data=["ch: bit.vec 8, 0", "out: bit.vec 8, 0"],
    main_body="""
def main < ch, out {
    stl.startup
    bit.input ch
    rep(8, i) bit.mov out + i*dw, ch + (7-i)*dw
    bit.print out
    stl.loop
}
""",
    in_bytes=b"\x01",
    out_bytes=b"\x80",
)

# 0085 xor_two_bytes
B(
    "0085",
    "xor_two_bytes",
    "Xor Two Bytes",
    value_data=["a: bit.vec 8, 0", "b: bit.vec 8, 0"],
    main_body="""
def main < a, b {
    stl.startup
    bit.input a
    bit.input b
    bit.xor 8, a, b
    bit.print a
    stl.loop
}
""",
    in_bytes=b"\xf0\x0f",
    out_bytes=b"\xff",
)

# 0086 and_two_bytes
B(
    "0086",
    "and_two_bytes",
    "And Two Bytes",
    value_data=["a: bit.vec 8, 0", "b: bit.vec 8, 0"],
    main_body="""
def main < a, b {
    stl.startup
    bit.input a
    bit.input b
    bit.and 8, a, b
    bit.print a
    stl.loop
}
""",
    in_bytes=b"\xf0\x3c",
    out_bytes=b"\x30",
)

# 0087 or_two_bytes
B(
    "0087",
    "or_two_bytes",
    "Or Two Bytes",
    value_data=["a: bit.vec 8, 0", "b: bit.vec 8, 0"],
    main_body="""
def main < a, b {
    stl.startup
    bit.input a
    bit.input b
    bit.or 8, a, b
    bit.print a
    stl.loop
}
""",
    in_bytes=b"\xf0\x0f",
    out_bytes=b"\xff",
)

# 0088 shift_left_one
B(
    "0088",
    "shift_left_one",
    "Shift Left One",
    value_data=["ch: bit.vec 8, 0"],
    main_body="""
def main < ch {
    stl.startup
    bit.input ch
    bit.shl 8, ch
    bit.print ch
    stl.loop
}
""",
    in_bytes=b"\x81",
    out_bytes=b"\x02",
)

# 0089 shift_right_one
B(
    "0089",
    "shift_right_one",
    "Shift Right One",
    value_data=["ch: bit.vec 8, 0"],
    main_body="""
def main < ch {
    stl.startup
    bit.input ch
    bit.shr 8, ch
    bit.print ch
    stl.loop
}
""",
    in_bytes=b"\x81",
    out_bytes=b"\x40",
)

# 0090 is_power_of_two — exactly one 1-bit
B(
    "0090",
    "is_power_of_two",
    "Is Power Of Two",
    extra_helpers=[ADD_BIT],
    value_data=["ch: bit.vec 8, 0", "count: bit.vec 16, 0", "one: bit.vec 16, 1"],
    main_body="""
def main @ yes, no, done < ch, count, one {
    stl.startup
    bit.input ch
    bit.zero 16, count
    rep(8, i) add_bit_into count, ch + i*dw
    bit.cmp 16, count, one, no, yes, no
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"\x08",
    out_bytes=b"1\n",
)

print("---")
print("BATCH 11 DONE")

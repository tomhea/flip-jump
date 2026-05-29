"""Phase 3 batch 12: bits — transforms, zero-counts, multi-byte ops (18 programs).

is_byte_zero, is_byte_full, xor_with_constant_55, and_with_constant_0f,
or_with_constant_80, byte_decrement_wrap, rotate_left_byte, rotate_right_byte,
byte_to_binary_string, count_leading_zeros, count_trailing_zeros,
count_bits_in_three_bytes, swap_two_bytes, xor_three_bytes, and_three_bytes,
or_three_bytes, gray_code_from_binary, unset_lowest_set_bit.

Run from the repo root:  python scripts/batch12_bits2.py
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

SCAN_ZERO = """
// One leading/trailing-zero step: while `still` scanning, count a 0 bit; a 1 bit stops the scan.
def scan_zero_step still, count, b @ is_one, end {
    bit.if0 still, end
    bit.if1 b, is_one
    bit.inc 16, count
    ;end
  is_one:
    bit.zero still
  end:
}
""".strip()

PRINT_BIT = """
// Print '1' if the bit at b is set, else '0'.
def print_bit b @ one, done {
    bit.if1 b, one
    stl.output '0'
    ;done
  one:
    stl.output '1'
  done:
}
""".strip()


def B(nnnn, slug, name, **kw):
    emit("bits", nnnn, slug, name, **kw)


# 0374 is_byte_zero
B(
    "0374",
    "is_byte_zero",
    "Is Byte Zero",
    value_data=["ch: bit.vec 8, 0"],
    main_body="""
def main @ yes, done < ch {
    stl.startup
    bit.input ch
    bit.if0 8, ch, yes
    stl.output "0\\n"
    ;done
  yes:
    stl.output "1\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"\x00",
    out_bytes=b"1\n",
)

# 0375 is_byte_full
B(
    "0375",
    "is_byte_full",
    "Is Byte Full",
    value_data=["ch: bit.vec 8, 0", "full: bit.vec 8, 0xff"],
    main_body="""
def main @ yes, no, done < ch, full {
    stl.startup
    bit.input ch
    bit.cmp 8, ch, full, no, yes, no
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"\xff",
    out_bytes=b"1\n",
)

# 0376 xor_with_constant_55
B(
    "0376",
    "xor_with_constant_55",
    "Xor With Constant 55",
    value_data=["ch: bit.vec 8, 0", "c55: bit.vec 8, 0x55"],
    main_body="""
def main < ch, c55 {
    stl.startup
    bit.input ch
    bit.xor 8, ch, c55
    bit.print ch
    stl.loop
}
""",
    in_bytes=b"\xff",
    out_bytes=b"\xaa",
)

# 0377 and_with_constant_0f
B(
    "0377",
    "and_with_constant_0f",
    "And With Constant 0f",
    value_data=["ch: bit.vec 8, 0", "c0f: bit.vec 8, 0x0f"],
    main_body="""
def main < ch, c0f {
    stl.startup
    bit.input ch
    bit.and 8, ch, c0f
    bit.print ch
    stl.loop
}
""",
    in_bytes=b"\xab",
    out_bytes=b"\x0b",
)

# 0378 or_with_constant_80
B(
    "0378",
    "or_with_constant_80",
    "Or With Constant 80",
    value_data=["ch: bit.vec 8, 0", "c80: bit.vec 8, 0x80"],
    main_body="""
def main < ch, c80 {
    stl.startup
    bit.input ch
    bit.or 8, ch, c80
    bit.print ch
    stl.loop
}
""",
    in_bytes=b"\x0f",
    out_bytes=b"\x8f",
)

# 0379 byte_decrement_wrap
B(
    "0379",
    "byte_decrement_wrap",
    "Byte Decrement Wrap",
    value_data=["ch: bit.vec 8, 0"],
    main_body="""
def main < ch {
    stl.startup
    bit.input ch
    bit.dec 8, ch
    bit.print ch
    stl.loop
}
""",
    in_bytes=b"\x00",
    out_bytes=b"\xff",
)

# 0380 rotate_left_byte — out[i+1]=ch[i], out[0]=ch[7]
B(
    "0380",
    "rotate_left_byte",
    "Rotate Left Byte",
    value_data=["ch: bit.vec 8, 0", "out: bit.vec 8, 0"],
    main_body="""
def main < ch, out {
    stl.startup
    bit.input ch
    bit.mov out, ch + 7*dw
    rep(7, i) bit.mov out + (i+1)*dw, ch + i*dw
    bit.print out
    stl.loop
}
""",
    in_bytes=b"\x81",
    out_bytes=b"\x03",
)

# 0381 rotate_right_byte — out[i]=ch[i+1], out[7]=ch[0]
B(
    "0381",
    "rotate_right_byte",
    "Rotate Right Byte",
    value_data=["ch: bit.vec 8, 0", "out: bit.vec 8, 0"],
    main_body="""
def main < ch, out {
    stl.startup
    bit.input ch
    bit.mov out + 7*dw, ch
    rep(7, i) bit.mov out + i*dw, ch + (i+1)*dw
    bit.print out
    stl.loop
}
""",
    in_bytes=b"\x81",
    out_bytes=b"\xc0",
)

# 0372 byte_to_binary_string — 8 chars MSB first
B(
    "0372",
    "byte_to_binary_string",
    "Byte To Binary String",
    extra_helpers=[PRINT_BIT],
    value_data=["ch: bit.vec 8, 0"],
    main_body="""
def main < ch {
    stl.startup
    bit.input ch
    rep(8, i) print_bit ch + (7-i)*dw
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"\x4a",
    out_bytes=b"01001010\n",
)

# 0370 count_leading_zeros — from MSB down to first 1 (zero byte -> 8)
B(
    "0370",
    "count_leading_zeros",
    "Count Leading Zeros",
    extra_helpers=[SCAN_ZERO],
    value_data=["ch: bit.vec 8, 0", "count: bit.vec 16, 0", "still: bit.bit"],
    main_body="""
def main < ch, count, still {
    stl.startup
    bit.input ch
    bit.zero 16, count
    bit.one still
    rep(8, i) scan_zero_step still, count, ch + (7-i)*dw
    bit.print_dec_uint 16, count
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"\x01",
    out_bytes=b"7\n",
)

# 0371 count_trailing_zeros — from LSB up to first 1 (zero byte -> 8)
B(
    "0371",
    "count_trailing_zeros",
    "Count Trailing Zeros",
    extra_helpers=[SCAN_ZERO],
    value_data=["ch: bit.vec 8, 0", "count: bit.vec 16, 0", "still: bit.bit"],
    main_body="""
def main < ch, count, still {
    stl.startup
    bit.input ch
    bit.zero 16, count
    bit.one still
    rep(8, i) scan_zero_step still, count, ch + i*dw
    bit.print_dec_uint 16, count
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"\x08",
    out_bytes=b"3\n",
)

# 0384 count_bits_in_three_bytes
B(
    "0384",
    "count_bits_in_three_bytes",
    "Count Bits In Three Bytes",
    extra_helpers=[ADD_BIT],
    value_data=["a: bit.vec 8, 0", "b: bit.vec 8, 0", "c: bit.vec 8, 0", "count: bit.vec 16, 0"],
    main_body="""
def main < a, b, c, count {
    stl.startup
    bit.input a
    bit.input b
    bit.input c
    bit.zero 16, count
    rep(8, i) add_bit_into count, a + i*dw
    rep(8, i) add_bit_into count, b + i*dw
    rep(8, i) add_bit_into count, c + i*dw
    bit.print_dec_uint 16, count
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"\xff\x00\x0f",
    out_bytes=b"12\n",
)

# 0896 swap_two_bytes
B(
    "0896",
    "swap_two_bytes",
    "Swap Two Bytes",
    value_data=["a: bit.vec 8, 0", "b: bit.vec 8, 0"],
    main_body="""
def main < a, b {
    stl.startup
    bit.input a
    bit.input b
    bit.print b
    bit.print a
    stl.loop
}
""",
    in_bytes=b"\xaa\xbb",
    out_bytes=b"\xbb\xaa",
)

# 0899 xor_three_bytes
B(
    "0899",
    "xor_three_bytes",
    "Xor Three Bytes",
    value_data=["a: bit.vec 8, 0", "b: bit.vec 8, 0", "c: bit.vec 8, 0"],
    main_body="""
def main < a, b, c {
    stl.startup
    bit.input a
    bit.input b
    bit.input c
    bit.xor 8, a, b
    bit.xor 8, a, c
    bit.print a
    stl.loop
}
""",
    in_bytes=b"\xf0\x0f\xff",
    out_bytes=b"\x00",
)

# 0900 and_three_bytes
B(
    "0900",
    "and_three_bytes",
    "And Three Bytes",
    value_data=["a: bit.vec 8, 0", "b: bit.vec 8, 0", "c: bit.vec 8, 0"],
    main_body="""
def main < a, b, c {
    stl.startup
    bit.input a
    bit.input b
    bit.input c
    bit.and 8, a, b
    bit.and 8, a, c
    bit.print a
    stl.loop
}
""",
    in_bytes=b"\xff\x0f\x3c",
    out_bytes=b"\x0c",
)

# 0901 or_three_bytes
B(
    "0901",
    "or_three_bytes",
    "Or Three Bytes",
    value_data=["a: bit.vec 8, 0", "b: bit.vec 8, 0", "c: bit.vec 8, 0"],
    main_body="""
def main < a, b, c {
    stl.startup
    bit.input a
    bit.input b
    bit.input c
    bit.or 8, a, b
    bit.or 8, a, c
    bit.print a
    stl.loop
}
""",
    in_bytes=b"\x01\x02\x04",
    out_bytes=b"\x07",
)

# 0924 gray_code_from_binary — byte XOR (byte >> 1)
B(
    "0924",
    "gray_code_from_binary",
    "Gray Code From Binary",
    value_data=["ch: bit.vec 8, 0", "tmp: bit.vec 8, 0"],
    main_body="""
def main < ch, tmp {
    stl.startup
    bit.input ch
    bit.mov 8, tmp, ch
    bit.shr 8, tmp
    bit.xor 8, ch, tmp
    bit.print ch
    stl.loop
}
""",
    in_bytes=b"\x05",
    out_bytes=b"\x07",
)

# 0933 unset_lowest_set_bit — byte AND (byte - 1)
B(
    "0933",
    "unset_lowest_set_bit",
    "Unset Lowest Set Bit",
    value_data=["ch: bit.vec 8, 0", "tmp: bit.vec 8, 0"],
    main_body="""
def main < ch, tmp {
    stl.startup
    bit.input ch
    bit.mov 8, tmp, ch
    bit.dec 8, tmp
    bit.and 8, ch, tmp
    bit.print ch
    stl.loop
}
""",
    in_bytes=b"\x0c",
    out_bytes=b"\x08",
)

print("---")
print("BATCH 12 DONE")

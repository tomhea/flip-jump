"""Phase 3 batch 13: bits — predicates, gray->binary, ones-counts, power-of-2 (16).

dominant_bit, min_two_bytes, max_two_bytes, byte_high_eq_low_nibble,
byte_is_bit_palindrome, byte_reverse_each_nibble, binary_from_gray_code,
count_leading_ones, count_trailing_ones, isolate_lowest_set_bit,
broadcast_lsb_to_byte, round_up_to_multiple_of_8, round_down_to_multiple_of_8,
next_power_of_2_byte, prev_power_of_2_byte, log2_ceil_byte.

Run from the repo root:  python scripts/batch13_bits3.py
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

SCAN_ONE = """
// One leading/trailing-one step: while `still` scanning, count a 1 bit; a 0 bit stops the scan.
def scan_one_step still, count, b @ is_zero, end {
    bit.if0 still, end
    bit.if0 b, is_zero
    bit.inc 16, count
    ;end
  is_zero:
    bit.zero still
  end:
}
""".strip()

PAIR_EQ = """
// If the bits at x and y differ, jump to `fail`.
def pair_eq_or_fail x, y, fail @ x1, ok {
    bit.if1 x, x1
    bit.if1 y, fail
    ;ok
  x1:
    bit.if0 y, fail
  ok:
}
""".strip()

GRAY2BIN = """
// out_k = ch_k XOR out_k1 — one running-XOR step of gray-code -> binary.
def gray2bin_step ok, ck, ok1 {
    bit.mov ok, ck
    bit.xor ok, ok1
}
""".strip()


def B(nnnn, slug, name, **kw):
    emit("bits", nnnn, slug, name, **kw)


# 0385 dominant_bit — popcount vs 4 -> 1 / tie / 0
B(
    "0385",
    "dominant_bit",
    "Dominant Bit",
    extra_helpers=[ADD_BIT],
    value_data=["ch: bit.vec 8, 0", "count: bit.vec 16, 0", "four: bit.vec 16, 4"],
    main_body="""
def main @ less, tie, greater, done < ch, count, four {
    stl.startup
    bit.input ch
    bit.zero 16, count
    rep(8, i) add_bit_into count, ch + i*dw
    bit.cmp 16, count, four, less, tie, greater
  less:
    stl.output "0\\n"
    ;done
  tie:
    stl.output "tie\\n"
    ;done
  greater:
    stl.output "1\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"\xff",
    out_bytes=b"1\n",
)

# 0897 min_two_bytes
B(
    "0897",
    "min_two_bytes",
    "Min Two Bytes",
    value_data=["a: bit.vec 8, 0", "b: bit.vec 8, 0"],
    main_body="""
def main @ use_a, use_b, done < a, b {
    stl.startup
    bit.input a
    bit.input b
    bit.cmp 8, a, b, use_a, use_a, use_b
  use_a:
    bit.print a
    ;done
  use_b:
    bit.print b
  done:
    stl.loop
}
""",
    in_bytes=b"\x05\x03",
    out_bytes=b"\x03",
)

# 0898 max_two_bytes
B(
    "0898",
    "max_two_bytes",
    "Max Two Bytes",
    value_data=["a: bit.vec 8, 0", "b: bit.vec 8, 0"],
    main_body="""
def main @ use_a, use_b, done < a, b {
    stl.startup
    bit.input a
    bit.input b
    bit.cmp 8, a, b, use_b, use_b, use_a
  use_a:
    bit.print a
    ;done
  use_b:
    bit.print b
  done:
    stl.loop
}
""",
    in_bytes=b"\x05\x03",
    out_bytes=b"\x05",
)

# 0902 byte_high_eq_low_nibble
B(
    "0902",
    "byte_high_eq_low_nibble",
    "Byte High Eq Low Nibble",
    value_data=["ch: bit.vec 8, 0"],
    main_body="""
def main @ yes, no, done < ch {
    stl.startup
    bit.input ch
    bit.cmp 4, ch, ch + 4*dw, no, yes, no
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"\xaa",
    out_bytes=b"1\n",
)

# 0903 byte_is_bit_palindrome
B(
    "0903",
    "byte_is_bit_palindrome",
    "Byte Is Bit Palindrome",
    extra_helpers=[PAIR_EQ],
    value_data=["ch: bit.vec 8, 0"],
    main_body="""
def main @ yes, no, done < ch {
    stl.startup
    bit.input ch
    rep(4, i) pair_eq_or_fail ch + i*dw, ch + (7-i)*dw, no
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"\x99",
    out_bytes=b"1\n",
)

# 0904 byte_reverse_each_nibble
B(
    "0904",
    "byte_reverse_each_nibble",
    "Byte Reverse Each Nibble",
    value_data=["ch: bit.vec 8, 0", "out: bit.vec 8, 0"],
    main_body="""
def main < ch, out {
    stl.startup
    bit.input ch
    rep(4, i) bit.mov out + i*dw, ch + (3-i)*dw
    rep(4, i) bit.mov out + (4+i)*dw, ch + (7-i)*dw
    bit.print out
    stl.loop
}
""",
    in_bytes=b"\x12",
    out_bytes=b"\x84",
)

# 0925 binary_from_gray_code
B(
    "0925",
    "binary_from_gray_code",
    "Binary From Gray Code",
    extra_helpers=[GRAY2BIN],
    value_data=["ch: bit.vec 8, 0", "out: bit.vec 8, 0"],
    main_body="""
def main < ch, out {
    stl.startup
    bit.input ch
    bit.mov out + 7*dw, ch + 7*dw
    rep(7, i) gray2bin_step out + (6-i)*dw, ch + (6-i)*dw, out + (7-i)*dw
    bit.print out
    stl.loop
}
""",
    in_bytes=b"\x07",
    out_bytes=b"\x05",
)

# 0929 count_leading_ones — from MSB
B(
    "0929",
    "count_leading_ones",
    "Count Leading Ones",
    extra_helpers=[SCAN_ONE],
    value_data=["ch: bit.vec 8, 0", "count: bit.vec 16, 0", "still: bit.bit"],
    main_body="""
def main < ch, count, still {
    stl.startup
    bit.input ch
    bit.zero 16, count
    bit.one still
    rep(8, i) scan_one_step still, count, ch + (7-i)*dw
    bit.print_dec_uint 16, count
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"\xe0",
    out_bytes=b"3\n",
)

# 0930 count_trailing_ones — from LSB
B(
    "0930",
    "count_trailing_ones",
    "Count Trailing Ones",
    extra_helpers=[SCAN_ONE],
    value_data=["ch: bit.vec 8, 0", "count: bit.vec 16, 0", "still: bit.bit"],
    main_body="""
def main < ch, count, still {
    stl.startup
    bit.input ch
    bit.zero 16, count
    bit.one still
    rep(8, i) scan_one_step still, count, ch + i*dw
    bit.print_dec_uint 16, count
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"\x07",
    out_bytes=b"3\n",
)

# 0934 isolate_lowest_set_bit — byte AND (-byte)
B(
    "0934",
    "isolate_lowest_set_bit",
    "Isolate Lowest Set Bit",
    value_data=["ch: bit.vec 8, 0", "tmp: bit.vec 8, 0"],
    main_body="""
def main < ch, tmp {
    stl.startup
    bit.input ch
    bit.mov 8, tmp, ch
    bit.not 8, tmp
    bit.inc 8, tmp
    bit.and 8, ch, tmp
    bit.print ch
    stl.loop
}
""",
    in_bytes=b"\x0c",
    out_bytes=b"\x04",
)

# 0935 broadcast_lsb_to_byte
B(
    "0935",
    "broadcast_lsb_to_byte",
    "Broadcast Lsb To Byte",
    value_data=["ch: bit.vec 8, 0", "zero_b: bit.vec 8, 0x00", "full_b: bit.vec 8, 0xff"],
    main_body="""
def main @ set, done < ch, zero_b, full_b {
    stl.startup
    bit.input ch
    bit.if1 ch, set
    bit.print zero_b
    ;done
  set:
    bit.print full_b
  done:
    stl.loop
}
""",
    in_bytes=b"\x01",
    out_bytes=b"\xff",
)

# 0931 round_up_to_multiple_of_8 — (x + 7) with low 3 bits cleared
B(
    "0931",
    "round_up_to_multiple_of_8",
    "Round Up To Multiple Of 8",
    value_data=["ch: bit.vec 8, 0", "seven: bit.vec 8, 7"],
    main_body="""
def main < ch, seven {
    stl.startup
    bit.input ch
    bit.add 8, ch, seven
    bit.zero ch + 0*dw
    bit.zero ch + 1*dw
    bit.zero ch + 2*dw
    bit.print ch
    stl.loop
}
""",
    in_bytes=b"\x01",
    out_bytes=b"\x08",
)

# 0932 round_down_to_multiple_of_8 — clear low 3 bits
B(
    "0932",
    "round_down_to_multiple_of_8",
    "Round Down To Multiple Of 8",
    value_data=["ch: bit.vec 8, 0"],
    main_body="""
def main < ch {
    stl.startup
    bit.input ch
    bit.zero ch + 0*dw
    bit.zero ch + 1*dw
    bit.zero ch + 2*dw
    bit.print ch
    stl.loop
}
""",
    in_bytes=b"\x0f",
    out_bytes=b"\x08",
)

# 0926 next_power_of_2_byte — smallest power of 2 >= input
B(
    "0926",
    "next_power_of_2_byte",
    "Next Power Of 2 Byte",
    value_data=["ch: bit.vec 8, 0", "p: bit.vec 8, 0"],
    main_body="""
def main @ loop, shift, done < ch, p {
    stl.startup
    bit.input ch
    bit.zero 8, p
    bit.inc 8, p
  loop:
    bit.cmp 8, p, ch, shift, done, done
  shift:
    bit.shl 8, p
    ;loop
  done:
    bit.print p
    stl.loop
}
""",
    in_bytes=b"\x05",
    out_bytes=b"\x08",
)

# 0927 prev_power_of_2_byte — largest power of 2 <= input
B(
    "0927",
    "prev_power_of_2_byte",
    "Prev Power Of 2 Byte",
    value_data=["ch: bit.vec 8, 0", "p: bit.vec 8, 0", "p2: bit.vec 8, 0"],
    main_body="""
def main @ loop, grow, done < ch, p, p2 {
    stl.startup
    bit.input ch
    bit.zero 8, p
    bit.inc 8, p
  loop:
    bit.mov 8, p2, p
    bit.shl 8, p2
    bit.cmp 8, p2, ch, grow, grow, done
  grow:
    bit.shl 8, p
    ;loop
  done:
    bit.print p
    stl.loop
}
""",
    in_bytes=b"\x05",
    out_bytes=b"\x04",
)

# 0928 log2_ceil_byte — smallest k with 2^k >= byte
B(
    "0928",
    "log2_ceil_byte",
    "Log2 Ceil Byte",
    value_data=["ch: bit.vec 8, 0", "p: bit.vec 8, 0", "k: bit.vec 16, 0"],
    main_body="""
def main @ loop, shift, done < ch, p, k {
    stl.startup
    bit.input ch
    bit.zero 8, p
    bit.inc 8, p
    bit.zero 16, k
  loop:
    bit.cmp 8, p, ch, shift, done, done
  shift:
    bit.shl 8, p
    bit.inc 16, k
    ;loop
  done:
    bit.print_dec_uint 16, k
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"\x05",
    out_bytes=b"3\n",
)

print("---")
print("BATCH 13 DONE")

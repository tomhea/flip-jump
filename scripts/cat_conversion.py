"""Phase 3: conversion category — base / unit / format conversions.

Implements 28 of the 30 APPROVED conversion programs (#0339-#0368). Each is a
small arithmetic + base-output transform:

- base conversions: dec<->hex, dec<->binary, dec<->octal, binary<->hex,
  hex<->binary;
- unit conversions: temperatures (signed, floor division), distance, time,
  money, angles-of-the-clock split into H:MM / M:SS;
- format conversions: thousands grouping, zero padding, explicit sign,
  digit/letter <-> word/index, nibble <-> hex char, Roman numerals (1-10).

Two programs are DEFERRED (left APPROVED, not implemented): word_to_digit
(#0357) and roman_to_dec_1_to_10 (#0360). Both must read a variable-length
token from stdin and match it against a fixed set of words — that is parsing,
not arithmetic, and belongs in the parsing category with a proper tokenizer.

Run from the repo root:  python scripts/cat_conversion.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog_arith import emit  # noqa: E402

# ----------------------------- shared helpers -----------------------------

# Print the low 4 bits at nib as a single lowercase hex digit (0-9, a-f).
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

# Output a single '0' or '1' byte for the bit at b.
PRINT_BIT_CHAR = """
// Output the bit at b as a single ASCII '0' or '1' byte.
def print_bit_char b @ one, zero, done {
    bit.if0 b, zero
  one:
    stl.output '1'
    ;done
  zero:
    stl.output '0'
  done:
}
""".strip()

# Read one '0'/'1' byte and fold it into value: value = value*2 + bit.
SHIFT_IN_BIT = """
// value[:n] = value*2 + (next stdin byte interpreted as binary digit '0'/'1').
def shift_in_bit n, value < bin_ch, bin_bit, bin_err {
    bit.shl n, value
    bit.input bin_ch
    bit.ascii2bin bin_err, bin_bit, bin_ch
    bit.xor value, bin_bit
}
""".strip()
D_SHIFT_IN = ["bin_ch: bit.vec 8, 0", "bin_bit: bit.bit", "bin_err: bit.bit"]

# Print an 8-bit value as 8 binary chars, MSB first.
PRINT_BYTE_BINARY = """
// Print byte[:8] as eight ASCII '0'/'1' bytes, most-significant bit first.
def print_byte_binary byte {
    rep(8, i) print_bit_char byte + (7-i)*dw
}
""".strip()

# Print one decimal digit value (0-9) at d4 as an ASCII byte.
PRINT_DIGIT = """
// Print the decimal digit value at d4[:4] (0-9) as a single ASCII byte.
def print_digit d4 < dig_out {
    bit.dec2ascii dig_out, d4
    bit.print dig_out
}
""".strip()
D_DIGIT = ["dig_out: bit.vec 8, 0"]

# Signed floor division: dst = floor(num / den), den > 0.
FLOOR_DIV = """
// dst[:n] = floor(num[:n] / den[:n]) for signed num and strictly-positive den.
// idiv truncates toward zero; floor differs only when num<0 and remainder!=0.
def floor_div_into n, dst, num, den @ dec_q, done < fd_q, fd_r {
    bit.idiv n, num, den, fd_q, fd_r
    bit.if0 n, fd_r, done
    bit.if0 num + (n-1)*dw, done
  dec_q:
    bit.dec n, fd_q
  done:
    bit.mov n, dst, fd_q
}
""".strip()
D_FLOOR_DIV = ["fd_q: bit.vec 16, 0", "fd_r: bit.vec 16, 0"]

# Print value[:16] (0-99) as exactly two decimal digits, zero-padded.
PRINT_TWO_DIGITS = """
// Print value[:16] (assumed 0-99) as exactly two decimal digits (zero-padded).
def print_two_digits value < td_q, td_r, ten16, td_hi, td_lo, off0 {
    bit.div 16, value, ten16, td_q, td_r
    bit.zero 8, td_hi
    bit.mov 4, td_hi, td_q
    bit.add 8, td_hi, off0
    bit.print td_hi
    bit.zero 8, td_lo
    bit.mov 4, td_lo, td_r
    bit.add 8, td_lo, off0
    bit.print td_lo
}
""".strip()
D_TWO_DIGITS = [
    "td_q: bit.vec 16, 0",
    "td_r: bit.vec 16, 0",
    "ten16: bit.vec 16, 10",
    "td_hi: bit.vec 8, 0",
    "td_lo: bit.vec 8, 0",
    "off0: bit.vec 8, 0x30",
]

# Print value[:16] (0-999) as exactly three decimal digits, zero-padded.
PRINT_THREE_DIGITS = """
// Print value[:16] (assumed 0-999) as exactly three decimal digits (zero-padded).
def print_three_digits value < h_q, h_r, t_q, t_r, hundred16, ten16b, h_d, t_d, o_d, zero30 {
    bit.div 16, value, hundred16, h_q, h_r
    bit.zero 8, h_d
    bit.mov 4, h_d, h_q
    bit.add 8, h_d, zero30
    bit.print h_d
    bit.div 16, h_r, ten16b, t_q, t_r
    bit.zero 8, t_d
    bit.mov 4, t_d, t_q
    bit.add 8, t_d, zero30
    bit.print t_d
    bit.zero 8, o_d
    bit.mov 4, o_d, t_r
    bit.add 8, o_d, zero30
    bit.print o_d
}
""".strip()
D_THREE_DIGITS = [
    "h_q: bit.vec 16, 0",
    "h_r: bit.vec 16, 0",
    "t_q: bit.vec 16, 0",
    "t_r: bit.vec 16, 0",
    "hundred16: bit.vec 16, 100",
    "ten16b: bit.vec 16, 10",
    "h_d: bit.vec 8, 0",
    "t_d: bit.vec 8, 0",
    "o_d: bit.vec 8, 0",
    "zero30: bit.vec 8, 0x30",
]

# Branch helpers for value->string dispatch. There is no compare-to-constant
# form, so each target value is a pre-declared constant vector and the helper
# compares the input against it (the predicate idiom from CONVENTIONS.md).
BRANCH_EQ4 = """
// If digit[:4] == kvec[:4], jump to target.
def branch_eq4 digit, kvec, target @ no {
    bit.cmp 4, digit, kvec, no, target, no
  no:
}
""".strip()
DIGIT_CONSTS = [f"k{v}: bit.vec 4, {v}" for v in range(9)]

BRANCH_EQ16 = """
// If value[:16] == kvec[:16], jump to target.
def branch_eq16 value, kvec, target @ no {
    bit.cmp 16, value, kvec, no, target, no
  no:
}
""".strip()
ROMAN_CONSTS = [f"v{v}: bit.vec 16, {v}" for v in range(1, 10)]

# A width-parameterized decimal reader. The shared read_decimal carries a
# 16-bit digit holder, so bit.add n would read past it for n>16; this version
# zero-extends its own n-bit digit. Used by dec_to_thousands_grouped (24-bit,
# to hold values up to 999999).
READ_DECIMAL_WIDE = """
// Read an unsigned decimal (digits until `\\n` or `\\0`) into value[:n].
def read_decimal_wide n, value @ loop, add_digit, end < rw_ch, rw_nl, rw_digit, rw_err {
    bit.zero n, value
  loop:
    bit.input rw_ch
    bit.if0 8, rw_ch, end
    bit.cmp 8, rw_ch, rw_nl, add_digit, end, add_digit
  add_digit:
    bit.mul10 n, value
    bit.zero n, rw_digit
    bit.ascii2dec rw_err, rw_digit, rw_ch
    bit.add n, value, rw_digit
    ;loop
  end:
}
""".strip()
D_READ_WIDE = ["rw_ch: bit.vec 8, 0", "rw_nl: bit.vec 8, '\\n'", "rw_digit: bit.vec 24, 0", "rw_err: bit.bit"]


def C(nnnn, slug, name, **kw):
    emit("conversion", nnnn, slug, name, **kw)


# ============================ base conversions ============================

# 0339 dec_to_hex — decimal 0-255 -> two lowercase hex digits.
C(
    "0339",
    "dec_to_hex",
    "Dec To Hex",
    unsigned=True,
    extra_helpers=[PRINT_HEX_NIBBLE],
    value_data=["value: bit.vec 8, 0"],
    extra_data=D_HEXNIB,
    main_body="""
def main < value {
    stl.startup
    read_decimal 8, value
    print_hex_nibble value + 4*dw
    print_hex_nibble value
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"255\n\0",
    out_bytes=b"ff\n",
)

# 0340 hex_to_dec — two lowercase hex digits -> decimal 0-255.
C(
    "0340",
    "hex_to_dec",
    "Hex To Dec",
    value_data=[
        "ch: bit.vec 8, 0",
        "hi: bit.vec 4, 0",
        "lo: bit.vec 4, 0",
        "value: bit.vec 16, 0",
        "err: bit.bit",
    ],
    main_body="""
def main < ch, hi, lo, value, err {
    stl.startup
    bit.input ch
    bit.ascii2hex err, hi, ch
    bit.input ch
    bit.ascii2hex err, lo, ch
    bit.zero 16, value
    bit.mov 4, value, lo
    bit.mov 4, value + 4*dw, hi
    bit.print_dec_uint 16, value
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"ff\n",
    out_bytes=b"255\n",
)

# 0341 dec_to_binary — decimal 0-255 -> 8-char binary string (MSB first).
C(
    "0341",
    "dec_to_binary",
    "Dec To Binary",
    unsigned=True,
    extra_helpers=[PRINT_BIT_CHAR, PRINT_BYTE_BINARY],
    value_data=["value: bit.vec 8, 0"],
    main_body="""
def main < value {
    stl.startup
    read_decimal 8, value
    print_byte_binary value
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"5\n\0",
    out_bytes=b"00000101\n",
)

# 0342 binary_to_dec — 8-char binary string -> decimal 0-255.
C(
    "0342",
    "binary_to_dec",
    "Binary To Dec",
    extra_helpers=[SHIFT_IN_BIT],
    value_data=["value: bit.vec 16, 0", "skip: bit.vec 8, 0"],
    extra_data=D_SHIFT_IN,
    main_body="""
def main < value, skip {
    stl.startup
    bit.zero 16, value
    rep(8, i) shift_in_bit 16, value
    bit.input skip
    bit.print_dec_uint 16, value
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"00000101\n",
    out_bytes=b"5\n",
)

# 0343 dec_to_octal — decimal 0-63 -> two octal digits.
C(
    "0343",
    "dec_to_octal",
    "Dec To Octal",
    unsigned=True,
    extra_helpers=[PRINT_DIGIT],
    value_data=["value: bit.vec 16, 0", "q: bit.vec 16, 0", "r: bit.vec 16, 0", "eight: bit.vec 16, 8"],
    extra_data=D_DIGIT,
    main_body="""
def main < value, q, r, eight {
    stl.startup
    read_decimal 16, value
    bit.div 16, value, eight, q, r
    print_digit q
    print_digit r
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"63\n\0",
    out_bytes=b"77\n",
)

# 0344 octal_to_dec — two octal digits -> decimal 0-63.
# value = hi*8 + lo; *8 is three left-shifts (bit.mul is unusable in this STL).
C(
    "0344",
    "octal_to_dec",
    "Octal To Dec",
    value_data=[
        "ch: bit.vec 8, 0",
        "digit: bit.vec 4, 0",
        "value: bit.vec 16, 0",
        "acc: bit.vec 16, 0",
        "err: bit.bit",
    ],
    main_body="""
def main < ch, digit, value, acc, err {
    stl.startup
    bit.zero 16, value
    bit.input ch
    bit.ascii2dec err, digit, ch
    bit.mov 4, value, digit
    rep(3, i) bit.shl 16, value
    bit.input ch
    bit.ascii2dec err, digit, ch
    bit.zero 16, acc
    bit.mov 4, acc, digit
    bit.add 16, value, acc
    bit.input ch
    bit.print_dec_uint 16, value
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"77\n",
    out_bytes=b"63\n",
)

# 0345 binary_to_hex — 8-char binary string -> two lowercase hex digits.
C(
    "0345",
    "binary_to_hex",
    "Binary To Hex",
    extra_helpers=[SHIFT_IN_BIT, PRINT_HEX_NIBBLE],
    value_data=["value: bit.vec 8, 0", "skip: bit.vec 8, 0"],
    extra_data=D_HEXNIB + D_SHIFT_IN,
    main_body="""
def main < value, skip {
    stl.startup
    bit.zero 8, value
    rep(8, i) shift_in_bit 8, value
    bit.input skip
    print_hex_nibble value + 4*dw
    print_hex_nibble value
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"01001010\n",
    out_bytes=b"4a\n",
)

# 0346 hex_to_binary — two lowercase hex digits -> 8-char binary string.
C(
    "0346",
    "hex_to_binary",
    "Hex To Binary",
    extra_helpers=[PRINT_BIT_CHAR, PRINT_BYTE_BINARY],
    value_data=[
        "ch: bit.vec 8, 0",
        "hi: bit.vec 4, 0",
        "lo: bit.vec 4, 0",
        "byte: bit.vec 8, 0",
        "err: bit.bit",
    ],
    main_body="""
def main < ch, hi, lo, byte, err {
    stl.startup
    bit.input ch
    bit.ascii2hex err, hi, ch
    bit.input ch
    bit.ascii2hex err, lo, ch
    bit.zero 8, byte
    bit.mov 4, byte, lo
    bit.mov 4, byte + 4*dw, hi
    print_byte_binary byte
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"4a\n",
    out_bytes=b"01001010\n",
)


# ====================== unit conversions: temperature ======================

# 0347 celsius_to_fahrenheit — floor(C*9/5 + 32), signed.
C(
    "0347",
    "celsius_to_fahrenheit",
    "Celsius To Fahrenheit",
    signed=True,
    mul=True,
    extra_helpers=[FLOOR_DIV],
    value_data=[
        "value: bit.vec 16, 0",
        "prod: bit.vec 16, 0",
        "result: bit.vec 16, 0",
        "nine: bit.vec 16, 9",
        "five: bit.vec 16, 5",
        "thirtytwo: bit.vec 16, 32",
    ],
    extra_data=D_FLOOR_DIV,
    main_body="""
def main < value, prod, result, nine, five, thirtytwo {
    stl.startup
    read_signed_decimal 16, value
    mul_into 16, prod, value, nine
    floor_div_into 16, result, prod, five
    bit.add 16, result, thirtytwo
    bit.print_dec_int 16, result
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"-1\n\0",
    out_bytes=b"30\n",
)

# 0348 fahrenheit_to_celsius — floor((F-32)*5/9), signed.
C(
    "0348",
    "fahrenheit_to_celsius",
    "Fahrenheit To Celsius",
    signed=True,
    mul=True,
    extra_helpers=[FLOOR_DIV],
    value_data=[
        "value: bit.vec 16, 0",
        "prod: bit.vec 16, 0",
        "result: bit.vec 16, 0",
        "five: bit.vec 16, 5",
        "nine: bit.vec 16, 9",
        "thirtytwo: bit.vec 16, 32",
    ],
    extra_data=D_FLOOR_DIV,
    main_body="""
def main < value, prod, result, five, nine, thirtytwo {
    stl.startup
    read_signed_decimal 16, value
    bit.sub 16, value, thirtytwo
    mul_into 16, prod, value, five
    floor_div_into 16, result, prod, nine
    bit.print_dec_int 16, result
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"212\n\0",
    out_bytes=b"100\n",
)


# ====================== unit conversions: distance/time ======================

# 0349 km_to_miles — floor(km*5/8).
C(
    "0349",
    "km_to_miles",
    "Km To Miles",
    unsigned=True,
    mul=True,
    value_data=[
        "value: bit.vec 16, 0",
        "prod: bit.vec 16, 0",
        "q: bit.vec 16, 0",
        "r: bit.vec 16, 0",
        "five: bit.vec 16, 5",
        "eight: bit.vec 16, 8",
    ],
    main_body="""
def main < value, prod, q, r, five, eight {
    stl.startup
    read_decimal 16, value
    mul_into 16, prod, value, five
    bit.div 16, prod, eight, q, r
    bit.print_dec_uint 16, q
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"100\n\0",
    out_bytes=b"62\n",
)

# 0350 miles_to_km — floor(miles*8/5).
C(
    "0350",
    "miles_to_km",
    "Miles To Km",
    unsigned=True,
    mul=True,
    value_data=[
        "value: bit.vec 16, 0",
        "prod: bit.vec 16, 0",
        "q: bit.vec 16, 0",
        "r: bit.vec 16, 0",
        "eight: bit.vec 16, 8",
        "five: bit.vec 16, 5",
    ],
    main_body="""
def main < value, prod, q, r, eight, five {
    stl.startup
    read_decimal 16, value
    mul_into 16, prod, value, eight
    bit.div 16, prod, five, q, r
    bit.print_dec_uint 16, q
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"60\n\0",
    out_bytes=b"96\n",
)

# 0351 minutes_to_hours_minutes — total minutes -> H:MM.
C(
    "0351",
    "minutes_to_hours_minutes",
    "Minutes To Hours Minutes",
    unsigned=True,
    extra_helpers=[PRINT_TWO_DIGITS],
    value_data=["value: bit.vec 16, 0", "q: bit.vec 16, 0", "r: bit.vec 16, 0", "sixty: bit.vec 16, 60"],
    extra_data=D_TWO_DIGITS,
    main_body="""
def main < value, q, r, sixty {
    stl.startup
    read_decimal 16, value
    bit.div 16, value, sixty, q, r
    bit.print_dec_uint 16, q
    stl.output ':'
    print_two_digits r
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"555\n\0",
    out_bytes=b"9:15\n",
)

# 0352 seconds_to_minutes_seconds — total seconds -> M:SS.
C(
    "0352",
    "seconds_to_minutes_seconds",
    "Seconds To Minutes Seconds",
    unsigned=True,
    extra_helpers=[PRINT_TWO_DIGITS],
    value_data=["value: bit.vec 16, 0", "q: bit.vec 16, 0", "r: bit.vec 16, 0", "sixty: bit.vec 16, 60"],
    extra_data=D_TWO_DIGITS,
    main_body="""
def main < value, q, r, sixty {
    stl.startup
    read_decimal 16, value
    bit.div 16, value, sixty, q, r
    bit.print_dec_uint 16, q
    stl.output ':'
    print_two_digits r
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"3599\n\0",
    out_bytes=b"59:59\n",
)

# 0353 hours_to_minutes — hours*60.
C(
    "0353",
    "hours_to_minutes",
    "Hours To Minutes",
    unsigned=True,
    mul=True,
    value_data=["value: bit.vec 16, 0", "prod: bit.vec 16, 0", "sixty: bit.vec 16, 60"],
    main_body="""
def main < value, prod, sixty {
    stl.startup
    read_decimal 16, value
    mul_into 16, prod, value, sixty
    bit.print_dec_uint 16, prod
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"24\n\0",
    out_bytes=b"1440\n",
)

# 0354 days_to_hours — days*24.
C(
    "0354",
    "days_to_hours",
    "Days To Hours",
    unsigned=True,
    mul=True,
    value_data=["value: bit.vec 16, 0", "prod: bit.vec 16, 0", "twentyfour: bit.vec 16, 24"],
    main_body="""
def main < value, prod, twentyfour {
    stl.startup
    read_decimal 16, value
    mul_into 16, prod, value, twentyfour
    bit.print_dec_uint 16, prod
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"30\n\0",
    out_bytes=b"720\n",
)


# ======================== format conversions ========================

# 0355 dec_to_thousands_grouped — 0-999999 with comma thousands separators.
# 999999 needs 20 bits, so value/hi/lo are 32-bit; the low group (0-999) is
# copied to a 16-bit holder for print_three_digits.
C(
    "0355",
    "dec_to_thousands_grouped",
    "Dec To Thousands Grouped",
    extra_helpers=[READ_DECIMAL_WIDE, PRINT_THREE_DIGITS],
    value_data=[
        "value: bit.vec 24, 0",
        "hi: bit.vec 24, 0",
        "lo: bit.vec 24, 0",
        "hi16: bit.vec 16, 0",
        "lo16: bit.vec 16, 0",
        "thousand: bit.vec 24, 1000",
    ],
    extra_data=D_READ_WIDE + D_THREE_DIGITS,
    main_body="""
def main @ plain, done < value, hi, lo, hi16, lo16, thousand {
    stl.startup
    read_decimal_wide 24, value
    bit.div 24, value, thousand, hi, lo
    bit.mov 16, hi16, hi
    bit.mov 16, lo16, lo
    bit.if0 24, hi, plain
    bit.print_dec_uint 16, hi16
    stl.output ','
    print_three_digits lo16
    ;done
  plain:
    bit.print_dec_uint 16, lo16
  done:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"12345\n\0",
    out_bytes=b"12,345\n",
)

# 0356 word_zero_to_nine — single digit 0-9 -> English word.
# Dispatch on the parsed digit by comparing it to each 4-bit constant; the
# final word (nine) is the fall-through, so only nine checks are needed.
C(
    "0356",
    "word_zero_to_nine",
    "Word Zero To Nine",
    extra_helpers=[BRANCH_EQ4],
    value_data=["ch: bit.vec 8, 0", "digit: bit.vec 4, 0", "err: bit.bit"],
    extra_data=DIGIT_CONSTS,
    main_body="""
def main @ d0, d1, d2, d3, d4, d5, d6, d7, d8, d9, done < ch, digit, err, \\
        k0, k1, k2, k3, k4, k5, k6, k7, k8 {
    stl.startup
    bit.input ch
    bit.ascii2dec err, digit, ch
    bit.input ch
    branch_eq4 digit, k0, d0
    branch_eq4 digit, k1, d1
    branch_eq4 digit, k2, d2
    branch_eq4 digit, k3, d3
    branch_eq4 digit, k4, d4
    branch_eq4 digit, k5, d5
    branch_eq4 digit, k6, d6
    branch_eq4 digit, k7, d7
    branch_eq4 digit, k8, d8
    ;d9
  d0:
    stl.output "zero"
    ;done
  d1:
    stl.output "one"
    ;done
  d2:
    stl.output "two"
    ;done
  d3:
    stl.output "three"
    ;done
  d4:
    stl.output "four"
    ;done
  d5:
    stl.output "five"
    ;done
  d6:
    stl.output "six"
    ;done
  d7:
    stl.output "seven"
    ;done
  d8:
    stl.output "eight"
    ;done
  d9:
    stl.output "nine"
  done:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"3\n\0",
    out_bytes=b"three\n",
)

# 0358 zero_pad_to_4 — 0-9999 -> 4-char zero-padded decimal.
C(
    "0358",
    "zero_pad_to_4",
    "Zero Pad To 4",
    unsigned=True,
    extra_helpers=[PRINT_DIGIT],
    value_data=[
        "value: bit.vec 16, 0",
        "q: bit.vec 16, 0",
        "r: bit.vec 16, 0",
        "thousand: bit.vec 16, 1000",
        "hundred: bit.vec 16, 100",
        "ten: bit.vec 16, 10",
        "nib: bit.vec 4, 0",
    ],
    extra_data=D_DIGIT,
    main_body="""
def main < value, q, r, thousand, hundred, ten, nib {
    stl.startup
    read_decimal 16, value
    bit.div 16, value, thousand, q, r
    bit.mov 4, nib, q
    print_digit nib
    bit.div 16, r, hundred, q, r
    bit.mov 4, nib, q
    print_digit nib
    bit.div 16, r, ten, q, r
    bit.mov 4, nib, q
    print_digit nib
    bit.mov 4, nib, r
    print_digit nib
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"7\n\0",
    out_bytes=b"0007\n",
)

# 0359 roman_numeral_1_to_10 — decimal 1-10 -> Roman numeral.
# Dispatch on the value against constants v1..v9; 10 (X) is the fall-through.
C(
    "0359",
    "roman_numeral_1_to_10",
    "Roman Numeral 1 To 10",
    unsigned=True,
    extra_helpers=[BRANCH_EQ16],
    value_data=["value: bit.vec 16, 0"],
    extra_data=ROMAN_CONSTS,
    main_body="""
def main @ r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, done < value, \\
        v1, v2, v3, v4, v5, v6, v7, v8, v9 {
    stl.startup
    read_decimal 16, value
    branch_eq16 value, v1, r1
    branch_eq16 value, v2, r2
    branch_eq16 value, v3, r3
    branch_eq16 value, v4, r4
    branch_eq16 value, v5, r5
    branch_eq16 value, v6, r6
    branch_eq16 value, v7, r7
    branch_eq16 value, v8, r8
    branch_eq16 value, v9, r9
    ;r10
  r1:
    stl.output "I"
    ;done
  r2:
    stl.output "II"
    ;done
  r3:
    stl.output "III"
    ;done
  r4:
    stl.output "IV"
    ;done
  r5:
    stl.output "V"
    ;done
  r6:
    stl.output "VI"
    ;done
  r7:
    stl.output "VII"
    ;done
  r8:
    stl.output "VIII"
    ;done
  r9:
    stl.output "IX"
    ;done
  r10:
    stl.output "X"
  done:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"4\n\0",
    out_bytes=b"IV\n",
)


# ======================== letter / index conversions ========================

# 0361 lowercase_letter_to_index — byte a-z -> 0-based index.
C(
    "0361",
    "lowercase_letter_to_index",
    "Lowercase Letter To Index",
    value_data=["ch: bit.vec 8, 0", "value: bit.vec 8, 0", "lower_a: bit.vec 8, 'a'"],
    main_body="""
def main < ch, value, lower_a {
    stl.startup
    bit.input ch
    bit.mov 8, value, ch
    bit.sub 8, value, lower_a
    bit.print_dec_uint 8, value
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"c",
    out_bytes=b"2\n",
)

# 0362 index_to_lowercase_letter — 0-25 -> lowercase letter byte (no newline).
C(
    "0362",
    "index_to_lowercase_letter",
    "Index To Lowercase Letter",
    unsigned=True,
    value_data=["value: bit.vec 8, 0", "lower_a: bit.vec 8, 'a'"],
    main_body="""
def main < value, lower_a {
    stl.startup
    read_decimal 8, value
    bit.add 8, value, lower_a
    bit.print value
    stl.loop
}
""",
    in_bytes=b"25\n\0",
    out_bytes=b"z",
)

# 0363 uppercase_letter_to_index — byte A-Z -> 0-based index.
C(
    "0363",
    "uppercase_letter_to_index",
    "Uppercase Letter To Index",
    value_data=["ch: bit.vec 8, 0", "value: bit.vec 8, 0", "upper_a: bit.vec 8, 'A'"],
    main_body="""
def main < ch, value, upper_a {
    stl.startup
    bit.input ch
    bit.mov 8, value, ch
    bit.sub 8, value, upper_a
    bit.print_dec_uint 8, value
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"C",
    out_bytes=b"2\n",
)


# ======================== money / nibble conversions ========================

# 0364 dollars_to_cents — dollars*100.
C(
    "0364",
    "dollars_to_cents",
    "Dollars To Cents",
    unsigned=True,
    mul=True,
    value_data=["value: bit.vec 16, 0", "prod: bit.vec 16, 0", "hundred: bit.vec 16, 100"],
    main_body="""
def main < value, prod, hundred {
    stl.startup
    read_decimal 16, value
    mul_into 16, prod, value, hundred
    bit.print_dec_uint 16, prod
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"99\n\0",
    out_bytes=b"9900\n",
)

# 0365 cents_to_dollars_cents — cents -> <dollars>.<cc>.
C(
    "0365",
    "cents_to_dollars_cents",
    "Cents To Dollars Cents",
    unsigned=True,
    extra_helpers=[PRINT_TWO_DIGITS],
    value_data=["value: bit.vec 16, 0", "q: bit.vec 16, 0", "r: bit.vec 16, 0", "hundred: bit.vec 16, 100"],
    extra_data=D_TWO_DIGITS,
    main_body="""
def main < value, q, r, hundred {
    stl.startup
    read_decimal 16, value
    bit.div 16, value, hundred, q, r
    bit.print_dec_uint 16, q
    stl.output '.'
    print_two_digits r
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"9999\n\0",
    out_bytes=b"99.99\n",
)

# 0366 nibble_to_hex_char — decimal 0-15 -> lowercase hex char + newline.
C(
    "0366",
    "nibble_to_hex_char",
    "Nibble To Hex Char",
    unsigned=True,
    extra_helpers=[PRINT_HEX_NIBBLE],
    value_data=["value: bit.vec 8, 0"],
    extra_data=D_HEXNIB,
    main_body="""
def main < value {
    stl.startup
    read_decimal 8, value
    print_hex_nibble value
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"10\n\0",
    out_bytes=b"a\n",
)

# 0367 hex_char_to_nibble — lowercase hex char -> decimal 0-15.
C(
    "0367",
    "hex_char_to_nibble",
    "Hex Char To Nibble",
    value_data=[
        "ch: bit.vec 8, 0",
        "hex: bit.vec 4, 0",
        "value: bit.vec 16, 0",
        "err: bit.bit",
    ],
    main_body="""
def main < ch, hex, value, err {
    stl.startup
    bit.input ch
    bit.ascii2hex err, hex, ch
    bit.input ch
    bit.zero 16, value
    bit.mov 4, value, hex
    bit.print_dec_uint 16, value
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"a\n",
    out_bytes=b"10\n",
)

# 0368 dec_with_explicit_sign — signed -9999..9999 -> always-signed decimal.
# print_dec_int omits the sign for non-negatives, so emit the sign byte by hand
# (negate negatives to a magnitude) and print the magnitude unsigned.
C(
    "0368",
    "dec_with_explicit_sign",
    "Dec With Explicit Sign",
    signed=True,
    value_data=["value: bit.vec 16, 0"],
    main_body="""
def main @ neg, pos, print_mag < value {
    stl.startup
    read_signed_decimal 16, value
    bit.if0 value + 15*dw, pos
  neg:
    stl.output '-'
    bit.neg 16, value
    ;print_mag
  pos:
    stl.output '+'
  print_mag:
    bit.print_dec_uint 16, value
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"5\n\0",
    out_bytes=b"+5\n",
)


print("---")
print("CAT_CONVERSION DONE")

"""Phase 3 batch 8: number_theory digit manipulation (7 programs).

digit_sum, digit_product, digit_count_small, reverse_digits, is_palindrome_num,
is_armstrong_3, happy_check_small. All use the divmod-by-10 digit loop.

Run from the repo root:  python scripts/batch08_numbertheory3.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog_arith import emit  # noqa: E402

# sum of squares of the base-10 digits of x (used by happy_check_small)
SUM_SQ_DIGITS = """
// dst = sum of squares of the base-10 digits of x (via a copy of x). x >= 0.
def sum_sq_digits_into n, dst, x @ loop, end < work, q, r, sq, ten {
    bit.zero n, dst
    bit.mov n, work, x
  loop:
    bit.div n, work, ten, q, r
    mul_into n, sq, r, r
    bit.add n, dst, sq
    bit.mov n, work, q
    bit.if0 n, work, end
    ;loop
  end:
}
""".strip()


def NT(nnnn, slug, name, **kw):
    emit("number_theory", nnnn, slug, name, **kw)


# 0158 digit_sum
NT(
    "0158",
    "digit_sum",
    "Digit Sum",
    unsigned=True,
    value_data=[
        "value: bit.vec 16, 0",
        "sum: bit.vec 16, 0",
        "q: bit.vec 16, 0",
        "r: bit.vec 16, 0",
        "ten: bit.vec 16, 10",
    ],
    main_body="""
def main @ loop, end < value, sum, q, r, ten {
    stl.startup
    read_decimal 16, value
    bit.zero 16, sum
  loop:
    bit.div 16, value, ten, q, r
    bit.add 16, sum, r
    bit.mov 16, value, q
    bit.if0 16, value, end
    ;loop
  end:
    bit.print_dec_uint 16, sum
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"123\n\0",
    out_bytes=b"6\n",
)

# 0159 digit_product
NT(
    "0159",
    "digit_product",
    "Digit Product",
    unsigned=True,
    mul=True,
    value_data=[
        "value: bit.vec 16, 0",
        "product: bit.vec 16, 1",
        "tmp: bit.vec 16, 0",
        "q: bit.vec 16, 0",
        "r: bit.vec 16, 0",
        "ten: bit.vec 16, 10",
    ],
    main_body="""
def main @ loop, end < value, product, tmp, q, r, ten {
    stl.startup
    read_decimal 16, value
  loop:
    bit.div 16, value, ten, q, r
    mul_into 16, tmp, product, r
    bit.mov 16, product, tmp
    bit.mov 16, value, q
    bit.if0 16, value, end
    ;loop
  end:
    bit.print_dec_uint 16, product
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"234\n\0",
    out_bytes=b"24\n",
)

# 0160 digit_count_small
NT(
    "0160",
    "digit_count_small",
    "Digit Count Small",
    unsigned=True,
    value_data=[
        "value: bit.vec 16, 0",
        "count: bit.vec 16, 0",
        "q: bit.vec 16, 0",
        "r: bit.vec 16, 0",
        "ten: bit.vec 16, 10",
    ],
    main_body="""
def main @ loop, end < value, count, q, r, ten {
    stl.startup
    read_decimal 16, value
    bit.zero 16, count
  loop:
    bit.inc 16, count
    bit.div 16, value, ten, q, r
    bit.mov 16, value, q
    bit.if0 16, value, end
    ;loop
  end:
    bit.print_dec_uint 16, count
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"42\n\0",
    out_bytes=b"2\n",
)

# 0161 reverse_digits
NT(
    "0161",
    "reverse_digits",
    "Reverse Digits",
    unsigned=True,
    value_data=[
        "value: bit.vec 16, 0",
        "rev: bit.vec 16, 0",
        "q: bit.vec 16, 0",
        "r: bit.vec 16, 0",
        "ten: bit.vec 16, 10",
    ],
    main_body="""
def main @ loop, end < value, rev, q, r, ten {
    stl.startup
    read_decimal 16, value
    bit.zero 16, rev
  loop:
    bit.div 16, value, ten, q, r
    bit.mul10 16, rev
    bit.add 16, rev, r
    bit.mov 16, value, q
    bit.if0 16, value, end
    ;loop
  end:
    bit.print_dec_uint 16, rev
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"123\n\0",
    out_bytes=b"321\n",
)

# 0157 is_palindrome_num — reverse a copy, compare to original
NT(
    "0157",
    "is_palindrome_num",
    "Is Palindrome Num",
    unsigned=True,
    value_data=[
        "value: bit.vec 16, 0",
        "work: bit.vec 16, 0",
        "rev: bit.vec 16, 0",
        "q: bit.vec 16, 0",
        "r: bit.vec 16, 0",
        "ten: bit.vec 16, 10",
    ],
    main_body="""
def main @ loop, check, yes, no, done < value, work, rev, q, r, ten {
    stl.startup
    read_decimal 16, value
    bit.mov 16, work, value
    bit.zero 16, rev
  loop:
    bit.div 16, work, ten, q, r
    bit.mul10 16, rev
    bit.add 16, rev, r
    bit.mov 16, work, q
    bit.if0 16, work, check
    ;loop
  check:
    bit.cmp 16, rev, value, no, yes, no
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"121\n\0",
    out_bytes=b"1\n",
)

# 0162 is_armstrong_3 — N == sum of cubes of its digits
NT(
    "0162",
    "is_armstrong_3",
    "Is Armstrong 3",
    unsigned=True,
    mul=True,
    value_data=[
        "value: bit.vec 16, 0",
        "work: bit.vec 16, 0",
        "sum: bit.vec 16, 0",
        "sq: bit.vec 16, 0",
        "cube: bit.vec 16, 0",
        "q: bit.vec 16, 0",
        "r: bit.vec 16, 0",
        "ten: bit.vec 16, 10",
    ],
    main_body="""
def main @ loop, check, yes, no, done < value, work, sum, sq, cube, q, r, ten {
    stl.startup
    read_decimal 16, value
    bit.mov 16, work, value
    bit.zero 16, sum
  loop:
    bit.div 16, work, ten, q, r
    mul_into 16, sq, r, r
    mul_into 16, cube, sq, r
    bit.add 16, sum, cube
    bit.mov 16, work, q
    bit.if0 16, work, check
    ;loop
  check:
    bit.cmp 16, sum, value, no, yes, no
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"153\n\0",
    out_bytes=b"1\n",
)

# 0163 happy_check_small — iterate sum-of-squared-digits until 1 (happy) or 4 (cycle)
NT(
    "0163",
    "happy_check_small",
    "Happy Check Small",
    unsigned=True,
    mul=True,
    extra_helpers=[SUM_SQ_DIGITS],
    value_data=[
        "value: bit.vec 16, 0",
        "newval: bit.vec 16, 0",
        "one: bit.vec 16, 1",
        "four: bit.vec 16, 4",
        "work: bit.vec 16, 0",
        "q: bit.vec 16, 0",
        "r: bit.vec 16, 0",
        "sq: bit.vec 16, 0",
        "ten: bit.vec 16, 10",
    ],
    main_body="""
def main @ loop, cont, cont2, happy, unhappy, done < value, newval, one, four {
    stl.startup
    read_decimal 16, value
  loop:
    bit.cmp 16, value, one, cont, happy, cont
  cont:
    bit.cmp 16, value, four, cont2, unhappy, cont2
  cont2:
    sum_sq_digits_into 16, newval, value
    bit.mov 16, value, newval
    ;loop
  happy:
    stl.output "1\\n"
    ;done
  unhappy:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"7\n\0",
    out_bytes=b"1\n",
)

print("---")
print("BATCH 8 DONE")

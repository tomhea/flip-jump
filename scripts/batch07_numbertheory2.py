"""Phase 3 batch 7: number_theory sequences & perfect powers (8 programs).

fib_n, fib_seq_n, is_fib_small, lucas_n, collatz_steps, collatz_sequence,
is_square_small, is_cube_small. Digit-manipulation programs are batch 8.

Run from the repo root:  python scripts/batch07_numbertheory2.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog_arith import emit  # noqa: E402


def NT(nnnn, slug, name, **kw):
    emit("number_theory", nnnn, slug, name, **kw)


# 0151 fib_n — F(N), F(0)=0, F(1)=1
NT(
    "0151",
    "fib_n",
    "Fib N",
    unsigned=True,
    value_data=["value: bit.vec 16, 0", "fa: bit.vec 16, 0", "fb: bit.vec 16, 0", "tmp: bit.vec 16, 0"],
    main_body="""
def main @ loop, end < value, fa, fb, tmp {
    stl.startup
    read_decimal 16, value
    bit.zero 16, fa
    bit.zero 16, fb
    bit.inc 16, fb
  loop:
    bit.if0 16, value, end
    bit.mov 16, tmp, fa
    bit.mov 16, fa, fb
    bit.add 16, fb, tmp
    bit.dec 16, value
    ;loop
  end:
    bit.print_dec_uint 16, fa
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"10\n\0",
    out_bytes=b"55\n",
)

# 0152 fib_seq_n — F(0)..F(N), one per line
NT(
    "0152",
    "fib_seq_n",
    "Fib Seq N",
    unsigned=True,
    value_data=[
        "limit: bit.vec 16, 0",
        "idx: bit.vec 16, 0",
        "fa: bit.vec 16, 0",
        "fb: bit.vec 16, 0",
        "tmp: bit.vec 16, 0",
    ],
    main_body="""
def main @ loop, body, end < limit, idx, fa, fb, tmp {
    stl.startup
    read_decimal 16, limit
    bit.zero 16, fa
    bit.zero 16, fb
    bit.inc 16, fb
    bit.zero 16, idx
  loop:
    bit.cmp 16, idx, limit, body, body, end
  body:
    bit.print_dec_uint 16, fa
    stl.output '\\n'
    bit.mov 16, tmp, fa
    bit.mov 16, fa, fb
    bit.add 16, fb, tmp
    bit.inc 16, idx
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"5\n\0",
    out_bytes=b"0\n1\n1\n2\n3\n5\n",
)

# 0153 is_fib_small — is N a Fibonacci number?
NT(
    "0153",
    "is_fib_small",
    "Is Fib Small",
    unsigned=True,
    value_data=["value: bit.vec 16, 0", "fa: bit.vec 16, 0", "fb: bit.vec 16, 0", "tmp: bit.vec 16, 0"],
    main_body="""
def main @ loop, step, yes, no, done < value, fa, fb, tmp {
    stl.startup
    read_decimal 16, value
    bit.zero 16, fa
    bit.zero 16, fb
    bit.inc 16, fb
  loop:
    bit.cmp 16, fa, value, step, yes, no
  step:
    bit.mov 16, tmp, fa
    bit.mov 16, fa, fb
    bit.add 16, fb, tmp
    ;loop
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"13\n\0",
    out_bytes=b"1\n",
)

# 0154 lucas_n — L(N), L(0)=2, L(1)=1
NT(
    "0154",
    "lucas_n",
    "Lucas N",
    unsigned=True,
    value_data=["value: bit.vec 16, 0", "la: bit.vec 16, 0", "lb: bit.vec 16, 0", "tmp: bit.vec 16, 0"],
    main_body="""
def main @ loop, end < value, la, lb, tmp {
    stl.startup
    read_decimal 16, value
    bit.zero 16, la
    bit.inc 16, la
    bit.inc 16, la
    bit.zero 16, lb
    bit.inc 16, lb
  loop:
    bit.if0 16, value, end
    bit.mov 16, tmp, la
    bit.mov 16, la, lb
    bit.add 16, lb, tmp
    bit.dec 16, value
    ;loop
  end:
    bit.print_dec_uint 16, la
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"5\n\0",
    out_bytes=b"11\n",
)

# 0155 collatz_steps — number of 3n+1/n2 steps to reach 1
NT(
    "0155",
    "collatz_steps",
    "Collatz Steps",
    unsigned=True,
    mul=True,
    value_data=[
        "value: bit.vec 16, 0",
        "count: bit.vec 16, 0",
        "tmp: bit.vec 16, 0",
        "q: bit.vec 16, 0",
        "r: bit.vec 16, 0",
        "one: bit.vec 16, 1",
        "two: bit.vec 16, 2",
        "three: bit.vec 16, 3",
    ],
    main_body="""
def main @ loop, step, even, after, end < value, count, tmp, q, r, one, two, three {
    stl.startup
    read_decimal 16, value
    bit.zero 16, count
  loop:
    bit.cmp 16, value, one, step, end, step
  step:
    bit.if0 value, even
    mul_into 16, tmp, value, three
    bit.mov 16, value, tmp
    bit.inc 16, value
    ;after
  even:
    bit.div 16, value, two, q, r
    bit.mov 16, value, q
  after:
    bit.inc 16, count
    ;loop
  end:
    bit.print_dec_uint 16, count
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"6\n\0",
    out_bytes=b"8\n",
)

# 0156 collatz_sequence — print the sequence from N down to 1
NT(
    "0156",
    "collatz_sequence",
    "Collatz Sequence",
    unsigned=True,
    mul=True,
    value_data=[
        "value: bit.vec 16, 0",
        "tmp: bit.vec 16, 0",
        "q: bit.vec 16, 0",
        "r: bit.vec 16, 0",
        "one: bit.vec 16, 1",
        "two: bit.vec 16, 2",
        "three: bit.vec 16, 3",
    ],
    main_body="""
def main @ loop, step, even, after, end < value, tmp, q, r, one, two, three {
    stl.startup
    read_decimal 16, value
  loop:
    bit.print_dec_uint 16, value
    stl.output '\\n'
    bit.cmp 16, value, one, step, end, step
  step:
    bit.if0 value, even
    mul_into 16, tmp, value, three
    bit.mov 16, value, tmp
    bit.inc 16, value
    ;after
  even:
    bit.div 16, value, two, q, r
    bit.mov 16, value, q
  after:
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"6\n\0",
    out_bytes=b"6\n3\n10\n5\n16\n8\n4\n2\n1\n",
)

# 0164 is_square_small — is N a perfect square?
NT(
    "0164",
    "is_square_small",
    "Is Square Small",
    unsigned=True,
    mul=True,
    value_data=["value: bit.vec 16, 0", "idx: bit.vec 16, 0", "sq: bit.vec 16, 0"],
    main_body="""
def main @ loop, next, yes, no, done < value, idx, sq {
    stl.startup
    read_decimal 16, value
    bit.zero 16, idx
  loop:
    mul_into 16, sq, idx, idx
    bit.cmp 16, sq, value, next, yes, no
  next:
    bit.inc 16, idx
    ;loop
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"16\n\0",
    out_bytes=b"1\n",
)

# 0165 is_cube_small — is N a perfect cube?
NT(
    "0165",
    "is_cube_small",
    "Is Cube Small",
    unsigned=True,
    mul=True,
    value_data=["value: bit.vec 16, 0", "idx: bit.vec 16, 0", "sq: bit.vec 16, 0", "cube: bit.vec 16, 0"],
    main_body="""
def main @ loop, next, yes, no, done < value, idx, sq, cube {
    stl.startup
    read_decimal 16, value
    bit.zero 16, idx
  loop:
    mul_into 16, sq, idx, idx
    mul_into 16, cube, sq, idx
    bit.cmp 16, cube, value, next, yes, no
  next:
    bit.inc 16, idx
    ;loop
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"27\n\0",
    out_bytes=b"1\n",
)

print("---")
print("BATCH 7 DONE")

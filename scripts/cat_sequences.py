"""Phase 3: the `sequences` category.

Integer-sequence generators. Each program either reads a small N (single ASCII
digit, or a one/two-digit decimal) and prints the first N terms, or has no input
and prints a fixed-length prefix of a named sequence. Output is either
space-separated terms + `\\n`, one term per line, or a single decimal answer.

All generators keep running state in a counter loop (no stored arrays):
- figurate numbers via incremental deltas or k(k+1)/2 style formulas,
- linear recurrences (lucas, perrin, padovan, pell, tribonacci, ...) by rotating
  a fixed window of registers,
- fibonacci-family filters / sums / squares,
- powers/multiples by repeated doubling/tripling/adding,
- derangement and catalan by their two-term recurrences.

Values stay <= 16 bits at every spec's N except `mersenne_check`, which uses
24-bit registers (2^17 - 1 = 131071) plus trial-division primality.

Deferred (need a 2-D / DP array, which this catalog avoids): `bell_first_5`,
`partition_first_5`.

Run from the repo root:  PYTHONIOENCODING=utf-8 python scripts/cat_sequences.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog_arith import emit  # noqa: E402

# --- shared helper macros -------------------------------------------------

# Print a leading space before every term except the first, then the decimal.
PRINT_SEP_DEC = """
// Print ` ` before all but the first term (tracked by `first`), then value[:n] as decimal.
def print_sep_dec n, value, first @ skip_space {
    bit.if1 first, skip_space
    stl.output ' '
  skip_space:
    bit.print_dec_uint n, value
    bit.zero first
}
""".strip()

# Trial-division primality of x[:n] into flag, testing divisors d while d*d <= x.
# The square d*d is maintained incrementally ((d+1)^2 = d^2 + 2d + 1) so the work
# is O(sqrt x) additions, not O(sqrt x) multiplications.
IS_PRIME_SQRT = """
// flag = 1 if x[:n] is prime, else 0. Trial division d = 2,3,... while d*d <= x. Assumes x >= 2.
def is_prime_sqrt_into n, flag, x @ loop, test, composite, done < ip_d, ip_dsq, ip_four, ip_q, ip_r {
    bit.one flag
    bit.zero n, ip_d
    bit.inc n, ip_d
    bit.inc n, ip_d
    bit.zero n, ip_dsq
    bit.add n, ip_dsq, ip_four
  loop:
    bit.cmp n, ip_dsq, x, test, test, done
  test:
    bit.div n, x, ip_d, ip_q, ip_r
    bit.if0 n, ip_r, composite
    bit.add n, ip_dsq, ip_d
    bit.add n, ip_dsq, ip_d
    bit.inc n, ip_dsq
    bit.inc n, ip_d
    ;loop
  composite:
    bit.zero flag
  done:
}
""".strip()

D_IS_PRIME = [
    "ip_d: bit.vec 24, 0",
    "ip_dsq: bit.vec 24, 0",
    "ip_four: bit.vec 24, 4",
    "ip_q: bit.vec 24, 0",
    "ip_r: bit.vec 24, 0",
]


def S(nnnn, slug, name, **kw):
    emit("sequences", nnnn, slug, name, **kw)


# ---------------------------------------------------------------------------
# Figurate numbers — read digit N, print first N terms space-separated.
# Each uses an incremental delta so no multiplication is needed.
# ---------------------------------------------------------------------------

# 0431 triangular_first_n — T(k) = T(k-1) + k
S(
    "0431",
    "triangular_first_n",
    "Triangular First N",
    unsigned=True,
    extra_helpers=[PRINT_SEP_DEC],
    value_data=[
        "limit: bit.vec 16, 0",
        "idx: bit.vec 16, 0",
        "term: bit.vec 16, 0",
        "first: bit.bit",
    ],
    main_body="""
def main @ loop, body, end < limit, idx, term, first {
    stl.startup
    read_decimal 16, limit
    bit.zero 16, term
    bit.zero 16, idx
    bit.one first
  loop:
    bit.cmp 16, idx, limit, body, end, end
  body:
    bit.inc 16, idx
    bit.add 16, term, idx
    print_sep_dec 16, term, first
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"5\n\0",
    out_bytes=b"1 3 6 10 15\n",
)

# 0432 square_first_n — S(k) = S(k-1) + (2k-1)
S(
    "0432",
    "square_first_n",
    "Square First N",
    unsigned=True,
    extra_helpers=[PRINT_SEP_DEC],
    value_data=[
        "limit: bit.vec 16, 0",
        "idx: bit.vec 16, 0",
        "term: bit.vec 16, 0",
        "odd: bit.vec 16, 1",
        "two: bit.vec 16, 2",
        "first: bit.bit",
    ],
    main_body="""
def main @ loop, body, end < limit, idx, term, odd, two, first {
    stl.startup
    read_decimal 16, limit
    bit.zero 16, term
    bit.zero 16, idx
    bit.zero 16, odd
    bit.inc 16, odd
    bit.one first
  loop:
    bit.cmp 16, idx, limit, body, end, end
  body:
    bit.inc 16, idx
    bit.add 16, term, odd
    bit.add 16, odd, two
    print_sep_dec 16, term, first
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"5\n\0",
    out_bytes=b"1 4 9 16 25\n",
)

# 0433 pentagonal_first_n — P(k) = P(k-1) + (3k-2); delta increases by 3
S(
    "0433",
    "pentagonal_first_n",
    "Pentagonal First N",
    unsigned=True,
    extra_helpers=[PRINT_SEP_DEC],
    value_data=[
        "limit: bit.vec 16, 0",
        "idx: bit.vec 16, 0",
        "term: bit.vec 16, 0",
        "delta: bit.vec 16, 1",
        "three: bit.vec 16, 3",
        "first: bit.bit",
    ],
    main_body="""
def main @ loop, body, end < limit, idx, term, delta, three, first {
    stl.startup
    read_decimal 16, limit
    bit.zero 16, term
    bit.zero 16, idx
    bit.zero 16, delta
    bit.inc 16, delta
    bit.one first
  loop:
    bit.cmp 16, idx, limit, body, end, end
  body:
    bit.inc 16, idx
    bit.add 16, term, delta
    bit.add 16, delta, three
    print_sep_dec 16, term, first
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"5\n\0",
    out_bytes=b"1 5 12 22 35\n",
)

# 0434 hexagonal_first_n — H(k) = H(k-1) + (4k-3); delta increases by 4
S(
    "0434",
    "hexagonal_first_n",
    "Hexagonal First N",
    unsigned=True,
    extra_helpers=[PRINT_SEP_DEC],
    value_data=[
        "limit: bit.vec 16, 0",
        "idx: bit.vec 16, 0",
        "term: bit.vec 16, 0",
        "delta: bit.vec 16, 1",
        "four: bit.vec 16, 4",
        "first: bit.bit",
    ],
    main_body="""
def main @ loop, body, end < limit, idx, term, delta, four, first {
    stl.startup
    read_decimal 16, limit
    bit.zero 16, term
    bit.zero 16, idx
    bit.zero 16, delta
    bit.inc 16, delta
    bit.one first
  loop:
    bit.cmp 16, idx, limit, body, end, end
  body:
    bit.inc 16, idx
    bit.add 16, term, delta
    bit.add 16, delta, four
    print_sep_dec 16, term, first
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"5\n\0",
    out_bytes=b"1 6 15 28 45\n",
)

# 0435 cube_first_n — k^3 via two repeated-addition multiplies
S(
    "0435",
    "cube_first_n",
    "Cube First N",
    unsigned=True,
    mul=True,
    extra_helpers=[PRINT_SEP_DEC],
    value_data=[
        "limit: bit.vec 16, 0",
        "idx: bit.vec 16, 0",
        "sq: bit.vec 16, 0",
        "term: bit.vec 16, 0",
        "first: bit.bit",
    ],
    main_body="""
def main @ loop, body, end < limit, idx, sq, term, first {
    stl.startup
    read_decimal 16, limit
    bit.zero 16, idx
    bit.one first
  loop:
    bit.cmp 16, idx, limit, body, end, end
  body:
    bit.inc 16, idx
    mul_into 16, sq, idx, idx
    mul_into 16, term, sq, idx
    print_sep_dec 16, term, first
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"5\n\0",
    out_bytes=b"1 8 27 64 125\n",
)

# 0436 tetrahedral_first_n — Te(k) = Te(k-1) + T(k), T(k) = T(k-1) + k
S(
    "0436",
    "tetrahedral_first_n",
    "Tetrahedral First N",
    unsigned=True,
    extra_helpers=[PRINT_SEP_DEC],
    value_data=[
        "limit: bit.vec 16, 0",
        "idx: bit.vec 16, 0",
        "tri: bit.vec 16, 0",
        "term: bit.vec 16, 0",
        "first: bit.bit",
    ],
    main_body="""
def main @ loop, body, end < limit, idx, tri, term, first {
    stl.startup
    read_decimal 16, limit
    bit.zero 16, idx
    bit.zero 16, tri
    bit.zero 16, term
    bit.one first
  loop:
    bit.cmp 16, idx, limit, body, end, end
  body:
    bit.inc 16, idx
    bit.add 16, tri, idx
    bit.add 16, term, tri
    print_sep_dec 16, term, first
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"5\n\0",
    out_bytes=b"1 4 10 20 35\n",
)

# ---------------------------------------------------------------------------
# Centered figurate numbers — fixed first 5, term starts at 1 and grows by an
# arithmetic delta whose step is 3 (triangular), 4 (square), or 6 (hexagonal).
# ---------------------------------------------------------------------------

# 0458 centered_triangular_first_5 — step 3
S(
    "0458",
    "centered_triangular_first_5",
    "Centered Triangular First 5",
    extra_helpers=[PRINT_SEP_DEC],
    value_data=[
        "limit: bit.vec 16, 5",
        "idx: bit.vec 16, 0",
        "term: bit.vec 16, 1",
        "delta: bit.vec 16, 0",
        "step: bit.vec 16, 3",
        "first: bit.bit",
    ],
    main_body="""
def main @ loop, body, end < limit, idx, term, delta, step, first {
    stl.startup
    bit.one first
  loop:
    bit.cmp 16, idx, limit, body, end, end
  body:
    print_sep_dec 16, term, first
    bit.add 16, delta, step
    bit.add 16, term, delta
    bit.inc 16, idx
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"",
    out_bytes=b"1 4 10 19 31\n",
)

# 0459 centered_square_first_5 — step 4
S(
    "0459",
    "centered_square_first_5",
    "Centered Square First 5",
    extra_helpers=[PRINT_SEP_DEC],
    value_data=[
        "limit: bit.vec 16, 5",
        "idx: bit.vec 16, 0",
        "term: bit.vec 16, 1",
        "delta: bit.vec 16, 0",
        "step: bit.vec 16, 4",
        "first: bit.bit",
    ],
    main_body="""
def main @ loop, body, end < limit, idx, term, delta, step, first {
    stl.startup
    bit.one first
  loop:
    bit.cmp 16, idx, limit, body, end, end
  body:
    print_sep_dec 16, term, first
    bit.add 16, delta, step
    bit.add 16, term, delta
    bit.inc 16, idx
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"",
    out_bytes=b"1 5 13 25 41\n",
)

# 0460 centered_hexagonal_first_5 — step 6
S(
    "0460",
    "centered_hexagonal_first_5",
    "Centered Hexagonal First 5",
    extra_helpers=[PRINT_SEP_DEC],
    value_data=[
        "limit: bit.vec 16, 5",
        "idx: bit.vec 16, 0",
        "term: bit.vec 16, 1",
        "delta: bit.vec 16, 0",
        "step: bit.vec 16, 6",
        "first: bit.bit",
    ],
    main_body="""
def main @ loop, body, end < limit, idx, term, delta, step, first {
    stl.startup
    bit.one first
  loop:
    bit.cmp 16, idx, limit, body, end, end
  body:
    print_sep_dec 16, term, first
    bit.add 16, delta, step
    bit.add 16, term, delta
    bit.inc 16, idx
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"",
    out_bytes=b"1 7 19 37 61\n",
)

# 0457 lazy_caterers_first_8 — L(k) = 1 + T(k); maintain triangular running sum
S(
    "0457",
    "lazy_caterers_first_8",
    "Lazy Caterers First 8",
    extra_helpers=[PRINT_SEP_DEC],
    value_data=[
        "limit: bit.vec 16, 8",
        "idx: bit.vec 16, 0",
        "tri: bit.vec 16, 0",
        "term: bit.vec 16, 0",
        "first: bit.bit",
    ],
    main_body="""
def main @ loop, body, end < limit, idx, tri, term, first {
    stl.startup
    bit.one first
  loop:
    bit.cmp 16, idx, limit, body, end, end
  body:
    bit.add 16, tri, idx
    bit.mov 16, term, tri
    bit.inc 16, term
    print_sep_dec 16, term, first
    bit.inc 16, idx
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"",
    out_bytes=b"1 2 4 7 11 16 22 29\n",
)

# ---------------------------------------------------------------------------
# Linear recurrences — rotate a fixed window of registers, print the front.
# ---------------------------------------------------------------------------

# 0440 lucas_first_n — L(0)=2, L(1)=1, L(k)=L(k-1)+L(k-2)
S(
    "0440",
    "lucas_first_n",
    "Lucas First N",
    unsigned=True,
    extra_helpers=[PRINT_SEP_DEC],
    value_data=[
        "limit: bit.vec 16, 0",
        "idx: bit.vec 16, 0",
        "a: bit.vec 16, 2",
        "b: bit.vec 16, 1",
        "tmp: bit.vec 16, 0",
        "first: bit.bit",
    ],
    main_body="""
def main @ loop, body, end < limit, idx, a, b, tmp, first {
    stl.startup
    read_decimal 16, limit
    bit.zero 16, idx
    bit.one first
  loop:
    bit.cmp 16, idx, limit, body, end, end
  body:
    print_sep_dec 16, a, first
    bit.mov 16, tmp, a
    bit.mov 16, a, b
    bit.add 16, b, tmp
    bit.inc 16, idx
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"7\n\0",
    out_bytes=b"2 1 3 4 7 11 18\n",
)

# 0441 perrin_first_10 — P(0)=3,P(1)=0,P(2)=2, P(k)=P(k-2)+P(k-3)
S(
    "0441",
    "perrin_first_10",
    "Perrin First 10",
    extra_helpers=[PRINT_SEP_DEC],
    value_data=[
        "limit: bit.vec 16, 10",
        "idx: bit.vec 16, 0",
        "a: bit.vec 16, 3",
        "b: bit.vec 16, 0",
        "c: bit.vec 16, 2",
        "nxt: bit.vec 16, 0",
        "first: bit.bit",
    ],
    main_body="""
def main @ loop, body, end < limit, idx, a, b, c, nxt, first {
    stl.startup
    bit.one first
  loop:
    bit.cmp 16, idx, limit, body, end, end
  body:
    print_sep_dec 16, a, first
    bit.mov 16, nxt, a
    bit.add 16, nxt, b
    bit.mov 16, a, b
    bit.mov 16, b, c
    bit.mov 16, c, nxt
    bit.inc 16, idx
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"",
    out_bytes=b"3 0 2 3 2 5 5 7 10 12\n",
)

# 0442 padovan_first_10 — P(0)=P(1)=P(2)=1, P(k)=P(k-2)+P(k-3)
S(
    "0442",
    "padovan_first_10",
    "Padovan First 10",
    extra_helpers=[PRINT_SEP_DEC],
    value_data=[
        "limit: bit.vec 16, 10",
        "idx: bit.vec 16, 0",
        "a: bit.vec 16, 1",
        "b: bit.vec 16, 1",
        "c: bit.vec 16, 1",
        "nxt: bit.vec 16, 0",
        "first: bit.bit",
    ],
    main_body="""
def main @ loop, body, end < limit, idx, a, b, c, nxt, first {
    stl.startup
    bit.one first
  loop:
    bit.cmp 16, idx, limit, body, end, end
  body:
    print_sep_dec 16, a, first
    bit.mov 16, nxt, a
    bit.add 16, nxt, b
    bit.mov 16, a, b
    bit.mov 16, b, c
    bit.mov 16, c, nxt
    bit.inc 16, idx
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"",
    out_bytes=b"1 1 1 2 2 3 4 5 7 9\n",
)

# 0443 jacobsthal_first_8 — J(0)=0,J(1)=1, J(k)=J(k-1)+2*J(k-2)
S(
    "0443",
    "jacobsthal_first_8",
    "Jacobsthal First 8",
    extra_helpers=[PRINT_SEP_DEC],
    value_data=[
        "limit: bit.vec 16, 8",
        "idx: bit.vec 16, 0",
        "a: bit.vec 16, 0",
        "b: bit.vec 16, 1",
        "nxt: bit.vec 16, 0",
        "first: bit.bit",
    ],
    main_body="""
def main @ loop, body, end < limit, idx, a, b, nxt, first {
    stl.startup
    bit.one first
  loop:
    bit.cmp 16, idx, limit, body, end, end
  body:
    print_sep_dec 16, a, first
    bit.mov 16, nxt, b
    bit.add 16, nxt, a
    bit.add 16, nxt, a
    bit.mov 16, a, b
    bit.mov 16, b, nxt
    bit.inc 16, idx
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"",
    out_bytes=b"0 1 1 3 5 11 21 43\n",
)

# 0444 pell_first_8 — P(0)=0,P(1)=1, P(k)=2*P(k-1)+P(k-2)
S(
    "0444",
    "pell_first_8",
    "Pell First 8",
    extra_helpers=[PRINT_SEP_DEC],
    value_data=[
        "limit: bit.vec 16, 8",
        "idx: bit.vec 16, 0",
        "a: bit.vec 16, 0",
        "b: bit.vec 16, 1",
        "nxt: bit.vec 16, 0",
        "first: bit.bit",
    ],
    main_body="""
def main @ loop, body, end < limit, idx, a, b, nxt, first {
    stl.startup
    bit.one first
  loop:
    bit.cmp 16, idx, limit, body, end, end
  body:
    print_sep_dec 16, a, first
    bit.mov 16, nxt, b
    bit.add 16, nxt, b
    bit.add 16, nxt, a
    bit.mov 16, a, b
    bit.mov 16, b, nxt
    bit.inc 16, idx
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"",
    out_bytes=b"0 1 2 5 12 29 70 169\n",
)

# 0445 tribonacci_first_10 — T(0)=T(1)=0,T(2)=1, T(k)=T(k-1)+T(k-2)+T(k-3)
S(
    "0445",
    "tribonacci_first_10",
    "Tribonacci First 10",
    extra_helpers=[PRINT_SEP_DEC],
    value_data=[
        "limit: bit.vec 16, 10",
        "idx: bit.vec 16, 0",
        "a: bit.vec 16, 0",
        "b: bit.vec 16, 0",
        "c: bit.vec 16, 1",
        "nxt: bit.vec 16, 0",
        "first: bit.bit",
    ],
    main_body="""
def main @ loop, body, end < limit, idx, a, b, c, nxt, first {
    stl.startup
    bit.one first
  loop:
    bit.cmp 16, idx, limit, body, end, end
  body:
    print_sep_dec 16, a, first
    bit.mov 16, nxt, a
    bit.add 16, nxt, b
    bit.add 16, nxt, c
    bit.mov 16, a, b
    bit.mov 16, b, c
    bit.mov 16, c, nxt
    bit.inc 16, idx
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"",
    out_bytes=b"0 0 1 1 2 4 7 13 24 44\n",
)

# 0446 tetranacci_first_8 — sum of the previous four; seeds 0,0,0,1
S(
    "0446",
    "tetranacci_first_8",
    "Tetranacci First 8",
    extra_helpers=[PRINT_SEP_DEC],
    value_data=[
        "limit: bit.vec 16, 8",
        "idx: bit.vec 16, 0",
        "a: bit.vec 16, 0",
        "b: bit.vec 16, 0",
        "c: bit.vec 16, 0",
        "d: bit.vec 16, 1",
        "nxt: bit.vec 16, 0",
        "first: bit.bit",
    ],
    main_body="""
def main @ loop, body, end < limit, idx, a, b, c, d, nxt, first {
    stl.startup
    bit.one first
  loop:
    bit.cmp 16, idx, limit, body, end, end
  body:
    print_sep_dec 16, a, first
    bit.mov 16, nxt, a
    bit.add 16, nxt, b
    bit.add 16, nxt, c
    bit.add 16, nxt, d
    bit.mov 16, a, b
    bit.mov 16, b, c
    bit.mov 16, c, d
    bit.mov 16, d, nxt
    bit.inc 16, idx
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"",
    out_bytes=b"0 0 0 1 1 2 4 8\n",
)

# ---------------------------------------------------------------------------
# Fibonacci-family — generate Fibonacci with a 2-register window, then
# filter / sum / square / reduce per spec.
# ---------------------------------------------------------------------------

# 0447 fibonacci_even_first_5 — keep terms with LSB clear
S(
    "0447",
    "fibonacci_even_first_5",
    "Fibonacci Even First 5",
    extra_helpers=[PRINT_SEP_DEC],
    value_data=[
        "limit: bit.vec 16, 5",
        "count: bit.vec 16, 0",
        "a: bit.vec 16, 0",
        "b: bit.vec 16, 1",
        "tmp: bit.vec 16, 0",
        "first: bit.bit",
    ],
    main_body="""
def main @ loop, advance, keep, next_fib, end < limit, count, a, b, tmp, first {
    stl.startup
    bit.one first
  loop:
    bit.cmp 16, count, limit, advance, end, end
  advance:
    bit.if0 a, keep
    ;next_fib
  keep:
    print_sep_dec 16, a, first
    bit.inc 16, count
  next_fib:
    bit.mov 16, tmp, a
    bit.mov 16, a, b
    bit.add 16, b, tmp
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"",
    out_bytes=b"0 2 8 34 144\n",
)

# 0448 fibonacci_odd_first_5 — keep terms with LSB set
S(
    "0448",
    "fibonacci_odd_first_5",
    "Fibonacci Odd First 5",
    extra_helpers=[PRINT_SEP_DEC],
    value_data=[
        "limit: bit.vec 16, 5",
        "count: bit.vec 16, 0",
        "a: bit.vec 16, 0",
        "b: bit.vec 16, 1",
        "tmp: bit.vec 16, 0",
        "first: bit.bit",
    ],
    main_body="""
def main @ loop, advance, keep, next_fib, end < limit, count, a, b, tmp, first {
    stl.startup
    bit.one first
  loop:
    bit.cmp 16, count, limit, advance, end, end
  advance:
    bit.if1 a, keep
    ;next_fib
  keep:
    print_sep_dec 16, a, first
    bit.inc 16, count
  next_fib:
    bit.mov 16, tmp, a
    bit.mov 16, a, b
    bit.add 16, b, tmp
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"",
    out_bytes=b"1 1 3 5 13\n",
)

# 0449 fibonacci_sum_first_n — accumulate F(1)+...+F(N), F(1)=F(2)=1
S(
    "0449",
    "fibonacci_sum_first_n",
    "Fibonacci Sum First N",
    unsigned=True,
    value_data=[
        "limit: bit.vec 16, 0",
        "idx: bit.vec 16, 0",
        "a: bit.vec 16, 1",
        "b: bit.vec 16, 1",
        "tmp: bit.vec 16, 0",
        "sum: bit.vec 16, 0",
    ],
    main_body="""
def main @ loop, body, end < limit, idx, a, b, tmp, sum {
    stl.startup
    read_decimal 16, limit
    bit.zero 16, idx
    bit.zero 16, sum
  loop:
    bit.cmp 16, idx, limit, body, end, end
  body:
    bit.add 16, sum, a
    bit.mov 16, tmp, a
    bit.mov 16, a, b
    bit.add 16, b, tmp
    bit.inc 16, idx
    ;loop
  end:
    bit.print_dec_uint 16, sum
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"12\n\0",
    out_bytes=b"376\n",
)

# 0450 fibonacci_squares_first_5 — F(k)^2 for k=1..5 (F(1)=F(2)=1)
S(
    "0450",
    "fibonacci_squares_first_5",
    "Fibonacci Squares First 5",
    mul=True,
    extra_helpers=[PRINT_SEP_DEC],
    value_data=[
        "limit: bit.vec 16, 5",
        "idx: bit.vec 16, 0",
        "a: bit.vec 16, 1",
        "b: bit.vec 16, 1",
        "tmp: bit.vec 16, 0",
        "sq: bit.vec 16, 0",
        "first: bit.bit",
    ],
    main_body="""
def main @ loop, body, end < limit, idx, a, b, tmp, sq, first {
    stl.startup
    bit.one first
  loop:
    bit.cmp 16, idx, limit, body, end, end
  body:
    mul_into 16, sq, a, a
    print_sep_dec 16, sq, first
    bit.mov 16, tmp, a
    bit.mov 16, a, b
    bit.add 16, b, tmp
    bit.inc 16, idx
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"",
    out_bytes=b"1 1 4 9 25\n",
)

# 0451 fibonacci_modulo_10 — compute F(N) (N<=20 fits 16 bits), print F(N) mod 10
S(
    "0451",
    "fibonacci_modulo_10",
    "Fibonacci Modulo 10",
    unsigned=True,
    value_data=[
        "limit: bit.vec 16, 0",
        "idx: bit.vec 16, 0",
        "a: bit.vec 16, 0",
        "b: bit.vec 16, 1",
        "tmp: bit.vec 16, 0",
        "ten: bit.vec 16, 10",
        "q: bit.vec 16, 0",
        "r: bit.vec 16, 0",
    ],
    main_body="""
def main @ loop, body, end < limit, idx, a, b, tmp, ten, q, r {
    stl.startup
    read_decimal 16, limit
    bit.zero 16, idx
  loop:
    bit.cmp 16, idx, limit, body, end, end
  body:
    bit.mov 16, tmp, a
    bit.mov 16, a, b
    bit.add 16, b, tmp
    bit.inc 16, idx
    ;loop
  end:
    bit.div 16, a, ten, q, r
    bit.print_dec_uint 16, r
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"20\n\0",
    out_bytes=b"5\n",
)

# 0921 fibonacci_pairs_first_n — print "F(i) F(i+1)\\n" for i = 0..N-1
S(
    "0921",
    "fibonacci_pairs_first_n",
    "Fibonacci Pairs First N",
    unsigned=True,
    value_data=[
        "limit: bit.vec 16, 0",
        "idx: bit.vec 16, 0",
        "a: bit.vec 16, 0",
        "b: bit.vec 16, 1",
        "tmp: bit.vec 16, 0",
    ],
    main_body="""
def main @ loop, body, end < limit, idx, a, b, tmp {
    stl.startup
    read_decimal 16, limit
    bit.zero 16, idx
  loop:
    bit.cmp 16, idx, limit, body, end, end
  body:
    bit.print_dec_uint 16, a
    stl.output ' '
    bit.print_dec_uint 16, b
    stl.output '\\n'
    bit.mov 16, tmp, a
    bit.mov 16, a, b
    bit.add 16, b, tmp
    bit.inc 16, idx
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"5\n\0",
    out_bytes=b"0 1\n1 1\n1 2\n2 3\n3 5\n",
)

# ---------------------------------------------------------------------------
# Powers and multiples — arithmetic / geometric progressions.
# ---------------------------------------------------------------------------

# 0917 evens_first_n — 2, 4, ..., 2N
S(
    "0917",
    "evens_first_n",
    "Evens First N",
    unsigned=True,
    extra_helpers=[PRINT_SEP_DEC],
    value_data=[
        "limit: bit.vec 16, 0",
        "idx: bit.vec 16, 0",
        "term: bit.vec 16, 0",
        "two: bit.vec 16, 2",
        "first: bit.bit",
    ],
    main_body="""
def main @ loop, body, end < limit, idx, term, two, first {
    stl.startup
    read_decimal 16, limit
    bit.zero 16, idx
    bit.zero 16, term
    bit.one first
  loop:
    bit.cmp 16, idx, limit, body, end, end
  body:
    bit.add 16, term, two
    print_sep_dec 16, term, first
    bit.inc 16, idx
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"5\n\0",
    out_bytes=b"2 4 6 8 10\n",
)

# 0918 odds_first_n — 1, 3, ..., 2N-1
S(
    "0918",
    "odds_first_n",
    "Odds First N",
    unsigned=True,
    extra_helpers=[PRINT_SEP_DEC],
    value_data=[
        "limit: bit.vec 16, 0",
        "idx: bit.vec 16, 0",
        "term: bit.vec 16, 1",
        "two: bit.vec 16, 2",
        "first: bit.bit",
    ],
    main_body="""
def main @ loop, body, end < limit, idx, term, two, first {
    stl.startup
    read_decimal 16, limit
    bit.zero 16, idx
    bit.zero 16, term
    bit.inc 16, term
    bit.one first
  loop:
    bit.cmp 16, idx, limit, body, end, end
  body:
    print_sep_dec 16, term, first
    bit.add 16, term, two
    bit.inc 16, idx
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"5\n\0",
    out_bytes=b"1 3 5 7 9\n",
)

# 0919 powers_of_2_first_n — 1, 2, 4, ..., 2^(N-1) by doubling
S(
    "0919",
    "powers_of_2_first_n",
    "Powers Of 2 First N",
    unsigned=True,
    extra_helpers=[PRINT_SEP_DEC],
    value_data=[
        "limit: bit.vec 16, 0",
        "idx: bit.vec 16, 0",
        "term: bit.vec 16, 1",
        "tmp: bit.vec 16, 0",
        "first: bit.bit",
    ],
    main_body="""
def main @ loop, body, end < limit, idx, term, tmp, first {
    stl.startup
    read_decimal 16, limit
    bit.zero 16, idx
    bit.zero 16, term
    bit.inc 16, term
    bit.one first
  loop:
    bit.cmp 16, idx, limit, body, end, end
  body:
    print_sep_dec 16, term, first
    bit.mov 16, tmp, term
    bit.add 16, term, tmp
    bit.inc 16, idx
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"7\n\0",
    out_bytes=b"1 2 4 8 16 32 64\n",
)

# 0920 powers_of_3_first_n — 1, 3, 9, ..., 3^(N-1) by *3 (repeated addition)
S(
    "0920",
    "powers_of_3_first_n",
    "Powers Of 3 First N",
    unsigned=True,
    mul=True,
    extra_helpers=[PRINT_SEP_DEC],
    value_data=[
        "limit: bit.vec 16, 0",
        "idx: bit.vec 16, 0",
        "term: bit.vec 16, 1",
        "tmp: bit.vec 16, 0",
        "three: bit.vec 16, 3",
        "first: bit.bit",
    ],
    main_body="""
def main @ loop, body, end < limit, idx, term, tmp, three, first {
    stl.startup
    read_decimal 16, limit
    bit.zero 16, idx
    bit.zero 16, term
    bit.inc 16, term
    bit.one first
  loop:
    bit.cmp 16, idx, limit, body, end, end
  body:
    print_sep_dec 16, term, first
    mul_into 16, tmp, term, three
    bit.mov 16, term, tmp
    bit.inc 16, idx
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"5\n\0",
    out_bytes=b"1 3 9 27 81\n",
)

# 0453 mersenne_first_5 — M(n) = 2^n - 1 for n = 1..5; pow doubles, term = pow-1
S(
    "0453",
    "mersenne_first_5",
    "Mersenne First 5",
    extra_helpers=[PRINT_SEP_DEC],
    value_data=[
        "limit: bit.vec 16, 5",
        "idx: bit.vec 16, 0",
        "powr: bit.vec 16, 2",
        "term: bit.vec 16, 0",
        "tmp: bit.vec 16, 0",
        "first: bit.bit",
    ],
    main_body="""
def main @ loop, body, end < limit, idx, powr, term, tmp, first {
    stl.startup
    bit.one first
  loop:
    bit.cmp 16, idx, limit, body, end, end
  body:
    bit.mov 16, term, powr
    bit.dec 16, term
    print_sep_dec 16, term, first
    bit.mov 16, tmp, powr
    bit.add 16, powr, tmp
    bit.inc 16, idx
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"",
    out_bytes=b"1 3 7 15 31\n",
)

# 0922 mersenne_first_n — M(k) = 2^k - 1 for k = 1..N
S(
    "0922",
    "mersenne_first_n",
    "Mersenne First N",
    unsigned=True,
    extra_helpers=[PRINT_SEP_DEC],
    value_data=[
        "limit: bit.vec 16, 0",
        "idx: bit.vec 16, 0",
        "powr: bit.vec 16, 2",
        "term: bit.vec 16, 0",
        "tmp: bit.vec 16, 0",
        "first: bit.bit",
    ],
    main_body="""
def main @ loop, body, end < limit, idx, powr, term, tmp, first {
    stl.startup
    read_decimal 16, limit
    bit.zero 16, idx
    bit.one first
  loop:
    bit.cmp 16, idx, limit, body, end, end
  body:
    bit.mov 16, term, powr
    bit.dec 16, term
    print_sep_dec 16, term, first
    bit.mov 16, tmp, powr
    bit.add 16, powr, tmp
    bit.inc 16, idx
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"7\n\0",
    out_bytes=b"1 3 7 15 31 63 127\n",
)

# 0455 fermat_first_4 — F(n) = 2^(2^n) + 1; square the base each step
S(
    "0455",
    "fermat_first_4",
    "Fermat First 4",
    mul=True,
    extra_helpers=[PRINT_SEP_DEC],
    value_data=[
        "limit: bit.vec 16, 4",
        "idx: bit.vec 16, 0",
        "base: bit.vec 16, 2",
        "term: bit.vec 16, 0",
        "tmp: bit.vec 16, 0",
        "first: bit.bit",
    ],
    main_body="""
def main @ loop, body, end < limit, idx, base, term, tmp, first {
    stl.startup
    bit.one first
  loop:
    bit.cmp 16, idx, limit, body, end, end
  body:
    bit.mov 16, term, base
    bit.inc 16, term
    print_sep_dec 16, term, first
    mul_into 16, tmp, base, base
    bit.mov 16, base, tmp
    bit.inc 16, idx
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"",
    out_bytes=b"3 5 17 257\n",
)

# ---------------------------------------------------------------------------
# Two-term recurrences with a multiply/divide step.
# ---------------------------------------------------------------------------

# 0439 derangement_first_5 — D(n) = (n-1)(D(n-1)+D(n-2)), D(0)=1, D(1)=0
S(
    "0439",
    "derangement_first_5",
    "Derangement First 5",
    mul=True,
    extra_helpers=[PRINT_SEP_DEC],
    value_data=[
        "limit: bit.vec 16, 5",
        "idx: bit.vec 16, 1",
        "a: bit.vec 16, 1",
        "b: bit.vec 16, 0",
        "sum: bit.vec 16, 0",
        "nxt: bit.vec 16, 0",
        "first: bit.bit",
    ],
    main_body="""
def main @ loop, body, end < limit, idx, a, b, sum, nxt, first {
    stl.startup
    bit.one first
  loop:
    bit.cmp 16, idx, limit, body, body, end
  body:
    print_sep_dec 16, b, first
    bit.mov 16, sum, a
    bit.add 16, sum, b
    mul_into 16, nxt, sum, idx
    bit.mov 16, a, b
    bit.mov 16, b, nxt
    bit.inc 16, idx
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"",
    out_bytes=b"0 1 2 9 44\n",
)

# 0437 catalan_first_5 — C(0)=1, C(n+1) = C(n)*(4n+2)/(n+2)
S(
    "0437",
    "catalan_first_5",
    "Catalan First 5",
    mul=True,
    extra_helpers=[PRINT_SEP_DEC],
    value_data=[
        "limit: bit.vec 16, 5",
        "idx: bit.vec 16, 0",
        "c: bit.vec 16, 1",
        "factor: bit.vec 16, 0",
        "den: bit.vec 16, 0",
        "num: bit.vec 16, 0",
        "rem: bit.vec 16, 0",
        "two: bit.vec 16, 2",
        "first: bit.bit",
    ],
    main_body="""
def main @ loop, body, end < limit, idx, c, factor, den, num, rem, two, first {
    stl.startup
    bit.one first
  loop:
    bit.cmp 16, idx, limit, body, end, end
  body:
    print_sep_dec 16, c, first
    bit.mov 16, factor, idx
    bit.shl 16, 2, factor
    bit.add 16, factor, two
    mul_into 16, num, c, factor
    bit.mov 16, den, idx
    bit.add 16, den, two
    bit.div 16, num, den, c, rem
    bit.inc 16, idx
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"",
    out_bytes=b"1 1 2 5 14\n",
)

# 0923 triangular_inverse_n — find k with T(k)==input, else -1
S(
    "0923",
    "triangular_inverse_n",
    "Triangular Inverse N",
    unsigned=True,
    value_data=[
        "target: bit.vec 16, 0",
        "idx: bit.vec 16, 0",
        "tri: bit.vec 16, 0",
    ],
    main_body="""
def main @ loop, grow, found, none, done_print < target, idx, tri {
    stl.startup
    read_decimal 16, target
    bit.zero 16, idx
    bit.zero 16, tri
  loop:
    bit.inc 16, idx
    bit.add 16, tri, idx
    bit.cmp 16, tri, target, grow, found, none
  grow:
    ;loop
  found:
    bit.print_dec_uint 16, idx
    stl.output '\\n'
    ;done_print
  none:
    stl.output "-1\\n"
  done_print:
    stl.loop
}
""",
    in_bytes=b"10\n\0",
    out_bytes=b"4\n",
)

# ---------------------------------------------------------------------------
# Mersenne primes — generate M(k) = 2^k - 1 and keep the prime ones, using
# sqrt-bounded trial division. 24-bit registers (room well beyond M(5) = 31).
# ---------------------------------------------------------------------------

# 0454 mersenne_prime_first_3 — first 3 primes among 2^k - 1 (k = 2, 3, 5)
S(
    "0454",
    "mersenne_prime_first_3",
    "Mersenne Prime First 3",
    extra_helpers=[IS_PRIME_SQRT, PRINT_SEP_DEC],
    extra_data=D_IS_PRIME,
    value_data=[
        "limit: bit.vec 24, 3",
        "count: bit.vec 24, 0",
        "powr: bit.vec 24, 4",
        "tmp: bit.vec 24, 0",
        "mers: bit.vec 24, 0",
        "prime: bit.bit",
        "first: bit.bit",
    ],
    main_body="""
def main @ loop, advance, keep, double, end < limit, count, powr, tmp, mers, prime, first {
    stl.startup
    bit.one first
  loop:
    bit.cmp 24, count, limit, advance, end, end
  advance:
    bit.mov 24, mers, powr
    bit.dec 24, mers
    is_prime_sqrt_into 24, prime, mers
    bit.if0 prime, double
  keep:
    print_sep_dec 24, mers, first
    bit.inc 24, count
  double:
    bit.mov 24, tmp, powr
    bit.add 24, powr, tmp
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"",
    out_bytes=b"3 7 31\n",
)

print("---")
print("CHUNK 7 OK")

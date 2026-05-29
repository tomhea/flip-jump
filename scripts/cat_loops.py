"""Phase 3: loops — counter / nested-loop demonstration programs.

The read-N-then-loop-and-print slice of the APPROVED `loops` category
(#0230-0280): repeat-a-byte loops, ASCII-art triangles/grids built from
nested counters, fixed-output sequence generators (alphabets, evens/odds,
Fibonacci, primes, squares, powers, factorials), running sums, ranges with a
step, FizzBuzz, and a couple of read-N-bytes loops.

Programs whose body must buffer an arbitrary input line and replay it N times
(repeat_line_n, line_then_n_blanks, print_box_with_label, numbered_lines) need
an array/pointer and are deferred to a later batch.

Counter loops live in `main` (allowed — only stl.startup/stl.loop are
main-only). Nested-loop bodies are pulled into helpers per CONVENTIONS.md.
Programs reuse the shared read_decimal helper via `unsigned=True`.

Run from the repo root:  python scripts/cat_loops.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog_arith import emit  # noqa: E402


def L(nnnn, slug, name, **kw):
    emit("loops", nnnn, slug, name, **kw)


# --- shared helpers -------------------------------------------------------

# Print the byte glyph `count` times (count[:16] is preserved via a scratch).
PRINT_GLYPH_TIMES = """
// Print the byte at glyph exactly count[:16] times.
def print_glyph_times count, glyph @ loop, end < rep_ctr {
    bit.mov 16, rep_ctr, count
  loop:
    bit.if0 16, rep_ctr, end
    bit.print glyph
    bit.dec 16, rep_ctr
    ;loop
  end:
}
""".strip()

D_REP_CTR = ["rep_ctr: bit.vec 16, 0"]

# Print val[:n] in decimal, preceded by a space on every call after the first.
# `first` starts at 1; the macro clears it once the first value is emitted.
PRINT_SPACED = """
// Print val[:n] in decimal; emit a leading space on all but the first call.
def print_spaced n, val, first @ subsequent, emit < sp {
    bit.if0 first, subsequent
    bit.zero first
    ;emit
  subsequent:
    bit.print sp
  emit:
    bit.print_dec_uint n, val
}
""".strip()

D_SPACED = ["sp: bit.vec 8, ' '", "first: bit.bit"]

# flag = 1 if x[:n] is prime (x >= 2), else 0. Trial division by 2..x-1.
IS_PRIME_INTO = """
// flag = 1 if x[:n] is prime (x >= 2), else 0. Trial division by 2..x-1.
def is_prime_into n, flag, x @ check, loop, test, composite, prime, end < d, q, r, two {
    bit.cmp n, x, two, composite, check, check
  check:
    bit.mov n, d, two
  loop:
    bit.cmp n, d, x, test, prime, prime
  test:
    bit.div n, x, d, q, r
    bit.if0 n, r, composite
    bit.inc n, d
    ;loop
  composite:
    bit.zero flag
    ;end
  prime:
    bit.one flag
  end:
}
""".strip()

D_PRIME = ["d: bit.vec 16, 0", "q: bit.vec 16, 0", "r: bit.vec 16, 0", "two: bit.vec 16, 2"]

# Print the FizzBuzz word(s) for idx[:16], or idx itself, then a newline.
PRINT_FIZZBUZZ = """
// Print FizzBuzz/Fizz/Buzz/idx for idx[:16] + \\n (idx % 3 and % 5 tests).
def print_fizzbuzz idx @ not3, fizz, buzz, num, done < q, r3, r5, three, five {
    bit.div 16, idx, three, q, r3
    bit.div 16, idx, five, q, r5
    bit.if1 16, r3, not3
    bit.if1 16, r5, fizz
    stl.output "FizzBuzz\\n"
    ;done
  not3:
    bit.if1 16, r5, num
  buzz:
    stl.output "Buzz\\n"
    ;done
  fizz:
    stl.output "Fizz\\n"
    ;done
  num:
    bit.print_dec_uint 16, idx
    stl.output '\\n'
  done:
}
""".strip()

D_FIZZBUZZ = [
    "q: bit.vec 16, 0",
    "r3: bit.vec 16, 0",
    "r5: bit.vec 16, 0",
    "three: bit.vec 16, 3",
    "five: bit.vec 16, 5",
]


print("--- writing loops programs ---")


# 0230 print_byte_n_times — read byte, skip its \n, read N, print byte N times.
L(
    "0230",
    "print_byte_n_times",
    "Print Byte N Times",
    unsigned=True,
    extra_helpers=[PRINT_GLYPH_TIMES],
    value_data=["glyph: bit.vec 8, 0", "sep: bit.vec 8, 0", "count: bit.vec 16, 0"],
    extra_data=D_REP_CTR,
    main_body="""
def main < glyph, sep, count {
    stl.startup
    bit.input glyph
    bit.input sep
    read_decimal 16, count
    print_glyph_times count, glyph
    stl.loop
}
""",
    in_bytes=b"A\n3\n\0",
    out_bytes=b"AAA",
)

# 0231 print_n_byte_lines — N lines, each "<byte>\n".
L(
    "0231",
    "print_n_byte_lines",
    "Print N Byte Lines",
    unsigned=True,
    value_data=["glyph: bit.vec 8, 0", "sep: bit.vec 8, 0", "count: bit.vec 16, 0"],
    main_body="""
def main @ loop, end < glyph, sep, count {
    stl.startup
    bit.input glyph
    bit.input sep
    read_decimal 16, count
  loop:
    bit.if0 16, count, end
    bit.print glyph
    stl.output '\\n'
    bit.dec 16, count
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"Q\n3\n\0",
    out_bytes=b"Q\nQ\nQ\n",
)

# 0237 solid_square — N rows of N glyphs (here '*').
L(
    "0237",
    "solid_square",
    "Solid Square",
    unsigned=True,
    extra_helpers=[PRINT_GLYPH_TIMES],
    value_data=["count: bit.vec 16, 0", "row: bit.vec 16, 0", "star: bit.vec 8, '*'"],
    extra_data=D_REP_CTR,
    main_body="""
def main @ loop, body, end < count, row, star {
    stl.startup
    read_decimal 16, count
    bit.zero 16, row
  loop:
    bit.cmp 16, row, count, body, end, end
  body:
    print_glyph_times count, star
    stl.output '\\n'
    bit.inc 16, row
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"3\n\0",
    out_bytes=b"***\n***\n***\n",
)

# 0270 print_vertical_bar — N lines each "*\n".
L(
    "0270",
    "print_vertical_bar",
    "Print Vertical Bar",
    unsigned=True,
    value_data=["count: bit.vec 16, 0"],
    main_body="""
def main @ loop, end < count {
    stl.startup
    read_decimal 16, count
  loop:
    bit.if0 16, count, end
    stl.output "*\\n"
    bit.dec 16, count
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"4\n\0",
    out_bytes=b"*\n*\n*\n*\n",
)

# 0271 print_horizontal_bar — one line of N '*' then \n.
L(
    "0271",
    "print_horizontal_bar",
    "Print Horizontal Bar",
    unsigned=True,
    extra_helpers=[PRINT_GLYPH_TIMES],
    value_data=["count: bit.vec 16, 0", "star: bit.vec 8, '*'"],
    extra_data=D_REP_CTR,
    main_body="""
def main < count, star {
    stl.startup
    read_decimal 16, count
    print_glyph_times count, star
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"5\n\0",
    out_bytes=b"*****\n",
)

# 0233 right_triangle_stars — row i (1..N) has i '*' then \n.
L(
    "0233",
    "right_triangle_stars",
    "Right Triangle Stars",
    unsigned=True,
    extra_helpers=[PRINT_GLYPH_TIMES],
    value_data=["count: bit.vec 16, 0", "row: bit.vec 16, 0", "star: bit.vec 8, '*'"],
    extra_data=D_REP_CTR,
    main_body="""
def main @ loop, body, end < count, row, star {
    stl.startup
    read_decimal 16, count
    bit.zero 16, row
    bit.inc 16, row
  loop:
    bit.cmp 16, row, count, body, body, end
  body:
    print_glyph_times row, star
    stl.output '\\n'
    bit.inc 16, row
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"4\n\0",
    out_bytes=b"*\n**\n***\n****\n",
)

# 0234 inverted_right_triangle — row i has (N+1-i) '*'; count runs N..1.
L(
    "0234",
    "inverted_right_triangle",
    "Inverted Right Triangle",
    unsigned=True,
    extra_helpers=[PRINT_GLYPH_TIMES],
    value_data=["count: bit.vec 16, 0", "stars: bit.vec 16, 0", "star: bit.vec 8, '*'"],
    extra_data=D_REP_CTR,
    main_body="""
def main @ loop, end < count, stars, star {
    stl.startup
    read_decimal 16, count
    bit.mov 16, stars, count
  loop:
    bit.if0 16, stars, end
    print_glyph_times stars, star
    stl.output '\\n'
    bit.dec 16, stars
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"4\n\0",
    out_bytes=b"****\n***\n**\n*\n",
)

# 0276 spaces_then_stars — row i: (N-i) spaces, then i '*', then \n.
L(
    "0276",
    "spaces_then_stars",
    "Spaces Then Stars",
    unsigned=True,
    extra_helpers=[PRINT_GLYPH_TIMES],
    value_data=[
        "count: bit.vec 16, 0",
        "row: bit.vec 16, 0",
        "gap: bit.vec 16, 0",
        "star: bit.vec 8, '*'",
        "space: bit.vec 8, ' '",
    ],
    extra_data=D_REP_CTR,
    main_body="""
def main @ loop, body, end < count, row, gap, star, space {
    stl.startup
    read_decimal 16, count
    bit.zero 16, row
    bit.inc 16, row
  loop:
    bit.cmp 16, row, count, body, body, end
  body:
    bit.mov 16, gap, count
    bit.sub 16, gap, row
    print_glyph_times gap, space
    print_glyph_times row, star
    stl.output '\\n'
    bit.inc 16, row
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"4\n\0",
    out_bytes=b"   *\n  **\n ***\n****\n",
)

# 0235 centered_pyramid — row i: (N-i) spaces, then (2i-1) '*', then \n.
L(
    "0235",
    "centered_pyramid",
    "Centered Pyramid",
    unsigned=True,
    extra_helpers=[PRINT_GLYPH_TIMES],
    value_data=[
        "count: bit.vec 16, 0",
        "row: bit.vec 16, 0",
        "gap: bit.vec 16, 0",
        "stars: bit.vec 16, 0",
        "star: bit.vec 8, '*'",
        "space: bit.vec 8, ' '",
    ],
    extra_data=D_REP_CTR,
    main_body="""
def main @ loop, body, end < count, row, gap, stars, star, space {
    stl.startup
    read_decimal 16, count
    bit.zero 16, row
    bit.inc 16, row
  loop:
    bit.cmp 16, row, count, body, body, end
  body:
    bit.mov 16, gap, count
    bit.sub 16, gap, row
    print_glyph_times gap, space
    bit.mov 16, stars, row
    bit.add 16, stars, row
    bit.dec 16, stars
    print_glyph_times stars, star
    stl.output '\\n'
    bit.inc 16, row
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"3\n\0",
    out_bytes=b"  *\n ***\n*****\n",
)

# 0268 print_l_shape — N-1 rows "*\n", then one row of N '*' + \n.
L(
    "0268",
    "print_l_shape",
    "Print L Shape",
    unsigned=True,
    extra_helpers=[PRINT_GLYPH_TIMES],
    value_data=["count: bit.vec 16, 0", "stem: bit.vec 16, 0", "star: bit.vec 8, '*'"],
    extra_data=D_REP_CTR,
    main_body="""
def main @ loop, end < count, stem, star {
    stl.startup
    read_decimal 16, count
    bit.mov 16, stem, count
    bit.dec 16, stem
  loop:
    bit.if0 16, stem, end
    stl.output "*\\n"
    bit.dec 16, stem
    ;loop
  end:
    print_glyph_times count, star
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"3\n\0",
    out_bytes=b"*\n*\n***\n",
)

# 0269 print_t_shape — row 0: N '*'; rows 1..N-1: (N-1)/2 spaces then '*'.
L(
    "0269",
    "print_t_shape",
    "Print T Shape",
    unsigned=True,
    extra_helpers=[PRINT_GLYPH_TIMES],
    value_data=[
        "count: bit.vec 16, 0",
        "row: bit.vec 16, 0",
        "gap: bit.vec 16, 0",
        "two: bit.vec 16, 2",
        "qtmp: bit.vec 16, 0",
        "rtmp: bit.vec 16, 0",
        "star: bit.vec 8, '*'",
        "space: bit.vec 8, ' '",
    ],
    extra_data=D_REP_CTR,
    main_body="""
def main @ loop, end < count, row, gap, two, qtmp, rtmp, star, space {
    stl.startup
    read_decimal 16, count
    print_glyph_times count, star
    stl.output '\\n'
    bit.mov 16, gap, count
    bit.dec 16, gap
    bit.div 16, gap, two, qtmp, rtmp
    bit.mov 16, gap, qtmp
    bit.mov 16, row, count
    bit.dec 16, row
  loop:
    bit.if0 16, row, end
    print_glyph_times gap, space
    stl.output "*\\n"
    bit.dec 16, row
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"5\n\0",
    out_bytes=b"*****\n  *\n  *\n  *\n  *\n",
)

# 0243 print_alphabet_lower — print 'a'..'z' then \n.
L(
    "0243",
    "print_alphabet_lower",
    "Print Alphabet Lower",
    value_data=["ch: bit.vec 8, 'a'", "past: bit.vec 8, '{'"],
    main_body="""
def main @ loop, body, end < ch, past {
    stl.startup
  loop:
    bit.cmp 8, ch, past, body, end, end
  body:
    bit.print ch
    bit.inc 8, ch
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"\0",
    out_bytes=b"abcdefghijklmnopqrstuvwxyz\n",
)

# 0244 print_alphabet_upper — print 'A'..'Z' then \n.
L(
    "0244",
    "print_alphabet_upper",
    "Print Alphabet Upper",
    value_data=["ch: bit.vec 8, 'A'", "past: bit.vec 8, '['"],
    main_body="""
def main @ loop, body, end < ch, past {
    stl.startup
  loop:
    bit.cmp 8, ch, past, body, end, end
  body:
    bit.print ch
    bit.inc 8, ch
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"\0",
    out_bytes=b"ABCDEFGHIJKLMNOPQRSTUVWXYZ\n",
)

# 0245 print_alphabet_reversed — print 'z'..'a' then \n.
L(
    "0245",
    "print_alphabet_reversed",
    "Print Alphabet Reversed",
    value_data=["ch: bit.vec 8, 'z'", "before: bit.vec 8, '`'"],
    main_body="""
def main @ loop, body, end < ch, before {
    stl.startup
  loop:
    bit.cmp 8, ch, before, end, end, body
  body:
    bit.print ch
    bit.dec 8, ch
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"\0",
    out_bytes=b"zyxwvutsrqponmlkjihgfedcba\n",
)

# 0246 print_digits_0_9 — print '0'..'9' then \n.
L(
    "0246",
    "print_digits_0_9",
    "Print Digits 0 9",
    value_data=["ch: bit.vec 8, '0'", "past: bit.vec 8, ':'"],
    main_body="""
def main @ loop, body, end < ch, past {
    stl.startup
  loop:
    bit.cmp 8, ch, past, body, end, end
  body:
    bit.print ch
    bit.inc 8, ch
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"\0",
    out_bytes=b"0123456789\n",
)

# 0253 count_to_10 — 1..10 each on its own line.
L(
    "0253",
    "count_to_10",
    "Count To 10",
    value_data=["idx: bit.vec 16, 1", "limit: bit.vec 16, 10"],
    main_body="""
def main @ loop, body, end < idx, limit {
    stl.startup
  loop:
    bit.cmp 16, idx, limit, body, body, end
  body:
    bit.print_dec_uint 16, idx
    stl.output '\\n'
    bit.inc 16, idx
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"\0",
    out_bytes=b"1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n",
)

# 0254 count_down_from_10 — 10..1 each on its own line.
L(
    "0254",
    "count_down_from_10",
    "Count Down From 10",
    value_data=["idx: bit.vec 16, 10"],
    main_body="""
def main @ loop, end < idx {
    stl.startup
  loop:
    bit.if0 16, idx, end
    bit.print_dec_uint 16, idx
    stl.output '\\n'
    bit.dec 16, idx
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"\0",
    out_bytes=b"10\n9\n8\n7\n6\n5\n4\n3\n2\n1\n",
)

# 0266 countdown_blastoff — 5..1 then "Blastoff!".
L(
    "0266",
    "countdown_blastoff",
    "Countdown Blastoff",
    value_data=["idx: bit.vec 16, 5"],
    main_body="""
def main @ loop, end < idx {
    stl.startup
  loop:
    bit.if0 16, idx, end
    bit.print_dec_uint 16, idx
    stl.output '\\n'
    bit.dec 16, idx
    ;loop
  end:
    stl.output "Blastoff!\\n"
    stl.loop
}
""",
    in_bytes=b"\0",
    out_bytes=b"5\n4\n3\n2\n1\nBlastoff!\n",
)

# 0247 print_evens_2_to_20 — 2,4,...,20 space-separated.
L(
    "0247",
    "print_evens_2_to_20",
    "Print Evens 2 To 20",
    extra_helpers=[PRINT_SPACED],
    value_data=["val: bit.vec 16, 2", "limit: bit.vec 16, 20", "step: bit.vec 16, 2"],
    extra_data=D_SPACED,
    main_body="""
def main @ loop, body, end < val, limit, step, first {
    stl.startup
    bit.one first
  loop:
    bit.cmp 16, val, limit, body, body, end
  body:
    print_spaced 16, val, first
    bit.add 16, val, step
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"\0",
    out_bytes=b"2 4 6 8 10 12 14 16 18 20\n",
)

# 0248 print_odds_1_to_19 — 1,3,...,19 space-separated.
L(
    "0248",
    "print_odds_1_to_19",
    "Print Odds 1 To 19",
    extra_helpers=[PRINT_SPACED],
    value_data=["val: bit.vec 16, 1", "limit: bit.vec 16, 19", "step: bit.vec 16, 2"],
    extra_data=D_SPACED,
    main_body="""
def main @ loop, body, end < val, limit, step, first {
    stl.startup
    bit.one first
  loop:
    bit.cmp 16, val, limit, body, body, end
  body:
    print_spaced 16, val, first
    bit.add 16, val, step
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"\0",
    out_bytes=b"1 3 5 7 9 11 13 15 17 19\n",
)

# 0249 print_multiples_5_to_50 — 5,10,...,50 space-separated.
L(
    "0249",
    "print_multiples_5_to_50",
    "Print Multiples 5 To 50",
    extra_helpers=[PRINT_SPACED],
    value_data=["val: bit.vec 16, 5", "limit: bit.vec 16, 50", "step: bit.vec 16, 5"],
    extra_data=D_SPACED,
    main_body="""
def main @ loop, body, end < val, limit, step, first {
    stl.startup
    bit.one first
  loop:
    bit.cmp 16, val, limit, body, body, end
  body:
    print_spaced 16, val, first
    bit.add 16, val, step
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"\0",
    out_bytes=b"5 10 15 20 25 30 35 40 45 50\n",
)

# 0255 print_ascii_a_to_k — ASCII codes 65..75 space-separated.
L(
    "0255",
    "print_ascii_a_to_k",
    "Print Ascii A To K",
    extra_helpers=[PRINT_SPACED],
    value_data=["val: bit.vec 16, 65", "limit: bit.vec 16, 75", "step: bit.vec 16, 1"],
    extra_data=D_SPACED,
    main_body="""
def main @ loop, body, end < val, limit, step, first {
    stl.startup
    bit.one first
  loop:
    bit.cmp 16, val, limit, body, body, end
  body:
    print_spaced 16, val, first
    bit.add 16, val, step
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"\0",
    out_bytes=b"65 66 67 68 69 70 71 72 73 74 75\n",
)

# 0256 print_powers_of_2_first_8 — 1 2 4 8 16 32 64 128 (double each term).
L(
    "0256",
    "print_powers_of_2_first_8",
    "Print Powers Of 2 First 8",
    extra_helpers=[PRINT_SPACED],
    value_data=["val: bit.vec 16, 1", "ctr: bit.vec 16, 8", "dbl: bit.vec 16, 0"],
    extra_data=D_SPACED,
    main_body="""
def main @ loop, end < val, ctr, dbl, first {
    stl.startup
    bit.one first
  loop:
    bit.if0 16, ctr, end
    print_spaced 16, val, first
    bit.mov 16, dbl, val
    bit.add 16, val, dbl
    bit.dec 16, ctr
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"\0",
    out_bytes=b"1 2 4 8 16 32 64 128\n",
)

# 0257 print_powers_of_3_first_5 — 1 3 9 27 81 (triple each term).
L(
    "0257",
    "print_powers_of_3_first_5",
    "Print Powers Of 3 First 5",
    mul=True,
    extra_helpers=[PRINT_SPACED],
    value_data=["val: bit.vec 16, 1", "ctr: bit.vec 16, 5", "prod: bit.vec 16, 0", "three: bit.vec 16, 3"],
    extra_data=D_SPACED,
    main_body="""
def main @ loop, end < val, ctr, prod, three, first {
    stl.startup
    bit.one first
  loop:
    bit.if0 16, ctr, end
    print_spaced 16, val, first
    mul_into 16, prod, val, three
    bit.mov 16, val, prod
    bit.dec 16, ctr
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"\0",
    out_bytes=b"1 3 9 27 81\n",
)

# 0258 print_factorial_first_6 — 1 2 6 24 120 720 (running product f*=i).
L(
    "0258",
    "print_factorial_first_6",
    "Print Factorial First 6",
    mul=True,
    extra_helpers=[PRINT_SPACED],
    value_data=[
        "fact: bit.vec 16, 1",
        "idx: bit.vec 16, 1",
        "limit: bit.vec 16, 6",
        "prod: bit.vec 16, 0",
    ],
    extra_data=D_SPACED,
    main_body="""
def main @ loop, body, end < fact, idx, limit, prod, first {
    stl.startup
    bit.one first
  loop:
    bit.cmp 16, idx, limit, body, body, end
  body:
    mul_into 16, prod, fact, idx
    bit.mov 16, fact, prod
    print_spaced 16, fact, first
    bit.inc 16, idx
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"\0",
    out_bytes=b"1 2 6 24 120 720\n",
)

# 0250 print_fibs_first_10 — 0 1 1 2 3 5 8 13 21 34 (rolling a,b).
L(
    "0250",
    "print_fibs_first_10",
    "Print Fibs First 10",
    extra_helpers=[PRINT_SPACED],
    value_data=[
        "a: bit.vec 16, 0",
        "b: bit.vec 16, 1",
        "nxt: bit.vec 16, 0",
        "ctr: bit.vec 16, 10",
    ],
    extra_data=D_SPACED,
    main_body="""
def main @ loop, end < a, b, nxt, ctr, first {
    stl.startup
    bit.one first
  loop:
    bit.if0 16, ctr, end
    print_spaced 16, a, first
    bit.mov 16, nxt, a
    bit.add 16, nxt, b
    bit.mov 16, a, b
    bit.mov 16, b, nxt
    bit.dec 16, ctr
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"\0",
    out_bytes=b"0 1 1 2 3 5 8 13 21 34\n",
)

# 0252 print_first_10_squares — 1 4 9 ... 100 (sq += next odd).
L(
    "0252",
    "print_first_10_squares",
    "Print First 10 Squares",
    extra_helpers=[PRINT_SPACED],
    value_data=[
        "sq: bit.vec 16, 0",
        "odd: bit.vec 16, 1",
        "two: bit.vec 16, 2",
        "ctr: bit.vec 16, 10",
    ],
    extra_data=D_SPACED,
    main_body="""
def main @ loop, end < sq, odd, two, ctr, first {
    stl.startup
    bit.one first
  loop:
    bit.if0 16, ctr, end
    bit.add 16, sq, odd
    print_spaced 16, sq, first
    bit.add 16, odd, two
    bit.dec 16, ctr
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"\0",
    out_bytes=b"1 4 9 16 25 36 49 64 81 100\n",
)

# 0251 print_first_10_primes — 2 3 5 7 11 13 17 19 23 29 (trial division).
L(
    "0251",
    "print_first_10_primes",
    "Print First 10 Primes",
    extra_helpers=[PRINT_SPACED, IS_PRIME_INTO],
    value_data=["cand: bit.vec 16, 2", "found: bit.vec 16, 0", "ten: bit.vec 16, 10", "flag: bit.bit"],
    extra_data=D_SPACED + D_PRIME,
    main_body="""
def main @ loop, body, next, end < cand, found, ten, flag, first {
    stl.startup
    bit.one first
  loop:
    bit.cmp 16, found, ten, body, end, end
  body:
    is_prime_into 16, flag, cand
    bit.if0 flag, next
    print_spaced 16, cand, first
    bit.inc 16, found
  next:
    bit.inc 16, cand
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"\0",
    out_bytes=b"2 3 5 7 11 13 17 19 23 29\n",
)

# 0272 sum_running_first_n — running sums 1,3,6,... for first N of 1+2+3+...
L(
    "0272",
    "sum_running_first_n",
    "Sum Running First N",
    unsigned=True,
    value_data=["count: bit.vec 16, 0", "idx: bit.vec 16, 0", "sum: bit.vec 16, 0"],
    main_body="""
def main @ loop, body, end < count, idx, sum {
    stl.startup
    read_decimal 16, count
    bit.zero 16, sum
    bit.zero 16, idx
    bit.inc 16, idx
  loop:
    bit.cmp 16, idx, count, body, body, end
  body:
    bit.add 16, sum, idx
    bit.print_dec_uint 16, sum
    stl.output '\\n'
    bit.inc 16, idx
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"4\n\0",
    out_bytes=b"1\n3\n6\n10\n",
)

# 0273 range_step_two — read lo, hi; print lo, lo+2, ... <= hi.
L(
    "0273",
    "range_step_two",
    "Range Step Two",
    unsigned=True,
    value_data=["lo: bit.vec 16, 0", "hi: bit.vec 16, 0", "val: bit.vec 16, 0", "step: bit.vec 16, 2"],
    main_body="""
def main @ loop, body, end < lo, hi, val, step {
    stl.startup
    read_decimal 16, lo
    read_decimal 16, hi
    bit.mov 16, val, lo
  loop:
    bit.cmp 16, val, hi, body, body, end
  body:
    bit.print_dec_uint 16, val
    stl.output '\\n'
    bit.add 16, val, step
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"4\n12\n\0",
    out_bytes=b"4\n6\n8\n10\n12\n",
)

# 0274 range_step_three — read lo, hi; print lo, lo+3, ... <= hi.
L(
    "0274",
    "range_step_three",
    "Range Step Three",
    unsigned=True,
    value_data=["lo: bit.vec 16, 0", "hi: bit.vec 16, 0", "val: bit.vec 16, 0", "step: bit.vec 16, 3"],
    main_body="""
def main @ loop, body, end < lo, hi, val, step {
    stl.startup
    read_decimal 16, lo
    read_decimal 16, hi
    bit.mov 16, val, lo
  loop:
    bit.cmp 16, val, hi, body, body, end
  body:
    bit.print_dec_uint 16, val
    stl.output '\\n'
    bit.add 16, val, step
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"2\n14\n\0",
    out_bytes=b"2\n5\n8\n11\n14\n",
)

# 0265 count_input_bytes_running — print 1-based position after each byte, stop at \n.
L(
    "0265",
    "count_input_bytes_running",
    "Count Input Bytes Running",
    value_data=["ch: bit.vec 8, 0", "nl: bit.vec 8, '\\n'", "pos: bit.vec 16, 0"],
    main_body="""
def main @ loop, count_it, end < ch, nl, pos {
    stl.startup
    bit.zero 16, pos
  loop:
    bit.input ch
    bit.cmp 8, ch, nl, count_it, end, count_it
  count_it:
    bit.inc 16, pos
    bit.print_dec_uint 16, pos
    stl.output '\\n'
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"abcd\n\0",
    out_bytes=b"1\n2\n3\n4\n",
)

# 0277 echo_first_n_bytes — read N + \n, then echo exactly N more bytes.
L(
    "0277",
    "echo_first_n_bytes",
    "Echo First N Bytes",
    unsigned=True,
    value_data=["count: bit.vec 16, 0"],
    main_body="""
def main @ loop, end < count, ch {
    stl.startup
    read_decimal 16, count
  loop:
    bit.if0 16, count, end
    bit.input ch
    bit.print ch
    bit.dec 16, count
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"3\nabc",
    out_bytes=b"abc",
)

# 0278 print_first_then_repeat — byte once, then the byte N times on a new line.
L(
    "0278",
    "print_first_then_repeat",
    "Print First Then Repeat",
    unsigned=True,
    extra_helpers=[PRINT_GLYPH_TIMES],
    value_data=["glyph: bit.vec 8, 0", "count: bit.vec 16, 0"],
    extra_data=D_REP_CTR,
    main_body="""
def main < glyph, count {
    stl.startup
    bit.input glyph
    read_decimal 16, count
    bit.print glyph
    stl.output '\\n'
    print_glyph_times count, glyph
    stl.loop
}
""",
    in_bytes=b"A3\n\0",
    out_bytes=b"A\nAAA",
)

# 0262 print_pair_grid — all (i,j) for i,j in 0-2, "i j\n", row-major.
PAIR_ROW = """
// Print "ri j\\n" for j in 0..count-1 (one grid row of (i,j) pairs).
def print_pair_row ri, count @ loop, body, end < jcol {
    bit.zero 16, jcol
  loop:
    bit.cmp 16, jcol, count, body, end, end
  body:
    bit.print_dec_uint 16, ri
    stl.output ' '
    bit.print_dec_uint 16, jcol
    stl.output '\\n'
    bit.inc 16, jcol
    ;loop
  end:
}
""".strip()

L(
    "0262",
    "print_pair_grid",
    "Print Pair Grid",
    extra_helpers=[PAIR_ROW],
    value_data=["i_idx: bit.vec 16, 0", "three: bit.vec 16, 3", "jcol: bit.vec 16, 0"],
    main_body="""
def main @ loop, body, end < i_idx, three {
    stl.startup
    bit.zero 16, i_idx
  loop:
    bit.cmp 16, i_idx, three, body, end, end
  body:
    print_pair_row i_idx, three
    bit.inc 16, i_idx
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"\0",
    out_bytes=b"0 0\n0 1\n0 2\n1 0\n1 1\n1 2\n2 0\n2 1\n2 2\n",
)

# 0275 print_pair_diff_grid — signed i-j for i,j in 0-3, "i-j\n", row-major.
DIFF_ROW = """
// Print "(ri-j)\\n" (signed) for j in 0..count-1 (one grid row of differences).
def print_diff_row ri, count @ loop, body, end < jcol, diff {
    bit.zero 16, jcol
  loop:
    bit.cmp 16, jcol, count, body, end, end
  body:
    bit.mov 16, diff, ri
    bit.sub 16, diff, jcol
    bit.print_dec_int 16, diff
    stl.output '\\n'
    bit.inc 16, jcol
    ;loop
  end:
}
""".strip()

L(
    "0275",
    "print_pair_diff_grid",
    "Print Pair Diff Grid",
    extra_helpers=[DIFF_ROW],
    value_data=[
        "i_idx: bit.vec 16, 0",
        "four: bit.vec 16, 4",
        "jcol: bit.vec 16, 0",
        "diff: bit.vec 16, 0",
    ],
    main_body="""
def main @ loop, body, end < i_idx, four {
    stl.startup
    bit.zero 16, i_idx
  loop:
    bit.cmp 16, i_idx, four, body, end, end
  body:
    print_diff_row i_idx, four
    bit.inc 16, i_idx
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"\0",
    out_bytes=(b"0\n-1\n-2\n-3\n" b"1\n0\n-1\n-2\n" b"2\n1\n0\n-1\n" b"3\n2\n1\n0\n"),
)

# 0263 fizzbuzz_to_15 — standard FizzBuzz lines 1..15.
L(
    "0263",
    "fizzbuzz_to_15",
    "Fizzbuzz To 15",
    extra_helpers=[PRINT_FIZZBUZZ],
    value_data=["idx: bit.vec 16, 1", "limit: bit.vec 16, 15"],
    extra_data=D_FIZZBUZZ,
    main_body="""
def main @ loop, body, end < idx, limit {
    stl.startup
  loop:
    bit.cmp 16, idx, limit, body, body, end
  body:
    print_fizzbuzz idx
    bit.inc 16, idx
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"\0",
    out_bytes=(b"1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz\n"),
)

# 0264 fizzbuzz_to_20 — same rules, lines 1..20.
L(
    "0264",
    "fizzbuzz_to_20",
    "Fizzbuzz To 20",
    extra_helpers=[PRINT_FIZZBUZZ],
    value_data=["idx: bit.vec 16, 1", "limit: bit.vec 16, 20"],
    extra_data=D_FIZZBUZZ,
    main_body="""
def main @ loop, body, end < idx, limit {
    stl.startup
  loop:
    bit.cmp 16, idx, limit, body, body, end
  body:
    print_fizzbuzz idx
    bit.inc 16, idx
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"\0",
    out_bytes=(
        b"1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n" b"11\nFizz\n13\n14\nFizzBuzz\n16\n17\nFizz\n19\nBuzz\n"
    ),
)

# 0232 print_byte_grid — N rows of N copies of the input byte, each + \n.
L(
    "0232",
    "print_byte_grid",
    "Print Byte Grid",
    unsigned=True,
    extra_helpers=[PRINT_GLYPH_TIMES],
    value_data=["glyph: bit.vec 8, 0", "sep: bit.vec 8, 0", "count: bit.vec 16, 0", "row: bit.vec 16, 0"],
    extra_data=D_REP_CTR,
    main_body="""
def main @ loop, body, end < glyph, sep, count, row {
    stl.startup
    bit.input glyph
    bit.input sep
    read_decimal 16, count
    bit.zero 16, row
  loop:
    bit.cmp 16, row, count, body, end, end
  body:
    print_glyph_times count, glyph
    stl.output '\\n'
    bit.inc 16, row
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"#\n3\n\0",
    out_bytes=b"###\n###\n###\n",
)

# 0236 hollow_box — top/bottom rows N '*'; middle rows '*' + (N-2) spaces + '*'.
HOLLOW_MIDDLE = """
// Print one hollow-box middle row: '*', (count-2) spaces, '*', newline.
def print_box_middle count, star, space @ loop, end < gap, mid_ctr {
    bit.print star
    bit.mov 16, gap, count
    bit.dec 16, gap
    bit.dec 16, gap
    bit.mov 16, mid_ctr, gap
  loop:
    bit.if0 16, mid_ctr, end
    bit.print space
    bit.dec 16, mid_ctr
    ;loop
  end:
    bit.print star
    stl.output '\\n'
}
""".strip()

L(
    "0236",
    "hollow_box",
    "Hollow Box",
    unsigned=True,
    extra_helpers=[PRINT_GLYPH_TIMES, HOLLOW_MIDDLE],
    value_data=[
        "count: bit.vec 16, 0",
        "inner: bit.vec 16, 0",
        "star: bit.vec 8, '*'",
        "space: bit.vec 8, ' '",
        "gap: bit.vec 16, 0",
    ],
    extra_data=D_REP_CTR + ["mid_ctr: bit.vec 16, 0"],
    main_body="""
def main @ loop, end < count, inner, star, space {
    stl.startup
    read_decimal 16, count
    print_glyph_times count, star
    stl.output '\\n'
    bit.mov 16, inner, count
    bit.dec 16, inner
    bit.dec 16, inner
  loop:
    bit.if0 16, inner, end
    print_box_middle count, star, space
    bit.dec 16, inner
    ;loop
  end:
    print_glyph_times count, star
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"4\n\0",
    out_bytes=b"****\n*  *\n*  *\n****\n",
)

# 0238 checkerboard — cell(i,j) is '*' if (i+j) even else '.', top-left '*'.
CHECKER_ROW = """
// Print row ri of an N-wide checkerboard: '*' where (ri+col) is even, else '.'.
def print_checker_row ri, count, star, dot @ loop, body, even, odd, next, end < col, parity {
    bit.zero 16, col
  loop:
    bit.cmp 16, col, count, body, end, end
  body:
    bit.mov 16, parity, ri
    bit.add 16, parity, col
    bit.if0 parity, even
  odd:
    bit.print dot
    ;next
  even:
    bit.print star
  next:
    bit.inc 16, col
    ;loop
  end:
    stl.output '\\n'
}
""".strip()

L(
    "0238",
    "checkerboard",
    "Checkerboard",
    unsigned=True,
    extra_helpers=[CHECKER_ROW],
    value_data=[
        "count: bit.vec 16, 0",
        "row: bit.vec 16, 0",
        "star: bit.vec 8, '*'",
        "dot: bit.vec 8, '.'",
        "col: bit.vec 16, 0",
        "parity: bit.vec 16, 0",
    ],
    main_body="""
def main @ loop, body, end < count, row, star, dot {
    stl.startup
    read_decimal 16, count
    bit.zero 16, row
  loop:
    bit.cmp 16, row, count, body, end, end
  body:
    print_checker_row row, count, star, dot
    bit.inc 16, row
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"3\n\0",
    out_bytes=b"*.*\n.*.\n*.*\n",
)

# 0239 diagonal_stars — cell(i,j) is '*' if i==j else '.'.
DIAG_ROW = """
// Print row ri of an N-wide grid: '*' where col==ri, else '.'; trailing newline.
def print_diag_row ri, count, star, dot @ loop, body, hit, miss, next, end < col {
    bit.zero 16, col
  loop:
    bit.cmp 16, col, count, body, end, end
  body:
    bit.cmp 16, col, ri, miss, hit, miss
  hit:
    bit.print star
    ;next
  miss:
    bit.print dot
  next:
    bit.inc 16, col
    ;loop
  end:
    stl.output '\\n'
}
""".strip()

L(
    "0239",
    "diagonal_stars",
    "Diagonal Stars",
    unsigned=True,
    extra_helpers=[DIAG_ROW],
    value_data=[
        "count: bit.vec 16, 0",
        "row: bit.vec 16, 0",
        "star: bit.vec 8, '*'",
        "dot: bit.vec 8, '.'",
        "col: bit.vec 16, 0",
    ],
    main_body="""
def main @ loop, body, end < count, row, star, dot {
    stl.startup
    read_decimal 16, count
    bit.zero 16, row
  loop:
    bit.cmp 16, row, count, body, end, end
  body:
    print_diag_row row, count, star, dot
    bit.inc 16, row
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"3\n\0",
    out_bytes=b"*..\n.*.\n..*\n",
)

# 0240 x_pattern — '*' if i==j or i+j==N-1 else '.'.
XPAT_ROW = """
// Print row ri of an N-wide X: '*' where col==ri or ri+col==N-1, else '.'.
def print_x_row ri, count, star, dot @ loop, body, anti, hit, miss, next, end < col, sum_rc, edge {
    bit.zero 16, col
    bit.mov 16, edge, count
    bit.dec 16, edge
  loop:
    bit.cmp 16, col, count, body, end, end
  body:
    bit.cmp 16, col, ri, anti, hit, anti
  anti:
    bit.mov 16, sum_rc, ri
    bit.add 16, sum_rc, col
    bit.cmp 16, sum_rc, edge, miss, hit, miss
  hit:
    bit.print star
    ;next
  miss:
    bit.print dot
  next:
    bit.inc 16, col
    ;loop
  end:
    stl.output '\\n'
}
""".strip()

L(
    "0240",
    "x_pattern",
    "X Pattern",
    unsigned=True,
    extra_helpers=[XPAT_ROW],
    value_data=[
        "count: bit.vec 16, 0",
        "row: bit.vec 16, 0",
        "star: bit.vec 8, '*'",
        "dot: bit.vec 8, '.'",
        "col: bit.vec 16, 0",
        "sum_rc: bit.vec 16, 0",
        "edge: bit.vec 16, 0",
    ],
    main_body="""
def main @ loop, body, end < count, row, star, dot {
    stl.startup
    read_decimal 16, count
    bit.zero 16, row
  loop:
    bit.cmp 16, row, count, body, end, end
  body:
    print_x_row row, count, star, dot
    bit.inc 16, row
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"5\n\0",
    out_bytes=b"*...*\n.*.*.\n..*..\n.*.*.\n*...*\n",
)

# 0241 plus_pattern — '*' along middle row/column (mid = (N-1)/2), else '.'.
PLUS_ROW = """
// Print row ri of an N-wide plus: '*' where ri==mid or col==mid, else '.'.
def print_plus_row ri, count, mid, star, dot @ loop, body, chkcol, hit, miss, next, end < col {
    bit.zero 16, col
  loop:
    bit.cmp 16, col, count, body, end, end
  body:
    bit.cmp 16, ri, mid, chkcol, hit, chkcol
  chkcol:
    bit.cmp 16, col, mid, miss, hit, miss
  hit:
    bit.print star
    ;next
  miss:
    bit.print dot
  next:
    bit.inc 16, col
    ;loop
  end:
    stl.output '\\n'
}
""".strip()

L(
    "0241",
    "plus_pattern",
    "Plus Pattern",
    unsigned=True,
    extra_helpers=[PLUS_ROW],
    value_data=[
        "count: bit.vec 16, 0",
        "row: bit.vec 16, 0",
        "mid: bit.vec 16, 0",
        "two: bit.vec 16, 2",
        "qd: bit.vec 16, 0",
        "rd: bit.vec 16, 0",
        "star: bit.vec 8, '*'",
        "dot: bit.vec 8, '.'",
        "col: bit.vec 16, 0",
    ],
    main_body="""
def main @ loop, body, end < count, row, mid, two, qd, rd, star, dot {
    stl.startup
    read_decimal 16, count
    bit.mov 16, mid, count
    bit.dec 16, mid
    bit.div 16, mid, two, qd, rd
    bit.mov 16, mid, qd
    bit.zero 16, row
  loop:
    bit.cmp 16, row, count, body, end, end
  body:
    print_plus_row row, count, mid, star, dot
    bit.inc 16, row
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"5\n\0",
    out_bytes=b"..*..\n..*..\n*****\n..*..\n..*..\n",
)

# 0242 v_pattern — width 2N-1; row i: '*' at col i and col 2N-i, else '.'.
VPAT_ROW = """
// Print one V row of given width: '*' at col==left or col==right (1-indexed).
def print_v_row left, right, width, star, dot @ loop, body, chkr, hit, miss, next, end < col {
    bit.zero 16, col
    bit.inc 16, col
  loop:
    bit.cmp 16, col, width, body, body, end
  body:
    bit.cmp 16, col, left, chkr, hit, chkr
  chkr:
    bit.cmp 16, col, right, miss, hit, miss
  hit:
    bit.print star
    ;next
  miss:
    bit.print dot
  next:
    bit.inc 16, col
    ;loop
  end:
    stl.output '\\n'
}
""".strip()

L(
    "0242",
    "v_pattern",
    "V Pattern",
    unsigned=True,
    extra_helpers=[VPAT_ROW],
    value_data=[
        "count: bit.vec 16, 0",
        "row: bit.vec 16, 0",
        "width: bit.vec 16, 0",
        "right: bit.vec 16, 0",
        "star: bit.vec 8, '*'",
        "dot: bit.vec 8, '.'",
        "col: bit.vec 16, 0",
    ],
    main_body="""
def main @ loop, body, end < count, row, width, right, star, dot {
    stl.startup
    read_decimal 16, count
    bit.mov 16, width, count
    bit.add 16, width, count
    bit.dec 16, width
    bit.zero 16, row
    bit.inc 16, row
  loop:
    bit.cmp 16, row, count, body, body, end
  body:
    bit.mov 16, right, count
    bit.add 16, right, count
    bit.sub 16, right, row
    print_v_row row, right, width, star, dot
    bit.inc 16, row
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"3\n\0",
    out_bytes=b"*...*\n.*.*.\n..*..\n",
)

# 0261 accumulate_sum — read ints (one per line) until empty line; print running sum.
READ_LINE_DECIMAL = """
// Read one decimal line into val[:16]. Set empty_flag if the line is just \\n/\\0.
def read_line_decimal val, empty_flag @ loop, mark_empty, done < ch, nl, digit, err {
    bit.zero 16, val
    bit.zero empty_flag
    bit.input ch
    bit.if0 8, ch, mark_empty
    bit.cmp 8, ch, nl, loop, mark_empty, loop
  loop:
    bit.mul10 16, val
    bit.ascii2dec err, digit, ch
    bit.add 16, val, digit
    bit.input ch
    bit.if0 8, ch, done
    bit.cmp 8, ch, nl, loop, done, loop
  mark_empty:
    bit.one empty_flag
  done:
}
""".strip()

L(
    "0261",
    "accumulate_sum",
    "Accumulate Sum",
    extra_helpers=[READ_LINE_DECIMAL],
    value_data=[
        "x: bit.vec 16, 0",
        "sum: bit.vec 16, 0",
        "empty_flag: bit.bit",
        "ch: bit.vec 8, 0",
        "nl: bit.vec 8, '\\n'",
        "digit: bit.vec 16, 0",
        "err: bit.bit",
    ],
    main_body="""
def main @ loop, end < x, sum, empty_flag {
    stl.startup
    bit.zero 16, sum
  loop:
    read_line_decimal x, empty_flag
    bit.if1 empty_flag, end
    bit.add 16, sum, x
    bit.print_dec_uint 16, sum
    stl.output '\\n'
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"10\n20\n5\n\n\0",
    out_bytes=b"10\n30\n35\n",
)

# 0260 line_then_n_blanks — read N + \n, echo a line, then N more \n.
ECHO_LINE = """
// Echo bytes (including the terminating \\n) until \\n or \\0 is reached.
def echo_line @ loop, end < ch, nl {
  loop:
    bit.input ch
    bit.if0 8, ch, end
    bit.print ch
    bit.cmp 8, ch, nl, loop, end, loop
  end:
}
""".strip()

L(
    "0260",
    "line_then_n_blanks",
    "Line Then N Blanks",
    unsigned=True,
    extra_helpers=[ECHO_LINE],
    value_data=["count: bit.vec 16, 0"],
    main_body="""
def main @ loop, end < count {
    stl.startup
    read_decimal 16, count
    echo_line
  loop:
    bit.if0 16, count, end
    stl.output '\\n'
    bit.dec 16, count
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"2\nhi\n\0",
    out_bytes=b"hi\n\n\n",
)

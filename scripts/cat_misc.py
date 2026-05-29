"""Phase 3 misc category: bounded loops/branches with exact outputs.

A coherent subset of the misc category — the ASCII-described, fully-bounded
programs (no buffer / array / pointer / recursion / unbounded state, and no
literal `|` or non-ASCII in the CATALOG description). Three clusters:

  * music theory: pitch classes, scales, transposition, triad test
  * number/date branches: magic-number, lucky checks, percent-of-day, zodiac
  * format/parse: zigzag art, flags, roman<->arabic, join, paragraph count, song

The deferred misc rows all carry a `<=`/`->` (a non-ASCII byte the header
would have to reproduce) or need a line/word buffer; they are left APPROVED
for a later batch.

Run from the repo root:  python scripts/cat_misc.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog_arith import MAX_INTO, MIN_INTO, emit  # noqa: E402

# Print (root + interval) mod 12 as decimal (no newline). interval is a data
# vector (bit.add needs an in-memory operand, not an immediate). Sum is < 24.
PRINT_DEGREE = """
// Print (root[:16] + interval[:16]) mod 12 as decimal (no newline). Sum is < 24.
def print_degree root, interval @ small, big, end < deg, twelve {
    bit.mov 16, deg, root
    bit.add 16, deg, interval
    bit.cmp 16, deg, twelve, small, big, big
  small:
    bit.print_dec_uint 16, deg
    ;end
  big:
    bit.sub 16, deg, twelve
    bit.print_dec_uint 16, deg
  end:
}
""".strip()

# The 12 chromatic interval constants (data vectors), shared by both scales.
INTERVAL_DATA = [
    "iv0: bit.vec 16, 0",
    "iv2: bit.vec 16, 2",
    "iv3: bit.vec 16, 3",
    "iv4: bit.vec 16, 4",
    "iv5: bit.vec 16, 5",
    "iv7: bit.vec 16, 7",
    "iv8: bit.vec 16, 8",
    "iv9: bit.vec 16, 9",
    "iv10: bit.vec 16, 10",
    "iv11: bit.vec 16, 11",
    "deg: bit.vec 16, 0",
    "twelve: bit.vec 16, 12",
]


# flag = 1 if x[:n] is prime (x >= 2), else 0. Trial division by 2..x-1.
IS_PRIME = """
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
IS_PRIME_DATA = ["d: bit.vec 16, 0", "q: bit.vec 16, 0", "r: bit.vec 16, 0", "two: bit.vec 16, 2"]


# Print the western zodiac sign for month[:16] (1-12) and day[:16] (1-31).
# Each month splits at a cutoff day into an "early" and a "late" sign.
ZODIAC_DECIDE = """
// Print the western zodiac sign for month[:16] (1-12), day[:16] (1-31).
def zodiac_decide month, day \
        @ m1, m2, m3, m4, m5, m6, m7, m8, m9, m10, m11, m12, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12, \
        e1, l1, e2, l2, e3, l3, e4, l4, e5, l5, e6, l6, e7, l7, e8, l8, e9, l9, e10, l10, e11, l11, e12, l12, end \
        < mo1, mo2, mo3, mo4, mo5, mo6, mo7, mo8, mo9, mo10, mo11, \
        d19, d20, d21, d22, d23 {
    bit.cmp 16, month, mo1, t2, m1, t2
  t2:
    bit.cmp 16, month, mo2, t3, m2, t3
  t3:
    bit.cmp 16, month, mo3, t4, m3, t4
  t4:
    bit.cmp 16, month, mo4, t5, m4, t5
  t5:
    bit.cmp 16, month, mo5, t6, m5, t6
  t6:
    bit.cmp 16, month, mo6, t7, m6, t7
  t7:
    bit.cmp 16, month, mo7, t8, m7, t8
  t8:
    bit.cmp 16, month, mo8, t9, m8, t9
  t9:
    bit.cmp 16, month, mo9, t10, m9, t10
  t10:
    bit.cmp 16, month, mo10, t11, m10, t11
  t11:
    bit.cmp 16, month, mo11, t12, m11, t12
  t12:
    ;m12
  m1:
    bit.cmp 16, day, d20, e1, l1, l1
  e1:
    stl.output "Capricorn"
    ;end
  l1:
    stl.output "Aquarius"
    ;end
  m2:
    bit.cmp 16, day, d19, e2, l2, l2
  e2:
    stl.output "Aquarius"
    ;end
  l2:
    stl.output "Pisces"
    ;end
  m3:
    bit.cmp 16, day, d21, e3, l3, l3
  e3:
    stl.output "Pisces"
    ;end
  l3:
    stl.output "Aries"
    ;end
  m4:
    bit.cmp 16, day, d20, e4, l4, l4
  e4:
    stl.output "Aries"
    ;end
  l4:
    stl.output "Taurus"
    ;end
  m5:
    bit.cmp 16, day, d21, e5, l5, l5
  e5:
    stl.output "Taurus"
    ;end
  l5:
    stl.output "Gemini"
    ;end
  m6:
    bit.cmp 16, day, d21, e6, l6, l6
  e6:
    stl.output "Gemini"
    ;end
  l6:
    stl.output "Cancer"
    ;end
  m7:
    bit.cmp 16, day, d23, e7, l7, l7
  e7:
    stl.output "Cancer"
    ;end
  l7:
    stl.output "Leo"
    ;end
  m8:
    bit.cmp 16, day, d23, e8, l8, l8
  e8:
    stl.output "Leo"
    ;end
  l8:
    stl.output "Virgo"
    ;end
  m9:
    bit.cmp 16, day, d23, e9, l9, l9
  e9:
    stl.output "Virgo"
    ;end
  l9:
    stl.output "Libra"
    ;end
  m10:
    bit.cmp 16, day, d23, e10, l10, l10
  e10:
    stl.output "Libra"
    ;end
  l10:
    stl.output "Scorpio"
    ;end
  m11:
    bit.cmp 16, day, d22, e11, l11, l11
  e11:
    stl.output "Scorpio"
    ;end
  l11:
    stl.output "Sagittarius"
    ;end
  m12:
    bit.cmp 16, day, d22, e12, l12, l12
  e12:
    stl.output "Sagittarius"
    ;end
  l12:
    stl.output "Capricorn"
  end:
}
""".strip()
ZODIAC_DATA = [
    "mo1: bit.vec 16, 1",
    "mo2: bit.vec 16, 2",
    "mo3: bit.vec 16, 3",
    "mo4: bit.vec 16, 4",
    "mo5: bit.vec 16, 5",
    "mo6: bit.vec 16, 6",
    "mo7: bit.vec 16, 7",
    "mo8: bit.vec 16, 8",
    "mo9: bit.vec 16, 9",
    "mo10: bit.vec 16, 10",
    "mo11: bit.vec 16, 11",
    "d19: bit.vec 16, 19",
    "d20: bit.vec 16, 20",
    "d21: bit.vec 16, 21",
    "d22: bit.vec 16, 22",
    "d23: bit.vec 16, 23",
]


# Helpers for the "bottles of beer" song. say_count prints the bottle phrase
# with correct grammar (0 -> "no more bottles", 1 -> "1 bottle", else plural);
# sing_verse prints the canonical 2-line refrain for a given bottle count.
BOTTLES_HELPERS = """
// Print "<n> bottle(s) of beer" for n[:16] (0 -> "no more bottles of beer").
def say_count n @ zero, one, many, many_print, suffix < zero16, one16 {
    bit.cmp 16, n, zero16, many, zero, many
  zero:
    stl.output "no more bottles"
    ;suffix
  one:
    stl.output "1 bottle"
    ;suffix
  many:
    bit.cmp 16, n, one16, many_print, one, many_print
  many_print:
    bit.print_dec_uint 16, n
    stl.output " bottles"
  suffix:
    stl.output " of beer"
}

// Print the canonical 2-line verse for `count` bottles (count >= 1). `lower`
// is scratch holding count-1 for the second line.
def sing_verse count, lower {
    say_count count
    stl.output " on the wall, "
    say_count count
    stl.output ".\\n"
    stl.output "Take one down and pass it around, "
    bit.mov 16, lower, count
    bit.dec 16, lower
    say_count lower
    stl.output " on the wall.\\n"
}
""".strip()
BOTTLES_DATA = ["zero16: bit.vec 16, 0", "one16: bit.vec 16, 1"]


def M(nnnn, slug, name, **kw):
    emit("misc", nnnn, slug, name, **kw)


# ===================================================================
# format / fixed-output
# ===================================================================

# print_zigzag_3_lines — fixed 3-line zigzag, no input
M(
    "0889",
    "print_zigzag_3_lines",
    "Print Zigzag 3 Lines",
    value_data=[],
    main_body="""
def main {
    stl.startup
    stl.output "*       *\\n  *   *  \\n    *    \\n"
    stl.loop
}
""",
    in_bytes=b"",
    out_bytes=b"*       *\n  *   *  \n    *    \n",
)


# ===================================================================
# number / branch
# ===================================================================

# magic_number_8 — N mod 8 == 0 -> magic, else not magic
M(
    "0880",
    "magic_number_8",
    "Magic Number 8",
    unsigned=True,
    value_data=[
        "val: bit.vec 16, 0",
        "eight: bit.vec 16, 8",
        "q: bit.vec 16, 0",
        "r: bit.vec 16, 0",
    ],
    main_body="""
def main @ magic, plain, done < val, eight, q, r {
    stl.startup
    read_decimal 16, val
    bit.div 16, val, eight, q, r
    bit.if0 16, r, magic
  plain:
    stl.output "not magic\\n"
    ;done
  magic:
    stl.output "magic!\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"24\n\0",
    out_bytes=b"magic!\n",
)

# lucky_sum_check — read 3 decimals 1-9, sum divisible by 7 -> 1 else 0
M(
    "0878",
    "lucky_sum_check",
    "Lucky Sum Check",
    unsigned=True,
    value_data=[
        "a: bit.vec 16, 0",
        "b: bit.vec 16, 0",
        "c: bit.vec 16, 0",
        "seven: bit.vec 16, 7",
        "q: bit.vec 16, 0",
        "r: bit.vec 16, 0",
    ],
    main_body="""
def main @ yes, no, done < a, b, c, seven, q, r {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    read_decimal 16, c
    bit.add 16, a, b
    bit.add 16, a, c
    bit.div 16, a, seven, q, r
    bit.if0 16, r, yes
  no:
    stl.output "0\\n"
    ;done
  yes:
    stl.output "1\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"3\n4\n7\n\0",
    out_bytes=b"1\n",
)

# lucky_year_has_7 — read year + \n, print 1 if any digit char is '7'
M(
    "0879",
    "lucky_year_has_7",
    "Lucky Year Has 7",
    value_data=[
        "ch: bit.vec 8, 0",
        "nl: bit.vec 8, '\\n'",
        "seven: bit.vec 8, '7'",
        "found: bit.bit",
    ],
    main_body="""
def main @ loop, check, hit, next, done, no, fin < ch, nl, seven, found {
    stl.startup
    bit.zero found
  loop:
    bit.input ch
    bit.if0 8, ch, done
    bit.cmp 8, ch, nl, check, done, check
  check:
    bit.cmp 8, ch, seven, next, hit, next
  hit:
    bit.one found
  next:
    ;loop
  done:
    bit.if0 found, no
    stl.output "1\\n"
    ;fin
  no:
    stl.output "0\\n"
  fin:
    stl.loop
}
""",
    in_bytes=b"1975\n\0",
    out_bytes=b"1\n",
)

# day_progress_percent — (hour*60+minute)*100/1440 == (total_minutes*5)/72
M(
    "0892",
    "day_progress_percent",
    "Day Progress Percent",
    unsigned=True,
    mul=True,
    value_data=[
        "hour: bit.vec 16, 0",
        "minute: bit.vec 16, 0",
        "total: bit.vec 16, 0",
        "scaled: bit.vec 16, 0",
        "sixty: bit.vec 16, 60",
        "five: bit.vec 16, 5",
        "sev2: bit.vec 16, 72",
        "q: bit.vec 16, 0",
        "r: bit.vec 16, 0",
    ],
    main_body="""
def main < hour, minute, total, scaled, sixty, five, sev2, q, r {
    stl.startup
    read_decimal 16, hour
    read_decimal 16, minute
    mul_into 16, total, sixty, hour
    bit.add 16, total, minute
    mul_into 16, scaled, total, five
    bit.div 16, scaled, sev2, q, r
    bit.print_dec_uint 16, q
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"12\n0\n\0",
    out_bytes=b"50\n",
)

# is_prime_or_one — read N 1-50, print prime if N is prime OR N==1, else composite
M(
    "0894",
    "is_prime_or_one",
    "Is Prime Or One",
    unsigned=True,
    extra_helpers=[IS_PRIME],
    value_data=["val: bit.vec 16, 0", "flag: bit.bit", "one: bit.vec 16, 1"],
    extra_data=IS_PRIME_DATA,
    main_body="""
def main @ yes, no, check_prime, done < val, flag, one {
    stl.startup
    read_decimal 16, val
    bit.cmp 16, val, one, no, yes, check_prime
  check_prime:
    is_prime_into 16, flag, val
    bit.if0 flag, no
  yes:
    stl.output "prime\\n"
    ;done
  no:
    stl.output "composite\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"1\n\0",
    out_bytes=b"prime\n",
)

# zodiac_chinese — read year 1900-2099, animal = (year-1900) mod 12
M(
    "0872",
    "zodiac_chinese",
    "Zodiac Chinese",
    unsigned=True,
    value_data=[
        "year: bit.vec 16, 0",
        "base: bit.vec 16, 1900",
        "twelve: bit.vec 16, 12",
        "q: bit.vec 16, 0",
        "r: bit.vec 16, 0",
    ],
    main_body="""
def main @ done < year, base, twelve, q, r {
    stl.startup
    read_decimal 16, year
    bit.sub 16, year, base
    bit.div 16, year, twelve, q, r
    pick12 r, done
  done:
    stl.output '\\n'
    stl.loop
}

// Print the Chinese zodiac animal whose index (0-11) is in r[:16].
def pick12 r, after \
        @ animal0, try1, try2, try3, try4, try5, try6, try7, try8, try9, try10, \
        a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11 \
        < c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11 {
    bit.cmp 16, r, c1, animal0, try1, try1
  animal0:
    stl.output "Rat"
    ;after
  try1:
    bit.cmp 16, r, c2, a1, try2, try2
  a1:
    stl.output "Ox"
    ;after
  try2:
    bit.cmp 16, r, c3, a2, try3, try3
  a2:
    stl.output "Tiger"
    ;after
  try3:
    bit.cmp 16, r, c4, a3, try4, try4
  a3:
    stl.output "Rabbit"
    ;after
  try4:
    bit.cmp 16, r, c5, a4, try5, try5
  a4:
    stl.output "Dragon"
    ;after
  try5:
    bit.cmp 16, r, c6, a5, try6, try6
  a5:
    stl.output "Snake"
    ;after
  try6:
    bit.cmp 16, r, c7, a6, try7, try7
  a6:
    stl.output "Horse"
    ;after
  try7:
    bit.cmp 16, r, c8, a7, try8, try8
  a7:
    stl.output "Goat"
    ;after
  try8:
    bit.cmp 16, r, c9, a8, try9, try9
  a8:
    stl.output "Monkey"
    ;after
  try9:
    bit.cmp 16, r, c10, a9, try10, try10
  a9:
    stl.output "Rooster"
    ;after
  try10:
    bit.cmp 16, r, c11, a10, a11, a11
  a10:
    stl.output "Dog"
    ;after
  a11:
    stl.output "Pig"
}
""",
    extra_data=[
        "c1: bit.vec 16, 1",
        "c2: bit.vec 16, 2",
        "c3: bit.vec 16, 3",
        "c4: bit.vec 16, 4",
        "c5: bit.vec 16, 5",
        "c6: bit.vec 16, 6",
        "c7: bit.vec 16, 7",
        "c8: bit.vec 16, 8",
        "c9: bit.vec 16, 9",
        "c10: bit.vec 16, 10",
        "c11: bit.vec 16, 11",
    ],
    in_bytes=b"2008\n\0",
    out_bytes=b"Rat\n",
)


# ===================================================================
# music theory cluster
# ===================================================================

# note_name_to_pitch_class — letter (+ optional '#') -> pitch class 0-11
M(
    "1023",
    "note_name_to_pitch_class",
    "Note Name To Pitch Class",
    value_data=[
        "ch: bit.vec 8, 0",
        "letter: bit.vec 8, 0",
        "pc: bit.vec 8, 0",
        "is_sharp: bit.bit",
        "sharp: bit.vec 8, '#'",
        "cc: bit.vec 8, 'C'",
        "dd: bit.vec 8, 'D'",
        "ee: bit.vec 8, 'E'",
        "ff: bit.vec 8, 'F'",
        "gg: bit.vec 8, 'G'",
        "aa: bit.vec 8, 'A'",
    ],
    main_body="""
def main @ try_d, try_e, try_f, try_g, try_a, set_b, apply \
        < ch, letter, pc, is_sharp, cc, dd, ee, ff, gg, aa, \
        dd_pc, ee_pc, ff_pc, gg_pc, aa_pc, bb_pc {
    stl.startup
    bit.input letter
    bit.zero is_sharp
    bit.input ch
    detect_sharp ch, is_sharp
    bit.cmp 8, letter, cc, try_d, apply, try_d
  try_d:
    bit.zero 8, pc
    bit.add 8, pc, dd_pc
    bit.cmp 8, letter, dd, try_e, apply, try_e
  try_e:
    bit.zero 8, pc
    bit.add 8, pc, ee_pc
    bit.cmp 8, letter, ee, try_f, apply, try_f
  try_f:
    bit.zero 8, pc
    bit.add 8, pc, ff_pc
    bit.cmp 8, letter, ff, try_g, apply, try_g
  try_g:
    bit.zero 8, pc
    bit.add 8, pc, gg_pc
    bit.cmp 8, letter, gg, try_a, apply, try_a
  try_a:
    bit.zero 8, pc
    bit.add 8, pc, aa_pc
    bit.cmp 8, letter, aa, set_b, apply, set_b
  set_b:
    bit.zero 8, pc
    bit.add 8, pc, bb_pc
  apply:
    apply_sharp pc, is_sharp
    bit.print_dec_uint 8, pc
    stl.output '\\n'
    stl.loop
}

// Set is_sharp if ch is '#'.
def detect_sharp ch, is_sharp @ hit, end < sharp {
    bit.cmp 8, ch, sharp, end, hit, end
  hit:
    bit.one is_sharp
  end:
}

// If is_sharp, pc += 1 (sharps raise the pitch class by a semitone).
def apply_sharp pc, is_sharp @ end {
    bit.if0 is_sharp, end
    bit.inc 8, pc
  end:
}
""",
    extra_data=[
        "dd_pc: bit.vec 8, 2",
        "ee_pc: bit.vec 8, 4",
        "ff_pc: bit.vec 8, 5",
        "gg_pc: bit.vec 8, 7",
        "aa_pc: bit.vec 8, 9",
        "bb_pc: bit.vec 8, 11",
    ],
    in_bytes=b"A#\n\0",
    out_bytes=b"10\n",
)

# midi_to_pitch_class — read MIDI 0-127, print midi mod 12
M(
    "1025",
    "midi_to_pitch_class",
    "Midi To Pitch Class",
    unsigned=True,
    value_data=[
        "val: bit.vec 16, 0",
        "twelve: bit.vec 16, 12",
        "q: bit.vec 16, 0",
        "r: bit.vec 16, 0",
    ],
    main_body="""
def main < val, twelve, q, r {
    stl.startup
    read_decimal 16, val
    bit.div 16, val, twelve, q, r
    bit.print_dec_uint 16, r
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"61\n\0",
    out_bytes=b"1\n",
)

# transpose_by_semitones — MIDI + signed shift, clamp to [0,127]
M(
    "1026",
    "transpose_by_semitones",
    "Transpose By Semitones",
    unsigned=True,
    signed=True,
    value_data=[
        "midi: bit.vec 16, 0",
        "shift: bit.vec 16, 0",
        "lo: bit.vec 16, 0",
        "hi: bit.vec 16, 127",
    ],
    main_body="""
def main @ check_hi, clamp_lo, use_hi, done < midi, shift, lo, hi {
    stl.startup
    read_decimal 16, midi
    read_signed_decimal 16, shift
    bit.add 16, midi, shift
    bit.if1 midi + 15*dw, clamp_lo
    bit.cmp 16, midi, hi, check_hi, done, use_hi
  check_hi:
    ;done
  use_hi:
    bit.mov 16, midi, hi
    ;done
  clamp_lo:
    bit.mov 16, midi, lo
  done:
    bit.print_dec_uint 16, midi
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"60\n7\n\0",
    out_bytes=b"67\n",
)

# major_scale_from_root_pcs — root + intervals 0,2,4,5,7,9,11, all mod 12
M(
    "1027",
    "major_scale_from_root_pcs",
    "Major Scale From Root Pcs",
    unsigned=True,
    extra_helpers=[PRINT_DEGREE],
    value_data=["root: bit.vec 16, 0"],
    extra_data=INTERVAL_DATA,
    main_body="""
def main < root, iv0, iv2, iv4, iv5, iv7, iv9, iv11 {
    stl.startup
    read_decimal 16, root
    print_degree root, iv0
    stl.output ' '
    print_degree root, iv2
    stl.output ' '
    print_degree root, iv4
    stl.output ' '
    print_degree root, iv5
    stl.output ' '
    print_degree root, iv7
    stl.output ' '
    print_degree root, iv9
    stl.output ' '
    print_degree root, iv11
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"0\n\0",
    out_bytes=b"0 2 4 5 7 9 11\n",
)

# minor_scale_from_root_pcs — root + intervals 0,2,3,5,7,8,10, all mod 12
M(
    "1028",
    "minor_scale_from_root_pcs",
    "Minor Scale From Root Pcs",
    unsigned=True,
    extra_helpers=[PRINT_DEGREE],
    value_data=["root: bit.vec 16, 0"],
    extra_data=INTERVAL_DATA,
    main_body="""
def main < root, iv0, iv2, iv3, iv5, iv7, iv8, iv10 {
    stl.startup
    read_decimal 16, root
    print_degree root, iv0
    stl.output ' '
    print_degree root, iv2
    stl.output ' '
    print_degree root, iv3
    stl.output ' '
    print_degree root, iv5
    stl.output ' '
    print_degree root, iv7
    stl.output ' '
    print_degree root, iv8
    stl.output ' '
    print_degree root, iv10
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"0\n\0",
    out_bytes=b"0 2 3 5 7 8 10\n",
)

# is_major_triad — read 3 MIDI, sort, check sorted intervals are 4 then 3
M(
    "1029",
    "is_major_triad",
    "Is Major Triad",
    unsigned=True,
    extra_helpers=[MIN_INTO, MAX_INTO],
    value_data=[
        "m1: bit.vec 16, 0",
        "m2: bit.vec 16, 0",
        "m3: bit.vec 16, 0",
        "lo: bit.vec 16, 0",
        "mid: bit.vec 16, 0",
        "hi: bit.vec 16, 0",
        "d1: bit.vec 16, 0",
        "d2: bit.vec 16, 0",
        "four: bit.vec 16, 4",
        "three: bit.vec 16, 3",
    ],
    main_body="""
def main @ yes, no, check_d2, done < m1, m2, m3, lo, mid, hi, d1, d2, four, three {
    stl.startup
    read_decimal 16, m1
    read_decimal 16, m2
    read_decimal 16, m3
    sort3 m1, m2, m3, lo, mid, hi
    bit.mov 16, d1, mid
    bit.sub 16, d1, lo
    bit.mov 16, d2, hi
    bit.sub 16, d2, mid
    bit.cmp 16, d1, four, no, check_d2, no
  check_d2:
    bit.cmp 16, d2, three, no, yes, no
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}

// Sort a,b,c (16-bit) into lo<=mid<=hi. mid = (a+b+c) - lo - hi.
def sort3 a, b, c, lo, mid, hi {
    min_into 16, lo, a, b
    min_into 16, lo, lo, c
    max_into 16, hi, a, b
    max_into 16, hi, hi, c
    bit.mov 16, mid, a
    bit.add 16, mid, b
    bit.add 16, mid, c
    bit.sub 16, mid, lo
    bit.sub 16, mid, hi
}
""",
    in_bytes=b"60\n64\n67\n\0",
    out_bytes=b"1\n",
)

# ===================================================================
# format / parse cluster
# ===================================================================

# country_flag_short — 3-letter code USA/FRA/JPN -> a hardcoded 2-line flag
M(
    "0875",
    "country_flag_short",
    "Country Flag Short",
    value_data=[
        "c0: bit.vec 8, 0",
        "c1: bit.vec 8, 0",
        "c2: bit.vec 8, 0",
        "uu: bit.vec 8, 'U'",
        "ff: bit.vec 8, 'F'",
    ],
    main_body="""
def main @ usa, fra, jpn, try_fra, done < c0, c1, c2, uu, ff {
    stl.startup
    bit.input c0
    bit.input c1
    bit.input c2
    bit.cmp 8, c0, uu, try_fra, usa, try_fra
  try_fra:
    bit.cmp 8, c0, ff, jpn, fra, jpn
  usa:
    stl.output "[***][===]\\n[===][***]\\n"
    ;done
  fra:
    stl.output "[|][#][=]\\n[|][#][=]\\n"
    ;done
  jpn:
    stl.output "[ === ]\\n[  O  ]\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"USA\n\0",
    out_bytes=b"[***][===]\n[===][***]\n",
)

# join_words_with_space — read N, then N \n-terminated words, join by single space
M(
    "0876",
    "join_words_with_space",
    "Join Words With Space",
    value_data=[
        "ch: bit.vec 8, 0",
        "count: bit.vec 8, 0",
        "idx: bit.vec 8, 0",
        "nl: bit.vec 8, '\\n'",
        "digit: bit.vec 4, 0",
        "err: bit.bit",
    ],
    main_body="""
def main @ loop, body, word, done < ch, count, idx, digit, err {
    stl.startup
    bit.input ch
    bit.ascii2dec err, digit, ch
    bit.zero 8, count
    bit.mov 4, count, digit
    bit.input ch
    bit.zero 8, idx
  loop:
    bit.cmp 8, idx, count, body, done, done
  body:
    bit.if0 8, idx, word
    stl.output ' '
  word:
    echo_word ch
    bit.inc 8, idx
    ;loop
  done:
    stl.output '\\n'
    stl.loop
}

// Echo bytes from stdin until \\n (the \\n is consumed, not printed).
def echo_word ch @ loop, print_it, end < nl {
  loop:
    bit.input ch
    bit.cmp 8, ch, nl, print_it, end, print_it
  print_it:
    bit.print ch
    ;loop
  end:
}
""",
    in_bytes=b"3\nfoo\nbar\nbaz\n\0",
    out_bytes=b"foo bar baz\n",
)

# arabic_to_roman_30 — read decimal 1-30, print Roman numeral
M(
    "0874",
    "arabic_to_roman_30",
    "Arabic To Roman 30",
    unsigned=True,
    value_data=[
        "val: bit.vec 16, 0",
        "tens: bit.vec 16, 0",
        "ones: bit.vec 16, 0",
        "ten: bit.vec 16, 10",
        "q: bit.vec 16, 0",
        "r: bit.vec 16, 0",
    ],
    main_body="""
def main @ tloop, tend < val, tens, ones, ten, q, r {
    stl.startup
    read_decimal 16, val
    bit.div 16, val, ten, q, r
    bit.mov 16, tens, q
    bit.mov 16, ones, r
  tloop:
    bit.if0 16, tens, tend
    stl.output 'X'
    bit.dec 16, tens
    ;tloop
  tend:
    print_ones_roman ones
    stl.output '\\n'
    stl.loop
}

// Print the Roman numeral for a ones digit 0-9 held in ones[:16].
def print_ones_roman ones \
        @ t2, t3, t4, t5, t6, t7, t8, t9, p1, p2, p3, p4, p5, p6, p7, p8, p9, end \
        < r1, r2, r3, r4, r5, r6, r7, r8, r9 {
    bit.cmp 16, ones, r1, t2, p1, t2
  t2:
    bit.cmp 16, ones, r2, t3, p2, t3
  t3:
    bit.cmp 16, ones, r3, t4, p3, t4
  t4:
    bit.cmp 16, ones, r4, t5, p4, t5
  t5:
    bit.cmp 16, ones, r5, t6, p5, t6
  t6:
    bit.cmp 16, ones, r6, t7, p6, t7
  t7:
    bit.cmp 16, ones, r7, t8, p7, t8
  t8:
    bit.cmp 16, ones, r8, t9, p8, t9
  t9:
    bit.cmp 16, ones, r9, end, p9, end
  p1:
    stl.output "I"
    ;end
  p2:
    stl.output "II"
    ;end
  p3:
    stl.output "III"
    ;end
  p4:
    stl.output "IV"
    ;end
  p5:
    stl.output "V"
    ;end
  p6:
    stl.output "VI"
    ;end
  p7:
    stl.output "VII"
    ;end
  p8:
    stl.output "VIII"
    ;end
  p9:
    stl.output "IX"
  end:
}
""",
    extra_data=[
        "r1: bit.vec 16, 1",
        "r2: bit.vec 16, 2",
        "r3: bit.vec 16, 3",
        "r4: bit.vec 16, 4",
        "r5: bit.vec 16, 5",
        "r6: bit.vec 16, 6",
        "r7: bit.vec 16, 7",
        "r8: bit.vec 16, 8",
        "r9: bit.vec 16, 9",
    ],
    in_bytes=b"24\n\0",
    out_bytes=b"XXIV\n",
)

# roman_to_arabic_30 — read Roman string, accumulate with subtractive rule
M(
    "0873",
    "roman_to_arabic_30",
    "Roman To Arabic 30",
    value_data=[
        "ch: bit.vec 8, 0",
        "nl: bit.vec 8, '\\n'",
        "ii: bit.vec 8, 'I'",
        "vv: bit.vec 8, 'V'",
        "total: bit.vec 16, 0",
        "cur: bit.vec 16, 0",
        "prev: bit.vec 16, 0",
        "twice: bit.vec 16, 0",
        "one16: bit.vec 16, 1",
        "five16: bit.vec 16, 5",
        "ten16: bit.vec 16, 10",
    ],
    main_body="""
def main @ loop, classify, set_one, set_v, set_five, set_x, accumulate, do_sub, no_sub, done \
        < ch, nl, ii, vv, total, cur, prev, twice, one16, five16, ten16 {
    stl.startup
    bit.zero 16, total
    bit.zero 16, prev
  loop:
    bit.input ch
    bit.if0 8, ch, done
    bit.cmp 8, ch, nl, classify, done, classify
  classify:
    bit.cmp 8, ch, ii, set_v, set_one, set_v
  set_one:
    bit.mov 16, cur, one16
    ;accumulate
  set_v:
    bit.cmp 8, ch, vv, set_x, set_five, set_x
  set_five:
    bit.mov 16, cur, five16
    ;accumulate
  set_x:
    bit.mov 16, cur, ten16
  accumulate:
    bit.add 16, total, cur
    bit.cmp 16, prev, cur, do_sub, no_sub, no_sub
  do_sub:
    bit.mov 16, twice, prev
    bit.add 16, twice, prev
    bit.sub 16, total, twice
  no_sub:
    bit.mov 16, prev, cur
    ;loop
  done:
    bit.print_dec_uint 16, total
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"XXIV\n\0",
    out_bytes=b"24\n",
)

# count_paragraphs — count maximal runs of non-empty lines
M(
    "0885",
    "count_paragraphs",
    "Count Paragraphs",
    value_data=[
        "ch: bit.vec 8, 0",
        "nl: bit.vec 8, '\\n'",
        "count: bit.vec 16, 0",
        "in_para: bit.bit",
        "line_filled: bit.bit",
    ],
    main_body="""
def main @ loop, mark_filled, eol, eof < ch, nl, count, in_para, line_filled {
    stl.startup
    bit.zero 16, count
    bit.zero in_para
    bit.zero line_filled
  loop:
    bit.input ch
    bit.if0 8, ch, eof
    bit.cmp 8, ch, nl, mark_filled, eol, mark_filled
  mark_filled:
    bit.one line_filled
    ;loop
  eol:
    end_line count, in_para, line_filled
    ;loop
  eof:
    end_line count, in_para, line_filled
    bit.print_dec_uint 16, count
    stl.output '\\n'
    stl.loop
}

// End the current line: a non-empty line opens a paragraph (count++) if one
// is not already open; an empty line closes any open paragraph. Resets the
// per-line content flag either way.
def end_line count, in_para, line_filled @ empty, opened, end {
    bit.if0 line_filled, empty
    bit.if1 in_para, opened
    bit.inc 16, count
    bit.one in_para
  opened:
    bit.zero line_filled
    ;end
  empty:
    bit.zero in_para
    bit.zero line_filled
  end:
}
""",
    in_bytes=b"para one\nstill one\n\npara two\n\0",
    out_bytes=b"2\n",
)

# zodiac_western — month + day -> western zodiac sign
M(
    "0871",
    "zodiac_western",
    "Zodiac Western",
    unsigned=True,
    extra_helpers=[ZODIAC_DECIDE],
    value_data=["month: bit.vec 16, 0", "day: bit.vec 16, 0"],
    extra_data=ZODIAC_DATA,
    main_body="""
def main < month, day {
    stl.startup
    read_decimal 16, month
    read_decimal 16, day
    zodiac_decide month, day
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"4\n15\n\0",
    out_bytes=b"Aries\n",
)

# ===================================================================
# song cluster
# ===================================================================


def _bottles_song(top: int) -> bytes:
    """The canonical verses counting down from `top` to 1 (matches sing_verse)."""

    def say(n):
        if n == 0:
            phrase = "no more bottles"
        elif n == 1:
            phrase = "1 bottle"
        else:
            phrase = f"{n} bottles"
        return phrase + " of beer"

    verses = []
    for c in range(top, 0, -1):
        verses.append(
            f"{say(c)} on the wall, {say(c)}.\n" f"Take one down and pass it around, {say(c - 1)} on the wall.\n"
        )
    return "".join(verses).encode()


# bottles_of_beer_5 — no input, 5 verses counting down from 5 to 1
M(
    "0869",
    "bottles_of_beer_5",
    "Bottles Of Beer 5",
    extra_helpers=[BOTTLES_HELPERS],
    value_data=["count: bit.vec 16, 5", "lower: bit.vec 16, 0"],
    extra_data=BOTTLES_DATA,
    main_body="""
def main @ loop, end < count, lower {
    stl.startup
  loop:
    bit.if0 16, count, end
    sing_verse count, lower
    bit.dec 16, count
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"",
    out_bytes=_bottles_song(5),
)

# bottles_of_beer_n — read digit N 1-9, print N verses counting down from N
M(
    "0870",
    "bottles_of_beer_n",
    "Bottles Of Beer N",
    unsigned=True,
    extra_helpers=[BOTTLES_HELPERS],
    value_data=["count: bit.vec 16, 0", "lower: bit.vec 16, 0"],
    extra_data=BOTTLES_DATA,
    main_body="""
def main @ loop, end < count, lower {
    stl.startup
    read_decimal 16, count
  loop:
    bit.if0 16, count, end
    sing_verse count, lower
    bit.dec 16, count
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"3\n\0",
    out_bytes=_bottles_song(3),
)

print("---")
print("MISC DONE")

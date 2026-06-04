"""Catalog category: branching — read + compare + branch + print.

These programs read one or more decimal/byte inputs, run comparisons via
`bit.cmp` (and sign-bit / parity tests), and print a classification: a sorted
pair/triple, a category word, a 1/0 flag, or a selected value. They lean on the
shared decimal-I/O helpers in `catalog_arith` (read_decimal / read_signed_decimal
/ mul_into) plus a few branching-specific helpers defined inline below.

Run from the repo root:  python scripts/cat_branching.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog_arith import MAX_INTO, MIN_INTO, emit  # noqa: E402


def B(nnnn, slug, name, **kw):
    emit("branching", nnnn, slug, name, **kw)


# ---- in_range: jump-to-yes/no for 8-bit byte bounds (recurs in byte classifiers) ----
IN_RANGE_8 = """
// Jump to `yes` if lo <= ch <= hi (lo, hi are bit[:8] bounds), else to `no`.
def in_range_8 ch, lo, hi, yes, no @ check_hi {
    bit.cmp 8, ch, lo, no, yes, check_hi
  check_hi:
    bit.cmp 8, ch, hi, yes, yes, no
}
""".strip()

# ---- 32-bit repeated-addition multiply (bmi needs 32-bit intermediates) ----
MUL32_INTO = """
// dst[:32] = addend[:32] * times[:32], via repeated addition (times is small).
def mul32_into dst, addend, times @ loop, end < mul32_counter {
    bit.zero 32, dst
    bit.mov 32, mul32_counter, times
  loop:
    bit.if0 32, mul32_counter, end
    bit.add 32, dst, addend
    bit.dec 32, mul32_counter
    ;loop
  end:
}
""".strip()

# ---- case folding for one byte (toggles ASCII bit 5 only for letters) ----
TO_UPPER_BYTE = """
// If ch is `a`-`z`, uppercase it by clearing ASCII bit 5 (0x20); else leave it.
def to_upper_byte ch @ do_fold, done < la, lz {
    in_range_8 ch, la, lz, do_fold, done
  do_fold:
    bit.not ch + 5*dw
  done:
}
""".strip()

TO_LOWER_BYTE = """
// If ch is `A`-`Z`, lowercase it by setting ASCII bit 5 (0x20); else leave it.
def to_lower_byte ch @ do_fold, done < ua, uz {
    in_range_8 ch, ua, uz, do_fold, done
  do_fold:
    bit.not ch + 5*dw
  done:
}
""".strip()


# ============================================================================
# Sorts of two / three decimals
# ============================================================================

# 0194 sort_two_asc
B(
    "0194",
    "sort_two_asc",
    "Sort Two Asc",
    unsigned=True,
    extra_helpers=[MIN_INTO, MAX_INTO],
    value_data=["a: bit.vec 16, 0", "b: bit.vec 16, 0", "lo: bit.vec 16, 0", "hi: bit.vec 16, 0"],
    main_body="""
def main < a, b, lo, hi {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    min_into 16, lo, a, b
    max_into 16, hi, a, b
    bit.print_dec_uint 16, lo
    stl.output '\\n'
    bit.print_dec_uint 16, hi
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"8\n3\n\0",
    out_bytes=b"3\n8\n",
)

# 0195 sort_two_desc
B(
    "0195",
    "sort_two_desc",
    "Sort Two Desc",
    unsigned=True,
    extra_helpers=[MIN_INTO, MAX_INTO],
    value_data=["a: bit.vec 16, 0", "b: bit.vec 16, 0", "lo: bit.vec 16, 0", "hi: bit.vec 16, 0"],
    main_body="""
def main < a, b, lo, hi {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    min_into 16, lo, a, b
    max_into 16, hi, a, b
    bit.print_dec_uint 16, hi
    stl.output '\\n'
    bit.print_dec_uint 16, lo
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"3\n8\n\0",
    out_bytes=b"8\n3\n",
)

# 0196 sort_three_asc — selection of min, then mid, then max via fold
B(
    "0196",
    "sort_three_asc",
    "Sort Three Asc",
    unsigned=True,
    extra_helpers=[MIN_INTO, MAX_INTO],
    value_data=[
        "a: bit.vec 16, 0",
        "b: bit.vec 16, 0",
        "c: bit.vec 16, 0",
        "lo: bit.vec 16, 0",
        "hi: bit.vec 16, 0",
        "mid: bit.vec 16, 0",
        "sum: bit.vec 16, 0",
    ],
    main_body="""
def main < a, b, c, lo, hi, mid, sum {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    read_decimal 16, c
    min_into 16, lo, a, b
    min_into 16, lo, lo, c
    max_into 16, hi, a, b
    max_into 16, hi, hi, c
    bit.mov 16, sum, a
    bit.add 16, sum, b
    bit.add 16, sum, c
    bit.sub 16, sum, lo
    bit.sub 16, sum, hi
    bit.mov 16, mid, sum
    bit.print_dec_uint 16, lo
    stl.output '\\n'
    bit.print_dec_uint 16, mid
    stl.output '\\n'
    bit.print_dec_uint 16, hi
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"5\n1\n3\n\0",
    out_bytes=b"1\n3\n5\n",
)

# 0197 sort_three_desc
B(
    "0197",
    "sort_three_desc",
    "Sort Three Desc",
    unsigned=True,
    extra_helpers=[MIN_INTO, MAX_INTO],
    value_data=[
        "a: bit.vec 16, 0",
        "b: bit.vec 16, 0",
        "c: bit.vec 16, 0",
        "lo: bit.vec 16, 0",
        "hi: bit.vec 16, 0",
        "mid: bit.vec 16, 0",
        "sum: bit.vec 16, 0",
    ],
    main_body="""
def main < a, b, c, lo, hi, mid, sum {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    read_decimal 16, c
    min_into 16, lo, a, b
    min_into 16, lo, lo, c
    max_into 16, hi, a, b
    max_into 16, hi, hi, c
    bit.mov 16, sum, a
    bit.add 16, sum, b
    bit.add 16, sum, c
    bit.sub 16, sum, lo
    bit.sub 16, sum, hi
    bit.mov 16, mid, sum
    bit.print_dec_uint 16, hi
    stl.output '\\n'
    bit.print_dec_uint 16, mid
    stl.output '\\n'
    bit.print_dec_uint 16, lo
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"5\n1\n3\n\0",
    out_bytes=b"5\n3\n1\n",
)

# ============================================================================
# Threshold classifiers (read one decimal, print a category word)
# ============================================================================

# 0198 classify_age — infant/child/teen/adult/senior
B(
    "0198",
    "classify_age",
    "Classify Age",
    unsigned=True,
    value_data=[
        "age: bit.vec 16, 0",
        "two: bit.vec 16, 2",
        "thirteen: bit.vec 16, 13",
        "twenty: bit.vec 16, 20",
        "sixtyfive: bit.vec 16, 65",
    ],
    main_body="""
def main @ infant, child, teen, adult, senior, done, t13, t20, t65 < age, two, thirteen, twenty, sixtyfive {
    stl.startup
    read_decimal 16, age
    bit.cmp 16, age, two, infant, t13, t13
  t13:
    bit.cmp 16, age, thirteen, child, t20, t20
  t20:
    bit.cmp 16, age, twenty, teen, t65, t65
  t65:
    bit.cmp 16, age, sixtyfive, adult, senior, senior
  infant:
    stl.output "infant\\n"
    ;done
  child:
    stl.output "child\\n"
    ;done
  teen:
    stl.output "teen\\n"
    ;done
  adult:
    stl.output "adult\\n"
    ;done
  senior:
    stl.output "senior\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"15\n\0",
    out_bytes=b"teen\n",
)

# 0199 classify_grade — A/B/C/D/F by score thresholds
B(
    "0199",
    "classify_grade",
    "Classify Grade",
    unsigned=True,
    value_data=[
        "score: bit.vec 16, 0",
        "ninety: bit.vec 16, 90",
        "eighty: bit.vec 16, 80",
        "seventy: bit.vec 16, 70",
        "sixty: bit.vec 16, 60",
    ],
    main_body="""
def main @ ga, gb, gc, gd, gf, done, t80, t70, t60 < score, ninety, eighty, seventy, sixty {
    stl.startup
    read_decimal 16, score
    bit.cmp 16, score, ninety, t80, ga, ga
  t80:
    bit.cmp 16, score, eighty, t70, gb, gb
  t70:
    bit.cmp 16, score, seventy, t60, gc, gc
  t60:
    bit.cmp 16, score, sixty, gf, gd, gd
  ga:
    stl.output "A\\n"
    ;done
  gb:
    stl.output "B\\n"
    ;done
  gc:
    stl.output "C\\n"
    ;done
  gd:
    stl.output "D\\n"
    ;done
  gf:
    stl.output "F\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"83\n\0",
    out_bytes=b"B\n",
)

# 0200 classify_temp_c — signed: freezing/cold/mild/warm/hot
B(
    "0200",
    "classify_temp_c",
    "Classify Temp C",
    signed=True,
    value_data=[
        "t: bit.vec 16, 0",
        "ten: bit.vec 16, 10",
        "twenty: bit.vec 16, 20",
        "thirty: bit.vec 16, 30",
    ],
    main_body="""
def main @ freezing, cold, mild, warm, hot, done, pos, t20, t30 < t, ten, twenty, thirty {
    stl.startup
    read_signed_decimal 16, t
    bit.if0 16, t, freezing
    bit.if1 t + 15*dw, freezing
  pos:
    bit.cmp 16, t, ten, cold, cold, t20
  t20:
    bit.cmp 16, t, twenty, mild, mild, t30
  t30:
    bit.cmp 16, t, thirty, warm, warm, hot
  freezing:
    stl.output "freezing\\n"
    ;done
  cold:
    stl.output "cold\\n"
    ;done
  mild:
    stl.output "mild\\n"
    ;done
  warm:
    stl.output "warm\\n"
    ;done
  hot:
    stl.output "hot\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"-4\n\0",
    out_bytes=b"freezing\n",
)

# 0205 compare_to_10 — less/equal/more
B(
    "0205",
    "compare_to_10",
    "Compare To 10",
    unsigned=True,
    value_data=["a: bit.vec 16, 0", "ten: bit.vec 16, 10"],
    main_body="""
def main @ less, equal, more, done < a, ten {
    stl.startup
    read_decimal 16, a
    bit.cmp 16, a, ten, less, equal, more
  less:
    stl.output "less\\n"
    ;done
  equal:
    stl.output "equal\\n"
    ;done
  more:
    stl.output "more\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"7\n\0",
    out_bytes=b"less\n",
)

# 0206 compare_to_100 — less/equal/more
B(
    "0206",
    "compare_to_100",
    "Compare To 100",
    unsigned=True,
    value_data=["a: bit.vec 16, 0", "hundred: bit.vec 16, 100"],
    main_body="""
def main @ less, equal, more, done < a, hundred {
    stl.startup
    read_decimal 16, a
    bit.cmp 16, a, hundred, less, equal, more
  less:
    stl.output "less\\n"
    ;done
  equal:
    stl.output "equal\\n"
    ;done
  more:
    stl.output "more\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"100\n\0",
    out_bytes=b"equal\n",
)

# 0204 even_or_odd_word — even/odd by bit 0
B(
    "0204",
    "even_or_odd_word",
    "Even Or Odd Word",
    unsigned=True,
    value_data=["a: bit.vec 16, 0"],
    main_body="""
def main @ odd, done < a {
    stl.startup
    read_decimal 16, a
    bit.if1 a, odd
    stl.output "even\\n"
    ;done
  odd:
    stl.output "odd\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"6\n\0",
    out_bytes=b"even\n",
)

# ============================================================================
# Table lookups (value -> fixed name)
# ============================================================================

# 0201 day_of_week_name — 0..6 -> Sunday..Saturday
B(
    "0201",
    "day_of_week_name",
    "Day Of Week Name",
    unsigned=True,
    value_data=[
        "day: bit.vec 16, 0",
        "d0: bit.vec 16, 0",
        "d1: bit.vec 16, 1",
        "d2: bit.vec 16, 2",
        "d3: bit.vec 16, 3",
        "d4: bit.vec 16, 4",
        "d5: bit.vec 16, 5",
    ],
    main_body="""
def main @ sun, mon, tue, wed, thu, fri, sat, done, t1, t2, t3, t4, t5 < day, d0, d1, d2, d3, d4, d5 {
    stl.startup
    read_decimal 16, day
    bit.cmp 16, day, d0, t1, sun, t1
  t1:
    bit.cmp 16, day, d1, t2, mon, t2
  t2:
    bit.cmp 16, day, d2, t3, tue, t3
  t3:
    bit.cmp 16, day, d3, t4, wed, t4
  t4:
    bit.cmp 16, day, d4, t5, thu, t5
  t5:
    bit.cmp 16, day, d5, sat, fri, sat
  sun:
    stl.output "Sunday\\n"
    ;done
  mon:
    stl.output "Monday\\n"
    ;done
  tue:
    stl.output "Tuesday\\n"
    ;done
  wed:
    stl.output "Wednesday\\n"
    ;done
  thu:
    stl.output "Thursday\\n"
    ;done
  fri:
    stl.output "Friday\\n"
    ;done
  sat:
    stl.output "Saturday\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"3\n\0",
    out_bytes=b"Wednesday\n",
)

# 0202 month_name — 1..12 -> January..December
# The `@` clause names all 12 month labels + 10 chained tmp labels; assembled
# from short pieces so no Python source line exceeds the 120-char limit.
_MONTH_HEAD = (
    "\ndef main "
    "@ jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec, done, "
    "t2, t3, t4, t5, t6, t7, t8, t9, t10, t11 "
    "< mo, m1, m2, m3, m4, m5, m6, m7, m8, m9, m10, m11 {"
)
B(
    "0202",
    "month_name",
    "Month Name",
    unsigned=True,
    value_data=[
        "mo: bit.vec 16, 0",
        "m1: bit.vec 16, 1",
        "m2: bit.vec 16, 2",
        "m3: bit.vec 16, 3",
        "m4: bit.vec 16, 4",
        "m5: bit.vec 16, 5",
        "m6: bit.vec 16, 6",
        "m7: bit.vec 16, 7",
        "m8: bit.vec 16, 8",
        "m9: bit.vec 16, 9",
        "m10: bit.vec 16, 10",
        "m11: bit.vec 16, 11",
    ],
    main_body=_MONTH_HEAD + """
    stl.startup
    read_decimal 16, mo
    bit.cmp 16, mo, m1, t2, jan, t2
  t2:
    bit.cmp 16, mo, m2, t3, feb, t3
  t3:
    bit.cmp 16, mo, m3, t4, mar, t4
  t4:
    bit.cmp 16, mo, m4, t5, apr, t5
  t5:
    bit.cmp 16, mo, m5, t6, may, t6
  t6:
    bit.cmp 16, mo, m6, t7, jun, t7
  t7:
    bit.cmp 16, mo, m7, t8, jul, t8
  t8:
    bit.cmp 16, mo, m8, t9, aug, t9
  t9:
    bit.cmp 16, mo, m9, t10, sep, t10
  t10:
    bit.cmp 16, mo, m10, t11, oct, t11
  t11:
    bit.cmp 16, mo, m11, dec, nov, dec
  jan:
    stl.output "January\\n"
    ;done
  feb:
    stl.output "February\\n"
    ;done
  mar:
    stl.output "March\\n"
    ;done
  apr:
    stl.output "April\\n"
    ;done
  may:
    stl.output "May\\n"
    ;done
  jun:
    stl.output "June\\n"
    ;done
  jul:
    stl.output "July\\n"
    ;done
  aug:
    stl.output "August\\n"
    ;done
  sep:
    stl.output "September\\n"
    ;done
  oct:
    stl.output "October\\n"
    ;done
  nov:
    stl.output "November\\n"
    ;done
  dec:
    stl.output "December\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"4\n\0",
    out_bytes=b"April\n",
)

# 0203 season_from_month — winter/spring/summer/fall
B(
    "0203",
    "season_from_month",
    "Season From Month",
    unsigned=True,
    value_data=[
        "mo: bit.vec 16, 0",
        "three: bit.vec 16, 3",
        "six: bit.vec 16, 6",
        "nine: bit.vec 16, 9",
        "twelve: bit.vec 16, 12",
    ],
    main_body="""
def main @ winter, spring, summer, fall, done, t6, t9, t12 < mo, three, six, nine, twelve {
    stl.startup
    read_decimal 16, mo
    bit.cmp 16, mo, three, winter, spring, t6
  t6:
    bit.cmp 16, mo, six, spring, summer, t9
  t9:
    bit.cmp 16, mo, nine, summer, fall, t12
  t12:
    bit.cmp 16, mo, twelve, fall, winter, winter
  winter:
    stl.output "winter\\n"
    ;done
  spring:
    stl.output "spring\\n"
    ;done
  summer:
    stl.output "summer\\n"
    ;done
  fall:
    stl.output "fall\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"4\n\0",
    out_bytes=b"spring\n",
)

# ============================================================================
# Byte classifiers (read exactly one byte; .in has no trailing \0)
# ============================================================================

# 0207 is_alphanumeric_byte
B(
    "0207",
    "is_alphanumeric_byte",
    "Is Alphanumeric Byte",
    extra_helpers=[IN_RANGE_8],
    value_data=[
        "ch: bit.vec 8, 0",
        "d0: bit.vec 8, '0'",
        "d9: bit.vec 8, '9'",
        "ua: bit.vec 8, 'A'",
        "uz: bit.vec 8, 'Z'",
        "la: bit.vec 8, 'a'",
        "lz: bit.vec 8, 'z'",
    ],
    main_body="""
def main @ yes, no, t_upper, t_lower, done < ch, d0, d9, ua, uz, la, lz {
    stl.startup
    bit.input ch
    in_range_8 ch, d0, d9, yes, t_upper
  t_upper:
    in_range_8 ch, ua, uz, yes, t_lower
  t_lower:
    in_range_8 ch, la, lz, yes, no
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"k",
    out_bytes=b"1\n",
)

# 0208 is_punctuation_byte — one of , . ? ! ; : ' -
# ASCII codes given as decimals to avoid escaping the apostrophe in a literal.
# `@`/`<` clause assembled from short pieces to stay under the 120-char limit.
_PUNCT_HEAD = (
    "\ndef main "
    "@ yes, no, done, c2, c3, c4, c5, c6, c7, c8 "
    "< ch, p_comma, p_dot, p_quest, p_bang, p_semi, p_colon, p_apos, p_dash {"
)
B(
    "0208",
    "is_punctuation_byte",
    "Is Punctuation Byte",
    value_data=[
        "ch: bit.vec 8, 0",
        "p_comma: bit.vec 8, 44",
        "p_dot: bit.vec 8, 46",
        "p_quest: bit.vec 8, 63",
        "p_bang: bit.vec 8, 33",
        "p_semi: bit.vec 8, 59",
        "p_colon: bit.vec 8, 58",
        "p_apos: bit.vec 8, 39",
        "p_dash: bit.vec 8, 45",
    ],
    main_body=_PUNCT_HEAD + """
    stl.startup
    bit.input ch
    bit.cmp 8, ch, p_comma, c2, yes, c2
  c2:
    bit.cmp 8, ch, p_dot, c3, yes, c3
  c3:
    bit.cmp 8, ch, p_quest, c4, yes, c4
  c4:
    bit.cmp 8, ch, p_bang, c5, yes, c5
  c5:
    bit.cmp 8, ch, p_semi, c6, yes, c6
  c6:
    bit.cmp 8, ch, p_colon, c7, yes, c7
  c7:
    bit.cmp 8, ch, p_apos, c8, yes, c8
  c8:
    bit.cmp 8, ch, p_dash, no, yes, no
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"!",
    out_bytes=b"1\n",
)

# 0209 is_whitespace_byte — space / tab / newline
B(
    "0209",
    "is_whitespace_byte",
    "Is Whitespace Byte",
    value_data=[
        "ch: bit.vec 8, 0",
        "w_space: bit.vec 8, 0x20",
        "w_tab: bit.vec 8, 0x09",
        "w_nl: bit.vec 8, 0x0A",
    ],
    main_body="""
def main @ yes, no, done, c2, c3 < ch, w_space, w_tab, w_nl {
    stl.startup
    bit.input ch
    bit.cmp 8, ch, w_space, c2, yes, c2
  c2:
    bit.cmp 8, ch, w_tab, c3, yes, c3
  c3:
    bit.cmp 8, ch, w_nl, no, yes, no
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"\t",
    out_bytes=b"1\n",
)

# 0210 char_class — digit / upper / lower / other
B(
    "0210",
    "char_class",
    "Char Class",
    extra_helpers=[IN_RANGE_8],
    value_data=[
        "ch: bit.vec 8, 0",
        "d0: bit.vec 8, '0'",
        "d9: bit.vec 8, '9'",
        "ua: bit.vec 8, 'A'",
        "uz: bit.vec 8, 'Z'",
        "la: bit.vec 8, 'a'",
        "lz: bit.vec 8, 'z'",
    ],
    main_body="""
def main @ digit, upper, lower, other, done, t_upper, t_lower < ch, d0, d9, ua, uz, la, lz {
    stl.startup
    bit.input ch
    in_range_8 ch, d0, d9, digit, t_upper
  t_upper:
    in_range_8 ch, ua, uz, upper, t_lower
  t_lower:
    in_range_8 ch, la, lz, lower, other
  digit:
    stl.output "digit\\n"
    ;done
  upper:
    stl.output "upper\\n"
    ;done
  lower:
    stl.output "lower\\n"
    ;done
  other:
    stl.output "other\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"7",
    out_bytes=b"digit\n",
)

# ============================================================================
# Selectors (a leading ASCII bit chooses between two behaviors)
# ============================================================================

# 0214 min_or_max_select — bit + \n, then two decimals; bit 0 -> min, 1 -> max
B(
    "0214",
    "min_or_max_select",
    "Min Or Max Select",
    unsigned=True,
    extra_helpers=[MIN_INTO, MAX_INTO],
    value_data=[
        "selbit: bit.vec 8, 0",
        "nlch: bit.vec 8, 0",
        "a: bit.vec 16, 0",
        "b: bit.vec 16, 0",
        "res: bit.vec 16, 0",
    ],
    main_body="""
def main @ want_max, emit, done < selbit, nlch, a, b, res {
    stl.startup
    bit.input selbit
    bit.input nlch
    read_decimal 16, a
    read_decimal 16, b
    bit.if1 selbit, want_max
    min_into 16, res, a, b
    ;emit
  want_max:
    max_into 16, res, a, b
  emit:
    bit.print_dec_uint 16, res
    stl.output '\\n'
  done:
    stl.loop
}
""",
    in_bytes=b"1\n10\n40\n\0",
    out_bytes=b"40\n",
)

# 0215 abs_or_negate_select — bit, then signed decimal; bit 0 -> abs, 1 -> negate
B(
    "0215",
    "abs_or_negate_select",
    "Abs Or Negate Select",
    signed=True,
    value_data=["selbit: bit.vec 8, 0", "a: bit.vec 16, 0"],
    main_body="""
def main @ want_neg, emit, done, take_abs < selbit, a {
    stl.startup
    bit.input selbit
    read_signed_decimal 16, a
    bit.if1 selbit, want_neg
  take_abs:
    bit.if0 a + 15*dw, emit
    bit.neg 16, a
    ;emit
  want_neg:
    bit.neg 16, a
  emit:
    bit.print_dec_int 16, a
    stl.output '\\n'
  done:
    stl.loop
}
""",
    in_bytes=b"15\n\0",
    out_bytes=b"-5\n",
)

# 0216 upper_or_lower_select — bit, then one byte; bit 0 -> uppercase, 1 -> lowercase
B(
    "0216",
    "upper_or_lower_select",
    "Upper Or Lower Select",
    extra_helpers=[IN_RANGE_8, TO_UPPER_BYTE, TO_LOWER_BYTE],
    value_data=[
        "selbit: bit.vec 8, 0",
        "ch: bit.vec 8, 0",
        "ua: bit.vec 8, 'A'",
        "uz: bit.vec 8, 'Z'",
        "la: bit.vec 8, 'a'",
        "lz: bit.vec 8, 'z'",
    ],
    main_body="""
def main @ want_lower, done < selbit, ch {
    stl.startup
    bit.input selbit
    bit.input ch
    bit.if1 selbit, want_lower
    to_upper_byte ch
    bit.print ch
    ;done
  want_lower:
    to_lower_byte ch
    bit.print ch
  done:
    stl.loop
}
""",
    in_bytes=b"0a",
    out_bytes=b"A",
)

# 0217 switch_on_digit — digit 0..9 -> letter a..j
B(
    "0217",
    "switch_on_digit",
    "Switch On Digit",
    value_data=["ch: bit.vec 8, 0", "zero: bit.vec 8, '0'", "lett_a: bit.vec 8, 'a'"],
    main_body="""
def main < ch, zero, lett_a {
    stl.startup
    bit.input ch
    bit.sub 8, ch, zero
    bit.add 8, ch, lett_a
    bit.print ch
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"5",
    out_bytes=b"f\n",
)

# ============================================================================
# Range / membership / ordering checks
# ============================================================================

# 0211 weekday_or_weekend — day 0..6 (Sun=0); Sat/Sun -> weekend
B(
    "0211",
    "weekday_or_weekend",
    "Weekday Or Weekend",
    unsigned=True,
    value_data=["day: bit.vec 16, 0", "d0: bit.vec 16, 0", "d6: bit.vec 16, 6"],
    main_body="""
def main @ weekend, weekday, done, check6 < day, d0, d6 {
    stl.startup
    read_decimal 16, day
    bit.cmp 16, day, d0, check6, weekend, check6
  check6:
    bit.cmp 16, day, d6, weekday, weekend, weekday
  weekday:
    stl.output "weekday\\n"
    ;done
  weekend:
    stl.output "weekend\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"6\n\0",
    out_bytes=b"weekend\n",
)

# 0212 is_business_hour — print 1 if 9 <= h <= 17 else 0
B(
    "0212",
    "is_business_hour",
    "Is Business Hour",
    unsigned=True,
    value_data=["h: bit.vec 16, 0", "nine: bit.vec 16, 9", "seventeen: bit.vec 16, 17"],
    main_body="""
def main @ yes, no, done, check_hi < h, nine, seventeen {
    stl.startup
    read_decimal 16, h
    bit.cmp 16, h, nine, no, check_hi, check_hi
  check_hi:
    bit.cmp 16, h, seventeen, yes, yes, no
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"14\n\0",
    out_bytes=b"1\n",
)

# 0224 compare_with_window — below / in / above
B(
    "0224",
    "compare_with_window",
    "Compare With Window",
    unsigned=True,
    value_data=["a: bit.vec 16, 0", "lo: bit.vec 16, 0", "hi: bit.vec 16, 0"],
    main_body="""
def main @ below, in_win, above, done, check_hi < a, lo, hi {
    stl.startup
    read_decimal 16, a
    read_decimal 16, lo
    read_decimal 16, hi
    bit.cmp 16, a, lo, below, check_hi, check_hi
  check_hi:
    bit.cmp 16, a, hi, in_win, in_win, above
  below:
    stl.output "below\\n"
    ;done
  in_win:
    stl.output "in\\n"
    ;done
  above:
    stl.output "above\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"5\n1\n9\n\0",
    out_bytes=b"in\n",
)

# 0225 sorted_check_three — non-decreasing -> 1 else 0
B(
    "0225",
    "sorted_check_three",
    "Sorted Check Three",
    unsigned=True,
    value_data=["a: bit.vec 16, 0", "b: bit.vec 16, 0", "c: bit.vec 16, 0"],
    main_body="""
def main @ yes, no, done, ok1 < a, b, c {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    read_decimal 16, c
    bit.cmp 16, a, b, ok1, ok1, no
  ok1:
    bit.cmp 16, b, c, yes, yes, no
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"1\n3\n3\n\0",
    out_bytes=b"1\n",
)

# 0226 sorted_check_four — non-decreasing -> 1 else 0
B(
    "0226",
    "sorted_check_four",
    "Sorted Check Four",
    unsigned=True,
    value_data=["a: bit.vec 16, 0", "b: bit.vec 16, 0", "c: bit.vec 16, 0", "d: bit.vec 16, 0"],
    main_body="""
def main @ yes, no, done, ok1, ok2 < a, b, c, d {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    read_decimal 16, c
    read_decimal 16, d
    bit.cmp 16, a, b, ok1, ok1, no
  ok1:
    bit.cmp 16, b, c, ok2, ok2, no
  ok2:
    bit.cmp 16, c, d, yes, yes, no
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"1\n2\n2\n5\n\0",
    out_bytes=b"1\n",
)

# 0223 any_zero_three — print 1 if any input is 0 else 0
B(
    "0223",
    "any_zero_three",
    "Any Zero Three",
    unsigned=True,
    value_data=["a: bit.vec 16, 0", "b: bit.vec 16, 0", "c: bit.vec 16, 0"],
    main_body="""
def main @ yes, no, done < a, b, c {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    read_decimal 16, c
    bit.if0 16, a, yes
    bit.if0 16, b, yes
    bit.if0 16, c, yes
    ;no
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"4\n0\n9\n\0",
    out_bytes=b"1\n",
)

# 0222 all_positive_three — signed; print 1 if all > 0 else 0
B(
    "0222",
    "all_positive_three",
    "All Positive Three",
    signed=True,
    value_data=["a: bit.vec 16, 0", "b: bit.vec 16, 0", "c: bit.vec 16, 0"],
    main_body="""
def main @ yes, no, done < a, b, c {
    stl.startup
    read_signed_decimal 16, a
    read_signed_decimal 16, b
    read_signed_decimal 16, c
    bit.if0 16, a, no
    bit.if1 a + 15*dw, no
    bit.if0 16, b, no
    bit.if1 b + 15*dw, no
    bit.if0 16, c, no
    bit.if1 c + 15*dw, no
    ;yes
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"3\n7\n1\n\0",
    out_bytes=b"1\n",
)

# 0221 parity_three — all even / all odd / mixed
B(
    "0221",
    "parity_three",
    "Parity Three",
    unsigned=True,
    value_data=["a: bit.vec 16, 0", "b: bit.vec 16, 0", "c: bit.vec 16, 0"],
    main_body="""
def main @ all_even, all_odd, mixed, done, a_odd < a, b, c {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    read_decimal 16, c
    bit.if1 a, a_odd
    bit.if1 b, mixed
    bit.if1 c, mixed
    ;all_even
  a_odd:
    bit.if0 b, mixed
    bit.if0 c, mixed
    ;all_odd
  all_even:
    stl.output "all even\\n"
    ;done
  all_odd:
    stl.output "all odd\\n"
    ;done
  mixed:
    stl.output "mixed\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"2\n4\n6\n\0",
    out_bytes=b"all even\n",
)

# ============================================================================
# Modular / sign / table branches
# ============================================================================

# 0213 fizzbuzz_classify_one — fizz / buzz / fizzbuzz / <N>
B(
    "0213",
    "fizzbuzz_classify_one",
    "Fizzbuzz Classify One",
    unsigned=True,
    value_data=[
        "x: bit.vec 16, 0",
        "three: bit.vec 16, 3",
        "five: bit.vec 16, 5",
        "q: bit.vec 16, 0",
        "r3: bit.vec 16, 0",
        "r5: bit.vec 16, 0",
    ],
    main_body="""
def main @ both, only3, only5, plain, done, chk_buzz < x, three, five, q, r3, r5 {
    stl.startup
    read_decimal 16, x
    bit.div 16, x, three, q, r3
    bit.div 16, x, five, q, r5
    bit.if1 16, r3, chk_buzz
    bit.if0 16, r5, both
    ;only3
  chk_buzz:
    bit.if0 16, r5, only5
  plain:
    bit.print_dec_uint 16, x
    stl.output '\\n'
    ;done
  only3:
    stl.output "fizz\\n"
    ;done
  only5:
    stl.output "buzz\\n"
    ;done
  both:
    stl.output "fizzbuzz\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"15\n\0",
    out_bytes=b"fizzbuzz\n",
)

# 0219 quadrant_2d — signed x,y -> 1/2/3/4 or axis
B(
    "0219",
    "quadrant_2d",
    "Quadrant 2d",
    signed=True,
    value_data=["x: bit.vec 16, 0", "y: bit.vec 16, 0"],
    main_body="""
def main @ q1, q2, q3, q4, axis, done, x_neg, x_pos_y < x, y {
    stl.startup
    read_signed_decimal 16, x
    read_signed_decimal 16, y
    bit.if0 16, x, axis
    bit.if0 16, y, axis
    bit.if1 x + 15*dw, x_neg
  x_pos_y:
    bit.if1 y + 15*dw, q4
    ;q1
  x_neg:
    bit.if1 y + 15*dw, q3
    ;q2
  q1:
    stl.output "1\\n"
    ;done
  q2:
    stl.output "2\\n"
    ;done
  q3:
    stl.output "3\\n"
    ;done
  q4:
    stl.output "4\\n"
    ;done
  axis:
    stl.output "axis\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"-3\n5\n\0",
    out_bytes=b"2\n",
)

# 0227 rps_winner — two bytes (each + \n): r/p/s; print 1 / 2 / tie
# `@`/`<` clause assembled from short pieces to stay under the 120-char limit.
_RPS_HEAD = (
    "\ndef main "
    "@ p1_wins, p2_wins, tie, done, not_tie, try_paper, p1_rock, p1_paper, p1_sciss "
    "< p1, p2, nlch, rock, paper, scissors {"
)
B(
    "0227",
    "rps_winner",
    "Rps Winner",
    value_data=[
        "p1: bit.vec 8, 0",
        "p2: bit.vec 8, 0",
        "nlch: bit.vec 8, 0",
        "rock: bit.vec 8, 'r'",
        "paper: bit.vec 8, 'p'",
        "scissors: bit.vec 8, 's'",
    ],
    main_body=_RPS_HEAD + """
    stl.startup
    bit.input p1
    bit.input nlch
    bit.input p2
    bit.input nlch
    bit.cmp 8, p1, p2, not_tie, tie, not_tie
  not_tie:
    bit.cmp 8, p1, rock, try_paper, p1_rock, try_paper
  try_paper:
    bit.cmp 8, p1, paper, p1_sciss, p1_paper, p1_sciss
  p1_rock:
    bit.cmp 8, p2, scissors, p2_wins, p1_wins, p2_wins
  p1_paper:
    bit.cmp 8, p2, rock, p2_wins, p1_wins, p2_wins
  p1_sciss:
    bit.cmp 8, p2, paper, p2_wins, p1_wins, p2_wins
  p1_wins:
    stl.output "1\\n"
    ;done
  p2_wins:
    stl.output "2\\n"
    ;done
  tie:
    stl.output "tie\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"r\np\n",
    out_bytes=b"2\n",
)

# 0228 leap_year_check — (y%4==0 && y%100!=0) || y%400==0
B(
    "0228",
    "leap_year_check",
    "Leap Year Check",
    unsigned=True,
    value_data=[
        "y: bit.vec 16, 0",
        "four: bit.vec 16, 4",
        "hundred: bit.vec 16, 100",
        "fourhundred: bit.vec 16, 400",
        "q: bit.vec 16, 0",
        "r: bit.vec 16, 0",
    ],
    main_body="""
def main @ yes, no, done, chk100, chk400 < y, four, hundred, fourhundred, q, r {
    stl.startup
    read_decimal 16, y
    bit.div 16, y, four, q, r
    bit.if1 16, r, chk400
  chk100:
    bit.div 16, y, hundred, q, r
    bit.if1 16, r, yes
  chk400:
    bit.div 16, y, fourhundred, q, r
    bit.if0 16, r, yes
    ;no
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"2000\n\0",
    out_bytes=b"1\n",
)

# ============================================================================
# Multi-comparison shape / ordering branches
# ============================================================================

# 0218 triangle_classify — equilateral / isosceles / scalene / not
B(
    "0218",
    "triangle_classify",
    "Triangle Classify",
    unsigned=True,
    value_data=["a: bit.vec 16, 0", "b: bit.vec 16, 0", "c: bit.vec 16, 0", "sum: bit.vec 16, 0"],
    main_body="""
def main @ equilateral, isosceles, scalene, not_tri, done, ti2, ti3, shape, ab_eq, not_ab, ac_check < a, b, c, sum {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    read_decimal 16, c
    bit.mov 16, sum, a
    bit.add 16, sum, b
    bit.cmp 16, sum, c, not_tri, not_tri, ti2
  ti2:
    bit.mov 16, sum, a
    bit.add 16, sum, c
    bit.cmp 16, sum, b, not_tri, not_tri, ti3
  ti3:
    bit.mov 16, sum, b
    bit.add 16, sum, c
    bit.cmp 16, sum, a, not_tri, not_tri, shape
  shape:
    bit.cmp 16, a, b, not_ab, ab_eq, not_ab
  ab_eq:
    bit.cmp 16, b, c, isosceles, equilateral, isosceles
  not_ab:
    bit.cmp 16, b, c, ac_check, isosceles, ac_check
  ac_check:
    bit.cmp 16, a, c, scalene, isosceles, scalene
  equilateral:
    stl.output "equilateral\\n"
    ;done
  isosceles:
    stl.output "isosceles\\n"
    ;done
  scalene:
    stl.output "scalene\\n"
    ;done
  not_tri:
    stl.output "not\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"5\n5\n8\n\0",
    out_bytes=b"isosceles\n",
)

# 0220 compare_three_order — ascending order of labels a,b,c (ties: alphabetical)
B(
    "0220",
    "compare_three_order",
    "Compare Three Order",
    unsigned=True,
    value_data=["a: bit.vec 16, 0", "b: bit.vec 16, 0", "c: bit.vec 16, 0"],
    main_body="""
def main @ abc, acb, bac, bca, cab, cba, done, a_le_b, b_lt_a, l1, r1 < a, b, c {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    read_decimal 16, c
    bit.cmp 16, a, b, a_le_b, a_le_b, b_lt_a
  a_le_b:
    bit.cmp 16, b, c, abc, abc, l1
  l1:
    bit.cmp 16, a, c, acb, acb, cab
  b_lt_a:
    bit.cmp 16, b, c, r1, r1, cba
  r1:
    bit.cmp 16, a, c, bac, bac, bca
  abc:
    stl.output "abc\\n"
    ;done
  acb:
    stl.output "acb\\n"
    ;done
  bac:
    stl.output "bac\\n"
    ;done
  bca:
    stl.output "bca\\n"
    ;done
  cab:
    stl.output "cab\\n"
    ;done
  cba:
    stl.output "cba\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"3\n1\n2\n\0",
    out_bytes=b"bca\n",
)

# ============================================================================
# Wide-arithmetic branch
# ============================================================================

# 0229 bmi_category — BMI = weight*10000/(height*height); under/normal/over/obese
# Inputs read as 16-bit decimals (both <= 250), zero-extended into 32-bit vecs
# so weight*10000 (up to 2,000,000) and height*height (up to 62,500) don't
# overflow. mul32_into multiplies by repeated addition; both loops run < 251x.
# `@`/`<` clause assembled from short pieces to stay under the 120-char limit.
_BMI_HEAD = (
    "\ndef main "
    "@ under, normal, over, obese, done, t25, t30 "
    "< w16, h16, weight, height, tenk, num, denom, bmi, rem, c18, c25, c30 {"
)
B(
    "0229",
    "bmi_category",
    "Bmi Category",
    unsigned=True,
    extra_helpers=[MUL32_INTO],
    value_data=[
        "w16: bit.vec 16, 0",
        "h16: bit.vec 16, 0",
        "weight: bit.vec 32, 0",
        "height: bit.vec 32, 0",
        "tenk: bit.vec 32, 10000",
        "num: bit.vec 32, 0",
        "denom: bit.vec 32, 0",
        "bmi: bit.vec 32, 0",
        "rem: bit.vec 32, 0",
        "c18: bit.vec 32, 18",
        "c25: bit.vec 32, 25",
        "c30: bit.vec 32, 30",
    ],
    extra_data=["mul32_counter: bit.vec 32, 0"],
    main_body=_BMI_HEAD + """
    stl.startup
    read_decimal 16, w16
    read_decimal 16, h16
    bit.zero 32, weight
    bit.zero 32, height
    bit.mov 16, weight, w16
    bit.mov 16, height, h16
    mul32_into num, tenk, weight
    mul32_into denom, height, height
    bit.div 32, num, denom, bmi, rem
    bit.cmp 32, bmi, c18, under, t25, t25
  t25:
    bit.cmp 32, bmi, c25, normal, t30, t30
  t30:
    bit.cmp 32, bmi, c30, over, obese, obese
  under:
    stl.output "under\\n"
    ;done
  normal:
    stl.output "normal\\n"
    ;done
  over:
    stl.output "over\\n"
    ;done
  obese:
    stl.output "obese\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"70\n170\n\0",
    out_bytes=b"normal\n",
)

print("---")
print("CAT BRANCHING DONE")

"""Phase 3 batch 9: strings — line counts, case transforms, Caesar, all-checks.

17 streaming line programs (read a \\n-terminated line char by char; no buffer).
Buffer-needing string programs (palindrome, repeat_line) and positional ones
(first/last char, substrings, char_at_index) are later batches.

Run from the repo root:  python scripts/batch09_strings.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog_arith import emit  # noqa: E402

# ---------------------------- shared helpers ----------------------------

IN_RANGE = """
// Jump to `yes` if lo <= ch <= hi (lo, hi are bit[:8] bounds), else to `no`.
def in_range ch, lo, hi, yes, no @ check_hi {
    bit.cmp 8, ch, lo, no, yes, check_hi
  check_hi:
    bit.cmp 8, ch, hi, yes, yes, no
}
""".strip()

IS_LETTER = """
// Jump to `yes` if ch is a letter (A-Z or a-z), else to `no`.
def is_letter ch, yes, no @ try_lower < upper_a, upper_z, lower_a, lower_z {
    in_range ch, upper_a, upper_z, yes, try_lower
  try_lower:
    in_range ch, lower_a, lower_z, yes, no
}
""".strip()

IS_VOWEL = """
// Jump to `yes` if ch is a/e/i/o/u in either case, else to `no`.
def is_vowel ch, yes, no @ t1, t2, t3, t4, t5, t6, t7, t8, t9 \\
        < va, ve, vi, vo, vu, vA, vE, vI, vO, vU {
    bit.cmp 8, ch, va, t1, yes, t1
  t1:
    bit.cmp 8, ch, ve, t2, yes, t2
  t2:
    bit.cmp 8, ch, vi, t3, yes, t3
  t3:
    bit.cmp 8, ch, vo, t4, yes, t4
  t4:
    bit.cmp 8, ch, vu, t5, yes, t5
  t5:
    bit.cmp 8, ch, vA, t6, yes, t6
  t6:
    bit.cmp 8, ch, vE, t7, yes, t7
  t7:
    bit.cmp 8, ch, vI, t8, yes, t8
  t8:
    bit.cmp 8, ch, vO, t9, yes, t9
  t9:
    bit.cmp 8, ch, vU, no, yes, no
}
""".strip()

CAESAR = """
// Caesar-shift ch forward by k within its own case; non-letters unchanged.
def caesar_shift ch, k @ try_lower, up, low, done < upper_a, upper_z, lower_a, lower_z {
    in_range ch, upper_a, upper_z, up, try_lower
  try_lower:
    in_range ch, lower_a, lower_z, low, done
  up:
    shift_within ch, k, upper_a
    ;done
  low:
    shift_within ch, k, lower_a
  done:
}

// ch = (ch - base + k) mod 26 + base, assuming base <= ch <= base+25 and k < 26.
def shift_within ch, k, base @ sub, nowrap < c26 {
    bit.sub 8, ch, base
    bit.add 8, ch, k
    bit.cmp 8, ch, c26, nowrap, sub, sub
  sub:
    bit.sub 8, ch, c26
  nowrap:
    bit.add 8, ch, base
}
""".strip()

D_RANGE = ["upper_a: bit.vec 8, 'A'", "upper_z: bit.vec 8, 'Z'", "lower_a: bit.vec 8, 'a'", "lower_z: bit.vec 8, 'z'"]
D_VOWEL = [
    "va: bit.vec 8, 'a'",
    "ve: bit.vec 8, 'e'",
    "vi: bit.vec 8, 'i'",
    "vo: bit.vec 8, 'o'",
    "vu: bit.vec 8, 'u'",
    "vA: bit.vec 8, 'A'",
    "vE: bit.vec 8, 'E'",
    "vI: bit.vec 8, 'I'",
    "vO: bit.vec 8, 'O'",
    "vU: bit.vec 8, 'U'",
]
D_NL = ["ch: bit.vec 8, 0", "nl: bit.vec 8, '\\n'"]
D_COUNT = ["count: bit.vec 16, 0"]


def S(nnnn, slug, name, **kw):
    emit("strings", nnnn, slug, name, **kw)


# ======================= counts (predicate + counter) =======================

# 0166 string_length
S(
    "0166",
    "string_length",
    "String Length",
    value_data=D_NL + D_COUNT,
    main_body="""
def main @ loop, body, end < ch, nl, count {
    stl.startup
    bit.zero 16, count
  loop:
    bit.input ch
    bit.if0 8, ch, end
    bit.cmp 8, ch, nl, body, end, body
  body:
    bit.inc 16, count
    ;loop
  end:
    bit.print_dec_uint 16, count
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"hello\n\0",
    out_bytes=b"5\n",
)

# 0168 count_vowels
S(
    "0168",
    "count_vowels",
    "Count Vowels",
    extra_helpers=[IS_VOWEL],
    value_data=D_NL + D_COUNT,
    extra_data=D_VOWEL,
    main_body="""
def main @ loop, body, hit, skip, end < ch, nl, count {
    stl.startup
    bit.zero 16, count
  loop:
    bit.input ch
    bit.if0 8, ch, end
    bit.cmp 8, ch, nl, body, end, body
  body:
    is_vowel ch, hit, skip
  hit:
    bit.inc 16, count
  skip:
    ;loop
  end:
    bit.print_dec_uint 16, count
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"hello world\n\0",
    out_bytes=b"3\n",
)

# 0169 count_consonants — letters that are not vowels
S(
    "0169",
    "count_consonants",
    "Count Consonants",
    extra_helpers=[IN_RANGE, IS_LETTER, IS_VOWEL],
    value_data=D_NL + D_COUNT,
    extra_data=D_RANGE + D_VOWEL,
    main_body="""
def main @ loop, body, chk_vowel, hit, skip, end < ch, nl, count {
    stl.startup
    bit.zero 16, count
  loop:
    bit.input ch
    bit.if0 8, ch, end
    bit.cmp 8, ch, nl, body, end, body
  body:
    is_letter ch, chk_vowel, skip
  chk_vowel:
    is_vowel ch, skip, hit
  hit:
    bit.inc 16, count
  skip:
    ;loop
  end:
    bit.print_dec_uint 16, count
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"hello world\n\0",
    out_bytes=b"7\n",
)

# 0170 count_letters
S(
    "0170",
    "count_letters",
    "Count Letters",
    extra_helpers=[IN_RANGE, IS_LETTER],
    value_data=D_NL + D_COUNT,
    extra_data=D_RANGE,
    main_body="""
def main @ loop, body, hit, skip, end < ch, nl, count {
    stl.startup
    bit.zero 16, count
  loop:
    bit.input ch
    bit.if0 8, ch, end
    bit.cmp 8, ch, nl, body, end, body
  body:
    is_letter ch, hit, skip
  hit:
    bit.inc 16, count
  skip:
    ;loop
  end:
    bit.print_dec_uint 16, count
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"ab, cd!\n\0",
    out_bytes=b"4\n",
)

# 0171 count_uppercase_letters
S(
    "0171",
    "count_uppercase_letters",
    "Count Uppercase Letters",
    extra_helpers=[IN_RANGE],
    value_data=D_NL + D_COUNT,
    extra_data=["upper_a: bit.vec 8, 'A'", "upper_z: bit.vec 8, 'Z'"],
    main_body="""
def main @ loop, body, hit, skip, end < ch, nl, count, upper_a, upper_z {
    stl.startup
    bit.zero 16, count
  loop:
    bit.input ch
    bit.if0 8, ch, end
    bit.cmp 8, ch, nl, body, end, body
  body:
    in_range ch, upper_a, upper_z, hit, skip
  hit:
    bit.inc 16, count
  skip:
    ;loop
  end:
    bit.print_dec_uint 16, count
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"Hello World\n\0",
    out_bytes=b"2\n",
)

# 0172 count_lowercase_letters
S(
    "0172",
    "count_lowercase_letters",
    "Count Lowercase Letters",
    extra_helpers=[IN_RANGE],
    value_data=D_NL + D_COUNT,
    extra_data=["lower_a: bit.vec 8, 'a'", "lower_z: bit.vec 8, 'z'"],
    main_body="""
def main @ loop, body, hit, skip, end < ch, nl, count, lower_a, lower_z {
    stl.startup
    bit.zero 16, count
  loop:
    bit.input ch
    bit.if0 8, ch, end
    bit.cmp 8, ch, nl, body, end, body
  body:
    in_range ch, lower_a, lower_z, hit, skip
  hit:
    bit.inc 16, count
  skip:
    ;loop
  end:
    bit.print_dec_uint 16, count
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"Hello World\n\0",
    out_bytes=b"8\n",
)

# 0193 count_letter_e
S(
    "0193",
    "count_letter_e",
    "Count Letter E",
    value_data=D_NL + D_COUNT + ["e_lower: bit.vec 8, 'e'", "e_upper: bit.vec 8, 'E'"],
    main_body="""
def main @ loop, body, chk_up, hit, skip, end < ch, nl, count, e_lower, e_upper {
    stl.startup
    bit.zero 16, count
  loop:
    bit.input ch
    bit.if0 8, ch, end
    bit.cmp 8, ch, nl, body, end, body
  body:
    bit.cmp 8, ch, e_lower, chk_up, hit, chk_up
  chk_up:
    bit.cmp 8, ch, e_upper, skip, hit, skip
  hit:
    bit.inc 16, count
  skip:
    ;loop
  end:
    bit.print_dec_uint 16, count
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"Eee free\n\0",
    out_bytes=b"5\n",
)


# ===================== case transforms (per char, echo) =====================

# 0180 uppercase_line — a-z -> A-Z (toggle bit 5)
S(
    "0180",
    "uppercase_line",
    "Uppercase Line",
    extra_helpers=[IN_RANGE],
    value_data=D_NL,
    extra_data=["lower_a: bit.vec 8, 'a'", "lower_z: bit.vec 8, 'z'"],
    main_body="""
def main @ loop, body, shift, emit_ch, end < ch, nl, lower_a, lower_z {
    stl.startup
  loop:
    bit.input ch
    bit.if0 8, ch, end
    bit.cmp 8, ch, nl, body, end, body
  body:
    in_range ch, lower_a, lower_z, shift, emit_ch
  shift:
    bit.not ch + 5*dw
  emit_ch:
    bit.print ch
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"Hello, World!\n\0",
    out_bytes=b"HELLO, WORLD!\n",
)

# 0181 lowercase_line — A-Z -> a-z (toggle bit 5)
S(
    "0181",
    "lowercase_line",
    "Lowercase Line",
    extra_helpers=[IN_RANGE],
    value_data=D_NL,
    extra_data=["upper_a: bit.vec 8, 'A'", "upper_z: bit.vec 8, 'Z'"],
    main_body="""
def main @ loop, body, shift, emit_ch, end < ch, nl, upper_a, upper_z {
    stl.startup
  loop:
    bit.input ch
    bit.if0 8, ch, end
    bit.cmp 8, ch, nl, body, end, body
  body:
    in_range ch, upper_a, upper_z, shift, emit_ch
  shift:
    bit.not ch + 5*dw
  emit_ch:
    bit.print ch
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"Hello, World!\n\0",
    out_bytes=b"hello, world!\n",
)

# 0182 swap_case_line — letters toggle case
S(
    "0182",
    "swap_case_line",
    "Swap Case Line",
    extra_helpers=[IN_RANGE, IS_LETTER],
    value_data=D_NL,
    extra_data=D_RANGE,
    main_body="""
def main @ loop, body, shift, emit_ch, end < ch, nl {
    stl.startup
  loop:
    bit.input ch
    bit.if0 8, ch, end
    bit.cmp 8, ch, nl, body, end, body
  body:
    is_letter ch, shift, emit_ch
  shift:
    bit.not ch + 5*dw
  emit_ch:
    bit.print ch
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"Hello, World!\n\0",
    out_bytes=b"hELLO, wORLD!\n",
)


# ============================ Caesar ciphers ============================


def caesar(nnnn, slug, name, k, in_bytes, out_bytes):
    S(
        nnnn,
        slug,
        name,
        extra_helpers=[IN_RANGE, CAESAR],
        value_data=D_NL + [f"k: bit.vec 8, {k}"],
        extra_data=D_RANGE + ["c26: bit.vec 8, 26"],
        main_body="""
def main @ loop, body, end < ch, nl, k {
    stl.startup
  loop:
    bit.input ch
    bit.if0 8, ch, end
    bit.cmp 8, ch, nl, body, end, body
  body:
    caesar_shift ch, k
    bit.print ch
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
        in_bytes=in_bytes,
        out_bytes=out_bytes,
    )


caesar("0177", "caesar_plus_1", "Caesar Plus 1", 1, b"Hello, zZ!\n\0", b"Ifmmp, aA!\n")
caesar("0178", "caesar_plus_3", "Caesar Plus 3", 3, b"abc XYZ!\n\0", b"def ABC!\n")
caesar("0179", "caesar_plus_13", "Caesar Plus 13", 13, b"Hello\n\0", b"Uryyb\n")


# ===================== all-bytes checks (early-exit) =====================


def all_check(nnnn, slug, name, helper, helper_data, body_call, in_bytes, out_bytes, main_refs=""):
    S(
        nnnn,
        slug,
        name,
        extra_helpers=helper,
        value_data=D_NL,
        extra_data=helper_data,
        main_body=f"""
def main @ loop, body, ok, fail, all_pass < ch, nl{main_refs} {{
    stl.startup
  loop:
    bit.input ch
    bit.if0 8, ch, all_pass
    bit.cmp 8, ch, nl, body, all_pass, body
  body:
    {body_call}
  ok:
    ;loop
  fail:
    stl.output "0\\n"
    stl.loop
  all_pass:
    stl.output "1\\n"
    stl.loop
}}
""",
        in_bytes=in_bytes,
        out_bytes=out_bytes,
    )


# 0186 is_all_uppercase
all_check(
    "0186",
    "is_all_uppercase",
    "Is All Uppercase",
    [IN_RANGE],
    ["upper_a: bit.vec 8, 'A'", "upper_z: bit.vec 8, 'Z'"],
    "in_range ch, upper_a, upper_z, ok, fail",
    b"ABC\n\0",
    b"1\n",
    main_refs=", upper_a, upper_z",
)

# 0187 is_all_lowercase
all_check(
    "0187",
    "is_all_lowercase",
    "Is All Lowercase",
    [IN_RANGE],
    ["lower_a: bit.vec 8, 'a'", "lower_z: bit.vec 8, 'z'"],
    "in_range ch, lower_a, lower_z, ok, fail",
    b"abc\n\0",
    b"1\n",
    main_refs=", lower_a, lower_z",
)

# 0188 is_all_digits
all_check(
    "0188",
    "is_all_digits",
    "Is All Digits",
    [IN_RANGE],
    ["digit_0: bit.vec 8, '0'", "digit_9: bit.vec 8, '9'"],
    "in_range ch, digit_0, digit_9, ok, fail",
    b"12345\n\0",
    b"1\n",
    main_refs=", digit_0, digit_9",
)

# 0189 is_all_letters (is_letter is a helper, so no direct bound refs in main)
all_check(
    "0189",
    "is_all_letters",
    "Is All Letters",
    [IN_RANGE, IS_LETTER],
    D_RANGE,
    "is_letter ch, ok, fail",
    b"abcXYZ\n\0",
    b"1\n",
)

print("---")
print("BATCH 9 DONE")

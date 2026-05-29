"""Phase 3 category: text_processing — single-pass streaming word/line stats.

8 streaming programs (read a line/stream char by char with small fixed state,
no full-text buffer): word_count_multiline, word_length_avg, word_length_max,
word_length_min, period_sentence_count, capitalize_first_letter,
capitalize_words, uncapitalize_first.

The other 12 text_processing rows all need the whole text (or a whole word)
buffered — char_freq_table (256-entry histogram), longest_word/shortest_word/
word_with_most_vowels (store + reprint a word), count_word_occurrences (store
the target word), reverse_words_in_line (buffer the line), count_unique_words
(set of seen words), longest_common_prefix/suffix_two (buffer a line),
line_starts_with/ends_with_substring + count_substring_occurrences (buffer the
pattern). They are left APPROVED (deferred) per the buffer/array/pointer rule.

Run from the repo root:  python scripts/cat_text_processing.py
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

# space (0x20) or tab (0x09); newline is handled separately by callers.
IS_SPACE_TAB = """
// Jump to `yes` if ch is a space or a tab, else to `no`.
def is_space_tab ch, yes, no @ try_tab < space, tab {
    bit.cmp 8, ch, space, try_tab, yes, try_tab
  try_tab:
    bit.cmp 8, ch, tab, no, yes, no
}
""".strip()

# Fold one finished word of length run[:16] into the running minimum.
FINALIZE_MIN = """
// If run > 0, update minlen[:16] to min(minlen, run); `have` marks first word.
def finalize_min run, minlen, have @ nonempty, first, smaller, end < zero16 {
    bit.cmp 16, run, zero16, end, end, nonempty
  nonempty:
    bit.if0 have, first
    bit.cmp 16, run, minlen, smaller, end, end
  first:
    bit.one have
    bit.mov 16, minlen, run
    ;end
  smaller:
    bit.mov 16, minlen, run
  end:
}
""".strip()

# Fold one finished word of length run[:16] into the running total and count.
FINALIZE_AVG = """
// If run > 0, add it to total[:16] and increment wcount[:16].
def finalize_avg run, total, wcount @ nonempty, end < zero16 {
    bit.cmp 16, run, zero16, end, end, nonempty
  nonempty:
    bit.add 16, total, run
    bit.inc 16, wcount
  end:
}
""".strip()

D_RANGE = ["upper_a: bit.vec 8, 'A'", "upper_z: bit.vec 8, 'Z'", "lower_a: bit.vec 8, 'a'", "lower_z: bit.vec 8, 'z'"]
D_NL = ["ch: bit.vec 8, 0", "nl: bit.vec 8, '\\n'"]
D_WS = ["space: bit.vec 8, ' '", "tab: bit.vec 8, '\\t'"]


def T(nnnn, slug, name, **kw):
    emit("text_processing", nnnn, slug, name, **kw)


# ==================== period / sentence-ish counting ====================

# 0470 period_sentence_count — count '.' bytes in the line
T(
    "0470",
    "period_sentence_count",
    "Period Sentence Count",
    value_data=D_NL + ["count: bit.vec 16, 0", "dot: bit.vec 8, '.'"],
    main_body="""
def main @ loop, body, hit, skip, end < ch, nl, count, dot {
    stl.startup
    bit.zero 16, count
  loop:
    bit.input ch
    bit.if0 8, ch, end
    bit.cmp 8, ch, nl, body, end, body
  body:
    bit.cmp 8, ch, dot, skip, hit, skip
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
    in_bytes=b"Hi. Go. Run.\n\0",
    out_bytes=b"3\n",
)


# ==================== word-length statistics (one line) ====================

# 0464 word_length_max — track current run length, keep the max
T(
    "0464",
    "word_length_max",
    "Word Length Max",
    extra_helpers=[IS_SPACE_TAB],
    value_data=D_NL + ["run: bit.vec 16, 0", "maxlen: bit.vec 16, 0"],
    extra_data=D_WS,
    main_body="""
def main @ loop, body, ws, letter, update, keep, end < ch, nl, run, maxlen {
    stl.startup
    bit.zero 16, run
    bit.zero 16, maxlen
  loop:
    bit.input ch
    bit.if0 8, ch, end
    bit.cmp 8, ch, nl, body, end, body
  body:
    is_space_tab ch, ws, letter
  ws:
    bit.zero 16, run
    ;loop
  letter:
    bit.inc 16, run
    bit.cmp 16, run, maxlen, keep, keep, update
  update:
    bit.mov 16, maxlen, run
  keep:
    ;loop
  end:
    bit.print_dec_uint 16, maxlen
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"a bb cccc dd\n\0",
    out_bytes=b"4\n",
)

# 0465 word_length_min — finalize each word, keep the smallest length
T(
    "0465",
    "word_length_min",
    "Word Length Min",
    extra_helpers=[IS_SPACE_TAB, FINALIZE_MIN],
    value_data=D_NL + ["run: bit.vec 16, 0", "minlen: bit.vec 16, 0", "have: bit.bit"],
    extra_data=D_WS + ["zero16: bit.vec 16, 0"],
    main_body="""
def main @ loop, body, ws, letter, end < ch, nl, run, minlen, have {
    stl.startup
    bit.zero 16, run
    bit.zero 16, minlen
    bit.zero have
  loop:
    bit.input ch
    bit.if0 8, ch, end
    bit.cmp 8, ch, nl, body, end, body
  body:
    is_space_tab ch, ws, letter
  ws:
    finalize_min run, minlen, have
    bit.zero 16, run
    ;loop
  letter:
    bit.inc 16, run
    ;loop
  end:
    finalize_min run, minlen, have
    bit.print_dec_uint 16, minlen
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"aaa bb cccc\n\0",
    out_bytes=b"2\n",
)

# 0463 word_length_avg — sum of word lengths / word count (floor)
T(
    "0463",
    "word_length_avg",
    "Word Length Avg",
    extra_helpers=[IS_SPACE_TAB, FINALIZE_AVG],
    value_data=D_NL
    + [
        "run: bit.vec 16, 0",
        "total: bit.vec 16, 0",
        "wcount: bit.vec 16, 0",
        "q: bit.vec 16, 0",
        "r: bit.vec 16, 0",
    ],
    extra_data=D_WS + ["zero16: bit.vec 16, 0"],
    main_body="""
def main @ loop, body, ws, letter, finish, none, done < ch, nl, run, total, wcount, q, r {
    stl.startup
    bit.zero 16, run
    bit.zero 16, total
    bit.zero 16, wcount
  loop:
    bit.input ch
    bit.if0 8, ch, finish
    bit.cmp 8, ch, nl, body, finish, body
  body:
    is_space_tab ch, ws, letter
  ws:
    finalize_avg run, total, wcount
    bit.zero 16, run
    ;loop
  letter:
    bit.inc 16, run
    ;loop
  finish:
    finalize_avg run, total, wcount
    bit.if0 16, wcount, none
    bit.div 16, total, wcount, q, r
    bit.print_dec_uint 16, q
    ;done
  none:
    stl.output '0'
  done:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"ab cde f\n\0",
    out_bytes=b"2\n",
)


# 0461 word_count_multiline — count whitespace-separated tokens until empty line
T(
    "0461",
    "word_count_multiline",
    "Word Count Multiline",
    extra_helpers=[IS_SPACE_TAB],
    value_data=D_NL + ["count: bit.vec 16, 0", "in_word: bit.bit", "line_filled: bit.bit"],
    extra_data=D_WS,
    main_body="""
def main @ loop, on_nl, on_byte, ws, token, start_token, end \\
        < ch, nl, count, in_word, line_filled {
    stl.startup
    bit.zero 16, count
    bit.zero in_word
    bit.zero line_filled
  loop:
    bit.input ch
    bit.if0 8, ch, end
    bit.cmp 8, ch, nl, on_byte, on_nl, on_byte
  on_nl:
    bit.if0 line_filled, end
    bit.zero in_word
    bit.zero line_filled
    ;loop
  on_byte:
    bit.one line_filled
    is_space_tab ch, ws, token
  ws:
    bit.zero in_word
    ;loop
  token:
    bit.if0 in_word, start_token
    ;loop
  start_token:
    bit.one in_word
    bit.inc 16, count
    ;loop
  end:
    bit.print_dec_uint 16, count
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"one two\nthree  four five\n\n\0",
    out_bytes=b"5\n",
)


# ==================== capitalization transforms (echo) ====================

# 0471 capitalize_first_letter — uppercase the first byte if a-z, echo the rest
T(
    "0471",
    "capitalize_first_letter",
    "Capitalize First Letter",
    extra_helpers=[IN_RANGE],
    value_data=D_NL,
    extra_data=["lower_a: bit.vec 8, 'a'", "lower_z: bit.vec 8, 'z'"],
    main_body="""
def main @ first, up, echo_first, loop, body, end < ch, nl, lower_a, lower_z {
    stl.startup
    bit.input ch
    bit.if0 8, ch, end
    bit.cmp 8, ch, nl, first, end, first
  first:
    in_range ch, lower_a, lower_z, up, echo_first
  up:
    bit.zero ch + 5*dw
  echo_first:
    bit.print ch
  loop:
    bit.input ch
    bit.if0 8, ch, end
    bit.cmp 8, ch, nl, body, end, body
  body:
    bit.print ch
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"hello world\n\0",
    out_bytes=b"Hello world\n",
)

# 0473 uncapitalize_first — lowercase the first byte if A-Z, echo the rest
T(
    "0473",
    "uncapitalize_first",
    "Uncapitalize First",
    extra_helpers=[IN_RANGE],
    value_data=D_NL,
    extra_data=["upper_a: bit.vec 8, 'A'", "upper_z: bit.vec 8, 'Z'"],
    main_body="""
def main @ first, down, echo_first, loop, body, end < ch, nl, upper_a, upper_z {
    stl.startup
    bit.input ch
    bit.if0 8, ch, end
    bit.cmp 8, ch, nl, first, end, first
  first:
    in_range ch, upper_a, upper_z, down, echo_first
  down:
    bit.one ch + 5*dw
  echo_first:
    bit.print ch
  loop:
    bit.input ch
    bit.if0 8, ch, end
    bit.cmp 8, ch, nl, body, end, body
  body:
    bit.print ch
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"Hello World\n\0",
    out_bytes=b"hello World\n",
)

# 0472 capitalize_words — first letter of each word uppercased, other letters lowercased
T(
    "0472",
    "capitalize_words",
    "Capitalize Words",
    extra_helpers=[IN_RANGE, IS_LETTER, IS_SPACE_TAB],
    value_data=D_NL + ["seen: bit.bit"],
    extra_data=D_RANGE + D_WS,
    main_body="""
def main @ loop, body, is_ws, letter, do_case, make_upper, emit_ch, end < ch, nl, seen {
    stl.startup
    bit.zero seen
  loop:
    bit.input ch
    bit.if0 8, ch, end
    bit.cmp 8, ch, nl, body, end, body
  body:
    is_space_tab ch, is_ws, letter
  is_ws:
    bit.zero seen
    ;emit_ch
  letter:
    is_letter ch, do_case, emit_ch
  do_case:
    bit.if0 seen, make_upper
    bit.one ch + 5*dw
    ;emit_ch
  make_upper:
    bit.zero ch + 5*dw
    bit.one seen
  emit_ch:
    bit.print ch
    ;loop
  end:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"hELLO wORLD foo\n\0",
    out_bytes=b"Hello World Foo\n",
)


print("---")
print("TEXT_PROCESSING DONE")

"""Phase 3 batch 10: strings positional/membership (8 programs).

first_char_of_line, last_char_of_line, starts_with_uppercase, ends_with_period,
has_char_in_line, char_at_index, substring_first_3, substring_last_3. All stream
with small fixed state (no full-line buffer). The 3 buffer-needing string
programs (is_palindrome_string, repeat_line_2x/3x) are still deferred.

Run from the repo root:  python scripts/batch10_strings2.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog_arith import emit  # noqa: E402

IN_RANGE = """
// Jump to `yes` if lo <= ch <= hi (lo, hi are bit[:8] bounds), else to `no`.
def in_range ch, lo, hi, yes, no @ check_hi {
    bit.cmp 8, ch, lo, no, yes, check_hi
  check_hi:
    bit.cmp 8, ch, hi, yes, yes, no
}
""".strip()


def S(nnnn, slug, name, **kw):
    emit("strings", nnnn, slug, name, **kw)


# 0173 first_char_of_line — print just the first byte
S(
    "0173",
    "first_char_of_line",
    "First Char Of Line",
    value_data=["ch: bit.vec 8, 0"],
    main_body="""
def main < ch {
    stl.startup
    bit.input ch
    bit.print ch
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"hello\n\0",
    out_bytes=b"h\n",
)

# 0191 substring_first_3 — print the first 3 bytes
S(
    "0191",
    "substring_first_3",
    "Substring First 3",
    value_data=["ch: bit.vec 8, 0"],
    main_body="""
def main < ch {
    stl.startup
    bit.input ch
    bit.print ch
    bit.input ch
    bit.print ch
    bit.input ch
    bit.print ch
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"hello\n\0",
    out_bytes=b"hel\n",
)

# 0184 starts_with_uppercase — is the first byte A-Z?
S(
    "0184",
    "starts_with_uppercase",
    "Starts With Uppercase",
    extra_helpers=[IN_RANGE],
    value_data=["ch: bit.vec 8, 0", "upper_a: bit.vec 8, 'A'", "upper_z: bit.vec 8, 'Z'"],
    main_body="""
def main @ yes, no, done < ch, upper_a, upper_z {
    stl.startup
    bit.input ch
    in_range ch, upper_a, upper_z, yes, no
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"Hello\n\0",
    out_bytes=b"1\n",
)

# 0174 last_char_of_line — track the last byte before \n
S(
    "0174",
    "last_char_of_line",
    "Last Char Of Line",
    value_data=["ch: bit.vec 8, 0", "last: bit.vec 8, 0", "nl: bit.vec 8, '\\n'"],
    main_body="""
def main @ loop, save, end < ch, last, nl {
    stl.startup
  loop:
    bit.input ch
    bit.if0 8, ch, end
    bit.cmp 8, ch, nl, save, end, save
  save:
    bit.mov 8, last, ch
    ;loop
  end:
    bit.print last
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"hello\n\0",
    out_bytes=b"o\n",
)

# 0185 ends_with_period — is the last byte before \n a '.'?
S(
    "0185",
    "ends_with_period",
    "Ends With Period",
    value_data=["ch: bit.vec 8, 0", "last: bit.vec 8, 0", "nl: bit.vec 8, '\\n'", "period: bit.vec 8, '.'"],
    main_body="""
def main @ loop, save, end, yes, no, done < ch, last, nl, period {
    stl.startup
    bit.zero 8, last
  loop:
    bit.input ch
    bit.if0 8, ch, end
    bit.cmp 8, ch, nl, save, end, save
  save:
    bit.mov 8, last, ch
    ;loop
  end:
    bit.cmp 8, last, period, no, yes, no
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"End.\n\0",
    out_bytes=b"1\n",
)

# 0183 has_char_in_line — read target byte, \n, then scan the line for it
S(
    "0183",
    "has_char_in_line",
    "Has Char In Line",
    value_data=["ch: bit.vec 8, 0", "target: bit.vec 8, 0", "nl: bit.vec 8, '\\n'"],
    main_body="""
def main @ loop, scan, neq, found, notfound, done < ch, target, nl {
    stl.startup
    bit.input target
    bit.input ch
  loop:
    bit.input ch
    bit.if0 8, ch, notfound
    bit.cmp 8, ch, nl, scan, notfound, scan
  scan:
    bit.cmp 8, ch, target, neq, found, neq
  neq:
    ;loop
  found:
    stl.output "1\\n"
    ;done
  notfound:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"l\nhello\n\0",
    out_bytes=b"1\n",
)

# 0190 char_at_index — read digit N + \n, then print the byte at 0-based index N
S(
    "0190",
    "char_at_index",
    "Char At Index",
    value_data=["ch: bit.vec 8, 0", "idx: bit.vec 8, 0", "target_idx: bit.vec 8, 0", "nl: bit.vec 8, '\\n'"],
    main_body="""
def main @ loop, body, hit, advance, done < ch, idx, target_idx, nl {
    stl.startup
    bit.input ch
    bit.mov 8, target_idx, ch
    bit.zero target_idx + 4*dw
    bit.zero target_idx + 5*dw
    bit.input ch
    bit.zero 8, idx
  loop:
    bit.input ch
    bit.if0 8, ch, done
    bit.cmp 8, ch, nl, body, done, body
  body:
    bit.cmp 8, idx, target_idx, advance, hit, advance
  hit:
    bit.print ch
    stl.output '\\n'
    ;done
  advance:
    bit.inc 8, idx
    ;loop
  done:
    stl.loop
}
""",
    in_bytes=b"2\nhello\n\0",
    out_bytes=b"l\n",
)

# 0192 substring_last_3 — print the 3 bytes immediately before \n (shift register)
S(
    "0192",
    "substring_last_3",
    "Substring Last 3",
    value_data=["ch: bit.vec 8, 0", "c0: bit.vec 8, 0", "c1: bit.vec 8, 0", "c2: bit.vec 8, 0", "nl: bit.vec 8, '\\n'"],
    main_body="""
def main @ loop, shift, end < ch, c0, c1, c2, nl {
    stl.startup
  loop:
    bit.input ch
    bit.if0 8, ch, end
    bit.cmp 8, ch, nl, shift, end, shift
  shift:
    bit.mov 8, c0, c1
    bit.mov 8, c1, c2
    bit.mov 8, c2, ch
    ;loop
  end:
    bit.print c0
    bit.print c1
    bit.print c2
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"hello\n\0",
    out_bytes=b"llo\n",
)

print("---")
print("BATCH 10 DONE")

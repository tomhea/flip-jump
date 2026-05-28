"""Phase 3 batch 3: arithmetic core (#0056-0075, minus the two loop programs).

Emits clean, helper-macro-structured .fj files for the 18 single-step
arithmetic programs (read decimal operands -> one operation -> print), then
registers + verifies each via catalog_register.

Values are 16-bit (0-65535 unsigned / -32768..32767 signed) — ample for every
test case and ~3x faster to compile than 32-bit. Run from the repo root:

    python scripts/batch03_arithmetic.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog_register import register  # noqa: E402

PROG = Path(__file__).resolve().parent.parent / "programs" / "catalog" / "arithmetic"

# ----- shared helper-macro definitions (appended per-file as needed) -----

READ_DECIMAL = """
// Read an unsigned decimal (digits until `\\n` or `\\0`) into value[:n].
def read_decimal n, value @ loop, add_digit, end < ch, nl, digit, err {
    bit.zero n, value
  loop:
    bit.input ch
    bit.if0 8, ch, end
    bit.cmp 8, ch, nl, add_digit, end, add_digit
  add_digit:
    bit.mul10 n, value
    bit.ascii2dec err, digit, ch
    bit.add n, value, digit
    ;loop
  end:
}
"""

READ_SIGNED = """
// Read a signed decimal (optional leading `-`, digits until `\\n`/`\\0`) into value[:n].
def read_signed_decimal n, value @ neg, body, add_digit, fin, end < ch, nl, minus, digit, err, neg_flag {
    bit.zero n, value
    bit.zero neg_flag
    bit.input ch
    bit.if0 8, ch, end
    bit.cmp 8, ch, minus, body, neg, body
  neg:
    bit.one neg_flag
    bit.input ch
  body:
    bit.if0 8, ch, fin
    bit.cmp 8, ch, nl, add_digit, fin, add_digit
  add_digit:
    bit.mul10 n, value
    bit.ascii2dec err, digit, ch
    bit.add n, value, digit
    bit.input ch
    ;body
  fin:
    bit.if0 neg_flag, end
    bit.neg n, value
  end:
}
"""

# Multiply via repeated addition (bit.mul is unusable in this STL version — its
# internal mul.mul_add_if fails to resolve; see flipjump_claude_conclusions.md).
MUL_INTO = """
// dst[:n] = addend[:n] * times[:n], via repeated addition (times is small).
def mul_into n, dst, addend, times @ loop, end < mul_counter {
    bit.zero n, dst
    bit.mov n, mul_counter, times
  loop:
    bit.if0 n, mul_counter, end
    bit.add n, dst, addend
    bit.dec n, mul_counter
    ;loop
  end:
}
"""

# scratch data each read helper needs (union when both are used)
SCRATCH_UNSIGNED = ["ch: bit.vec 8, 0", "nl: bit.vec 8, '\\n'", "digit: bit.vec 16, 0", "err: bit.bit"]
SCRATCH_SIGNED = ["minus: bit.vec 8, '-'", "neg_flag: bit.bit"]
SCRATCH_MUL = ["mul_counter: bit.vec 16, 0"]


def emit(
    nnnn, slug, *, main_body, value_data, unsigned=False, signed=False, mul=False, extra_data=None, in_bytes, out_bytes
):
    """Assemble a clean .fj (header + main + helpers + data) and register it."""
    desc_line = _catalog_desc(slug)
    name = _title(slug)

    parts = [f"// {name} (#{nnnn})", "", f"// {desc_line}", "", "main", "", main_body.strip()]

    helpers = []
    scratch = []
    if unsigned:
        helpers.append(READ_DECIMAL.strip())
        scratch += SCRATCH_UNSIGNED
    if signed:
        helpers.append(READ_SIGNED.strip())
        # signed needs the unsigned scratch set plus minus/neg_flag; de-dup below
        for s in SCRATCH_UNSIGNED:
            if s not in scratch:
                scratch.append(s)
        scratch += SCRATCH_SIGNED
    if mul:
        helpers.append(MUL_INTO.strip())
        scratch += SCRATCH_MUL
    for h in helpers:
        parts += ["", h]

    data = list(value_data) + (extra_data or []) + scratch
    parts += [""] + data + [""]

    fj = "\n".join(parts)
    (PROG / f"{slug}.fj").write_text(fj, encoding="utf-8", newline="\n")
    register(category="arithmetic", slug=slug, in_bytes=in_bytes, out_bytes=out_bytes)


# ----- CATALOG.md description lookup + title casing -----

_CATALOG = (Path(__file__).resolve().parent.parent / "programs" / "catalog" / "CATALOG.md").read_text(encoding="utf-8")


def _catalog_desc(slug):
    import re

    m = re.search(rf"\| APPROVED \| \S+ \| {re.escape(slug)} \| (.+?) \|", _CATALOG)
    if not m:
        raise SystemExit(f"no APPROVED row for {slug}")
    return m.group(1).strip()


_TITLE_OVERRIDES = {
    "add_two_decimals": "Add Two Decimals",
    "sub_two_decimals": "Sub Two Decimals",
    "mul_single_digits": "Mul Single Digits",
    "div_two_decimals": "Div Two Decimals",
    "mod_two_decimals": "Mod Two Decimals",
    "add_three_decimals": "Add Three Decimals",
    "abs_decimal": "Abs Decimal",
    "negate_decimal": "Negate Decimal",
    "inc_decimal": "Inc Decimal",
    "dec_decimal": "Dec Decimal",
    "double_decimal": "Double Decimal",
    "halve_decimal": "Halve Decimal",
    "square_small": "Square Small",
    "cube_small": "Cube Small",
    "min_two": "Min Two",
    "max_two": "Max Two",
    "mod_by_4": "Mod By 4",
    "mod_by_10": "Mod By 10",
}


def _title(slug):
    return _TITLE_OVERRIDES[slug]


# ============================ the 18 programs ============================

# 0056 add_two_decimals
emit(
    "0056",
    "add_two_decimals",
    unsigned=True,
    value_data=["a: bit.vec 16, 0", "b: bit.vec 16, 0"],
    main_body="""
def main < a, b {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    bit.add 16, a, b
    bit.print_dec_uint 16, a
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"12\n30\n\0",
    out_bytes=b"42\n",
)

# 0057 sub_two_decimals (signed result)
emit(
    "0057",
    "sub_two_decimals",
    signed=True,
    value_data=["a: bit.vec 16, 0", "b: bit.vec 16, 0"],
    main_body="""
def main < a, b {
    stl.startup
    read_signed_decimal 16, a
    read_signed_decimal 16, b
    bit.sub 16, a, b
    bit.print_dec_int 16, a
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"5\n8\n\0",
    out_bytes=b"-3\n",
)

# 0058 mul_single_digits
emit(
    "0058",
    "mul_single_digits",
    unsigned=True,
    mul=True,
    value_data=["a: bit.vec 16, 0", "b: bit.vec 16, 0", "p: bit.vec 16, 0"],
    main_body="""
def main < a, b, p {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    mul_into 16, p, a, b
    bit.print_dec_uint 16, p
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"6\n7\n\0",
    out_bytes=b"42\n",
)

# 0059 div_two_decimals
emit(
    "0059",
    "div_two_decimals",
    unsigned=True,
    value_data=["a: bit.vec 16, 0", "b: bit.vec 16, 0", "q: bit.vec 16, 0", "r: bit.vec 16, 0"],
    main_body="""
def main < a, b, q, r {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    bit.div 16, a, b, q, r
    bit.print_dec_uint 16, q
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"17\n5\n\0",
    out_bytes=b"3\n",
)

# 0060 mod_two_decimals
emit(
    "0060",
    "mod_two_decimals",
    unsigned=True,
    value_data=["a: bit.vec 16, 0", "b: bit.vec 16, 0", "q: bit.vec 16, 0", "r: bit.vec 16, 0"],
    main_body="""
def main < a, b, q, r {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    bit.div 16, a, b, q, r
    bit.print_dec_uint 16, r
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"17\n5\n\0",
    out_bytes=b"2\n",
)

# 0061 add_three_decimals
emit(
    "0061",
    "add_three_decimals",
    unsigned=True,
    value_data=["a: bit.vec 16, 0", "b: bit.vec 16, 0", "c: bit.vec 16, 0"],
    main_body="""
def main < a, b, c {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    read_decimal 16, c
    bit.add 16, a, b
    bit.add 16, a, c
    bit.print_dec_uint 16, a
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"1\n2\n3\n\0",
    out_bytes=b"6\n",
)

# 0062 abs_decimal — read signed, drop sign, print magnitude
emit(
    "0062",
    "abs_decimal",
    signed=True,
    value_data=["a: bit.vec 16, 0"],
    main_body="""
def main @ done < a {
    stl.startup
    read_signed_decimal 16, a
    bit.if0 a + 15*dw, done
    bit.neg 16, a
  done:
    bit.print_dec_uint 16, a
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"-42\n\0",
    out_bytes=b"42\n",
)

# 0063 negate_decimal
emit(
    "0063",
    "negate_decimal",
    signed=True,
    value_data=["a: bit.vec 16, 0"],
    main_body="""
def main < a {
    stl.startup
    read_signed_decimal 16, a
    bit.neg 16, a
    bit.print_dec_int 16, a
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"7\n\0",
    out_bytes=b"-7\n",
)

# 0064 inc_decimal
emit(
    "0064",
    "inc_decimal",
    signed=True,
    value_data=["a: bit.vec 16, 0"],
    main_body="""
def main < a {
    stl.startup
    read_signed_decimal 16, a
    bit.inc 16, a
    bit.print_dec_int 16, a
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"41\n\0",
    out_bytes=b"42\n",
)

# 0065 dec_decimal
emit(
    "0065",
    "dec_decimal",
    signed=True,
    value_data=["a: bit.vec 16, 0"],
    main_body="""
def main < a {
    stl.startup
    read_signed_decimal 16, a
    bit.dec 16, a
    bit.print_dec_int 16, a
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"43\n\0",
    out_bytes=b"42\n",
)

# 0066 double_decimal
emit(
    "0066",
    "double_decimal",
    signed=True,
    value_data=["a: bit.vec 16, 0", "t: bit.vec 16, 0"],
    main_body="""
def main < a, t {
    stl.startup
    read_signed_decimal 16, a
    bit.mov 16, t, a
    bit.add 16, a, t
    bit.print_dec_int 16, a
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"21\n\0",
    out_bytes=b"42\n",
)

# 0067 halve_decimal
emit(
    "0067",
    "halve_decimal",
    unsigned=True,
    value_data=["a: bit.vec 16, 0", "two: bit.vec 16, 2", "q: bit.vec 16, 0", "r: bit.vec 16, 0"],
    main_body="""
def main < a, two, q, r {
    stl.startup
    read_decimal 16, a
    bit.div 16, a, two, q, r
    bit.print_dec_uint 16, q
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"85\n\0",
    out_bytes=b"42\n",
)

# 0068 square_small
emit(
    "0068",
    "square_small",
    unsigned=True,
    mul=True,
    value_data=["a: bit.vec 16, 0", "p: bit.vec 16, 0"],
    main_body="""
def main < a, p {
    stl.startup
    read_decimal 16, a
    mul_into 16, p, a, a
    bit.print_dec_uint 16, p
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"12\n\0",
    out_bytes=b"144\n",
)

# 0069 cube_small
emit(
    "0069",
    "cube_small",
    unsigned=True,
    mul=True,
    value_data=["a: bit.vec 16, 0", "sq: bit.vec 16, 0", "p: bit.vec 16, 0"],
    main_body="""
def main < a, sq, p {
    stl.startup
    read_decimal 16, a
    mul_into 16, sq, a, a
    mul_into 16, p, sq, a
    bit.print_dec_uint 16, p
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"5\n\0",
    out_bytes=b"125\n",
)

# 0070 min_two
emit(
    "0070",
    "min_two",
    unsigned=True,
    value_data=["a: bit.vec 16, 0", "b: bit.vec 16, 0"],
    main_body="""
def main @ use_a, use_b, done < a, b {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    bit.cmp 16, a, b, use_a, use_a, use_b
  use_a:
    bit.print_dec_uint 16, a
    ;done
  use_b:
    bit.print_dec_uint 16, b
  done:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"7\n3\n\0",
    out_bytes=b"3\n",
)

# 0071 max_two
emit(
    "0071",
    "max_two",
    unsigned=True,
    value_data=["a: bit.vec 16, 0", "b: bit.vec 16, 0"],
    main_body="""
def main @ use_a, use_b, done < a, b {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    bit.cmp 16, a, b, use_b, use_b, use_a
  use_a:
    bit.print_dec_uint 16, a
    ;done
  use_b:
    bit.print_dec_uint 16, b
  done:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"7\n3\n\0",
    out_bytes=b"7\n",
)

# 0074 mod_by_4
emit(
    "0074",
    "mod_by_4",
    unsigned=True,
    value_data=["a: bit.vec 16, 0", "four: bit.vec 16, 4", "q: bit.vec 16, 0", "r: bit.vec 16, 0"],
    main_body="""
def main < a, four, q, r {
    stl.startup
    read_decimal 16, a
    bit.div 16, a, four, q, r
    bit.print_dec_uint 16, r
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"23\n\0",
    out_bytes=b"3\n",
)

# 0075 mod_by_10
emit(
    "0075",
    "mod_by_10",
    unsigned=True,
    value_data=["a: bit.vec 16, 0", "ten: bit.vec 16, 10", "q: bit.vec 16, 0", "r: bit.vec 16, 0"],
    main_body="""
def main < a, ten, q, r {
    stl.startup
    read_decimal 16, a
    bit.div 16, a, ten, q, r
    bit.print_dec_uint 16, r
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"237\n\0",
    out_bytes=b"7\n",
)

print("---")
print("BATCH 3 DONE")

"""Phase 3 batch 4: arithmetic predicates, comparisons, constant-ops, multi-input.

25 programs (the non-loop arithmetic remainder). Loops/sequences/N-inputs are
batch 5. Run from the repo root:  python scripts/batch04_arithmetic.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog_arith import MAX_INTO, MIN_INTO, emit  # noqa: E402


def A(nnnn, slug, name, **kw):
    emit("arithmetic", nnnn, slug, name, **kw)


# ---- two-input averages ----
A(
    "0101",
    "avg_two",
    "Avg Two",
    unsigned=True,
    value_data=["a: bit.vec 16, 0", "b: bit.vec 16, 0", "two: bit.vec 16, 2", "q: bit.vec 16, 0", "r: bit.vec 16, 0"],
    main_body="""
def main < a, b, two, q, r {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    bit.add 16, a, b
    bit.div 16, a, two, q, r
    bit.print_dec_uint 16, q
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"3\n8\n\0",
    out_bytes=b"5\n",
)

A(
    "0102",
    "avg_three",
    "Avg Three",
    unsigned=True,
    value_data=[
        "a: bit.vec 16, 0",
        "b: bit.vec 16, 0",
        "c: bit.vec 16, 0",
        "three: bit.vec 16, 3",
        "q: bit.vec 16, 0",
        "r: bit.vec 16, 0",
    ],
    main_body="""
def main < a, b, c, three, q, r {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    read_decimal 16, c
    bit.add 16, a, b
    bit.add 16, a, c
    bit.div 16, a, three, q, r
    bit.print_dec_uint 16, q
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"2\n4\n9\n\0",
    out_bytes=b"5\n",
)

# ---- comparison / sign ----
A(
    "0103",
    "compare_two",
    "Compare Two",
    unsigned=True,
    value_data=["a: bit.vec 16, 0", "b: bit.vec 16, 0"],
    main_body="""
def main @ lt, eq, gt, done < a, b {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    bit.cmp 16, a, b, lt, eq, gt
  lt:
    stl.output '<'
    ;done
  eq:
    stl.output '='
    ;done
  gt:
    stl.output '>'
  done:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"3\n8\n\0",
    out_bytes=b"<\n",
)

A(
    "0104",
    "sign_of",
    "Sign Of",
    signed=True,
    value_data=["a: bit.vec 16, 0"],
    main_body="""
def main @ neg, pos, zero, done < a {
    stl.startup
    read_signed_decimal 16, a
    bit.if0 16, a, zero
    bit.if1 a + 15*dw, neg
  pos:
    stl.output '+'
    ;done
  neg:
    stl.output '-'
    ;done
  zero:
    stl.output '0'
  done:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"-5\n\0",
    out_bytes=b"-\n",
)

# ---- predicates (print 1\n or 0\n) ----
A(
    "0105",
    "is_zero",
    "Is Zero",
    unsigned=True,
    value_data=["a: bit.vec 16, 0"],
    main_body="""
def main @ yes, done < a {
    stl.startup
    read_decimal 16, a
    bit.if0 16, a, yes
    stl.output "0\\n"
    ;done
  yes:
    stl.output "1\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"0\n\0",
    out_bytes=b"1\n",
)

A(
    "0106",
    "is_positive",
    "Is Positive",
    signed=True,
    value_data=["a: bit.vec 16, 0"],
    main_body="""
def main @ no, done < a {
    stl.startup
    read_signed_decimal 16, a
    bit.if0 16, a, no
    bit.if1 a + 15*dw, no
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"7\n\0",
    out_bytes=b"1\n",
)

A(
    "0107",
    "is_negative",
    "Is Negative",
    signed=True,
    value_data=["a: bit.vec 16, 0"],
    main_body="""
def main @ yes, done < a {
    stl.startup
    read_signed_decimal 16, a
    bit.if1 a + 15*dw, yes
    stl.output "0\\n"
    ;done
  yes:
    stl.output "1\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"-7\n\0",
    out_bytes=b"1\n",
)

A(
    "0115",
    "is_even",
    "Is Even",
    unsigned=True,
    value_data=["a: bit.vec 16, 0"],
    main_body="""
def main @ yes, done < a {
    stl.startup
    read_decimal 16, a
    bit.if0 a, yes
    stl.output "0\\n"
    ;done
  yes:
    stl.output "1\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"6\n\0",
    out_bytes=b"1\n",
)

A(
    "0116",
    "is_odd",
    "Is Odd",
    unsigned=True,
    value_data=["a: bit.vec 16, 0"],
    main_body="""
def main @ yes, done < a {
    stl.startup
    read_decimal 16, a
    bit.if1 a, yes
    stl.output "0\\n"
    ;done
  yes:
    stl.output "1\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"7\n\0",
    out_bytes=b"1\n",
)

# ---- expression ----
A(
    "0108",
    "add_with_expression",
    "Add With Expression",
    unsigned=True,
    value_data=["a: bit.vec 16, 0", "b: bit.vec 16, 0", "sum: bit.vec 16, 0"],
    main_body="""
def main < a, b, sum {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    bit.mov 16, sum, a
    bit.add 16, sum, b
    bit.print_dec_uint 16, a
    stl.output " + "
    bit.print_dec_uint 16, b
    stl.output " = "
    bit.print_dec_uint 16, sum
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"12\n30\n\0",
    out_bytes=b"12 + 30 = 42\n",
)

# ---- multiply by constant (repeated addition) ----
for nnnn, slug, name, k, sample, prod in [
    ("0109", "mul_by_3", "Mul By 3", 3, 10, 30),
    ("0110", "mul_by_5", "Mul By 5", 5, 8, 40),
    ("0111", "mul_by_7", "Mul By 7", 7, 6, 42),
    ("0112", "mul_by_10", "Mul By 10", 10, 9, 90),
]:
    A(
        nnnn,
        slug,
        name,
        unsigned=True,
        mul=True,
        value_data=["a: bit.vec 16, 0", f"k: bit.vec 16, {k}", "p: bit.vec 16, 0"],
        main_body="""
def main < a, k, p {
    stl.startup
    read_decimal 16, a
    mul_into 16, p, a, k
    bit.print_dec_uint 16, p
    stl.output '\\n'
    stl.loop
}
""",
        in_bytes=f"{sample}\n\0".encode(),
        out_bytes=f"{prod}\n".encode(),
    )

# ---- division-derived ----
A(
    "0113",
    "div_by_3_quot_rem",
    "Div By 3 Quot Rem",
    unsigned=True,
    value_data=["a: bit.vec 16, 0", "three: bit.vec 16, 3", "q: bit.vec 16, 0", "r: bit.vec 16, 0"],
    main_body="""
def main < a, three, q, r {
    stl.startup
    read_decimal 16, a
    bit.div 16, a, three, q, r
    bit.print_dec_uint 16, q
    stl.output ' '
    bit.print_dec_uint 16, r
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"17\n\0",
    out_bytes=b"5 2\n",
)

A(
    "0114",
    "complement_to_100",
    "Complement To 100",
    unsigned=True,
    value_data=["a: bit.vec 16, 0", "c100: bit.vec 16, 100"],
    main_body="""
def main < a, c100 {
    stl.startup
    read_decimal 16, a
    bit.sub 16, c100, a
    bit.print_dec_uint 16, c100
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"42\n\0",
    out_bytes=b"58\n",
)

A(
    "0136",
    "add_then_mod_10",
    "Add Then Mod 10",
    unsigned=True,
    value_data=["a: bit.vec 16, 0", "b: bit.vec 16, 0", "ten: bit.vec 16, 10", "q: bit.vec 16, 0", "r: bit.vec 16, 0"],
    main_body="""
def main < a, b, ten, q, r {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    bit.add 16, a, b
    bit.div 16, a, ten, q, r
    bit.print_dec_uint 16, r
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"7\n8\n\0",
    out_bytes=b"5\n",
)

# ---- swap ----
A(
    "0123",
    "swap_pair",
    "Swap Pair",
    unsigned=True,
    value_data=["a: bit.vec 16, 0", "b: bit.vec 16, 0"],
    main_body="""
def main < a, b {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    bit.print_dec_uint 16, b
    stl.output '\\n'
    bit.print_dec_uint 16, a
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"3\n8\n\0",
    out_bytes=b"8\n3\n",
)

# ---- abs difference ----
A(
    "0137",
    "abs_diff",
    "Abs Diff",
    unsigned=True,
    value_data=["a: bit.vec 16, 0", "b: bit.vec 16, 0", "t: bit.vec 16, 0"],
    main_body="""
def main @ a_ge_b, b_gt_a, done < a, b, t {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    bit.cmp 16, a, b, b_gt_a, a_ge_b, a_ge_b
  a_ge_b:
    bit.mov 16, t, a
    bit.sub 16, t, b
    ;done
  b_gt_a:
    bit.mov 16, t, b
    bit.sub 16, t, a
  done:
    bit.print_dec_uint 16, t
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"3\n8\n\0",
    out_bytes=b"5\n",
)

# ---- clamp ----
A(
    "0135",
    "clamp_to_max_9",
    "Clamp To Max 9",
    unsigned=True,
    value_data=["a: bit.vec 16, 0", "nine: bit.vec 16, 9"],
    main_body="""
def main @ use_a, use_9, done < a, nine {
    stl.startup
    read_decimal 16, a
    bit.cmp 16, a, nine, use_a, use_a, use_9
  use_a:
    bit.print_dec_uint 16, a
    ;done
  use_9:
    bit.print_dec_uint 16, nine
  done:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"42\n\0",
    out_bytes=b"9\n",
)

# ---- three-input min/max/range/median ----
A(
    "0125",
    "max_three",
    "Max Three",
    unsigned=True,
    extra_helpers=[MAX_INTO],
    value_data=["a: bit.vec 16, 0", "b: bit.vec 16, 0", "c: bit.vec 16, 0", "mx: bit.vec 16, 0"],
    main_body="""
def main < a, b, c, mx {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    read_decimal 16, c
    max_into 16, mx, a, b
    max_into 16, mx, mx, c
    bit.print_dec_uint 16, mx
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"3\n9\n5\n\0",
    out_bytes=b"9\n",
)

A(
    "0126",
    "min_three",
    "Min Three",
    unsigned=True,
    extra_helpers=[MIN_INTO],
    value_data=["a: bit.vec 16, 0", "b: bit.vec 16, 0", "c: bit.vec 16, 0", "mn: bit.vec 16, 0"],
    main_body="""
def main < a, b, c, mn {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    read_decimal 16, c
    min_into 16, mn, a, b
    min_into 16, mn, mn, c
    bit.print_dec_uint 16, mn
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"3\n9\n5\n\0",
    out_bytes=b"3\n",
)

A(
    "0127",
    "range_of_three",
    "Range Of Three",
    unsigned=True,
    extra_helpers=[MAX_INTO, MIN_INTO],
    value_data=["a: bit.vec 16, 0", "b: bit.vec 16, 0", "c: bit.vec 16, 0", "mx: bit.vec 16, 0", "mn: bit.vec 16, 0"],
    main_body="""
def main < a, b, c, mx, mn {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    read_decimal 16, c
    max_into 16, mx, a, b
    max_into 16, mx, mx, c
    min_into 16, mn, a, b
    min_into 16, mn, mn, c
    bit.sub 16, mx, mn
    bit.print_dec_uint 16, mx
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"3\n9\n5\n\0",
    out_bytes=b"6\n",
)

# median = (a+b+c) - max - min
A(
    "0124",
    "median_of_three",
    "Median Of Three",
    unsigned=True,
    extra_helpers=[MAX_INTO, MIN_INTO],
    value_data=[
        "a: bit.vec 16, 0",
        "b: bit.vec 16, 0",
        "c: bit.vec 16, 0",
        "mx: bit.vec 16, 0",
        "mn: bit.vec 16, 0",
        "sum: bit.vec 16, 0",
    ],
    main_body="""
def main < a, b, c, mx, mn, sum {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    read_decimal 16, c
    max_into 16, mx, a, b
    max_into 16, mx, mx, c
    min_into 16, mn, a, b
    min_into 16, mn, mn, c
    bit.mov 16, sum, a
    bit.add 16, sum, b
    bit.add 16, sum, c
    bit.sub 16, sum, mx
    bit.sub 16, sum, mn
    bit.print_dec_uint 16, sum
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"9\n3\n5\n\0",
    out_bytes=b"5\n",
)

# ---- in range ----
A(
    "0132",
    "is_in_range",
    "Is In Range",
    unsigned=True,
    value_data=["a: bit.vec 16, 0", "lo: bit.vec 16, 0", "hi: bit.vec 16, 0"],
    main_body="""
def main @ check_hi, yes, no, done < a, lo, hi {
    stl.startup
    read_decimal 16, a
    read_decimal 16, lo
    read_decimal 16, hi
    bit.cmp 16, a, lo, no, check_hi, check_hi
  check_hi:
    bit.cmp 16, a, hi, yes, yes, no
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"5\n1\n9\n\0",
    out_bytes=b"1\n",
)

print("---")
print("BATCH 4 DONE")

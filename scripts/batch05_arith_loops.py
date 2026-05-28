"""Phase 3 batch 5: arithmetic loops, sequences, and N-input reductions.

The 14 remaining arithmetic programs, completing the category. Counter loops
live in `main` (allowed — only stl.startup/stl.loop are main-only); they reuse
the shared read_decimal / mul_into / max_into / min_into helpers.

Run from the repo root:  python scripts/batch05_arith_loops.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog_arith import MAX_INTO, MIN_INTO, emit  # noqa: E402


def A(nnnn, slug, name, **kw):
    emit("arithmetic", nnnn, slug, name, **kw)


# 0072 sum_to_n — 1+2+...+N
A(
    "0072",
    "sum_to_n",
    "Sum To N",
    unsigned=True,
    value_data=["limit: bit.vec 16, 0", "idx: bit.vec 16, 0", "sum: bit.vec 16, 0"],
    main_body="""
def main @ loop, body, end < limit, idx, sum {
    stl.startup
    read_decimal 16, limit
    bit.zero 16, sum
    bit.zero 16, idx
    bit.inc 16, idx
  loop:
    bit.cmp 16, idx, limit, body, body, end
  body:
    bit.add 16, sum, idx
    bit.inc 16, idx
    ;loop
  end:
    bit.print_dec_uint 16, sum
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"5\n\0",
    out_bytes=b"15\n",
)

# 0073 factorial_small — N!
A(
    "0073",
    "factorial_small",
    "Factorial Small",
    unsigned=True,
    mul=True,
    value_data=["limit: bit.vec 16, 0", "idx: bit.vec 16, 0", "result: bit.vec 16, 1", "tmp: bit.vec 16, 0"],
    main_body="""
def main @ loop, body, end < limit, idx, result, tmp {
    stl.startup
    read_decimal 16, limit
    bit.zero 16, idx
    bit.inc 16, idx
  loop:
    bit.cmp 16, idx, limit, body, body, end
  body:
    mul_into 16, tmp, result, idx
    bit.mov 16, result, tmp
    bit.inc 16, idx
    ;loop
  end:
    bit.print_dec_uint 16, result
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"5\n\0",
    out_bytes=b"120\n",
)

# 0117 count_up_to_n
A(
    "0117",
    "count_up_to_n",
    "Count Up To N",
    unsigned=True,
    value_data=["limit: bit.vec 16, 0", "idx: bit.vec 16, 0"],
    main_body="""
def main @ loop, body, end < limit, idx {
    stl.startup
    read_decimal 16, limit
    bit.zero 16, idx
    bit.inc 16, idx
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
    in_bytes=b"3\n\0",
    out_bytes=b"1\n2\n3\n",
)

# 0118 count_down_from_n
A(
    "0118",
    "count_down_from_n",
    "Count Down From N",
    unsigned=True,
    value_data=["idx: bit.vec 16, 0"],
    main_body="""
def main @ loop, end < idx {
    stl.startup
    read_decimal 16, idx
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
    in_bytes=b"3\n\0",
    out_bytes=b"3\n2\n1\n",
)

# 0119 evens_up_to_n — start 2, step 2
A(
    "0119",
    "evens_up_to_n",
    "Evens Up To N",
    unsigned=True,
    value_data=["limit: bit.vec 16, 0", "idx: bit.vec 16, 2", "two: bit.vec 16, 2"],
    main_body="""
def main @ loop, body, end < limit, idx, two {
    stl.startup
    read_decimal 16, limit
  loop:
    bit.cmp 16, idx, limit, body, body, end
  body:
    bit.print_dec_uint 16, idx
    stl.output '\\n'
    bit.add 16, idx, two
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"6\n\0",
    out_bytes=b"2\n4\n6\n",
)

# 0120 odds_up_to_n — start 1, step 2
A(
    "0120",
    "odds_up_to_n",
    "Odds Up To N",
    unsigned=True,
    value_data=["limit: bit.vec 16, 0", "idx: bit.vec 16, 1", "two: bit.vec 16, 2"],
    main_body="""
def main @ loop, body, end < limit, idx, two {
    stl.startup
    read_decimal 16, limit
  loop:
    bit.cmp 16, idx, limit, body, body, end
  body:
    bit.print_dec_uint 16, idx
    stl.output '\\n'
    bit.add 16, idx, two
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"7\n\0",
    out_bytes=b"1\n3\n5\n7\n",
)

# 0121 multiples_of_3_to_n — start 3, step 3
A(
    "0121",
    "multiples_of_3_to_n",
    "Multiples Of 3 To N",
    unsigned=True,
    value_data=["limit: bit.vec 16, 0", "idx: bit.vec 16, 3", "step: bit.vec 16, 3"],
    main_body="""
def main @ loop, body, end < limit, idx, step {
    stl.startup
    read_decimal 16, limit
  loop:
    bit.cmp 16, idx, limit, body, body, end
  body:
    bit.print_dec_uint 16, idx
    stl.output '\\n'
    bit.add 16, idx, step
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"10\n\0",
    out_bytes=b"3\n6\n9\n",
)

# 0122 multiples_of_5_to_n — start 5, step 5
A(
    "0122",
    "multiples_of_5_to_n",
    "Multiples Of 5 To N",
    unsigned=True,
    value_data=["limit: bit.vec 16, 0", "idx: bit.vec 16, 5", "step: bit.vec 16, 5"],
    main_body="""
def main @ loop, body, end < limit, idx, step {
    stl.startup
    read_decimal 16, limit
  loop:
    bit.cmp 16, idx, limit, body, body, end
  body:
    bit.print_dec_uint 16, idx
    stl.output '\\n'
    bit.add 16, idx, step
    ;loop
  end:
    stl.loop
}
""",
    in_bytes=b"12\n\0",
    out_bytes=b"5\n10\n",
)

# 0133 pow_base2 — double 1, N times
A(
    "0133",
    "pow_base2",
    "Pow Base 2",
    unsigned=True,
    value_data=["ctr: bit.vec 16, 0", "result: bit.vec 16, 1", "tmp: bit.vec 16, 0"],
    main_body="""
def main @ loop, end < ctr, result, tmp {
    stl.startup
    read_decimal 16, ctr
  loop:
    bit.if0 16, ctr, end
    bit.mov 16, tmp, result
    bit.add 16, result, tmp
    bit.dec 16, ctr
    ;loop
  end:
    bit.print_dec_uint 16, result
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"5\n\0",
    out_bytes=b"32\n",
)

# 0134 pow_base3 — multiply 1 by 3, N times
A(
    "0134",
    "pow_base3",
    "Pow Base 3",
    unsigned=True,
    mul=True,
    value_data=["ctr: bit.vec 16, 0", "result: bit.vec 16, 1", "tmp: bit.vec 16, 0", "three: bit.vec 16, 3"],
    main_body="""
def main @ loop, end < ctr, result, tmp, three {
    stl.startup
    read_decimal 16, ctr
  loop:
    bit.if0 16, ctr, end
    mul_into 16, tmp, result, three
    bit.mov 16, result, tmp
    bit.dec 16, ctr
    ;loop
  end:
    bit.print_dec_uint 16, result
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"3\n\0",
    out_bytes=b"27\n",
)

# 0128 sum_of_n_inputs
A(
    "0128",
    "sum_of_n_inputs",
    "Sum Of N Inputs",
    unsigned=True,
    value_data=["count: bit.vec 16, 0", "x: bit.vec 16, 0", "sum: bit.vec 16, 0"],
    main_body="""
def main @ loop, end < count, x, sum {
    stl.startup
    read_decimal 16, count
    bit.zero 16, sum
  loop:
    bit.if0 16, count, end
    read_decimal 16, x
    bit.add 16, sum, x
    bit.dec 16, count
    ;loop
  end:
    bit.print_dec_uint 16, sum
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"3\n10\n20\n12\n\0",
    out_bytes=b"42\n",
)

# 0129 max_of_n_inputs — read first, then fold the rest
A(
    "0129",
    "max_of_n_inputs",
    "Max Of N Inputs",
    unsigned=True,
    extra_helpers=[MAX_INTO],
    value_data=["count: bit.vec 16, 0", "x: bit.vec 16, 0", "mx: bit.vec 16, 0"],
    main_body="""
def main @ loop, end < count, x, mx {
    stl.startup
    read_decimal 16, count
    read_decimal 16, mx
    bit.dec 16, count
  loop:
    bit.if0 16, count, end
    read_decimal 16, x
    max_into 16, mx, mx, x
    bit.dec 16, count
    ;loop
  end:
    bit.print_dec_uint 16, mx
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"3\n10\n40\n20\n\0",
    out_bytes=b"40\n",
)

# 0130 min_of_n_inputs
A(
    "0130",
    "min_of_n_inputs",
    "Min Of N Inputs",
    unsigned=True,
    extra_helpers=[MIN_INTO],
    value_data=["count: bit.vec 16, 0", "x: bit.vec 16, 0", "mn: bit.vec 16, 0"],
    main_body="""
def main @ loop, end < count, x, mn {
    stl.startup
    read_decimal 16, count
    read_decimal 16, mn
    bit.dec 16, count
  loop:
    bit.if0 16, count, end
    read_decimal 16, x
    min_into 16, mn, mn, x
    bit.dec 16, count
    ;loop
  end:
    bit.print_dec_uint 16, mn
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"3\n10\n40\n20\n\0",
    out_bytes=b"10\n",
)

# 0131 avg_of_n_inputs — preserve count for the final division
A(
    "0131",
    "avg_of_n_inputs",
    "Avg Of N Inputs",
    unsigned=True,
    value_data=[
        "count: bit.vec 16, 0",
        "ctr: bit.vec 16, 0",
        "x: bit.vec 16, 0",
        "sum: bit.vec 16, 0",
        "q: bit.vec 16, 0",
        "r: bit.vec 16, 0",
    ],
    main_body="""
def main @ loop, end < count, ctr, x, sum, q, r {
    stl.startup
    read_decimal 16, count
    bit.zero 16, sum
    bit.mov 16, ctr, count
  loop:
    bit.if0 16, ctr, end
    read_decimal 16, x
    bit.add 16, sum, x
    bit.dec 16, ctr
    ;loop
  end:
    bit.div 16, sum, count, q, r
    bit.print_dec_uint 16, q
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"3\n10\n20\n12\n\0",
    out_bytes=b"14\n",
)

print("---")
print("BATCH 5 DONE")

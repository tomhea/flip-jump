"""Catalog category: geometry — integer coordinate/shape arithmetic.

20 programs built on the shared decimal-I/O scaffolding in `catalog_arith`:
read_decimal / read_signed_decimal for input, mul_into (repeated addition) for
unsigned products, bit.div / bit.idiv for floor / signed division, and a local
`signed_mul_into` helper for signed products (multiplies magnitudes, then
applies the combined sign — so the repeated-addition loop count stays small
even when an operand is negative).

Deferred (7, reported separately, not implemented here):
  - manhattan_distance, chebyshev_distance   : CATALOG desc contains a literal
    `|`, which `catalog_desc` (and the emit header check) truncate; the rules
    forbid editing the shared scripts to work around it.
  - euclidean_distance_floor                 : non-ASCII desc (`≤`, `²`) and
    needs integer sqrt (deferred class).
  - signed_triangle_area_2x, circle_area_approx,
    circle_circumference_approx,
    counts_inside_unit_circle_grid_3x3        : non-ASCII desc
    (`×` / `π·²` / `∈`); deferred per the no-shared-script-edit rule.

Run from the repo root:  python scripts/cat_geometry.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog_arith import emit  # noqa: E402

# dst[:n] = a[:n] * b[:n] for signed values. Magnitudes are multiplied by
# repeated addition (so the loop runs |b| times, which the callers keep small),
# and the sign of the result is the XOR of the two operand signs. Inputs are
# left untouched (the helper works on private magnitude copies).
SIGNED_MUL_INTO = """
// dst[:n] = a[:n] * b[:n] (signed; magnitudes added |b| times, b kept small).
def signed_mul_into n, dst, a, b @ chk_b, do_mul, neg_done, end < smul_a, smul_cnt, smul_neg {
    bit.zero n, dst
    bit.zero smul_neg
    bit.mov n, smul_a, a
    bit.mov n, smul_cnt, b
    bit.if0 a + (n-1)*dw, chk_b
    bit.not smul_neg
    bit.neg n, smul_a
  chk_b:
    bit.if0 b + (n-1)*dw, do_mul
    bit.not smul_neg
    bit.neg n, smul_cnt
  do_mul:
    bit.if0 n, smul_cnt, neg_done
    bit.add n, dst, smul_a
    bit.dec n, smul_cnt
    ;do_mul
  neg_done:
    bit.if0 smul_neg, end
    bit.neg n, dst
  end:
}
""".strip()

SIGNED_MUL_DATA = ["smul_a: bit.vec 16, 0", "smul_cnt: bit.vec 16, 0", "smul_neg: bit.bit"]


def G(nnnn, slug, name, **kw):
    emit("geometry", nnnn, slug, name, **kw)


# ---------------------------------------------------------------------------
# Signed vector products (dot / cross) and signed slope.
# ---------------------------------------------------------------------------

# 0573 dot_product_2d — a*c + b*d (signed)
G(
    "0573",
    "dot_product_2d",
    "Dot Product 2D",
    signed=True,
    extra_helpers=[SIGNED_MUL_INTO],
    value_data=[
        "a: bit.vec 16, 0",
        "b: bit.vec 16, 0",
        "c: bit.vec 16, 0",
        "d: bit.vec 16, 0",
        "term: bit.vec 16, 0",
        "acc: bit.vec 16, 0",
    ],
    extra_data=SIGNED_MUL_DATA,
    main_body="""
def main < a, b, c, d, term, acc {
    stl.startup
    read_signed_decimal 16, a
    read_signed_decimal 16, b
    read_signed_decimal 16, c
    read_signed_decimal 16, d
    signed_mul_into 16, acc, a, c
    signed_mul_into 16, term, b, d
    bit.add 16, acc, term
    bit.print_dec_int 16, acc
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"1\n2\n3\n4\n\0",
    out_bytes=b"11\n",
)

# 0574 cross_product_2d_scalar — a*d - b*c (signed)
G(
    "0574",
    "cross_product_2d_scalar",
    "Cross Product 2D Scalar",
    signed=True,
    extra_helpers=[SIGNED_MUL_INTO],
    value_data=[
        "a: bit.vec 16, 0",
        "b: bit.vec 16, 0",
        "c: bit.vec 16, 0",
        "d: bit.vec 16, 0",
        "term: bit.vec 16, 0",
        "acc: bit.vec 16, 0",
    ],
    extra_data=SIGNED_MUL_DATA,
    main_body="""
def main < a, b, c, d, term, acc {
    stl.startup
    read_signed_decimal 16, a
    read_signed_decimal 16, b
    read_signed_decimal 16, c
    read_signed_decimal 16, d
    signed_mul_into 16, acc, a, d
    signed_mul_into 16, term, b, c
    bit.sub 16, acc, term
    bit.print_dec_int 16, acc
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"1\n2\n3\n4\n\0",
    out_bytes=b"-2\n",
)

# 0595 slope_int_or_undefined — undefined if x1==x2, else (y2-y1)/(x2-x1)
G(
    "0595",
    "slope_int_or_undefined",
    "Slope Int Or Undefined",
    signed=True,
    value_data=[
        "x1: bit.vec 16, 0",
        "y1: bit.vec 16, 0",
        "x2: bit.vec 16, 0",
        "y2: bit.vec 16, 0",
        "q: bit.vec 16, 0",
        "r: bit.vec 16, 0",
    ],
    main_body="""
def main @ divide, undefined, done < x1, y1, x2, y2, q, r {
    stl.startup
    read_signed_decimal 16, x1
    read_signed_decimal 16, y1
    read_signed_decimal 16, x2
    read_signed_decimal 16, y2
    bit.cmp 16, x1, x2, divide, undefined, divide
  divide:
    bit.sub 16, y2, y1
    bit.sub 16, x2, x1
    bit.idiv 16, y2, x2, q, r
    bit.print_dec_int 16, q
    ;done
  undefined:
    stl.output "undefined"
  done:
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"1\n2\n3\n8\n\0",
    out_bytes=b"3\n",
)

# ---------------------------------------------------------------------------
# Unsigned areas / perimeters.
# ---------------------------------------------------------------------------

# 0581 rectangle_area — width * height
G(
    "0581",
    "rectangle_area",
    "Rectangle Area",
    unsigned=True,
    mul=True,
    value_data=["width: bit.vec 16, 0", "height: bit.vec 16, 0", "area: bit.vec 16, 0"],
    main_body="""
def main < width, height, area {
    stl.startup
    read_decimal 16, width
    read_decimal 16, height
    mul_into 16, area, width, height
    bit.print_dec_uint 16, area
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"4\n7\n\0",
    out_bytes=b"28\n",
)

# 0582 rectangle_perimeter — 2 * (width + height)
G(
    "0582",
    "rectangle_perimeter",
    "Rectangle Perimeter",
    unsigned=True,
    value_data=["width: bit.vec 16, 0", "height: bit.vec 16, 0", "perim: bit.vec 16, 0"],
    main_body="""
def main < width, height, perim {
    stl.startup
    read_decimal 16, width
    read_decimal 16, height
    bit.mov 16, perim, width
    bit.add 16, perim, height
    bit.add 16, perim, perim
    bit.print_dec_uint 16, perim
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"4\n7\n\0",
    out_bytes=b"22\n",
)

# 0585 square_perimeter — 4 * side
G(
    "0585",
    "square_perimeter",
    "Square Perimeter",
    unsigned=True,
    value_data=["side: bit.vec 16, 0", "perim: bit.vec 16, 0"],
    main_body="""
def main < side, perim {
    stl.startup
    read_decimal 16, side
    bit.mov 16, perim, side
    bit.add 16, perim, side
    bit.add 16, perim, perim
    bit.print_dec_uint 16, perim
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"5\n\0",
    out_bytes=b"20\n",
)

# 0586 cube_surface_area — 6 * side * side
G(
    "0586",
    "cube_surface_area",
    "Cube Surface Area",
    unsigned=True,
    mul=True,
    value_data=["side: bit.vec 16, 0", "sq: bit.vec 16, 0", "area: bit.vec 16, 0", "six: bit.vec 16, 6"],
    main_body="""
def main < side, sq, area, six {
    stl.startup
    read_decimal 16, side
    mul_into 16, sq, side, side
    mul_into 16, area, sq, six
    bit.print_dec_uint 16, area
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"3\n\0",
    out_bytes=b"54\n",
)

# 0575 midpoint_2d — floor((x1+x2)/2) and floor((y1+y2)/2)
G(
    "0575",
    "midpoint_2d",
    "Midpoint 2D",
    unsigned=True,
    value_data=[
        "x1: bit.vec 16, 0",
        "y1: bit.vec 16, 0",
        "x2: bit.vec 16, 0",
        "y2: bit.vec 16, 0",
        "two: bit.vec 16, 2",
        "q: bit.vec 16, 0",
        "r: bit.vec 16, 0",
    ],
    main_body="""
def main < x1, y1, x2, y2, two, q, r {
    stl.startup
    read_decimal 16, x1
    read_decimal 16, y1
    read_decimal 16, x2
    read_decimal 16, y2
    bit.add 16, x1, x2
    bit.div 16, x1, two, q, r
    bit.print_dec_uint 16, q
    stl.output ' '
    bit.add 16, y1, y2
    bit.div 16, y1, two, q, r
    bit.print_dec_uint 16, q
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"2\n4\n6\n10\n\0",
    out_bytes=b"4 7\n",
)

# ---------------------------------------------------------------------------
# Point / coordinate predicates (print 1\n or 0\n).
# ---------------------------------------------------------------------------

# 0576 is_origin — 1 if x==0 and y==0
G(
    "0576",
    "is_origin",
    "Is Origin",
    unsigned=True,
    value_data=["x: bit.vec 16, 0", "y: bit.vec 16, 0"],
    main_body="""
def main @ no, done < x, y {
    stl.startup
    read_decimal 16, x
    read_decimal 16, y
    bit.if1 16, x, no
    bit.if1 16, y, no
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"0\n0\n\0",
    out_bytes=b"1\n",
)

# 0577 is_on_x_axis — reads x then y; 1 if y==0
G(
    "0577",
    "is_on_x_axis",
    "Is On X Axis",
    unsigned=True,
    value_data=["x: bit.vec 16, 0", "y: bit.vec 16, 0"],
    main_body="""
def main @ yes, done < x, y {
    stl.startup
    read_decimal 16, x
    read_decimal 16, y
    bit.if0 16, y, yes
    stl.output "0\\n"
    ;done
  yes:
    stl.output "1\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"5\n0\n\0",
    out_bytes=b"1\n",
)

# 0578 is_on_y_axis — reads x then y; 1 if x==0
G(
    "0578",
    "is_on_y_axis",
    "Is On Y Axis",
    unsigned=True,
    value_data=["x: bit.vec 16, 0", "y: bit.vec 16, 0"],
    main_body="""
def main @ yes, done < x, y {
    stl.startup
    read_decimal 16, x
    read_decimal 16, y
    bit.if0 16, x, yes
    stl.output "0\\n"
    ;done
  yes:
    stl.output "1\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"0\n7\n\0",
    out_bytes=b"1\n",
)

# 0587 is_point_inside_rect — xmin<=x<=xmax and ymin<=y<=ymax
G(
    "0587",
    "is_point_inside_rect",
    "Is Point Inside Rect",
    unsigned=True,
    value_data=[
        "px: bit.vec 16, 0",
        "py: bit.vec 16, 0",
        "xmin: bit.vec 16, 0",
        "ymin: bit.vec 16, 0",
        "xmax: bit.vec 16, 0",
        "ymax: bit.vec 16, 0",
    ],
    main_body="""
def main @ check2, check3, check4, yes, no, done < px, py, xmin, ymin, xmax, ymax {
    stl.startup
    read_decimal 16, px
    read_decimal 16, py
    read_decimal 16, xmin
    read_decimal 16, ymin
    read_decimal 16, xmax
    read_decimal 16, ymax
    bit.cmp 16, px, xmin, no, check2, check2
  check2:
    bit.cmp 16, px, xmax, check3, check3, no
  check3:
    bit.cmp 16, py, ymin, no, check4, check4
  check4:
    bit.cmp 16, py, ymax, yes, yes, no
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"3\n4\n0\n0\n5\n5\n\0",
    out_bytes=b"1\n",
)

# ---------------------------------------------------------------------------
# Distance-squared predicate (unsigned: square the absolute differences).
# ---------------------------------------------------------------------------

# 0588 is_point_inside_circle — (x-cx)^2 + (y-cy)^2 <= r^2
G(
    "0588",
    "is_point_inside_circle",
    "Is Point Inside Circle",
    unsigned=True,
    mul=True,
    extra_helpers=[
        """
// dst[:n] = (a-b)^2 for unsigned a,b (squares the absolute difference).
def abs_diff_sq_into n, dst, a, b @ a_ge_b, b_gt_a, have_diff < absq_d {
    bit.cmp n, a, b, b_gt_a, a_ge_b, a_ge_b
  a_ge_b:
    bit.mov n, absq_d, a
    bit.sub n, absq_d, b
    ;have_diff
  b_gt_a:
    bit.mov n, absq_d, b
    bit.sub n, absq_d, a
  have_diff:
    mul_into n, dst, absq_d, absq_d
}
""".strip()
    ],
    value_data=[
        "px: bit.vec 16, 0",
        "py: bit.vec 16, 0",
        "cx: bit.vec 16, 0",
        "cy: bit.vec 16, 0",
        "r: bit.vec 16, 0",
        "dist: bit.vec 16, 0",
        "tmp: bit.vec 16, 0",
        "rsq: bit.vec 16, 0",
    ],
    extra_data=["absq_d: bit.vec 16, 0"],
    main_body="""
def main @ yes, no, done < px, py, cx, cy, r, dist, tmp, rsq {
    stl.startup
    read_decimal 16, px
    read_decimal 16, py
    read_decimal 16, cx
    read_decimal 16, cy
    read_decimal 16, r
    abs_diff_sq_into 16, dist, px, cx
    abs_diff_sq_into 16, tmp, py, cy
    bit.add 16, dist, tmp
    mul_into 16, rsq, r, r
    bit.cmp 16, dist, rsq, yes, yes, no
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"3\n4\n0\n0\n5\n\0",
    out_bytes=b"1\n",
)

# ---------------------------------------------------------------------------
# Triangle-from-sides classifiers (read a, b, c).
# ---------------------------------------------------------------------------

# 0589 is_right_triangle_from_sides — some permutation has a^2+b^2==c^2
G(
    "0589",
    "is_right_triangle_from_sides",
    "Is Right Triangle From Sides",
    unsigned=True,
    mul=True,
    extra_helpers=[
        """
// Jump to `yes` if leg1*leg1 + leg2*leg2 == hyp*hyp (a right triangle).
def hyp_check n, leg1, leg2, hyp, yes @ no < hc_a2, hc_b2, hc_c2, hc_sum {
    mul_into n, hc_a2, leg1, leg1
    mul_into n, hc_b2, leg2, leg2
    mul_into n, hc_c2, hyp, hyp
    bit.mov n, hc_sum, hc_a2
    bit.add n, hc_sum, hc_b2
    bit.cmp n, hc_sum, hc_c2, no, yes, no
  no:
}
""".strip()
    ],
    value_data=["a: bit.vec 16, 0", "b: bit.vec 16, 0", "c: bit.vec 16, 0"],
    extra_data=["hc_a2: bit.vec 16, 0", "hc_b2: bit.vec 16, 0", "hc_c2: bit.vec 16, 0", "hc_sum: bit.vec 16, 0"],
    main_body="""
def main @ yes, no, done < a, b, c {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    read_decimal 16, c
    hyp_check 16, a, b, c, yes
    hyp_check 16, a, c, b, yes
    hyp_check 16, b, c, a, yes
  no:
    stl.output "0\\n"
    ;done
  yes:
    stl.output "1\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"4\n5\n3\n\0",
    out_bytes=b"1\n",
)

# 0590 is_isosceles — at least two sides equal
G(
    "0590",
    "is_isosceles",
    "Is Isosceles",
    unsigned=True,
    value_data=["a: bit.vec 16, 0", "b: bit.vec 16, 0", "c: bit.vec 16, 0"],
    main_body="""
def main @ check2, check3, yes, no, done < a, b, c {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    read_decimal 16, c
    bit.cmp 16, a, b, check2, yes, check2
  check2:
    bit.cmp 16, b, c, check3, yes, check3
  check3:
    bit.cmp 16, a, c, no, yes, no
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"5\n5\n8\n\0",
    out_bytes=b"1\n",
)

# 0591 is_equilateral — all three sides equal
G(
    "0591",
    "is_equilateral",
    "Is Equilateral",
    unsigned=True,
    value_data=["a: bit.vec 16, 0", "b: bit.vec 16, 0", "c: bit.vec 16, 0"],
    main_body="""
def main @ check2, yes, no, done < a, b, c {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    read_decimal 16, c
    bit.cmp 16, a, b, no, check2, no
  check2:
    bit.cmp 16, b, c, no, yes, no
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"6\n6\n6\n\0",
    out_bytes=b"1\n",
)

# 0592 is_scalene — all three sides distinct
G(
    "0592",
    "is_scalene",
    "Is Scalene",
    unsigned=True,
    value_data=["a: bit.vec 16, 0", "b: bit.vec 16, 0", "c: bit.vec 16, 0"],
    main_body="""
def main @ check2, check3, yes, no, done < a, b, c {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    read_decimal 16, c
    bit.cmp 16, a, b, check2, no, check2
  check2:
    bit.cmp 16, b, c, check3, no, check3
  check3:
    bit.cmp 16, a, c, yes, no, yes
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"3\n4\n5\n\0",
    out_bytes=b"1\n",
)

# ---------------------------------------------------------------------------
# Vector relationship checks (signed dot / cross == 0).
# ---------------------------------------------------------------------------

# 0593 perpendicular_vectors_check — dot product a*c + b*d == 0
G(
    "0593",
    "perpendicular_vectors_check",
    "Perpendicular Vectors Check",
    signed=True,
    extra_helpers=[SIGNED_MUL_INTO],
    value_data=[
        "a: bit.vec 16, 0",
        "b: bit.vec 16, 0",
        "c: bit.vec 16, 0",
        "d: bit.vec 16, 0",
        "term: bit.vec 16, 0",
        "acc: bit.vec 16, 0",
    ],
    extra_data=SIGNED_MUL_DATA,
    main_body="""
def main @ yes, done < a, b, c, d, term, acc {
    stl.startup
    read_signed_decimal 16, a
    read_signed_decimal 16, b
    read_signed_decimal 16, c
    read_signed_decimal 16, d
    signed_mul_into 16, acc, a, c
    signed_mul_into 16, term, b, d
    bit.add 16, acc, term
    bit.if0 16, acc, yes
    stl.output "0\\n"
    ;done
  yes:
    stl.output "1\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"1\n2\n2\n-1\n\0",
    out_bytes=b"1\n",
)

# 0594 parallel_vectors_check — cross product a*d - b*c == 0
G(
    "0594",
    "parallel_vectors_check",
    "Parallel Vectors Check",
    signed=True,
    extra_helpers=[SIGNED_MUL_INTO],
    value_data=[
        "a: bit.vec 16, 0",
        "b: bit.vec 16, 0",
        "c: bit.vec 16, 0",
        "d: bit.vec 16, 0",
        "term: bit.vec 16, 0",
        "acc: bit.vec 16, 0",
    ],
    extra_data=SIGNED_MUL_DATA,
    main_body="""
def main @ yes, done < a, b, c, d, term, acc {
    stl.startup
    read_signed_decimal 16, a
    read_signed_decimal 16, b
    read_signed_decimal 16, c
    read_signed_decimal 16, d
    signed_mul_into 16, acc, a, d
    signed_mul_into 16, term, b, c
    bit.sub 16, acc, term
    bit.if0 16, acc, yes
    stl.output "0\\n"
    ;done
  yes:
    stl.output "1\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"1\n2\n2\n4\n\0",
    out_bytes=b"1\n",
)

# ---------------------------------------------------------------------------
# Collinearity of three points (signed cross of difference vectors).
# ---------------------------------------------------------------------------

# 0579 is_collinear_3 — (x2-x1)*(y3-y1) - (y2-y1)*(x3-x1) == 0
G(
    "0579",
    "is_collinear_3",
    "Is Collinear 3",
    signed=True,
    extra_helpers=[SIGNED_MUL_INTO],
    value_data=[
        "x1: bit.vec 16, 0",
        "y1: bit.vec 16, 0",
        "x2: bit.vec 16, 0",
        "y2: bit.vec 16, 0",
        "x3: bit.vec 16, 0",
        "y3: bit.vec 16, 0",
        "dx2: bit.vec 16, 0",
        "dy2: bit.vec 16, 0",
        "dx3: bit.vec 16, 0",
        "dy3: bit.vec 16, 0",
        "term: bit.vec 16, 0",
        "acc: bit.vec 16, 0",
    ],
    extra_data=SIGNED_MUL_DATA,
    main_body="""
def main @ yes, done < x1, y1, x2, y2, x3, y3, dx2, dy2, dx3, dy3, term, acc {
    stl.startup
    read_signed_decimal 16, x1
    read_signed_decimal 16, y1
    read_signed_decimal 16, x2
    read_signed_decimal 16, y2
    read_signed_decimal 16, x3
    read_signed_decimal 16, y3
    bit.mov 16, dx2, x2
    bit.sub 16, dx2, x1
    bit.mov 16, dy2, y2
    bit.sub 16, dy2, y1
    bit.mov 16, dx3, x3
    bit.sub 16, dx3, x1
    bit.mov 16, dy3, y3
    bit.sub 16, dy3, y1
    signed_mul_into 16, acc, dx2, dy3
    signed_mul_into 16, term, dy2, dx3
    bit.sub 16, acc, term
    bit.if0 16, acc, yes
    stl.output "0\\n"
    ;done
  yes:
    stl.output "1\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"0\n0\n1\n1\n2\n2\n\0",
    out_bytes=b"1\n",
)

print("---")
print("CAT_GEOMETRY DONE")

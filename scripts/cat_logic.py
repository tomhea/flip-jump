"""Phase 3: logic — boolean / gate demos (22 programs).

and_gate, or_gate, xor_gate, nand_gate, nor_gate, xnor_gate, not_gate, and_3,
or_3, half_adder, logic_implies, boolean_xor_three, boolean_majority_three,
boolean_exactly_one, boolean_exactly_two, multiplexer_2to1, demultiplexer_1to2,
mux_4to1, encoder_4to2, decoder_2to4, full_adder, nand_universality_or.

Each input is an ASCII bit `0`/`1`, one per line. A byte is read with
`bit.input` and the value is bit 0 of that byte (ASCII '0'=0x30, '1'=0x31 differ
only in bit 0), copied into a single bit with `bit.mov`; the trailing `\\n` byte
is then consumed. Results are single bits printed as ASCII '0'/'1' via the
print helpers (`_nl` adds `\\n`, `_sp` adds a space, `_raw` adds nothing).

Run from the repo root:  python scripts/cat_logic.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog_arith import emit  # noqa: E402

# Read one ASCII bit line ('0'/'1' then '\n') into the single bit dst; consume the newline.
READ_ASCII_BIT = """
// Read one ASCII bit line ('0'/'1' then '\\n') into the single bit dst, then eat the '\\n'.
def read_ascii_bit dst, ch {
    bit.input ch
    bit.mov dst, ch
    bit.input ch
}
""".strip()

# Print a single bit as ASCII, with a trailing newline.
PRINT_BIT_NL = """
// Print the single bit b as ASCII '0'/'1' followed by '\\n'.
def print_bit_nl b @ zero, one, done {
    bit.if b, zero, one
  zero:
    stl.output "0\\n"
    ;done
  one:
    stl.output "1\\n"
  done:
}
""".strip()

# Print a single bit as ASCII, with a trailing space.
PRINT_BIT_SP = """
// Print the single bit b as ASCII '0'/'1' followed by a space.
def print_bit_sp b @ zero, one, done {
    bit.if b, zero, one
  zero:
    stl.output "0 "
    ;done
  one:
    stl.output "1 "
  done:
}
""".strip()

# Print a single bit as ASCII, no separator.
PRINT_BIT_RAW = """
// Print the single bit b as a bare ASCII '0'/'1' (no separator).
def print_bit_raw b @ zero, one, done {
    bit.if b, zero, one
  zero:
    stl.output '0'
    ;done
  one:
    stl.output '1'
  done:
}
""".strip()

# r = a AND b (all single bits; r may equal a or b only if distinct from the other).
AND_INTO = """
// r = a AND b (single bits). r must be distinct from a and b.
def and_into r, a, b {
    bit.mov r, a
    bit.and r, b
}
""".strip()

# r = a OR b (single bits). r must be distinct from a and b.
OR_INTO = """
// r = a OR b (single bits). r must be distinct from a and b.
def or_into r, a, b {
    bit.mov r, a
    bit.or r, b
}
""".strip()

# r = a XOR b (single bits). r must be distinct from a and b.
XOR_INTO = """
// r = a XOR b (single bits). r must be distinct from a and b.
def xor_into r, a, b {
    bit.mov r, a
    bit.xor r, b
}
""".strip()

# r = a NAND b (single bits). r must be distinct from a and b.
NAND_INTO = """
// r = a NAND b = NOT (a AND b) (single bits). r must be distinct from a and b.
def nand_into r, a, b {
    bit.mov r, a
    bit.and r, b
    bit.not r
}
""".strip()

# count[:n] += 1 for each of the listed single bits that is set; here just one helper add.
ADD_BIT_INTO = """
// Add 1 to count[:n] if the single bit b is set.
def add_bit_into n, count, b @ end {
    bit.if0 b, end
    bit.inc n, count
  end:
}
""".strip()


def L(nnnn, slug, name, **kw):
    emit("logic", nnnn, slug, name, **kw)


# Shared scratch for the two-input single-result gates.
TWO_IN = ["ch: bit.vec 8, 0", "va: bit.bit", "vb: bit.bit", "res: bit.bit"]
THREE_IN = ["ch: bit.vec 8, 0", "va: bit.bit", "vb: bit.bit", "vc: bit.bit", "res: bit.bit"]


# 0091 and_gate
L(
    "0091",
    "and_gate",
    "And Gate",
    extra_helpers=[READ_ASCII_BIT, PRINT_BIT_NL, AND_INTO],
    value_data=TWO_IN,
    main_body="""
def main < ch, va, vb, res {
    stl.startup
    read_ascii_bit va, ch
    read_ascii_bit vb, ch
    and_into res, va, vb
    print_bit_nl res
    stl.loop
}
""",
    in_bytes=b"1\n1\n",
    out_bytes=b"1\n",
)

# 0092 or_gate
L(
    "0092",
    "or_gate",
    "Or Gate",
    extra_helpers=[READ_ASCII_BIT, PRINT_BIT_NL, OR_INTO],
    value_data=TWO_IN,
    main_body="""
def main < ch, va, vb, res {
    stl.startup
    read_ascii_bit va, ch
    read_ascii_bit vb, ch
    or_into res, va, vb
    print_bit_nl res
    stl.loop
}
""",
    in_bytes=b"1\n0\n",
    out_bytes=b"1\n",
)

# 0093 xor_gate
L(
    "0093",
    "xor_gate",
    "Xor Gate",
    extra_helpers=[READ_ASCII_BIT, PRINT_BIT_NL, XOR_INTO],
    value_data=TWO_IN,
    main_body="""
def main < ch, va, vb, res {
    stl.startup
    read_ascii_bit va, ch
    read_ascii_bit vb, ch
    xor_into res, va, vb
    print_bit_nl res
    stl.loop
}
""",
    in_bytes=b"1\n0\n",
    out_bytes=b"1\n",
)

# 0094 nand_gate
L(
    "0094",
    "nand_gate",
    "Nand Gate",
    extra_helpers=[READ_ASCII_BIT, PRINT_BIT_NL, NAND_INTO],
    value_data=TWO_IN,
    main_body="""
def main < ch, va, vb, res {
    stl.startup
    read_ascii_bit va, ch
    read_ascii_bit vb, ch
    nand_into res, va, vb
    print_bit_nl res
    stl.loop
}
""",
    in_bytes=b"1\n1\n",
    out_bytes=b"0\n",
)

# 0095 nor_gate
L(
    "0095",
    "nor_gate",
    "Nor Gate",
    extra_helpers=[READ_ASCII_BIT, PRINT_BIT_NL, OR_INTO],
    value_data=TWO_IN,
    main_body="""
def main < ch, va, vb, res {
    stl.startup
    read_ascii_bit va, ch
    read_ascii_bit vb, ch
    or_into res, va, vb
    bit.not res
    print_bit_nl res
    stl.loop
}
""",
    in_bytes=b"0\n0\n",
    out_bytes=b"1\n",
)

# 0096 xnor_gate
L(
    "0096",
    "xnor_gate",
    "Xnor Gate",
    extra_helpers=[READ_ASCII_BIT, PRINT_BIT_NL, XOR_INTO],
    value_data=TWO_IN,
    main_body="""
def main < ch, va, vb, res {
    stl.startup
    read_ascii_bit va, ch
    read_ascii_bit vb, ch
    xor_into res, va, vb
    bit.not res
    print_bit_nl res
    stl.loop
}
""",
    in_bytes=b"1\n1\n",
    out_bytes=b"1\n",
)

# 0097 not_gate
L(
    "0097",
    "not_gate",
    "Not Gate",
    extra_helpers=[READ_ASCII_BIT, PRINT_BIT_NL],
    value_data=["ch: bit.vec 8, 0", "va: bit.bit"],
    main_body="""
def main < ch, va {
    stl.startup
    read_ascii_bit va, ch
    bit.not va
    print_bit_nl va
    stl.loop
}
""",
    in_bytes=b"0\n",
    out_bytes=b"1\n",
)

# 0098 and_3
L(
    "0098",
    "and_3",
    "And 3",
    extra_helpers=[READ_ASCII_BIT, PRINT_BIT_NL, AND_INTO],
    value_data=THREE_IN,
    main_body="""
def main < ch, va, vb, vc, res {
    stl.startup
    read_ascii_bit va, ch
    read_ascii_bit vb, ch
    read_ascii_bit vc, ch
    and_into res, va, vb
    bit.and res, vc
    print_bit_nl res
    stl.loop
}
""",
    in_bytes=b"1\n1\n1\n",
    out_bytes=b"1\n",
)

# 0099 or_3
L(
    "0099",
    "or_3",
    "Or 3",
    extra_helpers=[READ_ASCII_BIT, PRINT_BIT_NL, OR_INTO],
    value_data=THREE_IN,
    main_body="""
def main < ch, va, vb, vc, res {
    stl.startup
    read_ascii_bit va, ch
    read_ascii_bit vb, ch
    read_ascii_bit vc, ch
    or_into res, va, vb
    bit.or res, vc
    print_bit_nl res
    stl.loop
}
""",
    in_bytes=b"0\n0\n1\n",
    out_bytes=b"1\n",
)

# 0100 half_adder — sum = a XOR b, carry = a AND b, on two lines.
L(
    "0100",
    "half_adder",
    "Half Adder",
    extra_helpers=[READ_ASCII_BIT, PRINT_BIT_NL, XOR_INTO, AND_INTO],
    value_data=["ch: bit.vec 8, 0", "va: bit.bit", "vb: bit.bit", "sum: bit.bit", "carry: bit.bit"],
    main_body="""
def main < ch, va, vb, sum, carry {
    stl.startup
    read_ascii_bit va, ch
    read_ascii_bit vb, ch
    xor_into sum, va, vb
    and_into carry, va, vb
    print_bit_nl sum
    print_bit_nl carry
    stl.loop
}
""",
    in_bytes=b"1\n1\n",
    out_bytes=b"0\n1\n",
)

# 0905 logic_implies — (NOT A) OR B.
L(
    "0905",
    "logic_implies",
    "Logic Implies",
    extra_helpers=[READ_ASCII_BIT, PRINT_BIT_NL, OR_INTO],
    value_data=["ch: bit.vec 8, 0", "va: bit.bit", "vb: bit.bit", "res: bit.bit"],
    main_body="""
def main < ch, va, vb, res {
    stl.startup
    read_ascii_bit va, ch
    read_ascii_bit vb, ch
    bit.not va
    or_into res, va, vb
    print_bit_nl res
    stl.loop
}
""",
    in_bytes=b"1\n0\n",
    out_bytes=b"0\n",
)

# 0906 boolean_xor_three — a XOR b XOR c.
L(
    "0906",
    "boolean_xor_three",
    "Boolean Xor Three",
    extra_helpers=[READ_ASCII_BIT, PRINT_BIT_NL, XOR_INTO],
    value_data=THREE_IN,
    main_body="""
def main < ch, va, vb, vc, res {
    stl.startup
    read_ascii_bit va, ch
    read_ascii_bit vb, ch
    read_ascii_bit vc, ch
    xor_into res, va, vb
    bit.xor res, vc
    print_bit_nl res
    stl.loop
}
""",
    in_bytes=b"1\n1\n1\n",
    out_bytes=b"1\n",
)

# 0907 boolean_majority_three — at least two of three set.
L(
    "0907",
    "boolean_majority_three",
    "Boolean Majority Three",
    extra_helpers=[READ_ASCII_BIT, ADD_BIT_INTO],
    value_data=[
        "ch: bit.vec 8, 0",
        "va: bit.bit",
        "vb: bit.bit",
        "vc: bit.bit",
        "count: bit.vec 8, 0",
        "two: bit.vec 8, 2",
    ],
    main_body="""
def main @ yes, no, done < ch, va, vb, vc, count, two {
    stl.startup
    read_ascii_bit va, ch
    read_ascii_bit vb, ch
    read_ascii_bit vc, ch
    bit.zero 8, count
    add_bit_into 8, count, va
    add_bit_into 8, count, vb
    add_bit_into 8, count, vc
    bit.cmp 8, count, two, no, yes, yes
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"1\n1\n0\n",
    out_bytes=b"1\n",
)

# 0908 boolean_exactly_one — popcount == 1.
L(
    "0908",
    "boolean_exactly_one",
    "Boolean Exactly One",
    extra_helpers=[READ_ASCII_BIT, ADD_BIT_INTO],
    value_data=[
        "ch: bit.vec 8, 0",
        "va: bit.bit",
        "vb: bit.bit",
        "vc: bit.bit",
        "count: bit.vec 8, 0",
        "one: bit.vec 8, 1",
    ],
    main_body="""
def main @ yes, no, done < ch, va, vb, vc, count, one {
    stl.startup
    read_ascii_bit va, ch
    read_ascii_bit vb, ch
    read_ascii_bit vc, ch
    bit.zero 8, count
    add_bit_into 8, count, va
    add_bit_into 8, count, vb
    add_bit_into 8, count, vc
    bit.cmp 8, count, one, no, yes, no
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"1\n0\n0\n",
    out_bytes=b"1\n",
)

# 0909 boolean_exactly_two — popcount == 2.
L(
    "0909",
    "boolean_exactly_two",
    "Boolean Exactly Two",
    extra_helpers=[READ_ASCII_BIT, ADD_BIT_INTO],
    value_data=[
        "ch: bit.vec 8, 0",
        "va: bit.bit",
        "vb: bit.bit",
        "vc: bit.bit",
        "count: bit.vec 8, 0",
        "two: bit.vec 8, 2",
    ],
    main_body="""
def main @ yes, no, done < ch, va, vb, vc, count, two {
    stl.startup
    read_ascii_bit va, ch
    read_ascii_bit vb, ch
    read_ascii_bit vc, ch
    bit.zero 8, count
    add_bit_into 8, count, va
    add_bit_into 8, count, vb
    add_bit_into 8, count, vc
    bit.cmp 8, count, two, no, yes, no
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"1\n1\n0\n",
    out_bytes=b"1\n",
)

# 0910 multiplexer_2to1 — select d0 if sel==0 else d1.
L(
    "0910",
    "multiplexer_2to1",
    "Multiplexer 2to1",
    extra_helpers=[READ_ASCII_BIT, PRINT_BIT_NL],
    value_data=["ch: bit.vec 8, 0", "sel: bit.bit", "d0: bit.bit", "d1: bit.bit", "res: bit.bit"],
    main_body="""
def main @ pick0, pick1, done < ch, sel, d0, d1, res {
    stl.startup
    read_ascii_bit sel, ch
    read_ascii_bit d0, ch
    read_ascii_bit d1, ch
    bit.if sel, pick0, pick1
  pick0:
    bit.mov res, d0
    ;done
  pick1:
    bit.mov res, d1
  done:
    print_bit_nl res
    stl.loop
}
""",
    in_bytes=b"1\n0\n1\n",
    out_bytes=b"1\n",
)

# 0911 demultiplexer_1to2 — route data to one of two outputs based on selector.
L(
    "0911",
    "demultiplexer_1to2",
    "Demultiplexer 1to2",
    extra_helpers=[READ_ASCII_BIT, PRINT_BIT_SP, PRINT_BIT_NL],
    value_data=["ch: bit.vec 8, 0", "data: bit.bit", "sel: bit.bit", "y0: bit.bit", "y1: bit.bit"],
    main_body="""
def main @ route0, route1, done < ch, data, sel, y0, y1 {
    stl.startup
    read_ascii_bit data, ch
    read_ascii_bit sel, ch
    bit.zero y0
    bit.zero y1
    bit.if sel, route0, route1
  route0:
    bit.mov y0, data
    ;done
  route1:
    bit.mov y1, data
  done:
    print_bit_sp y0
    print_bit_nl y1
    stl.loop
}
""",
    in_bytes=b"1\n0\n",
    out_bytes=b"1 0\n",
)

# 0912 mux_4to1 — select one of four data bits by a 2-bit selector (s1*2+s0).
L(
    "0912",
    "mux_4to1",
    "Mux 4to1",
    extra_helpers=[READ_ASCII_BIT, PRINT_BIT_NL],
    value_data=[
        "ch: bit.vec 8, 0",
        "s1: bit.bit",
        "s0: bit.bit",
        "d0: bit.bit",
        "d1: bit.bit",
        "d2: bit.bit",
        "d3: bit.bit",
        "res: bit.bit",
    ],
    main_body="""
def main @ hi, lo, p0, p1, p2, p3, done < ch, s1, s0, d0, d1, d2, d3, res {
    stl.startup
    read_ascii_bit s1, ch
    read_ascii_bit s0, ch
    read_ascii_bit d0, ch
    read_ascii_bit d1, ch
    read_ascii_bit d2, ch
    read_ascii_bit d3, ch
    bit.if s1, lo, hi
  lo:
    bit.if s0, p0, p1
  hi:
    bit.if s0, p2, p3
  p0:
    bit.mov res, d0
    ;done
  p1:
    bit.mov res, d1
    ;done
  p2:
    bit.mov res, d2
    ;done
  p3:
    bit.mov res, d3
  done:
    print_bit_nl res
    stl.loop
}
""",
    in_bytes=b"1\n0\n0\n0\n1\n0\n",
    out_bytes=b"1\n",
)

# 0913 encoder_4to2 — one-hot 4 bits to 2-bit position (s1 = b2|b3, s0 = b1|b3).
L(
    "0913",
    "encoder_4to2",
    "Encoder 4to2",
    extra_helpers=[READ_ASCII_BIT, PRINT_BIT_RAW, OR_INTO],
    value_data=[
        "ch: bit.vec 8, 0",
        "b0: bit.bit",
        "b1: bit.bit",
        "b2: bit.bit",
        "b3: bit.bit",
        "s1: bit.bit",
        "s0: bit.bit",
    ],
    main_body="""
def main < ch, b0, b1, b2, b3, s1, s0 {
    stl.startup
    read_ascii_bit b0, ch
    read_ascii_bit b1, ch
    read_ascii_bit b2, ch
    read_ascii_bit b3, ch
    or_into s1, b2, b3
    or_into s0, b1, b3
    print_bit_raw s1
    print_bit_raw s0
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"0\n0\n0\n1\n",
    out_bytes=b"11\n",
)

# 0914 decoder_2to4 — one-hot 4-bit output at position s1*2+s0.
L(
    "0914",
    "decoder_2to4",
    "Decoder 2to4",
    extra_helpers=[READ_ASCII_BIT, PRINT_BIT_RAW],
    value_data=[
        "ch: bit.vec 8, 0",
        "s1: bit.bit",
        "s0: bit.bit",
        "y0: bit.bit",
        "y1: bit.bit",
        "y2: bit.bit",
        "y3: bit.bit",
    ],
    main_body="""
def main @ hi, lo, p0, p1, p2, p3, done < ch, s1, s0, y0, y1, y2, y3 {
    stl.startup
    read_ascii_bit s1, ch
    read_ascii_bit s0, ch
    bit.zero y0
    bit.zero y1
    bit.zero y2
    bit.zero y3
    bit.if s1, lo, hi
  lo:
    bit.if s0, p0, p1
  hi:
    bit.if s0, p2, p3
  p0:
    bit.one y0
    ;done
  p1:
    bit.one y1
    ;done
  p2:
    bit.one y2
    ;done
  p3:
    bit.one y3
  done:
    print_bit_raw y0
    print_bit_raw y1
    print_bit_raw y2
    print_bit_raw y3
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"1\n0\n",
    out_bytes=b"0010\n",
)

# 0915 full_adder — sum = a^b^cin, cout = (a&b) | (cin & (a^b)).
L(
    "0915",
    "full_adder",
    "Full Adder",
    extra_helpers=[READ_ASCII_BIT, PRINT_BIT_SP, PRINT_BIT_NL, XOR_INTO, AND_INTO, OR_INTO],
    value_data=[
        "ch: bit.vec 8, 0",
        "va: bit.bit",
        "vb: bit.bit",
        "cin: bit.bit",
        "axb: bit.bit",
        "sum: bit.bit",
        "ab: bit.bit",
        "cab: bit.bit",
        "cout: bit.bit",
    ],
    main_body="""
def main < ch, va, vb, cin, axb, sum, ab, cab, cout {
    stl.startup
    read_ascii_bit va, ch
    read_ascii_bit vb, ch
    read_ascii_bit cin, ch
    xor_into axb, va, vb
    xor_into sum, axb, cin
    and_into ab, va, vb
    and_into cab, cin, axb
    or_into cout, ab, cab
    print_bit_sp sum
    print_bit_nl cout
    stl.loop
}
""",
    in_bytes=b"1\n1\n0\n",
    out_bytes=b"0 1\n",
)

# 0916 nand_universality_or — OR(a, b) = NAND(NOT a, NOT b) built from NAND only.
L(
    "0916",
    "nand_universality_or",
    "Nand Universality Or",
    extra_helpers=[READ_ASCII_BIT, PRINT_BIT_NL, NAND_INTO],
    value_data=[
        "ch: bit.vec 8, 0",
        "va: bit.bit",
        "vb: bit.bit",
        "na: bit.bit",
        "nb: bit.bit",
        "res: bit.bit",
    ],
    main_body="""
def main < ch, va, vb, na, nb, res {
    stl.startup
    read_ascii_bit va, ch
    read_ascii_bit vb, ch
    nand_into na, va, va
    nand_into nb, vb, vb
    nand_into res, na, nb
    print_bit_nl res
    stl.loop
}
""",
    in_bytes=b"1\n0\n",
    out_bytes=b"1\n",
)

print("---")
print("LOGIC DONE")

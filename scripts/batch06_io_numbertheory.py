"""Phase 3 batch 6: finish io conversions + number_theory primes & divisors.

io (3): dec_to_char, char_to_hex, hex_to_char  (reverse_line still deferred —
needs a byte stack / recursion, built in a later category).
number_theory (13): is_prime_small, first_n_primes, prime_after,
count_primes_to_n, gcd_two, lcm_two, coprime_check, factor_count_small,
divisors_of_n, is_perfect_small, sum_of_divisors_small, is_abundant_small,
is_deficient_small.

Run from the repo root:  python scripts/batch06_io_numbertheory.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog_arith import emit  # noqa: E402

# ---------- number-theory helper macros (shared within the batch) ----------

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

GCD = """
// dst = gcd(a, b) via the Euclidean algorithm. a, b are bit[:n].
def gcd_into n, dst, a, b @ loop, end < ga, gb, q, r {
    bit.mov n, ga, a
    bit.mov n, gb, b
  loop:
    bit.if0 n, gb, end
    bit.div n, ga, gb, q, r
    bit.mov n, ga, gb
    bit.mov n, gb, r
    ;loop
  end:
    bit.mov n, dst, ga
}
""".strip()

SUM_PROPER = """
// dst = sum of proper divisors of x (1..x-1 that divide x). x >= 1.
def sum_proper_divisors_into n, dst, x @ loop, body, is_div, skip, end < d, q, r, one {
    bit.zero n, dst
    bit.mov n, d, one
  loop:
    bit.cmp n, d, x, body, end, end
  body:
    bit.div n, x, d, q, r
    bit.if0 n, r, is_div
    ;skip
  is_div:
    bit.add n, dst, d
  skip:
    bit.inc n, d
    ;loop
  end:
}
""".strip()

PRINT_HEX_NIBBLE = """
// Print the low 4 bits at nib as a single lowercase hex digit (0-9, a-f).
def print_hex_nibble nib @ small, big, done < hexout, ten, off_small, off_big {
    bit.zero 8, hexout
    bit.mov 4, hexout, nib
    bit.cmp 4, nib, ten, small, big, big
  small:
    bit.add 8, hexout, off_small
    ;done
  big:
    bit.add 8, hexout, off_big
  done:
    bit.print hexout
}
""".strip()

# common scratch fragments
S_PRIME = ["d: bit.vec 16, 0", "q: bit.vec 16, 0", "r: bit.vec 16, 0", "two: bit.vec 16, 2"]
S_GCD = ["ga: bit.vec 16, 0", "gb: bit.vec 16, 0", "q: bit.vec 16, 0", "r: bit.vec 16, 0"]
S_SUMPROPER = ["d: bit.vec 16, 0", "q: bit.vec 16, 0", "r: bit.vec 16, 0", "one: bit.vec 16, 1"]
S_HEXNIB = ["hexout: bit.vec 8, 0", "ten: bit.vec 4, 10", "off_small: bit.vec 8, 0x30", "off_big: bit.vec 8, 0x57"]


def IO(nnnn, slug, name, **kw):
    emit("io", nnnn, slug, name, **kw)


def NT(nnnn, slug, name, **kw):
    emit("number_theory", nnnn, slug, name, **kw)


# ============================ io conversions ============================

# 0045 dec_to_char — read decimal 0-127, output that byte.
IO(
    "0045",
    "dec_to_char",
    "Dec To Char",
    unsigned=True,
    value_data=["value: bit.vec 8, 0"],
    main_body="""
def main < value {
    stl.startup
    read_decimal 8, value
    bit.print value
    stl.loop
}
""",
    in_bytes=b"65\n\0",
    out_bytes=b"A",
)

# 0046 char_to_hex — read one byte, print "0xNN" (lowercase) + newline.
IO(
    "0046",
    "char_to_hex",
    "Char To Hex",
    extra_helpers=[PRINT_HEX_NIBBLE],
    value_data=["ch: bit.vec 8, 0"],
    extra_data=S_HEXNIB,
    main_body="""
def main < ch {
    stl.startup
    bit.input ch
    stl.output "0x"
    print_hex_nibble ch + 4*dw
    print_hex_nibble ch
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"A",
    out_bytes=b"0x41\n",
)

# 0047 hex_to_char — read "0xNN" (lowercase hex), output the byte.
IO(
    "0047",
    "hex_to_char",
    "Hex To Char",
    value_data=["ch: bit.vec 8, 0", "hi: bit.vec 4, 0", "lo: bit.vec 4, 0", "byte: bit.vec 8, 0", "err: bit.bit"],
    main_body="""
def main < ch, hi, lo, byte, err {
    stl.startup
    bit.input ch
    bit.input ch
    bit.input ch
    bit.ascii2hex err, hi, ch
    bit.input ch
    bit.ascii2hex err, lo, ch
    bit.zero 8, byte
    bit.mov 4, byte, lo
    bit.mov 4, byte + 4*dw, hi
    bit.print byte
    stl.loop
}
""",
    in_bytes=b"0x6a\n",
    out_bytes=b"j",
)


# ====================== number_theory: primes ======================

# 0138 is_prime_small
NT(
    "0138",
    "is_prime_small",
    "Is Prime Small",
    unsigned=True,
    extra_helpers=[IS_PRIME],
    value_data=["value: bit.vec 16, 0", "flag: bit.bit"],
    extra_data=S_PRIME,
    main_body="""
def main @ no, done < value, flag {
    stl.startup
    read_decimal 16, value
    is_prime_into 16, flag, value
    bit.if0 flag, no
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

# 0139 first_n_primes — first N primes, one per line
NT(
    "0139",
    "first_n_primes",
    "First N Primes",
    unsigned=True,
    extra_helpers=[IS_PRIME],
    value_data=["limit: bit.vec 16, 0", "found: bit.vec 16, 0", "cand: bit.vec 16, 0", "flag: bit.bit"],
    extra_data=S_PRIME,
    main_body="""
def main @ loop, body, next, done < limit, found, cand, flag, two {
    stl.startup
    read_decimal 16, limit
    bit.zero 16, found
    bit.mov 16, cand, two
  loop:
    bit.cmp 16, found, limit, body, done, done
  body:
    is_prime_into 16, flag, cand
    bit.if0 flag, next
    bit.print_dec_uint 16, cand
    stl.output '\\n'
    bit.inc 16, found
  next:
    bit.inc 16, cand
    ;loop
  done:
    stl.loop
}
""",
    in_bytes=b"3\n\0",
    out_bytes=b"2\n3\n5\n",
)

# 0140 prime_after — smallest prime strictly greater than N
NT(
    "0140",
    "prime_after",
    "Prime After",
    unsigned=True,
    extra_helpers=[IS_PRIME],
    value_data=["value: bit.vec 16, 0", "cand: bit.vec 16, 0", "flag: bit.bit"],
    extra_data=S_PRIME,
    main_body="""
def main @ loop < value, cand, flag {
    stl.startup
    read_decimal 16, value
    bit.mov 16, cand, value
  loop:
    bit.inc 16, cand
    is_prime_into 16, flag, cand
    bit.if0 flag, loop
    bit.print_dec_uint 16, cand
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"10\n\0",
    out_bytes=b"11\n",
)

# 0141 count_primes_to_n — count primes in [2..N]
NT(
    "0141",
    "count_primes_to_n",
    "Count Primes To N",
    unsigned=True,
    extra_helpers=[IS_PRIME],
    value_data=["limit: bit.vec 16, 0", "cand: bit.vec 16, 0", "count: bit.vec 16, 0", "flag: bit.bit"],
    extra_data=S_PRIME,
    main_body="""
def main @ loop, body, next, done < limit, cand, count, flag, two {
    stl.startup
    read_decimal 16, limit
    bit.zero 16, count
    bit.mov 16, cand, two
  loop:
    bit.cmp 16, cand, limit, body, body, done
  body:
    is_prime_into 16, flag, cand
    bit.if0 flag, next
    bit.inc 16, count
  next:
    bit.inc 16, cand
    ;loop
  done:
    bit.print_dec_uint 16, count
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"10\n\0",
    out_bytes=b"4\n",
)


# ====================== number_theory: gcd / lcm ======================

# 0142 gcd_two
NT(
    "0142",
    "gcd_two",
    "Gcd Two",
    unsigned=True,
    extra_helpers=[GCD],
    value_data=["a: bit.vec 16, 0", "b: bit.vec 16, 0", "g: bit.vec 16, 0"],
    extra_data=S_GCD,
    main_body="""
def main < a, b, g {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    gcd_into 16, g, a, b
    bit.print_dec_uint 16, g
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"48\n36\n\0",
    out_bytes=b"12\n",
)

# 0143 lcm_two — lcm = (a / gcd) * b
NT(
    "0143",
    "lcm_two",
    "Lcm Two",
    unsigned=True,
    mul=True,
    extra_helpers=[GCD],
    value_data=["a: bit.vec 16, 0", "b: bit.vec 16, 0", "g: bit.vec 16, 0", "lcm: bit.vec 16, 0"],
    extra_data=S_GCD,
    main_body="""
def main < a, b, g, lcm, q, r {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    gcd_into 16, g, a, b
    bit.div 16, a, g, q, r
    mul_into 16, lcm, q, b
    bit.print_dec_uint 16, lcm
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"4\n6\n\0",
    out_bytes=b"12\n",
)

# 0144 coprime_check — gcd(a,b) == 1 ?
NT(
    "0144",
    "coprime_check",
    "Coprime Check",
    unsigned=True,
    extra_helpers=[GCD],
    value_data=["a: bit.vec 16, 0", "b: bit.vec 16, 0", "g: bit.vec 16, 0", "one: bit.vec 16, 1"],
    extra_data=S_GCD,
    main_body="""
def main @ yes, no, done < a, b, g, one {
    stl.startup
    read_decimal 16, a
    read_decimal 16, b
    gcd_into 16, g, a, b
    bit.cmp 16, g, one, no, yes, no
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"9\n4\n\0",
    out_bytes=b"1\n",
)


# ====================== number_theory: divisors ======================

# 0145 factor_count_small — number of divisors of N (1..N)
NT(
    "0145",
    "factor_count_small",
    "Factor Count Small",
    unsigned=True,
    value_data=[
        "value: bit.vec 16, 0",
        "d: bit.vec 16, 0",
        "count: bit.vec 16, 0",
        "q: bit.vec 16, 0",
        "r: bit.vec 16, 0",
        "one: bit.vec 16, 1",
    ],
    main_body="""
def main @ loop, body, is_div, next, done < value, d, count, q, r, one {
    stl.startup
    read_decimal 16, value
    bit.zero 16, count
    bit.mov 16, d, one
  loop:
    bit.cmp 16, d, value, body, body, done
  body:
    bit.div 16, value, d, q, r
    bit.if0 16, r, is_div
    ;next
  is_div:
    bit.inc 16, count
  next:
    bit.inc 16, d
    ;loop
  done:
    bit.print_dec_uint 16, count
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"12\n\0",
    out_bytes=b"6\n",
)

# 0146 divisors_of_n — print divisors 1..N, one per line
NT(
    "0146",
    "divisors_of_n",
    "Divisors Of N",
    unsigned=True,
    value_data=[
        "value: bit.vec 16, 0",
        "d: bit.vec 16, 0",
        "q: bit.vec 16, 0",
        "r: bit.vec 16, 0",
        "one: bit.vec 16, 1",
    ],
    main_body="""
def main @ loop, body, is_div, next, done < value, d, q, r, one {
    stl.startup
    read_decimal 16, value
    bit.mov 16, d, one
  loop:
    bit.cmp 16, d, value, body, body, done
  body:
    bit.div 16, value, d, q, r
    bit.if0 16, r, is_div
    ;next
  is_div:
    bit.print_dec_uint 16, d
    stl.output '\\n'
  next:
    bit.inc 16, d
    ;loop
  done:
    stl.loop
}
""",
    in_bytes=b"12\n\0",
    out_bytes=b"1\n2\n3\n4\n6\n12\n",
)

# 0147 is_perfect_small — sum of proper divisors == N
NT(
    "0147",
    "is_perfect_small",
    "Is Perfect Small",
    unsigned=True,
    extra_helpers=[SUM_PROPER],
    value_data=["value: bit.vec 16, 0", "sp: bit.vec 16, 0"],
    extra_data=S_SUMPROPER,
    main_body="""
def main @ yes, no, done < value, sp {
    stl.startup
    read_decimal 16, value
    sum_proper_divisors_into 16, sp, value
    bit.cmp 16, sp, value, no, yes, no
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"6\n\0",
    out_bytes=b"1\n",
)

# 0148 sum_of_divisors_small — sum of ALL divisors (proper + N)
NT(
    "0148",
    "sum_of_divisors_small",
    "Sum Of Divisors Small",
    unsigned=True,
    extra_helpers=[SUM_PROPER],
    value_data=["value: bit.vec 16, 0", "sp: bit.vec 16, 0"],
    extra_data=S_SUMPROPER,
    main_body="""
def main < value, sp {
    stl.startup
    read_decimal 16, value
    sum_proper_divisors_into 16, sp, value
    bit.add 16, sp, value
    bit.print_dec_uint 16, sp
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"6\n\0",
    out_bytes=b"12\n",
)

# 0149 is_abundant_small — sum of proper divisors > N
NT(
    "0149",
    "is_abundant_small",
    "Is Abundant Small",
    unsigned=True,
    extra_helpers=[SUM_PROPER],
    value_data=["value: bit.vec 16, 0", "sp: bit.vec 16, 0"],
    extra_data=S_SUMPROPER,
    main_body="""
def main @ yes, no, done < value, sp {
    stl.startup
    read_decimal 16, value
    sum_proper_divisors_into 16, sp, value
    bit.cmp 16, sp, value, no, no, yes
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"12\n\0",
    out_bytes=b"1\n",
)

# 0150 is_deficient_small — sum of proper divisors < N
NT(
    "0150",
    "is_deficient_small",
    "Is Deficient Small",
    unsigned=True,
    extra_helpers=[SUM_PROPER],
    value_data=["value: bit.vec 16, 0", "sp: bit.vec 16, 0"],
    extra_data=S_SUMPROPER,
    main_body="""
def main @ yes, no, done < value, sp {
    stl.startup
    read_decimal 16, value
    sum_proper_divisors_into 16, sp, value
    bit.cmp 16, sp, value, yes, no, no
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"8\n\0",
    out_bytes=b"1\n",
)

print("---")
print("BATCH 6 DONE")

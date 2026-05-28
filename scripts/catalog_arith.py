"""Shared scaffolding for the arithmetic catalog batches (4, 5, ...).

Provides the decimal-I/O helper-macro source strings and an `emit()` that
assembles a clean header + main + helpers + data .fj and registers it.
batch03 predates this module and carries its own copies; batch04+ import here.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog_register import register  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CATALOG_MD = (ROOT / "programs" / "catalog" / "CATALOG.md").read_text(encoding="utf-8")

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
""".strip()

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
""".strip()

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
""".strip()

MAX_INTO = """
// dst[:n] = max(x[:n], y[:n]).
def max_into n, dst, x, y @ use_x, use_y, end {
    bit.cmp n, x, y, use_y, use_x, use_x
  use_x:
    bit.mov n, dst, x
    ;end
  use_y:
    bit.mov n, dst, y
  end:
}
""".strip()

MIN_INTO = """
// dst[:n] = min(x[:n], y[:n]).
def min_into n, dst, x, y @ use_x, use_y, end {
    bit.cmp n, x, y, use_x, use_x, use_y
  use_x:
    bit.mov n, dst, x
    ;end
  use_y:
    bit.mov n, dst, y
  end:
}
""".strip()

SCRATCH_UNSIGNED = ["ch: bit.vec 8, 0", "nl: bit.vec 8, '\\n'", "digit: bit.vec 16, 0", "err: bit.bit"]
SCRATCH_SIGNED = ["minus: bit.vec 8, '-'", "neg_flag: bit.bit"]
SCRATCH_MUL = ["mul_counter: bit.vec 16, 0"]


def catalog_desc(slug: str) -> str:
    m = re.search(rf"\| APPROVED \| \S+ \| {re.escape(slug)} \| (.+?) \|", CATALOG_MD)
    if not m:
        raise SystemExit(f"no APPROVED row for {slug}")
    return m.group(1).strip()


def emit(
    category,
    nnnn,
    slug,
    name,
    *,
    main_body,
    value_data,
    unsigned=False,
    signed=False,
    mul=False,
    extra_helpers=None,
    extra_data=None,
    in_bytes,
    out_bytes,
):
    """Assemble a clean .fj (header + main + helpers + data) and register it."""
    parts = [f"// {name} (#{nnnn})", "", f"// {catalog_desc(slug)}", "", "main", "", main_body.strip()]

    helpers = []
    scratch = []
    if unsigned:
        helpers.append(READ_DECIMAL)
        scratch += SCRATCH_UNSIGNED
    if signed:
        helpers.append(READ_SIGNED)
        for s in SCRATCH_UNSIGNED:
            if s not in scratch:
                scratch.append(s)
        scratch += SCRATCH_SIGNED
    if mul:
        helpers.append(MUL_INTO)
        scratch += SCRATCH_MUL
    helpers += extra_helpers or []
    for h in helpers:
        parts += ["", h]

    parts += [""] + list(value_data) + (extra_data or []) + scratch + [""]
    fj = "\n".join(parts)
    (ROOT / "programs" / "catalog" / category / f"{slug}.fj").write_text(fj, encoding="utf-8", newline="\n")
    register(category=category, slug=slug, in_bytes=in_bytes, out_bytes=out_bytes)

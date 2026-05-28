"""Register a hand-written catalog .fj: validate header, write fixtures, verify, append CSVs.

Batch 2+ workflow: the .fj files are written by hand (clean, reviewable, with
proper helper macros per CONVENTIONS.md), and this module handles the
mechanical parts:

    from catalog_register import register

    register(
        category="io",
        slug="only_digits",
        in_bytes=b"a1b2c3\0",
        out_bytes=b"123",
    )

It asserts the .fj header's description line byte-matches CATALOG.md (the
single-source-of-truth rule), writes .in/.out as raw bytes (LF, no CRLF
translation), compiles via `fj --asm`, runs via the flipjump module, and
idempotently appends rows to both catalog CSVs.
"""

from __future__ import annotations

import re
import subprocess
from functools import lru_cache
from pathlib import Path

from flipjump import run_test_output

ROOT = Path(__file__).resolve().parent.parent

CATALOG_PROG = ROOT / "programs" / "catalog"
CATALOG_IO = ROOT / "tests" / "inout" / "catalog"
CATALOG_MD = CATALOG_PROG / "CATALOG.md"
COMPILE_CSV = ROOT / "tests" / "tests_tables" / "test_compile_catalog.csv"
RUN_CSV = ROOT / "tests" / "tests_tables" / "test_run_catalog.csv"


@lru_cache(maxsize=1)
def _catalog_rows() -> dict[str, tuple[str, str]]:
    """Parse CATALOG.md once: {slug: (nnnn?, description)} for APPROVED rows.

    NNNN is not stored in CATALOG.md rows (assigned by position elsewhere), so
    we return ("", description); the .fj header is the authority for #NNNN.
    """
    txt = CATALOG_MD.read_text(encoding="utf-8")
    out: dict[str, tuple[str, str]] = {}
    for status, _cat, slug, desc in re.findall(r"\| (\w+) \| (\S+) \| (\S+) \| (.+?) \|", txt):
        if status == "APPROVED":
            out[slug] = ("", desc.strip())
    return out


def _write_lf(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(content)


def register(*, category: str, slug: str, in_bytes: bytes, out_bytes: bytes, word_size: int = 64) -> None:
    """Validate a hand-written .fj, write fixtures, verify, append CSV rows."""

    fj_path = CATALOG_PROG / category / f"{slug}.fj"
    if not fj_path.exists():
        raise RuntimeError(f"{fj_path} does not exist — write the .fj first")

    # Validate the header's first description line == CATALOG.md description.
    rows = _catalog_rows()
    if slug not in rows:
        raise RuntimeError(f"slug {slug!r} is not an APPROVED row in CATALOG.md")
    _, expected_desc = rows[slug]

    lines = fj_path.read_text(encoding="utf-8").splitlines()
    # Header shape: line0 "// Name (#NNNN)", line1 blank, line2 "// <desc>".
    if not (len(lines) >= 3 and lines[0].startswith("// ") and lines[1] == "" and lines[2].startswith("// ")):
        raise RuntimeError(f"{slug}: header must be '// Name (#NNNN)', blank, '// <desc>'")
    header_desc = lines[2][3:]
    if header_desc != expected_desc:
        raise RuntimeError(
            f"{slug}: header description does not match CATALOG.md:\n"
            f"  .fj : {header_desc!r}\n"
            f"  cat : {expected_desc!r}"
        )
    if not re.match(r"^// .+ \(#\d{4}\)$", lines[0]):
        raise RuntimeError(f"{slug}: first line must be '// <Name> (#NNNN)', got {lines[0]!r}")

    in_path = CATALOG_IO / category / f"{slug}.in"
    out_path = CATALOG_IO / category / f"{slug}.out"
    _write_lf(in_path, in_bytes)
    _write_lf(out_path, out_bytes)

    # Compile.
    fjm_path = ROOT / "tests" / "compiled" / "catalog" / category / f"{slug}.fjm"
    fjm_path.parent.mkdir(parents=True, exist_ok=True)
    asm_cmd = ["fj", "--asm", str(fj_path), "-o", str(fjm_path), "-s", "-w", str(word_size)]
    result = subprocess.run(asm_cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"compile failed for {slug}:\n  {result.stdout.decode('utf-8', 'replace')[:800]}\n"
            f"  {result.stderr.decode('utf-8', 'replace')[:800]}"
        )

    # Verify exact output via the flipjump module (raw bytes; no CRLF surprises).
    try:
        ok = run_test_output(
            fjm_path,
            in_bytes,
            out_bytes,
            should_raise_assertion_error=True,
            print_time=False,
            print_termination=False,
        )
    except AssertionError as e:
        raise RuntimeError(f"verify failed for {slug}: {e}") from e
    if not ok:
        raise RuntimeError(f"verify returned False for {slug}")

    # Append CSV rows (idempotent).
    fj_rel = fj_path.relative_to(ROOT).as_posix()
    fjm_rel = fjm_path.relative_to(ROOT).as_posix()
    in_rel = in_path.relative_to(ROOT).as_posix()
    out_rel = out_path.relative_to(ROOT).as_posix()
    compile_row = f"cat_{slug}, {fj_rel},{fjm_rel}, {word_size},3,0, True,True\n"
    run_row = f"cat_{slug}, {fjm_rel}, {in_rel},{out_rel}, True,True\n"

    for csv_path, row in ((COMPILE_CSV, compile_row), (RUN_CSV, run_row)):
        existing = csv_path.read_text(encoding="utf-8")
        if f"cat_{slug}," not in existing:
            with open(csv_path, "ab") as f:
                f.write(row.encode("utf-8"))

    print(f"OK {slug}")

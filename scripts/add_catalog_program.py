"""Helper for Phase 3 batch 1: write .fj/.in/.out files for a catalog program,
verify via the FlipJump interpreter, and append rows to the catalog CSVs.

Usage (from a sibling script that imports this):

    from add_catalog_program import add_program

    add_program(
        category="hello",
        slug="hello_world",
        nnnn="0001",
        fj_body='stl.startup\\nstl.output "Hello, World!\\n"\\nstl.loop\\n',
        in_bytes=b"",
        out_bytes=b"Hello, World!\\n",
    )

The helper writes files using LF line endings throughout (matching the
FlipJump interpreter's raw byte output), then runs the fj assembler+interpreter
once to verify that the program compiles, halts cleanly, and produces the
exact expected output bytes.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from flipjump import run_test_output

ROOT = Path(__file__).resolve().parent.parent

CATALOG_PROG = ROOT / "programs" / "catalog"
CATALOG_IO = ROOT / "tests" / "inout" / "catalog"
COMPILE_CSV = ROOT / "tests" / "tests_tables" / "test_compile_catalog.csv"
RUN_CSV = ROOT / "tests" / "tests_tables" / "test_run_catalog.csv"


def _write_lf(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(content)


def add_program(
    *,
    category: str,
    slug: str,
    nnnn: str,
    name_display: str,
    description: str,
    fj_body: str,
    in_bytes: bytes,
    out_bytes: bytes,
    word_size: int = 64,
    use_stl: bool = True,
) -> None:
    """Write .fj/.in/.out files, verify, and append CSV rows."""

    # Build the .fj source with the conventional header.
    fj_header = f"// {name_display} (#{nnnn})\n\n"
    for line in description.strip().split("\n"):
        fj_header += f"// {line.strip()}\n"
    fj_header += "\n"
    fj_src = fj_header + fj_body if fj_body.endswith("\n") else fj_header + fj_body + "\n"

    fj_path = CATALOG_PROG / category / f"{slug}.fj"
    in_path = CATALOG_IO / category / f"{slug}.in"
    out_path = CATALOG_IO / category / f"{slug}.out"

    _write_lf(fj_path, fj_src.encode("utf-8"))
    _write_lf(in_path, in_bytes)
    _write_lf(out_path, out_bytes)

    # Verify: compile via fj --asm, then run via the Python interpreter and
    # compare bytes (this matches what pytest's internal harness does).
    fjm_path = ROOT / "tests" / "compiled" / "catalog" / category / f"{slug}.fjm"
    fjm_path.parent.mkdir(parents=True, exist_ok=True)

    asm_cmd = ["fj", "--asm", str(fj_path), "-o", str(fjm_path), "-s", "-w", str(word_size)]
    if not use_stl:
        asm_cmd.append("--no_stl")
    result = subprocess.run(asm_cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"compile failed for {slug}:\n  stdout={result.stdout.decode('utf-8', 'replace')[:500]}\n"
            f"  stderr={result.stderr.decode('utf-8', 'replace')[:500]}"
        )

    # Use the Python FlipJump module directly so we get raw byte output
    # without OS-level CRLF translation.
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

    # Append CSV rows.
    fj_rel = fj_path.relative_to(ROOT).as_posix()
    fjm_rel = fjm_path.relative_to(ROOT).as_posix()
    in_rel = in_path.relative_to(ROOT).as_posix()
    out_rel = out_path.relative_to(ROOT).as_posix()

    compile_row = f"cat_{slug}, {fj_rel},{fjm_rel}, {word_size},3,0, {'True' if use_stl else 'False'},True\n"
    run_row = f"cat_{slug}, {fjm_rel}, {in_rel},{out_rel}, True,True\n"

    # idempotent append: skip if already present
    with open(COMPILE_CSV, "rb") as f:
        existing = f.read().decode("utf-8")
    if f"cat_{slug}," not in existing:
        with open(COMPILE_CSV, "ab") as f:
            f.write(compile_row.encode("utf-8"))
    with open(RUN_CSV, "rb") as f:
        existing = f.read().decode("utf-8")
    if f"cat_{slug}," not in existing:
        with open(RUN_CSV, "ab") as f:
            f.write(run_row.encode("utf-8"))

    print(f"OK {slug}")

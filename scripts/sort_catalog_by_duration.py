"""Sort the catalog CSVs by per-test duration (slowest first).

Runs the catalog compile and run suites with `--durations=0`, parses the
per-test timings, and rewrites each CSV with its rows ordered slowest-first.
This gives pytest-xdist the best chance to keep all workers busy until the end
(the longest job starts first instead of being the idle tail).

Reusable across batches — durations are measured live, not hard-coded.

Run from the repo root:

    python scripts/sort_catalog_by_duration.py
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPILE_CSV = ROOT / "tests" / "tests_tables" / "test_compile_catalog.csv"
RUN_CSV = ROOT / "tests" / "tests_tables" / "test_run_catalog.csv"

# Matches lines like: "0.27s call tests/test_fj.py::test_compile[cat_count_bytes]"
DURATION_RE = re.compile(r"^([\d.]+)s\s+call\s+.*\[(cat_\S+)\]\s*$")


def measure(kind: str) -> dict[str, float]:
    """Run the catalog suite for `kind` ('compile' or 'run'); return {name: seconds}."""
    cmd = ["pytest", "-n", "auto", "--catalog", f"--{kind}", "-q", "--no-header", "--durations=0"]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    durations: dict[str, float] = {}
    for line in out.splitlines():
        m = DURATION_RE.match(line.strip())
        if m:
            durations[m.group(2)] = float(m.group(1))
    return durations


def sort_csv(path: Path, durations: dict[str, float]) -> None:
    """Rewrite rows slowest-first; unknown rows sort to 0 (end)."""
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    lines.sort(key=lambda row: -durations.get(row.split(",", 1)[0].strip(), 0.0))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"Sorted {len(lines):>3} rows: {path.name}")


def main() -> None:
    sort_csv(COMPILE_CSV, measure("compile"))
    sort_csv(RUN_CSV, measure("run"))


if __name__ == "__main__":
    main()

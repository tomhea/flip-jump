"""Sort the catalog CSVs by per-test duration (slowest first).

Reads the durations dictionary inline (captured from a recent pytest run)
and rewrites the two CSVs in-place. The .fj/.in/.out files themselves are
unchanged — only row order moves.

After this, pytest -n auto schedules the longest jobs first, giving the
load-balancer the best chance to keep all workers busy until the end.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPILE_CSV = ROOT / "tests" / "tests_tables" / "test_compile_catalog.csv"
RUN_CSV = ROOT / "tests" / "tests_tables" / "test_run_catalog.csv"

# Compile-test durations (seconds) captured from `pytest -n auto --catalog --compile --durations=0`.
COMPILE_DURATIONS = {
    "cat_count_bytes": 0.27,
    "cat_hello_two_users": 0.23,
    "cat_count_lines": 0.23,
    "cat_hello_long_user": 0.21,
    "cat_echo_twice": 0.21,
    "cat_hello_alpha_world": 0.21,
    "cat_hello_no_newline": 0.21,
    "cat_hello_underline": 0.21,
    "cat_hello_ascii_first_five": 0.20,
    "cat_hello_user": 0.20,
    "cat_hello_then_question": 0.20,
    "cat_hello_world_3x": 0.20,
    "cat_hello_anonymous": 0.20,
    "cat_hello_question": 0.19,
    "cat_hello_box": 0.19,
    "cat_hello_world": 0.19,
    "cat_cat": 0.19,
    "cat_hello_two_lines": 0.19,
    "cat_hello_lowercase": 0.19,
    "cat_hello_world_overunder": 0.19,
    "cat_hello_then_length": 0.19,
    "cat_hello_exclaim_3x": 0.19,
    "cat_hello_one_char_per_line": 0.18,
    "cat_hello_hex_codes": 0.18,
    "cat_echo_thrice": 0.18,
    "cat_hello_tab_sep": 0.18,
    "cat_hello_reversed": 0.17,
    "cat_hello_uppercase": 0.17,
    "cat_skip_first_byte": 0.13,
    "cat_uppercase_filter": 0.12,
    "cat_lowercase_filter": 0.12,
}

# Run-test durations (seconds) captured similarly.
RUN_DURATIONS = {
    "cat_hello_two_users": 0.02,
    "cat_count_bytes": 0.02,
    "cat_uppercase_filter": 0.01,
    "cat_lowercase_filter": 0.01,
    "cat_count_lines": 0.01,
    "cat_hello_user": 0.01,
    "cat_echo_twice": 0.01,
    "cat_hello_long_user": 0.01,
    "cat_skip_first_byte": 0.01,
    "cat_hello_reversed": 0.01,
    "cat_hello_then_question": 0.01,
    "cat_hello_alpha_world": 0.01,
    "cat_hello_lowercase": 0.01,
}


def sort_csv(path: Path, durations: dict[str, float]) -> None:
    """Sort rows by duration (slowest first), unknowns at the end as 0."""
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]

    def key(row: str) -> float:
        name = row.split(",", 1)[0].strip()
        # Negative so that descending sort = slowest first.
        return -durations.get(name, 0.0)

    sorted_lines = sorted(lines, key=key)
    path.write_text("\n".join(sorted_lines) + "\n", encoding="utf-8", newline="\n")
    print(f"Sorted {len(sorted_lines):>3} rows: {path.name}")


def main() -> None:
    sort_csv(COMPILE_CSV, COMPILE_DURATIONS)
    sort_csv(RUN_CSV, RUN_DURATIONS)


if __name__ == "__main__":
    main()

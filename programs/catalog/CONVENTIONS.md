# Catalog Conventions

This document is the authoritative convention list for the demonstration catalog
under `programs/catalog/`. Read this end-to-end before writing or reviewing a
catalog program.

## Goal

A catalog of up-to-1200 distinct, small, working FlipJump programs that
collectively demonstrate the language is expressive enough to do anything.
Quality > quantity: a smaller catalog of meaningful programs beats a padded one.

## File layout

| Kind | Path |
|---|---|
| Source | `programs/catalog/<category>/<slug>.fj` |
| Input | `tests/inout/catalog/<category>/<slug>.in` |
| Expected output | `tests/inout/catalog/<category>/<slug>.out` |
| Compiled (generated) | `tests/compiled/catalog/<category>/<slug>.fjm` |

- **No `NNNN_` prefix in filenames.** Slugs are clean (e.g. `factorial.fj`).
- **Slugs are unique across the entire catalog**, not just within a category.
  This is forced by the pytest-name uniqueness rule below.
- **Categories** are listed in `CATALOG.md` and `README.md`.

## Catalog number `#NNNN`

Each program has a four-digit catalog number assigned when `CATALOG.md` is
locked at the end of Phase 2. The number appears in:

- The source header: `// Program Name (#NNNN)`.
- The README row.
- The `CATALOG.md` row.

Numbers are never recycled. A row retired during Phase 3 keeps its number;
its replacement gets a fresh higher number at the end of `CATALOG.md`.

## Program header — every `.fj` starts with this

```
// Program Name (#NNNN)

// 1-line description that exactly matches CATALOG.md / README.md description.
// 0-3 additional context lines, each beginning with `// `.

main

def main {
    stl.startup
    // ... body ...
    stl.loop
}

// Helper macros below, each prefixed with a 1-line `// what it does` comment.
```

The very first description line is the **single source of truth** and must
match the `description` column in `CATALOG.md` byte-for-byte. The README and
the `.fj` header propagate that text. Subsequent header lines may add context.

## `main` macro convention

- The macro is literally named `main` (not `<slug>_main`).
- The top-level non-macro code is essentially just the line `main`. The only
  other things allowed at top level are `segment` / `reserve` directives for
  programs that need explicit memory layout (per `programs/prime_sieve.fj`).
- Helper macros and variable declarations live below `def main { ... }`.
- **`stl.startup` and `stl.loop` appear ONLY inside `main`, never inside a
  helper macro.** They are the program-lifecycle bookends — the startup brings
  up the runtime, the loop halts it. A helper macro that contains either of
  them is misshapen: it's trying to be a program, not a function. (Look at
  the STL itself for the same rule — no `stl.macro` definition uses
  `stl.startup` or `stl.loop` in its body.)

## Sub-macros — "functionalize" the body

Programs more complex than a one-line `stl.output` should be decomposed into
helper `def`s, not crammed into `main`. `main` then reads as a sequence of
high-level calls. This isn't aesthetic — it's how the language is meant to be
used (every STL feature you call is itself a macro), and it pays back fast on
the medium-complexity programs (parsing, sorting, n-queens, etc.).

Practical rules of thumb:

- If `main`'s body is more than ~15 lines or has more than one `@`-label loop,
  pull each loop out into its own helper.
- A helper has a single clear job. Its name describes that job. Its `def` is
  preceded by a 1-line `// what it does` comment.
- Helpers receive their inputs via macro parameters and reference their
  external data via the `< ...` clause. They do NOT define their own
  `stl.startup` / `stl.loop` (see above).
- Loops over input bytes, decimal-digit parsing, case toggling, counter
  printing, etc. are all natural helper candidates and recur enough across
  the catalog that defining them once per program (and letting future programs
  copy the pattern) is the right call.

### Worked example

Don't:
```
def main @ loop, end < ch, counter {
    stl.startup
  loop:
    bit.input ch
    bit.if0 8, ch, end
    bit.inc 16, counter
    ;loop
  end:
    bit.print_dec_uint 16, counter
    stl.output '\n'
    stl.loop
}
```

Do:
```
def main < ch, counter {
    stl.startup
    count_input_bytes ch, counter
    bit.print_dec_uint 16, counter
    stl.output '\n'
    stl.loop
}

// Read bytes from stdin until \0, incrementing counter for each.
def count_input_bytes ch, counter @ loop, end {
  loop:
    bit.input ch
    bit.if0 8, ch, end
    bit.inc 16, counter
    ;loop
  end:
}
```

The "Do" version reads top-down as a recipe and the helper is reusable in
adjacent programs.

## Code style (CR-ist-enforced)

- Clean, easy-to-read macro and label names.
- Whitespace between logical sections.
- Helper macros under their `def` line have a `// what it does` comment, 1-2 lines.
- No dead code, no commented-out lines, no `TODO`s.
- Prefer `hex.*` macros over `bit.*` (4x smaller/faster).
- **For long repeats, use a runtime loop** (counter + cmp + branch).
  `rep` is the same as manual unroll; if compile time grows past ~5s, switch
  to a runtime loop.

## CSV rows (the two test-spec files)

Every catalog program contributes one row each to:

- `tests/tests_tables/test_compile_catalog.csv`
- `tests/tests_tables/test_run_catalog.csv`

### Compile row format (8 fields)
```
cat_<slug>, programs/catalog/<cat>/<slug>.fj, tests/compiled/catalog/<cat>/<slug>.fjm, 64, 3, 0, True, True
```
Fields: `name, fj_paths, fjm_out_path, word_size, version, flags, use_stl, warning_as_errors`.

### Run row format (6 fields)
```
cat_<slug>, tests/compiled/catalog/<cat>/<slug>.fjm, tests/inout/catalog/<cat>/<slug>.in, tests/inout/catalog/<cat>/<slug>.out, True, True
```
Fields: `name, fjm_path, in_file_path, out_file_path, read_in_as_binary, read_out_as_binary`.

### Test-name uniqueness rule
The first column is **always `cat_<slug>`**. The `cat_` prefix prevents
collision with existing test names (`hello_world`, `cat`, `simple`, etc. are
already used by the non-catalog CSVs, and pytest names are global).

### Binary I/O
`read_in_as_binary=True` and `read_out_as_binary=True` (both `True`). This
gives byte-exact matching and avoids CRLF translation surprises on Windows.

## Word-size override

- Default `w=64` (compile-CSV column 4).
- `w=32` is fine when it makes things simpler/smaller and the program still works.
- `w=16` only when truly necessary (e.g. a quine that needs tiny encoding).
- The CSV is the source of truth. If a program *requires* a specific `w`, say so
  in its header description.

## `use_stl=False` exception (rare)

A small number of programs may demonstrate FlipJump without the standard
library (per `programs/print_tests/hello_no-stl.fj`). For those, set CSV column
7 to `False` and provide your own `startup` / `output_bit` / `end_loop` macros.
The header + `main`-macro convention still applies.

## Running the tests

```
pytest --catalog                       # all catalog tests
pytest -n auto --catalog --compile     # parallel compile-only
pytest -n auto --catalog --run         # parallel run-only
pytest --catalog -k cat_<slug>         # one program
```

`pytest --catalog` is **mutually exclusive** with `--all`, `--regular`, and the
individual type flags (`--fast`, `--medium`, `--hexlib`, `--slow`). The repo is
green under both `pytest --all` (existing tests) and `pytest --catalog` (catalog
tests), but each invocation tests its own disjoint slice.

## STL extensions

If a useful macro is missing and would shorten this and several upcoming
programs, add it to the right STL file under `flipjump/stl/` and:

- Add corresponding test rows in `programs/<existing_category>/` plus
  `tests/tests_tables/test_*_<existing_speed>.csv` so the new macro is
  exercised by `pytest --all`.
- Document the addition in `../../flipjump_claude_conclusions.md` with rationale.
- STL additions are NOT counted against the catalog target.

## Per-program verification (before committing)

For each `<slug>`:

```
fj --asm programs/catalog/<cat>/<slug>.fj -o tests/compiled/catalog/<cat>/<slug>.fjm
# compile must finish in <= 5s wall clock

fj --run tests/compiled/catalog/<cat>/<slug>.fjm < tests/inout/catalog/<cat>/<slug>.in
# stdout must equal <slug>.out byte-for-byte; runtime <= a few seconds
```

A program is not done until both checks pass. The `/writing-flipjump-stl-code`
skill enforces this loop.

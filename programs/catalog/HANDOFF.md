# Catalog — Implementation Handoff

Handoff for completing the demonstration catalog. As of this writing: **526 / 1029
approved specs implemented**. **Pass 1 is COMPLETE** — all 15 started categories are now
finished (number_theory, geometry, bits, sequences, conversion, calendar_time, misc, io,
strings, loops, text_processing, plus the originally-complete arithmetic/branching/hello/logic).
This document is the plan for the remaining **~503 programs (Passes 2–4)**, plus the lessons
that make them fast to write.

**Read this first if you're picking up Pass 2+:** the catalog is now **hex-first**. Pass 1
ended by converting all arithmetic programs from `bit.*` to `hex.*` (≈4× faster in tight
loops) and adding the `hex/strings.fj` line-buffer macros. Default to `hex.*` for new
programs; reach for `bit.*` only for genuine bit-level manipulation (the `bits` category).
See "Lessons" below before writing anything.

## Before you write a single program — read these, in order

1. **`programs/catalog/CONVENTIONS.md`** — authoritative file format, naming, header,
   testing protocol. Non-negotiable; read it end-to-end.
2. **The `writing-flipjump-stl-code` skill** — how to actually write FlipJump: the
   memory model (`*dw` stride), bit-vs-hex, init macros, the verification loop, the
   "easy to misread" traps, and `reference/quick-signatures.md` for exact arg orders.
   Don't reinvent idioms it already documents.
3. **fjdocs.tomhe.app** — the authoritative macro reference (signatures, `@requires`,
   complexity). Don't guess signatures from memory; look them up. Fallback: the STL
   source under `flipjump/stl/`.

**Verification is mandatory** (per the skill + CONVENTIONS): a program is done only
when it both halts (`Finished by looping…`) AND prints byte-exact expected output.
Verify through the Python module / `reference/fj_verify.py`, never a Windows shell
pipe (CRLF). Run the suite with `pytest --catalog` (or `-k <slug>` for one).

## Tooling (scripts/)

- `add_catalog_program.py` — writes the `.fj` + `.in`/`.out` with LF newlines and
  verifies via the Python flipjump module (bypasses git autocrlf + Windows stdout
  CRLF). Use it; don't hand-create the fixtures.
- `catalog_register.py` — registers a program in the test CSVs; compiles with
  `--werror` so an undeclared `@`/`<` label is rejected at authoring time, not by
  pytest later.
- `sort_catalog_by_duration.py` — keep the test CSVs sorted slowest-first; it
  measurably shortens the parallel compile pass (the longest single compile is the
  critical-path tail).

---

## The remaining work, in four passes

Each program's exact name + spec description is a row in `CATALOG.md` (status
`APPROVED`). Implement in `CATALOG.md` order within a category. Sizes below are the
approved-spec counts still unimplemented.

### Pass 1 — DONE (80 programs, #1030–#1109)

All gaps in the started categories are implemented, hex-converted, and verified
(full-domain Python cross-checks; `pytest --catalog` green). Pass 1 established the
reusable patterns the later passes lean on — read these programs as worked examples:
- **Decimal compute** (number_theory, geometry, calendar_time): `hex.input_dec_uint/int`
  → `hex.add/sub/mul/div/cmp` on a `hex.vec 4` (or `8` when the result exceeds 16 bits)
  → `hex.print_dec_uint/int`. No hand-rolled decimal reader needed.
- **Line storage / tokenizing** (text_processing, strings, loops, misc): the
  `hex/strings.fj` macros (below) plus the token-scan (`instate` bit + per-token
  `(start-ptr, len)`) and parallel-array idioms in `longest_word`, `reverse_words_in_line`,
  `count_unique_words`, `count_word_occurrences`.
- **Fixed-size DP** (`bell_n_param`, `stirling_2nd_small`, `eulerian_n_k_small`):
  compile-time `rep` DP with constant indices + a runtime `copy_if_eq` select — no runtime
  pointers needed when the table is small and bounded.

### Pass 2 — algorithms, data_structures, language_demos (167)

| Category | n | Flavor (see CATALOG.md for the exact rows) |
|---|---:|---|
| algorithms | 68 | sorting/searching/scanning over small fixed arrays read from stdin |
| data_structures | 58 | array/stack/queue/set/lookup over N decimals (`array_count_*` shape) |
| language_demos | 41 | showcase FlipJump features themselves (macros, rep, pointers, self-modification) |

### Pass 3 — puzzles + cryptography‥parsing (209)

| Category | n | Flavor |
|---|---:|---|
| puzzles | 43 | small logic/brute-force puzzles with deterministic output |
| cryptography | 37 | caesar/xor/substitution/checksums on bytes (no real crypto) |
| encoding | 36 | base/hex/run-length/escape encode+decode round-trips |
| interactive | 33 | prompt→read→respond loops driven by scripted `.in` |
| graphics_ascii | 31 | ASCII shapes/grids/charts |
| parsing | 29 | tokenize/validate/evaluate tiny grammars |

### Pass 4 — simulation‥language_meta (127)

| Category | n | Flavor |
|---|---:|---|
| simulation | 27 | step a small state over time (cellular/physics-lite/counters) |
| games | 25 | deterministic game logic (tic-tac-toe judge, dice, etc.) |
| memory_layout | 22 | demonstrate addressing, vectors, pointers, alignment |
| state_machines | 20 | explicit FSMs over an input stream |
| recursion | 18 | recursive macros (`count_down_recursive` shape) |
| language_meta | 15 | meta/self-referential demos of the toolchain |

---

## Lessons learned (catalog-specific — coding lessons are in the skill)

**Hex-first.** New programs use `hex.*` on `hex.vec` numbers, not `bit.*` — ≈4× faster in
tight loops, and it's the maintainer's standing preference. `bit.*` is only for genuine
bit-level work (the `bits` category: shifts, masks, per-bit get/set). Width mapping: a
`bit.vec 16` becomes a `hex.vec 4`; `bit.vec 32` → `hex.vec 8`. **Watch the signatures** —
hex mul/div are NOT in-place like bit's (see the skill's `quick-signatures.md`):
- `hex.mul n, res, a, b` — `res = a*b`; `res` is an output that must NOT alias `a`/`b`.
  (Low-`n` products are two's-complement-correct, so it doubles as signed multiply.)
- `hex.div n, nb, q, r, a, b, div0` — `q=a/b`, `r=a%b`; jumps to `div0` on `b==0`. Arg
  order: widths, OUTPUTS, INPUTS, div0-label. `hex.idiv` is signed.
- `hex.input_dec_uint/int n, dst, error` + `hex.print_dec_uint/int n, x` replace the old
  hand-rolled `read_decimal`/`print_dec` entirely.

**STL line/byte-buffer macros — `hex/strings.fj` (use these, don't re-roll).** All take a
hex.pointer to the buffer:
- `hex.input_ptr_line ptr, len` — read input into `*ptr` until `\n`/0-byte(EOF); `len` := count.
- `hex.print_ptr_text ptr, len` — print `len` bytes from `*ptr`.
- `hex.print_ptr_line ptr, len` — print from `*ptr` until `\n`/0-byte; echoes a terminating
  `\n`; `len` := count (terminator excluded).
A byte buffer is `hex.vec CAP` (one byte per FJ op). For unbounded input/arrays use a
**`reserve`d** region (top-level, zeroed, not stored in the `.fjm`):
`buf:` newline `    reserve dw * 1000000`. The skill's `reference/line-buffer.md` has the
token-scan / parallel-array recipes built on top.

**Reusable idiom kits that carry across categories** (these are catalog-domain, beyond
what the skill documents):
- **EOF sentinel `\0`**: every catalog `.in` ends with `\0`; every reader does
  `bit.if0 8, ch, end` right after `bit.input ch`. `\0` is never data.
- **Number-theory trio** (powers algorithms in Pass 2): `is_prime_into n, flag, x`
  (trial division via `hex.div` remainder; bound the loop with the incremental-square
  trick below), `gcd_into n, dst, a, b` (Euclid), `sum_proper_divisors_into n, dst, x`.
  perfect/abundant/deficient and `lcm=(a/gcd)*b` all reduce to these. Write them in hex
  (`hex.vec 4`); see Pass 1's `wilson_prime_check`/`mersenne_check` for the loop shape.
- **Incremental square for √-bounded loops**: don't `mul` to get `d*d` each step;
  maintain `dsq` via `(d+1)^2 = d^2 + 2d + 1` (`dsq+=d; dsq+=d; dsq+=1; d++`). O(√x)
  adds, no multiply. Used by `is_prime_sqrt_into`.
- **Sequence-generation kit** (Pass 1 sequences + many algorithms): (1)
  `print_sep_dec n, value, first` prints a leading space before every term except the
  first (a `first: bit.bit` flag) → clean space-separated lists, no trailing space.
  (2) "Rotate a fixed register window" for linear recurrences (Lucas/Pell 2-window,
  Perrin/Tribonacci 3-window, …): print front, compute `nxt`, `mov` registers down.
  Figurate numbers avoid `mul` via an arithmetic `delta` that grows by a constant step.
- **Byte ↔ nibble**: a byte's two nibbles are at `ch` (low) and `ch + 4*dw` (high) —
  the same `*dw`-per-bit stride as the case-flip idiom (see skill "Memory model").

**Workflow gotchas (cost real time):**
- **Verification: flipjump is installed editable** (`pip install -e .`), so `fj`,
  `import flipjump`, and `scripts/catalog_register.py` all run the live repo — no stale
  site-packages, no `sys.path` workaround. Register with
  `from catalog_register import register; register(category=…, slug=…, in_bytes=…, out_bytes=…)`
  (compiles `--werror`, byte-checks, appends both CSVs, validates the header vs CATALOG.md).
- **Cross-check the full input domain, not one fixture.** For each program, compare against
  a Python reference over its whole spec range — `flipjump.assemble(...)` once, then
  `run_test_output(fjm, in, out)` over many inputs. This caught 2 real `m==1` edge bugs in
  Pass 1 that the canonical fixture missed.
- **Branch first**: `git checkout -b catalog/<batch> main` BEFORE writing files. Twice
  a batch was committed on `main` and the push failed.
- **Compile cost is flat ~0.18s/program at w=64** (STL macro resolution, not your
  body). ~1200 programs ≈ a few minutes parallel. Keep CSVs sorted slowest-first.
- **UTF-8 source (FIXED)**: `fj_parser.lex_parse_curr_file` now reads source with
  `open('r', encoding='utf-8')`, so non-ASCII source chars no longer depend on the OS
  locale. No `PYTHONUTF8=1` / ASCII-only-header workaround needed anymore.

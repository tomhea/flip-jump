# FlipJump — Running Conclusions

A notebook of observations collected while building the demonstration catalog
under `programs/catalog/`. Populated incrementally during Phases 2 and 3.

Purpose: capture the kind of project-knowledge that is worth carrying across
sessions — what compiles fast vs. slow, where the STL has gaps, recurring
idioms, gotchas that bit me, anything a future me (or you) would benefit from
knowing without re-discovering it.

Updated continuously. Treat entries as time-stamped facts, not durable truth —
the codebase changes underneath them.

## Compile-time pitfalls

- **At `w=64`, every program — even a single-`stl.output` hello — pays a
  ~0.18s base compile cost.** It's the cost of resolving the bit/hex STL macros,
  not the program body. With 31 trivial programs in batch 1 the parallel
  compile took 4.3-5.3s wall (`-n auto`); per-test cost was 0.12-0.27s with
  almost no variance. Implication: 1200 programs at `w=64` would run ~3.6 min
  on the same machine. Acceptable.

- **`stl.startup_and_init_all` adds ~6500 bits of program space** to bring up
  `hex.init` + `stl.ptr_init` + `stl.stack_init 100`. Programs that only need
  `bit.*` math can skip it — count_bytes/count_lines using `bit.inc 16, x` +
  `bit.print_dec_uint 16, x` compiled fine without it.

## STL gaps observed

- **`bit.mul` is unusable in this STL version (pip flipjump + repo both).**
  Calling `bit.mul n, dst, src` fails at macro-resolve with
  "macro mul.mul_add_if(4) is used but isn't defined" (raised from
  `flipjump/stl/bit/mul.fj` line 58). Even a minimal 2-line program triggers
  it; it's not something in my code. The working multiply paths are:
  (a) `hex.mul n, res, a, b` — used by `programs/simple_math_checks/series_sum.fj`
      and `func_tests/func7.fj`, requires `hex.init` and hex-layout operands; or
  (b) **repeated addition** for small multipliers, which keeps everything in
      bit-land. Batch 3 uses (b) via a `mul_into n, dst, addend, times` helper
      (`dst = addend added `times` times`) for mul_single_digits / square_small
      / cube_small. `bit.div` / `bit.idiv`, by contrast, work fine.

- **No `hex.print_dec_uint` exists.** I initially tried it for counter
  printing; the macro that prints a hex value in decimal is `bit.print_dec_uint
  n, x` (operates on `bit.vec n`, not `hex.vec`). The hex namespace has
  `hex.print` (raw bits), `hex.print_as_digit` (hex digit), `hex.print_uint`
  (hex base-16), and `hex.print_int` (signed hex) — but nothing for decimal.
  Workaround: use bit-based counters when decimal output is needed. (Worth
  considering an STL contribution at some point; deferred for now.)

## Pattern library (idioms that recur)

- **`stl.startup` and `stl.loop` live ONLY in `main`.** They are program
  bookends, not function bodies. A helper macro that contains either is
  misshapen — the STL itself follows this rule (search `flipjump/stl/`:
  no `def` body contains `stl.startup` or `stl.loop`). Batch 1's programs
  obey this trivially because everything is in `main`; batch 2 and beyond
  must keep enforcing it when helpers appear.

- **Functionalize the body.** Even for medium-complexity programs, pull
  per-loop and per-parse work into named `def`s rather than stacking them all
  in `main`. This matches how the STL is structured (each STL macro is a small
  focused job; the top-level startup/loop wraps the whole program) and pays
  off on recursion / parsing / sorts where helpers compose. Helper macros
  receive inputs as parameters and reference external data via the `< ...`
  clause; they do NOT define their own `stl.startup` / `stl.loop`.
  See CONVENTIONS.md "Sub-macros" for a worked example.

- **EOF sentinel `\0` in catalog `.in` files.** FixedIO raises
  `IOReadOnEOF` if the program reads past end of input, which surfaces as a
  test assertion failure. Convention: every catalog `.in` file ends with `\0`,
  and every reading program tests `bit.if0 8, ch, end` after `bit.input ch`.
  No program in the catalog ever reads `\0` as data — it's the universal
  termination marker.

- **Single-byte read-and-print loop.** Used by `cat`, `echo_twice`,
  `echo_thrice`, `skip_first_byte` and others:
  ```
  loop:
      bit.input ch
      bit.if0 8, ch, end
      bit.print ch
      ;loop
  end:
      stl.loop
  ```
  Variables go OUTSIDE the macro at top level (`ch: bit.vec 8, 0`) and the
  `def main` references them via the `< ch` clause.

- **Read-line-and-echo.** Used by `hello_user`, `hello_long_user`,
  `hello_two_users`: read until `\n` *or* `\0`, echoing each non-newline byte.
  The `bit.cmp 8, ch, nl, print_ch, end, print_ch` distinguishes data bytes
  (continue) from the line terminator (stop).

- **Bit-toggling for case-flip.** Used by `uppercase_filter` and
  `lowercase_filter`: ASCII upper/lower differ by exactly bit 5 (0x20). After
  range-checking `'a' ≤ ch ≤ 'z'` (or `'A'-'Z'`), toggle that bit with
  `bit.not ch + 5*dw`, print, and toggle back. The `5*dw` is non-obvious —
  each bit takes `dw=2w` bits of address space, so the 6th bit is `5*dw` past
  `ch`, not `5`.

- **Number-theory helper trio (batch 6).** `is_prime_into n, flag, x`
  (trial division 2..x-1, `bit.div` remainder test), `gcd_into n, dst, a, b`
  (Euclid: `while b: a,b = b, a%b`), `sum_proper_divisors_into n, dst, x`
  (loop d=1..x-1, add d where x%d==0). Perfect/abundant/deficient/
  sum_of_divisors all reduce to the proper-divisor sum; `lcm = (a/gcd)*b`
  avoids overflow. All 16-bit. These will carry into later sequence/algorithm
  categories.

- **Byte ↔ hex nibble (batch 6).** `print_hex_nibble`: copy the 4-bit nibble
  into an 8-bit holder, add `0x30` (digits 0-9) or `0x57` (letters a-f).
  `bit.ascii2hex` does the reverse. A byte's two nibbles live at `ch` (low) and
  `ch + 4*dw` (high) — same `*dw`-per-bit stride as the case-flip idiom.

## Speed observations

Batch 1 timings on Windows / `pytest -n auto` (12-core machine):

| Run | Wall (s) | pytest internal (s) | Note |
|---|---|---|---|
| Compile, source-order | 7.34 | 5.31 | baseline |
| Run, source-order | 4.91 | 3.97 | baseline |
| Compile, slowest-first | 5.16 | 4.30 | **~19% faster** |
| Run, slowest-first | 5.16 | 4.23 | dominated by xdist overhead |

Sorting compile rows by per-test duration (slowest first) measurably shortens
total wall-clock time for the compile pass because the longest single test
(`count_bytes` at 0.27s) acts as the critical-path tail. Sorting it to the
front lets the worker that picks it up finish around when the others run out
of short tasks, instead of being last. The run pass shows no improvement —
every run-test is sub-50ms, so xdist's setup + teardown dominate.

Recommendation: keep the CSVs sorted slowest-first as Phase 3 grows. The
sort-and-rerun pattern in `scripts/sort_catalog_by_duration.py` is the tool
for that.

## Cross-program learning order

Foundations slice (batch 1) intentionally orders programs from "no input,
fixed output" → "single-byte read loop" → "read-line loop" → "transform and
echo". The progression keeps the macro vocabulary climbing one level at a
time:
1. `stl.startup` + `stl.output "literal"` + `stl.loop` only.
2. + `bit.input` + `bit.if0` + `bit.print`.
3. + `bit.cmp` for terminator detection.
4. + `bit.inc` + `bit.print_dec_uint` for counters.
5. + `bit.not bit+i*dw` for in-place bit-toggle.

Each later program is the simplest one that uses one new technique.

## Surprises / gotchas

- **Workflow: `git checkout -b catalog/batch-NN-... main` BEFORE writing any
  files.** Twice (batches 8 and 9) I generated + committed a batch while still
  on `main`, then the `git push -u origin <branch>` failed with "src refspec
  ... does not match any". The recovery is safe but wasteful: `git branch
  <branch>` (captures the commit), `git reset --hard origin/main` (rewinds
  local main), `git checkout <branch>`, push. Just branch first.

- **NEVER name a global label `n` or `i` (or `w`, `dw`, `dbit`).** This cost
  me ~30 min in batch 2. A top-level `n: bit.vec 8, 0` silently corrupts
  *every* `bit.*`/`hex.*` macro call in the program, because `n` is the width
  parameter in every STL macro signature (`def cmp n, a, b, ...`) and `i` is
  the conventional `rep(n, i)` loop variable. The symptom is bizarre: the
  program crashes with `ip<2w` or a `runtime-memory-error` at a giant address
  (bit 63 set), often inside an *unrelated* macro like `bit.zero`, after only
  a handful of ops — and the *identical* code with the variable renamed works
  perfectly. Diagnosis is by elimination (rename the vars and the crash
  vanishes). Use descriptive names: `limit`, `idx`, `count`, `val_a`, `bound`,
  `counter`. `hello_iterations` was the first program to hit this (used `n`,
  `i` for limit/index); renamed to `limit`/`idx` and it compiled+ran cleanly.

- **Every inner label must be listed in the `@` clause, or the catalog test
  FAILS even though `fj --asm` "succeeds".** The catalog CSVs set
  `warning_as_errors=True` (column 8), so a label that's defined `label:` and
  used `;label` inside a macro body but omitted from `@ ...` is a *warning*
  under a plain `fj --asm` (compiles fine) but a hard *error* under pytest.
  min_two/max_two hit this in batch 3 (a `done` label missing from `@`). Fix:
  `scripts/catalog_register.py` now compiles with `--werror`, so register
  rejects it at authoring time instead of letting pytest be the first to fail.

- **The `<` clause is mandatory for global data referenced in a macro body.**
  Without it, the compiler reports "Declared a not extern/parameter label:
  nl, ch". The macro signature `def main @ inner-labels < global-data { ... }`
  is the contract — `@` introduces inner labels, `<` declares dependencies on
  externally-allocated data.

- **`bit.print ch` prints one byte; `bit.output ch` prints one BIT.** I
  initially used `bit.output ch` and the output came out as `=D` (the byte
  encoded as 8 bits worth of bits = lots of printables). The correct macro is
  `bit.print n, x` (1-byte form: `bit.print ch` where `ch: bit.vec 8, 0`).

- **Windows shell pipe (`echo "x" | fj`) adds CRLF.** Pytest's internal
  harness uses raw bytes (no CRLF translation), so `.out` files must contain
  ONLY `\n`, never `\r\n`. I lost time on a hello_world output mismatch
  driven by this. The helper `scripts/add_catalog_program.py` writes files
  with explicit LF newlines and verifies via the Python flipjump module
  directly (no subprocess) — bypasses both git's autocrlf and Windows fj's
  stdout translation.

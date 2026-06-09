# Catalog — Pass 4 Handoff (the final pass)

**Status:** Passes 1–3 are complete (902 / 1029 specs; Pass 3 = #1278–#1486). **Pass 4 is the
last 127 specs**, six categories, numbered **#1487–#1613** (continue sequentially in
(category-order, CATALOG.md-row-order)). Finishing Pass 4 completes the catalog (1029/1029).

This is a focused handoff; the master plan and the Pass-1/2/3 lessons live in
[`HANDOFF.md`](HANDOFF.md). Read that, [`CONVENTIONS.md`](CONVENTIONS.md), and the
`writing-flipjump-stl-code` skill before writing — verification is mandatory (compile
`--werror` + byte-exact run; never via a Windows shell pipe).

---

## The workflow that made Pass 3 fast — reuse it verbatim

Author each category with a **per-category Python "oracle-batch" script** (see `scripts/_pass3_*.py`
and the helpers in `scripts/_pass3.py`). The loop, per program:

1. Build the `.fj` body as a Python f-string (use `NL = chr(92)+"n"` for a FlipJump `\n`, `BS` for a
   backslash — never pipe backslash-laden source through bash).
2. Compute the expected `.out` with a tiny **Python oracle** — the spec rule in 2–3 lines — so the
   output is correct-by-construction. Hand-typed expected output just encodes the same mistake twice.
   (Fixed-output programs: the `.out` *is* the spec, write it directly.)
3. `write_fj(cat, slug, body)` (header is auto-pulled from `CATALOG.md`, so it byte-matches) then
   `catalog_register.register(category=, slug=, in_bytes=, out_bytes=, word_size=)` — it compiles
   `--werror`, runs byte-exact via the Python module, and appends both CSV rows idempotently.

Freeze the `#NNNN` assignment for all 127 at the start (extend `scripts/_pass3.py`'s pattern; numbers
start at 1487). Do the spec-comprehension (pick the `.in`, oracle the `.out`) yourself — that's where
correctness lives; the FJ body is the mechanical part.

## Reusable kits that carry into Pass 4

- **Streaming byte loop** — `hex.input b` (byte → `hex.vec 2`) → `hex.if0 2, b, done` (EOF) →
  `hex.cmp 2, b, nl, …` (`\n`) → process. Output a raw byte with `hex.print b`; fixed-width hex with
  `hex.print_as_digit n, b, 0`. Prefer `hex.*` (4× cheaper) — reserve `bit.*` for genuine 1-bit work.
- **Decimal I/O** — `hex.input_dec_uint/int n, dst, error` (stops at `\n`/`\0`) and the new
  **`hex.input_dec_uint/int_until n, dst, stop_byte`** (stop at the first non-digit, returned in
  `stop_byte`, no error) for fields delimited by `,`/`:`/etc.; `hex.print_dec_uint/int` to print.
- **Line buffer** — `hex.input_ptr_line` / `hex.print_ptr_text` (hex/strings.fj). Compare a line to a
  literal by storing the literal in a second buffer and walking both with `read_byte_and_inc` +
  `hex.cmp 2` (no per-literal macro needed).
- **Grid / array** — Mode 1 (constant index `arr + i*dw*cells`) for fixed small grids; Mode 2
  (`ptr_index` / `read_nth_byte` / `write_nth_byte`) for a runtime index — see the skill's
  `reference/array-access.md`.
- **Fixed output** — a single `stl.output "…"` (an `emit_fixed`-style helper); most `language_meta`
  and several `games` programs are pure fixed output.

## Traps (all documented in the skill — each bit Pass 3)

- **Indexed-pointer ops are O(w) at BOTH compile and run.** `read_nth_byte`/`ptr_index` expand to ~`w`
  ops and run ~`w` steps. Never bulk-unroll many of them (a 243× unroll took ~7 min to *assemble*);
  use a runtime loop, minimize indexed ops per iteration, and **drop to `w=32`** when values fit (pass
  `word_size=32` to `register`; the CSV records it). `memory_layout` leans on pointers — keep them in loops.
- **Width-mixing reads OOB, silently.** `hex.<op> n, a, b` reads `n` nibbles of *both* operands;
  `hex.sub hw, idx, two_nibble_const` reads garbage past the constant → wrong answer, compiles clean.
  Match widths (do the op at the narrower width, or declare the constant wide).
- **`@`/`<` clauses** — derive mechanically: `@` = the `name:` labels in the body; `<` = globals the
  body itself names (args count) minus those only the helpers it calls use. Thread `error`/`done`/
  `yes`/`no` labels through helper chains (a macro can only `;label` its own label or a passed one).
- **EOF vs `\0`** — scanning to true end-of-input terminates the run before your `if0` fires; stop on a
  `\n` already in the data, or append a trailing `\0` to the `.in`.

## The one genuinely new technique — `recursion` (18 programs)

Recursive macros run on the **call stack**: `stl.call <label>` / `stl.call <label>, n_params` and
`stl.return` (`flipjump/stl/ptrlib.fj`), with the stack brought up by `stl.startup_and_init_all`.
**Read the worked examples first: `programs/func_tests/func1.fj … func7.fj`** — they show parameter
passing on the stack, return values, and recursion depth. `factorial_recursive` / `fibonacci_recursive`
/ `sum_to_n_recursive` (and power/gcd) are the canonical shapes; keep N small (the specs bound it,
e.g. N ≤ 6–10) so depth stays shallow. The *point* of these is to demonstrate recursion, so use real
`stl.call` recursion, not an iterative loop dressed up.

## Per-category flavor & suggested approach

| Category | n | Flavor & approach |
|---|---:|---|
| **simulation** | 27 | Step a state one tick. Cellular automata dominate the front (`rule_30/90/110_one_step`: read an 8-cell `0/1` state, `next[i] = rule(left,self,right)` with wrap — the rule is an 8-bit truth table indexed by the 3-neighbor pattern; oracle it in Python, implement with bit tests or a small lookup). Also counters and physics-lite steppers. |
| **games** | 25 | Deterministic game logic. `tic_tac_toe_status` reuses the `puzzles/tic_tac_toe_winner` grid-read + win-check; `hangman_*` is line-buffer + per-letter reveal/lives; dice/score are small arithmetic. Mostly grid/string checks you already have patterns for. |
| **memory_layout** | 22 | Demonstrate addressing / vectors / pointers / alignment. `stack_overflow_demo`/`queue_overflow_demo` = fixed-cap-5 push/pop with a bound check; `pointer_basic` = write a value at an address, read it back. Use the pointer macros; N is small so indexed cost is fine. |
| **state_machines** | 20 | Explicit FSM over an input stream. `traffic_light_cycle` rotates a 3-state cycle N times; `dfa_even_zeros`/`dfa_odd_ones` scan a bit string toggling a state bit then accept/reject. Streaming loop + a state register + a transition branch/table. |
| **recursion** | 18 | Recursive macros via `stl.call` (see above). factorial / fibonacci / sum / power / gcd. |
| **language_meta** | 15 | Meta / self-referential. `print_word_size_compile_time` prints the `w` compile-time constant; `print_motto` and the explanation programs are fixed strings (`emit_fixed`); others demo `rep`/macros/self-modification. Mostly fixed-output or one compile-time value. |

## Finishing the catalog

1. **README rows** for the six categories (adapt `scripts/_pass3_readme.py` — same insert-after-the-`|---|` logic, new category list).
2. **Sort the CSVs** slowest-first (`scripts/sort_catalog_by_duration.py`).
3. **Green gate:** `pytest tests/test_fj.py --catalog --compile` and `--run` (both must pass; the new
   sudoku w=32 row shows the override works). If you add an STL macro, also keep `--all` / `--hexlib`
   green and document + test it per `CONVENTIONS.md` "STL extensions" + `../../flipjump_claude_conclusions.md`.
4. **CR loop** — run a strict reviewer until APPROVE. Pass 3's recurring blocking findings were
   **unused data declarations** (not caught by `--werror`) and **forbidden label names** (`n`/`i`/`w`/
   `dw`/`dbit`); sweep for both *before* the review (a quick Python pass over each `.fj` catches them).
5. Mark **Pass 4 DONE** in `HANDOFF.md` → the catalog is complete.

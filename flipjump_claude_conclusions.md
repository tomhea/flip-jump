# FlipJump — Running Conclusions

This notebook has been consolidated. The observations collected while building the
catalog now live where they belong, so the rest of this file was removed (the
guidance was either superseded by fixes, or moved):

- **How to write FlipJump code** (memory model / `*dw` stride, bit-vs-hex, init
  macros, the verification loop, the "easy-to-misread" traps, naming, exact macro
  signatures) → the **`writing-flipjump-stl-code` skill** (`SKILL.md` +
  `reference/`). The authoritative macro reference is **fjdocs.tomhe.app**.
- **Catalog authoring** (the remaining work plan, the reusable idiom kits —
  number-theory trio, sequence-window, incremental-square, EOF `\0` sentinel — the
  workflow gotchas: branch-first, slowest-first CSVs, CRLF-vs-LF, compile-cost
  expectations) → **`programs/catalog/HANDOFF.md`** and **`CONVENTIONS.md`**.

Several entries here were simply **stale** and were deleted, not moved — they
described limitations that have since been fixed: `bit.mul` (works now),
"no hex decimal printer" (now `hex.print_dec_uint/int` + `hex.input_dec_uint/int`),
and the `n`/`i`/`d` naming trap (`rep` iterators are now hygienic; the only
off-limits names are the `w`/`dw`/`dbit` constants, which the compiler now rejects).

## STL additions

Utility macros promoted from per-program catalog helpers. This is the changelog
(rationale + test row, as `CONVENTIONS.md` requires); the **usage** of each lives in its
doc-comment in the `.fj` and in the `writing-flipjump-stl-code` skill, under the noted
reference (where they sit alongside the rest of the utility macros).

- **`hex/strings.fj`** — `hex.input_ptr_line` / `print_ptr_text` / `print_ptr_line`: line &
  byte-buffer I/O over a hex.pointer (scratch kept inline, jumped over). Replaces the
  `read_line_into` / `print_buffer` helpers the Pass-1 storage programs each re-defined.
  Test: `hexlib-strings`. Skill: `reference/line-buffer.md`.

- **`hex/pointers/`** — `hex.ptr_index`, `hex.read_nth_byte/hex`, `hex.write_nth_byte/hex`:
  O(w) runtime *indexed* array access (works for negative index; single-unit — scale the index
  for n-hex cells). Replaces the per-program O(index) `get_at` / `set_at` walk Pass-2 re-defined
  ~22×. Test: `hexlib-nth_pointers`. Skill: `reference/array-access.md` (incl. the O(w)-cost caveat).

- **`hex/cond_jumps.fj`** — `hex.scmp n, a, b, lt, eq, gt`: signed counterpart of `hex.cmp`
  (sign-bias on copies — correct over the whole range, unlike a self-rolled `a-b`-then-test-sign,
  which overflows). Replaces the `scmp4` helper Pass-2 signed programs re-defined ~9×.
  Test: `hexlib-scmp`. Skill: `reference/quick-signatures.md`.

- **`hex/input.fj`** — `hex.input_dec_uint_until` / `hex.input_dec_int_until` (`n, dst, stop_byte`):
  read a decimal field, stop at the first non-digit (returned in the `stop_byte` output), no error
  path. The plain `hex.input_dec_uint/int n, dst, error` are now thin wrappers over them (check the
  returned `stop_byte ∈ {'\n','\0'}`, else jump `error`). Replaces the `read_num` helper Pass-3
  parsing re-defined. Test: `hexlib-input_dec_until`. Skill: `reference/quick-signatures.md`.

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

- **`hex/strings.fj`** (`hex.input_ptr_line`, `hex.print_ptr_text`, `hex.print_ptr_line`) — line /
  byte-buffer helpers, all operating on a hex.pointer to the buffer. Promoted from the
  per-program `read_line_into` / `print_buffer` helpers that the Pass-1 storage programs
  (io / strings / loops / misc / text_processing) each re-defined. They keep their pointer /
  byte-register / counter scratch *inline* (jumped over, like `mul.fj`), so a caller supplies only
  the buffer pointer and a length var. `input_ptr_line` reads until '\n'/0-byte; `print_ptr_text`
  prints len bytes; `print_ptr_line` prints until '\n'/0-byte (echoing a terminating '\n'),
  reporting the count. A byte buffer is `hex.vec CAP` (one byte per FJ op) or a `reserve`d region;
  requires `stl.startup_and_init_all`. Listed last in `stl/conf.json` (depends on hex pointers + I/O).
  Tested by `programs/hexlib_tests/basics1/strings.fj` (`hexlib-strings`).


- **`hex.ptr_index`, `hex.read_nth_byte/hex`, `hex.write_nth_byte/hex`** (in
  `hex/pointers/{pointer_arithmetics,read_pointers,write_pointers}.fj`) — runtime *indexed* array
  access. `ptr_index dst, ptr, index` computes `dst = ptr + index*2w` (the address of the index-th
  dw-aligned op past `*ptr`) using shifts + one add — O(w), independent of `index`, and correct for
  *negative* `index` too (two's-complement). The `read_nth_*` / `write_nth_*` wrappers compose it
  with `read_*` / `write_*`; all SINGLE-unit (one hex / one byte) — for n-hex cells the caller scales the index (`hex.mul`/shift)
  and uses `ptr_index`+`read_hex n`, or stores the array as bytes. The macros use a shared
  `hex.pointers.nth_ptr` scratch (from `ptr_init`), so they have no per-call data. Replaces the
  per-program `get_at` / `set_at` "walk the pointer `index` times" helpers (O(index) each) that the
  Pass-2 programs re-defined ~22×. `@requires hex.init + stl.ptr_init`. Tested by
  `programs/hexlib_tests/basics2/nth_pointers.fj` (`hexlib-nth_pointers`).

- **`hex.scmp n, a, b, lt, eq, gt`** (in `hex/cond_jumps.fj`) — SIGNED two's-complement compare,
  the signed counterpart of `hex.cmp` (which is unsigned). Flips the sign bit (MSB) of *copies* of
  `a,b` (inner scratch, `a,b` unmodified) then unsigned-compares — this maps the signed range
  monotonically onto the unsigned range, so it is correct over the whole range with no subtraction
  (hence no overflow; the naive `a-b`-then-test-sign-bit breaks when the difference overflows).
  Replaces the per-program `scmp4` sign-bias helper that Pass-2 signed programs re-defined ~9×.
  `@requires hex.cmp.init`. Tested by `programs/hexlib_tests/basics1/scmp.fj` (`hexlib-scmp`).

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

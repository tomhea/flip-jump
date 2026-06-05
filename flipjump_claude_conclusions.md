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

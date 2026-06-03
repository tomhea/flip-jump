# `sorts/utils/` — Pluggable helpers for the sort programs

Interchangeable building blocks compiled together with `../bubble_sort.fj`. To
build a runnable program, pick **one** `swap_adjacent` implementation and **one**
memory-access implementation; each pair exercises a different set of pointer
macros, which is the point of having several variants.

| File | Purpose |
|---|---|
| `_hex_memory_access.fj` | `read`/`write`/`xor`-to-pointer via the hex-pointer macros (slower). |
| `_byte_memory_access.fj` | Same interface via the byte-pointer macros (faster). |
| `_swap_adjacent_using_writes.fj` | `swap_adjacent` built on `hex.write_{hex,byte}` (slower). |
| `_swap_adjacent_using_xors.fj` | `swap_adjacent` built on `hex.xor_{hex,byte}_to_ptr` (faster). |

Each file begins with a comment describing how it must be combined.

# `sorts/` — Sorting programs

Sorting programs that double as tests for the memory-access (pointer) macros.
`bubble_sort.fj` is the main program; it is compiled together with one
`swap_adjacent` implementation and one memory-access implementation from
`utils/`, so the same algorithm is exercised against several macro
implementations (hex vs byte access, writes vs xors).

| File / folder | Purpose |
|---|---|
| `bubble_sort.fj` | Inputs a length and then that many hex numbers, bubble-sorts them, and prints them back. |
| `utils/` | Pluggable helper modules (swap and memory-access) compiled with `bubble_sort.fj`. |

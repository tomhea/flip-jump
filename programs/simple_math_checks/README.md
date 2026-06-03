# `simple_math_checks/` — Small binary-math checks

Medium-sized checks for the binary (`bit.*`) math macros — addition,
comparison, division and shifts — plus a small arithmetic-series algorithm that
uses the hex math macros. Each program runs its macro and prints a result
compared against the recorded `.out`.

| File | Purpose |
|---|---|
| `nadd.fj` | `bit.add` (add two 8-bit numbers). |
| `ncmp.fj` | `bit.cmp` (print `<`, `=` or `>`). |
| `bit_div.fj` | `bit.div` / `bit.div_loop` / `bit.idiv` / `bit.idiv_loop`, including signed cases. |
| `div10.fj` | `bit.div10` (repeatedly divide by 10, printing decimal digits). |
| `shra.fj` | `bit.shra` (arithmetic shift-right). |
| `series_sum.fj` | Arithmetic-series sum (`a1`, difference `d`, `n` terms) using hex math macros. |

# `hexlib_tests/div/` — Division tests

Tests for the `hex.div` (unsigned) and `hex.idiv` (signed) macros over a range
of dividend/divisor hex-lengths. Every test program is compiled **together with
`hexlib_div.fj`**, which supplies `stl.startup`, the random `DIV_*` test data,
and the shared test macros (see `tests/tests_tables/test_compile_hexlib.csv`).

| File | Purpose |
|---|---|
| `hexlib_div.fj` | Shared harness: startup, `DIV_*` data, and the `test_div` / `test_idiv` macros. |
| `test4_1.fj` / `test4_2.fj` / `test4_4.fj` | `hex.div`, 4-hex dividend, 1/2/4-hex divisor. |
| `test8_1.fj` / `test8_2.fj` / `test8_4.fj` / `test8_8.fj` | `hex.div`, 8-hex dividend, 1/2/4/8-hex divisor. |
| `test_idiv.fj` | Signed `hex.idiv`. |
| `test_idiv_cases.fj` | Signed `hex.idiv` across all four operand-sign combinations and its optimization variants. |

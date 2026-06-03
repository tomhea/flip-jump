# `multi_comp/` — Multi-file compilation tests

Demonstrates and tests compiling a program from several `.fj` files at once,
including in different file orders and with/without the standard library. The
test suite compiles these files in several combinations (e.g. `defs | a | b | c`
and `defs | a | c | b`) and checks they all produce the same output
(`tests/tests_tables/test_*_fast.csv`).

| File | Purpose |
|---|---|
| `a.fj` | Main file: prints rows of characters using macros from the other files. |
| `a_no_stl.fj` | Main file, no-STL variant: defines its own minimal IO instead of using the standard library. |
| `b.fj` | Helper: defines the `print_aaaa` macro. |
| `c.fj` | Helper: defines the `print_chars` and `println` macros. |
| `defs.fj` | Helper: defines shared constants and macros (`N`, `get_aaaaN`). |

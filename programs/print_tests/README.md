# `print_tests/` — Input/output and printing programs

Small programs that exercise the input and printing macros: echoing input,
printing strings, and printing numbers in hexadecimal/decimal form. They are run
by the fast/medium test categories (`tests/tests_tables/test_*_fast.csv`),
with inputs/outputs under `tests/inout/print_tests/`.

| File | Purpose |
|---|---|
| `hello_world.fj` | Prints "Hello, World!" using the standard library. |
| `hello_world_with_str.fj` | Same, via `bit.print_str` over a `bit.str` string. |
| `hello_no-stl.fj` | Same, but defines its own startup/output (no standard library). |
| `cat.fj` | Echoes input bytes until EOF. |
| `ncat.fj` | Echoes the bitwise-NOT of each input byte until EOF. |
| `hexprint.fj` | Adds two 4-bit numbers and prints the result as a hex digit. |
| `print_as_digit.fj` | Prints bit and hex values as digits. |
| `print_hex_int.fj` | Prints a signed number in hexadecimal form. |
| `print_dec.fj` | Prints numbers in decimal form, one per line. |
| `hex_print_dec.fj` | Decimal-printing coverage for the bit/hex `print_dec_*` macros. |
| `print_int_preserves_input.fj` | Regression: `print_hex_int` / `print_dec_int` must not mutate a negative input. |

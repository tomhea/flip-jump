# `hexlib_tests/` — Test suite for the `hex.*` standard library

An extensive test suite for the hexadecimal macros in `flipjump/stl/hex/`.
Each test drives a macro over many (often random) inputs and prints a result
that is compared against a recorded `.out` file. These are the heaviest tests
in the repo and run under the dedicated `hexlib` speed category
(`tests/tests_tables/test_*_hexlib.csv`).

The tests are grouped by feature into subdirectories:

| Subdirectory | Purpose |
|---|---|
| `basics1/` | Basic hex macros: arithmetic, memory, conditionals, input, printing. |
| `basics2/` | Bit/hex shifts and bit-counting macros. |
| `2params/` | Two-operand macros (`add`/`sub`/`and`/`or`/`cmp`) and their `_n` / `_shifted` variants. |
| `div/` | `hex.div` and signed `hex.idiv` division. |
| `mul/` | `hex.mul` and `hex.add_mul` multiplication. |

Many tests are split into a data/harness pair that is compiled together (see
each subdirectory's README) — for example a `*_test.fj` harness compiled with a
small data file, or `hexlib_div.fj` compiled with each `test*.fj`.

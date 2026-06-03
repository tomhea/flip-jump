# `concept_checks/` — Language-concept demonstrations

Small programs that demonstrate (and exercise) specific FlipJump language
concepts: pointers, type casting, namespaces-as-classes, and memory segments.
They double as regression tests and are run by the test suite via
`tests/tests_tables/test_*_medium.csv`.

| File | Purpose |
|---|---|
| `bit_ptr.fj` | Bit-pointer macros: `bit.ptr_flip`, `bit.ptr_jump`, `bit.ptr_wflip`. |
| `hex_ptr.fj` | Hex-pointer macros: `hex.ptr_flip`, `hex.ptr_jump`, `hex.ptr_wflip`. |
| `casting.fj` | Casting between bit-vectors and hex-vectors (`stl.bit2hex` / `stl.hex2bit`). |
| `pair_ns.fj` | Using a namespace as a class: defines the `Pair` object (two numbers) with `init`/`add`/`print`/`swap` methods. Used by `../pair_ns_tests/`. |
| `segments.fj` | The `segment` / `reserve` directives: reads input digits into reserved memory at fixed addresses and prints the result. |

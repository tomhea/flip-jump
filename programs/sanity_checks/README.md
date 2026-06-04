# `sanity_checks/` — Core-language sanity tests

The smallest, fastest tests in the repo: each one exercises a single core macro
or language feature so that a basic breakage is caught immediately. Run by the
fast test category (`tests/tests_tables/test_*_fast.csv`).

The `macro_*.fj` files are focused "sanity coverage" programs for a family of
standard-library macros; each begins with a comment listing exactly what it
covers.

| File | Purpose |
|---|---|
| `simple.fj` | `stl.skip`, a bare flip, and `#`-expression evaluation. |
| `not.fj` | `bit.not`. |
| `mathbit.fj` | `bit.inc1` (single-bit increment with carry). |
| `mathvec.fj` | `bit.inc` (bit-vector increment). |
| `rep.fj` | The `rep(...)` repetition directive. |
| `testbit.fj` / `testbit_with_nops.fj` | `bit.if` (with and without preceding no-ops). |
| `startup_init_all.fj` | `stl.startup_and_init_all` followed by a basic `hex.sub`/print. |
| `macro_logic.fj` | `bit.and` / `bit.or` / `bit.one`. |
| `macro_mul.fj` | `bit.mul` / `bit.mul_loop` / `bit.mul10`. |
| `macro_rotate.fj` | `bit.rol` / `bit.ror`. |
| `macro_ascii_bin.fj` | `bit.ascii2bin` / `bit.bin2ascii`. |
| `macro_bit_pointer.fj` | `bit.xor_to_ptr` / `bit.ptr_inc` / `bit.ptr_dec` / `bit.ptr_flip_dbit`. |
| `macro_hex_mul.fj` | `hex.mul10`. |
| `macro_hex_comp.fj` | `hex.mov` / `hex.swap` / `stl.comp_flip_if` / `stl.wflip_macro`. |
| `macro_hex_input.fj` | `hex.input_dec_uint` / `hex.input_dec_int`. |
| `macro_hex_minmax.fj` | `hex.min` / `hex.max`. |

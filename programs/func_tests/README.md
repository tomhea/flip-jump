# `func_tests/` — Function-call semantics tests

Programs that exercise the standard-library function machinery —
`stl.call` / `stl.return`, `stl.fcall` / `stl.fret`, and the
`hex.push*` / `hex.pop*` stack macros — built on top of
`stl.startup_and_init_all`. Each file has a top comment describing the exact
call pattern it checks; the expected output is in `tests/inout/func_tests/`.

| File | Purpose |
|---|---|
| `func1.fj` | A parameterless function call. |
| `func2.fj` | A diamond call-stack (`main->a->c` and `main->b->c`). |
| `func3.fj` | `push_hex` / `pop_hex` around an empty function call. |
| `func4.fj` | `ptr_flip_dbit` together with function calls. |
| `func5.fj` | `xor_hex_from_ptr` / `xor_hex_to_ptr` with function calls. |
| `func6.fj` | Unsigned multiplication of two numbers through the call stack. |
| `func7.fj` | Squared distance between pairs of points — a complex, repeated call stack with many `push`/`pop n`. |

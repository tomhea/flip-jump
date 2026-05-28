# `bit/` — bit-level macros

This folder builds bit-oriented variables, arithmetic, I/O, and pointers on top of FlipJump's single-instruction substrate. The macros here treat memory as flat bit arrays (`bit.vec n`) where each bit lives in one `dw`-aligned slot.

## What lives here

| File              | What it provides                                                                                     |
|-------------------|------------------------------------------------------------------------------------------------------|
| `memory.fj`       | `bit`, `vec`, `zero`, `one`, `mov`, `swap`, `unsafe_mov` — declaring and moving bits.                |
| `logics.fj`       | `xor`, `or`, `and`, `not`, plus `exact_*`, `double_*`, `address_and_variable_xor` building blocks.   |
| `math.fj`         | `inc`, `dec`, `add`, `sub`, `neg` and the `inc1` / `add1` carry-aware single-step variants.          |
| `mul.fj`          | `mul`, `mul10`, `mul_loop`, plus the `mul_add_if` building block.                                    |
| `div.fj`          | `div`, `idiv`, `div_loop`, `idiv_loop`, `div_step`, plus the decimal `div10` family.                 |
| `shifts.fj`       | `shl`, `shr`, `shra` plus the rotating `rol`, `ror`.                                                 |
| `cond_jumps.fj`   | `if`, `if0`, `if1`, `cmp` (3-way), `cmp_next_eq` per-bit step.                                       |
| `input.fj`        | `input_bit`, `input` (1 byte), `input` (n bytes, little-endian).                                     |
| `output.fj`       | `output`, `print`, `print_str`, `print_as_digit`, `print_dec_*`, `print_hex_*`, decimal `div10_step`.|
| `casting.fj`      | `str` (string literals), `bin2ascii`, `dec2ascii`, `hex2ascii`, and their `ascii2*` inverses.        |
| `pointers.fj`     | `ptr_init`, `ptr_jump`, `ptr_flip`, `ptr_wflip`, `ptr_flip_dbit`, and the `xor_*_ptr` operations.    |

## Conventions

- A **bit** is a single bit stored at one `dw`-aligned address.
- A **`bit[:n]`** (or `bit.vec n`) is `n` bits, slot `i` at address `base + i*dw`.
- Macros with an `n` parameter operate on the first `n` slots from a base address. `n > 0` is always assumed — passing `n = 0` to any vector macro is undefined behaviour.
- Variables intended as data (`bit`, `bit.vec`) must be placed in a region of memory that is **never executed** — typically below `stl.loop`. Running them as-is is undefined behaviour.
- Macros that depend on init state (`bit.pointers.ptr_init`) carry a `// @requires` line.
- Macros with non-obvious preconditions (e.g. `times <= n` in shifts) carry a `// @Assumes:` line.

For the rendered, navigable reference of every macro see <https://fjdocs.tomhe.app/stl/bit/>.

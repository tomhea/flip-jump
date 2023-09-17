# FlipJump Standard Library

The stl (**ST**andard-**L**ibrary) is a collection of FlipJump files, each a collection of **highly-optimized** and **[tested](../../tests/README.md)** macros, that are free to use by any FlipJump program that may benefit from it.

It mainly offers binary/hexadecimal data-structures, mathematical and logical operations, conditional jumps, pointers, casting, and input/output.

These FlipJump files result from a lot of research, runs, and many tests. 

**@note**: The faster mathematical macros are under the `hex` namespace.


# The Files

### [runlib.fj](runlib.fj)
This file contains constants and initialization macros.

Offers outputting constant chars/strings.

**@note**: It should be the first file in the compilation order.

### [bit/](bit/)
Defines the `bit` data-structure (for binary variables).

Offers macros for manipulating binary variables and vectors (i.e. numbers):

- [memory.fj](bit/memory.fj) - bit/vec, zero, one, mov, swap
- [cond_jumps.fj](bit/cond_jumps.fj) - if, cmp
- [logics.fj](bit/logics.fj) - xor, or, and, not
- [casting.fj](bit/casting.fj) - casting between bits and ascii
- [input.fj](bit/input.fj) - input into bit variables
- [output.fj](bit/output.fj) - output bits, bytes; print as hex/decimal
- [shifts.fj](bit/shifts.fj) - bit-shift left/right, bit-rotate left/right
- [math.fj](bit/math.fj) - inc, dec, add, sub
- [pointers.fj](bit/pointers.fj) - bit-vec pointers: flip, jump, xor_to, xor_from, inc/dec; pointers init

### [hex/](hex/)
Defines the `hex` data-structure (for hexadecimal variables).

**They are smaller and faster than 4 `bit`s.** 

Offers macros for manipulating hexadecimal variables and vectors (i.e. numbers):

- [memory.fj](hex/memory.fj) - hex/vec, zero, xor_by, set, mov, swap
- [cond_jumps.fj](hex/cond_jumps.fj) - if, cmp
- [logics.fj](hex/logics.fj) - xor, or, and, not
- [input.fj](hex/input.fj) - input bits into hex, input ascii as hex
- [output.fj](hex/output.fj) - output hex as bits/bytes; print as hex-number (in ascii)
- [shifts.fj](hex/shifts.fj) - shift left/right by 1 bit/hex
- [math_basic.fj](hex/math_basic.fj) - inc/dec, neg, count_bits, sign_extend
- [math.fj](hex/math.fj) - add/sub, {add/sub}_shifted, {add/sub}_constant
- [pointers.fj](hex/pointers.fj) - hex-vec pointers: flip, jump, xor_to, xor_from; stack/pointers init
- [advanced_pointers.fj](hex/advanced_pointers.fj) - hex-vec pointers: ptr/sp - inc/dec/add/sub, all push/pop
- [tables_init.fj](hex/tables_init.fj) - initializes the "results-tables" for the next hex macros: or,and, add,sub, cmp, mul

### [mathlib.fj](mathlib.fj)
Offers multiplication and division macros for bit/hex variables.

**@note**: The hex.div fails test as for now. You can use the bit version and castings.

### [casting.fj](casting.fj)
Offers casting between bits and hexes.

### [ptrlib.fj](ptrlib.fj)
Offers the concept of pointers, i.e. reading, jumping to, and flipping bits, directly from a pointer (i.e. a bit-variable that holds an address).

Also offers a stack and functions based on these pointers.

### [conf.json](conf.json)
A configurable json file that maintains ordered lists of the standard library files. 


# Documentation & Complexities
Every macro is documented with:
- Its **time complexity** (and if it's significantly different, the **space complexity** as well).
  - The complexities use the **@** sign, which is the log2 of the total number of fj ops in this program (can be it usually will be between 15-25).
  - The reason for this _weird_ log complexity, is that `wflip address, value` has the complexity of the number of on-bits in _address_; And it is widely used.
- An explanation about what the macro does (usually in a python-like syntax).
- The type of each of the parameters (bit/hex/bit.vec/hex.vec/constant/address and so on).
  - if a parameter is called bit/hex, it is a bit/hex variable (of size 1).
  - if a parameter (in a macro declared under the bit/hex namespaces) is used in the documentation as an array (x[:n], ascii[:8], etc.) - it is a bit/hex vector of the specified size; and that size is a size-constant.
- Optionally, what the macro assumes about the parameters, and what can you assume about the result.

## Fast search:
If you want to get to the source of a macro named some_macro (to view the macro's documentation, or its implementation), search in the stl/ folder for `'def some_macro '`.

I created an [autohotkey script](../../ide-extensions/pycharm/fj-pycharm-def-finder.ahk) that jumps to the definition in pycharm by pressing Ctrl+Shift+Click on the macro name, inside the flipjump repo.


# The Standard Library Basics

## Reserved Names
The standard library reserves all the labels under the "stl", "bit", and "hex" namespaces.

No other labels are reserved or used by the standard library.


## Startup Macros
FlipJump programs start running at address 0. The IO opcode is placed at address 2w, and a normal program just skips above it and then starts.

To keep things simple, we wrote the ```stl.startup``` macro. It should be the first used macro/op in your program. If you are using multiple files, then **it should only be declared once**, at the start of the first file.

Basically, The first line in a FlipJump program should be ```stl.startup```.

Instead, you can also use the ```stl.startup_and_init_all``` macro, which does the startup, and also every ```init``` macro that's exist in the standard library.

## Padding
We decided to make the padding a part of the FlipJump assembly.

```pad n``` - A special assembly-op that fills the current address with arbitrary fj ops, until the address is divisible by (n*dw).

We made it a part of the FlipJump assembly, in spite of the fact that padding CAN be defined with the other primitives of the FlipJump assembly:
```c
// @note - padding can also be implemented in fj itself! (but the saved-word pad is more compile-time efficient)
//   pad zeros up to the address
def pad address @ pad_start {
  pad_start:
    rep((0-pad_start/(2*w))%address, i) fj 0, 0
}
```
By making the padding a part of the assembly, we can (and do) **utilize the free space** we just gained.

The free space, gained by the padding, is also **being used for storing fj-ops that will be created by future ```wflip```s**. 

That way, **using the ```pad n```** macros won't only **not waste up space**, but might even **save space**; That's because ```wflip```s to a padded address are smaller (less 1's in that address binary representation -> less fj-ops will be created for ```wflip```ing there).

# Contribute

The FlipJump philosophy is to be the simplest language of all, that can do any modern computation.

FlipJump should be below the OS, as it's a cpu-architecture after all.

The FlipJump stl should be minimalistic, efficient in both space and time, and offer macros similar to x86 ops.

The generic stl macro should look like `macro_name n dst src` for an n-bit/hex variable, with dst being the destination-variable, and src being the source-variable.
- e.g. the [hex/math.fj](hex/math.fj) / `hex.add n, dst, src`. 

For more information about contributions, see [I-Want-To-Contribute Thread](https://github.com/tomhea/flip-jump/discussions/148) and [CONTRIBUTING.md](../../CONTRIBUTING.md).


# Read More

You can explore the full list of all macros from the [esolangs page](https://esolangs.org/wiki/FlipJump#The_Standard_Library).

If you are new to the FlipJump standard-library, Start by reading the [bit/logics.fj](bit/logics.fj) standard library file (start with `xor`). You can continue to the [bit.if](bit/cond_jumps.fj) macro afterwords. That's where the FlipJump magic begins.

If you want to understand how the deep optimized hex macros work, understand how the next macros are implemented: [hex.exact_xor](hex/logics.fj), [hex.output](hex/output.fj), [hex.inc1](hex/math_basic.fj), and [hex.add](hex/math.fj) (understand the concept of the [lookup tables](https://esolangs.org/wiki/FlipJump#Lookup_Tables).

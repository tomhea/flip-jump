# FlipJump Standard Library

The stl is a collection of FlipJump files, each a collection of **highly-optimized** and **[tested](../tests)** macros, that are free to use by any FlipJump program that may benefit from it.

It mainly offers binary/hexadecimal data-structures, mathematical and logical operations, conditional jumps, pointers, casting, and input/output.

These FlipJump files result from a lot of research, runs, and tests. 

**@note**: The faster mathematical macros are under the `hex` namespace.


# The Files

### [runlib.fj](runlib.fj)
This file contains constants and initialization macros.

**@note**: It should be the first file in the compilation order.

### [bit/](bit/)
Defines the `bit` data-structure (for binary variables).

Offers macros for manipulating binary variables and vectors (i.e. numbers).

You can find conditional jumps, memory manipulations, and logical and arithmetical macros. 

### [mathlib.fj](mathlib.fj)
Offers multiplication and division macros for bit/hex variables.

**@note**: The hex.div fails test as for now. You can use the bit version and castings.

### [hexlib.fj](hexlib.fj)
Defines the `hex` data-structure (for hexadecimal variables), which is smaller and faster than `bit`. 

Offers macros for manipulating hexadecimal variables and vectors (i.e. numbers).

You can find conditional jumps, memory manipulations, and logical and arithmetical macros. 

### [declib.fj](declib.fj)
Defines the `dec` data-structure (for decimal variables).

It is not implemented yet, but it would offer conditional jumps, memory manipulations, and arithmetical macros for manipulating decimal variables. 

### [iolib.fj](iolib.fj)
Offers outputting chars, strings. also outputting bit and hex variables as binary, hexadecimal, ascii, or decimal.

Offers input macros for the bit and hex variables, as numbers or as ascii.

Offers casting between different variable types.

### [ptrlib.fj](ptrlib.fj)
Offers the concept of pointers, i.e. reading, jumping to, and flipping bits, directly from a pointer (i.e. a bit-variable that holds an address).

Also offers a stack and functions based on these pointers.

### [conf.json](conf.json)
A configurable json file that maintains ordered lists of the standard library files. 


# Contribute

The FlipJump philosophy is to be the simplest language of all, that can do any modern computation.

FlipJump should be below the OS, as it's a cpu-architecture after all.

The FlipJump stl should be minimalistic, efficient in both space and time, and offer macros similar to x86 ops.

The generic stl macro should look like `macro_name n dst src` for an n-bit/hex variable, with dst being the destination-variable, and src being the source-variable.
- e.g. the [hexlib.fj](hexlib.fj) / `hex.add n, dst, src`. 


# Read More

You can explore the full list of all macros from the [esolang page](https://esolangs.org/wiki/FlipJump#The_Standard_Library).

If you are new to the FlipJump standard-library, Start by reading the [bit/logics.fj](stl/bit/logics.fj) standard library file (start with `xor`, `if`). That's where the FlipJump magic begins.

# FlipJump Source Code

## The FlipJump Macro-Assembler

// TODO - explain in one/two sentences about each file.
//  explain the assembler pipeline
//  explain how to call the assembler

## The FlipJump Interpreter

// TODO - explain in one/two sentences about each file
//  explain how the interpreter works (dictionary) and what is supports (unaligned-access?)
//  explain how to call the interpreter
//  explain about the debugger and its capabilities

// explain about generated label names




An example fj [hello-world](programs/print_tests/hello_no-stl.fj) program, not using the standard library.


# Project Structure

**[src](src)** (assembler + interpreter source files):
  - fj_parser.py    - pythonic lex/yacc parser.
  - preprocessor.py - unwind all macros and reps.
  - assembler.py    - assembles the macroless fj file.
  - fjm_run.py      - interpreter assembled fj files.
  - defs.py         - classes/functions/constants used throughout the project.
  - fjm.py          - read/write .fjm (flip-jump-memory) files.
  - fj.py           - the FlipJump Assembler & Interpreter script.
other branches:
  - [cpp_fji/](https://github.com/tomhea/flip-jump/tree/cpp-interpreter/src/cpp_fji)        - the cpp interpreter (much faster, about 2Mfj/s).
  - [riscv2fj/](https://github.com/tomhea/flip-jump/tree/riscv2fj/src/riscv2fj)       - translates a riscv-executable to an equivalent fj code.


# Read More

A very extensive explanation can be found on the [GitHub wiki page](https://github.com/tomhea/flip-jump/wiki/Learn-FlipJump).

More detailed explanation and the **specifications of the FlipJump assembly** can be found on the [FlipJump esolangs page](https://esolangs.org/wiki/FlipJump).

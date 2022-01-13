# FlipJump

FlipJump is an Esoteric language ([FlipJump esolangs page](https://esolangs.org/wiki/FlipJump)), with just 1 operation:  
- Flip a bit, then (unconditionally) jump.  
- The operation takes 2 memory words, then flips (inverts) the bit referenced by the first word, and jumps to the address referenced by the second word.  

This project is both a **Macro Assembler** and a **Standard Library** to the language.

## Hello, World!

A simple fj [hello-world](tests/hello_no-stl.fj) program, not using the standard library:

```c
def startup @ code_start > IO  {
    ;code_start
  IO:
    ;0
  code_start:
}


def output_bit bit < IO {
    IO + bit;
}
def output_char ascii {
    rep(8, i) output_bit ((ascii>>i)&1)
}

def end_loop @ loop_label {
    loop_label:
    ;loop_label
}

    startup
    
    output_char 'H'
    output_char 'e'
    output_char 'l'
    output_char 'l'
    output_char 'o'
    output_char ','
    output_char ' '
    output_char 'W'
    output_char 'o'
    output_char 'r'
    output_char 'l'
    output_char 'd'
    output_char '!'
    
    end_loop

```

The FlipJump assembly supports a ```str "Hello, World!"``` syntax for initializing a variable with a string value (```str``` is defined in iolib.fj)  
Look at [tests/hello_world.fj](tests/hello_world_with_str.fj) program using print_str macro ([stl/iolib.fj](stl/iolib.fj)) for more info.

Note that all of these macros are already implemented in the standard library:
- startup      in runlib.fj
- end_loop     in bitlib.fj (loop)
- output_char  in iolib.fj
- output       in iolib.fj  (for printing string consts, e.g. output "Hello, World!")

# How to run?

```bash
>>> fj.py hello.fj --no-stl
Hello, World!
```

  - The --no-stl flag tells the assembler not to include the standard library. The flag is needed as we implemented the macros ourselves.
  - You can use the -o flag to save the assembled file for later use too.
  - You can use the -t flag for testing the run with the expected outputs.

You can also assemble and run separately:

```bash
>>> fja.py hello.fj -o hello.fjm --no-stl
>>> fji.py hello.fjm
Hello, World!
```

- The first line will assemble your code (w=64 as bits default).
- The second line will run your code.

Moreover - you can run multiple test programs with defined input (.in file), and compare the outputs (with .out file):

```bash
>>> fji.py assembled/ --tests inout/
...
All tests passed! 100%
```

- The first path is the directory of the assembled .fjm test files.
- The second path is the directory of the corresponding .in and .out files (same name as the test.fjm name, but with a different extension).
- The tests will be run one at a time. For each failed test, a UNIX-like diff will be printed.

For example, you can test the entire FlipJump project (using all the tests in the tests/ dir) by:

```bash
>>> fja.py tests --tests
...
>>> fji.py tests/compiled --tests tests/inout
...
All tests passed! 100%
```

You can also use the faster (stable, but still in development) cpp-based interpreter (under src/cpp_fji):

```bash
>>> fji hello.fjm
Hello, World!
```


# Project Structure

**src** (assembler + interpreter source files):
  - cpp_fji/        - the cpp interpreter (much faster, about 2Mfj/s).
  - riscv2fj/       - translates a riscv-executable to an equivalent fj code.
  - fj_parser.py    - pythonic lex/yacc parser.
  - preprocessor.py - unwind all macros and reps.
  - assembler.py    - assembles the macroless fj file.
  - fjm_run.py      - interpreter assembled fj files.
  - defs.py         - classes/functions/constants used throughout the project.
  - fjm.py          - read/write .fjm (flip-jump-memory) files.
  - fja.py          - the FlipJump Assembler script.
  - fji.py          - the FlipJump Interpreter script.
  - fj.py           - the FlipJump Assembler & Interpreter script.

**stl** (standard library files - macros):
  - runlib.fj   - constants and initialization macros.
  - bitlib.fj   - macros for manipulating binary variables and vectors (i.e. numbers).
  - mathlib.fj  - advanced math macros (mul/div).
  - hexlib.fj   - macros for manipulating hexadecimal variables and vectors.
  - declib.fj   - macros for manipulating decimal variables and vectors.
  - iolib.fj    - input/output macros, bit/hex/dec casting.
  - ptrlib.fj   - pointers, stack and functions.

**tests** (FlipJump programs), for example:
  - compiled/   - the designated dir for the assembled test/ files.
  - inout/      - .in and .out files for each test in the folder above.
  - calc.fj     - command line 2 hex/dec calculator, ```a [+-*/%] b```.
  - func.fj     - performs function calls and operations on stack.
  - hexlib.fj   - tests the basic macros in stl/hexlib.fj.
  
# Read More

A very extensive explanation can be found on the [github wiki page](https://github.com/tomhea/flip-jump/wiki/Learn-FlipJump).

More detailed explanation and the specifications of the FlipJump assembly can be found on the [FlipJump esolangs page](https://esolangs.org/wiki/FlipJump).

Start by reading the [bitlib.fj](stl/bitlib.fj) standard library file. That's where the FlipJump magic begins.

You can also write and run programs for yourself! It is just [that](#how-to-run) easy :)

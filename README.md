# FlipJump

FlipJump is the simplest programing language.<br>
Yet, it can do **any modern computation**.

It's an Esoteric language ([FlipJump esolangs page](https://esolangs.org/wiki/FlipJump)), with just 1 operation `a;b`:  
- `not *a; jump b`

Which means - **Flip** a bit, then **Jump**.

The operation takes 2 memory addresses - it flips (inverts) the bit the first address points to, and jumps to (continue execution from) the second address.  

This project is a **Macro Assembler**, an **Interpreter** and a **Tested Standard Library** to the language.

This calculator was built with only FlipJump ([source](programs/calc.fj)):
![Calculations using only FlipJump](res/calc.gif)

## Hello, World!

A simple fj [hello-world](programs/print_tests/hello_no-stl.fj) program, not using the standard library:

```c
def startup @ code_start > IO  {
    ;code_start
  IO:
    ;0              // the second op is reserved for Input/Output.
  code_start:
}


def output_bit bit < IO {
    IO + bit;       // flipping IO+0 outputs 0; flipping IO+1 outputs 1.
}
def output_char ascii {
    rep(8, i) output_bit ((ascii>>i)&1)
}

def end_loop @ loop_label {
    loop_label:
    ;loop_label     // fj finishes on a self loop
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

The FlipJump assembly supports a ```"Hello, World!"``` syntax for initializing a variable with a string value.
Look at the [hello_world.fj](programs/print_tests/hello_world.fj) program for more info.

Note that all of these macros are already implemented in the standard library:
- startup      in [runlib.fj](stl/runlib.fj)
- end_loop     in [bitlib.fj](stl/bitlib.fj) (loop)
- output_char  in [iolib.fj](stl/iolib.fj)
- output       in [iolib.fj](stl/iolib.fj)  (for printing string consts, e.g. output "Hello, World!")

# How to download?

```bash
>>> git clone https://github.com/tomhea/flip-jump.git
Cloning into 'flip-jump'...
>>> cd flip-jump
>>> pip install -r requirements.txt
```

# How to run?

```bash
>>> python src/fj.py programs/hello_world.fj
Hello, World!
```
![Hello World in FlipJump](res/hello.gif)

  - The --no-stl flag tells the assembler not to include the standard library. for example: `python src/fj.py programs/hello_no-stl.fj --no-stl`.
  - the -w [WIDTH] flag allows compiling the .fj files to a WIDTH-bits memory width. WIDTH is 64 by default.
  - You can use the -o flag to save the assembled file for later use too.
  - you can find all the different flags with `python src/fj.py -h`.

You can also **[Test the project](tests/README.md)** with the project's tests, and with your tests.

You can also assemble and run separately:

```bash
>>> fj.py --asm hello.fj -o hello_world.fjm
>>> fj.py --run hello_world.fjm
Hello, World!
```

- The first line will assemble your code.
- The second line will run your code.

You can also use the faster [cpp-based interpreter](https://github.com/tomhea/fji-cpp):

```bash
>>> fji hello.fjm -s
Hello, World!
```

# Project Structure

**[src](src/README.md)** (assembler + interpreter source files):
  - fj.py           - the FlipJump Assembler & Interpreter script.
  - fjm.py          - read/write .fjm (flip-jump-memory) files.
  - fjm_run.py      - interpret / debug assembled fj files.
  - fj_parser.py    - pythonic lex/yacc parser.
  - preprocessor.py - unwind all macros and reps.
  - assembler.py    - assembles the macro-less fj file.
  - [more...](src/README.md)

**[stl](stl)** (standard library files - macros. [list of all macros](https://esolangs.org/wiki/FlipJump#The_Standard_Library)):
  - runlib.fj   - constants and initialization macros.
  - bitlib.fj   - macros for manipulating binary variables and vectors (i.e. numbers).
  - mathlib.fj  - advanced math macros (mul/div).
  - hexlib.fj   - macros for manipulating hexadecimal variables and vectors.
  - declib.fj   - macros for manipulating decimal variables and vectors (to be implemented).
  - iolib.fj    - input/output macros, bit/hex/dec casting.
  - ptrlib.fj   - pointers, stack and functions.
  - conf.json   - standard library list file.

**[programs](programs)** (FlipJump programs), for example:
  - [hello_world.fj](programs/print_tests/hello_world.fj)  - prints hello world :)
  - [calc.fj](programs/calc.fj)     - command line calculator for 2 hex/dec numbers: ```a [+-*/%] b```.
  - [func_tests/](programs/func_tests)     - performs function calls and operations on stack.
  - [hexlib_tests/](programs/hexlib_tests)   - tests for the macros in stl/hexlib.fj.
  - [quine16.fj](programs/quine16.fj)  - a 16-bits quine by [lestrozi](https://github.com/lestrozi); when assembled with `-w16 -v0` - prints itself.
  - [pair_ns.fj](programs/concept_checks/pair_ns.fj)  - simulating the concept of a Class using a namespace.
  - [print_dec.fj](programs/print_tests/print_dec.fj)    - prints binary variables as decimals.
  - [multi_comp/](programs/multi_comp) - simulates a big project (compilation of multiple files).

**[tests](tests/README.md)** (FlipJump programs), for example:
  - compiled/   - the designated directory for the assembled tests files.
  - inout/      - .in and .out files for each test in the folder above.
  - conftest.py - pytest configuration file.
  - test_fj.py  - tests for compilation and running ([how to run](tests/README.md#run-the-tests)).
  - test_compile_*.csv  - all compilation tests arguments ([compile test format](tests/README.md#compile-csvs-format)).
  - test_run_*.csv      - all running tests arguments ([run test format](tests/README.md#run-csvs-format)).
  - conf.json   - tests list file.


# Read More

A very extensive explanation can be found on the [GitHub wiki page](https://github.com/tomhea/flip-jump/wiki/Learn-FlipJump).

More detailed explanation and the **specifications of the FlipJump assembly** can be found on the [FlipJump esolangs page](https://esolangs.org/wiki/FlipJump).

Read more about the [flip-jump source files](src/README.md) and [how to run the tests](tests/README.md). 

If you want to contribute to this project, read the [CONTRIBUTING.md](CONTRIBUTING.md) file, and take a look at the [Discussions](https://github.com/tomhea/flip-jump/discussions/148).

If you are new to FlipJump and you want to learn how modern computation can be executed using FlipJump, Start by reading the [bitlib.fj](stl/bitlib.fj) standard library file (start with `xor`, `if`). That's where the FlipJump magic begins.

You can also write and run programs for yourself! It is just [that](README.md#how-to-run) easy :)


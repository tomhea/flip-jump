# FlipJump

FlipJump is an Esoteric language, with 1 operation: <br>
- Flip a bit, then (unconditionally) jump. <br>
- The operation takes 2 memory words, then flips (inverts) the bit referenced by the first word, and jumps to the address (which is the second word). <br>

This project supplies an **Macro Assembler** and **Standard Library** to the language.

If you are intrigued with what can be done, and how to use the assembler / standard library, **Read *conventions.txt***. <br>

### Hello, World!

```c
.startup

.print_str 20 str       // prints the string (until the implicit '\0'), and at most 20 characters.
.loop               // macro for ;$-dw - the run ends with a simple self-loop.
                    // $ is the next op address, and dw is the flip-jump opcode size (Double-Word).

str:
    ..string "Hello, World!\n(:"
```

Then get a good undertanding - follow the testbit.fj code, and follow the macros it uses (especialy the .if, which is based on the .xor):

```c
.startup        // taken from lib64.fj
.if x l0 l1     // taken from bitlib.fj

l0:
    ..output 'Z'    // syntactic-sugar for: do IO[bit] for bit in 01011010 (lsb to msb representation of 'Z'==5A)
    .loop
l1:
    ..output '1'
    .loop

x:
    .bit0           // bit0 => 'Z',  bit1 => '1'
```

# How to run?

```py
import run

run.assemble_and_run('input_file.fj')
```

- It will assemble your code with the standard library files (64 as bits default), and then run.
- It will create temp middle-files, such as the binary file, and the no_macros.fj file.

More options with assemble_and_run():
- Add an input with the defined_input argument.
- You can make the temp files non-temp too (just add the wanted paths to the call).

You can also execute the assemble and run separately:

```py
import run
import assembler

assembler.full_assemble(input_files, output_file)
run.run(output_file)
```

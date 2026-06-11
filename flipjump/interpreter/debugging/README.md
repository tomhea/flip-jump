# Debugging FlipJump Programs
Programs won't work on their first run. They just can't. That's why we support the next debugging flags.

- No debugging flags at all: Shows the last 10 executed addresses of tests that failed their run (i.e. finished not by looping). 
- `-d [PATH]`: Save debug information: Adds [very extensive label names](../../../tests/README.md#example-label-name-youll-get-with-using---debuginfo-len), Which are like a "**macro-stack**" for each of the last executed address. (can be used with `--debug-ops-list LEN`)
- `--debug-ops-list LEN`: Shows the last _LEN_ executed addresses (instead of 10). (can be used with `-d`)
- `-b NAME [NAME ...]`: Places breakpoints at every specified label NAMEs (note that label names are long: [more information about labels](../../README.md#generated-label-names)). (requires `-d`)
- `-B NAME [NAME ...]`: Places breakpoints at every label that contains one of the given NAMEs. (requires `-d`)

The debugger can single-step, read-memory, read flipjump variables (bit/hex/byte, and their vectors), continue, or skip forward a fixed number of opcodes.

The debugger is a CLI (no GUI dependency): at a breakpoint it prints the current address (with its macro-stack label), and prompts for the next action in the terminal - so it works over ssh and in CI (EOF/empty answers pick the safe default, Continue All). A session looks like this:

```
$ fj my_program.fj -d -B my_loop
  program break
==== Breakpoint ====
Address 0x180:
    my_loop.

2 ops executed.

flip 0x0:
    stl.startup -> ... -> :start:.
jump 0x180:
    my_loop.
  1. Read Memory
  2. Single Step
  3. Skip 10
  4. Skip 100
  5. Continue
  6. Continue All  (default)
choice> 1

==== Debug: read memory address ====
What memory-word would you like to read? ...
> 0x80

==== Read Memory ====
Reading 0x80:
memory[0x80] = 0  (or 0x0).

This address also goes by this label name:
0x80:
    stl.IO
```

Choices are picked by number or by a unique name prefix (`single` selects Single Step).

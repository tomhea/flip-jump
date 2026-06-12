# Debugging FlipJump Programs
Programs won't work on their first run. They just can't. That's why we support the next debugging flags.

- No debugging flags at all: Shows the last 10 executed addresses of tests that failed their run (i.e. finished not by looping). 
- `-d [PATH]`: Save debug information: Adds [very extensive label names](../../../tests/README.md#example-label-name-youll-get-with-using---debuginfo-len), Which are like a "**macro-stack**" for each of the last executed address. (can be used with `--debug-ops-list LEN`)
- `--debug-ops-list LEN`: Shows the last _LEN_ executed addresses (instead of 10). (can be used with `-d`)
- `-b NAME [NAME ...]`: Places breakpoints at every specified label NAMEs (note that label names are long: [more information about labels](../../README.md#generated-label-names)). (requires `-d`)
- `-B NAME [NAME ...]`: Places breakpoints at every label that contains one of the given NAMEs. (requires `-d`)

At a breakpoint the debugger prints the current address (with its macro-stack label) and waits
for a command in the terminal. Type `h` for the full list; the commands are:

| command | does |
|---|---|
| `h` / `help` / `?` | show the help (incl. all the `read` target formats) |
| `r` / `read TARGET` | read a memory-word / flipjump-variable (address, label, or a `:type:` variable - see the help) |
| `s` / `step` | execute one op |
| `s` / `skip N` | execute N more ops, then stop (N decimal or `0x`-hex) |
| `c` / `cont` / `continue` | run to the next breakpoint |
| `c*` / `ca` / `continue all` | run to the end, ignoring all breakpoints |
| `exit` (or Ctrl+C / EOF) | stop the run (a keyboard-interrupt) |

The debugger can read memory and flipjump variables (bit/hex/byte, and their vectors), single-step,
skip a fixed number of opcodes, or continue. A session looks like this:

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
(debug, "h" for help) > read 0x80

==== Read Memory ====
Reading 0x80:
memory[0x80] = 0  (or 0x0).

This address also goes by this label name:
0x80:
    stl.IO
(debug, "h" for help) > continue all
```

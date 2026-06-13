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
| `q` / `quit` / `exit` (or Ctrl+C / EOF) | stop the run (a keyboard-interrupt) |

The commands are case-insensitive.

The debugger can read memory and flipjump variables (bit/hex/byte, and their vectors), single-step,
skip a fixed number of opcodes, or continue. Take this program, which increments a counter 5 times:

```fj
// my_program.fj - increment a counter 5 times, then print it.

stl.startup_and_init_all

my_loop:
    hex.inc 2, counter
    hex.dec 2, remaining
    hex.if 2, remaining, done, my_loop
done:
    hex.print_as_digit 2, counter, 0
    stl.output '\n'
    stl.loop

counter:   hex.vec 2, 0x41
remaining: hex.vec 2, 5
```

A session on it - read the counter variable at two breakpoint hits (it increments in between),
single-step, skip 10 ops, then run to the end:

```
$ fj my_program.fj -s -d -B my_loop
  program break
==== Breakpoint ====
Address 0x10f700:
    my_loop.

1 ops executed.

flip 0x11894b (0x4b bits after:)
    counter.

jump 0x101f80:
    :wflips:1252.
(debug, "h" for help) > read :h2:counter

==== Reading FlipJump Variable ====
Reading the variable :h2:counter:
memory[0x118900, 0x118a00) = 65  (or 0x41).
(debug, "h" for help) > c
: continue
  program break
==== Breakpoint ====
Address 0x10f700:
    my_loop.

40 ops executed.

flip 0x11894b (0x4b bits after:)
    counter.

jump 0x101f80:
    :wflips:1252.
(debug, "h" for help) > read :h2:counter

==== Reading FlipJump Variable ====
Reading the variable :h2:counter:
memory[0x118900, 0x118a00) = 66  (or 0x42).
(debug, "h" for help) > s
: step
  program break
==== Debug Step ====
Address 0x101f80:
    :wflips:1252.

41 ops executed.

flip 0x11894c (0x4c bits after:)
    counter.

jump 0x101f00:
    :wflips:1253.
(debug, "h" for help) > skip 10
: skip
  program break
==== Debug Step ====
Address 0x101a00:
    :wflips:1264.

51 ops executed.

flip 0x11894e (0x4e bits after:)
    counter.

jump 0x101980:
    :wflips:1265.
(debug, "h" for help) > continue all
: continue_all
46
```

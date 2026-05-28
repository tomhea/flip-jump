# FlipJump Demonstration Catalog

A catalog of small, working FlipJump programs that collectively demonstrate
the language can express anything: arithmetic, strings, bits, state machines,
puzzles, simulations, and more. Each program is self-contained, simple, and
fully tested.

## How to use this catalog

Each program lives at `programs/catalog/<category>/<slug>.fj`. Its input and
expected output live at `tests/inout/catalog/<category>/<slug>.in|.out`. Run
the whole catalog with:

```
pytest --catalog
```

Or run a single program directly:

```
fj programs/catalog/<category>/<slug>.fj
```

See [CONVENTIONS.md](CONVENTIONS.md) for the file format, naming rules, and
testing protocol.

## Categories

1. [hello](#hello) — Hello / greeting variants
2. [io](#io) — cat, echo, head, transformations
3. [arithmetic](#arithmetic) — basic math
4. [number_theory](#number_theory) — primes, factorization, sequences
5. [strings](#strings) — text manipulation
6. [bits](#bits) — bit-level operations
7. [logic](#logic) — boolean / gate demos
8. [loops](#loops) — iteration patterns
9. [branching](#branching) — conditional / classification
10. [data_structures](#data_structures) — stacks, queues, arrays, sorts
11. [recursion](#recursion) — recursive algorithms
12. [interactive](#interactive) — input-driven programs
13. [conversion](#conversion) — unit / format conversion
14. [encoding](#encoding) — encoding / decoding
15. [algorithms](#algorithms) — classic algorithms
16. [geometry](#geometry) — 2D math
17. [simulation](#simulation) — cellular automata, etc.
18. [puzzles](#puzzles) — small combinatorial puzzles
19. [sequences](#sequences) — OEIS-style sequences
20. [text_processing](#text_processing) — tokenize, word count
21. [state_machines](#state_machines) — FSM demos
22. [parsing](#parsing) — expression parsing
23. [graphics_ascii](#graphics_ascii) — ASCII art / fractals
24. [language_demos](#language_demos) — one program per STL macro family
25. [cryptography](#cryptography) — toy ciphers
26. [memory_layout](#memory_layout) — pointer / stack demos
27. [language_meta](#language_meta) — quine variants, self-reference
28. [games](#games) — minigames
29. [calendar_time](#calendar_time) — date / time
30. [misc](#misc) — fizzbuzz, 99 bottles, etc.

---

## hello

| # | name | description |
|---|---|---|
| 0001 | hello_world | Prints `Hello, World!\n` and exits. |
| 0002 | hello_user | Reads a single-line name from stdin (terminated by `\n`) and prints `Hello, <name>!\n`. |
| 0003 | hello_world_3x | Prints `Hello, World!\n` three times consecutively. |
| 0005 | hello_lowercase | Prints `hello, world!\n` (all-lowercase variant). |
| 0006 | hello_uppercase | Prints `HELLO, WORLD!\n` (all-uppercase variant). |
| 0007 | hello_reversed | Prints `!dlroW ,olleH\n` (reversed greeting). |
| 0008 | hello_one_char_per_line | Prints each character of `Hello, World!` on its own line (13 lines). |
| 0009 | hello_two_lines | Prints `Hello,\nWorld!\n` — the greeting split into two lines. |
| 0010 | hello_box | Three lines of 17 chars: 17 stars / `* Hello, World! *` / 17 stars. |
| 0011 | hello_no_newline | Prints `Hello, World!` with no trailing newline. |
| 0012 | hello_tab_sep | Prints `Hello,\tWorld!\n` with a literal tab between the two halves. |
| 0013 | hello_question | Prints `Hello, World?\n` (question-mark variant). |
| 0014 | hello_exclaim_3x | Prints `Hello, World!!!\n` (three trailing exclamation marks). |
| 0015 | hello_long_user | Reads a name and prints `Welcome to FlipJump, <name>! Have a great day!\n`. |
| 0016 | hello_hex_codes | Prints the hex code-points of `Hello, World!` separated by spaces. |
| 0017 | hello_ascii_first_five | Prints the ASCII decimal codes of the first five characters of `Hello`. |
| 0018 | hello_underline | Prints `Hello, World!\n` followed by 13 dashes + `\n`. |
| 0019 | hello_two_users | Reads two names and prints `Hello, <name1> and <name2>!\n`. |
| 0020 | hello_anonymous | Prints `Hello, anonymous user!\n` (no input). |
| 0021 | hello_alpha_world | Prints the lowercase alphabet followed by space + the greeting. |
| 0022 | hello_then_length | Prints `Hello, World!\nLength: 13\n`. |
| 0023 | hello_then_question | Prints the greeting followed by `What's your name?` on next line. |
| 0025 | hello_world_overunder | Prints the greeting sandwiched between two rows of 13 `=` signs. |

## io

| # | name | description |
|---|---|---|
| 0026 | cat | Reads stdin and echoes each byte to stdout, byte-for-byte, until EOF. |
| 0027 | uppercase_filter | Reads stdin and prints each byte uppercased (`a`-`z` → `A`-`Z`). |
| 0028 | lowercase_filter | Reads stdin and prints each byte lowercased (`A`-`Z` → `a`-`z`). |
| 0030 | count_bytes | Reads all of stdin and prints the byte count as decimal + `\n`. |
| 0031 | count_lines | Reads stdin and prints the number of newline bytes as decimal + `\n`. |
| 0033 | echo_twice | Reads each byte of stdin and outputs it twice. |
| 0034 | echo_thrice | Reads each byte of stdin and outputs it three times. |
| 0035 | skip_first_byte | Reads stdin and outputs every byte except the very first one. |

## arithmetic

| # | name | description |
|---|---|---|

## number_theory

| # | name | description |
|---|---|---|

## strings

| # | name | description |
|---|---|---|

## bits

| # | name | description |
|---|---|---|

## logic

| # | name | description |
|---|---|---|

## loops

| # | name | description |
|---|---|---|

## branching

| # | name | description |
|---|---|---|

## data_structures

| # | name | description |
|---|---|---|

## recursion

| # | name | description |
|---|---|---|

## interactive

| # | name | description |
|---|---|---|

## conversion

| # | name | description |
|---|---|---|

## encoding

| # | name | description |
|---|---|---|

## algorithms

| # | name | description |
|---|---|---|

## geometry

| # | name | description |
|---|---|---|

## simulation

| # | name | description |
|---|---|---|

## puzzles

| # | name | description |
|---|---|---|

## sequences

| # | name | description |
|---|---|---|

## text_processing

| # | name | description |
|---|---|---|

## state_machines

| # | name | description |
|---|---|---|

## parsing

| # | name | description |
|---|---|---|

## graphics_ascii

| # | name | description |
|---|---|---|

## language_demos

| # | name | description |
|---|---|---|

## cryptography

| # | name | description |
|---|---|---|

## memory_layout

| # | name | description |
|---|---|---|

## language_meta

| # | name | description |
|---|---|---|

## games

| # | name | description |
|---|---|---|

## calendar_time

| # | name | description |
|---|---|---|

## misc

| # | name | description |
|---|---|---|

---

## Exceptional / fj.tomhe.app Examples candidates

Programs in this section are picks that are especially instructive or
beautiful, worth highlighting on the fj.tomhe.app Examples page. Populated
incrementally during Phase 3 implementation.

| # | name | why it's worth showcasing |
|---|---|---|

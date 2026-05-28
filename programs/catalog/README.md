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
| 0004 | hello_n_times | Reads a single ASCII digit `0`-`9` from stdin and prints `Hello, World!\n` that many times. |
| 0005 | hello_lowercase | Prints `hello, world!\n` (all-lowercase variant). |
| 0006 | hello_uppercase | Prints `HELLO, WORLD!\n` (all-uppercase variant). |
| 0007 | hello_reversed | Prints `!dlroW ,olleH\n` (the bytes of `Hello, World!\n` minus the newline, reversed, followed by `\n`). |
| 0008 | hello_one_char_per_line | Prints each character of `Hello, World!` on its own line (13 lines, each one char + `\n`). |
| 0009 | hello_two_lines | Prints `Hello,\nWorld!\n` — the greeting split into two lines at the comma. |
| 0010 | hello_box | Prints exactly three lines of 17 chars each + `\n`: line 1 and 3 are 17 `*` characters; line 2 is `* Hello, World! *` (1 star, space, the 13-byte greeting, space, 1 star). |
| 0011 | hello_no_newline | Prints exactly `Hello, World!` with no trailing newline. |
| 0012 | hello_tab_sep | Prints `Hello,\tWorld!\n` with a literal tab between `Hello,` and `World!`. |
| 0013 | hello_question | Prints `Hello, World?\n` (question-mark variant). |
| 0014 | hello_exclaim_3x | Prints `Hello, World!!!\n` (three trailing exclamation marks). |
| 0015 | hello_long_user | Reads a single-line name and prints `Welcome to FlipJump, <name>! Have a great day!\n`. |
| 0016 | hello_hex_codes | Prints the hex code-points of `Hello, World!` separated by spaces: `48 65 6c 6c 6f 2c 20 57 6f 72 6c 64 21\n`. |
| 0017 | hello_ascii_first_five | Prints the ASCII decimal codes of the first five characters of `Hello` separated by spaces: `72 101 108 108 111\n`. |
| 0018 | hello_underline | Prints `Hello, World!\n-------------\n` (13 dashes underlining the greeting). |
| 0019 | hello_two_users | Reads two `\n`-terminated names as two consecutive lines on stdin (same convention as `hello_user`) and prints `Hello, <name1> and <name2>!\n`. |
| 0020 | hello_anonymous | Prints `Hello, anonymous user!\n` (no input). |
| 0021 | hello_alpha_world | Prints the lowercase English alphabet followed by space and the greeting: `abcdefghijklmnopqrstuvwxyz Hello, World!\n`. |
| 0022 | hello_then_length | Prints `Hello, World!\nLength: 13\n`. |
| 0023 | hello_then_question | Prints `Hello, World!\nWhat's your name?\n` (greeting followed by a question on the next line). |
| 0024 | hello_iterations | Reads a single ASCII digit `1`-`9` and prints lines `Iteration <i>: Hello, World!\n` for each `i` from 1 to N. |
| 0025 | hello_world_overunder | Prints `=============\nHello, World!\n=============\n` (greeting sandwiched between two rows of 13 `=`). |

## io

| # | name | description |
|---|---|---|
| 0026 | cat | Reads stdin and echoes each byte to stdout, byte-for-byte, until EOF. |
| 0027 | uppercase_filter | Reads stdin and prints each byte uppercased (`a`-`z` → `A`-`Z`; other bytes unchanged). |
| 0028 | lowercase_filter | Reads stdin and prints each byte lowercased (`A`-`Z` → `a`-`z`; other bytes unchanged). |
| 0030 | count_bytes | Reads all of stdin, prints the total byte count as a decimal integer followed by `\n`. |
| 0031 | count_lines | Reads all of stdin, prints the number of `\n` bytes seen as decimal + `\n`. |
| 0032 | count_words | Reads all of stdin and prints the number of whitespace-separated tokens as decimal + `\n`. Whitespace = any of `' '`, `'\t'`, `'\n'`; runs of consecutive whitespace count as one separator; leading and trailing whitespace introduce no empty tokens; empty input prints `0\n`. |
| 0033 | echo_twice | Reads each byte of stdin and outputs it twice. |
| 0034 | echo_thrice | Reads each byte of stdin and outputs it three times. |
| 0035 | skip_first_byte | Reads stdin and outputs every byte except the very first one. |
| 0036 | swap_case | Reads stdin and swaps upper/lower for letter bytes; other bytes unchanged. |
| 0037 | strip_newlines | Reads stdin and outputs all bytes except `\n`. |
| 0038 | only_digits | Reads stdin and outputs only `0`-`9` bytes, dropping all others. |
| 0039 | only_letters | Reads stdin and outputs only `A`-`Z` and `a`-`z` bytes. |
| 0040 | only_vowels | Reads stdin and outputs only `a/e/i/o/u/A/E/I/O/U` bytes. |
| 0041 | only_uppercase | Reads stdin and outputs only `A`-`Z` bytes. |
| 0042 | tab_to_space | Reads stdin and replaces each `\t` with a single space; other bytes unchanged. |
| 0043 | space_to_tab | Reads stdin and replaces each space (` `) with `\t`; other bytes unchanged. |
| 0044 | char_to_dec | Reads exactly one byte from stdin and prints its ASCII decimal value as decimal + `\n`. |
| 0048 | echo_with_prefix | Reads stdin and prints each input byte preceded by `>`. |
| 0049 | echo_with_suffix | Reads stdin and prints each input byte followed by `!`. |
| 0050 | print_first_line | Reads stdin up to the first `\n` and prints only that line (including the `\n`). |
| 0051 | double_newlines | Reads stdin and outputs each `\n` byte as two `\n`s; other bytes unchanged. |
| 0052 | strip_spaces | Reads stdin and outputs all bytes except space (` `). |
| 0053 | input_then_thanks | Reads a single-line input and prints `Got it: <line>\nThank you!\n`. |
| 0054 | read_one_print_three | Reads one byte from stdin and prints the literal sequence `<byte><byte><byte>\n`. |
| 0055 | rot_ascii_plus_one | Reads stdin and outputs each byte plus 1, modulo 256 (so `0xFF` wraps to `0x00`). All bytes are transformed uniformly; no special-casing of letters or non-letters. |

## arithmetic

| # | name | description |
|---|---|---|
| 0056 | add_two_decimals | Reads two decimal integers (each on its own line) and prints their sum as decimal + `
`. |
| 0057 | sub_two_decimals | Reads two decimal integers (each on its own line) and prints `a - b` as a signed decimal + `
`. |
| 0058 | mul_single_digits | Reads two single-digit decimals `0`-`9` (each followed by `
`) and prints `a * b` as decimal + `
`. |
| 0059 | div_two_decimals | Reads two decimal integers (each on its own line; second is non-zero) and prints `a / b` as integer-division decimal + `
`. |
| 0060 | mod_two_decimals | Reads two decimal integers and prints `a % b` as decimal + `
`. |
| 0061 | add_three_decimals | Reads three decimal integers (each own line) and prints their sum + `
`. |
| 0062 | abs_decimal | Reads one signed decimal integer and prints its absolute value as decimal + `
`. |
| 0063 | negate_decimal | Reads one signed decimal integer and prints its negation as decimal + `
`. |
| 0064 | inc_decimal | Reads one decimal integer and prints `a + 1` as decimal + `
`. |
| 0065 | dec_decimal | Reads one decimal integer and prints `a - 1` as decimal + `
`. |
| 0066 | double_decimal | Reads one decimal integer and prints `a * 2` as decimal + `
`. |
| 0067 | halve_decimal | Reads one decimal integer and prints `a / 2` (integer division) as decimal + `
`. |
| 0068 | square_small | Reads one decimal integer in `0`-`15` and prints `a * a` as decimal + `
`. |
| 0069 | cube_small | Reads one decimal integer in `0`-`5` and prints `a * a * a` as decimal + `
`. |
| 0070 | min_two | Reads two decimal integers and prints the smaller as decimal + `
`. |
| 0071 | max_two | Reads two decimal integers and prints the larger as decimal + `
`. |
| 0074 | mod_by_4 | Reads one decimal integer and prints `a % 4` as a single digit + `
`. |
| 0075 | mod_by_10 | Reads one decimal integer and prints `a % 10` as a single digit + `
`. |
| 0101 | avg_two | Reads two decimal integers and prints their integer average `(a + b) / 2` (floor division) as decimal + `
`. |
| 0102 | avg_three | Reads three decimal integers and prints their integer average `(a + b + c) / 3` (floor division) as decimal + `
`. |
| 0103 | compare_two | Reads two decimal integers and prints `<` if `a < b`, `=` if `a == b`, `>` if `a > b`, followed by `
`. |
| 0104 | sign_of | Reads one signed decimal integer and prints `-` if negative, `0` if zero, `+` if positive, followed by `
`. |
| 0105 | is_zero | Reads one decimal integer and prints `1
` if it equals zero, else `0
`. |
| 0106 | is_positive | Reads one signed decimal integer and prints `1
` if `> 0`, else `0
`. |
| 0107 | is_negative | Reads one signed decimal integer and prints `1
` if `< 0`, else `0
`. |
| 0108 | add_with_expression | Reads two decimal integers and prints the human-readable expression `<a> + <b> = <sum>
`. |
| 0109 | mul_by_3 | Reads one decimal in `0`-`30` and prints `a * 3` as decimal + `
`. |
| 0110 | mul_by_5 | Reads one decimal in `0`-`20` and prints `a * 5` as decimal + `
`. |
| 0111 | mul_by_7 | Reads one decimal in `0`-`14` and prints `a * 7` as decimal + `
`. |
| 0112 | mul_by_10 | Reads one decimal in `0`-`100` and prints `a * 10` as decimal + `
`. |
| 0113 | div_by_3_quot_rem | Reads one decimal and prints `<quotient> <remainder>
` for division by 3 (single line, space-separated). |
| 0114 | complement_to_100 | Reads one decimal in `0`-`100` and prints `100 - a` as decimal + `
`. |
| 0115 | is_even | Reads one decimal integer and prints `1
` if even, else `0
`. |
| 0116 | is_odd | Reads one decimal integer and prints `1
` if odd, else `0
`. |
| 0123 | swap_pair | Reads two decimals (each on own line) and prints them in reverse order: `<b>
<a>
`. |
| 0124 | median_of_three | Reads three decimal integers and prints the median (middle value when sorted) as decimal + `
`. |
| 0125 | max_three | Reads three decimals and prints the maximum + `
`. |
| 0126 | min_three | Reads three decimals and prints the minimum + `
`. |
| 0127 | range_of_three | Reads three decimals and prints `max - min` + `
`. |
| 0132 | is_in_range | Reads three decimals `a`, `lo`, `hi` (in that order, each own line) and prints `1
` if `lo <= a <= hi`, else `0
`. |
| 0135 | clamp_to_max_9 | Reads one decimal in `0`-`99` and prints `min(a, 9)` + `
` (caps the value at 9). |
| 0136 | add_then_mod_10 | Reads two decimals and prints `(a + b) % 10` as a single digit + `
`. |
| 0137 | abs_diff | Reads two decimals and prints `|a - b|` as decimal + `
`. |

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

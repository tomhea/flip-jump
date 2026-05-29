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
| 0030 | count_bytes | Reads all of stdin, prints the total byte count as a decimal integer followed by `
`. |
| 0031 | count_lines | Reads all of stdin, prints the number of `
` bytes seen as decimal + `
`. |
| 0032 | count_words | Reads all of stdin and prints the number of whitespace-separated tokens as decimal + `
`. Whitespace = any of `' '`, `'	'`, `'
'`; runs of consecutive whitespace count as one separator; leading and trailing whitespace introduce no empty tokens; empty input prints `0
`. |
| 0033 | echo_twice | Reads each byte of stdin and outputs it twice. |
| 0034 | echo_thrice | Reads each byte of stdin and outputs it three times. |
| 0035 | skip_first_byte | Reads stdin and outputs every byte except the very first one. |
| 0036 | swap_case | Reads stdin and swaps upper/lower for letter bytes; other bytes unchanged. |
| 0037 | strip_newlines | Reads stdin and outputs all bytes except `
`. |
| 0038 | only_digits | Reads stdin and outputs only `0`-`9` bytes, dropping all others. |
| 0039 | only_letters | Reads stdin and outputs only `A`-`Z` and `a`-`z` bytes. |
| 0040 | only_vowels | Reads stdin and outputs only `a/e/i/o/u/A/E/I/O/U` bytes. |
| 0041 | only_uppercase | Reads stdin and outputs only `A`-`Z` bytes. |
| 0042 | tab_to_space | Reads stdin and replaces each `	` with a single space; other bytes unchanged. |
| 0043 | space_to_tab | Reads stdin and replaces each space (` `) with `	`; other bytes unchanged. |
| 0044 | char_to_dec | Reads exactly one byte from stdin and prints its ASCII decimal value as decimal + `
`. |
| 0045 | dec_to_char | Reads a decimal number `0`-`127` from stdin terminated by `
` and prints the corresponding ASCII byte. |
| 0046 | char_to_hex | Reads exactly one byte from stdin and prints `0xNN
` where NN is its two-digit hex code (lowercase). |
| 0047 | hex_to_char | Reads `0xNN
` from stdin (two lowercase hex digits) and prints the corresponding ASCII byte. |
| 0048 | echo_with_prefix | Reads stdin and prints each input byte preceded by `>`. |
| 0049 | echo_with_suffix | Reads stdin and prints each input byte followed by `!`. |
| 0050 | print_first_line | Reads stdin up to the first `
` and prints only that line (including the `
`). |
| 0051 | double_newlines | Reads stdin and outputs each `
` byte as two `
`s; other bytes unchanged. |
| 0052 | strip_spaces | Reads stdin and outputs all bytes except space (` `). |
| 0053 | input_then_thanks | Reads a single-line input and prints `Got it: <line>
Thank you!
`. |
| 0054 | read_one_print_three | Reads one byte from stdin and prints the literal sequence `<byte><byte><byte>
`. |
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
| 0072 | sum_to_n | Reads one decimal integer N in `0`-`20` and prints `1+2+...+N` as decimal + `
`. |
| 0073 | factorial_small | Reads one decimal integer N in `0`-`6` and prints `N!` as decimal + `
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
| 0117 | count_up_to_n | Reads decimal N in `0`-`9` and prints `1
2
...
N
` (one per line). For N=0 prints nothing. |
| 0118 | count_down_from_n | Reads decimal N in `0`-`9` and prints `N
(N-1)
...
1
`. For N=0 prints nothing. |
| 0119 | evens_up_to_n | Reads decimal N in `0`-`20` and prints even positive integers `2,4,...` up to and including N (if even) or N-1 (if odd), one per line. |
| 0120 | odds_up_to_n | Reads decimal N in `0`-`19` and prints odd positive integers `1,3,...` up to and including N (if odd) or N-1 (if even), one per line. |
| 0121 | multiples_of_3_to_n | Reads decimal N in `0`-`30` and prints positive multiples of 3 `3,6,...` ≤ N, one per line. |
| 0122 | multiples_of_5_to_n | Reads decimal N in `0`-`50` and prints positive multiples of 5 `5,10,...` ≤ N, one per line. |
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
| 0128 | sum_of_n_inputs | Reads decimal N (`1`-`9`) on first line, then N decimal integers (each own line), prints their sum + `
`. |
| 0129 | max_of_n_inputs | Reads decimal N (`1`-`9`), then N decimal integers, prints the maximum + `
`. |
| 0130 | min_of_n_inputs | Reads decimal N (`1`-`9`), then N decimal integers, prints the minimum + `
`. |
| 0131 | avg_of_n_inputs | Reads decimal N (`1`-`9`), then N decimal integers, prints their integer average (floor of sum/N) + `
`. |
| 0132 | is_in_range | Reads three decimals `a`, `lo`, `hi` (in that order, each own line) and prints `1
` if `lo <= a <= hi`, else `0
`. |
| 0133 | pow_base2 | Reads decimal N in `0`-`7` and prints `2^N` as decimal + `
`. |
| 0134 | pow_base3 | Reads decimal N in `0`-`5` and prints `3^N` as decimal + `
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
| 0138 | is_prime_small | Reads decimal N in `0`-`50` and prints `1
` if N is prime, else `0
`. |
| 0139 | first_n_primes | Reads decimal N in `1`-`10` and prints the first N prime numbers in ascending order, one per line. |
| 0140 | prime_after | Reads decimal N in `0`-`50` and prints the smallest prime strictly greater than N (guaranteed ≤ 53) + `
`. |
| 0141 | count_primes_to_n | Reads decimal N in `0`-`50` and prints the count of prime numbers in `[2..N]` as decimal + `
`. |
| 0142 | gcd_two | Reads two decimals (each ≤ 100) and prints their GCD as decimal + `
`. |
| 0143 | lcm_two | Reads two decimals each in `1`-`20` and prints their LCM as decimal + `
`. |
| 0144 | coprime_check | Reads two decimals (each ≤ 100) and prints `1
` if their GCD is 1, else `0
`. |
| 0145 | factor_count_small | Reads decimal N in `1`-`50` and prints the number of positive divisors of N as decimal + `
`. |
| 0146 | divisors_of_n | Reads decimal N in `1`-`30` and prints all positive divisors of N in ascending order, one per line. |
| 0147 | is_perfect_small | Reads decimal N in `1`-`30` and prints `1
` if N equals the sum of its proper divisors (divisors excluding N), else `0
`. |
| 0148 | sum_of_divisors_small | Reads decimal N in `1`-`30` and prints the sum of all positive divisors of N (including N) as decimal + `
`. |
| 0149 | is_abundant_small | Reads decimal N in `1`-`30` and prints `1
` if N is abundant (sum of proper divisors > N), else `0
`. |
| 0150 | is_deficient_small | Reads decimal N in `1`-`30` and prints `1
` if N is deficient (sum of proper divisors < N), else `0
`. |
| 0151 | fib_n | Reads decimal N in `0`-`12` and prints the N-th Fibonacci number `F(N)` (with `F(0)=0`, `F(1)=1`) + `
`. |
| 0152 | fib_seq_n | Reads decimal N in `0`-`12` and prints `F(0), F(1), ..., F(N)` one per line. |
| 0153 | is_fib_small | Reads decimal N in `0`-`200` and prints `1
` if N is a Fibonacci number, else `0
`. |
| 0154 | lucas_n | Reads decimal N in `0`-`10` and prints the N-th Lucas number (with `L(0)=2`, `L(1)=1`) + `
`. |
| 0155 | collatz_steps | Reads decimal N in `1`-`50` and prints the number of Collatz steps (3n+1 / n/2) to reach 1 + `
`. |
| 0156 | collatz_sequence | Reads decimal N in `1`-`15` and prints the Collatz sequence starting at N, terminating with 1, one number per line. |
| 0157 | is_palindrome_num | Reads decimal N in `0`-`999` and prints `1
` if its base-10 representation is a palindrome, else `0
`. |
| 0158 | digit_sum | Reads decimal N in `0`-`999` and prints the sum of its base-10 digits as decimal + `
`. |
| 0159 | digit_product | Reads decimal N in `0`-`999` and prints the product of its base-10 digits as decimal + `
`. |
| 0160 | digit_count_small | Reads decimal N in `0`-`999` and prints the number of base-10 digits (`1`, `2`, or `3`; `0` itself counts as 1 digit) + `
`. |
| 0161 | reverse_digits | Reads decimal N in `0`-`999` and prints the decimal with its digits reversed (e.g. `123` → `321`, `100` → `001` becomes `1`). |
| 0162 | is_armstrong_3 | Reads decimal N in `100`-`999` and prints `1
` if N equals the sum of cubes of its three digits, else `0
`. |
| 0163 | happy_check_small | Reads decimal N in `1`-`30` and prints `1
` if N is a happy number (iterated sum of squared digits reaches 1), else `0
`. |
| 0164 | is_square_small | Reads decimal N in `0`-`100` and prints `1
` if N is a perfect square, else `0
`. |
| 0165 | is_cube_small | Reads decimal N in `0`-`64` and prints `1
` if N is a perfect cube, else `0
`. |

## strings

| # | name | description |
|---|---|---|
| 0166 | string_length | Reads a single `
`-terminated line of length ≤ 80 and prints the length of the line (excluding the `
`) as decimal + `
`. |
| 0168 | count_vowels | Reads a `
`-terminated line ≤ 80 chars and prints the count of vowel letters (`aeiouAEIOU`) as decimal + `
`. |
| 0169 | count_consonants | Reads a `
`-terminated line ≤ 80 chars and prints the count of letter bytes that are NOT vowels as decimal + `
`. |
| 0170 | count_letters | Reads a `
`-terminated line ≤ 80 chars and prints the count of letter bytes (`A`-`Z` or `a`-`z`) as decimal + `
`. |
| 0171 | count_uppercase_letters | Reads a `
`-terminated line ≤ 80 chars and prints the count of `A`-`Z` bytes as decimal + `
`. |
| 0172 | count_lowercase_letters | Reads a `
`-terminated line ≤ 80 chars and prints the count of `a`-`z` bytes as decimal + `
`. |
| 0173 | first_char_of_line | Reads a non-empty `
`-terminated line and prints just its first byte followed by `
`. |
| 0174 | last_char_of_line | Reads a non-empty `
`-terminated line and prints just its last byte (the one before `
`) followed by `
`. |
| 0177 | caesar_plus_1 | Reads a `
`-terminated line ≤ 80 chars and prints the same line with each letter shifted forward by 1 in the alphabet (wraps `z`→`a`, `Z`→`A`); non-letter bytes pass through unchanged; ends with `
`. |
| 0178 | caesar_plus_3 | Reads a `
`-terminated line ≤ 80 chars and prints it with each letter Caesar-shifted by 3 (wraps within case); non-letters unchanged; ends with `
`. |
| 0179 | caesar_plus_13 | Reads a `
`-terminated line ≤ 80 chars and prints the ROT13 transformation: letters shifted by 13 (wraps within case); non-letters unchanged; ends with `
`. |
| 0180 | uppercase_line | Reads a `
`-terminated line ≤ 80 chars, uppercases its `a`-`z` bytes (others unchanged), prints result + `
`. |
| 0181 | lowercase_line | Reads a `
`-terminated line ≤ 80 chars, lowercases its `A`-`Z` bytes (others unchanged), prints result + `
`. |
| 0182 | swap_case_line | Reads a `
`-terminated line ≤ 80 chars and prints it with each letter's case toggled (others unchanged), ending with `
`. |
| 0183 | has_char_in_line | Reads exactly one byte, then a `
`, then a `
`-terminated line ≤ 80 chars. Prints `1
` if the line contains the first byte, else `0
`. |
| 0184 | starts_with_uppercase | Reads a non-empty `
`-terminated line and prints `1
` if its first byte is `A`-`Z`, else `0
`. |
| 0185 | ends_with_period | Reads a non-empty `
`-terminated line and prints `1
` if the last byte before `
` is `.`, else `0
`. |
| 0186 | is_all_uppercase | Reads a non-empty `
`-terminated line ≤ 80 chars and prints `1
` if every byte (excluding the `
`) is `A`-`Z`, else `0
`. |
| 0187 | is_all_lowercase | Reads a non-empty `
`-terminated line ≤ 80 chars and prints `1
` if every byte is `a`-`z`, else `0
`. |
| 0188 | is_all_digits | Reads a non-empty `
`-terminated line ≤ 80 chars and prints `1
` if every byte is `0`-`9`, else `0
`. |
| 0189 | is_all_letters | Reads a non-empty `
`-terminated line ≤ 80 chars and prints `1
` if every byte is `A`-`Z` or `a`-`z`, else `0
`. |
| 0190 | char_at_index | Reads a single ASCII digit `0`-`9`, then `
`, then a `
`-terminated line of at least N+1 chars. Prints the byte at 0-based index N + `
`. |
| 0191 | substring_first_3 | Reads a `
`-terminated line of at least 3 chars and prints just its first 3 bytes + `
`. |
| 0192 | substring_last_3 | Reads a `
`-terminated line of at least 3 chars and prints just its last 3 bytes (the 3 chars immediately before the `
`) + `
`. |
| 0193 | count_letter_e | Reads a `
`-terminated line ≤ 80 chars and prints the count of `e` or `E` bytes as decimal + `
`. |

## bits

| # | name | description |
|---|---|---|
| 0076 | popcount_byte | Reads one byte from stdin and prints its 1-bit count as a single decimal digit `0`-`8` + `
`. |
| 0077 | parity_byte | Reads one byte and prints `0` if it has an even number of 1-bits, `1` if odd, then `
`. |
| 0078 | high_nibble | Reads one byte and prints its high 4 bits as one lowercase hex char + `
`. |
| 0079 | low_nibble | Reads one byte and prints its low 4 bits as one lowercase hex char + `
`. |
| 0080 | swap_nibbles | Reads one byte and outputs the byte with low and high nibbles swapped. |
| 0081 | reverse_bits_byte | Reads one byte and outputs the byte with its 8 bits reversed (bit 0 ↔ bit 7, etc.). |
| 0085 | xor_two_bytes | Reads exactly two bytes and outputs their bitwise XOR as one byte. |
| 0086 | and_two_bytes | Reads exactly two bytes and outputs their bitwise AND as one byte. |
| 0087 | or_two_bytes | Reads exactly two bytes and outputs their bitwise OR as one byte. |
| 0088 | shift_left_one | Reads one byte and outputs `byte << 1` (low bit becomes 0; high bit is lost). |
| 0089 | shift_right_one | Reads one byte and outputs `byte >> 1` (high bit becomes 0; low bit is lost). |
| 0090 | is_power_of_two | Reads one byte and prints `1
` if it has exactly one 1-bit (and is nonzero), else `0
`. |
| 0370 | count_leading_zeros | Reads one byte and prints the count of zero bits before the first `1` (counting from the MSB downward), `0`-`8`, + `
`. The zero byte yields `8`. |
| 0371 | count_trailing_zeros | Reads one byte and prints the count of zero bits before the first `1` (counting from the LSB upward), `0`-`8`, + `
`. The zero byte yields `8`. |
| 0372 | byte_to_binary_string | Reads one byte (raw) and prints an 8-char binary string of `0`/`1` (MSB first), followed by `
`. Differs from `conversion/dec_to_binary` (which reads a decimal text representation). |
| 0374 | is_byte_zero | Reads one byte and prints `1
` if it equals `0x00`, else `0
`. |
| 0375 | is_byte_full | Reads one byte and prints `1
` if it equals `0xFF`, else `0
`. |
| 0376 | xor_with_constant_55 | Reads one byte and outputs `byte XOR 0x55`, as one raw byte. |
| 0377 | and_with_constant_0f | Reads one byte and outputs `byte AND 0x0F` (low nibble preserved, high nibble zeroed), as one raw byte. |
| 0378 | or_with_constant_80 | Reads one byte and outputs `byte OR 0x80` (MSB set, other bits preserved), as one raw byte. |
| 0379 | byte_decrement_wrap | Reads one byte and outputs `(byte - 1) mod 256` as one raw byte (e.g. `0x00` → `0xFF`). |
| 0380 | rotate_left_byte | Reads one byte and outputs the byte rotated left by 1 bit (MSB wraps around to LSB), as one raw byte. |
| 0381 | rotate_right_byte | Reads one byte and outputs the byte rotated right by 1 bit (LSB wraps around to MSB), as one raw byte. |
| 0384 | count_bits_in_three_bytes | Reads exactly 3 bytes and prints the total 1-bit count across all 24 bits as decimal `0`-`24` + `
`. |
| 0385 | dominant_bit | Reads one byte. Prints `1
` if it has more 1-bits than 0-bits (popcount > 4), `0
` if more 0-bits than 1-bits (popcount < 4), or `tie
` if popcount equals 4. |
| 0896 | swap_two_bytes | Reads exactly 2 bytes. Outputs them in reverse order (byte2 first, then byte1) as raw bytes. |
| 0897 | min_two_bytes | Reads exactly 2 bytes. Outputs the byte with smaller numeric value (treating as unsigned 0-255) as a raw byte. |
| 0898 | max_two_bytes | Reads exactly 2 bytes. Outputs the byte with larger numeric value as a raw byte. |
| 0899 | xor_three_bytes | Reads exactly 3 bytes. Outputs `b1 XOR b2 XOR b3` as one raw byte. |
| 0900 | and_three_bytes | Reads exactly 3 bytes. Outputs `b1 AND b2 AND b3` as one raw byte. |
| 0901 | or_three_bytes | Reads exactly 3 bytes. Outputs `b1 OR b2 OR b3` as one raw byte. |
| 0902 | byte_high_eq_low_nibble | Reads exactly 1 byte. Prints `1
` if the high nibble equals the low nibble (e.g. `0xAA`, `0x33`), else `0
`. |
| 0903 | byte_is_bit_palindrome | Reads exactly 1 byte. Prints `1
` if the byte's 8-bit binary representation reads the same forward and backward (e.g. `0x99` = `10011001`), else `0
`. |
| 0904 | byte_reverse_each_nibble | Reads exactly 1 byte. Reverses the bits within each nibble independently (high nibble reversed in place, low nibble reversed in place). Outputs the resulting byte as raw. |
| 0924 | gray_code_from_binary | Reads one byte and outputs the corresponding Gray code byte (`byte XOR (byte >> 1)`) as one raw byte. |
| 0925 | binary_from_gray_code | Reads one byte interpreted as a Gray code value and outputs the corresponding standard-binary byte (running XOR of all higher bits). |
| 0926 | next_power_of_2_byte | Reads one byte `0`-`128` and outputs the smallest power of 2 that is `>=` the input (`0` → `1`, `5` → `8`, `8` → `8`) as one raw byte. |
| 0927 | prev_power_of_2_byte | Reads one byte `1`-`255` and outputs the largest power of 2 that is `<=` the input (`5` → `4`, `8` → `8`) as one raw byte. |
| 0928 | log2_ceil_byte | Reads one byte `1`-`128` and prints `ceil(log2(byte))` as a single decimal digit `0`-`7` + `
` (e.g. `5` → `3`, `8` → `3`). |
| 0929 | count_leading_ones | Reads one byte and prints the count of consecutive `1` bits starting from the MSB (`0xE0` → `3`, `0xFF` → `8`) as decimal `0`-`8` + `
`. |
| 0930 | count_trailing_ones | Reads one byte and prints the count of consecutive `1` bits starting from the LSB (`0x07` → `3`, `0xFF` → `8`) as decimal `0`-`8` + `
`. |
| 0931 | round_up_to_multiple_of_8 | Reads one byte `0`-`247` and outputs the smallest multiple of 8 that is `>=` the input (`0` → `0`, `1` → `8`, `9` → `16`) as one raw byte. |
| 0932 | round_down_to_multiple_of_8 | Reads one byte `0`-`255` and outputs the largest multiple of 8 that is `<=` the input (`0` → `0`, `9` → `8`, `15` → `8`) as one raw byte. |
| 0933 | unset_lowest_set_bit | Reads one byte and outputs `byte AND (byte - 1)` (clears the lowest set bit) as one raw byte. For `byte = 0` outputs `0`. |
| 0934 | isolate_lowest_set_bit | Reads one byte and outputs `byte AND (-byte mod 256)` (keeps only the lowest set bit) as one raw byte. For `byte = 0` outputs `0`. |
| 0935 | broadcast_lsb_to_byte | Reads one byte. If its LSB is `0` outputs `0x00`; if `1` outputs `0xFF`. (Demonstrates sign-extension-from-1-bit pattern.) |

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
| 0869 | bottles_of_beer_5 | No input. Prints 5 verses of the "X bottles of beer on the wall" song counting down from 5 to 1. Each verse follows the canonical 2-line refrain. |
| 0870 | bottles_of_beer_n | Reads digit N `1`-`9` + `\n`. Prints N verses counting down from N to 1 (same per-verse format as `bottles_of_beer_5`). |
| 0871 | zodiac_western | Reads month `1`-`12` then day `1`-`31` (each own line). Prints the corresponding western zodiac sign (`Aries`, `Taurus`, ..., `Pisces`) + `\n`. |
| 0872 | zodiac_chinese | Reads year `1900`-`2099` + `\n`. Prints the corresponding Chinese zodiac animal (`Rat`, `Ox`, ..., `Pig`) + `\n`. |
| 0873 | roman_to_arabic_30 | Reads Roman numeral string (one of `I`-`XXX`, valid up to 30) + `\n`. Prints decimal `1`-`30` + `\n`. |
| 0874 | arabic_to_roman_30 | Reads decimal `1`-`30` + `\n`. Prints corresponding Roman numeral + `\n`. |
| 0875 | country_flag_short | Reads a 3-letter country code `USA`/`FRA`/`JPN` + `\n`. Prints a 2-line ASCII flag for that country (each row a string of pattern blocks). Hardcoded for 3 countries. |
| 0876 | join_words_with_space | Reads digit N `1`-`9` + `\n`, then N `\n`-terminated words. Prints them joined by single space + `\n`. |
| 0878 | lucky_sum_check | Reads 3 decimals `1`-`9` (each own line). Prints `1\n` if their sum is divisible by 7, else `0\n`. |
| 0879 | lucky_year_has_7 | Reads year `1900`-`2099` + `\n`. Prints `1\n` if its decimal representation contains the digit `7` anywhere, else `0\n`. |
| 0880 | magic_number_8 | Reads decimal N `0`-`999` + `\n`. Prints `magic!\n` if N mod 8 == 0, else `not magic\n`. |
| 0885 | count_paragraphs | Reads multi-line input terminated by EOF (or two consecutive `\n` characters as the final paragraph terminator). A paragraph is a maximal run of non-empty lines separated from other paragraphs by one or more empty lines. Prints the count of paragraphs as decimal + `\n`. |
| 0889 | print_zigzag_3_lines | No input. Prints a fixed 3-line zigzag of `*` characters: `*       *\n  *   *  \n    *    \n`. |
| 0892 | day_progress_percent | Reads decimal hour `0`-`23` + `\n`, minute `0`-`59` + `\n`. Prints `(hour * 60 + minute) * 100 / 1440` (floor) as decimal + `\n` (= percent of day elapsed). |
| 0894 | is_prime_or_one | Reads decimal `1`-`50` + `\n`. Prints `prime\n` if N is prime OR equals 1, else `composite\n`. (Variant: treats 1 as "kind of prime" for fun.) |
| 1023 | note_name_to_pitch_class | Reads a `\n`-terminated note name (one of `C`, `C#`, `D`, `D#`, `E`, `F`, `F#`, `G`, `G#`, `A`, `A#`, `B`). Prints the pitch class `0`-`11` as decimal + `\n` (`C` = 0). |
| 1025 | midi_to_pitch_class | Reads decimal MIDI `0`-`127` + `\n`. Prints `midi mod 12` as decimal `0`-`11` + `\n`. |
| 1026 | transpose_by_semitones | Reads decimal MIDI `0`-`127` + `\n`, then signed decimal shift `-24` to `24` + `\n`. Prints the new MIDI value `(input + shift)`, clamped to `[0, 127]`, as decimal + `\n`. |
| 1027 | major_scale_from_root_pcs | Reads decimal root pitch class `0`-`11` + `\n`. Prints the 7 pitch classes of the major scale starting at root (intervals 0, 2, 4, 5, 7, 9, 11), all mod 12, space-separated + `\n`. |
| 1028 | minor_scale_from_root_pcs | Reads decimal root pitch class `0`-`11` + `\n`. Prints the 7 pitch classes of the natural minor scale (intervals 0, 2, 3, 5, 7, 8, 10), all mod 12, space-separated + `\n`. |
| 1029 | is_major_triad | Reads 3 decimal MIDI numbers `m1 m2 m3` (each `0`-`127`, on own lines). Sorts them. Prints `1\n` if the intervals between consecutive sorted notes are `4, 3` semitones (i.e. major triad in root position), else `0\n`. |

---

## Exceptional / fj.tomhe.app Examples candidates

Programs in this section are picks that are especially instructive or
beautiful, worth highlighting on the fj.tomhe.app Examples page. Populated
incrementally during Phase 3 implementation.

| # | name | why it's worth showcasing |
|---|---|---|

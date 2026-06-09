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
| 1090 | reverse_line | Reads a single line from stdin (up to `
`) and prints it reversed followed by `
`. |

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
| 1030 | modular_inverse_brute | Reads decimals `a` `m` (each `1`-`30`, own line, with `gcd(a, m) = 1` guaranteed). Brute-forces `x` in `1..m-1` such that `(a * x) mod m == 1`. Prints `x` as decimal + `
`. |
| 1031 | crt_two_pairs | Reads 4 decimals `r1 m1 r2 m2` (each on own line, `m1`,`m2` coprime, each ≤ `10`). Finds `r` such that `r ≡ r1 mod m1` and `r ≡ r2 mod m2`, with `0 <= r < m1*m2`. Prints `r` as decimal + `
`. |
| 1032 | mod_factorial | Reads decimals `N` `m` (each `1`-`9` for N, `1`-`30` for m, on own lines). Prints `(N! mod m)` as decimal + `
`. |
| 1033 | mod_binomial_small | Reads decimals `N` `K` `m` (`N` `1`-`9`, `K` `0..N`, `m` `1`-`30`, on own lines). Prints `(C(N, K) mod m)` as decimal + `
`. |
| 1034 | mod_power_table | Reads decimals `base` `mod` (`base` `1`-`9`, `mod` `2`-`9`, on own lines). Prints `base^0 mod mod`, `base^1 mod mod`, ..., `base^(mod-1) mod mod` space-separated on one line + `
`. |
| 1035 | multiplicative_order_small | Reads decimals `a` `m` (each `2`-`20`, `gcd(a,m)=1`). Finds the smallest `k >= 1` such that `(a^k) mod m == 1`. Prints `k` as decimal + `
`. |
| 1036 | legendre_symbol_small | Reads decimals `a` `p` (`p` is an odd prime `3`-`19`, `a` `0`-`p-1`). Prints the Legendre symbol `(a/p)`: `1
` if `a` is a non-zero quadratic residue mod p, `-1
` if non-residue, `0
` if `a == 0`. |
| 1037 | jacobi_symbol_small | Reads decimals `a` `n` (`n` odd `1`-`19`, `a` `0`-`n-1`). Prints the Jacobi symbol as `1
`, `-1
`, or `0
`. |
| 1038 | mod_double_factorial | Reads decimals `N` `m` (`N` `0`-`9`, `m` `1`-`30`). Prints `(N!! mod m)` as decimal + `
` (where `N!! = N*(N-2)*(N-4)*...` down to 1 or 2). |
| 1039 | wilson_prime_check | Reads decimal `p` `2`-`30` + `
`. Computes `((p-1)! + 1) mod p`. Prints `1
` if this is `0` (i.e. `p` is prime by Wilson's theorem), else `0
`. |
| 1040 | inv_mod_via_fermat | Reads decimals `a` `p` (`p` prime `2`-`19`, `a` `1`-`p-1`). Computes `a^(p-2) mod p` (modular inverse via Fermat's little theorem). Prints inverse as decimal + `
`. |
| 1041 | primitive_root_check | Reads decimals `g` `p` (`p` prime `3`-`19`, `g` `1`-`p-1`). Prints `1
` if `g` is a primitive root mod p (i.e. its multiplicative order is `p-1`), else `0
`. |
| 1042 | discrete_log_brute_small | Reads decimals `g` `h` `p` (`p` prime `3`-`19`, `g` `1`-`p-1` primitive root, `h` `1`-`p-1`). Brute-forces `x` in `0..p-2` such that `g^x mod p == h`. Prints `x` as decimal + `
`. |
| 1043 | mod_sum_arithmetic | Reads decimals `N` `m` (`N` `1`-`30`, `m` `1`-`30`). Prints `((1 + 2 + ... + N) mod m)` as decimal + `
`. |
| 1044 | binomial_coefficient_small | Reads decimals `N` `K` (`N` `0`-`10`, `K` `0`-`N`, on own lines). Prints `C(N, K)` as decimal + `
`. |
| 1045 | multinomial_3_small | Reads 3 decimals `a` `b` `c` (each `0`-`5`, on own lines). Prints `(a + b + c)! / (a! * b! * c!)` as decimal + `
`. |
| 1046 | permutation_count_pn_k | Reads decimals `N` `K` (`N` `1`-`10`, `K` `0`-`N`). Prints `P(N, K) = N! / (N-K)!` as decimal + `
`. |
| 1047 | catalan_n_param | Reads decimal `N` `0`-`7` + `
`. Prints the `N`-th Catalan number `C(2N, N) / (N + 1)` as decimal + `
`. |
| 1048 | bell_n_param | Reads decimal `N` `0`-`6` + `
`. Prints the `N`-th Bell number `B(N)` as decimal + `
`. |
| 1049 | stirling_2nd_small | Reads decimals `N` `K` (`N` `0`-`6`, `K` `0`-`N`). Prints the Stirling number of the second kind `S(N, K)` as decimal + `
`. |
| 1050 | derangement_n_param | Reads decimal `N` `0`-`8` + `
`. Prints the `N`-th derangement number `D(N)` as decimal + `
`. |
| 1051 | eulerian_n_k_small | Reads decimals `N` `K` (`N` `1`-`6`, `K` `0`-`N-1`). Prints the Eulerian number `<N, K>` as decimal + `
`. |
| 1052 | lah_n_k_small | Reads decimals `N` `K` (`N` `1`-`6`, `K` `1`-`N`). Prints the (signed) Lah number `L(N, K)` as decimal + `
`. |
| 1053 | pascal_row_n | Reads decimal `N` `0`-`8` + `
`. Prints the `N`-th row of Pascal's triangle as `N+1` decimals space-separated + `
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
| 1091 | is_palindrome_string | Reads a `
`-terminated line ≤ 30 chars and prints `1
` if the line (excluding `
`) is a palindrome, else `0
`. |
| 1092 | repeat_line_2x | Reads a `
`-terminated line ≤ 40 chars and prints its content twice (concatenated, no internal separator), followed by `
`. |
| 1093 | repeat_line_3x | Reads a `
`-terminated line ≤ 30 chars and prints its content three times concatenated, followed by `
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
| 1061 | bit_at_position | Reads one byte, then one ASCII digit `0`-`7` (terminated by `
`), and prints the bit at that position as `0` or `1` + `
`. Convention: position `0` is the least-significant bit (LSB); position `7` is the most-significant bit (MSB). |
| 1062 | set_bit_at_position | Reads one byte then one digit `0`-`7` + `
` and outputs the byte with that bit set to 1. Convention: position `0` is the LSB; matches `bit_at_position`. |
| 1063 | clear_bit_at_position | Reads one byte then one digit `0`-`7` + `
` and outputs the byte with that bit cleared to 0. Convention: position `0` is the LSB; matches `bit_at_position`. |
| 1064 | toggle_bit_at_position | Reads one byte, then one ASCII digit `0`-`7` + `
`. Outputs the byte with the bit at that position XOR'd (toggled). Convention: position `0` is the LSB (matches `bit_at_position`). |
| 1065 | binary_string_to_byte | Reads an 8-char binary string of `0`/`1` + `
` and outputs the corresponding raw byte (no trailing `
`). Inverse of `byte_to_binary_string`. |
| 1066 | byte_concat_to_hex_word | Reads exactly two bytes (high then low) and prints 4 lowercase hex chars (no `0x` prefix) + `
`. The first byte's hex appears first. |
| 1067 | byte_split_from_hex_word | Reads exactly 4 lowercase hex chars + `
` and outputs two raw bytes: the high byte first, then the low byte. |
| 1068 | clear_low_k_bits | Reads one byte then one decimal digit `0`-`7` + `
`. Outputs the byte with the lowest `k` bits cleared (`byte AND (~((1<<k)-1))`) as one raw byte. |
| 1069 | set_low_k_bits | Reads one byte then one decimal digit `0`-`7` + `
`. Outputs the byte with the lowest `k` bits set to `1` (`byte OR ((1<<k)-1)`) as one raw byte. |

## logic

| # | name | description |
|---|---|---|
| 0091 | and_gate | Reads two ASCII bits (each is `0` or `1`, separated by `
`) and prints their AND as `0` or `1` + `
`. |
| 0092 | or_gate | Reads two ASCII bits and prints their OR + `
`. |
| 0093 | xor_gate | Reads two ASCII bits and prints their XOR + `
`. |
| 0094 | nand_gate | Reads two ASCII bits and prints their NAND + `
`. |
| 0095 | nor_gate | Reads two ASCII bits and prints their NOR + `
`. |
| 0096 | xnor_gate | Reads two ASCII bits and prints their XNOR + `
`. |
| 0097 | not_gate | Reads one ASCII bit and prints its negation + `
`. |
| 0098 | and_3 | Reads three ASCII bits (each followed by `
`) and prints their three-way AND + `
`. |
| 0099 | or_3 | Reads three ASCII bits and prints their three-way OR + `
`. |
| 0100 | half_adder | Reads two ASCII bits and prints the sum bit then the carry bit, both separated by `
` (two lines). |
| 0905 | logic_implies | Reads two `0`/`1` ASCII bits (each on own line). Prints `(NOT A) OR B` as `0` or `1` + `
` (A → B). |
| 0906 | boolean_xor_three | Reads three ASCII bits. Prints their XOR (= 1 iff odd number of 1s) + `
`. |
| 0907 | boolean_majority_three | Reads three ASCII bits. Prints `1
` if at least 2 of them are `1`, else `0
`. |
| 0908 | boolean_exactly_one | Reads three ASCII bits. Prints `1
` if exactly one of them is `1`, else `0
`. |
| 0909 | boolean_exactly_two | Reads three ASCII bits. Prints `1
` if exactly two are `1`, else `0
`. |
| 0910 | multiplexer_2to1 | Reads a selector bit + 2 data bits (each on own line). Outputs `data0` if selector is `0`, else `data1`, as one ASCII bit + `
`. |
| 0911 | demultiplexer_1to2 | Reads a data bit + selector bit. Outputs two bits separated by space + `
`: if selector is `0`, prints `<data> 0
`; if `1`, prints `0 <data>
`. |
| 0912 | mux_4to1 | Reads two selector bits + 4 data bits (each on own line). Outputs the selected data bit (selector encodes 0-3 as `s1*2+s0`) + `
`. |
| 0913 | encoder_4to2 | Reads 4 bits (assumed one-hot input, exactly one is `1`). Prints 2 bits as `<s1><s0>
` (e.g. position 0 → `00`, position 3 → `11`). |
| 0914 | decoder_2to4 | Reads 2 bits `s1 s0`. Prints 4 bits: position `s1*2+s0` is `1`, others are `0`. Output is 4 chars + `
`. |
| 0915 | full_adder | Reads three ASCII bits `a b c_in` (each own line). Prints `<sum> <c_out>
` where `sum = a XOR b XOR c_in` and `c_out = (a AND b) OR (c_in AND (a XOR b))`. |
| 0916 | nand_universality_or | Reads two ASCII bits `a b` (each own line). Computes `OR(a, b)` using ONLY `NAND` gates (no native AND/OR/NOT). Prints result + `
`. |

## loops

| # | name | description |
|---|---|---|
| 0230 | print_byte_n_times | Reads one byte then `
` then a digit `0`-`9` + `
`. Outputs the byte N times in a row. |
| 0231 | print_n_byte_lines | Reads one byte then `
` then a digit `0`-`9` + `
`. Prints N lines, each containing just that byte then `
`. |
| 0232 | print_byte_grid | Reads one byte then `
` then a digit `1`-`9` + `
`. Prints an N-by-N grid filled with that byte (N lines, each N bytes then `
`). |
| 0233 | right_triangle_stars | Reads digit N `1`-`9` + `
`. Prints a right triangle of `*`: row i (1..N) has i stars followed by `
`. |
| 0234 | inverted_right_triangle | Reads digit N `1`-`9` + `
`. Prints rows of `*`: row i has (N+1-i) stars + `
`. |
| 0235 | centered_pyramid | Reads digit N `1`-`9` + `
`. Prints N rows of width `2N-1`: row i has `N-i` leading spaces, then `2i-1` `*`, then `
`. |
| 0236 | hollow_box | Reads digit N `2`-`9` + `
`. Prints an N-by-N hollow box: top and bottom rows are N `*`; middle rows are `*` + (N-2) spaces + `*`, each + `
`. |
| 0237 | solid_square | Reads digit N `1`-`9` + `
`. Prints an N-by-N solid square of `*`. |
| 0238 | checkerboard | Reads digit N `1`-`8` + `
`. Prints an N-by-N checkerboard: top-left cell `*`, alternating `*` and `.` along each row and column. |
| 0239 | diagonal_stars | Reads digit N `1`-`9` + `
`. Prints an N-by-N grid where cell (i,j) is `*` if `i == j` else `.`, rows separated by `
`. |
| 0240 | x_pattern | Reads digit N `1`-`9` + `
` (N odd preferred). Prints an N-by-N grid where cell (i,j) is `*` if `i == j` or `i + j == N - 1` else `.`. |
| 0241 | plus_pattern | Reads odd digit N `1`/`3`/`5`/`7`/`9` + `
`. Prints an N-by-N grid with `*` along the middle row and the middle column, `.` elsewhere. |
| 0242 | v_pattern | Reads digit N `1`-`9` + `
`. Prints N rows on a `(2N-1)`-wide grid. For row `i` (1-indexed, 1..N), the cell at column `j` (1-indexed) is `*` if `j == i` or `j == 2N - i`, else `.`. Each row ends with `
`. Example for N=3: row 1 = `*...*
`, row 2 = `.*.*.
`, row 3 = `..*..
`. |
| 0243 | print_alphabet_lower | No input. Prints `abcdefghijklmnopqrstuvwxyz
`. |
| 0244 | print_alphabet_upper | No input. Prints `ABCDEFGHIJKLMNOPQRSTUVWXYZ
`. |
| 0245 | print_alphabet_reversed | No input. Prints `zyxwvutsrqponmlkjihgfedcba
`. |
| 0246 | print_digits_0_9 | No input. Prints `0123456789
`. |
| 0247 | print_evens_2_to_20 | No input. Prints `2 4 6 8 10 12 14 16 18 20
` (space-separated). |
| 0248 | print_odds_1_to_19 | No input. Prints `1 3 5 7 9 11 13 15 17 19
` (space-separated). |
| 0249 | print_multiples_5_to_50 | No input. Prints `5 10 15 20 25 30 35 40 45 50
`. |
| 0250 | print_fibs_first_10 | No input. Prints `0 1 1 2 3 5 8 13 21 34
` (the first 10 Fibonacci numbers, space-separated). |
| 0251 | print_first_10_primes | No input. Prints `2 3 5 7 11 13 17 19 23 29
`. |
| 0252 | print_first_10_squares | No input. Prints `1 4 9 16 25 36 49 64 81 100
`. |
| 0253 | count_to_10 | No input. Prints `1
2
...
10
` (one per line, ten lines total). |
| 0254 | count_down_from_10 | No input. Prints `10
9
...
1
`. |
| 0255 | print_ascii_a_to_k | No input. Prints `65 66 67 68 69 70 71 72 73 74 75
` (the ASCII codes of `A`-`K`, space-separated). |
| 0256 | print_powers_of_2_first_8 | No input. Prints `1 2 4 8 16 32 64 128
`. |
| 0257 | print_powers_of_3_first_5 | No input. Prints `1 3 9 27 81
`. |
| 0258 | print_factorial_first_6 | No input. Prints `1 2 6 24 120 720
` (factorials 1..6). |
| 0260 | line_then_n_blanks | Reads a digit N `0`-`9` + `
` then a `
`-terminated line ≤ 60 chars. Prints the line, then N additional `
` characters. |
| 0261 | accumulate_sum | Reads up to 9 decimal integers, each followed by `
`, terminated by an empty line (just `
`). After each input, prints the running sum on its own line. |
| 0262 | print_pair_grid | No input. Prints all pairs `(i, j)` for `i, j` in `0`-`2` in row-major order, each formatted as `i j
`. Output is 9 lines total. |
| 0263 | fizzbuzz_to_15 | No input. Prints lines 1 through 15 as standard FizzBuzz: multiples of 15 → `FizzBuzz`, of 3 → `Fizz`, of 5 → `Buzz`, else the number. One per line. |
| 0264 | fizzbuzz_to_20 | No input. Same rules as `fizzbuzz_to_15` but lines 1 through 20. |
| 0265 | count_input_bytes_running | Reads bytes until `
`. After each byte, prints the byte's 1-based position as decimal + `
`. Stops at `
` (does not print the position of the `
`). |
| 0266 | countdown_blastoff | No input. Prints `5
4
3
2
1
Blastoff!
`. |
| 0268 | print_l_shape | Reads digit N `2`-`9` + `
`. Prints an L-shape: N-1 rows of `*
` (left bar), then one row of N `*`s + `
` (bottom bar). |
| 0269 | print_t_shape | Reads digit N `3`/`5`/`7`/`9` + `
`. Prints a T-shape: row 0 is N `*`s; rows 1..N-1 each have (N-1)/2 leading spaces then `*` then `
`. |
| 0270 | print_vertical_bar | Reads digit N `1`-`9` + `
`. Prints N lines, each just `*
`. |
| 0271 | print_horizontal_bar | Reads digit N `1`-`9` + `
`. Prints a single line of N `*`s followed by `
`. |
| 0272 | sum_running_first_n | Reads digit N `1`-`9` + `
`. Prints running sums on separate lines: `1
3
6
10
...
` for the first N partial sums of `1+2+3+...`. |
| 0273 | range_step_two | Reads two decimals `lo` and `hi` (each own line, both 0-50, lo<=hi). Prints `lo, lo+2, lo+4, ...` up to ≤hi, one per line. |
| 0274 | range_step_three | Same as `range_step_two` but step 3. |
| 0275 | print_pair_diff_grid | No input. For all `i` in `0`-`3` and `j` in `0`-`3`, prints `i-j
` (signed) on its own line, in row-major (i,j) order. 16 lines total. |
| 0276 | spaces_then_stars | Reads digit N `1`-`9` + `
`. Prints N lines: row i has (N-i) spaces, then i `*`, then `
` (right-aligned triangle). |
| 0277 | echo_first_n_bytes | Reads digit N `0`-`9` + `
`, then reads N more bytes from stdin and outputs them verbatim. |
| 0278 | print_first_then_repeat | Reads one byte, then a digit N `1`-`9` + `
`. Outputs the byte once, then repeats it N times on a new line. |
| 1094 | repeat_line_n | Reads a digit N `1`-`9` + `
` then a `
`-terminated line ≤ 30 chars. Prints the line N times (each ending with the same `
`). |
| 1095 | hollow_diamond | Reads odd digit N `1`/`3`/`5`/`7`/`9` + `
`. Prints an N-by-N hollow diamond. Let `k = (N+1)/2` (the middle row index, 1-indexed). For row `i` (1..N), let `d = abs(i - k)` (distance from middle row). The row has 1-indexed columns 1..N: column `j` is `*` if `j == k - d` or `j == k + d`, else ` ` (space). Each row ends with `
`. Example for N=5: `  *  
 * * 
*   *
 * * 
  *  
`. |
| 1096 | print_box_with_label | Reads digit N `3`-`9` + `
` then a `
`-terminated line of exactly N-2 chars. Prints an N-wide hollow box of `*` with the input line centered as the middle row (`* <line> *`). |
| 1097 | numbered_lines | Reads digit N `1`-`9` + `
` then a `
`-terminated line ≤ 20 chars. Prints N lines, each prefixed with `<i>: ` (1-based) and then the line. |

## branching

| # | name | description |
|---|---|---|
| 0194 | sort_two_asc | Reads two decimal integers and prints them sorted ascending: `<smaller>
<larger>
`. |
| 0195 | sort_two_desc | Reads two decimal integers and prints them sorted descending: `<larger>
<smaller>
`. |
| 0196 | sort_three_asc | Reads three decimal integers and prints them sorted ascending, one per line. |
| 0197 | sort_three_desc | Reads three decimal integers and prints them sorted descending, one per line. |
| 0198 | classify_age | Reads decimal age `0`-`120` and prints `infant
` if `<2`, `child
` if `2-12`, `teen
` if `13-19`, `adult
` if `20-64`, `senior
` if `>=65`. |
| 0199 | classify_grade | Reads decimal score `0`-`100` and prints `A
` if `>=90`, `B
` if `80-89`, `C
` if `70-79`, `D
` if `60-69`, else `F
`. |
| 0200 | classify_temp_c | Reads signed decimal Celsius temperature and prints one of `freezing
` (≤0), `cold
` (1-10), `mild
` (11-20), `warm
` (21-30), `hot
` (≥31). |
| 0201 | day_of_week_name | Reads decimal `0`-`6` and prints `Sunday`/`Monday`/`Tuesday`/`Wednesday`/`Thursday`/`Friday`/`Saturday` followed by `
` (Sunday=0). |
| 0202 | month_name | Reads decimal `1`-`12` and prints the English month name (`January`...`December`) + `
`. |
| 0203 | season_from_month | Reads decimal month `1`-`12` and prints `winter
` (12,1,2), `spring
` (3,4,5), `summer
` (6,7,8), `fall
` (9,10,11). |
| 0204 | even_or_odd_word | Reads one decimal integer and prints `even
` or `odd
` (not `0`/`1`). |
| 0205 | compare_to_10 | Reads one decimal and prints `less
` if `<10`, `equal
` if `=10`, `more
` if `>10`. |
| 0206 | compare_to_100 | Reads one decimal and prints `less
` if `<100`, `equal
` if `=100`, `more
` if `>100`. |
| 0207 | is_alphanumeric_byte | Reads exactly one byte and prints `1
` if it's `0`-`9`/`A`-`Z`/`a`-`z`, else `0
`. |
| 0208 | is_punctuation_byte | Reads exactly one byte and prints `1
` if it's one of `,.?!;:'-` (the eight common punctuation marks), else `0
`. |
| 0209 | is_whitespace_byte | Reads exactly one byte and prints `1
` if it's space/tab/newline (`0x20`, `0x09`, `0x0A`), else `0
`. |
| 0210 | char_class | Reads exactly one byte and prints one of `digit
`, `upper
`, `lower
`, `other
` based on the byte's ASCII range. |
| 0211 | weekday_or_weekend | Reads decimal day-of-week `0`-`6` (Sunday=0) and prints `weekend
` (Sat/Sun) or `weekday
` (Mon-Fri). |
| 0212 | is_business_hour | Reads decimal hour `0`-`23` (24-hour clock) and prints `1
` if `9 <= h <= 17`, else `0
`. |
| 0213 | fizzbuzz_classify_one | Reads decimal N in `1`-`100` and prints just one of: `fizz
` if `N % 3 == 0` and not `% 5`; `buzz
` if `N % 5 == 0` and not `% 3`; `fizzbuzz
` if both; else `<N>
`. |
| 0214 | min_or_max_select | Reads one ASCII bit (`0` or `1`) followed by `
`, then two decimals each followed by `
`. If bit is `0` prints the min, if `1` prints the max + `
`. |
| 0215 | abs_or_negate_select | Reads one ASCII bit, then a signed decimal. If bit is `0` prints `abs(a)`, if `1` prints `-a`, each + `
`. |
| 0216 | upper_or_lower_select | Reads one ASCII bit, then exactly one byte. If bit is `0` outputs the byte uppercased, if `1` outputs it lowercased. |
| 0217 | switch_on_digit | Reads one ASCII digit `0`-`9` and prints `a
` for 0, `b
` for 1, …, `j
` for 9. |
| 0218 | triangle_classify | Reads three positive decimals `a`,`b`,`c` (each ≤ 99, on own line) as triangle side lengths. Prints `equilateral
`, `isosceles
`, `scalene
`, or `not
` (if no valid triangle). |
| 0219 | quadrant_2d | Reads two signed decimals `x` then `y` and prints `1
`/`2
`/`3
`/`4
` based on Cartesian quadrant; prints `axis
` if either coordinate is 0. |
| 0220 | compare_three_order | Reads three decimals `a`,`b`,`c` (each own line) and prints one of `abc`/`acb`/`bac`/`bca`/`cab`/`cba` + `
` indicating their ascending sorted order by original label. (Ties broken alphabetically by label.) |
| 0221 | parity_three | Reads three decimals and prints `all even
` if all are even, `all odd
` if all odd, else `mixed
`. |
| 0222 | all_positive_three | Reads three signed decimals and prints `1
` if all are `> 0`, else `0
`. |
| 0223 | any_zero_three | Reads three decimals and prints `1
` if at least one equals 0, else `0
`. |
| 0224 | compare_with_window | Reads three decimals `a`, `lo`, `hi` (each own line) and prints `below
` if `a < lo`, `in
` if `lo <= a <= hi`, `above
` if `a > hi`. |
| 0225 | sorted_check_three | Reads three decimals and prints `1
` if they are in non-decreasing order, else `0
`. |
| 0226 | sorted_check_four | Reads four decimals and prints `1
` if they are in non-decreasing order, else `0
`. |
| 0227 | rps_winner | Reads two bytes (each on own line, terminated by `
`): `r`/`p`/`s` (rock/paper/scissors) for player 1 and player 2. Prints `1
` if P1 wins, `2
` if P2 wins, `tie
` if tie. |
| 0228 | leap_year_check | Reads decimal year `1`-`9999` and prints `1
` if it's a leap year (Gregorian rule: `(y%4==0 && y%100!=0) || y%400==0`), else `0
`. |
| 0229 | bmi_category | Reads two decimals: weight-kg `1`-`200` then height-cm `100`-`250` (each own line). Computes BMI = weight*10000/(height*height) and prints `under
` (BMI<18), `normal
` (18-24), `over
` (25-29), `obese
` (≥30). |

## data_structures

| # | name | description |
|---|---|---|
| 1110 | array_sum_5 | Reads exactly 5 decimal integers, each on its own line, and prints their sum + `
`. |
| 1111 | array_sum_10 | Reads exactly 10 decimal integers, each on its own line, and prints their sum + `
`. |
| 1112 | array_max_5 | Reads exactly 5 decimals (each own line) and prints the maximum + `
`. |
| 1113 | array_max_10 | Reads exactly 10 decimals (each own line) and prints the maximum + `
`. |
| 1114 | array_min_5 | Reads exactly 5 decimals and prints the minimum + `
`. |
| 1115 | array_min_10 | Reads exactly 10 decimals and prints the minimum + `
`. |
| 1116 | array_avg_5 | Reads exactly 5 decimals and prints `floor(sum / 5)` + `
`. |
| 1117 | array_avg_10 | Reads exactly 10 decimals and prints `floor(sum / 10)` + `
`. |
| 1118 | array_count_zeros | Reads digit N `1`-`9` + `
`, then N decimal integers each own line. Prints the count of zeros as decimal + `
`. |
| 1119 | array_double_each | Reads digit N `1`-`9` + `
`, then N decimals. Prints `2*a_i` for each input on its own line, in the same order. |
| 1120 | array_increment_each | Reads digit N `1`-`9` + `
`, then N decimals. Prints `a_i + 1` for each input on its own line, in the same order. |
| 1121 | array_sum_evens | Reads digit N `1`-`9` + `
`, then N decimals. Prints the sum of even-valued elements + `
`. |
| 1122 | array_sum_odds | Reads digit N `1`-`9` + `
`, then N decimals. Prints the sum of odd-valued elements + `
`. |
| 1123 | array_range | Reads digit N `1`-`9` + `
`, then N decimals. Prints `max - min` + `
`. |
| 1124 | partial_sums | Reads digit N `1`-`9` + `
`, then N decimals. Prints the running cumulative sum after each input, one per line (N lines). |
| 1125 | histogram_5 | Reads exactly 5 ASCII digits `0`-`5` (each followed by `
`). For each input value `v`, prints `v` `*` characters then `
` (5 lines of output total). |
| 1126 | array_count_negatives | Reads digit N `1`-`9` + `
`, then N signed decimal integers. Prints the count of values `< 0` + `
`. |
| 1127 | array_count_positives | Reads digit N `1`-`9` + `
`, then N signed decimal integers. Prints the count of values `> 0` + `
`. |
| 1128 | array_count_above_threshold | Reads digit N `1`-`9` + `
`, then `threshold` (signed decimal) + `
`, then N signed decimals. Prints the count of values strictly greater than threshold + `
`. |
| 1129 | running_max | Reads digit N `1`-`9` + `
`, then N signed decimals (each own line). After each input, prints the running maximum so far on its own line (N lines of output). |
| 1130 | running_min | Reads digit N `1`-`9` + `
`, then N signed decimals. After each input, prints the running minimum so far on its own line. |
| 1131 | is_sorted_ascending | Reads digit N `1`-`9` + `
`, then N decimals. Prints `1
` if the sequence is non-decreasing, else `0
`. |
| 1132 | is_sorted_descending | Reads digit N `1`-`9` + `
`, then N decimals. Prints `1
` if the sequence is non-increasing, else `0
`. |
| 1133 | group_by_parity | Reads `N` `1`-`9` + `
`, then N decimals on own lines. Prints `even: <e>
odd: <o>
` with the counts. |
| 1134 | array_reverse_5 | Reads 5 decimals (each own line) and prints them in reverse order, one per line. |
| 1135 | swap_first_last_5 | Reads exactly 5 decimals and prints them with positions 0 and 4 swapped, one per line. |
| 1136 | swap_adjacent_pairs_6 | Reads exactly 6 decimals and prints them with each adjacent pair swapped (positions 0↔1, 2↔3, 4↔5), one per line in the new order. |
| 1137 | rotate_left_5 | Reads exactly 5 decimals and prints them rotated left by 1 (input `a b c d e` → output `b
c
d
e
a
`). |
| 1138 | rotate_right_5 | Reads exactly 5 decimals and prints them rotated right by 1 (input `a b c d e` → output `e
a
b
c
d
`). |
| 1139 | shift_right_zero_fill_5 | Reads exactly 5 decimals and prints them shifted right by 1 with 0-fill on the left (input `a b c d e` → output `0
a
b
c
d
`). |
| 1140 | min_index_5 | Reads exactly 5 decimals and prints the 0-based index of the minimum value + `
`. Ties: prints the smallest index among tied positions. |
| 1141 | max_index_5 | Reads exactly 5 decimals and prints the 0-based index of the maximum value + `
`. Ties: smallest index among tied positions. |
| 1142 | bubble_sort_5 | Reads exactly 5 decimals and prints them sorted ascending (one per line), implemented as bubble sort (adjacent-swap passes). The algorithm choice is the point. |
| 1143 | insertion_sort_5 | Reads exactly 5 decimals and prints them sorted ascending (one per line), implemented as insertion sort (extend prefix one element at a time). |
| 1144 | selection_sort_5 | Reads exactly 5 decimals and prints them sorted ascending (one per line), implemented as selection sort (find-min-and-swap each pass). |
| 1145 | array_median_5 | Reads exactly 5 decimals (any order) and prints the median (middle value when sorted) as decimal + `
`. |
| 1146 | count_inversions_5 | Reads exactly 5 decimals and prints the count of inversions (pairs `(i, j)` with `i < j` and `a_i > a_j`) as decimal + `
`. |
| 1147 | stack_push_pop_demo | Reads digit N `1`-`9` + `
`. Pushes integers `1..N` onto a stack, then pops all and prints each on its own line. Output is `N
(N-1)
...
1
` (reverse order). |
| 1148 | queue_enqueue_dequeue | Reads digit N `1`-`9` + `
`. Enqueues integers `1..N` then dequeues all, printing each on its own line. Output is `1
2
...
N
` (FIFO order). |
| 1149 | array_first_3 | Reads digit N `3`-`9` + `
`, then N decimals. Prints just the first 3 values, one per line. |
| 1150 | array_dedupe_sorted | Reads digit N `1`-`9` + `
`, then N decimals already sorted ascending. Prints the unique values in order, one per line. |
| 1151 | array_last_3 | Reads digit N `3`-`9` + `
`, then N decimals. Prints just the last 3 values, one per line. |
| 1152 | array_contains | Reads digit N `1`-`9` + `
`, then N decimals, then one more decimal `target`. Prints `1
` if target appears in the N-element array, else `0
`. |
| 1153 | linear_search | Reads digit N `1`-`9` + `
`, then N decimals, then `target`. Prints the 0-based index of the first match + `
`, or `not found
` if absent. |
| 1154 | binary_search_sorted | Reads digit N `1`-`9` + `
`, then N decimals already sorted ascending, then `target`. Prints the 0-based index of the match + `
` (any if duplicates), or `not found
`. Uses binary search. |
| 1155 | stack_reverse_line | Reads a `
`-terminated line ≤ 40 chars. Uses an explicit push-all-then-pop-all stack pattern (LIFO) to reverse the line; prints the reversed bytes followed by `
`. The stack demonstration is the point. |
| 1156 | queue_print_order | Reads digit N `1`-`9` + `
`, then exactly N bytes (no separator). Enqueues each byte then dequeues all, outputting them in original input order (FIFO demo). |
| 1157 | parens_matched | Reads a `
`-terminated string ≤ 40 chars containing only `(` and `)`. Prints `1
` if the parentheses are balanced (every `(` has a matching `)` in order), else `0
`. |
| 1158 | mixed_brackets_matched | Reads a `
`-terminated string ≤ 40 chars containing only `()[]{}`. Prints `1
` if all three bracket types are balanced AND properly nested (e.g. `([])` valid, `([)]` invalid), else `0
`. Use an explicit stack. |
| 1159 | count_distinct_bytes | Reads a `
`-terminated line ≤ 80 chars and prints the count of distinct byte values in the line (excluding the terminating `
`) as decimal + `
`. |
| 1160 | range_query_count_5 | Reads 5 decimals `0`-`99` (each on own line), then `lo` `hi` (`0`-`99`, on own lines). Prints the count of those values that satisfy `lo <= x <= hi` as decimal `0`-`5` + `
`. |
| 1161 | range_query_print_5 | Reads 5 decimals `0`-`99` (each on own line), then `lo` `hi`. Prints each value with `lo <= x <= hi` in input order, one per line. |
| 1162 | kv_lookup_5 | Reads 5 key-value pairs: each as decimal `key` `0`-`9` + `
`, then decimal `value` `0`-`99` + `
` (total 10 lines). Then reads a query key + `
`. Prints the value for that key as decimal + `
`, or `not found
` if the key wasn't among the 5. (Latest write wins on duplicates.) |
| 1163 | kv_lookup_n | Reads decimal `N` `1`-`9` + `
`, then N key-value pairs (same format as `kv_lookup_5`). Then reads a query key. Prints the value, or `not found
`. |
| 1164 | kv_update_then_lookup | Reads 5 key-value pairs (same format), then reads one update pair (new key + new value), then a query key. Applies the update (overwrites if key exists, else adds — but if adding would exceed capacity 6, drops the oldest entry). Prints lookup result or `not found
`. |
| 1165 | group_by_first_letter | Reads `N` `1`-`9` + `
`, then N `
`-terminated lowercase words. Groups by first letter and prints each `<letter> <count>
` line, sorted by letter ascending. |
| 1166 | select_max_per_group_2 | Reads 5 `(group, value)` pairs (each on 2 own lines, group `0` or `1`, value `0`-`99`). Prints `group 0 max: <v>
group 1 max: <v>
` (or `none
` for either group if no pairs). |
| 1167 | sort_by_key_5 | Reads 5 `(key, value)` pairs (each on 2 own lines, key `0`-`9` integer, value `0`-`99`). Sorts ascending by key (stable). Prints each pair as `<key> <value>
` (5 lines). |

## recursion

| # | name | description |
|---|---|---|

## interactive

| # | name | description |
|---|---|---|
| 1309 | echo_bot | Reads each `
`-terminated input line until an empty line (just `
`). For each non-empty line, prints `> <line>
`. |
| 1310 | greeting_bot | Reads a name (`
`-terminated, ≤ 20 chars) and prints `Hello, <name>!
Goodbye, <name>!
`. |
| 1311 | magic_eight_ball | Reads any `
`-terminated question (≤ 60 chars). Prints exactly one of 5 fixed answers selected by `(input_length_excluding_newline) mod 5`: `0→Yes
`, `1→No
`, `2→Maybe
`, `3→Ask again later
`, `4→Definitely
`. |
| 1312 | yes_no_validator | Reads `y` or `n` + `
` (any case is treated as exact byte). Prints `Affirmative
` for `y`, `Negative
` for `n`, otherwise `Please answer y or n
`. |
| 1313 | guess_one_round | Reads a single decimal digit `1`-`9` + `
`. Secret value is `7`. Prints `correct!
` if `7`, `too low
` if `<7`, `too high
` if `>7`. |
| 1314 | menu_selection | Reads a single digit `1`-`4` + `
`. Prints `Pizza
`, `Burger
`, `Salad
`, or `Soup
` for `1`/`2`/`3`/`4` respectively. |
| 1315 | password_check | Reads a `
`-terminated string ≤ 20 chars. Prints `Access granted
` if the line content (excluding `
`) equals the literal `flipjump`, else `Access denied
`. |
| 1316 | addition_quiz | Reads two single-digit decimals (each `
`-terminated), then a decimal answer (`
`-terminated, may be 1-2 digits). Prints `correct
` if the answer equals the sum of the two digits, else `wrong (expected <S>)
` with `S` the actual sum. |
| 1317 | multiplication_quiz | Same I/O shape as `addition_quiz` but for multiplication. Prints `correct
` if the answer equals the product, else `wrong (expected <P>)
`. |
| 1318 | interactive_calc | Reads one operator byte `+`, `-`, or `*` + `
`, then two decimal integers (each `
`-terminated). Prints the integer result + `
`. (For `-`, prints signed result.) |
| 1319 | user_input_loop_3 | Reads exactly 3 `
`-terminated lines (each ≤ 30 chars). Prints `1: <line1>
2: <line2>
3: <line3>
`. |
| 1320 | coin_flip_pseudo | Reads exactly one byte. Prints `Heads
` if its value is even, `Tails
` if odd. (Pseudo-random via input parity.) |
| 1321 | dice_roll_pseudo | Reads exactly one byte. Prints decimal `(byte mod 6) + 1` + `
` (range `1`-`6`). |
| 1322 | lucky_seven | Reads exactly one byte. Prints `Lucky!
` if `byte mod 7 == 0`, else `Try again
`. |
| 1323 | trivia_capital_france | First prints `What's the capital of France?
` on stdout. Then reads a `
`-terminated answer (≤ 20 chars). Prints `correct!
` if the answer is exactly `Paris`, else `wrong
`. |
| 1324 | trivia_largest_planet | First prints `What's the largest planet?
`. Then reads a `
`-terminated answer. Prints `correct!
` if exactly `Jupiter`, else `wrong
`. |
| 1325 | trivia_math | First prints `What's 2+2?
`. Then reads a decimal `
`-terminated answer. Prints `correct!
` if exactly `4`, else `wrong
`. |
| 1326 | balance_check | Reads decimal `0`-`9999` + `
`. Prints `low
` if `<100`, `ok
` if `100`-`999`, `high
` if `>=1000`. |
| 1327 | tip_calculator | Reads decimal bill `0`-`99` + `
`. Prints `(bill * 120) / 100` (20% tip, integer division) + `
`. |
| 1328 | tax_calculator | Reads decimal amount `0`-`999` + `
`. Prints `(amount * 110) / 100` (10% tax, integer division) + `
`. |
| 1329 | simple_login | Reads a `
`-terminated username, then a `
`-terminated password (each ≤ 20 chars). Prints `Welcome!
` if username is exactly `admin` and password is exactly `root`, else `Denied
`. |
| 1330 | survey_two_q | Reads two `
`-terminated `y`/`n` answers. Prints `Definitely
` for `y/y`, `Maybe
` for `y/n`, `Probably not
` for `n/y`, `Definitely not
` for `n/n`. |
| 1331 | cheer_team | Reads digit `1`-`3` + `
`. Prints `Go team <N>!
` exactly three times. |
| 1332 | quiz_show_score | Reads three single-digit decimals `0` or `1` (each `
`-terminated; `1` = correct, `0` = wrong for 3 rounds). Prints `Total: <S>
Grade: <G>
`, where `S` is the sum (0-3) and `G` is `A`/`B`/`C`/`F` for `3`/`2`/`1`/`0`. |
| 1333 | customer_rating | Reads digit `1`-`5` + `
`. Prints `Thank you for your <N>-star review!
`. |
| 1334 | clock_set | Reads two decimals on separate lines: hour `0`-`23` then minute `0`-`59`. Prints `Time set to <HH>:<MM>
` (each zero-padded to 2 digits). |
| 1335 | greeting_user_age | Reads a `
`-terminated name (≤ 20 chars) then a decimal age `0`-`120` + `
`. Prints `Hello, <name>! You are <age> years old.
`. |
| 1336 | todo_add | Reads a `
`-terminated task description (≤ 40 chars). Prints `Added: <task>
`. |
| 1337 | shopping_cart_check | Reads decimal price `0`-`999` + `
` then decimal budget `0`-`999` + `
`. If `price <= budget` prints `affordable
`, else prints `over budget by <X>
` where `X = price - budget`. |
| 1338 | number_guess_three_tries | Secret value is `5`. Reads up to 3 decimal guesses `1`-`10` (each `
`-terminated). After each guess prints `too low
`, `too high
`, or `correct!
` then exits on correct. If 3 wrong guesses, prints `Out of tries. Secret was 5.
` and exits. |
| 1339 | odd_one_out | Reads three decimals (each `
`-terminated). If exactly two are equal, prints the third (unique) value + `
`. Otherwise prints `none
` (covers both all-equal and all-different cases). |
| 1340 | chatbot_simple_reply | Reads a `
`-terminated line ≤ 40 chars. If equals `hi`, prints `Hello!
`. If equals `bye`, prints `Goodbye!
`. Otherwise prints `I don't understand.
`. |
| 1341 | interactive_addition_three | Reads three decimals (each `
`-terminated). Prints the human-readable expression `<a> + <b> + <c> = <sum>
`. |

## conversion

| # | name | description |
|---|---|---|
| 0339 | dec_to_hex | Reads decimal `0`-`255` + `
` and prints exactly two lowercase hex digits (no `0x` prefix), followed by `
`. |
| 0340 | hex_to_dec | Reads exactly two lowercase hex digits + `
` and prints the decimal `0`-`255` + `
`. |
| 0341 | dec_to_binary | Reads decimal `0`-`255` + `
` and prints an 8-char binary string of `0` and `1` (MSB first), followed by `
`. |
| 0342 | binary_to_dec | Reads an 8-char binary string of `0`/`1` + `
` and prints the decimal `0`-`255` + `
`. |
| 0343 | dec_to_octal | Reads decimal `0`-`63` + `
` and prints exactly two octal digits + `
`. |
| 0344 | octal_to_dec | Reads exactly two octal digits + `
` and prints the decimal `0`-`63` + `
`. |
| 0345 | binary_to_hex | Reads an 8-char binary string + `
` and prints exactly two lowercase hex digits + `
`. |
| 0346 | hex_to_binary | Reads exactly two lowercase hex digits + `
` and prints an 8-char binary string + `
`. |
| 0347 | celsius_to_fahrenheit | Reads a signed decimal Celsius temperature (range `-100`..`100`) + `
` and prints `floor(C * 9 / 5 + 32)` as a signed decimal + `
`. |
| 0348 | fahrenheit_to_celsius | Reads a signed decimal Fahrenheit temperature (range `-148`..`212`) + `
` and prints `floor((F - 32) * 5 / 9)` as a signed decimal + `
`. |
| 0349 | km_to_miles | Reads decimal kilometers `0`-`100` + `
` and prints `floor(km * 5 / 8)` as decimal miles + `
`. |
| 0350 | miles_to_km | Reads decimal miles `0`-`60` + `
` and prints `floor(miles * 8 / 5)` as decimal km + `
`. |
| 0351 | minutes_to_hours_minutes | Reads decimal total minutes `0`-`999` + `
` and prints `<H>:<MM>
`, where `H` is `total / 60` (no leading zero) and `MM` is `total % 60` zero-padded to 2 digits. |
| 0352 | seconds_to_minutes_seconds | Reads decimal total seconds `0`-`3599` + `
` and prints `<M>:<SS>
`, with `MM` zero-padded to 2 digits. |
| 0353 | hours_to_minutes | Reads decimal hours `0`-`24` + `
` and prints `hours * 60` as decimal + `
`. |
| 0354 | days_to_hours | Reads decimal days `0`-`30` + `
` and prints `days * 24` as decimal + `
`. |
| 0355 | dec_to_thousands_grouped | Reads decimal `0`-`999999` + `
` and prints the value with thousands separators (commas), then `
`. Examples: `7` → `7
`, `1000` → `1,000
`, `12345` → `12,345
`, `999999` → `999,999
`. |
| 0356 | word_zero_to_nine | Reads a single ASCII digit `0`-`9` + `
` and prints its English word (`zero`, `one`, `two`, ..., `nine`) + `
`. |
| 0358 | zero_pad_to_4 | Reads decimal `0`-`9999` + `
` and prints a 4-character zero-padded representation + `
`. Examples: `7` → `0007
`, `1234` → `1234
`. |
| 0359 | roman_numeral_1_to_10 | Reads decimal `1`-`10` + `
` and prints the corresponding Roman numeral (`I`, `II`, ..., `X`) + `
`. |
| 0361 | lowercase_letter_to_index | Reads exactly one byte `a`-`z` and prints its 0-based alphabet index (`a`→`0`, ..., `z`→`25`) as decimal + `
`. |
| 0362 | index_to_lowercase_letter | Reads decimal `0`-`25` + `
` and outputs exactly one byte: the corresponding lowercase letter (`0`→`a`, `25`→`z`). No trailing `
` after the byte. |
| 0363 | uppercase_letter_to_index | Reads exactly one byte `A`-`Z` and prints its 0-based alphabet index (`A`→`0`, ..., `Z`→`25`) as decimal + `
`. |
| 0364 | dollars_to_cents | Reads decimal dollars `0`-`99` + `
` and prints `dollars * 100` as decimal + `
`. |
| 0365 | cents_to_dollars_cents | Reads decimal cents `0`-`9999` + `
` and prints `<dollars>.<cc>
`, where `cc` is `cents % 100` zero-padded to 2 digits. |
| 0366 | nibble_to_hex_char | Reads decimal `0`-`15` + `
` and outputs exactly one byte: the corresponding lowercase hex char (`0`-`9` or `a`-`f`), followed by `
`. |
| 0367 | hex_char_to_nibble | Reads exactly one byte that's a lowercase hex char (`0`-`9` or `a`-`f`) + `
` and prints the decimal `0`-`15` + `
`. |
| 0368 | dec_with_explicit_sign | Reads a signed decimal `-9999`..`9999` + `
` and prints it with an always-explicit sign byte (`+` or `-`) prefix, followed by `
`. Examples: `5` → `+5
`, `0` → `+0
`, `-3` → `-3
`. |
| 1073 | word_to_digit | Reads one of the English number words `zero`, `one`, `two`, ..., `nine` (terminated by `
`) and prints the corresponding ASCII digit `0`-`9` + `
`. |
| 1074 | roman_to_dec_1_to_10 | Reads a Roman numeral string (one of `I`, `II`, ..., `X`) + `
` and prints the decimal `1`-`10` + `
`. |

## encoding

| # | name | description |
|---|---|---|
| 1342 | hex_dump_line | Reads a `
`-terminated line ≤ 16 chars. For each byte (excluding `
`), prints its 2-char lowercase hex, with space separators between bytes, then `
`. Example: input `hi
` → output `68 69
`. Empty input → just `
`. |
| 1343 | binary_dump_line | Reads a `
`-terminated line ≤ 16 chars. For each byte (excluding `
`), prints its 8-char binary representation (MSB first), space-separated, then `
`. |
| 1344 | octal_dump_line | Reads a `
`-terminated line ≤ 16 chars. For each byte (excluding `
`), prints its 3-char octal representation (zero-padded), space-separated, then `
`. |
| 1345 | decimal_dump_line | Reads a `
`-terminated line ≤ 16 chars. For each byte (excluding `
`), prints its decimal value (1-3 chars, no zero padding), space-separated, then `
`. |
| 1346 | ascii_table_printable_32_126 | No input. Prints lines `<code> <char>
` for each ASCII code 32-126 (printable range, 95 lines total). |
| 1347 | run_length_encode_simple | Reads a `
`-terminated lowercase-letter string ≤ 30 chars (runs of length ≤ 9). Prints run-length encoding as alternating `<letter><count>` concatenated, then `
`. Example: `aabcccccaaa` → `a2b1c5a3
`. |
| 1348 | run_length_decode_simple | Reads a `
`-terminated RLE string of alternating `<letter><digit 1-9>` ≤ 30 chars. Prints decoded string + `
`. Example: `a2b1c5` → `aabccccc
`. |
| 1349 | percent_encode_space | Reads a `
`-terminated line ≤ 40 chars. Replaces each space byte (` `) with `%20`. Other bytes unchanged. Prints result + `
`. |
| 1350 | percent_decode_space | Reads a `
`-terminated line ≤ 60 chars (may contain `%20` sequences). Replaces each `%20` triplet with a single space. Other bytes unchanged. Prints result + `
`. |
| 1351 | html_entity_encode_basic | Reads a `
`-terminated line ≤ 40 chars. Replaces `&` with `&amp;`, `<` with `&lt;`, `>` with `&gt;`. Other bytes unchanged. Prints result + `
`. |
| 1352 | html_entity_decode_basic | Reads a `
`-terminated line ≤ 80 chars (may contain `&amp;`/`&lt;`/`&gt;` sequences). Replaces each with `&`/`<`/`>` respectively. Other bytes unchanged. Prints result + `
`. |
| 1353 | atbash_cipher | Reads a `
`-terminated line ≤ 80 chars. For each letter, maps `a↔z`, `b↔y`, ..., `m↔n` (and the same within `A-Z`). Non-letters unchanged. Prints result + `
`. |
| 1354 | nato_phonetic_letter | Reads exactly one byte `A`-`Z` (no `
` required). Prints the NATO phonetic word for that letter (`Alpha`/`Bravo`/`Charlie`/.../`Zulu`) followed by `
`. |
| 1355 | nato_phonetic_word | Reads a `
`-terminated NATO phonetic word (one of the 26 standard words, exactly as spelled, capitalized). Prints the corresponding single uppercase letter (`A`-`Z`) + `
`. |
| 1356 | xor_key_07_roundtrip | Reads a `
`-terminated line ≤ 30 chars. XORs each byte (excluding `
`) with `0x07`. Outputs the XORed bytes followed by `
`. (Self-inverse — running twice on the same input yields original.) |
| 1357 | checksum_byte_sum | Reads a `
`-terminated line ≤ 30 chars. Prints the sum of the byte values (excluding `
`) modulo 256 as decimal + `
`. |
| 1358 | checksum_xor | Reads a `
`-terminated line ≤ 30 chars. Prints the XOR of all byte values (excluding `
`) as two lowercase hex chars + `
`. |
| 1359 | parity_byte_compute | Reads exactly 7 ASCII bits (each `0` or `1` byte, all on one `
`-terminated line, e.g. `1010101
`). Prints `0
` if the count of 1s among the 7 input bits is even, `1
` if odd. (This is the parity bit that, when appended, makes total ones EVEN.) |
| 1360 | nibble_dump_hex_colon | Reads a `
`-terminated line ≤ 16 chars. For each byte (excluding `
`), prints `<high>:<low>` where `<high>` is the high nibble's hex char and `<low>` is the low nibble's. Entries are space-separated; final `
`. Example: input `Aa
` → output `4:1 6:1
`. |
| 1361 | quoted_printable_simple | Reads a `
`-terminated line ≤ 20 chars. Each byte (excluding `
`) that is NOT printable ASCII (`0x20`-`0x7e`) becomes `=NN` where `NN` is its 2-char uppercase hex. Printable bytes unchanged. Prints result + `
`. |
| 1362 | count_chars_per_class | Reads a `
`-terminated line ≤ 80 chars. Prints `digits: <D>
letters: <L>
spaces: <S>
other: <O>
` where `D`/`L`/`S`/`O` are the counts of digits, letters, spaces, and other byte classes respectively (excluding the terminating `
`). |
| 1363 | csv_split_one_field | Reads a `
`-terminated CSV line ≤ 60 chars (no embedded commas in fields, no quotes). Prints each comma-separated field on its own line. |
| 1364 | tsv_to_csv | Reads a `
`-terminated TSV line ≤ 60 chars (tab-separated). Outputs the same line with each `\t` replaced by `,`. Final `
` preserved. |
| 1365 | csv_to_tsv | Reads a `
`-terminated CSV line ≤ 60 chars (no quoted commas). Outputs the same line with each `,` replaced by `\t`. Final `
` preserved. |
| 1366 | ascii_to_hex_concat | Reads a `
`-terminated line ≤ 20 chars. Prints all bytes (excluding `
`) as concatenated lowercase hex (no separators) followed by `
`. Example: `Hi
` → `4869
`. |
| 1367 | hex_concat_to_ascii | Reads a `
`-terminated lowercase-hex string ≤ 40 chars (even length). Prints decoded bytes + `
`. |
| 1368 | xor_encrypt_cycling_key | Reads a `
`-terminated key (`≤ 8 chars`), then a `
`-terminated message (`≤ 30 chars`). XORs each message byte (excluding terminating `
`) with `key[i mod key_length]`. Outputs the XOR'd bytes followed by `
`. |
| 1369 | ascii_to_morse_letter | Reads exactly one byte (a single lowercase letter `a`-`z` or digit `0`-`9`). Prints the International Morse Code representation using `.` and `-` (no spaces) + `
`. Example: `a` → `.-
`; `0` → `-----
`. |
| 1370 | morse_to_ascii_letter | Reads a `
`-terminated Morse Code sequence (using only `.` and `-`, ≤ 6 chars, one of the 36 lowercase-letter / digit codes). Prints the decoded ASCII byte (no extra `
`). |
| 1371 | nibble_to_base64_char | Reads a decimal `0`-`15` + `
`. Prints the corresponding base64 alphabet character (`A` for 0, `B` for 1, ..., `P` for 15), followed by `
`. |
| 1372 | emoji_smiley_or_frown | Reads exactly one byte `0` or `1` followed by `
`. Prints `:)
` for `1`, `:(
` for `0`. |
| 1373 | byte_class_counts | Reads a `
`-terminated line ≤ 80 chars. Prints `printable: <P>
control: <C>
` where `P` is the count of printable bytes (`0x20`-`0x7e`) and `C` is the count of control bytes (`<0x20` or `0x7f`), all excluding the terminating `
`. |
| 1374 | binary_xor_two_inputs | Reads two `
`-terminated 8-char binary strings (each on its own line, each is 8 chars of `0`/`1`). Prints their bitwise XOR as an 8-char binary string + `
`. |
| 1375 | binary_and_two_inputs | Same I/O shape as `binary_xor_two_inputs` but prints bitwise AND. |
| 1376 | binary_or_two_inputs | Same I/O shape as `binary_xor_two_inputs` but prints bitwise OR. |
| 1377 | xxd_style_dump | Reads a `
`-terminated line ≤ 16 chars. Prints one line: 4-digit zero-padded offset `0000`, two spaces, then hex bytes (lowercase, space-separated, max 16 bytes), then 2 spaces, then the printable ASCII (non-printables as `.`), then `
`. Example: input `hi
` → `0000  68 69  hi
`. |

## algorithms

| # | name | description |
|---|---|---|
| 1168 | linear_search_count | Reads digit N `1`-`9` + `
`, then N decimals (each own line), then a target decimal. Prints the count of occurrences of the target in the array as decimal + `
`. |
| 1169 | linear_search_last | Reads digit N `1`-`9` + `
`, then N decimals, then target. Prints the 0-based index of the LAST occurrence + `
`, or `not found
` if absent. |
| 1170 | binary_search_first_match | Reads digit N `1`-`9` + `
`, then N decimals sorted ascending (may have duplicates), then target. Prints the 0-based index of the FIRST occurrence (lower-bound) + `
`, or `not found
`. |
| 1171 | binary_search_last_match | Reads digit N `1`-`9` + `
`, then N decimals sorted ascending (may have duplicates), then target. Prints the 0-based index of the LAST occurrence (upper-bound-1) + `
`, or `not found
`. |
| 1172 | jump_search_sorted | Reads digit N `1`-`9` + `
`, then N decimals sorted ascending, then target. Prints the 0-based index of any match + `
`, or `not found
`. Implementation: jump search (block size ~√N, linear scan within block). |
| 1173 | exponential_search_sorted | Reads digit N `1`-`9` + `
`, then N decimals sorted ascending, then target. Prints the 0-based index of any match + `
`, or `not found
`. Implementation: exponential search (find range by doubling i, then binary search within range). |
| 1174 | ternary_search_sorted | Reads digit N `1`-`9` + `
`, then N decimals sorted ascending, then target. Prints the 0-based index of any match + `
`, or `not found
`. Implementation: ternary search (divide range into thirds). |
| 1175 | dutch_flag_3way | Reads digit N `1`-`9` + `
`, then N values each `0`, `1`, or `2` (one per line). Prints the values partitioned in order so all 0s come first, then all 1s, then all 2s (one per line). |
| 1176 | longest_run_length | Reads digit N `1`-`9` + `
`, then N decimals. Prints the length of the longest run of equal consecutive elements as decimal + `
`. |
| 1177 | find_missing_in_sequence | Reads digit N `2`-`9` + `
`, then `N-1` decimals which are some permutation of `{1, 2, ..., N}` with exactly one value missing. Prints the missing value + `
`. |
| 1178 | find_duplicate_in_sequence | Reads digit N `2`-`9` + `
`, then N decimals from `{1, 2, ..., N-1}` with exactly one value duplicated. Prints the duplicated value + `
`. |
| 1179 | is_permutation_1_to_n | Reads digit N `1`-`9` + `
`, then N decimals. Prints `1
` if the sequence is a permutation of `{1, 2, ..., N}`, else `0
`. |
| 1180 | min_max_one_pass | Reads digit N `1`-`9` + `
`, then N signed decimals. Prints `<min>
<max>
` using a single pass (pair-compare optimization). |
| 1181 | kadane_max_subarray | Reads digit N `1`-`9` + `
`, then N signed decimals. Prints the maximum contiguous subarray sum as signed decimal + `
`. Implementation: Kadane's algorithm. |
| 1182 | zigzag_array_check | Reads digit N `1`-`9` + `
`, then N decimals. Prints `1
` if the sequence strictly alternates `a[0] < a[1] > a[2] < a[3] > ...` (starting with rise), else `0
`. |
| 1183 | count_distinct_elements | Reads digit N `1`-`9` + `
`, then N decimals. Prints the count of distinct values + `
`. |
| 1184 | is_palindrome_array | Reads digit N `1`-`9` + `
`, then N decimals. Prints `1
` if the sequence reads the same forward and backward, else `0
`. |
| 1185 | count_local_maxima | Reads digit N `3`-`9` + `
`, then N decimals. Prints the count of strict local maxima (positions `i` with `0 < i < N-1` and `a[i-1] < a[i] > a[i+1]`) + `
`. |
| 1186 | count_local_minima | Reads digit N `3`-`9` + `
`, then N decimals. Prints the count of strict local minima + `
`. |
| 1187 | two_sum_unsorted | Reads digit N `2`-`9` + `
`, then N decimals, then `target`. Prints `i j
` (0-based, `i < j`) of any pair summing to target, or `not found
`. Implementation: nested loop. |
| 1188 | two_sum_sorted_two_pointers | Reads digit N `2`-`9` + `
`, then N decimals sorted ascending, then `target`. Prints `i j
` (0-based, `i < j`) of any pair summing to target, or `not found
`. Implementation: two-pointer (left, right). |
| 1189 | three_sum_zero | Reads digit N `3`-`9` + `
`, then N signed decimals. Prints `i j k
` (0-based, `i < j < k`) of any triple summing to 0, or `none
`. |
| 1190 | max_product_pair | Reads digit N `2`-`9` + `
`, then N signed decimals. Prints the maximum product of any two distinct-indexed elements as signed decimal + `
`. |
| 1191 | min_product_pair | Reads digit N `2`-`9` + `
`, then N signed decimals. Prints the minimum product of any two distinct-indexed elements + `
`. |
| 1193 | mode_of_5 | Reads exactly 5 decimals and prints the most frequent value + `
`. Ties broken by smallest value among the most frequent. |
| 1194 | mean_median_mode_5 | Reads exactly 5 decimals and prints `<mean>
<median>
<mode>
` (floor mean; median = middle of sorted; mode = most frequent value, ties broken by smallest). |
| 1195 | moore_voting_majority | Reads digit N `1`-`9` + `
`, then N decimals. Prints the majority element (value appearing strictly more than N/2 times) + `
`, or `none
` if no majority. Implementation: Boyer-Moore voting (one-pass + verify). |
| 1196 | tortoise_hare_cycle | Reads `start` `0`-`15` (own line). Iterates `x = (2*x + 1) mod 16` starting from `start`. Uses Floyd's tortoise-and-hare to detect when the sequence enters a cycle, then prints the cycle length as decimal + `
`. |
| 1197 | sieve_of_eratosthenes_30 | No input. Prints the primes in `[2, 30]` space-separated on one line + `
`: `2 3 5 7 11 13 17 19 23 29
`. Implementation: sieve of Eratosthenes (mark composites). |
| 1198 | sieve_of_eratosthenes_50 | No input. Prints the primes in `[2, 50]` space-separated + `
`. Implementation: sieve of Eratosthenes. |
| 1199 | euclidean_gcd_with_steps | Reads two positive decimals `a`, `b` each `1`-`100` (own lines). Prints each step of Euclidean GCD as `a b
` (current pair after `a = b, b = a % b`), terminating with `<gcd> 0
`. |
| 1200 | extended_gcd_small | Reads two positive decimals `a`, `b` each `1`-`30` (own lines). Prints `g x y
` such that `a*x + b*y = g = gcd(a, b)`, where `x`, `y` may be signed integers. |
| 1201 | fast_exponentiation | Reads `base` `2`-`5`, `exp` `0`-`10`, `mod` `1`-`100` (each own line). Prints `(base^exp) mod mod` as decimal + `
`. Implementation: exponentiation-by-squaring. |
| 1202 | matrix_transpose_3x3 | Reads 9 decimals (3 rows × 3 cols, row-major, each own line). Prints the transposed 3×3 matrix in row-major order, one row per output line with space-separated values + `
` per row (3 lines total). |
| 1203 | matrix_diagonal_sum_3x3 | Reads 9 decimals (3×3 row-major). Prints the sum of the main diagonal `a[0][0] + a[1][1] + a[2][2]` as decimal + `
`. |
| 1204 | matrix_is_symmetric_3x3 | Reads 9 decimals (3×3 row-major). Prints `1
` if the matrix equals its transpose, else `0
`. |
| 1205 | variance_5 | Reads exactly 5 decimals `0`-`99` (each on own line). Computes `mean = floor(sum/5)`, then `variance = sum((x_i - mean)^2) / 5` (floor). Prints variance as decimal + `
`. |
| 1206 | std_dev_5_floor_sqrt | Reads exactly 5 decimals `0`-`99`. Computes variance (as in `variance_5`), then prints `floor(sqrt(variance))` as decimal + `
`. Use integer-sqrt by linear scan. |
| 1207 | range_5_fixed | Reads exactly 5 decimals and prints `max - min` as decimal + `
`. |
| 1208 | mean_abs_deviation_5 | Reads exactly 5 decimals `0`-`99`. Computes `mean = floor(sum/5)`, then prints `floor(sum(|x_i - mean|) / 5)` as decimal + `
`. |
| 1209 | bernoulli_trial_count_8 | Reads exactly 8 raw bytes. Counts how many are even (a "success"). Prints count `0`-`8` as decimal + `
`. |
| 1210 | coin_until_first_head | Reads up to 20 raw bytes one at a time. Stops as soon as a byte with even value is read ("heads"). Prints the count of bytes read up to and including that first head as decimal + `
`. If no head appears in 20 bytes, prints `-1
`. |
| 1211 | z_score_compare_5 | Reads exactly 5 decimals `0`-`99` (population), then 1 additional decimal `0`-`99` (test value). Computes `mean` and `std_dev_5_floor_sqrt` of the 5 population values. Prints `floor((test - mean) / max(std_dev, 1))` as a signed decimal + `
`. |
| 1212 | coefficient_of_variation_5 | Reads exactly 5 decimals `1`-`99`. Computes `mean` and `std_dev_5_floor_sqrt`. Prints `floor(std_dev * 100 / mean)` as decimal percent + `
`. |
| 1213 | weighted_mean_3 | Reads 3 decimals (values `0`-`99` on own lines) then 3 decimals (weights `1`-`9` on own lines). Prints `floor(sum(v_i * w_i) / sum(w_i))` as decimal + `
`. |
| 1214 | lcg_step_8bit | Reads one byte (the seed/state). Applies one LCG step: `state = (state * 5 + 3) mod 256`. Outputs the new state as one raw byte. |
| 1215 | lcg_steps_n_8bit | Reads one byte (seed), then one decimal digit N `1`-`9` + `
`. Applies N LCG steps (constants `5` and `3`, mod 256) and prints each successive state as decimal on its own line (N lines total). |
| 1216 | xorshift_step_8bit | Reads one non-zero byte (state). Applies xorshift8: `s ^= s << 3; s ^= s >> 4; s ^= s << 2;` (all mod 256). Outputs the new state as one raw byte. |
| 1217 | xorshift_steps_n_8bit | Reads one non-zero byte (state), then decimal N `1`-`9` + `
`. Applies N xorshift8 steps. Prints each successive state as decimal on its own line. |
| 1218 | fisher_yates_shuffle_5 | Reads 5 decimals `0`-`9` (each on own line), then 5 raw bytes (the PRNG bytes). Applies Fisher-Yates shuffle: for `i` from 4 down to 1, swap `arr[i]` with `arr[byte[5-i] mod (i+1)]`. Prints the shuffled array as 5 decimals space-separated + `
`. |
| 1219 | dice_rolls_lcg_5 | Reads one byte (seed). Applies 5 LCG steps and prints `(state mod 6) + 1` as a decimal digit `1`-`6` on its own line (5 lines total). |
| 1220 | middle_square_step | Reads two bytes (low and high of a 16-bit state). Applies one middle-square step: square the 16-bit state to get a 32-bit result, then take the middle 16 bits. Outputs the new state as two raw bytes (low then high). |
| 1221 | blum_blum_shub_tiny | Reads one byte `1`-`15` (state). Applies one BBS step: `state = (state * state) mod 21` (where `21 = 3 * 7`, both Blum primes). Outputs the new state as one raw byte. |
| 1222 | weighted_choice_lcg | Reads three decimal weights `w0 w1 w2` (each `0`-`9`, on own lines; sum >= 1), then one byte (seed). Generates one LCG sample `r`, then picks bucket `i` such that `r mod (w0+w1+w2) < w0+w1+...+wi`. Prints `i` as decimal `0`-`2` + `
`. |
| 1223 | random_bits_n | Reads one byte (seed), then decimal N `1`-`9` + `
`. Applies N LCG steps and outputs the LSB of each state as a `0` or `1` char, all concatenated on a single line + `
`. |
| 1224 | random_byte_in_range | Reads one byte (seed), then `lo` `hi` (each on own line, both `0`-`9`, `lo <= hi`). Applies one LCG step, computes `lo + (state mod (hi - lo + 1))`, and prints as decimal + `
`. |
| 1225 | shuffle_short_string | Reads a `
`-terminated line of exactly 5 chars, then 5 raw bytes (PRNG). Applies Fisher-Yates shuffle on the 5 chars using the PRNG bytes (same indexing rule as `fisher_yates_shuffle_5`). Prints shuffled string + `
`. |
| 1226 | prng_period_count | Reads one byte (seed). Applies LCG steps with constants `5`, `3`, mod 256, counting steps until the state returns to the seed value. Prints the period as decimal + `
`. |
| 1227 | count_below_threshold_lcg | Reads one byte (seed), then one byte (threshold). Applies 10 LCG steps and counts how many states are strictly `<` threshold. Prints the count as decimal `0`-`10` + `
`. |
| 1228 | quicksort_5 | Reads exactly 5 decimal integers (each on own line) and prints them sorted ascending (one per line). Implementation: quicksort (recursive partition around a pivot). |
| 1229 | mergesort_5 | Reads exactly 5 decimals and prints them sorted ascending (one per line). Implementation: merge sort (recursive split + merge). |
| 1230 | heap_sort_5 | Reads exactly 5 decimals and prints them sorted ascending (one per line). Implementation: heap sort (build max-heap, repeatedly extract max). |
| 1231 | counting_sort_n_small | Reads digit N `1`-`9` + `
`, then N single-digit decimals `0`-`9`. Prints them sorted ascending (one per line) via counting sort (tally each value then emit in order). |
| 1232 | radix_sort_n_small | Reads digit N `1`-`9` + `
`, then N two-digit decimals `0`-`99`. Prints them sorted ascending (one per line) via radix sort (two passes: ones then tens). |
| 1233 | shell_sort_5 | Reads exactly 5 decimals and prints them sorted ascending. Implementation: shell sort with gap sequence `2, 1`. |
| 1234 | cycle_sort_5 | Reads exactly 5 decimals and prints them sorted ascending. Implementation: cycle sort (minimum-write sort — find each element's correct position and place via cycle following). |
| 1235 | pancake_sort_5 | Reads exactly 5 decimals and prints them sorted ascending. Implementation: pancake sort — only prefix reversals (no swaps). |
| 1236 | wave_array_arrange | Reads digit N `1`-`9` + `
`, then N decimals. Prints them rearranged in wave pattern (sorted ascending, then adjacent pairs swapped: `a[0] >= a[1] <= a[2] >= a[3] <= ...`), one per line. |

## geometry

| # | name | description |
|---|---|---|
| 0573 | dot_product_2d | Reads 4 decimals `a b c d` (each own line) representing vectors `(a,b)` and `(c,d)`. Prints `a*c + b*d` as signed decimal + `
`. |
| 0574 | cross_product_2d_scalar | Reads 4 decimals (each own line) representing two 2D vectors. Prints the scalar cross product `a*d - b*c` as signed decimal + `
`. |
| 0575 | midpoint_2d | Reads 4 decimals `x1 y1 x2 y2` (each own line). Prints `<mx> <my>
` where `mx = (x1+x2)/2` and `my = (y1+y2)/2` (floor division). |
| 0576 | is_origin | Reads 2 decimals `x y` (each own line). Prints `1
` if both are `0`, else `0
`. |
| 0577 | is_on_x_axis | Reads 2 decimals (each own line). Prints `1
` if `y == 0`, else `0
`. |
| 0578 | is_on_y_axis | Reads 2 decimals (each own line). Prints `1
` if `x == 0`, else `0
`. |
| 0579 | is_collinear_3 | Reads 6 decimals representing 3 points `(x1,y1) (x2,y2) (x3,y3)` (each coordinate on its own line). Prints `1
` if collinear (i.e. `(x2-x1)*(y3-y1) - (y2-y1)*(x3-x1) == 0`), else `0
`. |
| 0581 | rectangle_area | Reads two decimals `width` `height` (each own line, `0`-`100`). Prints `width * height` + `
`. |
| 0582 | rectangle_perimeter | Reads `width` `height` (each own line, `0`-`100`). Prints `2 * (width + height)` + `
`. |
| 0585 | square_perimeter | Reads decimal side `0`-`100` + `
`. Prints `4 * side` + `
`. |
| 0586 | cube_surface_area | Reads decimal side `0`-`20` + `
`. Prints `6 * side * side` + `
`. |
| 0587 | is_point_inside_rect | Reads 6 decimals (each own line): point `x y` then rect `xmin ymin xmax ymax`. Prints `1
` if `xmin <= x <= xmax` and `ymin <= y <= ymax`, else `0
`. |
| 0588 | is_point_inside_circle | Reads 5 decimals (each own line): point `x y`, center `cx cy`, radius `r` (all `0`-`50`). Prints `1
` if `(x-cx)^2 + (y-cy)^2 <= r^2`, else `0
`. |
| 0589 | is_right_triangle_from_sides | Reads 3 decimals `a b c` (each own line, each `1`-`50`) representing triangle side lengths in any order. Prints `1
` if some permutation satisfies `a^2 + b^2 == c^2`, else `0
`. |
| 0590 | is_isosceles | Reads 3 decimals (each on own line) representing triangle side lengths. Prints `1
` if at least two of the three sides are equal (i.e. equilateral triangles also qualify), else `0
`. |
| 0591 | is_equilateral | Reads 3 decimals. Prints `1
` if all three sides equal, else `0
`. |
| 0592 | is_scalene | Reads 3 decimals. Prints `1
` if all three sides are distinct, else `0
`. |
| 0593 | perpendicular_vectors_check | Reads 4 decimals (two 2D vectors). Prints `1
` if their dot product is `0` (perpendicular), else `0
`. |
| 0594 | parallel_vectors_check | Reads 4 decimals (two 2D vectors). Prints `1
` if their scalar cross product is `0` (parallel or anti-parallel), else `0
`. |
| 0595 | slope_int_or_undefined | Reads 4 decimals `x1 y1 x2 y2` (each own line, signed). If `x1 == x2`, prints `undefined
`. Otherwise prints `(y2 - y1) / (x2 - x1)` as signed integer division + `
`. |
| 1054 | manhattan_distance | Reads 4 decimals `x1 y1 x2 y2` (each own line). Prints `|x2-x1| + |y2-y1|` as decimal + `
`. |
| 1055 | chebyshev_distance | Reads 4 decimals (each own line). Prints `max(|x2-x1|, |y2-y1|)` + `
`. |
| 1056 | euclidean_distance_floor | Reads 4 decimals `x1 y1 x2 y2` (each `0`-`9`, own line). Prints `floor(sqrt((x2-x1)^2 + (y2-y1)^2))` as decimal + `
`. Squared distance ≤ 162, so integer sqrt via linear scan (`k` while `k² <= d`) stays trivially within compile budget. |
| 1057 | signed_triangle_area_2x | Reads 6 decimals (3 vertices, each coord own line). Prints `x1*(y2-y3) + x2*(y3-y1) + x3*(y1-y2)` as signed decimal + `
` (this is exactly 2× the signed area). |
| 1058 | circle_area_approx | Reads decimal radius `0`-`9` + `
`. Prints `(r * r * 314) / 100` (integer approximation of π·r²) + `
`. |
| 1059 | circle_circumference_approx | Reads decimal radius `0`-`9` + `
`. Prints `(2 * r * 314) / 100` (integer approximation of 2πr) + `
`. |
| 1060 | counts_inside_unit_circle_grid_3x3 | No input. Counts how many of the 9 lattice points `(i,j)` for `i,j ∈ {-1,0,1}` satisfy `i^2 + j^2 <= 1`. Prints the count as decimal + `
` (answer: 5). |

## simulation

| # | name | description |
|---|---|---|

## puzzles

| # | name | description |
|---|---|---|
| 1444 | n_queens_4_count | No input. Prints the number of distinct solutions to the 4-queens problem (`2`) + `
`. |
| 1445 | eight_queens_solution_count | No input. Prints `92` + `
` (the number of distinct solutions to the 8-queens problem). |
| 1446 | eight_queens_one_solution | No input. Prints one valid 8-queens solution as 8 column indices `0`-`7` for rows 0..7, space-separated, then `
`. (Use a canonical first solution.) |
| 1447 | magic_square_check_3x3 | Reads 9 decimals (3×3 row-major, each on own line). Prints `1
` if all 3 rows, all 3 columns, and both diagonals have the same sum, else `0
`. |
| 1448 | magic_square_fill_missing | Reads 9 decimals (3×3 row-major, each on own line) representing a known-valid 3×3 magic square with EXACTLY ONE cell replaced by `0` (the missing value). Prints the missing value as decimal + `
`. |
| 1449 | magic_constant_for_n | Reads digit N `3`-`9` + `
`. Prints `N * (N^2 + 1) / 2` (the magic constant for an N×N magic square containing `1..N²`) + `
`. |
| 1450 | sudoku_row_check_9 | Reads 9 decimals `1`-`9` (each on own line). Prints `1
` if all 9 values are distinct (a valid Sudoku row/column/block), else `0
`. |
| 1451 | sudoku_full_validation | Reads 9 lines, each 9 decimals (separated by spaces) representing a 9×9 Sudoku grid filled with `1`-`9`. Prints `1
` if all 9 rows AND all 9 columns AND all 9 3×3 boxes contain `1..9` (every row/col/box has 9 distinct values), else `0
`. |
| 1452 | tic_tac_toe_winner | Reads 3 lines of 3 chars each (`X`, `O`, or `.`) representing a tic-tac-toe board. Prints `X
` if X has won (three in a row/col/diag), `O
` if O has won, else `none
`. (Assume at most one side has won.) |
| 1453 | tic_tac_toe_board_full | Reads 3 lines of 3 chars each. Prints `1
` if no `.` chars remain (board is full), else `0
`. |
| 1454 | tic_tac_toe_simulate_moves | Reads digit N `1`-`9` + `
`, then N moves (each one digit `0`-`8` on its own line, indicating cell position 0=top-left, row-major). Players alternate starting with `X`. Prints the final 3×3 board (3 lines of 3 chars each, `.` for unmoved cells). |
| 1455 | tower_of_hanoi_count | Reads digit N `1`-`9` + `
`. Prints `2^N - 1` (minimum moves) + `
`. |
| 1456 | tower_of_hanoi_print_moves_3 | No input. Prints all 7 moves for the 3-disk Tower of Hanoi (from peg `A` to peg `C` using `B`), one per line, formatted `<disk>: <src>-><dst>
`. Example first move: `1: A->C
`. |
| 1457 | tower_of_hanoi_print_moves_4 | No input. Same format as `tower_of_hanoi_print_moves_3` but for 4 disks (15 moves total). |
| 1458 | word_anagram_check | Reads two `
`-terminated lowercase words (each ≤ 10 chars). Prints `1
` if they are anagrams (same multiset of letters), else `0
`. |
| 1459 | permutation_check_n | Reads digit N `1`-`9` + `
`, then N decimals (each own line), then another N decimals. Prints `1
` if the second N-tuple is a permutation of the first (same multiset), else `0
`. |
| 1460 | arithmetic_progression_check_5 | Reads exactly 5 signed decimals (each own line). Prints `1
` if they form an arithmetic progression (constant difference between consecutive elements), else `0
`. |
| 1461 | geometric_progression_check_4 | Reads exactly 4 decimals each `1`-`50` (own line). Prints `1
` if they form a geometric progression with integer common ratio `>= 2` (i.e. `a[i+1] = a[i] * r` for some integer `r >= 2`), else `0
`. |
| 1462 | fibonacci_5_check | Reads exactly 5 decimals (each own line). Prints `1
` if they match the first 5 Fibonacci values `0 1 1 2 3` exactly in order, else `0
`. |
| 1463 | find_missing_arith_progression | Reads exactly 4 decimals (each own line) with the value `0` representing a single missing element of a 4-element arithmetic progression. The remaining 3 values are in their correct AP positions; the `0` is the placeholder. Prints the missing value as decimal + `
`. |
| 1464 | find_missing_geom_progression | Reads exactly 4 decimals `1`-`50` with one being `0` (the missing entry) of a 4-element geometric progression with integer common ratio `>= 2`. Prints the missing value + `
`. |
| 1465 | counting_squares_2x2 | No input. Prints `5
` (the number of squares in a 2×2 lattice grid: four unit squares + one 2×2 square). |
| 1466 | counting_squares_3x3 | No input. Prints `14
` (number of squares in a 3×3 lattice grid: 9 unit + 4 of side 2 + 1 of side 3). |
| 1467 | counting_rectangles_3x3 | No input. Prints `36
` (number of rectangles in a 3×3 lattice grid). |
| 1468 | coin_change_count_small | Reads decimal amount `1`-`20` + `
`. Prints the number of distinct ways to make `amount` cents using coins of denominations `{1, 5, 10}` (order doesn't matter) + `
`. |
| 1469 | eight_puzzle_check_solved | Reads 9 decimals (each `0`-`8`, own line) representing a 3×3 8-puzzle state (0 = blank). Prints `1
` if it equals the solved state `1 2 3 4 5 6 7 8 0` (row-major), else `0
`. |
| 1470 | fifteen_puzzle_check_solved | Reads 16 decimals (each `0`-`15`, own line) representing a 4×4 15-puzzle state (0 = blank). Prints `1
` if it equals the solved state `1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 0` (row-major), else `0
`. |
| 1471 | cryptarithm_one_plus_one | Reads exactly 3 decimal digits `a b c` (each `0`-`9`, own line). Prints `1
` if `a + b == c` (i.e. the cryptarithm `a + b = c` is satisfied), else `0
`. |
| 1472 | river_crossing_count_classic | No input. Prints `7
` (the minimum number of trips for the classic farmer-wolf-goat-cabbage river crossing puzzle). |
| 1473 | bishop_attack_check | Reads 4 decimals `r1 c1 r2 c2` (each `0`-`7`, own line) — the two bishops' chessboard positions. Prints `1
` if they're on the same diagonal (i.e. `|r1-r2| == |c1-c2|`), else `0
`. |
| 1474 | rook_attack_check | Reads 4 decimals `r1 c1 r2 c2` (each `0`-`7`, own line). Prints `1
` if they're on the same row or same column, else `0
`. |
| 1475 | knight_attack_check | Reads 4 decimals `r1 c1 r2 c2` (each `0`-`7`, own line). Prints `1
` if they're one knight's move apart (i.e. `(|Δr|, |Δc|) == (1,2)` or `(2,1)`), else `0
`. |
| 1476 | queen_attack_check | Reads 4 decimals `r1 c1 r2 c2` (each `0`-`7`, own line). Prints `1
` if same row OR same column OR same diagonal, else `0
`. |
| 1477 | king_attack_check | Reads 4 decimals `r1 c1 r2 c2` (each `0`-`7`, own line). Prints `1
` if `max(|r1-r2|, |c1-c2|) == 1` (king's move neighbors), else `0
`. |
| 1478 | pawn_white_move_count | Reads 2 decimals `r c` (each `0`-`7`, own line) — a white pawn's position. Prints the number of legal forward moves (`1` from a non-starting row, `2` from row 6, `0` from row 0). |
| 1479 | is_chessboard_color | Reads 2 decimals `r c` (each `0`-`7`, own line). Prints `0
` if the square is "white" (i.e. `(r + c)` is even with a8/`r=0,c=0` treated as white), else `1
`. |
| 1480 | eight_queens_attack_pair_count | Reads exactly 8 decimals (each `0`-`7`, own line) representing the column of a queen for each row 0..7. Prints the count of pairs `(i, j)` with `i < j` such that queens on rows i and j attack each other (same column, or `|rows[i] - rows[j]| == |i - j|`) + `
`. |
| 1481 | dragon_curve_3_iterations | No input. Prints the heighway-dragon L/R turn sequence after exactly 3 paper-fold iterations, where `L` denotes a left turn and `R` denotes a right turn. The 3rd-iteration sequence has length `2^3 - 1 = 7`. Convention: start with a single `L` (1st iteration), and each next iteration appends `L` then the reverse-and-swap of the prior sequence. This yields iteration-3 = `LLRLLRR`. Output is exactly `LLRLLRR
`. |
| 1482 | partition_count_n | Reads digit N `1`-`9` + `
`. Prints the number of integer partitions of N (e.g. `p(4) = 5`) + `
`. |
| 1483 | knights_knaves_2 | Reads 2 decimals `s1` `s2` (each `0` or `1`, on own lines) representing two islanders' statements about each other: `s1`=0 means islander A says "B is a knight"; `s1`=1 means A says "B is a knave"; `s2` similarly is B's statement about A. Prints one of `AK BK
`, `AK BN
`, `AN BK
`, `AN BN
` (the consistent assignment) or `paradox
` if no consistent assignment exists. |
| 1484 | cnf_2var_2clause_sat | Reads two 2-CNF clauses as lines, each in the form `<lit1> <lit2>` where each literal is `x`, `!x`, `y`, or `!y`. Prints `SAT
` if there's an assignment to x, y making both clauses true, else `UNSAT
`. |
| 1485 | propositional_eval_2var | Reads a formula string `
`-terminated using only `x`, `y`, `&` (AND), `|` (OR), `!` (NOT), `(`, `)`. Then reads `x` value `0` or `1` + `
` and `y` value `0` or `1` + `
`. Prints `0
` or `1
` based on the evaluated formula. Formula ≤ 15 chars. |
| 1486 | tautology_check_2var | Reads a formula string `
`-terminated (same syntax as `propositional_eval_2var`, ≤ 15 chars). Prints `1
` if the formula is true for all 4 assignments of `x`, `y`, else `0
`. |

## sequences

| # | name | description |
|---|---|---|
| 0431 | triangular_first_n | Reads digit N `1`-`9` + `
`. Prints the first N triangular numbers `T(k) = k(k+1)/2` for `k = 1..N`, space-separated, ending with `
`. |
| 0432 | square_first_n | Reads digit N `1`-`9` + `
`. Prints the first N positive squares `1, 4, 9, ..., N²`, space-separated, + `
`. |
| 0433 | pentagonal_first_n | Reads digit N `1`-`9` + `
`. Prints the first N pentagonal numbers `P(k) = k(3k - 1)/2`, space-separated, + `
`. |
| 0434 | hexagonal_first_n | Reads digit N `1`-`9` + `
`. Prints the first N hexagonal numbers `H(k) = k(2k - 1)`, space-separated, + `
`. |
| 0435 | cube_first_n | Reads digit N `1`-`9` + `
`. Prints the first N positive cubes `1, 8, 27, ..., N³`, space-separated, + `
`. |
| 0436 | tetrahedral_first_n | Reads digit N `1`-`9` + `
`. Prints the first N tetrahedral numbers `Te(k) = k(k+1)(k+2)/6`, space-separated, + `
`. |
| 0437 | catalan_first_5 | No input. Prints the first 5 Catalan numbers `1 1 2 5 14
`. |
| 0439 | derangement_first_5 | No input. Prints the first 5 derangement numbers `D(n)` for `n = 1..5`: `0 1 2 9 44
`. |
| 0440 | lucas_first_n | Reads digit N `1`-`9` + `
`. Prints `L(0), L(1), ..., L(N-1)` (where `L(0)=2, L(1)=1`), space-separated, + `
`. |
| 0441 | perrin_first_10 | No input. Prints the first 10 Perrin sequence values starting `P(0)=3, P(1)=0, P(2)=2`: `3 0 2 3 2 5 5 7 10 12
`. |
| 0442 | padovan_first_10 | No input. Prints the first 10 Padovan sequence values starting `1 1 1 2 2 3 4 5 7 9
`. |
| 0443 | jacobsthal_first_8 | No input. Prints the first 8 Jacobsthal numbers `J(n)` starting `0 1 1 3 5 11 21 43
`. |
| 0444 | pell_first_8 | No input. Prints the first 8 Pell numbers `P(n)` starting `0 1 2 5 12 29 70 169
`. |
| 0445 | tribonacci_first_10 | No input. Prints the first 10 Tribonacci values starting `T(0)=T(1)=0, T(2)=1`: `0 0 1 1 2 4 7 13 24 44
`. |
| 0446 | tetranacci_first_8 | No input. Prints the first 8 Tetranacci values starting `0 0 0 1 1 2 4 8
`. |
| 0447 | fibonacci_even_first_5 | No input. Prints the first 5 even Fibonacci numbers: `0 2 8 34 144
`. |
| 0448 | fibonacci_odd_first_5 | No input. Prints the first 5 odd Fibonacci numbers: `1 1 3 5 13
`. |
| 0449 | fibonacci_sum_first_n | Reads digit N `1`-`12` + `
`. Prints `F(1) + F(2) + ... + F(N)` (with `F(1)=1, F(2)=1, ...`) as decimal + `
`. |
| 0450 | fibonacci_squares_first_5 | No input. Prints `F(1)² F(2)² ... F(5)²` = `1 1 4 9 25` space-separated + `
`. |
| 0451 | fibonacci_modulo_10 | Reads decimal N in `1`-`20` (one or two ASCII digits, terminated by `
`). Prints `F(N) mod 10` as a single decimal digit + `
`. |
| 0453 | mersenne_first_5 | No input. Prints the first 5 Mersenne numbers `M(n) = 2^n - 1` for `n = 1..5`: `1 3 7 15 31` space-separated + `
`. |
| 0454 | mersenne_prime_first_3 | No input. Prints the first 3 Mersenne primes: `3 7 31` space-separated + `
`. |
| 0455 | fermat_first_4 | No input. Prints the first 4 Fermat numbers `F(n) = 2^(2^n) + 1` for `n = 0..3`: `3 5 17 257` space-separated + `
`. |
| 0457 | lazy_caterers_first_8 | No input. Prints the first 8 lazy caterer's numbers (max regions with N cuts of a disc): `1 2 4 7 11 16 22 29` space-separated + `
`. |
| 0458 | centered_triangular_first_5 | No input. Prints the first 5 centered triangular numbers: `1 4 10 19 31` space-separated + `
`. |
| 0459 | centered_square_first_5 | No input. Prints the first 5 centered square numbers: `1 5 13 25 41` space-separated + `
`. |
| 0460 | centered_hexagonal_first_5 | No input. Prints the first 5 centered hexagonal numbers: `1 7 19 37 61` space-separated + `
`. |
| 0917 | evens_first_n | Reads digit N `1`-`9` + `
`. Prints first N positive even numbers `2, 4, ..., 2N` space-separated + `
`. |
| 0918 | odds_first_n | Reads digit N `1`-`9` + `
`. Prints first N positive odd numbers `1, 3, ..., 2N-1` space-separated + `
`. |
| 0919 | powers_of_2_first_n | Reads digit N `1`-`7` + `
`. Prints `2^0, 2^1, ..., 2^(N-1)` space-separated + `
`. |
| 0920 | powers_of_3_first_n | Reads digit N `1`-`5` + `
`. Prints `3^0, 3^1, ..., 3^(N-1)` space-separated + `
`. |
| 0921 | fibonacci_pairs_first_n | Reads digit N `1`-`8` + `
`. Prints `<F(i)> <F(i+1)>
` for `i = 0..N-1` (N lines of consecutive Fibonacci pairs). |
| 0922 | mersenne_first_n | Reads digit N `1`-`7` + `
`. Prints first N Mersenne numbers `M(k) = 2^k - 1` for `k = 1..N`, space-separated + `
`. |
| 0923 | triangular_inverse_n | Reads decimal triangular number `1`-`55` + `
` (i.e. one of `1, 3, 6, 10, 15, 21, 28, 36, 45, 55`). Prints the index `k` such that `T(k) == input`, else `-1` if input isn't triangular. |
| 1070 | bell_first_5 | No input. Prints the first 5 Bell numbers `1 1 2 5 15
`. |
| 1071 | partition_first_5 | No input. Prints the first 5 integer-partition counts `p(1), ..., p(5)` = `1 2 3 5 7` space-separated + `
`. |
| 1072 | mersenne_check | Reads decimal N in `2`-`17` (one or two ASCII digits, terminated by `
`). Prints `1
` if `2^N - 1` is prime, else `0
`. (Upper bound `17` keeps trial division ≤ √(2^17 - 1) ≈ 362, well within runtime budget.) |

## text_processing

| # | name | description |
|---|---|---|
| 0461 | word_count_multiline | Reads stdin until an empty line (`
` alone). Prints the total count of whitespace-separated tokens across all non-empty lines as decimal + `
`. Whitespace = `' '`, `'\t'`, `'\n'`; runs collapse; leading/trailing whitespace introduce no empty tokens. |
| 0463 | word_length_avg | Reads a `
`-terminated line ≤ 80 chars. Computes lengths of whitespace-separated tokens (space/tab/newline whitespace, runs collapse). Prints the floor of (sum of word lengths) / (word count) as decimal + `
`. If no words, prints `0\n`. |
| 0464 | word_length_max | Reads a `
`-terminated line ≤ 80 chars. Prints the length of the longest whitespace-separated token as decimal + `
`. Empty input → `0\n`. |
| 0465 | word_length_min | Reads a `
`-terminated line ≤ 80 chars. Prints the length of the shortest whitespace-separated token as decimal + `
`. Empty input → `0\n`. |
| 0470 | period_sentence_count | Reads a `
`-terminated line ≤ 80 chars. Prints the count of `.` bytes in the line (excluding `
`) as decimal + `
`. (Approximates sentence count by period count.) |
| 0471 | capitalize_first_letter | Reads a `
`-terminated line ≤ 80 chars. If the first byte is `a`-`z`, outputs it uppercased; the rest of the line is unchanged. Includes final `
`. |
| 0472 | capitalize_words | Reads a `
`-terminated line ≤ 80 chars. Outputs the line with the first letter of each whitespace-separated word uppercased; all other letters lowercased. Whitespace and non-letters unchanged. Includes final `
`. |
| 0473 | uncapitalize_first | Reads a `
`-terminated line ≤ 80 chars. If the first byte is `A`-`Z`, outputs it lowercased; the rest of the line is unchanged. Includes final `
`. |
| 1098 | char_freq_table | Reads a `
`-terminated line ≤ 80 chars. Prints each distinct byte value (excluding `
`) and its count, one `<byte> <count>
` per line, in ascending byte-value order. |
| 1099 | longest_word | Reads a `
`-terminated line ≤ 80 chars. Prints the longest whitespace-separated token + `
`. Ties: prints the first such word. Empty input → empty line `
`. |
| 1100 | shortest_word | Reads a `
`-terminated line ≤ 80 chars. Prints the shortest whitespace-separated token + `
`. Ties: prints the first such word. Empty input → empty line `
`. |
| 1101 | word_with_most_vowels | Reads a `
`-terminated line ≤ 80 chars. Prints the word with the most vowels (`aeiouAEIOU`) + `
`. Ties: first such word. Empty input → empty line `
`. |
| 1102 | count_word_occurrences | Reads a `
`-terminated target word (no whitespace), then a `
`-terminated line ≤ 80 chars. Prints the count of whitespace-separated tokens in the line that exactly equal the target (case-sensitive) + `
`. |
| 1103 | reverse_words_in_line | Reads a `
`-terminated line ≤ 80 chars. Splits on whitespace (single-space separator), prints the words in reverse order separated by single spaces, then `
`. Example: `hello world foo` → `foo world hello
`. |
| 1104 | count_unique_words | Reads a `
`-terminated line ≤ 80 chars. Splits on whitespace (case-sensitive, runs collapse). Prints the count of distinct words as decimal + `
`. |
| 1105 | longest_common_prefix_two | Reads two `
`-terminated lines (each ≤ 40 chars). Prints the longest common prefix + `
`. If no common prefix, prints just `
`. |
| 1106 | longest_common_suffix_two | Reads two `
`-terminated lines (each ≤ 40 chars). Prints the longest common suffix (compared between the lines' contents, excluding their `
`s) + `
`. If none, prints just `
`. |
| 1107 | line_starts_with_substring | Reads a `
`-terminated prefix (≤ 20 chars), then a `
`-terminated line (≤ 60 chars). Prints `1
` if the line starts with the prefix exactly, else `0
`. |
| 1108 | line_ends_with_substring | Reads a `
`-terminated suffix (≤ 20 chars), then a `
`-terminated line (≤ 60 chars). Prints `1
` if the line's content (excluding `
`) ends with the suffix exactly, else `0
`. |
| 1109 | count_substring_occurrences | Reads a `
`-terminated pattern (≤ 20 chars), then a `
`-terminated text (≤ 60 chars). Prints the count of non-overlapping left-to-right occurrences of pattern in text as decimal + `
`. Empty pattern → `0
`. |

## state_machines

| # | name | description |
|---|---|---|

## parsing

| # | name | description |
|---|---|---|
| 1378 | parse_integer_echo | Reads a `
`-terminated unsigned decimal `0`-`999999` and prints it back as decimal + `
`. Round-trip parse → integer → print. |
| 1379 | parse_signed_integer_echo | Reads a `
`-terminated signed decimal `-9999`..`9999` (may have leading `-` or `+`) and prints the canonical signed form + `
` (no leading `+`). |
| 1380 | eval_simple_expr_add | Reads `<a>+<b>` + `
` where `a` and `b` are single digits `0`-`9`. Prints `a + b` as decimal + `
`. |
| 1381 | eval_simple_expr_sub | Reads `<a>-<b>` + `
` (single digits). Prints `a - b` (signed) + `
`. |
| 1382 | eval_simple_expr_mul | Reads `<a>*<b>` + `
` (single digits). Prints `a * b` + `
`. |
| 1383 | eval_two_op_expr | Reads `<a><op><b>` + `
` where `op` is one of `+`, `-`, `*` and `a`, `b` are single digits. Prints the result + `
`. |
| 1384 | eval_three_op_lr | Reads `<a><op1><b><op2><c>` + `
` (single digits, `op` ∈ `+`/`-`/`*`). Evaluates strictly left-to-right (no precedence) and prints the result + `
`. |
| 1385 | eval_three_op_precedence | Reads `<a><op1><b><op2><c>` + `
` (single digits, `op` ∈ `+`/`-`/`*`). Applies standard precedence (`*` before `+`/`-`) and prints the result + `
`. |
| 1386 | tokenize_split_on_whitespace | Reads a `
`-terminated line ≤ 40 chars. Splits on runs of whitespace (`' '`, `'\t'`) and prints each non-empty token on its own line. |
| 1387 | tokenize_split_on_char | Reads exactly one separator byte + `
`, then a `
`-terminated line ≤ 40 chars. Splits the line on the separator byte and prints each token (including empty) on its own line. |
| 1388 | parse_hex_color | Reads `#RRGGBB
` (exactly 7 bytes + `
`, lowercase hex). Prints `R: <r>
G: <g>
B: <b>
` where `r`, `g`, `b` are decimal values `0`-`255`. |
| 1389 | parse_date_iso | Reads `YYYY-MM-DD
` (10 bytes + `
`). Prints `Year: <Y>
Month: <M>
Day: <D>
` with no leading zeros. |
| 1390 | parse_time_hhmm | Reads `HH:MM
` (5 bytes + `
`). Prints `<H>:<M>
` with no leading zeros (e.g. `09:05` → `9:5
`). |
| 1391 | parse_phone_simple | Reads `XXX-XXX-XXXX
` (12 bytes + `
`, dashes at positions 3 and 7). Prints the 10 digits concatenated (no dashes) + `
`. |
| 1392 | parse_url_protocol | Reads `<proto>://<rest>
` (proto is `1`-`8` lowercase letters). Prints the protocol + `
`. |
| 1393 | parse_email_at | Reads `<user>@<domain>
` (≤ 30 chars total, exactly one `@`). Prints `<user>
<domain>
`. |
| 1394 | parse_yaml_kv_simple | Reads `<key>: <value>
` (single colon-space separator; key is letters only, value any byte). Prints `<key>
<value>
`. |
| 1395 | parse_json_int | Reads `{"x":<num>}
` where `<num>` is a decimal `0`-`9999`. Prints `<num>` + `
`. |
| 1396 | parse_json_string | Reads `{"s":"<str>"}
` where `<str>` is any ASCII bytes (no escapes, no embedded `"`). Prints `<str>` + `
`. |
| 1397 | parse_json_bool | Reads `{"b":true}
` or `{"b":false}
`. Prints `1
` for `true`, `0
` for `false`. |
| 1398 | parse_decimal_list_sum | Reads a `
`-terminated comma-separated list of decimals (each `0`-`99`, up to 10 entries). Prints the sum + `
`. |
| 1399 | parse_decimal_list_max | Reads same format as `parse_decimal_list_sum`. Prints the maximum + `
`. |
| 1400 | parse_dimensions | Reads `WxH
` where `W` and `H` are decimals `0`-`99`. Prints `W * H` + `
`. |
| 1401 | parse_version_string | Reads `v<MAJOR>.<MINOR>.<PATCH>
` where each segment is `0`-`99`. Prints `<MAJOR> <MINOR> <PATCH>
` space-separated. |
| 1402 | parse_rgb_to_grayscale | Reads `R,G,B
` (each `0`-`255`, decimals separated by commas). Prints `floor((R*30 + G*59 + B*11) / 100)` as decimal + `
`. |
| 1403 | parse_simple_assignment | Reads `<var>=<value>
` where `var` is a single lowercase letter and `value` is a decimal `0`-`999`. Prints `<var> is <value>
`. |
| 1404 | parse_currency_dollars_cents | Reads `$<D>.<CC>
` where `D` is decimal `0`-`99` (no zero pad) and `CC` is exactly 2 decimal digits. Prints `D * 100 + CC` (total cents) + `
`. |
| 1405 | parse_signed_hex | Reads `[+-]?0x<HH>
` (optional sign byte then `0x` then exactly 2 lowercase hex chars). Prints the signed decimal value `-255`..`255` + `
`. |
| 1406 | parse_unit_value | Reads `<num><unit>
` where `num` is decimal `0`-`99` and `unit` is exactly one byte `s` (seconds), `m` (minutes), or `h` (hours). Prints `num` converted to seconds as decimal + `
`. |

## graphics_ascii

| # | name | description |
|---|---|---|
| 1278 | print_house_3 | No input. Prints a fixed 3-line ASCII house: line 1 ` /\ `, line 2 `/__\`, line 3 `|  |`, each + `
`. |
| 1279 | print_house_5 | No input. Prints a fixed 5-line ASCII house (taller and wider than `print_house_3`): line 1 `  /\  `, line 2 ` /  \ `, line 3 `/____\`, line 4 `|    |`, line 5 `|____|`, each + `
`. |
| 1280 | print_christmas_tree_5 | No input. Prints a fixed 5-row centered Christmas tree of `*` (rows of width 1,3,5,7,9 centered in a 9-col field with leading spaces). |
| 1281 | print_christmas_tree_7 | No input. Same shape as `print_christmas_tree_5` but with 7 rows (widths 1,3,5,7,9,11,13 in a 13-col field). |
| 1282 | print_star_5_point | No input. Prints a fixed 5-row 5-pointed star ASCII art (centered on 9-col field, using `*` and spaces). |
| 1283 | print_arrow_right_short | No input. Prints `--->
`. |
| 1284 | print_arrow_up_3 | No input. Prints a fixed 3-line upward arrow (`/\`, `||`, `||`), each + `
`. |
| 1285 | print_arrow_down_3 | No input. Prints a fixed 3-line downward arrow (`||`, `||`, `\/`), each + `
`. |
| 1286 | print_smiley_face_static | No input. Prints `:)
`. (Distinct from `emoji_smiley_or_frown` which reads input first.) |
| 1287 | print_heart_3 | No input. Prints a 3-row ASCII heart shape using `*`, e.g. line 1 ` * *`, line 2 `*****`, line 3 ` *** `, each + `
`. |
| 1288 | print_filled_diamond_5 | No input. Prints a 5-row filled diamond of `*` centered in a 5-col field: rows ` * `, `***`, `*****` (truncated to 5-col), `***`, ` * ` — actually use rows widths 1,3,5,3,1 centered on width-5 grid with leading spaces. |
| 1289 | print_filled_diamond_7 | No input. Same shape as `print_filled_diamond_5` but 7-row (widths 1,3,5,7,5,3,1 on 7-col grid). |
| 1290 | print_diamond_outline_5 | No input. Prints a 5-row outline-only diamond: rows ` * `, `* *`, ` * ` for top half mirrored... wait the precise pattern: row 1 `  *  `, row 2 ` * * `, row 3 `*   *`, row 4 ` * * `, row 5 `  *  ` (5×5 grid, only outline cells are `*`, others are space). |
| 1291 | print_box_with_text | Reads a `
`-terminated line ≤ 10 chars. Prints a 3-row box around the text: top row `+<dashes>+
`, middle row `| <text padded to 10 chars> |
`, bottom row `+<dashes>+
`. Box width is fixed (text padded with trailing spaces to 10 chars, total width 14). |
| 1292 | print_table_2x3 | No input. Prints a fixed 2-row × 3-column ASCII table with `+`, `-`, `|` separators and fixed contents (`Name` / `Age` / `City` headers + one data row `Alice` / `30` / `Paris`). |
| 1293 | print_chess_pawn | No input. Prints a multi-line ASCII chess pawn (3 lines, e.g. ` ○ 
 /_\\
 |_|`). |
| 1294 | print_chess_king | No input. Prints a multi-line ASCII chess king (4 lines, with `+`, `|`, `_`). |
| 1295 | print_chess_queen | No input. Prints a multi-line ASCII chess queen (4 lines, distinct shape from king). |
| 1296 | print_chess_bishop | No input. Prints a multi-line ASCII chess bishop (4 lines). |
| 1297 | print_chess_knight | No input. Prints a multi-line ASCII chess knight (4 lines, e.g. with `/\\`). |
| 1298 | print_chess_rook | No input. Prints a multi-line ASCII chess rook (4 lines, like a tower). |
| 1299 | print_dollar_sign_5x5 | No input. Prints a fixed 5×5 ASCII `$` sign using `*` and spaces. |
| 1300 | print_circle_radius_3 | No input. Prints a rasterized circle of radius 3 centered on a 7×7 grid: each cell is `*` if `i² + j² <= 9` (with `i, j` from `-3` to `3`), else `.`. |
| 1301 | print_circle_radius_4 | No input. Same construction as `print_circle_radius_3` but radius 4 on a 9×9 grid. |
| 1302 | print_sin_wave_one_period | No input. Prints a 5-row × 20-column ASCII approximation of one full sine wave period using `*` for plot points and `.` for empty. Use the formula `y = round(2 * sin(2π * x / 20)) + 2` for `x = 0..19` and plot `*` at `(y, x)`. |
| 1303 | print_bar_chart_v_3 | Reads 3 decimals each `0`-`5` (own line). Prints a 5-row × 3-col vertical bar chart: for each column `i`, `*` for rows ≥ `5 - input_i`, `.` otherwise. |
| 1304 | print_bar_chart_v_5 | Reads 5 decimals each `0`-`5` (own line). Same construction as `print_bar_chart_v_3` but 5 columns. |
| 1305 | print_bar_chart_h_3 | Reads 3 decimals each `0`-`9` (own line). Prints 3 rows: row `i` is `input_i` consecutive `*`s + `
`. |
| 1306 | print_bar_chart_h_5 | Reads 5 decimals each `0`-`9` (own line). Same as `print_bar_chart_h_3` with 5 rows. |
| 1307 | print_arrow_with_label | Reads a `
`-terminated line ≤ 20 chars. Prints `--> <line>
`. |
| 1308 | print_thermometer_5 | Reads decimal `0`-`5` + `
`. Prints a 5-row vertical thermometer: row `i` (counted from top) is `|` if `i >= 5 - input`, else ` `; then `
` after each row. |

## language_demos

| # | name | description |
|---|---|---|
| 1237 | demo_hex_add | Reads two lowercase hex chars (each on own line). Uses `hex.add`. Prints the result hex + `
` (mod 16, carry discarded). |
| 1238 | demo_hex_sub | Same I/O as `demo_hex_add` but uses `hex.sub`. |
| 1239 | demo_hex_xor | Same I/O but uses `hex.xor`. |
| 1240 | demo_hex_and | Same I/O but uses `hex.and`. |
| 1241 | demo_hex_or | Same I/O but uses `hex.or`. |
| 1242 | demo_hex_not | Reads one lowercase hex char + `
`. Uses `hex.not` (XOR with `f`). Prints result hex + `
`. |
| 1243 | demo_hex_inc | Reads one hex char + `
`. Uses `hex.inc`. Prints result hex + `
` (`f` wraps to `0`). |
| 1244 | demo_hex_dec | Same as `demo_hex_inc` but uses `hex.dec` (`0` wraps to `f`). |
| 1245 | demo_hex_cmp | Reads two hex chars (each own line). Uses `hex.cmp`. Prints `<`, `=`, or `>` + `
`. |
| 1246 | demo_hex_shl | Reads one hex char + `
`, then shift count `0`-`3` + `
`. Uses `hex.shl`. Prints result hex + `
`. |
| 1247 | demo_hex_shr | Same as `demo_hex_shl` but uses `hex.shr`. |
| 1248 | demo_hex_mul | Reads two hex chars. Uses `hex.mul`. Prints product as 2 hex chars + `
` (high then low nibble). |
| 1249 | demo_hex_div | Reads two hex chars (dividend then divisor, divisor non-zero). Uses `hex.div`. Prints quotient hex + `
`. |
| 1250 | demo_bit_swap | Reads two single bits `0`/`1` (each on own line). Uses `bit.swap` STL macro to swap them in place. Prints them in swapped order as `<b>
<a>
`. |
| 1251 | demo_bit_inc_4bit | Reads a 4-char `0`/`1` binary string + `
`. Uses `bit.inc` (4-bit). Prints result as 4-char binary + `
` (mod 16). |
| 1252 | demo_bit_dec_4bit | Same as `demo_bit_inc_4bit` but with `bit.dec`. |
| 1253 | demo_bit_mov | Reads a 4-char binary + `
`. Uses `bit.mov` to copy it into another variable, then prints the copy as 4-char binary + `
`. |
| 1254 | demo_bit_cmp_4bit | Reads two 4-char binary strings (each on own line). Uses `bit.cmp`. Prints `<`, `=`, or `>` + `
`. |
| 1255 | demo_bit_shl_4bit | Reads a 4-char binary + `
`, then digit `0`-`3` + `
` (shift count). Uses `bit.shl`. Prints result as 4-char binary + `
`. |
| 1256 | demo_bit_shr_4bit | Same as `demo_bit_shl_4bit` but with `bit.shr`. |
| 1257 | demo_bit_mul10_8bit | Reads an 8-char binary + `
`. Uses `bit.mul10`. Prints the result as decimal + `
` (assume no overflow). |
| 1258 | demo_bit_print_dec_uint | No input. Declares an internal 8-bit value `123`. Uses `bit.print_dec_uint` to print it as `123
`. |
| 1259 | demo_bit_print_hex_uint | No input. Declares an internal 8-bit value `255`. Uses `bit.print_hex_uint` to print it as `ff
`. |
| 1260 | demo_stl_output_string | No input. Uses `stl.output "Hello, FlipJump!
"` to print the string. |
| 1261 | demo_rep_5_stars | No input. Uses `rep(5, i) stl.output('*')` then `stl.output('
')` to print `*****
`. |
| 1262 | demo_rep_10_dashes | No input. Uses `rep(10, i) stl.output('-')` then `
`. Prints `----------
`. |
| 1263 | demo_segment_reserve | Uses `segment` + `reserve` to set up a small memory region of 8 bytes initialized to zero. Reads no input. Prints the first byte's value (which is `0`) + `
`. |
| 1264 | demo_compile_time_expr | No input. Internally uses a compile-time expression `(1 + 2) * (3 + 4)` to produce constant `21`. Uses `bit.print_dec_uint` to print `21
`. |
| 1265 | demo_macro_one_arg | Defines a macro `print_byte(b)` that calls `stl.output(b)`. The top-level invokes `print_byte('A')`. Prints `A
`. |
| 1266 | demo_namespace_usage | Defines `ns mathops { def add_one(x) { bit.inc x } }` and uses `mathops.add_one` on a 4-bit value `0011`. Prints result as 4-char binary + `
`. |
| 1267 | bf_inc_dec | Reads a `
`-terminated string ≤ 30 chars containing `+` and `-` (other bytes ignored). Interprets on a single cell (initially 0, mod 256). Prints final cell value as decimal + `
`. |
| 1268 | bf_inc_dec_print | Reads a `
`-terminated Brainfuck program ≤ 30 chars using only `+`, `-`, `.` (other bytes ignored). Interprets on a single cell (initially 0, mod 256). Each `.` outputs the cell value as one raw byte. Final newline after all output. |
| 1269 | bf_tape_4 | Reads a `
`-terminated BF program ≤ 30 chars using `+`, `-`, `<`, `>`, `.` (other bytes ignored). Interprets on a 4-cell tape (cells initially 0, mod 256). Each `.` outputs the current cell as one raw byte. The tape pointer stays in `[0, 3]` (out-of-bounds moves are silently ignored). Final newline after all output. |
| 1270 | stack_vm_push_add | Reads a `
`-terminated program string of tokens separated by spaces: `PUSH <d>` (push single digit `0`-`9`) and `ADD` (pop two values, push their sum). After interpreting all tokens, prints the final top of stack as decimal + `
`. ≤ 10 tokens total. |
| 1271 | stack_vm_pop_print | Reads a `
`-terminated program: `PUSH <d>` and `POP` (pop top and print as decimal + `
` for each POP). ≤ 10 tokens total. |
| 1272 | accumulator_5_ops | Reads decimal `acc_initial` `0`-`9` + `
`, then 5 `<op><digit>` tokens (each a 2-char ASCII pair like `+3`) separated by spaces on one line + `
`. Applies the 5 ops sequentially to acc. Prints the final acc as decimal + `
`. |
| 1273 | two_register_machine_5 | Reads decimal `R0` `R1` (each `0`-`9`, on own lines). Then 5 instructions on own lines, each one of `ADD0` (`R0 = R0 + R1`), `SUB0` (`R0 = R0 - R1`), `SWAP` (`R0 ↔ R1`), `INC0`, `INC1`. After all 5, prints `<R0> <R1>
`. |
| 1274 | subleq_one_step | Reads three decimals `m_a` `m_b` `pc` (each `0`-`9`, on own lines), then 10 decimals (the SUBLEQ memory cells `mem[0..9]`, each on own line, each `0`-`9`). Executes one SUBLEQ instruction `mem[m_b] = mem[m_b] - mem[m_a]; if mem[m_b] <= 0: pc = ...` (here we ignore the jump target — just the SUBLEQ subtract step). Prints the new value of `mem[m_b]` (signed decimal, may go negative) + `
`. |
| 1275 | unary_increment_tm | Reads a `
`-terminated string of `1`s (length 0-30), interpreted as a unary number. Outputs the same string with one additional `1` appended (representing N+1), followed by `
`. |
| 1276 | unary_addition_tm | Reads a `
`-terminated string of the form `1^a + 1^b` (e.g. `111+11` for 3+2). Outputs `1^(a+b)` + `
` (`11111` for 3+2). |
| 1277 | one_op_demo | No input. Simulates 5 successive applications of the FlipJump primitive `flip bit a; jump b` on a 4-byte memory region, with hardcoded `a, b` pairs. Prints the final memory contents as 8 hex digits + `
` (one nibble per output char, MSB first). |

## cryptography

| # | name | description |
|---|---|---|
| 1407 | caesar_shift_n | Reads a signed decimal shift `-25`..`25` + `
`, then a `
`-terminated line ≤ 80 chars. Shifts each letter by `n` positions within its case (wrapping at `a`/`z`/`A`/`Z`); non-letters unchanged. Prints result + `
`. |
| 1408 | caesar_brute_force | Reads a `
`-terminated ciphertext ≤ 20 chars (letters and spaces only). Prints all 26 possible Caesar-decrypts (shifts `0`-`25`), one per line. |
| 1409 | vigenere_encode_short | Reads a `
`-terminated lowercase key `1`-`8` chars, then a `
`-terminated plaintext ≤ 40 chars. Applies Vigenère: each plaintext letter is shifted by `key[i mod key_length] - 'a'` positions (within its case, non-letters unchanged). Prints ciphertext + `
`. |
| 1410 | vigenere_decode_short | Reads the same input format as `vigenere_encode_short` (key, then ciphertext). Applies the inverse shift (negative direction). Prints plaintext + `
`. |
| 1411 | simple_substitution_encode | Reads a 26-char `
`-terminated lowercase substitution mapping (the letter at position 0 is the substitution for `a`, position 1 for `b`, etc.). Then reads a `
`-terminated plaintext ≤ 40 chars; substitutes each lowercase letter using the mapping (non-letters unchanged). Prints + `
`. |
| 1412 | simple_substitution_decode | Reads the same 26-char mapping then ciphertext. Inverts the mapping (build inverse table) and applies to decode. Prints plaintext + `
`. |
| 1413 | rail_fence_2_rails | Reads a `
`-terminated plaintext ≤ 30 chars (no `
`s inside). Encodes using 2-rail rail-fence cipher (write zigzag on 2 rails, read row-by-row). Prints ciphertext + `
`. |
| 1414 | rail_fence_3_rails | Same I/O as `rail_fence_2_rails` but with 3 rails. |
| 1415 | columnar_transposition_3x3 | Reads a `
`-terminated plaintext of exactly 9 chars. Writes them into a 3×3 grid row-major, then reads out column-by-column. Prints the result + `
`. |
| 1416 | binary_complement_cipher | Reads a `
`-terminated line ≤ 30 chars. For each byte (excluding `
`), outputs the bitwise complement `~byte` as a raw byte. Final `
`. |
| 1417 | ascii_offset_encode_n | Reads a signed decimal shift `-128`..`127` + `
`, then a `
`-terminated line ≤ 30 chars. For each input byte, outputs `(byte + n) mod 256` as a raw byte. Final `
`. |
| 1418 | fermat_test_witness | Reads three decimals `a`, `n` (each `2`-`30`, own line). Prints `1
` if `a^(n-1) ≡ 1 (mod n)`, else `0
`. (Fermat's little theorem witness; passing doesn't guarantee primality.) |
| 1419 | simple_hash_sum_4bit | Reads a `
`-terminated line ≤ 30 chars. Computes the sum of all byte values (excluding `
`) modulo 16. Prints the result as a single lowercase hex char + `
`. |
| 1420 | one_time_pad_xor | Reads a `
`-terminated pad of `1`-`30` bytes, then a `
`-terminated message of EXACTLY the same length. XORs corresponding bytes; outputs the result as raw bytes + `
`. (Self-inverse — applying twice with the same pad returns the original.) |
| 1421 | polybius_square_encode | Reads exactly one uppercase letter `A`-`Z` (excluding `J`; `I` and `J` are merged) + `
`. Prints two decimal digits `<row><col>` (each `1`-`5`) + `
` based on the standard 5×5 Polybius square (row-major fill of `A B C D E F G H I/J K L M N O P Q R S T U V W X Y Z`). |
| 1422 | polybius_square_decode | Reads two decimal digits + `
` (e.g. `42`). Prints the corresponding uppercase letter from the standard 5×5 Polybius square + `
`. |
| 1423 | caesar_validate | Reads a signed decimal shift `-25`..`25` + `
`, then plaintext + `
`, then candidate ciphertext + `
` (each ≤ 20 chars). Prints `1
` if applying Caesar shift to plaintext yields the candidate ciphertext exactly, else `0
`. |
| 1424 | encrypt_then_reverse | Reads a `
`-terminated plaintext ≤ 20 chars. Applies Caesar shift of `+3` (ROT3) then reverses the result. Prints the final string + `
`. |
| 1425 | xor_with_position | Reads a `
`-terminated line ≤ 30 chars. For each byte at 0-based position `i`, outputs `byte XOR i` as a raw byte. Final `
`. |
| 1426 | shift_letter_by_position | Reads a `
`-terminated line ≤ 20 chars. For each letter at 0-based position `i`, shifts it by `i` positions within its case (non-letters unchanged). Prints result + `
`. |
| 1427 | encrypt_then_uppercase | Reads a `
`-terminated plaintext ≤ 20 chars. Applies Caesar shift of `+5`, then uppercases all letters. Prints + `
`. |
| 1428 | count_distinct_letters_ciphertext | Reads a `
`-terminated line ≤ 80 chars. Prints the count of distinct LETTER bytes (case-insensitive; `A` and `a` count as one) as decimal + `
`. |
| 1429 | modular_arith_demo | Reads three decimals `a`, `b`, `m` (each `0`-`50`, own line; `m >= 1`). Prints `(a+b) mod m
(a*b) mod m
` on two lines. |
| 1430 | djb2_hash_short | Reads a `
`-terminated line ≤ 30 chars. Computes the djb2 hash modulo 256: `h = 5381; for each byte b: h = ((h * 33) + b) mod 256`. Prints `h` as 2 lowercase hex chars + `
`. |
| 1431 | fnv1a_hash_short | Reads a `
`-terminated line ≤ 30 chars. Computes FNV-1a hash modulo 256: `h = 0; for each byte b: h = ((h XOR b) * 0x93) mod 256` (`0x93` = FNV prime `16777619 mod 256`). Prints `h` as 2 lowercase hex chars + `
`. (Distinct from `fnv1_hash_short` by operation order — XOR then multiply vs multiply then XOR.) |
| 1432 | polynomial_hash_mod_256 | Reads a `
`-terminated line ≤ 30 chars. Computes `sum(byte[i] * 31^i) mod 256` for `i = 0..n-1`. Prints `h` as 2 lowercase hex chars + `
`. |
| 1433 | crc8_simple | Reads a `
`-terminated line ≤ 30 chars. Computes CRC-8 using polynomial `0x07` starting with `crc = 0`. Prints CRC as 2 lowercase hex chars + `
`. |
| 1434 | pearson_hash_byte | Reads a `
`-terminated line ≤ 30 chars. Applies Pearson's 8-bit hash using a fixed 256-byte permutation table (defined in code). Prints hash as 2 lowercase hex chars + `
`. |
| 1435 | adler_lite_hash | Reads a `
`-terminated line ≤ 30 chars. Computes an Adler-32-style hash with small modulus: `a = 1; b = 0; for each byte: a = (a + byte) mod 251; b = (b + a) mod 251;` then prints `b * 256 + a` as 4 lowercase hex chars + `
`. |
| 1436 | rolling_hash_step | Reads decimal state `0`-`255` + `
`, then one byte. Updates state via `state = ((state * 31) + byte) mod 256` and prints the new state as 2 lowercase hex chars + `
`. |
| 1437 | djb2_compare_two | Reads two `
`-terminated lines (each ≤ 20 chars). Computes djb2 hash mod 256 of each. Prints `1
` if the hashes match, else `0
`. |
| 1438 | murmur_lite_4byte | Reads exactly 4 raw bytes. Computes a tiny Murmur-style hash: `h = 0x12345678; for each byte b: h = ((h XOR b) * 0x05) mod 256`. Prints `h` as 2 lowercase hex chars + `
`. |
| 1439 | fnv1_hash_short | Reads a `
`-terminated line ≤ 30 chars. Computes FNV-1 mod 256 with explicit multiplier `0x93` (FNV prime mod 256): `h = 0; for each byte b: h = ((h * 0x93) mod 256) XOR b`. Prints hash as 2 lowercase hex chars + `
`. (Distinct from `fnv1a_hash_short` by operation order — multiply then XOR vs XOR then multiply.) |
| 1440 | polynomial_hash_prime_251 | Reads a `
`-terminated line ≤ 30 chars. Same algorithm as `polynomial_hash_mod_256` but with modulus 251 instead of 256. Prints hash as decimal `0`-`250` + `
`. |
| 1441 | hash_to_bucket_10 | Reads a `
`-terminated line ≤ 20 chars. Computes djb2 hash, then takes `hash mod 10`. Prints the bucket index `0`-`9` as one decimal digit + `
`. |
| 1442 | hash_match_target | Reads exactly 2 hex chars + `
` (target hash), then a `
`-terminated line ≤ 20 chars. Prints `1
` if `djb2_hash_short(line) == target`, else `0
`. |
| 1443 | djb2_first_n_chars | Reads digit N `1`-`9` + `
`, then a `
`-terminated line ≥ N chars. Computes djb2 hash mod 256 of only the first N bytes of the line. Prints hash as 2 lowercase hex chars + `
`. |

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
| 0847 | day_of_week_from_date | Reads year `1900`-`2099`, month `1`-`12`, day `1`-`31` (each on own line). Computes day-of-week via Zeller's congruence. Prints `0`-`6` + `
` (Sunday=0). |
| 0848 | days_in_month | Reads year `1900`-`2099` then month `1`-`12` (each own line). Prints number of days `28`-`31` + `
` (accounts for leap year). |
| 0849 | days_in_year | Reads year `1900`-`2099` + `
`. Prints `366
` if leap year, else `365
`. |
| 0850 | is_valid_date | Reads year `1900`-`2099`, month, day (each own line). Prints `1
` if all three form a valid Gregorian date (month `1`-`12`, day within month accounting for leap), else `0
`. |
| 0852 | format_date_iso | Reads year `1900`-`2099`, month `1`-`12`, day `1`-`31` (each own line). Prints `YYYY-MM-DD
` with zero padding for MM and DD. |
| 0853 | parse_date_iso_validate | Reads `YYYY-MM-DD
` (10 chars + `
`). Prints `1
` if it parses as a valid date in `1900`-`2099`, else `0
`. |
| 0854 | format_time_12_hour | Reads 24-hour time as `HH:MM
` (HH `00`-`23`, MM `00`-`59`). Prints `<H>:<MM> AM
` or `<H>:<MM> PM
` (12-hour format; midnight is `12:00 AM`, noon is `12:00 PM`; H is 1-12, no zero padding; MM stays zero-padded). |
| 0855 | format_time_24_hour | Reads 12-hour time as `<H>:<MM> AM
` or `<H>:<MM> PM
` (H `1`-`12`, MM `00`-`59`). Prints 24-hour format `HH:MM
` with both fields zero-padded. |
| 0856 | seconds_to_clock_hms | Reads decimal total seconds `0`-`86399` + `
`. Prints `HH:MM:SS
` (all three fields zero-padded to 2 digits). |
| 0857 | clock_hms_to_seconds | Reads `HH:MM:SS
` (8 chars + `
`, each field zero-padded to 2 digits). Prints total seconds as decimal `0`-`86399` + `
`. |
| 0858 | short_name_to_month | Reads a 3-char month abbreviation (`Jan`-`Dec`) + `
`. Prints decimal `1`-`12` + `
`. |
| 0859 | day_of_year | Reads year `1900`-`2099`, month, day (each own line). Prints day-of-year `1`-`366` + `
` (accounts for leap). |
| 0860 | date_from_day_of_year | Reads year `1900`-`2099` + `
`, then day-of-year `1`-`366` + `
`. Prints `<month> <day>
` (no zero padding) for the date. |
| 0862 | weekend_check | Reads year, month, day (each own line). Prints `1
` if the date falls on Saturday or Sunday (computed via Zeller's), else `0
`. |
| 0863 | business_days_in_month | Reads year `1900`-`2099`, month `1`-`12` (each own line). Prints count of Mon-Fri days in that month as decimal + `
`. |
| 0864 | quarter_of_year | Reads month `1`-`12` + `
`. Prints quarter `1`-`4` + `
` (Jan-Mar=1, Apr-Jun=2, Jul-Sep=3, Oct-Dec=4). |
| 0865 | days_since_epoch_2000 | Reads year `2000`-`2099`, month, day (each own line). Prints days since `2000-01-01` (which is day 0) as decimal + `
`. |
| 0866 | epoch_to_date_2000 | Reads decimal days since `2000-01-01` (`0`-`36524`, own line). Prints `<year> <month> <day>
` for the corresponding Gregorian date. |
| 0867 | time_of_day_period | Reads decimal hour `0`-`23` + `
`. Prints `morning
` (5-11), `afternoon
` (12-16), `evening
` (17-20), or `night
` (21-4). |
| 0868 | days_to_next_weekday | Reads day-of-week `0`-`6` (Sun=0) + `
`, then target day-of-week `0`-`6` + `
`. Prints `(target - today + 7) mod 7` as decimal `0`-`6` + `
` (the number of days from today to the next occurrence of target; `0` if target equals today). |
| 1075 | dec_year_2digit_to_4digit | Reads 2-digit decimal `00`-`99` + `
`. Interprets via "pivot 50" rule: `50`-`99` → `1950`-`1999`, `00`-`49` → `2000`-`2049`. Prints 4-digit year + `
`. |
| 1076 | days_between_dates_same_year | Reads year, month1, day1, month2, day2 (each own line). Both dates in the same year; date2 ≥ date1. Prints absolute day difference as decimal + `
`. |

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
| 1077 | random_choice_pick_3 | Reads 3 `
`-terminated lines (each ≤ 20 chars) then one byte. Prints one of the 3 lines based on `byte mod 3`, followed by `
`. |
| 1078 | word_acronym_check | Reads two `
`-terminated lines: first an acronym (uppercase, ≤ 6 chars), second a sentence (≤ 40 chars). Prints `1
` if the acronym matches the uppercased first letter of each whitespace-separated word in the sentence (in order), else `0
`. |
| 1079 | is_valid_username | Reads `
`-terminated string ≤ 20 chars. Prints `1
` if its length is `3`-`12` and every byte is alphanumeric (`A`-`Z`/`a`-`z`/`0`-`9`), else `0
`. |
| 1080 | count_emoji_pairs | Reads `
`-terminated line ≤ 40 chars. Prints `<smileys> <frowns>
` where smileys is the count of `:)` and frowns is the count of `:(` substrings (non-overlapping, scanning left-to-right). |
| 1081 | is_pangram | Reads `
`-terminated line ≤ 80 chars. Prints `1
` if the line contains every letter `a`-`z` at least once (case-insensitive), else `0
`. |
| 1082 | is_cli_flag | Reads `
`-terminated string ≤ 20 chars. Prints `1
` if it starts with `-` (single-dash flag) OR `--` (long flag), else `0
`. |
| 1083 | count_non_alphanumeric | Reads `
`-terminated line ≤ 80 chars. Prints the count of bytes that are NEITHER letters NOR digits (excluding terminating `
`) as decimal + `
`. |
| 1084 | dollar_amount_to_words | Reads decimal `0`-`99` + `
`. Prints the English-words form `<tens_word> <ones_word>
` (e.g. `42` → `forty two
`; `7` → `seven
`; `10` → `ten
`; `20` → `twenty
`). |
| 1085 | letter_position_word | Reads `
`-terminated string ≤ 10 chars (letters only). Prints the 0-based alphabetic position of each letter (as decimal), space-separated, followed by `
`. Example: `abc
` → `0 1 2
`. |
| 1086 | greet_three_times | Reads `
`-terminated name (≤ 15 chars). Prints `Hello, <name>!
` three times (3 lines of output). |
| 1087 | print_progress_bar_10 | Reads digit `0`-`10` + `
`. Prints a 10-char progress bar: `<percent>` `#` characters followed by `(10 - percent)` `.` characters, then `
`. (e.g. `3` → `###.......
`.) |
| 1088 | bits_to_emoji_face | Reads two bits `e1 e2` (eye states, each `0` closed or `1` open, own line), then one bit `m` (mouth state, `0` frown / `1` smile, own line). Prints a 3-char emoji face combining these: e.g. `1 1 1` → `:)
`; `0 0 1` → `XD
`; `1 1 0` → `:(
`; `0 0 0` → `XO
`. |
| 1089 | midi_to_octave | Reads decimal `0`-`127` + `
`. Prints the octave number (signed: MIDI 0 → `-1`, MIDI 12 → `0`, MIDI 60 → `4`, MIDI 127 → `9`) + `
`. |

## Exceptional / fj.tomhe.app Examples candidates

Programs in this section are picks that are especially instructive or
beautiful, worth highlighting on the fj.tomhe.app Examples page. Populated
incrementally during Phase 3 implementation.

| # | name | why it's worth showcasing |
|---|---|---|

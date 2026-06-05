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

## recursion

| # | name | description |
|---|---|---|

## interactive

| # | name | description |
|---|---|---|

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

## algorithms

| # | name | description |
|---|---|---|

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

## Exceptional / fj.tomhe.app Examples candidates

Programs in this section are picks that are especially instructive or
beautiful, worth highlighting on the fj.tomhe.app Examples page. Populated
incrementally during Phase 3 implementation.

| # | name | why it's worth showcasing |
|---|---|---|

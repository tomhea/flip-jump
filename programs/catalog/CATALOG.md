# Catalog — Master Spec List

This file is the internal master list of catalog programs. Locked at the end
of Phase 2 (ideation). During Phase 3 it is the contract; rows are only added
when a `RETIRED` row is being replaced, and only at the end.

Number assignment is in (category-order, in-category-order) sequence — see
`CONVENTIONS.md`. Numbers are never recycled.

## Status

- **Phase 1 (Setup)**: complete (M0 merged or pending merge on `catalog/setup`).
- **Phase 2 (Ideation)**: in progress on `catalog/m1-ideation`. Specs are
  proposed in batches of ~100, CR-ist'd, then locked. `#NNNN` numbers are
  assigned only at the end of Phase 2.

Each row's `status` column is one of:
- `PROPOSED` — drafted, awaiting CR
- `APPROVED` — passed the CR-ist; will get a `#NNNN` at lock time
- `REJECT` — CR-ist rejected; row is kept for traceability but won't ship
- `OVERLAP` — CR-ist found it too close to an APPROVED row; not shipping
- `RETIRED` — APPROVED but unimplementable during Phase 3; number kept, replaced at end

## Batch 1 — foundations (101 approved)

Categories: hello (25), io (31), arithmetic (20), bits (15), logic (10).
All 101 rows CR-approved (6 UNCLEAR descriptions tightened in place; 0 reject, 0 overlap).

| status | category | name | description |
|---|---|---|---|
| APPROVED | hello | hello_world | Prints `Hello, World!\n` and exits. |
| APPROVED | hello | hello_user | Reads a single-line name from stdin (terminated by `\n`) and prints `Hello, <name>!\n`. |
| APPROVED | hello | hello_world_3x | Prints `Hello, World!\n` three times consecutively. |
| APPROVED | hello | hello_n_times | Reads a single ASCII digit `0`-`9` from stdin and prints `Hello, World!\n` that many times. |
| APPROVED | hello | hello_lowercase | Prints `hello, world!\n` (all-lowercase variant). |
| APPROVED | hello | hello_uppercase | Prints `HELLO, WORLD!\n` (all-uppercase variant). |
| APPROVED | hello | hello_reversed | Prints `!dlroW ,olleH\n` (the bytes of `Hello, World!\n` minus the newline, reversed, followed by `\n`). |
| APPROVED | hello | hello_one_char_per_line | Prints each character of `Hello, World!` on its own line (13 lines, each one char + `\n`). |
| APPROVED | hello | hello_two_lines | Prints `Hello,\nWorld!\n` — the greeting split into two lines at the comma. |
| APPROVED | hello | hello_box | Prints exactly three lines of 17 chars each + `\n`: line 1 and 3 are 17 `*` characters; line 2 is `* Hello, World! *` (1 star, space, the 13-byte greeting, space, 1 star). |
| APPROVED | hello | hello_no_newline | Prints exactly `Hello, World!` with no trailing newline. |
| APPROVED | hello | hello_tab_sep | Prints `Hello,\tWorld!\n` with a literal tab between `Hello,` and `World!`. |
| APPROVED | hello | hello_question | Prints `Hello, World?\n` (question-mark variant). |
| APPROVED | hello | hello_exclaim_3x | Prints `Hello, World!!!\n` (three trailing exclamation marks). |
| APPROVED | hello | hello_long_user | Reads a single-line name and prints `Welcome to FlipJump, <name>! Have a great day!\n`. |
| APPROVED | hello | hello_hex_codes | Prints the hex code-points of `Hello, World!` separated by spaces: `48 65 6c 6c 6f 2c 20 57 6f 72 6c 64 21\n`. |
| APPROVED | hello | hello_ascii_first_five | Prints the ASCII decimal codes of the first five characters of `Hello` separated by spaces: `72 101 108 108 111\n`. |
| APPROVED | hello | hello_underline | Prints `Hello, World!\n-------------\n` (13 dashes underlining the greeting). |
| APPROVED | hello | hello_two_users | Reads two `\n`-terminated names as two consecutive lines on stdin (same convention as `hello_user`) and prints `Hello, <name1> and <name2>!\n`. |
| APPROVED | hello | hello_anonymous | Prints `Hello, anonymous user!\n` (no input). |
| APPROVED | hello | hello_alpha_world | Prints the lowercase English alphabet followed by space and the greeting: `abcdefghijklmnopqrstuvwxyz Hello, World!\n`. |
| APPROVED | hello | hello_then_length | Prints `Hello, World!\nLength: 13\n`. |
| APPROVED | hello | hello_then_question | Prints `Hello, World!\nWhat's your name?\n` (greeting followed by a question on the next line). |
| APPROVED | hello | hello_iterations | Reads a single ASCII digit `1`-`9` and prints lines `Iteration <i>: Hello, World!\n` for each `i` from 1 to N. |
| APPROVED | hello | hello_world_overunder | Prints `=============\nHello, World!\n=============\n` (greeting sandwiched between two rows of 13 `=`). |
| APPROVED | io | cat | Reads stdin and echoes each byte to stdout, byte-for-byte, until EOF. |
| APPROVED | io | uppercase_filter | Reads stdin and prints each byte uppercased (`a`-`z` → `A`-`Z`; other bytes unchanged). |
| APPROVED | io | lowercase_filter | Reads stdin and prints each byte lowercased (`A`-`Z` → `a`-`z`; other bytes unchanged). |
| APPROVED | io | reverse_line | Reads a single line from stdin (up to `\n`) and prints it reversed followed by `\n`. |
| APPROVED | io | count_bytes | Reads all of stdin, prints the total byte count as a decimal integer followed by `\n`. |
| APPROVED | io | count_lines | Reads all of stdin, prints the number of `\n` bytes seen as decimal + `\n`. |
| APPROVED | io | count_words | Reads all of stdin and prints the number of whitespace-separated tokens as decimal + `\n`. Whitespace = any of `' '`, `'\t'`, `'\n'`; runs of consecutive whitespace count as one separator; leading and trailing whitespace introduce no empty tokens; empty input prints `0\n`. |
| APPROVED | io | echo_twice | Reads each byte of stdin and outputs it twice. |
| APPROVED | io | echo_thrice | Reads each byte of stdin and outputs it three times. |
| APPROVED | io | skip_first_byte | Reads stdin and outputs every byte except the very first one. |
| APPROVED | io | swap_case | Reads stdin and swaps upper/lower for letter bytes; other bytes unchanged. |
| APPROVED | io | strip_newlines | Reads stdin and outputs all bytes except `\n`. |
| APPROVED | io | only_digits | Reads stdin and outputs only `0`-`9` bytes, dropping all others. |
| APPROVED | io | only_letters | Reads stdin and outputs only `A`-`Z` and `a`-`z` bytes. |
| APPROVED | io | only_vowels | Reads stdin and outputs only `a/e/i/o/u/A/E/I/O/U` bytes. |
| APPROVED | io | only_uppercase | Reads stdin and outputs only `A`-`Z` bytes. |
| APPROVED | io | tab_to_space | Reads stdin and replaces each `\t` with a single space; other bytes unchanged. |
| APPROVED | io | space_to_tab | Reads stdin and replaces each space (` `) with `\t`; other bytes unchanged. |
| APPROVED | io | char_to_dec | Reads exactly one byte from stdin and prints its ASCII decimal value as decimal + `\n`. |
| APPROVED | io | dec_to_char | Reads a decimal number `0`-`127` from stdin terminated by `\n` and prints the corresponding ASCII byte. |
| APPROVED | io | char_to_hex | Reads exactly one byte from stdin and prints `0xNN\n` where NN is its two-digit hex code (lowercase). |
| APPROVED | io | hex_to_char | Reads `0xNN\n` from stdin (two lowercase hex digits) and prints the corresponding ASCII byte. |
| APPROVED | io | echo_with_prefix | Reads stdin and prints each input byte preceded by `>`. |
| APPROVED | io | echo_with_suffix | Reads stdin and prints each input byte followed by `!`. |
| APPROVED | io | print_first_line | Reads stdin up to the first `\n` and prints only that line (including the `\n`). |
| OVERLAP | io | print_until_period | OVERLAP with print_first_line (3-agent audit): same read-until-target-byte algorithm; differs only in terminator (`.` vs `\n`). Variant-by-single-character. Dropped. |
| APPROVED | io | double_newlines | Reads stdin and outputs each `\n` byte as two `\n`s; other bytes unchanged. |
| APPROVED | io | strip_spaces | Reads stdin and outputs all bytes except space (` `). |
| APPROVED | io | input_then_thanks | Reads a single-line input and prints `Got it: <line>\nThank you!\n`. |
| APPROVED | io | read_one_print_three | Reads one byte from stdin and prints the literal sequence `<byte><byte><byte>\n`. |
| APPROVED | io | rot_ascii_plus_one | Reads stdin and outputs each byte plus 1, modulo 256 (so `0xFF` wraps to `0x00`). All bytes are transformed uniformly; no special-casing of letters or non-letters. |
| APPROVED | arithmetic | add_two_decimals | Reads two decimal integers (each on its own line) and prints their sum as decimal + `\n`. |
| APPROVED | arithmetic | sub_two_decimals | Reads two decimal integers (each on its own line) and prints `a - b` as a signed decimal + `\n`. |
| APPROVED | arithmetic | mul_single_digits | Reads two single-digit decimals `0`-`9` (each followed by `\n`) and prints `a * b` as decimal + `\n`. |
| APPROVED | arithmetic | div_two_decimals | Reads two decimal integers (each on its own line; second is non-zero) and prints `a / b` as integer-division decimal + `\n`. |
| APPROVED | arithmetic | mod_two_decimals | Reads two decimal integers and prints `a % b` as decimal + `\n`. |
| APPROVED | arithmetic | add_three_decimals | Reads three decimal integers (each own line) and prints their sum + `\n`. |
| APPROVED | arithmetic | abs_decimal | Reads one signed decimal integer and prints its absolute value as decimal + `\n`. |
| APPROVED | arithmetic | negate_decimal | Reads one signed decimal integer and prints its negation as decimal + `\n`. |
| APPROVED | arithmetic | inc_decimal | Reads one decimal integer and prints `a + 1` as decimal + `\n`. |
| APPROVED | arithmetic | dec_decimal | Reads one decimal integer and prints `a - 1` as decimal + `\n`. |
| APPROVED | arithmetic | double_decimal | Reads one decimal integer and prints `a * 2` as decimal + `\n`. |
| APPROVED | arithmetic | halve_decimal | Reads one decimal integer and prints `a / 2` (integer division) as decimal + `\n`. |
| APPROVED | arithmetic | square_small | Reads one decimal integer in `0`-`15` and prints `a * a` as decimal + `\n`. |
| APPROVED | arithmetic | cube_small | Reads one decimal integer in `0`-`5` and prints `a * a * a` as decimal + `\n`. |
| APPROVED | arithmetic | min_two | Reads two decimal integers and prints the smaller as decimal + `\n`. |
| APPROVED | arithmetic | max_two | Reads two decimal integers and prints the larger as decimal + `\n`. |
| APPROVED | arithmetic | sum_to_n | Reads one decimal integer N in `0`-`20` and prints `1+2+...+N` as decimal + `\n`. |
| APPROVED | arithmetic | factorial_small | Reads one decimal integer N in `0`-`6` and prints `N!` as decimal + `\n`. |
| APPROVED | arithmetic | mod_by_4 | Reads one decimal integer and prints `a % 4` as a single digit + `\n`. |
| APPROVED | arithmetic | mod_by_10 | Reads one decimal integer and prints `a % 10` as a single digit + `\n`. |
| APPROVED | bits | popcount_byte | Reads one byte from stdin and prints its 1-bit count as a single decimal digit `0`-`8` + `\n`. |
| APPROVED | bits | parity_byte | Reads one byte and prints `0` if it has an even number of 1-bits, `1` if odd, then `\n`. |
| APPROVED | bits | high_nibble | Reads one byte and prints its high 4 bits as one lowercase hex char + `\n`. |
| APPROVED | bits | low_nibble | Reads one byte and prints its low 4 bits as one lowercase hex char + `\n`. |
| APPROVED | bits | swap_nibbles | Reads one byte and outputs the byte with low and high nibbles swapped. |
| APPROVED | bits | reverse_bits_byte | Reads one byte and outputs the byte with its 8 bits reversed (bit 0 ↔ bit 7, etc.). |
| APPROVED | bits | bit_at_position | Reads one byte, then one ASCII digit `0`-`7` (terminated by `\n`), and prints the bit at that position as `0` or `1` + `\n`. Convention: position `0` is the least-significant bit (LSB); position `7` is the most-significant bit (MSB). |
| APPROVED | bits | set_bit_at_position | Reads one byte then one digit `0`-`7` + `\n` and outputs the byte with that bit set to 1. Convention: position `0` is the LSB; matches `bit_at_position`. |
| APPROVED | bits | clear_bit_at_position | Reads one byte then one digit `0`-`7` + `\n` and outputs the byte with that bit cleared to 0. Convention: position `0` is the LSB; matches `bit_at_position`. |
| APPROVED | bits | xor_two_bytes | Reads exactly two bytes and outputs their bitwise XOR as one byte. |
| APPROVED | bits | and_two_bytes | Reads exactly two bytes and outputs their bitwise AND as one byte. |
| APPROVED | bits | or_two_bytes | Reads exactly two bytes and outputs their bitwise OR as one byte. |
| APPROVED | bits | shift_left_one | Reads one byte and outputs `byte << 1` (low bit becomes 0; high bit is lost). |
| APPROVED | bits | shift_right_one | Reads one byte and outputs `byte >> 1` (high bit becomes 0; low bit is lost). |
| APPROVED | bits | is_power_of_two | Reads one byte and prints `1\n` if it has exactly one 1-bit (and is nonzero), else `0\n`. |
| APPROVED | logic | and_gate | Reads two ASCII bits (each is `0` or `1`, separated by `\n`) and prints their AND as `0` or `1` + `\n`. |
| APPROVED | logic | or_gate | Reads two ASCII bits and prints their OR + `\n`. |
| APPROVED | logic | xor_gate | Reads two ASCII bits and prints their XOR + `\n`. |
| APPROVED | logic | nand_gate | Reads two ASCII bits and prints their NAND + `\n`. |
| APPROVED | logic | nor_gate | Reads two ASCII bits and prints their NOR + `\n`. |
| APPROVED | logic | xnor_gate | Reads two ASCII bits and prints their XNOR + `\n`. |
| APPROVED | logic | not_gate | Reads one ASCII bit and prints its negation + `\n`. |
| APPROVED | logic | and_3 | Reads three ASCII bits (each followed by `\n`) and prints their three-way AND + `\n`. |
| APPROVED | logic | or_3 | Reads three ASCII bits and prints their three-way OR + `\n`. |
| APPROVED | logic | half_adder | Reads two ASCII bits and prints the sum bit then the carry bit, both separated by `\n` (two lines). |

## Batch 2 — more arithmetic + number theory + strings (96 approved + 4 overlap)

Categories: arithmetic (39 net, 40 proposed), number_theory (29 net, 30 proposed), strings (29 net, 30 proposed).
CR-ist found 4 overlaps with batch 1 or within batch 2 (marked below); the other 96 are APPROVED.

| status | category | name | description |
|---|---|---|---|
| OVERLAP | arithmetic | add_four_decimals | OVERLAP with add_three_decimals + sum_of_n_inputs (2-agent audit): third bound-variant of add_N_decimals exceeds the 2-bound precedent. Dropped. |
| APPROVED | arithmetic | avg_two | Reads two decimal integers and prints their integer average `(a + b) / 2` (floor division) as decimal + `\n`. |
| APPROVED | arithmetic | avg_three | Reads three decimal integers and prints their integer average `(a + b + c) / 3` (floor division) as decimal + `\n`. |
| APPROVED | arithmetic | compare_two | Reads two decimal integers and prints `<` if `a < b`, `=` if `a == b`, `>` if `a > b`, followed by `\n`. |
| APPROVED | arithmetic | sign_of | Reads one signed decimal integer and prints `-` if negative, `0` if zero, `+` if positive, followed by `\n`. |
| APPROVED | arithmetic | is_zero | Reads one decimal integer and prints `1\n` if it equals zero, else `0\n`. |
| APPROVED | arithmetic | is_positive | Reads one signed decimal integer and prints `1\n` if `> 0`, else `0\n`. |
| APPROVED | arithmetic | is_negative | Reads one signed decimal integer and prints `1\n` if `< 0`, else `0\n`. |
| APPROVED | arithmetic | add_with_expression | Reads two decimal integers and prints the human-readable expression `<a> + <b> = <sum>\n`. |
| APPROVED | arithmetic | mul_by_3 | Reads one decimal in `0`-`30` and prints `a * 3` as decimal + `\n`. |
| APPROVED | arithmetic | mul_by_5 | Reads one decimal in `0`-`20` and prints `a * 5` as decimal + `\n`. |
| APPROVED | arithmetic | mul_by_7 | Reads one decimal in `0`-`14` and prints `a * 7` as decimal + `\n`. |
| APPROVED | arithmetic | mul_by_10 | Reads one decimal in `0`-`100` and prints `a * 10` as decimal + `\n`. |
| APPROVED | arithmetic | div_by_3_quot_rem | Reads one decimal and prints `<quotient> <remainder>\n` for division by 3 (single line, space-separated). |
| APPROVED | arithmetic | complement_to_100 | Reads one decimal in `0`-`100` and prints `100 - a` as decimal + `\n`. |
| OVERLAP | arithmetic | sum_of_digits_2digit | OVERLAP with number_theory/digit_sum: same algorithm restricted to 0-99 (a strict subset of digit_sum's 0-999 input). Dropped. |
| APPROVED | arithmetic | is_even | Reads one decimal integer and prints `1\n` if even, else `0\n`. |
| APPROVED | arithmetic | is_odd | Reads one decimal integer and prints `1\n` if odd, else `0\n`. |
| APPROVED | arithmetic | count_up_to_n | Reads decimal N in `0`-`9` and prints `1\n2\n...\nN\n` (one per line). For N=0 prints nothing. |
| APPROVED | arithmetic | count_down_from_n | Reads decimal N in `0`-`9` and prints `N\n(N-1)\n...\n1\n`. For N=0 prints nothing. |
| APPROVED | arithmetic | evens_up_to_n | Reads decimal N in `0`-`20` and prints even positive integers `2,4,...` up to and including N (if even) or N-1 (if odd), one per line. |
| APPROVED | arithmetic | odds_up_to_n | Reads decimal N in `0`-`19` and prints odd positive integers `1,3,...` up to and including N (if odd) or N-1 (if even), one per line. |
| APPROVED | arithmetic | multiples_of_3_to_n | Reads decimal N in `0`-`30` and prints positive multiples of 3 `3,6,...` ≤ N, one per line. |
| APPROVED | arithmetic | multiples_of_5_to_n | Reads decimal N in `0`-`50` and prints positive multiples of 5 `5,10,...` ≤ N, one per line. |
| APPROVED | arithmetic | swap_pair | Reads two decimals (each on own line) and prints them in reverse order: `<b>\n<a>\n`. |
| APPROVED | arithmetic | median_of_three | Reads three decimal integers and prints the median (middle value when sorted) as decimal + `\n`. |
| APPROVED | arithmetic | max_three | Reads three decimals and prints the maximum + `\n`. |
| APPROVED | arithmetic | min_three | Reads three decimals and prints the minimum + `\n`. |
| APPROVED | arithmetic | range_of_three | Reads three decimals and prints `max - min` + `\n`. |
| APPROVED | arithmetic | sum_of_n_inputs | Reads decimal N (`1`-`9`) on first line, then N decimal integers (each own line), prints their sum + `\n`. |
| APPROVED | arithmetic | max_of_n_inputs | Reads decimal N (`1`-`9`), then N decimal integers, prints the maximum + `\n`. |
| APPROVED | arithmetic | min_of_n_inputs | Reads decimal N (`1`-`9`), then N decimal integers, prints the minimum + `\n`. |
| APPROVED | arithmetic | avg_of_n_inputs | Reads decimal N (`1`-`9`), then N decimal integers, prints their integer average (floor of sum/N) + `\n`. |
| APPROVED | arithmetic | is_in_range | Reads three decimals `a`, `lo`, `hi` (in that order, each own line) and prints `1\n` if `lo <= a <= hi`, else `0\n`. |
| APPROVED | arithmetic | pow_base2 | Reads decimal N in `0`-`7` and prints `2^N` as decimal + `\n`. |
| APPROVED | arithmetic | pow_base3 | Reads decimal N in `0`-`5` and prints `3^N` as decimal + `\n`. |
| OVERLAP | arithmetic | triangle_number_n | OVERLAP with batch1/sum_to_n: triangular number T(N) = 1+2+...+N by definition; same I/O contract. Dropped. |
| APPROVED | arithmetic | clamp_to_max_9 | Reads one decimal in `0`-`99` and prints `min(a, 9)` + `\n` (caps the value at 9). |
| APPROVED | arithmetic | add_then_mod_10 | Reads two decimals and prints `(a + b) % 10` as a single digit + `\n`. |
| APPROVED | arithmetic | abs_diff | Reads two decimals and prints `|a - b|` as decimal + `\n`. |
| APPROVED | number_theory | is_prime_small | Reads decimal N in `0`-`50` and prints `1\n` if N is prime, else `0\n`. |
| APPROVED | number_theory | first_n_primes | Reads decimal N in `1`-`10` and prints the first N prime numbers in ascending order, one per line. |
| APPROVED | number_theory | prime_after | Reads decimal N in `0`-`50` and prints the smallest prime strictly greater than N (guaranteed ≤ 53) + `\n`. |
| APPROVED | number_theory | count_primes_to_n | Reads decimal N in `0`-`50` and prints the count of prime numbers in `[2..N]` as decimal + `\n`. |
| APPROVED | number_theory | gcd_two | Reads two decimals (each ≤ 100) and prints their GCD as decimal + `\n`. |
| APPROVED | number_theory | lcm_two | Reads two decimals each in `1`-`20` and prints their LCM as decimal + `\n`. |
| APPROVED | number_theory | coprime_check | Reads two decimals (each ≤ 100) and prints `1\n` if their GCD is 1, else `0\n`. |
| APPROVED | number_theory | factor_count_small | Reads decimal N in `1`-`50` and prints the number of positive divisors of N as decimal + `\n`. |
| APPROVED | number_theory | divisors_of_n | Reads decimal N in `1`-`30` and prints all positive divisors of N in ascending order, one per line. |
| APPROVED | number_theory | is_perfect_small | Reads decimal N in `1`-`30` and prints `1\n` if N equals the sum of its proper divisors (divisors excluding N), else `0\n`. |
| APPROVED | number_theory | sum_of_divisors_small | Reads decimal N in `1`-`30` and prints the sum of all positive divisors of N (including N) as decimal + `\n`. |
| OVERLAP | number_theory | proper_divisors_sum | OVERLAP with sum_of_divisors_small: differs only in whether N is included; same iteration/accumulation work. Dropped. |
| APPROVED | number_theory | is_abundant_small | Reads decimal N in `1`-`30` and prints `1\n` if N is abundant (sum of proper divisors > N), else `0\n`. |
| APPROVED | number_theory | is_deficient_small | Reads decimal N in `1`-`30` and prints `1\n` if N is deficient (sum of proper divisors < N), else `0\n`. |
| APPROVED | number_theory | fib_n | Reads decimal N in `0`-`12` and prints the N-th Fibonacci number `F(N)` (with `F(0)=0`, `F(1)=1`) + `\n`. |
| APPROVED | number_theory | fib_seq_n | Reads decimal N in `0`-`12` and prints `F(0), F(1), ..., F(N)` one per line. |
| APPROVED | number_theory | is_fib_small | Reads decimal N in `0`-`200` and prints `1\n` if N is a Fibonacci number, else `0\n`. |
| APPROVED | number_theory | lucas_n | Reads decimal N in `0`-`10` and prints the N-th Lucas number (with `L(0)=2`, `L(1)=1`) + `\n`. |
| APPROVED | number_theory | collatz_steps | Reads decimal N in `1`-`50` and prints the number of Collatz steps (3n+1 / n/2) to reach 1 + `\n`. |
| APPROVED | number_theory | collatz_sequence | Reads decimal N in `1`-`15` and prints the Collatz sequence starting at N, terminating with 1, one number per line. |
| APPROVED | number_theory | is_palindrome_num | Reads decimal N in `0`-`999` and prints `1\n` if its base-10 representation is a palindrome, else `0\n`. |
| APPROVED | number_theory | digit_sum | Reads decimal N in `0`-`999` and prints the sum of its base-10 digits as decimal + `\n`. |
| APPROVED | number_theory | digit_product | Reads decimal N in `0`-`999` and prints the product of its base-10 digits as decimal + `\n`. |
| APPROVED | number_theory | digit_count_small | Reads decimal N in `0`-`999` and prints the number of base-10 digits (`1`, `2`, or `3`; `0` itself counts as 1 digit) + `\n`. |
| APPROVED | number_theory | reverse_digits | Reads decimal N in `0`-`999` and prints the decimal with its digits reversed (e.g. `123` → `321`, `100` → `001` becomes `1`). |
| APPROVED | number_theory | is_armstrong_3 | Reads decimal N in `100`-`999` and prints `1\n` if N equals the sum of cubes of its three digits, else `0\n`. |
| APPROVED | number_theory | happy_check_small | Reads decimal N in `1`-`30` and prints `1\n` if N is a happy number (iterated sum of squared digits reaches 1), else `0\n`. |
| APPROVED | number_theory | is_square_small | Reads decimal N in `0`-`100` and prints `1\n` if N is a perfect square, else `0\n`. |
| APPROVED | number_theory | is_cube_small | Reads decimal N in `0`-`64` and prints `1\n` if N is a perfect cube, else `0\n`. |
| APPROVED | strings | string_length | Reads a single `\n`-terminated line of length ≤ 80 and prints the length of the line (excluding the `\n`) as decimal + `\n`. |
| OVERLAP | strings | string_reverse | OVERLAP with batch1/io/reverse_line: same single-line-reverse spec. Dropped. |
| APPROVED | strings | is_palindrome_string | Reads a `\n`-terminated line ≤ 30 chars and prints `1\n` if the line (excluding `\n`) is a palindrome, else `0\n`. |
| APPROVED | strings | count_vowels | Reads a `\n`-terminated line ≤ 80 chars and prints the count of vowel letters (`aeiouAEIOU`) as decimal + `\n`. |
| APPROVED | strings | count_consonants | Reads a `\n`-terminated line ≤ 80 chars and prints the count of letter bytes that are NOT vowels as decimal + `\n`. |
| APPROVED | strings | count_letters | Reads a `\n`-terminated line ≤ 80 chars and prints the count of letter bytes (`A`-`Z` or `a`-`z`) as decimal + `\n`. |
| APPROVED | strings | count_uppercase_letters | Reads a `\n`-terminated line ≤ 80 chars and prints the count of `A`-`Z` bytes as decimal + `\n`. |
| APPROVED | strings | count_lowercase_letters | Reads a `\n`-terminated line ≤ 80 chars and prints the count of `a`-`z` bytes as decimal + `\n`. |
| APPROVED | strings | first_char_of_line | Reads a non-empty `\n`-terminated line and prints just its first byte followed by `\n`. |
| APPROVED | strings | last_char_of_line | Reads a non-empty `\n`-terminated line and prints just its last byte (the one before `\n`) followed by `\n`. |
| APPROVED | strings | repeat_line_2x | Reads a `\n`-terminated line ≤ 40 chars and prints its content twice (concatenated, no internal separator), followed by `\n`. |
| APPROVED | strings | repeat_line_3x | Reads a `\n`-terminated line ≤ 30 chars and prints its content three times concatenated, followed by `\n`. |
| APPROVED | strings | caesar_plus_1 | Reads a `\n`-terminated line ≤ 80 chars and prints the same line with each letter shifted forward by 1 in the alphabet (wraps `z`→`a`, `Z`→`A`); non-letter bytes pass through unchanged; ends with `\n`. |
| APPROVED | strings | caesar_plus_3 | Reads a `\n`-terminated line ≤ 80 chars and prints it with each letter Caesar-shifted by 3 (wraps within case); non-letters unchanged; ends with `\n`. |
| APPROVED | strings | caesar_plus_13 | Reads a `\n`-terminated line ≤ 80 chars and prints the ROT13 transformation: letters shifted by 13 (wraps within case); non-letters unchanged; ends with `\n`. |
| APPROVED | strings | uppercase_line | Reads a `\n`-terminated line ≤ 80 chars, uppercases its `a`-`z` bytes (others unchanged), prints result + `\n`. |
| APPROVED | strings | lowercase_line | Reads a `\n`-terminated line ≤ 80 chars, lowercases its `A`-`Z` bytes (others unchanged), prints result + `\n`. |
| APPROVED | strings | swap_case_line | Reads a `\n`-terminated line ≤ 80 chars and prints it with each letter's case toggled (others unchanged), ending with `\n`. |
| APPROVED | strings | has_char_in_line | Reads exactly one byte, then a `\n`, then a `\n`-terminated line ≤ 80 chars. Prints `1\n` if the line contains the first byte, else `0\n`. |
| APPROVED | strings | starts_with_uppercase | Reads a non-empty `\n`-terminated line and prints `1\n` if its first byte is `A`-`Z`, else `0\n`. |
| APPROVED | strings | ends_with_period | Reads a non-empty `\n`-terminated line and prints `1\n` if the last byte before `\n` is `.`, else `0\n`. |
| APPROVED | strings | is_all_uppercase | Reads a non-empty `\n`-terminated line ≤ 80 chars and prints `1\n` if every byte (excluding the `\n`) is `A`-`Z`, else `0\n`. |
| APPROVED | strings | is_all_lowercase | Reads a non-empty `\n`-terminated line ≤ 80 chars and prints `1\n` if every byte is `a`-`z`, else `0\n`. |
| APPROVED | strings | is_all_digits | Reads a non-empty `\n`-terminated line ≤ 80 chars and prints `1\n` if every byte is `0`-`9`, else `0\n`. |
| APPROVED | strings | is_all_letters | Reads a non-empty `\n`-terminated line ≤ 80 chars and prints `1\n` if every byte is `A`-`Z` or `a`-`z`, else `0\n`. |
| APPROVED | strings | char_at_index | Reads a single ASCII digit `0`-`9`, then `\n`, then a `\n`-terminated line of at least N+1 chars. Prints the byte at 0-based index N + `\n`. |
| APPROVED | strings | substring_first_3 | Reads a `\n`-terminated line of at least 3 chars and prints just its first 3 bytes + `\n`. |
| APPROVED | strings | substring_last_3 | Reads a `\n`-terminated line of at least 3 chars and prints just its last 3 bytes (the 3 chars immediately before the `\n`) + `\n`. |
| APPROVED | strings | count_letter_e | Reads a `\n`-terminated line ≤ 80 chars and prints the count of `e` or `E` bytes as decimal + `\n`. |

## Batch 3 — branching + loops + recursion (99 approved + 2 overlap + 2 clarified)

Categories: branching (40 net), loops (51 net of 53 proposed), recursion (10 net).
CR-ist found 2 overlaps + 2 UNCLEAR descriptions (clarified in place); the other 99 are APPROVED.

| status | category | name | description |
|---|---|---|---|
| APPROVED | branching | sort_two_asc | Reads two decimal integers and prints them sorted ascending: `<smaller>\n<larger>\n`. |
| APPROVED | branching | sort_two_desc | Reads two decimal integers and prints them sorted descending: `<larger>\n<smaller>\n`. |
| APPROVED | branching | sort_three_asc | Reads three decimal integers and prints them sorted ascending, one per line. |
| APPROVED | branching | sort_three_desc | Reads three decimal integers and prints them sorted descending, one per line. |
| APPROVED | branching | classify_age | Reads decimal age `0`-`120` and prints `infant\n` if `<2`, `child\n` if `2-12`, `teen\n` if `13-19`, `adult\n` if `20-64`, `senior\n` if `>=65`. |
| APPROVED | branching | classify_grade | Reads decimal score `0`-`100` and prints `A\n` if `>=90`, `B\n` if `80-89`, `C\n` if `70-79`, `D\n` if `60-69`, else `F\n`. |
| APPROVED | branching | classify_temp_c | Reads signed decimal Celsius temperature and prints one of `freezing\n` (≤0), `cold\n` (1-10), `mild\n` (11-20), `warm\n` (21-30), `hot\n` (≥31). |
| APPROVED | branching | day_of_week_name | Reads decimal `0`-`6` and prints `Sunday`/`Monday`/`Tuesday`/`Wednesday`/`Thursday`/`Friday`/`Saturday` followed by `\n` (Sunday=0). |
| APPROVED | branching | month_name | Reads decimal `1`-`12` and prints the English month name (`January`...`December`) + `\n`. |
| APPROVED | branching | season_from_month | Reads decimal month `1`-`12` and prints `winter\n` (12,1,2), `spring\n` (3,4,5), `summer\n` (6,7,8), `fall\n` (9,10,11). |
| APPROVED | branching | even_or_odd_word | Reads one decimal integer and prints `even\n` or `odd\n` (not `0`/`1`). |
| OVERLAP | branching | sign_word | OVERLAP with sign_of (3-agent consensus): same 3-way sign classification; differs only in output template. Dropped. |
| APPROVED | branching | compare_to_10 | Reads one decimal and prints `less\n` if `<10`, `equal\n` if `=10`, `more\n` if `>10`. |
| APPROVED | branching | compare_to_100 | Reads one decimal and prints `less\n` if `<100`, `equal\n` if `=100`, `more\n` if `>100`. |
| APPROVED | branching | is_alphanumeric_byte | Reads exactly one byte and prints `1\n` if it's `0`-`9`/`A`-`Z`/`a`-`z`, else `0\n`. |
| APPROVED | branching | is_punctuation_byte | Reads exactly one byte and prints `1\n` if it's one of `,.?!;:'-` (the eight common punctuation marks), else `0\n`. |
| APPROVED | branching | is_whitespace_byte | Reads exactly one byte and prints `1\n` if it's space/tab/newline (`0x20`, `0x09`, `0x0A`), else `0\n`. |
| APPROVED | branching | char_class | Reads exactly one byte and prints one of `digit\n`, `upper\n`, `lower\n`, `other\n` based on the byte's ASCII range. |
| APPROVED | branching | weekday_or_weekend | Reads decimal day-of-week `0`-`6` (Sunday=0) and prints `weekend\n` (Sat/Sun) or `weekday\n` (Mon-Fri). |
| APPROVED | branching | is_business_hour | Reads decimal hour `0`-`23` (24-hour clock) and prints `1\n` if `9 <= h <= 17`, else `0\n`. |
| OVERLAP | branching | simple_op_calc | OVERLAP with interactive_calc (2-agent audit): same I/O shape; simple_op_calc is just the single-digit-operand subset of interactive_calc. Bounded-input precedent (sum_of_digits_2digit). Dropped. |
| APPROVED | branching | fizzbuzz_classify_one | Reads decimal N in `1`-`100` and prints just one of: `fizz\n` if `N % 3 == 0` and not `% 5`; `buzz\n` if `N % 5 == 0` and not `% 3`; `fizzbuzz\n` if both; else `<N>\n`. |
| APPROVED | branching | min_or_max_select | Reads one ASCII bit (`0` or `1`) followed by `\n`, then two decimals each followed by `\n`. If bit is `0` prints the min, if `1` prints the max + `\n`. |
| APPROVED | branching | abs_or_negate_select | Reads one ASCII bit, then a signed decimal. If bit is `0` prints `abs(a)`, if `1` prints `-a`, each + `\n`. |
| APPROVED | branching | upper_or_lower_select | Reads one ASCII bit, then exactly one byte. If bit is `0` outputs the byte uppercased, if `1` outputs it lowercased. |
| APPROVED | branching | switch_on_digit | Reads one ASCII digit `0`-`9` and prints `a\n` for 0, `b\n` for 1, …, `j\n` for 9. |
| APPROVED | branching | triangle_classify | Reads three positive decimals `a`,`b`,`c` (each ≤ 99, on own line) as triangle side lengths. Prints `equilateral\n`, `isosceles\n`, `scalene\n`, or `not\n` (if no valid triangle). |
| APPROVED | branching | quadrant_2d | Reads two signed decimals `x` then `y` and prints `1\n`/`2\n`/`3\n`/`4\n` based on Cartesian quadrant; prints `axis\n` if either coordinate is 0. |
| APPROVED | branching | compare_three_order | Reads three decimals `a`,`b`,`c` (each own line) and prints one of `abc`/`acb`/`bac`/`bca`/`cab`/`cba` + `\n` indicating their ascending sorted order by original label. (Ties broken alphabetically by label.) |
| APPROVED | branching | parity_three | Reads three decimals and prints `all even\n` if all are even, `all odd\n` if all odd, else `mixed\n`. |
| APPROVED | branching | all_positive_three | Reads three signed decimals and prints `1\n` if all are `> 0`, else `0\n`. |
| APPROVED | branching | any_zero_three | Reads three decimals and prints `1\n` if at least one equals 0, else `0\n`. |
| OVERLAP | branching | all_same_three | OVERLAP with is_equilateral (2-agent audit): identical algorithm and I/O contract; only the framing differs. Dropped. |
| APPROVED | branching | compare_with_window | Reads three decimals `a`, `lo`, `hi` (each own line) and prints `below\n` if `a < lo`, `in\n` if `lo <= a <= hi`, `above\n` if `a > hi`. |
| APPROVED | branching | sorted_check_three | Reads three decimals and prints `1\n` if they are in non-decreasing order, else `0\n`. |
| APPROVED | branching | sorted_check_four | Reads four decimals and prints `1\n` if they are in non-decreasing order, else `0\n`. |
| APPROVED | branching | rps_winner | Reads two bytes (each on own line, terminated by `\n`): `r`/`p`/`s` (rock/paper/scissors) for player 1 and player 2. Prints `1\n` if P1 wins, `2\n` if P2 wins, `tie\n` if tie. |
| APPROVED | branching | leap_year_check | Reads decimal year `1`-`9999` and prints `1\n` if it's a leap year (Gregorian rule: `(y%4==0 && y%100!=0) || y%400==0`), else `0\n`. |
| APPROVED | branching | bmi_category | Reads two decimals: weight-kg `1`-`200` then height-cm `100`-`250` (each own line). Computes BMI = weight*10000/(height*height) and prints `under\n` (BMI<18), `normal\n` (18-24), `over\n` (25-29), `obese\n` (≥30). |
| OVERLAP | branching | turn_signal | OVERLAP with menu_selection (2-agent audit): same byte→3-fixed-string-table algorithm. Same precedent as previously-dropped animal_sound, weather_report. Dropped. |
| APPROVED | loops | print_byte_n_times | Reads one byte then `\n` then a digit `0`-`9` + `\n`. Outputs the byte N times in a row. |
| APPROVED | loops | print_n_byte_lines | Reads one byte then `\n` then a digit `0`-`9` + `\n`. Prints N lines, each containing just that byte then `\n`. |
| APPROVED | loops | print_byte_grid | Reads one byte then `\n` then a digit `1`-`9` + `\n`. Prints an N-by-N grid filled with that byte (N lines, each N bytes then `\n`). |
| APPROVED | loops | right_triangle_stars | Reads digit N `1`-`9` + `\n`. Prints a right triangle of `*`: row i (1..N) has i stars followed by `\n`. |
| APPROVED | loops | inverted_right_triangle | Reads digit N `1`-`9` + `\n`. Prints rows of `*`: row i has (N+1-i) stars + `\n`. |
| APPROVED | loops | centered_pyramid | Reads digit N `1`-`9` + `\n`. Prints N rows of width `2N-1`: row i has `N-i` leading spaces, then `2i-1` `*`, then `\n`. |
| APPROVED | loops | hollow_box | Reads digit N `2`-`9` + `\n`. Prints an N-by-N hollow box: top and bottom rows are N `*`; middle rows are `*` + (N-2) spaces + `*`, each + `\n`. |
| APPROVED | loops | solid_square | Reads digit N `1`-`9` + `\n`. Prints an N-by-N solid square of `*`. |
| APPROVED | loops | checkerboard | Reads digit N `1`-`8` + `\n`. Prints an N-by-N checkerboard: top-left cell `*`, alternating `*` and `.` along each row and column. |
| APPROVED | loops | diagonal_stars | Reads digit N `1`-`9` + `\n`. Prints an N-by-N grid where cell (i,j) is `*` if `i == j` else `.`, rows separated by `\n`. |
| APPROVED | loops | x_pattern | Reads digit N `1`-`9` + `\n` (N odd preferred). Prints an N-by-N grid where cell (i,j) is `*` if `i == j` or `i + j == N - 1` else `.`. |
| APPROVED | loops | plus_pattern | Reads odd digit N `1`/`3`/`5`/`7`/`9` + `\n`. Prints an N-by-N grid with `*` along the middle row and the middle column, `.` elsewhere. |
| APPROVED | loops | v_pattern | Reads digit N `1`-`9` + `\n`. Prints N rows on a `(2N-1)`-wide grid. For row `i` (1-indexed, 1..N), the cell at column `j` (1-indexed) is `*` if `j == i` or `j == 2N - i`, else `.`. Each row ends with `\n`. Example for N=3: row 1 = `*...*\n`, row 2 = `.*.*.\n`, row 3 = `..*..\n`. |
| APPROVED | loops | print_alphabet_lower | No input. Prints `abcdefghijklmnopqrstuvwxyz\n`. |
| APPROVED | loops | print_alphabet_upper | No input. Prints `ABCDEFGHIJKLMNOPQRSTUVWXYZ\n`. |
| APPROVED | loops | print_alphabet_reversed | No input. Prints `zyxwvutsrqponmlkjihgfedcba\n`. |
| APPROVED | loops | print_digits_0_9 | No input. Prints `0123456789\n`. |
| APPROVED | loops | print_evens_2_to_20 | No input. Prints `2 4 6 8 10 12 14 16 18 20\n` (space-separated). |
| APPROVED | loops | print_odds_1_to_19 | No input. Prints `1 3 5 7 9 11 13 15 17 19\n` (space-separated). |
| APPROVED | loops | print_multiples_5_to_50 | No input. Prints `5 10 15 20 25 30 35 40 45 50\n`. |
| APPROVED | loops | print_fibs_first_10 | No input. Prints `0 1 1 2 3 5 8 13 21 34\n` (the first 10 Fibonacci numbers, space-separated). |
| APPROVED | loops | print_first_10_primes | No input. Prints `2 3 5 7 11 13 17 19 23 29\n`. |
| APPROVED | loops | print_first_10_squares | No input. Prints `1 4 9 16 25 36 49 64 81 100\n`. |
| APPROVED | loops | count_to_10 | No input. Prints `1\n2\n...\n10\n` (one per line, ten lines total). |
| APPROVED | loops | count_down_from_10 | No input. Prints `10\n9\n...\n1\n`. |
| APPROVED | loops | print_ascii_a_to_k | No input. Prints `65 66 67 68 69 70 71 72 73 74 75\n` (the ASCII codes of `A`-`K`, space-separated). |
| APPROVED | loops | print_powers_of_2_first_8 | No input. Prints `1 2 4 8 16 32 64 128\n`. |
| APPROVED | loops | print_powers_of_3_first_5 | No input. Prints `1 3 9 27 81\n`. |
| APPROVED | loops | print_factorial_first_6 | No input. Prints `1 2 6 24 120 720\n` (factorials 1..6). |
| APPROVED | loops | repeat_line_n | Reads a digit N `1`-`9` + `\n` then a `\n`-terminated line ≤ 30 chars. Prints the line N times (each ending with the same `\n`). |
| APPROVED | loops | line_then_n_blanks | Reads a digit N `0`-`9` + `\n` then a `\n`-terminated line ≤ 60 chars. Prints the line, then N additional `\n` characters. |
| APPROVED | loops | accumulate_sum | Reads up to 9 decimal integers, each followed by `\n`, terminated by an empty line (just `\n`). After each input, prints the running sum on its own line. |
| APPROVED | loops | print_pair_grid | No input. Prints all pairs `(i, j)` for `i, j` in `0`-`2` in row-major order, each formatted as `i j\n`. Output is 9 lines total. |
| APPROVED | loops | fizzbuzz_to_15 | No input. Prints lines 1 through 15 as standard FizzBuzz: multiples of 15 → `FizzBuzz`, of 3 → `Fizz`, of 5 → `Buzz`, else the number. One per line. |
| APPROVED | loops | fizzbuzz_to_20 | No input. Same rules as `fizzbuzz_to_15` but lines 1 through 20. |
| OVERLAP | loops | fizzbuzz_to_30 | OVERLAP with fizzbuzz_to_15/fizzbuzz_to_20: third bound-only variant adds no educational dimension beyond the first two. Dropped. |
| APPROVED | loops | count_input_bytes_running | Reads bytes until `\n`. After each byte, prints the byte's 1-based position as decimal + `\n`. Stops at `\n` (does not print the position of the `\n`). |
| APPROVED | loops | countdown_blastoff | No input. Prints `5\n4\n3\n2\n1\nBlastoff!\n`. |
| OVERLAP | loops | left_aligned_pyramid | OVERLAP with right_triangle_stars: same I/O and same body; description explicitly admits "handled identically." Dropped. |
| APPROVED | loops | hollow_diamond | Reads odd digit N `1`/`3`/`5`/`7`/`9` + `\n`. Prints an N-by-N hollow diamond. Let `k = (N+1)/2` (the middle row index, 1-indexed). For row `i` (1..N), let `d = abs(i - k)` (distance from middle row). The row has 1-indexed columns 1..N: column `j` is `*` if `j == k - d` or `j == k + d`, else ` ` (space). Each row ends with `\n`. Example for N=5: `  *  \n * * \n*   *\n * * \n  *  \n`. |
| APPROVED | loops | print_l_shape | Reads digit N `2`-`9` + `\n`. Prints an L-shape: N-1 rows of `*\n` (left bar), then one row of N `*`s + `\n` (bottom bar). |
| APPROVED | loops | print_t_shape | Reads digit N `3`/`5`/`7`/`9` + `\n`. Prints a T-shape: row 0 is N `*`s; rows 1..N-1 each have (N-1)/2 leading spaces then `*` then `\n`. |
| APPROVED | loops | print_vertical_bar | Reads digit N `1`-`9` + `\n`. Prints N lines, each just `*\n`. |
| APPROVED | loops | print_horizontal_bar | Reads digit N `1`-`9` + `\n`. Prints a single line of N `*`s followed by `\n`. |
| APPROVED | loops | sum_running_first_n | Reads digit N `1`-`9` + `\n`. Prints running sums on separate lines: `1\n3\n6\n10\n...\n` for the first N partial sums of `1+2+3+...`. |
| APPROVED | loops | range_step_two | Reads two decimals `lo` and `hi` (each own line, both 0-50, lo<=hi). Prints `lo, lo+2, lo+4, ...` up to ≤hi, one per line. |
| APPROVED | loops | range_step_three | Same as `range_step_two` but step 3. |
| APPROVED | loops | print_pair_diff_grid | No input. For all `i` in `0`-`3` and `j` in `0`-`3`, prints `i-j\n` (signed) on its own line, in row-major (i,j) order. 16 lines total. |
| APPROVED | loops | spaces_then_stars | Reads digit N `1`-`9` + `\n`. Prints N lines: row i has (N-i) spaces, then i `*`, then `\n` (right-aligned triangle). |
| APPROVED | loops | echo_first_n_bytes | Reads digit N `0`-`9` + `\n`, then reads N more bytes from stdin and outputs them verbatim. |
| APPROVED | loops | print_first_then_repeat | Reads one byte, then a digit N `1`-`9` + `\n`. Outputs the byte once, then repeats it N times on a new line. |
| APPROVED | loops | print_box_with_label | Reads digit N `3`-`9` + `\n` then a `\n`-terminated line of exactly N-2 chars. Prints an N-wide hollow box of `*` with the input line centered as the middle row (`* <line> *`). |
| APPROVED | loops | numbered_lines | Reads digit N `1`-`9` + `\n` then a `\n`-terminated line ≤ 20 chars. Prints N lines, each prefixed with `<i>: ` (1-based) and then the line. |
| APPROVED | recursion | factorial_recursive | Reads decimal N in `0`-`6` and prints `N!` using a recursive macro (via `stl.call` / `stl.return`). Same I/O as `arithmetic/factorial_small`; the purpose is to demonstrate recursion. |
| APPROVED | recursion | fibonacci_recursive | Reads decimal N in `0`-`10` and prints `F(N)` using a recursive macro. The purpose is to demonstrate naive double-recursion (not iteration). |
| APPROVED | recursion | sum_to_n_recursive | Reads decimal N in `0`-`10` and prints `1+2+...+N` using a recursive macro. Same I/O as `arithmetic/sum_to_n`; demonstrates the recursive accumulator pattern. |
| APPROVED | recursion | count_down_recursive | Reads decimal N in `0`-`9` + `\n`. Prints `N\n(N-1)\n...\n1\n` using a recursive macro that prints then recurses on N-1. |
| APPROVED | recursion | count_up_recursive | Reads decimal N in `0`-`9` + `\n`. Prints `1\n2\n...\nN\n` using a recursive macro that recurses on N-1 then prints. |
| APPROVED | recursion | power_recursive | Reads `base` `0`-`3` then `exp` `0`-`3` (each own line). Prints `base^exp` using a recursive macro `pow(b,e) = b * pow(b, e-1)`. |
| APPROVED | recursion | gcd_recursive | Reads two decimals `a`, `b` (each ≤ 50, own line). Prints `gcd(a,b)` using the recursive Euclidean algorithm. |
| APPROVED | recursion | multiply_by_addition | Reads two decimals each `0`-`8` and prints `a*b` computed via the recursive macro `mul(a,b) = a + mul(a, b-1)`. |
| APPROVED | recursion | is_even_mutual_recursive | Reads decimal N `0`-`10` and prints `1\n` if even else `0\n`, computed via mutual recursion: `is_even(0)=1`, `is_even(N) = is_odd(N-1)`, `is_odd(N) = is_even(N-1)`. |
| OVERLAP | recursion | is_odd_mutual_recursive | OVERLAP with is_even_mutual_recursive (2-agent audit): output is the strict bit-flip of is_even; description itself acknowledges "role swapped". Complement-of-existing-scan precedent. Dropped. |

## Batch 4 — data_structures + conversion + more bits (98 approved + 2 overlap)

Categories: data_structures (50 net), conversion (30 net), bits (18 net of 20 proposed).
CR-ist found 2 overlaps within batch 4 (msb_position ≡ count_leading_zeros, lsb_position ≡ count_trailing_zeros); other 98 are APPROVED.

| status | category | name | description |
|---|---|---|---|
| APPROVED | data_structures | stack_push_pop_demo | Reads digit N `1`-`9` + `\n`. Pushes integers `1..N` onto a stack, then pops all and prints each on its own line. Output is `N\n(N-1)\n...\n1\n` (reverse order). |
| APPROVED | data_structures | queue_enqueue_dequeue | Reads digit N `1`-`9` + `\n`. Enqueues integers `1..N` then dequeues all, printing each on its own line. Output is `1\n2\n...\nN\n` (FIFO order). |
| APPROVED | data_structures | stack_reverse_line | Reads a `\n`-terminated line ≤ 40 chars. Uses an explicit push-all-then-pop-all stack pattern (LIFO) to reverse the line; prints the reversed bytes followed by `\n`. The stack demonstration is the point. |
| APPROVED | data_structures | array_sum_5 | Reads exactly 5 decimal integers, each on its own line, and prints their sum + `\n`. |
| APPROVED | data_structures | array_sum_10 | Reads exactly 10 decimal integers, each on its own line, and prints their sum + `\n`. |
| APPROVED | data_structures | array_max_5 | Reads exactly 5 decimals (each own line) and prints the maximum + `\n`. |
| APPROVED | data_structures | array_max_10 | Reads exactly 10 decimals (each own line) and prints the maximum + `\n`. |
| APPROVED | data_structures | array_min_5 | Reads exactly 5 decimals and prints the minimum + `\n`. |
| APPROVED | data_structures | array_min_10 | Reads exactly 10 decimals and prints the minimum + `\n`. |
| APPROVED | data_structures | array_avg_5 | Reads exactly 5 decimals and prints `floor(sum / 5)` + `\n`. |
| APPROVED | data_structures | array_avg_10 | Reads exactly 10 decimals and prints `floor(sum / 10)` + `\n`. |
| APPROVED | data_structures | array_count_zeros | Reads digit N `1`-`9` + `\n`, then N decimal integers each own line. Prints the count of zeros as decimal + `\n`. |
| APPROVED | data_structures | array_count_negatives | Reads digit N `1`-`9` + `\n`, then N signed decimal integers. Prints the count of values `< 0` + `\n`. |
| APPROVED | data_structures | array_count_positives | Reads digit N `1`-`9` + `\n`, then N signed decimal integers. Prints the count of values `> 0` + `\n`. |
| APPROVED | data_structures | array_reverse_5 | Reads 5 decimals (each own line) and prints them in reverse order, one per line. |
| APPROVED | data_structures | array_double_each | Reads digit N `1`-`9` + `\n`, then N decimals. Prints `2*a_i` for each input on its own line, in the same order. |
| APPROVED | data_structures | array_increment_each | Reads digit N `1`-`9` + `\n`, then N decimals. Prints `a_i + 1` for each input on its own line, in the same order. |
| APPROVED | data_structures | array_first_3 | Reads digit N `3`-`9` + `\n`, then N decimals. Prints just the first 3 values, one per line. |
| APPROVED | data_structures | array_last_3 | Reads digit N `3`-`9` + `\n`, then N decimals. Prints just the last 3 values, one per line. |
| APPROVED | data_structures | bubble_sort_5 | Reads exactly 5 decimals and prints them sorted ascending (one per line), implemented as bubble sort (adjacent-swap passes). The algorithm choice is the point. |
| APPROVED | data_structures | insertion_sort_5 | Reads exactly 5 decimals and prints them sorted ascending (one per line), implemented as insertion sort (extend prefix one element at a time). |
| APPROVED | data_structures | selection_sort_5 | Reads exactly 5 decimals and prints them sorted ascending (one per line), implemented as selection sort (find-min-and-swap each pass). |
| APPROVED | data_structures | queue_print_order | Reads digit N `1`-`9` + `\n`, then exactly N bytes (no separator). Enqueues each byte then dequeues all, outputting them in original input order (FIFO demo). |
| APPROVED | data_structures | parens_matched | Reads a `\n`-terminated string ≤ 40 chars containing only `(` and `)`. Prints `1\n` if the parentheses are balanced (every `(` has a matching `)` in order), else `0\n`. |
| OVERLAP | data_structures | brackets_matched | OVERLAP with parens_matched: same balanced-pair scan; differs only in bracket character (4-agent audit). Dropped. |
| APPROVED | data_structures | mixed_brackets_matched | Reads a `\n`-terminated string ≤ 40 chars containing only `()[]{}`. Prints `1\n` if all three bracket types are balanced AND properly nested (e.g. `([])` valid, `([)]` invalid), else `0\n`. Use an explicit stack. |
| APPROVED | data_structures | count_distinct_bytes | Reads a `\n`-terminated line ≤ 80 chars and prints the count of distinct byte values in the line (excluding the terminating `\n`) as decimal + `\n`. |
| APPROVED | data_structures | array_dedupe_sorted | Reads digit N `1`-`9` + `\n`, then N decimals already sorted ascending. Prints the unique values in order, one per line. |
| APPROVED | data_structures | array_contains | Reads digit N `1`-`9` + `\n`, then N decimals, then one more decimal `target`. Prints `1\n` if target appears in the N-element array, else `0\n`. |
| APPROVED | data_structures | linear_search | Reads digit N `1`-`9` + `\n`, then N decimals, then `target`. Prints the 0-based index of the first match + `\n`, or `not found\n` if absent. |
| APPROVED | data_structures | binary_search_sorted | Reads digit N `1`-`9` + `\n`, then N decimals already sorted ascending, then `target`. Prints the 0-based index of the match + `\n` (any if duplicates), or `not found\n`. Uses binary search. |
| APPROVED | data_structures | min_index_5 | Reads exactly 5 decimals and prints the 0-based index of the minimum value + `\n`. Ties: prints the smallest index among tied positions. |
| APPROVED | data_structures | max_index_5 | Reads exactly 5 decimals and prints the 0-based index of the maximum value + `\n`. Ties: smallest index among tied positions. |
| APPROVED | data_structures | swap_first_last_5 | Reads exactly 5 decimals and prints them with positions 0 and 4 swapped, one per line. |
| APPROVED | data_structures | swap_adjacent_pairs_6 | Reads exactly 6 decimals and prints them with each adjacent pair swapped (positions 0↔1, 2↔3, 4↔5), one per line in the new order. |
| APPROVED | data_structures | rotate_left_5 | Reads exactly 5 decimals and prints them rotated left by 1 (input `a b c d e` → output `b\nc\nd\ne\na\n`). |
| APPROVED | data_structures | rotate_right_5 | Reads exactly 5 decimals and prints them rotated right by 1 (input `a b c d e` → output `e\na\nb\nc\nd\n`). |
| APPROVED | data_structures | shift_right_zero_fill_5 | Reads exactly 5 decimals and prints them shifted right by 1 with 0-fill on the left (input `a b c d e` → output `0\na\nb\nc\nd\n`). |
| APPROVED | data_structures | array_sum_evens | Reads digit N `1`-`9` + `\n`, then N decimals. Prints the sum of even-valued elements + `\n`. |
| APPROVED | data_structures | array_sum_odds | Reads digit N `1`-`9` + `\n`, then N decimals. Prints the sum of odd-valued elements + `\n`. |
| APPROVED | data_structures | array_count_above_threshold | Reads digit N `1`-`9` + `\n`, then `threshold` (signed decimal) + `\n`, then N signed decimals. Prints the count of values strictly greater than threshold + `\n`. |
| APPROVED | data_structures | histogram_5 | Reads exactly 5 ASCII digits `0`-`5` (each followed by `\n`). For each input value `v`, prints `v` `*` characters then `\n` (5 lines of output total). |
| APPROVED | data_structures | running_max | Reads digit N `1`-`9` + `\n`, then N signed decimals (each own line). After each input, prints the running maximum so far on its own line (N lines of output). |
| APPROVED | data_structures | running_min | Reads digit N `1`-`9` + `\n`, then N signed decimals. After each input, prints the running minimum so far on its own line. |
| APPROVED | data_structures | is_sorted_ascending | Reads digit N `1`-`9` + `\n`, then N decimals. Prints `1\n` if the sequence is non-decreasing, else `0\n`. |
| APPROVED | data_structures | is_sorted_descending | Reads digit N `1`-`9` + `\n`, then N decimals. Prints `1\n` if the sequence is non-increasing, else `0\n`. |
| APPROVED | data_structures | array_range | Reads digit N `1`-`9` + `\n`, then N decimals. Prints `max - min` + `\n`. |
| APPROVED | data_structures | partial_sums | Reads digit N `1`-`9` + `\n`, then N decimals. Prints the running cumulative sum after each input, one per line (N lines). |
| APPROVED | data_structures | count_inversions_5 | Reads exactly 5 decimals and prints the count of inversions (pairs `(i, j)` with `i < j` and `a_i > a_j`) as decimal + `\n`. |
| APPROVED | data_structures | array_median_5 | Reads exactly 5 decimals (any order) and prints the median (middle value when sorted) as decimal + `\n`. |
| APPROVED | conversion | dec_to_hex | Reads decimal `0`-`255` + `\n` and prints exactly two lowercase hex digits (no `0x` prefix), followed by `\n`. |
| APPROVED | conversion | hex_to_dec | Reads exactly two lowercase hex digits + `\n` and prints the decimal `0`-`255` + `\n`. |
| APPROVED | conversion | dec_to_binary | Reads decimal `0`-`255` + `\n` and prints an 8-char binary string of `0` and `1` (MSB first), followed by `\n`. |
| APPROVED | conversion | binary_to_dec | Reads an 8-char binary string of `0`/`1` + `\n` and prints the decimal `0`-`255` + `\n`. |
| APPROVED | conversion | dec_to_octal | Reads decimal `0`-`63` + `\n` and prints exactly two octal digits + `\n`. |
| APPROVED | conversion | octal_to_dec | Reads exactly two octal digits + `\n` and prints the decimal `0`-`63` + `\n`. |
| APPROVED | conversion | binary_to_hex | Reads an 8-char binary string + `\n` and prints exactly two lowercase hex digits + `\n`. |
| APPROVED | conversion | hex_to_binary | Reads exactly two lowercase hex digits + `\n` and prints an 8-char binary string + `\n`. |
| APPROVED | conversion | celsius_to_fahrenheit | Reads a signed decimal Celsius temperature (range `-100`..`100`) + `\n` and prints `floor(C * 9 / 5 + 32)` as a signed decimal + `\n`. |
| APPROVED | conversion | fahrenheit_to_celsius | Reads a signed decimal Fahrenheit temperature (range `-148`..`212`) + `\n` and prints `floor((F - 32) * 5 / 9)` as a signed decimal + `\n`. |
| APPROVED | conversion | km_to_miles | Reads decimal kilometers `0`-`100` + `\n` and prints `floor(km * 5 / 8)` as decimal miles + `\n`. |
| APPROVED | conversion | miles_to_km | Reads decimal miles `0`-`60` + `\n` and prints `floor(miles * 8 / 5)` as decimal km + `\n`. |
| APPROVED | conversion | minutes_to_hours_minutes | Reads decimal total minutes `0`-`999` + `\n` and prints `<H>:<MM>\n`, where `H` is `total / 60` (no leading zero) and `MM` is `total % 60` zero-padded to 2 digits. |
| APPROVED | conversion | seconds_to_minutes_seconds | Reads decimal total seconds `0`-`3599` + `\n` and prints `<M>:<SS>\n`, with `MM` zero-padded to 2 digits. |
| APPROVED | conversion | hours_to_minutes | Reads decimal hours `0`-`24` + `\n` and prints `hours * 60` as decimal + `\n`. |
| APPROVED | conversion | days_to_hours | Reads decimal days `0`-`30` + `\n` and prints `days * 24` as decimal + `\n`. |
| APPROVED | conversion | dec_to_thousands_grouped | Reads decimal `0`-`999999` + `\n` and prints the value with thousands separators (commas), then `\n`. Examples: `7` → `7\n`, `1000` → `1,000\n`, `12345` → `12,345\n`, `999999` → `999,999\n`. |
| APPROVED | conversion | word_zero_to_nine | Reads a single ASCII digit `0`-`9` + `\n` and prints its English word (`zero`, `one`, `two`, ..., `nine`) + `\n`. |
| APPROVED | conversion | word_to_digit | Reads one of the English number words `zero`, `one`, `two`, ..., `nine` (terminated by `\n`) and prints the corresponding ASCII digit `0`-`9` + `\n`. |
| APPROVED | conversion | zero_pad_to_4 | Reads decimal `0`-`9999` + `\n` and prints a 4-character zero-padded representation + `\n`. Examples: `7` → `0007\n`, `1234` → `1234\n`. |
| APPROVED | conversion | roman_numeral_1_to_10 | Reads decimal `1`-`10` + `\n` and prints the corresponding Roman numeral (`I`, `II`, ..., `X`) + `\n`. |
| APPROVED | conversion | roman_to_dec_1_to_10 | Reads a Roman numeral string (one of `I`, `II`, ..., `X`) + `\n` and prints the decimal `1`-`10` + `\n`. |
| APPROVED | conversion | lowercase_letter_to_index | Reads exactly one byte `a`-`z` and prints its 0-based alphabet index (`a`→`0`, ..., `z`→`25`) as decimal + `\n`. |
| APPROVED | conversion | index_to_lowercase_letter | Reads decimal `0`-`25` + `\n` and outputs exactly one byte: the corresponding lowercase letter (`0`→`a`, `25`→`z`). No trailing `\n` after the byte. |
| APPROVED | conversion | uppercase_letter_to_index | Reads exactly one byte `A`-`Z` and prints its 0-based alphabet index (`A`→`0`, ..., `Z`→`25`) as decimal + `\n`. |
| APPROVED | conversion | dollars_to_cents | Reads decimal dollars `0`-`99` + `\n` and prints `dollars * 100` as decimal + `\n`. |
| APPROVED | conversion | cents_to_dollars_cents | Reads decimal cents `0`-`9999` + `\n` and prints `<dollars>.<cc>\n`, where `cc` is `cents % 100` zero-padded to 2 digits. |
| APPROVED | conversion | nibble_to_hex_char | Reads decimal `0`-`15` + `\n` and outputs exactly one byte: the corresponding lowercase hex char (`0`-`9` or `a`-`f`), followed by `\n`. |
| APPROVED | conversion | hex_char_to_nibble | Reads exactly one byte that's a lowercase hex char (`0`-`9` or `a`-`f`) + `\n` and prints the decimal `0`-`15` + `\n`. |
| APPROVED | conversion | dec_with_explicit_sign | Reads a signed decimal `-9999`..`9999` + `\n` and prints it with an always-explicit sign byte (`+` or `-`) prefix, followed by `\n`. Examples: `5` → `+5\n`, `0` → `+0\n`, `-3` → `-3\n`. |
| APPROVED | bits | toggle_bit_at_position | Reads one byte, then one ASCII digit `0`-`7` + `\n`. Outputs the byte with the bit at that position XOR'd (toggled). Convention: position `0` is the LSB (matches `bit_at_position`). |
| APPROVED | bits | count_leading_zeros | Reads one byte and prints the count of zero bits before the first `1` (counting from the MSB downward), `0`-`8`, + `\n`. The zero byte yields `8`. |
| APPROVED | bits | count_trailing_zeros | Reads one byte and prints the count of zero bits before the first `1` (counting from the LSB upward), `0`-`8`, + `\n`. The zero byte yields `8`. |
| OVERLAP | bits | msb_position | OVERLAP with count_leading_zeros: same scan algorithm; msb_position = 7 - count_leading_zeros for non-zero bytes. Dropped. |
| OVERLAP | bits | lsb_position | OVERLAP with count_trailing_zeros: identical output for non-zero bytes; same scan from LSB. Dropped. |
| APPROVED | bits | byte_to_binary_string | Reads one byte (raw) and prints an 8-char binary string of `0`/`1` (MSB first), followed by `\n`. Differs from `conversion/dec_to_binary` (which reads a decimal text representation). |
| APPROVED | bits | binary_string_to_byte | Reads an 8-char binary string of `0`/`1` + `\n` and outputs the corresponding raw byte (no trailing `\n`). Inverse of `byte_to_binary_string`. |
| OVERLAP | bits | byte_to_hex_string | OVERLAP with char_to_hex (2-agent audit): same byte→2-hex-chars algorithm; differs only in `0x` prefix. Variant-by-prefix precedent. Dropped. |
| APPROVED | bits | is_byte_zero | Reads one byte and prints `1\n` if it equals `0x00`, else `0\n`. |
| APPROVED | bits | is_byte_full | Reads one byte and prints `1\n` if it equals `0xFF`, else `0\n`. |
| APPROVED | bits | xor_with_constant_55 | Reads one byte and outputs `byte XOR 0x55`, as one raw byte. |
| APPROVED | bits | and_with_constant_0f | Reads one byte and outputs `byte AND 0x0F` (low nibble preserved, high nibble zeroed), as one raw byte. |
| APPROVED | bits | or_with_constant_80 | Reads one byte and outputs `byte OR 0x80` (MSB set, other bits preserved), as one raw byte. |
| APPROVED | bits | byte_decrement_wrap | Reads one byte and outputs `(byte - 1) mod 256` as one raw byte (e.g. `0x00` → `0xFF`). |
| APPROVED | bits | rotate_left_byte | Reads one byte and outputs the byte rotated left by 1 bit (MSB wraps around to LSB), as one raw byte. |
| APPROVED | bits | rotate_right_byte | Reads one byte and outputs the byte rotated right by 1 bit (LSB wraps around to MSB), as one raw byte. |
| APPROVED | bits | byte_concat_to_hex_word | Reads exactly two bytes (high then low) and prints 4 lowercase hex chars (no `0x` prefix) + `\n`. The first byte's hex appears first. |
| APPROVED | bits | byte_split_from_hex_word | Reads exactly 4 lowercase hex chars + `\n` and outputs two raw bytes: the high byte first, then the low byte. |
| APPROVED | bits | count_bits_in_three_bytes | Reads exactly 3 bytes and prints the total 1-bit count across all 24 bits as decimal `0`-`24` + `\n`. |
| APPROVED | bits | dominant_bit | Reads one byte. Prints `1\n` if it has more 1-bits than 0-bits (popcount > 4), `0\n` if more 0-bits than 1-bits (popcount < 4), or `tie\n` if popcount equals 4. |

## Batch 5 — algorithms + sequences + text_processing (93 approved + 5 overlap + 2 clarified)

Categories: algorithms (45 net of 50), sequences (28 net of 30), text_processing (20 net).
CR-ist found 5 overlaps (4 bubble-variant sorts + insertion-point dup of first-match) + 2 UNCLEAR (tightened in place); other 93 APPROVED.

| status | category | name | description |
|---|---|---|---|
| APPROVED | algorithms | quicksort_5 | Reads exactly 5 decimal integers (each on own line) and prints them sorted ascending (one per line). Implementation: quicksort (recursive partition around a pivot). |
| APPROVED | algorithms | mergesort_5 | Reads exactly 5 decimals and prints them sorted ascending (one per line). Implementation: merge sort (recursive split + merge). |
| APPROVED | algorithms | heap_sort_5 | Reads exactly 5 decimals and prints them sorted ascending (one per line). Implementation: heap sort (build max-heap, repeatedly extract max). |
| APPROVED | algorithms | counting_sort_n_small | Reads digit N `1`-`9` + `\n`, then N single-digit decimals `0`-`9`. Prints them sorted ascending (one per line) via counting sort (tally each value then emit in order). |
| APPROVED | algorithms | radix_sort_n_small | Reads digit N `1`-`9` + `\n`, then N two-digit decimals `0`-`99`. Prints them sorted ascending (one per line) via radix sort (two passes: ones then tens). |
| OVERLAP | algorithms | cocktail_sort_5 | OVERLAP with batch4/bubble_sort_5: bidirectional bubble — same adjacent-swap kernel. Dropped. |
| OVERLAP | algorithms | gnome_sort_5 | OVERLAP with batch4/insertion_sort_5: walk-back-swap reformulation of insertion sort. Dropped. |
| APPROVED | algorithms | shell_sort_5 | Reads exactly 5 decimals and prints them sorted ascending. Implementation: shell sort with gap sequence `2, 1`. |
| OVERLAP | algorithms | odd_even_sort_5 | OVERLAP with batch4/bubble_sort_5: pass-pair split of bubble's adjacent-swap kernel. Dropped. |
| OVERLAP | algorithms | comb_sort_5 | OVERLAP with batch5/shell_sort_5: bubble with shrinking gap; shell already covers the gap-sequence idea. Dropped. |
| APPROVED | algorithms | cycle_sort_5 | Reads exactly 5 decimals and prints them sorted ascending. Implementation: cycle sort (minimum-write sort — find each element's correct position and place via cycle following). |
| APPROVED | algorithms | pancake_sort_5 | Reads exactly 5 decimals and prints them sorted ascending. Implementation: pancake sort — only prefix reversals (no swaps). |
| APPROVED | algorithms | linear_search_count | Reads digit N `1`-`9` + `\n`, then N decimals (each own line), then a target decimal. Prints the count of occurrences of the target in the array as decimal + `\n`. |
| APPROVED | algorithms | linear_search_last | Reads digit N `1`-`9` + `\n`, then N decimals, then target. Prints the 0-based index of the LAST occurrence + `\n`, or `not found\n` if absent. |
| APPROVED | algorithms | binary_search_first_match | Reads digit N `1`-`9` + `\n`, then N decimals sorted ascending (may have duplicates), then target. Prints the 0-based index of the FIRST occurrence (lower-bound) + `\n`, or `not found\n`. |
| APPROVED | algorithms | binary_search_last_match | Reads digit N `1`-`9` + `\n`, then N decimals sorted ascending (may have duplicates), then target. Prints the 0-based index of the LAST occurrence (upper-bound-1) + `\n`, or `not found\n`. |
| OVERLAP | algorithms | binary_search_insertion_point | OVERLAP with binary_search_first_match: lower-bound is exactly the first-match index whether target is present or absent. Same lower-bound algorithm with cosmetic output difference. Dropped. |
| APPROVED | algorithms | jump_search_sorted | Reads digit N `1`-`9` + `\n`, then N decimals sorted ascending, then target. Prints the 0-based index of any match + `\n`, or `not found\n`. Implementation: jump search (block size ~√N, linear scan within block). |
| APPROVED | algorithms | exponential_search_sorted | Reads digit N `1`-`9` + `\n`, then N decimals sorted ascending, then target. Prints the 0-based index of any match + `\n`, or `not found\n`. Implementation: exponential search (find range by doubling i, then binary search within range). |
| APPROVED | algorithms | ternary_search_sorted | Reads digit N `1`-`9` + `\n`, then N decimals sorted ascending, then target. Prints the 0-based index of any match + `\n`, or `not found\n`. Implementation: ternary search (divide range into thirds). |
| APPROVED | algorithms | sieve_of_eratosthenes_30 | No input. Prints the primes in `[2, 30]` space-separated on one line + `\n`: `2 3 5 7 11 13 17 19 23 29\n`. Implementation: sieve of Eratosthenes (mark composites). |
| APPROVED | algorithms | sieve_of_eratosthenes_50 | No input. Prints the primes in `[2, 50]` space-separated + `\n`. Implementation: sieve of Eratosthenes. |
| APPROVED | algorithms | euclidean_gcd_with_steps | Reads two positive decimals `a`, `b` each `1`-`100` (own lines). Prints each step of Euclidean GCD as `a b\n` (current pair after `a = b, b = a % b`), terminating with `<gcd> 0\n`. |
| APPROVED | algorithms | extended_gcd_small | Reads two positive decimals `a`, `b` each `1`-`30` (own lines). Prints `g x y\n` such that `a*x + b*y = g = gcd(a, b)`, where `x`, `y` may be signed integers. |
| APPROVED | algorithms | fast_exponentiation | Reads `base` `2`-`5`, `exp` `0`-`10`, `mod` `1`-`100` (each own line). Prints `(base^exp) mod mod` as decimal + `\n`. Implementation: exponentiation-by-squaring. |
| APPROVED | algorithms | min_max_one_pass | Reads digit N `1`-`9` + `\n`, then N signed decimals. Prints `<min>\n<max>\n` using a single pass (pair-compare optimization). |
| APPROVED | algorithms | mode_of_5 | Reads exactly 5 decimals and prints the most frequent value + `\n`. Ties broken by smallest value among the most frequent. |
| APPROVED | algorithms | mean_median_mode_5 | Reads exactly 5 decimals and prints `<mean>\n<median>\n<mode>\n` (floor mean; median = middle of sorted; mode = most frequent value, ties broken by smallest). |
| APPROVED | algorithms | dutch_flag_3way | Reads digit N `1`-`9` + `\n`, then N values each `0`, `1`, or `2` (one per line). Prints the values partitioned in order so all 0s come first, then all 1s, then all 2s (one per line). |
| APPROVED | algorithms | moore_voting_majority | Reads digit N `1`-`9` + `\n`, then N decimals. Prints the majority element (value appearing strictly more than N/2 times) + `\n`, or `none\n` if no majority. Implementation: Boyer-Moore voting (one-pass + verify). |
| APPROVED | algorithms | kadane_max_subarray | Reads digit N `1`-`9` + `\n`, then N signed decimals. Prints the maximum contiguous subarray sum as signed decimal + `\n`. Implementation: Kadane's algorithm. |
| APPROVED | algorithms | two_sum_unsorted | Reads digit N `2`-`9` + `\n`, then N decimals, then `target`. Prints `i j\n` (0-based, `i < j`) of any pair summing to target, or `not found\n`. Implementation: nested loop. |
| APPROVED | algorithms | two_sum_sorted_two_pointers | Reads digit N `2`-`9` + `\n`, then N decimals sorted ascending, then `target`. Prints `i j\n` (0-based, `i < j`) of any pair summing to target, or `not found\n`. Implementation: two-pointer (left, right). |
| APPROVED | algorithms | three_sum_zero | Reads digit N `3`-`9` + `\n`, then N signed decimals. Prints `i j k\n` (0-based, `i < j < k`) of any triple summing to 0, or `none\n`. |
| APPROVED | algorithms | max_product_pair | Reads digit N `2`-`9` + `\n`, then N signed decimals. Prints the maximum product of any two distinct-indexed elements as signed decimal + `\n`. |
| APPROVED | algorithms | min_product_pair | Reads digit N `2`-`9` + `\n`, then N signed decimals. Prints the minimum product of any two distinct-indexed elements + `\n`. |
| APPROVED | algorithms | longest_run_length | Reads digit N `1`-`9` + `\n`, then N decimals. Prints the length of the longest run of equal consecutive elements as decimal + `\n`. |
| APPROVED | algorithms | count_distinct_elements | Reads digit N `1`-`9` + `\n`, then N decimals. Prints the count of distinct values + `\n`. |
| APPROVED | algorithms | is_palindrome_array | Reads digit N `1`-`9` + `\n`, then N decimals. Prints `1\n` if the sequence reads the same forward and backward, else `0\n`. |
| APPROVED | algorithms | zigzag_array_check | Reads digit N `1`-`9` + `\n`, then N decimals. Prints `1\n` if the sequence strictly alternates `a[0] < a[1] > a[2] < a[3] > ...` (starting with rise), else `0\n`. |
| APPROVED | algorithms | count_local_maxima | Reads digit N `3`-`9` + `\n`, then N decimals. Prints the count of strict local maxima (positions `i` with `0 < i < N-1` and `a[i-1] < a[i] > a[i+1]`) + `\n`. |
| APPROVED | algorithms | count_local_minima | Reads digit N `3`-`9` + `\n`, then N decimals. Prints the count of strict local minima + `\n`. |
| APPROVED | algorithms | wave_array_arrange | Reads digit N `1`-`9` + `\n`, then N decimals. Prints them rearranged in wave pattern (sorted ascending, then adjacent pairs swapped: `a[0] >= a[1] <= a[2] >= a[3] <= ...`), one per line. |
| APPROVED | algorithms | is_permutation_1_to_n | Reads digit N `1`-`9` + `\n`, then N decimals. Prints `1\n` if the sequence is a permutation of `{1, 2, ..., N}`, else `0\n`. |
| APPROVED | algorithms | find_missing_in_sequence | Reads digit N `2`-`9` + `\n`, then `N-1` decimals which are some permutation of `{1, 2, ..., N}` with exactly one value missing. Prints the missing value + `\n`. |
| APPROVED | algorithms | find_duplicate_in_sequence | Reads digit N `2`-`9` + `\n`, then N decimals from `{1, 2, ..., N-1}` with exactly one value duplicated. Prints the duplicated value + `\n`. |
| APPROVED | algorithms | tortoise_hare_cycle | Reads `start` `0`-`15` (own line). Iterates `x = (2*x + 1) mod 16` starting from `start`. Uses Floyd's tortoise-and-hare to detect when the sequence enters a cycle, then prints the cycle length as decimal + `\n`. |
| APPROVED | algorithms | matrix_transpose_3x3 | Reads 9 decimals (3 rows × 3 cols, row-major, each own line). Prints the transposed 3×3 matrix in row-major order, one row per output line with space-separated values + `\n` per row (3 lines total). |
| APPROVED | algorithms | matrix_diagonal_sum_3x3 | Reads 9 decimals (3×3 row-major). Prints the sum of the main diagonal `a[0][0] + a[1][1] + a[2][2]` as decimal + `\n`. |
| APPROVED | algorithms | matrix_is_symmetric_3x3 | Reads 9 decimals (3×3 row-major). Prints `1\n` if the matrix equals its transpose, else `0\n`. |
| APPROVED | sequences | triangular_first_n | Reads digit N `1`-`9` + `\n`. Prints the first N triangular numbers `T(k) = k(k+1)/2` for `k = 1..N`, space-separated, ending with `\n`. |
| APPROVED | sequences | square_first_n | Reads digit N `1`-`9` + `\n`. Prints the first N positive squares `1, 4, 9, ..., N²`, space-separated, + `\n`. |
| APPROVED | sequences | pentagonal_first_n | Reads digit N `1`-`9` + `\n`. Prints the first N pentagonal numbers `P(k) = k(3k - 1)/2`, space-separated, + `\n`. |
| APPROVED | sequences | hexagonal_first_n | Reads digit N `1`-`9` + `\n`. Prints the first N hexagonal numbers `H(k) = k(2k - 1)`, space-separated, + `\n`. |
| APPROVED | sequences | cube_first_n | Reads digit N `1`-`9` + `\n`. Prints the first N positive cubes `1, 8, 27, ..., N³`, space-separated, + `\n`. |
| APPROVED | sequences | tetrahedral_first_n | Reads digit N `1`-`9` + `\n`. Prints the first N tetrahedral numbers `Te(k) = k(k+1)(k+2)/6`, space-separated, + `\n`. |
| APPROVED | sequences | catalan_first_5 | No input. Prints the first 5 Catalan numbers `1 1 2 5 14\n`. |
| APPROVED | sequences | bell_first_5 | No input. Prints the first 5 Bell numbers `1 1 2 5 15\n`. |
| APPROVED | sequences | derangement_first_5 | No input. Prints the first 5 derangement numbers `D(n)` for `n = 1..5`: `0 1 2 9 44\n`. |
| APPROVED | sequences | lucas_first_n | Reads digit N `1`-`9` + `\n`. Prints `L(0), L(1), ..., L(N-1)` (where `L(0)=2, L(1)=1`), space-separated, + `\n`. |
| APPROVED | sequences | perrin_first_10 | No input. Prints the first 10 Perrin sequence values starting `P(0)=3, P(1)=0, P(2)=2`: `3 0 2 3 2 5 5 7 10 12\n`. |
| APPROVED | sequences | padovan_first_10 | No input. Prints the first 10 Padovan sequence values starting `1 1 1 2 2 3 4 5 7 9\n`. |
| APPROVED | sequences | jacobsthal_first_8 | No input. Prints the first 8 Jacobsthal numbers `J(n)` starting `0 1 1 3 5 11 21 43\n`. |
| APPROVED | sequences | pell_first_8 | No input. Prints the first 8 Pell numbers `P(n)` starting `0 1 2 5 12 29 70 169\n`. |
| APPROVED | sequences | tribonacci_first_10 | No input. Prints the first 10 Tribonacci values starting `T(0)=T(1)=0, T(2)=1`: `0 0 1 1 2 4 7 13 24 44\n`. |
| APPROVED | sequences | tetranacci_first_8 | No input. Prints the first 8 Tetranacci values starting `0 0 0 1 1 2 4 8\n`. |
| APPROVED | sequences | fibonacci_even_first_5 | No input. Prints the first 5 even Fibonacci numbers: `0 2 8 34 144\n`. |
| APPROVED | sequences | fibonacci_odd_first_5 | No input. Prints the first 5 odd Fibonacci numbers: `1 1 3 5 13\n`. |
| APPROVED | sequences | fibonacci_sum_first_n | Reads digit N `1`-`12` + `\n`. Prints `F(1) + F(2) + ... + F(N)` (with `F(1)=1, F(2)=1, ...`) as decimal + `\n`. |
| APPROVED | sequences | fibonacci_squares_first_5 | No input. Prints `F(1)² F(2)² ... F(5)²` = `1 1 4 9 25` space-separated + `\n`. |
| APPROVED | sequences | fibonacci_modulo_10 | Reads decimal N in `1`-`20` (one or two ASCII digits, terminated by `\n`). Prints `F(N) mod 10` as a single decimal digit + `\n`. |
| APPROVED | sequences | partition_first_5 | No input. Prints the first 5 integer-partition counts `p(1), ..., p(5)` = `1 2 3 5 7` space-separated + `\n`. |
| APPROVED | sequences | mersenne_first_5 | No input. Prints the first 5 Mersenne numbers `M(n) = 2^n - 1` for `n = 1..5`: `1 3 7 15 31` space-separated + `\n`. |
| APPROVED | sequences | mersenne_prime_first_3 | No input. Prints the first 3 Mersenne primes: `3 7 31` space-separated + `\n`. |
| APPROVED | sequences | fermat_first_4 | No input. Prints the first 4 Fermat numbers `F(n) = 2^(2^n) + 1` for `n = 0..3`: `3 5 17 257` space-separated + `\n`. |
| APPROVED | sequences | mersenne_check | Reads decimal N in `2`-`17` (one or two ASCII digits, terminated by `\n`). Prints `1\n` if `2^N - 1` is prime, else `0\n`. (Upper bound `17` keeps trial division ≤ √(2^17 - 1) ≈ 362, well within runtime budget.) |
| APPROVED | sequences | lazy_caterers_first_8 | No input. Prints the first 8 lazy caterer's numbers (max regions with N cuts of a disc): `1 2 4 7 11 16 22 29` space-separated + `\n`. |
| APPROVED | sequences | centered_triangular_first_5 | No input. Prints the first 5 centered triangular numbers: `1 4 10 19 31` space-separated + `\n`. |
| APPROVED | sequences | centered_square_first_5 | No input. Prints the first 5 centered square numbers: `1 5 13 25 41` space-separated + `\n`. |
| APPROVED | sequences | centered_hexagonal_first_5 | No input. Prints the first 5 centered hexagonal numbers: `1 7 19 37 61` space-separated + `\n`. |
| APPROVED | text_processing | word_count_multiline | Reads stdin until an empty line (`\n` alone). Prints the total count of whitespace-separated tokens across all non-empty lines as decimal + `\n`. Whitespace = `' '`, `'\t'`, `'\n'`; runs collapse; leading/trailing whitespace introduce no empty tokens. |
| APPROVED | text_processing | char_freq_table | Reads a `\n`-terminated line ≤ 80 chars. Prints each distinct byte value (excluding `\n`) and its count, one `<byte> <count>\n` per line, in ascending byte-value order. |
| APPROVED | text_processing | word_length_avg | Reads a `\n`-terminated line ≤ 80 chars. Computes lengths of whitespace-separated tokens (space/tab/newline whitespace, runs collapse). Prints the floor of (sum of word lengths) / (word count) as decimal + `\n`. If no words, prints `0\n`. |
| APPROVED | text_processing | word_length_max | Reads a `\n`-terminated line ≤ 80 chars. Prints the length of the longest whitespace-separated token as decimal + `\n`. Empty input → `0\n`. |
| APPROVED | text_processing | word_length_min | Reads a `\n`-terminated line ≤ 80 chars. Prints the length of the shortest whitespace-separated token as decimal + `\n`. Empty input → `0\n`. |
| APPROVED | text_processing | longest_word | Reads a `\n`-terminated line ≤ 80 chars. Prints the longest whitespace-separated token + `\n`. Ties: prints the first such word. Empty input → empty line `\n`. |
| APPROVED | text_processing | shortest_word | Reads a `\n`-terminated line ≤ 80 chars. Prints the shortest whitespace-separated token + `\n`. Ties: prints the first such word. Empty input → empty line `\n`. |
| APPROVED | text_processing | word_with_most_vowels | Reads a `\n`-terminated line ≤ 80 chars. Prints the word with the most vowels (`aeiouAEIOU`) + `\n`. Ties: first such word. Empty input → empty line `\n`. |
| APPROVED | text_processing | count_word_occurrences | Reads a `\n`-terminated target word (no whitespace), then a `\n`-terminated line ≤ 80 chars. Prints the count of whitespace-separated tokens in the line that exactly equal the target (case-sensitive) + `\n`. |
| APPROVED | text_processing | period_sentence_count | Reads a `\n`-terminated line ≤ 80 chars. Prints the count of `.` bytes in the line (excluding `\n`) as decimal + `\n`. (Approximates sentence count by period count.) |
| APPROVED | text_processing | capitalize_first_letter | Reads a `\n`-terminated line ≤ 80 chars. If the first byte is `a`-`z`, outputs it uppercased; the rest of the line is unchanged. Includes final `\n`. |
| APPROVED | text_processing | capitalize_words | Reads a `\n`-terminated line ≤ 80 chars. Outputs the line with the first letter of each whitespace-separated word uppercased; all other letters lowercased. Whitespace and non-letters unchanged. Includes final `\n`. |
| APPROVED | text_processing | uncapitalize_first | Reads a `\n`-terminated line ≤ 80 chars. If the first byte is `A`-`Z`, outputs it lowercased; the rest of the line is unchanged. Includes final `\n`. |
| APPROVED | text_processing | reverse_words_in_line | Reads a `\n`-terminated line ≤ 80 chars. Splits on whitespace (single-space separator), prints the words in reverse order separated by single spaces, then `\n`. Example: `hello world foo` → `foo world hello\n`. |
| APPROVED | text_processing | count_unique_words | Reads a `\n`-terminated line ≤ 80 chars. Splits on whitespace (case-sensitive, runs collapse). Prints the count of distinct words as decimal + `\n`. |
| APPROVED | text_processing | longest_common_prefix_two | Reads two `\n`-terminated lines (each ≤ 40 chars). Prints the longest common prefix + `\n`. If no common prefix, prints just `\n`. |
| APPROVED | text_processing | longest_common_suffix_two | Reads two `\n`-terminated lines (each ≤ 40 chars). Prints the longest common suffix (compared between the lines' contents, excluding their `\n`s) + `\n`. If none, prints just `\n`. |
| APPROVED | text_processing | line_starts_with_substring | Reads a `\n`-terminated prefix (≤ 20 chars), then a `\n`-terminated line (≤ 60 chars). Prints `1\n` if the line starts with the prefix exactly, else `0\n`. |
| APPROVED | text_processing | line_ends_with_substring | Reads a `\n`-terminated suffix (≤ 20 chars), then a `\n`-terminated line (≤ 60 chars). Prints `1\n` if the line's content (excluding `\n`) ends with the suffix exactly, else `0\n`. |
| APPROVED | text_processing | count_substring_occurrences | Reads a `\n`-terminated pattern (≤ 20 chars), then a `\n`-terminated text (≤ 60 chars). Prints the count of non-overlapping left-to-right occurrences of pattern in text as decimal + `\n`. Empty pattern → `0\n`. |

## Batch 6 — interactive + encoding + state_machines (91 approved + 9 overlap)

Categories: interactive (35 net of 40), encoding (36 net of 40), state_machines (20 net).
CR-ist found 9 overlaps within batch or with prior batches; other 91 are APPROVED.

| status | category | name | description |
|---|---|---|---|
| APPROVED | interactive | echo_bot | Reads each `\n`-terminated input line until an empty line (just `\n`). For each non-empty line, prints `> <line>\n`. |
| APPROVED | interactive | greeting_bot | Reads a name (`\n`-terminated, ≤ 20 chars) and prints `Hello, <name>!\nGoodbye, <name>!\n`. |
| APPROVED | interactive | magic_eight_ball | Reads any `\n`-terminated question (≤ 60 chars). Prints exactly one of 5 fixed answers selected by `(input_length_excluding_newline) mod 5`: `0→Yes\n`, `1→No\n`, `2→Maybe\n`, `3→Ask again later\n`, `4→Definitely\n`. |
| APPROVED | interactive | yes_no_validator | Reads `y` or `n` + `\n` (any case is treated as exact byte). Prints `Affirmative\n` for `y`, `Negative\n` for `n`, otherwise `Please answer y or n\n`. |
| APPROVED | interactive | guess_one_round | Reads a single decimal digit `1`-`9` + `\n`. Secret value is `7`. Prints `correct!\n` if `7`, `too low\n` if `<7`, `too high\n` if `>7`. |
| APPROVED | interactive | menu_selection | Reads a single digit `1`-`4` + `\n`. Prints `Pizza\n`, `Burger\n`, `Salad\n`, or `Soup\n` for `1`/`2`/`3`/`4` respectively. |
| APPROVED | interactive | password_check | Reads a `\n`-terminated string ≤ 20 chars. Prints `Access granted\n` if the line content (excluding `\n`) equals the literal `flipjump`, else `Access denied\n`. |
| APPROVED | interactive | addition_quiz | Reads two single-digit decimals (each `\n`-terminated), then a decimal answer (`\n`-terminated, may be 1-2 digits). Prints `correct\n` if the answer equals the sum of the two digits, else `wrong (expected <S>)\n` with `S` the actual sum. |
| APPROVED | interactive | multiplication_quiz | Same I/O shape as `addition_quiz` but for multiplication. Prints `correct\n` if the answer equals the product, else `wrong (expected <P>)\n`. |
| OVERLAP | interactive | choose_path | OVERLAP with menu_selection (2-agent audit): same digit→fixed-string-table algorithm (3-line strings rather than 1-line). Same precedent as previously-dropped simple_meal_planner. Dropped. |
| APPROVED | interactive | interactive_calc | Reads one operator byte `+`, `-`, or `*` + `\n`, then two decimal integers (each `\n`-terminated). Prints the integer result + `\n`. (For `-`, prints signed result.) |
| APPROVED | interactive | user_input_loop_3 | Reads exactly 3 `\n`-terminated lines (each ≤ 30 chars). Prints `1: <line1>\n2: <line2>\n3: <line3>\n`. |
| APPROVED | interactive | coin_flip_pseudo | Reads exactly one byte. Prints `Heads\n` if its value is even, `Tails\n` if odd. (Pseudo-random via input parity.) |
| APPROVED | interactive | dice_roll_pseudo | Reads exactly one byte. Prints decimal `(byte mod 6) + 1` + `\n` (range `1`-`6`). |
| APPROVED | interactive | lucky_seven | Reads exactly one byte. Prints `Lucky!\n` if `byte mod 7 == 0`, else `Try again\n`. |
| APPROVED | interactive | trivia_capital_france | First prints `What's the capital of France?\n` on stdout. Then reads a `\n`-terminated answer (≤ 20 chars). Prints `correct!\n` if the answer is exactly `Paris`, else `wrong\n`. |
| APPROVED | interactive | trivia_largest_planet | First prints `What's the largest planet?\n`. Then reads a `\n`-terminated answer. Prints `correct!\n` if exactly `Jupiter`, else `wrong\n`. |
| APPROVED | interactive | trivia_math | First prints `What's 2+2?\n`. Then reads a decimal `\n`-terminated answer. Prints `correct!\n` if exactly `4`, else `wrong\n`. |
| APPROVED | interactive | balance_check | Reads decimal `0`-`9999` + `\n`. Prints `low\n` if `<100`, `ok\n` if `100`-`999`, `high\n` if `>=1000`. |
| OVERLAP | interactive | weather_report | OVERLAP with menu_selection: same digit→fixed-string-table algorithm; only the output strings differ. Dropped. |
| APPROVED | interactive | tip_calculator | Reads decimal bill `0`-`99` + `\n`. Prints `(bill * 120) / 100` (20% tip, integer division) + `\n`. |
| APPROVED | interactive | tax_calculator | Reads decimal amount `0`-`999` + `\n`. Prints `(amount * 110) / 100` (10% tax, integer division) + `\n`. |
| OVERLAP | interactive | age_in_dog_years | OVERLAP with batch2/arithmetic/mul_by_7: same a*7 algorithm and subrange. Dropped. |
| APPROVED | interactive | simple_login | Reads a `\n`-terminated username, then a `\n`-terminated password (each ≤ 20 chars). Prints `Welcome!\n` if username is exactly `admin` and password is exactly `root`, else `Denied\n`. |
| APPROVED | interactive | survey_two_q | Reads two `\n`-terminated `y`/`n` answers. Prints `Definitely\n` for `y/y`, `Maybe\n` for `y/n`, `Probably not\n` for `n/y`, `Definitely not\n` for `n/n`. |
| OVERLAP | interactive | story_branch_2 | OVERLAP with coin_flip_pseudo (2-agent audit): same byte-parity→2-string-table algorithm. Dropped. |
| APPROVED | interactive | cheer_team | Reads digit `1`-`3` + `\n`. Prints `Go team <N>!\n` exactly three times. |
| APPROVED | interactive | quiz_show_score | Reads three single-digit decimals `0` or `1` (each `\n`-terminated; `1` = correct, `0` = wrong for 3 rounds). Prints `Total: <S>\nGrade: <G>\n`, where `S` is the sum (0-3) and `G` is `A`/`B`/`C`/`F` for `3`/`2`/`1`/`0`. |
| APPROVED | interactive | customer_rating | Reads digit `1`-`5` + `\n`. Prints `Thank you for your <N>-star review!\n`. |
| APPROVED | interactive | clock_set | Reads two decimals on separate lines: hour `0`-`23` then minute `0`-`59`. Prints `Time set to <HH>:<MM>\n` (each zero-padded to 2 digits). |
| APPROVED | interactive | greeting_user_age | Reads a `\n`-terminated name (≤ 20 chars) then a decimal age `0`-`120` + `\n`. Prints `Hello, <name>! You are <age> years old.\n`. |
| APPROVED | interactive | to_do_add | Reads a `\n`-terminated task description (≤ 40 chars). Prints `Added: <task>\n`. |
| OVERLAP | interactive | todo_complete | OVERLAP with to_do_add: identical read-line-then-prefix-and-echo; differs only in the prefix word. Dropped. |
| APPROVED | interactive | shopping_cart_check | Reads decimal price `0`-`999` + `\n` then decimal budget `0`-`999` + `\n`. If `price <= budget` prints `affordable\n`, else prints `over budget by <X>\n` where `X = price - budget`. |
| APPROVED | interactive | number_guess_three_tries | Secret value is `5`. Reads up to 3 decimal guesses `1`-`10` (each `\n`-terminated). After each guess prints `too low\n`, `too high\n`, or `correct!\n` then exits on correct. If 3 wrong guesses, prints `Out of tries. Secret was 5.\n` and exits. |
| APPROVED | interactive | odd_one_out | Reads three decimals (each `\n`-terminated). If exactly two are equal, prints the third (unique) value + `\n`. Otherwise prints `none\n` (covers both all-equal and all-different cases). |
| APPROVED | interactive | chatbot_simple_reply | Reads a `\n`-terminated line ≤ 40 chars. If equals `hi`, prints `Hello!\n`. If equals `bye`, prints `Goodbye!\n`. Otherwise prints `I don't understand.\n`. |
| OVERLAP | interactive | simple_meal_planner | OVERLAP with menu_selection: same digit→fixed-string-table algorithm (subset by N=3). Dropped. |
| APPROVED | interactive | interactive_addition_three | Reads three decimals (each `\n`-terminated). Prints the human-readable expression `<a> + <b> + <c> = <sum>\n`. |
| OVERLAP | interactive | user_choice_length | OVERLAP with batch2/strings/string_length: same line-count algorithm; only the output template differs. Dropped. |
| APPROVED | encoding | hex_dump_line | Reads a `\n`-terminated line ≤ 16 chars. For each byte (excluding `\n`), prints its 2-char lowercase hex, with space separators between bytes, then `\n`. Example: input `hi\n` → output `68 69\n`. Empty input → just `\n`. |
| APPROVED | encoding | binary_dump_line | Reads a `\n`-terminated line ≤ 16 chars. For each byte (excluding `\n`), prints its 8-char binary representation (MSB first), space-separated, then `\n`. |
| APPROVED | encoding | octal_dump_line | Reads a `\n`-terminated line ≤ 16 chars. For each byte (excluding `\n`), prints its 3-char octal representation (zero-padded), space-separated, then `\n`. |
| APPROVED | encoding | decimal_dump_line | Reads a `\n`-terminated line ≤ 16 chars. For each byte (excluding `\n`), prints its decimal value (1-3 chars, no zero padding), space-separated, then `\n`. |
| APPROVED | encoding | ascii_table_printable_32_126 | No input. Prints lines `<code> <char>\n` for each ASCII code 32-126 (printable range, 95 lines total). |
| APPROVED | encoding | run_length_encode_simple | Reads a `\n`-terminated lowercase-letter string ≤ 30 chars (runs of length ≤ 9). Prints run-length encoding as alternating `<letter><count>` concatenated, then `\n`. Example: `aabcccccaaa` → `a2b1c5a3\n`. |
| APPROVED | encoding | run_length_decode_simple | Reads a `\n`-terminated RLE string of alternating `<letter><digit 1-9>` ≤ 30 chars. Prints decoded string + `\n`. Example: `a2b1c5` → `aabccccc\n`. |
| OVERLAP | encoding | base16_encode_short | OVERLAP with ascii_to_hex_concat: same algorithm; differs only in uppercase vs lowercase hex. Dropped (case is an impl-time toggle). |
| OVERLAP | encoding | base16_decode_short | OVERLAP with hex_concat_to_ascii: same algorithm; uppercase vs lowercase input. Dropped. |
| APPROVED | encoding | percent_encode_space | Reads a `\n`-terminated line ≤ 40 chars. Replaces each space byte (` `) with `%20`. Other bytes unchanged. Prints result + `\n`. |
| APPROVED | encoding | percent_decode_space | Reads a `\n`-terminated line ≤ 60 chars (may contain `%20` sequences). Replaces each `%20` triplet with a single space. Other bytes unchanged. Prints result + `\n`. |
| APPROVED | encoding | html_entity_encode_basic | Reads a `\n`-terminated line ≤ 40 chars. Replaces `&` with `&amp;`, `<` with `&lt;`, `>` with `&gt;`. Other bytes unchanged. Prints result + `\n`. |
| APPROVED | encoding | html_entity_decode_basic | Reads a `\n`-terminated line ≤ 80 chars (may contain `&amp;`/`&lt;`/`&gt;` sequences). Replaces each with `&`/`<`/`>` respectively. Other bytes unchanged. Prints result + `\n`. |
| APPROVED | encoding | atbash_cipher | Reads a `\n`-terminated line ≤ 80 chars. For each letter, maps `a↔z`, `b↔y`, ..., `m↔n` (and the same within `A-Z`). Non-letters unchanged. Prints result + `\n`. |
| APPROVED | encoding | nato_phonetic_letter | Reads exactly one byte `A`-`Z` (no `\n` required). Prints the NATO phonetic word for that letter (`Alpha`/`Bravo`/`Charlie`/.../`Zulu`) followed by `\n`. |
| APPROVED | encoding | nato_phonetic_word | Reads a `\n`-terminated NATO phonetic word (one of the 26 standard words, exactly as spelled, capitalized). Prints the corresponding single uppercase letter (`A`-`Z`) + `\n`. |
| APPROVED | encoding | xor_key_07_roundtrip | Reads a `\n`-terminated line ≤ 30 chars. XORs each byte (excluding `\n`) with `0x07`. Outputs the XORed bytes followed by `\n`. (Self-inverse — running twice on the same input yields original.) |
| APPROVED | encoding | checksum_byte_sum | Reads a `\n`-terminated line ≤ 30 chars. Prints the sum of the byte values (excluding `\n`) modulo 256 as decimal + `\n`. |
| APPROVED | encoding | checksum_xor | Reads a `\n`-terminated line ≤ 30 chars. Prints the XOR of all byte values (excluding `\n`) as two lowercase hex chars + `\n`. |
| APPROVED | encoding | parity_byte_compute | Reads exactly 7 ASCII bits (each `0` or `1` byte, all on one `\n`-terminated line, e.g. `1010101\n`). Prints `0\n` if the count of 1s among the 7 input bits is even, `1\n` if odd. (This is the parity bit that, when appended, makes total ones EVEN.) |
| APPROVED | encoding | nibble_dump_hex_colon | Reads a `\n`-terminated line ≤ 16 chars. For each byte (excluding `\n`), prints `<high>:<low>` where `<high>` is the high nibble's hex char and `<low>` is the low nibble's. Entries are space-separated; final `\n`. Example: input `Aa\n` → output `4:1 6:1\n`. |
| APPROVED | encoding | quoted_printable_simple | Reads a `\n`-terminated line ≤ 20 chars. Each byte (excluding `\n`) that is NOT printable ASCII (`0x20`-`0x7e`) becomes `=NN` where `NN` is its 2-char uppercase hex. Printable bytes unchanged. Prints result + `\n`. |
| APPROVED | encoding | count_chars_per_class | Reads a `\n`-terminated line ≤ 80 chars. Prints `digits: <D>\nletters: <L>\nspaces: <S>\nother: <O>\n` where `D`/`L`/`S`/`O` are the counts of digits, letters, spaces, and other byte classes respectively (excluding the terminating `\n`). |
| APPROVED | encoding | csv_split_one_field | Reads a `\n`-terminated CSV line ≤ 60 chars (no embedded commas in fields, no quotes). Prints each comma-separated field on its own line. |
| APPROVED | encoding | tsv_to_csv | Reads a `\n`-terminated TSV line ≤ 60 chars (tab-separated). Outputs the same line with each `\t` replaced by `,`. Final `\n` preserved. |
| APPROVED | encoding | csv_to_tsv | Reads a `\n`-terminated CSV line ≤ 60 chars (no quoted commas). Outputs the same line with each `,` replaced by `\t`. Final `\n` preserved. |
| APPROVED | encoding | ascii_to_hex_concat | Reads a `\n`-terminated line ≤ 20 chars. Prints all bytes (excluding `\n`) as concatenated lowercase hex (no separators) followed by `\n`. Example: `Hi\n` → `4869\n`. |
| APPROVED | encoding | hex_concat_to_ascii | Reads a `\n`-terminated lowercase-hex string ≤ 40 chars (even length). Prints decoded bytes + `\n`. |
| APPROVED | encoding | xor_encrypt_cycling_key | Reads a `\n`-terminated key (`≤ 8 chars`), then a `\n`-terminated message (`≤ 30 chars`). XORs each message byte (excluding terminating `\n`) with `key[i mod key_length]`. Outputs the XOR'd bytes followed by `\n`. |
| OVERLAP | encoding | base16_with_dash_separator | OVERLAP with hex_dump_line: same algorithm; differs only in separator character (dash vs space). Dropped. |
| APPROVED | encoding | ascii_to_morse_letter | Reads exactly one byte (a single lowercase letter `a`-`z` or digit `0`-`9`). Prints the International Morse Code representation using `.` and `-` (no spaces) + `\n`. Example: `a` → `.-\n`; `0` → `-----\n`. |
| APPROVED | encoding | morse_to_ascii_letter | Reads a `\n`-terminated Morse Code sequence (using only `.` and `-`, ≤ 6 chars, one of the 36 lowercase-letter / digit codes). Prints the decoded ASCII byte (no extra `\n`). |
| APPROVED | encoding | nibble_to_base64_char | Reads a decimal `0`-`15` + `\n`. Prints the corresponding base64 alphabet character (`A` for 0, `B` for 1, ..., `P` for 15), followed by `\n`. |
| APPROVED | encoding | emoji_smiley_or_frown | Reads exactly one byte `0` or `1` followed by `\n`. Prints `:)\n` for `1`, `:(\n` for `0`. |
| APPROVED | encoding | byte_class_counts | Reads a `\n`-terminated line ≤ 80 chars. Prints `printable: <P>\ncontrol: <C>\n` where `P` is the count of printable bytes (`0x20`-`0x7e`) and `C` is the count of control bytes (`<0x20` or `0x7f`), all excluding the terminating `\n`. |
| APPROVED | encoding | binary_xor_two_inputs | Reads two `\n`-terminated 8-char binary strings (each on its own line, each is 8 chars of `0`/`1`). Prints their bitwise XOR as an 8-char binary string + `\n`. |
| APPROVED | encoding | binary_and_two_inputs | Same I/O shape as `binary_xor_two_inputs` but prints bitwise AND. |
| APPROVED | encoding | binary_or_two_inputs | Same I/O shape as `binary_xor_two_inputs` but prints bitwise OR. |
| OVERLAP | encoding | ascii_to_decimal_codes | OVERLAP with decimal_dump_line: byte-for-byte identical specification (as the description acknowledged). Dropped. |
| APPROVED | encoding | xxd_style_dump | Reads a `\n`-terminated line ≤ 16 chars. Prints one line: 4-digit zero-padded offset `0000`, two spaces, then hex bytes (lowercase, space-separated, max 16 bytes), then 2 spaces, then the printable ASCII (non-printables as `.`), then `\n`. Example: input `hi\n` → `0000  68 69  hi\n`. |
| APPROVED | state_machines | traffic_light_cycle | Reads digit N `1`-`9` + `\n`. Prints the traffic-light states cycling `Red\nGreen\nYellow\n` (starting with Red), totaling exactly N lines. |
| APPROVED | state_machines | dfa_even_zeros | Reads a `\n`-terminated binary string of `0`/`1` (≤ 30 chars). Prints `1\n` if the count of `0` bytes (excluding `\n`) is even, else `0\n`. |
| APPROVED | state_machines | dfa_odd_ones | Reads a `\n`-terminated binary string of `0`/`1` (≤ 30 chars). Prints `1\n` if the count of `1` bytes (excluding `\n`) is odd, else `0\n`. |
| APPROVED | state_machines | dfa_ends_with_01 | Reads a `\n`-terminated binary string of `0`/`1` (≤ 30 chars). Prints `1\n` if the string ends with the two-byte pattern `01` (immediately before the `\n`), else `0\n`. |
| APPROVED | state_machines | dfa_contains_substring_abc | Reads a `\n`-terminated ASCII string ≤ 40 chars. Prints `1\n` if the string contains the substring `abc` anywhere, else `0\n`. Use a 4-state DFA. |
| APPROVED | state_machines | dfa_starts_a_ends_z | Reads a `\n`-terminated ASCII string of length ≥ 2 ≤ 30 chars. Prints `1\n` if first byte is `a` and last byte (immediately before `\n`) is `z`, else `0\n`. |
| APPROVED | state_machines | mealy_invert_bits | Reads a `\n`-terminated sequence of bits `0`/`1` (≤ 30 chars). For each input bit, outputs the inverted bit (Mealy machine: output depends on input transition). Prints all output bits as one concatenated string + `\n`. |
| APPROVED | state_machines | moore_count_state_mod4 | Reads a `\n`-terminated sequence of bits `0`/`1` (≤ 20 chars). State starts at `0`; each input bit increments state modulo 4. After each input, prints the current state (`0`-`3`); states are space-separated on a single line + `\n`. (Moore machine: output depends on current state.) |
| APPROVED | state_machines | lexer_digit_letter_other | Reads a `\n`-terminated ASCII string ≤ 40 chars. For each byte, prints `D` if digit, `L` if letter, `O` otherwise. All output chars on one line, then `\n`. |
| APPROVED | state_machines | vending_machine_state | Reads digit codes `1`/`2`/`3` (each `\n`-terminated; `1`=nickel(5¢), `2`=dime(10¢), `3`=quarter(25¢)) up to 10 inputs. Accumulates total; as soon as total ≥ 25, prints `Soda dispensed (change: <change>)\n` (where `change = total - 25`) and exits. If 10 inputs reached without 25, prints `Insufficient: <total>\n` and exits. |
| APPROVED | state_machines | matching_parens_depth_track | Reads a `\n`-terminated string of `(` and `)` (≤ 30 chars). Tracks depth starting at 0. After each input char, prints depth as decimal, comma-separated entries on one line + `\n`. Example: `(())` → `1,2,1,0\n`. |
| APPROVED | state_machines | ping_pong_toggle_state | Reads a `\n`-terminated bit string (`0`/`1`, ≤ 20 chars). State starts at `Ping`. On each `1` input, state toggles (`Ping↔Pong`); on each `0`, state stays. After each input, prints the current state + `\n` (one state per line). |
| APPROVED | state_machines | password_state_machine | Reads bytes one per line (`\n`-terminated; one byte per line) until either: state-accumulated last 4 bytes form the string `open` (then prints `Unlocked!\n` and exits) or 10 bytes have been read without forming `open` (then prints `Locked\n` and exits). |
| APPROVED | state_machines | dfa_divisible_by_3 | Reads a `\n`-terminated decimal-digit string ≤ 6 chars representing a non-negative integer N. Prints `1\n` if N is divisible by 3, else `0\n`. Implementation: 3-state DFA on digit stream (state = current N mod 3). |
| APPROVED | state_machines | dfa_divisible_by_2 | Reads a `\n`-terminated decimal-digit string ≤ 6 chars. Prints `1\n` if the represented N is divisible by 2, else `0\n`. Implementation: track last-digit parity (no need for multi-state). |
| APPROVED | state_machines | dfa_divisible_by_5 | Reads a `\n`-terminated decimal-digit string ≤ 6 chars. Prints `1\n` if the represented N is divisible by 5 (last digit is `0` or `5`), else `0\n`. |
| APPROVED | state_machines | nfa_a_or_b_then_c | Reads a `\n`-terminated string of exactly 2 lowercase letters. Prints `1\n` if the string matches the regex `(a|b)c` (first byte is `a` or `b`, second byte is `c`), else `0\n`. Demonstrates a simple NFA / regex matcher. |
| APPROVED | state_machines | regex_star_a | Reads a `\n`-terminated string of lowercase letters ≤ 30 chars. Prints `1\n` if the string matches `a*` (zero or more `a`s, no other characters), else `0\n`. |
| APPROVED | state_machines | regex_aa_repeated | Reads a `\n`-terminated string of lowercase letters ≤ 30 chars. Prints `1\n` if the string matches `(aa)*` (zero or more `aa` pairs, even count of `a`s, no other characters), else `0\n`. |
| APPROVED | state_machines | dfa_third_last_is_one | Reads a `\n`-terminated bit string of length ≥ 3, ≤ 30 chars. Prints `1\n` if the third-to-last bit (i.e. the bit two positions before the final bit, before `\n`) is `1`, else `0\n`. Implementation: 8-state DFA tracking last 3 bits. |

## Batch 7 — geometry + simulation + puzzles (92 approved + 4 overlap + 3 clarified)

Categories: geometry (27 net of 30), simulation (27 net of 28), puzzles (41 net).
CR-ist found 4 overlaps + 3 UNCLEAR (clarified in place). 92 APPROVED. Bookkeeping: section header said 100 rows but actual is 99 (simulation 28 not 30).

| status | category | name | description |
|---|---|---|---|
| APPROVED | geometry | manhattan_distance | Reads 4 decimals `x1 y1 x2 y2` (each own line). Prints `|x2-x1| + |y2-y1|` as decimal + `\n`. |
| APPROVED | geometry | chebyshev_distance | Reads 4 decimals (each own line). Prints `max(|x2-x1|, |y2-y1|)` + `\n`. |
| APPROVED | geometry | euclidean_distance_floor | Reads 4 decimals `x1 y1 x2 y2` (each `0`-`9`, own line). Prints `floor(sqrt((x2-x1)^2 + (y2-y1)^2))` as decimal + `\n`. Squared distance ≤ 162, so integer sqrt via linear scan (`k` while `k² <= d`) stays trivially within compile budget. |
| APPROVED | geometry | dot_product_2d | Reads 4 decimals `a b c d` (each own line) representing vectors `(a,b)` and `(c,d)`. Prints `a*c + b*d` as signed decimal + `\n`. |
| APPROVED | geometry | cross_product_2d_scalar | Reads 4 decimals (each own line) representing two 2D vectors. Prints the scalar cross product `a*d - b*c` as signed decimal + `\n`. |
| APPROVED | geometry | midpoint_2d | Reads 4 decimals `x1 y1 x2 y2` (each own line). Prints `<mx> <my>\n` where `mx = (x1+x2)/2` and `my = (y1+y2)/2` (floor division). |
| APPROVED | geometry | is_origin | Reads 2 decimals `x y` (each own line). Prints `1\n` if both are `0`, else `0\n`. |
| APPROVED | geometry | is_on_x_axis | Reads 2 decimals (each own line). Prints `1\n` if `y == 0`, else `0\n`. |
| APPROVED | geometry | is_on_y_axis | Reads 2 decimals (each own line). Prints `1\n` if `x == 0`, else `0\n`. |
| APPROVED | geometry | is_collinear_3 | Reads 6 decimals representing 3 points `(x1,y1) (x2,y2) (x3,y3)` (each coordinate on its own line). Prints `1\n` if collinear (i.e. `(x2-x1)*(y3-y1) - (y2-y1)*(x3-x1) == 0`), else `0\n`. |
| APPROVED | geometry | signed_triangle_area_2x | Reads 6 decimals (3 vertices, each coord own line). Prints `x1*(y2-y3) + x2*(y3-y1) + x3*(y1-y2)` as signed decimal + `\n` (this is exactly 2× the signed area). |
| APPROVED | geometry | rectangle_area | Reads two decimals `width` `height` (each own line, `0`-`100`). Prints `width * height` + `\n`. |
| APPROVED | geometry | rectangle_perimeter | Reads `width` `height` (each own line, `0`-`100`). Prints `2 * (width + height)` + `\n`. |
| APPROVED | geometry | circle_area_approx | Reads decimal radius `0`-`9` + `\n`. Prints `(r * r * 314) / 100` (integer approximation of π·r²) + `\n`. |
| APPROVED | geometry | circle_circumference_approx | Reads decimal radius `0`-`9` + `\n`. Prints `(2 * r * 314) / 100` (integer approximation of 2πr) + `\n`. |
| OVERLAP | geometry | square_area | OVERLAP with batch1/arithmetic/square_small: same read-N-print-N² algorithm; geometric framing only. Dropped. |
| APPROVED | geometry | square_perimeter | Reads decimal side `0`-`100` + `\n`. Prints `4 * side` + `\n`. |
| OVERLAP | geometry | cube_volume | OVERLAP with batch1/arithmetic/cube_small: same read-N-print-N³ algorithm. Dropped. |
| APPROVED | geometry | cube_surface_area | Reads decimal side `0`-`20` + `\n`. Prints `6 * side * side` + `\n`. |
| APPROVED | geometry | is_point_inside_rect | Reads 6 decimals (each own line): point `x y` then rect `xmin ymin xmax ymax`. Prints `1\n` if `xmin <= x <= xmax` and `ymin <= y <= ymax`, else `0\n`. |
| APPROVED | geometry | is_point_inside_circle | Reads 5 decimals (each own line): point `x y`, center `cx cy`, radius `r` (all `0`-`50`). Prints `1\n` if `(x-cx)^2 + (y-cy)^2 <= r^2`, else `0\n`. |
| APPROVED | geometry | is_right_triangle_from_sides | Reads 3 decimals `a b c` (each own line, each `1`-`50`) representing triangle side lengths in any order. Prints `1\n` if some permutation satisfies `a^2 + b^2 == c^2`, else `0\n`. |
| APPROVED | geometry | is_isosceles | Reads 3 decimals (each on own line) representing triangle side lengths. Prints `1\n` if at least two of the three sides are equal (i.e. equilateral triangles also qualify), else `0\n`. |
| APPROVED | geometry | is_equilateral | Reads 3 decimals. Prints `1\n` if all three sides equal, else `0\n`. |
| APPROVED | geometry | is_scalene | Reads 3 decimals. Prints `1\n` if all three sides are distinct, else `0\n`. |
| APPROVED | geometry | perpendicular_vectors_check | Reads 4 decimals (two 2D vectors). Prints `1\n` if their dot product is `0` (perpendicular), else `0\n`. |
| APPROVED | geometry | parallel_vectors_check | Reads 4 decimals (two 2D vectors). Prints `1\n` if their scalar cross product is `0` (parallel or anti-parallel), else `0\n`. |
| APPROVED | geometry | slope_int_or_undefined | Reads 4 decimals `x1 y1 x2 y2` (each own line, signed). If `x1 == x2`, prints `undefined\n`. Otherwise prints `(y2 - y1) / (x2 - x1)` as signed integer division + `\n`. |
| OVERLAP | geometry | is_within_squared_distance | OVERLAP with is_point_inside_circle: same squared-distance vs squared-threshold kernel; only parameter labeling differs. Dropped. |
| APPROVED | geometry | counts_inside_unit_circle_grid_3x3 | No input. Counts how many of the 9 lattice points `(i,j)` for `i,j ∈ {-1,0,1}` satisfy `i^2 + j^2 <= 1`. Prints the count as decimal + `\n` (answer: 5). |
| APPROVED | simulation | rule_30_one_step | Reads an 8-char binary string `0`/`1` + `\n` (initial cellular state). Computes the next generation using Wolfram Rule 30 with periodic boundary conditions (cell `i` depends on cells `i-1`, `i`, `i+1` modulo 8). Prints the resulting 8-char binary string + `\n`. |
| APPROVED | simulation | rule_90_one_step | Same I/O as `rule_30_one_step` but applies Rule 90. |
| APPROVED | simulation | rule_110_one_step | Same I/O but Rule 110. |
| APPROVED | simulation | rule_184_one_step | Same I/O but Rule 184 (traffic-flow CA). |
| APPROVED | simulation | rule_30_n_steps | Reads an 8-char binary string + `\n`, then a digit N `1`-`5` + `\n`. Prints N successive generations of Rule 30 (one per line, each an 8-char binary string + `\n`). |
| APPROVED | simulation | rule_90_n_steps | Same shape, Rule 90. |
| APPROVED | simulation | rule_110_n_steps | Same shape, Rule 110. |
| APPROVED | simulation | game_of_life_one_step_5x5 | Reads a 5×5 binary grid: 5 lines, each 5 chars of `0`/`1` + `\n`. Applies one Conway's Game of Life step with dead-boundary (cells outside grid treated as 0). Prints the resulting 5×5 grid in the same format. |
| APPROVED | simulation | game_of_life_blinker_3 | No input. Prints 3 successive generations of a fixed blinker pattern on a 5×5 grid (initial state: middle row `00100\n00100\n00100\n` framed by blank rows). Each generation is 5 lines of 5 chars + `\n`; generations separated by an empty line `\n`. |
| APPROVED | simulation | game_of_life_glider_5 | No input. Prints 5 successive generations of a fixed glider pattern on a 7×7 grid. Each generation is 7 lines of 7 chars + `\n`; generations separated by an empty line. |
| APPROVED | simulation | langton_ant_5_steps | No input. Simulates 5 steps of Langton's ant on a 7×7 grid (all cells initially white `.`), starting at center facing up. Prints the resulting grid (7 lines of 7 chars, where `.`=white, `#`=black) + `\n`. |
| APPROVED | simulation | langton_ant_10_steps | No input. Same as `langton_ant_5_steps` but 10 steps. |
| APPROVED | simulation | brownian_walk_1d | Reads digit N `1`-`9` + `\n`, then N raw bytes. Starts at position 0. For each byte, advances position by `+1` if byte value is even, `-1` if odd. Prints the final position as signed decimal + `\n`. |
| APPROVED | simulation | random_walk_grid_2d | Reads digit N `1`-`9` + `\n`, then N raw bytes. Starts at `(0,0)`. For each byte, moves according to `byte mod 4`: `0`=up (`y+1`), `1`=right (`x+1`), `2`=down (`y-1`), `3`=left (`x-1`). Prints final `<x> <y>\n`. |
| APPROVED | simulation | bouncing_ball_1d | Reads `pos` `0`-`9`, `velo` `-3` to `3` (signed), `steps` `1`-`9` (each own line). The ball moves on positions `0..9`; on hitting position `0` or `9`, velocity reverses sign. Prints the position after each of the `steps` steps, one per line. |
| APPROVED | simulation | bouncing_ball_2d | Same as `bouncing_ball_1d` but in 2D: reads `x` `y` `vx` `vy` `steps`. Both axes bounce independently at `[0,9]`. Prints `<x> <y>\n` after each step. |
| APPROVED | simulation | snake_advance_one_step | Reads a `\n`-terminated string of length `1`-`5` representing the snake's body positions on a 1D 10-cell line (`H` head, `B` body); positions separated by `.` for empty cells. Then reads one direction byte `L` or `R` + `\n`. Moves the head by 1 in that direction (no wrap; clamp to bounds); body follows. Prints the new state + `\n`. |
| APPROVED | simulation | tetris_print_empty_board_6x10 | No input. Prints an empty 6-row × 10-column Tetris board: 6 lines of `..........\n`. |
| APPROVED | simulation | tetris_drop_piece_o | Reads column `0`-`8` + `\n`. Drops an O-piece (2×2 square) at that column into an otherwise empty 6×10 board. Prints the resulting board (6 lines of 10 chars each, `.` empty, `#` occupied). |
| APPROVED | simulation | forest_fire_spread_3x3 | Reads a 3×3 grid: 3 lines of 3 chars each, where chars are `T` (tree), `F` (fire), `.` (empty). Applies one step: each `F` stays `F`, each `T` adjacent (4-neighborhood, no diagonal) to an `F` becomes `F`, all other cells unchanged. Prints the new 3×3 grid. |
| APPROVED | simulation | predator_prey_one_step | Reads `prey` `0`-`50`, `pred` `0`-`20` (each own line). Applies one Lotka-Volterra-inspired step: `prey' = prey + prey/4 - pred`, `pred' = pred + prey/10 - pred/4` (integer divisions, clamp at 0). Prints `<prey'> <pred'>\n`. |
| APPROVED | simulation | epidemic_si_one_step | Reads `S` `0`-`99`, `I` `0`-`99` (each own line). Applies one SI-model step: `new_infections = S * I / 100` (clamp to remaining S), `S' = S - new_infections`, `I' = I + new_infections`. Prints `<S'> <I'>\n`. |
| APPROVED | simulation | bacteria_double_n_times | Reads `pop` `1`-`99` (own line), `N` `0`-`6` (own line). Prints `pop * 2^N` as decimal + `\n`. |
| APPROVED | simulation | radioactive_decay_half_n | Reads `count` `0`-`9999` (own line), `N` `0`-`9` (own line). Prints `count / 2^N` (integer halving N times) as decimal + `\n`. |
| APPROVED | simulation | queue_advance_n_customers | Reads digit N `1`-`9` + `\n`. Prints N lines `serving customer K\n` for `K = 1..N`. |
| OVERLAP | simulation | cellular_avg_3 | OVERLAP with batch2/arithmetic/avg_three: identical floor((a+b+c)/3) algorithm and I/O contract. Dropped. |
| APPROVED | simulation | percolation_2x2 | Reads a 2×2 binary grid: 2 lines of 2 chars `0`/`1` each (1 = open, 0 = blocked). Prints `1\n` if there's a 4-connected path from any top-row open cell to any bottom-row open cell, else `0\n`. |
| APPROVED | simulation | flock_1d_step | Reads digit N `2`-`5` + `\n`, then N decimals `0`-`9` (each own line) representing positions on a 1D line. Computes the mean position (floor). Then each cell moves +1 if it's below mean, -1 if above, unchanged if equal. Prints the new positions, one per line. |
| APPROVED | puzzles | n_queens_4_count | No input. Prints the number of distinct solutions to the 4-queens problem (`2`) + `\n`. |
| OVERLAP | puzzles | n_queens_5_count | OVERLAP with n_queens_4_count + eight_queens_solution_count (3-agent audit): exceeds the 2-bound-variant precedent (fizzbuzz_to_30). Dropped; canonical small (4) and famous (8) cases retained. |
| OVERLAP | puzzles | n_queens_6_count | OVERLAP with n_queens_4_count + eight_queens_solution_count (3-agent audit): exceeds the 2-bound-variant precedent. Dropped. |
| APPROVED | puzzles | eight_queens_solution_count | No input. Prints `92` + `\n` (the number of distinct solutions to the 8-queens problem). |
| APPROVED | puzzles | eight_queens_one_solution | No input. Prints one valid 8-queens solution as 8 column indices `0`-`7` for rows 0..7, space-separated, then `\n`. (Use a canonical first solution.) |
| APPROVED | puzzles | magic_square_check_3x3 | Reads 9 decimals (3×3 row-major, each on own line). Prints `1\n` if all 3 rows, all 3 columns, and both diagonals have the same sum, else `0\n`. |
| APPROVED | puzzles | magic_square_fill_missing | Reads 9 decimals (3×3 row-major, each on own line) representing a known-valid 3×3 magic square with EXACTLY ONE cell replaced by `0` (the missing value). Prints the missing value as decimal + `\n`. |
| APPROVED | puzzles | magic_constant_for_n | Reads digit N `3`-`9` + `\n`. Prints `N * (N^2 + 1) / 2` (the magic constant for an N×N magic square containing `1..N²`) + `\n`. |
| APPROVED | puzzles | sudoku_row_check_9 | Reads 9 decimals `1`-`9` (each on own line). Prints `1\n` if all 9 values are distinct (a valid Sudoku row/column/block), else `0\n`. |
| APPROVED | puzzles | sudoku_full_validation | Reads 9 lines, each 9 decimals (separated by spaces) representing a 9×9 Sudoku grid filled with `1`-`9`. Prints `1\n` if all 9 rows AND all 9 columns AND all 9 3×3 boxes contain `1..9` (every row/col/box has 9 distinct values), else `0\n`. |
| APPROVED | puzzles | tic_tac_toe_winner | Reads 3 lines of 3 chars each (`X`, `O`, or `.`) representing a tic-tac-toe board. Prints `X\n` if X has won (three in a row/col/diag), `O\n` if O has won, else `none\n`. (Assume at most one side has won.) |
| APPROVED | puzzles | tic_tac_toe_board_full | Reads 3 lines of 3 chars each. Prints `1\n` if no `.` chars remain (board is full), else `0\n`. |
| APPROVED | puzzles | tic_tac_toe_simulate_moves | Reads digit N `1`-`9` + `\n`, then N moves (each one digit `0`-`8` on its own line, indicating cell position 0=top-left, row-major). Players alternate starting with `X`. Prints the final 3×3 board (3 lines of 3 chars each, `.` for unmoved cells). |
| APPROVED | puzzles | tower_of_hanoi_count | Reads digit N `1`-`9` + `\n`. Prints `2^N - 1` (minimum moves) + `\n`. |
| APPROVED | puzzles | tower_of_hanoi_print_moves_3 | No input. Prints all 7 moves for the 3-disk Tower of Hanoi (from peg `A` to peg `C` using `B`), one per line, formatted `<disk>: <src>-><dst>\n`. Example first move: `1: A->C\n`. |
| APPROVED | puzzles | tower_of_hanoi_print_moves_4 | No input. Same format as `tower_of_hanoi_print_moves_3` but for 4 disks (15 moves total). |
| APPROVED | puzzles | word_anagram_check | Reads two `\n`-terminated lowercase words (each ≤ 10 chars). Prints `1\n` if they are anagrams (same multiset of letters), else `0\n`. |
| APPROVED | puzzles | permutation_check_n | Reads digit N `1`-`9` + `\n`, then N decimals (each own line), then another N decimals. Prints `1\n` if the second N-tuple is a permutation of the first (same multiset), else `0\n`. |
| APPROVED | puzzles | arithmetic_progression_check_5 | Reads exactly 5 signed decimals (each own line). Prints `1\n` if they form an arithmetic progression (constant difference between consecutive elements), else `0\n`. |
| APPROVED | puzzles | geometric_progression_check_4 | Reads exactly 4 decimals each `1`-`50` (own line). Prints `1\n` if they form a geometric progression with integer common ratio `>= 2` (i.e. `a[i+1] = a[i] * r` for some integer `r >= 2`), else `0\n`. |
| APPROVED | puzzles | fibonacci_5_check | Reads exactly 5 decimals (each own line). Prints `1\n` if they match the first 5 Fibonacci values `0 1 1 2 3` exactly in order, else `0\n`. |
| APPROVED | puzzles | find_missing_arith_progression | Reads exactly 4 decimals (each own line) with the value `0` representing a single missing element of a 4-element arithmetic progression. The remaining 3 values are in their correct AP positions; the `0` is the placeholder. Prints the missing value as decimal + `\n`. |
| APPROVED | puzzles | find_missing_geom_progression | Reads exactly 4 decimals `1`-`50` with one being `0` (the missing entry) of a 4-element geometric progression with integer common ratio `>= 2`. Prints the missing value + `\n`. |
| APPROVED | puzzles | counting_squares_2x2 | No input. Prints `5\n` (the number of squares in a 2×2 lattice grid: four unit squares + one 2×2 square). |
| APPROVED | puzzles | counting_squares_3x3 | No input. Prints `14\n` (number of squares in a 3×3 lattice grid: 9 unit + 4 of side 2 + 1 of side 3). |
| APPROVED | puzzles | counting_rectangles_3x3 | No input. Prints `36\n` (number of rectangles in a 3×3 lattice grid). |
| APPROVED | puzzles | coin_change_count_small | Reads decimal amount `1`-`20` + `\n`. Prints the number of distinct ways to make `amount` cents using coins of denominations `{1, 5, 10}` (order doesn't matter) + `\n`. |
| APPROVED | puzzles | eight_puzzle_check_solved | Reads 9 decimals (each `0`-`8`, own line) representing a 3×3 8-puzzle state (0 = blank). Prints `1\n` if it equals the solved state `1 2 3 4 5 6 7 8 0` (row-major), else `0\n`. |
| APPROVED | puzzles | fifteen_puzzle_check_solved | Reads 16 decimals (each `0`-`15`, own line) representing a 4×4 15-puzzle state (0 = blank). Prints `1\n` if it equals the solved state `1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 0` (row-major), else `0\n`. |
| APPROVED | puzzles | cryptarithm_one_plus_one | Reads exactly 3 decimal digits `a b c` (each `0`-`9`, own line). Prints `1\n` if `a + b == c` (i.e. the cryptarithm `a + b = c` is satisfied), else `0\n`. |
| APPROVED | puzzles | river_crossing_count_classic | No input. Prints `7\n` (the minimum number of trips for the classic farmer-wolf-goat-cabbage river crossing puzzle). |
| APPROVED | puzzles | bishop_attack_check | Reads 4 decimals `r1 c1 r2 c2` (each `0`-`7`, own line) — the two bishops' chessboard positions. Prints `1\n` if they're on the same diagonal (i.e. `|r1-r2| == |c1-c2|`), else `0\n`. |
| APPROVED | puzzles | rook_attack_check | Reads 4 decimals `r1 c1 r2 c2` (each `0`-`7`, own line). Prints `1\n` if they're on the same row or same column, else `0\n`. |
| APPROVED | puzzles | knight_attack_check | Reads 4 decimals `r1 c1 r2 c2` (each `0`-`7`, own line). Prints `1\n` if they're one knight's move apart (i.e. `(|Δr|, |Δc|) == (1,2)` or `(2,1)`), else `0\n`. |
| APPROVED | puzzles | queen_attack_check | Reads 4 decimals `r1 c1 r2 c2` (each `0`-`7`, own line). Prints `1\n` if same row OR same column OR same diagonal, else `0\n`. |
| APPROVED | puzzles | king_attack_check | Reads 4 decimals `r1 c1 r2 c2` (each `0`-`7`, own line). Prints `1\n` if `max(|r1-r2|, |c1-c2|) == 1` (king's move neighbors), else `0\n`. |
| APPROVED | puzzles | pawn_white_move_count | Reads 2 decimals `r c` (each `0`-`7`, own line) — a white pawn's position. Prints the number of legal forward moves (`1` from a non-starting row, `2` from row 6, `0` from row 0). |
| APPROVED | puzzles | is_chessboard_color | Reads 2 decimals `r c` (each `0`-`7`, own line). Prints `0\n` if the square is "white" (i.e. `(r + c)` is even with a8/`r=0,c=0` treated as white), else `1\n`. |
| APPROVED | puzzles | eight_queens_attack_pair_count | Reads exactly 8 decimals (each `0`-`7`, own line) representing the column of a queen for each row 0..7. Prints the count of pairs `(i, j)` with `i < j` such that queens on rows i and j attack each other (same column, or `|rows[i] - rows[j]| == |i - j|`) + `\n`. |
| APPROVED | puzzles | dragon_curve_3_iterations | No input. Prints the heighway-dragon L/R turn sequence after exactly 3 paper-fold iterations, where `L` denotes a left turn and `R` denotes a right turn. The 3rd-iteration sequence has length `2^3 - 1 = 7`. Convention: start with a single `L` (1st iteration), and each next iteration appends `L` then the reverse-and-swap of the prior sequence. This yields iteration-3 = `LLRLLRR`. Output is exactly `LLRLLRR\n`. |
| APPROVED | puzzles | partition_count_n | Reads digit N `1`-`9` + `\n`. Prints the number of integer partitions of N (e.g. `p(4) = 5`) + `\n`. |

## Batch 8 — parsing + graphics_ascii + cryptography + memory_layout (96 approved + 4 overlap)

Categories: parsing (29 net), graphics_ascii (33 net), cryptography (24 net), memory_layout (10 net).
CR-ist found 4 overlaps; 96 APPROVED.

| status | category | name | description |
|---|---|---|---|
| APPROVED | parsing | parse_integer_echo | Reads a `\n`-terminated unsigned decimal `0`-`999999` and prints it back as decimal + `\n`. Round-trip parse → integer → print. |
| APPROVED | parsing | parse_signed_integer_echo | Reads a `\n`-terminated signed decimal `-9999`..`9999` (may have leading `-` or `+`) and prints the canonical signed form + `\n` (no leading `+`). |
| APPROVED | parsing | eval_simple_expr_add | Reads `<a>+<b>` + `\n` where `a` and `b` are single digits `0`-`9`. Prints `a + b` as decimal + `\n`. |
| APPROVED | parsing | eval_simple_expr_sub | Reads `<a>-<b>` + `\n` (single digits). Prints `a - b` (signed) + `\n`. |
| APPROVED | parsing | eval_simple_expr_mul | Reads `<a>*<b>` + `\n` (single digits). Prints `a * b` + `\n`. |
| APPROVED | parsing | eval_two_op_expr | Reads `<a><op><b>` + `\n` where `op` is one of `+`, `-`, `*` and `a`, `b` are single digits. Prints the result + `\n`. |
| APPROVED | parsing | eval_three_op_lr | Reads `<a><op1><b><op2><c>` + `\n` (single digits, `op` ∈ `+`/`-`/`*`). Evaluates strictly left-to-right (no precedence) and prints the result + `\n`. |
| APPROVED | parsing | eval_three_op_precedence | Reads `<a><op1><b><op2><c>` + `\n` (single digits, `op` ∈ `+`/`-`/`*`). Applies standard precedence (`*` before `+`/`-`) and prints the result + `\n`. |
| APPROVED | parsing | tokenize_split_on_whitespace | Reads a `\n`-terminated line ≤ 40 chars. Splits on runs of whitespace (`' '`, `'\t'`) and prints each non-empty token on its own line. |
| APPROVED | parsing | tokenize_split_on_char | Reads exactly one separator byte + `\n`, then a `\n`-terminated line ≤ 40 chars. Splits the line on the separator byte and prints each token (including empty) on its own line. |
| APPROVED | parsing | parse_hex_color | Reads `#RRGGBB\n` (exactly 7 bytes + `\n`, lowercase hex). Prints `R: <r>\nG: <g>\nB: <b>\n` where `r`, `g`, `b` are decimal values `0`-`255`. |
| APPROVED | parsing | parse_date_iso | Reads `YYYY-MM-DD\n` (10 bytes + `\n`). Prints `Year: <Y>\nMonth: <M>\nDay: <D>\n` with no leading zeros. |
| APPROVED | parsing | parse_time_hhmm | Reads `HH:MM\n` (5 bytes + `\n`). Prints `<H>:<M>\n` with no leading zeros (e.g. `09:05` → `9:5\n`). |
| APPROVED | parsing | parse_phone_simple | Reads `XXX-XXX-XXXX\n` (12 bytes + `\n`, dashes at positions 3 and 7). Prints the 10 digits concatenated (no dashes) + `\n`. |
| APPROVED | parsing | parse_url_protocol | Reads `<proto>://<rest>\n` (proto is `1`-`8` lowercase letters). Prints the protocol + `\n`. |
| APPROVED | parsing | parse_email_at | Reads `<user>@<domain>\n` (≤ 30 chars total, exactly one `@`). Prints `<user>\n<domain>\n`. |
| APPROVED | parsing | parse_yaml_kv_simple | Reads `<key>: <value>\n` (single colon-space separator; key is letters only, value any byte). Prints `<key>\n<value>\n`. |
| APPROVED | parsing | parse_json_int | Reads `{"x":<num>}\n` where `<num>` is a decimal `0`-`9999`. Prints `<num>` + `\n`. |
| APPROVED | parsing | parse_json_string | Reads `{"s":"<str>"}\n` where `<str>` is any ASCII bytes (no escapes, no embedded `"`). Prints `<str>` + `\n`. |
| APPROVED | parsing | parse_json_bool | Reads `{"b":true}\n` or `{"b":false}\n`. Prints `1\n` for `true`, `0\n` for `false`. |
| APPROVED | parsing | parse_decimal_list_sum | Reads a `\n`-terminated comma-separated list of decimals (each `0`-`99`, up to 10 entries). Prints the sum + `\n`. |
| APPROVED | parsing | parse_decimal_list_max | Reads same format as `parse_decimal_list_sum`. Prints the maximum + `\n`. |
| APPROVED | parsing | parse_dimensions | Reads `WxH\n` where `W` and `H` are decimals `0`-`99`. Prints `W * H` + `\n`. |
| APPROVED | parsing | parse_version_string | Reads `v<MAJOR>.<MINOR>.<PATCH>\n` where each segment is `0`-`99`. Prints `<MAJOR> <MINOR> <PATCH>\n` space-separated. |
| APPROVED | parsing | parse_rgb_to_grayscale | Reads `R,G,B\n` (each `0`-`255`, decimals separated by commas). Prints `floor((R*30 + G*59 + B*11) / 100)` as decimal + `\n`. |
| APPROVED | parsing | parse_simple_assignment | Reads `<var>=<value>\n` where `var` is a single lowercase letter and `value` is a decimal `0`-`999`. Prints `<var> is <value>\n`. |
| APPROVED | parsing | parse_currency_dollars_cents | Reads `$<D>.<CC>\n` where `D` is decimal `0`-`99` (no zero pad) and `CC` is exactly 2 decimal digits. Prints `D * 100 + CC` (total cents) + `\n`. |
| OVERLAP | parsing | parse_path_dir_file | OVERLAP with parse_email_at: same single-delimiter-split-and-print-two-parts algorithm; only the delimiter differs. Dropped. |
| APPROVED | parsing | parse_signed_hex | Reads `[+-]?0x<HH>\n` (optional sign byte then `0x` then exactly 2 lowercase hex chars). Prints the signed decimal value `-255`..`255` + `\n`. |
| APPROVED | parsing | parse_unit_value | Reads `<num><unit>\n` where `num` is decimal `0`-`99` and `unit` is exactly one byte `s` (seconds), `m` (minutes), or `h` (hours). Prints `num` converted to seconds as decimal + `\n`. |
| APPROVED | graphics_ascii | print_house_3 | No input. Prints a fixed 3-line ASCII house: line 1 ` /\ `, line 2 `/__\`, line 3 `|  |`, each + `\n`. |
| APPROVED | graphics_ascii | print_house_5 | No input. Prints a fixed 5-line ASCII house (taller and wider than `print_house_3`): line 1 `  /\  `, line 2 ` /  \ `, line 3 `/____\`, line 4 `|    |`, line 5 `|____|`, each + `\n`. |
| APPROVED | graphics_ascii | print_christmas_tree_5 | No input. Prints a fixed 5-row centered Christmas tree of `*` (rows of width 1,3,5,7,9 centered in a 9-col field with leading spaces). |
| APPROVED | graphics_ascii | print_christmas_tree_7 | No input. Same shape as `print_christmas_tree_5` but with 7 rows (widths 1,3,5,7,9,11,13 in a 13-col field). |
| APPROVED | graphics_ascii | print_star_5_point | No input. Prints a fixed 5-row 5-pointed star ASCII art (centered on 9-col field, using `*` and spaces). |
| APPROVED | graphics_ascii | print_arrow_right_short | No input. Prints `--->\n`. |
| OVERLAP | graphics_ascii | print_arrow_left_short | OVERLAP with print_arrow_right_short: directional mirror of the same 4-char fixed-string print (4-agent audit). Dropped. |
| APPROVED | graphics_ascii | print_arrow_up_3 | No input. Prints a fixed 3-line upward arrow (`/\`, `||`, `||`), each + `\n`. |
| APPROVED | graphics_ascii | print_arrow_down_3 | No input. Prints a fixed 3-line downward arrow (`||`, `||`, `\/`), each + `\n`. |
| APPROVED | graphics_ascii | print_smiley_face_static | No input. Prints `:)\n`. (Distinct from `emoji_smiley_or_frown` which reads input first.) |
| OVERLAP | graphics_ascii | print_frown_face_static | OVERLAP with print_smiley_face_static: 2-char content variant below threshold. Dropped. |
| OVERLAP | graphics_ascii | print_wink_face_static | OVERLAP with print_smiley_face_static: 2-char content variant below threshold. Dropped. |
| APPROVED | graphics_ascii | print_heart_3 | No input. Prints a 3-row ASCII heart shape using `*`, e.g. line 1 ` * *`, line 2 `*****`, line 3 ` *** `, each + `\n`. |
| APPROVED | graphics_ascii | print_filled_diamond_5 | No input. Prints a 5-row filled diamond of `*` centered in a 5-col field: rows ` * `, `***`, `*****` (truncated to 5-col), `***`, ` * ` — actually use rows widths 1,3,5,3,1 centered on width-5 grid with leading spaces. |
| APPROVED | graphics_ascii | print_filled_diamond_7 | No input. Same shape as `print_filled_diamond_5` but 7-row (widths 1,3,5,7,5,3,1 on 7-col grid). |
| APPROVED | graphics_ascii | print_diamond_outline_5 | No input. Prints a 5-row outline-only diamond: rows ` * `, `* *`, ` * ` for top half mirrored... wait the precise pattern: row 1 `  *  `, row 2 ` * * `, row 3 `*   *`, row 4 ` * * `, row 5 `  *  ` (5×5 grid, only outline cells are `*`, others are space). |
| OVERLAP | graphics_ascii | print_triangle_right_aligned_5 | OVERLAP with spaces_then_stars: fixed-N=5 specialization of the parameterized right-aligned triangle (4-agent audit). Dropped. |
| APPROVED | graphics_ascii | print_box_with_text | Reads a `\n`-terminated line ≤ 10 chars. Prints a 3-row box around the text: top row `+<dashes>+\n`, middle row `| <text padded to 10 chars> |\n`, bottom row `+<dashes>+\n`. Box width is fixed (text padded with trailing spaces to 10 chars, total width 14). |
| APPROVED | graphics_ascii | print_table_2x3 | No input. Prints a fixed 2-row × 3-column ASCII table with `+`, `-`, `|` separators and fixed contents (`Name` / `Age` / `City` headers + one data row `Alice` / `30` / `Paris`). |
| APPROVED | graphics_ascii | print_chess_pawn | No input. Prints a multi-line ASCII chess pawn (3 lines, e.g. ` ○ \n /_\\\n |_|`). |
| APPROVED | graphics_ascii | print_chess_king | No input. Prints a multi-line ASCII chess king (4 lines, with `+`, `|`, `_`). |
| APPROVED | graphics_ascii | print_chess_queen | No input. Prints a multi-line ASCII chess queen (4 lines, distinct shape from king). |
| APPROVED | graphics_ascii | print_chess_bishop | No input. Prints a multi-line ASCII chess bishop (4 lines). |
| APPROVED | graphics_ascii | print_chess_knight | No input. Prints a multi-line ASCII chess knight (4 lines, e.g. with `/\\`). |
| APPROVED | graphics_ascii | print_chess_rook | No input. Prints a multi-line ASCII chess rook (4 lines, like a tower). |
| APPROVED | graphics_ascii | print_dollar_sign_5x5 | No input. Prints a fixed 5×5 ASCII `$` sign using `*` and spaces. |
| APPROVED | graphics_ascii | print_circle_radius_3 | No input. Prints a rasterized circle of radius 3 centered on a 7×7 grid: each cell is `*` if `i² + j² <= 9` (with `i, j` from `-3` to `3`), else `.`. |
| APPROVED | graphics_ascii | print_circle_radius_4 | No input. Same construction as `print_circle_radius_3` but radius 4 on a 9×9 grid. |
| APPROVED | graphics_ascii | print_sin_wave_one_period | No input. Prints a 5-row × 20-column ASCII approximation of one full sine wave period using `*` for plot points and `.` for empty. Use the formula `y = round(2 * sin(2π * x / 20)) + 2` for `x = 0..19` and plot `*` at `(y, x)`. |
| APPROVED | graphics_ascii | print_bar_chart_v_3 | Reads 3 decimals each `0`-`5` (own line). Prints a 5-row × 3-col vertical bar chart: for each column `i`, `*` for rows ≥ `5 - input_i`, `.` otherwise. |
| APPROVED | graphics_ascii | print_bar_chart_v_5 | Reads 5 decimals each `0`-`5` (own line). Same construction as `print_bar_chart_v_3` but 5 columns. |
| APPROVED | graphics_ascii | print_bar_chart_h_3 | Reads 3 decimals each `0`-`9` (own line). Prints 3 rows: row `i` is `input_i` consecutive `*`s + `\n`. |
| APPROVED | graphics_ascii | print_bar_chart_h_5 | Reads 5 decimals each `0`-`9` (own line). Same as `print_bar_chart_h_3` with 5 rows. |
| APPROVED | graphics_ascii | print_arrow_with_label | Reads a `\n`-terminated line ≤ 20 chars. Prints `--> <line>\n`. |
| APPROVED | graphics_ascii | print_thermometer_5 | Reads decimal `0`-`5` + `\n`. Prints a 5-row vertical thermometer: row `i` (counted from top) is `|` if `i >= 5 - input`, else ` `; then `\n` after each row. |
| APPROVED | cryptography | caesar_shift_n | Reads a signed decimal shift `-25`..`25` + `\n`, then a `\n`-terminated line ≤ 80 chars. Shifts each letter by `n` positions within its case (wrapping at `a`/`z`/`A`/`Z`); non-letters unchanged. Prints result + `\n`. |
| APPROVED | cryptography | caesar_brute_force | Reads a `\n`-terminated ciphertext ≤ 20 chars (letters and spaces only). Prints all 26 possible Caesar-decrypts (shifts `0`-`25`), one per line. |
| APPROVED | cryptography | vigenere_encode_short | Reads a `\n`-terminated lowercase key `1`-`8` chars, then a `\n`-terminated plaintext ≤ 40 chars. Applies Vigenère: each plaintext letter is shifted by `key[i mod key_length] - 'a'` positions (within its case, non-letters unchanged). Prints ciphertext + `\n`. |
| APPROVED | cryptography | vigenere_decode_short | Reads the same input format as `vigenere_encode_short` (key, then ciphertext). Applies the inverse shift (negative direction). Prints plaintext + `\n`. |
| APPROVED | cryptography | simple_substitution_encode | Reads a 26-char `\n`-terminated lowercase substitution mapping (the letter at position 0 is the substitution for `a`, position 1 for `b`, etc.). Then reads a `\n`-terminated plaintext ≤ 40 chars; substitutes each lowercase letter using the mapping (non-letters unchanged). Prints + `\n`. |
| APPROVED | cryptography | simple_substitution_decode | Reads the same 26-char mapping then ciphertext. Inverts the mapping (build inverse table) and applies to decode. Prints plaintext + `\n`. |
| APPROVED | cryptography | rail_fence_2_rails | Reads a `\n`-terminated plaintext ≤ 30 chars (no `\n`s inside). Encodes using 2-rail rail-fence cipher (write zigzag on 2 rails, read row-by-row). Prints ciphertext + `\n`. |
| APPROVED | cryptography | rail_fence_3_rails | Same I/O as `rail_fence_2_rails` but with 3 rails. |
| APPROVED | cryptography | columnar_transposition_3x3 | Reads a `\n`-terminated plaintext of exactly 9 chars. Writes them into a 3×3 grid row-major, then reads out column-by-column. Prints the result + `\n`. |
| APPROVED | cryptography | binary_complement_cipher | Reads a `\n`-terminated line ≤ 30 chars. For each byte (excluding `\n`), outputs the bitwise complement `~byte` as a raw byte. Final `\n`. |
| APPROVED | cryptography | ascii_offset_encode_n | Reads a signed decimal shift `-128`..`127` + `\n`, then a `\n`-terminated line ≤ 30 chars. For each input byte, outputs `(byte + n) mod 256` as a raw byte. Final `\n`. |
| OVERLAP | cryptography | ascii_offset_decode_n | OVERLAP with ascii_offset_encode_n: same add-mod-256 kernel; decode is just encode with negated shift. Dropped. |
| APPROVED | cryptography | fermat_test_witness | Reads three decimals `a`, `n` (each `2`-`30`, own line). Prints `1\n` if `a^(n-1) ≡ 1 (mod n)`, else `0\n`. (Fermat's little theorem witness; passing doesn't guarantee primality.) |
| APPROVED | cryptography | simple_hash_sum_4bit | Reads a `\n`-terminated line ≤ 30 chars. Computes the sum of all byte values (excluding `\n`) modulo 16. Prints the result as a single lowercase hex char + `\n`. |
| APPROVED | cryptography | one_time_pad_xor | Reads a `\n`-terminated pad of `1`-`30` bytes, then a `\n`-terminated message of EXACTLY the same length. XORs corresponding bytes; outputs the result as raw bytes + `\n`. (Self-inverse — applying twice with the same pad returns the original.) |
| APPROVED | cryptography | polybius_square_encode | Reads exactly one uppercase letter `A`-`Z` (excluding `J`; `I` and `J` are merged) + `\n`. Prints two decimal digits `<row><col>` (each `1`-`5`) + `\n` based on the standard 5×5 Polybius square (row-major fill of `A B C D E F G H I/J K L M N O P Q R S T U V W X Y Z`). |
| APPROVED | cryptography | polybius_square_decode | Reads two decimal digits + `\n` (e.g. `42`). Prints the corresponding uppercase letter from the standard 5×5 Polybius square + `\n`. |
| APPROVED | cryptography | caesar_validate | Reads a signed decimal shift `-25`..`25` + `\n`, then plaintext + `\n`, then candidate ciphertext + `\n` (each ≤ 20 chars). Prints `1\n` if applying Caesar shift to plaintext yields the candidate ciphertext exactly, else `0\n`. |
| APPROVED | cryptography | encrypt_then_reverse | Reads a `\n`-terminated plaintext ≤ 20 chars. Applies Caesar shift of `+3` (ROT3) then reverses the result. Prints the final string + `\n`. |
| APPROVED | cryptography | xor_with_position | Reads a `\n`-terminated line ≤ 30 chars. For each byte at 0-based position `i`, outputs `byte XOR i` as a raw byte. Final `\n`. |
| APPROVED | cryptography | shift_letter_by_position | Reads a `\n`-terminated line ≤ 20 chars. For each letter at 0-based position `i`, shifts it by `i` positions within its case (non-letters unchanged). Prints result + `\n`. |
| APPROVED | cryptography | encrypt_then_uppercase | Reads a `\n`-terminated plaintext ≤ 20 chars. Applies Caesar shift of `+5`, then uppercases all letters. Prints + `\n`. |
| APPROVED | cryptography | count_distinct_letters_ciphertext | Reads a `\n`-terminated line ≤ 80 chars. Prints the count of distinct LETTER bytes (case-insensitive; `A` and `a` count as one) as decimal + `\n`. |
| APPROVED | cryptography | modular_arith_demo | Reads three decimals `a`, `b`, `m` (each `0`-`50`, own line; `m >= 1`). Prints `(a+b) mod m\n(a*b) mod m\n` on two lines. |
| OVERLAP | cryptography | caesar_double_application | OVERLAP with caesar_shift_n (2-agent audit): same Caesar-shift kernel called with shift=2n; trivial parameter doubling. Same precedent as previously-dropped ascii_offset_decode_n. Dropped. |
| APPROVED | memory_layout | stack_overflow_demo | Reads digit N `0`-`9` + `\n`. Allocates a fixed-size stack of capacity 5. Pushes N items (values 1..N); if N > 5, prints `Stack overflow at item <N>!\n` and exits when the 6th push would happen. If N ≤ 5, pushes all N then prints `Pushed <N> items.\n`. |
| APPROVED | memory_layout | queue_overflow_demo | Same shape as `stack_overflow_demo` but with a queue of capacity 5. Prints `Queue overflow at item <N>!\n` or `Enqueued <N> items.\n`. |
| APPROVED | memory_layout | pointer_basic | Reads decimal address `0`-`15` + `\n`, then decimal value `0`-`255` + `\n`. Writes the value at the address (in a 16-byte array initially zeroed), then reads it back and prints the value + `\n`. |
| APPROVED | memory_layout | memory_dump_zero_to_15 | No input. Initializes a 16-byte array to `addr * 17 mod 256` for `addr = 0..15`. Prints the 16 byte values as 2-char lowercase hex space-separated + `\n` (e.g. `00 11 22 ... ff`). |
| APPROVED | memory_layout | variable_swap_no_temp | Reads two decimals `a` `b` (each `0`-`99`, own line). Swaps using XOR trick (no temporary variable): `a ^= b; b ^= a; a ^= b;`. Prints `<new_a>\n<new_b>\n`. |
| APPROVED | memory_layout | variable_swap_with_temp | Reads two decimals `a` `b` (each `0`-`99`, own line). Swaps using a temporary variable `t = a; a = b; b = t;`. Prints `<new_a>\n<new_b>\n`. |
| APPROVED | memory_layout | array_indexed_access_5 | Reads 5 decimals (each `0`-`99`, own line), then a decimal index `0`-`4` (own line). Prints the array element at that index + `\n`. |
| APPROVED | memory_layout | linked_list_print_3 | No input. Builds a 3-node linked list with values `10`, `20`, `30` (head→tail). Traverses head-to-tail and prints each value on its own line. |
| APPROVED | memory_layout | stack_clear_demo | No input. Pushes 3 values onto a stack, then clears the stack (pops all without using results), then attempts to pop and prints `Stack empty\n` because pop on empty stack must report empty. |
| APPROVED | memory_layout | show_local_vs_global | No input. Declares a global variable `g = 100` and a local variable inside `main` `l = 200`. Prints `Local: 200\nGlobal: 100\n`. |

## Batch 9 — language_demos + games + memory_layout + language_meta + recursion (95 approved + 4 overlap + 1 clarified)

Categories: language_demos (30 net), games (28 net of 30), memory_layout (13 net of 15), language_meta (15 net), recursion (9 net of 10).
CR-ist: 95 APPROVED, 4 OVERLAP, 1 UNCLEAR-tightened.

| status | category | name | description |
|---|---|---|---|
| APPROVED | language_demos | demo_bit_swap | Reads two single bits `0`/`1` (each on own line). Uses `bit.swap` STL macro to swap them in place. Prints them in swapped order as `<b>\n<a>\n`. |
| APPROVED | language_demos | demo_bit_inc_4bit | Reads a 4-char `0`/`1` binary string + `\n`. Uses `bit.inc` (4-bit). Prints result as 4-char binary + `\n` (mod 16). |
| APPROVED | language_demos | demo_bit_dec_4bit | Same as `demo_bit_inc_4bit` but with `bit.dec`. |
| APPROVED | language_demos | demo_bit_mov | Reads a 4-char binary + `\n`. Uses `bit.mov` to copy it into another variable, then prints the copy as 4-char binary + `\n`. |
| APPROVED | language_demos | demo_bit_cmp_4bit | Reads two 4-char binary strings (each on own line). Uses `bit.cmp`. Prints `<`, `=`, or `>` + `\n`. |
| APPROVED | language_demos | demo_bit_shl_4bit | Reads a 4-char binary + `\n`, then digit `0`-`3` + `\n` (shift count). Uses `bit.shl`. Prints result as 4-char binary + `\n`. |
| APPROVED | language_demos | demo_bit_shr_4bit | Same as `demo_bit_shl_4bit` but with `bit.shr`. |
| APPROVED | language_demos | demo_bit_mul10_8bit | Reads an 8-char binary + `\n`. Uses `bit.mul10`. Prints the result as decimal + `\n` (assume no overflow). |
| APPROVED | language_demos | demo_bit_print_dec_uint | No input. Declares an internal 8-bit value `123`. Uses `bit.print_dec_uint` to print it as `123\n`. |
| APPROVED | language_demos | demo_bit_print_hex_uint | No input. Declares an internal 8-bit value `255`. Uses `bit.print_hex_uint` to print it as `ff\n`. |
| APPROVED | language_demos | demo_hex_add | Reads two lowercase hex chars (each on own line). Uses `hex.add`. Prints the result hex + `\n` (mod 16, carry discarded). |
| APPROVED | language_demos | demo_hex_sub | Same I/O as `demo_hex_add` but uses `hex.sub`. |
| APPROVED | language_demos | demo_hex_xor | Same I/O but uses `hex.xor`. |
| APPROVED | language_demos | demo_hex_and | Same I/O but uses `hex.and`. |
| APPROVED | language_demos | demo_hex_or | Same I/O but uses `hex.or`. |
| APPROVED | language_demos | demo_hex_not | Reads one lowercase hex char + `\n`. Uses `hex.not` (XOR with `f`). Prints result hex + `\n`. |
| APPROVED | language_demos | demo_hex_inc | Reads one hex char + `\n`. Uses `hex.inc`. Prints result hex + `\n` (`f` wraps to `0`). |
| APPROVED | language_demos | demo_hex_dec | Same as `demo_hex_inc` but uses `hex.dec` (`0` wraps to `f`). |
| APPROVED | language_demos | demo_hex_cmp | Reads two hex chars (each own line). Uses `hex.cmp`. Prints `<`, `=`, or `>` + `\n`. |
| APPROVED | language_demos | demo_hex_shl | Reads one hex char + `\n`, then shift count `0`-`3` + `\n`. Uses `hex.shl`. Prints result hex + `\n`. |
| APPROVED | language_demos | demo_hex_shr | Same as `demo_hex_shl` but uses `hex.shr`. |
| APPROVED | language_demos | demo_hex_mul | Reads two hex chars. Uses `hex.mul`. Prints product as 2 hex chars + `\n` (high then low nibble). |
| APPROVED | language_demos | demo_hex_div | Reads two hex chars (dividend then divisor, divisor non-zero). Uses `hex.div`. Prints quotient hex + `\n`. |
| APPROVED | language_demos | demo_stl_output_string | No input. Uses `stl.output "Hello, FlipJump!\n"` to print the string. |
| APPROVED | language_demos | demo_rep_5_stars | No input. Uses `rep(5, i) stl.output('*')` then `stl.output('\n')` to print `*****\n`. |
| APPROVED | language_demos | demo_rep_10_dashes | No input. Uses `rep(10, i) stl.output('-')` then `\n`. Prints `----------\n`. |
| APPROVED | language_demos | demo_segment_reserve | Uses `segment` + `reserve` to set up a small memory region of 8 bytes initialized to zero. Reads no input. Prints the first byte's value (which is `0`) + `\n`. |
| APPROVED | language_demos | demo_compile_time_expr | No input. Internally uses a compile-time expression `(1 + 2) * (3 + 4)` to produce constant `21`. Uses `bit.print_dec_uint` to print `21\n`. |
| APPROVED | language_demos | demo_macro_one_arg | Defines a macro `print_byte(b)` that calls `stl.output(b)`. The top-level invokes `print_byte('A')`. Prints `A\n`. |
| APPROVED | language_demos | demo_namespace_usage | Defines `ns mathops { def add_one(x) { bit.inc x } }` and uses `mathops.add_one` on a 4-bit value `0011`. Prints result as 4-char binary + `\n`. |
| APPROVED | games | tic_tac_toe_status | Reads 3 lines of 3 chars each (board state with `X`, `O`, `.`). Prints exactly one of `X wins\n`, `O wins\n`, `Draw\n` (board full, no winner), or `In progress\n` (no winner, board not full). |
| APPROVED | games | hangman_state_print | Reads a `\n`-terminated secret word ≤ 10 chars (lowercase letters), then a `\n`-terminated string of guessed letters ≤ 26 chars. Prints the secret with un-guessed letters as `_` (e.g. secret `hello`, guesses `el` → `_ell_\n`). |
| APPROVED | games | hangman_lives_check | Reads a digit `0`-`6` + `\n` (number of wrong guesses so far). Prints `<lives>\n` where `lives = 6 - wrong`. If `lives == 0`, additionally prints `Game over!\n` on a second line. |
| APPROVED | games | blackjack_hand_value | Reads digit N `1`-`9` + `\n`, then N card-value codes (each one of `A`, `2`-`9`, `T`, `J`, `Q`, `K` on its own line). Computes the best total (`A` is `1` or `11`, face cards `J`/`Q`/`K` are `10`). Prints the best total `≤ 21` (or, if even with `A=1` all hands bust, prints the minimum bust total). |
| APPROVED | games | blackjack_bust_check | Reads digit N `1`-`9` + `\n`, then N card-value codes (same alphabet as `blackjack_hand_value`). Prints `1\n` if minimum total (treating all aces as 1) exceeds 21, else `0\n`. |
| APPROVED | games | coin_toss_streak | Reads a `\n`-terminated string of `H`/`T` chars (≤ 20). Prints the length of the longest run of consecutive identical results as decimal + `\n`. |
| APPROVED | games | dice_three_rolls | Reads exactly 3 bytes (no separators). For each byte `b`, prints `(b mod 6) + 1` as decimal on its own line (3 lines of output). |
| APPROVED | games | card_blackjack_value | Reads exactly one card-value char (`A`, `2`-`9`, `T`, `J`, `Q`, `K`). Prints the blackjack value: `A` → `1`, `2`-`9` → that digit, `T`/`J`/`Q`/`K` → `10`. Output is decimal + `\n`. |
| APPROVED | games | minesweeper_count_center | Reads 3 lines of 3 chars each (each char `M` for mine or `.` for empty). Prints the count of mines (`M`) in the 8 cells around the center `(1,1)` (excluding center itself) as decimal + `\n`. |
| APPROVED | games | minesweeper_count_grid | Reads 3 lines of 3 chars each (chars are `M` for mine, `.` for empty). Prints a 3×3 output grid where each cell shows the number of mine-neighbors (`0`-`8`) if not a mine, or `*` if it is a mine. 3 lines of 3 chars each + `\n`. |
| APPROVED | games | game_2048_one_merge_row | Reads exactly 4 single-digit decimals `0`-`9` (each own line) representing 4 values in a row. Applies one 2048 merge step (slide non-zero values left, merge adjacent equal pairs once left-to-right, then slide again). Prints the resulting 4 values on one line, space-separated, + `\n`. |
| APPROVED | games | game_2048_check_done | Reads a 4×4 grid of decimal digits `0`-`9` (4 lines, each 4 chars). Prints `1\n` if no moves are possible (no zeros AND no two adjacent-equal pairs horizontally or vertically), else `0\n`. |
| OVERLAP | games | othello_count_pieces | OVERLAP with chess_piece_count (3-agent consensus): same count-two-piece-chars-on-grid algorithm; differs only in alphabet and grid size. Same precedent as previously-dropped checkers_piece_count. Dropped. |
| APPROVED | games | battleship_hit_check | Reads a 4×4 grid (`S` = ship, `.` = water): 4 lines of 4 chars each. Then reads a hit coordinate `r c` (each digit `0`-`3` on its own line). Prints `hit\n` if grid[r][c] is `S`, else `miss\n`. |
| APPROVED | games | battleship_ships_remaining | Reads a 4×4 grid (4 lines, each 4 chars; `S` = ship cell, `.` = water), then a `\n`-terminated stream of `H`/`M` chars (each char represents the outcome at the corresponding `S` cell, in row-major order, skipping `.` cells). Prints the count of `S` cells that received `M` (or no value) — i.e. ship cells NOT hit yet — as decimal + `\n`. |
| APPROVED | games | rps_play_3_rounds | Reads 6 chars (3 pairs): player 1 then player 2 for each of 3 rounds (each char on own line; `r`/`p`/`s`). Determines round winner for each (P1, P2, or tie). Prints final summary `P1: <p1_wins>\nP2: <p2_wins>\nTies: <ties>\n`. |
| APPROVED | games | word_guess_reveal | Reads a `\n`-terminated secret word ≤ 8 chars (lowercase) and a `\n`-terminated guess char (single lowercase letter). Prints the secret with un-revealed letters as `_` (only the guess char is "revealed"; others stay as `_`). E.g. secret `apple`, guess `p` → `_pp__\n`. |
| APPROVED | games | nim_winner_three_heaps | Reads 3 decimals (each `0`-`7`, own line) representing heap sizes. Prints `first\n` if first player has a winning strategy (XOR of heaps != 0), else `second\n`. |
| APPROVED | games | chess_piece_count | Reads exactly 8 lines, each 8 chars, where each char is a chess piece (`P`/`R`/`N`/`B`/`Q`/`K` for white, lowercase for black, `.` for empty). Prints `white: <w>\nblack: <b>\n` with counts. |
| APPROVED | games | chess_pawn_at_promotion | Reads 2 decimals `r c` (each `0`-`7`, own line) — a white pawn's position. Prints `1\n` if `r == 0` (white pawn at promotion row), else `0\n`. |
| OVERLAP | games | checkers_piece_count | OVERLAP with othello_count_pieces: same count-two-piece-chars algorithm; differs only in alphabet case and grid size. Dropped. |
| APPROVED | games | spelling_bee_check | Reads a `\n`-terminated set of 7 lowercase letters (the allowed letters), then a `\n`-terminated candidate word ≤ 10 chars. Prints `1\n` if every letter of the word is in the allowed set, else `0\n`. |
| APPROVED | games | wordle_feedback | Reads a `\n`-terminated secret word (exactly 5 lowercase letters), then a `\n`-terminated guess (exactly 5 lowercase letters). Prints exactly 5 feedback chars + `\n`: `G` for green (right letter, right position), `Y` for yellow (right letter, wrong position; track multiplicity correctly per standard Wordle rules), `_` for grey. |
| APPROVED | games | mastermind_feedback | Reads a `\n`-terminated 4-char secret code (each char `1`-`6`) and a `\n`-terminated 4-char guess. Prints `<black> <white>\n` where `black` = exact position matches, `white` = right color wrong position (with proper multiplicity per Mastermind rules). |
| APPROVED | games | game_of_life_count_alive_5x5 | Reads a 5×5 binary grid (5 lines of 5 chars `0`/`1`). Prints the count of `1` cells as decimal + `\n`. |
| APPROVED | games | snake_eat_food | Reads two decimals `pos_snake` `pos_food` (each `0`-`9`, own line). Prints `1\n` if equal (snake eats food), else `0\n`. |
| APPROVED | games | tetris_piece_rotate | Reads a 2×2 piece description (2 lines of 2 chars `*`/`.`). Prints the piece rotated 90° clockwise (still 2×2). |
| OVERLAP | games | pong_paddle_decision | OVERLAP with compare_two (3-agent consensus): same 3-way 2-input comparison; differs only in output template (chars vs phrases). Dropped. |
| APPROVED | memory_layout | ptr_advance_demo | Reads decimal base address `0`-`15` + `\n`, then offset `0`-`15` + `\n`. Prints `(base + offset) mod 16` as decimal + `\n` (simulates pointer advance with wraparound). |
| APPROVED | memory_layout | ptr_read_at_offset | Reads 16 decimals (each `0`-`255`, own line) representing a 16-byte array, then a base index `0`-`15` + `\n`, then an offset `0`-`15` + `\n`. Prints `array[(base + offset) mod 16]` as decimal + `\n`. |
| APPROVED | memory_layout | ptr_write_at_offset | Reads a base index `0`-`15` + `\n`, then offset `0`-`15` + `\n`, then a value `0`-`255` + `\n`. Writes the value at `(base + offset) mod 16` in an initially-zero 16-byte array, then prints the array as 16 decimals space-separated + `\n`. |
| APPROVED | memory_layout | memcpy_short | Reads digit N `1`-`8` + `\n`, then N source bytes (each on own line as decimal `0`-`255`). Copies the bytes into a destination buffer of size N, then prints the destination as N decimals space-separated + `\n`. |
| APPROVED | memory_layout | memset_short | Reads digit N `1`-`9` + `\n`, then decimal value V `0`-`255` + `\n`. Fills an N-byte buffer with V, then prints all N bytes as decimals space-separated + `\n`. |
| APPROVED | memory_layout | memcmp_short | Reads digit N `1`-`5` + `\n`, then N decimals (`0`-`255`, own line) for array A, then N decimals for array B. Prints `1\n` if all N pairs match, else `0\n`. |
| APPROVED | memory_layout | struct_two_fields | Reads two decimals `a` `b` (each `0`-`99`, own line) representing a 2-field struct `{a, b}`. Prints `field1=<a> field2=<b>\n`. |
| OVERLAP | memory_layout | struct_array_3 | OVERLAP with struct_two_fields: same read-pair-print-formatted algorithm scaled 3x; no new memory-layout concept. Dropped. |
| APPROVED | memory_layout | array_2d_access_3x3 | Reads 9 decimals (3×3 grid, row-major, each on own line), then a row `0`-`2` + `\n`, then a col `0`-`2` + `\n`. Prints `grid[row][col]` as decimal + `\n`. |
| APPROVED | memory_layout | array_2d_assign_3x3 | Reads 9 decimals (3×3 grid), then row `0`-`2`, col `0`-`2`, value (each own line). Updates the cell, then prints the new grid as 3 lines of 3 decimals space-separated + `\n` each. |
| APPROVED | memory_layout | linked_list_insert_at_head | No input. Starts with fixed list `[10, 20, 30]`. Inserts `99` at the head (so list becomes `[99, 10, 20, 30]`). Prints the new list values one per line. |
| APPROVED | memory_layout | linked_list_reverse | No input. Starts with fixed list `[10, 20, 30]`. Reverses by in-place pointer manipulation (head becomes 30). Prints `[30, 20, 10]` one value per line. |
| APPROVED | memory_layout | stack_of_stacks_demo | No input. Has two stacks `A` and `B`. Pushes `[1, 2, 3]` onto A and `[4, 5]` onto B. Then pops all from A printing each, then pops all from B printing each. Output: `3\n2\n1\n5\n4\n`. |
| OVERLAP | memory_layout | array_init_with_pattern | OVERLAP with batch8/memory_layout/memory_dump_zero_to_15: same init-with-pattern algorithm; differs only in array length, multiplier, and output format. Dropped. |
| APPROVED | language_meta | print_word_size_compile_time | No input. Uses the compile-time constant `#w` to print the program's word size as decimal + `\n` (e.g. `64\n` if compiled with `w=64`, `32\n` if `w=32`). |
| APPROVED | language_meta | print_motto | No input. Prints `Flip a bit, then jump.\n`. |
| APPROVED | language_meta | print_one_instruction_explanation | No input. Prints `The only operation is: a;b (flip bit at a, jump to b).\n`. |
| APPROVED | language_meta | print_self_description_short | No input. Prints `I am a FlipJump program.\n`. |
| APPROVED | language_meta | print_self_description_long | No input. Prints a 4-line self-description: `I am a FlipJump program.\nMy only operation is flip-and-jump.\nI was assembled from macros.\nI run in a finite memory.\n`. |
| APPROVED | language_meta | print_compile_time_factorial_5 | No input. Internally computes `5! = 120` at compile time (using a `rep`-based multiplicative chain). Prints `120\n`. |
| APPROVED | language_meta | print_compile_time_fibonacci_8 | No input. Internally computes `F(8) = 21` at compile time. Prints `21\n`. |
| APPROVED | language_meta | macro_arg_substitution_demo | Defines a macro `outer(x) { inner(x, x) }` and `inner(a, b) { stl.output(a); stl.output(b) }`. Top-level invokes `outer('X')`. Output: `XX\n`. |
| APPROVED | language_meta | namespace_isolation_demo | Defines two namespaces `foo` and `bar`, each with a macro `say()` printing different text. Top-level invokes `foo.say()` then `bar.say()`. Output: `from foo\nfrom bar\n`. |
| APPROVED | language_meta | print_macro_call_count_static | No input. The program defines a macro `count()` that increments a runtime variable and calls itself nothing further (just bumps a counter). The macro is invoked 5 times at top level. After the 5th call, the program prints the final counter value as decimal + `\n` (i.e. `5\n`). |
| APPROVED | language_meta | print_label_address_modulo | No input. Defines a label `here`, then prints `<address-of-here> mod 256` as decimal + `\n`. (The value depends on the compiled layout but is deterministic per build.) |
| APPROVED | language_meta | print_address_difference | No input. Defines two labels `a` and `b` with `b` placed 4 ops after `a`. Prints the byte-distance `b - a` as decimal + `\n` (deterministic per FJM encoding). |
| APPROVED | language_meta | rep_print_compile_time_unwind | No input. Uses `rep(8, i) stl.output('0' + i)` to print `01234567\n`. Demonstrates compile-time loop expansion. |
| APPROVED | language_meta | compile_time_string_length | No input. Internally has the string `"FlipJump"`. Uses `#"FlipJump"` or `strlen` macro to compute its length at compile time. Prints `8\n`. |
| APPROVED | language_meta | infinite_loop_explanation | No input. Prints `A FlipJump program ends with a self-loop.\n`, then enters `stl.loop`. |
| APPROVED | recursion | gcd_recursive_with_steps | Reads two decimals `a`, `b` (each `1`-`50`, own line). Computes `gcd(a, b)` via recursive macro and prints each step `a b\n` (current pair after `a = b, b = a % b`), terminating with `<gcd> 0\n`. (Different from `gcd_recursive` which prints only final value.) |
| APPROVED | recursion | sum_of_digits_recursive | Reads decimal N in `0`-`999` + `\n`. Computes sum of digits via recursive macro `digit_sum(N) = (N == 0) ? 0 : (N % 10) + digit_sum(N / 10)`. Prints decimal sum + `\n`. |
| APPROVED | recursion | reverse_digits_recursive | Reads decimal N in `0`-`999` + `\n`. Computes the decimal reverse via recursive macro (each level extracts last digit and recurses on N/10). Prints reversed digits + `\n`. |
| APPROVED | recursion | binary_search_recursive | Reads digit N `1`-`9` + `\n`, then N sorted decimals (each on own line), then target. Implements binary search via recursive macro that halves the search interval. Prints 0-based index + `\n` or `not found\n`. |
| OVERLAP | recursion | count_down_print_recursive | OVERLAP with batch3/recursion/count_down_recursive: identical I/O and identical recursion strategy. Same program. Dropped. |
| APPROVED | recursion | mutual_recursion_ping_pong | No input. Two mutually-recursive macros: `ping(N) { stl.output "ping\n"; if N>0: pong(N-1) }` and `pong(N) { stl.output "pong\n"; if N>0: ping(N-1) }`. Top-level invokes `ping(3)`. Output: `ping\npong\nping\npong\n`. |
| APPROVED | recursion | count_down_recursive_no_print | Reads digit N `1`-`9` + `\n`. Recursive macro that counts down without printing intermediate steps; at base case (N=0) prints `done\n`. Demonstrates pure recursion without side effects in the chain. |
| APPROVED | recursion | binary_to_decimal_recursive | Reads an 8-char `0`/`1` binary string + `\n`. Computes its decimal value via recursive macro `b2d(s) = head(s) * 2^(len-1) + b2d(tail(s))`. Prints decimal `0`-`255` + `\n`. |
| APPROVED | recursion | tail_recursion_demo | Reads decimal N `0`-`9` + `\n`. Uses tail-recursive macro to compute `2^N` (each call doubles an accumulator). Prints decimal + `\n`. Demonstrates tail-call pattern. |
| APPROVED | recursion | depth_of_recursion_proof | Reads digit N `0`-`9` + `\n`. Recursive macro that just decrements N to 0, then prints `Reached depth <N>\n` from the deepest call. Output: `Reached depth N\n`. |

## Batch 10 — calendar_time + misc + more bits/logic/sequences (80 approved + 19 overlap + 1 clarified)

Categories: calendar_time (23 net of 25), misc (27 net of 40), bits (9 net of 10), logic (13 net of 15), sequences (8 net of 10).
CR-ist: 80 APPROVED, 19 OVERLAP, 1 UNCLEAR-tightened. Higher overlap rate signals diminishing returns.

| status | category | name | description |
|---|---|---|---|
| APPROVED | calendar_time | day_of_week_from_date | Reads year `1900`-`2099`, month `1`-`12`, day `1`-`31` (each on own line). Computes day-of-week via Zeller's congruence. Prints `0`-`6` + `\n` (Sunday=0). |
| OVERLAP | calendar_time | day_of_week_word | OVERLAP with day_of_week_from_date (5-agent consensus): same Zeller's algorithm; differs only in output template (number vs name). Dropped. |
| APPROVED | calendar_time | days_in_month | Reads year `1900`-`2099` then month `1`-`12` (each own line). Prints number of days `28`-`31` + `\n` (accounts for leap year). |
| APPROVED | calendar_time | days_in_year | Reads year `1900`-`2099` + `\n`. Prints `366\n` if leap year, else `365\n`. |
| APPROVED | calendar_time | is_valid_date | Reads year `1900`-`2099`, month, day (each own line). Prints `1\n` if all three form a valid Gregorian date (month `1`-`12`, day within month accounting for leap), else `0\n`. |
| APPROVED | calendar_time | dec_year_2digit_to_4digit | Reads 2-digit decimal `00`-`99` + `\n`. Interprets via "pivot 50" rule: `50`-`99` → `1950`-`1999`, `00`-`49` → `2000`-`2049`. Prints 4-digit year + `\n`. |
| APPROVED | calendar_time | format_date_iso | Reads year `1900`-`2099`, month `1`-`12`, day `1`-`31` (each own line). Prints `YYYY-MM-DD\n` with zero padding for MM and DD. |
| APPROVED | calendar_time | parse_date_iso_validate | Reads `YYYY-MM-DD\n` (10 chars + `\n`). Prints `1\n` if it parses as a valid date in `1900`-`2099`, else `0\n`. |
| APPROVED | calendar_time | format_time_12_hour | Reads 24-hour time as `HH:MM\n` (HH `00`-`23`, MM `00`-`59`). Prints `<H>:<MM> AM\n` or `<H>:<MM> PM\n` (12-hour format; midnight is `12:00 AM`, noon is `12:00 PM`; H is 1-12, no zero padding; MM stays zero-padded). |
| APPROVED | calendar_time | format_time_24_hour | Reads 12-hour time as `<H>:<MM> AM\n` or `<H>:<MM> PM\n` (H `1`-`12`, MM `00`-`59`). Prints 24-hour format `HH:MM\n` with both fields zero-padded. |
| APPROVED | calendar_time | seconds_to_clock_hms | Reads decimal total seconds `0`-`86399` + `\n`. Prints `HH:MM:SS\n` (all three fields zero-padded to 2 digits). |
| APPROVED | calendar_time | clock_hms_to_seconds | Reads `HH:MM:SS\n` (8 chars + `\n`, each field zero-padded to 2 digits). Prints total seconds as decimal `0`-`86399` + `\n`. |
| OVERLAP | calendar_time | month_to_short_name | OVERLAP with month_name: same 12-string-table lookup; only the table strings differ (4-agent audit). Dropped. |
| APPROVED | calendar_time | short_name_to_month | Reads a 3-char month abbreviation (`Jan`-`Dec`) + `\n`. Prints decimal `1`-`12` + `\n`. |
| APPROVED | calendar_time | day_of_year | Reads year `1900`-`2099`, month, day (each own line). Prints day-of-year `1`-`366` + `\n` (accounts for leap). |
| APPROVED | calendar_time | date_from_day_of_year | Reads year `1900`-`2099` + `\n`, then day-of-year `1`-`366` + `\n`. Prints `<month> <day>\n` (no zero padding) for the date. |
| APPROVED | calendar_time | days_between_dates_same_year | Reads year, month1, day1, month2, day2 (each own line). Both dates in the same year; date2 ≥ date1. Prints absolute day difference as decimal + `\n`. |
| APPROVED | calendar_time | weekend_check | Reads year, month, day (each own line). Prints `1\n` if the date falls on Saturday or Sunday (computed via Zeller's), else `0\n`. |
| APPROVED | calendar_time | business_days_in_month | Reads year `1900`-`2099`, month `1`-`12` (each own line). Prints count of Mon-Fri days in that month as decimal + `\n`. |
| APPROVED | calendar_time | quarter_of_year | Reads month `1`-`12` + `\n`. Prints quarter `1`-`4` + `\n` (Jan-Mar=1, Apr-Jun=2, Jul-Sep=3, Oct-Dec=4). |
| OVERLAP | calendar_time | age_from_birth_year | OVERLAP with batch1/sub_two_decimals: same a-b algorithm with year-bounded subrange. Dropped (same precedent as age_in_dog_years vs mul_by_7). |
| APPROVED | calendar_time | days_since_epoch_2000 | Reads year `2000`-`2099`, month, day (each own line). Prints days since `2000-01-01` (which is day 0) as decimal + `\n`. |
| APPROVED | calendar_time | epoch_to_date_2000 | Reads decimal days since `2000-01-01` (`0`-`36524`, own line). Prints `<year> <month> <day>\n` for the corresponding Gregorian date. |
| APPROVED | calendar_time | time_of_day_period | Reads decimal hour `0`-`23` + `\n`. Prints `morning\n` (5-11), `afternoon\n` (12-16), `evening\n` (17-20), or `night\n` (21-4). |
| APPROVED | calendar_time | days_to_next_weekday | Reads day-of-week `0`-`6` (Sun=0) + `\n`, then target day-of-week `0`-`6` + `\n`. Prints `(target - today + 7) mod 7` as decimal `0`-`6` + `\n` (the number of days from today to the next occurrence of target; `0` if target equals today). |
| OVERLAP | misc | fizzbuzz_1_to_100 | OVERLAP with batch3/loops/fizzbuzz_to_15 + fizzbuzz_to_20: third bound-only variant beyond the kept pair. Dropped. |
| APPROVED | misc | bottles_of_beer_5 | No input. Prints 5 verses of the "X bottles of beer on the wall" song counting down from 5 to 1. Each verse follows the canonical 2-line refrain. |
| APPROVED | misc | bottles_of_beer_n | Reads digit N `1`-`9` + `\n`. Prints N verses counting down from N to 1 (same per-verse format as `bottles_of_beer_5`). |
| OVERLAP | misc | random_quote_picker | OVERLAP with magic_eight_ball (2-agent audit): same (integer mod 5)→5-string-table algorithm. Same precedent as previously-dropped fortune_cookie_picker. Dropped. |
| OVERLAP | misc | seasonal_greeting | OVERLAP with batch3/season_from_month: same month→season-bucket; differs only in output template. Dropped. |
| APPROVED | misc | zodiac_western | Reads month `1`-`12` then day `1`-`31` (each own line). Prints the corresponding western zodiac sign (`Aries`, `Taurus`, ..., `Pisces`) + `\n`. |
| APPROVED | misc | zodiac_chinese | Reads year `1900`-`2099` + `\n`. Prints the corresponding Chinese zodiac animal (`Rat`, `Ox`, ..., `Pig`) + `\n`. |
| APPROVED | misc | roman_to_arabic_30 | Reads Roman numeral string (one of `I`-`XXX`, valid up to 30) + `\n`. Prints decimal `1`-`30` + `\n`. |
| APPROVED | misc | arabic_to_roman_30 | Reads decimal `1`-`30` + `\n`. Prints corresponding Roman numeral + `\n`. |
| OVERLAP | misc | fortune_cookie_picker | OVERLAP with misc/random_quote_picker: identical byte mod 5 → 5-string-table algorithm; only content differs. Dropped. |
| OVERLAP | misc | animal_sound | OVERLAP with batch6/menu_selection: same byte→fixed-string-table algorithm. Dropped. |
| OVERLAP | misc | season_to_color | OVERLAP with batch6/menu_selection: same byte→fixed-string-table algorithm. Dropped. |
| APPROVED | misc | country_flag_short | Reads a 3-letter country code `USA`/`FRA`/`JPN` + `\n`. Prints a 2-line ASCII flag for that country (each row a string of pattern blocks). Hardcoded for 3 countries. |
| OVERLAP | misc | mood_emoji | OVERLAP with batch6/menu_selection: same digit→fixed-string-table algorithm. Dropped. |
| APPROVED | misc | join_words_with_space | Reads digit N `1`-`9` + `\n`, then N `\n`-terminated words. Prints them joined by single space + `\n`. |
| OVERLAP | misc | join_words_with_comma | OVERLAP with join_words_with_space: same algorithm; differs only in separator. Dropped (same precedent as base16_with_dash_separator). |
| APPROVED | misc | random_choice_pick_3 | Reads 3 `\n`-terminated lines (each ≤ 20 chars) then one byte. Prints one of the 3 lines based on `byte mod 3`, followed by `\n`. |
| APPROVED | misc | lucky_sum_check | Reads 3 decimals `1`-`9` (each own line). Prints `1\n` if their sum is divisible by 7, else `0\n`. |
| APPROVED | misc | lucky_year_has_7 | Reads year `1900`-`2099` + `\n`. Prints `1\n` if its decimal representation contains the digit `7` anywhere, else `0\n`. |
| APPROVED | misc | magic_number_8 | Reads decimal N `0`-`999` + `\n`. Prints `magic!\n` if N mod 8 == 0, else `not magic\n`. |
| OVERLAP | misc | weekly_activity | OVERLAP with batch6/menu_selection: same byte→fixed-string-table algorithm. Dropped. |
| APPROVED | misc | word_acronym_check | Reads two `\n`-terminated lines: first an acronym (uppercase, ≤ 6 chars), second a sentence (≤ 40 chars). Prints `1\n` if the acronym matches the uppercased first letter of each whitespace-separated word in the sentence (in order), else `0\n`. |
| APPROVED | misc | is_valid_username | Reads `\n`-terminated string ≤ 20 chars. Prints `1\n` if its length is `3`-`12` and every byte is alphanumeric (`A`-`Z`/`a`-`z`/`0`-`9`), else `0\n`. |
| APPROVED | misc | count_emoji_pairs | Reads `\n`-terminated line ≤ 40 chars. Prints `<smileys> <frowns>\n` where smileys is the count of `:)` and frowns is the count of `:(` substrings (non-overlapping, scanning left-to-right). |
| APPROVED | misc | is_pangram | Reads `\n`-terminated line ≤ 80 chars. Prints `1\n` if the line contains every letter `a`-`z` at least once (case-insensitive), else `0\n`. |
| OVERLAP | misc | sentence_ends_with_question | OVERLAP with batch2/strings/ends_with_period: same last-byte-check algorithm; differs only in target byte. Dropped. |
| APPROVED | misc | count_paragraphs | Reads multi-line input terminated by EOF (or two consecutive `\n` characters as the final paragraph terminator). A paragraph is a maximal run of non-empty lines separated from other paragraphs by one or more empty lines. Prints the count of paragraphs as decimal + `\n`. |
| APPROVED | misc | is_cli_flag | Reads `\n`-terminated string ≤ 20 chars. Prints `1\n` if it starts with `-` (single-dash flag) OR `--` (long flag), else `0\n`. |
| APPROVED | misc | count_non_alphanumeric | Reads `\n`-terminated line ≤ 80 chars. Prints the count of bytes that are NEITHER letters NOR digits (excluding terminating `\n`) as decimal + `\n`. |
| OVERLAP | misc | reverse_word_order_in_line | OVERLAP with batch5/text_processing/reverse_words_in_line: identical specification. Dropped. |
| OVERLAP | misc | titlecase_simple | OVERLAP with batch5/text_processing/capitalize_words: same algorithm. Dropped. |
| APPROVED | misc | dollar_amount_to_words | Reads decimal `0`-`99` + `\n`. Prints the English-words form `<tens_word> <ones_word>\n` (e.g. `42` → `forty two\n`; `7` → `seven\n`; `10` → `ten\n`; `20` → `twenty\n`). |
| OVERLAP | misc | print_thanks_n_times | OVERLAP with batch1/hello/hello_n_times: same `read digit, print fixed string N times` algorithm; differs only in output string. Dropped. |
| APPROVED | misc | print_zigzag_3_lines | No input. Prints a fixed 3-line zigzag of `*` characters: `*       *\n  *   *  \n    *    \n`. |
| APPROVED | misc | letter_position_word | Reads `\n`-terminated string ≤ 10 chars (letters only). Prints the 0-based alphabetic position of each letter (as decimal), space-separated, followed by `\n`. Example: `abc\n` → `0 1 2\n`. |
| APPROVED | misc | greet_three_times | Reads `\n`-terminated name (≤ 15 chars). Prints `Hello, <name>!\n` three times (3 lines of output). |
| APPROVED | misc | day_progress_percent | Reads decimal hour `0`-`23` + `\n`, minute `0`-`59` + `\n`. Prints `(hour * 60 + minute) * 100 / 1440` (floor) as decimal + `\n` (= percent of day elapsed). |
| APPROVED | misc | print_progress_bar_10 | Reads digit `0`-`10` + `\n`. Prints a 10-char progress bar: `<percent>` `#` characters followed by `(10 - percent)` `.` characters, then `\n`. (e.g. `3` → `###.......\n`.) |
| APPROVED | misc | is_prime_or_one | Reads decimal `1`-`50` + `\n`. Prints `prime\n` if N is prime OR equals 1, else `composite\n`. (Variant: treats 1 as "kind of prime" for fun.) |
| APPROVED | misc | bits_to_emoji_face | Reads two bits `e1 e2` (eye states, each `0` closed or `1` open, own line), then one bit `m` (mouth state, `0` frown / `1` smile, own line). Prints a 3-char emoji face combining these: e.g. `1 1 1` → `:)\n`; `0 0 1` → `XD\n`; `1 1 0` → `:(\n`; `0 0 0` → `XO\n`. |
| APPROVED | bits | swap_two_bytes | Reads exactly 2 bytes. Outputs them in reverse order (byte2 first, then byte1) as raw bytes. |
| APPROVED | bits | min_two_bytes | Reads exactly 2 bytes. Outputs the byte with smaller numeric value (treating as unsigned 0-255) as a raw byte. |
| APPROVED | bits | max_two_bytes | Reads exactly 2 bytes. Outputs the byte with larger numeric value as a raw byte. |
| APPROVED | bits | xor_three_bytes | Reads exactly 3 bytes. Outputs `b1 XOR b2 XOR b3` as one raw byte. |
| APPROVED | bits | and_three_bytes | Reads exactly 3 bytes. Outputs `b1 AND b2 AND b3` as one raw byte. |
| APPROVED | bits | or_three_bytes | Reads exactly 3 bytes. Outputs `b1 OR b2 OR b3` as one raw byte. |
| OVERLAP | bits | byte_count_zero_bits | OVERLAP with batch1/bits/popcount_byte: `8 - popcount`; trivial constant adjustment. Dropped (same precedent as msb_position vs count_leading_zeros). |
| APPROVED | bits | byte_high_eq_low_nibble | Reads exactly 1 byte. Prints `1\n` if the high nibble equals the low nibble (e.g. `0xAA`, `0x33`), else `0\n`. |
| APPROVED | bits | byte_is_bit_palindrome | Reads exactly 1 byte. Prints `1\n` if the byte's 8-bit binary representation reads the same forward and backward (e.g. `0x99` = `10011001`), else `0\n`. |
| APPROVED | bits | byte_reverse_each_nibble | Reads exactly 1 byte. Reverses the bits within each nibble independently (high nibble reversed in place, low nibble reversed in place). Outputs the resulting byte as raw. |
| APPROVED | logic | logic_implies | Reads two `0`/`1` ASCII bits (each on own line). Prints `(NOT A) OR B` as `0` or `1` + `\n` (A → B). |
| OVERLAP | logic | logic_biconditional | OVERLAP with batch1/logic/xnor_gate: biconditional A iff B is exactly XNOR. Dropped. |
| APPROVED | logic | boolean_xor_three | Reads three ASCII bits. Prints their XOR (= 1 iff odd number of 1s) + `\n`. |
| APPROVED | logic | boolean_majority_three | Reads three ASCII bits. Prints `1\n` if at least 2 of them are `1`, else `0\n`. |
| OVERLAP | logic | boolean_minority_three | OVERLAP with boolean_majority_three: minority = NOT majority; same count algorithm with negated output. Dropped. |
| OVERLAP | logic | boolean_none_three | OVERLAP with or_3 (2-agent audit): boolean_none_three = NOT(or_3); complement of an existing scan. Same precedent as previously-dropped boolean_minority_three. Dropped. |
| APPROVED | logic | boolean_exactly_one | Reads three ASCII bits. Prints `1\n` if exactly one of them is `1`, else `0\n`. |
| APPROVED | logic | boolean_exactly_two | Reads three ASCII bits. Prints `1\n` if exactly two are `1`, else `0\n`. |
| APPROVED | logic | multiplexer_2to1 | Reads a selector bit + 2 data bits (each on own line). Outputs `data0` if selector is `0`, else `data1`, as one ASCII bit + `\n`. |
| APPROVED | logic | demultiplexer_1to2 | Reads a data bit + selector bit. Outputs two bits separated by space + `\n`: if selector is `0`, prints `<data> 0\n`; if `1`, prints `0 <data>\n`. |
| APPROVED | logic | mux_4to1 | Reads two selector bits + 4 data bits (each on own line). Outputs the selected data bit (selector encodes 0-3 as `s1*2+s0`) + `\n`. |
| APPROVED | logic | encoder_4to2 | Reads 4 bits (assumed one-hot input, exactly one is `1`). Prints 2 bits as `<s1><s0>\n` (e.g. position 0 → `00`, position 3 → `11`). |
| APPROVED | logic | decoder_2to4 | Reads 2 bits `s1 s0`. Prints 4 bits: position `s1*2+s0` is `1`, others are `0`. Output is 4 chars + `\n`. |
| APPROVED | logic | full_adder | Reads three ASCII bits `a b c_in` (each own line). Prints `<sum> <c_out>\n` where `sum = a XOR b XOR c_in` and `c_out = (a AND b) OR (c_in AND (a XOR b))`. |
| APPROVED | logic | nand_universality_or | Reads two ASCII bits `a b` (each own line). Computes `OR(a, b)` using ONLY `NAND` gates (no native AND/OR/NOT). Prints result + `\n`. |
| OVERLAP | sequences | nat_first_n_spaced | OVERLAP with batch2/count_up_to_n: same algorithm; differs only in delimiter (space vs newline). Dropped. |
| APPROVED | sequences | evens_first_n | Reads digit N `1`-`9` + `\n`. Prints first N positive even numbers `2, 4, ..., 2N` space-separated + `\n`. |
| APPROVED | sequences | odds_first_n | Reads digit N `1`-`9` + `\n`. Prints first N positive odd numbers `1, 3, ..., 2N-1` space-separated + `\n`. |
| APPROVED | sequences | powers_of_2_first_n | Reads digit N `1`-`7` + `\n`. Prints `2^0, 2^1, ..., 2^(N-1)` space-separated + `\n`. |
| APPROVED | sequences | powers_of_3_first_n | Reads digit N `1`-`5` + `\n`. Prints `3^0, 3^1, ..., 3^(N-1)` space-separated + `\n`. |
| OVERLAP | sequences | squares_first_n_lines | OVERLAP with batch5/sequences/square_first_n: same algorithm; differs only in delimiter. Dropped. |
| OVERLAP | sequences | cubes_first_n_lines | OVERLAP with batch5/sequences/cube_first_n: same algorithm; differs only in delimiter. Dropped. |
| APPROVED | sequences | fibonacci_pairs_first_n | Reads digit N `1`-`8` + `\n`. Prints `<F(i)> <F(i+1)>\n` for `i = 0..N-1` (N lines of consecutive Fibonacci pairs). |
| APPROVED | sequences | mersenne_first_n | Reads digit N `1`-`7` + `\n`. Prints first N Mersenne numbers `M(k) = 2^k - 1` for `k = 1..N`, space-separated + `\n`. |
| APPROVED | sequences | triangular_inverse_n | Reads decimal triangular number `1`-`55` + `\n` (i.e. one of `1, 3, 6, 10, 15, 21, 28, 36, 45, 55`). Prints the index `k` such that `T(k) == input`, else `-1` if input isn't triangular. |

## Batch 11 — fresh subjects (105 net APPROVED + 13 OVERLAP + 1 REJECT + 1 UNCLEAR-tightened)

Subjects: bit_tricks, hashing, prng, modular_arithmetic, combinatorics, vm/interpreter, simple_db, probability_stats, music_theory, logic_puzzles.
Mapped to categories: bits (14 net), cryptography (13 net), algorithms (23 net), number_theory (24 net), language_demos (13 net), data_structures (9 net), puzzles (4 net), misc (7 net).

Three-stage review:
1. Standard CR-ist (1 fresh subagent) on 120 proposed: 111 APPROVED + 7 OVERLAP (bf_inc_only, counter_machine_demo, echo_machine_demo, count_distinct_keys_5, pitch_class_to_note_name, interval_semitones, interval_name_simple) + 1 REJECT (knights_knaves_1) + 1 UNCLEAR (fnv1_hash_short tightened with explicit `0x93` multiplier).
2. 3-agent cross-batch audit (agent 2 errored; agents 1 & 3 returned). Both-flagged consensus pairs: log2_floor_byte, quadratic_residue_check, xor_fold_to_nibble, coin_flips_lcg_8, binomial_proportion_5 (+ polynomial_hash_prime_251, unary_addition_tm, midi_to_pitch_class as borderline kept).
3. Final picks: 6 additional drops (the 5 above + accumulator_step which one agent flagged tight with exact simple_op_calc precedent). Catalog precedent kept polynomial_hash_prime_251 (variant-by-modulus), unary_addition_tm (TM educational framing), and midi_to_pitch_class (no pre-existing mod_by_12).

| status | category | name | description |
|---|---|---|---|
| APPROVED | bits | gray_code_from_binary | Reads one byte and outputs the corresponding Gray code byte (`byte XOR (byte >> 1)`) as one raw byte. |
| APPROVED | bits | binary_from_gray_code | Reads one byte interpreted as a Gray code value and outputs the corresponding standard-binary byte (running XOR of all higher bits). |
| APPROVED | bits | next_power_of_2_byte | Reads one byte `0`-`128` and outputs the smallest power of 2 that is `>=` the input (`0` → `1`, `5` → `8`, `8` → `8`) as one raw byte. |
| APPROVED | bits | prev_power_of_2_byte | Reads one byte `1`-`255` and outputs the largest power of 2 that is `<=` the input (`5` → `4`, `8` → `8`) as one raw byte. |
| OVERLAP | bits | log2_floor_byte | OVERLAP with count_leading_zeros (b4) (2/2 agent consensus, tight): log2_floor(b) = 7 - clz(b) for b in 1-255; constant offset of an existing scan. Exact msb_position vs clz precedent. Dropped. |
| APPROVED | bits | log2_ceil_byte | Reads one byte `1`-`128` and prints `ceil(log2(byte))` as a single decimal digit `0`-`7` + `\n` (e.g. `5` → `3`, `8` → `3`). |
| APPROVED | bits | count_leading_ones | Reads one byte and prints the count of consecutive `1` bits starting from the MSB (`0xE0` → `3`, `0xFF` → `8`) as decimal `0`-`8` + `\n`. |
| APPROVED | bits | count_trailing_ones | Reads one byte and prints the count of consecutive `1` bits starting from the LSB (`0x07` → `3`, `0xFF` → `8`) as decimal `0`-`8` + `\n`. |
| APPROVED | bits | round_up_to_multiple_of_8 | Reads one byte `0`-`247` and outputs the smallest multiple of 8 that is `>=` the input (`0` → `0`, `1` → `8`, `9` → `16`) as one raw byte. |
| APPROVED | bits | round_down_to_multiple_of_8 | Reads one byte `0`-`255` and outputs the largest multiple of 8 that is `<=` the input (`0` → `0`, `9` → `8`, `15` → `8`) as one raw byte. |
| APPROVED | bits | unset_lowest_set_bit | Reads one byte and outputs `byte AND (byte - 1)` (clears the lowest set bit) as one raw byte. For `byte = 0` outputs `0`. |
| APPROVED | bits | isolate_lowest_set_bit | Reads one byte and outputs `byte AND (-byte mod 256)` (keeps only the lowest set bit) as one raw byte. For `byte = 0` outputs `0`. |
| APPROVED | bits | broadcast_lsb_to_byte | Reads one byte. If its LSB is `0` outputs `0x00`; if `1` outputs `0xFF`. (Demonstrates sign-extension-from-1-bit pattern.) |
| APPROVED | bits | clear_low_k_bits | Reads one byte then one decimal digit `0`-`7` + `\n`. Outputs the byte with the lowest `k` bits cleared (`byte AND (~((1<<k)-1))`) as one raw byte. |
| APPROVED | bits | set_low_k_bits | Reads one byte then one decimal digit `0`-`7` + `\n`. Outputs the byte with the lowest `k` bits set to `1` (`byte OR ((1<<k)-1)`) as one raw byte. |
| APPROVED | cryptography | djb2_hash_short | Reads a `\n`-terminated line ≤ 30 chars. Computes the djb2 hash modulo 256: `h = 5381; for each byte b: h = ((h * 33) + b) mod 256`. Prints `h` as 2 lowercase hex chars + `\n`. |
| APPROVED | cryptography | fnv1a_hash_short | Reads a `\n`-terminated line ≤ 30 chars. Computes FNV-1a hash modulo 256: `h = 0; for each byte b: h = ((h XOR b) * 0x93) mod 256` (`0x93` = FNV prime `16777619 mod 256`). Prints `h` as 2 lowercase hex chars + `\n`. (Distinct from `fnv1_hash_short` by operation order — XOR then multiply vs multiply then XOR.) |
| APPROVED | cryptography | polynomial_hash_mod_256 | Reads a `\n`-terminated line ≤ 30 chars. Computes `sum(byte[i] * 31^i) mod 256` for `i = 0..n-1`. Prints `h` as 2 lowercase hex chars + `\n`. |
| APPROVED | cryptography | crc8_simple | Reads a `\n`-terminated line ≤ 30 chars. Computes CRC-8 using polynomial `0x07` starting with `crc = 0`. Prints CRC as 2 lowercase hex chars + `\n`. |
| APPROVED | cryptography | pearson_hash_byte | Reads a `\n`-terminated line ≤ 30 chars. Applies Pearson's 8-bit hash using a fixed 256-byte permutation table (defined in code). Prints hash as 2 lowercase hex chars + `\n`. |
| APPROVED | cryptography | adler_lite_hash | Reads a `\n`-terminated line ≤ 30 chars. Computes an Adler-32-style hash with small modulus: `a = 1; b = 0; for each byte: a = (a + byte) mod 251; b = (b + a) mod 251;` then prints `b * 256 + a` as 4 lowercase hex chars + `\n`. |
| APPROVED | cryptography | rolling_hash_step | Reads decimal state `0`-`255` + `\n`, then one byte. Updates state via `state = ((state * 31) + byte) mod 256` and prints the new state as 2 lowercase hex chars + `\n`. |
| OVERLAP | cryptography | xor_fold_to_nibble | OVERLAP with checksum_xor (b6) (2/2 agent consensus, borderline): same XOR-all-bytes kernel as checksum_xor; adds a thin nibble-XOR post-step (3 ops: extract high, extract low, XOR). Output half the size. Dropped per existing-scan + trivial-post-step precedent. |
| APPROVED | cryptography | djb2_compare_two | Reads two `\n`-terminated lines (each ≤ 20 chars). Computes djb2 hash mod 256 of each. Prints `1\n` if the hashes match, else `0\n`. |
| APPROVED | cryptography | murmur_lite_4byte | Reads exactly 4 raw bytes. Computes a tiny Murmur-style hash: `h = 0x12345678; for each byte b: h = ((h XOR b) * 0x05) mod 256`. Prints `h` as 2 lowercase hex chars + `\n`. |
| APPROVED | cryptography | fnv1_hash_short | Reads a `\n`-terminated line ≤ 30 chars. Computes FNV-1 mod 256 with explicit multiplier `0x93` (FNV prime mod 256): `h = 0; for each byte b: h = ((h * 0x93) mod 256) XOR b`. Prints hash as 2 lowercase hex chars + `\n`. (Distinct from `fnv1a_hash_short` by operation order — multiply then XOR vs XOR then multiply.) |
| APPROVED | cryptography | polynomial_hash_prime_251 | Reads a `\n`-terminated line ≤ 30 chars. Same algorithm as `polynomial_hash_mod_256` but with modulus 251 instead of 256. Prints hash as decimal `0`-`250` + `\n`. |
| APPROVED | cryptography | hash_to_bucket_10 | Reads a `\n`-terminated line ≤ 20 chars. Computes djb2 hash, then takes `hash mod 10`. Prints the bucket index `0`-`9` as one decimal digit + `\n`. |
| APPROVED | cryptography | hash_match_target | Reads exactly 2 hex chars + `\n` (target hash), then a `\n`-terminated line ≤ 20 chars. Prints `1\n` if `djb2_hash_short(line) == target`, else `0\n`. |
| APPROVED | cryptography | djb2_first_n_chars | Reads digit N `1`-`9` + `\n`, then a `\n`-terminated line ≥ N chars. Computes djb2 hash mod 256 of only the first N bytes of the line. Prints hash as 2 lowercase hex chars + `\n`. |
| APPROVED | algorithms | lcg_step_8bit | Reads one byte (the seed/state). Applies one LCG step: `state = (state * 5 + 3) mod 256`. Outputs the new state as one raw byte. |
| APPROVED | algorithms | lcg_steps_n_8bit | Reads one byte (seed), then one decimal digit N `1`-`9` + `\n`. Applies N LCG steps (constants `5` and `3`, mod 256) and prints each successive state as decimal on its own line (N lines total). |
| APPROVED | algorithms | xorshift_step_8bit | Reads one non-zero byte (state). Applies xorshift8: `s ^= s << 3; s ^= s >> 4; s ^= s << 2;` (all mod 256). Outputs the new state as one raw byte. |
| APPROVED | algorithms | xorshift_steps_n_8bit | Reads one non-zero byte (state), then decimal N `1`-`9` + `\n`. Applies N xorshift8 steps. Prints each successive state as decimal on its own line. |
| APPROVED | algorithms | fisher_yates_shuffle_5 | Reads 5 decimals `0`-`9` (each on own line), then 5 raw bytes (the PRNG bytes). Applies Fisher-Yates shuffle: for `i` from 4 down to 1, swap `arr[i]` with `arr[byte[5-i] mod (i+1)]`. Prints the shuffled array as 5 decimals space-separated + `\n`. |
| OVERLAP | algorithms | coin_flips_lcg_8 | OVERLAP with random_bits_n (b11) (2/2 agent consensus, borderline): same LCG-then-parity kernel; coin_flips_lcg_8 at N=8 is the fixed-K specialization with H/T characters instead of 0/1. Variant-by-output-character (sign_of/sign_word precedent). Dropped; keep random_bits_n as the variable-N canonical form. |
| APPROVED | algorithms | dice_rolls_lcg_5 | Reads one byte (seed). Applies 5 LCG steps and prints `(state mod 6) + 1` as a decimal digit `1`-`6` on its own line (5 lines total). |
| APPROVED | algorithms | middle_square_step | Reads two bytes (low and high of a 16-bit state). Applies one middle-square step: square the 16-bit state to get a 32-bit result, then take the middle 16 bits. Outputs the new state as two raw bytes (low then high). |
| APPROVED | algorithms | blum_blum_shub_tiny | Reads one byte `1`-`15` (state). Applies one BBS step: `state = (state * state) mod 21` (where `21 = 3 * 7`, both Blum primes). Outputs the new state as one raw byte. |
| APPROVED | algorithms | weighted_choice_lcg | Reads three decimal weights `w0 w1 w2` (each `0`-`9`, on own lines; sum >= 1), then one byte (seed). Generates one LCG sample `r`, then picks bucket `i` such that `r mod (w0+w1+w2) < w0+w1+...+wi`. Prints `i` as decimal `0`-`2` + `\n`. |
| APPROVED | algorithms | random_bits_n | Reads one byte (seed), then decimal N `1`-`9` + `\n`. Applies N LCG steps and outputs the LSB of each state as a `0` or `1` char, all concatenated on a single line + `\n`. |
| APPROVED | algorithms | random_byte_in_range | Reads one byte (seed), then `lo` `hi` (each on own line, both `0`-`9`, `lo <= hi`). Applies one LCG step, computes `lo + (state mod (hi - lo + 1))`, and prints as decimal + `\n`. |
| APPROVED | algorithms | shuffle_short_string | Reads a `\n`-terminated line of exactly 5 chars, then 5 raw bytes (PRNG). Applies Fisher-Yates shuffle on the 5 chars using the PRNG bytes (same indexing rule as `fisher_yates_shuffle_5`). Prints shuffled string + `\n`. |
| APPROVED | algorithms | prng_period_count | Reads one byte (seed). Applies LCG steps with constants `5`, `3`, mod 256, counting steps until the state returns to the seed value. Prints the period as decimal + `\n`. |
| APPROVED | algorithms | count_below_threshold_lcg | Reads one byte (seed), then one byte (threshold). Applies 10 LCG steps and counts how many states are strictly `<` threshold. Prints the count as decimal `0`-`10` + `\n`. |
| APPROVED | algorithms | variance_5 | Reads exactly 5 decimals `0`-`99` (each on own line). Computes `mean = floor(sum/5)`, then `variance = sum((x_i - mean)^2) / 5` (floor). Prints variance as decimal + `\n`. |
| APPROVED | algorithms | std_dev_5_floor_sqrt | Reads exactly 5 decimals `0`-`99`. Computes variance (as in `variance_5`), then prints `floor(sqrt(variance))` as decimal + `\n`. Use integer-sqrt by linear scan. |
| APPROVED | algorithms | range_5_fixed | Reads exactly 5 decimals and prints `max - min` as decimal + `\n`. |
| APPROVED | algorithms | mean_abs_deviation_5 | Reads exactly 5 decimals `0`-`99`. Computes `mean = floor(sum/5)`, then prints `floor(sum(|x_i - mean|) / 5)` as decimal + `\n`. |
| APPROVED | algorithms | bernoulli_trial_count_8 | Reads exactly 8 raw bytes. Counts how many are even (a "success"). Prints count `0`-`8` as decimal + `\n`. |
| APPROVED | algorithms | coin_until_first_head | Reads up to 20 raw bytes one at a time. Stops as soon as a byte with even value is read ("heads"). Prints the count of bytes read up to and including that first head as decimal + `\n`. If no head appears in 20 bytes, prints `-1\n`. |
| OVERLAP | algorithms | binomial_proportion_5 | OVERLAP with bernoulli_trial_count_8 (b11) (2/2 agent consensus, borderline): same count-even-bytes kernel; differs in N (5 vs 8) and a trivial `*20` output transform. Combination of fixed-K variant + constant-multiplier output transform. Dropped. |
| APPROVED | algorithms | z_score_compare_5 | Reads exactly 5 decimals `0`-`99` (population), then 1 additional decimal `0`-`99` (test value). Computes `mean` and `std_dev_5_floor_sqrt` of the 5 population values. Prints `floor((test - mean) / max(std_dev, 1))` as a signed decimal + `\n`. |
| APPROVED | algorithms | coefficient_of_variation_5 | Reads exactly 5 decimals `1`-`99`. Computes `mean` and `std_dev_5_floor_sqrt`. Prints `floor(std_dev * 100 / mean)` as decimal percent + `\n`. |
| APPROVED | algorithms | weighted_mean_3 | Reads 3 decimals (values `0`-`99` on own lines) then 3 decimals (weights `1`-`9` on own lines). Prints `floor(sum(v_i * w_i) / sum(w_i))` as decimal + `\n`. |
| APPROVED | number_theory | modular_inverse_brute | Reads decimals `a` `m` (each `1`-`30`, own line, with `gcd(a, m) = 1` guaranteed). Brute-forces `x` in `1..m-1` such that `(a * x) mod m == 1`. Prints `x` as decimal + `\n`. |
| APPROVED | number_theory | crt_two_pairs | Reads 4 decimals `r1 m1 r2 m2` (each on own line, `m1`,`m2` coprime, each ≤ `10`). Finds `r` such that `r ≡ r1 mod m1` and `r ≡ r2 mod m2`, with `0 <= r < m1*m2`. Prints `r` as decimal + `\n`. |
| APPROVED | number_theory | mod_factorial | Reads decimals `N` `m` (each `1`-`9` for N, `1`-`30` for m, on own lines). Prints `(N! mod m)` as decimal + `\n`. |
| APPROVED | number_theory | mod_binomial_small | Reads decimals `N` `K` `m` (`N` `1`-`9`, `K` `0..N`, `m` `1`-`30`, on own lines). Prints `(C(N, K) mod m)` as decimal + `\n`. |
| APPROVED | number_theory | mod_power_table | Reads decimals `base` `mod` (`base` `1`-`9`, `mod` `2`-`9`, on own lines). Prints `base^0 mod mod`, `base^1 mod mod`, ..., `base^(mod-1) mod mod` space-separated on one line + `\n`. |
| APPROVED | number_theory | multiplicative_order_small | Reads decimals `a` `m` (each `2`-`20`, `gcd(a,m)=1`). Finds the smallest `k >= 1` such that `(a^k) mod m == 1`. Prints `k` as decimal + `\n`. |
| APPROVED | number_theory | legendre_symbol_small | Reads decimals `a` `p` (`p` is an odd prime `3`-`19`, `a` `0`-`p-1`). Prints the Legendre symbol `(a/p)`: `1\n` if `a` is a non-zero quadratic residue mod p, `-1\n` if non-residue, `0\n` if `a == 0`. |
| OVERLAP | number_theory | quadratic_residue_check | OVERLAP with legendre_symbol_small (b11) (2/2 agent consensus, tight): same QR scan kernel; output collapses 3-valued Legendre (1/-1/0) to 2-valued (1/0). Output-fold of existing scan. Dropped. |
| APPROVED | number_theory | jacobi_symbol_small | Reads decimals `a` `n` (`n` odd `1`-`19`, `a` `0`-`n-1`). Prints the Jacobi symbol as `1\n`, `-1\n`, or `0\n`. |
| APPROVED | number_theory | mod_double_factorial | Reads decimals `N` `m` (`N` `0`-`9`, `m` `1`-`30`). Prints `(N!! mod m)` as decimal + `\n` (where `N!! = N*(N-2)*(N-4)*...` down to 1 or 2). |
| APPROVED | number_theory | wilson_prime_check | Reads decimal `p` `2`-`30` + `\n`. Computes `((p-1)! + 1) mod p`. Prints `1\n` if this is `0` (i.e. `p` is prime by Wilson's theorem), else `0\n`. |
| APPROVED | number_theory | inv_mod_via_fermat | Reads decimals `a` `p` (`p` prime `2`-`19`, `a` `1`-`p-1`). Computes `a^(p-2) mod p` (modular inverse via Fermat's little theorem). Prints inverse as decimal + `\n`. |
| APPROVED | number_theory | primitive_root_check | Reads decimals `g` `p` (`p` prime `3`-`19`, `g` `1`-`p-1`). Prints `1\n` if `g` is a primitive root mod p (i.e. its multiplicative order is `p-1`), else `0\n`. |
| APPROVED | number_theory | discrete_log_brute_small | Reads decimals `g` `h` `p` (`p` prime `3`-`19`, `g` `1`-`p-1` primitive root, `h` `1`-`p-1`). Brute-forces `x` in `0..p-2` such that `g^x mod p == h`. Prints `x` as decimal + `\n`. |
| APPROVED | number_theory | mod_sum_arithmetic | Reads decimals `N` `m` (`N` `1`-`30`, `m` `1`-`30`). Prints `((1 + 2 + ... + N) mod m)` as decimal + `\n`. |
| APPROVED | number_theory | binomial_coefficient_small | Reads decimals `N` `K` (`N` `0`-`10`, `K` `0`-`N`, on own lines). Prints `C(N, K)` as decimal + `\n`. |
| APPROVED | number_theory | multinomial_3_small | Reads 3 decimals `a` `b` `c` (each `0`-`5`, on own lines). Prints `(a + b + c)! / (a! * b! * c!)` as decimal + `\n`. |
| APPROVED | number_theory | permutation_count_pn_k | Reads decimals `N` `K` (`N` `1`-`10`, `K` `0`-`N`). Prints `P(N, K) = N! / (N-K)!` as decimal + `\n`. |
| APPROVED | number_theory | catalan_n_param | Reads decimal `N` `0`-`7` + `\n`. Prints the `N`-th Catalan number `C(2N, N) / (N + 1)` as decimal + `\n`. |
| APPROVED | number_theory | bell_n_param | Reads decimal `N` `0`-`6` + `\n`. Prints the `N`-th Bell number `B(N)` as decimal + `\n`. |
| APPROVED | number_theory | stirling_2nd_small | Reads decimals `N` `K` (`N` `0`-`6`, `K` `0`-`N`). Prints the Stirling number of the second kind `S(N, K)` as decimal + `\n`. |
| APPROVED | number_theory | derangement_n_param | Reads decimal `N` `0`-`8` + `\n`. Prints the `N`-th derangement number `D(N)` as decimal + `\n`. |
| APPROVED | number_theory | eulerian_n_k_small | Reads decimals `N` `K` (`N` `1`-`6`, `K` `0`-`N-1`). Prints the Eulerian number `<N, K>` as decimal + `\n`. |
| APPROVED | number_theory | lah_n_k_small | Reads decimals `N` `K` (`N` `1`-`6`, `K` `1`-`N`). Prints the (signed) Lah number `L(N, K)` as decimal + `\n`. |
| APPROVED | number_theory | pascal_row_n | Reads decimal `N` `0`-`8` + `\n`. Prints the `N`-th row of Pascal's triangle as `N+1` decimals space-separated + `\n`. |
| OVERLAP | language_demos | bf_inc_only | OVERLAP with strings/count_letter_e: single-cell `+`-counter with input ≤ 30 chars never wraps mod 256, so the program collapses to "count occurrences of target byte". Dropped — bf_inc_dec / bf_inc_dec_print / bf_tape_4 cover the BF family with real algorithmic depth. |
| APPROVED | language_demos | bf_inc_dec | Reads a `\n`-terminated string ≤ 30 chars containing `+` and `-` (other bytes ignored). Interprets on a single cell (initially 0, mod 256). Prints final cell value as decimal + `\n`. |
| APPROVED | language_demos | bf_inc_dec_print | Reads a `\n`-terminated Brainfuck program ≤ 30 chars using only `+`, `-`, `.` (other bytes ignored). Interprets on a single cell (initially 0, mod 256). Each `.` outputs the cell value as one raw byte. Final newline after all output. |
| APPROVED | language_demos | bf_tape_4 | Reads a `\n`-terminated BF program ≤ 30 chars using `+`, `-`, `<`, `>`, `.` (other bytes ignored). Interprets on a 4-cell tape (cells initially 0, mod 256). Each `.` outputs the current cell as one raw byte. The tape pointer stays in `[0, 3]` (out-of-bounds moves are silently ignored). Final newline after all output. |
| APPROVED | language_demos | stack_vm_push_add | Reads a `\n`-terminated program string of tokens separated by spaces: `PUSH <d>` (push single digit `0`-`9`) and `ADD` (pop two values, push their sum). After interpreting all tokens, prints the final top of stack as decimal + `\n`. ≤ 10 tokens total. |
| APPROVED | language_demos | stack_vm_pop_print | Reads a `\n`-terminated program: `PUSH <d>` and `POP` (pop top and print as decimal + `\n` for each POP). ≤ 10 tokens total. |
| OVERLAP | language_demos | accumulator_step | OVERLAP with interactive_calc (b11) (1/2 agent + exact precedent): same I/O shape (op byte + 2 decimals + result) and the 0-99 subrange is a subset of interactive_calc's unbounded operands. Same precedent as previously-dropped simple_op_calc. Dropped. |
| APPROVED | language_demos | accumulator_5_ops | Reads decimal `acc_initial` `0`-`9` + `\n`, then 5 `<op><digit>` tokens (each a 2-char ASCII pair like `+3`) separated by spaces on one line + `\n`. Applies the 5 ops sequentially to acc. Prints the final acc as decimal + `\n`. |
| APPROVED | language_demos | two_register_machine_5 | Reads decimal `R0` `R1` (each `0`-`9`, on own lines). Then 5 instructions on own lines, each one of `ADD0` (`R0 = R0 + R1`), `SUB0` (`R0 = R0 - R1`), `SWAP` (`R0 ↔ R1`), `INC0`, `INC1`. After all 5, prints `<R0> <R1>\n`. |
| OVERLAP | language_demos | counter_machine_demo | OVERLAP with parsing/parse_integer_echo: increment-N-times-from-0 is the identity map, so the I/O contract reduces to "read N, print N" exactly like parse_integer_echo. Dropped. |
| APPROVED | language_demos | subleq_one_step | Reads three decimals `m_a` `m_b` `pc` (each `0`-`9`, on own lines), then 10 decimals (the SUBLEQ memory cells `mem[0..9]`, each on own line, each `0`-`9`). Executes one SUBLEQ instruction `mem[m_b] = mem[m_b] - mem[m_a]; if mem[m_b] <= 0: pc = ...` (here we ignore the jump target — just the SUBLEQ subtract step). Prints the new value of `mem[m_b]` (signed decimal, may go negative) + `\n`. |
| APPROVED | language_demos | unary_increment_tm | Reads a `\n`-terminated string of `1`s (length 0-30), interpreted as a unary number. Outputs the same string with one additional `1` appended (representing N+1), followed by `\n`. |
| APPROVED | language_demos | unary_addition_tm | Reads a `\n`-terminated string of the form `1^a + 1^b` (e.g. `111+11` for 3+2). Outputs `1^(a+b)` + `\n` (`11111` for 3+2). |
| APPROVED | language_demos | one_op_demo | No input. Simulates 5 successive applications of the FlipJump primitive `flip bit a; jump b` on a 4-byte memory region, with hardcoded `a, b` pairs. Prints the final memory contents as 8 hex digits + `\n` (one nibble per output char, MSB first). |
| OVERLAP | language_demos | echo_machine_demo | OVERLAP with io/cat: spec admits "byte-for-byte echo" — the "1-instruction machine demo" framing is a shallow re-label of cat. Same precedent as turn_signal/animal_sound/etc. Dropped. |
| APPROVED | data_structures | kv_lookup_5 | Reads 5 key-value pairs: each as decimal `key` `0`-`9` + `\n`, then decimal `value` `0`-`99` + `\n` (total 10 lines). Then reads a query key + `\n`. Prints the value for that key as decimal + `\n`, or `not found\n` if the key wasn't among the 5. (Latest write wins on duplicates.) |
| APPROVED | data_structures | kv_lookup_n | Reads decimal `N` `1`-`9` + `\n`, then N key-value pairs (same format as `kv_lookup_5`). Then reads a query key. Prints the value, or `not found\n`. |
| APPROVED | data_structures | kv_update_then_lookup | Reads 5 key-value pairs (same format), then reads one update pair (new key + new value), then a query key. Applies the update (overwrites if key exists, else adds — but if adding would exceed capacity 6, drops the oldest entry). Prints lookup result or `not found\n`. |
| APPROVED | data_structures | range_query_count_5 | Reads 5 decimals `0`-`99` (each on own line), then `lo` `hi` (`0`-`99`, on own lines). Prints the count of those values that satisfy `lo <= x <= hi` as decimal `0`-`5` + `\n`. |
| APPROVED | data_structures | range_query_print_5 | Reads 5 decimals `0`-`99` (each on own line), then `lo` `hi`. Prints each value with `lo <= x <= hi` in input order, one per line. |
| APPROVED | data_structures | group_by_first_letter | Reads `N` `1`-`9` + `\n`, then N `\n`-terminated lowercase words. Groups by first letter and prints each `<letter> <count>\n` line, sorted by letter ascending. |
| APPROVED | data_structures | group_by_parity | Reads `N` `1`-`9` + `\n`, then N decimals on own lines. Prints `even: <e>\nodd: <o>\n` with the counts. |
| APPROVED | data_structures | select_max_per_group_2 | Reads 5 `(group, value)` pairs (each on 2 own lines, group `0` or `1`, value `0`-`99`). Prints `group 0 max: <v>\ngroup 1 max: <v>\n` (or `none\n` for either group if no pairs). |
| APPROVED | data_structures | sort_by_key_5 | Reads 5 `(key, value)` pairs (each on 2 own lines, key `0`-`9` integer, value `0`-`99`). Sorts ascending by key (stable). Prints each pair as `<key> <value>\n` (5 lines). |
| OVERLAP | data_structures | count_distinct_keys_5 | OVERLAP with algorithms/count_distinct_elements: same count-distinct algorithm (with N=5); the value half of each pair is read-and-discarded. The (key, value) framing is decorative. Dropped. |
| REJECT | puzzles | knights_knaves_1 | REJECT: too trivial — input restricted to 1 bit, output is a fixed 1-line string per bit (`K\n` or `paradox\n`). Pure 2-branch dispatch with zero computation. Dropped. |
| APPROVED | puzzles | knights_knaves_2 | Reads 2 decimals `s1` `s2` (each `0` or `1`, on own lines) representing two islanders' statements about each other: `s1`=0 means islander A says "B is a knight"; `s1`=1 means A says "B is a knave"; `s2` similarly is B's statement about A. Prints one of `AK BK\n`, `AK BN\n`, `AN BK\n`, `AN BN\n` (the consistent assignment) or `paradox\n` if no consistent assignment exists. |
| APPROVED | puzzles | cnf_2var_2clause_sat | Reads two 2-CNF clauses as lines, each in the form `<lit1> <lit2>` where each literal is `x`, `!x`, `y`, or `!y`. Prints `SAT\n` if there's an assignment to x, y making both clauses true, else `UNSAT\n`. |
| APPROVED | puzzles | propositional_eval_2var | Reads a formula string `\n`-terminated using only `x`, `y`, `&` (AND), `|` (OR), `!` (NOT), `(`, `)`. Then reads `x` value `0` or `1` + `\n` and `y` value `0` or `1` + `\n`. Prints `0\n` or `1\n` based on the evaluated formula. Formula ≤ 15 chars. |
| APPROVED | puzzles | tautology_check_2var | Reads a formula string `\n`-terminated (same syntax as `propositional_eval_2var`, ≤ 15 chars). Prints `1\n` if the formula is true for all 4 assignments of `x`, `y`, else `0\n`. |
| APPROVED | misc | note_name_to_pitch_class | Reads a `\n`-terminated note name (one of `C`, `C#`, `D`, `D#`, `E`, `F`, `F#`, `G`, `G#`, `A`, `A#`, `B`). Prints the pitch class `0`-`11` as decimal + `\n` (`C` = 0). |
| OVERLAP | misc | pitch_class_to_note_name | OVERLAP with branching/month_name: 12-entry digit→fixed-string-table lookup; only the table contents differ. Same precedent as previously-dropped month_to_short_name. Dropped. |
| APPROVED | misc | midi_to_octave | Reads decimal `0`-`127` + `\n`. Prints the octave number (signed: MIDI 0 → `-1`, MIDI 12 → `0`, MIDI 60 → `4`, MIDI 127 → `9`) + `\n`. |
| APPROVED | misc | midi_to_pitch_class | Reads decimal MIDI `0`-`127` + `\n`. Prints `midi mod 12` as decimal `0`-`11` + `\n`. |
| OVERLAP | misc | interval_semitones | OVERLAP with arithmetic/abs_diff: identical I/O and identical |a-b| algorithm; music framing is shallow. Dropped. |
| OVERLAP | misc | interval_name_simple | OVERLAP with branching/month_name: 13-entry digit→fixed-string-table lookup. Same precedent as previously-dropped month_to_short_name. Dropped. |
| APPROVED | misc | transpose_by_semitones | Reads decimal MIDI `0`-`127` + `\n`, then signed decimal shift `-24` to `24` + `\n`. Prints the new MIDI value `(input + shift)`, clamped to `[0, 127]`, as decimal + `\n`. |
| APPROVED | misc | major_scale_from_root_pcs | Reads decimal root pitch class `0`-`11` + `\n`. Prints the 7 pitch classes of the major scale starting at root (intervals 0, 2, 4, 5, 7, 9, 11), all mod 12, space-separated + `\n`. |
| APPROVED | misc | minor_scale_from_root_pcs | Reads decimal root pitch class `0`-`11` + `\n`. Prints the 7 pitch classes of the natural minor scale (intervals 0, 2, 3, 5, 7, 8, 10), all mod 12, space-separated + `\n`. |
| APPROVED | misc | is_major_triad | Reads 3 decimal MIDI numbers `m1 m2 m3` (each `0`-`127`, on own lines). Sorts them. Prints `1\n` if the intervals between consecutive sorted notes are `4, 3` semitones (i.e. major triad in root position), else `0\n`. |

## Retired rows (Phase 3)

When a row cannot be implemented within budget and gets replaced, mark it
`RETIRED: <reason>` in the `description` column, and add the replacement at
the bottom of the table with the next free `#NNNN`.

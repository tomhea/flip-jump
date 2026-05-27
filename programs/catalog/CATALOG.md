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
| APPROVED | io | print_until_period | Reads stdin and prints all bytes until (and including) the first `.`. Stops there. |
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
| APPROVED | arithmetic | add_four_decimals | Reads four decimal integers (each on its own line) and prints their sum as decimal + `\n`. |
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
| APPROVED | branching | sign_word | Reads one signed decimal and prints `positive\n`, `negative\n`, or `zero\n`. |
| APPROVED | branching | compare_to_10 | Reads one decimal and prints `less\n` if `<10`, `equal\n` if `=10`, `more\n` if `>10`. |
| APPROVED | branching | compare_to_100 | Reads one decimal and prints `less\n` if `<100`, `equal\n` if `=100`, `more\n` if `>100`. |
| APPROVED | branching | is_alphanumeric_byte | Reads exactly one byte and prints `1\n` if it's `0`-`9`/`A`-`Z`/`a`-`z`, else `0\n`. |
| APPROVED | branching | is_punctuation_byte | Reads exactly one byte and prints `1\n` if it's one of `,.?!;:'-` (the eight common punctuation marks), else `0\n`. |
| APPROVED | branching | is_whitespace_byte | Reads exactly one byte and prints `1\n` if it's space/tab/newline (`0x20`, `0x09`, `0x0A`), else `0\n`. |
| APPROVED | branching | char_class | Reads exactly one byte and prints one of `digit\n`, `upper\n`, `lower\n`, `other\n` based on the byte's ASCII range. |
| APPROVED | branching | weekday_or_weekend | Reads decimal day-of-week `0`-`6` (Sunday=0) and prints `weekend\n` (Sat/Sun) or `weekday\n` (Mon-Fri). |
| APPROVED | branching | is_business_hour | Reads decimal hour `0`-`23` (24-hour clock) and prints `1\n` if `9 <= h <= 17`, else `0\n`. |
| APPROVED | branching | simple_op_calc | Reads one byte from `+`/`-`/`*`, then `\n`, then a single digit `0`-`9`, then `\n`, then another digit `0`-`9`, then `\n`. Computes the operation and prints the decimal result + `\n`. |
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
| APPROVED | branching | all_same_three | Reads three decimals and prints `1\n` if all three are equal, else `0\n`. |
| APPROVED | branching | compare_with_window | Reads three decimals `a`, `lo`, `hi` (each own line) and prints `below\n` if `a < lo`, `in\n` if `lo <= a <= hi`, `above\n` if `a > hi`. |
| APPROVED | branching | sorted_check_three | Reads three decimals and prints `1\n` if they are in non-decreasing order, else `0\n`. |
| APPROVED | branching | sorted_check_four | Reads four decimals and prints `1\n` if they are in non-decreasing order, else `0\n`. |
| APPROVED | branching | rps_winner | Reads two bytes (each on own line, terminated by `\n`): `r`/`p`/`s` (rock/paper/scissors) for player 1 and player 2. Prints `1\n` if P1 wins, `2\n` if P2 wins, `tie\n` if tie. |
| APPROVED | branching | leap_year_check | Reads decimal year `1`-`9999` and prints `1\n` if it's a leap year (Gregorian rule: `(y%4==0 && y%100!=0) || y%400==0`), else `0\n`. |
| APPROVED | branching | bmi_category | Reads two decimals: weight-kg `1`-`200` then height-cm `100`-`250` (each own line). Computes BMI = weight*10000/(height*height) and prints `under\n` (BMI<18), `normal\n` (18-24), `over\n` (25-29), `obese\n` (≥30). |
| APPROVED | branching | turn_signal | Reads one byte: `L`, `R`, or `S`. Prints `left turn\n`, `right turn\n`, or `straight\n`. |
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
| APPROVED | recursion | is_odd_mutual_recursive | Reads decimal N `0`-`10` and prints `1\n` if odd else `0\n`, computed via the same mutual recursion as `is_even_mutual_recursive` but with the role swapped (entry point is `is_odd`). |

## Retired rows (Phase 3)

When a row cannot be implemented within budget and gets replaced, mark it
`RETIRED: <reason>` in the `description` column, and add the replacement at
the bottom of the table with the next free `#NNNN`.

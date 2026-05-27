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
| APPROVED | data_structures | brackets_matched | Reads a `\n`-terminated string ≤ 40 chars containing only `[` and `]`. Prints `1\n` if balanced, else `0\n`. |
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
| APPROVED | bits | byte_to_hex_string | Reads one byte (raw) and prints exactly two lowercase hex chars (no `0x` prefix) + `\n`. Differs from `io/char_to_hex` (which prints `0xNN\n`) and `conversion/dec_to_hex` (which reads a decimal text representation). |
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
| APPROVED | interactive | choose_path | Reads digit `1`-`3` + `\n`. For each choice prints a fixed 2-line story ending: `1`→`You chose the cave.\nA bat flies out!\n`; `2`→`You chose the river.\nA fish jumps high!\n`; `3`→`You chose the forest.\nA deer appears.\n`. |
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
| APPROVED | interactive | story_branch_2 | Reads one byte. If its value is even, prints `You chose left.\nYou found a treasure!\n`; if odd, prints `You chose right.\nYou met a dragon.\n`. |
| APPROVED | interactive | cheer_team | Reads digit `1`-`3` + `\n`. Prints `Go team <N>!\n` exactly three times. |
| APPROVED | interactive | quiz_show_score | Reads three single-digit decimals `0` or `1` (each `\n`-terminated; `1` = correct, `0` = wrong for 3 rounds). Prints `Total: <S>\nGrade: <G>\n`, where `S` is the sum (0-3) and `G` is `A`/`B`/`C`/`F` for `3`/`2`/`1`/`0`. |
| APPROVED | interactive | customer_rating | Reads digit `1`-`5` + `\n`. Prints `Thank you for your <N>-star review!\n`. |
| APPROVED | interactive | clock_set | Reads two decimals on separate lines: hour `0`-`23` then minute `0`-`59`. Prints `Time set to <HH>:<MM>\n` (each zero-padded to 2 digits). |
| APPROVED | interactive | greeting_user_age | Reads a `\n`-terminated name (≤ 20 chars) then a decimal age `0`-`120` + `\n`. Prints `Hello, <name>! You are <age> years old.\n`. |
| APPROVED | interactive | todo_add | Reads a `\n`-terminated task description (≤ 40 chars). Prints `Added: <task>\n`. |
| OVERLAP | interactive | todo_complete | OVERLAP with todo_add: identical read-line-then-prefix-and-echo; differs only in the prefix word. Dropped. |
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

## Retired rows (Phase 3)

When a row cannot be implemented within budget and gets replaced, mark it
`RETIRED: <reason>` in the `description` column, and add the replacement at
the bottom of the table with the next free `#NNNN`.

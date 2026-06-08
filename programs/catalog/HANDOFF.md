# Catalog — Implementation Handoff

Handoff for completing the demonstration catalog. As of this writing: **446 / 1029
approved specs implemented**, in 15 started categories; **3 categories complete**
(arithmetic, branching, hello, logic). This document is the plan for the remaining
~583 programs, plus the lessons that make them fast to write.

## Before you write a single program — read these, in order

1. **`programs/catalog/CONVENTIONS.md`** — authoritative file format, naming, header,
   testing protocol. Non-negotiable; read it end-to-end.
2. **The `writing-flipjump-stl-code` skill** — how to actually write FlipJump: the
   memory model (`*dw` stride), bit-vs-hex, init macros, the verification loop, the
   "easy to misread" traps, and `reference/quick-signatures.md` for exact arg orders.
   Don't reinvent idioms it already documents.
3. **fjdocs.tomhe.app** — the authoritative macro reference (signatures, `@requires`,
   complexity). Don't guess signatures from memory; look them up. Fallback: the STL
   source under `flipjump/stl/`.

**Verification is mandatory** (per the skill + CONVENTIONS): a program is done only
when it both halts (`Finished by looping…`) AND prints byte-exact expected output.
Verify through the Python module / `reference/fj_verify.py`, never a Windows shell
pipe (CRLF). Run the suite with `pytest --catalog` (or `-k <slug>` for one).

## Tooling (scripts/)

- `add_catalog_program.py` — writes the `.fj` + `.in`/`.out` with LF newlines and
  verifies via the Python flipjump module (bypasses git autocrlf + Windows stdout
  CRLF). Use it; don't hand-create the fixtures.
- `catalog_register.py` — registers a program in the test CSVs; compiles with
  `--werror` so an undeclared `@`/`<` label is rejected at authoring time, not by
  pytest later.
- `sort_catalog_by_duration.py` — keep the test CSVs sorted slowest-first; it
  measurably shortens the parallel compile pass (the longest single compile is the
  critical-path tail).

---

## The remaining work, in four passes

Each program's exact name + spec description is a row in `CATALOG.md` (status
`APPROVED`). Implement in `CATALOG.md` order within a category. Sizes below are the
approved-spec counts still unimplemented.

### Pass 1 — finish the 80 gaps in already-started categories (~80)

These are scattered missing specs in categories that are otherwise mostly done.
Lowest-risk, highest-leverage: the idioms already exist (see Lessons).

| Category | n | Missing slugs |
|---|---:|---|
| number_theory | 24 | modular_inverse_brute, crt_two_pairs, mod_factorial, mod_binomial_small, mod_power_table, multiplicative_order_small, legendre_symbol_small, jacobi_symbol_small, mod_double_factorial, wilson_prime_check, inv_mod_via_fermat, primitive_root_check, discrete_log_brute_small, mod_sum_arithmetic, binomial_coefficient_small, multinomial_3_small, permutation_count_pn_k, catalan_n_param, bell_n_param, stirling_2nd_small, derangement_n_param, eulerian_n_k_small, lah_n_k_small, pascal_row_n |
| misc | 13 | random_choice_pick_3, word_acronym_check, is_valid_username, count_emoji_pairs, is_pangram, is_cli_flag, count_non_alphanumeric, dollar_amount_to_words, letter_position_word, greet_three_times, print_progress_bar_10, bits_to_emoji_face, midi_to_octave |
| text_processing | 12 | char_freq_table, longest_word, shortest_word, word_with_most_vowels, count_word_occurrences, reverse_words_in_line, count_unique_words, longest_common_prefix_two, longest_common_suffix_two, line_starts_with_substring, line_ends_with_substring, count_substring_occurrences |
| bits | 9 | bit_at_position, set_bit_at_position, clear_bit_at_position, toggle_bit_at_position, binary_string_to_byte, byte_concat_to_hex_word, byte_split_from_hex_word, clear_low_k_bits, set_low_k_bits |
| geometry | 7 | manhattan_distance, chebyshev_distance, euclidean_distance_floor, signed_triangle_area_2x, circle_area_approx, circle_circumference_approx, counts_inside_unit_circle_grid_3x3 |
| loops | 4 | repeat_line_n, hollow_diamond, print_box_with_label, numbered_lines |
| strings | 3 | is_palindrome_string, repeat_line_2x, repeat_line_3x |
| sequences | 3 | bell_first_5, partition_first_5, mersenne_check |
| conversion | 2 | word_to_digit, roman_to_dec_1_to_10 |
| calendar_time | 2 | dec_year_2digit_to_4digit, days_between_dates_same_year |
| io | 1 | reverse_line |

> ℹ️ `mersenne_check` was originally deferred because its `CATALOG.md` description
> contains `√` and `≈`, which crashed the parser under a non-UTF-8 Windows locale. That
> parser bug is now fixed (source is read as UTF-8), so the constraint no longer applies.

### Pass 2 — algorithms, data_structures, language_demos (167)

| Category | n | Flavor (see CATALOG.md for the exact rows) |
|---|---:|---|
| algorithms | 68 | sorting/searching/scanning over small fixed arrays read from stdin |
| data_structures | 58 | array/stack/queue/set/lookup over N decimals (`array_count_*` shape) |
| language_demos | 41 | showcase FlipJump features themselves (macros, rep, pointers, self-modification) |

### Pass 3 — puzzles + cryptography‥parsing (209)

| Category | n | Flavor |
|---|---:|---|
| puzzles | 43 | small logic/brute-force puzzles with deterministic output |
| cryptography | 37 | caesar/xor/substitution/checksums on bytes (no real crypto) |
| encoding | 36 | base/hex/run-length/escape encode+decode round-trips |
| interactive | 33 | prompt→read→respond loops driven by scripted `.in` |
| graphics_ascii | 31 | ASCII shapes/grids/charts |
| parsing | 29 | tokenize/validate/evaluate tiny grammars |

### Pass 4 — simulation‥language_meta (127)

| Category | n | Flavor |
|---|---:|---|
| simulation | 27 | step a small state over time (cellular/physics-lite/counters) |
| games | 25 | deterministic game logic (tic-tac-toe judge, dice, etc.) |
| memory_layout | 22 | demonstrate addressing, vectors, pointers, alignment |
| state_machines | 20 | explicit FSMs over an input stream |
| recursion | 18 | recursive macros (`count_down_recursive` shape) |
| language_meta | 15 | meta/self-referential demos of the toolchain |

---

## Lessons learned (catalog-specific — coding lessons are in the skill)

**The STL got richer — use it, don't hand-roll.** Recent additions removed the two
biggest hand-rolled helpers:
- **Decimal I/O in hex-land now exists**: `hex.input_dec_uint/int n, dst, error` and
  `hex.print_dec_uint/int n, x` (+ `hex.mul10`, `hex.min/max`). The old per-program
  `read_decimal`/`print_dec` helpers are no longer needed for hex programs. (Bit
  programs still hand-roll the read loop — there is no `bit.input_dec_*`.)
- **`bit.mul` works now** (was previously broken at macro-resolve). Repeated-addition
  `mul_into` is no longer required for small multipliers — but it's still the cheapest
  option when one operand is a tiny constant, and incremental tricks beat both (below).
- `hex.div`/`hex.idiv` and `bit.div`/`bit.idiv` all work.

**Reusable idiom kits that carry across categories** (these are catalog-domain, beyond
what the skill documents):
- **EOF sentinel `\0`**: every catalog `.in` ends with `\0`; every reader does
  `bit.if0 8, ch, end` right after `bit.input ch`. `\0` is never data.
- **Number-theory trio** (powers Pass 1 + algorithms): `is_prime_into n, flag, x`
  (trial division, `bit.div` remainder), `gcd_into n, dst, a, b` (Euclid),
  `sum_proper_divisors_into n, dst, x`. perfect/abundant/deficient and `lcm=(a/gcd)*b`
  all reduce to these. All 16-bit.
- **Incremental square for √-bounded loops**: don't `mul` to get `d*d` each step;
  maintain `dsq` via `(d+1)^2 = d^2 + 2d + 1` (`dsq+=d; dsq+=d; dsq+=1; d++`). O(√x)
  adds, no multiply. Used by `is_prime_sqrt_into`.
- **Sequence-generation kit** (Pass 1 sequences + many algorithms): (1)
  `print_sep_dec n, value, first` prints a leading space before every term except the
  first (a `first: bit.bit` flag) → clean space-separated lists, no trailing space.
  (2) "Rotate a fixed register window" for linear recurrences (Lucas/Pell 2-window,
  Perrin/Tribonacci 3-window, …): print front, compute `nxt`, `mov` registers down.
  Figurate numbers avoid `mul` via an arithmetic `delta` that grows by a constant step.
- **Byte ↔ nibble**: a byte's two nibbles are at `ch` (low) and `ch + 4*dw` (high) —
  the same `*dw`-per-bit stride as the case-flip idiom (see skill "Memory model").

**Workflow gotchas (cost real time):**
- **Branch first**: `git checkout -b catalog/<batch> main` BEFORE writing files. Twice
  a batch was committed on `main` and the push failed.
- **Populate the `README.md` tables in the SAME PR — don't defer them.** Each category
  in `programs/catalog/README.md` has a per-program table (`| # | name | description |`).
  Pass 2 shipped the 167 programs with those three tables left empty and filled them in
  a separate follow-up PR (#341) — pure duplicated context-loading; don't repeat it. When
  you finish a batch, append one row per new program in the same PR:
  `| NNNN | slug | description |` where **NNNN** is the 4-digit number from the program
  header's `(#NNNN)` first line, **slug** is the filename without `.fj`, and **description**
  byte-matches the header / `CATALOG.md` line (a literal `\n` becomes a REAL newline inside
  the cell — see `number_theory/is_prime_small`). Rows sorted ascending by NNNN within each
  category. Derive them straight from the `.fj` headers (a throwaway script reading line 1
  for the number and line 3 for the description), never by hand.
- **Compile cost is flat ~0.18s/program at w=64** (STL macro resolution, not your
  body). ~1200 programs ≈ a few minutes parallel. Keep CSVs sorted slowest-first.
- **UTF-8 source (FIXED)**: `fj_parser.lex_parse_curr_file` now reads source with
  `open('r', encoding='utf-8')`, so non-ASCII source chars no longer depend on the OS
  locale. No `PYTHONUTF8=1` / ASCII-only-header workaround needed anymore.

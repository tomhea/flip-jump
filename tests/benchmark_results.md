# Interpreter benchmark results (WI-A, flipjump 1.5.0)

Benchmark: `python tests/benchmark_interpreter.py 2000` — `prime_sieve.fj`, sieve up to 2000,
`FixedIO` input, statistics timer (IO-paused) as the denominator.

## Baseline — fj==1.4.0 interpreter (commit 4da18b7)

Hardware: Windows 11 Pro, CPython 3.11.0.

| width | ops        | time   | speed        |
|-------|-----------:|-------:|-------------:|
| w=32  |  6,753,189 | 40.10s | 168,418 fj/s |
| w=64  | 13,486,652 | 90.93s | 148,321 fj/s |

Calibration: a minimal synthetic dict-based fetch/flip/jump loop runs at ~4.9M ops/s in CPython
on this machine — the upper bound for any pure-Python interpreter here. The ≥10M fj/s target
therefore requires the native fallback (MSVC Build Tools available on this machine).

## Python fast-loop (fast-run mode, fallback default since 1.5.0)

The run-loop with inlined memory accesses and IO/termination checks, per-op statistics skipped.

| width | ops        | time   | speed          | vs baseline |
|-------|-----------:|-------:|---------------:|------------:|
| w=32  |  6,753,189 |  1.75s | 3,866,762 fj/s |       23.0x |
| w=64  | 13,486,652 |  9.15s | 1,474,358 fj/s |        9.9x |

w=64 is markedly slower than w=32: addresses are >2^60 (prime_sieve's table sits at 1<<63), so
every int is a multi-digit CPython PyLong, and the small-int fast paths don't apply.

## Native engine (_fjcore C-extension, default since 1.5.0 when built)

Segment-aware paged memory (lazily-allocated 128KB pages) + the run-loop in C; Python is
called back only for IO. Build with `python build_fjcore.py`.

| width | n      | ops           | time   | speed            | vs baseline |
|-------|-------:|--------------:|-------:|-----------------:|------------:|
| w=32  |  5,000 |    16,580,560 |  0.17s |  96,305,331 fj/s |        572x |
| w=64  |  5,000 |    33,304,073 |  0.34s |  96,574,982 fj/s |        651x |
| w=64  | 200,000| 1,332,300,215 | 12.83s | 103,819,945 fj/s |        700x |

**The ≥10M fj/s acceptance is met with ~10x margin on every row.**

## Native-engine optimization history (i7-12700H, P-core ~4.6GHz)

| step | sieve w=32 | sieve w=64 | sieve w=64 1.3B-op | loop w=32 (compact) |
|---|---:|---:|---:|---:|
| v1: 1-entry page cache | 78M | 84M | 40M | - |
| v2: 16-way direct-mapped page cache | 96M | 97M | 104M | - |
| v3: one page lookup per op-pair | 127M | 129M | 140M | 123M |
| v4: flat storage for compact programs | 112-127M | 115-129M | 125-140M | 246M |
| v5: dedicated flat loop (no ring/paged branches) | - | - | - | 273M |
| v6: + MSVC PGO (`build_fjcore.py --pgo-*`, optional) | 122M | 128M | 132M | **280-286M** |

- v2: the ip/jump page and the flip-target page alternated every op and thrashed the single
  cached entry, forcing a hash lookup per access.
- v3: an op's flip-word and jump-word are adjacent (word_address, word_address+1) - one page
  lookup serves both (~30%).
- v4 (flat storage): programs whose segments all end below 8M words, at w<=32 with
  garbage-stop, get one dense array instead of the page table; out-of-segment words carry a
  bit-63 sentinel. This removes the page lookup from the serial jump-dependency chain
  (jump-word load -> next op's address -> next load), which bounds the loop: ~2x on
  compact-memory programs (DOOM's layout). prime_sieve declares a half-address-space segment,
  so it stays on the paged path (rows unchanged, run-to-run variance shown).
  `FLIPJUMP_NO_FLAT=1` forces the paged path (for A/B measurement).

- v5: when the memory is flat and no last-ops ring is requested (the shipping default),
  a dedicated loop runs with zero paged-mode/ring branches in the per-op path.
- v6: profile-guided optimization is available for local builds
  (`--pgo-instrument`, train on both the flat and paged paths, `--pgo-use`);
  the prebuilt wheels ship without it.

Cycle accounting at ~4.6GHz: v1 was ~46 CPU-cycles per fj-op, v6-flat is ~16. The serial
dependency floor (jump-word load -> address arithmetic -> next jump-word load, L1-resident)
is ~7-8 cycles/op (~600M fj/s); the paged-path floor is ~13-15 cycles (~330M fj/s).

(prime_sieve at w=32 is limited to n <= ~5792: its mark-pointer `p*p*dw` wraps the 2^32-bit
address space beyond that — a property of the program, reproduced identically on all engines.)

## OQ-A1 — decoded-op cache: measured, and rejected

A decoded-op cache prototype (cache `ip -> (flip_word_addr, flip_bit, jump_word_addr)`, with
the address-keyed invalidation dirty-check on every flip) was measured against the direct
loop in an op-shaped synthetic benchmark (CPython 3.11):

- w=32-like ints: direct 7.32M op/s, cached 8.88M op/s (**1.21x**)
- w=64-like ints: direct 5.70M op/s, cached 7.24M op/s (**1.27x**)

The dirty-check (one dict membership test per flip) eats roughly half of what the cache saves.
Diluted by the rest of the real loop (IO checks, termination checks, op counting), the
end-to-end gain is ~10% — and the pure-Python loop cannot approach 10M fj/s either way (the
synthetic no-op-body ceiling on this machine is ~4.9M). The native engine reads decoded words
from dense pages directly (no decode step exists), so a cache buys nothing there. Decision:
**no decoded-op cache**; the native engine is the speed path, the plain fast loop the fallback.

## w=32 vs w=64 — recommendation: **w=32** (for DOOM and op-heavy programs)

- **Op count (dominant factor):** hex/bit STL macro costs scale with w (`hex.add` is O(w/4)
  ops, pointers/wflip are O(w) flips). The same algorithm runs ~2x fewer fj-ops at w=32 —
  prime_sieve(2000) is 6.75M ops at w=32 vs 13.49M at w=64.
- **Native-engine per-op speed:** roughly equal (78M vs 84M fj/s) — so halving the op count
  halves wall-time. End-to-end, w=32 is ~2x faster for the same program.
- **Python-fallback per-op speed:** w=32 is 2.6x faster per-op (PyLong digit effects), on top
  of the op-count halving.
- **Memory:** native pages store 8B/word regardless of w, so footprint is the same per touched
  word — but w=32 programs touch half the words. The .fjm file is also half the size.
- **Fixed-point fit:** DOOM's 16.16 fixed-point fits w=32 exactly. The intermediate-width trap
  (U5): a 16.16 multiply needs a 64-bit product — two words + hand-carried overflow at w=32
  (extra ops in FixedMul, budgeted in WI-D), free at w=64. The LUT-heavy design (WI-D) keeps
  runtime multiplies rare, so this doesn't flip the verdict.
- **Address-space caveat:** w=32 has 2^32 bits of address space. Compact fixed layouts (DOOM's)
  fit easily, but quadratic pointer arithmetic can wrap (see the prime_sieve note above) —
  keep address computations bounded.

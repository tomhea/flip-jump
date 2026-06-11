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

The shipping engine (v6 below; sieve = sparse/paged path, loop = compact/flat path):

| program            | width | ops           | speed             | vs baseline |
|--------------------|-------|--------------:|------------------:|------------:|
| sieve (n=5,000)    | w=32  |    16,580,560 |  ~122M fj/s       |        727x |
| sieve (n=5,000)    | w=64  |    33,304,073 |  ~128M fj/s       |        864x |
| sieve (n=200,000)  | w=64  | 1,332,300,215 |  ~132M fj/s       |        892x |
| loop (compact)     | w=32  |   298,927,147 |  ~280M fj/s       |      1,664x |

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

### Re-measurement at the 1.5.0 finish-up (PGO rebuild, June 2026)

After the finish-up engine changes (configurable flat limit + storage-mode getter +
speculation counting mode - none on the per-op paths) the engine was PGO-rebuilt (trained
on both loop and sieve) and re-measured: **loop w=32 334M fj/s** (above the recorded
280-286M), sieve w=32/w=64 ~97-105M on short runs, and 72M on the sustained 1.3B-op run.
The sustained-run gap vs the recorded 132M is machine-state, not code: the pre-change
commit was rebuilt and measured in an A/B worktree the same hour and gives the same 71M -
long runs on this laptop decay from boost clocks. Short-run paged numbers sit within the
historical 96-140M band.

## WI-E - assembler speedup (1.5.0)

Benchmark: `python tests/benchmark_assembler.py` - three workload shapes: hello_world.fj
(the per-program fixed cost), prime_sieve.fj (macro-heavy), and a generated 64K-entry
byte-LUT program (data-heavy, the DOOM-mega-table shape). Acceptance: bit-identical .fjm
outputs - verified by sha256 on 14 outputs (10 catalog programs across categories + the 3
workloads, w=64 and w=32), cold- and warm-cache, before vs after.

What changed (all output-preserving):
- **Expr sharing** (`expr.py`): `eval_new` returns unchanged (sub)expressions as-is instead
  of deep-cloning them - Expr objects are immutable, so trees share nodes. Substituting a
  parameter is now a node swap, not a clone of the parameter's tree. Single-pass
  fold/unchanged detection. `FlipJump`/`WordFlip` ops likewise return themselves when
  nothing was substituted. This was the dominant macro-resolve cost (~1.1M `eval_new`
  calls assembling prime_sieve).
- **stl-prefix parse cache** (`fj_parser.py`): the parser state after the stl files (the
  consts + macros dicts and the main macro's ops) is snapshotted once per
  (stl files mtime/size, w, werror) and reused by every later assemble in the process.
  The parsed Macro/op objects are immutable from then on (the preprocessor
  clones-or-shares, never mutates), so sharing them is safe. This removes the ~0.13s
  per-program fixed cost the catalog used to pay ~1,000 times.
- `exact_eval` fast paths (labels resolve); bulk `struct.pack` of the data words and a
  lazy error-string in `add_segment` (fjm_writer).

| workload | before | after | speedup | now dominated by |
|---|---:|---:|---:|---|
| hello_world | 0.149s | 0.020s (warm) | 7.5x | stl parse (cold only) |
| prime_sieve | 2.35s | 1.58s | 1.5x | macro resolve + lzma |
| lut64k (64K-entry LUT) | 5.31s | 4.03s | 1.3x | SLY parsing of 64K data lines |
| catalog compile (1,029 programs) | ~14 min | 9:03 | 1.55x | per-program macro resolve |

Known remaining costs (documented, not pursued): the SLY lexer/parser's pure-python
per-token overhead dominates mega-table source files (~2.4s of lut64k - generating tables
as fewer, longer lines or assembling them once into a library would sidestep it); LZMA
compression (preset 6) is most of "create binary" and is part of the .fjm format itself.

## WI-F - jump-target speculation: miss-rate study. Verdict: **GO**

The native engine is bounded (~16 cycles/op flat) by the serial chain: this op's jump-word
load -> next op address -> next load. Jump-target speculation (remember the last jump target
per op address, start the next op's loads early, verify) only pays if the jump word at a
given ip rarely changes between executions. Measured with the exact counting mode
(`FLIPJUMP_MEASURE_SPECULATION=1` -> a dedicated slow reference loop in `_fjcore`, normal
hot paths untouched; `python tests/measure_speculation.py`):

| program | ops | first executions | misses | miss-rate | warm miss-rate |
|---|---:|---:|---:|---:|---:|
| loop w=32 (flat) | 298,927,147 | 387 | 22,666,658 | 7.58% | 7.58% |
| loop w=64 (paged) | 351,500,749 | 497 | 22,666,658 | 6.45% | 6.45% |
| sieve w=32 n=5000 (paged) | 16,580,560 | 34,947 | 1,032,607 | 6.23% | 6.24% |
| sieve w=64 n=5000 (paged) | 33,304,073 | 59,960 | 1,884,740 | 5.66% | 5.67% |
| hexlib mul64 | 984,638 | 46,719 | 85,587 | 8.69% | 9.13% |
| hexlib add_mul64 | 197,868 | 45,808 | 15,549 | 7.86% | 10.23% |
| hexlib div test8_8 | 161,920 | 15,884 | 8,537 | 5.27% | 5.85% |
| hexlib idiv | 308,357 | 31,060 | 19,218 | 6.23% | 6.93% |

(A miss = an executed op whose jump word differs from its value on the previous execution of
the same ip; "warm" excludes each ip's first execution from the denominator.)

**Every workload sits at 5.3-8.7% - below the ~10% GO threshold.** The FlipJump property
holds as conjectured: most executed ops (truth-table cells, straight-line code) have jump
words that never change after init; wflip-mutability concentrates in few dispatch/return
cells. With a correctly-predicted op the next op's two loads start one serial-chain step
early, so the expected gain is +50-80% on the flat path (~450-600M fj/s).
**Verdict: GO - build the speculation tier** (as engine work after 1.5.0; the 160x100@25fps
game target already fits the current engine, so this tier is headroom, not a dependency).


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

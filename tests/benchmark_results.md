# Interpreter benchmark results (WI-A, flipjump 1.5.0)

Benchmark: `python scripts/benchmark_interpreter.py 2000` — `prime_sieve.fj`, sieve up to 2000,
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

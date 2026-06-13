"""
The jump-target speculation miss-rate measurement.

Measures, per program, how often an executed op's jump word differs from its value on the
previous execution of the same ip - the would-be miss-rate of a "remember the last jump
target per op" speculation tier in the native engine. The measurement runs in _fjcore's
dedicated slow reference loop (FLIPJUMP_MEASURE_SPECULATION=1), so the numbers are exact
and the normal engines' hot paths are untouched.

Usage:
    python tests/benchmarks/measure_speculation.py

The verdict lives in tests/benchmarks/benchmark_results.md (the "speculation study" section).
"""

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

os.environ['FLIPJUMP_MEASURE_SPECULATION'] = '1'

from flipjump.interpreter import fjm_run  # noqa: E402
from flipjump.interpreter.io_devices.FixedIO import FixedIO  # noqa: E402
from tests.benchmarks.benchmark_interpreter import get_benchmark_fjm  # noqa: E402

HEXLIB_DIR = REPO_ROOT / 'tests' / 'compiled' / 'hexlib_tests'


def measure(name: str, fjm_path: Path, fixed_input: bytes) -> None:
    statistics = fjm_run.run(fjm_path, io_device=FixedIO(fixed_input), print_time=False)
    stats = statistics.speculation_stats
    assert stats is not None, 'the native engine (with FLIPJUMP_MEASURE_SPECULATION=1) is required'
    ops, first, misses = stats['ops'], stats['first_executions'], stats['misses']
    repeated = ops - first
    miss_rate = misses / ops if ops else 0.0
    warm_miss_rate = misses / repeated if repeated else 0.0
    print(
        f'{name:24}: {ops:>13,} ops, {first:>9,} first-executions, {misses:>11,} misses '
        f'=> miss-rate {miss_rate:7.3%} (warm {warm_miss_rate:7.3%})'
    )


def main() -> None:
    print('speculation miss-rate (jump word differs from its previous execution at the same ip;')
    print('"warm" excludes each ip\'s first execution from the denominator):\n')

    for width in (32, 64):
        measure(f'loop w={width}', get_benchmark_fjm('loop', width), b'')
    for width in (32, 64):
        measure(f'sieve w={width} (n=5000)', get_benchmark_fjm('sieve', width), b'5000\n')

    for hexlib_name in ('mul/mul64', 'mul/add_mul64', 'div/test8_8', 'div/test_idiv'):
        fjm_path = HEXLIB_DIR / (hexlib_name + '.fjm')
        if fjm_path.exists():
            measure(f'hexlib {hexlib_name}', fjm_path, b'')
        else:
            print(f'hexlib {hexlib_name:16}: SKIPPED (not compiled - run pytest --hexlib first)')


if __name__ == '__main__':
    main()

"""
The interpreter speed benchmark (fj/s) - prime_sieve.fj at w=32 and w=64.

Used to track the interpreter speedup work (flipjump 1.5.0, WI-A):
every interpreter change is measured against the recorded baseline in
scripts/benchmark_results.md.

Usage:
    python scripts/benchmark_interpreter.py [n=10000] [--w 32 64] [--fast]

The compiled .fjm files are cached under tests/compiled/benchmark/ (keyed by width),
so only the first invocation pays the assemble time.
"""

import argparse
import sys
from pathlib import Path
from time import time

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from flipjump import assemble  # noqa: E402
from flipjump.interpretter import fjm_run  # noqa: E402
from flipjump.interpretter.io_devices.FixedIO import FixedIO  # noqa: E402
from flipjump.utils.classes import TerminationCause  # noqa: E402

PRIME_SIEVE_FJ = REPO_ROOT / 'programs' / 'prime_sieve.fj'
COMPILED_DIR = REPO_ROOT / 'tests' / 'compiled' / 'benchmark'


def get_benchmark_fjm(memory_width: int) -> Path:
    """assemble prime_sieve.fj at the given width (cached on disk)."""
    COMPILED_DIR.mkdir(parents=True, exist_ok=True)
    fjm_path = COMPILED_DIR / f'prime_sieve_w{memory_width}.fjm'
    if not fjm_path.exists() or fjm_path.stat().st_mtime < PRIME_SIEVE_FJ.stat().st_mtime:
        print(f'assembling prime_sieve.fj at w={memory_width}...')
        assemble([PRIME_SIEVE_FJ], fjm_path, memory_width=memory_width, print_time=False)
    return fjm_path


def benchmark(memory_width: int, n: int) -> None:
    fjm_path = get_benchmark_fjm(memory_width)
    io_device = FixedIO(f'{n}\n'.encode())

    start_time = time()
    termination_statistics = fjm_run.run(
        fjm_path,
        io_device=io_device,
        print_time=False,
        last_ops_debugging_list_length=None,
    )
    wall_time = time() - start_time

    assert (
        termination_statistics.termination_cause == TerminationCause.Looping
    ), f'benchmark run failed: {termination_statistics.termination_cause}'

    ops = termination_statistics.op_counter
    run_time = termination_statistics.run_time
    print(f'w={memory_width}: {ops:,} ops in {run_time:.2f}s (wall {wall_time:.2f}s) ' f'=> {ops / run_time:,.0f} fj/s')


def main() -> None:
    parser = argparse.ArgumentParser(description='FlipJump interpreter speed benchmark (prime_sieve.fj)')
    parser.add_argument('n', type=int, nargs='?', default=10000, help='sieve upper bound (default 10000)')
    parser.add_argument('--w', type=int, nargs='+', default=[32, 64], help='memory widths to benchmark')
    args = parser.parse_args()

    for memory_width in args.w:
        benchmark(memory_width, args.n)


if __name__ == '__main__':
    main()

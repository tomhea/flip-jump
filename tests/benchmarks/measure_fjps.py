"""
Best-of-N fj/s for the flat (loop) and paged (sieve) benchmark programs at w=32 and w=64.

Measures whatever _fjcore is currently built - rebuild the engine with the compiler/flags under
test, then run this. Raw fj/s (best of N runs; peak = the least-throttled sample) is the reliable
SAME-MACHINE comparison: build A and build B on the same runner and the only variable is the
toolchain. No frequency probe / cycles-per-op here on purpose - an accurate effective clock needs
the APERF/MPERF MSRs (kernel-only), so a userspace probe would skew cross-build numbers; for a
same-machine A/B, fj/s is directly comparable and needs no clock.

Prints one CSV row per (program,width): `<label>,<program>,w<width>,<best_fj_per_sec>` so several
builds' outputs concatenate into one table.

Usage:  python tests/benchmarks/measure_fjps.py [--runs 9] [--n 5000] [--label gcc-O2]
"""

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from flipjump import assemble  # noqa: E402
from flipjump.interpreter import fjm_run, _fjcore  # type: ignore[attr-defined]  # noqa: E402
from flipjump.interpreter.io_devices.FixedIO import FixedIO  # noqa: E402
from flipjump.utils.classes import TerminationCause  # noqa: E402

PROGRAMS = {
    'loop': REPO_ROOT / 'tests' / 'benchmarks' / 'benchmark_loop.fj',
    'sieve': REPO_ROOT / 'programs' / 'prime_sieve.fj',
}
COMPILED_DIR = REPO_ROOT / 'tests' / 'compiled' / 'benchmark'


def best_fj_per_sec(fjm_path: Path, run_input: bytes, runs: int) -> float:
    best = 0.0
    for _ in range(runs):
        stats = fjm_run.run(fjm_path, io_device=FixedIO(run_input), print_time=False, last_ops_debugging_list_length=None)
        assert stats.termination_cause == TerminationCause.Looping, stats.termination_cause
        best = max(best, stats.op_counter / max(stats.run_time, 1e-9))
    return best


def main() -> None:
    parser = argparse.ArgumentParser(description='best-of-N fj/s for the benchmark programs')
    parser.add_argument('--runs', type=int, default=9, help='runs per measurement (best is kept)')
    parser.add_argument('--n', type=int, default=5000, help='sieve upper bound (keep <= 5000 at w=32)')
    parser.add_argument('--label', default='build', help='row label identifying this build')
    args = parser.parse_args()

    if _fjcore is None:
        sys.exit('the native engine (_fjcore) is not built - nothing to measure')

    COMPILED_DIR.mkdir(parents=True, exist_ok=True)
    for name, fj_path in PROGRAMS.items():
        run_input = f'{args.n}\n'.encode() if name == 'sieve' else b''
        for width in (32, 64):
            fjm_path = COMPILED_DIR / f'{name}_w{width}.fjm'
            assemble([fj_path], fjm_path, memory_width=width, print_time=False)
            fj_per_sec = best_fj_per_sec(fjm_path, run_input, args.runs)
            print(f'{args.label},{name},w{width},{fj_per_sec:.0f}')


if __name__ == '__main__':
    main()

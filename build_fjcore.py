"""
Build the optional native interpreter engine (flipjump/interpreter/_fjcore.c) in-place.

    python build_fjcore.py [--pgo-instrument | --pgo-use]

Requires a C compiler (MSVC Build Tools on Windows, gcc/clang elsewhere).
The flipjump package works without it - the interpreter falls back to the pure-Python
fast loop; the native engine is a ~100x speedup on top of that.

PGO (MSVC, optional): build with --pgo-instrument, run a training workload
(e.g. python tests/benchmark_interpreter.py --program loop --w 32), then rebuild
with --pgo-use.
"""

import sys

from setuptools import Extension, setup


def main() -> None:
    args = [arg for arg in sys.argv[1:] if not arg.startswith('--pgo')]
    extra_link_args = []
    if '--pgo-instrument' in sys.argv:
        extra_link_args = ['/GENPROFILE']
    elif '--pgo-use' in sys.argv:
        extra_link_args = ['/USEPROFILE']

    setup(
        name='flipjump-fjcore',
        ext_modules=[
            Extension(
                'flipjump.interpreter._fjcore',
                sources=['flipjump/interpreter/_fjcore.c'],
                extra_link_args=extra_link_args,
                py_limited_api=True,  # abi3: one binary covers every CPython >= 3.10
            )
        ],
        script_args=['build_ext', '--inplace', '--force'] + args,
    )


if __name__ == '__main__':
    main()

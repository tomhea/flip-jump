"""
Build the optional native interpreter engine (flipjump/interpreter/_fjcore.c) in-place.

    python build_fjcore.py

Requires a C compiler (MSVC Build Tools on Windows, gcc/clang elsewhere).
The flipjump package works without it - the interpreter falls back to the pure-Python
fast loop; the native engine is a ~30x speedup on top of that.
"""

import sys

from setuptools import Extension, setup


def main() -> None:
    setup(
        name='flipjump-fjcore',
        ext_modules=[
            Extension(
                'flipjump.interpreter._fjcore',
                sources=['flipjump/interpreter/_fjcore.c'],
            )
        ],
        script_args=['build_ext', '--inplace'] + sys.argv[1:],
    )


if __name__ == '__main__':
    main()

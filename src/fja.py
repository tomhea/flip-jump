#!/usr/bin/env python3

from assembler import assemble

from os.path import isfile, abspath, isdir
import argparse
from defs import *


def main():
    parser = argparse.ArgumentParser(description='Assemble and Run FlipJump programs.')
    parser.add_argument('file', help="the FlipJump file.", nargs='+')
    parser.add_argument('-s', '--silent', help="don't show assemble & run times", action='store_true')
    parser.add_argument('-o', '--outfile', help="output assembled file.", default="a.blm")
    parser.add_argument('--no-macros', help="output no-macros file.", default="a__no_macros.fj")
    parser.add_argument('-d', '--debug', help="output debug file (used for breakpoints).", default="a.fj_debug")
    parser.add_argument('-f', '--flags', help="default running flags", type=int, default=0)
    parser.add_argument('-w', '--width', help="specify memory-width. 64 by default",
                        type=int, default=64, choices=[8, 16, 32, 64])
    parser.add_argument('--no-stl', help="don't assemble/link the standard library files.", action='store_true')
    args = parser.parse_args()

    if not args.no_stl:
        args.file = stl() + args.file

    verbose_set = set()
    if not args.silent:
        verbose_set.add(Verbose.Time)

    for file in args.file:
        file = abspath(file)
        if not file.endswith('.fj'):
            parser.error(f'file {file} is not a .fj file.')
        if not isfile(abspath(file)):
            parser.error(f'file {file} does not exist.')

    assemble(args.file, args.outfile, args.width, flags=args.flags,
             preprocessed_file=args.no_macros, debugging_file=args.debug, verbose=verbose_set)



    # for test, _input in (('cat', "Hello World!\0"), ('ncat', ''.join(chr(0xff-ord(c)) for c in 'Flip Jump Rocks!\0')),
    #                      ('testbit', ''), ('testbit_with_nops', ''), ('mathbit', ''), ('mathvec', ''), ('not', ''),
    #                      ('rep', ''), ('ncmp', ''), ('nadd', ''), ('hexprint', ''), ('simple', ''), ('hello_world', ''),
    #                      ('ptr', ''), ('func', ''), ('print_hex_int', ''), ('calc', 'x82+x8f\nx152+x23\nx134\nx6-x15\nx132-x111\nx1234+x4321\n-x67\nxf+xfff6\nx1000b-xf\nxd0a0c0d0+x0e0d000e\nq\n')):
    #     # if test in ('func', 'calc'):
    #     #     continue
    #     if test not in (
    #             'calc',
    #     #         'print_hex_int',
    #             ):
    #         continue
    #     print(f'running test {test}({_input}):')
    #     run_time, ops_executed, output, finish_cause = assemble_and_run([f'tests/{test}.fj'], 64,
    #                     preprocessed_file=f'tests/compiled/{test}__no_macros.fj',
    #                     debugging_file=f'tests/compiled/{test}.fj_debug',
    #                     output_file=f'tests/compiled/{test}.blm',
    #                     defined_input=None,
    #                     verbose=set([
    #                         Verbose.Time,
    #                         Verbose.PrintOutput,
    #                         # Verbose.Run,
    #                     ]),
    #                     breakpoint_labels=set([
    #                         # '__to_jump',
    #                     ]),
    #                     breakpoint_any_labels=set([
    #                         # 'gibly',
    #                     ]))
    #     # print(output)
    #     print(f'finished by {finish_cause.value} after {run_time:.3f}s ({ops_executed} ops executed)')
    #     print()


if __name__ == '__main__':
    main()

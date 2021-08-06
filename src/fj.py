#!/usr/bin/env python3

from assembler import assemble
from run import debug_and_run

import os
from os.path import isfile, abspath, isdir, join
import difflib
from tempfile import mkstemp
import argparse
from defs import *


def main():
    parser = argparse.ArgumentParser(description='Assemble and Run FlipJump programs.')
    parser.add_argument('file', help="the FlipJump files.", nargs='+')
    parser.add_argument('-s', '--silent', help="don't show assemble & run times", action='store_true')
    parser.add_argument('-o', '--outfile', help="output assembled file.")
    parser.add_argument('--no-macros', help="output no-macros file.")
    parser.add_argument('-d', '--debug', help="debug file (used for breakpoints).", nargs='?', const=0)
    parser.add_argument('-f', '--flags', help="running flags", type=int, default=0)
    parser.add_argument('-w', '--width', help="specify memory-width. 64 by default.",
                        type=int, default=64, choices=[8, 16, 32, 64])
    parser.add_argument('--Werror', help="make all warnings into errors.", action='store_true')
    parser.add_argument('--no-stl', help="don't assemble/link the standard library files.", action='store_true')
    parser.add_argument('--stats', help="show macro usage statistics.", action='store_true')
    parser.add_argument('-t', '--test', help="expects paths to input/expected-output files "
                                             "(s.t. the files are path.in, path.out)", nargs='+')
    parser.add_argument('-b', '--breakpoint', help="pause when reaching this label",
                        default=[], action='append')
    parser.add_argument('-B', '--any_breakpoint', help="pause when reaching any label containing this",
                        default=[], action='append')

    args = parser.parse_args()



    ##### - ASSEMBLE

    verbose_set = set()
    if not args.silent:
        verbose_set.add(Verbose.Time)

    if not args.no_stl:
        args.file = stl() + args.file
    for file in args.file:
        file = abspath(file)
        if not file.endswith('.fj'):
            parser.error(f'file {file} is not a .fj file.')
        if not isfile(abspath(file)):
            parser.error(f'file {file} does not exist.')

    temp_assembled_file, temp_assembled_fd = False, 0
    if args.outfile is None:
        temp_assembled_fd, args.outfile = mkstemp()
        temp_assembled_file = True
    else:
        if not args.outfile.endswith('.fjm'):
            parser.error(f'output file {args.outfile} is not a .fjm file.')

    temp_debug_file, temp_debug_fd = False, 0
    if args.debug == 0:
        temp_debug_fd, args.debug = mkstemp()
        temp_debug_file = True

    assemble(args.file, args.outfile, args.width, args.Werror, flags=args.flags,
             show_statistics=args.stats,
             preprocessed_file=args.no_macros, debugging_file=args.debug, verbose=verbose_set)

    if temp_assembled_file:
        os.close(temp_assembled_fd)



    ##### - RUN

    verbose_set = set() if args.test else {Verbose.PrintOutput}
    if not args.silent:
        verbose_set.add(Verbose.Time)

    if args.test:
        failures = []
        total = 0
        for test in args.test:
            total += 1
            infile = f'{test}.in'
            outfile = f'{test}.out'
            if not isfile(infile):
                print(f'test "{test}" missing an infile ("{infile}").')
                failures.append(file)
                continue
            if not isfile(outfile):
                print(f'test "{test}" missing an outfile ("{outfile}").')
                failures.append(file)
                continue

            print(f'running {Path(file).name}:')
            with open(infile, 'r') as inf:
                test_input = inf.read()
            with open(outfile, 'r') as outf:
                expected_output = outf.read()
            run_time, ops_executed, output, finish_cause = \
                debug_and_run(args.outfile,
                              defined_input=test_input,
                              verbose=verbose_set)
            if output != expected_output:
                print(f'test "{file}" failed. here\'s the diff:')
                print(''.join(difflib.context_diff(output.splitlines(1), expected_output.splitlines(1),
                                                   fromfile='assembled file' if temp_assembled_file else args.outfile,
                                                   tofile=outfile)))
                failures.append(file)

            if not args.silent:
                print(f'finished by {finish_cause.value} after {run_time:.3f}s ({ops_executed} ops executed)')
            print()

        print()
        if len(failures) == 0:
            print(f'All tests passed! 100%')
        else:
            print(f'{total-len(failures)}/{total} tests passed ({(total-len(failures))/total*100:.2f}%).')
            print(f'Failed tests:')
            for test in failures:
                print(f'  {test}')
    else:

        breakpoint_set = set(args.breakpoint)
        breakpoint_any_set = set(args.any_breakpoint)

        run_time, ops_executed, output, finish_cause = \
            debug_and_run(args.outfile, debugging_file=args.debug,
                          defined_input=None,
                          verbose=verbose_set,
                          breakpoint_labels=breakpoint_set,
                          breakpoint_any_labels=breakpoint_any_set)

        if not args.silent:
            print(f'finished by {finish_cause.value} after {run_time:.3f}s ({ops_executed} ops executed)')
            print()

    if temp_debug_file:
        os.close(temp_debug_fd)


if __name__ == '__main__':
    main()

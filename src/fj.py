import os
from os.path import isfile, abspath
from pathlib import Path
from tempfile import mkstemp

import argparse
import difflib

from assembler import assemble
from fjm_run import debug_and_run
from defs import Verbose, FJReadFjmException, FJException, get_stl_paths


def main():
    parser = argparse.ArgumentParser(description='Assemble and Run FlipJump programs.')
    parser.add_argument('file', help="the FlipJump files.", nargs='+')
    parser.add_argument('-s', '--silent', help="don't show assemble & run times", action='store_true')
    parser.add_argument('-o', '--outfile', help="output assembled file.")
    parser.add_argument('--no-macros', help="output no-macros file.")
    parser.add_argument('-d', '--debug', help="debug file (used for breakpoints).", nargs='?', const=True)
    parser.add_argument('-v', '--version', help="fjm version", type=int, default=0)
    parser.add_argument('-f', '--flags', help="default running flags", type=int, default=0)
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
        args.file = get_stl_paths() + args.file
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
    if args.debug is None and (len(args.breakpoint) > 0 or len(args.any_breakpoint) > 0):
        print(f"Warning - breakpoints are used but the debugging flag (-d) is not specified. "
              f"Debugging data will be saved.")
        args.debug = True
    if args.debug is True:
        temp_debug_fd, args.debug = mkstemp()
        temp_debug_file = True

    try:
        assemble(args.file, args.outfile, args.width,
                 version=args.version, flags=args.flags,
                 warning_as_errors=args.Werror,
                 show_statistics=args.stats, verbose=verbose_set,
                 preprocessed_file=args.no_macros, debugging_file=args.debug)
    except FJException as e:
        print()
        print(e)
        exit(1)

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
                print(f'test "{test}" missing an infile ("{infile}").\n')
                failures.append(test)
                continue
            if not isfile(outfile):
                print(f'test "{test}" missing an outfile ("{outfile}").\n')
                failures.append(test)
                continue

            print(f'running {Path(test).name}:')
            with open(infile, 'rb') as inf:
                test_input = inf.read()
            with open(outfile, 'r') as outf:
                expected_output = outf.read().encode()

            try:
                run_time, ops_executed, flips_executed, output, termination_cause = \
                    debug_and_run(args.outfile,
                                  defined_input=test_input,
                                  verbose=verbose_set)

                if bytes(output) != expected_output:
                    print(f'test "{test}" failed. here\'s the diff:')
                    print(''.join(difflib.context_diff(str(output).splitlines(True), str(expected_output).splitlines(True),
                                                       fromfile='assembled file' if temp_assembled_file else args.outfile,
                                                       tofile=outfile)))
                    failures.append(test)
                    if not args.silent:
                        print(f'finished by {termination_cause} after {run_time:.3f}s ({ops_executed:,} ops executed, {flips_executed / ops_executed * 100:.2f}% flips)')
            except FJReadFjmException as e:
                print()
                print(e)
                failures.append(test)

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

        try:
            run_time, ops_executed, flips_executed, output, termination_cause = \
                debug_and_run(args.outfile, debugging_file=args.debug,
                              defined_input=None,
                              verbose=verbose_set,
                              breakpoint_labels=breakpoint_set,
                              breakpoint_any_labels=breakpoint_any_set)
            if not args.silent:
                print(f'finished by {termination_cause} after {run_time:.3f}s ({ops_executed:,} ops executed, {flips_executed / ops_executed * 100:.2f}% flips)')
                print()
        except FJReadFjmException as e:
            print()
            print(e)
            exit(1)

    if temp_debug_file:
        os.close(temp_debug_fd)


if __name__ == '__main__':
    main()

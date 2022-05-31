#!/usr/bin/env python3
import struct

from fjm_run import debug_and_run

from os.path import isfile, abspath, isdir, join
from defs import *
from glob import glob
import argparse
import difflib

from tests import test_run_from_csv_file


def main():
    parser = argparse.ArgumentParser(description='Run FlipJump programs.')
    parser.add_argument('file', help="the FlipJump file.")
    parser.add_argument('-s', '--silent', help="don't show run times", action='store_true')
    parser.add_argument('-t', '--trace', help="trace the running opcodes.", action='store_true')
    parser.add_argument('-f', '--flags', help="running flags", type=int, default=0)
    parser.add_argument('-d', '--debug', help='debugging file')
    parser.add_argument('-b', '--breakpoint', help="pause when reaching this label",
                        default=[], action='append')
    parser.add_argument('-B', '--any_breakpoint', help="pause when reaching any label containing this",
                        default=[], action='append')
    parser.add_argument('--tests', help="run all .fjm files in the given folder (instead of specifying a file). "
                                        "Expects an input/expected-output directory. "
                                        "Each *.fjm file will be tested with "
                                        "dir/*.in as input, and its output will be compared to dir/*.out.")
    parser.add_argument('--csv_tests', help="run all fjm tests in given .csv file", nargs='+')

    args = parser.parse_args()

    if args.csv_tests is not None:
        for csv_file in args.csv_tests:
            test_run_from_csv_file(csv_file)
        print('\nFinished running all tests.')
        exit()

    verbose_set = set() if args.tests else {Verbose.PrintOutput}
    if not args.silent:
        verbose_set.add(Verbose.Time)
    if args.trace:
        verbose_set.add(Verbose.Run)

    if args.tests:
        inout_dir = args.tests
        failures = []
        total = 0
        folder = abspath(args.file)
        if not isdir(folder):
            print('Error: The "file" argument should contain a folder path.')
            exit(1)
        for file in glob(join(folder, '*.fjm')):
            total += 1
            infile = abspath(str(Path(inout_dir) / f'{Path(file).stem}.in'))
            outfile = abspath(str(Path(inout_dir) / f'{Path(file).stem}.out'))
            if not isfile(infile):
                print(f'test "{file}" missing an infile ("{infile}").\n')
                failures.append(file)
                continue
            if not isfile(outfile):
                print(f'test "{file}" missing an outfile ("{outfile}").\n')
                failures.append(file)
                continue

            print(f'running {Path(file).name}:')
            with open(infile, 'rb') as inf:
                test_input = inf.read()
            with open(outfile, 'rb') as outf:
                expected_output = outf.read()

            try:
                run_time, ops_executed, flips_executed, output, finish_cause = \
                    debug_and_run(file, defined_input=test_input, verbose=verbose_set)

                if not args.silent:
                    print(f'finished by {finish_cause.value} after {run_time:.3f}s ({ops_executed:,} ops executed, {flips_executed/ops_executed*100:.2f}% flips)')

                if output != expected_output:
                    print(f'test "{file}" failed. here\'s the diff:')
                    print(''.join(difflib.context_diff(str(output).splitlines(True), str(expected_output).splitlines(True),
                                                       fromfile=file, tofile=outfile)))
                    failures.append(file)

                if finish_cause != RunFinish.Looping:
                    print(f'test "{file}" finished unexpectedly, with {finish_cause.value}.')
                    failures.append(file)
            except FJReadFjmException as e:
                print()
                print(e)
                failures.append(file)

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

        file = abspath(args.file)
        if not isfile(file):
            parser.error(f'file {file} does not exist.')
        if not file.endswith('.fjm'):
            parser.error(f'file {file} is not a .fjm file.')

        if args.debug:
            debug_file = abspath(args.debug)
            if not isfile(debug_file):
                parser.error(f'debug-file {debug_file} does not exist.')

        breakpoint_set = set(args.breakpoint)
        breakpoint_any_set = set(args.any_breakpoint)

        try:
            run_time, ops_executed, flips_executed, output, finish_cause = \
                debug_and_run(file, debugging_file=args.debug,
                              defined_input=None,
                              verbose=verbose_set,
                              breakpoint_labels=breakpoint_set,
                              breakpoint_any_labels=breakpoint_any_set)

            if not args.silent:
                print(f'finished by {finish_cause.value} after {run_time:.3f}s ({ops_executed:,} ops executed, {flips_executed/ops_executed*100:.2f}% flips)')
                print()
        except FJReadFjmException as e:
            print()
            print(e)
            exit(1)


if __name__ == '__main__':
    main()

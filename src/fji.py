import argparse
from os.path import isfile, abspath


from fjm_run import debug_and_run
from defs import Verbose, FJReadFjmException


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

    args = parser.parse_args()

    verbose_set = {Verbose.PrintOutput}
    if not args.silent:
        verbose_set.add(Verbose.Time)
    if args.trace:
        verbose_set.add(Verbose.Run)

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
        termination_statistics = \
            debug_and_run(file, debugging_file=args.debug,
                          defined_input=None,
                          verbose=verbose_set,
                          breakpoint_labels=breakpoint_set,
                          breakpoint_any_labels=breakpoint_any_set)

        if not args.silent:
            print(termination_statistics)
    except FJReadFjmException as e:
        print()
        print(e)
        exit(1)


if __name__ == '__main__':
    main()

from os.path import isfile, abspath

import argparse

from assembler import assemble
from defs import Verbose, FJException, get_stl_paths


def main():
    parser = argparse.ArgumentParser(description='Assemble FlipJump programs.')
    parser.add_argument('file', help="the FlipJump files.", nargs='+')
    parser.add_argument('-s', '--silent', help="don't show assemble times", action='store_true')
    parser.add_argument('-o', '--outfile', help="output assembled file.", default="a.fjm")
    parser.add_argument('--no-macros', help="output no-macros file.")
    parser.add_argument('-d', '--debug', help="output debug file (used for breakpoints).")
    parser.add_argument('-v', '--version', help="fjm version", type=int, default=0)
    parser.add_argument('-f', '--flags', help="default running flags", type=int, default=0)
    parser.add_argument('-w', '--width', help="specify memory-width. 64 by default.",
                        type=int, default=64, choices=[8, 16, 32, 64])
    parser.add_argument('--Werror', help="make all warnings into errors.", action='store_true')
    parser.add_argument('--no-stl', help="don't assemble/link the standard library files.", action='store_true')
    parser.add_argument('--stats', help="show macro usage statistics.", action='store_true')
    args = parser.parse_args()

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


if __name__ == '__main__':
    main()

#!/usr/bin/env python3

from assembler import assemble

from os.path import isfile, abspath, isdir, join
from glob import glob
import argparse
from defs import *


def main():
    parser = argparse.ArgumentParser(description='Assemble FlipJump programs.')
    parser.add_argument('file', help="the FlipJump files.", nargs='+')
    parser.add_argument('-s', '--silent', help="don't show assemble times", action='store_true')
    parser.add_argument('-o', '--outfile', help="output assembled file.", default="a.fjm")
    parser.add_argument('--no-macros', help="output no-macros file.")
    parser.add_argument('-d', '--debug', help="output debug file (used for breakpoints).")
    parser.add_argument('-f', '--flags', help="default running flags", type=int, default=0)
    parser.add_argument('-w', '--width', help="specify memory-width. 64 by default.",
                        type=int, default=64, choices=[8, 16, 32, 64])
    parser.add_argument('--Werror', help="make all warnings into errors.", action='store_true')
    parser.add_argument('--no-stl', help="don't assemble/link the standard library files.", action='store_true')
    parser.add_argument('--tests', help="compile all .fj files in the given folder (instead of specifying a file).",
                        action='store_true')
    parser.add_argument('--stats', help="show macro usage statistics.", action='store_true')
    args = parser.parse_args()

    verbose_set = set()
    if not args.silent:
        verbose_set.add(Verbose.Time)

    if args.tests:
        if len(args.file) != 1 or not isdir(args.file[0]):
            parser.error('the "file" argument should contain a folder path.')
        Path.mkdir(Path(args.file[0]) / 'compiled', exist_ok=True)
        for file in glob(join(args.file[0], '*.fj')):

            # if file not in (r'tests\calc.fj', r'tests\func.fj', r'tests\hexlib.fj'):
            #     continue

            print(f'compiling {Path(file).name}:')
            no_stl = args.no_stl or 'no-stl' in Path(file).stem
            assemble([file] if no_stl else stl() + [file],
                     (Path(args.file[0]) / 'compiled' / (Path(file).stem + '.fjm')),
                     args.width, args.Werror, flags=args.flags, verbose=verbose_set)
            print()

    else:
        if not args.no_stl:
            args.file = stl() + args.file
        for file in args.file:
            file = abspath(file)
            if not file.endswith('.fj'):
                parser.error(f'file {file} is not a .fj file.')
            if not isfile(abspath(file)):
                parser.error(f'file {file} does not exist.')
        assemble(args.file, args.outfile, args.width, args.Werror, flags=args.flags,
                 show_statistics=args.stats,
                 preprocessed_file=args.no_macros, debugging_file=args.debug, verbose=verbose_set)


if __name__ == '__main__':
    main()

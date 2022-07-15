import os
import argparse
from pathlib import Path
from tempfile import mkstemp, TemporaryDirectory
from typing import Tuple, List, Set

import assembler
import fjm_run
from defs import Verbose, FJReadFjmException, get_stl_paths


def get_run_verbose_set(args: argparse.Namespace) -> Set[Verbose]:
    """
    extract the running verbose-options into a verbose-set.
    @param args: the parsed arguments
    @return: the verbose-set
    """
    verbose_set = set()

    if not args.silent:
        verbose_set.add(Verbose.Time)
    if not args.no_output:
        verbose_set.add(Verbose.PrintOutput)
    if args.trace:
        verbose_set.add(Verbose.Run)

    return verbose_set


def get_temp_directory_suffix(args: argparse.Namespace) -> str:
    """
    create a suffix for the temp directory name, using args.
    @param args: the parsed arguments
    @return: the suffix
    """
    return f'__{"_".join(map(os.path.basename, args.files))}__temp_directory'


def get_file_tuples(args: argparse.Namespace) -> List[Tuple[str, Path]]:
    """
    get the list of .fj files to be assembled (stl + files).
    @param args: the parsed arguments
    @return: a list of file-tuples - (file_short_name, file_path)
    """
    file_tuples = []

    if not args.no_stl:
        for i, stl_path in enumerate(get_stl_paths(), start=1):
            file_tuples.append((f"s{i}", stl_path))

    for i, file in enumerate(args.files, start=1):
        file_tuples.append((f"f{i}", Path(file)))

    return file_tuples


def verify_file_exists(parser: argparse.ArgumentParser, path: Path) -> None:
    """
    verify that the file exists.
    @param parser: the parser
    @param path: the file's path
    """
    if not path.is_file():
        parser.error(f'file {path} does not exist.')


def verify_fj_files(parser: argparse.ArgumentParser, file_tuples: List[Tuple[str, Path]]) -> None:
    """
    verify that all files exist and with the right suffix.
    @param parser: the parser
    @param file_tuples: a list of file-tuples - (file_short_name, file_path)
    """
    for _, path in file_tuples:
        verify_file_exists(parser, path)
        if '.fj' != path.suffix:
            parser.error(f'file {path} is not a .fj file.')


def verify_fjm_file(parser: argparse.ArgumentParser, path: Path) -> None:
    """
    verify that this file exists and with the right suffix.
    @param parser: the parser
    @param path: the file's path
    """
    verify_file_exists(parser, path)
    if '.fjm' != path.suffix:
        parser.error(f'file {path} is not a .fjm file.')


def add_run_only_arguments(parser: argparse.ArgumentParser) -> None:
    """
    add the arguments that are usable in run time.
    @param parser: the parser
    """
    run_arguments = parser.add_argument_group('run arguments', 'Ignored when using the --assemble option')

    run_arguments.add_argument('-t', '--trace', help="output every running opcode", action='store_true')
    run_arguments.add_argument('--no_output', help="don't print the program's output", action='store_true')

    run_arguments.add_argument('-b', '--breakpoint', metavar='NAME', default=[], nargs="+",
                               help="pause when reaching this label")
    run_arguments.add_argument('-B', '--breakpoint_contains', metavar='NAME', default=[], nargs="+",
                               help="pause when reaching any label containing this")


def add_assemble_only_arguments(parser: argparse.ArgumentParser) -> None:
    """
    add the arguments that are usable in assemble time.
    @param parser: the parser
    """
    asm_arguments = parser.add_argument_group('assemble arguments', 'Ignored when using the --run option')

    asm_arguments.add_argument('-o', '--outfile', metavar='PATH', help="output assembled file")

    asm_arguments.add_argument('-w', '--width', type=int, default=64, choices=[8, 16, 32, 64], metavar='WIDTH',
                               help="specify memory-width. 64 by default")
    asm_arguments.add_argument('-v', '--version', metavar='VERSION', help="fjm version", type=int, default=0)
    asm_arguments.add_argument('-f', '--flags', help="the default .fjm unpacking & running flags", type=int, default=0)

    asm_arguments.add_argument('--werror', help="treat all assemble warnings as errors", action='store_true')
    asm_arguments.add_argument('--no_stl', help="don't assemble/link the standard library files", action='store_true')
    asm_arguments.add_argument('--stats', help="show macro code-size statistics", action='store_true')


def add_universal_arguments(parser: argparse.ArgumentParser) -> None:
    """
    add the arguments that are usable in both --asm and --run options.
    @param parser: the parser
    """
    parser.add_argument('files', help="the .fj files to assemble (if run-only, the .fjm file to run)", nargs='+')
    parser.add_argument('-s', '--silent', action='store_true',
                        help="don't show assemble & run times, and run statistics")
    parser.add_argument('-d', '--debug', nargs='?', const=True, metavar='PATH',
                        help="debug-file path (used for breakpoints). If you both assemble & run, "
                             "you may use this option without specifying a path, and a temporary file will be used")


def add_command_arguments(parser: argparse.ArgumentParser) -> None:
    """
    add the mutually exclusive --asm and --run options.
    @param parser: the parser
    """
    action = parser.add_mutually_exclusive_group()
    action.add_argument('-a', '--asm', action='store_true', help="assemble only. Ignores any run-arguments")
    action.add_argument('-r', '--run', action='store_true', help="run only. Ignores any assemble-arguments")


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """
    add the parser's arguments.
    @param parser: the parser
    """
    add_command_arguments(parser)
    add_universal_arguments(parser)
    add_assemble_only_arguments(parser)
    add_run_only_arguments(parser)


def get_argument_parser() -> argparse.ArgumentParser:
    """
    create the argument parser (with specific description and usage).
    @return: the argument parser
    """
    return argparse.ArgumentParser(
        description='Assemble and Run FlipJump programs.',
        usage=f'fj.py [--asm | --run] [arguments] files [files ...]\n'
              f'example usage:\n'
              f'  fj.py a.fj b.fj                               // assemble and run\n'
              f'  fj.py a.fj b.fj -o out.fjm                    // assemble save and run\n'
              f'  fj.py code.fj -d -B swap_start exit_label     // assemble and debug\n\n'
              f'  fj.py --asm -o o.fjm a.fj -d dir/debug.fjd            // assemble and save debug info\n'
              f'  fj.py --asm -o output.fjm a.fj b.fj --no_stl -w 32    '
              f'// assemble without the standard library, 32 bit memory\n\n'
              f'  fj.py --run prog.fjm                              // just run\n'
              f'  fj.py --run o.fjm -d dir/debug.fjd -B label       // run and debug'
    )


def main():
    # TODO document and move up fj.py
    # TODO remove mkstemp from all directories

    parser = get_argument_parser()
    add_arguments(parser)
    args = parser.parse_args()

    execute_assemble_run(args, parser)


def execute_assemble_run(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    with TemporaryDirectory(suffix=get_temp_directory_suffix(args)) as temp_dir_name:
        out_fjm_file = get_fjm_file_path(args, parser, temp_dir_name)
        debug_file = get_debug_file_path(args, temp_dir_name)
        fjm_file_to_run = args.files[0] if args.run else out_fjm_file

        if not args.run:
            assemble(out_fjm_file, debug_file, args, parser)

        if not args.asm:
            run(fjm_file_to_run, debug_file, args, parser)


def run(fjm_file_to_run: Path, debug_file: Path, args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    verify_fjm_file(parser, fjm_file_to_run)
    if debug_file:
        verify_file_exists(parser, debug_file)

    verbose_set = get_run_verbose_set(args)

    breakpoint_set = set(args.breakpoint)
    breakpoint_contains_set = set(args.breakpoint_contains)

    try:
        termination_statistics = \
            fjm_run.debug_and_run(fjm_file_to_run,
                                  debugging_file=debug_file,
                                  defined_input=None,
                                  verbose=verbose_set,
                                  breakpoint_labels=breakpoint_set,
                                  breakpoint_contains_labels=breakpoint_contains_set)
        if not args.silent:
            print(termination_statistics)
    except FJReadFjmException as e:
        print()
        print(e)
        exit(1)


def assemble(out_fjm_file: Path, debug_file: Path, args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    file_tuples = get_file_tuples(args)
    verify_fj_files(parser, file_tuples)

    assembler.assemble(file_tuples, out_fjm_file, args.width,
                       version=args.version, flags=args.flags,
                       warning_as_errors=args.werror,
                       show_statistics=args.stats, print_time=not args.silent,
                       debugging_file=debug_file)


def get_fjm_file_path(args: argparse.Namespace, parser: argparse.ArgumentParser, temp_dir_name: str) -> Path:
    """
    get the output-fjm path from args. If unspecified, create a temporary file under temp_dir_name.
    @param args: the parsed arguments
    @param parser: the parser
    @param temp_dir_name: a temporary directory that files can safely be created in
    @return: the output-fjm path
    """
    out_fjm_file = args.outfile

    if out_fjm_file is None:
        if args.asm:
            parser.error(f'assemble-only is used, but no outfile is specified.')
        out_fjm_file = os.path.join(temp_dir_name, 'out.fjm')
    elif not out_fjm_file.endswith('.fjm'):
        parser.error(f'output file {out_fjm_file} is not a .fjm file.')

    return Path(out_fjm_file)


def get_debug_file_path(args, temp_dir_name):
    debug_file = args.debug
    debug_file_needed = not args.asm and any((args.breakpoint, args.breakpoint_contains))

    if debug_file is None and debug_file_needed:
        if not args.silent:
            print(f"Parser Warning - breakpoints are used but the debugging flag (-d) is not specified. "
                  f"Debugging data will be saved.")
        debug_file = True

    if debug_file is True:
        debug_file = os.path.join(temp_dir_name, 'debug.fjd')

    if isinstance(debug_file, str):
        debug_file = Path(debug_file)

    return debug_file


if __name__ == '__main__':
    main()

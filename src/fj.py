import os
import argparse
import lzma
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Tuple, List, Callable

import assembler
import fjm_run
import fjm
from io_devices.StandardIO import StandardIO

from defs import get_stl_paths
from exceptions import FJReadFjmException
from breakpoints import get_breakpoint_handler

ErrorFunc = Callable[[str], None]


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


def verify_file_exists(error_func: ErrorFunc, path: Path) -> None:
    """
    verify that the file exists.
    @param error_func: the parser's error function
    @param path: the file's path
    """
    if not path.is_file():
        error_func(f'file {path} does not exist.')


def verify_fj_files(error_func: ErrorFunc, file_tuples: List[Tuple[str, Path]]) -> None:
    """
    verify that all files exist and with the right suffix.
    @param error_func: the parser's error function
    @param file_tuples: a list of file-tuples - (file_short_name, file_path)
    """
    for _, path in file_tuples:
        verify_file_exists(error_func, path)
        if '.fj' != path.suffix:
            error_func(f'file {path} is not a .fj file.')


def verify_fjm_file(error_func: ErrorFunc, path: Path) -> None:
    """
    verify that this file exists and with the right suffix.
    @param error_func: the parser's error function
    @param path: the file's path
    """
    verify_file_exists(error_func, path)
    if '.fjm' != path.suffix:
        error_func(f'file {path} is not a .fjm file.')


def get_files_paths(args: argparse.Namespace, error_func: ErrorFunc, temp_dir_name: str) -> Tuple[Path, Path, Path]:
    """
    generate the files paths from args, and create temp paths under temp_dir_name if necessary.
    @param args: the parsed arguments
    @param error_func: parser's error function
    @param temp_dir_name: the temp directory's name
    @return: the path of the debug-file, the (to-be-compiled) fjm, and the input fjm
    """
    out_fjm_path = get_fjm_file_path(args, error_func, temp_dir_name)
    debug_path = get_debug_file_path(args, error_func, temp_dir_name)
    in_fjm_path = Path(args.files[0]) if args.run else out_fjm_path

    return debug_path, in_fjm_path, out_fjm_path


def run(in_fjm_path: Path, debug_file: Path, args: argparse.Namespace, error_func: ErrorFunc) -> None:
    """
    prepare and verify arguments and io_device, and run the .fjm program.
    @param in_fjm_path: the input .fjm-file path
    @param debug_file: the debug-file path
    @param args: the parsed arguments
    @param error_func: the parser's error function
    """
    verify_fjm_file(error_func, in_fjm_path)
    if debug_file:
        verify_file_exists(error_func, debug_file)

    breakpoint_set = set(args.breakpoint)
    breakpoint_contains_set = set(args.breakpoint_contains)

    io_device = StandardIO(not args.no_output)

    try:
        breakpoint_handler = get_breakpoint_handler(debug_file, set(), breakpoint_set, breakpoint_contains_set)
        termination_statistics = fjm_run.run(
            in_fjm_path,
            io_device=io_device,
            show_trace=args.trace,
            time_verbose=not args.silent,
            breakpoint_handler=breakpoint_handler
        )
        if not args.silent:
            termination_statistics.print(labels_handler=breakpoint_handler,
                                         output_to_print=io_device.get_output(allow_incomplete_output=True))
    except FJReadFjmException as e:
        print()
        print(e)
        exit(1)


def get_version(args: argparse.Namespace) -> int:
    """
    @param args: the parsed arguments
    @return: the chosen version, or default if not specified
    """
    if args.version is not None:
        return args.version

    if args.outfile is not None:
        return fjm.CompressedVersion
    return fjm.NormalVersion


def assemble(out_fjm_file: Path, debug_file: Path, args: argparse.Namespace, error_func: ErrorFunc) -> None:
    """
    prepare and verify arguments, and assemble the .fj files.
    @param out_fjm_file: the to-be-compiled .fjm-file path
    @param debug_file: the debug-file path
    @param args: the parsed arguments
    @param error_func: the parser's error function
    """
    file_tuples = get_file_tuples(args)
    verify_fj_files(error_func, file_tuples)

    fjm_writer = fjm.Writer(out_fjm_file, args.width, get_version(args), flags=args.flags, lzma_preset=args.lzma_preset)
    assembler.assemble(file_tuples, args.width, fjm_writer,
                       warning_as_errors=args.werror, debugging_file_path=debug_file,
                       show_statistics=args.stats, print_time=not args.silent)


def get_fjm_file_path(args: argparse.Namespace, error_func: ErrorFunc, temp_dir_name: str) -> Path:
    """
    get the output-fjm path from args. If unspecified, create a temporary file under temp_dir_name.
    @param args: the parsed arguments
    @param error_func: the parser's error function
    @param temp_dir_name: a temporary directory that files can safely be created in
    @return: the output-fjm path
    """
    out_fjm_file = args.outfile

    if out_fjm_file is None:
        if args.asm:
            error_func(f'assemble-only is used, but no outfile is specified.')
        out_fjm_file = os.path.join(temp_dir_name, 'out.fjm')
    elif not args.run and not out_fjm_file.endswith('.fjm'):
        error_func(f'output file {out_fjm_file} is not a .fjm file.')

    return Path(out_fjm_file)


def get_debug_file_path(args: argparse.Namespace, error_func: ErrorFunc, temp_dir_name: str) -> Path:
    """
    get the debug-file path from args. If unspecified, create a temporary file under temp_dir_name.
    @param args: the parsed arguments
    @param error_func: the parser's error function
    @param temp_dir_name: a temporary directory that files can safely be created in
    @return: the debug-file path
    """
    debug_file = args.debug
    debug_file_needed = not args.asm and any((args.breakpoint, args.breakpoint_contains))

    if debug_file is None and debug_file_needed:
        if not args.silent:
            parser_warning = 'Parser Warning - breakpoints are used but the debugging flag (-d) is not specified.'
            if args.werror:
                error_func(parser_warning)
            print(f"{parser_warning} Debugging data will be saved.")
        debug_file = True

    if debug_file is True:
        if args.asm:
            error_func('assemble-only is used with the debug flag, but no debug file is specified.')
        if args.run:
            error_func('run-only is used with the debug flag, but no debug file is specified.')
        debug_file = os.path.join(temp_dir_name, 'debug.fjd')

    if isinstance(debug_file, str):
        debug_file = Path(debug_file)

    return debug_file


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

    supported_versions = ', '.join(f"{version}: {name}" for version, name in fjm.SUPPORTED_VERSIONS.items())
    asm_arguments.add_argument('-v', '--version', metavar='VERSION', type=int, default=None,
                               help=f"fjm version (default of {fjm.CompressedVersion}-compressed "
                                    f"if --outfile specified; version {fjm.NormalVersion} otherwise). "
                                    f"supported versions: {supported_versions}.")   # as in get_version()
    asm_arguments.add_argument('-f', '--flags', help="the default .fjm unpacking & running flags", type=int, default=0)

    asm_arguments.add_argument('--lzma_preset', type=int, default=lzma.PRESET_DEFAULT, choices=list(range(10)),
                               help=f"The preset used for the LZMA2 algorithm compression ("
                                    f"{lzma.PRESET_DEFAULT} by default; "
                                    f"used when version={fjm.CompressedVersion}).")

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
              f'  fj.py  a.fj b.fj                                      // assemble and run\n'
              f'  fj.py  a.fj b.fj  -o out.fjm                          // assemble save and run\n'
              f'  fj.py  code.fj  -d  -B swap_start exit_label          // assemble and debug\n\n'
              f'  fj.py --asm  -o o.fjm a.fj  -d dir/debug.fjd          // assemble and save debug info\n'
              f'  fj.py --asm  -o out.fjm  a.fj b.fj  --no_stl  -w 32   '
              f'// assemble without the standard library, 32 bit memory\n\n'
              f'  fj.py --run  prog.fjm                                 // just run\n'
              f'  fj.py --run  o.fjm  -d dir/debug.fjd  -B label        // run and debug\n '
    )


def parse_arguments() -> Tuple[argparse.Namespace, ErrorFunc]:
    """
    parse the command line arguments.
    @return: the parsed arguments, and the parser's error function
    """
    parser = get_argument_parser()
    add_arguments(parser)
    args = parser.parse_args()

    return args, parser.error


def execute_assemble_run(args: argparse.Namespace, error_func: ErrorFunc) -> None:
    """
    prepare temp files, and execute the run and assemble functions.
    @param args: the parsed arguments
    @param error_func: parser's error function
    """
    with TemporaryDirectory(suffix=get_temp_directory_suffix(args)) as temp_dir_name:
        debug_path, in_fjm_path, out_fjm_path = get_files_paths(args, error_func, temp_dir_name)

        if not args.run:
            assemble(out_fjm_path, debug_path, args, error_func)

        if not args.asm:
            run(in_fjm_path, debug_path, args, error_func)


def main() -> None:
    args, error_func = parse_arguments()
    execute_assemble_run(args, error_func)


if __name__ == '__main__':
    main()

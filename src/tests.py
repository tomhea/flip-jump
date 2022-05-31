import pytest
from pathlib import Path
import csv
import difflib

import fjm_run
import assembler
import defs


# TODO decide if raise/assert (pytest should handle it), or just print (so no-pytest could skip failed tests)


CSV_TRUE = 'True'
CSV_FALSE = 'False'
CSV_BOOLEAN = (CSV_TRUE, CSV_FALSE)


class CompileTestArgs:
    num_of_args = 8

    def __init__(self, test_name: str, fj_path: str, fjm_out_path: str,
                 word_size__str: str, version__str: str, flags__str: str,
                 use_stl__str: str, warning_as_errors__str: str):
        assert use_stl__str in CSV_BOOLEAN
        assert warning_as_errors__str in CSV_BOOLEAN

        self.test_name = test_name
        self.fj_files = defs.stl() + [fj_path] if use_stl__str == CSV_TRUE else [fj_path]

        self.fjm_out_path = fjm_out_path

        self.word_size = int(word_size__str)
        self.version = int(version__str)
        self.flags = int(flags__str)

        self.warning_as_errors = warning_as_errors__str == CSV_TRUE


def create_parent_directories(path: str):
    Path(path).absolute().parent.mkdir(parents=True, exist_ok=True)


def test_compile(args: CompileTestArgs) -> None:
    print(f'Compiling test {args.test_name}:')

    create_parent_directories(args.fjm_out_path)

    assembler.assemble(args.fj_files, args.fjm_out_path, args.word_size,
                       version=args.version, flags=args.flags,
                       warning_as_errors=args.warning_as_errors,
                       verbose={defs.Verbose.Time})


class RunTestArgs:
    num_of_args = 6

    def __init__(self, test_name: str, fjm_path: str,
                 in_file_path: str, out_file_path: str,
                 read_in_as_binary__str: str, read_out_as_binary__str: str):
        assert read_in_as_binary__str in CSV_BOOLEAN
        assert read_out_as_binary__str in CSV_BOOLEAN
        self.read_out_as_binary = read_out_as_binary__str == CSV_TRUE

        self.test_name = test_name
        self.fjm_path = fjm_path

        self.in_file_path = in_file_path
        self.out_file_path = out_file_path

        self.in_file_mode = 'rb' if read_in_as_binary__str == CSV_TRUE else 'r'
        self.out_file_mode = 'rb' if self.read_out_as_binary else 'r'

    def diff_output_with_expected(self, output: bytes):
        with open(self.out_file_path, self.out_file_mode) as out_file:
            expected_output = out_file.read()
            if self.read_out_as_binary:
                expected_output = expected_output.decode(encoding='raw_unicode_escape')
            output = output.decode(encoding='raw_unicode_escape')
            if output != expected_output:
                print(f'test "{self.test_name}" failed. here\'s the diff:')
                middle_newlines_padding = '\n\n'
                print(''.join(difflib.context_diff((output + middle_newlines_padding).splitlines(True),
                                                   (expected_output + middle_newlines_padding).splitlines(True),
                                                   fromfile=self.fjm_path, tofile=self.out_file_path)))


def test_same_input(args: RunTestArgs) -> None:
    print(f'Running test {args.test_name}:')

    with open(args.in_file_path, args.in_file_mode) as in_file:
        test_input = in_file.read()

        run_time, ops_executed, flips_executed, output, finish_cause =\
            fjm_run.run(args.fjm_path, defined_input=test_input, time_verbose=True)
        print(f'finished by {finish_cause.value} after {run_time:.3f}s '
              f'({ops_executed:,} ops executed, {flips_executed / ops_executed * 100:.2f}% flips)')

        assert finish_cause == defs.RunFinish.Looping
        args.diff_output_with_expected(output)


def argument_line_iterator(csv_file_path: str, num_of_args: int):
    with open(csv_file_path, 'r') as csv_file:
        for line_index, line in enumerate(csv.reader(csv_file)):
            if line:
                assert len(line) == num_of_args, f'expects {num_of_args} args, got {len(line)} ' \
                                                 f'(file {Path(csv_file_path).absolute()}, line {line_index + 1})'
                yield map(str.strip, line)


def test_compile_from_csv_file(csv_file_path: str):
    for line in argument_line_iterator(csv_file_path, CompileTestArgs.num_of_args):
        test_compile(CompileTestArgs(*line))


def test_run_from_csv_file(csv_file_path: str):
    for line in argument_line_iterator(csv_file_path, RunTestArgs.num_of_args):
        test_same_input(RunTestArgs(*line))
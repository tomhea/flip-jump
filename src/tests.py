import csv
from pathlib import Path
from typing import List

import assembler
import defs
import fjm_run


CSV_TRUE = 'True'
CSV_FALSE = 'False'
CSV_BOOLEAN = (CSV_TRUE, CSV_FALSE)


CompileCSVs = {'fast': 'tests/test_compile_fast.csv',
               'medium': 'tests/test_compile_medium.csv',
               'slow': 'tests/test_compile_slow.csv',
               'hexlib': 'tests/test_compile_hexlib.csv'}


RunCSVs = {'fast': 'tests/test_run_fast.csv',
           'medium': 'tests/test_run_medium.csv',
           'slow': 'tests/test_run_slow.csv',
           'hexlib': 'tests/test_run_hexlib.csv'}


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

    def __repr__(self) -> str:
        return self.test_name


def create_parent_directories(path: str):
    Path(path).absolute().parent.mkdir(parents=True, exist_ok=True)


def test_compile(compile_args: CompileTestArgs) -> None:
    print(f'Compiling test {compile_args.test_name}:')

    create_parent_directories(compile_args.fjm_out_path)

    assembler.assemble(compile_args.fj_files, compile_args.fjm_out_path, compile_args.word_size,
                       version=compile_args.version, flags=compile_args.flags,
                       warning_as_errors=compile_args.warning_as_errors,
                       verbose={defs.Verbose.Time})


class RunTestArgs:
    num_of_args = 6

    def __init__(self, test_name: str, fjm_path: str,
                 in_file_path: str, out_file_path: str,
                 read_in_as_binary__str: str, read_out_as_binary__str: str):
        assert read_in_as_binary__str in CSV_BOOLEAN
        assert read_out_as_binary__str in CSV_BOOLEAN
        self.read_in_as_binary = read_in_as_binary__str == CSV_TRUE
        self.read_out_as_binary = read_out_as_binary__str == CSV_TRUE

        self.test_name = test_name
        self.fjm_path = fjm_path

        self.in_file_path = in_file_path
        self.out_file_path = out_file_path

    def get_defined_input(self) -> bytes:
        if self.read_in_as_binary:
            with open(self.in_file_path, 'rb') as in_f:
                return in_f.read()
        else:
            with open(self.in_file_path, 'r') as in_f:
                return in_f.read().encode()

    def get_expected_output(self) -> str:
        if self.read_out_as_binary:
            with open(self.out_file_path, 'rb') as out_f:
                return out_f.read().decode('raw_unicode_escape')
        else:
            with open(self.out_file_path, 'r') as out_f:
                return out_f.read()

    def __repr__(self) -> str:
        return self.test_name


def test_run(run_args: RunTestArgs) -> None:
    print(f'Running test {run_args.test_name}:')

    run_time, ops_executed, flips_executed, output, finish_cause =\
        fjm_run.run(run_args.fjm_path, defined_input=run_args.get_defined_input(), time_verbose=True)

    print(f'finished by {finish_cause.value} after {run_time:.3f}s '
          f'({ops_executed:,} ops executed, {flips_executed / ops_executed * 100:.2f}% flips)')

    expected_finish_cause = defs.RunFinish.Looping
    assert finish_cause == expected_finish_cause

    output = output.decode('raw_unicode_escape')
    expected_output = run_args.get_expected_output()
    assert output == expected_output


def argument_line_iterator(csv_file_path: str, num_of_args: int):
    with open(csv_file_path, 'r') as csv_file:
        for line_index, line in enumerate(csv.reader(csv_file)):
            if line:
                assert len(line) == num_of_args, f'expects {num_of_args} args, got {len(line)} ' \
                                                 f'(file {Path(csv_file_path).absolute()}, line {line_index + 1})'
                yield map(str.strip, line)


# TODO maybe use pytest-dependency in the future,
#  to assure that if both a run and compile are tested - the run won't run before the compile,
#  and wil be skipped if compilation failed.


def get_compile_tests_args_from_csv(csv_file_path: str) -> List[CompileTestArgs]:
    return [CompileTestArgs(*line) for line in argument_line_iterator(csv_file_path, CompileTestArgs.num_of_args)]


def get_run_tests_args_from_csv(csv_file_path: str) -> List[RunTestArgs]:
    return [RunTestArgs(*line) for line in argument_line_iterator(csv_file_path, RunTestArgs.num_of_args)]

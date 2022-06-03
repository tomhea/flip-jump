import csv
from pathlib import Path
from typing import List, Iterable

import pytest

# register_assert_rewrite must be called before the import (to see inf on failed assertions in tests).
# FIXME find a better way
pytest.register_assert_rewrite('tests')
from test_fj import CompileTestArgs, RunTestArgs


# --- To Edit The Tests CSV Files ---
#       edit the TEST_TYPES variable:

TESTS_PATH = Path(__file__).parent.parent / 'tests'

TEST_TYPES = ('fast', 'medium', 'slow', 'hexlib')

CompileCSVs = {test_type: TESTS_PATH / f"test_compile_{test_type}.csv" for test_type in TEST_TYPES}
RunCSVs = {test_type: TESTS_PATH / f"test_run_{test_type}.csv" for test_type in TEST_TYPES}

# --- End Of Tests CSV Files ---


def argument_line_iterator(csv_file_path: Path, num_of_args: int) -> Iterable[List[str]]:
    with open(csv_file_path, 'r') as csv_file:
        for line_index, line in enumerate(csv.reader(csv_file)):
            if line:
                assert len(line) == num_of_args, f'expects {num_of_args} args, got {len(line)} ' \
                                                 f'(file {Path(csv_file_path).absolute()}, line {line_index + 1})'
                yield map(str.strip, line)


# TODO maybe use pytest-dependency in the future,
#  to assure that if both a run and compile are tested - the run won't run before the compile,
#  and wil be skipped if compilation failed.


def get_compile_tests_args_from_csv(csv_file_path: Path) -> List[CompileTestArgs]:
    return [CompileTestArgs(*line) for line in argument_line_iterator(csv_file_path, CompileTestArgs.num_of_args)]


def get_run_tests_args_from_csv(csv_file_path: Path) -> List[RunTestArgs]:
    return [RunTestArgs(*line) for line in argument_line_iterator(csv_file_path, RunTestArgs.num_of_args)]


def pytest_addoption(parser) -> None:
    for test_type in TEST_TYPES:
        parser.addoption(f"--{test_type}", action="store_true", help=f"run {test_type} tests")
    parser.addoption(f"--all", action="store_true", help=f"run all tests")


def pytest_generate_tests(metafunc) -> None:
    all_tests = metafunc.config.getoption('all')

    compile_tests = []
    if "compile_args" in metafunc.fixturenames:
        for test_type in TEST_TYPES:
            if all_tests or metafunc.config.getoption(test_type):
                if test_type in CompileCSVs:
                    compile_tests.extend(get_compile_tests_args_from_csv(CompileCSVs[test_type]))
        metafunc.parametrize("compile_args", compile_tests, ids=repr)

    run_tests = []
    if "run_args" in metafunc.fixturenames:
        for test_type in TEST_TYPES:
            if all_tests or metafunc.config.getoption(test_type):
                if test_type in RunCSVs:
                    run_tests.extend(get_run_tests_args_from_csv(RunCSVs[test_type]))
        metafunc.parametrize("run_args", run_tests, ids=repr)

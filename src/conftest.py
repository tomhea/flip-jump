import csv
import json
from pathlib import Path
from typing import List, Iterable

import pytest

# register_assert_rewrite must be called before the import (to see inf on failed assertions in tests).
# FIXME find a better way, as what if test_fj was imported before..
pytest.register_assert_rewrite('tests')
from test_fj import CompileTestArgs, RunTestArgs


TESTS_PATH = Path(__file__).parent.parent / 'tests'
with open(TESTS_PATH / 'conf.json', 'r') as tests_json:
    TESTS_OPTIONS = json.load(tests_json)

TEST_TYPES = TESTS_OPTIONS['ordered_speed_list']
DEFAULT_TYPE = TESTS_OPTIONS['default_type']


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
    assert 'all' not in TEST_TYPES
    for test_type in TEST_TYPES:
        parser.addoption(f"--{test_type}", action="store_true", help=f"run {test_type} tests")
    parser.addoption(f"--all", action="store_true", help=f"run all tests")


def pytest_generate_tests(metafunc) -> None:
    compiles_csvs = {test_type: TESTS_PATH / f"test_compile_{test_type}.csv" for test_type in TEST_TYPES}
    run_csvs = {test_type: TESTS_PATH / f"test_run_{test_type}.csv" for test_type in TEST_TYPES}

    def get_option(opt):
        return metafunc.config.getoption(opt)

    if get_option('all'):
        types_to_run = list(TEST_TYPES)
    else:
        types_to_run = list(filter(get_option, TEST_TYPES))
        if not types_to_run:
            types_to_run = [DEFAULT_TYPE]

    compile_tests = []
    if "compile_args" in metafunc.fixturenames:
        for test_type in types_to_run:
            if test_type in compiles_csvs:
                compile_tests.extend(get_compile_tests_args_from_csv(compiles_csvs[test_type]))
        metafunc.parametrize("compile_args", compile_tests, ids=repr)

    run_tests = []
    if "run_args" in metafunc.fixturenames:
        for test_type in types_to_run:
            if test_type in run_csvs:
                run_tests.extend(get_run_tests_args_from_csv(run_csvs[test_type]))
        metafunc.parametrize("run_args", run_tests, ids=repr)

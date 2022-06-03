import csv
from typing import List
from pathlib import Path

# Don't remove the "src." from src.tests. It will break the Assertion-info on failed assertions in tests.
from src.tests import CompileTestArgs, RunTestArgs


CompileCSVs = {
    'fast': 'tests/test_compile_fast.csv',
    'medium': 'tests/test_compile_medium.csv',
    'slow': 'tests/test_compile_slow.csv',
    'hexlib': 'tests/test_compile_hexlib.csv'
}


RunCSVs = {
    'fast': 'tests/test_run_fast.csv',
    'medium': 'tests/test_run_medium.csv',
    'slow': 'tests/test_run_slow.csv',
    'hexlib': 'tests/test_run_hexlib.csv'
}


TEST_TYPES = ('fast', 'medium', 'slow', 'hexlib')


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


def pytest_addoption(parser):
    for test_type in TEST_TYPES:
        parser.addoption(f"--{test_type}", action="store_true", help=f"run {test_type} tests")
    parser.addoption(f"--all", action="store_true", help=f"run all tests")


def pytest_generate_tests(metafunc):
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

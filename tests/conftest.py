import csv
import json
from pathlib import Path
from typing import List, Iterable, Callable, Tuple

from tests.test_fj import CompileTestArgs, RunTestArgs


TESTS_PATH = Path(__file__).parent
with open(TESTS_PATH / 'conf.json', 'r') as tests_json:
    TESTS_OPTIONS = json.load(tests_json)

TEST_TYPES = TESTS_OPTIONS['ordered_speed_list']
assert TEST_TYPES
DEFAULT_TYPE = TESTS_OPTIONS['default_type']
assert DEFAULT_TYPE in TEST_TYPES

ALL_FLAG = 'all'
COMPILE_FLAG = 'compile'
RUN_FLAG = 'run'
SAVED_KEYWORDS = {ALL_FLAG, COMPILE_FLAG, RUN_FLAG}


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
    colliding_keywords = set(TEST_TYPES) & SAVED_KEYWORDS
    assert not colliding_keywords

    for test_type in TEST_TYPES:
        parser.addoption(f"--{test_type}", action="store_true", help=f"run {test_type} tests")
    parser.addoption(f"--{ALL_FLAG}", action="store_true", help=f"run all tests")

    parser.addoption(f"--{COMPILE_FLAG}", action='store_true', help='only test compiling .fj files')
    parser.addoption(f"--{RUN_FLAG}", action='store_true', help='only test running .fjm files')


def get_test_compile_run(get_option: Callable[[str], bool]) -> Tuple[bool, bool]:
    check_compile_tests = get_option(COMPILE_FLAG)
    check_run_tests = get_option(RUN_FLAG)

    if check_compile_tests or check_run_tests:
        return check_compile_tests, check_run_tests
    return True, True


def get_types_to_run(get_option: Callable[[str], bool]) -> List[str]:
    if get_option(ALL_FLAG):
        types_to_run = list(TEST_TYPES)
    else:
        types_to_run = list(filter(get_option, TEST_TYPES))
        if not types_to_run:
            types_to_run = [DEFAULT_TYPE]
    return types_to_run


def pytest_generate_tests(metafunc) -> None:
    def get_option(opt):
        return metafunc.config.getoption(opt)

    check_compile_tests, check_run_tests = get_test_compile_run(get_option)
    types_to_run = get_types_to_run(get_option)

    if "compile_args" in metafunc.fixturenames:
        compile_tests = []
        if check_compile_tests:
            compiles_csvs = {test_type: TESTS_PATH / f"test_compile_{test_type}.csv" for test_type in types_to_run}
            for test_type in types_to_run:
                compile_tests.extend(get_compile_tests_args_from_csv(compiles_csvs[test_type]))
        metafunc.parametrize("compile_args", compile_tests, ids=repr)

    if "run_args" in metafunc.fixturenames:
        run_tests = []
        if check_run_tests:
            run_csvs = {test_type: TESTS_PATH / f"test_run_{test_type}.csv" for test_type in types_to_run}
            for test_type in types_to_run:
                run_tests.extend(get_run_tests_args_from_csv(run_csvs[test_type]))
        metafunc.parametrize("run_args", run_tests, ids=repr)

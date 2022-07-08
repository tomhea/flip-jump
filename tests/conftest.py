import csv
import json
from os import environ
from queue import Queue
from threading import Lock
from pathlib import Path
from typing import List, Iterable, Callable, Tuple, Optional, Any

import pytest

from tests.test_fj import CompileTestArgs, RunTestArgs


build_tests_lock = Lock()
build_tests_queue = Queue()


COMPILE_ARGUMENTS_FIXTURE = "compile_args"
RUN_ARGUMENTS_FIXTURE = "run_args"


TESTS_PATH = Path(__file__).parent
with open(TESTS_PATH / 'conf.json', 'r') as tests_json:
    TESTS_OPTIONS = json.load(tests_json)

TEST_TYPES = TESTS_OPTIONS['all_speed_ordered']
assert TEST_TYPES
REGULAR_TYPES = TESTS_OPTIONS['regular_speed_ordered']
assert REGULAR_TYPES
DEFAULT_TYPE = TESTS_OPTIONS['default_type']
assert DEFAULT_TYPE in TEST_TYPES


COMPILE_ORDER_INDEX = 1
RUN_ORDER_INDEX = 2


ALL_FLAG = 'all'
REGULAR_FLAG = 'regular'
COMPILE_FLAG = 'compile'
RUN_FLAG = 'run'
NAME_EXACT_FLAG = 'name'
NAME_CONTAINS_FLAG = 'contains'
NAME_STARTSWITH_FLAG = 'startswith'
NAME_ENDSWITH_FLAG = 'endswith'
SAVED_KEYWORDS = {ALL_FLAG, COMPILE_FLAG, RUN_FLAG,
                  NAME_EXACT_FLAG, NAME_CONTAINS_FLAG,
                  NAME_STARTSWITH_FLAG, NAME_ENDSWITH_FLAG}


def is_parallel_active() -> bool:
    """
    check if parallel is used - xdist works and uses >1 workers.
    @return: is parallel used
    """
    return int(environ.get('PYTEST_XDIST_WORKER_COUNT', default='0')) > 1


def argument_line_iterator(csv_file_path: Path, num_of_args: int) -> Iterable[List[str]]:
    """
    Iterate over the lines (with exact number of parameters)
    @note a line is a stripped argument list
    @param csv_file_path: the csv file
    @param num_of_args: right number of arguments per line
    @return: the line iterator
    """
    with open(csv_file_path, 'r') as csv_file:
        for line_index, line in enumerate(csv.reader(csv_file)):
            if line:
                assert len(line) == num_of_args, f'expects {num_of_args} args, got {len(line)} ' \
                                                 f'(file {Path(csv_file_path).absolute()}, line {line_index + 1})'
                yield map(str.strip, line)


def get_compile_tests_params_from_csv(csv_file_path: Path) -> List:
    """
    read the compile-tests from the csv
    @param csv_file_path: read tests from this csv
    @return: the list of pytest.params(CompileTestArgs, )
    """
    params = []

    for line in argument_line_iterator(csv_file_path, CompileTestArgs.num_of_args):
        args = CompileTestArgs(*line)
        params.append(pytest.param(args, marks=pytest.mark.run(order=COMPILE_ORDER_INDEX)))

    return params


def get_run_tests_params_from_csv(csv_file_path: Path) -> List:
    """
    read the run-tests from the csv
    @param csv_file_path: read tests from this csv
    @return: the list of pytest.params(RunTestArgs, depends=)
    """
    params = []

    for line in argument_line_iterator(csv_file_path, RunTestArgs.num_of_args):
        args = RunTestArgs(*line)
        params.append(pytest.param(args, marks=pytest.mark.run(order=RUN_ORDER_INDEX)))

    return params


def pytest_addoption(parser) -> None:
    """
    add the costume flags to pytest
    @param parser: the parser
    """
    colliding_keywords = set(TEST_TYPES) & SAVED_KEYWORDS
    assert not colliding_keywords

    for test_type in TEST_TYPES:
        parser.addoption(f"--{test_type}", action="store_true", help=f"run {test_type} tests")
    parser.addoption(f"--{REGULAR_FLAG}", action="store_true", help=f"run all regular tests ({', '.join(REGULAR_TYPES)})")
    parser.addoption(f"--{ALL_FLAG}", action="store_true", help=f"run all tests")

    parser.addoption(f"--{COMPILE_FLAG}", action='store_true', help='only test compiling .fj files')
    parser.addoption(f"--{RUN_FLAG}", action='store_true', help='only test running .fjm files')

    parser.addoption(f'--{NAME_EXACT_FLAG}', nargs='+',
                     help='only run tests with one of these names')
    parser.addoption(f'--{NAME_CONTAINS_FLAG}', nargs='+',
                     help='only run tests that contains one of these strings')
    parser.addoption(f'--{NAME_STARTSWITH_FLAG}', nargs='+',
                     help='only run tests that starts with one of these strings')
    parser.addoption(f'--{NAME_ENDSWITH_FLAG}', nargs='+',
                     help='only run tests that ends with one of these strings')


def get_test_compile_run(get_option: Callable[[str], bool]) -> Tuple[bool, bool]:
    """
    assess whether to run the compile-tests, and whether to run the run-tests.
    exit pytest if running in parallel both compile and run.
    @param get_option: function that returns the flags values
    @return: (test_compile, test_run) booleans
    """
    check_compile_tests = get_option(COMPILE_FLAG)
    check_run_tests = get_option(RUN_FLAG)

    if not check_compile_tests and not check_run_tests:
        check_compile_tests, check_run_tests = True, True

    if check_compile_tests and check_run_tests and is_parallel_active():
        pytest.exit("Can't run both compile and run (both --compile --run flags / none of them) "
                    "in parallel (-n auto/number>1), "
                    "as the run tests depends on the compile tests")

    return check_compile_tests, check_run_tests


def get_test_types_to_run__heavy_first(get_option: Callable[[str], bool]) -> List[str]:
    """
    get the test types to run (ordered, heavy tests first).
    @param get_option: function that returns the flags values
    @return: list of the test types to run
    """
    all_test_types_heavy_first = TEST_TYPES[::-1]
    regular_test_types_heavy_first = REGULAR_TYPES[::-1]

    if get_option(ALL_FLAG):
        types_to_run = list(all_test_types_heavy_first)
    elif get_option(REGULAR_FLAG):
        types_to_run = list(regular_test_types_heavy_first)
    else:
        types_to_run = list(filter(get_option, all_test_types_heavy_first))
        if not types_to_run:
            types_to_run = [DEFAULT_TYPE]
    return types_to_run


def is_test_name_ok(name: str, exact: Optional[List[str]], contains: Optional[List[str]],
                    startswith: Optional[List[str]], endswith: Optional[List[str]]) -> bool:
    """
    Check whether this test should be run (by the test's name).
    True if at least one of the checks below succeeds (checked if not None).
    @param name: the test name
    @param exact: list of strings that the test name should be in it
    @param contains: list of strings that the test name should contain one of them
    @param startswith: list of strings that the test name should start by one of them
    @param endswith: list of strings that the test name should end by one of them
    @return: will this test run?
    """
    if exact is not None:
        for option in exact:
            if name == option:
                return True

    if contains is not None:
        for option in contains:
            if option in name:
                return True

    if startswith is not None:
        for option in startswith:
            if name.startswith(option):
                return True

    if endswith is not None:
        for option in endswith:
            if name.endswith(option):
                return True

    return False


def filter_by_test_name(tests_args: List, get_option: Callable[[str], Optional[List[str]]]) -> List:
    """
    filter the test list by the test names (and the namings flags)
    @param tests_args: the tests
    @param get_option: function that returns the flags values
    @return: the filtered test list
    """
    exact = get_option(NAME_EXACT_FLAG)
    contains = get_option(NAME_CONTAINS_FLAG)
    startswith = get_option(NAME_STARTSWITH_FLAG)
    endswith = get_option(NAME_ENDSWITH_FLAG)

    if all(filter_list is None for filter_list in (exact, contains, startswith, endswith)):
        return tests_args

    return [args for args in tests_args if
            is_test_name_ok(args.values[0].test_name, exact, contains, startswith, endswith)]


def pytest_generate_tests(metafunc) -> None:
    """
    gather the tests from the csvs, and parametrize the compile-tests and run-tests fixtures with it.
    @param metafunc: enables to get-flags, parametrize-fixtures
    """
    def get_option(opt):
        return metafunc.config.getoption(opt)

    compile_tests__heavy_first, run_tests__heavy_first = get_tests_from_csvs__heavy_first__execute_once(get_option)

    if COMPILE_ARGUMENTS_FIXTURE in metafunc.fixturenames:
        metafunc.parametrize(COMPILE_ARGUMENTS_FIXTURE, compile_tests__heavy_first, ids=repr)

    if RUN_ARGUMENTS_FIXTURE in metafunc.fixturenames:
        metafunc.parametrize(RUN_ARGUMENTS_FIXTURE, run_tests__heavy_first, ids=repr)


def get_tests_from_csvs__heavy_first__execute_once(get_option: Callable[[str], Any]) -> Tuple[List, List]:
    """
    get the tests from the csv. heavy first.
    if more than 1 worker - only one worker will do the work, and distribute the result to the other workers.
    @param get_option: function that returns the flags values
    @return: the tests
    """
    if not is_parallel_active():
        return get_tests_from_csvs(get_option)

    with build_tests_lock:
        if build_tests_queue.empty():
            tests = get_tests_from_csvs(get_option)
        else:
            tests = build_tests_queue.get()
        build_tests_queue.put(tests)
        return tests


def get_tests_from_csvs(get_option: Callable[[str], Any]) -> Tuple[List, List]:
    """
    get the tests from the csv. heavy first.
    @param get_option: function that returns the flags values
    @return: the tests
    """
    check_compile_tests, check_run_tests = get_test_compile_run(get_option)

    types_to_run__heavy_first = get_test_types_to_run__heavy_first(get_option)

    compile_tests = []
    if check_compile_tests:
        compiles_csvs = {test_type: TESTS_PATH / f"test_compile_{test_type}.csv"
                         for test_type in types_to_run__heavy_first}
        for test_type in types_to_run__heavy_first:
            compile_tests.extend(get_compile_tests_params_from_csv(compiles_csvs[test_type]))
        compile_tests = filter_by_test_name(compile_tests, get_option)

    run_tests = []
    if check_run_tests:
        run_csvs = {test_type: TESTS_PATH / f"test_run_{test_type}.csv"
                    for test_type in types_to_run__heavy_first}
        for test_type in types_to_run__heavy_first:
            run_tests.extend(get_run_tests_params_from_csv(run_csvs[test_type]))
        run_tests = filter_by_test_name(run_tests, get_option)

    return compile_tests, run_tests

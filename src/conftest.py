import pytest
from src.tests import get_compile_tests_args_from_csv, get_run_tests_args_from_csv
from src.tests import CompileCSVs, RunCSVs


TEST_TYPES = ('fast', 'medium', 'slow', 'hexlib')


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
                compile_tests.extend(get_compile_tests_args_from_csv(CompileCSVs[test_type]))
        metafunc.parametrize("compile_args", compile_tests, ids=repr)

    run_tests = []
    if "run_args" in metafunc.fixturenames:
        for test_type in TEST_TYPES:
            if all_tests or metafunc.config.getoption(test_type):
                run_tests.extend(get_run_tests_args_from_csv(RunCSVs[test_type]))
        metafunc.parametrize("run_args", run_tests, ids=repr)

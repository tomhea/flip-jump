from queue import Queue
from threading import Lock
from pathlib import Path

from src import assembler
from src import fjm_run
from src.defs import TerminationCause, Verbose, get_stl_paths


CSV_TRUE = 'True'
CSV_FALSE = 'False'
CSV_BOOLEAN = (CSV_TRUE, CSV_FALSE)


ROOT_PATH = Path(__file__).parent.parent


compile_test_finish_lock = Lock()
finished_compile_tests_queue = Queue()


class CompileTestArgs:
    """
    Arguments class for a compile test
    """

    num_of_args = 8

    def __init__(self, test_name: str, fj_paths: str, fjm_out_path: str,
                 word_size__str: str, version__str: str, flags__str: str,
                 use_stl__str: str, warning_as_errors__str: str):
        """
        handling a line.split() from a csv file
        """
        assert use_stl__str in CSV_BOOLEAN
        assert warning_as_errors__str in CSV_BOOLEAN
        self.use_stl = use_stl__str == CSV_TRUE
        self.warning_as_errors = warning_as_errors__str == CSV_TRUE

        self.test_name = test_name

        included_files = get_stl_paths() if self.use_stl else []
        fj_paths_list = map(str.strip, fj_paths.split('|'))
        fj_absolute_paths_list = [ROOT_PATH / fj_path for fj_path in fj_paths_list]
        self.fj_files = included_files + fj_absolute_paths_list

        self.fjm_out_path = ROOT_PATH / fjm_out_path

        self.word_size = int(word_size__str)
        self.version = int(version__str)
        self.flags = int(flags__str)

    def __repr__(self) -> str:
        return self.test_name


def create_parent_directories(path: Path) -> None:
    """
    create all directories so that this path will be a valid path.
    @param path: the path
    """
    path.absolute().parent.mkdir(parents=True, exist_ok=True)


def test_compile(compile_args: CompileTestArgs) -> None:
    """
    test that the compilation is successful.
    @param compile_args: the test's arguments
    """
    print(f'Compiling test {compile_args.test_name}:')

    create_parent_directories(compile_args.fjm_out_path)

    assembler.assemble(compile_args.fj_files, compile_args.fjm_out_path, compile_args.word_size,
                       version=compile_args.version, flags=compile_args.flags,
                       warning_as_errors=compile_args.warning_as_errors,
                       verbose={Verbose.Time})


class RunTestArgs:
    """
    Arguments class for a run test
    """

    num_of_args = 6

    def __init__(self, test_name: str, fjm_path: str,
                 in_file_path: str, out_file_path: str,
                 read_in_as_binary__str: str, read_out_as_binary__str: str):
        """
        @note handling a line.split() (each is stripped) from a csv file
        """
        assert read_in_as_binary__str in CSV_BOOLEAN
        assert read_out_as_binary__str in CSV_BOOLEAN
        self.read_in_as_binary = read_in_as_binary__str == CSV_TRUE
        self.read_out_as_binary = read_out_as_binary__str == CSV_TRUE

        self.test_name = test_name
        self.fjm_path = ROOT_PATH / fjm_path

        if in_file_path:
            self.in_file_path = ROOT_PATH / in_file_path
        else:
            self.in_file_path = None

        if out_file_path:
            self.out_file_path = ROOT_PATH / out_file_path
        else:
            self.out_file_path = None

    def get_defined_input(self) -> bytes:
        """
        get input from the input file.
        @return: bytes of the input-file's content
        """
        if not self.in_file_path:
            return b''

        if self.read_in_as_binary:
            with open(self.in_file_path, 'rb') as in_f:
                return in_f.read()
        else:
            with open(self.in_file_path, 'r') as in_f:
                return in_f.read().encode()

    def get_expected_output(self) -> str:
        """
        get expected output from the output file.
        @return: string of the output-file's content
        """
        if not self.out_file_path:
            return ''

        if self.read_out_as_binary:
            with open(self.out_file_path, 'rb') as out_f:
                return out_f.read().decode('raw_unicode_escape')
        else:
            with open(self.out_file_path, 'r') as out_f:
                return out_f.read()

    def __repr__(self) -> str:
        return self.test_name


def test_run(run_args: RunTestArgs) -> None:
    """
    Run the test, assert finished by looping, and compare the output with the output-file.
    @param run_args: the test's arguments
    """
    print(f'Running test {run_args.test_name}:')

    termination_statistics = fjm_run.run(run_args.fjm_path,
                                         defined_input=run_args.get_defined_input(),
                                         time_verbose=True)

    print(termination_statistics)

    expected_termination_cause = TerminationCause.Looping
    assert termination_statistics.termination_cause == expected_termination_cause

    output = termination_statistics.standard_output.decode('raw_unicode_escape')
    expected_output = run_args.get_expected_output()
    assert output == expected_output

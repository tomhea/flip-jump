from queue import Queue
from threading import Lock
from pathlib import Path

from flipjump import run_test_output
from flipjump.assembler import assembler
from flipjump.fjm.fjm_consts import FJMVersion
from flipjump.utils.constants import io_bytes_encoding
from flipjump.utils.functions import get_stl_paths
from flipjump.fjm.fjm_writer import Writer


CSV_TRUE = 'True'
CSV_FALSE = 'False'
CSV_BOOLEAN = (CSV_TRUE, CSV_FALSE)


DEBUGGING_FILE_SUFFIX = '.fj_debugging_info'


ROOT_PATH = Path(__file__).parent.parent


class CompileTestArgs:
    """
    Arguments class for a compile test
    """

    num_of_csv_line_args = 8

    def __init__(self, save_debug_info: bool, test_name: str, fj_paths: str, fjm_out_path: str,
                 word_size__str: str, version__str: str, flags__str: str,
                 use_stl__str: str, warning_as_errors__str: str):
        """
        handling a line.split() from a csv file
        """
        assert use_stl__str in CSV_BOOLEAN
        assert warning_as_errors__str in CSV_BOOLEAN
        self.use_stl = use_stl__str == CSV_TRUE
        self.warning_as_errors = warning_as_errors__str == CSV_TRUE

        self.save_debug_info = save_debug_info

        self.test_name = test_name

        included_files = get_stl_paths() if self.use_stl else []
        fj_paths_list = map(str.strip, fj_paths.split('|'))
        fj_absolute_paths_list = [ROOT_PATH / fj_path for fj_path in fj_paths_list]

        included_files_tuples = [(f's{i}', path) for i, path in enumerate(included_files, start=1)]
        fj_paths_tuples = [(f'f{i}', path) for i, path in enumerate(fj_absolute_paths_list, start=1)]
        self.fj_files_tuples = included_files_tuples + fj_paths_tuples

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

    fjm_writer = Writer(compile_args.fjm_out_path, compile_args.word_size, FJMVersion(compile_args.version),
                        flags=compile_args.flags)

    debugging_file_path = None
    if compile_args.save_debug_info:
        debugging_file_path = Path(f'{compile_args.fjm_out_path}{DEBUGGING_FILE_SUFFIX}')

    assembler.assemble(compile_args.fj_files_tuples, compile_args.word_size, fjm_writer,
                       warning_as_errors=compile_args.warning_as_errors,
                       debugging_file_path=debugging_file_path)


class RunTestArgs:
    """
    Arguments class for a run test
    """

    num_of_csv_line_args = 6

    def __init__(self, save_debug_file: bool, debug_info_length: int, test_name: str, fjm_path: str,
                 in_file_path: str, out_file_path: str,
                 read_in_as_binary__str: str, read_out_as_binary__str: str
                 ):
        """
        @note handling a line.split() (each is stripped) from a csv file
        """
        assert read_in_as_binary__str in CSV_BOOLEAN
        assert read_out_as_binary__str in CSV_BOOLEAN
        self.read_in_as_binary = read_in_as_binary__str == CSV_TRUE
        self.read_out_as_binary = read_out_as_binary__str == CSV_TRUE

        self.save_debug_file = save_debug_file
        self.debug_info_length = debug_info_length

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
                return in_f.read().encode(io_bytes_encoding)

    def get_expected_output(self) -> bytes:
        """
        get expected output from the output file.
        @return: string of the output-file's content
        """
        if not self.out_file_path:
            return b''

        if self.read_out_as_binary:
            with open(self.out_file_path, 'rb') as out_f:
                return out_f.read()
        else:
            with open(self.out_file_path, 'r') as out_f:
                return out_f.read().encode(io_bytes_encoding)

    def __repr__(self) -> str:
        return self.test_name


def test_run(run_args: RunTestArgs) -> None:
    """
    Run the test, assert finished by looping, and compare the output with the output-file.
    @param run_args: the test's arguments
    """
    print(f'Running test {run_args.test_name}:')

    run_test_output(
        run_args.fjm_path,
        run_args.get_defined_input(),
        run_args.get_expected_output(),
        should_raise_assertion_error=True,
        debugging_file=Path(f'{run_args.fjm_path}{DEBUGGING_FILE_SUFFIX}'),
        print_time=True,
        last_ops_debugging_list_length=run_args.debug_info_length,
    )

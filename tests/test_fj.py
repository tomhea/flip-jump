from pathlib import Path

from src import assembler
from src import fjm_run
from src.defs import TerminationCause, Verbose, get_stl_paths


CSV_TRUE = 'True'
CSV_FALSE = 'False'
CSV_BOOLEAN = (CSV_TRUE, CSV_FALSE)


ROOT_PATH = Path(__file__).parent.parent


class CompileTestArgs:
    num_of_args = 8

    def __init__(self, test_name: str, fj_path: str, fjm_out_path: str,
                 word_size__str: str, version__str: str, flags__str: str,
                 use_stl__str: str, warning_as_errors__str: str):
        assert use_stl__str in CSV_BOOLEAN
        assert warning_as_errors__str in CSV_BOOLEAN
        self.use_stl = use_stl__str == CSV_TRUE
        self.warning_as_errors = warning_as_errors__str == CSV_TRUE

        self.test_name = test_name

        included_files = get_stl_paths() if self.use_stl else []
        self.fj_files = included_files + [ROOT_PATH / fj_path]

        self.fjm_out_path = ROOT_PATH / fjm_out_path

        self.word_size = int(word_size__str)
        self.version = int(version__str)
        self.flags = int(flags__str)

    def __repr__(self) -> str:
        return self.test_name


def create_parent_directories(path: Path):
    path.absolute().parent.mkdir(parents=True, exist_ok=True)


def test_compile(compile_args: CompileTestArgs) -> None:
    print(f'Compiling test {compile_args.test_name}:')

    create_parent_directories(compile_args.fjm_out_path)

    assembler.assemble(compile_args.fj_files, compile_args.fjm_out_path, compile_args.word_size,
                       version=compile_args.version, flags=compile_args.flags,
                       warning_as_errors=compile_args.warning_as_errors,
                       verbose={Verbose.Time})


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
        self.fjm_path = ROOT_PATH / fjm_path

        self.in_file_path = ROOT_PATH / in_file_path
        self.out_file_path = ROOT_PATH / out_file_path

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

    run_time, ops_executed, flips_executed, output, termination_cause =\
        fjm_run.run(run_args.fjm_path, defined_input=run_args.get_defined_input(), time_verbose=True)

    print(f'finished by {termination_cause} after {run_time:.3f}s '
          f'({ops_executed:,} ops executed, {flips_executed / ops_executed * 100:.2f}% flips)')

    expected_termination_cause = TerminationCause.Looping
    assert termination_cause == expected_termination_cause

    output = output.decode('raw_unicode_escape')
    expected_output = run_args.get_expected_output()
    assert output == expected_output

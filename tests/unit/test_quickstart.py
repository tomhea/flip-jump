"""
end-to-end unit-tests for the high-level API (flipjump/flipjump_quickstart.py).

assembles and runs the small no-stl hello program across the fjm-versions and memory-widths,
and checks the run_test_output success/failure contract.
"""

from pathlib import Path

import pytest

from flipjump import assemble_and_run, assemble_and_run_test_output, run_test_output
from flipjump.fjm.fjm_consts import FJMVersion
from flipjump.utils.classes import TerminationCause
from tests.unit.unit_utils import HELLO_NO_STL, HELLO_WORLD_OUTPUT, assemble_to_path


@pytest.mark.parametrize('fjm_version', list(FJMVersion))
@pytest.mark.parametrize('memory_width', [32, 64])
def test_assemble_and_run_hello(fjm_version: FJMVersion, memory_width: int) -> None:
    assert assemble_and_run_test_output(
        [HELLO_NO_STL],
        b'',
        HELLO_WORLD_OUTPUT,
        memory_width=memory_width,
        use_stl=False,
        fjm_version=fjm_version,
        should_raise_assertion_error=True,
        print_time=False,
        print_termination=False,
    )


def test_run_test_output_failure_returns_false(tmp_path: Path) -> None:
    fjm_path = assemble_to_path(HELLO_NO_STL.read_text(), tmp_path)
    assert not run_test_output(
        fjm_path,
        b'',
        b'WRONG OUTPUT',
        should_raise_assertion_error=False,
        print_time=False,
        print_termination=False,
    )


def test_run_test_output_failure_raises(tmp_path: Path) -> None:
    fjm_path = assemble_to_path(HELLO_NO_STL.read_text(), tmp_path)
    with pytest.raises(AssertionError):
        run_test_output(
            fjm_path,
            b'',
            b'WRONG OUTPUT',
            should_raise_assertion_error=True,
            print_time=False,
            print_termination=False,
        )


def test_assemble_and_run_returns_looping() -> None:
    statistics = assemble_and_run([HELLO_NO_STL], use_stl=False, print_time=False, print_termination=False)
    assert statistics.termination_cause == TerminationCause.Looping

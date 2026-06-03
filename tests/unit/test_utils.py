"""
unit-tests for the shared utilities (flipjump/utils/functions.py and classes.py).

covers the debug-label save/load round-trip, the file/path helpers, the run-statistics
flip/jump counting rule and last-ops deque, the TerminationCause strings, and PrintTimer.
"""

from pathlib import Path

import pytest

from flipjump.utils.classes import PrintTimer, RunStatistics, TerminationCause
from flipjump.utils.functions import (
    get_file_tuples,
    get_stl_paths,
    get_temp_directory_suffix,
    load_debugging_labels,
    save_debugging_labels,
)


def test_debugging_labels_round_trip(tmp_path: Path) -> None:
    debug_path = tmp_path / 'labels.fjd'
    labels = {'a': 1, 'b': 2, 'weird.name---x': 12345}
    save_debugging_labels(debug_path, labels)
    assert load_debugging_labels(debug_path) == labels


def test_debugging_labels_empty(tmp_path: Path) -> None:
    debug_path = tmp_path / 'labels.fjd'
    save_debugging_labels(debug_path, {})
    assert load_debugging_labels(debug_path) == {}


def test_get_temp_directory_suffix() -> None:
    assert get_temp_directory_suffix(['a.fj', 'b.fj']) == '__a.fj_b.fj__temp_directory'


def test_get_file_tuples_no_stl() -> None:
    file_tuples = get_file_tuples(['x.fj'], no_stl=True)
    assert [name for name, _ in file_tuples] == ['f1']
    assert file_tuples[0][1] == Path('x.fj')


def test_get_file_tuples_with_stl() -> None:
    stl_count = len(get_stl_paths())
    file_tuples = get_file_tuples(['x.fj'], no_stl=False)
    assert len(file_tuples) == stl_count + 1
    assert file_tuples[-1][0] == 'f1'


def test_get_stl_paths_are_fj_files() -> None:
    stl_paths = get_stl_paths()
    assert stl_paths
    assert all(path.suffix == '.fj' for path in stl_paths)


def test_register_op_counts() -> None:
    # _op_size and _after_null_flip are both 2*memory_width (here 2*8 == 16).
    statistics = RunStatistics(8, None)
    statistics.register_op(ip=0, flip_address=0, jump_address=16)  # flip<2w: no flip; jump==ip+2w: no jump
    statistics.register_op(ip=0, flip_address=16, jump_address=100)  # flip>=2w: flip; jump!=ip+2w: jump
    assert statistics.op_counter == 2
    assert statistics.flip_counter == 1
    assert statistics.jump_counter == 1


def test_register_op_flip_boundary() -> None:
    statistics = RunStatistics(8, None)
    statistics.register_op(ip=0, flip_address=15, jump_address=16)  # flip just below 2w: no flip
    assert statistics.flip_counter == 0


def test_register_op_address_deque_is_bounded() -> None:
    statistics = RunStatistics(8, 3)
    for ip in (10, 20, 30, 40, 50):
        statistics.register_op_address(ip)
    assert statistics.last_ops_addresses is not None
    assert list(statistics.last_ops_addresses) == [30, 40, 50]


def test_register_op_address_disabled() -> None:
    statistics = RunStatistics(8, None)
    statistics.register_op_address(10)
    assert statistics.last_ops_addresses is None


@pytest.mark.parametrize(
    'cause, text',
    [
        (TerminationCause.Looping, 'looping'),
        (TerminationCause.EOF, 'EOF'),
        (TerminationCause.NullIP, 'ip<2w'),
        (TerminationCause.RuntimeMemoryError, 'runtime-memory-error'),
        (TerminationCause.KeyboardInterrupt, 'keyboard-interrupt'),
    ],
)
def test_termination_cause_str(cause: TerminationCause, text: str) -> None:
    assert str(cause) == text


def test_print_timer_prints_when_enabled(capsys: pytest.CaptureFixture[str]) -> None:
    with PrintTimer('timing-message ', print_time=True):
        pass
    assert 'timing-message' in capsys.readouterr().out


def test_print_timer_silent_when_disabled(capsys: pytest.CaptureFixture[str]) -> None:
    with PrintTimer('timing-message ', print_time=False):
        pass
    assert capsys.readouterr().out == ''

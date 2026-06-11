"""
unit-tests for the breakpoint machinery (flipjump/interpreter/debugging/breakpoints.py):
breakpoint resolution (by address / exact label / label-substring), address-to-label
formatting, the debug actions (single step / skips / continue), and the memory- and
fj-variable-inspection helpers - all headless.
"""

from pathlib import Path
from typing import Dict, List, Optional

import pytest

from flipjump.fjm.fjm_consts import FJMVersion
from flipjump.fjm.fjm_writer import Writer
from flipjump.fjm.fjm_reader import Reader
from flipjump.interpreter.debugging import breakpoints
from flipjump.interpreter.debugging.breakpoints import (
    BreakpointHandler,
    BreakpointHandlerUnnecessary,
    calculate_variable_value,
    get_breakpoint_handler,
    get_breakpoints,
    handle_breakpoint,
    handle_read_f_j,
    load_labels_dictionary,
)
from flipjump.utils.classes import RunStatistics
from flipjump.utils.functions import save_debugging_labels


def make_handler(breakpoints: Dict[int, str] = {}, labels: Dict[str, int] = {}) -> BreakpointHandler:  # noqa: B006
    address_to_label = {address: label for label, address in labels.items()}
    return BreakpointHandler(dict(breakpoints), address_to_label, dict(labels))


class TestBreakpointResolution:
    def test_breakpoints_by_address_label_and_substring(self) -> None:
        labels = {'main': 256, 'main---inner---loop': 512, 'other': 1024}
        breakpoints = get_breakpoints({2048}, {'main'}, {'inner'}, labels)
        assert breakpoints == {2048: None, 512: 'main---inner---loop', 256: 'main'}

    def test_missing_breakpoint_label_warns_but_does_not_raise(self, capsys: pytest.CaptureFixture[str]) -> None:
        breakpoints = get_breakpoints(None, {'no_such_label'}, None, {})
        assert breakpoints == {}
        assert "can't be found" in capsys.readouterr().out

    def test_get_breakpoint_handler_loads_labels_from_debug_file(self, tmp_path: Path) -> None:
        debug_file = tmp_path / 'debug.fjd'
        save_debugging_labels(debug_file, {'start': 128, 'start---deep': 384})
        handler = get_breakpoint_handler(debug_file, None, None, {'deep'})
        assert handler.breakpoints == {384: 'start---deep'}
        assert handler.label_to_address['start'] == 128


class TestAddressFormatting:
    def test_exact_label(self) -> None:
        handler = make_handler(labels={'my_label': 256})
        assert 'my_label' in handler.get_address_str(256)
        assert '0x100' in handler.get_address_str(256)

    def test_macro_stack_label_is_multiline(self) -> None:
        handler = make_handler(labels={'main---macro1---macro2': 256})
        formatted = handler.get_address_str(256)
        assert 'main ->' in formatted
        assert 'macro2' in formatted

    def test_closest_previous_label_with_offset(self) -> None:
        handler = make_handler(labels={'before': 256})
        formatted = handler.get_address_str(300)
        assert 'before' in formatted
        assert '0x2c bits after' in formatted

    def test_unknown_address_is_hex(self) -> None:
        handler = make_handler()
        assert make_handler().get_address_str(0x1234) == '0x1234'
        assert handler.should_break(0x1234, 0) is False


class TestDebugActions:
    def test_single_step_and_skips_set_next_break(self) -> None:
        handler = make_handler()
        handler.apply_debug_action('Single Step', op_counter=100)
        assert handler.next_break == 101
        assert handler.should_break(ip=0xFFFF, op_counter=101)

        handler.apply_debug_action('Skip 10', op_counter=101)
        assert handler.next_break == 111
        handler.apply_debug_action('Skip 100', op_counter=111)
        assert handler.next_break == 211

    def test_continue_clears_next_break(self) -> None:
        handler = make_handler(breakpoints={256: 'bp'})
        handler.apply_debug_action('Single Step', op_counter=0)
        handler.apply_debug_action('Continue', op_counter=1)
        assert handler.next_break is None
        assert handler.should_break(ip=256, op_counter=2)  # real breakpoints still hit

    def test_continue_all_raises_unnecessary(self) -> None:
        handler = make_handler()
        with pytest.raises(BreakpointHandlerUnnecessary):
            handler.apply_debug_action('Continue All', op_counter=0)


def build_reader_with_data(tmp_path: Path, data: 'list[int]', memory_width: int = 16) -> Reader:
    fjm_path = tmp_path / 'mem.fjm'
    writer = Writer(fjm_path, memory_width, FJMVersion.NormalVersion)
    writer.add_simple_segment_with_data(0, data)
    writer.write_to_file()
    return Reader(fjm_path)


class TestVariableInspection:
    def test_calculate_hex_variable_value(self, tmp_path: Path) -> None:
        # w=16: a hex.vec 2 with the value 0x4F - hexes encoded as (value << #w) in the
        # ops' jump words (dbit = w + #w, #w = 5)
        data = [0, 0xF << 5, 0, 0x4 << 5, 0, 0, 0, 0]
        reader = build_reader_with_data(tmp_path, data)

        value, first_address, last_address = calculate_variable_value(('h', 2, 0), 0, reader)
        assert value == 0x4F
        assert (first_address, last_address) == (0, 2 * 16 * 2)

    def test_calculate_bit_variable_value_and_indexing(self, tmp_path: Path) -> None:
        # two bit[:2] variables in an array: [0b10, 0b01]
        data = [0, 0 << 5, 0, 1 << 5, 0, 1 << 5, 0, 0 << 5]
        reader = build_reader_with_data(tmp_path, data)

        assert calculate_variable_value(('b', 2, 0), 0, reader)[0] == 0b10
        assert calculate_variable_value(('b', 2, 1), 0, reader)[0] == 0b01

    def test_breakpoint_message_body_mentions_flip_and_jump(self, tmp_path: Path) -> None:
        reader = build_reader_with_data(tmp_path, [112, 64, 0, 0])
        handler = make_handler(labels={'op0': 0})
        body = handler.get_breakpoint_message_body(0, reader, op_counter=7)
        assert '7 ops executed' in body
        assert 'flip' in body and 'jump' in body
        assert '0x70' in body  # the flip target
        assert '0x40' in body  # the jump target


class TestLoadLabelsDictionary:
    def test_no_debugging_file_warns_when_needed(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert load_labels_dictionary(None, labels_file_needed=True) == {}
        assert "no debugging file" in capsys.readouterr().out
        assert load_labels_dictionary(None, labels_file_needed=False) == {}
        assert capsys.readouterr().out == ''

    def test_missing_debugging_file_warns(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        assert load_labels_dictionary(tmp_path / 'no_such.fjd', labels_file_needed=False) == {}
        assert "can't be found" in capsys.readouterr().out


class TestHandleReadFJ:
    def test_flip_and_jump_words_move_the_address(self) -> None:
        # :f:3:label -> 3 ops (6 words) forward; :j:3:label -> the jump word right after it
        prefix, address, label = handle_read_f_j(('f', 1, 3), 0x100, 'my_label', 16)
        assert prefix is None
        assert address == 0x100 + 6 * 16
        assert '+ 6w' in label

        prefix, address, label = handle_read_f_j(('j', 1, 3), 0x100, 'my_label', 16)
        assert prefix is None
        assert address == 0x100 + 7 * 16
        assert '+ 7w' in label

    def test_non_fj_prefix_is_returned_as_is(self) -> None:
        prefix, address, label = handle_read_f_j(('h', 2, 0), 0x100, None, 16)
        assert prefix == ('h', 2, 0)
        assert address == 0x100
        assert label == ''


class TestCalculateByteVariable:
    def test_calculate_byte_variable_value(self, tmp_path: Path) -> None:
        # w=16: a single byte variable with value 0xA7 - 8 data bits at offset #w=5
        reader = build_reader_with_data(tmp_path, [0, 0xA7 << 5, 0, 0])
        value, first_address, last_address = calculate_variable_value(('B', 1, 0), 0, reader)
        assert value == 0xA7
        assert (first_address, last_address) == (0, 2 * 16)


def run_read_memory(
    handler: BreakpointHandler,
    reader: Reader,
    user_answer: Optional[str],
    monkeypatch: pytest.MonkeyPatch,
    capsys: 'pytest.CaptureFixture[str]',
) -> str:
    """drive handler.handle_read_memory with a scripted answer; return what was printed."""
    monkeypatch.setattr(breakpoints, 'ask_for_text', lambda body_message, title_message: user_answer)
    handler.handle_read_memory(reader)
    return capsys.readouterr().out


class TestHandleReadMemory:
    def test_read_by_decimal_hex_and_label(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        reader = build_reader_with_data(tmp_path, [0x1234, 0, 0, 0])
        handler = make_handler(labels={'my_label': 0})

        assert 'memory[0x0] = 4660' in run_read_memory(handler, reader, '0', monkeypatch, capsys)
        assert 'memory[0x0] = 4660' in run_read_memory(handler, reader, '0x0', monkeypatch, capsys)
        assert 'memory[0x0] = 4660' in run_read_memory(handler, reader, 'my_label', monkeypatch, capsys)

    def test_read_hex_variable_with_prefix(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # the same hex.vec 2 (value 0x4F) as TestVariableInspection
        reader = build_reader_with_data(tmp_path, [0, 0xF << 5, 0, 0x4 << 5, 0, 0, 0, 0])
        handler = make_handler(labels={'var': 0})
        out = run_read_memory(handler, reader, ':h2:var', monkeypatch, capsys)
        assert '= 79' in out and '0x4f' in out

    def test_cancelled_query_reads_nothing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        reader = build_reader_with_data(tmp_path, [0, 0, 0, 0])
        assert run_read_memory(make_handler(), reader, None, monkeypatch, capsys) == ''

    def test_unresolvable_label_shows_error(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        reader = build_reader_with_data(tmp_path, [0, 0, 0, 0])
        out = run_read_memory(make_handler(), reader, 'no_such_label', monkeypatch, capsys)
        assert "can't resolve the address/label" in out

    def test_unaligned_address_shows_error(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        reader = build_reader_with_data(tmp_path, [0, 0, 0, 0])
        out = run_read_memory(make_handler(), reader, '3', monkeypatch, capsys)
        assert 'must be aligned' in out

    def test_out_of_memory_address_shows_error(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        reader = build_reader_with_data(tmp_path, [0, 0, 0, 0])
        out = run_read_memory(make_handler(), reader, str(1 << 20), monkeypatch, capsys)
        assert 'Bad memory address' in out

    def test_uninitialized_memory_region_shows_read_failure(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # address 0x1000 is aligned and in-range, but outside any segment (garbage-stop mode)
        reader = build_reader_with_data(tmp_path, [0, 0, 0, 0])
        out = run_read_memory(make_handler(), reader, '0x1000', monkeypatch, capsys)
        assert 'Read Memory Failure' in out


class TestQueryUserForDebugAction:
    def test_breakpoint_title_and_read_memory_loop(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        reader = build_reader_with_data(tmp_path, [112, 64, 0, 0])
        handler = make_handler(breakpoints={0: 'bp'})

        # first Read Memory (with a scripted read), then Continue
        actions = iter(['Read Memory', 'Continue'])
        monkeypatch.setattr(breakpoints, 'ask_for_choice', lambda body, title, choices, default: next(actions))
        monkeypatch.setattr(breakpoints, 'ask_for_text', lambda body_message, title_message: '0')
        action = handler.query_user_for_debug_action(0, reader, op_counter=5)
        assert action == 'Continue'
        assert 'memory[0x0]' in capsys.readouterr().out

    def test_debug_step_title_for_non_breakpoint_address(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        reader = build_reader_with_data(tmp_path, [112, 64, 0, 0])
        seen_titles = []

        def fake_choice(body: str, title: str, choices: List[str], default: str) -> str:
            seen_titles.append(title)
            return 'Continue All'

        monkeypatch.setattr(breakpoints, 'ask_for_choice', fake_choice)
        make_handler(breakpoints={0: 'bp'}).query_user_for_debug_action(0, reader, op_counter=0)
        make_handler().query_user_for_debug_action(0, reader, op_counter=0)
        assert seen_titles == ['Breakpoint', 'Debug Step']


class TestHandleBreakpointFlow:
    def test_continue_all_returns_none(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        reader = build_reader_with_data(tmp_path, [112, 64, 0, 0])
        handler = make_handler(breakpoints={0: 'bp'})
        statistics = RunStatistics(16, None)
        monkeypatch.setattr(breakpoints, 'ask_for_choice', lambda body, title, choices, default: 'Continue All')
        assert handle_breakpoint(handler, 0, reader, statistics) is None

    def test_single_step_keeps_the_handler_armed(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        reader = build_reader_with_data(tmp_path, [112, 64, 0, 0])
        handler = make_handler(breakpoints={0: 'bp'})
        statistics = RunStatistics(16, None)
        statistics.op_counter = 41
        monkeypatch.setattr(breakpoints, 'ask_for_choice', lambda body, title, choices, default: 'Single Step')
        assert handle_breakpoint(handler, 0, reader, statistics) is handler
        assert handler.next_break == 42


class TestDebuggerEndToEnd:
    def test_breakpoint_hit_then_continue_all_terminates_normally(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # a real assembled program: break on a label, EOF on the prompt (-> Continue All),
        # and the run must still terminate by looping.
        from flipjump import assemble_and_debug
        from flipjump.interpreter.io_devices.FixedIO import FixedIO
        from flipjump.utils.classes import TerminationCause
        from tests.unit.unit_utils import HELLO_NO_STL

        program = tmp_path / 'prog.fj'
        program.write_text(HELLO_NO_STL.read_text())

        def raise_eof(prompt: str = '') -> str:
            raise EOFError

        monkeypatch.setattr('builtins.input', raise_eof)
        statistics = assemble_and_debug(
            [program],
            breakpoints_contains={'code_start'},
            io_device=FixedIO(b''),
            print_time=False,
            print_termination=False,
        )
        assert statistics.termination_cause == TerminationCause.Looping
        assert 'program break' in capsys.readouterr().out

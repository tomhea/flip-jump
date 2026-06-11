"""
unit-tests for the breakpoint machinery (flipjump/interpreter/debugging/breakpoints.py):
breakpoint resolution (by address / exact label / label-substring), address-to-label
formatting, the debug actions (single step / skips / continue), and the memory- and
fj-variable-inspection helpers - all headless.
"""

from pathlib import Path
from typing import Dict

import pytest

from flipjump.fjm.fjm_consts import FJMVersion
from flipjump.fjm.fjm_writer import Writer
from flipjump.fjm.fjm_reader import Reader
from flipjump.interpreter.debugging.breakpoints import (
    BreakpointHandler,
    BreakpointHandlerUnnecessary,
    calculate_variable_value,
    get_breakpoint_handler,
    get_breakpoints,
)
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

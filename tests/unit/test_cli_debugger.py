"""
unit-tests for the CLI debugger (WI-C): the headless terminal prompts that replaced the
easygui message-boxes, and an end-to-end breakpoint session (break -> read memory ->
single step -> continue) driven through scripted stdin answers.
"""

from pathlib import Path
from typing import Iterator, List

import pytest

from flipjump.interpretter import fjm_run
from flipjump.interpretter.debugging import message_boxes
from flipjump.interpretter.debugging.breakpoints import get_breakpoint_handler
from flipjump.interpretter.io_devices.FixedIO import FixedIO
from flipjump.utils.classes import TerminationCause
from tests.unit.unit_utils import assemble_to_path

LOOP_PROGRAM = """
stl.startup
flipper+dbit;
my_loop_label:
;my_loop_label

flipper: hex.hex 0
"""


def feed_answers(monkeypatch: pytest.MonkeyPatch, answers: List[str]) -> None:
    answers_iterator: Iterator[str] = iter(answers)

    def fake_input(prompt: str = '') -> str:
        try:
            return next(answers_iterator)
        except StopIteration:
            raise EOFError

    monkeypatch.setattr('builtins.input', fake_input)


class TestPromptFunctions:
    def test_message_box_prints_body_and_title(self, capsys: pytest.CaptureFixture[str]) -> None:
        message_boxes.display_message_box('the body', 'The Title')
        captured = capsys.readouterr().out
        assert 'The Title' in captured
        assert 'the body' in captured

    def test_choices_by_number_and_by_name(self, monkeypatch: pytest.MonkeyPatch) -> None:
        feed_answers(monkeypatch, ['2'])
        assert message_boxes.display_message_box_with_choices_and_get_answer('b', 't', ['A', 'B', 'C'], 'C') == 'B'

        feed_answers(monkeypatch, ['single step'])
        choices = ['Read Memory', 'Single Step', 'Continue All']
        answer = message_boxes.display_message_box_with_choices_and_get_answer('b', 't', choices, 'Continue All')
        assert answer == 'Single Step'

    def test_choices_default_on_eof_and_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        feed_answers(monkeypatch, [])
        assert message_boxes.display_message_box_with_choices_and_get_answer('b', 't', ['A', 'B'], 'B') == 'B'
        feed_answers(monkeypatch, [''])
        assert message_boxes.display_message_box_with_choices_and_get_answer('b', 't', ['A', 'B'], 'B') == 'B'

    def test_choices_reprompts_on_invalid(self, monkeypatch: pytest.MonkeyPatch) -> None:
        feed_answers(monkeypatch, ['nonsense', '1'])
        assert message_boxes.display_message_box_with_choices_and_get_answer('b', 't', ['A', 'B'], 'B') == 'A'

    def test_text_answer_and_cancel(self, monkeypatch: pytest.MonkeyPatch) -> None:
        feed_answers(monkeypatch, ['  0x40  '])
        assert message_boxes.display_message_box_and_get_text_answer('b', 't') == '0x40'
        feed_answers(monkeypatch, [''])
        assert message_boxes.display_message_box_and_get_text_answer('b', 't') is None


class TestDebuggerEndToEnd:
    def run_with_breakpoint(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, answers: List[str]
    ) -> 'tuple[fjm_run.TerminationStatistics, object]':
        fjm_path = assemble_to_path(LOOP_PROGRAM, tmp_path, use_stl=True, with_debug=True)
        breakpoint_handler = get_breakpoint_handler(
            tmp_path / 'debug.fjd', None, None, breakpoint_contains_labels={'my_loop_label'}
        )
        assert breakpoint_handler.breakpoints, 'breakpoint was not resolved from the debug file'
        feed_answers(monkeypatch, answers)
        statistics = fjm_run.run(
            fjm_path, io_device=FixedIO(b''), print_time=False, breakpoint_handler=breakpoint_handler
        )
        return statistics, breakpoint_handler

    def test_break_step_continue(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        statistics, _ = self.run_with_breakpoint(tmp_path, monkeypatch, ['Single Step', 'Continue All'])
        assert statistics.termination_cause == TerminationCause.Looping
        captured = capsys.readouterr().out
        assert 'program break' in captured
        assert 'Single Step' in captured

    def test_break_read_memory_then_continue(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        statistics, _ = self.run_with_breakpoint(tmp_path, monkeypatch, ['Read Memory', '0', 'Continue All'])
        assert statistics.termination_cause == TerminationCause.Looping
        captured = capsys.readouterr().out
        assert 'memory[0x0]' in captured

    def test_break_on_eof_continues_all(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # no scripted answers at all: the default (Continue All) is chosen, the run finishes
        statistics, _ = self.run_with_breakpoint(tmp_path, monkeypatch, [])
        assert statistics.termination_cause == TerminationCause.Looping

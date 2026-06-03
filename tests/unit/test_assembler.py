"""
unit-tests for the assembler: the language rules compile, and the error/edge cases raise
the right exceptions.

each rule-test assembles a tiny inline no-stl program and asserts it produces a readable
.fjm; each error-test asserts the expected FlipJump exception.
"""

from pathlib import Path

import pytest

from flipjump.fjm.fjm_reader import Reader
from flipjump.utils.exceptions import (
    FlipJumpAssemblerException,
    FlipJumpException,
    FlipJumpParsingException,
    FlipJumpPreprocessorException,
)
from tests.unit.unit_utils import MINIMAL_STARTUP, assemble_to_path, compile_and_get_reader

# --- language rules: each program should assemble into a valid .fjm ---


def _program(body: str) -> str:
    return MINIMAL_STARTUP + '\nstartup\n' + body


def test_flip_jump_op(tmp_path: Path) -> None:
    reader = compile_and_get_reader(_program('a:\n8;a\n'), tmp_path)
    assert isinstance(reader, Reader)


def test_jump_only_op(tmp_path: Path) -> None:
    compile_and_get_reader(_program('loop:\n;loop\n'), tmp_path)


def test_flip_only_op(tmp_path: Path) -> None:
    compile_and_get_reader(_program('here:\n8;\nloop:\n;loop\n'), tmp_path)


def test_forward_and_backward_label_reference(tmp_path: Path) -> None:
    compile_and_get_reader(_program(';forward\nback:\n;back\nforward:\n;back\n'), tmp_path)


def test_constant_definition_and_use(tmp_path: Path) -> None:
    compile_and_get_reader(_program('X = 5\nhere:\n;(here + X)\n'), tmp_path)


def test_expression_in_address(tmp_path: Path) -> None:
    compile_and_get_reader(_program('here:\n;(here + 2*w)\nl:\n;l\n'), tmp_path)


def test_rep_macro_call(tmp_path: Path) -> None:
    source = MINIMAL_STARTUP + '\ndef m a < IO {\n a+IO;\n}\nstartup\nrep(4, i) m i\nl:\n;l\n'
    compile_and_get_reader(source, tmp_path)


def test_macro_definition_and_call(tmp_path: Path) -> None:
    source = MINIMAL_STARTUP + '\ndef m a {\n a;a\n}\nstartup\nm 8\nl:\n;l\n'
    compile_and_get_reader(source, tmp_path)


def test_nested_macro_call(tmp_path: Path) -> None:
    source = MINIMAL_STARTUP + '\ndef inner a {\n a;a\n}\ndef outer b {\n inner b\n}\nstartup\nouter 8\nl:\n;l\n'
    compile_and_get_reader(source, tmp_path)


def test_wflip_op(tmp_path: Path) -> None:
    compile_and_get_reader(_program('wflip 0x100, 0x5, l\nl:\n;l\n'), tmp_path)


def test_wflip_zero_value(tmp_path: Path) -> None:
    compile_and_get_reader(_program('wflip 0x100, 0, l\nl:\n;l\n'), tmp_path)


def test_multi_file_macro_sharing(tmp_path: Path) -> None:
    file_a = MINIMAL_STARTUP + '\ndef shared {\n 0;0\n}\n'
    file_b = 'startup\nshared\nl:\n;l\n'
    reader = compile_and_get_reader([file_a, file_b], tmp_path)
    assert isinstance(reader, Reader)


# --- error handling / edge cases ---


def test_syntax_error_raises(tmp_path: Path) -> None:
    with pytest.raises(FlipJumpParsingException):
        assemble_to_path('this is not valid fj $$$ {{{', tmp_path)


def test_undefined_label_raises(tmp_path: Path) -> None:
    with pytest.raises(FlipJumpException):
        assemble_to_path(_program(';undefined_label\n'), tmp_path)


def test_macro_recursion_depth_exceeded_raises(tmp_path: Path) -> None:
    source = 'def loop {\n    loop\n}\nloop\n'
    with pytest.raises(FlipJumpPreprocessorException):
        assemble_to_path(source, tmp_path, max_recursion_depth=50)


def test_address_beyond_memory_width_raises(tmp_path: Path) -> None:
    source = _program('segment 0x1000\n;0\n')
    with pytest.raises(FlipJumpAssemblerException):
        assemble_to_path(source, tmp_path, memory_width=8)

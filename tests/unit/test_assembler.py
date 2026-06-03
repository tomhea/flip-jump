"""
unit-tests for the assembler: the language rules compile (and, where there's arithmetic,
produce the expected memory-word), and the error/edge cases raise the right exceptions.

the rule-tests assemble a tiny inline no-stl program; MINIMAL_STARTUP is exactly two ops,
so the first user op always lands at word-index 4 (flip-word) / 5 (jump-word).
"""

from pathlib import Path

import pytest

from flipjump.utils.exceptions import (
    FlipJumpAssemblerException,
    FlipJumpParsingException,
    FlipJumpPreprocessorException,
)
from tests.unit.unit_utils import MINIMAL_STARTUP, assemble_to_path, compile_and_get_reader

# the word-indices of the first user op (right after the 2-op MINIMAL_STARTUP).
FIRST_OP_FLIP_WORD = 4
FIRST_OP_JUMP_WORD = 5

# --- language rules: each program should assemble into a valid .fjm ---


def _program(body: str) -> str:
    return MINIMAL_STARTUP + '\nstartup\n' + body


def test_flip_jump_op(tmp_path: Path) -> None:
    reader = compile_and_get_reader(_program('a:\n8;a\n'), tmp_path)
    assert reader.get_memory()[FIRST_OP_FLIP_WORD] == 8


def test_jump_only_op(tmp_path: Path) -> None:
    compile_and_get_reader(_program('loop:\n;loop\n'), tmp_path)


def test_flip_only_op(tmp_path: Path) -> None:
    compile_and_get_reader(_program('here:\n8;\nloop:\n;loop\n'), tmp_path)


def test_forward_and_backward_label_reference(tmp_path: Path) -> None:
    compile_and_get_reader(_program(';forward\nback:\n;back\nforward:\n;back\n'), tmp_path)


def test_constant_definition_and_use(tmp_path: Path) -> None:
    # the constant X must be substituted into the jump-word of ";X".
    reader = compile_and_get_reader(_program('X = 5\n;X\n'), tmp_path)
    assert reader.get_memory()[FIRST_OP_JUMP_WORD] == 5


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
    # wflip of word 0x100 with bits {0, 2} set emits a first fj-op that flips address 0x100.
    reader = compile_and_get_reader(_program('wflip 0x100, 0x5, l\nl:\n;l\n'), tmp_path)
    assert reader.get_memory()[FIRST_OP_FLIP_WORD] == 0x100


def test_wflip_zero_value(tmp_path: Path) -> None:
    compile_and_get_reader(_program('wflip 0x100, 0, l\nl:\n;l\n'), tmp_path)


def test_pad_directive(tmp_path: Path) -> None:
    compile_and_get_reader(_program('pad 4\nl:\n;l\n'), tmp_path)


def test_reserve_directive(tmp_path: Path) -> None:
    compile_and_get_reader(_program('reserve 2*w\nl:\n;l\n'), tmp_path)


def test_segment_directive(tmp_path: Path) -> None:
    compile_and_get_reader(_program('segment 0x400\nl:\n;l\n'), tmp_path)


def test_namespace(tmp_path: Path) -> None:
    source = 'ns A {\n def m {\n 5;6\n }\n}\n' + MINIMAL_STARTUP + '\nstartup\nA.m\nl:\n;l\n'
    reader = compile_and_get_reader(source, tmp_path)
    assert reader.get_memory()[FIRST_OP_FLIP_WORD] == 5


def test_multi_file_macro_sharing(tmp_path: Path) -> None:
    # file B calls a macro defined in file A; the macro's "5;6" op lands at the first word.
    file_a = MINIMAL_STARTUP + '\ndef shared {\n 5;6\n}\n'
    file_b = 'startup\nshared\nl:\n;l\n'
    reader = compile_and_get_reader([file_a, file_b], tmp_path)
    assert reader.get_memory()[FIRST_OP_FLIP_WORD] == 5
    assert reader.get_memory()[FIRST_OP_JUMP_WORD] == 6


# --- error handling / edge cases ---


def test_syntax_error_raises(tmp_path: Path) -> None:
    with pytest.raises(FlipJumpParsingException):
        assemble_to_path('this is not valid fj $$$ {{{', tmp_path)


def test_undefined_label_raises(tmp_path: Path) -> None:
    with pytest.raises(FlipJumpAssemblerException):
        assemble_to_path(_program(';undefined_label\n'), tmp_path)


def test_wrong_macro_argument_count_raises(tmp_path: Path) -> None:
    source = MINIMAL_STARTUP + '\ndef m a {\n a;a\n}\nstartup\nm 1, 2\nl:\n;l\n'
    with pytest.raises(FlipJumpPreprocessorException):
        assemble_to_path(source, tmp_path)


def test_duplicate_label_raises(tmp_path: Path) -> None:
    with pytest.raises(FlipJumpPreprocessorException):
        assemble_to_path(_program('dup:\ndup:\n;dup\n'), tmp_path)


def test_macro_recursion_depth_exceeded_raises(tmp_path: Path) -> None:
    source = 'def loop {\n    loop\n}\nloop\n'
    with pytest.raises(FlipJumpPreprocessorException):
        assemble_to_path(source, tmp_path, max_recursion_depth=50)


def test_address_beyond_memory_width_raises(tmp_path: Path) -> None:
    source = _program('segment 0x1000\n;0\n')
    with pytest.raises(FlipJumpAssemblerException):
        assemble_to_path(source, tmp_path, memory_width=8)

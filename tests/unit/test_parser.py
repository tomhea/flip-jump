"""
unit-tests for the lexer/number-parsing (flipjump/assembler/fj_parser.py).

these check the pure tokenization rules: number formats (dec/hex/bin, no octal), char
literals and their escapes, little-endian string packing, and comment handling.
"""

from pathlib import Path
from typing import List

import pytest

from flipjump.assembler.fj_parser import FJLexer, get_char_value_and_length
from flipjump.utils.exceptions import FlipJumpParsingException
from tests.unit.unit_utils import assemble_to_path


def _token_values(text: str, wanted_type: str) -> List[object]:
    return [token.value for token in FJLexer().tokenize(text) if token.type == wanted_type]


def _numbers(text: str) -> List[object]:
    return _token_values(text, 'NUMBER')


@pytest.mark.parametrize(
    'text, expected',
    [
        ('10', 10),
        ('0x10', 16),
        ('0X1f', 31),
        ('0b10', 2),
        ('0B101', 5),
        ('010', 10),  # no octal support: leading zero is still decimal
    ],
)
def test_number_formats(text: str, expected: int) -> None:
    assert _numbers(text) == [expected]


@pytest.mark.parametrize(
    'literal, expected',
    [
        ("'A'", 65),
        ("'0'", 48),
        (r"'\n'", 0x0A),
        (r"'\t'", 0x09),
        (r"'\0'", 0x00),
        (r"'\x41'", 0x41),
    ],
)
def test_char_literals(literal: str, expected: int) -> None:
    assert _numbers(literal) == [expected]


@pytest.mark.parametrize(
    's, expected_value, expected_length',
    [
        ('A', ord('A'), 1),
        (r'\n', 0x0A, 2),
        (r'\\', 0x5C, 2),
        ("\\'", 0x27, 2),
        (r'\x41', 0x41, 4),
    ],
)
def test_get_char_value_and_length(s: str, expected_value: int, expected_length: int) -> None:
    assert get_char_value_and_length(s) == (expected_value, expected_length)


def test_string_is_little_endian_packed() -> None:
    # "AB" -> 'A' at bits 0..7, 'B' at bits 8..15 == 0x4241
    string_tokens = _token_values('"AB"', 'STRING')
    assert string_tokens == [0x4241]


def test_line_comment_is_ignored() -> None:
    assert _numbers('10 // this is a comment\n20') == [10, 20]


def test_line_continuation_is_ignored() -> None:
    assert _numbers('10 \\\n 20') == [10, 20]


# A label whose name is also a constant is silently unusable (references resolve to the
# constant, never the label), so the parser must reject it - in either declaration order.
@pytest.mark.parametrize(
    'source',
    [
        'myc = 5\nmyc:\n',  # constant declared before the label
        'myc:\nmyc = 5\n',  # label declared before the constant
        'w:\n',  # the built-in width constant `w`
    ],
)
def test_label_shadowing_a_constant_is_rejected(source: str, tmp_path: Path) -> None:
    with pytest.raises(FlipJumpParsingException, match='also defined as a constant'):
        assemble_to_path(source, tmp_path, use_stl=False)


def test_label_not_shadowing_a_constant_is_accepted(tmp_path: Path) -> None:
    # a label whose name differs from every constant assembles fine (no false positive).
    assemble_to_path('myz = 5\nmyc:\n', tmp_path, use_stl=False)

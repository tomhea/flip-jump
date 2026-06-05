"""
unit-tests for the lexer/number-parsing (flipjump/assembler/fj_parser.py).

these check the pure tokenization rules: number formats (dec/hex/bin, no octal), char
literals and their escapes, little-endian string packing, and comment handling.
"""

from pathlib import Path
from typing import List, Tuple, Union

import pytest

import flipjump.assembler.fj_parser as fj_parser
from flipjump.assembler.fj_parser import FJLexer, char_escape_dict, get_char_value_and_length
from flipjump.utils.exceptions import FlipJumpParsingException
from tests.unit.unit_utils import assemble_to_path


def _token_values(text: str, wanted_type: str) -> List[object]:
    return [token.value for token in FJLexer().tokenize(text) if token.type == wanted_type]


def _numbers(text: str) -> List[object]:
    return _token_values(text, 'NUMBER')


def _strings(text: str) -> List[object]:
    return _token_values(text, 'STRING')


def _pack(byte_values: List[int]) -> int:
    # the lexer packs a string little-endian: first char in the low byte.
    return sum(value << (8 * i) for i, value in enumerate(byte_values))


def _tokenize_collecting_errors(text: str) -> Tuple[List[object], bool]:
    # error()/all_errors/curr_file are module globals only initialized inside parse_macro_tree; seed them
    # so a lexer error in a pure-lexer test can't NameError or leak into another. the file name is only
    # used to format the error message. returns (string token values, errored?).
    fj_parser.error_occurred = False
    fj_parser.all_errors = ''
    fj_parser.curr_file = Path('<test>')
    fj_parser.curr_file_short_name = '<test>'
    strings = _strings(text)
    return strings, fj_parser.error_occurred


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


@pytest.mark.parametrize('escape_char, expected_value', list(char_escape_dict.items()))
def test_every_escape_key_decodes_in_a_char_literal(escape_char: str, expected_value: int) -> None:
    # \0 \a \b \e \f \n \r \t \v \\ \' \" \?  -- each must lex and decode to its byte.
    assert _numbers(f"'\\{escape_char}'") == [expected_value]


@pytest.mark.parametrize(
    'string_literal, expected_bytes',
    [
        (r'"\\"', [0x5C]),  # escaped backslash: regressed by the naive fix, must still parse
        (r'"\""', [0x22]),  # escaped quote
        (r'"\?"', [0x3F]),  # escaped question-mark
        (r'"a\tb"', [ord('a'), 0x09, ord('b')]),  # escape between printables
        (r'"\x41Z"', [0x41, ord('Z')]),  # \xHH followed by a printable, not swallowed
        (r'"\\x41"', [0x5C, ord('x'), ord('4'), ord('1')]),  # escaped backslash then literal x41
    ],
)
def test_valid_strings_pack_correctly(string_literal: str, expected_bytes: List[int]) -> None:
    assert _strings(string_literal) == [_pack(expected_bytes)]


@pytest.mark.parametrize(
    'bad_string',
    [
        r'"\q"',  # unknown escape, non-hex tail  -- used to crash: int('', 16) ValueError
        r'"\xZZ"',  # bad hex                      -- used to crash: int('ZZ', 16) ValueError
        r'"\x4"',  # truncated hex                 -- used to silently decode to 0x04
        r'"\d41"',  # unknown escape, hex tail     -- used to SILENTLY decode to 0x41 == "A"
        r'"\g30"',  # unknown escape, hex tail     -- used to SILENTLY decode to 0x30 == "0"
        '"\\"',  # lone backslash                  -- incomplete escape
    ],
)
def test_invalid_escape_is_rejected_not_miscompiled(bad_string: str) -> None:
    # the whole point: an invalid escape must NOT crash, and must NOT silently become a wrong byte.
    # it produces no STRING token and flags a lexer error (-> a clean parse error downstream).
    strings, errored = _tokenize_collecting_errors(bad_string)
    assert strings == []
    assert errored


def test_line_comment_is_ignored() -> None:
    assert _numbers('10 // this is a comment\n20') == [10, 20]


def test_line_continuation_is_ignored() -> None:
    assert _numbers('10 \\\n 20') == [10, 20]


# A label whose (namespace-qualified) name is also a constant is silently unusable (references
# resolve to the constant, never the label), so the parser must reject it - in either declaration
# order, across files, and within the same namespace.
@pytest.mark.parametrize(
    'source',
    [
        'myc = 5\nmyc:\n',  # constant declared before the label
        'myc:\nmyc = 5\n',  # label declared before the constant
        'w:\n',  # the built-in width constant `w`
        'ns foo {\n bar = 5\n bar:\n ;0\n}\n',  # same-namespace collision (foo.bar)
        ['myc:\n', 'myc = 5\n'],  # label in the first file, constant in a later file
    ],
)
def test_label_shadowing_a_constant_is_rejected(source: Union[str, List[str]], tmp_path: Path) -> None:
    with pytest.raises(FlipJumpParsingException, match='also defined as a constant'):
        assemble_to_path(source, tmp_path, use_stl=False)


@pytest.mark.parametrize(
    'source',
    [
        'myz = 5\nmyc:\n',  # a label whose name differs from every constant
        'myc = 5\nns foo {\n myc:\n ;0\n}\n',  # foo.myc label is NOT shadowed by top-level const myc
    ],
)
def test_label_not_shadowing_a_constant_is_accepted(source: str, tmp_path: Path) -> None:
    assemble_to_path(source, tmp_path, use_stl=False)

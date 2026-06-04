"""
unit-tests for the Expr arithmetic-tree (flipjump/assembler/inner_classes/expr.py).

these are pure tests - they build Expr trees directly and check resolution, the math
operators, and the failure modes, without assembling anything.
"""

from typing import Tuple

import pytest

from flipjump.assembler.inner_classes.expr import Expr, get_minimized_expr
from flipjump.utils.exceptions import FlipJumpExprException


def _binary(op: str, a: int, b: int) -> Expr:
    return Expr((op, (Expr(a), Expr(b))))


def test_is_int() -> None:
    assert Expr(5).is_int()
    assert not Expr('x').is_int()
    assert not _binary('+', 1, 2).is_int()


def test_int_conversion_resolved() -> None:
    assert int(Expr(7)) == 7


def test_int_conversion_unresolved_raises() -> None:
    with pytest.raises(FlipJumpExprException):
        int(Expr('x'))


def test_all_unknown_labels() -> None:
    assert Expr(3).all_unknown_labels() == set()
    assert Expr('x').all_unknown_labels() == {'x'}
    assert Expr(('+', (Expr('a'), Expr(('*', (Expr('b'), Expr(2))))))).all_unknown_labels() == {'a', 'b'}


def test_eval_new_full_resolution() -> None:
    result = Expr(('+', (Expr('a'), Expr(2)))).eval_new({'a': Expr(3)})
    assert result.is_int()
    assert int(result) == 5


def test_eval_new_partial_keeps_unknown_but_folds_ints() -> None:
    result = Expr(('+', (Expr('a'), Expr(('*', (Expr(2), Expr(3))))))).eval_new({})
    assert not result.is_int()
    assert result.all_unknown_labels() == {'a'}


def test_exact_eval_full() -> None:
    assert Expr(('+', (Expr('a'), Expr(2)))).exact_eval({'a': 3}) == 5


def test_exact_eval_missing_label_raises() -> None:
    with pytest.raises(FlipJumpExprException):
        Expr(('+', (Expr('a'), Expr(2)))).exact_eval({})


@pytest.mark.parametrize(
    'op, a, b, expected',
    [
        ('+', 7, 3, 10),
        ('-', 7, 3, 4),
        ('*', 7, 3, 21),
        ('/', 7, 2, 3),
        ('%', 7, 3, 1),
        ('<<', 1, 4, 16),
        ('>>', 256, 4, 16),
        ('^', 0b1100, 0b1010, 0b0110),
        ('|', 0b1100, 0b1010, 0b1110),
        ('&', 0b1100, 0b1010, 0b1000),
        ('<', 2, 3, 1),
        ('<', 3, 2, 0),
        ('>', 3, 2, 1),
        ('<=', 3, 3, 1),
        ('>=', 2, 3, 0),
        ('==', 3, 3, 1),
        ('==', 3, 4, 0),
        ('!=', 3, 3, 0),
        ('!=', 3, 4, 1),
    ],
)
def test_binary_operators(op: str, a: int, b: int, expected: int) -> None:
    assert int(_binary(op, a, b).eval_new({})) == expected
    assert _binary(op, a, b).exact_eval({}) == expected


@pytest.mark.parametrize('value, expected', [(8, 4), (0, 0), (1, 1), (255, 8)])
def test_bit_length_operator(value: int, expected: int) -> None:
    assert int(Expr(('#', (Expr(value),))).eval_new({})) == expected


@pytest.mark.parametrize('condition, expected', [(1, 10), (0, 20)])
def test_ternary_operator(condition: int, expected: int) -> None:
    expr = Expr(('?:', (Expr(condition), Expr(10), Expr(20))))
    assert int(expr.eval_new({})) == expected


@pytest.mark.parametrize('op', ['/', '%'])
def test_division_by_zero_eval_new_raises(op: str) -> None:
    with pytest.raises(FlipJumpExprException):
        _binary(op, 1, 0).eval_new({})


@pytest.mark.parametrize('op', ['/', '%'])
def test_division_by_zero_exact_eval_raises(op: str) -> None:
    with pytest.raises(FlipJumpExprException):
        _binary(op, 1, 0).exact_eval({})


def test_get_minimized_expr_folds_all_ints() -> None:
    minimized = get_minimized_expr('+', (Expr(2), Expr(3)))
    assert minimized.is_int()
    assert int(minimized) == 5


def test_get_minimized_expr_keeps_tree_with_label() -> None:
    params: Tuple[Expr, ...] = (Expr('x'), Expr(3))
    minimized = get_minimized_expr('+', params)
    assert not minimized.is_int()
    assert minimized.all_unknown_labels() == {'x'}

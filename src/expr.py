from __future__ import annotations

from typing import Union, Tuple, Set, Dict
from operator import mul, add, sub, floordiv, lshift, rshift, mod, xor, or_, and_

from exceptions import FJExprException


# dictionary from a math-op string, to its pythonic function.
# @note: if changed, update Expr.__str__().
op_string_to_function = {
    '+': add, '-': sub, '*': mul, '/': floordiv, '%': mod,
    '<<': lshift, '>>': rshift, '^': xor, '|': or_, '&': and_,
    '#': lambda x: x.bit_length(),
    '?:': lambda a, b, c: b if a else c,
    '<': lambda a, b: 1 if a < b else 0,
    '>': lambda a, b: 1 if a > b else 0,
    '<=': lambda a, b: 1 if a <= b else 0,
    '>=': lambda a, b: 1 if a >= b else 0,
    '==': lambda a, b: 1 if a == b else 0,
    '!=': lambda a, b: 1 if a != b else 0,
}


class Expr:
    """
    The python representation of a .fj expression (from labels, consts and math-ops)
    """
    def __init__(self, expr: Union[int, str, Tuple[str, Tuple[Expr, ...]]]):
        self.value = expr

    def is_int(self) -> bool:
        return isinstance(self.value, int)

    def __int__(self):
        if self.is_int():
            return self.value
        raise FJExprException(f"Can't resolve labels:  {', '.join(self.all_unknown_labels())}")

    def all_unknown_labels(self) -> Set[str]:
        """
        @return: all labels used (recursively) in this expression.
        """
        if isinstance(self.value, int):
            return set()
        if isinstance(self.value, str):
            return {self.value}
        return set(label for expr in self.value[1] for label in expr.all_unknown_labels())

    def eval_new(self, id_dict: Dict[str, Expr]) -> Expr:
        """
        creates a new Expr, as minimal as possible.
        replaces every string it can with its dictionary value, and evaluates any op it can.
        @param id_dict: the label->ExprValue dictionary to be used
        @raise FJExprException if math op failed
        @return: the new Expr
        """
        if isinstance(self.value, int):
            return Expr(self.value)

        if isinstance(self.value, str):
            if self.value in id_dict:
                return id_dict[self.value].eval_new({})
            return Expr(self.value)

        op, args = self.value
        evaluated_args: Tuple[Expr, ...] = tuple(e.eval_new(id_dict) for e in args)
        if all(isinstance(e.value, int) for e in evaluated_args):
            try:
                return Expr(op_string_to_function[op](*(arg.value for arg in evaluated_args)))
            except Exception as e:
                raise FJExprException(f'{repr(e)}. bad math operation ({op}): {str(self)}.')
        return Expr((op, evaluated_args))

    def exact_eval(self, labels: Dict[str, int]) -> int:
        """
        evaluates the expression's value with the labels
        @param labels: the label->value dictionary to be used
        @raise FJExprException if it can't evaluate
        @return: the integer-value of the expression
        """
        if isinstance(self.value, int):
            return self.value

        if isinstance(self.value, str):
            if self.value in labels:
                return labels[self.value]
            raise FJExprException(f"Can't evaluate label {self.value} in expression {self}")

        op, args = self.value
        evaluated_args: Tuple[int, ...] = tuple(e.exact_eval(labels) for e in args)
        try:
            return op_string_to_function[op](*evaluated_args)
        except Exception as e:
            raise FJExprException(f'{repr(e)}. bad math operation ({op}): {str(self)}.')

    def __str__(self) -> str:
        if isinstance(self.value, tuple):
            op, expressions = self.value
            if len(expressions) == 1:
                e1 = expressions[0]
                return f'(#{str(e1)})'
            elif len(expressions) == 2:
                e1, e2 = expressions
                return f'({str(e1)} {op} {str(e2)})'
            else:
                e1, e2, e3 = expressions
                return f'({str(e1)} ? {str(e2)} : {str(e3)})'
        if isinstance(self.value, str):
            return self.value
        if isinstance(self.value, int):
            return hex(self.value)[2:]
        raise FJExprException(f'bad expression: {self.value} (of type {type(self.value)})')


def get_minimized_expr(op: str, params: Tuple[Expr, ...]) -> Expr:
    """
    tries to calculate the op on the params, if possible. returns the resulting Expr.
    @param op: the math-op string
    @param params: the op parameters
    @return: the expression
    """
    if all(param.is_int() for param in params):
        return Expr(op_string_to_function[op](*map(int, params)))
    else:
        return Expr((op, params))

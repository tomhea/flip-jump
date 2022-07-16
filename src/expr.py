from __future__ import annotations

from typing import Union, Tuple, Set, Dict
from operator import mul, add, sub, floordiv, lshift, rshift, mod, xor, or_, and_

from exceptions import FJExprException


parsing_op2func = {
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
    def __init__(self, expr: Union[int, str, Tuple[str, Tuple[Expr]]]):
        self.val = expr

    def __int__(self):
        if isinstance(self.val, int):
            return self.val
        raise FJExprException(f"Can't resolve labels:  {', '.join(self.all_unknown_labels())}")

    def all_unknown_labels(self) -> Set[str]:
        if isinstance(self.val, int):
            return set()
        if isinstance(self.val, str):
            return {self.val}
        return set(label for expr in self.val[1] for label in expr.all_unknown_labels())

    # replaces every string it can with its dictionary value, and evaluates anything it can.
    def eval_new(self, id_dict: Dict[str, Expr]) -> Expr:
        if isinstance(self.val, int):
            return Expr(self.val)

        if isinstance(self.val, str):
            if self.val in id_dict:
                return id_dict[self.val].eval_new({})
            return Expr(self.val)

        op, args = self.val
        evaluated_args: Tuple[Expr, ...] = tuple(e.eval_new(id_dict) for e in args)
        if all(isinstance(e.val, int) for e in evaluated_args):
            try:
                return Expr(parsing_op2func[op](*(arg.val for arg in evaluated_args)))
            except Exception as e:
                raise FJExprException(f'{repr(e)}. bad math operation ({op}): {str(self)}.')
        return Expr((op, evaluated_args))

    def __str__(self) -> str:
        if isinstance(self.val, tuple):
            op, exps = self.val
            if len(exps) == 1:
                e1 = exps[0]
                return f'(#{str(e1)})'
            elif len(exps) == 2:
                e1, e2 = exps
                return f'({str(e1)} {op} {str(e2)})'
            else:
                e1, e2, e3 = exps
                return f'({str(e1)} ? {str(e2)} : {str(e3)})'
        if isinstance(self.val, str):
            return self.val
        if isinstance(self.val, int):
            return hex(self.val)[2:]
        raise FJExprException(f'bad expression: {self.val} (of type {type(self.val)})')

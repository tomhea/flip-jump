from __future__ import annotations

from copy import copy
from dataclasses import dataclass
import json
from enum import IntEnum    # IntEnum equality works between files.
from pathlib import Path
from operator import mul, add, sub, floordiv, lshift, rshift, mod, xor, or_, and_
from time import time
from typing import List, Tuple, Dict, Union, Set


parsing_op2func = {'+': add, '-': sub, '*': mul, '/': floordiv, '%': mod,
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


class FJException(Exception):
    pass


class FJParsingException(FJException):
    pass


class FJPreprocessorException(FJException):
    pass


class FJExprException(FJException):
    pass


class FJAssemblerException(FJException):
    pass


class FJReadFjmException(FJException):
    pass


class FJWriteFjmException(FJException):
    pass


def smart_int16(num: str) -> int:
    try:
        return int(num, 16)
    except ValueError as ve:
        raise FJException(f'{num} is not a number!') from ve


STL_PATH = Path(__file__).parent.parent / 'stl'
with open(STL_PATH / 'conf.json', 'r') as stl_json:
    STL_OPTIONS = json.load(stl_json)


def get_stl_paths() -> List[Path]:
    return [STL_PATH / f'{lib}.fj' for lib in STL_OPTIONS['all']]


id_re = r'[a-zA-Z_][a-zA-Z_0-9]*'
dot_id_re = fr'(({id_re})|\.*)?(\.({id_re}))+'

bin_num = r'0[bB][01]+'
hex_num = r'0[xX][0-9a-fA-F]+'
dec_num = r'[0-9]+'

char_escape_dict = {'0': 0x0, 'a': 0x7, 'b': 0x8, 'e': 0x1b, 'f': 0xc, 'n': 0xa, 'r': 0xd, 't': 0x9, 'v': 0xb,
                    '\\': 0x5c, "'": 0x27, '"': 0x22, '?': 0x3f}
escape_chars = ''.join(k for k in char_escape_dict)
char = fr'[ -~]|\\[{escape_chars}]|\\[xX][0-9a-fA-F]{{2}}'

number_re = fr"({bin_num})|({hex_num})|('({char})')|({dec_num})"
string_re = fr'"({char})*"'


def get_char_value_and_length(s: str) -> Tuple[int, int]:
    if s[0] != '\\':
        return ord(s[0]), 1
    if s[1] in char_escape_dict:
        return char_escape_dict[s[1]], 2
    return int(s[2:4], 16), 4


class Verbose(IntEnum):
    Parse = 1
    LabelDict = 2
    LabelSolve = 3
    Run = 4
    Time = 5
    PrintOutput = 6


class TerminationCause(IntEnum):
    Looping = 0
    Input = 1
    NullIP = 2

    def __str__(self) -> str:
        return ['looping', 'input', 'ip<2w'][self.value]


class SegmentEntry(IntEnum):
    StartAddress = 0
    ReserveAddress = 1
    WflipAddress = 2


BoundaryAddressesList = List[Tuple[SegmentEntry, int]]


class PrintTimer:
    def __init__(self, init_message: str, *, print_time: bool = True):
        self.init_message = init_message
        self.print_time = print_time

    def __enter__(self) -> None:
        if self.print_time:
            self.start_time = time()
            print(self.init_message, end='', flush=True)

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.print_time:
            print(f'{time() - self.start_time:.3f}s')


class OpType(IntEnum):  # op.data array content:

    FlipJump = 1        # expr, expr                # Survives until (2) label resolve
    WordFlip = 2        # expr, expr, expr          # Survives until (2) label resolve
    Segment = 3         # expr                      # Survives until (2) label resolve
    Reserve = 4         # expr                      # Survives until (2) label resolve
    Label = 5           # ID                        # Survives until (1) macro resolve
    Macro = 6           # ID, [expr..]              # Survives until (1) macro resolve
    Rep = 7             # expr, ID, macro_call      # Survives until (1) macro resolve


@dataclass
class MacroName:
    name: str
    parameter_num: int

    def __str__(self) -> str:
        if 0 == self.parameter_num:
            return self.name
        return f"{self.name}({self.parameter_num})"

    def __hash__(self):
        return hash((self.name, self.parameter_num))


main_macro = MacroName('', 0)


@dataclass
class CodePosition:
    file: str
    file_number: int
    line: int

    def __str__(self) -> str:
        return f"file {self.file} (line {self.line})"

    def short_str(self) -> str:
        return f"f{self.file_number}:l{self.line}"


class Op:
    def __init__(self, op_type: OpType, data: List[Union[Expr, str, MacroCall], ...], code_position: CodePosition):
        self.type = op_type
        self.data = data
        self.code_position = code_position

    def __str__(self) -> str:
        return f'{f"{self.type}:"[7:]:10}    Data: {", ".join([str(d) for d in self.data])}    ' \
               f'{self.code_position}'

    def eval_int_data(self, id_dict: Dict[str, Expr]) -> Tuple[int]:
        return tuple(int(expr.eval_new(id_dict)) for expr in self.data)

    def eval_new(self, id_dict: Dict[str, Expr]) -> Op:
        op = copy(self)
        op.data = [expr.eval_new(id_dict) for expr in self.data]
        return op


class FlipJump(Op):
    def __init__(self, flip: Expr, jump: Expr, code_position: CodePosition):
        super(FlipJump, self).__init__(OpType.FlipJump, [flip, jump], code_position)

    def get_flip(self, label: Dict[str, Expr]) -> int:
        return int(self.data[0].eval_new(label))

    def get_jump(self, label: Dict[str, Expr]) -> int:
        return int(self.data[1].eval_new(label))


class MacroCall(Op):
    def __init__(self, macro_name: str, arguments: List[Expr], code_position: CodePosition):
        super(MacroCall, self).__init__(OpType.Macro, arguments, code_position)
        self.macro_name = MacroName(macro_name, len(arguments))

    def macro_trace_str(self) -> str:
        return f'macro {self.macro_name} ({self.code_position})'


class RepCall(Op):
    def __init__(self, times: Expr, iterator_name: str, macro_name: str, arguments: List[Expr], code_position: CodePosition):
        super(RepCall, self).__init__(OpType.Rep, [times, *arguments], code_position)
        self.iterator_name = iterator_name
        self.macro_name = MacroName(macro_name, len(arguments))

    def get_times(self) -> int:
        try:
            return int(self.data[0])
        except FJExprException as e:
            raise FJExprException(f"Can't calculate rep time on {self.code_position}") from e

    def calculate_times(self, labels: Dict[str, Expr]) -> int:
        self.data[0] = self.data[0].eval_new(labels)
        return self.get_times()

    def calculate_arguments(self, iterator_value: int) -> Tuple[Expr, ...]:
        iterator_dict = {self.iterator_name: Expr(iterator_value)}
        try:
            return tuple(expr.eval_new(iterator_dict) for expr in self.data[1:])
        except FJExprException as e:
            raise FJExprException(f"Can't calculate rep arguments on {self.code_position}") from e

    def rep_trace_str(self, iter_value: int) -> str:
        return f'rep({self.iterator_name}={iter_value}, out of 0..{self.get_times()-1}) ' \
               f'macro {self.macro_name}  ({self.code_position})'


class Macro:
    # [(params, quiet_params), statements, (curr_file, p.lineno, ns_name)]

    def __init__(self, params: List[str], local_params: List[str],
                 ops: List[Op], namespace: str,
                 code_position: CodePosition):
        self.params = params
        self.local_params = local_params
        self.ops = ops
        self.namespace = namespace
        self.code_position = code_position


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

    def eval_new(self, id_dict: Dict[str, Expr], i=0) -> Expr:
        # TODO remove i
        if isinstance(self.val, int):
            return Expr(self.val)

        if isinstance(self.val, str):
            if self.val in id_dict:
                return id_dict[self.val].eval_new({}, i+1)
            return Expr(self.val)

        op, args = self.val
        evaluated_args: Tuple[Expr, ...] = tuple(e.eval_new(id_dict, i+1) for e in args)
        if all(isinstance(e.val, int) for e in evaluated_args):
            try:
                return Expr(parsing_op2func[op](*(arg.val for arg in evaluated_args)))
            except Exception as e:
                raise FJExprException(f'{repr(e)}. bad math operation ({op}): {str(self)}.')
        return Expr((op, evaluated_args))

    # replaces every string it can with its dictionary value, and evaluates anything it can.
    # returns the list of unknown id's
    def eval(self, id_dict: Dict[str, Expr], code_position: CodePosition) -> List[str]:
        if self.is_tuple():
            op, exps = self.val
            res = [e.eval(id_dict, code_position) for e in exps]
            if any(res):
                return sum(res, start=[])
            else:
                try:
                    self.val = parsing_op2func[op](*[e.val for e in exps])
                    return []
                except BaseException as e:
                    raise FJExprException(f'{repr(e)}. bad math operation ({op}): {str(self)} in {code_position}')
        elif self.is_str():
            if self.val in id_dict:
                self.val = id_dict[self.val].val
                return self.eval({}, code_position)
            else:
                return [self.val]
        return []

    def is_int(self) -> bool:
        return type(self.val) is int

    def is_str(self) -> bool:
        return type(self.val) is str

    def is_tuple(self) -> bool:
        return type(self.val) is tuple

    def __str__(self) -> str:
        if self.is_tuple():
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
        if self.is_str():
            return self.val
        if self.is_int():
            return hex(self.val)[2:]
        raise FJExprException(f'bad expression: {self.val} (of type {type(self.val)})')


def eval_all(op: Op, id_dict: Dict[str, Expr] = None) -> List[str]:
    if id_dict is None:
        id_dict = {}

    ids = []
    for expr in op.data:
        if type(expr) is Expr:
            ids += expr.eval(id_dict, op.code_position)
    if op.type == OpType.Rep:
        macro_op = op.data[2]
        ids += eval_all(macro_op, id_dict)
    return ids


def get_all_used_labels(ops: List[Op]) -> Tuple[Set[str], Set[str]]:
    used_labels, declared_labels = set(), set()
    for op in ops:
        if isinstance(op, RepCall):
            n, *macro_call_data = op.data
            i = op.iterator_name
            used_labels.update(n.eval({}, op.code_position))
            new_labels = set()
            new_labels.update(*[e.eval({}, op.code_position) for e in macro_call_data])
            used_labels.update(new_labels - {i})
        elif op.type == OpType.Label:
            declared_labels.add(op.data[0])
        else:
            for expr in op.data:
                if type(expr) is Expr:
                    used_labels.update(expr.eval({}, op.code_position))
    return used_labels, declared_labels


def id_swap(op: Op, id_dict: Dict[str, Expr]) -> None:
    new_data = []
    for datum in op.data:
        if type(datum) is str and datum in id_dict:
            swapped_label = id_dict[datum]
            if not swapped_label.is_str():
                raise FJExprException(f'Bad label swap (from {datum} to {swapped_label}) in {op}.')
            new_data.append(swapped_label.val)
        else:
            new_data.append(datum)
    op.data = new_data


def new_label(macro_path: str, label_name: str) -> Expr:
    return Expr(f'{macro_path}---{label_name}')


wflip_start_label = '_.wflip_area_start_'


def next_address() -> Expr:
    return Expr('$')

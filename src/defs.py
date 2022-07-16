from __future__ import annotations

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


class TerminationCause(IntEnum):
    Looping = 0
    EOF = 1
    NullIP = 2

    def __str__(self) -> str:
        return ['looping', 'EOF', 'ip<2w'][self.value]


class SegmentEntry(IntEnum):
    StartAddress = 0
    ReserveAddress = 1
    WflipAddress = 2


BoundaryAddressesList = List[Tuple[SegmentEntry, int]]


macro_separator_string = "---"


def get_nice_label_repr(label: str, pad: int = 0) -> str:
    parts = label.split(macro_separator_string)
    return ' ->\n'.join(f"{' '*(pad+i)}{part}" for i, part in enumerate(parts))


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


class MacroName:
    def __init__(self, name: str, parameter_num: int = 0):
        self.name = name
        self.parameter_num = parameter_num

    def __str__(self) -> str:
        if 0 == self.parameter_num:
            return self.name
        return f"{self.name}({self.parameter_num})"

    def to_tuple(self):
        return self.name, self.parameter_num

    def __hash__(self):
        return hash(self.to_tuple())

    def __eq__(self, other):
        return type(other) == MacroName and self.to_tuple() == other.to_tuple()


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


main_macro = MacroName('')


@dataclass
class CodePosition:
    file: str
    file_short_name: str
    line: int

    def __str__(self) -> str:
        return f"file {self.file} (line {self.line})"

    def short_str(self) -> str:
        return f"{self.file_short_name}:l{self.line}"


class Label:
    def __init__(self, name: str, code_position: CodePosition):
        self.name = name
        self.code_position = code_position

    def __str__(self):
        return f'Label "{self.name}:", at {self.code_position}'

    def eval_name(self, id_dict: Dict[str, Expr]) -> str:
        if self.name in id_dict:
            new_name = id_dict[self.name].val
            if isinstance(new_name, str):
                return new_name
            raise FJExprException(f'Bad label swap (from {self.name} to {id_dict[self.name]}) in {self.code_position}.')
        return self.name


class FlipJump:
    """
    data = [flip_address, jump_address]
    """
    def __init__(self, flip: Expr, jump: Expr, code_position: CodePosition):
        self.flip = flip
        self.jump = jump
        self.code_position = code_position

    def __str__(self):
        return f"Flip: {self.flip}, Jump: {self.jump}, at {self.code_position}"

    def eval_new(self, id_dict: Dict[str, Expr]) -> FlipJump:
        return FlipJump(self.flip.eval_new(id_dict), self.jump.eval_new(id_dict), self.code_position)

    def all_unknown_labels(self) -> Set[str]:
        return {label
                for expr in (self.flip, self.jump)
                for label in expr.all_unknown_labels()}

    def get_flip(self, labels: Dict[str, Expr]) -> int:
        return int(self.flip.eval_new(labels))

    def get_jump(self, labels: Dict[str, Expr]) -> int:
        return int(self.jump.eval_new(labels))


class WordFlip:
    """
    data = [word_address, value, return_address]
    """
    def __init__(self, word_address: Expr, flip_value: Expr, return_address: Expr, code_position: CodePosition):
        self.word_address = word_address
        self.flip_value = flip_value
        self.return_address = return_address
        self.code_position = code_position

    def __str__(self):
        return f"Flip Word {self.word_address} by {self.flip_value}, and return to {self.return_address}. " \
               f"at {self.code_position}"

    def eval_new(self, id_dict: Dict[str, Expr]) -> WordFlip:
        return WordFlip(self.word_address.eval_new(id_dict), self.flip_value.eval_new(id_dict),
                        self.return_address.eval_new(id_dict), self.code_position)

    def all_unknown_labels(self) -> Set[str]:
        return {label
                for expr in (self.word_address, self.flip_value, self.return_address)
                for label in expr.all_unknown_labels()}

    def get_word_address(self, labels: Dict[str, Expr]) -> int:
        return int(self.word_address.eval_new(labels))

    def get_flip_value(self, labels: Dict[str, Expr]) -> int:
        return int(self.flip_value.eval_new(labels))

    def get_return_address(self, labels: Dict[str, Expr]) -> int:
        return int(self.return_address.eval_new(labels))


class Segment:
    """
    data = [start_address]
    """
    def __init__(self, start_address: Expr, code_position: CodePosition):
        self.start_address = start_address
        self.code_position = code_position

    def __str__(self):
        return f"Segment {self.start_address}, at {self.code_position}"

    def eval_new(self, id_dict: Dict[str, Expr]) -> Segment:
        return Segment(self.start_address.eval_new(id_dict), self.code_position)

    def all_unknown_labels(self) -> Set[str]:
        return {label for label in self.start_address.all_unknown_labels()}

    def get_address(self) -> int:
        try:
            return int(self.start_address)
        except FJExprException as e:
            raise FJExprException(f"Can't calculate segment address on {self.code_position}") from e

    def calculate_address(self, labels: Dict[str, Expr]) -> int:
        self.start_address = self.start_address.eval_new(labels)
        return self.get_address()


class Reserve:
    """
    data = [reserved_bit_size]
    """
    def __init__(self, reserved_bit_size: Expr, code_position: CodePosition):
        self.reserved_bit_size = reserved_bit_size
        self.code_position = code_position

    def __str__(self):
        return f"Reserve {self.reserved_bit_size}, at {self.code_position}"

    def eval_new(self, id_dict: Dict[str, Expr]) -> Reserve:
        return Reserve(self.reserved_bit_size.eval_new(id_dict), self.code_position)

    def all_unknown_labels(self) -> Set[str]:
        return {label for label in self.reserved_bit_size.all_unknown_labels()}

    def get_reserved_bit_size(self) -> int:
        try:
            return int(self.reserved_bit_size)
        except FJExprException as e:
            raise FJExprException(f"Can't calculate reserved bits size on {self.code_position}") from e

    def calculate_reserved_bit_size(self, labels: Dict[str, Expr]) -> int:
        self.reserved_bit_size = self.reserved_bit_size.eval_new(labels)
        return self.get_reserved_bit_size()


class MacroCall:
    """
    data = ordered list of macro arguments
    """
    def __init__(self, macro_name: str, arguments: List[Expr], code_position: CodePosition):
        self.macro_name = MacroName(macro_name, len(arguments))
        self.arguments = arguments
        self.code_position = code_position

    def __str__(self):
        return f"macro call. {self.macro_name.name} {', '.join(map(str, self.arguments))}. at {self.code_position}"

    def eval_new(self, id_dict: Dict[str, Expr]) -> MacroCall:
        return MacroCall(self.macro_name.name, [arg.eval_new(id_dict) for arg in self.arguments], self.code_position)

    def all_unknown_labels(self) -> Set[str]:
        return {label for expr in self.arguments for label in expr.all_unknown_labels()}

    def trace_str(self) -> str:
        return f'macro {self.macro_name} ({self.code_position})'


class RepCall:
    """
    data[0] = repeat_times
    data[1:] = ordered list of macro arguments
    """
    def __init__(self, repeat_times: Expr, iterator_name: str, macro_name: str, arguments: List[Expr],
                 code_position: CodePosition):
        self.repeat_times = repeat_times
        self.iterator_name = iterator_name
        self.macro_name = MacroName(macro_name, len(arguments))
        self.arguments = arguments
        self.code_position = code_position

    def __str__(self):
        return f"rep call. rep({self.repeat_times}, {self.iterator_name}) {self.macro_name.name} " \
               f"{', '.join(map(str, self.arguments))}. at {self.code_position}"

    def eval_new(self, id_dict: Dict[str, Expr]) -> RepCall:
        return RepCall(self.repeat_times.eval_new(id_dict), self.iterator_name, self.macro_name.name,
                       [expr.eval_new(id_dict) for expr in self.arguments], self.code_position)

    def all_unknown_labels(self) -> Set[str]:
        times = self.repeat_times
        arguments = self.arguments
        arguments_labels = set(label for e in arguments for label in e.all_unknown_labels())
        return times.all_unknown_labels() | (arguments_labels - {self.iterator_name})

    def get_times(self) -> int:
        try:
            return int(self.repeat_times)
        except FJExprException as e:
            raise FJExprException(f"Can't calculate rep times on {self.code_position}") from e

    def calculate_times(self, labels: Dict[str, Expr]) -> int:
        self.repeat_times = self.repeat_times.eval_new(labels)
        return self.get_times()

    def calculate_arguments(self, iterator_value: int) -> Tuple[Expr, ...]:
        iterator_dict = {self.iterator_name: Expr(iterator_value)}
        try:
            return tuple(expr.eval_new(iterator_dict) for expr in self.arguments)
        except FJExprException as e:
            raise FJExprException(f"Can't calculate rep arguments on {self.code_position}") from e

    def trace_str(self, iter_value: int) -> str:
        """
        assumes calculate_times successfully called before
        """
        return f'rep({self.iterator_name}={iter_value}, out of 0..{self.get_times()-1}) ' \
               f'macro {self.macro_name}  ({self.code_position})'


Op = Union[FlipJump, WordFlip, Label, MacroCall, RepCall, Segment, Reserve]
LastPhaseOp = Union[FlipJump, WordFlip, Segment, Reserve]


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


def get_used_labels(ops: List[Op]) -> Set[str]:
    used_labels = set()
    for op in ops:
        if not isinstance(op, Label):
            used_labels.update(op.all_unknown_labels())
    return used_labels


def get_declared_labels(ops: List[Op]) -> Set[str]:
    return set(op.name for op in ops if isinstance(op, Label))


def new_label(macro_path: str, label_name: str) -> Expr:
    return Expr(f'{macro_path}---{label_name}')


wflip_start_label = '_.wflip_area_start_'


def next_address() -> Expr:
    return Expr('$')


bytes_encoding = 'raw_unicode_escape'

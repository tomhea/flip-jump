from __future__ import annotations

from dataclasses import dataclass
from typing import Union, Dict, Set, List, Tuple

from expr import Expr
from exceptions import FJExprException


@dataclass
class CodePosition:
    file: str
    file_short_name: str
    line: int

    def __str__(self) -> str:
        return f"file {self.file} (line {self.line})"

    def short_str(self) -> str:
        return f"{self.file_short_name}:l{self.line}"


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


main_macro = MacroName('')


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


class Label:
    def __init__(self, name: str, code_position: CodePosition):
        self.name = name
        self.code_position = code_position

    def __str__(self):
        return f'Label "{self.name}:", at {self.code_position}'

    def eval_name(self, id_dict: Dict[str, Expr]) -> str:
        if self.name in id_dict:
            new_name = id_dict[self.name].value
            if isinstance(new_name, str):
                return new_name
            raise FJExprException(f'Bad label swap (from {self.name} to {id_dict[self.name]}) in {self.code_position}.')
        return self.name


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


Op = Union[FlipJump, WordFlip, Label, MacroCall, RepCall, Segment, Reserve]


WFLIP_NOT_INSERTED_YET = -1


class NewSegment:
    def __init__(self, start_address: int):
        self.start_address = start_address
        self.wflip_start_address = WFLIP_NOT_INSERTED_YET


class ReserveBits:
    def __init__(self, first_address_after_reserved: int):
        self.first_address_after_reserved = first_address_after_reserved


LastPhaseOp = Union[FlipJump, WordFlip, NewSegment, ReserveBits]

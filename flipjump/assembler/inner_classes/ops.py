from __future__ import annotations

import dataclasses
import os
from dataclasses import dataclass
from typing import Union, Dict, Set, List, Tuple

from flipjump.utils.exceptions import FlipJumpExprException
from flipjump.assembler.inner_classes.expr import Expr


@dataclass
class CodePosition:
    """
    A position in the .fj files.
    """
    file: str
    file_short_name: str    # shortened file name. usually s1,s2,... for stl, and f1,f2,... for the rest.
    line: int

    def __str__(self) -> str:
        return f"file {self.file} (line {self.line})"

    def short_str(self) -> str:
        return f"{self.file_short_name}:l{self.line}"

    def __repr__(self) -> str:
        return f"{os.path.basename(self.file)}:{self.line}"


class MacroName:
    """
    Unique for every macro definition.
    """
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

    def __repr__(self):
        return str(self)


# The macro that holds the ops that are outside any macro.
initial_macro_name = MacroName('')
initial_args = []
initial_labels_prefix = ''


class FlipJump:
    """
    The python representation of the "flip; jump" fj-assembly op.
    """
    def __init__(self, flip: Expr, jump: Expr, code_position: CodePosition):
        self.flip = flip
        self.jump = jump
        self.code_position = code_position

    def __str__(self):
        return f"Flip: {self.flip}, Jump: {self.jump}, at {self.code_position}"

    def eval_new(self, labels_dict: Dict[str, Expr]) -> FlipJump:
        return FlipJump(self.flip.eval_new(labels_dict), self.jump.eval_new(labels_dict), self.code_position)

    def all_unknown_labels(self) -> Set[str]:
        return {label
                for expr in (self.flip, self.jump)
                for label in expr.all_unknown_labels()}

    def get_flip(self, labels: Dict[str, int]) -> int:
        return self.flip.exact_eval(labels)

    def get_jump(self, labels: Dict[str, int]) -> int:
        return self.jump.exact_eval(labels)


class WordFlip:
    """
    The python representation of the "wflip address, value [, return_address]" fj-assembly op.
    """
    def __init__(self, word_address: Expr, flip_value: Expr, return_address: Expr, code_position: CodePosition):
        self.word_address = word_address
        self.flip_value = flip_value
        self.return_address = return_address
        self.code_position = code_position

    def __str__(self):
        return f"Flip Word {self.word_address} by {self.flip_value}, and return to {self.return_address}. " \
               f"at {self.code_position}"

    def eval_new(self, labels_dict: Dict[str, Expr]) -> WordFlip:
        return WordFlip(self.word_address.eval_new(labels_dict), self.flip_value.eval_new(labels_dict),
                        self.return_address.eval_new(labels_dict), self.code_position)

    def all_unknown_labels(self) -> Set[str]:
        return {label
                for expr in (self.word_address, self.flip_value, self.return_address)
                for label in expr.all_unknown_labels()}

    def get_word_address(self, labels: Dict[str, int]) -> int:
        return self.word_address.exact_eval(labels)

    def get_flip_value(self, labels: Dict[str, int]) -> int:
        return self.flip_value.exact_eval(labels)

    def get_return_address(self, labels: Dict[str, int]) -> int:
        return self.return_address.exact_eval(labels)


class Pad:
    """
    The python representation of the "pad ops_alignment" fj-assembly op.
    """
    def __init__(self, ops_alignment: Expr, code_position: CodePosition):
        self.ops_alignment = ops_alignment
        self.code_position = code_position

    def __str__(self):
        return f"Pad {self.ops_alignment} ops, at {self.code_position}"

    def eval_new(self, labels_dict: Dict[str, Expr]) -> Pad:
        return Pad(self.ops_alignment.eval_new(labels_dict), self.code_position)

    def all_unknown_labels(self) -> Set[str]:
        return self.ops_alignment.all_unknown_labels()

    def calculate_ops_alignment(self, labels: Dict[str, int]) -> int:
        try:
            return self.ops_alignment.exact_eval(labels)
        except FlipJumpExprException as e:
            raise FlipJumpExprException(f"Can't calculate pad ops_alignment on {self.code_position}") from e


class Segment:
    """
    The python representation of the "segment start_address" fj-assembly op.
    """
    def __init__(self, start_address: Expr, code_position: CodePosition):
        self.start_address = start_address
        self.code_position = code_position

    def __str__(self):
        return f"Segment {self.start_address}, at {self.code_position}"

    def eval_new(self, labels_dict: Dict[str, Expr]) -> Segment:
        return Segment(self.start_address.eval_new(labels_dict), self.code_position)

    def all_unknown_labels(self) -> Set[str]:
        return {label for label in self.start_address.all_unknown_labels()}

    def calculate_address(self, labels: Dict[str, int]) -> int:
        try:
            return self.start_address.exact_eval(labels)
        except FlipJumpExprException as e:
            raise FlipJumpExprException(f"Can't calculate segment address on {self.code_position}") from e


class Reserve:
    """
    The python representation of the "reserve bit_size" fj-assembly op.
    """
    def __init__(self, reserved_bit_size: Expr, code_position: CodePosition):
        self.reserved_bit_size = reserved_bit_size
        self.code_position = code_position

    def __str__(self):
        return f"Reserve {self.reserved_bit_size}, at {self.code_position}"

    def eval_new(self, labels_dict: Dict[str, Expr]) -> Reserve:
        return Reserve(self.reserved_bit_size.eval_new(labels_dict), self.code_position)

    def all_unknown_labels(self) -> Set[str]:
        return {label for label in self.reserved_bit_size.all_unknown_labels()}

    def calculate_reserved_bit_size(self, labels: Dict[str, int]) -> int:
        try:
            return self.reserved_bit_size.exact_eval(labels)
        except FlipJumpExprException as e:
            raise FlipJumpExprException(f"Can't calculate reserved bits size on {self.code_position}") from e


class MacroCall:
    """
    The python representation of the "macro-call [args...]" fj-assembly op.
    """
    def __init__(self, macro_name: str, arguments: List[Expr], code_position: CodePosition):
        self.macro_name = MacroName(macro_name, len(arguments))
        self.arguments = arguments
        self.code_position = code_position

    def __str__(self):
        return f"macro call. {self.macro_name.name} {', '.join(map(str, self.arguments))}. at {self.code_position}"

    def eval_new(self, labels_dict: Dict[str, Expr]) -> MacroCall:
        return MacroCall(self.macro_name.name, [arg.eval_new(labels_dict) for arg in self.arguments],
                         self.code_position)

    def all_unknown_labels(self) -> Set[str]:
        return {label for expr in self.arguments for label in expr.all_unknown_labels()}

    def trace_str(self) -> str:
        return f'macro {self.macro_name} ({self.code_position})'


class RepCall:
    """
    The python representation of the "rep(n, i) macro_call [args...]" fj-assembly op.
    """
    def __init__(self, repeat_times: Expr, iterator_name: str, macro_name: str, arguments: List[Expr],
                 code_position: CodePosition):
        self.current_index = 0
        self.repeat_times = repeat_times
        self.iterator_name = iterator_name
        self.macro_name = MacroName(macro_name, len(arguments))
        self.arguments = arguments
        self.code_position = code_position

    def __str__(self):
        return f"rep call. rep({self.repeat_times}, {self.iterator_name}) {self.macro_name.name} " \
               f"{', '.join(map(str, self.arguments))}. at {self.code_position}"

    def eval_new(self, labels_dict: Dict[str, Expr]) -> RepCall:
        return RepCall(self.repeat_times.eval_new(labels_dict), self.iterator_name, self.macro_name.name,
                       [expr.eval_new(labels_dict) for expr in self.arguments], self.code_position)

    def all_unknown_labels(self) -> Set[str]:
        times = self.repeat_times
        arguments = self.arguments
        arguments_labels = set(label for e in arguments for label in e.all_unknown_labels())
        return times.all_unknown_labels() | (arguments_labels - {self.iterator_name})

    def get_times(self) -> int:
        try:
            return int(self.repeat_times)
        except FlipJumpExprException as e:
            raise FlipJumpExprException(f"Can't calculate rep times on {self.code_position}") from e

    def calculate_times(self, labels: Dict[str, int]) -> int:
        try:
            times = self.repeat_times.exact_eval(labels)
            self.repeat_times = Expr(times)
            return times
        except FlipJumpExprException as e:
            raise FlipJumpExprException(f"Can't calculate rep times on {self.code_position}") from e

    def calculate_arguments(self, iterator_value: int) -> Tuple[Expr, ...]:
        iterator_dict = {self.iterator_name: Expr(iterator_value)}
        try:
            return tuple(expr.eval_new(iterator_dict) for expr in self.arguments)
        except FlipJumpExprException as e:
            raise FlipJumpExprException(f"Can't calculate rep arguments on {self.code_position}") from e

    def trace_str(self) -> str:
        """
        @note assumes calculate_times successfully called before
        """
        return f'rep({self.iterator_name}={self.current_index}, out of 0..{int(self.repeat_times)-1}) ' \
               f'macro {self.macro_name}  ({self.code_position})'


class Label:
    """
    The python representation of the "label:" fj-assembly op.
    """
    def __init__(self, name: str, code_position: CodePosition):
        self.name = name
        self.code_position = code_position

    def __str__(self):
        return f'Label "{self.name}:", at {self.code_position}'

    def eval_name(self, labels_dict: Dict[str, Expr]) -> str:
        if self.name in labels_dict:
            new_name = labels_dict[self.name].value
            if isinstance(new_name, str):
                return new_name
            raise FlipJumpExprException(
                f'Bad label swap (from {self.name} to {labels_dict[self.name]}) in {self.code_position}.')
        return self.name


def get_used_labels(ops: List[Op]) -> Set[str]:
    used_labels = set()
    for op in ops:
        if not isinstance(op, Label):
            used_labels.update(op.all_unknown_labels())
    return used_labels


def get_declared_labels(ops: List[Op]) -> Set[str]:
    return set(op.name for op in ops if isinstance(op, Label))


# The input for the preprocessor
Op = Union[FlipJump, WordFlip, Pad, Label, MacroCall, RepCall, Segment, Reserve]


@dataclasses.dataclass
class Macro:
    """
    The python representation of a .fj macro (macro declaration).
    """
    params: List[str]
    local_params: List[str]
    ops: List[Op]
    namespace: str
    code_position: CodePosition

    def __repr__(self) -> str:
        return f'{self.namespace}.MACRO({", ".join(self.params)})  ({repr(self.code_position)})'


WFLIP_NOT_INSERTED_YET = -1


class NewSegment:
    """
    The python expressions-resolved (all compilation data is known) representation
     of the "segment start_address" fj-assembly op.
    """
    def __init__(self, start_address: int):
        """
        @param start_address: the first address of the new segment
        """
        self.start_address = start_address

        # a stub, to be resolved later with the start of the wflip area address
        self.wflip_start_address = WFLIP_NOT_INSERTED_YET


class ReserveBits:
    """
    The python expressions-resolved (all compilation data is known) representation
     of the "reserve bit_size" fj-assembly op.
    """
    def __init__(self, first_address_after_reserved: int):
        """
        @param first_address_after_reserved: the address right after the reserved "segment".
        """
        self.first_address_after_reserved = first_address_after_reserved


class Padding:
    """
    The python expressions-resolved (all compilation data is known) representation
     of the "pad ops_alignment" fj-assembly op.
    """
    def __init__(self, ops_count: int):
        """
        @param ops_count: the number of fj-ops to pad.
        """
        self.ops_count = ops_count


# The input to the labels-resolve
LastPhaseOp = Union[FlipJump, WordFlip, Padding, NewSegment, ReserveBits]

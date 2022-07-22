from __future__ import annotations
import collections
from typing import Dict, Tuple, Iterable, Union, Deque

import plotly.graph_objects as go

from defs import main_macro, wflip_start_label, \
    CodePosition, Macro, MacroName, \
    macro_separator_string
from exceptions import FJPreprocessorException, FJExprException
from expr import Expr
from ops import FlipJump, WordFlip, Label, Segment, Reserve, MacroCall, RepCall, LastPhaseOp, new_label, NewSegment, \
    ReserveBits

CurrTree = Deque[Union[MacroCall, RepCall]]
PreprocessorResults = Tuple[Deque[LastPhaseOp], Dict[str, Expr]]


def macro_resolve_error(curr_tree: CurrTree, msg='', *, orig_exception: BaseException = None) -> None:
    error_str = f"Macro Resolve Error" + (f':\n  {msg}\n' if msg else '.\n')
    if curr_tree:
        error_str += 'Macro call trace:\n'
        for i, op in enumerate(curr_tree):
            error_str += f'  {i}) {op.trace_str()}\n'
    raise FJPreprocessorException(error_str) from orig_exception


def clean_name_for_pie_graph(macro_name: str) -> str:
    return macro_name


def show_macro_usage_pie_graph(macro_code_size: Dict[str, int], total_code_size: int, *,
                               min_main_thresh: float = 0.05, min_secondary_thresh: float = 0.01,
                               child_significance_min_thresh: float = 0.1) -> None:
    main_thresh = min_main_thresh * total_code_size
    secondary_thresh = min_secondary_thresh * total_code_size
    first_level = {}
    second_level = collections.defaultdict(lambda: dict())
    for k, v in macro_code_size.items():
        if macro_separator_string not in k:
            if v < main_thresh:
                continue
            first_level[k] = v
        else:
            if v < secondary_thresh:
                continue
            k_split = k.split(macro_separator_string)
            if len(k_split) != 2:
                continue
            parent, name = k_split
            if float(v) / macro_code_size[parent] < child_significance_min_thresh:
                continue
            second_level[parent][name] = v

    chosen = []
    for k, v in sorted(first_level.items(), key=lambda x: x[1], reverse=True):
        k_name = clean_name_for_pie_graph(k)
        if len(second_level[k]) == 0:
            chosen.append((k_name, v))
        else:
            for k2, v2 in sorted(second_level[k].items(), key=lambda x: x[1], reverse=True):
                k2_name = clean_name_for_pie_graph(k2)
                chosen.append((f"{k_name}  =>  {k2_name}", v2))
                v -= v2
            if v >= secondary_thresh:
                chosen.append((f"{k_name} others", v))

    others = total_code_size - sum([value for label, value in chosen])
    chosen.append(('all others', others))

    fig = go.Figure(data=[go.Pie(labels=[label for label, value in chosen],
                                 values=[value for label, value in chosen],
                                 textinfo='label+percent'
                                 )])
    fig.show()


class PreprocessorData:
    class _PrepareMacroCall:
        def __init__(self, curr_tree: CurrTree,
                     calling_op: Union[MacroCall, RepCall], macros: Dict[MacroName, Macro]):
            self.curr_tree = curr_tree
            self.calling_op = calling_op
            self.macros = macros

        def __enter__(self):
            macro_name = self.calling_op.macro_name
            if macro_name not in self.macros:
                macro_resolve_error(self.curr_tree, f"macro {macro_name} is used but isn't defined.")
            self.curr_tree.append(self.calling_op)

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.curr_tree.pop()

    def __init__(self):
        self.curr_address: int = 0

        self.macro_code_size = collections.defaultdict(lambda: 0)

        self.curr_tree: CurrTree = collections.deque()

        self.curr_segment_index: int = 0
        self.labels_code_positions: Dict[str, CodePosition] = {}

        self.result_ops: Deque[LastPhaseOp] = collections.deque()
        self.labels: Dict[str, Expr] = {}

        first_segment: NewSegment = NewSegment(0)
        self.last_new_segment: NewSegment = first_segment
        self.result_ops.append(first_segment)

    def patch_last_wflip_address(self):
        self.last_new_segment.wflip_start_address = self.curr_address

    def finish(self, show_statistics: bool):
        self.patch_last_wflip_address()
        if show_statistics:
            show_macro_usage_pie_graph(dict(self.macro_code_size), self.curr_address)

    def prepare_macro_call(self, calling_op: Union[MacroCall, RepCall], macros: Dict[MacroName, Macro])\
            -> PreprocessorData._PrepareMacroCall:
        return PreprocessorData._PrepareMacroCall(self.curr_tree, calling_op, macros)

    def get_results(self) -> PreprocessorResults:
        return self.result_ops, self.labels

    def insert_segment(self, next_segment_start: int) -> None:
        self.labels[f'{wflip_start_label}{self.curr_segment_index}'] = Expr(self.curr_address)
        self.curr_segment_index += 1

        self.patch_last_wflip_address()

        new_segment = NewSegment(next_segment_start)
        self.last_new_segment = new_segment
        self.result_ops.append(new_segment)

        self.curr_address = next_segment_start

    def insert_reserve(self, reserved_bits_size: int) -> None:
        self.curr_address += reserved_bits_size
        self.result_ops.append(ReserveBits(self.curr_address))

    def insert_label(self, label: str, code_position: CodePosition):
        if label in self.labels:
            other_position = self.labels_code_positions[label]
            macro_resolve_error(self.curr_tree, f'label declared twice - "{label}" on '
                                                f'{code_position} and {other_position}')
        self.labels_code_positions[label] = code_position
        self.labels[label] = Expr(self.curr_address)

    def register_macro_code_size(self, macro_path: str, init_curr_address: int):
        if 1 <= len(self.curr_tree) <= 2:
            self.macro_code_size[macro_path] += self.curr_address - init_curr_address


def resolve_macros(w: int, macros: Dict[MacroName, Macro], show_statistics: bool = False)\
        -> PreprocessorResults:
    preprocessor_data = PreprocessorData()
    resolve_macro_aux(preprocessor_data,
                      w, macros,
                      main_macro, [], '')

    preprocessor_data.finish(show_statistics)
    return preprocessor_data.get_results()


def resolve_macro_aux(preprocessor_data: PreprocessorData,
                      w: int, macros: Dict[MacroName, Macro],
                      macro_name: MacroName, args: Iterable[Expr], macro_path: str) -> None:

    init_curr_address = preprocessor_data.curr_address
    current_macro = macros[macro_name]
    id_dict = get_id_dictionary(current_macro, args, current_macro.namespace, macro_path)

    for op in current_macro.ops:

        if isinstance(op, Label):
            preprocessor_data.insert_label(op.eval_name(id_dict), op.code_position)

        elif isinstance(op, FlipJump) or isinstance(op, WordFlip):
            preprocessor_data.curr_address += 2 * w
            id_dict['$'] = Expr(preprocessor_data.curr_address)
            preprocessor_data.result_ops.append(op.eval_new(id_dict))
            del id_dict['$']

        elif isinstance(op, MacroCall):
            op = op.eval_new(id_dict)
            next_macro_path = (f"{macro_path}{macro_separator_string}" if macro_path else "") + \
                f"{op.code_position.short_str()}:{op.macro_name}"
            with preprocessor_data.prepare_macro_call(op, macros):
                resolve_macro_aux(preprocessor_data,
                                  w, macros,
                                  op.macro_name, op.arguments, next_macro_path)

        elif isinstance(op, RepCall):
            op = op.eval_new(id_dict)
            rep_times = get_rep_times(op, preprocessor_data)
            if rep_times == 0:
                continue
            next_macro_path = (f"{macro_path}{macro_separator_string}" if macro_path else "") + \
                f"{op.code_position.short_str()}:rep{{}}:{op.macro_name}"
            with preprocessor_data.prepare_macro_call(op, macros):
                for i in range(rep_times):
                    resolve_macro_aux(preprocessor_data,
                                      w, macros,
                                      op.macro_name, op.calculate_arguments(i), next_macro_path.format(i))

        elif isinstance(op, Segment):
            op = op.eval_new(id_dict)
            next_segment_start = get_next_segment_start(op, preprocessor_data, w)
            preprocessor_data.insert_segment(next_segment_start)

        elif isinstance(op, Reserve):
            op = op.eval_new(id_dict)
            reserved_bits_size = get_reserved_bits_size(op, preprocessor_data, w)
            preprocessor_data.insert_reserve(reserved_bits_size)

        else:
            macro_resolve_error(preprocessor_data.curr_tree, f"Can't assemble this opcode - {str(op)}")

    preprocessor_data.register_macro_code_size(macro_path, init_curr_address)


def get_rep_times(op: RepCall, preprocessor_data: PreprocessorData):
    try:
        return op.calculate_times(preprocessor_data.labels)
    except FJExprException as e:
        macro_resolve_error(preprocessor_data.curr_tree, f'rep {op.macro_name} failed.', orig_exception=e)


def get_next_segment_start(op: Segment, preprocessor_data: PreprocessorData, w: int):
    try:
        next_segment_start = op.calculate_address(preprocessor_data.labels)
        if next_segment_start % w != 0:
            macro_resolve_error(preprocessor_data.curr_tree, f'segment ops must have a w-aligned address: '
                                                             f'{hex(next_segment_start)}. In {op.code_position}.')
        return next_segment_start
    except FJExprException as e:
        macro_resolve_error(preprocessor_data.curr_tree, f'segment failed.', orig_exception=e)


def get_reserved_bits_size(op: Reserve, preprocessor_data: PreprocessorData, w: int):
    try:
        reserved_bits_size = op.calculate_reserved_bit_size(preprocessor_data.labels)
        if reserved_bits_size % w != 0:
            macro_resolve_error(preprocessor_data.curr_tree, f'reserve ops must have a w-aligned value: '
                                                             f'{hex(reserved_bits_size)}. In {op.code_position}.')
        return reserved_bits_size
    except FJExprException as e:
        macro_resolve_error(preprocessor_data.curr_tree, f'reserve failed.', orig_exception=e)


def get_id_dictionary(current_macro: Macro, args: Iterable[Expr], namespace: str, macro_path: str):
    id_dict: Dict[str, Expr] = dict(zip(current_macro.params, args))
    for local_param in current_macro.local_params:
        id_dict[local_param] = new_label(macro_path, local_param)
    if namespace:
        for k in list(id_dict.keys()):
            id_dict[f'{namespace}.{k}'] = id_dict[k]
    return id_dict

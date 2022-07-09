import collections
from copy import deepcopy
from pathlib import Path
from typing import Dict, List, Tuple, Iterable

import plotly.graph_objects as go

from defs import main_macro, wflip_start_label, new_label, \
    Op, OpType, SegmentEntry, Expr, FJPreprocessorException, \
    eval_all, CodePosition, Macro, MacroName, BoundaryAddressesList, MacroCall, RepCall, FJExprException, \
    FlipJump, WordFlip, Label

macro_separator_string = "---"


def macro_resolve_error(curr_tree: List[str], msg='', *, orig_exception: BaseException = None) -> None:
    error_str = f"Macro Resolve Error" + (f':\n  {msg}' if msg else '.') + f'\nmacro call trace:\n'
    for i, trace_str in enumerate(curr_tree):
        error_str += f'  {i}) {trace_str}\n'
    raise FJPreprocessorException(error_str) from orig_exception


def output_ops(ops: List[Op], output_file: Path) -> None:
    with open(output_file, 'w') as f:
        for op in ops:
            eval_all(op)
            if op.type == OpType.FlipJump:
                f.write(f'  {op.data[0]};{op.data[1]}\n')
            elif op.type == OpType.WordFlip:
                f.write(f'  wflip {op.data[0]}, {op.data[1]}, {op.data[2]}\n')
            elif op.type == OpType.Label:
                f.write(f'{op.data[0]}:\n')


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


def resolve_macros(w: int, macros: Dict[MacroName, Macro],
                   output_file: Path = None, show_statistics: bool = False)\
        -> Tuple[List[Op], Dict[str, Expr], BoundaryAddressesList]:
    curr_address = [0]
    result_ops: List[Op] = []
    labels: Dict[str, Expr] = {}
    last_address_index = [0]
    boundary_addresses: BoundaryAddressesList = [(SegmentEntry.StartAddress, 0)]  # SegEntries
    stat_dict = collections.defaultdict(lambda: 0)

    resolve_macro_aux(w, '', [], macros, main_macro, [], stat_dict,
                      labels, result_ops, boundary_addresses, curr_address, last_address_index, {})
    if output_file:
        output_ops(result_ops, output_file)

    if show_statistics:
        show_macro_usage_pie_graph(dict(stat_dict), curr_address[0])

    boundary_addresses.append((SegmentEntry.WflipAddress, curr_address[0]))
    return result_ops, labels, boundary_addresses


def try_int(op: Op, expr: Expr) -> int:
    if expr.is_int():
        return expr.val
    raise FJPreprocessorException(f"Can't resolve the following name: {expr.eval({}, op.code_position)} (in op={op}).")


def resolve_macro_aux(w: int, macro_path: str, curr_tree: List[str], macros: Dict[MacroName, Macro],
                      macro_name: MacroName, args: Iterable[Expr], macro_code_size: Dict[str, int],
                      labels: Dict[str, Expr], result_ops: List[Op], boundary_addresses: BoundaryAddressesList, curr_address: List[int], last_address_index, labels_code_positions: Dict[str, CodePosition],
                      code_position: CodePosition = None)\
        -> None:
    init_curr_address = curr_address[0]

    if macro_name not in macros:
        if not code_position:
            macro_resolve_error(curr_tree, f"macro {macro_name} isn't defined.")
        else:
            macro_resolve_error(curr_tree, f"macro {macro_name} isn't defined. Used in {code_position}.")

    current_macro = macros[macro_name]

    id_dict = get_id_dictionary(current_macro, args, current_macro.namespace, macro_path)

    for op in current_macro.ops:
        # macro-resolve
        if not isinstance(op, Label) and op.type not in (OpType.Rep, OpType.FlipJump, OpType.Macro):
            op = deepcopy(op)
            eval_all(op, id_dict)

        if isinstance(op, Label):
            label = op.eval_name(id_dict)
            if label in labels:
                other_position = labels_code_positions[label]
                macro_resolve_error(curr_tree, f'label declared twice - "{label}" on {op.code_position} '
                                               f'and {other_position}')
            labels[label] = Expr(curr_address[0])
            labels_code_positions[label] = op.code_position
        elif isinstance(op, FlipJump) or isinstance(op, WordFlip):
            curr_address[0] += 2 * w
            id_dict['$'] = Expr(curr_address[0])
            result_ops.append(op.eval_new(id_dict))
            del id_dict['$']
        elif isinstance(op, MacroCall):
            op = op.eval_new(id_dict)

            next_macro_path = (f"{macro_path}{macro_separator_string}" if macro_path else "") + \
                f"{op.code_position.short_str()}:{op.macro_name}"

            resolve_macro_aux(w, next_macro_path, curr_tree + [op.macro_trace_str()], macros,
                              op.macro_name, op.data, macro_code_size,
                              labels, result_ops, boundary_addresses, curr_address, last_address_index,
                              labels_code_positions, code_position=op.code_position)
        elif isinstance(op, RepCall):
            op = op.eval_new(id_dict)

            try:
                times = op.calculate_times(labels)
                if times == 0:
                    continue

                next_macro_path = (f"{macro_path}{macro_separator_string}" if macro_path else "") + \
                                  f"{op.code_position.short_str()}:rep{{}}:{op.macro_name}"

                for i in range(times):
                    resolve_macro_aux(w, next_macro_path.format(i), curr_tree + [op.rep_trace_str(i)], macros,
                                      op.macro_name, op.calculate_arguments(i), macro_code_size,
                                      labels, result_ops, boundary_addresses, curr_address, last_address_index,
                                      labels_code_positions, code_position=op.code_position)
            except FJExprException as e:
                macro_resolve_error(curr_tree, f'rep {op.macro_name} failed.', orig_exception=e)
        # labels_resolve
        elif op.type == OpType.Segment:
            eval_all(op, labels)
            value = try_int(op, op.data[0])
            if value % w != 0:
                macro_resolve_error(curr_tree, f'segment ops must have a w-aligned address. In {op}.')

            boundary_addresses.append((SegmentEntry.WflipAddress, curr_address[0]))
            labels[f'{wflip_start_label}{last_address_index[0]}'] = Expr(curr_address[0])
            last_address_index[0] += 1

            curr_address[0] = value
            boundary_addresses.append((SegmentEntry.StartAddress, curr_address[0]))
            result_ops.append(op)
        elif op.type == OpType.Reserve:
            eval_all(op, labels)
            value = try_int(op, op.data[0])
            if value % w != 0:
                macro_resolve_error(curr_tree, f'reserve ops must have a w-aligned value. In {op}.')

            curr_address[0] += value
            boundary_addresses.append((SegmentEntry.ReserveAddress, curr_address[0]))
            labels[f'{wflip_start_label}{last_address_index[0]}'] = Expr(curr_address[0])

            last_address_index[0] += 1
            result_ops.append(op)
        else:
            macro_resolve_error(curr_tree, f"Can't assemble this opcode - {str(op)}")
            if not isinstance(op, Op):
                macro_resolve_error(curr_tree, f"bad op (not of Op type)! type {type(op)}, str {str(op)}.")

    if 1 <= len(curr_tree) <= 2:
        macro_code_size[macro_path] += curr_address[0] - init_curr_address


def get_id_dictionary(current_macro: Macro, args: Iterable[Expr], namespace: str, macro_path: str):
    id_dict: Dict[str, Expr] = dict(zip(current_macro.params, args))
    for local_param in current_macro.local_params:
        id_dict[local_param] = new_label(macro_path, local_param)
    if namespace:
        for k in list(id_dict.keys()):
            id_dict[f'{namespace}.{k}'] = id_dict[k]
    return id_dict

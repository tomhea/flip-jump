import collections
from copy import deepcopy
from itertools import count
from pathlib import Path
from typing import Dict, List, Tuple, Iterable

import plotly.graph_objects as go

from defs import main_macro, wflip_start_label, new_label, \
    Op, OpType, SegmentEntry, Expr, FJPreprocessorException, \
    eval_all, id_swap, CodePosition, Macro, MacroName, BoundaryAddressesList, MacroCall


def macro_resolve_error(curr_tree: List[str], msg='') -> None:
    error_str = f"Macro Resolve Error" + (f':\n  {msg}' if msg else '.') + f'\nmacro call trace:\n'
    for i, trace_str in enumerate(curr_tree):
        error_str += f'  {i}) {trace_str}\n'
    raise FJPreprocessorException(error_str)


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
    if '_rep_' not in macro_name:
        return macro_name

    try:
        # TODO macro_name might have some legitimate underscores
        rep_count = macro_name.split('_')[3]
        inner_macro = macro_name.split("'")[1]
        arg_count = macro_name.split(', ')[1].split(')')[0]
        return f"{inner_macro}({arg_count})*{rep_count}"
    except IndexError:
        print(f'Graph creation Warning: can\'t unpack rep_macro_name: {macro_name}')
        return macro_name


def show_macro_usage_pie_graph(macro_code_size: Dict[str, int], total_code_size: int,
                               min_main_thresh: float = 0.05, min_secondary_thresh: float = 0.02) -> None:
    main_thresh = min_main_thresh * total_code_size
    secondary_thresh = min_secondary_thresh * total_code_size
    first_level = {}
    second_level = collections.defaultdict(lambda: dict())
    for k, v in macro_code_size.items():
        if ' => ' not in k:
            if v < main_thresh:
                continue
            first_level[k] = v
        else:
            if v < secondary_thresh:
                continue
            k_split = k.split(' => ')
            if len(k_split) != 2:
                continue
            parent, name = k_split
            second_level[parent][name] = v

    chosen = []
    for k, v in sorted(first_level.items(), key=lambda x: x[1], reverse=True):
        k_name = clean_name_for_pie_graph(k)
        if len(second_level[k]) == 0:
            chosen.append((k_name, v))
        else:
            for k2, v2 in sorted(second_level[k].items(), key=lambda x: x[1], reverse=True):
                k2_name = clean_name_for_pie_graph(k2)
                chosen.append((f"{k_name} => {k2_name}", v2))
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
                   output_file: Path = None, show_statistics: bool = False, verbose: bool = False)\
        -> Tuple[List[Op], Dict[str, int], BoundaryAddressesList]:
    curr_address = [0]
    result_ops: List[Op] = []
    labels: Dict[str, int] = {}
    last_address_index = [0]
    label_places = {}
    boundary_addresses: BoundaryAddressesList = [(SegmentEntry.StartAddress, 0)]  # SegEntries
    stat_dict = collections.defaultdict(lambda: 0)

    resolve_macro_aux(w, '', [], macros, main_macro, [], {}, count(), stat_dict,
                      labels, result_ops, boundary_addresses, curr_address, last_address_index, label_places,
                      verbose)
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


def resolve_macro_aux(w: int, parent_name: str, curr_tree: List[str], macros: Dict[MacroName, Macro],
                      macro_name: MacroName, args: Iterable[Expr], rep_dict: Dict[str, Expr], dollar_count: count, macro_code_size: Dict[str, int],
                      labels: Dict[str, int], result_ops: List[Op], boundary_addresses: BoundaryAddressesList, curr_address: List[int], last_address_index, labels_code_positions: Dict[str, CodePosition],
                      verbose: bool = False, code_position: CodePosition = None)\
        -> None:
    init_curr_address = curr_address[0]

    if macro_name not in macros:
        if not code_position or None in (code_position.file, code_position.line):
            macro_resolve_error(curr_tree, f"macro {macro_name} isn't defined.")
        else:
            macro_resolve_error(curr_tree, f"macro {macro_name} isn't defined. Used in {code_position}.")

    full_name = (f"{parent_name} => " if parent_name else "") + str(macro_name)
    current_macro = macros[macro_name]

    id_dict = get_id_dictionary(current_macro, args, dollar_count, rep_dict, current_macro.namespace)

    for op in current_macro.ops:
        # macro-resolve
        if not isinstance(op, Op):
            macro_resolve_error(curr_tree, f"bad op (not of Op type)! type {type(op)}, str {str(op)}.")
        if verbose:
            print(op)
        op = deepcopy(op)
        eval_all(op, id_dict)
        id_swap(op, id_dict)
        if isinstance(op, MacroCall):
            resolve_macro_aux(w, full_name, curr_tree + [op.macro_trace_str()], macros, op.macro_name,
                              op.data, {}, dollar_count, macro_code_size,
                              labels, result_ops, boundary_addresses, curr_address, last_address_index,
                              labels_code_positions, verbose, code_position=op.code_position)
        elif op.type == OpType.Rep:
            eval_all(op, labels)
            n, i_name, macro_call = op.data
            if not n.is_int():
                macro_resolve_error(curr_tree, f'Rep used without a number "{str(n)}" '
                                               f'in {op.code_position}.')
            times = n.val
            if times == 0:
                continue
            if i_name in rep_dict:
                macro_resolve_error(curr_tree, f'Rep index {i_name} is declared twice; maybe an inner rep. '
                                               f'in {op.code_position}.')
            macro_name = macro_call.macro_name
            pseudo_macro_name = MacroName(new_label(dollar_count, f'rep_{times}_{macro_name}').val, 1)  # just moved outside (before) the for loop
            for i in range(times):
                rep_dict[i_name] = Expr(i)  # TODO - call the macro_name directly, and do deepcopy(op) beforehand.
                macros[pseudo_macro_name] = Macro([], [], [macro_call], current_macro.namespace, op.code_position)
                resolve_macro_aux(w, full_name, curr_tree + [op.rep_trace_str(i, times)], macros,
                                  pseudo_macro_name, [], rep_dict, dollar_count, macro_code_size,
                                  labels, result_ops, boundary_addresses, curr_address, last_address_index,
                                  labels_code_positions, verbose, code_position=op.code_position)
            if i_name in rep_dict:
                del rep_dict[i_name]
            else:
                macro_resolve_error(curr_tree, f'Rep is used but {i_name} index is gone; maybe also declared elsewhere.'
                                               f' in {op.code_position}.')

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
        elif op.type in {OpType.FlipJump, OpType.WordFlip}:
            curr_address[0] += 2*w
            eval_all(op, {'$': Expr(curr_address[0])})
            if verbose:
                print(f'op added: {str(op)}')
            result_ops.append(op)
        elif op.type == OpType.Label:
            label = op.data[0]
            if label in labels:
                other_position = labels_code_positions[label]
                macro_resolve_error(curr_tree, f'label declared twice - "{label}" on {op.code_position} '
                                               f'and {other_position}')
            if verbose:
                print(f'label added: "{label}" in {op.code_position}')
            labels[label] = Expr(curr_address[0])
            labels_code_positions[label] = op.code_position
        else:
            macro_resolve_error(curr_tree, f"Can't assemble this opcode - {str(op)}")

    if 1 <= len(curr_tree) <= 2:
        macro_code_size[full_name] += curr_address[0] - init_curr_address


def get_id_dictionary(current_macro: Macro, args: Iterable[Op], dollar_count: count, rep_dict: Dict[str, Expr], namespace: str):
    id_dict: Dict[str, Expr] = dict(zip(current_macro.params, args))
    for local_param in current_macro.local_params:
        id_dict[local_param] = new_label(dollar_count, local_param)
    for k in rep_dict:
        id_dict[k] = rep_dict[k]
    if namespace:
        for k in list(id_dict.keys()):
            id_dict[f'{namespace}.{k}'] = id_dict[k]
    return id_dict

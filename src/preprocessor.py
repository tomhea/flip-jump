import collections
from typing import Dict, List, Tuple, Iterable, Union, Deque

import plotly.graph_objects as go

from defs import main_macro, wflip_start_label, new_label, \
    SegmentEntry, Expr, FJPreprocessorException, \
    CodePosition, Macro, MacroName, BoundaryAddressesList, MacroCall, RepCall, FJExprException, \
    FlipJump, WordFlip, Label, Segment, Reserve, LastPhaseOp, macro_separator_string

CurrTree = Deque[Union[MacroCall, RepCall]]


def macro_resolve_error(curr_tree: CurrTree, msg='', *, orig_exception: BaseException = None) -> None:
    error_str = f"Macro Resolve Error" + (f':\n  {msg}' if msg else '.') + f'\nmacro call trace:\n'
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


def resolve_macros(w: int, macros: Dict[MacroName, Macro], show_statistics: bool = False)\
        -> Tuple[Deque[LastPhaseOp], Dict[str, Expr], BoundaryAddressesList]:
    curr_address = [0]
    result_ops: Deque[LastPhaseOp] = collections.deque()
    labels: Dict[str, Expr] = {}
    last_address_index = [0]
    boundary_addresses: BoundaryAddressesList = [(SegmentEntry.StartAddress, 0)]  # SegEntries
    stat_dict = collections.defaultdict(lambda: 0)

    resolve_macro_aux(w, '', collections.deque(), macros, main_macro, [], stat_dict,
                      labels, result_ops, boundary_addresses, curr_address, last_address_index, {})

    if show_statistics:
        show_macro_usage_pie_graph(dict(stat_dict), curr_address[0])

    boundary_addresses.append((SegmentEntry.WflipAddress, curr_address[0]))
    return result_ops, labels, boundary_addresses


def resolve_macro_aux(w: int, macro_path: str, curr_tree: CurrTree, macros: Dict[MacroName, Macro],
                      macro_name: MacroName, args: Iterable[Expr], macro_code_size: Dict[str, int],
                      labels: Dict[str, Expr], result_ops: Deque[LastPhaseOp], boundary_addresses: BoundaryAddressesList,
                      curr_address: List[int], last_address_index, labels_code_positions: Dict[str, CodePosition],
                      code_position: CodePosition = None)\
        -> None:
    init_curr_address = curr_address[0]

    if macro_name not in macros:
        macro_resolve_error(curr_tree, f"macro {macro_name} isn't defined. Used in {code_position}.")

    current_macro = macros[macro_name]

    id_dict = get_id_dictionary(current_macro, args, current_macro.namespace, macro_path)

    for op in current_macro.ops:
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
            curr_tree.append(op)
            resolve_macro_aux(w, next_macro_path, curr_tree, macros,
                              op.macro_name, op.arguments, macro_code_size,
                              labels, result_ops, boundary_addresses, curr_address, last_address_index,
                              labels_code_positions, code_position=op.code_position)
            curr_tree.pop()
        elif isinstance(op, RepCall):
            op = op.eval_new(id_dict)
            try:
                times = op.calculate_times(labels)
                if times == 0:
                    continue
                next_macro_path = (f"{macro_path}{macro_separator_string}" if macro_path else "") + \
                                  f"{op.code_position.short_str()}:rep{{}}:{op.macro_name}"
                for i in range(times):
                    curr_tree.append(op)
                    resolve_macro_aux(w, next_macro_path.format(i), curr_tree, macros,
                                      op.macro_name, op.calculate_arguments(i), macro_code_size,
                                      labels, result_ops, boundary_addresses, curr_address, last_address_index,
                                      labels_code_positions, code_position=op.code_position)
                    curr_tree.pop()
            except FJExprException as e:
                macro_resolve_error(curr_tree, f'rep {op.macro_name} failed.', orig_exception=e)
        elif isinstance(op, Segment):
            op = op.eval_new(id_dict)
            try:
                value = op.calculate_address(labels)
                if value % w != 0:
                    macro_resolve_error(curr_tree, f'segment ops must have a w-aligned address. In {op}.')
            except FJExprException as e:
                macro_resolve_error(curr_tree, f'segment failed.', orig_exception=e)

            boundary_addresses.append((SegmentEntry.WflipAddress, curr_address[0]))
            labels[f'{wflip_start_label}{last_address_index[0]}'] = Expr(curr_address[0])
            last_address_index[0] += 1

            curr_address[0] = value
            boundary_addresses.append((SegmentEntry.StartAddress, curr_address[0]))

            result_ops.append(op)
        elif isinstance(op, Reserve):
            op = op.eval_new(id_dict)
            try:
                value = op.calculate_reserved_bit_size(labels)
                if value % w != 0:
                    macro_resolve_error(curr_tree, f'reserve ops must have a w-aligned value. In {op}.')
            except FJExprException as e:
                macro_resolve_error(curr_tree, f'reserve failed.', orig_exception=e)

            curr_address[0] += value

            boundary_addresses.append((SegmentEntry.ReserveAddress, curr_address[0]))
            labels[f'{wflip_start_label}{last_address_index[0]}'] = Expr(curr_address[0])
            last_address_index[0] += 1

            result_ops.append(op)
        else:
            macro_resolve_error(curr_tree, f"Can't assemble this opcode - {str(op)}")

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

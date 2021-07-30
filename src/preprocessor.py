from itertools import count
from defs import *
from copy import deepcopy
import collections
import matplotlib.pyplot as plt
import plotly.graph_objects as go


def macro_resolve_error(curr_tree, msg=''):
    print()
    if msg:
        print(f"Macro Resolve Error:")
        print(f"  {msg}")
    else:
        print(f"Macro Resolve Error.")

    print(f"macro call trace:")
    for i, trace_str in enumerate(curr_tree):
        print(f'  {i}) {trace_str}')
    error(1)


def output_ops(ops, output_file):
    with open(output_file, 'w') as f:
        for op in ops:
            eval_all(op)
            if op.type == OpType.FlipJump:
                f.write(f'  {op.data[0]};{op.data[1]}\n')
            elif op.type == OpType.WordFlip:
                f.write(f'  wflip {op.data[0]}, {op.data[1]}, {op.data[2]}\n')
            elif op.type == OpType.Label:
                f.write(f'{op.data[0]}:\n')


def dict_pie_graph(d, total, min_main_thresh=0.05, min_secondary_thresh=0.02):
    main_thresh = min_main_thresh * total
    secondary_thresh = min_secondary_thresh * total
    first_level = {}
    second_level = collections.defaultdict(lambda: dict())
    for k, v in d.items():
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
        if len(second_level[k]) == 0:
            chosen.append((k, v))
        else:
            for k2, v2 in sorted(second_level[k].items(), key=lambda x: x[1], reverse=True):
                chosen.append((f"{k} => {k2}", v2))
                v -= v2
            if v >= secondary_thresh:
                chosen.append((f"{k} others", v))

    others = total - sum([v for l, v in chosen])
    chosen.append(('all others', others))

    fig = go.Figure(data=[go.Pie(labels=[l for l, v in chosen],
                                 values=[v for l, v in chosen],
                                 textinfo='label+percent'
                                 )])
    fig.show()

    # plt.pie(d.values(), labels=d.keys(), autopct='%1.2f%%')
    # plt.savefig(output_file)


def resolve_macros(w, macros, output_file=None, show_statistics=False, verbose=False):
    curr_address = [0]
    rem_ops = []
    labels = {}
    last_address_index = [0]
    label_places = {}
    boundary_addresses = [(SegEntry.StartAddress, 0)]  # SegEntries
    stat_dict = collections.defaultdict(lambda: 0)

    ops = resolve_macro_aux(w, '', [], macros, main_macro, [], {}, count(), stat_dict,
                            labels, rem_ops, boundary_addresses, curr_address, last_address_index, label_places,
                            verbose)
    if output_file:
        output_ops(ops, output_file)

    if show_statistics:
        dict_pie_graph(dict(stat_dict), curr_address[0])

    boundary_addresses.append((SegEntry.WflipAddress, curr_address[0]))
    return rem_ops, labels, boundary_addresses


def try_int(op, expr):
    if expr.is_int():
        return expr.val
    error(f"Can't resolve the following name: {expr.eval({}, op.file, op.line)} (in op={op}).")


def resolve_macro_aux(w, parent_name, curr_tree, macros, macro_name, args, rep_dict, dollar_count, stat_dict,
                      labels, rem_ops, boundary_addresses, curr_address, last_address_index, label_places,
                      verbose=False, file=None, line=None):
    commands = []
    init_curr_address = curr_address[0]
    this_curr_address = 0
    if macro_name not in macros:
        macro_name = f'{macro_name[0]}({macro_name[1]})'
        if None in (file, line):
            macro_resolve_error(curr_tree, f"macro {macro_name} isn't defined.")
        else:
            macro_resolve_error(curr_tree, f"macro {macro_name} isn't defined. Used in file {file} (line {line}).")
    full_name = (f"{parent_name} => " if parent_name else "") + macro_name[0] + (f"({macro_name[1]})" if macro_name[0] else "")
    (params, dollar_params), ops, (_, _, ns_name) = macros[macro_name]
    id_dict = dict(zip(params, args))
    for dp in dollar_params:
        id_dict[dp] = new_label(dollar_count, dp)
    for k in rep_dict:
        id_dict[k] = rep_dict[k]
    if ns_name:
        for k in list(id_dict.keys()):
            id_dict[f'{ns_name}.{k}'] = id_dict[k]

    for op in ops:
        # macro-resolve
        if type(op) is not Op:
            macro_resolve_error(curr_tree, f"bad op (not of Op type)! type {type(op)}, str {str(op)}.")
        if verbose:
            print(op)
        op = deepcopy(op)
        eval_all(op, id_dict)
        id_swap(op, id_dict)
        if op.type == OpType.Macro:
            commands += resolve_macro_aux(w, full_name, curr_tree+[op.macro_trace_str()], macros, op.data[0], list(op.data[1:]), {}, dollar_count, stat_dict,
                                          labels, rem_ops, boundary_addresses, curr_address, last_address_index, label_places,
                                          verbose, file=op.file, line=op.line)
        elif op.type == OpType.Rep:
            eval_all(op, labels)
            n, i_name, macro_call = op.data
            if not n.is_int():
                macro_resolve_error(curr_tree, f'Rep used without a number "{str(n)}" '
                                               f'in file {op.file} line {op.line}.')
            times = n.val
            if times == 0:
                continue
            if i_name in rep_dict:
                macro_resolve_error(curr_tree, f'Rep index {i_name} is declared twice; maybe an inner rep. '
                                               f'in file {op.file} line {op.line}.')
            pseudo_macro_name = (new_label(dollar_count).val, 1)  # just moved outside (before) the for loop
            for i in range(times):
                rep_dict[i_name] = Expr(i)  # TODO - call the macro_name directly, and do deepcopy(op) beforehand.
                macros[pseudo_macro_name] = (([], []), [macro_call], (op.file, op.line, ns_name))
                commands += resolve_macro_aux(w, full_name, curr_tree+[op.rep_trace_str(i, times)], macros, pseudo_macro_name, [], rep_dict, dollar_count, stat_dict,
                                              labels, rem_ops, boundary_addresses, curr_address, last_address_index, label_places,
                                              verbose, file=op.file, line=op.line)
            if i_name in rep_dict:
                del rep_dict[i_name]
            else:
                macro_resolve_error(curr_tree, f'Rep is used but {i_name} index is gone; maybe also declared elsewhere. '
                                               f'in file {op.file} line {op.line}.')

        # labels_resolve
        elif op.type == OpType.Segment:
            eval_all(op, labels)
            value = try_int(op, op.data[0])
            if value % w != 0:
                macro_resolve_error(curr_tree, f'segment ops must have a w-aligned address. In {op}.')

            boundary_addresses.append((SegEntry.WflipAddress, curr_address[0]))
            labels[f'{wflip_start_label}{last_address_index[0]}'] = Expr(curr_address[0])
            last_address_index[0] += 1

            this_curr_address += value - curr_address[0]
            curr_address[0] = value
            boundary_addresses.append((SegEntry.StartAddress, curr_address[0]))
            rem_ops.append(op)
        elif op.type == OpType.Reserve:
            eval_all(op, labels)
            value = try_int(op, op.data[0])
            if value % w != 0:
                macro_resolve_error(curr_tree, f'reserve ops must have a w-aligned value. In {op}.')

            this_curr_address += value
            curr_address[0] += value
            boundary_addresses.append((SegEntry.ReserveAddress, curr_address[0]))
            labels[f'{wflip_start_label}{last_address_index[0]}'] = Expr(curr_address[0])

            last_address_index[0] += 1
            rem_ops.append(op)
        elif op.type in {OpType.FlipJump, OpType.WordFlip}:
            this_curr_address += 2*w
            curr_address[0] += 2*w
            eval_all(op, {'$': Expr(curr_address[0])})
            if verbose:
                print(f'op added: {str(op)}')
            rem_ops.append(op)
        elif op.type == OpType.Label:
            label = op.data[0]
            if label in labels:
                other_file, other_line = label_places[label]
                macro_resolve_error(curr_tree, f'label declared twice - "{label}" on file {op.file} (line {op.line}) '
                                               f'and file {other_file} (line {other_line})')
            if verbose:
                print(f'label added: "{label}" in {op.file} line {op.line}')
            labels[label] = Expr(curr_address[0])
            label_places[label] = (op.file, op.line)
        else:
            macro_resolve_error(curr_tree, f"Can't assemble this opcode - {str(op)}")

    # if len(curr_tree) == 1:
    #     stat_dict[macro_name[0]] += curr_address[0] - init_curr_address
    # stat_dict[macro_name[0]] += this_curr_address
    if 1 <= len(curr_tree) <= 2:
        stat_dict[full_name] += curr_address[0] - init_curr_address
    return commands


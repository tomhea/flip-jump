from itertools import count
from defs import *
from copy import deepcopy


def output_ops(ops, output_file):
    with open(output_file, 'w') as f:
        for op in ops:
            eval_all(op)
            if op.type == OpType.FlipJump:
                f.write(f'  {op.data[0]};{op.data[1]}\n')
            elif op.type == OpType.WordFlip:
                f.write(f'  .wflip {op.data[0]} {op.data[1]}\n')
            elif op.type == OpType.Label:
                f.write(f'{op.data[0]}:\n')


def resolve_macros(w, macros, output_file=None, verbose=False):
    curr_address = [0]
    rem_ops = []
    labels = {}
    last_address_index = [0]
    label_places = {}
    boundary_addresses = [(SegEntry.StartAddress, 0)]  # SegEntries

    ops = resolve_macro_aux(w, macros, main_macro, [], {}, count(),
                            labels, rem_ops, boundary_addresses, curr_address, last_address_index, label_places,
                            verbose)
    if output_file:
        output_ops(ops, output_file)

    boundary_addresses.append((SegEntry.WflipAddress, curr_address[0]))
    return rem_ops, labels, boundary_addresses


def try_int(op, expr):
    if expr.is_int():
        return expr.val
    error(f"Can't resolve the following name: {expr.eval({}, op.file, op.line)} (in op={op}).")


def resolve_macro_aux(w, macros, macro_name, args, rep_dict, dollar_count,
                      labels, rem_ops, boundary_addresses, curr_address, last_address_index, label_places,
                      verbose=False, file=None, line=None):
    commands = []
    if macro_name not in macros:
        macro_name = f'{macro_name[0]}({macro_name[1]})'
        if None in (file, line):
            error(f"macro {macro_name} isn't defined.")
        else:
            error(f"macro {macro_name} isn't defined. Used in file {file} (line {line}).")
    (params, dollar_params), ops, _ = macros[macro_name]
    id_dict = dict(zip(params, args))
    for dp in dollar_params:
        id_dict[dp] = new_label(dollar_count, dp)
    for k in rep_dict:
        id_dict[k] = rep_dict[k]

    for op in ops:
        # macro-resolve
        if type(op) is not Op:
            error(type(op) + str(op) + '\n\n' + str(ops))
        if verbose:
            print(op)
        op = deepcopy(op)
        eval_all(op, id_dict)
        id_swap(op, id_dict)
        if op.type == OpType.Macro:
            commands += resolve_macro_aux(w, macros, op.data[0], list(op.data[1:]), {}, dollar_count,
                                          labels, rem_ops, boundary_addresses, curr_address, last_address_index, label_places,
                                          verbose, file=op.file, line=op.line)
        elif op.type == OpType.Rep:
            eval_all(op, labels)
            n, i_name, macro_call = op.data
            if not n.is_int():
                error(f'Rep used without a number "{str(n)}" in file {op.file} line {op.line}.')
            times = n.val
            if times == 0:
                continue
            if i_name in rep_dict:
                error(f'Rep index {i_name} is declared twice; maybe an inner rep. in file {op.file} line {op.line}.')
            pseudo_macro_name = (new_label(dollar_count).val, 1)  # just moved outside (before) the for loop
            for i in range(times):
                rep_dict[i_name] = Expr(i)  # TODO - call the macro_name directly, and do deepcopy(op) beforehand.
                macros[pseudo_macro_name] = (([], []), [macro_call], (op.file, op.line))
                commands += resolve_macro_aux(w, macros, pseudo_macro_name, [], rep_dict, dollar_count,
                                              labels, rem_ops, boundary_addresses, curr_address, last_address_index, label_places,
                                              verbose, file=op.file, line=op.line)
            if i_name in rep_dict:
                del rep_dict[i_name]
            else:
                error(f'Rep is used but {i_name} index is gone; maybe also declared elsewhere. in file {op.file} line {op.line}.')

        # labels_resolve
        elif op.type == OpType.Segment:
            eval_all(op, labels)
            value = try_int(op, op.data[0])
            if value % w != 0:
                error(f'.segment ops must have a w-aligned address. In {op}.')

            boundary_addresses.append((SegEntry.WflipAddress, curr_address[0]))
            labels[f'{wflip_start_label}{last_address_index[0]}'] = Expr(curr_address[0])
            last_address_index[0] += 1

            curr_address[0] = value
            boundary_addresses.append((SegEntry.StartAddress, curr_address[0]))
            rem_ops.append(op)
        elif op.type == OpType.Reserve:
            eval_all(op, labels)
            value = try_int(op, op.data[0])
            if value % w != 0:
                error(f'.reserve ops must have a w-aligned value. In {op}.')

            curr_address[0] += value
            boundary_addresses.append((SegEntry.ReserveAddress, curr_address[0]))
            labels[f'{wflip_start_label}{last_address_index[0]}'] = Expr(curr_address[0])

            last_address_index[0] += 1
            rem_ops.append(op)
        elif op.type in {OpType.FlipJump, OpType.WordFlip}:
            delta = 2 * w
            end_address = curr_address[0] + delta
            eval_all(op, {'$': Expr(end_address)})
            curr_address[0] = end_address
            if op.type == OpType.WordFlip:
                op.data += (Expr(end_address),)
            if verbose:
                print(f'op added: {str(op)}')
            rem_ops.append(op)
        elif op.type == OpType.Label:
            label = op.data[0]
            if label in labels:
                other_file, other_line = label_places[label]
                error(
                    f'label declared twice - "{label}" on file {op.file} (line {op.line}) and file {other_file} (line {other_line})')
            if verbose:
                print(f'label added: "{label}" in {op.file} line {op.line}')
            labels[label] = Expr(curr_address[0])
            label_places[label] = (op.file, op.line)
        else:
            error(f"Can't assemble this opcode - {str(op)}")

    return commands


def main():
    print('preprocessing')
    # for test_name in ('cat', 'ncat', 'mathbit', 'not', 'testbit', 'mathvec'):
    #     preprocess([f'tests/{test_name}.fj'], f'tests/compiled/{test_name}__no_macros.fj')


if __name__ == '__main__':
    main()

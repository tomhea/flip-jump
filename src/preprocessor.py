from itertools import count
from defs import *
from copy import deepcopy


def output_ops(ops, output_file):
    with open(output_file, 'w') as f:
        for op in ops:
            eval_all(op)
            if op.type == OpType.FlipJump:
                f.write(f'  {op.data[0]};{op.data[1]}\n')
            elif op.type == OpType.Label:
                f.write(f'{op.data[0]}:\n')
            elif op.type == OpType.BitSpecific:
                f.write(f'  [{op.data[0]}]{op.data[1]}\n')
            elif op.type == OpType.DDFlipBy:
                f.write(f'  ..flip_by {op.data[0]} {op.data[1]}\n')


def resolve_macros(macros, output_file=None, verbose=False):
    ops = resolve_macro_aux(macros, main_macro, [], {}, count(), verbose)
    if output_file:
        output_ops(ops, output_file)
    return ops


def resolve_macro_aux(macros, macro_name, args, rep_dict, dollar_count, verbose=False, file=None, line=None):
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
        if type(op) is not Op:
            error(type(op) + str(op) + '\n\n' + str(ops))
        if verbose:
            print(op)
        op = deepcopy(op)
        eval_all(op, id_dict)
        id_swap(op, id_dict)
        if op.type == OpType.Macro:
            commands += resolve_macro_aux(macros, op.data[0], list(op.data[1:]), {}, dollar_count, verbose, file=op.file, line=op.line)
        elif op.type == OpType.Rep:
            n, i_name, statements = op.data
            statements = list(statements)
            if not n.is_int():
                error(f'Rep used without a number "{str(n)}" in file {op.file} line {op.line}.')
            times = n.val
            if times == 0:
                continue
            if i_name in rep_dict:
                error(f'Rep index {i_name} is declared twice; maybe an inner rep. in file {op.file} line {op.line}.')
            pseudo_macro_name = (new_label(dollar_count).val, 1)  # just moved outside (before) the for loop
            for i in range(times):
                rep_dict[i_name] = Expr(i)
                macros[pseudo_macro_name] = (([], []), statements, (op.file, op.line))
                commands += resolve_macro_aux(macros, pseudo_macro_name, [], rep_dict, dollar_count, verbose, file=op.file, line=op.line)
            if i_name in rep_dict:
                del rep_dict[i_name]
            else:
                error(f'Rep is used but {i_name} index is gone; maybe also declared elsewhere. in file {op.file} line {op.line}.')
        else:
            commands.append(op)
    return commands


def main():
    print('preprocessing')
    # for test_name in ('cat', 'ncat', 'mathbit', 'not', 'testbit', 'mathvec'):
    #     preprocess([f'tests/{test_name}.fj'], f'tests/compiled/{test_name}__no_macros.fj')


if __name__ == '__main__':
    main()

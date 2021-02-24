from itertools import count
from defs import *


def printable_address(address):
    if address.index < 0:
        index = f'[0-{hex(0-address.index)[2:]}]'
    elif address.index > 0:
        index = f'[{hex(address.index)[2:]}]'
    else:
        index = ''

    if address.type == AddrType.ID:
        return address.base + index
    if address.type == AddrType.Number:
        return hex(address.base)[2:] + index

    if address.type == AddrType.SkipAfter:
        return f'>{address.base}{index}'
    if address.type == AddrType.SkipBefore:
        return f'<{address.base}{index}'

    error('not suppose to get here (1)')


def output_ops(ops, output_file):
    with open(output_file, 'w') as f:
        for op in ops:
            eval_all(op)
            if op.type == OpType.FlipJump:
                f.write(f'{op.data[0]};{op.data[1]}\n')
            elif op.type == OpType.Label:
                f.write(f'{op.data[0]}:\n')
            elif op.type == OpType.BitSpecific:
                f.write(f'{op.data[0]}#{op.data[1]}\n')
            elif op.type == OpType.DDPad:
                f.write(f'..pad {op.data[0]}\n')
            elif op.type == OpType.DDFlipBy:
                f.write(f'..flip_by {op.data[0]} {op.data[1]}\n')
            elif op.type == OpType.DDFlipByDbit:
                f.write(f'..flip_by_dbit {op.data[0]} {op.data[1]}\n')
            elif op.type == OpType.DDVar:
                f.write(f'..var {op.data[0]} {op.data[1]}\n')


def resolve_macros(macros, output_file=None, verbose=False):
    ops = resolve_macro_aux(macros, main_macro, [], count(), verbose)
    if output_file:
        output_ops(ops, output_file)
    return ops


def eval_all(op, id_dict={}):
    for expr in op.data:
        if type(expr) is Expr:
            expr.eval(id_dict, op.file, op.line)


def resolve_macro_aux(macros, macro_name, args, dollar_count, verbose=False):
    commands = []
    if macro_name not in macros:
        error(f"macro '{macro_name}' isn't defined.")
    (params, dollar_params), ops = macros[macro_name]
    id_dict = dict(zip(params + dollar_params, args + [new_label(dollar_count) for _ in dollar_params]))
    for op in ops:
        if type(op) is not Op:
            error(type(op) + str(op) + '\n\n' + str(ops))
        if verbose:
            print(op)
        eval_all(op, id_dict=id_dict)
        if op.type == OpType.Macro:
            commands += resolve_macro_aux(macros, op.data[0], list(op.data[1:]), dollar_count, verbose)
        elif op.type == OpType.Rep:
            n, i_name, statements = op.data
            statements = list(statements)
            if not n.is_int():
                error(f'Rep used without a number "{str(n)}" in file {op.file} line {op.line}.')
            times = n.val
            for i in range(times):
                pseudo_macro_name = (new_label(dollar_count).base, 1)   # TODO move outside (before) the for loop
                macros[pseudo_macro_name] = (([i_name], []), statements)
                commands += resolve_macro_aux(macros, pseudo_macro_name, [Expr(i)], dollar_count, verbose)
        elif op.type == OpType.DDOutput:
            c = op.data[0]
            if not c.is_int():
                error(f'..output used without a number "{str(c)}" in file {op.file} line {op.line}.')
            num = c.val & 0xff
            for i in range(8):
                commands.append(Op(OpType.FlipJump, (Expr(Expr('IO'), add, (num >> i) & 1), next_address), op.file, op.line))
        else:
            commands.append(op)
    return commands


def main():
    print('preprocessing')
    # for test_name in ('cat', 'ncat', 'mathbit', 'not', 'testbit', 'mathvec'):
    #     preprocess([f'tests/{test_name}.fj'], f'tests/compiled/{test_name}__no_macros.fj')


if __name__ == '__main__':
    main()

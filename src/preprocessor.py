from itertools import count
from defs import *


w = 64


def printable_address(address, start_label):
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

    error('not suppose to ge here (1)')

    # using_line_labels
    if address.type == AddrType.SkipAfter:
        return f'{start_label}[{hex((2 + address.base)*w)[2:]}]{index}'
    if address.type == AddrType.SkipBefore:
        return f'{start_label}[0-{hex(address.base)[2:]*w}]{index}'


def output_ops(ops, output_file):
    counter = count()
    with open(output_file, 'w') as f:
        for op in ops:
            curr_label = f'__line_label{next(counter)}'
            # f.write(f'({curr_label})\n')
            if op.type == OpType.FlipJump:
                f.write(f'{printable_address(op.data[0], curr_label)};{printable_address(op.data[1], curr_label)}\n')
            elif op.type == OpType.Label:
                f.write(f'({op.data[0]})\n')
            elif op.type == OpType.BitSpecific:
                f.write(f'{hex(op.data[0])[2:]}#{printable_address(op.data[1], curr_label)}\n')
            elif op.type == OpType.DDPad:
                f.write(f'..pad {hex(op.data[0])[2:]}\n')
            elif op.type == OpType.DDFlipBy:
                f.write(f'..flip_by {printable_address(op.data[0], curr_label)} {printable_address(op.data[1], curr_label)}\n')
            elif op.type == OpType.DDFlipByDbit:
                f.write(f'..flip_by_dbit {printable_address(op.data[0], curr_label)} {printable_address(op.data[1], curr_label)}\n')
            elif op.type == OpType.DDVar:
                f.write(f'..var {hex(op.data[0])[2:]} {printable_address(op.data[1], curr_label)}\n')


def resolve_macros(macros, output_file=None, verbose=False):
    ops = resolve_macro_aux(macros, main_macro, [], count(), verbose)
    if output_file:
        output_ops(ops, output_file)
    return ops


def fix_labels(op, params, args):
    new_data = []
    for datum in op.data:
        if type(datum) is Address and datum.type == AddrType.ID and datum.base in params:
            arg_address = args[params.index(datum.base)]
            new_data.append(Address(arg_address.type, arg_address.base, datum.index + arg_address.index))
        elif op.type == OpType.Rep and type(datum) is list:
            res = [Op(_op.type, fix_labels(_op, params, args), _op.file, _op.line) for _op in datum]
            new_data.append(res)
        elif op.type == OpType.Label and datum in params:
            new_data.append(args[params.index(datum)].base)
        else:
            new_data.append(datum)
    return new_data


def resolve_macro_aux(macros, macro_name, args, dollar_count, verbose=False):
    commands = []
    if macro_name not in macros:
        error(f"macro '{macro_name}' isn't defined.")
    (params, dollar_params), ops = macros[macro_name]
    params += dollar_params
    args += [new_label(dollar_count) for _ in dollar_params]    # dollar_args
    for op in ops:
        if type(op) is not Op:
            error(type(op) + str(op) + '\n\n' + str(ops))
        if verbose:
            print(op)
        fixed_data = fix_labels(op, params, args)
        op = Op(op.type, fixed_data, op.file, op.line)
        if op.type == OpType.Macro:
            commands += resolve_macro_aux(macros, op.data[0], list(op.data[1:]), dollar_count, verbose)
        elif op.type == OpType.Rep:
            n, i_name, statements = op.data
            statements = list(statements)
            if n.type != AddrType.Number:
                error(f'Rep used without a number "{n.base}" in file {op.file} line {op.line}.')
            times = n.base + n.index
            for i in range(times):
                pseudo_macro_name = (new_label(dollar_count).base, 1)
                macros[pseudo_macro_name] = (([i_name], []), statements)
                commands += resolve_macro_aux(macros, pseudo_macro_name, [i], dollar_count, verbose)
        elif op.type == OpType.DDOutput:
            num = op.data[0]
            io_base = (AddrType.ID, 'IO')
            for i in range(8):
                commands.append(Op(OpType.FlipJump, (Address(*io_base, (num >> i) & 1), next_address), op.file, op.line))
        else:
            commands.append(op)
    return commands


def main():
    print('preprocessing')
    # for test_name in ('cat', 'ncat', 'mathbit', 'not', 'testbit', 'mathvec'):
    #     preprocess([f'tests/{test_name}.fj'], f'tests/compiled/{test_name}__no_macros.fj')


if __name__ == '__main__':
    main()

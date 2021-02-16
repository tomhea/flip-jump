import re
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

    if address.base_type == AddrType.ID:
        return address.base + index
    if address.base_type == AddrType.Number:
        return hex(address.base)[2:] + index
    if address.base_type == AddrType.SkipAfter:
        return f'{start_label}[{hex((2 + address.base)*w)[2:]}]{index}'
    if address.base_type == AddrType.SkipBefore:
        return f'{start_label}[0-{hex(address.base)[2:]*w}]{index}'


def output_ops(ops, output_file):
    counter = count()
    with open(output_file, 'w') as f:
        for op in ops:
            curr_label = f'__line_label{next(counter)}'
            f.write(f'({curr_label})\n')
            if op.op_type == OpType.FlipJump:
                f.write(f'{printable_address(op.data[0], curr_label)};{printable_address(op.data[1], curr_label)}\n')
            elif op.op_type == OpType.Label:
                f.write(f'({op.data[0]})\n')
            elif op.op_type == OpType.BitSpecific:
                f.write(f'{hex(op.data[0])[2:]}#{printable_address(op.data[1], curr_label)}\n')
            elif op.op_type == OpType.DDPad:
                f.write(f'..pad {hex(op.data[0])[2:]}\n')
            elif op.op_type == OpType.DDFlipBy:
                f.write(f'..flip_by {printable_address(op.data[0], curr_label)} {printable_address(op.data[1], curr_label)}\n')
            elif op.op_type == OpType.DDFlipByDbit:
                f.write(f'..flip_by_dbit {printable_address(op.data[0], curr_label)} {printable_address(op.data[1], curr_label)}\n')
            elif op.op_type == OpType.DDVar:
                f.write(f'..var {hex(op.data[0])[2:]} {printable_address(op.data[1], curr_label)}\n')


def resolve_macros(macros, output_file=None):
    ops = resolve_macro_aux(macros, main_macro, [], count())
    if output_file:
        output_ops(ops, output_file)
    return ops


def fix_labels(op, params, args):
    new_data = []
    print(op, op.data, new_data)

    for datum in op.data:
        if type(datum) is Address and datum.base_type == AddrType.ID and datum.base in params:
            arg_address = args[params.index(datum.base)]
            new_data.append(Address((arg_address.base_type, arg_address.base), datum.index + arg_address.index))
        elif op.op_type == OpType.Rep and type(datum) is list:
            new_data.append(fix_labels(_op, params, args) for _op in datum)
        elif op.op_type == OpType.Label and datum in params:
            new_data.append(args[params.index(datum)].base)
        else:
            new_data.append(datum)
    print(op, op.data, new_data)
    return new_data


def resolve_macro_aux(macros, macro_name, args, dollar_count):
    commands = []
    if macro_name not in macros:
        error(f"macro '{macro_name}' isn't defined.")
    (params, dollar_params), ops = macros[macro_name]
    params += dollar_params
    args += [new_label(dollar_count) for _ in dollar_params]    # dollar_args
    for op in ops:
        old_data = op.data
        op.data = fix_labels(op, params, args)
        if op.op_type == OpType.Macro:
            commands += resolve_macro_aux(macros, op.data[0], list(op.data[1:]), dollar_count)
        elif op.op_type == OpType.Rep:
            n, i_name, statements = op.data
            if n.base_type != AddrType.Number:
                error(f"Rep used without a number ({n.base})")
            times = n.base + n.index
            for i in range(times):
                pseudo_macro_name = (new_label(dollar_count).base, 1)
                macros[pseudo_macro_name] = (([i_name], []), statements)
                commands += resolve_macro_aux(macros, pseudo_macro_name, [i], dollar_count)
        elif op.op_type == OpType.DDOutput:
            num = op.data[0]
            io_base = (AddrType.ID, 'IO')
            for i in range(8):
                commands.append(Op(OpType.FlipJump, (Address(io_base, (num >> i) & 1), next_address), op.file, op.line))
        else:
            commands.append(op)
        op.data = old_data
    return commands


# def resolve_macro_aux(macros, defs, macro_name, args, dollar_count):
#     commands = []
#     if macro_name not in macros:
#         error(f"macro '{macro_name}' isn't defined.")
#     params, ops = macros[macro_name]
#     for op in ops:
#         op = re.sub(r'\$', lambda x: f'{next(dollar_count)}', op)    # handle '$' => next number
#         for par, arg in zip(params, args):
#             op = re.sub(fr'\b{par}\b', arg, op)                     # replace parameters with arguments
#         for def_name in defs:
#             op = re.sub(fr'\b{def_name}\b', defs[def_name], op)     # replace defined with their values
#
#         if op.startswith('.') and not op.startswith('..'):
#             uops = op[1:].split()
#             name, new_args = uops[0], uops[1:]
#             commands += resolve_macro_aux(macros, defs, (name, len(new_args)), new_args, dollar_count)
#         else:
#             commands.append(op)
#     return commands


# def first_pass(code):
#     last_def_name = main_macro
#     macros = {last_def_name: ([], []), defs_macro: ([], [])}
#
#     for op in code:
#         if op.startswith('.def '):
#             uops = op.split()
#             args = uops[2:]
#             last_def_name = (uops[1], len(args))
#             macros[last_def_name] = (args, [])
#         elif op == '.defs':
#             last_def_name = defs_macro
#         elif op == '.end':
#             last_def_name = main_macro
#         else:
#             macro_call = (re.match(r'\.\b', op) or re.search(r'\s\.\b', op)) and op.count('.') == 1
#             double_dot_macro = (re.match(r'\.\.\b', op) or re.search(r'\s\.\.\b', op)) and op.count('.') == 2
#             regular_op = '.' not in op
#             if not regular_op and not macro_call and not double_dot_macro:
#                 error(f'Bad dot in line: {op}')
#             macros[last_def_name][1].append(op)
#
#     defs = dict([exp.replace(' ', '').split('=') for exp in macros.pop(defs_macro)[1]])
#     return macros, defs


# def preprocess(macros, output_file, stl_type=64):
#     if stl_type:
#         input_files = stl(stl_type) + input_files
#
#     macros = first_pass(code)
#     commands = resolve_main_macro(macros)
#
#     open(output_file, 'w').write('\n'.join(commands))


def main():
    print('preprocessing')
    # for test_name in ('cat', 'ncat', 'mathbit', 'not', 'testbit', 'mathvec'):
    #     preprocess([f'tests/{test_name}.fj'], f'tests/compiled/{test_name}__no_macros.fj')


if __name__ == '__main__':
    main()

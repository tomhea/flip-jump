import re
from itertools import count

main_macro = ('.__M_a_i_n__', 0)
defs_macro = ('.__D_e_f_s__', 0)


def resolve_main_macro(macros, defs):
    return resolve_macro_aux(macros, defs, main_macro, [], count())


def resolve_macro_aux(macros, defs, macro_name, args, dollar_count):
    commands = []
    params, ops = macros[macro_name]
    for op in ops:
        op = re.sub(r'\$', lambda x: f'{next(dollar_count)}', op)    # handle '$' => next number
        for par, arg in zip(params, args):
            op = re.sub(fr'\b{par}\b', arg, op)                     # replace parameters with arguments
        for def_name in defs:
            op = re.sub(fr'\b{def_name}\b', defs[def_name], op)     # replace defined with their values

        if op.startswith('.') and not op.startswith('..'):
            uops = op[1:].split()
            name, new_args = uops[0], uops[1:]
            commands += resolve_macro_aux(macros, defs, (name, len(new_args)), new_args, dollar_count)
        else:
            commands.append(op)
    return commands


def first_pass(code):
    last_def_name = main_macro
    macros = {last_def_name: ([], []), defs_macro: ([], [])}

    for op in code:
        if op.startswith('.def '):
            uops = op.split()
            args = uops[2:]
            last_def_name = (uops[1], len(args))
            macros[last_def_name] = (args, [])
        elif op == '.defs':
            last_def_name = defs_macro
        elif op == '.end':
            last_def_name = main_macro
        else:
            macros[last_def_name][1].append(op)

    defs = dict([exp.replace(' ', '').split('=') for exp in macros.pop(defs_macro)[1]])
    return macros, defs


def preprocess(input_files, output_file, stl=64):
    if stl:
        input_files += [f'stl/{name}.fjm' for name in ('bitlib', 'veclib', f'lib{stl}')]

    code = [' '.join(line.split('//', 1)[0].rsplit(':', 1)[-1].split()) for input_file in input_files for line in open(input_file, 'r')]
    code = [op for op in code if op]
    macros, defs = first_pass(code)
    commands = resolve_main_macro(macros, defs)
    # print('\n'.join(f'{str(m)}:  {str(macros[m])}' for m in macros))
    # print('\n'.join(f'{str(c)}' for c in commands))

    open(output_file, 'w').write('\n'.join(commands))


def main():
    print('preprocessing')
    for test_name in ('cat', 'ncat', 'mathbit', 'not', 'testbit', 'mathvec'):
        preprocess([f'tests/{test_name}.fjm'], f'tests/{test_name}.fj')


if __name__ == '__main__':
    main()

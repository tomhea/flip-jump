# class Runner:
#     def __init__(self, program_file, width):
#         self.mem_bit_size = width
#         self.mem = []
#         self.ip = 0
#         with open(program_file, 'rb') as f:
#             data = f.read(width // 8)
#             while data:
#                 self.mem.append(int.from_bytes(data, 'little'))
#                 data = f.read(width // 8)
#
#         # in/out (every 8 bits are interpreted as an ascii char)
#         self.input_buffer = ''
#         self.output_buffer = ''
#
#     def exec_one(self):
#         x = self.mem[self.ip]

from numbers import Number

MainMacro = '.Main'


# TODO: change program to resolve the MainMacro macro recursively (output every known command).
#   Every child will inherit the names from his father (handle $s).
#   Should recursively eliminate all macro commands, but the .. (double-dot) ones.


def resolve_macro_dict_tree(solved_counter, dict):
    something_resolved = True
    while something_resolved:
        something_resolved = False
        for k in dict:
            if all(isinstance(son, Number) for son in dict[k][1:]):
                dict[solved_counter] = dict[k]
                pass
            else:
                for son in dict[k][1:]:
                    if not isinstance(son, Number):
                        def_name, args = son
                        if isinstance(dict[def_name], Number):
                            kids_nums = dict[dict[def_name]]

                            # TODO


    pass


TEMP = 0x300
# each memory bit mem[i] will be saved in the larger form at mem[(1<<31) + (i<<6)]


def get_all_defs(code):
    solved_counter = 0
    last_def_name = MainMacro
    dict = {last_def_name: [[]]}

    for op in code:
        if op.startswith('.def '):
            _, last_def_name, args = op.split(maxsplit=2)
            dict[last_def_name] = [args.split()]
        elif op == '.end':
            last_def_name = MainMacro
        else:
            if op.startswith('..') or op.replace('.', '') == op:
                dict[solved_counter] = op
                dict[last_def_name].append(solved_counter)
                solved_counter += 1
            else:
                def_name, args = op.split(maxsplit=1)
                dict[last_def_name].append((def_name, args.split()))
    return solved_counter, dict


def main(program_file):
    code = [' '.join(line.split('//', 1)[0].rsplit(':', 1)[-1].split()) for line in open(program_file, 'r').readlines()]
    code = [op for op in code if op]
    solved_counter, dict = get_all_defs(code)
    resolve_macro_dict_tree(solved_counter, dict)
    print(dict)
    print(code)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main('lib64.fjm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

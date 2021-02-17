import blm
from preprocessor import resolve_macros
from tempfile import mkstemp
import os
import re
from operator import mul, add, sub, floordiv
from defs import *
from parser import parse_macro_tree


class CommandType(Enum):
    FlipSCJump = 0      # lambda w,f,j  : 2*w
    HashTagBits = 1     # lambda w,n,b  : int(n, 16)
    DDotPad = 2         # lambda w,n    : w*int(n, 16)
    DDotFlipBy = 3      # lambda w,to,by: w*w
    DDotFlipByDBit = 4  # lambda w,to,by: w*(w-w.bit_length())
    DDotVar = 5
    DDotOutput = 6


double_dot_commands = {'pad': (CommandType.DDotPad, 1),
                       'flip_by': (CommandType.DDotFlipBy, 2),
                       'flip_by_dbit': (CommandType.DDotFlipByDBit, 2),
                       'var': (CommandType.DDotVar, 2),
                       'output': (CommandType.DDotOutput, 1)}


def handle_front_labels(line, labels, bit_address):
    line = line.strip()
    while line.startswith('('):
        end = line.find(')')
        label = line[1:end].strip()
        if not re.match(r'\w+$', label):
            error(f'bad label name: ({label})')
        if label in labels:
            error(f'label ({label}) is declared twice!')
        labels[label] = bit_address
        line = line[end+1:].strip()
    return line


def first_pass(code, bit_width=64):     # labels addresses, remove (label) defs, implied ';'
    bit_address = 0
    labels = {}
    next_code = []

    for line in code:
        line = handle_front_labels(line, labels, bit_address)
        non_labels_line = re.sub(r'\([^)(]*\)', '', line)

        if not non_labels_line:
            if line:
                error('bad labels line')
        elif '#' in non_labels_line:
            res = re.match(r'[0-9A-Fa-f]+#[0-9A-Fa-f]+', line)
            if not res:
                error(f'bad line with # (no n#b in opcode): {line}')

            curr_code = res.group()
            n, b = curr_code.split('#')
            bit_address += smart_int16(n)
            if handle_front_labels(line[len(curr_code):], labels, bit_address):
                error('bad line with # (forbidden actions after the main n#b)')
            next_code.append((CommandType.HashTagBits, (n, b)))

        elif non_labels_line.startswith('..'):
            uops = non_labels_line[2:].split()
            name, args = uops[0], uops[1:]
            if name not in double_dot_commands:
                error(f'bad line with .. (not such macro ..{name})')
            command_type, num_args = double_dot_commands[name]
            if num_args != len(args):
                error(f'bad line with .. (..{name} takes {num_args} arguments, not {len(args)})')

            if command_type == CommandType.DDotPad:
                x = smart_int16(args[0]) * bit_width
                filled_bits = (-bit_address) % x
                if filled_bits:
                    next_code.append((CommandType.HashTagBits, (hex(filled_bits)[2:], 0)))
                    bit_address += filled_bits
            elif command_type == CommandType.DDotFlipBy:
                bit_address += 2 * bit_width
                next_code.append((CommandType.DDotFlipBy, args + [bit_address]))
            elif command_type == CommandType.DDotFlipByDBit:
                bit_address += 2 * bit_width
                next_code.append((CommandType.DDotFlipByDBit, args + [bit_address]))
            elif command_type == CommandType.DDotVar:
                bit_address += 2 * bit_width * smart_int16(args[0])
                next_code.append((CommandType.DDotVar, args))
            elif command_type == CommandType.DDotOutput:
                output = smart_int16(args[0]) & 0xff
                for i in range(8):
                    bit_address += 2 * bit_width
                    next_code.append((CommandType.FlipSCJump, (f'IO[{(output >> i) & 1}]', bit_address)))
            else:
                error("bad '..' opcode")

            if line.find('(') >= 0:
                leftovers = handle_front_labels(line[line.find('('):], labels, bit_address)
                if leftovers:
                    error(f'bad line with .. (forbidden actions after the macro and arguments): {leftovers}')

        else:
            if ';' not in non_labels_line:  # implicit ;
                line += ';'
            line = re.sub(r'\s', '', line)
            re_query = r'\w+(\[\w+([\*\+\-\/]\w+)?\])*'

            uops = line.split(';')
            if len(uops) != 2:
                error("can't have more then 1 ';' in a line")
            f, j = uops

            bit_address += bit_width
            if not f:
                f = 'temp'
            else:
                res = re.match(re_query, f)
                if not res:
                    error('bad flipping address.')
                old_f = f
                f = res.group()
                if handle_front_labels(old_f[len(f):], labels, bit_address):
                    error('bad line with ; (forbidden actions after the flipping address)')

            j = handle_front_labels(j, labels, bit_address)
            bit_address += bit_width
            if not j:
                j = hex(bit_address)[2:]
            else:
                res = re.match(re_query, j)
                if not res:
                    error('bad jumping address.')
                old_j = j
                j = res.group()
                if handle_front_labels(old_j[len(j):], labels, bit_address):
                    error('bad line with ; (forbidden actions after the jumping address)')

            next_code.append((CommandType.FlipSCJump, (f, j)))

    return labels, next_code, bit_address


def arg_to_int_address(arg, labels):
    if type(arg) is int:
        return arg

    address = 0
    base_address = re.match(r'\w+', arg)
    if not base_address:
        error(f'bad characters in base address in: {arg}')
    base_address = base_address.group()
    if not base_address:
        address = 0
    elif re.match(r'[0-9A-Fa-f]+$', base_address):
        address = smart_int16(base_address)
    else:
        if base_address in labels:
            address = labels[base_address]
        else:
            error(f'base address label not found: {arg}')

    arg = re.sub(r'\s', '', arg[len(base_address):])
    single_brackets = re.findall(r'\[[0-9A-Fa-f]+]', arg)
    binary_op_brackets = re.findall(r'\[[0-9A-Fa-f]+[*+\-/][0-9A-Fa-f]+]', arg)
    if len(''.join(single_brackets + binary_op_brackets)) != len(arg):
        error(f'bad actions between the brackets in: {base_address + arg}')

    for bracket in single_brackets:
        if bracket not in arg:
            error(f'weird bracket found: {bracket} in: {base_address + arg}')
        address += smart_int16(bracket[1:-1])

    for bracket in binary_op_brackets:
        if bracket not in arg:
            error(f'weird bracket found: {bracket} in: {base_address + arg}')
        bracket = bracket[1:-1]
        binary_op = re.sub(r'[0-9A-Fa-f]', '', bracket)
        x, y = (smart_int16(v) for v in bracket.split(binary_op))
        address += {'*': mul, '+': add, '-': sub, '/': floordiv}[binary_op](x, y)

    return address


def lsb_first_bin_array(int_value, bit_size):
    return [int(c) for c in bin(int_value)[2:].zfill(bit_size)[-bit_size:]][::-1]


def write_flip_jump(data, f, j, bit_width):
    data += lsb_first_bin_array(f, bit_width)
    data += lsb_first_bin_array(j, bit_width)


def second_pass(writer, labels, code, bit_width, last_address):
    data = []
    for command_type, args in code:
        args = [arg_to_int_address(arg, labels) for arg in args]
        if command_type == CommandType.FlipSCJump:
            f, j = args
            write_flip_jump(data, f, j, bit_width)
        elif command_type == CommandType.HashTagBits:
            n, b = args
            data += lsb_first_bin_array(b, n)
        elif command_type == CommandType.DDotPad:
            error('..pad should not be handled at second pass level')
        elif command_type == CommandType.DDotVar:
            n, v = args
            temp_address = labels['temp']
            for i in range(n):
                write_flip_jump(data, temp_address, 2*bit_width if v & (1 << i) else 0, bit_width)
        elif command_type in (CommandType.DDotFlipBy, CommandType.DDotFlipByDBit):
            to_address, by_address, return_address = args
            temp_address = labels['temp']

            first_bit = 0 if command_type == CommandType.DDotFlipBy else bit_width.bit_length()+1
            flip_bits = [i for i in range(first_bit, bit_width) if by_address & (1 << i)]

            if len(flip_bits) <= 1:
                write_flip_jump(data, to_address + flip_bits[0] if flip_bits else temp_address, return_address, bit_width)
            else:
                write_flip_jump(data, to_address + flip_bits[0], last_address, bit_width)
                next = last_address
                for bit in flip_bits[1:-1]:
                    next += 2*bit_width
                    code.append((CommandType.FlipSCJump, (to_address + bit, next)))
                last_address = next + 2 * bit_width
                code.append((CommandType.FlipSCJump, (to_address + flip_bits[-1], return_address)))

        else:
            assert False

    writer.add_simple_sector_with_data(0, data)


def assemble(input_file, output_file, bit_width):
    writer = blm.Writer(bit_width)
    code = [' '.join(line.split('//', 1)[0].rsplit(':', 1)[-1].split()) for line in open(input_file, 'r')]
    code = [op for op in code if op]
    labels, code, last_address = first_pass(code, bit_width)

    second_pass(writer, labels, code, bit_width, last_address)

    writer.write_to_file(output_file)


def full_assemble(input_files, output_file, preprocessed_file=None, bit_width=64, use_stl=True, verbose=False):
    temp_preprocessed_file, temp_fd = False, 0
    if preprocessed_file is None:
        temp_fd, preprocessed_file = mkstemp()
        temp_preprocessed_file = True

    if use_stl:
        input_files = stl(bit_width) + input_files
    macros = parse_macro_tree(input_files)
    ops = resolve_macros(macros, output_file=preprocessed_file)
    assemble(preprocessed_file, output_file, bit_width)

    if temp_preprocessed_file:
        os.close(temp_fd)


def main():
    print('assembling')
    for test_name in ('cat',):#, 'ncat', 'mathbit', 'not', 'testbit', 'mathvec'):
        full_assemble([f'tests/{test_name}.fj'], f'tests/compiled/{test_name}.blm',
                      preprocessed_file=f'tests/compiled/{test_name}__no_macros.fj')


if __name__ == '__main__':
    main()

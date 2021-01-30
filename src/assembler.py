import fjc
from preprocessor import preprocess
from tempfile import mkstemp
import os
import re
from enum import Enum


def error(msg):     # TODO: print file and line number too (should be transferred via extra temp file!)
    print(f'\nERROR: {msg}\n')
    exit(1)


class CommandType(Enum):
    FlipSCJump = 0      # lambda w,f,j  : 2*w
    HashTagBits = 1     # lambda w,n,b  : int(n, 16)
    DDotPad = 2         # lambda w,n    : w*int(n, 16)
    DDotFlipBy = 3      # lambda w,to,by: w*w
    DDotFlipByDBit = 4  # lambda w,to,by: w*(w-w.bit_length())


double_dot_commands = {'pad': (CommandType.DDotPad, 1),
                       'flip_by': (CommandType.DDotFlipBy, 2),
                       'flip_by_dbit': (CommandType.DDotFlipByDBit, 2)}


def handle_front_labels(line, labels, bit_address):
    line = line.strip()
    while line.startswith('('):
        end = line.find(')')
        label = line[1:end]
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
        non_labels_line = re.sub(r'\([^\)\(]*\)', '', line)

        if not non_labels_line:
            if line:
                error('bad labels line')
        elif '#' in non_labels_line:
            res = re.search(r'[0-9A-Fa-f]+#[0-9A-Fa-f]+', line)
            if not res:
                error('bad line with # (no n#b in opcode)')

            curr_code = res.group()
            n, b = curr_code.split('#')
            bit_address += int(n, 16)
            if handle_front_labels(line[len(curr_code):], labels, bit_address):
                error('bad line with # (forbidden actions after the main n#b)')
            next_code.append((CommandType.HashTagBits, (n, b)))

            pass
        elif non_labels_line.startswith('..'):
            uops = non_labels_line[2:].split()
            name, args = uops[0], uops[1:]
            if name not in double_dot_commands:
                error(f'bad line with .. (not such macro ..{name})')
            command_type, num_args = double_dot_commands[name]
            if num_args != len(args):
                error(f'bad line with .. (..{name} takes {num_args} arguments, not {len(args)})')

            if command_type == CommandType.DDotPad:
                x = int(args[0], 16) * bit_width
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
            else:
                assert False
            if line.find('(') >= 0:
                leftovers = handle_front_labels(line + line.find('('), labels, bit_address)
                if leftovers:
                    error(f'bad line with .. (forbidden actions after the macro and arguments): {leftovers}')

        else:
            if ';' not in non_labels_line:
                line += ';'
            middle_bit_address = bit_address + bit_width
            next_bit_address = bit_address + 2 * bit_width
            re_query = r'\w+(\[[0-9A-Fa-f]+(\*[0-9A-Fa-f]+)?])*'

            uops = line.split(';')
            if len(uops) != 2:
                error("can't have more then 1 ';' in a line")
            f, j = uops

            bit_address = middle_bit_address
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
            bit_address = next_bit_address
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

# class CommandType(Enum):
#     FlipSCJump = 0      # lambda w,f,j  : 2*w
#     HashTagBits = 1     # lambda w,n,b  : int(n, 16)
#     DDotPad = 2         # lambda w,n    : w*int(n, 16)
#     DDotFlipBy = 3      # lambda w,to,by: w*w
#     DDotFlipByDBit = 4  # lambda w,to,by: w*(w-w.bit_length())


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
        address = int(base_address, 16)
    else:
        if base_address in labels:
            address = labels[base_address]
        else:
            error(f'base address label not found: {arg}')

    arg = arg[len(base_address):]

    single_brackets = re.findall(r'\[[0-9A-Fa-f]+\]', arg)
    multiplication_brackets = re.findall(r'\[[0-9A-Fa-f]+\*[0-9A-Fa-f]+\]', arg)
    if len(''.join(single_brackets + multiplication_brackets)) != len(arg):
        error(f'bad actions between the brackets in: {base_address + arg}')

    for bracket in single_brackets:
        if bracket not in arg:
            error(f'weird bracket found: {bracket} in: {base_address + arg}')
        address += int(bracket[1:-1], 16)

    for bracket in multiplication_brackets:
        if bracket not in arg:
            error(f'weird bracket found: {bracket} in: {base_address + arg}')
        x, y = (int(v, 16) for v in bracket[1:-1].split('*'))
        address += x * y

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
            n, b = (int(arg, 16) for arg in args)
            data += [int(c) for c in bin(b)[2:].zfill(n)[-n:]][::-1]
        elif command_type == CommandType.DDotPad:
            error('..pad should not be handled at second pass level')
        elif command_type in (CommandType.DDotFlipBy, CommandType.DDotFlipByDBit):
            # should take w F;next ops.
            # can be improved to b-1 times F;next, one time F;end,
            # and w-b times temp;next (for b - number of 1's in by_address bit representation)

            to_address, by_address, return_address = args
            temp_address = labels['temp']
            # next = start_address

            first_bit = 0 if command_type == CommandType.DDotFlipBy else bit_width.bit_length()
            flip_bits = [i for i in range(first_bit, bit_width) if by_address & (1 << i)]

            if len(flip_bits) <= 1:
                if len(flip_bits) == 0:
                    write_flip_jump(data, temp_address, return_address, bit_width)
                else:
                    write_flip_jump(data, to_address + flip_bits[0], return_address, bit_width)
            else:
                next = last_address
                write_flip_jump(data, to_address + flip_bits[0], next, bit_width)
                for bit in flip_bits[1:-1]:
                    next += 2*bit_width
                    code.append((CommandType.FlipSCJump, (to_address + bit, next)))
                last_address = next + 2 * bit_width
                code.append((CommandType.FlipSCJump, (to_address + flip_bits[-1], return_address)))

        else:
            assert False

    writer.add_simple_sector_with_data(0, data)


def assemble(input_file, output_file, bit_width):
    writer = fjc.Writer(bit_width)
    code = [' '.join(line.split('//', 1)[0].rsplit(':', 1)[-1].split()) for line in open(input_file, 'r')]
    code = [op for op in code if op]
    labels, code, last_address = first_pass(code, bit_width)

    second_pass(writer, labels, code, bit_width, last_address)

    writer.write_to_file(output_file)


def full_assemble(input_files, output_file, preprocessed_file=None, bit_width=64, stl=True):
    temp_preprocessed_file, temp_fd = False, 0
    if preprocessed_file is None:
        temp_fd, preprocessed_file = mkstemp()
        temp_preprocessed_file = True

    preprocess(input_files, preprocessed_file, stl=bit_width if stl else False)
    assemble(preprocessed_file, output_file, bit_width)

    if temp_preprocessed_file:
        os.close(temp_fd)


def main():
    print('assembling')
    for test_name in ('cat',):#, 'ncat', 'mathbit', 'not', 'testbit', 'mathvec'):
        full_assemble([f'tests/{test_name}.fjm'], f'tests/{test_name}.fjc', preprocessed_file=f'tests/{test_name}.fj')


if __name__ == '__main__':
    main()

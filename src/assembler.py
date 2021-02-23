import blm
from preprocessor import resolve_macros
from tempfile import mkstemp
import os
from defs import *
from parser import parse_macro_tree


def resolve_skip_addresses(op, start_address, end_address):
    data = []
    for datum in op.data:
        if type(datum) is Address and datum.type in (AddrType.SkipAfter, AddrType.SkipBefore):
            data.append(Address(AddrType.Number, datum.base,
                                end_address + datum.index
                                if datum.type == AddrType.SkipAfter
                                else start_address - datum.index))
        else:
            data.append(datum)
    op.data = data


def label_dictionary_pass(ops, w, verbose=False):
    curr_address = 0
    rem_ops = []
    labels = {}
    label_places = {}

    for op in ops:
        if op.type == OpType.DDPad:
            padding_length = (-curr_address) % (op.data[0] * w)
            op = Op(OpType.BitSpecific, (padding_length, Address(AddrType.Number, 0, 0)), op.file, op.line)

        if op.type in {OpType.FlipJump, OpType.BitSpecific, OpType.DDFlipBy, OpType.DDFlipByDbit, OpType.DDVar}:
            delta = 2*w
            if op.type == OpType.BitSpecific:
                delta = op.data[0]
            elif op.type == OpType.DDVar:
                delta = op.data[0] * 2*w
            end_address = curr_address + delta
            resolve_skip_addresses(op, curr_address, end_address)
            curr_address = end_address
            if op.type in {OpType.DDFlipBy, OpType.DDFlipByDbit}:
                op.data.append(end_address)
            if verbose:
                print(f'op added: {str(op)}')
            rem_ops.append(op)
        elif op.type == OpType.Label:
            label = op.data[0]
            if label in labels:
                other_file, other_line = label_places[label]
                error(f'label declared twice - "{label}" on file {op.file} (line {op.line}) and file {other_file} (line {other_line})')
            if verbose:
                print(f'label added: "{label}" in {op.file} line {op.line}')
            labels[label] = curr_address
            label_places[label] = (op.file, op.line)
        else:
            error(f"Can't assemble this opcode - {str(op)}")

    return rem_ops, labels, curr_address


def resolve_address(op, addr, labels):
    if addr.type == AddrType.Number:
        return addr.base + addr.index
    if addr.type == AddrType.ID:
        label = addr.base
        if label not in labels:
            error(f'label not found - "{str(addr)}", in op {str(op)}')
        return labels[label] + addr.index
    error(f'bad address/label - "{str(addr)}", in op {str(op)}')


def lsb_first_bin_array(int_value, bit_size):
    return [int(c) for c in bin(int_value & ((1 << bit_size) - 1))[2:].zfill(bit_size)[-bit_size:]][::-1][:bit_size]


def write_flip_jump(bits, f, j, w):
    bits += lsb_first_bin_array(f, w)
    bits += lsb_first_bin_array(j, w)


def labels_resolve(ops, labels, last_address, w, output_file, verbose=False):   # TODO handle verbose?
    bits = []
    resolved_temp_address = labels[temp_address.base]

    for op in ops:
        if op.type == OpType.FlipJump:
            f, j = (resolve_address(op, op.data[i], labels) for i in (0, 1))
            write_flip_jump(bits, f, j, w)
        elif op.type == OpType.BitSpecific:
            n, v = op.data[0], resolve_address(op, op.data[1], labels)
            bits += lsb_first_bin_array(v, n)
        elif op.type in (OpType.DDFlipBy, OpType.DDFlipByDbit):
            to_address, by_address = (resolve_address(op, op.data[i], labels) for i in (0, 1))
            return_address = op.data[2]
            first_bit = 0 if op.type == OpType.DDFlipBy else w.bit_length() + 1
            flip_bits = [i for i in range(first_bit, w) if by_address & (1 << i)]

            if len(flip_bits) <= 1:
                write_flip_jump(bits, to_address + flip_bits[0] if flip_bits else resolved_temp_address, return_address, w)
            else:
                write_flip_jump(bits, to_address + flip_bits[0], last_address, w)
                next_op = last_address
                for bit in flip_bits[1:-1]:
                    next_op += 2*w
                    ops.append(Op(OpType.FlipJump, (Address(AddrType.Number, to_address, bit),
                                                    Address(AddrType.Number, next_op, 0)), op.file, op.line))
                last_address = next_op + 2*w
                ops.append(Op(OpType.FlipJump, (Address(AddrType.Number, to_address, flip_bits[-1]),
                                                Address(AddrType.Number, return_address, 0)), op.file, op.line))
        elif op.type == OpType.DDVar:
            n, v = op.data[0], resolve_address(op, op.data[1], labels)
            for i in range(n):
                write_flip_jump(bits, resolved_temp_address, 2*w if v & (1 << i) else 0, w)
        else:
            error(f"Can't resolve/assemble the next opcode - {str(op)}")

    writer = blm.Writer(w)
    writer.add_simple_sector_with_data(0, bits)
    writer.write_to_file(output_file)


def assemble(input_files, output_file, preprocessed_file=None, w=64, use_stl=True, verbose=set()):
    temp_preprocessed_file, temp_fd = False, 0
    if preprocessed_file is None:
        temp_fd, preprocessed_file = mkstemp()
        temp_preprocessed_file = True

    if use_stl:
        input_files = stl(w) + input_files

    macros = parse_macro_tree(input_files, verbose=Verbose.Parse in verbose)
    ops = resolve_macros(macros, output_file=preprocessed_file, verbose=Verbose.MacroSolve in verbose)
    ops, labels, last_address = label_dictionary_pass(ops, w, verbose=Verbose.LabelDict in verbose)
    labels_resolve(ops, labels, last_address, w, output_file, verbose=Verbose.LabelSolve in verbose)

    if temp_preprocessed_file:
        os.close(temp_fd)


def main():
    pass
    print('not assembling')
    # for test_name in ('cat',):#, 'ncat', 'mathbit', 'not', 'testbit', 'mathvec'):
    #     full_assemble([f'tests/{test_name}.fj'], f'tests/compiled/{test_name}.blm',
    #                   preprocessed_file=f'tests/compiled/{test_name}__no_macros.fj')


if __name__ == '__main__':
    main()

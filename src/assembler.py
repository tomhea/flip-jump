import blm
from preprocessor import resolve_macros
from tempfile import mkstemp
import os
from os.path import isfile, getmtime
from defs import *
from parser import parse_macro_tree
import pickle


def try_int(op, expr):
    if expr.is_int():
        return expr.val
    error(f"Can't resolve the following name: {expr.eval({}, op.file, op.line)} (in op={op}).")


def label_dictionary_pass(ops, w, verbose=False):
    curr_address = 0
    rem_ops = []
    labels = {}
    label_places = {}

    for op in ops:
        if op.type == OpType.DDPad:
            padding_length = (-curr_address) % (try_int(op, op.data[0]) * 2 * w)
            op = Op(OpType.BitSpecific, (Expr(padding_length), Expr(0)), op.file, op.line)

        if op.type in {OpType.FlipJump, OpType.BitSpecific, OpType.DDFlipBy, OpType.DDFlipByDbit, OpType.BitVar}:
            delta = 2*w
            if op.type == OpType.BitSpecific:
                delta = try_int(op, op.data[0])
            elif op.type == OpType.BitVar:
                delta = try_int(op, op.data[0]) * 2*w
            end_address = curr_address + delta
            eval_all(op, {'$': Expr(end_address)})
            curr_address = end_address
            if op.type in {OpType.DDFlipBy, OpType.DDFlipByDbit}:
                op.data += (Expr(end_address),)
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
            labels[label] = Expr(curr_address)
            label_places[label] = (op.file, op.line)
        else:
            error(f"Can't assemble this opcode - {str(op)}")

    return rem_ops, labels, curr_address


def lsb_first_bin_array(int_value, bit_size):
    return [int(c) for c in bin(int_value & ((1 << bit_size) - 1))[2:].zfill(bit_size)[-bit_size:]][::-1][:bit_size]


def write_flip_jump(bits, f, j, w):
    bits += lsb_first_bin_array(f, w)
    bits += lsb_first_bin_array(j, w)


def labels_resolve(ops, labels, last_address, w, output_file, verbose=False, flags=0):   # TODO handle verbose?
    if last_address >= (1<<w):
        error(f"Not enough space with the {w}-width.")
    bits = []
    if 'temp' not in labels:
        temp_temp_address = (1 << w) - 1
        print(f"Warning:  'temp' is not declared. It will be defined as {hex(temp_temp_address)[2:]}")
        labels['temp'] = Expr(temp_temp_address)
    resolved_temp_address = labels['temp'].val
    labels['__flip_by_Garden'] = Expr(last_address)

    for op in ops:
        ids = eval_all(op, labels)
        if ids:
            error(f"Can't resolve the following names: {', '.join(ids)} (in op {op}).")
        vals = [datum.val for datum in op.data]

        if op.type == OpType.FlipJump:
            f, j = vals
            write_flip_jump(bits, f, j, w)
        elif op.type == OpType.BitSpecific:
            n, v = vals
            bits += lsb_first_bin_array(v, n)
        elif op.type in (OpType.DDFlipBy, OpType.DDFlipByDbit):
            to_address, by_address, return_address = vals
            first_bit = 0 if op.type == OpType.DDFlipBy else w.bit_length() + 1
            flip_bits = [i for i in range(first_bit, w) if by_address & (1 << i)]

            if len(flip_bits) <= 1:
                write_flip_jump(bits, to_address + flip_bits[0] if flip_bits else resolved_temp_address, return_address, w)
            else:
                write_flip_jump(bits, to_address + flip_bits[0], last_address, w)
                next_op = last_address
                for bit in flip_bits[1:-1]:
                    next_op += 2*w
                    ops.append(Op(OpType.FlipJump, (Expr(to_address+bit), Expr(next_op)), op.file, op.line))
                last_address = next_op + 2*w
                if last_address >= (1 << w):
                    error(f"Not enough space with the {w}-width.")
                ops.append(Op(OpType.FlipJump, (Expr(to_address + flip_bits[-1]), Expr(return_address)), op.file, op.line))
        elif op.type == OpType.BitVar:
            n, v = vals
            for i in range(n):
                write_flip_jump(bits, resolved_temp_address, 2*w if v & (1 << i) else 0, w)
        else:
            error(f"Can't resolve/assemble the next opcode - {str(op)}")

    writer = blm.Writer(w, w, flags=flags if flags else 0)
    writer.add_simple_sector_with_data(0, bits)
    writer.write_to_file(output_file)


def assemble(input_files, output_file, w, flags=None,
             preprocessed_file=None, debugging_file=None, verbose=set()):
    if w not in (8, 16, 32, 64):
        error(f'The width ({w}) must be one of (8, 16, 32, 64).')

    # if only_cache:
    #     if isfile(debugging_file):
    #         with open(debugging_file, 'rb') as f:
    #             return pickle.load(f)
    #     print(debugging_file)
    #     return {}

    # if assembled files are up to date
    # if try_cached and debugging_file and isfile(output_file) and isfile(debugging_file):
    #     if max(getmtime(infile) for infile in input_files) \
    #             < min(getmtime(outfile) for outfile in (debugging_file, output_file)):
    #         if Verbose.Time in verbose:
    #             print(f'  loading assembled data...')
    #         with open(debugging_file, 'rb') as f:
    #             return pickle.load(f)

    temp_preprocessed_file, temp_fd = False, 0
    if preprocessed_file is None:
        temp_fd, preprocessed_file = mkstemp()
        temp_preprocessed_file = True

    start_time = time()
    macros = parse_macro_tree(input_files, w, verbose=Verbose.Parse in verbose)
    if Verbose.Time in verbose:
        print(f'  parsing:         {time() - start_time:.3f}s')

    start_time = time()
    ops = resolve_macros(macros, output_file=preprocessed_file, verbose=Verbose.MacroSolve in verbose)
    if Verbose.Time in verbose:
        print(f'  macro resolve:   {time() - start_time:.3f}s')

    start_time = time()
    ops, labels, last_address = label_dictionary_pass(ops, w, verbose=Verbose.LabelDict in verbose)
    if Verbose.Time in verbose:
        print(f'  labels pass:     {time() - start_time:.3f}s')

    start_time = time()
    labels_resolve(ops, labels, last_address, w, output_file, verbose=Verbose.LabelSolve in verbose, flags=flags)
    if Verbose.Time in verbose:
        print(f'  labels resolve:  {time() - start_time:.3f}s')

    if temp_preprocessed_file:
        os.close(temp_fd)

    labels = {label: labels[label].val for label in labels}

    if debugging_file:
        with open(debugging_file, 'wb') as f:
            pickle.dump(labels, f, pickle.HIGHEST_PROTOCOL)

    return labels


def main():
    pass
    print('not assembling')
    # for test_name in ('cat',):#, 'ncat', 'mathbit', 'not', 'testbit', 'mathvec'):
    #     full_assemble([f'tests/{test_name}.fj'], f'tests/compiled/{test_name}.blm',
    #                   preprocessed_file=f'tests/compiled/{test_name}__no_macros.fj')


if __name__ == '__main__':
    main()

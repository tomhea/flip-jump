import fjm
from preprocessor import resolve_macros
from tempfile import mkstemp
import os
from time import time
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
    boundary_addresses = [(SegEntry.StartAddress, 0)]   # SegEntries
    last_address_index = 0

    for op in ops:
        if op.type == OpType.Segment:
            eval_all(op, labels)
            value = try_int(op, op.data[0])
            if value % w != 0:
                error(f'.segment ops must have a w-aligned address. In {op}.')

            boundary_addresses.append((SegEntry.WflipAddress, curr_address))
            labels[f'{wflip_start_label}{last_address_index}'] = Expr(curr_address)
            last_address_index += 1

            curr_address = value
            boundary_addresses.append((SegEntry.StartAddress, curr_address))
            rem_ops.append(op)
        elif op.type == OpType.Reserve:
            eval_all(op, labels)
            value = try_int(op, op.data[0])
            if value % w != 0:
                error(f'.reserve ops must have a w-aligned value. In {op}.')

            curr_address += value
            boundary_addresses.append((SegEntry.ReserveAddress, curr_address))
            labels[f'{wflip_start_label}{last_address_index}'] = Expr(curr_address)

            last_address_index += 1
            rem_ops.append(op)
        elif op.type in {OpType.FlipJump, OpType.WordsValue, OpType.WordFlip}:
            delta = 2*w
            if op.type == OpType.WordsValue:
                eval_all(op, labels)
                delta = w * try_int(op, op.data[0])
            end_address = curr_address + delta
            eval_all(op, {'$': Expr(end_address)})
            curr_address = end_address
            if op.type == OpType.WordFlip:
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

    boundary_addresses.append((SegEntry.WflipAddress, curr_address))
    return rem_ops, labels, boundary_addresses


def lsb_first_bin_array(int_value, bit_size):
    return [int(c) for c in bin(int_value & ((1 << bit_size) - 1))[2:].zfill(bit_size)[-bit_size:]][::-1][:bit_size]


def write_flip_jump(bits, f, j, w):
    bits += lsb_first_bin_array(f, w)
    bits += lsb_first_bin_array(j, w)


def close_segment(w, segment_index, boundary_addresses, writer, first_address, last_address, bits, wflips):
    if first_address == last_address:
        return
    assert_none_crossing_segments(segment_index, first_address, last_address, boundary_addresses)

    data_start, data_length = writer.add_data(bits + wflips)
    segment_length = (last_address - first_address) // w
    if segment_length < data_length:
        error(f'segment-length is smaller than data-length:  {segment_length} < {data_length}')
    writer.add_segment(first_address // w, segment_length, data_start, data_length)

    bits.clear()
    wflips.clear()


def clean_segment_index(index, boundary_addresses):
    clean_index = 0
    for entry in boundary_addresses[:index]:
        if entry[0] == SegEntry.WflipAddress:
            clean_index += 1
    return clean_index


def assert_none_crossing_segments(curr_segment_index, old_address, new_address, boundary_addresses):
    min_i = None
    min_seg_start = None

    last_start = None
    last_start_i = None
    for i, entry in enumerate(boundary_addresses):
        if entry[0] == SegEntry.StartAddress:
            last_start = entry[1]
            last_start_i = i
        if entry[0] == SegEntry.WflipAddress:
            if entry[1] != last_start:
                if old_address < last_start < new_address:
                    if min_i is None or min_seg_start > last_start:
                        min_i = last_start_i
                        min_seg_start = last_start

    if min_i is not None:
        error(f"Overlapping segments (address {hex(new_address)}): "
              f"seg[{clean_segment_index(curr_segment_index, boundary_addresses)}]=({hex(boundary_addresses[curr_segment_index][1])}..) and "
              f"seg[{clean_segment_index(min_i, boundary_addresses)}]=({hex(min_seg_start)}..)")


def get_next_wflip_entry_index(boundary_addresses, index):
    length = len(boundary_addresses)
    while boundary_addresses[index][0] != SegEntry.WflipAddress:
        index += 1
        if index >= length:
            error(f'No WflipAddress entry found in boundary_addresses.')
    return index


def labels_resolve(ops, labels, boundary_addresses, w, output_file, verbose=False, flags=0):   # TODO handle verbose?
    if max(e[1] for e in boundary_addresses) >= (1 << w):
        error(f"Not enough space with the {w}-width.")

    writer = fjm.Writer(w, w, flags=flags if flags else 0)

    bits = []
    wflips = []
    segment_index = 0
    last_start_seg_index = segment_index
    first_address = boundary_addresses[last_start_seg_index][1]
    wflip_address = boundary_addresses[get_next_wflip_entry_index(boundary_addresses, 0)][1]

    for op in ops:
        ids = eval_all(op, labels)
        if ids:
            error(f"Can't resolve the following names: {', '.join(ids)} (in op {op}).")
        vals = [datum.val for datum in op.data]

        if op.type == OpType.FlipJump:
            f, j = vals
            bits += [f, j]
        elif op.type == OpType.WordsValue:
            n, v = vals
            bits += [v] * n
        elif op.type == OpType.Segment:
            segment_index += 2
            close_segment(w, last_start_seg_index, boundary_addresses, writer, first_address, wflip_address, bits, wflips)
            last_start_seg_index = segment_index
            first_address = boundary_addresses[last_start_seg_index][1]
            wflip_address = boundary_addresses[get_next_wflip_entry_index(boundary_addresses, segment_index)][1]
        elif op.type == OpType.Reserve:
            segment_index += 1
            last_address = boundary_addresses[segment_index][1]
            close_segment(w, last_start_seg_index, boundary_addresses, writer, first_address, last_address, bits, [])
            first_address = last_address
        elif op.type == OpType.WordFlip:
            to_address, by_address, return_address = vals
            flip_bits = [i for i in range(w) if by_address & (1 << i)]

            if len(flip_bits) <= 1:
                bits += [to_address + flip_bits[0] if flip_bits else 0,
                         return_address]
            else:
                bits += [to_address + flip_bits[0],
                         wflip_address]
                next_op = wflip_address
                for bit in flip_bits[1:-1]:
                    next_op += 2*w
                    wflips += [to_address+bit,
                               next_op]
                wflips += [to_address + flip_bits[-1],
                           return_address]
                wflip_address = next_op + 2 * w

                if wflip_address >= (1 << w):
                    error(f"Not enough space with the {w}-width.")
        else:
            error(f"Can't resolve/assemble the next opcode - {str(op)}")

    close_segment(w, last_start_seg_index, boundary_addresses, writer, first_address, wflip_address, bits, wflips)
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
    #     full_assemble([f'tests/{test_name}.fj'], f'tests/compiled/{test_name}.fjm',
    #                   preprocessed_file=f'tests/compiled/{test_name}__no_macros.fj')


if __name__ == '__main__':
    main()

import os
import pickle
from tempfile import mkstemp

import fjm
from fj_parser import parse_macro_tree
from preprocessor import resolve_macros
from defs import eval_all, Verbose, SegmentEntry, FJAssemblerException, OpType, PrintTimer, FlipJump, WordFlip, \
    FJException


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
        raise FJAssemblerException(f'segment-length is smaller than data-length:  {segment_length} < {data_length}')
    writer.add_segment(first_address // w, segment_length, data_start, data_length)

    bits.clear()
    wflips.clear()


def clean_segment_index(index, boundary_addresses):
    clean_index = 0
    for entry in boundary_addresses[:index]:
        if entry[0] == SegmentEntry.WflipAddress:
            clean_index += 1
    return clean_index


def assert_none_crossing_segments(curr_segment_index, old_address, new_address, boundary_addresses):
    min_i = None
    min_seg_start = None

    last_start = None
    last_start_i = None
    for i, entry in enumerate(boundary_addresses):
        if entry[0] == SegmentEntry.StartAddress:
            last_start = entry[1]
            last_start_i = i
        if entry[0] == SegmentEntry.WflipAddress:
            if entry[1] != last_start:
                if old_address < last_start < new_address:
                    if min_i is None or min_seg_start > last_start:
                        min_i = last_start_i
                        min_seg_start = last_start

    if min_i is not None:
        raise FJAssemblerException(f"Overlapping segments (address {hex(new_address)}): "
                                   f"seg[{clean_segment_index(curr_segment_index, boundary_addresses)}]"
                                   f"=({hex(boundary_addresses[curr_segment_index][1])}..) and "
                                   f"seg[{clean_segment_index(min_i, boundary_addresses)}]=({hex(min_seg_start)}..)")


def get_next_wflip_entry_index(boundary_addresses, index):
    length = len(boundary_addresses)
    while boundary_addresses[index][0] != SegmentEntry.WflipAddress:
        index += 1
        if index >= length:
            raise FJAssemblerException(f'No WflipAddress entry found in boundary_addresses.')
    return index


def labels_resolve(ops, labels, boundary_addresses, w, writer):
    if max(e[1] for e in boundary_addresses) >= (1 << w):
        raise FJAssemblerException(f"Not enough space with the {w}-width.")

    bits = []
    wflips = []
    segment_index = 0
    last_start_seg_index = segment_index
    first_address = boundary_addresses[last_start_seg_index][1]
    wflip_address = boundary_addresses[get_next_wflip_entry_index(boundary_addresses, 0)][1]

    for op in ops:
        try:
            vals = op.eval_int_data(labels)
        except FJException as e:
            raise FJAssemblerException(f"Can't resolve labels in op {op}.") from e

        if isinstance(op, FlipJump):
            f, j = vals
            bits += [f, j]
        elif op.type == OpType.Segment:
            segment_index += 2
            close_segment(w, last_start_seg_index, boundary_addresses, writer, first_address, wflip_address, bits,
                          wflips)
            last_start_seg_index = segment_index
            first_address = boundary_addresses[last_start_seg_index][1]
            wflip_address = boundary_addresses[get_next_wflip_entry_index(boundary_addresses, segment_index)][1]
        elif op.type == OpType.Reserve:
            segment_index += 1
            last_address = boundary_addresses[segment_index][1]
            close_segment(w, last_start_seg_index, boundary_addresses, writer, first_address, last_address, bits, [])
            first_address = last_address
        elif isinstance(op, WordFlip):
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
                    raise FJAssemblerException(f"Not enough space with the {w}-width.")
        else:
            raise FJAssemblerException(f"Can't resolve/assemble the next opcode - {str(op)}")

    close_segment(w, last_start_seg_index, boundary_addresses, writer, first_address, wflip_address, bits, wflips)


def assemble(input_files, output_file, w,
             *, version=0, flags=0,
             warning_as_errors=True,
             show_statistics=False, preprocessed_file=None, debugging_file=None, verbose=None):
    if verbose is None:
        verbose = set()

    writer = fjm.Writer(output_file, w, version=version, flags=flags)

    temp_preprocessed_file, temp_fd = False, 0
    if preprocessed_file is None:
        temp_fd, preprocessed_file = mkstemp()
        temp_preprocessed_file = True

    time_verbose = Verbose.Time in verbose

    with PrintTimer('  parsing:         ', print_time=time_verbose):
        macros = parse_macro_tree(input_files, w, warning_as_errors)

    with PrintTimer('  macro resolve:   ', print_time=time_verbose):
        ops, labels, boundary_addresses = resolve_macros(w, macros, output_file=preprocessed_file,
                                                         show_statistics=show_statistics)

    with PrintTimer('  labels resolve:  ', print_time=time_verbose):
        labels_resolve(ops, labels, boundary_addresses, w, writer)

    with PrintTimer('  create binary:   ', print_time=time_verbose):
        writer.write_to_file()

    if temp_preprocessed_file:
        os.close(temp_fd)

    labels = {label: labels[label].val for label in labels}

    if debugging_file:
        with open(debugging_file, 'wb') as f:
            pickle.dump(labels, f, pickle.HIGHEST_PROTOCOL)

    return labels

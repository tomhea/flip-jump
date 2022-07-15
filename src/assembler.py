import pickle
from pathlib import Path
from typing import Deque, List, Dict, Tuple

import fjm
from fj_parser import parse_macro_tree
from preprocessor import resolve_macros
from defs import Verbose, SegmentEntry, FJAssemblerException, PrintTimer, FlipJump, WordFlip, \
    FJException, Segment, Reserve, BoundaryAddressesList, Expr, LastPhaseOp


def close_segment(w: int,
                  segment_index: int, boundary_addresses: BoundaryAddressesList,
                  writer: fjm.Writer,
                  first_address: int, last_address: int,
                  fj_words: List[int], wflip_words: List[int]) -> None:
    if first_address == last_address:
        return
    assert_none_crossing_segments(segment_index, first_address, last_address, boundary_addresses)

    data_start, data_length = writer.add_data(fj_words + wflip_words)
    segment_length = (last_address - first_address) // w
    if segment_length < data_length:
        raise FJAssemblerException(f'segment-length is smaller than data-length:  {segment_length} < {data_length}')
    writer.add_segment(first_address // w, segment_length, data_start, data_length)

    fj_words.clear()
    wflip_words.clear()


def get_clean_segment_index(index: int, boundary_addresses: BoundaryAddressesList) -> int:
    clean_index = 0
    for entry in boundary_addresses[:index]:
        if entry[0] == SegmentEntry.WflipAddress:
            clean_index += 1
    return clean_index


def assert_none_crossing_segments(curr_segment_index: int,
                                  old_address: int, new_address: int,
                                  boundary_addresses: BoundaryAddressesList) -> None:
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
                                   f"seg[{get_clean_segment_index(curr_segment_index, boundary_addresses)}]"
                                   f"=({hex(boundary_addresses[curr_segment_index][1])}..) and "
                                   f"seg[{get_clean_segment_index(min_i, boundary_addresses)}]=({hex(min_seg_start)}..)")


def get_next_wflip_entry_index(boundary_addresses: BoundaryAddressesList, index: int) -> int:
    length = len(boundary_addresses)
    while boundary_addresses[index][0] != SegmentEntry.WflipAddress:
        index += 1
        if index >= length:
            raise FJAssemblerException(f'No WflipAddress entry found in boundary_addresses.')
    return index


def labels_resolve(ops: Deque[LastPhaseOp], labels: Dict[str, Expr],
                   boundary_addresses: BoundaryAddressesList,
                   w: int, writer: fjm.Writer) -> None:
    if max(e[1] for e in boundary_addresses) >= (1 << w):
        raise FJAssemblerException(f"Not enough space with the {w}-width.")

    fj_words = []
    wflip_words = []
    segment_index = 0
    last_start_seg_index = segment_index
    first_address = boundary_addresses[last_start_seg_index][1]
    wflip_address = boundary_addresses[get_next_wflip_entry_index(boundary_addresses, 0)][1]

    for op in ops:
        if isinstance(op, FlipJump):
            try:
                fj_words += (op.get_flip(labels), op.get_jump(labels))
            except FJException as e:
                raise FJAssemblerException(f"Can't resolve labels in op {op}.") from e
        elif isinstance(op, WordFlip):
            try:
                word_address = op.get_word_address(labels)
                flip_value = op.get_flip_value(labels)
                return_address = op.get_return_address(labels)
            except FJException as e:
                raise FJAssemblerException(f"Can't resolve labels in op {op}.") from e

            flip_bits = [i for i in range(w) if flip_value & (1 << i)]

            if len(flip_bits) <= 1:
                fj_words += (word_address + flip_bits[0] if flip_bits else 0, return_address)
            else:
                fj_words += (word_address + flip_bits[0], wflip_address)
                next_op = wflip_address
                for bit in flip_bits[1:-1]:
                    next_op += 2*w
                    wflip_words += (word_address+bit, next_op)
                wflip_words += (word_address + flip_bits[-1], return_address)
                wflip_address = next_op + 2 * w

                if wflip_address >= (1 << w):
                    raise FJAssemblerException(f"Not enough space with the {w}-width.")
        elif isinstance(op, Segment):
            segment_index += 2
            close_segment(w, last_start_seg_index, boundary_addresses, writer, first_address, wflip_address, fj_words,
                          wflip_words)
            last_start_seg_index = segment_index
            first_address = boundary_addresses[last_start_seg_index][1]
            wflip_address = boundary_addresses[get_next_wflip_entry_index(boundary_addresses, segment_index)][1]
        elif isinstance(op, Reserve):
            segment_index += 1
            last_address = boundary_addresses[segment_index][1]
            close_segment(w, last_start_seg_index, boundary_addresses, writer, first_address, last_address, fj_words, [])
            first_address = last_address
        else:
            raise FJAssemblerException(f"Can't resolve/assemble the next opcode - {str(op)}")

    close_segment(w, last_start_seg_index, boundary_addresses, writer, first_address, wflip_address, fj_words, wflip_words)


def assemble(input_files: List[Tuple[str, Path]], output_file, w,
             *, version=0, flags=0,
             warning_as_errors=True,
             show_statistics=False, debugging_file=None, print_time=True):
    writer = fjm.Writer(output_file, w, version=version, flags=flags)

    with PrintTimer('  parsing:         ', print_time=print_time):
        macros = parse_macro_tree(input_files, w, warning_as_errors)

    with PrintTimer('  macro resolve:   ', print_time=print_time):
        ops, labels, boundary_addresses = resolve_macros(w, macros,
                                                         show_statistics=show_statistics)

    with PrintTimer('  labels resolve:  ', print_time=print_time):
        labels_resolve(ops, labels, boundary_addresses, w, writer)

    with PrintTimer('  create binary:   ', print_time=print_time):
        writer.write_to_file()

    labels = {label: labels[label].val for label in labels}

    if debugging_file:
        with open(debugging_file, 'wb') as f:
            pickle.dump(labels, f, pickle.HIGHEST_PROTOCOL)

    return labels

import pickle
from pathlib import Path
from typing import Deque, List, Dict, Tuple, Optional

import fjm
from fj_parser import parse_macro_tree
from preprocessor import resolve_macros

from expr import Expr
from defs import PrintTimer
from ops import FlipJump, WordFlip, LastPhaseOp, NewSegment, ReserveBits
from exceptions import FJAssemblerException, FJException, FJWriteFjmException


def add_segment_to_fjm(w: int,
                       fjm_writer: fjm.Writer,
                       first_address: int, last_address: int,
                       fj_words: List[int], wflip_words: Optional[List[int]]) -> None:
    if first_address == last_address:
        return

    if first_address % w != 0 or last_address % w != 0:
        raise FJAssemblerException(f'segment boundaries are unaligned: [{hex(first_address)}, {hex(last_address-1)}].')

    assert_address_in_memory(w, first_address)
    assert_address_in_memory(w, last_address)

    words_to_write = fj_words if wflip_words is None else fj_words + wflip_words
    data_start, data_length = fjm_writer.add_data(words_to_write)

    first_word_address = first_address // w
    segment_word_length = (last_address - first_address) // w

    try:
        fjm_writer.add_segment(first_word_address, segment_word_length, data_start, data_length)
    except FJWriteFjmException as e:
        raise FJAssemblerException(f"failed to add the segment: "
                                   f"[{hex(first_address)}, {hex(last_address-1)}].") from e

    fj_words.clear()
    if wflip_words is not None:
        wflip_words.clear()


def assert_address_in_memory(w: int, address: int):
    if address < 0 or address >= (1 << w):
        raise FJAssemblerException(f"Not enough space with the {w}-width.")


def insert_wflip_ops(wflip_address: int, flip_value: int, return_address: int,
                     fj_words: List[int], wflip_words: List[int], w: int, word_address: int):
    flip_bits = [i for i in range(w) if flip_value & (1 << i)]

    if len(flip_bits) <= 1:
        fj_words += (word_address + flip_bits[0] if flip_bits else 0, return_address)
    else:
        fj_words += (word_address + flip_bits[0], wflip_address)
        next_op = wflip_address
        for bit in flip_bits[1:-1]:
            next_op += 2 * w
            wflip_words += (word_address + bit, next_op)
        wflip_words += (word_address + flip_bits[-1], return_address)
        wflip_address = next_op + 2 * w

    return wflip_address


def labels_resolve(ops: Deque[LastPhaseOp], labels: Dict[str, Expr],
                   w: int, fjm_writer: fjm.Writer) -> None:
    fj_words = []
    wflip_words = []

    first_segment: NewSegment = ops.popleft()
    first_address: int = first_segment.start_address
    wflip_address: int = first_segment.wflip_start_address

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

            wflip_address = insert_wflip_ops(wflip_address, flip_value, return_address,
                                             fj_words, wflip_words, w, word_address)

        elif isinstance(op, NewSegment):
            add_segment_to_fjm(w, fjm_writer, first_address, wflip_address, fj_words, wflip_words)
            first_address = op.start_address
            wflip_address = op.wflip_start_address

        elif isinstance(op, ReserveBits):
            add_segment_to_fjm(w, fjm_writer, first_address, op.first_address_after_reserved, fj_words, None)
            first_address = op.first_address_after_reserved

        else:
            raise FJAssemblerException(f"Can't resolve/assemble the next opcode - {str(op)}")

    add_segment_to_fjm(w, fjm_writer, first_address, wflip_address, fj_words, wflip_words)


def assemble(input_files: List[Tuple[str, Path]], output_file: Path, w: int,
             *, version: int = 0, flags: int = 0,
             warning_as_errors: bool = True,
             show_statistics: bool = False, debugging_file: Optional[Path] = None, print_time: bool = True)\
        -> None:
    """
    runs the assembly pipeline. assembles the input files to a .fjm.
    @param input_files:[in]: a list of (short_file_name, fj_file_path). The files will to be parsed in that given order.
    @param output_file:[in]: the path to the .fjm file
    @param w:[in]: the memory-width
    @param version: the .fjm version
    @param flags: the .fjm flags
    @param warning_as_errors: treat warnings as errors (stop execution on warnings)
    @param show_statistics: if true shows macro-usage statistics
    @param debugging_file:[in]: is specified, save debug information in this file
    @param print_time: if true prints the times of each assemble-stage
    """
    fjm_writer = fjm.Writer(output_file, w, version=version, flags=flags)

    with PrintTimer('  parsing:         ', print_time=print_time):
        macros = parse_macro_tree(input_files, w, warning_as_errors)

    with PrintTimer('  macro resolve:   ', print_time=print_time):
        ops, labels = resolve_macros(w, macros, show_statistics=show_statistics)

    with PrintTimer('  labels resolve:  ', print_time=print_time):
        labels_resolve(ops, labels, w, fjm_writer)

    with PrintTimer('  create binary:   ', print_time=print_time):
        fjm_writer.write_to_file()

    labels = {label: labels[label].value for label in labels}

    if debugging_file:
        with open(debugging_file, 'wb') as f:
            pickle.dump(labels, f, pickle.HIGHEST_PROTOCOL)

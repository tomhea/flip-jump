import dataclasses
import pickle
from collections import defaultdict
from pathlib import Path
from typing import Deque, List, Dict, Tuple, Optional

import fjm
from fj_parser import parse_macro_tree
from preprocessor import resolve_macros

from expr import Expr
from defs import PrintTimer
from ops import FlipJump, WordFlip, LastPhaseOp, NewSegment, ReserveBits, Padding
from exceptions import FJAssemblerException, FJException, FJWriteFjmException


def assert_address_in_memory(w: int, address: int):
    if address < 0 or address >= (1 << w):
        raise FJAssemblerException(f"Not enough space with the {w}-width.")


def validate_addresses(w, first_address, last_address):
    if first_address % w != 0 or last_address % w != 0:
        raise FJAssemblerException(f'segment boundaries are unaligned: '
                                   f'[{hex(first_address)}, {hex(last_address - 1)}].')

    assert_address_in_memory(w, first_address)
    assert_address_in_memory(w, last_address)


def add_segment_to_fjm(w: int,
                       fjm_writer: fjm.Writer,
                       first_address: int, last_address: int,
                       fj_words: List[int], wflip_words: List[int]) -> None:
    validate_addresses(w, first_address, last_address)
    if first_address == last_address:
        return

    data_start, data_length = fjm_writer.add_data(fj_words + wflip_words)

    try:
        fjm_writer.add_segment(first_address // w, (last_address - first_address) // w, data_start, data_length)
    except FJWriteFjmException as e:
        raise FJAssemblerException(f"failed to add the segment: "
                                   f"[{hex(first_address)}, {hex(last_address-1)}].") from e

    fj_words.clear()
    wflip_words.clear()


@dataclasses.dataclass
class WFlipSpot:
    list: List[int]
    index: int
    address: int


class BinaryData:
    def __init__(self, w: int, first_segment: NewSegment):
        self.w = w

        self.first_address = first_segment.start_address
        self.wflip_address = first_segment.wflip_start_address

        self.current_address = self.first_address

        self.fj_words: List[int] = []
        self.wflip_words: List[int] = []

        self.padding_ops_indices: List[int] = []    # indices in self.fj_words

        # return_address -> { (f3, f2, f1, f0) -> start_flip_address }
        self.wflips_dict: Dict[int, Dict[Tuple[int, ...],]] = defaultdict(lambda: {})

    def get_wflip_spot(self) -> WFlipSpot:
        if self.padding_ops_indices:
            index = self.padding_ops_indices.pop()
            return WFlipSpot(self.fj_words, index, self.first_address + self.w * index)

        wflip_spot = WFlipSpot(self.wflip_words, len(self.wflip_words), self.wflip_address)
        self.wflip_words += (0, 0)
        self.wflip_address += 2*self.w
        return wflip_spot

    def close_and_add_segment(self, fjm_writer: fjm.Writer) -> None:
        add_segment_to_fjm(self.w, fjm_writer, self.first_address, self.wflip_address, self.fj_words, self.wflip_words)

    def insert_fj_op(self, flip: int, jump: int) -> None:
        self.fj_words += (flip, jump)
        self.current_address += 2*self.w

    def insert_wflip_ops(self, word_address: int, flip_value: int, return_address: int) -> None:
        if 0 == flip_value:
            self.insert_fj_op(0, return_address)
        else:
            return_dict = self.wflips_dict[return_address]

            # this is the order of flip_addresses (tested with many other orders) that produces the best
            #  found-statistic for searching flip_bit[:i] with different i's in return_dict.
            flip_addresses = [word_address + i for i in range(self.w) if flip_value & (1 << i)][::-1]

            # insert the first op
            self.insert_fj_op(flip_addresses.pop(), 0)
            last_return_address_index = self.fj_words, len(self.fj_words) - 1

            while flip_addresses:
                flips_key = tuple(flip_addresses)
                ops_list, last_address_index = last_return_address_index

                if flips_key in return_dict:
                    # connect the last op to the already created wflip-chain
                    ops_list[last_address_index] = return_dict[flips_key]
                    return
                else:
                    # insert a new wflip op, and connect the last one to it
                    wflip_spot = self.get_wflip_spot()

                    ops_list[last_address_index] = wflip_spot.address
                    return_dict[flips_key] = wflip_spot.address

                    wflip_spot.list[wflip_spot.index] = flip_addresses.pop()
                    last_return_address_index = wflip_spot.list, wflip_spot.index + 1

            ops_list, last_address_index = last_return_address_index
            ops_list[last_address_index] = return_address

    def insert_padding(self, ops_count: int) -> None:
        for i in range(len(self.fj_words), len(self.fj_words) + 2 * ops_count, 2):
            self.padding_ops_indices.append(i)
            self.fj_words += (0, 0)
        self.current_address += ops_count * (2*self.w)

    def insert_new_segment(self, fjm_writer: fjm.Writer, first_address: int, wflip_first_address: int) -> None:
        self.close_and_add_segment(fjm_writer)

        self.first_address = first_address
        self.wflip_address = wflip_first_address
        self.current_address = self.first_address

        self.padding_ops_indices.clear()

    def insert_reserve_bits(self, fjm_writer: fjm.Writer, new_first_address: int) -> None:
        add_segment_to_fjm(self.w, fjm_writer, self.first_address, new_first_address, self.fj_words, [])

        self.first_address = new_first_address
        self.current_address = self.first_address

        self.padding_ops_indices.clear()


def labels_resolve(ops: Deque[LastPhaseOp], labels: Dict[str, Expr],
                   w: int, fjm_writer: fjm.Writer) -> None:
    first_segment: NewSegment = ops.popleft()
    if not isinstance(first_segment, NewSegment):
        raise FJAssemblerException(f"The first op must be of type NewSegment (and not {first_segment}).")

    binary_data = BinaryData(w, first_segment)

    for op in ops:
        if isinstance(op, FlipJump):
            try:
                binary_data.insert_fj_op(op.get_flip(labels), op.get_jump(labels))
            except FJException as e:
                raise FJAssemblerException(f"Can't resolve labels in op {op}.") from e

        elif isinstance(op, WordFlip):
            try:
                binary_data.insert_wflip_ops(op.get_word_address(labels), op.get_flip_value(labels),
                                             op.get_return_address(labels))
            except FJException as e:
                raise FJAssemblerException(f"Can't resolve labels in op {op}.") from e

        elif isinstance(op, Padding):
            binary_data.insert_padding(op.ops_count)

        elif isinstance(op, NewSegment):
            binary_data.insert_new_segment(fjm_writer, op.start_address, op.wflip_start_address)

        elif isinstance(op, ReserveBits):
            binary_data.insert_reserve_bits(fjm_writer, op.first_address_after_reserved)

        else:
            raise FJAssemblerException(f"Can't resolve/assemble the next opcode - {str(op)}")

    binary_data.close_and_add_segment(fjm_writer)


def assemble(input_files: List[Tuple[str, Path]], output_file: Path, w: int, version,
             *, flags: int = 0, lzma_preset: Optional[int] = None,
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
    @param lzma_preset: the preset to be used when compressing the .fjm data
    @param warning_as_errors: treat warnings as errors (stop execution on warnings)
    @param show_statistics: if true shows macro-usage statistics
    @param debugging_file:[in]: is specified, save debug information in this file
    @param print_time: if true prints the times of each assemble-stage
    """
    fjm_writer = fjm.Writer(output_file, w, version, flags=flags, lzma_preset=lzma_preset)

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

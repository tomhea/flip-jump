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

    if wflip_words and len(fj_words) > 1000 and len(wflip_words) > 1000:
        print(f'wflips={len(wflip_words) / len(fj_words + wflip_words) * 100:.3f}%')

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


class BinaryData:
    def __init__(self, w: int, first_segment: NewSegment):
        self.w = w

        self.fj_words: List[int] = []
        self.wflip_words: List[int] = []

        self.padding_ops_indices: List[int] = []    # indices in self.fj_words

        # return_address -> { (i3, i2, i1, i0) -> address }
        self.wflips_dict: Dict[int, Dict[Tuple[int, ...],]] = defaultdict(lambda: {})

        self.first_address = first_segment.start_address
        self.wflip_address = first_segment.wflip_start_address

        self.current_address = self.first_address

        self.saved_ops = 0

    def get_wflip_spot(self):
        if self.padding_ops_indices:
            self.saved_ops += 1
            index = self.padding_ops_indices.pop()
            return self.fj_words, index, self.first_address + self.w * index

        index = len(self.wflip_words)
        address = self.wflip_address

        self.wflip_words += (0, 0)
        self.wflip_address += 2*self.w

        return self.wflip_words, index, address

    def close_and_add_segment(self, fjm_writer: fjm.Writer):
        add_segment_to_fjm(self.w, fjm_writer, self.first_address, self.wflip_address, self.fj_words, self.wflip_words)

    def new_segment(self, fjm_writer: fjm.Writer, new_segment_op: NewSegment):
        self.close_and_add_segment(fjm_writer)
        self.first_address = new_segment_op.start_address
        self.wflip_address = new_segment_op.wflip_start_address
        self.current_address = self.first_address
        self.padding_ops_indices.clear()

    def reserve_bits(self, fjm_writer: fjm.Writer, reserve_bits_op: ReserveBits):
        new_first_address = reserve_bits_op.first_address_after_reserved
        add_segment_to_fjm(self.w, fjm_writer, self.first_address, new_first_address, self.fj_words, None)
        self.first_address = new_first_address
        self.current_address = self.first_address
        self.padding_ops_indices.clear()


def labels_resolve(ops: Deque[LastPhaseOp], labels: Dict[str, Expr],
                   w: int, fjm_writer: fjm.Writer) -> None:
    op_size = 2*w

    return_addresses = []
    wflip_sizes = []
    same_bits = 4

    first_segment: NewSegment = ops.popleft()
    binary_data = BinaryData(w, first_segment)

    for op in ops:

        if isinstance(op, FlipJump):
            try:
                binary_data.fj_words += (op.get_flip(labels), op.get_jump(labels))
                binary_data.current_address += op_size
            except FJException as e:
                raise FJAssemblerException(f"Can't resolve labels in op {op}.") from e

        elif isinstance(op, WordFlip):
            try:
                word_address = op.get_word_address(labels)
                flip_value = op.get_flip_value(labels)
                return_address = op.get_return_address(labels)
            except FJException as e:
                raise FJAssemblerException(f"Can't resolve labels in op {op}.") from e

            return_dict = binary_data.wflips_dict[return_address]

            # this is the order of flip_addresses (tested with many other orders) that produces the best found-statistic
            #  for searching flip_bit[:i] with different i's in return_dict.
            flip_addresses = [word_address + i for i in range(w) if flip_value & (1 << i)][::-1]

            if len(flip_addresses) >= same_bits:
                return_addresses.append((*flip_addresses[:same_bits], return_address))
                wflip_sizes.append(len(flip_addresses))

            if len(flip_addresses) <= 1:
                if flip_addresses:
                    return_dict[(flip_addresses[0], )] = binary_data.current_address
                    binary_data.fj_words += (flip_addresses[0], return_address)
                else:
                    binary_data.fj_words += (0, return_address)
            else:
                first_bit = flip_addresses.pop()
                binary_data.fj_words += (first_bit, 0)
                last_return_address_index = binary_data.fj_words, len(binary_data.fj_words) - 1

                while flip_addresses:
                    flips_key = tuple(flip_addresses)
                    ops_list, index = last_return_address_index
                    if flips_key in return_dict:
                        ops_list[index] = return_dict[flips_key]
                        last_return_address_index = None
                        binary_data.saved_ops += len(flips_key)
                        break
                    else:
                        wflip_spot_list, wflip_spot_index, wflip_spot_address = binary_data.get_wflip_spot()

                        ops_list[index] = wflip_spot_address
                        return_dict[flips_key] = wflip_spot_address

                        wflip_spot_list[wflip_spot_index] = flip_addresses.pop()
                        last_return_address_index = wflip_spot_list, wflip_spot_index + 1

                if last_return_address_index is not None:
                    ops_list, index = last_return_address_index
                    ops_list[index] = return_address

                # next_op = wflip_address
                # for bit in flip_addresses[:-1]:
                #     next_op += 2 * w
                #     wflip_words += (bit, next_op)
                # wflip_words += (flip_addresses[-1], return_address)
                # wflip_address = next_op + 2 * w

            binary_data.current_address += op_size

        elif isinstance(op, Padding):
            for i in range(len(binary_data.fj_words), len(binary_data.fj_words) + 2*op.ops_count, 2):
                binary_data.padding_ops_indices.append(i)
                binary_data.fj_words += (0, 0)
            binary_data.current_address += op.ops_count * op_size

        elif isinstance(op, NewSegment):
            binary_data.new_segment(fjm_writer, op)

        elif isinstance(op, ReserveBits):
            binary_data.reserve_bits(fjm_writer, op)

        else:
            raise FJAssemblerException(f"Can't resolve/assemble the next opcode - {str(op)}")

    binary_data.close_and_add_segment(fjm_writer)

    if return_addresses and wflip_sizes:
        print(f'repeated-returns({same_bits})={(len(return_addresses) - len(set(return_addresses))) / len(return_addresses) * 100:.3f}%  '
              f'(each {sum(wflip_sizes) / len(wflip_sizes):.2f} ops)  '
              f'(total fj ops = {len(fjm_writer.data) // 2})  '
              f'(saved {binary_data.saved_ops / (len(fjm_writer.data) // 2 + binary_data.saved_ops) * 100:.3f}%)')


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

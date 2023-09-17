import dataclasses
from collections import defaultdict
from pathlib import Path
from typing import Deque, List, Dict, Tuple, Optional

from flipjump.fjm.fjm_writer import Writer
from flipjump.utils.constants import WFLIP_LABEL_PREFIX
from flipjump.utils.functions import save_debugging_labels
from flipjump.utils.classes import PrintTimer
from flipjump.assembler.fj_parser import parse_macro_tree
from flipjump.utils.exceptions import FlipJumpAssemblerException, FlipJumpException, FlipJumpWriteFjmException
from flipjump.assembler.inner_classes.ops import FlipJump, WordFlip, LastPhaseOp, NewSegment, ReserveBits, Padding
from flipjump.assembler.preprocessor import resolve_macros


def assert_address_in_memory(memory_width: int, address: int):
    if address < 0 or address >= (1 << memory_width):
        raise FlipJumpAssemblerException(f"Not enough space with the {memory_width}-bits memory-width.")


def validate_addresses(memory_width, first_address, last_address):
    if first_address % memory_width != 0 or last_address % memory_width != 0:
        raise FlipJumpAssemblerException(f'segment boundaries are unaligned: '
                                         f'[{hex(first_address)}, {hex(last_address - 1)}].')

    assert_address_in_memory(memory_width, first_address)
    assert_address_in_memory(memory_width, last_address)


def add_segment_to_fjm(memory_width: int,
                       fjm_writer: Writer,
                       first_address: int, last_address: int,
                       fj_words: List[int], wflip_words: List[int]) -> None:
    validate_addresses(memory_width, first_address, last_address)
    if first_address == last_address:
        return

    data_words = fj_words + wflip_words
    data_start = fjm_writer.add_data(data_words)

    segment_start_address = first_address // memory_width
    segment_length = (last_address - first_address) // memory_width

    try:
        fjm_writer.add_segment(segment_start_address, segment_length, data_start, len(data_words))
    except FlipJumpWriteFjmException as e:
        exception_message = (f"failed to add the segment: "
                             f"{fjm_writer.get_segment_addresses_repr(segment_start_address, segment_length)}.")
        raise FlipJumpAssemblerException(exception_message) from e

    fj_words.clear()
    wflip_words.clear()


@dataclasses.dataclass
class WFlipSpot:
    list: List[int]
    index: int
    address: int


class BinaryData:
    def __init__(self, memory_width: int, first_segment: NewSegment, labels: Dict[str, int]):
        self.memory_width = memory_width

        self.first_address = first_segment.start_address
        self.wflip_address = first_segment.wflip_start_address

        self.labels = labels
        self.wflips_so_far = 0

        self.current_address = self.first_address

        self.fj_words: List[int] = []
        self.wflip_words: List[int] = []

        self.padding_ops_indices: List[int] = []    # indices in self.fj_words

        # return_address -> { (f3, f2, f1, f0) -> start_flip_address }
        self.wflips_dict: Dict[int, Dict[Tuple[int, ...]]] = defaultdict(lambda: {})

    def get_wflip_spot(self) -> WFlipSpot:
        if self.padding_ops_indices:
            index = self.padding_ops_indices.pop()
            return WFlipSpot(self.fj_words, index, self.first_address + self.memory_width * index)

        wflip_spot = WFlipSpot(self.wflip_words, len(self.wflip_words), self.wflip_address)
        self.wflip_words += (0, 0)
        self.wflip_address += 2*self.memory_width
        return wflip_spot

    def close_and_add_segment(self, fjm_writer: Writer) -> None:
        add_segment_to_fjm(self.memory_width, fjm_writer, self.first_address, self.wflip_address, self.fj_words, self.wflip_words)

    def _insert_wflip_label(self, address: int):
        self.labels[f'{WFLIP_LABEL_PREFIX}{self.wflips_so_far}'] = address
        self.wflips_so_far += 1

    def insert_fj_op(self, flip: int, jump: int) -> None:
        self.fj_words += (flip, jump)
        self.current_address += 2*self.memory_width

    def insert_wflip_ops(self, word_address: int, flip_value: int, return_address: int) -> None:
        if 0 == flip_value:
            self.insert_fj_op(0, return_address)
        else:
            assert_address_in_memory(self.memory_width, flip_value)

            return_dict = self.wflips_dict[return_address]

            # this is the order of flip_addresses (tested with many other orders) that produces the best
            #  found-statistic for searching flip_bit[:i] with different i's in return_dict.
            flip_addresses = [word_address + i for i in range(self.memory_width) if flip_value & (1 << i)][::-1]

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
                    self._insert_wflip_label(wflip_spot.address)

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
        self.current_address += ops_count * (2 * self.memory_width)

    def insert_new_segment(self, fjm_writer: Writer, first_address: int, wflip_first_address: int) -> None:
        self.close_and_add_segment(fjm_writer)

        self.first_address = first_address
        self.wflip_address = wflip_first_address
        self.current_address = self.first_address

        self.padding_ops_indices.clear()

    def insert_reserve_bits(self, fjm_writer: Writer, new_first_address: int) -> None:
        add_segment_to_fjm(self.memory_width, fjm_writer, self.first_address, new_first_address, self.fj_words, [])

        self.first_address = new_first_address
        self.current_address = self.first_address

        self.padding_ops_indices.clear()


def labels_resolve(ops: Deque[LastPhaseOp], labels: Dict[str, int],
                   memory_width: int, fjm_writer: Writer) -> None:
    """
    resolve the labels and expressions to get the list of fj ops, and add all the data and segments into the fjm_writer.
    @param ops:[in]: the list ops returned from the preprocessor stage
    @param labels:[in]: dictionary from label to its resolved value
    @param memory_width: the memory-width
    @param fjm_writer: [out]: the .fjm file writer
    """
    first_segment: NewSegment = ops.popleft()
    if not isinstance(first_segment, NewSegment):
        raise FlipJumpAssemblerException(f"The first op must be of type NewSegment (and not {first_segment}).")

    binary_data = BinaryData(memory_width, first_segment, labels)

    for op in ops:
        if isinstance(op, FlipJump):
            try:
                binary_data.insert_fj_op(op.get_flip(labels), op.get_jump(labels))
            except FlipJumpException as e:
                raise FlipJumpAssemblerException(f"{e} in op {op}.")

        elif isinstance(op, WordFlip):
            try:
                binary_data.insert_wflip_ops(op.get_word_address(labels), op.get_flip_value(labels),
                                             op.get_return_address(labels))
            except FlipJumpException as e:
                raise FlipJumpAssemblerException(f"{e} in op {op}.")

        elif isinstance(op, Padding):
            binary_data.insert_padding(op.ops_count)

        elif isinstance(op, NewSegment):
            binary_data.insert_new_segment(fjm_writer, op.start_address, op.wflip_start_address)

        elif isinstance(op, ReserveBits):
            binary_data.insert_reserve_bits(fjm_writer, op.first_address_after_reserved)

        else:
            raise FlipJumpAssemblerException(f"Can't resolve/assemble the next opcode - {str(op)}")

    binary_data.close_and_add_segment(fjm_writer)


def assemble(input_files: List[Tuple[str, Path]], memory_width: int, fjm_writer: Writer, *,
             warning_as_errors: bool = True, debugging_file_path: Optional[Path] = None,
             show_statistics: bool = False, print_time: bool = True)\
        -> None:
    """
    runs the assembly pipeline. assembles the input files to a .fjm.
    :param input_files:[in]: a list of (short_file_name, fj_file_path). The files will to be parsed in that given order.
    :param memory_width: the memory-width
    :param fjm_writer:[out]: the .fjm file writer
    :param warning_as_errors: treat warnings as errors (stop execution on warnings)
    :param debugging_file_path:[out]: is specified, save debug information in this file
    :param show_statistics: if true shows macro-usage statistics
    :param print_time: if true prints the times of each assemble-stage
    """
    try:
        with PrintTimer('  parsing:         ', print_time=print_time):
            macros = parse_macro_tree(input_files, memory_width, warning_as_errors)

        with PrintTimer('  macro resolve:   ', print_time=print_time):
            ops, labels = resolve_macros(memory_width, macros, show_statistics=show_statistics)

        with PrintTimer('  labels resolve:  ', print_time=print_time):
            labels_resolve(ops, labels, memory_width, fjm_writer)

        with PrintTimer('  create binary:   ', print_time=print_time):
            fjm_writer.write_to_file()
            save_debugging_labels(debugging_file_path, labels)

    except FlipJumpException as fj_exception:
        raise fj_exception
    except Exception as unknown_exception:
        raise FlipJumpAssemblerException("Unknown exception during assembling the .fj files, please report this bug") \
            from unknown_exception

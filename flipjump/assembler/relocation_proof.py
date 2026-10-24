"""
the relocation proof: a table pool's program does what the program without the pool does, op for op.

It does not trust the pool. It expands the program twice, without and with the pool, with no label folded into a
number, and maps every op of the plain program to the pooled one: a moved op by the label before it in the pool
(labels keep their names), every other op in order. Then it checks what a wrong move or a wrong pin breaks:
    - every moved op is an op of a declared table (preprocessor.relocatable_call), and a declared table moves
      whole: all its ops by one distance, or none;
    - every operand that is an address - one label plus a constant - is the plain operand mapped, so an offset
      from an outside label into a moved table fails. A number is a value and is not compared. An operand
      computed from labels in any other way (`(ptr >> 8) & 15`) is not compared either - it is counted as
      unchecked - unless it names a label of a moved table: then it fails, since nothing can check it;
    - (BlockPool) every pinned word rests at its value xor its base, and every wflip of it flips an address
      xor the base and a number as it is - read back from the assembled words, wflip chains included.
"""

from __future__ import annotations

import bisect
import dataclasses
from array import array
from pathlib import Path
from typing import Callable, Dict, Iterator, List, Optional, Set, Tuple, Union

from flipjump.assembler.assembler import labels_resolve, resolve_pinned
from flipjump.assembler.inner_classes.expr import Expr
from flipjump.assembler.inner_classes.ops import FlipJump, Macro, MacroName, NewSegment, Padding, ReserveBits, WordFlip
from flipjump.assembler.inner_classes.op_stream import OpStream, linear_sum
from flipjump.assembler.preprocessor import resolve_macros
from flipjump.assembler.table_pool import TablePool
from flipjump.fjm.fjm_consts import FJMVersion
from flipjump.fjm.fjm_writer import Writer

_Op = Union[FlipJump, WordFlip]


@dataclasses.dataclass
class RelocationProof:
    """the proof's findings: every mismatch fails it; `unchecked` counts the operands it could not compare (values
    computed from labels that no moved table owns)"""

    mismatches: List[str]
    unchecked: int


def _ops(stream: OpStream, memory_width: int) -> Iterator[Tuple[int, Optional[_Op]]]:
    """(address, op) of every op in stream order, and (its start, None) where a segment starts"""
    op_bits = 2 * memory_width
    address = 0
    for op in stream.iter_ops():
        if isinstance(op, NewSegment):
            address = op.start_address
            yield address, None
        elif isinstance(op, ReserveBits):
            address = op.first_address_after_reserved
        elif isinstance(op, Padding):
            address += op.ops_count * op_bits
        else:
            yield address, op
            address += op_bits


def _operands(op: _Op) -> Tuple[Expr, ...]:
    if isinstance(op, FlipJump):
        return op.flip, op.jump
    return op.word_address, op.flip_value, op.return_address


def _is_one_address(operand: Expr) -> bool:
    """one label plus a constant: an address the pool may move"""
    linear = linear_sum(operand)
    return linear is not None and linear[0] is not None


class _Shifts:
    """runs of plain op addresses [start, end), each moved by one delta"""

    def __init__(self) -> None:
        self.starts = array('Q')
        self.ends = array('Q')
        self.deltas: List[int] = []

    def add(self, address: int, delta: int, op_bits: int) -> None:
        if self.starts and self.ends[-1] == address and self.deltas[-1] == delta:
            self.ends[-1] = address + op_bits
        else:
            self.starts.append(address)
            self.ends.append(address + op_bits)
            self.deltas.append(delta)

    def delta(self, address: int) -> Optional[int]:
        index = bisect.bisect_right(self.starts, address) - 1
        if index >= 0 and address < self.ends[index]:
            return self.deltas[index]
        return None


class _Image:
    """the words a Writer holds, read by bit address"""

    def __init__(self, writer: Writer, memory_width: int):
        self.memory_width = memory_width
        self.segments = sorted(writer.segments)
        self.starts = [segment[0] for segment in self.segments]
        self.data = writer.data

    def word(self, address: int) -> Optional[int]:
        index = address // self.memory_width
        position = bisect.bisect_right(self.starts, index) - 1
        if position < 0:
            return None
        start, length, data_start, data_length = self.segments[position]
        if index >= start + length:
            return None
        return self.data[data_start + index - start] if index - start < data_length else 0


def prove_relocation(
    memory_width: int, macros: Dict[MacroName, Macro], table_pool: TablePool, *, max_reported: int = 20
) -> RelocationProof:
    """
    expand `macros` without a pool and with `table_pool` (a fresh one, as for any assembly), and compare the two
    programs op by op (see the module docstring). A refusal of the pool's own (a pin it cannot hold) is raised.
    @return: the proof: up to max_reported mismatches, each naming the plain op's address and the label before
    it, and how many operands could not be compared
    """
    op_bits = 2 * memory_width
    extents: List[Tuple[int, int]] = []
    plain_stream, plain_labels = resolve_macros(
        memory_width, macros, save_debug_labels=False, fold_labels=False, relocatable_extents=extents
    )
    pooled_stream, pooled_labels = resolve_macros(
        memory_width, macros, save_debug_labels=False, fold_labels=False, table_pool=table_pool
    )
    pool_start = table_pool.pool_start()
    mismatches: List[str] = []

    def mismatch(text: str) -> None:
        if len(mismatches) < max_reported:
            mismatches.append(text)

    plain_by_address = sorted((address, name) for name, address in plain_labels.items())
    label_addresses = [address for address, _ in plain_by_address]

    def where(address: int) -> str:
        index = bisect.bisect_right(label_addresses, address) - 1
        if index < 0:
            return hex(address)
        label_address, name = plain_by_address[index]
        return f'{hex(address)} ({name} + {(address - label_address) // op_bits} ops)'

    extents.sort()
    extent_starts = [start for start, _ in extents]

    def extent_of(address: int) -> int:
        """the index of the declared table holding the plain op at `address`, or -1"""
        index = bisect.bisect_right(extent_starts, address) - 1
        return index if index >= 0 and address < extents[index][1] else -1

    # the moved ops, each at the plain address the pool label before it gives
    moved_labels = {name for name, address in pooled_labels.items() if address >= pool_start}
    pool_labels = sorted((pooled_labels[name], name) for name in moved_labels)
    pool_label_addresses = [address for address, _ in pool_labels]
    moved: Dict[int, Tuple[int, _Op]] = {}  # plain address -> (pooled address, op)
    for pooled_address, op_in_pool in _ops(pooled_stream, memory_width):
        if op_in_pool is None or pooled_address < pool_start:
            continue
        index = bisect.bisect_right(pool_label_addresses, pooled_address) - 1
        if index < 0 or pool_labels[index][1] not in plain_labels:
            mismatch(f'the pooled op at {hex(pooled_address)} follows no label of the plain program')
            continue
        label = pool_labels[index][1]
        plain_address = plain_labels[label] + pooled_address - pooled_labels[label]
        if extent_of(plain_address) < 0:
            mismatch(f'the plain op at {where(plain_address)} moved, and it is no op of a declared table')
        moved[plain_address] = (pooled_address, op_in_pool)

    def pooled_inline() -> Iterator[Tuple[int, _Op]]:
        for address, op in _ops(pooled_stream, memory_width):
            if op is not None and address < pool_start:
                yield address, op

    # the other ops pair up in order; a declared table moves whole
    shifts = _Shifts()
    inline = pooled_inline()
    extent_deltas: Dict[int, int] = {}
    moved_seen = 0
    for plain_address, op in _ops(plain_stream, memory_width):
        if op is None:
            continue
        if plain_address in moved:
            moved_seen += 1
            delta = moved[plain_address][0] - plain_address
        else:
            pooled = next(inline, None)
            if pooled is None:
                mismatch(f'the plain op at {where(plain_address)} has no op in the pooled program')
                break
            delta = pooled[0] - plain_address
        shifts.add(plain_address, delta, op_bits)
        extent = extent_of(plain_address)
        if extent >= 0 and extent_deltas.setdefault(extent, delta) != delta:
            mismatch(f'the declared table at {where(extents[extent][0])} moved in pieces')
    if moved_seen != len(moved):
        mismatch(f'{len(moved) - moved_seen} moved ops are no op of the plain program')
    extra = sum(1 for _ in inline)
    if extra:
        mismatch(f'the pooled program has {extra} inline ops more than the plain one')

    deltas_at: Dict[int, Set[int]] = {}
    for name, address in plain_labels.items():
        deltas_at.setdefault(address, set()).add(pooled_labels.get(name, address) - address)

    def mapped(value: int) -> Set[int]:
        """where a plain address is with the pool: its op's place, else the labels' at the address before it
        (a `reserve`d region, a label at a moved table's place - the table's or the code after it), else unmoved"""
        delta = shifts.delta(value - value % op_bits)
        if delta is not None:
            return {value + delta}
        index = bisect.bisect_right(label_addresses, value) - 1
        if index < 0:
            return {value}
        return {value + delta for delta in deltas_at[label_addresses[index]]}

    # the pins: a pin the pool cannot hold is refused here, as when assembling
    table_pool.labels_resolved(pooled_labels)
    pinned, _ = resolve_pinned(table_pool.pinned_words(), pooled_labels, exclude=table_pool.pin_exclude)

    # every operand that is an address maps
    unchecked = 0
    inline = pooled_inline()
    pairs: List[Tuple[_Op, int, _Op]] = []  # (plain op, pooled address, pooled op) of the pin check
    for plain_address, op in _ops(plain_stream, memory_width):
        if op is None:
            continue
        if plain_address in moved:
            pooled_address, pooled_op = moved[plain_address]
        else:
            next_inline = next(inline, None)
            if next_inline is None:
                break
            pooled_address, pooled_op = next_inline
        if type(pooled_op) is not type(op):
            mismatch(f'the plain op at {where(plain_address)} is {op}, the pooled one {pooled_op}')
            continue
        if pinned and _touches_a_pin(pooled_address, pooled_op, pooled_labels, pinned, memory_width):
            pairs.append((op, pooled_address, pooled_op))
        for plain_operand, pooled_operand in zip(_operands(op), _operands(pooled_op)):
            named = plain_operand.all_unknown_labels()
            if not named:
                continue  # a number: a value
            if not _is_one_address(plain_operand):
                if named & moved_labels:
                    mismatch(
                        f'the plain op at {where(plain_address)} ({op}): {plain_operand} computes from '
                        f'{sorted(named & moved_labels)[0]}, a label of a moved table, so it cannot be checked'
                    )
                else:
                    unchecked += 1
                continue
            expected = mapped(plain_operand.exact_eval(plain_labels))
            actual = pooled_operand.exact_eval(pooled_labels)
            if actual not in expected:
                mismatch(
                    f'the plain op at {where(plain_address)} ({op}): {plain_operand} should be '
                    f'{" or ".join(hex(v) for v in sorted(expected))} with the pool, and is {hex(actual)}'
                )

    if pinned:
        _check_pins(memory_width, pooled_stream, pooled_labels, pinned, pool_start, pairs, mismatch)
    return RelocationProof(mismatches, unchecked)


def _check_pins(
    memory_width: int,
    stream: OpStream,
    labels: Dict[str, int],
    pinned: Dict[int, int],
    pool_start: int,
    pairs: List[Tuple[_Op, int, _Op]],
    mismatch: Callable[[str], None],
) -> None:
    """the assembled words of the pinned program: each pinned word rests at its value xor its base, and each wflip
    of it flips the plain value's kind - an address xor the base, a number as it is"""
    writer = Writer(Path('relocation_proof.fjm'), memory_width, FJMVersion.NormalVersion)
    labels_resolve(stream, labels, memory_width, writer, save_wflip_labels=False, pinned=pinned, pool_start=pool_start)
    image = _Image(writer, memory_width)
    rested = set()
    for plain_op, address, pooled_op in pairs:
        if isinstance(pooled_op, FlipJump):
            base = pinned.get(address + memory_width)
            if base is None:
                continue
            rested.add(address + memory_width)
            expected = pooled_op.jump.exact_eval(labels) ^ base
            if image.word(address + memory_width) != expected:
                mismatch(f'the pinned word at {hex(address + memory_width)} does not rest at its value xor its base')
            continue
        assert isinstance(pooled_op, WordFlip) and isinstance(plain_op, WordFlip)
        word = pooled_op.word_address.exact_eval(labels)
        base = pinned.get(word)
        if base is None:
            continue
        value = pooled_op.flip_value.exact_eval(labels)
        if plain_op.flip_value.all_unknown_labels():
            if not _is_one_address(plain_op.flip_value):
                mismatch(f'the pinned word at {hex(word)} is wflipped by {plain_op.flip_value}, computed from labels')
                continue
            value ^= base
        flipped = _flipped(image, address, pooled_op.return_address.exact_eval(labels), memory_width)
        if flipped is None or flipped != _bits(value, word, memory_width):
            mismatch(f'the wflip at {hex(address)} of the pinned word at {hex(word)} does not flip {hex(value)}')
    for word in sorted(set(pinned) - rested)[:3]:
        mismatch(f'the pinned word at {hex(word)} is no op: it cannot rest at its base')


def _touches_a_pin(address: int, op: _Op, labels: Dict[str, int], pinned: Dict[int, int], memory_width: int) -> bool:
    """is the op a pinned word's own op, or a wflip of a pinned word?"""
    if isinstance(op, FlipJump):
        return address + memory_width in pinned
    return op.word_address.exact_eval(labels) in pinned


def _bits(value: int, word: int, memory_width: int) -> Set[int]:
    return {word + bit for bit in range(memory_width) if value >> bit & 1}


def _flipped(image: _Image, address: int, return_address: int, memory_width: int) -> Optional[Set[int]]:
    """the bits the wflip chain at `address` flips, followed until it jumps to `return_address` (None: it does not)"""
    flipped: Set[int] = set()
    for _ in range(memory_width + 1):
        flip, jump = image.word(address), image.word(address + memory_width)
        if flip is None or jump is None:
            return None
        if flip:
            flipped ^= {flip}
        if jump == return_address:
            return flipped
        address = jump
    return None

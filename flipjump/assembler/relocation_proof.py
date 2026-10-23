"""
the relocation proof: a table pool's program does what the program without the pool does, op for op.

It does not trust the pool. It expands the program twice, without and with the pool, and maps every op of the
plain program to the pooled one: a moved op by the label before it in the pool (labels keep their names), every
other op in order. Then it checks the two things a wrong move breaks:
    - an op moves with the label before it in its segment, so a jump computed from a label (a table dispatch,
      `label + k*dw`) still lands on the op it did - an op cut off its table, or a table taken too long, fails;
    - every operand that is an address (flip, jump, and a wflip's word, value and return address) is the plain
      operand mapped - an offset from an outside label that reaches into a moved table fails. A value computed
      from an address (`(ptr >> 8) & 15`, a pointer's digit) changes with the code and is not compared; a
      number is compared as an address.
The comparison is of the op stream, before labels-resolve builds the wflip chains and writes BlockPool's pins.
"""

from __future__ import annotations

import bisect
from array import array
from typing import Dict, Iterator, List, Optional, Set, Tuple, Union

from flipjump.assembler.inner_classes.expr import Expr
from flipjump.assembler.inner_classes.ops import FlipJump, Macro, MacroName, NewSegment, Padding, ReserveBits, WordFlip
from flipjump.assembler.inner_classes.op_stream import OpStream
from flipjump.assembler.preprocessor import resolve_macros
from flipjump.assembler.table_pool import TablePool

_Op = Union[FlipJump, WordFlip]


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


def _is_an_address(operand: Expr) -> bool:
    """is the operand a number, a label, or a sum of them (an address the pool may move), not a value
    computed from an address (`(ptr >> 8) & 15`)?"""
    value = operand.value
    if not isinstance(value, tuple):
        return True
    op, args = value
    return op in ('+', '-') and all(_is_an_address(arg) for arg in args)


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


def relocation_mismatches(
    memory_width: int, macros: Dict[MacroName, Macro], table_pool: TablePool, *, max_reported: int = 20
) -> List[str]:
    """
    expand `macros` without a pool and with `table_pool`, and compare the two programs op by op (see the module
    docstring). The pool must be a fresh one, as for any assembly.
    @return: up to max_reported mismatches, each naming the plain op's address and the label before it (none: the
    pooled program is the plain one, moved)
    """
    op_bits = 2 * memory_width
    plain_stream, plain_labels = resolve_macros(memory_width, macros, save_debug_labels=False)
    pooled_stream, pooled_labels = resolve_macros(memory_width, macros, save_debug_labels=False, table_pool=table_pool)
    overflow_base: Optional[int] = getattr(table_pool, 'overflow_base', None)
    pool_start = table_pool.pool_base if overflow_base is None else min(table_pool.pool_base, overflow_base)
    mismatches: List[str] = []

    def mismatch(text: str) -> None:
        if len(mismatches) < max_reported:
            mismatches.append(text)

    # the plain labels in address order: an op's region, and its name in a message
    plain_by_address = sorted((address, name) for name, address in plain_labels.items())
    label_addresses = [address for address, _ in plain_by_address]

    def where(address: int) -> str:
        index = bisect.bisect_right(label_addresses, address) - 1
        if index < 0:
            return hex(address)
        label_address, name = plain_by_address[index]
        return f'{hex(address)} ({name} + {(address - label_address) // op_bits} ops)'

    # the moved ops, each at the plain address the pool label before it gives
    pool_labels = sorted((address, name) for name, address in pooled_labels.items() if address >= pool_start)
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
        moved[plain_labels[label] + pooled_address - pooled_labels[label]] = (pooled_address, op_in_pool)

    def pooled_inline() -> Iterator[Tuple[int, _Op]]:
        for address, op in _ops(pooled_stream, memory_width):
            if op is not None and address < pool_start:
                yield address, op

    # the other ops pair up in order; each op moves with the label before it in its segment
    deltas_at: Dict[int, Set[int]] = {}
    for name, address in plain_labels.items():
        deltas_at.setdefault(address, set()).add(pooled_labels.get(name, address) - address)
    shifts = _Shifts()
    inline = pooled_inline()
    region: Optional[Set[int]] = None
    label_index = 0
    moved_seen = 0
    for plain_address, op in _ops(plain_stream, memory_width):
        if op is None:
            region = None  # a segment starts: the labels before it govern nothing in it
            label_index = bisect.bisect_left(label_addresses, plain_address)
            continue
        while label_index < len(label_addresses) and label_addresses[label_index] <= plain_address:
            region = deltas_at[label_addresses[label_index]]
            label_index += 1
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
        if region is not None and delta not in region:
            mismatch(f'the plain op at {where(plain_address)} moved apart from the label before it')
    if moved_seen != len(moved):
        mismatch(f'{len(moved) - moved_seen} moved ops are no op of the plain program')
    extra = sum(1 for _ in inline)
    if extra:
        mismatch(f'the pooled program has {extra} inline ops more than the plain one')

    def mapped(value: int) -> Set[int]:
        """where a plain address may be with the pool: its op's, else the labels' at it (one at a moved table's
        place can be the table's or the inline code's), else unmoved"""
        delta = shifts.delta(value - value % op_bits)
        if delta is not None:
            return {value + delta}
        return {value + delta for delta in deltas_at.get(value, {0})}

    # every operand maps
    inline = pooled_inline()
    for plain_address, op in _ops(plain_stream, memory_width):
        if op is None:
            continue
        if plain_address in moved:
            pooled_op: Optional[_Op] = moved[plain_address][1]
        else:
            pooled_op = next(inline, (0, None))[1]
            if pooled_op is None:
                break
        if type(pooled_op) is not type(op):
            mismatch(f'the plain op at {where(plain_address)} is {op}, the pooled one {pooled_op}')
            continue
        for plain_operand, pooled_operand in zip(_operands(op), _operands(pooled_op)):
            if not _is_an_address(plain_operand):
                continue
            expected = mapped(plain_operand.exact_eval(plain_labels))
            actual = pooled_operand.exact_eval(pooled_labels)
            if actual not in expected:
                mismatch(
                    f'the plain op at {where(plain_address)} ({op}): {plain_operand} should be '
                    f'{" or ".join(hex(v) for v in sorted(expected))} with the pool, and is {hex(actual)}'
                )
    return mismatches

"""
unit-tests for the assembler's table placement: TablePool (relocate lookup tables to
low-popcount addresses), BlockPool (group the tables dispatched through one jump word into an
aligned block, so the arming wflip writes an index instead of an address), the table detector
(relocatable_table_end) and the pin resolver (assembler.resolve_pinned).

the property pinned throughout: a relocated or blocked program produces the SAME output as the
inline one, in fewer ops - a table is reached only by jump, so its address is free to choose.

a placing BlockPool's census (what it met, in the shape the next placing pool takes) must equal a
counting pass's report on the same program, and stale counts may cost ops but never correctness.
"""

import json
from itertools import islice
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import pytest

from flipjump import assemble
from flipjump.assembler.assembler import resolve_pinned
from flipjump.assembler.inner_classes.expr import Expr
from flipjump.assembler.inner_classes.ops import CodePosition, FlipJump, Label, MacroName, Op, Pad, WordFlip
from flipjump.assembler.preprocessor import (
    DECLINE_INHERENT,
    DECLINE_STALE,
    RESERVED_BELOW,
    BlockCensus,
    BlockPool,
    PreprocessorData,
    TablePool,
    heat_key,
    merge_aliased_groups,
    relocatable_table_end,
)
from flipjump.assembler.fj_parser import parse_macro_tree
from flipjump.assembler.preprocessor import resolve_macros
from flipjump.fjm.fjm_reader import Reader
from flipjump.interpreter import fjm_run
from flipjump.interpreter.io_devices.FixedIO import FixedIO
from flipjump.utils.constants import DEFAULT_MAX_MACRO_RECURSION_DEPTH
from flipjump.utils.exceptions import FlipJumpException, FlipJumpPreprocessorException
from flipjump.utils.functions import get_file_tuples

W = 32
OP_BITS = 2 * W
POOL_BASE = 1 << 26  # above everything the programs below reach
CODE_POSITION = CodePosition('file.fj', 'f1', 1)

XOR_PROGRAM = """
stl.startup_and_init_all
    hex.set 4, a, 0x1234
    hex.set 4, b, 0x5678
    rep(24, i) hex.xor 4, a, b
    hex.print_uint 4, a, 1, 1
    stl.loop
a: hex.vec 4
b: hex.vec 4
"""

CMP_PROGRAM = """
stl.startup_and_init_all
    hex.set 4, a, 0x00F5
    hex.set 4, b, 0x0031
    rep(6, i) hex.shl_bit 4, a
    rep(2, i) hex.shr_hex 4, a
    hex.mul 4, r, a, b
    hex.cmp 4, r, b, LT, EQ, GT
LT:
    hex.print_uint 4, r, 1, 1
    ;done
EQ:
    hex.print_uint 4, b, 1, 1
    ;done
GT:
    hex.print_uint 4, a, 1, 1
done:
    stl.loop
a: hex.vec 4
b: hex.vec 4
r: hex.vec 4
"""

# hex.input_hex's table has a `wflip` ENTRY (`flip3: wflip stl.IO+w, flip3, end`): the run of plain
# ops before it is not a table, and a pass that moves them away from it miscompiles every input
INPUT_PROGRAM = """
stl.startup_and_init_all
    hex.input b
    hex.print_uint 2, b, 1, 1
    stl.loop
b: hex.vec 2
"""

# `hex.xor e, d` arms d's jump word, so BlockPool pins d; the pointer read of d then jumps
# through that word expecting `value*dw` and lands in the block instead of the decoder
POINTER_PROGRAM = """
stl.startup_and_init_all
    hex.set d, 6
    hex.xor e, d
    hex.set v, 0xD
    hex.xor_hex_from_ptr v, p
    hex.print_as_digit v, 1
    stl.loop
d: hex.hex
e: hex.hex
v: hex.hex
p: hex.vec w/4, d
"""

# bit.exact_xor's table ends in `dst;` - a fall-through into the next op - so it must be refused
FALL_THROUGH_PROGRAM = """
stl.startup_and_init_all
    rep(16, i) bit.xor a+i*dw, b+i*dw
    bit.print 8, a
    stl.loop
a: bit.vec 16, 0x4A4B
b: bit.vec 16, 0x0102
"""


# every hex digit appears once, so each shift reaches all 16 entries of both of its tables
SHIFT_PROGRAM = """
stl.startup_and_init_all
    hex.shl_bit 16, a
    hex.shr_bit 16, b
    hex.print_as_digit 16, a, 0
    hex.print_as_digit 16, b, 0
    stl.loop
a: hex.vec 16, 0xFEDCBA9876543210
b: hex.vec 16, 0xFEDCBA9876543210
"""
SHIFT_MACROS = frozenset({'hex.shifts.shl_bit_once', 'hex.shifts.shr_bit_once'})


# --- helpers ---


def build_and_run(
    source: str,
    tmp_path: Path,
    pool: Optional[TablePool],
    name: str = 'p',
    fixed_input: bytes = b'',
    memory_width: int = W,
) -> Tuple[bytes, int, Path]:
    """assemble `source` with the stl (and the pool, if given), run it on `fixed_input`, and
    return (output, op count, fjm path)."""
    fj_path = tmp_path / f'{name}.fj'
    fj_path.write_text(source)
    fjm_path = tmp_path / f'{name}.fjm'
    assemble([fj_path], fjm_path, memory_width=memory_width, print_time=False, table_pool=pool)
    io_device = FixedIO(fixed_input)
    statistics = fjm_run.run(fjm_path, io_device=io_device, print_time=False)
    return io_device.get_output(allow_incomplete_output=True), statistics.op_counter, fjm_path


def pool_segments(fjm_path: Path, memory_width: int = W) -> List[int]:
    """the word addresses of the segments that landed in the pool"""
    reader = Reader(fjm_path)
    return [s.segment_start for s in reader.memory_segments if s.segment_start * memory_width >= POOL_BASE]


def blocked(source: str, tmp_path: Path, span_bits: Optional[int] = None) -> Tuple[bytes, int, BlockPool]:
    """the two-pass blocking build: count, then place with the frozen counts"""
    counting = BlockPool(W, POOL_BASE, span_bits=span_bits)
    build_and_run(source, tmp_path, counting, name='counting')
    placing = BlockPool(W, POOL_BASE, counts=counting.counts, widths=counting.widths, span_bits=span_bits)
    output, ops, _ = build_and_run(source, tmp_path, placing, name='placing')
    return output, ops, placing


def _flipjump(jump: str) -> FlipJump:
    return FlipJump(Expr('d0'), Expr(jump), CODE_POSITION)


def _table_ops(entries: int, *, interior_label: bool = False, trailing_label: bool = True) -> List[Op]:
    """the shape of a dispatch table in a macro body: the arm, pad, switch:, entries, [end:], the
    disarm"""
    ops: List[Op] = [
        WordFlip(Expr('src_word'), Expr('switch'), Expr('src'), CODE_POSITION),
        Pad(Expr(16), CODE_POSITION),
        Label('switch', CODE_POSITION),
    ]
    for i in range(entries):
        if interior_label and i == entries // 2:
            ops.append(Label('mid', CODE_POSITION))
        ops.append(_flipjump('end'))
    if trailing_label:
        ops.append(Label('end', CODE_POSITION))
    ops.append(WordFlip(Expr('src_word'), Expr('switch'), Expr('end'), CODE_POSITION))
    return ops


# --- TablePool ---


def test_offsets_are_handed_out_cheapest_popcount_first() -> None:
    pool = TablePool(W, POOL_BASE, run_ops=16, span_bits=16 * OP_BITS * 64)
    offsets = list(islice(pool._cheapest_offsets(), 100))
    assert offsets[:8] == [0, 1, 2, 4, 8, 16, 32, 3]
    assert sorted(offsets) == list(range(64))
    assert offsets == sorted(range(64), key=lambda v: (bin(v).count('1'), v))


def test_offsets_are_generated_lazily_so_w64_works() -> None:
    # an unbounded pool at w=64 has 2^49 run offsets; they are never materialised
    pool = TablePool(64, 1 << 40)
    assert pool.reserve(16, 16) == (1 << 40, True, 0)
    pool.commit((1 << 40) + 16 * 128)
    blocked_pool = BlockPool(64, 1 << 40, counts={'g': 2}, widths={'g': 16})
    assert blocked_pool.reserve(16, 16, group='g', group_expr=Expr('g')) == (1 << 40, True, 0)


def test_run_ops_must_make_a_power_of_two_run() -> None:
    with pytest.raises(ValueError):
        TablePool(W, POOL_BASE, run_ops=24)


def test_reserve_opens_a_run_then_aligns_inside_it() -> None:
    pool = TablePool(W, POOL_BASE, run_ops=256)
    assert pool.reserve(16, 16) == (POOL_BASE, True, 0)
    pool.commit(POOL_BASE + 16 * OP_BITS)
    assert pool.reserve(4, 4) == (POOL_BASE + 16 * OP_BITS, False, 0)
    pool.commit(POOL_BASE + 20 * OP_BITS)
    # the next 16-aligned spot is op 32 of the run: 12 ops of gap the caller must emit as padding
    assert pool.reserve(16, 16) == (POOL_BASE + 32 * OP_BITS, False, 12)
    assert pool.allocated == 3 and pool.declined == 0


def test_a_table_wider_than_a_run_claims_consecutive_slots() -> None:
    pool = TablePool(W, POOL_BASE, run_ops=256)
    assert pool.reserve(16, 16) == (POOL_BASE, True, 0)
    pool.commit(POOL_BASE + 16 * OP_BITS)
    run_bits = 256 * OP_BITS
    # 300 ops do not fit the 240 left in run 0, nor a single run: slots 1 and 2 are taken together
    assert pool.reserve(16, 300) == (POOL_BASE + run_bits, True, 0)
    pool.commit(POOL_BASE + run_bits + 300 * OP_BITS)
    assert pool._consumed == {0, 1, 2}
    # the next new run skips the claimed slots
    assert pool.reserve(16, 256) == (POOL_BASE + 4 * run_bits, True, 0)


def test_reserve_declines_when_the_pool_is_full() -> None:
    pool = TablePool(W, POOL_BASE, run_ops=16, span_bits=16 * OP_BITS)  # room for exactly one run
    assert pool.reserve(16, 16) == (POOL_BASE, True, 0)
    pool.commit(POOL_BASE + 16 * OP_BITS)
    assert pool.reserve(16, 16) is None
    assert pool.declined == 1


def test_commit_past_the_reserved_run_raises() -> None:
    pool = TablePool(W, POOL_BASE, run_ops=16)
    pool.reserve(16, 16)
    with pytest.raises(FlipJumpPreprocessorException):
        pool.commit(POOL_BASE + 32 * OP_BITS)


def test_wants_honours_the_capacity_and_the_callback() -> None:
    name = MacroName('exact_xor', 5)
    assert TablePool(W, POOL_BASE).wants(name)
    capped = TablePool(W, POOL_BASE, capacity=1)
    assert capped.wants(name)
    capped.reserve(16, 16)
    assert not capped.wants(name)
    picky = TablePool(W, POOL_BASE, wants=lambda macro_name, labels_prefix: labels_prefix.startswith('hot'))
    assert picky.wants(name, 'hot---site') and not picky.wants(name, 'cold---site')


def test_a_plain_pool_pins_nothing() -> None:
    assert TablePool(W, POOL_BASE).pinned_words() == {}


# --- relocatable_table_end ---


def test_table_end_trims_the_trailing_label_and_names_the_source_word() -> None:
    ops = _table_ops(16)
    found = relocatable_table_end(ops, 1)
    assert found is not None
    end_index, count, source_word = found
    assert end_index == 18 and count == 16  # arm, pad, switch:, then 16 entries; `end:` stays inline
    assert isinstance(ops[end_index], FlipJump) and isinstance(ops[end_index + 1], Label)
    assert str(source_word) == 'src_word'


def test_table_end_keeps_an_interior_label_inside_the_table() -> None:
    ops = _table_ops(8, interior_label=True)
    found = relocatable_table_end(ops, 1)
    assert found is not None
    assert found[1] == 8
    after_table = ops[found[0] + 1]
    assert isinstance(after_table, Label) and after_table.name == 'end'


def test_table_end_refuses_a_fall_through_entry() -> None:
    ops = _table_ops(4)
    ops[4] = FlipJump(Expr('d0'), Expr('$'), CODE_POSITION)  # `d0;` continues to the next address
    assert relocatable_table_end(ops, 1) is None


def test_table_end_needs_at_least_one_entry() -> None:
    ops = _table_ops(0)
    assert relocatable_table_end(ops, 1) is None


def test_table_end_refuses_a_wflip_that_is_not_the_disarm() -> None:
    # hex.input_hex's shape: flip0: entries, flip1: entries, flip3: `wflip stl.IO+w, flip3, end`
    ops = _table_ops(4)
    ops[6:6] = [Label('flip3', CODE_POSITION), WordFlip(Expr('src_word'), Expr('flip3'), Expr('end'), CODE_POSITION)]
    assert relocatable_table_end(ops, 1) is None
    # and a run whose only label is the head, ended by a wflip of something else entirely
    ops = _table_ops(4, trailing_label=False)
    ops[-1] = WordFlip(Expr('other_word'), Expr('elsewhere'), Expr('end'), CODE_POSITION)
    assert relocatable_table_end(ops, 1) is None


def test_table_end_accepts_a_run_that_simply_ends() -> None:
    # hex.cmp's second table: entries and interior labels, then the macro body ends
    ops = _table_ops(3, interior_label=True, trailing_label=False)[:-1]
    found = relocatable_table_end(ops, 1)
    assert found is not None and found[1] == 3 and found[2] is None


def test_table_end_refuses_a_pad_that_is_fallen_into() -> None:
    ops = _table_ops(4)
    ops[0] = FlipJump(Expr('d0'), Expr('$'), CODE_POSITION)  # `d0;` before the pad walks into it
    assert relocatable_table_end(ops, 1) is None
    ops[0] = WordFlip(Expr('src_word'), Expr('switch'), Expr('$'), CODE_POSITION)  # a 2-arg wflip does too
    assert relocatable_table_end(ops, 1) is None
    ops[0] = Label('before', CODE_POSITION)  # nothing but labels before the pad: reached from outside
    assert relocatable_table_end(ops, 1) is None
    assert relocatable_table_end(_table_ops(4)[1:], 0) is None


# --- resolve_pinned ---


def _sum(label: str, value: Union[int, str]) -> Expr:
    return Expr(('+', (Expr(label), Expr(value))))


def test_resolve_pinned_resolves_each_word_once_labels_are_known() -> None:
    pinned, conflicts = resolve_pinned({_sum('x', 32): 0x1000, Expr('y'): 0x2000}, {'x': 4096, 'y': 8192})
    assert pinned == {4128: 0x1000, 8192: 0x2000} and conflicts == 0


def test_resolve_pinned_drops_both_pins_of_an_aliased_word() -> None:
    # `(x + 32)` and `(x + w)` are different expressions naming one word; either base is wrong
    # for the other block, so the word is left un-pinned (the full address is then written)
    pinned, conflicts = resolve_pinned({_sum('x', 32): 0x1000, _sum('x', 'w'): 0x2000}, {'x': 4096, 'w': 32})
    assert pinned == {} and conflicts == 1


def test_resolve_pinned_keeps_an_alias_with_one_base() -> None:
    pinned, conflicts = resolve_pinned({_sum('x', 32): 0x1000, _sum('x', 'w'): 0x1000}, {'x': 4096, 'w': 32})
    assert pinned == {4128: 0x1000} and conflicts == 0


def test_resolve_pinned_skips_the_runtime_words_and_unresolvable_ones() -> None:
    pinned, _ = resolve_pinned({Expr(64): 0x1000, Expr('missing'): 0x2000, Expr('z'): 0x3000}, {'z': 1 << 20})
    assert pinned == {1 << 20: 0x3000}
    assert RESERVED_BELOW > 64  # stl.IO's word, which the runtime intercepts


def test_resolve_pinned_lets_the_caller_veto_a_word() -> None:
    pinned, _ = resolve_pinned(
        {Expr('a'): 1, Expr('b'): 2}, {'a': 4096, 'b': 8192}, exclude=lambda a, labels: a == 8192
    )
    assert pinned == {4096: 1}


# --- BlockPool, on synthetic reservations ---


def test_counting_pass_records_counts_widths_and_the_width_histogram() -> None:
    counting = BlockPool(W, POOL_BASE)
    for width in (16, 16, 31):
        assert counting.reserve(16, width, group='g', group_expr=Expr('g')) is None
    assert counting.counts == {'g': 3}
    assert counting.widths == {'g': 31}
    assert counting.width_hist == {'g': {16: 2, 31: 1}}
    assert counting.pinned_words() == {}  # nothing was placed, so nothing is pinned


def test_placing_pass_hands_out_slots_and_pins_the_word() -> None:
    placing = BlockPool(W, POOL_BASE, counts={'g': 3}, widths={'g': 16})
    slot_bits = 16 * OP_BITS
    word = Expr('g')
    assert [placing.reserve(16, 16, group='g', group_expr=word) for _ in range(3)] == [
        (POOL_BASE + i * slot_bits, True, 0) for i in range(3)
    ]
    assert placing.allocated == 3 and placing.declined == 0
    assert placing.pinned_words() == {word: POOL_BASE}


def test_more_tables_than_counted_decline_and_break_the_group() -> None:
    placing = BlockPool(W, POOL_BASE, counts={'g': 3}, widths={'g': 16})
    for _ in range(4):  # 3 counted -> 4 slots; the 5th has nowhere to go
        placing.reserve(16, 16, group='g', group_expr=Expr('g'))
    assert placing.reserve(16, 16, group='g', group_expr=Expr('g')) is None
    assert placing.declined_overflow == 1 and placing.broken_groups == {'g'}
    assert placing.pinned_words() == {}  # a broken group is never pinned...
    placing.pin_broken = True
    assert list(placing.pinned_words().values()) == [POOL_BASE]  # ...unless the caller opts in


def test_a_table_wider_than_its_slot_declines() -> None:
    placing = BlockPool(W, POOL_BASE, counts={'g': 2}, widths={'g': 16})
    assert placing.reserve(16, 40, group='g', group_expr=Expr('g')) is None
    assert placing.declined_too_wide == 1 and 'g' in placing.broken_groups


def test_an_uncounted_group_and_an_ungrouped_table_decline() -> None:
    placing = BlockPool(W, POOL_BASE, counts={'g': 2}, widths={'g': 16})
    assert placing.reserve(16, 16, group='other', group_expr=Expr('other')) is None
    assert placing.declined_no_block == 1
    assert placing.reserve(16, 16) is None
    assert placing.ungrouped == 1


def test_the_runtime_words_are_never_relocated() -> None:
    # `stl.IO` is a LABEL, declared by stl.startup before any code dispatches through it, so the
    # guard sees it resolved; a program variable, declared after the code, is not resolvable yet
    pool = TablePool(W, POOL_BASE)
    data = PreprocessorData(W, {}, DEFAULT_MAX_MACRO_RECURSION_DEPTH, table_pool=pool)
    data.labels['stl.IO'] = 64
    name = MacroName('exact_xor', 5)
    assert not data.begin_relocation(name, 16, 16, '', '(stl.IO + 32)', _sum('stl.IO', 32))
    assert pool.reserved_words == 1 and pool.allocated == 0
    assert data.begin_relocation(name, 16, 16, '', '(x + 32)', _sum('x', 32))
    assert pool.reserved_words == 1 and pool.allocated == 1


def test_sparse_indices_use_the_cheapest_slots_of_a_spread_block() -> None:
    placing = BlockPool(W, POOL_BASE, counts={'g': 300}, widths={'g': 16}, spread=2, spread_min_count=256)
    slot_bits = 16 * OP_BITS
    addresses = [placing.reserve(16, 16, group='g', group_expr=Expr('g'))[0] for _ in range(4)]  # type: ignore[index]
    assert addresses == [POOL_BASE + i * slot_bits for i in (0, 1, 2, 4)]


def test_width_buckets_give_each_width_its_own_sub_block() -> None:
    placing = BlockPool(
        W,
        POOL_BASE,
        counts={'g': 4},
        widths={'g': 64},
        width_hist={'g': {16: 3, 64: 1}},
        width_buckets=True,
        max_slot_ops=512,
    )
    layout, block_bits = placing._bucket_layout('g')
    assert layout == {64: (0, 1, 1), 16: (64 * OP_BITS, 4, 3)}
    assert block_bits == 2 * 64 * OP_BITS
    assert placing.reserve(16, 40, group='g', group_expr=Expr('g')) == (POOL_BASE, True, 0)
    assert placing.reserve(16, 16, group='g', group_expr=Expr('g')) == (POOL_BASE + 64 * OP_BITS, True, 0)
    assert placing.reserve(16, 200, group='g', group_expr=Expr('g')) is None  # a width never counted
    assert placing.declined_too_wide == 1


def test_eviction_drops_the_least_valuable_group_when_the_pool_is_short() -> None:
    kwargs = dict(counts={'a': 1, 'b': 3}, widths={'a': 16, 'b': 16}, span_bits=2 * 16 * OP_BITS)
    greedy = BlockPool(W, POOL_BASE, **kwargs)  # type: ignore[arg-type]
    assert greedy.evicted_low_value == 0 and greedy.broken_groups == {'b'}
    evicting = BlockPool(W, POOL_BASE, evict_by_value=True, **kwargs)  # type: ignore[arg-type]
    assert evicting.evicted_low_value == 1 and evicting.broken_groups == {'b'}
    assert set(evicting.groups) == {'a'}


def test_canonical_alias_merges_groups_that_name_one_word() -> None:
    counting = BlockPool(W, POOL_BASE)
    counting.reserve(16, 16, group='(x + 32)', group_expr=_sum('x', 32))
    counting.reserve(16, 16, group='(x + w)', group_expr=_sum('x', 'w'))
    counting.reserve(16, 16, group='y', group_expr=Expr('y'))
    assert counting.canonical_alias({'x': 4096, 'w': 32, 'y': 8192}) == {'(x + w)': '(x + 32)'}
    merged = BlockPool(W, POOL_BASE, alias={'(x + w)': '(x + 32)'})
    merged.reserve(16, 16, group='(x + w)', group_expr=_sum('x', 'w'))
    assert merged.counts == {'(x + 32)': 1}


# --- pin protection: BlockPool(heat=...) ---


def _place(pool: BlockPool, sites: List[str], width: int = 16) -> Dict[str, int]:
    """{site path: slot index} for tables of `width` ops reserved in this order, all in group 'g'"""
    base = pool.groups['g'][0]
    out = {}
    for site in sites:
        reserved = pool.reserve(16, width, group='g', group_expr=Expr('g'), labels_prefix=site)
        assert reserved is not None
        out[site] = (reserved[0] - base) // (16 * OP_BITS)
    return out


def test_heat_key_strips_the_call_site_coordinates() -> None:
    assert heat_key('f13:l2210:sim.pass(3)---s2:l40:rep3:hex.exact_xor(5)') == 'sim.pass(3)---rep3:hex.exact_xor(5)'
    assert heat_key('((f13:l2210:sim.pass(3)---hp + 128) + 32)') == '((sim.pass(3)---hp + 128) + 32)'
    assert heat_key('(hex.tables.res + 32)') == '(hex.tables.res + 32)'


def test_hot_sites_get_the_cheapest_indices_whatever_the_encounter_order() -> None:
    sites = [f'f1:l{line}:cold' for line in range(5)] + ['f1:l9:hot']  # the hot table comes LAST
    plain = BlockPool(W, POOL_BASE, counts={'g': 6}, widths={'g': 16})
    assert _place(plain, sites)['f1:l9:hot'] == 5  # encounter order: popcount 2
    hot = BlockPool(W, POOL_BASE, counts={'g': 6}, widths={'g': 16}, heat={'g': [('hot', 0, 16)]})
    placed = _place(hot, sites)
    assert placed['f1:l9:hot'] == 0  # its rank's index: popcount 0
    assert sorted(placed.values()) == [0, 1, 2, 3, 4, 5]  # the others take the next cheapest, once each
    assert hot.hot_sites_matched == 1


def test_hot_sites_rank_within_their_width_bucket() -> None:
    kwargs = dict(
        counts={'g': 4}, widths={'g': 64}, width_hist={'g': {16: 2, 64: 2}}, width_buckets=True, max_slot_ops=512
    )
    pool = BlockPool(W, POOL_BASE, heat={'g': [('b', 0, 16), ('a', 0, 64)]}, **kwargs)  # type: ignore[arg-type]
    wide, narrow = 64 * OP_BITS, 16 * OP_BITS
    # each width holds its 2 tables plus its 1 reserved rank: 4 slots; the 64-op bucket comes first
    narrow_bucket = 4 * wide
    got = [
        pool.reserve(16, width, group='g', group_expr=Expr('g'), labels_prefix=site)
        for site, width in (('f1:l1:x', 64), ('f1:l2:a', 64), ('f1:l3:y', 16), ('f1:l4:b', 16))
    ]
    assert [address - POOL_BASE for address, _, _ in got] == [  # type: ignore[misc]
        wide,  # x: the rank after `a`'s
        0,  # a: the cheapest 64-op slot
        narrow_bucket + narrow,  # y: the rank after `b`'s
        narrow_bucket,  # b: the cheapest 16-op slot
    ]


def test_three_listed_sites_take_three_distinct_cheapest_indices() -> None:
    heat = {'g': [('a', 0, 16), ('b', 0, 16), ('c', 0, 16)]}
    pool = BlockPool(W, POOL_BASE, counts={'g': 4}, widths={'g': 16}, heat=heat)
    # 4 tables + 3 reserved ranks -> 8 slots, cheapest first 0, 1, 2, 4, 3, ...
    assert _place(pool, ['f1:l1:c', 'f1:l2:x', 'f1:l3:b', 'f1:l4:a']) == {
        'f1:l1:c': 2,
        'f1:l2:x': 4,
        'f1:l3:b': 1,
        'f1:l4:a': 0,
    }


def test_a_listed_site_whose_width_changed_is_placed_as_unlisted() -> None:
    # `a` was profiled as a 16-op table and is now 64 ops wide; `c` is listed at 64 ops. Taking `a`'s
    # old rank in the 64-op width would put it in `c`'s slot.
    pool = BlockPool(
        W,
        POOL_BASE,
        counts={'g': 3},
        widths={'g': 64},
        width_hist={'g': {64: 2, 16: 1}},
        width_buckets=True,
        max_slot_ops=512,
        heat={'g': [('a', 0, 16), ('c', 0, 64)]},
    )
    got = {
        site: pool.reserve(16, width, group='g', group_expr=Expr('g'), labels_prefix=f'f1:l{line}:{site}')
        for line, (site, width) in enumerate((('a', 64), ('c', 64), ('b', 16)))
    }
    assert got['a'] == (POOL_BASE + 64 * OP_BITS, True, 0)  # unlisted in its new width: after `c`'s rank
    assert got['c'] == (POOL_BASE, True, 0)
    assert pool.hot_sites_width_changed == 1 and pool.hot_sites_matched == 1


def test_occurrences_count_the_tables_that_decline() -> None:
    # the counting pass saw both tables, so the heat list numbers the 16-op one as occurrence 1
    pool = BlockPool(W, POOL_BASE, counts={'g': 2}, widths={'g': 64}, heat={'g': [('site', 1, 16)]})
    assert pool.reserve(16, 64, group='g', group_expr=Expr('g'), labels_prefix='f1:l1:site') is None  # too wide
    assert pool.reserve(16, 16, group='g', group_expr=Expr('g'), labels_prefix='f1:l2:site') == (POOL_BASE, True, 0)
    assert pool.hot_sites_matched == 1


def test_a_listed_site_the_program_lost_pushes_no_table_out() -> None:
    sites = [f'f1:l{line}:t' for line in range(4)]
    for heat in (None, {'g': [('gone', 0, 16)]}):
        pool = BlockPool(W, POOL_BASE, counts={'g': 4}, widths={'g': 16}, heat=heat)
        assert sorted(_place(pool, sites).values()) == ([0, 1, 2, 3] if heat is None else [1, 2, 3, 4])
        assert pool.declined == 0 and not pool.broken_groups


def test_a_hot_width_grows_only_when_its_ranks_do_not_fit() -> None:
    # 300 tables with spread 2 own 1,024 slots, so 300 reserved ranks (600 in all) fit and the block
    # keeps its size; sizing the next power of two of 600 before the spread would double it
    kwargs = dict(counts={'g': 300}, widths={'g': 16}, spread=2, spread_min_count=256)
    plain = BlockPool(W, POOL_BASE, **kwargs)  # type: ignore[arg-type]
    heat = {'g': [(f's{i}', 0, 16) for i in range(300)]}
    hot = BlockPool(W, POOL_BASE, heat=heat, **kwargs)  # type: ignore[arg-type]
    assert hot._block_bits('g') == plain._block_bits('g')
    # 4 tables own 4 slots: 3 more ranks do not fit, so the block doubles
    small = BlockPool(W, POOL_BASE, counts={'g': 4}, widths={'g': 16})
    grown = BlockPool(W, POOL_BASE, counts={'g': 4}, widths={'g': 16}, heat={'g': [(s, 0, 16) for s in 'abc']})
    assert grown._block_bits('g') == 2 * small._block_bits('g')


def test_a_hot_bucket_grows_only_when_its_ranks_do_not_fit() -> None:
    # the width-bucket layout, which doom builds with: the same rule, width by width
    kwargs = dict(
        counts={'g': 300},
        widths={'g': 16},
        width_hist={'g': {16: 300}},
        width_buckets=True,
        max_slot_ops=512,
        spread=2,
        spread_min_count=256,
    )
    plain = BlockPool(W, POOL_BASE, **kwargs)  # type: ignore[arg-type]
    heat = {'g': [(f's{i}', 0, 16) for i in range(300)]}
    hot = BlockPool(W, POOL_BASE, heat=heat, **kwargs)  # type: ignore[arg-type]
    assert hot._block_bits('g') == plain._block_bits('g')


def test_a_bucket_pool_group_without_a_histogram_keeps_room_for_its_ranks() -> None:
    # width buckets on, but no width histogram for the group: its layout falls back to the uniform
    # shape, which must still find the ranks the bucket mode keyed by width
    pool = BlockPool(W, POOL_BASE, counts={'g': 4}, widths={'g': 16}, width_buckets=True, heat={'g': [('gone', 0, 16)]})
    sites = [f'f1:l{line}:t' for line in range(4)]
    assert sorted(_place(pool, sites).values()) == [1, 2, 3, 4]
    assert pool.declined == 0 and not pool.broken_groups


def test_eviction_counts_the_hole_hot_first_placement_leaves() -> None:
    # 16 slots; `h` first leaves a hole in front of `big` (8 slots, aligned to 8), so the plain
    # sum of 14 slots fits and the layout does not. Every group lost must be one evicted by value.
    kwargs = dict(
        counts={'h': 1, 'big': 8, 'mid': 4, 'low': 1},
        widths={'h': 16, 'big': 16, 'mid': 16, 'low': 16},
        span_bits=16 * 16 * OP_BITS,
        evict_by_value=True,
    )
    assert set(BlockPool(W, POOL_BASE, **kwargs).groups) == {'h', 'big', 'mid', 'low'}  # type: ignore[arg-type]
    hot = BlockPool(W, POOL_BASE, heat={'h': [('x', 0, 16)]}, **kwargs)  # type: ignore[arg-type]
    assert 'h' in hot.groups
    assert len(hot.broken_groups) == hot.evicted_low_value == 1  # none lost to placement order


def test_eviction_counts_the_holes_among_hot_blocks() -> None:
    # heat order h1 (1 slot), then h2 (4 slots, aligned to 4): 3 slots stay empty, so 9 one-slot
    # groups need 17 of 16 slots and one must be evicted by value, not lost to placement order
    counts = {'h1': 1, 'h2': 4, **{f'n{i}': 1 for i in range(9)}}
    kwargs = dict(counts=counts, widths={g: 16 for g in counts}, span_bits=16 * 16 * OP_BITS, evict_by_value=True)
    pool = BlockPool(W, POOL_BASE, heat={'h1': [], 'h2': []}, **kwargs)  # type: ignore[arg-type]
    assert len(pool.broken_groups) == pool.evicted_low_value == 1


def test_eviction_stops_once_the_biggest_block_is_gone() -> None:
    # `big` (8 slots) is evicted first; that also removes the hole in front of it, so the 9 one-slot
    # groups then fit: exactly one eviction
    counts = {'h': 1, 'big': 8, **{f's{i}': 1 for i in range(9)}}
    kwargs = dict(counts=counts, widths={g: 16 for g in counts}, span_bits=16 * 16 * OP_BITS, evict_by_value=True)
    pool = BlockPool(W, POOL_BASE, heat={'h': []}, **kwargs)  # type: ignore[arg-type]
    assert pool.evicted_low_value == 1 and 'big' not in pool.groups and len(pool.groups) == 10


def test_eviction_without_heat_keeps_the_plain_sum() -> None:
    # no list must evict exactly as 1.5.1 does, also where the pool base is not aligned to the
    # biggest block: the plain sum (16 slots) fits, nothing is evicted, `big` takes its aligned
    # slot and `q`, `r` are lost to placement order
    base = POOL_BASE + 16 * OP_BITS
    counts = {'big': 8, 'q': 3, 'r': 4}
    pool = BlockPool(
        W, base, counts=counts, widths={g: 16 for g in counts}, span_bits=16 * 16 * OP_BITS, evict_by_value=True
    )
    assert pool.evicted_low_value == 0 and set(pool.groups) == {'big'}


def test_hot_groups_are_placed_first_from_the_pool_base() -> None:
    kwargs = dict(counts={'big': 8, 'small': 1}, widths={'big': 16, 'small': 16})
    plain = BlockPool(W, POOL_BASE, **kwargs)  # type: ignore[arg-type]
    assert plain.groups['big'][0] == POOL_BASE  # biggest first
    hot = BlockPool(W, POOL_BASE, heat={'small': [('h', 0, 16)]}, **kwargs)  # type: ignore[arg-type]
    assert hot.groups['small'][0] == POOL_BASE and hot.groups['big'][0] > POOL_BASE


def test_sites_that_share_a_key_are_told_apart_by_occurrence() -> None:
    # two calls of one macro on different lines strip to one key; the heat list names the second
    pool = BlockPool(W, POOL_BASE, counts={'g': 2}, widths={'g': 16}, heat={'g': [('site', 1, 16)]})
    assert _place(pool, ['f1:l5:site', 'f1:l8:site']) == {'f1:l5:site': 1, 'f1:l8:site': 0}


def test_a_hot_group_is_pinned_even_when_it_breaks() -> None:
    kwargs = dict(counts={'g': 2}, widths={'g': 16})
    for heat, pinned in ((None, False), ({'g': [('h', 0, 16)]}, True)):
        pool = BlockPool(W, POOL_BASE, heat=heat, **kwargs)  # type: ignore[arg-type]
        # 2 tables counted: with no list the third overflows; with one (2 + 1 rank -> 4 slots,
        # rank 0 kept for `h`) the fourth does
        for line in range(5):
            pool.reserve(16, 16, group='g', group_expr=Expr('g'), labels_prefix=f'f1:l{line}:t')
        assert pool.broken_groups == {'g'}
        assert bool(pool.pinned_words()) == pinned


def test_a_hot_group_that_gets_no_block_raises() -> None:
    kwargs = dict(counts={'a': 1, 'g': 2}, widths={'a': 16, 'g': 16}, span_bits=16 * OP_BITS)
    assert 'g' in BlockPool(W, POOL_BASE, **kwargs).broken_groups  # type: ignore[arg-type]  # silent without heat
    with pytest.raises(FlipJumpPreprocessorException, match='pin protection'):
        BlockPool(W, POOL_BASE, heat={'g': [('h', 0, 16)]}, **kwargs)  # type: ignore[arg-type]


def test_eviction_never_drops_a_hot_group() -> None:
    kwargs = dict(counts={'a': 1, 'b': 3}, widths={'a': 16, 'b': 16}, span_bits=4 * 16 * OP_BITS, evict_by_value=True)
    assert set(BlockPool(W, POOL_BASE, **kwargs).groups) == {'a'}  # type: ignore[arg-type]  # `b` is worth least
    hot = BlockPool(W, POOL_BASE, heat={'b': [('h', 0, 16)]}, **kwargs)  # type: ignore[arg-type]
    assert set(hot.groups) == {'b'} and hot.evicted_low_value == 1


def test_heat_names_are_matched_without_coordinates_and_reported() -> None:
    heat = {'((x + 64) + 32)': [('h', 0, 16)], '(gone + 32)': [('h', 0, 16)], '(twice + 32)': [('h', 0, 16)]}
    counts = {'((f2:l7:x + 64) + 32)': 1, '(f1:l1:twice + 32)': 1, '(f1:l2:twice + 32)': 1}
    pool = BlockPool(W, POOL_BASE, counts=counts, widths={g: 16 for g in counts}, heat=heat)
    assert set(pool.hot_sites) == {'((f2:l7:x + 64) + 32)'}
    assert pool.hot_missing == ['(gone + 32)'] and pool.hot_ambiguous == ['(twice + 32)']
    assert pool.heat_report() == {
        'hot_groups': 1,
        'hot_groups_missing': 1,
        'hot_groups_ambiguous': 1,
        'hot_sites_listed': 1,
        'hot_sites_matched': 0,
        'hot_sites_width_changed': 0,
    }


def test_the_heat_list_may_not_name_a_site_twice() -> None:
    with pytest.raises(FlipJumpPreprocessorException, match='twice'):
        BlockPool(W, POOL_BASE, counts={'g': 2}, widths={'g': 16}, heat={'g': [('h', 0, 16), ('h', 0, 16)]})


def test_no_heat_and_an_empty_heat_list_change_nothing() -> None:
    kwargs = dict(counts={'g': 300, 'k': 5}, widths={'g': 16, 'k': 16}, spread=2, spread_min_count=256)
    sites = [(group, f'f1:l{i}:t') for i in range(40) for group in ('g', 'k') if group == 'g' or i < 5]
    results = []
    for heat in (None, {}, {'(absent + 32)': [('h', 0, 16)]}):
        pool = BlockPool(W, POOL_BASE, heat=heat, **kwargs)  # type: ignore[arg-type]
        results.append([pool.reserve(16, 16, group=g, group_expr=Expr(g), labels_prefix=site) for g, site in sites])
    assert results[0] == results[1] == results[2]


class _SiteRecorder(BlockPool):
    """a counting pool that also records each table's group and site path, in encounter order"""

    def __init__(self) -> None:
        super().__init__(W, POOL_BASE)
        self.sites: List[Tuple[str, str]] = []

    def reserve(
        self,
        ops_alignment: int,
        table_ops: int,
        group: Optional[str] = None,
        group_expr: Optional[Expr] = None,
        labels_prefix: str = '',
    ) -> Optional[Tuple[int, bool, int]]:
        if group is not None:
            self.sites.append((group, labels_prefix))
        return super().reserve(ops_alignment, table_ops, group, group_expr, labels_prefix)


def test_a_heat_ordered_program_is_the_same_program_in_fewer_ops(tmp_path: Path) -> None:
    counting = _SiteRecorder()
    build_and_run(XOR_PROGRAM, tmp_path, counting, name='counting')
    reference, plain_ops, _ = build_and_run(
        XOR_PROGRAM, tmp_path, BlockPool(W, POOL_BASE, counts=counting.counts, widths=counting.widths), name='plain'
    )
    # the busiest group's LAST table, which encounter order hands its dearest index
    group = max(counting.counts, key=lambda g: (counting.counts[g], g))
    last_site = heat_key([site for g, site in counting.sites if g == group][-1])
    assert last_site.endswith('hex.exact_xor(5)')  # a real table's path, not an empty one
    occurrence = sum(1 for g, site in counting.sites if g == group and heat_key(site) == last_site) - 1
    placing = BlockPool(
        W,
        POOL_BASE,
        counts=counting.counts,
        widths=counting.widths,
        heat={heat_key(group): [(last_site, occurrence, 16)]},
    )
    output, ops, _ = build_and_run(XOR_PROGRAM, tmp_path, placing, name='heat')
    assert output == reference
    assert placing.hot_sites_matched == 1 and placing.pinned_words()
    assert ops < plain_ops


# --- end to end: a relocated or blocked program is the same program, in fewer ops ---


@pytest.mark.parametrize('memory_width', [32, 64])
def test_relocated_tables_leave_the_output_unchanged(tmp_path: Path, memory_width: int) -> None:
    reference, reference_ops, inline_fjm = build_and_run(
        XOR_PROGRAM, tmp_path, None, name='inline', memory_width=memory_width
    )
    assert reference and not pool_segments(inline_fjm)
    pool = TablePool(memory_width, POOL_BASE, run_ops=256)
    output, ops, fjm_path = build_and_run(XOR_PROGRAM, tmp_path, pool, memory_width=memory_width)
    assert output == reference
    assert pool.allocated > 0 and pool_segments(fjm_path, memory_width)
    assert ops < reference_ops


def test_a_pool_that_wants_nothing_is_inert(tmp_path: Path) -> None:
    reference, reference_ops, _ = build_and_run(XOR_PROGRAM, tmp_path, None, name='inline')
    pool = TablePool(W, POOL_BASE, wants=lambda macro_name, labels_prefix: False)
    output, ops, fjm_path = build_and_run(XOR_PROGRAM, tmp_path, pool)
    assert (output, ops) == (reference, reference_ops)
    assert pool.allocated == 0 and not pool_segments(fjm_path)


@pytest.mark.parametrize('blocking', [False, True], ids=['TablePool', 'BlockPool'])
def test_an_input_table_is_never_split(tmp_path: Path, blocking: bool) -> None:
    reference, _, _ = build_and_run(INPUT_PROGRAM, tmp_path, None, name='inline', fixed_input=b'A')
    assert reference == b'0x41'
    pool: TablePool
    if blocking:
        counting = BlockPool(W, POOL_BASE)
        build_and_run(INPUT_PROGRAM, tmp_path, counting, name='counting', fixed_input=b'A')
        pool = BlockPool(W, POOL_BASE, counts=counting.counts, widths=counting.widths)
    else:
        pool = TablePool(W, POOL_BASE)
    output, _, _ = build_and_run(INPUT_PROGRAM, tmp_path, pool, fixed_input=b'A')
    assert output == reference


def test_a_pinned_word_read_through_a_pointer_needs_the_callers_exclusion(tmp_path: Path) -> None:
    reference, _, _ = build_and_run(POINTER_PROGRAM, tmp_path, None, name='inline')
    assert reference == b'B'
    # relocation alone is fine: the word still holds its bare value
    output, _, _ = build_and_run(POINTER_PROGRAM, tmp_path, TablePool(W, POOL_BASE), name='relocated')
    assert output == reference
    counting = BlockPool(W, POOL_BASE)
    build_and_run(POINTER_PROGRAM, tmp_path, counting, name='counting')
    assert counting.reads_words_raw
    # pinning without a declaration of the cells pointers reach is refused, not miscompiled
    with pytest.raises(FlipJumpException, match='pin_exclude'):
        blocked_pool = BlockPool(W, POOL_BASE, counts=counting.counts, widths=counting.widths)
        build_and_run(POINTER_PROGRAM, tmp_path, blocked_pool, name='refused')
    # with the pointed cell excluded from pinning the blocked program is the same program; the
    # veto sees the bit address of the cell's JUMP word, `d + w`
    blocked_pool = BlockPool(W, POOL_BASE, counts=counting.counts, widths=counting.widths)
    exclude: Callable[[int, Dict[str, int]], bool] = lambda address, labels: address == labels['d'] + W  # noqa: E731
    blocked_pool.pin_exclude = exclude
    output, _, _ = build_and_run(POINTER_PROGRAM, tmp_path, blocked_pool, name='excluded')
    assert output == reference
    assert blocked_pool.pinned_words()  # the other armed words are still pinned


def test_a_fall_through_table_is_refused(tmp_path: Path) -> None:
    reference, _, _ = build_and_run(FALL_THROUGH_PROGRAM, tmp_path, None, name='inline')
    pool = TablePool(W, POOL_BASE)
    output, _, _ = build_and_run(FALL_THROUGH_PROGRAM, tmp_path, pool)
    assert output == reference and pool.allocated == 0


def test_a_program_that_grows_into_the_pool_is_refused(tmp_path: Path) -> None:
    with pytest.raises(FlipJumpException):
        build_and_run(XOR_PROGRAM, tmp_path, TablePool(W, 1 << 12))


@pytest.mark.parametrize('source', [XOR_PROGRAM, CMP_PROGRAM], ids=['hex.xor', 'hex.cmp/shift/mul'])
def test_blocked_tables_leave_the_output_unchanged_and_cost_fewer_ops(source: str, tmp_path: Path) -> None:
    reference, reference_ops, _ = build_and_run(source, tmp_path, None, name='inline')
    output, ops, placing = blocked(source, tmp_path)
    assert output == reference
    assert placing.allocated > 0 and placing.pinned_words()
    assert ops < reference_ops


def test_the_shift_tables_are_tables_a_pool_can_see(tmp_path: Path) -> None:
    # shl_bit_once / shr_bit_once dispatch like exact_xor, but built their tables with `rep` and a
    # nested table macro - the same ops, invisible to relocatable_table_end, so a pool that wanted
    # them registered none and they paid a full address on every arm
    reference, reference_ops, _ = build_and_run(SHIFT_PROGRAM, tmp_path, None, name='inline')
    assert reference == b'fdb97530eca864207f6e5d4c3b2a1908'
    wants: Callable[[MacroName, str], bool] = lambda macro_name, labels_prefix: (  # noqa: E731
        macro_name.name in SHIFT_MACROS
    )
    counting = BlockPool(W, POOL_BASE, wants=wants)
    build_and_run(SHIFT_PROGRAM, tmp_path, counting, name='counting')
    assert sum(counting.counts.values()) == 32  # shl_bit 16 + shr_bit 16, one table per call
    placing = BlockPool(W, POOL_BASE, counts=counting.counts, widths=counting.widths, wants=wants)
    output, ops, _ = build_and_run(SHIFT_PROGRAM, tmp_path, placing, name='placing')
    assert output == reference
    assert placing.allocated == 32 and placing.pinned_words()
    assert ops < reference_ops


def test_a_blocked_program_with_declined_tables_is_still_correct(tmp_path: Path) -> None:
    # a tiny span forces declines: the broken groups are un-pinned, and their tables stay inline
    reference, _, _ = build_and_run(CMP_PROGRAM, tmp_path, None, name='inline')
    output, _, placing = blocked(CMP_PROGRAM, tmp_path, span_bits=1 << 16)
    assert output == reference
    assert placing.declined > 0 and placing.broken_groups
    pinned = set(placing.pinned_words())
    for group, (_, expr) in placing.groups.items():
        assert (expr in pinned) == (expr is not None and group not in placing.broken_groups)


# --- the census: a placing pass records what it met, so the next build needs no counting pass ---

# `b` and `b+0` name one word through two expressions, so its groups come in aliased pairs
ALIAS_PROGRAM = """
stl.startup_and_init_all
    hex.set 4, a, 0x1234
    hex.set 4, b, 0x5678
    hex.xor 4, a, b
    hex.xor 4, a, b+0
    hex.print_uint 4, a, 1, 1
    stl.loop
a: hex.vec 4
b: hex.vec 4
"""

CENSUS_PROGRAMS = {'hex.xor': XOR_PROGRAM, 'hex.cmp/shift/mul': CMP_PROGRAM, 'aliased words': ALIAS_PROGRAM}
STALE_KINDS = ('fresh', 'too_few', 'too_narrow', 'missing_groups', 'too_many', 'other_program')


@pytest.fixture(scope='module')
def counted_programs(tmp_path_factory: pytest.TempPathFactory) -> Dict[str, Tuple[bytes, BlockPool]]:
    """{program: (its inline output, the counting pool that counted it)}, built once per module"""
    tmp_path = tmp_path_factory.mktemp('counted')
    counted = {}
    for index, source in enumerate(CENSUS_PROGRAMS.values()):
        reference, _, _ = build_and_run(source, tmp_path, None, name=f'inline{index}')
        counting = BlockPool(W, POOL_BASE)
        build_and_run(source, tmp_path, counting, name=f'counting{index}')
        counted[source] = (reference, counting)
    return counted


def _stale(kind: str, census: BlockCensus, other: BlockCensus) -> Dict[str, Any]:
    """placing-pool arguments made from `census` the way a cached census goes stale"""
    kwargs = census.pool_kwargs()
    if kind == 'too_few':  # every group lost tables since: the extra ones overflow
        kwargs['counts'] = {group: max(1, count // 2) for group, count in census.counts.items()}
    elif kind == 'too_narrow':  # every table grew: none fits its slot
        kwargs['widths'] = {group: 1 for group in census.widths}
        kwargs['width_hist'] = {group: {1: count} for group, count in census.counts.items()}
    elif kind == 'missing_groups':  # half the groups are new since
        kept = sorted(census.counts)[::2]
        kwargs = BlockCensus(
            {g: census.counts[g] for g in kept},
            {g: census.widths[g] for g in kept},
            {g: census.width_hist[g] for g in kept},
            {g: c for g, c in census.alias.items() if c in kept},
        ).pool_kwargs()
    elif kind == 'too_many':  # every group shrank since: room to spare, nothing declines
        kwargs['counts'] = {group: 2 * count for group, count in census.counts.items()}
    elif kind == 'other_program':  # a cache of a different program altogether
        kwargs = other.pool_kwargs()
    else:
        assert kind == 'fresh'
    return kwargs


def assert_recorded_as_counted(placing: BlockPool, counting: BlockPool) -> None:
    """the placing pass's recording is what the counting pass reported: every field a census
    carries (raw and alias-merged), the group expressions, and the tables that had no group"""
    recording = placing.recording
    assert recording is not placing and recording.counting
    assert recording.counts == counting.counts
    assert recording.widths == counting.widths
    assert recording.width_hist == counting.width_hist
    assert {g: str(e) for g, e in recording.exprs.items()} == {g: str(e) for g, e in counting.exprs.items()}
    assert recording.ungrouped == counting.ungrouped
    assert placing.census() == counting.census()
    assert placing.census(merge_aliases=True) == counting.census(merge_aliases=True)


@pytest.mark.parametrize('pin_broken', [False, True], ids=['unpin-broken', 'pin-broken'])
@pytest.mark.parametrize('kind', STALE_KINDS)
@pytest.mark.parametrize('program', list(CENSUS_PROGRAMS), ids=list(CENSUS_PROGRAMS))
def test_a_placing_pass_records_what_a_counting_pass_reports_and_stays_correct(
    tmp_path: Path,
    counted_programs: Dict[str, Tuple[bytes, BlockPool]],
    program: str,
    kind: str,
    pin_broken: bool,
) -> None:
    source = CENSUS_PROGRAMS[program]
    reference, counting = counted_programs[source]
    other_source = CMP_PROGRAM if source is XOR_PROGRAM else XOR_PROGRAM
    other = counted_programs[other_source][1].census(merge_aliases=True)
    given = _stale(kind, counting.census(merge_aliases=True), other)
    placing = BlockPool(W, POOL_BASE, pin_broken=pin_broken, **given)
    output, _, _ = build_and_run(source, tmp_path, placing)

    assert output == reference  # stale counts cost ops, never correctness
    assert_recorded_as_counted(placing, counting)
    report = placing.decline_report()
    assert (
        sum(report.values())
        == placing.declined
        == sum(n for causes in placing.declines_by_group.values() for n in causes.values())
    )
    assert placing.stale_declines == placing.declined  # these programs have no inherent decline
    expected_cause = {'too_few': 'overflow', 'too_narrow': 'width_overflow', 'missing_groups': 'new_group'}.get(kind)
    if kind in ('fresh', 'too_many'):  # the program's own counts, or more room than it needs
        assert placing.declined == 0 and not placing.broken_groups
    elif expected_cause is None:  # another program's: shares some groups (`a`, `b`), not their counts
        assert placing.stale_declines > 0
    else:
        assert report[expected_cause] > 0
    # the census of what it placed is the program's own whatever it was given, so comparing the two
    # tells a build whether its cache was stale
    fresh = placing.census(merge_aliases=True)
    assert fresh == counting.census(merge_aliases=True)
    assert (fresh.pool_kwargs() == given) == (kind == 'fresh')


@pytest.mark.parametrize('program', list(CENSUS_PROGRAMS), ids=list(CENSUS_PROGRAMS))
def test_a_cached_census_rebuilds_the_two_pass_binary(
    tmp_path: Path, counted_programs: Dict[str, Tuple[bytes, BlockPool]], program: str
) -> None:
    """build 1 places from a STALE cache (a different program's) and caches its census; build 2
    places from that census and is the two-pass build's binary, byte for byte"""
    source = CENSUS_PROGRAMS[program]
    reference, counting = counted_programs[source]
    _, two_pass_ops, two_pass_fjm = build_and_run(
        source, tmp_path, BlockPool(W, POOL_BASE, **counting.census(merge_aliases=True).pool_kwargs()), name='two'
    )
    other_source = CMP_PROGRAM if source is XOR_PROGRAM else XOR_PROGRAM
    stale = counted_programs[other_source][1].census(merge_aliases=True)
    first = BlockPool(W, POOL_BASE, **json_round_trip(stale).pool_kwargs())
    output, _, _ = build_and_run(source, tmp_path, first, name='first')
    assert output == reference and first.stale_declines > 0
    cached = json_round_trip(first.census(merge_aliases=True))
    assert cached != stale

    second = BlockPool(W, POOL_BASE, **cached.pool_kwargs())
    output, ops, fjm_path = build_and_run(source, tmp_path, second, name='second')
    assert output == reference and ops == two_pass_ops
    assert fjm_path.read_bytes() == two_pass_fjm.read_bytes()
    assert second.declined == 0 and second.stale_declines == 0
    assert second.census(merge_aliases=True) == cached  # a fixed point: the next build changes nothing


def json_round_trip(census: BlockCensus) -> BlockCensus:
    """through the JSON a build caches it as"""
    return BlockCensus.from_json(json.loads(json.dumps(census.to_json())))


def test_the_census_survives_json_and_rebuilds_its_pool() -> None:
    census = BlockCensus({'g': 3, 'h': 1}, {'g': 31, 'h': 16}, {'g': {16: 2, 31: 1}, 'h': {16: 1}}, {'h2': 'h'})
    assert json_round_trip(census) == census
    pool = BlockPool(W, POOL_BASE, **json_round_trip(census).pool_kwargs())
    assert pool.counts == census.counts and pool.width_hist == census.width_hist and pool.alias == census.alias


def test_merging_aliases_adds_counts_and_histograms_and_keeps_the_widest() -> None:
    merged = merge_aliased_groups(
        {'x': 2, 'y': 3, 'z': 1},
        {'x': 16, 'y': 31, 'z': 16},
        {'x': {16: 2}, 'y': {16: 2, 31: 1}, 'z': {16: 1}},
        {'y': 'x'},
    )
    assert merged == ({'x': 5, 'z': 1}, {'x': 31, 'z': 16}, {'x': {16: 4, 31: 1}, 'z': {16: 1}})


def test_a_census_merges_the_aliases_its_own_labels_imply() -> None:
    placing = BlockPool(W, POOL_BASE, counts={'(x + 32)': 1}, widths={'(x + 32)': 16})
    placing.reserve(16, 16, group='(x + 32)', group_expr=_sum('x', 32))
    placing.reserve(16, 16, group='(x + w)', group_expr=_sum('x', 'w'))  # the same word: 'new_group'
    with pytest.raises(FlipJumpPreprocessorException, match='after assemble'):
        placing.census(merge_aliases=True)  # no labels yet
    assert placing.census() == BlockCensus(
        {'(x + 32)': 1, '(x + w)': 1}, {'(x + 32)': 16, '(x + w)': 16}, {'(x + 32)': {16: 1}, '(x + w)': {16: 1}}, {}
    )
    placing.labels_resolved({'x': 4096, 'w': 32})
    assert placing.census(merge_aliases=True) == BlockCensus(
        {'(x + 32)': 2}, {'(x + 32)': 16}, {'(x + 32)': {16: 2}}, {'(x + w)': '(x + 32)'}
    )


def test_declines_are_told_apart_per_group_by_cause() -> None:
    word = Expr('g')
    # uniform slots: g's tables are counted 16 ops wide, max_slot_ops is 32
    pool = BlockPool(W, POOL_BASE, counts={'g': 2, 'big': 1 << 20}, widths={'g': 16, 'big': 16}, span_bits=1 << 20)
    assert pool.reserve(16, 16, group='g', group_expr=word) is not None
    assert pool.reserve(16, 24, group='g', group_expr=word) is None  # fits a 32-op slot, not g's 16
    assert pool.reserve(16, 40, group='g', group_expr=word) is None  # fits no slot max_slot_ops allows
    assert pool.reserve(16, 16, group='g', group_expr=word) is not None
    assert pool.reserve(16, 16, group='g', group_expr=word) is None  # a third table: g counted 2
    assert pool.reserve(16, 16, group='new', group_expr=Expr('new')) is None
    assert pool.reserve(16, 16, group='big', group_expr=Expr('big')) is None  # counted, no room
    assert pool.declines_by_group == {
        'g': {'width_overflow': 1, 'too_wide': 1, 'overflow': 1},
        'new': {'new_group': 1},
        'big': {'no_block': 1},
    }
    assert pool.decline_report() == {
        'new_group': 1,
        'width_overflow': 1,
        'overflow': 1,
        'no_block': 1,
        'too_wide': 1,
    }
    assert pool.stale_declines == 3 and set(DECLINE_STALE) | set(DECLINE_INHERENT) == set(pool.decline_report())
    # the aggregate counters keep their meaning: no block (new or not), too wide (either way), overflow
    assert (pool.declined_no_block, pool.declined_too_wide, pool.declined_overflow) == (2, 2, 1)
    assert pool.broken_groups == {'g', 'big'}  # `big` broke when it got no block (_preallocate)

    # width buckets: a width the counts lack for the group is stale, one over max_slot_ops is not
    bucketed = BlockPool(
        W, POOL_BASE, counts={'g': 2}, widths={'g': 16}, width_hist={'g': {16: 2}}, width_buckets=True, max_slot_ops=64
    )
    assert bucketed.reserve(16, 40, group='g', group_expr=word) is None
    assert bucketed.reserve(16, 65, group='g', group_expr=word) is None
    assert bucketed.declines_by_group == {'g': {'width_overflow': 1, 'too_wide': 1}}


def test_a_recording_that_misses_a_table_is_caught(
    tmp_path: Path, counted_programs: Dict[str, Tuple[bytes, BlockPool]], monkeypatch: pytest.MonkeyPatch
) -> None:
    """THE NEGATIVE CONTROL of the census tests: a recorder that drops one table, or keeps one too
    narrow, must fail assert_recorded_as_counted - else that check proves nothing"""
    reference, counting = counted_programs[XOR_PROGRAM]
    real_reserve = BlockPool.reserve

    for mutant in ('drop_last', 'narrow_one'):
        seen = {'calls': 0}

        def mutated(
            self: BlockPool,
            ops_alignment: int,
            table_ops: int,
            group: Optional[str] = None,
            group_expr: Optional[Expr] = None,
            labels_prefix: str = '',
            _mutant: str = mutant,
        ) -> Optional[Tuple[int, bool, int]]:
            if self.counting and group is not None:  # the RECORDING's reserve, not the placing one
                seen['calls'] += 1
                if seen['calls'] == sum(counting.counts.values()) and _mutant == 'drop_last':
                    return None
                if seen['calls'] == 1 and _mutant == 'narrow_one':
                    table_ops = ops_alignment = 1
            return real_reserve(self, ops_alignment, table_ops, group, group_expr, labels_prefix)

        monkeypatch.setattr(BlockPool, 'reserve', mutated)
        placing = BlockPool(W, POOL_BASE, **counting.census().pool_kwargs())
        output, _, _ = build_and_run(XOR_PROGRAM, tmp_path, placing, name=mutant)
        monkeypatch.setattr(BlockPool, 'reserve', real_reserve)
        assert output == reference  # the program is fine; only the recording is wrong
        with pytest.raises(AssertionError):
            assert_recorded_as_counted(placing, counting)


# --- one pass: tables wait out of the op stream, and are placed once the expansion is done ---

# a table whose entries flip `y+dbit + $ - $` (y's lowest value bit): `$` is computed while the macro
# expands, so a one-pass pool cannot defer it. 5 -> the entry flips y 2 -> 3, and y ^= x is 6.
NEXT_ADDRESS_PROGRAM = (
    """
def dollar_table x, y @ switch, end {
    wflip x+w, switch, x
    pad 16
  switch:
"""
    + '    y+dbit+$-$;end\n' * 16
    + """
  end:
    wflip x+w, switch
}
stl.startup_and_init_all
    hex.set x, 5
    hex.set y, 2
    dollar_table x, y
    hex.xor y, x
    hex.print_as_digit y, 0
    stl.loop
x: hex.hex
y: hex.hex
"""
)

# a table label (an extern of its macro) named by a `rep` count, which is evaluated DURING the
# expansion - one pass has no address for it yet
EXPANSION_TIME_PROGRAM = (
    """
def ext_table x @ end > ext_switch {
    wflip x+w, ext_switch, x
    pad 16
  ext_switch:
"""
    + '    ;end\n' * 16
    + """
  end:
    wflip x+w, ext_switch
}
def nothing {
    ;$
}
stl.startup_and_init_all
    hex.set x, 5
    ext_table x
    rep(ext_switch - ext_switch + 1, i) nothing
    hex.print_as_digit x, 0
    stl.loop
x: hex.hex
"""
)

# XOR_PROGRAM with more code after its variables: unreachable, but its tables are expanded
APPENDED_PROGRAM = XOR_PROGRAM + """
    hex.xor 4, a, b
    hex.xor 4, b, a
    stl.loop
"""


def two_pass_build(
    source: str, tmp_path: Path, merge_aliases: bool = False, memory_width: int = W, **kwargs: Any
) -> Tuple[bytes, int, Path, BlockPool, BlockPool]:
    """(output, ops, fjm, counting pool, placing pool) of the two-pass blocking build"""
    counting = BlockPool(memory_width, POOL_BASE, **kwargs)
    build_and_run(source, tmp_path, counting, name='counting', memory_width=memory_width)
    census = counting.census(merge_aliases=merge_aliases).pool_kwargs()
    placing = BlockPool(memory_width, POOL_BASE, **census, **kwargs)
    output, ops, fjm_path = build_and_run(source, tmp_path, placing, name='two_pass', memory_width=memory_width)
    return output, ops, fjm_path, counting, placing


def expand_labels(source: str, tmp_path: Path, pool: Optional[TablePool], name: str = 'p') -> Dict[str, int]:
    """the labels of `source` expanded with the stl and `pool` (macro expansion only)"""
    fj_path = tmp_path / f'{name}.fj'
    fj_path.write_text(source)
    macros = parse_macro_tree(get_file_tuples([str(fj_path)]), W, True)
    _, labels = resolve_macros(W, macros, table_pool=pool, save_debug_labels=False)
    return labels


ONE_PASS_CASES: Dict[str, Tuple[str, Dict[str, Any]]] = {
    'hex.xor': (XOR_PROGRAM, {}),
    'hex.cmp/shift/mul': (CMP_PROGRAM, {}),
    'aliased words': (ALIAS_PROGRAM, {}),
    'shifts': (SHIFT_PROGRAM, {'wants': lambda macro_name, labels_prefix: macro_name.name in SHIFT_MACROS}),
}
ONE_PASS_LAYOUTS: Dict[str, Dict[str, Any]] = {
    'uniform': {},
    'buckets': {'width_buckets': True, 'max_slot_ops': 512},
    'spread': {'spread': 2, 'spread_min_count': 4},
}


@pytest.mark.parametrize('merge_aliases', [False, True], ids=['no-alias', 'merge-aliases'])
@pytest.mark.parametrize('layout', list(ONE_PASS_LAYOUTS))
@pytest.mark.parametrize('case', list(ONE_PASS_CASES))
def test_one_pass_builds_the_two_pass_binary_byte_for_byte(
    tmp_path: Path, case: str, layout: str, merge_aliases: bool
) -> None:
    source, case_kwargs = ONE_PASS_CASES[case]
    kwargs = {**case_kwargs, **ONE_PASS_LAYOUTS[layout]}
    reference, _, _ = build_and_run(source, tmp_path, None, name='inline')
    two_output, two_ops, two_fjm, counting, placing = two_pass_build(source, tmp_path, merge_aliases, **kwargs)
    assert placing.declined == 0  # the precondition for identical binaries

    one = BlockPool(W, POOL_BASE, one_pass=True, merge_aliases=merge_aliases, **kwargs)
    output, ops, fjm_path = build_and_run(source, tmp_path, one, name='one_pass')
    assert output == two_output == reference
    assert fjm_path.read_bytes() == two_fjm.read_bytes() and ops == two_ops
    assert one.deferred == placing.allocated == one.allocated > 0
    assert one.overflowed == one.declined == one.kept_inline == 0
    assert one.census(merge_aliases=merge_aliases) == counting.census(merge_aliases=merge_aliases)
    assert {g: base for g, (base, _) in one.groups.items()} == {g: base for g, (base, _) in placing.groups.items()}


def test_one_pass_merges_its_census_by_a_given_alias(
    tmp_path: Path, counted_programs: Dict[str, Tuple[bytes, BlockPool]]
) -> None:
    reference, counting = counted_programs[ALIAS_PROGRAM]
    merged = counting.census(merge_aliases=True)
    assert merged.alias  # the program does alias its words
    _, _, two_fjm = build_and_run(ALIAS_PROGRAM, tmp_path, BlockPool(W, POOL_BASE, **merged.pool_kwargs()), name='two')
    one = BlockPool(W, POOL_BASE, one_pass=True, alias=merged.alias)  # sized from its census, merged by the alias
    output, _, fjm_path = build_and_run(ALIAS_PROGRAM, tmp_path, one, name='one')
    assert output == reference and fjm_path.read_bytes() == two_fjm.read_bytes()
    assert one.counts == merged.counts


@pytest.mark.parametrize('memory_width', [32, 64])
def test_one_pass_reads_input_and_runs_at_both_widths(tmp_path: Path, memory_width: int) -> None:
    reference, _, _ = build_and_run(
        INPUT_PROGRAM, tmp_path, None, name='inline', fixed_input=b'A', memory_width=memory_width
    )
    counting = BlockPool(memory_width, POOL_BASE)
    build_and_run(INPUT_PROGRAM, tmp_path, counting, name='counting', fixed_input=b'A', memory_width=memory_width)
    placing = BlockPool(memory_width, POOL_BASE, **counting.census().pool_kwargs())
    _, _, two_fjm = build_and_run(
        INPUT_PROGRAM, tmp_path, placing, name='two', fixed_input=b'A', memory_width=memory_width
    )
    one = BlockPool(memory_width, POOL_BASE, one_pass=True)
    output, _, fjm_path = build_and_run(
        INPUT_PROGRAM, tmp_path, one, name='one', fixed_input=b'A', memory_width=memory_width
    )
    assert output == reference == b'0x41'
    assert fjm_path.read_bytes() == two_fjm.read_bytes() and one.deferred > 0


def test_one_pass_with_pin_protection_builds_the_two_pass_binary(tmp_path: Path) -> None:
    counting = _SiteRecorder()
    build_and_run(XOR_PROGRAM, tmp_path, counting, name='counting')
    group = max(counting.counts, key=lambda g: (counting.counts[g], g))
    last_site = heat_key([site for g, site in counting.sites if g == group][-1])
    occurrence = sum(1 for g, site in counting.sites if g == group and heat_key(site) == last_site) - 1
    heat = {heat_key(group): [(last_site, occurrence, 16)]}
    placing = BlockPool(W, POOL_BASE, counts=counting.counts, widths=counting.widths, heat=heat)
    two_output, _, two_fjm = build_and_run(XOR_PROGRAM, tmp_path, placing, name='two')
    one = BlockPool(W, POOL_BASE, one_pass=True, heat=heat)
    output, _, fjm_path = build_and_run(XOR_PROGRAM, tmp_path, one, name='one')
    assert output == two_output
    assert one.hot_sites_matched == placing.hot_sites_matched == 1
    assert fjm_path.read_bytes() == two_fjm.read_bytes()


def test_a_one_pass_placement_in_another_order_is_caught(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """THE NEGATIVE CONTROL of the byte-identity tests: placing the same tables in another order is
    a correct program, and a DIFFERENT binary - which the byte comparison must see"""
    reference, _, two_fjm, _, _ = two_pass_build(XOR_PROGRAM, tmp_path)
    real_place = BlockPool.place_deferred

    def reversed_order(self: BlockPool, tables: Any, labels: Dict[str, int]) -> List[Optional[int]]:
        return real_place(self, tables[::-1], labels)[::-1]

    monkeypatch.setattr(BlockPool, 'place_deferred', reversed_order)
    output, _, fjm_path = build_and_run(XOR_PROGRAM, tmp_path, BlockPool(W, POOL_BASE, one_pass=True), name='reversed')
    assert output == reference
    assert fjm_path.read_bytes() != two_fjm.read_bytes()


@pytest.mark.parametrize('buckets', [False, True], ids=['uniform', 'buckets'])
@pytest.mark.parametrize('pin_broken', [False, True], ids=['unpin-broken', 'pin-broken'])
def test_one_pass_keeps_a_table_too_wide_for_any_slot_inline_like_two_pass(
    tmp_path: Path, buckets: bool, pin_broken: bool
) -> None:
    """no counts can give hex.cmp's 31-op table a slot of max_slot_ops=16, so a placing pass
    declines it at its pad; one pass decides it there too, and the binaries stay identical"""
    kwargs: Dict[str, Any] = {'max_slot_ops': 16, 'pin_broken': pin_broken, 'width_buckets': buckets}
    counting_kwargs = {k: v for k, v in kwargs.items() if k != 'pin_broken'}
    counting = BlockPool(W, POOL_BASE, **counting_kwargs)
    build_and_run(CMP_PROGRAM, tmp_path, counting, name='counting')
    placing = BlockPool(W, POOL_BASE, **counting.census().pool_kwargs(), **kwargs)
    two_output, _, two_fjm = build_and_run(CMP_PROGRAM, tmp_path, placing, name='two')
    one = BlockPool(W, POOL_BASE, one_pass=True, **kwargs)
    output, _, fjm_path = build_and_run(CMP_PROGRAM, tmp_path, one, name='one')
    assert output == two_output
    assert placing.decline_report()['too_wide'] == one.decline_report()['too_wide'] == one.declined > 0
    assert one.overflowed == 0 and one.broken_groups == placing.broken_groups
    assert fjm_path.read_bytes() == two_fjm.read_bytes()


ONE_PASS_DECLINES: Dict[str, Tuple[Optional[Dict[str, Any]], str]] = {
    'tiny span': ({'span_bits': 1 << 14}, 'no_block'),
    'stale counts': (None, 'overflow'),  # half of the program's own counts, frozen
    'empty counts': ({'counts': {}, 'widths': {}}, 'new_group'),
}


@pytest.mark.parametrize('pin_broken', [False, True], ids=['unpin-broken', 'pin-broken'])
@pytest.mark.parametrize('scenario', list(ONE_PASS_DECLINES))
def test_one_pass_sends_what_gets_no_block_to_the_overflow_region(
    tmp_path: Path, counted_programs: Dict[str, Tuple[bytes, BlockPool]], scenario: str, pin_broken: bool
) -> None:
    reference, counting = counted_programs[CMP_PROGRAM]
    kwargs, cause = ONE_PASS_DECLINES[scenario]
    if kwargs is None:
        census = counting.census()
        kwargs = {**census.pool_kwargs(), 'counts': {g: max(1, n // 2) for g, n in census.counts.items()}}
    one = BlockPool(W, POOL_BASE, one_pass=True, pin_broken=pin_broken, **kwargs)
    output, _, fjm_path = build_and_run(CMP_PROGRAM, tmp_path, one)
    assert output == reference
    assert one.decline_report()[cause] > 0 and one.overflowed == one.declined
    assert one.deferred == one.allocated + one.overflowed  # nothing went back inline
    blocks_end = POOL_BASE + one._used
    overflow = [s for s in Reader(fjm_path).memory_segments if s.segment_start * W >= blocks_end]
    assert len(overflow) == one.overflowed  # one segment per overflow table, all above the blocks
    assert all(s.segment_start * W % (4 * OP_BITS) == 0 for s in overflow)  # aligned like their `pad`


def test_the_op_stream_does_not_depend_on_what_one_pass_decides(tmp_path: Path) -> None:
    """every label outside the tables lands at the same address whatever the pool does with them -
    while the two-pass build, which keeps a declined table inline, moves them"""

    def outside_tables(labels: Dict[str, int]) -> Dict[str, int]:
        return {label: address for label, address in labels.items() if address < POOL_BASE}

    configs: List[Dict[str, Any]] = [{}, {'span_bits': 1 << 14}, {'span_bits': 1 << 16}, {'counts': {}, 'widths': {}}]
    one_pass = [
        outside_tables(expand_labels(CMP_PROGRAM, tmp_path, BlockPool(W, POOL_BASE, one_pass=True, **config)))
        for config in configs
    ]
    assert all(labels == one_pass[0] for labels in one_pass[1:])
    counting = BlockPool(W, POOL_BASE)
    expand_labels(CMP_PROGRAM, tmp_path, counting)
    census = counting.census().pool_kwargs()
    extras: List[Dict[str, Any]] = [{}, {'span_bits': 1 << 14}]
    fresh, tiny = (
        outside_tables(expand_labels(CMP_PROGRAM, tmp_path, BlockPool(W, POOL_BASE, **census, **extra)))
        for extra in extras
    )
    assert fresh == one_pass[0]  # with nothing declined, both modes lay the stream out alike
    assert tiny != fresh  # the comparison can see a moved stream


def test_one_pass_with_frozen_counts_keeps_the_layout_when_code_is_appended(tmp_path: Path) -> None:
    """the doom-flipjump game tier assembles twice, the second time with code appended: given the
    first assembly's census, the second lays out everything the first had at the same addresses"""
    first = BlockPool(W, POOL_BASE, one_pass=True)
    first_labels = expand_labels(XOR_PROGRAM, tmp_path, first, name='first')
    census = first.census()
    second = BlockPool(W, POOL_BASE, one_pass=True, **census.pool_kwargs())
    second_labels = expand_labels(APPENDED_PROGRAM, tmp_path, second, name='second')
    assert {label: second_labels[label] for label in first_labels} == first_labels
    assert {g: b for g, (b, _) in second.groups.items()} == {g: b for g, (b, _) in first.groups.items()}
    # each appended table took a spare slot of its group's power-of-two block, or - the block being
    # full - went to the overflow region
    appended = sum(second.census().counts.values()) - sum(census.counts.values())
    assert appended > 0 and second.allocated - first.allocated + second.overflowed == appended
    assert second.overflowed == second.stale_declines > 0
    reference, _, _ = build_and_run(XOR_PROGRAM, tmp_path, None, name='inline')
    output, _, _ = build_and_run(
        APPENDED_PROGRAM, tmp_path, BlockPool(W, POOL_BASE, one_pass=True, **census.pool_kwargs()), name='appended'
    )
    assert output == reference


def test_the_overflow_region_can_be_placed_and_must_fit(
    tmp_path: Path, counted_programs: Dict[str, Tuple[bytes, BlockPool]]
) -> None:
    reference, counting = counted_programs[XOR_PROGRAM]
    base = POOL_BASE // 2  # between the program and the pool
    pool = BlockPool(W, POOL_BASE, one_pass=True, counts={}, widths={}, overflow_base=base)
    output, _, fjm_path = build_and_run(XOR_PROGRAM, tmp_path, pool, name='below')
    assert output == reference and pool.overflowed > 0
    starts = [s.segment_start * W for s in Reader(fjm_path).memory_segments]
    assert sum(1 for start in starts if base <= start < POOL_BASE) == pool.overflowed
    too_few = counting.census().pool_kwargs()
    too_few['counts'] = {group: count // 2 for group, count in counting.counts.items()}  # some overflow
    with pytest.raises(FlipJumpException, match='overlaps the blocks'):
        build_and_run(XOR_PROGRAM, tmp_path, BlockPool(W, POOL_BASE, one_pass=True, overflow_base=POOL_BASE, **too_few))
    with pytest.raises(FlipJumpException, match='past the 32-bit memory'):
        build_and_run(
            XOR_PROGRAM,
            tmp_path,
            BlockPool(W, POOL_BASE, one_pass=True, counts={}, widths={}, overflow_base=(1 << W) - OP_BITS),
        )


def test_a_table_whose_entries_use_the_next_address_stays_inline(tmp_path: Path) -> None:
    reference, _, _ = build_and_run(NEXT_ADDRESS_PROGRAM, tmp_path, None, name='inline')
    assert reference == b'6'
    one = BlockPool(W, POOL_BASE, one_pass=True)
    output, _, _ = build_and_run(NEXT_ADDRESS_PROGRAM, tmp_path, one, name='one')
    assert output == reference
    assert one.kept_inline == 1 and one.deferred > 0  # hex.xor's tables still left the stream
    counting = BlockPool(W, POOL_BASE)
    build_and_run(NEXT_ADDRESS_PROGRAM, tmp_path, counting, name='counting')
    assert one.census() == counting.census()  # it is counted all the same


def test_a_table_label_evaluated_during_the_expansion_is_refused_by_one_pass(tmp_path: Path) -> None:
    reference, _, _ = build_and_run(EXPANSION_TIME_PROGRAM, tmp_path, None, name='inline')
    output, _, _ = two_pass_build(EXPANSION_TIME_PROGRAM, tmp_path)[:3]
    assert output == reference == b'5'  # two passes know the address when the rep needs it
    with pytest.raises(FlipJumpException, match='ext_switch, the label of a table that one-pass blocking places'):
        build_and_run(EXPANSION_TIME_PROGRAM, tmp_path, BlockPool(W, POOL_BASE, one_pass=True), name='one')

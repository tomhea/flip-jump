"""
unit-tests for the table pool's gap hunt: every crafted program (tests/unit/pool_gaps) either runs with a pool
exactly as without one, or is refused with the reason - and the pool's smaller promises (a pool lays out one
assembly, a TablePool slot is aligned and inside the span, a wflip area that leaves the memory says so).
"""

from pathlib import Path
from typing import Dict, Optional, Tuple

import pytest

from flipjump import assemble, assemble_run_according_to_cmd_line_args
from flipjump.assembler.table_pool import BlockPool, OffsetGuard, TablePool
from flipjump.utils.exceptions import FlipJumpException
from tests.unit.pool_fuzzer import run
from tests.unit.test_table_pool import build_and_run, relocatable

GAPS = Path(__file__).parent / 'pool_gaps'
W = 32
OP_BITS = 2 * W
POOL_BASE = 1 << 26


def _pool(kind: str, memory_width: int, source: Path, tmp_path: Path) -> TablePool:
    base = 1 << (memory_width - 1)
    if kind == 'cli':  # fj --pool-tables
        return BlockPool(memory_width, base, one_pass=True)
    if kind == 'table':
        return TablePool(memory_width, base, run_ops=16)
    counting = BlockPool(memory_width, base)
    assemble([source], tmp_path / 'count.fjm', memory_width=memory_width, print_time=False, table_pool=counting)
    return BlockPool(memory_width, base, counts=counting.counts, widths=counting.widths)


SAME = None
GUARD_C06 = (
    r'the operand `L` of the op at 0x480 \(in the top level\) names L, declared at 0x400 before the `pad` of the '
    r'table T: it named the table\'s start'
)
GUARD_C07_PLUS = (
    r'the operand `T \+ 64` of the op at 0x80 \(after the label f1:l11:stl.startup---code_start\) leaves the moved '
    r'table T at 0x80000000: an offset from a moved table\'s label must stay inside it'
)
GUARD_C07_COMPOUND = (
    r'the operand `\(\(T \+ 64\) \| 0\)` of the op at 0x80 \(after the label f1:l11:stl.startup---code_start\) '
    r'lands at 0x80000040, in the table pool \(it computes from T, of the moved table T\)'
)
GUARDED = [
    'c06_label_before_pad',
    'c07a_reach_in_plus',
    'c07b_reach_in_compound',
    'c07c_reach_in_compound_labelled',
    'c07d_reach_in_plus_labelled',
]
# (program, memory width): {pool: SAME, or the words of its refusal}
CASES: Dict[Tuple[str, int], Dict[str, Optional[str]]] = {
    ('c01_raw_read_bit_ptr', 32): {'cli': 'pointer runtime', 'two_pass': 'pointer runtime', 'table': SAME},  # B1
    ('c16_runtime_write_upper_half', 32): {'cli': 'pointer runtime', 'table': SAME},  # B1
    ('c02_pinned_floor', 32): {'cli': SAME, 'two_pass': SAME, 'table': SAME},  # B2
    ('c03_pinned_in_reserve', 32): {'cli': 'are no op', 'two_pass': 'are no op', 'table': SAME},  # B3
    ('c08_retarget_xor', 32): {'cli': 'computed from labels', 'two_pass': 'computed from labels', 'table': SAME},  # B4
    ('c08b_retarget_xor_labelled', 32): {'cli': 'computed from labels', 'table': SAME},  # B4
    ('c05_label_offset_out_of_table', 32): {'cli': 'leaves the table through', 'table': 'leaves the table through'},
    ('c05b_trailing_label', 32): {'cli': 'declares a label after its last op', 'table': 'after its last op'},  # B5
    ('c09_pad3', 32): {'cli': 'power-of-two pad', 'table': 'power-of-two pad'},  # B6
    ('c10_wflip_area_crosses_pool', 16): {'cli': 'its wflip area reach', 'table': 'its wflip area reach'},  # M1
    ('c11_segment_above_pool', 16): {'cli': 'inside the table pool'},  # M2
    ('c14_accidental_namespace', 32): {'cli': 'needs a `pad`'},  # M6: a reserved namespace with the pool
    ('c13_label_between_pad_and_call', 32): {'cli': SAME, 'table': SAME},
    ('c15_nested_namespaces', 32): {'cli': SAME, 'table': SAME},
    ('c19_no_label_after_call', 32): {'cli': SAME, 'table': SAME},
    # an operand outside a moved table that names a label and reaches the table's place (OffsetGuard)
    ('c06_label_before_pad', 32): {'cli': GUARD_C06, 'table': GUARD_C06},
    ('c07a_reach_in_plus', 32): {'cli': GUARD_C07_PLUS, 'table': GUARD_C07_PLUS},
    ('c07b_reach_in_compound', 32): {'cli': GUARD_C07_COMPOUND, 'table': GUARD_C07_COMPOUND},
    ('c07c_reach_in_compound_labelled', 32): {'cli': GUARD_C07_COMPOUND, 'table': GUARD_C07_COMPOUND},
    ('c07d_reach_in_plus_labelled', 32): {'cli': GUARD_C07_PLUS, 'table': GUARD_C07_PLUS},
}
PARAMS = [(name, width, pool, refusal) for (name, width), pools in CASES.items() for pool, refusal in pools.items()]


@pytest.mark.parametrize('name, memory_width, pool, refusal', PARAMS, ids=[f'{p[0]}-{p[2]}' for p in PARAMS])
def test_a_crafted_program_runs_the_same_with_the_pool_or_is_refused(
    tmp_path: Path, name: str, memory_width: int, pool: str, refusal: Optional[str]
) -> None:
    source = GAPS / f'{name}.fj'
    plain = tmp_path / 'plain.fjm'
    assemble([source], plain, memory_width=memory_width, print_time=False)
    pooled = tmp_path / 'pooled.fjm'
    if refusal is not None:
        with pytest.raises(FlipJumpException, match=refusal):
            assemble(
                [source],
                pooled,
                memory_width=memory_width,
                print_time=False,
                table_pool=_pool(pool, memory_width, source, tmp_path),
            )
        return
    table_pool = _pool(pool, memory_width, source, tmp_path)
    assemble([source], pooled, memory_width=memory_width, print_time=False, table_pool=table_pool)
    assert table_pool.allocated and run(pooled, 30) == run(plain, 30)


@pytest.mark.parametrize('pool', ['cli', 'table'])
@pytest.mark.parametrize('name', GUARDED)
def test_without_the_offset_guard_a_reach_into_a_moved_table_miscompiles(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str, pool: str
) -> None:
    # the control: each refusal above prevents a real miscompile, which this run shows
    monkeypatch.setattr(OffsetGuard, 'check', lambda self, label, address, offset: None)
    monkeypatch.setattr(OffsetGuard, 'check_expr', lambda self, expr, value, is_address=True: None)
    source = GAPS / f'{name}.fj'
    plain = tmp_path / 'plain.fjm'
    assemble([source], plain, memory_width=W, print_time=False)
    pooled = tmp_path / 'pooled.fjm'
    table_pool = _pool(pool, W, source, tmp_path)
    assemble([source], pooled, memory_width=W, print_time=False, table_pool=table_pool)
    assert table_pool.allocated and run(pooled, 30) != run(plain, 30)


# `before + 2*dw` names the table's third entry ('B') only while the table is where it was declared; the
# OffsetGuard sees each in a different place
_TABLE_AND_PRINTS = """
before:
    pad 1
    tbl.__relocatable__.table tbl_start, print_a, print_b
print_a:
    stl.output 'A'
    stl.loop
print_b:
    stl.output 'B'
    stl.loop
""" + relocatable('tbl', 'start, a, b', 'start', '    ;a\n    ;a\n    ;b\n    ;a\n')
OUTSIDE_OFFSET_PROGRAMS = {
    # the label is declared after the operand: labels_resolve checks it
    'deferred': ('stl.startup\n    ;before + 2*dw\n' + _TABLE_AND_PRINTS, 'reaches across the place of the table'),
    # the label is known when the operand is emitted, after the table moved: the preprocessor checks it
    'folded': ('stl.startup\n    ;go\n' + _TABLE_AND_PRINTS + 'go:\n    ;before + 2*dw\n', 'reaches across'),
    # the label is known, and the table moves after the operand: refused when it moves
    'pending': (
        'stl.startup\nhere:\n    ;here + 3*dw\n' + _TABLE_AND_PRINTS,
        'of an earlier op reaches over the place',
    ),
}


@pytest.mark.parametrize('program', sorted(OUTSIDE_OFFSET_PROGRAMS))
def test_an_offset_from_outside_into_a_moved_table_is_refused_wherever_it_is_seen(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, program: str
) -> None:
    # (a TablePool: the table is dispatched through no word, so a BlockPool would keep it in place)
    source, refusal = OUTSIDE_OFFSET_PROGRAMS[program]
    assert build_and_run(source, tmp_path, None, name='plain')[0] == b'B'
    path = tmp_path / 'p.fj'
    path.write_text(source)
    with pytest.raises(FlipJumpException, match=refusal):
        build_and_run(source, tmp_path, _pool('table', W, path, tmp_path), name='pooled')
    # the control: without the guard it is a miscompile
    monkeypatch.setattr(OffsetGuard, 'check', lambda self, label, address, offset: None)
    table_pool = _pool('table', W, path, tmp_path)
    assert build_and_run(source, tmp_path, table_pool, name='unguarded')[0] != b'B' and table_pool.allocated


_XOR = """
stl.startup
    hex.xor x, y
    hex.print_as_digit x, 0
    stl.loop
x: hex.hex 3
y: hex.hex 5
"""


def _source(tmp_path: Path, text: str = _XOR) -> Path:
    path = tmp_path / 'p.fj'
    path.write_text(text)
    return path


def test_a_pool_lays_out_one_assembly(tmp_path: Path) -> None:
    pool: TablePool
    for pool in (TablePool(W, POOL_BASE), BlockPool(W, POOL_BASE), BlockPool(W, POOL_BASE, one_pass=True)):
        assemble([_source(tmp_path)], tmp_path / 'a.fjm', memory_width=W, print_time=False, table_pool=pool)
        with pytest.raises(FlipJumpException, match='already laid out'):  # M4
            assemble([_source(tmp_path)], tmp_path / 'b.fjm', memory_width=W, print_time=False, table_pool=pool)


def test_an_overflow_region_below_the_program_is_refused(tmp_path: Path) -> None:
    pool = BlockPool(W, POOL_BASE, one_pass=True, overflow_base=16 * OP_BITS)  # M3
    with pytest.raises(FlipJumpException, match='inside the table pool'):
        assemble([_source(tmp_path)], tmp_path / 'a.fjm', memory_width=W, print_time=False, table_pool=pool)


def test_a_flat_memory_run_of_a_w64_pooled_program_is_refused(tmp_path: Path) -> None:
    # M5: the tables sit at 2^63, so a flat window would map 2^57 words
    args = ['--asm', '-s', '-o', str(tmp_path / 'a.fjm'), '-w', '64', '--pool-tables', '--run-flags', '1']
    with pytest.raises(SystemExit):
        assemble_run_according_to_cmd_line_args(cmd_line_args=[*args, str(_source(tmp_path))])


def test_a_tablepool_slot_is_aligned_and_a_passed_slot_is_used_later() -> None:
    run_bits = 16 * OP_BITS
    pool = TablePool(W, POOL_BASE + run_bits, run_ops=16)  # M8: offset 0 is not 32-op aligned
    reserved = pool.reserve(32, 32)
    assert reserved is not None and reserved[0] % (32 * OP_BITS) == 0
    pool.commit(reserved[0] + 32 * OP_BITS)
    assert pool.reserve(16, 16) == (POOL_BASE + run_bits, True, 0)  # the offset passed over above


def test_a_tablepool_table_past_the_span_is_declined() -> None:
    pool = TablePool(W, POOL_BASE, run_ops=16, span_bits=16 * OP_BITS)  # M8: one run of span
    assert pool.reserve(16, 32) is None and pool.declined == 1


def test_a_wflip_area_past_the_memory_says_so(tmp_path: Path) -> None:
    # M9: at w=16 this program's wflip chains need more than the 2^16 bits of memory
    wflips = ''.join(f'    wflip z+w, {(i * 4999 + 0x0F0F) & 0xFFFE}\n' for i in range(600))
    source = _source(tmp_path, f'stl.startup\n{wflips}    stl.loop\nz: hex.hex\n')
    with pytest.raises(FlipJumpException, match='Not enough space with the 16-bits memory-width: the wflip area'):
        assemble([source], tmp_path / 'a.fjm', memory_width=16, print_time=False)

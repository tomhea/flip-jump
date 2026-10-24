"""
unit-tests for the relocation proof (flipjump/assembler/relocation_proof.py): with a table pool, every program
of the test tables is the program without it, moved - and the proof sees a corrupted moved op, a declared table
moved in pieces or with an op that is not its own, an offset from an outside label into a moved table, an
operand it cannot compare, and a pin whose arms were not rewritten; it passes correct programs it once rejected.
"""

import csv
from pathlib import Path
from typing import Any, Dict, Iterator, List, Tuple

import pytest

from flipjump.assembler import assembler, relocation_proof
from flipjump.assembler.fj_parser import parse_macro_tree
from flipjump.assembler.inner_classes.expr import Expr
from flipjump.assembler.inner_classes.ops import FlipJump, Macro, MacroName, NewSegment
from flipjump.assembler.relocation_proof import prove_relocation
from flipjump.assembler.table_pool import BlockPool, TablePool
from flipjump.utils.exceptions import FlipJumpAssemblerException, FlipJumpPreprocessorException
from flipjump.utils.functions import get_file_tuples
from tests.unit.test_table_pool import build_and_run, relocatable
from tests.unit.unit_utils import PROGRAMS_DIR

W = 32
POOL_BASE = 1 << 26
TABLES = PROGRAMS_DIR.parent / 'tests' / 'tests_tables'
GAPS = Path(__file__).parent / 'pool_gaps'


def _test_table_programs() -> List[Tuple[str, List[str], int, bool]]:
    """(name, .fj paths, memory width, use stl) of the programs the compile tables build"""
    programs = []
    for stem in ('hexlib', 'fast', 'medium', 'slow'):
        with open(TABLES / f'test_compile_{stem}.csv') as table:
            for row in csv.reader(table):
                if row and row[0].strip():
                    files = [str(PROGRAMS_DIR.parent / path.strip()) for path in row[1].split('|')]
                    programs.append((row[0].strip(), files, int(row[3]), row[6].strip() == 'True'))
    return programs


TEST_TABLE_PROGRAMS = _test_table_programs()


def _macros(files: List[str], memory_width: int, use_stl: bool = True) -> Dict[MacroName, Macro]:
    return parse_macro_tree(get_file_tuples(files, no_stl=not use_stl), memory_width, True)


def _cli_pool(memory_width: int) -> BlockPool:
    return BlockPool(memory_width, 1 << (memory_width - 1), one_pass=True)  # the pool of fj --pool-tables


@pytest.mark.parametrize('program', TEST_TABLE_PROGRAMS, ids=[program[0] for program in TEST_TABLE_PROGRAMS])
def test_every_test_program_is_the_same_program_with_the_pool(program: Tuple[str, List[str], int, bool]) -> None:
    _, files, memory_width, use_stl = program
    pool = _cli_pool(memory_width)
    try:
        proof = prove_relocation(memory_width, _macros(files, memory_width, use_stl), pool)
    except FlipJumpPreprocessorException as refused:
        assert 'inside the table pool' in str(refused)  # prime_sieve's segment at the top of memory
        pytest.skip('the program reaches the pool')
    except FlipJumpAssemblerException as refused:
        assert 'pointer runtime' in str(refused)  # its pins need a pin_exclude: veto them all, the tables still move
        pool = _cli_pool(memory_width)
        pool.pin_exclude = lambda address, labels: True
        proof = prove_relocation(memory_width, _macros(files, memory_width, use_stl), pool)
    assert proof.mismatches == []
    if not pool.allocated:
        pytest.skip('the program uses no relocatable table')


def test_a_tablepool_program_is_the_same_program_too() -> None:
    files = [str(PROGRAMS_DIR / 'hexlib_tests' / '2params' / 'and.fj')]
    pool = TablePool(64, 1 << 63)
    assert prove_relocation(64, _macros(files, 64), pool).mismatches == [] and pool.allocated > 0


def _gap(name: str) -> List[str]:
    return [str(GAPS / f'{name}.fj')]


# `before + 2*dw` names the table's third entry ('B') only while the table is where it was declared
OUTSIDE_OFFSET_PROGRAM = """
stl.startup
    ;before + 2*dw
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


def _write(tmp_path: Path, source: str) -> List[str]:
    path = tmp_path / 'p.fj'
    path.write_text(source)
    return [str(path)]


def test_an_offset_from_outside_into_a_moved_table_fails_the_proof(tmp_path: Path) -> None:
    proof = prove_relocation(W, _macros(_write(tmp_path, OUTSIDE_OFFSET_PROGRAM), W), TablePool(W, POOL_BASE))
    assert any('(before + 128)' in mismatch for mismatch in proof.mismatches), proof.mismatches
    # and it is a miscompile: the moved program prints nothing where the plain one prints B
    assert build_and_run(OUTSIDE_OFFSET_PROGRAM, tmp_path, None, name='plain')[0] == b'B'
    assert build_and_run(OUTSIDE_OFFSET_PROGRAM, tmp_path, TablePool(W, POOL_BASE), name='pooled')[0] != b'B'


@pytest.mark.parametrize('name', ['c06_label_before_pad', 'c07a_reach_in_plus', 'c07d_reach_in_plus_labelled'])
def test_an_outside_label_reaching_a_moved_tables_place_fails_the_proof(name: str) -> None:
    assert prove_relocation(W, _macros(_gap(name), W), _cli_pool(W)).mismatches


@pytest.mark.parametrize('name', ['c07b_reach_in_compound', 'c07c_reach_in_compound_labelled'])
def test_an_operand_computed_from_a_moved_label_fails_the_proof(name: str) -> None:
    # `(T + dw) | 0` is not one address: the proof cannot map it, so it fails it rather than skip it
    mismatches = prove_relocation(W, _macros(_gap(name), W), _cli_pool(W)).mismatches
    assert any('cannot be checked' in mismatch for mismatch in mismatches), mismatches


def test_an_operand_computed_from_unmoved_labels_is_counted_unchecked(tmp_path: Path) -> None:
    base = OUTSIDE_OFFSET_PROGRAM.replace('    ;before + 2*dw\n', '    ;tbl_start + 2*dw\n')
    unchecked = prove_relocation(W, _macros(_write(tmp_path, base), W), TablePool(W, POOL_BASE)).unchecked
    source = base.replace('    ;tbl_start + 2*dw\n', '    ;tbl_start + 2*dw\n    ;(print_a | 0)\n')
    proof = prove_relocation(W, _macros(_write(tmp_path, source), W), TablePool(W, POOL_BASE))
    assert proof.mismatches == [] and proof.unchecked == unchecked + 1


@pytest.mark.parametrize(
    'name, memory_width, pool',
    [
        ('c19_no_label_after_call', W, 'cli'),  # an op after a moved table with no label of its own
        ('c10_wflip_area_crosses_pool', W, 'cli'),  # wflip values that are numbers equal to code addresses
        ('c03_pinned_in_reserve', W, 'table'),  # a label + offset into a `reserve` after a moved table
    ],
)
def test_correct_programs_pass_the_proof(name: str, memory_width: int, pool: str) -> None:
    table_pool = _cli_pool(memory_width) if pool == 'cli' else TablePool(memory_width, 1 << (memory_width - 1))
    assert prove_relocation(memory_width, _macros(_gap(name), memory_width), table_pool).mismatches == []


def _with_extents_changed(monkeypatch: pytest.MonkeyPatch, start: int, end: int) -> None:
    """the plain expansion reports every declared table `start` ops later and `end` ops longer (the proof's
    control: what it reads as declared, the pool did not move)"""
    real_resolve = getattr(relocation_proof, 'resolve_macros')

    def changing(*args: Any, **kwargs: Any) -> Any:
        result = real_resolve(*args, **kwargs)
        extents = kwargs.get('relocatable_extents')
        if extents is not None:
            op_bits = 2 * args[0]
            extents[:] = [(s + start * op_bits, e + end * op_bits) for s, e in extents]
        return result

    monkeypatch.setattr('flipjump.assembler.relocation_proof.resolve_macros', changing)


def test_a_table_moved_short_of_its_declaration_fails_the_proof(monkeypatch: pytest.MonkeyPatch) -> None:
    files = [str(PROGRAMS_DIR / 'hexlib_tests' / '2params' / 'and.fj')]
    _with_extents_changed(monkeypatch, 0, 1)  # the op after each table read as its last
    mismatches = prove_relocation(64, _macros(files, 64), _cli_pool(64)).mismatches
    assert any('moved in pieces' in mismatch for mismatch in mismatches), mismatches


def test_a_moved_op_that_no_declaration_holds_fails_the_proof(monkeypatch: pytest.MonkeyPatch) -> None:
    files = [str(PROGRAMS_DIR / 'hexlib_tests' / '2params' / 'and.fj')]
    _with_extents_changed(monkeypatch, 1, 0)  # each table's first op read as outside it
    mismatches = prove_relocation(64, _macros(files, 64), _cli_pool(64)).mismatches
    assert any('no op of a declared table' in mismatch for mismatch in mismatches), mismatches


def test_a_corrupted_moved_op_fails_the_proof(monkeypatch: pytest.MonkeyPatch) -> None:
    files = [str(PROGRAMS_DIR / 'hexlib_tests' / '2params' / 'and.fj')]
    real_resolve = getattr(relocation_proof, 'resolve_macros')

    def corrupting(*args: Any, **kwargs: Any) -> Any:
        stream, labels = real_resolve(*args, **kwargs)
        if kwargs.get('table_pool') is None:
            return stream, labels

        class Corrupted:
            """the pooled stream, with the jump of its first moved op one op further"""

            def iter_ops(self) -> Iterator[Any]:
                in_pool, done = False, False
                for op in stream.iter_ops():
                    if isinstance(op, NewSegment):
                        in_pool = op.start_address >= (1 << 63)
                    elif in_pool and not done and isinstance(op, FlipJump):
                        op = FlipJump(op.flip, Expr(('+', (op.jump, Expr(128)))), op.code_position)
                        done = True
                    yield op

        return Corrupted(), labels

    assert prove_relocation(64, _macros(files, 64), _cli_pool(64)).mismatches == []
    monkeypatch.setattr('flipjump.assembler.relocation_proof.resolve_macros', corrupting)
    monkeypatch.setattr('flipjump.assembler.relocation_proof.labels_resolve', lambda *args, **kwargs: None)
    mismatches = prove_relocation(64, _macros(files, 64), _cli_pool(64)).mismatches
    assert any('with the pool' in mismatch for mismatch in mismatches), mismatches


def test_a_pin_whose_arms_are_not_rewritten_fails_the_proof(monkeypatch: pytest.MonkeyPatch) -> None:
    # the fuzzer's pin_floor control: the pinned words rest at value ^ base, but no arm or disarm is rewritten
    files = [str(PROGRAMS_DIR / 'hexlib_tests' / '2params' / 'and.fj')]
    assert prove_relocation(64, _macros(files, 64), _cli_pool(64)).mismatches == []
    monkeypatch.setattr(assembler.BinaryData, 'pinned_value', lambda self, word, value, kind: value)
    mismatches = prove_relocation(64, _macros(files, 64), _cli_pool(64)).mismatches
    assert any('of the pinned word' in mismatch for mismatch in mismatches), mismatches


def test_a_pin_that_does_not_rest_at_its_base_fails_the_proof(monkeypatch: pytest.MonkeyPatch) -> None:
    files = [str(PROGRAMS_DIR / 'hexlib_tests' / '2params' / 'and.fj')]
    real_insert = assembler.BinaryData.insert_fj_op

    def unbased(self: Any, flip: int, jump: int) -> None:
        pinned, self.pinned = self.pinned, None
        real_insert(self, flip, jump)
        self.pinned = pinned

    monkeypatch.setattr(assembler.BinaryData, 'insert_fj_op', unbased)
    monkeypatch.setattr(assembler.BinaryData, 'unbaked_pins', lambda self: [])
    mismatches = prove_relocation(64, _macros(files, 64), _cli_pool(64)).mismatches
    assert any('does not rest at its value xor its base' in mismatch for mismatch in mismatches), mismatches

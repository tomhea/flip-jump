"""
unit-tests for the relocation proof (flipjump/assembler/relocation_proof.py): with a table pool, every program
of the test tables is the program without it, moved - and the proof sees a moved op that is corrupted, a table
cut short, and an offset from an outside label into a moved table.
"""

import csv
from pathlib import Path
from typing import Any, Dict, Iterator, List, Tuple

import pytest

from flipjump.assembler import relocation_proof
from flipjump.assembler.fj_parser import parse_macro_tree
from flipjump.assembler.inner_classes.expr import Expr
from flipjump.assembler.inner_classes.ops import FlipJump, Macro, MacroName, NewSegment
from flipjump.assembler.relocation_proof import relocation_mismatches
from flipjump.assembler.table_pool import BlockPool, TablePool
from flipjump.utils.exceptions import FlipJumpPreprocessorException
from flipjump.utils.functions import get_file_tuples
from tests.unit.test_table_pool import build_and_run, relocatable
from tests.unit.unit_utils import PROGRAMS_DIR

W = 32
POOL_BASE = 1 << 26
TABLES = PROGRAMS_DIR.parent / 'tests' / 'tests_tables'


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


@pytest.mark.parametrize('program', TEST_TABLE_PROGRAMS, ids=[program[0] for program in TEST_TABLE_PROGRAMS])
def test_every_test_program_is_the_same_program_with_the_pool(program: Tuple[str, List[str], int, bool]) -> None:
    _, files, memory_width, use_stl = program
    pool = BlockPool(memory_width, 1 << (memory_width - 1), one_pass=True)  # the pool of fj --pool-tables
    try:
        mismatches = relocation_mismatches(memory_width, _macros(files, memory_width, use_stl), pool)
    except FlipJumpPreprocessorException as refused:
        assert 'inside the table pool' in str(refused)  # prime_sieve's segment at the top of memory
        pytest.skip('the program reaches the pool')
    assert mismatches == []
    if not pool.allocated:
        pytest.skip('the program uses no relocatable table')


def test_a_tablepool_program_is_the_same_program_too(tmp_path: Path) -> None:
    files = [str(PROGRAMS_DIR / 'hexlib_tests' / '2params' / 'and.fj')]
    pool = TablePool(64, 1 << 63)
    assert relocation_mismatches(64, _macros(files, 64), pool) == [] and pool.allocated > 0


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

# the declaration holds three of the table's four entries: the fourth, reached at the start label + 3 ops, is
# outside it, so it stays behind when the table moves
SHORT_TABLE_PROGRAM = """
stl.startup_and_init_all
    hex.set x, 3
    go x
    stl.loop
x: hex.hex
def go x @ switch, end {
    wflip x+w, switch, x
    pad 4
    go.__relocatable__.table switch, end
    ;end
  end:
    wflip x+w, switch
    stl.output 'D'
}
""" + relocatable('go', 'switch, end', 'switch', '    ;end\n' * 3)


def _write(tmp_path: Path, source: str) -> List[str]:
    path = tmp_path / 'p.fj'
    path.write_text(source)
    return [str(path)]


def test_an_offset_from_outside_into_a_moved_table_fails_the_proof(tmp_path: Path) -> None:
    mismatches = relocation_mismatches(W, _macros(_write(tmp_path, OUTSIDE_OFFSET_PROGRAM), W), TablePool(W, POOL_BASE))
    assert any('(before + 128)' in mismatch for mismatch in mismatches), mismatches
    # and it is a miscompile: the moved program prints nothing where the plain one prints B
    assert build_and_run(OUTSIDE_OFFSET_PROGRAM, tmp_path, None, name='plain')[0] == b'B'
    assert build_and_run(OUTSIDE_OFFSET_PROGRAM, tmp_path, TablePool(W, POOL_BASE), name='pooled')[0] != b'B'


def test_a_table_declared_one_op_short_fails_the_proof(tmp_path: Path) -> None:
    mismatches = relocation_mismatches(W, _macros(_write(tmp_path, SHORT_TABLE_PROGRAM), W), TablePool(W, POOL_BASE))
    assert any('moved apart from the label before it' in mismatch for mismatch in mismatches), mismatches


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
                        op = FlipJump(op.flip, Expr(op.jump.exact_eval(labels) + 128), op.code_position)
                        done = True
                    yield op

        return Corrupted(), labels

    assert relocation_mismatches(64, _macros(files, 64), BlockPool(64, 1 << 63, one_pass=True)) == []
    monkeypatch.setattr('flipjump.assembler.relocation_proof.resolve_macros', corrupting)
    mismatches = relocation_mismatches(64, _macros(files, 64), BlockPool(64, 1 << 63, one_pass=True))
    assert len(mismatches) == 1 and 'with the pool' in mismatches[0], mismatches

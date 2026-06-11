"""
unit-tests for the assembler's stl-prefix parse cache (flipjump/assembler/fj_parser.py).

the parser state after the leading stl files is snapshotted once and reused by later
assembles in the same process. pinned here: cache hits produce bit-identical outputs,
the cache is keyed by file mtime/size + memory-width (so edits and width changes
invalidate it), and non-stl files are never cached.
"""

from pathlib import Path
from typing import Dict, List, Tuple

import pytest

from flipjump.assembler import fj_parser
from tests.unit.unit_utils import HELLO_NO_STL, assemble_to_path


@pytest.fixture()
def isolated_cache(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    """redirect the cacheable directory to a temp 'stl' and start with an empty cache."""
    fake_stl_dir = tmp_path / 'stl'
    fake_stl_dir.mkdir()
    monkeypatch.setattr(fj_parser, '_STL_DIR', fake_stl_dir.resolve())
    empty_cache: Dict[fj_parser._StlCacheKey, fj_parser._StlCacheValue] = {}
    monkeypatch.setattr(fj_parser, '_stl_prefix_cache', empty_cache)
    return fake_stl_dir


def make_files(fake_stl_dir: Path, tmp_path: Path) -> List[Tuple[str, Path]]:
    """one cacheable 'stl' file (a macro definition) + one user file using it."""
    stl_file = fake_stl_dir / 'lib.fj'
    stl_file.write_text('def looper @ loop_label {\n  loop_label:\n    ;loop_label\n}\n')
    user_file = tmp_path / 'prog.fj'
    user_file.write_text('looper\n')
    return [('s1', stl_file), ('f1', user_file)]


def test_prefix_length_counts_only_the_leading_stl_files(isolated_cache: Path, tmp_path: Path) -> None:
    files = make_files(isolated_cache, tmp_path)
    assert fj_parser._stl_prefix_length(files) == 1
    assert fj_parser._stl_prefix_length(files[::-1]) == 0  # the user file leads - nothing cacheable
    assert fj_parser._stl_prefix_length([files[0], files[0]]) == 2


def test_cache_hit_returns_the_same_macros(isolated_cache: Path, tmp_path: Path) -> None:
    files = make_files(isolated_cache, tmp_path)

    first_macros = fj_parser.parse_macro_tree(files, 64, warning_as_errors=False)
    assert len(fj_parser._stl_prefix_cache) == 1

    second_macros = fj_parser.parse_macro_tree(files, 64, warning_as_errors=False)
    assert len(fj_parser._stl_prefix_cache) == 1  # reused, not re-added
    assert first_macros.keys() == second_macros.keys()


def test_cache_is_invalidated_when_a_cached_file_changes(isolated_cache: Path, tmp_path: Path) -> None:
    files = make_files(isolated_cache, tmp_path)
    fj_parser.parse_macro_tree(files, 64, warning_as_errors=False)
    assert len(fj_parser._stl_prefix_cache) == 1

    # rewrite the cacheable file (different size => different key, even with a same-second mtime)
    files[0][1].write_text('def looper @ loop_label {\n  loop_label:\n    ;loop_label\n}\n// changed\n')
    fj_parser.parse_macro_tree(files, 64, warning_as_errors=False)
    assert len(fj_parser._stl_prefix_cache) == 2


def test_cache_is_keyed_by_memory_width(isolated_cache: Path, tmp_path: Path) -> None:
    files = make_files(isolated_cache, tmp_path)
    fj_parser.parse_macro_tree(files, 64, warning_as_errors=False)
    fj_parser.parse_macro_tree(files, 32, warning_as_errors=False)
    assert len(fj_parser._stl_prefix_cache) == 2


def test_user_only_files_are_never_cached(isolated_cache: Path, tmp_path: Path) -> None:
    program = tmp_path / 'prog.fj'
    program.write_text('loop_label:\n;loop_label\n')
    fj_parser.parse_macro_tree([('f1', program)], 64, warning_as_errors=False)
    assert len(fj_parser._stl_prefix_cache) == 0


def test_assembling_twice_in_one_process_is_bit_identical(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # the real stl, from a cold cache: the first assemble fills it, the second hits it,
    # and the outputs are byte-identical
    cold_cache: Dict[fj_parser._StlCacheKey, fj_parser._StlCacheValue] = {}
    monkeypatch.setattr(fj_parser, '_stl_prefix_cache', cold_cache)
    (tmp_path / 'a').mkdir()
    (tmp_path / 'b').mkdir()
    first = assemble_to_path(HELLO_NO_STL.read_text(), tmp_path / 'a', use_stl=True)
    assert len(cold_cache) == 1  # the stl prefix was snapshotted
    second = assemble_to_path(HELLO_NO_STL.read_text(), tmp_path / 'b', use_stl=True)
    assert len(cold_cache) == 1  # ... and reused
    assert first.read_bytes() == second.read_bytes()

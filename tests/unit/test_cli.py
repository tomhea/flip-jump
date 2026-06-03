"""
unit-tests for the command-line interface (flipjump/flipjump_cli.py).

drives the public assemble_run_according_to_cmd_line_args entry-point with argument lists,
and checks get_version's defaulting/validation logic.
"""

from pathlib import Path

import pytest

from flipjump import assemble_run_according_to_cmd_line_args
from flipjump.fjm.fjm_consts import FJMVersion
from flipjump.fjm.fjm_reader import Reader
from flipjump.flipjump_cli import get_version
from tests.unit.unit_utils import HELLO_NO_STL, assemble_to_path


def _write_hello(tmp_path: Path) -> Path:
    fj_path = tmp_path / 'hello.fj'
    fj_path.write_text(HELLO_NO_STL.read_text())
    return fj_path


def test_cli_assemble_only(tmp_path: Path) -> None:
    fj_path = _write_hello(tmp_path)
    out_path = tmp_path / 'out.fjm'
    assemble_run_according_to_cmd_line_args(
        cmd_line_args=['--asm', '-o', str(out_path), '--no_stl', '-w', '32', '-s', str(fj_path)]
    )
    assert out_path.is_file()
    assert Reader(out_path).memory_width == 32


def test_cli_run_only(tmp_path: Path) -> None:
    fjm_path = assemble_to_path(HELLO_NO_STL.read_text(), tmp_path)
    assemble_run_according_to_cmd_line_args(cmd_line_args=['--run', '-s', '--no_output', str(fjm_path)])


def test_cli_assemble_and_run(tmp_path: Path) -> None:
    fj_path = _write_hello(tmp_path)
    assemble_run_according_to_cmd_line_args(cmd_line_args=['--no_stl', '-s', '--no_output', str(fj_path)])


def test_cli_mutually_exclusive_asm_run(tmp_path: Path) -> None:
    fj_path = _write_hello(tmp_path)
    with pytest.raises(SystemExit):
        assemble_run_according_to_cmd_line_args(cmd_line_args=['-a', '-r', str(fj_path)])


def test_cli_invalid_width(tmp_path: Path) -> None:
    fj_path = _write_hello(tmp_path)
    out_path = tmp_path / 'out.fjm'
    with pytest.raises(SystemExit):
        assemble_run_according_to_cmd_line_args(
            cmd_line_args=['--asm', '-o', str(out_path), '--no_stl', '-w', '7', str(fj_path)]
        )


def test_cli_missing_file(tmp_path: Path) -> None:
    out_path = tmp_path / 'out.fjm'
    with pytest.raises(SystemExit):
        assemble_run_according_to_cmd_line_args(
            cmd_line_args=['--asm', '-o', str(out_path), '--no_stl', str(tmp_path / 'does_not_exist.fj')]
        )


def _no_error(message: str) -> None:
    raise AssertionError(f'unexpected error: {message}')


def test_get_version_default_with_outfile() -> None:
    assert get_version(None, True, _no_error) == FJMVersion.CompressedVersion


def test_get_version_default_without_outfile() -> None:
    assert get_version(None, False, _no_error) == FJMVersion.NormalVersion


def test_get_version_explicit() -> None:
    assert get_version(2, False, _no_error) == FJMVersion.RelativeJumpVersion


def test_get_version_invalid_calls_error() -> None:
    def raise_error(message: str) -> None:
        raise SystemExit(message)

    with pytest.raises(SystemExit):
        get_version(99, False, raise_error)

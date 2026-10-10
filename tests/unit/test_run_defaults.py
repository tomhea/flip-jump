"""
unit-tests for the program's own run defaults in the python API (flipjump/interpreter/run_defaults.py, used by
flipjump_quickstart.run / debug and by the `fj` command line alike): the io device and the flat-memory window
the .fjm's header asks for, the assemble_and_* helpers compiling them in, and the package's exports.
"""

import struct
from pathlib import Path
from typing import Any, Dict, List

import pytest

import flipjump
from flipjump import flipjump_quickstart
from flipjump.fjm.fjm_consts import IO_MODE_NAMES, IO_MODE_PC, RUN_FLAG_FLAT_MEMORY, _header_base_size
from flipjump.fjm.fjm_reader import read_fjm_header
from flipjump.interpreter import fjm_run
from flipjump.interpreter.io_devices.cli_devices import IO_MODES
from flipjump.interpreter.io_devices.StandardIO import StandardIO
from flipjump.interpreter.run_defaults import FLAT_MEMORY_AUTO_MAX_WORDS
from flipjump.utils.exceptions import FlipJumpFlatMemoryException
from tests.unit.unit_utils import MINIMAL_STARTUP, assemble_to_path, native_engine_required


@pytest.fixture(autouse=True)
def clean_flat_mode_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for var in ('FLIPJUMP_NO_NATIVE', 'FLIPJUMP_NO_FLAT', 'FLIPJUMP_FLAT_MAX_WORDS', 'FLIPJUMP_TEST_FLAT_ALLOC_FAIL'):
        monkeypatch.delenv(var, raising=False)


def _program(top: int) -> str:
    """a w=32 looping program whose small reserved segment ends 4 words past `top` (its span)"""
    return MINIMAL_STARTUP + f'\nstartup\nloop: ;loop\n\nsegment {top} * w\nreserve 4 * w\n'


def _patch_header(path: Path, *, run_flags: int = 0, io_mode: int = 0) -> None:
    raw = bytearray(path.read_bytes())
    struct.pack_into('<LL', raw, _header_base_size, run_flags, io_mode)
    path.write_bytes(bytes(raw))


def _spy_engine(monkeypatch: pytest.MonkeyPatch) -> List[Dict[str, Any]]:
    """record what the python API hands the engine (fjm_run.run's window arguments)"""
    seen: List[Dict[str, Any]] = []
    real_run = fjm_run.run

    def spy(*args: Any, **kwargs: Any) -> Any:
        stats = real_run(*args, **kwargs)
        seen.append(
            {'words': kwargs.get('flat_max_words'), 'required': kwargs.get('flat_required'), 'mode': stats.storage_mode}
        )
        return stats

    monkeypatch.setattr(fjm_run, 'run', spy)
    return seen


def test_every_compiled_io_mode_names_a_real_io_device() -> None:
    # the header's io modes and the --io devices are two tables; a mode with no device would break `fj --run`
    assert set(IO_MODE_NAMES.values()) <= set(IO_MODES)


def test_the_package_exports_the_run_header_api() -> None:
    for name in ('IO_MODE_STANDARD', 'IO_MODE_PC', 'RUN_FLAG_FLAT_MEMORY', 'FjmHeader', 'read_fjm_header'):
        assert hasattr(flipjump, name) and name in flipjump.__all__


@pytest.mark.parametrize('io_mode, expected', [(0, 'standard'), (IO_MODE_PC, 'pc')])
def test_run_without_a_device_uses_the_compiled_io_mode(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, io_mode: int, expected: str
) -> None:
    fjm_path = assemble_to_path(_program(1 << 10), tmp_path, memory_width=32)
    _patch_header(fjm_path, io_mode=io_mode)
    modes: List[str] = []

    def make(mode: str) -> Any:
        modes.append(mode)
        return StandardIO(False)

    monkeypatch.setattr(flipjump_quickstart, 'make_io_device', make)
    flipjump_quickstart.run(fjm_path, print_time=False, print_termination=False)
    assert modes == [expected]
    # an explicit device always wins: the compiled mode is not even looked at
    flipjump_quickstart.run(fjm_path, io_device=StandardIO(False), print_time=False, print_termination=False)
    assert modes == [expected]


@native_engine_required
def test_run_follows_the_compiled_flat_memory_flag_and_the_overrides(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    top = FLAT_MEMORY_AUTO_MAX_WORDS  # a span over the automatic limit
    span = top + 4
    fjm_path = assemble_to_path(_program(top), tmp_path, memory_width=32)
    seen = _spy_engine(monkeypatch)

    def run(**kwargs: Any) -> Dict[str, Any]:
        flipjump_quickstart.run(
            fjm_path, io_device=StandardIO(False), print_time=False, print_termination=False, **kwargs
        )
        return seen[-1]

    assert run() == {'words': None, 'required': False, 'mode': 'hybrid'}
    assert run(flat_memory=True) == {'words': span, 'required': True, 'mode': 'flat'}
    assert run(run_flags=RUN_FLAG_FLAT_MEMORY) == {'words': span, 'required': True, 'mode': 'flat'}
    _patch_header(fjm_path, run_flags=RUN_FLAG_FLAT_MEMORY)
    assert run() == {'words': span, 'required': True, 'mode': 'flat'}
    assert run(run_flags=0) == {'words': None, 'required': False, 'mode': 'hybrid'}
    assert run(flat_max_words=4) == {'words': 4, 'required': False, 'mode': 'hybrid'}


@native_engine_required
def test_a_small_program_runs_flat_from_the_api_too(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fjm_path = assemble_to_path(_program(1 << 10), tmp_path, memory_width=32)
    seen = _spy_engine(monkeypatch)
    flipjump_quickstart.run(fjm_path, io_device=StandardIO(False), print_time=False, print_termination=False)
    assert seen == [{'words': (1 << 10) + 4, 'required': False, 'mode': 'flat'}]


@native_engine_required
def test_a_failed_compiled_flat_memory_says_how_to_run_it_from_the_api(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fjm_path = assemble_to_path(_program(FLAT_MEMORY_AUTO_MAX_WORDS), tmp_path, memory_width=32)
    _patch_header(fjm_path, run_flags=RUN_FLAG_FLAT_MEMORY)
    monkeypatch.setenv('FLIPJUMP_TEST_FLAT_ALLOC_FAIL', '1')
    with pytest.raises(FlipJumpFlatMemoryException, match='--run-flags 0 might fix that'):
        flipjump_quickstart.run(fjm_path, io_device=StandardIO(False), print_time=False, print_termination=False)


@pytest.mark.parametrize('helper', ['assemble_and_run', 'assemble_and_debug', 'assemble_and_run_test_output'])
def test_the_assemble_and_helpers_compile_the_flags_in(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, helper: str
) -> None:
    fj_path = tmp_path / 'p.fj'
    fj_path.write_text(MINIMAL_STARTUP + '\nstartup\nloop: ;loop\n')
    headers: List[Any] = []
    real_debug = flipjump_quickstart.debug

    def debug(fjm_path: Path, *args: Any, **kwargs: Any) -> Any:
        headers.append(read_fjm_header(fjm_path))
        kwargs['io_device'] = StandardIO(False)  # the compiled mode is pc: no window in a test
        return real_debug(fjm_path, *args, **kwargs)

    monkeypatch.setattr(flipjump_quickstart, 'debug', debug)
    monkeypatch.setattr(flipjump_quickstart, 'run_test_output', _run_test_output_through(debug))
    flags = {'run_flags': RUN_FLAG_FLAT_MEMORY, 'io_mode': IO_MODE_PC}
    kwargs: Dict[str, Any] = {'use_stl': False, 'memory_width': 32, 'print_time': False, 'print_termination': False}
    if helper == 'assemble_and_run_test_output':
        getattr(flipjump_quickstart, helper)([fj_path], b'', b'', **kwargs, **flags)
    else:
        getattr(flipjump_quickstart, helper)([fj_path], **kwargs, **flags)
    assert [(h.run_flags, h.io_mode) for h in headers] == [(RUN_FLAG_FLAT_MEMORY, IO_MODE_PC)]


def _run_test_output_through(debug: Any) -> Any:
    """run_test_output, routed through the spying debug (it calls fjm_run directly otherwise)"""

    def run_test_output(fjm_path: Path, fixed_input: bytes, expected_output: bytes, **kwargs: Any) -> bool:
        debug(fjm_path, None, print_time=False, print_termination=False)
        return True

    return run_test_output

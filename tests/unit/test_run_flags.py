"""
unit-tests for what a .fjm carries about how to run it, and for loading it.

the header's run flags and io mode (`fj --run-flags N` / `--io-mode N` compile them in; `--run-flags` and
`--io` override them at run time), the flat window the CLI derives from them, the error a forced flat
memory gives when it cannot be allocated, and the lean native load (the .fjm's bytes straight into the
engine, no python object per word) - pinned against the Reader's memory, word for word.
"""

import lzma
import struct
from pathlib import Path
from typing import Any, List, Optional, Tuple

import pytest

from flipjump import assemble_run_according_to_cmd_line_args
from flipjump import flipjump_cli
from flipjump.fjm.fjm_consts import (
    FJMVersion,
    IO_MODE_PC,
    IO_MODE_STANDARD,
    RUN_FLAG_FLAT_MEMORY,
    _LZMA_FORMAT,
    _lzma_compression_filters,
    _header_base_size,
)
from flipjump.fjm.fjm_reader import Reader, read_fjm_header
from flipjump.fjm.fjm_writer import Writer
from flipjump.interpreter import fjm_run
from flipjump.interpreter.io_devices.StandardIO import StandardIO
from flipjump.utils.exceptions import FlipJumpReadFjmException, FlipJumpWriteFjmException
from flipjump.utils.progress import ProgressBar
from tests.unit.unit_utils import MINIMAL_STARTUP, PROGRAMS_DIR, assemble_to_path, native_engine_required

try:
    from flipjump.interpreter import _fjcore  # type: ignore[attr-defined]
except ImportError:
    _fjcore = None


@pytest.fixture(autouse=True)
def clean_flat_mode_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for var in ('FLIPJUMP_NO_NATIVE', 'FLIPJUMP_NO_FLAT', 'FLIPJUMP_FLAT_MAX_WORDS', 'FLIPJUMP_TEST_FLAT_ALLOC_FAIL'):
        monkeypatch.delenv(var, raising=False)


def _write_simple(path: Path, version: FJMVersion = FJMVersion.NormalVersion, **flags: int) -> Path:
    writer = Writer(path, 16, version, **flags)
    writer.add_simple_segment_with_data(0, [0, 0])
    writer.write_to_file()
    return path


# --- the header ---


def test_the_flags_are_two_u32s_after_the_base_header(tmp_path: Path) -> None:
    # `u64 flags` became `u32 run_flags; u32 io_mode` - same 12 header-extension bytes, so files
    # written before (all with flags 0) read unchanged
    path = _write_simple(tmp_path / 'x.fjm', run_flags=RUN_FLAG_FLAT_MEMORY, io_mode=IO_MODE_PC)
    raw = path.read_bytes()
    assert struct.unpack_from('<LLL', raw, _header_base_size) == (RUN_FLAG_FLAT_MEMORY, IO_MODE_PC, 0)
    header = read_fjm_header(path)
    assert (header.run_flags, header.io_mode) == (RUN_FLAG_FLAT_MEMORY, IO_MODE_PC)
    reader = Reader(path)
    assert (reader.run_flags, reader.io_mode) == (RUN_FLAG_FLAT_MEMORY, IO_MODE_PC)


def test_the_flags_default_to_zero(tmp_path: Path) -> None:
    header = read_fjm_header(_write_simple(tmp_path / 'x.fjm'))
    assert (header.run_flags, header.io_mode) == (0, IO_MODE_STANDARD)


def test_a_base_version_file_has_no_flags(tmp_path: Path) -> None:
    header = read_fjm_header(_write_simple(tmp_path / 'x.fjm', FJMVersion.BaseVersion))
    assert (header.run_flags, header.io_mode) == (0, 0)
    for flags in ({'run_flags': 1}, {'io_mode': 1}):
        with pytest.raises(FlipJumpWriteFjmException):
            Writer(tmp_path / 'y.fjm', 16, FJMVersion.BaseVersion, **flags)


@pytest.mark.parametrize('flags', [{'run_flags': 2}, {'run_flags': 3}, {'run_flags': 1 << 31}, {'io_mode': 2}])
def test_the_writer_rejects_bad_flags(tmp_path: Path, flags: Any) -> None:
    with pytest.raises(FlipJumpWriteFjmException, match='bad'):
        Writer(tmp_path / 'x.fjm', 16, FJMVersion.NormalVersion, **flags)


@pytest.mark.parametrize('offset, value', [(0, 2), (0, 0x80000000), (4, 2), (4, 0xFFFFFFFF)])
def test_the_reader_rejects_bad_flags(tmp_path: Path, offset: int, value: int) -> None:
    # offset 0 is run_flags, 4 is io_mode: anything but the defined values is a bad-flags error
    path = _write_simple(tmp_path / 'x.fjm')
    raw = bytearray(path.read_bytes())
    struct.pack_into('<L', raw, _header_base_size + offset, value)
    path.write_bytes(bytes(raw))
    for read in (read_fjm_header, Reader):
        with pytest.raises(FlipJumpReadFjmException, match='bad flags'):
            read(path)


# --- the CLI: compiling the flags in ---


def _looping_source() -> str:
    return MINIMAL_STARTUP + '\nstartup\nloop: ;loop\n'


def test_cli_compiles_the_flags_into_the_fjm(tmp_path: Path) -> None:
    fj_path = tmp_path / 'p.fj'
    fj_path.write_text(_looping_source())
    out = tmp_path / 'out.fjm'
    assemble_run_according_to_cmd_line_args(
        cmd_line_args=['--asm', '-s', '--no_stl', '-o', str(out), '--io-mode', '1', '--run-flags', '1', str(fj_path)]
    )
    header = read_fjm_header(out)
    assert (header.run_flags, header.io_mode) == (RUN_FLAG_FLAT_MEMORY, IO_MODE_PC)


@pytest.mark.parametrize(
    'argument, value', [('--io-mode', '2'), ('--io-mode', '-1'), ('--run-flags', '2'), ('--run-flags', '6')]
)
def test_cli_rejects_bad_flag_values(argument: str, value: str, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        flipjump_cli.parse_arguments(cmd_line_args=['--asm', '-o', 'o.fjm', argument, value, 'a.fj'])
    assert 'bad' in capsys.readouterr().err


def test_the_old_flags_option_is_gone() -> None:
    with pytest.raises(SystemExit):
        flipjump_cli.parse_arguments(cmd_line_args=['--asm', '-o', 'o.fjm', '--flags', '1', 'a.fj'])


# --- the CLI: running by the compiled flags ---


def _spy_io_modes(monkeypatch: pytest.MonkeyPatch) -> List[str]:
    """record the io mode the CLI builds its device for (and give it a standard device, no window)"""
    modes: List[str] = []

    def make(mode: str) -> Any:
        modes.append(mode)
        return StandardIO(False)

    monkeypatch.setattr(flipjump_cli, 'make_io_device', make)
    return modes


def test_the_compiled_io_mode_picks_the_device_and_io_overrides_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fjm_path = assemble_to_path(_looping_source(), tmp_path)
    for io_mode, extra, expected in (
        (IO_MODE_STANDARD, [], 'standard'),
        (IO_MODE_PC, [], 'pc'),
        (IO_MODE_PC, ['--io', 'standard'], 'standard'),
        (IO_MODE_STANDARD, ['--io', 'pc'], 'pc'),
    ):
        raw = bytearray(fjm_path.read_bytes())
        struct.pack_into('<L', raw, _header_base_size + 4, io_mode)
        fjm_path.write_bytes(bytes(raw))
        modes = _spy_io_modes(monkeypatch)
        assemble_run_according_to_cmd_line_args(cmd_line_args=['--run', '-s', *extra, str(fjm_path)])
        assert modes == [expected], (io_mode, extra)


# w=32 looping programs whose small reserved segment ends 4 words past `top` (the span decides the window)
def _high_segment_program(top: int) -> str:
    return MINIMAL_STARTUP + f'\nstartup\nloop: ;loop\n\nsegment {top} * w\nreserve 4 * w\n'


_BIG_TOP = flipjump_cli.FLAT_MEMORY_AUTO_MAX_WORDS


def _set_run_flags(fjm_path: Path, run_flags: int) -> None:
    raw = bytearray(fjm_path.read_bytes())
    struct.pack_into('<L', raw, _header_base_size, run_flags)
    fjm_path.write_bytes(bytes(raw))


def _run_and_spy(
    fjm_path: Path, monkeypatch: pytest.MonkeyPatch, extra: List[str]
) -> Tuple[Optional[int], bool, Optional[str]]:
    """run once; -> (flat_max_words passed, flat_required passed, storage mode)"""
    seen: List[Tuple[Optional[int], bool, Optional[str]]] = []
    real_run = fjm_run.run

    def spy(*a: Any, **kw: Any) -> Any:
        stats = real_run(*a, **kw)
        seen.append((kw.get('flat_max_words'), kw.get('flat_required', False), stats.storage_mode))
        return stats

    monkeypatch.setattr(fjm_run, 'run', spy)
    assemble_run_according_to_cmd_line_args(cmd_line_args=['--run', '-s', *extra, str(fjm_path)])
    monkeypatch.setattr(fjm_run, 'run', real_run)
    return seen[0]


@native_engine_required
def test_the_flat_memory_run_flag_runs_flat_and_run_flags_overrides_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # a span over the automatic limit: without the flag the engine's default window ('hybrid')
    fjm_path = assemble_to_path(_high_segment_program(_BIG_TOP), tmp_path, memory_width=32)
    span = _BIG_TOP + 4
    assert _run_and_spy(fjm_path, monkeypatch, []) == (None, False, 'hybrid')
    assert _run_and_spy(fjm_path, monkeypatch, ['--run-flags', '1']) == (span, True, 'flat')
    _set_run_flags(fjm_path, RUN_FLAG_FLAT_MEMORY)
    assert _run_and_spy(fjm_path, monkeypatch, []) == (span, True, 'flat')
    assert _run_and_spy(fjm_path, monkeypatch, ['--run-flags', '0']) == (None, False, 'hybrid')
    # the explicit window options still win over the compiled flag
    assert _run_and_spy(fjm_path, monkeypatch, ['--flat-max-words', '4']) == (4, False, 'hybrid')


@native_engine_required
@pytest.mark.parametrize(
    'compiled, extra, advice',
    [
        (RUN_FLAG_FLAT_MEMORY, [], '--run-flags 0'),
        (0, ['--run-flags', '1'], '--run-flags 0'),
        (0, ['--flat-memory'], 'without --flat-memory'),
    ],
)
def test_a_forced_flat_memory_that_cannot_be_allocated_says_how_to_run_anyway(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    compiled: int,
    extra: List[str],
    advice: str,
) -> None:
    fjm_path = assemble_to_path(_high_segment_program(_BIG_TOP), tmp_path, memory_width=32)
    _set_run_flags(fjm_path, compiled)
    monkeypatch.setenv('FLIPJUMP_TEST_FLAT_ALLOC_FAIL', '1')
    with pytest.raises(SystemExit) as exit_info:
        assemble_run_according_to_cmd_line_args(cmd_line_args=['--run', '-s', *extra, str(fjm_path)])
    message = str(exit_info.value.code)
    assert advice in message and 'at a cost of speed' in message
    assert f'{_BIG_TOP + 4:,} words' in message


@native_engine_required
def test_an_unforced_flat_window_still_falls_back_to_paged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    # the automatic window (a small span, no flag) was not asked for: a failed allocation runs paged
    fjm_path = assemble_to_path(_high_segment_program(1 << 10), tmp_path, memory_width=32)
    monkeypatch.setenv('FLIPJUMP_TEST_FLAT_ALLOC_FAIL', '1')
    assert _run_and_spy(fjm_path, monkeypatch, [])[2] == 'paged'
    assert 'running paged' in capfd.readouterr().err


# --- the lean native load ---


def _lean_load(fjm_path: Path, flat_max_words: Optional[int] = None) -> Any:
    with ProgressBar('', print_time=False) as progress:
        core, _memory_width = fjm_run._load_native(fjm_path, flat_max_words, False, progress)
    return core


def _assert_loaded_like_the_reader(fjm_path: Path, flat_max_words: Optional[int] = None) -> None:
    reader = Reader(fjm_path)
    core = _lean_load(fjm_path, flat_max_words)
    mismatches = [address for address, value in reader.memory.items() if core.get_word(address) != value]
    assert not mismatches, f'{len(mismatches)} words differ, first at {hex(mismatches[0])}'
    for start, end in reader.zeros_boundaries:  # the long reserved tails the Reader leaves implicit
        assert core.get_word(start) == 0 and core.get_word(end - 1) == 0


_TWO_SEGMENTS = (
    MINIMAL_STARTUP
    + '''
startup
loop: ;loop
a: ;a
b: a+3;b
segment 0x4000
c: ;loop
d: c+5;c
reserve 2000 * w
'''
)


@native_engine_required
@pytest.mark.parametrize('version', list(FJMVersion))
@pytest.mark.parametrize('memory_width', [16, 32, 64])  # (w=8 has 32 words: too small for this program)
def test_the_lean_load_equals_the_reader(tmp_path: Path, version: FJMVersion, memory_width: int) -> None:
    # every version (v2/v3 store the jump words relative to their address) and every width
    fjm_path = assemble_to_path(_TWO_SEGMENTS, tmp_path, memory_width=memory_width, fjm_version=version)
    _assert_loaded_like_the_reader(fjm_path)


@native_engine_required
@pytest.mark.parametrize('flat_max_words', [None, 4, 0x4001])
def test_the_lean_load_equals_the_reader_in_every_storage_mode(tmp_path: Path, flat_max_words: Optional[int]) -> None:
    # 'flat', and two 'hybrid' windows - one cutting into the second segment: the words above the
    # window must land in the paged part
    fjm_path = assemble_to_path(_TWO_SEGMENTS, tmp_path, memory_width=32, fjm_version=FJMVersion.CompressedVersion)
    _assert_loaded_like_the_reader(fjm_path, flat_max_words)


_COMPILED_PROGRAMS = sorted((PROGRAMS_DIR.parent / 'tests' / 'compiled').rglob('*.fjm'))


@native_engine_required
@pytest.mark.skipif(not _COMPILED_PROGRAMS, reason='no compiled test programs (run the compile tests first)')
def test_the_lean_load_equals_the_reader_on_the_compiled_test_programs() -> None:
    for fjm_path in _COMPILED_PROGRAMS[:40]:
        _assert_loaded_like_the_reader(fjm_path)


@native_engine_required
def test_the_lean_load_check_catches_a_wrong_word(tmp_path: Path) -> None:
    # the negative control of the checks above: one flipped bit in the loaded image is seen
    fjm_path = assemble_to_path(_TWO_SEGMENTS, tmp_path, memory_width=32, fjm_version=FJMVersion.CompressedVersion)
    reader, core = Reader(fjm_path), _lean_load(fjm_path)
    address = reader.memory_segments[1].segment_start + 1  # a relative jump word
    core.set_word(address, core.get_word(address) ^ 1)
    assert core.get_word(address) != reader.memory[address]


@native_engine_required
def test_set_words_bytes_reads_little_endian_words_and_restores_relative_jumps() -> None:
    core = _fjcore.Memory(16)
    core.add_segment(0x100, 4)
    data = struct.pack('<6H', 0xAAAA, 1, 2, 0x10, 0xFFFF, 0x20)
    core.set_words_bytes(0x100, data, 2, 4, True)
    # words 2..5 of the data; odd words get + (address * w)
    assert [core.get_word(0x100 + i) for i in range(4)] == [
        2,
        (0x10 + 0x101 * 16) & 0xFFFF,
        0xFFFF,
        (0x20 + 0x103 * 16) & 0xFFFF,
    ]
    with pytest.raises(ValueError):
        core.set_words_bytes(0x100, data, 4, 3, False)  # words 4..6 of a 6-word buffer


@native_engine_required
def test_decide_storage_with_flat_required_raises_memory_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv('FLIPJUMP_TEST_FLAT_ALLOC_FAIL', '1')
    core = _fjcore.Memory(32, flat_required=True)
    core.add_segment(0, 8)
    with pytest.raises(MemoryError):
        core.decide_storage()
    relaxed = _fjcore.Memory(32)
    relaxed.add_segment(0, 8)
    relaxed.decide_storage()  # the default: warn and run paged
    assert relaxed.storage_mode == 'paged'


# --- the writer's chunked compression ---


@pytest.mark.parametrize('size', [0, 1, 999, (1 << 20) + 7, 3 * (1 << 20)])
def test_chunked_compression_equals_one_shot(tmp_path: Path, size: int) -> None:
    # the compression is fed in chunks (to show its progress); its bytes must be exactly lzma.compress's
    data = bytes((i * 2654435761 >> 13) & 0xFF if i % 7 else 0 for i in range(size))
    writer = Writer(tmp_path / 'x.fjm', 32, FJMVersion.CompressedVersion)
    chunked = writer._compress_data(data)
    one_shot = lzma.compress(data, format=_LZMA_FORMAT, filters=_lzma_compression_filters(64, writer.lzma_preset))
    assert chunked == one_shot

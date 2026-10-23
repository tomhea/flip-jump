"""
end-to-end tests for the io-devices: an .fj program drives the InMemoryScreen over the output
stream with io_devices/README.md's commands (golden frame-hash + PNG output), a scripted keyboard
replays deterministically into an .fj polling loop, and the complete PcIO device (screen + keyboard
together) runs a program.
"""

import hashlib
from pathlib import Path

import pytest

from flipjump.interpreter import fjm_run
from flipjump.interpreter.io_devices.KeyboardIO import KeyboardIO, ScriptedKeyEventSource
from flipjump.interpreter.io_devices.ScreenIO import XTERM256, InMemoryScreen
from flipjump.interpreter.io_devices.pygame_window import PcIO
from flipjump.utils.classes import TerminationCause
from tests.unit.unit_utils import assemble_to_path

# the screen stream of io_devices/README.md: init_screen 4x2 format 8; define_palette slot 0, entries 0-1;
# draw_raw 0,1,0,1 / 1,0,1,0; present. The program outputs it byte by byte.
SCREEN_STREAM = (
    bytes([0x01, 4, 0, 2, 0, 8])
    + bytes([0x02, 0, 0, 1, 10, 20, 30, 200, 100, 0])
    + bytes([0x10, 0, 1, 0, 1, 1, 0, 1, 0])
    + bytes([0x1F])
)
SCREEN_PROGRAM = 'stl.startup\n' + ''.join(f'stl.output_char {byte}\n' for byte in SCREEN_STREAM) + 'stl.loop\n'

# the hash of a format-8 frame: the values, one byte each, then all 256 entries of the presented palette
EXPECTED_FRAME_HASH = hashlib.sha256(
    bytes([0, 1, 0, 1, 1, 0, 1, 0])
    + bytes([10, 20, 30, 200, 100, 0])
    + b''.join(bytes(colour) for colour in XTERM256[2:])
).hexdigest()

# 3-bit colours, written BIT by bit (stl.output_bit): init 8x1 format 3, then draw_raw of 1..7, 0 - the
# README's "8 pixels of 3 bits take 3 bytes" - then present.
PACKED_PROGRAM = (
    'stl.startup\n'
    + ''.join(f'stl.output_char {byte}\n' for byte in [0x01, 8, 0, 1, 0, 3, 0x10])
    + ''.join(f'stl.output_bit {(value >> i) & 1}\n' for value in [1, 2, 3, 4, 5, 6, 7, 0] for i in range(3))
    + 'stl.output_char 0x1F\nstl.loop\n'
)

# a program whose stream is wrong: a stray zero byte where a command should start
BAD_SCREEN_PROGRAM = SCREEN_PROGRAM.replace('stl.output_char 31\n', 'stl.output_char 0\n')
assert BAD_SCREEN_PROGRAM != SCREEN_PROGRAM


# polls the keyboard 5 tics (one status HEX each: 0x0 idle, 0x8 key-up, 0x9 key-down):
# prints D/U + the keycode char per event, '.' when idle, and '!' at the end.
KEYBOARD_PROGRAM = """
stl.startup_and_init_all

rep(5, i) poll_once

stl.output '!'
stl.loop

def poll_once @ event, down, up, after_downup, no_event, end < status, keycode, KEY_DOWN {
    hex.input_hex status
    hex.if status, no_event, event
  event:
    hex.input keycode
    hex.cmp 1, status, KEY_DOWN, up, down, up
  down:
    stl.output 'D'
    ;after_downup
  up:
    stl.output 'U'
  after_downup:
    hex.print keycode
    ;end
  no_event:
    stl.output '.'
  end:
}

status:   hex.hex
keycode:  hex.vec 2
KEY_DOWN: hex.hex 9
"""


def test_fj_program_drives_the_screen(tmp_path: Path, engine: str) -> None:
    fjm_path = assemble_to_path(SCREEN_PROGRAM, tmp_path, use_stl=True)
    frames_dir = tmp_path / 'frames'
    screen = InMemoryScreen(frames_dir=frames_dir)

    statistics = fjm_run.run(fjm_path, io_device=screen, print_time=False)

    assert statistics.termination_cause == TerminationCause.Looping
    assert screen.frame_count == 1
    assert screen.frame_hashes[0][1] == EXPECTED_FRAME_HASH
    assert (frames_dir / 'frame_000000.png').exists()
    assert screen.last_frame_rgb[:2] == [(10, 20, 30), (200, 100, 0)]
    assert screen.get_output() == b''  # the output ended between commands


def test_fj_program_packs_3_bit_colours(tmp_path: Path, engine: str) -> None:
    fjm_path = assemble_to_path(PACKED_PROGRAM, tmp_path, use_stl=True)
    screen = InMemoryScreen()
    statistics = fjm_run.run(fjm_path, io_device=screen, print_time=False)
    assert statistics.termination_cause == TerminationCause.Looping
    assert screen.frame_count == 1
    assert screen.pixel_indices == [1, 2, 3, 4, 5, 6, 7, 0]


def test_control_a_bad_stream_stops_the_run(tmp_path: Path, engine: str) -> None:
    fjm_path = assemble_to_path(BAD_SCREEN_PROGRAM, tmp_path, use_stl=True)
    screen = InMemoryScreen()
    # the engines report the device's error differently (the native run wraps it), but both stop on it
    with pytest.raises(Exception) as failure:
        fjm_run.run(fjm_path, io_device=screen, print_time=False)
    message = 'ScreenIO: reserved (0x00) at output byte 25, frame 0: opcode 0x00 is reserved (a stray zero byte?)'
    assert message in repr(failure.value) + repr(failure.value.__cause__)
    assert screen.frame_count == 0


def test_scripted_keyboard_replay_is_deterministic(tmp_path: Path, engine: str) -> None:
    fjm_path = assemble_to_path(KEYBOARD_PROGRAM, tmp_path, use_stl=True)

    for _ in range(2):  # the replay is deterministic - two runs, identical output
        source = ScriptedKeyEventSource.from_text('0, down, 72\n2, up, 75\n')
        keyboard = KeyboardIO(source)
        statistics = fjm_run.run(fjm_path, io_device=keyboard, print_time=False)
        assert statistics.termination_cause == TerminationCause.Looping
        assert keyboard.get_output() == b'DH.UK..!'


def test_pc_device_combines_keyboard_and_screen(tmp_path: Path, engine: str) -> None:
    # the complete PcIO device built from explicit components: screen out + (empty) keyboard in
    fjm_path = assemble_to_path(SCREEN_PROGRAM, tmp_path, use_stl=True)
    screen = InMemoryScreen(frames_dir=tmp_path / 'frames')
    keyboard = KeyboardIO(ScriptedKeyEventSource.from_text(''))
    statistics = fjm_run.run(fjm_path, io_device=PcIO(screen, keyboard), print_time=False)
    assert statistics.termination_cause == TerminationCause.Looping
    assert screen.frame_count == 1


def test_pc_headless_runs_a_program(tmp_path: Path) -> None:
    # the headless 'pc' (#4): scripted keys in + PNG frames out, built programmatically
    fjm_path = assemble_to_path(SCREEN_PROGRAM, tmp_path, use_stl=True)
    events_path = tmp_path / 'events.txt'
    events_path.write_text('0, down, 72\n')
    frames_dir = tmp_path / 'frames'

    statistics = fjm_run.run(fjm_path, io_device=PcIO.headless(events_path, frames_dir), print_time=False)
    assert statistics.termination_cause == TerminationCause.Looping
    assert (frames_dir / 'frame_000000.png').exists()

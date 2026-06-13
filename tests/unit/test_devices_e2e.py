"""
end-to-end tests for the io-devices: an .fj program drives the InMemoryScreen over the output
stream (golden frame-hash + PNG output), a scripted keyboard replays deterministically into
an .fj polling loop, and the complete PcIO device (screen + keyboard together) runs a program.
"""

import hashlib
from pathlib import Path

from flipjump.interpreter import fjm_run
from flipjump.interpreter.io_devices.KeyboardIO import KeyboardIO, ScriptedKeyEventSource
from flipjump.interpreter.io_devices.ScreenIO import InMemoryScreen
from flipjump.interpreter.io_devices.pygame_window import PcIO
from flipjump.utils.classes import TerminationCause
from tests.unit.unit_utils import assemble_to_path

# emits: init_screen(4x2, bpp=8, palette=2); set_palette(palette); update_screen(screen).
# the palette and framebuffer are static packed-byte data ops (the byte at dbit..dbit+7
# of an op is encoded as `;value * dw`).
SCREEN_PROGRAM = """
def output_u16 val {
    rep(2, i) stl.output_char (val >> (8*i)) & 0xFF
}
def output_address addr {
    // one bit at a time: the bit value is an op operand, so label-addresses are fine
    rep(w, i) stl.output_bit (addr >> i) & 1
}

stl.startup

stl.output_char 1            // init_screen
output_u16 4            // width
output_u16 2            // height
stl.output_char 8            // bpp
output_u16 2            // palette_size

stl.output_char 2            // set_palette
output_address palette

stl.output_char 3            // update_screen
output_address screen

stl.loop

palette:                // 2 entries * 3 packed bytes (R, G, B)
    ;10  * dw
    ;20  * dw
    ;30  * dw
    ;200 * dw
    ;100 * dw
    ;0   * dw

screen:                 // 4x2 pixels, one packed byte each
    ;0 * dw
    ;1 * dw
    ;0 * dw
    ;1 * dw
    ;1 * dw
    ;0 * dw
    ;1 * dw
    ;0 * dw
"""

EXPECTED_FRAME_HASH = hashlib.sha256(bytes([0, 1, 0, 1, 1, 0, 1, 0]) + bytes([10, 20, 30, 200, 100, 0])).hexdigest()

# same screen and palette, but the frame arrives with the raw command (0x05): the pixel
# bytes are output in-stream - no framebuffer in program memory, no memory-hook read.
RAW_SCREEN_PROGRAM = """
def output_u16 val {
    rep(2, i) stl.output_char (val >> (8*i)) & 0xFF
}
def output_address addr {
    rep(w, i) stl.output_bit (addr >> i) & 1
}

stl.startup

stl.output_char 1            // init_screen
output_u16 4            // width
output_u16 2            // height
stl.output_char 8            // bpp
output_u16 2            // palette_size

stl.output_char 2            // set_palette
output_address palette

stl.output_char 5            // update_screen_raw: the 4x2 pixel bytes follow in-stream
rep(8, i) stl.output_char (0x01011010 >> (4*i)) & 0xF   // pixels 0,1,0,1,1,0,1,0

stl.loop

palette:                // 2 entries * 3 packed bytes (R, G, B)
    ;10  * dw
    ;20  * dw
    ;30  * dw
    ;200 * dw
    ;100 * dw
    ;0   * dw
"""


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
    assert screen.last_frame_rgb[0] == (10, 20, 30)
    assert screen.last_frame_rgb[1] == (200, 100, 0)


def test_fj_program_drives_the_screen_with_the_raw_command(tmp_path: Path, engine: str) -> None:
    fjm_path = assemble_to_path(RAW_SCREEN_PROGRAM, tmp_path, use_stl=True)
    frames_dir = tmp_path / 'frames'
    screen = InMemoryScreen(frames_dir=frames_dir)

    statistics = fjm_run.run(fjm_path, io_device=screen, print_time=False)

    assert statistics.termination_cause == TerminationCause.Looping
    assert screen.frame_count == 1
    # the raw in-stream frame hashes identically to the memory-hook frame of SCREEN_PROGRAM
    assert screen.frame_hashes[0][1] == EXPECTED_FRAME_HASH
    assert (frames_dir / 'frame_000000.png').exists()


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

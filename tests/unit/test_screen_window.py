"""
unit-tests for the interactive screen window (ScreenWindow.py) - run headless with SDL's
dummy video driver, so they work on Windows/Linux/macOS and in CI.

pinned: the window opens from the init_screen command and presents real frames, live key
events (incl. the special >=0x80 keycodes) flow into a KeyboardIO, F11 is captured for the
fullscreen toggle and never delivered, and closing the window stops the run cleanly.
"""

from pathlib import Path
from typing import Iterator

import pytest

pygame = pytest.importorskip('pygame')

from flipjump.interpreter import fjm_run  # noqa: E402
from flipjump.interpreter.io_devices.KeyboardIO import KeyboardIO  # noqa: E402
from flipjump.interpreter.io_devices.ScreenWindow import (  # noqa: E402
    KEYCODE_UP,
    InteractiveScreen,
)
from flipjump.utils.classes import TerminationCause  # noqa: E402
from flipjump.utils.exceptions import IODeviceException  # noqa: E402
from tests.unit.test_devices_e2e import EXPECTED_FRAME_HASH, RAW_SCREEN_PROGRAM  # noqa: E402
from tests.unit.test_screen_io import write_byte, write_u16  # noqa: E402
from tests.unit.unit_utils import assemble_to_path  # noqa: E402


@pytest.fixture(autouse=True)
def headless_sdl(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setenv('SDL_VIDEODRIVER', 'dummy')
    monkeypatch.setenv('SDL_AUDIODRIVER', 'dummy')
    yield
    pygame.quit()


def init_2x2_screen(device: InteractiveScreen) -> None:
    write_byte(device, 1)  # CMD init_screen
    write_u16(device, 2)
    write_u16(device, 2)
    write_byte(device, 8)  # bpp
    write_u16(device, 0)  # palette_size


def present_raw_2x2(device: InteractiveScreen) -> None:
    write_byte(device, 5)  # CMD update_screen_raw
    for pixel in (0, 0, 0, 0):
        write_byte(device, pixel)


def post_key(key: int, *, is_down: bool = True) -> None:
    event_type = pygame.KEYDOWN if is_down else pygame.KEYUP
    pygame.event.post(pygame.event.Event(event_type, key=key))


def read_status_hex(keyboard: KeyboardIO) -> int:
    return sum(int(keyboard.read_bit()) << i for i in range(4))


def read_byte(keyboard: KeyboardIO) -> int:
    return sum(int(keyboard.read_bit()) << i for i in range(8))


def test_init_screen_opens_the_window() -> None:
    device = InteractiveScreen()
    init_2x2_screen(device)
    surface = pygame.display.get_surface()
    assert surface is not None
    assert surface.get_size() == (2, 2)


def test_present_draws_the_frame_pixels() -> None:
    device = InteractiveScreen()
    init_2x2_screen(device)
    device.palette = [(9, 8, 7)]  # a palette entry, so the drawn pixel is not the default black
    present_raw_2x2(device)
    assert device.frame_count == 1
    surface = pygame.display.get_surface()
    assert surface.get_at((0, 0))[:3] == (9, 8, 7)


def test_live_key_events_reach_a_keyboard_device() -> None:
    device = InteractiveScreen()
    init_2x2_screen(device)
    keyboard = KeyboardIO(device.key_event_source)

    post_key(pygame.K_a)
    assert read_status_hex(keyboard) == 0x9  # key down
    assert read_byte(keyboard) == ord('a')

    post_key(pygame.K_a, is_down=False)
    assert read_status_hex(keyboard) == 0x8  # key up
    assert read_byte(keyboard) == ord('a')

    assert read_status_hex(keyboard) == 0x0  # idle


def test_special_keys_use_the_byte_keycodes() -> None:
    device = InteractiveScreen()
    init_2x2_screen(device)
    keyboard = KeyboardIO(device.key_event_source)
    post_key(pygame.K_UP)
    assert read_status_hex(keyboard) == 0x9
    assert read_byte(keyboard) == KEYCODE_UP


def test_f11_toggles_fullscreen_and_is_not_delivered(monkeypatch: pytest.MonkeyPatch) -> None:
    device = InteractiveScreen()
    init_2x2_screen(device)
    keyboard = KeyboardIO(device.key_event_source)
    toggle_calls = []
    monkeypatch.setattr(pygame.display, 'toggle_fullscreen', lambda: toggle_calls.append(True))
    post_key(pygame.K_F11)
    post_key(pygame.K_b)
    assert read_status_hex(keyboard) == 0x9
    assert read_byte(keyboard) == ord('b')  # 'b' arrives; F11 was consumed by the toggle
    assert toggle_calls == [True]


def test_unmapped_keys_are_ignored() -> None:
    device = InteractiveScreen()
    init_2x2_screen(device)
    keyboard = KeyboardIO(device.key_event_source)
    post_key(pygame.K_F5)  # no byte keycode - ignored
    assert read_status_hex(keyboard) == 0x0


def test_closing_the_window_raises_keyboard_interrupt() -> None:
    device = InteractiveScreen()
    init_2x2_screen(device)
    pygame.event.post(pygame.event.Event(pygame.QUIT))
    with pytest.raises(KeyboardInterrupt):
        device.window.pump_events()
    assert device.window.closed


def test_fj_program_presents_into_the_window(tmp_path: Path) -> None:
    # the raw-command E2E program, now presented into a (dummy-driver) window
    fjm_path = assemble_to_path(RAW_SCREEN_PROGRAM, tmp_path, use_stl=True)
    device = InteractiveScreen()
    statistics = fjm_run.run(fjm_path, io_device=device, print_time=False)
    assert statistics.termination_cause == TerminationCause.Looping
    assert device.frame_count == 1
    assert device.frame_hashes[0][1] == EXPECTED_FRAME_HASH
    surface = pygame.display.get_surface()
    assert surface.get_at((0, 0))[:3] == (10, 20, 30)  # palette entry 0
    assert surface.get_at((1, 0))[:3] == (200, 100, 0)  # palette entry 1


def test_cli_live_keyboard_requires_the_interactive_screen() -> None:
    from flipjump.interpreter.io_devices.cli_devices import create_io_device

    with pytest.raises(IODeviceException):
        create_io_device('keyboard', 'standard')


def test_cli_screen_with_live_keyboard_wiring() -> None:
    from flipjump.interpreter.io_devices.cli_devices import SplitIO, create_io_device

    io_device = create_io_device('keyboard', 'screen')
    assert isinstance(io_device, SplitIO)
    assert isinstance(io_device.output_device, InteractiveScreen)
    assert isinstance(io_device.input_device, KeyboardIO)
    assert io_device.input_device.event_source is io_device.output_device.key_event_source


def test_closing_the_window_terminates_a_real_run(tmp_path: Path, engine: str) -> None:
    # QUIT is already pending when the program presents its first frame: the pump raises
    # KeyboardInterrupt inside the run, and the interpreter must turn it into a clean
    # keyboard-interrupt termination (on both engines).
    fjm_path = assemble_to_path(RAW_SCREEN_PROGRAM, tmp_path, use_stl=True)
    device = InteractiveScreen()
    device.window.ensure_open(4, 2)  # open early so the QUIT event can be posted
    pygame.event.post(pygame.event.Event(pygame.QUIT))

    statistics = fjm_run.run(fjm_path, io_device=device, print_time=False)
    assert statistics.termination_cause == TerminationCause.KeyboardInterrupt
    assert device.window.closed
    # storage_mode is set only by the native engine - prove the right engine actually ran
    assert (statistics.storage_mode is not None) == (engine == 'native')

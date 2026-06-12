"""
unit-tests for the interactive pygame window (pygame_window.py) - run headless with SDL's
dummy video driver, so they work on Windows/Linux/macOS and in CI.

pinned: the screen opens/draws the shared window; live key events (incl. the special
>=0x80 keycodes) flow from the window into a KeyboardIO that does NOT depend on the screen;
F11 toggles fullscreen and is never delivered; closing the window stops the run; and the CLI
wires the two interactive devices onto one shared window (a lone live keyboard opens its own).
"""

from pathlib import Path
from typing import Iterator

import pytest

pygame = pytest.importorskip('pygame')

from flipjump.interpreter import fjm_run  # noqa: E402
from flipjump.interpreter.io_devices.KeyboardIO import KeyboardIO  # noqa: E402
from flipjump.interpreter.io_devices.pygame_window import (  # noqa: E402
    KEYCODE_UP,
    InteractiveScreen,
    PygameWindow,
    WindowKeyEventSource,
)
from flipjump.utils.classes import TerminationCause  # noqa: E402
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


def keyboard_on(window: PygameWindow) -> KeyboardIO:
    """a KeyboardIO reading live keys from the window - built without referencing any screen."""
    return KeyboardIO(WindowKeyEventSource(window))


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
    window = PygameWindow()
    window.ensure_open_for_input()
    keyboard = keyboard_on(window)

    post_key(pygame.K_a)
    assert read_status_hex(keyboard) == 0x9  # key down
    assert read_byte(keyboard) == ord('a')

    post_key(pygame.K_a, is_down=False)
    assert read_status_hex(keyboard) == 0x8  # key up
    assert read_byte(keyboard) == ord('a')

    assert read_status_hex(keyboard) == 0x0  # idle


def test_special_keys_use_the_byte_keycodes() -> None:
    window = PygameWindow()
    window.ensure_open_for_input()
    keyboard = keyboard_on(window)
    post_key(pygame.K_UP)
    assert read_status_hex(keyboard) == 0x9
    assert read_byte(keyboard) == KEYCODE_UP


def test_f11_toggles_fullscreen_and_is_not_delivered(monkeypatch: pytest.MonkeyPatch) -> None:
    window = PygameWindow()
    window.ensure_open_for_input()
    keyboard = keyboard_on(window)
    toggle_calls = []
    monkeypatch.setattr(pygame.display, 'toggle_fullscreen', lambda: toggle_calls.append(True))
    post_key(pygame.K_F11)
    post_key(pygame.K_b)
    assert read_status_hex(keyboard) == 0x9
    assert read_byte(keyboard) == ord('b')  # 'b' arrives; F11 was consumed by the toggle
    assert toggle_calls == [True]


def test_unmapped_keys_are_ignored() -> None:
    window = PygameWindow()
    window.ensure_open_for_input()
    keyboard = keyboard_on(window)
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


def test_cli_live_keyboard_alone_opens_its_own_window() -> None:
    # a live keyboard with no --do screen no longer errors: it opens its own small input window
    from flipjump.interpreter.io_devices.cli_devices import SplitIO, create_io_device

    io_device = create_io_device('keyboard', 'standard')
    assert isinstance(io_device, SplitIO)
    assert isinstance(io_device.input_device, KeyboardIO)
    window = io_device.input_device.event_source._window  # type: ignore[attr-defined]
    assert isinstance(window, PygameWindow)
    assert window.is_open  # opened for input, since there's no screen to size it


def test_cli_screen_and_keyboard_share_one_window() -> None:
    # the two interactive devices are wired onto the SAME window, with no device->device link
    from flipjump.interpreter.io_devices.cli_devices import SplitIO, create_io_device

    io_device = create_io_device('keyboard', 'screen')
    assert isinstance(io_device, SplitIO)
    assert isinstance(io_device.output_device, InteractiveScreen)
    assert isinstance(io_device.input_device, KeyboardIO)
    keyboard_window = io_device.input_device.event_source._window  # type: ignore[attr-defined]
    assert keyboard_window is io_device.output_device.window
    # the screen opens/sizes the window on its init-screen command, so the composition root
    # must NOT have pre-opened it for input here
    assert not keyboard_window.is_open


def test_cli_screen_alone_does_not_preopen_the_window() -> None:
    # screen-alone: the window is created but opened lazily by the screen, not for input
    from flipjump.interpreter.io_devices.cli_devices import create_io_device

    io_device = create_io_device('standard', 'screen')
    screen = io_device.output_device  # type: ignore[attr-defined]
    assert isinstance(screen, InteractiveScreen)
    assert not screen.window.is_open  # opens only on the program's init-screen command


def test_cli_live_keyboard_with_console_output() -> None:
    # the user's example: windowed live-key capture (its own input window) + plain console
    # text output. the keyboard gets a window; the output device is a non-windowed StandardIO.
    from flipjump.interpreter.io_devices.StandardIO import StandardIO
    from flipjump.interpreter.io_devices.cli_devices import SplitIO, create_io_device

    io_device = create_io_device('keyboard', 'console')
    assert isinstance(io_device, SplitIO)
    assert isinstance(io_device.input_device, KeyboardIO)
    assert isinstance(io_device.output_device, StandardIO)  # console = terminal text output
    window = io_device.input_device.event_source._window  # type: ignore[attr-defined]
    assert isinstance(window, PygameWindow)
    assert window.is_open  # the keyboard opened its own input window (no screen to size it)


def test_closing_the_window_terminates_a_real_run(tmp_path: Path, engine: str) -> None:
    # QUIT is already pending when the program presents its first frame: the pump raises
    # KeyboardInterrupt inside the run, and the interpreter must turn it into a clean
    # keyboard-interrupt termination (on every engine).
    fjm_path = assemble_to_path(RAW_SCREEN_PROGRAM, tmp_path, use_stl=True)
    device = InteractiveScreen()
    device.window.ensure_open(4, 2)  # open early so the QUIT event can be posted
    pygame.event.post(pygame.event.Event(pygame.QUIT))

    statistics = fjm_run.run(fjm_path, io_device=device, print_time=False)
    assert statistics.termination_cause == TerminationCause.KeyboardInterrupt
    assert device.window.closed
    # storage_mode is set only by the native engine - prove the right engine actually ran
    assert (statistics.storage_mode is not None) == (engine == 'native')

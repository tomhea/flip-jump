"""
the interactive screen backend: a real window (pygame/SDL) behind the same command
stream as the headless InMemoryScreen, plus a live keyboard source.

InteractiveScreen presents every frame into a window (scaled up from the logical
screen size; F11 toggles fullscreen), and exposes key_event_source - a KeyEventSource
fed by the window's real key events - so a KeyboardIO over it receives whatever is
pressed while the window is focused. Closing the window raises KeyboardInterrupt,
which the interpreter turns into a clean keyboard-interrupt termination.

keycodes delivered to the fj program (one byte): printable/control keys send their
ascii-like SDL keycode (k < 0x80, e.g. 'a'=97, esc=27, enter=13, space=32); the
arrows/shift/ctrl/alt send 0x80-0x86 (up,down,left,right,shift,ctrl,alt). other keys
are ignored. F11 is captured for the fullscreen toggle and is never delivered.

pygame is an optional dependency: `pip install flipjump[screen]`. the window must be
driven from the main thread (a macOS/SDL requirement) - the interpreter already runs
there. works on Windows, Linux and macOS; tests run headless with SDL's dummy driver.
"""

from collections import deque
from pathlib import Path
from typing import Any, Deque, List, Optional, Tuple

from flipjump.interpreter.io_devices.KeyboardIO import KeyEventSource
from flipjump.interpreter.io_devices.ScreenIO import InMemoryScreen
from flipjump.utils.exceptions import IODeviceException

# the >=0x80 keycodes (the SDL keycodes of these keys don't fit a byte)
KEYCODE_UP = 0x80
KEYCODE_DOWN = 0x81
KEYCODE_LEFT = 0x82
KEYCODE_RIGHT = 0x83
KEYCODE_SHIFT = 0x84
KEYCODE_CTRL = 0x85
KEYCODE_ALT = 0x86


def _import_pygame() -> Any:
    try:
        import pygame
    except ImportError as import_error:
        raise IODeviceException(
            'the interactive screen needs pygame - install it with `pip install flipjump[screen]`'
        ) from import_error
    return pygame


class ScreenWindow:
    """owns the window and the live key-event queue. opened on the first ensure_open."""

    def __init__(self, *, title: str = 'FlipJump'):
        self._pygame = _import_pygame()
        self._title = title
        self._screen_surface = None
        self.key_events: Deque[Tuple[bool, int]] = deque()  # (is_down, keycode)
        self.closed = False

        pg = self._pygame
        self._special_keycodes = {
            pg.K_UP: KEYCODE_UP,
            pg.K_DOWN: KEYCODE_DOWN,
            pg.K_LEFT: KEYCODE_LEFT,
            pg.K_RIGHT: KEYCODE_RIGHT,
            pg.K_LSHIFT: KEYCODE_SHIFT,
            pg.K_RSHIFT: KEYCODE_SHIFT,
            pg.K_LCTRL: KEYCODE_CTRL,
            pg.K_RCTRL: KEYCODE_CTRL,
            pg.K_LALT: KEYCODE_ALT,
            pg.K_RALT: KEYCODE_ALT,
        }

    def ensure_open(self, width: int, height: int) -> None:
        """open (or resize) the window for a width x height logical screen."""
        if self._screen_surface is not None and self._screen_surface.get_size() == (width, height):
            return  # already open at this size - recreating the window would flicker
        pg = self._pygame
        pg.display.init()
        pg.display.set_caption(self._title)
        # SCALED scales the small logical surface up to a window-sized one (and handles
        # fullscreen scaling); RESIZABLE lets the user drag-resize.
        self._screen_surface = pg.display.set_mode((width, height), pg.SCALED | pg.RESIZABLE)

    def _byte_keycode(self, sdl_key: int) -> Optional[int]:
        if 0 < sdl_key < 0x80:
            return sdl_key
        return self._special_keycodes.get(sdl_key)

    def pump_events(self) -> None:
        """process pending window events: queue key transitions, F11 = fullscreen toggle,
        closing the window raises KeyboardInterrupt (a clean run termination)."""
        if self.closed or self._screen_surface is None:
            return
        pg = self._pygame
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.closed = True
                raise KeyboardInterrupt
            if event.type in (pg.KEYDOWN, pg.KEYUP):
                if event.key == pg.K_F11:
                    if event.type == pg.KEYDOWN:
                        try:
                            pg.display.toggle_fullscreen()
                        except pg.error:
                            pass  # some video drivers (e.g. the headless dummy) can't toggle
                    continue
                keycode = self._byte_keycode(event.key)
                if keycode is not None:
                    self.key_events.append((event.type == pg.KEYDOWN, keycode))

    def draw(self, width: int, height: int, rgb_pixels: List[Tuple[int, int, int]]) -> None:
        """blit a full frame (row-major RGB tuples) and present it."""
        if self._screen_surface is None:
            return
        pg = self._pygame
        rgb_bytes = bytes(channel for pixel in rgb_pixels for channel in pixel)
        frame_surface = pg.image.frombuffer(rgb_bytes, (width, height), 'RGB')
        self._screen_surface.blit(frame_surface, (0, 0))
        pg.display.flip()

    def close(self) -> None:
        if not self.closed:
            self.closed = True
            self._pygame.display.quit()


class WindowKeyEventSource(KeyEventSource):
    """the live key events of a ScreenWindow (pumps the window before every poll)."""

    def __init__(self, window: ScreenWindow):
        self._window = window

    def next_due_event(self, tic: int) -> Optional[Tuple[bool, int]]:
        self._window.pump_events()
        return self._window.key_events.popleft() if self._window.key_events else None


class InteractiveScreen(InMemoryScreen):
    """the InMemoryScreen command stream, presented into a real window.

    key_event_source delivers the window's live key events - wire a KeyboardIO over it
    (the --di keyboard CLI spec does exactly that when --do screen is windowed)."""

    def __init__(self, *, frames_dir: Optional[Path] = None, window_title: str = 'FlipJump'):
        super().__init__(frames_dir=frames_dir)
        self.window = ScreenWindow(title=window_title)
        self.key_event_source = WindowKeyEventSource(self.window)

    def _init_screen(self, width: int, height: int, bpp: int, palette_size: int) -> None:
        super()._init_screen(width, height, bpp, palette_size)
        self.window.ensure_open(width, height)

    def _present(self) -> None:
        super()._present()
        self.window.draw(self.width, self.height, self.last_frame_rgb)
        self.window.pump_events()

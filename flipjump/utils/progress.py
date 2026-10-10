"""
the live progress bar of a long stage (assembling, loading a program).

`ProgressBar` is a drop-in for `PrintTimer`: it prints the same `  stage:  1.234s` line when the
stage ends, so a log, a pipe or a test sees exactly what it always saw. Only on an interactive
terminal does the line come alive while the stage runs:

      loading memory:  ███████████████▋░░░░░░░░░░░░░░  52%  0:01 · 0:01 left  decompressing

The bar is drawn on one line (carriage return, no scrolling) and redrawn at most ~12 times a
second, so a caller may report progress from a hot loop as long as it does so every few thousand
items (`active` tells it whether to bother at all). `FLIPJUMP_PROGRESS=0` turns the bars off;
`NO_COLOR` keeps them but drops the color.
"""

from __future__ import annotations

import os
import shutil
import sys
from time import monotonic, time
from typing import Any, Optional, TextIO

_REDRAW_SECONDS = 0.08
_BAR_WIDTH = 30
_PARTIALS = ' ▏▎▍▌▋▊▉'  # eighths of a cell, for a smooth leading edge
_FULL, _EMPTY = '█', '░'
_ASCII_FULL, _ASCII_EMPTY = '#', '-'
_SPINNER = '⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
_ASCII_SPINNER = '|/-\\'

_COLOR_BAR = '\x1b[36m'  # cyan
_COLOR_DIM = '\x1b[2m'
_COLOR_RESET = '\x1b[0m'


def _enable_windows_vt(stream: TextIO) -> bool:
    """turn on ANSI escape processing in a Windows console (off by default in the classic one).
    @return: whether escapes will render"""
    if os.name != 'nt':
        return True
    try:
        import ctypes
        import msvcrt

        # getattr: these exist only on Windows, which a type-checker on another platform does not know
        kernel32 = getattr(ctypes, 'windll').kernel32
        handle = getattr(msvcrt, 'get_osfhandle')(stream.fileno())
        mode = ctypes.c_uint32()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        enable_virtual_terminal_processing = 0x0004
        if mode.value & enable_virtual_terminal_processing:
            return True
        return bool(kernel32.SetConsoleMode(handle, mode.value | enable_virtual_terminal_processing))
    except Exception:  # noqa: BLE001 - any failure just means no color
        return False


def _can_encode(stream: TextIO, text: str) -> bool:
    try:
        text.encode(stream.encoding or 'ascii')
        return True
    except (UnicodeEncodeError, LookupError):
        return False


def _format_seconds(seconds: float) -> str:
    seconds = int(seconds)
    if seconds >= 3600:
        return f'{seconds // 3600}:{seconds // 60 % 60:02d}:{seconds % 60:02d}'
    return f'{seconds // 60}:{seconds % 60:02d}'


def progress_enabled(stream: Optional[TextIO] = None) -> bool:
    """would a progress bar be drawn on this stream? (an interactive terminal, not turned off)"""
    stream = stream if stream is not None else sys.stdout
    if os.environ.get('FLIPJUMP_PROGRESS', '1') == '0' or os.environ.get('TERM') == 'dumb':
        return False
    try:
        return stream.isatty()
    except (AttributeError, ValueError):
        return False


class ProgressBar:
    """
    the progress line of one stage. usage:

        with ProgressBar('  loading memory:  ', print_time=True, total=n) as bar:
            for i in ...:
                ...
                if bar.active and i % 4096 == 0:
                    bar.update(i, stage='decompressing')

    `update(done)` takes ABSOLUTE progress in units of `total` (set it later with `set_total` if it
    is only known once the stage has started). Without a total the bar is a spinner. When the stage
    ends, the line is replaced by the stage's time, exactly as PrintTimer prints it.
    """

    def __init__(
        self,
        init_message: str,
        *,
        print_time: bool = True,
        total: Optional[float] = None,
        stream: Optional[TextIO] = None,
    ) -> None:
        self.init_message = init_message
        self.print_time = print_time
        self.total = total
        self.stream = stream if stream is not None else sys.stdout
        self.active = print_time and progress_enabled(self.stream)
        self.done = 0.0
        self.stage = ''
        self._start_wall = 0.0
        self._start = 0.0
        self._last_draw = 0.0
        self._drawn_width = 0
        self._spin = 0
        self._unicode = self.active and _can_encode(self.stream, _FULL + _EMPTY + _PARTIALS + _SPINNER + '·')
        self._color = self.active and 'NO_COLOR' not in os.environ and _enable_windows_vt(self.stream)

    def __enter__(self) -> 'ProgressBar':
        self._start_wall = time()
        self._start = monotonic()
        if self.print_time:
            if self.active:
                self._draw(force=True)
            else:
                print(self.init_message, end='', flush=True, file=self.stream)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if not self.print_time:
            return
        elapsed = f'{time() - self._start_wall:.3f}s'
        if self.active:
            line = self.init_message + elapsed
            padding = ' ' * max(0, self._drawn_width - len(line))
            print('\r' + line + padding, file=self.stream, flush=True)
        else:
            print(elapsed, file=self.stream, flush=True)

    def set_total(self, total: Optional[float]) -> None:
        self.total = total
        self._draw()

    def update(self, done: float, *, stage: Optional[str] = None) -> None:
        """report the absolute progress (in units of `total`), and optionally the current sub-stage"""
        self.done = done
        if stage is not None and stage != self.stage:
            self.stage = stage
            self._draw(force=True)
            return
        self._draw()

    def _bar(self, fraction: float) -> str:
        if self._unicode:
            eighths = int(fraction * _BAR_WIDTH * 8)
            full, partial = divmod(eighths, 8)
            filled = _FULL * full + (_PARTIALS[partial] if full < _BAR_WIDTH and partial else '')
            empty = _EMPTY * (_BAR_WIDTH - len(filled))
        else:
            full = int(fraction * _BAR_WIDTH)
            filled, empty = _ASCII_FULL * full, _ASCII_EMPTY * (_BAR_WIDTH - full)
        if self._color:
            return f'{_COLOR_BAR}{filled}{_COLOR_DIM}{empty}{_COLOR_RESET}'
        return filled + empty

    def _draw(self, *, force: bool = False) -> None:
        if not self.active or not self.print_time:
            return
        now = monotonic()
        if not force and now - self._last_draw < _REDRAW_SECONDS:
            return
        self._last_draw = now
        elapsed = now - self._start
        dot = '·' if self._unicode else '-'
        if self.total:
            fraction = min(1.0, max(0.0, self.done / self.total))
            timing = _format_seconds(elapsed)
            if fraction >= 0.02 and elapsed >= 1:
                timing += f' {dot} {_format_seconds(elapsed * (1 - fraction) / fraction)} left'
            body = f'{self._bar(fraction)} {int(fraction * 100):3d}%  {timing}'
            visible = _BAR_WIDTH + 6 + len(timing)
        else:
            spinner = _SPINNER if self._unicode else _ASCII_SPINNER
            self._spin = (self._spin + 1) % len(spinner)
            body = f'{spinner[self._spin]} {_format_seconds(elapsed)}'
            visible = len(body)
        line_width = shutil.get_terminal_size((100, 24)).columns - 1
        stage = f'  {self.stage}' if self.stage else ''
        room = line_width - len(self.init_message) - visible
        stage = stage[: max(0, room)]
        width = len(self.init_message) + visible + len(stage)
        if self._color and stage:
            stage = f'{_COLOR_DIM}{stage}{_COLOR_RESET}'
        padding = ' ' * max(0, self._drawn_width - width)
        self._drawn_width = width
        self.stream.write('\r' + self.init_message + body + stage + padding)
        self.stream.flush()

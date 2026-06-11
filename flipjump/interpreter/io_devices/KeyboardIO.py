"""
the keyboard input-device (WI-B).
non-blocking, virtual-time, scriptable: the FJ program polls one status HEX per tic
(read with `hex.input_hex`, 4 input bits lsb-first) and keeps its own frame-counter clock -
there is no timer device, and idle polling never EOFs.

the status hex: 0x0 = no event; 0x8 = a key was released; 0x9 = a key was pressed
(bit 3 = event-present, bit 0 = is_down). on an event, the keycode byte follows - either
through the input stream right after the status hex (stream mode - read it with
`hex.input`), or written into a fixed memory mailbox (one packed-byte op at
mailbox_bit_address) via the device<->memory hook before the status hex is returned
(mailbox mode).

the event source is pluggable: ScriptedKeyEventSource replays a `tic, down/up, keycode`
event file (deterministic E2E tests and CI - the DOOM-demo-playback equivalent), and
QueueKeyEventSource accepts live host events.
"""

from collections import deque
from pathlib import Path
from typing import Deque, List, NamedTuple, Optional, Tuple

from flipjump.interpreter.io_devices.IODevice import IODevice
from flipjump.interpreter.io_devices.device_memory import DeviceMemory
from flipjump.utils.exceptions import IODeviceException


class KeyEvent(NamedTuple):
    tic: int
    is_down: bool
    keycode: int


class KeyEventSource:
    """the pluggable source of key events. next_due_event is polled once per tic."""

    def next_due_event(self, tic: int) -> Optional[Tuple[bool, int]]:
        """return the next due (is_down, keycode) at the given tic, or None."""
        raise NotImplementedError


class ScriptedKeyEventSource(KeyEventSource):
    """replays a fixed event list - events become due once the tic-clock reaches their tic."""

    def __init__(self, events: List[KeyEvent]):
        self.events = sorted(events, key=lambda event: event.tic)
        self._next_index = 0

    @classmethod
    def from_text(cls, text: str) -> 'ScriptedKeyEventSource':
        """parse `tic, down/up, keycode` lines ('#'-comments and empty lines are skipped)."""
        events = []
        for line_number, line in enumerate(text.splitlines(), start=1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = [part.strip() for part in line.split(',')]
            if len(parts) != 3:
                raise IODeviceException(f'bad scripted-keyboard line {line_number}: {line!r}')
            tic, down_up, keycode = parts
            if down_up.lower() in ('down', '1'):
                is_down = True
            elif down_up.lower() in ('up', '0'):
                is_down = False
            else:
                raise IODeviceException(f'bad down/up value on scripted-keyboard line {line_number}: {down_up!r}')
            events.append(KeyEvent(int(tic, 0), is_down, int(keycode, 0)))
        return cls(events)

    @classmethod
    def from_file(cls, events_file: Path) -> 'ScriptedKeyEventSource':
        return cls.from_text(events_file.read_text())

    def next_due_event(self, tic: int) -> Optional[Tuple[bool, int]]:
        if self._next_index < len(self.events) and self.events[self._next_index].tic <= tic:
            event = self.events[self._next_index]
            self._next_index += 1
            return event.is_down, event.keycode
        return None


class QueueKeyEventSource(KeyEventSource):
    """live host events: push (is_down, keycode) anytime; every pushed event is due immediately."""

    def __init__(self) -> None:
        self._queue: Deque[Tuple[bool, int]] = deque()

    def push(self, is_down: bool, keycode: int) -> None:
        self._queue.append((is_down, keycode))

    def next_due_event(self, tic: int) -> Optional[Tuple[bool, int]]:
        return self._queue.popleft() if self._queue else None


class KeyboardIO(IODevice):
    """
    the keyboard input-device. see the module docstring for the polling protocol.
    output written to this device is buffered (get_output), so it can also be used standalone.
    """

    NO_KEY_STATUS = 0x0
    KEY_UP_STATUS = 0x8
    KEY_DOWN_STATUS = 0x9

    def __init__(self, event_source: KeyEventSource, *, mailbox_bit_address: Optional[int] = None):
        self.event_source = event_source
        self.mailbox_bit_address = mailbox_bit_address
        self.device_memory: Optional[DeviceMemory] = None

        self.tic = 0
        self._pending_input_bits: Deque[bool] = deque()

        self._output = b''
        self._current_output_byte = 0
        self._output_bits_count = 0

    def attach_memory(self, device_memory: DeviceMemory) -> None:
        self.device_memory = device_memory

    def _queue_input_byte(self, value: int) -> None:
        for i in range(8):
            self._pending_input_bits.append((value >> i) & 1 == 1)

    def _queue_input_hex(self, value: int) -> None:
        for i in range(4):
            self._pending_input_bits.append((value >> i) & 1 == 1)

    def _poll(self) -> None:
        """one tic: queue the status hex (and deliver the keycode, by mode)."""
        event = self.event_source.next_due_event(self.tic)
        self.tic += 1
        if event is None:
            self._queue_input_hex(self.NO_KEY_STATUS)
            return

        is_down, keycode = event
        status = self.KEY_DOWN_STATUS if is_down else self.KEY_UP_STATUS
        if self.mailbox_bit_address is not None:
            if self.device_memory is None:
                raise IODeviceException('mailbox-mode keyboard is not attached to the interpreter memory')
            self.device_memory.write_data_byte(self.mailbox_bit_address, keycode)
            self._queue_input_hex(status)
        else:
            self._queue_input_hex(status)
            self._queue_input_byte(keycode)

    def read_bit(self) -> bool:
        if not self._pending_input_bits:
            self._poll()
        return self._pending_input_bits.popleft()

    def write_bit(self, bit: bool) -> None:
        self._current_output_byte |= bit << self._output_bits_count
        self._output_bits_count += 1
        if self._output_bits_count == 8:
            self._output += self._current_output_byte.to_bytes(1, 'little')
            self._current_output_byte = 0
            self._output_bits_count = 0

    def get_output(self, *, allow_incomplete_output: bool = False) -> bytes:
        return self._output

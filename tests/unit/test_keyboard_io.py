"""
unit-tests for the keyboard input-device (WI-B).

the keyboard is non-blocking and runs on virtual time: the FJ program polls one status BIT
per tic - 0 = no event, 1 = an event is due. the event payload (one is_down bit + one
keycode byte) is delivered either through the input stream (stream mode) or written into a
fixed memory mailbox via the device<->memory hook (mailbox mode). the event source is
pluggable: a scripted event file makes replays deterministic; idle polling never EOFs.
"""

from typing import Dict

from flipjump.interpreter.io_devices.KeyboardIO import (
    KeyEvent,
    KeyboardIO,
    ScriptedKeyEventSource,
)
from flipjump.interpreter.io_devices.device_memory import DeviceMemory


class FakeDeviceMemory(DeviceMemory):
    def __init__(self, memory_width: int = 64):
        self.memory_width = memory_width
        self.words: Dict[int, int] = {}

    def read_word(self, word_address: int) -> int:
        return self.words.get(word_address, 0)

    def write_word(self, word_address: int, value: int) -> None:
        self.words[word_address] = value & ((1 << self.memory_width) - 1)


def read_byte(device: KeyboardIO) -> int:
    value = 0
    for i in range(8):
        value |= int(device.read_bit()) << i
    return value


def read_event(device: KeyboardIO) -> 'tuple[bool, int]':
    """read [is_down bit][keycode byte] from the stream (after a 1 status bit)."""
    is_down = device.read_bit()
    return is_down, read_byte(device)


class TestScriptedKeyEventSource:
    def test_parses_event_file_lines(self) -> None:
        source = ScriptedKeyEventSource.from_text('0, down, 72\n2, up, 72\n# comment\n\n5, down, 0x20\n')
        assert source.events == [KeyEvent(0, True, 72), KeyEvent(2, False, 72), KeyEvent(5, True, 0x20)]

    def test_accepts_numeric_down_up(self) -> None:
        source = ScriptedKeyEventSource.from_text('3, 1, 10\n4, 0, 11\n')
        assert source.events == [KeyEvent(3, True, 10), KeyEvent(4, False, 11)]


class TestKeyboardStreamMode:
    def test_replay_is_deterministic_and_never_eofs(self) -> None:
        source = ScriptedKeyEventSource.from_text('0, down, 72\n2, up, 72\n')
        device = KeyboardIO(source)

        # tic 0: event due -> status bit 1, then [is_down=1][72]
        assert device.read_bit() is True
        assert read_event(device) == (True, 72)
        # tic 1: nothing -> a single 0 bit
        assert device.read_bit() is False
        # tic 2: the up event
        assert device.read_bit() is True
        assert read_event(device) == (False, 72)
        # idle forever - one 0 bit per tic, never raises IOReadOnEOF
        for _ in range(50):
            assert device.read_bit() is False

    def test_late_events_are_delivered_in_order(self) -> None:
        # two events on the same tic: the second is delivered on the next poll
        source = ScriptedKeyEventSource.from_text('0, down, 1\n0, down, 2\n')
        device = KeyboardIO(source)
        assert device.read_bit() is True
        assert read_event(device) == (True, 1)
        assert device.read_bit() is True
        assert read_event(device) == (True, 2)
        assert device.read_bit() is False


class TestKeyboardMailboxMode:
    def test_payload_is_written_to_the_mailbox(self) -> None:
        memory = FakeDeviceMemory(memory_width=64)
        mailbox_bit_address = 0x4000  # dw-aligned
        source = ScriptedKeyEventSource.from_text('0, down, 72\n')
        device = KeyboardIO(source, mailbox_bit_address=mailbox_bit_address)
        device.attach_memory(memory)

        # only the status bit passes through the stream
        assert device.read_bit() is True
        assert memory.read_data_byte(mailbox_bit_address) == 0x01  # is_down
        assert memory.read_data_byte(mailbox_bit_address + 128) == 72  # keycode (dw = 128)

        # next poll: no event; the mailbox is not rewritten
        assert device.read_bit() is False
        assert memory.read_data_byte(mailbox_bit_address + 128) == 72

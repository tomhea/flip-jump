"""
unit-tests for the keyboard input-device (WI-B).

the keyboard is non-blocking and runs on virtual time: the FJ program polls one status HEX
per tic - 0x0 = no event, 0x8 = key released, 0x9 = key pressed. on an event the keycode
byte follows, through the input stream (stream mode) or written into a fixed memory mailbox
via the device<->memory hook (mailbox mode). the event source is pluggable: a scripted
event file makes replays deterministic; idle polling never EOFs.
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


def read_status_hex(device: KeyboardIO) -> int:
    """read the 4-bit (lsb-first) status hex - what hex.input_hex sees."""
    value = 0
    for i in range(4):
        value |= int(device.read_bit()) << i
    return value


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

        # tic 0: key-down event -> status 0x9, then the keycode byte
        assert read_status_hex(device) == 0x9
        assert read_byte(device) == 72
        # tic 1: nothing -> status 0x0
        assert read_status_hex(device) == 0x0
        # tic 2: the key-up event -> status 0x8
        assert read_status_hex(device) == 0x8
        assert read_byte(device) == 72
        # idle forever - one 0x0 status hex per tic, never raises IOReadOnEOF
        for _ in range(50):
            assert read_status_hex(device) == 0x0

    def test_late_events_are_delivered_in_order(self) -> None:
        # two events on the same tic: the second is delivered on the next poll
        source = ScriptedKeyEventSource.from_text('0, down, 1\n0, down, 2\n')
        device = KeyboardIO(source)
        assert (read_status_hex(device), read_byte(device)) == (0x9, 1)
        assert (read_status_hex(device), read_byte(device)) == (0x9, 2)
        assert read_status_hex(device) == 0x0


class TestKeyboardMailboxMode:
    def test_payload_is_written_to_the_mailbox(self) -> None:
        memory = FakeDeviceMemory(memory_width=64)
        mailbox_bit_address = 0x4000  # dw-aligned
        source = ScriptedKeyEventSource.from_text('0, down, 72\n')
        device = KeyboardIO(source, mailbox_bit_address=mailbox_bit_address)
        device.attach_memory(memory)

        # only the status hex passes through the stream (is_down is inside it)
        assert read_status_hex(device) == 0x9
        assert memory.read_data_byte(mailbox_bit_address) == 72  # the keycode

        # next poll: no event; the mailbox is not rewritten
        assert read_status_hex(device) == 0x0
        assert memory.read_data_byte(mailbox_bit_address) == 72

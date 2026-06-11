"""
unit-tests for the keyboard input-device.

the keyboard is non-blocking and runs on virtual time: the FJ program polls one status HEX
per tic - 0x0 = no event, 0x8 = key released, 0x9 = key pressed. on an event the keycode
byte follows through the input stream. the event source is pluggable: a scripted event
file makes replays deterministic; idle polling never EOFs.
"""

from flipjump.interpreter.io_devices.KeyboardIO import (
    KeyEvent,
    KeyboardIO,
    ScriptedKeyEventSource,
)


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


class TestKeyboard:
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

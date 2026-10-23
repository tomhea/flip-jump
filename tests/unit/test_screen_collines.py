"""
draw_collines (io_devices/README.md): the field widths R and C at every boundary, the README's byte
example, KEEP / COPY / END and the auto-end at h, columns in any order and revisited - and a property
test: an encoder written HERE, from the README alone, turns >= 500 random target pictures into
draw_collines / draw_raw streams, and the device must reproduce every picture exactly.
"""

import random
from collections import Counter
from typing import Any, List, Optional, Sequence, Tuple

import pytest

from flipjump.interpreter.io_devices.ScreenIO import InMemoryScreen, column_field_width, row_field_width
from flipjump.utils.exceptions import IODeviceException
from tests.unit import screen_stream as ss


def screen_after(stream: bytes) -> InMemoryScreen:
    device = InMemoryScreen()
    ss.feed(device, stream)
    return device


def column(device: InMemoryScreen, x: int) -> List[int]:
    return device.pixel_indices[x :: device.width]  # noqa: E203


# ---------------------------------------------------------------- the README's example


README_EXAMPLE = bytes.fromhex('01 04 00 03 00 08' '11 30 05 D1 F3' '1F')


def test_the_readmes_example() -> None:
    device = screen_after(README_EXAMPLE)
    assert (device.width, device.height, device.format) == (4, 3, 8)
    # column 0 filled with 5, column 1 copied from it, the rest colour 0
    assert device.pixel_indices == [5, 5, 0, 0] * 3
    assert device.frame_count == 1
    assert ss.draw_collines([(0, [('fill', 3, 5)]), (1, [('copy', 3)])], 4, 3, 8) == README_EXAMPLE[6:11]


def test_the_readmes_example_bit_by_bit() -> None:
    device = InMemoryScreen()
    ss.feed_bits(device, README_EXAMPLE)
    assert device.pixel_indices == [5, 5, 0, 0] * 3


def test_control_the_readmes_example_with_its_copy_moved_to_column_0() -> None:
    """the negative control: D1 -> D0 makes it a COPY in column 0"""
    stream = README_EXAMPLE.replace(bytes([0xD1]), bytes([0xD0]))
    with pytest.raises(IODeviceException) as failure:
        ss.feed(InMemoryScreen(), stream)
    assert str(failure.value) == (
        'ScreenIO: draw_collines (0x11) at output byte 6, frame 0, column 0, cursor 0: '
        'COPY copies column x - 1, and column 0 has none'
    )


# ---------------------------------------------------------------- R and C


@pytest.mark.parametrize(
    'height, row_bits',
    [(1, 4), (11, 4), (12, 8), (251, 8), (252, 12), (4091, 12), (4092, 16), (65_531, 16)],
)
def test_the_row_field_width_at_every_boundary(height: int, row_bits: int) -> None:
    assert row_field_width(height) == row_bits
    # drawn with R-bit row fields, a full column of colour 1 lands exactly
    device = screen_after(
        ss.init_screen(1, height, 1) + ss.command(0x11, (0, 4), (height, row_bits), (1, 1), (15, 4)) + ss.PRESENT
    )
    assert device.pixel_indices == [1] * height


@pytest.mark.parametrize(
    'width, column_bits',
    [(1, 4), (14, 4), (15, 8), (254, 8), (255, 12), (4094, 12), (4095, 16), (65_534, 16)],
)
def test_the_column_field_width_at_every_boundary(width: int, column_bits: int) -> None:
    assert column_field_width(width) == column_bits
    # the last column, drawn with a C-bit column field (and END_CMD = 2^C - 1)
    stream = ss.init_screen(width, 1, 1) + ss.command(
        0x11, (width - 1, column_bits), (1, 4), (1, 1), (2**column_bits - 1, column_bits)
    )
    device = screen_after(stream)
    assert device.pixel_indices[-1] == 1 and sum(device.pixel_indices) == 1


def test_the_widths_are_the_readmes() -> None:
    for height in range(1, 5000):
        assert row_field_width(height) == ss.field_widths(1, height)[0]
    for width in range(1, 5000):
        assert column_field_width(width) == ss.field_widths(width, 1)[1]


# ---------------------------------------------------------------- the items


def test_end_leaves_the_rows_below_the_cursor() -> None:
    device = screen_after(ss.init_screen(2, 4, 8) + ss.draw_raw([9] * 8, 8))
    ss.feed(device, ss.draw_collines([(1, [('fill', 2, 3), ('end',)])], 2, 4, 8))
    assert column(device, 1) == [3, 3, 9, 9]
    assert column(device, 0) == [9] * 4  # a column never mentioned keeps its pixels


def test_a_column_ends_by_itself_at_h() -> None:
    # after reaching h the next field is a column field: here END_CMD, which as a row field would be END
    device = screen_after(
        ss.init_screen(3, 2, 8)
        + ss.draw_collines([(2, [('fill', 2, 4)]), (0, [('fill', 1, 6), ('fill', 2, 7)])], 3, 2, 8)
    )
    assert device.pixel_indices == [6, 0, 4, 7, 0, 4]


def test_keep_keeps_the_last_presented_frame() -> None:
    device = screen_after(ss.init_screen(1, 4, 8) + ss.draw_raw([1, 2, 3, 4], 8) + ss.PRESENT)
    ss.feed(device, ss.draw_collines([(0, [('keep', 2), ('fill', 4, 9)])], 1, 4, 8) + ss.PRESENT)
    assert device.pixel_indices == [1, 2, 9, 9]


def test_keep_after_an_earlier_draw_in_the_same_frame_keeps_the_new_pixels() -> None:
    device = screen_after(ss.init_screen(1, 4, 8) + ss.draw_raw([1, 2, 3, 4], 8) + ss.PRESENT)
    ss.feed(device, ss.draw_collines([(0, [('fill', 4, 7)])], 1, 4, 8))  # this frame draws the column ...
    ss.feed(device, ss.draw_collines([(0, [('keep', 3), ('fill', 4, 8)])], 1, 4, 8))  # ... then keeps its top
    assert device.pixel_indices == [7, 7, 7, 8]


def test_keep_acts_from_the_cursor_not_from_row_0() -> None:
    device = screen_after(ss.init_screen(1, 5, 8) + ss.draw_raw([1, 2, 3, 4, 5], 8))
    ss.feed(device, ss.draw_collines([(0, [('fill', 2, 9), ('keep', 4), ('fill', 5, 6)])], 1, 5, 8))
    assert device.pixel_indices == [9, 9, 3, 4, 6]


def test_copy_copies_the_left_column_from_the_cursor() -> None:
    device = screen_after(ss.init_screen(2, 4, 8) + ss.draw_raw([1, 5, 2, 6, 3, 7, 4, 8], 8))
    ss.feed(device, ss.draw_collines([(1, [('fill', 1, 9), ('copy', 3)])], 2, 4, 8))
    assert column(device, 1) == [9, 2, 3, 8]


def test_copy_after_x_minus_1_was_redrawn_copies_the_new_pixels() -> None:
    device = screen_after(ss.init_screen(2, 3, 8) + ss.draw_raw([1, 1, 1, 1, 1, 1], 8) + ss.PRESENT)
    ss.feed(device, ss.draw_collines([(0, [('fill', 3, 4)]), (1, [('copy', 3)])], 2, 3, 8))
    assert column(device, 1) == [4, 4, 4]


def test_copy_before_x_minus_1_is_redrawn_copies_the_old_pixels() -> None:
    device = screen_after(ss.init_screen(2, 3, 8) + ss.draw_raw([1, 2, 1, 2, 1, 2], 8) + ss.PRESENT)
    ss.feed(device, ss.draw_collines([(1, [('copy', 3)]), (0, [('fill', 3, 4)])], 2, 3, 8))
    assert column(device, 0) == [4, 4, 4] and column(device, 1) == [1, 1, 1]


def test_columns_in_any_order_skipped_and_revisited() -> None:
    columns: List[Tuple[int, List[Tuple[Any, ...]]]] = [
        (3, [('fill', 3, 1)]),
        (0, [('fill', 3, 2)]),
        (3, [('keep', 1), ('fill', 2, 7), ('end',)]),  # an overlay: KEEP down to it, then fill
        (0, [('fill', 1, 5), ('end',)]),
    ]
    device = screen_after(ss.init_screen(4, 3, 8) + ss.draw_collines(columns, 4, 3, 8) + ss.PRESENT)
    assert device.pixel_indices == [5, 0, 0, 1, 2, 0, 0, 7, 2, 0, 0, 1]


def test_an_empty_draw_collines_draws_nothing() -> None:
    device = screen_after(ss.init_screen(2, 2, 8) + ss.draw_raw([1, 2, 3, 4], 8) + ss.draw_collines([], 2, 2, 8))
    assert device.pixel_indices == [1, 2, 3, 4]


def test_an_empty_column() -> None:
    device = screen_after(
        ss.init_screen(2, 2, 8) + ss.draw_raw([1, 2, 3, 4], 8) + ss.draw_collines([(1, [('end',)])], 2, 2, 8)
    )
    assert device.pixel_indices == [1, 2, 3, 4]


@pytest.mark.parametrize('bits', [1, 3, 5, 12, 16, 24])
def test_the_colour_field_is_b_bits(bits: int) -> None:
    colour = (1 << bits) - 2 if bits > 1 else 1
    device = screen_after(ss.init_screen(2, 2, bits) + ss.draw_collines([(1, [('fill', 2, colour)])], 2, 2, bits))
    assert column(device, 1) == [colour, colour]


# ---------------------------------------------------------------- the property test


class Encoder:
    """an independent, README-only encoder: a bit list, fields lsb first, zero padding."""

    def __init__(self) -> None:
        self.bits: List[int] = []

    def put(self, value: int, width: int) -> None:
        self.bits += [(value >> i) & 1 for i in range(width)]

    def end_command(self) -> None:
        self.bits += [0] * (-len(self.bits) % 8)

    def data(self) -> bytes:
        assert len(self.bits) % 8 == 0
        octets = [self.bits[i:][:8] for i in range(0, len(self.bits), 8)]
        return bytes(int(''.join(map(str, reversed(octet))), 2) for octet in octets)


def encode_init(enc: Encoder, width: int, height: int, screen_format: int) -> None:
    enc.put(0x01, 8)
    enc.put(width, 16)
    enc.put(height, 16)
    enc.put(screen_format, 8)
    enc.end_command()


def encode_raw(enc: Encoder, target: Sequence[int], bits: int) -> None:
    enc.put(0x10, 8)
    for value in target:
        enc.put(value, bits)
    enc.end_command()


def encode_collines(
    rng: random.Random,
    enc: Encoder,
    screen: List[int],
    target: Sequence[int],
    width: int,
    height: int,
    bits: int,
    stats: 'Counter[str]',
) -> None:
    """draw `target` over `screen` (the encoder's own model of what the device holds, updated as it goes):
    every column, in a random order, some first scribbled over and fixed later, each as random runs of
    fills, KEEPs, COPYs and ENDs that are correct for the model at that moment."""
    row_bits = min(r for r in (4, 8, 12, 16) if height < 2**r - 4)
    column_bits = min(c for c in (4, 8, 12, 16) if width < 2**c - 1)
    end, keep, copy = 2**row_bits - 1, 2**row_bits - 2, 2**row_bits - 3

    def cell(x: int, y: int) -> int:
        return y * width + x

    def run_length(x: int, start: int, matches) -> int:  # type: ignore[no-untyped-def]
        length = 0
        while start + length < height and matches(start + length):
            length += 1
        return length

    def emit_column(x: int, wanted: Sequence[int]) -> None:
        enc.put(x, column_bits)
        cursor = 0
        while cursor < height:
            if all(screen[cell(x, y)] == wanted[y] for y in range(cursor, height)) and rng.random() < 0.5:
                enc.put(end, row_bits)
                stats['end'] += 1
                return
            options = []
            fill_length = run_length(x, cursor, lambda y: wanted[y] == wanted[cursor])
            options.append(('fill', fill_length))
            keep_length = run_length(x, cursor, lambda y: screen[cell(x, y)] == wanted[y])
            if keep_length:
                options.append(('keep', keep_length))
            if x > 0:
                copy_length = run_length(x, cursor, lambda y: screen[cell(x - 1, y)] == wanted[y])
                if copy_length:
                    options.append(('copy', copy_length))
            kind, longest = rng.choice(options)
            stop = cursor + rng.randint(1, longest)
            stats[kind] += 1
            stats['auto-end'] += stop == height
            if kind == 'fill':
                enc.put(stop, row_bits)
                enc.put(wanted[cursor], bits)
            else:
                enc.put(keep if kind == 'keep' else copy, row_bits)
                enc.put(stop, row_bits)
            for y in range(cursor, stop):
                source = cell(x - 1, y) if kind == 'copy' else None
                screen[cell(x, y)] = screen[source] if source is not None else wanted[y]
            cursor = stop

    enc.put(0x11, 8)
    order = list(range(width))
    rng.shuffle(order)
    scribbled = rng.sample(order, k=rng.randint(0, min(3, width)))
    for x in scribbled:  # draw these wrong first; they are revisited below
        emit_column(x, [rng.randrange(1 << bits) for _ in range(height)])
        stats['revisited'] += 1
    for x in order:
        wanted = [target[cell(x, y)] for y in range(height)]
        if x not in scribbled and all(screen[cell(x, y)] == wanted[y] for y in range(height)) and rng.random() < 0.7:
            stats['skipped'] += 1
            continue  # skipped: it already shows its target
        emit_column(x, wanted)
    enc.put(2**column_bits - 1, column_bits)
    enc.end_command()
    assert screen == list(target)


def random_picture(rng: random.Random, size: int, bits: int, previous: Optional[List[int]]) -> List[int]:
    palette_size = 1 << bits
    colours = [rng.randrange(palette_size) for _ in range(rng.randint(1, 4))]
    picture = []
    for i in range(size):
        if previous is not None and rng.random() < 0.4:
            picture.append(previous[i])
        elif picture and rng.random() < 0.6:
            picture.append(picture[-1])
        else:
            picture.append(rng.choice(colours))
    return picture


def random_size(rng: random.Random) -> Tuple[int, int]:
    roll = rng.random()
    if roll < 0.08:  # a tall or wide screen: the 8- and 12-bit fields and their edges
        return rng.choice(
            [
                (rng.randint(1, 3), rng.choice([11, 12, 251, 252, 300])),
                (rng.choice([14, 15, 254, 255, 300]), rng.randint(1, 3)),
            ]
        )
    return rng.randint(1, 18), rng.randint(1, 14)


def test_random_pictures_round_trip_through_the_device() -> None:
    rng = random.Random(0x5C12EE)
    screens = frames = 0
    stats: 'Counter[str]' = Counter()
    while frames < 600:
        width, height = random_size(rng)
        screen_format = rng.choice([*range(1, 17), 24])
        bits = screen_format
        enc = Encoder()
        encode_init(enc, width, height, screen_format)
        device = InMemoryScreen()
        model = [0] * (width * height)
        previous: Optional[List[int]] = None
        stream_frames = rng.randint(1, 4)
        targets = []
        for _ in range(stream_frames):
            target = random_picture(rng, width * height, bits, previous)
            if rng.random() < 0.2:
                encode_raw(enc, target, bits)
                model = list(target)
            else:
                encode_collines(rng, enc, model, target, width, height, bits, stats)
                stats['collines'] += 1
            enc.put(0x1F, 8)
            targets.append(target)
            previous = target
        stream = enc.data()
        presented = []
        original_present = device._present

        def record(device: InMemoryScreen = device, original=original_present) -> None:  # type: ignore[no-untyped-def]
            original()
            presented.append(list(device.pixel_indices))

        device._present = record  # type: ignore[method-assign]
        ss.feed(device, stream)
        assert presented == targets, (width, height, screen_format)
        assert device.frame_count == stream_frames
        screens += 1
        frames += stream_frames
    assert screens >= 150 and frames >= 600
    # not vacuous: every kind of item, and every way a column can go, was exercised many times
    assert all(
        stats[kind] >= 200 for kind in ('fill', 'keep', 'copy', 'end', 'auto-end', 'revisited', 'skipped')
    ), stats


def test_control_the_property_test_sees_a_wrong_picture() -> None:
    """the round trip's own negative control: a stream with one colour bit flipped reproduces a different
    picture, and the same stream cut by its last byte is refused with the exact message."""
    rng = random.Random(7)
    enc = Encoder()
    encode_init(enc, 6, 5, 8)
    target = random_picture(rng, 30, 8, None)
    encode_raw(enc, target, 8)
    stream = enc.data()
    assert screen_after(stream).pixel_indices == target
    flipped = bytearray(stream)
    flipped[6 + 1 + 3] ^= 0x01
    assert screen_after(bytes(flipped)).pixel_indices != target
    cut = screen_after(stream[:-1])
    with pytest.raises(IODeviceException) as failure:
        cut.get_output()
    assert str(failure.value) == (
        'ScreenIO: draw_raw (0x10) at output byte 6, frame 0, pixel (5, 4): '
        "the program's output ended inside draw_raw (0x10): 240 of its bits read"
    )

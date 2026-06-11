"""
unit-tests for the InMemoryScreen256 output-device (WI-B) - headless-first.

the FJ program emits command bytes over the output stream (init_screen / set_palette /
update_screen / update_rectangle); buffer contents are read from the interpreter memory via
the device<->memory hook. the headless backend keeps the expanded RGB frame, writes one PNG
per present, timestamps presents, and keeps a per-frame hash log for golden tests.
"""

import hashlib
import zlib
from pathlib import Path
from typing import Dict

import pytest

from flipjump.interpreter.io_devices.ScreenIO import InMemoryScreen256
from flipjump.interpreter.io_devices.device_memory import DeviceMemory
from flipjump.utils.exceptions import IODeviceException


class FakeDeviceMemory(DeviceMemory):
    def __init__(self, memory_width: int = 64):
        self.memory_width = memory_width
        self.words: Dict[int, int] = {}

    def read_word(self, word_address: int) -> int:
        return self.words.get(word_address, 0)

    def write_word(self, word_address: int, value: int) -> None:
        self.words[word_address] = value & ((1 << self.memory_width) - 1)


def write_byte(device: InMemoryScreen256, value: int) -> None:
    for i in range(8):
        device.write_bit((value >> i) & 1 == 1)


def write_u16(device: InMemoryScreen256, value: int) -> None:
    write_byte(device, value & 0xFF)
    write_byte(device, (value >> 8) & 0xFF)


def write_address(device: InMemoryScreen256, bit_address: int, memory_width: int = 64) -> None:
    for i in range(memory_width // 8):
        write_byte(device, (bit_address >> (8 * i)) & 0xFF)


def make_screen(tmp_path: Path) -> 'tuple[InMemoryScreen256, FakeDeviceMemory]':
    memory = FakeDeviceMemory()
    device = InMemoryScreen256(frames_dir=tmp_path)
    device.attach_memory(memory)
    return device, memory


PALETTE_ADDRESS = 0x10000
SCREEN_ADDRESS = 0x20000
DW = 128  # w=64


def store_palette(memory: FakeDeviceMemory, colors: 'list[tuple[int, int, int]]') -> None:
    # 3 packed-bytes (R, G, B) per entry, each in its own op
    for entry, (r, g, b) in enumerate(colors):
        base = PALETTE_ADDRESS + 3 * entry * DW
        memory.write_data_byte(base, r)
        memory.write_data_byte(base + DW, g)
        memory.write_data_byte(base + 2 * DW, b)


def store_pixels(memory: FakeDeviceMemory, base: int, pixels: 'list[int]') -> None:
    for k, pixel in enumerate(pixels):
        memory.write_data_byte(base + k * DW, pixel)


def init_4x2(device: InMemoryScreen256, memory: FakeDeviceMemory, bpp: int = 8) -> None:
    write_byte(device, 1)  # CMD init_screen
    write_u16(device, 4)
    write_u16(device, 2)
    write_byte(device, bpp)
    write_u16(device, 2)  # palette_size
    store_palette(memory, [(10, 20, 30), (200, 100, 0)])
    write_byte(device, 2)  # CMD set_palette
    write_address(device, PALETTE_ADDRESS)


def test_init_set_palette_update_screen(tmp_path: Path) -> None:
    device, memory = make_screen(tmp_path)
    init_4x2(device, memory)

    store_pixels(memory, SCREEN_ADDRESS, [0, 1, 0, 1, 1, 0, 1, 0])
    write_byte(device, 3)  # CMD update_screen
    write_address(device, SCREEN_ADDRESS)

    assert device.frame_count == 1
    assert device.last_frame_rgb[0] == (10, 20, 30)
    assert device.last_frame_rgb[1] == (200, 100, 0)
    assert len(device.last_frame_rgb) == 8

    # one PNG per present, with a valid signature and the right size
    frame_files = sorted(tmp_path.glob('*.png'))
    assert len(frame_files) == 1
    png = frame_files[0].read_bytes()
    assert png.startswith(b'\x89PNG\r\n\x1a\n')

    # the hash log: (time_ns, sha256-of-frame), reproducible
    assert len(device.frame_hashes) == 1
    time_ns, frame_hash = device.frame_hashes[0]
    assert time_ns > 0
    expected = hashlib.sha256(bytes([0, 1, 0, 1, 1, 0, 1, 0]) + bytes([10, 20, 30, 200, 100, 0])).hexdigest()
    assert frame_hash == expected


def test_update_rectangle_blits_into_frame(tmp_path: Path) -> None:
    device, memory = make_screen(tmp_path)
    init_4x2(device, memory)

    store_pixels(memory, SCREEN_ADDRESS, [0] * 8)
    write_byte(device, 3)
    write_address(device, SCREEN_ADDRESS)

    rect_address = 0x30000
    store_pixels(memory, rect_address, [1, 1])  # a 1x2 column
    write_byte(device, 4)  # CMD update_rectangle
    write_u16(device, 2)  # x
    write_u16(device, 0)  # y
    write_u16(device, 1)  # rect w
    write_u16(device, 2)  # rect h
    write_address(device, rect_address)

    assert device.frame_count == 2
    # pixel (2,0) and (2,1) are now palette entry 1
    assert device.last_frame_rgb[2] == (200, 100, 0)
    assert device.last_frame_rgb[4 + 2] == (200, 100, 0)
    assert device.last_frame_rgb[0] == (10, 20, 30)


def test_bpp4_masks_pixel_indices(tmp_path: Path) -> None:
    device, memory = make_screen(tmp_path)
    init_4x2(device, memory, bpp=4)

    # a stored byte 0x31 must be masked to its low nibble (1) at bpp=4
    store_pixels(memory, SCREEN_ADDRESS, [0x31, 0, 0, 0, 0, 0, 0, 0])
    write_byte(device, 3)
    write_address(device, SCREEN_ADDRESS)
    assert device.last_frame_rgb[0] == (200, 100, 0)


def test_update_screen_raw_streams_pixels(tmp_path: Path) -> None:
    device, memory = make_screen(tmp_path)
    init_4x2(device, memory)

    write_byte(device, 5)  # CMD update_screen_raw - pixels arrive in-stream, no memory read
    for pixel in [0, 1, 0, 1, 1, 0, 1, 0]:
        write_byte(device, pixel)

    assert device.frame_count == 1
    assert device.last_frame_rgb[0] == (10, 20, 30)
    assert device.last_frame_rgb[1] == (200, 100, 0)
    # byte-identical frame-hash to a memory-hook update_screen of the same pixels
    expected = hashlib.sha256(bytes([0, 1, 0, 1, 1, 0, 1, 0]) + bytes([10, 20, 30, 200, 100, 0])).hexdigest()
    assert device.frame_hashes[0][1] == expected


def test_update_screen_raw_masks_bpp4(tmp_path: Path) -> None:
    device, memory = make_screen(tmp_path)
    init_4x2(device, memory, bpp=4)

    write_byte(device, 5)
    write_byte(device, 0x31)  # masked to its low nibble (1) at bpp=4
    for _ in range(7):
        write_byte(device, 0)
    assert device.last_frame_rgb[0] == (200, 100, 0)


def test_update_screen_raw_requires_initialized_screen(tmp_path: Path) -> None:
    device, _ = make_screen(tmp_path)
    with pytest.raises(IODeviceException):
        write_byte(device, 5)


def test_update_screen_raw_works_without_the_memory_hook(tmp_path: Path) -> None:
    # raw frames need no device<->memory hook at all (palette_size=0: all pixels are black)
    device = InMemoryScreen256(frames_dir=tmp_path)
    write_byte(device, 1)  # CMD init_screen
    write_u16(device, 4)
    write_u16(device, 2)
    write_byte(device, 8)
    write_u16(device, 0)  # palette_size

    write_byte(device, 5)
    for pixel in [0, 1, 0, 1, 1, 0, 1, 0]:
        write_byte(device, pixel)

    assert device.frame_count == 1
    assert device.last_frame_rgb == [(0, 0, 0)] * 8
    assert (tmp_path / 'frame_000000.png').exists()


def test_png_pixels_decode_correctly(tmp_path: Path) -> None:
    device, memory = make_screen(tmp_path)
    init_4x2(device, memory)
    store_pixels(memory, SCREEN_ADDRESS, [1, 0, 0, 0, 0, 0, 0, 1])
    write_byte(device, 3)
    write_address(device, SCREEN_ADDRESS)

    png = sorted(tmp_path.glob('*.png'))[0].read_bytes()
    idat_start = png.index(b'IDAT') + 4
    idat_length = int.from_bytes(png[idat_start - 8 : idat_start - 4], 'big')  # noqa: E203
    raw = zlib.decompress(png[idat_start : idat_start + idat_length])  # noqa: E203
    # 2 scanlines of (filter byte 0 + 4 RGB pixels)
    assert raw[0] == 0
    assert raw[1:4] == bytes([200, 100, 0])
    assert raw[4:7] == bytes([10, 20, 30])

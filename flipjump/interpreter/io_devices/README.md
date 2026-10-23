# FlipJump I/O devices

A FlipJump program has exactly two I/O channels: an **input bit stream** and an **output bit stream**.
Every device here is a protocol on top of them. The program writes commands to its output and reads
events from its input; the device does the rest.

> **Status.** This file is the *planned* API. Where today's `ScreenIO.py` and `KeyboardIO.py` still
> differ from it, [Changes from today's implementation](#changes-from-todays-implementation) lists how.
> The other devices are as described.

| Device | File | Channels | Use |
|---|---|---|---|
| Standard | `StandardIO.py` | stdin / stdout | the default (`fj --io standard`) |
| PC | `pygame_window.py` | screen (output) + keyboard (input), one window | `fj --io pc` |
| Screen | `ScreenIO.py` | output | the screen protocol (headless or in the PC window) |
| Keyboard | `KeyboardIO.py` | input | the keyboard protocol (live or scripted) |
| Fixed | `FixedIO.py` | a bytes buffer in, captured out | tests |
| Broken | `BrokenIO.py` | none (raises on any I/O) | programs that must do no I/O |

The PC window needs `pip install flipjump[io]` (pygame-ce). A `.fjm` can carry its I/O mode in its header,
so `fj --run game.fjm` needs no `--io` flag.

---

## Keyboard

The program **polls**: it reads one status nibble per poll (`hex.input_hex`). There is no timer; the program
keeps its own frame clock, and idle polling never hits end-of-input.

| Status nibble | Meaning | Then |
|---|---|---|
| `0x0` | no event | — |
| `0x9` | a key was **pressed** | read the keycode byte (`hex.input`) |
| `0x8` | a key was **released** | read the keycode byte (`hex.input`) |

The keycode byte **must** be read after an event, or every later poll is out of phase.

### Keycodes

The codes are the ones Arduino's `Keyboard.h` uses: **ASCII below `0x80`**, the **modifiers at `0x80`–`0x87`**,
and **every other key at `0x88` + its USB HID usage ID**.

- A key is reported as the key, not as what it types: letters are lowercase (`'a'` = 97), the digit row is
  `'0'`–`'9'`, whatever modifiers are held. Shift is its own event.
- A key that has an ASCII code is always sent as that code: Backspace `8`, Tab `9`, Enter `13`, Esc `27`,
  Space `32`. So `0x88`–`0xC0` (the HID numbers of those keys and of the printable keys) are never sent.

| Code | Key |
|---|---|
| `0x08` `0x09` `0x0D` `0x1B` | Backspace, Tab, Enter, Esc |
| `0x20`–`0x7E` | the printable keys: Space, `'0'`–`'9'`, `'a'`–`'z'`, punctuation (unshifted) |
| `0x80` `0x81` `0x82` `0x83` | Left Ctrl, Left Shift, Left Alt, Left GUI (Windows / Command) |
| `0x84` `0x85` `0x86` `0x87` | Right Ctrl, Right Shift, Right Alt, Right GUI |
| `0xC1` | Caps Lock |
| `0xC2`–`0xCD` | F1–F12 |
| `0xCE` `0xCF` `0xD0` | Print Screen, Scroll Lock, Pause |
| `0xD1` `0xD2` `0xD3` | Insert, Home, Page Up |
| `0xD4` `0xD5` `0xD6` | Delete, End, Page Down |
| `0xD7` `0xD8` `0xD9` `0xDA` | **Right, Left, Down, Up** |
| `0xDB` | Num Lock |
| `0xDC` `0xDD` `0xDE` `0xDF` `0xE0` | keypad `/` `*` `-` `+` Enter |
| `0xE1`–`0xE9`, `0xEA`, `0xEB` | keypad `1`–`9`, `0`, `.` |
| `0xED` | Menu |
| `0xF0`–`0xFB` | F13–F24 |

A program that wants "either Ctrl" tests both `0x80` and `0x84` (the same for Shift, Alt and GUI).
Keys not in the table are not delivered. In the PC window F11 toggles fullscreen and is never delivered.
Scripted input (tests, replays): a text file of `tic, down/up, keycode` lines (`ScriptedKeyEventSource`).

---

## Screen

### How a command is written

1. A command starts on a **byte boundary** with its **opcode byte**.
2. Its fields follow, **packed back to back at exactly their width in bits**, least-significant bit first
   (the order FlipJump already outputs bits in). A 4-bit pixel costs 4 bits; 8 pixels of 3 bits take 3 bytes.
3. The command ends with **zero bits up to the next byte boundary**.
4. Multi-byte numbers (`w`, `h`, ...) are little-endian.
5. Nothing reaches the screen until **`present`** (`0x1F`).

### Opcodes

| Opcode | Command | Fields | Group |
|---|---|---|---|
| `0x00` | — | reserved: an error (catches a stray zero byte) | |
| `0x01` | `init_screen` | `w:16` `h:16` `format:8` | setup |
| `0x02` | `define_palette` | `slot:8` `first:B` `last:B` then `(last−first+1) × (R:8 G:8 B:8)` | setup |
| `0x03` | `set_max_fps` | `fps:8` (0 = no cap) | setup |
| `0x04` | `set_window_title` | UTF-8 bytes, then `0x00` | setup |
| `0x05` | `set_window_icon` | `w:8` `h:8` then `w×h` colours of `B` bits | setup |
| `0x06` | `select_palette` | `slot:8` | setup |
| `0x07` | `builtin_palette` | `slot:8` `id:8` | setup |
| `0x10` | `draw_raw` | `w×h` colours of `B` bits, row-major | draw |
| `0x11` | `draw_collines` | columns (below), ended by the top column value | draw |
| `0x1F` | `present` | — | show |

`B` = the format's bits per colour. `init_screen` must come first; `0x02`, `0x06`, `0x07` exist only in indexed
formats.

### Formats (`init_screen`'s `format` = bits per colour)

| `format` | Model | Colour | Default palette in slot 0 |
|---|---|---|---|
| `1` | indexed | 1 bit | black, white |
| `2` | indexed | 2 bits | 4 greys |
| `4` | indexed | 4 bits | the 16 EGA/VGA colours |
| `8` | indexed | 8 bits | xterm-256: the 16 colours, a 6×6×6 RGB cube, 24 greys |
| `3`, `5`–`7`, `9`–`16` | indexed | that many bits | the RGB cube of that many bits (below) |
| `17`–`23` | — | refused | — |
| `24` | direct RGB | 24 bits: `R:8 G:8 B:8` | none (no palettes) |

**The RGB cube of `b` bits**: green gets `⌈b/3⌉` bits, red `⌈(b − green)/2⌉`, blue the rest —
3 → 1:1:1 (8 colours), 6 → 2:2:2, 12 → 4:4:4, 15 → 5:5:5, 16 → 5:6:5 ("high colour").

A colour value `≥ 2^B` is an error. The picture starts as colour 0 everywhere.

### Palettes (indexed formats)

- The picture holds **colour indices**; the palette **selected when `present` runs** gives them their RGB.
  So switching palette (a flash, a fade) costs 2 bytes, not a redraw.
- 256 slots. Slot 0 holds the format's default; the others start as copies of it.
- `define_palette` sets entries `first`…`last` (inclusive) of one slot. Entries are always 8-bit R, G, B.
  A large palette can be sent in several ranges.
- `builtin_palette` copies a built-in into a slot:

| `id` | Built-in |
|---|---|
| `0` | black / white |
| `1` | grey ramp, `2^B` levels |
| `2` | EGA-16 |
| `3` | xterm-256 |
| `4` | the RGB cube of `B` bits |

### `draw_collines` — the picture as column runs

The fastest way to draw: each column is a list of **runs** from the top down, and the program has already
resolved what is in front, so the device only fills.

**Field widths** (fixed by `init_screen`, always a multiple of 4 bits):

| Field | Width | Top values are tokens | Limit |
|---|---|---|---|
| row (`y2`, `y`) | `R` = the smallest of 4, 8, 12, 16 with `h < 2^R − 4` | the top **4** | `h ≤ 11 / 251 / 4,091 / 65,531` |
| column (`x`, `src`) | `C` = the smallest of 4, 8, 12, 16 with `w < 2^C` | the top **1** | `w ≤ 15 / 255 / 4,095 / 65,535` |

**Grammar:**

```
draw_collines := 0x11  ( column )*  END_CMD
column        := x  item*                       x = the column to draw (any order; repeats allowed)
item          := y2 colour                      fill rows [cursor, y2) with colour; cursor = y2
               | KEEP y                         leave rows [cursor, y) as they are; cursor = y
               | COPY src y                     copy rows [cursor, y) from column src; cursor = y
               | END                            the column is done (rows below the cursor are left as they are)
```

| Row-field value | Token | At `R = 8` |
|---|---|---|
| `2^R − 1` | END (column) | `0xFF` |
| `2^R − 2` | KEEP | `0xFE` |
| `2^R − 3` | COPY | `0xFD` |
| `2^R − 4` | reserved | `0xFC` |
| `0 … h` | a row | `0x00`–`0xFB` |

| Column-field value | Meaning |
|---|---|
| `2^C − 1` | END_CMD: the command is over |
| `0 … w−1` | a column |

**Rules:**

- Each column's cursor starts at row 0. Every fill, KEEP and COPY must move it forward: `cursor < y2 ≤ h`.
- A column also ends by itself when the cursor reaches `h` (so full columns need no END).
- KEEP and COPY act on rows `[cursor, y)` only — from where the column is now, not from row 0.
- COPY reads the picture as it is at that moment, including what this command already drew.
- Columns can come in any order, be skipped, or be drawn again (e.g. an overlay: `KEEP` down to it, then fill).

### Example

A 4×3 screen, 8-bit colour: column 0 filled with colour 5, column 1 copied from it, then shown.
Here `R = 4` and `C = 4` (both fields are nibbles); the first field of each byte is in its low nibble.

```
01  04 00  03 00  08      init_screen  w=4 h=3 format=8
11                        draw_collines
30 05                       x=0, y2=3 | colour 0x05            (column 0: rows 0-2 = 5, ends at h)
D1 30                       x=1, COPY | src=0, y=3            (column 1: rows 0-2 copied)
0F                          END_CMD (x=0xF), then 4 zero bits of padding
1F                        present
```

### Errors

The device raises (`IODeviceException`) on: an unknown or reserved opcode; any command before
`init_screen`; a field out of range (a colour `≥ 2^B`, a row past `h`, a column past `w`, a cursor that does
not move forward, COPY's `src` out of range); a palette command in RGB format; a format of 17–23 or 0.

### Backends

| Backend | Output per `present` |
|---|---|
| headless (default in tests) | the RGB frame in memory, a PNG per frame, a sha256 per frame (for golden tests) |
| PC window | a scaled window; `set_max_fps` makes `present` wait (the headless backend never waits) |

---

## Changes from today's implementation

### Screen

| Today's `ScreenIO.py` | This API |
|---|---|
| `0x01 init_screen [w:2][h:2][bpp:1][palette_size:2]` | `0x01 init_screen [w:2][h:2][format:1]` |
| `0x02 set_palette [address]` (read from memory) | `0x02 define_palette` (in the stream) + `0x06 select_palette` |
| `0x03` / `0x04` / `0x06` framebuffer presents (read from memory) | removed: draw with `0x10` / `0x11` |
| `0x05 update_screen_raw` | `0x10 draw_raw` + `0x1F present` (bit-packed at the format's width) |
| `0x0B begin_frame_collines` (`[x]…0xFF`, `0xFE` / `0xFD` / `0xFC`) | `0x11 draw_collines` + `0x1F present` (tokens at the top of nibble-sized fields; `COPY` names its source) |
| `0x12` / `0x13` / `0x14` title / icon / max fps | `0x04` / `0x05` / `0x03` |

The screen never reads program memory, so it needs no device-memory hook.

### Keyboard

The protocol (status nibble, then keycode) is unchanged; the codes above `0x80` move to Arduino's.

| Key | Today's `KeyboardIO.py` | This API |
|---|---|---|
| Up, Down, Left, Right | `0x80` `0x81` `0x82` `0x83` | `0xDA` `0xD9` `0xD8` `0xD7` |
| Shift | `0x84` (either) | `0x81` left, `0x85` right |
| Ctrl | `0x85` (either) | `0x80` left, `0x84` right |
| Alt | `0x86` (either) | `0x82` left, `0x86` right |
| GUI, F-keys, Insert … Page Down, keypad, Caps / Num / Scroll Lock, Pause, Print Screen, Menu | not delivered | the table above |

The codes `0x80`–`0x86` mean different keys before and after, so a program that reads the keyboard must be
rebuilt for this change, together with the screen's.

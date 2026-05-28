"""Phase 3 batch 1: implement the foundations programs from CATALOG.md.

Run from the repo root:

    python scripts/batch01_foundations.py

Each call writes .fj/.in/.out, verifies via the FlipJump interpreter, and appends
CSV rows. Idempotent — safe to re-run.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from add_catalog_program import add_program  # noqa: E402


# ============== Simple "print fixed string, no input" pattern ==============


def simple(slug, nnnn, name, desc, output_str):
    """Convenience for no-input fixed-output programs."""
    fj = "main\n\n" "def main {\n" "    stl.startup\n" f'    stl.output "{output_str}"\n' "    stl.loop\n" "}\n"
    # Decode the source-level escapes (\n, \t, etc.) to raw bytes for the .out file.
    out_bytes = output_str.encode("utf-8").decode("unicode_escape").encode("utf-8")
    add_program(
        category="hello",
        slug=slug,
        nnnn=nnnn,
        name_display=name,
        description=desc,
        fj_body=fj,
        in_bytes=b"",
        out_bytes=out_bytes,
    )


# ---------------------------- hello (20 simple) ----------------------------

simple("hello_world", "0001", "Hello World", 'Prints "Hello, World!\\n" and exits.', "Hello, World!\\n")

simple(
    "hello_world_3x",
    "0003",
    "Hello World 3x",
    'Prints "Hello, World!\\n" three times consecutively.',
    "Hello, World!\\nHello, World!\\nHello, World!\\n",
)

simple(
    "hello_lowercase",
    "0005",
    "Hello Lowercase",
    'Prints "hello, world!\\n" (all-lowercase variant).',
    "hello, world!\\n",
)

simple(
    "hello_uppercase",
    "0006",
    "Hello Uppercase",
    'Prints "HELLO, WORLD!\\n" (all-uppercase variant).',
    "HELLO, WORLD!\\n",
)

simple("hello_reversed", "0007", "Hello Reversed", 'Prints "!dlroW ,olleH\\n" (reversed greeting).', "!dlroW ,olleH\\n")

simple(
    "hello_one_char_per_line",
    "0008",
    "Hello One Char Per Line",
    'Prints each character of "Hello, World!" on its own line (13 lines).',
    "H\\ne\\nl\\nl\\no\\n,\\n \\nW\\no\\nr\\nl\\nd\\n!\\n",
)

simple(
    "hello_two_lines",
    "0009",
    "Hello Two Lines",
    'Prints "Hello,\\nWorld!\\n" with the greeting split into two lines.',
    "Hello,\\nWorld!\\n",
)

simple(
    "hello_box",
    "0010",
    "Hello Box",
    'Three lines of 17 chars: top/bottom = 17 stars; middle = "* Hello, World! *".',
    "*****************\\n* Hello, World! *\\n*****************\\n",
)

simple(
    "hello_no_newline", "0011", "Hello No Newline", 'Prints "Hello, World!" with no trailing newline.', "Hello, World!"
)

simple(
    "hello_tab_sep",
    "0012",
    "Hello Tab Sep",
    'Prints "Hello,\\tWorld!\\n" with a literal tab between Hello, and World!.',
    "Hello,\\tWorld!\\n",
)

simple(
    "hello_question", "0013", "Hello Question", 'Prints "Hello, World?\\n" (question-mark variant).', "Hello, World?\\n"
)

simple(
    "hello_exclaim_3x",
    "0014",
    "Hello Exclaim 3x",
    'Prints "Hello, World!!!\\n" (three trailing exclamation marks).',
    "Hello, World!!!\\n",
)

simple(
    "hello_hex_codes",
    "0016",
    "Hello Hex Codes",
    "Prints the hex code-points of 'Hello, World!' separated by spaces.",
    "48 65 6c 6c 6f 2c 20 57 6f 72 6c 64 21\\n",
)

simple(
    "hello_ascii_first_five",
    "0017",
    "Hello ASCII First Five",
    "Prints the ASCII decimal codes of the first five characters of 'Hello' space-separated.",
    "72 101 108 108 111\\n",
)

simple(
    "hello_underline",
    "0018",
    "Hello Underline",
    'Prints "Hello, World!\\n" followed by 13 dashes + \\n.',
    "Hello, World!\\n-------------\\n",
)

simple(
    "hello_anonymous",
    "0020",
    "Hello Anonymous",
    'Prints "Hello, anonymous user!\\n" (no input).',
    "Hello, anonymous user!\\n",
)

simple(
    "hello_alpha_world",
    "0021",
    "Hello Alpha World",
    'Prints the lowercase alphabet followed by space and the greeting.',
    "abcdefghijklmnopqrstuvwxyz Hello, World!\\n",
)

simple(
    "hello_then_length",
    "0022",
    "Hello Then Length",
    'Prints "Hello, World!\\nLength: 13\\n".',
    "Hello, World!\\nLength: 13\\n",
)

simple(
    "hello_then_question",
    "0023",
    "Hello Then Question",
    'Prints greeting followed by "What\\u0027s your name?" on next line.',
    "Hello, World!\\nWhat's your name?\\n",
)

simple(
    "hello_world_overunder",
    "0025",
    "Hello World OverUnder",
    'Prints greeting sandwiched between two rows of 13 = signs.',
    "=============\\nHello, World!\\n=============\\n",
)


# ---------------------------- hello (3 read-line) ----------------------------


def read_line_program(slug, nnnn, name, desc, prefix_str, suffix_str, sample_name=b"Alice"):
    """Read one \\n-terminated line, echo as prefix + line + suffix."""
    fj = (
        "main\n\n"
        f"def main @ read_loop, print_ch, end < ch, nl {{\n"
        "    stl.startup\n"
        f'    stl.output "{prefix_str}"\n'
        "  read_loop:\n"
        "    bit.input ch\n"
        "    bit.if0 8, ch, end\n"
        "    bit.cmp 8, ch, nl, print_ch, end, print_ch\n"
        "  print_ch:\n"
        "    bit.print ch\n"
        "    ;read_loop\n"
        "  end:\n"
        f'    stl.output "{suffix_str}"\n'
        "    stl.loop\n"
        "}\n\n"
        "ch: bit.vec 8, 0\n"
        "nl: bit.vec 8, '\\n'\n"
    )
    out_bytes = (
        prefix_str.encode("utf-8").decode("unicode_escape").encode("utf-8")
        + sample_name
        + suffix_str.encode("utf-8").decode("unicode_escape").encode("utf-8")
    )
    add_program(
        category="hello",
        slug=slug,
        nnnn=nnnn,
        name_display=name,
        description=desc,
        fj_body=fj,
        in_bytes=sample_name + b"\n",
        out_bytes=out_bytes,
    )


read_line_program(
    "hello_user",
    "0002",
    "Hello User",
    'Reads a name and prints "Hello, <name>!\\n".',
    "Hello, ",
    "!\\n",
)

read_line_program(
    "hello_long_user",
    "0015",
    "Hello Long User",
    'Reads a name and prints "Welcome to FlipJump, <name>! Have a great day!\\n".',
    "Welcome to FlipJump, ",
    "! Have a great day!\\n",
)


# hello_two_users: read two names sequentially
def hello_two_users():
    fj = (
        "main\n\n"
        "def main @ read1, print1, after1, read2, print2, end < ch, nl {\n"
        "    stl.startup\n"
        '    stl.output "Hello, "\n'
        "  read1:\n"
        "    bit.input ch\n"
        "    bit.if0 8, ch, end\n"
        "    bit.cmp 8, ch, nl, print1, after1, print1\n"
        "  print1:\n"
        "    bit.print ch\n"
        "    ;read1\n"
        "  after1:\n"
        '    stl.output " and "\n'
        "  read2:\n"
        "    bit.input ch\n"
        "    bit.if0 8, ch, end\n"
        "    bit.cmp 8, ch, nl, print2, end, print2\n"
        "  print2:\n"
        "    bit.print ch\n"
        "    ;read2\n"
        "  end:\n"
        '    stl.output "!\\n"\n'
        "    stl.loop\n"
        "}\n\n"
        "ch: bit.vec 8, 0\n"
        "nl: bit.vec 8, '\\n'\n"
    )
    add_program(
        category="hello",
        slug="hello_two_users",
        nnnn="0019",
        name_display="Hello Two Users",
        description='Reads two names and prints "Hello, <name1> and <name2>!\\n".',
        fj_body=fj,
        in_bytes=b"Alice\nBob\n",
        out_bytes=b"Hello, Alice and Bob!\n",
    )


hello_two_users()


# ============================== io (8 simple) ==============================


def io_simple(slug, nnnn, name, desc, fj_body, in_bytes, out_bytes):
    add_program(
        category="io",
        slug=slug,
        nnnn=nnnn,
        name_display=name,
        description=desc,
        fj_body=fj_body,
        in_bytes=in_bytes,
        out_bytes=out_bytes,
    )


# 26. cat — echo stdin to stdout byte-for-byte until EOF.
io_simple(
    "cat",
    "0026",
    "Cat",
    "Reads stdin and echoes each byte to stdout until EOF.",
    (
        "main\n\n"
        "def main @ loop, end < ch {\n"
        "    stl.startup\n"
        "  loop:\n"
        "    bit.input ch\n"
        "    bit.if0 8, ch, end\n"
        "    bit.print ch\n"
        "    ;loop\n"
        "  end:\n"
        "    stl.loop\n"
        "}\n\n"
        "ch: bit.vec 8, 0\n"
    ),
    b"hello\0",
    b"hello",
)

# 30. count_bytes — read all stdin, print byte count.
# Strategy: a 16-bit bit-vector counter (supports up to 65535 bytes);
# bit.inc per byte; bit.print_dec_uint at the end.
io_simple(
    "count_bytes",
    "0030",
    "Count Bytes",
    "Reads all of stdin and prints the byte count as decimal + newline.",
    (
        "main\n\n"
        "def main @ loop, end < ch, counter {\n"
        "    stl.startup\n"
        "  loop:\n"
        "    bit.input ch\n"
        "    bit.if0 8, ch, end\n"
        "    bit.inc 16, counter\n"
        "    ;loop\n"
        "  end:\n"
        "    bit.print_dec_uint 16, counter\n"
        "    stl.output '\\n'\n"
        "    stl.loop\n"
        "}\n\n"
        "ch: bit.vec 8, 0\n"
        "counter: bit.vec 16, 0\n"
    ),
    b"hello\0",
    b"5\n",
)

# 31. count_lines — count '\n' bytes.
io_simple(
    "count_lines",
    "0031",
    "Count Lines",
    "Reads stdin and prints the number of newline bytes as decimal + newline.",
    (
        "main\n\n"
        "def main @ loop, inc_count, not_nl, end < ch, nl, counter {\n"
        "    stl.startup\n"
        "  loop:\n"
        "    bit.input ch\n"
        "    bit.if0 8, ch, end\n"
        "    bit.cmp 8, ch, nl, not_nl, inc_count, not_nl\n"
        "  inc_count:\n"
        "    bit.inc 16, counter\n"
        "  not_nl:\n"
        "    ;loop\n"
        "  end:\n"
        "    bit.print_dec_uint 16, counter\n"
        "    stl.output '\\n'\n"
        "    stl.loop\n"
        "}\n\n"
        "ch: bit.vec 8, 0\n"
        "nl: bit.vec 8, '\\n'\n"
        "counter: bit.vec 16, 0\n"
    ),
    b"a\nb\nc\n\0",
    b"3\n",
)

# 33. echo_twice
io_simple(
    "echo_twice",
    "0033",
    "Echo Twice",
    "Reads each byte of stdin and outputs it twice.",
    (
        "main\n\n"
        "def main @ loop, end < ch {\n"
        "    stl.startup\n"
        "  loop:\n"
        "    bit.input ch\n"
        "    bit.if0 8, ch, end\n"
        "    bit.print ch\n"
        "    bit.print ch\n"
        "    ;loop\n"
        "  end:\n"
        "    stl.loop\n"
        "}\n\n"
        "ch: bit.vec 8, 0\n"
    ),
    b"ab\0",
    b"aabb",
)

# 34. echo_thrice
io_simple(
    "echo_thrice",
    "0034",
    "Echo Thrice",
    "Reads each byte of stdin and outputs it three times.",
    (
        "main\n\n"
        "def main @ loop, end < ch {\n"
        "    stl.startup\n"
        "  loop:\n"
        "    bit.input ch\n"
        "    bit.if0 8, ch, end\n"
        "    bit.print ch\n"
        "    bit.print ch\n"
        "    bit.print ch\n"
        "    ;loop\n"
        "  end:\n"
        "    stl.loop\n"
        "}\n\n"
        "ch: bit.vec 8, 0\n"
    ),
    b"ab\0",
    b"aaabbb",
)

# 35. skip_first_byte
io_simple(
    "skip_first_byte",
    "0035",
    "Skip First Byte",
    "Reads stdin and outputs every byte except the very first one.",
    (
        "main\n\n"
        "def main @ read_first, loop, end < ch {\n"
        "    stl.startup\n"
        "  read_first:\n"
        "    bit.input ch\n"
        "    bit.if0 8, ch, end\n"
        "  loop:\n"
        "    bit.input ch\n"
        "    bit.if0 8, ch, end\n"
        "    bit.print ch\n"
        "    ;loop\n"
        "  end:\n"
        "    stl.loop\n"
        "}\n\n"
        "ch: bit.vec 8, 0\n"
    ),
    b"Xhello\0",
    b"hello",
)

# 27. uppercase_filter — for each byte, if a-z output (byte - 32) else output as-is.
io_simple(
    "uppercase_filter",
    "0027",
    "Uppercase Filter",
    "Reads stdin and prints each byte uppercased (a-z -> A-Z; others unchanged).",
    (
        "main\n\n"
        "def main @ loop, check_low, lower, print_unchanged, end < ch, a_lower, z_lower {\n"
        "    stl.startup\n"
        "  loop:\n"
        "    bit.input ch\n"
        "    bit.if0 8, ch, end\n"
        "    // if ch < 'a' -> unchanged; else check upper bound\n"
        "    bit.cmp 8, ch, a_lower, print_unchanged, check_low, check_low\n"
        "  check_low:\n"
        "    // ch >= 'a'; if ch > 'z' -> unchanged; else lower\n"
        "    bit.cmp 8, ch, z_lower, lower, lower, print_unchanged\n"
        "  lower:\n"
        "    // ch in a..z; output (ch - 32) by toggling bit 5 (0x20)\n"
        "    bit.not ch + 5*dw\n"
        "    bit.print ch\n"
        "    bit.not ch + 5*dw\n"
        "    ;loop\n"
        "  print_unchanged:\n"
        "    bit.print ch\n"
        "    ;loop\n"
        "  end:\n"
        "    stl.loop\n"
        "}\n\n"
        "ch: bit.vec 8, 0\n"
        "a_lower: bit.vec 8, 'a'\n"
        "z_lower: bit.vec 8, 'z'\n"
    ),
    b"Hello, World!\n\0",
    b"HELLO, WORLD!\n",
)

# 28. lowercase_filter — for each byte, if A-Z output (byte + 32) else as-is.
io_simple(
    "lowercase_filter",
    "0028",
    "Lowercase Filter",
    "Reads stdin and prints each byte lowercased (A-Z -> a-z; others unchanged).",
    (
        "main\n\n"
        "def main @ loop, check_low, upper, print_unchanged, end < ch, a_upper, z_upper {\n"
        "    stl.startup\n"
        "  loop:\n"
        "    bit.input ch\n"
        "    bit.if0 8, ch, end\n"
        "    bit.cmp 8, ch, a_upper, print_unchanged, check_low, check_low\n"
        "  check_low:\n"
        "    bit.cmp 8, ch, z_upper, upper, upper, print_unchanged\n"
        "  upper:\n"
        "    // ch in A..Z; output (ch + 32) by toggling bit 5 (0x20)\n"
        "    bit.not ch + 5*dw\n"
        "    bit.print ch\n"
        "    bit.not ch + 5*dw\n"
        "    ;loop\n"
        "  print_unchanged:\n"
        "    bit.print ch\n"
        "    ;loop\n"
        "  end:\n"
        "    stl.loop\n"
        "}\n\n"
        "ch: bit.vec 8, 0\n"
        "a_upper: bit.vec 8, 'A'\n"
        "z_upper: bit.vec 8, 'Z'\n"
    ),
    b"Hello, World!\n\0",
    b"hello, world!\n",
)

print("---")
print("BATCH 1 DONE")

from __future__ import annotations

import json
from enum import IntEnum    # IntEnum equality works between files.
from pathlib import Path
from time import time
from typing import List, Tuple

from ops import CodePosition, Op, MacroName
from expr import Expr

id_re = r'[a-zA-Z_][a-zA-Z_0-9]*'
dot_id_re = fr'(({id_re})|\.*)?(\.({id_re}))+'

bin_num = r'0[bB][01]+'
hex_num = r'0[xX][0-9a-fA-F]+'
dec_num = r'[0-9]+'

char_escape_dict = {'0': 0x0, 'a': 0x7, 'b': 0x8, 'e': 0x1b, 'f': 0xc, 'n': 0xa, 'r': 0xd, 't': 0x9, 'v': 0xb,
                    '\\': 0x5c, "'": 0x27, '"': 0x22, '?': 0x3f}
escape_chars = ''.join(k for k in char_escape_dict)
char = fr'[ -~]|\\[{escape_chars}]|\\[xX][0-9a-fA-F]{{2}}'

number_re = fr"({bin_num})|({hex_num})|('({char})')|({dec_num})"
string_re = fr'"({char})*"'

wflip_start_label = '_.wflip_area_start_'


def next_address() -> Expr:
    return Expr('$')


def get_char_value_and_length(s: str) -> Tuple[int, int]:
    if s[0] != '\\':
        return ord(s[0]), 1
    if s[1] in char_escape_dict:
        return char_escape_dict[s[1]], 2
    return int(s[2:4], 16), 4


def get_stl_paths() -> List[Path]:
    stl_path = Path(__file__).parent.parent / 'stl'
    with open(stl_path / 'conf.json', 'r') as stl_json:
        stl_options = json.load(stl_json)
    return [stl_path / f'{lib}.fj' for lib in stl_options['all']]


class TerminationCause(IntEnum):
    Looping = 0
    EOF = 1
    NullIP = 2

    def __str__(self) -> str:
        return ['looping', 'EOF', 'ip<2w'][self.value]


class SegmentEntry(IntEnum):
    StartAddress = 0
    ReserveAddress = 1
    WflipAddress = 2


BoundaryAddressesList = List[Tuple[SegmentEntry, int]]


macro_separator_string = "---"

bytes_encoding = 'raw_unicode_escape'


def get_nice_label_repr(label: str, pad: int = 0) -> str:
    parts = label.split(macro_separator_string)
    return ' ->\n'.join(f"{' '*(pad+i)}{part}" for i, part in enumerate(parts))


class PrintTimer:
    def __init__(self, init_message: str, *, print_time: bool = True):
        self.init_message = init_message
        self.print_time = print_time

    def __enter__(self) -> None:
        if self.print_time:
            self.start_time = time()
            print(self.init_message, end='', flush=True)

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.print_time:
            print(f'{time() - self.start_time:.3f}s')


class Macro:
    # [(params, quiet_params), statements, (curr_file, p.lineno, ns_name)]

    def __init__(self, params: List[str], local_params: List[str],
                 ops: List[Op], namespace: str,
                 code_position: CodePosition):
        self.params = params
        self.local_params = local_params
        self.ops = ops
        self.namespace = namespace
        self.code_position = code_position


main_macro = MacroName('')

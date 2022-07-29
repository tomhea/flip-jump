from __future__ import annotations

import dataclasses
import json
from enum import IntEnum    # IntEnum equality works between files.
from pathlib import Path
from time import time
from typing import List

from ops import CodePosition, Op


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


macro_separator_string = "---"

bytes_encoding = 'raw_unicode_escape'


class PrintTimer:
    """
    prints the time a code segment took.
    usage:
    with PrintTimer('long_function time: '):
        long_function()
    """
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


@dataclasses.dataclass
class Macro:
    """
    The python representation of a .fj macro.
    """
    params: List[str]
    local_params: List[str]
    ops: List[Op]
    namespace: str
    code_position: CodePosition

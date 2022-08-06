from __future__ import annotations

import dataclasses
import json
from enum import IntEnum    # IntEnum equality works between files.
from pathlib import Path
from time import time
from typing import List

from ops import CodePosition, Op


def get_stl_paths() -> List[Path]:
    """
    @return: list of the ordered standard-library paths
    """
    stl_path = Path(__file__).parent.parent / 'stl'
    with open(stl_path / 'conf.json', 'r') as stl_json:
        stl_options = json.load(stl_json)
    return [stl_path / f'{lib}.fj' for lib in stl_options['all']]


class TerminationCause(IntEnum):
    Looping = 0         # Finished by jumping to the last op, without flipping it (the "regular" finish/exit)
    EOF = 1             # Finished by reading input when there is no more input
    NullIP = 2          # Finished by jumping back to the initial op 0 (bad finish)
    UnalignedWord = 3   # FOR FUTURE SUPPORT - tried to access an unaligned word (bad finish)
    UnalignedOp = 4     # FOR FUTURE SUPPORT - tried to access a dword-unaligned op (bad finish)

    def __str__(self) -> str:
        return ['looping', 'EOF', 'ip<2w', 'unaligned-word', 'unaligned-op'][self.value]


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


class RunStatistics:
    """
    maintains times and counters of the current run.
    """
    class PauseTimer:
        def __init__(self):
            self.paused_time = 0

        def __enter__(self):
            self.pause_start_time = time()

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.paused_time += time() - self.pause_start_time

    def __init__(self, w: int):
        self._op_size = 2 * w
        self._after_null_flip = 2 * w

        self.op_counter = 0
        self.flip_counter = 0
        self.jump_counter = 0

        self._start_time = time()
        self.pause_timer = self.PauseTimer()

    def get_run_time(self) -> float:
        return time() - self._start_time - self.pause_timer.paused_time

    def register_op(self, ip: int, flip_address: int, jump_address: int) -> None:
        self.op_counter += 1
        if flip_address >= self._after_null_flip:
            self.flip_counter += 1
        if jump_address != ip + self._op_size:
            self.jump_counter += 1

from pathlib import Path
from time import time
from typing import Optional, Set

import fjm
from defs import TerminationCause, PrintTimer
from breakpoints import BreakpointHandler, handle_breakpoint, get_breakpoint_handler

from io_devices.IODevice import IODevice
from io_devices.BrokenIO import BrokenIO
from io_devices.io_exceptions import IOReadOnEOF


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


class TerminationStatistics:
    """
    saves the run-statistics and data of the fj program-termination, to be presented nicely.
    also saves the program's output.
    """
    def __init__(self, run_statistics: RunStatistics, termination_cause: TerminationCause):
        self.run_time = run_statistics.get_run_time()

        self.op_counter = run_statistics.op_counter
        self.flip_counter = run_statistics.flip_counter
        self.jump_counter = run_statistics.jump_counter

        self.termination_cause = termination_cause

    def __str__(self):
        flips_percentage = self.flip_counter / self.op_counter * 100
        jumps_percentage = self.jump_counter / self.op_counter * 100
        return f'Finished by {self.termination_cause} after {self.run_time:.3f}s ' \
               f'(' \
               f'{self.op_counter:,} ops executed; ' \
               f'{flips_percentage:.2f}% flips, ' \
               f'{jumps_percentage:.2f}% jumps' \
               f').'


def run(fjm_path: Path, *,
        breakpoint_handler: Optional[BreakpointHandler] = None,
        io_device: Optional[IODevice] = None,
        show_trace: bool = False,
        time_verbose: bool = False) \
        -> TerminationStatistics:
    """
    run / debug a .fjm file (a FlipJump interpreter)
    @param fjm_path: the path to the .fjm file
    @param breakpoint_handler:[in]: the breakpoint handler (if not None - debug, and break on its breakpoints)
    @param io_device:[in,out]: the device handling input/output
    @param show_trace: if true print every opcode executed
    @param time_verbose: if true print running times
    @return: the run's termination-statistics
    """
    with PrintTimer('  loading memory:  ', print_time=time_verbose):
        mem = fjm.Reader(fjm_path)

    if io_device is None:
        io_device = BrokenIO()

    ip = 0
    w = mem.w

    statistics = RunStatistics(w)

    while True:
        # handle breakpoints
        if breakpoint_handler and breakpoint_handler.should_break(ip, statistics.op_counter):
            breakpoint_handler = handle_breakpoint(breakpoint_handler, ip, mem, statistics)

        # read flip word
        flip_address = mem.get_word(ip)
        trace_flip(ip, flip_address, show_trace)

        # handle IO
        handle_output(flip_address, io_device, w)
        try:
            handle_input(io_device, ip, mem, statistics)
        except IOReadOnEOF:
            return TerminationStatistics(statistics, TerminationCause.EOF)

        # FLIP!
        mem.write_bit(flip_address, 1-mem.read_bit(flip_address))

        # read jump word
        jump_address = mem.get_word(ip+w)
        trace_jump(jump_address, show_trace)
        statistics.register_op(ip, flip_address, jump_address)

        # check finish?
        if jump_address == ip and not ip <= flip_address < ip+2*w:
            return TerminationStatistics(statistics, TerminationCause.Looping)
        if jump_address < 2*w:
            return TerminationStatistics(statistics, TerminationCause.NullIP)

        # JUMP!
        ip = jump_address


def handle_input(io_device: IODevice, ip: int, mem: fjm.Reader, statistics: RunStatistics) -> None:
    w = mem.w
    in_addr = 3 * w + w.bit_length()  # 3w + dww

    if ip <= in_addr < ip + 2 * w:
        with statistics.pause_timer:
            input_bit = io_device.read_bit()
        mem.write_bit(in_addr, input_bit)


def handle_output(flip_address: int, io_device: IODevice, w: int):
    out_addr = 2 * w
    if out_addr <= flip_address <= out_addr + 1:
        io_device.write_bit(out_addr + 1 == flip_address)


def trace_jump(jump_address: int, show_trace: bool) -> None:
    if show_trace:
        print(hex(jump_address)[2:])


def trace_flip(ip: int, flip_address: int, show_trace: bool) -> None:
    if show_trace:
        print(hex(ip)[2:].rjust(7), end=':   ')
        print(hex(flip_address)[2:], end='; ', flush=True)

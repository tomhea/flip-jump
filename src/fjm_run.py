from pathlib import Path
from time import time
from sys import stdin, stdout
from typing import Optional, Set

import fjm
from defs import Verbose, TerminationCause, PrintTimer
from breakpoints import BreakpointHandler, handle_breakpoint, get_breakpoint_handler


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
    def __init__(self, run_statistics: RunStatistics, standard_output: bytes, termination_cause: TerminationCause):
        self.run_time = run_statistics.get_run_time()

        self.op_counter = run_statistics.op_counter
        self.flip_counter = run_statistics.flip_counter
        self.jump_counter = run_statistics.jump_counter

        self.standard_output = standard_output
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
        defined_input: Optional[bytes] = None,
        show_trace: bool = False,
        time_verbose: bool = False,
        output_verbose: bool = True) \
        -> TerminationStatistics:
    """
    run a .fjm file (a FlipJump interpreter)
    @param fjm_path: the path to the .fjm file
    @param breakpoint_handler: the breakpoint handler
    @param defined_input: fixed-input, or None for stdin
    @param show_trace: if true print every opcode executed
    @param time_verbose: if true print running times
    @param output_verbose: if true print program's output
    @return: the run's termination-statistics
    """
    with PrintTimer('  loading memory:  ', print_time=time_verbose):
        mem = fjm.Reader(fjm_path)

    ip = 0
    w = mem.w
    out_addr = 2*w
    in_addr = 3*w + w.bit_length()     # 3w + dww

    input_char, input_size = 0, 0
    output_char, output_size = 0, 0
    output = bytes()

    output_anything_yet = False

    statistics = RunStatistics(w)

    while True:
        if breakpoint_handler and breakpoint_handler.should_break(ip, statistics.op_counter):
            breakpoint_handler = handle_breakpoint(breakpoint_handler, ip, mem, statistics)

        flip_address = mem.get_word(ip)

        trace_flip(ip, flip_address, show_trace)

        # handle output
        if out_addr <= flip_address <= out_addr+1:
            output_char |= (flip_address-out_addr) << output_size
            output_byte = bytes([output_char])
            output_size += 1
            if output_size == 8:
                output += output_byte
                if output_verbose:
                    if show_trace:
                        for _ in range(3):
                            print()
                        print(f'Outputted Char:  ', end='')
                        stdout.buffer.write(bytes([output_char]))
                        stdout.flush()
                        for _ in range(3):
                            print()
                    else:
                        stdout.buffer.write(bytes([output_char]))
                        stdout.flush()
                output_anything_yet = True
                output_char, output_size = 0, 0

        # handle input
        if ip <= in_addr < ip+2*w:
            if input_size == 0:
                if defined_input is None:
                    with statistics.pause_timer:
                        input_char = stdin.buffer.read(1)[0]
                elif len(defined_input) > 0:
                    input_char = defined_input[0]
                    defined_input = defined_input[1:]
                else:
                    if output_verbose and output_anything_yet:
                        print()
                    # Reading a null input byte
                    return TerminationStatistics(statistics, output, TerminationCause.Input)
                input_size = 8
            mem.write_bit(in_addr, input_char & 1)
            input_char = input_char >> 1
            input_size -= 1

        mem.write_bit(flip_address, 1-mem.read_bit(flip_address))     # Flip!

        jump_address = mem.get_word(ip+w)

        statistics.register_op(ip, flip_address, jump_address)

        trace_jump(jump_address, show_trace)

        if jump_address == ip and not ip <= flip_address < ip+2*w:
            if output_verbose and output_anything_yet and breakpoint_handler:
                print()
            return TerminationStatistics(statistics, output, TerminationCause.Looping)          # infinite simple loop
        if jump_address < 2*w:
            if output_verbose and output_anything_yet and breakpoint_handler:
                print()
            return TerminationStatistics(statistics, output, TerminationCause.NullIP)           # null ip

        ip = jump_address     # Jump!


def trace_jump(jump_address: int, show_trace: bool) -> None:
    if show_trace:
        print(hex(jump_address)[2:])


def trace_flip(ip: int, flip_address: int, show_trace: bool) -> None:
    if show_trace:
        print(hex(ip)[2:].rjust(7), end=':   ')
        print(hex(flip_address)[2:], end='; ', flush=True)


def debug_and_run(fjm_path: Path,
                  verbose: Set[Verbose],
                  debugging_file: Path = None,
                  defined_input: Optional[bytes] = None,
                  breakpoint_addresses: Optional[Set[int]] = None,
                  breakpoint_labels: Optional[Set[str]] = None,
                  breakpoint_contains_labels: Optional[Set[str]] = None) \
        -> TerminationStatistics:
    """
    run a .fjm file with a breakpoint_handler (a FlipJump interpreter & debugger)
    @param fjm_path: the path to the .fjm file
    @param verbose: the verbose option set (out of Run,Time,PrintOutput)
    @param debugging_file: the debug file path (created at assemble time)
    @param defined_input: fixed-input, or None for stdin
    @param breakpoint_addresses: set of addresses to break at
    @param breakpoint_labels: set of labels to break at
    @param breakpoint_contains_labels: set of strings, to break at every label that contains one of them
    @return: the run's termination-statistics
    """
    breakpoint_handler = get_breakpoint_handler(
        debugging_file, breakpoint_addresses, breakpoint_labels, breakpoint_contains_labels)

    termination_statistics = run(
        fjm_path, defined_input=defined_input,
        show_trace=Verbose.Run in verbose,
        time_verbose=Verbose.Time in verbose,
        output_verbose=Verbose.PrintOutput in verbose,
        breakpoint_handler=breakpoint_handler)

    return termination_statistics

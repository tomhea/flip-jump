from pathlib import Path
from typing import Optional, Deque

import fjm

from defs import TerminationCause, PrintTimer, RunStatistics
from breakpoints import BreakpointHandler, handle_breakpoint
from exceptions import FJRuntimeMemoryException

from io_devices.IODevice import IODevice
from io_devices.BrokenIO import BrokenIO
from io_devices.io_exceptions import IOReadOnEOF


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
        self.last_ops_addresses: Deque[int] = run_statistics.last_ops_addresses

        self.termination_cause = termination_cause

    @staticmethod
    def beautify_address(address: int, breakpoint_handler: Optional[BreakpointHandler]):
        if not breakpoint_handler:
            return hex(address)

        return breakpoint_handler.get_address_str(address)

    def print(self, *, labels_handler: Optional[BreakpointHandler] = None, output_to_print: Optional[bytes] = None):
        """
        Prints the termination cause, run times, ops-statistics.
        If ended not by looping - Then print the last-opcodes` addresses as well (and their label names if possible).
        @param labels_handler: Used to find the label name for each address (from the last-opcodes` addresses).
        @param output_to_print: if specified and terminated not by looping - print the given output.
        """

        flips_percentage = self.flip_counter / self.op_counter * 100
        jumps_percentage = self.jump_counter / self.op_counter * 100

        last_ops_str = ''
        output_str = ''
        if TerminationCause.Looping != self.termination_cause:
            last_ops_str = f'\n\nLast {len(self.last_ops_addresses)} ops were at these addresses ' \
                           f'(The most-recent op, the one that failed, is first):\n  ' + \
                           '\n  '.join([self.beautify_address(address, labels_handler)
                                        for address in self.last_ops_addresses][::-1])
            if output_to_print is not None:
                output_str = f"Program's output before it was terminated:  {output_to_print}\n\n"

        print(f'\n'
              f'{output_str}'
              f'Finished by {str(self.termination_cause)} after {self.run_time:.3f}s '
              f'('
              f'{self.op_counter:,} ops executed; '
              f'{flips_percentage:.2f}% flips, '
              f'{jumps_percentage:.2f}% jumps'
              f').'
              f'{last_ops_str}'
              )


def handle_input(io_device: IODevice, ip: int, mem: fjm.Reader, statistics: RunStatistics) -> None:
    w = mem.w
    in_addr = 3 * w + w.bit_length()  # 3w + #w

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

    try:
        while True:
            statistics.register_op_address(ip)

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
            mem.write_bit(flip_address, not mem.read_bit(flip_address))

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

    except FJRuntimeMemoryException:
        return TerminationStatistics(statistics, TerminationCause.RuntimeMemoryError)

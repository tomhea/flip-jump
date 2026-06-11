"""
the flipjump interpreter.
executes a compiled .fjm program one flip-jump op at a time - managing the memory,
routing input/output through an IODevice, handling breakpoints, detecting termination,
and collecting run statistics (returned as TerminationStatistics).

two run-loops are implemented:
- the fast loop (the default): the memory accesses and IO/termination checks are inlined,
  and the per-op statistics (flip/jump counters) are skipped. ~20x faster.
- the featured loop: supports breakpoints, tracing, and full statistics. selected when
  debugging features are requested, or explicitly with profile=True.
"""

from pathlib import Path
from typing import Optional, Deque

from flipjump.fjm import fjm_reader
from flipjump.interpretter.debugging.breakpoints import BreakpointHandler, handle_breakpoint
from flipjump.utils.classes import TerminationCause, PrintTimer, RunStatistics
from flipjump.utils.exceptions import (
    FlipJumpRuntimeMemoryException,
    IOReadOnEOF,
    FlipJumpException,
    FlipJumpRuntimeException,
)
from flipjump.interpretter.io_devices.BrokenIO import BrokenIO
from flipjump.interpretter.io_devices.IODevice import IODevice


class TerminationStatistics:
    """
    saves the run-statistics and data of the fj program-termination, to be presented nicely.
    also saves the program's output.
    """

    def __init__(
        self,
        run_statistics: RunStatistics,
        termination_cause: TerminationCause,
        *,
        memory_error_address: Optional[int] = None,
    ) -> None:
        self.run_time = run_statistics.get_run_time()

        self.op_counter = run_statistics.op_counter
        self.flip_counter = run_statistics.flip_counter
        self.jump_counter = run_statistics.jump_counter
        self.detailed_statistics = run_statistics.detailed_statistics
        self.last_ops_addresses: Optional[Deque[int]] = run_statistics.last_ops_addresses

        self.termination_cause = termination_cause
        self.memory_error_address = memory_error_address

    @staticmethod
    def beautify_address(address: int, breakpoint_handler: Optional[BreakpointHandler]) -> str:
        if not breakpoint_handler:
            return hex(address)

        return breakpoint_handler.get_address_str(address)

    def print(
        self, *, labels_handler: Optional[BreakpointHandler] = None, output_to_print: Optional[bytes] = None
    ) -> None:
        """
        Prints the termination cause, run times, ops-statistics.
        If ended not by looping - Then print the last-opcodes` addresses as well (and their label names if possible).
        @param labels_handler: Used to find the label name for each address (from the last-opcodes` addresses).
        @param output_to_print: if specified and terminated not by looping - print the given output.
        """

        flips_jumps_str = ''
        if self.detailed_statistics and self.op_counter:
            flips_percentage = self.flip_counter / self.op_counter * 100
            jumps_percentage = self.jump_counter / self.op_counter * 100
            flips_jumps_str = f'; {flips_percentage:.2f}% flips, {jumps_percentage:.2f}% jumps'

        last_ops_str = ''
        output_str = ''
        if TerminationCause.Looping != self.termination_cause:
            if self.last_ops_addresses is not None:
                labels_handler_missing_string = (
                    ''
                    if labels_handler is not None and labels_handler.address_to_label
                    else '**** You may want to use debugging flags for more debugging info ****\n\n'
                )
                last_ops_str = (
                    f'\n\n{labels_handler_missing_string}'
                    f'Last {len(self.last_ops_addresses)} ops were at these addresses '
                    f'(The most-recent op, the one that failed, is first):\n  '
                    + '\n  '.join(
                        [self.beautify_address(address, labels_handler) for address in self.last_ops_addresses][::-1]
                    )
                )
            if output_to_print is not None:
                output_str = f"Program's output before it was terminated:  {output_to_print!r}\n\n"

        termination_cause_str = str(self.termination_cause)
        if self.memory_error_address is not None:
            termination_cause_str += f" (address {hex(self.memory_error_address)})"
        print(
            f'\n'
            f'{output_str}'
            f'Finished by {termination_cause_str} after {self.run_time:.3f}s '
            f'('
            f'{self.op_counter:,} ops executed'
            f'{flips_jumps_str}'
            f').'
            f'{last_ops_str}'
        )


def _handle_input(io_device: IODevice, ip: int, mem: fjm_reader.Reader, statistics: RunStatistics) -> None:
    """
    if the ip is in the input-bit range, read a bit from the io_device into the memory.
    """
    w = mem.memory_width
    in_addr = 3 * w + w.bit_length()  # 3w + #w

    if ip <= in_addr < ip + 2 * w:
        with statistics.pause_timer:
            input_bit = io_device.read_bit()
        mem.write_bit(in_addr, input_bit)


def _handle_output(flip_address: int, io_device: IODevice, w: int) -> None:
    """
    if the ip is in the output-bit range, output the corresponding bit to the io_device.
    """
    out_addr = 2 * w
    if out_addr <= flip_address <= out_addr + 1:
        io_device.write_bit(out_addr + 1 == flip_address)


def _trace_jump(jump_address: int, show_trace: bool) -> None:
    """
    if show_trace is enabled, print the current jump-address.
    """
    if show_trace:
        print(hex(jump_address)[2:])


def _trace_flip(ip: int, flip_address: int, show_trace: bool) -> None:
    """
    if show_trace is enabled, print the current ip-address and flip-address.
    """
    if show_trace:
        print(hex(ip)[2:].rjust(7), end=':   ')
        print(hex(flip_address)[2:], end='; ', flush=True)


def run(
    fjm_path: Path,
    *,
    breakpoint_handler: Optional[BreakpointHandler] = None,
    io_device: Optional[IODevice] = None,
    show_trace: bool = False,
    print_time: bool = False,
    last_ops_debugging_list_length: Optional[int] = None,
    profile: bool = False,
) -> TerminationStatistics:
    """
    run / debug a .fjm file (a FlipJump interpreter)
    @param fjm_path: the path to the .fjm file
    @param breakpoint_handler:[in]: the breakpoint handler (if not None - debug, and break on its breakpoints)
    @param io_device:[in,out]: the device handling input/output
    @param show_trace: if true print every opcode executed
    @param print_time: if true print running times
    @param last_ops_debugging_list_length: The length of the last-ops list
    @param profile: if true use the featured loop and collect the full per-op statistics
    (flip/jump counters). by default the fast loop is used (which skips them).
    @return: the run's termination-statistics
    """
    with PrintTimer('  loading memory:  ', print_time=print_time):
        mem = fjm_reader.Reader(fjm_path)

    if io_device is None:
        io_device = BrokenIO()

    statistics = RunStatistics(mem.memory_width, last_ops_debugging_list_length)

    try:
        if profile or show_trace or breakpoint_handler is not None:
            return _run_featured(mem, io_device, statistics, breakpoint_handler, show_trace)
        return _run_fast(mem, io_device, statistics)

    except FlipJumpRuntimeMemoryException as mem_e:
        return TerminationStatistics(
            statistics, TerminationCause.RuntimeMemoryError, memory_error_address=mem_e.memory_address
        )
    except FlipJumpException as fj_exception:
        raise fj_exception
    except KeyboardInterrupt:
        return TerminationStatistics(statistics, TerminationCause.KeyboardInterrupt)
    except Exception as unknown_exception:
        raise FlipJumpRuntimeException(
            "Unknown exception during running an .fjm file, please report this bug"
        ) from unknown_exception


def _run_featured(
    mem: fjm_reader.Reader,
    io_device: IODevice,
    statistics: RunStatistics,
    breakpoint_handler: Optional[BreakpointHandler],
    show_trace: bool,
) -> TerminationStatistics:
    """
    the featured run-loop: supports breakpoints and tracing, and collects the full
    per-op statistics (the flip/jump counters and the last-ops debugging list).
    """
    ip = 0
    w = mem.memory_width

    while True:
        statistics.register_op_address(ip)

        # handle breakpoints
        if breakpoint_handler and breakpoint_handler.should_break(ip, statistics.op_counter):
            breakpoint_handler = handle_breakpoint(breakpoint_handler, ip, mem, statistics)

        # read flip word
        flip_address = mem.get_word(ip)
        _trace_flip(ip, flip_address, show_trace)

        # handle IO
        _handle_output(flip_address, io_device, w)
        try:
            _handle_input(io_device, ip, mem, statistics)
        except IOReadOnEOF:
            return TerminationStatistics(statistics, TerminationCause.EOF)

        # FLIP!
        mem.write_bit(flip_address, not mem.read_bit(flip_address))

        # read jump word
        jump_address = mem.get_word(ip + w)
        _trace_jump(jump_address, show_trace)
        statistics.register_op(ip, flip_address, jump_address)

        # check finish?
        if jump_address == ip and not ip <= flip_address < ip + 2 * w:
            return TerminationStatistics(statistics, TerminationCause.Looping)
        if jump_address < 2 * w:
            return TerminationStatistics(statistics, TerminationCause.NullIP)

        # JUMP!
        ip = jump_address


def _run_fast(  # noqa: C901
    mem: fjm_reader.Reader, io_device: IODevice, statistics: RunStatistics
) -> TerminationStatistics:
    """
    the fast run-loop. behaves exactly like the featured loop, but the memory accesses and
    the IO/termination checks are inlined into the loop, and the per-op flip/jump counters
    are skipped (op_counter is still maintained).
    the loop body is duplicated: with and without last-ops tracking (tracking costs ~10%).
    """
    memory = mem.memory
    w = mem.memory_width
    ww = w.bit_length() - 1  # log2(w)
    dw = 2 * w
    bit_mask = w - 1
    in_addr = 3 * w + w.bit_length()  # 3w + #w
    in_lo = in_addr - dw  # the input bit is in the current op iff in_lo < ip <= in_addr
    out1 = dw + 1  # the output bits are dw, dw+1

    get_word = mem.get_word
    read_missing_word = mem._get_memory_word
    write_bit = mem.write_bit
    io_write_bit = io_device.write_bit
    io_read_bit = io_device.read_bit
    pause_timer = statistics.pause_timer

    last_ops = statistics.last_ops_addresses
    append_last_op = last_ops.append if last_ops is not None else None

    statistics.detailed_statistics = False
    ip = 0
    ops = 0
    try:
        while True:
            if append_last_op is not None:
                append_last_op(ip)

            # read flip word
            bit_offset = ip & bit_mask
            if bit_offset:
                flip_address = get_word(ip)
            else:
                word_address = ip >> ww
                try:
                    flip_address = memory[word_address]
                except KeyError:
                    flip_address = read_missing_word(word_address)

            # handle IO (both checks fail after a single comparison for almost all ops)
            if flip_address <= out1:
                if flip_address >= dw:
                    io_write_bit(out1 == flip_address)
            if ip <= in_addr and ip > in_lo:
                try:
                    with pause_timer:
                        input_bit = io_read_bit()
                except IOReadOnEOF:
                    statistics.op_counter = ops
                    return TerminationStatistics(statistics, TerminationCause.EOF)
                write_bit(in_addr, input_bit)

            # FLIP!
            flip_word_address = flip_address >> ww
            try:
                flip_word_value = memory[flip_word_address]
            except KeyError:
                flip_word_value = read_missing_word(flip_word_address)
            memory[flip_word_address] = flip_word_value ^ (1 << (flip_address & bit_mask))

            # read jump word (after the flip - the flip may modify it)
            if bit_offset:
                jump_address = get_word(ip + w)
            else:
                jump_word_address = (ip >> ww) + 1
                try:
                    jump_address = memory[jump_word_address]
                except KeyError:
                    jump_address = read_missing_word(jump_word_address)
            ops += 1

            # check finish?
            if jump_address == ip and not ip <= flip_address < ip + dw:
                statistics.op_counter = ops
                return TerminationStatistics(statistics, TerminationCause.Looping)
            if jump_address < dw:
                statistics.op_counter = ops
                return TerminationStatistics(statistics, TerminationCause.NullIP)

            # JUMP!
            ip = jump_address
    finally:
        # keep op_counter valid on the exception paths too (memory errors, Ctrl+C)
        statistics.op_counter = ops

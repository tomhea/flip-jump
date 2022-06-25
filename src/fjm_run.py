import pickle
from os import path
from pathlib import Path
from time import time
from sys import stdin, stdout
from typing import Optional, List, Dict, Set

import easygui

import fjm
from defs import Verbose, TerminationCause, PrintTimer


class BreakpointHandlerUnnecessary(Exception):
    pass


def display_message_box_and_get_answer(msg: str, title: str, choices: List[str]) -> str:
    # TODO deprecated warning. use another gui (tkinter? seems not so simple)
    return easygui.buttonbox(msg, title, choices)


class BreakpointHandler:
    def __init__(self, breakpoints: Set[int], address_to_label: Dict[int, str]):
        self.breakpoints = breakpoints
        self.address_to_label = address_to_label

        if 0 not in self.address_to_label:
            self.address_to_label[0] = 'memory_start_0x0000'

        self.next_break = None

    def should_break(self, ip: int, op_counter: int) -> bool:
        return self.next_break == op_counter or ip in self.breakpoints

    def get_address_str(self, address: int):
        if address in self.address_to_label:
            return f'{hex(address)[2:]} ({self.address_to_label[address]})'
        elif address in self.breakpoints:
            return hex(address)
        else:
            address_before = max([a for a in self.address_to_label if a <= address])
            return f'{hex(address)[2:]} ({self.address_to_label[address_before]} + {hex(address - address_before)})'

    def get_message_box_body(self, ip: int, mem: fjm.Reader, op_counter: int):
        address = self.get_address_str(ip)
        flip = self.get_address_str(mem.get_word(ip))
        jump = self.get_address_str(mem.get_word(ip + mem.w))
        return f'Address {address}  ({op_counter} ops executed):\n  flip: {flip}.\n  jump: {jump}.'

    def query_user_for_debug_action(self, ip: int, mem: fjm.Reader, op_counter: int):
        title = "Breakpoint" if ip in self.breakpoints else "Debug Step"
        body = self.get_message_box_body(ip, mem, op_counter)
        actions = ['Single Step', 'Skip 10', 'Skip 100', 'Skip 1000', 'Continue', 'Continue All']

        action = display_message_box_and_get_answer(body, title, actions)
        if action is None:
            action = 'Continue All'
        return action

    def apply_debug_action(self, action: str, op_counter: int):
        if action == 'Single Step':
            self.next_break = op_counter + 1
        elif action == 'Skip 10':
            self.next_break = op_counter + 10
        elif action == 'Skip 100':
            self.next_break = op_counter + 100
        elif action == 'Skip 1000':
            self.next_break = op_counter + 1000
        elif action == 'Continue':
            self.next_break = None
        elif action == 'Continue All':
            self.next_break = None
            raise BreakpointHandlerUnnecessary()


class RunStatistics:
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
        verbose: bool = False,
        time_verbose: bool = False,
        output_verbose: bool = False):

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
        if verbose:
            print(f'{hex(ip)[2:].rjust(7)}:   {hex(flip_address)[2:]}', end='; ', flush=True)

        # handle output
        if out_addr <= flip_address <= out_addr+1:
            output_char |= (flip_address-out_addr) << output_size
            output_byte = bytes([output_char])
            output_size += 1
            if output_size == 8:
                output += output_byte
                if output_verbose:
                    if verbose:
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
                    return TerminationStatistics(statistics, output, TerminationCause.Input)    # Reading a null input byte
                input_size = 8
            mem.write_bit(in_addr, input_char & 1)
            input_char = input_char >> 1
            input_size -= 1

        mem.write_bit(flip_address, 1-mem.read_bit(flip_address))     # Flip!

        jump_address = mem.get_word(ip+w)

        statistics.register_op(ip, flip_address, jump_address)

        if verbose:
            print(hex(jump_address)[2:])

        if jump_address == ip and not ip <= flip_address < ip+2*w:
            if output_verbose and output_anything_yet and breakpoint_handler:
                print()
            return TerminationStatistics(statistics, output, TerminationCause.Looping)          # infinite simple loop
        if jump_address < 2*w:
            if output_verbose and output_anything_yet and breakpoint_handler:
                print()
            return TerminationStatistics(statistics, output, TerminationCause.NullIP)           # null ip

        ip = jump_address     # Jump!


def handle_breakpoint(breakpoint_handler, ip, mem, statistics):
    print('  program break', end="", flush=True)
    with statistics.pause_timer:
        action = breakpoint_handler.query_user_for_debug_action(ip, mem, statistics.op_counter)
    print(f': {action}')

    try:
        breakpoint_handler.apply_debug_action(action, statistics.op_counter)
    except BreakpointHandlerUnnecessary:
        breakpoint_handler = None

    return breakpoint_handler


def get_breakpoints(breakpoint_addresses: Optional[Set[int]],
                    breakpoint_labels: Optional[Set[str]],
                    breakpoint_any_labels: Optional[Set[str]],
                    label_to_address: Dict[str, int]):
    breakpoints = set(breakpoint_addresses) if breakpoint_labels else set()

    if breakpoint_labels is not None:
        for bl in breakpoint_labels:
            if bl not in label_to_address:
                print(f"Warning:  Breakpoint label {bl} can't be found!")
            else:
                breakpoints.add(label_to_address[bl])

    # TODO improve the speed of this part with suffix trees
    if breakpoint_any_labels is not None:
        for bal in breakpoint_any_labels:
            for label in label_to_address:
                if bal in label:
                    breakpoints.add(label_to_address[label])

    return breakpoints


def load_labels_dictionary(debugging_file, labels_file_needed):
    label_to_address = []
    if debugging_file is not None:
        if path.isfile(debugging_file):
            with open(debugging_file, 'rb') as f:
                label_to_address = pickle.load(f)
        else:
            print(f"Warning:  debugging file {debugging_file} can't be found!")
    elif labels_file_needed:
        print(f"Warning:  debugging labels can't be found! no debugging file specified.")
    return label_to_address


def debug_and_run(input_file, debugging_file=None,
                  defined_input: Optional[bytes] = None, verbose=None,
                  breakpoint_addresses=None, breakpoint_labels=None, breakpoint_any_labels=None) -> TerminationStatistics:
    if verbose is None:
        verbose = set()

    labels_file_needed = breakpoint_addresses or breakpoint_any_labels
    label_to_address = load_labels_dictionary(debugging_file, labels_file_needed)

    address_to_label = {label_to_address[label]: label for label in label_to_address}
    breakpoints = get_breakpoints(breakpoint_addresses, breakpoint_labels, breakpoint_any_labels, label_to_address)

    breakpoint_handler = BreakpointHandler(breakpoints, address_to_label) if breakpoints else None

    termination_statistics = run(
        input_file, defined_input=defined_input,
        verbose=Verbose.Run in verbose,
        time_verbose=Verbose.Time in verbose,
        output_verbose=Verbose.PrintOutput in verbose,
        breakpoint_handler=breakpoint_handler)

    return termination_statistics

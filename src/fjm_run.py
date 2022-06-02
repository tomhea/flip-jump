from typing import Optional

import fjm

from os import path
from sys import stdin, stdout
from time import time
import pickle
import easygui

from defs import *


def get_address_str(address, breakpoints, labels_dict):
    if address in breakpoints:
        return f'{hex(address)[2:]} ({breakpoints[address]})'
    else:
        if address in labels_dict:
            return f'{hex(address)[2:]} ({labels_dict[address]})'
        else:
            address_before = max([a for a in labels_dict if a <= address])
            return f'{hex(address)[2:]} ({labels_dict[address_before]} + {hex(address - address_before)})'


def run(input_file, breakpoints=None, defined_input: Optional[bytes] = None, verbose=False, time_verbose=False, output_verbose=False,
        next_break=None, labels_dict=None):
    if labels_dict is None:
        labels_dict = {}
    if breakpoints is None:
        breakpoints = {}

    if time_verbose:
        print(f'  loading memory:  ', end='', flush=True)
    start_time = time()
    mem = fjm.Reader(input_file)
    if time_verbose:
        print(f'{time() - start_time:.3f}s')

    ip = 0
    w = mem.w
    out_addr = 2*w
    in_addr = 3*w + w.bit_length()     # 3w + dww

    input_char, input_size = 0, 0
    output_char, output_size = 0, 0
    output = bytes()

    if 0 not in labels_dict:
        labels_dict[0] = 'memory_start_0x0000'

    output_anything_yet = False
    ops_executed = 0
    flips_executed = 0

    start_time = time()
    pause_time = 0

    while True:
        if next_break == ops_executed or ip in breakpoints:
            pause_time_start = time()
            title = "Breakpoint" if ip in breakpoints else "Single Step"
            address = get_address_str(ip, breakpoints, labels_dict)
            flip = f'flip: {get_address_str(mem.get_word(ip), breakpoints, labels_dict)}'
            jump = f'jump: {get_address_str(mem.get_word(ip + w), breakpoints, labels_dict)}'
            button_body = f'Address {address}  ({ops_executed} ops executed):\n  {flip}.\n  {jump}.'
            print('  program break', end="")
            action = easygui.buttonbox(button_body, title, ['Single Step', 'Skip 10', 'Skip 100', 'Skip 1000',
                                                            'Continue', 'Continue All'])
            if action is None:
                action = 'Continue All'
            print(f': {action}')
            if action == 'Single Step':
                next_break = ops_executed + 1
            elif action == 'Skip 10':
                next_break = ops_executed + 10
            elif action == 'Skip 100':
                next_break = ops_executed + 100
            elif action == 'Skip 1000':
                next_break = ops_executed + 1000
            elif action == 'Continue':
                next_break = None
            elif action == 'Continue All':
                next_break = None
                breakpoints.clear()
            pause_time += time() - pause_time_start

        f = mem.get_word(ip)
        if verbose:
            print(f'{hex(ip)[2:].rjust(7)}:   {hex(f)[2:]}', end='; ', flush=True)

        ops_executed += 1
        if f >= 2*w:
            flips_executed += 1

        # handle output
        if out_addr <= f <= out_addr+1:
            output_char |= (f-out_addr) << output_size
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
                    pause_time_start = time()
                    input_char = stdin.buffer.read(1)[0]
                    pause_time += time() - pause_time_start
                elif len(defined_input) > 0:
                    input_char = defined_input[0]
                    defined_input = defined_input[1:]
                else:
                    if output_verbose and output_anything_yet:
                        print()
                    run_time = time() - start_time - pause_time
                    return run_time, ops_executed, flips_executed, output, RunFinish.Input  # no more input
                input_size = 8
            mem.write_bit(in_addr, input_char & 1)
            input_char = input_char >> 1
            input_size -= 1

        mem.write_bit(f, 1-mem.read_bit(f))     # Flip!
        new_ip = mem.get_word(ip+w)
        if verbose:
            print(hex(new_ip)[2:])

        if new_ip == ip and not ip <= f < ip+2*w:
            if output_verbose and output_anything_yet and breakpoints:
                print()
            run_time = time()-start_time-pause_time
            return run_time, ops_executed, flips_executed, output, RunFinish.Looping        # infinite simple loop
        if new_ip < 2*w:
            if output_verbose and output_anything_yet and breakpoints:
                print()
            run_time = time() - start_time - pause_time
            return run_time, ops_executed, flips_executed, output, RunFinish.NullIP         # null ip
        ip = new_ip     # Jump!


def debug_and_run(input_file, debugging_file=None,
                  defined_input: Optional[bytes] = None, verbose=None,
                  breakpoint_addresses=None, breakpoint_labels=None, breakpoint_any_labels=None):
    if breakpoint_any_labels is None:
        breakpoint_any_labels = set()
    if breakpoint_labels is None:
        breakpoint_labels = set()
    if breakpoint_addresses is None:
        breakpoint_addresses = set()
    if verbose is None:
        verbose = set()

    labels = []
    if debugging_file is not None:
        if path.isfile(debugging_file):
            with open(debugging_file, 'rb') as f:
                labels = pickle.load(f)
        else:
            print(f"Warning:  debugging file {debugging_file} can't be found!")
    elif breakpoint_labels or breakpoint_addresses or breakpoint_any_labels:
        print(f"Warning:  debugging labels can't be found! no debugging file specified.")

    # Handle breakpoints
    breakpoint_map = {ba: hex(ba) for ba in breakpoint_addresses}
    for bl in breakpoint_labels:
        if bl not in labels:
            print(f"Warning:  Breakpoint label {bl} can't be found!")
        else:
            breakpoint_map[labels[bl]] = bl
    for bal in breakpoint_any_labels:
        for label in labels:
            if bal in label:
                breakpoint_map[labels[label]] = f'{bal}@{label}'

    opposite_labels = {labels[label]: label for label in labels}

    run_time, ops_executed, flips_executed, output, finish_cause = run(
        input_file, defined_input=defined_input,
        verbose=Verbose.Run in verbose,
        time_verbose=Verbose.Time in verbose,
        output_verbose=Verbose.PrintOutput in verbose,
        breakpoints=breakpoint_map, labels_dict=opposite_labels)

    return run_time, ops_executed, flips_executed, output, finish_cause

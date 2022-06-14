import pickle
from os import path
from time import time
from typing import Optional, List
from basicio import BasicIO

import easygui

import fjm
from defs import Verbose, TerminationCause


def display_message_box_and_get_answer(msg: str, title: str, choices: List[str]) -> str:
    # TODO deprecated warning. use another gui (tkinter? seems not so simple)
    return easygui.buttonbox(msg, title, choices)


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
        next_break=None, labels_dict=None, attachedDevices=[]):

    basicIO = BasicIO(defined_input, output_verbose, verbose)
    allDevices = [basicIO] + attachedDevices

    def getDevice(n):
        if not attachedDevices:
            n = 0

        return allDevices[n]

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
    device_addr = 4*w

    if 0 not in labels_dict:
        labels_dict[0] = 'memory_start_0x0000'

    ops_executed = 0
    flips_executed = 0

    pause_time = 0
    start_time = time()

    while True:
        if next_break == ops_executed or ip in breakpoints:
            pause_time_start = time()
            title = "Breakpoint" if ip in breakpoints else "Single Step"
            address = get_address_str(ip, breakpoints, labels_dict)
            flip = f'flip: {get_address_str(mem.get_word(ip), breakpoints, labels_dict)}'
            jump = f'jump: {get_address_str(mem.get_word(ip + w), breakpoints, labels_dict)}'
            body = f'Address {address}  ({ops_executed} ops executed):\n  {flip}.\n  {jump}.'
            actions = ['Single Step', 'Skip 10', 'Skip 100', 'Skip 1000', 'Continue', 'Continue All']
            print('  program break', end="", flush=True)
            action = display_message_box_and_get_answer(body, title, actions)

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
            device = mem.get_word(device_addr)
            getDevice(device).writeBit(f-out_addr)

        # handle input
        if ip <= in_addr < ip+2*w:
            device = mem.get_word(device_addr)
            try:
                mem.write_bit(in_addr, getDevice(device).readBit())
            except BasicIO.NoMoreInputException:
                run_time = time() - start_time - pause_time - basicIO.pause_time
                return run_time, ops_executed, flips_executed, basicIO.output, TerminationCause.Input  # no more input


        mem.write_bit(f, 1-mem.read_bit(f))     # Flip!
        new_ip = mem.get_word(ip+w)
        if verbose:
            print(hex(new_ip)[2:])

        if new_ip == ip and not ip <= f < ip+2*w:
            if output_verbose and basicIO.output_anything_yet and breakpoints:
                print()
            run_time = time() - start_time - pause_time - basicIO.pause_time
            return run_time, ops_executed, flips_executed, basicIO.output, TerminationCause.Looping        # infinite simple loop
        if new_ip < 2*w:
            if output_verbose and basicIO.output_anything_yet and breakpoints:
                print()
            run_time = time() - start_time - pause_time - basicIO.pause_time
            return run_time, ops_executed, flips_executed, basicIO.output, TerminationCause.NullIP         # null ip
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

    run_time, ops_executed, flips_executed, output, termination_cause = run(
        input_file, defined_input=defined_input,
        verbose=Verbose.Run in verbose,
        time_verbose=Verbose.Time in verbose,
        output_verbose=Verbose.PrintOutput in verbose,
        breakpoints=breakpoint_map, labels_dict=opposite_labels)

    return run_time, ops_executed, flips_executed, output, termination_cause

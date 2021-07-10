#!/usr/bin/env python3

import fjm
from readchar import readchar

from os.path import isfile, abspath, isdir, join
from glob import glob
from time import time
import argparse
from defs import *
import pickle


def run(input_file, breakpoints={}, defined_input=None, verbose=False, time_verbose=False, output_verbose=False,
        single_step=False, labels_dict={}):
    print(f'  loading memory:  ', end='', flush=True)
    start_time = time()
    mem = fjm.Reader(input_file)
    if time_verbose:
        print(f'{time() - start_time:.3f}s')

    ip = 0
    w = mem.w
    OUT = 2*w
    IN = 3*w + w.bit_length()     # 3w + dww

    input_char, input_size = 0, 0
    output_char, output_size = 0, 0
    output = ''

    if 0 not in labels_dict:
        labels_dict[0] = 'memory_start_0x0000'

    output_anything_yet = False
    ops_executed = 0

    start_time = time()
    pause_time = 0

    while True:
        if single_step or ip in breakpoints:
            pause_time_start = time()
            if ip in breakpoints:
                print(f'\nBreakpoint {breakpoints[ip]} (Address {hex(ip)[2:]}):')
            else:
                if ip in labels_dict:
                    print(f'\nAddress {hex(ip)[2:]} ({labels_dict[ip]}):')
                else:
                    address_before = max([a for a in labels_dict if a <= ip])
                    print(f'\nAddress {hex(ip)[2:]} ({labels_dict[address_before]} + {hex(ip - address_before)}):')
            print(f'  f: {hex(mem.get_word(ip))[2:]}\n  j: {hex(mem.get_word(ip + w))[2:]}')
            action = input(f's/S for single step, c/C to continue: ')
            if action in ['s', 'S']:
                single_step = True
            if action in ['c', 'C']:
                single_step = False
            pause_time += time() - pause_time_start

        ops_executed += 1

        f = mem.get_word(ip)
        if verbose:
            print(f'{hex(ip)[2:].rjust(7)}:   {hex(f)[2:]}', end='; ', flush=True)

        # handle output
        if OUT <= f <= OUT+1:
            output_char |= (f-OUT) << output_size
            output_size += 1
            if output_size == 8:
                output += chr(output_char)
                if verbose:
                    print(f'\n\n\nOutputed Char:  {chr(output_char)}\n\n\n', end='', flush=True)
                else:
                    print(chr(output_char), end='', flush=True)
                output_anything_yet = True
                output_char, output_size = 0, 0

        # handle input
        if ip <= IN < ip+2*w:
            if input_size == 0:
                if defined_input is None:
                    pause_time_start = time()
                    input_char = ord(readchar())
                    pause_time += time() - pause_time_start
                elif len(defined_input) > 0:
                    input_char = ord(defined_input[0])
                    defined_input = defined_input[1:]
                else:
                    if output_verbose and output_anything_yet:
                        print()
                    run_time = time() - start_time - pause_time
                    return run_time, ops_executed, output, RunFinish.Input  # no more input
                input_size = 8
            mem.write_bit(IN, input_char & 1)
            input_char = input_char >> 1
            input_size -= 1

        mem.write_bit(f, 1-mem.read_bit(f))     # Flip!
        new_ip = mem.get_word(ip+w)
        if verbose:
            print(hex(new_ip)[2:])
        if new_ip == ip and not ip <= f < ip+2*w:
            if output_verbose and output_anything_yet:
                print()
            run_time = time()-start_time-pause_time
            return run_time, ops_executed, output, RunFinish.Looping       # infinite simple loop
        ip = new_ip     # Jump!


def debug_and_run(input_file, debugging_file=None,
                     defined_input=None, verbose=set(),
                     breakpoint_addresses=set(), breakpoint_labels=set(), breakpoint_any_labels=set()):
    labels = []
    if debugging_file:
        if isfile(debugging_file):
            with open(debugging_file, 'rb') as f:
                labels = pickle.load(f)

    if not labels and (breakpoint_labels or breakpoint_addresses or breakpoint_any_labels):
        print(f'Warning:  debugging labels can\'t be found!')

    # Handle breakpoints
    breakpoint_map = {ba: hex(ba) for ba in breakpoint_addresses}
    for bl in breakpoint_labels:
        if bl not in labels:
            print(f'Warning:  Breakpoint label {bl} can\'t be found!')
        else:
            breakpoint_map[labels[bl]] = bl
    for bal in breakpoint_any_labels:
        for label in labels:
            if bal in label:
                breakpoint_map[labels[label]] = f'{bal}@{label}'

    opposite_labels = {labels[label]: label for label in labels}

    run_time, ops_executed, output, finish_cause = run(input_file, defined_input=defined_input, verbose=Verbose.Run in verbose,
                                         time_verbose=Verbose.Time in verbose, output_verbose=Verbose.PrintOutput in verbose,
                                         breakpoints=breakpoint_map, labels_dict=opposite_labels)

    return run_time, ops_executed, output, finish_cause


def main():
    parser = argparse.ArgumentParser(description='Assemble and Run FlipJump programs.')
    parser.add_argument('file', help="the FlipJump file.")
    parser.add_argument('-s', '--silent', help="don't show run times", action='store_true')
    parser.add_argument('-t', '--trace', help="trace the running opcodes.", action='store_true')
    parser.add_argument('-f', '--flags', help="running flags", type=int, default=0)
    parser.add_argument('-d', '--debug', help='debugging file')
    parser.add_argument('-b', '--breakpoint', help="pause when reaching this label",
                        default=[], action='append')
    parser.add_argument('-B', '--any_breakpoint', help="pause when reaching any label containing this",
                        default=[], action='append')
    parser.add_argument('--tests', help="run all .fjm files in the given folder (instead of specifying a file).",
                        action='store_true')
    args = parser.parse_args()

    verbose_set = {Verbose.PrintOutput}
    if not args.silent:
        verbose_set.add(Verbose.Time)
    if args.trace:
        verbose_set.add(Verbose.Run)

    if args.tests:
        folder = abspath(args.file)
        if not isdir(folder):
            error('the "file" argument should contain a folder path.')
        for file in glob(join(folder, '*fjm')):
            print(f'running {Path(file).name}:')
            run_time, ops_executed, output, finish_cause = \
                debug_and_run(file,
                              defined_input=None,
                              verbose=verbose_set)
            if not args.silent:
                print(f'finished by {finish_cause.value} after {run_time:.3f}s ({ops_executed} ops executed)')
            print()
    else:

        file = abspath(args.file)
        if not isfile(file):
            parser.error(f'file {file} does not exist.')
        if not file.endswith('.fjm'):
            parser.error(f'file {file} is not a .fjm file.')

        if args.debug:
            debug_file = abspath(args.debug)
            if not isfile(debug_file):
                parser.error(f'debug-file {debug_file} does not exist.')

        breakpoint_set = set(args.breakpoint)
        breakpoint_any_set = set(args.any_breakpoint)

        run_time, ops_executed, output, finish_cause = \
            debug_and_run(file, debugging_file=args.debug,
                          defined_input=None,
                          verbose=verbose_set,
                          breakpoint_labels=breakpoint_set,
                          breakpoint_any_labels=breakpoint_any_set)

        if not args.silent:
            print(f'finished by {finish_cause.value} after {run_time:.3f}s ({ops_executed} ops executed)')
            print()


if __name__ == '__main__':
    main()

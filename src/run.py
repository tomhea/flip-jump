from assembler import assemble
import blm
from readchar import readchar
from tempfile import mkstemp
import os
from defs import *


def run(input_file, breakpoints={}, defined_input=None, verbose=False, time_verbose=False, output_verbose=False,
        single_step=False, labels_dict={}):
    start_time = time()
    mem = blm.Reader(input_file)
    if time_verbose:
        print(f'  loading memory:  {time() - start_time:.3f}s')

    ip = 0
    w = mem.w
    OUT = 2*w
    IN = 3*w + w.bit_length()     # 5w + dww

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
                print(f'\nBreakpoint {breakpoints[ip]}:')
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
            print(f'{hex(ip)[2:].rjust(7)}:   {hex(f)[2:]}', end='; ')

        # handle output
        if OUT <= f <= OUT+1:
            output_char |= (f-OUT) << output_size
            output_size += 1
            if output_size == 8:
                output += chr(output_char)
                if verbose:
                    print(f'\n\n\nOutputed Char:  {chr(output_char)}\n\n\n', end='')
                else:
                    print(chr(output_char), end='')
                output_anything_yet = True
                # if output_char == 0:
                #     print(f'\nfinished by input after {time()-start_time-pause_time:.3f}s ({ops_executed} ops executed)')
                #     break
                output_char, output_size = 0, 0

        # handle input
        if ip <= IN < ip+2*w:
            if input_size == 0:
                if defined_input is None:
                    input_char = ord(readchar())
                else:
                    input_char = ord(defined_input[0])
                    defined_input = defined_input[1:]
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
            return run_time, ops_executed, output       # infinite simple loop
        ip = new_ip     # Jump!


def assemble_and_run(input_files, w, preprocessed_file=None, output_file=None, defined_input=None, verbose=set(),
                     breakpoint_addresses=set(), breakpoint_labels=set(), breakpoint_any_labels=set()):
    temp_output_file, temp_fd = False, 0
    if output_file is None:
        temp_fd, output_file = mkstemp()
        temp_output_file = True

    labels = assemble(input_files, output_file, w, preprocessed_file=preprocessed_file, verbose=verbose)

    # Handle breakpoints
    breakpoint_map = {ba: hex(ba) for ba in breakpoint_addresses}
    for bl in breakpoint_labels:
        if bl not in labels:
            print(f'Warning:  Breakpoint label {bl} can\'t be found!')
        else:
            breakpoint_map[labels[bl].val] = bl
    for bal in breakpoint_any_labels:
        for label in labels:
            if bal in label:
                breakpoint_map[labels[label].val] = f'{bal}@{label}'

    opposite_labels = {labels[label].val: label for label in labels}

    run_time, ops_executed, output = run(output_file, defined_input=defined_input, verbose=Verbose.Run in verbose,
                                         time_verbose=Verbose.Time in verbose, output_verbose=Verbose.PrintOutput,
                                         breakpoints=breakpoint_map, labels_dict=opposite_labels)

    if temp_output_file:
        os.close(temp_fd)

    return run_time, ops_executed, output


def main():
    for test, _input in (('cat', "Hello World!\0"), ('ncat', ''.join(chr(0xff-ord(c)) for c in 'Flip Jump Rocks!'+'\0')),
                         ('testbit', ''), ('testbit_with_nops', ''), ('mathbit', ''), ('mathvec', ''), ('not', ''),
                         ('rep', ''), ('ncmp', ''), ('nadd', ''), ('hexprint', ''), ('simple', ''), ('hello_world', ''),
                         ('ptr', ''), ('func', '')):
        if test in ('func',):
            continue
        # if test != 'func':
        #     continue
        print(f'running test {test}({_input}):')
        run_time, ops_executed, output = assemble_and_run([f'tests/{test}.fj'], 64,
                        preprocessed_file=f'tests/compiled/{test}__no_macros.fj',
                        output_file=f'tests/compiled/{test}.blm',
                        defined_input=_input,
                        verbose=set([
                            # Verbose.Time,
                            Verbose.PrintOutput,
                            # Verbose.Run,
                        ]),
                        breakpoint_labels=set([
                            # '__to_jump',
                        ]))
        # print(output)
        print(f'finished by looping after {run_time:.3f}s ({ops_executed} ops executed)')
        print()


if __name__ == '__main__':
    main()

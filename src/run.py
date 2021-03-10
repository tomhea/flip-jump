from assembler import assemble
import blm
from readchar import readchar
from tempfile import mkstemp
import os
from defs import *


def run(input_file, breakpoints={}, defined_input=None, verbose=False, time_verbose=False, single_step=False):
    start_time = time()
    mem = blm.Reader(input_file)
    if time_verbose:
        print(f'  loading memory:  {time() - start_time:.3f}s')

    ip = 0
    w = mem.w
    OUT = 2*w
    IN = 3*w + w.bit_length()     # 5w + dww

    output_char, output_size = 0, 0
    input_char, input_size = 0, 0

    output_anything_yet = False
    ops_executed = 0

    start_time = time()

    while True:
        if single_step:
            print(f'\nAddress {hex(ip)[2:]}:')
            print(f'  f: {hex(mem.get_word(ip))[2:]}\n  j: {hex(mem.get_word(ip + w))[2:]}')
            action = input(f's/S for single step, c/C to continue: ')
            if action in ['s', 'S']:
                single_step = True
            if action in ['c', 'C']:
                single_step = False
        elif ip in breakpoints:
            print(f'\nBreakpoint {breakpoints[ip]}:')
            print(f'  f: {hex(mem.get_word(ip))[2:]}\n  j: {hex(mem.get_word(ip+w))[2:]}')
            action = input(f's/S for single step, anything else to continue: ')
            if action in ['s', 'S']:
                single_step = True

        ops_executed += 1

        f = mem.get_word(ip)
        if verbose:
            print(f'{hex(ip)[2:].rjust(5)}:   {hex(f)[2:]}', end='; ')

        # handle output
        if OUT <= f <= OUT+1:
            output_char |= (f-OUT) << output_size
            output_size += 1
            if output_size == 8:
                if verbose:
                    print(f'\n\n\nOutputed Char:  {chr(output_char)}\n\n\n', end='')
                else:
                    print(chr(output_char), end='')
                output_anything_yet = True
                if output_char == 0:
                    print(f'\nfinished by input after {time()-start_time:.3f}s ({ops_executed} ops executed)')
                    break
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
            if output_anything_yet:
                print()
            print(f'finished by looping after {time()-start_time:.3f}s ({ops_executed} ops executed)')
            break       # infinite simple loop
        ip = new_ip     # Jump!


def assemble_and_run(input_files, preprocessed_file=None, output_file=None, defined_input=None, verbose=set(),
                     breakpoint_addresses=set(), breakpoint_labels=set(), breakpoint_any_labels=set()):
    temp_output_file, temp_fd = False, 0
    if output_file is None:
        temp_fd, output_file = mkstemp()
        temp_output_file = True

    labels = assemble(input_files, output_file, preprocessed_file=preprocessed_file, verbose=verbose)

    breakpoint_map = {ba:hex(ba) for ba in breakpoint_addresses}
    for bl in breakpoint_labels:
        if bl not in labels:
            error(f'Breakpoint label {bl} can\'t be found!')
        breakpoint_map[labels[bl].val] = bl
    for bal in breakpoint_any_labels:
        for label in labels:
            if bal in label:
                breakpoint_map[labels[label].val] = f'{bal}@{label}'

    run(output_file, defined_input=defined_input, verbose=Verbose.Run in verbose, time_verbose=Verbose.Time in verbose, breakpoints=breakpoint_map)

    if temp_output_file:
        os.close(temp_fd)


def main():
    for test, _input in (('cat', "Hello World!\0"), ('ncat', ''.join(chr(0xff-ord(c)) for c in 'Flip Jump Rocks!'+'\0')),
                         ('testbit', ''), ('testbit_with_nops', ''), ('mathbit', ''), ('mathvec', ''), ('not', ''),
                         ('rep', ''), ('ncmp', ''), ('nadd', ''), ('hexprint', ''), ('simple', ''), ('hello_world', ''),
                         ('ptr', '')):
        # if test != 'ptr':
        #     continue
        print(f'running test {test}({_input}):')
        assemble_and_run([f'tests/{test}.fj'], preprocessed_file=f'tests/compiled/{test}__no_macros.fj',
                         output_file=f'tests/compiled/{test}.blm', defined_input=_input, verbose=set([
                # Verbose.Time,
                # Verbose.Run,
            ]),
                         breakpoint_labels=set([
                             # '__to_jump',
                             # 'd3_var',
                         ]))
        print()


if __name__ == '__main__':
    main()

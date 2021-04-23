#!/usr/bin/env python3

from assembler import assemble
import blm
from readchar import readchar
from tempfile import mkstemp
from os import mkdir, close

from os.path import isfile, abspath, isdir
import argparse
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
                # if output_char == 0:
                #     print(f'\nfinished by input after {time()-start_time-pause_time:.3f}s ({ops_executed} ops executed)')
                #     break
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


def assemble_and_run(input_files, w, try_cached=True, use_stl=True, preprocessed_file=None, debugging_file=None,
                     output_file=None, defined_input=None, verbose=set(), only_run=False,
                     breakpoint_addresses=set(), breakpoint_labels=set(), breakpoint_any_labels=set()):
    temp_output_file, temp_fd = False, 0
    if output_file is None:
        temp_fd, output_file = mkstemp()
        temp_output_file = True

    labels = assemble(input_files, output_file, w, try_cached=try_cached, use_stl=use_stl, only_cache=only_run,
                      preprocessed_file=preprocessed_file, debugging_file=debugging_file, verbose=verbose)

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

    run_time, ops_executed, output, finish_cause = run(output_file, defined_input=defined_input, verbose=Verbose.Run in verbose,
                                         time_verbose=Verbose.Time in verbose, output_verbose=Verbose.PrintOutput,
                                         breakpoints=breakpoint_map, labels_dict=opposite_labels)

    if temp_output_file:
        close(temp_fd)

    return run_time, ops_executed, output, finish_cause


def main():
    parser = argparse.ArgumentParser(description='Assemble and Run FlipJump programs.')
    parser.add_argument('file', help="the FlipJump file.", nargs='+')
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument('-a', '--assemble', help="only assembles the (.fj) file", action='store_true')
    action_group.add_argument('-r', '--run', help="only runs the (.blm) file", action='store_true')
    parser.add_argument('-v', '--verbose', help="show assemble & run times", action='store_true')
    parser.add_argument('-t', '--trace', help="trace the running opcodes.", action='store_true')
    parser.add_argument('-w', '--width', help="specify memory-width. 64 by default",
                        type=int, default=64)
    parser.add_argument('-b', '--breakpoint', help="pause when reaching this label",
                        default=[], action='append')
    parser.add_argument('-B', '--any_breakpoint', help="pause when reaching any label containing this",
                        default=[], action='append')
    parser.add_argument('--no_cache', help="reassemble the file, don't use any cached results.", action='store_true')
    parser.add_argument('--no_stl', help="don't assemble/link the standard library files.", action='store_true')
    args = parser.parse_args()

    if args.width < 8:
        print('error: w should be at least 8.')
        exit(1)
    if args.width & (args.width-1):
        print('error: w should be a power of 2.')
        exit(1)

    for file in args.file:
        if not isfile(abspath(file)):
            print(f'error: file {file} does not exist.')
            exit(1)

    file = abspath(args.file[0])

    if file.endswith('.fj'):
        fj_ext = True
    elif file.endswith('.blm'):
        fj_ext = False
    else:
        print(f'error: bad file extension.')
        exit(1)

    base_file_name = file.rsplit('.', 1)[0]
    base_dir_name, file_name = base_file_name.rsplit('/', 1)

    base_fj_dir = base_dir_name + '/__fj_compiled__'

    if len(args.file) == 1 and abspath(args.file[0]).endswith('.blm'):
        base_fj_dir = base_dir_name
    elif not isdir(base_fj_dir):
        mkdir(base_fj_dir)

    preprocessed_file = f'{base_fj_dir}/{file_name}__no_macros.fj'
    debugging_file = f'{base_fj_dir}/{file_name}.fj_debug'
    output_file = f'{base_fj_dir}/{file_name}.blm'

    verbose_set = {Verbose.PrintOutput}
    if args.verbose:
        verbose_set.add(Verbose.Time)
    if args.trace:
        verbose_set.add(Verbose.Run)

    breakpoint_set = set(args.breakpoint)
    breakpoint_any_set = set(args.any_breakpoint)

    if args.assemble and not args.run:
        for file in args.file:
            file = abspath(file)
            if not file.endswith('.fj'):
                print(f'error: file {file} is not a .fj file.')
                exit(1)
        assemble(args.file, output_file, args.width, try_cached=not args.no_cache, use_stl=not args.no_stl,
                 preprocessed_file=preprocessed_file, debugging_file=debugging_file, verbose=verbose_set)
        exit()
    elif args.run and not args.assemble:
        if len(args.file) != 1:
            print('specify just one file to run')
        file = abspath(args.file[0])
        if not file.endswith('.blm'):
            print(f'error: file {file} is not a .blm file.')
            exit(1)
        args.file = []
        output_file = file

    run_time, ops_executed, output, finish_cause = \
        assemble_and_run(args.file, args.width,
                         try_cached=not args.no_cache,
                         use_stl=not args.no_stl,
                         only_run=args.run and not args.assemble,
                         preprocessed_file=preprocessed_file,
                         debugging_file=debugging_file,
                         output_file=output_file,
                         defined_input=None,
                         verbose=verbose_set,
                         breakpoint_labels=breakpoint_set,
                         breakpoint_any_labels=breakpoint_any_set)
    # print(output)
    if args.verbose:
        print(f'finished by {finish_cause.value} after {run_time:.3f}s ({ops_executed} ops executed)')
        print()

    exit()

    for test, _input in (('cat', "Hello World!\0"), ('ncat', ''.join(chr(0xff-ord(c)) for c in 'Flip Jump Rocks!\0')),
                         ('testbit', ''), ('testbit_with_nops', ''), ('mathbit', ''), ('mathvec', ''), ('not', ''),
                         ('rep', ''), ('ncmp', ''), ('nadd', ''), ('hexprint', ''), ('simple', ''), ('hello_world', ''),
                         ('ptr', ''), ('func', ''), ('print_hex_int', ''), ('calc', 'x82+x8f\nx152+x23\nx134\nx6-x15\nx132-x111\nx1234+x4321\n-x67\nxf+xfff6\nx1000b-xf\nxd0a0c0d0+x0e0d000e\nq\n')):
        # if test in ('func', 'calc'):
        #     continue
        if test not in (
                'calc',
        #         'print_hex_int',
                ):
            continue
        print(f'running test {test}({_input}):')
        run_time, ops_executed, output, finish_cause = assemble_and_run([f'tests/{test}.fj'], 64,
                        preprocessed_file=f'tests/compiled/{test}__no_macros.fj',
                        debugging_file=f'tests/compiled/{test}.fj_debug',
                        output_file=f'tests/compiled/{test}.blm',
                        defined_input=None,
                        verbose=set([
                            Verbose.Time,
                            Verbose.PrintOutput,
                            # Verbose.Run,
                        ]),
                        breakpoint_labels=set([
                            # '__to_jump',
                        ]),
                        breakpoint_any_labels=set([
                            # 'gibly',
                        ]))
        # print(output)
        print(f'finished by {finish_cause.value} after {run_time:.3f}s ({ops_executed} ops executed)')
        print()


if __name__ == '__main__':
    main()

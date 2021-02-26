from assembler import assemble
import blm
from readchar import readchar
from tempfile import mkstemp
import os
from defs import *


def run(input_file, defined_input=None, verbose=False):
    ip = 0
    mem = blm.Reader(input_file)
    w = mem.w
    OUT = 2*w
    IN = 3*w + w.bit_length()     # 5w + dww

    output_char, output_size = 0, 0
    input_char, input_size = 0, 0

    output_anything_yet = False
    ops_executed = 0

    while True:
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
                    print(f'\nfinished by input ({ops_executed} ops executed)')
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
            mem[IN] = input_char & 1
            input_char = input_char >> 1
            input_size -= 1

        mem.flip(f)
        new_ip = mem.get_word(ip+w)
        if verbose:
            print(hex(new_ip)[2:])
        if new_ip == ip and not ip <= f < ip+2*w:
            if output_anything_yet:
                print()
            print(f'finished by looping ({ops_executed} ops executed)')
            break       # infinite simple loop
        ip = new_ip


def assemble_and_run(input_files, preprocessed_file=None, output_file=None, defined_input=None, verbose=set()):
    temp_output_file, temp_fd = False, 0
    if output_file is None:
        temp_fd, output_file = mkstemp()
        temp_output_file = True

    assemble(input_files, output_file, preprocessed_file=preprocessed_file, verbose=verbose)
    run(output_file, defined_input=defined_input, verbose=Verbose.Run in verbose)

    if temp_output_file:
        os.close(temp_fd)


def main():
    for test, _input in (('cat', "Hello World!\0"), ('ncat', ''.join(chr(255-ord(c)) for c in 'Flip Jump Rocks!\0')),
                         ('testbit', ''), ('testbit_with_nops', ''), ('mathbit', ''), ('mathvec', ''), ('not', ''), ('rep', '')):
        # if test != 'mathvec':
        #     continue
        print(f'running test {test}({_input}):')
        assemble_and_run([f'tests/{test}.fj'], preprocessed_file=f'tests/compiled/{test}__no_macros.fj',
                         output_file=f'tests/compiled/{test}.blm', defined_input=_input, verbose=set([]))
        print()


if __name__ == '__main__':
    main()

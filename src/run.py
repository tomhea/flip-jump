from assembler import full_assemble
import fjc
from readchar import readchar
from tempfile import mkstemp
import os


def run(input_file, defined_input=None):
    ip = 0
    mem = fjc.Reader(input_file)
    w = mem.w
    OUT = 4*w
    IN = 5*w + w.bit_length()     # 5w + dww

    output_char, output_size = 0, 0
    input_char, input_size = 0, 0

    output_anything_yet = False

    while True:
        f = mem.get_word(ip)

        # handle output
        if OUT <= f <= OUT+1:
            output_char |= (f-OUT) << output_size
            output_size += 1
            if output_size == 8:
                print(chr(output_char), end='')
                output_anything_yet = True
                if output_char == 0:
                    print('\nfinished by input')
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
        if new_ip == ip and not ip <= f < ip+2*w:
            if output_anything_yet:
                print()
            print('finished by looping')
            break       # infinite simple loop
        ip = new_ip


def assemble_and_run(input_files, preprocessed_file=None, output_file=None, defined_input=None):
    temp_output_file, temp_fd = False, 0
    if output_file is None:
        temp_fd, output_file = mkstemp()
        temp_output_file = True

    full_assemble(input_files, output_file, preprocessed_file=preprocessed_file)
    run(output_file, defined_input=defined_input)

    if temp_output_file:
        os.close(temp_fd)


def main():
    for test, _input in (('cat', "Hello World!\0"), ('ncat', "¹\x93\x96\x8fßµ\x8a\x92\x8fß\xad\x90\x9c\x94\x8cÞÿ"),
                         ('testbit', ''), ('mathbit', ''), ('mathvec', ''), ('not', '')):
        print(f'running test {test}({_input}):')
        assemble_and_run([f'tests/{test}.fjm'], preprocessed_file=f'tests/{test}.fj', output_file=f'tests/{test}.fjc', defined_input=_input)
        print()


if __name__ == '__main__':
    main()

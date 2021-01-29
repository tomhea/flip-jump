import assembler
import fjc
from readchar import readchar


def run(input_file):
    ip = 0
    mem = fjc.Reader(input_file)
    w = mem.w
    OUT = 4*w
    IN = 5*w + w.bit_length()     # 5w + dww

    output_char, output_size = 0, 0
    input_char, input_size = 0, 0

    while True:
        f = mem.get_word(ip)

        # handle output
        if OUT <= f <= OUT+1:
            output_char = (output_char << 1) | (f-OUT)
            output_size += 1
            if output_size == 8:
                print(chr(output_char), end='')
                output_char, output_size = 0, 0

        # handle input
        if ip <= IN < ip+2*w:
            if input_size == 0:
                input_char = readchar()
                input_size = 8
            mem[IN] = input_char & 1
            input_char = input_char << 1
            input_size -= 1

        mem.flip(f)
        new_ip = mem.get_word(ip+w)
        if new_ip == ip and not ip <= f < ip+2*w:
            break       # infinite simple loop
        ip = new_ip


def main():
    run('tests/cat.fjc')


if __name__ == '__main__':
    main()

import fjc
from preprocessor import preprocess
from tempfile import mkstemp
import os


def handle_front_labels(line, labels, bit_address):
    # TODO regex magic, ignore leading whitespaces and add leading labels
    return line


def first_pass(code, bit_width=64):     # labels addresses, remove (label) defs, implied ';'
    bit_address = 0
    labels = {}
    next_code = []

    for line in code:
        # handle labels with handle_front_labels() at all times

        # if should_be_code_but_no_;():
            # add_implicit_;()

        if '#' in code:
            pass
        if ';' in line:
            pass
            bit_address += 2*bit_width

    return labels, next_code


def assemble(input_file, output_file, bit_width=64):
    writer = fjc.Writer(bit_width)
    code = [' '.join(line.split('//', 1)[0].rsplit(':', 1)[-1].split()) for line in open(input_file, 'r')]
    code = [op for op in code if op]
    labels, code = first_pass(code, bit_width)

    # TODO: swap labels, handle [][][], write to fjc writer as binary.
    writer.write_to_file(output_file)


def full_assemble(input_files, output_file, preprocessed_file=None, bit_width=64, stl=True):
    temp_preprocessed_file, temp_fd = False, 0
    if preprocessed_file is None:
        temp_fd, preprocessed_file = mkstemp()
        temp_preprocessed_file = True

    preprocess(input_files, preprocessed_file)
    assemble(preprocessed_file, output_file, bit_width=64, stl=True)

    if temp_preprocessed_file:
        os.close(temp_fd)


def main():
    print('assembling')
    for test_name in ('cat', 'ncat', 'mathbit', 'not', 'testbit', 'mathvec'):
        full_assemble([f'tests/{test_name}.fjm'], f'tests/{test_name}.fjc', preprocessed_file=f'tests/{test_name}.fj')


if __name__ == '__main__':
    main()

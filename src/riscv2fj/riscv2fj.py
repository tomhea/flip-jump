from elftools.elf.elffile import ELFFile


def write_op(file, op):
    file.write(f'    \\\\TODO op 0x{op:08x}')
    # TODO real ops here.


def addr_label(addr):
    return f'__RISCV_ADDR_{addr:08X}'


def write_data(file, data, vaddr, reserved):
    file.write(f'.segment __RISCV_MEM + 0x{vaddr:08x}*8*dw\n')
    for byte in data:
        file.write(f'.var 8 {byte}\n')
    if reserved > 0:
        file.write(f'.reserve {reserved}*8*dw\n')
    file.write(f'\n\n')


def write_text(ops_file, jmp_file, data, vaddr):
    jmp_file.write(f'.segment __RISCV_JMP + 0x{vaddr:08x}/4*dw\n')
    for i in range(0, len(data), 4):
        op = int.from_bytes(data[i:i+4], 'little')
        addr = vaddr + i
        label = addr_label(addr)
        jmp_file.write(f';{label}\n')
        ops_file.write(f'{label}:\n')
        write_op(ops_file, op)
        ops_file.write(f'\n')

    jmp_file.write(f'\n\n')
    ops_file.write(f'\n\n')


def riscv2fj(elf_path, mem_path, jmp_path, ops_path):
    mem_fj = open(mem_path, 'w')
    jmp_fj = open(jmp_path, 'w')
    ops_fj = open(ops_path, 'w')

    with open(elf_path, 'rb') as f:
        elf = ELFFile(f)
        ops_fj.write(f"__RISCV_MEM = 1<<(w-1)                            \\\\ start of memory\n"
                     f"__RISCV_JMP = __RISCV_MEM - (__RISCV_MEM / 32)    \\\\ start of jump table\n\n"
                     f";{addr_label(elf['e_entry'])}                            \\\\ entry point\n"
                     f".riscv_init                                       \\\\ init registers, structs, functions\n\n\n\n")

        for seg in elf.iter_segments():
            if seg['p_type'] != 'PT_LOAD':
                continue

            flags, vaddr, filesz, memsz = seg['p_flags'], seg['p_vaddr'], seg['p_filesz'], seg['p_memsz']
            data = seg.data()
            if flags & 1:   # if execute flag is on
                write_text(ops_fj, jmp_fj, data, vaddr)
            write_data(mem_fj, data, vaddr, memsz - filesz)

    mem_fj.close()
    jmp_fj.close()
    ops_fj.close()


if __name__ == '__main__':
    riscv2fj('sample_exe64.elf', 'mem.fj', 'jmp.fj', 'ops.fj')

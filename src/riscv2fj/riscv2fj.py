from elftools.elf.elffile import ELFFile
from typing import TextIO, Iterator, Tuple


RV_LUI = 0b0110111
RV_AUIPC = 0b0010111
RV_JAL = 0b1101111
RV_JALR = 0b1100111

RV_B = 0b1100011
RV_BEQ = 0b000
RV_BNE = 0b001
RV_BLT = 0b100
RV_BGE = 0b101
RV_BLTU = 0b110
RV_BGEU = 0b111

RV_L = 0b0000011
RV_LB = 0b000
RV_LH = 0b001
RV_LW = 0b010
RV_LBU = 0b100
RV_LHU = 0b101

RV_S = 0b0100011
RV_SB = 0b000
RV_SH = 0b001
RV_SW = 0b010


def register_name(register_index: int) -> str:
    """
    @param register_index: the 5 lsb will be used.
    """
    return f'.regs.x{register_index & 0x1f}'


def get_hex_comment(op: int) -> str:
    return f'\\\\ op 0x{op:08x}'


def r_type(macro_name: str, op: int) -> str:
    return f'    .{macro_name} {register_name(op >> 7)} {register_name(op >> 15)} {register_name(op >> 20)}'\
           f'\t\t{get_hex_comment(op)}\n'


def i_type(macro_name: str, op: int) -> str:
    imm = op >> 20
    return f'    .{macro_name} {register_name(op >> 15)} 0x{imm:x}' \
           f'\t\t{get_hex_comment(op)}\n'


def s_type(macro_name: str, op: int) -> str:
    imm11_5 = op >> 25
    imm4_0 = (op >> 7) & 0x1f
    imm = (imm11_5 << 5) | (imm4_0 << 0)
    return f'    .{macro_name} {register_name(op >> 15)} {register_name(op >> 20)} 0x{imm:x}' \
           f'\t\t{get_hex_comment(op)}\n'


def b_type(macro_name: str, op: int) -> str:
    imm12 = op >> 31
    imm10_5 = (op >> 25) & 0x3f
    imm4_1 = (op >> 8) & 0xf
    imm11 = (op >> 7) & 0x1
    imm = (imm12 << 12) | (imm10_5 << 5) | (imm4_1 << 1) | (imm11 << 11)
    return f'    .{macro_name} {register_name(op >> 15)} {register_name(op >> 20)} 0x{imm:x}' \
           f'\t\t{get_hex_comment(op)}\n'


def u_type(macro_name: str, op: int) -> str:
    imm = op & 0xfffff000
    return f'    .{macro_name} {register_name(op >> 7)} 0x{imm:x}' \
           f'\t\t{get_hex_comment(op)}\n'


def j_type(macro_name: str, op: int) -> str:
    imm20 = op >> 31
    imm10_1 = (op >> 21) & 0x3ff
    imm11 = (op >> 20) & 0x1
    imm_19_12 = (op >> 12) & 0xff
    imm = (imm20 << 20) | (imm10_1 << 1) | (imm11 << 11) | (imm_19_12 << 12)
    return f'    .{macro_name} {register_name(op >> 7)} 0x{imm:x}' \
           f'\t\t{get_hex_comment(op)}\n'


def write_op(ops_file: TextIO, full_op: int) -> None:
    opcode = full_op & 0x7f
    funct3 = (full_op >> 12) & 7
    funct7 = full_op >> 25
    x0_changed = False

    if opcode == RV_LUI:
        ops_file.write(u_type('lui', full_op))
    elif opcode == RV_AUIPC:
        ops_file.write(u_type('auipc', full_op))
    elif opcode == RV_JAL:
        ops_file.write(j_type('jal', full_op))
    elif opcode == RV_JALR:
        if funct3 != 0:
            ops_file.write(f'    // ERROR - bad funct3 at jalr op - 0x{full_op:08x}\n')
        else:
            ops_file.write(i_type('jalr', full_op))

    elif opcode == RV_B:
        if funct3 == RV_BEQ:
            ops_file.write(b_type('beq', full_op))
        elif funct3 == RV_BNE:
            ops_file.write(b_type('bne', full_op))
        elif funct3 == RV_BLT:
            ops_file.write(b_type('blt', full_op))
        elif funct3 == RV_BGE:
            ops_file.write(b_type('bge', full_op))
        elif funct3 == RV_BLTU:
            ops_file.write(b_type('bltu', full_op))
        elif funct3 == RV_BGEU:
            ops_file.write(b_type('bgeu', full_op))

    else:
        ops_file.write(f'    \\\\TODO not-implemented op 0x{full_op:08x}\n')
        # TODO real ops here.

    x0_changed = True
    if x0_changed:
        ops_file.write('    hex.zero 8 .regs.zero\n')

    ops_file.write('\n')


def get_addr_label_name(addr: int) -> str:
    return f'ADDR_{addr:08X}'


def write_jump_to_addr_label(jmp_file: TextIO, addr: int) -> None:
    jmp_file.write(f';.{get_addr_label_name(addr)}\n')


def write_declare_addr_label(ops_file: TextIO, addr: int) -> None:
    ops_file.write(f'{get_addr_label_name(addr)}:\n')


def write_memory_data(mem_file: TextIO, data: bytes, virtual_address: int, reserved_bytes_size: int) -> None:
    mem_file.write(f'segment .MEM + 0x{virtual_address:08x}*8*dw\n')
    for byte in data:
        mem_file.write(f'hex.vec 2 {byte}\n')
    if reserved_bytes_size > 0:
        mem_file.write(f'reserve {reserved_bytes_size}*2*dw\n')
    mem_file.write(f'\n\n')


def ops_and_addr_iterator(data: bytes, virtual_address: int) -> Iterator[Tuple[int, int]]:
    return ((int.from_bytes(data[i:i+4], 'little'), virtual_address + i)
            for i in range(0, len(data), 4))


def write_ops_and_jumps(ops_file: TextIO, jmp_file: TextIO, data: bytes, virtual_address: int) -> None:
    jmp_file.write(f'segment .JMP + 0x{virtual_address:08x}/4*dw\n')
    for op, addr in ops_and_addr_iterator(data, virtual_address):
        write_jump_to_addr_label(jmp_file, addr)
        write_declare_addr_label(ops_file, addr)
        write_op(ops_file, op)

    jmp_file.write(f'\n\n')
    ops_file.write(f'\n\n')


def write_open_riscv_namespace(file: TextIO) -> None:
    file.write(f"ns riscv {{\n\n\n")


def write_init_riscv_ops(ops_file: TextIO, start_addr: int) -> None:
    ops_file.write(f"MEM = 1<<(w-1)                      \\\\ start of memory\n"
                   f"JMP = __RV_MEM - (__RV_MEM / 32)    \\\\ start of jump table\n\n"
                   f";.{get_addr_label_name(start_addr)}                     \\\\ entry point\n"
                   f".init                               \\\\ init registers, structs, functions\n\n\n\n")


def write_close_riscv_namespace(file: TextIO) -> None:
    file.write(f"}}\n")


def is_loaded_to_memory(segment):
    return segment['p_type'] == 'PT_LOAD'


def is_segment_executable(segment):
    return segment['p_flags'] & 1


def get_virtual_start_address(segment):
    return segment['p_vaddr']


def get_reserved_byte_size(segment):
    return segment['p_memsz'] - segment['p_filesz']


def get_segment_data(segment) -> bytes:
    return segment.data()


def write_segment(mem_file: TextIO, jmp_file: TextIO, ops_file: TextIO, segment) -> None:
    virtual_address = get_virtual_start_address(segment)
    reserved_byte_size = get_reserved_byte_size(segment)
    data = get_segment_data(segment)

    if is_segment_executable(segment):
        write_ops_and_jumps(ops_file, jmp_file, data, virtual_address)
    write_memory_data(mem_file, data, virtual_address, reserved_byte_size)


def get_start_address(elf: ELFFile) -> int:
    return elf['e_entry']


def write_file_prefixes(mem_file: TextIO, jmp_file: TextIO, ops_file: TextIO, elf: ELFFile) -> None:
    for file in (mem_file, jmp_file, ops_file):
        write_open_riscv_namespace(file)

    write_init_riscv_ops(ops_file, get_start_address(elf))


def write_file_suffixes(mem_file: TextIO, jmp_file: TextIO, ops_file: TextIO) -> None:
    for file in (mem_file, jmp_file, ops_file):
        write_close_riscv_namespace(file)


def get_segments(elf: ELFFile) -> Iterator:
    return elf.iter_segments()


def create_fj_files_from_riscv_elf(elf_path, mem_path, jmp_path, ops_path):
    with open(mem_path, 'w') as mem_file, open(jmp_path, 'w') as jmp_file, open(ops_path, 'w') as ops_file:
        with open(elf_path, 'rb') as elf_file:
            elf = ELFFile(elf_file)
            write_file_prefixes(mem_file, jmp_file, ops_file, elf)

            for segment in get_segments(elf):
                if is_loaded_to_memory(segment):
                    write_segment(mem_file, jmp_file, ops_file, segment)

            write_file_suffixes(mem_file, jmp_file, ops_file)


if __name__ == '__main__':
    create_fj_files_from_riscv_elf('sample_exe64.elf',
                                   mem_path='mem.fj', jmp_path='jmp.fj', ops_path='ops.fj')

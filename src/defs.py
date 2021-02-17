from enum import Enum


main_macro = ('.__M_a_i_n__', 0)


def error(msg):
    print(f'\nERROR: {msg}\n')
    exit(1)


def smart_int16(num):
    try:
        return int(num, 16)
    except ...:
        error(f'{num} is not a number!')


def stl(xx):
    if xx not in (8, 16, 32, 64):
        error(f"no such stl: lib{xx}.fj")
    return [f'stl/{lib}.fj' for lib in (f'lib{xx}', 'bitlib', 'veclib')]


id_re = r'[a-zA-Z_][a-zA-Z_0-9]*'
number_re = r'[0-9a-fA-F]+'


class Verbose(Enum):
    Parse = 1
    MacroSolve = 2
    LabelDict = 3
    LabelSolve = 4
    Run = 5


class OpType(Enum):
    FlipJump = 1        # address, address              # Survives until (3) label resolve
    BitSpecific = 2     # NUMBER, address               # Survives until (3) label resolve
    DDFlipBy = 3        # address, address              # Survives until (3) label resolve  (at later
    DDFlipByDbit = 4    # address, address              # Survives until (3) label resolve
    DDVar = 5           # NUMBER, address               # Survives until (3) label resolve
    Label = 6           # ID                            # Survives until (2) label dictionary
    DDPad = 7           # NUMBER                        # Survives until (2) label dictionary
    Macro = 8           # ID, address [address..]       # Survives until (1) macro resolve
    Rep = 9             # address, ID, statements       # Survives until (1) macro resolve
    DDOutput = 10       # NUMBER                        # Survives until (1) macro resolve


class Op:
    def __init__(self, op_type, data, file, line):
        self.type = op_type
        self.data = data
        self.file = file
        self.line = line

    def __str__(self):
        return f'{f"{self.type}:"[7:]:10}    Data: {", ".join([str(d) for d in self.data])}    File: {self.file} (line {self.line})'


class AddrType(Enum):
    ID = 1
    Number = 2
    SkipBefore = 3
    SkipAfter = 4


class Address:
    def __init__(self, addr_type, base, index):
        self.type = addr_type
        self.base = base
        self.index = index

    def __str__(self):
        if self.index == 0:
            return f'{self.base}'
        return f'{self.base}[{self.index}]'


def new_label(counter):
    return Address(AddrType.ID, f'__label{next(counter)}', 0)


temp_address = Address(AddrType.ID, 'temp', 0)
next_address = Address(AddrType.SkipAfter, 0, 0)

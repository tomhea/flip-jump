from enum import Enum
from operator import mul, add, sub, floordiv


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
    return [f'stl/{lib}.fj' for lib in (f'lib{xx}', 'bitlib', 'veclib', 'iolib')]


id_re = r'[a-zA-Z_][a-zA-Z_0-9]*'
hex_num = r'0[xX][0-9a-fA-F]+'
bin_num = r'0[bB][01]+'
dec_num = r'[0-9]+'
number_re = rf'({bin_num})|({hex_num})|({dec_num})'


class Verbose(Enum):
    Parse = 1
    MacroSolve = 2
    LabelDict = 3
    LabelSolve = 4
    Run = 5


class OpType(Enum):
    FlipJump = 1        # expr, expr                # Survives until (3) label resolve
    BitSpecific = 2     # expr, expr                # Survives until (3) label resolve
    DDFlipBy = 3        # expr, expr                # Survives until (3) label resolve  (at later
    DDFlipByDbit = 4    # expr, expr                # Survives until (3) label resolve
    DDVar = 5           # expr, expr                # Survives until (3) label resolve
    Label = 6           # ID                        # Survives until (2) label dictionary
    DDPad = 7           # expr                      # Survives until (2) label dictionary
    Macro = 8           # ID, expr [expr..]         # Survives until (1) macro resolve
    Rep = 9             # expr, ID, statements      # Survives until (1) macro resolve
    DDOutput = 10       # expr                      # Survives until (1) macro resolve


class Op:
    def __init__(self, op_type, data, file, line):
        self.type = op_type
        self.data = data
        self.file = file
        self.line = line

    def __str__(self):
        return f'{f"{self.type}:"[7:]:10}    Data: {", ".join([str(d) for d in self.data])}    File: {self.file} (line {self.line})'


# class AddrType(Enum):
#     ID = 1
#     Number = 2
#     SkipBefore = 3
#     SkipAfter = 4
#
#
# class Address:
#     def __init__(self, addr_type, base, index):
#         self.type = addr_type
#         self.base = base
#         self.index = index
#
#     def __str__(self):
#         base_hex = hex(self.base)[2:] if type(self.base) is int else self.base
#         if self.index == 0:
#             return f'{base_hex}'
#         return f'{base_hex}[{hex(self.index)[2:]}]'


class Expr:
    def __init__(self, expr):
        self.val = expr

    # replaces every string it can with its dictionary value, and evaluates anything it can.
    # returns the list of unknown id's
    def eval(self, id_dict, file, line):
        if self.is_tuple():
            e1, op, e2 = self.val
            res1 = e1.eval(id_dict, file, line)
            res2 = e2.eval(id_dict, file, line)
            if res1 or res2:
                return res1 + res2
            else:
                try:
                    self.val = op(e1.val, e2.val)
                    return []
                except BaseException as e:
                    error(f'{repr(e)}. bad math operation: {str(self)} in file {file} (line {line})')
        elif self.is_str():
            if self.val in id_dict:
                self.val = id_dict[self.val].val
                return self.eval({}, file, line)
            else:
                return [self.val]
        return []

    def is_int(self):
        return type(self.val) is int

    def is_str(self):
        return type(self.val) is str

    def is_tuple(self):
        return type(self.val) is tuple

    def __str__(self):
        if self.is_tuple():
            e1, op, e2 = self.val
            return f'({str(e1)} {op.__name__} {str(e2)})'
        if self.is_str():
            return self.val
        if self.is_int():
            return hex(self.val)[2:]
        error(f'bad expression: {self.val} (of type {type(self.val)})')


def eval_all(op, id_dict={}):
    ids = []
    for expr in op.data:
        if type(expr) is Expr:
            ids += expr.eval(id_dict, op.file, op.line)
    return ids


def id_swap(op, id_dict={}):
    new_data = []
    for datum in op.data:
        if type(datum) is str and datum in id_dict:
            swapped_label = id_dict[datum]
            if not swapped_label.is_str():
                error(f'Bad label swap (from {datum} to {swapped_label}) in {op}.')
            new_data.append(swapped_label.val)
        else:
            new_data.append(datum)
    op.data = tuple(new_data)


def new_label(counter):
    return Expr(f'__label{next(counter)}')


def temp_address() -> Expr:
    return Expr('temp')


def next_address() -> Expr:
    return Expr('>')

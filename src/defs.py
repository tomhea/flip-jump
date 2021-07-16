from enum import Enum
from pathlib import Path


main_macro = ('.__M_a_i_n__', 0)


def error(msg):
    print()
    print(f'ERROR: {msg}')
    print()
    exit(1)


def smart_int16(num):
    try:
        return int(num, 16)
    except ...:
        error(f'{num} is not a number!')


def stl():
    path = Path(__file__).parent

    return [str(path / f'../stl/{lib}.fj') for lib in (f'runlib', 'bitlib', 'veclib', 'iolib', 'ptrlib', 'mathlib')]


id_re = r'[a-zA-Z_][a-zA-Z_0-9]*'
dot_id_re = fr'({id_re}|\.*)?(\.({id_re}))+'

bin_num = r'0[bB][01]+'
hex_num = r'0[xX][0-9a-fA-F]+'
dec_num = r'[0-9]+'

char_escape_dict = {'0': 0x0, 'a': 0x7, 'b': 0x8, 'e': 0x1b, 'f': 0xc, 'n': 0xa, 'r': 0xd, 't': 0x9, 'v': 0xb, '\\': 0x5c, "'": 0x27, '"': 0x22, '?': 0x3f}
escape_chars = ''.join(k for k in char_escape_dict)
char = fr'[ -~]|\\[{escape_chars}]|\\[xX][0-9a-fA-F]{{2}}'

number_re = fr"({bin_num})|({hex_num})|('({char})')|({dec_num})"
string_re = fr'"({char})*"'


def handle_char(s):
    if s[0] != '\\':
        return ord(s[0]), 1
    if s[1] in char_escape_dict:
        return char_escape_dict[s[1]], 2
    return int(s[2:4], 16), 4


class Verbose(Enum):
    Parse = 1
    MacroSolve = 2
    LabelDict = 3
    LabelSolve = 4
    Run = 5
    Time = 6
    PrintOutput = 7


class RunFinish(Enum):
    Looping = 'looping'
    Input = 'input'


class SegEntry(Enum):
    StartAddress = 0
    ReserveAddress = 1
    WflipAddress = 2


class OpType(Enum):     # op.data array content:

    FlipJump = 1        # expr, expr                # Survives until (2) label resolve
    WordFlip = 2        # expr, expr                # Survives until (2) label resolve
    Segment = 3         # expr                      # Survives until (2) label resolve
    Reserve = 4         # expr                      # Survives until (2) label resolve
    Label = 5           # ID                        # Survives until (1) macro resolve
    Macro = 6           # ID, expr [expr..]         # Survives until (1) macro resolve
    Rep = 7             # expr, ID, macro_call      # Survives until (1) macro resolve


class Op:
    def __init__(self, op_type, data, file, line):
        self.type = op_type
        self.data = data
        self.file = file
        self.line = line

    def __str__(self):
        return f'{f"{self.type}:"[7:]:10}    Data: {", ".join([str(d) for d in self.data])}    File: {self.file} (line {self.line})'

    def macro_trace_str(self):
        assert self.type == OpType.Macro
        macro_name, param_len = self.data[0]
        return f'macro {macro_name}({param_len}) (File {self.file}, line {self.line})'

    def rep_trace_str(self, iter_value, iter_times):
        assert self.type == OpType.Rep
        _, iter_name, macro = self.data
        macro_name, param_len = macro.data[0]
        return f'rep({iter_name}={iter_value}, out of 0..{iter_times-1}) ' \
               f'macro {macro_name}({param_len})  (File {self.file}, line {self.line})'


class Expr:
    def __init__(self, expr):
        self.val = expr

    # replaces every string it can with its dictionary value, and evaluates anything it can.
    # returns the list of unknown id's
    def eval(self, id_dict, file, line):
        if self.is_tuple():
            op, exps = self.val
            res = [e.eval(id_dict, file, line) for e in exps]
            if any(res):
                return sum(res, start=[])
            else:
                try:
                    self.val = op(*[e.val for e in exps])
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
            op, exps = self.val
            if len(exps) == 1:
                e1 = exps[0]
                return f'(#{str(e1)})'
            elif len(exps) == 2:
                e1, e2 = exps
                return f'({str(e1)} {op.__name__} {str(e2)})'
            else:
                e1, e2, e3 = exps
                return f'({str(e1)} ? {str(e2)} : {str(e3)})'
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
    if op.type == OpType.Rep:
        macro_op = op.data[2]
        ids += eval_all(macro_op, id_dict)
    return ids


def id_swap(op, id_dict):
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


def new_label(counter, name=''):
    if name == '':
        return Expr(f'__label{next(counter)}')
    else:
        return Expr(f'__label{next(counter)}_{name}')


wflip_start_label = '__wflip_area_start_'


def next_address() -> Expr:
    return Expr('$')

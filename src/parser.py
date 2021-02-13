from sly import Lexer, Parser
from enum import Enum
from operator import mul, add, sub, floordiv
from os.path import isfile


global curr_file


def error(msg):
    print(f'\nERROR: {msg}\n')
    exit(1)


def stl(xx):
    return [f'stl/{lib}.fj' for lib in (f'lib{xx}', 'bitlib', 'veclib')]


class OpType(Enum):
    FlipJump = 1
    Label = 2
    Macro = 3
    Rep = 4
    BitSpecific = 5
    DDPad = 6
    DDFlipBy = 7
    DDFlipByDbit = 8
    DDVar = 9
    DDOutput = 10


class AddrType(Enum):
    ID = 1
    Number = 2
    SkipBefore = 3
    SkipAfter = 4
    Dollar = 5


main_macro = ('.__M_a_i_n__', 0)
temp_address = (AddrType.ID, 'temp')
next_address = (AddrType.SkipAfter, 0)


class CalcLexer(Lexer):
    tokens = {DEF, END, REP,
              DDPAD, DDFLIP_BY_DBIT, DDFLIP_BY, DDVAR, DDOUTPUT,
              ID, NUMBER, DOLLAR,
              MATH_OP, ASSIGN,
              LBRACKET, RBRACKET, LPAREN, RPAREN,
              DOT, NL, SC,
              SKIP_BEFORE, SKIP_AFTER, HASHTAG}

    ignore_ending_comment = r'//.*'
    ignore_beginning_comment = r'.*:'

    DEF = r'\.def'
    END = r'\.end'
    REP = r'\.rep'

    DDPAD = r'\.\.pad'
    DDFLIP_BY_DBIT = r'\.\.flip_by_dbit'
    DDFLIP_BY = r'\.\.flip_by'
    DDVAR = r'\.\.var'
    DDOUTPUT = r'\.\.output'

    # Tokens
    ID = r'[a-zA-Z_][a-zA-Z_0-9]*'
    NUMBER = r'[0-9a-fA-F]+'
    DOLLAR = r'\$'

    MATH_OP = r'[+\-*/]'
    ASSIGN = r'='

    LBRACKET = r'\['
    RBRACKET = r'\]'
    LPAREN = r'\('
    RPAREN = r'\)'

    # Punctuations
    DOT = r'\.'
    NL = r'[\r\n]'
    SC = r';'

    SKIP_BEFORE = r'<'
    SKIP_AFTER = r'>'
    HASHTAG = r'#'

    ignore = ' \t'

    def MATH_OP(self, t):
        t.value = {'*': mul, '+': add, '-': sub, '/': floordiv}[t.value]
        return t

    def NUMBER(self, t):
        t.value = int(t.value, 16)
        return t

    def NL(self, t):
        self.lineno += 1
        return t

    def error(self, t):
        print(f"Lexing Error at file {curr_file} line {self.lineno}: {t.value[0]}")
        self.index += 1


class CalcParser(Parser):
    tokens = CalcLexer.tokens
    # debugfile = 'src/parser.out'

    def __init__(self):
        self.macros = {main_macro: [[], []]}
        self.defs = {}

    def error(self, token):
        print(f'Syntax Error at file {curr_file} line {token.lineno}, token=({token.type}, {token.value})')

    @_('definable_line_statements')
    def program(self, p):
        self.macros[main_macro][1] += p[0]

    @_('definable_line_statements definable_line_statement')
    def definable_line_statements(self, p):
        if p[1]:
            return p[0] + p[1]
        return p[0]

    @_('empty')
    def definable_line_statements(self, p):
        return []

    @_('')
    def empty(self, p):
        return None

    @_('line_statement')
    def definable_line_statement(self, p):
        return p[0]

    @_('labels macro_def labels NL')
    def definable_line_statement(self, p):
        return p[0] + p[2]

    @_('DEF ID macro_params NL line_statements END')
    def macro_def(self, p):
        params = p[2]
        name = (p[1], len(params))
        statements = p[4]
        self.macros[name] = [params, statements]
        return None

    @_('macro_args address')
    def macro_args(self, p):
        return p[0] + [p[1]]

    @_('macro_args DOLLAR')
    def macro_args(self, p):
        return p[0] + [(AddrType.Dollar, '')]

    @_('empty')
    def macro_args(self, p):
        return []

    @_('macro_params ID')
    def macro_params(self, p):
        return p[0] + [p[1]]

    @_('empty')
    def macro_params(self, p):
        return []

    @_('line_statements line_statement')
    def line_statements(self, p):
        return p[0] + p[1]

    @_('empty')
    def line_statements(self, p):
        return []

    @_('labels statement labels NL')
    def line_statement(self, p):
        if p[1]:
            return p[0] + [p[1]] + p[2]
        return p[0] + p[2]

    @_('labels NL')
    def line_statement(self, p):
        return p[0]

    @_('labels label')
    def labels(self, p):
        return p[0] + [p[1]]

    @_('empty')
    def labels(self, p):
        return []

    @_('LPAREN ID RPAREN')
    def label(self, p):
        return OpType.Label, p[1]

    @_('address')
    def statement(self, p):
        return OpType.FlipJump, (p[0], next_address)

    @_('address SC')
    def statement(self, p):
        return OpType.FlipJump, (p[0], next_address)

    @_('address SC address')
    def statement(self, p):
        return OpType.FlipJump, (p[0], p[2])

    @_('SC address')
    def statement(self, p):
        return OpType.FlipJump, (temp_address, p[1])

    @_('SC')
    def statement(self, p):
        return OpType.FlipJump, (temp_address, next_address)

    @_('DOT ID macro_args')
    def statement(self, p):
        return OpType.Macro, ((p[1], len(p[2])), p[2])

    @_('DDPAD NUMBER')
    def statement(self, p):
        return OpType.DDPad, (p[1],)

    @_('DDFLIP_BY address address')
    def statement(self, p):
        return OpType.DDFlipBy, (p[1], p[2])

    @_('DDFLIP_BY_DBIT address address')
    def statement(self, p):
        return OpType.DDFlipByDbit, (p[1], p[2])

    @_('DDVAR NUMBER address')
    def statement(self, p):
        return OpType.DDVar, (p[1], p[2])

    @_('DDOUTPUT NUMBER')
    def statement(self, p):
        return OpType.DDOutput, (p[1] & 0xff,)

    @_('NUMBER HASHTAG address')
    def statement(self, p):
        return OpType.BitSpecific, (p[0], p[2])

    @_('ID ASSIGN address')
    def statement(self, p):
        (base_type, base_value), brackets = p[2]
        if base_type == AddrType.Number:
            self.defs[p[0]] = base_value + brackets
            return None
        error(f'No such variable at file {curr_file} line {p.lineno}:  {base_value}.')

    @_('REP ID ID NL line_statements END')
    def statement(self, p):
        return OpType.Rep, (p[1], p[2], p[4])

    @_('REP ID ID ID macro_args')
    def statement(self, p):
        return OpType.Rep, (p[1], p[2], [(OpType.Macro, ((p[3], len(p[4])), p[4]))])

    @_('base_address address_brackets')     # or maybe just expression? no more [], just +-/*
    def address(self, p):
        return p[0], p[1]

    @_('SKIP_BEFORE NUMBER')
    def base_address(self, p):
        return AddrType.SkipBefore, p[1]

    @_('SKIP_AFTER NUMBER')
    def base_address(self, p):
        return AddrType.SkipAfter, p[1]

    @_('NUMBER')
    def base_address(self, p):
        return AddrType.Number, p[0]

    @_('ID')
    def base_address(self, p):
        if p[0] in self.defs:
            return AddrType.Number, self.defs[p[0]]
        return AddrType.ID, p[0]

    @_('address_brackets address_bracket')
    def address_brackets(self, p):
        return p[0] + p[1]

    @_('empty')
    def address_brackets(self, p):
        return 0

    @_('LBRACKET num_id RBRACKET')
    def address_bracket(self, p):
        return p[1]

    @_('LBRACKET num_id MATH_OP num_id RBRACKET')
    def address_bracket(self, p):
        return p[2](p[1], p[3])

    @_('NUMBER')
    def num_id(self, p):
        return p[0]

    @_('ID')
    def num_id(self, p):
        if p[0] in self.defs:
            return self.defs[p[0]]
        error(f'No such variable at file {curr_file} line {p.lineno}:  {p[0]}.')


def parse(input_files):
    global curr_file
    lexer = CalcLexer()
    parser = CalcParser()
    for curr_file in input_files:
        if not isfile(curr_file):
            error(f"No such file {curr_file}.")
        text = open(curr_file, 'r').read()
        parser.parse(lexer.tokenize(text))

    return parser.macros


if __name__ == '__main__':
    macros = parse(stl(64) + ['tests/testbit.fj'])
    for macro in macros:
        print(f'\n{macro}:\n  ' + '\n  '.join(str(state) for state in macros[macro][1]))

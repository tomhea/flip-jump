from sly import Lexer, Parser
from operator import mul, add, sub, floordiv
from os.path import isfile
from defs import *


global curr_file, curr_text


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
    ID = id_re
    NUMBER = number_re
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

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.macros = {main_macro: [([], []), []]}
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
        name = (p[1], len(params[0]))
        statements = p[4]
        self.macros[name] = [params, statements]
        return None

    @_('addresses address')
    def addresses(self, p):
        return p[0] + [p[1]]

    @_('empty')
    def addresses(self, p):
        return []

    @_('ids')
    def macro_params(self, p):
        return p[0], []

    @_('ids DOLLAR ids')
    def macro_params(self, p):
        return p[0], p[2]

    @_('ids ID')
    def ids(self, p):
        return p[0] + [p[1]]

    @_('empty')
    def ids(self, p):
        return []

    @_('line_statements line_statement')
    def line_statements(self, p):
        if self.verbose:
            print('\n'.join(str(_) for _ in p[1]))
        return p[0] + p[1]

    @_('empty')
    def line_statements(self, p):
        return []

    @_('labels statement labels NL')
    def line_statement(self, p):
        if p[1]:
            if p[1].line is None:
                p[1].line = p.lineno
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
        return Op(OpType.Label, (p[1],), curr_file, p.lineno)

    @_('address')
    def statement(self, p):
        return Op(OpType.FlipJump, (p[0], next_address), curr_file, None)  # FIXME

    @_('address SC')
    def statement(self, p):
        return Op(OpType.FlipJump, (p[0], next_address), curr_file, p.lineno)

    @_('address SC address')
    def statement(self, p):
        return Op(OpType.FlipJump, (p[0], p[2]), curr_file, p.lineno)

    @_('SC address')
    def statement(self, p):
        return Op(OpType.FlipJump, (temp_address, p[1]), curr_file, p.lineno)

    @_('SC')
    def statement(self, p):
        return Op(OpType.FlipJump, (temp_address, next_address), curr_file, p.lineno)

    @_('DOT ID addresses')
    def statement(self, p):
        return Op(OpType.Macro, ((p[1], len(p[2])), *p[2]), curr_file, p.lineno)

    @_('DDPAD NUMBER')
    def statement(self, p):
        return Op(OpType.DDPad, (p[1],), curr_file, p.lineno)

    @_('DDFLIP_BY address address')
    def statement(self, p):
        return Op(OpType.DDFlipBy, (p[1], p[2]), curr_file, p.lineno)

    @_('DDFLIP_BY_DBIT address address')
    def statement(self, p):
        return Op(OpType.DDFlipByDbit, (p[1], p[2]), curr_file, p.lineno)

    @_('DDVAR NUMBER address')
    def statement(self, p):
        return Op(OpType.DDVar, (p[1], p[2]), curr_file, p.lineno)

    @_('DDOUTPUT NUMBER')
    def statement(self, p):
        return Op(OpType.DDOutput, (p[1] & 0xff,), curr_file, p.lineno)

    @_('NUMBER HASHTAG address')
    def statement(self, p):
        return Op(OpType.BitSpecific, (p[0], p[2]), curr_file, p.lineno)

    @_('ID ASSIGN address')
    def statement(self, p):
        if p[2].type == AddrType.Number:
            self.defs[p[0]] = p[2].base + p[2].index
            return None
        error(f'No such variable at file {curr_file} line {p.lineno}:  {p[2].base}.')

    @_('REP address ID NL line_statements END')
    def statement(self, p):
        return Op(OpType.Rep, (p[1], p[2], p[4]), curr_file, p.lineno)

    @_('REP address ID ID addresses')
    def statement(self, p):
        return Op(OpType.Rep, (p[1], p[2],
                               [Op(OpType.Macro, ((p[3], len(p[4])), *p[4]), curr_file, p.lineno)]
                               ), curr_file, p.lineno)

    @_('base_address address_brackets')     # or maybe just expression? no more [], just +-/*
    def address(self, p):
        return Address(*p[0], p[1])

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


def parse_macro_tree(input_files, verbose=False):
    global curr_file, curr_text
    lexer = CalcLexer()
    parser = CalcParser(verbose=verbose)
    for curr_file in input_files:
        if not isfile(curr_file):
            error(f"No such file {curr_file}.")
        curr_text = open(curr_file, 'r').read()
        parser.parse(lexer.tokenize(curr_text))

    return parser.macros


if __name__ == '__main__':
    # for test in ('cat', 'mathbit', 'mathvec', 'ncat', 'not', 'testbit', 'testbit_with_nops'):
    #     parse_macro_tree(stl(64) + [f'tests/{test}.fj'])
    macros = parse_macro_tree(stl(64) + ['tests/testbit.fj'])
    # for macro in macros:
    #     print(f'\n{macro}:\n  ' + '\n  '.join(str(state) for state in macros[macro][1]))

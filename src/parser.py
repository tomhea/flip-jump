from sly import Lexer, Parser
from os.path import isfile
from defs import *


global curr_file, curr_text


class CalcLexer(Lexer):
    tokens = {DEF, END, REP,
              DDPAD, DDFLIP_BY_DBIT, DDFLIP_BY, DDVAR, DDOUTPUT,
              ID, NUMBER, DOLLAR,
              DOT, NL, SC, COLON,
              NEXT, HASHTAG}

    literals = {'=', '+', '-', '*', '/', '(', ')'}

    ignore_ending_comment = r'//.*'
    # ignore_beginning_comment = r'.*:'

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

    COLON = r'\:'

    # Punctuations
    DOT = r'\.'
    NL = r'[\r\n]'
    SC = r';'

    NEXT = r'>'
    HASHTAG = r'#'

    ignore = ' \t'

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
    precedence = (
        ('left', '+', '-'),
        ('left', '*', '/'),
        # ('right', 'UMINUS'),
    )
    debugfile = 'src/parser.out'

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.macros = {main_macro: [([], []), []]}
        self.defs = {}

    def check_params(self, ids, macro_name):
        for id in ids:
            if id in self.defs:
                error(f'parameter {id} in macro {macro_name[0]}({macro_name[1]}) is also defined as a constant variable (with value {self.defs[id]})')
        for i1 in range(len(ids)):
            for i2 in range(i1):
                if ids[i1] == ids[i2]:
                    error(f'parameter {ids[i1]} in macro {macro_name[0]}({macro_name[1]}) is declared twice!')

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

    @_('labels macro_def NL')
    def definable_line_statement(self, p):
        return p[0]

    @_('DEF ID macro_params NL line_statements END')
    def macro_def(self, p):
        params = p[2]
        name = (p[1], len(params[0]))
        self.check_params(params[0] + params[1], name)
        statements = p[4]
        self.macros[name] = [params, statements]
        return None

    # @_('addresses address')
    # def addresses(self, p):
    #     return p[0] + [p[1]]
    #
    # @_('empty')
    # def addresses(self, p):
    #     return []

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

    @_('labels statement NL')
    def line_statement(self, p):
        if p[1]:
            if p[1].line is None:
                p[1].line = p.lineno
            return p[0] + [p[1]]
        return p[0]

    @_('labels NL')
    def line_statement(self, p):
        return p[0]

    @_('labels label')
    def labels(self, p):
        return p[0] + [p[1]]

    @_('empty')
    def labels(self, p):
        return []

    @_('ID COLON')
    def label(self, p):
        return Op(OpType.Label, (p[0],), curr_file, p.lineno)

    @_('expr')
    def statement(self, p):
        return Op(OpType.FlipJump, (p[0], next_address), curr_file, None)  # FIXME

    @_('expr SC')
    def statement(self, p):
        return Op(OpType.FlipJump, (p[0], next_address), curr_file, p.lineno)

    @_('expr SC expr')
    def statement(self, p):
        return Op(OpType.FlipJump, (p[0], p[2]), curr_file, p.lineno)

    @_('SC expr')
    def statement(self, p):
        return Op(OpType.FlipJump, (temp_address, p[1]), curr_file, p.lineno)

    @_('SC')
    def statement(self, p):
        return Op(OpType.FlipJump, (temp_address, next_address), curr_file, p.lineno)

    @_('DOT ID expressions')
    def statement(self, p):
        return Op(OpType.Macro, ((p[1], len(p[2])), *p[2]), curr_file, p.lineno)

    @_('DDPAD expr')
    def statement(self, p):
        return Op(OpType.DDPad, (p[1],), curr_file, p.lineno)

    @_('DDFLIP_BY expr expr')
    def statement(self, p):
        return Op(OpType.DDFlipBy, (p[1], p[2]), curr_file, p.lineno)

    @_('DDFLIP_BY_DBIT expr expr')
    def statement(self, p):
        return Op(OpType.DDFlipByDbit, (p[1], p[2]), curr_file, p.lineno)

    @_('DDVAR expr expr')
    def statement(self, p):
        return Op(OpType.DDVar, (p[1], p[2]), curr_file, p.lineno)

    @_('DDOUTPUT expr')
    def statement(self, p):
        return Op(OpType.DDOutput, (p[1],), curr_file, p.lineno)

    @_('expr HASHTAG expr')
    def statement(self, p):
        return Op(OpType.BitSpecific, (p[0], p[2]), curr_file, p.lineno)

    @_('ID "=" expr')
    def statement(self, p):
        if not p.expr.eval(self.defs, curr_file, p.lineno):
            self.defs[p.ID] = p.expr
            return None
        error(f'Can\'t evaluate expression at file {curr_file} line {p.lineno}:  {str(p.expr)}.')

    @_('REP expr ID NL line_statements END')
    def statement(self, p):
        return Op(OpType.Rep, (p.expr, p.ID, p.line_statements), curr_file, p.lineno)

    @_('REP expr ID ID expressions')
    def statement(self, p):
        exps = p.expressions
        return Op(OpType.Rep,
                  (p.expr, p.ID0, [Op(OpType.Macro, ((p.ID1, len(exps)), *exps), curr_file, p.lineno)]),
                  curr_file, p.lineno)

    # @_('base_address address_brackets')
    # def address(self, p):
    #     return Address(*p[0], p[1])
    #
    # @_('skip_address address_brackets')
    # def address(self, p):
    #     return Address(*p[0], p[1])
    #
    # @_('SKIP_BEFORE base_address')
    # def skip_address(self, p):
    #     if p[1][0] != AddrType.Number:
    #         error("After '<' must be a constant number.")
    #     return AddrType.SkipBefore, p[1][1]
    #
    # @_('NEXT base_address')
    # def skip_address(self, p):
    #     if p[1][0] != AddrType.Number:
    #         error("After '>' must be a constant number.")
    #     return AddrType.SkipAfter, p[1][1]
    #
    # @_('NUMBER')
    # def base_address(self, p):
    #     return AddrType.Number, p[0]
    #
    # @_('ID')
    # def base_address(self, p):
    #     if p[0] in self.defs:
    #         return AddrType.Number, self.defs[p[0]]
    #     return AddrType.ID, p[0]
    #
    # @_('address_brackets address_bracket')
    # def address_brackets(self, p):
    #     return p[0] + p[1]
    #
    # @_('empty')
    # def address_brackets(self, p):
    #     return 0
    #
    # @_('LBRACKET num_id RBRACKET')
    # def address_bracket(self, p):
    #     return p[1]
    #
    # @_('LBRACKET num_id MATH_OP num_id RBRACKET')
    # def address_bracket(self, p):
    #     return p[2](p[1], p[3])
    #
    # @_('NUMBER')
    # def num_id(self, p):
    #     return p[0]
    #
    # @_('ID')
    # def num_id(self, p):
    #     if p[0] in self.defs:
    #         return self.defs[p[0]]
    #     error(f'No such variable at file {curr_file} line {p.lineno}:  {p[0]}.')

    @_('expressions expr')
    def expressions(self, p):
        return p.expressions + [p.expr]

    @_('empty')
    def expressions(self, p):
        return []

    @_('expr "+" expr')
    def expr(self, p):
        return Expr((p.expr0, add, p.expr1))

    @_('expr "-" expr')
    def expr(self, p):
        return Expr((p.expr0, sub, p.expr1))

    @_('expr "*" expr')
    def expr(self, p):
        return Expr((p.expr0, mul, p.expr1))

    @_('expr "/" expr')
    def expr(self, p):
        return Expr((p.expr0, div, p.expr1))

    # # The shift/reduce conflict can be solved using "," between macro arguments.
    # @_('"-" expr %prec UMINUS')
    # def expr(self, p):
    #     return Expr((Expr(0), sub, p.expr))

    @_('"(" expr ")"')
    def expr(self, p):
        return p.expr

    @_('NUMBER')
    def expr(self, p):
        return Expr(p.NUMBER)

    @_('NEXT')
    def expr(self, p):
        return Expr(p.NEXT)

    @_('ID')
    def expr(self, p):
        if p[0] in self.defs:
            return self.defs[p.ID]
        return Expr(p.ID)


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

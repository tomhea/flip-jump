from sly import Lexer, Parser
from enum import Enum


class OpType(Enum):
    FlipJump = 1
    DotMacro = 2
    DotDotMacro = 3
    BitSpecific = 4
    Label = 5


main_macro = ('.__M_a_i_n__', 0)
defs_macro = ('.__D_e_f_s__', 0)


class CalcLexer(Lexer):
    tokens = { ID, NUMBER, PLUS, TIMES, MINUS, DIVIDE, ASSIGN, LPAREN, RPAREN }
    ignore = ' \t'

    DEFS = r'defs'
    DEF = r'def'
    END = r'end'
    REP = r'rep'

    # Tokens
    ID = r'[a-zA-Z_]\w*'
    NUMBER = r'[0-9a-fA-F]+'

    # Special symbols
    PLUS = r'\+'
    MINUS = r'-'
    TIMES = r'\*'
    DIVIDE = r'/'
    ASSIGN = r'='
    LBRACKET = r'\['
    RBRACKET = r'\]'
    LPAREN = r'\('
    RPAREN = r'\)'
    DOT = r'\.'

    DOLLAR = r'\$'
    SKIP = r'[<>]'
    HASHTAG = r'#'

    NL = r'\n'
    SC = r';'

    # Extra action for newlines
    def NL(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        print("Illegal character '%s'" % t.value[0])
        self.index += 1


class CalcParser(Parser):
    tokens = CalcLexer.tokens
    debugfile = 'parser.out'

    precedence = (
        ('left', PLUS, MINUS),
        ('left', TIMES, DIVIDE),
        ('right', UMINUS),
        )

    def __init__(self):
        self.macros = {main_macro: ([], []), defs_macro: ([], [])}
        self.last_def_name = main_macro

    @_('')
    def empty(self, p):
        return None

    @_('program definable_line_statement')
    def program(self, p):
        return p[0] + [p[1]]

    @_('empty')
    def program(self, p):
        return []

    @_('line_statement')
    def definable_line_statement(self, p):
        return p

    @_('labels macro_def labels NL')
    def definable_line_statement(self, p):
        return p[0] + p[2]

    @_('DOT DEF ID macro_params NL line_statements DOT END')
    def macro_def(self, p):
        # TODO add macro definition
        params = p[3]
        name = (p[2].ID, len(params))
        statements = p[5]
        self.macros[name] = (params, statements)
        return None

    @_('macro_params ID')
    def macro_params(self, p):
        return p[0] + [p[1].ID]

    @_('empty')
    def macro_params(self, p):
        return []

    @_('line_statements line_statement')
    def line_statements(self, p):
        return p[0] + [p[1]]

    @_('empty')
    def line_statements(self, p):
        return []

    @_('labels statement labels NL')
    def line_statement(self, p):
        op_list = p[0] + [p[1]] + p[2] if p[1] else p[0] + p[2]
        self.macros[self.last_def_name][1] += op_list
        print(op_list)
        return op_list

    @_('labels label')
    def labels(self, p):
        return p[0] + [p[1]]

    @_('empty')
    def labels(self, p):
        return []

    @_('LPAREN ID RPAREN')
    def label(self, p):
        return OpType.Label, p.ID

    @_('empty')
    def statement(self, p):
        return None

    @_('address')
    def statement(self, p):
        return OpType.FlipJump, (p[0], '>0')

    @_('address SC')
    def statement(self, p):
        return OpType.FlipJump, (p[0], '>0')

    @_('address SC address')
    def statement(self, p):
        return OpType.FlipJump, (p[0], p[2])

    @_('SC address')
    def statement(self, p):
        return OpType.FlipJump, ('temp', p[1])

    @_('SC')
    def statement(self, p):
        return OpType.FlipJump, ('temp', '>0')

    @_('DOT ID macro_params')
    def statement(self, p):
        return OpType.DotMacro, (p[1].ID, p[2])

    @_('DOT DOT ID macro_params')
    def statement(self, p):
        return OpType.DotDotMacro, (p[2].ID, p[3])

    @_('NUMBER HASHTAG address')
    def statement(self, p):
        return OpType.BitSpecific, (p[0], p[2])

    @_('base_address address_brackets')     # or maybe just expression? no more [], just +-/*
    def address(self, p):
        pass    # TODO

    @_('SKIP NUMBER')
    def base_address(self, p):
        pass    # TODO

    @_('NUMBER')
    def base_address(self, p):
        pass  # TODO

    @_('address_brackets address_bracket')
    def address_brackets(self, p):
        return p[0] + [p[1]]

    @_('empty')
    def address_brackets(self, p):
        return []






    # @_('expr')
    # def statement(self, p):
    #     print(p.expr)
    #
    # @_('expr PLUS expr')
    # def expr(self, p):
    #     return p.expr0 + p.expr1
    #
    # @_('expr MINUS expr')
    # def expr(self, p):
    #     return p.expr0 - p.expr1
    #
    # @_('expr TIMES expr')
    # def expr(self, p):
    #     return p.expr0 * p.expr1
    #
    # @_('expr DIVIDE expr')
    # def expr(self, p):
    #     return p.expr0 / p.expr1
    #
    # @_('MINUS expr %prec UMINUS')
    # def expr(self, p):
    #     return -p.expr
    #
    # @_('LPAREN expr RPAREN')
    # def expr(self, p):
    #     return p.expr
    #
    # @_('NUMBER')
    # def expr(self, p):
    #     return int(p.NUMBER)
    #
    # @_('NAME')
    # def expr(self, p):
    #     try:
    #         return self.names[p.NAME]
    #     except LookupError:
    #         print(f'Undefined name {p.NAME!r}')
    #         return 0


if __name__ == '__main__':
    lexer = CalcLexer()
    parser = CalcParser()
    while True:
        try:
            text = input('calc > ')
        except EOFError:
            break
        if text:
            parser.parse(lexer.tokenize(text))

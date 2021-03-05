from sly import Lexer, Parser
from os.path import isfile
from defs import *


global curr_file, curr_text


class CalcLexer(Lexer):
    tokens = {DEF, END, REP,
              DDPAD, DDFLIP_BY_DBIT, DDFLIP_BY, DDVAR, DDOUTPUT,
              DOT_ID, ID, NUMBER, SHL, SHR,
              NL, SC,
              HASHTAG}

    literals = {'=', '+', '-', '*', '/', '%', '(', ')', '$', '^', '|', '&', '?', ':'}

    ignore_ending_comment = r'//.*'
    # ignore_beginning_comment = r'.*:'

    # Tokens
    ID = id_re
    NUMBER = number_re

    DOT_ID = fr'\.({id_re})'
    DOT_ID[r'.def'] = DEF
    DOT_ID[r'.end'] = END
    DOT_ID[r'.rep'] = REP


    DDPAD = r'\.\.pad'
    DDFLIP_BY_DBIT = r'\.\.flip_by_dbit'
    DDFLIP_BY = r'\.\.flip_by'
    DDVAR = r'\.\.var'
    DDOUTPUT = r'\.\.output'

    SHL = r'<<'
    SHR = r'>>'

    # Punctuations
    # DOT = r'\.'
    NL = r'[\r\n]'
    SC = r';'

    HASHTAG = r'#'

    ignore = ' \t'

    def NUMBER(self, t):
        n = t.value
        if len(n) >= 2:
            if n[0] == "'":
                t.value = ord(n[1])
            elif n[1] in 'xX':
                t.value = int(n, 16)
            elif n[1] in 'bB':
                t.value = int(n, 2)
            else:
                t.value = int(n)
        else:
            t.value = int(t.value)
        return t

    def NL(self, t):
        self.lineno += 1
        return t

    def DOT_ID(self, t):
        t.value = t.value[1:]
        return t

    def error(self, t):
        print(f"Lexing Error at file {curr_file} line {self.lineno}: {t.value[0]}")
        self.index += 1


class CalcParser(Parser):
    tokens = CalcLexer.tokens
    precedence = (
        ('right', '?', ':'),
        ('left', '|'),
        ('left', '^'),
        ('left', '&'),
        ('left', SHL, SHR),
        ('left', '+', '-'),
        ('left', '*', '/', '%'),
        # ('right', 'UMINUS'),
    )
    # debugfile = 'src/parser.out'

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
        self.macros[main_macro][1] += p.definable_line_statements

    @_('definable_line_statements NL definable_line_statement')
    def definable_line_statements(self, p):
        if p[2]:
            return p[0] + p[2]
        return p[0]

    @_('definable_line_statement')
    def definable_line_statements(self, p):
        if p[0]:
            return p[0]
        return []

    # @_('empty')
    # def definable_line_statements(self, p):
    #     return []

    @_('')
    def empty(self, p):
        return None

    @_('line_statement')
    def definable_line_statement(self, p):
        return p.line_statement

    @_('labels macro_def')
    def definable_line_statement(self, p):
        return p.labels

    @_('DEF ID macro_params line_statements NL END')
    def macro_def(self, p):
        params = p.macro_params
        name = (p.ID, len(params[0]))
        self.check_params(params[0] + params[1], name)
        statements = p.line_statements
        self.macros[name] = [params, statements]
        return None

    @_('ids')
    def macro_params(self, p):
        return p.ids, []

    @_('ids ":" ids')
    def macro_params(self, p):
        return p.ids0, p.ids1

    @_('ids ID')
    def ids(self, p):
        return p.ids + [p.ID]

    @_('empty')
    def ids(self, p):
        return []

    @_('line_statements NL line_statement')
    def line_statements(self, p):
        if self.verbose:
            print('\n'.join(str(_) for _ in p.line_statement))
        return p.line_statements + p.line_statement

    @_('empty')
    def line_statements(self, p):
        return []

    @_('labels statement')
    def line_statement(self, p):
        if p.statement:
            return p.labels + [p.statement]
        return p.labels

    @_('labels')
    def line_statement(self, p):
        return p.labels

    @_('labels label')
    def labels(self, p):
        return p.labels + [p.label]

    @_('empty')
    def labels(self, p):
        return []

    @_('ID ":"')
    def label(self, p):
        return Op(OpType.Label, (p.ID,), curr_file, p.lineno)

    @_('_expr')
    def statement(self, p):
        expr, line = p._expr
        return Op(OpType.FlipJump, (expr, next_address()), curr_file, line)

    @_('expr SC')
    def statement(self, p):
        return Op(OpType.FlipJump, (p.expr, next_address()), curr_file, p.lineno)

    @_('expr SC expr')
    def statement(self, p):
        return Op(OpType.FlipJump, (p.expr0, p.expr1), curr_file, p.lineno)

    @_('SC expr')
    def statement(self, p):
        return Op(OpType.FlipJump, (temp_address(), p.expr), curr_file, p.lineno)

    @_('SC')
    def statement(self, p):
        return Op(OpType.FlipJump, (temp_address(), next_address()), curr_file, p.lineno)

    @_('DOT_ID expressions')
    def statement(self, p):
        return Op(OpType.Macro, ((p.DOT_ID, len(p.expressions)), *p.expressions), curr_file, p.lineno)

    @_('DDPAD expr')
    def statement(self, p):
        return Op(OpType.DDPad, (p.expr,), curr_file, p.lineno)

    @_('DDFLIP_BY expr expr')
    def statement(self, p):
        return Op(OpType.DDFlipBy, (p.expr0, p.expr1), curr_file, p.lineno)

    @_('DDFLIP_BY_DBIT expr expr')
    def statement(self, p):
        return Op(OpType.DDFlipByDbit, (p.expr0, p.expr1), curr_file, p.lineno)

    @_('DDVAR expr expr')
    def statement(self, p):
        return Op(OpType.DDVar, (p.expr0, p.expr1), curr_file, p.lineno)

    @_('DDOUTPUT expr')
    def statement(self, p):
        return Op(OpType.DDOutput, (p.expr,), curr_file, p.lineno)

    @_('expr HASHTAG expr')
    def statement(self, p):
        return Op(OpType.BitSpecific, (p.expr0, p.expr1), curr_file, p.lineno)

    @_('ID "=" expr')
    def statement(self, p):
        if not p.expr.eval(self.defs, curr_file, p.lineno):
            self.defs[p.ID] = p.expr
            return None
        error(f'Can\'t evaluate expression at file {curr_file} line {p.lineno}:  {str(p.expr)}.')

    @_('REP expr ID line_statements NL END')
    def statement(self, p):
        return Op(OpType.Rep, (p.expr, p.ID, p.line_statements), curr_file, p.lineno)

    @_('REP expr ID ID expressions')
    def statement(self, p):
        exps = p.expressions
        return Op(OpType.Rep,
                  (p.expr, p.ID0, [Op(OpType.Macro, ((p.ID1, len(exps)), *exps), curr_file, p.lineno)]),
                  curr_file, p.lineno)

    @_('expressions expr')
    def expressions(self, p):
        return p.expressions + [p.expr]

    @_('empty')
    def expressions(self, p):
        return []

    @_('_expr')
    def expr(self, p):
        return p._expr[0]

    @_('_expr "+" _expr')
    def _expr(self, p):
        return Expr((add, (p._expr0[0], p._expr1[0]))), p.lineno

    @_('_expr "-" _expr')
    def _expr(self, p):
        return Expr((sub, (p._expr0[0], p._expr1[0]))), p.lineno

    @_('_expr "*" _expr')
    def _expr(self, p):
        return Expr((mul, (p._expr0[0], p._expr1[0]))), p.lineno

    @_('_expr "/" _expr')
    def _expr(self, p):
        return Expr((floordiv, (p._expr0[0], p._expr1[0]))), p.lineno

    @_('_expr "%" _expr')
    def _expr(self, p):
        return Expr((mod, (p._expr0[0], p._expr1[0]))), p.lineno

    @_('_expr SHL _expr')
    def _expr(self, p):
        return Expr((lshift, (p._expr0[0], p._expr1[0]))), p.lineno

    @_('_expr SHR _expr')
    def _expr(self, p):
        return Expr((rshift, (p._expr0[0], p._expr1[0]))), p.lineno

    @_('_expr "^" _expr')
    def _expr(self, p):
        return Expr((xor, (p._expr0[0], p._expr1[0]))), p.lineno

    @_('_expr "|" _expr')
    def _expr(self, p):
        return Expr((or_, (p._expr0[0], p._expr1[0]))), p.lineno

    @_('_expr "&" _expr')
    def _expr(self, p):
        return Expr((and_, (p._expr0[0], p._expr1[0]))), p.lineno

    @_('_expr "?" _expr ":" _expr')
    def _expr(self, p):
        return Expr((lambda a, b, c: b if a else c, (p._expr0[0], p._expr1[0], p._expr2[0]))), p.lineno

    # # The shift/reduce conflict can be solved using "," between macro arguments.
    # @_('"-" expr %prec UMINUS')
    # def expr(self, p):
    #     return Expr((Expr(0), sub, p.expr))

    @_('"(" _expr ")"')
    def _expr(self, p):
        return p._expr

    @_('NUMBER')
    def _expr(self, p):
        return Expr(p.NUMBER), p.lineno

    @_('"$"')
    def _expr(self, p):
        return Expr('$'), p.lineno

    @_('ID')
    def _expr(self, p):
        if p.ID in self.defs:
            return self.defs[p.ID], p.lineno
        return Expr(p.ID), p.lineno


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

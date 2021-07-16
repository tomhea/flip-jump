from sly import Lexer, Parser
from os.path import isfile
from operator import mul, add, sub, floordiv, lshift, rshift, mod, xor, or_, and_
from defs import *


global curr_file, curr_text, error_occurred, curr_namespace, reserved_names


def syntax_error(line, msg=''):
    global error_occurred
    error_occurred = True
    print()
    if msg:
        print(f"Syntax Error in file {curr_file} line {line}:")
        print(f"  {msg}")
    else:
        print(f"Syntax Error in file {curr_file} line {line}")


class FJLexer(Lexer):
    tokens = {NS, DEF, REP,
              WFLIP, SEGMENT, RESERVE,
              ID, DOT_ID, NUMBER, STRING,
              LE, GE, EQ, NEQ,
              SHL, SHR,
              NL, SC}

    literals = {'=', '+', '-', '*', '/', '%',
                '(', ')',
                '$',
                '^', '|', '&',
                '?', ':',
                '<', '>'
                '"',
                '#',
                '{', '}',
                "@", ","}

    ignore_ending_comment = r'//.*'

    # Tokens
    DOT_ID = dot_id_re
    ID = id_re
    NUMBER = number_re
    STRING = string_re

    ID[r'def'] = DEF
    ID[r'rep'] = REP
    ID[r'ns'] = NS

    ID[r'wflip'] = WFLIP

    ID[r'segment'] = SEGMENT
    ID[r'reserve'] = RESERVE

    global reserved_names
    reserved_names = {DEF, REP, NS, WFLIP, SEGMENT, RESERVE}

    LE = "<="
    GE = ">="

    EQ = "=="
    NEQ = "!="

    SHL = r'<<'
    SHR = r'>>'

    # Punctuations
    NL = r'[\r\n]'
    SC = r';'

    ignore = ' \t'

    def NUMBER(self, t):
        n = t.value
        if len(n) >= 2:
            if n[0] == "'":
                t.value = handle_char(n[1:-1])[0]
            elif n[1] in 'xX':
                t.value = int(n, 16)
            elif n[1] in 'bB':
                t.value = int(n, 2)
            else:
                t.value = int(n)
        else:
            t.value = int(t.value)
        return t

    def STRING(self, t):
        chars = []
        s = t.value[1:-1]
        i = 0
        while i < len(s):
            val, length = handle_char(s[i:])
            chars.append(val)
            i += length
        t.value = sum(val << (i*8) for i, val in enumerate(chars))
        return t

    def NL(self, t):
        self.lineno += 1
        return t

    def error(self, t):
        global error_occurred
        error_occurred = True
        print()
        print(f"Lexing Error in file {curr_file} line {self.lineno}: {t.value[0]}")
        self.index += 1


class FJParser(Parser):
    tokens = FJLexer.tokens
    # TODO add Unary Minus (-), Unary Not (~). Maybe add logical or (||) and logical and (&&).
    precedence = (
        ('right', '?', ':'),
        ('left', '|'),
        ('left', '^'),
        ('nonassoc', '<', '>', LE, GE),
        ('left', EQ, NEQ),
        ('left', '&'),
        ('left', SHL, SHR),
        ('left', '+', '-'),
        ('left', '*', '/', '%'),
        ('right', '#'),
    )
    # debugfile = 'src/parser.out'

    def __init__(self, w, verbose=False):
        self.verbose = verbose
        self.defs = {'w': Expr(w)}

        # [(params, quiet_params), statements, (curr_file, p.lineno, ns_name)]
        self.macros = {main_macro: [([], []), [], (None, None, '')]}

    def check_macro_name(self, name, line):
        global reserved_names
        base_name = self.ns_to_base_name(name[0])
        if base_name in reserved_names:
            syntax_error(line, f'macro name can\'t be {name[0]} ({base_name} is a reserved name)!')
        if name in self.macros:
            _, _, (other_file, other_line, _) = self.macros[name]
            syntax_error(line, f'macro {name} is declared twice! '
                               f'also declared in file {other_file} (line {other_file}).')

    def check_params(self, ids, macro_name, line):
        for id in ids:
            if id in self.defs:
                syntax_error(line, f'parameter {id} in macro {macro_name[0]}({macro_name[1]}) '
                                   f'is also defined as a constant variable (with value {self.defs[id]})')
        for i1 in range(len(ids)):
            for i2 in range(i1):
                if ids[i1] == ids[i2]:
                    syntax_error(line, f'parameter {ids[i1]} in macro {macro_name[0]}({macro_name[1]}) '
                                       f'is declared twice!')

    def ns_name(self):
        return '.'.join(curr_namespace)

    def ns_full_name(self, base_name):
        return '.'.join(curr_namespace + [base_name])

    def dot_id_to_ns_full_name(self, p):
        base_name = p.DOT_ID
        without_dots = base_name.lstrip('.')
        if len(without_dots) == len(base_name):

            return base_name
        num_of_dots = len(base_name) - len(without_dots)
        if num_of_dots - 1 > len(curr_namespace):
            syntax_error(p.lineno, f'Used more leading dots than current namespace depth '
                                   f'({num_of_dots}-1 > {len(curr_namespace)})')
        return '.'.join(curr_namespace[:len(curr_namespace)-(num_of_dots-1)] + [without_dots])

    def ns_to_base_name(self, name):
        return name.split('.')[-1]

    def error(self, token):
        global error_occurred
        error_occurred = True
        print()
        print(f'Syntax Error in file {curr_file} line {token.lineno}, token=("{token.type}", {token.value})')

    @_('definable_line_statements')
    def program(self, p):
        self.macros[main_macro][1] += p.definable_line_statements

    @_('definable_line_statements NL definable_line_statement')
    def definable_line_statements(self, p):
        if p.definable_line_statement:
            return p.definable_line_statements + p.definable_line_statement
        return p.definable_line_statements

    @_('definable_line_statement')
    def definable_line_statements(self, p):
        if p.definable_line_statement:
            return p.definable_line_statement
        return []

    @_('')
    def empty(self, p):
        return None

    @_('line_statement')
    def definable_line_statement(self, p):
        return p.line_statement

    @_('macro_def')
    def definable_line_statement(self, p):
        return []

    @_('NS ID')
    def namespace(self, p):
        curr_namespace.append(p.ID)

    @_('namespace "{" NL definable_line_statements NL "}"')
    def definable_line_statement(self, p):
        curr_namespace.pop()
        return p.definable_line_statements

    @_('DEF ID macro_params "{" NL line_statements NL "}"')
    def macro_def(self, p):
        params = p.macro_params
        name = (self.ns_full_name(p.ID), len(params[0]))
        self.check_macro_name(name, p.lineno)
        self.check_params(params[0] + params[1], name, p.lineno)
        statements = p.line_statements
        self.macros[name] = [params, statements, (curr_file, p.lineno, self.ns_name())]
        return None

    @_('empty')
    def macro_params(self, p):
        return [], []

    @_('ids')
    def macro_params(self, p):
        return p.ids, []

    @_('"@" ids')
    def macro_params(self, p):
        return [], p.ids

    @_('ids "@" ids')
    def macro_params(self, p):
        return p.ids0, p.ids1

    @_('ids "," ID')
    def ids(self, p):
        return p.ids + [p.ID]

    @_('ID')
    def ids(self, p):
        return [p.ID]

    @_('line_statements NL line_statement')
    def line_statements(self, p):
        return p.line_statements + p.line_statement

    @_('line_statement')
    def line_statements(self, p):
        return p.line_statement

    # @_('empty')
    # def line_statements(self, p):
    #     return []

    @_('empty')
    def line_statement(self, p):
        return []

    @_('statement')
    def line_statement(self, p):
        if p.statement:
            return [p.statement]
        return []

    @_('label statement')
    def line_statement(self, p):
        if p.statement:
            return [p.label, p.statement]
        return [p.label]

    @_('label')
    def line_statement(self, p):
        return [p.label]

    @_('ID ":"')
    def label(self, p):
        return Op(OpType.Label, (self.ns_full_name(p.ID),), curr_file, p.lineno)

    @_('expr SC')
    def statement(self, p):
        return Op(OpType.FlipJump, (p.expr, next_address()), curr_file, p.lineno)

    @_('expr SC expr')
    def statement(self, p):
        return Op(OpType.FlipJump, (p.expr0, p.expr1), curr_file, p.lineno)

    @_('SC expr')
    def statement(self, p):
        return Op(OpType.FlipJump, (Expr(0), p.expr), curr_file, p.lineno)

    @_('SC')
    def statement(self, p):
        return Op(OpType.FlipJump, (Expr(0), next_address()), curr_file, p.lineno)

    @_('ID')
    def id(self, p):
        return p.ID, p.lineno

    @_('DOT_ID')
    def id(self, p):
        return self.dot_id_to_ns_full_name(p), p.lineno

    @_('id')
    def statement(self, p):
        macro_name, lineno = p.id
        return Op(OpType.Macro, ((macro_name, 0), ), curr_file, lineno)

    @_('id expressions')
    def statement(self, p):
        macro_name, lineno = p.id
        return Op(OpType.Macro, ((macro_name, len(p.expressions)), *p.expressions), curr_file, lineno)

    @_('WFLIP expr "," expr')
    def statement(self, p):
        return Op(OpType.WordFlip, (p.expr0, p.expr1), curr_file, p.lineno)

    @_('ID "=" expr')
    def statement(self, p):
        name = self.ns_full_name(p.ID)
        if name in self.defs:
            syntax_error(p.lineno, f'Can\'t redeclare the variable "{name}".')
        if not p.expr.eval(self.defs, curr_file, p.lineno):
            self.defs[name] = p.expr
            return None
        syntax_error(p.lineno, f'Can\'t evaluate expression:  {str(p.expr)}.')

    @_('REP "(" expr "," ID ")" id')
    def statement(self, p):
        id, lineno = p.id
        return Op(OpType.Rep,
                  (p.expr, p.ID, Op(OpType.Macro, ((id, 0), ), curr_file, lineno)),
                  curr_file, p.lineno)

    @_('REP "(" expr "," ID ")" id expressions')
    def statement(self, p):
        exps = p.expressions
        id, lineno = p.id
        return Op(OpType.Rep,
                  (p.expr, p.ID, Op(OpType.Macro, ((id, len(exps)), *exps), curr_file, lineno)),
                  curr_file, p.lineno)

    @_('SEGMENT expr')
    def statement(self, p):
        return Op(OpType.Segment, (p.expr,), curr_file, p.lineno)

    @_('RESERVE expr')
    def statement(self, p):
        return Op(OpType.Reserve, (p.expr,), curr_file, p.lineno)

    @_('expressions "," expr')
    def expressions(self, p):
        return p.expressions + [p.expr]

    @_('expr')
    def expressions(self, p):
        return [p.expr]

    @_('_expr')
    def expr(self, p):
        return p._expr[0]

    @_('_expr "+" _expr')
    def _expr(self, p):
        return Expr((add, (p._expr0[0], p._expr1[0]))), p.lineno

    @_('_expr "-" _expr')
    def _expr(self, p):
        return Expr((sub, (p._expr0[0], p._expr1[0]))), p.lineno

    @_('"(" "-" _expr ")"')
    def _expr(self, p):
        return Expr((sub, (Expr(0), p._expr[0]))), p.lineno

    @_('_expr "*" _expr')
    def _expr(self, p):
        return Expr((mul, (p._expr0[0], p._expr1[0]))), p.lineno

    @_('"#" _expr')
    def _expr(self, p):
        return Expr((lambda x: x.bit_length(), (p._expr[0],))), p.lineno

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

    @_('_expr "<" _expr')
    def _expr(self, p):
        return Expr((lambda a, b: 1 if a < b else 0, (p._expr0[0], p._expr1[0]))), p.lineno

    @_('_expr ">" _expr')
    def _expr(self, p):
        return Expr((lambda a, b: 1 if a > b else 0, (p._expr0[0], p._expr1[0]))), p.lineno

    @_('_expr LE _expr')
    def _expr(self, p):
        return Expr((lambda a, b: 1 if a <= b else 0, (p._expr0[0], p._expr1[0]))), p.lineno

    @_('_expr GE _expr')
    def _expr(self, p):
        return Expr((lambda a, b: 1 if a >= b else 0, (p._expr0[0], p._expr1[0]))), p.lineno

    @_('_expr EQ _expr')
    def _expr(self, p):
        return Expr((lambda a, b: 1 if a == b else 0, (p._expr0[0], p._expr1[0]))), p.lineno

    @_('_expr NEQ _expr')
    def _expr(self, p):
        return Expr((lambda a, b: 1 if a != b else 0, (p._expr0[0], p._expr1[0]))), p.lineno

    @_('"(" _expr ")"')
    def _expr(self, p):
        return p._expr

    @_('NUMBER')
    def _expr(self, p):
        return Expr(p.NUMBER), p.lineno

    @_('STRING')
    def _expr(self, p):
        return Expr(p.STRING), p.lineno

    @_('"$"')
    def _expr(self, p):
        return Expr('$'), p.lineno

    @_('id')
    def _expr(self, p):
        id, lineno = p.id
        if id in self.defs:
            return self.defs[id], lineno
        return Expr(id), lineno


def exit_if_errors():
    if error_occurred:
        print()
        print(f'Errors found in file {curr_file}. Assembly stopped.')
        exit(1)


def parse_macro_tree(input_files, w, verbose=False):
    global curr_file, curr_text, error_occurred, curr_namespace
    error_occurred = False

    lexer = FJLexer()
    parser = FJParser(w, verbose=verbose)
    for curr_file in input_files:
        if not isfile(curr_file):
            error(f"No such file {curr_file}.")
        curr_text = open(curr_file, 'r').read()
        curr_namespace = []
        lex_res = lexer.tokenize(curr_text)
        exit_if_errors()
        parser.parse(lex_res)
        exit_if_errors()

    return parser.macros

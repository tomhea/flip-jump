from os import path
from pathlib import Path
from typing import Set, List, Tuple, Dict, Union

import sly
from sly.lex import Token
from sly.yacc import YaccProduction as ParsedRule

from flipjump.utils.exceptions import FlipJumpExprException, FlipJumpParsingException
from flipjump.assembler.inner_classes.expr import Expr, get_minimized_expr
from flipjump.assembler.inner_classes.ops import get_used_labels, get_declared_labels, \
    CodePosition, MacroName, Op, Macro, initial_macro_name, \
    MacroCall, RepCall, FlipJump, WordFlip, Label, Segment, Reserve, Pad

global curr_file, curr_file_short_name, curr_text, error_occurred, all_errors, curr_namespace


def get_position(lineno: int) -> CodePosition:
    return CodePosition(curr_file, curr_file_short_name, lineno)


def syntax_error(lineno: int, msg='') -> None:
    global error_occurred, all_errors
    error_occurred = True
    curr_position = get_position(lineno)

    if msg:
        error_string = f"Syntax Error in {curr_position}:\n  {msg}"
    else:
        error_string = f"Syntax Error in {curr_position}"
    all_errors += f"{error_string}\n"

    print(error_string)


def syntax_warning(line: int, is_error: bool, msg: str = '') -> None:
    error_string = f"Syntax Warning in file {curr_file}"
    if line is not None:
        error_string += f" line {line}"
    if msg:
        error_string += f":\n  {msg}"

    if is_error:
        global error_occurred, all_errors
        error_occurred = True
        all_errors += f"{error_string}\n"

    print(error_string)


# Regex for the parser

id_re = r'[a-zA-Z_][a-zA-Z_0-9]*'
dot_id_re = fr'(({id_re})|\.*)?(\.({id_re}))+'

bin_num = r'0[bB][01]+'
hex_num = r'0[xX][0-9a-fA-F]+'
dec_num = r'[0-9]+'

char_escape_dict = {'0': 0x0, 'a': 0x7, 'b': 0x8, 'e': 0x1b, 'f': 0xc, 'n': 0xa, 'r': 0xd, 't': 0x9, 'v': 0xb,
                    '\\': 0x5c, "'": 0x27, '"': 0x22, '?': 0x3f}
escape_chars = ''.join(k for k in char_escape_dict)
char = fr'[ -~]|\\[{escape_chars}]|\\[xX][0-9a-fA-F]{{2}}'

number_re = fr"({bin_num})|({hex_num})|('({char})')|({dec_num})"
string_re = fr'"({char})*"'


def get_char_value_and_length(s: str) -> Tuple[int, int]:
    if s[0] != '\\':
        return ord(s[0]), 1
    if s[1] in char_escape_dict:
        return char_escape_dict[s[1]], 2
    return int(s[2:4], 16), 4


# noinspection PyUnboundLocalVariable,PyRedeclaration
class FJLexer(sly.Lexer):
    # noinspection PyUnresolvedReferences
    tokens = {NS, DEF, REP,
              WFLIP, PAD, SEGMENT, RESERVE,
              ID, DOT_ID, NUMBER, STRING,
              LE, GE, EQ, NEQ,
              SHL, SHR,
              NL, SC}

    literals = {'=', '+', '-', '*', '/', '%',
                '(', ')',
                '$',
                '^', '|', '&',
                '?', ':',
                '<', '>',
                '"',
                '#',
                '{', '}',
                "@", ","}

    ignore_ending_comment = r'//.*'
    ignore_line_continuation = r'\\[ \t]*\n'

    # Tokens
    DOT_ID = dot_id_re
    ID = id_re
    NUMBER = number_re
    STRING = string_re

    # noinspection PyUnresolvedReferences
    ID[r'def'] = DEF
    # noinspection PyUnresolvedReferences
    ID[r'rep'] = REP
    # noinspection PyUnresolvedReferences
    ID[r'ns'] = NS

    # noinspection PyUnresolvedReferences
    ID[r'wflip'] = WFLIP
    # noinspection PyUnresolvedReferences
    ID[r'pad'] = PAD

    # noinspection PyUnresolvedReferences
    ID[r'segment'] = SEGMENT
    # noinspection PyUnresolvedReferences
    ID[r'reserve'] = RESERVE

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

    # noinspection PyTypeChecker
    def NUMBER(self, t: Token) -> Token:
        n = t.value
        if len(n) >= 2:
            # noinspection PyUnresolvedReferences
            if n[0] == "'":
                t.value = get_char_value_and_length(n[1:-1])[0]
            elif n[1] in 'xX':
                t.value = int(n, 16)
            elif n[1] in 'bB':
                t.value = int(n, 2)
            else:
                t.value = int(n)
        else:
            t.value = int(t.value)
        return t

    def STRING(self, t: Token) -> Token:
        chars = []
        s = t.value[1:-1]
        i = 0
        while i < len(s):
            val, length = get_char_value_and_length(s[i:])
            chars.append(val)
            i += length
        t.value = sum(val << (i*8) for i, val in enumerate(chars))
        return t

    def NL(self, t: Token) -> Token:
        self.lineno += 1
        return t

    def error(self, t: Token) -> None:
        global error_occurred, all_errors
        error_occurred = True

        error_string = f"Lexing Error in {get_position(self.lineno)}: {t.value[0]}"
        all_errors += f"{error_string}\n"
        print(error_string)

        self.index += 1


def next_address() -> Expr:
    return Expr('$')


# noinspection PyUnusedLocal,PyUnresolvedReferences
class FJParser(sly.Parser):
    tokens = FJLexer.tokens
    # TODO add Unary Minus (-), Unary Not (~). Maybe add logical or (||) and logical and (&&). Maybe handle power (**).
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

    def __init__(self, memory_width: int, warning_as_errors: bool):
        self.consts: Dict[str, Expr] = {'w': Expr(memory_width)}
        self.warning_as_errors: bool = warning_as_errors
        self.macros: Dict[MacroName, Macro] = {initial_macro_name: Macro([], [], [], '', None)}

    def validate_free_macro_name(self, name: MacroName, lineno: int) -> None:
        if name in self.macros:
            syntax_error(lineno, f'macro {name} is declared twice! '
                                 f'also declared in {self.macros[name].code_position}.')

    def validate_params(self, ids: List[str], macro_name: MacroName, lineno: int) -> None:
        for param_id in ids:
            if param_id in self.consts:
                syntax_error(lineno, f'parameter {param_id} in macro {macro_name}) '
                                     f'is also defined as a constant variable (with value {self.consts[param_id]})')
        seen_ids = set()
        for _id in ids:
            if _id in seen_ids:
                syntax_error(lineno, f'parameter {_id} in macro {macro_name}) is declared twice!')
            else:
                seen_ids.add(_id)

    def validate_label_usage(self, labels_used: Set[str], labels_declared: Set[str],
                             regular_labels: Set[str], extern_labels: Set[str], global_labels: Set[str],
                             lineno: int, macro_name: MacroName) -> None:
        self.validate_labels_groups(extern_labels, global_labels, regular_labels, lineno, macro_name)

        self.validate_no_unused_labels(regular_labels, global_labels, labels_declared, labels_used, lineno, macro_name)
        self.validate_no_unknown_label_uses(regular_labels, global_labels, labels_declared, labels_used,
                                            lineno, macro_name)
        self.validate_no_bad_label_declarations(regular_labels, extern_labels, labels_declared, lineno, macro_name)
        self.validate_all_extern_labels_are_declared(extern_labels, labels_declared, lineno, macro_name)

    @staticmethod
    def validate_labels_groups(extern_labels: Set[str], global_labels: Set[str], regular_labels: Set[str],
                               lineno: int, macro_name: MacroName) -> None:
        if global_labels & extern_labels:
            syntax_error(lineno, f"In macro {macro_name}:  "
                                 f"extern labels can't be global labels: " + ', '.join(global_labels & extern_labels))
        if global_labels & regular_labels:
            syntax_error(lineno, f"In macro {macro_name}:  "
                                 f"extern labels can't be regular labels: " + ', '.join(global_labels & regular_labels))
        if extern_labels & regular_labels:
            syntax_error(lineno, f"In macro {macro_name}:  "
                                 f"global labels can't be regular labels: " + ', '.join(extern_labels & regular_labels))

    def validate_no_unused_labels(self, regular_labels: Set[str], global_labels: Set[str],
                                  labels_declared: Set[str], labels_used: Set[str],
                                  lineno: int, macro_name: MacroName) -> None:
        unused_labels = regular_labels.union(global_labels) - \
                        labels_used.union(self.to_base_name(label) for label in labels_declared)
        if unused_labels:
            syntax_warning(lineno, self.warning_as_errors,
                           f"In macro {macro_name}:  "
                           f"unused labels: {', '.join(unused_labels)}.")

    def validate_all_extern_labels_are_declared(self, extern_labels: Set[str], labels_declared: Set[str],
                                                lineno: int, macro_name: MacroName) -> None:
        unused_labels = extern_labels - {self.to_base_name(label) for label in labels_declared}
        if unused_labels:
            syntax_warning(lineno, self.warning_as_errors,
                           f"In macro {macro_name}:  "
                           f"undeclared extern label: {', '.join(unused_labels)}.")

    def validate_no_bad_label_declarations(self, regular_labels: Set[str], extern_labels: Set[str],
                                           labels_declared: Set[str],
                                           lineno: int, macro_name: MacroName) -> None:
        bad_declarations = labels_declared - set(
            self.ns_full_name(label) for label in extern_labels.union(regular_labels))
        if bad_declarations:
            syntax_warning(lineno, self.warning_as_errors,
                           f"In macro {macro_name}:  "
                           f"Declared a not extern/parameter label: {', '.join(bad_declarations)}.")

    def validate_no_unknown_label_uses(self, regular_labels: Set[str], global_labels: Set[str],
                                       labels_declared: Set[str], labels_used: Set[str],
                                       lineno: int, macro_name: MacroName) -> None:
        bad_uses = labels_used - global_labels - regular_labels - set(labels_declared) - {'$'}
        if bad_uses:
            syntax_warning(lineno, self.warning_as_errors,
                           f"In macro {macro_name}:  "
                           f"Used a not global/parameter/declared-extern label: {', '.join(bad_uses)}.")

    @staticmethod
    def validate_no_segment_or_reserve(ops: List[Op], macro_name: MacroName) -> None:
        for op in ops:
            if isinstance(op, Segment):
                syntax_error(op.code_position.line, f"segment can't be declared inside a macro ({macro_name}).")
            if isinstance(op, Reserve):
                syntax_error(op.code_position.line, f"reserve can't be declared inside a macro ({macro_name}).")

    def validate_macro_declaration(self, name: MacroName, ops: List[Op], lineno: int,
                                   params: List[str], local_params: List[str],
                                   global_params: Set[str], extern_params: Set[str]) -> None:
        self.validate_free_macro_name(name, lineno)

        regular_params = params + local_params
        self.validate_params(regular_params, name, lineno)
        self.validate_label_usage(get_used_labels(ops), get_declared_labels(ops),
                                  set(regular_params), set(extern_params), set(global_params),
                                  lineno, name)

        self.validate_no_segment_or_reserve(ops, name)

    @staticmethod
    def ns_name() -> str:
        return '.'.join(curr_namespace)

    @staticmethod
    def ns_full_name(base_name: str) -> str:
        return '.'.join(curr_namespace + [base_name])

    @staticmethod
    def base_name_to_ns_full_name(base_name: str, lineno: int) -> str:
        without_dots = base_name.lstrip('.')
        if len(without_dots) == len(base_name):
            return base_name

        num_of_dots = len(base_name) - len(without_dots)
        if num_of_dots - 1 > len(curr_namespace):
            syntax_error(lineno, f'Used more leading dots than current namespace depth '
                                 f'({num_of_dots}-1 > {len(curr_namespace)})')

        return '.'.join(curr_namespace[:len(curr_namespace)-(num_of_dots-1)] + [without_dots])

    @staticmethod
    def to_base_name(name: str) -> str:
        return name.split('.')[-1]

    def error(self, token: Token) -> None:
        global error_occurred, all_errors
        error_occurred = True

        if token is None:
            error_string = f'Syntax Error in {get_position(self.line_position(None))}. ' \
                           f'Maybe missing }} or {{ before this line?'
        else:
            error_string = f'Syntax Error in {get_position(token.lineno)}, token=("{token.type}", {token.value})'

        all_errors += f"{error_string}\n"
        print(error_string)

    # Parsing Rules:

    @_('definable_line_statements')
    def program(self, p: ParsedRule) -> None:
        ops = p.definable_line_statements
        self.macros[initial_macro_name].ops += ops

    # noinspection PyUnresolvedReferences
    @_('definable_line_statements NL definable_line_statement')
    def definable_line_statements(self, p: ParsedRule) -> List[Op]:
        if p.definable_line_statement:
            p.definable_line_statements.extend(p.definable_line_statement)
        return p.definable_line_statements

    @_('definable_line_statement')
    def definable_line_statements(self, p: ParsedRule) -> List[Op]:
        if p.definable_line_statement:
            return p.definable_line_statement
        return []

    @_('')
    def empty(self, p: ParsedRule) -> None:
        return None

    @_('line_statement')
    def definable_line_statement(self, p: ParsedRule) -> List[Op]:
        return p.line_statement

    @_('macro_def')
    def definable_line_statement(self, p: ParsedRule) -> List[Op]:
        return []

    @_('NS ID')
    def namespace(self, p: ParsedRule) -> None:
        curr_namespace.append(p.ID)

    @_('namespace "{" NL definable_line_statements NL "}"')
    def definable_line_statement(self, p: ParsedRule) -> List[Op]:
        curr_namespace.pop()
        return p.definable_line_statements

    @_('DEF ID macro_params "{" NL line_statements NL "}"')
    def macro_def(self, p: ParsedRule) -> None:
        params, local_params, global_params, extern_params = p.macro_params
        name = MacroName(self.ns_full_name(p.ID), len(params))
        ops = p.line_statements

        self.validate_macro_declaration(name, ops, p.lineno, params, local_params, global_params, extern_params)

        self.macros[name] = Macro(params, local_params, ops, self.ns_name(), get_position(p.lineno))
        return None

    @_('empty')
    def maybe_ids(self, p: ParsedRule) -> List[str]:
        return []

    @_('IDs')
    def maybe_ids(self, p: ParsedRule) -> List[str]:
        return p.IDs

    @_('empty')
    def maybe_local_ids(self, p: ParsedRule) -> List[str]:
        return []

    @_('"@" IDs')
    def maybe_local_ids(self, p: ParsedRule) -> List[str]:
        return p.IDs

    @_('empty')
    def maybe_global_ids(self, p: ParsedRule) -> List[str]:
        return []

    @_('"<" ids')
    def maybe_global_ids(self, p: ParsedRule) -> List[str]:
        return p.ids

    @_('empty')
    def maybe_extern_ids(self, p: ParsedRule) -> List[str]:
        return []

    @_('">" IDs')
    def maybe_extern_ids(self, p: ParsedRule) -> List[str]:
        return p.IDs

    @_('maybe_ids maybe_local_ids maybe_global_ids maybe_extern_ids')
    def macro_params(self, p: ParsedRule) -> Tuple[List[str], List[str], List[str], List[str]]:
        return p.maybe_ids, p.maybe_local_ids, p.maybe_global_ids, p.maybe_extern_ids

    @_('IDs "," ID')
    def IDs(self, p: ParsedRule) -> List[str]:
        return p.IDs + [p.ID]

    @_('ID')
    def IDs(self, p: ParsedRule) -> List[str]:
        return [p.ID]

    @_('line_statements NL line_statement')
    def line_statements(self, p: ParsedRule) -> List[Op]:
        p.line_statements.extend(p.line_statement)
        return p.line_statements

    @_('line_statement')
    def line_statements(self, p: ParsedRule) -> List[Op]:
        return p.line_statement

    # @_('empty')
    # def line_statements(self, p: ParsedRule) -> List[Op]:
    #     return []

    @_('empty')
    def line_statement(self, p: ParsedRule) -> List[Op]:
        return []

    @_('statement')
    def line_statement(self, p: ParsedRule) -> List[Op]:
        if p.statement:
            return [p.statement]
        return []

    @_('label statement')
    def line_statement(self, p: ParsedRule) -> List[Op]:
        if p.statement:
            return [p.label, p.statement]
        return [p.label]

    @_('label')
    def line_statement(self, p: ParsedRule) -> List[Op]:
        return [p.label]

    @_('ID ":"')
    def label(self, p: ParsedRule) -> Label:
        return Label(self.ns_full_name(p.ID), get_position(p.lineno))

    @_('expr SC')
    def statement(self, p: ParsedRule) -> FlipJump:
        return FlipJump(p.expr, next_address(), get_position(p.lineno))

    @_('expr SC expr')
    def statement(self, p: ParsedRule) -> FlipJump:
        return FlipJump(p.expr0, p.expr1, get_position(p.lineno))

    @_('SC expr')
    def statement(self, p: ParsedRule) -> FlipJump:
        return FlipJump(Expr(0), p.expr, get_position(p.lineno))

    @_('SC')
    def statement(self, p: ParsedRule) -> FlipJump:
        return FlipJump(Expr(0), next_address(), get_position(p.lineno))

    @_('ID')
    def id(self, p: ParsedRule) -> Tuple[str, int]:
        return p.ID, p.lineno

    @_('DOT_ID')
    def id(self, p: ParsedRule) -> Tuple[str, int]:
        return self.base_name_to_ns_full_name(p.DOT_ID, p.lineno), p.lineno

    @_('ids "," id')
    def ids(self, p: ParsedRule) -> List[str]:
        return p.ids + [p.id[0]]

    @_('id')
    def ids(self, p: ParsedRule) -> List[str]:
        return [p.id[0]]

    @_('id')
    def statement(self, p: ParsedRule) -> MacroCall:
        macro_name, lineno = p.id
        return MacroCall(macro_name, [], get_position(lineno))

    @_('id expressions')
    def statement(self, p: ParsedRule) -> MacroCall:
        macro_name, lineno = p.id
        return MacroCall(macro_name, p.expressions, get_position(lineno))

    @_('WFLIP expr "," expr')
    def statement(self, p: ParsedRule) -> WordFlip:
        return WordFlip(p.expr0, p.expr1, next_address(), get_position(p.lineno))

    @_('WFLIP expr "," expr "," expr')
    def statement(self, p: ParsedRule) -> WordFlip:
        return WordFlip(p.expr0, p.expr1, p.expr2, get_position(p.lineno))

    @_('PAD expr')
    def statement(self, p: ParsedRule) -> Pad:
        return Pad(p.expr, get_position(p.lineno))

    @_('ID "=" expr')
    def statement(self, p: ParsedRule) -> None:
        name = self.ns_full_name(p.ID)
        if name in self.consts:
            syntax_error(p.lineno, f'Can\'t redeclare the variable "{name}".')

        evaluated = p.expr.eval_new(self.consts)
        try:
            self.consts[name] = Expr(int(evaluated))
        except FlipJumpExprException:
            syntax_error(p.lineno, f'Can\'t evaluate expression:  {str(evaluated)}.')

    @_('REP "(" expr "," ID ")" id')
    def statement(self, p: ParsedRule) -> RepCall:
        macro_name, lineno = p.id
        code_position = get_position(lineno)
        return RepCall(p.expr, p.ID, macro_name, [], code_position)

    @_('REP "(" expr "," ID ")" id expressions')
    def statement(self, p: ParsedRule) -> RepCall:
        macro_name, lineno = p.id
        code_position = get_position(lineno)
        return RepCall(p.expr, p.ID, macro_name, p.expressions, code_position)

    @_('SEGMENT expr')
    def statement(self, p: ParsedRule) -> Segment:
        return Segment(p.expr, get_position(p.lineno))

    @_('RESERVE expr')
    def statement(self, p: ParsedRule) -> Reserve:
        return Reserve(p.expr, get_position(p.lineno))

    @_('expressions "," expr')
    def expressions(self, p: ParsedRule) -> List[Expr]:
        return p.expressions + [p.expr]

    @_('expr')
    def expressions(self, p: ParsedRule) -> List[Expr]:
        return [p.expr]

    @_('expr_')
    def expr(self, p: ParsedRule) -> Expr:
        return p.expr_[0]

    @_('expr_ "+" expr_')
    def expr_(self, p: ParsedRule) -> Tuple[Expr, int]:
        return get_minimized_expr('+', (p.expr_0[0], p.expr_1[0])), p.lineno

    @_('expr_ "-" expr_')
    def expr_(self, p: ParsedRule) -> Tuple[Expr, int]:
        return get_minimized_expr('-', (p.expr_0[0], p.expr_1[0])), p.lineno

    @_('expr_ "*" expr_')
    def expr_(self, p: ParsedRule) -> Tuple[Expr, int]:
        return get_minimized_expr('*', (p.expr_0[0], p.expr_1[0])), p.lineno

    @_('"#" expr_')
    def expr_(self, p: ParsedRule) -> Tuple[Expr, int]:
        return get_minimized_expr('#', (p.expr_[0],)), p.lineno

    @_('expr_ "/" expr_')
    def expr_(self, p: ParsedRule) -> Tuple[Expr, int]:
        return get_minimized_expr('/', (p.expr_0[0], p.expr_1[0])), p.lineno

    @_('expr_ "%" expr_')
    def expr_(self, p: ParsedRule) -> Tuple[Expr, int]:
        return get_minimized_expr('%', (p.expr_0[0], p.expr_1[0])), p.lineno

    @_('expr_ SHL expr_')
    def expr_(self, p: ParsedRule) -> Tuple[Expr, int]:
        return get_minimized_expr('<<', (p.expr_0[0], p.expr_1[0])), p.lineno

    @_('expr_ SHR expr_')
    def expr_(self, p: ParsedRule) -> Tuple[Expr, int]:
        return get_minimized_expr('>>', (p.expr_0[0], p.expr_1[0])), p.lineno

    @_('expr_ "^" expr_')
    def expr_(self, p: ParsedRule) -> Tuple[Expr, int]:
        return get_minimized_expr('^', (p.expr_0[0], p.expr_1[0])), p.lineno

    @_('expr_ "|" expr_')
    def expr_(self, p: ParsedRule) -> Tuple[Expr, int]:
        return get_minimized_expr('|', (p.expr_0[0], p.expr_1[0])), p.lineno

    @_('expr_ "&" expr_')
    def expr_(self, p: ParsedRule) -> Tuple[Expr, int]:
        return get_minimized_expr('&', (p.expr_0[0], p.expr_1[0])), p.lineno

    @_('expr_ "?" expr_ ":" expr_')
    def expr_(self, p: ParsedRule) -> Tuple[Expr, int]:
        return get_minimized_expr('?:', (p.expr_0[0], p.expr_1[0], p.expr_2[0])), p.lineno

    @_('expr_ "<" expr_')
    def expr_(self, p: ParsedRule) -> Tuple[Expr, int]:
        return get_minimized_expr('<', (p.expr_0[0], p.expr_1[0])), p.lineno

    @_('expr_ ">" expr_')
    def expr_(self, p: ParsedRule) -> Tuple[Expr, int]:
        return get_minimized_expr('>', (p.expr_0[0], p.expr_1[0])), p.lineno

    @_('expr_ LE expr_')
    def expr_(self, p: ParsedRule) -> Tuple[Expr, int]:
        return get_minimized_expr('<=', (p.expr_0[0], p.expr_1[0])), p.lineno

    @_('expr_ GE expr_')
    def expr_(self, p: ParsedRule) -> Tuple[Expr, int]:
        return get_minimized_expr('>=', (p.expr_0[0], p.expr_1[0])), p.lineno

    @_('expr_ EQ expr_')
    def expr_(self, p: ParsedRule) -> Tuple[Expr, int]:
        return get_minimized_expr('==', (p.expr_0[0], p.expr_1[0])), p.lineno

    @_('expr_ NEQ expr_')
    def expr_(self, p: ParsedRule) -> Tuple[Expr, int]:
        return get_minimized_expr('!=', (p.expr_0[0], p.expr_1[0])), p.lineno

    @_('"(" expr_ ")"')
    def expr_(self, p: ParsedRule) -> Tuple[Expr, int]:
        return p.expr_

    @_('NUMBER')
    def expr_(self, p: ParsedRule) -> Tuple[Expr, int]:
        return Expr(p.NUMBER), p.lineno

    @_('STRING')
    def expr_(self, p: ParsedRule) -> Tuple[Expr, int]:
        return Expr(p.STRING), p.lineno

    @_('"$"')
    def expr_(self, p: ParsedRule) -> Tuple[Expr, int]:
        return next_address(), p.lineno

    @_('id')
    def expr_(self, p: ParsedRule) -> Tuple[Expr, int]:
        id_str, lineno = p.id
        if id_str in self.consts:
            return self.consts[id_str], lineno
        return Expr(id_str), lineno


def exit_if_errors() -> None:
    if error_occurred:
        raise FlipJumpParsingException(f'Errors found in file {curr_file}. Assembly stopped.\n\nThe Errors:\n{all_errors}')


def validate_current_file(files_seen: Set[Union[str, Path]]) -> None:
    if not path.isfile(curr_file):
        raise FlipJumpParsingException(f"No such file {curr_file}.")

    if curr_file_short_name in files_seen:
        raise FlipJumpParsingException(f"Short file name is repeated: '{curr_file_short_name}'.")

    abs_path = curr_file.absolute()
    if abs_path in files_seen:
        raise FlipJumpParsingException(f".fj file path is repeated: '{abs_path}'.")

    files_seen.add(curr_file_short_name)
    files_seen.add(abs_path)


def lex_parse_curr_file(lexer: FJLexer, parser: FJParser) -> None:
    global curr_text, curr_namespace
    curr_text = curr_file.open('r').read()
    curr_namespace = []

    lex_res = lexer.tokenize(curr_text)
    exit_if_errors()

    parser.parse(lex_res)
    exit_if_errors()


def parse_macro_tree(input_files: List[Tuple[str, Path]], memory_width: int, warning_as_errors: bool) \
        -> Dict[MacroName, Macro]:
    """
    parse the .fj files and create a macro-dictionary.
    The files will be parsed as if they were concatenated.
    @param input_files:[in]: a list of (short_file_name, fj_file_path). The files will to be parsed in that given order.
    @param memory_width:[in]: the memory-width
    @param warning_as_errors:[in]: treat warnings as errors (stop execution on warnings)
    @return: the macro-dictionary.
    """
    global curr_file, curr_file_short_name, error_occurred, all_errors
    error_occurred = False
    all_errors = ''

    files_seen: Set[Union[str, Path]] = set()

    lexer = FJLexer()
    parser = FJParser(memory_width, warning_as_errors)

    for curr_file_short_name, curr_file in input_files:
        validate_current_file(files_seen)
        lex_parse_curr_file(lexer, parser)

    return parser.macros

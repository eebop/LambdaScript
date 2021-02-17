from sly import Lexer, Parser
import atexit
import os
import readline
import re
import sys
import py_interface
from py_interface import Cancel
STATIC = [
'if',
'then',
'else',
]

def completer(text, state):
    all = STATIC + list(parser.names.keys())
    returns = [x+" " for x in all if x.startswith(text)] + [None]
    return returns[state]

histfile = os.path.join(os.path.expanduser("~"), ".lbd_hist")
try:
    readline.read_history_file(histfile)
except FileNotFoundError:
    os.system(os.path.join('touch ~', '.lbd_hist'))
readline.parse_and_bind("tab: complete")
readline.set_history_length(1000)
readline.set_completer(completer)

class CalcLexer(Lexer):
    tokens = {IF, THEN, ELSE, NAME, NUMBER, PLUS, TIMES, MINUS, DIVIDE, ASSIGN, COLONASSIGN, LPAREN, RPAREN, COMMA, EXPONENT, LBRACKET, RBRACKET, EQUALEQUAL, COMMENT, NEWLINE, STRING, LCURLYBRACE, RCURLYBRACE, GREATERTHEN, LESSTHEN, NOT, MOD, SEMI}
    ignore = ' \t'



    # Tokens
    IF = 'if'
    THEN = 'then'
    ELSE = 'else'
    # WHILE = 'while'
    # DO = 'do'

    NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
    NUMBER = r'[\d.]+'

    # Special symbols
    EQUALEQUAL = '=='
    PLUS = r'\+'
    MINUS = r'-'
    TIMES = r'\*'
    DIVIDE = r'/'
    ASSIGN = r'='
    LPAREN = r'\('
    RPAREN = r'\)'
    EXPONENT = r'\^'
    COMMA = r','
    COLONASSIGN = r':='
    LBRACKET = r'\['
    RBRACKET = r'\]'
    COMMENT = r'#.*'
    STRING = r"""('[^']+')|("[^"]+")"""
    LCURLYBRACE = r'{'
    RCURLYBRACE = r'}'
    GREATERTHEN = r'>'
    LESSTHEN = r'<'
    NOT = '!'
    MOD = '%'
    SEMI = ';'



    NEWLINE = r'\n+'


    def error(self, t):
        print("Illegal character '%s'" % t.value[0])
        self.index += 1



class CalcParser(Parser):
    #debugfile = 'parser.out'
    tokens = CalcLexer.tokens


    precedence = (
        ('left', ASSIGN, COLONASSIGN),
        ('left', EQUALEQUAL, NOT),
        ('left', PLUS, MINUS),
        ('left', TIMES, DIVIDE, MOD),
        ('left', EXPONENT),
        ('left', LPAREN, RPAREN),
        ('left', GREATERTHEN, LESSTHEN),
        ('left', IF, THEN, ELSE),
        ('right', UMINUS, UPLUS),
        ('left', NEWLINE, SEMI),

        )

    def __init__(self, txt='', args=()):
        self.names = {'import': py_interface.import_LScript(('name',)), 'exec_py': py_interface.Exec(('code', 'namespace')), 'print':py_interface.print_obj(('object',)), 'input':py_interface.get_input(('object',))}
        self.text = txt
        self.args = args

    @_('expr')
    def statement(self, p):
        if type(p.expr) == float:
            if int(p.expr) == p.expr:
                self.names['_'] = int(p.expr)
                return int(p.expr)
        self.names['_'] = p.expr
        return p.expr

    @_('statement COMMENT')
    def statement(self, p):
        return p.statement

    @_('')
    def statement(self, p):
        pass

    @_('statement NEWLINE statement')
    def statement(self, p):
        return p.statement1

    def call(self, name, functioncall=()):
        try:
            return name.run({**self.names, **{x:y for x, y in zip(name.args, functioncall + (((None,) * (len(name.args) - len(functioncall))) if (len(name.args) > len(functioncall)) else ()))}})
        except AttributeError:
            raise
            print(f'{name!r} is not callable')
            raise Cancel
        except LookupError:
            print(f'Undefined name {name!r}')
            raise Cancel

    @_('expr SEMI expr')
    def expr(self, p):
        return p.expr1

    @_('expr GREATERTHEN expr')
    def expr(self, p):
        try:
            return int(p.expr0 > p.expr1)
        except TypeError:
            print('Invalid comparison')
            raise Cancel


    @_('expr LESSTHEN expr')
    def expr(self, p):
        try:
            return int(p.expr0 < p.expr1)
        except TypeError:
            print('Invalid comparison')
            raise Cancel

    @_('expr GREATERTHEN ASSIGN expr')
    def expr(self, p):
        try:
            return int(p.expr0 >= p.expr1)
        except TypeError:
            print('Invalid comparison')
            raise Cancel

    @_('expr LESSTHEN ASSIGN expr')
    def expr(self, p):
        try:
            return int(p.expr0 <= p.expr1)
        except TypeError:
            print('Invalid comparison')
            raise Cancel

    @_('expr NOT ASSIGN expr')
    def expr(self, p):
        try:
            return int(p.expr0 != p.expr1)
        except TypeError:
            print('Invalid comparison')
            raise Cancel


    @_('expr MOD expr')
    def expr(self, p):
        try:
            return int(p.expr0 % p.expr1)
        except TypeError:
            print('Invalid comparison')
            raise Cancel

    # @_('LIMPORT expr RIMPORT')
    # def expr(self, p):
    #     var = int(p.expr) if (type(p.expr) == float) and (int(p.expr) == p.expr) else p.expr
    #     answer = str(var) + '.lbd'
    #     try:
    #         with open(answer) as f:
    #             text = f.read()
    #         if text[-1] == '\n':
    #             text = text[:-1]
    #         name = CalcParser(text)
    #         answer = self.call(name, ())
    #         self.names.update(name.names)
    #         return answer
    #     except FileNotFoundError:
    #         print('cannot find file %s' % answer)
    #         raise Cancel

    @_('')
    def dot_star(self, p):
        return ''

    def add_string(self, main, add, spacer=True):
        answer = str(main) + str(add).strip()
        if answer and answer[-1] != ' ' and spacer:
            answer = answer + ' '
        return answer

    @_('LCURLYBRACE dot_star anything_dot_star RCURLYBRACE')
    def anything(self, p):
        answer = '{ '
        answer = self.add_string(answer, p.dot_star)
        answer = self.add_string(answer, p.anything_dot_star)
        answer = answer + '}'
        return answer

    @_('anything dot_star anything_dot_star')
    def anything_dot_star(self, p):
        answer = self.add_string('', p.anything)
        answer = self.add_string(answer, p.dot_star)
        answer = self.add_string(answer, p.anything_dot_star, False)
        return answer

    @_('')
    def anything_dot_star(self, p):
        return ''

    @_('expr EQUALEQUAL expr')
    def expr(self, p):
        return float(p.expr0 == p.expr1)

    @_('IF anything THEN anything ELSE anything')
    def if_statement(self, p):
        if self.call(CalcParser(p.anything0[1:-1]), ()):
            return self.call(CalcParser(p.anything1[1:-1]), ())
        else:
            return self.call(CalcParser(p.anything2[1:-1]), ())





    @_('STRING')
    def expr(self, p):
        return p.STRING[1:-1].replace('\\n', '\n')


    @_('if_statement')
    def expr(self, p):
        return p.if_statement

    @_('anything')
    def expr(self, p):
        return CalcParser(p.anything[1:-1])

    @_('NAME functioncalldefine ASSIGN anything')
    def expr(self, p):
        self.names[p.NAME] = CalcParser(p.anything[1:-1], p.functioncalldefine)

    @_('NAME functioncalldefine COLONASSIGN anything')
    def expr(self, p):
        self.names[p.NAME] = CalcParser(p.anything[1:-1], p.functioncalldefine)
        return self.names[p.NAME]

    @_('expr functioncall')
    def expr(self, p):
        return self.call(p.expr, p.functioncall)

    @_('NAME ASSIGN expr')
    def expr(self, p):
        self.names[p.NAME] = p.expr

    @_('NAME COLONASSIGN expr')
    def expr(self, p):
        self.names[p.NAME] = p.expr
        return p.expr

    @_('expr PLUS expr')
    def expr(self, p):
        return p.expr0 + p.expr1

    @_('expr MINUS expr')
    def expr(self, p):
        return p.expr0 - p.expr1

    @_('expr TIMES expr')
    def expr(self, p):
        return p.expr0 * p.expr1

    @_('expr DIVIDE expr')
    def expr(self, p):
        return p.expr0 / p.expr1

    @_('expr EXPONENT expr')
    def expr(self, p):
        return p.expr0 ** p.expr1

    @_('MINUS expr %prec UMINUS')
    def expr(self, p):
        return -p.expr

    @_('PLUS expr %prec UPLUS')
    def expr(self, p):
        return p.expr

    @_('LPAREN expr RPAREN')
    def expr(self, p):
        return p.expr

    @_('NUMBER')
    def expr(self, p):
        return float(p.NUMBER)

    @_('LBRACKET RBRACKET')
    def functioncalldefine(self, p):
        return ()

    @_('LBRACKET argsdefine RBRACKET')
    def functioncalldefine(self, p):
        return p.argsdefine

    @_('NAME remainingargsdefine')
    def argsdefine(self, p):
        return (p.NAME, *p.remainingargsdefine)

    @_('COMMA NAME remainingargsdefine')
    def remainingargsdefine(self, p):
        return (p.NAME, *p.remainingargsdefine)

    @_('')
    def remainingargsdefine(self, p):
        return ()

    @_('LPAREN RPAREN')
    def functioncall(self, p):
        return ()

    @_('LPAREN args RPAREN')
    def functioncall(self, p):
        return p.args

    @_('expr remainingargs')
    def args(self, p):
        return (p.expr, *p.remainingargs)

    @_('COMMA expr remainingargs')
    def remainingargs(self, p):
        return (p.expr, *p.remainingargs)

    @_('')
    def remainingargs(self, p):
        return ()

    @_('LBRACKET args RBRACKET')
    def expr(self, p):
        return py_interface.callable_list(p.args)

    @_('LBRACKET RBRACKET')
    def expr(self, p):
        return py_interface.callable_list([])


    @_('NAME')
    def expr(self, p):
        return self.get_name(p.NAME)

    def get_name(self, name):
        try:
            return self.names[name]
        except LookupError:
            print(f'Undefined name {name!r}')
            raise Cancel

    def run(self, names):
        self.names = names
        return self.parse(lexer.tokenize(self.text))

    def __str__(self):
        args = str(list(self.args)).replace("'", "")
        text = '{' + self.text + '}'
        return f'lambda{args} = ' + text

    def __repr__(self):
        return str(self)

    def __add__(self, other):
        print('Illegal operation on a lambda')
        raise Cancel

    def __sub__(self, other):
        print('Illegal operation on a lambda')
        raise Cancel

    def __truediv__(self, other):
        print('Illegal operation on a lambda')
        raise Cancel

    def __mul__(self, other):
        print('Illegal operation on a lambda')
        raise Cancel

    def __radd__(self, other):
        print('Illegal operation on a lambda')
        raise Cancel

    def __rsub__(self, other):
        print('Illegal operation on a lambda')
        raise Cancel

    def __rtruediv__(self, other):
        print('Illegal operation on a lambda')
        raise Cancel

    def __rmul__(self, other):
        print('Illegal operation on a lambda')
        raise Cancel

    # forced

    @_('LPAREN dot_star')
    def dot_star(self, p):
        if p.dot_star:
            return p.LPAREN + ' ' + p.dot_star
        else:
            return p.LPAREN

    @_('PLUS dot_star')
    def dot_star(self, p):
        if p.dot_star:
            return p.PLUS + ' ' + p.dot_star
        else:
            return p.PLUS

    @_('LBRACKET dot_star')
    def dot_star(self, p):
        if p.dot_star:
            return p.LBRACKET + ' ' + p.dot_star
        else:
            return p.LBRACKET

    @_('COMMA dot_star')
    def dot_star(self, p):
        if p.dot_star:
            return p.COMMA + ' ' + p.dot_star
        else:
            return p.COMMA

    @_('COLONASSIGN dot_star')
    def dot_star(self, p):
        if p.dot_star:
            return p.COLONASSIGN + ' ' + p.dot_star
        else:
            return p.COLONASSIGN

    @_('EXPONENT dot_star')
    def dot_star(self, p):
        if p.dot_star:
            return p.EXPONENT + ' ' + p.dot_star
        else:
            return p.EXPONENT

    @_('ASSIGN dot_star')
    def dot_star(self, p):
        if p.dot_star:
            return p.ASSIGN + ' ' + p.dot_star
        else:
            return p.ASSIGN

    @_('TIMES dot_star')
    def dot_star(self, p):
        if p.dot_star:
            return p.TIMES + ' ' + p.dot_star
        else:
            return p.TIMES

    @_('RBRACKET dot_star')
    def dot_star(self, p):
        if p.dot_star:
            return p.RBRACKET + ' ' + p.dot_star
        else:
            return p.RBRACKET

    @_('EQUALEQUAL dot_star')
    def dot_star(self, p):
        if p.dot_star:
            return p.EQUALEQUAL + ' ' + p.dot_star
        else:
            return p.EQUALEQUAL

    @_('RPAREN dot_star')
    def dot_star(self, p):
        if p.dot_star:
            return p.RPAREN + ' ' + p.dot_star
        else:
            return p.RPAREN

    @_('NAME dot_star')
    def dot_star(self, p):
        if p.dot_star:
            return p.NAME + ' ' + p.dot_star
        else:
            return p.NAME

    @_('IF dot_star')
    def dot_star(self, p):
        if p.dot_star:
            return p.IF + ' ' + p.dot_star
        else:
            return p.IF

    @_('STRING dot_star')
    def dot_star(self, p):
        if p.dot_star:
            return p.STRING + ' ' + p.dot_star
        else:
            return p.STRING

    @_('COMMENT dot_star')
    def dot_star(self, p):
        if p.dot_star:
            return p.COMMENT + ' ' + p.dot_star
        else:
            return p.COMMENT

    @_('DIVIDE dot_star')
    def dot_star(self, p):
        if p.dot_star:
            return p.DIVIDE + ' ' + p.dot_star
        else:
            return p.DIVIDE


    @_('NEWLINE dot_star')
    def dot_star(self, p):
        if p.dot_star:
            return p.NEWLINE + ' ' + p.dot_star
        else:
            return p.NEWLINE

    @_('NUMBER dot_star')
    def dot_star(self, p):
        if p.dot_star:
            return p.NUMBER + ' ' + p.dot_star
        else:
            return p.NUMBER

    @_('MINUS dot_star')
    def dot_star(self, p):
        if p.dot_star:
            return p.MINUS + ' ' + p.dot_star
        else:
            return p.MINUS

    @_('THEN dot_star')
    def dot_star(self, p):
        if p.dot_star:
            return p.THEN + ' ' + p.dot_star
        else:
            return p.THEN

    @_('ELSE dot_star')
    def dot_star(self, p):
        if p.dot_star:
            return p.ELSE + ' ' + p.dot_star
        else:
            return p.ELSE


    @_('GREATERTHEN dot_star')
    def dot_star(self, p):
        if p.dot_star:
            return p.GREATERTHEN + ' ' + p.dot_star
        else:
            return p.GREATERTHEN

    @_('LESSTHEN dot_star')
    def dot_star(self, p):
        if p.dot_star:
            return p.LESSTHEN + ' ' + p.dot_star
        else:
            return p.LESSTHEN

    @_('NOT dot_star')
    def dot_star(self, p):
        if p.dot_star:
            return p.NOT + ' ' + p.dot_star
        else:
            return p.NOT

    @_('MOD dot_star')
    def dot_star(self, p):
        if p.dot_star:
            return p.MOD + ' ' + p.dot_star
        else:
            return p.MOD

    @_('SEMI dot_star')
    def dot_star(self, p):
        if p.dot_star:
            return p.SEMI + ' ' + p.dot_star
        else:
            return p.SEMI


    # @_('DO dot_star')
    # def dot_star(self, p):
    #     if p.dot_star:
    #         return p.DO + ' ' + p.dot_star
    #     else:
    #         return p.DO
    #
    # @_('WHILE dot_star')
    # def dot_star(self, p):
    #     if p.dot_star:
    #         return p.WHILE + ' ' + p.dot_star
    #     else:
    #         return p.WHILE


def command_line():
    while True:
        try:
            text = input('>> ')
            code = re.sub("'.*'", "", text)
            while code.count('{') != code.count('}'):
                text = text + '\n' + input('.. ')
                code = re.sub("'.*'", "", text)
        except (EOFError, KeyboardInterrupt):
            print()
            break
        try:
            l = lexer.tokenize(text)
            #print(list(l))
            answer = parser.parse(l)

        except Cancel:
            pass
        else:
            if answer != None:
                print(repr(answer))
    atexit.register(readline.write_history_file, histfile)


lexer = CalcLexer()
parser = CalcParser()
#parser.parse(lexer.tokenize("<'" + os.path.join(os.path.dirname(__file__), "__autoimport__'>")))
args = sys.argv[1:]
options = sum([x[1:] for x in args if x.startswith('-') and not x.startswith('--')])
files = [x for x in args if not x.startswith('-')]
if files:
    with open(files[0], 'r') as f:
        text = f.read()
    if text[-1] == '\n':
        text = text[:-1]
    try:
        parser.parse(lexer.tokenize(text))
    except Cancel:
        pass
else:
    command_line()

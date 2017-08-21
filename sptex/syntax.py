import math
import re
from util import *

OUTPUT_EXTENSION = '.tex'
MAIN_KEYWORD = 'SP'

global_data = {}

class LineProcessor:
    def process_line(self, line):
        return line

class Replace(LineProcessor):
    def __init__(self, pattern, replacement):
        LineProcessor.__init__(self)

        self.pattern = pattern
        self.replacement = replacement
    
    def process_line(self, line):
        return re.sub(self.pattern, self.replacement, line)

class EXEC_ENGINE:
    _current = None
    _cleared_globals = None
    def __init__(self):
        # self.locals = {}
        self._cur_indent = ''
        pass
    
    def _exec(var, expr, indent = ''):
        var._return_string = ''
        var._cur_indent = indent
        # _env = {}
        # dict_concat(var.locals, _env)
        # dict_concat(locals(), _env)
        
        #  exec(expr, None, _env)
        exec(expr)
        
        return var._return_string.split('\n')
        
    def _eval(var, expr):
        # _env = {}
        # dict_concat(var.locals, _env)
        # dict_concat(locals(), _env)
        
        # return eval(expr, None, _env)
        return eval(expr)
        
    def get_current():
        if EXEC_ENGINE._current == None:
            EXEC_ENGINE._cleared_globals = globals()
            EXEC_ENGINE._current = EXEC_ENGINE()
        
        return EXEC_ENGINE._current
    
    def _reset():
        EXEC_ENGINE._current = None
        if EXEC_ENGINE._cleared_globals != None:
            cur_globals = globals()
            cur_globals.clear()
            dict_concat(EXEC_ENGINE._cleared_globals, cur_globals)
    
    def _add_env(self, key, value):
        # self.locals[key] = value
        globals()[key] = value

def put(string):
    var = EXEC_ENGINE.get_current()
    if len(var._return_string) == 0 or var._return_string.endswith('\n'):
        var._return_string += var._cur_indent
        
    var._return_string += str(string)
    
def put_line(line):
    put(line)
    put('\n')
    
def put_lines(lines):
    for line in lines:
        put_line(line)
    
def SP(expr = ''):
    if len(expr) == 0:
        return 'SP'
    
    return str(EXEC_ENGINE.get_current()._eval(expr))

class SP_EX:
    def run(self, lines):
        first_indentation = get_indentation(lines[0])
        lines[0] = lines[0].lstrip()
        align_indentation(lines, 1, len(lines))
        return_lines = EXEC_ENGINE.get_current()._exec('\n'.join(lines), first_indentation)
        return return_lines

class SP_SAVE:
    def __init__(self, var_name):
        self.var_name = var_name
        
    def run(self, lines):
        new = []
        for line in lines:
            new.append('\'' + escape_script_string(line) + '\'')
        
        EXEC_ENGINE.get_current()._exec('var.' + self.var_name + '=[' + ','.join(new) + ']')
        
        return lines

class SP_DEF:
    def run(self, lines):
        lines[0] = lines[0].lstrip()
        func_name = lines[0][:skip_word_char(lines[0], 0)]
        lines[0] = 'def ' + lines[0]
        if not lines[0].endswith(':'):
            lines[0] += ':'
        
        align_indentation(lines, 0, len(lines))
        lines.append('EXEC_ENGINE.get_current()._add_env(\'%s\', %s)' % (func_name, func_name))
        #  lines.append('var.%s = %s' % (func_name, func_name))
        EXEC_ENGINE.get_current()._exec('\n'.join(lines))
        return []

class SP_CLASS:
    def run(self, lines):
        lines[0] = lines[0].lstrip()
        class_name = lines[0][:skip_word_char(lines[0], 0)]
        lines[0] = 'class ' + lines[0]
        if not lines[0].endswith(':'):
            lines[0] += ':'
        
        align_indentation(lines, 0, len(lines))
        lines.append('EXEC_ENGINE.get_current()._add_env(\'%s\', %s)' % (class_name, class_name))
        #  lines.append('var.%s = %s' % (class_name, class_name))
        EXEC_ENGINE.get_current()._exec('\n'.join(lines))
        return []

SHORTCUT_LIST = [
    # <= and >=
    Replace(r'<=', r'\\leq'),
    Replace(r'>=', r'\\geq'),
    
    # approximate equal
    Replace(r'~=', r'\\approx'),
    
    # ~
    Replace(r'~', r'\\sim'),
    
    # ^* asterisk
    Replace(r'\^\*', r'^\\ast'),
    
    # * multiply
    Replace(r'\*', r'\\cdot'),
    
    # ...
    Replace(r'\.\.\.', r'\\hdots'),
    
    # nCk combination
    Replace(r'(\b\w+|\{[^\{\}]*\})C(\w+\b|\{[^\{\}]*\})', r'\\binom{\1}{\2}'),
    
    # {a}/{b} fraction
    Replace(r'(\b\w+|\{[^\{\}]*\})\s*/\s*(\w+\b|\{[^\{\}]*\})', r'\\frac{\1}{\2}'),
    
    # infinity
    Replace(r'\b(?:infty|inf|infinity)\b', r'\\infty'),
    
    # integrate from a to b of f(x) dx
    Replace(r'\b(?:integral|int|integrate)\s+(?:from\s+)?(.*?)\s+to\s+(.*?)\s+of\b', r'\\int_{\1}^{\2}'),
    
    # evaluated at a
    Replace(r'\b(?:eval|evaluated?)\s+at\b', r'\\Big|_'),
    
    # evaluated from a to b
    Replace(r'\b(?:eval|evaluated?)\s+(?:from\s+)?(.*?)\s+to\b', r'\\Big|_{\1}^'),
    
    # sum from i = a to b of f(x)
    Replace(r'\bsum\s+(?:from\s+)?(.*?)\s+to\s+(.*?)\s+of\b', r'\\sum_{\1}^{\2}'),
    
    # limit at x to infinity of f(x)
    Replace(r'\b(?:limit|lim)\s+(?:at\s+)(.*?)\s+to\s+(.*?)\s+of\b', r'\\lim_{\1 \\to \2}'),
]

#  from config import CUSTOM_SHORTCUT_LIST
#  SHORTCUT_LIST += CUSTOM_SHORTCUT_LIST

class SP_SC:
    def run(self, lines):
        for i in range(len(lines)):
            for syntax in SHORTCUT_LIST:
                lines[i] = syntax.process_line(lines[i])
        
        return lines

class SP_ENV:
    def __init__(self, env):
        self.env = env
    
    def run(self, lines):
        lines[0] = indented_insert(lines[0], '\\begin{%s}' % self.env)
        top_indent = get_indentation(lines[0])
        lines.append(top_indent + ('\\end{%s}' % self.env))
        return lines
    
class SP_LIST:
    def run(self, lines):
        return SP_ENV('itemize').run(lines)
    
class SP_ENUM:
    def run(self, lines):
        return SP_ENV('enumerate').run(lines)
    
class SP_ITEM:
    def run(self, lines):
        lines[0] = indented_insert(lines[0], '\\item ')
        return lines
    
class SP_UPPER:
    def run(self, lines):
        for i in range(len(lines)):
            lines[i] = lines[i].upper()
            
        return lines


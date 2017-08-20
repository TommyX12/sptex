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

class EXEC_ENGINE():
    _current = None
    def __init__(self):
        self.locals = {}
    
    def _exec(var, expr):
        _env = {}
        dict_concat(var.locals, _env)
        dict_concat(locals(), _env)
        exec(expr, None, _env)
        
    def _eval(var, expr):
        _env = {}
        dict_concat(var.locals, _env)
        dict_concat(locals(), _env)
        return eval(expr, _env)
        
    def _get_current():
        if EXEC_ENGINE._current == None:
            EXEC_ENGINE._current = EXEC_ENGINE()
        
        return EXEC_ENGINE._current
    
    def _reset():
        EXEC_ENGINE._current = None
    
    def _add_env(self, key, value):
        self.locals[key] = value

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

class SP_SC():
    def run(self, lines):
        for i in range(len(lines)):
            for syntax in SHORTCUT_LIST:
                lines[i] = syntax.process_line(lines[i])
        
        return lines
    
class SP_EX():
    def run(self, lines):
        lines[0] = lines[0].lstrip()
        align_indentation(lines, 1, len(lines))
        EXEC_ENGINE._get_current()._exec('\n'.join(lines))
        return []

class SP_SAVE():
    def __init__(self, var_name):
        self.var_name = var_name
        
    def run(self, lines):
        new = []
        for line in lines:
            new.append('\'' + escape_script_string(line) + '\'')
        
        EXEC_ENGINE._get_current()._exec('var.' + self.var_name + '=[' + ','.join(new) + ']')
        
        return lines

class SP_DEF():
    def run(self, lines):
        lines[0] = lines[0].lstrip()
        func_name = lines[0][:skip_word_char(lines[0], 0)]
        lines[0] = 'def ' + lines[0]
        if not lines[0].endswith(':'):
            lines[0] += ':'
        
        align_indentation(lines, 0, len(lines))
        lines.append('EXEC_ENGINE._get_current()._add_env(\'%s\', %s)' % (func_name, func_name))
        EXEC_ENGINE._get_current()._exec('\n'.join(lines))
        return []

class SP_CLASS():
    def run(self, lines):
        top_indent = get_indentation(lines[0])
        class_name_start = skip_white_space(lines[0], 0)
        class_name_end = skip_word_char(lines[0], class_name_start)
        class_name = lines[0][class_name_start:class_name_end]
        lines[0] = top_indent + 'class ' + lines[0].lstrip()
        if not lines[0].endswith(':'):
            lines[0] += ':'
        
        align_indentation(lines, 0, len(lines))
        lines.append('EXEC_ENGINE._get_current()._add_env(\'%s\', %s)' % (class_name, class_name))
        EXEC_ENGINE._get_current()._exec('\n'.join(lines))
        return []

class SP_UPPER():
    def run(self, lines):
        for i in range(len(lines)):
            lines[i] = lines[i].upper()
            
        return lines

def SP(expr = ''):
    if len(expr) == 0:
        return 'SP'
    
    return str(EXEC_ENGINE._get_current()._eval(expr))


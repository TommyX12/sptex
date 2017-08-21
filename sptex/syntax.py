import math
import re
from util import *
from fractions import *

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
        self._ans        = None
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
        ans = var._ans
        var._ans = eval(expr)
        return var._ans
        
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
    
    def _set_add_sp_func(self, func):
        self._add_sp = func

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
        lines.append('EXEC_ENGINE.get_current()._add_env(\'{0}\', {0})'.format(func_name))
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
        lines.append('EXEC_ENGINE.get_current()._add_env(\'{0}\', {0})'.format(class_name))
        EXEC_ENGINE.get_current()._exec('\n'.join(lines))
        return []

class SP_SPDEF:
    def run(self, lines):
        lines[0] = lines[0].lstrip()
        class_name_end = skip_word_char(lines[0], 0)
        class_name = lines[0][:class_name_end]
        arg_start = class_name_end
        arg_end = extract_paren(lines[0], arg_start)
        if arg_start == arg_end:
            args     = []
            defaults = []
            
        else:
            args     = lines[0][arg_start + 1:arg_end - 1].split(',')
            defaults = ['' for i in args]
            for i in range(len(args)):
                ind = args[i].find('=')
                if ind >= 0:
                    defaults[i] = args[i][ind:]
                    args[i] = args[i][:ind].strip()
        
        lines[0] = 'class ' + MAIN_KEYWORD + '_' + cut(lines[0], arg_start, arg_end)
        if not lines[0].endswith(':'):
            lines[0] += ':'
        
        align_indentation(lines, 1, len(lines), '        ')
        lines = insert(lines, 1, 
        [
            '    def __init__('
            + ','.join(['self'] + [args[i] + defaults[i] for i in range(len(args))])
            + '):',
        ]
        + [
            '        self.{0}={0}'.format(arg) for arg in args
        ]
        + [
            '        pass',
            '    def run(self, lines):',
        ]
        + [
            '        {0}=self.{0}'.format(arg) for arg in args
        ]
        )
        
        lines.append('EXEC_ENGINE.get_current()._add_sp(\'{0}\', {1})'.format(class_name, MAIN_KEYWORD + '_' + class_name))
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
    Replace(r'\b(sum|prod)\s+(?:from\s+)?(.*?)\s+to\s+(.*?)\s+of\b', r'\\\1_{\2}^{\3}'),
    
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
        lines[0] = indented_insert(lines[0], '\\begin{{{0}}}'.format(self.env))
        top_indent = get_indentation(lines[0])
        lines.append(top_indent + ('\\end{{{0}}}'.format(self.env)))
        return lines
    
class SP_DOCUMENT:
    def __init__(self, size = '12pt', doc_class = 'article'):
        self.size = size
        self.doc_class = doc_class
    
    def run(self, lines):
        lines.insert(0, '\\documentclass[{0}]{{{1}}}'.format(self.size, self.doc_class))
        
        return lines
    
class SP_PACKAGES:
    def run(self, lines):
        for i in range(len(lines)):
            if is_empty_line(lines[i]):
                continue
            
            lines[i] = '\\usepackage{' + lines[i].strip() + '}'
        
        return lines
    
class SP_BODY:
    def run(self, lines):
        return SP_ENV('document').run(lines)
    
class SP_LIST:
    def __init__(self, ordered = False, bullet_char = '-'):
        self.ordered     = ordered
        self.bullet_char = bullet_char
        
    def run(self, lines):
        bullet_indent = None
        for i in range(1, len(lines)):
            line = lines[i]
            if re.search(r'^\s*{0}\s+'.format(self.bullet_char), line):
                bullet_indent = get_indentation(line)
                break
        
        if bullet_indent != None:
            for i in range(1, len(lines)):
                lines[i] = re.sub(r'^{0}{1}'.format(bullet_indent, self.bullet_char), bullet_indent + '\\item ', lines[i])
        
        env = 'enumerate' if self.ordered else 'itemize'
        
        return SP_ENV(env).run(lines)

class SP_UPPER:
    def run(self, lines):
        for i in range(len(lines)):
            lines[i] = lines[i].upper()
            
        return lines

class SP_AUTOBR:
    def __init__(self, start = 0, end = -1, include_last = False):
        self.start        = start
        self.end          = end
        self.include_last = include_last
        
    def run(self, lines):
        j = -1
        end = len(lines) if self.end < 0 else self.end
        for i in range(self.start, end):
            if not is_empty_line(lines[i]):
                if self.include_last:
                    j = i
                
                if j >= 0 and not has_stripped_suffix(lines[j], '\\\\'):
                    lines[j] += ' \\\\'
                
                j = i
        
        return lines

class SP_TABLE:
    def __init__(self,
            centered        = True,
            hlines          = True,
            auto_line_break = True):
        
        self.centered = centered
        self.hlines   = hlines
        self.auto_line_break = auto_line_break
    
    def run(self, lines):
        if self.auto_line_break:
            lines = SP_AUTOBR(1, len(lines), True).run(lines)
        
        if self.hlines:
            min_indent = align_indentation(lines, 1)
            for i in range(1, len(lines)):
                lines[i] += ' \\hline '
                
            lines.insert(1, '\\hline ')
            add_indentation(lines, min_indent, 1)
        
        lines[0] = indented_insert(lines[0], '{')
        lines[0] += '}'
        lines = SP_ENV('tabular').run(lines)
        if self.centered:
            lines = SP_ENV('center').run(lines)
            
        return lines

class SP_EQU:
    def __init__(self,
            tag                = None,
            aligned            = True,
            auto_line_break    = True,
            auto_align         = True,
            auto_align_marks   = [ '=', '\\approx'],
            auto_align_all     = False,
            whitespace_spacing = True):
        
        self.tag                = tag
        self.aligned            = aligned
        self.auto_align         = auto_align
        self.auto_align_marks   = auto_align_marks
        self.auto_line_break    = auto_line_break
        self.auto_align_all     = auto_align_all
        self.whitespace_spacing = whitespace_spacing
    
    def run(self, lines):
        if self.auto_line_break:
            lines = SP_AUTOBR().run(lines)
        
        if self.aligned and self.auto_align and self.auto_align_marks != None and len(self.auto_align_marks) > 0:
            for i in range(len(lines)):
                line = lines[i]
                braces_match = [0 for i in range(len(line))]
                cnt = 0
                for j in range(len(line)):
                    braces_match[j] = cnt
                    if line[j] == '{':
                        cnt += 1
                    
                    elif line[j] == '}':
                        cnt -= 1
                    
                for mark in self.auto_align_marks:
                    j = 0
                    k = True
                    while True:
                        j = line.find(mark, j)
                        if j >= len(line) or j < 0:
                            break
                        
                        if braces_match[j] != 0:
                            j += 1
                            continue
                        
                        if j == 0 or line[j - 1] != '&':
                            line = insert(line, j, '&' if k else '&&')
                        
                        if not self.auto_align_all:
                            break
                        
                        j += 1 if k else 2
                        k = not k
                        
                        j += 1
                        
                lines[i] = line
                
        if self.whitespace_spacing:
            for i in range(len(lines)):
                indent_len = get_indentation_len(lines[i])
                lines[i] = lines[i][:indent_len] + re.sub(r'  ', r'~', lines[i][indent_len:])
        
        env = 'align' if self.aligned else 'gather'
        if self.tag == None or len(self.tag) == 0:
            env += '*'
        
        elif self.tag == 'auto':
            pass
        
        else:
            lines[0] = indented_insert(lines[0], '\\tag{{0}} '.format(self.tag))
        
        return SP_ENV(env).run(lines)

class SP_CODE:
    def __init__(self, auto_line_break = True):
        self.auto_line_break = auto_line_break
        
    def run(self, lines):
        if self.auto_line_break:
            lines = SP_AUTOBR().run(lines)
        
        lines[0] = indented_insert(lines[0], '\\ttfamily ')
        return lines

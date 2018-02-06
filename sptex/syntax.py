import math
import re
import os
from util import *
from fractions import *

OUTPUT_EXTENSIONS = {
    '.sptex': '.tex',
    '.spcls': '.cls',
}
MAIN_KEYWORD = 'SP'

global_data = {}

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
        
        if var._return_string.endswith('\n'):
            var._return_string = var._return_string[:-1]
        
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
    
    def eval_top_level(expr):
        return eval(expr)
    
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
        new = [
            '\'' + escape_script_string(line) + '\''
            for line in lines
        ]
        
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

class SP_ALIAS:
    def __init__(self, old, new):
        self.old = old
        self.new = new
        
    def run(self, lines):
        for i in range(len(lines)):
            lines[i] = re.sub(self.old, self.new, lines[i])
            
        return lines

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
        
        lines.append('EXEC_ENGINE.get_current()._add_env(\'{0}\', {0})'.format(MAIN_KEYWORD + '_' + class_name))
        EXEC_ENGINE.get_current()._exec('\n'.join(lines))
        return []

class RegexReplace:
    def __init__(self, pattern, replacement):
        self.pattern = pattern
        self.replacement = replacement
    
    def process_line(self, line):
        return re.sub(self.pattern, self.replacement, line)

class BracketReplace:
    def __init__(self, pattern, replacement):
        self.pattern = pattern
        self.replacement = replacement
        
        pattern_bm = get_bracket_match(pattern)
        pattern_bm = get_bracket_match(pattern)
    
    def process_line(self, line):
        pass

SHORTCUT_LIST = [
    # <= and >=
    RegexReplace(r'<=', r'\\leq'),
    RegexReplace(r'!=', r'\\neq'),
    RegexReplace(r'>=', r'\\geq'),
    
    # approximate equal
    RegexReplace(r'~=', r'\\approx'),
    
    # ~
    RegexReplace(r'~', r'\\sim'),
    
    # ^* asterisk
    RegexReplace(r'\^\*', r'^\\ast'),
    
    # * multiply
    RegexReplace(r'\*', r'\\cdot'),
    
    # ...
    RegexReplace(r'\.\.\.', r'\\hdots'),
    
    # arrows
    RegexReplace(r'-\>', r'\\to'),
    RegexReplace(r'=\>', r'\\Rightarrow'),
    RegexReplace(r'\<=', r'\\Leftarrow'),
    RegexReplace(r'\<=\>', r'\\Leftrightarrow'),
    
    # (n)C(k) combination
    RegexReplace(r'(\b\w+|\{[^\{\}]*\})C(\w+\b|\{[^\{\}]*\})', r'\\binom{\1}{\2}'),
    #  BracketReplace('#(1)C#(2)', '\\binom{#(1)}{#(2)}'),
    
    # (a)/(b) fraction
    RegexReplace(r'(\b\w+|\{[^\{\}]*\})\s*/\s*(\w+\b|\{[^\{\}]*\})', r'\\frac{\1}{\2}'),
    #  BracketReplace('#(1) / #(2)', '\\frac{#(1)}{#(2)}')
    
    # infinity
    #  RegexReplace(r'\b(?:infty|inf|infinity)\b', r'\\infty'),
    
    # integrate from a to b of f(x) dx
    RegexReplace(r'\b(?:integral|int|integrate)\s+(?:from\s+)?(.*?)\s+to\s+(.*?)\s+of\b', r'\\int_{\1}^{\2}'),
    
    # evaluated at a
    RegexReplace(r'\b(?:eval|evaluated?)\s+at\b', r'\\Big|_'),
    
    # evaluated from a to b
    RegexReplace(r'\b(?:eval|evaluated?)\s+(?:from\s+)?(.*?)\s+to\b', r'\\Big|_{\1}^'),
    
    # sum from i = a to b of f(x)
    RegexReplace(r'\b(sum|prod)\s+(?:from\s+)?(.*?)\s+to\s+(.*?)\s+of\b', r'\\\1_{\2}^{\3}'),
    
    # sum from i in R of f(x)
    RegexReplace(r'\b(sum|prod)\s+(?:from\s+)?(.*?)\s+of\b', r'\\\1_{\2}'),
    
    # limit at x to infinity of f(x)
    RegexReplace(r'\b(?:limit|lim)\s+(?:at\s+)?(.*?)\s+to\s+(.*?)\s+of\b', r'\\lim_{\1 \\to \2}'),
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
    
class SP_INCLUDE:
    def run(self, lines):
        path = lines[0].strip()
        
        if not os.path.exists(path):
            print('WARNING: include "{0}" does not exist'.format(path))
            return []
        
        return read_file(path).split('\n')

class SP_LEFTALIGN:
    def run(self, lines):
        lines[0] = lines[0].lstrip()
        align_indentation(lines, 1, len(lines))
        return lines
    
class SP_PACKAGES:
    def run(self, lines):
        for i in range(len(lines)):
            line = lines[i].strip()
            if is_empty_line(line):
                continue
            
            ind = skip_word_char(line, 0)
            package, arg = line[:ind], line[ind:].strip()
            if len(arg) > 0:
                arg = '[' + arg + ']'
            
            lines[i] = '\\usepackage' + arg + '{' + package + '}'
        
        return lines
    
class SP_COMMENT:
    def run(self, lines):
        return []
    
class SP_BODY:
    def run(self, lines):
        return SP_ENV('document').run(lines)

class SP_INDENT:
    def __init__(self, margin = '1.5em'):
        self.margin = margin
    
    def run(self, lines):
        lines.insert(0, '[' + self.margin + ']{0em}')
        return SP_ENV('addmargin').run(lines)
    
class SP_LIST:
    def __init__(self, ordered = False, bullet_char = '-', spacing = '0.5em'):
        self.ordered     = ordered
        self.bullet_char = bullet_char
        self.spacing     = spacing
        
    def run(self, lines):
        first_indentation = get_indentation(lines[0])
        bullet_indent = None
        for i in range(1, len(lines)):
            line = lines[i]
            if re.search(r'^\s*{0}\s+'.format(self.bullet_char), line):
                bullet_indent = get_indentation(line)
                break
        
        if bullet_indent != None:
            for i in range(1, len(lines)):
                lines[i] = re.sub(r'^{0}{1}'.format(bullet_indent, self.bullet_char), bullet_indent + '\\item ', lines[i])
        
        if self.spacing is not None:
            lines.insert(0, '\\setlength\\itemsep{' + self.spacing + '}')
        
        env = 'enumerate' if self.ordered else 'itemize'
        
        return SP_ENV(env).run(lines)

class SP_UPPER:
    def run(self, lines):
        for i in range(len(lines)):
            lines[i] = lines[i].upper()
            
        return lines

class SP_AUTOBR:
    def __init__(self, start = 0, end = -1, include_last = True):
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
            lines = SP_AUTOBR(1, len(lines)).run(lines)
        
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

class SP_MATRIX:
    def __init__(self,
            flag            = "b",
            auto_line_break = True):
        
        self.flag            = flag
        self.auto_line_break = auto_line_break
    
    def run(self, lines):
        if self.auto_line_break:
            lines = SP_AUTOBR(1, len(lines)).run(lines)
        
        lines = SP_ENV(self.flag + 'matrix').run(lines)
            
        return lines

class SP_FIGURE:
    def __init__(self, width = 110):
        self.width = width
    
    def run(self, lines):
        figure_path = lines[0].strip()
        caption = lines[1].strip() if len(lines) > 1 else ''
        
        lines = [
            '[ht!]',
            '\\centering',
            '\\includegraphics[width=' + str(self.width) + 'mm]{' + figure_path + '}',
            '\\caption{' + caption + '\\label{overflow}}',
        ]
        return SP_ENV('figure').run(lines)

class SP_EQU:
    def __init__(self,
            tag                = None,
            aligned            = True,
            auto_line_break    = True,
            auto_align         = True,
            auto_align_marks   = ['=', '\\approx', '\\leq', '\\geq', '<', '>', '\\neq'],
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
            lines = SP_AUTOBR(include_last = False).run(lines)
        
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
            lines[0] = indented_insert(lines[0], '\\tag{%s} ' % (self.tag))
        
        return SP_ENV(env).run(lines)

class SP_CODE:
    def __init__(self, auto_line_break = True):
        self.auto_line_break = auto_line_break
        
    def run(self, lines):
        if self.auto_line_break:
            lines = SP_AUTOBR().run(lines)
        
        lines[0] = indented_insert(lines[0], '{\\ttfamily ')
        lines[len(lines) - 1] += '}'
        return lines

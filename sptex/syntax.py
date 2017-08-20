import re
from config import CUSTOM_SHORTCUT_LIST

OUTPUT_EXTENSION = '.tex'
MAIN_KEYWORD = 'SP'

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
] + CUSTOM_SHORTCUT_LIST

class LineProcessor:
    def __init__(self):
        pass
    
    def process_line(self, line):
        return line

class Replace(LineProcessor):
    def __init__(self, pattern, replacement):
        LineProcessor.__init__(self)

        self.pattern = pattern
        self.replacement = replacement
    
    def process_line(self, line):
        return re.sub(self.pattern, self.replacement, line)

class SP_SC():
    def __init__(self):
        pass
    
    def run(self, lines):
        for i in range(len(lines)):
            for syntax in SHORTCUT_LIST:
                lines[i] = syntax.process_line(lines[i])
        
        return lines

class SP_A():
    def __init__(self):
        pass
    
    def run(self, lines):
        return lines

class SP_B():
    def __init__(self):
        pass
        
    def run(self, lines):
        return lines

class SP_C():
    def __init__(self):
        pass
        
    def run(self, lines):
        return lines

def SP(arg = None):
    if arg == None:
        return 'SP'
    
    return str(arg)

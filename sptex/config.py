from syntax import *

CUSTOM_SYNTAX_LIST = [
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

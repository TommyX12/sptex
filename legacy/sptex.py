import os, sys, glob
import re
from util import *
from syntax import *
from config import CUSTOM_SHORTCUT_LIST

SHORTCUT_LIST = [
    # remove keyword
    Replace(r'^(\s*)%s\b' % SHORTCUT_KEYWORD, r'\1'),
] + CUSTOM_SHORTCUT_LIST

NORMAL_LIST = [
    # remove keyword
    Replace(r'^(\s*)%s\b' % NORMAL_KEYWORD, r'\1'),
]

def get_default_output_path(input_path):
    return input_path[:input_path.rfind('.')] + OUTPUT_EXTENSION

def compile(input_text):
    input_lines = input_text.split('\n')
    output_lines = []
    
    for input_line in input_lines:
        output_line = input_line
        if re.search(r'^(\s*)%s\b' % (NORMAL_KEYWORD), output_line):
            for syntax in NORMAL_LIST:
                output_line = syntax.process_line(output_line)
            
        elif re.search(r'^(\s*)%s\b' % (SHORTCUT_KEYWORD), output_line):
            for syntax in SHORTCUT_LIST:
                output_line = syntax.process_line(output_line)
            
        output_lines.append(output_line)
    
    return '\n'.join(output_lines)

def main(argc, argv):
    if argc < 2 or argc > 3:
        print('usage: python %s input_path [output_path]' % argv[0])
        return 1
    
    input_path = argv[1]
    if not input_path.endswith('.sptex'):
        print('invalid input file name extension.')
        return 1
    
    output_path = argv[2] if argc == 3 else get_default_output_path(input_path)
    
    input_text = read_file(input_path)
    output_text = compile(input_text)
    
    write_file(output_path, output_text)
    
    return 0

if __name__ == '__main__':
    #  main(len(sys.argv), sys.argv)
    pass
    
    




def listify(lines, indent_match, row, end_row):
    while row < end_row:
        line = lines[row]
        if re.search(r'^\s*%s\s+\w+' % (MAIN_KEYWORD), line):
            # manual splitting that finds indentation, preprocessor name, arguments (...), and first char.
            # remove the parts about preprocessor name, arguments (...), space to first char.
            
            listify(lines, indent_match, row, indent_match[row])
            
            # lines[row] = 'SP_A().run(' + lines[row]
            row = indent_match[row] - 1
            lines[row] += ')'
        
        else:
            lines[row] = '[\'' + escape_script_string(lines[row]) + '\']'
            # manually search to find SP(...). replace them with ' + SP(...) + '. only allow search inline
            
        lines[row] += '+'
        row += 1
    
    lines[row - 1] += '[]'
    
"""
SP A() the quick brown
    fox jumped
    over the SP(2 + 3)
    SP B() HAIDOMO
    SP C() test title
        SP() hello
        world
    
    lazy dog

testing other things
hi

"""

print('\n'.join(eval(
"""
(
SP_A().run(['the quick brown'] + 
['    fox jumped'] + 
['    over the ' + SP(2 + 3) + ''] + 
SP_B().run(['    HAIDOMO'] + []) + 
SP_C().run(['    test title'] +
['        ' + SP() + ' hello'] + 
['        world'] + []) + 
['    '] + 
['    lazy dog'] + []) + 
['testing other things'] + 
['hi'] + []
)
"""
)))

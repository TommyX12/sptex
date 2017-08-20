import os, sys, glob
import re
from util import *
from syntax import *

def get_default_output_path(input_path):
    return input_path[:input_path.rfind('.')] + OUTPUT_EXTENSION

def get_indentation_len(line):
    ptr = 0
    while ptr < len(line):
        if line[ptr] != ' ' and line[ptr] != '\t':
            break
        
        ptr += 1
        
    return ptr

def get_indentation(line):
    return line[:get_indentation_len(line)]

def is_empty_line(line):
    return len(line.lstrip()) == 0

def skip(line, i, chars):
    while i < len(line) and line[i] in chars:
        i += 1
    
    return i

def skip_white_space(line, i):
    return skip(line, i, ' \t\n')

def skip_word_char(line, i):
    return skip(line, i, 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_')

def get_indent_match(lines):
    result = [0 for i in range(len(lines))]
    indent_stack = [] # element: (line index, indentation)
    for i in range(len(lines)):
        line = lines[i]
        if is_empty_line(line):
            continue
        
        cur_indent = get_indentation_len(line)
        while len(indent_stack) > 0 and top(indent_stack)[1] <= cur_indent:
            result[indent_stack.pop()[0]] = i

    for entry in indent_stack:
        result[entry[0]] = len(lines)
            
    return result

def extract_paren(line, i):
    if (line[i] != '(') return i
    cnt = 1
    i += 1
    while i < len(line):
        if line[i] == '(':
            cnt += 1
        
        elif line[i] == ')':
            cnt -= 1
            if cnt == 0:
                return i + 1
        
        i += 1
    
    return len(line)

def listify(lines, indent_match, row, end_row):
    while row < end_row:
        line = lines[row]
        if re.search(r'^\s*%s\s+\w+' % (MAIN_KEYWORD), line):
            # manual splitting that finds indentation, preprocessor name, arguments (...), and first char.
            indent_len = get_indentation_len(line)
            indent = line[:indent_len]
            sp_start = skip_white_space(line, indent_len + len(MAIN_KEYWORD))
            sp_end = skip_word_char(line, sp_start)
            arg_start = sp_end
            arg_end = extract_paren(arg_start)
            first_line_start = skip_white_space(arg_end)
            
            sp_text = MAIN_KEYWORD + '_' + line[sp_start:arg_end]
            if arg_start == arg_end:
                sp_text += '()'
            
            sp_text += '.run('
            
            # remove the parts about preprocessor name, arguments (...), space to first char.
            lines[row] = cut(lines[row], sp_start, first_line_start)
            
            listify(lines, indent_match, row, indent_match[row])
            
            lines[row] = sp_text + lines[row]
            row = indent_match[row] - 1
            lines[row] += ')'
        
        else:
            result = '['
            #  lines[row] = escape_script_string(lines[row])
            # manually search to find SP(...). replace them with ' + SP(...) + '. only allow search inline
            i = 0
            pat = MAIN_KEYWORD + '('
            while i < len(line):
                i = line.find(pat, i)
                if i < 0:
                    result += '\'' + escape_script_string(line[i:])
                
            
            result += '\']'
            lines[row] = result
            
        lines[row] += '+'
        row += 1
    
    lines[row - 1] += '[]'
    
def eval_lines(lines):
    return eval('\n'.join(['('] + lines + [')']))
    
def compile(input_text):
    lines = input_text.split('\n')
    
    # first pass:
    indent_match = get_indent_match(lines)
    listify(lines, indent_match, 0, len(lines))
        
    # second pass:
    return '\n'.join(eval_lines(lines))


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
    # main(len(sys.argv), sys.argv)
    pass
    
    

test_input = """
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

print("---------------------------------")

print(compile(test_input))

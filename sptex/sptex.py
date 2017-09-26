import os, sys, glob
import re
from util import *
from syntax import *

def get_default_output_path(input_path):
    old_extension = input_path[input_path.rfind('.'):]
    return input_path[:input_path.rfind('.')] + OUTPUT_EXTENSIONS[old_extension]

def listify(lines, indent_match, start_row, end_row):
    row = start_row
    while row < end_row:
        line = lines[row]
        if re.search(r'^\s*{0}\s+\w+'.format(MAIN_KEYWORD), line):
            # manual splitting that finds indentation, preprocessor name, arguments (...), and first char.
            indent_len = get_indentation_len(line)
            indent = line[:indent_len]
            sp_start = skip_white_space(line, indent_len + len(MAIN_KEYWORD))
            sp_end = skip_word_char(line, sp_start)
            arg_start = sp_end
            arg_end = extract_paren(line, arg_start)
            first_line_start = skip_white_space(line, arg_end)
            
            sp_text = MAIN_KEYWORD + '_' + line[sp_start:arg_end]
            if arg_start == arg_end:
                sp_text += '()'
            
            sp_text += '.run('
            
            # remove the parts about preprocessor name, arguments (...), space to first char.
            lines[row] = cut(lines[row], indent_len, first_line_start)
            
            listify(lines, indent_match, row, indent_match[row])
            
            lines[row] = sp_text + lines[row]
            row = indent_match[row] - 1
            lines[row] += ')'
        
        else:
            #  result = ['\'\'']
            result = ['\'\''] if row == start_row else []
            #  lines[row] = escape_script_string(lines[row])
            # manually search to find SP(...). replace them with ' + SP(...) + '. only allow search inline
            i = 0
            pat = MAIN_KEYWORD + '('
            while i < len(line):
                j = line.find(pat, i)
                if j < 0:
                    result.append('\'' + escape_script_string(line[i:]) + '\'')
                    break
                
                result.append('\'' + escape_script_string(line[i:j]) + '\'')
                j += len(MAIN_KEYWORD)
                i = extract_paren(line, j)
                result.append(MAIN_KEYWORD + '(\'' + escape_script_string(line[j + 1:i - 1]) + '\')')
            lines[row] = '[' + '+'.join(result) + ']'
            
        lines[row] += '+'
        row += 1
    
    lines[row - 1] += '[]'
    
def eval_lines(lines):
    return EXEC_ENGINE.eval_top_level('\n'.join(['('] + lines + [')']))
    
def compile(input_text):
    lines = input_text.split('\n')
    
    # first pass:
    indent_match = get_indent_match(lines)
    listify(lines, indent_match, 0, len(lines))
    
    # second pass:
    return '\n'.join(eval_lines(lines))


def main(argc, argv):
    if argc < 2 or argc > 3:
        print('usage: python {0} input_path [output_path]'.format(argv[0]))
        return 1
    
    input_path = argv[1]
    #  if not input_path.endswith('.sptex'):
        #  print('invalid input file name extension.')
        #  return 1
    
    output_path = argv[2] if argc == 3 else get_default_output_path(input_path)
    
    input_text = read_file(input_path)
    output_text = compile(input_text)
    
    write_file(output_path, output_text)
    
    return 0

if __name__ == '__main__':
    main(len(sys.argv), sys.argv)
    pass
    
    

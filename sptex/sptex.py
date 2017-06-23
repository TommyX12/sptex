import os, sys, glob
import re
from util import *
from syntax import *
from config import CUSTOM_SYNTAX_LIST

SYNTAX_LIST = [
    # remove keyword
    Replace(r'^(\s*)%s\b' % KEYWORD, r'\1'),
] + CUSTOM_SYNTAX_LIST

def get_default_output_path(input_path):
    return input_path[:input_path.rfind('.')] + OUTPUT_EXTENSION

def compile(input_text):
    input_lines = input_text.split('\n')
    output_lines = []
    
    for input_line in input_lines:
        output_line = input_line
        if re.search(r'^(\s*)%s\b' % (KEYWORD), output_line):
            for syntax in SYNTAX_LIST:
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
    main(len(sys.argv), sys.argv)

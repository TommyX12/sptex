import os, sys, glob
import re
from util import *

OUTPUT_EXTENSION = '.tex'
KEYWORD = 'SP'

def get_default_output_path(input_path):
    return input_path[:input_path.rfind('.')] + OUTPUT_EXTENSION

def compile(input_text):
    input_lines = input_text.split('\n')
    output_lines = []
    
    for input_line in input_lines:
        output_line = input_line
        if output_line.strip().startswith(KEYWORD):
            output_line = re.sub(r'^(\s*)SP', r'\1', output_line)
            output_line = re.sub(r'<=', r'\\leq', output_line)
            output_line = re.sub(r'>=', r'\\geq', output_line)
            output_line = re.sub(r'~=', r'\\approx', output_line)
            output_line = re.sub(r'~', r'\\sim', output_line)
            output_line = re.sub(r'(?:integral|int) (?:from )?(.*) to (.*) of', r'\\int_{\1}^{\2}', output_line)
            output_line = re.sub(r'sum (.*) (?:from )?to (.*) of', r'\\sum_{\1}^{\2}', output_line)
            output_line = re.sub(r'(?:limit|lim) (.*) to (.*) of', r'\\lim_{\1\\to\2}', output_line)
            
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

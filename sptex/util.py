import os, sys, codecs
import glob
import re

def list_dir(pattern):
    return glob.glob(pattern)   

def read_file(path):
    if not os.path.exists(path):
        write_file(path, '')

    with open(path, encoding='utf-8-sig') as f:
        content = f.read()
    
    return content

def write_file(path, data):
    file = open(path, 'w')
    file.write(data)
    file.close()

def clamp(num, l, r):
    if num < l:
        return l

    if num > r:
        return r
    
    return num

def escape_script_string(str):
    str = re.sub(r'([\\\"\'])', r'\\\1', str)
    return str

def top(stack):
    return stack[len(stack) - 1]

def cut(string, i, j):
    return string[:i] + string[j:]

def dict_concat(src, dest):
    for key in src:
        dest[key] = src[key]
    
    return dest

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

def extract_paren(line, i):
    if i >= len(line) or line[i] != '(':
        return i
    
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

def align_indentation(lines, i, j):
    min_indent = -1
    for k in range(i, j):
        if is_empty_line(lines[k]):
            continue
        
        cur_indent = get_indentation_len(lines[k])
        if min_indent == -1 or cur_indent < min_indent:
            min_indent = cur_indent
    
    if min_indent >= 0:
        for k in range(i, j):
            lines[k] = lines[k][min_indent:]

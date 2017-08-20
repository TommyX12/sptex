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



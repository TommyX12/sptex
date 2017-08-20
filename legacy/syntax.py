import re

OUTPUT_EXTENSION = '.tex'
MAIN_KEYWORD = 'SP'
SHORTCUT_KEYWORD = 'SC'
NORMAL_KEYWORD = 'NM'
ENV_KEYWORD = 'EV'

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

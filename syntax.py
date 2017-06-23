import re

OUTPUT_EXTENSION = '.tex'
KEYWORD = 'SP'

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


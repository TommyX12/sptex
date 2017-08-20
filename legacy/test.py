import os, sys, glob
import re
from util import *
from syntax import *
from config import CUSTOM_SHORTCUT_LIST

str = """
class Test:
    def __init__(self):
        self.x = 1
        print("hi")

test = Test()

result = test
"""

exec(str)

print(result)

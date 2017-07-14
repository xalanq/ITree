# LICENSE:
#     itree - LGPL v3.0
#     mistune - BSD
#     PySide - LGPL v3.0
#     MathJax - Apache
#     SyntaxHighlighter - LGPL v3.0
# see the file "LICENSE"

# functions and packages template

from PySide.QtGui import *
from PySide.QtCore import *
from PySide.QtWebKit import *
from PySide.QtNetwork import *
from imarkdown import *
import os, sys

APP_NAME = 'ITree'
VERSION = 'Alpha 1.2'
AUTHOR = 'iwtwiioi'
EMAIL = 'iwtwiioi@gmail.com'
APP_PATH = os.path.dirname(os.path.abspath(sys.argv[0])) + os.path.sep

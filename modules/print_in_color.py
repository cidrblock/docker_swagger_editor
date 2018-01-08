from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter

class PrintInColor:

    @classmethod
    def message(self, color, action, string, **kwargs):
        RED = '\033[91m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        END = '\033[0m'
        bspaces = " "*(int((12-len(action))/2))
        espaces = " "*(12-len(bspaces)-len(action))
        print(locals()[color] + "[" + bspaces + action + espaces + "] " + string + END, **kwargs)

    @classmethod
    def code(self, string):
        print(highlight(string, PythonLexer(), TerminalFormatter()))

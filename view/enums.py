from enum import Enum


class Color(Enum):
    BLUE = "\033[94m"
    END = "\033[0m"
    GREEN = "\033[92m"
    RED = "\033[91m"


class ViewMode(Enum):
    OPTIONS = 0
    REGISTER = 1
    RECORD = 2
    PROCESS_ONE = 3
    PROCESS_ALL = 4
    SEARCH = 5
    PAYSLIP = 6
    HISTORY = 7
    REPORT = 8
    QUIT = 9

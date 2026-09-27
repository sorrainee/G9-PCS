import os
import subprocess
import sys
from enum import Enum
from random import uniform
from time import sleep


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


class View:
    blue = "\033[94m"
    color_end = "\033[0m"
    HEADER = f"{'-' * 10}  SystemD [Payroll and Compensation]  {'-' * 10}\n"
    DESCRIPTION = f"To exit views other than this one pre-emptively, enter '{blue}:q{color_end}' in any input.\n"
    QUIT_SIGNAL = ":q"

    def clear_screen(self):
        subprocess.call("cls" if os.name == "nt" else "clear")

    def typewriter(self, string: str):
        for s in string:
            print(s, end="")
            sys.stdout.flush()
            sleep(uniform(0.01, 0.08))

    def error(self, msg: str):
        red = "\033[31m"
        color_end = "\033[0m"
        print(f"{red}{msg}{color_end}\n")

    def success(self, msg: str):
        green = "\033[92m"
        color_end = "\033[0m"
        print(f"{green}{msg}{color_end}\n")

    def input(self, msg: str = "What would you like to do?"):
        choice = input(msg + "\n> ").strip()

        if choice == self.QUIT_SIGNAL:
            self.set_view_mode(ViewMode.OPTIONS)

        return choice

    def back(self):
        input("Press any key to return\n> ")
        self.view = ViewMode.OPTIONS

    def exit(self):
        self.clear_screen()
        self.typewriter("Thanks for using SystemD. Have a nice day!")
        self.view = ViewMode.QUIT

    def start(self):
        self.clear_screen()
        self.typewriter(self.HEADER)
        self.view = ViewMode.OPTIONS

    def options(self):
        self.clear_screen()
        self.view = ViewMode.OPTIONS
        print(
            self.HEADER
            + self.DESCRIPTION
            + """
[1] Register employee
[2] Record employee attendance
[3] Process employee payroll
[4] Process all payrolls
[5] Search employee
[6] Display payslip
[7] Show payroll history
[8] Generate reports
[9] Exit
"""
        )

    def set_view_mode(self, mode: ViewMode):
        self.clear_screen()
        self.view = mode

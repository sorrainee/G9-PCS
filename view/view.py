import math
import os
import subprocess
import sys
from enum import Enum
from random import uniform
from time import sleep

from model.employee import Employee
from model.manager import PayrollEntry


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
        self.set_view_mode(ViewMode.OPTIONS)

    def start(self):
        self.clear_screen()
        self.typewriter(self.HEADER)
        self.set_view_mode(ViewMode.OPTIONS)

    def set_view_mode(self, mode: ViewMode):
        self.clear_screen()
        self.view = mode

    def options_view(self):
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

    def employee_view(self, employee: Employee):
        self.success(f"Found employee {employee.id}")
        print(employee.__str__() + "\n")

    def payslip_view(self, entry: PayrollEntry):
        self.success(f"Found payroll entry for employee {entry.employee.id}")
        print(entry.__str__() + "\n")

    def history_view(self, entries: list[PayrollEntry]):
        if len(entries) <= 0:
            self.error("No payroll records found.")
        else:
            for e in entries:
                print(e.__str__() + "\n")

            self.success(f"Displayed {len(entries)} payroll(s).")

    def report_view(self, report):
        border = "-" * 5
        green = "\033[92m"
        red = "\033[91m"
        color_end = "\033[0m"

        print(self.HEADER)
        print("Employee and Performance Statistics Report\n")

        print(f"{border}  Payroll Total per Employee Type\n")
        for k, v in report["payroll"].items():
            print(f"{k}: {green}{v:,.2f}{color_end}")

        print(f"\n{border}  Highest and Lowest Net Pay")
        items = report["net_pay"]
        print(
            f"Highest Pay: {green}{items['highest']:,.2f}{color_end}\nLowest Pay: {green}{items['lowest']:,.2f}{color_end}"
        )

        print(f"\n{border}  Deductions and Benefits Summary\n")
        deductions = report["deduction"]["total"]
        benefits = report["benefit"]["total"]
        print(
            f"A total of {red}{deductions:,.2f}{color_end} has been deducted across all employee payrolls.\nMeanwhile, a total of {green}{benefits:,.2f}{color_end} benefits has been paid across all employees."
        )

        print(f"\n{border} Employees with Overtime Hours and Zero-Payable Contracts\n")

        overtime = report["employee_filter"]["overtime"]
        zero_payable = report["employee_filter"]["zero-payable"]

        print("\nOvertime Employees:\n")
        for e in overtime:
            print(
                f"{e.employee.__str__()}\nOvertime Hours: {e.attendance.overtime_hours}hr(s)\n"
            )

        print("\nZero-Payable Contracted Employees:\n")
        for e in zero_payable:
            print(
                f"{e.employee.__str__()}\nTotal Sales: {green}{math.fsum(e.attendance.sales):,.2f}{color_end}\n"
            )
        print("\n")

    def exit_view(self):
        self.typewriter("Thanks for using SystemD. Have a nice day!")

import math
import os
import subprocess
import sys
from random import uniform
from time import sleep

from model.employee import Employee
from model.manager import PayrollEntry
from view.enums import Color, ViewMode


class View:
    SYSTEM_NAME = "systemd"
    HEADER = f"{'-' * 10}  {SYSTEM_NAME} [Payroll and Compensation]  {'-' * 10}\n"
    DESCRIPTION = f"To exit views other than this one pre-emptively, enter '{Color.BLUE}:q{Color.END}' in any input.\n"
    QUIT_SIGNAL = ":q"

    def clear_screen(self):
        subprocess.call("cls" if os.name == "nt" else "clear")

    def typewriter(self, string: str):
        for s in string:
            print(s, end="")
            sys.stdout.flush()
            sleep(uniform(0.01, 0.08))

    def error(self, msg: str):
        print(f"{Color.RED.value}{msg}{Color.END.value}\n")

    def success(self, msg: str):
        print(f"{Color.GREEN.value}{msg}{Color.END.value}\n")

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
[6] Display payslipen
[7] Show payroll history
[8] Generate reports
[9] Exit
"""
        )

    def employee_view(self, employee: Employee):
        self.success(f"Found employee {employee.id}")
        print(employee.__str__() + "\n")

    def payslip_view(self, employee_id: str, entry: PayrollEntry):
        self.success(f"Found payroll entry for employee {entry.employee.id}")
        print(entry.__str__() + "\n")

    def history_view(self, entries: list[PayrollEntry]):
        if len(entries) <= 0:
            self.error("No payroll records found.")
        else:
            for e in entries:
                print(e.__str__() + "\n")

            self.success(
                f"Displayed {len(entries)} payroll{'s' if len(entries) > 1 else ''}."
            )

    def report_view(self, report):
        border = "-" * 5

        print(self.HEADER)
        print("Employee and Performance Statistics Report\n")

        print(f"{border}  Payroll Total per Employee Type\n")
        for k, v in report["payroll"].items():
            print(f"{k}: {Color.GREEN.value}{v:,.2f}{Color.END.value}")

        print(f"\n{border}  Highest and Lowest Net Pay")
        items = report["net_pay"]
        print(
            f"Highest Pay: {Color.GREEN.value}{items['highest']:,.2f}{Color.END.value}\nLowest Pay: {Color.GREEN.value}{items['lowest']:,.2f}{Color.END.value}"
        )

        print(f"\n{border}  Deductions and Benefits Summary\n")
        deductions = report["deduction"]["total"]
        benefits = report["benefit"]["total"]
        print(
            f"A total of {Color.RED.value}{deductions:,.2f}{Color.END.value} has been deducted across all employee payrolls.\nMeanwhile, a total of {Color.GREEN.value}{benefits:,.2f}{Color.END.value} benefits has been paid across all employees."
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
                f"{e.employee.__str__()}\nTotal Sales: {Color.GREEN.value}{math.fsum(e.attendance.sales):,.2f}{Color.END.value}\n"
            )

    def exit_view(self):
        self.typewriter(f"Thanks for using {self.SYSTEM_NAME}. Have a nice day!")

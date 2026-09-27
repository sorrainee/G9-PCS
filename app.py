import math
import re
import sys
from time import sleep

from controller.manager import PayrollManager
from model.attendance import AttendanceRecord
from model.employee import (
    CommissionEmployee,
    Employee,
    PartTimeEmployee,
    RegularEmployee,
)
from model.exception import PayrollException
from view.view import View, ViewMode


class Application:
    def __init__(self, ui: View, manager: PayrollManager):
        self.ui = ui
        self.manager = manager

    def run(self):
        self.ui.start()

        while True:
            match self.ui.view:
                case ViewMode.OPTIONS:
                    self.options()
                case ViewMode.REGISTER:
                    self.register()
                case ViewMode.RECORD:
                    self.record()
                case ViewMode.PROCESS_ONE:
                    self.process_payroll()
                case ViewMode.PROCESS_ALL:
                    self.process_all_payrolls()
                case ViewMode.SEARCH:
                    self.search()
                case ViewMode.PAYSLIP:
                    self.payslip()
                case ViewMode.HISTORY:
                    self.history()
                case ViewMode.REPORT:
                    self.report()
                case ViewMode.QUIT:
                    sys.exit()

    # Helpers

    def options(self):
        self.ui.options()
        while True:
            match self.ui.input():
                case "1":
                    self.ui.set_view_mode(ViewMode.REGISTER)
                case "2":
                    self.ui.set_view_mode(ViewMode.RECORD)
                case "3":
                    self.ui.set_view_mode(ViewMode.PROCESS_ONE)
                case "4":
                    self.ui.set_view_mode(ViewMode.PROCESS_ALL)
                case "5":
                    self.ui.set_view_mode(ViewMode.SEARCH)
                case "6":
                    self.ui.set_view_mode(ViewMode.PAYSLIP)
                case "7":
                    self.ui.set_view_mode(ViewMode.HISTORY)
                case "8":
                    self.ui.set_view_mode(ViewMode.REPORT)
                case "9":
                    self.ui.exit()
                case _:
                    self.ui.error("Available operations are only from 1 to 9")
                    continue
            break

    def register(self):
        rate: float
        employee: Employee

        id = self.ui.input("What is the employee's ID?")

        if id == self.ui.QUIT_SIGNAL:
            return

        while True:
            name = self.ui.input("What is the employee's registered name?")

            if name == self.ui.QUIT_SIGNAL:
                return

            if (
                any(s.isdigit() for s in name)
                or re.compile("[@_!#$%^&*()<>?/\\|}{~:]").search(name) != None
            ):
                self.ui.error(
                    "Employee's name is invalid. Please ensure no digit or special characters are present."
                )
                continue
            break

        while True:
            employee_choice = self.ui.input(
                "Enter the number according to their employee type [1 (Regular) / 2 (Part-timer) / 3 (Commission-based)]"
            )

            if employee_choice == self.ui.QUIT_SIGNAL:
                return

            match employee_choice:
                case "1":
                    employee = RegularEmployee(id, name, 0)
                case "2":
                    employee = PartTimeEmployee(id, name, 0)
                case "3":
                    employee = CommissionEmployee(id, name, 0)
                case _:
                    self.ui.error("Available employee types are only between 1 to 3")
                    continue
            break

        while True:
            try:
                f = self.ui.input(
                    f"How much is the employee's salary? Provide the {'hourly' if isinstance(employee, PartTimeEmployee) else 'weekly' if isinstance(employee, RegularEmployee) else 'pricing'} salary."
                )

                if f == self.ui.QUIT_SIGNAL:
                    return

                rate = float(f)

                break
            except ValueError:
                self.ui.error("Employee's salary is invalid.")
                continue

        try:
            employee.rate = rate
            self.manager.create_employee(employee)
        except PayrollException as e:
            self.ui.error(str(e))
        else:
            self.ui.success(f"Successfully added employee {id}.")
        finally:
            self.ui.back()

    def record(self):
        hours: int
        overtime_hours = 0
        absences = 0
        id: str
        sales: list[float] = []
        employee: Employee

        while True:
            id = self.ui.input(
                "Who's attendance are you creating? Provide their employee ID."
            )

            if id == self.ui.QUIT_SIGNAL:
                return

            try:
                employee = self.manager.find_employee(id)
            except PayrollException as e:
                self.ui.error(str(e))
                continue
            break

        while True:
            try:
                i = self.ui.input("How many hours has the employee worked?")

                if i == self.ui.QUIT_SIGNAL:
                    return

                hours = int(i)
            except ValueError:
                self.ui.error("Fill in a valid amount of work hours.")
                continue
            else:
                if hours <= 0:
                    self.ui.error("Work hours must be at least 1 hour.")
                    continue
            break

        if isinstance(employee, RegularEmployee):
            while True:
                try:
                    i = self.ui.input(
                        "How many hours has the employee worked overtime? Leave blank if none."
                    )

                    if i == self.ui.QUIT_SIGNAL:
                        return

                    if len(i) == 0:
                        i = "0"

                    overtime_hours = int(i)
                except ValueError:
                    self.ui.error("Fill in a valid amount of overtime hours.")
                    continue
                else:
                    if hours < 0:
                        self.ui.error("Overtime hours may not be less than 0.")
                        continue
                break

            while True:
                try:
                    i = self.ui.input(
                        "How many absences has the employee made? Leave blank if none."
                    )

                    if i == self.ui.QUIT_SIGNAL:
                        return

                    if len(i) == 0:
                        i = "0"

                    absences = int(i)
                except ValueError:
                    self.ui.error("Fill in a valid amount of absences.")
                    continue
                else:
                    if hours <= 0:
                        self.ui.error("Absence count may not be less than 0.")
                        continue
                break

        elif isinstance(employee, CommissionEmployee):
            answer = ""
            while answer.lower() != "q":
                while True:
                    answer = self.ui.input(
                        "Enter the sales the employee has made. Press 'q' once finished to proceed."
                    )

                    if answer == self.ui.QUIT_SIGNAL:
                        return

                    try:
                        sales.append(float(answer))
                    except ValueError:
                        self.ui.error("Enter a valid sale amount.")
                        continue
                    break

        try:
            self.manager.create_attendace(
                AttendanceRecord(id, hours, overtime_hours, absences, sales)
            )
        except PayrollException as e:
            self.ui.error(str(e))
        else:
            self.ui.success(f"Added attendance for employee {id}.")
        finally:
            self.ui.back()

    def process_payroll(self):
        id: str

        while True:
            id = self.ui.input(
                "Who's payroll are you processing? Provide their employee ID."
            )

            if id == self.ui.QUIT_SIGNAL:
                return

            try:
                self.manager.find_employee(id)
            except PayrollException as e:
                self.ui.error(str(e))
                continue
            break

        try:
            self.manager.process_payroll(id)
        except PayrollException as e:
            self.ui.error(str(e))
        else:
            self.ui.success(f"Processed payroll for employee {id}.")
        finally:
            self.ui.back()

    def process_all_payrolls(self):
        print("Processing every payroll for every employee. This might take a while...")
        sleep(0.5)

        try:
            self.manager.process_all_payroll()
        except PayrollException as e:
            self.ui.error(str(e))
        else:
            self.ui.success("Successfully processed every employee's payrolls.")
        finally:
            self.ui.back()

    def search(self):
        id: str
        employee: Employee

        while True:
            id = self.ui.input("Who are you searching? Provide their employee ID.")

            if id == self.ui.QUIT_SIGNAL:
                return

            try:
                employee = self.manager.find_employee(id)
            except PayrollException as e:
                self.ui.error(str(e))
                continue
            break

        self.ui.success(f"Found employee {id}")
        print(employee.__str__() + "\n")
        self.ui.back()

    def payslip(self):
        id: str

        while True:
            id = self.ui.input(
                "Who's payslip are you viewing? Provide their employee ID."
            )

            if id == self.ui.QUIT_SIGNAL:
                return

            try:
                self.manager.find_employee(id)
            except PayrollException as e:
                self.ui.error(str(e))
                continue
            break

        try:
            payslip = self.manager.find_payroll_entry(id)
        except PayrollException as e:
            self.ui.error(str(e))
        else:
            self.ui.success(f"Found payroll entry for employee {id}")
            print(payslip.__str__() + "\n")
        finally:
            self.ui.back()

    def history(self):
        if len(self.manager.payrolls) <= 0:
            self.ui.error("No payroll records found.")
        else:
            for e in self.manager.payrolls:
                print(e.__str__() + "\n")

        self.ui.back()

    def report(self):
        border = "-" * 5
        green = "\033[92m"
        red = "\033[91m"
        blue = "\033[94m"
        color_end = "\033[0m"

        try:
            report = self.manager.report(
                payroll=True,
                net_pay=True,
                deduction=True,
                benefit=True,
                employee_filter=["overtime", "zero-payable"],
            )
        except PayrollException as e:
            self.ui.error(str(e))
        else:
            print(self.ui.HEADER)
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

            print(
                f"\n{border} Employees with Overtime Hours and Zero-Payable Contracts\n"
            )

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
        finally:
            self.ui.back()

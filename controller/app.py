import re
import sys
from time import sleep

from model.attendance import AttendanceRecord
from model.employee import *
from model.exception import PayrollException
from model.manager import PayrollManager
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
                    self.handle_options()
                case ViewMode.REGISTER:
                    self.handle_register()
                case ViewMode.RECORD:
                    self.handle_record()
                case ViewMode.PROCESS_ONE:
                    self.handle_process_payroll()
                case ViewMode.PROCESS_ALL:
                    self.handle_process_all_payrolls()
                case ViewMode.SEARCH:
                    self.handle_search()
                case ViewMode.PAYSLIP:
                    self.handle_payslip()
                case ViewMode.HISTORY:
                    self.handle_history()
                case ViewMode.REPORT:
                    self.handle_report()
                case ViewMode.QUIT:
                    self.handle_exit()

    # Helpers

    def handle_options(self):
        self.ui.options_view()

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
                    self.ui.set_view_mode(ViewMode.QUIT)
                case _:
                    self.ui.error("Available operations are only from 1 to 9")
                    continue
            break

    def handle_register(self):
        rate: float
        employee: Employee

        while True:
            id = self.ui.input(
                "What is the employee's ID? Leave blank for an auto-generated ID."
            )

            if id == self.ui.QUIT_SIGNAL:
                return

            if len(id) == 0:
                n = 7
                n ^= n << 13
                n ^= n >> 17
                n ^= n << 5
                id = f"E-{n}"

            try:
                self.manager.find_employee(id)
            except PayrollException:
                break
            else:
                self.ui.error(
                    f"Unable to register employee. ID {id} is already registered to an employee."
                )
                continue

        while True:
            name = self.ui.input("What is the employee's registered name?")

            if name == self.ui.QUIT_SIGNAL:
                return

            if len(name) == 0:
                self.ui.error("Input cannot be blank.")
                continue

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

            if len(employee_choice) == 0:
                self.ui.error("Input cannot be blank.")
                continue

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

                if len(f) == 0:
                    self.ui.error("Input cannot be blank.")
                    continue

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

    def handle_record(self):
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

            if len(id) == 0:
                self.ui.error("Input cannot be blank.")
                continue

            try:
                employee = self.manager.find_employee(id)

                try:
                    self.manager.find_attendance(employee.id)
                except PayrollException:
                    pass
                else:
                    self.ui.error(
                        f"Unable to record data. Employee {id} already has a recorded attendance."
                    )
                    continue
            except PayrollException as e:
                self.ui.error(str(e))
                continue
            break

        while True:
            try:
                i = self.ui.input("How many hours has the employee worked?")

                if i == self.ui.QUIT_SIGNAL:
                    return

                if len(i) == 0:
                    self.ui.error("Input cannot be blank.")
                    continue

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

                    if len(answer) == 0:
                        self.ui.error("Input cannot be blank.")
                        continue

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

    def handle_process_payroll(self):
        id: str

        while True:
            id = self.ui.input(
                "Who's payroll are you processing? Provide their employee ID."
            )

            if id == self.ui.QUIT_SIGNAL:
                return

            if len(id) == 0:
                self.ui.error("Input cannot be blank.")
                continue

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

    def handle_process_all_payrolls(self):
        print("Processing every payroll for every employee. This might take a while...")
        sleep(0.5)

        try:
            count = self.manager.process_all_payroll()
        except PayrollException as e:
            self.ui.error(str(e))
        else:
            self.ui.success(
                f"Successfully processed {count} employee{"s'" if count > 1 else "'s"} payroll{'s' if count > 1 else ''}."
            )
        finally:
            self.ui.back()

    def handle_search(self):
        id: str
        employee: Employee

        while True:
            id = self.ui.input("Who are you searching? Provide their employee ID.")

            if id == self.ui.QUIT_SIGNAL:
                return

            if len(id) == 0:
                self.ui.error("Input cannot be blank.")
                continue

            try:
                employee = self.manager.find_employee(id)
            except PayrollException as e:
                self.ui.error(str(e))
                continue
            break
        self.ui.employee_view(employee)
        self.ui.back()

    def handle_payslip(self):
        id: str

        while True:
            id = self.ui.input(
                "Who's payslip are you viewing? Provide their employee ID."
            )

            if id == self.ui.QUIT_SIGNAL:
                return

            if len(id) == 0:
                self.ui.error("Input cannot be blank.")
                continue

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
            self.ui.payslip_view(id, payslip)
        finally:
            self.ui.back()

    def handle_history(self):
        self.ui.history_view(self.manager.payrolls)
        self.ui.back()

    def handle_report(self):
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
            self.ui.report_view(report)
        finally:
            self.ui.back()

    def handle_exit(self):
        self.ui.exit_view()
        sleep(0.5)
        sys.exit()

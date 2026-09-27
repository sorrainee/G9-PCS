from model.attendance import AttendanceRecord
from model.deduction import Deduction
from model.employee import *
from model.exception import PayrollException


class PayrollEntry:
    def __init__(
        self,
        employee: Employee,
        attendance: AttendanceRecord,
        deductions: tuple[Deduction, ...],
        benefits: tuple[Benefit, ...],
    ):
        self.__employee = employee
        self.__attendance = attendance
        self.deductions = deductions
        self.benefits = benefits
        self.status = "Processed"

    @property
    def employee(self):
        return self.__employee

    @property
    def attendance(self):
        return self.__attendance

    def gross_pay(self) -> float:
        return self.employee.calculate_gross_pay(self.attendance)

    def net_pay(self) -> float:
        return self.gross_pay() - self.calculate_deductions()

    def calculate_absence_deduction(self) -> float:
        return self.employee.rate * (
            self.attendance.hours - self.attendance.absences * 24
        )

    def calculate_deductions(self) -> float:
        deduction = self.calculate_absence_deduction()
        for d in self.deductions:
            deduction += self.gross_pay() / d.value

        return deduction

    def calculate_benefits(self) -> float:
        benefits = 0.0
        for b in self.benefits:
            benefits += b.value

        return benefits

    def __str__(self) -> str:
        s = f"====Payslip for Employee {self.employee.id}====\nStatus: {self.status}\nName: {self.employee.name}\nHours Worked: {self.attendance.hours:,d}hrs\nRate: {self.employee.rate:,.2f}\nAmount: {self.gross_pay():,.2f}\nDeductions:\n"

        if self.attendance.absences > 0:
            s += f"Absence ({self.attendance.absences}x): {self.calculate_absence_deduction()}"

        for d in self.deductions:
            s += f"{d.name.replace('_', ' ').title()}: {self.gross_pay() - (self.gross_pay() / d.value):,.2f}\n"

        s += "\n"

        for b in self.benefits:
            s += f"{b.name.replace('_', ' ').title()}: {b.value:,.2f}"

        s += f"\nAmount Paid:\n{self.net_pay()}"

        return s


class PayrollManager:
    maximum_work_hours = 60

    def __init__(self):
        self.__employees: dict[str, Employee] = {}
        self.__attendance: dict[str, AttendanceRecord] = {}
        self.__payrolls: list[PayrollEntry] = []

    @property
    def employees(self):
        return self.__employees

    @property
    def attendance(self):
        return self.__attendance

    @property
    def payrolls(self):
        return self.__payrolls

    def employee_exists(self, employee_id: str):
        return employee_id in self.employees

    def attendance_exists(self, employee_id: str):
        return employee_id in self.attendance

    def create_employee(self, employee: Employee):
        if self.employee_exists(employee.id):
            raise PayrollException(
                f"Cannot register employee. Employee {employee.id} is already registered."
            )

        self.employees[employee.id] = employee

    def create_attendace(self, attendance: AttendanceRecord):
        if not self.employee_exists(attendance.employee_id):
            raise PayrollException(
                f"Cannot record data. Data does not belong to a registered employee {attendance.employee_id}."
            )

        if self.attendance_exists(attendance.employee_id):
            raise PayrollException(
                f"Cannot record data. Employee {attendance.employee_id} already has an attendance filled out."
            )

        if attendance.hours > self.maximum_work_hours:
            raise PayrollException(
                "Cannot record data. Work hours exceeds the maximum work hours."
            )

        self.attendance[attendance.employee_id] = attendance

    def process_payroll(self, employee_id: str):
        if not self.employee_exists(employee_id):
            raise PayrollException(
                f"No payroll to process. {employee_id} does not belong to any registered employees."
            )

        if not self.attendance_exists(employee_id):
            raise PayrollException(f"No data belongs to employee {employee_id}.")

        if self.find_payroll_entry(employee_id) != None:
            raise PayrollException(
                f"Unable to process payroll. Payroll for employee {employee_id} already exists."
            )

        employee = self.find_employee(employee_id)

        self.payrolls.append(
            PayrollEntry(
                employee,
                self.attendance[employee_id],
                (Deduction.INCOME_TAX,),
                employee.get_benefits(),
            )
        )

    def process_all_payroll(self):
        for id in self.employees:
            self.process_payroll(id)

    def find_employee(self, employee_id: str) -> Employee:
        if not self.employee_exists(employee_id):
            raise PayrollException(
                f"Employee not found. {employee_id} does not belong to any registered employees."
            )

        return self.employees[employee_id]

    def find_payroll_entry(self, employee_id: str):
        return (
            None
            if len(self.payrolls) == 0
            else next(filter(lambda e: e.employee.id == employee_id, self.payrolls))
        )

    def report(self, **kwargs):
        """
        Available kwargs:

        `payroll` filters the payrolls into the total cost per employee type. Returns a dict of employee type: payroll cost pair\n
        `net_pay` sorts the payroll cost into highest and lowest. Returns a dict containing the highest and lowest payroll\n
        `deduction` sums the total deduction of every payroll. Returns a dict containing the total amount of deductions\n
        `benefit` sums the total benefits of every payroll. Returns a dict containing the total amount of benefits of employees\n
        `employee_filter` filters the employees whether they are available for overtime or they are under the zero-payable contract.
        Possible values are `overtime` and `zero-payable`
        """
        report = {}
        try:
            for k, v in kwargs.items():
                match k:
                    case "payroll":
                        report["payroll"] = {
                            "Regular Employee": math.fsum(
                                e.net_pay()
                                for e in filter(
                                    lambda e: isinstance(e.employee, RegularEmployee),
                                    self.payrolls,
                                )
                            ),
                            "Part-time Employee": math.fsum(
                                e.net_pay()
                                for e in filter(
                                    lambda e: isinstance(e.employee, PartTimeEmployee),
                                    self.payrolls,
                                )
                            ),
                            "Commission-based Employee": math.fsum(
                                e.net_pay()
                                for e in filter(
                                    lambda e: isinstance(
                                        e.employee, CommissionEmployee
                                    ),
                                    self.payrolls,
                                )
                            ),
                        }
                    case "net_pay":
                        l = sorted(
                            self.payrolls, key=lambda e: e.net_pay(), reverse=True
                        )
                        report["net_pay"] = {"highest": l[0], "lowest": l[-1]}
                    case "deduction":
                        report["deduction"] = {
                            "total": math.fsum(
                                [e.calculate_deductions() for e in self.payrolls]
                            )
                        }
                    case "benefit":
                        report["benefit"] = {
                            "total": math.fsum(
                                [e.calculate_benefits() for e in self.payrolls]
                            )
                        }
                    case "employee_filter":
                        for f in v:
                            match f.lower():
                                case "overtime":
                                    report["employee_filter"] = {
                                        "overtime": filter(
                                            lambda e: (
                                                e.attendance.overtime_hours > 0
                                                and not isinstance(
                                                    e, CommissionEmployee
                                                )
                                            ),
                                            self.payrolls,
                                        )
                                    }
                                case "zero-payable":
                                    report["employee_filter"] = {
                                        "zero-payable": filter(
                                            lambda e: isinstance(e, CommissionEmployee),
                                            self.employees.values(),
                                        )
                                    }
        except IndexError:
            raise PayrollException(
                "Failed to generate report. There are no payrolls to formulate report from."
            )

        return report

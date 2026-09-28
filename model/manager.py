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
        daily_rate = self.employee.rate * 12 / 365
        return daily_rate * self.attendance.absences

    def calculate_deductions(self) -> float:
        deduction = (
            self.calculate_absence_deduction()
            if isinstance(self.employee, RegularEmployee)
            else 0
        )
        for d in self.deductions:
            deduction += self.gross_pay() / d.value

        return deduction

    def calculate_benefits(self) -> float:
        benefits = 0.0
        for b in self.benefits:
            benefits += b.value

        return benefits

    @override
    def __str__(self) -> str:
        green = "\033[92m"
        red = "\033[91m"
        blue = "\033[94m"
        color_end = "\033[0m"

        s = f"----  Payslip for Employee {blue}{self.employee.id}{color_end}  ----\nStatus: {blue}{self.status}{color_end}\nName: {self.employee.name}\nHours Worked: {self.attendance.hours:,d}hr(s)\nRate: {self.employee.rate:,.2f}\nAmount: {self.gross_pay():,.2f}\n\n"

        if self.attendance.absences > 0 or len(self.deductions) > 0:
            s += "Deductions:\n"

            if self.attendance.absences > 0:
                s += f"Absence ({self.attendance.absences}x): {red}{self.calculate_absence_deduction():,.2f}{color_end}\n"

            for d in self.deductions:
                s += f"{d.name.replace('_', ' ').title()}: {red}{(self.gross_pay() / d.value):,.2f}{color_end}\n"

            s += "\n"

        if len(self.benefits) > 0:
            s += "Benefits:\n"
            for b in self.benefits:
                s += f"{b.name.replace('_', ' ').title()}: {green}{b.value:,.2f}{color_end}\n"

        s += f"\nAmount Paid: {green}{self.net_pay():,.2f}{color_end}"

        return s


class PayrollManager:
    def __init__(self):
        self.__employees: dict[str, Employee] = {}
        self.__attendance: dict[str, AttendanceRecord] = {}
        self.__payrolls: list[PayrollEntry] = []

        self.__init_test_data()

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

    def payroll_exists(self, employee_id: str):
        return employee_id in [e.employee.id for e in self.payrolls]

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

        self.attendance[attendance.employee_id] = attendance

    def process_payroll(self, employee_id: str):
        if not self.employee_exists(employee_id):
            raise PayrollException(
                f"No payroll to process. {employee_id} does not belong to any registered employees."
            )

        if not self.attendance_exists(employee_id):
            raise PayrollException(f"No data belongs to employee {employee_id}.")

        if self.payroll_exists(employee_id):
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
            if self.payroll_exists(id):
                continue

            self.process_payroll(id)

    def find_employee(self, employee_id: str) -> Employee:
        if not self.employee_exists(employee_id):
            raise PayrollException(
                f"Employee not found. {employee_id} does not belong to any registered employees."
            )

        return self.employees[employee_id]

    def find_payroll_entry(self, employee_id: str):
        return next(filter(lambda e: e.employee.id == employee_id, self.payrolls))

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
                        report["net_pay"] = {
                            "highest": l[0].net_pay(),
                            "lowest": l[-1].net_pay(),
                        }
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
                        report["employee_filter"] = {"overtime": [], "zero-payable": []}
                        for f in v:
                            match f.lower():
                                case "overtime":
                                    report["employee_filter"]["overtime"] = list(
                                        filter(
                                            lambda e: (
                                                e.attendance.overtime_hours > 0
                                                and isinstance(
                                                    e.employee, RegularEmployee
                                                )
                                            ),
                                            self.payrolls,
                                        )
                                    )
                                case "zero-payable":
                                    report["employee_filter"]["zero-payable"] = list(
                                        filter(
                                            lambda e: isinstance(
                                                e.employee, CommissionEmployee
                                            ),
                                            self.payrolls,
                                        )
                                    )
        except IndexError:
            raise PayrollException(
                "Failed to generate report. There are no payrolls to formulate report from."
            )

        return report

    def __init_test_data(self):
        monthly_to_weekly = lambda s: s * 12 / 52

        employees = [
            RegularEmployee("E-001", "Janver Flores", monthly_to_weekly(60000)),
            PartTimeEmployee("E-002", "Lester Perez", 260),
            CommissionEmployee("E-003", "Mark Rafael Mallari", 15000),
            RegularEmployee("E-004", "Wester Bester", monthly_to_weekly(45000)),
            RegularEmployee("E-005", "Maxx Paxx", monthly_to_weekly(28000)),
            PartTimeEmployee("E-006", "Chrisus Jeebus", 270),
            PartTimeEmployee("E-007", "Queenie Seezy", 295),
            CommissionEmployee("E-008", "Teddie Boogey", 25000),
            CommissionEmployee("E-009", "Ophelia Jakarta", 18000),
            CommissionEmployee("E-010", "Derrick Kendrick", 20000),
        ]

        attendances = [
            AttendanceRecord("E-001", 48, 3, 2, []),
            AttendanceRecord("E-002", 32, 0, 0, []),
            AttendanceRecord("E-003", 26, 0, 0, [15000, 15000, 150000]),
            AttendanceRecord("E-004", 52, 6, 4, []),
            AttendanceRecord("E-005", 60, 12, 0, []),
            AttendanceRecord("E-006", 38, 0, 0, []),
            AttendanceRecord("E-007", 37, 0, 0, []),
            AttendanceRecord("E-008", 28, 0, 0, [25000, 26000, 25500]),
            AttendanceRecord("E-009", 24, 0, 0, [18000, 18500, 19050]),
            AttendanceRecord("E-010", 45, 0, 0, [20000, 22000, 25000]),
        ]

        for i in range(len(employees)):
            self.create_employee(employees[i])
            self.create_attendace(attendances[i])

        self.process_payroll(employees[3].id)
        self.process_payroll(employees[8].id)
        self.process_payroll(employees[6].id)
        self.process_payroll(employees[2].id)
        self.process_payroll(employees[5].id)

    @override
    def __str__(self) -> str:
        return super().__str__()

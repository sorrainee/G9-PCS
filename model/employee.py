import math
from abc import ABC, abstractmethod
from typing import override

from model.attendance import AttendanceRecord
from model.benefit import *


class Employee(ABC):
    def __init__(self, id: str, name: str, rate: float):
        self.__id = id
        self.name = name
        self.rate = rate

    @property
    def id(self) -> str:
        return self.__id

    @abstractmethod
    def calculate_gross_pay(self, attendance: AttendanceRecord) -> float:
        pass

    @abstractmethod
    def get_benefits(self) -> tuple[Benefit, ...]:
        pass

    def __str__(self) -> str:
        return f"Employee ID: {self.id}\nName: {self.name}"


class RegularEmployee(Employee):
    __overtime_entitlement = 1.5
    standard_work_hours = 40

    def __init__(self, id: str, name: str, salary: float):
        super().__init__(id, name, salary)

    def calculate_overtime_pay(self, hours: int, overtime_hours: int):
        # Formula from Fair Labor Standards Act
        overtime_rate = self.rate / self.__class__.standard_work_hours
        return (
            0
            if hours < self.__class__.standard_work_hours
            else (
                overtime_rate * self.__class__.__overtime_entitlement * overtime_hours
            )
        )

    @override
    def calculate_gross_pay(self, attendance: AttendanceRecord) -> float:
        return self.rate + self.calculate_overtime_pay(
            attendance.hours, attendance.overtime_hours
        )

    @override
    def get_benefits(self):
        return tuple([b for b in RegularBenefit])

    def __str__(self) -> str:
        return super().__str__() + f"\nSalary: {self.rate:,.2f}"


class PartTimeEmployee(Employee):
    def __init__(self, id: str, name: str, wage: float):
        super().__init__(id, name, wage)

    @override
    def calculate_gross_pay(self, attendance: AttendanceRecord) -> float:
        return self.rate * attendance.hours

    @override
    def get_benefits(self):
        return tuple([b for b in PartTimeBenefit])

    def __str__(self) -> str:
        return super().__str__() + f"\nHourly Wage: {self.rate:,.2f}"


class CommissionEmployee(Employee):
    def __init__(self, id: str, name: str, pricing: float):
        super().__init__(id, name, pricing)

    @override
    def calculate_gross_pay(self, attendance: AttendanceRecord) -> float:
        return math.fsum(attendance.sales)

    @override
    def get_benefits(self):
        return tuple([b for b in CommissionBenefit])

    def __str__(self) -> str:
        return super().__str__() + f"\nBase Pricing: {self.rate:,.2f}"

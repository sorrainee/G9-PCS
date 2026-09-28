import math
from abc import ABC, abstractmethod
from typing import override

from model.attendance import AttendanceRecord
from model.benefit import *
from view.enums import Color


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

    @override
    def __str__(self) -> str:
        return f"Employee ID: {Color.BLUE.value}{self.id}{Color.END.value}\nName: {self.name}"

    @override
    def __eq__(self, value: object, /) -> bool:
        if isinstance(value, Employee):
            return self.id == value.id
        return super().__eq__(value)


class RegularEmployee(Employee):
    # sourced from wage.is Philippines
    overtime_entitlement = 1.25
    standard_work_hours = 48  # Weekly

    def __init__(self, id: str, name: str, salary: float):
        super().__init__(id, name, salary)

    def calculate_overtime_pay(self, hours: int, overtime_hours: int):
        # Formula from FLSA
        overtime_rate = self.rate / self.__class__.standard_work_hours
        return (
            0
            if hours < self.__class__.standard_work_hours
            else (overtime_rate * self.__class__.overtime_entitlement * overtime_hours)
        )

    @override
    def calculate_gross_pay(self, attendance: AttendanceRecord) -> float:
        return self.rate + self.calculate_overtime_pay(
            attendance.hours, attendance.overtime_hours
        )

    @override
    def get_benefits(self):
        return tuple([b for b in RegularBenefit])

    @override
    def __str__(self) -> str:
        return (
            super().__str__()
            + f"\nSalary: {Color.GREEN.value}{self.rate:,.2f}{Color.END.value}"
        )


class PartTimeEmployee(Employee):
    def __init__(self, id: str, name: str, wage: float):
        super().__init__(id, name, wage)

    @override
    def calculate_gross_pay(self, attendance: AttendanceRecord) -> float:
        return self.rate * attendance.hours

    @override
    def get_benefits(self):
        return tuple([b for b in PartTimeBenefit])

    @override
    def __str__(self) -> str:
        return (
            super().__str__()
            + f"\nHourly Wage: {Color.GREEN.value}{self.rate:,.2f}{Color.END.value}"
        )


class CommissionEmployee(Employee):
    def __init__(self, id: str, name: str, pricing: float):
        super().__init__(id, name, pricing)

    @override
    def calculate_gross_pay(self, attendance: AttendanceRecord) -> float:
        return math.fsum(attendance.sales)

    @override
    def get_benefits(self):
        return tuple([b for b in CommissionBenefit])

    @override
    def __str__(self) -> str:
        return (
            super().__str__()
            + f"\nBase Pricing: {Color.GREEN.value}{self.rate:,.2f}{Color.END.value}"
        )

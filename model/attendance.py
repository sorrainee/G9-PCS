from typing import override


class AttendanceRecord:
    def __init__(
        self,
        employee_id: str,
        hours: int,
        overtime_hours: int,
        absences: int,
        sales: list[float],
    ) -> None:
        self.__employee_id = employee_id
        self.hours = hours
        self.overtime_hours = overtime_hours
        self.absences = absences
        self.sales = sales

    @property
    def employee_id(self) -> str:
        return self.__employee_id

    @override
    def __str__(self) -> str:
        return f"Employee ID: {self.employee_id}\nWork Hours: {self.hours}hr(s)\nOvertime Hours: {self.overtime_hours}hr(s)\nAbsences: {self.absences}\nSales: {','.join([f'{s:,.2f}' for s in self.sales])}"

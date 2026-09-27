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

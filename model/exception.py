from typing import override


class PayrollException(Exception):
    @override
    def __str__(self) -> str:
        return super().__str__()

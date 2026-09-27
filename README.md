# G9-PCS

A payroll and compensation system by Group 9. A python activity.

## System Overview

## Class Diagram

![UML Class Diagram](assets/class_diagram.png)

## Class Responsbility Table / CRC Card

![CRC Card](assets/crc.png)

## Test Cases

| Test ID | Test Objective                                 | Input                                                                                                                                                                   | Expected Result                                                                        | Actual Result                                                                          | Status |
| :-----: | :--------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------- | :----: |
|    1    | Register at least 3 employees                  | RegularEmployee(id="E-001", name="JF FJ", rate=45000), PartTimeEmployee(id="E-002", name="SA CU", rate=67000), CommissionEmployee(id="E-003", name="VN YA", rate=35000) | Registered employees will be added to the collection                                   | Registered employees were added to the collection                                      |  Pass  |
|    2    | Reject an employee with an existing ID         | Employee ID: "E-001"                                                                                                                                                    | Halt operation and show an error message                                               | Halted operation and showed an error message                                           |  Pass  |
|    3    | Record valid work data                         | Employee ID: "E-001", Hours worked: 42, Overtime hours: 2, Absences: 0                                                                                                  | Operation will register work data for the employee and show a success message          | Operation registered work data for the employee and displayed a success message        |  Pass  |
|    4    | Reject impossible hours                        | Work hour: -45                                                                                                                                                          | Operation will not proceed and will show an error message about the minimum work hours | Operation did not proceed and showed an error message about the minimum work hours     |  Pass  |
|    5    | Process one payroll per employee type          |                                                                                                                                                                         |                                                                                        |                                                                                        |  Pass  |
|    6    | Reject payroll for employees without work data | Employee ID: "E-001"                                                                                                                                                    | Operation halts and will show an error message about insufficient data                 | Operation did not proceed and showed an error message about insufficient employee data |  Pass  |
|    7    | Reject duplicate payroll processing            |                                                                                                                                                                         |                                                                                        |                                                                                        |  Pass  |
|    8    | Generate payslip and verify computations       |                                                                                                                                                                         |                                                                                        |                                                                                        |  Pass  |

## Screenshots

![Main view](assets/main.png)
_Screenshot of main view displaying the different operations available_

![Register view](assets/register.png)
_Screenshot of the register view with a successful operation_

![Attendance view](assets/record.png)
_Screenshot of the attendance record view with a successful operation_

![Payroll view](assets/payroll.png)
_Screenshot of the payroll view for an employee with a successful operation_

![Payroll All view](assets/payroll_all.png)
_Screenshot of the payroll view for every employee with a successful operation_

![Search view](assets/search.png)
_Screenshot of the search view with a successful operation_

![Payslip view](assets/payslip.png)
_Screenshot of the payslip view with a successful operation_

![Payslip History view](assets/history.png)
_Screenshot of the payslip histor with a successful operation_

![Report view](assets/history.png)
_Screenshot of the report view with a successful operation_

![Exit view](assets/exit.png)
_Screenshot of the exit view_

![Register Failed view](assets/register_failed.png)
_Screenshot of the register view with an invalid operation_

![Search Failed view](assets/search_failed.png)
_Screenshot of the search view with an invalid operation_

## Reflection

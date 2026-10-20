# Music School Management System (MSMS)

## 1. Project Overview

The Music School Management System (MSMS) is a Python application for managing students, teachers, courses, attendance and payments at a music school.

The application uses Streamlit to provide a web interface. The ScheduleManager class handles the main application logic and saves data in a JSON file.

## 2. Main Features

### Student Management
- Search for students by name or ID.
- Register new students with their name and first instrument.
- Save student information to the JSON data file.

### Daily Roster and Attendance
- View lessons by day of the week.
- Display course names, instruments, teachers, times and rooms.
- Check in students who are enrolled in the selected course.
- Save attendance records with timestamps.

### Finance and Payments
- Record payments for existing students.
- Store the payment amount, payment method and timestamp.
- View a student's payment history.
- Export finance and attendance records to CSV files.

### Logging and Data Backup
- Record important application events in `msms.log`.
- Create timestamped JSON backups in `data/backups`.
- Keep a backup of the data before starting an application session.

## 3. Project Structure

text
PST5 Material/
├── app/
│   ├── admin_utils.py
│   ├── schedule.py
│   ├── student.py
│   ├── teacher.py
│   └── user.py
├── data/
│   ├── msms.json
│   └── backups/
├── gui/
│   ├── finance_pages.py
│   ├── main_dashboard.py
│   ├── roster_pages.py
│   └── student_pages.py
├── tests/
│   └── test_schedule_manager.py
├── main.py
├── Fragment5_1.py
├── Fragment5_2.py
└── README.md


## 4. Requirements

The project uses Python and the following packages:

- Streamlit
- pandas
- pytest

Install the packages from the project root directory using:

bash
python -m pip install streamlit pandas pytest


## 5. How to Run the Application

Open a terminal in the project root directory and run:

bash
streamlit run main.py


Open the local URL shown in the terminal if the browser does not open automatically.

Use the sidebar to navigate between Student Management, Daily Roster and Payments.

## 6. How to Run the Tests

Run the automated test suite with:

bash
python -m pytest -v


The tests cover course creation, payment recording, payment history, rejection of payments for unknown students, saving and reloading payment data, attendance persistence and CSV report export.

## 7. Data Storage

Application data is stored in `data/msms.json`.

The JSON file contains student, teacher, course and attendance information. Payment records are stored in the `finance_log` field.

When the application saves data, the existing attendance and payment records are included so that they are not lost during normal updates.

CSV reports can be exported for finance and attendance records.

## 8. Design Choices and Assumptions

- `ScheduleManager` handles the main business logic and data storage.
- The GUI pages call methods on the shared ScheduleManager instance.
- JSON is used for persistent storage because it is simple to read and update.
- Payment records require an existing student, a positive amount and a non-empty payment method.
- Attendance can only be recorded when the student and course exist and the student is enrolled in that course.
- Logging and timestamped backups help with checking application events and protecting data.

## 9. Current Test Result

The automated test suite was run using:

bash
python -m pytest -v


The latest test run passed all 7 tests.

Tests should be run again after any changes to the source code.


import csv
import datetime
import json
import logging
import os

from app.student import StudentUser
from app.teacher import TeacherUser, Course


class ScheduleManager:
    """Manages students, teachers, courses, attendance and payments."""

    def __init__(self, data_path="data/msms.json"):
        self.data_path = data_path

        self.students = []
        self.teachers = []
        self.courses = []
        self.attendance_log = []
        self.finance_log = []

        self.next_lesson_id = 1

        self._load_data()

    def _load_data(self):
        """Loads application data from a JSON file."""
        try:
            with open(self.data_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            self.students = []
            for item in data.get("students", []):
                student = StudentUser(item["id"], item["name"])
                student.enrolled_course_ids = item.get(
                    "enrolled_course_ids", []
                )

                if "instrument" in item:
                    student.instrument = item["instrument"]

                self.students.append(student)

            self.teachers = []
            for item in data.get("teachers", []):
                teacher = TeacherUser(
                    item["id"],
                    item["name"],
                    item.get("speciality", "")
                )
                self.teachers.append(teacher)

            self.courses = []
            for item in data.get("courses", []):
                course = Course(
                    item["id"],
                    item["name"],
                    item.get("instrument", ""),
                    item.get("teacher_id")
                )
                course.enrolled_student_ids = item.get(
                    "enrolled_student_ids", []
                )
                course.lessons = item.get("lessons", [])
                self.courses.append(course)

            # Support existing data files without a finance_log key.
            self.attendance_log = data.get("attendance", [])
            self.finance_log = data.get("finance_log", [])

            lesson_ids = [
                lesson.get("lesson_id", 0)
                for course in self.courses
                for lesson in course.lessons
            ]
            self.next_lesson_id = max(lesson_ids, default=0) + 1

        except FileNotFoundError:
            logging.warning(
                "Data file %s was not found. Starting with empty data.",
                self.data_path
            )

        except (json.JSONDecodeError, KeyError, TypeError) as error:
            logging.error("Could not load data: %s", error)
            raise

    def _save_data(self):
        """Saves application data to the JSON file."""
        data_to_save = {
            "students": [],
            "teachers": [],
            "courses": [],
            "attendance": self.attendance_log,
            "finance_log": self.finance_log
        }

        for student in self.students:
            student_data = {
                "id": student.id,
                "name": student.name,
                "enrolled_course_ids": student.enrolled_course_ids
            }

            if hasattr(student, "instrument"):
                student_data["instrument"] = student.instrument

            data_to_save["students"].append(student_data)

        for teacher in self.teachers:
            data_to_save["teachers"].append({
                "id": teacher.id,
                "name": teacher.name,
                "speciality": teacher.speciality
            })

        for course in self.courses:
            data_to_save["courses"].append({
                "id": course.id,
                "name": course.name,
                "instrument": course.instrument,
                "teacher_id": course.teacher_id,
                "enrolled_student_ids": course.enrolled_student_ids,
                "lessons": course.lessons
            })

        directory = os.path.dirname(self.data_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(self.data_path, "w", encoding="utf-8") as file:
            json.dump(data_to_save, file, indent=4)

    def find_student_by_id(self, student_id):
        """Finds a student by ID."""
        for student in self.students:
            if student.id == student_id:
                return student
        return None

    def find_course_by_id(self, course_id):
        """Finds a course by ID."""
        for course in self.courses:
            if course.id == course_id:
                return course
        return None

    def find_students(self, search_term):
        """Finds students by matching their name or ID."""
        term = str(search_term).strip().lower()
        results = []

        for student in self.students:
            if (
                term in student.name.lower()
                or term in str(student.id).lower()
            ):
                results.append({
                    "id": student.id,
                    "name": student.name,
                    "instrument": getattr(student, "instrument", ""),
                    "enrolled_course_ids": student.enrolled_course_ids
                })

        return results

    def register_new_student(self, name, instrument):
        """Registers a new student and saves the information."""
        name = name.strip()
        instrument = instrument.strip()

        if not name or not instrument:
            logging.warning("Student registration rejected: empty fields.")
            return False

        student_ids = [student.id for student in self.students]
        new_id = max(student_ids, default=0) + 1

        student = StudentUser(new_id, name)
        student.instrument = instrument

        self.students.append(student)
        self._save_data()

        logging.info(
            "Registered student %s with ID %s.",
            name,
            new_id
        )
        return True

    def create_course(self, name, instrument, teacher_id):
        """Creates a course and saves it."""
        name = name.strip()
        instrument = instrument.strip()

        if not name or not instrument:
            logging.warning("Course creation rejected: empty fields.")
            return False

        course_ids = [course.id for course in self.courses]
        new_id = max(course_ids, default=0) + 1

        course = Course(new_id, name, instrument, teacher_id)
        self.courses.append(course)
        self._save_data()

        logging.info("Created course %s with ID %s.", name, new_id)
        return course

    def check_in(self, student_id, course_id):
        """Records attendance only when the student is enrolled."""
        student = self.find_student_by_id(student_id)
        course = self.find_course_by_id(course_id)

        if not student or not course:
            logging.warning(
                "Check-in failed: invalid student or course ID."
            )
            return False

        is_enrolled = (
            student_id in course.enrolled_student_ids
            or course_id in student.enrolled_course_ids
        )

        if not is_enrolled:
            logging.warning(
                "Check-in rejected: student %s is not enrolled "
                "in course %s.",
                student_id,
                course_id
            )
            return False

        record = {
            "student_id": student_id,
            "course_id": course_id,
            "timestamp": datetime.datetime.now().isoformat()
        }

        self.attendance_log.append(record)
        self._save_data()

        logging.info(
            "Student %s checked into course %s.",
            student_id,
            course_id
        )
        return True

    def record_payment(self, student_id, amount, method):
        """Records a payment for an existing student."""
        student = self.find_student_by_id(student_id)

        if not student:
            logging.warning(
                "Payment rejected: student ID %s was not found.",
                student_id
            )
            return False

        try:
            amount = float(amount)
        except (TypeError, ValueError):
            return False

        method = str(method).strip()

        if amount <= 0 or not method:
            return False

        payment_record = {
            "student_id": student_id,
            "amount": round(amount, 2),
            "method": method,
            "timestamp": datetime.datetime.now().isoformat()
        }

        self.finance_log.append(payment_record)
        self._save_data()

        logging.info(
            "Payment of %.2f recorded for student ID %s.",
            amount,
            student_id
        )
        return True

    def get_payment_history(self, student_id):
        """Returns payment records for one student."""
        return [
            payment
            for payment in self.finance_log
            if payment["student_id"] == student_id
        ]

    def export_report(self, kind, out_path):
        """Exports finance or attendance records to a CSV file."""
        if kind == "finance":
            records = self.finance_log
            headers = ["student_id", "amount", "method", "timestamp"]

        elif kind == "attendance":
            records = self.attendance_log
            headers = ["student_id", "course_id", "timestamp"]

        else:
            logging.error("Unknown report type: %s", kind)
            return False

        directory = os.path.dirname(out_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        try:
            with open(
                out_path, "w", newline="", encoding="utf-8"
            ) as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=headers,
                    extrasaction="ignore"
                )
                writer.writeheader()
                writer.writerows(records)

            logging.info("Exported %s report to %s.", kind, out_path)
            return True

        except OSError as error:
            logging.error("Could not export report: %s", error)
            return False

    def cancel_lesson(self, lesson_id, reason):
        """Cancels a lesson and logs the reason."""
        for course in self.courses:
            for lesson in course.lessons:
                if lesson.get("lesson_id") == lesson_id:
                    course.lessons.remove(lesson)
                    self._save_data()

                    logging.warning(
                        "Lesson ID %s was cancelled. Reason: %s",
                        lesson_id,
                        reason
                    )
                    return True

        logging.warning(
            "Could not cancel lesson ID %s because it was not found.",
            lesson_id
        )
        return False


import csv

import pytest

from app.schedule import ScheduleManager


@pytest.fixture
def fresh_manager(tmp_path):
    """Creates a manager with a separate temporary JSON file."""
    test_file = tmp_path / "test_data.json"
    return ScheduleManager(data_path=str(test_file))


def test_create_course(fresh_manager):
    """Checks that a course can be created and saved."""
    fresh_manager.create_course("Beginner Piano", "Piano", 1)

    assert len(fresh_manager.courses) == 1
    assert fresh_manager.courses[0].name == "Beginner Piano"
    assert fresh_manager.courses[0].instrument == "Piano"


def test_record_payment_and_history(fresh_manager):
    """Checks that a payment can be recorded for an existing student."""
    assert fresh_manager.register_new_student(
        "Test Student", "Piano"
    ) is True

    student_id = fresh_manager.students[0].id

    result = fresh_manager.record_payment(
        student_id, 100.00, "Credit Card"
    )

    history = fresh_manager.get_payment_history(student_id)

    assert result is True
    assert len(history) == 1
    assert history[0]["amount"] == 100.00
    assert history[0]["method"] == "Credit Card"


def test_get_payment_history_no_results(fresh_manager):
    """Checks that a student without payments has an empty history."""
    history = fresh_manager.get_payment_history(999)

    assert history == []


def test_payment_rejects_unknown_student(fresh_manager):
    """Checks that a payment is rejected for a missing student."""
    result = fresh_manager.record_payment(
        999, 100.00, "Cash"
    )

    assert result is False
    assert fresh_manager.finance_log == []


def test_payment_persists_after_reload(fresh_manager):
    """Checks that payment data survives reloading the JSON file."""
    fresh_manager.register_new_student("Test Student", "Piano")
    student_id = fresh_manager.students[0].id

    fresh_manager.record_payment(student_id, 50.00, "Cash")

    reloaded_manager = ScheduleManager(
        data_path=fresh_manager.data_path
    )

    history = reloaded_manager.get_payment_history(student_id)

    assert len(history) == 1
    assert history[0]["amount"] == 50.00
    assert len(reloaded_manager.attendance_log) == 0


def test_check_in_persists_after_reload(fresh_manager):
    """Checks that attendance survives reloading the JSON file."""
    fresh_manager.register_new_student("Test Student", "Piano")
    student_id = fresh_manager.students[0].id

    fresh_manager.create_course("Beginner Piano", "Piano", 1)
    course_id = fresh_manager.courses[0].id

    # Enrol the student before checking in.
    fresh_manager.students[0].enrolled_course_ids.append(course_id)
    fresh_manager.courses[0].enrolled_student_ids.append(student_id)
    fresh_manager._save_data()

    result = fresh_manager.check_in(student_id, course_id)

    assert result is True

    reloaded_manager = ScheduleManager(
        data_path=fresh_manager.data_path
    )

    assert len(reloaded_manager.attendance_log) == 1
    assert reloaded_manager.attendance_log[0]["student_id"] == student_id
    assert reloaded_manager.attendance_log[0]["course_id"] == course_id


def test_export_finance_report(fresh_manager, tmp_path):
    """Checks that the finance report is written to a CSV file."""
    fresh_manager.register_new_student("Test Student", "Piano")
    student_id = fresh_manager.students[0].id

    fresh_manager.record_payment(student_id, 25.00, "Cash")

    report_path = tmp_path / "finance_report.csv"
    result = fresh_manager.export_report(
        "finance", str(report_path)
    )

    assert result is True
    assert report_path.exists()

    with open(report_path, "r", newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 1
    assert rows[0]["student_id"] == str(student_id)
    assert rows[0]["method"] == "Cash"
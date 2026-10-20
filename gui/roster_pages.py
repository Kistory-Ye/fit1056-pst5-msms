
import streamlit as st
import pandas as pd


def show_roster_page(manager):
    """Displays the daily roster and student check-in form."""
    st.header("Daily Roster")

    day = st.selectbox(
        "Select a day",
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    )

    teacher_list = {
        teacher.id: teacher.name
        for teacher in manager.teachers
    }

    # Display lessons scheduled for the selected day.
    roster = []

    for course in manager.courses:
        for lesson in course.lessons:
            if lesson.get("day") == day:
                roster.append({
                    "Course": course.name,
                    "Instrument": course.instrument,
                    "Teacher": teacher_list.get(
                        course.teacher_id, "Unknown"
                    ),
                    "Time": lesson.get("start_time", ""),
                    "Room": lesson.get("room", ""),
                    "Lesson ID": lesson.get("lesson_id", "")
                })

    st.subheader("Daily Course Schedule")

    if roster:
        st.dataframe(
            pd.DataFrame(roster),
            use_container_width=True
        )
    else:
        st.info(f"No lessons scheduled for {day}.")

    # Only allow check-in for courses scheduled on this day.
    st.subheader("Student Check-in")

    day_courses = [
        course
        for course in manager.courses
        if any(
            lesson.get("day") == day
            for lesson in course.lessons
        )
    ]

    if not day_courses:
        st.info(f"No courses are available for check-in on {day}.")
        return

    course_options = {
        f"{course.name} (ID: {course.id})": course.id
        for course in day_courses
    }

    selected_course_name = st.selectbox(
        "Select Course",
        list(course_options.keys()),
        key="check_in_course"
    )

    course_id = course_options[selected_course_name]
    selected_course = manager.find_course_by_id(course_id)

    enrolled_students = [
        student
        for student in manager.students
        if (
            student.id in selected_course.enrolled_student_ids
            or course_id in student.enrolled_course_ids
        )
    ]

    if not enrolled_students:
        st.warning("No students are enrolled in this course.")
        return

    student_options = {
        f"{student.name} (ID: {student.id})": student.id
        for student in enrolled_students
    }

    with st.form("check_in_form"):
        selected_student_name = st.selectbox(
            "Select Student",
            list(student_options.keys())
        )

        submitted = st.form_submit_button("Check-in Student")

        if submitted:
            student_id = student_options[selected_student_name]
            success = manager.check_in(student_id, course_id)

            if success:
                st.success(
                    f"Checked in {selected_student_name} "
                    f"for {selected_course_name}!"
                )
            else:
                st.error(
                    "Check-in failed. The student may not be enrolled "
                    "in this course."
                )

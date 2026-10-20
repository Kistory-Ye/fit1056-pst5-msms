import streamlit as st


def show_student_management_page(manager):
    """Displays student search and registration features."""
    st.header("Student Management")

    # Search for students by name or ID.
    st.subheader("Find a Student")
    search_term = st.text_input("Search by Name or ID")

    if search_term.strip():
        results = manager.find_students(search_term)

        if results:
            st.dataframe(results, use_container_width=True)
        else:
            st.info("No students found.")

    # Register a new student.
    st.subheader("Register a New Student")

    with st.form("registration_form"):
        reg_name = st.text_input("New Student Name")
        reg_instrument = st.text_input("First Instrument")

        submitted = st.form_submit_button("Register Student")

        if submitted:
            if not reg_name.strip() or not reg_instrument.strip():
                st.error("Please enter the student name and instrument.")
            else:
                success = manager.register_new_student(
                    reg_name,
                    reg_instrument
                )

                if success:
                    st.success(
                        f"Successfully registered {reg_name.strip()}!"
                    )
                else:
                    st.error(
                        "Registration failed. Please check the information."
                    )


import streamlit as st
import pandas as pd


def show_finance_page(manager):
    """Displays payment recording and payment history."""
    st.header("Finance & Payments")

    student_list = {
        f"{student.name} (ID: {student.id})": student.id
        for student in manager.students
    }

    # Section 1: Record a payment.
    st.subheader("Record New Payment")

    if not student_list:
        st.warning("There are no students available. Register a student first.")
    else:
        with st.form("payment_form"):
            selected_student_name = st.selectbox(
                "Select Student",
                list(student_list.keys())
            )

            amount = st.number_input(
                "Payment Amount",
                min_value=0.01,
                step=0.01,
                format="%.2f"
            )

            method = st.text_input(
                "Payment Method (e.g., Credit Card, Cash)"
            )

            submitted = st.form_submit_button("Record Payment")

            if submitted:
                if not method.strip():
                    st.error("Please enter a payment method.")
                else:
                    student_id = student_list[selected_student_name]

                    success = manager.record_payment(
                        student_id,
                        amount,
                        method.strip()
                    )

                    if success:
                        st.success(
                            f"Payment of ${amount:.2f} "
                            f"for {selected_student_name} recorded."
                        )
                    else:
                        st.error(
                            "Payment failed. Please check the student "
                            "and payment details."
                        )

    # Section 2: View payment history.
    st.subheader("View Student Payment History")

    if not student_list:
        st.info("Register a student before viewing payment history.")
    else:
        history_student_name = st.selectbox(
            "Select Student to View History",
            list(student_list.keys()),
            key="history_student"
        )

        history_student_id = student_list[history_student_name]
        history = manager.get_payment_history(history_student_id)

        if history:
            df = pd.DataFrame(history)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("This student has no payment history.")

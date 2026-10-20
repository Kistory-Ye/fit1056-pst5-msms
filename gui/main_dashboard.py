
import streamlit as st

from app.schedule import ScheduleManager
from gui.student_pages import show_student_management_page
from gui.roster_pages import show_roster_page
from gui.finance_pages import show_finance_page


def launch():
    """Sets up the main application window and navigation."""
    st.set_page_config(
        layout="wide",
        page_title="Music School Management System"
    )

    # Create one manager and keep it while navigating between pages.
    if "manager" not in st.session_state:
        st.session_state.manager = ScheduleManager()

    manager = st.session_state.manager

    st.sidebar.title("MSMS Navigation")

    page = st.sidebar.radio(
        "Go to",
        ["Student Management", "Daily Roster", "Payments"]
    )

    if page == "Student Management":
        show_student_management_page(manager)

    elif page == "Daily Roster":
        show_roster_page(manager)

    elif page == "Payments":
        show_finance_page(manager)

import streamlit as st
from datetime import date, datetime

from database.supabase_client import get_supabase_client
from views.profile import display_profile
from views.todaysrecord import display_todays_record
from views.history import display_history
from views.achievements import display_achievements
from views.settings import display_settings 
from Ui.ui_components import (
    render_water_circle,
    render_exercise_circle
)

WATER_GOAL = 2.0
EXERCISE_GOAL = 30

# - Sidebar navigation pages -

NAV_PAGES = [
    "Home",
    "My Profile",
    "Today's Record",
    "Health History",
    "Achievements",
    "Settings",
]


# - Home Page - 

def greeting_for_now():
    hour = datetime.now().hour

    if hour < 12:
        return "Good morning"
    if hour < 18:
        return "Good afternoon"
    return "Good evening"

# - mga goals -
def status_message(water, exercise, record_saved):
    """One short sentence that reacts to today's progress."""

    water_done = water >= WATER_GOAL
    exercise_done = exercise >= EXERCISE_GOAL

    if water_done and exercise_done:
        return "You hit both goals today. Nice work."

    if water_done:
        left = EXERCISE_GOAL - exercise
        return f"Water goal done. {left} more minutes of movement to go."

    if exercise_done:
        left = WATER_GOAL - water
        return f"Exercise goal done. {left:.1f} L more water to go."

    if water == 0 and exercise == 0:
        return "Nothing logged yet today. A glass of water is a good start."

    if not record_saved:
        return "Looking good so far. Don't forget to save your record."

    return "You're making progress. Keep it going."

# - bmi -
def bmi_label(bmi):
    """Return (category, streamlit color) for a BMI value."""

    if bmi < 18.5:
        return "Underweight", "blue"
    if bmi < 25:
        return "Normal", "green"
    if bmi < 30:
        return "Overweight", "orange"
    return "Obesity", "red"


def display_home(user, display_name):

    # - Load today's saved record -

    user_id = st.session_state.get("auth_user_id")

    water = 0.0
    exercise = 0
    record_saved = False
    overview_error = None

    if not user_id:
        overview_error = (
            "Your authenticated user ID is missing. "
            "Please log out and log in again."
        )

    else:
        try:
            response = (
                get_supabase_client()
                .table("health_records")
                .select("record_date, water, exercise")
                .eq("user_id", user_id)
                .eq("record_date", date.today().isoformat())
                .limit(1)
                .execute()
            )

            records = response.data or []

            if records:
                water = float(records[0].get("water") or 0)
                exercise = int(records[0].get("exercise") or 0)
                record_saved = True

        except Exception as error:
            overview_error = str(error)

    # - Header -

    st.title(f"{greeting_for_now()}, {display_name}")

    if overview_error:
        st.warning("We couldn't load today's record.")

        with st.expander("Technical details"):
            st.code(overview_error)
    else:
        st.write(status_message(water, exercise, record_saved))

    # - Today's progress (the two circles) -

    water_col, exercise_col = st.columns(2, gap="large")

    with water_col:
        st.subheader(":material/water_drop: Water")
        render_water_circle(water, WATER_GOAL)

    with exercise_col:
        st.subheader(":material/directions_run: Exercise")
        render_exercise_circle(exercise, EXERCISE_GOAL)

    if not record_saved and not overview_error:
        st.caption("Today's record hasn't been saved yet.")

    # - BMI + quick action -

    bmi_col, action_col = st.columns(2, gap="large")

    with bmi_col:

        with st.container(border=True):

            st.markdown("**:material/monitor_weight: Body Mass Index**")

            bmi = user.calculate_bmi() if user is not None else 0

            if bmi and bmi > 0:
                category, color = bmi_label(bmi)

                st.markdown(f"## {bmi:.1f}  :{color}[{category}]")
            else:
                st.write(
                    "Add your height and weight in **My Profile** "
                    "to see your BMI."
                )

    with action_col:

        with st.container(border=True):

            st.markdown("**:material/edit_calendar: Log today**")

            if st.button(
                "Open Today's Record",
                icon=":material/arrow_forward:",
                key="home_open_record",
                use_container_width=True
            ):
                st.session_state.page = "Today's Record"
                st.rerun()


def display_frontpage():

    if not st.session_state.get("logged_in", False):
        st.warning("Please log in to access HealthyMe.")
        return

    if "page" not in st.session_state:
        st.session_state.page = "Home"

    # - User Info -

    user = st.session_state.get("user")

    username = st.session_state.get("username", "User")
    nickname = st.session_state.get("nickname", "") or ""

    display_name = nickname.strip() or username

    # - Side bar -

    with st.sidebar:

        st.title(":material/favorite: HealthyMe")

        st.write(f"Signed in as **{display_name}**")

        st.divider()

        for page_name in NAV_PAGES:

            if st.button(
                page_name,
                key=f"nav_{page_name}",
                use_container_width=True
            ):
                st.session_state.page = page_name
                st.rerun()

        st.divider()

        if st.button(
            "Log Out",
            key="nav_logout",
            use_container_width=True
        ):

            # - Sign out of Supabase Auth. --
            try:
                get_supabase_client().auth.sign_out()
            except Exception:
                pass

            # - Clear this user's local Streamlit session. -
            st.session_state.clear()
            st.rerun()

    
    # - PAGES -

    if st.session_state.page == "Home":

        display_home(user, display_name)

    elif st.session_state.page == "My Profile":

        display_profile()

    elif st.session_state.page == "Today's Record":

        display_todays_record()

    elif st.session_state.page == "Health History":

        display_history()

    elif st.session_state.page == "Achievements":

        display_achievements()

    elif st.session_state.page == "Settings":

        display_settings()
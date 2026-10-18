import streamlit as st

from datetime import date
from database.supabase_client import get_supabase_client

from Ui.ui_components import (
    render_water_circle,
    render_exercise_circle
)

# - HELPER: MARK RECORD AS UNSAVED -

def mark_record_unsaved():
    st.session_state.record_saved = False


# - TODAY'S HEALTH RECORD -

def display_todays_record():

    st.title("Today's Health Record")

    st.write(
        "Keep track of your healthy habits today!"
    )

    st.divider()

    # - CHECK AUTHENTICATED USER -

    user_id = st.session_state.get("auth_user_id")

    if not user_id:
        st.error(
            "Your account session is missing. "
            "Please log out and log in again."
        )
        return

    supabase = get_supabase_client()
    today = date.today().isoformat()

    # - DEFAULT VALUES -

    if "water_goal" not in st.session_state:
        st.session_state.water_goal = 2.0

    if "water_intake" not in st.session_state:
        st.session_state.water_intake = 0.0

    if "exercise_minutes" not in st.session_state:
        st.session_state.exercise_minutes = 0

    if "record_saved" not in st.session_state:
        st.session_state.record_saved = False

    if "health_history" not in st.session_state:
        st.session_state.health_history = []

    # - LOAD TODAY'S RECORD -

    record_key = f"{user_id}:{today}"

    if st.session_state.get("loaded_record_key") != record_key:

        try:
            response = (
                supabase.table("health_records")
                .select("record_date, water, exercise")
                .eq("user_id", user_id)
                .eq("record_date", today)
                .limit(1)
                .execute()
            )

            records = response.data or []

            if records:
                saved_record = records[0]

                st.session_state.water_intake = float(
                    saved_record.get("water") or 0
                )

                st.session_state.exercise_minutes = int(
                    saved_record.get("exercise") or 0
                )

                st.session_state.record_saved = True

            else:
                st.session_state.water_intake = 0.0
                st.session_state.exercise_minutes = 0
                st.session_state.record_saved = False

            st.session_state.loaded_record_key = record_key

        except Exception as error:
            st.error(
                f"Could not load today's record from Supabase: {error}"
            )
            return

    # - WATER INTAKE -

    water = float(st.session_state.water_intake)
    goal = float(st.session_state.water_goal)

    water_col, controls_col = st.columns(
        [1, 1.2],
        gap="large"
    )

    # LEFT SIDE: WATER CIRCLE
    with water_col:
        render_water_circle(water, goal)

    # RIGHT SIDE: WATER INTAKE BUTTONS
    with controls_col:

        st.subheader("Water Intake")
        st.write("### Add Water")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("+250 mL", use_container_width=True):
                st.session_state.water_intake = min(
                    st.session_state.water_intake + 0.25,
                    goal
                )

                st.session_state.record_saved = False
                st.rerun()

        with col2:
            if st.button("+500 mL", use_container_width=True):
                st.session_state.water_intake = min(
                    st.session_state.water_intake + 0.5,
                    goal
                )

                st.session_state.record_saved = False
                st.rerun()

        with col3:
            if st.button("+1 L", use_container_width=True):
                st.session_state.water_intake = min(
                    st.session_state.water_intake + 1.0,
                    goal
                )

                st.session_state.record_saved = False
                st.rerun()

        if st.button("Reset Water", use_container_width=True):
            st.session_state.water_intake = 0.0
            st.session_state.record_saved = False
            st.rerun()

        water = float(st.session_state.water_intake)

        if water >= goal:
            st.success(
                "Amazing! You reached your daily water goal!"
            )

        elif water > 0:
            st.info(
                f"You need {goal - water:.1f} L more "
                "to reach your daily goal."
            )

        else:
            st.write(
                "Start drinking water to track your progress!"
            )

    st.divider()

    # - EXERCISE -

    exercise_goal = 30

    exercise_col, controls_col = st.columns(
        [1, 1.2],
        gap="large"
    )

    # LEFT SIDE: EXERCISE CIRCLE
    with exercise_col:
        render_exercise_circle(
            int(st.session_state.exercise_minutes),
            exercise_goal
        )

    # RIGHT SIDE: EXERCISE INPUT
    with controls_col:

        st.subheader("Exercise")

        exercise_minutes = st.number_input(
            "Exercise duration today (minutes)",
            min_value=0,
            max_value=300,
            step=5,
            key="exercise_minutes",
            on_change=mark_record_unsaved
        )

        if exercise_minutes >= exercise_goal:
            st.success(
                "Great job! You reached your exercise goal!"
            )

        elif exercise_minutes > 0:
            st.info(
                f"Only {exercise_goal - exercise_minutes} "
                "more minutes to reach your exercise goal!"
            )

        else:
            st.write(
                "Start with a few minutes of movement today!"
            )

    st.divider()

    # - SAVE RECORD TO SUPABASE -

    if st.button(
        "Save Today's Record",
        use_container_width=True
    ):

        new_record = {
            "user_id": user_id,
            "record_date": today,
            "water": float(st.session_state.water_intake),
            "exercise": int(st.session_state.exercise_minutes)
        }

        try:
            (
                supabase.table("health_records")
                .upsert(
                    new_record,
                    on_conflict="user_id,record_date"
                )
                .execute()
            )

            st.session_state.record_saved = True
            st.session_state.loaded_record_key = record_key

            # Keep the session's history copy in sync.
            history = st.session_state.health_history

            updated_record = {
                "date": today,
                "water": new_record["water"],
                "exercise": new_record["exercise"]
            }

            history = [
                record for record in history
                if record.get("date") != today
            ]

            history.append(updated_record)
            st.session_state.health_history = history

            st.success(
                "Today's health record has been saved to Supabase!"
            )

        except Exception as error:
            st.error(
                f"Could not save your health record: {error}"
            )

    # - TODAY'S SUMMARY -

    if st.session_state.get("record_saved", False):

        st.divider()
        st.subheader("Today's Summary")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Water",
                f"{st.session_state.water_intake:.1f} L"
            )

        with col2:
            st.metric(
                "Exercise",
                f"{st.session_state.exercise_minutes} min"
            )

        st.success(
            "Your record is saved for today!"
        )
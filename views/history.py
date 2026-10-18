import streamlit as st
import calendar
from datetime import date, datetime

from controllers.controller import RecordController


def parse_record_date(value):
    """Convert a database date into a Python date object."""
    try:
        return date.fromisoformat(str(value)[:10])
    except (ValueError, TypeError):
        return None


def summary_card(icon, label, value, note):
    """A bordered card with an icon label, a big number, and a note."""
    with st.container(border=True):
        st.markdown(f"{icon} **{label}**")
        st.markdown(f"## {value}")
        st.caption(note)


def display_history():

    # - PAGE HEADER -

    st.title("Health History")

    st.caption(
        "Your progress, one day at a time. "
        "Keep track of your healthy habits and celebrate every step."
    )

    st.divider()

    # - CHECK AUTHENTICATED USER -

    user_id = st.session_state.get("auth_user_id")

    if not user_id:
        st.error(
            "Your login session is missing. "
            "Please log out and log in again."
        )
        return

    # - LOAD SAVED HEALTH RECORDS -

    try:
        records = RecordController().get_all(user_id)

        history = []

        for item in records:

            parsed_date = parse_record_date(
                item.get("record_date")
            )

            if parsed_date is None:
                continue

            history.append({
                "date": parsed_date.isoformat(),
                "date_obj": parsed_date,
                "water": float(item.get("water") or 0),
                "exercise": int(item.get("exercise") or 0)
            })

    except Exception as error:

        st.error(
            "We couldn't load your health history from Supabase."
        )

        with st.expander("Technical details"):
            st.code(str(error))

        return

    # - GOALS AND MONTH SELECTOR -

    water_goal = 2.0
    exercise_goal = 30
    today = date.today()

    # Always include the current month, even if no record exists yet.
    month_keys = {
        record["date_obj"].strftime("%Y-%m")
        for record in history
    }

    month_keys.add(today.strftime("%Y-%m"))

    month_options = sorted(
        month_keys,
        reverse=True
    )

    def format_month(month_key):
        return datetime.strptime(
            month_key,
            "%Y-%m"
        ).strftime("%B %Y")

    st.subheader(":material/calendar_month: Your Monthly Overview")

    selected_month = st.selectbox(
        "Choose a month",
        options=month_options,
        format_func=format_month,
        key="history_selected_month"
    )

    month_history = [
        record for record in history
        if record["date_obj"].strftime("%Y-%m") == selected_month
    ]

    days_in_month = calendar.monthrange(
        int(selected_month[:4]),
        int(selected_month[5:7])
    )[1]

    # - MONTHLY SUMMARY -

    water_days = sum(
        1 for record in month_history
        if record["water"] >= water_goal
    )

    exercise_days = sum(
        1 for record in month_history
        if record["exercise"] >= exercise_goal
    )

    healthy_days = sum(
        1 for record in month_history
        if (
            record["water"] >= water_goal
            and record["exercise"] >= exercise_goal
        )
    )

    saved_records = len(month_history)

    col1, col2 = st.columns(2)

    with col1:
        summary_card(
            ":material/water_drop:",
            "Water Goal Days",
            water_days,
            "Days with at least 2.0 L of water recorded."
        )

    with col2:
        summary_card(
            ":material/directions_run:",
            "Exercise Goal Days",
            exercise_days,
            "Days with at least 30 minutes of exercise recorded."
        )

    col3, col4 = st.columns(2)

    with col3:
        summary_card(
            ":material/favorite:",
            "Healthy Days",
            healthy_days,
            "Days when both goals were reached."
        )

    with col4:
        summary_card(
            ":material/assignment:",
            "Saved Records",
            saved_records,
            "Daily records saved this month."
        )

    st.divider()

    # - MONTHLY PROGRESS -

    st.subheader(":material/trending_up: Your Progress")

    st.caption(
        "Progress is based on the number of days each goal was reached "
        "out of the total days in the selected month."
    )

    water_progress = min(
        water_days / days_in_month,
        1.0
    )

    exercise_progress = min(
        exercise_days / days_in_month,
        1.0
    )

    st.markdown(":material/water_drop: **Water Goal**")

    st.progress(
        water_progress,
        text=f"{water_days} / {days_in_month} days reached"
    )

    st.markdown(":material/directions_run: **Exercise Goal**")

    st.progress(
        exercise_progress,
        text=f"{exercise_days} / {days_in_month} days reached"
    )

    st.divider()

    # - RECENT RECORDS -

    st.subheader(":material/receipt_long: Recent Records")

    if not month_history:

        st.info(
            f"No health records saved for {format_month(selected_month)} yet. "
            "Go to Today's Record and save your water intake and exercise."
        )

    else:

        sorted_history = sorted(
            month_history,
            key=lambda record: record["date"],
            reverse=True
        )

        for record in sorted_history:

            record_date = record["date_obj"]
            water = record["water"]
            exercise = record["exercise"]

            water_reached = water >= water_goal
            exercise_reached = exercise >= exercise_goal

            if water_reached and exercise_reached:
                status = ":material/celebration: Both goals reached!"
            elif water_reached or exercise_reached:
                status = ":material/thumb_up: One goal reached!"
            else:
                status = ":material/trending_up: Keep going!"

            with st.container(border=True):

                date_col, water_col, exercise_col = st.columns(
                    [1.5, 1, 1]
                )

                with date_col:

                    st.markdown(
                        f"**{record_date.strftime('%b %d, %Y')}**"
                    )

                    st.caption(status)

                with water_col:

                    st.markdown(":material/water_drop: **Water**")
                    st.write(f"{water:.1f} L")

                    if water_reached:
                        st.caption(
                            ":material/check_circle: :green[Goal reached]"
                        )
                    else:
                        st.caption("Goal not reached")

                with exercise_col:

                    st.markdown(":material/directions_run: **Exercise**")
                    st.write(f"{exercise} min")

                    if exercise_reached:
                        st.caption(
                            ":material/check_circle: :green[Goal reached]"
                        )
                    else:
                        st.caption("Goal not reached")

    st.divider()

    # - MOTIVATION -

    st.subheader(":material/favorite: Keep Going!")

    if healthy_days > 0:

        st.success(
            f"You had {healthy_days} healthy "
            f"{'day' if healthy_days == 1 else 'days'} "
            f"in {format_month(selected_month)}. "
            "Keep building those habits!"
        )

    else:

        st.info(
            "Every saved record is a step forward. "
            "Keep tracking your water and exercise each day!"
        )
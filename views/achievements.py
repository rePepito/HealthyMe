import streamlit as st
from datetime import date, timedelta
from controllers.controller import ProfileController, RecordController


def longest_streak(dates):
    """Return the longest run of consecutive days in a set of dates."""
    best = 0
    current = 0
    previous = None

    for day in sorted(dates):

        if previous is not None and day - previous == timedelta(days=1):
            current += 1
        else:
            current = 1

        best = max(best, current)
        previous = day

    return best


def render_achievement(unlocked, icon, title, done_text, todo_text):
    """Show one achievement card: green when unlocked, locked otherwise."""

    if unlocked:
        st.success(
            f"**{title} — Unlocked!**\n\n{done_text}",
            icon=icon
        )
    else:
        st.info(
            f"**{title}**\n\n{todo_text}",
            icon=":material/lock:"
        )


def display_achievements():

    st.title("Achievements")

    st.write(
        "Keep building healthy habits and collect your achievements!"
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

    # - LOAD PROFILE AND HEALTH RECORDS -

    try:

        profile_created = (
            ProfileController().get_profile(user_id) is not None
        )

        history = RecordController().get_all(user_id)

    except Exception as error:

        st.error("Could not load your achievements from Supabase.")

        with st.expander("Technical details"):
            st.code(str(error))

        return

    # - CALCULATE PROGRESS -

    water_goal = 2.0
    exercise_goal = 30

    water_goal_days = 0
    exercise_days = 0
    saved_records = len(history)

    record_dates = set()

    for record in history:

        water = float(record.get("water") or 0)
        exercise = int(record.get("exercise") or 0)

        if water >= water_goal:
            water_goal_days += 1

        if exercise >= exercise_goal:
            exercise_days += 1

        record_date = record.get("record_date")

        if record_date:

            try:
                parsed_date = date.fromisoformat(
                    str(record_date)[:10]
                )

                record_dates.add(parsed_date)

            except (ValueError, TypeError):
                pass

    # - ACHIEVEMENT STATUS -

    first_record = saved_records >= 1

    hydration_hero = water_goal_days >= 1

    keep_moving = exercise_days >= 1

    # Three consecutive days with a saved health record.
    best_streak = longest_streak(record_dates)
    three_day_streak = best_streak >= 3

    # - DISPLAY ACHIEVEMENTS -

    st.subheader(":material/emoji_events: Your Achievements")

    render_achievement(
        profile_created,
        ":material/flag:",
        "First Step",
        "You created your first HealthyMe profile!",
        "Create your HealthyMe profile to unlock this achievement."
    )

    render_achievement(
        first_record,
        ":material/assignment_turned_in:",
        "HealthyMe Starter",
        "You completed your first daily health record!",
        "Save your first daily health record to unlock this achievement."
    )

    render_achievement(
        hydration_hero,
        ":material/water_drop:",
        "Hydration Hero",
        "You reached your daily water goal!",
        "Reach your 2 L daily water goal to unlock this achievement."
    )

    render_achievement(
        keep_moving,
        ":material/directions_run:",
        "Keep Moving",
        "You reached your 30-minute exercise goal!",
        "Complete 30 minutes of exercise in one day "
        "to unlock this achievement."
    )

    render_achievement(
        three_day_streak,
        ":material/local_fire_department:",
        "3-Day Streak",
        "You saved health records on three consecutive days!",
        "Save a health record on three consecutive days "
        "to unlock this achievement."
    )

    # Show streak progress so it's clear why it's locked or unlocked.
    st.caption(
        f":material/local_fire_department: Longest streak so far: "
        f"**{best_streak} {'day' if best_streak == 1 else 'days'}**"
    )

    st.divider()

    # - ACHIEVEMENT SUMMARY -

    achievements = [
        profile_created,
        first_record,
        hydration_hero,
        keep_moving,
        three_day_streak
    ]

    unlocked = sum(achievements)
    total = len(achievements)

    st.subheader(":material/trending_up: Achievement Progress")

    st.progress(
        unlocked / total,
        text=f"{unlocked} / {total} achievements unlocked"
    )

    st.write(
        f"You have unlocked **{unlocked} out of {total}** achievements."
    )

    st.divider()

    # - MOTIVATION -

    st.subheader(":material/favorite: Keep Going!")

    if unlocked == total:

        st.success(
            "Amazing! You unlocked all achievements! "
            "Keep taking care of yourself!",
            icon=":material/celebration:"
        )

    elif unlocked >= 3:

        st.info(
            "You're doing great! "
            "Keep going and unlock the remaining achievements!",
            icon=":material/local_fire_department:"
        )

    else:

        st.info(
            "Every small step counts. "
            "Keep tracking your healthy habits!",
            icon=":material/directions_walk:"
        )
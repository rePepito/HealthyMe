import streamlit as st


def display_settings():

    st.title(":material/settings: Settings")

    st.write(
        "Manage your HealthyMe account and preferences."
    )

    st.divider()

    # - ACCOUNT SETTINGS -

    st.subheader(":material/manage_accounts: Account Settings")

    new_username = st.text_input(
        "Username",
        value=st.session_state.get("username", "")
    )

    new_password = st.text_input(
        "New Password",
        type="password",
        placeholder="Leave blank to keep current password"
    )

    confirm_password = st.text_input(
        "Confirm New Password",
        type="password",
        placeholder="Re-enter your new password"
    )

    st.divider()

    # - SAVE ACCOUNT CHANGES -

    if st.button(
        "Save Changes",
        icon=":material/save:",
        use_container_width=True
    ):

        if new_username.strip() == "":

            st.error(
                "Please enter a username.",
                icon=":material/error:"
            )

        elif new_password.strip() != "":

            if new_password != confirm_password:

                st.error(
                    "Passwords do not match.",
                    icon=":material/lock:"
                )

            elif len(new_password) < 4:

                st.error(
                    "Password must be at least 4 characters.",
                    icon=":material/lock:"
                )

            else:

                st.session_state.username = new_username.strip()
                st.session_state.password = new_password

                user = st.session_state.get("user")

                if user is not None:
                    user.username = new_username.strip()

                st.success(
                    "Username and password updated successfully!",
                    icon=":material/check_circle:"
                )

        else:

            st.session_state.username = new_username.strip()

            user = st.session_state.get("user")

            if user is not None:
                user.username = new_username.strip()

            st.success(
                "Account settings updated successfully!",
                icon=":material/check_circle:"
            )

    st.divider()

    # - ACCOUNT INFORMATION -

    st.subheader(":material/badge: Account Information")

    st.write(
        f"**Username:** {st.session_state.get('username', '')}"
    )

    nickname = st.session_state.get("nickname", "").strip()

    if nickname:
        st.write(f"**Nickname:** {nickname}")
    else:
        st.write("**Nickname:** Not set")

    birthday = st.session_state.get("birthday", "")

    if birthday:
        st.write(f"**Birthday:** {birthday}")

    st.divider()

    # - REMINDERS -

    st.subheader(":material/notifications: Reminders")

    reminder = st.toggle(
        "Enable health reminders",
        key="health_reminders_enabled"
    )

    if reminder:
        st.success(
            "Health reminders are enabled!",
            icon=":material/notifications_active:"
        )
    else:
        st.info(
            "Health reminders are currently disabled.",
            icon=":material/notifications_off:"
        )

    st.divider()

    # - APP INFORMATION -

    st.subheader(":material/info: About HealthyMe")

    st.write(
        "HealthyMe is a personal health tracker "
        "designed to help users monitor their daily "
        "water intake, exercise, BMI, and health progress."
    )

    st.caption(
        "HealthyMe Prototype • Python + Streamlit"
    )
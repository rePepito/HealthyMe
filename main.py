import re
from pathlib import Path

import streamlit as st
from importlib import import_module
from models.user import HealthyMeUser
from database.supabase_client import get_supabase_client


st.set_page_config(
    page_title="HealthyMe",
    page_icon=":material/favorite:",
    layout="wide"
)

# - Styless -

_css_file = Path(__file__).parent / "Ui" / "style.css"

if _css_file.exists():
    st.markdown(
        f"<style>{_css_file.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True
    )

#---
supabase = get_supabase_client()

# Internal identifier for the username-only prototype.
# Users still enter only their username and password.

AUTH_DOMAIN = "unsnfvbjibeelkjyzkmp.supabase.co"
#----

def username_to_auth_email(username):
    username = username.strip().lower()

    if not re.fullmatch(r"[a-zA-Z0-9_-]{3,30}", username):
        raise ValueError(
            "Use 3â€“30 characters: letters, numbers, _ or -."
        )

    return f"{username}@{AUTH_DOMAIN}"


def start_user_session(auth_user, username):
    user_id = str(auth_user.id)

        # - Load this user's profile from Supabase. -
    
    result = (
        supabase.table("users")
        .select("username, nickname, birthday, height, weight, avatar_path")
        .eq("auth_user_id", user_id)
        .limit(1)
        .execute()
    )

    profiles = result.data or []

    if not profiles:
        raise ValueError(
            "Your profile was not found in the database. "
            "Please check the Supabase profile trigger."
        )

    profile = profiles[0]

    user = HealthyMeUser(
        profile["username"],
        profile.get("nickname") or "",
        profile.get("birthday") or "",
        float(profile.get("height") or 160.0),
        float(profile.get("weight") or 50.0)
    )

    st.session_state.user = user
    st.session_state.auth_user_id = user_id
    st.session_state.username = user.username
    st.session_state.nickname = user.nickname
    st.session_state.birthday = user.birthday
    st.session_state.height = user.height
    st.session_state.weight = user.weight
    st.session_state.health_goal = ""
    st.session_state.logged_in = True
    st.session_state.show_create_profile = False
    st.session_state.show_login = False

    # Clear cached daily values so the record page
    # can load the new user's data from the database.
    
    for key in (
        "water_intake",
        "exercise_minutes",
        "record_saved",
        "health_history",
        "loaded_record_key"
    ):
        st.session_state.pop(key, None)



# - SESSION STATE -

defaults = {
    "logged_in": False,
    "show_create_profile": False,
    "show_login": False,
    "username": "",
    "nickname": "",
    "birthday": "",
    "height": 160.0,
    "weight": 50.0
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# - OPEN FRONT PAGE -

if st.session_state.logged_in:
    frontpage = import_module("views.frontpage")

    if hasattr(frontpage, "display_frontpage"):
        frontpage.display_frontpage()

    st.stop()


# WELCOME PAGE (centered card)
# Styled by .st-key-auth_card in Ui/style.css

_, auth_col, _ = st.columns([1, 1.3, 1])

with auth_col.container(key="auth_card"):

    st.markdown(
        """
        <style>
        .st-key-auth_card [data-testid="stElementContainer"],
        .st-key-auth_card [data-testid="stMarkdownContainer"] {
            width: 100% !important;
        }
        .st-key-auth_card h1,
        .st-key-auth_card h3,
        .st-key-auth_card p {
            text-align: center !important;
        }
        .st-key-auth_card [data-testid="stWidgetLabel"] p {
            text-align: left !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
        
    st.title(" :material/favorite: Welcome to HealthyMe!")

    st.write(
        "Your personal health tracker for building "
        "healthy everyday habits."
    )

    st.divider()

    # - GET STARTED -

    if (
        not st.session_state.show_create_profile
        and not st.session_state.show_login
    ):
        st.markdown('<h3 style="text-align:center;">Get Started</h3>', unsafe_allow_html=True)

        if st.button(
            "Create New Profile",
            icon=":material/person_add:",
            key="btn_show_create",
            use_container_width=True
        ):
            st.session_state.show_create_profile = True
            st.rerun()

        if st.button(
            "Already Have a Profile",
            icon=":material/login:",
            key="btn_show_login",
            use_container_width=True
        ):
            st.session_state.show_login = True
            st.rerun()

    # - CREATE PROFILE -

    if st.session_state.show_create_profile:
        st.markdown('<h3 style="text-align:center;">Create Your Profile</h3>', unsafe_allow_html=True)

        #username ni
        username = st.text_input(
            "Username",
            placeholder="3–30 letters, numbers, _ or -"
        )
        #nickname ni
        nickname = st.text_input(
            "Nickname (Optional)",
            placeholder="Enter a nickname if you want"
        )
        #passworrdd
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Create your password"
        )
        #birthday
        st.write("Birthday")

        col1, col2, col3 = st.columns(3)

        with col1:
            month = st.selectbox(
                "Month",
                [
                    "January", "February", "March",
                    "April", "May", "June",
                    "July", "August", "September",
                    "October", "November", "December"
                ]
            )

        with col2:
            day = st.number_input(
                "Day",
                min_value=1,
                max_value=31,
                value=1
            )

        with col3:
            year = st.number_input(
                "Year",
                min_value=1900,
                max_value=2026,
                value=2000
            )

        birthday = f"{month} {day}, {year}"

        st.write("Body Information")

        col1, col2 = st.columns(2)

        with col1:
            height = st.number_input(
                "Height (cm)",
                min_value=1.0,
                max_value=250.0,
                value=160.0,
                step=0.1
            )

        with col2:
            weight = st.number_input(
                "Weight (kg)",
                min_value=1.0,
                max_value=300.0,
                value=50.0,
                step=0.1
            ) 
           
        st.divider()

        if st.button(
            "Create Profile",
            icon=":material/check:",
            key="btn_create_profile",
            use_container_width=True
        ):
            if not username.strip():
                st.error("Please enter a username.")

            elif not password:
                st.error("Please enter a password.")

            elif len(password) < 6:
                st.error("Password must be at least 6 characters.")

            else:
                try:
                    clean_username = username.strip().lower()
                    auth_email = username_to_auth_email(
                        clean_username
                    )

                    response = supabase.auth.sign_up({
                        "email": auth_email,
                        "password": password,
                        "options": {
                            "data": {
                                "username": clean_username,
                                "nickname": nickname.strip(),
                                "birthday": birthday,
                                "height": height,
                                "weight": weight
                            }
                        }
                    })

                    if response.user is None:
                        st.error("Account creation failed.")

                    elif response.session is None:
                        st.error(
                            "No login session was returned. "
                            "Check that Confirm email is OFF in Supabase. "
                            "This prototype uses usernames, not real emails."
                        )

                    else:
                        start_user_session(
                            response.user,
                            clean_username
                        )

                        st.success("Profile created successfully!")
                        st.rerun()

                except Exception as error:
                    st.error(f"Could not create profile: {error}")

        if st.button(
            "Back",
            icon=":material/arrow_back:",
            key="btn_back_create"
        ):
            st.session_state.show_create_profile = False
            st.rerun()

    # - LOGIN -

    if st.session_state.show_login:
        st.markdown('<h3 style="text-align:center;">Welcome Back!</h3>', unsafe_allow_html=True)

        username = st.text_input(
            "Username",
            placeholder="Enter your username"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )

        st.divider()

        if st.button(
            "Login",
            icon=":material/login:",
            key="btn_login",
            use_container_width=True
        ):
            if not username.strip():
                st.error("Please enter your username.")

            elif not password:
                st.error("Please enter your password.")

            else:
                try:
                    clean_username = username.strip().lower()
                    auth_email = username_to_auth_email(
                        clean_username
                    )

                    response = supabase.auth.sign_in_with_password({
                        "email": auth_email,
                        "password": password
                    })

                    if response.user is None:
                        st.error("Login failed. Please try again.")
                    else:
                        start_user_session(
                            response.user,
                            clean_username
                        )
                        st.rerun()

                except Exception:
                    st.error(
                        "Login failed. Check your username and password."
                    )

        if st.button(
            "Back",
            icon=":material/arrow_back:",
            key="btn_back_login"
        ):
            st.session_state.show_login = False
            st.rerun()
"""Controllers for HealthyMe (the C in MVC).

These classes hold the logic that talks to Supabase. The pages (views)
only call these methods and display the result, so no page needs to know
how the database works.

    AuthController     sign up, log in, log out
    ProfileController  load/save the profile and the profile picture
    RecordController   load/save the daily water and exercise records
"""

import re
from datetime import date

import streamlit as st

from database.supabase_client import get_supabase_client


class AuthController:
    """Accounts: sign up, log in, log out."""

    # Internal identifier for the username-only prototype.
    DEFAULT_AUTH_DOMAIN = "unsnfvbjibeelkjyzkmp.supabase.co"
    USERNAME_PATTERN = r"[a-zA-Z0-9_-]{3,30}"
    MIN_PASSWORD_LENGTH = 6

    def __init__(self):
        self._supabase = get_supabase_client()

    # ---- helpers ----

    @classmethod
    def clean_username(cls, username):
        username = (username or "").strip().lower()

        if not re.fullmatch(cls.USERNAME_PATTERN, username):
            raise ValueError(
                "Use 3–30 characters: letters, numbers, _ or -."
            )

        return username

    @classmethod
    def _auth_email(cls, username):
        domain = st.secrets.get("AUTH_DOMAIN", cls.DEFAULT_AUTH_DOMAIN)
        return f"{cls.clean_username(username)}@{domain}"

    @classmethod
    def validate_password(cls, password):
        if not password:
            raise ValueError("Please enter a password.")

        if len(password) < cls.MIN_PASSWORD_LENGTH:
            raise ValueError(
                f"Password must be at least {cls.MIN_PASSWORD_LENGTH} "
                "characters."
            )

    # ---- actions ----

    def sign_up(self, username, password, nickname, birthday, height, weight):
        """Create an account. Returns the Supabase auth response."""
        self.validate_password(password)

        return self._supabase.auth.sign_up({
            "email": self._auth_email(username),
            "password": password,
            "options": {
                "data": {
                    "username": self.clean_username(username),
                    "nickname": (nickname or "").strip(),
                    "birthday": birthday,
                    "height": height,
                    "weight": weight
                }
            }
        })

    def log_in(self, username, password):
        """Log in. Returns the Supabase auth response."""
        return self._supabase.auth.sign_in_with_password({
            "email": self._auth_email(username),
            "password": password
        })

    def log_out(self):
        """Sign out of Supabase. Never raises."""
        try:
            self._supabase.auth.sign_out()
        except Exception:
            pass


class ProfileController:
    """The user's profile row and profile picture."""

    PROFILE_FIELDS = (
        "username, nickname, birthday, "
        "height, weight, health_goal, avatar_path"
    )
    AVATAR_BUCKET = "avatars"

    def __init__(self):
        self._supabase = get_supabase_client()

    def get_profile(self, user_id):
        """Return the profile as a dict, or None if it doesn't exist."""
        response = (
            self._supabase.table("users")
            .select(self.PROFILE_FIELDS)
            .eq("auth_user_id", user_id)
            .limit(1)
            .execute()
        )

        rows = response.data or []
        return rows[0] if rows else None

    def update_profile(
        self, user_id, nickname, birthday, height, weight, health_goal
    ):
        """Save profile changes. Returns the saved row, or None."""
        response = (
            self._supabase.table("users")
            .update({
                "nickname": (nickname or "").strip(),
                "birthday": (birthday or "").strip(),
                "height": float(height),
                "weight": float(weight),
                "health_goal": (health_goal or "").strip()
            })
            .eq("auth_user_id", user_id)
            .select(self.PROFILE_FIELDS)
            .execute()
        )

        rows = response.data or []
        return rows[0] if rows else None

    def download_avatar(self, avatar_path):
        """Return the picture's bytes, or None if there is no picture."""
        if not avatar_path:
            return None

        return (
            self._supabase.storage
            .from_(self.AVATAR_BUCKET)
            .download(avatar_path)
        )

    def upload_avatar(self, user_id, photo_bytes, content_type):
        """Upload a new picture and save its path. Returns the path."""
        avatar_path = f"{user_id}/avatar"

        self._supabase.storage.from_(self.AVATAR_BUCKET).upload(
            path=avatar_path,
            file=photo_bytes,
            file_options={
                "content-type": content_type,
                "upsert": "true"
            }
        )

        response = (
            self._supabase.table("users")
            .update({"avatar_path": avatar_path})
            .eq("auth_user_id", user_id)
            .select("avatar_path")
            .execute()
        )

        if not response.data:
            raise RuntimeError(
                "The photo uploaded, but its path "
                "was not saved to your profile."
            )

        return avatar_path


class RecordController:
    """The daily health records (water and exercise)."""

    COLUMNS = "record_date, water, exercise"

    def __init__(self):
        self._supabase = get_supabase_client()

    def get_today(self, user_id):
        """Return today's record as a dict, or None if not saved yet."""
        return self.get_by_date(user_id, date.today())

    def get_by_date(self, user_id, record_date):
        response = (
            self._supabase.table("health_records")
            .select(self.COLUMNS)
            .eq("user_id", user_id)
            .eq("record_date", record_date.isoformat())
            .limit(1)
            .execute()
        )

        rows = response.data or []
        return rows[0] if rows else None

    def get_all(self, user_id):
        """Return every saved record, newest first (a list of dicts)."""
        response = (
            self._supabase.table("health_records")
            .select(self.COLUMNS)
            .eq("user_id", user_id)
            .order("record_date", desc=True)
            .execute()
        )

        return response.data or []

    def save(self, user_id, water, exercise, record_date=None):
        """Save (insert or update) one day's record."""
        record_date = record_date or date.today()

        record = {
            "user_id": user_id,
            "record_date": record_date.isoformat(),
            "water": float(water),
            "exercise": int(exercise)
        }

        (
            self._supabase.table("health_records")
            .upsert(record, on_conflict="user_id,record_date")
            .execute()
        )

        return record
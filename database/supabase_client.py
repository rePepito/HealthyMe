import streamlit as st
from supabase import create_client


class SupabaseClientProvider:
    """Creates the Supabase client once per browser session.

    The client is kept in st.session_state on purpose: it remembers the
    logged-in user's auth token, so every page shares the same login.
    """

    _SESSION_KEY = "supabase_client"

    @classmethod
    def get_client(cls):
        if cls._SESSION_KEY not in st.session_state:
            st.session_state[cls._SESSION_KEY] = cls._create_client()

        return st.session_state[cls._SESSION_KEY]

    @staticmethod
    def _create_client():
        try:
            url = st.secrets["SUPABASE_URL"]
            key = st.secrets["SUPABASE_KEY"]
        except (KeyError, FileNotFoundError):
            raise RuntimeError(
                "Supabase settings are missing. Add SUPABASE_URL and "
                "SUPABASE_KEY to .streamlit/secrets.toml."
            )

        return create_client(url, key)


def get_supabase_client():
    """Shortcut so other files can just call get_supabase_client()."""
    return SupabaseClientProvider.get_client()
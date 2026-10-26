
import streamlit as st
import base64
import hmac
from pathlib import Path

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Khwezi Mining | Monitoring System",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. LOGIN SESSION MANAGEMENT
# ==========================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = None

if "role" not in st.session_state:
    st.session_state.role = None


def authenticate_user(username, password):
    """Verify login details stored in Streamlit secrets."""

    try:
        users = st.secrets["users"]
    except (KeyError, FileNotFoundError):
        return None

    if username not in users:
        return None

    user = users[username]

    if hmac.compare_digest(
        password.encode("utf-8"),
        user["password"].encode("utf-8")
    ):
        return user["role"]

    return None


def logout_user():
    """Log out the current user."""

    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.rerun()


# ==========================================
# 3. BACKGROUND IMAGE
# ==========================================

image_path = Path(__file__).parent / "mining_bg.png"

background_css = ""

if image_path.exists():
    encoded_image = base64.b64encode(
        image_path.read_bytes()
    ).decode("utf-8")

    background_css = f"""
    background-image:
        linear-gradient(
            90deg,
            rgba(6, 16, 31, 0.94) 0%,
            rgba(6, 16, 31, 0.78) 45%,
            rgba(6, 16, 31, 0.42) 100%
        ),
        url("data:image/png;base64,{encoded_image}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    """

# ==========================================
# 4. CUSTOM CSS STYLING
# ==========================================

st.html(f"""
<style>

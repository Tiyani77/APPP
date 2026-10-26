
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
    initial_sidebar_state="expanded" if st.session_state.get("logged_in", False) else "collapsed"
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

if image_path.exists() and not st.session_state.get("logged_in", False):
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

.stApp {{
    background-color: #081525;
    {background_css}
    color: white;
}}

header[data-testid="stHeader"] {{
    background: transparent;
}}

.block-container {{
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}}

#MainMenu {{
    visibility: hidden;
}}

/* COMPANY BRAND */

.brand {{
    font-size: 23px;
    font-weight: 800;
    letter-spacing: 3px;
    color: #F5BD50;
}}

.tagline {{
    font-size: 11px;
    letter-spacing: 2px;
    color: #D6DCE6;
    margin-top: 7px;
}}

/* HERO SECTION */

.hero {{
    padding-top: 55px;
}}

.hero-line {{
    width: 65px;
    height: 5px;
    background: #F5BD50;
    margin-bottom: 25px;
}}

.hero-title {{
    font-size: clamp(44px, 5vw, 78px);
    font-weight: 800;
    line-height: 1.15;
    color: white;
    margin-bottom: 20px;
}}

.gold {{
    color: #F5BD50;
}}

.subtitle {{
    font-size: clamp(19px, 2vw, 27px);
    font-weight: 650;
    color: white;
    margin-bottom: 25px;
}}

.description {{
    font-size: 18px;
    color: #D7DFE9;
    line-height: 1.8;
    max-width: 540px;
}}

/* LOGIN PANEL */

div[data-testid="stForm"] {{
    background: rgba(12, 24, 42, 0.91);
    border: 1px solid rgba(255,255,255,0.19);
    border-radius: 20px;
    padding: 30px;
    box-shadow: 0 15px 40px rgba(0,0,0,0.25);
}}

.login-heading {{
    text-align: center;
    color: #F5BD50;
    font-size: 29px;
    font-weight: 750;
    margin-bottom: 8px;
}}

.login-subtitle {{
    text-align: center;
    color: #CFD7E2;
    font-size: 15px;
    margin-bottom: 22px;
}}

div[data-testid="stForm"] label {{
    color: white !important;
    font-weight: 500;
}}

div[data-testid="stForm"] input {{
    border-radius: 9px;
}}

div[data-testid="stFormSubmitButton"] button {{
    background: #F5BD50;
    color: #101827;
    border: none;
    border-radius: 9px;
    min-height: 50px;
    font-size: 16px;
    font-weight: 750;
    width: 100%;
}}

div[data-testid="stFormSubmitButton"] button:hover {{
    background: #FFD477;
    color: #101827;
    border: none;
}}

/* FEATURE CARDS */

.feature-card {{
    background: rgba(9, 23, 41, 0.90);
    border: 1px solid rgba(255,255,255,0.17);
    border-radius: 17px;
    padding: 25px 12px;
    min-height: 205px;
    text-align: center;
    transition: all 0.3s ease;
}}

.feature-card:hover {{
    transform: translateY(-5px);
    border-color: #F5BD50;
    background: rgba(19, 35, 55, 0.97);
}}

.feature-icon {{
    font-size: 34px;
    margin-bottom: 15px;
}}

.feature-title {{
    font-size: 16px;
    font-weight: 750;
    color: white;
    margin-bottom: 12px;
}}

.feature-text {{
    font-size: 13px;
    line-height: 1.6;
    color: #CFD8E4;
}}

/* SYSTEM STATUS */

.system-status {{
    background: rgba(12, 24, 42, 0.8);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 25px;
    padding: 12px 16px;
    color: #E8F5EE;
    font-size: 14px;
    text-align: center;
}}

.status-dot {{
    color: #26D67A;
}}

/* DASHBOARD */

.dashboard-card {{
    background: rgba(12, 24, 42, 0.92);
    border: 1px solid rgba(245,189,80,0.25);
    border-radius: 18px;
    padding: 25px;
    margin-top: 20px;
}}

.dashboard-title {{
    font-size: 38px;
    font-weight: 800;
    color: #F5BD50;
}}

.dashboard-text {{
    font-size: 17px;
    color: #D7DFE9;
    line-height: 1.7;
}}

.role-badge {{
    display: inline-block;
    background: rgba(245,189,80,0.14);
    color: #F5BD50;
    padding: 10px 18px;
    border-radius: 25px;
    border: 1px solid rgba(245,189,80,0.4);
    font-weight: 700;
    margin-top: 12px;
}}

/* LOGOUT BUTTON */

div[data-testid="stButton"] button {{
    background: #F5BD50;
    color: #101827;
    border: none;
    border-radius: 9px;
    font-weight: 750;
}}

div[data-testid="stButton"] button:hover {{
    background: #FFD477;
    color: #101827;
}}

/* FOOTER */

.footer {{
    text-align: center;
    color: #B9C4D2;
    font-size: 12px;
    margin-top: 35px;
    padding-bottom: 10px;
}}

/* RESPONSIVE DESIGN */

@media (max-width: 768px) {{
    .hero {{
        padding-top: 15px;
    }}

    .hero-title {{
        font-size: 44px;
    }}

    .feature-card {{
        min-height: 170px;
    }}

    .block-container {{
        padding-left: 1rem;
        padding-right: 1rem;
    }}
}}

</style>
""")


# ==========================================
# 5. HTML HELPER
# ==========================================

def show_html(html):
    st.html(html)


# ==========================================
# STEP 3 - PART 1: ROLE-BASED NAVIGATION
# ==========================================

ROLE_PAGES = {
    "Administrator": ["Dashboard", "Worker Safety", "Safety Incidents",
                      "Equipment Monitoring", "Maintenance", "Risk Assessment",
                      "Reports", "Manage Users"],
    "Safety Officer": ["Dashboard", "Worker Safety", "Safety Incidents",
                       "Risk Assessment", "Reports"],
    "Mining Engineer": ["Dashboard", "Worker Safety", "Safety Incidents",
                        "Equipment Monitoring", "Maintenance", "Risk Assessment", "Reports"],
    "Maintenance Engineer": ["Dashboard", "Equipment Monitoring", "Maintenance", "Reports"],
    "Manager": ["Dashboard", "Worker Safety", "Safety Incidents",
                "Equipment Monitoring", "Maintenance", "Risk Assessment", "Reports"],
}

# ==========================================
# 6. AUTHENTICATED DASHBOARD
# ==========================================

if st.session_state.logged_in:
    role = st.session_state.role
    username = st.session_state.username
    allowed_pages = ROLE_PAGES.get(role, ["Dashboard"])

    # Keep the mining photograph on the cover page only.
    st.html("""
    <style>
    [data-testid="stSidebar"] {background: #101F32;}
    [data-testid="stSidebar"] * {color: #E8EEF5;}
    </style>
    """)

    with st.sidebar:
        st.markdown("## ⛏️ KHWEZI MINING")
        st.caption("Operations Control Centre")
        st.divider()
        st.write(f"👤 **{username}**")
        st.caption(f"Role: {role}")
        st.divider()
        selected_page = st.radio("Navigation", allowed_pages)
        st.divider()
        if st.button("🚪 Logout", key="sidebar_logout", use_container_width=True):
            logout_user()

    # ==========================================
    # STEP 3 - PART 2: FUNCTIONAL PAGE CONTENT
    # ==========================================

    if selected_page == "Dashboard":
        show_html("""
        <div class="brand">⛏️ KHWEZI MINING</div>
        <div class="tagline">HEALTH | SAFETY | EQUIPMENT MONITORING</div>
        """)
        st.write("")
        st.title("⛏️ Mining Operations Dashboard")
        st.success(f"Welcome back, {username}!")
        st.write(f"Your Role: **{role}**")
        st.divider()

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("👷 Total Workers", "—")
        with col2:
            st.metric("🛡️ Safety Incidents", "—")
        with col3:
            st.metric("⚙️ Active Equipment", "—")
        with col4:
            st.metric("⚠️ Risk Alerts", "—")

        st.divider()
        st.subheader("📊 Mining Operations Overview")
        st.info("Dashboard statistics will appear once we connect the monitoring modules.")

    elif selected_page == "Worker Safety":
        st.title("👷 Worker Safety Monitoring")
        st.info("This section will monitor worker safety, PPE compliance and fatigue.")

    elif selected_page == "Safety Incidents":
        st.title("🛡️ Safety Incident Management")
        st.info("This section will record and track mining safety incidents.")

    elif selected_page == "Equipment Monitoring":
        st.title("⚙️ Equipment Monitoring")
        st.info("This section will track equipment condition, availability and performance.")

    elif selected_page == "Maintenance":
        st.title("🔧 Maintenance Management")
        st.info("This section will manage maintenance schedules and equipment repairs.")

    elif selected_page == "Risk Assessment":
        st.title("⚠️ Risk Assessment")
        st.info("This section will identify and evaluate mining operational risks.")

    elif selected_page == "Reports":
        st.title("📊 Reports and Analytics")
        st.info("This section will generate mining safety and equipment reports.")

    elif selected_page == "Manage Users":
        st.title("👥 User Management")
        st.info("This section will manage user accounts and access permissions.")

    st.stop()


# ==========================================
# 7. COVER PAGE HEADER
# ==========================================

header_left, header_right = st.columns([3, 1])

with header_left:
    show_html("""
    <div class="brand">
        ⛏️ KHWEZI MINING
    </div>

    <div class="tagline">
        SAFE PEOPLE | RELIABLE EQUIPMENT | SMARTER OPERATIONS
    </div>
    """)

with header_right:
    show_html("""
    <div class="system-status">
        <span class="status-dot">●</span>
        System Online
    </div>
    """)


# ==========================================
# 8. HERO SECTION AND LOGIN
# ==========================================

st.write("")

left, right = st.columns([1.3, 1], gap="large")

with left:
    show_html("""
    <div class="hero">
        <div class="hero-line"></div>

        <div class="hero-title">
            Khwezi <span class="gold">Mining</span>
        </div>

        <div class="subtitle">
            Health, Safety and Equipment Monitoring
        </div>

        <p class="description">
            A digital solution for safer people,
            reliable equipment and smarter
            mining operations.
        </p>
    </div>
    """)

with right:
    with st.form("login_form"):

        show_html("""
        <div class="login-heading">
            🔐 User Login
        </div>

        <div class="login-subtitle">
            Access your account to continue
        </div>
        """)

        username = st.text_input(
            "Username",
            placeholder="Enter your username"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )

        submitted = st.form_submit_button(
            "Login →",
            use_container_width=True
        )

        if submitted:

            if not username or not password:
                st.warning(
                    "Please enter your username and password."
                )

            else:
                clean_username = username.strip()

                role = authenticate_user(
                    clean_username,
                    password
                )

                if role is not None:
                    st.session_state.logged_in = True
                    st.session_state.username = clean_username
                    st.session_state.role = role

                    st.rerun()

                else:
                    st.error(
                        "Invalid username or password."
                    )


# ==========================================
# 9. APPLICATION FEATURES
# ==========================================

st.write("")
st.write("")
st.write("")

features = [
    (
        "👷",
        "Worker Safety",
        "Monitor and record worker safety information"
    ),
    (
        "🛡️",
        "Incident Tracking",
        "Identify and analyse safety incidents"
    ),
    (
        "⚙️",
        "Equipment Monitoring",
        "Track equipment condition and performance"
    ),
    (
        "🔧",
        "Maintenance",
        "Plan and manage maintenance activities"
    ),
    (
        "📊",
        "Data Analysis",
        "Visualise data and generate reports"
    )
]

columns = st.columns(5, gap="small")

for column, (icon, title, description) in zip(
    columns, features
):
    with column:
        show_html(f"""
        <div class="feature-card">
            <div class="feature-icon">{icon}</div>
            <div class="feature-title">{title}</div>
            <div class="feature-text">{description}</div>
        </div>
        """)


# ==========================================
# 10. FOOTER
# ==========================================

show_html("""
<div class="footer">
    © 2026 Khwezi Mining |
    Health, Safety & Equipment Monitoring System
</div>
""")

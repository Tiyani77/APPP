
import streamlit as st
import base64
import hmac
import hashlib
import secrets
import sqlite3
import csv
import io
import zipfile
import pandas as pd
from datetime import datetime
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


def hash_password(password, salt=None):
    """PBKDF2-HMAC password hashing for locally managed demo users."""
    salt = salt or secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), 310000
    )
    return salt, hashed.hex()


def initialise_users_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS managed_users (
                username TEXT PRIMARY KEY COLLATE NOCASE,
                password_salt TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)


def get_managed_users():
    with get_connection() as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            "SELECT username, role, active, created_at, updated_at "
            "FROM managed_users ORDER BY username"
        ).fetchall()
    return [dict(row) for row in rows]


def secret_usernames():
    try:
        return list(st.secrets["users"].keys())
    except (KeyError, FileNotFoundError):
        return []


def authenticate_user(username, password):
    """Authenticate managed users first, then legacy Streamlit Secrets accounts."""
    initialise_users_database()
    with get_connection() as connection:
        row = connection.execute(
            "SELECT password_salt, password_hash, role, active "
            "FROM managed_users WHERE username = ?", (username,)
        ).fetchone()
    if row is not None:
        salt, expected, role, active = row
        _, candidate = hash_password(password, salt)
        if active and hmac.compare_digest(candidate, expected):
            return role
        return None

    try:
        users = st.secrets["users"]
    except (KeyError, FileNotFoundError):
        return None
    if username not in users:
        return None
    user = users[username]
    if hmac.compare_digest(
        password.encode("utf-8"), user["password"].encode("utf-8")
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
# STEP 3 - PART 3: DASHBOARD STYLING
# ==========================================

st.html("""
<style>
[data-testid="stMetric"] {
    background: rgba(20, 40, 63, 0.96);
    border: 1px solid rgba(245, 189, 80, 0.35);
    border-radius: 16px;
    padding: 22px;
    min-height: 145px;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.18);
}
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] * {
    color: #D6DFEB !important;
    font-size: 15px !important;
    font-weight: 600 !important;
}
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] * {
    color: #F5BD50 !important;
    font-size: 34px !important;
    font-weight: 800 !important;
}
[data-testid="stSidebar"] {
    background: #101F32 !important;
    border-right: 1px solid rgba(245, 189, 80, 0.2);
}
[data-testid="stSidebar"] [role="radiogroup"] label {
    padding: 8px;
    border-radius: 8px;
}
h1, h2, h3 { color: #FFFFFF !important; }
hr { border-color: rgba(245, 189, 80, 0.15) !important; }
</style>
""")


# Ensure risk matrix expanders have legible dark styling.
st.html("""
<style>
[data-testid="stExpander"] {
    background: #102238 !important;
    border: 1px solid rgba(245,189,80,0.28) !important;
    border-radius: 10px !important;
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary *,
[data-testid="stExpander"] details,
[data-testid="stExpander"] details * {
    color: #F2F5FA !important;
}
</style>
""")

# ==========================================
# INPUT READABILITY FIX - LIGHT FIELDS / DARK TEXT
# ==========================================

st.html("""
<style>
/* Streamlit text areas, text inputs, dates, times and numeric fields. */
[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input,
[data-testid="stTimeInput"] input,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
    color: #142338 !important;
    -webkit-text-fill-color: #142338 !important;
    caret-color: #142338 !important;
}
[data-testid="stTextArea"] textarea::placeholder,
[data-testid="stTextInput"] input::placeholder,
[data-baseweb="input"] input::placeholder,
[data-baseweb="textarea"] textarea::placeholder {
    color: #69788b !important;
    -webkit-text-fill-color: #69788b !important;
    opacity: 1 !important;
}
/* Dropdown values and options must also be legible. */
[data-testid="stSelectbox"] [data-baseweb="select"] *,
[data-baseweb="popover"] [role="option"] {
    color: #142338 !important;
}
</style>
""")

# ==========================================
# FIX FORM LABEL CONTRAST ON DARK BACKGROUND
# ==========================================

st.html("""
<style>
/* Labels outside and inside forms should be easy to read. */
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span,
[data-testid="stWidgetLabel"] label,
[data-testid="stForm"] [data-testid="stWidgetLabel"] p {
    color: #F2F5FA !important;
    -webkit-text-fill-color: #F2F5FA !important;
    opacity: 1 !important;
    font-weight: 600 !important;
}
/* Some Streamlit versions use the widget label element directly. */
[data-testid="stTextInput"] > label,
[data-testid="stSelectbox"] > label,
[data-testid="stNumberInput"] > label,
[data-testid="stTextArea"] > label,
[data-testid="stDateInput"] > label,
[data-testid="stTimeInput"] > label {
    color: #F2F5FA !important;
    -webkit-text-fill-color: #F2F5FA !important;
    opacity: 1 !important;
}
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
# STEP 4 - WORKER SAFETY DATA (DEMO STORAGE)
# ==========================================

DATABASE_PATH = Path(__file__).parent / "khwezi_safety.db"

def get_connection():
    return sqlite3.connect(DATABASE_PATH, timeout=10)

def initialise_safety_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS safety_inspections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inspection_time TEXT NOT NULL,
                worker_id TEXT NOT NULL,
                worker_name TEXT NOT NULL,
                work_area TEXT NOT NULL,
                shift TEXT NOT NULL,
                ppe_compliant INTEGER NOT NULL,
                fatigue_level TEXT NOT NULL,
                hours_worked REAL NOT NULL,
                observation TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                recorded_by TEXT NOT NULL
            )
        """)

def calculate_risk(ppe_compliant, fatigue_level, hours_worked):
    # Demonstration-only rules; not certified mine safety limits.
    if not ppe_compliant or fatigue_level == "High" or hours_worked > 12:
        return "High"
    if fatigue_level == "Moderate" or hours_worked > 10:
        return "Medium"
    return "Low"

def get_safety_inspections():
    with get_connection() as connection:
        connection.row_factory = sqlite3.Row
        results = connection.execute(
            "SELECT * FROM safety_inspections ORDER BY id DESC"
        ).fetchall()
    return [dict(record) for record in results]

# ==========================================
# STEP 5 - SAFETY INCIDENT MANAGEMENT
# ==========================================

INCIDENT_EDITORS = {"Administrator", "Safety Officer", "Mining Engineer"}
INCIDENT_MANAGERS = {"Administrator", "Safety Officer"}

def initialise_incident_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS safety_incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reported_at TEXT NOT NULL,
                incident_date TEXT NOT NULL,
                incident_time TEXT NOT NULL,
                incident_type TEXT NOT NULL,
                work_area TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT NOT NULL,
                injury_reported INTEGER NOT NULL,
                equipment_involved INTEGER NOT NULL,
                immediate_action TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Open',
                investigation_notes TEXT NOT NULL DEFAULT '',
                reported_by TEXT NOT NULL
            )
        """)

def get_incidents():
    with get_connection() as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            "SELECT * FROM safety_incidents ORDER BY id DESC"
        ).fetchall()
    return [dict(row) for row in rows]


# ==========================================
# STEP 6 - EQUIPMENT MONITORING
# ==========================================

EQUIPMENT_EDITORS = {"Administrator", "Mining Engineer", "Maintenance Engineer"}
EQUIPMENT_STATUSES = ["Operational", "Under Maintenance", "Out of Service"]
EQUIPMENT_CONDITIONS = ["Good", "Fair", "Poor", "Critical"]

def initialise_equipment_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS mining_equipment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                equipment_code TEXT NOT NULL UNIQUE,
                equipment_name TEXT NOT NULL,
                equipment_type TEXT NOT NULL,
                work_area TEXT NOT NULL,
                operational_status TEXT NOT NULL,
                condition_rating TEXT NOT NULL,
                running_hours REAL NOT NULL DEFAULT 0,
                downtime_hours REAL NOT NULL DEFAULT 0,
                temperature_c REAL,
                vibration_mms REAL,
                last_inspection TEXT NOT NULL,
                notes TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL,
                updated_by TEXT NOT NULL
            )
        """)
        # Upgrade databases created by earlier versions without deleting records.
        existing = {row[1] for row in connection.execute("PRAGMA table_info(mining_equipment)")}
        for column, definition in {
            "downtime_hours": "REAL NOT NULL DEFAULT 0",
            "temperature_c": "REAL",
            "vibration_mms": "REAL",
        }.items():
            if column not in existing:
                connection.execute(f"ALTER TABLE mining_equipment ADD COLUMN {column} {definition}")

def get_equipment():
    with get_connection() as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            "SELECT * FROM mining_equipment ORDER BY equipment_code"
        ).fetchall()
    return [dict(row) for row in rows]

def sensor_band(value, warning_at, critical_above):
    """Educational threshold classifier; None means not measured."""
    if value is None:
        return "Not recorded"
    if value > critical_above:
        return "Critical"
    if value >= warning_at:
        return "Warning"
    return "Normal"


def temperature_band(value):
    return sensor_band(value, 80, 100)


def vibration_band(value):
    return sensor_band(value, 5, 8)


def equipment_availability(item):
    """Time-based availability = operating/(operating+downtime)*100."""
    operating = float(item["running_hours"] or 0)
    downtime = float(item["downtime_hours"] or 0)
    total = operating + downtime
    return 100 * operating / total if total > 0 else None


def equipment_needs_attention(item):
    return (item["condition_rating"] in ("Poor", "Critical")
            or item["operational_status"] != "Operational"
            or temperature_band(item["temperature_c"]) in ("Warning", "Critical")
            or vibration_band(item["vibration_mms"]) in ("Warning", "Critical"))

# ==========================================
# STEP 7 - MAINTENANCE MANAGEMENT
# ==========================================

MAINTENANCE_EDITORS = {"Administrator", "Maintenance Engineer", "Mining Engineer"}
MAINTENANCE_STATUSES = ["Open", "Scheduled", "In Progress", "Completed", "Cancelled"]
MAINTENANCE_PRIORITIES = ["Low", "Medium", "High", "Critical"]
MAINTENANCE_TYPES = ["Preventive Service", "Corrective Repair", "Inspection", "Emergency Repair", "Other"]


def initialise_maintenance_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS maintenance_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                equipment_id INTEGER NOT NULL,
                order_type TEXT NOT NULL,
                priority TEXT NOT NULL,
                description TEXT NOT NULL,
                assigned_technician TEXT NOT NULL,
                scheduled_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Open',
                completion_notes TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                created_by TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                updated_by TEXT NOT NULL,
                FOREIGN KEY(equipment_id) REFERENCES mining_equipment(id)
            )
        """)


def get_maintenance_orders():
    with get_connection() as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute("""
            SELECT m.*, e.equipment_code, e.equipment_name, e.work_area
            FROM maintenance_orders AS m
            JOIN mining_equipment AS e ON e.id = m.equipment_id
            ORDER BY m.id DESC
        """).fetchall()
    return [dict(row) for row in rows]



# ==========================================
# STEP 8 - RISK ASSESSMENT
# ==========================================

RISK_EDITORS = {"Administrator", "Safety Officer", "Mining Engineer"}
RISK_REVIEWERS = {"Administrator", "Safety Officer"}
RISK_STATUSES = ["Open", "Controls In Progress", "Under Review", "Closed"]
RISK_LIKELIHOOD = {
    "1 - Rare": 1,
    "2 - Unlikely": 2,
    "3 - Possible": 3,
    "4 - Likely": 4,
    "5 - Almost Certain": 5,
}
RISK_SEVERITY = {
    "1 - Insignificant": 1,
    "2 - Minor": 2,
    "3 - Moderate": 3,
    "4 - Major": 4,
    "5 - Catastrophic": 5,
}


def risk_band(score):
    # Illustrative 5x5 matrix. Site-approved methodology must replace it.
    if score >= 17:
        return "Critical"
    if score >= 10:
        return "High"
    if score >= 5:
        return "Medium"
    return "Low"


def initialise_risk_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS risk_assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assessment_date TEXT NOT NULL,
                work_area TEXT NOT NULL,
                activity TEXT NOT NULL,
                hazard TEXT NOT NULL,
                potential_consequence TEXT NOT NULL,
                likelihood INTEGER NOT NULL,
                severity INTEGER NOT NULL,
                risk_score INTEGER NOT NULL,
                risk_rating TEXT NOT NULL,
                existing_controls TEXT NOT NULL,
                additional_controls TEXT NOT NULL,
                responsible_person TEXT NOT NULL,
                target_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Open',
                review_notes TEXT NOT NULL DEFAULT '',
                assessed_by TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                updated_by TEXT NOT NULL
            )
        """)


def get_risk_assessments():
    with get_connection() as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            "SELECT * FROM risk_assessments ORDER BY id DESC"
        ).fetchall()
    return [dict(row) for row in rows]

# ==========================================
# STEP 9 - REPORTS READABILITY / DOWNLOAD BUTTONS
# ==========================================

st.html("""
<style>
/* Gold CSV/ZIP export buttons, with readable navy text. */
[data-testid="stDownloadButton"] button {
    background: #F5BD50 !important;
    border: 1px solid #E0A52E !important;
    color: #081525 !important;
    font-weight: 750 !important;
    border-radius: 10px !important;
    min-height: 44px !important;
}
[data-testid="stDownloadButton"] button *,
[data-testid="stDownloadButton"] button p {
    color: #081525 !important;
    -webkit-text-fill-color: #081525 !important;
}
[data-testid="stDownloadButton"] button:hover:not(:disabled) {
    background: #FFD477 !important;
    border-color: #FFD477 !important;
}
[data-testid="stDownloadButton"] button:disabled {
    background: #38485C !important;
    border-color: #46576C !important;
    color: #C5CDD8 !important;
    opacity: 0.8 !important;
}
[data-testid="stDownloadButton"] button:disabled * {
    color: #C5CDD8 !important;
    -webkit-text-fill-color: #C5CDD8 !important;
}
/* Light register tables are retained for contrast, but their data text is dark. */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(245,189,80,0.4) !important;
    border-radius: 10px !important;
    overflow: hidden;
}
/* Ensure report selectors remain readable. */
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background-color: #E9EEF5 !important;
}
/* Prevent white expander headers in the risk module. */
[data-testid="stExpander"] summary {
    background: #14283F !important;
}
</style>
""")

# ==========================================
# 6. AUTHENTICATED DASHBOARD
# ==========================================

if st.session_state.logged_in:
    role = st.session_state.role
    username = st.session_state.username
    allowed_pages = ROLE_PAGES.get(role, ["Dashboard"])
    initialise_users_database()
    initialise_safety_database()
    initialise_incident_database()
    initialise_equipment_database()
    initialise_maintenance_database()
    initialise_risk_database()
    risk_assessments = get_risk_assessments()
    maintenance_orders = get_maintenance_orders()
    equipment = get_equipment()
    inspections = get_safety_inspections()
    incidents = get_incidents()

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
            st.metric("👷 Workers Inspected", len({r["worker_id"] for r in inspections}))
        with col2:
            st.metric("🛡️ Safety Incidents", len(incidents))
        with col3:
            st.metric("⚙️ Active Equipment", sum(e["operational_status"] == "Operational" for e in equipment))
        with col4:
            st.metric("⚠️ High-Risk Inspections", sum(r["risk_level"] == "High" for r in inspections))

        st.divider()
        st.subheader("📊 Mining Operations Overview")
        st.info("Worker Safety, Safety Incidents and Equipment Monitoring are connected.")
        if equipment:
            st.warning(
                f"Equipment requiring attention: {sum(equipment_needs_attention(e) for e in equipment)}"
            )
        outstanding_maintenance = sum(
            order["status"] not in ("Completed", "Cancelled")
            for order in maintenance_orders
        )
        st.metric("🔧 Outstanding Maintenance Orders", outstanding_maintenance)
        open_risks = [r for r in risk_assessments if r["status"] != "Closed"]
        st.metric("⚠️ Open Risk Assessments", len(open_risks))
        if equipment:
            operating_total = sum(float(e["running_hours"] or 0) for e in equipment)
            downtime_total = sum(float(e["downtime_hours"] or 0) for e in equipment)
            total_hours = operating_total + downtime_total
            availability = 100 * operating_total / total_hours if total_hours else None
            st.metric("⚙️ Time-Based Equipment Availability", f"{availability:.1f}%" if availability is not None else "N/A")
            st.caption("Availability = operating hours ÷ (operating hours + downtime hours) × 100. N/A when no hours are recorded.")
            sensor_alerts = [e for e in equipment if temperature_band(e["temperature_c"]) in ("Warning", "Critical") or vibration_band(e["vibration_mms"]) in ("Warning", "Critical")]
            if sensor_alerts:
                st.error(f"🌡️ {len(sensor_alerts)} equipment item(s) have abnormal temperature or vibration readings.")
        serious_incidents = [i for i in incidents if i["severity"] in ("High", "Critical") and i["status"] != "Closed"]
        if serious_incidents:
            st.error(f"{len(serious_incidents)} high/critical safety incident(s) still require investigation or closure.")
        serious_risks = [r for r in open_risks if r["risk_rating"] in ("High", "Critical")]
        if serious_risks:
            st.error(f"{len(serious_risks)} high/critical risk assessment(s) remain open.")
        if outstanding_maintenance:
            st.warning(f"{outstanding_maintenance} maintenance work order(s) outstanding.")

    elif selected_page == "Worker Safety":
        st.title("👷 Worker Safety Monitoring")
        st.caption("Record PPE compliance, fatigue, work hours and safety observations.")

        a, b, c = st.columns(3)
        a.metric("Inspections Recorded", len(inspections))
        b.metric("High-Risk Records", sum(r["risk_level"] == "High" for r in inspections))
        c.metric("PPE Non-compliance", sum(not r["ppe_compliant"] for r in inspections))

        if role in ("Administrator", "Safety Officer"):
            st.subheader("➕ New Worker Safety Inspection")
            with st.form("new_worker_safety_inspection", clear_on_submit=True):
                left, right = st.columns(2)
                with left:
                    worker_id = st.text_input("Worker ID *", placeholder="e.g. KM001")
                    worker_name = st.text_input("Worker Name *")
                    work_area = st.selectbox("Work Area", [
                        "Open Pit", "Underground", "Processing Plant",
                        "Workshop", "Other"
                    ])
                    shift = st.selectbox("Shift", ["Day", "Night"])
                with right:
                    ppe_compliant = st.checkbox("Required PPE correctly worn", value=True)
                    fatigue_level = st.selectbox("Fatigue Level", ["Low", "Moderate", "High"])
                    hours_worked = st.number_input(
                        "Hours Worked", min_value=0.0, max_value=24.0,
                        value=8.0, step=0.5
                    )
                observation = st.text_area("Safety Observation / Notes")
                submitted_inspection = st.form_submit_button(
                    "💾 Save Inspection", use_container_width=True
                )

            if submitted_inspection:
                if not worker_id.strip() or not worker_name.strip():
                    st.error("Please enter both Worker ID and Worker Name.")
                else:
                    risk_level = calculate_risk(
                        ppe_compliant, fatigue_level, hours_worked
                    )
                    with get_connection() as connection:
                        connection.execute("""
                            INSERT INTO safety_inspections (
                                inspection_time, worker_id, worker_name,
                                work_area, shift, ppe_compliant, fatigue_level,
                                hours_worked, observation, risk_level, recorded_by
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            datetime.now().isoformat(timespec="seconds"),
                            worker_id.strip(), worker_name.strip(),
                            work_area, shift, int(ppe_compliant), fatigue_level,
                            hours_worked, observation.strip(), risk_level, username
                        ))
                    st.session_state["safety_saved_risk"] = risk_level
                    st.rerun()
        else:
            st.info("Your role can view inspections but cannot create them.")

        saved_risk = st.session_state.pop("safety_saved_risk", None)
        if saved_risk == "High":
            st.error("High-risk inspection saved. Escalate for prompt review.")
        elif saved_risk == "Medium":
            st.warning("Medium-risk inspection saved. Follow-up recommended.")
        elif saved_risk == "Low":
            st.success("Inspection saved successfully (low risk).")

        st.subheader("📋 Saved Safety Inspections")
        if inspections:
            search_term = st.text_input("Search Worker ID or Name").strip().lower()
            risk_filter = st.selectbox(
                "Filter by Risk", ["All", "Low", "Medium", "High"]
            )
            filtered = [
                r for r in inspections
                if (not search_term or search_term in r["worker_id"].lower()
                    or search_term in r["worker_name"].lower())
                and (risk_filter == "All" or r["risk_level"] == risk_filter)
            ]
            st.dataframe(filtered, use_container_width=True, hide_index=True)

            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=list(inspections[0].keys()))
            writer.writeheader()
            writer.writerows(filtered)
            st.download_button(
                "⬇️ Export Inspections as CSV",
                output.getvalue(),
                file_name="khwezi_worker_safety.csv",
                mime="text/csv"
            )
        else:
            st.info("No inspections recorded yet.")

        st.caption(
            "Demo only: risk rules are illustrative, and Streamlit Cloud local "
            "database files may be lost on restart or redeployment."
        )

    elif selected_page == "Safety Incidents":
        st.title("🛡️ Safety Incident Management")
        st.caption("Report, investigate and monitor workplace safety incidents.")

        total_incidents = len(incidents)
        open_incidents = sum(i["status"] != "Closed" for i in incidents)
        serious_incidents = sum(
            i["severity"] in ("High", "Critical") for i in incidents
        )
        a, b, c = st.columns(3)
        a.metric("Total Incidents", total_incidents)
        b.metric("Open / In Progress", open_incidents)
        c.metric("High / Critical", serious_incidents)

        if role in INCIDENT_EDITORS:
            st.subheader("➕ Report a New Incident")
            with st.form("new_incident", clear_on_submit=True):
                left, right = st.columns(2)
                with left:
                    incident_date = st.date_input("Incident Date")
                    incident_time = st.time_input("Incident Time")
                    incident_type = st.selectbox("Incident Type", [
                        "Near Miss", "Slip / Trip / Fall", "Equipment Failure",
                        "Vehicle Incident", "Falling Object", "Fire / Explosion",
                        "Hazardous Exposure", "Other"
                    ])
                    work_area = st.selectbox("Location / Work Area", [
                        "Open Pit", "Underground", "Processing Plant",
                        "Workshop", "Other"
                    ])
                with right:
                    severity = st.selectbox("Severity", [
                        "Low", "Medium", "High", "Critical"
                    ])
                    injury_reported = st.checkbox("Injury reported")
                    equipment_involved = st.checkbox("Equipment involved")
                description = st.text_area("Incident Description *")
                immediate_action = st.text_area("Immediate Action Taken *")
                submit_incident = st.form_submit_button(
                    "💾 Save Incident Report", use_container_width=True
                )

            if submit_incident:
                if not description.strip() or not immediate_action.strip():
                    st.error("Incident Description and Immediate Action are required.")
                else:
                    with get_connection() as connection:
                        connection.execute("""
                            INSERT INTO safety_incidents (
                                reported_at, incident_date, incident_time,
                                incident_type, work_area, severity, description,
                                injury_reported, equipment_involved,
                                immediate_action, status, investigation_notes,
                                reported_by
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            datetime.now().isoformat(timespec="seconds"),
                            incident_date.isoformat(), incident_time.strftime("%H:%M"),
                            incident_type, work_area, severity,
                            description.strip(), int(injury_reported),
                            int(equipment_involved), immediate_action.strip(),
                            "Open", "", username
                        ))
                    st.session_state["incident_saved"] = severity
                    st.rerun()
        else:
            st.info("Your role can view incidents but cannot submit new reports.")

        saved_severity = st.session_state.pop("incident_saved", None)
        if saved_severity in ("High", "Critical"):
            st.error("Incident saved. Escalate this serious incident immediately using your site's procedures.")
        elif saved_severity:
            st.success("Incident report saved successfully.")

        st.subheader("📋 Incident Register")
        if incidents:
            search_incident = st.text_input("Search descriptions or work areas").strip().lower()
            filter_severity = st.selectbox(
                "Filter Severity", ["All", "Low", "Medium", "High", "Critical"]
            )
            filter_status = st.selectbox(
                "Filter Status", ["All", "Open", "In Progress", "Closed"]
            )
            filtered_incidents = [
                item for item in incidents
                if (not search_incident
                    or search_incident in item["description"].lower()
                    or search_incident in item["work_area"].lower())
                and (filter_severity == "All" or item["severity"] == filter_severity)
                and (filter_status == "All" or item["status"] == filter_status)
            ]
            st.dataframe(filtered_incidents, use_container_width=True, hide_index=True)
            export = io.StringIO()
            writer = csv.DictWriter(export, fieldnames=list(incidents[0].keys()))
            writer.writeheader()
            writer.writerows(filtered_incidents)
            st.download_button(
                "⬇️ Export Incident Register (CSV)",
                data=export.getvalue(),
                file_name="khwezi_incident_register.csv", mime="text/csv"
            )

            if role in INCIDENT_MANAGERS:
                st.subheader("🔎 Update Investigation")
                with st.form("update_incident_status"):
                    incident_id = st.selectbox(
                        "Incident to Update",
                        options=[item["id"] for item in incidents],
                        format_func=lambda x: f"INC-{x:04d}"
                    )
                    chosen = next(item for item in incidents if item["id"] == incident_id)
                    statuses = ["Open", "In Progress", "Closed"]
                    new_status = st.selectbox(
                        "Investigation Status", statuses,
                        index=statuses.index(chosen["status"])
                    )
                    investigation_notes = st.text_area(
                        "Investigation Notes / Follow-up",
                        value=chosen["investigation_notes"]
                    )
                    update_submitted = st.form_submit_button("Update Investigation")
                if update_submitted:
                    with get_connection() as connection:
                        connection.execute("""
                            UPDATE safety_incidents
                            SET status = ?, investigation_notes = ?
                            WHERE id = ?
                        """, (new_status, investigation_notes.strip(), incident_id))
                    st.session_state["incident_updated"] = True
                    st.rerun()
            if st.session_state.pop("incident_updated", False):
                st.success("Investigation updated successfully.")
        else:
            st.info("No incidents have been reported yet.")

        st.caption(
            "Demo system: reports do not replace emergency response, "
            "statutory notifications or formal mine investigation procedures. "
            "Local Streamlit Cloud storage may be lost on restart or redeployment."
        )

    elif selected_page == "Equipment Monitoring":
        st.title("⚙️ Equipment Monitoring")
        st.caption("Register mining assets, inspect their condition and monitor availability.")

        total_equipment = len(equipment)
        operational_count = sum(e["operational_status"] == "Operational" for e in equipment)
        attention_count = sum(equipment_needs_attention(e) for e in equipment)
        critical_count = sum(e["condition_rating"] == "Critical" or temperature_band(e["temperature_c"]) == "Critical" or vibration_band(e["vibration_mms"]) == "Critical" for e in equipment)

        metric1, metric2, metric3, metric4 = st.columns(4)
        metric1.metric("Total Equipment", total_equipment)
        metric2.metric("Operational", operational_count)
        metric3.metric("Needs Attention", attention_count)
        metric4.metric("Critical Condition", critical_count)

        if attention_count:
            st.warning(
                f"{attention_count} equipment item(s) need attention. "
                "Review their condition and operational status."
            )

        st.caption("Prototype sensor limits: Temperature normal <80°C, warning 80–100°C, critical >100°C; vibration normal <5 mm/s, warning 5–8 mm/s, critical >8 mm/s.")
        for item in equipment:
            t_band = temperature_band(item["temperature_c"])
            v_band = vibration_band(item["vibration_mms"])
            if "Critical" in (t_band, v_band):
                st.error(f"🚨 CRITICAL — {item['equipment_code']}: Temperature {item['temperature_c']}°C ({t_band}); vibration {item['vibration_mms']} mm/s ({v_band}). Escalate for inspection.")
            elif "Warning" in (t_band, v_band):
                st.warning(f"⚠️ WARNING — {item['equipment_code']}: Temperature {item['temperature_c']}°C ({t_band}); vibration {item['vibration_mms']} mm/s ({v_band}).")

        if role in EQUIPMENT_EDITORS:
            st.subheader("➕ Register New Equipment")
            with st.form("register_equipment", clear_on_submit=True):
                left, right = st.columns(2)
                with left:
                    equipment_code = st.text_input("Equipment ID *", placeholder="e.g. HT001")
                    equipment_name = st.text_input("Equipment Name *", placeholder="e.g. Haul Truck 01")
                    equipment_type = st.selectbox("Equipment Type", [
                        "Haul Truck", "Excavator", "Drill Rig", "Loader",
                        "Bulldozer", "Conveyor", "Pump", "Other"
                    ])
                    equipment_area = st.selectbox("Equipment Work Area", [
                        "Open Pit", "Underground", "Processing Plant", "Workshop", "Other"
                    ])
                with right:
                    equipment_status = st.selectbox("Operational Status", EQUIPMENT_STATUSES)
                    equipment_condition = st.selectbox("Condition Rating", EQUIPMENT_CONDITIONS)
                    equipment_hours = st.number_input(
                        "Running Hours", min_value=0.0, value=0.0, step=1.0
                    )
                    inspection_date = st.date_input("Last Inspection Date")
                sensor_left, sensor_right = st.columns(2)
                with sensor_left:
                    equipment_temp = st.number_input("Temperature (°C)", min_value=0.0, value=60.0, step=1.0, key="new_equipment_temp")
                    equipment_downtime = st.number_input("Downtime Hours", min_value=0.0, value=0.0, step=1.0, key="new_equipment_downtime")
                with sensor_right:
                    equipment_vibration = st.number_input("Vibration (mm/s)", min_value=0.0, value=3.0, step=0.5, key="new_equipment_vibration")
                equipment_notes = st.text_area("Equipment Notes")
                add_equipment = st.form_submit_button(
                    "💾 Save Equipment", use_container_width=True
                )

            if add_equipment:
                if not equipment_code.strip() or not equipment_name.strip():
                    st.error("Equipment ID and Equipment Name are required.")
                elif inspection_date > datetime.now().date():
                    st.error("Last Inspection Date cannot be in the future.")
                else:
                    try:
                        with get_connection() as connection:
                            connection.execute("""
                                INSERT INTO mining_equipment (
                                    equipment_code, equipment_name, equipment_type,
                                    work_area, operational_status, condition_rating,
                                    running_hours, downtime_hours, temperature_c, vibration_mms,
                                    last_inspection, notes, updated_at, updated_by
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                equipment_code.strip().upper(), equipment_name.strip(),
                                equipment_type, equipment_area, equipment_status,
                                equipment_condition, equipment_hours,
                                equipment_downtime, equipment_temp, equipment_vibration,
                                inspection_date.isoformat(), equipment_notes.strip(),
                                datetime.now().isoformat(timespec="seconds"), username
                            ))
                        st.session_state["equipment_saved"] = (temperature_band(equipment_temp), vibration_band(equipment_vibration))
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("That Equipment ID already exists. Use a unique ID.")
        else:
            st.info("Your role can view equipment but cannot register or update it.")

        saved_bands = st.session_state.pop("equipment_saved", None)
        if saved_bands:
            st.success("Equipment registered successfully.")
            if "Critical" in saved_bands:
                st.error("CRITICAL sensor reading saved. Escalate immediately using site procedures.")
            elif "Warning" in saved_bands:
                st.warning("Abnormal sensor reading saved. Inspection recommended.")
        updated_bands = st.session_state.pop("equipment_updated", None)
        if updated_bands:
            st.success("Equipment status and inspection details updated.")
            if "Critical" in updated_bands:
                st.error("CRITICAL equipment sensor reading. Escalate for immediate review.")
            elif "Warning" in updated_bands:
                st.warning("Equipment sensor warning. Inspection recommended.")

        st.subheader("📋 Equipment Register")
        if equipment:
            equipment_search = st.text_input(
                "Search Equipment ID, Name or Type"
            ).strip().lower()
            equipment_filter = st.selectbox(
                "Filter Equipment Status", ["All"] + EQUIPMENT_STATUSES
            )
            filtered_equipment = [
                e for e in equipment
                if (not equipment_search
                    or equipment_search in e["equipment_code"].lower()
                    or equipment_search in e["equipment_name"].lower()
                    or equipment_search in e["equipment_type"].lower())
                and (equipment_filter == "All"
                     or e["operational_status"] == equipment_filter)
            ]
            display_equipment = []
            for item in filtered_equipment:
                entry = dict(item)
                entry["temperature_status"] = temperature_band(item["temperature_c"])
                entry["vibration_status"] = vibration_band(item["vibration_mms"])
                av = equipment_availability(item)
                entry["availability_percent"] = round(av, 1) if av is not None else None
                display_equipment.append(entry)
            st.dataframe(display_equipment, use_container_width=True, hide_index=True)

            csv_buffer = io.StringIO()
            csv_writer = csv.DictWriter(
                csv_buffer, fieldnames=list(equipment[0].keys())
            )
            csv_writer.writeheader()
            csv_writer.writerows(filtered_equipment)
            st.download_button(
                "⬇️ Export Equipment Register (CSV)",
                csv_buffer.getvalue(),
                file_name="khwezi_equipment_register.csv",
                mime="text/csv"
            )

            if role in EQUIPMENT_EDITORS:
                st.subheader("🔧 Update Equipment Condition / Status")
                equipment_ids = [e["id"] for e in equipment]
                selected_equipment_id = st.selectbox(
                    "Select Equipment",
                    equipment_ids,
                    format_func=lambda x: next(
                        e["equipment_code"] + " — " + e["equipment_name"]
                        for e in equipment if e["id"] == x
                    )
                )
                chosen_equipment = next(
                    e for e in equipment if e["id"] == selected_equipment_id
                )
                with st.form(f"update_equipment_{selected_equipment_id}"):
                    left, right = st.columns(2)
                    with left:
                        updated_status = st.selectbox(
                            "Update Operational Status", EQUIPMENT_STATUSES,
                            index=EQUIPMENT_STATUSES.index(
                                chosen_equipment["operational_status"]
                            )
                        )
                        updated_condition = st.selectbox(
                            "Update Condition", EQUIPMENT_CONDITIONS,
                            index=EQUIPMENT_CONDITIONS.index(
                                chosen_equipment["condition_rating"]
                            )
                        )
                    with right:
                        updated_hours = st.number_input(
                            "Updated Running Hours", min_value=0.0,
                            value=float(chosen_equipment["running_hours"]),
                            step=1.0
                        )
                        updated_inspection = st.date_input(
                            "Updated Inspection Date",
                            value=datetime.fromisoformat(
                                chosen_equipment["last_inspection"]
                            ).date()
                        )
                    sensor_left, sensor_right = st.columns(2)
                    with sensor_left:
                        updated_temp = st.number_input("Updated Temperature (°C)", min_value=0.0, value=float(chosen_equipment["temperature_c"] if chosen_equipment["temperature_c"] is not None else 60.0), step=1.0)
                        updated_downtime = st.number_input("Updated Downtime Hours", min_value=0.0, value=float(chosen_equipment["downtime_hours"] or 0), step=1.0)
                    with sensor_right:
                        updated_vibration = st.number_input("Updated Vibration (mm/s)", min_value=0.0, value=float(chosen_equipment["vibration_mms"] if chosen_equipment["vibration_mms"] is not None else 3.0), step=0.5)
                    updated_notes = st.text_area(
                        "Updated Notes", value=chosen_equipment["notes"]
                    )
                    update_equipment = st.form_submit_button(
                        "💾 Save Equipment Update", use_container_width=True
                    )
                if update_equipment:
                    if updated_inspection > datetime.now().date():
                        st.error("Inspection date cannot be in the future.")
                    elif updated_hours < chosen_equipment["running_hours"]:
                        st.error("Running hours cannot be less than the previously recorded value.")
                    else:
                        with get_connection() as connection:
                            connection.execute("""
                                UPDATE mining_equipment
                                SET operational_status = ?, condition_rating = ?,
                                    running_hours = ?, downtime_hours = ?,
                                    temperature_c = ?, vibration_mms = ?, last_inspection = ?,
                                    notes = ?, updated_at = ?, updated_by = ?
                                WHERE id = ?
                            """, (
                                updated_status, updated_condition, updated_hours,
                                updated_downtime, updated_temp, updated_vibration,
                                updated_inspection.isoformat(), updated_notes.strip(),
                                datetime.now().isoformat(timespec="seconds"),
                                username, selected_equipment_id
                            ))
                        st.session_state["equipment_updated"] = (temperature_band(updated_temp), vibration_band(updated_vibration))
                        st.rerun()
        else:
            st.info("No equipment has been registered yet.")

        st.caption(
            "Demo only: alerts are indicative, not certified safety or "
            "maintenance decisions. Streamlit Cloud local SQLite records may "
            "be lost after restart or redeployment."
        )

    elif selected_page == "Maintenance":
        st.title("🔧 Maintenance Management")
        st.caption("Schedule servicing, assign technicians and track repairs and work orders.")

        outstanding = [o for o in maintenance_orders if o["status"] not in ("Completed", "Cancelled")]
        overdue = [o for o in outstanding if o["scheduled_date"] < datetime.now().date().isoformat()]
        urgent = [o for o in outstanding if o["priority"] in ("High", "Critical")]
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Work Orders", len(maintenance_orders))
        m2.metric("Outstanding", len(outstanding))
        m3.metric("Overdue", len(overdue))
        m4.metric("High / Critical Open", len(urgent))

        if overdue:
            st.warning(f"{len(overdue)} overdue maintenance work order(s). Review schedules promptly.")
        if urgent:
            st.error(f"{len(urgent)} high/critical priority work order(s) remain outstanding.")

        if role in MAINTENANCE_EDITORS:
            st.subheader("➕ Create Maintenance Work Order")
            if not equipment:
                st.info("Register equipment under Equipment Monitoring before creating a work order.")
            else:
                with st.form("create_maintenance_order", clear_on_submit=True):
                    left, right = st.columns(2)
                    with left:
                        selected_asset = st.selectbox(
                            "Equipment *", [e["id"] for e in equipment],
                            format_func=lambda equipment_id: next(
                                f'{e["equipment_code"]} — {e["equipment_name"]}'
                                for e in equipment if e["id"] == equipment_id
                            )
                        )
                        maintenance_type = st.selectbox("Maintenance Type", MAINTENANCE_TYPES)
                        maintenance_priority = st.selectbox("Priority", MAINTENANCE_PRIORITIES)
                    with right:
                        assigned_technician = st.text_input("Assigned Technician *")
                        scheduled_date = st.date_input("Scheduled Service Date")
                        initial_status = st.selectbox("Work Order Status", ["Open", "Scheduled"])
                    maintenance_description = st.text_area("Work Description *")
                    create_order = st.form_submit_button("💾 Create Work Order", use_container_width=True)

                if create_order:
                    if not assigned_technician.strip() or not maintenance_description.strip():
                        st.error("Assigned Technician and Work Description are required.")
                    else:
                        now = datetime.now().isoformat(timespec="seconds")
                        with get_connection() as connection:
                            connection.execute("""
                                INSERT INTO maintenance_orders (
                                    equipment_id, order_type, priority, description,
                                    assigned_technician, scheduled_date, status,
                                    completion_notes, created_at, created_by,
                                    updated_at, updated_by
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                selected_asset, maintenance_type, maintenance_priority,
                                maintenance_description.strip(), assigned_technician.strip(),
                                scheduled_date.isoformat(), initial_status, "", now,
                                username, now, username
                            ))
                        st.session_state["maintenance_created"] = True
                        st.rerun()
        else:
            st.info("Your role can view maintenance work orders but cannot create or update them.")

        if st.session_state.pop("maintenance_created", False):
            st.success("Maintenance work order created successfully.")
        if st.session_state.pop("maintenance_updated", False):
            st.success("Maintenance work order updated successfully.")

        st.subheader("📋 Maintenance Work Order Register")
        if maintenance_orders:
            search_order = st.text_input("Search Equipment, Technician or Description").strip().lower()
            left, right = st.columns(2)
            with left:
                status_filter = st.selectbox("Filter Work Order Status", ["All"] + MAINTENANCE_STATUSES)
            with right:
                priority_filter = st.selectbox("Filter Priority", ["All"] + MAINTENANCE_PRIORITIES)
            filtered_orders = [
                o for o in maintenance_orders
                if (not search_order or any(search_order in str(o[field]).lower()
                    for field in ("equipment_code", "equipment_name", "assigned_technician", "description")))
                and (status_filter == "All" or o["status"] == status_filter)
                and (priority_filter == "All" or o["priority"] == priority_filter)
            ]
            st.dataframe(filtered_orders, use_container_width=True, hide_index=True)
            buffer = io.StringIO()
            writer = csv.DictWriter(buffer, fieldnames=list(maintenance_orders[0].keys()))
            writer.writeheader()
            writer.writerows(filtered_orders)
            st.download_button("⬇️ Export Work Orders (CSV)", buffer.getvalue(),
                               file_name="khwezi_maintenance_orders.csv", mime="text/csv")

            if role in MAINTENANCE_EDITORS:
                st.subheader("🛠️ Update Work Order / Repair Progress")
                order_id = st.selectbox(
                    "Select Work Order", [o["id"] for o in maintenance_orders],
                    format_func=lambda order_id: next(
                        f'WO-{o["id"]:04d} — {o["equipment_code"]} ({o["status"]})'
                        for o in maintenance_orders if o["id"] == order_id
                    )
                )
                chosen = next(o for o in maintenance_orders if o["id"] == order_id)
                with st.form(f"update_maintenance_{order_id}"):
                    left, right = st.columns(2)
                    with left:
                        new_maintenance_status = st.selectbox(
                            "Update Status", MAINTENANCE_STATUSES,
                            index=MAINTENANCE_STATUSES.index(chosen["status"])
                        )
                        new_maintenance_priority = st.selectbox(
                            "Update Priority", MAINTENANCE_PRIORITIES,
                            index=MAINTENANCE_PRIORITIES.index(chosen["priority"])
                        )
                    with right:
                        new_technician = st.text_input(
                            "Assigned Technician", value=chosen["assigned_technician"]
                        )
                        new_schedule = st.date_input(
                            "Scheduled Service Date",
                            value=datetime.fromisoformat(chosen["scheduled_date"]).date()
                        )
                    new_completion_notes = st.text_area(
                        "Repair Notes / Work Performed", value=chosen["completion_notes"]
                    )
                    update_order = st.form_submit_button("💾 Save Work Order Update", use_container_width=True)
                if update_order:
                    if not new_technician.strip():
                        st.error("An assigned technician is required.")
                    elif new_maintenance_status == "Completed" and not new_completion_notes.strip():
                        st.error("Add work performed / completion notes before marking Completed.")
                    else:
                        with get_connection() as connection:
                            connection.execute("""
                                UPDATE maintenance_orders
                                SET status = ?, priority = ?, assigned_technician = ?,
                                    scheduled_date = ?, completion_notes = ?,
                                    updated_at = ?, updated_by = ?
                                WHERE id = ?
                            """, (
                                new_maintenance_status, new_maintenance_priority,
                                new_technician.strip(), new_schedule.isoformat(),
                                new_completion_notes.strip(),
                                datetime.now().isoformat(timespec="seconds"),
                                username, order_id
                            ))
                        st.session_state["maintenance_updated"] = True
                        st.rerun()
        else:
            st.info("No maintenance work orders have been created yet.")

        st.caption(
            "Demo only. Completing a work order does not automatically certify equipment "
            "as safe or return it to service. An authorised inspection and release process "
            "is still required. Local Streamlit Cloud database records may be lost."
        )

    elif selected_page == "Risk Assessment":
        st.title("⚠️ Mining Risk Assessment")
        st.caption("Identify hazards, assess likelihood and severity, and track control actions.")

        active_risks = [r for r in risk_assessments if r["status"] != "Closed"]
        serious_risks = [
            r for r in active_risks if r["risk_rating"] in ("High", "Critical")
        ]
        overdue_risks = [
            r for r in active_risks
            if r["target_date"] < datetime.now().date().isoformat()
        ]

        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Total Assessments", len(risk_assessments))
        r2.metric("Open Assessments", len(active_risks))
        r3.metric("High / Critical Open", len(serious_risks))
        r4.metric("Overdue Controls", len(overdue_risks))

        if serious_risks:
            st.error(
                f"{len(serious_risks)} high/critical assessment(s) remain open. "
                "Escalate through your site's safety procedures."
            )
        if overdue_risks:
            st.warning(f"{len(overdue_risks)} risk control action(s) are overdue.")

        with st.expander("📊 Illustrative 5 × 5 Risk Matrix"):
            st.write(
                "Risk Score = Likelihood × Severity. "
                "Low: 1–4 | Medium: 5–9 | High: 10–16 | Critical: 17–25."
            )
            st.caption(
                "These categories are examples, not an approved mine risk methodology. "
                "A site's competent risk team must establish its own criteria."
            )

        if role in RISK_EDITORS:
            st.subheader("➕ New Hazard and Risk Assessment")
            with st.form("create_risk_assessment", clear_on_submit=True):
                left, right = st.columns(2)
                with left:
                    risk_date = st.date_input("Assessment Date", key="risk_date")
                    risk_area = st.selectbox(
                        "Work Area",
                        ["Open Pit", "Underground", "Processing Plant",
                         "Workshop", "Haul Road", "Other"],
                        key="risk_area"
                    )
                    risk_activity = st.text_input(
                        "Task / Activity *", placeholder="e.g. Haul truck loading"
                    )
                    risk_hazard = st.text_area(
                        "Hazard Identified *",
                        placeholder="e.g. Interaction between pedestrians and mobile equipment"
                    )
                    risk_consequence = st.text_area(
                        "Potential Consequence *",
                        placeholder="e.g. Serious injury from vehicle collision"
                    )
                with right:
                    risk_likelihood = st.selectbox(
                        "Likelihood (1–5)", list(RISK_LIKELIHOOD), key="risk_likelihood"
                    )
                    risk_severity = st.selectbox(
                        "Severity (1–5)", list(RISK_SEVERITY), key="risk_severity"
                    )
                    risk_responsible = st.text_input("Responsible Person *")
                    risk_target = st.date_input(
                        "Control Action Target Date", key="risk_target"
                    )
                risk_existing = st.text_area("Existing Control Measures *")
                risk_additional = st.text_area("Additional Control Actions *")
                save_risk = st.form_submit_button(
                    "💾 Save Risk Assessment", use_container_width=True
                )

            if save_risk:
                required_fields = [
                    risk_activity, risk_hazard, risk_consequence,
                    risk_existing, risk_additional, risk_responsible
                ]
                if any(not field.strip() for field in required_fields):
                    st.error("Complete all fields marked * before saving.")
                elif risk_date > datetime.now().date():
                    st.error("Assessment Date cannot be in the future.")
                elif risk_target < risk_date:
                    st.error("Control target date cannot precede the assessment date.")
                else:
                    likelihood_value = RISK_LIKELIHOOD[risk_likelihood]
                    severity_value = RISK_SEVERITY[risk_severity]
                    score = likelihood_value * severity_value
                    rating = risk_band(score)
                    now = datetime.now().isoformat(timespec="seconds")
                    with get_connection() as connection:
                        connection.execute("""
                            INSERT INTO risk_assessments (
                                assessment_date, work_area, activity, hazard,
                                potential_consequence, likelihood, severity,
                                risk_score, risk_rating, existing_controls,
                                additional_controls, responsible_person,
                                target_date, status, review_notes, assessed_by,
                                created_at, updated_at, updated_by
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            risk_date.isoformat(), risk_area, risk_activity.strip(),
                            risk_hazard.strip(), risk_consequence.strip(),
                            likelihood_value, severity_value, score, rating,
                            risk_existing.strip(), risk_additional.strip(),
                            risk_responsible.strip(), risk_target.isoformat(),
                            "Open", "", username, now, now, username
                        ))
                    st.session_state["risk_saved_rating"] = rating
                    st.rerun()
        else:
            st.info("Your role can view risk assessments but cannot create or edit them.")

        saved_rating = st.session_state.pop("risk_saved_rating", None)
        if saved_rating in ("High", "Critical"):
            st.error(
                f"{saved_rating} risk assessment saved. "
                "Escalate immediately according to site procedures."
            )
        elif saved_rating:
            st.success(f"{saved_rating} risk assessment saved successfully.")

        if st.session_state.pop("risk_updated", False):
            st.success("Risk assessment updated successfully.")

        st.subheader("📋 Risk Assessment Register")
        if risk_assessments:
            risk_search = st.text_input(
                "Search Hazard, Activity, Work Area or Responsible Person"
            ).strip().lower()
            filter_col1, filter_col2 = st.columns(2)
            with filter_col1:
                rating_filter = st.selectbox(
                    "Filter Risk Rating", ["All", "Low", "Medium", "High", "Critical"]
                )
            with filter_col2:
                risk_status_filter = st.selectbox(
                    "Filter Assessment Status", ["All"] + RISK_STATUSES
                )

            filtered_risks = [
                r for r in risk_assessments
                if (
                    not risk_search or any(
                        risk_search in str(r[field]).lower()
                        for field in (
                            "hazard", "activity", "work_area", "responsible_person"
                        )
                    )
                )
                and (rating_filter == "All" or r["risk_rating"] == rating_filter)
                and (risk_status_filter == "All" or r["status"] == risk_status_filter)
            ]
            st.dataframe(filtered_risks, use_container_width=True, hide_index=True)

            risk_csv = io.StringIO()
            risk_writer = csv.DictWriter(
                risk_csv, fieldnames=list(risk_assessments[0].keys())
            )
            risk_writer.writeheader()
            risk_writer.writerows(filtered_risks)
            st.download_button(
                "⬇️ Export Risk Register (CSV)",
                risk_csv.getvalue(),
                file_name="khwezi_risk_register.csv",
                mime="text/csv"
            )

            if role in RISK_REVIEWERS:
                st.subheader("🔎 Review Risk and Control Progress")
                selected_risk_id = st.selectbox(
                    "Select Risk Assessment",
                    [r["id"] for r in risk_assessments],
                    format_func=lambda risk_id: next(
                        f'RA-{r["id"]:04d} — {r["activity"]} ({r["risk_rating"]})'
                        for r in risk_assessments if r["id"] == risk_id
                    )
                )
                chosen_risk = next(
                    r for r in risk_assessments if r["id"] == selected_risk_id
                )
                st.info(
                    f'Original Risk: {chosen_risk["risk_score"]}/25 '
                    f'({chosen_risk["risk_rating"]}). '
                    "Closing an action does not automatically reduce the risk score."
                )
                with st.form(f"review_risk_{selected_risk_id}"):
                    review_left, review_right = st.columns(2)
                    with review_left:
                        new_risk_status = st.selectbox(
                            "Control Action Status", RISK_STATUSES,
                            index=RISK_STATUSES.index(chosen_risk["status"])
                        )
                        new_responsible = st.text_input(
                            "Responsible Person",
                            value=chosen_risk["responsible_person"]
                        )
                    with review_right:
                        new_target_date = st.date_input(
                            "Control Action Target Date",
                            value=datetime.fromisoformat(
                                chosen_risk["target_date"]
                            ).date()
                        )
                    new_control_notes = st.text_area(
                        "Review Notes / Evidence of Controls",
                        value=chosen_risk["review_notes"]
                    )
                    update_risk = st.form_submit_button(
                        "💾 Save Risk Review", use_container_width=True
                    )

                if update_risk:
                    if not new_responsible.strip():
                        st.error("Responsible Person is required.")
                    elif new_risk_status == "Closed" and not new_control_notes.strip():
                        st.error(
                            "Add evidence / review notes before closing an assessment."
                        )
                    else:
                        with get_connection() as connection:
                            connection.execute("""
                                UPDATE risk_assessments
                                SET status = ?, responsible_person = ?,
                                    target_date = ?, review_notes = ?,
                                    updated_at = ?, updated_by = ?
                                WHERE id = ?
                            """, (
                                new_risk_status, new_responsible.strip(),
                                new_target_date.isoformat(),
                                new_control_notes.strip(),
                                datetime.now().isoformat(timespec="seconds"),
                                username, selected_risk_id
                            ))
                        st.session_state["risk_updated"] = True
                        st.rerun()
        else:
            st.info("No risk assessments have been recorded yet.")

        st.caption(
            "Demo only: risk scores and thresholds are illustrative. "
            "This tool does not replace a site-approved risk assessment, "
            "competent-person review or statutory mine safety procedures. "
            "Local SQLite data may be lost after redeployment."
        )

    elif selected_page == "Reports":
        st.title("📊 Reports and Analytics")
        st.caption("Operational overview and downloadable reports from recorded mine data.")

        # All figures below come from the application's existing SQLite tables.
        # Date filtering applies to event records; equipment is a current snapshot.
        today = datetime.now().date()
        period = st.selectbox(
            "Reporting Period",
            ["All Records", "Last 7 Days", "Last 30 Days", "Last 90 Days", "This Year"],
            key="reports_period",
        )

        def in_reporting_period(value):
            if period == "All Records":
                return True
            try:
                event_date = datetime.fromisoformat(str(value)[:10]).date()
            except (TypeError, ValueError):
                return False
            if period == "This Year":
                return event_date.year == today.year
            days = {"Last 7 Days": 7, "Last 30 Days": 30, "Last 90 Days": 90}[period]
            return 0 <= (today - event_date).days < days

        report_inspections = [r for r in inspections if in_reporting_period(r["inspection_time"])]
        report_incidents = [r for r in incidents if in_reporting_period(r["incident_date"])]
        report_orders = [r for r in maintenance_orders if in_reporting_period(r["created_at"])]
        report_risks = [r for r in risk_assessments if in_reporting_period(r["assessment_date"])]

        open_incidents = [i for i in report_incidents if i["status"] != "Closed"]
        serious_incidents = [i for i in report_incidents if i["severity"] in ("High", "Critical")]
        open_orders = [o for o in maintenance_orders if o["status"] not in ("Completed", "Cancelled")]
        open_risk_records = [r for r in risk_assessments if r["status"] != "Closed"]
        serious_open_risks = [r for r in open_risk_records if r["risk_rating"] in ("High", "Critical")]
        attention_equipment = [e for e in equipment if equipment_needs_attention(e)]

        st.subheader("📌 Key Performance Indicators")
        a, b, c, d = st.columns(4)
        a.metric("Worker Inspections", len(report_inspections))
        b.metric("Safety Incidents", len(report_incidents))
        c.metric("Equipment Registered", len(equipment))
        d.metric("Risk Assessments", len(report_risks))
        a, b, c, d = st.columns(4)
        a.metric("Open Incidents (Period)", len(open_incidents))
        b.metric("Equipment Needing Attention", len(attention_equipment))
        c.metric("Outstanding Work Orders", len(open_orders))
        d.metric("High / Critical Open Risks", len(serious_open_risks))

        if serious_open_risks:
            st.error(f"⚠️ {len(serious_open_risks)} high/critical risk assessment(s) remain open. Follow site escalation procedures.")
        if attention_equipment:
            st.warning(f"⚙️ {len(attention_equipment)} equipment item(s) need attention.")
        if serious_incidents:
            st.warning(f"🛡️ {len(serious_incidents)} high/critical incident(s) were reported in the selected period.")

        st.divider()
        st.subheader("📈 Operational Trends")
        left, right = st.columns(2)
        with left:
            st.markdown("**Incident Severity**")
            if report_incidents:
                severity_counts = pd.Series(
                    [r["severity"] for r in report_incidents]
                ).value_counts().reindex(["Low", "Medium", "High", "Critical"], fill_value=0)
                st.bar_chart(severity_counts.rename_axis("Severity"), color="#F5BD50")
            else:
                st.info("No incidents in the selected period.")

            st.markdown("**Worker Inspection Risk Levels**")
            if report_inspections:
                worker_counts = pd.Series(
                    [r["risk_level"] for r in report_inspections]
                ).value_counts().reindex(["Low", "Medium", "High"], fill_value=0)
                st.bar_chart(worker_counts.rename_axis("Risk Level"), color="#F5BD50")
            else:
                st.info("No worker inspections in the selected period.")

        with right:
            st.markdown("**Current Equipment Condition**")
            if equipment:
                condition_counts = pd.Series(
                    [e["condition_rating"] for e in equipment]
                ).value_counts().reindex(EQUIPMENT_CONDITIONS, fill_value=0)
                st.bar_chart(condition_counts.rename_axis("Condition"), color="#F5BD50")
            else:
                st.info("No equipment registered yet.")

            st.markdown("**Risk Assessment Ratings**")
            if report_risks:
                risk_counts = pd.Series(
                    [r["risk_rating"] for r in report_risks]
                ).value_counts().reindex(["Low", "Medium", "High", "Critical"], fill_value=0)
                st.bar_chart(risk_counts.rename_axis("Rating"), color="#F5BD50")
            else:
                st.info("No risk assessments in the selected period.")

        st.divider()
        st.subheader("📋 Registers and Data Export")
        report_datasets = {
            "Worker Safety": report_inspections,
            "Safety Incidents": report_incidents,
            "Equipment Monitoring": equipment,
            "Maintenance": report_orders,
            "Risk Assessment": report_risks,
        }
        selected_report = st.selectbox("Select Report", list(report_datasets), key="report_dataset")
        selected_records = report_datasets[selected_report]
        if selected_records:
            st.dataframe(pd.DataFrame(selected_records), use_container_width=True, hide_index=True)
        else:
            st.info("No records available for this report and period.")

        def make_csv(records):
            if not records:
                return ""
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=list(records[0].keys()))
            writer.writeheader()
            writer.writerows(records)
            return output.getvalue()

        st.download_button(
            "⬇️ Download Selected Report (CSV)",
            data=make_csv(selected_records),
            file_name="khwezi_" + selected_report.lower().replace(" ", "_") + ".csv",
            mime="text/csv",
            use_container_width=True,
            disabled=not selected_records,
        )

        archive_buffer = io.BytesIO()
        with zipfile.ZipFile(archive_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, records in report_datasets.items():
                if records:
                    archive.writestr(
                        "khwezi_" + name.lower().replace(" ", "_") + ".csv",
                        make_csv(records),
                    )
        st.download_button(
            "📦 Download All Reports (ZIP)",
            data=archive_buffer.getvalue(),
            file_name="khwezi_mining_reports.zip",
            mime="application/zip",
            use_container_width=True,
        )
        st.caption(
            "Reporting period filters dated activity records. Equipment and outstanding-action "
            "KPIs reflect current status across all dates. This demonstration uses local SQLite "
            "storage, which may be lost when Streamlit Community Cloud restarts or redeploys. "
            "Reports are not a substitute for approved statutory safety reporting."
        )

    elif selected_page == "Manage Users":
        st.title("👥 User Management")
        st.caption("Administrator-only account management and role permissions.")

        if role != "Administrator":
            st.error("Access denied. Administrator permissions required.")
            st.stop()

        managed = get_managed_users()
        legacy_names = secret_usernames()
        c1, c2, c3 = st.columns(3)
        c1.metric("Managed Accounts", len(managed))
        c2.metric("Active Managed Accounts", sum(u["active"] for u in managed))
        c3.metric("Secrets Accounts", len(legacy_names))

        st.info(
            "Existing Secrets accounts remain available for login but cannot be "
            "edited here. New accounts are stored in the local demonstration database."
        )

        st.subheader("➕ Create User Account")
        with st.form("create_managed_user", clear_on_submit=True):
            left, right = st.columns(2)
            with left:
                new_username = st.text_input("New Username *")
                new_role = st.selectbox("Account Role", list(ROLE_PAGES))
            with right:
                new_password = st.text_input("Password *", type="password")
                confirm_password = st.text_input("Confirm Password *", type="password")
            create_user = st.form_submit_button("💾 Create Account", use_container_width=True)

        if create_user:
            clean_name = new_username.strip().lower()
            if not clean_name or not clean_name.replace("_", "").isalnum():
                st.error("Use a username containing only letters, numbers or underscores.")
            elif clean_name in [name.lower() for name in legacy_names]:
                st.error("This username is already configured in Streamlit Secrets.")
            elif len(new_password) < 12:
                st.error("Password must be at least 12 characters long.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                salt, digest = hash_password(new_password)
                now = datetime.now().isoformat(timespec="seconds")
                try:
                    with get_connection() as connection:
                        connection.execute("""
                            INSERT INTO managed_users (
                                username, password_salt, password_hash, role,
                                active, created_at, updated_at
                            ) VALUES (?, ?, ?, ?, 1, ?, ?)
                        """, (clean_name, salt, digest, new_role, now, now))
                    st.session_state["user_notice"] = "Account created successfully."
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("That username already exists.")

        if st.session_state.pop("user_notice", None):
            st.success("User account changes saved successfully.")

        st.subheader("📋 User Accounts")
        if legacy_names:
            st.write("**Accounts managed through Streamlit Secrets**")
            st.dataframe(
                [{"Username": name, "Role": st.secrets["users"][name]["role"],
                  "Source": "Streamlit Secrets"} for name in legacy_names],
                use_container_width=True, hide_index=True
            )
        if managed:
            st.write("**Locally managed accounts**")
            st.dataframe(
                [{"Username": u["username"], "Role": u["role"],
                  "Status": "Active" if u["active"] else "Disabled",
                  "Created": u["created_at"]} for u in managed],
                use_container_width=True, hide_index=True
            )

            st.subheader("🔧 Edit Managed User")
            selected_username = st.selectbox(
                "Select Account", [u["username"] for u in managed]
            )
            chosen = next(u for u in managed if u["username"] == selected_username)
            with st.form("edit_managed_user"):
                edit_role = st.selectbox(
                    "Role", list(ROLE_PAGES),
                    index=list(ROLE_PAGES).index(chosen["role"])
                )
                edit_active = st.checkbox("Account Enabled", value=bool(chosen["active"]))
                reset_password = st.text_input(
                    "New Password (leave blank to keep existing)", type="password"
                )
                save_edit = st.form_submit_button(
                    "💾 Save User Changes", use_container_width=True
                )
            if save_edit:
                if reset_password and len(reset_password) < 12:
                    st.error("New password must be at least 12 characters long.")
                elif selected_username == username and (
                    not edit_active or edit_role != "Administrator"
                ):
                    st.error("You cannot disable or remove your own Administrator access.")
                else:
                    now = datetime.now().isoformat(timespec="seconds")
                    with get_connection() as connection:
                        if reset_password:
                            salt, digest = hash_password(reset_password)
                            connection.execute("""
                                UPDATE managed_users
                                SET role = ?, active = ?, password_salt = ?,
                                    password_hash = ?, updated_at = ?
                                WHERE username = ?
                            """, (edit_role, int(edit_active), salt, digest,
                                  now, selected_username))
                        else:
                            connection.execute("""
                                UPDATE managed_users
                                SET role = ?, active = ?, updated_at = ?
                                WHERE username = ?
                            """, (edit_role, int(edit_active), now, selected_username))
                    st.session_state["user_notice"] = "Updated"
                    st.rerun()
        else:
            st.info("No locally managed accounts yet. Create one above.")

        st.subheader("🔐 Role Permissions")
        st.dataframe(
            [{"Role": r, "Accessible Pages": ", ".join(pages)}
             for r, pages in ROLE_PAGES.items()],
            use_container_width=True, hide_index=True
        )
        st.warning(
            "Demo only: Streamlit Community Cloud's local SQLite storage may be "
            "lost after restart or redeployment, including new accounts. "
            "Do not use demo credentials or store real employee information. "
            "For production, use durable storage and a managed identity provider."
        )

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
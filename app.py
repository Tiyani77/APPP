
import streamlit as st
import base64
import textwrap
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
# 2. BACKGROUND IMAGE
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
# 3. CUSTOM DESIGN AND COLOURS
# ==========================================

st.markdown(f"""
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

h1, h2, h3, p {{
    color: white;
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

/* MAIN HERO */

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

/* LOGIN FORM */

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

/* FOOTER */

.footer {{
    text-align: center;
    color: #B9C4D2;
    font-size: 12px;
    margin-top: 35px;
    padding-bottom: 10px;
}}

/* MOBILE */

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
""", unsafe_allow_html=True)


# ==========================================
# 4. HELPER FOR HTML
# ==========================================

def show_html(html):
    st.markdown(
        textwrap.dedent(html).strip(),
        unsafe_allow_html=True
    )


# ==========================================
# 5. HEADER
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
    st.success("● System Online")


# ==========================================
# 6. HERO SECTION AND LOGIN
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
                st.info(
                    "Login authentication will be added next."
                )


# ==========================================
# 7. APPLICATION FEATURES
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
# 8. FOOTER
# ==========================================

show_html("""
<div class="footer">
    © 2026 Khwezi Mining |
    Health, Safety & Equipment Monitoring System
</div>
""")

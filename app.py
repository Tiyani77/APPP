
import streamlit as st
import base64
from pathlib import Path

st.set_page_config(
    page_title="Khwezi Mining | Monitoring System",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load background image
image_path = Path(__file__).parent / "mining_bg.png"

background_css = ""

if image_path.exists():
    encoded = base64.b64encode(
        image_path.read_bytes()
    ).decode()

    background_css = f"""
    background-image:
        linear-gradient(
            90deg,
            rgba(8, 19, 35, 0.94),
            rgba(8, 19, 35, 0.55)
        ),
        url("data:image/png;base64,{encoded}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    """

st.markdown(f"""
<style>
    .stApp {{
        background-color: #0B1728;
        {background_css}
        color: #FFFFFF;
    }}

    header[data-testid="stHeader"] {{
        background: transparent;
    }}

    .block-container {{
        padding-top: 2rem;
        max-width: 1300px;
    }}

    h1, h2, h3, p {{
        color: #FFFFFF !important;
    }}

    .brand {{
        color: #F5BD50;
        font-size: 20px;
        font-weight: 800;
        letter-spacing: 3px;
        margin-bottom: 55px;
    }}

    .hero-title {{
        font-size: clamp(44px, 5vw, 72px);
        font-weight: 800;
        line-height: 1.15;
        margin-bottom: 18px;
    }}

    .gold {{
        color: #F5BD50;
    }}

    .subtitle {{
        font-size: 24px;
        font-weight: 600;
        margin-bottom: 25px;
    }}

    .description {{
        font-size: 18px;
        color: #D3DCE8 !important;
        line-height: 1.8;
        max-width: 550px;
    }}

    .login-heading {{
        text-align: center;
        color: #F5BD50;
        font-size: 27px;
        font-weight: 700;
        margin-bottom: 10px;
    }}

    div[data-testid="stForm"] {{
        background: rgba(15, 27, 45, 0.85);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 18px;
        padding: 28px;
    }}

    .stButton button,
    div[data-testid="stFormSubmitButton"] button {{
        background-color: #F5BD50;
        color: #101827;
        font-weight: 800;
        border: none;
        border-radius: 9px;
        width: 100%;
        padding: 12px;
    }}

    .stButton button:hover,
    div[data-testid="stFormSubmitButton"] button:hover {{
        background-color: #FFD47B;
        color: #101827;
    }}

    .feature-card {{
        background: rgba(10, 23, 40, 0.88);
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 15px;
        padding: 22px 12px;
        text-align: center;
        min-height: 170px;
    }}

    .feature-icon {{
        font-size: 32px;
        margin-bottom: 12px;
    }}

    .feature-title {{
        font-weight: 700;
        font-size: 16px;
        color: white;
        margin-bottom: 8px;
    }}

    .feature-text {{
        font-size: 13px;
        color: #CBD5E1 !important;
    }}
</style>
""", unsafe_allow_html=True)


# Header
st.markdown("""
<div class="brand">
    ⛏️ KHWEZI MINING
    <span style="font-size:12px;color:#D3DCE8;">
        &nbsp; | SAFE PEOPLE • RELIABLE EQUIPMENT
    </span>
</div>
""", unsafe_allow_html=True)


# Hero and login area
left, right = st.columns([1.3, 1], gap="large")

with left:
    st.markdown("""
    <div style="padding-top:45px;">
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
    """, unsafe_allow_html=True)

with right:
    with st.form("login_form"):
        st.markdown("""
        <div class="login-heading">
            🔐 User Login
        </div>
        <p style="text-align:center;color:#CBD5E1;">
            Access your account to continue
        </p>
        """, unsafe_allow_html=True)

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
            st.info(
                "Login functionality will be added next."
            )


st.write("")
st.write("")
st.write("")

# Feature cards
features = [
    ("👷", "Worker Safety", "Monitor worker safety information"),
    ("🛡️", "Incident Tracking", "Record and analyse incidents"),
    ("⚙️", "Equipment Monitoring", "Track equipment conditions"),
    ("🔧", "Maintenance", "Manage equipment maintenance"),
    ("📊", "Data Analysis", "Visualise data and reports")
]

columns = st.columns(5, gap="small")

for col, (icon, title, description) in zip(columns, features):
    with col:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feature-icon">{icon}</div>
            <div class="feature-title">{title}</div>
            <p class="feature-text">{description}</p>
        </div>
        """, unsafe_allow_html=True)


st.markdown("""
<p style="
    text-align:center;
    color:#94A3B8 !important;
    font-size:12px;
    margin-top:45px;
">
    © 2026 Khwezi Mining | Health, Safety &
    Equipment Monitoring System
</p>
""", unsafe_allow_html=True)

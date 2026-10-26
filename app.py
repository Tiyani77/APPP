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
# 6. AUTHENTICATED DASHBOARD & ROLE PERMISSIONS
# ==========================================

ROLE_PERMISSIONS = {
    "Administrator": [
        "Dashboard", "Worker Safety", "Safety Incidents",
        "Equipment Monitoring", "Maintenance", "Risk Assessment",
        "Reports", "Manage Users"
    ],
    "Safety Officer": [
        "Dashboard", "Worker Safety", "Safety Incidents",
        "Risk Assessment", "Reports"
    ],
    "Mining Engineer": [
        "Dashboard", "Worker Safety", "Safety Incidents",

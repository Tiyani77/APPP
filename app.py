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

import streamlit as st
import hashlib
import json
import os

USERS_FILE = "users.json"
PROFILES_FILE = "profiles.json"


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def load_users() -> dict:
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {
        "admin": hash_password("admin123"),
        "patient1": hash_password("diet@123"),
    }


def save_users(users: dict):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def load_profiles() -> dict:
    if os.path.exists(PROFILES_FILE):
        with open(PROFILES_FILE, "r") as f:
            return json.load(f)
    return {}


def save_profile(username: str, profile: dict):
    profiles = load_profiles()
    profiles[username] = profile
    with open(PROFILES_FILE, "w") as f:
        json.dump(profiles, f, indent=2)


def get_profile(username: str) -> dict:
    profiles = load_profiles()
    return profiles.get(username, {})


def login_page():
    st.markdown("""
    <style>
    .auth-title { font-size: 2rem; font-weight: 700; color: #1a6b3c; text-align: center; }
    .auth-subtitle { color: #555; text-align: center; margin-bottom: 1.5rem; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="auth-title">🥗 NutriSouth AI</div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-subtitle">South Indian Diabetic Diet Advisor</div>', unsafe_allow_html=True)
        st.divider()

        tab_login, tab_register = st.tabs(["🔑 Login", "📝 Register"])

        with tab_login:
            username = st.text_input("Username", key="login_user", placeholder="Enter username")
            password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter password")

            if st.button("Login", use_container_width=True, type="primary", key="login_btn"):
                users = load_users()
                if username in users and users[username] == hash_password(password):
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = username
                    profile = get_profile(username)
                    if profile:
                        for k, v in profile.items():
                            st.session_state[k] = v
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

            st.markdown("---")
            st.caption("Demo: `admin` / `admin123`")

        with tab_register:
            new_user    = st.text_input("Choose Username", key="reg_user", placeholder="e.g. john_doe")
            new_pass    = st.text_input("Choose Password", type="password", key="reg_pass", placeholder="Min 6 characters")
            confirm_pass= st.text_input("Confirm Password", type="password", key="reg_confirm")

            if st.button("Register", use_container_width=True, type="primary", key="reg_btn"):
                users = load_users()
                if not new_user or not new_pass:
                    st.error("Username and password cannot be empty.")
                elif len(new_pass) < 6:
                    st.error("Password must be at least 6 characters.")
                elif new_pass != confirm_pass:
                    st.error("Passwords do not match.")
                elif new_user in users:
                    st.error("Username already exists.")
                else:
                    users[new_user] = hash_password(new_pass)
                    save_users(users)
                    st.success(f"Account created for **{new_user}**! You can now log in.")


def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


def require_login():
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        login_page()
        st.stop()
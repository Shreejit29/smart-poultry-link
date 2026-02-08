import streamlit as st
import requests

BACKEND_URL = "https://smart-poultry-link.onrender.com"


def login_ui():
    st.subheader("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            response = requests.post(
                f"{BACKEND_URL}/login",
                params={"username": username, "password": password},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                st.session_state["token"] = data["access_token"]
                st.session_state["role"] = data["role"]
                st.session_state["trust"] = data["trust"]
                st.success("Login successful")
            else:
                st.error("Invalid credentials")

        except Exception as e:
            st.error("Backend not reachable")

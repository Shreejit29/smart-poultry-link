import streamlit as st
from login import login_ui
from consumer import consumer_ui
from admin import admin_ui

st.set_page_config(page_title="Smart Poultry Link", layout="centered")

st.title("🐔 Smart Poultry Link")

if "token" not in st.session_state:
    login_ui()
else:
    st.success("Logged in")

    role = st.session_state.get("role")

    if role == "consumer":
        consumer_ui()
    elif role == "admin":
        admin_ui()
    else:
        st.warning("Unknown role")

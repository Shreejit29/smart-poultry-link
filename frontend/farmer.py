import streamlit as st
import requests

BACKEND_URL = "https://smart-poultry-link.onrender.com"


def farmer_ui():
    st.subheader("🚜 Farmer Dashboard")

    # For MVP: user_id is fixed / known
    # Later this will come from JWT
    user_id = st.number_input(
        "Your User ID",
        min_value=1,
        step=1
    )

    if st.button("Load Dashboard"):
        try:
            response = requests.get(
                f"{BACKEND_URL}/farmer/dashboard",
                params={"user_id": user_id},
                timeout=10
            )

            if response.status_code != 200:
                st.error("Farmer profile not found")
                return

            data = response.json()

            # Status
            if data["is_active"]:
                st.success("🟢 Status: Active")
            else:
                st.warning("🔴 Status: Offline")

            st.divider()

            # Capacity
            col1, col2 = st.columns(2)
            col1.metric("Total Capacity (kg)", data["capacity_kg"])
            col2.metric("Available (kg)", data["available_kg"])

            st.divider()

            # Performance metrics
            col3, col4, col5 = st.columns(3)
            col3.metric("Trust Score", round(data["trust"], 2))
            col4.metric("Acceptance Rate", round(data["acceptance_rate"], 2))
            col5.metric("SLA Score", round(data["sla_score"], 2))

        except Exception:
            st.error("Backend not reachable")

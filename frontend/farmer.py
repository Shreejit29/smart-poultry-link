import streamlit as st
import requests

BACKEND_URL = "https://smart-poultry-link.onrender.com"


def farmer_ui():
    st.subheader("🚜 Farmer Dashboard")

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

            # Availability toggle
            current_status = data["is_active"]
            status_label = "Online" if current_status else "Offline"

            st.subheader(f"Status: {status_label}")

            new_status = st.toggle(
                "Go Online / Offline",
                value=current_status
            )

            if new_status != current_status:
                toggle_res = requests.post(
                    f"{BACKEND_URL}/farmer/availability",
                    params={
                        "user_id": user_id,
                        "is_active": 1 if new_status else 0
                    },
                    timeout=10
                )

                if toggle_res.status_code == 200:
                    st.success("Availability updated")
                else:
                    st.error("Failed to update availability")

            st.divider()

            # Capacity metrics
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

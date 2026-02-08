import streamlit as st
import requests
import pandas as pd

BACKEND_URL = "https://smart-poultry-link.onrender.com"


def admin_ui():
    st.subheader("🛠️ Admin Dashboard")

    tab1, tab2, tab3 = st.tabs(["👤 Users", "🚜 Farmers", "🧾 Orders"])

    # ---------------- USERS ----------------
    with tab1:
        st.markdown("### Users")
        res = requests.get(f"{BACKEND_URL}/admin/users")
        df = pd.DataFrame(res.json())
        st.dataframe(df, use_container_width=True)

        st.divider()
        st.markdown("#### Modify User")
        user_id = st.number_input("User ID", min_value=1, step=1)
        trust = st.slider("Trust", 0.0, 1.0, 0.5)
        block = st.toggle("Block user")

        if st.button("Update User"):
            requests.post(
                f"{BACKEND_URL}/admin/user/trust",
                params={"user_id": user_id, "trust": trust}
            )
            requests.post(
                f"{BACKEND_URL}/admin/user/block",
                params={"user_id": user_id, "is_blocked": int(block)}
            )
            st.success("User updated")

    # ---------------- FARMERS ----------------
    with tab2:
        st.markdown("### Farmers")
        res = requests.get(f"{BACKEND_URL}/admin/farmers")
        df = pd.DataFrame(res.json())
        st.dataframe(df, use_container_width=True)

        st.divider()
        st.markdown("#### Modify Farmer")
        farmer_id = st.number_input("Farmer ID", min_value=1, step=1)
        trust = st.slider("Farmer Trust", 0.0, 1.0, 0.5)
        block = st.toggle("Block farmer")

        if st.button("Update Farmer"):
            requests.post(
                f"{BACKEND_URL}/admin/farmer/trust",
                params={"farmer_id": farmer_id, "trust": trust}
            )
            requests.post(
                f"{BACKEND_URL}/admin/farmer/block",
                params={"farmer_id": farmer_id, "is_blocked": int(block)}
            )
            st.success("Farmer updated")

    # ---------------- ORDERS ----------------
    with tab3:
        st.markdown("### Orders")
        res = requests.get(f"{BACKEND_URL}/admin/orders")
        df = pd.DataFrame(res.json())
        st.dataframe(df, use_container_width=True)

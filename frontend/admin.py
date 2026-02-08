import streamlit as st
import requests
import pandas as pd

BACKEND_URL = "https://smart-poultry-link.onrender.com"


def admin_ui():
    st.subheader("🛠️ Admin Dashboard")

    tab1, tab2, tab3 = st.tabs(["👤 Users", "🚜 Farmers", "🧾 Orders"])

    # ---------------- USERS ----------------
    with tab1:
        st.markdown("### Registered Users")
        try:
            res = requests.get(f"{BACKEND_URL}/admin/users", timeout=10)
            if res.status_code == 200:
                df = pd.DataFrame(res.json())
                st.dataframe(df, use_container_width=True)
            else:
                st.error("Failed to load users")
        except Exception:
            st.error("Backend not reachable")

    # ---------------- FARMERS ----------------
    with tab2:
        st.markdown("### Registered Farmers")
        try:
            res = requests.get(f"{BACKEND_URL}/admin/farmers", timeout=10)
            if res.status_code == 200:
                df = pd.DataFrame(res.json())
                st.dataframe(df, use_container_width=True)
            else:
                st.error("Failed to load farmers")
        except Exception:
            st.error("Backend not reachable")

    # ---------------- ORDERS ----------------
    with tab3:
        st.markdown("### Orders Overview")
        try:
            res = requests.get(f"{BACKEND_URL}/admin/orders", timeout=10)
            if res.status_code == 200:
                df = pd.DataFrame(res.json())
                st.dataframe(df, use_container_width=True)
            else:
                st.error("Failed to load orders")
        except Exception:
            st.error("Backend not reachable")

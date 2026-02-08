import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

BACKEND_URL = "https://smart-poultry-link.onrender.com"


def admin_ui():
    st.subheader("🛠️ Admin Dashboard")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📊 Analytics", "👤 Users", "🚜 Farmers", "🧾 Orders"]
    )

    # ---------------- ANALYTICS ----------------
    with tab1:
        st.markdown("### 📊 Platform KPIs")

        res = requests.get(f"{BACKEND_URL}/admin/analytics")
        data = res.json()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Users", data["total_users"])
        col2.metric("Total Farmers", data["total_farmers"])
        col3.metric("Active Farmers", data["active_farmers"])

        col4, col5, col6 = st.columns(3)
        col4.metric("Total Orders", data["total_orders"])
        col5.metric("Successful Orders", data["successful_orders"])
        col6.metric("Failed Orders", data["failed_orders"])

        st.divider()

        # Trust charts
        fig, ax = plt.subplots()
        ax.bar(
            ["Consumers", "Farmers"],
            [data["avg_user_trust"], data["avg_farmer_trust"]]
        )
        ax.set_ylim(0, 1)
        ax.set_ylabel("Average Trust")
        ax.set_title("Average Trust Levels")
        st.pyplot(fig)

    # ---------------- USERS ----------------
    with tab2:
        st.markdown("### Users")
        df = pd.DataFrame(
            requests.get(f"{BACKEND_URL}/admin/users").json()
        )
        st.dataframe(df, use_container_width=True)

    # ---------------- FARMERS ----------------
    with tab3:
        st.markdown("### Farmers")
        df = pd.DataFrame(
            requests.get(f"{BACKEND_URL}/admin/farmers").json()
        )
        st.dataframe(df, use_container_width=True)

    # ---------------- ORDERS ----------------
    with tab4:
        st.markdown("### Orders")
        df = pd.DataFrame(
            requests.get(f"{BACKEND_URL}/admin/orders").json()
        )
        st.dataframe(df, use_container_width=True)

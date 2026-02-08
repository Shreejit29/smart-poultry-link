import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

BACKEND_URL = "https://smart-poultry-link.onrender.com"


def admin_ui():
    st.title("🛠️ Admin Control Center")

    tabs = st.tabs(["📊 Analytics", "👤 Users", "🚜 Farmers", "🧾 Orders"])

    # ================= ANALYTICS =================
    with tabs[0]:
        data = requests.get(f"{BACKEND_URL}/admin/analytics").json()

        col1, col2, col3 = st.columns(3)
        col1.metric("Users", data["total_users"])
        col2.metric("Farmers", data["total_farmers"])
        col3.metric("Active Farmers", data["active_farmers"])

        col4, col5, col6 = st.columns(3)
        col4.metric("Orders", data["total_orders"])
        col5.metric("Success", data["successful_orders"])
        col6.metric("Failed", data["failed_orders"])

        fig, ax = plt.subplots()
        ax.bar(["Consumers", "Farmers"],
               [data["avg_user_trust"], data["avg_farmer_trust"]])
        ax.set_ylim(0, 1)
        ax.set_ylabel("Avg Trust")
        st.pyplot(fig)

    # ================= USERS =================
    with tabs[1]:
        users = pd.DataFrame(
            requests.get(f"{BACKEND_URL}/admin/users").json()
        )
        st.dataframe(users, use_container_width=True)

        st.subheader("Modify User")
        uid = st.number_input("User ID", min_value=1, step=1)
        trust = st.slider("Trust", 0.0, 1.0, 0.5)
        block = st.toggle("Block User")

        if st.button("Update User"):
            requests.post(f"{BACKEND_URL}/admin/user/trust",
                          params={"user_id": uid, "trust": trust})
            requests.post(f"{BACKEND_URL}/admin/user/block",
                          params={"user_id": uid, "is_blocked": int(block)})
            st.success("User updated")

    # ================= FARMERS =================
    with tabs[2]:
        farmers = pd.DataFrame(
            requests.get(f"{BACKEND_URL}/admin/farmers").json()
        )
        st.dataframe(farmers, use_container_width=True)

        st.subheader("Modify Farmer")
        fid = st.number_input("Farmer ID", min_value=1, step=1)
        trust = st.slider("Farmer Trust", 0.0, 1.0, 0.5)
        block = st.toggle("Block Farmer")

        if st.button("Update Farmer"):
            requests.post(f"{BACKEND_URL}/admin/farmer/trust",
                          params={"farmer_id": fid, "trust": trust})
            requests.post(f"{BACKEND_URL}/admin/farmer/block",
                          params={"farmer_id": fid, "is_blocked": int(block)})
            st.success("Farmer updated")

    # ================= ORDERS =================
    with tabs[3]:
        orders = pd.DataFrame(
            requests.get(f"{BACKEND_URL}/admin/orders").json()
        )
        st.dataframe(orders, use_container_width=True)

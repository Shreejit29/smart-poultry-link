import streamlit as st
import requests

BACKEND_URL = "https://smart-poultry-link.onrender.com"


def farmer_ui():
    st.subheader("🚜 Farmer Dashboard")

    farmer_id = st.number_input(
        "Your Farmer ID",
        min_value=1,
        step=1
    )

    if st.button("Load Dashboard"):
        try:
            # Fetch dashboard metrics
            dash = requests.get(
                f"{BACKEND_URL}/farmer/dashboard",
                params={"user_id": farmer_id},
                timeout=10
            )

            if dash.status_code != 200:
                st.error("Farmer profile not found")
                return

            data = dash.json()

            # Status
            st.success("🟢 Online" if data["is_active"] else "🔴 Offline")

            col1, col2 = st.columns(2)
            col1.metric("Capacity (kg)", data["capacity_kg"])
            col2.metric("Available (kg)", data["available_kg"])

            col3, col4, col5 = st.columns(3)
            col3.metric("Trust", round(data["trust"], 2))
            col4.metric("Acceptance Rate", round(data["acceptance_rate"], 2))
            col5.metric("SLA Score", round(data["sla_score"], 2))

            st.divider()

            # 🔔 ORDER INBOX
            st.subheader("📥 Incoming Orders")

            inbox = requests.get(
                f"{BACKEND_URL}/farmer/orders",
                params={"farmer_id": farmer_id},
                timeout=10
            )

            orders = inbox.json()

            if not orders:
                st.info("No new orders assigned")
                return

            for o in orders:
                st.markdown(f"### 🧾 Order #{o['order_id']}")
                st.write(f"Quantity: {o['qty']} kg")

                colA, colB = st.columns(2)

                if colA.button("✅ Accept", key=f"accept_{o['order_id']}"):
                    requests.post(
                        f"{BACKEND_URL}/farmer/order/decision",
                        params={
                            "farmer_id": farmer_id,
                            "order_id": o["order_id"],
                            "decision": "ACCEPT"
                        }
                    )
                    st.success("Order accepted")

                if colB.button("❌ Reject", key=f"reject_{o['order_id']}"):
                    requests.post(
                        f"{BACKEND_URL}/farmer/order/decision",
                        params={
                            "farmer_id": farmer_id,
                            "order_id": o["order_id"],
                            "decision": "REJECT"
                        }
                    )
                    st.warning("Order rejected")

        except Exception:
            st.error("Backend not reachable")

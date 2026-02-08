import streamlit as st
import requests
from charts import trust_chart

BACKEND_URL = "https://smart-poultry-link.onrender.com"


def consumer_ui():
    st.subheader("🛒 Place Order")

    qty = st.slider("Select quantity (kg)", min_value=1, max_value=20, value=5)
    amount = qty * 200

    st.info(f"💰 Amount (dummy): ₹{amount}")

    if "trust" not in st.session_state:
        st.session_state["trust"] = 0.5

    if st.button("Pay & Place Order"):
        try:
            response = requests.post(
                f"{BACKEND_URL}/order",
                params={"qty": qty, "user_id": 1},
                timeout=10
            )

            data = response.json()

            st.session_state["trust"] = data["updated_trust"]

            if data["payment_status"] == "SUCCESS":
                st.success("✅ Payment Successful")
            else:
                st.error("❌ Payment Failed")

            st.write("🧾 Order Status:", data["order_status"])
            st.write("🔑 Transaction ID:", data["transaction_id"])

        except Exception:
            st.error("Backend not reachable")

    st.divider()
    st.subheader("📈 Your Trust Score")
    st.pyplot(trust_chart(st.session_state["trust"]))

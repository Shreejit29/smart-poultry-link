import streamlit as st
import requests

BACKEND_URL = "https://smart-poultry-link.onrender.com"


def consumer_ui():
    st.subheader("🛒 Place Order")

    qty = st.slider("Select quantity (kg)", min_value=1, max_value=20, value=5)
    amount = qty * 200

    st.info(f"💰 Amount (dummy): ₹{amount}")

    if st.button("Pay & Place Order"):
        try:
            response = requests.post(
                f"{BACKEND_URL}/order",
                params={
                    "qty": qty,
                    "user_id": 1  # MVP simplification
                },
                timeout=10
            )

            data = response.json()

            if data["payment_status"] == "SUCCESS":
                st.success("✅ Payment Successful")
                st.write("🧾 Order Status:", data["order_status"])
                st.write("🔑 Transaction ID:", data["transaction_id"])
            else:
                st.error("❌ Payment Failed. Please try again.")

        except Exception:
            st.error("Backend not reachable")

import streamlit as st
import pandas as pd
import numpy as np

# IMPORT MODULES
import auth
import payment
import model
import admin

# -----------------------
# INIT DATABASE
# -----------------------
auth.create_users_table()
payment.create_contribution_table()

# -----------------------
# AUTH UI
# -----------------------
menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Register":
    st.subheader("Create Account")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Register"):
        if auth.register_user(u, p):
            st.success("Registered successfully")
        else:
            st.error("User already exists")

elif choice == "Login":
    st.subheader("Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if auth.login_user(u, p):
            st.session_state["user"] = u
            st.success("Logged in")
        else:
            st.error("Invalid credentials")

# -----------------------
# MAIN APP
# -----------------------
if "user" in st.session_state:

    st.title("📊 Equb Smart Dashboard")

    user = st.session_state["user"]

    # -----------------------
    # PAYMENT
    # -----------------------
    st.subheader("💳 Contribution")

    amount = st.number_input("Enter Amount", min_value=0.0)

    if st.button("Pay"):
        payment.save_payment(user, amount)
        st.success("Payment successful")

    # -----------------------
    # LOAD DATA
    # -----------------------
    df = pd.DataFrame(payment.get_all_payments(),
                      columns=["User", "Amount", "Status", "Time"])

    st.subheader("📋 Contributions")
    st.dataframe(df)

    # -----------------------
    # MODEL ENGINE
    # -----------------------
    if not df.empty:
        members = df["User"].unique()
        weights = model.compute_weights(len(members))
        probs = model.compute_probabilities(weights)

        total = df["Amount"].sum()

        st.subheader("📈 Probabilities")
        prob_df = pd.DataFrame({"Member": members, "Probability": probs})
        st.dataframe(prob_df)
        st.bar_chart(prob_df.set_index("Member"))

        st.subheader("💰 Expected Rewards")
        exp = model.expected_rewards(probs, total)
        st.write(dict(zip(members, exp)))

        st.subheader("⚖️ Fairness")
        st.write(model.fairness_metric(probs))

        if st.button("🎲 Run Draw"):
            winner = model.run_draw(members, probs)
            st.success(f"Winner: {winner}")

    # -----------------------
    # ADMIN PANEL
    # -----------------------
    role = auth.get_user_role(user)

    if role == "admin":
        admin.admin_panel()

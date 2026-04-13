import streamlit as st
import pandas as pd
import numpy as np
import sqlite3

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
# SESSION INIT
# -----------------------
if "user" not in st.session_state:
    st.session_state["user"] = None

# -----------------------
# SIDEBAR MENU
# -----------------------
menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

# -----------------------
# REGISTER
# -----------------------
if choice == "Register":
    st.subheader("📝 Create Account")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        if username and password:
            success = auth.register_user(username, password)
            if success:
                st.success("✅ Account created successfully")
            else:
                st.error("❌ Username already exists")
        else:
            st.warning("⚠️ Fill all fields")

# -----------------------
# LOGIN
# -----------------------
elif choice == "Login":
    st.subheader("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if auth.login_user(username, password):
            st.session_state["user"] = username
            st.success(f"Welcome {username}")
        else:
            st.error("Invalid credentials")

# -----------------------
# MAIN DASHBOARD
# -----------------------
if st.session_state["user"]:

    user = st.session_state["user"]

    st.title("📊 Equb Smart Dashboard")
    st.write(f"👤 Logged in as: **{user}**")

    # -----------------------
    # DATABASE CONNECTION
    # -----------------------
    conn = sqlite3.connect("equb.db", check_same_thread=False)

    # -----------------------
    # SHOW USERS
    # -----------------------
    st.subheader("👥 Registered Users")
    users = auth.get_all_users()
    st.write(users)

    # -----------------------
    # CONTRIBUTION
    # -----------------------
    st.subheader("💳 Contribution")

    amount = st.number_input("Enter Amount", min_value=0.0)

    if st.button("Pay"):
        if amount > 0:
            payment.save_payment(user, amount)
            st.success("✅ Payment successful")
        else:
            st.warning("⚠️ Enter valid amount")

    # -----------------------
    # LOAD CONTRIBUTIONS
    # -----------------------
    df = pd.DataFrame(payment.get_all_payments(),
                      columns=["User", "Amount", "Status", "Time"])

    st.subheader("📋 Contributions")
    st.dataframe(df)

    # -----------------------
    # MATHEMATICAL MODEL
    # -----------------------
    if len(users) > 0:

        members = np.array(users)
        weights = model.compute_weights(len(members))
        probs = model.compute_probabilities(weights)

        total = df["Amount"].sum() if not df.empty else 0

        st.subheader("📈 Probabilities")

        prob_df = pd.DataFrame({
            "Member": members,
            "Probability": probs
        })

        st.dataframe(prob_df)
        st.bar_chart(prob_df.set_index("Member"))

        # -----------------------
        # EXPECTED REWARD
        # -----------------------
        st.subheader("💰 Expected Rewards")

        exp = model.expected_rewards(probs, total)
        st.write(dict(zip(members, exp)))

        # -----------------------
        # FAIRNESS
        # -----------------------
        st.subheader("⚖️ Fairness (Variance)")
        st.write(model.fairness_metric(probs))

        # -----------------------
        # DRAW
        # -----------------------
        if st.button("🎲 Run Draw"):
            winner = model.run_draw(members, probs)
            st.success(f"🏆 Winner: {winner}")

    # -----------------------
    # ADMIN PANEL
    # -----------------------
    role = auth.get_user_role(user)

    if role == "admin":
        st.subheader("🛠️ Admin Panel")
        admin.admin_panel()

    # -----------------------
    # LOGOUT
    # -----------------------
    if st.sidebar.button("Logout"):
        st.session_state["user"] = None
        st.rerun()

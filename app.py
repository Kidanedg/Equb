import streamlit as st
import pandas as pd
import numpy as np

# MODULES
import auth
import group
import payment
import model
import admin

# -----------------------
# INIT SYSTEM
# -----------------------
auth.create_users_table()
auth.create_default_admin()
group.create_group_tables()
payment.create_contribution_table()

# -----------------------
# SESSION STATE
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
    st.subheader("📝 Register")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Create Account"):
        success, msg = auth.register_user(username, password)
        if success:
            st.success(msg)
        else:
            st.error(msg)

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
# MAIN APP
# -----------------------
if st.session_state["user"]:

    user = st.session_state["user"]

    st.title("📊 Equb Smart System")
    st.write(f"👤 Logged in as: **{user}**")

    # =======================
    # GROUP MANAGEMENT
    # =======================
    st.sidebar.subheader("🏦 Equb Groups")

    new_group = st.sidebar.text_input("New Group Name")

    if st.sidebar.button("Create Group"):
        success, msg = group.create_group(new_group, user)
        if success:
            st.sidebar.success(msg)
        else:
            st.sidebar.warning(msg)

    all_groups = group.get_groups()

    group_id = None

    if all_groups:
        group_dict = {
            f"{g[1]} (ID {g[0]})": g[0] for g in all_groups
        }

        selected_group = st.sidebar.selectbox(
            "Select Group", list(group_dict.keys())
        )

        group_id = group_dict[selected_group]

        if st.sidebar.button("Join Group"):
            success, msg = group.join_group(group_id, user)
            if success:
                st.sidebar.success(msg)
            else:
                st.sidebar.warning(msg)

    # =======================
    # GROUP DASHBOARD
    # =======================
    if group_id:

        st.header(f"🏦 {selected_group}")

        # -----------------------
        # MEMBERS
        # -----------------------
        members = group.get_group_members(group_id)

        st.subheader("👥 Members")
        st.write(members)

        # -----------------------
        # CONTRIBUTION
        # -----------------------
        st.subheader("💳 Contribution")

        amount = st.number_input("Enter Amount", min_value=0.0)

        if st.button("Pay"):
            success, msg = payment.save_payment(user, group_id, amount)
            if success:
                st.success(msg)
            else:
                st.warning(msg)

        # -----------------------
        # LOAD DATA
        # -----------------------
        data = payment.get_group_payments(group_id)

        df = pd.DataFrame(
            data,
            columns=["User", "Group", "Amount", "Status", "Time"]
        )

        st.subheader("📋 Contributions")

        if df.empty:
            st.info("No contributions yet")
        else:
            st.dataframe(df)

        # -----------------------
        # TOTAL
        # -----------------------
        total = payment.get_group_total(group_id)
        st.write(f"💰 Total Pool: **{total}**")

        # -----------------------
        # MATHEMATICAL MODEL
        # -----------------------
        if len(members) > 0:

            members_array = np.array(members)

            weights = model.compute_weights(len(members_array))
            probs = model.compute_probabilities(weights)

            # -----------------------
            # PROBABILITIES
            # -----------------------
            st.subheader("📈 Probabilities")

            prob_df = pd.DataFrame({
                "Member": members_array,
                "Probability": probs
            })

            st.dataframe(prob_df)
            st.bar_chart(prob_df.set_index("Member"))

            # -----------------------
            # EXPECTED REWARD
            # -----------------------
            st.subheader("💰 Expected Rewards")

            exp = model.expected_rewards(probs, total)
            st.write(dict(zip(members_array, exp)))

            # -----------------------
            # FAIRNESS
            # -----------------------
            st.subheader("⚖️ Fairness")

            fairness = model.fairness_metric(probs)
            st.write(fairness)

            # -----------------------
            # DRAW
            # -----------------------
            if st.button("🎲 Run Draw"):
                winner = model.run_draw(members_array, probs)
                st.success(f"🏆 Winner: {winner}")

    else:
        st.info("👈 Create or select a group")

    # =======================
    # ADMIN PANEL
    # =======================
    role = auth.get_user_role(user)

    if role == "admin":
        st.subheader("🛠️ Admin Panel")
        admin.admin_panel()

    # =======================
    # LOGOUT
    # =======================
    if st.sidebar.button("Logout"):
        st.session_state["user"] = None
        st.rerun()

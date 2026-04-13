import streamlit as st
import pandas as pd
import numpy as np

import auth
import group
import payment
import admin

# INIT
auth.create_users_table()
auth.create_default_admin()
group.create_group_tables()
payment.create_contribution_table()

if "user" not in st.session_state:
    st.session_state["user"] = None

menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

# -----------------------
# REGISTER
# -----------------------
if choice == "Register":
    st.title("Register")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Register"):
        success, msg = auth.register_user(u, p)
        st.success(msg) if success else st.error(msg)

# -----------------------
# LOGIN
# -----------------------
elif choice == "Login":
    st.title("Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if auth.login_user(u, p):
            st.session_state["user"] = u
            st.rerun()
        else:
            st.error("Invalid")

# -----------------------
# MAIN APP
# -----------------------
if st.session_state["user"]:

    user = st.session_state["user"]

    st.title("📊 Equb Smart System")
    st.write(f"👤 Logged in as: {user}")

    # -----------------------
    # CREATE GROUP
    # -----------------------
    st.sidebar.subheader("Create Group")

    gname = st.sidebar.text_input("Group Name")
    members_input = st.sidebar.text_area("Members (comma separated)")

    if st.sidebar.button("Create"):
        members = [m.strip() for m in members_input.split(",") if m.strip()]
        success, msg = group.create_group(gname, user, members)
        st.sidebar.success(msg) if success else st.sidebar.error(msg)
        st.rerun()

    # -----------------------
    # LOAD USER GROUPS ONLY
    # -----------------------
    user_groups = group.get_user_groups(user)

    if not user_groups:
        st.info("No group yet")
        st.stop()

    gdict = {f"{g[1]} (ID {g[0]})": g[0] for g in user_groups}
    selected = st.sidebar.selectbox("Select Group", list(gdict.keys()))
    gid = gdict[selected]

    st.header(selected)

    # -----------------------
    # MEMBERS
    # -----------------------
    members = group.get_group_members(gid)
    st.write("👥 Members:", members)

    # -----------------------
    # CYCLE
    # -----------------------
    cycle = group.get_cycle(gid)
    st.subheader(f"🔄 Cycle: {cycle}")

    eligible = group.get_eligible_members(gid)
    st.write("Eligible:", eligible)

    # -----------------------
    # PAYMENT
    # -----------------------
    amount = st.number_input("Amount", min_value=0.0)

    if st.button("Pay"):
        success, msg = payment.save_payment(user, gid, amount)
        st.success(msg) if success else st.error(msg)

    # -----------------------
    # TOTAL
    # -----------------------
    total = payment.get_group_total(gid)
    st.write(f"💰 Total Pool: {total}")

    # -----------------------
    # DRAW
    # -----------------------
    if eligible:

        probs = np.ones(len(eligible)) / len(eligible)

        if st.button("🎲 Draw Winner"):
            winner = np.random.choice(eligible, p=probs)

            group.save_winner(gid, winner)

            st.success(f"🏆 Winner: {winner}")

            if group.check_cycle_reset(gid):
                st.info("🔁 New cycle started!")

            st.rerun()

    else:
        st.warning("All members received → resetting soon")

    # -----------------------
    # PAYMENTS DATA
    # -----------------------
    data = payment.get_group_payments(gid)

    df = pd.DataFrame(
        data,
        columns=["User", "Group", "Amount", "Status", "Time"]
    )

    st.dataframe(df)

    # -----------------------
    # ADMIN
    # -----------------------
    if auth.get_user_role(user) == "admin":
        admin.admin_panel()

    if st.sidebar.button("Logout"):
        st.session_state["user"] = None
        st.rerun()

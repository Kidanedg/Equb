import streamlit as st
import sqlite3
import pandas as pd

conn = sqlite3.connect("equb.db", check_same_thread=False)
c = conn.cursor()

# -----------------------
# ADMIN PANEL
# -----------------------
def admin_panel():

    st.write("### 🧑‍💼 System Administration")

    tab1, tab2, tab3 = st.tabs([
        "👤 Users",
        "🏦 Groups",
        "💳 Payments"
    ])

    # =========================
    # USERS
    # =========================
    with tab1:
        st.subheader("👤 Users")

        users = c.execute("SELECT username, role FROM users").fetchall()
        df = pd.DataFrame(users, columns=["Username", "Role"])

        st.dataframe(df)

        # Delete user
        user_to_delete = st.text_input("Delete Username")

        if st.button("Delete User"):
            try:
                c.execute("DELETE FROM users WHERE username=?", (user_to_delete,))
                conn.commit()
                st.success("User deleted")
            except Exception as e:
                st.error(str(e))

    # =========================
    # GROUPS
    # =========================
    with tab2:
        st.subheader("🏦 Groups")

        groups = c.execute("SELECT id, name, owner FROM groups").fetchall()
        df = pd.DataFrame(groups, columns=["ID", "Name", "Owner"])

        st.dataframe(df)

        group_id = st.number_input("Group ID to delete", step=1)

        if st.button("Delete Group"):
            try:
                c.execute("DELETE FROM groups WHERE id=?", (group_id,))
                c.execute("DELETE FROM group_members WHERE group_id=?", (group_id,))
                conn.commit()
                st.success("Group deleted")
            except Exception as e:
                st.error(str(e))

    # =========================
    # PAYMENTS
    # =========================
    with tab3:
        st.subheader("💳 Payments")

        payments = c.execute("""
            SELECT id, user, group_id, amount, status, timestamp
            FROM contributions
        """).fetchall()

        df = pd.DataFrame(
            payments,
            columns=["ID", "User", "Group", "Amount", "Status", "Time"]
        )

        st.dataframe(df)

        payment_id = st.number_input("Payment ID to delete", step=1)

        if st.button("Delete Payment"):
            try:
                c.execute("DELETE FROM contributions WHERE id=?", (payment_id,))
                conn.commit()
                st.success("Payment deleted")
            except Exception as e:
                st.error(str(e))

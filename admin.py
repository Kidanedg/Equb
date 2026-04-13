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

        users = c.execute("""
            SELECT username, role FROM users
            ORDER BY username
        """).fetchall()

        df = pd.DataFrame(users, columns=["Username", "Role"])
        st.dataframe(df)

        st.markdown("#### ⚠️ Delete User")

        user_to_delete = st.text_input("Username to delete")

        if st.button("Delete User"):
            if not user_to_delete:
                st.warning("Enter username")
            elif user_to_delete == "admin":
                st.error("Cannot delete default admin")
            else:
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

        groups = c.execute("""
            SELECT id, name, owner, cycle_no FROM groups
        """).fetchall()

        group_data = []

        for g in groups:
            gid = g[0]

            member_count = c.execute("""
                SELECT COUNT(*) FROM group_members WHERE group_id=?
            """, (gid,)).fetchone()[0]

            total = c.execute("""
                SELECT SUM(amount) FROM contributions WHERE group_id=?
            """, (gid,)).fetchone()[0]

            group_data.append([
                g[0], g[1], g[2], g[3],
                member_count,
                total if total else 0
            ])

        df = pd.DataFrame(
            group_data,
            columns=["ID", "Name", "Owner", "Cycle", "Members", "Total Pool"]
        )

        st.dataframe(df)

        st.markdown("#### ⚠️ Delete Group")

        group_id = st.number_input("Group ID", step=1)

        if st.button("Delete Group"):
            if group_id <= 0:
                st.warning("Enter valid group ID")
            else:
                try:
                    c.execute("DELETE FROM groups WHERE id=?", (group_id,))
                    c.execute("DELETE FROM group_members WHERE group_id=?", (group_id,))
                    c.execute("DELETE FROM contributions WHERE group_id=?", (group_id,))
                    c.execute("DELETE FROM winners WHERE group_id=?", (group_id,))
                    conn.commit()
                    st.success("Group and all data deleted")
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
            ORDER BY timestamp DESC
        """).fetchall()

        df = pd.DataFrame(
            payments,
            columns=["ID", "User", "Group", "Amount", "Status", "Time"]
        )

        st.dataframe(df)

        # -----------------------
        # SUMMARY
        # -----------------------
        st.markdown("### 📊 Summary")

        total = c.execute("""
            SELECT SUM(amount) FROM contributions
        """).fetchone()[0]

        count = c.execute("""
            SELECT COUNT(*) FROM contributions
        """).fetchone()[0]

        st.write(f"💰 Total Money: {total if total else 0}")
        st.write(f"📦 Total Transactions: {count}")

        # -----------------------
        # DELETE PAYMENT
        # -----------------------
        st.markdown("#### ⚠️ Delete Payment")

        payment_id = st.number_input("Payment ID", step=1)

        if st.button("Delete Payment"):
            if payment_id <= 0:
                st.warning("Enter valid ID")
            else:
                try:
                    c.execute("DELETE FROM contributions WHERE id=?", (payment_id,))
                    conn.commit()
                    st.success("Payment deleted")
                except Exception as e:
                    st.error(str(e))

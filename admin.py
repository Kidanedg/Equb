import streamlit as st
import pandas as pd
import sqlite3

conn = sqlite3.connect("equb.db", check_same_thread=False)

def admin_panel():
    st.subheader("🛠️ Admin Dashboard")

    df = pd.read_sql("SELECT * FROM contributions", conn)
    st.write("All Contributions")
    st.dataframe(df)

    if not df.empty:
        st.write("📊 Contributions Summary")
        st.bar_chart(df.groupby("user")["amount"].sum())

    if st.button("Run Global Draw"):
        st.warning("Admin triggered system-wide draw")

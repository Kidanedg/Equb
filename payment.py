import sqlite3
from datetime import datetime

# -----------------------
# DATABASE
# -----------------------
conn = sqlite3.connect("equb.db", check_same_thread=False)
c = conn.cursor()

# -----------------------
# CREATE TABLE
# -----------------------
def create_contribution_table():
    c.execute("""
    CREATE TABLE IF NOT EXISTS contributions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        group_id INTEGER,
        amount REAL,
        status TEXT,
        timestamp TEXT
    )
    """)
    conn.commit()

# -----------------------
# SAVE PAYMENT
# -----------------------
def save_payment(user, group_id, amount):

    if amount <= 0:
        return False, "Amount must be greater than 0"

    try:
        c.execute("""
        INSERT INTO contributions (user, group_id, amount, status, timestamp)
        VALUES (?, ?, ?, ?, ?)
        """, (
            user,
            group_id,
            amount,
            "paid",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        conn.commit()
        return True, "Payment recorded"

    except Exception as e:
        return False, str(e)

# -----------------------
# GET PAYMENTS
# -----------------------
def get_group_payments(group_id):
    try:
        return c.execute("""
        SELECT user, group_id, amount, status, timestamp
        FROM contributions
        WHERE group_id=?
        ORDER BY timestamp DESC
        """, (group_id,)).fetchall()

    except Exception as e:
        print("ERROR:", e)
        return []

# -----------------------
# TOTAL
# -----------------------
def get_group_total(group_id):
    result = c.execute("""
        SELECT SUM(amount)
        FROM contributions
        WHERE group_id=?
    """, (group_id,)).fetchone()

    return result[0] if result[0] else 0

import sqlite3
from datetime import datetime

# -----------------------
# DATABASE CONNECTION
# -----------------------
conn = sqlite3.connect("equb.db", check_same_thread=False)
conn.execute("PRAGMA foreign_keys = ON")
c = conn.cursor()

# -----------------------
# CREATE TABLE
# -----------------------
def create_contribution_table():
    c.execute("""
    CREATE TABLE IF NOT EXISTS contributions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT NOT NULL,
        group_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        status TEXT DEFAULT 'completed',
        timestamp TEXT,
        FOREIGN KEY(group_id) REFERENCES groups(id) ON DELETE CASCADE
    )
    """)
    conn.commit()

# -----------------------
# SAVE PAYMENT
# -----------------------
def save_payment(user, group_id, amount):
    if not user or not group_id:
        return False, "Invalid user or group"

    if amount <= 0:
        return False, "Amount must be greater than 0"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        c.execute("""
        INSERT INTO contributions (user, group_id, amount, status, timestamp)
        VALUES (?, ?, ?, ?, ?)
        """, (user, group_id, amount, "completed", timestamp))

        conn.commit()
        return True, "Payment recorded"

    except Exception as e:
        return False, str(e)

# -----------------------
# GET GROUP PAYMENTS
# -----------------------
def get_group_payments(group_id):
    return c.execute("""
    SELECT user, group_id, amount, status, timestamp
    FROM contributions
    WHERE group_id=?
    ORDER BY timestamp DESC
    """, (group_id,)).fetchall()

# -----------------------
# GET USER PAYMENTS
# -----------------------
def get_user_payments(user):
    return c.execute("""
    SELECT user, group_id, amount, status, timestamp
    FROM contributions
    WHERE user=?
    ORDER BY timestamp DESC
    """, (user,)).fetchall()

# -----------------------
# TOTAL GROUP CONTRIBUTION
# -----------------------
def get_group_total(group_id):
    result = c.execute("""
    SELECT SUM(amount)
    FROM contributions
    WHERE group_id=?
    """, (group_id,)).fetchone()

    return result[0] if result[0] else 0

# -----------------------
# TOTAL USER CONTRIBUTION
# -----------------------
def get_user_total(user):
    result = c.execute("""
    SELECT SUM(amount)
    FROM contributions
    WHERE user=?
    """, (user,)).fetchone()

    return result[0] if result[0] else 0

# -----------------------
# COUNT PAYMENTS
# -----------------------
def count_group_payments(group_id):
    result = c.execute("""
    SELECT COUNT(*)
    FROM contributions
    WHERE group_id=?
    """, (group_id,)).fetchone()

    return result[0]

# -----------------------
# DELETE PAYMENT (ADMIN)
# -----------------------
def delete_payment(payment_id):
    try:
        c.execute(
            "DELETE FROM contributions WHERE id=?",
            (payment_id,)
        )
        conn.commit()
        return True, "Payment deleted"

    except Exception as e:
        return False, str(e)

# -----------------------
# UPDATE PAYMENT STATUS
# -----------------------
def update_payment_status(payment_id, status):
    try:
        c.execute(
            "UPDATE contributions SET status=? WHERE id=?",
            (status, payment_id)
        )
        conn.commit()
        return True, "Status updated"

    except Exception as e:
        return False, str(e)

# -----------------------
# GET LAST PAYMENT
# -----------------------
def get_last_payment(group_id):
    return c.execute("""
    SELECT user, amount, timestamp
    FROM contributions
    WHERE group_id=?
    ORDER BY timestamp DESC
    LIMIT 1
    """, (group_id,)).fetchone()

import sqlite3
from datetime import datetime

# -----------------------
# DATABASE CONNECTION
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
        user TEXT NOT NULL,
        group_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        status TEXT DEFAULT 'paid',
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
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
        return False, "Amount must be greater than zero"

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
        return True, "Payment saved successfully"

    except Exception as e:
        return False, str(e)


# -----------------------
# GET GROUP PAYMENTS
# -----------------------
def get_group_payments(group_id):

    try:
        rows = c.execute("""
        SELECT user, group_id, amount, status, timestamp
        FROM contributions
        WHERE group_id=?
        ORDER BY timestamp DESC
        """, (group_id,)).fetchall()

        return rows

    except Exception as e:
        print("ERROR:", e)
        return []


# -----------------------
# GET TOTAL POOL
# -----------------------
def get_group_total(group_id):

    result = c.execute("""
    SELECT SUM(amount)
    FROM contributions
    WHERE group_id=? AND status='paid'
    """, (group_id,)).fetchone()

    return result[0] if result[0] else 0.0


# -----------------------
# GET USER CONTRIBUTIONS
# -----------------------
def get_user_payments(username):

    return c.execute("""
    SELECT user, group_id, amount, status, timestamp
    FROM contributions
    WHERE user=?
    ORDER BY timestamp DESC
    """, (username,)).fetchall()


# -----------------------
# DELETE PAYMENT (ADMIN)
# -----------------------
def delete_payment(payment_id):

    try:
        c.execute("DELETE FROM contributions WHERE id=?", (payment_id,))
        conn.commit()
        return True, "Payment deleted"

    except Exception as e:
        return False, str(e)


# -----------------------
# UPDATE PAYMENT STATUS
# -----------------------
def update_payment_status(payment_id, new_status):

    try:
        c.execute("""
        UPDATE contributions
        SET status=?
        WHERE id=?
        """, (new_status, payment_id))

        conn.commit()
        return True, "Status updated"

    except Exception as e:
        return False, str(e)


# -----------------------
# GROUP SUMMARY
# -----------------------
def get_group_summary(group_id):

    total = get_group_total(group_id)

    count = c.execute("""
    SELECT COUNT(*)
    FROM contributions
    WHERE group_id=?
    """, (group_id,)).fetchone()[0]

    avg = c.execute("""
    SELECT AVG(amount)
    FROM contributions
    WHERE group_id=?
    """, (group_id,)).fetchone()[0]

    return {
        "total": total,
        "transactions": count,
        "average": avg if avg else 0
    }


# -----------------------
# CLEAR GROUP DATA (ADMIN)
# -----------------------
def clear_group_payments(group_id):

    try:
        c.execute("DELETE FROM contributions WHERE group_id=?", (group_id,))
        conn.commit()
        return True, "Group payments cleared"

    except Exception as e:
        return False, str(e)

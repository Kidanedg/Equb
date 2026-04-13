import sqlite3
from datetime import datetime

# -----------------------
# DATABASE CONNECTION
# -----------------------
conn = sqlite3.connect("equb.db", check_same_thread=False)
c = conn.cursor()

# -----------------------
# CREATE TABLE + MIGRATION
# -----------------------
def create_contribution_table():

    # Create full table (for new DB)
    c.execute("""
    CREATE TABLE IF NOT EXISTS contributions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        group_id INTEGER,
        amount REAL,
        status TEXT DEFAULT 'paid',
        timestamp TEXT
    )
    """)

    # 🔥 MIGRATION FIXES (for old DB)
    try:
        c.execute("ALTER TABLE contributions ADD COLUMN group_id INTEGER")
    except:
        pass

    try:
        c.execute("ALTER TABLE contributions ADD COLUMN status TEXT DEFAULT 'paid'")
    except:
        pass

    try:
        c.execute("ALTER TABLE contributions ADD COLUMN timestamp TEXT")
    except:
        pass

    conn.commit()


# -----------------------
# SAVE PAYMENT
# -----------------------
def save_payment(user, group_id, amount):

    if not user or not group_id:
        return False, "Invalid user or group"

    if amount <= 0:
        return False, "Amount must be greater than 0"

    try:
        c.execute("""
            INSERT INTO contributions (user, group_id, amount, status, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (user, group_id, amount, "paid", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        conn.commit()
        return True, "Payment saved successfully"

    except Exception as e:
        print("SAVE ERROR:", e)
        return False, str(e)


# -----------------------
# GET PAYMENTS
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
        print("FETCH ERROR:", e)
        return []


# -----------------------
# GET TOTAL CONTRIBUTION
# -----------------------
def get_group_total(group_id):

    try:
        result = c.execute("""
            SELECT SUM(amount)
            FROM contributions
            WHERE group_id=?
        """, (group_id,)).fetchone()

        if result and result[0] is not None:
            return float(result[0])

        return 0.0

    except Exception as e:
        print("TOTAL ERROR:", e)
        return 0.0


# -----------------------
# OPTIONAL: USER TOTAL
# -----------------------
def get_user_total(user, group_id):

    try:
        result = c.execute("""
            SELECT SUM(amount)
            FROM contributions
            WHERE user=? AND group_id=?
        """, (user, group_id)).fetchone()

        if result and result[0]:
            return float(result[0])

        return 0.0

    except:
        return 0.0


# -----------------------
# OPTIONAL: DELETE PAYMENT (ADMIN)
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

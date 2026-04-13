import sqlite3

conn = sqlite3.connect("equb.db", check_same_thread=False)
c = conn.cursor()

def create_contribution_table():
    c.execute("""
    CREATE TABLE IF NOT EXISTS contributions (
        user TEXT,
        group_id INTEGER,
        amount REAL,
        status TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()

def save_payment(user, group_id, amount):
    c.execute("INSERT INTO contributions VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
              (user, group_id, amount, "paid"))
    conn.commit()

def get_group_payments(group_id):
    return c.execute("SELECT * FROM contributions WHERE group_id=?", (group_id,)).fetchall()

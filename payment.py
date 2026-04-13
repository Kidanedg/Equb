import sqlite3

conn = sqlite3.connect("equb.db", check_same_thread=False)
c = conn.cursor()

def create_contribution_table():
    c.execute("""
    CREATE TABLE IF NOT EXISTS contributions (
        user TEXT,
        amount REAL,
        status TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()

def save_payment(user, amount):
    c.execute("INSERT INTO contributions VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
              (user, amount, "paid"))
    conn.commit()

def get_all_payments():
    return c.execute("SELECT * FROM contributions").fetchall()

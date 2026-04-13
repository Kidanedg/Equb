import sqlite3
import bcrypt

conn = sqlite3.connect("equb.db", check_same_thread=False)
c = conn.cursor()

def create_users_table():
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password BLOB,
        role TEXT
    )
    """)
    conn.commit()

def register_user(username, password):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        c.execute("INSERT INTO users VALUES (?, ?, ?)", (username, hashed, "user"))
        conn.commit()
        return True
    except:
        return False

def login_user(username, password):
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    result = c.fetchone()
    if result:
        return bcrypt.checkpw(password.encode(), result[0])
    return False

def get_user_role(username):
    c.execute("SELECT role FROM users WHERE username=?", (username,))
    result = c.fetchone()
    return result[0] if result else "user"

import sqlite3
import bcrypt

# -----------------------
# DATABASE CONNECTION
# -----------------------
conn = sqlite3.connect("equb.db", check_same_thread=False)
c = conn.cursor()

# -----------------------
# CREATE TABLE
# -----------------------
def create_users_table():
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password BLOB,
        role TEXT
    )
    """)
    conn.commit()

# -----------------------
# REGISTER USER
# -----------------------
def register_user(username, password, role="user"):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        c.execute("INSERT INTO users VALUES (?, ?, ?)", (username, hashed, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # user already exists

# -----------------------
# LOGIN USER
# -----------------------
def login_user(username, password):
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    result = c.fetchone()

    if result:
        return bcrypt.checkpw(password.encode(), result[0])
    return False

# -----------------------
# GET ROLE
# -----------------------
def get_user_role(username):
    c.execute("SELECT role FROM users WHERE username=?", (username,))
    result = c.fetchone()
    return result[0] if result else None

# -----------------------
# GET ALL USERS
# -----------------------
def get_all_users():
    c.execute("SELECT username FROM users")
    return [row[0] for row in c.fetchall()]

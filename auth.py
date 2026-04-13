import sqlite3
import bcrypt

# -----------------------
# DATABASE CONNECTION
# -----------------------
conn = sqlite3.connect("equb.db", check_same_thread=False)
c = conn.cursor()

# -----------------------
# CREATE USERS TABLE
# -----------------------
def create_users_table():
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password BLOB NOT NULL,
        role TEXT DEFAULT 'user'
    )
    """)
    conn.commit()

# -----------------------
# REGISTER USER
# -----------------------
def register_user(username, password, role="user"):
    if not username or not password:
        return False, "Username and password required"

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    try:
        c.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, hashed, role)
        )
        conn.commit()
        return True, "User registered successfully"

    except sqlite3.IntegrityError:
        return False, "Username already exists"

# -----------------------
# LOGIN USER
# -----------------------
def login_user(username, password):
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    result = c.fetchone()

    if result:
        stored_password = result[0]
        if bcrypt.checkpw(password.encode(), stored_password):
            return True
    return False

# -----------------------
# GET USER ROLE
# -----------------------
def get_user_role(username):
    c.execute("SELECT role FROM users WHERE username=?", (username,))
    result = c.fetchone()
    return result[0] if result else None

# -----------------------
# SET USER ROLE (ADMIN USE)
# -----------------------
def set_user_role(username, role):
    c.execute("UPDATE users SET role=? WHERE username=?", (role, username))
    conn.commit()

# -----------------------
# GET ALL USERS
# -----------------------
def get_all_users():
    c.execute("SELECT username, role FROM users")
    return c.fetchall()

# -----------------------
# DELETE USER (ADMIN)
# -----------------------
def delete_user(username):
    c.execute("DELETE FROM users WHERE username=?", (username,))
    conn.commit()

# -----------------------
# CHECK IF USER EXISTS
# -----------------------
def user_exists(username):
    c.execute("SELECT 1 FROM users WHERE username=?", (username,))
    return c.fetchone() is not None

# -----------------------
# CREATE DEFAULT ADMIN (RUN ONCE)
# -----------------------
def create_default_admin():
    if not user_exists("admin"):
        hashed = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt())
        c.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("admin", hashed, "admin")
        )
        conn.commit()

# -----------------------
# CHANGE PASSWORD
# -----------------------
def change_password(username, new_password):
    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
    c.execute(
        "UPDATE users SET password=? WHERE username=?",
        (hashed, username)
    )
    conn.commit()

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
# PASSWORD VALIDATION
# -----------------------
def validate_password(password):
    if len(password) < 4:
        return False, "Password must be at least 4 characters"
    return True, ""


# -----------------------
# REGISTER USER
# -----------------------
def register_user(username, password, role="user"):

    if not username or not password:
        return False, "Username and password required"

    valid, msg = validate_password(password)
    if not valid:
        return False, msg

    if user_exists(username):
        return False, "Username already exists"

    try:
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        c.execute("""
        INSERT INTO users (username, password, role)
        VALUES (?, ?, ?)
        """, (username.strip(), hashed, role))

        conn.commit()
        return True, "User registered successfully"

    except Exception as e:
        return False, str(e)


# -----------------------
# LOGIN USER
# -----------------------
def login_user(username, password):

    if not username or not password:
        return False

    c.execute("SELECT password FROM users WHERE username=?", (username,))
    result = c.fetchone()

    if result:
        stored_password = result[0]

        try:
            if bcrypt.checkpw(password.encode(), stored_password):
                return True
        except:
            return False

    return False


# -----------------------
# GET USER ROLE
# -----------------------
def get_user_role(username):
    c.execute("SELECT role FROM users WHERE username=?", (username,))
    result = c.fetchone()
    return result[0] if result else None


# -----------------------
# SET USER ROLE (ADMIN)
# -----------------------
def set_user_role(username, role):

    if role not in ["user", "admin"]:
        return False, "Invalid role"

    try:
        c.execute("""
        UPDATE users SET role=? WHERE username=?
        """, (role, username))
        conn.commit()
        return True, "Role updated"
    except Exception as e:
        return False, str(e)


# -----------------------
# GET ALL USERS
# -----------------------
def get_all_users():
    return c.execute("""
    SELECT username, role FROM users
    ORDER BY username
    """).fetchall()


# -----------------------
# DELETE USER (SAFE)
# -----------------------
def delete_user(username, current_user=None):

    # Prevent deleting yourself
    if username == current_user:
        return False, "You cannot delete yourself"

    try:
        c.execute("DELETE FROM users WHERE username=?", (username,))
        conn.commit()
        return True, "User deleted"
    except Exception as e:
        return False, str(e)


# -----------------------
# CHECK USER EXISTS
# -----------------------
def user_exists(username):
    result = c.execute(
        "SELECT 1 FROM users WHERE username=?",
        (username,)
    ).fetchone()

    return result is not None


# -----------------------
# CREATE DEFAULT ADMIN
# -----------------------
def create_default_admin():

    if not user_exists("admin"):

        hashed = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt())

        c.execute("""
        INSERT INTO users (username, password, role)
        VALUES (?, ?, ?)
        """, ("admin", hashed, "admin"))

        conn.commit()


# -----------------------
# CHANGE PASSWORD
# -----------------------
def change_password(username, new_password):

    valid, msg = validate_password(new_password)
    if not valid:
        return False, msg

    try:
        hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())

        c.execute("""
        UPDATE users SET password=?
        WHERE username=?
        """, (hashed, username))

        conn.commit()
        return True, "Password updated"

    except Exception as e:
        return False, str(e)

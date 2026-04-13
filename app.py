import sqlite3

# -----------------------
# DATABASE CONNECTION
# -----------------------
conn = sqlite3.connect("equb.db", check_same_thread=False)
c = conn.cursor()

# -----------------------
# CREATE TABLES
# -----------------------
def create_group_tables():

    c.execute("""
    CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        owner TEXT NOT NULL
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS group_members (
        group_id INTEGER,
        username TEXT,
        UNIQUE(group_id, username)
    )
    """)

    conn.commit()

# -----------------------
# CREATE GROUP
# -----------------------
def create_group(name, owner):

    if not name or not owner:
        return False, "Group name and owner required"

    try:
        c.execute(
            "INSERT INTO groups (name, owner) VALUES (?, ?)",
            (name.strip(), owner.strip())
        )

        group_id = c.lastrowid

        # Add owner as member
        c.execute("""
        INSERT OR IGNORE INTO group_members (group_id, username)
        VALUES (?, ?)
        """, (group_id, owner))

        conn.commit()
        return True, f"Group '{name}' created"

    except Exception as e:
        return False, str(e)

# -----------------------
# GET ALL GROUPS
# -----------------------
def get_groups():
    try:
        return c.execute("""
            SELECT id, name, owner
            FROM groups
            ORDER BY id DESC
        """).fetchall()

    except Exception as e:
        print("Error fetching groups:", e)
        return []

# -----------------------
# JOIN GROUP
# -----------------------
def join_group(group_id, username):

    if not group_id or not username:
        return False, "Invalid group or username"

    # Prevent duplicate join
    existing = c.execute(
        "SELECT 1 FROM group_members WHERE group_id=? AND username=?",
        (group_id, username)
    ).fetchone()

    if existing:
        return False, "User already in group"

    try:
        c.execute(
            "INSERT INTO group_members (group_id, username) VALUES (?, ?)",
            (group_id, username)
        )
        conn.commit()
        return True, "Joined group successfully"

    except Exception as e:
        return False, str(e)

# -----------------------
# LEAVE GROUP
# -----------------------
def leave_group(group_id, username):

    try:
        c.execute(
            "DELETE FROM group_members WHERE group_id=? AND username=?",
            (group_id, username)
        )
        conn.commit()
        return True, "Left group"

    except Exception as e:
        return False, str(e)

# -----------------------
# DELETE GROUP (OWNER ONLY)
# -----------------------
def delete_group(group_id, username):

    owner = c.execute(
        "SELECT owner FROM groups WHERE id=?",
        (group_id,)
    ).fetchone()

    if not owner:
        return False, "Group not found"

    if owner[0] != username:
        return False, "Only owner can delete group"

    try:
        c.execute("DELETE FROM groups WHERE id=?", (group_id,))
        c.execute("DELETE FROM group_members WHERE group_id=?", (group_id,))
        conn.commit()
        return True, "Group deleted"

    except Exception as e:
        return False, str(e)

# -----------------------
# GET GROUP MEMBERS
# -----------------------
def get_group_members(group_id):

    try:
        members = c.execute(
            "SELECT username FROM group_members WHERE group_id=?",
            (group_id,)
        ).fetchall()

        return [m[0] for m in members]

    except Exception as e:
        print("Error fetching members:", e)
        return []

# -----------------------
# GET USER GROUPS
# -----------------------
def get_user_groups(username):

    try:
        return c.execute("""
            SELECT g.id, g.name
            FROM groups g
            JOIN group_members gm ON g.id = gm.group_id
            WHERE gm.username=?
        """, (username,)).fetchall()

    except Exception as e:
        print("Error fetching user groups:", e)
        return []

# -----------------------
# CHECK MEMBERSHIP
# -----------------------
def is_member(group_id, username):

    result = c.execute(
        "SELECT 1 FROM group_members WHERE group_id=? AND username=?",
        (group_id, username)
    ).fetchone()

    return result is not None

# -----------------------
# GET GROUP INFO
# -----------------------
def get_group_info(group_id):

    return c.execute(
        "SELECT id, name, owner FROM groups WHERE id=?",
        (group_id,)
    ).fetchone()

# -----------------------
# COUNT MEMBERS
# -----------------------
def count_members(group_id):

    result = c.execute(
        "SELECT COUNT(*) FROM group_members WHERE group_id=?",
        (group_id,)
    ).fetchone()

    return result[0] if result else 0

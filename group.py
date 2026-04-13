import sqlite3

# -----------------------
# DATABASE CONNECTION
# -----------------------
conn = sqlite3.connect("equb.db", check_same_thread=False)
conn.execute("PRAGMA foreign_keys = ON")  # Enable FK
c = conn.cursor()

# -----------------------
# CREATE TABLES
# -----------------------
def create_group_tables():
    # GROUP TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        owner TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # MEMBERS TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS group_members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER,
        username TEXT,
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(group_id, username),
        FOREIGN KEY(group_id) REFERENCES groups(id) ON DELETE CASCADE
    )
    """)

    conn.commit()

# -----------------------
# CREATE GROUP
# -----------------------
def create_group(name, owner):
    if not name.strip():
        return False, "Group name required"

    try:
        # Prevent duplicate group names for same owner
        existing = c.execute(
            "SELECT 1 FROM groups WHERE name=? AND owner=?",
            (name, owner)
        ).fetchone()

        if existing:
            return False, "You already created this group"

        c.execute(
            "INSERT INTO groups (name, owner) VALUES (?, ?)",
            (name, owner)
        )
        group_id = c.lastrowid

        # Add owner as member
        c.execute("""
        INSERT OR IGNORE INTO group_members (group_id, username)
        VALUES (?, ?)
        """, (group_id, owner))

        conn.commit()
        return True, f"Group '{name}' created successfully"

    except Exception as e:
        return False, str(e)

# -----------------------
# JOIN GROUP
# -----------------------
def join_group(group_id, username):
    if not group_id or not username:
        return False, "Invalid input"

    # Check if group exists
    group = c.execute(
        "SELECT id FROM groups WHERE id=?",
        (group_id,)
    ).fetchone()

    if not group:
        return False, "Group not found"

    # Check duplicate
    existing = c.execute(
        "SELECT 1 FROM group_members WHERE group_id=? AND username=?",
        (group_id, username)
    ).fetchone()

    if existing:
        return False, "Already a member"

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
        # Prevent owner leaving
        owner = c.execute(
            "SELECT owner FROM groups WHERE id=?",
            (group_id,)
        ).fetchone()

        if owner and owner[0] == username:
            return False, "Owner cannot leave group"

        c.execute(
            "DELETE FROM group_members WHERE group_id=? AND username=?",
            (group_id, username)
        )
        conn.commit()

        return True, "Left group"

    except Exception as e:
        return False, str(e)

# -----------------------
# DELETE GROUP
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
        conn.commit()
        return True, "Group deleted"

    except Exception as e:
        return False, str(e)

# -----------------------
# GET ALL GROUPS
# -----------------------
def get_groups():
    return c.execute("""
        SELECT id, name, owner, created_at
        FROM groups
        ORDER BY id DESC
    """).fetchall()

# -----------------------
# GET GROUP MEMBERS
# -----------------------
def get_group_members(group_id):
    return [
        row[0] for row in c.execute(
            "SELECT username FROM group_members WHERE group_id=?",
            (group_id,)
        ).fetchall()
    ]

# -----------------------
# GET USER GROUPS
# -----------------------
def get_user_groups(username):
    return c.execute("""
        SELECT g.id, g.name
        FROM groups g
        JOIN group_members gm ON g.id = gm.group_id
        WHERE gm.username=?
    """, (username,)).fetchall()

# -----------------------
# CHECK MEMBERSHIP
# -----------------------
def is_member(group_id, username):
    return c.execute(
        "SELECT 1 FROM group_members WHERE group_id=? AND username=?",
        (group_id, username)
    ).fetchone() is not None

# -----------------------
# GROUP INFO
# -----------------------
def get_group_info(group_id):
    return c.execute("""
        SELECT id, name, owner, created_at
        FROM groups WHERE id=?
    """, (group_id,)).fetchone()

# -----------------------
# COUNT MEMBERS
# -----------------------
def count_members(group_id):
    result = c.execute(
        "SELECT COUNT(*) FROM group_members WHERE group_id=?",
        (group_id,)
    ).fetchone()
    return result[0] if result else 0

# -----------------------
# REMOVE MEMBER (ADMIN/OWNER)
# -----------------------
def remove_member(group_id, username, requester):
    owner = c.execute(
        "SELECT owner FROM groups WHERE id=?",
        (group_id,)
    ).fetchone()

    if not owner:
        return False, "Group not found"

    if requester != owner[0]:
        return False, "Only owner can remove members"

    try:
        c.execute(
            "DELETE FROM group_members WHERE group_id=? AND username=?",
            (group_id, username)
        )
        conn.commit()
        return True, "Member removed"

    except Exception as e:
        return False, str(e)

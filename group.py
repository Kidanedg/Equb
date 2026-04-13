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
# CREATE GROUP WITH MEMBERS
# -----------------------
def create_group(name, owner, members_list):
    if not name or not owner:
        return False, "Group name and owner required"

    try:
        # Create group
        c.execute(
            "INSERT INTO groups (name, owner) VALUES (?, ?)",
            (name.strip(), owner.strip())
        )
        group_id = c.lastrowid

        # Add owner
        c.execute("""
        INSERT OR IGNORE INTO group_members (group_id, username)
        VALUES (?, ?)
        """, (group_id, owner))

        # Add members
        for member in members_list:
            member = member.strip()
            if member:
                c.execute("""
                INSERT OR IGNORE INTO group_members (group_id, username)
                VALUES (?, ?)
                """, (group_id, member))

        conn.commit()
        return True, f"Group '{name}' created successfully"

    except Exception as e:
        return False, str(e)

# -----------------------
# GET ALL GROUPS
# -----------------------
def get_groups():
    return c.execute(
        "SELECT id, name, owner FROM groups ORDER BY id DESC"
    ).fetchall()

# -----------------------
# GET MEMBERS
# -----------------------
def get_group_members(group_id):
    return [
        row[0] for row in c.execute(
            "SELECT username FROM group_members WHERE group_id=?",
            (group_id,)
        ).fetchall()
    ]

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
# USER GROUPS
# -----------------------
def get_user_groups(username):
    return c.execute("""
        SELECT g.id, g.name
        FROM groups g
        JOIN group_members gm ON g.id = gm.group_id
        WHERE gm.username=?
    """, (username,)).fetchall()

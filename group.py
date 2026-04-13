import sqlite3

conn = sqlite3.connect("equb.db", check_same_thread=False)
c = conn.cursor()

def create_group_tables():
    c.execute("""
    CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        owner TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS group_members (
        group_id INTEGER,
        username TEXT
    )
    """)
    conn.commit()

def create_group(name, owner):
    c.execute("INSERT INTO groups (name, owner) VALUES (?, ?)", (name, owner))
    group_id = c.lastrowid

    # owner automatically joins
    c.execute("INSERT INTO group_members VALUES (?, ?)", (group_id, owner))
    conn.commit()

def join_group(group_id, username):
    c.execute("INSERT INTO group_members VALUES (?, ?)", (group_id, username))
    conn.commit()

def get_groups():
    return c.execute("SELECT * FROM groups").fetchall()

def get_user_groups(username):
    return c.execute("""
    SELECT g.id, g.name FROM groups g
    JOIN group_members gm ON g.id = gm.group_id
    WHERE gm.username=?
    """, (username,)).fetchall()

def get_group_members(group_id):
    return [row[0] for row in c.execute(
        "SELECT username FROM group_members WHERE group_id=?",
        (group_id,)
    ).fetchall()]

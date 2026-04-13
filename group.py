import sqlite3

conn = sqlite3.connect("equb.db", check_same_thread=False)
c = conn.cursor()

# -----------------------
# CREATE TABLES
# -----------------------
def create_group_tables():
    c.execute("""
    CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        owner TEXT,
        cycle_no INTEGER DEFAULT 1
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS group_members (
        group_id INTEGER,
        username TEXT,
        UNIQUE(group_id, username)
    )
    """)

    # Track winners per cycle
    c.execute("""
    CREATE TABLE IF NOT EXISTS winners (
        group_id INTEGER,
        username TEXT,
        cycle_no INTEGER
    )
    """)

    conn.commit()

# -----------------------
# CREATE GROUP
# -----------------------
def create_group(name, owner, members_list):

    c.execute(
        "INSERT INTO groups (name, owner) VALUES (?, ?)",
        (name, owner)
    )

    group_id = c.lastrowid

    # Add owner
    c.execute("""
    INSERT OR IGNORE INTO group_members VALUES (?, ?)
    """, (group_id, owner))

    # Add members
    for m in members_list:
        if m.strip():
            c.execute("""
            INSERT OR IGNORE INTO group_members VALUES (?, ?)
            """, (group_id, m.strip()))

    conn.commit()
    return True, "Group created"

# -----------------------
# GET GROUPS
# -----------------------
def get_groups():
    return c.execute("SELECT id, name FROM groups").fetchall()

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

# -----------------------
# MEMBERS
# -----------------------
def get_group_members(group_id):
    return [r[0] for r in c.execute(
        "SELECT username FROM group_members WHERE group_id=?",
        (group_id,)
    ).fetchall()]

# -----------------------
# JOIN GROUP
# -----------------------
def join_group(group_id, username):
    try:
        c.execute("""
        INSERT OR IGNORE INTO group_members VALUES (?, ?)
        """, (group_id, username))
        conn.commit()
        return True, "Joined group"
    except Exception as e:
        return False, str(e)

# -----------------------
# GET CURRENT CYCLE
# -----------------------
def get_cycle(group_id):
    return c.execute(
        "SELECT cycle_no FROM groups WHERE id=?",
        (group_id,)
    ).fetchone()[0]

# -----------------------
# GET ELIGIBLE MEMBERS
# -----------------------
def get_eligible_members(group_id):

    cycle = get_cycle(group_id)

    members = set(get_group_members(group_id))

    winners = set(r[0] for r in c.execute("""
        SELECT username FROM winners
        WHERE group_id=? AND cycle_no=?
    """, (group_id, cycle)).fetchall())

    return list(members - winners)

# -----------------------
# SAVE WINNER
# -----------------------
def save_winner(group_id, username):

    cycle = get_cycle(group_id)

    c.execute("""
    INSERT INTO winners VALUES (?, ?, ?)
    """, (group_id, username, cycle))

    conn.commit()

# -----------------------
# CHECK RESET CYCLE
# -----------------------
def check_cycle_reset(group_id):

    members = get_group_members(group_id)
    eligible = get_eligible_members(group_id)

    if len(eligible) == 0:
        # All members got reward → new cycle
        c.execute("""
        UPDATE groups SET cycle_no = cycle_no + 1 WHERE id=?
        """, (group_id,))
        conn.commit()
        return True

    return False

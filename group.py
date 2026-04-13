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
def create_group(name, owner, members):
    if not name:
        return False, "Group name required"

    c.execute(
        "INSERT INTO groups (name, owner) VALUES (?, ?)",
        (name, owner)
    )
    gid = c.lastrowid

    # add owner + members
    all_members = list(set(members + [owner]))

    for m in all_members:
        c.execute(
            "INSERT OR IGNORE INTO group_members VALUES (?, ?)",
            (gid, m)
        )

    conn.commit()
    return True, f"Group '{name}' created"


# -----------------------
# GET USER GROUPS ONLY
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
    rows = c.execute(
        "SELECT username FROM group_members WHERE group_id=?",
        (group_id,)
    ).fetchall()
    return [r[0] for r in rows]


# -----------------------
# CYCLE
# -----------------------
def get_cycle(group_id):
    result = c.execute(
        "SELECT cycle_no FROM groups WHERE id=?",
        (group_id,)
    ).fetchone()

    if result:
        return result[0]
    return 1


# -----------------------
# ELIGIBLE MEMBERS (NO REPEAT)
# -----------------------
def get_eligible_members(group_id):
    cycle = get_cycle(group_id)

    all_members = get_group_members(group_id)

    winners = c.execute("""
        SELECT username FROM winners
        WHERE group_id=? AND cycle_no=?
    """, (group_id, cycle)).fetchall()

    winners = [w[0] for w in winners]

    return [m for m in all_members if m not in winners]


# -----------------------
# SAVE WINNER
# -----------------------
def save_winner(group_id, username):
    cycle = get_cycle(group_id)

    c.execute("""
        INSERT INTO winners (group_id, username, cycle_no)
        VALUES (?, ?, ?)
    """, (group_id, username, cycle))

    conn.commit()


# -----------------------
# RESET CYCLE IF COMPLETE
# -----------------------
def check_cycle_reset(group_id):
    members = get_group_members(group_id)
    eligible = get_eligible_members(group_id)

    if len(eligible) == 0:
        c.execute("""
            UPDATE groups
            SET cycle_no = cycle_no + 1
            WHERE id=?
        """, (group_id,))
        conn.commit()
        return True

    return False

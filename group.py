import sqlite3

conn = sqlite3.connect("equb.db", check_same_thread=False)
c = conn.cursor()

# -----------------------
# CREATE TABLES + MIGRATION
# -----------------------
def create_group_tables():

    # CREATE TABLE (if new)
    c.execute("""
    CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        owner TEXT,
        cycle_no INTEGER DEFAULT 1
    )
    """)

    # 🔥 MIGRATION FIX (VERY IMPORTANT)
    try:
        c.execute("ALTER TABLE groups ADD COLUMN cycle_no INTEGER DEFAULT 1")
    except:
        pass  # already exists

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
        "INSERT INTO groups (name, owner, cycle_no) VALUES (?, ?, 1)",
        (name, owner)
    )
    gid = c.lastrowid

    # ensure owner included
    all_members = list(set(members + [owner]))

    for m in all_members:
        c.execute(
            "INSERT OR IGNORE INTO group_members (group_id, username) VALUES (?, ?)",
            (gid, m)
        )

    conn.commit()
    return True, f"Group '{name}' created successfully"


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
# GET MEMBERS
# -----------------------
def get_group_members(group_id):
    rows = c.execute(
        "SELECT username FROM group_members WHERE group_id=?",
        (group_id,)
    ).fetchall()
    return [r[0] for r in rows]


# -----------------------
# SAFE GET CYCLE
# -----------------------
def get_cycle(group_id):
    try:
        result = c.execute(
            "SELECT cycle_no FROM groups WHERE id=?",
            (group_id,)
        ).fetchone()

        if result and result[0] is not None:
            return result[0]

        return 1

    except Exception as e:
        print("Cycle error:", e)
        return 1


# -----------------------
# ELIGIBLE MEMBERS
# -----------------------
def get_eligible_members(group_id):
    cycle = get_cycle(group_id)

    members = get_group_members(group_id)

    winners = c.execute("""
        SELECT username FROM winners
        WHERE group_id=? AND cycle_no=?
    """, (group_id, cycle)).fetchall()

    winners = [w[0] for w in winners]

    return [m for m in members if m not in winners]


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
# RESET CYCLE
# -----------------------
def check_cycle_reset(group_id):
    members = get_group_members(group_id)
    eligible = get_eligible_members(group_id)

    if len(members) > 0 and len(eligible) == 0:
        c.execute("""
            UPDATE groups
            SET cycle_no = cycle_no + 1
            WHERE id=?
        """, (group_id,))
        conn.commit()
        return True

    return False

import os
import shutil
import sqlite3
import sys

DB_FILE = "notes.db"
DB_BACKUP = "notes.db.bak"

try:
    if not os.path.exists(DB_FILE):
        print("Failed: notes.db not found.")
        sys.exit(1)

    shutil.copy2(DB_FILE, DB_BACKUP)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.execute("PRAGMA table_info(notes)")
    columns = [row[1] for row in cursor.fetchall()]

    if "type" not in columns:
        conn.close()
        print("Success: No migration needed, 'type' column not found.")
        sys.exit(0)

    conn.execute("""
        CREATE TABLE notes_new (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            title      TEXT NOT NULL,
            subtitle   TEXT NOT NULL DEFAULT '',
            body       TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.execute("""
        INSERT INTO notes_new (id, title, subtitle, body, created_at)
        SELECT id, title, subtitle, body, created_at FROM notes
    """)

    count = conn.execute("SELECT COUNT(*) FROM notes_new").fetchone()[0]

    conn.execute("DROP TABLE notes")
    conn.execute("ALTER TABLE notes_new RENAME TO notes")
    conn.commit()
    conn.close()

    print(f"Success: {count} note{'s' if count != 1 else ''} migrated.")

except Exception as e:
    print(f"Failed: {e}")
    sys.exit(1)

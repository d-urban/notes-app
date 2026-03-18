import sqlite3
from datetime import datetime

DB_FILE = "notes.db"


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            title      TEXT NOT NULL,
            subtitle   TEXT NOT NULL DEFAULT '',
            body       TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def get_all_notes():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM notes ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def create_note(title: str, body: str, subtitle: str = ""):
    conn = get_connection()
    created_at = datetime.now().isoformat()
    cursor = conn.execute(
        "INSERT INTO notes (title, subtitle, body, created_at) VALUES (?, ?, ?, ?)",
        (title, subtitle, body, created_at)
    )
    conn.commit()
    note_id = cursor.lastrowid
    conn.close()
    return {"id": note_id, "title": title, "subtitle": subtitle, "body": body, "created_at": created_at}


def update_note(note_id: int, title: str, body: str, subtitle: str = ""):
    conn = get_connection()
    conn.execute(
        "UPDATE notes SET title = ?, subtitle = ?, body = ? WHERE id = ?",
        (title, subtitle, body, note_id)
    )
    conn.commit()
    conn.close()


def delete_note(note_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()

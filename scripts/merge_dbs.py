import os
import shutil
import sqlite3
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_FILE = os.path.join(ROOT_DIR, "notes.db.new")

NOTES_DDL = """
    CREATE TABLE notes (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        title      TEXT NOT NULL,
        subtitle   TEXT NOT NULL DEFAULT '',
        body       TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
"""

EXPECTED_COLUMNS = {"id", "title", "subtitle", "body", "created_at"}


def get_columns(conn):
    cursor = conn.execute("PRAGMA table_info(notes)")
    return {row[1] for row in cursor.fetchall()}


def validate_db(path):
    if not os.path.exists(path):
        print(f"Failed: file not found: {path}")
        sys.exit(1)
    if not os.path.isfile(path):
        print(f"Failed: not a file: {path}")
        sys.exit(1)

    try:
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
    except sqlite3.DatabaseError as e:
        print(f"Failed: could not open database '{path}': {e}")
        sys.exit(1)

    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    if "notes" not in tables:
        print(f"Failed: no 'notes' table found in '{path}'")
        conn.close()
        sys.exit(1)

    columns = get_columns(conn)
    if columns != EXPECTED_COLUMNS:
        missing = EXPECTED_COLUMNS - columns
        extra = columns - EXPECTED_COLUMNS
        parts = []
        if missing:
            parts.append(f"missing columns: {sorted(missing)}")
        if extra:
            parts.append(f"unexpected columns: {sorted(extra)}")
        print(f"Failed: incompatible schema in '{path}': {'; '.join(parts)}")
        conn.close()
        sys.exit(1)

    return conn


def backup_db(path):
    backup_path = path + ".pre.merge"
    shutil.copy2(path, backup_path)
    print(f"  Backed up: {backup_path}")


def fetch_notes(conn):
    cursor = conn.execute(
        "SELECT title, subtitle, body, created_at FROM notes"
    )
    return cursor.fetchall()


def merge(path1, path2):
    conn1 = validate_db(path1)
    conn2 = validate_db(path2)

    if os.path.exists(OUTPUT_FILE):
        print(f"Failed: output file already exists: {OUTPUT_FILE}")
        conn1.close()
        conn2.close()
        sys.exit(1)

    cols1 = get_columns(conn1)
    cols2 = get_columns(conn2)
    if cols1 != cols2:
        print(
            "Failed: schemas do not match between the two databases.\n"
            f"  {path1}: {sorted(cols1)}\n"
            f"  {path2}: {sorted(cols2)}"
        )
        conn1.close()
        conn2.close()
        sys.exit(1)

    backup_db(path1)
    backup_db(path2)

    rows1 = fetch_notes(conn1)
    rows2 = fetch_notes(conn2)
    conn1.close()
    conn2.close()

    out_conn = sqlite3.connect(OUTPUT_FILE)
    out_conn.execute(NOTES_DDL)
    out_conn.commit()

    seen = set()
    inserted1 = skipped1 = inserted2 = skipped2 = 0

    for row in rows1:
        title, subtitle, body, created_at = (
            row["title"],
            row["subtitle"],
            row["body"],
            row["created_at"],
        )
        key = (title, subtitle, body)
        if key in seen:
            skipped1 += 1
            continue
        seen.add(key)
        out_conn.execute(
            "INSERT INTO notes (title, subtitle, body, created_at) VALUES (?, ?, ?, ?)",
            (title, subtitle, body, created_at),
        )
        inserted1 += 1

    for row in rows2:
        title, subtitle, body, created_at = (
            row["title"],
            row["subtitle"],
            row["body"],
            row["created_at"],
        )
        key = (title, subtitle, body)
        if key in seen:
            skipped2 += 1
            continue
        seen.add(key)
        out_conn.execute(
            "INSERT INTO notes (title, subtitle, body, created_at) VALUES (?, ?, ?, ?)",
            (title, subtitle, body, created_at),
        )
        inserted2 += 1

    out_conn.commit()
    total = inserted1 + inserted2
    out_conn.close()

    print(f"Success: merged into '{OUTPUT_FILE}'")
    print(
        f"  {os.path.basename(path1)}: {inserted1} inserted, {skipped1} skipped (duplicate)"
    )
    print(
        f"  {os.path.basename(path2)}: {inserted2} inserted, {skipped2} skipped (duplicate)"
    )
    print(f"  Total notes in output: {total}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python scripts/merge_dbs.py <db_file_1> <db_file_2>")
        sys.exit(1)

    merge(sys.argv[1], sys.argv[2])

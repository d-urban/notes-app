# Notes App

A simple self-hosted notes app with rich text support, image pasting, search, and more.

## Features

- Add notes with a title, optional subtitle, and rich text body
- Paste screenshots directly into the body with Ctrl+V
- Search notes by title and subtitle, with an option to also search the body
- Long notes are collapsed with a "Show more" toggle
- Edit and delete existing notes

## Requirements

- Python 3
- FastAPI
- uvicorn

## Setup & Running

Install dependencies on ubuntu WSL environment:

```
apt update
apt install uvicorn python3-fastapi
```

Start the server:

```
python main.py
```

Then open your browser at `http://localhost:8000`.

## Systemd Service (Auto-start on Boot)

A script is included to set up a systemd service that starts the app automatically on boot. It dynamically resolves the working directory (from the script's location) and the current user. `sudo` is required.

```
chmod +x create_systemd_service.sh
./create_systemd_service.sh
```

## Database Migration

If you are upgrading from an older version of the app that used a `type` column (short/long notes), run the migration script once to convert your existing database:

```
python migrate_from_long_short_to_one_type.py
```

This will back up your existing `notes.db` to `notes.db.bak` before making any changes.

## File Overview

- `main.py` — FastAPI server and API endpoints
- `database.py` — SQLite database setup and queries
- `index.html` — Frontend UI served by the app
- `migrate_from_long_short_to_one_type.py` — One-time migration script for upgrading from older versions
- `create_systemd_service.sh` — Sets up and enables a systemd service to auto-start the app on boot

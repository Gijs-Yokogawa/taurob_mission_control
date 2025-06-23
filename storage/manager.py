# storage/manager.py
# Beheer van checkpoints in SQLite-database

import sqlite3
import json
from pathlib import Path

# Plaats database in subfolder 'checkpoints'
DB_DIR = Path(__file__).parent.parent / "checkpoints"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "checkpoints.db"

# Zorg dat de database en tabel bestaan bij eerste gebruik
def initialize_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS checkpoints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            checkpoint_id INTEGER,
            type TEXT,
            name TEXT,
            json TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()

# Laad alle checkpoints uit de DB, inclusief alle kolommen
def load_all_checkpoints():
    initialize_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, checkpoint_id, type, name, json, created_at
        FROM checkpoints
        ORDER BY id DESC;
        """
    )
    rows = cur.fetchall()
    conn.close()
    return rows

# Voeg een checkpoint toe of werk bij op checkpoint_id wanneer >0 (handmatige upsert)
def save_checkpoint(data: dict, checkpoint_id: int):
    initialize_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    jstr = json.dumps(data)
    # Voor templates (checkpoint_id <= 0) altijd nieuwe record, zet checkpoint_id op NULL
    if checkpoint_id > 0:
        # Check of er al een record bestaat met deze checkpoint_id
        cur.execute(
            "SELECT id FROM checkpoints WHERE checkpoint_id = ?",
            (checkpoint_id,)
        )
        exists = cur.fetchone()
        if exists:
            # Update bestaand record
            cur.execute(
                """
                UPDATE checkpoints
                SET type = ?, name = ?, json = ?, created_at = CURRENT_TIMESTAMP
                WHERE checkpoint_id = ?
                """,
                (
                    data.get("ActionType"),
                    data.get("ActionName"),
                    jstr,
                    checkpoint_id
                )
            )
        else:
            # Insert nieuw record met deze checkpoint_id
            cur.execute(
                """
                INSERT INTO checkpoints (checkpoint_id, type, name, json)
                VALUES (?, ?, ?, ?)
                """,
                (
                    checkpoint_id,
                    data.get("ActionType"),
                    data.get("ActionName"),
                    jstr
                )
            )
    else:
        # Templates of ad-hoc checkpoints: altijd nieuwe insert, gebruik NULL voor checkpoint_id
        cur.execute(
            """
            INSERT INTO checkpoints (checkpoint_id, type, name, json)
            VALUES (?, ?, ?, ?)
            """,
            (
                None,
                data.get("ActionType"),
                data.get("ActionName"),
                jstr
            )
        )
    conn.commit()
    conn.close()
    conn.close()

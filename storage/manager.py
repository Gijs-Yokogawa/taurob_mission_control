# storage/manager.py

import os
import sqlite3
import json
from pathlib import Path

DEFAULT_DB_PATH = "checkpoints/checkpoints_chat.db"  # Default locatie
CONFIG_FILE = Path(__file__).resolve().parent.parent / "db_config.json"


def get_db_path() -> str:
    """Bepaal het pad naar de database.

    Geeft eerst de waarde uit de omgevingsvariabele ``DB_PATH`` terug.
    Als deze niet aanwezig is, wordt gekeken naar ``db_config.json`` in de
    projectroot. In dat bestand kan een sleutel ``DB_PATH`` staan met het pad
    naar de database. Wanneer geen van beide aanwezig is, wordt
    ``DEFAULT_DB_PATH`` gebruikt.
    """

    env_path = os.getenv("DB_PATH")
    if env_path:
        return env_path

    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
            if isinstance(data, dict) and data.get("DB_PATH"):
                return data["DB_PATH"]
        except Exception:
            pass

    return DEFAULT_DB_PATH


def init_db():
    """Zorgt dat de tabel bestaat met de juiste structuur."""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS checkpoints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            checkpoint_id TEXT UNIQUE,
            type TEXT,
            name TEXT,
            json TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            modified_local INTEGER DEFAULT 0
        )
    """)

    # Zorg dat kolom modified_local bestaat (voor oudere databases)
    cursor.execute("PRAGMA table_info(checkpoints)")
    columns = [row[1] for row in cursor.fetchall()]
    if "modified_local" not in columns:
        cursor.execute(
            "ALTER TABLE checkpoints ADD COLUMN modified_local INTEGER DEFAULT 0"
        )

    conn.commit()
    conn.close()


def update_local_checkpoints_from_api(api_checkpoints: list):
    """Vervangt alle lokale checkpoints met data uit de API."""
    print("[DB] → update_local_checkpoints_from_api() aangeroepen")
    init_db()
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    cursor.execute("DELETE FROM checkpoints")

    for cp in api_checkpoints:
        cursor.execute(
            """
            INSERT INTO checkpoints (checkpoint_id, type, name, json, created_at, modified_local)
            VALUES (?, ?, ?, ?, ?, 0)
        """,
            (
                cp.get("ActionID"),
                cp.get("ActionType"),
                cp.get("ActionName"),
                json.dumps(cp),
                cp.get("created_at", ""),
            ),
        )

    conn.commit()
    conn.close()
    print(f"[DB] {len(api_checkpoints)} checkpoints uit API opgeslagen.")


def get_all_checkpoints_from_db(order_by="id", ascending=True):
    """Geeft alle checkpoints terug voor weergave in TreeView, gesorteerd."""
    init_db()
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    order_dir = "ASC" if ascending else "DESC"
    # Zorg dat order_by veilig is, beperk tot toegestane kolommen
    if order_by not in ("id", "checkpoint_id", "type", "name", "created_at"):
        order_by = "id"

    query = f"SELECT checkpoint_id, name, type, created_at FROM checkpoints ORDER BY {order_by} {order_dir}"
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    return rows


def get_checkpoint_json_by_id(checkpoint_id: str):
    """Haalt het volledige JSON-object van een checkpoint op."""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    cursor.execute("SELECT json FROM checkpoints WHERE checkpoint_id = ?", (checkpoint_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return json.loads(row[0])
    return None


def checkpoint_exists(checkpoint_id: str) -> bool:
    """Check of een checkpoint met dit ID bestaat."""
    init_db()
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM checkpoints WHERE checkpoint_id = ? LIMIT 1",
        (checkpoint_id,),
    )
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def save_checkpoint(checkpoint_data: dict, modified: bool = False):
    """Slaat een checkpoint op in de database, vervangt als deze al bestaat."""
    print("[DB] → save_checkpoint() aangeroepen")
    init_db()
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO checkpoints (checkpoint_id, type, name, json, created_at, modified_local)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(checkpoint_id) DO UPDATE SET
            type=excluded.type,
            name=excluded.name,
            json=excluded.json,
            created_at=excluded.created_at,
            modified_local=excluded.modified_local
    """,
        (
            checkpoint_data.get("id"),
            checkpoint_data.get("type"),
            checkpoint_data.get("name"),
            json.dumps(checkpoint_data),
            checkpoint_data.get("created_at", ""),
            int(modified),
        ),
    )

    conn.commit()
    conn.close()
    print(f"[DB] Checkpoint '{checkpoint_data.get('name')}' opgeslagen of bijgewerkt.")


def delete_checkpoint_local(checkpoint_id: str):
    """Verwijdert een checkpoint lokaal uit de database."""
    print("[DB] → delete_checkpoint_local() aangeroepen")
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    cursor.execute("DELETE FROM checkpoints WHERE checkpoint_id = ?", (checkpoint_id,))
    conn.commit()
    conn.close()
    print(f"[DB] Checkpoint met ID '{checkpoint_id}' verwijderd uit lokale DB.")


def mark_checkpoint_modified(checkpoint_id: str, modified: bool = True):
    """Markeer een checkpoint als lokaal aangepast."""
    init_db()
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE checkpoints SET modified_local = ? WHERE checkpoint_id = ?",
        (1 if modified else 0, checkpoint_id),
    )
    conn.commit()
    conn.close()


def get_modified_checkpoints() -> list:
    """Haal alle checkpoints op die lokaal aangepast zijn."""
    init_db()
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT json FROM checkpoints WHERE modified_local = 1")
    rows = cursor.fetchall()
    conn.close()
    return [json.loads(r[0]) for r in rows]

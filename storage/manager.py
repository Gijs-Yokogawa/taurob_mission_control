# storage/manager.py

import sqlite3
import json

DB_PATH = "checkpoints/checkpoints_synced.db"  # Pas dit aan indien nodig


def init_db():
    """Zorgt dat de tabel bestaat met de juiste structuur."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS checkpoints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            checkpoint_id TEXT UNIQUE,
            type TEXT,
            name TEXT,
            json TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def update_local_checkpoints_from_api(api_checkpoints: list):
    """Vervangt alle lokale checkpoints met data uit de API."""
    print("[DB] → update_local_checkpoints_from_api() aangeroepen")
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM checkpoints")

    for cp in api_checkpoints:
        cursor.execute("""
            INSERT INTO checkpoints (checkpoint_id, type, name, json, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            cp.get("ActionID"),
            cp.get("ActionType"),
            cp.get("ActionName"),
            json.dumps(cp),
            cp.get("created_at", "")
        ))

    conn.commit()
    conn.close()
    print(f"[DB] {len(api_checkpoints)} checkpoints uit API opgeslagen.")


def get_all_checkpoints_from_db(order_by="id", ascending=True):
    """Geeft alle checkpoints terug voor weergave in TreeView, gesorteerd."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
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
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT json FROM checkpoints WHERE checkpoint_id = ?", (checkpoint_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return json.loads(row[0])
    return None


def save_checkpoint(checkpoint_data: dict):
    """Slaat een checkpoint op in de database, vervangt als deze al bestaat."""
    print("[DB] → save_checkpoint() aangeroepen")
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO checkpoints (checkpoint_id, type, name, json, created_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(checkpoint_id) DO UPDATE SET
            type=excluded.type,
            name=excluded.name,
            json=excluded.json,
            created_at=excluded.created_at
    """, (
        checkpoint_data.get("id"),
        checkpoint_data.get("type"),
        checkpoint_data.get("name"),
        json.dumps(checkpoint_data),
        checkpoint_data.get("created_at", "")
    ))

    conn.commit()
    conn.close()
    print(f"[DB] Checkpoint '{checkpoint_data.get('name')}' opgeslagen of bijgewerkt.")


def delete_checkpoint_local(checkpoint_id: str):
    """Verwijdert een checkpoint lokaal uit de database."""
    print("[DB] → delete_checkpoint_local() aangeroepen")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM checkpoints WHERE checkpoint_id = ?", (checkpoint_id,))
    conn.commit()
    conn.close()
    print(f"[DB] Checkpoint met ID '{checkpoint_id}' verwijderd uit lokale DB.")

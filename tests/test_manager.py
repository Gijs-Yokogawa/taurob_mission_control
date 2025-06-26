import sqlite3
import json
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import storage.manager as manager


def setup_temp_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DB_PATH", str(db_path))
    manager.init_db()
    return db_path


def test_init_db_creates_table(tmp_path, monkeypatch):
    db_path = setup_temp_db(tmp_path, monkeypatch)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(checkpoints)")
    columns = [row[1] for row in cursor.fetchall()]
    conn.close()
    assert [
        "id",
        "checkpoint_id",
        "type",
        "name",
        "json",
        "created_at",
        "modified_local",
    ] == columns


def test_save_and_get_checkpoint(tmp_path, monkeypatch):
    setup_temp_db(tmp_path, monkeypatch)
    checkpoint = {
        "id": "123",
        "type": "demo",
        "name": "First",
        "created_at": "2024-01-01",
    }
    manager.save_checkpoint(checkpoint)
    result = manager.get_checkpoint_json_by_id("123")
    assert result["id"] == "123"
    assert result["name"] == "First"

    # Update the checkpoint and ensure it overwrites
    checkpoint["name"] = "Updated"
    manager.save_checkpoint(checkpoint)
    result = manager.get_checkpoint_json_by_id("123")
    assert result["name"] == "Updated"


def test_get_checkpoint_json_by_id_none(tmp_path, monkeypatch):
    setup_temp_db(tmp_path, monkeypatch)
    assert manager.get_checkpoint_json_by_id("missing") is None

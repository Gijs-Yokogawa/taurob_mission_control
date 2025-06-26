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


def test_get_all_checkpoints_sorted_case_insensitive(tmp_path, monkeypatch):
    setup_temp_db(tmp_path, monkeypatch)
    checkpoints = [
        {"id": "1", "type": "demo", "name": "alpha", "created_at": "2024-01-01"},
        {"id": "2", "type": "demo", "name": "Bravo", "created_at": "2024-01-01"},
        {"id": "3", "type": "demo", "name": "charlie", "created_at": "2024-01-01"},
    ]
    for cp in checkpoints:
        manager.save_checkpoint(cp)

    rows = manager.get_all_checkpoints_from_db(order_by="name", ascending=True)
    names = [r[1] for r in rows]
    assert names == ["alpha", "Bravo", "charlie"]

    rows_desc = manager.get_all_checkpoints_from_db(order_by="name", ascending=False)
    names_desc = [r[1] for r in rows_desc]
    assert names_desc == ["charlie", "Bravo", "alpha"]


def test_save_checkpoint_preserves_json(tmp_path, monkeypatch):
    setup_temp_db(tmp_path, monkeypatch)
    checkpoint = {
        "ActionID": "42",
        "ActionName": "demo",
        "ActionType": "drive",
        "RobotPose": "",
        "ActionInfo": "",
        "Metadata": "",
    }
    manager.save_checkpoint(checkpoint)
    result = manager.get_checkpoint_json_by_id("42")
    assert result == checkpoint


def test_save_checkpoint_sets_timestamp(tmp_path, monkeypatch):
    db_path = setup_temp_db(tmp_path, monkeypatch)
    checkpoint = {"id": "55", "type": "demo", "name": "t"}
    manager.save_checkpoint(checkpoint)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT created_at FROM checkpoints WHERE checkpoint_id = '55'")
    row = cursor.fetchone()[0]
    conn.close()
    assert row != ""


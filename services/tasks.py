"""Persistent, claim-safe Mara_OS task queue. No command execution."""
import sqlite3
import threading
import time
from pathlib import Path

_lock = threading.RLock()
SCHEMA = """CREATE TABLE IF NOT EXISTS tasks (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 description TEXT NOT NULL,
 state TEXT NOT NULL DEFAULT 'pending',
 agent TEXT,
 created_at INTEGER NOT NULL,
 updated_at INTEGER NOT NULL
)"""

def connect(path):
    db = sqlite3.connect(str(path), timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA busy_timeout=10000")
    db.execute(SCHEMA)
    db.commit()
    return db

def create_task(path, description):
    if not isinstance(description, str) or not 1 <= len(description.strip()) <= 2000:
        raise ValueError("Task description must be 1–2000 characters")
    with _lock, connect(path) as db:
        now = int(time.time())
        cur = db.execute("INSERT INTO tasks(description,created_at,updated_at) VALUES(?,?,?)",
                         (description.strip(), now, now))
        db.commit()
        return cur.lastrowid

def list_tasks(path):
    with _lock, connect(path) as db:
        return [dict(row) for row in db.execute("SELECT * FROM tasks ORDER BY id DESC LIMIT 200")]

def claim_task(path, agent):
    if agent not in ("Aria", "Alex", "Astyria", "Aurelius"):
        raise ValueError("Unknown agent")
    with _lock, connect(path) as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT id FROM tasks WHERE state='pending' ORDER BY id LIMIT 1").fetchone()
        if row is None:
            db.rollback()
            return None
        db.execute("UPDATE tasks SET state='claimed',agent=?,updated_at=? WHERE id=?",
                   (agent, int(time.time()), row["id"]))
        db.commit()
        return row["id"]

def finish_task(path, task_id, agent, success=True):
    if agent not in ("Aria", "Alex", "Astyria", "Aurelius"):
        raise ValueError("Unknown agent")
    with _lock, connect(path) as db:
        cur = db.execute(
            "UPDATE tasks SET state=?,updated_at=? WHERE id=? AND agent=? AND state='claimed'",
            ("done" if success else "failed", int(time.time()), task_id, agent))
        db.commit()
        return cur.rowcount == 1

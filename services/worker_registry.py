"""Persistent registry for independently managed Mara_OS worker slots."""
import sqlite3
import time
import uuid
from services.agent_workers import AGENTS, connect

KINDS = ("chat", "diagnostics")
MAX_PER_AGENT = 8

def initialize():
    with connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS worker_slots (
          id TEXT PRIMARY KEY, agent TEXT NOT NULL, kind TEXT NOT NULL,
          desired TEXT NOT NULL, created_at INTEGER NOT NULL, updated_at INTEGER NOT NULL)""")

def list_workers():
    initialize()
    with connect() as db:
        return [dict(row) for row in db.execute("SELECT * FROM worker_slots ORDER BY created_at,id")]

def add_worker(agent, kind):
    if agent not in AGENTS or kind not in KINDS:
        raise ValueError("Unknown agent or worker kind")
    initialize()
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        count = db.execute("SELECT COUNT(*) FROM worker_slots WHERE agent=? AND desired='running'",(agent,)).fetchone()[0]
        if count >= MAX_PER_AGENT:
            raise ValueError("Worker limit reached")
        now = int(time.time())
        ident = uuid.uuid4().hex
        db.execute("INSERT INTO worker_slots VALUES(?,?,?,?,?,?)",(ident,agent,kind,"running",now,now))
        return ident

def remove_worker(ident):
    initialize()
    with connect() as db:
        cur = db.execute("UPDATE worker_slots SET desired='stopped',updated_at=? WHERE id=? AND desired='running'",
                         (int(time.time()), ident))
        return cur.rowcount == 1

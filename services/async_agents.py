"""SQLite-backed asynchronous agent jobs. API submission never calls the model."""
import json
import sqlite3
import time
from pathlib import Path

AGENTS = ("Aria", "Alex", "Astyria", "Aurelius")
SCHEMA = """CREATE TABLE IF NOT EXISTS agent_jobs (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 agent TEXT NOT NULL, message TEXT NOT NULL,
 state TEXT NOT NULL DEFAULT 'queued',
 result TEXT, error TEXT,
 created_at INTEGER NOT NULL, updated_at INTEGER NOT NULL
)"""

def connect(path):
    db = sqlite3.connect(str(path), timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA busy_timeout=10000")
    db.execute(SCHEMA)
    db.commit()
    return db

def submit(path, agent, message):
    if agent not in AGENTS or not isinstance(message, str) or not 1 <= len(message.strip()) <= 8000:
        raise ValueError("Invalid agent or message")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with connect(path) as db:
        now = int(time.time())
        row = db.execute("INSERT INTO agent_jobs(agent,message,created_at,updated_at) VALUES(?,?,?,?)",
                         (agent, message.strip(), now, now))
        db.commit()
        return row.lastrowid

def get_job(path, job_id):
    if not isinstance(job_id, int) or job_id < 1:
        raise ValueError("Invalid job ID")
    with connect(path) as db:
        row = db.execute("SELECT id,agent,state,result,error,created_at,updated_at FROM agent_jobs WHERE id=?", (job_id,)).fetchone()
        return dict(row) if row else None

def list_jobs(path):
    with connect(path) as db:
        return [dict(row) for row in db.execute("SELECT id,agent,state,result,error,created_at,updated_at FROM agent_jobs ORDER BY id DESC LIMIT 100")]

def claim(path, agent):
    if agent not in AGENTS: raise ValueError("Invalid agent")
    with connect(path) as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT id,message FROM agent_jobs WHERE agent=? AND state='queued' ORDER BY id LIMIT 1", (agent,)).fetchone()
        if row:
            db.execute("UPDATE agent_jobs SET state='running',updated_at=? WHERE id=?", (int(time.time()),row["id"]))
        db.commit()
        return dict(row) if row else None

def finish(path, job_id, result=None, error=None):
    state = "failed" if error else "done"
    with connect(path) as db:
        db.execute("UPDATE agent_jobs SET state=?,result=?,error=?,updated_at=? WHERE id=? AND state='running'",
                   (state,json.dumps(result,ensure_ascii=False) if result is not None else None,
                    str(error)[:300] if error else None,int(time.time()),job_id))
        db.commit()

"""Mara_OS background worker service: durable jobs, independent agent loops.

No arbitrary shell execution or implicit root. Linux capabilities are delegated
only to explicitly authorized adapters.
"""
import asyncio
import json
import os
import sqlite3
import time
from pathlib import Path

AGENTS = ("Aria", "Alex", "Astyria", "Aurelius")
DB_PATH = Path(os.environ.get("MARA_WORKER_DB", "data/agent_workers.sqlite3"))
POLL_SECONDS = 1.5

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(DB_PATH), timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("""CREATE TABLE IF NOT EXISTS jobs (
      id INTEGER PRIMARY KEY AUTOINCREMENT, agent TEXT NOT NULL,
      kind TEXT NOT NULL, payload TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'pending',
      result TEXT, created_at INTEGER NOT NULL, updated_at INTEGER NOT NULL)""")
    db.execute("""CREATE TABLE IF NOT EXISTS events (
      id INTEGER PRIMARY KEY AUTOINCREMENT, job_id INTEGER NOT NULL,
      agent TEXT NOT NULL, state TEXT NOT NULL, message TEXT NOT NULL,
      created_at INTEGER NOT NULL)""")
    db.commit()
    return db

def event(db, job_id, agent, state, message):
    db.execute("INSERT INTO events(job_id,agent,state,message,created_at) VALUES(?,?,?,?,?)",
               (job_id, agent, state, message[:1000], int(time.time())))

def enqueue(agent, kind, payload):
    if agent not in AGENTS or kind not in ("chat", "diagnostics"):
        raise ValueError("Unknown agent or task kind")
    if not isinstance(payload, str) or not 1 <= len(payload) <= 8000:
        raise ValueError("Invalid payload")
    with connect() as db:
        now = int(time.time())
        cur = db.execute("INSERT INTO jobs(agent,kind,payload,created_at,updated_at) VALUES(?,?,?,?,?)",
                         (agent, kind, payload, now, now))
        event(db, cur.lastrowid, agent, "pending", "Queued")
        return cur.lastrowid

def get_jobs(agent=None, limit=50):
    with connect() as db:
        if agent is not None and agent not in AGENTS:
            raise ValueError("Unknown agent")
        rows = db.execute("SELECT id,agent,kind,state,result,created_at,updated_at FROM jobs WHERE (? IS NULL OR agent=?) ORDER BY id DESC LIMIT ?",
                          (agent, agent, min(max(int(limit), 1), 200))).fetchall()
        return [dict(row) for row in rows]

def get_events(job_id):
    with connect() as db:
        return [dict(row) for row in db.execute(
            "SELECT id,agent,state,message,created_at FROM events WHERE job_id=? ORDER BY id", (job_id,))]

def claim(agent, kind=None):
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT id,kind,payload FROM jobs WHERE agent=? AND state='pending' AND (? IS NULL OR kind=?) ORDER BY id LIMIT 1", (agent, kind, kind)).fetchone()
        if row is None:
            return None
        now = int(time.time())
        db.execute("UPDATE jobs SET state='running',updated_at=? WHERE id=?", (now, row["id"]))
        event(db, row["id"], agent, "running", "Worker started")
        return dict(row)

async def execute(agent, job):
    if job["kind"] == "chat":
        from services.openai_agents import run_agent
        response = await asyncio.wait_for(asyncio.to_thread(run_agent, agent, job["payload"]), timeout=120)
        return response["text"]
    if job["kind"] == "diagnostics":
        from shell.mara_shell import run_adapter, COMMANDS
        if job["payload"] not in COMMANDS:
            raise ValueError("Unknown diagnostic adapter")
        return json.dumps(await run_adapter(job["payload"]), ensure_ascii=False)
    raise ValueError("Unsupported task kind")

def desktop_signal(agent, window, action):
    try:
        from services.live_desktop import emit
        emit(agent, window, action)
    except (OSError, sqlite3.Error) as exc:
        print(f'Desktop event unavailable: {type(exc).__name__}', flush=True)

async def worker(agent, kind=None, slot_id=None):
    while True:
        if slot_id:
            from services.worker_registry import list_workers
            slot = next((x for x in await asyncio.to_thread(list_workers) if x['id'] == slot_id), None)
            if not slot or slot['desired'] != 'running':
                return
        job = await asyncio.to_thread(claim, agent, kind)
        if job is None:
            await asyncio.sleep(POLL_SECONDS)
            continue
        window = 'terminal' if job['kind'] == 'diagnostics' else 'chat'
        await asyncio.to_thread(desktop_signal, agent, window, 'show')
        await asyncio.to_thread(desktop_signal, agent, 'logs', 'show')
        try:
            result = await execute(agent, job)
            state, message = "done", "Completed"
        except Exception as exc:
            result = type(exc).__name__
            state, message = "failed", "Execution failed"
        with connect() as db:
            db.execute("UPDATE jobs SET state=?,result=?,updated_at=? WHERE id=?",
                       (state, str(result)[:24000], int(time.time()), job["id"]))
            event(db, job["id"], agent, state, message)
        # Keep the task's result visible; only the agent/user should dismiss it.

async def main():
    # Crash recovery: requeue incomplete jobs on restart.
    with connect() as db:
        db.execute("UPDATE jobs SET state='pending',updated_at=? WHERE state='running'", (int(time.time()),))
    from services.worker_registry import initialize, list_workers
    await asyncio.to_thread(initialize)
    active = {}
    try:
        while True:
            slots = await asyncio.to_thread(list_workers)
            desired = {x['id']: x for x in slots if x['desired'] == 'running'}
            for ident, task in list(active.items()):
                if ident not in desired or task.done():
                    if not task.done():
                        task.cancel()
                    active.pop(ident)
            for ident, slot in desired.items():
                if ident not in active:
                    active[ident] = asyncio.create_task(worker(slot['agent'], slot['kind'], ident))
            await asyncio.sleep(POLL_SECONDS)
    finally:
        for task in active.values():
            task.cancel()
        await asyncio.gather(*active.values(), return_exceptions=True)

if __name__ == "__main__":
    asyncio.run(main())

"""Persisted AI desktop window intents; UI-only, no OS window-manager control."""
import json
import sqlite3
import time
from services.agent_workers import AGENTS, connect

WINDOWS = ("chat", "terminal", "logs", "workers", "files", "resources")
ACTIONS = ("show", "hide")
def initialize():
    with connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS desktop_events (
          id INTEGER PRIMARY KEY AUTOINCREMENT, agent TEXT NOT NULL,
          window TEXT NOT NULL, action TEXT NOT NULL, created_at INTEGER NOT NULL)""")
def emit(agent, window, action):
    if agent not in AGENTS or window not in WINDOWS or action not in ACTIONS:
        raise ValueError("Invalid desktop event")
    initialize()
    with connect() as db:
        cur = db.execute("INSERT INTO desktop_events(agent,window,action,created_at) VALUES(?,?,?,?)",
                         (agent,window,action,int(time.time())))
        return cur.lastrowid
def events(since=0, limit=100):
    initialize()
    since=max(0,int(since)); limit=min(200,max(1,int(limit)))
    with connect() as db:
        return [dict(x) for x in db.execute(
            "SELECT id,agent,window,action,created_at FROM desktop_events WHERE id>? ORDER BY id LIMIT ?",
            (since,limit))]

"""Persistent, ordered global synchronization events for Mara_OS clients."""
import json
import os
import sqlite3
import time
from pathlib import Path

DB_PATH=Path(os.environ.get("MARA_SYNC_DB","data/global_sync.sqlite3"))
TOPICS=("chat","terminal","python","workers","tasks","logs","vision","desktop","files","system")
MAX_PAYLOAD=16_000

def connect():
    DB_PATH.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(str(DB_PATH),timeout=10)
    db.row_factory=sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("""CREATE TABLE IF NOT EXISTS sync_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT NOT NULL, kind TEXT NOT NULL,
        payload TEXT NOT NULL, created_at INTEGER NOT NULL)""")
    db.commit()
    return db

def publish(topic,kind,payload):
    if topic not in TOPICS or not isinstance(kind,str) or not 1<=len(kind)<=64 or not kind.replace("_","").replace("-","").isalnum():
        raise ValueError("Invalid synchronization topic or kind")
    if not isinstance(payload,dict):
        raise ValueError("Payload must be an object")
    encoded=json.dumps(payload,ensure_ascii=False,separators=(",",":"))
    if len(encoded.encode("utf-8"))>MAX_PAYLOAD:
        raise ValueError("Synchronization payload too large")
    with connect() as db:
        cur=db.execute("INSERT INTO sync_events(topic,kind,payload,created_at) VALUES(?,?,?,?)",
                       (topic,kind,encoded,int(time.time())))
        return cur.lastrowid

def events(since=0,limit=100):
    since=int(since)
    limit=int(limit)
    if since<0 or not 1<=limit<=200:
        raise ValueError("Invalid synchronization cursor")
    with connect() as db:
        rows=db.execute("SELECT id,topic,kind,payload,created_at FROM sync_events WHERE id>? ORDER BY id LIMIT ?",(since,limit)).fetchall()
        return [{**dict(row),"payload":json.loads(row["payload"])} for row in rows]

"""Persistent, bounded Real Vision result history. Images are never stored."""
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "data" / "vision.sqlite3"
AGENTS = ("Aria", "Alex", "Astyria", "Aurelius")

def _connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB, timeout=10)
    conn.execute("""CREATE TABLE IF NOT EXISTS vision_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent TEXT NOT NULL,
        source TEXT NOT NULL,
        question TEXT NOT NULL,
        result TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
    )""")
    return conn

def save(agent, source, question, result):
    if agent not in AGENTS or not isinstance(source,str) or not 1<=len(source)<=100 or not isinstance(question,str) or not 1<=len(question)<=4000 or not isinstance(result,str) or not 1<=len(result)<=20000:
        raise ValueError("Invalid vision history")
    with _connect() as conn:
        cur = conn.execute("INSERT INTO vision_history(agent,source,question,result) VALUES(?,?,?,?)", (agent,source,question,result))
        conn.execute("DELETE FROM vision_history WHERE id NOT IN (SELECT id FROM vision_history ORDER BY id DESC LIMIT 200)")
        return cur.lastrowid

def list_recent(limit=20):
    if not isinstance(limit,int) or not 1<=limit<=100:
        raise ValueError("Invalid limit")
    with _connect() as conn:
        conn.row_factory=sqlite3.Row
        return [dict(row) for row in conn.execute("SELECT id,agent,source,question,result,created_at FROM vision_history ORDER BY id DESC LIMIT ?",(limit,))]

def delete_all():
    with _connect() as conn:
        return conn.execute("DELETE FROM vision_history").rowcount


from __future__ import annotations
import sqlite3, os, json, time

DB="runtime/state/sessions.db"
os.makedirs("runtime/state", exist_ok=True)

def init():
    conn=sqlite3.connect(DB); c=conn.cursor()
    c.execute("create table if not exists sessions (sid text primary key, data text, ts integer)")
    conn.commit(); conn.close()

def save(sid: str, data: dict):
    init()
    conn=sqlite3.connect(DB); c=conn.cursor()
    c.execute("insert or replace into sessions (sid, data, ts) values (?,?,?)", (sid, json.dumps(data), int(time.time())))
    conn.commit(); conn.close()

def load(sid: str) -> dict | None:
    init()
    conn=sqlite3.connect(DB); c=conn.cursor()
    c.execute("select data from sessions where sid=?", (sid,))
    row=c.fetchone(); conn.close()
    return json.loads(row[0]) if row else None

def all() -> list[dict]:
    init()
    conn=sqlite3.connect(DB); c=conn.cursor()
    out=[]
    for sid,data,ts in c.execute("select sid, data, ts from sessions order by ts desc"):
        d=json.loads(data); d['_sid']=sid; d['_ts']=ts; out.append(d)
    conn.close(); return out

def purge(before_ts: int) -> int:
    init()
    conn=sqlite3.connect(DB); c=conn.cursor()
    c.execute("delete from sessions where ts < ?", (before_ts,))
    n=c.rowcount; conn.commit(); conn.close(); return n

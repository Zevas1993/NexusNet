
from __future__ import annotations
import sqlite3, os
from typing import List, Tuple, Optional
from .schemas import AtomicFact

class TKG:
    def __init__(self, db_path: str = "runtime/temporal/tkg.sqlite"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db = sqlite3.connect(db_path)
        self._init()

    def _init(self):
        cur = self.db.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS facts(
                id INTEGER PRIMARY KEY,
                subject TEXT, predicate TEXT, object TEXT,
                prov_source TEXT, prov_url TEXT, prov_author TEXT, prov_conf REAL,
                start TEXT, end TEXT, meta TEXT
            )
        """)
        self.db.commit()

    def upsert(self, facts: List[AtomicFact]) -> int:
        cur = self.db.cursor()
        n=0
        for f in facts:
            cur.execute("""INSERT INTO facts(subject,predicate,object,prov_source,prov_url,prov_author,prov_conf,start,end,meta)
              VALUES(?,?,?,?,?,?,?,?,?,?)""", (
                f.subject, f.predicate, f.obj,
                f.prov.source, f.prov.url, f.prov.author, f.prov.confidence,
                f.window.start, f.window.end, (f.meta or {}).__repr__()
            ))
            n+=1
        self.db.commit()
        return n

    def as_of(self, query: str, date_iso: str) -> List[Tuple]:
        # naive search: filter by LIKE and window
        cur = self.db.cursor()
        like = f"%{query}%"
        cur.execute("""SELECT subject,predicate,object,start,end,prov_source,prov_conf
                       FROM facts WHERE (subject LIKE ? OR object LIKE ?) AND (start IS NULL OR start<=?) AND (end IS NULL OR end>=?)""",
                    (like, like, date_iso, date_iso))
        return cur.fetchall()

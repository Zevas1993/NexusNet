
import os, duckdb, re, json, hashlib, time
from typing import List, Dict, Any, Optional
from .config import settings

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "temporal.duckdb"))
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def _connect():
    con = duckdb.connect(DB_PATH)
    con.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        doc_id TEXT PRIMARY KEY,
        domain TEXT,
        text TEXT,
        ts TIMESTAMP
    );
    """)
    con.execute("""
    CREATE TABLE IF NOT EXISTS edges (
        src TEXT,
        dst TEXT,
        relation TEXT,
        ts TIMESTAMP
    );
    """)
    return con

def _simple_bm25(query: str, texts: List[str]) -> List[int]:
    # Naive BM25-like scoring based on term frequency; sufficient for offline default
    words = re.findall(r"\w+", query.lower())
    scores = []
    for i, t in enumerate(texts):
        tokens = re.findall(r"\w+", t.lower())
        score = sum(tokens.count(w) for w in words)
        scores.append((score, i))
    scores.sort(reverse=True)
    return [i for _, i in scores]

def _entailment_gate(query: str, text: str) -> bool:
    # Lightweight lexical entailment: require >= 2 overlapping keywords
    q = set(re.findall(r"\w+", query.lower()))
    t = set(re.findall(r"\w+", text.lower()))
    return len(q & t) >= 2

class TemporalGraphRAG:
    def __init__(self):
        self.con = _connect()

    def ingest(self, docs: List[Dict[str, Any]]) -> int:
        count = 0
        for d in docs:
            ts = d.get("timestamp") or time.strftime("%Y-%m-%d %H:%M:%S")
            self.con.execute("INSERT OR REPLACE INTO documents VALUES (?, ?, ?, ?)", (d["doc_id"], d.get("domain","default"), d["text"], ts))
            # naive edge extraction: link consecutive sentences
            sents = re.split(r"[.!?]\s+", d["text"])
            for i in range(len(sents)-1):
                self.con.execute("INSERT INTO edges VALUES (?, ?, ?, ?)", (f"{d['doc_id']}#s{i}", f"{d['doc_id']}#s{i+1}", "next", ts))
            count += 1
        return count

    def query(self, query: str, time_from: Optional[str], time_to: Optional[str], k: int=5, domain: Optional[str]="default") -> List[Dict[str, Any]]:
        q = "SELECT doc_id, text, ts FROM documents WHERE domain = ?"
        params = [domain]
        if time_from:
            q += " AND ts >= ?"
            params.append(time_from)
        if time_to:
            q += " AND ts <= ?"
            params.append(time_to)
        rows = self.con.execute(q, params).fetchall()
        texts = [r[1] for r in rows]
        order = _simple_bm25(query, texts)[: max(k*2, 10)]
        results = []
        for idx in order:
            doc_id, text, ts = rows[idx]
            if _entailment_gate(query, text):
                results.append({"doc_id": doc_id, "text": text[:500], "ts": str(ts)})
            if len(results) >= k:
                break
        return results

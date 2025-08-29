
from __future__ import annotations
import os
try:
    import psycopg2, psycopg2.extras  # type: ignore
except Exception:  # keep import optional
    psycopg2 = None

def available():
    return psycopg2 is not None and os.environ.get("PGVECTOR_URL")

def create_tables(conn):
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS documents(
            id SERIAL PRIMARY KEY,
            path TEXT,
            content TEXT
        );
        """)
        conn.commit()

def insert_doc(conn, path: str, content: str):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO documents(path, content) VALUES (%s,%s)", (path, content))
    conn.commit()

def search(conn, q: str, top_k: int = 5):
    # Minimal LIKE search as placeholder (vector search requires ivfflat & embeddings setup).
    with conn.cursor() as cur:
        cur.execute("SELECT path, content FROM documents WHERE content ILIKE %s LIMIT %s", (f"%{q}%", top_k))
        return [{"path": p, "content": c} for (p,c) in cur.fetchall()]

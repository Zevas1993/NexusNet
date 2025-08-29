
from __future__ import annotations

def available() -> bool:
    try:
        import psycopg2  # noqa: F401
        return True
    except Exception:
        return False

def _conn():
    import os
    import psycopg2  # type: ignore
    dsn=os.environ.get("PG_DSN") or None
    if not dsn:
        host=os.environ.get("PGHOST","localhost")
        port=int(os.environ.get("PGPORT","5432"))
        db=os.environ.get("PGDATABASE","nexusnet")
        user=os.environ.get("PGUSER","postgres")
        password=os.environ.get("PGPASSWORD","")
        dsn=f"host={host} port={port} dbname={db} user={user} password={password}"
    return psycopg2.connect(dsn)

def _has_pgvector(cur) -> bool:
    try:
        cur.execute("select exists (select 1 from pg_type where typname='vector')")
        return bool(cur.fetchone()[0])
    except Exception:
        return False

def ensure_schema(dim: int = 384) -> bool:
    try:
        import psycopg2  # noqa
        conn=_conn(); cur=conn.cursor()
        has_vec=_has_pgvector(cur)
        if has_vec:
            cur.execute(f"""            create table if not exists rag_docs (
              doc_id text primary key,
              text   text,
              meta   jsonb,
              embedding vector({dim})
            );
            """)
            cur.execute("create index if not exists rag_docs_emb_idx on rag_docs using ivfflat (embedding vector_cosine_ops);")
        else:
            cur.execute("""            create table if not exists rag_docs (
              doc_id text primary key,
              text   text,
              meta   jsonb
            );
            """)
        conn.commit(); cur.close(); conn.close()
        return True
    except Exception:
        return False

def _embed(text: str):
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        v = model.encode([text], normalize_embeddings=True)[0]
        return v.tolist()
    except Exception:
        return None

def upsert(doc_id: str, text: str, meta: dict):
    try:
        import psycopg2, json  # noqa
        conn=_conn(); cur=conn.cursor()
        has_vec=_has_pgvector(cur)
        if has_vec:
            emb=_embed(text)
            if emb is None:
                # store without embedding if ST not available
                cur.execute("insert into rag_docs (doc_id, text, meta) values (%s,%s,%s) on conflict (doc_id) do update set text=EXCLUDED.text, meta=EXCLUDED.meta", (doc_id, text, json.dumps(meta)))
            else:
                cur.execute("insert into rag_docs (doc_id, text, meta, embedding) values (%s,%s,%s,%s) on conflict (doc_id) do update set text=EXCLUDED.text, meta=EXCLUDED.meta, embedding=EXCLUDED.embedding", (doc_id, text, json.dumps(meta), emb))
        else:
            cur.execute("insert into rag_docs (doc_id, text, meta) values (%s,%s,%s) on conflict (doc_id) do update set text=EXCLUDED.text, meta=EXCLUDED.meta", (doc_id, text, json.dumps(meta)))
        conn.commit(); cur.close(); conn.close()
        return True
    except Exception:
        return False

def search(query: str, top_k: int = 5):
    try:
        import psycopg2  # noqa
        conn=_conn(); cur=conn.cursor()
        has_vec=_has_pgvector(cur)
        if has_vec:
            q_emb=_embed(query)
            if q_emb is None:
                # fall back to LIKE if embedding model missing
                cur.execute("select doc_id, left(text, 200) as snippet from rag_docs where text ilike %s limit %s", (f"%{query}%", top_k))
                rows=cur.fetchall()
                cur.close(); conn.close()
                return [{"source": f"pg:{doc_id}", "text": snip, "score": 0.1} for doc_id, snip in rows]
            # cosine distance: smaller is better; invert to score
            cur.execute("select doc_id, left(text,200) as snippet, 1 - (embedding <=> %s) as score from rag_docs order by embedding <=> %s asc limit %s", (q_emb, q_emb, top_k))
            rows=cur.fetchall(); cur.close(); conn.close()
            return [{"source": f"pg:{doc_id}", "text": snip, "score": float(score)} for doc_id, snip, score in rows]
        else:
            cur.execute("select doc_id, left(text, 200) as snippet from rag_docs where text ilike %s limit %s", (f"%{query}%", top_k))
            rows=cur.fetchall(); cur.close(); conn.close()
            return [{"source": f"pg:{doc_id}", "text": snip, "score": 0.1} for doc_id, snip in rows]
    except Exception:
        return []

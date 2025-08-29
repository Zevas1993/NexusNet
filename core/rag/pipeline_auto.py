
from __future__ import annotations
import os
from typing import List, Dict

def get_context(query: str) -> List[Dict]:
    backend = os.environ.get("RAG_BACKEND","lite")
    if backend == "pgvector":
        try:
            from core.rag.pgvector_client import available, search
            if available():
                import psycopg2  # type: ignore
                conn = psycopg2.connect(os.environ["PGVECTOR_URL"])
                rows = search(conn, query, top_k=int(os.environ.get("RAG_TOPK","5")))
                conn.close()
                return [{"text": r["content"], "source": r["path"]} for r in rows]
        except Exception:
            pass
    # fallback
    from core.rag.pipeline_lite import get_context as lite
    return lite(query)

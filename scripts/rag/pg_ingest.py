
#!/usr/bin/env python3
from __future__ import annotations
import os, glob
from pathlib import Path

def main():
    url = os.environ.get("PGVECTOR_URL")
    if not url:
        print("Set PGVECTOR_URL to a Postgres connection string, e.g. postgres://user:pass@127.0.0.1:5432/nexusnet")
        return
    try:
        import psycopg2  # type: ignore
    except Exception as e:
        print("psycopg2 not installed. Use: pip install psycopg2-binary")
        return
    from core.rag.pgvector_client import create_tables, insert_doc

    conn = psycopg2.connect(url)
    create_tables(conn)
    corpus = os.environ.get("CORPUS_DIR","data/corpus/sample")
    for p in glob.glob(str(Path(corpus)/"**/*"), recursive=True):
        if os.path.isfile(p) and os.path.getsize(p) < 2_000_000:
            try:
                txt = Path(p).read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            insert_doc(conn, p, txt)
    conn.close()
    print("Ingest complete.")
if __name__ == "__main__":
    main()

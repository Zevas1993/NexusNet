import os

from __future__ import annotations
from typing import List, Dict, Any
from .tkg import TKG

class TemporalRetriever:
    def __init__(self, db_path: str = "runtime/temporal/tkg.sqlite"):
        self.tkg = TKG(db_path)

    def ingest(self, texts: List[str], extractor):
        items = 0
        for t in texts:
            facts = extractor.extract_atomic(t)
            items += self.tkg.upsert(facts)
        return items

    def retrieve_as_of(self, query: str, date_iso: str, limit: int = 20) -> List[Dict[str,Any]]:
        rows = self.tkg.as_of(query, date_iso)[:limit]
        return [{
            "subject": r[0], "predicate": r[1], "object": r[2],
            "start": r[3], "end": r[4], "source": r[5], "confidence": r[6]
        } for r in rows]


# Optional Neo4j backend (enterprise)
try:
    from .neo4j_driver import Neo4jTKG
except Exception:
    Neo4jTKG = None

def retrieve_as_of_neo4j(query: str, date: str, limit: int = 20):
    uri = os.environ.get("NEO4J_URI")
    user = os.environ.get("NEO4J_USER")
    pwd  = os.environ.get("NEO4J_PASS")
    if not (uri and user and pwd) or Neo4jTKG is None:
        return []
    try:
        client = Neo4jTKG(uri, user, pwd)
        rows = client.as_of(query, date, limit=limit)
        client.close()
        return rows
    except Exception:
        return []

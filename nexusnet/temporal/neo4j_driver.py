
from __future__ import annotations
try:
    from neo4j import GraphDatabase   # type: ignore
except Exception:
    GraphDatabase = None

class Neo4jTKG:
    def __init__(self, uri: str, user: str, password: str):
        if GraphDatabase is None:
            raise RuntimeError("neo4j driver not available")
        self._driver = GraphDatabase.driver(uri, auth=(user, password))
    def close(self):
        self._driver.close()
    def as_of(self, query: str, date: str, limit: int = 20):
        cypher = """        MATCH (s)-[r]->(o)
        WHERE r.start <= date($d) AND (r.end IS NULL OR r.end >= date($d))
          AND (toLower(s.name) CONTAINS toLower($q) OR toLower(o.name) CONTAINS toLower($q))
        RETURN s.name AS subject, type(r) AS predicate, o.name AS object, r.start AS start, r.end AS end, r.source AS source, r.confidence AS confidence
        LIMIT $limit
        """
        with self._driver.session() as sess:
            res = sess.run(cypher, q=query, d=date, limit=limit)
            return [dict(r) for r in res]

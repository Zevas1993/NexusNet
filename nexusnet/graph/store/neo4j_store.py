from __future__ import annotations

from ...schemas import GraphHit
from .base_store import GraphStore


class Neo4jGraphStore(GraphStore):
    provider_name = "neo4j"
    status_label = "IMPLEMENTATION BRANCH"

    def ingest(self, *, source: str, nodes, edges, metadata: dict | None = None) -> dict:
        return {
            "provider": self.provider_name,
            "available": False,
            "status_label": self.status_label,
            "notes": ["Optional external provider path is not enabled in the default local-first install."],
        }

    def query(self, *, query: str, top_k: int = 5, plane_tags: list[str] | None = None) -> list[GraphHit]:
        return []

    def status(self) -> dict:
        return {
            "provider_name": self.provider_name,
            "status_label": self.status_label,
            "available": False,
            "notes": ["Neo4j remains an optional provider path behind future feature flags."],
        }

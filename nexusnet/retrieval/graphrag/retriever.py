from __future__ import annotations

from ...graph.store import GraphStore


class GraphRAGRetriever:
    def __init__(self, store: GraphStore):
        self.store = store

    def query(self, *, query: str, top_k: int = 5, plane_tags: list[str] | None = None) -> list[dict]:
        return [hit.model_dump(mode="json") for hit in self.store.query(query=query, top_k=top_k, plane_tags=plane_tags)]

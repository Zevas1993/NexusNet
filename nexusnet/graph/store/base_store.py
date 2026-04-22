from __future__ import annotations

from abc import ABC, abstractmethod

from ...schemas import GraphEdgeRecord, GraphHit, GraphNodeRecord


class GraphStore(ABC):
    provider_name = "graph-store"
    status_label = "STRONG ACCEPTED DIRECTION"

    @abstractmethod
    def ingest(self, *, source: str, nodes: list[GraphNodeRecord], edges: list[GraphEdgeRecord], metadata: dict | None = None) -> dict:
        raise NotImplementedError

    @abstractmethod
    def query(self, *, query: str, top_k: int = 5, plane_tags: list[str] | None = None) -> list[GraphHit]:
        raise NotImplementedError

    @abstractmethod
    def status(self) -> dict:
        raise NotImplementedError

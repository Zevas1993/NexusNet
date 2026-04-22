from __future__ import annotations

import json
import re
from pathlib import Path

from ...schemas import GraphEdgeRecord, GraphHit, GraphNodeRecord, GraphProvenanceRecord
from .base_store import GraphStore


def _normalize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9_]+", text.lower())


class LocalGraphStore(GraphStore):
    provider_name = "local-file"
    status_label = "IMPLEMENTATION BRANCH"

    def __init__(self, artifacts_dir: Path):
        self.path = artifacts_dir / "graph" / "local_store.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text(json.dumps({"nodes": [], "edges": [], "sources": []}, indent=2), encoding="utf-8")

    def ingest(self, *, source: str, nodes: list[GraphNodeRecord], edges: list[GraphEdgeRecord], metadata: dict | None = None) -> dict:
        payload = self._load()
        existing_nodes = {node["node_id"]: node for node in payload["nodes"]}
        for node in nodes:
            existing_nodes[node.node_id] = node.model_dump(mode="json")
        payload["nodes"] = list(existing_nodes.values())

        existing_edges = {edge["edge_id"]: edge for edge in payload["edges"]}
        for edge in edges:
            existing_edges[edge.edge_id] = edge.model_dump(mode="json")
        payload["edges"] = list(existing_edges.values())

        payload["sources"].append({"source": source, "metadata": metadata or {}, "node_count": len(nodes), "edge_count": len(edges)})
        self._save(payload)
        return {"provider": self.provider_name, "source": source, "nodes_added": len(nodes), "edges_added": len(edges)}

    def query(self, *, query: str, top_k: int = 5, plane_tags: list[str] | None = None) -> list[GraphHit]:
        query_terms = _normalize(query)
        if not query_terms:
            return []
        payload = self._load()
        hits: list[GraphHit] = []
        for node in payload["nodes"]:
            if plane_tags and not set(plane_tags).intersection(node.get("plane_tags", [])):
                continue
            haystack = _normalize(f"{node.get('label', '')} {node.get('content', '')}")
            overlap = sum(haystack.count(term) for term in query_terms)
            if overlap <= 0:
                continue
            provenance = GraphProvenanceRecord.model_validate(node.get("provenance", {"source": "graph", "plane_tags": []}))
            hits.append(
                GraphHit(
                    node_id=node["node_id"],
                    label=node.get("label", node["node_id"]),
                    content=node.get("content", ""),
                    score=float(overlap) / max(len(query_terms), 1),
                    plane_tags=node.get("plane_tags", []),
                    provenance=provenance,
                )
            )
        hits.sort(key=lambda hit: hit.score, reverse=True)
        return hits[:top_k]

    def status(self) -> dict:
        payload = self._load()
        return {
            "provider_name": self.provider_name,
            "status_label": self.status_label,
            "path": str(self.path),
            "node_count": len(payload["nodes"]),
            "edge_count": len(payload["edges"]),
            "source_count": len(payload["sources"]),
        }

    def _load(self) -> dict:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, payload: dict) -> None:
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

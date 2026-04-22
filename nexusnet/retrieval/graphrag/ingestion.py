from __future__ import annotations

import re

from ...graph.store import GraphStore
from ...memory.graph_bridge import MemoryGraphBridge
from ...schemas import GraphEdgeRecord, GraphIngestRequest, GraphNodeRecord, new_id
from .provenance import graph_provenance


def _sentences(text: str) -> list[str]:
    parts = [part.strip() for part in re.split(r"[.!?\n]+", text) if part.strip()]
    return parts or [text.strip()]


class GraphRAGIngestionService:
    def __init__(self, *, store: GraphStore, graph_bridge: MemoryGraphBridge):
        self.store = store
        self.graph_bridge = graph_bridge

    def ingest(self, request: GraphIngestRequest) -> dict:
        plane_tags = self.graph_bridge.plane_tags(request.plane_hint)
        sentences = _sentences(request.text)
        nodes: list[GraphNodeRecord] = []
        edges: list[GraphEdgeRecord] = []
        previous_node_id: str | None = None
        for index, sentence in enumerate(sentences):
            node_id = new_id("gnode")
            nodes.append(
                GraphNodeRecord(
                    node_id=node_id,
                    label=f"{request.source}#{index}",
                    node_type="fact",
                    content=sentence,
                    plane_tags=plane_tags,
                    provenance=graph_provenance(
                        source=request.source,
                        session_id=request.session_id,
                        source_doc_id=request.metadata.get("doc_id"),
                        source_trace_id=request.metadata.get("trace_id"),
                        plane_tags=plane_tags,
                    ).model_dump(mode="json"),
                )
            )
            if previous_node_id is not None:
                edges.append(
                    GraphEdgeRecord(
                        source_node_id=previous_node_id,
                        target_node_id=node_id,
                        relation="sequence",
                        plane_tags=plane_tags,
                        provenance={"source": request.source},
                    )
                )
            previous_node_id = node_id
        return self.store.ingest(source=request.source, nodes=nodes, edges=edges, metadata=request.metadata)

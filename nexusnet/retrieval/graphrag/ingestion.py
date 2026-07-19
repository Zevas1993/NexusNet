from __future__ import annotations

import hashlib
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
        genesis_admission = _record_genesis_graph_ingest_admission(self, request)
        if genesis_admission and genesis_admission.get("memory_write_allowed") is not True:
            return {
                "provider": getattr(self.store, "provider_name", "graph-store"),
                "source": request.source,
                "nodes_added": 0,
                "edges_added": 0,
                "ingest_blocked": True,
                "block_reason": "genesis_memory_admission_blocked",
                "genesis_memory_admission": genesis_admission,
                "raw_content_included": False,
            }
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
        result = self.store.ingest(source=request.source, nodes=nodes, edges=edges, metadata=request.metadata)
        result["ingest_blocked"] = False
        if genesis_admission:
            result["genesis_memory_admission"] = genesis_admission
            result["raw_content_included"] = False
        return result

    def activate_genesis_memory(
        self,
        *,
        memory_id: str,
        memory_ref: str,
        session_ref_digest: str,
        source_ref: str,
        content: str,
        content_ref: str,
    ) -> dict:
        graph_source = f"genesis-memory::{memory_id}"
        plane_tags = self.graph_bridge.plane_tags("semantic")
        node_id = f"gnode-{hashlib.sha256(memory_id.encode('utf-8')).hexdigest()[:20]}"
        node = GraphNodeRecord(
            node_id=node_id,
            label=f"{source_ref}#canon-memory",
            node_type="fact",
            content=content,
            plane_tags=plane_tags,
            provenance=graph_provenance(
                source=graph_source,
                session_id=session_ref_digest,
                source_doc_id=memory_id,
                source_trace_id=memory_ref,
                plane_tags=plane_tags,
            ).model_dump(mode="json"),
        )
        result = self.store.ingest(
            source=graph_source,
            nodes=[node],
            edges=[],
            metadata={
                "genesis_memory_id": memory_id,
                "memory_ref": memory_ref,
                "source_ref": source_ref,
                "content_ref": content_ref,
                "genesis_truth_state": "active",
            },
        )
        return {
            "surface_id": "genesis-memory-live-graphrag-activation",
            "status": "active",
            "memory_id": memory_id,
            "graph_source": graph_source,
            "node_ids": [node_id],
            "nodes_added": int(result.get("nodes_added") or 0),
            "edges_added": int(result.get("edges_added") or 0),
            "raw_content_included": False,
        }

    def deactivate_genesis_memory(self, *, memory_id: str, reason_ref: str) -> dict:
        graph_source = f"genesis-memory::{memory_id}"
        deactivate_source = getattr(self.store, "deactivate_source", None)
        if not callable(deactivate_source):
            raise RuntimeError("configured graph store cannot deactivate governed memory sources")
        result = deactivate_source(graph_source, reason_ref=reason_ref)
        return {
            "surface_id": "genesis-memory-live-graphrag-deactivation",
            "status": "revoked",
            "memory_id": memory_id,
            "graph_source": graph_source,
            "nodes_removed": int(result.get("nodes_removed") or 0),
            "edges_removed": int(result.get("edges_removed") or 0),
            "reason_ref": reason_ref,
            "raw_content_included": False,
        }


def _record_genesis_graph_ingest_admission(
    service: GraphRAGIngestionService,
    request: GraphIngestRequest,
) -> dict:
    admission = getattr(service, "genesis_memory_admission", None)
    record_manual_ingress = getattr(admission, "record_manual_ingress", None)
    if not callable(record_manual_ingress):
        return {}
    return record_manual_ingress(
        session_id=request.session_id,
        ingress_route="graph-node-ingest",
        content=request.text,
        metadata=_graph_ingest_admission_metadata(request),
    )


def _graph_ingest_admission_metadata(request: GraphIngestRequest) -> dict:
    metadata = dict(request.metadata or {})
    return {
        "source_kind": metadata.get("source_kind") or "graph-node-ingest",
        "privacy_class": metadata.get("privacy_class") or "unspecified",
        "consent_status": metadata.get("consent_status") or "not-declared",
        "rights_license_status": metadata.get("rights_license_status")
        or metadata.get("license_status")
        or "not-declared",
    }

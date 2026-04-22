from __future__ import annotations

from ...schemas import GraphProvenanceRecord


def graph_provenance(*, source: str, session_id: str | None, source_doc_id: str | None, source_trace_id: str | None, plane_tags: list[str], lineage: str = "live-derived") -> GraphProvenanceRecord:
    return GraphProvenanceRecord(
        source=source,
        session_id=session_id,
        source_doc_id=source_doc_id,
        source_trace_id=source_trace_id,
        plane_tags=plane_tags,
        lineage=lineage,
        validity={"mode": "latest_valid"},
    )

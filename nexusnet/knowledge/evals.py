from __future__ import annotations

from typing import Any


def compiled_vs_raw_eval(*, artifact: dict[str, Any] | None, raw_source_count: int) -> dict[str, Any]:
    field_count = 0
    if artifact:
        content = artifact.get("content") or {}
        field_count += 1 if content.get("summary") else 0
        field_count += len(content.get("facts") or [])
        field_count += len(content.get("relationships") or [])
        field_count += len(content.get("recommended_actions") or [])
    citation_count = len((artifact or {}).get("field_citations") or {})
    estimated_raw_context_units = max(raw_source_count, 1)
    estimated_compiled_units = max(field_count, 1)
    return {
        "eval_id": "knowledge_artifact_compiled_vs_raw.v0.1",
        "raw_source_count": raw_source_count,
        "compiled_field_count": field_count,
        "citation_field_count": citation_count,
        "citation_coverage": 1.0 if artifact and artifact.get("validation", {}).get("valid") else 0.0,
        "estimated_context_reduction": max(0.0, 1.0 - (estimated_compiled_units / (estimated_raw_context_units * 8))),
    }

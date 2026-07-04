from __future__ import annotations

from typing import Any

from .provenance import source_digest


def freshness_report_for(artifact: dict[str, Any] | None, sources: list[dict[str, Any]]) -> dict[str, Any]:
    if artifact is None:
        return {
            "freshness_state": "missing",
            "changed_source_refs": [],
            "missing_source_refs": [],
        }
    previous = {item.get("source_ref"): item.get("digest") for item in artifact.get("source_digests") or []}
    current = {source.get("source_ref"): source_digest(source) for source in sources}
    changed = sorted(source_ref for source_ref, digest in current.items() if previous.get(source_ref) and previous[source_ref] != digest)
    missing = sorted(source_ref for source_ref in previous if source_ref not in current)
    return {
        "freshness_state": "stale" if changed or missing else "current",
        "changed_source_refs": changed,
        "missing_source_refs": missing,
        "previous_source_count": len(previous),
        "current_source_count": len(current),
    }

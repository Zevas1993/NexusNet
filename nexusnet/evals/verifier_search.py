from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow


class VerifierSearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    search_id: str
    objective: str
    scorer_ref: str
    candidates: list[dict[str, Any]] = Field(default_factory=list)
    constraints: dict[str, float] = Field(default_factory=dict)
    evidence_refs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class VerifierSearchRegistry:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.records_dir = self.artifacts_dir / "evals" / "verifier-search" if self.artifacts_dir else None
        if self.records_dir is not None:
            self.records_dir.mkdir(parents=True, exist_ok=True)
        self._memory_records: list[dict[str, Any]] = []

    def record_search(self, request: VerifierSearchRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, VerifierSearchRequest) else VerifierSearchRequest.model_validate(request)
        scored = [_score_candidate(candidate, normalized.constraints) for candidate in normalized.candidates]
        allowed = [candidate for candidate in scored if not candidate["blockers"]]
        blocked = [candidate for candidate in scored if candidate["blockers"]]
        selected = sorted(allowed, key=lambda item: item["multi_objective_score"], reverse=True)[0] if allowed else None
        record = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "verifier-search",
            "search_id": normalized.search_id,
            "objective": normalized.objective,
            "scorer_ref": normalized.scorer_ref,
            "status": "candidate-selected" if selected else "blocked",
            "runtime_state": "live-bound" if selected else "degraded",
            "created_at": utcnow().isoformat(),
            "selected": selected,
            "candidate_count": len(scored),
            "candidates": scored,
            "blocked_candidates": blocked,
            "constraints": normalized.constraints,
            "evidence_refs": normalized.evidence_refs,
            "promotion_boundary": "verifier-search-results-remain-shadow-until-human-review",
            "metadata": normalized.metadata,
            "operator_actions": _operator_actions(),
        }
        self._persist(record)
        return record

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        records = self._list_records(limit=limit)
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "verifier-search",
            "authority": "NexusBrain",
            "runtime_state": "degraded"
            if any(record.get("status") == "blocked" for record in records)
            else ("live-bound" if records else "static-canon"),
            "search_count": len(records),
            "latest_search": records[0] if records else None,
            "searches": records,
            "operator_actions": _operator_actions(),
        }

    def _persist(self, record: dict[str, Any]) -> None:
        self._memory_records.insert(0, record)
        self._memory_records = self._memory_records[:50]
        if self.records_dir is not None:
            path = self.records_dir / f"{_safe_id(record['search_id'])}.json"
            record["artifact_path"] = str(path)
            path.write_text(json.dumps(record, indent=2), encoding="utf-8")

    def _list_records(self, *, limit: int) -> list[dict[str, Any]]:
        records = list(self._memory_records)
        seen = {record.get("search_id") for record in records}
        if self.records_dir is not None:
            for path in self.records_dir.glob("*.json"):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if payload.get("search_id") not in seen:
                    records.append(payload)
        records.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return records[:limit]


def _score_candidate(candidate: dict[str, Any], constraints: dict[str, float]) -> dict[str, Any]:
    scores = {str(key): float(value) for key, value in (candidate.get("scores") or {}).items()}
    blockers = []
    if scores.get("source_faithfulness", 0.0) < constraints.get("minimum_source_faithfulness", 0.0):
        blockers.append("source_faithfulness_below_constraint")
    if scores.get("safety", 1.0) < constraints.get("minimum_safety", 0.0):
        blockers.append("safety_below_constraint")
    multi_objective_score = round(
        (0.35 * scores.get("quality", 0.0))
        + (0.25 * scores.get("source_faithfulness", 0.0))
        + (0.25 * scores.get("safety", 0.0))
        + (0.15 * scores.get("latency", 0.0)),
        4,
    )
    return {**candidate, "scores": scores, "multi_objective_score": multi_objective_score, "blockers": blockers}


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/verifier-search"},
        "record_search": {"method": "POST", "endpoint": "/ops/brain/verifier-search/runs"},
    }


def _safe_id(value: str) -> str:
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in value)[:160] or "verifier_search"

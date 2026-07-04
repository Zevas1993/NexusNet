from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow


RetrievalMode = Literal["lexical", "semantic", "graph", "temporal", "rerank"]
SourceClass = Literal[
    "primary_source",
    "secondary_source",
    "repo",
    "paper",
    "video_transcript",
    "memory",
    "operator_supplied",
]


class RetrievalPlanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan_id: str
    user_goal: str
    source_classes: list[SourceClass] = Field(default_factory=list)
    query_decomposition: list[str] = Field(default_factory=list)
    retrieval_modes: list[RetrievalMode] = Field(default_factory=list)
    evidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    cost_budget_ms: int = Field(default=1500, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrievalPlanner:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.plans_dir = self.artifacts_dir / "retrieval" / "planner" if self.artifacts_dir else None
        if self.plans_dir is not None:
            self.plans_dir.mkdir(parents=True, exist_ok=True)
        self._memory_plans: list[dict[str, Any]] = []

    def plan(self, request: RetrievalPlanRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, RetrievalPlanRequest) else RetrievalPlanRequest.model_validate(request)
        findings = _planner_findings(normalized)
        blocked = bool(findings)
        payload = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "retrieval-planner",
            "plan_id": normalized.plan_id,
            "user_goal": normalized.user_goal,
            "status": "blocked" if blocked else "planned",
            "runtime_state": "degraded" if blocked else "live-bound",
            "created_at": utcnow().isoformat(),
            "source_classes": normalized.source_classes,
            "query_decomposition": normalized.query_decomposition,
            "retrieval_modes": normalized.retrieval_modes or ["lexical", "semantic", "rerank"],
            "evidence_threshold": normalized.evidence_threshold,
            "cost_budget_ms": normalized.cost_budget_ms,
            "stop_condition": "enough_verified_sources_or_explicit_unknown",
            "claim_ledger_contract": {
                "requires_source_status": True,
                "requires_contradiction_refs": True,
                "unsupported_claim_state": "explicit_unknown",
            },
            "critic_loop": [
                "grade_document_relevance",
                "rewrite_query_when_evidence_misses_goal",
                "preserve_contradictions",
                "abstain_when_threshold_not_met",
            ],
            "poisoning_controls": ["private_source_block", "stale_source_warning", "memory_quality_downgrade"],
            "planner_findings": findings,
            "required_controls": _required_controls(),
            "metadata": normalized.metadata,
            "operator_actions": _operator_actions(),
        }
        self._persist(payload)
        return payload

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        plans = self._list_plans(limit=limit)
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "retrieval-planner",
            "authority": "NexusBrain",
            "runtime_state": "degraded"
            if any(plan.get("status") == "blocked" for plan in plans)
            else ("live-bound" if plans else "static-canon"),
            "plan_count": len(plans),
            "blocked_count": sum(1 for plan in plans if plan.get("status") == "blocked"),
            "latest_plan": plans[0] if plans else None,
            "plans": plans,
            "required_controls": _required_controls(),
            "operator_actions": _operator_actions(),
        }

    def _persist(self, payload: dict[str, Any]) -> None:
        self._memory_plans.insert(0, payload)
        self._memory_plans = self._memory_plans[:50]
        if self.plans_dir is not None:
            path = self.plans_dir / f"{_safe_id(payload['plan_id'])}.json"
            payload["artifact_path"] = str(path)
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _list_plans(self, *, limit: int) -> list[dict[str, Any]]:
        plans = list(self._memory_plans)
        seen = {plan.get("plan_id") for plan in plans}
        if self.plans_dir is not None:
            for path in self.plans_dir.glob("*.json"):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if payload.get("plan_id") not in seen:
                    plans.append(payload)
        plans.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return plans[:limit]


def _planner_findings(request: RetrievalPlanRequest) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if not request.query_decomposition:
        findings.append(
            {
                "rule_id": "retrieval_plan_requires_decomposition",
                "severity": "hard_fail",
                "message": "Complex retrieval requires query decomposition.",
            }
        )
    if request.evidence_threshold < 0.65:
        findings.append(
            {
                "rule_id": "retrieval_plan_requires_evidence_threshold",
                "severity": "hard_fail",
                "message": "Evidence threshold must be at least 0.65 for source-backed answers.",
            }
        )
    if not request.source_classes:
        findings.append(
            {
                "rule_id": "retrieval_plan_requires_source_classes",
                "severity": "hard_fail",
                "message": "Retrieval plans must name source classes.",
            }
        )
    return findings


def _required_controls() -> list[str]:
    return [
        "retrieval_plan_schema",
        "hybrid_retrieval_modes",
        "claim_ledger",
        "critic_loop",
        "poisoning_controls",
        "cost_latency_budget",
    ]


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/retrieval/planner"},
        "plan": {"method": "POST", "endpoint": "/ops/brain/retrieval/plans"},
        "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/retrieval-planner"},
    }


def _safe_id(value: str) -> str:
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in value)[:160] or "retrieval_plan"

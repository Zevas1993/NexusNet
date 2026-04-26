from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from nexus.schemas import new_id


class EBTScoreRequest(BaseModel):
    capsule_id: str
    confidence: float = Field(ge=0.0, le=1.0)
    risk: float = Field(ge=0.0, le=1.0)
    memory_influence: str
    critique_result: str
    fallback_reason: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class EBTScoringContract:
    """Traceable EBT routing contract; weights remain unresolved canon."""

    required_fields = [
        "confidence",
        "risk",
        "capsule_choice",
        "memory_influence",
        "fallback_reason",
        "critique_result",
    ]

    def contract(self) -> dict[str, Any]:
        return {
            "status": "pluggable_contract",
            "formula_status": "unresolved",
            "required_fields": list(self.required_fields),
            "route_decisions": ["use_capsule", "fallback", "hold_for_critique"],
            "notes": [
                "Every route records confidence, risk, capsule choice, memory influence, fallback reason, and critique result.",
                "Formula weights stay unresolved until trace-first evals prove a stable policy.",
            ],
        }

    def score(self, request: EBTScoreRequest) -> dict[str, Any]:
        if request.fallback_reason:
            route_decision = "fallback"
        elif request.risk >= 0.65 or request.critique_result in {"warning", "error"}:
            route_decision = "hold_for_critique"
        else:
            route_decision = "use_capsule"
        return {
            "score_id": new_id("ebt"),
            "status": "diagnostic_only",
            "confidence": request.confidence,
            "risk": request.risk,
            "capsule_choice": request.capsule_id,
            "memory_influence": request.memory_influence,
            "fallback_reason": request.fallback_reason,
            "critique_result": request.critique_result,
            "route_decision": route_decision,
            "formula_status": "unresolved",
            "metadata": dict(request.metadata),
        }

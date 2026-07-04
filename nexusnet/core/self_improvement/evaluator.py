from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .event_schema import ImprovementEvent
from .provenance import ProvenanceRecord
from .triage import TriageDecision


CheckStatus = Literal["pass", "warn", "fail"]
EvaluationStatus = Literal["pass", "needs_review", "blocked"]


class EvaluationCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    check_id: str
    status: CheckStatus
    detail: str
    evidence_refs: list[str] = Field(default_factory=list)


class EvaluationReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    status: EvaluationStatus
    checks: list[EvaluationCheck]
    blockers: list[str] = Field(default_factory=list)


class ImprovementEvaluator:
    def evaluate(
        self,
        event: ImprovementEvent,
        decision: TriageDecision,
        provenance: ProvenanceRecord,
    ) -> EvaluationReport:
        checks: list[EvaluationCheck] = []
        blockers: list[str] = []

        source_status: CheckStatus = "pass"
        if provenance.unsupported_source_ids:
            source_status = "fail"
            blockers.append("unsupported-sources")
        elif provenance.source_count == 0:
            source_status = "warn"
        checks.append(
            EvaluationCheck(
                check_id="source-coverage",
                status=source_status,
                detail="Context sources must carry source ids and provenance before promotion.",
                evidence_refs=provenance.evidence_refs,
            )
        )

        safety_status: CheckStatus = "pass"
        if event.safety.contains_secrets:
            safety_status = "fail"
            blockers.append("contains-secrets")
        elif event.safety.contains_private_data:
            safety_status = "warn"
        checks.append(
            EvaluationCheck(
                check_id="safety-privacy",
                status=safety_status,
                detail="Secrets are blocked; private data requires review and redaction.",
            )
        )

        checks.append(
            EvaluationCheck(
                check_id="direct-training-block",
                status="pass" if "direct_model_training" not in decision.safe_optimization_modes else "fail",
                detail=decision.model_update_boundary,
            )
        )
        if "direct_model_training" in decision.safe_optimization_modes:
            blockers.append("direct-model-training-requested")

        checks.append(
            EvaluationCheck(
                check_id="human-review",
                status="warn" if decision.review_required else "pass",
                detail="Review is required before memory, prompt, routing, or training-candidate promotion.",
            )
        )
        checks.append(
            EvaluationCheck(
                check_id="eval-generation",
                status="pass" if "create_eval_case" in decision.labels else "warn",
                detail="Failures and low-confidence events should become held-out eval material before behavior changes.",
            )
        )

        if blockers:
            status: EvaluationStatus = "blocked"
        elif any(check.status == "warn" for check in checks):
            status = "needs_review"
        else:
            status = "pass"
        return EvaluationReport(event_id=event.event_id, status=status, checks=checks, blockers=blockers)

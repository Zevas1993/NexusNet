from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .evaluator import EvaluationReport
from .improvement_queue import ImprovementQueueItem


GateStatus = Literal["pass", "blocked"]
REQUIRED_CHECK_IDS = ["project-continuity", "factuality", "tool-use", "safety-privacy"]


class RegressionGateCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    check_id: str
    status: Literal["pass", "fail", "not_run"]
    evidence_ref: str = ""


class RegressionGateReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    queue_id: str
    event_id: str
    status: GateStatus
    can_promote: bool
    required_check_ids: list[str] = Field(default_factory=lambda: list(REQUIRED_CHECK_IDS))
    checks: list[RegressionGateCheck] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)


class RegressionGate:
    def evaluate(
        self,
        item: ImprovementQueueItem,
        evaluation: EvaluationReport,
        *,
        test_results: list[dict[str, str]] | None = None,
        operator_approved: bool = False,
    ) -> RegressionGateReport:
        result_by_id = {result.get("check_id", ""): result for result in (test_results or [])}
        checks: list[RegressionGateCheck] = []
        blockers: list[str] = []

        for check_id in REQUIRED_CHECK_IDS:
            raw = result_by_id.get(check_id)
            if raw is None:
                checks.append(RegressionGateCheck(check_id=check_id, status="not_run"))
                blockers.append(f"{check_id}-not-run")
                continue
            status = "pass" if raw.get("status") == "pass" else "fail"
            checks.append(
                RegressionGateCheck(
                    check_id=check_id,
                    status=status,
                    evidence_ref=raw.get("evidence_ref", ""),
                )
            )
            if status != "pass":
                blockers.append(f"{check_id}-failed")

        if evaluation.status == "blocked":
            blockers.extend(evaluation.blockers or ["evaluation-blocked"])
        if item.decision.review_required and not operator_approved:
            blockers.append("operator-approval-required")
        if item.status not in {"proposed", "validated", "approved"}:
            blockers.append(f"queue-status-{item.status}-not-promotable")

        blockers = list(dict.fromkeys(blockers))
        return RegressionGateReport(
            queue_id=item.queue_id,
            event_id=item.event.event_id,
            status="blocked" if blockers else "pass",
            can_promote=not blockers,
            checks=checks,
            blockers=blockers,
        )

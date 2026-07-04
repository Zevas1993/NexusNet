"""PB-2026-06-03-099 - Focal Coding Model Lane (Mellum2-style), shadow coding-route evaluator.

Builds on the existing `EdgeModelCertificationRegistry` model passports. Adds the PB-099-specific
rule: a focal coding model may serve local completion / patch drafting / test gen / narrow refactor /
review triage ONLY through SHADOW routing until it beats (or justifies) its route against the
incumbent provider on NexusNet-OWNED fixtures. Proposed writes are ordinary tool-action proposals
through the existing ToolActionHarness gates. No distillation/training unless source rights permit.
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

FOCAL_CODING_TASKS = (
    "code_completion", "patch_drafting", "test_generation", "narrow_refactor", "review_triage",
    "harness_update_suggestion",
)


class CodingRouteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model_id: str
    task: str
    candidate_score: float                 # focal model score on a NexusNet-owned fixture
    incumbent_id: str
    incumbent_score: float
    license_reviewed: bool = False
    eval_suite_refs: list[str] = Field(default_factory=list)
    rollback_provider: str = ""
    distillation_requested: bool = False
    distillation_rights: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class CodingRouteEvaluator:
    """Shadow-route a focal coding model; propose promotion only on owned-fixture wins. Non-mutating."""

    mutates_production = False

    def __init__(self, *, win_margin: float = 0.02) -> None:
        self.win_margin = win_margin
        self.records: list[dict[str, Any]] = []

    def evaluate(self, request: CodingRouteRequest) -> dict[str, Any]:
        reasons: list[str] = []
        if request.task not in FOCAL_CODING_TASKS:
            reasons.append(f"task_outside_focal_lane:{request.task}")
        if not request.license_reviewed:
            reasons.append("license_card_not_reviewed")
        if not request.eval_suite_refs:
            reasons.append("no_eval_evidence")
        if not request.rollback_provider:
            reasons.append("no_rollback_provider")
        if request.distillation_requested and not request.distillation_rights:
            reasons.append("distillation_without_rights_blocked")

        decision: Literal["block", "shadow_route", "promote_candidate"]
        if reasons:
            decision = "block"
        elif request.candidate_score >= request.incumbent_score + self.win_margin:
            decision = "promote_candidate"
            reasons.append("beats_incumbent_on_owned_fixture")
        else:
            decision = "shadow_route"
            reasons.append("remains_shadow_until_it_beats_incumbent")

        record = {
            "model_id": request.model_id,
            "task": request.task,
            "decision": decision,
            "candidate_score": request.candidate_score,
            "incumbent_id": request.incumbent_id,
            "incumbent_score": request.incumbent_score,
            "reasons": reasons,
            "writes_via_tool_action_harness": True,   # writes never bypass existing gates
            "shadow_only": decision != "promote_candidate",
            "mutates_production": False,
        }
        self.records.append(record)
        return record

    def metrics(self) -> dict[str, Any]:
        n = len(self.records)
        return {
            "routes": n,
            "promote_candidates": sum(1 for r in self.records if r["decision"] == "promote_candidate"),
            "shadow": sum(1 for r in self.records if r["decision"] == "shadow_route"),
            "blocked": sum(1 for r in self.records if r["decision"] == "block"),
        }

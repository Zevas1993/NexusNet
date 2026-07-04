from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


CandidateStatus = Literal[
    "watchlist",
    "quarantined",
    "benchmarked",
    "shadow",
    "canary",
    "active",
    "retired",
    "blocked",
]
TeacherRole = Literal[
    "generator",
    "critic",
    "verifier",
    "retriever",
    "simulator",
    "compact_apprentice",
    "judge",
]
GateStatus = Literal["approved", "blocked", "needs_review", "not_required"]

_PROMOTION_STATUSES: set[CandidateStatus] = {"shadow", "canary"}
_AUTONOMY_RULE = (
    "new-teacher-candidates-start-watchlist-or-quarantined-and-require-source-license-privacy-hardware-cost-benchmark-gates-before-promotion"
)
_NON_BLOCKING_GATES: set[GateStatus] = {"approved", "not_required"}


class TeacherCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    model_or_tool_id: str
    provider: str
    source_url: str
    candidate_status: CandidateStatus = "watchlist"
    teacher_roles: list[TeacherRole] = Field(default_factory=list)
    license_gate: GateStatus = "needs_review"
    privacy_gate: GateStatus = "needs_review"
    hardware_gate: GateStatus = "needs_review"
    cost_gate: GateStatus = "needs_review"
    eval_family: list[str] = Field(default_factory=list)
    domain_scope: list[str] = Field(default_factory=list)
    risk_scope: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)
    benchmark_refs: list[str] = Field(default_factory=list)
    replacement_candidates: list[str] = Field(default_factory=list)
    last_researched_at: str | None = None
    retirement_reason: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class TeacherCandidateUniverse:
    def __init__(self, candidates: Iterable[TeacherCandidate | dict[str, Any]] | None = None) -> None:
        self._candidates: dict[str, TeacherCandidate] = {}
        for candidate in candidates or []:
            self.register(candidate)

    def register(
        self,
        candidate: TeacherCandidate | dict[str, Any],
        *,
        replace: bool = False,
    ) -> TeacherCandidate:
        normalized = candidate if isinstance(candidate, TeacherCandidate) else TeacherCandidate.model_validate(candidate)
        if normalized.candidate_id in self._candidates and not replace:
            raise ValueError(f"Teacher candidate already registered: {normalized.candidate_id}")
        self._candidates[normalized.candidate_id] = normalized
        return normalized

    def get(self, candidate_id: str) -> TeacherCandidate | None:
        candidate = self._candidates.get(candidate_id)
        return candidate.model_copy(deep=True) if candidate is not None else None

    def list_candidates(
        self,
        *,
        status: CandidateStatus | None = None,
        role: TeacherRole | None = None,
        candidate_status: CandidateStatus | None = None,
        teacher_role: TeacherRole | None = None,
        domain: str | None = None,
    ) -> list[TeacherCandidate]:
        status_filter = status or candidate_status
        role_filter = role or teacher_role
        candidates = [candidate.model_copy(deep=True) for candidate in self._candidates.values()]
        if status_filter is not None:
            candidates = [candidate for candidate in candidates if candidate.candidate_status == status_filter]
        if role_filter is not None:
            candidates = [candidate for candidate in candidates if role_filter in candidate.teacher_roles]
        if domain is not None:
            candidates = [candidate for candidate in candidates if domain in candidate.domain_scope]
        return sorted(candidates, key=lambda candidate: candidate.candidate_id)

    def promotion_allowed(self, candidate_id: str) -> bool:
        return not self.promotion_blockers(candidate_id)

    def promotion_blockers(self, candidate_id: str) -> list[str]:
        candidate = self._candidates.get(candidate_id)
        if candidate is None:
            return ["candidate_missing"]

        blockers: list[str] = []
        if candidate.candidate_status not in _PROMOTION_STATUSES:
            blockers.append("candidate_status_not_shadow_or_canary")

        for gate_name in ["license_gate", "privacy_gate", "hardware_gate", "cost_gate"]:
            gate_status = getattr(candidate, gate_name)
            if gate_status == "blocked":
                blockers.append(f"{gate_name}_blocked")
            elif gate_status not in _NON_BLOCKING_GATES:
                blockers.append(f"{gate_name}_not_approved")

        if not candidate.source_refs:
            blockers.append("source_refs_missing")
        if not candidate.benchmark_refs:
            blockers.append("benchmark_refs_missing")
        if candidate.candidate_status == "retired" or candidate.retirement_reason:
            blockers.append("candidate_retired")

        return blockers

    def summary(self) -> dict[str, Any]:
        candidates = self.list_candidates()
        promotion_ready = [candidate for candidate in candidates if self.promotion_allowed(candidate.candidate_id)]
        status_counts: dict[str, int] = {}
        for candidate in candidates:
            status_counts[candidate.candidate_status] = status_counts.get(candidate.candidate_status, 0) + 1

        return {
            "surface_id": "teacher-candidate-universe",
            "candidate_count": len(candidates),
            "status_counts": status_counts,
            "promotion_ready_count": len(promotion_ready),
            "promotion_ready_candidate_ids": [candidate.candidate_id for candidate in promotion_ready],
            "autonomy_rule": _AUTONOMY_RULE,
        }


def build_default_teacher_candidate_universe() -> TeacherCandidateUniverse:
    return TeacherCandidateUniverse(_bootstrap_candidates())


def _bootstrap_candidates() -> list[TeacherCandidate]:
    return [
        TeacherCandidate(
            candidate_id="leanstral-1-5",
            model_or_tool_id="mistralai/Leanstral-1.5-119B-A6B",
            provider="huggingface",
            source_url="https://huggingface.co/mistralai/Leanstral-1.5-119B-A6B",
            candidate_status="watchlist",
            teacher_roles=["verifier", "critic"],
            license_gate="needs_review",
            privacy_gate="needs_review",
            hardware_gate="needs_review",
            cost_gate="needs_review",
            eval_family=["formal-proof", "code-verification"],
            domain_scope=["formal_methods", "math", "coding", "quantum"],
            risk_scope=["medium", "high"],
            source_refs=["hf::mistralai/Leanstral-1.5-119B-A6B"],
        ),
        TeacherCandidate(
            candidate_id="qwen3-coder-next",
            model_or_tool_id="Qwen/Qwen3-Coder-Next",
            provider="huggingface",
            source_url="https://huggingface.co/Qwen/Qwen3-Coder-Next",
            candidate_status="watchlist",
            teacher_roles=["generator", "critic"],
            license_gate="approved",
            privacy_gate="needs_review",
            hardware_gate="needs_review",
            cost_gate="needs_review",
            eval_family=["coding", "agentic-software"],
            domain_scope=["software", "coding"],
            risk_scope=["medium"],
            source_refs=["hf::Qwen/Qwen3-Coder-Next"],
        ),
        TeacherCandidate(
            candidate_id="medgemma-1-5-4b",
            model_or_tool_id="google/medgemma-1.5-4b-it",
            provider="huggingface",
            source_url="https://huggingface.co/google/medgemma-1.5-4b-it",
            candidate_status="quarantined",
            teacher_roles=["critic", "verifier"],
            license_gate="needs_review",
            privacy_gate="needs_review",
            hardware_gate="approved",
            cost_gate="approved",
            eval_family=["medical-safety", "clinical-reasoning", "claim-verification"],
            domain_scope=["medical", "holistic_medicine"],
            risk_scope=["high"],
            source_refs=["hf::google/medgemma-1.5-4b-it"],
        ),
    ]

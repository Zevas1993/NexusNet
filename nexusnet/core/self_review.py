from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow
from nexusnet.policy import PolicyKernel


CandidateType = Literal["output", "memory", "prompt_policy", "tool", "runtime", "adapter", "protocol", "research"]


class SelfReviewIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    issue_id: str
    severity: Literal["hard_fail", "warning"] = "warning"
    status: Literal["open", "resolved", "waived"] = "open"
    detail: str = ""


class SelfReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    review_id: str
    candidate_id: str
    candidate_type: CandidateType
    target_surface: str
    reviewer_refs: list[str] = Field(default_factory=list)
    verifier_refs: list[str] = Field(default_factory=list)
    eval_refs: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    issues: list[SelfReviewIssue] = Field(default_factory=list)
    uncertainty: float = 0.0
    operator_approved: bool = False
    upstream_eval_gate: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SelfReviewGate:
    def __init__(self, *, artifacts_dir: Path | None = None):
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.reviews_dir = self.artifacts_dir / "self-review" / "reviews" if self.artifacts_dir else None
        if self.reviews_dir is not None:
            self.reviews_dir.mkdir(parents=True, exist_ok=True)
        self._memory_reviews: list[dict[str, Any]] = []
        self.policy_kernel = PolicyKernel.default()

    def review(self, request: SelfReviewRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, SelfReviewRequest) else SelfReviewRequest.model_validate(request)
        upstream_eval_gate = _upstream_eval_gate(normalized)
        review_findings = _review_findings(normalized, upstream_eval_gate=upstream_eval_gate)
        policy_scan = self.policy_kernel.scan(_policy_targets(normalized))
        blocked = bool(review_findings) or policy_scan.summary.active_hard_fail_count > 0
        review = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "self-review",
            "review_id": normalized.review_id,
            "candidate_id": normalized.candidate_id,
            "candidate_type": normalized.candidate_type,
            "target_surface": normalized.target_surface,
            "status": "blocked" if blocked else "accepted-shadow",
            "review_state": "blocked-by-review" if blocked else "review-passed",
            "created_at": utcnow().isoformat(),
            "reviewer_refs": normalized.reviewer_refs,
            "verifier_refs": normalized.verifier_refs,
            "eval_refs": normalized.eval_refs,
            "evidence_refs": normalized.evidence_refs,
            "issues": [issue.model_dump(mode="json") for issue in normalized.issues],
            "uncertainty": normalized.uncertainty,
            "operator_approved": normalized.operator_approved,
            "upstream_eval_gate": upstream_eval_gate,
            "required_controls": _required_controls(),
            "review_findings": review_findings,
            "policy_scan": policy_scan.model_dump(mode="json"),
            "metadata": normalized.metadata,
        }
        self._persist(review)
        return review

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        reviews = self._list_reviews(limit=limit)
        latest = reviews[0] if reviews else None
        runtime_state = "static-canon"
        if latest:
            runtime_state = "degraded" if latest.get("status") == "blocked" else "live-bound"
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "self-review",
            "authority": "NexusBrain",
            "runtime_state": runtime_state,
            "review_count": len(reviews),
            "accepted_count": sum(1 for review in reviews if review.get("status") == "accepted-shadow"),
            "blocked_count": sum(1 for review in reviews if review.get("status") == "blocked"),
            "latest_review": latest,
            "reviews": reviews,
            "required_controls": _required_controls(),
            "operator_actions": _operator_actions(),
        }

    def scorecard(self) -> dict[str, Any]:
        summary = self.summary()
        return {
            **summary,
            "source_documents": [
                "docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md",
                "docs/SELF_IMPROVEMENT_LAYER.md",
                "docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md",
            ],
            "review_boundary": "no-self-only-review-no-unverified-output-no-high-impact-change-without-operator-approval",
            "promotion_boundary": "accepted-reviews-enter-shadow-or-evidence-ledger-before-active-use",
        }

    def _persist(self, review: dict[str, Any]) -> None:
        self._memory_reviews.insert(0, review)
        self._memory_reviews = self._memory_reviews[:50]
        if self.reviews_dir is not None:
            safe_id = review["review_id"].replace(":", "_").replace("/", "_")
            path = self.reviews_dir / f"{safe_id}.json"
            review["artifact_path"] = str(path)
            path.write_text(json.dumps(review, indent=2), encoding="utf-8")

    def _list_reviews(self, *, limit: int) -> list[dict[str, Any]]:
        reviews = list(self._memory_reviews)
        seen = {review.get("review_id") for review in reviews}
        if self.reviews_dir is not None:
            for path in self.reviews_dir.glob("*.json"):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if payload.get("review_id") not in seen:
                    reviews.append(payload)
        reviews.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return reviews[:limit]


def _review_findings(request: SelfReviewRequest, *, upstream_eval_gate: dict[str, Any] | None = None) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    upstream_eval_gate = upstream_eval_gate or {}
    normalized_reviewers = {ref.strip().lower() for ref in request.reviewer_refs if ref.strip()}
    only_self = not normalized_reviewers or normalized_reviewers == {"nexusbrain"}
    if only_self:
        findings.append(
            {
                "rule_id": "self_review_requires_independent_reviewer",
                "severity": "hard_fail",
                "message": "Self-review cannot rely only on NexusBrain; AO, expert, tool, or external verifier review is required.",
            }
        )
    if not request.verifier_refs:
        findings.append(
            {
                "rule_id": "self_review_requires_external_or_tool_verifier",
                "severity": "hard_fail",
                "message": "Self-review requires an external, tool, eval, or independent verifier reference.",
            }
        )
    if not request.evidence_refs:
        findings.append(
            {
                "rule_id": "self_review_requires_evidence_refs",
                "severity": "hard_fail",
                "message": "Self-review requires evidence references before acceptance.",
            }
        )
    open_hard_issues = [issue for issue in request.issues if issue.severity == "hard_fail" and issue.status == "open"]
    if open_hard_issues:
        findings.append(
            {
                "rule_id": "self_review_requires_issue_resolution",
                "severity": "hard_fail",
                "message": "Self-review cannot pass while hard-fail issues remain open.",
            }
        )
    if request.uncertainty > 0.5:
        findings.append(
            {
                "rule_id": "self_review_uncertainty_above_threshold",
                "severity": "hard_fail",
                "message": "High uncertainty requires revision, more evidence, or operator escalation.",
            }
        )
    if request.candidate_type in {"memory", "prompt_policy", "tool", "runtime", "adapter", "protocol"} and not request.operator_approved:
        findings.append(
            {
                "rule_id": "self_review_requires_operator_approval_for_high_impact",
                "severity": "hard_fail",
                "message": "High-impact behavior or runtime candidates require operator approval before passing review.",
            }
        )
    if request.candidate_type == "output" and (request.uncertainty > 0.5 or open_hard_issues) and not request.operator_approved:
        findings.append(
            {
                "rule_id": "self_review_requires_operator_approval_for_high_impact",
                "severity": "hard_fail",
                "message": "High-risk output review requires operator approval or revision.",
            }
        )
    if upstream_eval_gate.get("promotion_allowed") is False:
        findings.append(
            {
                "rule_id": "self_review_blocks_eval_promotion_gate",
                "severity": "hard_fail",
                "message": "Self-review cannot accept a candidate while the upstream eval promotion gate is blocked.",
            }
        )
    lifecycle_gate = upstream_eval_gate.get("upstream_lifecycle_gate") or {}
    if lifecycle_gate.get("lifecycle_status") == "closed_loop_blocked":
        findings.append(
            {
                "rule_id": "self_review_blocks_upstream_lifecycle_gate",
                "severity": "hard_fail",
                "message": "Self-review cannot accept a candidate from a blocked growth lifecycle.",
            }
        )
    return findings


def _upstream_eval_gate(request: SelfReviewRequest) -> dict[str, Any]:
    gate = request.upstream_eval_gate or {}
    lifecycle_gate = gate.get("upstream_lifecycle_gate") or {}
    blockers = [str(item) for item in gate.get("blockers") or []]
    blockers.extend(str(item) for item in lifecycle_gate.get("blockers") or [])
    return {
        "promotion_allowed": gate.get("promotion_allowed"),
        "blockers": sorted(set(blockers)),
        "upstream_lifecycle_gate": lifecycle_gate,
        "source": gate.get("source") or "eval_registry_shadow_run",
    }


def _policy_targets(request: SelfReviewRequest) -> list[dict[str, Any]]:
    promotion_requested = request.candidate_type in {"memory", "prompt_policy", "tool", "runtime", "adapter", "protocol"}
    targets: list[dict[str, Any]] = [
        {
            "target_id": f"review-artifact::{request.review_id}",
            "target_type": "artifact",
            "metadata": {
                "promotion_requested": True,
                "license_state": "approved" if request.evidence_refs else None,
                "provenance_refs": request.evidence_refs,
            },
        },
        {
            "target_id": f"review-promotion::{request.review_id}",
            "target_type": "autonomous_update",
            "metadata": {
                "promotion_requested": promotion_requested,
                "rollback_plan": request.metadata.get("rollback_plan", "self-review-shadow-rollback") if promotion_requested else "",
                "monitoring_plan": request.metadata.get("monitoring_plan", "self-review-monitoring") if promotion_requested else "",
            },
        },
    ]
    if request.candidate_type == "adapter":
        targets.append(
            {
                "target_id": f"training::{request.review_id}",
                "target_type": "training_candidate",
                "metadata": {
                    "contains_private_data": bool(request.metadata.get("contains_private_data")),
                    "uses_user_data": bool(request.metadata.get("uses_user_data")),
                    "operator_approved": request.operator_approved,
                    "promotion_requested": promotion_requested,
                    "eval_refs": request.eval_refs,
                },
            }
        )
    return targets


def _required_controls() -> list[str]:
    return [
        "independent_reviewers",
        "external_or_tool_verifier",
        "evidence_refs",
        "issue_log",
        "uncertainty_threshold",
        "operator_approval",
        "policy_scan",
    ]


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/self-review"},
        "record_review": {"method": "POST", "endpoint": "/ops/brain/self-review/reviews"},
        "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/self-review"},
    }

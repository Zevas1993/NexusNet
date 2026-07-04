from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow
from nexusnet.policy import PolicyKernel


LearningTarget = Literal[
    "style_behavior",
    "stable_behavior",
    "tool_routing",
    "domain_knowledge",
    "fresh_knowledge",
    "private_user_memory",
    "safety_policy",
    "multimodal_grounding",
    "other",
]
LicenseStatus = Literal["approved", "blocked", "needs_review"]
DatasetManifestStatus = Literal["ready", "needs_review", "blocked", "unknown"]


class FineTuneDecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision_id: str
    candidate_id: str
    learning_target: LearningTarget
    failure_modes: list[str] = Field(default_factory=list)
    prompt_attempted: bool = False
    rag_attempted: bool = False
    agent_loop_attempted: bool = False
    eval_refs: list[str] = Field(default_factory=list)
    provenance_refs: list[str] = Field(default_factory=list)
    contains_private_data: bool = False
    license_status: LicenseStatus = "needs_review"
    operator_approved: bool = False
    dataset_manifest_id: str = ""
    dataset_manifest_status: DatasetManifestStatus = "unknown"
    dataset_radar_training_review_gate: dict[str, Any] = Field(default_factory=dict)
    adapter_plan_id: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class FineTuneDecisionGate:
    def __init__(self, *, artifacts_dir: Path | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.decisions_dir = self.artifacts_dir / "adapters" / "fine-tune-decision-gate" if self.artifacts_dir else None
        if self.decisions_dir is not None:
            self.decisions_dir.mkdir(parents=True, exist_ok=True)
        self._memory_decisions: list[dict[str, Any]] = []
        self.policy_kernel = PolicyKernel.default()

    def decide(self, request: FineTuneDecisionRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, FineTuneDecisionRequest) else FineTuneDecisionRequest.model_validate(request)
        decision_findings = _decision_findings(normalized)
        policy_scan = self.policy_kernel.scan(_policy_targets(normalized))
        blocked = _has_hard_fail(decision_findings) or policy_scan.summary.active_hard_fail_count > 0
        status, recommended_path = _route(normalized, blocked=blocked)
        allowed = status == "adapter-shadow-eligible"
        decision = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "fine-tune-decision-gate",
            "decision_id": normalized.decision_id,
            "candidate_id": normalized.candidate_id,
            "status": status,
            "recommended_path": recommended_path,
            "runtime_state": "degraded" if blocked else ("live-bound" if allowed else "shadow-only"),
            "created_at": utcnow().isoformat(),
            "learning_target": normalized.learning_target,
            "failure_modes": normalized.failure_modes,
            "prompt_attempted": normalized.prompt_attempted,
            "rag_attempted": normalized.rag_attempted,
            "agent_loop_attempted": normalized.agent_loop_attempted,
            "eval_refs": normalized.eval_refs,
            "provenance_refs": normalized.provenance_refs,
            "contains_private_data": normalized.contains_private_data,
            "license_status": normalized.license_status,
            "operator_approved": normalized.operator_approved,
            "dataset_manifest_id": normalized.dataset_manifest_id,
            "dataset_manifest_status": normalized.dataset_manifest_status,
            "dataset_radar_training_review_gate": normalized.dataset_radar_training_review_gate,
            "adapter_plan_id": normalized.adapter_plan_id,
            "adapter_training_allowed": allowed,
            "training_boundary": "decision-only-no-training-job",
            "promotion_boundary": "adapter-training-requires-prompt-rag-agent-loop-exhaustion-eval-provenance-rights-and-operator-approval",
            "required_controls": _required_controls(),
            "decision_findings": decision_findings,
            "policy_scan": policy_scan.model_dump(mode="json"),
            "operator_actions": _operator_actions(),
            "metadata": normalized.metadata,
        }
        self._persist(decision)
        return decision

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        decisions = self._list_decisions(limit=limit)
        blocked_count = sum(1 for decision in decisions if decision.get("status") == "blocked")
        latest_decision = decisions[0] if decisions else None
        runtime_state = "static-canon"
        if decisions:
            runtime_state = "degraded" if blocked_count or latest_decision.get("status") == "blocked" else "live-bound"
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "fine-tune-decision-gate",
            "authority": "NexusBrain",
            "runtime_state": runtime_state,
            "decision_count": len(decisions),
            "adapter_eligible_count": sum(1 for decision in decisions if decision.get("status") == "adapter-shadow-eligible"),
            "blocked_count": blocked_count,
            "retrieval_first_count": sum(1 for decision in decisions if decision.get("recommended_path") == "rag"),
            "latest_decision": latest_decision,
            "decisions": decisions,
            "canonical_ladder": _canonical_ladder(),
            "required_controls": _required_controls(),
            "operator_actions": _operator_actions(),
            "training_boundary": "decision-only-no-training-job",
        }

    def scorecard(self) -> dict[str, Any]:
        summary = self.summary()
        return {
            **summary,
            "source_documents": [
                "youtube-transcript::v7qMjy_RxOs",
                "docs/NEXUSNET_YOUTUBE_ASSIMILATION_INTAKE_2026-04-30.md",
                "docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md",
            ],
            "assimilation_pattern": "prompt-first-then-rag-then-agent-loop-then-human-reviewed-adapter-candidate",
            "knowledge_rule": "fresh-or-changing-knowledge-stays-retrieval-first",
            "privacy_rule": "raw-user-sessions-browser-history-and-transcripts-require-rights-provenance-review-and-operator-approval",
        }

    def _persist(self, decision: dict[str, Any]) -> None:
        self._memory_decisions.insert(0, decision)
        self._memory_decisions = self._memory_decisions[:50]
        if self.decisions_dir is not None:
            safe_id = decision["decision_id"].replace(":", "_").replace("/", "_")
            path = self.decisions_dir / f"{safe_id}.json"
            decision["artifact_path"] = str(path)
            path.write_text(json.dumps(decision, indent=2), encoding="utf-8")

    def _list_decisions(self, *, limit: int) -> list[dict[str, Any]]:
        decisions = list(self._memory_decisions)
        seen = {decision.get("decision_id") for decision in decisions}
        if self.decisions_dir is not None:
            for path in self.decisions_dir.glob("*.json"):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if payload.get("decision_id") not in seen:
                    decisions.append(payload)
        decisions.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return decisions[:limit]


def _route(request: FineTuneDecisionRequest, *, blocked: bool) -> tuple[str, str]:
    if blocked:
        return "blocked", "blocked"
    if not request.prompt_attempted:
        return "prompt-first", "prompt"
    if request.learning_target in {"fresh_knowledge", "private_user_memory", "domain_knowledge"}:
        return "rag-first", "rag"
    if not request.rag_attempted:
        return "rag-first", "rag"
    if not request.agent_loop_attempted:
        return "agent-loop-first", "agent-loop"
    return "adapter-shadow-eligible", "adapter-training"


def _decision_findings(request: FineTuneDecisionRequest) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if request.contains_private_data and not request.operator_approved:
        findings.append(_finding("fine_tune_gate_private_data_requires_operator_approval", "Private fine-tune candidates require explicit operator approval."))
    if request.license_status != "approved":
        findings.append(_finding("fine_tune_gate_requires_approved_license", "Fine-tune candidates require approved dataset and model license status."))
    if not request.eval_refs:
        findings.append(_finding("fine_tune_gate_requires_eval_refs", "Fine-tune decisions require held-out eval references before any adapter route."))
    if not request.provenance_refs:
        findings.append(_finding("fine_tune_gate_requires_provenance_refs", "Fine-tune decisions require source-to-claim and dataset provenance references."))
    if request.learning_target in {"fresh_knowledge", "private_user_memory", "domain_knowledge"}:
        findings.append(
            _finding(
                "fine_tune_gate_changing_knowledge_stays_retrieval_first",
                "Changing knowledge should be solved with retrieval or memory updates before adapter training.",
                severity="advisory",
            )
        )
    if request.prompt_attempted and request.rag_attempted and request.agent_loop_attempted and not request.dataset_manifest_id:
        findings.append(_finding("fine_tune_gate_requires_dataset_manifest", "Adapter-eligible candidates require a curated dataset manifest."))
    if (
        request.prompt_attempted
        and request.rag_attempted
        and request.agent_loop_attempted
        and request.dataset_manifest_status in {"needs_review", "blocked"}
    ):
        findings.append(
            _finding(
                "fine_tune_gate_requires_ready_dataset_manifest",
                "Adapter-eligible candidates require a DatasetForge manifest whose status is ready.",
            )
        )
    training_review_gate = request.dataset_radar_training_review_gate or {}
    if (
        request.prompt_attempted
        and request.rag_attempted
        and request.agent_loop_attempted
        and training_review_gate
        and not training_review_gate.get("allowed")
    ):
        findings.append(
            _finding(
                "fine_tune_gate_dataset_radar_training_review_blocked",
                "Dataset Radar training-review blockers must be cleared before adapter eligibility.",
            )
        )
    if request.prompt_attempted and request.rag_attempted and request.agent_loop_attempted and not request.adapter_plan_id:
        findings.append(_finding("fine_tune_gate_requires_adapter_plan", "Adapter-eligible candidates require an adapter training plan reference."))
    return findings


def _finding(rule_id: str, message: str, severity: str = "hard_fail") -> dict[str, str]:
    return {"rule_id": rule_id, "severity": severity, "message": message}


def _has_hard_fail(findings: list[dict[str, str]]) -> bool:
    return any(finding.get("severity") == "hard_fail" for finding in findings)


def _policy_targets(request: FineTuneDecisionRequest) -> list[dict[str, Any]]:
    return [
        {
            "target_id": f"training::{request.decision_id}",
            "target_type": "training_candidate",
            "metadata": {
                "contains_private_data": request.contains_private_data,
                "uses_user_data": request.contains_private_data,
                "operator_approved": request.operator_approved,
                "promotion_requested": True,
                "eval_refs": request.eval_refs,
            },
        },
        {
            "target_id": f"artifact::{request.decision_id}",
            "target_type": "artifact",
            "metadata": {
                "promotion_requested": True,
                "license_state": "approved" if request.license_status == "approved" else None,
                "provenance_refs": request.provenance_refs,
            },
        },
        {
            "target_id": f"autonomous-update::{request.decision_id}",
            "target_type": "autonomous_update",
            "metadata": {
                "promotion_requested": False,
                "rollback_plan": request.adapter_plan_id,
                "monitoring_plan": "adapter-shadow-eval-required-before-activation",
            },
        },
    ]


def _canonical_ladder() -> list[dict[str, str]]:
    return [
        {"stage_id": "prompt-first", "label": "Try a better prompt or instruction patch first.", "state": "required-baseline"},
        {"stage_id": "rag-first", "label": "Use retrieval or memory updates for changing knowledge.", "state": "required-baseline"},
        {"stage_id": "agent-loop-first", "label": "Use tool routing or agentic loops when the failure is workflow-shaped.", "state": "required-baseline"},
        {"stage_id": "adapter-shadow-only", "label": "Only then create a human-reviewable adapter training candidate.", "state": "shadow-only"},
    ]


def _required_controls() -> list[str]:
    return [
        "prompt-first",
        "rag-first",
        "agent-loop-first",
        "eval-provenance-required",
        "operator-approval-required",
        "rights-license-required",
        "dataset-manifest-required",
        "dataset-manifest-ready-required",
        "dataset-radar-training-review-required",
        "adapter-plan-required",
        "adapter-shadow-only",
    ]


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/fine-tune-decision-gate"},
        "decide": {"method": "POST", "endpoint": "/ops/brain/fine-tune-decision-gate/decisions"},
        "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/fine-tune-decision-gate"},
        "dataset_forge": {"method": "GET", "endpoint": "/ops/brain/dataset-forge"},
        "adapter_training": {"method": "GET", "endpoint": "/ops/brain/adapter-training"},
    }

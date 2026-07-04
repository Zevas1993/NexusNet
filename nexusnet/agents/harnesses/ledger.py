from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow
from nexusnet.policy import PolicyKernel


HarnessChangeType = Literal[
    "planner",
    "tool_routing",
    "context_management",
    "memory_policy",
    "sandboxing",
    "review_loop",
    "scheduler",
    "eval_harness",
]


class HarnessLedgerEntryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entry_id: str
    harness_id: str
    change_type: HarnessChangeType
    proposer: str
    diff_summary: str
    source_refs: list[str] = Field(default_factory=list)
    shadow_run_refs: list[str] = Field(default_factory=list)
    optimization_eval_refs: list[str] = Field(default_factory=list)
    heldout_eval_refs: list[str] = Field(default_factory=list)
    baseline_score: float = 0.0
    candidate_score: float = 0.0
    regression_failures: list[str] = Field(default_factory=list)
    security_review_passed: bool = False
    rollback_plan: str = ""
    operator_approved: bool = False
    upstream_self_review_gate: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class HarnessImprovementLedger:
    def __init__(self, *, artifacts_dir: Path | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.entries_dir = self.artifacts_dir / "agents" / "harness-improvement-ledger" if self.artifacts_dir else None
        if self.entries_dir is not None:
            self.entries_dir.mkdir(parents=True, exist_ok=True)
        self._memory_entries: list[dict[str, Any]] = []
        self.policy_kernel = PolicyKernel.default()

    def record(self, request: HarnessLedgerEntryRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, HarnessLedgerEntryRequest) else HarnessLedgerEntryRequest.model_validate(request)
        upstream_self_review_gate = _upstream_self_review_gate(normalized)
        findings = _ledger_findings(normalized, upstream_self_review_gate=upstream_self_review_gate)
        policy_scan = self.policy_kernel.scan(_policy_targets(normalized))
        blocked = _has_hard_fail(findings) or policy_scan.summary.active_hard_fail_count > 0
        promotion_allowed = not blocked
        entry = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "harness-improvement-ledger",
            "entry_id": normalized.entry_id,
            "harness_id": normalized.harness_id,
            "change_type": normalized.change_type,
            "proposer": normalized.proposer,
            "diff_summary": normalized.diff_summary,
            "status": "blocked" if blocked else "shadow-validated",
            "runtime_state": "degraded" if blocked else "live-bound",
            "promotion_allowed": promotion_allowed,
            "created_at": utcnow().isoformat(),
            "source_refs": normalized.source_refs,
            "shadow_run_refs": normalized.shadow_run_refs,
            "optimization_eval_refs": normalized.optimization_eval_refs,
            "heldout_eval_refs": normalized.heldout_eval_refs,
            "baseline_score": normalized.baseline_score,
            "candidate_score": normalized.candidate_score,
            "score_delta": round(normalized.candidate_score - normalized.baseline_score, 4),
            "regression_failures": normalized.regression_failures,
            "security_review_passed": normalized.security_review_passed,
            "rollback_plan": normalized.rollback_plan,
            "operator_approved": normalized.operator_approved,
            "upstream_self_review_gate": upstream_self_review_gate,
            "ledger_findings": findings,
            "policy_scan": policy_scan.model_dump(mode="json"),
            "required_controls": _required_controls(),
            "promotion_boundary": "harness-diffs-require-shadow-run-heldout-eval-separation-security-rollback-and-operator-approval",
            "operator_actions": _operator_actions(),
            "metadata": normalized.metadata,
        }
        self._persist(entry)
        return entry

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        entries = self._list_entries(limit=limit)
        blocked_count = sum(1 for entry in entries if entry.get("status") == "blocked")
        latest_entry = entries[0] if entries else None
        runtime_state = "static-canon"
        if entries:
            runtime_state = "degraded" if blocked_count or latest_entry.get("status") == "blocked" else "live-bound"
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "harness-improvement-ledger",
            "authority": "NexusBrain",
            "runtime_state": runtime_state,
            "entry_count": len(entries),
            "shadow_validated_count": sum(1 for entry in entries if entry.get("status") == "shadow-validated"),
            "blocked_count": blocked_count,
            "average_score_delta": _average(entry.get("score_delta", 0.0) for entry in entries if entry.get("status") == "shadow-validated"),
            "latest_entry": latest_entry,
            "entries": entries,
            "required_controls": _required_controls(),
            "operator_actions": _operator_actions(),
            "evolution_boundary": "the-harness-can-evolve-only-through-shadow-tested-eval-separated-ledgered-changes",
        }

    def scorecard(self) -> dict[str, Any]:
        summary = self.summary()
        return {
            **summary,
            "source_documents": [
                "docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md#agent-harness-self-improvement",
                "docs/NEXUSNET_YOUTUBE_ASSIMILATION_INTAKE_2026-04-30.md",
                "docs/SELF_IMPROVEMENT_LAYER.md",
            ],
            "watch_items": ["AutoHarness", "Meta-Harness", "Reflexion", "self-review", "heldout-eval-leakage"],
            "control_panel_label": "Harness Improvement Ledger",
        }

    def _persist(self, entry: dict[str, Any]) -> None:
        self._memory_entries = [item for item in self._memory_entries if item.get("entry_id") != entry.get("entry_id")]
        self._memory_entries.insert(0, entry)
        self._memory_entries = self._memory_entries[:50]
        if self.entries_dir is not None:
            safe_id = entry["entry_id"].replace(":", "_").replace("/", "_")
            path = self.entries_dir / f"{safe_id}.json"
            entry["artifact_path"] = str(path)
            path.write_text(json.dumps(entry, indent=2), encoding="utf-8")

    def _list_entries(self, *, limit: int) -> list[dict[str, Any]]:
        entries = list(self._memory_entries)
        seen = {entry.get("entry_id") for entry in entries}
        if self.entries_dir is not None:
            for path in self.entries_dir.glob("*.json"):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if payload.get("entry_id") not in seen:
                    entries.append(payload)
        entries.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return entries[:limit]


def _ledger_findings(
    request: HarnessLedgerEntryRequest,
    *,
    upstream_self_review_gate: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    upstream_self_review_gate = upstream_self_review_gate or {}
    if not request.source_refs:
        findings.append(_finding("harness_ledger_requires_source_refs", "Harness changes require source, paper, trace, or operator evidence references."))
    if not request.shadow_run_refs:
        findings.append(_finding("harness_ledger_requires_shadow_runs", "Harness changes require shadow-run evidence before promotion."))
    if not request.heldout_eval_refs:
        findings.append(_finding("harness_ledger_requires_heldout_eval_refs", "Harness changes require held-out eval evidence."))
    if set(request.optimization_eval_refs) & set(request.heldout_eval_refs):
        findings.append(_finding("harness_ledger_blocks_heldout_overlap", "Optimization evals and held-out evals must remain separated."))
    if request.candidate_score <= request.baseline_score:
        findings.append(_finding("harness_ledger_requires_positive_score_delta", "Harness candidate must improve on the baseline before promotion."))
    if request.regression_failures:
        findings.append(_finding("harness_ledger_blocks_regression_failures", "Harness candidate has unresolved regression failures."))
    if not request.security_review_passed:
        findings.append(_finding("harness_ledger_requires_security_review", "Harness changes require security review before promotion."))
    if not request.rollback_plan.strip():
        findings.append(_finding("harness_ledger_requires_rollback_plan", "Harness changes require a rollback plan."))
    if not request.operator_approved:
        findings.append(_finding("harness_ledger_requires_operator_approval", "Harness changes require operator approval before promotion."))
    if upstream_self_review_gate.get("status") == "blocked" or upstream_self_review_gate.get("review_state") == "blocked-by-review":
        findings.append(_finding("harness_ledger_blocks_self_review_gate", "Harness changes cannot be promotion-allowed while upstream self-review is blocked."))
    upstream_eval_gate = upstream_self_review_gate.get("upstream_eval_gate") or {}
    if upstream_eval_gate.get("promotion_allowed") is False:
        findings.append(_finding("harness_ledger_blocks_upstream_eval_gate", "Harness changes cannot be promotion-allowed while upstream eval evidence is blocked."))
    upstream_lifecycle_gate = upstream_eval_gate.get("upstream_lifecycle_gate") or {}
    if upstream_lifecycle_gate.get("lifecycle_status") == "closed_loop_blocked":
        findings.append(_finding("harness_ledger_blocks_upstream_lifecycle_gate", "Harness changes cannot be promotion-allowed while upstream lifecycle evidence is blocked."))
    return findings


def _upstream_self_review_gate(request: HarnessLedgerEntryRequest) -> dict[str, Any]:
    gate = request.upstream_self_review_gate or {}
    eval_gate = gate.get("upstream_eval_gate") or {}
    lifecycle_gate = eval_gate.get("upstream_lifecycle_gate") or {}
    blockers = [str(item) for item in gate.get("blockers") or []]
    blockers.extend(str(item) for item in eval_gate.get("blockers") or [])
    blockers.extend(str(item) for item in lifecycle_gate.get("blockers") or [])
    return {
        "status": gate.get("status") or "not_provided",
        "review_state": gate.get("review_state") or "unknown",
        "review_id": gate.get("review_id") or "",
        "blockers": sorted(set(blockers)),
        "upstream_eval_gate": {
            **eval_gate,
            "blockers": sorted(set([str(item) for item in eval_gate.get("blockers") or []] + [str(item) for item in lifecycle_gate.get("blockers") or []])),
            "upstream_lifecycle_gate": lifecycle_gate,
        },
        "source": gate.get("source") or "self_review_scorecard",
    }


def _policy_targets(request: HarnessLedgerEntryRequest) -> list[dict[str, Any]]:
    return [
        {
            "target_id": f"harness-ledger::{request.entry_id}",
            "target_type": "autonomous_update",
            "metadata": {
                "promotion_requested": request.operator_approved,
                "rollback_plan": request.rollback_plan,
                "monitoring_plan": "harness-shadow-runs-heldout-evals-and-regression-monitoring",
            },
        },
        {
            "target_id": f"harness-artifact::{request.entry_id}",
            "target_type": "artifact",
            "metadata": {
                "promotion_requested": request.operator_approved,
                "license_state": "approved",
                "provenance_refs": [*request.source_refs, *request.shadow_run_refs, *request.heldout_eval_refs],
            },
        },
    ]


def _finding(rule_id: str, message: str, severity: str = "hard_fail") -> dict[str, str]:
    return {"rule_id": rule_id, "severity": severity, "message": message}


def _has_hard_fail(findings: list[dict[str, str]]) -> bool:
    return any(finding.get("severity") == "hard_fail" for finding in findings)


def _average(values: Any) -> float:
    realized = [float(value or 0.0) for value in values]
    if not realized:
        return 0.0
    return round(sum(realized) / len(realized), 4)


def _required_controls() -> list[str]:
    return [
        "harness_diff_summary",
        "source_refs",
        "shadow_run_refs",
        "optimization_eval_refs",
        "heldout_eval_refs",
        "heldout_eval_separation",
        "score_delta",
        "regression_failures",
        "security_review",
        "rollback_plan",
        "operator_approval",
    ]


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/evolution/harness-ledger"},
        "record": {"method": "POST", "endpoint": "/ops/brain/evolution/harness-ledger/entries"},
        "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/harness-ledger"},
        "self_review": {"method": "GET", "endpoint": "/ops/brain/self-review"},
        "autonomous_updates": {"method": "GET", "endpoint": "/ops/brain/autonomous-updates"},
    }

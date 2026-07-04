from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow
from nexusnet.policy import PolicyKernel


EvalSuiteType = Literal["agentic", "runtime", "retrieval", "memory", "security", "multimodal", "coding"]
PromotionTarget = Literal["autonomous_update", "adapter", "quantization", "memory", "tooling", "none"]


class EvalSuiteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    suite_id: str
    suite_type: EvalSuiteType
    target_surfaces: list[str] = Field(default_factory=list)
    benchmark_refs: list[str] = Field(default_factory=list)
    held_out: bool = False
    external_or_tool_verifier: bool = True
    metrics: dict[str, float] = Field(default_factory=dict)
    promotion_target: PromotionTarget = "none"
    evidence_refs: list[str] = Field(default_factory=list)
    rollback_plan: str = "regression-baseline-rollback"
    monitoring_plan: str = "eval-trend-and-drift-monitoring"
    metadata: dict[str, Any] = Field(default_factory=dict)


class ShadowEvalRunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    candidate_ref: str
    baseline_ref: str = ""
    metrics: dict[str, float] = Field(default_factory=dict)
    trace_refs: list[str] = Field(default_factory=list)
    evaluator_refs: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    operator_approved: bool = False
    lifecycle_ref: str = ""
    lifecycle_status: str = "unknown"
    growth_engine_gate: dict[str, Any] = Field(default_factory=dict)
    artifact_trust_promotion: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvalRegistry:
    def __init__(self, *, artifacts_dir: Path | None = None):
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.suites_dir = self.artifacts_dir / "evals" / "registry" if self.artifacts_dir else None
        self.shadow_runs_dir = self.artifacts_dir / "evals" / "shadow-runs" if self.artifacts_dir else None
        if self.suites_dir is not None:
            self.suites_dir.mkdir(parents=True, exist_ok=True)
        if self.shadow_runs_dir is not None:
            self.shadow_runs_dir.mkdir(parents=True, exist_ok=True)
        self._memory_suites: list[dict[str, Any]] = []
        self._memory_shadow_runs: list[dict[str, Any]] = []
        self.policy_kernel = PolicyKernel.default()

    @classmethod
    def default(cls, *, artifacts_dir: Path | None = None) -> "EvalRegistry":
        return cls(artifacts_dir=artifacts_dir)

    def register(self, request: EvalSuiteRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, EvalSuiteRequest) else EvalSuiteRequest.model_validate(request)
        eval_findings = _eval_findings(normalized)
        policy_scan = self.policy_kernel.scan(_policy_targets(normalized))
        blocked = bool(eval_findings) or policy_scan.summary.active_hard_fail_count > 0
        suite = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "eval-registry",
            "suite_id": normalized.suite_id,
            "suite_type": normalized.suite_type,
            "target_surfaces": normalized.target_surfaces,
            "benchmark_refs": normalized.benchmark_refs,
            "held_out": normalized.held_out,
            "external_or_tool_verifier": normalized.external_or_tool_verifier,
            "metrics": normalized.metrics,
            "promotion_target": normalized.promotion_target,
            "promotion_gate": "blocked" if blocked else "passed",
            "status": "blocked" if blocked else "active",
            "created_at": utcnow().isoformat(),
            "evidence_refs": normalized.evidence_refs,
            "rollback_plan": normalized.rollback_plan,
            "monitoring_plan": normalized.monitoring_plan,
            "required_controls": _required_controls(),
            "eval_findings": eval_findings,
            "policy_scan": policy_scan.model_dump(mode="json"),
            "metadata": normalized.metadata,
        }
        self._persist(suite)
        return suite

    def run_shadow(self, suite_id: str, request: ShadowEvalRunRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, ShadowEvalRunRequest) else ShadowEvalRunRequest.model_validate(request)
        suite = self._get_suite(suite_id)
        upstream_lifecycle_gate = _upstream_lifecycle_gate(normalized)
        findings = _shadow_findings(normalized, suite=suite, upstream_lifecycle_gate=upstream_lifecycle_gate)
        policy_scan = self.policy_kernel.scan(_shadow_policy_targets(suite_id, normalized))
        blocked = bool(findings) or policy_scan.summary.active_hard_fail_count > 0
        run = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "eval-shadow-run",
            "run_id": normalized.run_id,
            "suite_id": suite_id,
            "candidate_ref": normalized.candidate_ref,
            "baseline_ref": normalized.baseline_ref,
            "status": "blocked" if blocked else "passed-shadow",
            "runtime_state": "degraded" if blocked else "live-bound",
            "promotion_allowed": not blocked,
            "created_at": utcnow().isoformat(),
            "suite_snapshot": suite,
            "metrics": normalized.metrics,
            "trace_refs": normalized.trace_refs,
            "evaluator_refs": normalized.evaluator_refs,
            "evidence_refs": normalized.evidence_refs,
            "operator_approved": normalized.operator_approved,
            "upstream_lifecycle_gate": upstream_lifecycle_gate,
            "shadow_findings": findings,
            "policy_scan": policy_scan.model_dump(mode="json"),
            "promotion_boundary": "shadow-runs-require-baseline-trace-external-evaluator-evidence-regression-free-result-and-operator-approval",
            "metadata": normalized.metadata,
        }
        self._persist_shadow_run(run)
        return run

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        suites = self._list_suites(limit=limit)
        shadow_runs = self._list_shadow_runs(limit=limit)
        blocked_count = sum(1 for suite in suites if suite.get("status") == "blocked")
        blocked_shadow_count = sum(1 for run in shadow_runs if run.get("status") == "blocked")
        latest_suite = suites[0] if suites else None
        latest_shadow_run = shadow_runs[0] if shadow_runs else None
        runtime_state = "static-canon"
        if suites or shadow_runs:
            latest_suite_blocked = bool(latest_suite and latest_suite.get("status") == "blocked")
            latest_shadow_blocked = bool(latest_shadow_run and latest_shadow_run.get("status") == "blocked")
            runtime_state = "degraded" if blocked_count or blocked_shadow_count or latest_suite_blocked or latest_shadow_blocked else "live-bound"
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "eval-registry",
            "authority": "NexusBrain",
            "runtime_state": runtime_state,
            "suite_count": len(suites),
            "shadow_run_count": len(shadow_runs),
            "active_count": sum(1 for suite in suites if suite.get("status") == "active"),
            "blocked_count": blocked_count,
            "passed_shadow_count": sum(1 for run in shadow_runs if run.get("status") == "passed-shadow"),
            "blocked_shadow_count": blocked_shadow_count,
            "latest_suite": latest_suite,
            "latest_shadow_run": latest_shadow_run,
            "suites": suites,
            "shadow_runs": shadow_runs,
            "benchmark_lanes": _benchmark_lanes(),
            "required_controls": _required_controls(),
            "operator_actions": _operator_actions(),
        }

    def scorecard(self) -> dict[str, Any]:
        summary = self.summary()
        return {
            **summary,
            "source_documents": [
                "docs/NEXUSNET_FORWARD_RESEARCH_RADAR_2026-04-28.md",
                "docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md",
                "docs/NEXUSNET_QUANTIZATION_AGENTIC_RESEARCH_EXPANSION_2026-04-28.md",
            ],
            "promotion_boundary": "no-autonomous-update-without-held-out-external-eval-and-regression-gate",
        }

    def _persist(self, suite: dict[str, Any]) -> None:
        self._memory_suites.insert(0, suite)
        self._memory_suites = self._memory_suites[:50]
        if self.suites_dir is not None:
            safe_id = suite["suite_id"].replace(":", "_").replace("/", "_")
            path = self.suites_dir / f"{safe_id}.json"
            suite["artifact_path"] = str(path)
            path.write_text(json.dumps(suite, indent=2), encoding="utf-8")

    def _persist_shadow_run(self, run: dict[str, Any]) -> None:
        self._memory_shadow_runs = [item for item in self._memory_shadow_runs if item.get("run_id") != run.get("run_id")]
        self._memory_shadow_runs.insert(0, run)
        self._memory_shadow_runs = self._memory_shadow_runs[:50]
        if self.shadow_runs_dir is not None:
            safe_id = run["run_id"].replace(":", "_").replace("/", "_")
            path = self.shadow_runs_dir / f"{safe_id}.json"
            run["artifact_path"] = str(path)
            path.write_text(json.dumps(run, indent=2), encoding="utf-8")

    def _list_suites(self, *, limit: int) -> list[dict[str, Any]]:
        suites = list(self._memory_suites)
        seen = {suite.get("suite_id") for suite in suites}
        if self.suites_dir is not None:
            for path in self.suites_dir.glob("*.json"):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if payload.get("suite_id") not in seen:
                    suites.append(payload)
        suites.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return suites[:limit]

    def _list_shadow_runs(self, *, limit: int) -> list[dict[str, Any]]:
        runs = list(self._memory_shadow_runs)
        seen = {run.get("run_id") for run in runs}
        if self.shadow_runs_dir is not None:
            for path in self.shadow_runs_dir.glob("*.json"):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if payload.get("run_id") not in seen:
                    runs.append(payload)
        runs.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return runs[:limit]

    def _get_suite(self, suite_id: str) -> dict[str, Any] | None:
        for suite in self._list_suites(limit=500):
            if suite.get("suite_id") == suite_id:
                return suite
        return None


def _eval_findings(request: EvalSuiteRequest) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if not request.held_out:
        findings.append(
            {
                "rule_id": "eval_suite_requires_held_out_cases",
                "severity": "hard_fail",
                "message": "Promotion eval suites must include held-out cases.",
            }
        )
    if not request.external_or_tool_verifier or not request.benchmark_refs:
        findings.append(
            {
                "rule_id": "eval_suite_requires_external_or_tool_verifier",
                "severity": "hard_fail",
                "message": "Eval suites need an external benchmark, tool verifier, or Nexus-held-out verifier.",
            }
        )
    if int(request.metrics.get("regression_count", 0)) > 0:
        findings.append(
            {
                "rule_id": "eval_suite_requires_regression_free_result",
                "severity": "hard_fail",
                "message": "Eval suites with regressions cannot promote autonomous changes.",
            }
        )
    return findings


def _policy_targets(request: EvalSuiteRequest) -> list[dict[str, Any]]:
    promotion_requested = request.promotion_target != "none"
    return [
        {
            "target_id": f"eval-artifact::{request.suite_id}",
            "target_type": "artifact",
            "metadata": {
                "promotion_requested": promotion_requested,
                "license_state": "approved" if request.evidence_refs else None,
                "provenance_refs": request.evidence_refs,
            },
        },
        {
            "target_id": f"eval-promotion::{request.suite_id}",
            "target_type": "autonomous_update",
            "metadata": {
                "promotion_requested": promotion_requested,
                "rollback_plan": request.rollback_plan,
                "monitoring_plan": request.monitoring_plan,
            },
        },
    ]


def _shadow_findings(
    request: ShadowEvalRunRequest,
    *,
    suite: dict[str, Any] | None,
    upstream_lifecycle_gate: dict[str, Any],
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if suite is None:
        findings.append(_shadow_finding("shadow_eval_requires_registered_suite", "Shadow eval run requires a registered eval suite."))
    if not request.baseline_ref.strip():
        findings.append(_shadow_finding("shadow_eval_requires_baseline_ref", "Shadow eval run requires a baseline reference."))
    if not request.trace_refs:
        findings.append(_shadow_finding("shadow_eval_requires_trace_refs", "Shadow eval run requires trace references."))
    if not request.evaluator_refs:
        findings.append(_shadow_finding("shadow_eval_requires_external_evaluator_refs", "Shadow eval run requires external or tool evaluator references."))
    if not request.evidence_refs:
        findings.append(_shadow_finding("shadow_eval_requires_evidence_refs", "Shadow eval run requires evidence references."))
    if int(request.metrics.get("regression_count", 0)) > 0:
        findings.append(_shadow_finding("shadow_eval_blocks_regressions", "Shadow eval run with regressions cannot promote."))
    if not request.operator_approved:
        findings.append(_shadow_finding("shadow_eval_requires_operator_approval", "Shadow eval run requires operator approval for promotion use."))
    if request.lifecycle_status == "closed_loop_blocked":
        findings.append(
            _shadow_finding(
                "shadow_eval_blocks_blocked_lifecycle",
                "Shadow eval run cannot promote from a blocked production lifecycle.",
            )
        )
    if upstream_lifecycle_gate["growth_engine_gate_allowed"] is False:
        findings.append(
            _shadow_finding(
                "shadow_eval_blocks_growth_engine_gate",
                "Shadow eval run cannot promote while the upstream Growth Engine gate is blocked.",
            )
        )
    if upstream_lifecycle_gate["artifact_trust_promotion_allowed"] is False:
        findings.append(
            _shadow_finding(
                "shadow_eval_blocks_artifact_trust_promotion",
                "Shadow eval run cannot promote when artifact-trust replay promotion is blocked.",
            )
        )
    return findings


def _upstream_lifecycle_gate(request: ShadowEvalRunRequest) -> dict[str, Any]:
    growth_engine_gate = request.growth_engine_gate or {}
    artifact_trust_promotion = request.artifact_trust_promotion or {}
    blockers = [str(item) for item in growth_engine_gate.get("blockers") or []]
    blockers.extend(str(item) for item in artifact_trust_promotion.get("promotion_blockers") or [])
    if request.lifecycle_status == "closed_loop_blocked":
        blockers.append("production_lifecycle_blocked")
    return {
        "lifecycle_ref": request.lifecycle_ref,
        "lifecycle_status": request.lifecycle_status,
        "growth_engine_gate_allowed": growth_engine_gate.get("allowed"),
        "artifact_trust_promotion_allowed": artifact_trust_promotion.get("promotion_allowed"),
        "blockers": sorted(set(blockers)),
    }


def _shadow_policy_targets(suite_id: str, request: ShadowEvalRunRequest) -> list[dict[str, Any]]:
    return [
        {
            "target_id": f"shadow-eval::{request.run_id}",
            "target_type": "artifact",
            "metadata": {
                "promotion_requested": request.operator_approved,
                "license_state": "approved" if request.evidence_refs else None,
                "provenance_refs": [suite_id, *request.trace_refs, *request.evaluator_refs, *request.evidence_refs],
            },
        },
        {
            "target_id": f"shadow-eval-promotion::{request.run_id}",
            "target_type": "autonomous_update",
            "metadata": {
                "promotion_requested": request.operator_approved,
                "rollback_plan": request.baseline_ref,
                "monitoring_plan": "shadow-eval-trend-and-regression-monitoring",
            },
        },
    ]


def _shadow_finding(rule_id: str, message: str) -> dict[str, str]:
    return {"rule_id": rule_id, "severity": "hard_fail", "message": message}


def _required_controls() -> list[str]:
    return [
        "held_out_cases",
        "external_not_self_grading",
        "gaia_tau_osworld_swebench_lanes",
        "nexus_specific_eval_cases",
        "regression_free_result",
        "artifact_provenance",
        "rollback_plan",
        "trend_monitoring",
        "shadow_run_trace_refs",
        "shadow_run_external_evaluator_refs",
    ]


def _benchmark_lanes() -> list[dict[str, str]]:
    return [
        {"lane_id": "gaia", "scope": "general-agent-reasoning", "status": "cataloged"},
        {"lane_id": "tau-bench", "scope": "tool-and-user-simulation", "status": "cataloged"},
        {"lane_id": "osworld", "scope": "computer-use-and-screen-agents", "status": "cataloged"},
        {"lane_id": "swe-bench", "scope": "software-engineering", "status": "cataloged"},
        {"lane_id": "nexus-held-out", "scope": "project-specific-regression", "status": "required"},
    ]


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/eval-registry"},
        "eval_suites": {"method": "GET", "endpoint": "/ops/brain/eval-suites"},
        "register_suite": {"method": "POST", "endpoint": "/ops/brain/eval-registry/suites"},
        "run_shadow": {"method": "POST", "endpoint": "/ops/brain/eval-suites/{suite_id}/run-shadow"},
        "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/eval-registry"},
    }

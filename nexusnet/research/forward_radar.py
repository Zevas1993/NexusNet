from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow
from nexusnet.policy import PolicyKernel


SourceQuality = Literal["primary", "verified", "secondary", "unverified"]
LicenseStatus = Literal["approved", "blocked", "needs_review"]
SecurityReview = Literal["passed", "blocked", "needs_review"]


class ForwardRadarCandidateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    radar_id: str
    title: str
    lane: str
    summary: str
    source_refs: list[str] = Field(default_factory=list)
    source_quality: SourceQuality = "unverified"
    license_status: LicenseStatus = "needs_review"
    security_review: SecurityReview = "needs_review"
    runtime_evidence_refs: list[str] = Field(default_factory=list)
    eval_refs: list[str] = Field(default_factory=list)
    observability_refs: list[str] = Field(default_factory=list)
    rollback_plan: str = ""
    operator_approved: bool = False
    open_first: bool = True
    local_first: bool = True
    upstream_harness_ledger_gate: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ForwardRadarRegistry:
    def __init__(self, *, artifacts_dir: Path | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.records_dir = self.artifacts_dir / "research" / "forward-radar" if self.artifacts_dir else None
        if self.records_dir is not None:
            self.records_dir.mkdir(parents=True, exist_ok=True)
        self._memory_records: list[dict[str, Any]] = []
        self.policy_kernel = PolicyKernel.default()

    def review(self, radar_id: str, request: ForwardRadarCandidateRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, ForwardRadarCandidateRequest) else ForwardRadarCandidateRequest.model_validate(request)
        upstream_harness_ledger_gate = _upstream_harness_ledger_gate(normalized)
        review_findings = _review_findings(radar_id, normalized, upstream_harness_ledger_gate=upstream_harness_ledger_gate)
        gate_summary = _gate_summary(normalized)
        policy_scan = self.policy_kernel.scan(_policy_targets(normalized))
        hard_blocked = _has_hard_fail(review_findings)
        promotion_allowed = gate_summary["failed_gate_count"] == 0 and policy_scan.summary.active_hard_fail_count == 0 and not hard_blocked
        status = _status(normalized, promotion_allowed=promotion_allowed, hard_blocked=hard_blocked)
        record = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "forward-radar",
            "radar_id": normalized.radar_id,
            "title": normalized.title,
            "lane": normalized.lane,
            "summary": normalized.summary,
            "status": status,
            "runtime_state": "live-bound" if promotion_allowed else "research-candidate",
            "promotion_allowed": promotion_allowed,
            "created_at": utcnow().isoformat(),
            "source_refs": normalized.source_refs,
            "source_quality": normalized.source_quality,
            "license_status": normalized.license_status,
            "security_review": normalized.security_review,
            "runtime_evidence_refs": normalized.runtime_evidence_refs,
            "eval_refs": normalized.eval_refs,
            "observability_refs": normalized.observability_refs,
            "rollback_plan": normalized.rollback_plan,
            "operator_approved": normalized.operator_approved,
            "open_first": normalized.open_first,
            "local_first": normalized.local_first,
            "upstream_harness_ledger_gate": upstream_harness_ledger_gate,
            "gate_summary": gate_summary,
            "review_findings": review_findings,
            "policy_scan": policy_scan.model_dump(mode="json"),
            "promotion_boundary": "forward-radar-candidates-require-source-license-security-runtime-eval-observability-rollback-and-operator-gates",
            "operator_actions": _operator_actions(),
            "metadata": normalized.metadata,
        }
        self._persist(record)
        return record

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        records = self._list_records(limit=limit)
        promotion_ready_count = sum(1 for record in records if record.get("status") == "promotion-ready")
        watchlist_count = sum(1 for record in records if record.get("status") == "watchlist")
        blocked_count = sum(1 for record in records if record.get("status") == "blocked")
        latest_candidate = records[0] if records else None
        runtime_state = "static-canon"
        if records:
            if blocked_count or latest_candidate.get("status") == "blocked":
                runtime_state = "degraded"
            elif promotion_ready_count == len(records):
                runtime_state = "live-bound"
            else:
                runtime_state = "research-candidate"
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "forward-radar",
            "authority": "NexusBrain",
            "runtime_state": runtime_state,
            "candidate_count": len(records),
            "promotion_ready_count": promotion_ready_count,
            "watchlist_count": watchlist_count,
            "blocked_count": blocked_count,
            "latest_candidate": latest_candidate,
            "candidates": records,
            "required_gates": _required_gates(),
            "operator_actions": _operator_actions(),
        }

    def get(self, radar_id: str) -> dict[str, Any] | None:
        for record in self._list_records(limit=500):
            if record.get("radar_id") == radar_id:
                return record
        return None

    def scorecard(self) -> dict[str, Any]:
        summary = self.summary()
        return {
            **summary,
            "source_documents": [
                "docs/NEXUSNET_FORWARD_RESEARCH_RADAR_2026-04-28.md",
                "docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md",
                "docs/NEXUSNET_QUANTIZATION_AGENTIC_RESEARCH_EXPANSION_2026-04-28.md",
            ],
            "watch_items": ["TurboQuant", "LMCache", "A2A", "AG-UI", "OSWorld", "GraphRAG", "Sigstore", "WebNN"],
            "autonomy_rule": "researchers-can-discover-and-propose-but-not-promote-without-all-gates-and-operator-approval",
        }

    def _persist(self, record: dict[str, Any]) -> None:
        self._memory_records = [item for item in self._memory_records if item.get("radar_id") != record.get("radar_id")]
        self._memory_records.insert(0, record)
        self._memory_records = self._memory_records[:50]
        if self.records_dir is not None:
            safe_id = record["radar_id"].replace(":", "_").replace("/", "_")
            path = self.records_dir / f"{safe_id}.json"
            record["artifact_path"] = str(path)
            path.write_text(json.dumps(record, indent=2), encoding="utf-8")

    def _list_records(self, *, limit: int) -> list[dict[str, Any]]:
        records = list(self._memory_records)
        seen = {record.get("radar_id") for record in records}
        if self.records_dir is not None:
            for path in self.records_dir.glob("*.json"):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if payload.get("radar_id") not in seen:
                    records.append(payload)
        records.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return records[:limit]


def _review_findings(
    path_radar_id: str,
    request: ForwardRadarCandidateRequest,
    *,
    upstream_harness_ledger_gate: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    upstream_harness_ledger_gate = upstream_harness_ledger_gate or {}
    if path_radar_id != request.radar_id:
        findings.append(_finding("forward_radar_path_id_mismatch", "Path radar_id must match request radar_id."))
    if not request.source_refs or request.source_quality not in {"primary", "verified"}:
        findings.append(_finding("forward_radar_requires_primary_or_verified_source", "Forward Radar candidates require primary or verified source evidence."))
    if request.license_status != "approved":
        findings.append(_finding("forward_radar_requires_approved_license", "Forward Radar candidates require approved license posture before promotion."))
    if request.security_review != "passed":
        findings.append(_finding("forward_radar_requires_security_review", "Forward Radar candidates require a passed security review."))
    if not request.runtime_evidence_refs:
        findings.append(_finding("forward_radar_requires_runtime_evidence", "Forward Radar candidates require runtime or hardware evidence."))
    if not request.eval_refs:
        findings.append(_finding("forward_radar_requires_eval_refs", "Forward Radar candidates require eval or regression evidence."))
    if not request.observability_refs:
        findings.append(_finding("forward_radar_requires_observability_refs", "Forward Radar candidates require trace or observability evidence."))
    if not request.rollback_plan.strip():
        findings.append(_finding("forward_radar_requires_rollback_plan", "Forward Radar candidates require a rollback or demotion plan."))
    if not request.operator_approved:
        findings.append(_finding("forward_radar_requires_operator_approval", "Forward Radar candidates require operator approval before promotion."))
    if upstream_harness_ledger_gate.get("promotion_allowed") is False or upstream_harness_ledger_gate.get("status") == "blocked":
        findings.append(_finding("forward_radar_blocks_harness_ledger_gate", "Forward Radar candidates cannot become promotion-ready while upstream harness-ledger evidence is blocked.", severity="hard_fail"))
    upstream_self_review_gate = upstream_harness_ledger_gate.get("upstream_self_review_gate") or {}
    if upstream_self_review_gate.get("status") == "blocked" or upstream_self_review_gate.get("review_state") == "blocked-by-review":
        findings.append(_finding("forward_radar_blocks_upstream_self_review_gate", "Forward Radar candidates cannot become promotion-ready while upstream self-review is blocked.", severity="hard_fail"))
    upstream_eval_gate = upstream_self_review_gate.get("upstream_eval_gate") or {}
    if upstream_eval_gate.get("promotion_allowed") is False:
        findings.append(_finding("forward_radar_blocks_upstream_eval_gate", "Forward Radar candidates cannot become promotion-ready while upstream eval evidence is blocked.", severity="hard_fail"))
    upstream_lifecycle_gate = upstream_eval_gate.get("upstream_lifecycle_gate") or {}
    if upstream_lifecycle_gate.get("lifecycle_status") == "closed_loop_blocked":
        findings.append(_finding("forward_radar_blocks_upstream_lifecycle_gate", "Forward Radar candidates cannot become promotion-ready while upstream lifecycle evidence is blocked.", severity="hard_fail"))
    return findings


def _upstream_harness_ledger_gate(request: ForwardRadarCandidateRequest) -> dict[str, Any]:
    gate = request.upstream_harness_ledger_gate or {}
    self_review_gate = gate.get("upstream_self_review_gate") or {}
    eval_gate = self_review_gate.get("upstream_eval_gate") or {}
    lifecycle_gate = eval_gate.get("upstream_lifecycle_gate") or {}
    blockers = [str(item) for item in gate.get("blockers") or []]
    blockers.extend(str(item) for item in self_review_gate.get("blockers") or [])
    blockers.extend(str(item) for item in eval_gate.get("blockers") or [])
    blockers.extend(str(item) for item in lifecycle_gate.get("blockers") or [])
    return {
        "promotion_allowed": gate.get("promotion_allowed"),
        "status": gate.get("status") or "not_provided",
        "entry_id": gate.get("entry_id") or "",
        "blockers": sorted(set(blockers)),
        "upstream_self_review_gate": {
            **self_review_gate,
            "blockers": sorted(
                set(
                    [str(item) for item in self_review_gate.get("blockers") or []]
                    + [str(item) for item in eval_gate.get("blockers") or []]
                    + [str(item) for item in lifecycle_gate.get("blockers") or []]
                )
            ),
            "upstream_eval_gate": {
                **eval_gate,
                "blockers": sorted(set([str(item) for item in eval_gate.get("blockers") or []] + [str(item) for item in lifecycle_gate.get("blockers") or []])),
                "upstream_lifecycle_gate": lifecycle_gate,
            },
        },
        "source": gate.get("source") or "harness_improvement_ledger",
    }


def _gate_summary(request: ForwardRadarCandidateRequest) -> dict[str, Any]:
    gates = {
        "source": bool(request.source_refs and request.source_quality in {"primary", "verified"}),
        "license": request.license_status == "approved",
        "security": request.security_review == "passed",
        "runtime": bool(request.runtime_evidence_refs),
        "eval": bool(request.eval_refs),
        "observability": bool(request.observability_refs),
        "rollback": bool(request.rollback_plan.strip()),
        "operator": request.operator_approved,
    }
    return {
        "gates": gates,
        "passed_gate_count": sum(1 for passed in gates.values() if passed),
        "failed_gate_count": sum(1 for passed in gates.values() if not passed),
    }


def _policy_targets(request: ForwardRadarCandidateRequest) -> list[dict[str, Any]]:
    return [
        {
            "target_id": f"forward-radar::{request.radar_id}",
            "target_type": "artifact",
            "metadata": {
                "promotion_requested": request.operator_approved,
                "license_state": "approved" if request.license_status == "approved" else None,
                "provenance_refs": request.source_refs,
            },
        },
        {
            "target_id": f"forward-radar-update::{request.radar_id}",
            "target_type": "autonomous_update",
            "metadata": {
                "promotion_requested": request.operator_approved,
                "rollback_plan": request.rollback_plan,
                "monitoring_plan": "forward-radar-shadow-review-and-eval-monitoring",
            },
        },
    ]


def _status(request: ForwardRadarCandidateRequest, *, promotion_allowed: bool, hard_blocked: bool = False) -> str:
    if hard_blocked:
        return "blocked"
    if request.license_status == "blocked" or request.security_review == "blocked":
        return "blocked"
    if promotion_allowed:
        return "promotion-ready"
    return "watchlist"


def _finding(rule_id: str, message: str, severity: str = "gate_missing") -> dict[str, str]:
    return {"rule_id": rule_id, "severity": severity, "message": message}


def _has_hard_fail(findings: list[dict[str, str]]) -> bool:
    return any(finding.get("severity") == "hard_fail" for finding in findings)


def _required_gates() -> list[str]:
    return ["source", "license", "security", "runtime", "eval", "observability", "rollback", "operator"]


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/forward-radar"},
        "candidate": {"method": "GET", "endpoint": "/ops/brain/forward-radar/{radar_id}"},
        "review": {"method": "POST", "endpoint": "/ops/brain/forward-radar/{radar_id}/review"},
        "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/forward-radar"},
    }

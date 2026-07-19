from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


Severity = Literal["hard_fail", "warning"]


class PolicyTarget(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_id: str
    target_type: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class PolicyWaiver(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_id: str
    target_id: str
    approved_by: str
    reason: str
    expires_at: datetime

    @property
    def waiver_id(self) -> str:
        return f"waiver::{self.rule_id}::{self.target_id}"

    def is_active(self, *, now: datetime | None = None) -> bool:
        now = now or datetime.now(timezone.utc)
        expires_at = self.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return bool(self.approved_by.strip() and self.reason.strip() and expires_at > now)


class PolicyRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_id: str
    title: str
    severity: Severity
    target_types: list[str]
    description: str
    required_evidence: list[str] = Field(default_factory=list)
    promotion_gate: str


class PolicyFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    finding_id: str
    rule_id: str
    target_id: str
    target_type: str
    severity: Severity
    message: str
    blocked: bool
    waived: bool = False
    waiver_ref: str | None = None
    required_evidence: list[str] = Field(default_factory=list)
    promotion_gate: str


class PolicyScanSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_count: int
    finding_count: int
    hard_fail_count: int
    warning_count: int
    waived_count: int
    active_hard_fail_count: int
    active_warning_count: int
    allow_merge: bool


class PolicyScanReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status_label: str = "LOCKED CANON"
    authority: str = "NexusBrain"
    policy_boundary: str = "deterministic-floor-under-agentic-work"
    summary: PolicyScanSummary
    findings: list[PolicyFinding] = Field(default_factory=list)
    rules: list[PolicyRule] = Field(default_factory=list)


class PolicyScanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    targets: list[PolicyTarget]
    waivers: list[PolicyWaiver] = Field(default_factory=list)


class PolicyKernel:
    def __init__(self, rules: list[PolicyRule]) -> None:
        self.rules = rules

    @classmethod
    def default(cls) -> "PolicyKernel":
        return cls(
            [
                PolicyRule(
                    rule_id="training_candidate_requires_operator_approval",
                    title="Training candidates using private data require operator approval",
                    severity="hard_fail",
                    target_types=["training_candidate"],
                    description="Blocks adapter or fine-tune candidates that include private/user data without explicit approval.",
                    required_evidence=["privacy_classification", "operator_approval"],
                    promotion_gate="privacy-license-human-review",
                ),
                PolicyRule(
                    rule_id="training_candidate_requires_eval_gate",
                    title="Training candidates require eval evidence before promotion",
                    severity="hard_fail",
                    target_types=["training_candidate"],
                    description="Blocks promotion of adapter or fine-tune candidates without held-out eval evidence.",
                    required_evidence=["eval_refs", "regression_gate"],
                    promotion_gate="adapter-eval-regression-gate",
                ),
                PolicyRule(
                    rule_id="memory_update_requires_provenance",
                    title="Memory updates require provenance",
                    severity="hard_fail",
                    target_types=["memory_update"],
                    description="Blocks memory promotion when source-to-claim provenance is missing.",
                    required_evidence=["provenance_refs"],
                    promotion_gate="source-to-claim-map",
                ),
                PolicyRule(
                    rule_id="canon_claim_requires_verified_source_status",
                    title="Canon claims require verified source status",
                    severity="hard_fail",
                    target_types=["claim"],
                    description="Blocks canon claim promotion when source status is not primary or secondary verified.",
                    required_evidence=["source_status", "source_refs"],
                    promotion_gate="synthetic-truth-guard",
                ),
                PolicyRule(
                    rule_id="write_tool_requires_sandbox",
                    title="Write-enabled tools require sandboxing",
                    severity="hard_fail",
                    target_types=["tool_execution"],
                    description="Blocks write-enabled tool execution unless a sandbox or equivalent isolation boundary is active.",
                    required_evidence=["sandbox_state", "tool_scope"],
                    promotion_gate="sandbox-permission-audit",
                ),
                PolicyRule(
                    rule_id="protocol_adapter_requires_trust_envelope",
                    title="Protocol adapters require trust envelopes",
                    severity="hard_fail",
                    target_types=["protocol_adapter"],
                    description="Blocks enabled MCP/A2A/ACP/AG-UI style adapters without identity, consent, permissions, and revocation.",
                    required_evidence=["identity", "consent", "permissions", "revocation"],
                    promotion_gate="protocol-trust-envelope",
                ),
                PolicyRule(
                    rule_id="artifact_requires_license_and_provenance",
                    title="Promoted artifacts require license and provenance evidence",
                    severity="hard_fail",
                    target_types=["artifact"],
                    description="Blocks artifact promotion when provenance or license posture is missing.",
                    required_evidence=["artifact_provenance", "license_state"],
                    promotion_gate="artifact-trust-review",
                ),
                PolicyRule(
                    rule_id="code_change_requires_tests",
                    title="Code changes require verification evidence",
                    severity="warning",
                    target_types=["code_change"],
                    description="Warns when code changes do not declare a targeted verification or test path.",
                    required_evidence=["tests_provided"],
                    promotion_gate="verification-before-completion",
                ),
                PolicyRule(
                    rule_id="code_change_requires_codegraph_manifest",
                    title="Code changes require codegraph manifest evidence",
                    severity="hard_fail",
                    target_types=["code_change"],
                    description="Blocks code-affecting changes that do not carry GitNexus graph, impact, and detect-changes evidence.",
                    required_evidence=["codegraph_manifest_ref"],
                    promotion_gate="codegraph-required-context-gate",
                ),
                PolicyRule(
                    rule_id="autonomous_update_requires_rollback",
                    title="Autonomous updates require rollback plans",
                    severity="hard_fail",
                    target_types=["autonomous_update"],
                    description="Blocks autonomous promotion without rollback evidence and monitored deployment state.",
                    required_evidence=["rollback_plan", "monitoring_plan"],
                    promotion_gate="shadow-promote-monitor-rollback",
                ),
            ]
        )

    def rules_payload(self) -> dict[str, Any]:
        return {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "policy_boundary": "deterministic-floor-under-agentic-work",
            "rule_count": len(self.rules),
            "rules": [rule.model_dump(mode="json") for rule in self.rules],
            "operator_actions": {
                "policy_scan": {
                    "method": "POST",
                    "endpoint": "/ops/brain/policy/scan",
                    "body": {"targets": [], "waivers": []},
                },
                "policy_scorecard": {
                    "method": "GET",
                    "endpoint": "/ops/brain/canon/policy-kernel",
                },
            },
        }

    def scorecard(self) -> dict[str, Any]:
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "governance-observability",
            "authority": "NexusBrain",
            "policy_kernel_state": "live-bound",
            "policy_boundary": "deterministic-floor-under-agentic-work",
            "required_controls": [
                "deterministic_floor_under_agentic_work",
                "machine_readable_rules",
                "hard_fail_warning_tiers",
                "waiver_ledger",
                "policy_scan_report",
                "promotion_gate_mapping",
                "audit_visibility",
            ],
            "default_rule_count": len(self.rules),
            "rule_families": sorted({target_type for rule in self.rules for target_type in rule.target_types}),
            "promotion_rule": "policy findings must be resolved, waived with expiry, or blocked before autonomous promotion",
            "operator_actions": {
                "rules": {"method": "GET", "endpoint": "/ops/brain/policy/rules"},
                "scan": {"method": "POST", "endpoint": "/ops/brain/policy/scan"},
            },
        }

    def authorize_plan_write(self, target_path: str) -> dict[str, Any]:
        normalized_path = target_path.replace("\\", "/").lstrip("/")
        allowed_prefixes = ("docs/superpowers/plans/", "docs/superpowers/specs/")
        allowed = (
            ".." not in normalized_path.split("/")
            and any(normalized_path.startswith(prefix) for prefix in allowed_prefixes)
        )
        return {
            "plan_mode": True,
            "target_path": normalized_path,
            "allowed": allowed,
            "reason": "plan_artifact_allowlist" if allowed else "plan_mode_repo_write_blocked",
            "allowed_prefixes": list(allowed_prefixes),
        }

    def scan(
        self,
        targets: list[PolicyTarget | dict[str, Any]],
        *,
        waivers: list[PolicyWaiver | dict[str, Any]] | None = None,
    ) -> PolicyScanReport:
        normalized_targets = [target if isinstance(target, PolicyTarget) else PolicyTarget.model_validate(target) for target in targets]
        normalized_waivers = [
            waiver if isinstance(waiver, PolicyWaiver) else PolicyWaiver.model_validate(waiver)
            for waiver in (waivers or [])
        ]
        findings: list[PolicyFinding] = []
        for target in normalized_targets:
            for rule in self.rules:
                if target.target_type not in rule.target_types:
                    continue
                message = self._evaluate_rule(rule, target)
                if not message:
                    continue
                waiver = self._matching_waiver(rule, target, normalized_waivers)
                waived = bool(waiver)
                findings.append(
                    PolicyFinding(
                        finding_id=f"finding::{rule.rule_id}::{target.target_id}",
                        rule_id=rule.rule_id,
                        target_id=target.target_id,
                        target_type=target.target_type,
                        severity=rule.severity,
                        message=message,
                        blocked=rule.severity == "hard_fail" and not waived,
                        waived=waived,
                        waiver_ref=waiver.waiver_id if waiver else None,
                        required_evidence=list(rule.required_evidence),
                        promotion_gate=rule.promotion_gate,
                    )
                )

        hard_fail_count = sum(1 for finding in findings if finding.severity == "hard_fail")
        warning_count = sum(1 for finding in findings if finding.severity == "warning")
        waived_count = sum(1 for finding in findings if finding.waived)
        active_hard_fail_count = sum(1 for finding in findings if finding.severity == "hard_fail" and not finding.waived)
        active_warning_count = sum(1 for finding in findings if finding.severity == "warning" and not finding.waived)
        return PolicyScanReport(
            summary=PolicyScanSummary(
                target_count=len(normalized_targets),
                finding_count=len(findings),
                hard_fail_count=hard_fail_count,
                warning_count=warning_count,
                waived_count=waived_count,
                active_hard_fail_count=active_hard_fail_count,
                active_warning_count=active_warning_count,
                allow_merge=active_hard_fail_count == 0,
            ),
            findings=findings,
            rules=list(self.rules),
        )

    def _matching_waiver(
        self,
        rule: PolicyRule,
        target: PolicyTarget,
        waivers: list[PolicyWaiver],
    ) -> PolicyWaiver | None:
        for waiver in waivers:
            if waiver.rule_id == rule.rule_id and waiver.target_id == target.target_id and waiver.is_active():
                return waiver
        return None

    def _evaluate_rule(self, rule: PolicyRule, target: PolicyTarget) -> str | None:
        metadata = target.metadata
        if rule.rule_id == "training_candidate_requires_operator_approval":
            if (metadata.get("contains_private_data") or metadata.get("uses_user_data")) and not metadata.get("operator_approved"):
                return "Training candidate uses private/user data without explicit operator approval."
        if rule.rule_id == "training_candidate_requires_eval_gate":
            if metadata.get("promotion_requested") and not metadata.get("eval_refs"):
                return "Training candidate promotion requested without eval references."
        if rule.rule_id == "memory_update_requires_provenance":
            if not metadata.get("provenance_refs"):
                return "Memory update is missing source-to-claim provenance references."
        if rule.rule_id == "canon_claim_requires_verified_source_status":
            if metadata.get("promotion_requested") and metadata.get("source_status") not in {
                "primary_verified",
                "secondary_verified",
            }:
                return "Canon claim promotion requested without verified source status."
        if rule.rule_id == "write_tool_requires_sandbox":
            if metadata.get("write_enabled") and not metadata.get("sandboxed"):
                return "Write-enabled tool execution is missing an active sandbox boundary."
        if rule.rule_id == "protocol_adapter_requires_trust_envelope":
            if metadata.get("enabled") and not metadata.get("trust_envelope"):
                return "Enabled protocol adapter is missing a trust envelope."
        if rule.rule_id == "artifact_requires_license_and_provenance":
            if metadata.get("promotion_requested") and (
                not metadata.get("license_state") or not metadata.get("provenance_refs")
            ):
                return "Artifact promotion requested without license and provenance evidence."
        if rule.rule_id == "code_change_requires_tests":
            if not metadata.get("tests_provided"):
                return "Code change does not declare targeted verification evidence."
        if rule.rule_id == "code_change_requires_codegraph_manifest":
            if not metadata.get("codegraph_manifest_ref"):
                return "Code change is missing codegraph manifest evidence."
        if rule.rule_id == "autonomous_update_requires_rollback":
            if metadata.get("promotion_requested") and (
                not metadata.get("rollback_plan") or not metadata.get("monitoring_plan")
            ):
                return "Autonomous update promotion requested without rollback and monitoring plans."
        return None

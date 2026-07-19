from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow
from nexusnet.policy import PolicyKernel


AutonomousUpdateType = Literal["memory", "prompt_policy", "adapter", "quantization", "runtime", "protocol", "tool"]
AutonomousUpdateState = Literal["proposal", "shadow", "canary", "active"]
SAFE_APPLY_REQUIRED_AO_GUARD_AOS = ("AdminAO", "GovernanceAO", "SecurityAO", "EvalsAO")


class AutonomousUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    update_id: str
    update_type: AutonomousUpdateType
    target_ref: str
    requested_state: AutonomousUpdateState = "proposal"
    eval_refs: list[str] = Field(default_factory=list)
    target_surfaces: list[str] = Field(default_factory=list)
    artifact_trust_refs: list[str] = Field(default_factory=list)
    rollback_plan: str = ""
    monitoring_plan: str = ""
    operator_approved: bool = False
    sandbox_ref: str = ""
    upstream_eval_gate: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AutonomousUpdateController:
    def __init__(self, *, artifacts_dir: Path | None = None):
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.proposals_dir = self.artifacts_dir / "autonomous-updates" / "proposals" if self.artifacts_dir else None
        self.approvals_dir = self.artifacts_dir / "autonomous-updates" / "approvals" if self.artifacts_dir else None
        self.applied_dir = self.artifacts_dir / "autonomous-updates" / "applied" if self.artifacts_dir else None
        self.safe_files_dir = self.artifacts_dir / "autonomous-updates" / "safe-files" if self.artifacts_dir else None
        self.rollbacks_dir = self.artifacts_dir / "autonomous-updates" / "rollbacks" if self.artifacts_dir else None
        self.test_evidence_dir = self.artifacts_dir / "autonomous-updates" / "test-evidence" if self.artifacts_dir else None
        self.sandboxes_dir = self.artifacts_dir / "autonomous-updates" / "sandboxes" if self.artifacts_dir else None
        if self.proposals_dir is not None:
            self.proposals_dir.mkdir(parents=True, exist_ok=True)
        for directory in (
            self.approvals_dir,
            self.applied_dir,
            self.safe_files_dir,
            self.rollbacks_dir,
            self.test_evidence_dir,
            self.sandboxes_dir,
        ):
            if directory is not None:
                directory.mkdir(parents=True, exist_ok=True)
        self._memory_proposals: list[dict[str, Any]] = []
        self._memory_approvals: list[dict[str, Any]] = []
        self._memory_applied: list[dict[str, Any]] = []
        self._memory_rollbacks: list[dict[str, Any]] = []
        self._memory_test_evidence: list[dict[str, Any]] = []
        self._proposal_cache: list[dict[str, Any]] | None = None
        self.policy_kernel = PolicyKernel.default()

    def propose(self, request: AutonomousUpdateRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, AutonomousUpdateRequest) else AutonomousUpdateRequest.model_validate(request)
        # Proposal input cannot grant the operator approval required for execution.
        normalized = normalized.model_copy(update={"operator_approved": False})
        upstream_eval_gate = _upstream_eval_gate(normalized)
        update_findings = _update_findings(normalized, upstream_eval_gate=upstream_eval_gate)
        policy_scan = self.policy_kernel.scan(_policy_targets(normalized))
        blocked = bool(update_findings) or policy_scan.summary.active_hard_fail_count > 0
        proposal = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "autonomous-updates",
            "update_id": normalized.update_id,
            "update_type": normalized.update_type,
            "target_ref": normalized.target_ref,
            "requested_state": normalized.requested_state,
            "status": _status_for(normalized, blocked=blocked),
            "promotion_state": _promotion_state(normalized, blocked=blocked),
            "created_at": utcnow().isoformat(),
            "eval_refs": normalized.eval_refs,
            "target_surfaces": _dedupe_refs(normalized.target_surfaces),
            "artifact_trust_refs": normalized.artifact_trust_refs,
            "rollback_plan": normalized.rollback_plan,
            "monitoring_plan": normalized.monitoring_plan,
            "operator_approved": normalized.operator_approved,
            "sandbox_ref": normalized.sandbox_ref,
            "upstream_eval_gate": upstream_eval_gate,
            "gate_summary": {
                "all_required_gates_present": not blocked,
                "eval_gate": bool(normalized.eval_refs),
                "eval_promotion_gate": upstream_eval_gate["promotion_allowed"] is not False,
                "artifact_trust_gate": bool(normalized.artifact_trust_refs),
                "rollback": bool(normalized.rollback_plan.strip()),
                "monitoring": bool(normalized.monitoring_plan.strip()),
                "operator_approval": normalized.operator_approved,
                "sandbox": bool(normalized.sandbox_ref.strip()),
            },
            "required_controls": _required_controls(),
            "update_findings": update_findings,
            "policy_scan": policy_scan.model_dump(mode="json"),
            "metadata": normalized.metadata,
        }
        self._persist(proposal)
        return proposal

    def approve(
        self,
        update_id: str,
        *,
        approved_by: str = "",
        approval_ref: str = "",
        approval_evidence: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        proposal = self._find_proposal(update_id)
        bound_approval = _bound_admin_approval_evidence(update_id, approval_evidence)
        evidence_gate = _admin_approval_evidence_gate(proposal)
        approval = {
            "status_label": "LOCKED CANON",
            "surface_id": "autonomous-updates",
            "update_id": update_id,
            "status": "admin-approved",
            "approval_ref": bound_approval["approval_ref"],
            "approval_subject": bound_approval["approval_subject"],
            "approved_update_id": bound_approval["approved_update_id"],
            "approver_digest": bound_approval["approver_digest"],
            "rationale_digest": bound_approval["rationale_digest"],
            "metadata_digest": bound_approval["metadata_digest"],
            "approved_at": utcnow().isoformat(),
            "operator_approved": True,
            "active_production_mutated": False,
            "next_action": "apply-safe-artifact",
            "evidence_gate": evidence_gate,
        }
        proposal["operator_approved"] = True
        proposal["status"] = "admin-approved"
        proposal["promotion_state"] = "admin-approved-pending-safe-apply"
        proposal["admin_approval"] = approval
        self._persist(proposal)
        self._persist_record(approval, self.approvals_dir, self._memory_approvals, suffix="approval")
        return approval

    def attach_eval_replay(self, update_id: str, eval_replay: dict[str, Any]) -> dict[str, Any]:
        proposal = self._find_proposal(update_id)
        evidence_refs = [str(ref) for ref in (eval_replay.get("evidence_refs") or []) if str(ref or "")]
        evaluator_refs = [str(ref) for ref in (eval_replay.get("evaluator_refs") or []) if str(ref or "")]
        metadata = eval_replay.get("metadata") if isinstance(eval_replay.get("metadata"), dict) else {}
        compact = {
            "run_id": eval_replay.get("run_id"),
            "suite_id": eval_replay.get("suite_id"),
            "status": eval_replay.get("status"),
            "promotion_allowed": bool(eval_replay.get("promotion_allowed")),
            "operator_approved": bool(eval_replay.get("operator_approved")),
            "evidence_refs": evidence_refs,
            "evaluator_refs": evaluator_refs,
            "artifact_gate_refs": _artifact_gate_refs_from_replay(
                {"evidence_refs": evidence_refs, "evaluator_refs": evaluator_refs, "metadata": metadata}
            ),
            "metadata": metadata,
        }
        proposal["latest_eval_replay"] = compact
        proposal["upstream_eval_gate"] = {
            "promotion_allowed": compact["promotion_allowed"],
            "shadow_run_ref": compact["run_id"],
            "suite_id": compact["suite_id"],
            "status": compact["status"],
            "blockers": [finding.get("rule_id") for finding in (eval_replay.get("shadow_findings") or [])],
        }
        proposal["gate_summary"]["eval_promotion_gate"] = compact["promotion_allowed"]
        self._persist(proposal)
        return compact

    def apply_safe(
        self,
        update_id: str,
        *,
        test_refs: list[str] | None = None,
        test_results: list[dict[str, Any]] | None = None,
        test_evidence_refs: list[str] | None = None,
        ao_guard: dict[str, Any] | None = None,
        immune_governance_decision_id: str | None = None,
    ) -> dict[str, Any]:
        proposal = self._find_proposal(update_id)
        if not _proposal_has_bound_admin_approval(proposal):
            raise ValueError("stored admin approval bound to this update is required before safe apply")
        rollback_plan = str(proposal.get("rollback_plan") or "").strip()
        if not rollback_plan:
            raise ValueError("rollback plan is required before safe apply")
        if proposal.get("update_type") not in {"prompt_policy", "runtime"}:
            raise ValueError("safe apply is limited to prompt_policy and runtime updates")
        if not str(proposal.get("target_ref") or "").startswith("safe-artifact::"):
            raise ValueError("safe apply target_ref must start with safe-artifact::")
        evidence_results = self._test_results_from_evidence_refs(test_evidence_refs)
        normalized_test_results = [*evidence_results, *_normalize_test_results(test_results)]
        if not _test_evidence_passed(evidence_results):
            raise ValueError("passing isolated sandbox test evidence is required before safe apply")
        if _requires_shadow_eval_replay(proposal) and not _shadow_eval_replay_passed(
            proposal.get("latest_eval_replay"), proposal=proposal
        ):
            raise ValueError("artifact-backed passed shadow eval replay evidence is required before release-wrapper safe apply")
        ao_guard_summary = _safe_apply_ao_guard_summary(ao_guard)
        immune_governance = getattr(self, "immune_governance", None)
        immune_decision = (
            immune_governance.require_decision(
                decision_id=immune_governance_decision_id,
                candidate_ref=update_id,
                candidate_kind="autonomous-update-safe-apply",
            )
            if immune_governance is not None
            else None
        )

        safe_file_path = self._safe_file_path(update_id)
        previous_content = safe_file_path.read_text(encoding="utf-8") if safe_file_path.exists() else None
        safe_payload = ((proposal.get("metadata") or {}).get("safe_payload") or {})
        safe_record = {
            "schema_version": "autonomous_update_safe_file.v0.1",
            "update_id": update_id,
            "target_ref": proposal.get("target_ref"),
            "safe_payload": safe_payload,
            "active_production_mutated": False,
            "test_results": normalized_test_results,
            "immune_governance_decision": immune_decision,
            **ao_guard_summary,
            "applied_at": utcnow().isoformat(),
        }
        safe_file_path.write_text(json.dumps(safe_record, indent=2, sort_keys=True), encoding="utf-8")
        applied = {
            "status_label": "LOCKED CANON",
            "surface_id": "autonomous-updates",
            "update_id": update_id,
            "status": "applied-shadow-safe-file",
            "safe_file_path": str(safe_file_path),
            "rollback_plan": rollback_plan,
            "previous_content": previous_content,
            "test_refs": list(test_refs or []),
            "test_evidence_refs": list(test_evidence_refs or []),
            "test_results": normalized_test_results,
            "immune_governance_decision": immune_decision,
            "active_production_mutated": False,
            **ao_guard_summary,
            "applied_at": safe_record["applied_at"],
        }
        proposal["status"] = "applied-shadow-safe-file"
        proposal["promotion_state"] = "shadow-safe-file-applied"
        proposal["latest_apply"] = {k: v for k, v in applied.items() if k != "previous_content"}
        self._persist(proposal)
        self._persist_record(applied, self.applied_dir, self._memory_applied, suffix="applied")
        return {k: v for k, v in applied.items() if k != "previous_content"}

    def rollback(self, update_id: str, *, reason: str) -> dict[str, Any]:
        applied = self._find_applied(update_id)
        safe_file_path = Path(str(applied.get("safe_file_path") or self._safe_file_path(update_id)))
        previous_content = applied.get("previous_content")
        if previous_content is None:
            if safe_file_path.exists():
                safe_file_path.unlink()
            rollback_restored = True
        else:
            safe_file_path.write_text(str(previous_content), encoding="utf-8")
            rollback_restored = True
        rollback = {
            "status_label": "LOCKED CANON",
            "surface_id": "autonomous-updates",
            "update_id": update_id,
            "status": "rolled-back",
            "reason": reason,
            "safe_file_path": str(safe_file_path),
            "rollback_restored": rollback_restored,
            "active_production_mutated": False,
            "rolled_back_at": utcnow().isoformat(),
        }
        try:
            proposal = self._find_proposal(update_id)
            proposal["status"] = "rolled-back"
            proposal["promotion_state"] = "rolled-back-to-previous-safe-file"
            proposal["latest_rollback"] = rollback
            self._persist(proposal)
        except KeyError:
            pass
        self._persist_record(rollback, self.rollbacks_dir, self._memory_rollbacks, suffix="rollback")
        return rollback

    def run_sandbox_tests(
        self,
        update_id: str,
        *,
        command: str,
        project_root: Path | str,
        timeout_seconds: int = 60,
    ) -> dict[str, Any]:
        if self.test_evidence_dir is None:
            raise ValueError("sandbox test execution requires an artifacts_dir")
        proposal = self._find_proposal(update_id)
        if not _proposal_has_bound_admin_approval(proposal):
            raise ValueError("stored admin approval bound to this update is required before sandbox test execution")
        root = Path(project_root).resolve()
        _allowlisted_pytest_argv(command, project_root=root)
        bounded_timeout = max(1, min(int(timeout_seconds or 60), 120))
        started_at = utcnow().isoformat()
        run_id = hashlib.sha256(f"{update_id}|{command}|{started_at}".encode("utf-8")).hexdigest()[:16]
        artifact_run_root = self._sandbox_run_root(update_id, run_id)
        sandbox_workspace = _sandbox_workspace_root(update_id, run_id)
        if artifact_run_root.exists():
            shutil.rmtree(artifact_run_root)
        if sandbox_workspace.exists():
            shutil.rmtree(sandbox_workspace)
        artifact_run_root.mkdir(parents=True, exist_ok=True)
        phase_timings: dict[str, float] = {}
        phase_status_path = artifact_run_root / "phase-status.json"

        def mark_phase(phase: str) -> None:
            phase_status_path.write_text(
                json.dumps(
                    {
                        "schema_version": "autonomous_update_sandbox_phase_status.v0.1",
                        "update_id": update_id,
                        "run_id": run_id,
                        "phase": phase,
                        "phase_timings": phase_timings,
                        "updated_at": utcnow().isoformat(),
                    },
                    indent=2,
                    sort_keys=True,
                ),
                encoding="utf-8",
            )

        phase_started = time.perf_counter()
        mark_phase("copy-workspace")
        shutil.copytree(root, sandbox_workspace, ignore=_sandbox_copy_ignore)
        phase_timings["copy_seconds"] = round(time.perf_counter() - phase_started, 4)
        phase_started = time.perf_counter()
        mark_phase("pre-manifest")
        pre_manifest = _file_manifest(sandbox_workspace)
        phase_timings["pre_manifest_seconds"] = round(time.perf_counter() - phase_started, 4)
        active_evidence_prefixes = list(SANDBOX_ACTIVE_MANIFEST_EXCLUDED_PREFIXES)
        phase_started = time.perf_counter()
        mark_phase("active-pre-manifest")
        active_pre_manifest = _file_manifest(
            root,
            exclude_prefixes=active_evidence_prefixes,
            include_root_dirs=SANDBOX_ROOT_SOURCE_DIRS,
        )
        phase_timings["active_pre_manifest_seconds"] = round(time.perf_counter() - phase_started, 4)
        pre_manifest_path = artifact_run_root / "pre-manifest.json"
        pre_manifest_path.write_text(json.dumps(_manifest_payload(pre_manifest, root=sandbox_workspace), indent=2, sort_keys=True), encoding="utf-8")
        argv = _allowlisted_pytest_argv(command, project_root=sandbox_workspace)
        sandbox_environment = _sandbox_subprocess_environment(sandbox_workspace)
        phase_started = time.perf_counter()
        mark_phase("pytest")
        try:
            completed = subprocess.run(
                argv,
                cwd=sandbox_workspace,
                capture_output=True,
                text=True,
                timeout=bounded_timeout,
                shell=False,
                env=sandbox_environment,
            )
            returncode = int(completed.returncode)
            stdout = completed.stdout or ""
            stderr = completed.stderr or ""
            timed_out = False
        except subprocess.TimeoutExpired as exc:
            returncode = 124
            stdout = str(exc.stdout or "")
            stderr = str(exc.stderr or "")
            timed_out = True
        phase_timings["pytest_seconds"] = round(time.perf_counter() - phase_started, 4)

        phase_started = time.perf_counter()
        mark_phase("post-manifest")
        post_manifest = _file_manifest(sandbox_workspace)
        phase_timings["post_manifest_seconds"] = round(time.perf_counter() - phase_started, 4)
        phase_started = time.perf_counter()
        mark_phase("active-post-manifest")
        active_post_manifest = _file_manifest(
            root,
            exclude_prefixes=active_evidence_prefixes,
            include_root_dirs=SANDBOX_ROOT_SOURCE_DIRS,
        )
        phase_timings["active_post_manifest_seconds"] = round(time.perf_counter() - phase_started, 4)
        phase_started = time.perf_counter()
        mark_phase("diff")
        diff_summary = _manifest_diff(pre_manifest, post_manifest)
        unsafe_changes = [
            change
            for change in diff_summary["changes"]
            if not _allowed_sandbox_change(str(change.get("path") or ""))
        ]
        diff_summary["unsafe_change_count"] = len(unsafe_changes)
        diff_summary["unsafe_changes"] = unsafe_changes[:20]
        diff_summary["allowed_change_count"] = diff_summary["changed_file_count"] - len(unsafe_changes)
        active_diff_summary = _manifest_diff(active_pre_manifest, active_post_manifest)
        active_project_mutated = active_diff_summary["changed_file_count"] > 0
        post_manifest_path = artifact_run_root / "post-manifest.json"
        diff_path = artifact_run_root / "diff.json"
        post_manifest_path.write_text(json.dumps(_manifest_payload(post_manifest, root=sandbox_workspace), indent=2, sort_keys=True), encoding="utf-8")
        diff_path.write_text(
            json.dumps(
                {
                    "schema_version": "autonomous_update_sandbox_diff.v0.1",
                    "diff_summary": diff_summary,
                    "active_project_diff_summary": active_diff_summary,
                },
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        phase_timings["diff_seconds"] = round(time.perf_counter() - phase_started, 4)
        mark_phase("evidence")

        passed = returncode == 0 and not timed_out and not unsafe_changes and not active_project_mutated
        completed_at = utcnow().isoformat()
        evidence_ref = f"sandbox-test::{_safe_id(update_id)}::{run_id}"
        failure_count = 0
        if not passed:
            failure_count = max(
                1,
                (0 if returncode == 0 and not timed_out else 1)
                + len(unsafe_changes)
                + (1 if active_project_mutated else 0),
            )
        evidence = {
            "schema_version": "autonomous_update_sandbox_test_evidence.v0.1",
            "status_label": "LOCKED CANON",
            "surface_id": "autonomous-updates",
            "update_id": update_id,
            "evidence_ref": evidence_ref,
            "command": str(command),
            "argv": argv,
            "status": "passed" if passed else "failed",
            "passed": passed,
            "returncode": returncode,
            "failure_count": failure_count,
            "timed_out": timed_out,
            "started_at": started_at,
            "completed_at": completed_at,
            "stdout_tail": stdout[-4000:],
            "stderr_tail": stderr[-4000:],
            "pre_manifest_path": str(pre_manifest_path),
            "post_manifest_path": str(post_manifest_path),
            "diff_path": str(diff_path),
            "phase_status_path": str(phase_status_path),
            "phase_timings": dict(phase_timings),
            "diff_summary": diff_summary,
            "active_project_diff_summary": active_diff_summary,
            "sandbox": {
                "mode": "isolated-filesystem-copy-allowlisted-pytest",
                "shell_used": False,
                "active_project_root_digest": _sha256_text(str(root)),
                "sandbox_root_digest": _sha256_text(str(sandbox_workspace)),
                "active_project_root_mutated": active_project_mutated,
                "active_production_mutated": False,
                "active_manifest_scope": "source-root-dirs-and-root-files",
                "active_manifest_included_root_dirs": sorted(SANDBOX_ROOT_SOURCE_DIRS),
                "active_manifest_excluded_prefixes": active_evidence_prefixes,
                "write_scope": "sandbox-copy-only; allowed changes limited to pytest cache, runtime, and artifacts inside sandbox",
                "isolation_boundary": "pytest executes in copied sandbox workspace, not active project root",
                "environment_policy": "credential-cleansed-minimal-child-environment",
                "ambient_credential_environment_inherited": False,
                "environment_variable_count": len(sandbox_environment),
                "network_required": False,
                "network_policy": "not-required-no-os-level-network-enforcement",
                "os_level_network_enforcement": False,
            },
            "allowlist": {
                "runner": "pytest",
                "allowed_targets": ["tests/*.py", "tests/**/*.py"],
                "allowed_options": ["-q", "--quiet", "--maxfail=1"],
                "allowed_write_scopes": [".pytest_cache/", "**/__pycache__/", "runtime/", "artifacts/"],
            },
        }
        self._persist_test_evidence(evidence)
        proposal["latest_sandbox_test_evidence"] = {
            key: value
            for key, value in evidence.items()
            if key not in {"stdout_tail", "stderr_tail"}
        }
        self._persist(proposal)
        return evidence

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        proposals = self._list_proposals(limit=limit)
        applied = self._list_records(self.applied_dir, self._memory_applied, limit=limit)
        rollbacks = self._list_records(self.rollbacks_dir, self._memory_rollbacks, limit=limit)
        test_evidence = self._list_records(self.test_evidence_dir, self._memory_test_evidence, limit=limit)
        blocked_count = sum(1 for proposal in proposals if proposal.get("status") == "blocked")
        latest_proposal = proposals[0] if proposals else None
        artifact_bound_replay_gate = _artifact_bound_replay_gate_summary(proposals)
        runtime_state = "static-canon"
        if proposals:
            runtime_state = "degraded" if blocked_count or latest_proposal.get("status") == "blocked" else "live-bound"
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "autonomous-updates",
            "authority": "NexusBrain",
            "runtime_state": runtime_state,
            "proposal_count": len(proposals),
            "shadow_ready_count": sum(1 for proposal in proposals if proposal.get("promotion_state") == "shadow-ready"),
            "canary_ready_count": sum(1 for proposal in proposals if proposal.get("promotion_state") == "canary-ready"),
            "active_ready_count": sum(1 for proposal in proposals if proposal.get("promotion_state") == "active-ready"),
            "blocked_count": blocked_count,
            "admin_approved_count": sum(1 for proposal in proposals if proposal.get("operator_approved")),
            "applied_safe_file_count": len(applied),
            "rolled_back_count": len(rollbacks),
            "sandbox_test_evidence_count": len(test_evidence),
            "latest_proposal": latest_proposal,
            "latest_applied": applied[0] if applied else None,
            "latest_rollback": rollbacks[0] if rollbacks else None,
            "latest_sandbox_test_evidence": test_evidence[0] if test_evidence else None,
            "proposals": proposals,
            "artifact_bound_replay_gate": artifact_bound_replay_gate,
            "required_controls": _required_controls(),
            "operator_actions": _operator_actions(),
        }

    def public_summary(self, *, limit: int = 50) -> dict[str, Any]:
        summary = self.summary(limit=limit)
        public_proposals = [
            _public_autonomous_update_record(proposal)
            for proposal in summary.get("proposals", [])
            if isinstance(proposal, dict)
        ]
        public_by_update_id = {
            str(proposal.get("update_id") or ""): proposal
            for proposal in public_proposals
            if str(proposal.get("update_id") or "")
        }
        latest_proposal = summary.get("latest_proposal")
        latest_update_id = str(latest_proposal.get("update_id") or "") if isinstance(latest_proposal, dict) else ""
        return {
            **summary,
            "latest_proposal": public_by_update_id.get(latest_update_id),
            "latest_applied": _public_autonomous_update_record(summary.get("latest_applied")),
            "latest_rollback": _public_autonomous_update_record(summary.get("latest_rollback")),
            "latest_sandbox_test_evidence": _public_sandbox_test_evidence(
                summary.get("latest_sandbox_test_evidence")
            ),
            "proposals": public_proposals,
            "privacy_boundary": (
                "sanitized-autonomous-update-statuses-refs-counts-and-contained-sandbox-evidence-only-"
                "no-raw-output-local-paths-or-subprocess-argv"
            ),
        }

    def public_sandbox_test_evidence(self, evidence: dict[str, Any]) -> dict[str, Any]:
        return _public_sandbox_test_evidence(evidence)

    def scorecard(self) -> dict[str, Any]:
        summary = self.public_summary()
        return {
            **summary,
            "source_documents": [
                "docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md",
                "docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md",
                "docs/NEXUSNET_YOUTUBE_ASSIMILATION_INTAKE_2026-04-30.md",
            ],
            "promotion_boundary": "no-autonomous-update-without-eval-artifact-trust-rollback-monitoring-operator-and-sandbox-proof",
            "self_improvement_boundary": "memory-prompt-routing-and-runtime-updates-enter-shadow-before-active-use",
        }

    def _persist(self, proposal: dict[str, Any]) -> None:
        existing = [item for item in self._memory_proposals if item.get("update_id") != proposal.get("update_id")]
        self._memory_proposals.insert(0, proposal)
        self._memory_proposals = [proposal, *existing][:50]
        self._proposal_cache = None
        if self.proposals_dir is not None:
            safe_id = _safe_id(proposal["update_id"])
            path = self.proposals_dir / f"{safe_id}.json"
            proposal["artifact_path"] = str(path)
            path.write_text(json.dumps(proposal, indent=2), encoding="utf-8")

    def _list_proposals(self, *, limit: int) -> list[dict[str, Any]]:
        if self._proposal_cache is None:
            proposals = list(self._memory_proposals)
            seen = {proposal.get("update_id") for proposal in proposals}
            if self.proposals_dir is not None:
                for path in self.proposals_dir.glob("*.json"):
                    try:
                        payload = json.loads(path.read_text(encoding="utf-8"))
                    except (OSError, json.JSONDecodeError):
                        continue
                    if payload.get("update_id") not in seen:
                        proposals.append(payload)
            proposals.sort(key=lambda item: item.get("created_at") or "", reverse=True)
            self._proposal_cache = proposals
        return self._proposal_cache[:limit]

    def _find_proposal(self, update_id: str) -> dict[str, Any]:
        for proposal in self._list_proposals(limit=500):
            if proposal.get("update_id") == update_id:
                return proposal
        raise KeyError(f"Unknown autonomous update proposal: {update_id}")

    def _find_applied(self, update_id: str) -> dict[str, Any]:
        for applied in self._list_records(self.applied_dir, self._memory_applied, limit=500):
            if applied.get("update_id") == update_id:
                return applied
        raise KeyError(f"Autonomous update has not been applied: {update_id}")

    def _safe_file_path(self, update_id: str) -> Path:
        if self.safe_files_dir is None:
            raise ValueError("safe file apply requires an artifacts_dir")
        self.safe_files_dir.mkdir(parents=True, exist_ok=True)
        return self.safe_files_dir / f"{_safe_id(update_id)}.json"

    def _sandbox_run_root(self, update_id: str, run_id: str) -> Path:
        if self.sandboxes_dir is None:
            raise ValueError("sandbox test execution requires an artifacts_dir")
        path = self.sandboxes_dir / _safe_id(update_id) / run_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _persist_record(
        self,
        record: dict[str, Any],
        directory: Path | None,
        memory: list[dict[str, Any]],
        *,
        suffix: str,
    ) -> None:
        memory.insert(0, record)
        del memory[50:]
        if directory is not None:
            directory.mkdir(parents=True, exist_ok=True)
            path = directory / f"{_safe_id(record['update_id'])}.{suffix}.json"
            record["artifact_path"] = str(path)
            path.write_text(json.dumps(record, indent=2), encoding="utf-8")

    def _list_records(self, directory: Path | None, memory: list[dict[str, Any]], *, limit: int) -> list[dict[str, Any]]:
        records = list(memory)
        seen = {(record.get("update_id"), record.get("status"), record.get("artifact_path")) for record in records}
        if directory is not None:
            for path in directory.glob("*.json"):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                key = (payload.get("update_id"), payload.get("status"), payload.get("artifact_path"))
                if key not in seen:
                    records.append(payload)
        records.sort(
            key=lambda item: item.get("rolled_back_at") or item.get("applied_at") or item.get("approved_at") or "",
            reverse=True,
        )
        return records[:limit]

    def _persist_test_evidence(self, evidence: dict[str, Any]) -> None:
        self._memory_test_evidence.insert(0, evidence)
        del self._memory_test_evidence[50:]
        if self.test_evidence_dir is not None:
            self.test_evidence_dir.mkdir(parents=True, exist_ok=True)
            path = self.test_evidence_dir / f"{_safe_id(evidence['evidence_ref'])}.json"
            evidence["artifact_path"] = str(path)
            path.write_text(json.dumps(evidence, indent=2, sort_keys=True), encoding="utf-8")

    def _find_test_evidence(self, evidence_ref: str) -> dict[str, Any]:
        for evidence in self._list_records(self.test_evidence_dir, self._memory_test_evidence, limit=500):
            if evidence.get("evidence_ref") == evidence_ref or evidence.get("artifact_path") == evidence_ref:
                return evidence
        raise KeyError(f"Unknown sandbox test evidence: {evidence_ref}")

    def _test_results_from_evidence_refs(self, evidence_refs: list[str] | None) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for evidence_ref in evidence_refs or []:
            evidence = self._find_test_evidence(str(evidence_ref))
            results.append(
                {
                    "command": str(evidence.get("command") or ""),
                    "passed": evidence.get("passed") is True,
                    "failure_count": int(evidence.get("failure_count") or 0),
                    "evidence_ref": str(evidence.get("evidence_ref") or ""),
                    "artifact_path": str(evidence.get("artifact_path") or ""),
                    "sandbox_mode": str((evidence.get("sandbox") or {}).get("mode") or ""),
                    "active_project_root_mutated": bool(
                        (evidence.get("sandbox") or {}).get("active_project_root_mutated")
                    ),
                    "diff_summary": evidence.get("diff_summary") or {},
                    "pre_manifest_path": str(evidence.get("pre_manifest_path") or ""),
                    "post_manifest_path": str(evidence.get("post_manifest_path") or ""),
                    "diff_path": str(evidence.get("diff_path") or ""),
                    "returncode": int(evidence.get("returncode") or 0),
                }
            )
        return results


AUTONOMOUS_UPDATE_APPROVAL_SUBJECT = "release-wrapper-autonomous-update"


def _bound_admin_approval_evidence(
    update_id: str,
    approval_evidence: dict[str, Any] | None,
) -> dict[str, str]:
    evidence = approval_evidence if isinstance(approval_evidence, dict) else {}
    approval_ref = str(evidence.get("approval_ref") or evidence.get("approval_decision_id") or "").strip()
    subject = str(evidence.get("approval_subject") or evidence.get("subject") or "").strip()
    decision = str(evidence.get("decision") or evidence.get("status") or "").strip().lower()
    approved_update_id = str(evidence.get("approved_update_id") or evidence.get("update_id") or "").strip()
    if (
        not approval_ref
        or subject != AUTONOMOUS_UPDATE_APPROVAL_SUBJECT
        or decision != "approved"
        or approved_update_id != update_id
    ):
        raise ValueError("stored admin approval must bind the exact autonomous update before execution")
    return {
        "approval_ref": approval_ref,
        "approval_subject": subject,
        "approved_update_id": approved_update_id,
        "approver_digest": str(evidence.get("approver_digest") or ""),
        "rationale_digest": str(evidence.get("rationale_digest") or ""),
        "metadata_digest": str(evidence.get("metadata_digest") or ""),
    }


def _proposal_has_bound_admin_approval(proposal: dict[str, Any]) -> bool:
    approval = proposal.get("admin_approval") if isinstance(proposal.get("admin_approval"), dict) else {}
    return bool(
        proposal.get("operator_approved") is True
        and approval.get("status") == "admin-approved"
        and approval.get("approval_subject") == AUTONOMOUS_UPDATE_APPROVAL_SUBJECT
        and approval.get("approved_update_id") == proposal.get("update_id")
        and approval.get("approval_ref")
    )


def _update_findings(request: AutonomousUpdateRequest, *, upstream_eval_gate: dict[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if request.requested_state != "proposal" and not request.eval_refs:
        findings.append(
            {
                "rule_id": "autonomous_update_requires_eval_evidence",
                "severity": "hard_fail",
                "message": "Autonomous updates cannot promote without held-out or external eval evidence.",
            }
        )
    if request.requested_state in {"shadow", "canary", "active"} and not request.artifact_trust_refs:
        findings.append(
            {
                "rule_id": "autonomous_update_requires_artifact_trust",
                "severity": "hard_fail",
                "message": "Autonomous updates need artifact trust, provenance, or signed manifest evidence.",
            }
        )
    if request.requested_state in {"shadow", "canary", "active"} and not request.operator_approved:
        findings.append(
            {
                "rule_id": "autonomous_update_requires_operator_approval",
                "severity": "hard_fail",
                "message": "Operator approval is required before autonomous updates enter shadow, canary, or active state.",
            }
        )
    if request.requested_state in {"shadow", "canary", "active"} and not request.sandbox_ref.strip():
        findings.append(
            {
                "rule_id": "autonomous_update_requires_sandbox",
                "severity": "hard_fail",
                "message": "Autonomous updates require a sandbox or equivalent isolation reference.",
            }
        )
    if request.requested_state in {"shadow", "canary", "active"} and upstream_eval_gate["promotion_allowed"] is False:
        findings.append(
            {
                "rule_id": "autonomous_update_blocks_eval_promotion_gate",
                "severity": "hard_fail",
                "message": "Autonomous updates cannot promote from blocked shadow eval evidence.",
            }
        )
    lifecycle_gate = upstream_eval_gate.get("upstream_lifecycle_gate") or {}
    if request.requested_state in {"shadow", "canary", "active"} and lifecycle_gate.get("lifecycle_status") == "closed_loop_blocked":
        findings.append(
            {
                "rule_id": "autonomous_update_blocks_upstream_lifecycle_gate",
                "severity": "hard_fail",
                "message": "Autonomous updates cannot promote while upstream lifecycle evidence is blocked.",
            }
        )
    return findings


def _upstream_eval_gate(request: AutonomousUpdateRequest) -> dict[str, Any]:
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


def _policy_targets(request: AutonomousUpdateRequest) -> list[dict[str, Any]]:
    promotion_requested = request.requested_state != "proposal"
    return [
        {
            "target_id": f"autonomous-update::{request.update_id}",
            "target_type": "autonomous_update",
            "metadata": {
                "promotion_requested": promotion_requested,
                "rollback_plan": request.rollback_plan,
                "monitoring_plan": request.monitoring_plan,
            },
        },
        {
            "target_id": f"artifact::{request.update_id}",
            "target_type": "artifact",
            "metadata": {
                "promotion_requested": promotion_requested,
                "license_state": "approved" if request.artifact_trust_refs else None,
                "provenance_refs": request.artifact_trust_refs,
            },
        },
        {
            "target_id": f"sandbox::{request.update_id}",
            "target_type": "tool_execution",
            "metadata": {
                "write_enabled": promotion_requested,
                "sandboxed": bool(request.sandbox_ref.strip()),
                "tool_scope": request.update_type,
            },
        },
    ]


def _status_for(request: AutonomousUpdateRequest, *, blocked: bool) -> str:
    if blocked:
        return "blocked"
    if request.requested_state == "proposal":
        return "proposed"
    return f"{request.requested_state}-approved"


def _promotion_state(request: AutonomousUpdateRequest, *, blocked: bool) -> str:
    if blocked:
        return "blocked-by-policy"
    if request.requested_state == "proposal":
        return "proposal-ready"
    return f"{request.requested_state}-ready"


def _required_controls() -> list[str]:
    return [
        "eval_gate",
        "artifact_trust_gate",
        "rollback",
        "monitoring",
        "operator_approval",
        "sandbox",
        "policy_scan",
        "shadow_promote_monitor_rollback",
    ]


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/autonomous-updates"},
        "propose": {"method": "POST", "endpoint": "/ops/brain/autonomous-updates/proposals"},
        "admin_approve": {"method": "POST", "endpoint": "/ops/brain/autonomous-updates/{update_id}/admin-approval"},
        "sandbox_tests": {"method": "POST", "endpoint": "/ops/brain/autonomous-updates/{update_id}/sandbox-tests"},
        "apply_safe": {"method": "POST", "endpoint": "/ops/brain/autonomous-updates/{update_id}/apply"},
        "rollback": {"method": "POST", "endpoint": "/ops/brain/autonomous-updates/{update_id}/rollback"},
        "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/autonomous-updates"},
    }


def _admin_approval_evidence_gate(proposal: dict[str, Any]) -> dict[str, Any]:
    eval_refs = [str(item) for item in (proposal.get("eval_refs") or [])]
    artifact_trust_refs = [str(item) for item in (proposal.get("artifact_trust_refs") or [])]
    rollback_plan = str(proposal.get("rollback_plan") or "").strip()
    monitoring_plan = str(proposal.get("monitoring_plan") or "").strip()
    return {
        "eval_refs": eval_refs,
        "artifact_trust_refs": artifact_trust_refs,
        "rollback_plan_present": bool(rollback_plan),
        "monitoring_plan_present": bool(monitoring_plan),
        "all_required_refs_present": bool(eval_refs and artifact_trust_refs and rollback_plan and monitoring_plan),
    }


def _normalize_test_results(test_results: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for item in test_results or []:
        failures = item.get("failure_count", 0)
        try:
            failure_count = int(failures)
        except (TypeError, ValueError):
            failure_count = 1
        normalized.append(
            {
                "command": str(item.get("command") or ""),
                "passed": bool(item.get("passed")),
                "failure_count": failure_count,
                "evidence_ref": str(item.get("evidence_ref") or ""),
            }
        )
    return normalized


def _test_evidence_passed(test_results: list[dict[str, Any]]) -> bool:
    if not test_results:
        return False
    for result in test_results:
        diff_summary = result.get("diff_summary") if isinstance(result.get("diff_summary"), dict) else {}
        if result.get("passed") is not True:
            return False
        if int(result.get("failure_count") or 0) != 0:
            return False
        if result.get("sandbox_mode") != "isolated-filesystem-copy-allowlisted-pytest":
            return False
        if result.get("active_project_root_mutated") is True:
            return False
        if int(diff_summary.get("unsafe_change_count") or 0) != 0:
            return False
    return True


def _safe_apply_ao_guard_summary(ao_guard: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(ao_guard, dict):
        raise ValueError("AO guard receipts required before safe apply")
    required = set(SAFE_APPLY_REQUIRED_AO_GUARD_AOS)
    required_aos = {str(item) for item in (ao_guard.get("required_aos") or [])}
    received_aos = {str(item) for item in (ao_guard.get("received_aos") or [])}
    receipts = [receipt for receipt in (ao_guard.get("receipts") or []) if isinstance(receipt, dict)]
    receipt_aos = {str(receipt.get("ao_name") or "") for receipt in receipts}
    receipt_refs = [str(item) for item in (ao_guard.get("receipt_refs") or []) if str(item or "")]
    if not receipt_refs:
        receipt_refs = [str(receipt.get("execution_id") or "") for receipt in receipts if receipt.get("execution_id")]
    valid = (
        ao_guard.get("surface_id") == "release-wrapper-ao-guard"
        and ao_guard.get("action") == "apply"
        and ao_guard.get("passed") is True
        and ao_guard.get("raw_content_included") is False
        and ao_guard.get("active_production_mutation_allowed") is False
        and required.issubset(required_aos)
        and required.issubset(received_aos)
        and required.issubset(receipt_aos)
        and bool(receipt_refs)
    )
    if not valid:
        raise ValueError("AO guard receipts required before safe apply")
    for receipt in receipts:
        if str(receipt.get("ao_name") or "") not in required:
            continue
        if receipt.get("surface_id") != "ao-execution-receipt":
            raise ValueError("AO guard receipts required before safe apply")
        if receipt.get("raw_content_included") is not False:
            raise ValueError("AO guard receipts required before safe apply")
        if receipt.get("active_production_mutation_allowed") is not False:
            raise ValueError("AO guard receipts required before safe apply")
        if list(receipt.get("direct_local_state_reads") or []) != []:
            raise ValueError("AO guard receipts required before safe apply")
    return {
        "ao_guard_required": True,
        "ao_guard_passed": True,
        "ao_guard_aos": sorted(required),
        "ao_guard_receipt_refs": receipt_refs,
        "ao_guard_surface_id": "release-wrapper-ao-guard",
    }


def _requires_shadow_eval_replay(proposal: dict[str, Any]) -> bool:
    metadata = proposal.get("metadata") if isinstance(proposal.get("metadata"), dict) else {}
    safe_payload = metadata.get("safe_payload") if isinstance(metadata.get("safe_payload"), dict) else {}
    eval_refs = [str(ref) for ref in (proposal.get("eval_refs") or [])]
    source = str(metadata.get("source") or "")
    target_ref = str(proposal.get("target_ref") or "")
    return (
        source in {"release-wrapper-runtime", "release-wrapper-dream-research-queue", "release-wrapper-dream-research"}
        or metadata.get("dream_research_queue") is True
        or safe_payload.get("peer_shadow_import") is True
        or target_ref.startswith("safe-artifact::release-wrapper")
        or bool(_proposal_artifact_gate_refs(proposal))
        or any(ref.startswith("federated-packet-import::") for ref in eval_refs)
        or any(ref.startswith("eval::release-wrapper-") for ref in eval_refs)
    )


def _shadow_eval_replay_passed(eval_replay: Any, *, proposal: dict[str, Any] | None = None) -> bool:
    if not isinstance(eval_replay, dict):
        return False
    base_passed = (
        eval_replay.get("status") == "passed-shadow"
        and eval_replay.get("promotion_allowed") is True
        and eval_replay.get("operator_approved") is True
        and bool(eval_replay.get("run_id"))
        and bool(eval_replay.get("suite_id"))
    )
    if not base_passed:
        return False
    if proposal is None:
        return True
    required_suite_refs = set(_proposal_eval_suite_refs(proposal))
    if required_suite_refs and str(eval_replay.get("suite_id") or "") not in required_suite_refs:
        return False
    required_gate_refs = set(_proposal_artifact_gate_refs(proposal))
    if required_gate_refs:
        replay_gate_refs = set(_artifact_gate_refs_from_replay(eval_replay))
        if not required_gate_refs.issubset(replay_gate_refs):
            return False
    return True


def _artifact_bound_replay_gate_summary(proposals: list[dict[str, Any]]) -> dict[str, Any]:
    required: list[dict[str, Any]] = []
    for proposal in proposals:
        gate_refs = _proposal_artifact_gate_refs(proposal)
        if not gate_refs:
            continue
        replay = proposal.get("latest_eval_replay") if isinstance(proposal.get("latest_eval_replay"), dict) else {}
        replay_bound = _shadow_eval_replay_passed(replay, proposal=proposal)
        required.append(
            {
                "update_id": proposal.get("update_id"),
                "status": proposal.get("status"),
                "promotion_state": proposal.get("promotion_state"),
                "operator_approved": proposal.get("operator_approved") is True,
                "required_artifact_gate_refs": gate_refs,
                "required_eval_suite_refs": _proposal_eval_suite_refs(proposal),
                "latest_replay_status": replay.get("status"),
                "latest_replay_suite_id": replay.get("suite_id"),
                "latest_replay_bound": replay_bound,
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
            }
        )
    bound_count = sum(1 for item in required if item["latest_replay_bound"] is True)
    missing_count = len(required) - bound_count
    return {
        "surface_id": "artifact-bound-autonomous-update-replay-gate",
        "status": "not-required" if not required else "passed-shadow" if missing_count == 0 else "blocked",
        "required_count": len(required),
        "bound_replay_count": bound_count,
        "missing_bound_replay_count": missing_count,
        "latest_required_proposal": required[0] if required else None,
        "required_proposals": required,
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "privacy_boundary": "sanitized-update-ids-eval-suite-refs-and-artifact-gate-refs-only",
        "mutation_boundary": "status-projection-only-no-active-production-mutation",
    }


def _proposal_eval_suite_refs(proposal: dict[str, Any]) -> list[str]:
    metadata = proposal.get("metadata") if isinstance(proposal.get("metadata"), dict) else {}
    safe_payload = metadata.get("safe_payload") if isinstance(metadata.get("safe_payload"), dict) else {}
    refs = [
        str(ref)
        for ref in (proposal.get("eval_refs") or [])
        if str(ref).startswith("eval::release-wrapper-")
    ]
    for value in (metadata.get("evals_ao_eval_suite_id"), safe_payload.get("evals_ao_eval_suite_id")):
        if str(value or "").startswith("eval::release-wrapper-"):
            refs.append(str(value))
    return _dedupe_refs(refs)


def _proposal_artifact_gate_refs(proposal: dict[str, Any]) -> list[str]:
    metadata = proposal.get("metadata") if isinstance(proposal.get("metadata"), dict) else {}
    safe_payload = metadata.get("safe_payload") if isinstance(metadata.get("safe_payload"), dict) else {}
    refs = [str(ref) for ref in (proposal.get("eval_refs") or []) if str(ref).startswith("evals-ao-artifact::")]
    for value in (
        metadata.get("evals_ao_artifact_gate_ref"),
        safe_payload.get("evals_ao_artifact_gate_ref"),
    ):
        normalized = _normalize_artifact_gate_ref(value)
        if normalized:
            refs.append(normalized)
    return _dedupe_refs(refs)


def _artifact_gate_refs_from_replay(eval_replay: dict[str, Any]) -> list[str]:
    metadata = eval_replay.get("metadata") if isinstance(eval_replay.get("metadata"), dict) else {}
    refs: list[str] = []
    for collection_name in ("evidence_refs", "evaluator_refs", "artifact_gate_refs"):
        refs.extend(
            str(ref)
            for ref in (eval_replay.get(collection_name) or [])
            if str(ref).startswith("evals-ao-artifact::")
        )
    for value in (
        metadata.get("evals_ao_artifact_gate_ref"),
        metadata.get("gate_id"),
    ):
        normalized = _normalize_artifact_gate_ref(value)
        if normalized:
            refs.append(normalized)
    for value in metadata.get("evals_ao_artifact_gate_refs") or []:
        normalized = _normalize_artifact_gate_ref(value)
        if normalized:
            refs.append(normalized)
    return _dedupe_refs(refs)


def _normalize_artifact_gate_ref(value: Any) -> str:
    ref = str(value or "")
    return ref if ref.startswith("evals-ao-artifact::") else ""


def _dedupe_refs(refs: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for ref in refs:
        if ref and ref not in seen:
            seen.add(ref)
            deduped.append(ref)
    return deduped


def _allowlisted_pytest_argv(command: str, *, project_root: Path) -> list[str]:
    stripped = str(command or "").strip()
    if not stripped:
        raise ValueError("allowlisted pytest command is required")
    if any(marker in stripped for marker in [";", "&", "|", ">", "<", "`", "\n", "\r"]):
        raise ValueError("allowlisted pytest command cannot contain shell metacharacters")
    parts = stripped.split()
    if parts[:3] == ["python", "-m", "pytest"]:
        pytest_args = parts[3:]
    elif parts[:3] == [sys.executable, "-m", "pytest"]:
        pytest_args = parts[3:]
    elif parts and parts[0] == "pytest":
        pytest_args = parts[1:]
    else:
        raise ValueError("allowlisted pytest command must start with pytest")
    if not pytest_args:
        raise ValueError("allowlisted pytest command requires at least one tests/ target")

    saw_target = False
    for arg in pytest_args:
        if arg in {"-q", "--quiet"} or arg.startswith("--maxfail="):
            continue
        if arg.startswith("-"):
            raise ValueError(f"allowlisted pytest option is not permitted: {arg}")
        _validate_pytest_target(arg, project_root=project_root)
        saw_target = True
    if not saw_target:
        raise ValueError("allowlisted pytest command requires at least one tests/ target")
    return [sys.executable, "-m", "pytest", "--rootdir", str(project_root), *pytest_args]


def _validate_pytest_target(target: str, *, project_root: Path) -> None:
    path_part = str(target).split("::", 1)[0]
    normalized = path_part.replace("\\", "/")
    if not normalized.startswith("tests/") or ".." in normalized.split("/"):
        raise ValueError("allowlisted pytest target must stay under tests/")
    if not normalized.endswith(".py"):
        raise ValueError("allowlisted pytest target must be a .py file")
    resolved = (project_root / path_part).resolve()
    root = project_root.resolve()
    if not str(resolved).lower().startswith(str(root).lower()):
        raise ValueError("allowlisted pytest target must stay inside the project root")
    if not resolved.exists():
        raise ValueError(f"allowlisted pytest target does not exist: {path_part}")


SANDBOX_ROOT_SOURCE_DIRS: set[str] = {
    "app",
    "apps",
    "assets",
    "benchmarks",
    "config",
    "configs",
    "connectors",
    "core",
    "memory",
    "nexus",
    "nexusnet",
    "research",
    "scripts",
    "services",
    "src",
    "tests",
    "tools",
    "training",
    "ui",
    "utils",
}

SANDBOX_ACTIVE_MANIFEST_EXCLUDED_PREFIXES: list[str] = [
    ".codex/",
    ".codex-remote-attachments/",
    ".git/",
    ".gitnexus/",
    ".pytest-tmp/",
    ".venv/",
    "artifacts/",
    "data/",
    "dist/",
    "docs/",
    "mobile/",
    "monitoring/",
    "patent/",
    "pytest-cache-files-*/",
    "quantlab/",
    "recursive_dreamer/",
    "rl/",
    "runtime/",
    "teachers/",
    "temporal/",
    "venv/",
]


def _sandbox_copy_ignore(directory: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    root_like = {"nexus", "nexusnet", "tests"}.issubset(set(names))
    blocked_names = {
        ".codex",
        ".codex-remote-attachments",
        ".git",
        ".gitnexus",
        ".idea",
        ".mypy_cache",
        ".pytest_cache",
        ".pytest-tmp",
        ".ruff_cache",
        ".venv",
        ".vscode",
        "__pycache__",
        "artifacts",
        "build",
        "dist",
        "node_modules",
        "venv",
    }
    for name in names:
        if root_like and (Path(directory) / name).is_dir() and name not in SANDBOX_ROOT_SOURCE_DIRS:
            ignored.add(name)
            continue
        if (
            name in blocked_names
            or name.startswith("pytest-cache-files-")
            or name.endswith(".pyc")
            or name.endswith(".pyo")
        ):
            ignored.add(name)
    return ignored


def _sandbox_workspace_root(update_id: str, run_id: str) -> Path:
    return Path(tempfile.gettempdir()) / "nexusnet-autonomous-update-sandboxes" / _safe_id(update_id) / run_id / "workspace"


def _sandbox_subprocess_environment(sandbox_workspace: Path) -> dict[str, str]:
    sandbox_temp = sandbox_workspace / ".nexusnet-sandbox-tmp"
    sandbox_home = sandbox_workspace / ".nexusnet-sandbox-home"
    for directory in (
        sandbox_temp,
        sandbox_home,
        sandbox_home / "AppData" / "Roaming",
        sandbox_home / "AppData" / "Local",
    ):
        directory.mkdir(parents=True, exist_ok=True)

    bootstrap_keys = ("SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT", "PATH")
    environment = {
        key: value
        for key in bootstrap_keys
        if (value := os.environ.get(key))
    }
    environment.update(
        {
            "TEMP": str(sandbox_temp),
            "TMP": str(sandbox_temp),
            "TMPDIR": str(sandbox_temp),
            "HOME": str(sandbox_home),
            "USERPROFILE": str(sandbox_home),
            "APPDATA": str(sandbox_home / "AppData" / "Roaming"),
            "LOCALAPPDATA": str(sandbox_home / "AppData" / "Local"),
            "PYTHONNOUSERSITE": "1",
            "PYTHONPATH": "",
            "PYTEST_ADDOPTS": "",
            "PIP_NO_INPUT": "1",
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
            "NEXUSNET_AUTONOMOUS_SANDBOX": "1",
        }
    )
    return environment


_PUBLIC_AUTONOMOUS_UPDATE_OMITTED_KEYS = {
    "argv",
    "artifact_path",
    "diff_path",
    "phase_status_path",
    "post_manifest_path",
    "pre_manifest_path",
    "previous_content",
    "safe_file_path",
    "stderr_tail",
    "stdout_tail",
}


def _public_autonomous_update_record(record: Any) -> dict[str, Any] | None:
    if not isinstance(record, dict):
        return None
    public: dict[str, Any] = {}
    for key, value in record.items():
        if key in _PUBLIC_AUTONOMOUS_UPDATE_OMITTED_KEYS:
            continue
        if key in {"changes", "unsafe_changes"}:
            continue
        if isinstance(value, dict):
            public[key] = _public_autonomous_update_record(value) or {}
        elif isinstance(value, list):
            public[key] = [
                _public_autonomous_update_record(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            public[key] = value
    return public


def _public_sandbox_test_evidence(evidence: Any) -> dict[str, Any] | None:
    public = _public_autonomous_update_record(evidence)
    if public is None:
        return None
    public["diagnostic_artifact_available"] = bool(public.get("evidence_ref"))
    public["raw_content_included"] = False
    public["privacy_boundary"] = (
        "sanitized-sandbox-status-refs-counts-and-containment-metadata-only-"
        "no-output-local-paths-or-subprocess-argv"
    )
    return public


def _file_manifest(
    root: Path,
    *,
    exclude_prefixes: list[str] | None = None,
    include_root_dirs: set[str] | None = None,
) -> dict[str, dict[str, Any]]:
    root = root.resolve()
    prefixes = [prefix.replace("\\", "/") for prefix in (exclude_prefixes or [])]
    manifest: dict[str, dict[str, Any]] = {}
    paths: list[Path] = []
    if include_root_dirs is None:
        paths = list(root.rglob("*"))
    else:
        for child in root.iterdir():
            if child.is_file():
                paths.append(child)
            elif child.is_dir() and child.name in include_root_dirs:
                paths.extend(child.rglob("*"))
    for path in paths:
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if any(rel == prefix.rstrip("/") or rel.startswith(prefix) for prefix in prefixes):
            continue
        try:
            data = path.read_bytes()
        except OSError:
            continue
        manifest[rel] = {
            "path": rel,
            "size": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
    return manifest


def _manifest_payload(manifest: dict[str, dict[str, Any]], *, root: Path) -> dict[str, Any]:
    return {
        "schema_version": "autonomous_update_sandbox_manifest.v0.1",
        "root_digest": _sha256_text(str(root.resolve())),
        "file_count": len(manifest),
        "files": [manifest[key] for key in sorted(manifest)],
    }


def _manifest_diff(
    before: dict[str, dict[str, Any]],
    after: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    changes: list[dict[str, Any]] = []
    before_paths = set(before)
    after_paths = set(after)
    for path in sorted(after_paths - before_paths):
        changes.append({"path": path, "change_type": "added", "size": after[path]["size"]})
    for path in sorted(before_paths - after_paths):
        changes.append({"path": path, "change_type": "removed", "size": before[path]["size"]})
    for path in sorted(before_paths & after_paths):
        if before[path]["sha256"] != after[path]["sha256"] or before[path]["size"] != after[path]["size"]:
            changes.append(
                {
                    "path": path,
                    "change_type": "modified",
                    "before_size": before[path]["size"],
                    "after_size": after[path]["size"],
                }
            )
    return {
        "changed_file_count": len(changes),
        "added_count": sum(1 for change in changes if change["change_type"] == "added"),
        "modified_count": sum(1 for change in changes if change["change_type"] == "modified"),
        "removed_count": sum(1 for change in changes if change["change_type"] == "removed"),
        "changes": changes[:100],
    }


def _allowed_sandbox_change(path: str) -> bool:
    normalized = path.replace("\\", "/")
    parts = normalized.split("/")
    if "__pycache__" in parts or normalized.endswith((".pyc", ".pyo")):
        return True
    return normalized.startswith((".pytest_cache/", "runtime/", "artifacts/"))


def _sha256_text(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def _safe_id(value: str) -> str:
    return value.replace(":", "_").replace("/", "_").replace("\\", "_")

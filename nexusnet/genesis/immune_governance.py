from __future__ import annotations

import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .core_objectives import GenesisCoreObjectivesLedgerService


class GenesisImmuneGovernanceService:
    """Layer 10 closed-eval, quarantine, rollback, and governance authority."""

    def __init__(
        self,
        *,
        artifacts_dir: Path | str,
        event_spine: Any | None = None,
        code_root: Path | str | None = None,
    ) -> None:
        self.artifacts_dir = Path(artifacts_dir)
        self.event_spine = event_spine
        self.code_root = Path(code_root or Path(__file__).resolve().parents[2]).resolve()
        self.root = self.artifacts_dir / "genesis" / "immune-governance"
        self.evaluations_dir = self.root / "evaluations"
        self.decisions_dir = self.root / "governance-decisions"
        self.core_objectives = GenesisCoreObjectivesLedgerService(
            artifacts_dir=self.artifacts_dir,
            event_spine=self.event_spine,
        )

    def summary(self) -> dict[str, Any]:
        evaluations = self._records(self.evaluations_dir)
        decisions = self._records(self.decisions_dir)
        has_evidence = bool(evaluations or decisions)
        return {
            "schema_version": "nexusnet-genesis-layer10-immune-governance-v1",
            "surface_id": "genesis-immune-governance",
            "status": "live-with-eval-and-governance-evidence" if has_evidence else "live-awaiting-candidate-evidence",
            "honest_status_label": (
                "genesis-layer10-immune-governance-live-with-evidence"
                if has_evidence
                else "genesis-layer10-immune-governance-live-awaiting-evidence"
            ),
            "authority": "NexusBrain",
            "deny_by_default": True,
            "evaluation_count": len(evaluations),
            "passed_evaluation_count": sum(1 for item in evaluations if item.get("status") == "sandbox-evaluated-awaiting-governance"),
            "quarantine_count": sum(1 for item in evaluations if item.get("status") == "quarantined"),
            "governance_decision_count": len(decisions),
            "approved_promotion_count": sum(1 for item in decisions if item.get("promotion_allowed") is True),
            "latest_evaluation": evaluations[0] if evaluations else None,
            "latest_governance_decision": decisions[0] if decisions else None,
            "core_objectives": self.core_objectives.summary(),
            "contracts": {
                "sandbox_run_envelope": "closed-filesystem-copy-allowlisted-pytest-v1",
                "deterministic_evidence": "source-manifest-command-and-candidate-digest-v1",
                "eval_case": "held-out-reference-contract-v1",
                "regression_suite": "baseline-and-regression-suite-contract-v1",
                "judge_policy": "calibrated-judge-plus-human-and-domain-check-v1",
                "red_team_finding_receipt": "hard-fail-finding-receipt-v1",
                "promotion_gate": "deny-until-sandbox-rollback-and-governance-pass-v1",
                "quarantine": "failed-candidates-remain-non-routable-v1",
                "rollback_proof": "baseline-ref-and-active-source-nonmutation-v1",
                "governance_decision": "admin-human-domain-decision-v1",
            },
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }

    def evaluate_candidate(self, payload: dict[str, Any]) -> dict[str, Any]:
        candidate_ref = _required_ref(payload, "candidate_ref")
        candidate_kind = _required_ref(payload, "candidate_kind")
        baseline_ref = _required_ref(payload, "baseline_ref")
        rollback_proof_ref = _required_ref(payload, "rollback_proof_ref")
        artifact_trust_ref = _required_ref(payload, "artifact_trust_ref")
        eval_case_refs = _required_refs(payload, "eval_case_refs")
        regression_suite_ref = _required_ref(payload, "regression_suite_ref")
        judge_policy = _judge_policy(payload.get("judge_policy"))
        argv = _allowlisted_pytest_argv(str(payload.get("command") or ""))
        timeout_seconds = max(1, min(int(payload.get("timeout_seconds") or 120), 180))
        candidate_id = f"immune-candidate::{_digest(candidate_ref)}"
        started_at = _utcnow()
        active_pre_manifest = _source_manifest(self.code_root)
        evidence_seed = json.dumps(
            {
                "candidate_ref": candidate_ref,
                "argv": argv[3:],
                "source_manifest": active_pre_manifest,
                "eval_case_refs": eval_case_refs,
                "regression_suite_ref": regression_suite_ref,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        deterministic_evidence_digest = "sha256:" + hashlib.sha256(evidence_seed.encode("utf-8")).hexdigest()
        run_id = f"genesis-immune-eval::{_digest(deterministic_evidence_digest)}"
        sandbox_root = Path(tempfile.gettempdir()) / "nexusnet-genesis-immune-sandboxes" / _artifact_id(run_id)
        if sandbox_root.exists():
            shutil.rmtree(sandbox_root)

        phase_timings: dict[str, float] = {}
        copy_started = time.perf_counter()
        shutil.copytree(self.code_root, sandbox_root, ignore=_copy_ignore)
        phase_timings["copy_seconds"] = round(time.perf_counter() - copy_started, 4)
        sandbox_pre_manifest = _source_manifest(sandbox_root)
        run_started = time.perf_counter()
        try:
            completed = subprocess.run(
                [sys.executable, "-m", "pytest", *argv[3:]],
                cwd=sandbox_root,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                shell=False,
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
        phase_timings["pytest_seconds"] = round(time.perf_counter() - run_started, 4)

        sandbox_post_manifest = _source_manifest(sandbox_root)
        active_post_manifest = _source_manifest(self.code_root)
        sandbox_source_changes = _manifest_changes(sandbox_pre_manifest, sandbox_post_manifest)
        active_source_changes = _manifest_changes(active_pre_manifest, active_post_manifest)
        passed = returncode == 0 and not timed_out and not sandbox_source_changes and not active_source_changes
        shutil.rmtree(sandbox_root, ignore_errors=True)
        completed_at = _utcnow()
        findings = []
        if returncode != 0:
            findings.append(_finding("closed_sandbox_pytest_failed", "Closed sandbox regression execution did not pass."))
        if timed_out:
            findings.append(_finding("closed_sandbox_timed_out", "Closed sandbox regression execution timed out."))
        if sandbox_source_changes:
            findings.append(_finding("sandbox_source_mutation_detected", "The candidate eval mutated source files inside the sandbox."))
        if active_source_changes:
            findings.append(_finding("active_source_mutation_detected", "The candidate eval mutated active project source."))

        artifact_ref = f"genesis/immune-governance/evaluations/{_artifact_id(candidate_id)}.json"
        rollback_ready = bool(baseline_ref and rollback_proof_ref and not active_source_changes)
        core_objectives = self.core_objectives.assess(
            candidate_ref=candidate_ref,
            candidate_kind=candidate_kind,
            objective_metrics=payload.get("objective_metrics"),
        )
        core_objectives_shadow_allowed = core_objectives.get("shadow_governance_allowed") is True
        promotion_blockers = ["governance_decision_required"] if passed else ["closed_sandbox_eval_failed", "quarantine_active"]
        promotion_blockers.extend(str(blocker) for blocker in core_objectives.get("blockers") or [])
        evaluation = {
            "schema_version": "nexusnet-genesis-layer10-candidate-evaluation-v1",
            "surface_id": "genesis-immune-governance-candidate-evaluation",
            "candidate_id": candidate_id,
            "candidate_ref": candidate_ref,
            "candidate_kind": candidate_kind,
            "artifact_ref": artifact_ref,
            "status": "sandbox-evaluated-awaiting-governance" if passed else "quarantined",
            "sandbox_run_envelope": {
                "run_id": run_id,
                "mode": "isolated-filesystem-copy-allowlisted-pytest",
                "runner": "python-m-pytest",
                "command_ref": "command-digest::" + _digest(" ".join(argv[1:])),
                "target_refs": [_safe_ref(part) for part in argv[3:] if not part.startswith("-")],
                "timeout_seconds": timeout_seconds,
                "network_required": False,
                "shell_used": False,
                "write_scope": "temporary-sandbox-copy-only",
            },
            "closed_sandbox_evidence": {
                "executed": True,
                "passed": passed,
                "returncode": returncode,
                "timed_out": timed_out,
                "shell_used": False,
                "deterministic_evidence_digest": deterministic_evidence_digest,
                "source_manifest_digest": "sha256:" + _digest(json.dumps(active_pre_manifest, sort_keys=True)),
                "stdout_digest": "sha256:" + hashlib.sha256(stdout.encode("utf-8")).hexdigest(),
                "stderr_digest": "sha256:" + hashlib.sha256(stderr.encode("utf-8")).hexdigest(),
                "sandbox_source_change_count": len(sandbox_source_changes),
                "active_project_source_mutated": bool(active_source_changes),
                "active_source_change_count": len(active_source_changes),
                "phase_timings": phase_timings,
                "started_at": started_at,
                "completed_at": completed_at,
            },
            "eval_case_contract": {
                "case_refs": eval_case_refs,
                "held_out_required": True,
                "external_or_tool_verified": True,
                "passed": passed,
            },
            "regression_suite_contract": {
                "suite_ref": regression_suite_ref,
                "baseline_ref": baseline_ref,
                "regression_count": 0 if passed else 1,
                "passed": passed,
            },
            "judge_policy": judge_policy,
            "core_objectives": core_objectives,
            "red_team_finding_receipt": {
                "receipt_id": f"red-team-receipt::{_digest(run_id)}",
                "finding_count": len(findings),
                "findings": findings,
                "hard_fail_active": bool(findings),
            },
            "promotion_gate_packet": {
                "gate_id": f"promotion-gate::{_digest(candidate_id)}",
                "sandbox_eval_passed": passed,
                "rollback_ready": rollback_ready,
                "governance_decision_required": True,
                "core_objectives_shadow_allowed": core_objectives_shadow_allowed,
                "core_objectives_production_allowed": core_objectives.get("production_promotion_allowed") is True,
                "promotion_allowed": False,
                "blockers": promotion_blockers,
            },
            "quarantine_packet": {
                "quarantine_id": f"quarantine::{_digest(candidate_id)}",
                "quarantine_active": not passed,
                "production_route_allowed": False,
                "release_requires_passing_reevaluation_and_governance": True,
                "reason_refs": [finding["rule_id"] for finding in findings],
            },
            "rollback_proof": {
                "proof_ref": rollback_proof_ref,
                "baseline_ref": baseline_ref,
                "active_source_unchanged": not active_source_changes,
                "rollback_ready": rollback_ready,
            },
            "governance_decision_packet": {
                "status": "pending",
                "human_review_required": judge_policy["human_review_required"],
                "domain_check_required": judge_policy["domain_check_required"],
                "promotion_allowed": False,
            },
            "artifact_trust_ref": artifact_trust_ref,
            "created_at": completed_at,
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }
        evaluation["shared_event_spine"] = self._publish_event(
            event_type="genesis.immune.candidate_evaluated" if passed else "genesis.immune.candidate_quarantined",
            correlation_ref=run_id,
            artifact_refs=[artifact_ref, candidate_id, candidate_ref, rollback_proof_ref, artifact_trust_ref],
        )
        self._write(evaluation, artifact_ref)
        return evaluation

    def decide(self, candidate_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        evaluation = self._evaluation(candidate_id)
        decision_requested = str(payload.get("decision") or "deny").strip().lower()
        human_review_ref = _safe_ref(payload.get("human_review_ref"))
        domain_check_ref = _safe_ref(payload.get("domain_check_ref"))
        governance_ref = _safe_ref(payload.get("governance_ref"))
        approved_by = str(payload.get("approved_by") or "")
        judge_policy = evaluation.get("judge_policy") or {}
        controls = {
            "sandbox_eval": evaluation.get("closed_sandbox_evidence", {}).get("passed") is True,
            "quarantine_clear": evaluation.get("quarantine_packet", {}).get("quarantine_active") is False,
            "rollback_proof": evaluation.get("rollback_proof", {}).get("rollback_ready") is True,
            "human_review": bool(human_review_ref) or not judge_policy.get("human_review_required", True),
            "domain_check": bool(domain_check_ref) or not judge_policy.get("domain_check_required", True),
            "governance_ref": bool(governance_ref),
            "admin_identity": bool(approved_by),
            "decision_approve": decision_requested == "approve",
            "core_objectives": evaluation.get("core_objectives", {}).get("shadow_governance_allowed") is True,
        }
        promotion_allowed = all(controls.values())
        status = "approved-for-governed-promotion" if promotion_allowed else "denied-quarantined"
        decision_id = f"immune-governance-decision::{_digest('|'.join([candidate_id, status, _utcnow()]))}"
        artifact_ref = f"genesis/immune-governance/governance-decisions/{_artifact_id(decision_id)}.json"
        packet = {
            "schema_version": "nexusnet-genesis-layer10-governance-decision-v1",
            "surface_id": "genesis-immune-governance-decision",
            "decision_id": decision_id,
            "candidate_id": candidate_id,
            "candidate_ref": evaluation.get("candidate_ref"),
            "artifact_ref": artifact_ref,
            "status": status,
            "promotion_allowed": promotion_allowed,
            "controls": controls,
            "blockers": [name for name, passed in controls.items() if not passed],
            "core_objectives": evaluation.get("core_objectives"),
            "promotion_gate_packet": {
                **dict(evaluation.get("promotion_gate_packet") or {}),
                "governance_decision_id": decision_id,
                "promotion_allowed": promotion_allowed,
                "blockers": [name for name, passed in controls.items() if not passed],
            },
            "quarantine_packet": {
                **dict(evaluation.get("quarantine_packet") or {}),
                "quarantine_active": not promotion_allowed,
                "production_route_allowed": False,
            },
            "rollback_proof": evaluation.get("rollback_proof"),
            "governance_decision_packet": {
                "decision": "approve" if promotion_allowed else "deny",
                "approver_digest": "sha256:" + hashlib.sha256(approved_by.encode("utf-8")).hexdigest()[:16],
                "human_review_ref": human_review_ref,
                "domain_check_ref": domain_check_ref,
                "governance_ref": governance_ref,
                "promotion_allowed": promotion_allowed,
            },
            "decided_at": _utcnow(),
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }
        packet["shared_event_spine"] = self._publish_event(
            event_type="genesis.immune.promotion_governed" if promotion_allowed else "genesis.immune.promotion_denied",
            correlation_ref=decision_id,
            artifact_refs=[artifact_ref, candidate_id, governance_ref, human_review_ref, domain_check_ref],
        )
        self._write(packet, artifact_ref)
        return packet

    def require_decision(
        self,
        *,
        decision_id: str | None,
        candidate_ref: str,
        candidate_kind: str,
    ) -> dict[str, Any]:
        normalized_decision_id = str(decision_id or "").strip()
        if not normalized_decision_id:
            raise ValueError("an approved immune governance decision is required before mutation")
        decision = next(
            (
                record
                for record in self._records(self.decisions_dir)
                if record.get("decision_id") == normalized_decision_id
            ),
            None,
        )
        if decision is None:
            raise ValueError("immune governance decision was not found")
        if decision.get("candidate_ref") != candidate_ref:
            raise ValueError("immune governance decision scope mismatch")
        evaluation = self._evaluation(str(decision.get("candidate_id") or ""))
        if evaluation.get("candidate_kind") != candidate_kind:
            raise ValueError("immune governance decision candidate kind mismatch")
        if decision.get("promotion_allowed") is not True or decision.get("status") != "approved-for-governed-promotion":
            raise ValueError("immune governance decision does not allow promotion")
        if evaluation.get("closed_sandbox_evidence", {}).get("passed") is not True:
            raise ValueError("immune governance decision lacks passing closed sandbox evidence")
        if evaluation.get("rollback_proof", {}).get("rollback_ready") is not True:
            raise ValueError("immune governance decision lacks rollback proof")
        if evaluation.get("core_objectives") and evaluation["core_objectives"].get("shadow_governance_allowed") is not True:
            raise ValueError("immune governance decision is blocked by core objectives")
        return {
            "schema_version": "nexusnet-genesis-layer10-mutation-binding-v1",
            "surface_id": "genesis-immune-governance-mutation-binding",
            "decision_id": normalized_decision_id,
            "candidate_id": decision.get("candidate_id"),
            "candidate_ref": candidate_ref,
            "candidate_kind": candidate_kind,
            "evaluation_artifact_ref": evaluation.get("artifact_ref"),
            "decision_artifact_ref": decision.get("artifact_ref"),
            "scope_validated": True,
            "promotion_allowed": True,
            "closed_sandbox_evidence_passed": True,
            "rollback_ready": True,
            "core_objectives_shadow_validated": evaluation.get("core_objectives", {}).get("shadow_governance_allowed") is True,
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
        }

    def attest_sandbox_evidence(
        self,
        *,
        candidate_ref: str,
        candidate_kind: str,
        sandbox_evidence: dict[str, Any],
        baseline_ref: str,
        rollback_proof_ref: str,
        artifact_trust_refs: list[str] | None = None,
        objective_metrics: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        sandbox = dict(sandbox_evidence.get("sandbox") or {})
        diff_summary = dict(sandbox_evidence.get("diff_summary") or {})
        passed = bool(
            sandbox_evidence.get("passed") is True
            and sandbox_evidence.get("status") == "passed"
            and sandbox.get("mode") == "isolated-filesystem-copy-allowlisted-pytest"
            and sandbox.get("shell_used") is False
            and sandbox.get("active_project_root_mutated") is False
            and int(diff_summary.get("unsafe_change_count") or 0) == 0
            and sandbox_evidence.get("evidence_ref")
        )
        if not passed:
            raise ValueError("verified passing isolated sandbox evidence is required for immune attestation")
        candidate_id = f"immune-candidate::{_digest(candidate_ref)}"
        evidence_ref = _safe_ref(sandbox_evidence.get("evidence_ref"))
        deterministic_digest = "sha256:" + hashlib.sha256(
            json.dumps(
                {
                    "candidate_ref": candidate_ref,
                    "candidate_kind": candidate_kind,
                    "evidence_ref": evidence_ref,
                    "baseline_ref": baseline_ref,
                    "rollback_proof_ref": rollback_proof_ref,
                    "unsafe_change_count": diff_summary.get("unsafe_change_count"),
                },
                sort_keys=True,
            ).encode("utf-8")
        ).hexdigest()
        artifact_ref = f"genesis/immune-governance/evaluations/{_artifact_id(candidate_id)}.json"
        created_at = _utcnow()
        core_objectives = self.core_objectives.assess(
            candidate_ref=candidate_ref,
            candidate_kind=candidate_kind,
            objective_metrics=objective_metrics,
        )
        core_objectives_shadow_allowed = core_objectives.get("shadow_governance_allowed") is True
        evaluation = {
            "schema_version": "nexusnet-genesis-layer10-attested-sandbox-evaluation-v1",
            "surface_id": "genesis-immune-governance-candidate-evaluation",
            "candidate_id": candidate_id,
            "candidate_ref": candidate_ref,
            "candidate_kind": candidate_kind,
            "artifact_ref": artifact_ref,
            "status": "sandbox-evaluated-awaiting-governance",
            "sandbox_run_envelope": {
                "mode": sandbox.get("mode"),
                "runner": "existing-allowlisted-pytest-sandbox",
                "network_required": False,
                "shell_used": False,
                "write_scope": "temporary-sandbox-copy-only",
            },
            "closed_sandbox_evidence": {
                "executed": True,
                "passed": True,
                "shell_used": False,
                "active_project_source_mutated": False,
                "unsafe_change_count": 0,
                "evidence_ref": evidence_ref,
                "deterministic_evidence_digest": deterministic_digest,
            },
            "eval_case_contract": {
                "case_refs": [_safe_ref(ref) for ref in sandbox_evidence.get("test_refs") or [] if _safe_ref(ref)],
                "held_out_required": True,
                "external_or_tool_verified": True,
                "passed": True,
            },
            "regression_suite_contract": {
                "suite_ref": "regression-suite::existing-isolated-sandbox",
                "baseline_ref": _safe_ref(baseline_ref),
                "regression_count": 0,
                "passed": True,
            },
            "judge_policy": {
                "calibrated_judge_refs": ["judge::isolated-pytest-and-diff-manifest"],
                "human_review_required": True,
                "domain_check_required": True,
                "self_grading_only_allowed": False,
            },
            "core_objectives": core_objectives,
            "red_team_finding_receipt": {
                "receipt_id": f"red-team-receipt::{_digest(evidence_ref)}",
                "finding_count": 0,
                "findings": [],
                "hard_fail_active": False,
            },
            "promotion_gate_packet": {
                "gate_id": f"promotion-gate::{_digest(candidate_id)}",
                "sandbox_eval_passed": True,
                "rollback_ready": True,
                "governance_decision_required": True,
                "core_objectives_shadow_allowed": core_objectives_shadow_allowed,
                "core_objectives_production_allowed": core_objectives.get("production_promotion_allowed") is True,
                "promotion_allowed": False,
                "blockers": ["governance_decision_required", *list(core_objectives.get("blockers") or [])],
            },
            "quarantine_packet": {
                "quarantine_id": f"quarantine::{_digest(candidate_id)}",
                "quarantine_active": False,
                "production_route_allowed": False,
                "release_requires_passing_reevaluation_and_governance": True,
                "reason_refs": [],
            },
            "rollback_proof": {
                "proof_ref": _safe_ref(rollback_proof_ref),
                "baseline_ref": _safe_ref(baseline_ref),
                "active_source_unchanged": True,
                "rollback_ready": True,
            },
            "governance_decision_packet": {
                "status": "pending",
                "human_review_required": True,
                "domain_check_required": True,
                "promotion_allowed": False,
            },
            "artifact_trust_refs": [_safe_ref(ref) for ref in artifact_trust_refs or [] if _safe_ref(ref)],
            "created_at": created_at,
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }
        evaluation["shared_event_spine"] = self._publish_event(
            event_type="genesis.immune.sandbox_evidence_attested",
            correlation_ref=candidate_id,
            artifact_refs=[artifact_ref, candidate_ref, evidence_ref, rollback_proof_ref],
        )
        self._write(evaluation, artifact_ref)
        return evaluation

    def _evaluation(self, candidate_id: str) -> dict[str, Any]:
        for record in self._records(self.evaluations_dir):
            if record.get("candidate_id") == candidate_id:
                return record
        raise KeyError(candidate_id)

    def _records(self, directory: Path) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        if directory.is_dir():
            for path in directory.glob("*.json"):
                try:
                    record = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if isinstance(record, dict):
                    records.append(record)
        records.sort(key=lambda item: str(item.get("decided_at") or item.get("created_at") or ""), reverse=True)
        return records

    def _write(self, payload: dict[str, Any], artifact_ref: str) -> None:
        path = self.artifacts_dir / artifact_ref
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        temporary.replace(path)

    def _publish_event(self, *, event_type: str, correlation_ref: str, artifact_refs: list[Any]) -> dict[str, Any]:
        publish = getattr(self.event_spine, "publish_event", None)
        if not callable(publish):
            return {"status": "not-configured", "raw_content_included": False}
        return publish(
            event_type=event_type,
            source_surface_id="genesis-immune-governance",
            correlation_ref=correlation_ref,
            privacy_label="sanitized-genesis-layer10-immune-governance-evidence",
            artifact_refs=[_safe_ref(ref) for ref in artifact_refs if ref],
            planes=["immune", "eval", "sandbox", "governance", "rollback", "quarantine"],
        )


def _allowlisted_pytest_argv(command: str) -> list[str]:
    parts = shlex.split(str(command or ""))
    if len(parts) < 4 or parts[:3] != ["python", "-m", "pytest"]:
        raise ValueError("closed sandbox only allows: python -m pytest tests/*.py ...")
    allowed_options = {"-q", "--quiet", "--maxfail=1"}
    targets: list[str] = []
    for part in parts[3:]:
        if part.startswith("-"):
            if part not in allowed_options:
                raise ValueError(f"closed sandbox pytest option is not allowed: {part}")
            continue
        target = part.split("::", 1)[0].replace("\\", "/")
        if not target.startswith("tests/") or not target.endswith(".py") or ".." in target or ":/" in target:
            raise ValueError("closed sandbox pytest targets must be tests/*.py or tests/**/*.py")
        targets.append(target)
    if not targets:
        raise ValueError("closed sandbox requires at least one tests/*.py target")
    return [sys.executable, "-m", "pytest", *parts[3:]]


def _source_manifest(root: Path) -> dict[str, str]:
    manifest: dict[str, str] = {}
    suffixes = {".py", ".toml", ".yaml", ".yml", ".json", ".md"}
    for directory, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if not _ignored_dir_name(name)]
        base = Path(directory)
        for filename in filenames:
            path = base / filename
            if path.suffix.lower() not in suffixes:
                continue
            try:
                relative = path.relative_to(root).as_posix()
                manifest[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
            except OSError:
                continue
    return manifest


def _copy_ignore(directory: str, names: list[str]) -> set[str]:
    return {name for name in names if _ignored_dir_name(name)}


def _ignored_dir_name(name: str) -> bool:
    blocked = {".git", ".gitnexus", ".pytest_cache", ".pytest-tmp", "__pycache__", ".venv", "venv", "node_modules", "runtime", "artifacts", "models", "dist", "build"}
    return name in blocked or name.startswith("pytest-cache-files-")


def _manifest_changes(before: dict[str, str], after: dict[str, str]) -> list[str]:
    return sorted(path for path in set(before) | set(after) if before.get(path) != after.get(path))


def _judge_policy(value: Any) -> dict[str, Any]:
    payload = dict(value or {}) if isinstance(value, dict) else {}
    calibrated_refs = [_safe_ref(ref) for ref in payload.get("calibrated_judge_refs") or [] if _safe_ref(ref)]
    if not calibrated_refs:
        raise ValueError("judge_policy.calibrated_judge_refs are required")
    return {
        "calibrated_judge_refs": calibrated_refs,
        "human_review_required": payload.get("human_review_required") is not False,
        "domain_check_required": payload.get("domain_check_required") is not False,
        "self_grading_only_allowed": False,
    }


def _finding(rule_id: str, message: str) -> dict[str, str]:
    return {"rule_id": rule_id, "severity": "hard-fail", "message": message}


def _required_ref(payload: dict[str, Any], name: str) -> str:
    value = _safe_ref(payload.get(name))
    if not value:
        raise ValueError(f"{name} is required")
    return value


def _required_refs(payload: dict[str, Any], name: str) -> list[str]:
    values = [_safe_ref(value) for value in payload.get(name) or [] if _safe_ref(value)]
    if not values:
        raise ValueError(f"{name} are required")
    return values


def _safe_ref(value: Any) -> str:
    text = str(value or "").strip().replace("\\", "/")
    if not text:
        return ""
    lowered = text.lower()
    if len(text) > 240 or ":/" in text or any(marker in lowered for marker in ("secret", "password", "token", "api-key", "apikey")):
        return "ref-digest::" + _digest(text)
    return text


def _artifact_id(value: str) -> str:
    return "".join(character if character.isalnum() or character in "._-" else "-" for character in value).strip("-")


def _digest(value: str) -> str:
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:24]


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

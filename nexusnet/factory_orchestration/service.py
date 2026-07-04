from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import new_id, utcnow


class FactoryOrchestrationService:
    """Governed issue-to-validation factory metadata.

    This assimilates Dark Factory/Archon-style mechanics as auditable control
    records. V1 does not spawn agents, merge PRs, push branches, deploy, or
    execute package/tool commands without the existing gateway/product-sweep path.
    """

    def __init__(self, *, artifacts_dir: Path | str, events: Any | None = None):
        self.artifacts_dir = Path(artifacts_dir)
        self.output_dir = self.artifacts_dir / "factory-orchestration"
        self.events = events

    def summary(self, *, limit: int = 100) -> dict[str, Any]:
        records = self._records(limit=limit)
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "record_count": len(records),
            "status_counts": self._counts(records, "status"),
            "record_type_counts": self._counts(records, "record_type"),
            "dark_factory_patterns_assimilated": [
                "github_issue_as_factory_intake",
                "batch_triage_before_dispatch",
                "scheduled_orchestrator_cadence",
                "workflow_packaging_with_deterministic_nodes",
                "real_reproduction_before_issue_comment",
                "browser_e2e_hard_gate",
                "protected_file_escalation",
                "deployment_rollback_reopen_loop",
                "token_model_budget_scorecard",
                "weekly_comprehensive_regression",
            ],
            "execution_allowed": False,
            "mutation_allowed": False,
            "autonomous_merge_allowed": False,
            "deployment_allowed": False,
            "latest_record": records[0] if records else None,
            "items": records,
        }

    def compact_summary(self, *, limit: int = 50) -> dict[str, Any]:
        payload = self.summary(limit=limit)
        return {
            "status_label": payload["status_label"],
            "record_count": payload["record_count"],
            "status_counts": payload["status_counts"],
            "record_type_counts": payload["record_type_counts"],
            "autonomous_merge_allowed": False,
            "deployment_allowed": False,
            "execution_allowed": False,
            "mutation_allowed": False,
            "latest_record": payload["latest_record"],
        }

    def triage_batch(
        self,
        *,
        source: dict[str, Any] | None = None,
        issues: list[dict[str, Any]] | None = None,
        cadence: str = "scheduled_batch",
        max_parallel: int = 1,
        priority_rules: dict[str, Any] | None = None,
        protected_paths: list[str] | None = None,
        token_budget: dict[str, Any] | None = None,
        linked_trace_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        issues = [dict(issue) for issue in (issues or [])]
        record = self._base_record(
            record_type="triage",
            status="triaged_metadata_only",
            source=source,
            linked_trace_ids=linked_trace_ids,
        )
        record.update(
            {
                "queue": {
                    "issue_count": len(issues),
                    "issues": issues,
                    "cadence": cadence,
                    "max_parallel": max(1, int(max_parallel or 1)),
                    "dispatch_mode": "scheduled_batch_metadata_only",
                    "batch_context_required": True,
                },
                "priority_decision": self._priority_decision(issues, priority_rules or {}),
                "protected_paths": {
                    "patterns": [str(item) for item in (protected_paths or [])],
                    "mutation_requires_human": True,
                    "touches_escalate_to": "human_review_and_gateway",
                },
                "validation_requirements": {
                    "plan_required": True,
                    "fresh_context_review_required": True,
                    "adversarial_review_required": True,
                    "browser_e2e_required_when_ui": True,
                    "static_only_never_confirms_user_facing_bug": True,
                },
                "deployment_gate": self._deployment_gate(),
                "model_budget": self._model_budget(token_budget or {}),
                "risk_flags": [
                    "autonomous_merge",
                    "unbounded_token_spend",
                    "protected_file_mutation",
                    "agent_queue_starvation",
                ],
            }
        )
        self._finalize(record, "factory_orchestration.triage_recorded")
        return {"status_label": "STRONG ACCEPTED DIRECTION", "record": record}

    def reproduction_check(
        self,
        *,
        issue_ref: str,
        reproduction_surface: str = "cli",
        required_tools: list[str] | None = None,
        comment_policy: str = "draft_evidence_only",
        e2e_required: bool = True,
        static_analysis_only: bool = False,
        linked_trace_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        status = "blocked_real_reproduction_required" if static_analysis_only and e2e_required else "reproduction_planned_metadata_only"
        record = self._base_record(record_type="reproduction_check", status=status, linked_trace_ids=linked_trace_ids)
        record.update(
            {
                "source": {
                    **record["source"],
                    "issue_ref": issue_ref,
                    "reproduction_surface": reproduction_surface,
                },
                "queue": {"issue_count": 1, "issues": [{"issue_ref": issue_ref}], "dispatch_mode": "manual_metadata_only"},
                "priority_decision": {"ordered_issue_refs": [issue_ref], "reason": "single issue reproduction"},
                "protected_paths": {"patterns": [], "mutation_requires_human": True},
                "validation_requirements": {
                    "real_reproduction_required": True,
                    "static_analysis_sufficient": False,
                    "e2e_required": bool(e2e_required),
                    "required_tools": [str(item) for item in (required_tools or [])],
                    "issue_comment_allowed": "draft_only_after_evidence" if comment_policy == "draft_evidence_only" else comment_policy,
                    "evidence_artifacts_required": ["logs", "commands", "screenshots_or_cli_output"],
                },
                "deployment_gate": self._deployment_gate(),
                "model_budget": self._model_budget({}),
                "risk_flags": ["phantom_reproduction", "misleading_issue_comment", "tool_execution_request"],
            }
        )
        self._finalize(record, "factory_orchestration.reproduction_recorded")
        return {"status_label": "STRONG ACCEPTED DIRECTION", "record": record}

    def pr_validation(
        self,
        *,
        pr_ref: str,
        required_validation_profiles: list[str] | None = None,
        browser_validation_required: bool = False,
        start_service_status: str = "not_started",
        deployment_target: str | None = None,
        merge_policy: str | None = None,
        linked_trace_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        failed_required_browser = browser_validation_required and start_service_status != "ready"
        status = "blocked_validation_failed" if failed_required_browser else "pr_validation_planned_metadata_only"
        record = self._base_record(record_type="pr_validation", status=status, linked_trace_ids=linked_trace_ids)
        record.update(
            {
                "source": {
                    **record["source"],
                    "pr_ref": pr_ref,
                    "deployment_target": deployment_target,
                    "merge_policy_requested": merge_policy,
                },
                "queue": {"issue_count": 0, "pr_ref": pr_ref, "dispatch_mode": "pr_review_metadata_only"},
                "priority_decision": {"ordered_issue_refs": [], "reason": "pull request validation"},
                "protected_paths": {"patterns": [], "mutation_requires_human": True},
                "validation_requirements": {
                    "required_validation_profiles": [str(item) for item in (required_validation_profiles or [])],
                    "browser_validation_required": bool(browser_validation_required),
                    "browser_validation_hard_gate": bool(browser_validation_required),
                    "start_service_status": start_service_status,
                    "e2e_skipped_is_failure": bool(browser_validation_required),
                    "fresh_context_review_required": True,
                    "adversarial_review_required": True,
                },
                "deployment_gate": self._deployment_gate(blocked=failed_required_browser),
                "model_budget": self._model_budget({}),
                "risk_flags": ["phantom_validation", "autonomous_merge", "ungoverned_deployment"],
            }
        )
        self._finalize(record, "factory_orchestration.pr_validation_recorded")
        return {"status_label": "STRONG ACCEPTED DIRECTION", "record": record}

    def _base_record(
        self,
        *,
        record_type: str,
        status: str,
        source: dict[str, Any] | None = None,
        linked_trace_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        record_id = new_id("factory")
        trace_ids = list(linked_trace_ids or []) or [f"trace_{record_id}"]
        source_payload = {
            "source_name": "Dark Factory / Archon assimilation",
            "source_url": "https://github.com/coleam00/Archon",
            "observed_at": utcnow().isoformat(),
            **(source or {}),
        }
        return {
            "record_id": record_id,
            "record_type": record_type,
            "status": status,
            "source": source_payload,
            "policy_path": [
                {
                    "stage": "factory-orchestration",
                    "decision": "hold",
                    "reason": "agent execution, PR writes, pushes, merges, deployments, and package/tool execution are deny-by-default",
                }
            ],
            "approval_path": {"decision": "not_requested", "human_approval_is_not_execution_authority": True},
            "product_sweep_gate_ids": [
                "phase-9-product-ops",
                "parallel-run-gate",
                "gateway-policy",
                "product-sweep-security",
                "operator-surface-truthfulness",
            ],
            "telemetry_trace_ids": trace_ids,
            "execution_authority": self._execution_authority(record_type),
            "execution_allowed": False,
            "mutation_allowed": False,
            "created_at": utcnow().isoformat(),
        }

    def _execution_authority(self, record_type: str) -> dict[str, Any]:
        capability_map = {
            "triage": [
                "factory_orchestration",
                "autonomous_agent_execution",
                "pr_push",
                "pr_merge",
                "deployment",
            ],
            "reproduction_check": [
                "factory_orchestration",
                "autonomous_agent_execution",
                "network_write",
                "file_write",
            ],
            "pr_validation": [
                "factory_orchestration",
                "autonomous_agent_execution",
                "pr_push",
                "pr_merge",
                "deployment",
            ],
        }
        return {
            "required": True,
            "service": "execution_authority",
            "lease_endpoint": "/ops/brain/execution-authority/leases/request",
            "required_capabilities": capability_map.get(record_type, ["factory_orchestration"]),
            "execution_allowed": False,
            "mutation_allowed": False,
            "reason": "Factory work requires scoped expiring leases before agent execution, writes, PR actions, or deployment.",
        }

    def _priority_decision(self, issues: list[dict[str, Any]], priority_rules: dict[str, Any]) -> dict[str, Any]:
        def score(issue: dict[str, Any]) -> int:
            labels = [str(item).lower() for item in issue.get("labels", []) or []]
            title = str(issue.get("title") or "").lower()
            value = 0
            for key, raw_score in priority_rules.items():
                if str(key).lower() in labels or str(key).lower() in title:
                    try:
                        value += int(raw_score)
                    except (TypeError, ValueError):
                        value += 0
            if "bug" in labels or "broken" in title or "crash" in title:
                value += 50
            if "security" in labels:
                value += 100
            return value

        ranked = sorted(issues, key=score, reverse=True)
        return {
            "ordered_issue_refs": [str(issue.get("issue_ref") or issue.get("id") or issue.get("title")) for issue in ranked],
            "scores": {
                str(issue.get("issue_ref") or issue.get("id") or issue.get("title")): score(issue)
                for issue in ranked
            },
            "batch_triage_required": True,
            "reason": "compare issues as a batch before dispatching scarce agents/tokens",
        }

    def _model_budget(self, token_budget: dict[str, Any]) -> dict[str, Any]:
        return {
            "token_budget": token_budget,
            "model_candidates": list(token_budget.get("model_candidates", []) or []),
            "cost_cap_required": True,
            "provider_swap_allowed": "governed_metadata_only",
            "live_provider_registration_allowed": False,
        }

    def _deployment_gate(self, *, blocked: bool = True) -> dict[str, Any]:
        return {
            "merge_allowed": False,
            "deployment_allowed": False,
            "autonomous_push_allowed": False,
            "autonomous_pr_creation_allowed": False,
            "reopen_or_rollback_required": bool(blocked),
            "human_review_required_for_promotion": True,
        }

    def _finalize(self, record: dict[str, Any], event_type: str) -> None:
        artifact_path = self.output_dir / f"{record['record_id']}.json"
        record["artifact_path"] = str(artifact_path)
        self._write(record, artifact_path)
        self._event(event_type, record)

    def _event(self, event_type: str, record: dict[str, Any]) -> None:
        if not self.events:
            return
        self.events.record(
            event_type=event_type,
            subject=f"factory_orchestration:{record['record_id']}",
            trace_ids=record.get("telemetry_trace_ids") or [],
            payload={
                "record_id": record["record_id"],
                "record_type": record["record_type"],
                "status": record["status"],
                "execution_allowed": False,
                "mutation_allowed": False,
                "decision": "hold",
                "artifact_path": record.get("artifact_path"),
            },
        )

    def _records(self, *, limit: int) -> list[dict[str, Any]]:
        if not self.output_dir.exists():
            return []
        records: list[dict[str, Any]] = []
        for path in sorted(self.output_dir.glob("factory_*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
            try:
                records.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                continue
            if len(records) >= limit:
                break
        return records

    def _write(self, record: dict[str, Any], path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record, indent=2), encoding="utf-8")

    def _counts(self, records: list[dict[str, Any]], key: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for record in records:
            value = str(record.get(key) or "unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts

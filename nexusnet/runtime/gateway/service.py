from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import new_id, utcnow
from nexusnet.recipes.reports import build_recipe_execution_report


class LocalRuntimeGateway:
    def __init__(
        self,
        *,
        skill_registry: Any,
        policy_engine: Any,
        approvals: Any,
        skill_catalog: Any | None = None,
        extension_catalog: Any | None = None,
        permission_service: Any | None = None,
        sandbox_service: Any | None = None,
        guardrail_service: Any | None = None,
        adversary_review: Any | None = None,
        execution_store: Any | None = None,
        artifacts_dir: Any | None = None,
    ):
        self.skill_registry = skill_registry
        self.policy_engine = policy_engine
        self.approvals = approvals
        self.skill_catalog = skill_catalog
        self.extension_catalog = extension_catalog
        self.permission_service = permission_service
        self.sandbox_service = sandbox_service
        self.guardrail_service = guardrail_service
        self.adversary_review = adversary_review
        self.execution_store = execution_store
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self._resolution_log: list[dict[str, Any]] = []

    def resolve(
        self,
        *,
        agent_id: str,
        workspace_id: str = "default",
        requested_tools: list[str] | None = None,
        requested_extensions: list[str] | None = None,
        require_user_approval: bool = False,
        trigger_source: str = "gateway:direct",
        linked_trace_ids: list[str] | None = None,
        record_gateway_flow: bool = False,
    ) -> dict[str, Any]:
        visible = self.skill_registry.visible_packages(agent_id=agent_id, workspace_id=workspace_id)
        requested_tools = list(requested_tools or [])
        requested_extensions = list(requested_extensions or [])
        extension_resolution = self._extension_resolution(
            workspace_id=workspace_id,
            requested_extensions=requested_extensions,
        )
        effective_requested_tools = sorted(set([*requested_tools, *(extension_resolution.get("allowed_tools") or [])]))
        skill_policy = self.policy_engine.evaluate(
            agent_id=agent_id,
            workspace_id=workspace_id,
            requested_tools=effective_requested_tools,
            visible_packages=visible,
            require_user_approval=require_user_approval,
        )
        policy = self._merge_policy_decisions(
            skill_policy=skill_policy,
            extension_resolution=extension_resolution,
        )
        risk_level = self._risk_level(
            effective_requested_tools=effective_requested_tools,
            requested_extensions=requested_extensions,
            fallback_reason=policy.get("fallback_reason"),
        )
        permission_review = (
            self.permission_service.review_request(
                requested_tools=effective_requested_tools,
                risk_level=risk_level,
            )
            if self.permission_service is not None
            else None
        )
        adversary_review = self._adversary_review(
            agent_id=agent_id,
            effective_requested_tools=effective_requested_tools,
            requested_extensions=requested_extensions,
            extension_resolution=extension_resolution,
            permission_review=permission_review,
            policy=policy,
            require_user_approval=require_user_approval,
            risk_level=risk_level,
        )
        approvals_snapshot = self.approvals.snapshot(limit=10)
        resolution_id = new_id("gateway")
        gateway_decision_path = self._gateway_decision_path(
            resolution_id=resolution_id,
            requested_tools=requested_tools,
            effective_requested_tools=effective_requested_tools,
            extension_resolution=extension_resolution,
            policy=policy,
            permission_review=permission_review,
            adversary_review=adversary_review,
            trigger_source=trigger_source,
        )
        approval_path = {
            "decision": policy.get("decision"),
            "require_user_approval": require_user_approval,
            "approval_required_states": approvals_snapshot.get("approval_required_states", []),
            "policy_path": policy.get("policy_path", []),
            "fallback_reason": policy.get("fallback_reason"),
        }
        flow_families = self._flow_families(
            trigger_source=trigger_source,
            requested_tools=requested_tools,
            requested_extensions=requested_extensions,
            effective_requested_tools=effective_requested_tools,
            extension_resolution=extension_resolution,
            approval_path=approval_path,
            adversary_review=adversary_review,
        )
        resolution = {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "resolution_id": resolution_id,
            "created_at": utcnow().isoformat(),
            "gateway_pattern": "local-control-plane",
            "agent_id": agent_id,
            "workspace_id": workspace_id,
            "trigger_source": trigger_source,
            "requested_tools": requested_tools,
            "requested_extensions": requested_extensions,
            "effective_requested_tools": effective_requested_tools,
            "visible_skill_packages": visible,
            "selected_skill_packages": policy.get("matched_packages", []),
            "selected_extension_bundles": extension_resolution.get("selected_bundles", []),
            "extension_bundle_ids": extension_resolution.get("selected_bundle_ids", []),
            "policy": policy,
            "skill_policy": skill_policy,
            "extension_policy": extension_resolution,
            "approvals": approvals_snapshot,
            "skill_catalog": self.skill_catalog.summary() if self.skill_catalog is not None else None,
            "extension_catalog": self.extension_catalog.summary(workspace_id=workspace_id) if self.extension_catalog is not None else None,
            "approval_path": approval_path,
            "permission_review": permission_review,
            "sandbox": self.sandbox_service.summary() if self.sandbox_service is not None else None,
            "persistent_guardrails": self.guardrail_service.summary() if self.guardrail_service is not None else None,
            "adversary_review": adversary_review or (self.adversary_review.summary() if self.adversary_review is not None else None),
            "fallback_reason": policy.get("fallback_reason"),
            "policy_path": policy.get("policy_path", []),
            "gateway_decision_path": gateway_decision_path,
            "approval_fallback_chain": self._approval_fallback_chain(
                policy=policy,
                approval_path=approval_path,
                permission_review=permission_review,
                adversary_review=adversary_review,
            ),
            "flow_families": flow_families,
            "execution_path": self._execution_path(
                requested_tools=requested_tools,
                requested_extensions=requested_extensions,
                effective_requested_tools=effective_requested_tools,
                extension_resolution=extension_resolution,
                permission_review=permission_review,
                adversary_review=adversary_review,
            ),
            "linked_trace_ids": list(linked_trace_ids or []),
            "linked_report_ids": sorted(
                {
                    *[report_id for report_id in extension_resolution.get("linked_report_ids", []) if report_id],
                    *(
                        [((adversary_review.get("report") or {}).get("report_id"))]
                        if isinstance(adversary_review, dict) and (adversary_review.get("report") or {}).get("report_id")
                        else []
                    ),
                }
            ),
            "adversary_review_report_ids": (
                [((adversary_review.get("report") or {}).get("report_id"))]
                if isinstance(adversary_review, dict) and (adversary_review.get("report") or {}).get("report_id")
                else []
            ),
            "extension_provenance": extension_resolution.get("selected_bundle_provenance", []),
            "compare_refs": {
                "summary": "/ops/brain/gateway",
                "history": "/ops/brain/gateway/history",
                "history_detail_template": "/ops/brain/gateway/history/{execution_id}",
                "history_compare": "/ops/brain/gateway/history/compare",
                "extensions": "/ops/brain/extensions",
                "extension_detail_template": "/ops/brain/extensions/{bundle_id}",
                "extension_policy_history": "/ops/brain/extensions/policy-history",
                "extension_policy_history_compare": "/ops/brain/extensions/policy-history/compare",
                "extension_policy_rollouts": "/ops/brain/extensions/policy-rollouts",
                "extension_certifications": "/ops/brain/extensions/certifications",
                "extension_certification_compare": "/ops/brain/extensions/certifications/compare",
                "adversary_review_compare": "/ops/brain/security/adversary-reviews/compare",
            },
        }
        artifact_path = self._write_resolution_artifact(resolution)
        resolution["artifact_path"] = str(artifact_path)
        if record_gateway_flow:
            execution_history = self._record_gateway_execution(resolution=resolution)
            if execution_history is not None:
                resolution["execution_history"] = execution_history
        self._resolution_log.insert(0, resolution)
        self._resolution_log = self._resolution_log[:50]
        return resolution

    def summary(self, *, session_id: str | None = None, agent_id: str = "standard-wrapper-agent", workspace_id: str = "default") -> dict[str, Any]:
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "session_id": session_id,
            "gateway_pattern": "local-control-plane",
            "packages": self.skill_registry.visible_packages(agent_id=agent_id, workspace_id=workspace_id),
            "skill_catalog": self.skill_catalog.summary() if self.skill_catalog is not None else None,
            "extension_catalog": self.extension_catalog.summary(workspace_id=workspace_id) if self.extension_catalog is not None else None,
            "approvals": self.approvals.snapshot(limit=10),
            "permissions": self.permission_service.summary() if self.permission_service is not None else None,
            "sandbox": self.sandbox_service.summary() if self.sandbox_service is not None else None,
            "persistent_guardrails": self.guardrail_service.summary() if self.guardrail_service is not None else None,
            "adversary_review": self.adversary_review.summary() if self.adversary_review is not None else None,
            "recent_resolutions": self._resolution_log[:10],
            "history": self.history_summary(agent_id=agent_id, workspace_id=workspace_id, limit=10),
            "compare_refs": {
                "history": "/ops/brain/gateway/history",
                "history_detail_template": "/ops/brain/gateway/history/{execution_id}",
                "history_compare": "/ops/brain/gateway/history/compare",
                "extensions": "/ops/brain/extensions",
                "extension_detail_template": "/ops/brain/extensions/{bundle_id}",
            },
        }

    def history_summary(
        self,
        *,
        agent_id: str | None = None,
        workspace_id: str | None = None,
        trigger_source: str | None = None,
        status: str | None = None,
        limit: int = 12,
    ) -> dict[str, Any]:
        items = self._history_items(
            agent_id=agent_id,
            workspace_id=workspace_id,
            trigger_source=trigger_source,
            status=status,
            limit=limit,
        )
        latest = items[0] if items else {}
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "execution_count": len(items),
            "latest_execution": latest or None,
            "latest_report_id": ((latest.get("report") or {}).get("report_id")),
            "latest_resolution_id": latest.get("gateway_resolution_id"),
            "latest_extension_bundle_ids": latest.get("extension_bundle_ids", []),
            "latest_linked_trace_ids": latest.get("linked_trace_ids", []),
            "latest_linked_report_ids": latest.get("linked_report_ids", []),
            "latest_adversary_report_ids": latest.get("adversary_review_report_ids", []),
            "latest_extension_policy_set_ids": latest.get("extension_policy_set_ids", []),
            "latest_extension_bundle_families": latest.get("extension_bundle_families", []),
            "latest_flow_families": latest.get("flow_families", []),
            "flow_family_counts": self._flow_family_counts(items),
            "latest_by_flow_family": self._latest_by_flow_family(items),
            "compare_refs": {
                "history": "/ops/brain/gateway/history",
                "history_detail_template": "/ops/brain/gateway/history/{execution_id}",
                "history_compare": "/ops/brain/gateway/history/compare",
            },
            "items": items,
        }

    def history_detail(self, execution_id: str) -> dict[str, Any] | None:
        if self.execution_store is None:
            return None
        record = self.execution_store.get(execution_id)
        if record is None or record.get("execution_kind") != "gateway":
            return None
        report = record.get("report") or {}
        payload = None
        markdown = None
        if report.get("payload_path"):
            try:
                payload = json.loads(Path(report["payload_path"]).read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                payload = None
        if report.get("markdown_path"):
            try:
                markdown = Path(report["markdown_path"]).read_text(encoding="utf-8")
            except OSError:
                markdown = None
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "item": record,
            "report_payload": payload,
            "report_markdown": markdown,
            "compare_refs": {
                "history": "/ops/brain/gateway/history",
                "history_compare": "/ops/brain/gateway/history/compare",
            },
        }

    def compare_history(self, left_execution_id: str, right_execution_id: str) -> dict[str, Any] | None:
        if self.execution_store is None:
            return None
        comparison = self.execution_store.compare(left_execution_id, right_execution_id)
        if comparison is None:
            return None
        if any(card.get("execution_kind") != "gateway" for card in [comparison.get("left", {}), comparison.get("right", {})]):
            return None
        return {
            **comparison,
            "compare_refs": {
                "history": "/ops/brain/gateway/history",
                "history_detail_template": "/ops/brain/gateway/history/{execution_id}",
            },
        }

    def _extension_resolution(self, *, workspace_id: str, requested_extensions: list[str]) -> dict[str, Any]:
        if self.extension_catalog is not None and requested_extensions:
            return self.extension_catalog.resolve_requested_extensions(
                workspace_id=workspace_id,
                requested_extensions=requested_extensions,
            )
        return {
            "decision": "allow",
            "fallback_reason": None,
            "selected_bundle_ids": [],
            "selected_bundles": [],
            "allowed_tools": [],
            "risk_flags": [],
            "policy_path": [],
            "linked_report_ids": [],
            "selected_bundle_provenance": [],
            "requested_extensions": requested_extensions,
        }

    def _merge_policy_decisions(self, *, skill_policy: dict[str, Any], extension_resolution: dict[str, Any]) -> dict[str, Any]:
        skill_decision = skill_policy.get("decision", "allow")
        extension_decision = extension_resolution.get("decision", "allow")
        if "deny" in {skill_decision, extension_decision}:
            decision = "deny"
            fallback_reason = skill_policy.get("fallback_reason") or extension_resolution.get("fallback_reason") or "policy-deny"
        elif "allow-if-approved" in {skill_decision, extension_decision}:
            decision = "allow-if-approved"
            fallback_reason = extension_resolution.get("fallback_reason") or skill_policy.get("fallback_reason")
        elif "ask" in {skill_decision, extension_decision}:
            decision = "ask"
            fallback_reason = extension_resolution.get("fallback_reason") or skill_policy.get("fallback_reason")
        else:
            decision = "allow"
            fallback_reason = skill_policy.get("fallback_reason") or extension_resolution.get("fallback_reason")
        return {
            **skill_policy,
            "decision": decision,
            "fallback_reason": fallback_reason,
            "policy_path": [
                *(skill_policy.get("policy_path", []) or []),
                *(extension_resolution.get("policy_path", []) or []),
            ],
            "extension_bundle_ids": extension_resolution.get("selected_bundle_ids", []),
            "extension_policy_set_ids": extension_resolution.get("selected_policy_set_ids", []),
            "extension_bundle_families": extension_resolution.get("selected_bundle_families", []),
            "extension_policy_history_ids": extension_resolution.get("selected_policy_history_ids", []),
            "extension_policy_statuses": extension_resolution.get("selected_policy_statuses", []),
            "extension_certification_ids": extension_resolution.get("selected_bundle_certification_ids", []),
            "extension_certification_statuses": extension_resolution.get("selected_bundle_certification_statuses", []),
            "extension_risk_flags": extension_resolution.get("risk_flags", []),
        }

    def _risk_level(
        self,
        *,
        effective_requested_tools: list[str],
        requested_extensions: list[str],
        fallback_reason: str | None,
    ) -> str:
        elevated_tool_families = {
            "shell.exec",
            "powershell.exec",
            "cmd.exec",
            "filesystem.write",
            "filesystem.delete",
            "network.external",
            "http.post",
            "http.request",
            "secrets.read",
            "credentials.read",
            "env.secret",
            "provider.acp",
            "git.commit",
        }
        if (
            any(tool in elevated_tool_families for tool in effective_requested_tools)
            or fallback_reason in {"ambiguous-binding", "extension-outside-allowlist"}
            or len(effective_requested_tools) > 1
            or requested_extensions
        ):
            return "high"
        return "medium"

    def _adversary_review(
        self,
        *,
        agent_id: str,
        effective_requested_tools: list[str],
        requested_extensions: list[str],
        extension_resolution: dict[str, Any],
        permission_review: dict[str, Any] | None,
        policy: dict[str, Any],
        require_user_approval: bool,
        risk_level: str,
    ) -> dict[str, Any] | None:
        if self.adversary_review is None:
            return None
        should_review = bool(
            effective_requested_tools
            or requested_extensions
            or (permission_review and permission_review.get("decision") == "review-required")
            or policy.get("fallback_reason")
        )
        if not should_review:
            return None
        return self.adversary_review.review(
            subject=f"gateway::{agent_id}",
            requested_tools=effective_requested_tools,
            risk_level=(permission_review or {}).get("risk_level", risk_level),
            reviewer_status="unavailable" if require_user_approval else "available",
            summary="Goose-pattern adversary review is fail-closed or escalate in NexusNet.",
            fallback_reason=policy.get("fallback_reason"),
            policy_path=policy.get("policy_path", []),
            multi_step=len(effective_requested_tools) > 1 or len(requested_extensions) > 1,
            approval_requested=require_user_approval,
            approval_required=bool(
                (permission_review and permission_review.get("decision") == "review-required")
                or policy.get("decision") in {"ask", "allow-if-approved"}
            ),
            allowed_tools=sorted(set([*effective_requested_tools, *(extension_resolution.get("allowed_tools") or [])])),
            requested_extensions=requested_extensions,
            allowed_extensions=extension_resolution.get("selected_bundle_ids", []),
            trigger_source="gateway-resolve",
        )

    def _gateway_decision_path(
        self,
        *,
        resolution_id: str,
        requested_tools: list[str],
        effective_requested_tools: list[str],
        extension_resolution: dict[str, Any],
        policy: dict[str, Any],
        permission_review: dict[str, Any] | None,
        adversary_review: dict[str, Any] | None,
        trigger_source: str,
    ) -> list[dict[str, Any]]:
        return [
            {
                "resolution_id": resolution_id,
                "stage": "gateway-resolution",
                "trigger_source": trigger_source,
                "decision": policy.get("decision"),
                "fallback_reason": policy.get("fallback_reason"),
                "requested_tools": requested_tools,
                "effective_requested_tools": effective_requested_tools,
                "requested_extensions": extension_resolution.get("requested_extensions", []),
                "selected_extension_bundles": extension_resolution.get("selected_bundle_ids", []),
                "selected_policy_set_ids": extension_resolution.get("selected_policy_set_ids", []),
                "selected_bundle_families": extension_resolution.get("selected_bundle_families", []),
                "selected_policy_history_ids": extension_resolution.get("selected_policy_history_ids", []),
                "selected_policy_statuses": extension_resolution.get("selected_policy_statuses", []),
                "selected_bundle_certification_ids": extension_resolution.get("selected_bundle_certification_ids", []),
                "selected_bundle_certification_statuses": extension_resolution.get("selected_bundle_certification_statuses", []),
                "permission_decision": ((permission_review or {}).get("decision")),
                "adversary_decision": ((adversary_review or {}).get("decision")),
            }
        ]

    def _approval_fallback_chain(
        self,
        *,
        policy: dict[str, Any],
        approval_path: dict[str, Any],
        permission_review: dict[str, Any] | None,
        adversary_review: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        return [
            {
                "stage": "policy",
                "decision": policy.get("decision"),
                "fallback_reason": policy.get("fallback_reason"),
            },
            {
                "stage": "approval",
                "decision": approval_path.get("decision"),
                "require_user_approval": approval_path.get("require_user_approval", False),
            },
            {
                "stage": "permission",
                "decision": (permission_review or {}).get("decision"),
                "risk_level": (permission_review or {}).get("risk_level"),
            },
            {
                "stage": "adversary-review",
                "decision": (adversary_review or {}).get("decision"),
                "report_id": (((adversary_review or {}).get("report") or {}).get("report_id")),
            },
        ]

    def _execution_path(
        self,
        *,
        requested_tools: list[str],
        requested_extensions: list[str],
        effective_requested_tools: list[str],
        extension_resolution: dict[str, Any],
        permission_review: dict[str, Any] | None,
        adversary_review: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        return [
            {
                "stage": "requested-input",
                "tool_count": len(requested_tools),
                "extension_count": len(requested_extensions),
            },
            {
                "stage": "extension-governance",
                "decision": extension_resolution.get("decision"),
                "selected_bundle_ids": extension_resolution.get("selected_bundle_ids", []),
                "selected_policy_set_ids": extension_resolution.get("selected_policy_set_ids", []),
                "selected_bundle_families": extension_resolution.get("selected_bundle_families", []),
                "selected_policy_history_ids": extension_resolution.get("selected_policy_history_ids", []),
                "selected_policy_statuses": extension_resolution.get("selected_policy_statuses", []),
                "selected_bundle_certification_ids": extension_resolution.get("selected_bundle_certification_ids", []),
                "selected_bundle_certification_statuses": extension_resolution.get("selected_bundle_certification_statuses", []),
                "fallback_reason": extension_resolution.get("fallback_reason"),
            },
            {
                "stage": "tool-resolution",
                "requested_tools": requested_tools,
                "effective_requested_tools": effective_requested_tools,
            },
            {
                "stage": "permission-review",
                "decision": (permission_review or {}).get("decision"),
                "risk_level": (permission_review or {}).get("risk_level"),
            },
            {
                "stage": "adversary-review",
                "decision": (adversary_review or {}).get("decision"),
                "report_id": (((adversary_review or {}).get("report") or {}).get("report_id")),
            },
        ]

    def _write_resolution_artifact(self, resolution: dict[str, Any]) -> Path:
        if self.artifacts_dir is None:
            raise RuntimeError("gateway artifacts_dir is required for persisted Goose coverage")
        output_path = self.artifacts_dir / "gateway" / "resolutions" / f"{resolution['resolution_id']}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(resolution, indent=2), encoding="utf-8")
        return output_path

    def _record_gateway_execution(self, *, resolution: dict[str, Any]) -> dict[str, Any] | None:
        if self.execution_store is None or self.artifacts_dir is None:
            return None
        extension_policy_set_ids = sorted(
            {
                item.get("policy_set_id")
                for item in resolution.get("extension_provenance", [])
                if item.get("policy_set_id")
            }
        )
        extension_bundle_families = sorted(
            {
                item.get("bundle_family")
                for item in resolution.get("extension_provenance", [])
                if item.get("bundle_family")
            }
        )
        status = {
            "deny": "blocked",
            "allow-if-approved": "approval-pending",
            "ask": "approval-pending",
        }.get((resolution.get("policy") or {}).get("decision"), "success")
        record = self.execution_store.record(
            recipe_id=f"gateway::{resolution.get('agent_id')}",
            execution_kind="gateway",
            ao_association=[resolution.get("agent_id")] if resolution.get("agent_id") else [],
            trigger_source=str(resolution.get("trigger_source") or "gateway:direct"),
            parameter_set={
                "agent_id": resolution.get("agent_id"),
                "workspace_id": resolution.get("workspace_id"),
                "requested_tools": resolution.get("requested_tools", []),
                "requested_extensions": resolution.get("requested_extensions", []),
                "effective_requested_tools": resolution.get("effective_requested_tools", []),
            },
            linked_trace_ids=resolution.get("linked_trace_ids", []),
            linked_subagent_ids=[],
            policy_path=resolution.get("policy_path", []),
            approval_path=resolution.get("approval_path", {}),
            gateway_decision_path=resolution.get("gateway_decision_path", []),
            gateway_resolution_id=resolution.get("resolution_id"),
            execution_path=resolution.get("execution_path", []),
            approval_fallback_chain=resolution.get("approval_fallback_chain", []),
            adversary_review_report_ids=resolution.get("adversary_review_report_ids", []),
            linked_report_ids=resolution.get("linked_report_ids", []),
            extension_bundle_ids=resolution.get("extension_bundle_ids", []),
            extension_policy_set_ids=extension_policy_set_ids,
            extension_bundle_families=extension_bundle_families,
            extension_provenance=resolution.get("extension_provenance", []),
            artifacts_produced=[resolution.get("artifact_path")] if resolution.get("artifact_path") else [],
            status=status,
            metadata={
                "agent_id": resolution.get("agent_id"),
                "workspace_id": resolution.get("workspace_id"),
                "trigger_source": resolution.get("trigger_source"),
                "fallback_reason": resolution.get("fallback_reason"),
                "extension_policy_decision": (resolution.get("extension_policy") or {}).get("decision"),
                "extension_policy_set_ids": extension_policy_set_ids,
                "extension_bundle_families": extension_bundle_families,
                "extension_policy_history_ids": resolution.get("policy", {}).get("extension_policy_history_ids", []),
                "extension_policy_statuses": resolution.get("policy", {}).get("extension_policy_statuses", []),
                "extension_certification_ids": resolution.get("policy", {}).get("extension_certification_ids", []),
                "extension_certification_statuses": resolution.get("policy", {}).get("extension_certification_statuses", []),
                "permission_decision": ((resolution.get("permission_review") or {}).get("decision")),
            },
        )
        report = build_recipe_execution_report(artifacts_dir=self.artifacts_dir, record=record)
        record["report"] = report
        record["linked_report_ids"] = sorted(
            set(
                [
                    *record.get("linked_report_ids", []),
                    report["report_id"],
                    *record.get("adversary_review_report_ids", []),
                ]
            )
        )
        record["artifacts_produced"] = sorted(set([*record.get("artifacts_produced", []), report["payload_path"], report["markdown_path"]]))
        Path(record["artifact_path"]).write_text(json.dumps(record, indent=2), encoding="utf-8")
        return record

    def _history_items(
        self,
        *,
        agent_id: str | None,
        workspace_id: str | None,
        trigger_source: str | None,
        status: str | None,
        limit: int,
    ) -> list[dict[str, Any]]:
        if self.execution_store is None:
            return []
        items: list[dict[str, Any]] = []
        for item in self.execution_store.list_executions(execution_kind="gateway", limit=max(limit * 4, limit)):
            metadata = item.get("metadata", {}) or {}
            parameter_set = item.get("parameter_set", {}) or {}
            if agent_id and metadata.get("agent_id") != agent_id:
                continue
            if workspace_id and metadata.get("workspace_id") != workspace_id:
                continue
            if trigger_source and item.get("trigger_source") != trigger_source:
                continue
            if status and item.get("status") != status:
                continue
            items.append(
                {
                    **item,
                    "requested_extensions": parameter_set.get("requested_extensions", []),
                }
            )
            if len(items) >= limit:
                break
        return items

    def _flow_families(
        self,
        *,
        trigger_source: str,
        requested_tools: list[str],
        requested_extensions: list[str],
        effective_requested_tools: list[str],
        extension_resolution: dict[str, Any],
        approval_path: dict[str, Any],
        adversary_review: dict[str, Any] | None,
    ) -> list[str]:
        families = {"gateway-controlled", "gateway-only"}
        bundle_families = set(extension_resolution.get("selected_bundle_families", []) or [])
        if requested_extensions and not requested_tools:
            families.add("extension-only")
        if (
            "provider.acp" in set([*requested_tools, *effective_requested_tools])
            or "acp-provider-lane" in bundle_families
            or any(str(extension_id).startswith("acp-") for extension_id in requested_extensions)
            or "acp" in trigger_source
        ):
            families.add("acp-bridged")
        if approval_path.get("decision") in {"ask", "allow-if-approved"} or adversary_review:
            families.add("approval-heavy")
        if trigger_source.startswith("schedule:") or trigger_source.startswith("scheduled:"):
            families.add("scheduled")
        if trigger_source.startswith("subagent-plan:") or trigger_source.startswith("delegation:") or trigger_source.startswith("parallel:"):
            families.add("subagent-delegation")
        return sorted(families)

    def _flow_family_counts(self, items: list[dict[str, Any]]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in items:
            for family in item.get("flow_families", []):
                counts[family] = counts.get(family, 0) + 1
        return counts

    def _latest_by_flow_family(self, items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
        latest: dict[str, dict[str, Any]] = {}
        for item in items:
            for family in item.get("flow_families", []):
                latest.setdefault(
                    family,
                    {
                        "execution_id": item.get("execution_id"),
                        "resolution_id": item.get("gateway_resolution_id"),
                        "status": item.get("status"),
                        "trigger_source": item.get("trigger_source"),
                        "report_id": ((item.get("report") or {}).get("report_id")),
                    },
                )
        return latest

from __future__ import annotations

from pathlib import Path
from typing import Any

from .policy_history import PolicyHistoryService
from .policy_rollouts import PolicyRolloutService
from .policy_sets import ExtensionPolicySetRegistry


class ExtensionBundlePolicyService:
    HIGH_RISK_TOOLS = {
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

    def __init__(self, *, policy_sets: list[dict[str, Any]] | None = None, artifacts_dir: str | Path | None = None):
        self.policy_sets = ExtensionPolicySetRegistry(policy_sets=policy_sets)
        self.EXTENSION_TOOL_MAP = self.policy_sets.allowed_tool_map()
        self.EXTENSION_PERMISSION_MAP = self.policy_sets.permission_map()
        self.policy_history = PolicyHistoryService(artifacts_dir=artifacts_dir or ".")
        self.policy_rollouts = PolicyRolloutService()

    def policy_set_summary(self) -> dict[str, Any]:
        base = self.policy_sets.summary()
        lifecycle_records = self._lifecycle_records()
        lifecycle_map = {
            (str(item.get("policy_set_id")), str(item.get("version"))): item
            for item in lifecycle_records
        }
        rollouts = self.policy_rollouts.summary(records=lifecycle_records)
        items = []
        for item in base.get("items", []):
            lifecycle = lifecycle_map.get((str(item.get("policy_set_id")), str(item.get("version"))), {})
            items.append(
                {
                    **item,
                    "lineage_anchor_id": lifecycle.get("lineage_anchor_id"),
                    "stable_policy_version_id": lifecycle.get("stable_policy_version_id"),
                    "artifact_id": lifecycle.get("artifact_id"),
                    "artifact_path": lifecycle.get("artifact_path"),
                    "status": lifecycle.get("status", item.get("status")),
                    "created_from": lifecycle.get("created_from", item.get("created_from")),
                    "supersedes": lifecycle.get("supersedes", item.get("supersedes", [])),
                    "author": lifecycle.get("author", item.get("author")),
                    "origin": lifecycle.get("origin", item.get("origin")),
                    "effective_scope": lifecycle.get("effective_scope", item.get("effective_scope", {})),
                    "created_at": lifecycle.get("created_at", item.get("created_at")),
                    "activated_at": lifecycle.get("activated_at", item.get("activated_at")),
                    "retired_at": lifecycle.get("retired_at", item.get("retired_at")),
                    "rollback_reference": lifecycle.get("rollback_reference", item.get("rollback_reference")),
                    "linked_evidence_ids": lifecycle.get("linked_evidence_ids", item.get("linked_evidence_ids", [])),
                    "linked_report_ids": lifecycle.get("linked_report_ids", item.get("linked_report_ids", [])),
                    "status_history": lifecycle.get("status_history", item.get("status_history", [])),
                    "report": lifecycle.get("report"),
                }
            )
        latest = lifecycle_records[0] if lifecycle_records else {}
        return {
            **base,
            "items": items,
            "history_count": len(lifecycle_records),
            "status_counts": rollouts.get("status_counts", {}),
            "latest_artifact_id": latest.get("artifact_id"),
            "latest_report_id": ((latest.get("report") or {}).get("report_id")),
            "latest_policy_status": latest.get("status"),
            "rollouts": rollouts,
        }

    def policy_set_detail(self, *, policy_set_id: str, version: str | None = None) -> dict[str, Any] | None:
        detail = self.policy_sets.detail(policy_set_id=policy_set_id, version=version)
        if detail is None:
            return None
        lifecycle = self.policy_history.detail(policy_set_id=policy_set_id, version=version)
        lifecycle_item = (lifecycle or {}).get("item") or {}
        rollout_detail = self.policy_rollouts.detail(
            bundle_family=str(lifecycle_item.get("bundle_family") or (detail.get("policy_set") or {}).get("bundle_family") or ""),
            records=self._lifecycle_records(),
        )
        policy_set = {
            **(detail.get("policy_set") or {}),
            "lineage_anchor_id": lifecycle_item.get("lineage_anchor_id"),
            "stable_policy_version_id": lifecycle_item.get("stable_policy_version_id"),
            "artifact_id": lifecycle_item.get("artifact_id"),
            "artifact_path": lifecycle_item.get("artifact_path"),
            "status": lifecycle_item.get("status", (detail.get("policy_set") or {}).get("status")),
            "created_from": lifecycle_item.get("created_from", (detail.get("policy_set") or {}).get("created_from")),
            "supersedes": lifecycle_item.get("supersedes", (detail.get("policy_set") or {}).get("supersedes", [])),
            "author": lifecycle_item.get("author", (detail.get("policy_set") or {}).get("author")),
            "origin": lifecycle_item.get("origin", (detail.get("policy_set") or {}).get("origin")),
            "effective_scope": lifecycle_item.get("effective_scope", (detail.get("policy_set") or {}).get("effective_scope", {})),
            "created_at": lifecycle_item.get("created_at", (detail.get("policy_set") or {}).get("created_at")),
            "activated_at": lifecycle_item.get("activated_at", (detail.get("policy_set") or {}).get("activated_at")),
            "retired_at": lifecycle_item.get("retired_at", (detail.get("policy_set") or {}).get("retired_at")),
            "rollback_reference": lifecycle_item.get("rollback_reference", (detail.get("policy_set") or {}).get("rollback_reference")),
            "linked_evidence_ids": lifecycle_item.get("linked_evidence_ids", (detail.get("policy_set") or {}).get("linked_evidence_ids", [])),
            "linked_report_ids": lifecycle_item.get("linked_report_ids", (detail.get("policy_set") or {}).get("linked_report_ids", [])),
            "status_history": lifecycle_item.get("status_history", (detail.get("policy_set") or {}).get("status_history", [])),
            "report": lifecycle_item.get("report"),
        }
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "policy_set": policy_set,
            "lifecycle": lifecycle,
            "rollout": rollout_detail,
            "rollouts": self.policy_rollout_summary(),
        }

    def policy_rollout_summary(self) -> dict[str, Any]:
        return self.policy_rollouts.summary(records=self._lifecycle_records())

    def evaluate(
        self,
        *,
        bundle: dict[str, Any],
        workspace_id: str,
        permission_summary: dict[str, Any] | None = None,
        sandbox_summary: dict[str, Any] | None = None,
        acp_compatibility: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        bundle_id = str(bundle.get("extension_id") or bundle.get("bundle_id") or "unknown-bundle")
        policy_set = self.policy_sets.resolve(bundle=bundle)
        policy_lifecycle = self._lifecycle_record_for(policy_set=policy_set)
        policy_lineage = self.policy_history.detail(
            policy_set_id=str(policy_set.get("policy_set_id") or ""),
            version=str(policy_set.get("version") or ""),
        ) or {}
        allowed_tools = list(policy_set.get("allowed_tools", []))
        inherited_permissions = list(policy_set.get("inherited_permissions", []))
        extension_kind = str(bundle.get("extension_kind") or "unknown")
        policy_set_id = str(policy_set.get("policy_set_id") or "unknown-policy-set")
        policy_set_version = str(policy_set.get("version") or "unknown")
        bundle_family = str(policy_set.get("bundle_family") or f"{extension_kind}-family")
        high_risk_tools = [tool for tool in allowed_tools if tool in self.HIGH_RISK_TOOLS]
        active_permission_mode = ((permission_summary or {}).get("active_mode") or {}).get("mode_id")
        active_sandbox_profile = ((sandbox_summary or {}).get("active_profile") or {}).get("profile_id")
        acp_items = (acp_compatibility or {}).get("items", [])
        compatible_provider_ids = [item.get("provider_id") for item in acp_items if item.get("compatible")]
        missing_features = sorted(
            {
                feature
                for item in acp_items
                for feature in item.get("missing_features", [])
                if feature
            }
        )

        workspace_visible = workspace_id in bundle.get("workspace_scopes", []) or "*" in bundle.get("workspace_scopes", [])
        enabled = bool(bundle.get("enabled", False))
        approval_decision = str(policy_set.get("approval_mode") or "allow")
        approval_reason = "policy-set-default"
        if not workspace_visible:
            approval_decision = "deny"
            approval_reason = "workspace-outside-bundle-scope"
        elif not enabled:
            approval_decision = "deny"
            approval_reason = "bundle-disabled"
        elif high_risk_tools and approval_decision == "allow":
            approval_decision = "allow-if-approved"
            approval_reason = "policy-set-escalated-for-high-risk"

        risk_flags: list[str] = list(policy_set.get("risk_flags", []) or [])
        if extension_kind == "acp-provider" and not compatible_provider_ids:
            risk_flags.append("extension-acp-privilege-inheritance-confusion-risk")
        if high_risk_tools and approval_decision == "allow-if-approved":
            risk_flags.append("bundle-level-permission-escalation-attempt-risk")

        return {
            "bundle_id": bundle_id,
            "policy_set_id": policy_set_id,
            "policy_set_version": policy_set_version,
            "policy_set_label": policy_set.get("label"),
            "bundle_family": bundle_family,
            "workspace_visible": workspace_visible,
            "allowed_tools": allowed_tools,
            "inherited_permissions": inherited_permissions,
            "high_risk_tools": high_risk_tools,
            "permission_mode": active_permission_mode,
            "sandbox_posture": active_sandbox_profile,
            "approval_path": {
                "decision": approval_decision,
                "reason": approval_reason,
                "policy_set_id": policy_set_id,
                "policy_set_version": policy_set_version,
            },
            "acp_compatibility": {
                "compatible_provider_ids": compatible_provider_ids,
                "provider_count": len(acp_items),
                "feature_missing": missing_features,
                "items": acp_items,
                "recommended_provider_kinds": list(policy_set.get("recommended_provider_kinds", []) or []),
            },
            "risk_flags": sorted(set(risk_flags)),
            "policy_lifecycle": {
                **policy_lifecycle,
                "lineage": policy_lineage.get("lineage", []),
                "lineage_depth": policy_lineage.get("lineage_depth", 0),
                "latest_status_transition": policy_lineage.get("latest_status_transition"),
            },
        }

    def _lifecycle_records(self) -> list[dict[str, Any]]:
        return sorted(
            [self.policy_history.record(policy_set=item) for item in self.policy_sets.items(public=False)],
            key=lambda item: (
                str(item.get("activated_at") or item.get("created_at") or ""),
                str(item.get("created_at") or ""),
                str(item.get("version") or ""),
            ),
            reverse=True,
        )

    def _lifecycle_record_for(self, *, policy_set: dict[str, Any]) -> dict[str, Any]:
        return self.policy_history.record(policy_set=policy_set)

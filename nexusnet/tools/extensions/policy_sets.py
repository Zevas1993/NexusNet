from __future__ import annotations

from copy import deepcopy
from typing import Any


class ExtensionPolicySetRegistry:
    DEFAULT_POLICY_SETS = [
        {
            "policy_set_id": "goose-mcp-readonly",
            "version": "2026.02",
            "label": "Goose MCP Readonly Filesystem",
            "bundle_family": "filesystem-bridge",
            "bundle_ids": ["mcp-filesystem"],
            "allowed_tools": ["filesystem.readonly"],
            "inherited_permissions": ["workspace-root-read", "mcp-bridge"],
            "approval_mode": "allow",
            "sandbox_posture": "workspace-write",
            "recommended_provider_kinds": [],
            "risk_flags": [],
            "author": "nexusnet-governance",
            "origin": "goose-policy-lifecycle-fixture",
            "effective_scope": {
                "workspace_scopes": ["default", "*"],
                "bundle_ids": ["mcp-filesystem"],
                "roots": ["{project_root}"],
                "operator_surfaces": ["wrapper", "ops", "visualizer"],
            },
            "status": "superseded",
            "created_from": "goose-mcp-readonly@2026.01",
            "supersedes": ["goose-mcp-readonly@2026.01"],
            "created_at": "2026-03-22T12:00:00+00:00",
            "activated_at": "2026-03-27T12:00:00+00:00",
            "retired_at": "2026-04-01T12:00:00+00:00",
            "rollback_reference": "goose-mcp-readonly@2026.01",
            "linked_evidence_ids": [
                "goose-policy-lifecycle-fixture",
            ],
            "linked_report_ids": [],
            "status_history": [
                {
                    "status": "draft",
                    "changed_at": "2026-03-22T12:00:00+00:00",
                    "reason": "filesystem-bridge-lineage-draft",
                },
                {
                    "status": "approved",
                    "changed_at": "2026-03-25T12:00:00+00:00",
                    "reason": "readonly-filesystem-governance-approved",
                },
                {
                    "status": "active",
                    "changed_at": "2026-03-27T12:00:00+00:00",
                    "reason": "readonly-filesystem-rollout-activated",
                },
                {
                    "status": "superseded",
                    "changed_at": "2026-04-01T12:00:00+00:00",
                    "reason": "newer-filesystem-rollout-superseded-2026_02",
                },
            ],
            "notes": [
                "Historical filesystem-bridge lineage fixture retained for compare and export workflows.",
            ],
        },
        {
            "policy_set_id": "goose-local-retrieval-pack",
            "version": "2026.02",
            "label": "Goose Local Retrieval Pack",
            "bundle_family": "retrieval-pack",
            "bundle_ids": ["local-retrieval-pack"],
            "allowed_tools": ["retrieval.query", "governance.audit"],
            "inherited_permissions": ["retrieval-query", "governance-audit"],
            "approval_mode": "allow",
            "sandbox_posture": "read-only",
            "recommended_provider_kinds": ["review-agent"],
            "risk_flags": [],
            "author": "nexusnet-governance",
            "origin": "goose-policy-lifecycle-fixture",
            "effective_scope": {
                "workspace_scopes": ["default", "*"],
                "bundle_ids": ["local-retrieval-pack"],
                "roots": ["{project_root}"],
                "operator_surfaces": ["wrapper", "ops", "visualizer"],
            },
            "status": "rolled_back",
            "created_from": "goose-local-retrieval-pack@2026.01",
            "supersedes": ["goose-local-retrieval-pack@2026.01"],
            "created_at": "2026-03-18T12:00:00+00:00",
            "activated_at": "2026-03-21T12:00:00+00:00",
            "retired_at": "2026-03-23T12:00:00+00:00",
            "rollback_reference": "goose-local-retrieval-pack@2026.01",
            "linked_evidence_ids": [
                "goose-policy-lifecycle-fixture",
                "goose-certification-depth-fixture",
            ],
            "linked_report_ids": [],
            "status_history": [
                {
                    "status": "draft",
                    "changed_at": "2026-03-18T12:00:00+00:00",
                    "reason": "retrieval-pack-governance-draft",
                },
                {
                    "status": "shadow",
                    "changed_at": "2026-03-19T12:00:00+00:00",
                    "reason": "retrieval-pack-shadow-rollout",
                },
                {
                    "status": "approved",
                    "changed_at": "2026-03-20T12:00:00+00:00",
                    "reason": "retrieval-pack-bounded-approval",
                },
                {
                    "status": "active",
                    "changed_at": "2026-03-21T12:00:00+00:00",
                    "reason": "retrieval-pack-rollout-activated",
                },
                {
                    "status": "rolled_back",
                    "changed_at": "2026-03-23T12:00:00+00:00",
                    "reason": "retrieval-pack-operator-rollback-to-2026_01",
                },
            ],
            "notes": [
                "Historical retrieval-pack rollback fixture retained to deepen certification lineage across stored artifacts.",
            ],
        },
        {
            "policy_set_id": "goose-local-retrieval-pack",
            "version": "2026.03",
            "label": "Goose Local Retrieval Pack",
            "bundle_family": "retrieval-pack",
            "bundle_ids": ["local-retrieval-pack"],
            "allowed_tools": ["retrieval.query", "governance.audit"],
            "inherited_permissions": ["retrieval-query", "governance-audit"],
            "approval_mode": "allow",
            "sandbox_posture": "read-only",
            "recommended_provider_kinds": ["review-agent"],
            "risk_flags": [],
            "author": "nexusnet-governance",
            "origin": "goose-policy-lifecycle-fixture",
            "effective_scope": {
                "workspace_scopes": ["default", "*"],
                "bundle_ids": ["local-retrieval-pack"],
                "roots": ["{project_root}"],
                "operator_surfaces": ["wrapper", "ops", "visualizer"],
            },
            "status": "superseded",
            "created_from": "goose-local-retrieval-pack@2026.02",
            "supersedes": ["goose-local-retrieval-pack@2026.02"],
            "created_at": "2026-03-24T12:00:00+00:00",
            "activated_at": "2026-03-30T12:00:00+00:00",
            "retired_at": "2026-04-03T12:00:00+00:00",
            "rollback_reference": "goose-local-retrieval-pack@2026.02",
            "linked_evidence_ids": [
                "goose-policy-lifecycle-fixture",
            ],
            "linked_report_ids": [],
            "status_history": [
                {
                    "status": "draft",
                    "changed_at": "2026-03-24T12:00:00+00:00",
                    "reason": "retrieval-pack-lineage-draft",
                },
                {
                    "status": "approved",
                    "changed_at": "2026-03-27T12:00:00+00:00",
                    "reason": "retrieval-pack-lineage-approved",
                },
                {
                    "status": "active",
                    "changed_at": "2026-03-30T12:00:00+00:00",
                    "reason": "retrieval-pack-lineage-active",
                },
                {
                    "status": "superseded",
                    "changed_at": "2026-04-03T12:00:00+00:00",
                    "reason": "retrieval-pack-superseded-by-2026_04",
                },
            ],
            "notes": [
                "Historical retrieval-pack lineage fixture retained for compare and supersession coverage.",
            ],
        },
        {
            "policy_set_id": "goose-acp-coding-provider",
            "version": "2026.02",
            "label": "Goose ACP Coding Provider",
            "bundle_family": "acp-provider-lane",
            "bundle_ids": ["acp-coding-lane"],
            "allowed_tools": ["provider.acp", "filesystem.write", "shell.exec"],
            "inherited_permissions": ["acp-bridge", "workspace-write-requested", "shell-exec-requested"],
            "approval_mode": "allow-if-approved",
            "sandbox_posture": "workspace-write",
            "recommended_provider_kinds": ["coding-agent"],
            "risk_flags": [
                "extension-acp-privilege-inheritance-confusion-risk",
                "bundle-level-permission-escalation-attempt-risk",
            ],
            "author": "nexusnet-governance",
            "origin": "goose-policy-lifecycle-fixture",
            "effective_scope": {
                "workspace_scopes": ["default"],
                "bundle_ids": ["acp-coding-lane"],
                "roots": ["{project_root}"],
                "operator_surfaces": ["wrapper", "ops", "visualizer"],
                "provider_gate": "optional-acp-provider",
            },
            "status": "superseded",
            "created_from": "goose-acp-coding-provider@2026.01",
            "supersedes": ["goose-acp-coding-provider@2026.01"],
            "created_at": "2026-03-21T12:00:00+00:00",
            "activated_at": "2026-03-26T12:00:00+00:00",
            "retired_at": "2026-03-28T11:59:59+00:00",
            "rollback_reference": "goose-acp-coding-provider@2026.01",
            "linked_evidence_ids": [
                "goose-acp-diagnostics-baseline",
                "goose-policy-lifecycle-fixture",
                "goose-certification-depth-fixture",
            ],
            "linked_report_ids": [],
            "status_history": [
                {
                    "status": "draft",
                    "changed_at": "2026-03-21T12:00:00+00:00",
                    "reason": "acp-provider-governance-draft",
                },
                {
                    "status": "approved",
                    "changed_at": "2026-03-24T12:00:00+00:00",
                    "reason": "provider-gated-approval-complete",
                },
                {
                    "status": "active",
                    "changed_at": "2026-03-26T12:00:00+00:00",
                    "reason": "bounded-acp-lane-activated-under-fixture",
                },
                {
                    "status": "superseded",
                    "changed_at": "2026-03-28T11:59:59+00:00",
                    "reason": "provider-gated-lane-superseded-before-shadow-refresh",
                },
            ],
            "notes": [
                "Historical ACP supersession fixture retained so certification lineage spans revoked, held, and shadow-approved artifacts.",
            ],
        },
        {
            "policy_set_id": "goose-acp-coding-provider",
            "version": "2026.03",
            "label": "Goose ACP Coding Provider",
            "bundle_family": "acp-provider-lane",
            "bundle_ids": ["acp-coding-lane"],
            "allowed_tools": ["provider.acp", "filesystem.write", "shell.exec"],
            "inherited_permissions": ["acp-bridge", "workspace-write-requested", "shell-exec-requested"],
            "approval_mode": "allow-if-approved",
            "sandbox_posture": "workspace-write",
            "recommended_provider_kinds": ["coding-agent"],
            "risk_flags": [
                "extension-acp-privilege-inheritance-confusion-risk",
                "bundle-level-permission-escalation-attempt-risk",
            ],
            "author": "nexusnet-governance",
            "origin": "goose-policy-lifecycle-fixture",
            "effective_scope": {
                "workspace_scopes": ["default"],
                "bundle_ids": ["acp-coding-lane"],
                "roots": ["{project_root}"],
                "operator_surfaces": ["wrapper", "ops", "visualizer"],
                "provider_gate": "optional-acp-provider",
            },
            "status": "held",
            "created_from": "goose-acp-coding-provider@2026.02",
            "supersedes": ["goose-acp-coding-provider@2026.02"],
            "created_at": "2026-03-28T12:00:00+00:00",
            "activated_at": None,
            "retired_at": "2026-04-04T11:59:59+00:00",
            "rollback_reference": "goose-acp-coding-provider@2026.02",
            "linked_evidence_ids": [
                "goose-acp-diagnostics-baseline",
                "goose-policy-lifecycle-fixture",
            ],
            "linked_report_ids": [],
            "status_history": [
                {
                    "status": "draft",
                    "changed_at": "2026-03-28T12:00:00+00:00",
                    "reason": "acp-provider-governance-draft",
                },
                {
                    "status": "approved",
                    "changed_at": "2026-04-01T12:00:00+00:00",
                    "reason": "provider-gated-approval-complete",
                },
                {
                    "status": "held",
                    "changed_at": "2026-04-04T11:59:59+00:00",
                    "reason": "privilege-inheritance-confusion-held-pre-promotion",
                },
            ],
            "notes": [
                "Historical held ACP provider fixture retained to prove shadow-approved to held lineage.",
            ],
        },
        {
            "policy_set_id": "goose-mcp-readonly",
            "version": "2026.03",
            "label": "Goose MCP Readonly Filesystem",
            "bundle_family": "filesystem-bridge",
            "bundle_ids": ["mcp-filesystem"],
            "allowed_tools": ["filesystem.readonly"],
            "inherited_permissions": ["workspace-root-read", "mcp-bridge"],
            "approval_mode": "allow",
            "sandbox_posture": "workspace-write",
            "recommended_provider_kinds": [],
            "risk_flags": [],
            "author": "nexusnet-governance",
            "origin": "goose-policy-lifecycle-fixture",
            "effective_scope": {
                "workspace_scopes": ["default", "*"],
                "bundle_ids": ["mcp-filesystem"],
                "roots": ["{project_root}"],
                "operator_surfaces": ["wrapper", "ops", "visualizer"],
            },
            "status": "rolled_back",
            "created_from": "goose-mcp-readonly@2026.02",
            "supersedes": ["goose-mcp-readonly@2026.02"],
            "created_at": "2026-04-01T12:00:00+00:00",
            "activated_at": "2026-04-02T12:00:00+00:00",
            "retired_at": "2026-04-04T12:00:00+00:00",
            "rollback_reference": "goose-mcp-readonly@2026.02",
            "linked_evidence_ids": [
                "goose-gateway-coverage-baseline",
                "goose-policy-lifecycle-fixture",
            ],
            "linked_report_ids": [],
            "status_history": [
                {
                    "status": "draft",
                    "changed_at": "2026-04-01T12:00:00+00:00",
                    "reason": "readonly-filesystem-governance-draft",
                },
                {
                    "status": "shadow",
                    "changed_at": "2026-04-01T18:00:00+00:00",
                    "reason": "filesystem-bridge-shadow-rollout",
                },
                {
                    "status": "approved",
                    "changed_at": "2026-04-02T06:00:00+00:00",
                    "reason": "bounded-local-first-filesystem-approved",
                },
                {
                    "status": "active",
                    "changed_at": "2026-04-02T12:00:00+00:00",
                    "reason": "gateway-coverage-pre-rollout-activated",
                },
                {
                    "status": "rolled_back",
                    "changed_at": "2026-04-04T12:00:00+00:00",
                    "reason": "operator-rollback-to-stable-readonly-lineage",
                },
            ],
            "notes": [
                "Filesystem bridge rollback fixture used for explicit lifecycle validation.",
            ],
        },
        {
            "policy_set_id": "goose-local-retrieval-pack",
            "version": "2026.04",
            "label": "Goose Local Retrieval Pack",
            "bundle_family": "retrieval-pack",
            "bundle_ids": ["local-retrieval-pack"],
            "allowed_tools": ["retrieval.query", "governance.audit"],
            "inherited_permissions": ["retrieval-query", "governance-audit"],
            "approval_mode": "allow",
            "sandbox_posture": "read-only",
            "recommended_provider_kinds": ["review-agent"],
            "risk_flags": [],
            "author": "nexusnet-governance",
            "origin": "goose-policy-versioning-baseline",
            "effective_scope": {
                "workspace_scopes": ["default", "*"],
                "bundle_ids": ["local-retrieval-pack"],
                "roots": ["{project_root}"],
                "operator_surfaces": ["wrapper", "ops", "visualizer"],
            },
            "status": "active",
            "created_from": "goose-local-retrieval-pack@2026.03",
            "supersedes": ["goose-local-retrieval-pack@2026.03"],
            "created_at": "2026-04-03T12:00:00+00:00",
            "activated_at": "2026-04-08T12:00:00+00:00",
            "retired_at": None,
            "rollback_reference": "goose-local-retrieval-pack@2026.03",
            "linked_evidence_ids": [
                "goose-gateway-coverage-baseline",
                "goose-policy-versioning-baseline",
            ],
            "linked_report_ids": [],
            "status_history": [
                {
                    "status": "draft",
                    "changed_at": "2026-04-03T12:00:00+00:00",
                    "reason": "retrieval-pack-governance-draft",
                },
                {
                    "status": "shadow",
                    "changed_at": "2026-04-04T12:00:00+00:00",
                    "reason": "retrieval-pack-shadow-rollout",
                },
                {
                    "status": "approved",
                    "changed_at": "2026-04-06T12:00:00+00:00",
                    "reason": "retrieval-pack-bounded-approval",
                },
                {
                    "status": "active",
                    "changed_at": "2026-04-08T12:00:00+00:00",
                    "reason": "retrieval-pack-rollout-activated",
                },
            ],
            "notes": [
                "Local retrieval and governance audit bundle for bounded operator workflows.",
            ],
        },
        {
            "policy_set_id": "goose-acp-coding-provider",
            "version": "2026.04",
            "label": "Goose ACP Coding Provider",
            "bundle_family": "acp-provider-lane",
            "bundle_ids": ["acp-coding-lane"],
            "allowed_tools": ["provider.acp", "filesystem.write", "shell.exec"],
            "inherited_permissions": ["acp-bridge", "workspace-write-requested", "shell-exec-requested"],
            "approval_mode": "allow-if-approved",
            "sandbox_posture": "workspace-write",
            "recommended_provider_kinds": ["coding-agent"],
            "risk_flags": [
                "extension-acp-privilege-inheritance-confusion-risk",
                "bundle-level-permission-escalation-attempt-risk",
            ],
            "author": "nexusnet-governance",
            "origin": "goose-policy-versioning-baseline",
            "effective_scope": {
                "workspace_scopes": ["default"],
                "bundle_ids": ["acp-coding-lane"],
                "roots": ["{project_root}"],
                "operator_surfaces": ["wrapper", "ops", "visualizer"],
                "provider_gate": "optional-acp-provider",
            },
            "status": "shadow",
            "created_from": "goose-acp-coding-provider@2026.03",
            "supersedes": ["goose-acp-coding-provider@2026.03"],
            "created_at": "2026-04-04T12:00:00+00:00",
            "activated_at": None,
            "retired_at": None,
            "rollback_reference": "goose-acp-coding-provider@2026.03",
            "linked_evidence_ids": [
                "goose-acp-diagnostics-baseline",
                "goose-policy-versioning-baseline",
            ],
            "linked_report_ids": [],
            "status_history": [
                {
                    "status": "draft",
                    "changed_at": "2026-04-04T12:00:00+00:00",
                    "reason": "acp-provider-governance-draft",
                },
                {
                    "status": "shadow",
                    "changed_at": "2026-04-10T12:00:00+00:00",
                    "reason": "optional-acp-provider-shadow-rollout",
                },
            ],
            "notes": [
                "ACP provider lanes remain optional and require explicit governance approval.",
                "High-risk ACP bundle requests must fail closed or escalate.",
            ],
        },
        {
            "policy_set_id": "goose-mcp-readonly",
            "version": "2026.04",
            "label": "Goose MCP Readonly Filesystem",
            "bundle_family": "filesystem-bridge",
            "bundle_ids": ["mcp-filesystem"],
            "allowed_tools": ["filesystem.readonly"],
            "inherited_permissions": ["workspace-root-read", "mcp-bridge"],
            "approval_mode": "allow",
            "sandbox_posture": "workspace-write",
            "recommended_provider_kinds": [],
            "risk_flags": [],
            "author": "nexusnet-governance",
            "origin": "goose-policy-versioning-baseline",
            "effective_scope": {
                "workspace_scopes": ["default", "*"],
                "bundle_ids": ["mcp-filesystem"],
                "roots": ["{project_root}"],
                "operator_surfaces": ["wrapper", "ops", "visualizer"],
            },
            "status": "active",
            "created_from": "goose-mcp-readonly@2026.03",
            "supersedes": ["goose-mcp-readonly@2026.03"],
            "created_at": "2026-04-02T12:00:00+00:00",
            "activated_at": "2026-04-07T12:00:00+00:00",
            "retired_at": None,
            "rollback_reference": "goose-mcp-readonly@2026.03",
            "linked_evidence_ids": [
                "goose-gateway-coverage-baseline",
                "goose-policy-versioning-baseline",
            ],
            "linked_report_ids": [],
            "status_history": [
                {
                    "status": "draft",
                    "changed_at": "2026-04-02T12:00:00+00:00",
                    "reason": "readonly-filesystem-governance-draft",
                },
                {
                    "status": "approved",
                    "changed_at": "2026-04-05T12:00:00+00:00",
                    "reason": "bounded-local-first-filesystem-approved",
                },
                {
                    "status": "active",
                    "changed_at": "2026-04-07T12:00:00+00:00",
                    "reason": "gateway-coverage-baseline-activated",
                },
            ],
            "notes": [
                "Roots-aware read-only bridge for local-first workspace inspection.",
                "Write and delete tools remain outside the default Goose filesystem bundle lane.",
            ],
        },
    ]

    def __init__(self, *, policy_sets: list[dict[str, Any]] | None = None):
        self._policy_sets = [deepcopy(item) for item in (policy_sets or self.DEFAULT_POLICY_SETS)]
        self._by_bundle_id: dict[str, dict[str, Any]] = {}
        self._by_policy_set_id: dict[str, list[dict[str, Any]]] = {}
        for item in self._policy_sets:
            for bundle_id in item.get("bundle_ids", []) or []:
                self._by_bundle_id[str(bundle_id)] = item
            self._by_policy_set_id.setdefault(str(item.get("policy_set_id") or "unknown"), []).append(item)

    def resolve(self, *, bundle: dict[str, Any]) -> dict[str, Any]:
        bundle_id = str(bundle.get("extension_id") or bundle.get("bundle_id") or "unknown-bundle")
        resolved = self._by_bundle_id.get(bundle_id)
        if resolved is None:
            resolved = self._fallback_policy_set(bundle=bundle)
        return deepcopy(resolved)

    def items(self, *, public: bool = True) -> list[dict[str, Any]]:
        items = [deepcopy(item) for item in self._policy_sets]
        if not public:
            return items
        return [self._public_item(item) for item in items]

    def summary(self) -> dict[str, Any]:
        items = [self._public_item(item) for item in self._policy_sets]
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "policy_set_count": len(items),
            "bundle_family_count": len({item.get("bundle_family") for item in items if item.get("bundle_family")}),
            "policy_set_ids": [item.get("policy_set_id") for item in items if item.get("policy_set_id")],
            "bundle_families": sorted({item.get("bundle_family") for item in items if item.get("bundle_family")}),
            "versions": sorted({item.get("version") for item in items if item.get("version")}),
            "items": items,
        }

    def detail(self, *, policy_set_id: str, version: str | None = None) -> dict[str, Any] | None:
        candidates = self._by_policy_set_id.get(policy_set_id, [])
        if version:
            candidates = [item for item in candidates if str(item.get("version")) == str(version)]
        if not candidates:
            return None
        item = self._public_item(self._sort_candidates(candidates)[0])
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "policy_set": item,
        }

    def allowed_tool_map(self) -> dict[str, list[str]]:
        mapping: dict[str, list[str]] = {}
        for item in self._policy_sets:
            for bundle_id in item.get("bundle_ids", []) or []:
                mapping[str(bundle_id)] = list(item.get("allowed_tools", []) or [])
        return mapping

    def permission_map(self) -> dict[str, list[str]]:
        mapping: dict[str, list[str]] = {}
        for item in self._policy_sets:
            for bundle_id in item.get("bundle_ids", []) or []:
                mapping[str(bundle_id)] = list(item.get("inherited_permissions", []) or [])
        return mapping

    def _sort_candidates(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted(
            items,
            key=lambda item: (
                str(item.get("activated_at") or item.get("created_at") or ""),
                str(item.get("created_at") or ""),
                str(item.get("version") or ""),
            ),
            reverse=True,
        )

    def _public_item(self, item: dict[str, Any]) -> dict[str, Any]:
        return {
            "policy_set_id": item.get("policy_set_id"),
            "version": item.get("version"),
            "label": item.get("label"),
            "bundle_family": item.get("bundle_family"),
            "bundle_ids": list(item.get("bundle_ids", []) or []),
            "allowed_tools": list(item.get("allowed_tools", []) or []),
            "inherited_permissions": list(item.get("inherited_permissions", []) or []),
            "approval_mode": item.get("approval_mode"),
            "sandbox_posture": item.get("sandbox_posture"),
            "recommended_provider_kinds": list(item.get("recommended_provider_kinds", []) or []),
            "risk_flags": list(item.get("risk_flags", []) or []),
            "author": item.get("author"),
            "origin": item.get("origin"),
            "effective_scope": deepcopy(item.get("effective_scope") or {}),
            "status": item.get("status", "draft"),
            "created_from": item.get("created_from"),
            "supersedes": list(item.get("supersedes", []) or []),
            "created_at": item.get("created_at"),
            "activated_at": item.get("activated_at"),
            "retired_at": item.get("retired_at"),
            "rollback_reference": item.get("rollback_reference"),
            "linked_evidence_ids": list(item.get("linked_evidence_ids", []) or []),
            "linked_report_ids": list(item.get("linked_report_ids", []) or []),
            "status_history": list(item.get("status_history", []) or []),
            "notes": list(item.get("notes", []) or []),
        }

    def _fallback_policy_set(self, *, bundle: dict[str, Any]) -> dict[str, Any]:
        bundle_id = str(bundle.get("extension_id") or bundle.get("bundle_id") or "unknown-bundle")
        extension_kind = str(bundle.get("extension_kind") or "unknown")
        approval_mode = "allow-if-approved" if extension_kind == "acp-provider" else "allow"
        return {
            "policy_set_id": f"goose-generic-{extension_kind}",
            "version": "2026.04",
            "label": f"Goose Generic {extension_kind}",
            "bundle_family": f"{extension_kind}-family",
            "bundle_ids": [bundle_id],
            "allowed_tools": [],
            "inherited_permissions": [],
            "approval_mode": approval_mode,
            "sandbox_posture": "workspace-write" if extension_kind == "acp-provider" else "read-only",
            "recommended_provider_kinds": ["coding-agent"] if extension_kind == "acp-provider" else [],
            "risk_flags": ["extension-acp-privilege-inheritance-confusion-risk"] if extension_kind == "acp-provider" else [],
            "author": "nexusnet-governance",
            "origin": "goose-policy-lifecycle-fallback",
            "effective_scope": {
                "workspace_scopes": list(bundle.get("workspace_scopes", []) or []),
                "bundle_ids": [bundle_id],
                "roots": list(bundle.get("roots", []) or []),
            },
            "status": "draft",
            "created_from": None,
            "supersedes": [],
            "created_at": "2026-04-14T12:00:00+00:00",
            "activated_at": None,
            "retired_at": None,
            "rollback_reference": None,
            "linked_evidence_ids": [],
            "linked_report_ids": [],
            "status_history": [
                {
                    "status": "draft",
                    "changed_at": "2026-04-14T12:00:00+00:00",
                    "reason": "fallback-governance-policy-set-created",
                },
            ],
            "notes": ["Fallback governance policy set for previously unseen Goose-derived bundles."],
        }

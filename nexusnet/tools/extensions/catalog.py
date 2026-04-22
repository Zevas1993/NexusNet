from __future__ import annotations

from typing import Any

from .certification import ExtensionBundleCertificationService
from .policies import ExtensionBundlePolicyService
from .policy_reports import build_policy_compare_report
from .provenance import ExtensionBundleProvenanceService
from .reports import build_extension_certification_compare_report


class ExtensionCatalogService:
    def __init__(
        self,
        *,
        runtime_configs: dict[str, Any],
        project_root: str,
        artifacts_dir: str | None = None,
        permission_service: Any | None = None,
        sandbox_service: Any | None = None,
        acp_bridge: Any | None = None,
        adversary_review: Any | None = None,
    ):
        extensions = ((runtime_configs.get("goose_lane") or {}).get("extensions") or {}).get("catalog") or []
        self.project_root = project_root
        self.extensions = [self._normalize(item) for item in extensions]
        self.permission_service = permission_service
        self.sandbox_service = sandbox_service
        self.acp_bridge = acp_bridge
        self.adversary_review = adversary_review
        self.policy = ExtensionBundlePolicyService(artifacts_dir=artifacts_dir or project_root)
        self.provenance = ExtensionBundleProvenanceService(artifacts_dir=artifacts_dir or project_root)
        self.certification = ExtensionBundleCertificationService(artifacts_dir=artifacts_dir or project_root)

    def summary(self, *, workspace_id: str = "default") -> dict[str, Any]:
        visible = [
            item
            for item in self.extensions
            if workspace_id in item.get("workspace_scopes", []) or "*" in item.get("workspace_scopes", [])
        ]
        bundles = sorted(
            [self._bundle_record(item=item, workspace_id=workspace_id) for item in visible],
            key=lambda item: str(item.get("created_at") or ""),
            reverse=True,
        )
        enabled = [item for item in bundles if item.get("enabled_state") == "enabled"]
        approval_required_count = sum(
            1
            for item in bundles
            if ((item.get("approval_path") or {}).get("decision")) in {"allow-if-approved", "ask"}
        )
        high_risk_bundle_count = sum(1 for item in bundles if item.get("high_risk_tools"))
        latest_bundle = bundles[0] if bundles else {}
        latest_certification = latest_bundle.get("certification") or {}
        policy_summary = self.policy.policy_set_summary()
        policy_rollouts = policy_summary.get("rollouts") or {"family_count": 0, "status_counts": {}, "latest_bundle_family": None}
        policy_set_ids = sorted({item.get("policy_set_id") for item in bundles if item.get("policy_set_id")})
        family_counts: dict[str, int] = {}
        certification_status_counts: dict[str, int] = {}
        for item in bundles:
            family = item.get("bundle_family")
            if family:
                family_counts[str(family)] = family_counts.get(str(family), 0) + 1
            certification_status = item.get("certification_status")
            if certification_status:
                certification_status_counts[str(certification_status)] = certification_status_counts.get(str(certification_status), 0) + 1
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "extension_count": len(bundles),
            "enabled_count": len(enabled),
            "mcp_compatible_count": sum(1 for item in bundles if item.get("mcp_compatible")),
            "workspace_id": workspace_id,
            "approval_required_count": approval_required_count,
            "high_risk_bundle_count": high_risk_bundle_count,
            "policy_set_count": len(policy_set_ids),
            "bundle_family_count": len(family_counts),
            "policy_set_ids": policy_set_ids,
            "bundle_family_counts": family_counts,
            "latest_bundle_artifact_id": latest_bundle.get("artifact_id"),
            "latest_bundle_report_id": ((latest_bundle.get("report") or {}).get("report_id")),
            "latest_bundle_id": latest_bundle.get("bundle_id"),
            "latest_policy_set_id": latest_bundle.get("policy_set_id"),
            "latest_policy_set_version": latest_bundle.get("policy_set_version"),
            "latest_bundle_family": latest_bundle.get("bundle_family"),
            "latest_policy_status": ((latest_bundle.get("policy_lifecycle") or {}).get("status")),
            "latest_policy_history_artifact_id": ((latest_bundle.get("policy_lifecycle") or {}).get("artifact_id")),
            "latest_policy_history_report_id": ((((latest_bundle.get("policy_lifecycle") or {}).get("report")) or {}).get("report_id")),
            "latest_bundle_human_summary": ((latest_bundle.get("report") or {}).get("human_summary")),
            "latest_certification_artifact_id": latest_bundle.get("certification_artifact_id"),
            "latest_certification_report_id": latest_bundle.get("certification_report_id"),
            "latest_certification_status": latest_bundle.get("certification_status"),
            "latest_certification_human_summary": ((latest_certification.get("report") or {}).get("human_summary")),
            "bundle_ids": [item.get("bundle_id") for item in bundles if item.get("bundle_id")],
            "risk_flag_counts": self._risk_flag_counts(bundles),
            "certification_status_counts": certification_status_counts,
            "policy_status_counts": policy_summary.get("status_counts", {}),
            "policy_history_count": policy_summary.get("history_count", 0),
            "policy_rollout_family_count": policy_rollouts.get("family_count", 0),
            "policy_rollout_status_counts": policy_rollouts.get("status_counts", {}),
            "compare_refs": {
                "summary": "/ops/brain/extensions",
                "bundle_detail_template": "/ops/brain/extensions/{bundle_id}",
                "policy_sets": "/ops/brain/extensions/policy-sets",
                "policy_set_detail_template": "/ops/brain/extensions/policy-sets/{policy_set_id}",
                "policy_history": "/ops/brain/extensions/policy-history",
                "policy_history_detail_template": "/ops/brain/extensions/policy-history/{policy_set_id}",
                "policy_history_compare": "/ops/brain/extensions/policy-history/compare",
                "policy_rollouts": "/ops/brain/extensions/policy-rollouts",
                "certifications": "/ops/brain/extensions/certifications",
                "certification_detail_template": "/ops/brain/extensions/certifications/{artifact_id}",
                "certification_compare": "/ops/brain/extensions/certifications/compare",
            },
            "extensions": bundles,
        }

    def detail(self, bundle_id: str, *, workspace_id: str = "default") -> dict[str, Any] | None:
        summary = self.summary(workspace_id=workspace_id)
        bundle = next((item for item in summary.get("extensions", []) if item.get("bundle_id") == bundle_id), None)
        if bundle is None:
            return None
        artifact_id = bundle.get("artifact_id")
        detail = self.provenance.detail(artifact_id) if artifact_id else None
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "bundle": bundle,
            "detail": detail,
            "certification_detail": self.certification.detail(str(bundle.get("certification_artifact_id")))
            if bundle.get("certification_artifact_id")
            else None,
            "policy_set_detail": self.policy_set_detail(
                policy_set_id=str(bundle.get("policy_set_id") or ""),
                version=str(bundle.get("policy_set_version") or ""),
                workspace_id=workspace_id,
            )
            if bundle.get("policy_set_id")
            else None,
            "compare_refs": {
                "summary": "/ops/brain/extensions",
                "bundle_detail_template": "/ops/brain/extensions/{bundle_id}",
                "policy_sets": "/ops/brain/extensions/policy-sets",
                "policy_set_detail_template": "/ops/brain/extensions/policy-sets/{policy_set_id}",
                "policy_history": "/ops/brain/extensions/policy-history",
                "policy_history_detail_template": "/ops/brain/extensions/policy-history/{policy_set_id}",
                "policy_history_compare": "/ops/brain/extensions/policy-history/compare",
                "policy_rollouts": "/ops/brain/extensions/policy-rollouts",
                "certifications": "/ops/brain/extensions/certifications",
                "certification_detail_template": "/ops/brain/extensions/certifications/{artifact_id}",
                "certification_compare": "/ops/brain/extensions/certifications/compare",
            },
        }

    def policy_set_summary(self, *, workspace_id: str = "default") -> dict[str, Any]:
        policy_summary = self.policy.policy_set_summary()
        bundles = self.summary(workspace_id=workspace_id).get("extensions", [])
        bundle_counts: dict[str, int] = {}
        latest_bundles: dict[str, dict[str, Any]] = {}
        for bundle in bundles:
            policy_set_id = bundle.get("policy_set_id")
            if not policy_set_id:
                continue
            bundle_counts[str(policy_set_id)] = bundle_counts.get(str(policy_set_id), 0) + 1
            latest_bundles.setdefault(str(policy_set_id), bundle)
        items = []
        for item in policy_summary.get("items", []):
            policy_set_id = str(item.get("policy_set_id") or "")
            latest_bundle = latest_bundles.get(policy_set_id) or {}
            items.append(
                {
                    **item,
                    "workspace_id": workspace_id,
                    "bundle_count_in_workspace": bundle_counts.get(policy_set_id, 0),
                    "latest_bundle_id": latest_bundle.get("bundle_id"),
                    "latest_bundle_report_id": ((latest_bundle.get("report") or {}).get("report_id")),
                    "latest_bundle_certification_status": latest_bundle.get("certification_status"),
                    "latest_bundle_certification_report_id": latest_bundle.get("certification_report_id"),
                }
            )
        return {
            **policy_summary,
            "workspace_id": workspace_id,
            "items": items,
            "compare_refs": {
                "summary": "/ops/brain/extensions/policy-sets",
                "detail_template": "/ops/brain/extensions/policy-sets/{policy_set_id}",
                "extensions": "/ops/brain/extensions",
                "bundle_detail_template": "/ops/brain/extensions/{bundle_id}",
                "history": "/ops/brain/extensions/policy-history",
                "history_detail_template": "/ops/brain/extensions/policy-history/{policy_set_id}",
                "rollouts": "/ops/brain/extensions/policy-rollouts",
            },
        }

    def policy_set_detail(self, *, policy_set_id: str, version: str | None = None, workspace_id: str = "default") -> dict[str, Any] | None:
        detail = self.policy.policy_set_detail(policy_set_id=policy_set_id, version=version)
        if detail is None:
            return None
        bundles = [
            item
            for item in self.summary(workspace_id=workspace_id).get("extensions", [])
            if item.get("policy_set_id") == policy_set_id and (version is None or str(item.get("policy_set_version")) == str(version))
        ]
        return {
            **detail,
            "workspace_id": workspace_id,
            "bundles": bundles,
            "bundle_count_in_workspace": len(bundles),
            "compare_refs": {
                "summary": "/ops/brain/extensions/policy-sets",
                "extensions": "/ops/brain/extensions",
                "bundle_detail_template": "/ops/brain/extensions/{bundle_id}",
                "history": "/ops/brain/extensions/policy-history",
                "history_detail_template": "/ops/brain/extensions/policy-history/{policy_set_id}",
                "rollouts": "/ops/brain/extensions/policy-rollouts",
            },
        }

    def policy_history_summary(self, *, workspace_id: str = "default") -> dict[str, Any]:
        summary = self.policy_set_summary(workspace_id=workspace_id)
        items = []
        for item in summary.get("items", []):
            items.append(
                {
                    "policy_set_id": item.get("policy_set_id"),
                    "version": item.get("version"),
                    "bundle_family": item.get("bundle_family"),
                    "lineage_anchor_id": item.get("lineage_anchor_id"),
                    "stable_policy_version_id": item.get("stable_policy_version_id"),
                    "artifact_id": item.get("artifact_id"),
                    "artifact_path": item.get("artifact_path"),
                    "status": item.get("status"),
                    "created_from": item.get("created_from"),
                    "supersedes": item.get("supersedes", []),
                    "rollback_reference": item.get("rollback_reference"),
                    "author": item.get("author"),
                    "origin": item.get("origin"),
                    "effective_scope": item.get("effective_scope", {}),
                    "linked_evidence_ids": item.get("linked_evidence_ids", []),
                    "linked_report_ids": item.get("linked_report_ids", []),
                    "bundle_count_in_workspace": item.get("bundle_count_in_workspace", 0),
                }
            )
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "workspace_id": workspace_id,
            "artifact_count": len(items),
            "latest_artifact_id": summary.get("latest_artifact_id"),
            "latest_report_id": summary.get("latest_report_id"),
            "latest_policy_status": summary.get("latest_policy_status"),
            "status_counts": summary.get("status_counts", {}),
            "items": items,
            "compare_refs": {
                "summary": "/ops/brain/extensions/policy-history",
                "detail_template": "/ops/brain/extensions/policy-history/{policy_set_id}",
                "compare": "/ops/brain/extensions/policy-history/compare",
                "policy_sets": "/ops/brain/extensions/policy-sets",
                "rollouts": "/ops/brain/extensions/policy-rollouts",
            },
        }

    def policy_history_detail(self, *, policy_set_id: str, version: str | None = None, workspace_id: str = "default") -> dict[str, Any] | None:
        detail = self.policy.policy_history.detail(policy_set_id=policy_set_id, version=version)
        if detail is None:
            return None
        bundle_matches = [
            item
            for item in self.summary(workspace_id=workspace_id).get("extensions", [])
            if item.get("policy_set_id") == policy_set_id and (version is None or str(item.get("policy_set_version")) == str(version))
        ]
        return {
            **detail,
            "workspace_id": workspace_id,
            "bundles": bundle_matches,
            "bundle_count_in_workspace": len(bundle_matches),
            "lineage": detail.get("lineage", []),
            "lineage_depth": detail.get("lineage_depth", 0),
            "latest_status_transition": detail.get("latest_status_transition"),
            "compare_refs": {
                "summary": "/ops/brain/extensions/policy-history",
                "compare": "/ops/brain/extensions/policy-history/compare",
                "policy_sets": "/ops/brain/extensions/policy-sets",
                "rollouts": "/ops/brain/extensions/policy-rollouts",
            },
        }

    def policy_rollout_summary(self) -> dict[str, Any]:
        rollouts = self.policy.policy_rollout_summary()
        return {
            **rollouts,
            "compare_refs": {
                "summary": "/ops/brain/extensions/policy-rollouts",
                "policy_sets": "/ops/brain/extensions/policy-sets",
                "policy_history": "/ops/brain/extensions/policy-history",
            },
        }

    def certification_summary(self, *, workspace_id: str = "default") -> dict[str, Any]:
        items = self.certification.list(workspace_id=workspace_id, limit=50)
        status_counts: dict[str, int] = {}
        for item in items:
            status = str(item.get("certification_status") or "draft")
            status_counts[status] = status_counts.get(status, 0) + 1
        latest = items[0] if items else {}
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "workspace_id": workspace_id,
            "artifact_count": len(items),
            "latest_artifact_id": latest.get("artifact_id"),
            "latest_report_id": ((latest.get("report") or {}).get("report_id")),
            "latest_certification_status": latest.get("certification_status"),
            "status_counts": status_counts,
            "items": items,
            "compare_refs": {
                "summary": "/ops/brain/extensions/certifications",
                "detail_template": "/ops/brain/extensions/certifications/{artifact_id}",
                "compare": "/ops/brain/extensions/certifications/compare",
                "extensions": "/ops/brain/extensions",
            },
        }

    def certification_detail(self, artifact_id: str) -> dict[str, Any] | None:
        return self.certification.detail(artifact_id)

    def compare_policy_history(
        self,
        *,
        left_policy_set_id: str,
        right_policy_set_id: str,
        left_version: str | None = None,
        right_version: str | None = None,
        workspace_id: str = "default",
    ) -> dict[str, Any] | None:
        left = self.policy_history_detail(policy_set_id=left_policy_set_id, version=left_version, workspace_id=workspace_id)
        right = self.policy_history_detail(policy_set_id=right_policy_set_id, version=right_version, workspace_id=workspace_id)
        if left is None or right is None:
            return None
        left_item = left.get("item") or {}
        right_item = right.get("item") or {}
        left_risks = set(left_item.get("risk_flags", []))
        right_risks = set(right_item.get("risk_flags", []))
        left_reports = set(left_item.get("linked_report_ids", []))
        right_reports = set(right_item.get("linked_report_ids", []))
        left_evidence = set(left_item.get("linked_evidence_ids", []))
        right_evidence = set(right_item.get("linked_evidence_ids", []))
        diff = {
            "status_changed": left_item.get("status") != right_item.get("status"),
            "bundle_family_changed": left_item.get("bundle_family") != right_item.get("bundle_family"),
            "version_changed": left_item.get("version") != right_item.get("version"),
            "rollback_reference_changed": left_item.get("rollback_reference") != right_item.get("rollback_reference"),
            "risk_flags_added": sorted(right_risks - left_risks),
            "risk_flags_removed": sorted(left_risks - right_risks),
            "linked_report_ids_added": sorted(right_reports - left_reports),
            "linked_report_ids_removed": sorted(left_reports - right_reports),
            "linked_evidence_ids_added": sorted(right_evidence - left_evidence),
            "linked_evidence_ids_removed": sorted(left_evidence - right_evidence),
            "supersedes_left": left_item.get("supersedes", []),
            "supersedes_right": right_item.get("supersedes", []),
            "lineage_depth_left": left.get("lineage_depth", 0),
            "lineage_depth_right": right.get("lineage_depth", 0),
            "latest_status_transition_left": left.get("latest_status_transition"),
            "latest_status_transition_right": right.get("latest_status_transition"),
        }
        export = build_policy_compare_report(
            artifacts_dir=self.policy.policy_history.artifacts_dir,
            left=self._policy_compare_card(left_item),
            right=self._policy_compare_card(right_item),
            diff=diff,
        )
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "left": self._policy_compare_card(left_item),
            "right": self._policy_compare_card(right_item),
            "scene_delta": {
                "refs": {
                    "left": f"{left_item.get('policy_set_id')}@{left_item.get('version')}",
                    "right": f"{right_item.get('policy_set_id')}@{right_item.get('version')}",
                },
                "hot_subjects": [
                    {
                        "subject": risk,
                        "delta": (1 if risk in right_risks else 0) - (1 if risk in left_risks else 0),
                    }
                    for risk in sorted(left_risks | right_risks)
                    if risk in left_risks.symmetric_difference(right_risks)
                ],
                "hot_links": [
                    {"link_id": "linked_report_count_delta", "delta": len(right_reports) - len(left_reports)},
                    {"link_id": "linked_evidence_count_delta", "delta": len(right_evidence) - len(left_evidence)},
                ],
            },
            "diff": diff,
            "export": export,
            "compare_refs": {
                "summary": "/ops/brain/extensions/policy-history",
                "detail_template": "/ops/brain/extensions/policy-history/{policy_set_id}",
            },
        }

    def compare_certifications(self, *, left_artifact_id: str, right_artifact_id: str) -> dict[str, Any] | None:
        left = self.certification_detail(left_artifact_id)
        right = self.certification_detail(right_artifact_id)
        if left is None or right is None:
            return None
        left_item = left.get("item") or {}
        right_item = right.get("item") or {}
        left_risks = set(left_item.get("risk_flags", []))
        right_risks = set(right_item.get("risk_flags", []))
        left_reviews = set(left_item.get("adversary_review_report_ids", []))
        right_reviews = set(right_item.get("adversary_review_report_ids", []))
        left_tools = set(left_item.get("allowed_tools", []))
        right_tools = set(right_item.get("allowed_tools", []))
        diff = {
            "certification_status_changed": left_item.get("certification_status") != right_item.get("certification_status"),
            "policy_status_changed": left_item.get("policy_status") != right_item.get("policy_status"),
            "privilege_inheritance_confusion_changed": left_item.get("privilege_inheritance_confusion") != right_item.get("privilege_inheritance_confusion"),
            "risk_flags_added": sorted(right_risks - left_risks),
            "risk_flags_removed": sorted(left_risks - right_risks),
            "allowed_tools_added": sorted(right_tools - left_tools),
            "allowed_tools_removed": sorted(left_tools - right_tools),
            "adversary_review_report_ids_added": sorted(right_reviews - left_reviews),
            "adversary_review_report_ids_removed": sorted(left_reviews - right_reviews),
            "remediation_actions_left": left_item.get("recommended_remediation_actions", []),
            "remediation_actions_right": right_item.get("recommended_remediation_actions", []),
            "restoration_detected_changed": left_item.get("restoration_detected") != right_item.get("restoration_detected"),
            "supersedes_artifact_changed": left_item.get("supersedes_artifact_id") != right_item.get("supersedes_artifact_id"),
            "certification_lineage_depth_left": left_item.get("certification_lineage_depth", 0),
            "certification_lineage_depth_right": right_item.get("certification_lineage_depth", 0),
            "certification_lineage_statuses_left": left_item.get("certification_lineage_statuses", []),
            "certification_lineage_statuses_right": right_item.get("certification_lineage_statuses", []),
            "historical_certification_artifact_ids_left": left_item.get("historical_certification_artifact_ids", []),
            "historical_certification_artifact_ids_right": right_item.get("historical_certification_artifact_ids", []),
            "restored_from_certification_artifact_ids_left": left_item.get("restored_from_certification_artifact_ids", []),
            "restored_from_certification_artifact_ids_right": right_item.get("restored_from_certification_artifact_ids", []),
            "permission_delta_left": left_item.get("permission_delta_from_previous", {}),
            "permission_delta_right": right_item.get("permission_delta_from_previous", {}),
        }
        export = build_extension_certification_compare_report(
            artifacts_dir=self.provenance.artifacts_dir,
            left=self._certification_compare_card(left_item),
            right=self._certification_compare_card(right_item),
            diff=diff,
        )
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "left": self._certification_compare_card(left_item),
            "right": self._certification_compare_card(right_item),
            "scene_delta": {
                "refs": {
                    "left": left_artifact_id,
                    "right": right_artifact_id,
                },
                "hot_subjects": [
                    {
                        "subject": risk,
                        "delta": (1 if risk in right_risks else 0) - (1 if risk in left_risks else 0),
                    }
                    for risk in sorted(left_risks | right_risks)
                    if risk in left_risks.symmetric_difference(right_risks)
                ],
                "hot_links": [
                    {"link_id": "allowed_tool_count_delta", "delta": len(right_tools) - len(left_tools)},
                    {"link_id": "adversary_report_count_delta", "delta": len(right_reviews) - len(left_reviews)},
                ],
            },
            "diff": diff,
            "export": export,
            "compare_refs": {
                "summary": "/ops/brain/extensions/certifications",
                "detail_template": "/ops/brain/extensions/certifications/{artifact_id}",
            },
        }

    def resolve_requested_extensions(self, *, workspace_id: str, requested_extensions: list[str]) -> dict[str, Any]:
        requested_extensions = list(requested_extensions or [])
        summary = self.summary(workspace_id=workspace_id)
        bundles_by_id = {item.get("bundle_id"): item for item in summary.get("extensions", [])}
        selected_bundles: list[dict[str, Any]] = []
        denied_extensions: list[str] = []
        policy_path: list[dict[str, Any]] = []
        approval_modes: set[str] = set()
        risk_flags: set[str] = set()
        for extension_id in requested_extensions:
            bundle = bundles_by_id.get(extension_id)
            if bundle is None:
                denied_extensions.append(extension_id)
                policy_path.append({"bundle_id": extension_id, "decision": "deny", "reason": "bundle-outside-workspace-scope"})
                continue
            approval = bundle.get("approval_path") or {}
            decision = approval.get("decision", "allow")
            if decision == "deny":
                denied_extensions.append(extension_id)
                policy_path.append({"bundle_id": extension_id, "decision": "deny", "reason": approval.get("reason")})
                continue
            selected_bundles.append(bundle)
            approval_modes.add(decision)
            risk_flags.update(bundle.get("risk_flags", []))
            policy_path.append(
                {
                    "bundle_id": extension_id,
                    "decision": "match",
                    "approval_behavior": decision,
                    "workspace_scopes": bundle.get("workspace_scopes", []),
                    "policy_set_id": bundle.get("policy_set_id"),
                    "policy_set_version": bundle.get("policy_set_version"),
                    "bundle_family": bundle.get("bundle_family"),
                    "policy_status": ((bundle.get("policy_lifecycle") or {}).get("status")),
                    "certification_status": bundle.get("certification_status"),
                }
            )
        if denied_extensions:
            decision = "deny"
            fallback_reason = "extension-outside-allowlist"
        elif "allow-if-approved" in approval_modes:
            decision = "allow-if-approved"
            fallback_reason = "extension-approval-required"
        elif "ask" in approval_modes:
            decision = "ask"
            fallback_reason = "extension-ask-fallback"
        else:
            decision = "allow"
            fallback_reason = None
        return {
            "workspace_id": workspace_id,
            "requested_extensions": requested_extensions,
            "decision": decision,
            "fallback_reason": fallback_reason,
            "denied_extensions": denied_extensions,
            "selected_bundle_ids": [item.get("bundle_id") for item in selected_bundles if item.get("bundle_id")],
            "selected_policy_set_ids": sorted({item.get("policy_set_id") for item in selected_bundles if item.get("policy_set_id")}),
            "selected_policy_set_versions": sorted({item.get("policy_set_version") for item in selected_bundles if item.get("policy_set_version")}),
            "selected_bundle_families": sorted({item.get("bundle_family") for item in selected_bundles if item.get("bundle_family")}),
            "selected_policy_history_ids": sorted({((item.get("policy_lifecycle") or {}).get("artifact_id")) for item in selected_bundles if ((item.get("policy_lifecycle") or {}).get("artifact_id"))}),
            "selected_policy_statuses": sorted({((item.get("policy_lifecycle") or {}).get("status")) for item in selected_bundles if ((item.get("policy_lifecycle") or {}).get("status"))}),
            "selected_bundle_certification_ids": sorted({item.get("certification_artifact_id") for item in selected_bundles if item.get("certification_artifact_id")}),
            "selected_bundle_certification_statuses": sorted({item.get("certification_status") for item in selected_bundles if item.get("certification_status")}),
            "selected_bundles": selected_bundles,
            "allowed_tools": sorted({tool for item in selected_bundles for tool in item.get("allowed_tools", [])}),
            "risk_flags": sorted(risk_flags),
            "policy_path": policy_path,
            "selected_bundle_artifact_ids": [item.get("artifact_id") for item in selected_bundles if item.get("artifact_id")],
            "selected_bundle_report_ids": [((item.get("report") or {}).get("report_id")) for item in selected_bundles if (item.get("report") or {}).get("report_id")],
            "selected_policy_report_ids": [((((item.get("policy_lifecycle") or {}).get("report")) or {}).get("report_id")) for item in selected_bundles if (((item.get("policy_lifecycle") or {}).get("report")) or {}).get("report_id")],
            "selected_bundle_certification_report_ids": [item.get("certification_report_id") for item in selected_bundles if item.get("certification_report_id")],
            "selected_bundle_provenance": [
                {
                    "bundle_id": item.get("bundle_id"),
                    "artifact_id": item.get("artifact_id"),
                    "report_id": ((item.get("report") or {}).get("report_id")),
                    "risk_flags": item.get("risk_flags", []),
                    "allowed_tools": item.get("allowed_tools", []),
                    "policy_set_id": item.get("policy_set_id"),
                    "policy_set_version": item.get("policy_set_version"),
                    "bundle_family": item.get("bundle_family"),
                    "approval_path": item.get("approval_path", {}),
                    "policy_lifecycle": item.get("policy_lifecycle", {}),
                    "certification_artifact_id": item.get("certification_artifact_id"),
                    "certification_status": item.get("certification_status"),
                    "certification_report_id": item.get("certification_report_id"),
                }
                for item in selected_bundles
            ],
            "linked_report_ids": sorted(
                {
                    *[
                        ((item.get("report") or {}).get("report_id"))
                        for item in selected_bundles
                        if (item.get("report") or {}).get("report_id")
                    ],
                    *[
                        ((((item.get("policy_lifecycle") or {}).get("report")) or {}).get("report_id"))
                        for item in selected_bundles
                        if (((item.get("policy_lifecycle") or {}).get("report")) or {}).get("report_id")
                    ],
                    *[
                        item.get("certification_report_id")
                        for item in selected_bundles
                        if item.get("certification_report_id")
                    ],
                }
            ),
        }

    def _normalize(self, item: dict[str, Any]) -> dict[str, Any]:
        payload = dict(item)
        payload["mcp_compatible"] = payload.get("extension_kind") in {"mcp", "acp-provider"}
        payload["roots"] = [str(root).replace("{project_root}", self.project_root) for root in payload.get("roots", [])]
        return payload

    def _bundle_record(self, *, item: dict[str, Any], workspace_id: str) -> dict[str, Any]:
        bundle_id = str(item.get("extension_id"))
        allowed_tools = self.policy.EXTENSION_TOOL_MAP.get(bundle_id, [])
        acp_compatibility = (
            self.acp_bridge.compatibility_summary(
                requested_tools=allowed_tools,
                requested_extensions=[bundle_id],
                subagent_mode="parallel",
            )
            if self.acp_bridge is not None
            else {"items": []}
        )
        policy = self.policy.evaluate(
            bundle=item,
            workspace_id=workspace_id,
            permission_summary=self.permission_service.summary() if self.permission_service is not None else None,
            sandbox_summary=self.sandbox_service.summary() if self.sandbox_service is not None else None,
            acp_compatibility=acp_compatibility,
        )
        recent_reviews = (((self.adversary_review.summary() if self.adversary_review is not None else {}) or {}).get("recent_reviews")) or []
        certification = self.certification.record(
            bundle={
                "bundle_id": bundle_id,
                "label": item.get("label"),
                "workspace_id": workspace_id,
                "enabled_state": "enabled" if item.get("enabled", False) else "disabled",
                "workspace_scopes": item.get("workspace_scopes", []),
                "roots": item.get("roots", []),
                **policy,
            },
            recent_reviews=recent_reviews,
        )
        record = self.provenance.record(
            bundle={
                "bundle_id": bundle_id,
                "extension_id": bundle_id,
                "label": item.get("label"),
                "workspace_id": workspace_id,
                "enabled_state": "enabled" if item.get("enabled", False) else "disabled",
                "extension_kind": item.get("extension_kind"),
                "mcp_compatible": item.get("mcp_compatible", False),
                "workspace_scopes": item.get("workspace_scopes", []),
                "roots": item.get("roots", []),
                "certification_status": certification.get("certification_status"),
                "certification_artifact_id": certification.get("artifact_id"),
                "certification_report_id": ((certification.get("report") or {}).get("report_id")),
                "stable_certification_id": certification.get("stable_certification_id"),
                "certification_lineage_depth": certification.get("certification_lineage_depth"),
                "certification_lineage_statuses": certification.get("certification_lineage_statuses", []),
                "historical_certification_artifact_ids": certification.get("historical_certification_artifact_ids", []),
                "historical_certification_statuses": certification.get("historical_certification_statuses", []),
                "restoration_detected": certification.get("restoration_detected", False),
                "restored_from_policy_versions": certification.get("restored_from_policy_versions", []),
                "restored_from_certification_artifact_ids": certification.get("restored_from_certification_artifact_ids", []),
                "restored_from_certification_statuses": certification.get("restored_from_certification_statuses", []),
                "policy_lineage_statuses": certification.get("policy_lineage_statuses", []),
                "adversary_review_report_ids": certification.get("adversary_review_report_ids", []),
                "privilege_inheritance_confusion": certification.get("privilege_inheritance_confusion", False),
                **policy,
            }
        )
        return {
            **item,
            **policy,
            "certification": certification,
            "certification_status": certification.get("certification_status"),
            "certification_artifact_id": certification.get("artifact_id"),
            "certification_report_id": ((certification.get("report") or {}).get("report_id")),
            "adversary_review_report_ids": certification.get("adversary_review_report_ids", []),
            "privilege_inheritance_confusion": certification.get("privilege_inheritance_confusion", False),
            **record,
        }

    def _risk_flag_counts(self, bundles: list[dict[str, Any]]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for bundle in bundles:
            for flag in bundle.get("risk_flags", []):
                counts[flag] = counts.get(flag, 0) + 1
        return counts

    def _policy_compare_card(self, item: dict[str, Any]) -> dict[str, Any]:
        return {
            "policy_set_id": item.get("policy_set_id"),
            "version": item.get("version"),
            "status": item.get("status"),
            "bundle_family": item.get("bundle_family"),
            "artifact_id": item.get("artifact_id"),
            "report_id": ((item.get("report") or {}).get("report_id")),
            "risk_flags": item.get("risk_flags", []),
            "rollback_reference": item.get("rollback_reference"),
            "linked_report_ids": item.get("linked_report_ids", []),
            "linked_evidence_ids": item.get("linked_evidence_ids", []),
            "lineage_anchor_id": item.get("lineage_anchor_id"),
            "stable_policy_version_id": item.get("stable_policy_version_id"),
            "latest_status_transition": (item.get("status_history") or [{}])[-1],
        }

    def _certification_compare_card(self, item: dict[str, Any]) -> dict[str, Any]:
        return {
            "artifact_id": item.get("artifact_id"),
            "bundle_id": item.get("bundle_id"),
            "bundle_family": item.get("bundle_family"),
            "policy_set_id": item.get("policy_set_id"),
            "policy_set_version": item.get("policy_set_version"),
            "policy_status": item.get("policy_status"),
            "certification_status": item.get("certification_status"),
            "privilege_inheritance_confusion": item.get("privilege_inheritance_confusion"),
            "allowed_tools": item.get("allowed_tools", []),
            "risk_flags": item.get("risk_flags", []),
            "adversary_review_report_ids": item.get("adversary_review_report_ids", []),
            "report_id": ((item.get("report") or {}).get("report_id")),
            "lineage_anchor_id": item.get("lineage_anchor_id"),
            "stable_certification_id": item.get("stable_certification_id"),
            "supersedes_artifact_id": item.get("supersedes_artifact_id"),
            "policy_lineage_statuses": item.get("policy_lineage_statuses", []),
            "restoration_detected": item.get("restoration_detected"),
            "restored_from_policy_versions": item.get("restored_from_policy_versions", []),
            "restored_from_certification_artifact_ids": item.get("restored_from_certification_artifact_ids", []),
            "restored_from_certification_statuses": item.get("restored_from_certification_statuses", []),
            "historical_certification_artifact_ids": item.get("historical_certification_artifact_ids", []),
            "historical_certification_statuses": item.get("historical_certification_statuses", []),
            "certification_lineage_depth": item.get("certification_lineage_depth", 0),
            "certification_lineage_statuses": item.get("certification_lineage_statuses", []),
            "latest_certification_transition": item.get("latest_certification_transition"),
            "permission_delta_from_previous": item.get("permission_delta_from_previous", {}),
            "risk_flag_delta_from_previous": item.get("risk_flag_delta_from_previous", {}),
        }

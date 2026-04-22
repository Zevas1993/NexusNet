from __future__ import annotations

from typing import Any

from .capabilities import ACPBridgeCapabilityService
from .health import ACPBridgeHealthService
from nexusnet.providers.acp.diagnostics import ACPProviderDiagnostics


class ACPBridgeService:
    def __init__(self, *, catalog: Any, artifacts_dir: str | None = None):
        self.catalog = catalog
        self.capabilities = ACPBridgeCapabilityService()
        self.diagnostics = ACPProviderDiagnostics(artifacts_dir=artifacts_dir)
        self.health = ACPBridgeHealthService(diagnostics=self.diagnostics, capabilities=self.capabilities)

    def summary(self) -> dict[str, Any]:
        catalog = self.catalog.summary()
        health = self.health.summarize(providers=catalog.get("providers", []))
        providers = health.get("providers", [])
        return {
            "status_label": "EXPLORATORY / PROTOTYPE",
            "enabled": catalog.get("enabled", False),
            "provider_count": len(providers),
            "providers": providers,
            "health": health,
            "compare_refs": {
                "health": "/ops/brain/acp/health",
                "provider_detail_template": "/ops/brain/acp/providers/{provider_id}",
                "provider_compare": "/ops/brain/acp/providers/compare",
                "compatibility": "/ops/brain/acp/compatibility",
            },
        }

    def health_summary(self) -> dict[str, Any]:
        return self.health.summarize(providers=self.catalog.summary().get("providers", []))

    def provider_detail(self, provider_id: str) -> dict[str, Any] | None:
        health = self.health_summary()
        for provider in health.get("providers", []):
            if provider.get("provider_id") == provider_id:
                capability = provider.get("capabilities") or {}
                diagnostic = provider.get("diagnostic") or {}
                compatibility_examples = self.compatibility_summary(
                    requested_tools=["filesystem.write"],
                    requested_extensions=["acp-coding-lane"],
                    subagent_mode="parallel",
                )
                provider_example = next(
                    (item for item in compatibility_examples.get("items", []) if item.get("provider_id") == provider_id),
                    None,
                )
                return {
                    "status_label": "EXPLORATORY / PROTOTYPE",
                    "provider": provider,
                    "operator_summary": {
                        "headline": diagnostic.get("readiness_summary"),
                        "recommended_action": diagnostic.get("recommended_action"),
                        "remediation_actions": diagnostic.get("remediation_actions", []),
                        "config_gaps": diagnostic.get("config_gaps", []),
                        "readiness_checks": diagnostic.get("readiness_checks", []),
                        "probe_mode": diagnostic.get("probe_mode"),
                        "probe_status": diagnostic.get("probe_status"),
                        "probe_readiness_state": diagnostic.get("probe_readiness_state"),
                        "probe_contract_id": diagnostic.get("probe_contract_id"),
                        "probe_execution_policy": diagnostic.get("probe_execution_policy"),
                        "supports_live_probe": diagnostic.get("supports_live_probe", False),
                        "live_probe_blockers": diagnostic.get("live_probe_blockers", []),
                        "bounded_probe_budget": diagnostic.get("bounded_probe_budget", {}),
                        "bounded_probe_summary": diagnostic.get("bounded_probe_summary"),
                        "version_compatible": diagnostic.get("version_compatible", True),
                        "feature_compatibility_status": (capability.get("feature_compatibility") or {}).get("status"),
                        "workspace_scope_support": capability.get("workspace_scope_support"),
                        "compatibility_fixture_count": len(capability.get("compatibility_fixtures", [])),
                        "live_probe_example_count": len(capability.get("live_probe_examples", [])),
                        "bundle_family_compatibility": capability.get("bundle_family_compatibility", []),
                    },
                    "compatibility_example": provider_example,
                    "compare_refs": {
                        "health": "/ops/brain/acp/health",
                        "provider_compare": "/ops/brain/acp/providers/compare",
                        "compatibility": "/ops/brain/acp/compatibility",
                    },
                }
        return None

    def compare_providers(self, left_provider_id: str, right_provider_id: str) -> dict[str, Any] | None:
        left = self.provider_detail(left_provider_id)
        right = self.provider_detail(right_provider_id)
        if left is None or right is None:
            return None
        left_provider = left.get("provider") or {}
        right_provider = right.get("provider") or {}
        left_summary = left.get("operator_summary") or {}
        right_summary = right.get("operator_summary") or {}
        left_bundles = set(left_summary.get("bundle_family_compatibility", []))
        right_bundles = set(right_summary.get("bundle_family_compatibility", []))
        left_remediation = set(left_summary.get("remediation_actions", []))
        right_remediation = set(right_summary.get("remediation_actions", []))
        left_gaps = set(left_summary.get("config_gaps", []))
        right_gaps = set(right_summary.get("config_gaps", []))
        diff = {
            "status_changed": (left_provider.get("diagnostic") or {}).get("status") != (right_provider.get("diagnostic") or {}).get("status"),
            "probe_mode_changed": left_summary.get("probe_mode") != right_summary.get("probe_mode"),
            "probe_status_changed": left_summary.get("probe_status") != right_summary.get("probe_status"),
            "probe_readiness_state_changed": left_summary.get("probe_readiness_state") != right_summary.get("probe_readiness_state"),
            "probe_execution_policy_changed": left_summary.get("probe_execution_policy") != right_summary.get("probe_execution_policy"),
            "version_compatible_changed": left_summary.get("version_compatible") != right_summary.get("version_compatible"),
            "feature_compatibility_changed": left_summary.get("feature_compatibility_status") != right_summary.get("feature_compatibility_status"),
            "bundle_families_added": sorted(right_bundles - left_bundles),
            "bundle_families_removed": sorted(left_bundles - right_bundles),
            "remediation_actions_added": sorted(right_remediation - left_remediation),
            "remediation_actions_removed": sorted(left_remediation - right_remediation),
            "config_gaps_added": sorted(right_gaps - left_gaps),
            "config_gaps_removed": sorted(left_gaps - right_gaps),
            "live_probe_blockers_added": sorted(
                set(right_summary.get("live_probe_blockers", [])) - set(left_summary.get("live_probe_blockers", []))
            ),
            "live_probe_blockers_removed": sorted(
                set(left_summary.get("live_probe_blockers", [])) - set(right_summary.get("live_probe_blockers", []))
            ),
            "live_probe_example_count_delta": int(right_summary.get("live_probe_example_count", 0)) - int(left_summary.get("live_probe_example_count", 0)),
            "compatibility_fixture_count_delta": int(right_summary.get("compatibility_fixture_count", 0)) - int(left_summary.get("compatibility_fixture_count", 0)),
        }
        left_card = self._compare_card(left_provider, left_summary)
        right_card = self._compare_card(right_provider, right_summary)
        export = self.diagnostics.write_compare_report(left=left_card, right=right_card, diff=diff)
        return {
            "status_label": "EXPLORATORY / PROTOTYPE",
            "left": left_card,
            "right": right_card,
            "scene_delta": {
                "refs": {"left": left_provider_id, "right": right_provider_id},
                "hot_subjects": [
                    {
                        "subject": item,
                        "delta": (1 if item in right_gaps else 0) - (1 if item in left_gaps else 0),
                    }
                    for item in sorted(left_gaps | right_gaps)
                    if item in left_gaps.symmetric_difference(right_gaps)
                ],
                "hot_links": [
                    {"link_id": "compatibility_fixture_count_delta", "delta": diff["compatibility_fixture_count_delta"]},
                    {"link_id": "live_probe_example_count_delta", "delta": diff["live_probe_example_count_delta"]},
                ],
            },
            "diff": diff,
            "human_summary": (
                f"ACP compare `{left_provider_id}` vs `{right_provider_id}` tracks "
                f"`{left_summary.get('probe_mode')}` -> `{right_summary.get('probe_mode')}` "
                f"with {len(diff['remediation_actions_added']) + len(diff['remediation_actions_removed'])} remediation deltas."
            ),
            "export": export,
            "compare_refs": {
                "health": "/ops/brain/acp/health",
                "provider_detail_template": "/ops/brain/acp/providers/{provider_id}",
                "provider_compare": "/ops/brain/acp/providers/compare",
                "compatibility": "/ops/brain/acp/compatibility",
            },
        }

    def compatibility_summary(
        self,
        *,
        requested_tools: list[str] | None = None,
        requested_extensions: list[str] | None = None,
        subagent_mode: str | None = None,
    ) -> dict[str, Any]:
        requested_tools = list(requested_tools or [])
        requested_extensions = list(requested_extensions or [])
        health = self.health_summary()
        items = []
        for provider in health.get("providers", []):
            capability = provider.get("capabilities") or {}
            diagnostic = provider.get("diagnostic") or {}
            tool_compatibility = set(capability.get("tool_compatibility") or [])
            extension_compatibility = set(capability.get("extension_compatibility") or [])
            supported_modes = set(((capability.get("subagent_compatibility") or {}).get("modes") or []))
            missing_tools = [tool for tool in requested_tools if tool not in tool_compatibility]
            missing_extensions = [extension for extension in requested_extensions if extension not in extension_compatibility]
            mode_supported = subagent_mode is None or subagent_mode in supported_modes
            feature_status = (capability.get("feature_compatibility") or {}).get("status")
            items.append(
                {
                    "provider_id": provider.get("provider_id"),
                    "status": diagnostic.get("status"),
                    "compatible": (
                        not missing_tools
                        and not missing_extensions
                        and mode_supported
                        and diagnostic.get("status") == "ready-if-reachable"
                        and bool(diagnostic.get("version_compatible", True))
                        and feature_status == "compatible"
                    ),
                    "missing_tools": missing_tools,
                    "missing_extensions": missing_extensions,
                    "requested_tools": requested_tools,
                    "requested_extensions": requested_extensions,
                    "requested_subagent_mode": subagent_mode,
                    "mode_supported": mode_supported,
                    "supported_modes": sorted(supported_modes),
                    "supported_extensions": sorted(extension_compatibility),
                    "supported_bundle_families": sorted(capability.get("bundle_family_compatibility", []) or []),
                    "compatibility_fixture_ids": [
                        item.get("fixture_id")
                        for item in capability.get("compatibility_fixtures", [])
                        if item.get("fixture_id")
                    ],
                    "probe_mode": diagnostic.get("probe_mode"),
                    "probe_status": diagnostic.get("probe_status"),
                    "probe_readiness_state": diagnostic.get("probe_readiness_state"),
                    "probe_contract_id": diagnostic.get("probe_contract_id"),
                    "probe_execution_policy": diagnostic.get("probe_execution_policy"),
                    "supports_live_probe": diagnostic.get("supports_live_probe", False),
                    "live_probe_example_ids": [
                        item.get("probe_id")
                        for item in capability.get("live_probe_examples", [])
                        if item.get("probe_id")
                    ],
                    "version_compatible": diagnostic.get("version_compatible", True),
                    "feature_compatibility_status": feature_status,
                    "missing_features": (capability.get("feature_compatibility") or {}).get("missing_features", []),
                    "config_gaps": diagnostic.get("config_gaps", []),
                    "live_probe_blockers": diagnostic.get("live_probe_blockers", []),
                    "bounded_probe_budget": diagnostic.get("bounded_probe_budget", {}),
                    "bounded_probe_summary": diagnostic.get("bounded_probe_summary"),
                    "readiness_checks": diagnostic.get("readiness_checks", []),
                    "readiness_summary": diagnostic.get("readiness_summary"),
                    "recommended_action": diagnostic.get("recommended_action"),
                    "remediation_actions": diagnostic.get("remediation_actions", []),
                }
            )
        return {
            "status_label": "EXPLORATORY / PROTOTYPE",
            "requested_tools": requested_tools,
            "requested_extensions": requested_extensions,
            "requested_subagent_mode": subagent_mode,
            "compatible_provider_count": sum(1 for item in items if item.get("compatible")),
            "items": items,
        }

    def _compare_card(self, provider: dict[str, Any], operator_summary: dict[str, Any]) -> dict[str, Any]:
        capability = provider.get("capabilities") or {}
        diagnostic = provider.get("diagnostic") or {}
        return {
            "provider_id": provider.get("provider_id"),
            "provider_kind": provider.get("provider_kind"),
            "status": diagnostic.get("status"),
            "probe_mode": operator_summary.get("probe_mode"),
            "probe_status": operator_summary.get("probe_status"),
            "probe_readiness_state": operator_summary.get("probe_readiness_state"),
            "recommended_action": operator_summary.get("recommended_action"),
            "remediation_actions": operator_summary.get("remediation_actions", []),
            "config_gaps": operator_summary.get("config_gaps", []),
            "live_probe_blockers": operator_summary.get("live_probe_blockers", []),
            "probe_execution_policy": operator_summary.get("probe_execution_policy"),
            "bounded_probe_budget": operator_summary.get("bounded_probe_budget", {}),
            "bundle_family_compatibility": operator_summary.get("bundle_family_compatibility", []),
            "feature_compatibility_status": operator_summary.get("feature_compatibility_status"),
            "version_compatible": operator_summary.get("version_compatible"),
            "compatibility_fixture_ids": [
                item.get("fixture_id")
                for item in capability.get("compatibility_fixtures", [])
                if item.get("fixture_id")
            ],
            "live_probe_example_ids": [
                item.get("probe_id")
                for item in capability.get("live_probe_examples", [])
                if item.get("probe_id")
            ],
        }

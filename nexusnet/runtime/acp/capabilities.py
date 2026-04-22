from __future__ import annotations

from typing import Any


class ACPBridgeCapabilityService:
    def provider_capabilities(self, provider: dict[str, Any]) -> dict[str, Any]:
        provider_kind = str(provider.get("provider_kind") or "unknown")
        provider_id = str(provider.get("provider_id") or provider_kind)
        declared_protocol_version = str(provider.get("protocol_version") or "1.0")
        feature_flags = list(provider.get("feature_flags") or [])
        if provider_kind == "coding-agent":
            capabilities = ["code-review", "bounded-edit-plan", "subagent-compatible"]
            tool_compatibility = ["filesystem.readonly", "filesystem.write", "shell.exec"]
            subagent_modes = ["sequential", "parallel"]
            required_features = ["bounded-edit-plan", "subagent-compatible"]
            extension_compatibility = ["acp-coding-lane", "mcp-filesystem"]
            bundle_family_compatibility = ["acp-provider-lane", "filesystem-bridge"]
            workspace_scope_support = "roots-aware"
        elif provider_kind == "review-agent":
            capabilities = ["review-report", "trace-audit", "subagent-compatible"]
            tool_compatibility = ["governance.audit", "retrieval.query"]
            subagent_modes = ["sequential"]
            required_features = ["review-report"]
            extension_compatibility = ["acp-coding-lane"]
            bundle_family_compatibility = ["acp-provider-lane", "retrieval-pack"]
            workspace_scope_support = "provider-scoped"
        else:
            capabilities = ["bounded-provider"]
            tool_compatibility = []
            subagent_modes = []
            required_features = []
            extension_compatibility = []
            bundle_family_compatibility = []
            workspace_scope_support = "unknown"
        if not feature_flags:
            feature_flags = capabilities[:]
        missing_features = [feature for feature in required_features if feature not in feature_flags]
        compatibility_fixtures = [
            {
                "fixture_id": f"{provider_kind}-{family}-fixture",
                "bundle_family": family,
                "required_tools": [tool for tool in tool_compatibility[:2]],
                "required_extensions": [extension for extension in extension_compatibility[:1]],
                "readiness_checks": [
                    "provider-enabled",
                    "endpoint-configured",
                    "protocol-version-compatible",
                    "feature-flags-declared",
                ],
            }
            for family in bundle_family_compatibility
        ]
        live_probe_examples = [
            {
                "probe_id": f"{provider_id}-{family}-probe",
                "bundle_family": family,
                "requested_tools": [tool for tool in tool_compatibility[:2]],
                "requested_extensions": [extension for extension in extension_compatibility[:1]],
                "subagent_mode": subagent_modes[0] if subagent_modes else None,
                "expected_outcome": "bounded-readiness",
            }
            for family in bundle_family_compatibility
        ]
        return {
            "provider_id": provider.get("provider_id"),
            "provider_kind": provider_kind,
            "declared_protocol_version": declared_protocol_version,
            "capability_inventory": capabilities,
            "feature_flags": feature_flags,
            "required_features": required_features,
            "missing_features": missing_features,
            "tool_compatibility": tool_compatibility,
            "extension_compatibility": extension_compatibility,
            "bundle_family_compatibility": bundle_family_compatibility,
            "compatibility_fixtures": compatibility_fixtures,
            "subagent_compatibility": {
                "supported": bool(subagent_modes),
                "modes": subagent_modes,
                "tool_inheritance_mode": "bounded-intersection",
            },
            "workspace_scope_support": workspace_scope_support,
            "probe_contract": {
                "probe_contract_id": f"{provider_id}-bounded-live-probe",
                "requires_endpoint": True,
                "requires_auth": True,
                "example_requested_tools": tool_compatibility[:2],
                "example_requested_extensions": extension_compatibility[:1],
                "example_subagent_mode": subagent_modes[0] if subagent_modes else None,
            },
            "live_probe_examples": live_probe_examples,
            "feature_compatibility": {
                "status": "compatible" if not missing_features else "missing-features",
                "missing_features": missing_features,
            },
        }

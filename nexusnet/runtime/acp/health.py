from __future__ import annotations

from typing import Any


class ACPBridgeHealthService:
    def __init__(self, *, diagnostics: Any, capabilities: Any):
        self.diagnostics = diagnostics
        self.capabilities = capabilities

    def summarize(self, *, providers: list[dict[str, Any]]) -> dict[str, Any]:
        items = []
        status_counts: dict[str, int] = {}
        failure_pattern_counts: dict[str, int] = {}
        timeout_pattern_counts: dict[str, int] = {}
        probe_mode_counts: dict[str, int] = {}
        probe_status_counts: dict[str, int] = {}
        probe_readiness_state_counts: dict[str, int] = {}
        remediation_action_counts: dict[str, int] = {}
        recommended_action_counts: dict[str, int] = {}
        config_gap_counts: dict[str, int] = {}
        live_probe_blocker_counts: dict[str, int] = {}
        compatibility_fixture_count = 0
        live_probe_example_count = 0
        for provider in providers:
            diagnostic = self.diagnostics.run(provider=provider)
            capability = self.capabilities.provider_capabilities(provider)
            item = {**provider, "diagnostic": diagnostic, "capabilities": capability}
            items.append(item)
            status = diagnostic.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
            failure_pattern = diagnostic.get("failure_pattern", "unknown")
            timeout_pattern = diagnostic.get("timeout_pattern", "unknown")
            probe_mode = diagnostic.get("probe_mode", "unknown")
            probe_status = diagnostic.get("probe_status", "unknown")
            probe_readiness_state = diagnostic.get("probe_readiness_state", "unknown")
            failure_pattern_counts[failure_pattern] = failure_pattern_counts.get(failure_pattern, 0) + 1
            timeout_pattern_counts[timeout_pattern] = timeout_pattern_counts.get(timeout_pattern, 0) + 1
            probe_mode_counts[probe_mode] = probe_mode_counts.get(probe_mode, 0) + 1
            probe_status_counts[probe_status] = probe_status_counts.get(probe_status, 0) + 1
            probe_readiness_state_counts[probe_readiness_state] = probe_readiness_state_counts.get(probe_readiness_state, 0) + 1
            for action in diagnostic.get("remediation_actions", []):
                remediation_action_counts[action] = remediation_action_counts.get(action, 0) + 1
            recommended_action = diagnostic.get("recommended_action")
            if recommended_action:
                recommended_action_counts[recommended_action] = recommended_action_counts.get(recommended_action, 0) + 1
            for gap in diagnostic.get("config_gaps", []):
                config_gap_counts[gap] = config_gap_counts.get(gap, 0) + 1
            for blocker in diagnostic.get("live_probe_blockers", []):
                live_probe_blocker_counts[blocker] = live_probe_blocker_counts.get(blocker, 0) + 1
            compatibility_fixture_count += len(capability.get("compatibility_fixtures", []))
            live_probe_example_count += len(capability.get("live_probe_examples", []))
        return {
            "status_label": "EXPLORATORY / PROTOTYPE",
            "provider_count": len(items),
            "status_counts": status_counts,
            "failure_pattern_counts": failure_pattern_counts,
            "timeout_pattern_counts": timeout_pattern_counts,
            "probe_mode_counts": probe_mode_counts,
            "probe_status_counts": probe_status_counts,
            "probe_readiness_state_counts": probe_readiness_state_counts,
            "remediation_action_counts": remediation_action_counts,
            "recommended_action_counts": recommended_action_counts,
            "config_gap_counts": config_gap_counts,
            "live_probe_blocker_counts": live_probe_blocker_counts,
            "compatibility_fixture_count": compatibility_fixture_count,
            "live_probe_example_count": live_probe_example_count,
            "ready_count": sum(1 for item in items if item.get("diagnostic", {}).get("status") == "ready-if-reachable"),
            "disabled_count": sum(1 for item in items if item.get("diagnostic", {}).get("status") == "disabled"),
            "misconfigured_count": sum(1 for item in items if item.get("diagnostic", {}).get("status") == "misconfigured"),
            "version_mismatch_count": sum(1 for item in items if item.get("diagnostic", {}).get("status") == "version-mismatch"),
            "live_probe_capable_count": sum(1 for item in items if item.get("diagnostic", {}).get("probe_mode") == "live-probe-capable"),
            "live_probe_active_count": sum(1 for item in items if item.get("diagnostic", {}).get("probe_mode") == "live-probe"),
            "simulated_probe_count": sum(1 for item in items if item.get("diagnostic", {}).get("probe_mode") == "simulated"),
            "provider_gated_count": sum(
                1 for item in items if item.get("diagnostic", {}).get("probe_execution_policy") == "optional-provider-gated"
            ),
            "blocked_probe_count": sum(1 for item in items if item.get("diagnostic", {}).get("probe_readiness_state") == "blocked"),
            "version_compatible_count": sum(1 for item in items if item.get("diagnostic", {}).get("version_compatible")),
            "feature_compatible_count": sum(
                1 for item in items if (item.get("capabilities", {}).get("feature_compatibility", {}) or {}).get("status") == "compatible"
            ),
            "feature_incompatible_count": sum(
                1 for item in items if (item.get("capabilities", {}).get("feature_compatibility", {}) or {}).get("status") != "compatible"
            ),
            "readiness_check_total": sum(item.get("diagnostic", {}).get("readiness_check_count", 0) for item in items),
            "readiness_check_pass_total": sum(item.get("diagnostic", {}).get("passed_check_count", 0) for item in items),
            "graceful_degradation": True,
            "providers": items,
        }

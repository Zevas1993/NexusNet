from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ACPProviderDiagnostics:
    def __init__(self, *, artifacts_dir: str | None = None):
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir else None

    def run(self, *, provider: dict[str, Any]) -> dict[str, Any]:
        provider_id = str(provider.get("provider_id") or "unknown-provider")
        endpoint = provider.get("endpoint")
        enabled = bool(provider.get("enabled", False))
        available = bool(enabled and endpoint)
        auth_ready = bool(endpoint)
        protocol_version = str(provider.get("protocol_version") or "1.0")
        minimum_protocol_version = str(provider.get("minimum_protocol_version") or "1.0")
        version_compatible = protocol_version >= minimum_protocol_version
        feature_flags = list(provider.get("feature_flags") or [])
        last_probe_status = provider.get("last_probe_status")
        timeout_pattern = "not-configured"
        failure_pattern = "graceful-absence"
        config_gaps: list[str] = []
        remediation_actions: list[str] = []
        probe_mode = "simulated"
        probe_status = "not-attempted"
        probe_contract_id = f"{provider_id}-bounded-live-probe"
        probe_execution_policy = "optional-provider-gated"
        live_probe_blockers: list[str] = []
        bounded_probe_budget = {
            "max_attempts": 1,
            "timeout_ms": int(provider.get("probe_timeout_ms") or 5000),
            "write_scope": "read-only-diagnostics",
        }
        readiness_checks = [
            {
                "check_id": "provider-enabled",
                "passed": enabled,
                "detail": "Provider must be enabled before ACP routing is considered.",
            },
            {
                "check_id": "endpoint-configured",
                "passed": bool(endpoint),
                "detail": "Providers need a bounded endpoint before live ACP probes are valid.",
            },
            {
                "check_id": "auth-config-ready",
                "passed": auth_ready,
                "detail": "Auth and config posture must be present before ACP promotion.",
            },
            {
                "check_id": "protocol-version-compatible",
                "passed": version_compatible,
                "detail": "Protocol and minimum protocol versions must align.",
            },
            {
                "check_id": "feature-flags-declared",
                "passed": bool(feature_flags),
                "detail": "Feature flags are required for capability compatibility reporting.",
            },
        ]
        if available:
            timeout_pattern = "provider-gated-timeout"
            failure_pattern = "probe-required"
            remediation_actions.append("run-bounded-live-probe")
            probe_mode = "live-probe-capable"
            probe_status = "probe-required"
        elif enabled and not endpoint:
            timeout_pattern = "configuration-missing"
            failure_pattern = "missing-endpoint"
            config_gaps.append("endpoint-missing")
            remediation_actions.append("configure-endpoint")
            probe_status = "blocked-misconfiguration"
            live_probe_blockers.append("endpoint-missing")
        elif not enabled:
            config_gaps.append("provider-disabled")
            remediation_actions.append("enable-provider-if-needed")
            probe_status = "simulated-disabled"
            live_probe_blockers.append("provider-disabled")
        if not version_compatible:
            config_gaps.append("protocol-version-mismatch")
            remediation_actions.append("align-protocol-version")
            if probe_mode == "live-probe-capable":
                probe_status = "blocked-version-mismatch"
            live_probe_blockers.append("protocol-version-mismatch")
        if not feature_flags:
            config_gaps.append("feature-flags-unspecified")
            remediation_actions.append("declare-feature-flags")
            live_probe_blockers.append("feature-flags-unspecified")
        if last_probe_status:
            probe_mode = "live-probe"
            probe_status = str(last_probe_status)
            failure_pattern = str(provider.get("last_probe_failure_pattern") or ("probe-failed" if last_probe_status != "passed" else "probe-passed"))
            timeout_pattern = str(provider.get("last_probe_timeout_pattern") or timeout_pattern)
            live_probe_blockers = []
        if available and version_compatible:
            status = "ready-if-reachable"
            readiness_summary = "Provider is configured well enough for a bounded live ACP probe."
            recommended_action = "Probe connectivity and auth on a supported ACP-capable lane before promotion."
        elif enabled and not version_compatible:
            status = "version-mismatch"
            readiness_summary = "Provider is enabled but protocol compatibility blocks bounded use."
            recommended_action = "Align protocol version or lower the provider minimum before enabling the lane."
        elif enabled:
            status = "misconfigured"
            readiness_summary = "Provider is enabled but missing enough configuration for bounded execution."
            recommended_action = "Complete endpoint or auth configuration before attempting ACP bridge use."
        else:
            status = "disabled"
            readiness_summary = "Provider is optional and currently disabled; graceful degradation remains active."
            recommended_action = "No action required unless an ACP lane is intentionally being brought online."
        if probe_mode == "live-probe":
            probe_readiness_state = "active"
        elif available and version_compatible:
            probe_readiness_state = "ready"
        elif enabled:
            probe_readiness_state = "blocked"
        else:
            probe_readiness_state = "simulated"
        return {
            "provider_id": provider_id,
            "available": available,
            "auth_config_ready": auth_ready,
            "endpoint_configured": bool(endpoint),
            "protocol_version": protocol_version,
            "minimum_protocol_version": minimum_protocol_version,
            "version_compatible": version_compatible,
            "feature_flag_count": len(feature_flags),
            "timeout_pattern": timeout_pattern,
            "failure_pattern": failure_pattern,
            "config_gaps": config_gaps,
            "remediation_actions": remediation_actions,
            "readiness_checks": readiness_checks,
            "readiness_check_count": len(readiness_checks),
            "passed_check_count": sum(1 for item in readiness_checks if item.get("passed")),
            "readiness_summary": readiness_summary,
            "recommended_action": recommended_action,
            "supports_live_probe": available and version_compatible,
            "probe_mode": probe_mode,
            "probe_status": probe_status,
            "probe_readiness_state": probe_readiness_state,
            "probe_contract_id": probe_contract_id,
            "probe_execution_policy": probe_execution_policy,
            "live_probe_candidate": bool(enabled and endpoint),
            "live_probe_blockers": sorted(set(live_probe_blockers)),
            "bounded_probe_budget": bounded_probe_budget,
            "bounded_probe_summary": (
                f"{probe_execution_policy} / {bounded_probe_budget['max_attempts']} attempt / {bounded_probe_budget['timeout_ms']}ms timeout"
            ),
            "probe_result_status": probe_status if probe_mode == "live-probe" else None,
            "status": status,
        }

    def write_compare_report(self, *, left: dict[str, Any], right: dict[str, Any], diff: dict[str, Any]) -> dict[str, Any] | None:
        if self.artifacts_dir is None:
            return None
        report_id = f"acpcompare_{_slug(left.get('provider_id'))}_{_slug(right.get('provider_id'))}"
        report_dir = self.artifacts_dir / "acp" / "compare_reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        payload_path = report_dir / f"{report_id}.json"
        markdown_path = report_dir / f"{report_id}.md"
        human_summary = (
            f"ACP compare `{left.get('provider_id')}` vs `{right.get('provider_id')}` "
            f"tracks `{left.get('probe_mode')}` -> `{right.get('probe_mode')}` and "
            f"{len(diff.get('remediation_actions_added', [])) + len(diff.get('remediation_actions_removed', []))} remediation deltas."
        )
        payload = {
            "report_id": report_id,
            "left": left,
            "right": right,
            "diff": diff,
            "human_summary": human_summary,
        }
        markdown = "\n".join(
            [
                f"# ACP Compare Report {report_id}",
                "",
                "## Probe State",
                f"- Left provider: `{left.get('provider_id')}`",
                f"- Right provider: `{right.get('provider_id')}`",
                f"- Probe mode: `{left.get('probe_mode')}` -> `{right.get('probe_mode')}`",
                f"- Probe status: `{left.get('probe_status')}` -> `{right.get('probe_status')}`",
                f"- Probe readiness state: `{left.get('probe_readiness_state')}` -> `{right.get('probe_readiness_state')}`",
                f"- Probe execution policy: `{left.get('probe_execution_policy')}` -> `{right.get('probe_execution_policy')}`",
                "",
                "## Provider Gate",
                f"- Left bounded probe budget: `{left.get('bounded_probe_budget', {})}`",
                f"- Right bounded probe budget: `{right.get('bounded_probe_budget', {})}`",
                f"- Left blockers: {', '.join(left.get('live_probe_blockers', [])) or 'none'}",
                f"- Right blockers: {', '.join(right.get('live_probe_blockers', [])) or 'none'}",
                "",
                "## Compatibility Delta",
                f"- Version compatible: `{left.get('version_compatible')}` -> `{right.get('version_compatible')}`",
                f"- Feature compatibility: `{left.get('feature_compatibility_status')}` -> `{right.get('feature_compatibility_status')}`",
                f"- Bundle families added: {', '.join(diff.get('bundle_families_added', [])) or 'none'}",
                f"- Bundle families removed: {', '.join(diff.get('bundle_families_removed', [])) or 'none'}",
                "",
                "## Remediation And Blockers",
                f"- Remediation actions added: {', '.join(diff.get('remediation_actions_added', [])) or 'none'}",
                f"- Remediation actions removed: {', '.join(diff.get('remediation_actions_removed', [])) or 'none'}",
                f"- Live probe blockers added: {', '.join(diff.get('live_probe_blockers_added', [])) or 'none'}",
                f"- Live probe blockers removed: {', '.join(diff.get('live_probe_blockers_removed', [])) or 'none'}",
                f"- Config gaps added: {', '.join(diff.get('config_gaps_added', [])) or 'none'}",
                f"- Config gaps removed: {', '.join(diff.get('config_gaps_removed', [])) or 'none'}",
                "",
                "## Human Summary",
                human_summary,
            ]
        )
        payload_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        markdown_path.write_text(markdown, encoding="utf-8")
        return {
            "report_id": report_id,
            "human_summary": human_summary,
            "payload_path": str(payload_path),
            "markdown_path": str(markdown_path),
        }


def _slug(value: Any) -> str:
    return "".join(ch if str(ch).isalnum() else "_" for ch in str(value or "unknown")).strip("_").lower()

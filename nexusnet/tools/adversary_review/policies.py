from __future__ import annotations

from typing import Any


class AdversaryRiskPolicyEngine:
    FAMILY_PATTERNS = {
        "file-mutation-risk": {"filesystem.write", "filesystem.delete", "git.commit"},
        "shell-exec-risk": {"shell.exec", "powershell.exec", "cmd.exec"},
        "network-egress-risk": {"network.external", "http.post", "http.request"},
        "credential-secrets-risk": {"secrets.read", "credentials.read", "env.secret"},
        "provider-bridge-risk": {"provider.acp"},
    }
    HIGH_RISK_TOOLS = {
        tool
        for patterns in FAMILY_PATTERNS.values()
        for tool in patterns
    }

    def assess(
        self,
        *,
        requested_tools: list[str],
        fallback_reason: str | None = None,
        policy_path: list[dict[str, Any]] | None = None,
        multi_step: bool | None = None,
        approval_requested: bool | None = None,
        approval_required: bool | None = None,
        allowed_tools: list[str] | None = None,
        requested_extensions: list[str] | None = None,
        allowed_extensions: list[str] | None = None,
        trigger_source: str | None = None,
    ) -> dict[str, Any]:
        families: list[str] = []
        for family, patterns in self.FAMILY_PATTERNS.items():
            if any(tool in patterns for tool in requested_tools):
                families.append(family)
        if fallback_reason == "ambiguous-binding" or any(step.get("reason") == "ambiguous-precedence-match" for step in (policy_path or [])):
            families.append("ambiguous-tool-binding-risk")
        if multi_step is True or len(requested_tools) > 1:
            families.append("multi-step-escalation-risk")
        if approval_required and approval_requested is False:
            families.append("chained-approval-bypass-risk")
        allowed_tools = list(allowed_tools or [])
        requested_extensions = list(requested_extensions or [])
        allowed_extensions = list(allowed_extensions or [])
        extension_or_acp_confusion = (
            (
                any("acp" in extension for extension in requested_extensions)
                or any(tool == "provider.acp" for tool in requested_tools)
            )
            and (
                ((bool(requested_extensions) and not allowed_extensions))
                or any(ext not in allowed_extensions for ext in requested_extensions)
            )
        )
        if (
            (bool(requested_tools) and not allowed_tools)
            or any(tool not in allowed_tools for tool in requested_tools)
            or ((bool(requested_extensions) and not allowed_extensions))
            or any(ext not in allowed_extensions for ext in requested_extensions)
            or (trigger_source and trigger_source.startswith("subagent-plan") and allowed_tools and sorted(set(requested_tools)) != sorted(set(allowed_tools)))
        ):
            families.append("recipe-subagent-privilege-confusion-risk")
        if extension_or_acp_confusion:
            families.append("extension-acp-privilege-inheritance-confusion-risk")
        if requested_extensions and (
            any(tool in self.HIGH_RISK_TOOLS for tool in requested_tools)
            or any(tool not in allowed_tools for tool in requested_tools)
            or any(ext not in allowed_extensions for ext in requested_extensions)
        ):
            families.append("bundle-level-permission-escalation-attempt-risk")
        families = sorted(set(families))
        critical = {
            "credential-secrets-risk",
            "ambiguous-tool-binding-risk",
            "chained-approval-bypass-risk",
            "recipe-subagent-privilege-confusion-risk",
            "extension-acp-privilege-inheritance-confusion-risk",
            "bundle-level-permission-escalation-attempt-risk",
        }
        if any(family in critical for family in families):
            risk_level = "critical"
        elif families:
            risk_level = "high"
        else:
            risk_level = "medium"
        return {
            "risk_families": families,
            "risk_level": risk_level,
            "high_risk": bool(families),
            "policy_path_count": len(policy_path or []),
            "approval_required": approval_required,
            "approval_requested": approval_requested,
        }

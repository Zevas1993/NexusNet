from __future__ import annotations

from collections import defaultdict


class GatewayPolicyEngine:
    def evaluate(
        self,
        *,
        agent_id: str,
        workspace_id: str,
        requested_tools: list[str],
        visible_packages: list[dict],
        require_user_approval: bool = False,
    ) -> dict:
        tool_matches: dict[str, list[dict]] = defaultdict(list)
        for package in visible_packages:
            for tool_name in package.get("allowed_tools", []):
                tool_matches[tool_name].append(package)

        matched_packages = []
        ambiguous_tools = []
        denied_tools = []
        approval_modes = set()
        policy_path = []
        for tool_name in requested_tools:
            matches = sorted(tool_matches.get(tool_name, []), key=lambda item: (-item["precedence"], item["skill_id"]))
            if not matches:
                denied_tools.append(tool_name)
                policy_path.append({"tool": tool_name, "decision": "deny", "reason": "no-visible-skill-match"})
                continue
            if len(matches) > 1 and matches[0]["precedence"] == matches[1]["precedence"]:
                ambiguous_tools.append(tool_name)
                policy_path.append({"tool": tool_name, "decision": "deny", "reason": "ambiguous-precedence-match"})
                continue
            match = matches[0]
            matched_packages.append(match)
            approval_modes.add(match.get("approval_behavior", "allow"))
            policy_path.append(
                {
                    "tool": tool_name,
                    "decision": "match",
                    "skill_id": match["skill_id"],
                    "approval_behavior": match.get("approval_behavior", "allow"),
                    "precedence": match.get("precedence"),
                }
            )

        if ambiguous_tools:
            decision = "deny"
            rationale = "Deny-by-default on ambiguous execution binding."
            fallback_reason = "ambiguous-binding"
        elif denied_tools:
            decision = "deny"
            rationale = "Requested tool is outside the visible skill allowlist."
            fallback_reason = "tool-outside-allowlist"
        elif require_user_approval or "allow-if-approved" in approval_modes:
            decision = "allow-if-approved"
            rationale = "Execution is policy-eligible but requires explicit approval before live use."
            fallback_reason = "explicit-approval-required"
        elif "ask" in approval_modes:
            decision = "ask"
            rationale = "Execution falls back to ask because the matched skill package requires explicit operator confirmation."
            fallback_reason = "ask-fallback"
        else:
            decision = "allow"
            rationale = "Execution fits the visible skill packages and current allowlists."
            fallback_reason = None

        return {
            "agent_id": agent_id,
            "workspace_id": workspace_id,
            "decision": decision,
            "rationale": rationale,
            "requested_tools": requested_tools,
            "matched_skill_ids": sorted({package["skill_id"] for package in matched_packages}),
            "matched_packages": [
                {
                    "skill_id": package["skill_id"],
                    "precedence": package.get("precedence"),
                    "approval_behavior": package.get("approval_behavior"),
                    "workspace_allowlist": package.get("workspace_allowlist", []),
                }
                for package in matched_packages
            ],
            "ambiguous_tools": sorted(set(ambiguous_tools)),
            "denied_tools": sorted(set(denied_tools)),
            "deny_by_default_on_ambiguity": True,
            "policy_mode": "local-first-openclaw-patterns",
            "policy_path": policy_path,
            "fallback_reason": fallback_reason,
        }

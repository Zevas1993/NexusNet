from __future__ import annotations


class GatewayScenarioCatalog:
    def summary(self, *, recent_reviews: list[dict] | None = None) -> dict:
        recent_reviews = list(recent_reviews or [])
        covered = sorted({family for review in recent_reviews for family in review.get("risk_families", [])})
        return {
            "status_label": "EXPLORATORY / PROTOTYPE",
            "scenario_families": [
                "file-mutation-risk",
                "shell-exec-risk",
                "network-egress-risk",
                "credential-secrets-risk",
                "ambiguous-tool-binding-risk",
                "multi-step-escalation-risk",
                "chained-approval-bypass-risk",
                "recipe-subagent-privilege-confusion-risk",
                "extension-acp-privilege-inheritance-confusion-risk",
                "bundle-level-permission-escalation-attempt-risk",
            ],
            "covered_families": covered,
            "coverage_count": len(covered),
        }

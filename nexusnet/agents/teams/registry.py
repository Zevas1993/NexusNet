from __future__ import annotations


class AgentTeamRegistry:
    def summary(self) -> dict:
        return {
            "status_label": "EXPLORATORY / PROTOTYPE",
            "team_patterns": [
                {"team_id": "research-scout-team", "roles": ["researcher", "analyst", "critique"]},
                {"team_id": "tool-builder-team", "roles": ["coder", "toolsmith", "builder"]},
            ],
        }

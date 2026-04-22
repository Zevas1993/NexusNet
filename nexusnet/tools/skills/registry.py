from __future__ import annotations

from copy import deepcopy


class SkillPackageRegistry:
    def __init__(self):
        self._packages = [
            {
                "skill_id": "filesystem-readonly",
                "label": "Filesystem Readonly",
                "status_label": "STRONG ACCEPTED DIRECTION",
                "source": "nexusnet-skill-package",
                "category": "ops",
                "tags": ["filesystem", "local-first", "readonly"],
                "precedence": 60,
                "visible_to_agents": ["openclaw-agent", "hermes-agent"],
                "workspace_allowlist": ["default", "*"],
                "allowed_tools": ["filesystem.readonly"],
                "approval_behavior": "allow",
            },
            {
                "skill_id": "retrieval-audit",
                "label": "Retrieval Audit",
                "status_label": "STRONG ACCEPTED DIRECTION",
                "source": "nexusnet-skill-package",
                "category": "research",
                "tags": ["retrieval", "audit", "graph"],
                "precedence": 80,
                "visible_to_agents": ["openclaw-agent", "standard-wrapper-agent"],
                "workspace_allowlist": ["default", "*"],
                "allowed_tools": ["retrieval.query", "governance.audit"],
                "approval_behavior": "allow",
            },
            {
                "skill_id": "policy-approval-gate",
                "label": "Policy Approval Gate",
                "status_label": "STRONG ACCEPTED DIRECTION",
                "source": "nexusnet-skill-package",
                "category": "governance",
                "tags": ["policy", "approvals", "safety"],
                "precedence": 90,
                "visible_to_agents": ["openclaw-agent"],
                "workspace_allowlist": ["default", "*"],
                "allowed_tools": ["governance.audit"],
                "approval_behavior": "allow-if-approved",
            },
            {
                "skill_id": "visual-grounding",
                "label": "Visual Grounding",
                "status_label": "EXPLORATORY / PROTOTYPE",
                "source": "nexusnet-skill-package",
                "category": "vision",
                "tags": ["vision", "grounding", "multimodal"],
                "precedence": 70,
                "visible_to_agents": ["openclaw-agent", "hermes-agent"],
                "workspace_allowlist": ["default", "*"],
                "allowed_tools": ["retrieval.query"],
                "approval_behavior": "ask",
            },
        ]

    def list_packages(self) -> list[dict]:
        return [deepcopy(item) for item in sorted(self._packages, key=lambda item: (-item["precedence"], item["skill_id"]))]

    def visible_packages(self, *, agent_id: str, workspace_id: str = "default") -> list[dict]:
        visible = []
        for package in self._packages:
            allowed_workspaces = package.get("workspace_allowlist", ["*"])
            if agent_id not in package.get("visible_to_agents", []) and "*" not in package.get("visible_to_agents", []):
                continue
            if workspace_id not in allowed_workspaces and "*" not in allowed_workspaces:
                continue
            visible.append(deepcopy(package))
        visible.sort(key=lambda item: (-item["precedence"], item["skill_id"]))
        return visible

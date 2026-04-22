from __future__ import annotations

from typing import Any


class SkillSyncPlanner:
    def __init__(self, *, skill_registry: Any, config: dict[str, Any] | None = None):
        self.skill_registry = skill_registry
        self.config = config or {}
        self._history: list[dict[str, Any]] = []

    def plan(self, *, source_id: str, category: str | None = None) -> dict[str, Any]:
        source = next(
            (item for item in (self.config.get("skills") or {}).get("import_sources", []) if item.get("source_id") == source_id),
            None,
        )
        packages = self.skill_registry.list_packages()
        selected = [
            package
            for package in packages
            if category is None or package.get("category") == category or category in package.get("tags", [])
        ]
        plan = {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "source": source,
            "category": category,
            "package_count": len(selected),
            "selected_skill_ids": [item["skill_id"] for item in selected],
            "read_only": True,
            "allowlist_required": True,
        }
        self._history.insert(0, plan)
        self._history = self._history[:25]
        return plan

    def history(self) -> list[dict[str, Any]]:
        return self._history[:10]

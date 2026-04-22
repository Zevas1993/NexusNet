from __future__ import annotations

from pathlib import Path
from typing import Any

from nexusnet.recipes.history import RecipeHistoryService


class RunbookHistoryService:
    def __init__(self, *, recipe_history: RecipeHistoryService, recipe_catalog: Any, artifacts_dir: Path):
        self.recipe_history = recipe_history
        self.recipe_catalog = recipe_catalog
        self.artifacts_dir = Path(artifacts_dir)

    def execute(self, **kwargs) -> dict[str, Any]:
        return self.recipe_history.execute(**kwargs)

    def summary(
        self,
        *,
        recipe_id: str | None = None,
        schedule_id: str | None = None,
        trigger_source: str | None = None,
        status: str | None = None,
        limit: int = 12,
    ) -> dict[str, Any]:
        return self.recipe_history.summary(
            execution_kind="runbook",
            recipe_id=recipe_id,
            schedule_id=schedule_id,
            trigger_source=trigger_source,
            status=status,
            limit=limit,
        )

    def detail(self, execution_id: str) -> dict[str, Any] | None:
        detail = self.recipe_history.detail(execution_id)
        if detail and detail.get("item", {}).get("execution_kind") != "runbook":
            return None
        return detail

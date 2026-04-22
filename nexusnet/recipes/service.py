from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .schema import RecipeDefinition


class RecipeCatalogService:
    def __init__(self, *, config_dir: Path, runtime_configs: dict[str, Any]):
        repo_root = Path(__file__).resolve().parents[2]
        self.config = runtime_configs.get("goose_lane") or {}
        loader = (self.config.get("recipes") or {}).get("loader") or {}
        configured_roots = loader.get("roots") or ["nexusnet/aos/recipes", "nexusnet/runbooks"]
        self.recipe_roots = [repo_root / root for root in configured_roots]
        self.workspace_recipe_root = config_dir / "recipes"

    def summary(self) -> dict[str, Any]:
        items = self.list_items()
        recipes = [item for item in items if item.kind == "recipe"]
        runbooks = [item for item in items if item.kind == "runbook"]
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "schema_kind": "portable-yaml-recipes",
            "recipe_count": len(recipes),
            "runbook_count": len(runbooks),
            "parameterized_count": sum(1 for item in items if item.parameterized),
            "schedule_compatible_ids": [item.recipe_id for item in items if item.schedule_compatible],
            "items": [self._serialize(item) for item in items],
            "validation": self.validation_summary(items),
        }

    def list_items(self) -> list[RecipeDefinition]:
        items: list[RecipeDefinition] = []
        for root in [*self.recipe_roots, self.workspace_recipe_root]:
            if not root.exists():
                continue
            for path in sorted(root.glob("*.yaml")):
                payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
                if not isinstance(payload, dict):
                    continue
                kind = payload.get("kind")
                if kind not in {"recipe", "runbook"}:
                    payload["kind"] = "runbook" if "runbook" in path.stem else "recipe"
                items.append(RecipeDefinition.from_payload(payload, source_path=path))
        items.sort(key=lambda item: (item.kind, item.recipe_id))
        return items

    def get(self, recipe_id: str) -> dict[str, Any] | None:
        for item in self.list_items():
            if item.recipe_id == recipe_id:
                return self._serialize(item)
        return None

    def validation_summary(self, items: list[RecipeDefinition] | None = None) -> dict[str, Any]:
        items = items or self.list_items()
        errors: list[dict[str, Any]] = []
        seen: set[str] = set()
        for item in items:
            if item.recipe_id in seen:
                errors.append({"recipe_id": item.recipe_id, "reason": "duplicate-recipe-id"})
            seen.add(item.recipe_id)
            if not item.ao_targets:
                errors.append({"recipe_id": item.recipe_id, "reason": "missing-ao-target"})
            if not item.steps:
                errors.append({"recipe_id": item.recipe_id, "reason": "missing-steps"})
        return {
            "ok": not errors,
            "item_count": len(items),
            "error_count": len(errors),
            "errors": errors,
        }

    def _serialize(self, item: RecipeDefinition) -> dict[str, Any]:
        payload = item.model_dump(mode="json")
        payload["schedule_compatible"] = item.schedule_compatible
        payload["parameterized"] = item.parameterized
        return payload

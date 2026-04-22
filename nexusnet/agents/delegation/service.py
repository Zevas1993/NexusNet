from __future__ import annotations

from typing import Any


class DelegationPlanner:
    def __init__(self, *, recipe_service: Any, extension_catalog: Any):
        self.recipe_service = recipe_service
        self.extension_catalog = extension_catalog

    def summary(self) -> dict[str, Any]:
        recipe_summary = self.recipe_service.summary()
        first_recipe = ((recipe_summary.get("items") or [{}])[0]) or {}
        example = self.plan(recipe_id=first_recipe.get("recipe_id", ""), parent_task="goose-pattern-example") if first_recipe else None
        return {
            "status_label": "EXPLORATORY / PROTOTYPE",
            "recipe_count": recipe_summary.get("recipe_count", 0),
            "schedule_compatible_ids": recipe_summary.get("schedule_compatible_ids", []),
            "example_plan": example,
        }

    def plan(self, *, recipe_id: str, parent_task: str) -> dict[str, Any]:
        recipe = self.recipe_service.get(recipe_id)
        if recipe is None:
            return {
                "status_label": "UNRESOLVED CONFLICT",
                "recipe_id": recipe_id,
                "parent_task": parent_task,
                "workers": [],
                "error": "recipe-not-found",
            }
        enabled_extensions = [
            item
            for item in self.extension_catalog.summary().get("extensions", [])
            if item.get("enabled_state") == "enabled"
        ][:2]
        requested_extension_ids = [item.get("bundle_id") for item in enabled_extensions if item.get("bundle_id")]
        requested_policy_set_ids = sorted({item.get("policy_set_id") for item in enabled_extensions if item.get("policy_set_id")})
        requested_bundle_families = sorted({item.get("bundle_family") for item in enabled_extensions if item.get("bundle_family")})
        worker_specs = []
        for index, step in enumerate(recipe.get("steps", [])):
            if step.get("action") not in {"subagent", "ao-dispatch", "skill-bundle", "tool-bundle"}:
                continue
            worker_specs.append(
                {
                    "subagent_id": f"{recipe_id}-worker-{index + 1}",
                    "task": step.get("description"),
                    "requested_tools": step.get("approved_tools", []),
                    "requested_extensions": requested_extension_ids,
                    "requested_policy_set_ids": requested_policy_set_ids,
                    "requested_bundle_families": requested_bundle_families,
                    "result_summary": step.get("action"),
                }
            )
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "recipe_id": recipe_id,
            "parent_task": parent_task,
            "worker_count": len(worker_specs),
            "workers": worker_specs,
        }

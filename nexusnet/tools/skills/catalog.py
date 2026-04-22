from __future__ import annotations

from collections import Counter
from typing import Any

from .benchmark import SkillBenchmarkService
from .sync import SkillSyncPlanner


class SkillCatalogService:
    def __init__(
        self,
        *,
        skill_registry: Any,
        store: Any | None = None,
        config: dict[str, Any] | None = None,
        extension_catalog: Any | None = None,
    ):
        self.skill_registry = skill_registry
        self.store = store
        self.config = config or {}
        self.extension_catalog = extension_catalog
        self.sync_planner = SkillSyncPlanner(skill_registry=skill_registry, config=self.config)
        self.benchmarks = SkillBenchmarkService(skill_registry=skill_registry)

    def summary(self) -> dict[str, Any]:
        packages = self.skill_registry.list_packages()
        traces = self.store.list_traces(limit=80) if self.store is not None else []
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "package_count": len(packages),
            "category_counts": self._category_counts(packages),
            "packages": packages,
            "import_sources": list((self.config.get("skills") or {}).get("import_sources", [])),
            "sync_history": self.sync_planner.history(),
            "benchmark_summary": self.benchmark_from_traces(traces),
            "optimization_summary": self.optimize_from_traces(traces),
            "extension_catalog": self.extension_catalog.summary() if self.extension_catalog is not None else None,
        }

    def sync_plan(self, *, source_id: str, category: str | None = None) -> dict[str, Any]:
        return self.sync_planner.plan(source_id=source_id, category=category)

    def benchmark_from_traces(self, traces: list[dict[str, Any]]) -> dict[str, Any]:
        return self.benchmarks.benchmark_from_traces(traces)

    def optimize_from_traces(self, traces: list[dict[str, Any]]) -> dict[str, Any]:
        return self.benchmarks.optimize_from_traces(traces)

    def _category_counts(self, packages: list[dict[str, Any]]) -> dict[str, int]:
        counts = Counter(item.get("category", "uncategorized") for item in packages)
        return dict(sorted(counts.items()))

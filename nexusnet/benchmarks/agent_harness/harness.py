from __future__ import annotations

from typing import Any


class AgentHarnessBenchmarkCatalog:
    def summary(self) -> dict[str, Any]:
        tasks = [
            {
                "task_id": "dynamic-tool-search",
                "goal": "Locate, rank, and apply tools without assuming a fixed tool path.",
            },
            {
                "task_id": "memory-scaffold-self-repair",
                "goal": "Use memory and failure traces to repair a scaffold over multiple rounds.",
            },
            {
                "task_id": "agent-team-coordination",
                "goal": "Maintain stable role identity and cross-agent task delegation.",
            },
            {
                "task_id": "benchmark-driven-skill-building",
                "goal": "Derive reusable skill patterns from repeated benchmark trajectories.",
            },
        ]
        return {
            "status_label": "EXPLORATORY / PROTOTYPE",
            "teacher_reference": "minimax-m27-reference",
            "teacher_role": "benchmark-teacher",
            "tasks": tasks,
            "scenario_families": [item["task_id"] for item in tasks],
            "source_status": "primary-backed-reference-lane",
            "default_runtime": False,
        }

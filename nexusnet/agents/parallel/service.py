from __future__ import annotations


class ParallelExecutionAdvisor:
    def __init__(self, *, max_parallel: int):
        self.max_parallel = max_parallel

    def summary(self) -> dict:
        return {
            "status_label": "EXPLORATORY / PROTOTYPE",
            "max_parallel": self.max_parallel,
            "supported_modes": ["sequential", "parallel"],
            "restricted_inheritance": True,
        }

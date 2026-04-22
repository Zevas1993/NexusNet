from __future__ import annotations

from typing import Any


def load_triattention_thresholds() -> dict[str, Any]:
    return {
        "threshold_set_id": "triattention-v2026-r1",
        "max_avg_kv_memory_ratio": 0.8,
        "min_avg_throughput_ratio": 0.82,
        "max_avg_latency_ratio": 1.08,
        "min_avg_stability_delta": -0.06,
        "min_avg_reasoning_delta": -0.08,
        "max_avg_regression_delta": 0.03,
    }

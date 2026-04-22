from __future__ import annotations

from typing import Any


class TriAttentionProviderCard:
    def summary(self, *, enabled: bool = False) -> dict:
        return {
            "provider_name": "triattention",
            "status_label": "EXPLORATORY / PROTOTYPE",
            "enabled": enabled,
            "default_on": False,
            "research_only": True,
            "focus": ["kv compression", "long-context efficiency", "key-importance estimation"],
        }

    def estimate(self, *, context_tokens: int) -> dict[str, Any]:
        scale = max(context_tokens, 1024) / 1024.0
        return {
            "context_tokens": context_tokens,
            "kv_memory_mb": round(180.0 * scale * 0.62, 3),
            "throughput_tokens_per_s": round(max(8.0, 96.0 / scale), 3),
            "latency_ms": round(19.0 + scale * 5.1, 3),
            "stability_score": round(max(0.55, 0.94 - (scale * 0.018)), 3),
            "reasoning_quality": round(max(0.58, 0.91 - (scale * 0.012)), 3),
            "long_context_regression": round(min(0.28, scale * 0.012), 3),
        }

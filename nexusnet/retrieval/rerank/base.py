from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from nexus.schemas import RetrievalHit


@dataclass
class StageTwoRerankResult:
    provider_name: str
    applied: bool
    top_k_before: int
    top_k_after: int
    latency_ms: int
    hits: list[RetrievalHit] = field(default_factory=list)
    rerank_scores: dict[str, float] = field(default_factory=dict)
    diagnostics: dict[str, Any] = field(default_factory=dict)

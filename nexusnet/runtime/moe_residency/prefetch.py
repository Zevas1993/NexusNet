from __future__ import annotations

from collections import Counter, defaultdict


class RouteTransitionPrefetcher:
    """Learns route transitions without participating in route selection."""

    def __init__(self, *, max_candidates: int = 2) -> None:
        if max_candidates <= 0:
            raise ValueError("max_candidates must be positive")
        self.max_candidates = max_candidates
        self._counts: dict[tuple[str, tuple[int, ...], str], Counter[int]] = defaultdict(Counter)

    def observe(
        self,
        source_layer_id: str,
        selected_experts: tuple[int, ...],
        target_layer_id: str,
        target_experts: tuple[int, ...],
    ) -> None:
        key = (source_layer_id, tuple(selected_experts), target_layer_id)
        self._counts[key].update(target_experts)

    def candidates(
        self,
        source_layer_id: str,
        selected_experts: tuple[int, ...],
        target_layer_id: str,
    ) -> tuple[int, ...]:
        key = (source_layer_id, tuple(selected_experts), target_layer_id)
        ranked = sorted(
            self._counts.get(key, {}).items(),
            key=lambda item: (-item[1], item[0]),
        )
        return tuple(expert_id for expert_id, _ in ranked[: self.max_candidates])

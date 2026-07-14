from __future__ import annotations

from .schemas import PlanEvidence, SLOProfile


class ParetoController:
    def frontier(self, evidence: list[PlanEvidence]) -> list[PlanEvidence]:
        eligible = [
            item
            for item in evidence
            if item.status == "completed" and item.repeat_count >= 3 and item.quality_equivalent and item.stable
        ]
        return sorted(
            [item for item in eligible if not any(self._dominates(other, item) for other in eligible if other != item)],
            key=lambda item: item.plan.plan_id,
        )

    def select(self, frontier: list[PlanEvidence], slo: SLOProfile) -> PlanEvidence:
        constrained = [item for item in frontier if self._satisfies(item, slo)]
        candidates = constrained or frontier
        if not candidates:
            raise ValueError("no verified Pareto candidate")
        if slo.objective == "latency":
            return min(candidates, key=lambda item: (item.warm_latency_ms or float("inf"), item.uncertainty))
        if slo.objective == "throughput":
            return max(candidates, key=lambda item: (item.throughput_tokens_s, -item.uncertainty))
        if slo.objective == "memory":
            return min(candidates, key=lambda item: (item.peak_vram_bytes + item.peak_ram_bytes, item.warm_latency_ms or float("inf")))
        return min(
            candidates,
            key=lambda item: (
                (item.warm_latency_ms or float("inf")) * (1 + item.uncertainty),
                item.peak_vram_bytes + item.peak_ram_bytes,
            ),
        )

    @staticmethod
    def _dominates(left: PlanEvidence, right: PlanEvidence) -> bool:
        left_values = (left.warm_latency_ms or float("inf"), -left.throughput_tokens_s, left.peak_ram_bytes, left.peak_vram_bytes, left.bytes_moved, left.uncertainty)
        right_values = (right.warm_latency_ms or float("inf"), -right.throughput_tokens_s, right.peak_ram_bytes, right.peak_vram_bytes, right.bytes_moved, right.uncertainty)
        return all(a <= b for a, b in zip(left_values, right_values)) and any(a < b for a, b in zip(left_values, right_values))

    @staticmethod
    def _satisfies(item: PlanEvidence, slo: SLOProfile) -> bool:
        return not (
            (slo.max_latency_ms is not None and (item.warm_latency_ms is None or item.warm_latency_ms > slo.max_latency_ms))
            or (slo.min_throughput_tokens_s is not None and item.throughput_tokens_s < slo.min_throughput_tokens_s)
            or (slo.max_peak_ram_bytes is not None and item.peak_ram_bytes > slo.max_peak_ram_bytes)
            or (slo.max_peak_vram_bytes is not None and item.peak_vram_bytes > slo.max_peak_vram_bytes)
            or (slo.require_quality_equivalence and not item.quality_equivalent)
        )

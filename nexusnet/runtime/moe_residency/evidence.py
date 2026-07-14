from __future__ import annotations

import re
from dataclasses import dataclass, field
from numbers import Real
from typing import Mapping


_METRIC_KEYS = {
    "storage_misses",
    "ram_hits",
    "hot_hits",
    "ram_evictions",
    "hot_evictions",
    "bytes_read",
    "ram_occupancy",
    "hot_occupancy",
    "prefetch_requests",
    "prefetch_hits",
    "prefetch_failures",
    "prefetch_cancellations",
    "prefetch_coalesced",
    "prefetch_wasted",
    "active_leases",
    "inflight_prefetches",
}
_REASON_CODE = re.compile(r"^[a-z0-9][a-z0-9_:-]{0,79}$")
_REF_CODE = re.compile(r"^[a-z0-9][a-z0-9_.:/-]{0,255}$")


@dataclass
class ExpertResidencyEvidence:
    plan_ref: str
    manifest_ref: str
    tier_metrics: dict[str, int | float] = field(default_factory=dict)
    fallback_events: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not _REF_CODE.fullmatch(self.plan_ref) or not _REF_CODE.fullmatch(self.manifest_ref):
            raise ValueError("plan_ref and manifest_ref must be sanitized references")

    def record_store_metrics(self, metrics: Mapping[str, object]) -> None:
        for key, value in metrics.items():
            if key not in _METRIC_KEYS:
                continue
            if isinstance(value, bool) or not isinstance(value, Real):
                raise TypeError(f"metric {key} must be numeric")
            self.tier_metrics[key] = value

    def record_fallback(self, reason_code: str) -> None:
        if not _REASON_CODE.fullmatch(reason_code):
            raise ValueError("fallback reason must be a sanitized reason code")
        self.fallback_events.append(reason_code)

    def snapshot(self) -> dict[str, object]:
        runtime_state = "tiered-warming"
        if self.fallback_events:
            runtime_state = "tiered-degraded"
        elif self.tier_metrics.get("hot_hits", 0) or self.tier_metrics.get("ram_hits", 0):
            runtime_state = "tiered-warm"
        elif self.tier_metrics.get("storage_misses", 0):
            runtime_state = "tiered-cold"
        return {
            "schema_version": "expert_residency_evidence.v0.1",
            "authority": "NexusBrain",
            "plan_ref": self.plan_ref,
            "manifest_ref": self.manifest_ref,
            "runtime_state": runtime_state,
            "tier_metrics": dict(sorted(self.tier_metrics.items())),
            "fallback_events": list(self.fallback_events),
            "privacy_boundary": "numeric-runtime-metrics-and-sanitized-reason-codes-only",
        }

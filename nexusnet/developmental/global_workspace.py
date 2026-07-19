from __future__ import annotations

import hashlib
import json
from typing import Any


class GlobalWorkspaceRouter:
    """Evidence-gated ignition bottleneck for NexusBrain-wide broadcasts."""

    def __init__(self, *, capacity: int = 4, ignition_threshold: float = 0.6) -> None:
        if capacity < 1:
            raise ValueError("capacity must be positive")
        if not 0.0 <= ignition_threshold <= 1.0:
            raise ValueError("ignition_threshold must be between zero and one")
        self.capacity = capacity
        self.ignition_threshold = ignition_threshold
        self._broadcasts: list[dict[str, Any]] = []

    def ignite(self, *, workspace_id: str, candidates: list[dict[str, Any]]) -> dict[str, Any]:
        ranked: list[dict[str, Any]] = []
        for candidate in candidates:
            evidence_refs = sorted({str(ref) for ref in candidate.get("evidence_refs", []) if ref})
            if not evidence_refs:
                continue
            score = self._score(candidate)
            if score < self.ignition_threshold:
                continue
            ranked.append(
                {
                    "candidate_id": str(candidate["candidate_id"]),
                    "content_ref": str(candidate["content_ref"]),
                    "ignition_score": round(score, 6),
                    "evidence_refs": evidence_refs,
                    "signals": {
                        key: round(self._bounded(candidate.get(key)), 6)
                        for key in ("goal_relevance", "salience", "anomaly", "contradiction", "eval_failure")
                    },
                }
            )
        ranked.sort(key=lambda item: (-item["ignition_score"], item["candidate_id"]))
        broadcast = ranked[: self.capacity]
        digest = hashlib.sha256(
            json.dumps({"workspace_id": workspace_id, "broadcast": broadcast}, sort_keys=True).encode("utf-8")
        ).hexdigest()[:16]
        result = {
            "surface_id": "global-workspace-router",
            "workspace_id": workspace_id,
            "broadcast_id": f"broadcast:{digest}",
            "status": "broadcast" if broadcast else "no-ignition",
            "broadcast_count": len(broadcast),
            "broadcast": broadcast,
            "rejected_count": len(candidates) - len(broadcast),
            "production_mutation_allowed": False,
        }
        self._broadcasts.insert(0, result)
        self._broadcasts = self._broadcasts[:128]
        return dict(result)

    def summary(self) -> dict[str, Any]:
        return {
            "surface_id": "global-workspace-router",
            "runtime_state": "live-bound" if self._broadcasts else "ready",
            "broadcast_count": len(self._broadcasts),
            "latest_broadcast": dict(self._broadcasts[0]) if self._broadcasts else None,
            "capacity": self.capacity,
            "ignition_threshold": self.ignition_threshold,
        }

    @classmethod
    def _score(cls, candidate: dict[str, Any]) -> float:
        signals = [
            cls._bounded(candidate.get("goal_relevance")),
            cls._bounded(candidate.get("salience")),
            cls._bounded(candidate.get("anomaly")),
            cls._bounded(candidate.get("contradiction")),
            cls._bounded(candidate.get("eval_failure")),
        ]
        strongest = max(signals)
        supporting = sum(signals) / len(signals)
        return min(1.0, (0.7 * strongest) + (0.3 * supporting))

    @staticmethod
    def _bounded(value: Any) -> float:
        try:
            return max(0.0, min(1.0, float(value or 0.0)))
        except (TypeError, ValueError):
            return 0.0

from __future__ import annotations

from pathlib import Path
from typing import Any

from .kernel import DevelopmentalCortexKernel


class DevelopmentalCortexService:
    """Live operator surface over the developmental cortex spine.

    Aggregates the read-only summaries of every developmental sub-surface and records
    shadow-only assessment packets. This is a non-mutating governance surface: it never
    promotes a candidate or allows production mutation.
    """

    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.kernel = DevelopmentalCortexKernel(artifacts_dir=artifacts_dir)
        self._assessments: list[dict[str, Any]] = []

    def assess(self, request: dict[str, Any]) -> dict[str, Any]:
        result = self.kernel.assess(
            request_id=str(request["request_id"]),
            task_ref=str(request["task_ref"]),
            trace_refs=list(request.get("trace_refs") or []),
            evidence_refs=list(request.get("evidence_refs") or []),
            runtime_state=dict(request.get("runtime_state") or {}),
            memory_state=dict(request.get("memory_state") or {}),
            authority_state=dict(request.get("authority_state") or {}),
            eval_state=dict(request.get("eval_state") or {}),
        )
        self._assessments.insert(0, result)
        return result

    def _subsurfaces(self) -> dict[str, Any]:
        return {
            "body_schema": self.kernel.body_schema.snapshot(),
            "global_workspace": self.kernel.global_workspace.summary(),
            "semantic_memory": self.kernel.semantic_memory.summary(),
            "reference_frames": self.kernel.reference_frames.summary(),
            "dreaming_simulator": self.kernel.simulator.summary(),
            "causal_lab": self.kernel.causal_lab.summary(),
            "growth_archive": self.kernel.growth_archive.summary(),
            "promotion_tribunal": {
                "surface_id": "promotion-tribunal",
                "authority": "NexusBrain",
                "decision_boundary": "active-promotion-requires-all-gates-and-operator-approval",
            },
        }

    def scorecard(self) -> dict[str, Any]:
        subsurfaces = self._subsurfaces()
        degraded = any(
            str(surface.get("runtime_state")) == "degraded" for surface in subsurfaces.values()
        )
        runtime_state = "degraded" if degraded else ("live-bound" if self._assessments else "static-canon")
        latest = self._assessments[0] if self._assessments else None
        return {
            "surface_id": "developmental-cortex-kernel",
            "authority": "NexusBrain",
            "runtime_state": runtime_state,
            "production_mutation_allowed": False,
            "assessment_count": len(self._assessments),
            "latest_assessment": latest,
            "subsurfaces": subsurfaces,
            "mutation_boundary": "developmental-cortex-is-shadow-only-evidence-gated-no-production-mutation",
            "operator_actions": {
                "inspect": {"method": "GET", "endpoint": "/ops/brain/canon/developmental-cortex"},
                "assess": {"method": "POST", "endpoint": "/ops/brain/developmental-cortex/assess"},
            },
        }

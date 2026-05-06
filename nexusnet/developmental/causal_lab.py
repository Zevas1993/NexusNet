from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .contracts import CausalInterventionRecord


class CausalInterventionLab:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.interventions_dir = self.artifacts_dir / "developmental" / "causal-lab" if self.artifacts_dir else None
        if self.interventions_dir is not None:
            self.interventions_dir.mkdir(parents=True, exist_ok=True)
        self._interventions: list[dict[str, Any]] = []

    def record_intervention(
        self,
        *,
        intervention_id: str,
        variable: str,
        control_value: str,
        treatment_value: str,
        observed_delta: dict[str, float],
        evidence_refs: list[str],
    ) -> dict[str, Any]:
        findings = []
        if not evidence_refs:
            findings.append("causal_intervention_requires_evidence_refs")
        record = CausalInterventionRecord(
            intervention_id=intervention_id,
            variable=variable,
            control_value=control_value,
            treatment_value=treatment_value,
            observed_delta=observed_delta,
            evidence_refs=evidence_refs,
            status="blocked" if findings else "recorded",
            causal_confidence=self._confidence(observed_delta, has_evidence=bool(evidence_refs)),
            findings=findings,
        ).model_dump(mode="json")
        self._persist(record)
        return record

    def summary(self) -> dict[str, Any]:
        return {
            "surface_id": "causal-intervention-lab",
            "authority": "NexusBrain",
            "runtime_state": "degraded"
            if any(intervention.get("status") == "blocked" for intervention in self._interventions)
            else ("live-bound" if self._interventions else "static-canon"),
            "intervention_count": len(self._interventions),
            "latest_intervention": self._interventions[0] if self._interventions else None,
            "boundary": "sandboxed-intervention-records-only-no-production-action",
        }

    def _persist(self, record: dict[str, Any]) -> None:
        if self.interventions_dir is None:
            self._interventions.insert(0, record)
            return
        path = self._artifact_path_for_intervention_id(record["intervention_id"])
        record["artifact_path"] = str(path)
        path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
        self._interventions.insert(0, record)

    def _artifact_path_for_intervention_id(self, intervention_id: str) -> Path:
        if self.interventions_dir is None:
            raise ValueError("interventions_dir is required for persisted causal interventions")
        digest = hashlib.sha256(intervention_id.encode("utf-8")).hexdigest()
        path = self.interventions_dir / f"{digest}.json"
        interventions_root = self.interventions_dir.resolve()
        resolved_path = path.resolve()
        if resolved_path.parent != interventions_root:
            raise ValueError("causal intervention artifact path escaped interventions directory")
        return path

    def _confidence(self, observed_delta: dict[str, float], *, has_evidence: bool) -> str:
        if not has_evidence:
            return "unknown"
        if any(abs(delta) >= 0.05 for delta in observed_delta.values()):
            return "confirmed"
        return "unknown"

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .contracts import CausalInterventionRecord


class CausalInterventionLab:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.root = Path(artifacts_dir) / "developmental" / "causal-lab" if artifacts_dir is not None else None
        if self.root is not None:
            self.root.mkdir(parents=True, exist_ok=True)
        self._records: list[dict[str, Any]] = []

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
        findings = [] if evidence_refs else ["causal_intervention_requires_evidence_refs"]
        confidence = "confirmed" if evidence_refs and any(abs(value) >= 0.05 for value in observed_delta.values()) else "unknown"
        record = CausalInterventionRecord(
            intervention_id=intervention_id,
            variable=variable,
            control_value=control_value,
            treatment_value=treatment_value,
            observed_delta=observed_delta,
            evidence_refs=evidence_refs,
            status="blocked" if findings else "recorded",
            causal_confidence=confidence,
            findings=findings,
        ).model_dump(mode="json")
        self._persist(record)
        return record

    def summary(self) -> dict[str, Any]:
        return {
            "surface_id": "causal-intervention-lab",
            "authority": "NexusBrain",
            "runtime_state": "degraded" if any(item.get("status") == "blocked" for item in self._records) else ("live-bound" if self._records else "static-canon"),
            "intervention_count": len(self._records),
            "latest_intervention": self._records[0] if self._records else None,
            "boundary": "sandboxed-intervention-records-only-no-production-action",
        }

    def _persist(self, record: dict[str, Any]) -> None:
        self._records.insert(0, record)
        if self.root is None:
            return
        path = self.root / f"{_safe_id(record['intervention_id'])}.json"
        record["artifact_path"] = str(path)
        path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")


def _safe_id(value: str) -> str:
    return value.replace(":", "_").replace("/", "_")[:160] or "intervention"

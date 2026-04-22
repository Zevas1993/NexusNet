from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import new_id, utcnow


class GuardrailAnalysisService:
    def __init__(self, *, artifacts_dir: Path):
        self.artifacts_dir = artifacts_dir
        self._recent: list[dict[str, Any]] = []

    def analyze(self, *, before: dict[str, Any] | None = None, after: dict[str, Any] | None = None, stress_tests: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        before = before or {"refusal_rate": 0.12, "stability": 0.94, "circuit_weight": 0.48}
        after = after or {"refusal_rate": 0.11, "stability": 0.91, "circuit_weight": 0.44}
        stress_tests = stress_tests or [{"test_id": "compensation-check", "passed": True, "delta": -0.01}]
        analysis_id = new_id("guardrailanalysis")
        rebound_detected = any(float(item.get("delta", 0.0)) > 0.03 for item in stress_tests)
        payload = {
            "status_label": "EXPLORATORY / PROTOTYPE",
            "analysis_id": analysis_id,
            "created_at": utcnow().isoformat(),
            "research_only": True,
            "quarantine_required": True,
            "promotion_default": "blocked",
            "mechanistic_findings": [
                {
                    "finding_id": "circuit-localization",
                    "summary": "Structured circuit-localization style comparison over bounded before/after artifacts.",
                    "before_circuit_weight": before.get("circuit_weight"),
                    "after_circuit_weight": after.get("circuit_weight"),
                },
                {
                    "finding_id": "compensation-rebound",
                    "summary": "Compensation and rebound signals remain review-only and non-deployable.",
                    "rebound_detected": rebound_detected,
                },
            ],
            "before": before,
            "after": after,
            "stress_tests": stress_tests,
            "robustness_summary": {
                "stability_delta": round(float(after.get("stability", 0.0)) - float(before.get("stability", 0.0)), 4),
                "refusal_rate_delta": round(float(after.get("refusal_rate", 0.0)) - float(before.get("refusal_rate", 0.0)), 4),
                "rebound_detected": rebound_detected,
            },
            "governance": {
                "requires_evalsao": True,
                "requires_safetyao": True,
                "requires_external_audit": True,
                "weight_surgery_allowed": False,
            },
        }
        artifact_path = self._write_artifact(analysis_id=analysis_id, payload=payload)
        payload["artifact_path"] = str(artifact_path)
        self._recent.insert(0, payload)
        self._recent = self._recent[:25]
        return payload

    def summary(self) -> dict[str, Any]:
        return {
            "status_label": "EXPLORATORY / PROTOTYPE",
            "research_only": True,
            "quarantine_required": True,
            "latest_analysis": self._recent[0] if self._recent else None,
            "analysis_count": len(self._recent),
        }

    def _write_artifact(self, *, analysis_id: str, payload: dict[str, Any]) -> Path:
        destination = self.artifacts_dir / "research" / "interpretability" / f"{analysis_id}.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return destination

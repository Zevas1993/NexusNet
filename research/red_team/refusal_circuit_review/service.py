from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import new_id, utcnow


class RefusalCircuitReviewService:
    def __init__(self, *, artifacts_dir: Path, guardrail_analysis: Any):
        self.artifacts_dir = artifacts_dir
        self.guardrail_analysis = guardrail_analysis
        self._recent: list[dict[str, Any]] = []

    def review(self, *, before: dict[str, Any] | None = None, after: dict[str, Any] | None = None) -> dict[str, Any]:
        analysis = self.guardrail_analysis.analyze(before=before, after=after)
        review_id = new_id("redteamreview")
        payload = {
            "status_label": "EXPLORATORY / PROTOTYPE",
            "review_id": review_id,
            "created_at": utcnow().isoformat(),
            "research_only": True,
            "quarantine_flag_required": True,
            "non_promotion_default": True,
            "mainline_model_editing_allowed": False,
            "guardrail_ablation_allowed": False,
            "analysis_ref": analysis["analysis_id"],
            "analysis_artifact_path": analysis["artifact_path"],
            "governance": {
                "requires_evalsao": True,
                "requires_safetyao": True,
                "requires_external_audit": True,
                "rollback_required": True,
            },
            "operator_summary": [
                "Quarantined interpretability/red-team lane only.",
                "No refusal-removal or liberation flows are enabled.",
                "Reports remain non-promotable by default and must preserve rollback lineage.",
            ],
        }
        artifact_path = self._write_artifact(review_id=review_id, payload=payload)
        payload["artifact_path"] = str(artifact_path)
        self._recent.insert(0, payload)
        self._recent = self._recent[:25]
        return payload

    def summary(self) -> dict[str, Any]:
        return {
            "status_label": "EXPLORATORY / PROTOTYPE",
            "research_only": True,
            "quarantine_required": True,
            "latest_review": self._recent[0] if self._recent else None,
            "review_count": len(self._recent),
        }

    def _write_artifact(self, *, review_id: str, payload: dict[str, Any]) -> Path:
        destination = self.artifacts_dir / "research" / "red-team" / f"{review_id}.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return destination

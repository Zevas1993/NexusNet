from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .contracts import GrowthArchiveCandidate


class GrowthArchive:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.root = Path(artifacts_dir) / "developmental" / "growth-archive" if artifacts_dir is not None else None
        if self.root is not None:
            self.root.mkdir(parents=True, exist_ok=True)
        self._records: list[dict[str, Any]] = []

    def record_candidate(
        self,
        *,
        candidate_id: str,
        candidate_type: str,
        diversity_key: str,
        scores: dict[str, float],
        evidence_refs: list[str],
    ) -> dict[str, Any]:
        findings = [] if evidence_refs else ["growth_candidate_requires_evidence_refs"]
        record = GrowthArchiveCandidate(
            candidate_id=candidate_id,
            candidate_type=candidate_type,
            diversity_key=diversity_key,
            scores=scores,
            evidence_refs=evidence_refs,
            promotion_state="blocked" if findings else "archived-shadow",
            findings=findings,
        ).model_dump(mode="json")
        self._persist(record)
        return record

    def summary(self) -> dict[str, Any]:
        return {
            "surface_id": "growth-archive",
            "authority": "NexusBrain",
            "runtime_state": "degraded" if any(item.get("promotion_state") == "blocked" for item in self._records) else ("live-bound" if self._records else "static-canon"),
            "candidate_count": len(self._records),
            "diversity_key_count": len({item.get("diversity_key") for item in self._records}),
            "latest_candidate": self._records[0] if self._records else None,
            "production_mutation_allowed": False,
        }

    def _persist(self, record: dict[str, Any]) -> None:
        self._records.insert(0, record)
        if self.root is None:
            return
        path = self.root / f"{record['candidate_id'].replace(':', '_').replace('/', '_')}.json"
        record["artifact_path"] = str(path)
        path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from nexus.schemas import utcnow
from pydantic import ValidationError

from .contracts import GrowthArchiveCandidate


class GrowthArchive:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.candidates_dir = self.artifacts_dir / "developmental" / "growth-archive" if self.artifacts_dir else None
        if self.candidates_dir is not None:
            self.candidates_dir.mkdir(parents=True, exist_ok=True)
        self._candidates: list[dict[str, Any]] = []

    def record_candidate(
        self,
        *,
        candidate_id: str,
        candidate_type: str,
        diversity_key: str,
        scores: dict[str, float],
        evidence_refs: list[str],
    ) -> dict[str, Any]:
        findings = []
        if not evidence_refs:
            findings.append("growth_candidate_requires_evidence_refs")
        record = GrowthArchiveCandidate(
            candidate_id=candidate_id,
            candidate_type=candidate_type,
            diversity_key=diversity_key,
            scores=scores,
            evidence_refs=evidence_refs,
            promotion_state="blocked" if findings else "archived-shadow",
            findings=findings,
            created_at=utcnow().isoformat(),
        ).model_dump(mode="json")
        self._persist(record)
        return record

    def summary(self) -> dict[str, Any]:
        candidates = self._list_candidates()
        return {
            "surface_id": "growth-archive",
            "authority": "NexusBrain",
            "runtime_state": "degraded"
            if any(candidate.get("promotion_state") == "blocked" for candidate in candidates)
            else ("live-bound" if candidates else "static-canon"),
            "candidate_count": len(candidates),
            "diversity_key_count": len({candidate.get("diversity_key") for candidate in candidates}),
            "latest_candidate": candidates[0] if candidates else None,
            "production_mutation_allowed": False,
        }

    def _persist(self, record: dict[str, Any]) -> None:
        if self.candidates_dir is None:
            self._candidates.insert(0, record)
            return
        path = self._artifact_path_for_candidate_id(record["candidate_id"])
        record["artifact_path"] = str(path)
        path.write_text(json.dumps(record, allow_nan=False, indent=2, sort_keys=True), encoding="utf-8")
        self._candidates.insert(0, record)

    def _artifact_path_for_candidate_id(self, candidate_id: str) -> Path:
        if self.candidates_dir is None:
            raise ValueError("candidates_dir is required for persisted growth candidates")
        digest = hashlib.sha256(candidate_id.encode("utf-8")).hexdigest()
        path = self.candidates_dir / f"{digest}.json"
        candidates_root = self.candidates_dir.resolve()
        resolved_path = path.resolve()
        if resolved_path.parent != candidates_root:
            raise ValueError("growth candidate artifact path escaped candidates directory")
        return path

    def _list_candidates(self) -> list[dict[str, Any]]:
        candidates_by_id: dict[str, dict[str, Any]] = {}
        if self.candidates_dir is not None:
            disk_candidates: dict[str, tuple[str, str, dict[str, Any]]] = {}
            for path in sorted(self.candidates_dir.glob("*.json"), key=lambda item: item.name):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                    if not isinstance(payload, dict):
                        continue
                    candidate = GrowthArchiveCandidate(**payload).model_dump(mode="json")
                except (OSError, json.JSONDecodeError, ValidationError):
                    continue
                candidate_id = candidate.get("candidate_id")
                candidate_key = (candidate.get("created_at") or "", path.name)
                if candidate_id not in disk_candidates or candidate_key > disk_candidates[candidate_id][:2]:
                    disk_candidates[candidate_id] = (*candidate_key, candidate)
            for candidate_id, (_, _, candidate) in disk_candidates.items():
                candidates_by_id[candidate_id] = candidate
        for candidate in reversed(self._candidates):
            candidate_id = candidate.get("candidate_id")
            if candidate_id:
                candidates_by_id[candidate_id] = candidate
        candidates = list(candidates_by_id.values())
        candidates.sort(key=lambda item: (item.get("created_at") or "", item.get("candidate_id") or ""), reverse=True)
        return candidates

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import utcnow

from .contracts import ReferenceFrameRecord


class ReferenceFrameStore:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.frames_dir = self.artifacts_dir / "developmental" / "reference-frames" if self.artifacts_dir else None
        if self.frames_dir is not None:
            self.frames_dir.mkdir(parents=True, exist_ok=True)
        self._frames: list[dict[str, Any]] = []

    def record(
        self,
        *,
        frame_id: str,
        frame_type: str,
        subject_ref: str,
        facts: list[dict[str, str]],
        evidence_refs: list[str],
        uncertainty: float = 0.0,
    ) -> dict[str, Any]:
        findings = []
        if not evidence_refs:
            findings.append("reference_frame_requires_evidence_refs")
        if any("mutate production without review" in str(fact.get("claim", "")).lower() for fact in facts):
            findings.append("reference_frame_blocks_unreviewed_mutation_claim")
        record = ReferenceFrameRecord(
            frame_id=frame_id,
            frame_type=frame_type,
            subject_ref=subject_ref,
            facts=facts,
            evidence_refs=evidence_refs,
            uncertainty=uncertainty,
            findings=findings,
            runtime_state="degraded" if findings else "live-bound",
            mutation_allowed=False,
        ).model_dump(mode="json")
        record["created_at"] = utcnow().isoformat()
        self._persist(record)
        return record

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        frames = self._list_frames(limit=limit)
        return {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "reference-frame-store",
            "runtime_state": "degraded" if any(frame.get("findings") for frame in frames) else ("live-bound" if frames else "static-canon"),
            "frame_count": len(frames),
            "latest_frame": frames[0] if frames else None,
            "frames": frames,
            "mutation_boundary": "reference-frames-model-context-without-production-mutation",
        }

    def _persist(self, record: dict[str, Any]) -> None:
        self._frames.insert(0, record)
        if self.frames_dir is None:
            return
        safe = record["frame_id"].replace(":", "_").replace("/", "_")
        path = self.frames_dir / f"{safe}.json"
        record["artifact_path"] = str(path)
        path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")

    def _list_frames(self, *, limit: int) -> list[dict[str, Any]]:
        frames = list(self._frames)
        if self.frames_dir is not None:
            seen = {frame.get("frame_id") for frame in frames}
            for path in self.frames_dir.glob("*.json"):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if payload.get("frame_id") not in seen:
                    frames.append(payload)
        frames.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return frames[:limit]

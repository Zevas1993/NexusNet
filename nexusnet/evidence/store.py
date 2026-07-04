from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from nexus.schemas import utcnow

from .contracts import EvidenceRecord


class EvidenceStore:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.root = Path(artifacts_dir) / "evidence" / "records" if artifacts_dir is not None else None
        if self.root is not None:
            self.root.mkdir(parents=True, exist_ok=True)
        self._records: list[dict[str, Any]] = []

    def append(self, *, kind: str, subject_ref: str, payload: dict[str, Any], source_refs: list[str]) -> dict[str, Any]:
        previous_hash = self._records[0]["content_hash"] if self._records else ""
        base = {
            "record_id": f"evidence::{kind}::{len(self._records) + 1}",
            "kind": kind,
            "subject_ref": subject_ref,
            "payload": payload,
            "source_refs": source_refs,
            "previous_hash": previous_hash,
            "created_at": utcnow().isoformat(),
        }
        digest = hashlib.sha256(json.dumps(base, sort_keys=True).encode("utf-8")).hexdigest()
        model_fields = {key: value for key, value in base.items() if key != "created_at"}
        record = EvidenceRecord(**model_fields, content_hash=f"sha256:{digest}").model_dump(mode="json")
        record["created_at"] = base["created_at"]
        self._records.insert(0, record)
        if self.root is not None:
            path = self.root / f"{digest[:16]}.json"
            record["artifact_path"] = str(path)
            path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
        return record

    def projection(self) -> dict[str, Any]:
        kind_counts: dict[str, int] = {}
        for record in self._records:
            kind = str(record.get("kind") or "unknown")
            kind_counts[kind] = kind_counts.get(kind, 0) + 1
        return {
            "surface_id": "content-addressed-evidence-store",
            "authority": "NexusBrain",
            "runtime_state": "live-bound" if self._records else "static-canon",
            "record_count": len(self._records),
            "kind_counts": kind_counts,
            "latest_hash": self._records[0]["content_hash"] if self._records else "",
        }

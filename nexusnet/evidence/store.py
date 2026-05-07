from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from .contracts import EvidenceRecord


class EvidenceStore:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.records_dir = self.artifacts_dir / "evidence" / "records" if self.artifacts_dir else None
        if self.records_dir is not None:
            self.records_dir.mkdir(parents=True, exist_ok=True)
        self._records: list[dict[str, Any]] = []

    def append(
        self,
        *,
        kind: str,
        subject_ref: str,
        payload: dict[str, Any],
        source_refs: list[str],
    ) -> dict[str, Any]:
        records = self._merged_records()
        base_record = {
            "record_id": f"evidence::{kind}::{len(records) + 1}",
            "kind": kind,
            "subject_ref": subject_ref,
            "payload": payload,
            "source_refs": source_refs,
            "previous_hash": records[-1]["content_hash"] if records else "",
        }
        canonical_base = self._canonical_json(base_record)
        digest = hashlib.sha256(canonical_base.encode("utf-8")).hexdigest()
        record = {
            **base_record,
            "content_hash": f"sha256:{digest}",
            "artifact_path": None,
        }
        record = EvidenceRecord(**record).model_dump(mode="json")
        self._persist(record, digest)
        return record

    def projection(self) -> dict[str, Any]:
        records = self._merged_records()
        kind_counts = dict(Counter(record["kind"] for record in records))
        return {
            "surface_id": "content-addressed-evidence-store",
            "authority": "NexusBrain",
            "runtime_state": "live-bound" if records else "static-canon",
            "record_count": len(records),
            "kind_counts": kind_counts,
            "latest_hash": records[-1]["content_hash"] if records else "",
        }

    def _persist(self, record: dict[str, Any], digest: str) -> None:
        if self.records_dir is None:
            self._records.append(record)
            return
        path = self._artifact_path_for_digest(digest)
        record["artifact_path"] = str(path)
        record = EvidenceRecord(**record).model_dump(mode="json")
        path.write_text(self._canonical_json(record), encoding="utf-8")
        self._records.append(record)

    def _artifact_path_for_digest(self, digest: str) -> Path:
        if self.records_dir is None:
            raise ValueError("records_dir is required for persisted evidence records")
        path = self.records_dir / f"{digest}.json"
        records_root = self.records_dir.resolve()
        resolved_path = path.resolve()
        if resolved_path.parent != records_root:
            raise ValueError("evidence artifact path escaped records directory")
        return path

    def _merged_records(self) -> list[dict[str, Any]]:
        records_by_key: dict[str, dict[str, Any]] = {}
        for record in self._records:
            valid_record = EvidenceRecord(**record).model_dump(mode="json")
            key = valid_record.get("content_hash") or valid_record["record_id"]
            records_by_key[key] = valid_record
        if self.records_dir is not None:
            for path in sorted(self.records_dir.glob("*.json"), key=lambda item: item.name):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                    if not isinstance(payload, dict):
                        continue
                    record = EvidenceRecord(**payload).model_dump(mode="json")
                except (OSError, json.JSONDecodeError, ValidationError):
                    continue
                key = record.get("content_hash") or record["record_id"]
                records_by_key.setdefault(key, record)
        return self._chain_ordered(list(records_by_key.values()))

    def _chain_ordered(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not records:
            return []
        by_previous: dict[str, list[dict[str, Any]]] = {}
        for record in records:
            by_previous.setdefault(record.get("previous_hash") or "", []).append(record)
        for chained in by_previous.values():
            chained.sort(key=self._record_sort_key)

        ordered: list[dict[str, Any]] = []
        seen_hashes: set[str] = set()
        current_previous = ""
        while True:
            candidates = [
                record
                for record in by_previous.get(current_previous, [])
                if record["content_hash"] not in seen_hashes
            ]
            if not candidates:
                break
            record = candidates[0]
            ordered.append(record)
            seen_hashes.add(record["content_hash"])
            current_previous = record["content_hash"]

        remaining = [record for record in records if record["content_hash"] not in seen_hashes]
        remaining.sort(key=self._record_sort_key)
        return ordered + remaining

    def _record_sort_key(self, record: dict[str, Any]) -> tuple[int, str]:
        suffix = record["record_id"].rsplit("::", 1)[-1]
        try:
            ordinal = int(suffix)
        except ValueError:
            ordinal = 0
        return (ordinal, record["content_hash"])

    def _canonical_json(self, value: dict[str, Any]) -> str:
        return json.dumps(value, allow_nan=False, separators=(",", ":"), sort_keys=True)

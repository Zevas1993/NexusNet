from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from nexus.schemas import new_id


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class MemoryRecord(BaseModel):
    memory_id: str = Field(default_factory=lambda: new_id("memfact"))
    fact_id: str
    content: str
    source: str
    evidence: dict[str, Any] = Field(default_factory=dict)
    effective_at: datetime = Field(default_factory=_utcnow)
    stored_at: datetime = Field(default_factory=_utcnow)
    archived: bool = False
    discarded: bool = False
    supersedes: str | None = None


class MemoryOperatingSystem:
    """Lifecycle controller above memory planes with provenance and temporal truth."""

    def __init__(self, persistence_path: Path | str | None = None):
        self._versions: dict[str, list[MemoryRecord]] = {}
        self._by_memory_id: dict[str, MemoryRecord] = {}
        self.persistence_path = Path(persistence_path) if persistence_path else None
        self._load()

    def store(
        self,
        *,
        fact_id: str,
        content: str,
        source: str,
        evidence: dict[str, Any] | None = None,
        effective_at: datetime | None = None,
    ) -> MemoryRecord:
        record = MemoryRecord(
            fact_id=fact_id,
            content=content,
            source=source,
            evidence=evidence or {},
            effective_at=effective_at or _utcnow(),
        )
        self._append(record)
        return record

    def update(
        self,
        *,
        fact_id: str,
        content: str,
        source: str,
        evidence: dict[str, Any] | None = None,
        effective_at: datetime | None = None,
    ) -> MemoryRecord:
        prior = self.retrieve(fact_id, include_archived=True, include_discarded=True)
        record = MemoryRecord(
            fact_id=fact_id,
            content=content,
            source=source,
            evidence=evidence or {},
            effective_at=effective_at or _utcnow(),
            supersedes=prior.memory_id if prior else None,
        )
        self._append(record)
        return record

    def retrieve(
        self,
        fact_id: str,
        *,
        as_of: datetime | None = None,
        include_archived: bool = False,
        include_discarded: bool = False,
    ) -> MemoryRecord | None:
        candidates = list(self._versions.get(fact_id, []))
        if as_of is not None:
            candidates = [record for record in candidates if record.effective_at <= as_of]
        if not include_archived:
            candidates = [record for record in candidates if not record.archived]
        if not include_discarded:
            candidates = [record for record in candidates if not record.discarded]
        if not candidates:
            return None
        return max(candidates, key=lambda record: (record.effective_at, record.stored_at))

    def summarize(self, fact_id: str | None = None) -> dict[str, Any]:
        fact_ids = [fact_id] if fact_id else sorted(self._versions)
        return {
            "fact_count": len(fact_ids),
            "version_count": sum(len(self._versions.get(item, [])) for item in fact_ids),
            "persistence_path": str(self.persistence_path) if self.persistence_path else None,
            "facts": {
                item: {
                    "current": (self.retrieve(item, include_archived=True, include_discarded=True).model_dump(mode="json") if self.retrieve(item, include_archived=True, include_discarded=True) else None),
                    "versions": len(self._versions.get(item, [])),
                }
                for item in fact_ids
            },
        }

    def archive(self, fact_id: str) -> MemoryRecord | None:
        current = self.retrieve(fact_id, include_archived=True, include_discarded=True)
        for record in self._versions.get(fact_id, []):
            record.archived = True
        if current is not None:
            self._persist()
        return current

    def discard(self, fact_id: str) -> MemoryRecord | None:
        current = self.retrieve(fact_id, include_archived=True, include_discarded=True)
        for record in self._versions.get(fact_id, []):
            record.discarded = True
        if current is not None:
            self._persist()
        return current

    def forget(self, fact_id: str) -> MemoryRecord | None:
        """Redact stored content while preserving a non-retrievable audit tombstone."""
        current = self.retrieve(fact_id, include_archived=True, include_discarded=True)
        for record in self._versions.get(fact_id, []):
            digest = hashlib.sha256(record.content.encode("utf-8")).hexdigest()
            record.content = f"[forgotten:sha256:{digest}]"
            record.discarded = True
        if current is not None:
            self._persist()
        return current

    def export_state(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "records": [
                record.model_dump(mode="json")
                for fact_versions in self._versions.values()
                for record in fact_versions
            ],
        }

    def restore_state(self, payload: dict[str, Any]) -> None:
        records = payload.get("records")
        if not isinstance(records, list):
            raise ValueError("memory state requires a records list")
        self._versions.clear()
        self._by_memory_id.clear()
        for item in records:
            self._append(MemoryRecord.model_validate(item), persist=False)
        self._persist()

    def dereference(self, memory_id: str) -> dict[str, Any]:
        record = self._by_memory_id[memory_id]
        return {
            "memory_id": record.memory_id,
            "fact_id": record.fact_id,
            "source": record.source,
            "evidence": record.evidence,
            "effective_at": record.effective_at.isoformat(),
            "content": record.content,
        }

    def provenance_lookup(self, fact_id: str) -> dict[str, Any]:
        versions = list(self._versions.get(fact_id, []))
        return {
            "fact_id": fact_id,
            "version_count": len(versions),
            "sources": [record.source for record in versions],
            "memory_ids": [record.memory_id for record in versions],
            "latest": versions[-1].memory_id if versions else None,
        }

    def _append(self, record: MemoryRecord, *, persist: bool = True) -> None:
        self._versions.setdefault(record.fact_id, []).append(record)
        self._versions[record.fact_id].sort(key=lambda item: (item.effective_at, item.stored_at))
        self._by_memory_id[record.memory_id] = record
        if persist:
            self._persist()

    def _load(self) -> None:
        if self.persistence_path is None or not self.persistence_path.exists():
            return
        payload = json.loads(self.persistence_path.read_text(encoding="utf-8"))
        for item in payload.get("records", []):
            self._append(MemoryRecord.model_validate(item), persist=False)

    def _persist(self) -> None:
        if self.persistence_path is None:
            return
        self.persistence_path.parent.mkdir(parents=True, exist_ok=True)
        payload = self.export_state()
        temporary = self.persistence_path.with_suffix(self.persistence_path.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        os.replace(temporary, self.persistence_path)

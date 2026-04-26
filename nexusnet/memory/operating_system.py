from __future__ import annotations

from datetime import datetime, timezone
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

    def __init__(self):
        self._versions: dict[str, list[MemoryRecord]] = {}
        self._by_memory_id: dict[str, MemoryRecord] = {}

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
        return current

    def discard(self, fact_id: str) -> MemoryRecord | None:
        current = self.retrieve(fact_id, include_archived=True, include_discarded=True)
        for record in self._versions.get(fact_id, []):
            record.discarded = True
        return current

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

    def _append(self, record: MemoryRecord) -> None:
        self._versions.setdefault(record.fact_id, []).append(record)
        self._versions[record.fact_id].sort(key=lambda item: (item.effective_at, item.stored_at))
        self._by_memory_id[record.memory_id] = record

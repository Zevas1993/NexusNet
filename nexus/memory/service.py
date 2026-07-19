from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable

from ..config import NexusPaths
from ..schemas import MemoryQuery, MemoryRecord, MemoryScore, Message
from ..storage import NexusStore


class MemoryService:
    DEFAULT_PLANES = (
        "working",
        "episodic",
        "semantic",
        "procedural",
        "benchmark",
        "dream",
        "curriculum",
        "architecture",
        "optimization",
    )

    def __init__(self, paths: NexusPaths, store: NexusStore):
        self.paths = paths
        self.store = store

    def append_messages(self, session_id: str, messages: Iterable[Message]) -> list[MemoryRecord]:
        saved = []
        for message in messages:
            gate = getattr(self, "genesis_memory_admission", None)
            if gate is not None and hasattr(gate, "record_manual_ingress"):
                decision = gate.record_manual_ingress(
                    session_id=session_id,
                    ingress_route="manual-memory-append",
                    content=message.content,
                    metadata={"source_kind": "manual-memory-message", "role": message.role},
                )
                if decision.get("memory_write_allowed") is not True:
                    continue
            record = MemoryRecord(
                session_id=session_id,
                plane="working",
                role=message.role,
                content={"text": message.content},
                tags=["chat"],
                score=MemoryScore(relevance=0.8, freshness=1.0, importance=0.5),
            )
            self.store.add_memory_record(record.model_dump(mode="json"))
            saved.append(record)
        self._update_analytics(session_id)
        return saved

    def record_episode(self, session_id: str, trace_id: str, summary: str, outcome: str) -> MemoryRecord:
        record = MemoryRecord(
            session_id=session_id,
            plane="episodic",
            content={"trace_id": trace_id, "summary": summary, "outcome": outcome},
            tags=["trace", "episode"],
            score=MemoryScore(relevance=0.7, freshness=0.9, importance=0.8, success_history=0.6),
        )
        self.store.add_memory_record(record.model_dump(mode="json"))
        self._update_analytics(session_id)
        return record

    def record_semantic(self, session_id: str, fact: str, source: str) -> MemoryRecord:
        record = MemoryRecord(
            session_id=session_id,
            plane="semantic",
            content={"fact": fact, "source": source},
            tags=["summary", "fact"],
            score=MemoryScore(relevance=0.7, freshness=0.6, importance=0.7, recurrence=0.2),
        )
        self.store.add_memory_record(record.model_dump(mode="json"))
        self._update_analytics(session_id)
        return record

    def activate_genesis_memory(
        self,
        *,
        memory_id: str,
        memory_ref: str,
        session_ref_digest: str,
        source_ref: str,
        content: str,
        content_ref: str,
    ) -> dict:
        record = MemoryRecord(
            memory_id=memory_id,
            session_id=session_ref_digest,
            plane="semantic",
            role="NexusBrain",
            content={
                "fact": content,
                "source": source_ref,
                "genesis_memory_id": memory_id,
                "genesis_memory_ref": memory_ref,
                "content_ref": content_ref,
            },
            tags=["canon", "genesis-layer7", "source-grounded"],
            score=MemoryScore(relevance=1.0, freshness=1.0, importance=0.9, recurrence=0.0),
        )
        self.store.add_memory_record(record.model_dump(mode="json"))
        self._update_analytics(session_ref_digest)
        state_ref = self._write_genesis_runtime_state(
            memory_id=memory_id,
            state="active",
            runtime_ref=f"semantic-memory::{memory_id}",
        )
        return {
            "surface_id": "genesis-memory-semantic-activation",
            "status": "active",
            "memory_id": memory_id,
            "state_ref": state_ref,
            "raw_content_included": False,
        }

    def deactivate_genesis_memory(
        self,
        *,
        memory_id: str,
        session_ref_digest: str,
        reason_ref: str,
    ) -> dict:
        state_ref = self._write_genesis_runtime_state(
            memory_id=memory_id,
            state="revoked",
            reason_ref=reason_ref,
        )
        self._update_analytics(session_ref_digest)
        return {
            "surface_id": "genesis-memory-semantic-deactivation",
            "status": "revoked",
            "memory_id": memory_id,
            "state_ref": state_ref,
            "reason_ref": reason_ref,
            "raw_content_included": False,
        }

    def record_procedural(self, session_id: str, pattern: str, rationale: str) -> MemoryRecord:
        record = MemoryRecord(
            session_id=session_id,
            plane="procedural",
            content={"pattern": pattern, "rationale": rationale},
            tags=["procedure", "playbook"],
            score=MemoryScore(relevance=0.6, freshness=0.5, importance=0.7, success_history=0.5),
        )
        self.store.add_memory_record(record.model_dump(mode="json"))
        self._update_analytics(session_id)
        return record

    def query(self, request: MemoryQuery) -> list[MemoryRecord]:
        self._migrate_legacy_session(request.session_id)
        records = self.store.list_memory_records(request.session_id, request.plane, request.limit)
        return [
            MemoryRecord.model_validate(record)
            for record in records
            if self._genesis_record_active(record)
        ]

    def session_view(self, session_id: str) -> dict:
        records = self.query(MemoryQuery(session_id=session_id, limit=500))
        grouped = {plane: [] for plane in self.DEFAULT_PLANES}
        for record in records:
            grouped.setdefault(record.plane, []).append(record.model_dump(mode="json"))
        analytics = self.store.get_memory_analytics(session_id) or self._update_analytics(session_id)
        return {"session_id": session_id, "planes": grouped, "analytics": analytics}

    def recent_messages(self, session_id: str, limit: int = 6) -> list[Message]:
        records = self.query(MemoryQuery(session_id=session_id, plane="working", limit=limit))
        messages = []
        for record in records[-limit:]:
            text = record.content.get("text")
            if text:
                messages.append(Message(role=record.role or "user", content=text))
        return messages

    def _update_analytics(self, session_id: str) -> dict:
        records = [
            record
            for record in self.store.list_memory_records(session_id, limit=1000)
            if self._genesis_record_active(record)
        ]
        counts = {plane: 0 for plane in self.DEFAULT_PLANES}
        last_updated = None
        for record in records:
            counts[record["plane"]] = counts.get(record["plane"], 0) + 1
            last_updated = record["updated_at"]
        analytics = {"counts": counts, "total_records": len(records), "last_updated": last_updated}
        self.store.save_memory_analytics(session_id, analytics, last_updated or "")
        return analytics

    def _migrate_legacy_session(self, session_id: str) -> None:
        if self.store.list_memory_records(session_id, limit=1):
            return
        legacy_path = self.paths.legacy_sessions_dir / f"{session_id}.jsonl"
        if not legacy_path.exists():
            return
        records = []
        with legacy_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    continue
                text = payload.get("content")
                if not text:
                    continue
                records.append(Message(role=payload.get("role", "user"), content=text))
        if records:
            self.append_messages(session_id, records)

    def _write_genesis_runtime_state(
        self,
        *,
        memory_id: str,
        state: str,
        runtime_ref: str | None = None,
        reason_ref: str | None = None,
    ) -> str:
        key = hashlib.sha256(memory_id.encode("utf-8")).hexdigest()[:24]
        relative_ref = f"genesis/memory-foundation/runtime/memory/{key}.json"
        path = self.paths.artifacts_dir / relative_ref
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "memory_id": memory_id,
                    "state": state,
                    "runtime_ref": runtime_ref,
                    "reason_ref": reason_ref,
                    "raw_content_included": False,
                },
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        return relative_ref

    def _genesis_record_active(self, record: dict) -> bool:
        content = record.get("content") if isinstance(record.get("content"), dict) else {}
        memory_id = str(content.get("genesis_memory_id") or "")
        if not memory_id:
            return True
        key = hashlib.sha256(memory_id.encode("utf-8")).hexdigest()[:24]
        path = (
            self.paths.artifacts_dir
            / "genesis"
            / "memory-foundation"
            / "runtime"
            / "memory"
            / f"{key}.json"
        )
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return False
        return payload.get("state") == "active"

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any, Iterable, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow


Sensitivity = Literal["public", "internal", "confidential", "regulated", "secret"]


class EngramRecordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_id: str | None = None
    text: str
    fact: str
    source_ref: str
    tags: list[str] = Field(default_factory=list)
    sensitivity: Sensitivity = "internal"
    metadata: dict[str, Any] = Field(default_factory=dict)


class EngramLookupRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str
    context_terms: list[str] = Field(default_factory=list)
    top_k: int = Field(default=5, ge=1, le=25)
    include_sensitive: bool = False


class NexusEngramIndex:
    def __init__(
        self,
        *,
        artifacts_dir: Path | str | None = None,
        table_size: int = 4096,
        head_count: int = 8,
        ngram_orders: tuple[int, ...] = (1, 2, 3),
    ) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.records_dir = self.artifacts_dir / "memory" / "engram-index" if self.artifacts_dir else None
        if self.records_dir is not None:
            self.records_dir.mkdir(parents=True, exist_ok=True)
        self.table_size = max(int(table_size), 2)
        self.head_count = max(int(head_count), 1)
        self.ngram_orders = tuple(sorted(set(int(order) for order in ngram_orders if int(order) > 0))) or (1,)
        self._records: dict[str, dict[str, Any]] = {}
        self._slot_records: dict[str, set[str]] = {}
        self._load_existing()

    def store(self, request: EngramRecordRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, EngramRecordRequest) else EngramRecordRequest.model_validate(request)
        record_id = normalized.record_id or f"engram::{_stable_id(normalized.text)}"
        tokens = _tokens(normalized.text)
        hashes = self._hashes(tokens)
        record = {
            "status_label": "LOCKED CANON",
            "surface_id": "engram-memory-index",
            "record_id": record_id,
            "text": normalized.text,
            "fact": normalized.fact,
            "source_ref": normalized.source_ref,
            "tags": sorted({_normalize_term(tag) for tag in normalized.tags if _normalize_term(tag)}),
            "sensitivity": normalized.sensitivity,
            "tokens": tokens,
            "hashes": hashes,
            "created_at": utcnow().isoformat(),
            "metadata": normalized.metadata,
        }
        self._records[record_id] = record
        self._index_record(record)
        self._persist(record)
        return record

    def lookup(self, request: EngramLookupRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, EngramLookupRequest) else EngramLookupRequest.model_validate(request)
        query_tokens = _tokens(normalized.text)
        query_hashes = self._hashes(query_tokens)
        query_slots = {item["slot_key"] for item in query_hashes}
        candidates: dict[str, set[str]] = {}
        for slot_key in query_slots:
            for record_id in self._slot_records.get(slot_key, set()):
                candidates.setdefault(record_id, set()).add(slot_key)

        findings: list[str] = []
        skipped_sensitive = False
        results: list[dict[str, Any]] = []
        for record_id, matching_slots in candidates.items():
            record = self._records[record_id]
            if record.get("sensitivity") != "public" and not normalized.include_sensitive:
                skipped_sensitive = True
                continue
            result = self._result(record, matching_slots, query_tokens, normalized.context_terms)
            if result["gate_score"] > 0:
                results.append(result)

        if skipped_sensitive:
            findings.append("sensitive_records_excluded")

        results.sort(key=lambda item: (item["gate_score"], item["ngram_hit_count"], item["record_id"]), reverse=True)
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "engram-memory-index",
            "authority": "NexusBrain",
            "runtime_state": "degraded" if findings else "live-bound",
            "query": normalized.model_dump(mode="json"),
            "results": results[: normalized.top_k],
            "result_count": len(results[: normalized.top_k]),
            "findings": findings,
            "memory_boundary": "explicit-memory-sidecar-not-hidden-weight-authority",
            "required_controls": _required_controls(),
            "operator_actions": _operator_actions(),
        }

    def summary(self) -> dict[str, Any]:
        records = list(self._records.values())
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "engram-memory-index",
            "authority": "NexusBrain",
            "runtime_state": "live-bound" if records else "static-canon",
            "record_count": len(records),
            "table_size": self.table_size,
            "head_count": self.head_count,
            "ngram_orders": list(self.ngram_orders),
            "collision_slot_count": self._collision_slot_count(),
            "sensitivity_counts": _counts(record.get("sensitivity", "internal") for record in records),
            "recent_records": sorted(records, key=lambda item: item.get("created_at") or "", reverse=True)[:10],
            "memory_boundary": "explicit-memory-sidecar-not-hidden-weight-authority",
            "required_controls": _required_controls(),
            "operator_actions": _operator_actions(),
        }

    def scorecard(self) -> dict[str, Any]:
        return {
            **self.summary(),
            "control_panel_label": "Engram Memory Index",
            "source_documents": [
                "docs/NEXUSNET_YOUTUBE_ASSIMILATION_INTAKE_2026-04-30.md#engram-memory",
                "docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md",
            ],
            "architecture_contract": [
                "multiplicative_xor_hashing",
                "multi_head_collision_mitigation",
                "context_aware_gate",
                "sensitive_record_lookup_gate",
                "sidecar_memory_not_model_weights",
            ],
        }

    def _hashes(self, tokens: list[str]) -> list[dict[str, Any]]:
        token_ids = [_token_id(token) for token in tokens]
        hashes: list[dict[str, Any]] = []
        for order in self.ngram_orders:
            if len(token_ids) < order:
                continue
            for start in range(0, len(token_ids) - order + 1):
                ids = token_ids[start : start + order]
                text = " ".join(tokens[start : start + order])
                for head in range(self.head_count):
                    slot = self._slot(ids, head)
                    slot_key = f"{order}:{head}:{slot}"
                    hashes.append(
                        {
                            "order": order,
                            "head": head,
                            "slot": slot,
                            "slot_key": slot_key,
                            "ngram": text,
                        }
                    )
        return hashes

    def _slot(self, token_ids: list[int], head: int) -> int:
        mixed = 0
        for position, token_id in enumerate(token_ids):
            mixed ^= (token_id * _odd_multiplier(head, position)) & ((1 << 64) - 1)
        return mixed % self.table_size

    def _index_record(self, record: dict[str, Any]) -> None:
        record_id = record["record_id"]
        for item in record.get("hashes", []):
            self._slot_records.setdefault(item["slot_key"], set()).add(record_id)

    def _result(
        self,
        record: dict[str, Any],
        matching_slots: set[str],
        query_tokens: list[str],
        context_terms: list[str],
    ) -> dict[str, Any]:
        record_slots = {item["slot_key"] for item in record.get("hashes", [])}
        denominator = max(min(len(record_slots), len(matching_slots) + max(len(query_tokens), 1)), 1)
        hash_score = min(len(matching_slots) / denominator, 1.0)
        record_terms = set(record.get("tokens", [])) | set(record.get("tags", [])) | set(_tokens(record.get("fact", "")))
        query_terms = set(query_tokens) | {_normalize_term(term) for term in context_terms if _normalize_term(term)}
        overlap_score = len(record_terms & query_terms) / max(len(query_terms), 1)
        context_set = {_normalize_term(term) for term in context_terms if _normalize_term(term)}
        context_score = len(set(record.get("tags", [])) & context_set) / max(len(context_set), 1) if context_set else 0.0
        raw_gate = (0.48 * hash_score) + (0.32 * overlap_score) + (0.20 * context_score)
        gate_score = round(1 / (1 + math.exp(-6 * (raw_gate - 0.35))), 4)
        collision_count = sum(1 for slot in matching_slots if len(self._slot_records.get(slot, set())) > 1)
        return {
            "record_id": record["record_id"],
            "text": record["text"],
            "fact": record["fact"],
            "source_ref": record["source_ref"],
            "tags": record.get("tags", []),
            "sensitivity": record.get("sensitivity", "internal"),
            "gate_score": gate_score,
            "ngram_hit_count": len(matching_slots),
            "matching_slots": sorted(matching_slots),
            "collision_count": collision_count,
            "multi_head_hashes": [
                item for item in record.get("hashes", []) if item["slot_key"] in matching_slots
            ][:12],
        }

    def _persist(self, record: dict[str, Any]) -> None:
        if self.records_dir is None:
            return
        path = self.records_dir / f"{_safe_name(record['record_id'])}.json"
        record["artifact_path"] = str(path)
        path.write_text(json.dumps(record, indent=2), encoding="utf-8")

    def _load_existing(self) -> None:
        if self.records_dir is None:
            return
        for path in self.records_dir.glob("*.json"):
            try:
                record = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if not record.get("record_id"):
                continue
            self._records[record["record_id"]] = record
            self._index_record(record)

    def _collision_slot_count(self) -> int:
        return sum(1 for records in self._slot_records.values() if len(records) > 1)


def _tokens(text: str) -> list[str]:
    return [_normalize_term(match.group(0)) for match in re.finditer(r"[A-Za-z0-9_'-]+", text) if _normalize_term(match.group(0))]


def _normalize_term(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace("'", "")


def _token_id(token: str) -> int:
    return int.from_bytes(hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest(), byteorder="big", signed=False)


def _stable_id(text: str) -> str:
    return hashlib.blake2b(text.encode("utf-8"), digest_size=8).hexdigest()


def _odd_multiplier(head: int, position: int) -> int:
    seed = f"nexus-engram::{head}::{position}".encode("utf-8")
    value = int.from_bytes(hashlib.blake2b(seed, digest_size=8).digest(), byteorder="big", signed=False)
    return value | 1


def _safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)[:160] or "engram"


def _counts(values: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts


def _required_controls() -> list[str]:
    return [
        "multiplicative_xor_hash",
        "multi_head_hash_collision_budget",
        "context_aware_gate",
        "source_ref_required",
        "sensitive_record_lookup_gate",
        "collision_pressure_summary",
    ]


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/memory/engram"},
        "record": {"method": "POST", "endpoint": "/ops/brain/memory/engram/records"},
        "lookup": {"method": "POST", "endpoint": "/ops/brain/memory/engram/lookup"},
        "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/engram-memory"},
    }

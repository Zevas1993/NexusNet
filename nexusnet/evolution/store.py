from __future__ import annotations

import json
import math
import os
import re
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

from nexusnet.evolution.contracts import sanitize_reference


EVENT_SCHEMA_VERSION = "nexusnet-evolution-event-v1"
CLAIM_BOUNDARY_TOKEN = "reference-presence-is-not-semantic-proof"
EVENT_KEYS = frozenset(
    {
        "schema_version",
        "sequence",
        "event_type",
        "recorded_at",
        "previous_event_sha256",
        "payload_sha256",
        "payload",
        "event_sha256",
    }
)
METADATA_STRING_KEYS = frozenset(
    {
        "schema_version",
        "unit_kind",
        "authority_class",
        "privacy_class",
        "license_state",
        "trust_state",
        "federation_policy",
        "lifecycle_state",
        "family",
        "problem_class",
        "status",
    }
)
REFERENCE_LIST_KEYS = frozenset({"affected_workloads"})
IDENTIFIER_OR_REFERENCE_LIST_KEYS = frozenset({"affected_hardware_classes"})
NUMERIC_FLOAT_KEYS = frozenset(
    {
        "severity",
        "quality_risk",
        "safety_risk",
        "opportunity_score",
        "expected_value",
        "research_budget_request",
    }
)
NUMERIC_INTEGER_KEYS = frozenset({"recurrence", "legacy_aspect_total"})
BOOLEAN_KEYS = frozenset({"legacy_taxonomy_fully_covered"})
OPTIONAL_REFERENCE_KEYS = frozenset(
    {"current_release_ref", "registration_schema_ref", "evidence_ref"}
)
UNIT_PAYLOAD_KEYS = frozenset(
    {
        "schema_version", "unit_id", "unit_kind", "owner_brain_ref",
        "parent_unit_refs", "child_unit_refs", "capability_refs", "genome_refs",
        "implementation_refs", "dependency_refs", "pathway_refs", "authority_class",
        "privacy_class", "license_state", "trust_state", "current_release_ref",
        "checkpoint_refs", "health_refs", "workload_refs", "eval_suite_refs",
        "invariant_refs", "growth_pressure_refs", "candidate_refs", "federation_policy",
        "lifecycle_state", "registration_schema_ref", "rollback_refs",
        "improvement_strategy_refs",
    }
)
GENOME_PAYLOAD_KEYS = frozenset(
    {"schema_version", "genome_id", "family", "content_ref", "invariant_refs"}
)
PRESSURE_PAYLOAD_KEYS = frozenset(
    {
        "schema_version", "pressure_id", "target_unit_refs", "source_evidence_refs",
        "problem_class", "severity", "recurrence", "affected_workloads",
        "affected_hardware_classes", "quality_risk", "safety_risk",
        "opportunity_score", "expected_value", "research_budget_request", "status",
    }
)
FOUNDATION_PAYLOAD_KEYS = frozenset(
    {"schema_version", "foundation_id", "status", "evidence_ref", "claim_boundary"}
)
SNAPSHOT_PAYLOAD_KEYS = frozenset(
    {
        "schema_version", "snapshot_id", "registered_unit_refs", "implementation_refs",
        "dependency_refs", "pathway_refs", "capability_refs", "health_refs",
        "workload_refs", "resource_refs", "benchmark_refs", "candidate_refs",
        "governance_refs", "external_alternative_refs", "unresolved_refs",
    }
)
LEGACY_TAXONOMY_PAYLOAD_KEYS = frozenset(
    {
        "legacy_taxonomy_id", "legacy_aspect_total",
        "legacy_taxonomy_fully_covered", "aspect_refs", "covered_refs",
        "uncovered_refs",
    }
)
CONTRACT_PAYLOAD_SCHEMAS = (
    UNIT_PAYLOAD_KEYS,
    GENOME_PAYLOAD_KEYS,
    PRESSURE_PAYLOAD_KEYS,
    FOUNDATION_PAYLOAD_KEYS,
    SNAPSHOT_PAYLOAD_KEYS,
)
EVENT_PAYLOAD_SCHEMAS = {
    "unit.registered": (UNIT_PAYLOAD_KEYS,),
    "genome.registered": (GENOME_PAYLOAD_KEYS,),
    "pressure.recorded": (PRESSURE_PAYLOAD_KEYS,),
    "foundation.recorded": (FOUNDATION_PAYLOAD_KEYS,),
    "snapshot.recorded": (SNAPSHOT_PAYLOAD_KEYS,),
    "contract.recorded": CONTRACT_PAYLOAD_SCHEMAS,
    "legacy-taxonomy.observed": (LEGACY_TAXONOMY_PAYLOAD_KEYS,),
}
SAFE_TOKEN_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9._-]{0,127}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_PROCESS_LOCKS_GUARD = threading.Lock()
_PROCESS_LOCKS: dict[str, threading.RLock] = {}


class EvolutionIntegrityError(RuntimeError):
    """Raised when persisted evolution events fail integrity verification."""


def _process_lock(path: Path) -> threading.RLock:
    key = str(path.resolve())
    with _PROCESS_LOCKS_GUARD:
        return _PROCESS_LOCKS.setdefault(key, threading.RLock())


@contextmanager
def _exclusive_chain_access(path: Path):
    lock_path = path.with_suffix(path.suffix + ".lock")
    process_lock = _process_lock(lock_path)
    with process_lock:
        with lock_path.open("a+b") as lock_stream:
            lock_stream.seek(0, os.SEEK_END)
            if lock_stream.tell() == 0:
                lock_stream.write(b"\0")
                lock_stream.flush()
                os.fsync(lock_stream.fileno())
            lock_stream.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(lock_stream.fileno(), msvcrt.LK_LOCK, 1)
            else:
                import fcntl

                fcntl.flock(lock_stream.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                lock_stream.seek(0)
                if os.name == "nt":
                    msvcrt.locking(lock_stream.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(lock_stream.fileno(), fcntl.LOCK_UN)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _sha256(value: Any) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _sanitize_metadata_token(value: str, *, field_name: str) -> str:
    if not SAFE_TOKEN_PATTERN.fullmatch(value) or value.lower().startswith("sk-"):
        raise ValueError(
            f"unsafe payload metadata: {field_name} must be a bounded safe token"
        )
    return value


def _sanitize_reference_list(value: Any, *, field_name: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"unsafe payload metadata: {field_name} must be references")
    return [sanitize_reference(item) for item in value]


def _sanitize_field(field_name: str, value: Any) -> Any:
    if field_name == "claim_boundary":
        if value != CLAIM_BOUNDARY_TOKEN:
            raise ValueError(
                "unsafe payload metadata: claim_boundary must use the controlled token"
            )
        return value
    if field_name.endswith("_id"):
        if not isinstance(value, str):
            raise ValueError(f"unsafe payload metadata: {field_name} must be a reference")
        return sanitize_reference(value)
    if field_name.endswith("_ref"):
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError(f"unsafe payload metadata: {field_name} must be a reference")
        return sanitize_reference(value)
    if field_name.endswith("_refs") or field_name in REFERENCE_LIST_KEYS:
        return _sanitize_reference_list(value, field_name=field_name)
    if field_name in IDENTIFIER_OR_REFERENCE_LIST_KEYS:
        if not isinstance(value, list) or not all(
            isinstance(item, str) for item in value
        ):
            raise ValueError(
                f"unsafe payload metadata: {field_name} must be safe tokens or references"
            )
        return [
            sanitize_reference(item)
            if ":" in item
            else _sanitize_metadata_token(item, field_name=field_name)
            for item in value
        ]
    if field_name in METADATA_STRING_KEYS:
        if not isinstance(value, str):
            raise ValueError(
                f"unsafe payload metadata: {field_name} must be a bounded safe token"
            )
        return _sanitize_metadata_token(value, field_name=field_name)
    if field_name in NUMERIC_FLOAT_KEYS:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"unsafe payload metadata: {field_name} must be numeric")
        if not math.isfinite(value):
            raise ValueError(f"unsafe payload metadata: {field_name} must be finite")
        return value
    if field_name in NUMERIC_INTEGER_KEYS:
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"unsafe payload metadata: {field_name} must be an integer")
        return value
    if field_name in BOOLEAN_KEYS:
        if not isinstance(value, bool):
            raise ValueError(f"unsafe payload metadata: {field_name} must be boolean")
        return value
    if field_name in OPTIONAL_REFERENCE_KEYS and value is None:
        return None
    raise ValueError(f"unsafe payload metadata: unknown field {field_name}")


def _payload_schema(event_type: str, payload: dict[str, Any]) -> frozenset[str]:
    schemas = EVENT_PAYLOAD_SCHEMAS.get(event_type, ())
    payload_keys = set(payload)
    matches = [schema for schema in schemas if payload_keys <= schema]
    if not matches:
        raise ValueError("unsafe payload metadata: unknown event payload shape")
    return min(matches, key=len)


def _sanitize_payload(event_type: str, value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("unsafe payload metadata: payload must be an object")
    allowed_fields = _payload_schema(event_type, value)
    sanitized: dict[str, Any] = {}
    for key, nested in value.items():
        if not isinstance(key, str) or key not in allowed_fields:
            raise ValueError("unsafe payload metadata: keys must be allowlisted strings")
        sanitized[key] = _sanitize_field(key, nested)
    return sanitized


def _validate_event_record(record: dict[str, Any], event_number: int) -> None:
    if set(record) != EVENT_KEYS:
        raise EvolutionIntegrityError(
            f"event {event_number} does not match the exact event schema"
        )
    if record["schema_version"] != EVENT_SCHEMA_VERSION:
        raise EvolutionIntegrityError(
            f"event {event_number} has unsupported schema_version"
        )
    sequence = record["sequence"]
    if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence <= 0:
        raise EvolutionIntegrityError(f"event {event_number} has invalid sequence")
    event_type = record["event_type"]
    if not isinstance(event_type, str):
        raise EvolutionIntegrityError(f"event {event_number} has invalid event_type")
    try:
        _sanitize_metadata_token(event_type, field_name="event_type")
    except ValueError as exc:
        raise EvolutionIntegrityError(
            f"event {event_number} has invalid event_type"
        ) from exc
    recorded_at = record["recorded_at"]
    if not isinstance(recorded_at, str):
        raise EvolutionIntegrityError(f"event {event_number} has invalid recorded_at")
    try:
        timestamp = datetime.fromisoformat(recorded_at)
    except ValueError as exc:
        raise EvolutionIntegrityError(
            f"event {event_number} has invalid recorded_at"
        ) from exc
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise EvolutionIntegrityError(f"event {event_number} has invalid recorded_at")
    previous_hash = record["previous_event_sha256"]
    if previous_hash is not None and (
        not isinstance(previous_hash, str)
        or not SHA256_PATTERN.fullmatch(previous_hash)
    ):
        raise EvolutionIntegrityError(
            f"event {event_number} has invalid previous_event_sha256"
        )
    if not isinstance(record["payload"], dict):
        raise EvolutionIntegrityError(f"event {event_number} has invalid payload")
    for hash_field in ("payload_sha256", "event_sha256"):
        value = record[hash_field]
        if not isinstance(value, str) or not SHA256_PATTERN.fullmatch(value):
            raise EvolutionIntegrityError(
                f"event {event_number} has invalid {hash_field}"
            )


class EvolutionEventStore:
    def __init__(self, root: Path):
        self.path = root / "evolution" / "events.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        with _exclusive_chain_access(self.path):
            replayed = self._replay_unlocked()
            _sanitize_metadata_token(event_type, field_name="event_type")
            sanitized_payload = _sanitize_payload(event_type, payload)
            previous_hash = replayed[-1]["event_sha256"] if replayed else None
            record = {
                "schema_version": EVENT_SCHEMA_VERSION,
                "sequence": len(replayed) + 1,
                "event_type": event_type,
                "recorded_at": datetime.now(timezone.utc).isoformat(),
                "previous_event_sha256": previous_hash,
                "payload_sha256": _sha256(sanitized_payload),
                "payload": sanitized_payload,
            }
            record["event_sha256"] = _sha256(record)
            with self.path.open("a", encoding="utf-8", newline="\n") as stream:
                stream.write(_canonical_json(record) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
            return record

    def replay(self) -> list[dict[str, Any]]:
        with _exclusive_chain_access(self.path):
            return self._replay_unlocked()

    def _replay_unlocked(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []

        replayed: list[dict[str, Any]] = []
        previous_hash: str | None = None
        with self.path.open("r", encoding="utf-8") as stream:
            for expected_sequence, line in enumerate(stream, start=1):
                try:
                    record = json.loads(line)
                except (json.JSONDecodeError, TypeError) as exc:
                    raise EvolutionIntegrityError(
                        f"event {expected_sequence} is not valid JSON"
                    ) from exc
                if not isinstance(record, dict):
                    raise EvolutionIntegrityError(
                        f"event {expected_sequence} must be an event object"
                    )
                _validate_event_record(record, expected_sequence)
                if record["sequence"] != expected_sequence:
                    raise EvolutionIntegrityError(
                        f"event {expected_sequence} has non-contiguous sequence"
                    )
                if record["previous_event_sha256"] != previous_hash:
                    raise EvolutionIntegrityError(
                        f"event {expected_sequence} previous hash mismatch"
                    )
                payload = record["payload"]
                try:
                    sanitized_payload = _sanitize_payload(record["event_type"], payload)
                except ValueError as exc:
                    raise EvolutionIntegrityError(
                        f"event {expected_sequence} has unsafe payload metadata: {exc}"
                    ) from exc
                if sanitized_payload != payload:
                    raise EvolutionIntegrityError(
                        f"event {expected_sequence} has non-canonical payload metadata"
                    )
                if record["payload_sha256"] != _sha256(payload):
                    raise EvolutionIntegrityError(
                        f"event {expected_sequence} payload hash mismatch"
                    )
                event_hash = record["event_sha256"]
                record_without_hash = {
                    key: value for key, value in record.items() if key != "event_sha256"
                }
                if event_hash != _sha256(record_without_hash):
                    raise EvolutionIntegrityError(
                        f"event {expected_sequence} event hash mismatch"
                    )
                replayed.append(record)
                previous_hash = event_hash
        return replayed

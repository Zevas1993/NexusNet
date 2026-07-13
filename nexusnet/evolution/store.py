from __future__ import annotations

import json
import os
import re
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ValidationError

from nexusnet.evolution.contracts import (
    EverythingStateSnapshot,
    EvolvableUnit,
    FoundationCheck,
    GenomeRef,
    GrowthPressure,
    sanitize_reference,
)


EVENT_SCHEMA_VERSION = "nexusnet-evolution-event-v1"
LEGACY_TAXONOMY_ID = "schema:legacy-self-improvement-taxonomy-v1"
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
UNIT_PAYLOAD_KEYS = frozenset(EvolvableUnit.model_fields)
GENOME_PAYLOAD_KEYS = frozenset(GenomeRef.model_fields)
PRESSURE_PAYLOAD_KEYS = frozenset(GrowthPressure.model_fields)
FOUNDATION_PAYLOAD_KEYS = frozenset(FoundationCheck.model_fields)
SNAPSHOT_PAYLOAD_KEYS = frozenset(EverythingStateSnapshot.model_fields)
LEGACY_TAXONOMY_PAYLOAD_KEYS = frozenset(
    {
        "legacy_taxonomy_id", "legacy_aspect_total",
        "legacy_taxonomy_fully_covered", "aspect_refs", "covered_refs",
        "uncovered_refs",
    }
)
CONTRACT_PAYLOAD_SCHEMAS: tuple[tuple[frozenset[str], type[BaseModel]], ...] = (
    (UNIT_PAYLOAD_KEYS, EvolvableUnit),
    (GENOME_PAYLOAD_KEYS, GenomeRef),
    (PRESSURE_PAYLOAD_KEYS, GrowthPressure),
    (FOUNDATION_PAYLOAD_KEYS, FoundationCheck),
    (SNAPSHOT_PAYLOAD_KEYS, EverythingStateSnapshot),
)
EVENT_PAYLOAD_MODELS: dict[str, tuple[frozenset[str], type[BaseModel]]] = {
    "unit.registered": (UNIT_PAYLOAD_KEYS, EvolvableUnit),
    "genome.registered": (GENOME_PAYLOAD_KEYS, GenomeRef),
    "pressure.recorded": (PRESSURE_PAYLOAD_KEYS, GrowthPressure),
    "foundation.recorded": (FOUNDATION_PAYLOAD_KEYS, FoundationCheck),
    "snapshot.recorded": (SNAPSHOT_PAYLOAD_KEYS, EverythingStateSnapshot),
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


def _validate_model_payload(
    payload: dict[str, Any],
    *,
    expected_keys: frozenset[str],
    model: type[BaseModel],
) -> dict[str, Any]:
    if set(payload) != expected_keys:
        raise ValueError("unsafe payload metadata: payload keys must match exactly")
    try:
        validated = model.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(f"unsafe payload metadata: consumer validation failed: {exc}") from exc
    return validated.model_dump(mode="json")


def _validate_legacy_taxonomy(payload: dict[str, Any]) -> dict[str, Any]:
    if set(payload) != LEGACY_TAXONOMY_PAYLOAD_KEYS:
        raise ValueError("unsafe payload metadata: payload keys must match exactly")
    taxonomy_id = payload["legacy_taxonomy_id"]
    total = payload["legacy_aspect_total"]
    fully_covered = payload["legacy_taxonomy_fully_covered"]
    if taxonomy_id != LEGACY_TAXONOMY_ID:
        raise ValueError("unsafe payload metadata: invalid legacy taxonomy id")
    if isinstance(total, bool) or not isinstance(total, int) or total < 0:
        raise ValueError("unsafe payload metadata: invalid legacy aspect total")
    if not isinstance(fully_covered, bool):
        raise ValueError("unsafe payload metadata: invalid legacy coverage flag")
    refs: dict[str, list[str]] = {}
    for field_name in ("aspect_refs", "covered_refs", "uncovered_refs"):
        value = payload[field_name]
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise ValueError(f"unsafe payload metadata: {field_name} must be references")
        sanitized = [sanitize_reference(item) for item in value]
        if len(set(sanitized)) != len(sanitized):
            raise ValueError(f"unsafe payload metadata: {field_name} must be unique")
        refs[field_name] = sorted(sanitized)
    aspects = set(refs["aspect_refs"])
    covered = set(refs["covered_refs"])
    uncovered = set(refs["uncovered_refs"])
    expected_fully_covered = total > 0 and covered == aspects and not uncovered
    if (
        len(aspects) != total
        or covered & uncovered
        or covered | uncovered != aspects
        or fully_covered != expected_fully_covered
    ):
        raise ValueError("unsafe payload metadata: inconsistent legacy taxonomy coverage")
    return {
        "legacy_taxonomy_id": taxonomy_id,
        "legacy_aspect_total": total,
        "legacy_taxonomy_fully_covered": fully_covered,
        **refs,
    }


def _sanitize_payload(event_type: str, value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("unsafe payload metadata: payload must be an object")
    if event_type == "legacy-taxonomy.observed":
        return _validate_legacy_taxonomy(value)
    if event_type == "contract.recorded":
        matches = [entry for entry in CONTRACT_PAYLOAD_SCHEMAS if set(value) == entry[0]]
        if len(matches) != 1:
            raise ValueError("unsafe payload metadata: unknown contract payload shape")
        expected_keys, model = matches[0]
        return _validate_model_payload(value, expected_keys=expected_keys, model=model)
    payload_model = EVENT_PAYLOAD_MODELS.get(event_type)
    if payload_model is None:
        raise ValueError("unsafe payload metadata: unknown event type")
    expected_keys, model = payload_model
    return _validate_model_payload(value, expected_keys=expected_keys, model=model)


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

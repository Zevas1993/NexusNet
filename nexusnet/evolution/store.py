from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

from nexusnet.evolution.contracts import sanitize_reference


EVENT_SCHEMA_VERSION = "nexusnet-evolution-event-v1"
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
        "claim_boundary",
    }
)
REFERENCE_LIST_KEYS = frozenset({"affected_workloads"})
IDENTIFIER_OR_REFERENCE_LIST_KEYS = frozenset({"affected_hardware_classes"})
SAFE_TOKEN_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9._-]{0,127}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class EvolutionIntegrityError(RuntimeError):
    """Raised when persisted evolution events fail integrity verification."""


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
    return _sanitize_payload(value)


def _sanitize_payload(value: Any) -> Any:
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, nested in value.items():
            if not isinstance(key, str):
                raise ValueError("unsafe payload metadata: keys must be strings")
            sanitized[key] = _sanitize_field(key, nested)
        return sanitized
    if isinstance(value, list):
        return [_sanitize_payload(item) for item in value]
    if isinstance(value, str):
        raise ValueError(
            "unsafe payload metadata: string fields require an allowlisted metadata key"
        )
    if value is None or isinstance(value, (bool, int, float)):
        return value
    raise ValueError("unsafe payload metadata: unsupported value type")


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
    if not isinstance(event_type, str) or not SAFE_TOKEN_PATTERN.fullmatch(event_type):
        raise EvolutionIntegrityError(f"event {event_number} has invalid event_type")
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
        replayed = self.replay()
        _sanitize_metadata_token(event_type, field_name="event_type")
        sanitized_payload = _sanitize_payload(payload)
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
                    sanitized_payload = _sanitize_payload(payload)
                except ValueError as exc:
                    raise EvolutionIntegrityError(
                        f"event {expected_sequence} has unsafe payload metadata"
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

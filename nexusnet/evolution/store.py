from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

from nexusnet.evolution.contracts import sanitize_reference


EVENT_SCHEMA_VERSION = "nexusnet-evolution-event-v1"


class EvolutionIntegrityError(RuntimeError):
    """Raised when persisted evolution events fail integrity verification."""


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _sha256(value: Any) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _sanitize_payload(value: Any, *, reference_value: bool = False) -> Any:
    if isinstance(value, dict):
        return {
            key: _sanitize_payload(
                nested,
                reference_value=reference_value
                or key.endswith("_ref")
                or key.endswith("_refs"),
            )
            for key, nested in value.items()
        }
    if isinstance(value, list):
        return [
            _sanitize_payload(item, reference_value=reference_value) for item in value
        ]
    if reference_value and isinstance(value, str):
        return sanitize_reference(value)
    return value


class EvolutionEventStore:
    def __init__(self, root: Path):
        self.path = root / "evolution" / "events.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        replayed = self.replay()
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
                if record.get("sequence") != expected_sequence:
                    raise EvolutionIntegrityError(
                        f"event {expected_sequence} has non-contiguous sequence"
                    )
                if record.get("previous_event_sha256") != previous_hash:
                    raise EvolutionIntegrityError(
                        f"event {expected_sequence} previous hash mismatch"
                    )
                payload = record.get("payload")
                if record.get("payload_sha256") != _sha256(payload):
                    raise EvolutionIntegrityError(
                        f"event {expected_sequence} payload hash mismatch"
                    )
                event_hash = record.get("event_sha256")
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

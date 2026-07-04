from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _write_text_mirrored(payload: str, *, primary_path: Path, public_path: Path | None) -> None:
    primary_path.parent.mkdir(parents=True, exist_ok=True)
    primary_path.write_text(payload, encoding="utf-8")
    if public_path is not None and public_path != primary_path:
        public_path.parent.mkdir(parents=True, exist_ok=True)
        public_path.write_text(payload, encoding="utf-8")


def _append_text_mirrored(payload: str, *, primary_path: Path, public_path: Path | None) -> None:
    primary_path.parent.mkdir(parents=True, exist_ok=True)
    with primary_path.open("a", encoding="utf-8") as handle:
        handle.write(payload)
    if public_path is not None and public_path != primary_path:
        public_path.parent.mkdir(parents=True, exist_ok=True)
        with public_path.open("a", encoding="utf-8") as handle:
            handle.write(payload)


def write_release_health_heartbeat_supervisor_state(
    state: dict[str, Any],
    *,
    primary_path: Path,
    public_path: Path | None = None,
) -> None:
    _write_text_mirrored(
        json.dumps(state, indent=2, sort_keys=True),
        primary_path=primary_path,
        public_path=public_path,
    )


def append_release_health_heartbeat_supervisor_pulse(
    pulse: dict[str, Any],
    *,
    primary_path: Path,
    public_path: Path | None = None,
) -> None:
    _append_text_mirrored(
        json.dumps(pulse, sort_keys=True) + "\n",
        primary_path=primary_path,
        public_path=public_path,
    )


def load_release_health_heartbeat_supervisor_state(
    *,
    candidate_paths: list[Path],
    schema_version: str,
    surface_id: str,
    fallback_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    for path in candidate_paths:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if is_replayable_release_health_heartbeat_supervisor_state(
            record,
            schema_version=schema_version,
            surface_id=surface_id,
        ):
            return record
    return dict(fallback_state or {})


def load_release_health_heartbeat_supervisor_pulses(
    *,
    candidate_paths: list[Path],
    schema_version: str,
    surface_id: str,
    loop_schema_version: str,
    limit: int = 100,
) -> list[dict[str, Any]]:
    bounded_limit = max(0, int(limit))
    if bounded_limit == 0:
        return []

    for path in candidate_paths:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        records: list[dict[str, Any]] = []
        for line in lines:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if is_replayable_release_health_heartbeat_supervisor_pulse(
                record,
                schema_version=schema_version,
                surface_id=surface_id,
                loop_schema_version=loop_schema_version,
            ):
                records.append(record)
        if records:
            return records[-bounded_limit:]
    return []


def is_replayable_release_health_heartbeat_supervisor_state(
    record: dict[str, Any],
    *,
    schema_version: str,
    surface_id: str,
) -> bool:
    return (
        isinstance(record, dict)
        and record.get("schema_version") == schema_version
        and record.get("surface_id") == surface_id
        and record.get("raw_content_included") is False
        and record.get("active_production_mutation_allowed") is False
        and record.get("active_production_mutated") is False
        and record.get("status") in {"enabled", "disabled"}
        and isinstance(record.get("enabled"), bool)
    )


def is_replayable_release_health_heartbeat_supervisor_pulse(
    record: dict[str, Any],
    *,
    schema_version: str,
    surface_id: str,
    loop_schema_version: str,
) -> bool:
    loop = record.get("loop") if isinstance(record, dict) and isinstance(record.get("loop"), dict) else {}
    return (
        isinstance(record, dict)
        and record.get("schema_version") == schema_version
        and record.get("surface_id") == surface_id
        and record.get("raw_content_included") is False
        and record.get("active_production_mutation_allowed") is False
        and record.get("active_production_mutated") is False
        and record.get("manual_endpoint_used") is False
        and bool(record.get("pulse_id"))
        and bool(record.get("loop_id"))
        and loop.get("schema_version") == loop_schema_version
        and loop.get("raw_content_included") is False
        and loop.get("active_production_mutation_allowed") is False
        and loop.get("active_production_mutated") is False
    )

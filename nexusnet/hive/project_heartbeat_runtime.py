from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from nexusnet.hive.project_heartbeat_replay import (
    attach_native_project_heartbeat_replay,
    native_project_heartbeat_record,
)


NATIVE_PROJECT_HEARTBEAT_RUNTIME_SURFACE_ID = "hive-native-project-heartbeat-runtime-emission"


@dataclass(frozen=True)
class NativeProjectHeartbeatEmission:
    surface_id: str
    record_id: str
    artifact_path: Path | None
    heartbeat: dict[str, Any]
    replay_record: dict[str, Any]
    raw_content_included: bool = False
    active_production_mutated: bool = False


def emit_native_project_heartbeat_runtime(
    *,
    heartbeat: dict[str, Any],
    record_id: str,
    recorded_at: str,
    artifact_path: Path | None,
) -> NativeProjectHeartbeatEmission:
    replay_record = native_project_heartbeat_record(
        record_id=record_id,
        heartbeat=heartbeat,
        recorded_at=recorded_at,
    )
    attached_heartbeat = attach_native_project_heartbeat_replay(
        heartbeat,
        replay_record,
    )
    return NativeProjectHeartbeatEmission(
        surface_id=NATIVE_PROJECT_HEARTBEAT_RUNTIME_SURFACE_ID,
        record_id=record_id,
        artifact_path=artifact_path,
        heartbeat=attached_heartbeat,
        replay_record=replay_record,
    )

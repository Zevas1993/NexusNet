from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from nexusnet.hive.project_heartbeat_payload import project_heartbeat_payload
from nexusnet.hive.project_heartbeat_runtime import emit_native_project_heartbeat_runtime


NATIVE_PROJECT_HEARTBEAT_CYCLE_SURFACE_ID = "hive-native-project-heartbeat-cycle"


@dataclass(frozen=True)
class NativeProjectHeartbeatCycle:
    surface_id: str
    payload_surface_id: str
    emission_surface_id: str
    record_id: str
    artifact_path: Path | None
    heartbeat: dict[str, Any]
    replay_record: dict[str, Any]
    raw_content_included: bool = False
    active_production_mutated: bool = False


def run_native_project_heartbeat_cycle(
    *,
    heartbeat_inputs: dict[str, Any],
    record_id: str,
    recorded_at: str,
    artifact_path: Path | None,
) -> NativeProjectHeartbeatCycle:
    heartbeat = project_heartbeat_payload(**dict(heartbeat_inputs))
    emission = emit_native_project_heartbeat_runtime(
        heartbeat=heartbeat,
        record_id=record_id,
        recorded_at=recorded_at,
        artifact_path=artifact_path,
    )
    return NativeProjectHeartbeatCycle(
        surface_id=NATIVE_PROJECT_HEARTBEAT_CYCLE_SURFACE_ID,
        payload_surface_id=str(heartbeat.get("surface_id") or ""),
        emission_surface_id=emission.surface_id,
        record_id=record_id,
        artifact_path=artifact_path,
        heartbeat=emission.heartbeat,
        replay_record=emission.replay_record,
    )

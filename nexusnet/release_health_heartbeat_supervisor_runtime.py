from __future__ import annotations

from datetime import datetime, timezone
from collections.abc import Callable
from typing import Any

from nexusnet.release_health_heartbeat_supervisor_history import (
    build_release_health_heartbeat_supervisor_repair_history,
)
from nexusnet.release_health_heartbeat_supervisor_pulse import build_release_health_heartbeat_supervisor_pulse
from nexusnet.release_health_heartbeat_supervisor_state import (
    build_release_health_heartbeat_supervisor_ticked_state,
)


def _parse_supervisor_timestamp(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def release_health_heartbeat_supervisor_due_status(
    state: dict[str, Any],
    *,
    now: datetime,
) -> str:
    if not state.get("enabled"):
        return "disabled"
    parsed = _parse_supervisor_timestamp(state.get("next_due_at"))
    if parsed is None:
        return "due"
    current = now.replace(tzinfo=timezone.utc) if now.tzinfo is None else now.astimezone(timezone.utc)
    return "due" if current >= parsed else "scheduled"


def build_release_health_heartbeat_supervisor_summary(
    *,
    state: dict[str, Any],
    pulses: list[dict[str, Any]],
    repair_history: dict[str, Any],
    session_ref_digest: str | None,
    state_artifact_ref: str,
    pulse_artifact_ref: str,
    now: datetime,
) -> dict[str, Any]:
    records = [
        record
        for record in pulses
        if not session_ref_digest or str(record.get("session_ref_digest") or "") == f"sha256:{session_ref_digest}"
    ]
    latest_pulse = records[-1] if records else None
    summary = {
        **state,
        "runtime_state": "live-evidence" if records else "configured" if state.get("enabled") else "disabled",
        "next_due_status": release_health_heartbeat_supervisor_due_status(state, now=now),
        "pulse_count": len(records),
        "global_pulse_count": len(pulses),
        "latest_pulse_id": (latest_pulse or {}).get("pulse_id") or state.get("latest_pulse_id"),
        "latest_loop_id": (latest_pulse or {}).get("loop_id") or state.get("latest_loop_id"),
        "latest_pulse": latest_pulse,
        "repair_history": repair_history,
        "timer": {
            "interval_seconds": state.get("interval_seconds"),
            "next_due_at": state.get("next_due_at"),
            "last_tick_at": state.get("last_tick_at"),
            "sleep_performed": False,
            "background_thread_started": False,
            "scheduler_mode": "governed-product-path-due-tick",
        },
        "evidence_refs": [
            "/ops/wrapper/release-runtime",
            "/ops/wrapper/status-card",
            "/ops/wrapper/release-health-heartbeat/supervisor/configure",
            state_artifact_ref,
            pulse_artifact_ref,
            (latest_pulse or {}).get("loop_id"),
        ],
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
    }
    summary["evidence_refs"] = [str(ref) for ref in summary["evidence_refs"] if str(ref or "")]
    return summary


def build_release_health_heartbeat_supervisor_summary_plan(
    *,
    state: dict[str, Any],
    pulses: list[dict[str, Any]],
    readiness_runs: list[dict[str, Any]],
    session_ref_digest: str | None,
    state_artifact_ref: str,
    pulse_artifact_ref: str,
    now: datetime,
    safe_ref: Callable[[str], str],
) -> dict[str, Any]:
    current_pulses = list(pulses)
    scoped_pulses = [
        record
        for record in current_pulses
        if not session_ref_digest or str(record.get("session_ref_digest") or "") == f"sha256:{session_ref_digest}"
    ]
    repair_history = build_release_health_heartbeat_supervisor_repair_history(
        readiness_runs=readiness_runs,
        pulses=scoped_pulses,
        session_ref_digest=session_ref_digest,
        safe_ref=safe_ref,
    )
    summary = build_release_health_heartbeat_supervisor_summary(
        state=state,
        pulses=current_pulses,
        repair_history=repair_history,
        session_ref_digest=session_ref_digest,
        state_artifact_ref=state_artifact_ref,
        pulse_artifact_ref=pulse_artifact_ref,
        now=now,
    )
    return {
        "status": "assembled",
        "session_ref_digest": session_ref_digest,
        "scoped_pulse_count": len(scoped_pulses),
        "global_pulse_count": len(current_pulses),
        "scoped_pulse_ids": [
            str(record.get("pulse_id")) for record in scoped_pulses if str(record.get("pulse_id") or "")
        ],
        "repair_history": repair_history,
        "summary": summary,
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
    }


def release_health_heartbeat_supervisor_tick_settings(state: dict[str, Any]) -> dict[str, int]:
    return {
        "max_pulses": max(1, min(int(state.get("max_pulses_per_tick") or 1), 5)),
        "interval_seconds": max(1, min(int(state.get("interval_seconds") or 60), 3600)),
    }


def release_health_heartbeat_supervisor_loop_trigger(trigger: str) -> str:
    if trigger == "wrapper-interaction-periodic":
        return "periodic-wrapper-interaction-auto"
    return f"periodic-{trigger}"


def release_health_heartbeat_supervisor_pulse_id(
    *,
    generated_at: str,
    trigger: str,
    loop_id_or_index: Any,
    digest: Callable[[str], str],
) -> str:
    return f"release-health-heartbeat-supervisor-pulse::{digest(generated_at + trigger + str(loop_id_or_index))}"


def build_release_health_heartbeat_supervisor_tick_result(
    *,
    summary: dict[str, Any],
    pulse_emitted: bool,
    tick_result: str,
    emitted_pulse_count: int | None = None,
) -> dict[str, Any]:
    result = {
        **summary,
        "pulse_emitted": bool(pulse_emitted),
        "tick_result": tick_result,
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
    }
    if emitted_pulse_count is not None:
        result["emitted_pulse_count"] = max(0, int(emitted_pulse_count))
    return result


def build_release_health_heartbeat_supervisor_tick_plan(
    *,
    state: dict[str, Any],
    pulses: list[dict[str, Any]],
    repair_history: dict[str, Any],
    session_ref_digest: str | None,
    trigger: str,
    schema_version: str,
    surface_id: str,
    loop_schema_version: str,
    state_artifact_ref: str,
    pulse_artifact_ref: str,
    now: Callable[[], datetime],
    digest: Callable[[str], str],
    run_loop: Callable[[dict[str, Any]], dict[str, Any]],
) -> dict[str, Any]:
    current_pulses = list(pulses)
    due_now = now()

    if not state.get("enabled"):
        summary = build_release_health_heartbeat_supervisor_summary(
            state=state,
            pulses=current_pulses,
            repair_history=repair_history,
            session_ref_digest=session_ref_digest,
            state_artifact_ref=state_artifact_ref,
            pulse_artifact_ref=pulse_artifact_ref,
            now=due_now,
        )
        result = build_release_health_heartbeat_supervisor_tick_result(
            summary=summary,
            pulse_emitted=False,
            tick_result="disabled",
        )
        return {
            "tick_result": "disabled",
            "state": state,
            "pulses": [],
            "all_pulses": current_pulses,
            "summary": summary,
            "result": result,
            "persist_state": False,
            "persist_pulses": False,
            "persist_summary": False,
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }

    if release_health_heartbeat_supervisor_due_status(state, now=due_now) != "due":
        summary = build_release_health_heartbeat_supervisor_summary(
            state=state,
            pulses=current_pulses,
            repair_history=repair_history,
            session_ref_digest=session_ref_digest,
            state_artifact_ref=state_artifact_ref,
            pulse_artifact_ref=pulse_artifact_ref,
            now=due_now,
        )
        result = build_release_health_heartbeat_supervisor_tick_result(
            summary=summary,
            pulse_emitted=False,
            tick_result="not-due",
        )
        return {
            "tick_result": "not-due",
            "state": state,
            "pulses": [],
            "all_pulses": current_pulses,
            "summary": summary,
            "result": result,
            "persist_state": False,
            "persist_pulses": False,
            "persist_summary": False,
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }

    tick_settings = release_health_heartbeat_supervisor_tick_settings(state)
    interval_seconds = tick_settings["interval_seconds"]
    generated_loops: list[dict[str, Any]] = []
    for index in range(tick_settings["max_pulses"]):
        loop = run_loop(
            {
                "index": index,
                "trigger": release_health_heartbeat_supervisor_loop_trigger(trigger),
                "interval_seconds": interval_seconds,
            }
        )
        generated_loops.append(
            {
                "index": index,
                "generated_at": now().isoformat(),
                "loop": loop,
            }
        )

    pulse_batch = build_release_health_heartbeat_supervisor_pulse_batch(
        schema_version=schema_version,
        surface_id=surface_id,
        state_artifact_ref=state_artifact_ref,
        pulse_artifact_ref=pulse_artifact_ref,
        trigger=trigger,
        session_ref_digest=f"sha256:{session_ref_digest}" if session_ref_digest else None,
        interval_seconds=interval_seconds,
        generated_loops=generated_loops,
        digest=digest,
    )
    emitted = list(pulse_batch["pulses"])
    all_pulses = (current_pulses + emitted)[-100:]
    ticked_state = build_release_health_heartbeat_supervisor_ticked_state(
        previous_state=state,
        ticked_at=now(),
        interval_seconds=interval_seconds,
        latest_pulse=pulse_batch["latest_pulse"] or {},
    )
    summary = build_release_health_heartbeat_supervisor_summary(
        state=ticked_state,
        pulses=all_pulses,
        repair_history=repair_history,
        session_ref_digest=session_ref_digest,
        state_artifact_ref=state_artifact_ref,
        pulse_artifact_ref=pulse_artifact_ref,
        now=now(),
    )
    result = build_release_health_heartbeat_supervisor_tick_result(
        summary=summary,
        pulse_emitted=True,
        tick_result="pulsed",
        emitted_pulse_count=len(emitted),
    )
    return {
        "tick_result": "pulsed",
        "state": ticked_state,
        "pulses": emitted,
        "all_pulses": all_pulses,
        "summary": summary,
        "result": result,
        "persist_state": True,
        "persist_pulses": bool(emitted),
        "persist_summary": True,
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
        "loop_schema_version": loop_schema_version,
    }


def build_release_health_heartbeat_supervisor_pulse_batch(
    *,
    schema_version: str,
    surface_id: str,
    state_artifact_ref: str,
    pulse_artifact_ref: str,
    trigger: str,
    session_ref_digest: str | None,
    interval_seconds: int,
    generated_loops: list[dict[str, Any]],
    digest: Callable[[str], str],
) -> dict[str, Any]:
    pulses: list[dict[str, Any]] = []
    for fallback_index, generated_loop in enumerate(generated_loops):
        loop = generated_loop.get("loop") if isinstance(generated_loop.get("loop"), dict) else {}
        index = generated_loop.get("index", fallback_index)
        generated_at = str(generated_loop.get("generated_at") or "")
        loop_id_or_index = loop.get("loop_id") or index
        pulse = build_release_health_heartbeat_supervisor_pulse(
            schema_version=schema_version,
            surface_id=surface_id,
            state_artifact_ref=state_artifact_ref,
            pulse_artifact_ref=pulse_artifact_ref,
            pulse_id=release_health_heartbeat_supervisor_pulse_id(
                generated_at=generated_at,
                trigger=trigger,
                loop_id_or_index=loop_id_or_index,
                digest=digest,
            ),
            generated_at=generated_at,
            trigger=trigger,
            session_ref_digest=session_ref_digest,
            interval_seconds=interval_seconds,
            loop=loop,
        )
        pulses.append(pulse)
    return {
        "emitted_pulse_count": len(pulses),
        "pulses": pulses,
        "latest_pulse": pulses[-1] if pulses else None,
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
    }

from __future__ import annotations

import hashlib
from typing import Any

from nexus.schemas import utcnow


NATIVE_HIVE_HEARTBEAT_REQUIRED_ORGANS = (
    "neural_bus",
    "hive_blackboard",
    "plane_trace",
    "federated_learning_packet",
    "federated_prior_update",
    "runtime_growth_receipt",
    "dream_research_queue",
)


def build_native_hive_heartbeat_receipt(
    *,
    interaction: dict[str, Any],
    hive_result: dict[str, Any],
    federated_packet: dict[str, Any],
    improvement_queue_id: str | None,
) -> dict[str, Any]:
    created_at = utcnow().isoformat()
    trace_id = str(interaction.get("trace_id") or hive_result.get("run_id") or "trace")
    hive_run_id = str(hive_result.get("run_id") or "")
    neural_bus = hive_result.get("neural_bus") if isinstance(hive_result.get("neural_bus"), dict) else {}
    hive_blackboard = (
        hive_result.get("hive_blackboard")
        if isinstance(hive_result.get("hive_blackboard"), dict)
        else {}
    )
    plane_trace = hive_result.get("plane_trace") if isinstance(hive_result.get("plane_trace"), dict) else {}
    federated_prior_update = (
        hive_result.get("federated_prior_update")
        if isinstance(hive_result.get("federated_prior_update"), dict)
        else {}
    )
    runtime_growth_receipt = (
        hive_result.get("runtime_growth_receipt")
        if isinstance(hive_result.get("runtime_growth_receipt"), dict)
        else {}
    )
    organs = [
        _heartbeat_organ(
            "neural_bus",
            f"neural-bus::{_safe_ref(str(neural_bus.get('bus_id')))}" if neural_bus.get("bus_id") else None,
            blocker="neural_bus_missing",
        ),
        _heartbeat_organ(
            "hive_blackboard",
            (
                f"hive-blackboard::{_safe_ref(str(hive_blackboard.get('residual_state_id')))}"
                if hive_blackboard.get("residual_state_id")
                else None
            ),
            blocker="hive_blackboard_missing",
        ),
        _heartbeat_organ(
            "plane_trace",
            (
                f"plane-trace::{_safe_ref(str(plane_trace.get('trace_ledger_id')))}"
                if plane_trace.get("trace_ledger_id")
                else None
            ),
            blocker="plane_trace_missing",
        ),
        _heartbeat_organ(
            "federated_learning_packet",
            (
                f"federated-packet::{_safe_ref(str(federated_packet.get('packet_id')))}"
                if federated_packet.get("packet_id")
                else None
            ),
            blocker="federated_learning_packet_missing",
        ),
        _heartbeat_organ(
            "federated_prior_update",
            (
                f"federated-prior::{_safe_ref(str(federated_prior_update.get('prior_update_id')))}"
                if federated_prior_update.get("prior_update_id")
                else None
            ),
            blocker="federated_prior_update_missing",
        ),
        _heartbeat_organ(
            "runtime_growth_receipt",
            (
                f"runtime-growth-receipt::{_safe_ref(str(runtime_growth_receipt.get('receipt_id')))}"
                if runtime_growth_receipt.get("receipt_id")
                else None
            ),
            blocker="runtime_growth_receipt_missing",
        ),
        _heartbeat_organ(
            "dream_research_queue",
            (
                f"dream-research-queue::{_safe_ref(str(improvement_queue_id))}"
                if improvement_queue_id
                else None
            ),
            blocker="dream_research_queue_missing",
        ),
    ]
    covered_count = sum(1 for organ in organs if organ["status"] == "covered")
    degraded_count = len(organs) - covered_count
    blockers = [str(organ["blocker"]) for organ in organs if organ.get("blocker")]
    heartbeat_seed = "|".join(
        [
            trace_id,
            hive_run_id,
            str(interaction.get("session_ref_digest") or ""),
            created_at,
            ",".join(f"{organ['organ_id']}:{organ['status']}" for organ in organs),
        ]
    )
    return {
        "schema_version": "nexusnet-release-wrapper-native-hive-heartbeat-v1",
        "surface_id": "release-wrapper-native-hive-heartbeat",
        "heartbeat_id": f"native-hive-heartbeat::{_privacy_digest(heartbeat_seed)}",
        "created_at": created_at,
        "status": "covered" if degraded_count == 0 else "degraded",
        "session_ref_digest": interaction.get("session_ref_digest"),
        "trace_ref": f"trace::{trace_id}",
        "hive_run_ref": f"hive-forward::{hive_run_id}" if hive_run_id else None,
        "required_organs": list(NATIVE_HIVE_HEARTBEAT_REQUIRED_ORGANS),
        "organs": organs,
        "covered_count": covered_count,
        "degraded_count": degraded_count,
        "blockers": blockers,
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
        "privacy_boundary": "sanitized-native-hive-ids-counts-and-evidence-refs-only-no-raw-prompts-outputs-session-ids-or-local-paths",
        "mutation_boundary": "heartbeat-receipt-only-no-active-production-mutation",
    }


def _heartbeat_organ(organ_id: str, ref: str | None, *, blocker: str) -> dict[str, Any]:
    ref_value = str(ref or "").strip()
    covered = bool(ref_value)
    return {
        "organ_id": organ_id,
        "status": "covered" if covered else "degraded",
        "evidence_refs": [ref_value] if covered else [],
        "blocker": None if covered else blocker,
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
    }


def _privacy_digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def _safe_ref(value: str) -> str:
    return value.replace(":", "_").replace("/", "_").replace("\\", "_")


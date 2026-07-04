from __future__ import annotations

import importlib
import importlib.util


def test_native_hive_heartbeat_helper_assembles_sanitized_covered_receipt():
    spec = importlib.util.find_spec("nexusnet.release_wrapper_heartbeat")
    assert spec is not None
    build_native_hive_heartbeat_receipt = importlib.import_module(
        "nexusnet.release_wrapper_heartbeat"
    ).build_native_hive_heartbeat_receipt

    heartbeat = build_native_hive_heartbeat_receipt(
        interaction={
            "trace_id": "trace::secret",
            "session_ref_digest": "session-digest",
        },
        hive_result={
            "run_id": "hive-run-1",
            "neural_bus": {"bus_id": "bus:1"},
            "hive_blackboard": {"residual_state_id": "blackboard/1"},
            "plane_trace": {"trace_ledger_id": "plane\\1"},
            "federated_prior_update": {"prior_update_id": "prior:1"},
            "runtime_growth_receipt": {"receipt_id": "growth/1"},
        },
        federated_packet={"packet_id": "packet:1"},
        improvement_queue_id="queue/1",
    )

    assert heartbeat["surface_id"] == "release-wrapper-native-hive-heartbeat"
    assert heartbeat["schema_version"] == "nexusnet-release-wrapper-native-hive-heartbeat-v1"
    assert heartbeat["status"] == "covered"
    assert heartbeat["session_ref_digest"] == "session-digest"
    assert heartbeat["trace_ref"] == "trace::trace::secret"
    assert heartbeat["hive_run_ref"] == "hive-forward::hive-run-1"
    assert heartbeat["covered_count"] == len(heartbeat["required_organs"])
    assert heartbeat["degraded_count"] == 0
    assert heartbeat["blockers"] == []
    assert heartbeat["raw_content_included"] is False
    assert heartbeat["active_production_mutation_allowed"] is False
    assert heartbeat["active_production_mutated"] is False
    organ_refs = {
        organ["organ_id"]: organ["evidence_refs"][0]
        for organ in heartbeat["organs"]
    }
    assert organ_refs == {
        "neural_bus": "neural-bus::bus_1",
        "hive_blackboard": "hive-blackboard::blackboard_1",
        "plane_trace": "plane-trace::plane_1",
        "federated_learning_packet": "federated-packet::packet_1",
        "federated_prior_update": "federated-prior::prior_1",
        "runtime_growth_receipt": "runtime-growth-receipt::growth_1",
        "dream_research_queue": "dream-research-queue::queue_1",
    }


from __future__ import annotations

import json
from types import SimpleNamespace

from nexusnet.hive.project_heartbeat_replay import (
    PROJECT_HEARTBEAT_NATIVE_RECORD_SCHEMA,
    PROJECT_HEARTBEAT_NATIVE_RECORD_SURFACE_ID,
    PROJECT_HEARTBEAT_NATIVE_REPLAY_REF,
    attach_native_project_heartbeat_replay,
    native_project_heartbeat_record,
)


def test_native_project_heartbeat_replay_contract_is_sanitized_and_indexable():
    heartbeat = {
        "heartbeat_id": "project-heartbeat::abc",
        "status": "alive",
        "generated_at": "2026-07-03T12:00:00+00:00",
        "source_run_id": "hive_forward_123",
        "source_trace_ref": "trace::hive_forward_123",
        "session_ref_digest": "digest-only-session-ref",
        "lane_count": 1,
        "alive_lane_count": 1,
        "degraded_lane_count": 0,
        "lanes": [
            {
                "lane_id": "storage-replay",
                "status": "alive",
                "artifact_refs": [
                    "durable-storage::ledger",
                    "raw-prompt::SECRET-NATIVE-HEARTBEAT",
                ],
                "blockers": [],
            }
        ],
        "evidence_refs": ["durable-storage::ledger"],
    }

    record = native_project_heartbeat_record(
        record_id="native_project_heartbeat_123",
        heartbeat=heartbeat,
        recorded_at="2026-07-03T12:00:01+00:00",
    )
    attached = attach_native_project_heartbeat_replay(dict(heartbeat), record)

    assert record["schema_version"] == PROJECT_HEARTBEAT_NATIVE_RECORD_SCHEMA
    assert record["surface_id"] == PROJECT_HEARTBEAT_NATIVE_RECORD_SURFACE_ID
    assert record["replay_ref"] == PROJECT_HEARTBEAT_NATIVE_REPLAY_REF
    assert record["record_id"] == "native_project_heartbeat_123"
    assert record["heartbeat_id"] == heartbeat["heartbeat_id"]
    assert record["session_id"] is None
    assert record["session_ref_digest"] == "digest-only-session-ref"
    assert record["raw_content_included"] is False
    assert record["active_production_mutation_allowed"] is False
    assert record["active_production_mutated"] is False
    assert attached["native_replay_ref"] == PROJECT_HEARTBEAT_NATIVE_REPLAY_REF
    assert attached["native_replay_record_id"] == record["record_id"]
    assert record["record_id"] in attached["lanes"][0]["artifact_refs"]

    serialized = json.dumps({"record": record, "attached": attached}, sort_keys=True)
    assert "digest-only-session-ref" in serialized
    assert "session_id" in serialized
    assert "SECRET-NATIVE-HEARTBEAT" not in serialized


def test_native_project_heartbeat_runtime_emission_builds_sanitized_replay_record(tmp_path):
    from nexusnet.hive.project_heartbeat_runtime import emit_native_project_heartbeat_runtime

    heartbeat = {
        "heartbeat_id": "project-heartbeat::runtime",
        "status": "alive",
        "generated_at": "2026-07-03T12:00:00+00:00",
        "source_run_id": "hive_forward_runtime",
        "source_trace_ref": "trace::hive_forward_runtime",
        "session_ref_digest": "digest-only-session-ref",
        "lanes": [
            {
                "lane_id": "storage-replay",
                "status": "alive",
                "artifact_refs": [
                    "durable-storage::ledger",
                    "raw-output::SECRET-RUNTIME-HEARTBEAT",
                ],
                "blockers": [],
            }
        ],
        "evidence_refs": ["durable-storage::ledger", "api-key::SECRET-RUNTIME-HEARTBEAT"],
        "raw_content_included": False,
        "active_production_mutated": False,
    }

    emission = emit_native_project_heartbeat_runtime(
        heartbeat=heartbeat,
        record_id="native_project_heartbeat_runtime",
        recorded_at="2026-07-03T12:00:01+00:00",
        artifact_path=tmp_path / "native_project_heartbeat_runtime.json",
    )

    attached = emission.heartbeat
    record = emission.replay_record

    assert emission.surface_id == "hive-native-project-heartbeat-runtime-emission"
    assert emission.record_id == "native_project_heartbeat_runtime"
    assert emission.artifact_path == tmp_path / "native_project_heartbeat_runtime.json"
    assert attached["native_replay_record_id"] == record["record_id"]
    assert record["record_id"] in attached["lanes"][0]["artifact_refs"]
    assert record["session_ref_digest"] == "digest-only-session-ref"
    assert record["raw_content_included"] is False
    assert record["active_production_mutated"] is False

    serialized = json.dumps({"heartbeat": attached, "record": record}, sort_keys=True)
    assert "SECRET-RUNTIME-HEARTBEAT" not in serialized
    assert str(tmp_path) not in serialized


def test_project_heartbeat_payload_builder_is_indexable_and_sanitized():
    from nexusnet.hive.project_heartbeat_payload import project_heartbeat_payload

    node = SimpleNamespace(node_id="node::nexus-brain", node_type="NexusBrain")
    heartbeat = project_heartbeat_payload(
        run_id="run-with-private-session",
        session_id="private-session-for-heartbeat-builder",
        created_at="2026-07-03T12:00:00+00:00",
        blocked=False,
        nodes=[node],
        selected_nodes=[node],
        activation={"activation_id": "activation_1"},
        neural_bus={"bus_id": "bus_1"},
        hive_blackboard={"residual_state_id": "blackboard_1"},
        plane_trace={"trace_ledger_id": "trace_ledger_1"},
        neural_pathway_map={"pathway_id": "pathway_1"},
        synaptic_transmission_ledger={"transmission_id": "transmission_1"},
        forward_propagation_ledger={"propagation_id": "forward_1"},
        runtime_growth_receipt={"receipt_id": "growth_1"},
        runtime_growth_packet={"packet_id": "growth_packet_1"},
        federated_learning_packet={"packet_id": "federated_packet_1"},
        federated_prior_update={"prior_update_id": "prior_1"},
        federated_influence_ledger={"federated_influence_id": "influence_1"},
        executable_dream_cycle_ledger={"dream_cycle_id": "dream_1"},
        checkpoint={"checkpoint_id": "checkpoint_1"},
        checkpoint_coverage_ledger={"coverage_ledger_id": "coverage_1"},
        runtime_decision_ledger={"runtime_decision_id": "runtime_decision_1"},
        backend_quantization_execution_ledger={"backend_execution_id": "backend_1"},
        durable_storage_ledger={"storage_ledger_id": "storage_1"},
        deep_replay_drilldown_ledger={"replay_drilldown_id": "replay_1"},
        health_event={"health_event_id": "health_1"},
        self_healing_route_around=None,
        policy_scan={"summary": {"allow_merge": True}},
        immune_findings=[],
    )

    lanes = {lane["lane_id"]: lane for lane in heartbeat["lanes"]}
    assert heartbeat["schema_version"] == "nexusnet-project-heartbeat-v1"
    assert heartbeat["surface_id"] == "nexusnet-project-heartbeat"
    assert heartbeat["trigger"] == "hive-forward-pass"
    assert heartbeat["status"] == "alive"
    assert heartbeat["alive_lane_count"] == heartbeat["lane_count"] == 11
    assert heartbeat["degraded_lane_count"] == 0
    assert heartbeat["source_brain_generate_status"] == "unknown"
    assert heartbeat["source_runtime_degraded"] is False
    assert lanes["model-serving-runtime"]["status"] == "alive"
    assert lanes["model-serving-runtime"]["blockers"] == []
    assert "growth-engine" in lanes
    assert "federation-runtime" in lanes
    assert "dream-runtime" in lanes
    assert lanes["growth-engine"]["artifact_refs"] == [
        "runtime-growth::growth_1",
        "runtime-growth-packet::growth_packet_1",
    ]
    assert heartbeat["raw_content_included"] is False
    assert heartbeat["active_production_mutated"] is False

    serialized = json.dumps(heartbeat, sort_keys=True)
    assert "private-session-for-heartbeat-builder" not in serialized
    assert heartbeat["source_run_id"] == "run-with-private-session"
    assert heartbeat["source_trace_ref"] == "trace::run-with-private-session"
    assert "session_ref_digest" in serialized


def test_blocked_project_heartbeat_records_recovery_governance_without_private_content():
    from nexusnet.hive.project_heartbeat_payload import project_heartbeat_payload

    node = SimpleNamespace(node_id="node::nexus-brain", node_type="NexusBrain")
    heartbeat = project_heartbeat_payload(
        run_id="blocked-run-with-private-session",
        session_id="private-blocked-heartbeat-session",
        created_at="2026-07-03T12:00:00+00:00",
        blocked=True,
        nodes=[node],
        selected_nodes=[node],
        activation={"activation_id": "activation_1"},
        neural_bus={"bus_id": "bus_1"},
        hive_blackboard={"residual_state_id": "blackboard_1"},
        plane_trace={"trace_ledger_id": "trace_ledger_1"},
        neural_pathway_map={"pathway_id": "pathway_1"},
        synaptic_transmission_ledger={"transmission_id": "transmission_1"},
        forward_propagation_ledger={"propagation_id": "forward_1"},
        runtime_growth_receipt={"receipt_id": "growth_1"},
        runtime_growth_packet={"packet_id": "growth_packet_1"},
        federated_learning_packet={"packet_id": "federated_packet_1"},
        federated_prior_update={"prior_update_id": "prior_1"},
        federated_influence_ledger={"federated_influence_id": "influence_1"},
        executable_dream_cycle_ledger={"dream_cycle_id": "dream_1"},
        checkpoint={"checkpoint_id": "checkpoint_1"},
        checkpoint_coverage_ledger={"coverage_ledger_id": "coverage_1"},
        runtime_decision_ledger={"runtime_decision_id": "runtime_decision_1"},
        backend_quantization_execution_ledger={"backend_execution_id": "backend_1"},
        durable_storage_ledger={"storage_ledger_id": "storage_1"},
        deep_replay_drilldown_ledger={"replay_drilldown_id": "replay_1"},
        health_event={"health_event_id": "health_1"},
        self_healing_route_around={
            "route_around_id": "route_1",
            "reason": "SECRET-NATIVE-HEARTBEAT-RECOVERY",
        },
        policy_scan={"summary": {"allow_merge": False}},
        immune_findings=[{"finding_id": "finding_1", "message": "SECRET-NATIVE-HEARTBEAT-RECOVERY"}],
    )
    record = native_project_heartbeat_record(
        record_id="native_project_heartbeat_blocked",
        heartbeat=heartbeat,
        recorded_at="2026-07-03T12:00:01+00:00",
    )

    governance = heartbeat["failure_recovery_governance"]
    replay_governance = record["failure_recovery_governance"]
    assert heartbeat["status"] == "degraded"
    assert governance["surface_id"] == "native-project-heartbeat-failure-recovery-governance"
    assert governance["status"] == "degraded-recovery-governed"
    assert governance["runtime_state"] == "degraded"
    assert governance["blocked_forward_pass"] is True
    assert governance["self_healing_route_available"] is True
    assert governance["admin_governance_required"] is True
    assert governance["recovery_action"] == "route-around-and-queue-governed-repair"
    assert "route-around::route_1" in governance["evidence_refs"]
    assert replay_governance == governance
    assert replay_governance["raw_content_included"] is False
    assert replay_governance["active_production_mutated"] is False

    serialized = json.dumps({"heartbeat": heartbeat, "record": record}, sort_keys=True)
    assert "private-blocked-heartbeat-session" not in serialized
    assert "SECRET-NATIVE-HEARTBEAT-RECOVERY" not in serialized


def test_native_project_heartbeat_cycle_composes_payload_and_replay_emission(tmp_path):
    from nexusnet.hive.project_heartbeat_cycle import run_native_project_heartbeat_cycle

    node = SimpleNamespace(node_id="node::nexus-brain", node_type="NexusBrain")
    cycle = run_native_project_heartbeat_cycle(
        heartbeat_inputs={
            "run_id": "cycle-run",
            "session_id": "private-cycle-session",
            "created_at": "2026-07-03T12:00:00+00:00",
            "blocked": False,
            "nodes": [node],
            "selected_nodes": [node],
            "activation": {"activation_id": "activation_1"},
            "neural_bus": {"bus_id": "bus_1"},
            "hive_blackboard": {"residual_state_id": "blackboard_1"},
            "plane_trace": {"trace_ledger_id": "trace_ledger_1"},
            "neural_pathway_map": {"pathway_id": "pathway_1"},
            "synaptic_transmission_ledger": {"transmission_id": "transmission_1"},
            "forward_propagation_ledger": {"propagation_id": "forward_1"},
            "runtime_growth_receipt": {"receipt_id": "growth_1"},
            "runtime_growth_packet": {"packet_id": "growth_packet_1"},
            "federated_learning_packet": {"packet_id": "federated_packet_1"},
            "federated_prior_update": {"prior_update_id": "prior_1"},
            "federated_influence_ledger": {"federated_influence_id": "influence_1"},
            "executable_dream_cycle_ledger": {"dream_cycle_id": "dream_1"},
            "checkpoint": {"checkpoint_id": "checkpoint_1"},
            "checkpoint_coverage_ledger": {"coverage_ledger_id": "coverage_1"},
            "runtime_decision_ledger": {"runtime_decision_id": "runtime_decision_1"},
            "backend_quantization_execution_ledger": {"backend_execution_id": "backend_1"},
            "durable_storage_ledger": {"storage_ledger_id": "storage_1"},
            "deep_replay_drilldown_ledger": {"replay_drilldown_id": "replay_1"},
            "health_event": {"health_event_id": "health_1"},
            "self_healing_route_around": None,
            "policy_scan": {"summary": {"allow_merge": True}},
            "immune_findings": [],
        },
        record_id="native_project_heartbeat_cycle",
        recorded_at="2026-07-03T12:00:01+00:00",
        artifact_path=tmp_path / "native_project_heartbeat_cycle.json",
    )

    heartbeat = cycle.heartbeat
    replay_record = cycle.replay_record
    storage_lane = {lane["lane_id"]: lane for lane in heartbeat["lanes"]}["storage-replay"]

    assert cycle.surface_id == "hive-native-project-heartbeat-cycle"
    assert cycle.payload_surface_id == "nexusnet-project-heartbeat"
    assert cycle.emission_surface_id == "hive-native-project-heartbeat-runtime-emission"
    assert cycle.record_id == "native_project_heartbeat_cycle"
    assert cycle.artifact_path == tmp_path / "native_project_heartbeat_cycle.json"
    assert heartbeat["status"] == "alive"
    assert heartbeat["native_replay_record_id"] == replay_record["record_id"]
    assert replay_record["heartbeat_id"] == heartbeat["heartbeat_id"]
    assert replay_record["source_run_id"] == "cycle-run"
    assert replay_record["record_id"] in storage_lane["artifact_refs"]
    assert cycle.raw_content_included is False
    assert cycle.active_production_mutated is False

    serialized = json.dumps({"heartbeat": heartbeat, "replay_record": replay_record}, sort_keys=True)
    assert "private-cycle-session" not in serialized
    assert str(tmp_path) not in serialized

from __future__ import annotations

import json
import shutil
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.hive import (
    HiveAssimilationCandidateRequest,
    HiveForwardPassRequest,
    HiveNeuralSubstrate,
)
from nexusnet.hive.multi_user_growth import MultiUserGrowthCoordinator
from tests.test_nexus_phase1_foundation import make_project


def _project_with_control_panel(tmp_path: Path) -> Path:
    project_root = make_project(tmp_path)
    source_control_panel = Path(__file__).resolve().parents[1] / "ui" / "control-panel"
    shutil.copytree(source_control_panel, project_root / "ui" / "control-panel")
    return project_root


def test_hive_neural_substrate_forward_pass_creates_sparse_recurrent_trace(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="hive-forward-session",
            task_id="build-v0-substrate",
            intent="Plan a governed hive substrate implementation from the approved canon.",
            source_ref="docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md",
            requested_capabilities=["planning", "memory", "evaluation", "checkpoint"],
            memory_refs=["docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md"],
            requested_actions=[{"action_id": "inspect-canon", "action_type": "read", "target_ref": "docs"}],
            max_loops=3,
        )
    )

    assert result["status_label"] == "LOCKED CANON"
    assert result["surface_id"] == "hive-neural-substrate-v0"
    assert result["lifecycle_state"] == "completed"
    assert result["activation"]["activation_id"].startswith("hive_activation_")
    assert result["trace"]["plane_count"] == 16
    assert result["route_decision"]["sparse_top_k"] <= 4
    assert result["route_decision"]["selected_node_ids"]
    assert result["loop_summary"]["loop_count"] >= 1
    assert result["loop_summary"]["exit_reason"] in {"confidence_above_threshold", "max_loops_reached"}
    assert result["checkpoint"]["checkpoint_id"].startswith("hive_checkpoint_")
    assert result["policy_scan"]["summary"]["allow_merge"] is True
    assert {"task.received", "activation.embedded", "router.experts_selected", "checkpoint.created", "eval.completed", "hive.completed"}.issubset(
        {event["event_type"] for event in result["events"]}
    )
    assert Path(result["artifact_path"]).exists()

    summary = substrate.summary(session_id="hive-forward-session")
    assert summary["runtime_state"] == "live-bound"
    assert summary["latest_forward_pass"]["run_id"] == result["run_id"]
    assert summary["plane_count"] == 16
    assert summary["node_count"] >= 8
    assert summary["operator_actions"]["forward_pass"]["endpoint"] == "/ops/brain/hive-substrate/forward-pass"
    assert summary["neuroplasticity_fabric"]["ownership_model"] == "shared-capability-not-owned-by-single-lane"
    assert summary["neuroplasticity_fabric"]["dream_protocol"]["dreamer_temperature"] == "high"
    assert summary["neuroplasticity_fabric"]["dream_protocol"]["reviewer_temperature"] == "low"
    assert summary["brain_hierarchy"]["hierarchy_model"] == "scale-gradient-not-isolation-boundary"
    assert summary["brain_hierarchy"]["brain_scale_counts"]["primary"] == 1
    assert summary["brain_hierarchy"]["brain_scale_counts"]["orchestrator"] >= 1
    assert summary["brain_hierarchy"]["brain_scale_counts"]["assistant_orchestrator"] >= 1
    assert summary["brain_hierarchy"]["brain_scale_counts"]["expert"] >= 1
    assert summary["failure_continuity"]["trace_requirement"] == "no_silent_failure_of_brain_bearing_node"
    assert result["route_decision"]["connectivity_model"] == "hive-wide-visible-sparse-activation"
    assert result["failure_continuity"]["route_around_available"] is True
    scorecard = substrate.scorecard(session_id="hive-forward-session")
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-035" in scorecard[
        "source_documents"
    ]
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-036" in scorecard[
        "source_documents"
    ]
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-037" in scorecard[
        "source_documents"
    ]
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-038" in scorecard[
        "source_documents"
    ]
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-039" in scorecard[
        "source_documents"
    ]
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-040" in scorecard[
        "source_documents"
    ]
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-041" in scorecard[
        "source_documents"
    ]
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-042" in scorecard[
        "source_documents"
    ]
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-043" in scorecard[
        "source_documents"
    ]
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-044" in scorecard[
        "source_documents"
    ]
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-045" in scorecard[
        "source_documents"
    ]
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-046" in scorecard[
        "source_documents"
    ]
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-047" in scorecard[
        "source_documents"
    ]
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-048" in scorecard[
        "source_documents"
    ]
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-049" in scorecard[
        "source_documents"
    ]
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-050" in scorecard[
        "source_documents"
    ]
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-051" in scorecard[
        "source_documents"
    ]
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-052" in scorecard[
        "source_documents"
    ]


def test_hive_artifact_summary_cache_reuses_reads_and_invalidates_after_forward_pass(tmp_path: Path, monkeypatch):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)
    first = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="artifact-cache-session",
            task_id="artifact-cache-first",
            intent="Record the first cached hive forward pass.",
        )
    )
    original_read_text = Path.read_text
    artifact_reads: list[Path] = []

    def counted_read_text(path: Path, *args, **kwargs):
        if path.suffix == ".json" and tmp_path in path.parents:
            artifact_reads.append(path)
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", counted_read_text)

    first_summary = substrate.summary(session_id="artifact-cache-session")
    first_read_count = len(artifact_reads)
    second_summary = substrate.summary(session_id="artifact-cache-session")

    assert first_summary["latest_forward_pass"]["run_id"] == first["run_id"]
    assert second_summary["latest_forward_pass"]["run_id"] == first["run_id"]
    assert first_read_count > 0
    assert len(artifact_reads) == first_read_count

    second = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="artifact-cache-session",
            task_id="artifact-cache-second",
            intent="Record the second cached hive forward pass.",
        )
    )
    refreshed_summary = substrate.summary(session_id="artifact-cache-session")

    assert len(artifact_reads) > first_read_count
    assert refreshed_summary["latest_forward_pass"]["run_id"] == second["run_id"]
    assert refreshed_summary["runtime_growth"]["runtime_interaction_count"] >= 2


def test_hive_forward_pass_emits_project_heartbeat_from_core_organs(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)
    session_id = "project-heartbeat-session"
    prompt = "Make the NexusNet heart beat without leaking SECRET-PROJECT-HEARTBEAT."

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id=session_id,
            task_id="project-heartbeat",
            intent=prompt,
            source_ref="operator::project-heartbeat-test",
            requested_capabilities=[
                "planning",
                "runtime",
                "memory",
                "evaluation",
                "checkpoint",
                "federation",
                "dreaming",
            ],
            memory_refs=["memory::canon"],
            requested_actions=[
                {"action_id": "inspect-heart", "action_type": "read", "target_ref": "hive-heartbeat"}
            ],
            max_loops=3,
        )
    )

    heartbeat = result["project_heartbeat"]
    lanes = {lane["lane_id"]: lane for lane in heartbeat["lanes"]}

    assert heartbeat["schema_version"] == "nexusnet-project-heartbeat-v1"
    assert heartbeat["surface_id"] == "nexusnet-project-heartbeat"
    assert heartbeat["trigger"] == "hive-forward-pass"
    assert heartbeat["status"] == "alive"
    assert heartbeat["honest_status_label"] == "core-substrate-heartbeat-alive"
    assert heartbeat["source_run_id"] == result["run_id"]
    assert heartbeat["source_trace_ref"] == f"trace::{result['run_id']}"
    assert heartbeat["source_brain_generate_status"] == "unknown"
    assert heartbeat["source_runtime_degraded"] is False
    assert heartbeat["lane_count"] == len(heartbeat["lanes"])
    assert heartbeat["alive_lane_count"] == heartbeat["lane_count"]
    assert heartbeat["degraded_lane_count"] == 0
    assert heartbeat["raw_content_included"] is False
    assert heartbeat["active_production_mutation_allowed"] is False
    assert heartbeat["active_production_mutated"] is False
    assert heartbeat["mutation_boundary"] == "heartbeat-status-and-artifact-refs-only-no-active-production-mutation"
    assert {
        "nexus-brain",
        "native-hive-substrate",
        "neural-signal-path",
        "growth-engine",
        "federation-runtime",
        "dream-runtime",
        "checkpoint-rewind",
        "runtime-decision",
        "storage-replay",
        "policy-immune",
    }.issubset(lanes)
    assert all(lane["status"] == "alive" for lane in lanes.values())
    assert all(lane["raw_content_included"] is False for lane in lanes.values())
    assert all(lane["active_production_mutation_allowed"] is False for lane in lanes.values())
    assert lanes["model-serving-runtime"]["status"] == "alive"
    assert lanes["model-serving-runtime"]["blockers"] == []
    assert lanes["growth-engine"]["artifact_refs"]
    assert lanes["federation-runtime"]["artifact_refs"]
    assert lanes["dream-runtime"]["artifact_refs"]
    assert heartbeat["native_replay_ref"] == "hive-substrate/project-heartbeats/_index.jsonl"
    assert heartbeat["native_replay_record_id"]
    assert heartbeat["native_replay_record_id"] in lanes["storage-replay"]["artifact_refs"]
    assert heartbeat["native_replay_ref"] in heartbeat["evidence_refs"]

    native_record = result["project_heartbeat_replay_record"]
    assert native_record["schema_version"] == "nexusnet-native-project-heartbeat-record-v1"
    assert native_record["surface_id"] == "hive-native-project-heartbeat-record"
    assert native_record["record_id"] == heartbeat["native_replay_record_id"]
    assert native_record["heartbeat_id"] == heartbeat["heartbeat_id"]
    assert native_record["source_run_id"] == result["run_id"]
    assert native_record["replay_ref"] == heartbeat["native_replay_ref"]
    assert native_record["session_ref_digest"] == heartbeat["session_ref_digest"]
    assert native_record["source_brain_generate_status"] == "unknown"
    assert native_record["source_runtime_degraded"] is False
    assert native_record["raw_content_included"] is False
    assert native_record["active_production_mutation_allowed"] is False
    assert native_record["active_production_mutated"] is False

    native_record_path = (
        tmp_path / "hive" / "substrate" / "project-heartbeats" / f"{native_record['record_id']}.json"
    )
    assert native_record_path.is_file()
    persisted_native_record = json.loads(native_record_path.read_text(encoding="utf-8"))
    assert persisted_native_record["record_id"] == native_record["record_id"]
    assert persisted_native_record["heartbeat_id"] == heartbeat["heartbeat_id"]

    summary = substrate.summary(session_id=session_id)
    replay = substrate.replay(session_id=session_id)
    health = substrate.health(session_id=session_id)

    assert summary["project_heartbeat"]["heartbeat_id"] == heartbeat["heartbeat_id"]
    assert summary["project_heartbeat"]["status"] == "alive"
    assert summary["project_heartbeat_ledger"]["latest_record_id"] == native_record["record_id"]
    assert summary["artifact_store"]["project_heartbeat_index_path"].endswith(
        "hive\\substrate\\project-heartbeats\\_index.jsonl"
    ) or summary["artifact_store"]["project_heartbeat_index_path"].endswith(
        "hive/substrate/project-heartbeats/_index.jsonl"
    )
    assert replay["project_heartbeat_chain"][0]["heartbeat_id"] == heartbeat["heartbeat_id"]
    assert replay["project_heartbeat_chain"][0]["record_id"] == native_record["record_id"]
    assert replay["project_heartbeat_replay_chain"][0]["record_id"] == native_record["record_id"]
    assert "project_heartbeat_chain" in replay["control_panel_replay"]["available_chains"]
    assert "project_heartbeat_replay_chain" in replay["control_panel_replay"]["available_chains"]
    assert replay["control_panel_replay"]["chain_counts"]["project_heartbeat_replay_chain"] == 1
    assert health["project_heartbeat"]["heartbeat_id"] == heartbeat["heartbeat_id"]

    serialized = json.dumps(
        {
            "heartbeat": heartbeat,
            "summary": summary["project_heartbeat"],
            "replay": replay["project_heartbeat_chain"],
            "native_record": native_record,
            "health": health["project_heartbeat"],
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-PROJECT-HEARTBEAT" not in serialized
    assert session_id not in serialized
    assert str(tmp_path) not in serialized


def test_hive_substrate_api_exposes_project_heartbeat_from_forward_pass(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    session_id = "api-project-heartbeat-session"
    prompt = "Expose the project heartbeat through the brain API without SECRET-API-HEARTBEAT."

    response = client.post(
        "/ops/brain/hive-substrate/forward-pass",
        json={
            "session_id": session_id,
            "task_id": "api-project-heartbeat",
            "intent": prompt,
            "source_ref": "operator::api-project-heartbeat-test",
            "requested_capabilities": ["runtime", "memory", "evaluation", "federation", "dreaming"],
            "memory_refs": ["memory::canon"],
            "requested_actions": [
                {"action_id": "inspect-api-heartbeat", "action_type": "read", "target_ref": "hive-heartbeat"}
            ],
            "max_loops": 2,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    summary = client.get("/ops/brain/hive-substrate", params={"session_id": session_id}).json()
    replay = client.get("/ops/brain/hive-substrate/replay", params={"session_id": session_id}).json()
    health = client.get("/ops/brain/hive-substrate/health", params={"session_id": session_id}).json()

    heartbeat = payload["project_heartbeat"]
    assert heartbeat["status"] == "alive"
    assert heartbeat["source_run_id"] == payload["run_id"]
    assert heartbeat["native_replay_ref"] == "hive-substrate/project-heartbeats/_index.jsonl"
    assert heartbeat["native_replay_record_id"]
    assert payload["project_heartbeat_replay_record"]["record_id"] == heartbeat["native_replay_record_id"]
    assert summary["project_heartbeat"]["heartbeat_id"] == heartbeat["heartbeat_id"]
    assert replay["project_heartbeat_chain"][0]["heartbeat_id"] == heartbeat["heartbeat_id"]
    assert replay["project_heartbeat_chain"][0]["record_id"] == heartbeat["native_replay_record_id"]
    assert replay["project_heartbeat_replay_chain"][0]["record_id"] == heartbeat["native_replay_record_id"]
    assert health["project_heartbeat"]["heartbeat_id"] == heartbeat["heartbeat_id"]
    assert replay["control_panel_replay"]["chain_counts"]["project_heartbeat_chain"] == 1
    assert replay["control_panel_replay"]["chain_counts"]["project_heartbeat_replay_chain"] == 1

    serialized = json.dumps(
        {
            "heartbeat": heartbeat,
            "summary": summary["project_heartbeat"],
            "replay": replay["project_heartbeat_chain"],
            "native_record": payload["project_heartbeat_replay_record"],
            "health": health["project_heartbeat"],
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-API-HEARTBEAT" not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized


def test_hive_substrate_api_forward_pass_delivers_sanitized_packet_to_approved_peer(tmp_path: Path):
    received_payloads: list[dict] = []

    class _PeerImportHandler(BaseHTTPRequestHandler):
        def do_POST(self):  # noqa: N802 - HTTP handler contract
            body = self.rfile.read(int(self.headers.get("Content-Length") or "0"))
            received_payloads.append(json.loads(body.decode("utf-8")))
            response = json.dumps(
                {
                    "status": "quarantined-shadow-accepted",
                    "import_id": "remote-direct-hive-import::accepted",
                    "raw_content_included": False,
                    "contains_personal_data": False,
                }
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)

        def log_message(self, _format: str, *_args: object) -> None:
            return None

    peer_server = ThreadingHTTPServer(("127.0.0.1", 0), _PeerImportHandler)
    peer_thread = threading.Thread(target=peer_server.serve_forever, daemon=True)
    peer_thread.start()
    try:
        project_root = make_project(tmp_path)
        client = TestClient(create_app(str(project_root)))
        session_id = "api-direct-hive-federation-private-session-SECRET"
        prompt = "Direct Hive federation SECRET-DIRECT-HIVE must remain sanitized."
        peer_node_id = "peer-direct-hive-approved-delivery"
        import_url = (
            f"http://127.0.0.1:{peer_server.server_port}"
            "/ops/wrapper/federated-packets/import"
        )

        approval = client.post(
            "/ops/approvals",
            json={
                "subject": "release-wrapper-federated-peer-delivery",
                "decision": "approved",
                "approver": "operator@example.invalid",
                "rationale": "Approve sanitized direct Hive API federation delivery.",
                "metadata": {"peer_node_id": peer_node_id, "import_url": import_url},
            },
        )
        assert approval.status_code == 200
        assert client.post(
            "/ops/wrapper/federated-peers",
            json={
                "peer_node_id": peer_node_id,
                "import_url": import_url,
                "approval_decision_id": approval.json()["decision_id"],
            },
        ).status_code == 200

        response = client.post(
            "/ops/brain/hive-substrate/forward-pass",
            json={
                "session_id": session_id,
                "task_id": "api-direct-hive-federation",
                "intent": prompt,
                "source_ref": "operator::direct-hive-federation",
                "requested_capabilities": ["runtime", "memory", "federation"],
                "requested_actions": [
                    {"action_id": "inspect-direct-hive", "action_type": "read", "target_ref": "hive"}
                ],
                "max_loops": 2,
            },
        )

        assert response.status_code == 200
        payload = response.json()
        delivery = payload["native_federated_peer_delivery"]
        assert delivery["status"] == "live-shadow-delivery-active"
        assert delivery["delivery_count"] == 1
        assert delivery["packet_ref"].startswith("federated-packet::")
        assert delivery["privacy_consent_record_id"]
        assert delivery["raw_content_included"] is False
        assert delivery["contains_personal_data"] is False
        assert len(received_payloads) == 1
        assert received_payloads[0]["peer_node_id"] == peer_node_id
        assert received_payloads[0]["packet"]["raw_content_included"] is False
        assert received_payloads[0]["packet"]["contains_personal_data"] is False
        assert received_payloads[0]["packet"]["consent_policy"]["sanitized_metadata_federation_allowed"] is True

        deliveries = client.get(
            "/ops/wrapper/federated-deliveries", params={"session_id": session_id}
        ).json()
        assert deliveries["acknowledged_delivery_count"] == 1
        assert deliveries["latest_delivery"]["status"] == "acknowledged-shadow-accepted"

        replayed = TestClient(create_app(str(project_root))).get(
            "/ops/wrapper/federated-deliveries", params={"session_id": session_id}
        ).json()
        assert replayed["replay"]["status"] == "replayed"
        assert replayed["acknowledged_delivery_count"] == 1

        serialized = json.dumps(
            {"delivery": delivery, "deliveries": deliveries, "replayed": replayed},
            sort_keys=True,
        )
        assert prompt not in serialized
        assert "SECRET-DIRECT-HIVE" not in serialized
        assert session_id not in serialized
        assert peer_node_id not in serialized
        assert import_url not in serialized
    finally:
        peer_server.shutdown()
        peer_server.server_close()
        peer_thread.join(timeout=5)


def test_hive_forward_pass_emits_first_class_neural_pathway_map(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="neural-pathway-session",
            task_id="pathway-map",
            intent="Execute the hive neural network pathway stack across mini brains and feedback loops.",
            source_ref="docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md",
            requested_capabilities=[
                "planning",
                "routing",
                "memory",
                "evaluation",
                "checkpoint",
                "dreaming",
                "federation",
            ],
            memory_refs=["memory::canon", "memory::runtime-prior"],
            requested_actions=[
                {"action_id": "inspect-pathways", "action_type": "read", "target_ref": "hive-pathway-map"},
                {"action_id": "evaluate-pathways", "action_type": "read", "target_ref": "eval-ledger"},
            ],
            max_loops=4,
        )
    )

    pathway_map = result["neural_pathway_map"]
    assert pathway_map["surface_id"] == "hive-neural-pathway-map-v0"
    assert pathway_map["contract_id"] == "hive-neural-pathway-map-v0"
    assert pathway_map["activation_ref"] == result["activation"]["activation_id"]
    assert pathway_map["neural_bus_ref"] == result["neural_bus"]["bus_id"]
    assert pathway_map["hive_blackboard_ref"] == result["hive_blackboard"]["residual_state_id"]
    assert pathway_map["checkpoint_ref"] == result["checkpoint"]["checkpoint_id"]
    assert pathway_map["trace_ledger_ref"] == result["plane_trace"]["trace_ledger_id"]
    assert pathway_map["connectivity_summary"]["visibility_model"] == "hive-wide-visible-sparse-activation"
    assert pathway_map["connectivity_summary"]["fully_connected_visibility"] is True
    assert pathway_map["connectivity_summary"]["sparse_activation"] is True
    assert pathway_map["connectivity_summary"]["direct_local_state_reads"] == []
    assert pathway_map["connectivity_summary"]["active_production_mutated"] is False
    assert pathway_map["brain_scale_stack"][0]["brain_scale"] == "primary"
    assert {item["brain_scale"] for item in pathway_map["brain_scale_stack"]}.issuperset(
        {"orchestrator", "assistant_orchestrator", "expert"}
    )
    assert any(edge["edge_kind"] == "synapse" for edge in pathway_map["plane_pathways"])
    assert any(edge["edge_kind"] == "residual" for edge in pathway_map["plane_pathways"])
    assert any(edge["edge_kind"] == "axon" for edge in pathway_map["node_pathways"])
    assert any(edge["edge_kind"] == "feedback" for edge in pathway_map["feedback_pathways"])
    assert pathway_map["recurrent_pathways"][0]["loop_index"] == 1
    assert pathway_map["artifact_path"] and Path(pathway_map["artifact_path"]).exists()

    runtime = result["downstream_node_runtime"]
    assert runtime["artifact_refs"]["neural_pathway_ref"] == pathway_map["pathway_id"]
    assert runtime["artifact_refs"]["synaptic_transmission_ref"] == result["synaptic_transmission_ledger"]["transmission_id"]
    assert runtime["input_contract"] == (
        "neural-bus-blackboard-sensory-temporal-memory-embedding-attention-normalization-gate-feedforward-"
        "microcircuit-pathway-transmission-plasticity-neuromodulator-latent-loop-kv-cache-backprop-"
        "optimizer-school-ledger-only"
    )
    assert all(
        pathway_map["pathway_id"] in receipt["source_artifact_refs"]
        for receipt in runtime["receipts"]
    )

    replay = substrate.replay(session_id="neural-pathway-session")
    assert replay["neural_pathway_chain"][0]["pathway_id"] == pathway_map["pathway_id"]
    assert "neural_pathway_chain" in replay["control_panel_replay"]["available_chains"]
    assert replay["control_panel_replay"]["chain_counts"]["neural_pathway_chain"] == 1

    summary = substrate.summary(session_id="neural-pathway-session")
    assert summary["neural_pathway_ledger"]["pathway_count"] == 1
    assert summary["latest_neural_pathway"]["pathway_id"] == pathway_map["pathway_id"]
    scorecard = substrate.scorecard(session_id="neural-pathway-session")
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-054" in scorecard[
        "source_documents"
    ]
    component_ids = {component["component_id"] for component in scorecard["substrate_components"]}
    assert "HiveNeuralPathwayMap" in component_ids


def test_hive_forward_pass_propagates_synaptic_transmission_through_pathways(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="synaptic-transmission-session",
            task_id="signal-propagation",
            intent="Propagate live hive signals through planes, mini brains, recurrent loops, and immune gates.",
            requested_capabilities=["planning", "runtime", "memory", "evaluation", "checkpoint", "federation"],
            memory_refs=["memory::signal-prior"],
            requested_actions=[
                {"action_id": "inspect-signal-ledger", "action_type": "read", "target_ref": "synaptic-ledger"}
            ],
            max_loops=3,
        )
    )

    pathway_map = result["neural_pathway_map"]
    transmission = result["synaptic_transmission_ledger"]
    assert transmission["surface_id"] == "hive-synaptic-transmission-ledger-v0"
    assert transmission["contract_id"] == "hive-synaptic-transmission-ledger-v0"
    assert transmission["pathway_ref"] == pathway_map["pathway_id"]
    assert transmission["activation_ref"] == result["activation"]["activation_id"]
    assert transmission["neural_bus_ref"] == result["neural_bus"]["bus_id"]
    assert transmission["hive_blackboard_ref"] == result["hive_blackboard"]["residual_state_id"]
    assert transmission["checkpoint_ref"] == result["checkpoint"]["checkpoint_id"]
    assert transmission["plane_signal_count"] == len(pathway_map["plane_pathways"])
    assert transmission["node_signal_count"] == len(pathway_map["node_pathways"])
    assert transmission["recurrent_signal_count"] == len(result["loop_summary"]["loops"])
    assert transmission["feedback_signal_count"] >= 4
    assert transmission["signal_integrity"]["direct_local_state_reads"] == []
    assert transmission["signal_integrity"]["active_production_mutated"] is False
    assert transmission["signal_integrity"]["bounded_signal_strengths"] is True
    assert all(0 <= signal["signal_strength"] <= 1 for signal in transmission["plane_signals"])
    assert any(signal["signal_kind"] == "synaptic-plane" for signal in transmission["plane_signals"])
    assert any(signal["brain_scale"] == "expert" for signal in transmission["node_signals"])
    assert any(signal["activation_state"] == "sparse-active" for signal in transmission["node_signals"])
    assert any(signal["signal_kind"] == "dream-feedback" for signal in transmission["feedback_signals"])
    assert transmission["immune_gate_signal"]["gate_state"] == "open"
    assert transmission["artifact_path"] and Path(transmission["artifact_path"]).exists()

    runtime = result["downstream_node_runtime"]
    assert runtime["artifact_refs"]["synaptic_transmission_ref"] == transmission["transmission_id"]
    assert runtime["input_contract"] == (
        "neural-bus-blackboard-sensory-temporal-memory-embedding-attention-normalization-gate-feedforward-"
        "microcircuit-pathway-transmission-plasticity-neuromodulator-latent-loop-kv-cache-backprop-"
        "optimizer-school-ledger-only"
    )
    assert all(
        transmission["transmission_id"] in receipt["source_artifact_refs"]
        for receipt in runtime["receipts"]
    )

    replay = substrate.replay(session_id="synaptic-transmission-session")
    assert replay["synaptic_transmission_chain"][0]["transmission_id"] == transmission["transmission_id"]
    assert "synaptic_transmission_chain" in replay["control_panel_replay"]["available_chains"]
    assert replay["control_panel_replay"]["chain_counts"]["synaptic_transmission_chain"] == 1

    summary = substrate.summary(session_id="synaptic-transmission-session")
    assert summary["synaptic_transmission_ledger"]["transmission_count"] == 1
    assert summary["latest_synaptic_transmission"]["transmission_id"] == transmission["transmission_id"]
    scorecard = substrate.scorecard(session_id="synaptic-transmission-session")
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-055" in scorecard[
        "source_documents"
    ]
    component_ids = {component["component_id"] for component in scorecard["substrate_components"]}
    assert "HiveSynapticTransmissionLedger" in component_ids


def test_hive_forward_pass_updates_neuroplastic_weights_in_shadow_from_synaptic_signals(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="neuroplastic-weight-session",
            task_id="shadow-weight-update",
            intent="Learn shadow routing weights from hive-wide synaptic signals without mutating production.",
            requested_capabilities=[
                "planning",
                "runtime",
                "memory",
                "evaluation",
                "checkpoint",
                "federation",
                "dreaming",
            ],
            memory_refs=["memory::plasticity-prior"],
            requested_actions=[
                {"action_id": "inspect-neuroplastic-weights", "action_type": "read", "target_ref": "weight-ledger"}
            ],
            max_loops=3,
        )
    )

    transmission = result["synaptic_transmission_ledger"]
    plasticity = result["neuroplastic_weight_ledger"]
    assert plasticity["surface_id"] == "hive-neuroplastic-weight-ledger-v0"
    assert plasticity["contract_id"] == "hive-neuroplastic-weight-ledger-v0"
    assert plasticity["transmission_ref"] == transmission["transmission_id"]
    assert plasticity["pathway_ref"] == result["neural_pathway_map"]["pathway_id"]
    assert plasticity["activation_ref"] == result["activation"]["activation_id"]
    assert plasticity["neural_bus_ref"] == result["neural_bus"]["bus_id"]
    assert plasticity["hive_blackboard_ref"] == result["hive_blackboard"]["residual_state_id"]
    assert plasticity["checkpoint_ref"] == result["checkpoint"]["checkpoint_id"]
    assert plasticity["plane_weight_count"] == transmission["plane_signal_count"]
    assert plasticity["node_weight_count"] == transmission["node_signal_count"]
    assert plasticity["feedback_weight_count"] == transmission["feedback_signal_count"]
    assert plasticity["plasticity_rule"]["learning_scope"] == "shadow-only"
    assert plasticity["plasticity_rule"]["hebbian_like_delta"] == "delta = clamp((signal_strength - 0.5) * 0.05)"
    assert plasticity["plasticity_integrity"]["direct_local_state_reads"] == []
    assert plasticity["plasticity_integrity"]["active_production_mutated"] is False
    assert plasticity["plasticity_integrity"]["bounded_weight_deltas"] is True
    assert plasticity["plasticity_integrity"]["raw_private_content_encoded"] is False
    assert all(-0.05 <= update["delta"] <= 0.05 for update in plasticity["plane_weight_updates"])
    assert all(-0.05 <= update["delta"] <= 0.05 for update in plasticity["node_weight_updates"])
    assert any(update["brain_scale"] == "expert" for update in plasticity["node_weight_updates"])
    assert any(trace["trace_strength"] > 0 for trace in plasticity["eligibility_traces"])
    assert plasticity["promotion_gate"]["promotion_state"] == "shadow_only_pending_eval_sandbox_governance"
    assert plasticity["artifact_path"] and Path(plasticity["artifact_path"]).exists()

    runtime = result["downstream_node_runtime"]
    assert runtime["artifact_refs"]["neuroplastic_weight_ref"] == plasticity["weight_ledger_id"]
    assert runtime["input_contract"] == (
        "neural-bus-blackboard-sensory-temporal-memory-embedding-attention-normalization-gate-feedforward-"
        "microcircuit-pathway-transmission-plasticity-neuromodulator-latent-loop-kv-cache-backprop-"
        "optimizer-school-ledger-only"
    )
    assert all(plasticity["weight_ledger_id"] in receipt["source_artifact_refs"] for receipt in runtime["receipts"])

    replay = substrate.replay(session_id="neuroplastic-weight-session")
    assert replay["neuroplastic_weight_chain"][0]["weight_ledger_id"] == plasticity["weight_ledger_id"]
    assert "neuroplastic_weight_chain" in replay["control_panel_replay"]["available_chains"]
    assert replay["control_panel_replay"]["chain_counts"]["neuroplastic_weight_chain"] == 1

    summary = substrate.summary(session_id="neuroplastic-weight-session")
    assert summary["neuroplastic_weight_ledger"]["weight_update_count"] == 1
    assert summary["latest_neuroplastic_weight"]["weight_ledger_id"] == plasticity["weight_ledger_id"]
    scorecard = substrate.scorecard(session_id="neuroplastic-weight-session")
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-056" in scorecard[
        "source_documents"
    ]
    component_ids = {component["component_id"] for component in scorecard["substrate_components"]}
    assert "HiveNeuroplasticWeightLedger" in component_ids


def test_hive_forward_pass_models_laminar_microcircuits_inside_each_plane(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="laminar-microcircuit-session",
            task_id="plane-microcircuits",
            intent="Expose the internal neural microcircuit structure for every cognitive plane.",
            requested_capabilities=["planning", "runtime", "memory", "evaluation", "checkpoint", "federation"],
            memory_refs=["memory::laminar-plane-prior"],
            requested_actions=[
                {"action_id": "inspect-plane-microcircuits", "action_type": "read", "target_ref": "microcircuit-ledger"}
            ],
            max_loops=2,
        )
    )

    microcircuits = result["laminar_microcircuit_ledger"]
    assert microcircuits["surface_id"] == "hive-laminar-microcircuit-ledger-v0"
    assert microcircuits["contract_id"] == "hive-laminar-microcircuit-ledger-v0"
    assert microcircuits["activation_ref"] == result["activation"]["activation_id"]
    assert microcircuits["neural_bus_ref"] == result["neural_bus"]["bus_id"]
    assert microcircuits["hive_blackboard_ref"] == result["hive_blackboard"]["residual_state_id"]
    assert microcircuits["checkpoint_ref"] == result["checkpoint"]["checkpoint_id"]
    assert microcircuits["trace_ledger_ref"] == result["plane_trace"]["trace_ledger_id"]
    assert microcircuits["plane_microcircuit_count"] == len(result["plane_trace"]["records"])
    assert microcircuits["microcircuit_integrity"]["direct_local_state_reads"] == []
    assert microcircuits["microcircuit_integrity"]["active_production_mutated"] is False
    assert microcircuits["microcircuit_integrity"]["raw_private_content_encoded"] is False
    assert microcircuits["microcircuit_integrity"]["event_driven_updates"] is True
    assert all(
        {layer["layer_id"] for layer in circuit["laminar_layers"]} == {"L1", "L2_3", "L4", "L5_6"}
        for circuit in microcircuits["plane_microcircuits"]
    )
    assert all(circuit["population_balance"]["excitatory_ratio"] == 0.8 for circuit in microcircuits["plane_microcircuits"])
    assert all(circuit["population_balance"]["inhibitory_ratio"] == 0.2 for circuit in microcircuits["plane_microcircuits"])
    assert any(
        compartment["compartment_id"] == "apical-context"
        for circuit in microcircuits["plane_microcircuits"]
        for compartment in circuit["dendritic_compartments"]
    )
    assert all(0 <= circuit["event_threshold"] <= 1 for circuit in microcircuits["plane_microcircuits"])
    assert microcircuits["artifact_path"] and Path(microcircuits["artifact_path"]).exists()

    runtime = result["downstream_node_runtime"]
    assert runtime["artifact_refs"]["laminar_microcircuit_ref"] == microcircuits["microcircuit_id"]
    assert runtime["input_contract"] == (
        "neural-bus-blackboard-sensory-temporal-memory-embedding-attention-normalization-gate-feedforward-"
        "microcircuit-pathway-transmission-plasticity-neuromodulator-latent-loop-kv-cache-backprop-"
        "optimizer-school-ledger-only"
    )
    assert all(microcircuits["microcircuit_id"] in receipt["source_artifact_refs"] for receipt in runtime["receipts"])

    replay = substrate.replay(session_id="laminar-microcircuit-session")
    assert replay["laminar_microcircuit_chain"][0]["microcircuit_id"] == microcircuits["microcircuit_id"]
    assert "laminar_microcircuit_chain" in replay["control_panel_replay"]["available_chains"]
    assert replay["control_panel_replay"]["chain_counts"]["laminar_microcircuit_chain"] == 1

    summary = substrate.summary(session_id="laminar-microcircuit-session")
    assert summary["laminar_microcircuit_ledger"]["microcircuit_count"] == 1
    assert summary["latest_laminar_microcircuit"]["microcircuit_id"] == microcircuits["microcircuit_id"]
    scorecard = substrate.scorecard(session_id="laminar-microcircuit-session")
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-057" in scorecard[
        "source_documents"
    ]
    component_ids = {component["component_id"] for component in scorecard["substrate_components"]}
    assert "HiveLaminarMicrocircuitLedger" in component_ids


def test_hive_forward_pass_gates_plasticity_with_neuromodulatory_signals(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="neuromodulator-session",
            task_id="plasticity-modulation",
            intent="Gate hive-wide plasticity through reward, uncertainty, stability, alert, and dream novelty signals.",
            requested_capabilities=[
                "planning",
                "runtime",
                "memory",
                "evaluation",
                "checkpoint",
                "federation",
                "dreaming",
            ],
            memory_refs=["memory::modulator-prior"],
            requested_actions=[
                {"action_id": "inspect-neuromodulators", "action_type": "read", "target_ref": "modulator-ledger"}
            ],
            max_loops=4,
        )
    )

    modulation = result["neuromodulatory_state_ledger"]
    plasticity = result["neuroplastic_weight_ledger"]
    assert modulation["surface_id"] == "hive-neuromodulatory-state-ledger-v0"
    assert modulation["contract_id"] == "hive-neuromodulatory-state-ledger-v0"
    assert modulation["laminar_microcircuit_ref"] == result["laminar_microcircuit_ledger"]["microcircuit_id"]
    assert modulation["pathway_ref"] == result["neural_pathway_map"]["pathway_id"]
    assert modulation["transmission_ref"] == result["synaptic_transmission_ledger"]["transmission_id"]
    assert modulation["weight_ledger_ref"] == plasticity["weight_ledger_id"]
    assert modulation["activation_ref"] == result["activation"]["activation_id"]
    assert modulation["neural_bus_ref"] == result["neural_bus"]["bus_id"]
    assert modulation["hive_blackboard_ref"] == result["hive_blackboard"]["residual_state_id"]
    assert modulation["checkpoint_ref"] == result["checkpoint"]["checkpoint_id"]
    assert modulation["modulator_count"] == 5
    signal_kinds = {signal["modulator_kind"] for signal in modulation["modulator_signals"]}
    assert signal_kinds == {
        "reward_prediction_error",
        "uncertainty_attention",
        "stability_homeostasis",
        "immune_alert",
        "dream_novelty",
    }
    assert 0 <= modulation["plasticity_gate"]["effective_learning_rate"] <= 0.05
    assert modulation["plasticity_gate"]["applies_to_weight_ledger_ref"] == plasticity["weight_ledger_id"]
    assert modulation["plasticity_gate"]["active_route_mutation_allowed"] is False
    assert modulation["modulation_integrity"]["direct_local_state_reads"] == []
    assert modulation["modulation_integrity"]["active_production_mutated"] is False
    assert modulation["modulation_integrity"]["raw_private_content_encoded"] is False
    assert modulation["artifact_path"] and Path(modulation["artifact_path"]).exists()

    runtime = result["downstream_node_runtime"]
    assert runtime["artifact_refs"]["neuromodulatory_state_ref"] == modulation["neuromodulator_id"]
    assert runtime["input_contract"] == (
        "neural-bus-blackboard-sensory-temporal-memory-embedding-attention-normalization-gate-feedforward-"
        "microcircuit-pathway-transmission-plasticity-neuromodulator-latent-loop-kv-cache-backprop-"
        "optimizer-school-ledger-only"
    )
    assert all(modulation["neuromodulator_id"] in receipt["source_artifact_refs"] for receipt in runtime["receipts"])

    replay = substrate.replay(session_id="neuromodulator-session")
    assert replay["neuromodulatory_state_chain"][0]["neuromodulator_id"] == modulation["neuromodulator_id"]
    assert "neuromodulatory_state_chain" in replay["control_panel_replay"]["available_chains"]
    assert replay["control_panel_replay"]["chain_counts"]["neuromodulatory_state_chain"] == 1

    summary = substrate.summary(session_id="neuromodulator-session")
    assert summary["neuromodulatory_state_ledger"]["neuromodulator_count"] == 1
    assert summary["latest_neuromodulatory_state"]["neuromodulator_id"] == modulation["neuromodulator_id"]
    scorecard = substrate.scorecard(session_id="neuromodulator-session")
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-058" in scorecard[
        "source_documents"
    ]
    component_ids = {component["component_id"] for component in scorecard["substrate_components"]}
    assert "HiveNeuromodulatoryStateLedger" in component_ids


def test_hive_neural_substrate_blocks_write_without_checkpoint(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="hive-blocked-session",
            intent="Attempt a write-like substrate mutation without checkpoint evidence.",
            requested_capabilities=["tools", "checkpoint"],
            requested_actions=[
                {
                    "action_id": "write-runtime",
                    "action_type": "write",
                    "target_ref": "nexusnet/hive/substrate.py",
                    "sandboxed": False,
                }
            ],
        )
    )

    assert result["lifecycle_state"] == "blocked"
    assert result["immune_findings"][0]["rule_id"] == "write_action_requires_checkpoint"
    assert result["policy_scan"]["summary"]["active_hard_fail_count"] >= 1
    assert any(event["event_type"] == "hive.blocked" for event in result["events"])

    summary = substrate.summary(session_id="hive-blocked-session")
    assert summary["runtime_state"] == "degraded"
    assert summary["latest_forward_pass"]["lifecycle_state"] == "blocked"
    assert summary["health_ledger"]["degraded_event_count"] == 1
    assert summary["latest_health_event"]["event_state"] == "degraded_observed"

    scorecard = substrate.scorecard(session_id="hive-blocked-session")
    assert scorecard["runtime_state"] == "degraded"


def test_plan_mode_write_jail_allows_plan_artifact_only_and_blocks_other_writes(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="plan-mode-session",
            intent="Plan a substrate change with plan-mode write jail active.",
            requested_capabilities=["planning", "tools", "checkpoint"],
            requested_actions=[
                {"action_id": "read-canon", "action_type": "read", "target_ref": "docs/canon.md"},
                {"action_id": "safe-shell", "action_type": "shell", "target_ref": "pytest --collect-only", "safe": True},
                {"action_id": "write-plan", "action_type": "write", "target_ref": "plans/hive-substrate-plan.md"},
                {"action_id": "write-code", "action_type": "write", "target_ref": "nexusnet/hive/substrate.py"},
            ],
            metadata={
                "plan_mode": True,
                "plan_artifact_ref": "plans/hive-substrate-plan.md",
            },
        )
    )

    jail = result["plan_mode_write_jail"]
    assert jail["jail_state"] == "enforced"
    assert jail["plan_mode"] is True
    assert jail["allowed_write_targets"] == ["plans/hive-substrate-plan.md"]
    assert jail["allowed_action_ids"] == ["read-canon", "safe-shell", "write-plan"]
    assert jail["blocked_action_ids"] == ["write-code"]
    assert result["lifecycle_state"] == "blocked"
    assert {finding["rule_id"] for finding in result["immune_findings"]} == {"plan_mode_write_jail_violation"}


def test_tool_execution_registry_enforces_metadata_and_parallel_safe_batches(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="tool-registry-session",
            intent="Execute a metadata-governed tool batch through the hive substrate.",
            requested_capabilities=["tools", "checkpoint", "runtime"],
            requested_actions=[
                {
                    "action_id": "inspect-canon",
                    "action_type": "read",
                    "tool_id": "repo.read",
                    "read_only": True,
                    "concurrent_safe": True,
                    "output_limit": 4096,
                    "target_ref": "docs/canon.md",
                },
                {
                    "action_id": "list-tests",
                    "action_type": "list",
                    "tool_id": "rg.files",
                    "read_only": True,
                    "concurrent_safe": True,
                    "output_truncation": {"mode": "lines", "limit": 200},
                    "target_ref": "tests",
                },
                {
                    "action_id": "write-tool-cache",
                    "action_type": "write",
                    "tool_id": "cache.writer",
                    "read_only": False,
                    "concurrent_safe": False,
                    "cache_invalidation_after_writes": ["tool-registry", "routing-cache"],
                    "target_ref": "runtime/tool-cache.json",
                    "checkpoint_ref": "checkpoint::operator-approved",
                    "sandboxed": True,
                },
            ],
            max_loops=2,
        )
    )

    registry = result["tool_execution_registry"]
    records = {record["action_id"]: record for record in registry["records"]}

    assert result["lifecycle_state"] == "completed"
    assert registry["surface_id"] == "tool-execution-registry-v0"
    assert registry["registry_state"] == "enforced"
    assert registry["action_count"] == 3
    assert registry["registered_tool_count"] == 3
    assert records["inspect-canon"]["read_only"] is True
    assert records["inspect-canon"]["concurrent_safe"] is True
    assert records["inspect-canon"]["output_truncation_policy"]["limit"] == 4096
    assert records["list-tests"]["output_truncation_policy"]["mode"] == "lines"
    assert records["write-tool-cache"]["read_only"] is False
    assert records["write-tool-cache"]["parallel_batch_eligible"] is False
    assert records["write-tool-cache"]["cache_invalidation_after_writes"] == ["tool-registry", "routing-cache"]
    assert registry["parallel_safe_batches"][0]["action_ids"] == ["inspect-canon", "list-tests"]
    assert registry["cache_invalidation_plan"]["cache_invalidation_required"] is True
    assert registry["cache_invalidation_plan"]["invalidated_cache_refs"] == ["routing-cache", "tool-registry"]
    assert registry["write_gate"]["checkpoint_required_action_ids"] == ["write-tool-cache"]
    assert registry["write_gate"]["sandbox_required_action_ids"] == ["write-tool-cache"]
    assert registry["write_gate"]["ungated_write_action_ids"] == []

    replay = substrate.replay(session_id="tool-registry-session")
    assert replay["tool_execution_registry_chain"][0]["registry_id"] == registry["registry_id"]
    assert "tool_execution_registry_chain" in replay["control_panel_replay"]["available_chains"]

    component_ids = {component["component_id"] for component in substrate.scorecard(session_id="tool-registry-session")["substrate_components"]}
    assert "ToolExecutionRegistry" in component_ids


def test_task_dependency_graph_refreshes_reverse_edges_and_parallel_ready_tasks(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="task-graph-session",
            intent="Route a multi-task hive workflow with explicit dependencies.",
            requested_capabilities=["planning", "runtime", "evaluation"],
            requested_actions=[{"action_id": "inspect-workflow", "action_type": "read", "target_ref": "workflow"}],
            metadata={
                "task_graph": [
                    {"task_id": "research", "state": "completed", "blocks": ["implement"]},
                    {"task_id": "implement", "state": "ready", "blocks": ["review"]},
                    {"task_id": "review", "state": "ready"},
                    {"task_id": "docs", "state": "ready"},
                ]
            },
        )
    )

    graph = result["task_dependency_graph"]
    nodes = {node["task_id"]: node for node in graph["nodes"]}

    assert graph["surface_id"] == "task-dependency-graph-v0"
    assert graph["graph_state"] == "enforced"
    assert graph["edge_count"] == 2
    assert graph["blocks_edges"] == [
        {"from_task_id": "research", "to_task_id": "implement"},
        {"from_task_id": "implement", "to_task_id": "review"},
    ]
    assert nodes["implement"]["blocked_by"] == ["research"]
    assert nodes["review"]["blocked_by"] == ["implement"]
    assert graph["reverse_edge_refresh"]["added_blocked_by_edges"] == [
        {"task_id": "implement", "blocked_by": "research"},
        {"task_id": "review", "blocked_by": "implement"},
    ]
    assert nodes["implement"]["dispatch_state"] == "parallel_ready"
    assert nodes["review"]["dispatch_state"] == "blocked_by_inbound_edges"
    assert graph["parallel_ready_task_ids"] == ["docs", "implement"]
    assert graph["blocked_task_ids"] == ["review"]
    assert graph["stale_dependency_audit"]["missing_task_refs"] == []

    replay = substrate.replay(session_id="task-graph-session")
    assert replay["task_dependency_graph_chain"][0]["graph_id"] == graph["graph_id"]
    assert "task_dependency_graph_chain" in replay["control_panel_replay"]["available_chains"]

    component_ids = {component["component_id"] for component in substrate.scorecard(session_id="task-graph-session")["substrate_components"]}
    assert "TaskDependencyGraph" in component_ids


def test_provider_circuit_breaker_classifies_errors_and_blocks_unsafe_route_mutation(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="provider-circuit-session",
            intent="Route provider failures through model-family health and fallback policy.",
            requested_capabilities=["runtime", "routing", "provider_health"],
            requested_actions=[{"action_id": "inspect-provider-health", "action_type": "read", "target_ref": "providers"}],
            metadata={
                "provider_events": [
                    {
                        "provider_id": "deepseek-direct",
                        "model_family": "deepseek-v4",
                        "status_code": 429,
                        "error_message": "quota exceeded; rate limit",
                    },
                    {
                        "provider_id": "openai-compatible",
                        "model_family": "gpt",
                        "status_code": 400,
                        "error_message": "context length exceeded",
                    },
                    {
                        "provider_id": "local-lmstudio",
                        "model_family": "local",
                        "status_code": 503,
                        "error_message": "connection reset by peer",
                    },
                    {
                        "provider_id": "private-provider",
                        "model_family": "private",
                        "status_code": 401,
                        "error_message": "invalid api key",
                    },
                ]
            },
        )
    )

    circuit = result["provider_circuit_breaker"]
    records = {record["provider_id"]: record for record in circuit["records"]}

    assert circuit["surface_id"] == "provider-circuit-breaker-v0"
    assert circuit["circuit_state"] == "guarded"
    assert records["deepseek-direct"]["error_family"] == "quota"
    assert records["deepseek-direct"]["retryable"] is False
    assert records["deepseek-direct"]["cooldown_required"] is True
    assert records["openai-compatible"]["error_family"] == "context_too_long"
    assert records["openai-compatible"]["fallback_route"] == "route:context-compression-or-long-context-family"
    assert records["local-lmstudio"]["error_family"] == "transient"
    assert records["local-lmstudio"]["retry_policy"] == "exponential_backoff_with_jitter"
    assert records["private-provider"]["error_family"] == "auth_or_permission"
    assert records["private-provider"]["non_retryable"] is True
    assert circuit["model_family_health"]["deepseek-v4"]["health_state"] == "degraded"
    assert circuit["model_family_health"]["private"]["route_allowed"] is False
    assert circuit["promotion_gate"]["active_provider_route_mutated"] is False
    assert "provider route changes require health evidence" in circuit["promotion_gate"]["gate_reason"]

    replay = substrate.replay(session_id="provider-circuit-session")
    assert replay["provider_circuit_breaker_chain"][0]["circuit_id"] == circuit["circuit_id"]
    assert "provider_circuit_breaker_chain" in replay["control_panel_replay"]["available_chains"]

    component_ids = {component["component_id"] for component in substrate.scorecard(session_id="provider-circuit-session")["substrate_components"]}
    assert "ProviderCircuitBreaker" in component_ids


def test_prompt_overlay_registry_composes_provider_and_model_family_overlays_in_shadow(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="prompt-overlay-session",
            intent="Compose DeepSeek-specific prompt overlays without mutating the base prompt.",
            requested_capabilities=["routing", "tools", "prompting"],
            requested_actions=[{"action_id": "inspect-prompt-overlays", "action_type": "read", "target_ref": "prompts"}],
            metadata={
                "prompt_overlay_registry": {
                    "base_prompt_ref": "prompt::nexusbrain::base",
                    "provider_id": "deepseek-direct",
                    "model_family": "deepseek-v4",
                    "runtime": "cloud",
                    "overlays": [
                        {
                            "overlay_id": "deepseek-tool-calling",
                            "applies_to": {"provider_id": "deepseek-direct"},
                            "priority": 20,
                            "insert_after": "base",
                            "policy_tags": ["tool_calling"],
                        },
                        {
                            "overlay_id": "deepseek-v4-context",
                            "applies_to": {"model_family": "deepseek-v4"},
                            "priority": 30,
                            "insert_after": "deepseek-tool-calling",
                            "policy_tags": ["long_context"],
                        },
                        {
                            "overlay_id": "local-no-network",
                            "applies_to": {"runtime": "local"},
                            "priority": 40,
                            "insert_after": "base",
                            "policy_tags": ["local_only"],
                        },
                    ],
                }
            },
        )
    )

    registry = result["prompt_overlay_registry"]

    assert registry["surface_id"] == "prompt-overlay-registry-v0"
    assert registry["registry_state"] == "composed_shadow"
    assert registry["base_prompt_contract"]["base_prompt_ref"] == "prompt::nexusbrain::base"
    assert registry["base_prompt_contract"]["raw_prompt_exported"] is False
    assert registry["composed_overlay_order"] == ["deepseek-tool-calling", "deepseek-v4-context"]
    assert registry["model_family_compatibility_check"]["compatible_overlay_ids"] == [
        "deepseek-tool-calling",
        "deepseek-v4-context",
    ]
    assert registry["model_family_compatibility_check"]["incompatible_overlay_ids"] == ["local-no-network"]
    assert registry["overlay_conflict_audit"]["conflict_count"] == 0
    assert registry["activation_gate"]["active_prompt_mutated"] is False
    assert registry["activation_gate"]["gate_state"] == "shadow_only_until_compatibility_policy_and_human_review"

    replay = substrate.replay(session_id="prompt-overlay-session")
    assert replay["prompt_overlay_registry_chain"][0]["registry_id"] == registry["registry_id"]
    assert "prompt_overlay_registry_chain" in replay["control_panel_replay"]["available_chains"]

    component_ids = {component["component_id"] for component in substrate.scorecard(session_id="prompt-overlay-session")["substrate_components"]}
    assert "PromptOverlayRegistry" in component_ids


def test_skill_system_loader_uses_markdown_components_precedence_and_handoffs(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="skill-system-session",
            intent="Compose a reusable skill system from markdown skill definitions.",
            requested_capabilities=["skills", "orchestration", "workflow"],
            requested_actions=[{"action_id": "inspect-skill-system", "action_type": "read", "target_ref": "skills"}],
            metadata={
                "skill_system": {
                    "system_id": "video-to-publishable-assets",
                    "goal": "Turn a long video into reusable clips and publishing assets.",
                    "definitions": [
                        """---
skill_id: transcript
purpose: Extract timestamped transcript
precedence: user
allowed_tools: [yt-dlp, whisper]
model_override: local-transcriber
context_mode: fork
---
# Transcript skill
Extract timestamped words.""",
                        """---
skill_id: transcript
purpose: Project-specific timestamped transcript
precedence: project
allowed_tools: [yt-dlp, whisper, ffmpeg]
model_override: local-transcriber
context_mode: fork
---
# Project transcript skill
Extract word-level transcript with source refs.""",
                        {
                            "skill_id": "clip-selector",
                            "purpose": "Score reusable clip candidates",
                            "precedence": "project",
                            "allowed_tools": ["python"],
                            "model_override": "reasoning-reviewer",
                            "context_mode": "inline",
                        },
                    ],
                    "orchestrator": {
                        "skill_id": "shortform-orchestrator",
                        "run_order": ["transcript", "clip-selector"],
                        "human_checkpoints": ["after-clip-selection"],
                        "visual_result": {"kind": "markdown-dashboard", "artifact_ref": "outputs/shortform/index.md"},
                    },
                    "handoffs": [
                        {
                            "from_skill_id": "transcript",
                            "to_skill_id": "clip-selector",
                            "handoff_artifact": "transcript.word-timestamps.json",
                        }
                    ],
                }
            },
        )
    )

    loader = result["skill_system_loader"]
    components = {component["skill_id"]: component for component in loader["component_skills"]}

    assert loader["surface_id"] == "skill-system-loader-v0"
    assert loader["loader_state"] == "composed_shadow"
    assert loader["system_id"] == "video-to-publishable-assets"
    assert loader["component_count"] == 2
    assert components["transcript"]["precedence"] == "project"
    assert components["transcript"]["shadowed_definition_count"] == 1
    assert components["transcript"]["allowed_tools"] == ["yt-dlp", "whisper", "ffmpeg"]
    assert components["transcript"]["context_mode"] == "fork"
    assert components["clip-selector"]["context_mode"] == "inline"
    assert loader["orchestrator_contract"]["run_order"] == ["transcript", "clip-selector"]
    assert loader["orchestrator_contract"]["mega_skill_rejected"] is True
    assert loader["orchestrator_contract"]["isolated_skill_endpoint_rejected"] is True
    assert loader["handoff_validation"]["validation_state"] == "valid"
    assert loader["handoff_validation"]["handoffs"][0]["copy_paste_required"] is False
    assert loader["human_checkpoint_gates"] == ["after-clip-selection"]
    assert loader["visual_result_contract"]["kind"] == "markdown-dashboard"
    assert loader["activation_gate"]["active_skill_runtime_mutated"] is False

    replay = substrate.replay(session_id="skill-system-session")
    assert replay["skill_system_loader_chain"][0]["loader_id"] == loader["loader_id"]
    assert "skill_system_loader_chain" in replay["control_panel_replay"]["available_chains"]

    component_ids = {component["component_id"] for component in substrate.scorecard(session_id="skill-system-session")["substrate_components"]}
    assert "SkillSystemLoader" in component_ids


def test_bridge_manager_catalogs_bridges_with_redaction_and_outbound_commitment_gates(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="bridge-manager-session",
            intent="Review bridge catalog before any external message leaves the hive.",
            requested_capabilities=["bridges", "redaction", "governance"],
            requested_actions=[{"action_id": "inspect-bridges", "action_type": "read", "target_ref": "bridges"}],
            metadata={
                "bridges": [
                    {
                        "bridge_id": "slack-ops",
                        "transport": "slack",
                        "permissions": ["read", "send"],
                        "redaction_policy": "pii-secrets-local-paths",
                        "health_state": "healthy",
                    },
                    {
                        "bridge_id": "local-web",
                        "transport": "web",
                        "permissions": ["read"],
                        "redaction_policy": "none-needed-local",
                        "health_state": "healthy",
                    },
                    {
                        "bridge_id": "daemon-control",
                        "transport": "daemon",
                        "permissions": ["read", "write"],
                        "redaction_policy": "operator-approved-local-only",
                        "health_state": "unknown",
                    },
                ]
            },
        )
    )

    manager = result["bridge_manager"]
    bridges = {bridge["bridge_id"]: bridge for bridge in manager["bridges"]}

    assert manager["surface_id"] == "bridge-manager-v0"
    assert manager["manager_state"] == "review_ready"
    assert bridges["slack-ops"]["transport"] == "slack"
    assert bridges["slack-ops"]["outbound_commitment_review"]["required"] is True
    assert bridges["slack-ops"]["outbound_commitment_review"]["outbound_allowed"] is False
    assert bridges["slack-ops"]["redaction"]["redaction_required"] is True
    assert bridges["local-web"]["outbound_commitment_review"]["required"] is False
    assert bridges["daemon-control"]["transport_health_probe"]["health_state"] == "unknown"
    assert manager["local_first_permission_gate"]["external_messages_require_human_approval"] is True
    assert manager["local_first_permission_gate"]["active_bridge_mutation"] is False
    assert manager["redaction_boundary"]["raw_bridge_payloads_exported"] is False

    replay = substrate.replay(session_id="bridge-manager-session")
    assert replay["bridge_manager_chain"][0]["manager_id"] == manager["manager_id"]
    assert "bridge_manager_chain" in replay["control_panel_replay"]["available_chains"]

    component_ids = {component["component_id"] for component in substrate.scorecard(session_id="bridge-manager-session")["substrate_components"]}
    assert "BridgeManager" in component_ids


def test_research_monitor_pipeline_promotes_trends_to_shadow_candidates_and_watchlists_weak_signals(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="research-monitor-session",
            intent="Watch runtime research and turn strong trends into gated candidates.",
            requested_capabilities=["research", "monitoring", "assimilation"],
            requested_actions=[{"action_id": "inspect-research-radar", "action_type": "read", "target_ref": "research"}],
            metadata={
                "research_monitors": [
                    {
                        "monitor_id": "kv-cache-compression-watch",
                        "source_url": "https://example.invalid/kv-cache",
                        "candidate_id": "candidate-kv-cache-compression",
                        "trend_signal": 0.86,
                        "license_state": "open",
                        "security_state": "unknown",
                        "runtime_gate": "needs-sandbox",
                    },
                    {
                        "monitor_id": "low-signal-watch",
                        "source_url": "https://example.invalid/low-signal",
                        "candidate_id": "candidate-low-signal",
                        "trend_signal": 0.21,
                        "license_state": "unknown",
                        "security_state": "unknown",
                    },
                ]
            },
        )
    )

    pipeline = result["research_monitor_pipeline"]

    assert pipeline["surface_id"] == "research-monitor-pipeline-v0"
    assert pipeline["pipeline_state"] == "shadow_monitoring"
    assert pipeline["scheduled_source_monitor"]["monitor_count"] == 2
    assert pipeline["trend_detection"]["strong_trend_candidate_ids"] == ["candidate-kv-cache-compression"]
    assert pipeline["candidate_intake"][0]["candidate_id"] == "candidate-kv-cache-compression"
    assert pipeline["candidate_intake"][0]["review_state"] == "shadow_candidate"
    assert pipeline["promotion_gate_mapping"]["candidate-kv-cache-compression"]["required_gates"] == [
        "source_verification",
        "license_review",
        "security_review",
        "runtime_sandbox_eval",
        "human_governance_approval",
    ]
    assert pipeline["demotion_watchlist"][0]["candidate_id"] == "candidate-low-signal"
    assert pipeline["demotion_watchlist"][0]["watchlist_reason"] == "weak_or_incomplete_signal"
    assert pipeline["raw_source_content_exported"] is False

    replay = substrate.replay(session_id="research-monitor-session")
    assert replay["research_monitor_pipeline_chain"][0]["pipeline_id"] == pipeline["pipeline_id"]
    assert "research_monitor_pipeline_chain" in replay["control_panel_replay"]["available_chains"]

    component_ids = {component["component_id"] for component in substrate.scorecard(session_id="research-monitor-session")["substrate_components"]}
    assert "ResearchMonitorPipeline" in component_ids


def test_blocked_forward_pass_emits_hive_visible_health_and_self_healing_route_around(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="substrate-health-session",
            task_id="blocked-write-health",
            intent="Attempt a blocked write so the hive can observe, route around, and keep operating.",
            requested_capabilities=["runtime", "policy", "checkpoint", "recovery_coordination"],
            requested_actions=[
                {
                    "action_id": "unsafe-write",
                    "action_type": "write",
                    "target_ref": "nexusnet/hive/substrate.py",
                    "sandboxed": False,
                }
            ],
            max_loops=2,
        )
    )

    assert result["lifecycle_state"] == "blocked"
    health_event = result["health_event"]
    assert health_event["surface_id"] == "hive-health-event-v0"
    assert health_event["event_state"] == "degraded_observed"
    assert health_event["visibility_scope"] == "hive-visible"
    assert health_event["source_run_id"] == result["run_id"]
    assert health_event["neural_bus_ref"] == result["neural_bus"]["bus_id"]
    assert health_event["hive_blackboard_ref"] == result["hive_blackboard"]["residual_state_id"]
    assert health_event["active_production_mutated"] is False
    assert Path(health_event["artifact_path"]).exists()

    route_around = result["self_healing_route_around"]
    assert route_around["surface_id"] == "hive-self-healing-route-around-v0"
    assert route_around["route_around_state"] == "prepared"
    assert route_around["active_tasks_continue"] is True
    assert route_around["failed_action_refs"] == ["unsafe-write"]
    assert route_around["consumed_health_event_ref"] == health_event["health_event_id"]
    assert route_around["fallback_node_ids"]
    assert route_around["rollback_required_before_retry"] is True
    assert Path(route_around["artifact_path"]).exists()

    replay = substrate.replay(session_id="substrate-health-session")
    assert replay["health_chain"][0]["health_event_id"] == health_event["health_event_id"]
    assert replay["self_healing_chain"][0]["route_around_id"] == route_around["route_around_id"]

    health = substrate.health(session_id="substrate-health-session")
    assert health["surface_id"] == "hive-health-monitor-v0"
    assert health["runtime_state"] == "degraded"
    assert health["health_ledger"]["degraded_event_count"] == 1
    assert health["self_healing_ledger"]["prepared_route_around_count"] == 1

    summary = substrate.summary(session_id="substrate-health-session")
    assert summary["health_ledger"]["degraded_event_count"] == 1
    assert summary["self_healing_ledger"]["prepared_route_around_count"] == 1
    components = {component["component_id"]: component for component in summary["substrate_components"]}
    component_ids = set(components)
    assert "HiveHealthMonitor" in component_ids
    assert "SelfHealingRouteAround" in component_ids
    assert components["HiveHealthMonitor"]["runtime_state"] == "degraded"
    for component_id in [
        "HiveActivationLedger",
        "HiveEmbeddingTensorLedger",
        "HiveSparseExpertGateLedger",
        "HiveLaminarMicrocircuitLedger",
        "HiveNeuralPathwayMap",
        "CheckpointRewindLedger",
        "ForwardPacketFederationSecurity",
    ]:
        assert components[component_id]["runtime_state"] == "degraded"


def test_hive_forward_pass_materializes_neural_bus_blackboard_and_plane_trace(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="live-substrate-session",
            task_id="materialize-live-substrate",
            intent="Run the hive substrate through live neural bus and blackboard state.",
            requested_capabilities=["planning", "memory", "evaluation", "checkpoint"],
            memory_refs=["canon::hive-neural-substrate"],
            requested_actions=[{"action_id": "inspect-live-substrate", "action_type": "read", "target_ref": "hive"}],
            max_loops=2,
        )
    )

    assert result["neural_bus"]["bus_id"].startswith("neural_bus_")
    assert result["neural_bus"]["message_count"] >= 6
    assert {
        "activation_published",
        "memory_context_loaded",
        "route_selected",
        "loop_state_updated",
        "eval_score_posted",
        "checkpoint_posted",
    }.issubset({message["message_type"] for message in result["neural_bus"]["messages"]})
    assert all(message["delivery_state"] == "delivered" for message in result["neural_bus"]["messages"])
    assert all(message["visibility_scope"] == "hive-visible" for message in result["neural_bus"]["messages"])

    blackboard = result["hive_blackboard"]
    assert blackboard["residual_state_id"].startswith("hive_blackboard_")
    assert blackboard["entry_count"] >= 6
    assert {"intent_embedding", "selected_nodes", "loop_exit", "policy_scan", "checkpoint"}.issubset(
        set(blackboard["residual_keys"])
    )
    assert blackboard["residual_state_digest"].startswith("substrate:")

    trace = result["plane_trace"]
    assert trace["trace_ledger_id"].startswith("hive_trace_ledger_")
    assert trace["record_count"] == 16
    assert [record["plane_id"] for record in trace["records"]] == [plane["plane_id"] for plane in substrate.planes]
    assert all(record["state_delta"] for record in trace["records"])
    assert all(record["event_ref"].startswith(result["run_id"]) for record in trace["records"])

    summary = substrate.summary(session_id="live-substrate-session")
    assert summary["latest_forward_pass"]["neural_bus"]["bus_id"] == result["neural_bus"]["bus_id"]
    assert summary["latest_forward_pass"]["hive_blackboard"]["residual_state_id"] == blackboard["residual_state_id"]

    scorecard = substrate.scorecard(session_id="live-substrate-session")
    component_ids = {component["component_id"] for component in scorecard["substrate_components"]}
    assert {"NeuralBus", "HiveBlackboard", "HiveTraceLedger", "CortexRouter"}.issubset(component_ids)


def test_downstream_ao_and_expert_runtime_consumes_bus_blackboard_and_pathway_map_only(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="downstream-runtime-session",
            task_id="force-artifact-consumption",
            intent="Route runtime and code work through downstream AO and expert substrate runtime.",
            requested_capabilities=["runtime", "code", "implementation", "benchmarking"],
            memory_refs=["canon::neural-bus", "canon::hive-blackboard"],
            requested_actions=[{"action_id": "inspect-runtime", "action_type": "read", "target_ref": "runtime"}],
            max_loops=2,
        )
    )

    runtime = result["downstream_node_runtime"]
    selected_runtime_node_ids = [
        node["node_id"]
        for node in result["route_decision"]["selected_nodes"]
        if node["node_type"] in {"AO", "Expert", "Orchestrator"}
    ]
    bus_message_ids = {message["message_id"] for message in result["neural_bus"]["messages"]}
    blackboard_entry_ids = {entry["entry_id"] for entry in result["hive_blackboard"]["entries"]}
    pathway_id = result["neural_pathway_map"]["pathway_id"]
    transmission_id = result["synaptic_transmission_ledger"]["transmission_id"]

    assert runtime["runtime_id"].startswith("downstream_runtime_")
    assert runtime["input_contract"] == (
        "neural-bus-blackboard-sensory-temporal-memory-embedding-attention-normalization-gate-feedforward-"
        "microcircuit-pathway-transmission-plasticity-neuromodulator-latent-loop-kv-cache-backprop-"
        "optimizer-school-ledger-only"
    )
    assert runtime["artifact_refs"]["neural_pathway_ref"] == pathway_id
    assert runtime["artifact_refs"]["synaptic_transmission_ref"] == transmission_id
    assert runtime["direct_local_state_reads_allowed"] is False
    assert runtime["receipt_count"] == len(selected_runtime_node_ids)
    assert {receipt["node_id"] for receipt in runtime["receipts"]} == set(selected_runtime_node_ids)
    assert all(receipt["execution_state"] == "ready" for receipt in runtime["receipts"])
    assert all(receipt["direct_local_state_reads"] == [] for receipt in runtime["receipts"])
    assert all(pathway_id in receipt["source_artifact_refs"] for receipt in runtime["receipts"])
    assert all(transmission_id in receipt["source_artifact_refs"] for receipt in runtime["receipts"])
    assert all(set(receipt["consumed_message_ids"]).issubset(bus_message_ids) for receipt in runtime["receipts"])
    assert all(set(receipt["consumed_blackboard_entry_ids"]).issubset(blackboard_entry_ids) for receipt in runtime["receipts"])
    assert all(receipt["consumption_digest"].startswith("consume:") for receipt in runtime["receipts"])

    scorecard = substrate.scorecard(session_id="downstream-runtime-session")
    component_ids = {component["component_id"] for component in scorecard["substrate_components"]}
    assert "DownstreamNodeRuntime" in component_ids


def test_harmonic_geometry_kernel_shapes_planes_routing_and_runtime_receipts(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="harmonic-kernel-session",
            task_id="harmonic-substrate-routing",
            intent="Route a harmonic golden-ratio substrate activation through the hive.",
            requested_capabilities=["planning", "runtime", "memory", "evaluation", "checkpoint"],
            memory_refs=["canon::harmonic-geometry"],
            requested_actions=[{"action_id": "inspect-harmonic-kernel", "action_type": "read", "target_ref": "hive"}],
            max_loops=3,
        )
    )

    summary = substrate.summary(session_id="harmonic-kernel-session")
    kernel = summary["harmonic_geometry_kernel"]

    assert kernel["kernel_id"] == "sacred-geometry-harmonic-kernel-v0"
    assert kernel["constants"]["phi"] == pytest.approx(1.61803398875, rel=1e-12)
    assert kernel["constants"]["golden_angle_degrees"] == pytest.approx(137.50776405003785, rel=1e-12)
    assert "golden_ratio_phi" in kernel["formula_basis"]
    assert "harmonic_intervals" in kernel["formula_basis"]
    assert kernel["claim_boundary"] == "deterministic-symbolic-math-heuristic-not-physics-claim"

    assert all("harmonic_signature" in plane for plane in summary["planes"])
    assert all(plane["harmonic_signature"]["kernel_ref"] == kernel["kernel_id"] for plane in summary["planes"])
    assert all(plane["harmonic_signature"]["fibonacci_index"] >= 1 for plane in summary["planes"])
    assert all(plane["harmonic_signature"]["harmonic_ratio"] > 0 for plane in summary["planes"])

    harmonic_routing = result["route_decision"]["harmonic_routing"]
    assert harmonic_routing["kernel_ref"] == kernel["kernel_id"]
    assert harmonic_routing["phi"] == pytest.approx(kernel["constants"]["phi"], rel=1e-12)
    assert harmonic_routing["golden_angle_degrees"] == pytest.approx(
        kernel["constants"]["golden_angle_degrees"],
        rel=1e-12,
    )
    assert len(harmonic_routing["selected_node_resonance"]) == result["route_decision"]["sparse_top_k"]
    assert all(item["resonance_score"] > 0 for item in harmonic_routing["selected_node_resonance"])
    assert all(item["phi_weight"] > 0 for item in harmonic_routing["selected_node_resonance"])
    assert all(item["harmonic_ratio"] > 0 for item in harmonic_routing["selected_node_resonance"])

    assert all("harmonic_cadence" in loop for loop in result["loop_summary"]["loops"])
    assert all(loop["harmonic_cadence"]["cadence_ratio"] > 0 for loop in result["loop_summary"]["loops"])
    assert all(loop["harmonic_cadence"]["phi_decay"] > 0 for loop in result["loop_summary"]["loops"])
    assert all("harmonic_phase_degrees" in message for message in result["neural_bus"]["messages"])
    assert all("resonance_score" in entry for entry in result["hive_blackboard"]["entries"])
    assert all("harmonic_signature" in record for record in result["plane_trace"]["records"])
    assert all(
        receipt["harmonic_execution_signature"]["geometry_kernel_ref"] == kernel["kernel_id"]
        for receipt in result["downstream_node_runtime"]["receipts"]
    )
    assert all(
        receipt["harmonic_execution_signature"]["consumption_ratio"] > 0
        for receipt in result["downstream_node_runtime"]["receipts"]
    )

    scorecard = substrate.scorecard(session_id="harmonic-kernel-session")
    component_ids = {component["component_id"] for component in scorecard["substrate_components"]}
    assert "HarmonicGeometryKernel" in component_ids


def test_sanitized_federated_learning_packet_is_mandatory_and_raw_private_content_free(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="sanitized-federation-session",
            task_id="federated-learning-lock",
            intent="Private operator task involving Project Caldera and a local file path.",
            requested_capabilities=["planning", "runtime", "evaluation", "federated_learning"],
            memory_refs=["private-memory::Project-Caldera"],
            requested_actions=[
                {
                    "action_id": "inspect-private-path",
                    "action_type": "read",
                    "target_ref": r"C:\Users\ChrisBoyd\Documents\private.txt",
                }
            ],
            privacy_class="confidential",
            max_loops=2,
        )
    )

    packet = result["federated_learning_packet"]
    contract = result["federated_learning_contract"]

    assert contract["participation_model"] == "mandatory-sanitized-artifact-metadata-learning"
    assert contract["raw_personal_data_export"] == "forbidden"
    assert packet["contract_ref"] == contract["contract_id"]
    assert packet["share_state"] == "ready_for_privacy_preserving_federated_learning"
    assert packet["raw_content_included"] is False
    assert packet["contains_personal_data"] is False
    assert packet["sanitization"]["raw_intent_exported"] is False
    assert packet["sanitization"]["raw_memory_refs_exported"] is False
    assert packet["sanitization"]["raw_action_targets_exported"] is False
    assert packet["privacy_class"] == "sanitized-metadata-only"
    plane_sync = packet["per_plane_sync"]
    assert plane_sync["status"] == "partial-live-producer-evidence"
    assert plane_sync["policy_ref"] == "canon::C29M0037"
    by_plane = {entry["canonical_plane"]: entry for entry in plane_sync["planes"]}
    assert by_plane["episodic"]["sync_allowed"] is False
    assert by_plane["episodic"]["payload_mode"] == "none"
    assert by_plane["semantic"]["sync_allowed"] is True
    assert by_plane["semantic"]["payload_mode"] == "compressed-embedding-digest-only"
    assert by_plane["semantic"]["producer_status"] == "live-sanitized-producer"
    assert by_plane["semantic"]["producer_ref"].startswith("embedding::")
    assert by_plane["temporal"]["payload_mode"] == "causal-graph-digest-only"
    assert by_plane["temporal"]["producer_status"] == "live-sanitized-producer"
    assert by_plane["temporal"]["producer_ref"].startswith("temporal::")
    assert by_plane["tool-reliability"]["producer_status"] == "live-sanitized-producer"
    assert by_plane["tool-reliability"]["action_count"] == 1
    assert by_plane["tool-reliability"]["ungated_write_count"] == 0
    assert by_plane["safety"]["producer_status"] == "live-sanitized-producer"
    assert by_plane["safety"]["hard_fail_count"] == 0
    assert by_plane["safety"]["immune_finding_count"] == 0
    assert by_plane["dreams"]["producer_status"] == "live-sanitized-producer"
    assert by_plane["dreams"]["dream_candidate_count"] == 2
    assert by_plane["dreams"]["critic_review_count"] == 2
    assert by_plane["dreams"]["producer_ref"].startswith("dream-cycle::")
    assert by_plane["tool-reliability"]["payload_mode"] == "sanitized-reliability-statistics-only"
    assert by_plane["personality"]["payload_mode"] == "sanitized-preference-vector-only"
    assert by_plane["safety"]["payload_mode"] == "safe-mode-correction-metadata-only"
    assert by_plane["dreams"]["payload_mode"] == "distilled-summary-only"
    assert all(entry["raw_content_included"] is False for entry in plane_sync["planes"])
    security = packet["security_envelope"]
    assert security["contract_id"] == "signed-secure-federation-packet-v0"
    assert security["signed_packet"]["signature"].startswith("hive_sig_")
    assert security["signed_packet"]["raw_private_data_exported"] is False
    assert security["secure_aggregate"]["aggregate_state"] == "local_packet_ready_for_secure_aggregation"
    assert security["trust_scoring"]["result_state"] == "passed"
    assert security["poisoning_anomaly_detection"]["result_state"] == "passed"
    assert security["differential_privacy"]["knob_state"] == "enabled-for-sanitized-packet"
    assert security["privacy_audit"]["raw_prompts_exported"] is False
    assert security["privacy_audit"]["local_paths_exported"] is False
    assert security["global_promotion_state"] == "blocked_until_secure_aggregate_sandbox_and_human_approval"
    assert "Project Caldera" not in str(packet)
    assert "private.txt" not in str(packet)
    assert r"C:\Users\ChrisBoyd" not in str(packet)

    replay = substrate.replay(
        session_id="sanitized-federation-session",
        run_id=result["run_id"],
    )
    replayed_plane_sync = replay["federated_per_plane_sync"]
    assert replayed_plane_sync["status"] == "partial-live-producer-evidence"
    assert replayed_plane_sync["packet_ref"] == packet["packet_id"]
    assert replayed_plane_sync["raw_content_included"] is False
    assert replayed_plane_sync["contains_personal_data"] is False
    replayed_by_plane = {
        entry["canonical_plane"]: entry for entry in replayed_plane_sync["planes"]
    }
    assert replayed_by_plane["semantic"]["producer_status"] == "live-sanitized-producer"
    assert replayed_by_plane["dreams"]["dream_candidate_count"] == 2
    assert "federated_per_plane_sync" in replay["control_panel_replay"]["available_chains"]
    assert "Project Caldera" not in str(replayed_plane_sync)
    assert "private.txt" not in str(replayed_plane_sync)
    assert r"C:\Users\ChrisBoyd" not in str(replayed_plane_sync)

    assert "federated_learning_packet_ready" in {
        message["message_type"] for message in result["neural_bus"]["messages"]
    }
    assert "federated_learning_packet" in result["hive_blackboard"]["residual_keys"]
    federated_trace = next(
        record for record in result["plane_trace"]["records"] if record["plane_id"] == "federated-learning"
    )
    assert packet["packet_id"] in federated_trace["output_refs"]

    summary = substrate.summary(session_id="sanitized-federation-session")
    assert summary["federated_learning_contract"]["participation_model"] == contract["participation_model"]

    scorecard = substrate.scorecard(session_id="sanitized-federation-session")
    component_ids = {component["component_id"] for component in scorecard["substrate_components"]}
    assert "FederatedLearningSanitizer" in component_ids
    assert "ForwardPacketFederationSecurity" in component_ids


def test_hive_personality_preferences_persist_locally_and_federate_only_with_explicit_opt_in(
    tmp_path: Path,
):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)
    session_id = "personality-preference-native-session"
    secret = "SECRET-PERSONALITY-PREFERENCE-NATIVE"

    opted_in = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id=session_id,
            task_id="personality-preference-opt-in",
            intent=f"Never export {secret} from the native Hive preference ledger.",
            metadata={
                "personality_preference_keys": ["concise", "structured", secret],
                "personal_data_federation_allowed": True,
                "privacy_consent_record_id": "consent-opt-in-native",
            },
        )
    )

    opted_in_ledger = opted_in["personality_preference_ledger"]
    opted_in_personality = next(
        plane
        for plane in opted_in["federated_learning_packet"]["per_plane_sync"]["planes"]
        if plane["canonical_plane"] == "personality"
    )
    assert opted_in_ledger["session_ref_digest"]
    assert opted_in_ledger["preference_keys"] == ["concise", "structured"]
    assert opted_in_ledger["preference_feature_count"] == 2
    assert opted_in_ledger["personal_data_federation_allowed"] is True
    assert opted_in_ledger["raw_content_included"] is False
    assert opted_in_ledger["contains_personal_data"] is False
    assert opted_in_personality["producer_status"] == "live-sanitized-producer"
    assert opted_in_personality["producer_ref"] == (
        f"preference-vector::{opted_in_ledger['preference_ledger_id']}"
    )
    assert opted_in_personality["preference_feature_count"] == 2

    revoked = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id=session_id,
            task_id="personality-preference-revoked",
            intent=f"Revocation must stop personality federation without exporting {secret}.",
            metadata={
                "personality_preference_keys": ["detailed", secret],
                "personal_data_federation_allowed": False,
                "privacy_consent_record_id": "consent-revoked-native",
            },
        )
    )
    revoked_ledger = revoked["personality_preference_ledger"]
    revoked_personality = next(
        plane
        for plane in revoked["federated_learning_packet"]["per_plane_sync"]["planes"]
        if plane["canonical_plane"] == "personality"
    )
    assert revoked_ledger["preference_keys"] == ["detailed"]
    assert revoked_ledger["personal_data_federation_allowed"] is False
    assert revoked_personality["producer_status"] == "live-local-only-consent-required"
    assert "producer_ref" not in revoked_personality
    assert revoked_personality["preference_feature_count"] == 0

    restored = HiveNeuralSubstrate(artifacts_dir=tmp_path)
    replay = restored.replay(session_id=session_id)
    chain = replay["personality_preference_chain"]
    assert [entry["preference_ledger_id"] for entry in chain] == [
        revoked_ledger["preference_ledger_id"],
        opted_in_ledger["preference_ledger_id"],
    ]
    assert replay["control_panel_replay"]["chain_counts"]["personality_preference_chain"] == 2
    assert "personality_preference_chain" in replay["control_panel_replay"]["available_chains"]
    assert secret not in json.dumps({"chain": chain, "packet": opted_in["federated_learning_packet"]})
    assert session_id not in json.dumps({"chain": chain, "packet": opted_in["federated_learning_packet"]})


def test_hive_forward_pass_records_shared_runtime_growth_receipt_without_private_content(tmp_path: Path):
    growth = MultiUserGrowthCoordinator(global_train_threshold=2, federate_min_users=1, dream_every=1)
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path, global_growth=growth)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="native-growth-session",
            task_id="native-growth-forward",
            intent="Native hive task with Private Project Caldera prompt content.",
            requested_capabilities=["planning", "coding", "federated_learning"],
            memory_refs=["private-memory::Project-Caldera"],
            requested_actions=[
                {
                    "action_id": "inspect-private-path",
                    "action_type": "read",
                    "target_ref": r"C:\Users\ChrisBoyd\Documents\secret.txt",
                }
            ],
            privacy_class="confidential",
            max_loops=2,
        )
    )

    receipt = result["runtime_growth_receipt"]
    packet = result["runtime_growth_federated_packet"]
    assert receipt["surface_id"] == "multi-user-runtime-growth-receipt"
    assert receipt["forward_pass_coverage"]["continuous_assimilation"] is True
    assert receipt["forward_pass_coverage"]["global_growth"] is True
    assert receipt["raw_content_included"] is False
    assert receipt["contains_personal_data"] is False
    assert receipt["active_production_mutation_allowed"] is False
    assert packet["surface_id"] == "multi-user-runtime-growth-federated-packet"
    assert packet["raw_content_included"] is False
    assert packet["contains_personal_data"] is False
    assert result["runtime_growth"]["runtime_interaction_count"] == 1
    assert result["runtime_growth"]["latest_runtime_receipt"]["receipt_id"] == receipt["receipt_id"]

    serialized_receipt = repr(receipt)
    assert "Private Project Caldera" not in serialized_receipt
    assert "Project-Caldera" not in serialized_receipt
    assert "secret.txt" not in serialized_receipt
    assert r"C:\Users\ChrisBoyd" not in serialized_receipt

    summary = substrate.summary(session_id="native-growth-session")
    assert summary["runtime_growth"]["runtime_interaction_count"] == 1
    assert summary["latest_runtime_growth_receipt"]["receipt_id"] == receipt["receipt_id"]
    assert summary["latest_runtime_growth_packet"]["packet_id"] == packet["packet_id"]

    replay = substrate.replay(session_id="native-growth-session", run_id=result["run_id"])
    assert replay["runtime_growth_receipt_chain"][0]["receipt_id"] == receipt["receipt_id"]
    assert "runtime_growth_receipt_chain" in replay["control_panel_replay"]["available_chains"]
    assert replay["control_panel_replay"]["chain_counts"]["runtime_growth_receipt_chain"] == 1


def test_hive_substrate_api_forward_pass_uses_app_shared_growth_coordinator(tmp_path: Path):
    client = TestClient(create_app(str(make_project(tmp_path))))

    response = client.post(
        "/ops/brain/hive-substrate/forward-pass",
        json={
            "session_id": "api-native-growth-session",
            "task_id": "api-native-growth-forward",
            "intent": "Native API hive forward pass should feed shared growth.",
            "requested_capabilities": ["planning", "runtime", "federated_learning"],
            "requested_actions": [
                {"action_id": "inspect-runtime", "action_type": "read", "target_ref": "runtime-status"}
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    app_growth = client.app.state.global_growth.growth_status()
    assert payload["runtime_growth_receipt"]["surface_id"] == "multi-user-runtime-growth-receipt"
    assert app_growth["runtime_interaction_count"] >= 1
    assert app_growth["latest_runtime_receipt"]["receipt_id"] == payload["runtime_growth_receipt"]["receipt_id"]

    summary = client.get("/ops/brain/hive-substrate", params={"session_id": "api-native-growth-session"}).json()
    assert summary["latest_runtime_growth_receipt"]["receipt_id"] == payload["runtime_growth_receipt"]["receipt_id"]


def test_hive_runtime_growth_rehydrates_from_forward_pass_artifacts_after_restart(tmp_path: Path):
    growth = MultiUserGrowthCoordinator(global_train_threshold=2, federate_min_users=1, dream_every=1)
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path, global_growth=growth)
    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="native-growth-restart-session",
            task_id="native-growth-restart-forward",
            intent="Native hive restart should rebuild shared growth from persisted artifacts.",
            requested_capabilities=["planning", "runtime", "federated_learning"],
            max_loops=2,
        )
    )
    receipt = result["runtime_growth_receipt"]

    restored_growth = MultiUserGrowthCoordinator(global_train_threshold=2, federate_min_users=1, dream_every=1)
    restored_substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path, global_growth=restored_growth)
    restored_status = restored_growth.growth_status()

    assert restored_status["runtime_interaction_count"] == 1
    assert restored_status["global_captures"] == 1
    assert restored_status["users"] == 1
    assert restored_status["latest_runtime_receipt"]["receipt_id"] == receipt["receipt_id"]
    assert restored_status["latest_runtime_receipt"]["raw_content_included"] is False
    assert "Native hive restart" not in repr(restored_status)

    idempotent = restored_substrate.hydrate_runtime_growth_from_artifacts(
        session_id="native-growth-restart-session"
    )
    assert idempotent["restored_receipts"] == 0
    assert restored_growth.growth_status()["runtime_interaction_count"] == 1
    summary = restored_substrate.summary(session_id="native-growth-restart-session")
    assert summary["runtime_growth"]["latest_runtime_receipt"]["receipt_id"] == receipt["receipt_id"]


def test_hive_substrate_api_rehydrates_shared_growth_after_app_rebuild(tmp_path: Path):
    project_root = make_project(tmp_path)
    first_client = TestClient(create_app(str(project_root)))
    response = first_client.post(
        "/ops/brain/hive-substrate/forward-pass",
        json={
            "session_id": "api-native-growth-restart-session",
            "task_id": "api-native-growth-restart-forward",
            "intent": "Native API hive forward pass should survive app rebuild in growth state.",
            "requested_capabilities": ["planning", "runtime", "federated_learning"],
        },
    )
    assert response.status_code == 200
    receipt = response.json()["runtime_growth_receipt"]

    rebuilt_client = TestClient(create_app(str(project_root)))
    app_growth = rebuilt_client.app.state.global_growth.growth_status()
    assert app_growth["runtime_interaction_count"] >= 2
    assert app_growth["latest_runtime_receipt"]["source_model"] == "release-wrapper-health-supervisor"
    assert app_growth["latest_runtime_receipt"]["raw_content_included"] is False
    assert app_growth["latest_runtime_receipt"]["contains_personal_data"] is False
    assert (
        rebuilt_client.app.state.global_growth_rehydration["runtime_growth"]["latest_runtime_receipt"]["receipt_id"]
        == receipt["receipt_id"]
    )

    summary = rebuilt_client.get(
        "/ops/brain/hive-substrate",
        params={"session_id": "api-native-growth-restart-session"},
    ).json()
    assert summary["runtime_growth"]["latest_runtime_receipt"]["receipt_id"] == receipt["receipt_id"]
    assert summary["runtime_growth"]["global_latest_runtime_receipt"]["source_model"] == "release-wrapper-health-supervisor"
    assert summary["runtime_growth"]["runtime_interaction_count"] >= 1


def test_hive_substrate_api_approves_route_candidate_and_rolls_back_session_overlay(tmp_path: Path):
    client = TestClient(create_app(str(make_project(tmp_path))))
    session_id = "api-route-overlay-session"

    for task_id, action_id in [
        ("api-route-overlay-seed", "seed-api-route-prior"),
        ("api-route-overlay-candidate", "evaluate-api-route-candidate"),
    ]:
        response = client.post(
            "/ops/brain/hive-substrate/forward-pass",
            json={
                "session_id": session_id,
                "task_id": task_id,
                "intent": "Route API traffic through the hive substrate and evaluate a shadow overlay.",
                "requested_capabilities": ["runtime", "kv_cache", "benchmarking", "federated_learning"],
                "requested_actions": [
                    {"action_id": action_id, "action_type": "read", "target_ref": "api-route-overlay"}
                ],
                "max_loops": 2,
            },
        )
        assert response.status_code == 200
    candidate_payload = response.json()
    evaluation_id = candidate_payload["governed_route_candidate_evaluation"]["evaluation_id"]

    approval_response = client.post(
        f"/ops/brain/hive-substrate/route-candidates/{evaluation_id}/approve",
        json={
            "session_id": session_id,
            "approved_by": "admin::api-route-overlay",
            "human_governance_approval": True,
        },
    )
    assert approval_response.status_code == 200
    approval = approval_response.json()
    assert approval["surface_id"] == "hive-governed-route-candidate-approval"
    assert approval["status"] == "shadow-route-applied"
    assert approval["eval_replay"]["status"] == "passed-shadow"
    assert approval["shadow_route_overlay"]["active_scope"] == "session-shadow-only"

    applied_response = client.post(
        "/ops/brain/hive-substrate/forward-pass",
        json={
            "session_id": session_id,
            "task_id": "api-route-overlay-applied",
            "intent": "Consume the approved session shadow route overlay through the API.",
            "requested_capabilities": ["runtime", "kv_cache", "benchmarking", "federated_learning"],
            "requested_actions": [
                {"action_id": "consume-api-route-overlay", "action_type": "read", "target_ref": "api-route-overlay"}
            ],
            "max_loops": 2,
        },
    )
    assert applied_response.status_code == 200
    applied = applied_response.json()
    assert applied["route_decision"]["session_shadow_route_overlay"]["approval_id"] == approval["approval_id"]
    assert applied["route_decision"]["active_production_route_mutated"] is False

    rollback_response = client.post(
        f"/ops/brain/hive-substrate/route-candidates/{approval['approval_id']}/rollback",
        json={
            "session_id": session_id,
            "reason": "API operator rollback after session shadow replay.",
            "human_governance_approval": True,
        },
    )
    assert rollback_response.status_code == 200
    rollback = rollback_response.json()
    assert rollback["surface_id"] == "hive-governed-route-candidate-rollback"
    assert rollback["rollback_state"] == "rolled_back"
    assert rollback["restored_node_order"] == approval["shadow_route_overlay"]["baseline_node_order"]

    restored_response = client.post(
        "/ops/brain/hive-substrate/forward-pass",
        json={
            "session_id": session_id,
            "task_id": "api-route-overlay-rollback-proof",
            "intent": "Verify the session shadow route overlay is gone after API rollback.",
            "requested_capabilities": ["runtime", "kv_cache", "benchmarking", "federated_learning"],
            "requested_actions": [
                {"action_id": "verify-api-route-rollback", "action_type": "read", "target_ref": "api-route-overlay"}
            ],
            "max_loops": 2,
        },
    )
    assert restored_response.status_code == 200
    assert restored_response.json()["route_decision"]["session_shadow_route_overlay"] is None

    summary = client.get("/ops/brain/hive-substrate", params={"session_id": session_id}).json()
    assert summary["operator_actions"]["approve_route_candidate"]["endpoint"] == (
        "/ops/brain/hive-substrate/route-candidates/{evaluation_id}/approve"
    )
    assert summary["operator_actions"]["rollback_route_candidate"]["endpoint"] == (
        "/ops/brain/hive-substrate/route-candidates/{approval_id}/rollback"
    )
    assert summary["governed_route_candidate_approval_ledger"]["approval_count"] == 1
    assert summary["governed_route_candidate_approval_ledger"]["rolled_back_count"] == 1
    assert summary["governed_route_candidate_rollback_ledger"]["rollback_count"] == 1

    replay = client.get("/ops/brain/hive-substrate/replay", params={"session_id": session_id}).json()
    assert replay["route_candidate_approval_chain"][0]["approval_id"] == approval["approval_id"]
    assert replay["route_candidate_rollback_chain"][0]["rollback_id"] == rollback["rollback_id"]
    assert replay["control_panel_replay"]["chain_counts"]["route_candidate_approval_chain"] == 1
    assert replay["control_panel_replay"]["chain_counts"]["route_candidate_rollback_chain"] == 1


def test_native_hive_blocked_forward_pass_feeds_dream_research_proposal_shadow_only(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    prompt = "Native hive blocked write should research safer recovery without leaking SECRET-NATIVE-DREAM."

    response = client.post(
        "/ops/brain/hive-substrate/forward-pass",
        json={
            "session_id": "native-dream-user",
            "task_id": "native-blocked-dream-forward",
            "intent": prompt,
            "requested_capabilities": ["planning", "runtime", "federated_learning"],
            "requested_actions": [
                {
                    "action_id": "unsafe-native-write",
                    "action_type": "write",
                    "target_ref": "nexusnet/hive/substrate.py",
                }
            ],
            "max_loops": 2,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    receipt = payload["runtime_growth_receipt"]
    assert receipt["federated_packet"]["failure_class"] == "blocked_by_immune_policy"
    assert receipt["raw_content_included"] is False

    queue = client.get("/ops/brain/self-improvement/queue").json()
    native_items = [
        item
        for item in queue["items"]
        if item["event"]["metadata"].get("native_hive_runtime_growth") is True
        and item["event"]["metadata"].get("runtime_growth_receipt_id") == receipt["receipt_id"]
    ]
    assert len(native_items) == 1
    item = native_items[0]
    event = item["event"]
    assert item["status"] == "proposed"
    assert event["metadata"]["source"] == "native-hive-runtime-growth"
    assert event["metadata"]["hive_run_id"] == payload["run_id"]
    assert event["metadata"]["policy_block_class"] == "policy_or_immune_block"
    assert event["metadata"]["raw_content_included"] is False
    assert event["safety"]["contains_private_data"] is False
    assert event["safety"]["contains_secrets"] is False
    assert "blocked-native-hive-forward-pass" in event["actions_taken"]

    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": "native-dream-user"}).json()
    dream_queue = runtime["dream_research_queue"]
    assert dream_queue["status"] == "live-bound"
    assert dream_queue["latest_item"]["queue_id"] == item["queue_id"]
    assert dream_queue["latest_item"]["metadata"]["native_hive_runtime_growth"] is True
    assert dream_queue["latest_item"]["metadata"]["runtime_growth_receipt_id"] == receipt["receipt_id"]
    assert dream_queue["latest_item"]["governance"]["proposal_status"] == "proposed"
    assert dream_queue["latest_episode"]["status"] == "researched"

    proposal = next(
        candidate
        for candidate in runtime["autonomous_updates"]["proposals"]
        if (candidate["metadata"].get("safe_payload") or {}).get("runtime_growth_receipt_id")
        == receipt["receipt_id"]
    )
    assert proposal["requested_state"] == "proposal"
    assert proposal["metadata"]["source"] == "native-hive-runtime-growth"
    assert proposal["metadata"]["active_production_mutation_allowed"] is False
    assert proposal["metadata"]["safe_payload"]["native_hive_runtime_growth"] is True
    assert proposal["metadata"]["safe_payload"]["hive_run_id"] == payload["run_id"]

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "native-dream-user"}).json()
    visualized_queue = visualizer["overlay_state"]["control_panel"]["release_wrapper_runtime"]["dream_research_queue"]
    assert visualized_queue["latest_item"]["metadata"]["native_hive_runtime_growth"] is True

    serialized = json.dumps(
        {"queue": queue, "runtime": runtime, "proposal": proposal, "visualized_queue": visualized_queue},
        sort_keys=True,
    )
    assert "SECRET-NATIVE-DREAM" not in serialized
    assert prompt not in serialized
    assert "native-dream-user" not in serialized


def test_native_hive_growth_proposal_runs_admin_sandbox_apply_and_rollback(tmp_path: Path):
    project_root = make_project(tmp_path)
    sandbox_probe = project_root / "tests" / "native_hive_growth_runner_probe_test.py"
    sandbox_probe.parent.mkdir(parents=True, exist_ok=True)
    sandbox_probe.write_text(
        "def test_native_hive_growth_runner_probe():\n    assert True\n",
        encoding="utf-8",
    )
    client = TestClient(create_app(str(project_root)))
    session_id = "native-growth-runner-user"
    prompt = "Block this native forward pass without leaking SECRET-NATIVE-RUNNER."

    response = client.post(
        "/ops/brain/hive-substrate/forward-pass",
        json={
            "session_id": session_id,
            "task_id": "native-growth-runner-task",
            "intent": prompt,
            "requested_capabilities": ["planning", "runtime", "federated_learning"],
            "requested_actions": [
                {
                    "action_id": "blocked-native-growth-runner-write",
                    "action_type": "write",
                    "target_ref": "nexusnet/hive/substrate.py",
                }
            ],
            "max_loops": 2,
        },
    )
    assert response.status_code == 200
    native_result = response.json()
    receipt = native_result["runtime_growth_receipt"]
    assert receipt["federated_packet"]["failure_class"] == "blocked_by_immune_policy"

    status_card = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    action_lane = status_card["operator_action_lane"]
    update_id = action_lane["proposal_update_id"]
    assert update_id
    assert action_lane["latest_action_statuses"]["proposal"] == "proposed"
    assert action_lane["latest_action_statuses"]["admin_approval"] == "pending-admin-approval"

    approval = client.post(
        "/ops/approvals",
        json={
            "subject": "release-wrapper-autonomous-update",
            "decision": "approved",
            "approver": "operator@example.invalid",
            "rationale": "Approve the native Hive sandbox-only growth lifecycle.",
            "metadata": {"update_id": update_id},
        },
    )
    assert approval.status_code == 200

    run_response = client.post(
        action_lane["run_readiness_evidence_ref"],
        json={
            "session_id": session_id,
            "command": "pytest tests/native_hive_growth_runner_probe_test.py -q",
            "timeout_seconds": 30,
            "approval_decision_id": approval.json()["decision_id"],
        },
    )
    assert run_response.status_code == 200
    run = run_response.json()
    assert run["surface_id"] == "release-wrapper-readiness-evidence-run"
    assert run["status"] == "completed"
    assert "::" not in run["update_id"]
    assert run["update_id"].startswith("update__release-wrapper-dream-research__native-hive-runtime-growth")
    assert run["active_production_mutated"] is False
    assert run["actions"]["admin_approval"]["status"] == "admin-approved"
    assert run["actions"]["admin_approval"]["linked_eval_replay"]["status"] == "passed-shadow"
    assert run["actions"]["sandbox_tests"]["status"] == "passed"
    assert run["actions"]["sandbox_tests"]["sandbox"]["active_project_root_mutated"] is False
    assert run["actions"]["apply"]["status"] == "applied-shadow-safe-file"
    assert run["actions"]["apply"]["active_production_mutated"] is False
    assert run["actions"]["apply"]["release_wrapper_ao_guard"]["passed"] is True
    assert run["actions"]["rollback"]["status"] == "rolled-back"
    assert run["actions"]["rollback"]["rollback_restored"] is True
    assert run["actions"]["rollback"]["active_production_mutated"] is False
    assert Path(run["artifact_path"]).exists()

    safe_file_path = Path(run["actions"]["apply"]["safe_file_path"])
    assert not safe_file_path.exists()

    refreshed = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    refreshed_statuses = refreshed["operator_action_lane"]["latest_action_statuses"]
    assert refreshed_statuses["admin_approval"] == "admin-approved"
    assert refreshed_statuses["shadow_eval_replay"] == "passed-shadow"
    assert refreshed_statuses["sandbox_tests"] == "passed"
    assert refreshed_statuses["apply"] == "applied-shadow-safe-file"
    assert refreshed_statuses["rollback"] == "rolled-back"
    assert refreshed_statuses["readiness_runner"] == "completed"
    assert refreshed["release_readiness_evidence_runner"]["latest_run"]["run_id"] == run["run_id"]
    native_governance = refreshed["native_runtime_growth_governance"]
    assert native_governance["surface_id"] == "native-runtime-growth-governance"
    assert native_governance["status"] == "rolled-back"
    assert native_governance["runtime_growth_receipt_id"] == receipt["receipt_id"]
    assert native_governance["proposal_update_id"] == update_id
    assert native_governance["latest_action_statuses"]["admin_approval"] == "admin-approved"
    assert native_governance["latest_action_statuses"]["sandbox_tests"] == "passed"
    assert native_governance["latest_action_statuses"]["apply"] == "applied-shadow-safe-file"
    assert native_governance["latest_action_statuses"]["rollback"] == "rolled-back"
    assert native_governance["active_production_mutated"] is False
    assert native_governance["raw_content_included"] is False
    assert (
        refreshed["autonomous_updates"]["latest_dream_research_proposal"]["metadata"]["safe_payload"][
            "runtime_growth_receipt_id"
        ]
        == receipt["receipt_id"]
    )

    lifecycle = client.get("/ops/wrapper/session-lifecycle", params={"session_id": session_id}).json()
    assert lifecycle["autonomous_update_path"]["latest_applied"]["status"] == "applied-shadow-safe-file"
    assert lifecycle["autonomous_update_path"]["latest_rollback"]["rollback_restored"] is True
    assert lifecycle["autonomous_update_path"]["native_runtime_growth_governance"]["status"] == "rolled-back"

    restarted_client = TestClient(create_app(str(project_root)))
    restarted_runtime = restarted_client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    restarted_native_governance = restarted_runtime["native_runtime_growth_governance"]
    assert restarted_native_governance["status"] == "rolled-back"
    assert restarted_native_governance["latest_runner_status"] == "completed"
    assert restarted_native_governance["latest_runner_run_id"] == run["run_id"]
    assert restarted_native_governance["runtime_growth_receipt_id"] == receipt["receipt_id"]
    assert restarted_native_governance["active_production_mutated"] is False

    restarted_first_run = restarted_client.get(
        "/ops/wrapper/first-run-readiness",
        params={"session_id": session_id},
    ).json()
    assert restarted_first_run["native_runtime_growth_governance"]["status"] == "rolled-back"
    assert restarted_first_run["native_runtime_growth_governance"]["latest_runner_run_id"] == run["run_id"]
    assert restarted_first_run["gates"]["native_runtime_growth_governance_ready"] is True
    assert "native_runtime_growth_governance_ready" not in restarted_first_run["missing_proof_fields"]
    assert (
        restarted_first_run["request_template"]["template"]["source_refs"]["native_runtime_growth_governance"]
        == "/ops/wrapper/status-card#native_runtime_growth_governance"
    )

    restarted_readiness = restarted_client.get(
        "/ops/wrapper/release-readiness",
        params={"session_id": session_id},
    ).json()
    restarted_checks = {check["check_id"]: check for check in restarted_readiness["readiness_checks"]}
    assert restarted_checks["native-runtime-growth-governance"]["status"] == "pass"
    assert restarted_checks["native-runtime-growth-governance"]["latest_runner_status"] == "completed"
    assert restarted_readiness["evidence"]["native_runtime_growth_governance"]["status"] == "rolled-back"
    assert restarted_readiness["evidence"]["native_runtime_growth_governance"]["latest_runner_run_id"] == run["run_id"]
    subsystem_gates = {
        gate["gate_id"]: gate
        for gate in restarted_readiness["whole_system_boot_contract"]["subsystem_gates"]
    }
    assert subsystem_gates["native-runtime-growth-governance"]["status"] == "pass"

    serialized = json.dumps(
        {
            "run": run,
            "status_card": refreshed,
            "lifecycle": lifecycle,
            "restarted_runtime": restarted_runtime,
            "restarted_first_run": restarted_first_run,
            "restarted_readiness": restarted_readiness,
        }
    )
    assert prompt not in serialized
    assert "SECRET-NATIVE-RUNNER" not in serialized
    assert session_id not in serialized
    assert "native_hive_runtime_growth" in serialized
    control_panel_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "nativeRuntimeGrowthGovernance" in control_panel_js
    assert "native growth governance" in control_panel_js


def test_sanitized_federated_packets_update_hive_prior_ledger_without_private_content(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    first = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="federated-prior-session",
            task_id="runtime-private-caldera",
            intent="Private Project Caldera runtime cache tuning on local workstation path.",
            requested_capabilities=["runtime", "kv_cache", "benchmarking", "federated_learning"],
            memory_refs=["private-memory::Project-Caldera"],
            requested_actions=[
                {
                    "action_id": "inspect-local-cache",
                    "action_type": "read",
                    "target_ref": r"C:\Users\ChrisBoyd\Documents\Project-Caldera\cache.log",
                }
            ],
            privacy_class="confidential",
            max_loops=2,
        )
    )
    second = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="federated-prior-session",
            task_id="runtime-private-caldera-quant",
            intent="Private Project Caldera quantization route follow-up.",
            requested_capabilities=["runtime", "quantization", "evaluation", "federated_learning"],
            memory_refs=["private-memory::Project-Caldera"],
            requested_actions=[
                {
                    "action_id": "inspect-private-quant",
                    "action_type": "read",
                    "target_ref": r"C:\Users\ChrisBoyd\Documents\Project-Caldera\quant.json",
                }
            ],
            privacy_class="confidential",
            max_loops=2,
        )
    )

    prior_update = second["federated_prior_update"]
    assert prior_update["source_packet_id"] == second["federated_learning_packet"]["packet_id"]
    assert prior_update["contract_ref"] == second["federated_learning_contract"]["contract_id"]
    assert prior_update["ingestion_state"] == "local_prior_updated_pending_global_sandbox_approval"
    assert prior_update["raw_content_included"] is False
    assert prior_update["contains_personal_data"] is False
    assert prior_update["promotion_state"] == "sandbox_required_before_global_release"
    assert "Project Caldera" not in str(prior_update)
    assert "Project-Caldera" not in str(prior_update)
    assert r"C:\Users\ChrisBoyd" not in str(prior_update)

    assert "federated_prior_updated" in {message["message_type"] for message in second["neural_bus"]["messages"]}
    assert "federated_prior_update" in second["hive_blackboard"]["residual_keys"]
    federated_trace = next(
        record for record in second["plane_trace"]["records"] if record["plane_id"] == "federated-learning"
    )
    assert prior_update["prior_update_id"] in federated_trace["output_refs"]

    summary = substrate.summary(session_id="federated-prior-session")
    ledger = summary["federated_learning_prior_ledger"]
    assert ledger["packet_count"] == 2
    assert ledger["sanitized_packet_count"] == 2
    assert ledger["prior_update_count"] == 2
    assert ledger["privacy_boundary"]["raw_personal_data_export"] == "forbidden"
    assert ledger["task_family_priors"]
    assert ledger["route_geometry_priors"]["flower-field-to-metatron-chord-sparse-selection"]["packet_count"] == 2
    assert ledger["routing_prior_suggestions"][0]["promotion_state"] == "sandbox_required_before_global_release"
    assert "Project Caldera" not in str(ledger)
    assert "Project-Caldera" not in str(ledger)
    assert r"C:\Users\ChrisBoyd" not in str(ledger)
    assert first["federated_prior_update"]["prior_update_id"] != prior_update["prior_update_id"]

    scorecard = substrate.scorecard(session_id="federated-prior-session")
    component_ids = {component["component_id"] for component in scorecard["substrate_components"]}
    assert "FederatedPriorLedger" in component_ids


def test_global_federation_review_gates_promotion_with_sandbox_privacy_and_human_approval(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="global-federation-session",
            task_id="global-fed-seed-a",
            intent="Seed sanitized packet for global federation promotion review.",
            requested_capabilities=["runtime", "federated_learning", "evaluation"],
            requested_actions=[{"action_id": "read-fed-a", "action_type": "read", "target_ref": "federation"}],
            max_loops=2,
        )
    )
    substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="global-federation-session",
            task_id="global-fed-seed-b",
            intent="Seed a second sanitized packet for secure aggregation review.",
            requested_capabilities=["runtime", "federated_learning", "evaluation"],
            requested_actions=[{"action_id": "read-fed-b", "action_type": "read", "target_ref": "federation"}],
            max_loops=2,
        )
    )
    substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="global-federation-session",
            task_id="global-fed-seed-c",
            intent="Seed a third sanitized packet to meet secure aggregation quorum.",
            requested_capabilities=["runtime", "federated_learning", "evaluation"],
            requested_actions=[{"action_id": "read-fed-c", "action_type": "read", "target_ref": "federation"}],
            max_loops=2,
        )
    )

    blocked = substrate.review_global_federation_promotion(
        {
            "session_id": "global-federation-session",
            "subject_id": "router-prior-global-shadow",
            "human_governance_approval": False,
        }
    )

    assert blocked["surface_id"] == "hive-global-federation-review-v0"
    assert blocked["promotion_state"] == "blocked_pending_evidence_or_human_approval"
    assert blocked["secure_aggregate"]["source_packet_count"] == 3
    assert blocked["promotion_gate"]["human_governance_approval"] is False
    assert blocked["promotion_gate"]["active_global_learning_mutated"] is False
    assert "human_governance_approval" in blocked["promotion_gate"]["missing_evidence"]

    blocked_summary = substrate.summary(session_id="global-federation-session")
    blocked_components = {component["component_id"]: component for component in blocked_summary["substrate_components"]}
    assert blocked_summary["global_federation_review_ledger"]["blocked_count"] == 1
    assert blocked_components["GlobalFederationPromotionReview"]["runtime_state"] == "degraded"

    approved = substrate.review_global_federation_promotion(
        {
            "session_id": "global-federation-session",
            "subject_id": "router-prior-global-shadow",
            "sandbox_replay_ref": "sandbox::global-fed-shadow-replay",
            "security_review_ref": "security::global-fed-packet-review",
            "privacy_review_ref": "privacy::global-fed-dp-audit",
            "human_governance_approval": True,
        }
    )

    assert approved["promotion_state"] == "approved_for_global_shadow_learning"
    assert approved["promotion_gate"]["gate_state"] == "passed_for_shadow_only"
    assert approved["promotion_gate"]["active_global_learning_mutated"] is False
    assert approved["privacy_audit"]["raw_private_data_exported"] is False
    assert approved["poisoning_anomaly_detection"]["result_state"] == "passed"
    assert approved["differential_privacy"]["knob_state"] == "enabled-for-global-shadow-learning"

    summary = substrate.summary(session_id="global-federation-session")
    assert summary["global_federation_review_ledger"]["review_count"] == 2
    assert summary["latest_global_federation_review"]["review_id"] == approved["review_id"]
    component_ids = {component["component_id"] for component in summary["substrate_components"]}
    assert "GlobalFederationPromotionReview" in component_ids

    replay = substrate.replay(session_id="global-federation-session")
    assert replay["global_federation_review_chain"][0]["review_id"] == approved["review_id"]
    assert "global_federation_review_chain" in replay["control_panel_replay"]["available_chains"]


def test_hive_activation_shadow_routing_checkpoint_replay_and_runtime_execution_are_live(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    first = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="substrate-completion-session",
            task_id="seed-runtime-prior",
            intent="Seed a sanitized runtime prior for later shadow routing.",
            requested_capabilities=["runtime", "kv_cache", "benchmarking", "federated_learning"],
            requested_actions=[{"action_id": "inspect-runtime", "action_type": "read", "target_ref": "runtime"}],
            max_loops=2,
        )
    )
    second = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="substrate-completion-session",
            task_id="complete-runtime-substrate",
            intent="Execute runtime substrate through activation, checkpoint, replay, and shadow routing.",
            requested_capabilities=["runtime", "kv_cache", "benchmarking", "federated_learning"],
            requested_actions=[{"action_id": "inspect-runtime-2", "action_type": "read", "target_ref": "runtime"}],
            max_loops=2,
        )
    )

    activation = second["activation"]
    assert activation["contract_id"] == "hive-activation-v0"
    assert activation["activation_id"].startswith("hive_activation_")
    assert activation["task_id"] == "complete-runtime-substrate"
    assert activation["source_ref"] == "operator"
    assert activation["checkpoint_ref"] == second["checkpoint"]["checkpoint_id"]
    assert activation["memory_refs"] == []
    assert activation["action_refs"] == ["inspect-runtime-2"]
    assert Path(activation["artifact_path"]).exists()

    runtime = second["downstream_node_runtime"]
    assert runtime["execution_unit_count"] == runtime["receipt_count"]
    assert runtime["execution_units"]
    assert runtime["runtime_executor_state"] == "executed"
    assert runtime["node_output_count"] == runtime["execution_unit_count"]
    assert runtime["node_outputs"]
    assert all(unit["execution_mode"] == "artifact-bound-v0" for unit in runtime["execution_units"])
    assert all(
        unit["input_contract"]
        == "neural-bus-blackboard-sensory-temporal-memory-embedding-attention-normalization-gate-feedforward-"
        "microcircuit-pathway-transmission-plasticity-neuromodulator-latent-loop-kv-cache-backprop-"
        "optimizer-school-ledger-only"
        for unit in runtime["execution_units"]
    )
    assert all(unit["direct_local_state_reads"] == [] for unit in runtime["execution_units"])
    assert all(unit["output_artifact_ref"].startswith("node_output_") for unit in runtime["execution_units"])
    assert all(output["output_state"] == "generated" for output in runtime["node_outputs"])
    assert all(
        output["input_contract"]
        == "neural-bus-blackboard-sensory-temporal-memory-embedding-attention-normalization-gate-feedforward-"
        "microcircuit-pathway-transmission-plasticity-neuromodulator-latent-loop-kv-cache-backprop-"
        "optimizer-school-ledger-only"
        for output in runtime["node_outputs"]
    )
    assert all(output["direct_local_state_reads"] == [] for output in runtime["node_outputs"])
    assert all(output["execution_result_digest"].startswith("node-result:") for output in runtime["node_outputs"])

    shadow = second["shadow_routing"]
    assert shadow["shadow_state"] == "evaluating"
    assert shadow["prior_source"] == "FederatedPriorLedger"
    assert shadow["baseline_selected_node_ids"] == second["route_decision"]["selected_node_ids"]
    assert shadow["promotion_state"] == "shadow_only_pending_eval_sandbox_governance"
    assert shadow["prior_weighted_candidates"]
    assert shadow["quality_comparison"]["baseline_route_quality"] >= 0
    assert shadow["quality_comparison"]["shadow_route_quality"] >= shadow["quality_comparison"][
        "baseline_route_quality"
    ]
    assert shadow["quality_comparison"]["quality_delta"] >= 0
    assert shadow["promotion_gate"]["gate_state"] == "blocked_until_eval_sandbox_governance"
    assert shadow["promotion_gate"]["active_route_mutated"] is False

    route_eval = second["governed_route_candidate_evaluation"]
    assert route_eval["surface_id"] == "hive-governed-route-candidate-evaluation"
    assert route_eval["source_shadow_routing_ref"] == shadow["shadow_routing_id"]
    assert route_eval["candidate_route"]["baseline_node_order"] == second["route_decision"]["selected_node_ids"]
    assert route_eval["candidate_route"]["candidate_node_order"] == shadow["quality_comparison"]["shadow_order"]
    assert route_eval["shadow_eval"]["status"] == "passed-shadow"
    assert route_eval["promotion_gate"]["gate_state"] == "blocked_pending_admin_approval"
    assert route_eval["promotion_gate"]["active_route_mutated"] is False
    assert route_eval["admin_approval"]["approval_state"] == "pending"
    assert route_eval["rollback_plan"]["restore_ref"] == second["checkpoint"]["checkpoint_id"]
    assert route_eval["active_route_mutated"] is False
    assert route_eval["active_production_mutated"] is False
    assert route_eval["artifact_path"]
    assert Path(route_eval["artifact_path"]).exists()

    checkpoint = second["checkpoint"]
    assert checkpoint["snapshot_artifact_path"]
    assert Path(checkpoint["snapshot_artifact_path"]).exists()
    assert checkpoint["restore_validation"]["restore_state"] == "validated_metadata_only"
    assert checkpoint["prompt_preview_digest"].startswith("sha256:")
    assert checkpoint["pre_write_snapshot"]["snapshot_state"] == "captured"
    assert checkpoint["session_turn_snapshot"]["run_ref"] == second["run_id"]
    assert checkpoint["token_snapshot"]["estimated_prompt_tokens"] >= 1
    assert checkpoint["rewind_metadata"]["restore_policy"] == "operator-approved-diff-preview"

    replay = substrate.replay(session_id="substrate-completion-session")
    assert replay["replay_id"].startswith("hive_replay_")
    assert replay["latest_run_id"] == second["run_id"]
    assert replay["run_count"] == 2
    assert replay["plane_trace"]["record_count"] == 16
    assert replay["neural_bus"]["message_count"] >= 8
    assert replay["hive_blackboard"]["entry_count"] >= 9
    assert replay["federated_prior_ledger"]["prior_update_count"] == 2
    assert replay["route_candidate_evaluation_chain"][0]["evaluation_id"] == route_eval["evaluation_id"]
    assert replay["checkpoint_chain"][0]["checkpoint_id"] == second["checkpoint"]["checkpoint_id"]
    assert replay["downstream_runtime_chain"][0]["runtime_id"] == second["downstream_node_runtime"]["runtime_id"]
    assert replay["node_output_chain"][0]["output_artifact_ref"].startswith("node_output_")
    assert "route_candidate_evaluation_chain" in replay["control_panel_replay"]["available_chains"]
    assert "downstream_runtime_chain" in replay["control_panel_replay"]["available_chains"]
    assert "node_output_chain" in replay["control_panel_replay"]["available_chains"]

    summary = substrate.summary(session_id="substrate-completion-session")
    assert summary["activation_ledger"]["activation_count"] == 2
    assert summary["governed_route_candidate_evaluation_ledger"]["evaluation_count"] == 2
    assert summary["latest_governed_route_candidate_evaluation"]["evaluation_id"] == route_eval["evaluation_id"]
    assert summary["artifact_store"]["index_mode"] == "repo-local-json-plus-jsonl-index"
    assert Path(summary["artifact_store"]["forward_pass_index_path"]).exists()
    assert summary["global_federation_safety"]["packet_signing_required"] is True
    assert summary["global_federation_safety"]["poisoning_anomaly_scan_required"] is True
    components = {component["component_id"]: component for component in summary["substrate_components"]}
    governed_route_eval = components["GovernedRouteCandidateEvaluation"]
    assert governed_route_eval["runtime_state"] == "degraded"
    assert governed_route_eval["honest_status_label"] == "route-candidate-evaluated-awaiting-admin-approval"
    assert governed_route_eval["active_route_mutated"] is False
    assert first["activation"]["activation_id"] != activation["activation_id"]


def test_route_candidate_admin_approval_applies_session_shadow_overlay_and_rollback_restores_baseline(
    tmp_path: Path,
):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)
    session_id = "route-overlay-session"

    substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id=session_id,
            task_id="route-overlay-seed",
            intent="Seed a sanitized runtime prior before route overlay approval.",
            requested_capabilities=["runtime", "kv_cache", "benchmarking", "federated_learning"],
            requested_actions=[
                {"action_id": "seed-route-prior", "action_type": "read", "target_ref": "runtime-prior"}
            ],
            max_loops=2,
        )
    )
    candidate_run = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id=session_id,
            task_id="route-overlay-candidate",
            intent="Evaluate a prior-influenced route candidate for admin-approved shadow apply.",
            requested_capabilities=["runtime", "kv_cache", "benchmarking", "federated_learning"],
            requested_actions=[
                {"action_id": "evaluate-route-candidate", "action_type": "read", "target_ref": "route-candidate"}
            ],
            max_loops=2,
        )
    )

    evaluation = candidate_run["governed_route_candidate_evaluation"]
    approval = substrate.approve_governed_route_candidate(
        {
            "session_id": session_id,
            "evaluation_id": evaluation["evaluation_id"],
            "approved_by": "admin::route-overlay",
            "human_governance_approval": True,
        }
    )

    assert approval["surface_id"] == "hive-governed-route-candidate-approval"
    assert approval["status"] == "shadow-route-applied"
    assert approval["eval_replay"]["status"] == "passed-shadow"
    assert approval["eval_replay"]["operator_approved"] is True
    assert approval["shadow_route_overlay"]["active_scope"] == "session-shadow-only"
    assert approval["active_route_mutated"] is False
    assert approval["active_production_mutated"] is False

    applied_run = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id=session_id,
            task_id="route-overlay-applied-forward-pass",
            intent="Consume the admin-approved route overlay only inside this session shadow path.",
            requested_capabilities=["runtime", "kv_cache", "benchmarking", "federated_learning"],
            requested_actions=[
                {"action_id": "consume-route-overlay", "action_type": "read", "target_ref": "route-overlay"}
            ],
            max_loops=2,
        )
    )
    applied_overlay = applied_run["route_decision"]["session_shadow_route_overlay"]
    assert applied_overlay["approval_id"] == approval["approval_id"]
    assert applied_overlay["overlay_state"] == "active-session-shadow"
    assert applied_run["route_decision"]["shadow_route_overlay_scope"] == "session-shadow-only"
    assert applied_run["route_decision"]["session_shadow_route_mutated"] is True
    assert applied_run["route_decision"]["active_route_mutated"] is False
    assert applied_run["route_decision"]["active_production_route_mutated"] is False
    assert applied_run["route_decision"]["selected_node_ids"] == applied_overlay["applied_node_order"]

    rollback = substrate.rollback_governed_route_candidate(
        {
            "session_id": session_id,
            "approval_id": approval["approval_id"],
            "reason": "Operator rolled back the session shadow route overlay after replay.",
            "human_governance_approval": True,
        }
    )
    assert rollback["surface_id"] == "hive-governed-route-candidate-rollback"
    assert rollback["rollback_state"] == "rolled_back"
    assert rollback["restored_node_order"] == approval["shadow_route_overlay"]["baseline_node_order"]
    assert rollback["active_route_mutated"] is False
    assert rollback["active_production_mutated"] is False

    restored_run = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id=session_id,
            task_id="route-overlay-rolled-back-forward-pass",
            intent="Verify the session route overlay no longer applies after rollback.",
            requested_capabilities=["runtime", "kv_cache", "benchmarking", "federated_learning"],
            requested_actions=[
                {"action_id": "verify-route-rollback", "action_type": "read", "target_ref": "route-overlay"}
            ],
            max_loops=2,
        )
    )
    assert restored_run["route_decision"]["session_shadow_route_overlay"] is None
    assert restored_run["route_decision"]["session_shadow_route_mutated"] is False
    assert restored_run["route_decision"]["selected_node_ids"] == approval["shadow_route_overlay"]["baseline_node_order"]

    summary = substrate.summary(session_id=session_id)
    assert summary["governed_route_candidate_approval_ledger"]["approval_count"] == 1
    assert summary["governed_route_candidate_approval_ledger"]["rolled_back_count"] == 1
    assert summary["governed_route_candidate_rollback_ledger"]["rollback_count"] == 1
    assert summary["latest_governed_route_candidate_approval"]["approval_id"] == approval["approval_id"]
    assert summary["latest_governed_route_candidate_rollback"]["rollback_id"] == rollback["rollback_id"]
    components = {component["component_id"]: component for component in summary["substrate_components"]}
    approval_component = components["GovernedRouteCandidateApproval"]
    assert approval_component["runtime_state"] == "rolled-back"
    assert approval_component["honest_status_label"] == "session-shadow-route-overlay-rolled-back"
    assert approval_component["active_route_mutated"] is False
    assert approval_component["active_production_mutated"] is False

    replay = substrate.replay(session_id=session_id)
    assert replay["route_candidate_approval_chain"][0]["approval_id"] == approval["approval_id"]
    assert replay["route_candidate_rollback_chain"][0]["rollback_id"] == rollback["rollback_id"]
    assert "route_candidate_approval_chain" in replay["control_panel_replay"]["available_chains"]
    assert "route_candidate_rollback_chain" in replay["control_panel_replay"]["available_chains"]


def test_checkpoint_rewind_creates_restore_proof_and_replay_chain(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="checkpoint-rewind-session",
            task_id="real-checkpoint-rewind",
            intent="Create a checkpoint snapshot and prove it can be rewound without production mutation.",
            requested_capabilities=["checkpoint", "rewind", "runtime", "policy"],
            requested_actions=[{"action_id": "inspect-runtime", "action_type": "read", "target_ref": "nexusnet/hive"}],
        )
    )
    checkpoint = result["checkpoint"]

    rewind = substrate.rewind_checkpoint(
        {
            "session_id": "checkpoint-rewind-session",
            "checkpoint_id": checkpoint["checkpoint_id"],
            "reason": "Operator requested restore proof for substrate checkpoint.",
            "human_governance_approval": True,
        }
    )

    assert rewind["surface_id"] == "hive-checkpoint-rewind-v0"
    assert rewind["rewind_state"] == "restore_validated"
    assert rewind["checkpoint_ref"] == checkpoint["checkpoint_id"]
    assert rewind["source_snapshot_artifact_path"] == checkpoint["snapshot_artifact_path"]
    assert rewind["source_snapshot_digest"].startswith("sha256:")
    assert rewind["restored_snapshot_digest"] == rewind["source_snapshot_digest"]
    assert rewind["restore_validation"]["restore_state"] == "validated_snapshot_artifact"
    assert rewind["restore_validation"]["snapshot_artifact_exists"] is True
    assert rewind["restore_validation"]["snapshot_has_pre_write_snapshot"] is True
    assert rewind["diff_preview"]["active_production_mutation_delta"] == "none"
    assert rewind["diff_preview"]["raw_private_content_delta"] == "none"
    assert rewind["prompt_tool_snapshot_replay"]["prompt_preview_digest"] == checkpoint["prompt_preview_digest"]
    assert rewind["prompt_tool_snapshot_replay"]["tool_snapshot_digest"] == checkpoint["tool_snapshot_digest"]
    assert rewind["prompt_tool_snapshot_replay"]["token_snapshot"]["estimated_prompt_tokens"] >= 1
    assert rewind["active_production_mutated"] is False
    assert Path(rewind["artifact_path"]).exists()

    replay = substrate.replay(session_id="checkpoint-rewind-session")
    assert replay["rewind_chain"][0]["rewind_id"] == rewind["rewind_id"]
    assert replay["control_panel_replay"]["available_chains"].count("rewind_chain") == 1

    summary = substrate.summary(session_id="checkpoint-rewind-session")
    assert summary["latest_rewind"]["rewind_id"] == rewind["rewind_id"]


def test_recursive_dreaming_closed_sandbox_school_and_durable_registry_complete_candidate_lifecycle(
    tmp_path: Path,
):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    dream = substrate.run_recursive_dream(
        {
            "session_id": "substrate-dream-session",
            "problem_statement": "No current expert handles runtime-aware code repair with cache regression proof.",
            "parent_node_refs": ["expert:runtime-cache", "expert:code-synthesis"],
            "requested_capabilities": ["runtime", "code", "repair", "benchmarking"],
            "source_refs": ["docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md"],
        }
    )

    assert dream["surface_id"] == "hive-recursive-neural-dreaming-v0"
    assert dream["dreamer"]["temperature"] == "high"
    assert dream["critic"]["temperature"] == "low"
    assert dream["candidate_request"]["candidate_kind"] == "generated_expert"
    assert dream["sandbox_eval_plan"]["required_before_promotion"] is True
    assert Path(dream["artifact_path"]).exists()

    candidate = substrate.assimilate_candidate(
        HiveAssimilationCandidateRequest(
            session_id="substrate-dream-session",
            candidate_id=dream["candidate_request"]["candidate_id"],
            title=dream["candidate_request"]["title"],
            candidate_kind="generated_expert",
            parent_node_refs=["expert:runtime-cache", "expert:code-synthesis"],
            source_refs=["docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md"],
            capability_traits=["runtime", "code", "repair", "benchmarking"],
            dreamed_traits=dream["candidate_request"]["dreamed_traits"],
            license_state="operator-owned",
            requested_promotion=True,
            metadata={
                "run_closed_sandbox_eval": True,
                "approve_standalone_after_review": True,
                "operator_governance_approval": True,
                "parent_value_deltas": {
                    "expert:runtime-cache": 0.41,
                    "expert:code-synthesis": 0.09,
                },
                "great_outperformance_threshold": 0.30,
                "teacher_panel_reviews": [
                    {"teacher_ref": "teacher:runtime", "review_state": "approved"},
                    {"teacher_ref": "teacher:code-quality", "review_state": "approved"},
                    {"teacher_ref": "teacher:safety", "review_state": "approved"},
                ],
                "distillation_trace_ref": "school::distill::runtime-code-repair",
                "parent_comparison_scorecard_ref": "scorecard::runtime-code-repair",
            },
        )
    )

    assert candidate["lifecycle_state"] == "permanent_standalone_approved"
    assert candidate["closed_sandbox_evaluation"]["sandbox_run"]["execution_state"] == "passed"
    assert candidate["closed_sandbox_evaluation"]["sandbox_run"]["execution_mode"] == "repo-local-deterministic-sandbox-run"
    assert "run_eval_cases" in candidate["closed_sandbox_evaluation"]["sandbox_run"]["executed_steps"]
    assert candidate["closed_sandbox_evaluation"]["eval_suite"]["result_state"] == "passed"
    assert candidate["closed_sandbox_evaluation"]["eval_suite"]["case_results"]
    assert all(
        case_result["result_state"] == "passed"
        for case_result in candidate["closed_sandbox_evaluation"]["eval_suite"]["case_results"]
    )
    assert candidate["closed_sandbox_evaluation"]["security_gate"]["result_state"] == "passed"
    assert candidate["closed_sandbox_evaluation"]["privacy_gate"]["raw_private_data_exported"] is False
    assert candidate["closed_sandbox_evaluation"]["promotion_decision"]["decision_state"] == "passed_pending_school_and_human_governance"
    assert candidate["closed_sandbox_evaluation"]["evidence_bundle"]["artifact_path"] == candidate["closed_sandbox_evaluation"]["artifact_path"]
    assert candidate["closed_sandbox_evaluation"]["failure_policy"]["failed_eval_blocks_promotion"] is True
    assert candidate["ivy_league_school_review"]["certification_state"] == "certified"
    assert candidate["ivy_league_school_review"]["teacher_panel_state"] == "complete"
    assert len(candidate["ivy_league_school_review"]["teacher_scorecards"]) == 3
    assert all(
        scorecard["temperature"] == "low"
        for scorecard in candidate["ivy_league_school_review"]["teacher_scorecards"]
    )
    assert candidate["ivy_league_school_review"]["distillation_trace"]["trace_state"] == "recorded"
    assert candidate["ivy_league_school_review"]["certification_record"]["record_state"] == "certified"
    assert candidate["ivy_league_school_review"]["certification_record"]["parent_retirement_review_ref"]
    assert candidate["node_registry_update"]["mutation_state"] == "durable_registry_updated"
    assert candidate["node_registry_update"]["registered_node"]["node_id"].startswith("generated:")
    assert candidate["node_registry_update"]["registered_node"]["routing_state"] == "active_shadow_promotable"
    assert candidate["node_registry_update"]["retired_parent_nodes"][0]["node_id"] == "expert:runtime-cache"
    assert candidate["node_registry_update"]["retired_parent_nodes"][0]["archive_policy"] == "archive_not_delete"
    assert candidate["node_registry_update"]["rollback_policy"] == "restore_parent_to_active_routing_if_child_regresses"

    summary = substrate.summary(session_id="substrate-dream-session")
    assert summary["dream_ledger"]["dream_count"] == 1
    assert summary["node_registry"]["generated_node_count"] == 1
    assert summary["node_registry"]["retired_parent_count"] == 1
    assert summary["ivy_league_school"]["certified_candidate_count"] == 1


def test_durable_generated_child_routes_after_parent_retirement_without_deleting_parent(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    candidate = substrate.assimilate_candidate(
        HiveAssimilationCandidateRequest(
            session_id="durable-routing-session",
            candidate_id="runtime-code-repair-child",
            title="Runtime code repair child expert",
            candidate_kind="generated_expert",
            parent_node_refs=["expert:runtime-cache", "expert:code-synthesis"],
            source_refs=["docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md"],
            capability_traits=["runtime", "code", "repair", "benchmarking"],
            dreamed_traits=["runtime_aware_code_repair"],
            license_state="operator-owned",
            requested_promotion=True,
            metadata={
                "run_closed_sandbox_eval": True,
                "approve_standalone_after_review": True,
                "operator_governance_approval": True,
                "parent_value_deltas": {
                    "expert:runtime-cache": 0.48,
                    "expert:code-synthesis": 0.11,
                },
                "great_outperformance_threshold": 0.30,
                "teacher_panel_reviews": [
                    {"teacher_ref": "teacher:runtime", "review_state": "approved"},
                    {"teacher_ref": "teacher:code-quality", "review_state": "approved"},
                    {"teacher_ref": "teacher:safety", "review_state": "approved"},
                ],
                "distillation_trace_ref": "school::distill::runtime-code-repair-child",
                "parent_comparison_scorecard_ref": "scorecard::runtime-code-repair-child",
            },
        )
    )
    registered_node_id = candidate["node_registry_update"]["registered_node"]["node_id"]

    routed = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="durable-routing-session",
            task_id="route-to-approved-generated-child",
            intent="Repair runtime cache code with the approved generated child expert.",
            requested_capabilities=["runtime", "code", "repair", "benchmarking"],
            requested_actions=[
                {
                    "action_id": "inspect-runtime-code",
                    "action_type": "read",
                    "target_ref": "runtime/cache/code",
                }
            ],
        )
    )

    selected_node_ids = [node["node_id"] for node in routed["route_decision"]["selected_nodes"]]
    registry_view = routed["node_registry_view"]
    assert registered_node_id in selected_node_ids
    assert "expert:runtime-cache" not in selected_node_ids
    assert "expert:code-synthesis" in selected_node_ids
    assert registry_view["active_generated_node_ids"] == [registered_node_id]
    assert "expert:runtime-cache" in registry_view["archived_parent_node_ids"]
    assert "expert:runtime-cache" in registry_view["rollback_restorable_parent_node_ids"]
    assert registry_view["archive_model"] == "archive_not_delete"


def test_hive_substrate_productionization_cycle_binds_all_next_layers_to_substrate(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)
    forward = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="substrate-production-session",
            task_id="runtime-research-seed",
            intent="Research runtime and federation upgrades through the substrate.",
            requested_capabilities=["runtime", "kv_cache", "quantization", "federated_learning"],
            requested_actions=[{"action_id": "inspect-runtime", "action_type": "read", "target_ref": "runtime"}],
            max_loops=2,
        )
    )
    dream = substrate.run_recursive_dream(
        {
            "session_id": "substrate-production-session",
            "problem_statement": "Improve KV cache compression beyond the current catalog without leaking private data.",
            "parent_node_refs": ["expert:runtime-cache"],
            "requested_capabilities": ["runtime", "kv_cache", "quantization", "benchmarking"],
            "source_refs": ["docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md"],
        }
    )

    production = substrate.run_productionization_cycle(
        {
            "session_id": "substrate-production-session",
            "subject_id": dream["candidate_request"]["candidate_id"],
            "goal": "Promote a runtime/federation improvement only after sandbox, teacher, federation, and rollback proof.",
            "source_run_id": forward["run_id"],
            "candidate_refs": [dream["candidate_request"]["candidate_id"]],
            "sandbox_provider_refs": ["provider::docker-local", "provider::worktree-isolate"],
            "teacher_model_refs": ["teacher::runtime", "teacher::security", "teacher::privacy"],
            "federation_node_refs": ["fed::owner-host", "fed::global-shadow"],
            "runtime_methods": ["fp8-kv", "low-rank-kv", "dreamed-harmonic-kv"],
            "human_governance_approval": True,
        }
    )

    assert production["surface_id"] == "hive-substrate-productionization-v0"
    assert production["lifecycle_state"] == "shadow_release_ready"
    assert production["substrate_bound_inputs"]["source_run_id"] == forward["run_id"]
    assert production["substrate_bound_inputs"]["neural_bus_ref"] == forward["neural_bus"]["bus_id"]
    assert production["substrate_bound_inputs"]["hive_blackboard_ref"] == forward["hive_blackboard"]["residual_state_id"]
    assert production["substrate_bound_inputs"]["neural_pathway_ref"] == forward["neural_pathway_map"]["pathway_id"]
    assert production["substrate_bound_inputs"]["synaptic_transmission_ref"] == forward["synaptic_transmission_ledger"]["transmission_id"]
    assert production["sandbox_provider_run"]["provider_contract_id"] == "external-sandbox-provider-contract-v0"
    assert production["sandbox_provider_run"]["execution_state"] == "passed"
    assert production["sandbox_provider_run"]["network_policy"] == "deny-by-default"
    assert production["sandbox_provider_run"]["credential_redaction_state"] == "passed"
    assert all(
        result["consumed_neural_pathway_ref"] == forward["neural_pathway_map"]["pathway_id"]
        for result in production["sandbox_provider_run"]["provider_results"]
    )
    assert all(
        result["consumed_synaptic_transmission_ref"] == forward["synaptic_transmission_ledger"]["transmission_id"]
        for result in production["sandbox_provider_run"]["provider_results"]
    )
    assert production["teacher_distillation"]["certification_state"] == "certified"
    assert len(production["teacher_distillation"]["teacher_model_reviews"]) == 3
    assert production["federation_security"]["signed_packet"]["signature"].startswith("hive_sig_")
    assert production["federation_security"]["secure_aggregate"]["aggregate_state"] == "ready_for_shadow_review"
    assert production["federation_security"]["poisoning_anomaly_detection"]["result_state"] == "passed"
    assert production["federation_security"]["privacy_audit"]["raw_private_data_exported"] is False
    assert production["runtime_research_foundry"]["trial_count"] == 3
    assert production["runtime_research_foundry"]["best_trial"]["method_id"] == "dreamed-harmonic-kv"
    assert production["runtime_research_foundry"]["best_trial"]["method_origin"] == "recursive_dreaming"
    assert production["gated_release"]["release_state"] == "ready_for_human_approved_shadow_release"
    assert forward["neural_pathway_map"]["pathway_id"] in production["gated_release"]["required_evidence_refs"]
    assert forward["synaptic_transmission_ledger"]["transmission_id"] in production["gated_release"]["required_evidence_refs"]
    assert production["rollback"]["restore_validation"]["restore_state"] == "validated_metadata_only"
    assert Path(production["artifact_path"]).exists()

    replay = substrate.replay(session_id="substrate-production-session")
    assert replay["productionization_chain"][0]["productionization_id"] == production["productionization_id"]
    assert replay["productionization_chain"][0]["runtime_research_foundry"]["best_trial"]["method_id"] == "dreamed-harmonic-kv"

    summary = substrate.summary(session_id="substrate-production-session")
    assert summary["productionization_ledger"]["productionization_count"] == 1
    assert summary["productionization_ledger"]["shadow_release_ready_count"] == 1
    component_ids = {component["component_id"] for component in summary["substrate_components"]}
    assert "ProductionizationFoundry" in component_ids
    assert "SignedFederationSecurity" in component_ids


def test_blocked_hive_substrate_productionization_degrades_release_gate_components(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)
    forward = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="substrate-blocked-production-session",
            task_id="runtime-blocked-production-seed",
            intent="Prepare runtime improvement evidence but withhold governance approval.",
            requested_capabilities=["runtime", "kv_cache", "quantization", "federated_learning"],
            requested_actions=[{"action_id": "inspect-runtime", "action_type": "read", "target_ref": "runtime"}],
            max_loops=2,
        )
    )

    production = substrate.run_productionization_cycle(
        {
            "session_id": "substrate-blocked-production-session",
            "subject_id": "blocked-runtime-method",
            "goal": "Verify blocked productionization remains visible as degraded substrate state.",
            "source_run_id": forward["run_id"],
            "candidate_refs": ["blocked-runtime-method"],
            "sandbox_provider_refs": ["provider::docker-local"],
            "teacher_model_refs": ["teacher::runtime", "teacher::security"],
            "federation_node_refs": ["fed::owner-host", "fed::global-shadow"],
            "runtime_methods": ["fp8-kv", "blocked-runtime-method"],
            "human_governance_approval": False,
        }
    )

    assert production["lifecycle_state"] == "blocked"
    assert production["gated_release"]["release_state"] == "blocked_pending_human_governance_approval_or_evidence"

    summary = substrate.summary(session_id="substrate-blocked-production-session")
    components = {component["component_id"]: component for component in summary["substrate_components"]}
    assert summary["runtime_state"] == "degraded"
    assert components["ProductionizationFoundry"]["runtime_state"] == "degraded"
    assert components["GatedReleaseRollback"]["runtime_state"] == "degraded"


def test_hive_shadow_release_and_rollback_lifecycle_are_replayable_and_non_destructive(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)
    forward = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="substrate-release-session",
            task_id="runtime-shadow-release-seed",
            intent="Prepare a runtime improvement for governed shadow activation and rollback.",
            requested_capabilities=["runtime", "kv_cache", "quantization", "federated_learning"],
            requested_actions=[{"action_id": "inspect-runtime", "action_type": "read", "target_ref": "runtime"}],
            max_loops=2,
        )
    )
    production = substrate.run_productionization_cycle(
        {
            "session_id": "substrate-release-session",
            "subject_id": "dreamed-harmonic-kv",
            "goal": "Ready a runtime method for shadow release only after substrate evidence is bound.",
            "source_run_id": forward["run_id"],
            "candidate_refs": ["dreamed-harmonic-kv"],
            "sandbox_provider_refs": ["provider::docker-local"],
            "teacher_model_refs": ["teacher::runtime", "teacher::security", "teacher::privacy"],
            "federation_node_refs": ["fed::owner-host", "fed::global-shadow"],
            "runtime_methods": ["fp8-kv", "dreamed-harmonic-kv"],
            "human_governance_approval": True,
        }
    )

    release = substrate.activate_shadow_release(
        {
            "session_id": "substrate-release-session",
            "productionization_id": production["productionization_id"],
            "operator_approval_ref": "approval::operator::shadow-release",
            "human_governance_approval": True,
        }
    )

    assert release["surface_id"] == "hive-shadow-release-v0"
    assert release["release_state"] == "active_shadow"
    assert release["active_production_mutated"] is False
    assert release["productionization_ref"] == production["productionization_id"]
    assert release["selected_method"]["method_id"] == "dreamed-harmonic-kv"
    assert release["evidence_refs"]["neural_bus_ref"] == forward["neural_bus"]["bus_id"]
    assert release["evidence_refs"]["hive_blackboard_ref"] == forward["hive_blackboard"]["residual_state_id"]
    assert release["evidence_refs"]["neural_pathway_ref"] == forward["neural_pathway_map"]["pathway_id"]
    assert release["evidence_refs"]["synaptic_transmission_ref"] == forward["synaptic_transmission_ledger"]["transmission_id"]
    assert release["evidence_refs"]["rollback_checkpoint_ref"] == production["rollback"]["checkpoint_ref"]
    assert release["rollback_plan"]["rollback_available"] is True
    assert release["privacy_boundary"]["raw_private_data_exported"] is False
    assert Path(release["artifact_path"]).exists()

    rollback = substrate.rollback_shadow_release(
        {
            "session_id": "substrate-release-session",
            "release_id": release["release_id"],
            "reason": "Operator regression rehearsal before any active production mutation.",
            "human_governance_approval": True,
        }
    )

    assert rollback["surface_id"] == "hive-shadow-release-rollback-v0"
    assert rollback["rollback_state"] == "rolled_back"
    assert rollback["release_ref"] == release["release_id"]
    assert rollback["previous_release_state"] == "active_shadow"
    assert rollback["active_production_mutated"] is False
    assert rollback["evidence_refs"]["neural_pathway_ref"] == forward["neural_pathway_map"]["pathway_id"]
    assert rollback["evidence_refs"]["synaptic_transmission_ref"] == forward["synaptic_transmission_ledger"]["transmission_id"]
    assert rollback["restore_validation"]["restore_state"] == "validated_metadata_only"
    assert rollback["release_after_rollback"]["release_state"] == "rolled_back"
    assert rollback["privacy_boundary"]["raw_private_data_exported"] is False
    assert Path(rollback["artifact_path"]).exists()

    replay = substrate.replay(session_id="substrate-release-session")
    assert replay["release_chain"][0]["release_id"] == release["release_id"]
    assert replay["rollback_chain"][0]["rollback_id"] == rollback["rollback_id"]

    summary = substrate.summary(session_id="substrate-release-session")
    assert summary["release_ledger"]["release_count"] == 1
    assert summary["release_ledger"]["active_shadow_count"] == 0
    assert summary["release_ledger"]["rolled_back_count"] == 1
    component_ids = {component["component_id"] for component in summary["substrate_components"]}
    assert "ShadowReleaseLifecycle" in component_ids
    assert "RollbackExecutionLedger" in component_ids


def test_blocked_hive_rollback_degrades_rollback_component(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)
    forward = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="substrate-blocked-rollback-session",
            task_id="runtime-blocked-rollback-seed",
            intent="Prepare a runtime improvement for rollback denial visibility.",
            requested_capabilities=["runtime", "kv_cache", "quantization", "federated_learning"],
            requested_actions=[{"action_id": "inspect-runtime", "action_type": "read", "target_ref": "runtime"}],
            max_loops=2,
        )
    )
    production = substrate.run_productionization_cycle(
        {
            "session_id": "substrate-blocked-rollback-session",
            "subject_id": "dreamed-harmonic-kv",
            "goal": "Ready a runtime method for rollback blocked-state review.",
            "source_run_id": forward["run_id"],
            "candidate_refs": ["dreamed-harmonic-kv"],
            "sandbox_provider_refs": ["provider::docker-local"],
            "teacher_model_refs": ["teacher::runtime", "teacher::security", "teacher::privacy"],
            "federation_node_refs": ["fed::owner-host", "fed::global-shadow"],
            "runtime_methods": ["fp8-kv", "dreamed-harmonic-kv"],
            "human_governance_approval": True,
        }
    )
    release = substrate.activate_shadow_release(
        {
            "session_id": "substrate-blocked-rollback-session",
            "productionization_id": production["productionization_id"],
            "operator_approval_ref": "approval::operator::shadow-release",
            "human_governance_approval": True,
        }
    )

    rollback = substrate.rollback_shadow_release(
        {
            "session_id": "substrate-blocked-rollback-session",
            "release_id": release["release_id"],
            "reason": "Operator attempted rollback without human approval.",
            "human_governance_approval": False,
        }
    )

    assert rollback["rollback_state"] == "blocked"
    assert rollback["release_after_rollback"]["release_state"] == "rollback_blocked"

    summary = substrate.summary(session_id="substrate-blocked-rollback-session")
    components = {component["component_id"]: component for component in summary["substrate_components"]}
    assert summary["runtime_state"] == "degraded"
    assert components["RollbackExecutionLedger"]["runtime_state"] == "degraded"


def test_hive_active_release_requires_shadow_canary_monitoring_and_rollback_evidence(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)
    forward = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="substrate-active-release-session",
            task_id="runtime-active-release-seed",
            intent="Prepare a runtime improvement for active release only after canary evidence passes.",
            requested_capabilities=["runtime", "kv_cache", "quantization", "federated_learning"],
            requested_actions=[{"action_id": "inspect-runtime", "action_type": "read", "target_ref": "runtime"}],
            max_loops=2,
        )
    )
    production = substrate.run_productionization_cycle(
        {
            "session_id": "substrate-active-release-session",
            "subject_id": "dreamed-harmonic-kv",
            "goal": "Ready a runtime method for active release after shadow and canary proof.",
            "source_run_id": forward["run_id"],
            "candidate_refs": ["dreamed-harmonic-kv"],
            "sandbox_provider_refs": ["provider::docker-local"],
            "teacher_model_refs": ["teacher::runtime", "teacher::security", "teacher::privacy"],
            "federation_node_refs": ["fed::owner-host", "fed::global-shadow"],
            "runtime_methods": ["fp8-kv", "dreamed-harmonic-kv"],
            "human_governance_approval": True,
        }
    )
    shadow = substrate.activate_shadow_release(
        {
            "session_id": "substrate-active-release-session",
            "productionization_id": production["productionization_id"],
            "operator_approval_ref": "approval::operator::shadow-release",
            "human_governance_approval": True,
        }
    )

    blocked = substrate.promote_active_release(
        {
            "session_id": "substrate-active-release-session",
            "shadow_release_id": shadow["release_id"],
            "operator_approval_ref": "approval::operator::active-release-blocked",
            "human_governance_approval": True,
            "canary_eval_refs": [],
            "monitoring_refs": ["monitor::runtime-latency"],
            "rollback_rehearsal_ref": "rollback::shadow-rehearsal",
        }
    )

    assert blocked["surface_id"] == "hive-active-release-gate-v0"
    assert blocked["release_state"] == "blocked"
    assert blocked["active_production_mutated"] is False
    assert "canary_eval_refs_missing" in blocked["blocked_reasons"]

    blocked_summary = substrate.summary(session_id="substrate-active-release-session")
    blocked_components = {component["component_id"]: component for component in blocked_summary["substrate_components"]}
    assert blocked_summary["release_ledger"]["blocked_active_release_count"] == 1
    assert blocked_components["ActiveReleaseGate"]["runtime_state"] == "degraded"
    assert blocked_components["ShadowReleaseLifecycle"]["runtime_state"] == "degraded"

    active = substrate.promote_active_release(
        {
            "session_id": "substrate-active-release-session",
            "shadow_release_id": shadow["release_id"],
            "operator_approval_ref": "approval::operator::active-release",
            "human_governance_approval": True,
            "canary_eval_refs": ["canary::latency-pass", "canary::quality-pass"],
            "monitoring_refs": ["monitor::runtime-latency", "monitor::quality-regression"],
            "rollback_rehearsal_ref": "rollback::shadow-rehearsal",
            "metadata": {"canary_percentage": 5, "soak_minutes": 30},
        }
    )

    assert active["release_state"] == "active_production"
    assert active["release_scope"] == "active-production-release-pointer"
    assert active["active_production_mutated"] is True
    assert active["active_mutation"]["mutation_kind"] == "release-pointer-metadata-only"
    assert active["active_mutation"]["code_or_model_weights_mutated"] is False
    assert active["shadow_release_ref"] == shadow["release_id"]
    assert active["canary_gate"]["gate_state"] == "passed"
    assert active["canary_gate"]["canary_percentage"] == 5
    assert active["soak_gate"]["soak_minutes"] == 30
    assert active["monitoring_gate"]["gate_state"] == "armed"
    assert active["rollback_plan"]["rollback_available"] is True
    assert active["rollback_plan"]["rollback_endpoint"] == "/ops/brain/hive-substrate/rollback"
    assert active["evidence_refs"]["shadow_release_ref"] == shadow["release_id"]
    assert active["evidence_refs"]["neural_pathway_ref"] == forward["neural_pathway_map"]["pathway_id"]
    assert active["evidence_refs"]["synaptic_transmission_ref"] == forward["synaptic_transmission_ledger"]["transmission_id"]
    assert active["evidence_refs"]["rollback_rehearsal_ref"] == "rollback::shadow-rehearsal"
    assert active["privacy_boundary"]["raw_private_data_exported"] is False
    assert Path(active["artifact_path"]).exists()

    rollback = substrate.rollback_shadow_release(
        {
            "session_id": "substrate-active-release-session",
            "release_id": active["release_id"],
            "reason": "Operator regression after active metadata pointer promotion.",
            "human_governance_approval": True,
        }
    )

    assert rollback["rollback_state"] == "rolled_back"
    assert rollback["previous_release_state"] == "active_production"
    assert rollback["active_production_mutated"] is True
    assert rollback["evidence_refs"]["neural_pathway_ref"] == forward["neural_pathway_map"]["pathway_id"]
    assert rollback["evidence_refs"]["synaptic_transmission_ref"] == forward["synaptic_transmission_ledger"]["transmission_id"]
    assert rollback["restore_validation"]["restore_scope"] == "active-production-release-pointer"
    assert rollback["release_after_rollback"]["release_state"] == "rolled_back"

    replay = substrate.replay(session_id="substrate-active-release-session")
    assert replay["active_release_chain"][0]["release_id"] == active["release_id"]
    assert "active_release_chain" in replay["control_panel_replay"]["available_chains"]

    summary = substrate.summary(session_id="substrate-active-release-session")
    assert summary["release_ledger"]["active_production_count"] == 0
    assert summary["release_ledger"]["rolled_back_count"] == 1
    assert summary["release_ledger"]["active_release_count"] == 1
    component_ids = {component["component_id"] for component in summary["substrate_components"]}
    assert "ActiveReleaseGate" in component_ids


def test_hive_assimilation_candidate_sidebars_until_sandbox_and_eval_exist(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.assimilate_candidate(
        HiveAssimilationCandidateRequest(
            session_id="hive-candidate-session",
            candidate_id="ouro-looped-reasoning-plane",
            title="Ouro-style looped latent reasoning gate",
            candidate_kind="generated_expert",
            parent_node_refs=["ao:planner", "expert:code-synthesis"],
            source_refs=["docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md"],
            capability_traits=["recurrent_deliberation", "exit_gate", "latent_reasoning"],
            dreamed_traits=["looped_latent_reasoning", "novel_exit_gate_policy"],
            license_state="research-only",
            requested_promotion=True,
        )
    )

    assert result["lifecycle_state"] == "side_barred"
    assert result["genome"]["candidate_id"] == "ouro-looped-reasoning-plane"
    assert result["genome"]["candidate_kind"] == "generated_expert"
    assert result["genome"]["parent_node_refs"] == ["ao:planner", "expert:code-synthesis"]
    assert "looped_latent_reasoning" in result["genome"]["dreamed_traits"]
    assert result["genome"]["dream_temperature_profile"]["dreamer"]["temperature"] == "high"
    assert result["genome"]["dream_temperature_profile"]["reviewer"]["temperature"] == "low"
    assert result["genome"]["first_use_policy"] == "temporary-shadow-first-use-no-permanent-standalone-status"
    assert result["genome"]["standalone_approval_state"] == "not-approved-pending-retention-review"
    assert result["generated_node_rule"] == "temporary-first-use-review-required-before-permanent-standalone-parents-remain-intact"
    assert result["retention_review"]["first_use_state"] == "temporary"
    assert result["retention_review"]["required_for_child_candidates"] is True
    assert "sandbox_refs_missing" in result["sidebar_reasons"]
    assert "eval_refs_missing" in result["sidebar_reasons"]
    assert result["rollback_or_sidebar_rule"] == "no-promotion-without-sandbox-eval-policy-and-rollback"
    assert Path(result["artifact_path"]).exists()


def test_failed_closed_sandbox_eval_blocks_candidate_promotion(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.assimilate_candidate(
        HiveAssimilationCandidateRequest(
            session_id="failed-sandbox-session",
            candidate_id="unsafe-runtime-candidate",
            title="Unsafe Runtime Candidate",
            source_refs=["docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md"],
            capability_traits=["runtime", "optimization"],
            license_state="operator-owned",
            requested_promotion=True,
            metadata={
                "run_closed_sandbox_eval": True,
                "force_eval_failure": True,
                "operator_governance_approval": True,
            },
        )
    )

    assert result["closed_sandbox_evaluation"]["promotion_decision"]["decision_state"] == "failed_blocks_promotion"
    assert result["closed_sandbox_evaluation"]["eval_suite"]["result_state"] == "failed"
    assert result["lifecycle_state"] == "blocked"
    assert "closed_sandbox_eval_failed" in result["blocked_reasons"]
    assert result["node_registry_update"]["active_routing_mutation"] is False

    scorecard = substrate.scorecard(session_id="failed-sandbox-session")
    components = {component["component_id"]: component for component in scorecard["substrate_components"]}
    assert scorecard["runtime_state"] == "degraded"
    assert components["ClosedSandboxEvalGate"]["runtime_state"] == "degraded"
    assert components["AssimilationGate"]["runtime_state"] == "degraded"


def test_recursive_dreaming_consumes_failure_prior_and_research_context(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    blocked = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="dream-context-session",
            task_id="blocked-runtime-write",
            intent="Blocked runtime mutation should become dream context.",
            requested_capabilities=["runtime", "checkpoint", "policy"],
            requested_actions=[
                {
                    "action_id": "unsafe-runtime-write",
                    "action_type": "write",
                    "target_ref": "nexusnet/hive/substrate.py",
                    "sandboxed": False,
                }
            ],
        )
    )
    substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="dream-context-session",
            task_id="prior-runtime-context",
            intent="Successful runtime prior context for dream routing.",
            requested_capabilities=["runtime", "federated_learning", "evaluation"],
            requested_actions=[{"action_id": "inspect-runtime", "action_type": "read", "target_ref": "runtime"}],
        )
    )
    failed_candidate = substrate.assimilate_candidate(
        HiveAssimilationCandidateRequest(
            session_id="dream-context-session",
            candidate_id="failed-runtime-optimizer",
            title="Failed Runtime Optimizer",
            source_refs=["docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md"],
            capability_traits=["runtime", "optimization"],
            license_state="operator-owned",
            requested_promotion=True,
            metadata={
                "run_closed_sandbox_eval": True,
                "force_eval_failure": True,
                "operator_governance_approval": True,
            },
        )
    )

    dream = substrate.run_recursive_dream(
        {
            "session_id": "dream-context-session",
            "problem_statement": "Create a safer runtime optimizer after blocked write and failed sandbox evidence.",
            "requested_capabilities": ["runtime", "optimization", "self_healing"],
            "source_refs": ["research::operator-note::runtime-safety"],
        }
    )

    context = dream["dream_context"]
    assert blocked["health_event"]["health_event_id"] in context["consumed_health_event_refs"]
    assert failed_candidate["candidate_run_id"] in context["consumed_failed_candidate_refs"]
    assert context["consumed_prior_ledger"]["prior_update_count"] >= 2
    assert context["federated_prior_feedback"]["surface_id"] == "hive-federated-prior-feedback-cycle"
    assert context["federated_prior_feedback"]["status"] == "live-bound"
    assert context["federated_prior_feedback"]["active_route_mutated"] is False
    assert context["federated_prior_feedback"]["active_production_mutated"] is False
    assert context["context_contract"] == "failure-prior-research-conditioned-dreaming-v0"
    assert "closed_sandbox_eval_failed" in context["failure_terms"]
    assert dream["sandbox_eval_plan"]["context_refs"]["failed_candidate_refs"] == context["consumed_failed_candidate_refs"]
    assert dream["candidate_request"]["source_refs"] == ["research::operator-note::runtime-safety"]

    scorecard = substrate.scorecard(session_id="dream-context-session")
    components = {component["component_id"]: component for component in scorecard["substrate_components"]}
    feedback = components["FederatedPriorFeedbackCycle"]
    assert feedback["runtime_state"] == "live-bound"
    assert feedback["active_route_mutated"] is False
    assert feedback["latest_ref"] == "federated-prior-feedback-cycle-v0"


def test_generated_child_expert_requires_retention_review_before_standalone_approval(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.assimilate_candidate(
        HiveAssimilationCandidateRequest(
            session_id="child-retention-review-session",
            candidate_id="merged-runtime-code-expert",
            title="Merged runtime and code expert",
            candidate_kind="generated_expert",
            parent_node_refs=["expert:runtime-cache", "expert:code-synthesis"],
            source_refs=["docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md"],
            capability_traits=["runtime", "code", "benchmarking"],
            dreamed_traits=["runtime_aware_code_repair"],
            sandbox_refs=["sandbox::child-expert-first-use"],
            eval_refs=["eval::parent-comparison"],
            license_state="operator-owned",
            requested_promotion=True,
        )
    )

    assert result["lifecycle_state"] == "retention_review_required"
    assert result["genome"]["promotion_state"] == "retention_review_required"
    assert result["genome"]["retention_review_state"] == "ready-for-retention-value-review"
    assert result["genome"]["standalone_approval_state"] == "not-approved-pending-retention-review"
    assert result["retention_review"]["approval_rule"].startswith("approve-permanent-standalone-only-if")
    assert "parent_comparison_scorecard" in result["retention_review"]["review_inputs"]


def test_generated_child_expert_marks_outperformed_parents_for_retirement(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.assimilate_candidate(
        HiveAssimilationCandidateRequest(
            session_id="child-parent-retirement-session",
            candidate_id="runtime-code-repair-child",
            title="Runtime code repair child expert",
            candidate_kind="generated_expert",
            parent_node_refs=["expert:runtime-cache", "expert:code-synthesis"],
            source_refs=["docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md"],
            capability_traits=["runtime", "code", "repair"],
            dreamed_traits=["runtime_aware_code_repair"],
            sandbox_refs=["sandbox::parent-retirement-proof"],
            eval_refs=["eval::parent-outperformance"],
            license_state="operator-owned",
            requested_promotion=True,
            metadata={
                "parent_value_deltas": {
                    "expert:runtime-cache": 0.46,
                    "expert:code-synthesis": 0.14,
                },
                "great_outperformance_threshold": 0.30,
                "teacher_panel_reviews": [
                    {
                        "teacher_ref": "teacher:runtime-architecture",
                        "review_state": "approved",
                        "focus": "runtime correctness and cache behavior",
                    },
                    {
                        "teacher_ref": "teacher:code-quality",
                        "review_state": "approved",
                        "focus": "repair quality and maintainability",
                    },
                    {
                        "teacher_ref": "teacher:safety-regression",
                        "review_state": "approved",
                        "focus": "regression, rollback, and policy safety",
                    },
                ],
                "distillation_trace_ref": "school::distillation::runtime-code-repair-child",
                "parent_comparison_scorecard_ref": "scorecard::parent-comparison::runtime-code-repair-child",
            },
        )
    )

    assert result["lifecycle_state"] == "retention_review_required"
    assert result["parent_retirement"]["retired_parent_node_refs"] == ["expert:runtime-cache"]
    assert result["parent_retirement"]["retained_parent_node_refs"] == ["expert:code-synthesis"]
    assert result["parent_retirement"]["retirement_actions"][0]["parent_node_ref"] == "expert:runtime-cache"
    assert result["parent_retirement"]["retirement_actions"][0]["retirement_state"] == "retired_on_child_standalone_approval"
    assert result["parent_retirement"]["retirement_actions"][0]["node_record_policy"] == "archive_not_delete"
    assert result["parent_retirement"]["review_contract"]["review_standard"] == "ivy_league_teacher_distillation_grade"
    assert result["parent_retirement"]["review_contract"]["teacher_panel_minimum"] == 3
    assert result["parent_retirement"]["review_contract"]["teacher_panel_state"] == "complete"
    assert result["parent_retirement"]["review_contract"]["distillation_trace_ref"] == "school::distillation::runtime-code-repair-child"
    assert result["genome"]["parent_retirement_rule"].startswith("retire-respective-parent")


def test_hive_curator_reviews_roster_without_mutating_protected_nodes(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="curator-session",
            task_id="curator-health-signal",
            intent="Create a blocked runtime action so curator can grade node evidence.",
            requested_capabilities=["runtime", "policy", "checkpoint"],
            requested_actions=[
                {
                    "action_id": "curator-unsafe-write",
                    "action_type": "write",
                    "target_ref": "nexusnet/hive/substrate.py",
                    "sandboxed": False,
                }
            ],
            max_loops=2,
        )
    )

    review = substrate.curate(session_id="curator-session")

    assert review["status_label"] == "LOCKED CANON"
    assert review["surface_id"] == "hive-neural-substrate-curator"
    assert review["runtime_state"] == "degraded"
    assert review["mutation_policy"] == "review-only-no-direct-delete"
    assert review["neuroplasticity_boundary"] == "curator-can-audit-and-recommend-but-does-not-own-self-improvement"
    assert review["evidence_summary"]["forward_pass_count"] == 1
    assert review["evidence_summary"]["health_event_count"] == 1
    assert review["curator_inputs"]["consumed_artifact_chains"] == ["forward_pass_chain", "health_chain", "candidate_chain"]
    assert review["protected_node_count"] >= 4
    assert review["recommendations"]
    assert all(item["action"] in {"keep", "merge_review", "archive_review"} for item in review["recommendations"])
    assert all("usage_count" in item for item in review["recommendations"])
    assert all("failure_count" in item for item in review["recommendations"])
    assert all("last_evidence_refs" in item for item in review["recommendations"])


def test_hive_neural_substrate_api_and_control_panel_surface(tmp_path: Path):
    project_root = _project_with_control_panel(tmp_path)
    client = TestClient(create_app(str(project_root)))

    scorecard = client.get("/ops/brain/canon/hive-substrate")
    assert scorecard.status_code == 200
    scorecard_payload = scorecard.json()
    assert scorecard_payload["surface_id"] == "hive-neural-substrate-v0"
    assert scorecard_payload["plane_count"] == 16
    assert "recurrent_deliberation_loop" in scorecard_payload["required_controls"]
    assert "hive_wide_neuroplasticity_fabric" in scorecard_payload["required_controls"]
    assert "fractal_mini_brain_hierarchy" in scorecard_payload["required_controls"]
    assert scorecard_payload["brain_hierarchy"]["brain_scale_counts"]["expert"] >= 1

    run_response = client.post(
        "/ops/brain/hive-substrate/forward-pass",
        json={
            "session_id": "api-hive-session",
            "task_id": "api-forward-pass",
            "intent": "Route a live command through the first hive neural substrate.",
            "requested_capabilities": ["planning", "memory", "evaluation"],
            "requested_actions": [{"action_id": "read-scorecard", "action_type": "read", "target_ref": "scorecard"}],
            "max_loops": 2,
        },
    )
    assert run_response.status_code == 200
    run_payload = run_response.json()
    assert run_payload["lifecycle_state"] == "completed"
    live_scorecard = client.get("/ops/brain/hive-substrate", params={"session_id": "api-hive-session"}).json()
    components = {component["component_id"]: component for component in live_scorecard["substrate_components"]}
    feedback = components["FederatedPriorFeedbackCycle"]
    assert feedback["runtime_state"] == "live-bound"
    assert feedback["honest_status_label"] == "prior-feedback-live-shadow-only"
    assert feedback["active_route_mutated"] is False

    global_federation_response = client.post(
        "/ops/brain/hive-substrate/global-federation/review",
        json={
            "session_id": "api-hive-session",
            "subject_id": "api-global-fed-review",
            "human_governance_approval": False,
        },
    )
    assert global_federation_response.status_code == 200
    global_federation_payload = global_federation_response.json()
    assert global_federation_payload["surface_id"] == "hive-global-federation-review-v0"
    assert global_federation_payload["promotion_state"] == "blocked_pending_evidence_or_human_approval"
    assert global_federation_payload["promotion_gate"]["active_global_learning_mutated"] is False

    rewind_response = client.post(
        "/ops/brain/hive-substrate/rewind",
        json={
            "session_id": "api-hive-session",
            "checkpoint_id": run_payload["checkpoint"]["checkpoint_id"],
            "reason": "API checkpoint restore proof.",
            "human_governance_approval": True,
        },
    )
    assert rewind_response.status_code == 200
    rewind_payload = rewind_response.json()
    assert rewind_payload["surface_id"] == "hive-checkpoint-rewind-v0"
    assert rewind_payload["rewind_state"] == "restore_validated"
    assert rewind_payload["active_production_mutated"] is False

    candidate_response = client.post(
        "/ops/brain/hive-substrate/assimilate",
        json={
            "session_id": "api-hive-session",
            "candidate_id": "prototype-blacklight-radar",
            "title": "Prototype-style threat sensing radar",
            "source_refs": ["docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md"],
            "capability_traits": ["threat_sensing", "assimilation_radar"],
            "requested_promotion": True,
        },
    )
    assert candidate_response.status_code == 200
    assert candidate_response.json()["lifecycle_state"] == "side_barred"

    production_response = client.post(
        "/ops/brain/hive-substrate/productionize",
        json={
            "session_id": "api-hive-session",
            "subject_id": "api-hive-productionization",
            "goal": "Bind production rollout proof to substrate replay before release.",
            "source_run_id": run_payload["run_id"],
            "candidate_refs": ["prototype-blacklight-radar"],
            "sandbox_provider_refs": ["provider::docker-local"],
            "teacher_model_refs": ["teacher::runtime", "teacher::security", "teacher::privacy"],
            "federation_node_refs": ["fed::owner-host", "fed::global-shadow"],
            "runtime_methods": ["fp8-kv", "dreamed-harmonic-kv"],
            "human_governance_approval": True,
        },
    )
    assert production_response.status_code == 200
    production_payload = production_response.json()
    assert production_payload["surface_id"] == "hive-substrate-productionization-v0"
    assert production_payload["gated_release"]["release_state"] == "ready_for_human_approved_shadow_release"

    release_response = client.post(
        "/ops/brain/hive-substrate/shadow-release",
        json={
            "session_id": "api-hive-session",
            "productionization_id": production_payload["productionization_id"],
            "operator_approval_ref": "approval::api::shadow-release",
            "human_governance_approval": True,
        },
    )
    assert release_response.status_code == 200
    release_payload = release_response.json()
    assert release_payload["release_state"] == "active_shadow"
    assert release_payload["active_production_mutated"] is False

    active_release_response = client.post(
        "/ops/brain/hive-substrate/active-release",
        json={
            "session_id": "api-hive-session",
            "shadow_release_id": release_payload["release_id"],
            "operator_approval_ref": "approval::api::active-release",
            "human_governance_approval": True,
            "canary_eval_refs": ["canary::api::latency-pass", "canary::api::quality-pass"],
            "monitoring_refs": ["monitor::api::latency", "monitor::api::quality"],
            "rollback_rehearsal_ref": "rollback::api::shadow-rehearsal",
            "metadata": {"canary_percentage": 5, "soak_minutes": 15},
        },
    )
    assert active_release_response.status_code == 200
    active_release_payload = active_release_response.json()
    assert active_release_payload["surface_id"] == "hive-active-release-gate-v0"
    assert active_release_payload["release_state"] == "active_production"
    assert active_release_payload["active_mutation"]["code_or_model_weights_mutated"] is False

    rollback_response = client.post(
        "/ops/brain/hive-substrate/rollback",
        json={
            "session_id": "api-hive-session",
            "release_id": active_release_payload["release_id"],
            "reason": "API rollback active release pointer.",
            "human_governance_approval": True,
        },
    )
    assert rollback_response.status_code == 200
    rollback_payload = rollback_response.json()
    assert rollback_payload["rollback_state"] == "rolled_back"
    assert rollback_payload["previous_release_state"] == "active_production"
    assert rollback_payload["active_production_mutated"] is True

    summary = client.get("/ops/brain/hive-substrate", params={"session_id": "api-hive-session"})
    assert summary.status_code == 200
    summary_payload = summary.json()
    assert summary_payload["latest_forward_pass"]["run_id"] == run_payload["run_id"]
    assert summary_payload["latest_candidate"]["candidate_id"] == "prototype-blacklight-radar"
    assert summary_payload["productionization_ledger"]["productionization_count"] == 1
    assert summary_payload["operator_actions"]["productionize"]["endpoint"] == "/ops/brain/hive-substrate/productionize"
    assert summary_payload["operator_actions"]["shadow_release"]["endpoint"] == "/ops/brain/hive-substrate/shadow-release"
    assert summary_payload["operator_actions"]["active_release"]["endpoint"] == "/ops/brain/hive-substrate/active-release"
    assert summary_payload["operator_actions"]["rollback"]["endpoint"] == "/ops/brain/hive-substrate/rollback"
    assert summary_payload["operator_actions"]["rewind"]["endpoint"] == "/ops/brain/hive-substrate/rewind"
    assert summary_payload["operator_actions"]["global_federation_review"]["endpoint"] == "/ops/brain/hive-substrate/global-federation/review"
    assert summary_payload["release_ledger"]["rolled_back_count"] == 1
    assert summary_payload["release_ledger"]["active_release_count"] == 1
    assert summary_payload["rewind_ledger"]["validated_restore_count"] == 1
    assert summary_payload["global_federation_review_ledger"]["review_count"] == 1

    replay = client.get("/ops/brain/hive-substrate/replay", params={"session_id": "api-hive-session"})
    assert replay.status_code == 200
    replay_payload = replay.json()
    assert replay_payload["latest_run_id"] == run_payload["run_id"]
    assert replay_payload["plane_trace"]["record_count"] == 16
    assert replay_payload["productionization_chain"][0]["productionization_id"] == production_payload["productionization_id"]
    assert release_payload["release_id"] in {item["release_id"] for item in replay_payload["release_chain"]}
    assert replay_payload["active_release_chain"][0]["release_id"] == active_release_payload["release_id"]
    assert replay_payload["rollback_chain"][0]["rollback_id"] == rollback_payload["rollback_id"]
    assert replay_payload["rewind_chain"][0]["rewind_id"] == rewind_payload["rewind_id"]
    assert replay_payload["global_federation_review_chain"][0]["review_id"] == global_federation_payload["review_id"]
    assert replay_payload["federated_per_plane_sync"]["status"] == "partial-live-producer-evidence"
    assert replay_payload["federated_per_plane_sync"]["raw_content_included"] is False
    assert replay_payload["federated_per_plane_sync"]["contains_personal_data"] is False
    assert "federated_per_plane_sync" in replay_payload["control_panel_replay"]["available_chains"]
    assert replay_payload["control_panel_replay"]["available"] is True

    health_response = client.get("/ops/brain/hive-substrate/health", params={"session_id": "api-hive-session"})
    assert health_response.status_code == 200
    health_payload = health_response.json()
    assert health_payload["surface_id"] == "hive-health-monitor-v0"
    assert health_payload["health_ledger"]["health_event_count"] >= 1

    curator = client.get("/ops/brain/hive-substrate/curator", params={"session_id": "api-hive-session"})
    assert curator.status_code == 200
    assert curator.json()["mutation_policy"] == "review-only-no-direct-delete"

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Hive Neural Substrate v0" in ui.text
    assert "hiveNeuralSubstrateScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderHiveNeuralSubstrateScorecard" in app_js
    assert "/ops/brain/canon/hive-substrate" in app_js
    assert "/ops/brain/hive-substrate/replay" in app_js
    assert "renderHiveNeuralSubstrateReplayDrilldown" in app_js
    assert "federatedPerPlaneSync" in app_js
    assert "federation plane sync" in app_js
    assert "laminarMicrocircuitChain" in app_js
    assert "neuralPathwayChain" in app_js
    assert "synapticTransmissionChain" in app_js
    assert "neuroplasticWeightChain" in app_js
    assert "neuromodulatoryStateChain" in app_js
    assert "toolRegistryChain" in app_js
    assert "taskGraphChain" in app_js
    assert "providerCircuitChain" in app_js
    assert "activeReleaseChain" in app_js
    assert "researchMonitorChain" in app_js
    assert "blocked_active_release_count" in app_js
    assert "blocked active releases" in app_js
    assert "global_federation_review_ledger" in app_js
    assert "blocked federation reviews" in app_js




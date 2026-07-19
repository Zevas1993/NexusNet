from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexus.schemas import Message, RetrievalDocumentInput, RetrievalIngestRequest, RetrievalRequest
from nexusnet.core.brain import RuntimeUnavailableError
from nexusnet.memory.quality_ledger import SourceClaimRequest
from nexusnet.schemas import SessionContext
from tests.test_nexus_phase1_foundation import make_project


def _approve_layer10_self_repair_candidate(client: TestClient, proposal_id: str) -> dict:
    evaluated = client.post(
        "/ops/brain/genesis-immune-governance/candidates/evaluate",
        json={
            "candidate_ref": proposal_id,
            "candidate_kind": "self-repair-safe-apply",
            "command": "python -m pytest tests/test_hive_final_waves.py::test_immune_gate_attenuates_anomalies -q",
            "baseline_ref": "baseline::self-repair-safe-apply",
            "rollback_proof_ref": "rollback-proof::self-repair-safe-apply",
            "artifact_trust_ref": "artifact-trust::self-repair-safe-apply",
            "eval_case_refs": ["eval-case::self-repair-safe-apply"],
            "regression_suite_ref": "regression-suite::genesis-self-repair",
            "judge_policy": {
                "human_review_required": True,
                "domain_check_required": True,
                "calibrated_judge_refs": ["judge::genesis-self-repair-held-out"],
            },
        },
    ).json()
    return client.post(
        f"/ops/brain/genesis-immune-governance/candidates/{evaluated['candidate_id']}/decide",
        json={
            "decision": "approve",
            "approved_by": "genesis-self-repair-immune-admin",
            "human_review_ref": "human-review::genesis-self-repair",
            "domain_check_ref": "domain-check::genesis-self-repair",
            "governance_ref": "governance::genesis-self-repair",
        },
    ).json()


def test_genesis_foundation_status_replays_sanitized_layers_0_to_3(tmp_path: Path):
    project_root = make_project(tmp_path)
    session_id = "genesis-private-session-SECRET"
    client = TestClient(create_app(str(project_root)))

    response = client.get("/ops/brain/genesis-foundation", params={"session_id": session_id})
    assert response.status_code == 200
    payload = response.json()

    assert payload["surface_id"] == "nexusnet-genesis-foundation-status"
    assert payload["status_label"] == "LOCKED CANON"
    assert payload["authority"] == "NexusBrain"
    assert payload["foundation_scope"] == "whole-project"
    assert payload["active_production_mutation_allowed"] is False
    assert payload["raw_content_included"] is False

    authority_chain = payload["source_authority_chain"]
    assert authority_chain[0]["source_ref"] == "docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md"
    assert authority_chain[1]["source_ref"] == "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md"
    assert authority_chain[-1]["source_ref"] == "docs/superpowers/specs/2026-07-05-nexusnet-genesis-build-order-design.md"

    source_manifest = payload["canon_source_manifest"]
    assert source_manifest["surface_id"] == "whole-project-canon-source-manifest"
    assert source_manifest["source_count"] >= 7
    assert source_manifest["ingested_source_count"] >= 6
    assert source_manifest["raw_content_included"] is False
    assert "docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md" in source_manifest["source_refs"]

    layer_ids = [layer["layer_id"] for layer in payload["build_layers"][:4]]
    assert layer_ids == [
        "layer-0-canon-repo-truth",
        "layer-1-harness-identity-authority",
        "layer-2-authority-isolation-fabric",
        "layer-3-neural-bus-blackboard-plane-trace",
    ]
    assert all(layer["status"] == "live-control-plane" for layer in payload["build_layers"][:4])
    assert all(layer["production_approved"] is False for layer in payload["build_layers"][:4])

    preflight = payload["harness_preflight"]
    assert preflight["mode"] == "non-mutating"
    assert preflight["decision"] == "review-required"
    assert preflight["loaded_artifact_count"] >= 6
    assert preflight["active_production_mutation_allowed"] is False
    assert preflight["raw_secret_material_loaded"] is False

    authority_envelope = payload["nexusbrain_authority_envelope"]
    assert authority_envelope["authority"] == "NexusBrain"
    assert authority_envelope["mother_brain_owned"] is True
    assert authority_envelope["parent_child_brain_contract"]["parent_ref"] == "NexusBrain"
    assert "production-mutation" in authority_envelope["denied_action_classes"]

    receipt = payload["authority_receipt"]
    assert receipt["decision_authority"] == "NexusBrain"
    assert receipt["decision"] == "review-required"
    assert "read-status" in receipt["allowed_action_classes"]
    assert "production-mutation" in receipt["denied_action_classes"]
    assert receipt["active_production_mutation_allowed"] is False

    isolation = payload["permission_isolation_receipt"]
    assert isolation["sandbox_tier"] == "read-only"
    assert isolation["ambient_credentials_allowed"] is False
    assert isolation["fail_closed"] is True
    assert isolation["active_production_mutation_allowed"] is False

    projection = payload["neural_bus_hive_blackboard_projection"]
    assert projection["typed_event_envelope"]["schema_version"] == "nexusnet-neural-bus-event-envelope-v1"
    assert projection["typed_event_envelope"]["event_privacy_label"] == "sanitized-foundation-status"
    assert projection["hive_blackboard_snapshot"]["schema_version"] == "nexusnet-hive-blackboard-snapshot-v1"
    assert projection["plane_trace"]["schema_version"] == "nexusnet-plane-trace-ledger-v1"
    assert projection["raw_content_included"] is False
    assert projection["active_production_mutation_allowed"] is False

    replay = payload["replay"]
    assert replay["latest_artifact_ref"].startswith("genesis-foundation::")
    assert replay["artifact_ref_kind"] == "content-addressed-sanitized-status"
    assert replay["raw_content_included"] is False

    restarted_client = TestClient(create_app(str(project_root)))
    restarted = restarted_client.get("/ops/brain/genesis-foundation", params={"session_id": session_id}).json()
    assert restarted["replay"]["status"] == "replayed"
    assert restarted["replay"]["latest_artifact_ref"] == replay["latest_artifact_ref"]
    assert [layer["layer_id"] for layer in restarted["build_layers"][:4]] == layer_ids

    visualizer = restarted_client.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]
    assert control_panel["genesis_foundation_status"]["surface_id"] == "nexusnet-genesis-foundation-status"
    assert control_panel["genesis_foundation_status"]["replay"]["latest_artifact_ref"] == replay["latest_artifact_ref"]
    assert control_panel["live_refs"]["genesis_foundation_status"] == "/ops/brain/genesis-foundation"

    serialized = json.dumps(
        {
            "payload": restarted,
            "genesis_foundation_status": control_panel["genesis_foundation_status"],
            "live_ref": control_panel["live_refs"]["genesis_foundation_status"],
        },
        sort_keys=True,
    )
    assert session_id not in serialized
    assert "SECRET" not in serialized
    assert str(project_root) not in serialized
    assert "F:\\" not in serialized


def test_genesis_foundation_replays_live_layer4_hive_substrate_ledgers_after_brain_use(tmp_path: Path):
    project_root = make_project(tmp_path)
    session_id = "genesis-layer4-private-session-SECRET"
    prompt = "Private Genesis Layer 4 SECRET-LAYER4 should not enter substrate replay."
    client = TestClient(create_app(str(project_root)))
    services = client.app.state.services

    result = services.brain.generate(
        session_context=SessionContext(
            session_id=session_id,
            expert="researcher",
            task_type="runtime-heartbeat",
            use_retrieval=False,
            metadata={"graph_plane_tags": ["runtime", "federated_learning"]},
        ),
        prompt=prompt,
        model_hint="mock/default",
    )
    native_hive = result.inference_trace.metrics["native_hive_forward_pass"]
    assert native_hive["status"] == "completed"

    restarted_client = TestClient(create_app(str(project_root)))
    payload = restarted_client.get("/ops/brain/genesis-foundation", params={"session_id": session_id}).json()
    layer4 = payload["layer4_neural_substrate_ledger_spine"]

    assert layer4["surface_id"] == "genesis-layer4-neural-substrate-ledger-spine"
    assert layer4["status"] == "live-substrate"
    assert layer4["source"] == "nexusbrain-generate"
    assert layer4["source_hive_run_id"] == native_hive["hive_run_id"]
    assert layer4["project_heartbeat_id"] == native_hive["project_heartbeat_id"]
    assert layer4["runtime_growth_receipt_id"] == native_hive["runtime_growth_receipt_id"]
    assert layer4["federated_packet_id"] == native_hive["federated_packet_id"]
    assert layer4["raw_content_included"] is False
    assert layer4["active_production_mutation_allowed"] is False

    expected_ledgers = {
        "hive_activation",
        "sensory_input",
        "embedding_tensor",
        "temporal_positional",
        "memory_engram",
        "attention_routing",
        "residual_normalization",
        "sparse_expert_gate",
        "feedforward_expert",
        "laminar_microcircuit",
        "neural_pathway",
        "synaptic_transmission",
        "neuroplastic_weight",
        "neuromodulatory_state",
        "latent_loop_exit",
        "kv_cache_compression",
        "loss_backpropagation",
        "optimizer_school",
        "computational_graph",
        "model_genome",
        "tensor_runtime_kernel",
        "layer_block_stack",
        "durable_storage",
        "checkpoint_coverage",
        "runtime_decision",
        "backend_quantization_execution",
    }
    ledger_ids = {ledger["ledger_id"] for ledger in layer4["ledgers"]}
    assert expected_ledgers <= ledger_ids
    for ledger in layer4["ledgers"]:
        assert ledger["status"] == "covered"
        assert ledger["artifact_ref"]
        assert ledger["surface_id"]
        assert ledger["raw_content_included"] is False
        assert ledger["active_production_mutation_allowed"] is False

    layer4_build_layer = next(
        layer for layer in payload["build_layers"] if layer["layer_id"] == "layer-4-neural-substrate-ledger-spine"
    )
    assert layer4_build_layer["status"] == "live-substrate"
    assert layer4_build_layer["production_approved"] is False
    assert layer4_build_layer["evidence_refs"][0] == layer4["source_hive_run_ref"]

    control_panel = restarted_client.get(
        "/ops/brain/visualizer/state",
        params={"session_id": session_id},
    ).json()["overlay_state"]["control_panel"]
    control_layer4 = control_panel["genesis_foundation_status"]["layer4_neural_substrate_ledger_spine"]
    assert control_layer4["source_hive_run_id"] == native_hive["hive_run_id"]
    assert control_layer4["covered_ledger_count"] >= len(expected_ledgers)

    serialized = json.dumps(
        {
            "layer4": layer4,
            "control_layer4": control_layer4,
            "build_layer": layer4_build_layer,
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-LAYER4" not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized
    assert "F:\\" not in serialized


def test_native_hive_forward_delivers_sanitized_packet_to_approved_peer_and_replays_acknowledgement(
    tmp_path: Path,
    monkeypatch,
):
    received_payloads: list[dict] = []

    class _PeerImportHandler(BaseHTTPRequestHandler):
        def do_POST(self):  # noqa: N802 - HTTP handler contract
            body = self.rfile.read(int(self.headers.get("Content-Length") or "0"))
            received_payloads.append(json.loads(body.decode("utf-8")))
            response = json.dumps(
                {
                    "status": "quarantined-shadow-accepted",
                    "import_id": "remote-native-hive-import::accepted",
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

    monkeypatch.setenv("NEXUSNET_ALLOW_MOCK_RUNTIME", "1")
    peer_server = ThreadingHTTPServer(("127.0.0.1", 0), _PeerImportHandler)
    peer_thread = threading.Thread(target=peer_server.serve_forever, daemon=True)
    peer_thread.start()
    try:
        project_root = make_project(tmp_path)
        session_id = "genesis-native-federation-private-session-SECRET"
        prompt = "Native Hive federation SECRET-NATIVE-FEDERATION must remain sanitized."
        peer_node_id = "peer-native-hive-approved-delivery"
        import_url = (
            f"http://127.0.0.1:{peer_server.server_port}"
            "/ops/wrapper/federated-packets/import"
        )
        client = TestClient(create_app(str(project_root)))

        approval = client.post(
            "/ops/approvals",
            json={
                "subject": "release-wrapper-federated-peer-delivery",
                "decision": "approved",
                "approver": "operator@example.invalid",
                "rationale": "Approve local sanitized native Hive federation delivery.",
                "metadata": {"peer_node_id": peer_node_id, "import_url": import_url},
            },
        )
        assert approval.status_code == 200
        registration = client.post(
            "/ops/wrapper/federated-peers",
            json={
                "peer_node_id": peer_node_id,
                "import_url": import_url,
                "approval_decision_id": approval.json()["decision_id"],
            },
        )
        assert registration.status_code == 200

        result = client.app.state.services.brain.generate(
            session_context=SessionContext(
                session_id=session_id,
                expert="researcher",
                task_type="native-hive-federated-peer-delivery",
                use_retrieval=False,
            ),
            prompt=prompt,
            model_hint="mock/default",
        )
        native_hive = result.inference_trace.metrics["native_hive_forward_pass"]
        delivery = native_hive["native_federated_peer_delivery"]

        assert delivery["status"] == "live-shadow-delivery-active"
        assert delivery["delivery_count"] == 1
        assert delivery["packet_ref"].startswith("federated-packet::")
        assert delivery["privacy_consent_record_id"]
        assert len(received_payloads) == 1
        delivered_payload = received_payloads[0]
        assert delivered_payload["peer_node_id"] == peer_node_id
        assert delivered_payload["packet"]["raw_content_included"] is False
        assert delivered_payload["packet"]["contains_personal_data"] is False
        assert delivered_payload["packet"]["consent_policy"]["sanitized_metadata_federation_allowed"] is True

        deliveries = client.get(
            "/ops/wrapper/federated-deliveries", params={"session_id": session_id}
        ).json()
        assert deliveries["status"] == "live-shadow-delivery-active"
        assert deliveries["delivery_count"] == 1
        assert deliveries["acknowledged_delivery_count"] == 1
        assert deliveries["latest_delivery"]["status"] == "acknowledged-shadow-accepted"

        replayed = TestClient(create_app(str(project_root))).get(
            "/ops/wrapper/federated-deliveries", params={"session_id": session_id}
        ).json()
        assert replayed["replay"]["status"] == "replayed"
        assert replayed["delivery_count"] == 1
        assert replayed["latest_delivery"]["status"] == "acknowledged-shadow-accepted"

        serialized = json.dumps(
            {"native_hive": native_hive, "deliveries": deliveries, "replayed": replayed},
            sort_keys=True,
        )
        assert prompt not in serialized
        assert "SECRET-NATIVE-FEDERATION" not in serialized
        assert session_id not in serialized
        assert peer_node_id not in serialized
        assert import_url not in serialized
    finally:
        peer_server.shutdown()
        peer_server.server_close()
        peer_thread.join(timeout=5)


def test_genesis_foundation_replays_degraded_layer4_ledgers_after_runtime_unavailable(
    tmp_path: Path,
    monkeypatch,
):
    monkeypatch.setenv("NEXUSNET_PRODUCT_MODE", "1")
    monkeypatch.delenv("NEXUSNET_ALLOW_MOCK_RUNTIME", raising=False)
    project_root = make_project(tmp_path)
    session_id = "genesis-layer4-failed-private-session-SECRET"
    prompt = "Private failed Genesis Layer 4 SECRET-FAILED-LAYER4 must stay out of replay."
    client = TestClient(create_app(str(project_root)), raise_server_exceptions=False)

    response = client.post(
        "/chat",
        json={
            "session_id": session_id,
            "message": prompt,
            "model_hint": "ollama/mistral-small:4",
            "rag": False,
        },
    )

    assert response.status_code == 503
    detail = response.json()["detail"]
    native_hive = detail["native_hive_forward_pass"]
    assert native_hive["status"] == "completed"
    assert native_hive["brain_generate_status"] == "runtime-unavailable"
    assert native_hive["critique_status"] == "not-run"
    assert native_hive["hive_run_id"]
    assert native_hive["project_heartbeat_id"]
    assert native_hive["runtime_growth_receipt_id"]
    assert native_hive["federated_packet_id"]
    assert native_hive["raw_content_included"] is False
    assert native_hive["active_production_mutated"] is False

    restarted_client = TestClient(create_app(str(project_root)))
    payload = restarted_client.get("/ops/brain/genesis-foundation", params={"session_id": session_id}).json()
    layer4 = payload["layer4_neural_substrate_ledger_spine"]

    assert layer4["status"] == "degraded"
    assert layer4["honest_status_label"] == "layer4-native-hive-substrate-ledgers-degraded"
    assert layer4["source"] == "nexusbrain-generate"
    assert layer4["source_brain_generate_status"] == "runtime-unavailable"
    assert layer4["source_hive_run_id"] == native_hive["hive_run_id"]
    assert layer4["project_heartbeat_id"] == native_hive["project_heartbeat_id"]
    assert layer4["runtime_growth_receipt_id"] == native_hive["runtime_growth_receipt_id"]
    assert layer4["federated_packet_id"] == native_hive["federated_packet_id"]
    assert layer4["covered_ledger_count"] == layer4["required_ledger_count"]
    assert layer4["missing_ledger_ids"] == []
    assert "nexusbrain_generate_status::runtime-unavailable" in layer4["blockers"]
    assert layer4["raw_content_included"] is False
    assert layer4["active_production_mutation_allowed"] is False

    layer4_build_layer = next(
        layer for layer in payload["build_layers"] if layer["layer_id"] == "layer-4-neural-substrate-ledger-spine"
    )
    assert layer4_build_layer["status"] == "degraded"
    assert layer4_build_layer["production_approved"] is False

    control_panel = restarted_client.get(
        "/ops/brain/visualizer/state",
        params={"session_id": session_id},
    ).json()["overlay_state"]["control_panel"]
    control_layer4 = control_panel["genesis_foundation_status"]["layer4_neural_substrate_ledger_spine"]
    assert control_layer4["status"] == "degraded"
    assert control_layer4["source_hive_run_id"] == native_hive["hive_run_id"]
    assert control_layer4["source_brain_generate_status"] == "runtime-unavailable"

    serialized = json.dumps(
        {
            "detail": detail,
            "layer4": layer4,
            "control_layer4": control_layer4,
            "build_layer": layer4_build_layer,
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-FAILED-LAYER4" not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized
    assert "F:\\" not in serialized


def test_genesis_foundation_records_layer4_heartbeat_when_no_live_adapter_exists(
    tmp_path: Path,
    monkeypatch,
):
    monkeypatch.setenv("NEXUSNET_PRODUCT_MODE", "1")
    monkeypatch.setenv("NEXUSNET_ALLOW_MOCK_RUNTIME", "0")
    project_root = make_project(tmp_path)
    session_id = "genesis-layer4-no-adapter-private-session-SECRET"
    client = TestClient(create_app(str(project_root)), raise_server_exceptions=False)

    def unavailable_adapter(runtime_name: str):
        raise KeyError(runtime_name)

    monkeypatch.setattr(client.app.state.services.runtime_registry, "get_adapter", unavailable_adapter)

    with pytest.raises(RuntimeUnavailableError) as exc_info:
        client.app.state.services.brain.generate(
            session_context=SessionContext(
                session_id=session_id,
                expert="researcher",
                task_type="runtime-unavailable-no-live-adapter",
                use_retrieval=False,
            ),
            prompt="Private no-adapter SECRET-NO-ADAPTER must stay out of Layer 4.",
            model_hint="mock/default",
        )

    detail = exc_info.value.detail
    assert "no-live-runtime-available" in detail["blocked_reasons"]
    native_hive = detail["native_hive_forward_pass"]
    assert native_hive["brain_generate_status"] == "runtime-unavailable"
    assert native_hive["hive_run_id"]
    assert native_hive["runtime_growth_receipt_id"]
    assert native_hive["federated_packet_id"]

    restarted = TestClient(create_app(str(project_root))).get(
        "/ops/brain/genesis-foundation",
        params={"session_id": session_id},
    ).json()
    layer4 = restarted["layer4_neural_substrate_ledger_spine"]
    assert layer4["status"] == "degraded"
    assert layer4["source_hive_run_id"] == native_hive["hive_run_id"]
    assert layer4["source_brain_generate_status"] == "runtime-unavailable"
    assert layer4["covered_ledger_count"] == layer4["required_ledger_count"]

    serialized = json.dumps({"detail": detail, "layer4": layer4}, sort_keys=True)
    assert session_id not in serialized
    assert "SECRET-NO-ADAPTER" not in serialized
    assert str(project_root) not in serialized


def test_genesis_foundation_receipts_project_into_nexusbrain_owned_context_graph(tmp_path: Path):
    project_root = make_project(tmp_path)
    session_id = "genesis-nexusgraph-private-session-SECRET"
    prompt = "Private Genesis NexusGraph SECRET-NEXUSGRAPH should not enter graph receipts."
    client = TestClient(create_app(str(project_root)))
    services = client.app.state.services

    result = services.brain.generate(
        session_context=SessionContext(
            session_id=session_id,
            expert="researcher",
            task_type="genesis-nexusgraph-foundation",
            use_retrieval=False,
            metadata={"graph_plane_tags": ["canon", "authority", "graph", "runtime"]},
        ),
        prompt=prompt,
        model_hint="mock/default",
    )
    native_hive = result.inference_trace.metrics["native_hive_forward_pass"]

    foundation = client.get("/ops/brain/genesis-foundation", params={"session_id": session_id}).json()
    assert foundation["layer4_neural_substrate_ledger_spine"]["source_hive_run_id"] == native_hive["hive_run_id"]

    context_graph = client.get("/ops/brain/context-graph").json()
    projection = context_graph["nexusgraph_foundation_projection"]
    assert projection["schema_version"] == "nexusnet-context-graph-genesis-foundation-projections-v1"
    assert projection["surface_id"] == "context-graph-genesis-foundation-projections"
    assert projection["status"] == "live-control-plane"
    assert projection["projection_count"] >= 1
    latest = projection["latest_projection"]
    assert latest["schema_version"] == "nexusnet-context-graph-genesis-foundation-projection-v1"
    assert latest["source"] == "genesis-foundation"
    assert latest["mother_brain_authority"] == "NexusBrain"
    assert latest["nexusgraph_ownership"] == "NexusBrain"
    assert latest["gitnexus_provider_role"] == "external-codegraph-provider-not-final-brain"
    assert latest["foundation_artifact_ref"] == foundation["replay"]["latest_artifact_ref"]
    assert latest["authority_receipt_id"] == foundation["authority_receipt"]["receipt_id"]
    assert latest["permission_isolation_receipt_id"] == foundation["permission_isolation_receipt"]["receipt_id"]
    assert latest["neural_bus_event_ref"] == foundation["neural_bus_hive_blackboard_projection"]["typed_event_envelope"]["event_ref"]
    assert (
        latest["hive_blackboard_snapshot_ref"]
        == foundation["neural_bus_hive_blackboard_projection"]["hive_blackboard_snapshot"]["snapshot_ref"]
    )
    assert latest["plane_trace_ref"] == foundation["neural_bus_hive_blackboard_projection"]["plane_trace"]["trace_ref"]
    assert latest["layer4_substrate_ref"] == foundation["layer4_neural_substrate_ledger_spine"]["source_hive_run_ref"]
    assert latest["runtime_status"] == "graph-evidence-captured"
    assert latest["raw_content_included"] is False
    assert latest["active_production_mutation_allowed"] is False
    assert latest["contains_personal_data"] is False

    restarted_client = TestClient(create_app(str(project_root)))
    restarted_graph = restarted_client.get("/ops/brain/context-graph").json()
    restarted_projection = restarted_graph["nexusgraph_foundation_projection"]
    assert restarted_projection["latest_projection"]["projection_id"] == latest["projection_id"]
    assert restarted_projection["latest_projection"]["foundation_artifact_ref"] == foundation["replay"]["latest_artifact_ref"]

    control_panel = restarted_client.get(
        "/ops/brain/visualizer/state",
        params={"session_id": session_id},
    ).json()["overlay_state"]["control_panel"]
    control_projection = control_panel["context_graph_status"]["nexusgraph_foundation_projection"]
    assert control_projection["latest_projection"]["projection_id"] == latest["projection_id"]
    assert control_panel["live_refs"]["context_graph_status"] == "/ops/brain/context-graph"

    serialized = json.dumps(
        {
            "foundation": foundation,
            "context_graph": restarted_graph,
            "control_projection": control_projection,
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-NEXUSGRAPH" not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized
    assert "F:\\" not in serialized


def test_context_graph_records_sandbox_governed_impact_receipt_from_genesis_projection(tmp_path: Path):
    project_root = make_project(tmp_path)
    session_id = "genesis-graph-impact-private-session-SECRET"
    private_marker = "SECRET-GRAPH-IMPACT"
    prompt = f"Private Genesis graph impact {private_marker} should not enter receipts."
    client = TestClient(create_app(str(project_root)))
    services = client.app.state.services

    result = services.brain.generate(
        session_context=SessionContext(
            session_id=session_id,
            expert="researcher",
            task_type="genesis-graph-impact-receipt",
            use_retrieval=False,
            metadata={"graph_plane_tags": ["graph", "authority", "sandbox", "rollback"]},
        ),
        prompt=prompt,
        model_hint="mock/default",
    )
    native_hive = result.inference_trace.metrics["native_hive_forward_pass"]
    foundation = client.get("/ops/brain/genesis-foundation", params={"session_id": session_id}).json()
    assert foundation["layer4_neural_substrate_ledger_spine"]["source_hive_run_id"] == native_hive["hive_run_id"]

    context_graph = client.get("/ops/brain/context-graph").json()
    source_projection = context_graph["nexusgraph_foundation_projection"]["latest_projection"]
    local_target = project_root / "nexusnet" / "context_graph" / "service.py"

    impact_response = client.post(
        "/ops/brain/context-graph/impact-receipts",
        json={
            "session_id": session_id,
            "source_projection_id": source_projection["projection_id"],
            "proposed_change": {
                "change_summary": f"Private mutation proposal {private_marker} must be sanitized.",
                "effect_type": "filesystem_write",
                "target_refs": ["nexusnet/context_graph/service.py", str(local_target)],
                "changed_file_refs": [str(local_target)],
                "rollback_plan": f"Rollback private graph proposal {private_marker}.",
                "sandbox_command": "python -m pytest tests/test_genesis_foundation.py -q",
            },
            "gitnexus_evidence": {
                "provider": "GitNexus",
                "target_symbol": "ContextGraphService",
                "impact_risk": "LOW",
                "direct_callers": 1,
                "affected_processes": [],
                "indexed_repo": "NexusNet",
            },
        },
    )
    assert impact_response.status_code == 200
    receipt = impact_response.json()["receipt"]

    assert receipt["schema_version"] == "nexusnet-context-graph-impact-receipt-v1"
    assert receipt["surface_id"] == "context-graph-impact-receipt"
    assert receipt["status"] == "blocked-review-required"
    assert receipt["source_projection_id"] == source_projection["projection_id"]
    assert receipt["mother_brain_authority"] == "NexusBrain"
    assert receipt["nexusgraph_ownership"] == "NexusBrain"
    assert receipt["gitnexus_provider_evidence"]["provider_role"] == "external-codegraph-provider-not-final-brain"
    assert receipt["gitnexus_provider_evidence"]["impact_risk"] == "LOW"
    assert receipt["gitnexus_provider_evidence"]["provider_status"] == "provided"
    assert receipt["authority_gate"]["decision"] == "review-required"
    assert receipt["authority_gate"]["admin_approval_required"] is True
    assert receipt["authority_gate"]["production_action_allowed"] is False
    assert receipt["sandbox_governance"]["closed_sandbox_required"] is True
    assert receipt["sandbox_governance"]["sandbox_eval_status"] == "not-run"
    assert receipt["rollback_governance"]["rollback_required"] is True
    assert receipt["graph_impact"]["source_projection_id"] == source_projection["projection_id"]
    assert source_projection["foundation_artifact_ref"] in receipt["graph_impact"]["affected_graph_refs"]
    assert "sandbox_eval_required" in receipt["blockers"]
    assert "admin_approval_required" in receipt["blockers"]
    assert receipt["execution_allowed"] is False
    assert receipt["mutation_allowed"] is False
    assert receipt["active_production_mutation_allowed"] is False
    assert receipt["raw_content_included"] is False
    assert receipt["contains_personal_data"] is False

    restarted_client = TestClient(create_app(str(project_root)))
    restarted_graph = restarted_client.get("/ops/brain/context-graph").json()
    impact_summary = restarted_graph["nexusgraph_impact_receipts"]
    assert impact_summary["schema_version"] == "nexusnet-context-graph-impact-receipts-v1"
    assert impact_summary["status"] == "live-control-plane"
    assert impact_summary["receipt_count"] >= 1
    assert impact_summary["latest_receipt"]["receipt_id"] == receipt["receipt_id"]
    assert impact_summary["latest_receipt"]["source_projection_id"] == source_projection["projection_id"]

    control_panel = restarted_client.get(
        "/ops/brain/visualizer/state",
        params={"session_id": session_id},
    ).json()["overlay_state"]["control_panel"]
    control_receipts = control_panel["context_graph_status"]["nexusgraph_impact_receipts"]
    assert control_receipts["latest_receipt"]["receipt_id"] == receipt["receipt_id"]
    assert control_panel["live_refs"]["context_graph_status"] == "/ops/brain/context-graph"

    serialized = json.dumps(
        {
            "receipt": receipt,
            "impact_summary": impact_summary,
            "control_receipts": control_receipts,
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert private_marker not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized
    assert "F:\\" not in serialized


def test_context_graph_impact_receipt_runs_closed_sandbox_eval_before_apply(tmp_path: Path):
    project_root = make_project(tmp_path)
    sandbox_test_path = project_root / "tests" / "test_context_graph_receipt_sandbox.py"
    sandbox_test_path.parent.mkdir(parents=True, exist_ok=True)
    sandbox_test_path.write_text(
        "def test_context_graph_receipt_sandbox_gate():\n    assert True\n",
        encoding="utf-8",
    )
    session_id = "genesis-graph-sandbox-private-session-SECRET"
    private_marker = "SECRET-GRAPH-SANDBOX"
    prompt = f"Private graph sandbox proposal {private_marker} must stay out of receipts."
    client = TestClient(create_app(str(project_root)))
    services = client.app.state.services

    services.brain.generate(
        session_context=SessionContext(
            session_id=session_id,
            expert="researcher",
            task_type="genesis-graph-sandbox-receipt",
            use_retrieval=False,
            metadata={"graph_plane_tags": ["graph", "sandbox", "admin", "rollback"]},
        ),
        prompt=prompt,
        model_hint="mock/default",
    )
    client.get("/ops/brain/genesis-foundation", params={"session_id": session_id})
    source_projection = client.get("/ops/brain/context-graph").json()["nexusgraph_foundation_projection"][
        "latest_projection"
    ]

    impact_response = client.post(
        "/ops/brain/context-graph/impact-receipts",
        json={
            "session_id": session_id,
            "source_projection_id": source_projection["projection_id"],
            "proposed_change": {
                "change_summary": f"Run sandbox before private graph apply {private_marker}.",
                "effect_type": "filesystem_write",
                "target_refs": ["nexusnet/context_graph/service.py"],
                "changed_file_refs": ["nexusnet/context_graph/service.py"],
                "rollback_plan": f"Rollback private sandbox proposal {private_marker}.",
                "sandbox_command": "python -m pytest tests/test_context_graph_receipt_sandbox.py -q",
            },
            "gitnexus_evidence": {
                "provider": "GitNexus",
                "target_symbol": "ContextGraphService",
                "impact_risk": "LOW",
                "direct_callers": 1,
                "affected_processes": [],
                "indexed_repo": "NexusNet",
            },
        },
    )
    assert impact_response.status_code == 200
    receipt = impact_response.json()["receipt"]

    blocked_apply = client.post(
        f"/ops/brain/context-graph/impact-receipts/{receipt['receipt_id']}/apply",
        json={"session_id": session_id},
    )
    assert blocked_apply.status_code == 400
    assert "sandbox eval" in blocked_apply.json()["detail"].lower()

    sandbox_eval_response = client.post(
        f"/ops/brain/context-graph/impact-receipts/{receipt['receipt_id']}/sandbox-eval",
        json={
            "session_id": session_id,
            "command": "python -m pytest tests/test_context_graph_receipt_sandbox.py -q",
            "timeout_seconds": 60,
        },
    )
    assert sandbox_eval_response.status_code == 200
    sandbox_eval = sandbox_eval_response.json()["sandbox_eval"]
    assert sandbox_eval["schema_version"] == "nexusnet-context-graph-impact-sandbox-eval-v1"
    assert sandbox_eval["status"] == "passed"
    assert sandbox_eval["passed"] is True
    assert sandbox_eval["receipt_id"] == receipt["receipt_id"]
    assert sandbox_eval["sandbox"]["mode"] == "isolated-filesystem-copy-allowlisted-pytest"
    assert sandbox_eval["sandbox"]["shell_used"] is False
    assert sandbox_eval["sandbox"]["active_project_source_mutated"] is False
    assert sandbox_eval["sandbox"]["active_production_mutated"] is False
    assert sandbox_eval["allowlist"]["runner"] == "pytest"
    assert sandbox_eval["raw_content_included"] is False
    assert sandbox_eval["contains_personal_data"] is False

    blocked_after_eval = client.post(
        f"/ops/brain/context-graph/impact-receipts/{receipt['receipt_id']}/apply",
        json={"session_id": session_id},
    )
    assert blocked_after_eval.status_code == 400
    assert "admin approval" in blocked_after_eval.json()["detail"].lower()

    restarted_client = TestClient(create_app(str(project_root)))
    restarted_graph = restarted_client.get("/ops/brain/context-graph").json()
    impact_summary = restarted_graph["nexusgraph_impact_receipts"]
    latest_receipt = impact_summary["latest_receipt"]
    assert impact_summary["latest_sandbox_eval_run"]["eval_run_id"] == sandbox_eval["eval_run_id"]
    assert latest_receipt["latest_sandbox_eval_run"]["eval_run_id"] == sandbox_eval["eval_run_id"]
    assert latest_receipt["sandbox_governance"]["sandbox_eval_status"] == "passed"
    assert "sandbox_eval_required" not in latest_receipt["blockers"]
    assert "admin_approval_required" in latest_receipt["blockers"]

    control_panel = restarted_client.get(
        "/ops/brain/visualizer/state",
        params={"session_id": session_id},
    ).json()["overlay_state"]["control_panel"]
    control_receipts = control_panel["context_graph_status"]["nexusgraph_impact_receipts"]
    assert control_receipts["latest_sandbox_eval_run"]["eval_run_id"] == sandbox_eval["eval_run_id"]

    serialized = json.dumps(
        {
            "sandbox_eval": sandbox_eval,
            "impact_summary": impact_summary,
            "control_receipts": control_receipts,
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert private_marker not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized
    assert "F:\\" not in serialized


def test_context_graph_impact_receipt_admin_apply_rollback_emit_federated_packets(tmp_path: Path):
    project_root = make_project(tmp_path)
    sandbox_test_path = project_root / "tests" / "test_context_graph_receipt_lifecycle.py"
    sandbox_test_path.parent.mkdir(parents=True, exist_ok=True)
    sandbox_test_path.write_text(
        "def test_context_graph_receipt_lifecycle_gate():\n    assert True\n",
        encoding="utf-8",
    )
    session_id = "genesis-graph-apply-private-session-SECRET"
    private_marker = "SECRET-GRAPH-APPLY"
    admin_identity = "graph-admin-secret@example.invalid"
    prompt = f"Private graph lifecycle proposal {private_marker} must stay out of receipts."
    client = TestClient(create_app(str(project_root)))
    services = client.app.state.services

    services.brain.generate(
        session_context=SessionContext(
            session_id=session_id,
            expert="researcher",
            task_type="genesis-graph-apply-receipt",
            use_retrieval=False,
            metadata={"graph_plane_tags": ["graph", "sandbox", "admin", "rollback", "federation"]},
        ),
        prompt=prompt,
        model_hint="mock/default",
    )
    client.get("/ops/brain/genesis-foundation", params={"session_id": session_id})
    source_projection = client.get("/ops/brain/context-graph").json()["nexusgraph_foundation_projection"][
        "latest_projection"
    ]
    receipt = client.post(
        "/ops/brain/context-graph/impact-receipts",
        json={
            "session_id": session_id,
            "source_projection_id": source_projection["projection_id"],
            "proposed_change": {
                "change_summary": f"Admin approved graph shadow apply {private_marker}.",
                "effect_type": "filesystem_write",
                "target_refs": ["nexusnet/context_graph/service.py"],
                "changed_file_refs": ["nexusnet/context_graph/service.py"],
                "rollback_plan": f"Rollback graph shadow apply {private_marker}.",
                "sandbox_command": "python -m pytest tests/test_context_graph_receipt_lifecycle.py -q",
            },
            "gitnexus_evidence": {
                "provider": "GitNexus",
                "target_symbol": "ContextGraphService",
                "impact_risk": "LOW",
                "direct_callers": 1,
                "affected_processes": [],
                "indexed_repo": "NexusNet",
            },
        },
    ).json()["receipt"]

    sandbox_eval = client.post(
        f"/ops/brain/context-graph/impact-receipts/{receipt['receipt_id']}/sandbox-eval",
        json={
            "session_id": session_id,
            "command": "python -m pytest tests/test_context_graph_receipt_lifecycle.py -q",
            "timeout_seconds": 60,
        },
    ).json()["sandbox_eval"]
    assert sandbox_eval["passed"] is True
    sandbox_packet = sandbox_eval["federated_outcome_packet"]
    assert sandbox_packet["outcome_type"] == "context_graph_impact_sandbox_eval_passed"
    assert sandbox_packet["per_user_global_learning_state"]["global_federated_packet_captured"] is True

    approved = client.post(
        f"/ops/brain/context-graph/impact-receipts/{receipt['receipt_id']}/approve",
        json={"session_id": session_id, "approved_by": admin_identity, "approval_ref": "admin::context-graph-apply"},
    ).json()["approval"]
    assert approved["status"] == "admin-approved"
    assert approved["operator_approved"] is True
    assert approved["approver_digest"].startswith("sha256:")
    assert admin_identity not in json.dumps(approved, sort_keys=True)

    applied = client.post(
        f"/ops/brain/context-graph/impact-receipts/{receipt['receipt_id']}/apply",
        json={"session_id": session_id},
    ).json()["application"]
    assert applied["status"] == "applied-shadow-safe-file"
    assert applied["active_production_mutated"] is False
    assert applied["safe_file_ref"].startswith("context-graphs/safe-files/")
    assert applied["sandbox_eval_run_id"] == sandbox_eval["eval_run_id"]
    apply_packet = applied["federated_outcome_packet"]
    assert apply_packet["outcome_type"] == "context_graph_impact_applied"
    assert apply_packet["sandbox_eval_run_id"] == sandbox_eval["eval_run_id"]
    assert apply_packet["per_user_global_learning_state"]["runtime_growth_captured"] is True
    safe_file = services.paths.artifacts_dir / applied["safe_file_ref"]
    assert safe_file.exists()
    safe_payload = json.loads(safe_file.read_text(encoding="utf-8"))
    assert safe_payload["receipt_id"] == receipt["receipt_id"]
    assert safe_payload["active_production_mutated"] is False
    assert safe_payload["raw_content_included"] is False

    rollback = client.post(
        f"/ops/brain/context-graph/impact-receipts/{receipt['receipt_id']}/rollback",
        json={"session_id": session_id, "reason": f"Rollback private graph apply {private_marker}"},
    ).json()["rollback"]
    assert rollback["status"] == "rolled-back"
    assert rollback["rollback_restored"] is True
    assert rollback["active_production_mutated"] is False
    assert not safe_file.exists()
    rollback_packet = rollback["federated_outcome_packet"]
    assert rollback_packet["outcome_type"] == "context_graph_impact_rolled_back"
    assert rollback_packet["rollback_id"] == rollback["rollback_id"]

    restarted_client = TestClient(create_app(str(project_root)))
    context_graph = restarted_client.get("/ops/brain/context-graph").json()
    impact_summary = context_graph["nexusgraph_impact_receipts"]
    latest_receipt = impact_summary["latest_receipt"]
    assert latest_receipt["receipt_id"] == receipt["receipt_id"]
    assert latest_receipt["latest_approval"]["approval_ref"] == approved["approval_ref"]
    assert latest_receipt["latest_application"]["apply_id"] == applied["apply_id"]
    assert latest_receipt["latest_rollback"]["rollback_id"] == rollback["rollback_id"]
    assert impact_summary["latest_application"]["apply_id"] == applied["apply_id"]
    assert impact_summary["latest_rollback"]["rollback_id"] == rollback["rollback_id"]

    federated = restarted_client.get(
        "/ops/brain/genesis-federated-outcomes",
        params={"session_id": session_id},
    ).json()
    assert federated["status"] == "live-control-plane"
    assert federated["packet_count"] >= 3
    assert federated["latest_packet"]["outcome_type"] == "context_graph_impact_rolled_back"
    assert federated["per_user_global_learning_state"]["global_federated_packet_captured"] is True

    control_panel = restarted_client.get(
        "/ops/brain/visualizer/state",
        params={"session_id": session_id},
    ).json()["overlay_state"]["control_panel"]
    control_receipts = control_panel["context_graph_status"]["nexusgraph_impact_receipts"]
    assert control_receipts["latest_rollback"]["rollback_id"] == rollback["rollback_id"]
    assert control_panel["genesis_federated_outcome_status"]["latest_packet"]["outcome_type"] == (
        "context_graph_impact_rolled_back"
    )

    serialized = json.dumps(
        {
            "sandbox_eval": sandbox_eval,
            "approved": approved,
            "applied": applied,
            "rollback": rollback,
            "context_graph": context_graph,
            "federated": federated,
            "control_receipts": control_receipts,
            "control_federated": control_panel["genesis_federated_outcome_status"],
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert private_marker not in serialized
    assert session_id not in serialized
    assert admin_identity not in serialized
    assert str(project_root) not in serialized
    assert "F:\\" not in serialized


def test_genesis_heartbeat_chain_appends_two_real_brain_interactions_and_replays_safely(tmp_path: Path):
    project_root = make_project(tmp_path)
    session_id = "genesis-heartbeat-private-session-SECRET"
    prompt_one = "Private Genesis heartbeat SECRET-HEARTBEAT-ONE should not be stored."
    prompt_two = "Private Genesis heartbeat SECRET-HEARTBEAT-TWO should not be stored."
    client = TestClient(create_app(str(project_root)))
    services = client.app.state.services

    first = services.brain.generate(
        session_context=SessionContext(
            session_id=session_id,
            expert="researcher",
            task_type="genesis-heartbeat",
            use_retrieval=False,
            metadata={"graph_plane_tags": ["runtime", "growth", "federated_learning"]},
        ),
        prompt=prompt_one,
        model_hint="mock/default",
    )
    second = services.brain.generate(
        session_context=SessionContext(
            session_id=session_id,
            expert="researcher",
            task_type="genesis-heartbeat",
            use_retrieval=False,
            metadata={"graph_plane_tags": ["runtime", "growth", "federated_learning"]},
        ),
        prompt=prompt_two,
        model_hint="mock/default",
    )
    first_hive = first.inference_trace.metrics["native_hive_forward_pass"]
    second_hive = second.inference_trace.metrics["native_hive_forward_pass"]

    assert first_hive["status"] == "completed"
    assert second_hive["status"] == "completed"
    assert first_hive["genesis_heartbeat_record_id"]
    assert second_hive["genesis_heartbeat_record_id"]
    assert first_hive["genesis_heartbeat_record_id"] != second_hive["genesis_heartbeat_record_id"]

    restarted_client = TestClient(create_app(str(project_root)))
    response = restarted_client.get("/ops/brain/genesis-heartbeat", params={"session_id": session_id})
    assert response.status_code == 200
    chain = response.json()

    assert chain["schema_version"] == "nexusnet-genesis-heartbeat-chain-v1"
    assert chain["surface_id"] == "genesis-heartbeat-chain"
    assert chain["status"] == "alive"
    assert chain["source"] == "nexusbrain-generate"
    assert chain["heartbeat_count"] == 2
    assert chain["global_heartbeat_count"] >= 2
    assert chain["latest_record_id"] == second_hive["genesis_heartbeat_record_id"]
    assert chain["latest_source_hive_run_id"] == second_hive["hive_run_id"]
    assert chain["latest_runtime_growth_receipt_id"] == second_hive["runtime_growth_receipt_id"]
    assert chain["latest_federated_packet_id"] == second_hive["federated_packet_id"]
    assert chain["raw_content_included"] is False
    assert chain["active_production_mutation_allowed"] is False
    assert chain["active_production_mutated"] is False

    records = chain["records"]
    assert [record["record_id"] for record in records] == [
        second_hive["genesis_heartbeat_record_id"],
        first_hive["genesis_heartbeat_record_id"],
    ]
    for record, hive in zip(records, [second_hive, first_hive]):
        assert record["schema_version"] == "nexusnet-genesis-heartbeat-record-v1"
        assert record["surface_id"] == "genesis-heartbeat-record"
        assert record["status"] == "alive"
        assert record["source"] == "nexusbrain-generate"
        assert record["source_hive_run_id"] == hive["hive_run_id"]
        assert record["project_heartbeat_id"] == hive["project_heartbeat_id"]
        assert record["runtime_growth_receipt_id"] == hive["runtime_growth_receipt_id"]
        assert record["federated_packet_id"] == hive["federated_packet_id"]
        assert record["per_user_global_learning_state"]["session_ref_digest"]
        assert record["per_user_global_learning_state"]["runtime_growth_captured"] is True
        assert record["per_user_global_learning_state"]["global_federated_packet_captured"] is True
        assert record["admin_update_governance"]["admin_approval_required"] is True
        assert record["admin_update_governance"]["safe_apply_allowed"] is False
        assert record["admin_update_governance"]["rollback_required"] is True
        assert record["raw_content_included"] is False
        assert record["active_production_mutation_allowed"] is False
        assert record["active_production_mutated"] is False

    control_panel = restarted_client.get(
        "/ops/brain/visualizer/state",
        params={"session_id": session_id},
    ).json()["overlay_state"]["control_panel"]
    assert control_panel["genesis_heartbeat_status"]["latest_record_id"] == second_hive["genesis_heartbeat_record_id"]
    assert control_panel["genesis_heartbeat_status"]["heartbeat_count"] == 2
    assert control_panel["live_refs"]["genesis_heartbeat_status"] == "/ops/brain/genesis-heartbeat"

    serialized = json.dumps(
        {
            "chain": chain,
            "control_heartbeat": control_panel["genesis_heartbeat_status"],
            "live_ref": control_panel["live_refs"]["genesis_heartbeat_status"],
        },
        sort_keys=True,
    )
    assert prompt_one not in serialized
    assert prompt_two not in serialized
    assert "SECRET-HEARTBEAT" not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized
    assert "F:\\" not in serialized


def test_genesis_heartbeat_publishes_real_brain_use_to_replayable_event_spine(tmp_path: Path):
    project_root = make_project(tmp_path)
    session_id = "genesis-event-spine-private-session-SECRET"
    prompt_one = "Private Genesis event spine SECRET-EVENT-SPINE-ONE should not be stored."
    prompt_two = "Private Genesis event spine SECRET-EVENT-SPINE-TWO should not be stored."
    client = TestClient(create_app(str(project_root)))
    services = client.app.state.services

    first = services.brain.generate(
        session_context=SessionContext(
            session_id=session_id,
            expert="researcher",
            task_type="genesis-event-spine",
            use_retrieval=False,
            metadata={"graph_plane_tags": ["runtime", "growth", "federated_learning"]},
        ),
        prompt=prompt_one,
        model_hint="mock/default",
    )
    second = services.brain.generate(
        session_context=SessionContext(
            session_id=session_id,
            expert="researcher",
            task_type="genesis-event-spine",
            use_retrieval=False,
            metadata={"graph_plane_tags": ["runtime", "growth", "federated_learning"]},
        ),
        prompt=prompt_two,
        model_hint="mock/default",
    )
    first_hive = first.inference_trace.metrics["native_hive_forward_pass"]
    second_hive = second.inference_trace.metrics["native_hive_forward_pass"]

    restarted_client = TestClient(create_app(str(project_root)))
    chain = restarted_client.get("/ops/brain/genesis-heartbeat", params={"session_id": session_id}).json()

    event_ledger = chain["neural_bus_event_ledger"]
    assert event_ledger["schema_version"] == "nexusnet-genesis-heartbeat-neural-bus-ledger-v1"
    assert event_ledger["surface_id"] == "genesis-heartbeat-neural-bus-event-ledger"
    assert event_ledger["mode"] == "append-only-file-backed"
    assert event_ledger["event_count"] == 2
    assert event_ledger["global_event_count"] >= 2
    assert event_ledger["latest_event_ref"].startswith("neural-bus-event::")
    assert event_ledger["latest_heartbeat_record_id"] == second_hive["genesis_heartbeat_record_id"]
    assert event_ledger["raw_content_included"] is False
    assert event_ledger["active_production_mutation_allowed"] is False

    blackboard = chain["hive_blackboard_projection"]
    assert blackboard["schema_version"] == "nexusnet-genesis-heartbeat-hive-blackboard-ledger-v1"
    assert blackboard["surface_id"] == "genesis-heartbeat-hive-blackboard-ledger"
    assert blackboard["latest_snapshot_ref"].startswith("hive-blackboard::")
    assert blackboard["latest_heartbeat_record_id"] == second_hive["genesis_heartbeat_record_id"]
    assert blackboard["snapshot_count"] == 2
    assert blackboard["raw_content_included"] is False

    plane_trace = chain["plane_trace_projection"]
    assert plane_trace["schema_version"] == "nexusnet-genesis-heartbeat-plane-trace-ledger-v1"
    assert plane_trace["surface_id"] == "genesis-heartbeat-plane-trace-ledger"
    assert plane_trace["latest_trace_ref"].startswith("plane-trace::")
    assert plane_trace["trace_count"] == 2
    assert "runtime" in plane_trace["latest_planes"]
    assert "federation" in plane_trace["latest_planes"]
    assert plane_trace["raw_content_included"] is False

    control_panel = restarted_client.get(
        "/ops/brain/visualizer/state",
        params={"session_id": session_id},
    ).json()["overlay_state"]["control_panel"]
    control_heartbeat = control_panel["genesis_heartbeat_status"]
    assert control_heartbeat["neural_bus_event_ledger"]["latest_event_ref"] == event_ledger["latest_event_ref"]
    assert control_heartbeat["hive_blackboard_projection"]["latest_snapshot_ref"] == blackboard["latest_snapshot_ref"]
    assert control_heartbeat["plane_trace_projection"]["latest_trace_ref"] == plane_trace["latest_trace_ref"]
    assert control_panel["live_refs"]["genesis_heartbeat_status"] == "/ops/brain/genesis-heartbeat"

    records = chain["records"]
    assert [record["record_id"] for record in records] == [
        second_hive["genesis_heartbeat_record_id"],
        first_hive["genesis_heartbeat_record_id"],
    ]
    for record, hive in zip(records, [second_hive, first_hive]):
        projection = record["neural_bus_projection"]
        envelope = projection["typed_event_envelope"]
        assert envelope["schema_version"] == "nexusnet-neural-bus-event-envelope-v1"
        assert envelope["event_type"] == "genesis.heartbeat.recorded"
        assert envelope["correlation_ref"] == record["record_id"]
        assert envelope["source_hive_run_ref"] == f"hive-forward::{hive['hive_run_id']}"
        assert envelope["artifact_bound"] is True
        assert envelope["event_privacy_label"] == "sanitized-genesis-heartbeat"
        assert projection["hive_blackboard_snapshot"]["source_heartbeat_record_id"] == record["record_id"]
        assert projection["plane_trace"]["source_hive_run_ref"] == f"hive-forward::{hive['hive_run_id']}"
        assert projection["raw_content_included"] is False
        assert projection["active_production_mutation_allowed"] is False

    persisted_events = (
        services.paths.artifacts_dir / "genesis" / "heartbeat" / "neural_bus_events.jsonl"
    ).read_text(encoding="utf-8")
    serialized = json.dumps(
        {
            "chain": chain,
            "persisted_events": persisted_events,
        },
        sort_keys=True,
    )
    assert prompt_one not in serialized
    assert prompt_two not in serialized
    assert "SECRET-EVENT-SPINE" not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized
    assert "F:\\" not in serialized


def test_primary_chat_interaction_returns_nexusbrain_forward_pass_evidence(tmp_path: Path):
    project_root = make_project(tmp_path)
    session_id = "genesis-primary-chat-private-session-SECRET"
    prompt = "Private primary-chat activation SECRET-PRIMARY-CHAT must not enter evidence."
    client = TestClient(create_app(str(project_root)))

    chat = client.post(
        "/chat",
        json={
            "session_id": session_id,
            "message": prompt,
            "rag": False,
        },
    )

    assert chat.status_code == 200
    forward_pass = chat.json()["forward_pass_evidence"]
    assert forward_pass["status"] == "completed"
    assert forward_pass["nexusbrain_native_hive_forward_pass_id"]
    assert forward_pass["global_growth_receipt_id"]
    assert forward_pass["federated_packet_id"]
    assert forward_pass["genesis_heartbeat_record_id"]
    assert forward_pass["raw_content_included"] is False
    assert forward_pass["active_production_mutation_allowed"] is False
    assert forward_pass["active_production_mutated"] is False

    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    interaction = runtime["latest_interaction"]
    activation = interaction["nexusbrain_genesis_activation"]
    assert forward_pass["nexusbrain_native_hive_forward_pass_id"] == activation["hive_run_id"]
    assert forward_pass["global_growth_receipt_id"] == interaction["runtime_growth_receipt_id"]
    assert forward_pass["federated_packet_id"] == interaction["federated_packet_id"]
    assert forward_pass["genesis_heartbeat_record_id"] == activation["genesis_heartbeat_record_id"]


def test_openai_provider_interaction_runs_through_nexusbrain_genesis_spine_and_replays(tmp_path: Path):
    project_root = make_project(tmp_path)
    session_id = "genesis-provider-private-session-SECRET"
    prompt = "Private attached-provider activation SECRET-PROVIDER-GENESIS must not enter evidence."
    client = TestClient(create_app(str(project_root)))

    chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
        },
    )

    assert chat.status_code == 200
    forward_pass = chat.json()["nexusnet"]["forward_pass_evidence"]
    assert forward_pass["status"] == "completed"
    assert forward_pass["nexusbrain_native_hive_forward_pass_id"]
    assert forward_pass["global_growth_receipt_id"]
    assert forward_pass["federated_packet_id"]
    assert forward_pass["genesis_heartbeat_record_id"]
    assert forward_pass["raw_content_included"] is False
    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    interaction = runtime["latest_interaction"]
    activation = interaction["nexusbrain_genesis_activation"]
    assert activation["surface_id"] == "nexusbrain-native-hive-forward-pass"
    assert activation["activation_source"] == "wrapped-model-interaction"
    assert activation["status"] == "completed"
    assert activation["hive_run_id"] == interaction["hive_run_id"]
    assert activation["genesis_heartbeat_record_id"]
    assert activation["genesis_sensory_event_id"]
    assert activation["genesis_memory_admission_decision_id"]
    assert activation["federated_learning_packet_id"] == interaction["federated_packet_id"]
    assert forward_pass["nexusbrain_native_hive_forward_pass_id"] == activation["hive_run_id"]
    assert forward_pass["global_growth_receipt_id"] == interaction["runtime_growth_receipt_id"]
    assert forward_pass["federated_packet_id"] == interaction["federated_packet_id"]
    assert forward_pass["genesis_heartbeat_record_id"] == activation["genesis_heartbeat_record_id"]
    assert activation["runtime_growth_federated_packet_id"].startswith("hive-runtime-growth::")
    assert activation["raw_content_included"] is False
    assert activation["contains_personal_data"] is False
    assert activation["active_production_mutated"] is False

    restarted = TestClient(create_app(str(project_root)))
    heartbeat = restarted.get("/ops/brain/genesis-heartbeat", params={"session_id": session_id}).json()
    event_spine = restarted.get("/ops/brain/genesis-event-spine", params={"session_id": session_id}).json()
    sensory = restarted.get("/ops/brain/genesis-sensory-provenance", params={"session_id": session_id}).json()
    admission = restarted.get("/ops/brain/genesis-memory-admission", params={"session_id": session_id}).json()
    outbox = restarted.get("/ops/wrapper/federated-packets", params={"session_id": session_id}).json()
    context_graph = restarted.get("/ops/brain/context-graph").json()
    control_panel = restarted.get(
        "/ops/brain/visualizer/state",
        params={"session_id": session_id},
    ).json()["overlay_state"]["control_panel"]

    assert heartbeat["latest_record_id"] == activation["genesis_heartbeat_record_id"]
    assert sensory["latest_event_id"] == activation["genesis_sensory_event_id"]
    assert admission["latest_decision_id"] == activation["genesis_memory_admission_decision_id"]
    assert {
        "genesis.heartbeat.recorded",
        "genesis.sensory.provenance",
        "genesis.memory.admission.decision",
    } <= {event["event_type"] for event in event_spine["events"]}
    assert event_spine["blackboard_snapshot_count"] == event_spine["event_count"]
    assert event_spine["plane_trace_count"] == event_spine["event_count"]
    assert outbox["packet_count"] == 1
    assert outbox["latest_packet"]["packet_id"] == activation["federated_learning_packet_id"]
    assert outbox["latest_packet"]["raw_content_included"] is False
    assert outbox["latest_packet"]["contains_personal_data"] is False
    latest_projection = context_graph["nexusgraph_foundation_projection"]["latest_projection"]
    assert latest_projection["projection_id"] == activation["genesis_context_graph_projection_id"]
    assert latest_projection["layer4_substrate_ref"] == f"hive-forward::{activation['hive_run_id']}"
    assert control_panel["genesis_heartbeat_status"]["latest_record_id"] == activation["genesis_heartbeat_record_id"]
    assert control_panel["genesis_event_spine_status"]["latest_event_ref"] == event_spine["latest_event_ref"]
    assert control_panel["genesis_memory_admission_status"]["latest_decision_id"] == activation[
        "genesis_memory_admission_decision_id"
    ]

    serialized = json.dumps(
        {
            "activation": activation,
            "heartbeat": heartbeat,
            "event_spine": event_spine,
            "sensory": sensory,
            "admission": admission,
            "outbox": outbox,
            "context_graph": latest_projection,
            "control_panel": {
                "heartbeat": control_panel["genesis_heartbeat_status"],
                "event_spine": control_panel["genesis_event_spine_status"],
                "memory": control_panel["genesis_memory_admission_status"],
            },
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-PROVIDER-GENESIS" not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized
    assert "F:\\" not in serialized


def test_genesis_shared_event_spine_links_runtime_heartbeat_sensory_memory_evidence_and_eval(tmp_path: Path):
    project_root = make_project(tmp_path)
    session_id = "genesis-shared-spine-private-session-SECRET"
    prompt = "Private Genesis shared spine SECRET-SHARED-SPINE should not enter the event spine."
    client = TestClient(create_app(str(project_root)))
    services = client.app.state.services

    result = services.brain.generate(
        session_context=SessionContext(
            session_id=session_id,
            expert="researcher",
            task_type="genesis-shared-event-spine",
            use_retrieval=False,
            metadata={"graph_plane_tags": ["runtime", "sensory", "memory", "evidence", "eval"]},
        ),
        prompt=prompt,
        model_hint="mock/default",
    )
    native_hive = result.inference_trace.metrics["native_hive_forward_pass"]
    heartbeat_record_id = native_hive["genesis_heartbeat_record_id"]
    sensory_event_id = native_hive["genesis_sensory_event_id"]
    admission_decision_id = native_hive["genesis_memory_admission_decision_id"]

    evidence = client.get("/ops/brain/genesis-evidence-spine", params={"session_id": session_id}).json()
    gate = client.post(
        "/ops/brain/genesis-memory-replay/promotion-gate",
        json={
            "session_id": session_id,
            "eval_refs": ["eval::shared-spine-focused"],
            "sandbox_ref": "sandbox::shared-spine-closed",
            "artifact_trust_refs": [evidence["artifact_trust_registry"]["records"][0]["artifact_ref"]],
            "rollback_plan": evidence["checkpoint_snapshot"]["checkpoint_id"],
            "governance_approval_ref": "governance::shared-spine-review",
            "admin_approval_ref": "admin::shared-spine-review",
        },
    ).json()
    sandbox_eval = client.post(
        "/ops/brain/genesis-memory-replay/promotion-gate/sandbox-eval",
        json={
            "gate_id": gate["gate_id"],
            "artifact_trust_ref": evidence["artifact_trust_registry"]["records"][0]["artifact_ref"],
            "rollback_proof_ref": evidence["checkpoint_snapshot"]["checkpoint_id"],
            "eval_cases": [
                {
                    "case_id": "blocked-private-memory-remains-blocked",
                    "target": "memory_write",
                    "expected_allowed": False,
                }
            ],
        },
    ).json()

    restarted_client = TestClient(create_app(str(project_root)))
    event_spine = restarted_client.get("/ops/brain/genesis-event-spine", params={"session_id": session_id}).json()
    assert event_spine["schema_version"] == "nexusnet-genesis-event-spine-v1"
    assert event_spine["surface_id"] == "genesis-event-spine"
    assert event_spine["status"] == "live-control-plane"
    assert event_spine["event_count"] >= 6
    assert event_spine["blackboard_snapshot_count"] == event_spine["event_count"]
    assert event_spine["plane_trace_count"] == event_spine["event_count"]
    assert event_spine["latest_event_ref"].startswith("genesis-event::")
    assert event_spine["raw_content_included"] is False
    assert event_spine["active_production_mutation_allowed"] is False

    events = event_spine["events"]
    event_types = {event["event_type"] for event in events}
    assert {
        "genesis.heartbeat.recorded",
        "genesis.sensory.provenance",
        "genesis.memory.admission.decision",
        "genesis.evidence.checkpoint",
        "genesis.memory.promotion.gate",
        "genesis.memory.promotion.sandbox_eval",
    } <= event_types
    assert all(event["session_ref_digest"] == event_spine["session_ref_digest"] for event in events)
    assert all(event["artifact_bound"] is True for event in events)
    assert all(event["raw_content_included"] is False for event in events)
    assert any(event["correlation_ref"] == heartbeat_record_id for event in events)
    assert any(event["correlation_ref"] == sensory_event_id for event in events)
    assert any(event["correlation_ref"] == admission_decision_id for event in events)
    assert any(event["correlation_ref"] == gate["gate_id"] for event in events)
    assert any(event["correlation_ref"] == sandbox_eval["eval_run_id"] for event in events)

    heartbeat = restarted_client.get("/ops/brain/genesis-heartbeat", params={"session_id": session_id}).json()
    sensory = restarted_client.get("/ops/brain/genesis-sensory-provenance", params={"session_id": session_id}).json()
    admission = restarted_client.get("/ops/brain/genesis-memory-admission", params={"session_id": session_id}).json()
    replayed_evidence = restarted_client.get("/ops/brain/genesis-evidence-spine", params={"session_id": session_id}).json()
    replayed_gate = restarted_client.get(
        "/ops/brain/genesis-memory-replay/promotion-gate",
        params={"session_id": session_id},
    ).json()

    event_refs = {event["event_ref"] for event in events}
    assert heartbeat["shared_event_spine"]["latest_event_ref"] in event_refs
    assert sensory["events"][0]["shared_event_spine"]["event_ref"] in event_refs
    assert admission["latest_decision"]["shared_event_spine"]["event_ref"] in event_refs
    assert replayed_evidence["shared_event_spine"]["latest_event_ref"] in event_refs
    assert replayed_gate["shared_event_spine"]["event_ref"] in event_refs
    assert replayed_gate["latest_sandbox_eval_run"]["shared_event_spine"]["event_ref"] in event_refs

    control_panel = restarted_client.get(
        "/ops/brain/visualizer/state",
        params={"session_id": session_id},
    ).json()["overlay_state"]["control_panel"]
    assert control_panel["genesis_event_spine_status"]["latest_event_ref"] == event_spine["latest_event_ref"]
    assert control_panel["live_refs"]["genesis_event_spine_status"] == "/ops/brain/genesis-event-spine"

    serialized = json.dumps(
        {
            "event_spine": event_spine,
            "control": control_panel["genesis_event_spine_status"],
            "heartbeat": heartbeat,
            "sensory": sensory,
            "admission": admission,
            "evidence": replayed_evidence,
            "gate": replayed_gate,
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-SHARED-SPINE" not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized
    assert "F:\\" not in serialized


def test_genesis_evidence_spine_checkpoints_applies_and_rolls_back_safe_file_after_real_brain_use(tmp_path: Path):
    project_root = make_project(tmp_path)
    session_id = "genesis-evidence-private-session-SECRET"
    prompt = "Private Genesis evidence SECRET-LAYER5 should not enter evidence replay."
    client = TestClient(create_app(str(project_root)))
    services = client.app.state.services

    result = services.brain.generate(
        session_context=SessionContext(
            session_id=session_id,
            expert="researcher",
            task_type="genesis-evidence-spine",
            use_retrieval=False,
            metadata={"graph_plane_tags": ["runtime", "checkpoint", "rollback", "federated_learning"]},
        ),
        prompt=prompt,
        model_hint="mock/default",
    )
    native_hive = result.inference_trace.metrics["native_hive_forward_pass"]
    heartbeat_record_id = native_hive["genesis_heartbeat_record_id"]

    evidence = client.get("/ops/brain/genesis-evidence-spine", params={"session_id": session_id}).json()
    assert evidence["schema_version"] == "nexusnet-genesis-evidence-spine-v1"
    assert evidence["surface_id"] == "genesis-evidence-checkpoint-spine"
    assert evidence["status"] == "live-control-plane"
    assert evidence["latest_heartbeat_record_id"] == heartbeat_record_id
    assert evidence["checkpoint_snapshot"]["source_heartbeat_record_id"] == heartbeat_record_id
    assert evidence["checkpoint_snapshot"]["checkpoint_id"].startswith("genesis-checkpoint::")
    operation = evidence["operation_receipt"]
    assert operation["status"] == "recorded"
    assert operation["source_heartbeat_record_id"] == heartbeat_record_id
    assert operation["source_hive_run_id"] == native_hive["hive_run_id"]
    assert operation["checkpoint_id"] == evidence["checkpoint_snapshot"]["checkpoint_id"]
    assert operation["hive_activation_id"]
    assert operation["neural_pathway_id"]
    assert operation["synaptic_transmission_id"]
    assert operation["replay_status"] == "replayed"
    assert operation["rollback_aware"] is True
    assert evidence["artifact_trust_registry"]["trust_status"] == "trusted"
    assert evidence["artifact_trust_registry"]["trusted_ref_count"] >= 3
    assert any(ref.startswith("sha256:") for ref in evidence["content_addressed_evidence_refs"])
    assert evidence["raw_content_included"] is False
    assert evidence["active_production_mutation_allowed"] is False

    proposed = client.post(
        "/ops/brain/genesis-evidence-spine/proposals",
        json={
            "session_id": session_id,
            "target_ref": "genesis/safe-files/layer5-evidence-demo.json",
            "content": '{"layer": 5, "status": "shadow-safe-file"}',
            "reason": "record sanitized Layer 5 safe-file evidence",
        },
    ).json()
    assert proposed["status"] == "proposal"
    assert proposed["target_ref"] == "genesis/safe-files/layer5-evidence-demo.json"
    assert proposed["admin_approval_required"] is True
    assert proposed["safe_apply_allowed"] is False
    assert proposed["rollback_plan"]["rollback_available"] is True
    assert proposed["raw_content_included"] is False

    approved = client.post(
        f"/ops/brain/genesis-evidence-spine/proposals/{proposed['proposal_id']}/approve",
        json={"approved_by": "layer5-admin@example.invalid", "approval_ref": "admin-approval::layer5"},
    ).json()
    assert approved["status"] == "admin-approved"
    assert approved["operator_approved"] is True
    assert approved["approver_digest"].startswith("sha256:")
    assert "layer5-admin@example.invalid" not in json.dumps(approved, sort_keys=True)

    applied = client.post(
        f"/ops/brain/genesis-evidence-spine/proposals/{proposed['proposal_id']}/apply",
        json={
            "test_results": [
                {
                    "command": "python -m pytest tests/test_genesis_foundation.py -q",
                    "passed": True,
                    "failure_count": 0,
                    "evidence_ref": "pytest::genesis-evidence-spine-focused",
                }
            ]
        },
    ).json()
    assert applied["status"] == "applied-shadow-safe-file"
    assert applied["active_production_mutated"] is False
    assert applied["safe_file_ref"] == "genesis/safe-files/layer5-evidence-demo.json"
    assert applied["rollback_ref"].startswith("genesis-rollback::")
    safe_file_path = services.paths.artifacts_dir / "genesis" / "safe-files" / "layer5-evidence-demo.json"
    assert safe_file_path.read_text(encoding="utf-8") == '{"layer": 5, "status": "shadow-safe-file"}'

    rollback = client.post(
        f"/ops/brain/genesis-evidence-spine/proposals/{proposed['proposal_id']}/rollback",
        json={"reason": "focused regression rollback proof"},
    ).json()
    assert rollback["status"] == "rolled-back"
    assert rollback["rollback_restored"] is True
    assert rollback["active_production_mutated"] is False
    assert not safe_file_path.exists()

    restarted_client = TestClient(create_app(str(project_root)))
    replayed = restarted_client.get("/ops/brain/genesis-evidence-spine", params={"session_id": session_id}).json()
    assert replayed["latest_heartbeat_record_id"] == heartbeat_record_id
    assert replayed["operation_receipt"]["operation_receipt_id"] == operation["operation_receipt_id"]
    assert replayed["operation_receipt"]["replay_status"] == "replayed"
    assert replayed["safe_apply_governance"]["latest_proposal_id"] == proposed["proposal_id"]
    assert replayed["safe_apply_governance"]["latest_apply_status"] == "applied-shadow-safe-file"
    assert replayed["safe_apply_governance"]["latest_rollback_status"] == "rolled-back"

    control_panel = restarted_client.get(
        "/ops/brain/visualizer/state",
        params={"session_id": session_id},
    ).json()["overlay_state"]["control_panel"]
    assert control_panel["genesis_evidence_spine_status"]["latest_heartbeat_record_id"] == heartbeat_record_id
    assert (
        control_panel["genesis_evidence_spine_status"]["operation_receipt"]["operation_receipt_id"]
        == operation["operation_receipt_id"]
    )
    assert control_panel["genesis_evidence_spine_status"]["safe_apply_governance"]["latest_rollback_status"] == "rolled-back"
    assert control_panel["live_refs"]["genesis_evidence_spine_status"] == "/ops/brain/genesis-evidence-spine"

    serialized = json.dumps(
        {
            "evidence": replayed,
            "control": control_panel["genesis_evidence_spine_status"],
            "proposal": proposed,
            "approval": approved,
            "apply": applied,
            "rollback": rollback,
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-LAYER5" not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized
    assert "F:\\" not in serialized


def test_genesis_evidence_spine_binds_failed_brain_transaction_to_operation_receipt(
    tmp_path: Path,
    monkeypatch,
):
    monkeypatch.setenv("NEXUSNET_PRODUCT_MODE", "1")
    monkeypatch.delenv("NEXUSNET_ALLOW_MOCK_RUNTIME", raising=False)
    project_root = make_project(tmp_path)
    session_id = "genesis-layer5-failed-private-session-SECRET"
    prompt = "Private failed Genesis Layer 5 SECRET-FAILED-LAYER5 must stay out of evidence."
    client = TestClient(create_app(str(project_root)), raise_server_exceptions=False)

    response = client.post(
        "/chat",
        json={
            "session_id": session_id,
            "message": prompt,
            "model_hint": "ollama/mistral-small:4",
            "rag": False,
        },
    )

    assert response.status_code == 503
    native_hive = response.json()["detail"]["native_hive_forward_pass"]
    assert native_hive["genesis_operation_receipt_id"]
    operation_receipt_dir = (
        client.app.state.services.paths.artifacts_dir
        / "genesis"
        / "evidence-spine"
        / "operation-receipts"
    )
    receipt_files = list(operation_receipt_dir.glob("*.json"))
    assert len(receipt_files) == 1
    persisted_before_status_read = json.loads(receipt_files[0].read_text(encoding="utf-8"))
    assert persisted_before_status_read["operation_receipt_id"] == native_hive["genesis_operation_receipt_id"]
    assert persisted_before_status_read["replay_status"] == "recorded"
    heartbeat = client.get("/ops/brain/genesis-heartbeat", params={"session_id": session_id}).json()
    heartbeat_record = heartbeat["records"][0]
    evidence = client.get("/ops/brain/genesis-evidence-spine", params={"session_id": session_id}).json()
    checkpoint = evidence["checkpoint_snapshot"]
    operation = evidence["operation_receipt"]

    assert operation["schema_version"] == "nexusnet-genesis-operation-receipt-v1"
    assert operation["surface_id"] == "genesis-operation-receipt"
    assert operation["status"] == "degraded-source"
    assert operation["source_brain_generate_status"] == "runtime-unavailable"
    assert operation["source_heartbeat_record_id"] == native_hive["genesis_heartbeat_record_id"]
    assert operation["source_hive_run_id"] == native_hive["hive_run_id"]
    assert operation["hive_activation_id"] == heartbeat_record["hive_activation_id"]
    assert operation["neural_pathway_id"] == heartbeat_record["neural_pathway_id"]
    assert operation["synaptic_transmission_id"] == heartbeat_record["synaptic_transmission_id"]
    assert operation["checkpoint_id"] == checkpoint["checkpoint_id"]
    assert operation["runtime_growth_receipt_id"] == native_hive["runtime_growth_receipt_id"]
    assert operation["federated_packet_id"] == native_hive["federated_packet_id"]
    assert operation["content_ref"].startswith("sha256:")
    assert operation["rollback_aware"] is True
    assert operation["replay_status"] == "replayed"
    assert operation["raw_content_included"] is False
    assert operation["active_production_mutation_allowed"] is False

    assert checkpoint["source_brain_generate_status"] == "runtime-unavailable"
    assert checkpoint["hive_activation_id"] == operation["hive_activation_id"]
    assert checkpoint["neural_pathway_id"] == operation["neural_pathway_id"]
    assert checkpoint["synaptic_transmission_id"] == operation["synaptic_transmission_id"]
    assert evidence["shared_event_spine"]["operation_receipt_id"] == operation["operation_receipt_id"]
    trust_kinds = {
        record["artifact_kind"]
        for record in evidence["artifact_trust_registry"]["records"]
    }
    assert "genesis-operation-receipt" in trust_kinds
    assert operation["content_ref"] in evidence["content_addressed_evidence_refs"]

    restarted_client = TestClient(create_app(str(project_root)))
    replayed = restarted_client.get(
        "/ops/brain/genesis-evidence-spine",
        params={"session_id": session_id},
    ).json()
    assert replayed["operation_receipt"]["operation_receipt_id"] == operation["operation_receipt_id"]
    assert replayed["operation_receipt"]["replay_status"] == "replayed"
    assert replayed["checkpoint_snapshot"]["checkpoint_id"] == checkpoint["checkpoint_id"]

    control_panel = restarted_client.get(
        "/ops/brain/visualizer/state",
        params={"session_id": session_id},
    ).json()["overlay_state"]["control_panel"]
    control_evidence = control_panel["genesis_evidence_spine_status"]
    assert control_evidence["operation_receipt"]["operation_receipt_id"] == operation["operation_receipt_id"]
    assert control_evidence["operation_receipt"]["status"] == "degraded-source"

    serialized = json.dumps(
        {
            "heartbeat": heartbeat_record,
            "evidence": replayed,
            "control": control_evidence,
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-FAILED-LAYER5" not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized
    assert "F:\\" not in serialized


def test_degraded_native_hive_forward_automatically_creates_idempotent_governed_repair_proposal(
    tmp_path: Path,
    monkeypatch,
):
    project_root = make_project(tmp_path)
    session_id = "genesis-automatic-repair-private-session-SECRET"
    healthy_prompt = "Healthy Genesis forward pass SECRET-HEALTHY must not propose a repair."
    degraded_prompt = "Degraded Genesis forward pass SECRET-DEGRADED must stay out of repair evidence."

    monkeypatch.setenv("NEXUSNET_ALLOW_MOCK_RUNTIME", "1")
    healthy_client = TestClient(create_app(str(project_root)))
    healthy_result = healthy_client.app.state.services.brain.generate(
        session_context=SessionContext(
            session_id=session_id,
            expert="researcher",
            task_type="genesis-automatic-repair-healthy",
            use_retrieval=False,
        ),
        prompt=healthy_prompt,
        model_hint="mock/default",
    )
    healthy_forward_pass = healthy_result.inference_trace.metrics["native_hive_forward_pass"]
    assert healthy_forward_pass["genesis_self_repair_status"] == "not-eligible"
    assert healthy_forward_pass["genesis_self_repair_proposal_id"] is None
    assert healthy_forward_pass["genesis_dream_research_status"] == "not-eligible"
    assert healthy_forward_pass["genesis_dream_research_proposal_id"] is None

    monkeypatch.setenv("NEXUSNET_PRODUCT_MODE", "1")
    monkeypatch.delenv("NEXUSNET_ALLOW_MOCK_RUNTIME", raising=False)
    degraded_client = TestClient(create_app(str(project_root)), raise_server_exceptions=False)
    response = degraded_client.post(
        "/chat",
        json={
            "session_id": session_id,
            "message": degraded_prompt,
            "model_hint": "ollama/mistral-small:4",
            "rag": False,
        },
    )

    assert response.status_code == 503
    native_hive = response.json()["detail"]["native_hive_forward_pass"]
    proposal_id = native_hive["genesis_self_repair_proposal_id"]
    assert native_hive["genesis_heartbeat_status"] == "degraded"
    assert native_hive["genesis_self_repair_status"] == "proposal"
    assert proposal_id
    dream_proposal_id = native_hive["genesis_dream_research_proposal_id"]
    assert native_hive["genesis_dream_research_status"] == "dream-proposal"
    assert dream_proposal_id
    project_heartbeat = degraded_client.app.state.services.brain.hive_substrate.summary(
        session_id=session_id
    )["project_heartbeat"]
    project_heartbeat_lanes = {lane["lane_id"]: lane for lane in project_heartbeat["lanes"]}
    assert project_heartbeat["status"] == "degraded"
    assert project_heartbeat["source_brain_generate_status"] == "runtime-unavailable"
    assert project_heartbeat_lanes["model-serving-runtime"]["status"] == "degraded"
    assert any(
        "runtime-unavailable" in blocker
        for blocker in project_heartbeat_lanes["model-serving-runtime"]["blockers"]
    )
    assert project_heartbeat_lanes["native-hive-substrate"]["status"] == "degraded"
    assert "native_hive_forward_pass_blocked" in project_heartbeat_lanes["native-hive-substrate"]["blockers"]
    native_project_heartbeat = degraded_client.app.state.services.brain.hive_substrate.replay(
        session_id=session_id
    )["project_heartbeat_replay_chain"][0]
    assert native_project_heartbeat["source_brain_generate_status"] == "runtime-unavailable"
    assert native_project_heartbeat["source_runtime_degraded"] is True

    heartbeat = degraded_client.get(
        "/ops/brain/genesis-heartbeat",
        params={"session_id": session_id},
    ).json()
    degraded_record = next(record for record in heartbeat["records"] if record["status"] == "degraded")
    self_repair = degraded_client.get(
        "/ops/brain/genesis-self-repair",
        params={"session_id": session_id},
    ).json()
    proposal = self_repair["recent_proposals"][0]
    dream_research = degraded_client.get(
        "/ops/brain/genesis-dream-research",
        params={"session_id": session_id},
    ).json()
    dream = dream_research["recent_proposals"][0]

    assert self_repair["proposal_count"] == 1
    assert self_repair["sandbox_eval_count"] == 0
    assert self_repair["approval_count"] == 0
    assert self_repair["application_count"] == 0
    assert self_repair["rollback_count"] == 0
    assert proposal["proposal_id"] == proposal_id
    assert proposal["proposal_origin"] == "automatic-degraded-heartbeat"
    assert proposal["source_event_type"] == "genesis.heartbeat.recorded"
    assert proposal["admin_approval_required"] is True
    assert proposal["sandbox_eval_required"] is True
    assert proposal["safe_apply_allowed"] is False
    assert proposal["active_production_mutated"] is False
    assert proposal["raw_content_included"] is False
    assert dream_research["proposal_count"] == 1
    assert dream["dream_proposal_id"] == dream_proposal_id
    assert dream["proposal_origin"] == "automatic-degraded-heartbeat"
    assert dream["source_event_type"] == "genesis.heartbeat.recorded"
    assert dream["linked_self_repair_proposal_id"] == proposal_id
    assert dream["promotion_allowed"] is False
    assert dream["sandbox_eval_required"] is True
    assert dream["admin_approval_required"] is True
    assert dream["active_production_mutated"] is False
    assert dream["raw_content_included"] is False
    assert not (
        degraded_client.app.state.services.paths.artifacts_dir
        / "genesis"
        / "safe-files"
        / "self-repair"
    ).exists()

    replay = degraded_client.app.state.genesis_self_repair.propose_from_degraded_heartbeat(
        session_id=session_id,
        heartbeat_record=degraded_record,
    )
    assert replay["status"] == "proposal-replayed"
    assert replay["proposal_id"] == proposal_id
    dream_replay = degraded_client.app.state.genesis_dream_research.propose_from_degraded_heartbeat(
        session_id=session_id,
        heartbeat_record=degraded_record,
    )
    assert dream_replay["status"] == "dream-proposal-replayed"
    assert dream_replay["dream_proposal_id"] == dream_proposal_id

    restarted_client = TestClient(create_app(str(project_root)))
    restarted = restarted_client.get(
        "/ops/brain/genesis-self-repair",
        params={"session_id": session_id},
    ).json()
    assert restarted["proposal_count"] == 1
    assert restarted["latest_proposal_id"] == proposal_id
    assert restarted["automatic_observation"]["degraded_heartbeat_proposal_count"] == 1
    assert restarted["automatic_observation"]["active_production_mutated"] is False
    restarted_dream_research = restarted_client.get(
        "/ops/brain/genesis-dream-research",
        params={"session_id": session_id},
    ).json()
    assert restarted_dream_research["proposal_count"] == 1
    assert restarted_dream_research["latest_dream_proposal_id"] == dream_proposal_id
    assert restarted_dream_research["automatic_observation"]["degraded_heartbeat_proposal_count"] == 1
    assert restarted_dream_research["automatic_observation"]["promotion_started"] is False
    control_panel = restarted_client.get(
        "/ops/brain/visualizer/state",
        params={"session_id": session_id},
    ).json()["overlay_state"]["control_panel"]
    control_repair = control_panel["genesis_self_repair_status"]
    assert control_repair["latest_proposal_id"] == proposal_id
    assert control_repair["automatic_observation"]["degraded_heartbeat_proposal_count"] == 1
    assert control_repair["automatic_observation"]["safe_apply_started"] is False
    control_dream_research = control_panel["genesis_dream_research_status"]
    assert control_dream_research["latest_dream_proposal_id"] == dream_proposal_id
    assert control_dream_research["automatic_observation"]["degraded_heartbeat_proposal_count"] == 1
    assert control_dream_research["automatic_observation"]["promotion_started"] is False

    serialized = json.dumps(
        {
            "native_hive": native_hive,
            "self_repair": restarted,
            "replay": replay,
            "control": control_repair,
            "dream_research": restarted_dream_research,
            "dream_replay": dream_replay,
            "control_dream_research": control_dream_research,
        },
        sort_keys=True,
    )
    assert healthy_prompt not in serialized
    assert degraded_prompt not in serialized
    assert "SECRET-HEALTHY" not in serialized
    assert "SECRET-DEGRADED" not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized
    assert "F:\\" not in serialized


def test_genesis_self_repair_consumes_shared_event_for_admin_approved_safe_apply_and_rollback(tmp_path: Path):
    project_root = make_project(tmp_path)
    session_id = "genesis-self-repair-private-session-SECRET"
    prompt = "Private Genesis self repair SECRET-SELF-REPAIR should not enter repair evidence."
    admin_identity = "layer9-self-repair-admin@example.invalid"
    client = TestClient(create_app(str(project_root)))
    services = client.app.state.services

    result = services.brain.generate(
        session_context=SessionContext(
            session_id=session_id,
            expert="researcher",
            task_type="genesis-self-repair",
            use_retrieval=False,
            metadata={"graph_plane_tags": ["self_repair", "governance", "rollback", "event_spine"]},
        ),
        prompt=prompt,
        model_hint="mock/default",
    )
    native_hive = result.inference_trace.metrics["native_hive_forward_pass"]
    admission_decision_id = native_hive["genesis_memory_admission_decision_id"]

    event_spine = client.get("/ops/brain/genesis-event-spine", params={"session_id": session_id}).json()
    memory_event = next(
        event
        for event in event_spine["events"]
        if event["event_type"] == "genesis.memory.admission.decision"
    )
    assert memory_event["correlation_ref"] == admission_decision_id

    proposal = client.post(
        "/ops/brain/genesis-self-repair/proposals/from-event",
        json={
            "session_id": session_id,
            "event_ref": memory_event["event_ref"],
            "target_ref": "genesis/safe-files/self-repair/event-spine-repair.json",
            "repair_objective": "restore governed event-spine memory admission posture",
        },
    ).json()
    assert proposal["status"] == "proposal"
    assert proposal["source_event_ref"] == memory_event["event_ref"]
    assert proposal["source_event_type"] == "genesis.memory.admission.decision"
    assert proposal["target_ref"] == "genesis/safe-files/self-repair/event-spine-repair.json"
    assert proposal["admin_approval_required"] is True
    assert proposal["sandbox_eval_required"] is True
    assert proposal["safe_apply_allowed"] is False
    assert proposal["raw_content_included"] is False

    blocked_apply = client.post(
        f"/ops/brain/genesis-self-repair/proposals/{proposal['proposal_id']}/apply",
        json={
            "test_results": [
                {
                    "command": "python -m pytest tests/test_genesis_foundation.py -q",
                    "passed": True,
                    "failure_count": 0,
                    "evidence_ref": "pytest::self-repair-before-approval",
                }
            ]
        },
    )
    assert blocked_apply.status_code == 400
    assert "sandbox eval" in blocked_apply.json()["detail"].lower()

    sandbox_eval = client.post(
        f"/ops/brain/genesis-self-repair/proposals/{proposal['proposal_id']}/sandbox-eval",
        json={
            "eval_cases": [
                {"case_id": "source-event-is-sanitized", "expected": "sanitized-event"},
                {"case_id": "safe-file-boundary", "expected": "genesis-safe-file"},
                {"case_id": "rollback-boundary", "expected": "rollback-required"},
            ],
            "artifact_trust_ref": "artifact-trust::genesis-self-repair-event-spine",
            "rollback_proof_ref": "rollback-proof::genesis-self-repair-event-spine",
        },
    ).json()
    assert sandbox_eval["status"] == "passed"
    assert sandbox_eval["passed"] is True
    assert sandbox_eval["proposal_id"] == proposal["proposal_id"]
    assert sandbox_eval["source_event_ref"] == memory_event["event_ref"]
    assert sandbox_eval["case_count"] == 3
    assert sandbox_eval["shared_event_spine"]["event_type"] == "genesis.self_repair.sandbox_eval"
    assert sandbox_eval["raw_content_included"] is False

    approved = client.post(
        f"/ops/brain/genesis-self-repair/proposals/{proposal['proposal_id']}/approve",
        json={"approved_by": admin_identity, "approval_ref": "admin-approval::genesis-self-repair-event-spine"},
    ).json()
    assert approved["status"] == "admin-approved"
    assert approved["operator_approved"] is True
    assert approved["proposal_id"] == proposal["proposal_id"]
    assert approved["approver_digest"].startswith("sha256:")
    assert admin_identity not in json.dumps(approved, sort_keys=True)
    immune_decision = _approve_layer10_self_repair_candidate(client, proposal["proposal_id"])

    applied = client.post(
        f"/ops/brain/genesis-self-repair/proposals/{proposal['proposal_id']}/apply",
        json={
            "test_results": [
                {
                    "command": "python -m pytest tests/test_genesis_foundation.py -q",
                    "passed": True,
                    "failure_count": 0,
                    "evidence_ref": "pytest::genesis-self-repair-focused",
                }
            ],
            "immune_governance_decision_id": immune_decision["decision_id"],
        },
    ).json()
    assert applied["status"] == "applied-shadow-safe-file"
    assert applied["self_repair_status"] == "applied"
    assert applied["evidence_spine_apply"]["status"] == "applied-shadow-safe-file"
    assert applied["active_production_mutated"] is False
    safe_file_path = services.paths.artifacts_dir / "genesis" / "safe-files" / "self-repair" / "event-spine-repair.json"
    safe_file_payload = json.loads(safe_file_path.read_text(encoding="utf-8"))
    assert safe_file_payload["source_event_ref"] == memory_event["event_ref"]
    assert safe_file_payload["repair_status"] == "shadow-safe-file-applied"
    assert safe_file_payload["raw_content_included"] is False
    assert safe_file_payload["active_production_mutated"] is False

    rollback = client.post(
        f"/ops/brain/genesis-self-repair/proposals/{proposal['proposal_id']}/rollback",
        json={"reason": "focused self-repair rollback proof SECRET-ROLLBACK"},
    ).json()
    assert rollback["status"] == "rolled-back"
    assert rollback["self_repair_status"] == "rolled-back"
    assert rollback["rollback_restored"] is True
    assert rollback["evidence_spine_rollback"]["status"] == "rolled-back"
    assert rollback["active_production_mutated"] is False
    assert not safe_file_path.exists()

    restarted_client = TestClient(create_app(str(project_root)))
    replayed = restarted_client.get("/ops/brain/genesis-self-repair", params={"session_id": session_id}).json()
    assert replayed["schema_version"] == "nexusnet-genesis-self-repair-v1"
    assert replayed["status"] == "live-control-plane"
    assert replayed["latest_proposal_id"] == proposal["proposal_id"]
    assert replayed["latest_sandbox_eval_run"]["eval_run_id"] == sandbox_eval["eval_run_id"]
    assert replayed["latest_application"]["apply_id"] == applied["apply_id"]
    assert replayed["latest_rollback"]["rollback_id"] == rollback["rollback_id"]
    assert replayed["shared_event_spine"]["event_count"] >= 4

    control_panel = restarted_client.get(
        "/ops/brain/visualizer/state",
        params={"session_id": session_id},
    ).json()["overlay_state"]["control_panel"]
    assert control_panel["genesis_self_repair_status"]["latest_proposal_id"] == proposal["proposal_id"]
    assert control_panel["genesis_self_repair_status"]["latest_rollback"]["status"] == "rolled-back"
    assert control_panel["live_refs"]["genesis_self_repair_status"] == "/ops/brain/genesis-self-repair"

    serialized = json.dumps(
        {
            "event_spine": event_spine,
            "proposal": proposal,
            "sandbox_eval": sandbox_eval,
            "approval": approved,
            "apply": applied,
            "safe_file": safe_file_payload,
            "rollback": rollback,
            "replayed": replayed,
            "control": control_panel["genesis_self_repair_status"],
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-SELF-REPAIR" not in serialized
    assert "SECRET-ROLLBACK" not in serialized
    assert session_id not in serialized
    assert admin_identity not in serialized
    assert str(project_root) not in serialized
    assert "F:\\" not in serialized


def test_genesis_dream_research_proposes_from_shared_event_and_feeds_governed_self_repair(tmp_path: Path):
    project_root = make_project(tmp_path)
    session_id = "genesis-dream-research-private-session-SECRET"
    prompt = "Private Genesis dream research SECRET-DREAM-RESEARCH should not enter dream evidence."
    admin_identity = "layer12-dream-admin@example.invalid"
    client = TestClient(create_app(str(project_root)))
    services = client.app.state.services

    result = services.brain.generate(
        session_context=SessionContext(
            session_id=session_id,
            expert="researcher",
            task_type="genesis-dream-research",
            use_retrieval=False,
            metadata={"graph_plane_tags": ["dream", "research", "self_repair", "governance"]},
        ),
        prompt=prompt,
        model_hint="mock/default",
    )
    native_hive = result.inference_trace.metrics["native_hive_forward_pass"]
    admission_decision_id = native_hive["genesis_memory_admission_decision_id"]

    event_spine = client.get("/ops/brain/genesis-event-spine", params={"session_id": session_id}).json()
    memory_event = next(
        event
        for event in event_spine["events"]
        if event["event_type"] == "genesis.memory.admission.decision"
    )
    assert memory_event["correlation_ref"] == admission_decision_id

    dream = client.post(
        "/ops/brain/genesis-dream-research/proposals/from-event",
        json={
            "session_id": session_id,
            "event_ref": memory_event["event_ref"],
            "dream_objective": "dream a governed repair path for memory-admission quarantine",
            "research_refs": [
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md",
                "docs/research/CANON_DEEP_DETAIL_ADDENDUM_2026-05-31.md",
            ],
            "target_ref": "genesis/safe-files/self-repair/dream-research-event-repair.json",
        },
    ).json()
    assert dream["schema_version"] == "nexusnet-genesis-dream-research-proposal-v1"
    assert dream["status"] == "dream-proposal"
    assert dream["source_event_ref"] == memory_event["event_ref"]
    assert dream["source_event_type"] == "genesis.memory.admission.decision"
    assert dream["dream_packet"]["dream_temperature"] == 0.95
    assert dream["critique_packet"]["critic_temperature"] == 0.2
    assert dream["research_packet"]["research_ref_count"] == 2
    assert dream["self_repair_candidate"]["status"] == "proposal"
    assert dream["self_repair_candidate"]["source_event_ref"] == memory_event["event_ref"]
    assert dream["linked_self_repair_proposal_id"] == dream["self_repair_candidate"]["proposal_id"]
    assert dream["promotion_allowed"] is False
    assert dream["raw_content_included"] is False

    linked_proposal_id = dream["linked_self_repair_proposal_id"]
    blocked_apply = client.post(
        f"/ops/brain/genesis-self-repair/proposals/{linked_proposal_id}/apply",
        json={
            "test_results": [
                {
                    "command": "python -m pytest tests/test_genesis_foundation.py -q",
                    "passed": True,
                    "failure_count": 0,
                    "evidence_ref": "pytest::dream-linked-before-eval",
                }
            ]
        },
    )
    assert blocked_apply.status_code == 400
    assert "sandbox eval" in blocked_apply.json()["detail"].lower()

    sandbox_eval = client.post(
        f"/ops/brain/genesis-self-repair/proposals/{linked_proposal_id}/sandbox-eval",
        json={
            "eval_cases": [
                {"case_id": "dream-source-event-is-sanitized", "expected": "sanitized-event"},
                {"case_id": "dream-has-low-temp-critique", "expected": "critique-required"},
                {"case_id": "dream-linked-repair-is-rollback-bound", "expected": "rollback-required"},
            ],
            "artifact_trust_ref": "artifact-trust::genesis-dream-research",
            "rollback_proof_ref": "rollback-proof::genesis-dream-research",
        },
    ).json()
    assert sandbox_eval["status"] == "passed"
    assert sandbox_eval["proposal_id"] == linked_proposal_id

    approved = client.post(
        f"/ops/brain/genesis-self-repair/proposals/{linked_proposal_id}/approve",
        json={"approved_by": admin_identity, "approval_ref": "admin-approval::genesis-dream-research"},
    ).json()
    assert approved["status"] == "admin-approved"
    assert admin_identity not in json.dumps(approved, sort_keys=True)
    immune_decision = _approve_layer10_self_repair_candidate(client, linked_proposal_id)

    applied = client.post(
        f"/ops/brain/genesis-self-repair/proposals/{linked_proposal_id}/apply",
        json={
            "test_results": [
                {
                    "command": "python -m pytest tests/test_genesis_foundation.py -q",
                    "passed": True,
                    "failure_count": 0,
                    "evidence_ref": "pytest::genesis-dream-research-focused",
                }
            ],
            "immune_governance_decision_id": immune_decision["decision_id"],
        },
    ).json()
    assert applied["status"] == "applied-shadow-safe-file"
    safe_file_path = services.paths.artifacts_dir / "genesis" / "safe-files" / "self-repair" / "dream-research-event-repair.json"
    safe_file_payload = json.loads(safe_file_path.read_text(encoding="utf-8"))
    assert safe_file_payload["source_event_ref"] == memory_event["event_ref"]
    assert safe_file_payload["repair_status"] == "shadow-safe-file-applied"
    assert safe_file_payload["raw_content_included"] is False

    rollback = client.post(
        f"/ops/brain/genesis-self-repair/proposals/{linked_proposal_id}/rollback",
        json={"reason": "focused dream-research rollback proof SECRET-DREAM-ROLLBACK"},
    ).json()
    assert rollback["status"] == "rolled-back"
    assert rollback["rollback_restored"] is True
    assert not safe_file_path.exists()

    restarted_client = TestClient(create_app(str(project_root)))
    replayed = restarted_client.get("/ops/brain/genesis-dream-research", params={"session_id": session_id}).json()
    assert replayed["schema_version"] == "nexusnet-genesis-dream-research-v1"
    assert replayed["status"] == "live-control-plane"
    assert replayed["latest_dream_proposal_id"] == dream["dream_proposal_id"]
    assert replayed["latest_proposal"]["linked_self_repair_proposal_id"] == linked_proposal_id
    assert replayed["shared_event_spine"]["event_count"] >= 1

    control_panel = restarted_client.get(
        "/ops/brain/visualizer/state",
        params={"session_id": session_id},
    ).json()["overlay_state"]["control_panel"]
    assert control_panel["genesis_dream_research_status"]["latest_dream_proposal_id"] == dream["dream_proposal_id"]
    assert control_panel["genesis_dream_research_status"]["latest_proposal"]["linked_self_repair_proposal_id"] == linked_proposal_id
    assert control_panel["live_refs"]["genesis_dream_research_status"] == "/ops/brain/genesis-dream-research"

    serialized = json.dumps(
        {
            "dream": dream,
            "sandbox_eval": sandbox_eval,
            "approval": approved,
            "apply": applied,
            "safe_file": safe_file_payload,
            "rollback": rollback,
            "replayed": replayed,
            "control": control_panel["genesis_dream_research_status"],
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-DREAM-RESEARCH" not in serialized
    assert "SECRET-DREAM-ROLLBACK" not in serialized
    assert session_id not in serialized
    assert admin_identity not in serialized
    assert str(project_root) not in serialized
    assert "F:\\" not in serialized


def test_genesis_dream_self_repair_outcomes_emit_federated_growth_packets(tmp_path: Path):
    project_root = make_project(tmp_path)
    session_id = "genesis-federated-outcomes-private-session-SECRET"
    prompt = "Private Genesis federated outcome SECRET-FED-OUTCOME should not enter packets."
    admin_identity = "layer12-fed-admin@example.invalid"
    client = TestClient(create_app(str(project_root)))
    services = client.app.state.services

    result = services.brain.generate(
        session_context=SessionContext(
            session_id=session_id,
            expert="researcher",
            task_type="genesis-federated-outcomes",
            use_retrieval=False,
            metadata={"graph_plane_tags": ["dream", "self_repair", "federation", "growth"]},
        ),
        prompt=prompt,
        model_hint="mock/default",
    )
    native_hive = result.inference_trace.metrics["native_hive_forward_pass"]
    event_spine = client.get("/ops/brain/genesis-event-spine", params={"session_id": session_id}).json()
    memory_event = next(
        event
        for event in event_spine["events"]
        if event["event_type"] == "genesis.memory.admission.decision"
    )
    assert memory_event["correlation_ref"] == native_hive["genesis_memory_admission_decision_id"]

    dream = client.post(
        "/ops/brain/genesis-dream-research/proposals/from-event",
        json={
            "session_id": session_id,
            "event_ref": memory_event["event_ref"],
            "dream_objective": "federate governed dream and self-repair outcomes",
            "research_refs": ["docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md"],
            "target_ref": "genesis/safe-files/self-repair/federated-dream-repair.json",
        },
    ).json()
    dream_packet = dream["federated_outcome_packet"]
    assert dream_packet["schema_version"] == "nexusnet-genesis-federated-outcome-packet-v1"
    assert dream_packet["outcome_type"] == "dream_research_proposed"
    assert dream_packet["source_event_ref"] == memory_event["event_ref"]
    assert dream_packet["linked_self_repair_proposal_id"] == dream["linked_self_repair_proposal_id"]
    assert dream_packet["per_user_global_learning_state"]["runtime_growth_captured"] is True
    assert dream_packet["per_user_global_learning_state"]["global_federated_packet_captured"] is True
    assert dream_packet["federated_packet"]["raw_content_included"] is False

    linked_proposal_id = dream["linked_self_repair_proposal_id"]
    sandbox_eval = client.post(
        f"/ops/brain/genesis-self-repair/proposals/{linked_proposal_id}/sandbox-eval",
        json={
            "eval_cases": [
                {"case_id": "federated-dream-source-event", "expected": "sanitized-event"},
                {"case_id": "federated-dream-safe-file", "expected": "safe-file"},
            ],
            "artifact_trust_ref": "artifact-trust::genesis-federated-outcome",
            "rollback_proof_ref": "rollback-proof::genesis-federated-outcome",
        },
    ).json()
    sandbox_packet = sandbox_eval["federated_outcome_packet"]
    assert sandbox_packet["outcome_type"] == "self_repair_sandbox_eval_passed"
    assert sandbox_packet["per_user_global_learning_state"]["global_federated_packet_captured"] is True

    approved = client.post(
        f"/ops/brain/genesis-self-repair/proposals/{linked_proposal_id}/approve",
        json={"approved_by": admin_identity, "approval_ref": "admin-approval::genesis-federated-outcome"},
    ).json()
    assert approved["status"] == "admin-approved"
    immune_decision = _approve_layer10_self_repair_candidate(client, linked_proposal_id)

    applied = client.post(
        f"/ops/brain/genesis-self-repair/proposals/{linked_proposal_id}/apply",
        json={
            "test_results": [
                {
                    "command": "python -m pytest tests/test_genesis_foundation.py -q",
                    "passed": True,
                    "failure_count": 0,
                    "evidence_ref": "pytest::genesis-federated-outcomes-focused",
                }
            ],
            "immune_governance_decision_id": immune_decision["decision_id"],
        },
    ).json()
    apply_packet = applied["federated_outcome_packet"]
    assert apply_packet["outcome_type"] == "self_repair_applied"
    assert apply_packet["source_event_ref"] == memory_event["event_ref"]

    rollback = client.post(
        f"/ops/brain/genesis-self-repair/proposals/{linked_proposal_id}/rollback",
        json={"reason": "focused federated rollback proof SECRET-FED-ROLLBACK"},
    ).json()
    rollback_packet = rollback["federated_outcome_packet"]
    assert rollback_packet["outcome_type"] == "self_repair_rolled_back"
    assert rollback_packet["rollback_id"] == rollback["rollback_id"]
    assert rollback_packet["active_production_mutation_allowed"] is False

    restarted_client = TestClient(create_app(str(project_root)))
    federated = restarted_client.get(
        "/ops/brain/genesis-federated-outcomes",
        params={"session_id": session_id},
    ).json()
    assert federated["schema_version"] == "nexusnet-genesis-federated-outcomes-v1"
    assert federated["status"] == "live-control-plane"
    assert federated["packet_count"] >= 4
    assert federated["latest_packet"]["outcome_type"] == "self_repair_rolled_back"
    assert federated["global_growth_impact"]["global_captures"] >= 4
    assert federated["per_user_global_learning_state"]["runtime_growth_captured"] is True
    assert federated["shared_event_spine"]["event_count"] >= 4

    control_panel = restarted_client.get(
        "/ops/brain/visualizer/state",
        params={"session_id": session_id},
    ).json()["overlay_state"]["control_panel"]
    assert control_panel["genesis_federated_outcome_status"]["latest_packet"]["outcome_type"] == "self_repair_rolled_back"
    assert control_panel["live_refs"]["genesis_federated_outcome_status"] == "/ops/brain/genesis-federated-outcomes"

    serialized = json.dumps(
        {
            "dream_packet": dream_packet,
            "sandbox_packet": sandbox_packet,
            "apply_packet": apply_packet,
            "rollback_packet": rollback_packet,
            "federated": federated,
            "control": control_panel["genesis_federated_outcome_status"],
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-FED-OUTCOME" not in serialized
    assert "SECRET-FED-ROLLBACK" not in serialized
    assert session_id not in serialized
    assert admin_identity not in serialized
    assert str(project_root) not in serialized
    assert "F:\\" not in serialized


def test_genesis_sensory_provenance_privacy_gate_records_real_brain_use_without_raw_content(tmp_path: Path):
    project_root = make_project(tmp_path)
    session_id = "genesis-sensory-private-session-SECRET"
    prompt = "Private Genesis sensory SECRET-LAYER6 should not enter sensory replay."
    client = TestClient(create_app(str(project_root)))
    services = client.app.state.services

    result = services.brain.generate(
        session_context=SessionContext(
            session_id=session_id,
            expert="researcher",
            task_type="genesis-sensory-provenance",
            use_retrieval=False,
            metadata={"graph_plane_tags": ["sensory", "provenance", "privacy", "neural_bus"]},
        ),
        prompt=prompt,
        model_hint="mock/default",
    )
    native_hive = result.inference_trace.metrics["native_hive_forward_pass"]
    sensory_event_id = native_hive["genesis_sensory_event_id"]
    heartbeat_record_id = native_hive["genesis_heartbeat_record_id"]

    sensory = client.get("/ops/brain/genesis-sensory-provenance", params={"session_id": session_id}).json()
    assert sensory["schema_version"] == "nexusnet-genesis-sensory-provenance-v1"
    assert sensory["surface_id"] == "genesis-sensory-provenance-privacy-gate"
    assert sensory["status"] == "live-control-plane"
    assert sensory["latest_event_id"] == sensory_event_id
    assert sensory["latest_heartbeat_record_id"] == heartbeat_record_id
    assert sensory["sensory_event_count"] == 1
    assert sensory["raw_content_included"] is False
    assert sensory["active_production_mutation_allowed"] is False

    latest_event = sensory["events"][0]
    assert latest_event["event_id"] == sensory_event_id
    assert latest_event["source_identity"]["source_kind"] == "end-user-wrapper-model-interaction"
    assert latest_event["source_identity"]["source_ref_digest"].startswith("sha256:")
    assert latest_event["trust_tier"] == "local-runtime-observed"
    assert latest_event["privacy_gate"]["privacy_class"] == "operator-private"
    assert latest_event["privacy_gate"]["redaction_status"] == "metadata-only-redacted"
    assert latest_event["privacy_gate"]["consent_status"] == "runtime-use-only"
    assert latest_event["privacy_gate"]["rights_license_status"] == "not-approved-for-training"
    assert latest_event["privacy_gate"]["quarantine_decision"]["training_allowed"] is False
    assert latest_event["privacy_gate"]["quarantine_decision"]["memory_write_allowed"] is False
    assert latest_event["neural_bus_projection"]["typed_event_envelope"]["event_type"] == "genesis.sensory.provenance"
    assert latest_event["neural_bus_projection"]["typed_event_envelope"]["event_privacy_label"] == "sanitized-sensory-provenance"
    assert latest_event["neural_bus_projection"]["plane_trace"]["planes"] == [
        "sensory",
        "provenance",
        "privacy",
        "neural_bus",
    ]

    restarted_client = TestClient(create_app(str(project_root)))
    replayed = restarted_client.get("/ops/brain/genesis-sensory-provenance", params={"session_id": session_id}).json()
    assert replayed["latest_event_id"] == sensory_event_id
    assert replayed["events"][0]["replay_status"] == "replayed"

    control_panel = restarted_client.get(
        "/ops/brain/visualizer/state",
        params={"session_id": session_id},
    ).json()["overlay_state"]["control_panel"]
    assert control_panel["genesis_sensory_provenance_status"]["latest_event_id"] == sensory_event_id
    assert control_panel["genesis_sensory_provenance_status"]["latest_heartbeat_record_id"] == heartbeat_record_id
    assert control_panel["live_refs"]["genesis_sensory_provenance_status"] == "/ops/brain/genesis-sensory-provenance"

    serialized = json.dumps(
        {
            "sensory": replayed,
            "control": control_panel["genesis_sensory_provenance_status"],
            "native_hive": native_hive,
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-LAYER6" not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized
    assert "F:\\" not in serialized


def test_failed_brain_transaction_propagates_layer5_receipt_through_sensory_and_memory_admission(
    tmp_path: Path,
    monkeypatch,
):
    monkeypatch.setenv("NEXUSNET_PRODUCT_MODE", "1")
    monkeypatch.delenv("NEXUSNET_ALLOW_MOCK_RUNTIME", raising=False)
    project_root = make_project(tmp_path)
    session_id = "genesis-layer6-failed-private-session-SECRET"
    prompt = "Private failed Genesis Layer 6 SECRET-FAILED-LAYER6 must stay quarantined."
    client = TestClient(create_app(str(project_root)), raise_server_exceptions=False)

    response = client.post(
        "/chat",
        json={
            "session_id": session_id,
            "message": prompt,
            "model_hint": "ollama/mistral-small:4",
            "rag": False,
        },
    )

    assert response.status_code == 503
    native_hive = response.json()["detail"]["native_hive_forward_pass"]
    operation_receipt_id = native_hive["genesis_operation_receipt_id"]
    checkpoint_id = native_hive["genesis_evidence_checkpoint_id"]

    sensory = client.get("/ops/brain/genesis-sensory-provenance", params={"session_id": session_id}).json()
    sensory_event = sensory["events"][0]
    assert sensory["latest_operation_receipt_id"] == operation_receipt_id
    assert sensory["latest_evidence_checkpoint_id"] == checkpoint_id
    assert sensory_event["operation_receipt_id"] == operation_receipt_id
    assert sensory_event["evidence_checkpoint_id"] == checkpoint_id
    assert sensory_event["source_brain_generate_status"] == "runtime-unavailable"
    assert sensory_event["source_critique_status"] == "not-run"
    assert sensory_event["privacy_gate"]["source_outcome_status"] == "runtime-unavailable"
    assert sensory_event["privacy_gate"]["failure_observation_only"] is True
    assert sensory_event["privacy_gate"]["consent_status"] == "runtime-use-only"
    assert sensory_event["privacy_gate"]["quarantine_decision"]["memory_write_allowed"] is False
    assert operation_receipt_id in sensory_event["provenance_refs"]
    assert checkpoint_id in sensory_event["provenance_refs"]
    assert operation_receipt_id in sensory_event["shared_event_spine"]["evidence_refs"]

    admission = client.get("/ops/brain/genesis-memory-admission", params={"session_id": session_id}).json()
    decision = admission["latest_decision"]
    assert admission["latest_operation_receipt_id"] == operation_receipt_id
    assert admission["latest_evidence_checkpoint_id"] == checkpoint_id
    assert decision["operation_receipt_id"] == operation_receipt_id
    assert decision["evidence_checkpoint_id"] == checkpoint_id
    assert decision["source_brain_generate_status"] == "runtime-unavailable"
    assert decision["decision"] == "blocked-private-runtime-content"
    assert decision["memory_write_allowed"] is False
    assert decision["retrieval_truth_allowed"] is False
    assert decision["training_allowed"] is False
    assert operation_receipt_id in decision["evidence_refs"]
    assert checkpoint_id in decision["evidence_refs"]
    assert native_hive["genesis_memory_admission"]["operation_receipt_id"] == operation_receipt_id
    assert native_hive["genesis_memory_admission"]["evidence_checkpoint_id"] == checkpoint_id

    restarted_client = TestClient(create_app(str(project_root)))
    replayed_sensory = restarted_client.get(
        "/ops/brain/genesis-sensory-provenance",
        params={"session_id": session_id},
    ).json()
    replayed_admission = restarted_client.get(
        "/ops/brain/genesis-memory-admission",
        params={"session_id": session_id},
    ).json()
    assert replayed_sensory["events"][0]["operation_receipt_id"] == operation_receipt_id
    assert replayed_sensory["events"][0]["replay_status"] == "replayed"
    assert replayed_admission["latest_decision"]["operation_receipt_id"] == operation_receipt_id
    assert replayed_admission["latest_decision"]["replay_status"] == "replayed"

    control_panel = restarted_client.get(
        "/ops/brain/visualizer/state",
        params={"session_id": session_id},
    ).json()["overlay_state"]["control_panel"]
    assert (
        control_panel["genesis_sensory_provenance_status"]["latest_operation_receipt_id"]
        == operation_receipt_id
    )
    assert (
        control_panel["genesis_memory_admission_status"]["latest_operation_receipt_id"]
        == operation_receipt_id
    )

    serialized = json.dumps(
        {
            "sensory": replayed_sensory,
            "admission": replayed_admission,
            "control_sensory": control_panel["genesis_sensory_provenance_status"],
            "control_admission": control_panel["genesis_memory_admission_status"],
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-FAILED-LAYER6" not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized
    assert "F:\\" not in serialized


def test_genesis_memory_admission_blocks_private_sensory_from_memory_and_retrieval_truth(tmp_path: Path):
    project_root = make_project(tmp_path)
    session_id = "genesis-memory-private-session-SECRET"
    prompt = "Private Genesis memory admission SECRET-LAYER7 should not become memory truth."
    client = TestClient(create_app(str(project_root)))
    services = client.app.state.services

    result = services.brain.generate(
        session_context=SessionContext(
            session_id=session_id,
            expert="researcher",
            task_type="genesis-memory-admission",
            use_retrieval=False,
            metadata={"graph_plane_tags": ["memory", "provenance", "privacy", "retrieval"]},
        ),
        prompt=prompt,
        model_hint="mock/default",
    )
    native_hive = result.inference_trace.metrics["native_hive_forward_pass"]

    memory_view = services.memory.session_view(session_id)
    retrieval_policy = services.retrieval.query_with_policy(
        request=RetrievalRequest(
            query="SECRET-LAYER7 memory admission",
            session_id=session_id,
            top_k=5,
        )
    )
    serialized_admission_surfaces = json.dumps(
            {
                "memory_view": memory_view,
                "retrieval_policy": retrieval_policy,
            },
            sort_keys=True,
            default=lambda value: value.model_dump(mode="json") if hasattr(value, "model_dump") else str(value),
        )
    assert prompt not in serialized_admission_surfaces
    assert "SECRET-LAYER7" not in serialized_admission_surfaces

    admission_decision_id = native_hive["genesis_memory_admission_decision_id"]
    admission = client.get("/ops/brain/genesis-memory-admission", params={"session_id": session_id}).json()
    assert admission["schema_version"] == "nexusnet-genesis-memory-admission-v1"
    assert admission["surface_id"] == "genesis-memory-admission-gate"
    assert admission["status"] == "live-control-plane"
    assert admission["latest_decision_id"] == admission_decision_id
    assert admission["latest_sensory_event_id"] == native_hive["genesis_sensory_event_id"]
    assert admission["latest_decision"]["decision"] == "blocked-private-runtime-content"
    assert admission["latest_decision"]["memory_write_allowed"] is False
    assert admission["latest_decision"]["retrieval_truth_allowed"] is False
    assert admission["latest_decision"]["training_allowed"] is False
    assert admission["latest_decision"]["sanitized_receipt_written"] is True
    assert admission["latest_decision"]["raw_content_included"] is False
    assert admission["raw_content_included"] is False
    assert admission["active_production_mutation_allowed"] is False

    restarted_client = TestClient(create_app(str(project_root)))
    replayed = restarted_client.get("/ops/brain/genesis-memory-admission", params={"session_id": session_id}).json()
    assert replayed["latest_decision_id"] == admission_decision_id
    assert replayed["latest_decision"]["replay_status"] == "replayed"

    control_panel = restarted_client.get(
        "/ops/brain/visualizer/state",
        params={"session_id": session_id},
    ).json()["overlay_state"]["control_panel"]
    assert control_panel["genesis_memory_admission_status"]["latest_decision_id"] == admission_decision_id
    assert control_panel["genesis_memory_admission_status"]["latest_decision"]["decision"] == "blocked-private-runtime-content"
    assert control_panel["live_refs"]["genesis_memory_admission_status"] == "/ops/brain/genesis-memory-admission"

    serialized = json.dumps(
        {
            "admission": replayed,
            "control": control_panel["genesis_memory_admission_status"],
            "native_hive": native_hive,
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-LAYER7" not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized
    assert "F:\\" not in serialized


def test_genesis_memory_admission_gates_manual_memory_and_retrieval_ingress(tmp_path: Path):
    project_root = make_project(tmp_path)
    session_id = "genesis-manual-ingress-private-session-SECRET"
    private_text = "Manual private ingress SECRET-LAYER7B must not become memory or retrieval truth."
    client = TestClient(create_app(str(project_root)))
    services = client.app.state.services

    saved_memory = services.memory.append_messages(
        session_id,
        [Message(role="user", content=private_text)],
    )
    doc_ids = services.retrieval.ingest(
        RetrievalIngestRequest(
            documents=[
                RetrievalDocumentInput(
                    source="manual-private-upload",
                    title="Manual private ingress",
                    text=private_text,
                    metadata={
                        "source_kind": "manual-operator-ingress",
                        "session_id": session_id,
                        "privacy_class": "operator-private",
                        "consent_status": "runtime-use-only",
                        "rights_license_status": "not-approved-for-training",
                    },
                )
            ]
        )
    )

    assert saved_memory == []
    assert doc_ids == []

    memory_view = services.memory.session_view(session_id)
    retrieval_policy = services.retrieval.query_with_policy(
        RetrievalRequest(
            query="SECRET-LAYER7B manual private ingress",
            session_id=session_id,
            top_k=5,
        )
    )
    serialized_ingress_surfaces = json.dumps(
        {
            "memory_view": memory_view,
            "retrieval_policy": retrieval_policy,
        },
        sort_keys=True,
        default=lambda value: value.model_dump(mode="json") if hasattr(value, "model_dump") else str(value),
    )
    assert private_text not in serialized_ingress_surfaces
    assert "SECRET-LAYER7B" not in serialized_ingress_surfaces

    admission = client.get("/ops/brain/genesis-memory-admission", params={"session_id": session_id}).json()
    assert admission["schema_version"] == "nexusnet-genesis-memory-admission-v1"
    assert admission["surface_id"] == "genesis-memory-admission-gate"
    assert admission["status"] == "live-control-plane"
    assert admission["decision_count"] >= 2

    decisions = admission["decisions"]
    by_route = {decision["ingress_route"]: decision for decision in decisions}
    assert by_route["manual-memory-append"]["decision"] == "blocked-private-manual-ingress"
    assert by_route["manual-memory-append"]["memory_write_allowed"] is False
    assert by_route["retrieval-document-ingest"]["decision"] == "blocked-private-manual-ingress"
    assert by_route["retrieval-document-ingest"]["retrieval_truth_allowed"] is False
    assert by_route["retrieval-document-ingest"]["training_allowed"] is False
    assert all(decision["sanitized_receipt_written"] is True for decision in decisions)
    assert all(decision["raw_content_included"] is False for decision in decisions)

    restarted_client = TestClient(create_app(str(project_root)))
    replayed = restarted_client.get("/ops/brain/genesis-memory-admission", params={"session_id": session_id}).json()
    assert replayed["decision_count"] >= 2
    assert replayed["decisions"][0]["replay_status"] == "replayed"

    control_panel = restarted_client.get(
        "/ops/brain/visualizer/state",
        params={"session_id": session_id},
    ).json()["overlay_state"]["control_panel"]
    assert control_panel["genesis_memory_admission_status"]["decision_count"] >= 2
    assert control_panel["live_refs"]["genesis_memory_admission_status"] == "/ops/brain/genesis-memory-admission"

    serialized = json.dumps(
        {
            "admission": replayed,
            "control": control_panel["genesis_memory_admission_status"],
        },
        sort_keys=True,
    )
    assert private_text not in serialized
    assert "SECRET-LAYER7B" not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized
    assert "F:\\" not in serialized


def test_genesis_memory_admission_gates_private_source_claims_from_graph_kac_and_training_truth(tmp_path: Path):
    project_root = make_project(tmp_path)
    session_id = "genesis-source-claim-private-session-SECRET"
    private_claim = "Private source claim SECRET-LAYER7C must not become graph, KAC, retrieval, or training truth."
    client = TestClient(create_app(str(project_root)))
    services = client.app.state.services

    claim = services.brain_memory_quality.record_claim(
        SourceClaimRequest(
            claim_id="claim::genesis-layer7c-private",
            answer_id="answer::genesis-layer7c",
            claim_text=private_claim,
            answerability_status="source_backed",
            source_status="operator_supplied",
            source_refs=["manual-private-source"],
            graph_refs=["graph::operator-private"],
            contains_private_data=True,
            consent_ref="",
            confidence=0.86,
            promotion_state="canon_candidate",
            metadata={
                "session_id": session_id,
                "source_kind": "manual-operator-ingress",
                "privacy_class": "operator-private",
                "consent_status": "runtime-use-only",
                "rights_license_status": "not-approved-for-training",
            },
        )
    )

    assert claim["status"] == "blocked"
    assert claim["claim_text"].startswith("redacted::sha256:")
    assert claim["raw_content_included"] is False
    assert claim["memory_write_allowed"] is False
    assert claim["retrieval_truth_allowed"] is False
    assert claim["training_allowed"] is False
    assert claim["graph_truth_allowed"] is False
    assert claim["knowledge_artifact_allowed"] is False
    assert claim["genesis_memory_admission"]["ingress_route"] == "source-claim-record"
    assert claim["genesis_memory_admission"]["decision"] == "blocked-private-manual-ingress"
    assert claim["metadata"]["session_ref_digest"].startswith("sha256:")
    assert "session_id" not in claim["metadata"]

    claim_artifact = Path(claim["artifact_path"]).read_text(encoding="utf-8")
    serialized_claim = json.dumps({"claim": claim, "artifact": claim_artifact}, sort_keys=True)
    assert private_claim not in serialized_claim
    assert "SECRET-LAYER7C" not in serialized_claim
    assert session_id not in serialized_claim

    admission = client.get("/ops/brain/genesis-memory-admission", params={"session_id": session_id}).json()
    decisions = admission["decisions"]
    by_route = {decision["ingress_route"]: decision for decision in decisions}
    assert by_route["source-claim-record"]["decision"] == "blocked-private-manual-ingress"
    assert by_route["source-claim-record"]["memory_write_allowed"] is False
    assert by_route["source-claim-record"]["retrieval_truth_allowed"] is False
    assert by_route["source-claim-record"]["training_allowed"] is False
    assert by_route["source-claim-record"]["raw_content_included"] is False

    restarted_client = TestClient(create_app(str(project_root)))
    control_panel = restarted_client.get(
        "/ops/brain/visualizer/state",
        params={"session_id": session_id},
    ).json()["overlay_state"]["control_panel"]

    serialized = json.dumps(
        {
            "admission": restarted_client.get(
                "/ops/brain/genesis-memory-admission",
                params={"session_id": session_id},
            ).json(),
            "control": control_panel["genesis_memory_admission_status"],
        },
        sort_keys=True,
    )
    assert private_claim not in serialized
    assert "SECRET-LAYER7C" not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized
    assert "F:\\" not in serialized


def test_genesis_memory_admission_gates_kac_and_graph_ingress_from_private_sources(tmp_path: Path):
    project_root = make_project(tmp_path)
    session_id = "genesis-kac-graph-private-session-SECRET"
    private_text = "Private KAC graph ingress SECRET-LAYER7D must not become compiled, graph, retrieval, or training truth."
    client = TestClient(create_app(str(project_root)))

    compiled = client.post(
        "/ops/brain/knowledge-artifacts/compile",
        json={
            "task_family": "genesis_private_source_gate",
            "scope": {"rbac_scope": ["operator"]},
            "sources": [
                {
                    "source_ref": "manual:private-kac-source",
                    "title": "Private KAC source",
                    "text": private_text,
                    "permission_state": "allowed",
                    "privacy_class": "operator-private",
                    "license_state": "not-approved-for-training",
                    "rbac_scope": ["operator"],
                    "metadata": {
                        "session_id": session_id,
                        "source_kind": "manual-operator-ingress",
                        "privacy_class": "operator-private",
                        "consent_status": "runtime-use-only",
                        "rights_license_status": "not-approved-for-training",
                    },
                }
            ],
        },
    )

    assert compiled.status_code == 200
    artifact = compiled.json()
    assert artifact["status"] == "blocked"
    assert artifact["source_digests"] == []
    assert artifact["source_ref_security_gate"]["allowed"] is False
    assert artifact["source_ref_security_gate"]["blocked_count"] == 1
    assert artifact["blocked_source_refs"][0]["reason"] == "genesis_memory_admission_blocked"
    assert artifact["control_panel_replay"]["genesis_memory_admission_gate"]["blocked_count"] == 1
    assert artifact["artifact_trust_preview"]["status"] == "quarantined"

    queried = client.post(
        "/ops/brain/knowledge-artifacts/query",
        json={
            "intent": "use_private_compiled_context",
            "contexts": [artifact["artifact_id"]],
            "filters": {"task_family": "genesis_private_source_gate"},
            "budget": {"prefer_compiled_artifacts": True, "fallback_to_raw_retrieval": True},
        },
    )
    assert queried.status_code == 200
    assert queried.json()["fallback_state"] == "compiled_artifact_quarantined"
    assert queried.json()["runtime_context_allowed"] is False

    graph_ingest = client.post(
        "/ops/brain/graph/ingest",
        json={
            "source": "manual-private-graph",
            "text": private_text,
            "session_id": session_id,
            "plane_hint": "dream",
            "metadata": {
                "doc_id": "private-graph-doc",
                "source_kind": "manual-operator-ingress",
                "privacy_class": "operator-private",
                "consent_status": "runtime-use-only",
                "rights_license_status": "not-approved-for-training",
            },
        },
    )
    assert graph_ingest.status_code == 200
    graph_payload = graph_ingest.json()
    assert graph_payload["ingest_blocked"] is True
    assert graph_payload["nodes_added"] == 0
    assert graph_payload["edges_added"] == 0
    assert graph_payload["genesis_memory_admission"]["decision"] == "blocked-private-manual-ingress"
    assert graph_payload["genesis_memory_admission"]["raw_content_included"] is False

    graph_query = client.post(
        "/ops/brain/graph/query",
        json={"query": "compiled graph ingress", "top_k": 5, "plane_tags": ["imaginal"]},
    )
    assert graph_query.status_code == 200
    assert graph_query.json()["hits"] == []

    admission = client.get("/ops/brain/genesis-memory-admission", params={"session_id": session_id}).json()
    by_route = {decision["ingress_route"]: decision for decision in admission["decisions"]}
    assert by_route["knowledge-artifact-source-ingest"]["memory_write_allowed"] is False
    assert by_route["knowledge-artifact-source-ingest"]["retrieval_truth_allowed"] is False
    assert by_route["knowledge-artifact-source-ingest"]["training_allowed"] is False
    assert by_route["graph-node-ingest"]["memory_write_allowed"] is False
    assert by_route["graph-node-ingest"]["retrieval_truth_allowed"] is False
    assert by_route["graph-node-ingest"]["training_allowed"] is False

    control_panel = client.get(
        "/ops/brain/visualizer/state",
        params={"session_id": session_id},
    ).json()["overlay_state"]["control_panel"]
    assert control_panel["genesis_memory_admission_status"]["decision_count"] >= 2
    assert control_panel["knowledge_artifacts_scorecard"]["latest_artifact"]["artifact_trust_preview"]["status"] == "quarantined"

    serialized = json.dumps(
        {
            "artifact": artifact,
            "query": queried.json(),
            "graph_ingest": graph_payload,
            "graph_query": graph_query.json(),
            "admission": admission,
            "control": {
                "genesis": control_panel["genesis_memory_admission_status"],
                "knowledge": control_panel["knowledge_artifacts_scorecard"],
            },
        },
        sort_keys=True,
    )
    assert private_text not in serialized
    assert "SECRET-LAYER7D" not in serialized
    assert session_id not in serialized

    sanitized_evidence_surfaces = json.dumps(
        {
            "graph_ingest": graph_payload,
            "graph_query": graph_query.json(),
            "admission": admission,
            "control": control_panel["genesis_memory_admission_status"],
        },
        sort_keys=True,
    )
    assert str(project_root) not in sanitized_evidence_surfaces
    assert "F:\\" not in sanitized_evidence_surfaces


def test_genesis_replay_sanitizes_kac_paths_and_context_graph_private_inputs(tmp_path: Path):
    project_root = make_project(tmp_path)
    session_id = "genesis-context-graph-private-session-SECRET"
    private_marker = "SECRET-LAYER7E"
    source_path = project_root / "docs" / "kac-public-source.md"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_text(
        "Public KAC source proves sanitized artifact replay can preserve references without local paths.",
        encoding="utf-8",
    )
    private_corpus = project_root / "private" / private_marker
    client = TestClient(create_app(str(project_root)))

    compiled = client.post(
        "/ops/brain/knowledge-artifacts/compile",
        json={
            "task_family": "genesis_sanitized_replay",
            "source_refs": ["docs/kac-public-source.md"],
            "scope": {"rbac_scope": ["operator"]},
        },
    )
    assert compiled.status_code == 200
    artifact = compiled.json()
    assert "artifact_path" not in artifact
    assert artifact["artifact_storage_ref"].startswith("knowledge/artifacts/")

    detail = client.get(f"/ops/brain/knowledge-artifacts/{artifact['artifact_id']}")
    assert detail.status_code == 200
    assert "artifact_path" not in detail.json()
    assert detail.json()["artifact_storage_ref"] == artifact["artifact_storage_ref"]

    plan = client.post(
        "/ops/brain/context-graph/index-plan",
        json={
            "source": {
                "source_name": f"Private context source {private_marker}",
                "source_url": "https://example.test/context-source",
                "session_id": session_id,
            },
            "corpus_root": str(private_corpus),
            "content_kinds": ["code", "docs"],
            "assistant_platforms": ["codex"],
            "graph_ignore_patterns": [f"private/{private_marker}/**"],
            "changed_files": [str(private_corpus / "operator-note.md")],
            "linked_trace_ids": [session_id],
        },
    )
    assert plan.status_code == 200
    plan_record = plan.json()["record"]
    assert "artifact_path" not in plan_record
    assert plan_record["artifact_storage_ref"].startswith("context-graphs/")
    assert plan_record["corpus"]["root_ref"].startswith("sha256:")
    assert plan_record["corpus"]["root_sanitized"] is True
    assert "changed_file_refs" in plan_record["corpus"]
    assert "changed_files" not in plan_record["corpus"]
    assert all("planned_artifact_ref" in output for output in plan_record["graph_outputs"])
    assert all("planned_path" not in output for output in plan_record["graph_outputs"])

    query = client.post(
        "/ops/brain/context-graph/query",
        json={
            "graph_record_id": plan_record["record_id"],
            "question": f"What does {private_marker} private corpus prove?",
            "mode": "query",
            "linked_trace_ids": [session_id],
        },
    )
    assert query.status_code == 200
    query_record = query.json()["record"]
    assert "artifact_path" not in query_record
    assert "question" not in query_record
    assert query_record["question_ref"].startswith("sha256:")
    assert query_record["artifact_storage_ref"].startswith("context-graphs/queries/")

    context_graph = client.get("/ops/brain/context-graph").json()
    control_panel = client.get(
        "/ops/brain/visualizer/state",
        params={"session_id": session_id},
    ).json()["overlay_state"]["control_panel"]
    product = client.get("/ops/brain/product-sweep/status").json()["status_surfaces"]["context_graph"]

    serialized = json.dumps(
        {
            "artifact": artifact,
            "detail": detail.json(),
            "plan": plan_record,
            "query": query_record,
            "context_graph": context_graph,
            "control_knowledge": control_panel["knowledge_artifacts_scorecard"],
            "product_context_graph": product,
        },
        sort_keys=True,
    )
    assert str(project_root) not in serialized
    assert "F:\\" not in serialized
    assert session_id not in serialized
    assert private_marker not in serialized


def test_context_graph_plan_and_query_are_genesis_admitted_and_projected(tmp_path: Path):
    project_root = make_project(tmp_path)
    session_id = "genesis-context-graph-admission-session-SECRET"
    private_marker = "SECRET-LAYER7F"
    private_question = f"Should {private_marker} become reusable context graph truth?"
    private_corpus = project_root / "private" / private_marker
    client = TestClient(create_app(str(project_root)))

    plan = client.post(
        "/ops/brain/context-graph/index-plan",
        json={
            "session_id": session_id,
            "source": {
                "source_name": f"Private context graph source {private_marker}",
                "source_url": "https://example.test/context-source",
                "source_kind": "manual-operator-ingress",
                "privacy_class": "operator-private",
                "consent_status": "runtime-use-only",
                "rights_license_status": "not-approved-for-training",
            },
            "corpus_root": str(private_corpus),
            "content_kinds": ["code", "docs"],
            "assistant_platforms": ["codex"],
            "changed_files": [str(private_corpus / "operator-note.md")],
            "linked_trace_ids": [session_id],
        },
    )

    assert plan.status_code == 200
    plan_record = plan.json()["record"]
    assert plan_record["status"] == "blocked_by_genesis_memory_admission"
    assert plan_record["execution_allowed"] is False
    assert plan_record["mutation_allowed"] is False
    plan_gate = plan_record["genesis_memory_admission_gate"]
    assert plan_gate["surface_id"] == "genesis-memory-admission-gate"
    assert plan_gate["ingress_route"] == "context-graph-index-plan"
    assert plan_gate["decision_count"] == 1
    assert plan_gate["blocked_count"] == 1
    assert plan_gate["memory_write_allowed"] is False
    assert plan_gate["retrieval_truth_allowed"] is False
    assert plan_gate["training_allowed"] is False
    assert plan_gate["raw_content_included"] is False
    assert plan_record["genesis_memory_admission"]["decision"] == "blocked-private-manual-ingress"
    assert plan_record["genesis_memory_admission"]["raw_content_included"] is False

    query = client.post(
        "/ops/brain/context-graph/query",
        json={
            "session_id": session_id,
            "graph_record_id": plan_record["record_id"],
            "question": private_question,
            "mode": "query",
            "linked_trace_ids": [session_id],
        },
    )

    assert query.status_code == 200
    query_record = query.json()["record"]
    assert query_record["status"] == "blocked_by_genesis_memory_admission"
    assert "question" not in query_record
    query_gate = query_record["genesis_memory_admission_gate"]
    assert query_gate["ingress_route"] == "context-graph-query"
    assert query_gate["blocked_count"] == 1
    assert query_gate["memory_write_allowed"] is False
    assert query_record["genesis_memory_admission"]["decision"] == "blocked-private-manual-ingress"

    admission = client.get("/ops/brain/genesis-memory-admission", params={"session_id": session_id}).json()
    by_route = {decision["ingress_route"]: decision for decision in admission["decisions"]}
    assert by_route["context-graph-index-plan"]["memory_write_allowed"] is False
    assert by_route["context-graph-query"]["memory_write_allowed"] is False

    restarted_client = TestClient(create_app(str(project_root)))
    context_graph = restarted_client.get("/ops/brain/context-graph").json()
    assert context_graph["genesis_memory_admission_gate"]["blocked_count"] >= 2
    assert context_graph["latest_record"]["genesis_memory_admission_gate"]["blocked_count"] == 1

    product = restarted_client.get("/ops/brain/product-sweep/status").json()["status_surfaces"]["context_graph"]
    assert product["genesis_memory_admission_gate"]["blocked_count"] >= 2
    assert product["genesis_memory_admission_gate"]["memory_write_allowed"] is False

    control_panel = restarted_client.get(
        "/ops/brain/visualizer/state",
        params={"session_id": session_id},
    ).json()["overlay_state"]["control_panel"]
    assert control_panel["context_graph_status"]["genesis_memory_admission_gate"]["blocked_count"] >= 2
    assert control_panel["live_refs"]["context_graph_status"] == "/ops/brain/context-graph"

    serialized = json.dumps(
        {
            "plan": plan_record,
            "query": query_record,
            "admission": admission,
            "context_graph": context_graph,
            "product": product,
            "control": control_panel["context_graph_status"],
        },
        sort_keys=True,
    )
    assert private_question not in serialized
    assert private_marker not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized
    assert "F:\\" not in serialized


def test_genesis_memory_replay_joins_live_admission_receipts_without_raw_content(tmp_path: Path):
    project_root = make_project(tmp_path)
    session_id = "genesis-memory-replay-private-session-SECRET"
    private_marker = "SECRET-LAYER7G"
    private_text = f"Private replay intake {private_marker} must stay out of reusable memory truth."
    client = TestClient(create_app(str(project_root)))
    services = client.app.state.services

    services.brain.generate(
        session_context=SessionContext(
            session_id=session_id,
            expert="researcher",
            task_type="genesis-memory-replay",
            use_retrieval=False,
            metadata={"graph_plane_tags": ["memory", "replay", "governance"]},
        ),
        prompt=private_text,
        model_hint="mock/default",
    )
    services.memory.append_messages(session_id, [Message(role="user", content=private_text)])
    services.retrieval.ingest(
        RetrievalIngestRequest(
            documents=[
                RetrievalDocumentInput(
                    source="memory-replay-private-upload",
                    title="Memory replay private upload",
                    text=private_text,
                    metadata={
                        "source_kind": "manual-operator-ingress",
                        "session_id": session_id,
                        "privacy_class": "operator-private",
                        "consent_status": "runtime-use-only",
                        "rights_license_status": "not-approved-for-training",
                    },
                )
            ]
        )
    )
    services.brain_memory_quality.record_claim(
        SourceClaimRequest(
            claim_id="claim::genesis-layer7g-private",
            answer_id="answer::genesis-layer7g",
            claim_text=private_text,
            answerability_status="source_backed",
            source_status="operator_supplied",
            source_refs=["manual-private-source"],
            graph_refs=["graph::operator-private"],
            contains_private_data=True,
            consent_ref="",
            confidence=0.81,
            promotion_state="canon_candidate",
            metadata={
                "session_id": session_id,
                "source_kind": "manual-operator-ingress",
                "privacy_class": "operator-private",
                "consent_status": "runtime-use-only",
                "rights_license_status": "not-approved-for-training",
            },
        )
    )

    compiled = client.post(
        "/ops/brain/knowledge-artifacts/compile",
        json={
            "task_family": "genesis_memory_replay_private_source",
            "scope": {"rbac_scope": ["operator"]},
            "sources": [
                {
                    "source_ref": "manual:memory-replay-private-kac-source",
                    "title": "Memory replay private KAC source",
                    "text": private_text,
                    "permission_state": "allowed",
                    "privacy_class": "operator-private",
                    "license_state": "not-approved-for-training",
                    "rbac_scope": ["operator"],
                    "metadata": {
                        "session_id": session_id,
                        "source_kind": "manual-operator-ingress",
                        "privacy_class": "operator-private",
                        "consent_status": "runtime-use-only",
                        "rights_license_status": "not-approved-for-training",
                    },
                }
            ],
        },
    )
    assert compiled.status_code == 200
    assert compiled.json()["status"] == "blocked"

    graph_ingest = client.post(
        "/ops/brain/graph/ingest",
        json={
            "source": "memory-replay-private-graph",
            "text": private_text,
            "session_id": session_id,
            "plane_hint": "dream",
            "metadata": {
                "doc_id": "memory-replay-private-graph-doc",
                "source_kind": "manual-operator-ingress",
                "privacy_class": "operator-private",
                "consent_status": "runtime-use-only",
                "rights_license_status": "not-approved-for-training",
            },
        },
    )
    assert graph_ingest.status_code == 200
    assert graph_ingest.json()["ingest_blocked"] is True

    plan = client.post(
        "/ops/brain/context-graph/index-plan",
        json={
            "session_id": session_id,
            "source": {
                "source_name": f"Memory replay private context {private_marker}",
                "source_url": "https://example.test/context-source",
                "source_kind": "manual-operator-ingress",
                "privacy_class": "operator-private",
                "consent_status": "runtime-use-only",
                "rights_license_status": "not-approved-for-training",
            },
            "corpus_root": str(project_root / "private" / private_marker),
            "content_kinds": ["code", "docs"],
            "assistant_platforms": ["codex"],
            "changed_files": [str(project_root / "private" / private_marker / "note.md")],
            "linked_trace_ids": [session_id],
        },
    )
    assert plan.status_code == 200
    plan_record = plan.json()["record"]
    query = client.post(
        "/ops/brain/context-graph/query",
        json={
            "session_id": session_id,
            "graph_record_id": plan_record["record_id"],
            "question": f"Can {private_marker} become reusable graph context?",
            "mode": "query",
            "linked_trace_ids": [session_id],
        },
    )
    assert query.status_code == 200

    restarted_client = TestClient(create_app(str(project_root)))
    replay = restarted_client.get("/ops/brain/genesis-memory-replay", params={"session_id": session_id})
    assert replay.status_code == 200
    payload = replay.json()

    assert payload["schema_version"] == "nexusnet-genesis-memory-replay-v1"
    assert payload["surface_id"] == "genesis-memory-replay"
    assert payload["status"] == "live-control-plane"
    assert payload["source"] == "genesis-memory-admission-decisions"
    assert payload["decision_count"] >= 8
    assert payload["blocked_count"] >= 8
    assert payload["allowed_count"] == 0
    assert payload["raw_content_included"] is False
    assert payload["active_production_mutation_allowed"] is False
    assert payload["active_production_mutated"] is False

    expected_routes = {
        "nexusbrain-generate",
        "manual-memory-append",
        "retrieval-document-ingest",
        "source-claim-record",
        "knowledge-artifact-source-ingest",
        "graph-node-ingest",
        "context-graph-index-plan",
        "context-graph-query",
    }
    assert expected_routes <= set(payload["route_counts"])
    assert expected_routes <= {route["route"] for route in payload["route_replay"]}
    assert all(route["raw_content_included"] is False for route in payload["route_replay"])
    assert all(route["blocked_count"] >= 1 for route in payload["route_replay"] if route["route"] in expected_routes)
    assert payload["memory_truth_state"]["memory_write_allowed"] is False
    assert payload["memory_truth_state"]["retrieval_truth_allowed"] is False
    assert payload["memory_truth_state"]["training_allowed"] is False
    assert payload["artifact_ref"] == "genesis/memory-admission/decisions.jsonl"
    assert payload["evidence_refs"][0] == "genesis/memory-admission/decisions.jsonl"

    control_panel = restarted_client.get(
        "/ops/brain/visualizer/state",
        params={"session_id": session_id},
    ).json()["overlay_state"]["control_panel"]
    assert control_panel["genesis_memory_replay_status"]["decision_count"] == payload["decision_count"]
    assert expected_routes <= set(control_panel["genesis_memory_replay_status"]["route_counts"])
    assert control_panel["live_refs"]["genesis_memory_replay_status"] == "/ops/brain/genesis-memory-replay"

    serialized = json.dumps(
        {
            "replay": payload,
            "control": control_panel["genesis_memory_replay_status"],
        },
        sort_keys=True,
    )
    assert private_text not in serialized
    assert private_marker not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized
    assert "F:\\" not in serialized


def test_genesis_memory_replay_promotion_gate_blocks_truth_without_eval_governance(tmp_path: Path):
    project_root = make_project(tmp_path)
    session_id = "genesis-memory-promotion-gate-private-session-SECRET"
    private_marker = "SECRET-LAYER7H"
    private_text = f"Private promotion gate intake {private_marker} must not become promoted truth."
    client = TestClient(create_app(str(project_root)))
    services = client.app.state.services

    services.brain.generate(
        session_context=SessionContext(
            session_id=session_id,
            expert="researcher",
            task_type="genesis-memory-promotion-gate",
            use_retrieval=False,
            metadata={"graph_plane_tags": ["memory", "eval", "governance"]},
        ),
        prompt=private_text,
        model_hint="mock/default",
    )
    services.memory.append_messages(session_id, [Message(role="user", content=private_text)])
    services.retrieval.ingest(
        RetrievalIngestRequest(
            documents=[
                RetrievalDocumentInput(
                    source="memory-promotion-gate-private-upload",
                    title="Memory promotion gate private upload",
                    text=private_text,
                    metadata={
                        "source_kind": "manual-operator-ingress",
                        "session_id": session_id,
                        "privacy_class": "operator-private",
                        "consent_status": "runtime-use-only",
                        "rights_license_status": "not-approved-for-training",
                    },
                )
            ]
        )
    )

    restarted_client = TestClient(create_app(str(project_root)))
    gate = restarted_client.get(
        "/ops/brain/genesis-memory-replay/promotion-gate",
        params={"session_id": session_id},
    )
    assert gate.status_code == 200
    packet = gate.json()

    assert packet["schema_version"] == "nexusnet-genesis-memory-replay-promotion-gate-v1"
    assert packet["surface_id"] == "genesis-memory-replay-promotion-gate"
    assert packet["status"] == "blocked"
    assert packet["promotion_allowed"] is False
    assert packet["source"] == "genesis-memory-replay"
    assert packet["replay_decision_count"] >= 3
    assert packet["blocked_decision_count"] >= 3
    assert packet["raw_content_included"] is False
    assert packet["active_production_mutation_allowed"] is False
    assert packet["active_production_mutated"] is False

    required_controls = {
        "held_out_eval",
        "sandbox_eval",
        "artifact_trust",
        "rollback_plan",
        "governance_approval",
        "admin_approval",
    }
    assert required_controls <= set(packet["required_controls"])
    assert required_controls <= set(packet["missing_controls"])
    assert packet["eval_gate"]["passed"] is False
    assert packet["sandbox_gate"]["passed"] is False
    assert packet["governance_gate"]["passed"] is False
    assert packet["artifact_trust_gate"]["passed"] is False
    assert packet["rollback_gate"]["passed"] is False
    assert packet["promotion_targets"]["memory_truth"]["allowed"] is False
    assert packet["promotion_targets"]["retrieval_truth"]["allowed"] is False
    assert packet["promotion_targets"]["training_material"]["allowed"] is False
    assert packet["promotion_targets"]["graph_truth"]["allowed"] is False
    assert "blocked_private_or_unapproved_decisions_present" in packet["promotion_targets"]["memory_truth"]["blockers"]

    artifact_ref = packet["artifact_ref"]
    assert artifact_ref.startswith("genesis/memory-admission/promotion-gates/")
    artifact_path = services.paths.artifacts_dir / artifact_ref
    assert artifact_path.exists()
    artifact_payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact_payload["gate_id"] == packet["gate_id"]
    assert artifact_payload["raw_content_included"] is False

    control_panel = restarted_client.get(
        "/ops/brain/visualizer/state",
        params={"session_id": session_id},
    ).json()["overlay_state"]["control_panel"]
    assert control_panel["genesis_memory_replay_promotion_gate_status"]["status"] == "blocked"
    assert control_panel["genesis_memory_replay_promotion_gate_status"]["promotion_allowed"] is False
    assert control_panel["live_refs"]["genesis_memory_replay_promotion_gate_status"] == (
        "/ops/brain/genesis-memory-replay/promotion-gate"
    )

    serialized = json.dumps(
        {
            "packet": packet,
            "artifact": artifact_payload,
            "control": control_panel["genesis_memory_replay_promotion_gate_status"],
        },
        sort_keys=True,
    )
    assert private_text not in serialized
    assert private_marker not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized
    assert "F:\\" not in serialized


def test_genesis_memory_replay_promotion_gate_accepts_controls_without_truth_mutation(tmp_path: Path):
    project_root = make_project(tmp_path)
    private_session_id = "genesis-memory-promotion-controlled-private-session-SECRET"
    public_session_id = "genesis-memory-promotion-controlled-public-session"
    private_marker = "SECRET-LAYER7I"
    private_text = f"Private controlled gate intake {private_marker} must remain blocked."
    public_text = "Public controlled gate intake can become eligible after evidence gates."
    client = TestClient(create_app(str(project_root)))
    services = client.app.state.services

    services.memory.append_messages(private_session_id, [Message(role="user", content=private_text)])
    services.retrieval.ingest(
        RetrievalIngestRequest(
            documents=[
                RetrievalDocumentInput(
                    source="memory-promotion-controlled-private-upload",
                    title="Memory promotion controlled private upload",
                    text=private_text,
                    metadata={
                        "source_kind": "manual-operator-ingress",
                        "session_id": private_session_id,
                        "privacy_class": "operator-private",
                        "consent_status": "runtime-use-only",
                        "rights_license_status": "not-approved-for-training",
                    },
                )
            ]
        )
    )
    services.retrieval.ingest(
        RetrievalIngestRequest(
            documents=[
                RetrievalDocumentInput(
                    source="memory-promotion-controlled-public-upload",
                    title="Memory promotion controlled public upload",
                    text=public_text,
                    metadata={
                        "source_kind": "public-doc-corpus",
                        "session_id": public_session_id,
                        "privacy_class": "public",
                        "consent_status": "training-approved",
                        "rights_license_status": "approved-for-training",
                    },
                )
            ]
        )
    )

    controls = {
        "eval_refs": [
            "eval::genesis-memory-replay-held-out",
            "raw-prompt::must-be-sanitized",
        ],
        "sandbox_ref": "sandbox::genesis-memory-replay-closed-run",
        "artifact_trust_refs": ["artifact-trust::genesis-memory-admission-decisions"],
        "rollback_plan": "rollback::genesis-memory-replay-shadow-only",
        "governance_approval_ref": "governance::layer10-memory-promotion-review",
        "admin_approval_ref": "admin::layer10-memory-promotion-review",
    }

    private_gate = client.post(
        "/ops/brain/genesis-memory-replay/promotion-gate",
        json={"session_id": private_session_id, **controls},
    )
    assert private_gate.status_code == 200
    private_packet = private_gate.json()

    assert private_packet["status"] == "blocked"
    assert private_packet["promotion_allowed"] is False
    assert private_packet["missing_controls"] == []
    assert private_packet["eval_gate"]["passed"] is True
    assert private_packet["sandbox_gate"]["passed"] is True
    assert private_packet["artifact_trust_gate"]["passed"] is True
    assert private_packet["rollback_gate"]["passed"] is True
    assert private_packet["governance_gate"]["passed"] is True
    assert private_packet["submitted_control_evidence"]["control_count"] == 6
    assert private_packet["active_production_mutation_allowed"] is False
    assert private_packet["active_production_mutated"] is False
    assert "blocked_private_or_unapproved_decisions_present" in (
        private_packet["promotion_targets"]["memory_truth"]["blockers"]
    )
    assert "raw-prompt::must-be-sanitized" not in private_packet["evidence_refs"]

    public_gate = client.post(
        "/ops/brain/genesis-memory-replay/promotion-gate",
        json={"session_id": public_session_id, **controls},
    )
    assert public_gate.status_code == 200
    public_packet = public_gate.json()

    assert public_packet["status"] == "promotion-allowed"
    assert public_packet["promotion_allowed"] is True
    assert public_packet["missing_controls"] == []
    assert public_packet["blocked_decision_count"] == 0
    assert public_packet["allowed_decision_count"] >= 1
    assert all(target["allowed"] is True for target in public_packet["promotion_targets"].values())
    assert public_packet["active_production_mutation_allowed"] is False
    assert public_packet["active_production_mutated"] is False
    assert public_packet["mutation_boundary"] == (
        "read-only-gate-no-truth-promotion-training-graph-write-or-production-mutation"
    )

    artifact_path = services.paths.artifacts_dir / public_packet["artifact_ref"]
    artifact_payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact_payload["gate_id"] == public_packet["gate_id"]
    assert artifact_payload["submitted_control_evidence"]["control_count"] == 6
    assert artifact_payload["raw_content_included"] is False

    restarted_client = TestClient(create_app(str(project_root)))
    control_panel = restarted_client.get(
        "/ops/brain/visualizer/state",
        params={"session_id": public_session_id},
    ).json()["overlay_state"]["control_panel"]
    control_gate = control_panel["genesis_memory_replay_promotion_gate_status"]
    assert control_gate["gate_id"] == public_packet["gate_id"]
    assert control_gate["status"] == "promotion-allowed"
    assert control_gate["promotion_allowed"] is True
    assert control_gate["submitted_control_evidence"]["control_count"] == 6

    serialized = json.dumps(
        {
            "private_packet": private_packet,
            "public_packet": public_packet,
            "artifact": artifact_payload,
            "control": control_gate,
        },
        sort_keys=True,
    )
    assert private_text not in serialized
    assert public_text not in serialized
    assert private_marker not in serialized
    assert private_session_id not in serialized
    assert public_session_id not in serialized
    assert str(project_root) not in serialized
    assert "F:\\" not in serialized


def test_genesis_memory_replay_promotion_gate_shadow_apply_and_rollback_are_governed(tmp_path: Path):
    project_root = make_project(tmp_path)
    private_session_id = "genesis-memory-apply-private-session-SECRET"
    public_session_id = "genesis-memory-apply-public-session"
    private_marker = "SECRET-LAYER10A"
    private_text = f"Private governed apply intake {private_marker} must never shadow-promote."
    public_text = "Public governed apply intake can create a shadow candidate only."
    admin_identity = "layer10-admin@example.invalid"
    client = TestClient(create_app(str(project_root)))
    services = client.app.state.services

    services.retrieval.ingest(
        RetrievalIngestRequest(
            documents=[
                RetrievalDocumentInput(
                    source="memory-apply-private-upload",
                    title="Memory apply private upload",
                    text=private_text,
                    metadata={
                        "source_kind": "manual-operator-ingress",
                        "session_id": private_session_id,
                        "privacy_class": "operator-private",
                        "consent_status": "runtime-use-only",
                        "rights_license_status": "not-approved-for-training",
                    },
                )
            ]
        )
    )
    services.retrieval.ingest(
        RetrievalIngestRequest(
            documents=[
                RetrievalDocumentInput(
                    source="memory-apply-public-upload",
                    title="Memory apply public upload",
                    text=public_text,
                    metadata={
                        "source_kind": "public-doc-corpus",
                        "session_id": public_session_id,
                        "privacy_class": "public",
                        "consent_status": "training-approved",
                        "rights_license_status": "approved-for-training",
                    },
                )
            ]
        )
    )

    controls = {
        "eval_refs": ["eval::genesis-memory-apply-held-out"],
        "sandbox_ref": "sandbox::genesis-memory-apply-closed-run",
        "artifact_trust_refs": ["artifact-trust::genesis-memory-apply"],
        "rollback_plan": "rollback::genesis-memory-apply-shadow-only",
        "governance_approval_ref": "governance::layer10-memory-apply-review",
        "admin_approval_ref": "admin::layer10-memory-apply-review",
    }
    private_gate = client.post(
        "/ops/brain/genesis-memory-replay/promotion-gate",
        json={"session_id": private_session_id, **controls},
    ).json()
    public_gate = client.post(
        "/ops/brain/genesis-memory-replay/promotion-gate",
        json={"session_id": public_session_id, **controls},
    ).json()

    apply_controls = {
        "eval_result_refs": ["eval-result::genesis-memory-apply-regression-pass"],
        "sandbox_eval_ref": "sandbox-eval::genesis-memory-apply-closed-pass",
        "artifact_trust_ref": "artifact-trust::genesis-memory-apply-candidate",
        "rollback_proof_ref": "rollback-proof::genesis-memory-apply-candidate",
        "admin_decision_ref": "admin-decision::genesis-memory-apply-shadow-candidate",
        "approved_by": admin_identity,
    }
    private_apply = client.post(
        "/ops/brain/genesis-memory-replay/promotion-gate/apply",
        json={"gate_id": private_gate["gate_id"], **apply_controls},
    )
    assert private_apply.status_code == 200
    private_apply_packet = private_apply.json()
    assert private_apply_packet["status"] == "blocked"
    assert private_apply_packet["apply_allowed"] is False
    assert private_apply_packet["gate_promotion_allowed"] is False
    assert private_apply_packet["shadow_candidate_written"] is False
    assert private_apply_packet["active_production_mutation_allowed"] is False
    assert private_apply_packet["active_production_mutated"] is False
    assert "promotion_gate_not_allowed" in private_apply_packet["blockers"]

    public_sandbox_eval = client.post(
        "/ops/brain/genesis-memory-replay/promotion-gate/sandbox-eval",
        json={
            "gate_id": public_gate["gate_id"],
            "eval_cases": [
                {
                    "case_id": "memory-apply-shadow-positive",
                    "target": "memory_truth",
                    "expected_allowed": True,
                }
            ],
            "artifact_trust_ref": "artifact-trust::genesis-memory-apply-sandbox",
            "rollback_proof_ref": "rollback-proof::genesis-memory-apply-sandbox",
        },
    ).json()
    assert public_sandbox_eval["status"] == "passed"

    public_apply = client.post(
        "/ops/brain/genesis-memory-replay/promotion-gate/apply",
        json={
            "gate_id": public_gate["gate_id"],
            "sandbox_eval_run_id": public_sandbox_eval["eval_run_id"],
            **apply_controls,
        },
    )
    assert public_apply.status_code == 200
    public_apply_packet = public_apply.json()
    assert public_apply_packet["status"] == "shadow-candidate-written"
    assert public_apply_packet["apply_allowed"] is True
    assert public_apply_packet["gate_promotion_allowed"] is True
    assert public_apply_packet["shadow_candidate_written"] is True
    assert public_apply_packet["shadow_candidate_ref"].startswith(
        "genesis/memory-admission/promotion-candidates/"
    )
    assert public_apply_packet["sandbox_eval"]["eval_run_id"] == public_sandbox_eval["eval_run_id"]
    assert public_apply_packet["admin_decision_packet"]["decision"] == "admin-approved-shadow-only"
    assert public_apply_packet["admin_decision_packet"]["admin_actor_digest"].startswith("sha256:")
    assert public_apply_packet["rollback_proof"]["rollback_available"] is True
    assert public_apply_packet["active_production_mutation_allowed"] is False
    assert public_apply_packet["active_production_mutated"] is False

    candidate_path = services.paths.artifacts_dir / public_apply_packet["shadow_candidate_ref"]
    candidate_payload = json.loads(candidate_path.read_text(encoding="utf-8"))
    assert candidate_payload["status"] == "shadow-candidate"
    assert candidate_payload["application_id"] == public_apply_packet["application_id"]
    assert candidate_payload["raw_content_included"] is False
    assert candidate_payload["active_production_mutated"] is False

    rollback = client.post(
        "/ops/brain/genesis-memory-replay/promotion-gate/rollback",
        json={
            "application_id": public_apply_packet["application_id"],
            "reason": "operator requested rollback SECRET-ROLLBACK-REDACT",
        },
    )
    assert rollback.status_code == 200
    rollback_packet = rollback.json()
    assert rollback_packet["status"] == "rollback-recorded"
    assert rollback_packet["rollback_state"] == "shadow-candidate-reverted"
    assert rollback_packet["shadow_candidate_retained_for_audit"] is True
    assert rollback_packet["active_production_mutation_allowed"] is False
    assert rollback_packet["active_production_mutated"] is False

    restarted_client = TestClient(create_app(str(project_root)))
    control_panel = restarted_client.get(
        "/ops/brain/visualizer/state",
        params={"session_id": public_session_id},
    ).json()["overlay_state"]["control_panel"]
    control_gate = control_panel["genesis_memory_replay_promotion_gate_status"]
    assert control_gate["gate_id"] == public_gate["gate_id"]
    assert control_gate["latest_governed_application"]["application_id"] == public_apply_packet["application_id"]
    assert control_gate["latest_governed_application"]["status"] == "shadow-candidate-written"
    assert control_gate["latest_rollback_record"]["rollback_id"] == rollback_packet["rollback_id"]
    assert control_gate["latest_rollback_record"]["status"] == "rollback-recorded"

    serialized = json.dumps(
        {
            "private_apply": private_apply_packet,
            "public_apply": public_apply_packet,
            "candidate": candidate_payload,
            "rollback": rollback_packet,
            "control": control_gate,
        },
        sort_keys=True,
    )
    assert private_text not in serialized
    assert public_text not in serialized
    assert private_marker not in serialized
    assert "SECRET-ROLLBACK-REDACT" not in serialized
    assert private_session_id not in serialized
    assert public_session_id not in serialized
    assert admin_identity not in serialized
    assert str(project_root) not in serialized
    assert "F:\\" not in serialized


def test_genesis_memory_replay_promotion_apply_requires_closed_sandbox_eval_receipt(tmp_path: Path):
    project_root = make_project(tmp_path)
    session_id = "genesis-memory-sandbox-eval-public-session"
    public_text = "Public sandbox eval intake can become a shadow candidate after closed eval."
    admin_identity = "layer10-sandbox-admin@example.invalid"
    client = TestClient(create_app(str(project_root)))
    services = client.app.state.services

    services.retrieval.ingest(
        RetrievalIngestRequest(
            documents=[
                RetrievalDocumentInput(
                    source="memory-sandbox-eval-public-upload",
                    title="Memory sandbox eval public upload",
                    text=public_text,
                    metadata={
                        "source_kind": "public-doc-corpus",
                        "session_id": session_id,
                        "privacy_class": "public",
                        "consent_status": "training-approved",
                        "rights_license_status": "approved-for-training",
                    },
                )
            ]
        )
    )

    gate = client.post(
        "/ops/brain/genesis-memory-replay/promotion-gate",
        json={
            "session_id": session_id,
            "eval_refs": ["eval::genesis-memory-sandbox-eval-held-out"],
            "sandbox_ref": "sandbox::genesis-memory-sandbox-eval-closed-run",
            "artifact_trust_refs": ["artifact-trust::genesis-memory-sandbox-eval"],
            "rollback_plan": "rollback::genesis-memory-sandbox-eval-shadow-only",
            "governance_approval_ref": "governance::layer10-memory-sandbox-eval-review",
            "admin_approval_ref": "admin::layer10-memory-sandbox-eval-review",
        },
    ).json()
    assert gate["promotion_allowed"] is True

    apply_controls = {
        "artifact_trust_ref": "artifact-trust::genesis-memory-sandbox-eval-candidate",
        "rollback_proof_ref": "rollback-proof::genesis-memory-sandbox-eval-candidate",
        "admin_decision_ref": "admin-decision::genesis-memory-sandbox-eval-shadow-candidate",
        "approved_by": admin_identity,
    }
    missing_eval_apply = client.post(
        "/ops/brain/genesis-memory-replay/promotion-gate/apply",
        json={"gate_id": gate["gate_id"], **apply_controls},
    ).json()
    assert missing_eval_apply["status"] == "blocked"
    assert missing_eval_apply["apply_allowed"] is False
    assert missing_eval_apply["shadow_candidate_written"] is False
    assert "closed_sandbox_eval_receipt_required" in missing_eval_apply["blockers"]

    failing_eval = client.post(
        "/ops/brain/genesis-memory-replay/promotion-gate/sandbox-eval",
        json={
            "gate_id": gate["gate_id"],
            "eval_cases": [
                {
                    "case_id": "promotion-allowed-negative-control",
                    "target": "memory_truth",
                    "expected_allowed": False,
                }
            ],
            "artifact_trust_ref": "artifact-trust::genesis-memory-sandbox-eval-failing",
            "rollback_proof_ref": "rollback-proof::genesis-memory-sandbox-eval-failing",
        },
    )
    assert failing_eval.status_code == 200
    failing_eval_packet = failing_eval.json()
    assert failing_eval_packet["status"] == "failed"
    assert failing_eval_packet["passed"] is False
    assert failing_eval_packet["failed_count"] == 1
    assert failing_eval_packet["raw_content_included"] is False

    failed_eval_apply = client.post(
        "/ops/brain/genesis-memory-replay/promotion-gate/apply",
        json={
            "gate_id": gate["gate_id"],
            "sandbox_eval_run_id": failing_eval_packet["eval_run_id"],
            **apply_controls,
        },
    ).json()
    assert failed_eval_apply["status"] == "blocked"
    assert failed_eval_apply["apply_allowed"] is False
    assert "sandbox_eval_passed_required" in failed_eval_apply["blockers"]

    passing_eval = client.post(
        "/ops/brain/genesis-memory-replay/promotion-gate/sandbox-eval",
        json={
            "gate_id": gate["gate_id"],
            "eval_cases": [
                {
                    "case_id": "memory-truth-promotion-positive",
                    "target": "memory_truth",
                    "expected_allowed": True,
                },
                {
                    "case_id": "training-material-promotion-positive",
                    "target": "training_material",
                    "expected_allowed": True,
                },
            ],
            "artifact_trust_ref": "artifact-trust::genesis-memory-sandbox-eval-passing",
            "rollback_proof_ref": "rollback-proof::genesis-memory-sandbox-eval-passing",
        },
    )
    assert passing_eval.status_code == 200
    passing_eval_packet = passing_eval.json()
    assert passing_eval_packet["status"] == "passed"
    assert passing_eval_packet["passed"] is True
    assert passing_eval_packet["case_count"] == 2
    assert passing_eval_packet["failed_count"] == 0
    assert passing_eval_packet["sandbox_tier"] == "closed-deterministic"
    assert passing_eval_packet["artifact_ref"].startswith(
        "genesis/memory-admission/promotion-sandbox-evals/"
    )
    eval_artifact = json.loads((services.paths.artifacts_dir / passing_eval_packet["artifact_ref"]).read_text(encoding="utf-8"))
    assert eval_artifact["eval_run_id"] == passing_eval_packet["eval_run_id"]
    assert eval_artifact["raw_content_included"] is False

    applied = client.post(
        "/ops/brain/genesis-memory-replay/promotion-gate/apply",
        json={
            "gate_id": gate["gate_id"],
            "sandbox_eval_run_id": passing_eval_packet["eval_run_id"],
            **apply_controls,
        },
    ).json()
    assert applied["status"] == "shadow-candidate-written"
    assert applied["apply_allowed"] is True
    assert applied["sandbox_eval"]["eval_run_id"] == passing_eval_packet["eval_run_id"]
    assert applied["sandbox_eval"]["passed"] is True
    assert applied["sandbox_eval"]["artifact_ref"] == passing_eval_packet["artifact_ref"]
    assert applied["shadow_candidate_written"] is True
    assert applied["active_production_mutation_allowed"] is False
    assert applied["active_production_mutated"] is False

    restarted_client = TestClient(create_app(str(project_root)))
    control_gate = restarted_client.get(
        "/ops/brain/visualizer/state",
        params={"session_id": session_id},
    ).json()["overlay_state"]["control_panel"]["genesis_memory_replay_promotion_gate_status"]
    assert control_gate["latest_sandbox_eval_run"]["eval_run_id"] == passing_eval_packet["eval_run_id"]
    assert control_gate["latest_sandbox_eval_run"]["status"] == "passed"
    assert control_gate["latest_governed_application"]["application_id"] == applied["application_id"]
    assert control_gate["latest_governed_application"]["sandbox_eval"]["eval_run_id"] == passing_eval_packet["eval_run_id"]

    serialized = json.dumps(
        {
            "missing_eval_apply": missing_eval_apply,
            "failing_eval": failing_eval_packet,
            "failed_eval_apply": failed_eval_apply,
            "passing_eval": passing_eval_packet,
            "eval_artifact": eval_artifact,
            "applied": applied,
            "control": control_gate,
        },
        sort_keys=True,
    )
    assert public_text not in serialized
    assert session_id not in serialized
    assert admin_identity not in serialized
    assert str(project_root) not in serialized
    assert "F:\\" not in serialized


def test_genesis_memory_foundation_commits_public_source_and_rolls_back_retrieval_truth(tmp_path: Path):
    project_root = make_project(tmp_path)
    session_id = "genesis-layer7-public-memory-session"
    public_text = "The governed Layer 7 source states that cedar calibration uses seven checkpoints."
    substituted_text = "SECRET substituted private content must not enter canonical memory."
    admin_identity = "layer7-memory-admin@example.invalid"
    client = TestClient(create_app(str(project_root)))
    services = client.app.state.services
    baseline_growth = client.app.state.global_growth.growth_status()
    baseline_active_growth = baseline_growth["active_global_captures"]
    assert baseline_growth["global_sources_per_node"].get("expert.memory", 0) == 0

    doc_ids = services.retrieval.ingest(
        RetrievalIngestRequest(
            documents=[
                RetrievalDocumentInput(
                    source="canon-source::cedar-calibration",
                    title="Cedar calibration source",
                    text=public_text,
                    metadata={
                        "source_kind": "public-doc-corpus",
                        "session_id": session_id,
                        "privacy_class": "public",
                        "consent_status": "training-approved",
                        "rights_license_status": "approved-for-training",
                    },
                )
            ]
        )
    )
    assert len(doc_ids) == 1
    assert doc_ids[0].startswith("genesis-retrieval-candidate::")
    precommit_policy = services.retrieval.query_with_policy(
        RetrievalRequest(query="cedar checkpoints", session_id=session_id, top_k=10)
    )
    assert precommit_policy["hits"] == []
    assert precommit_policy["candidate_source_counts"]["lexical"] == 0
    assert precommit_policy["candidate_source_counts"]["memory"] == 0
    assert precommit_policy["candidate_source_counts"]["graph"] == 0
    assert services.brain_graph_retriever.query(query="cedar checkpoints", top_k=10) == []
    precommit_growth = client.app.state.global_growth.growth_status()
    assert precommit_growth["active_global_captures"] == baseline_active_growth
    assert precommit_growth["global_sources_per_node"].get("expert.memory", 0) == 0

    admission = client.get(
        "/ops/brain/genesis-memory-admission",
        params={"session_id": session_id},
    ).json()
    decision = admission["decisions"][0]
    assert decision["memory_write_allowed"] is True
    assert decision["retrieval_truth_allowed"] is True
    assert decision["source_ref"] == "canon-source::cedar-calibration"

    gate = client.post(
        "/ops/brain/genesis-memory-replay/promotion-gate",
        json={
            "session_id": session_id,
            "eval_refs": ["eval::layer7-memory-held-out"],
            "sandbox_ref": "sandbox::layer7-memory-closed",
            "artifact_trust_refs": ["artifact-trust::layer7-memory-source"],
            "rollback_plan": "rollback::layer7-memory-canonical-record",
            "governance_approval_ref": "governance::layer7-memory-review",
            "admin_approval_ref": "admin::layer7-memory-review",
        },
    ).json()
    assert gate["promotion_allowed"] is True
    assert gate["source_bindings"][0]["decision_id"] == decision["decision_id"]
    assert gate["source_bindings"][0]["content_ref"] == decision["content_ref"]

    sandbox_eval = client.post(
        "/ops/brain/genesis-memory-replay/promotion-gate/sandbox-eval",
        json={
            "gate_id": gate["gate_id"],
            "eval_cases": [
                {"case_id": "layer7-memory-truth", "target": "memory_truth", "expected_allowed": True},
                {"case_id": "layer7-retrieval-truth", "target": "retrieval_truth", "expected_allowed": True},
                {"case_id": "layer7-graph-truth", "target": "graph_truth", "expected_allowed": True},
            ],
            "artifact_trust_ref": "artifact-trust::layer7-memory-sandbox",
            "rollback_proof_ref": "rollback-proof::layer7-memory-sandbox",
        },
    ).json()
    assert sandbox_eval["passed"] is True

    application = client.post(
        "/ops/brain/genesis-memory-replay/promotion-gate/apply",
        json={
            "gate_id": gate["gate_id"],
            "sandbox_eval_run_id": sandbox_eval["eval_run_id"],
            "artifact_trust_ref": "artifact-trust::layer7-memory-candidate",
            "rollback_proof_ref": "rollback-proof::layer7-memory-candidate",
            "admin_decision_ref": "admin-decision::layer7-memory-shadow",
            "approved_by": admin_identity,
        },
    ).json()
    assert application["status"] == "shadow-candidate-written"

    substituted = client.post(
        "/ops/brain/genesis-memory-replay/promotion-gate/commit",
        json={
            "application_id": application["application_id"],
            "source_content_by_decision_id": {decision["decision_id"]: substituted_text},
            "governance_commit_ref": "governance::layer7-memory-commit",
            "admin_commit_ref": "admin::layer7-memory-commit",
            "approved_by": admin_identity,
        },
    )
    assert substituted.status_code == 400
    assert "content digest does not match admitted source" in substituted.json()["detail"]

    committed = client.post(
        "/ops/brain/genesis-memory-replay/promotion-gate/commit",
        json={
            "application_id": application["application_id"],
            "source_content_by_decision_id": {decision["decision_id"]: public_text},
            "governance_commit_ref": "governance::layer7-memory-commit",
            "admin_commit_ref": "admin::layer7-memory-commit",
            "approved_by": admin_identity,
        },
    )
    assert committed.status_code == 200
    commit = committed.json()
    assert commit["status"] == "canonical-memory-committed"
    assert commit["active_production_mutation_allowed"] is True
    assert commit["active_production_mutated"] is True
    assert commit["memory_record_count"] == 1
    assert commit["retrieval_packet_count"] == 1
    assert commit["graph_node_count"] >= 3
    assert commit["graph_edge_count"] >= 2
    assert commit["per_user_growth_state"]["active_memory_count"] == 1
    assert commit["global_growth_state"]["active_memory_count"] == 1
    assert commit["memory_evolution_passport_ref"].startswith("genesis/memory-foundation/passports/")
    assert commit["raw_content_included"] is False
    runtime_activation = commit["runtime_activation"]
    assert runtime_activation["status"] == "activated"
    assert runtime_activation["lexical_retrieval"]["status"] == "active"
    assert runtime_activation["semantic_memory"]["status"] == "active"
    assert runtime_activation["live_graphrag"]["status"] == "active"
    assert runtime_activation["global_growth"]["status"] == "active"

    postcommit_policy = services.retrieval.query_with_policy(
        RetrievalRequest(query="cedar checkpoints", session_id=session_id, top_k=10)
    )
    assert postcommit_policy["candidate_source_counts"]["lexical"] >= 1
    assert postcommit_policy["candidate_source_counts"]["memory"] >= 1
    assert postcommit_policy["candidate_source_counts"]["graph"] >= 1
    assert postcommit_policy["hits"]
    assert services.brain_graph_retriever.query(query="cedar checkpoints", top_k=10)
    live_growth = client.app.state.global_growth.growth_status()
    assert live_growth["active_global_captures"] == baseline_active_growth + 1
    assert live_growth["global_sources_per_node"]["expert.memory"] == 1
    assert live_growth["latest_runtime_receipt"]["receipt_id"] == (
        runtime_activation["global_growth"]["receipts"][0]["receipt_id"]
    )
    assert live_growth["latest_runtime_receipt"]["knowledge_ref"].startswith("ref-digest::")

    query = client.get(
        "/ops/brain/genesis-memory-foundation/query",
        params={"query": "cedar checkpoints", "session_id": session_id},
    )
    assert query.status_code == 200
    query_payload = query.json()
    assert query_payload["hit_count"] == 1
    hit = query_payload["hits"][0]
    assert hit["content"] == public_text
    assert hit["content_ref"] == decision["content_ref"]
    assert hit["source_ref"] == "canon-source::cedar-calibration"
    assert hit["retrieval_packet_ref"].startswith("genesis/memory-foundation/retrieval/")
    assert hit["graph_refs"]
    assert hit["contradiction_state"] == "not-observed"
    assert hit["stale_state"] == "current"
    assert hit["raw_source_fallback"]["allowed"] is True

    restarted_client = TestClient(create_app(str(project_root)))
    replayed = restarted_client.get(
        "/ops/brain/genesis-memory-foundation/query",
        params={"query": "cedar checkpoints", "session_id": session_id},
    ).json()
    assert replayed["hit_count"] == 1
    assert replayed["hits"][0]["memory_id"] == hit["memory_id"]
    restarted_services = restarted_client.app.state.services
    restarted_policy = restarted_services.retrieval.query_with_policy(
        RetrievalRequest(query="cedar checkpoints", session_id=session_id, top_k=10)
    )
    assert restarted_policy["candidate_source_counts"]["lexical"] >= 1
    assert restarted_policy["candidate_source_counts"]["memory"] >= 1
    assert restarted_policy["candidate_source_counts"]["graph"] >= 1
    restarted_growth = restarted_client.app.state.global_growth.growth_status()
    assert restarted_growth["global_sources_per_node"]["expert.memory"] == 1

    control_panel = restarted_client.get(
        "/ops/brain/visualizer/state",
        params={"session_id": session_id},
    ).json()["overlay_state"]["control_panel"]
    foundation_status = control_panel["genesis_memory_foundation_status"]
    assert foundation_status["honest_status_label"] == "genesis-layer7-memory-foundation-live"
    assert foundation_status["active_memory_count"] == 1
    assert foundation_status["latest_commit"]["commit_id"] == commit["commit_id"]

    rollback = restarted_client.post(
        "/ops/brain/genesis-memory-replay/promotion-gate/rollback",
        json={
            "application_id": application["application_id"],
            "reason": "operator withdrew canonical source SECRET-ROLLBACK-DETAIL",
        },
    )
    assert rollback.status_code == 200
    rollback_packet = rollback.json()
    assert rollback_packet["rollback_state"] == "canonical-memory-reverted"
    assert rollback_packet["active_production_mutation_allowed"] is True
    assert rollback_packet["active_production_mutated"] is True
    assert rollback_packet["reverted_memory_count"] == 1
    runtime_deactivation = rollback_packet["runtime_deactivation"]
    assert runtime_deactivation["status"] == "passivated"
    assert runtime_deactivation["lexical_retrieval"]["status"] == "revoked"
    assert runtime_deactivation["semantic_memory"]["status"] == "revoked"
    assert runtime_deactivation["live_graphrag"]["status"] == "revoked"
    assert runtime_deactivation["global_growth"]["status"] == "passivated"

    after_rollback = TestClient(create_app(str(project_root)))
    empty_query = after_rollback.get(
        "/ops/brain/genesis-memory-foundation/query",
        params={"query": "cedar checkpoints", "session_id": session_id},
    ).json()
    assert empty_query["hit_count"] == 0
    after_services = after_rollback.app.state.services
    revoked_policy = after_services.retrieval.query_with_policy(
        RetrievalRequest(query="cedar checkpoints", session_id=session_id, top_k=10)
    )
    assert revoked_policy["hits"] == []
    assert revoked_policy["candidate_source_counts"]["lexical"] == 0
    assert revoked_policy["candidate_source_counts"]["memory"] == 0
    assert revoked_policy["candidate_source_counts"]["graph"] == 0
    revoked_memory_view = after_services.memory.session_view(admission["session_ref_digest"])
    assert revoked_memory_view["planes"]["semantic"] == []
    assert revoked_memory_view["analytics"]["total_records"] == 0
    revoked_growth = after_rollback.app.state.global_growth.growth_status()
    assert revoked_growth["global_sources_per_node"].get("expert.memory", 0) == 0
    assert revoked_growth["passivated_global_captures"] >= 1
    summary = after_rollback.get("/ops/brain/genesis-memory-foundation").json()
    assert summary["active_memory_count"] == 0
    assert summary["revoked_memory_count"] == 1
    assert summary["latest_rollback"]["rollback_id"] == rollback_packet["rollback_id"]
    global_index = json.loads(
        (
            services.paths.artifacts_dir
            / "genesis"
            / "memory-foundation"
            / "indexes"
            / "global.json"
        ).read_text(encoding="utf-8")
    )
    assert global_index["active_memory_count"] == 0
    user_indexes = list(
        (
            services.paths.artifacts_dir
            / "genesis"
            / "memory-foundation"
            / "indexes"
            / "users"
        ).glob("*.json")
    )
    assert len(user_indexes) == 1
    assert json.loads(user_indexes[0].read_text(encoding="utf-8"))["active_memory_count"] == 0

    sanitized = json.dumps(
        {
            "commit": commit,
            "foundation_status": foundation_status,
            "rollback": rollback_packet,
            "summary": summary,
        },
        sort_keys=True,
    )
    assert public_text not in sanitized
    assert substituted_text not in sanitized
    assert "SECRET-ROLLBACK-DETAIL" not in sanitized
    assert session_id not in sanitized
    assert admin_identity not in sanitized
    assert str(project_root) not in sanitized
    assert "F:\\" not in sanitized


def test_genesis_memory_source_evolution_passivates_and_requires_fresh_governed_recommit(tmp_path: Path):
    project_root = make_project(tmp_path)
    session_id = "genesis-layer7-memory-evolution-session"
    original_text = "The cedar calibration canon requires seven checkpoints before activation."
    refreshed_text = "The cedar calibration canon now requires nine checkpoints before activation."
    admin_identity = "memory-evolution-admin@example.invalid"
    client = TestClient(create_app(str(project_root)))
    services = client.app.state.services

    decision, initial_commit = _commit_public_genesis_memory(
        client,
        session_id=session_id,
        source_ref="canon-source::cedar-calibration-evolution",
        content=original_text,
        admin_identity=admin_identity,
        control_suffix="initial",
    )
    initial_hit = client.get(
        "/ops/brain/genesis-memory-foundation/query",
        params={"query": "seven checkpoints", "session_id": session_id},
    ).json()["hits"][0]
    memory_id = initial_hit["memory_id"]

    unchanged = client.post(
        "/ops/brain/genesis-memory-foundation/refresh",
        json={
            "memory_id": memory_id,
            "session_id": session_id,
            "refreshed_content": original_text,
            "source_refresh_ref": "source-refresh::cedar-unchanged",
        },
    )
    assert unchanged.status_code == 200
    unchanged_packet = unchanged.json()
    assert unchanged_packet["status"] == "verified-current"
    assert unchanged_packet["content_changed"] is False
    assert unchanged_packet["active_production_mutated"] is False
    assert unchanged_packet["recommit_required"] is False
    assert client.get(
        "/ops/brain/genesis-memory-foundation/query",
        params={"query": "seven checkpoints", "session_id": session_id},
    ).json()["hit_count"] == 1

    evolved = client.post(
        "/ops/brain/genesis-memory-foundation/refresh",
        json={
            "memory_id": memory_id,
            "session_id": session_id,
            "refreshed_content": refreshed_text,
            "source_refresh_ref": "source-refresh::cedar-contradiction",
            "classification": "contradictory",
            "contradiction_refs": ["contradiction-eval::cedar-checkpoint-count"],
        },
    )
    assert evolved.status_code == 200
    evolution = evolved.json()
    assert evolution["status"] == "contradiction-passivated"
    assert evolution["content_changed"] is True
    assert evolution["stale_state"] == "source-changed"
    assert evolution["contradiction_state"] == "confirmed"
    assert evolution["previous_content_ref"] == decision["content_ref"]
    assert evolution["refreshed_content_ref"] != decision["content_ref"]
    assert evolution["current_memory_state"] == "contradicted"
    assert evolution["recommit_required"] is True
    assert evolution["required_controls"] == [
        "held_out_eval",
        "closed_sandbox_eval",
        "artifact_trust",
        "rollback_proof",
        "governance_approval",
        "admin_approval",
    ]
    assert evolution["candidate_decision_ref"].startswith("genesis-memory-admission::")
    assert evolution["runtime_deactivation"]["lexical_retrieval"]["status"] == "revoked"
    assert evolution["runtime_deactivation"]["semantic_memory"]["status"] == "revoked"
    assert evolution["runtime_deactivation"]["live_graphrag"]["status"] == "revoked"
    assert evolution["runtime_deactivation"]["global_growth"]["status"] == "passivated"
    assert evolution["active_production_mutated"] is True

    passivated_query = client.get(
        "/ops/brain/genesis-memory-foundation/query",
        params={"query": "cedar checkpoints", "session_id": session_id},
    ).json()
    assert passivated_query["hit_count"] == 0
    passivated_policy = services.retrieval.query_with_policy(
        RetrievalRequest(query="cedar checkpoints", session_id=session_id, top_k=10)
    )
    assert passivated_policy["candidate_source_counts"]["lexical"] == 0
    assert passivated_policy["candidate_source_counts"]["memory"] == 0
    assert passivated_policy["candidate_source_counts"]["graph"] == 0
    assert services.brain_graph_retriever.query(query="cedar checkpoints", top_k=10) == []
    assert client.app.state.global_growth.growth_status()["global_sources_per_node"].get(
        "expert.memory", 0
    ) == 0

    degraded = client.get(
        "/ops/brain/genesis-memory-foundation",
        params={"session_id": session_id},
    ).json()
    assert degraded["status"] == "degraded-contradicted"
    assert degraded["active_memory_count"] == 0
    assert degraded["contradicted_memory_count"] == 1
    assert degraded["evolution_count"] == 2
    assert degraded["latest_evolution"]["evolution_id"] == evolution["evolution_id"]
    assert degraded["latest_evolution"]["candidate_decision_ref"] == evolution["candidate_decision_ref"]

    selected_gate = client.post(
        "/ops/brain/genesis-memory-replay/promotion-gate",
        json={
            "session_id": session_id,
            "decision_refs": [evolution["candidate_decision_ref"]],
            "eval_refs": ["eval::cedar-evolution-held-out"],
            "sandbox_ref": "sandbox::cedar-evolution-closed",
            "artifact_trust_refs": ["artifact-trust::cedar-evolution-source"],
            "rollback_plan": "rollback::cedar-evolution-memory",
            "governance_approval_ref": "governance::cedar-evolution-review",
            "admin_approval_ref": "admin::cedar-evolution-review",
        },
    )
    assert selected_gate.status_code == 200
    gate = selected_gate.json()
    assert gate["promotion_allowed"] is True
    assert gate["decision_refs"] == [evolution["candidate_decision_ref"]]
    assert gate["replay_decision_count"] == 1

    sandbox_eval = client.post(
        "/ops/brain/genesis-memory-replay/promotion-gate/sandbox-eval",
        json={
            "gate_id": gate["gate_id"],
            "eval_cases": [
                {"case_id": "evolved-memory-truth", "target": "memory_truth", "expected_allowed": True},
                {"case_id": "evolved-retrieval-truth", "target": "retrieval_truth", "expected_allowed": True},
                {"case_id": "evolved-graph-truth", "target": "graph_truth", "expected_allowed": True},
            ],
            "artifact_trust_ref": "artifact-trust::cedar-evolution-sandbox",
            "rollback_proof_ref": "rollback-proof::cedar-evolution-sandbox",
        },
    ).json()
    assert sandbox_eval["passed"] is True
    application = client.post(
        "/ops/brain/genesis-memory-replay/promotion-gate/apply",
        json={
            "gate_id": gate["gate_id"],
            "sandbox_eval_run_id": sandbox_eval["eval_run_id"],
            "artifact_trust_ref": "artifact-trust::cedar-evolution-candidate",
            "rollback_proof_ref": "rollback-proof::cedar-evolution-candidate",
            "admin_decision_ref": "admin-decision::cedar-evolution-shadow",
            "approved_by": admin_identity,
        },
    ).json()
    recommitted = client.post(
        "/ops/brain/genesis-memory-replay/promotion-gate/commit",
        json={
            "application_id": application["application_id"],
            "source_content_by_decision_id": {
                evolution["candidate_decision_ref"]: refreshed_text,
            },
            "governance_commit_ref": "governance::cedar-evolution-commit",
            "admin_commit_ref": "admin::cedar-evolution-commit",
            "approved_by": admin_identity,
        },
    )
    assert recommitted.status_code == 200
    recommit = recommitted.json()
    assert recommit["commit_id"] != initial_commit["commit_id"]
    assert recommit["memory_record_count"] == 1

    restarted = TestClient(create_app(str(project_root)))
    current_query = restarted.get(
        "/ops/brain/genesis-memory-foundation/query",
        params={"query": "nine checkpoints", "session_id": session_id},
    ).json()
    assert current_query["hit_count"] == 1
    assert current_query["hits"][0]["content"] == refreshed_text
    assert restarted.get(
        "/ops/brain/genesis-memory-foundation/query",
        params={"query": "seven", "session_id": session_id},
    ).json()["hit_count"] == 0
    restarted_growth = restarted.app.state.global_growth.growth_status()
    assert restarted_growth["global_sources_per_node"]["expert.memory"] == 1
    control = restarted.get(
        "/ops/brain/visualizer/state",
        params={"session_id": session_id},
    ).json()["overlay_state"]["control_panel"]["genesis_memory_foundation_status"]
    assert control["status"] == "live-with-memory-evolution"
    assert control["honest_status_label"] == "genesis-layer7-memory-foundation-live-with-memory-evolution"
    assert control["active_memory_count"] == 1
    assert control["contradicted_memory_count"] == 1
    assert control["latest_evolution"]["evolution_id"] == evolution["evolution_id"]

    sanitized = json.dumps(
        {
            "unchanged": unchanged_packet,
            "evolution": evolution,
            "degraded": degraded,
            "gate": gate,
            "recommit": recommit,
            "control": control,
        },
        sort_keys=True,
    )
    assert original_text not in sanitized
    assert refreshed_text not in sanitized
    assert session_id not in sanitized
    assert admin_identity not in sanitized
    assert str(project_root) not in sanitized
    assert "F:\\" not in sanitized


def _commit_public_genesis_memory(
    client: TestClient,
    *,
    session_id: str,
    source_ref: str,
    content: str,
    admin_identity: str,
    control_suffix: str,
) -> tuple[dict[str, object], dict[str, object]]:
    services = client.app.state.services
    services.retrieval.ingest(
        RetrievalIngestRequest(
            documents=[
                RetrievalDocumentInput(
                    source=source_ref,
                    title="Governed memory evolution source",
                    text=content,
                    metadata={
                        "source_kind": "public-doc-corpus",
                        "session_id": session_id,
                        "privacy_class": "public",
                        "consent_status": "training-approved",
                        "rights_license_status": "approved-for-training",
                    },
                )
            ]
        )
    )
    decision = client.get(
        "/ops/brain/genesis-memory-admission",
        params={"session_id": session_id},
    ).json()["decisions"][0]
    gate = client.post(
        "/ops/brain/genesis-memory-replay/promotion-gate",
        json={
            "session_id": session_id,
            "decision_refs": [decision["decision_id"]],
            "eval_refs": [f"eval::{control_suffix}"],
            "sandbox_ref": f"sandbox::{control_suffix}",
            "artifact_trust_refs": [f"artifact-trust::{control_suffix}"],
            "rollback_plan": f"rollback::{control_suffix}",
            "governance_approval_ref": f"governance::{control_suffix}",
            "admin_approval_ref": f"admin::{control_suffix}",
        },
    ).json()
    sandbox_eval = client.post(
        "/ops/brain/genesis-memory-replay/promotion-gate/sandbox-eval",
        json={
            "gate_id": gate["gate_id"],
            "eval_cases": [
                {"case_id": f"memory-{control_suffix}", "target": "memory_truth", "expected_allowed": True},
                {"case_id": f"retrieval-{control_suffix}", "target": "retrieval_truth", "expected_allowed": True},
                {"case_id": f"graph-{control_suffix}", "target": "graph_truth", "expected_allowed": True},
            ],
            "artifact_trust_ref": f"artifact-trust::sandbox-{control_suffix}",
            "rollback_proof_ref": f"rollback-proof::sandbox-{control_suffix}",
        },
    ).json()
    application = client.post(
        "/ops/brain/genesis-memory-replay/promotion-gate/apply",
        json={
            "gate_id": gate["gate_id"],
            "sandbox_eval_run_id": sandbox_eval["eval_run_id"],
            "artifact_trust_ref": f"artifact-trust::candidate-{control_suffix}",
            "rollback_proof_ref": f"rollback-proof::candidate-{control_suffix}",
            "admin_decision_ref": f"admin-decision::{control_suffix}",
            "approved_by": admin_identity,
        },
    ).json()
    commit = client.post(
        "/ops/brain/genesis-memory-replay/promotion-gate/commit",
        json={
            "application_id": application["application_id"],
            "source_content_by_decision_id": {decision["decision_id"]: content},
            "governance_commit_ref": f"governance-commit::{control_suffix}",
            "admin_commit_ref": f"admin-commit::{control_suffix}",
            "approved_by": admin_identity,
        },
    )
    assert commit.status_code == 200
    return decision, commit.json()

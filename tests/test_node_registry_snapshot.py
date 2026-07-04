from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.growth import NexusNetProductionSpine
from tests.test_growth_lifecycle_orchestrator import lifecycle_request
from tests.test_nexus_phase1_foundation import make_project


def decision_request(eval_path: str) -> dict:
    return {
        "cycle_id": "cycle:registry_snapshot_001",
        "decision_id": "decision:promote_coder_child",
        "action": "promote_child",
        "student_id": "student:coder_child_snapshot",
        "parent_node_ref": "node:expert_coder",
        "human_approved": True,
        # Promotion requires an explicit adapter-artifact trust-clearance attestation
        # (NodeRegistryDecisionEngine.apply blocks on adapter_artifact_trust_clear_required).
        "adapter_artifact_trust_status": "clear",
        "adapter_artifact_trust_clear": True,
        "eval_scorecard_path": eval_path,
    }


def test_node_registry_snapshot_reads_active_roster_events_and_rollback(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)
    cycle_dir = tmp_path / "growth" / "production-spine" / "registry_snapshot_001"
    eval_path = cycle_dir / "eval-gauntlets" / "eval_001" / "eval_scorecard.json"
    eval_path.parent.mkdir(parents=True, exist_ok=True)
    eval_path.write_text(
        (
            '{"promotion_allowed": true, "student_score": 0.94, "parent_score": 0.87, '
            '"teacher_council_score": 0.91, "lower_confidence_surpass_bound": 0.03}'
        ),
        encoding="utf-8",
    )
    decision = spine.apply_node_registry_decision(decision_request(str(eval_path)))

    snapshot = spine.node_registry_snapshot({"cycle_id": "cycle:registry_snapshot_001", "snapshot_id": "snapshot:registry"})

    assert decision["decision"] == "promote_child"
    assert snapshot["status"] == "node_registry_snapshot_ready"
    assert snapshot["active_registry"]["student_state"] == "permanent_active"
    assert snapshot["active_roster"]["student:coder_child_snapshot"]["state"] == "permanent_active"
    assert snapshot["active_roster"]["node:expert_coder"]["state"] == "active"
    assert snapshot["events_count"] == 1
    assert snapshot["rollback_restorable"] is True
    assert snapshot["artifacts"]["rollback_snapshot_path"].endswith("rollback_snapshot.json")


def test_node_registry_snapshot_includes_lifecycle_replay_evidence(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)
    request = lifecycle_request()
    request.update({"cycle_id": "cycle:registry_lifecycle_001", "lifecycle_id": "lifecycle:registry_lifecycle"})

    lifecycle = spine.run_growth_lifecycle(request)
    snapshot = spine.node_registry_snapshot({"cycle_id": "cycle:registry_lifecycle_001", "snapshot_id": "snapshot:lifecycle"})

    assert snapshot["lifecycle_replay"]["lifecycle_id"] == "lifecycle:registry_lifecycle"
    assert snapshot["lifecycle_replay"]["status"] == "closed_loop_complete"
    assert snapshot["lifecycle_replay"]["replay_consistency"]["passed"] is True
    assert (
        snapshot["lifecycle_replay"]["artifact_bridge"]["training_checkpoint_path"]
        == lifecycle["artifact_bridge"]["training_checkpoint_path"]
    )


def test_node_registry_snapshot_api_and_scorecard_action(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    eval_path = project_root / "runtime" / "artifacts" / "growth" / "production-spine" / "registry_snapshot_001" / "eval.json"
    eval_path.parent.mkdir(parents=True, exist_ok=True)
    eval_path.write_text('{"promotion_allowed": true}', encoding="utf-8")
    decision = client.post("/ops/brain/production-spine/node-registry-decisions", json=decision_request(str(eval_path)))
    assert decision.status_code == 200

    snapshot = client.post(
        "/ops/brain/production-spine/node-registry-snapshot",
        json={"cycle_id": "cycle:registry_snapshot_001", "snapshot_id": "snapshot:api"},
    )

    assert snapshot.status_code == 200
    assert snapshot.json()["status"] == "node_registry_snapshot_ready"

    scorecard = client.get("/ops/brain/canon/production-spine")
    assert scorecard.status_code == 200
    assert (
        scorecard.json()["operator_actions"]["inspect_node_registry_snapshot"]["endpoint"]
        == "/ops/brain/production-spine/node-registry-snapshot"
    )

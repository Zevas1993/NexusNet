from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.operations.assimilation_targets import AssimilationTargetRegistry
from tests.test_nexus_phase1_foundation import make_project


EXPECTED_VIDEO_TARGET_IDS = {
    "frontier-small-model-training",
    "jarvis-operator-shell",
    "space-self-updating-surface",
    "agentic-rag-planner",
    "gitnexus-codegraph-gate",
    "synthetic-truth-guard",
    "black-box-interpretability-plane",
    "darwin-godel-machine-lineage",
    "alphaevolve-verifier-search",
    "tars-computer-use-operator",
    "nanochat-constrained-hardware-reference",
    "colibri-moe-architecture-intake",
}


def test_video_assimilation_scorecard_covers_all_specs():
    registry = AssimilationTargetRegistry()

    scorecard = registry.video_scorecard(session_id="video-assimilation")

    assert scorecard["status_label"] == "LOCKED CANON"
    assert scorecard["surface_id"] == "video-assimilation-targets"
    assert scorecard["target_count"] == 12
    assert {target["target_id"] for target in scorecard["targets"]} == EXPECTED_VIDEO_TARGET_IDS
    assert scorecard["coverage_summary"]["refs_only_count"] == 0
    assert scorecard["coverage_summary"]["shadow_only_count"] >= 3
    assert scorecard["coverage_summary"]["clean_room_required_count"] >= 1
    jarvis = next(target for target in scorecard["targets"] if target["target_id"] == "jarvis-operator-shell")
    assert jarvis["source_status"] == "primary_verified"
    assert jarvis["clean_room_required"] is True
    assert "CC BY-NC 4.0" in jarvis["license_boundary"]

    nanochat = next(
        target for target in scorecard["targets"] if target["target_id"] == "nanochat-constrained-hardware-reference"
    )
    assert nanochat["source_status"] == "primary_verified"
    assert nanochat["promotion_state"] == "shadow_certification"
    assert nanochat["clean_room_required"] is False
    assert nanochat["nexus_surfaces"] == ["hardware_profile", "inference_evolution", "dream_lab"]
    assert {"device_aware_precision", "memory_budget_envelope", "reproducible_experiment_contract"}.issubset(
        nanochat["required_controls"]
    )

    colibri = next(target for target in scorecard["targets"] if target["target_id"] == "colibri-moe-architecture-intake")
    assert colibri["source_status"] == "primary_verified"
    assert colibri["promotion_state"] == "shadow_certification"
    assert colibri["clean_room_required"] is True
    assert colibri["nexus_surfaces"] == ["moe_residency", "inference_evolution"]
    assert {"explicit_architecture_descriptor", "sanitized_live_residency_telemetry"}.issubset(
        colibri["required_controls"]
    )


def test_video_assimilation_api_exposes_scorecard(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.get("/ops/brain/video-assimilation-targets")

    assert response.status_code == 200
    payload = response.json()
    assert payload["target_count"] == 12
    assert payload["operator_actions"]["scorecard"]["endpoint"] == "/ops/brain/canon/video-assimilation-targets"

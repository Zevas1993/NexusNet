from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexus.services import build_services
from nexusnet.visuals import NexusVisualizerCompiler
from tests.test_nexus_phase1_foundation import make_project


def test_visualizer_scene_matches_checked_in_bundle():
    compiler = NexusVisualizerCompiler()
    compiled = compiler.compile_scene().model_dump(mode="json")
    checked_in = json.loads(Path("ui/visualizer/data/scene.json").read_text(encoding="utf-8"))

    assert compiled == checked_in
    capsules = [node for node in compiled["nodes"] if node["node_type"] == "capsule"]
    assert len(capsules) == 19
    assert "curriculum-architect" not in [node["subject"] for node in capsules]


def test_visualizer_scene_tracks_authoritative_live_roster(tmp_path: Path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    scene = services.brain_visualizer.scene_payload()
    capsules = [node for node in scene["nodes"] if node["node_type"] == "capsule"]
    expected = [
        assignment.subject
        for assignment in services.brain_teachers.list_assignments()
        if assignment.registry_layer == "v2026_live" and not assignment.auxiliary and assignment.roster_position
    ]

    assert [node["subject"] for node in capsules] == expected
    assert scene["manifest"]["default_renderer"] == "svg-canvas"
    assert scene["manifest"]["render_policy"]["enhancement_path"] == "repo-local-threejs"


def test_visualizer_endpoint_and_static_ui_are_available(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    state = client.get("/ops/brain/visualizer/state", params={"session_id": "visual-session"})
    assert state.status_code == 200
    payload = state.json()
    assert payload["status_label"] == "LOCKED CANON"
    assert payload["manifest"]["default_mode_id"] == "engineering"
    assert payload["overlay_state"]["safe_mode_physiology"]["retry_state"] in {"stable", "fallback-path-active"}

    ui_index = client.get("/ui/visualizer/")
    assert ui_index.status_code == 200
    assert "NexusNet Neural Visualizer" in ui_index.text

    scene = client.get("/ui/visualizer/data/scene.json")
    assert scene.status_code == 200
    assert scene.json()["scene_version"] == "visuals-2026.1"

    legacy = client.get("/ui/3d/")
    assert legacy.status_code == 200
    assert "canonical NexusNet visualizer" in legacy.text


def test_visualizer_overlay_exposes_telemetry_filters_and_performance_profile(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    client.post("/chat", json={"session_id": "visual-session", "message": "Plan a benchmark review", "rag": False})
    payload = client.get("/ops/brain/visualizer/state", params={"session_id": "visual-session"}).json()
    overlay = payload["overlay_state"]

    assert overlay["link_activity"]["status"] in {"bound", "degraded"}
    assert "core_to_capsule" in overlay["link_activity"]
    assert "dream" in overlay["loop_activity"]
    assert "teacher" in overlay["evidence_activity"]
    assert overlay["physiology_activity"]["vram"]["bound"] is False
    assert "expert_capsules" in overlay["filter_catalog"]
    assert "disagreement_compare_endpoint" in overlay["diff_catalog"]
    assert overlay["replay_catalog"]["endpoint"] == "/ops/brain/visualizer/replay"
    assert overlay["performance_profile"]["available_tiers"] == ["auto", "full", "balanced", "safe"]
    assert "providers" in overlay["telemetry_sources"]
    assert "summary" in overlay["telemetry_sources"]
    assert "health" in overlay["telemetry_sources"]["summary"]
    assert "kind" in overlay["telemetry_sources"]["providers"][0]
    assert "device_capability_profile" in overlay["performance_profile"]

    ui_index = client.get("/ui/visualizer/")
    assert "Replay Scrubber" in ui_index.text
    assert "Render Tier" in ui_index.text
    assert "Low Power Clamp" in ui_index.text
    assert "Replay Anchor" in ui_index.text
    assert "Replay Timeline" in ui_index.text
    assert "Compare Cohorts" in ui_index.text
    assert "Operator Inspection" in ui_index.text
    assert "Depth Inspection" in ui_index.text


def test_visualizer_goose_compare_controls_and_catalog_are_read_only(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    gateway = client.get(
        "/ops/brain/gateway",
        params={
            "requested_extensions": "mcp-filesystem",
            "requested_tools": "filesystem.readonly",
            "trigger_source": "visualizer:goose-compare",
        },
    )
    assert gateway.status_code == 200

    adversary = client.post(
        "/ops/brain/security/adversary-review",
        json={
            "subject": "visualizer::goose-compare",
            "requested_tools": ["shell.exec"],
            "allowed_tools": ["shell.exec"],
            "risk_level": "high",
            "reviewer_status": "available",
            "trigger_source": "visualizer:goose-compare",
        },
    )
    assert adversary.status_code == 200

    payload = client.get("/ops/brain/visualizer/state", params={"session_id": "visualizer-goose-compare"}).json()
    overlay = payload["overlay_state"]
    goose_compare = overlay["inspection_controls"]["goose_compare"]
    goose_catalog = overlay["diff_catalog"]["goose_compare"]

    assert goose_compare["gateway_executions"]
    assert goose_compare["policy_versions"]
    assert goose_compare["certifications"]
    assert goose_compare["adversary_reviews"]
    assert goose_compare["acp_providers"]
    assert goose_compare["group_filters"]
    assert "policy-lifecycle" in goose_compare["default_expanded_groups"]
    assert goose_catalog["gateway_compare_endpoint"] == "/ops/brain/gateway/history/compare"
    assert goose_catalog["policy_compare_endpoint"] == "/ops/brain/extensions/policy-history/compare"
    assert goose_catalog["certification_compare_endpoint"] == "/ops/brain/extensions/certifications/compare"
    assert goose_catalog["adversary_compare_endpoint"] == "/ops/brain/security/adversary-reviews/compare"
    assert goose_catalog["acp_compare_endpoint"] == "/ops/brain/acp/providers/compare"
    assert "policy-lifecycle" in goose_catalog["group_names"]
    assert goose_catalog["group_descriptions"]["trace-and-artifacts"]
    assert "policy-lifecycle" in goose_catalog["default_expanded_groups"]

    ui_index = client.get("/ui/visualizer/")
    assert ui_index.status_code == 200
    assert "Compare Gateway" in ui_index.text
    assert "Compare Policies" in ui_index.text
    assert "Compare Certifications" in ui_index.text
    assert "Compare Adversary" in ui_index.text
    assert "Compare ACP" in ui_index.text
    assert "Grouped Diff Sections" in ui_index.text
    assert "Goose Diff Filters" in ui_index.text
    assert "Expand All Groups" in ui_index.text
    assert "Collapse All Groups" in ui_index.text
    assert "Reset Group Filters" in ui_index.text

    wrapper = client.get("/ops/brain/wrapper-surface").json()
    assert "policy-lifecycle" in wrapper["assimilation"]["compare_groups"]["goose_compare"]["group_names"]
    assert "policy-lifecycle" in wrapper["assimilation"]["compare_groups"]["goose_compare"]["default_expanded_groups"]


def test_visualizer_replay_and_route_compare_endpoints_work(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    client.post("/chat", json={"session_id": "visual-session", "message": "Explain the operator kernel", "rag": True})
    client.post("/chat", json={"session_id": "visual-session", "message": "Write Python code for a router test", "rag": False})

    replay = client.get("/ops/brain/visualizer/replay", params={"session_id": "visual-session", "limit": 6})
    assert replay.status_code == 200
    replay_payload = replay.json()
    assert replay_payload["frame_count"] >= 1
    assert replay_payload["frames"][0]["overlay"]["link_activity"]["status"] in {"bound", "degraded"}
    assert "provider_chain" in replay_payload["frames"][0]["source_ref"]

    route_compare = client.get(
        "/ops/brain/visualizer/route-activity/compare",
        params={"session_id": "visual-session", "left_window": 1, "right_window": 2},
    )
    assert route_compare.status_code == 200
    route_payload = route_compare.json()
    assert route_payload["left"]["window"] == 1
    assert route_payload["right"]["window"] == 2
    assert "dream_intensity_delta" in route_payload["diff"]
    assert "scene_delta" in route_payload


def test_visualizer_compare_endpoints_surface_disagreement_and_replacement_diffs(tmp_path: Path):
    project_root = make_project(tmp_path)
    app = create_app(str(project_root))
    services = app.state.services
    now = datetime.now(timezone.utc).isoformat()

    services.store.save_teacher_disagreement_artifact(
        {
            "artifact_id": "teachdis-left",
            "subject": "coder",
            "registry_layer": "v2026_live",
            "primary_teacher_id": "Qwen3-Coder-Next",
            "secondary_teacher_id": "Devstral 2",
            "arbitration_result": "SELECT_BEST",
            "benchmark_family": "multi-file patching",
            "disagreement_severity": 0.21,
            "lfm2_lane": None,
            "lfm2_bounded_ok": True,
            "created_at": now,
        }
    )
    services.store.save_teacher_disagreement_artifact(
        {
            "artifact_id": "teachdis-right",
            "subject": "coder",
            "registry_layer": "v2026_live",
            "primary_teacher_id": "Qwen3-Coder-Next",
            "secondary_teacher_id": "Devstral 2",
            "arbitration_result": "PATCH_DOMAIN_WITH_LFM2_EDITS_THEN_VERIFY",
            "benchmark_family": "multi-file patching",
            "disagreement_severity": 0.56,
            "lfm2_lane": "toolsmith",
            "lfm2_bounded_ok": True,
            "created_at": now,
        }
    )
    services.store.save_replacement_readiness_report(
        {
            "report_id": "repl-left",
            "subject": "coder",
            "teacher_id": "Qwen3-Coder-Next",
            "replacement_mode": "shadow",
            "ready": False,
            "subject_trend_ready": True,
            "fleet_gate_ready": False,
            "cohort_gate_ready": False,
            "rollback_ready": True,
            "metrics": {"native_vs_primary_delta": 0.12},
            "created_at": now,
        }
    )
    services.store.save_replacement_readiness_report(
        {
            "report_id": "repl-right",
            "subject": "coder",
            "teacher_id": "Qwen3-Coder-Next",
            "replacement_mode": "replace",
            "ready": True,
            "subject_trend_ready": True,
            "fleet_gate_ready": True,
            "cohort_gate_ready": True,
            "rollback_ready": True,
            "metrics": {"native_vs_primary_delta": 0.41},
            "created_at": now,
        }
    )

    client = TestClient(app)
    disagreement = client.get(
        "/ops/brain/visualizer/disagreements/compare",
        params={"left_artifact_id": "teachdis-left", "right_artifact_id": "teachdis-right"},
    )
    assert disagreement.status_code == 200
    assert disagreement.json()["diff"]["severity_delta"] == 0.35
    assert "scene_delta" in disagreement.json()

    readiness = client.get(
        "/ops/brain/visualizer/replacement-readiness/compare",
        params={"left_report_id": "repl-left", "right_report_id": "repl-right"},
    )
    assert readiness.status_code == 200
    assert readiness.json()["diff"]["replacement_modes"] == ["shadow", "replace"]
    assert readiness.json()["diff"]["metric_delta"]["native_vs_primary_delta"] == 0.29
    assert "scene_delta" in readiness.json()


def test_visualizer_cohort_compare_exposes_scene_delta(tmp_path: Path):
    project_root = make_project(tmp_path)
    app = create_app(str(project_root))
    services = app.state.services
    client = TestClient(app)

    client.post("/chat", json={"session_id": "visual-session", "message": "Write router code", "rag": False})
    services.brain_teacher_fleets.build(fleet_id="coding_agent_fleet", window_id="short", subject="coder")
    services.brain_teacher_fleets.build(fleet_id="coding_agent_fleet", window_id="long", subject="coder")

    cohort_compare = client.get(
        "/ops/brain/teachers/cohorts/compare",
        params={"fleet_id": "coding_agent_fleet", "subject": "coder", "left_window": "short", "right_window": "long"},
    )
    assert cohort_compare.status_code == 200
    payload = cohort_compare.json()
    assert "scene_delta" in payload
    assert payload["scene_delta"]["hot_subjects"][0]["subject"] == "coder"
    assert any(item["link_id"] == "core::coder" for item in payload["scene_delta"]["hot_links"])

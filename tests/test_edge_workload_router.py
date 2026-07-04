from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.runtime.edge_router import EdgeWorkloadRequest, EdgeWorkloadRouter
from tests.test_nexus_phase1_foundation import make_project


def test_edge_workload_router_keeps_private_offline_transcription_local_with_explainability():
    router = EdgeWorkloadRouter()

    decision = router.route(
        EdgeWorkloadRequest(
            workload_id="voice::private-meeting",
            workload_type="transcription",
            input_modalities=["audio"],
            data_sensitivity="private",
            offline_required=True,
            latency_target_ms=900,
            quality_priority="balanced",
            hardware_snapshot={
                "local_cpu": True,
                "local_gpu": True,
                "local_gpu_vram_gb": 24,
                "browser_webgpu": True,
                "android_npu": False,
                "wsl_gpu": True,
            },
        )
    )

    assert decision["status_label"] == "LOCKED CANON"
    assert decision["authority"] == "NexusBrain"
    assert decision["selected_lane_id"] == "local-gpu"
    assert decision["selected_lane"]["privacy_posture"] == "local-private"
    assert "privacy_sensitive" in decision["reason_codes"]
    assert "offline_required" in decision["reason_codes"]
    cloud = next(candidate for candidate in decision["candidates"] if candidate["lane_id"] == "cloud-api")
    assert cloud["eligible"] is False
    assert "offline-required" in cloud["blockers"]
    assert decision["policy_scan"]["summary"]["allow_merge"] is True


def test_edge_workload_router_allows_cloud_for_public_frontier_reasoning_when_not_private():
    router = EdgeWorkloadRouter()

    decision = router.route(
        {
            "workload_id": "analysis::public-benchmark",
            "workload_type": "frontier_reasoning",
            "input_modalities": ["text"],
            "data_sensitivity": "public",
            "offline_required": False,
            "latency_target_ms": 4000,
            "quality_priority": "maximum",
            "hardware_snapshot": {"local_cpu": True, "local_gpu": False, "browser_webgpu": False},
        }
    )

    assert decision["selected_lane_id"] == "cloud-api"
    assert "frontier_quality" in decision["reason_codes"]
    assert decision["selected_lane"]["cost_posture"] == "metered"
    assert decision["policy_scan"]["summary"]["allow_merge"] is True


def test_edge_workload_router_blocks_live_route_from_upstream_aitune_gate():
    router = EdgeWorkloadRouter()

    decision = router.route(
        EdgeWorkloadRequest(
            workload_id="analysis::blocked-upstream-runtime",
            workload_type="frontier_reasoning",
            input_modalities=["text"],
            data_sensitivity="public",
            offline_required=False,
            latency_target_ms=4000,
            quality_priority="maximum",
            hardware_snapshot={"local_cpu": True, "local_gpu": False, "browser_webgpu": False},
            upstream_aitune_gate={
                "status": "blocked-upstream-gate",
                "can_execute_here": False,
                "readiness_blockers": ["runtime_backend_not_validated"],
            },
        )
    )

    assert decision["selected_lane_id"] == "cloud-api"
    assert decision["status"] == "blocked-upstream-gate"
    assert decision["runtime_state"] == "degraded"
    assert decision["upstream_aitune_gate"]["blockers"] == ["runtime_backend_not_validated"]
    assert "upstream_aitune_gate_blocked" in decision["reason_codes"]
    assert "router_alignment_blocks_upstream_aitune_gate" in decision["route_blockers"]

    summary = router.summary()
    assert summary["runtime_state"] == "degraded"
    assert summary["latest_decision"]["status"] == "blocked-upstream-gate"


def test_edge_workload_router_api_blackbox_and_control_panel_surface(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/edge-workload-router/route",
        json={
            "workload_id": "vision::local-inspection",
            "workload_type": "vision",
            "input_modalities": ["image"],
            "data_sensitivity": "regulated",
            "offline_required": True,
            "latency_target_ms": 1200,
            "quality_priority": "balanced",
            "hardware_snapshot": {
                "local_cpu": True,
                "local_gpu": False,
                "browser_webgpu": True,
                "android_npu": True,
            },
        },
    )

    assert response.status_code == 200
    route = response.json()
    assert route["selected_lane_id"] in {"browser-webgpu-webnn", "android-npu"}
    assert "regulated_data" in route["reason_codes"]

    summary = client.get("/ops/brain/edge-workload-router")
    assert summary.status_code == 200
    summary_payload = summary.json()
    assert summary_payload["runtime_state"] == "live-bound"
    assert summary_payload["latest_decision"]["workload_id"] == "vision::local-inspection"

    scorecard = client.get("/ops/brain/canon/edge-workload-router")
    assert scorecard.status_code == 200
    scorecard_payload = scorecard.json()
    assert "local_vs_cloud_explainability" in scorecard_payload["required_controls"]
    assert scorecard_payload["operator_actions"]["route"]["endpoint"] == "/ops/brain/edge-workload-router/route"

    blocked = client.post(
        "/ops/brain/edge-workload-router/route",
        json={
            "workload_id": "analysis::api-blocked-upstream-runtime",
            "workload_type": "frontier_reasoning",
            "input_modalities": ["text"],
            "data_sensitivity": "public",
            "offline_required": False,
            "latency_target_ms": 4000,
            "quality_priority": "maximum",
            "hardware_snapshot": {"local_cpu": True, "local_gpu": False, "browser_webgpu": False},
            "upstream_aitune_gate": {
                "status": "blocked-upstream-gate",
                "can_execute_here": False,
                "readiness_blockers": ["runtime_backend_not_validated"],
            },
        },
    )
    assert blocked.status_code == 200
    assert blocked.json()["status"] == "blocked-upstream-gate"

    degraded_scorecard = client.get("/ops/brain/canon/edge-workload-router")
    assert degraded_scorecard.status_code == 200
    degraded_payload = degraded_scorecard.json()
    assert degraded_payload["runtime_state"] == "degraded"
    assert degraded_payload["latest_decision"]["status"] == "blocked-upstream-gate"

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "edge-router-cockpit"})
    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    assert control_panel["edge_workload_router_scorecard"]["runtime_state"] == "degraded"

    blackbox = client.get("/ops/brain/canon/blackbox", params={"session_id": "edge-router-cockpit"}).json()
    assert blackbox["scorecard_refs"]["edge_workload_router"] == "/ops/brain/canon/edge-workload-router"

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Edge Workload Router" in ui.text
    assert "edgeWorkloadRouterScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderEdgeWorkloadRouterScorecard" in app_js
    assert "/ops/brain/canon/edge-workload-router" in app_js

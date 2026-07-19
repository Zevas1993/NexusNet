from __future__ import annotations

import json

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


def _observation(*, source_refs: list[str]) -> dict:
    return {
        "candidate_id": "acme-code-model",
        "model_id": "acme/code-model",
        "provider": "acme-ai",
        "release_url": "https://example.invalid/acme/code-model",
        "source_refs": source_refs,
        "teacher_roles": ["generator", "critic"],
        "domain_scope": ["coding", "software"],
        "risk_scope": ["medium"],
        "license_gate": "approved",
        "privacy_gate": "approved",
        "hardware_gate": "approved",
        "cost_gate": "approved",
        "security_review": "passed",
    }


def test_layer14_static_model_release_observation_merges_into_teacher_universe_and_replays(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    observed = client.post(
        "/ops/brain/model-release-radar/observations",
        json=_observation(source_refs=["release::acme-code-model"]),
    )
    assert observed.status_code == 200
    first = observed.json()
    assert first["status"] == "watchlist"
    assert first["candidate_intake"]["candidate"]["candidate_status"] == "watchlist"
    assert first["candidate_intake"]["teacher_capability_passport"]["promotion_allowed"] is False
    assert first["raw_content_included"] is False

    duplicate = client.post(
        "/ops/brain/model-release-radar/observations",
        json=_observation(source_refs=["release-note::acme-code-model"]),
    )
    assert duplicate.status_code == 200
    assert set(duplicate.json()["candidate_intake"]["candidate"]["source_refs"]) == {
        "release::acme-code-model",
        "release-note::acme-code-model",
    }

    radar = client.get("/ops/brain/model-release-radar")
    assert radar.status_code == 200
    summary = radar.json()
    assert summary["model_release_observation_count"] == 1
    assert summary["watchlist_count"] == 1
    assert summary["promotion_ready_count"] == 0

    governance = client.get("/ops/brain/genesis-teacher-governance").json()
    assert governance["persisted_candidate_intake_count"] == 1
    assert governance["persisted_candidate_ids"] == ["acme-code-model"]

    visualizer = client.get("/ops/brain/visualizer/state").json()
    scorecard = visualizer["overlay_state"]["control_panel"]["forward_radar_scorecard"]
    assert scorecard["model_release"]["model_release_observation_count"] == 1

    replay = TestClient(create_app(str(project_root))).get("/ops/brain/model-release-radar").json()
    assert replay["model_release_observation_count"] == 1
    assert replay["watchlist_count"] == 1

    serialized = json.dumps({"first": first, "summary": summary, "replay": replay})
    assert str(project_root) not in serialized
    assert "raw_prompt" not in serialized
    assert "raw_output" not in serialized


def test_layer14_downtime_scheduler_persists_blocked_and_dry_run_packets_without_execution(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    observed = client.post(
        "/ops/brain/model-release-radar/observations",
        json=_observation(source_refs=["release::acme-code-model"]),
    )
    assert observed.status_code == 200

    blocked = client.post(
        "/ops/brain/model-release-radar/downtime-benchmarks",
        json={
            "candidate_id": "acme-code-model",
            "serving": True,
            "temp_c": 60.0,
            "free_vram_mb": 4096.0,
            "budget_available": True,
            "release_gate_open": True,
        },
    )
    assert blocked.status_code == 200
    assert blocked.json()["status"] == "skipped"
    assert "system_busy_serving" in blocked.json()["blockers"]
    assert blocked.json()["benchmark_execution_allowed"] is False

    queued = client.post(
        "/ops/brain/model-release-radar/downtime-benchmarks",
        json={
            "candidate_id": "acme-code-model",
            "serving": False,
            "temp_c": 60.0,
            "free_vram_mb": 4096.0,
            "budget_available": True,
            "release_gate_open": True,
        },
    )
    assert queued.status_code == 200
    assert queued.json()["status"] == "queued-dry-run"
    assert queued.json()["planned_stages"] == ["metadata-validation", "safety-provenance-scan", "hardware-cost-estimate"]
    assert queued.json()["benchmark_execution_allowed"] is False
    assert queued.json()["model_download_allowed"] is False
    assert queued.json()["active_teacher_promotion_allowed"] is False
    assert queued.json()["raw_content_included"] is False

    summary = client.get("/ops/brain/model-release-radar").json()
    scheduler = summary["downtime_scheduler"]
    assert scheduler["packet_count"] == 2
    assert scheduler["skipped_count"] == 1
    assert scheduler["queued_dry_run_count"] == 1

    visualizer = client.get("/ops/brain/visualizer/state").json()
    scorecard = visualizer["overlay_state"]["control_panel"]["forward_radar_scorecard"]
    assert scorecard["model_release"]["downtime_scheduler"]["packet_count"] == 2

    replay = TestClient(create_app(str(project_root))).get("/ops/brain/model-release-radar").json()
    assert replay["downtime_scheduler"]["packet_count"] == 2
    assert replay["downtime_scheduler"]["queued_dry_run_count"] == 1


def test_layer14_bounded_smoke_eval_consumes_queued_packet_and_keeps_candidate_non_promotable(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    assert client.post(
        "/ops/brain/model-release-radar/observations",
        json=_observation(source_refs=["release::acme-code-model"]),
    ).status_code == 200
    queued = client.post(
        "/ops/brain/model-release-radar/downtime-benchmarks",
        json={
            "candidate_id": "acme-code-model",
            "serving": False,
            "temp_c": 60.0,
            "free_vram_mb": 4096.0,
            "budget_available": True,
            "release_gate_open": True,
        },
    )
    assert queued.status_code == 200

    smoke = client.post(
        "/ops/brain/model-release-radar/smoke-evals",
        json={"candidate_id": "acme-code-model", "packet_id": queued.json()["packet_id"]},
    )
    assert smoke.status_code == 200
    result = smoke.json()
    assert result["status"] == "synthetic-metadata-smoke-eval-passed"
    assert result["sandbox_action"]["status"] == "planned-shadow"
    assert result["sandbox_action"]["execution_allowed"] is False
    assert result["benchmark_execution_allowed"] is False
    assert result["model_download_allowed"] is False
    assert result["candidate_status_after"] == "watchlist"
    assert result["recommendation"]["status"] == "keep-watchlist-awaiting-real-eval"
    assert result["recommendation"]["active_teacher_promotion_allowed"] is False
    assert result["raw_content_included"] is False

    summary = client.get("/ops/brain/model-release-radar").json()
    assert summary["smoke_eval_summary"]["smoke_eval_count"] == 1
    assert summary["smoke_eval_summary"]["synthetic_passed_count"] == 1

    replay = TestClient(create_app(str(project_root))).get("/ops/brain/model-release-radar").json()
    assert replay["smoke_eval_summary"]["smoke_eval_count"] == 1


def test_layer14_isolated_fixture_runner_executes_sanitized_contract_without_model_promotion(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    assert client.post(
        "/ops/brain/model-release-radar/observations",
        json=_observation(source_refs=["release::acme-code-model"]),
    ).status_code == 200
    queued = client.post(
        "/ops/brain/model-release-radar/downtime-benchmarks",
        json={
            "candidate_id": "acme-code-model",
            "serving": False,
            "temp_c": 60.0,
            "free_vram_mb": 4096.0,
            "budget_available": True,
            "release_gate_open": True,
        },
    )
    assert queued.status_code == 200
    smoke = client.post(
        "/ops/brain/model-release-radar/smoke-evals",
        json={"candidate_id": "acme-code-model", "packet_id": queued.json()["packet_id"]},
    )
    assert smoke.status_code == 200

    fixture = client.post(
        "/ops/brain/model-release-radar/synthetic-fixtures",
        json={"candidate_id": "acme-code-model", "smoke_eval_id": smoke.json()["eval_id"]},
    )
    assert fixture.status_code == 200
    result = fixture.json()
    assert result["status"] == "isolated-synthetic-capability-fixture-passed"
    assert result["evaluation_kind"] == "isolated-process-synthetic-fixture"
    assert result["isolated_process"]["status"] == "completed"
    assert result["fixture_checks"]["structured_output_contract"] is True
    assert result["fixture_checks"]["declared_teacher_roles_present"] is True
    assert result["real_model_execution"] is False
    assert result["model_download_allowed"] is False
    assert result["model_attach_allowed"] is False
    assert result["candidate_status_after"] == "watchlist"
    assert result["recommendation"]["status"] == "keep-watchlist-awaiting-real-model-eval"
    assert result["recommendation"]["active_teacher_promotion_allowed"] is False
    assert result["raw_content_included"] is False

    summary = client.get("/ops/brain/model-release-radar").json()
    fixture_summary = summary["synthetic_fixture_summary"]
    assert fixture_summary["fixture_eval_count"] == 1
    assert fixture_summary["isolated_fixture_passed_count"] == 1
    assert fixture_summary["real_model_benchmark_count"] == 0

    visualizer = client.get("/ops/brain/visualizer/state").json()
    scorecard = visualizer["overlay_state"]["control_panel"]["forward_radar_scorecard"]
    assert scorecard["model_release"]["synthetic_fixture_summary"]["fixture_eval_count"] == 1

    replay = TestClient(create_app(str(project_root))).get("/ops/brain/model-release-radar").json()
    assert replay["synthetic_fixture_summary"]["fixture_eval_count"] == 1

    serialized = json.dumps({"result": result, "summary": summary, "replay": replay})
    assert str(project_root) not in serialized
    assert "raw_prompt" not in serialized
    assert "raw_output" not in serialized

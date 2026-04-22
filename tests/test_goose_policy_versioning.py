from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


def test_goose_recipe_execution_links_gateway_execution_artifacts(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    chat = client.post(
        "/chat",
        json={
            "session_id": "goose-recipe-policy-versioning",
            "message": "Create a trace anchor for Goose recipe gateway linkage.",
            "rag": False,
        },
    )
    assert chat.status_code == 200
    trace_id = chat.json()["trace_id"]

    response = client.post(
        "/ops/brain/recipes/execute",
        json={
            "recipe_id": "ao-deep-research",
            "trigger_source": "recipe:manual-review",
            "session_id": "goose-recipe-policy-versioning",
            "parameter_set": {"topic": "Policy versioned gateway coverage"},
            "status": "success",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["gateway_execution_id"]
    assert payload["gateway_report_id"]
    assert payload["gateway_resolution_id"]
    assert trace_id in payload["linked_trace_ids"]
    assert any("gateway\\resolutions" in artifact or "gateway/resolutions" in artifact for artifact in payload["artifacts_produced"])
    assert "recipe-driven" in payload["flow_families"]
    assert "gateway-controlled" in payload["flow_families"]

    gateway_history = client.get("/ops/brain/gateway/history", params={"trigger_source": "recipe:manual-review"})
    assert gateway_history.status_code == 200
    gateway_history_json = gateway_history.json()
    assert gateway_history_json["latest_execution"]["execution_id"] == payload["gateway_execution_id"]
    assert gateway_history_json["latest_report_id"] == payload["gateway_report_id"]

    wrapper = client.get("/ops/brain/wrapper-surface").json()
    visualizer = client.get("/ops/brain/visualizer/state").json()
    runtime_posture = visualizer["overlay_state"]["runtime_posture"]
    assert wrapper["goose"]["recipes"]["history"]["latest_gateway_execution_id"] == payload["gateway_execution_id"]
    assert wrapper["goose"]["recipes"]["history"]["flow_family_counts"]["recipe-driven"] >= 1
    assert runtime_posture["goose_latest_recipe_gateway_execution_id"] == payload["gateway_execution_id"]
    assert runtime_posture["goose_latest_recipe_gateway_report_id"] == payload["gateway_report_id"]
    assert runtime_posture["goose_recipe_flow_family_counts"]["recipe-driven"] >= 1


def test_goose_subagent_plan_persists_policy_set_and_bundle_family_traceability(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/subagents/plan",
        json={
            "recipe_id": "ao-deep-research",
            "parent_task": "Expand a Goose worker plan under versioned bundle governance.",
            "mode": "parallel",
            "linked_trace_ids": ["trace-goose-policy-set"],
        },
    )
    assert response.status_code == 200
    payload = response.json()
    execution_history = payload["execution_history"]
    assert "goose-mcp-readonly" in execution_history["extension_policy_set_ids"]
    assert "filesystem-bridge" in execution_history["extension_bundle_families"]
    assert execution_history["gateway_execution_id"]
    assert execution_history["gateway_report_id"]

    gateway_resolution = payload["gateway_resolution"]
    assert gateway_resolution["execution_history"]["execution_id"] == execution_history["gateway_execution_id"]
    assert any(item["policy_set_id"] == "goose-mcp-readonly" for item in gateway_resolution["extension_provenance"])
    assert any(item["bundle_family"] == "filesystem-bridge" for item in gateway_resolution["extension_provenance"])

    gateway_history = client.get("/ops/brain/gateway/history", params={"trigger_source": "subagent-plan:parallel"})
    assert gateway_history.status_code == 200
    history_json = gateway_history.json()
    assert "goose-mcp-readonly" in history_json["latest_extension_policy_set_ids"]
    assert "filesystem-bridge" in history_json["latest_extension_bundle_families"]
    assert "subagent-delegation" in execution_history["flow_families"]
    assert history_json["flow_family_counts"]["subagent-delegation"] >= 1


def test_goose_extension_policy_sets_are_read_only_and_versioned(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    summary = client.get("/ops/brain/extensions/policy-sets")
    assert summary.status_code == 200
    summary_json = summary.json()
    assert summary_json["policy_set_count"] >= 3
    assert "filesystem-bridge" in summary_json["bundle_families"]

    detail = client.get("/ops/brain/extensions/policy-sets/goose-mcp-readonly")
    assert detail.status_code == 200
    detail_json = detail.json()
    assert detail_json["policy_set"]["policy_set_id"] == "goose-mcp-readonly"
    assert detail_json["policy_set"]["version"] == "2026.04"
    assert detail_json["bundle_count_in_workspace"] >= 1

    bundle = client.get("/ops/brain/extensions/mcp-filesystem")
    assert bundle.status_code == 200
    bundle_json = bundle.json()
    assert bundle_json["bundle"]["policy_set_id"] == "goose-mcp-readonly"
    assert bundle_json["bundle"]["policy_set_version"] == "2026.04"
    assert bundle_json["policy_set_detail"]["policy_set"]["bundle_family"] == "filesystem-bridge"

    wrapper = client.get("/ops/brain/wrapper-surface").json()
    visualizer = client.get("/ops/brain/visualizer/state").json()
    assert wrapper["goose"]["extension_policy_sets"]["policy_set_count"] >= 3
    assert visualizer["overlay_state"]["runtime_posture"]["goose_extension_policy_set_count"] >= 3


def test_goose_policy_lifecycle_and_bundle_certification_are_exposed_read_only(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    history = client.get("/ops/brain/extensions/policy-history")
    assert history.status_code == 200
    history_json = history.json()
    assert history_json["artifact_count"] >= 3
    assert "active" in history_json["status_counts"]
    assert history_json["status_counts"]["rolled_back"] >= 1
    assert history_json["status_counts"]["superseded"] >= 1
    assert history_json["status_counts"]["held"] >= 1

    detail = client.get("/ops/brain/extensions/policy-history/goose-acp-coding-provider")
    assert detail.status_code == 200
    detail_json = detail.json()
    assert detail_json["item"]["policy_set_id"] == "goose-acp-coding-provider"
    assert detail_json["item"]["status"] == "shadow"
    assert detail_json["item"]["rollback_reference"] == "goose-acp-coding-provider@2026.03"
    assert detail_json["lineage_depth"] >= 3
    assert "held" in [item["status"] for item in detail_json["lineage"] if item.get("status")]
    assert "superseded" in [item["status"] for item in detail_json["lineage"] if item.get("status")]
    assert detail_json["latest_status_transition"]["status"] == "shadow"

    rolled_back_detail = client.get(
        "/ops/brain/extensions/policy-history/goose-mcp-readonly",
        params={"version": "2026.03"},
    )
    assert rolled_back_detail.status_code == 200
    rolled_back_detail_json = rolled_back_detail.json()
    assert rolled_back_detail_json["item"]["status"] == "rolled_back"
    assert rolled_back_detail_json["item"]["rollback_reference"] == "goose-mcp-readonly@2026.02"
    assert rolled_back_detail_json["item"]["stable_policy_version_id"] == "goose-mcp-readonly@2026.03"

    active_detail = client.get(
        "/ops/brain/extensions/policy-history/goose-mcp-readonly",
        params={"version": "2026.04"},
    )
    assert active_detail.status_code == 200
    active_detail_json = active_detail.json()
    assert active_detail_json["item"]["status"] == "active"
    assert active_detail_json["item"]["stable_policy_version_id"] == "goose-mcp-readonly@2026.04"
    assert any(item["status"] == "rolled_back" for item in active_detail_json["lineage"] if item.get("status"))
    assert any(item["status"] == "superseded" for item in active_detail_json["lineage"] if item.get("status"))

    retrieval_active_detail = client.get(
        "/ops/brain/extensions/policy-history/goose-local-retrieval-pack",
        params={"version": "2026.04"},
    )
    assert retrieval_active_detail.status_code == 200
    retrieval_active_json = retrieval_active_detail.json()
    assert retrieval_active_json["item"]["status"] == "active"
    assert retrieval_active_json["lineage_depth"] >= 3
    assert any(item["status"] == "rolled_back" for item in retrieval_active_json["lineage"] if item.get("status"))
    assert any(item["status"] == "superseded" for item in retrieval_active_json["lineage"] if item.get("status"))

    rollouts = client.get("/ops/brain/extensions/policy-rollouts")
    assert rollouts.status_code == 200
    rollout_json = rollouts.json()
    assert rollout_json["family_count"] >= 3
    assert any(item["bundle_family"] == "acp-provider-lane" for item in rollout_json["items"])
    acp_rollout = next(item for item in rollout_json["items"] if item["bundle_family"] == "acp-provider-lane")
    assert any(item["version"] == "2026.03" for item in acp_rollout["held_versions"])
    filesystem_rollout = next(item for item in rollout_json["items"] if item["bundle_family"] == "filesystem-bridge")
    assert any(item["version"] == "2026.03" for item in filesystem_rollout["rolled_back_versions"])
    assert any(item["version"] == "2026.02" for item in filesystem_rollout["superseded_versions"])

    bundle = client.get("/ops/brain/extensions/acp-coding-lane")
    assert bundle.status_code == 200
    bundle_json = bundle.json()
    assert bundle_json["bundle"]["certification_status"] == "shadow-approved"
    assert bundle_json["bundle"]["certification_artifact_id"]
    assert bundle_json["bundle"]["policy_lifecycle"]["artifact_id"]

    certification = client.get(f"/ops/brain/extensions/certifications/{bundle_json['bundle']['certification_artifact_id']}")
    assert certification.status_code == 200
    certification_json = certification.json()
    assert certification_json["item"]["privilege_inheritance_confusion"] is True
    assert "review-extension-acp-permission-inheritance" in certification_json["item"]["recommended_remediation_actions"]
    assert certification_json["item"]["stable_certification_id"] == "acp-coding-lane::goose-acp-coding-provider::2026.04"
    assert certification_json["item"]["policy_lineage_statuses"][:2] == ["shadow", "held"]
    assert certification_json["item"]["certification_lineage_depth"] >= 3
    assert certification_json["item"]["historical_certification_artifact_ids"]
    assert "held" in certification_json["item"]["certification_lineage_statuses"]
    assert "revoked" in certification_json["item"]["certification_lineage_statuses"]
    assert certification_json["item"]["restoration_detected"] is True
    assert len(certification_json["item"]["restored_from_certification_artifact_ids"]) >= 2
    assert certification_json["lineage_summary"]["historical_artifact_count"] >= 2
    assert certification_json["item"]["permission_delta_from_previous"]["added"] == []

    policy_compare = client.get(
        "/ops/brain/extensions/policy-history/compare",
        params={
            "left_policy_set_id": "goose-mcp-readonly",
            "right_policy_set_id": "goose-acp-coding-provider",
            "left_version": "2026.04",
            "right_version": "2026.04",
        },
    )
    assert policy_compare.status_code == 200
    policy_compare_json = policy_compare.json()
    assert policy_compare_json["diff"]["status_changed"] is True
    assert policy_compare_json["left"]["policy_set_id"] == "goose-mcp-readonly"
    assert policy_compare_json["right"]["policy_set_id"] == "goose-acp-coding-provider"
    assert policy_compare_json["export"]["report_id"]
    assert Path(policy_compare_json["export"]["payload_path"]).exists()
    assert Path(policy_compare_json["export"]["markdown_path"]).exists()
    assert "Lifecycle Delta" in Path(policy_compare_json["export"]["markdown_path"]).read_text(encoding="utf-8")

    filesystem_bundle = client.get("/ops/brain/extensions/mcp-filesystem")
    assert filesystem_bundle.status_code == 200
    filesystem_bundle_json = filesystem_bundle.json()
    filesystem_certification = client.get(
        f"/ops/brain/extensions/certifications/{filesystem_bundle_json['bundle']['certification_artifact_id']}"
    )
    assert filesystem_certification.status_code == 200
    filesystem_certification_json = filesystem_certification.json()
    assert filesystem_certification_json["item"]["restoration_detected"] is True
    assert "goose-mcp-readonly@2026.03" in filesystem_certification_json["item"]["restored_from_policy_versions"]
    assert "rolled_back" in filesystem_certification_json["item"]["policy_lineage_statuses"]
    assert "superseded" in filesystem_certification_json["item"]["policy_lineage_statuses"]
    assert filesystem_certification_json["item"]["certification_lineage_depth"] >= 3
    assert len(filesystem_certification_json["item"]["historical_certification_artifact_ids"]) >= 2
    assert "rolled_back" in filesystem_certification_json["item"]["certification_lineage_statuses"]
    assert "revoked" in filesystem_certification_json["item"]["certification_lineage_statuses"]
    assert filesystem_certification_json["lineage_summary"]["historical_fixture_count"] >= 2

    retrieval_bundle = client.get("/ops/brain/extensions/local-retrieval-pack")
    assert retrieval_bundle.status_code == 200
    retrieval_bundle_json = retrieval_bundle.json()
    retrieval_certification = client.get(
        f"/ops/brain/extensions/certifications/{retrieval_bundle_json['bundle']['certification_artifact_id']}"
    )
    assert retrieval_certification.status_code == 200
    retrieval_certification_json = retrieval_certification.json()
    assert retrieval_certification_json["item"]["bundle_family"] == "retrieval-pack"
    assert retrieval_certification_json["item"]["restoration_detected"] is True
    assert retrieval_certification_json["item"]["certification_lineage_depth"] >= 3
    assert "rolled_back" in retrieval_certification_json["item"]["certification_lineage_statuses"]
    assert "revoked" in retrieval_certification_json["item"]["certification_lineage_statuses"]
    assert len(retrieval_certification_json["item"]["historical_certification_artifact_ids"]) >= 2
    assert retrieval_certification_json["lineage_summary"]["historical_fixture_count"] >= 2

    certification_compare = client.get(
        "/ops/brain/extensions/certifications/compare",
        params={
            "left_artifact_id": filesystem_bundle_json["bundle"]["certification_artifact_id"],
            "right_artifact_id": bundle_json["bundle"]["certification_artifact_id"],
        },
    )
    assert certification_compare.status_code == 200
    certification_compare_json = certification_compare.json()
    assert certification_compare_json["diff"]["privilege_inheritance_confusion_changed"] is True
    assert certification_compare_json["diff"]["certification_lineage_depth_left"] >= 3
    assert certification_compare_json["diff"]["certification_lineage_depth_right"] >= 2
    assert certification_compare_json["diff"]["historical_certification_artifact_ids_left"]
    assert certification_compare_json["export"]["report_id"]
    assert Path(certification_compare_json["export"]["payload_path"]).exists()
    assert Path(certification_compare_json["export"]["markdown_path"]).exists()
    assert "Lineage And Restoration" in Path(certification_compare_json["export"]["markdown_path"]).read_text(encoding="utf-8")

    wrapper = client.get("/ops/brain/wrapper-surface").json()
    assert wrapper["goose"]["extension_policy_history"]["artifact_count"] >= 3
    assert wrapper["goose"]["extension_policy_rollouts"]["family_count"] >= 3
    assert wrapper["goose"]["extension_certifications"]["artifact_count"] >= 3
    assert wrapper["assimilation"]["compare_refs"]["goose_extension_policy_history_compare"].endswith("/compare")
    assert wrapper["assimilation"]["compare_refs"]["goose_extension_certification_compare"].endswith("/compare")

    visualizer = client.get("/ops/brain/visualizer/state").json()
    runtime_posture = visualizer["overlay_state"]["runtime_posture"]
    assert runtime_posture["goose_policy_history_count"] >= 3
    assert runtime_posture["goose_latest_policy_history_artifact_id"]
    assert runtime_posture["goose_latest_certification_status"]
    assert runtime_posture["goose_policy_history_compare_ref"].endswith("/compare")
    assert runtime_posture["goose_certification_compare_ref"].endswith("/compare")


def test_goose_acp_readiness_reports_fixtures_and_checks(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    health = client.get("/ops/brain/acp/health")
    assert health.status_code == 200
    health_json = health.json()
    assert "config_gap_counts" in health_json
    assert "recommended_action_counts" in health_json
    assert health_json["compatibility_fixture_count"] >= 1
    assert health_json["readiness_check_total"] >= health_json["readiness_check_pass_total"]
    assert "probe_mode_counts" in health_json
    assert "probe_status_counts" in health_json

    provider = client.get("/ops/brain/acp/providers/acp-local-coder")
    assert provider.status_code == 200
    provider_json = provider.json()
    assert provider_json["operator_summary"]["readiness_checks"]
    assert provider_json["operator_summary"]["compatibility_fixture_count"] >= 1
    assert "filesystem-bridge" in provider_json["operator_summary"]["bundle_family_compatibility"]
    assert provider_json["operator_summary"]["probe_contract_id"]
    assert provider_json["operator_summary"]["probe_mode"] in {"simulated", "live-probe-capable", "live-probe"}

    compatibility = client.post(
        "/ops/brain/acp/compatibility",
        json={
            "requested_tools": ["filesystem.write"],
            "requested_extensions": ["acp-coding-lane"],
            "subagent_mode": "parallel",
        },
    )
    assert compatibility.status_code == 200
    compatibility_json = compatibility.json()
    item = next(entry for entry in compatibility_json["items"] if entry["provider_id"] == "acp-local-coder")
    assert "acp-provider-lane" in item["supported_bundle_families"]
    assert item["compatibility_fixture_ids"]
    assert isinstance(item["config_gaps"], list)
    assert item["readiness_checks"]
    assert item["probe_mode"] in {"simulated", "live-probe-capable", "live-probe"}
    assert item["probe_contract_id"]

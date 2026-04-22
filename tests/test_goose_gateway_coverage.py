from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


def test_goose_gateway_direct_flow_persists_history_and_bundle_provenance(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    chat = client.post(
        "/chat",
        json={
            "session_id": "goose-gateway-direct",
            "message": "Create a trace anchor for direct Goose gateway coverage.",
            "rag": False,
        },
    )
    assert chat.status_code == 200
    trace_id = chat.json()["trace_id"]

    gateway = client.get(
        "/ops/brain/gateway",
        params={
            "session_id": "goose-gateway-direct",
            "requested_extensions": "mcp-filesystem",
            "requested_tools": "filesystem.readonly",
            "trigger_source": "gateway:operator-review",
        },
    )
    assert gateway.status_code == 200
    gateway_json = gateway.json()
    execution_history = gateway_json["execution_history"]
    assert gateway_json["extension_bundle_ids"] == ["mcp-filesystem"]
    assert execution_history["gateway_resolution_id"] == gateway_json["resolution_id"]
    assert trace_id in execution_history["linked_trace_ids"]
    assert execution_history["extension_bundle_ids"] == ["mcp-filesystem"]
    assert "gateway-controlled" in execution_history["flow_families"]
    assert "gateway-only" in execution_history["flow_families"]
    assert execution_history["extension_provenance"][0]["bundle_id"] == "mcp-filesystem"
    assert execution_history["extension_provenance"][0]["policy_lifecycle"]["artifact_id"]
    assert execution_history["extension_provenance"][0]["certification_artifact_id"]

    history = client.get("/ops/brain/gateway/history", params={"trigger_source": "gateway:operator-review"})
    assert history.status_code == 200
    history_json = history.json()
    assert history_json["latest_execution"]["execution_id"] == execution_history["execution_id"]
    assert history_json["latest_resolution_id"] == gateway_json["resolution_id"]
    assert history_json["latest_extension_bundle_ids"] == ["mcp-filesystem"]
    assert "gateway-controlled" in history_json["flow_family_counts"]
    assert "gateway-only" in history_json["latest_flow_families"]

    detail = client.get(f"/ops/brain/gateway/history/{execution_history['execution_id']}")
    assert detail.status_code == 200
    detail_json = detail.json()
    assert detail_json["item"]["gateway_resolution_id"] == gateway_json["resolution_id"]
    assert detail_json["report_markdown"]
    assert detail_json["item"]["metadata"]["extension_policy_history_ids"]
    assert detail_json["item"]["metadata"]["extension_certification_ids"]

    bundle = client.get("/ops/brain/extensions/mcp-filesystem")
    assert bundle.status_code == 200
    bundle_json = bundle.json()
    assert bundle_json["bundle"]["bundle_id"] == "mcp-filesystem"
    assert bundle_json["bundle"]["artifact_id"]
    assert bundle_json["detail"]["report_payload"]["bundle_id"] == "mcp-filesystem"

    wrapper = client.get("/ops/brain/wrapper-surface").json()
    goose = wrapper["goose"]
    assert goose["gateway"]["history"]["latest_resolution_id"] == gateway_json["resolution_id"]
    assert goose["extensions"]["latest_bundle_id"]

    visualizer = client.get("/ops/brain/visualizer/state").json()
    runtime_posture = visualizer["overlay_state"]["runtime_posture"]
    assert runtime_posture["goose_gateway_execution_count"] >= 1
    assert runtime_posture["goose_latest_gateway_resolution_id"] == gateway_json["resolution_id"]
    assert runtime_posture["goose_latest_gateway_extension_bundle_id"] == "mcp-filesystem"
    assert "gateway-controlled" in runtime_posture["goose_gateway_flow_family_counts"]
    assert runtime_posture["goose_latest_extension_bundle_id"]


def test_goose_acp_health_exposes_remediation_and_compatibility_actions(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    health = client.get("/ops/brain/acp/health")
    assert health.status_code == 200
    health_json = health.json()
    assert "remediation_action_counts" in health_json
    assert health_json["graceful_degradation"] is True
    assert "probe_mode_counts" in health_json
    assert "probe_status_counts" in health_json
    assert "probe_readiness_state_counts" in health_json
    assert health_json["provider_gated_count"] == health_json["provider_count"]

    provider = client.get("/ops/brain/acp/providers/acp-local-coder")
    assert provider.status_code == 200
    provider_json = provider.json()
    assert provider_json["operator_summary"]["recommended_action"]
    assert isinstance(provider_json["operator_summary"]["remediation_actions"], list)
    assert isinstance(provider_json["operator_summary"]["config_gaps"], list)
    assert provider_json["operator_summary"]["probe_mode"] in {"simulated", "live-probe-capable", "live-probe"}
    assert provider_json["operator_summary"]["probe_readiness_state"] in {"simulated", "blocked", "ready", "active"}
    assert provider_json["operator_summary"]["probe_execution_policy"] == "optional-provider-gated"
    assert isinstance(provider_json["operator_summary"]["live_probe_blockers"], list)
    assert "timeout_ms" in provider_json["operator_summary"]["bounded_probe_budget"]

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
    assert item["requested_extensions"] == ["acp-coding-lane"]
    assert item["recommended_action"]
    assert isinstance(item["remediation_actions"], list)
    assert item["probe_mode"] in {"simulated", "live-probe-capable", "live-probe"}
    assert isinstance(item["live_probe_example_ids"], list)
    assert item["probe_readiness_state"] in {"simulated", "blocked", "ready", "active"}
    assert item["probe_execution_policy"] == "optional-provider-gated"
    assert isinstance(item["live_probe_blockers"], list)


def test_goose_gateway_compare_and_flow_family_counts_are_read_only(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    baseline = client.get(
        "/ops/brain/gateway",
        params={
            "requested_extensions": "mcp-filesystem",
            "requested_tools": "filesystem.readonly",
            "trigger_source": "gateway:baseline-review",
        },
    )
    assert baseline.status_code == 200
    baseline_json = baseline.json()

    approval_heavy = client.get(
        "/ops/brain/gateway",
        params={
            "requested_extensions": "acp-coding-lane",
            "requested_tools": "shell.exec,provider.acp",
            "require_user_approval": True,
            "trigger_source": "gateway:acp-review",
        },
    )
    assert approval_heavy.status_code == 200
    approval_heavy_json = approval_heavy.json()
    assert "approval-heavy" in approval_heavy_json["execution_history"]["flow_families"]
    assert "acp-bridged" in approval_heavy_json["execution_history"]["flow_families"]

    comparison = client.get(
        "/ops/brain/gateway/history/compare",
        params={
            "left_execution_id": baseline_json["execution_history"]["execution_id"],
            "right_execution_id": approval_heavy_json["execution_history"]["execution_id"],
        },
    )
    assert comparison.status_code == 200
    comparison_json = comparison.json()
    assert "acp-bridged" in comparison_json["diff"]["flow_families_added"]
    assert comparison_json["left"]["execution_kind"] == "gateway"
    assert comparison_json["right"]["execution_kind"] == "gateway"
    assert comparison_json["export"]["report_id"]
    assert Path(comparison_json["export"]["payload_path"]).exists()
    assert Path(comparison_json["export"]["markdown_path"]).exists()
    assert "Flow And Policy Delta" in Path(comparison_json["export"]["markdown_path"]).read_text(encoding="utf-8")

    history = client.get("/ops/brain/gateway/history")
    assert history.status_code == 200
    history_json = history.json()
    assert history_json["flow_family_counts"]["gateway-controlled"] >= 2
    assert history_json["flow_family_counts"]["approval-heavy"] >= 1

    acp_compare = client.get(
        "/ops/brain/acp/providers/compare",
        params={
            "left_provider_id": "acp-local-coder",
            "right_provider_id": "acp-review-assistant",
        },
    )
    assert acp_compare.status_code == 200
    acp_compare_json = acp_compare.json()
    assert "retrieval-pack" in acp_compare_json["diff"]["bundle_families_added"]
    assert "filesystem-bridge" in acp_compare_json["diff"]["bundle_families_removed"]
    assert "probe_readiness_state_changed" in acp_compare_json["diff"]
    assert acp_compare_json["left"]["probe_execution_policy"] == "optional-provider-gated"
    assert acp_compare_json["export"]["report_id"]
    assert Path(acp_compare_json["export"]["payload_path"]).exists()
    assert Path(acp_compare_json["export"]["markdown_path"]).exists()
    assert "Probe State" in Path(acp_compare_json["export"]["markdown_path"]).read_text(encoding="utf-8")

    wrapper = client.get("/ops/brain/wrapper-surface").json()
    assert wrapper["assimilation"]["compare_refs"]["goose_acp_provider_compare"] == "/ops/brain/acp/providers/compare"
    assert "policy-lifecycle" in wrapper["assimilation"]["compare_groups"]["goose_compare"]["group_names"]

    visualizer = client.get("/ops/brain/visualizer/state").json()
    overlay = visualizer["overlay_state"]
    assert overlay["runtime_posture"]["goose_acp_compare_ref"] == "/ops/brain/acp/providers/compare"
    assert overlay["diff_catalog"]["goose_compare"]["acp_compare_endpoint"] == "/ops/brain/acp/providers/compare"
    assert overlay["diff_catalog"]["goose_compare"]["acp_provider_count"] >= 2
    assert "policy-lifecycle" in overlay["diff_catalog"]["goose_compare"]["group_names"]
    assert overlay["runtime_posture"]["goose_acp_provider_gated_count"] >= 2
    assert "simulated" in overlay["runtime_posture"]["goose_acp_probe_readiness_state_counts"]


def test_goose_bundle_privilege_escalation_paths_escalate_and_fail_closed(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    review = client.post(
        "/ops/brain/security/adversary-review",
        json={
            "subject": "gateway::bundle-escalation-attempt",
            "requested_tools": ["shell.exec", "provider.acp"],
            "requested_extensions": ["acp-coding-lane"],
            "allowed_tools": ["retrieval.query"],
            "allowed_extensions": ["local-retrieval-pack"],
            "risk_level": "high",
            "reviewer_status": "available",
            "trigger_source": "gateway:bundle-escalation",
            "approval_requested": True,
            "approval_required": True,
        },
    )
    assert review.status_code == 200
    review_json = review.json()
    assert review_json["decision"] == "escalate"
    assert "bundle-level-permission-escalation-attempt-risk" in review_json["risk_families"]
    assert review_json["fail_open_allowed"] is False

    detail = client.get(f"/ops/brain/security/adversary-reviews/{review_json['review_id']}")
    assert detail.status_code == 200
    detail_json = detail.json()
    assert "shell.exec" in detail_json["report_payload"]["requested_tools"]
    assert "acp-coding-lane" in detail_json["report_payload"]["requested_extensions"]
    assert detail_json["audit_export_payload"]["decision"] == "escalate"

    audit_export = client.get(f"/ops/brain/security/adversary-reviews/{review_json['review_id']}/audit-export")
    assert audit_export.status_code == 200
    audit_export_json = audit_export.json()
    assert audit_export_json["payload"]["decision"] == "escalate"
    assert "bundle-level-permission-escalation-attempt-risk" in audit_export_json["payload"]["risk_families"]

    baseline_review = client.post(
        "/ops/brain/security/adversary-review",
        json={
            "subject": "gateway::baseline-shell-review",
            "requested_tools": ["shell.exec"],
            "allowed_tools": ["shell.exec"],
            "risk_level": "high",
            "reviewer_status": "available",
            "trigger_source": "gateway:baseline-shell",
        },
    )
    assert baseline_review.status_code == 200
    compare = client.get(
        "/ops/brain/security/adversary-reviews/compare",
        params={
            "left_review_id": baseline_review.json()["review_id"],
            "right_review_id": review_json["review_id"],
        },
    )
    assert compare.status_code == 200
    compare_json = compare.json()
    assert "bundle-level-permission-escalation-attempt-risk" in compare_json["diff"]["risk_families_added"]
    assert compare_json["export"]["export_id"]
    assert Path(compare_json["export"]["payload_path"]).exists()
    assert Path(compare_json["export"]["markdown_path"]).exists()

    wrapper = client.get("/ops/brain/wrapper-surface").json()
    compare_refs = wrapper["goose"]["security"]["adversary_review"]["compare_refs"]
    assert compare_refs["audit_export_template"].endswith("/audit-export")
    assert compare_refs["review_compare"].endswith("/compare")

    visualizer = client.get("/ops/brain/visualizer/state").json()
    assert visualizer["overlay_state"]["runtime_posture"]["goose_latest_adversary_audit_export_id"]

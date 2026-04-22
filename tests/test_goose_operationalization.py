from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import _write_yaml, make_project


def test_goose_recipe_and_runbook_history_persist_and_surface(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    chat = client.post(
        "/chat",
        json={
            "session_id": "goose-recipe-session",
            "message": "Explain recipe-linked traceability",
            "rag": False,
        },
    )
    assert chat.status_code == 200
    trace_id = chat.json()["trace_id"]

    recipe = client.post(
        "/ops/brain/recipes/execute",
        json={
            "recipe_id": "ao-deep-research",
            "trigger_source": "manual",
            "session_id": "goose-recipe-session",
            "parameter_set": {"topic": "Gateway provenance", "depth": 2},
            "linked_trace_ids": ["trace-001"],
            "linked_subagent_ids": ["subagent-001"],
            "policy_path": [{"policy": "ask", "reason": "operator-review"}],
            "approval_path": {"decision": "ask"},
            "artifacts_produced": ["artifact://recipe/research-summary"],
            "status": "success",
        },
    )
    assert recipe.status_code == 200
    recipe_json = recipe.json()
    assert Path(recipe_json["artifact_path"]).exists()
    assert recipe_json["report"]["report_id"]
    assert trace_id in recipe_json["linked_trace_ids"]
    assert recipe_json["gateway_decision_path"]
    assert recipe_json["approval_fallback_chain"]

    runbook = client.post(
        "/ops/brain/runbooks/execute",
        json={
            "recipe_id": "runbook-retrieval-review",
            "trigger_source": "manual",
            "session_id": "goose-recipe-session",
            "parameter_set": {"candidate_id": "cand-123"},
            "linked_trace_ids": ["trace-002"],
            "linked_subagent_ids": ["subagent-002"],
            "policy_path": [{"policy": "readonly-research", "reason": "ops-review"}],
            "approval_path": {"decision": "allow"},
            "artifacts_produced": ["artifact://runbook/review-summary"],
            "status": "success",
        },
    )
    assert runbook.status_code == 200
    runbook_json = runbook.json()
    assert Path(runbook_json["artifact_path"]).exists()

    recipe_history = client.get("/ops/brain/recipes/history")
    assert recipe_history.status_code == 200
    recipe_history_json = recipe_history.json()
    assert recipe_history_json["execution_count"] >= 1
    assert recipe_history_json["latest_execution"]["execution_id"] == recipe_json["execution_id"]

    recipe_detail = client.get(f"/ops/brain/recipes/history/{recipe_json['execution_id']}")
    assert recipe_detail.status_code == 200
    assert recipe_detail.json()["report_markdown"]

    runbook_history = client.get("/ops/brain/runbooks/history")
    assert runbook_history.status_code == 200
    runbook_history_json = runbook_history.json()
    assert runbook_history_json["execution_count"] >= 1
    assert runbook_history_json["latest_execution"]["execution_id"] == runbook_json["execution_id"]

    wrapper = client.get("/ops/brain/wrapper-surface")
    assert wrapper.status_code == 200
    goose_recipes = wrapper.json()["goose"]["recipes"]
    assert goose_recipes["history"]["execution_count"] >= 1
    assert goose_recipes["runbook_history"]["execution_count"] >= 1
    assert goose_recipes["compare_refs"]["history"] == "/ops/brain/recipes/history"
    assert goose_recipes["compare_refs"]["history_compare"] == "/ops/brain/recipes/history/compare"
    assert goose_recipes["compare_refs"]["runbook_history_compare"] == "/ops/brain/runbooks/history/compare"

    visualizer = client.get("/ops/brain/visualizer/state")
    assert visualizer.status_code == 200
    runtime_posture = visualizer.json()["overlay_state"]["runtime_posture"]
    assert runtime_posture["goose_latest_recipe_execution_id"] == recipe_json["execution_id"]
    assert runtime_posture["goose_latest_runbook_execution_id"] == runbook_json["execution_id"]
    assert runtime_posture["goose_latest_recipe_report_id"] == recipe_history_json["latest_report_id"]
    assert runtime_posture["goose_latest_runbook_report_id"] == runbook_history_json["latest_report_id"]
    assert runtime_posture["goose_latest_recipe_gateway_resolution_id"] == recipe_history_json["latest_gateway_resolution_id"]


def test_goose_subagent_plan_automatically_records_execution_history(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/subagents/plan",
        json={
            "recipe_id": "ao-deep-research",
            "parent_task": "Investigate recipe-linked subagent provenance",
            "mode": "parallel",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["execution_history"]["recipe_id"] == "ao-deep-research"
    assert payload["execution_history"]["trigger_source"] == "subagent-plan:parallel"
    assert payload["execution_history"]["linked_subagent_ids"]
    assert Path(payload["execution_history"]["artifact_path"]).exists()

    history = client.get("/ops/brain/recipes/history", params={"recipe_id": "ao-deep-research"})
    assert history.status_code == 200
    history_json = history.json()
    assert history_json["execution_count"] >= 1
    assert history_json["latest_execution"]["execution_id"] == payload["execution_history"]["execution_id"]
    assert history_json["latest_report_id"] == payload["execution_history"]["report"]["report_id"]


def test_goose_subagent_privilege_confusion_escalates_and_is_linked(tmp_path: Path):
    project_root = make_project(tmp_path)
    _write_yaml(
        project_root / "runtime" / "config" / "recipes" / "privileged_confusion.yaml",
        {
            "recipe_id": "ao-privilege-confusion",
            "kind": "recipe",
            "label": "AO Privilege Confusion",
            "description": "Deliberately mismatched step tool request to validate bounded inheritance.",
            "version": "1.0",
            "ao_targets": ["ResearchAO"],
            "approved_tool_sets": ["readonly-research"],
            "steps": [
                {
                    "step_id": "unsafe-step",
                    "action": "tool-bundle",
                    "description": "Attempt to request a shell tool outside the approved tool set.",
                    "approved_tools": ["shell.exec"],
                }
            ],
        },
    )
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/subagents/plan",
        json={
            "recipe_id": "ao-privilege-confusion",
            "parent_task": "Exercise privilege confusion handling",
            "mode": "sequential",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["privilege_review"] is not None
    assert payload["privilege_review"]["decision"] == "escalate"
    assert "recipe-subagent-privilege-confusion-risk" in payload["privilege_review"]["risk_families"]
    assert payload["execution_history"]["adversary_review_report_ids"]
    assert payload["execution"]["privilege_review"]["review_id"] == payload["privilege_review"]["review_id"]


def test_goose_scheduled_history_is_persistent_and_idempotent(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    scheduled_chat = client.post(
        "/chat",
        json={
            "session_id": "scheduled-goose",
            "message": "Monitor runtime posture and flag governance drift.",
            "wrapper_mode": "scheduled-monitor",
            "rag": False,
        },
    )
    assert scheduled_chat.status_code == 200

    first = client.get("/ops/brain/agents/scheduled/history")
    second = client.get("/ops/brain/agents/scheduled/history")
    assert first.status_code == 200
    assert second.status_code == 200
    first_json = first.json()
    second_json = second.json()
    assert first_json["history_count"] >= 1
    assert second_json["history_count"] == first_json["history_count"]
    assert second_json["latest_artifact"]["artifact_id"] == first_json["latest_artifact"]["artifact_id"]

    detail = client.get(f"/ops/brain/agents/scheduled/history/{first_json['latest_artifact']['artifact_id']}")
    assert detail.status_code == 200
    detail_json = detail.json()
    assert detail_json["report_markdown"]

    wrapper = client.get("/ops/brain/wrapper-surface").json()
    scheduled = wrapper["goose"]["scheduled"]["history"]
    assert scheduled["history_count"] >= 1

    visualizer = client.get("/ops/brain/visualizer/state").json()
    runtime_posture = visualizer["overlay_state"]["runtime_posture"]
    assert runtime_posture["goose_scheduled_history_count"] >= 1
    monitor_history = client.get("/ops/brain/agents/scheduled/history", params={"workflow_id": "scheduled-monitor"}).json()
    assert runtime_posture["goose_latest_scheduled_artifact_id"] == monitor_history["latest_artifact"]["artifact_id"]


def test_goose_acp_health_and_adversary_review_operationalization_surface(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    acp_health = client.get("/ops/brain/acp/health")
    assert acp_health.status_code == 200
    acp_health_json = acp_health.json()
    assert acp_health_json["provider_count"] >= 1
    assert acp_health_json["graceful_degradation"] is True
    assert "version_compatible_count" in acp_health_json
    assert "feature_compatible_count" in acp_health_json

    provider_detail = client.get("/ops/brain/acp/providers/acp-local-coder")
    assert provider_detail.status_code == 200
    provider_detail_json = provider_detail.json()
    assert provider_detail_json["provider"]["provider_id"] == "acp-local-coder"
    assert provider_detail_json["provider"]["capabilities"]["subagent_compatibility"]["supported"] is True
    assert provider_detail_json["provider"]["diagnostic"]["version_compatible"] is True

    compatibility = client.post(
        "/ops/brain/acp/compatibility",
        json={"requested_tools": ["filesystem.write"], "subagent_mode": "parallel"},
    )
    assert compatibility.status_code == 200
    compatibility_json = compatibility.json()
    assert compatibility_json["requested_tools"] == ["filesystem.write"]
    assert compatibility_json["compatible_provider_count"] >= 0
    assert any(item["provider_id"] == "acp-local-coder" for item in compatibility_json["items"])
    assert "version_compatible" in compatibility_json["items"][0]
    assert "feature_compatibility_status" in compatibility_json["items"][0]

    gateway = client.get(
        "/ops/brain/gateway",
        params={
            "requested_tools": "shell.exec,network.external,provider.acp",
            "require_user_approval": True,
        },
    )
    assert gateway.status_code == 200
    gateway_json = gateway.json()
    review = gateway_json["adversary_review"]
    assert review["fail_open_allowed"] is False
    assert review["decision"] in {"deny", "escalate"}
    assert "shell-exec-risk" in review["risk_families"]
    assert "network-egress-risk" in review["risk_families"]
    assert "provider-bridge-risk" in review["risk_families"]
    assert "multi-step-escalation-risk" in review["risk_families"]
    assert review["report"]["report_id"]

    reviews = client.get("/ops/brain/security/adversary-reviews")
    assert reviews.status_code == 200
    reviews_json = reviews.json()
    assert reviews_json["latest_report_id"] == review["report"]["report_id"]
    assert reviews_json["family_counts"]["shell-exec-risk"] >= 1

    review_detail = client.get(f"/ops/brain/security/adversary-reviews/{review['review_id']}")
    assert review_detail.status_code == 200
    review_detail_json = review_detail.json()
    assert review_detail_json["item"]["review_id"] == review["review_id"]
    assert review_detail_json["report_markdown"]

    wrapper = client.get("/ops/brain/wrapper-surface").json()
    goose = wrapper["goose"]
    assert goose["acp"]["health"]["provider_count"] >= 1
    assert goose["acp"]["compare_refs"]["compatibility"] == "/ops/brain/acp/compatibility"
    assert goose["security"]["adversary_review"]["latest_report_id"] == review["report"]["report_id"]
    assert goose["security"]["adversary_review"]["compare_refs"]["review_compare"] == "/ops/brain/security/adversary-reviews/compare"

    visualizer = client.get("/ops/brain/visualizer/state").json()
    runtime_posture = visualizer["overlay_state"]["runtime_posture"]
    assert runtime_posture["goose_acp_ready_count"] >= 0
    assert "simulated" in runtime_posture["goose_acp_probe_mode_counts"]
    assert runtime_posture["goose_acp_version_compatible_count"] >= 0
    assert runtime_posture["goose_acp_feature_compatible_count"] >= 0
    assert runtime_posture["goose_latest_adversary_report_id"] == review["report"]["report_id"]
    assert runtime_posture["goose_adversary_family_counts"]["shell-exec-risk"] >= 1
    assert runtime_posture["goose_adversary_compare_ref"] == "/ops/brain/security/adversary-reviews/compare"

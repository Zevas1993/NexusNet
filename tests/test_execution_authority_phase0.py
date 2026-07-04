from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_graphify_dark_factory_assimilation import GRAPHIFY_REPO
from tests.test_nexus_phase1_foundation import make_project


def test_execution_authority_denies_lease_without_required_approvals(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/execution-authority/leases/request",
        json={
            "capability": "external_package_install",
            "scope": {
                "workspace_id": "default",
                "target": "graphifyy",
                "commands": ["pip install graphifyy"],
            },
            "budget": {"max_usd": 1.0, "max_minutes": 10},
            "rollback_plan": {"strategy": "delete_isolated_venv"},
            "approval_id": "",
            "approval_decision": "not_requested",
            "gateway_decision": "hold",
            "product_sweep_gate_ids": ["gateway-policy", "license-review"],
            "product_sweep_decision": "not_evaluated",
            "requested_execution": True,
            "requested_mutation": True,
        },
    )

    assert response.status_code == 200
    lease = response.json()["lease"]
    assert lease["lease_id"].startswith("lease_")
    assert lease["status"] == "blocked_missing_authority"
    assert lease["execution_allowed"] is False
    assert lease["mutation_allowed"] is False
    assert lease["required_authority"]["approval"] == "missing"
    assert lease["required_authority"]["gateway"] == "missing"
    assert lease["required_authority"]["product_sweep"] == "missing"
    assert lease["required_authority"]["expires_at"] == "missing"
    assert lease["policy_path"][0]["decision"] == "deny"
    assert lease["approval_path"]["decision"] == "not_requested"
    assert Path(lease["artifact_path"]).exists()

    eval_response = client.post(
        "/ops/brain/execution-authority/evaluate",
        json={
            "lease_id": lease["lease_id"],
            "capability": "external_package_install",
            "scope": {"workspace_id": "default", "target": "graphifyy"},
        },
    )
    assert eval_response.status_code == 200
    assert eval_response.json()["decision"]["execution_allowed"] is False
    assert eval_response.json()["decision"]["reason"] == "lease_not_granted"


def test_execution_authority_grants_expiring_scope_bound_lease_when_all_gates_pass(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/execution-authority/leases/request",
        json={
            "capability": "hook_write",
            "scope": {
                "workspace_id": "default",
                "target": "AGENTS.md",
                "allowed_paths": ["AGENTS.md", ".opencode/plugins/graphify.js"],
            },
            "expires_at": "2099-01-01T00:00:00+00:00",
            "budget": {"max_usd": 0.0, "max_minutes": 5},
            "rollback_plan": {"strategy": "reverse_patch", "artifact": "hook-write.patch"},
            "approval_id": "approval-hook-001",
            "approval_decision": "approved",
            "gateway_decision": "allow",
            "product_sweep_gate_ids": ["gateway-policy", "operator-surface-truthfulness"],
            "product_sweep_decision": "passed",
            "evidence": {"patch_artifact": "hook-write.patch", "review": "fresh_context"},
            "requested_execution": True,
            "requested_mutation": True,
        },
    )

    assert response.status_code == 200
    lease = response.json()["lease"]
    assert lease["status"] == "granted"
    assert lease["execution_allowed"] is True
    assert lease["mutation_allowed"] is True
    assert lease["required_authority"] == {
        "approval": "satisfied",
        "gateway": "satisfied",
        "product_sweep": "satisfied",
        "rollback": "satisfied",
        "budget": "satisfied",
        "expires_at": "satisfied",
    }
    assert lease["scope_hash"]
    assert lease["policy_path"][0]["decision"] == "allow"

    allowed = client.post(
        "/ops/brain/execution-authority/evaluate",
        json={
            "lease_id": lease["lease_id"],
            "capability": "hook_write",
            "scope": {
                "workspace_id": "default",
                "target": "AGENTS.md",
                "allowed_paths": ["AGENTS.md", ".opencode/plugins/graphify.js"],
            },
        },
    )
    assert allowed.status_code == 200
    assert allowed.json()["decision"]["execution_allowed"] is True
    assert allowed.json()["decision"]["mutation_allowed"] is True

    mismatched = client.post(
        "/ops/brain/execution-authority/evaluate",
        json={
            "lease_id": lease["lease_id"],
            "capability": "hook_write",
            "scope": {"workspace_id": "default", "target": ".github/workflows/deploy.yml"},
        },
    )
    assert mismatched.status_code == 200
    assert mismatched.json()["decision"]["execution_allowed"] is False
    assert mismatched.json()["decision"]["reason"] == "scope_mismatch"


def test_context_graph_and_factory_surfaces_require_execution_authority(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    graph = client.post(
        "/ops/brain/context-graph/index-plan",
        json={
            "source": {"source_name": "Graphify", "source_url": GRAPHIFY_REPO},
            "corpus_root": str(project_root),
            "content_kinds": ["code", "docs", "video"],
            "assistant_platforms": ["codex", "opencode"],
        },
    ).json()["record"]
    assert graph["execution_authority"]["required"] is True
    assert graph["execution_authority"]["execution_allowed"] is False
    assert {
        "external_package_install",
        "hook_write",
        "context_graph_semantic_extraction",
    } <= set(graph["execution_authority"]["required_capabilities"])

    factory = client.post(
        "/ops/brain/factory-orchestration/pr-validation",
        json={
            "pr_ref": "repo#80",
            "required_validation_profiles": ["unit", "agent_browser_e2e"],
            "browser_validation_required": True,
            "start_service_status": "failed",
            "deployment_target": "production",
        },
    ).json()["record"]
    assert factory["execution_authority"]["required"] is True
    assert factory["execution_authority"]["execution_allowed"] is False
    assert {
        "autonomous_agent_execution",
        "pr_push",
        "pr_merge",
        "deployment",
    } <= set(factory["execution_authority"]["required_capabilities"])


def test_execution_authority_status_surfaces_and_telemetry(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    client.post(
        "/ops/brain/execution-authority/leases/request",
        json={
            "capability": "provider_registration",
            "scope": {"workspace_id": "default", "provider_id": "lm-studio"},
            "budget": {"max_usd": 0.0},
            "rollback_plan": {"strategy": "remove_provider_scorecard"},
            "approval_decision": "not_requested",
            "gateway_decision": "hold",
            "product_sweep_gate_ids": ["runtime-certification"],
            "product_sweep_decision": "not_evaluated",
        },
    )

    authority = client.get("/ops/brain/execution-authority")
    assert authority.status_code == 200
    assert authority.json()["lease_count"] == 1
    assert authority.json()["execution_allowed_count"] == 0
    assert authority.json()["capability_counts"]["provider_registration"] == 1

    product = client.get("/ops/brain/product-sweep/status")
    assert product.status_code == 200
    assert "execution_authority" in product.json()["status_surfaces"]
    assert product.json()["status_surfaces"]["execution_authority"]["execution_allowed_count"] == 0

    assimilation = client.get("/ops/brain/assimilation/status")
    assert assimilation.status_code == 200
    assert "execution_authority" in assimilation.json()

    telemetry = client.get("/ops/brain/telemetry/normalized")
    assert telemetry.status_code == 200
    assert telemetry.json()["span_kind_counts"]["execution_authority"] >= 1

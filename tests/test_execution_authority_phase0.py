from __future__ import annotations

import hashlib
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
    assert lease["artifact_ref"].startswith("execution-authority://lease_")
    assert lease["artifact_available"] is True
    assert "artifact_path" not in lease
    assert "scope" not in lease
    assert "budget" not in lease
    assert "rollback_plan" not in lease
    assert "evidence" not in lease
    assert "telemetry_trace_ids" not in lease

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
    assert "artifact_path" not in eval_response.json()["lease"]


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


def test_execution_authority_public_surfaces_redact_internal_artifact_and_scope_paths(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    private_path = str(project_root / "private" / "candidate.patch")

    requested = client.post(
        "/ops/brain/execution-authority/leases/request",
        json={
            "capability": "file_write",
            "scope": {"workspace_path": private_path, "target": "candidate.patch"},
            "expires_at": "2099-01-01T00:00:00+00:00",
            "budget": {"max_usd": 0.0, "max_minutes": 1},
            "rollback_plan": {"strategy": "reverse_patch", "artifact_path": private_path},
            "approval_id": "approval-private-path",
            "approval_decision": "approved",
            "gateway_decision": "allow",
            "product_sweep_gate_ids": ["authority-privacy"],
            "product_sweep_decision": "passed",
            "evidence": {"source_path": private_path},
            "requested_execution": True,
            "requested_mutation": True,
            "linked_trace_ids": ["trace-private-path"],
        },
    )

    assert requested.status_code == 200
    public_lease = requested.json()["lease"]
    lease_id = public_lease["lease_id"]
    assert private_path not in repr(public_lease)
    assert "artifact_path" not in public_lease
    assert {"scope", "budget", "rollback_plan", "evidence", "telemetry_trace_ids"}.isdisjoint(public_lease)
    assert public_lease["artifact_ref"] == f"execution-authority://{lease_id}"

    internal_lease = client.app.state.services.brain_execution_authority._load(lease_id)
    assert Path(internal_lease["artifact_path"]).exists()
    assert internal_lease["scope"]["workspace_path"] == private_path
    assert internal_lease["rollback_plan"]["artifact_path"] == private_path

    evaluated = client.post(
        "/ops/brain/execution-authority/evaluate",
        json={
            "lease_id": lease_id,
            "capability": "file_write",
            "scope": {"workspace_path": private_path, "target": "candidate.patch"},
            "linked_trace_ids": ["trace-private-path"],
        },
    )
    assert evaluated.status_code == 200
    assert private_path not in repr(evaluated.json())
    assert "artifact_path" not in evaluated.json()["lease"]

    summary = client.get("/ops/brain/execution-authority")
    assert summary.status_code == 200
    assert private_path not in repr(summary.json())
    assert "artifact_path" not in summary.json()["latest_lease"]

    compact = client.get("/ops/brain/product-sweep/status")
    assert compact.status_code == 200
    assert private_path not in repr(compact.json()["status_surfaces"]["execution_authority"])


def test_execution_authority_lease_gates_real_read_only_tool_execution(tmp_path: Path):
    project_root = make_project(tmp_path)
    (project_root / "tool-readme.txt").write_text("nexus tool surface", encoding="utf-8")
    (project_root / "other.txt").write_text("not lease scoped", encoding="utf-8")
    client = TestClient(create_app(str(project_root)))
    scope = {
        "tool_ref": "fs",
        "action_type": "read",
        "target": "tool-readme.txt",
        "sandbox_root_digest": hashlib.sha256(str(project_root.resolve()).encode("utf-8")).hexdigest(),
    }

    lease_response = client.post(
        "/ops/brain/execution-authority/leases/request",
        json={
            "capability": "deterministic_tool_boundary",
            "scope": scope,
            "expires_at": "2099-01-01T00:00:00+00:00",
            "budget": {"max_usd": 0.0, "max_minutes": 1},
            "rollback_plan": {"strategy": "no-mutation-readonly"},
            "approval_id": "approval::tool-readonly",
            "approval_decision": "approved",
            "gateway_decision": "allow",
            "product_sweep_gate_ids": ["tool-readonly"],
            "product_sweep_decision": "passed",
            "requested_execution": True,
            "requested_mutation": False,
        },
    )
    assert lease_response.status_code == 200
    lease_id = lease_response.json()["lease"]["lease_id"]

    executed = client.post(
        "/ops/brain/tools/actions/execute",
        json={
            "action_id": "api-read-1",
            "tool_ref": "fs",
            "action_type": "read",
            "target": "tool-readme.txt",
            "evidence_refs": ["ev://tool-read"],
            "lease_id": lease_id,
        },
    )
    assert executed.status_code == 200
    assert executed.json()["executed"] is True
    assert executed.json()["result"]["text"] == "nexus tool surface"

    summary = client.get("/ops/brain/canon/tool-action-harness")
    assert summary.status_code == 200
    latest = summary.json()["latest_execution"]
    assert summary.json()["execution_count"] == 1
    assert latest["raw_content_included"] is False
    assert "result" not in latest
    assert "nexus tool surface" not in repr(latest)

    mismatched = client.post(
        "/ops/brain/tools/actions/execute",
        json={
            "action_id": "api-read-2",
            "tool_ref": "fs",
            "action_type": "read",
            "target": "other.txt",
            "evidence_refs": ["ev://tool-read"],
            "lease_id": lease_id,
        },
    )
    assert mismatched.status_code == 200
    assert mismatched.json()["executed"] is False
    assert "execution_authority::scope_mismatch" in mismatched.json()["findings"]


def test_control_panel_tool_lane_distinguishes_plans_from_real_readonly_execution(tmp_path: Path):
    app_js = (Path(__file__).resolve().parents[1] / "ui" / "control-panel" / "app.js").read_text(
        encoding="utf-8"
    )

    assert "executions ${tools.execution_count || 0}" in app_js
    assert "tools.latest_execution" in app_js

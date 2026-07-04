from __future__ import annotations

import shutil
from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.agents import SandboxAgentFactory, SandboxAgentFactoryRunRequest
from tests.test_nexus_phase1_foundation import make_project


def _project_with_control_panel(tmp_path: Path) -> Path:
    project_root = make_project(tmp_path)
    source_control_panel = Path(__file__).resolve().parents[1] / "ui" / "control-panel"
    shutil.copytree(source_control_panel, project_root / "ui" / "control-panel")
    return project_root


def test_sandbox_agent_factory_creates_afk_manifest_and_artifact(tmp_path: Path):
    factory = SandboxAgentFactory(artifacts_dir=tmp_path)

    result = factory.start(
        SandboxAgentFactoryRunRequest(
            session_id="sandbox-session",
            backlog_ref="github:issues?label=sandcastle",
            target_branch="main",
            task_ids=["NN-101", "NN-102"],
            agent_profile="claude-code",
            sandbox_provider="docker",
            workflow_template="parallel-planner-review-merge",
            max_parallel_agents=2,
            prompts={"planner": "select unblocked work", "implementer": "implement and test"},
            required_checks=["pytest tests/test_sandbox_agent_factory.py -q"],
        )
    )

    assert result["status_label"] == "LOCKED CANON"
    assert result["surface_id"] == "sandbox-agent-factory"
    assert result["lifecycle_state"] == "planned"
    assert result["manifest"]["worktree_strategy"] == "one-worktree-per-task"
    assert result["manifest"]["sandbox_provider"] == "docker"
    assert result["manifest"]["merge_policy"] == "reviewed-tests-pass-policy-clean"
    assert [block["role"] for block in result["blocks"]] == ["planner", "implementer", "reviewer", "merger"]
    assert result["policy_scan"]["summary"]["allow_merge"] is True
    assert {"run.created", "planner.queued", "implementers.parallelized", "reviewer.queued", "merger.gated"}.issubset(
        {event["event_type"] for event in result["events"]}
    )
    assert Path(result["artifact_path"]).exists()

    summary = factory.summary(session_id="sandbox-session")
    assert summary["runtime_state"] == "live-bound"
    assert summary["latest_run"]["run_id"] == result["run_id"]
    assert summary["operator_actions"]["create_run"]["endpoint"] == "/ops/brain/sandbox-agent-factory/runs"


def test_sandbox_agent_factory_attaches_codegraph_manifest(tmp_path: Path):
    factory = SandboxAgentFactory(artifacts_dir=tmp_path)

    result = factory.start(
        SandboxAgentFactoryRunRequest(
            session_id="sandbox-codegraph",
            backlog_ref="github:issues?label=sandcastle",
            target_branch="main",
            task_ids=["NN-301"],
            required_checks=["pytest -q"],
        )
    )

    # The plan-stage run records a codegraph manifest through NexusNet's own CodegraphGate, and
    # because that manifest is allowed, the code_change policy rule no longer hard-fails the run.
    assert result["lifecycle_state"] == "planned"
    assert result["codegraph_manifest"]["status"] == "allowed"
    assert result["codegraph_manifest"]["manifest_id"].startswith("codegraph::sandbox-factory::")
    assert result["policy_scan"]["summary"]["allow_merge"] is True
    assert "code_change_requires_codegraph_manifest" not in {
        finding["rule_id"] for finding in result["policy_scan"]["findings"]
    }


def test_sandbox_agent_factory_blocks_on_stale_codegraph_index(tmp_path: Path):
    factory = SandboxAgentFactory(artifacts_dir=tmp_path)

    # Operator supplies real graph evidence whose indexed commit is stale and impact is HIGH;
    # the same internal CodegraphGate must refuse to vouch for the plan, leaving the code_change
    # target without a manifest ref so the policy gate blocks the run.
    result = factory.start(
        SandboxAgentFactoryRunRequest(
            session_id="sandbox-stale-graph",
            backlog_ref="github:issues?label=sandcastle",
            target_branch="main",
            task_ids=["NN-401"],
            required_checks=["pytest -q"],
            metadata={
                "codegraph": {
                    "run_kind": "code_edit",
                    "indexed_commit": "abc",
                    "worktree_commit": "def",
                    "impact_risk": "HIGH",
                }
            },
        )
    )

    assert result["codegraph_manifest"]["status"] == "blocked"
    assert result["lifecycle_state"] == "blocked"
    assert result["policy_scan"]["summary"]["allow_merge"] is False


def test_sandbox_agent_factory_blocks_unsafe_permissions(tmp_path: Path):
    factory = SandboxAgentFactory(artifacts_dir=tmp_path)

    result = factory.start(
        {
            "session_id": "sandbox-block-session",
            "backlog_ref": "github:issues?label=sandcastle",
            "target_branch": "main",
            "task_ids": ["NN-unsafe"],
            "agent_profile": "claude-code",
            "sandbox_provider": "docker",
            "workflow_template": "parallel-planner-review-merge",
            "requested_permissions": ["host_home_write", "network_unrestricted", "merge_without_review"],
            "required_checks": [],
        }
    )

    assert result["lifecycle_state"] == "blocked"
    assert {finding["rule_id"] for finding in result["immune_findings"]} == {
        "host_home_write_blocked",
        "network_unrestricted_blocked",
        "merge_without_review_blocked",
    }
    assert result["policy_scan"]["summary"]["active_hard_fail_count"] >= 1
    assert any(event["event_type"] == "run.blocked" for event in result["events"])


def test_sandbox_agent_factory_blocks_afk_run_from_upstream_aitune_gate(tmp_path: Path):
    factory = SandboxAgentFactory(artifacts_dir=tmp_path)

    result = factory.start(
        SandboxAgentFactoryRunRequest(
            session_id="sandbox-upstream-blocked",
            backlog_ref="github:issues?label=sandcastle",
            target_branch="main",
            task_ids=["NN-runtime-blocked"],
            agent_profile="codex",
            sandbox_provider="docker",
            workflow_template="parallel-planner-review-merge",
            max_parallel_agents=1,
            required_checks=["pytest tests/test_sandbox_agent_factory.py -q"],
            upstream_aitune_gate={
                "status": "blocked-upstream-gate",
                "can_execute_here": False,
                "readiness_blockers": ["sandbox_runtime_not_validated"],
            },
        )
    )

    assert result["lifecycle_state"] == "blocked-upstream-gate"
    assert result["runtime_state"] == "degraded"
    assert result["upstream_aitune_gate"]["blockers"] == ["sandbox_runtime_not_validated"]
    assert result["policy_scan"]["summary"]["allow_merge"] is False
    assert all(block["status"] == "blocked-upstream-gate" for block in result["blocks"])
    assert any(event["event_type"] == "upstream_aitune_gate_blocked" for event in result["events"])

    summary = factory.summary(session_id="sandbox-upstream-blocked")
    assert summary["runtime_state"] == "degraded"
    assert summary["blocked_count"] == 1


def test_sandbox_agent_factory_api_and_control_panel_surface(tmp_path: Path):
    project_root = _project_with_control_panel(tmp_path)
    client = TestClient(create_app(str(project_root)))

    scorecard = client.get("/ops/brain/canon/sandbox-agent-factory")
    assert scorecard.status_code == 200
    scorecard_payload = scorecard.json()
    assert scorecard_payload["surface_id"] == "sandbox-agent-factory"
    assert scorecard_payload["control_panel_label"] == "Sandbox Agent Factory"
    assert "planner_implementer_reviewer_merger_flow" in scorecard_payload["required_controls"]

    run = client.post(
        "/ops/brain/sandbox-agent-factory/runs",
        json={
            "session_id": "sandbox-api-session",
            "backlog_ref": "github:issues?label=sandcastle",
            "target_branch": "main",
            "task_ids": ["NN-201"],
            "agent_profile": "codex",
            "sandbox_provider": "docker",
            "workflow_template": "parallel-planner-review-merge",
            "max_parallel_agents": 1,
            "required_checks": ["python -m pytest tests/test_sandbox_agent_factory.py -q"],
        },
    )
    assert run.status_code == 200
    run_payload = run.json()
    assert run_payload["lifecycle_state"] == "planned"

    summary = client.get("/ops/brain/sandbox-agent-factory", params={"session_id": "sandbox-api-session"})
    assert summary.status_code == 200
    assert summary.json()["latest_run"]["run_id"] == run_payload["run_id"]

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Sandbox Agent Factory" in ui.text
    assert "sandboxAgentFactoryScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderSandboxAgentFactoryScorecard" in app_js
    assert "/ops/brain/canon/sandbox-agent-factory" in app_js


def test_sandcastle_assimilation_target_registered_in_scorecard(tmp_path: Path):
    project_root = _project_with_control_panel(tmp_path)
    client = TestClient(create_app(str(project_root)))

    payload = client.get("/ops/brain/canon/assimilation-targets").json()

    assert payload["coverage_summary"]["target_count"] == 10
    target = next(item for item in payload["targets"] if item["target_id"] == "sandbox-agent-factory")
    assert target["label"] == "Sandcastle-Style AFK Sandbox Agent Factory"
    assert target["implementation_state"] == "v0-runtime-bound"
    assert "planner_implementer_reviewer_merger_flow" in target["required_controls"]
    assert "merge_back_policy_gate" in target["required_controls"]
    assert any("sandbox-agent-factory" in ref for ref in target["endpoint_refs"])

    source_ids = {source["source_id"] for source in payload["source_refs"]}
    assert {"mattpocock-sandcastle", "sandcastle-sourcepulse", "sandcastle-devcontainer-gist"}.issubset(source_ids)

    detail = client.get("/ops/brain/assimilation-targets/sandbox-agent-factory").json()
    assert detail["target"]["operator_contract"]["control_panel_card"] == "Sandbox Agent Factory"

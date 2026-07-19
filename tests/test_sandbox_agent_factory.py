from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.agents import SandboxAgentFactory, SandboxAgentFactoryRunRequest
from nexusnet.agents.sandbox_factory import _container_command
from tests.test_nexus_phase1_foundation import make_project


def _project_with_control_panel(tmp_path: Path) -> Path:
    project_root = make_project(tmp_path)
    source_control_panel = Path(__file__).resolve().parents[1] / "ui" / "control-panel"
    shutil.copytree(source_control_panel, project_root / "ui" / "control-panel")
    return project_root


def _docker_engine_available() -> bool:
    if shutil.which("docker") is None:
        return False
    return subprocess.run(
        ["docker", "info"], capture_output=True, text=True, timeout=10, check=False
    ).returncode == 0


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


def test_sandbox_agent_factory_executes_local_dev_command_with_bounded_evidence(tmp_path: Path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    factory = SandboxAgentFactory(artifacts_dir=tmp_path, allowed_workspace_root=tmp_path)
    planned = factory.start(
        SandboxAgentFactoryRunRequest(
            session_id="local-exec",
            backlog_ref="local:test",
            task_ids=["NN-local"],
            sandbox_provider="local-devcontainer",
            required_checks=["python smoke"],
        )
    )

    execution = factory.execute_local(
        run_id=planned["run_id"],
        workspace=workspace,
        command=[sys.executable, "-c", "from pathlib import Path; Path('proof.txt').write_text('ok'); print('done')"],
        timeout_seconds=10,
    )

    assert execution["state"] == "completed"
    assert execution["return_code"] == 0
    assert execution["stdout"] == "done\n"
    assert (workspace / "proof.txt").read_text(encoding="utf-8") == "ok"
    assert Path(execution["evidence_path"]).exists()


def test_sandbox_agent_factory_rejects_workspace_outside_allowed_root(tmp_path: Path):
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    factory = SandboxAgentFactory(artifacts_dir=tmp_path / "artifacts", allowed_workspace_root=allowed)
    planned = factory.start(
        SandboxAgentFactoryRunRequest(
            session_id="escape",
            backlog_ref="local:test",
            task_ids=["NN-escape"],
            sandbox_provider="local-devcontainer",
            required_checks=["python smoke"],
        )
    )

    with pytest.raises(PermissionError, match="outside allowed root"):
        factory.execute_local(
            run_id=planned["run_id"],
            workspace=outside,
            command=[sys.executable, "-c", "print('unsafe')"],
        )


def test_sandbox_agent_factory_creates_real_worktree_and_passes_executable_merge_gates(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "nexusnet@example.test"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "NexusNet Test"], cwd=repo, check=True)
    (repo / "base.txt").write_text("base\n", encoding="utf-8")
    subprocess.run(["git", "add", "base.txt"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "base"], cwd=repo, check=True, capture_output=True, text=True)

    factory = SandboxAgentFactory(
        artifacts_dir=tmp_path / "artifacts",
        allowed_workspace_root=tmp_path,
    )
    planned = factory.start(
        SandboxAgentFactoryRunRequest(
            session_id="worktree-merge-gate",
            backlog_ref="local:test",
            target_branch="main",
            task_ids=["NN-shared-prefix-alpha", "NN-shared-prefix-beta"],
            sandbox_provider="local-devcontainer",
            required_checks=["python-smoke"],
        )
    )

    worktree = factory.create_worktree(
        run_id=planned["run_id"],
        repo_root=repo,
        task_id="NN-shared-prefix-alpha",
    )
    worktree_path = Path(worktree["worktree_path"])
    assert worktree_path.is_dir()
    assert worktree["branch"].startswith("codex/sandbox-agent/")
    second_worktree = factory.create_worktree(
        run_id=planned["run_id"],
        repo_root=repo,
        task_id="NN-shared-prefix-beta",
    )
    assert second_worktree["branch"] != worktree["branch"]
    assert second_worktree["worktree_path"] != worktree["worktree_path"]

    (worktree_path / "feature.txt").write_text("implemented\n", encoding="utf-8")
    subprocess.run(["git", "add", "feature.txt"], cwd=worktree_path, check=True)
    subprocess.run(["git", "commit", "-m", "implement task"], cwd=worktree_path, check=True, capture_output=True, text=True)

    gate = factory.evaluate_merge_gate(
        run_id=planned["run_id"],
        task_id="NN-shared-prefix-alpha",
        review_approved=True,
        rollback_ref="main",
        check_commands={"python-smoke": [sys.executable, "-c", "print('check-ok')"]},
        timeout_seconds=30,
    )

    assert gate["decision"] == "merge_ready"
    assert gate["checks_passed"] is True
    assert gate["review_approved"] is True
    assert gate["policy_clean"] is True
    assert gate["worktree_clean"] is True
    assert gate["commits_ahead"] == 1
    assert gate["check_receipts"][0]["stdout"] == "check-ok\n"
    assert Path(gate["evidence_path"]).exists()


def test_container_command_enforces_isolation_and_resource_limits(tmp_path: Path):
    workspace = (tmp_path / "workspace").resolve()
    workspace.mkdir()

    command = _container_command(
        runtime="docker",
        workspace=workspace,
        image="python:3.11-alpine",
        command=["python", "-c", "print('ok')"],
    )

    assert command[:3] == ["docker", "run", "--rm"]
    assert ["--network", "none"] == command[command.index("--network") : command.index("--network") + 2]
    assert "--read-only" in command
    assert ["--cap-drop", "ALL"] == command[command.index("--cap-drop") : command.index("--cap-drop") + 2]
    assert ["--security-opt", "no-new-privileges"] == command[
        command.index("--security-opt") : command.index("--security-opt") + 2
    ]
    assert any(item.startswith("type=bind,source=") and item.endswith(",target=/workspace") for item in command)
    assert command[-4:] == ["python:3.11-alpine", "python", "-c", "print('ok')"]


@pytest.mark.skipif(not _docker_engine_available(), reason="Docker engine is unavailable")
def test_sandbox_agent_factory_executes_real_docker_container(tmp_path: Path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    factory = SandboxAgentFactory(artifacts_dir=tmp_path, allowed_workspace_root=tmp_path)
    planned = factory.start(
        SandboxAgentFactoryRunRequest(
            session_id="docker-exec",
            backlog_ref="local:test",
            task_ids=["NN-docker"],
            sandbox_provider="docker",
            required_checks=["container smoke"],
        )
    )

    execution = factory.execute_container(
        run_id=planned["run_id"],
        workspace=workspace,
        image="python:3.11-alpine",
        command=["python", "-c", "from pathlib import Path; Path('container-proof.txt').write_text('container-ok'); print('docker-done')"],
        timeout_seconds=120,
    )

    assert execution["state"] == "completed"
    assert execution["stdout"] == "docker-done\n"
    assert (workspace / "container-proof.txt").read_text(encoding="utf-8") == "container-ok"
    assert execution["execution_boundary"] == "container-isolated"


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


def test_sandbox_agent_factory_api_executes_local_dev_run(tmp_path: Path):
    project_root = _project_with_control_panel(tmp_path)
    workspace = project_root / "runtime" / "local-exec"
    workspace.mkdir(parents=True)
    client = TestClient(create_app(str(project_root)))
    planned = client.post(
        "/ops/brain/sandbox-agent-factory/runs",
        json={
            "session_id": "sandbox-local-api",
            "backlog_ref": "local:test",
            "task_ids": ["NN-local-api"],
            "sandbox_provider": "local-devcontainer",
            "required_checks": ["python smoke"],
        },
    ).json()

    executed = client.post(
        f"/ops/brain/sandbox-agent-factory/runs/{planned['run_id']}/execute-local",
        json={
            "workspace": str(workspace),
            "command": [sys.executable, "-c", "print('api-done')"],
            "timeout_seconds": 10,
        },
    )

    assert executed.status_code == 200
    assert executed.json()["state"] == "completed"
    assert executed.json()["stdout"] == "api-done\n"


def test_sandbox_agent_factory_api_creates_worktree_and_evaluates_merge_gate(tmp_path: Path):
    project_root = _project_with_control_panel(tmp_path)
    repo = project_root / "runtime" / "worktree-repo"
    repo.mkdir(parents=True)
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "nexusnet@example.test"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "NexusNet Test"], cwd=repo, check=True)
    (repo / "base.txt").write_text("base\n", encoding="utf-8")
    subprocess.run(["git", "add", "base.txt"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "base"], cwd=repo, check=True, capture_output=True, text=True)
    client = TestClient(create_app(str(project_root)))
    planned = client.post(
        "/ops/brain/sandbox-agent-factory/runs",
        json={
            "session_id": "sandbox-worktree-api",
            "backlog_ref": "local:test",
            "target_branch": "main",
            "task_ids": ["NN-worktree-api"],
            "sandbox_provider": "local-devcontainer",
            "required_checks": ["python-smoke"],
        },
    ).json()

    worktree_response = client.post(
        f"/ops/brain/sandbox-agent-factory/runs/{planned['run_id']}/worktrees",
        json={"repo_root": str(repo), "task_id": "NN-worktree-api"},
    )
    assert worktree_response.status_code == 200, worktree_response.text
    worktree_path = Path(worktree_response.json()["worktree_path"])
    (worktree_path / "api-feature.txt").write_text("implemented\n", encoding="utf-8")
    subprocess.run(["git", "add", "api-feature.txt"], cwd=worktree_path, check=True)
    subprocess.run(["git", "commit", "-m", "api feature"], cwd=worktree_path, check=True, capture_output=True, text=True)

    gate_response = client.post(
        f"/ops/brain/sandbox-agent-factory/runs/{planned['run_id']}/merge-gates",
        json={
            "task_id": "NN-worktree-api",
            "review_approved": True,
            "rollback_ref": "main",
            "check_commands": {"python-smoke": [sys.executable, "-c", "print('api-check-ok')"]},
            "timeout_seconds": 30,
        },
    )

    assert gate_response.status_code == 200
    assert gate_response.json()["decision"] == "merge_ready"
    assert gate_response.json()["check_receipts"][0]["stdout"] == "api-check-ok\n"


@pytest.mark.skipif(not _docker_engine_available(), reason="Docker engine is unavailable")
def test_sandbox_agent_factory_api_executes_docker_run(tmp_path: Path):
    project_root = _project_with_control_panel(tmp_path)
    workspace = project_root / "runtime" / "docker-exec"
    workspace.mkdir(parents=True)
    client = TestClient(create_app(str(project_root)))
    planned = client.post(
        "/ops/brain/sandbox-agent-factory/runs",
        json={
            "session_id": "sandbox-docker-api",
            "backlog_ref": "local:test",
            "task_ids": ["NN-docker-api"],
            "sandbox_provider": "docker",
            "required_checks": ["container smoke"],
        },
    ).json()

    executed = client.post(
        f"/ops/brain/sandbox-agent-factory/runs/{planned['run_id']}/execute-container",
        json={
            "workspace": str(workspace),
            "image": "python:3.11-alpine",
            "command": ["python", "-c", "print('container-api-done')"],
            "timeout_seconds": 120,
        },
    )

    assert executed.status_code == 200
    assert executed.json()["state"] == "completed"
    assert executed.json()["stdout"] == "container-api-done\n"


def test_sandcastle_assimilation_target_registered_in_scorecard(tmp_path: Path):
    project_root = _project_with_control_panel(tmp_path)
    client = TestClient(create_app(str(project_root)))

    payload = client.get("/ops/brain/canon/assimilation-targets").json()

    assert payload["coverage_summary"]["target_count"] == 10
    target = next(item for item in payload["targets"] if item["target_id"] == "sandbox-agent-factory")
    assert target["label"] == "Sandcastle-Style AFK Sandbox Agent Factory"
    assert target["implementation_state"] == "runtime-executable-local-and-container"
    assert "planner_implementer_reviewer_merger_flow" in target["required_controls"]
    assert "merge_back_policy_gate" in target["required_controls"]
    assert any("sandbox-agent-factory" in ref for ref in target["endpoint_refs"])

    source_ids = {source["source_id"] for source in payload["source_refs"]}
    assert {"mattpocock-sandcastle", "sandcastle-sourcepulse", "sandcastle-devcontainer-gist"}.issubset(source_ids)

    detail = client.get("/ops/brain/assimilation-targets/sandbox-agent-factory").json()
    assert detail["target"]["operator_contract"]["control_panel_card"] == "Sandbox Agent Factory"

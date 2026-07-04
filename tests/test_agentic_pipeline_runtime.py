from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.agents.pipelines import AgenticPipelineRequest, AgenticPipelineRuntime, PipelineBlockSpec
from tests.test_nexus_phase1_foundation import make_project


def test_agentic_pipeline_runtime_creates_manifest_events_artifact_and_policy_gate(tmp_path: Path):
    runtime = AgenticPipelineRuntime(artifacts_dir=tmp_path)

    run = runtime.start(
        AgenticPipelineRequest(
            session_id="pipeline-session",
            pipeline_id="canon-build-pipeline",
            goal="Build a governed NexusNet feature from canon research.",
            profile_id="nexusbrain-governed-dev",
            requested_by="NexusBrain",
            blocks=[
                PipelineBlockSpec(block_id="planner", role="planner", expected_output="implementation manifest"),
                PipelineBlockSpec(block_id="policy-gate", role="policy", expected_output="policy scan"),
                PipelineBlockSpec(block_id="manager-review", role="reviewer", expected_output="promotion decision"),
            ],
            policy_targets=[
                {
                    "target_id": "tool::unsafe-write",
                    "target_type": "tool_execution",
                    "metadata": {"write_enabled": True, "sandboxed": False},
                }
            ],
        )
    )

    assert run["status_label"] == "LOCKED CANON"
    assert run["run_id"].startswith("agentic_pipeline_")
    assert run["authority"] == "NexusBrain"
    assert run["lifecycle_state"] == "blocked_by_policy"
    assert run["manifest"]["fresh_context_per_block"] is True
    assert run["manifest"]["artifact_mode"] == "repo-disk-ledger"
    assert run["manifest"]["branch_policy"]["isolated_worktree_required"] is True
    assert [block["block_id"] for block in run["blocks"]] == ["planner", "policy-gate", "manager-review"]
    assert all(block["context_mode"] == "fresh-subprocess" for block in run["blocks"])
    assert run["policy_scan"]["summary"]["active_hard_fail_count"] == 1
    assert run["policy_scan"]["findings"][0]["rule_id"] == "write_tool_requires_sandbox"
    assert {"pipeline_created", "block_started", "block_completed", "policy_scan_completed", "pipeline_blocked"}.issubset(
        {event["event_type"] for event in run["events"]}
    )
    assert Path(run["artifact_path"]).exists()

    summary = runtime.summary()
    assert summary["status_label"] == "LOCKED CANON"
    assert summary["latest_run"]["run_id"] == run["run_id"]
    assert summary["blocked_count"] == 1
    assert summary["operator_actions"]["create_run"]["endpoint"] == "/ops/brain/agentic-pipelines/runs"


def test_agentic_pipeline_runtime_blocks_before_start_from_upstream_aitune_gate(tmp_path: Path):
    runtime = AgenticPipelineRuntime(artifacts_dir=tmp_path)

    run = runtime.start(
        AgenticPipelineRequest(
            session_id="pipeline-upstream-blocked",
            pipeline_id="runtime-gated-pipeline",
            goal="Run a governed runtime operation only when QES evidence is clear.",
            blocks=[
                PipelineBlockSpec(block_id="executor", role="executor", expected_output="runtime output"),
                PipelineBlockSpec(block_id="reviewer", role="reviewer", expected_output="review decision"),
            ],
            policy_targets=[
                {
                    "target_id": "memory::approved",
                    "target_type": "memory_update",
                    "metadata": {"provenance_refs": ["docs/source.md"]},
                }
            ],
            upstream_aitune_gate={
                "status": "blocked-upstream-gate",
                "can_execute_here": False,
                "readiness_blockers": ["pipeline_runtime_not_validated"],
            },
        )
    )

    assert run["lifecycle_state"] == "blocked_by_upstream_aitune_gate"
    assert run["runtime_state"] == "degraded"
    assert run["upstream_aitune_gate"]["blockers"] == ["pipeline_runtime_not_validated"]
    assert run["policy_scan"]["summary"]["allow_merge"] is False
    assert all(block["status"] == "blocked-upstream-gate" for block in run["blocks"])
    assert "block_started" not in {event["event_type"] for event in run["events"]}
    assert "upstream_aitune_gate_blocked" in {event["event_type"] for event in run["events"]}

    summary = runtime.summary(session_id="pipeline-upstream-blocked")
    assert summary["runtime_state"] == "degraded"
    assert summary["blocked_count"] == 1


def test_agentic_pipeline_api_blackbox_and_control_panel_surface(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/agentic-pipelines/runs",
        json={
            "session_id": "pipeline-api-session",
            "pipeline_id": "self-improvement-pipeline",
            "goal": "Turn an approved improvement candidate into a governed implementation plan.",
            "profile_id": "nexusbrain-governed-dev",
            "requested_by": "NexusBrain",
            "blocks": [
                {"block_id": "research", "role": "researcher", "expected_output": "source brief"},
                {"block_id": "planner", "role": "planner", "expected_output": "implementation plan"},
                {"block_id": "policy-gate", "role": "policy", "expected_output": "policy scan"},
                {"block_id": "manager-review", "role": "reviewer", "expected_output": "review decision"},
            ],
            "policy_targets": [
                {
                    "target_id": "memory::approved",
                    "target_type": "memory_update",
                    "metadata": {"provenance_refs": ["docs/NEXUSNET_YOUTUBE_ASSIMILATION_INTAKE_2026-04-30.md"]},
                }
            ],
        },
    )

    assert response.status_code == 200
    run = response.json()
    assert run["lifecycle_state"] == "completed"
    assert run["policy_scan"]["summary"]["allow_merge"] is True

    summary = client.get("/ops/brain/agentic-pipelines", params={"session_id": "pipeline-api-session"})
    assert summary.status_code == 200
    summary_payload = summary.json()
    assert summary_payload["latest_run"]["run_id"] == run["run_id"]
    assert summary_payload["run_count"] == 1

    scorecard = client.get("/ops/brain/canon/agentic-pipelines")
    assert scorecard.status_code == 200
    scorecard_payload = scorecard.json()
    assert scorecard_payload["runtime_state"] == "live-bound"
    assert "deterministic_gate_checks" in scorecard_payload["required_controls"]
    assert scorecard_payload["operator_actions"]["create_run"]["endpoint"] == "/ops/brain/agentic-pipelines/runs"

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "pipeline-api-session"})
    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    assert control_panel["agentic_pipeline_scorecard"]["runtime_state"] == "live-bound"
    assert control_panel["agentic_pipeline_scorecard"]["latest_run"]["run_id"] == run["run_id"]

    blackbox = client.get("/ops/brain/canon/blackbox", params={"session_id": "pipeline-api-session"}).json()
    assert blackbox["scorecard_refs"]["agentic_pipelines"] == "/ops/brain/canon/agentic-pipelines"

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Agentic Pipeline Runtime" in ui.text
    assert "agenticPipelineScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderAgenticPipelineScorecard" in app_js
    assert "/ops/brain/canon/agentic-pipelines" in app_js

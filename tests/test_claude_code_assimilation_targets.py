from __future__ import annotations

import shutil
from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


EXPECTED_TARGET_IDS = {
    "tool-execution-registry",
    "checkpoint-rewind-ledger",
    "task-dependency-graph",
    "provider-circuit-error-classifier",
    "prompt-overlay-registry",
    "plan-mode-write-jail",
    "skill-system-orchestrator",
    "bridge-manager",
    "research-monitor-pipeline",
    "sandbox-agent-factory",
}


def _project_with_control_panel(tmp_path: Path) -> Path:
    project_root = make_project(tmp_path)
    source_control_panel = Path(__file__).resolve().parents[1] / "ui" / "control-panel"
    shutil.copytree(source_control_panel, project_root / "ui" / "control-panel")
    return project_root


def test_assimilation_targets_scorecard_covers_all_requested_targets(tmp_path: Path):
    project_root = _project_with_control_panel(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.get("/ops/brain/canon/assimilation-targets")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status_label"] == "LOCKED CANON"
    assert payload["coverage_summary"]["target_count"] == 10
    assert {target["target_id"] for target in payload["targets"]} == EXPECTED_TARGET_IDS

    skill_system = next(target for target in payload["targets"] if target["target_id"] == "skill-system-orchestrator")
    assert skill_system["architecture"] == "orchestrator-plus-composable-skills"
    assert "mega_skill_rejected" in skill_system["required_controls"]
    assert "isolated_skill_endpoint_rejected" in skill_system["required_controls"]

    source_ids = {source["source_id"] for source in payload["source_refs"]}
    assert {"cheetahclaws-python", "mattpocock-skills", "openai-symphony", "mattpocock-sandcastle"}.issubset(source_ids)

    sandbox_target = next(target for target in payload["targets"] if target["target_id"] == "sandbox-agent-factory")
    assert sandbox_target["implementation_state"] == "runtime-executable-local-and-container"
    assert "merge_back_policy_gate" in sandbox_target["required_controls"]

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "assimilation-cockpit"})
    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    assert control_panel["assimilation_target_scorecard"]["surface_id"] == "claude-code-assimilation-targets"


def test_skill_system_composer_builds_chained_orchestrator_with_handoffs(tmp_path: Path):
    project_root = _project_with_control_panel(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/skill-systems/compose",
        json={
            "system_id": "weekly-video-clips",
            "goal": "Turn one long-form video URL into five reviewed short-form clips.",
            "trigger": {"kind": "manual", "input_ref": "youtube_url"},
            "components": [
                {
                    "skill_id": "transcript-extraction",
                    "purpose": "extract word-level timestamps",
                    "required_input": "video_url",
                    "output": "timestamped_transcript",
                },
                {
                    "skill_id": "clip-selection",
                    "purpose": "score hook-worthy moments",
                    "required_input": "timestamped_transcript",
                    "output": "approved_clip_windows",
                },
                {
                    "skill_id": "portrait-render",
                    "purpose": "reframe approved windows into portrait clips",
                    "required_input": "approved_clip_windows",
                    "output": "rendered_portrait_clips",
                },
                {
                    "skill_id": "publishing-package",
                    "purpose": "package clips with titles and thumbnails",
                    "required_input": "rendered_portrait_clips",
                    "output": "ready_to_schedule_package",
                },
            ],
            "human_checkpoints": [
                {"checkpoint_id": "approve_clip_windows", "after_skill_id": "clip-selection"},
                {"checkpoint_id": "approve_final_package", "after_skill_id": "publishing-package"},
            ],
            "visual_result": {"kind": "html-dashboard", "artifact_ref": "runtime/artifacts/skill-systems/weekly-video-clips"},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status_label"] == "LOCKED CANON"
    assert payload["orchestrator"]["pattern"] == "sequential_workflow_orchestration"
    assert payload["orchestrator"]["anti_patterns_rejected"] == [
        "isolated_skill_endpoint",
        "mega_skill",
        "manual_copy_paste_handoff",
    ]
    assert payload["context_policy"]["component_context_rule"] == "load-exact-step-context-only"
    assert payload["context_policy"]["progressive_disclosure"] is True
    assert payload["handoff_map"][0]["from_skill_id"] == "transcript-extraction"
    assert payload["handoff_map"][0]["to_skill_id"] == "clip-selection"
    assert payload["human_checkpoints"][0]["after_skill_id"] == "clip-selection"


def test_skill_system_executor_endpoint_runs_a_local_registered_skill(tmp_path: Path):
    project_root = _project_with_control_panel(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/skill-systems/execute",
        json={
            "system": {
                "system_id": "passthrough-system",
                "goal": "Carry reviewed text through one governed local handoff.",
                "components": [
                    {
                        "skill_id": "context-passthrough",
                        "purpose": "pass reviewed input to the next local step",
                        "required_input": "reviewed_text",
                        "output": "handoff_text",
                    }
                ],
            },
            "initial_context": {"reviewed_text": "NexusNet"},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["lifecycle_state"] == "completed"
    assert payload["outputs"] == {"handoff_text": "NexusNet"}


def test_skill_system_executor_api_pauses_and_resumes_required_human_checkpoint(tmp_path: Path):
    client = TestClient(create_app(str(_project_with_control_panel(tmp_path))))
    paused_response = client.post(
        "/ops/brain/skill-systems/execute",
        json={
            "system": {
                "system_id": "checkpoint-api-system",
                "goal": "Require approval after preparing reviewed text.",
                "components": [
                    {
                        "skill_id": "context-passthrough",
                        "purpose": "prepare reviewed text",
                        "required_input": "source_text",
                        "output": "reviewed_text",
                    }
                ],
                "human_checkpoints": [
                    {
                        "checkpoint_id": "approve-reviewed-text",
                        "after_skill_id": "context-passthrough",
                        "required": True,
                    }
                ],
            },
            "initial_context": {"source_text": "review me"},
        },
    )

    assert paused_response.status_code == 200
    paused = paused_response.json()
    assert paused["lifecycle_state"] == "awaiting_human_checkpoint"
    resumed_response = client.post(
        f"/ops/brain/skill-systems/runs/{paused['run_id']}/resume",
        json={"approved_checkpoint_ids": ["approve-reviewed-text"]},
    )

    assert resumed_response.status_code == 200
    resumed = resumed_response.json()
    assert resumed["lifecycle_state"] == "completed"
    assert resumed["outputs"] == {"reviewed_text": "review me"}
    assert resumed["checkpoint_receipts"][0]["state"] == "approved"


def test_control_panel_surfaces_assimilation_targets(tmp_path: Path):
    project_root = _project_with_control_panel(tmp_path)
    client = TestClient(create_app(str(project_root)))

    ui = client.get("/ui/control-panel/")

    assert ui.status_code == 200
    assert "Assimilation Target Matrix" in ui.text
    assert "Skill Systems Orchestrator" in ui.text
    assert "assimilationTargetScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderAssimilationTargetScorecard" in app_js
    assert "/ops/brain/canon/assimilation-targets" in app_js
    assert "/ops/brain/skill-systems/compose" in app_js


def test_assimilation_targets_point_to_executable_runtime_sources(tmp_path: Path):
    payload = TestClient(create_app(str(_project_with_control_panel(tmp_path)))).get(
        "/ops/brain/canon/assimilation-targets"
    ).json()
    targets = {target["target_id"]: target for target in payload["targets"]}

    assert "nexusnet/operations/checkpoint_rewind.py" in targets["checkpoint-rewind-ledger"]["implementation_source_refs"]
    assert "/ops/brain/skill-systems/execute" in targets["skill-system-orchestrator"]["endpoint_refs"]
    assert "/ops/brain/skill-systems/runs/{run_id}/resume" in targets["skill-system-orchestrator"]["endpoint_refs"]
    assert "/ops/tools/filesystem.write" in targets["tool-execution-registry"]["endpoint_refs"]
    assert "/ops/tools/batch" in targets["tool-execution-registry"]["endpoint_refs"]
    assert "/ops/brain/agentic-pipelines/runs/{run_id}/claim-ready" in targets["task-dependency-graph"]["endpoint_refs"]
    assert "nexusnet/computer_fabric/bridges.py" in targets["bridge-manager"]["implementation_source_refs"]
    assert "/ops/brain/bridges/commitments/{commitment_id}/dispatch" in targets["bridge-manager"]["endpoint_refs"]
    assert "nexusnet/research/monitor.py" in targets["research-monitor-pipeline"]["implementation_source_refs"]
    assert "/ops/brain/research-monitors/poll-due" in targets["research-monitor-pipeline"]["endpoint_refs"]
    assert "/ops/brain/sandbox-agent-factory/runs/{run_id}/execute-local" in targets["sandbox-agent-factory"]["endpoint_refs"]
    assert "/ops/brain/sandbox-agent-factory/runs/{run_id}/execute-container" in targets["sandbox-agent-factory"]["endpoint_refs"]
    assert "/ops/brain/sandbox-agent-factory/runs/{run_id}/merge-gates" in targets["sandbox-agent-factory"]["endpoint_refs"]

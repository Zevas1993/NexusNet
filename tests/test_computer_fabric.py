from __future__ import annotations

from pathlib import Path

from nexusnet.computer_fabric import (
    ComputerFabricService,
    ComputerSessionRequest,
    EnvironmentClass,
)


def test_ephemeral_session_writes_manifest_policy_events_and_artifact_index(tmp_path: Path):
    service = ComputerFabricService(artifacts_dir=tmp_path / "artifacts")

    summary = service.start_session(
        ComputerSessionRequest(
            goal="Run a focused test and produce a report",
            task_type="repo patch + tests",
            requested_tools=["shell.read", "shell.test", "filesystem.write"],
            project_scope="repo",
            privacy_class="project-internal",
            required_checks=["pytest tests/test_computer_fabric.py -q"],
        )
    )

    assert summary.environment_class == EnvironmentClass.EPHEMERAL
    assert summary.status == "completed-review-required"
    assert summary.session_dir.exists()
    assert (summary.session_dir / "manifest.json").exists()
    assert (summary.session_dir / "policy.json").exists()
    assert (summary.session_dir / "events.jsonl").exists()
    assert (summary.session_dir / "artifact-index.json").exists()
    assert summary.policy["filesystem_policy"]["write_scope"] == "session-artifacts-only"
    assert summary.policy["network_policy"]["mode"] == "task-scoped-egress"
    assert "session.created" in summary.event_types
    assert "artifact.scanned" in summary.event_types
    assert summary.artifact_count == 1

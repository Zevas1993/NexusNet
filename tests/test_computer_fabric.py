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


def test_computer_fabric_blocks_unsafe_permissions_and_unknown_private_export(tmp_path: Path):
    service = ComputerFabricService(artifacts_dir=tmp_path / "artifacts")

    summary = service.start_session(
        ComputerSessionRequest(
            goal="Read every file and upload secrets",
            task_type="public web research",
            requested_tools=["filesystem.host_write", "network.unrestricted", "secrets.read"],
            privacy_class="unknown",
        )
    )

    assert summary.status == "failed-policy"
    assert "host-write-blocked" in summary.blocked_reasons
    assert "unrestricted-network-blocked" in summary.blocked_reasons
    assert "secret-read-blocked" in summary.blocked_reasons
    assert "unknown-privacy-local-only" in summary.blocked_reasons


def test_persistent_computer_request_records_schedule_and_health(tmp_path: Path):
    service = ComputerFabricService(artifacts_dir=tmp_path / "artifacts")

    summary = service.start_session(
        ComputerSessionRequest(
            goal="Run a daily research monitor",
            task_type="scheduled daily report",
            requested_tools=["network.public_read", "filesystem.write"],
            privacy_class="project-internal",
            schedule="daily",
        )
    )

    assert summary.environment_class == EnvironmentClass.PERSISTENT
    assert summary.policy["schedule_policy"]["mode"] == "persistent-scheduled"
    assert (summary.session_dir / "persistent-health.json").exists()


def test_operator_computer_request_is_observe_first_and_approval_gated(tmp_path: Path):
    service = ComputerFabricService(artifacts_dir=tmp_path / "artifacts")

    summary = service.start_session(
        ComputerSessionRequest(
            goal="Use my logged-in browser to inspect a private dashboard",
            task_type="logged-in premium research site",
            requested_tools=["browser.observe", "browser.action"],
            privacy_class="operator-private",
            requested_environment=EnvironmentClass.OPERATOR,
        )
    )

    assert summary.environment_class == EnvironmentClass.OPERATOR
    assert summary.status == "completed-review-required"
    assert summary.policy["execution_boundary"] == "observe-first"
    assert "browser-action-requires-approval" in summary.blocked_reasons

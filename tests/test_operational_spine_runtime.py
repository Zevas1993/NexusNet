from __future__ import annotations

import pytest

from nexusnet.operations.spine import OperationalSpineService


def test_worktree_registry_blocks_misalignment_and_persists_sanitized_state(tmp_path):
    service = OperationalSpineService(artifacts_dir=tmp_path)
    blocked = service.register_worktree(
        worktree_id="wt:feature",
        path="F:/secret/project/worktree",
        canonical_branch="codex/integration",
        current_branch="feature/unreviewed",
        preserved_ref="commit:abc",
        dirty=True,
        owner="agent:builder",
    )

    assert blocked["status"] == "blocked"
    assert set(blocked["blockers"]) == {"branch-not-canonical", "dirty-worktree"}
    assert "path" not in blocked
    assert blocked["path_digest"].startswith("sha256:")
    assert OperationalSpineService(artifacts_dir=tmp_path).summary()["worktree_count"] == 1


def test_release_channel_requires_flag_monitoring_rollback_and_approval(tmp_path):
    service = OperationalSpineService(artifacts_dir=tmp_path)
    release = service.register_release(
        release_id="release:1",
        channel="canary",
        artifact_ref="artifact:wheel:1",
        owner="operator:release",
        feature_flag="flag:new-runtime",
        monitoring_ref="monitor:runtime",
        rollback_ref="rollback:runtime-v0",
        evidence_refs=["tests:green"],
        approval_refs=["approval:release"],
    )

    assert release["status"] == "ready"
    observation = service.record_monitor_observation(
        monitor_id="monitor:runtime",
        release_id="release:1",
        metrics={"error_rate": 0.12, "latency_p95_ms": 5000},
        thresholds={"error_rate": 0.02, "latency_p95_ms": 1500},
        evidence_refs=["telemetry:window-1"],
    )
    assert observation["status"] == "slo-violated"
    assert observation["rollback_required"] is True
    assert service.release("release:1")["status"] == "rollback-required"


def test_scheduler_is_authority_gated_and_due_jobs_are_deterministic(tmp_path):
    service = OperationalSpineService(artifacts_dir=tmp_path)
    with pytest.raises(PermissionError):
        service.schedule(
            job_id="job:unsafe",
            action_ref="action:update-runtime",
            interval_seconds=60,
            authority_ref=None,
            enabled=True,
        )
    job = service.schedule(
        job_id="job:monitor",
        action_ref="action:monitor-runtime",
        interval_seconds=60,
        authority_ref="lease:monitor",
        enabled=True,
        next_run_at="2026-07-15T12:00:00+00:00",
    )
    assert job["enabled"] is True
    assert [item["job_id"] for item in service.due_jobs(at="2026-07-15T12:00:00+00:00")] == ["job:monitor"]


def test_disaster_recovery_snapshot_and_restore_are_real_and_audited(tmp_path):
    service = OperationalSpineService(artifacts_dir=tmp_path)
    service.register_worktree(
        worktree_id="wt:main",
        path="F:/repo",
        canonical_branch="codex/integration",
        current_branch="codex/integration",
        preserved_ref="commit:good",
        dirty=False,
        owner="operator:release",
    )
    snapshot = service.create_recovery_snapshot(snapshot_id="snapshot:good", evidence_refs=["backup:verified"])
    service.register_worktree(
        worktree_id="wt:bad",
        path="F:/repo-bad",
        canonical_branch="codex/integration",
        current_branch="feature/bad",
        preserved_ref="commit:bad",
        dirty=True,
        owner="agent:bad",
    )

    restored = service.restore_recovery_snapshot(
        snapshot["snapshot_id"], approval_ref="approval:disaster-recovery", reason_ref="incident:1"
    )

    assert restored["status"] == "restored"
    assert service.summary()["worktree_count"] == 1
    assert service.worktree("wt:bad") is None

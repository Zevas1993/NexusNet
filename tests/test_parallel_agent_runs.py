from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


def test_parallel_run_prepare_records_github_issue_isolation_and_product_sweep_surface(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/parallel-runs/prepare",
        json={
            "source_type": "github_issue",
            "source_ref": "coleam00/Archon#42",
            "base_branch": "main",
            "workspace_id": "default",
            "agent_id": "standard-wrapper-agent",
            "database_mode": "sqlite_clone",
            "requested_tools": ["git.worktree.create", "filesystem.write", "network.external"],
            "requested_extensions": ["mcp-github"],
            "validation_profile": "python-fast",
        },
    )
    assert response.status_code == 200
    payload = response.json()

    assert payload["run_id"].startswith("prun_github-issue-coleam00-archon-42")
    assert payload["status"] == "prepared"
    assert payload["source"] == {
        "source_type": "github_issue",
        "source_ref": "coleam00/Archon#42",
    }
    assert payload["branch_name"] == "codex/agent-run-github-issue-coleam00-archon-42"
    assert payload["worktree_path"].endswith(f".worktrees/agent-runs/{payload['run_id']}")
    assert payload["worktree"]["state"] == "planned_only"
    assert payload["worktree"]["created"] is False
    assert payload["port_allocations"][0]["name"] == "app"
    assert payload["port_allocations"][0]["port"] >= 4100
    assert payload["database_isolation"]["mode"] == "sqlite_clone"
    assert payload["database_isolation"]["state"] == "planned_clone"
    assert payload["dependency_bootstrap"]["status"] in {"ready", "not_required", "policy_blocked"}
    assert payload["validation"]["profile"] == "python-fast"
    assert payload["execution_allowed"] is False
    assert payload["mutation_allowed"] is False
    assert payload["gateway_decision_path"]
    assert payload["workflow_execution_id"]
    assert payload["review_summary"]["review_count"] == 0
    assert payload["self_healing_summary"]["signal_count"] == 0
    assert Path(payload["artifact_path"]).exists()

    repeat = client.post(
        "/ops/brain/parallel-runs/prepare",
        json={
            "source_type": "github_issue",
            "source_ref": "coleam00/Archon#42",
            "database_mode": "sqlite_clone",
        },
    )
    assert repeat.status_code == 200
    repeat_json = repeat.json()
    assert repeat_json["run_id"] == payload["run_id"]
    assert repeat_json["port_allocations"] == payload["port_allocations"]

    summary = client.get("/ops/brain/parallel-runs")
    assert summary.status_code == 200
    summary_json = summary.json()
    assert summary_json["run_count"] == 1
    assert summary_json["latest_run"]["run_id"] == payload["run_id"]
    assert summary_json["event_log"]["event_type_counts"]["parallel_run.prepared"] >= 1
    assert summary_json["event_log"]["event_type_counts"]["parallel_run.port_allocated"] >= 1
    assert summary_json["event_log"]["event_type_counts"]["parallel_run.database_isolation_selected"] >= 1
    assert summary_json["event_log"]["event_type_counts"]["parallel_run.validation_started"] >= 1
    assert summary_json["event_log"]["event_type_counts"]["parallel_run.validation_completed"] >= 1
    assert summary_json["event_log"]["event_type_counts"]["parallel_run.cleanup_recorded"] >= 1

    product_sweep = client.get("/ops/brain/product-sweep/status")
    assert product_sweep.status_code == 200
    sweep_json = product_sweep.json()
    parallel_surface = sweep_json["status_surfaces"]["archon_pi_assimilation"]["parallel_runs"]
    assert parallel_surface["latest_run"]["run_id"] == payload["run_id"]
    assert parallel_surface["execution_allowed"] is False


def test_parallel_run_review_and_self_healing_report_are_gated_and_persisted(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    prepared = client.post(
        "/ops/brain/parallel-runs/prepare",
        json={
            "source_type": "manual",
            "source_ref": "parallel agent transcript assimilation",
            "requested_tools": ["git.worktree.create"],
        },
    )
    assert prepared.status_code == 200
    run_id = prepared.json()["run_id"]

    review = client.post(
        f"/ops/brain/parallel-runs/{run_id}/review",
        json={
            "lane": "adversarial",
            "decision": "changes_requested",
            "reviewer": "codex-adversarial-review",
            "findings": [
                {
                    "severity": "high",
                    "message": "Validation did not prove the assigned port was live.",
                    "artifact": "validation-log.json",
                }
            ],
            "linked_trace_ids": ["trace-review-001"],
        },
    )
    assert review.status_code == 200
    review_json = review.json()
    assert review_json["status"] == "review_changes_requested"
    assert review_json["review_summary"]["review_count"] == 1
    assert review_json["review_summary"]["decision_counts"]["changes_requested"] == 1
    assert review_json["review_summary"]["lane_counts"]["adversarial"] == 1
    assert review_json["execution_allowed"] is False
    assert review_json["mutation_allowed"] is False

    self_healing = client.post(
        f"/ops/brain/parallel-runs/{run_id}/self-healing-report",
        json={
            "signals": [
                {
                    "category": "missing_validation",
                    "target": "workflow",
                    "message": "Add an E2E port probe before PR review.",
                    "source": "adversarial-review",
                },
                {
                    "category": "environment_conflict",
                    "target": "gate",
                    "message": "Record port allocation conflicts as gate evidence.",
                    "source": "parallel-run-prepare",
                },
            ],
            "linked_trace_ids": ["trace-retro-001"],
        },
    )
    assert self_healing.status_code == 200
    report_json = self_healing.json()
    assert report_json["self_healing_summary"]["signal_count"] == 2
    assert report_json["self_healing_summary"]["category_counts"]["missing_validation"] == 1
    assert report_json["self_healing_summary"]["target_counts"]["workflow"] == 1
    assert report_json["execution_allowed"] is False
    assert report_json["mutation_allowed"] is False

    history = client.get("/ops/brain/parallel-runs/history", params={"source_type": "manual"})
    assert history.status_code == 200
    history_json = history.json()
    assert history_json["run_count"] == 1
    assert history_json["latest_run"]["run_id"] == run_id
    assert "parallel_run.review_completed" in history_json["event_type_counts"]
    assert "parallel_run.self_healing_signal_recorded" in history_json["event_type_counts"]


def test_parallel_run_rejects_unsupported_source_database_review_and_self_healing_values(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    bad_source = client.post(
        "/ops/brain/parallel-runs/prepare",
        json={"source_type": "jira", "source_ref": "NX-1"},
    )
    assert bad_source.status_code == 400
    assert "unsupported source_type" in bad_source.json()["detail"]

    bad_database = client.post(
        "/ops/brain/parallel-runs/prepare",
        json={"source_type": "local_spec", "source_ref": "docs/spec.md", "database_mode": "prod"},
    )
    assert bad_database.status_code == 400
    assert "unsupported database_mode" in bad_database.json()["detail"]

    prepared = client.post(
        "/ops/brain/parallel-runs/prepare",
        json={"source_type": "local_spec", "source_ref": "docs/spec.md"},
    )
    assert prepared.status_code == 200
    run_id = prepared.json()["run_id"]

    bad_review = client.post(
        f"/ops/brain/parallel-runs/{run_id}/review",
        json={"lane": "same_context", "decision": "approved"},
    )
    assert bad_review.status_code == 400
    assert "unsupported review lane" in bad_review.json()["detail"]

    bad_signal = client.post(
        f"/ops/brain/parallel-runs/{run_id}/self-healing-report",
        json={"signals": [{"category": "misc", "target": "workflow", "message": "Too vague"}]},
    )
    assert bad_signal.status_code == 400
    assert "unsupported self-healing category" in bad_signal.json()["detail"]

from __future__ import annotations

from threading import Barrier

import pytest
from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexus.tools.registry import ToolRegistry
from tests.test_nexus_phase1_foundation import make_project


def test_tool_registry_executes_declared_readonly_tool_with_bounded_output():
    registry = ToolRegistry()
    result = registry.execute(
        "filesystem.readonly",
        {"path": "notes.txt"},
        executor=lambda payload: {"content": "x" * 20_000, "path": payload["path"]},
    )

    assert result["ok"] is True
    assert result["tool_name"] == "filesystem.readonly"
    assert result["output"]["content"] == "x" * 16_000
    assert result["receipt"]["output_truncated"] is True


def test_tool_registry_rejects_undeclared_input_fields():
    registry = ToolRegistry()

    with pytest.raises(ValueError, match="undeclared input fields: delete"):
        registry.execute(
            "filesystem.readonly",
            {"path": "notes.txt", "delete": True},
            executor=lambda payload: {"content": "unused"},
        )


def test_nexusnet_tool_api_reads_only_within_the_project_root(tmp_path):
    project_root = make_project(tmp_path)
    (project_root / "safe.txt").write_text("project-local evidence", encoding="utf-8")
    client = TestClient(create_app(str(project_root)))

    response = client.post("/ops/tools/filesystem.readonly", json={"path": "safe.txt"})

    assert response.status_code == 200
    assert response.json()["output"]["content"] == "project-local evidence"
    escaped = client.post("/ops/tools/filesystem.readonly", json={"path": "../outside.txt"})
    assert escaped.status_code == 400


def test_filesystem_write_is_plan_jailed_checkpointed_atomic_and_cache_invalidating(tmp_path):
    project_root = make_project(tmp_path)
    target = project_root / "docs" / "superpowers" / "plans" / "runtime.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("before", encoding="utf-8")
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/tools/filesystem.write",
        json={"path": "docs/superpowers/plans/runtime.md", "content": "after", "mode": "plan"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert target.read_text(encoding="utf-8") == "after"
    assert payload["receipt"]["cache_invalidation_required"] is True
    assert payload["receipt"]["invalidated_cache_keys"] == ["filesystem:docs/superpowers/plans/runtime.md"]
    checkpoint = payload["receipt"]["pre_write_checkpoint"]
    rewind = client.post(
        f"/ops/brain/checkpoints/{checkpoint['checkpoint_id']}/rewind",
        json={"subject_ref": checkpoint["subject_ref"]},
    )
    assert rewind.json()["checkpoint"]["state"] == {"content": "before", "existed": True}

    blocked = client.post(
        "/ops/tools/filesystem.write",
        json={"path": "nexusnet/runtime/unsafe.py", "content": "bad", "mode": "plan"},
    )
    assert blocked.status_code == 400
    assert not (project_root / "nexusnet" / "runtime" / "unsafe.py").exists()


def test_implementation_write_is_confined_to_runtime_sandbox(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    allowed = client.post(
        "/ops/tools/filesystem.write",
        json={"path": "runtime/sandboxes/run-1/output.txt", "content": "ok", "mode": "implementation"},
    )
    blocked = client.post(
        "/ops/tools/filesystem.write",
        json={"path": "nexusnet/core/unsafe.py", "content": "bad", "mode": "implementation"},
    )

    assert allowed.status_code == 200
    assert (project_root / "runtime" / "sandboxes" / "run-1" / "output.txt").read_text(encoding="utf-8") == "ok"
    assert blocked.status_code == 400


def test_tool_registry_executes_readonly_batch_concurrently_in_request_order():
    registry = ToolRegistry()
    barrier = Barrier(2)

    def executor(tool_name, payload):
        barrier.wait(timeout=2)
        return {"content": payload["path"]}

    batch = registry.execute_batch(
        [
            {"tool_name": "filesystem.readonly", "payload": {"path": "a.txt"}},
            {"tool_name": "filesystem.readonly", "payload": {"path": "b.txt"}},
        ],
        executor=executor,
        max_workers=2,
    )

    assert batch["parallelized"] is True
    assert [result["output"]["content"] for result in batch["results"]] == ["a.txt", "b.txt"]


def test_tool_batch_api_reads_multiple_project_files(tmp_path):
    project_root = make_project(tmp_path)
    (project_root / "a.txt").write_text("A", encoding="utf-8")
    (project_root / "b.txt").write_text("B", encoding="utf-8")
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/tools/batch",
        json={
            "requests": [
                {"tool_name": "filesystem.readonly", "payload": {"path": "a.txt"}},
                {"tool_name": "filesystem.readonly", "payload": {"path": "b.txt"}},
            ]
        },
    )

    assert response.status_code == 200
    assert [item["output"]["content"] for item in response.json()["results"]] == ["A", "B"]

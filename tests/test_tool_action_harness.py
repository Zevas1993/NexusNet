import json
from pathlib import Path

import pytest

from nexusnet.tools.action_harness import ToolActionHarness


def test_tool_action_harness_allows_readonly_observation(tmp_path):
    harness = ToolActionHarness(artifacts_dir=tmp_path)

    result = harness.plan_action(
        action_id="tool:browser:observe",
        tool_ref="browser",
        action_type="observe",
        requested_effect="browser",
        contains_private_data=False,
        sandbox_state="session-readonly",
        operator_approved=False,
        evidence_refs=["trace:observe"],
    )

    assert result["status"] == "planned-shadow"
    assert result["execution_allowed"] is False
    assert result["operator_confirmation_required"] is False


def test_tool_action_harness_requires_confirmation_for_mutation(tmp_path):
    harness = ToolActionHarness(artifacts_dir=tmp_path)

    result = harness.plan_action(
        action_id="tool:desktop:click",
        tool_ref="desktop",
        action_type="click",
        requested_effect="desktop",
        contains_private_data=True,
        sandbox_state="none",
        operator_approved=False,
        evidence_refs=["trace:click"],
    )

    assert result["status"] == "blocked"
    assert result["operator_confirmation_required"] is True
    assert "mutating_tool_action_requires_sandbox" in result["findings"]


@pytest.mark.parametrize(
    ("tool_ref", "action_type"),
    [
        ("shell", "shell.exec"),
        ("powershell", "powershell.exec"),
        ("cmd", "cmd.exec"),
        ("filesystem", "filesystem.write"),
        ("filesystem", "filesystem.delete"),
        ("git", "git.commit"),
    ],
)
def test_tool_action_harness_blocks_dotted_mutating_actions(
    tmp_path,
    tool_ref,
    action_type,
):
    harness = ToolActionHarness(artifacts_dir=tmp_path)

    result = harness.plan_action(
        action_id=f"tool:{action_type}",
        tool_ref=tool_ref,
        action_type=action_type,
        requested_effect=tool_ref,
        contains_private_data=False,
        sandbox_state="none",
        operator_approved=False,
        evidence_refs=[f"trace:{action_type}"],
    )

    assert result["status"] == "blocked"
    assert result["operator_confirmation_required"] is True
    assert "mutating_tool_action_requires_sandbox" in result["findings"]
    assert "mutating_tool_action_requires_operator_confirmation" in result["findings"]


@pytest.mark.parametrize("tool_ref", ["filesystem.write", "filesystem.delete", "git.commit"])
def test_tool_action_harness_blocks_dotted_mutating_tool_refs(tmp_path, tool_ref):
    harness = ToolActionHarness(artifacts_dir=tmp_path)

    result = harness.plan_action(
        action_id=f"tool:{tool_ref}:observe",
        tool_ref=tool_ref,
        action_type="observe",
        requested_effect=tool_ref,
        contains_private_data=False,
        sandbox_state="none",
        operator_approved=False,
        evidence_refs=[f"trace:{tool_ref}"],
    )

    assert result["status"] == "blocked"
    assert result["operator_confirmation_required"] is True
    assert "mutating_tool_action_requires_sandbox" in result["findings"]
    assert "mutating_tool_action_requires_operator_confirmation" in result["findings"]


@pytest.mark.parametrize("invalid_value", [[], {}])
def test_tool_action_harness_rejects_invalid_sandbox_state_without_persisting(
    tmp_path,
    invalid_value,
):
    harness = ToolActionHarness(artifacts_dir=tmp_path)

    with pytest.raises(ValueError, match="sandbox_state must be a string"):
        harness.plan_action(
            action_id="tool:desktop:click",
            tool_ref="desktop",
            action_type="click",
            requested_effect="desktop",
            contains_private_data=False,
            sandbox_state=invalid_value,
            operator_approved=False,
            evidence_refs=["trace:click"],
        )

    assert harness.summary()["plan_count"] == 0
    assert list((tmp_path / "tools" / "action-harness").glob("*.json")) == []


@pytest.mark.parametrize(
    ("field_name", "overrides", "expected_message"),
    [
        ("action_id", {"action_id": ""}, "action_id must be a non-empty string"),
        ("tool_ref", {"tool_ref": ""}, "tool_ref must be a non-empty string"),
        ("evidence_refs", {"evidence_refs": [""]}, "evidence_refs must contain non-empty strings"),
    ],
)
def test_tool_action_harness_rejects_empty_ids_and_refs_without_persisting(
    tmp_path,
    field_name,
    overrides,
    expected_message,
):
    harness = ToolActionHarness(artifacts_dir=tmp_path)
    kwargs = {
        "action_id": "tool:browser:observe",
        "tool_ref": "browser",
        "action_type": "observe",
        "requested_effect": "browser",
        "contains_private_data": False,
        "sandbox_state": "session-readonly",
        "operator_approved": False,
        "evidence_refs": ["trace:observe"],
        **overrides,
    }

    with pytest.raises(ValueError, match=expected_message):
        harness.plan_action(**kwargs)

    assert harness.summary()["plan_count"] == 0
    assert list((tmp_path / "tools" / "action-harness").glob("*.json")) == []


@pytest.mark.parametrize("invalid_value", ["false", 0, 1, [], {}])
def test_tool_action_harness_rejects_invalid_contains_private_data_without_persisting(
    tmp_path,
    invalid_value,
):
    harness = ToolActionHarness(artifacts_dir=tmp_path)

    with pytest.raises(ValueError, match="contains_private_data must be a boolean"):
        harness.plan_action(
            action_id="tool:browser:observe",
            tool_ref="browser",
            action_type="observe",
            requested_effect="browser",
            contains_private_data=invalid_value,
            sandbox_state="session-readonly",
            operator_approved=False,
            evidence_refs=["trace:observe"],
        )

    assert harness.summary()["plan_count"] == 0
    assert list((tmp_path / "tools" / "action-harness").glob("*.json")) == []


@pytest.mark.parametrize("invalid_value", ["false", 0, 1, [], {}])
def test_tool_action_harness_rejects_invalid_operator_approval_without_persisting(
    tmp_path,
    invalid_value,
):
    harness = ToolActionHarness(artifacts_dir=tmp_path)

    with pytest.raises(ValueError, match="operator_approved must be a boolean"):
        harness.plan_action(
            action_id="tool:browser:observe",
            tool_ref="browser",
            action_type="observe",
            requested_effect="browser",
            contains_private_data=False,
            sandbox_state="session-readonly",
            operator_approved=invalid_value,
            evidence_refs=["trace:observe"],
        )

    assert harness.summary()["plan_count"] == 0
    assert list((tmp_path / "tools" / "action-harness").glob("*.json")) == []


def test_tool_action_harness_returned_plan_mutation_does_not_corrupt_summary(tmp_path):
    harness = ToolActionHarness(artifacts_dir=tmp_path)
    result = harness.plan_action(
        action_id="tool:browser:observe",
        tool_ref="browser",
        action_type="observe",
        requested_effect="browser",
        contains_private_data=False,
        sandbox_state="session-readonly",
        operator_approved=False,
        evidence_refs=["trace:observe"],
    )

    result["status"] = "blocked"
    result["findings"].append("tampered")

    summary = harness.summary()

    assert summary["latest_plan"]["status"] == "planned-shadow"
    assert summary["latest_plan"]["findings"] == []
    assert summary["runtime_state"] == "live-bound"


def test_tool_action_harness_fresh_summary_sees_persisted_plans(tmp_path):
    harness = ToolActionHarness(artifacts_dir=tmp_path)
    result = harness.plan_action(
        action_id="tool:desktop:click",
        tool_ref="desktop",
        action_type="click",
        requested_effect="desktop",
        contains_private_data=True,
        sandbox_state="none",
        operator_approved=False,
        evidence_refs=["trace:click"],
    )

    summary = ToolActionHarness(artifacts_dir=tmp_path).summary()

    assert summary["plan_count"] == 1
    assert summary["runtime_state"] == "degraded"
    assert summary["latest_plan"]["action_id"] == result["action_id"]


def test_tool_action_harness_skips_invalid_disk_plans_without_hiding_valid_plan(tmp_path):
    harness = ToolActionHarness(artifacts_dir=tmp_path)
    valid = harness.plan_action(
        action_id="tool:browser:observe",
        tool_ref="browser",
        action_type="observe",
        requested_effect="browser",
        contains_private_data=False,
        sandbox_state="session-readonly",
        operator_approved=False,
        evidence_refs=["trace:observe"],
    )
    plans_dir = tmp_path / "tools" / "action-harness"
    (plans_dir / "corrupt.json").write_text("{", encoding="utf-8")
    (plans_dir / "non-object.json").write_text(json.dumps([]), encoding="utf-8")
    (plans_dir / "shape-invalid.json").write_text(
        json.dumps({"action_id": "tool:missing:fields"}),
        encoding="utf-8",
    )
    semantic_invalid = json.loads(Path(valid["artifact_path"]).read_text(encoding="utf-8"))
    semantic_invalid["execution_allowed"] = True
    (plans_dir / "semantic-invalid.json").write_text(
        json.dumps(semantic_invalid),
        encoding="utf-8",
    )

    summary = ToolActionHarness(artifacts_dir=tmp_path).summary()

    assert summary["plan_count"] == 1
    assert summary["latest_plan"]["action_id"] == valid["action_id"]


def test_tool_action_harness_unsafe_action_ids_stay_in_flat_artifact_dir(tmp_path):
    harness = ToolActionHarness(artifacts_dir=tmp_path)
    result = harness.plan_action(
        action_id="../escape/tool:desktop\\click",
        tool_ref="desktop",
        action_type="click",
        requested_effect="desktop",
        contains_private_data=False,
        sandbox_state="session-shadow",
        operator_approved=True,
        evidence_refs=["trace:click"],
    )

    artifact_path = Path(result["artifact_path"]).resolve()
    plans_dir = (tmp_path / "tools" / "action-harness").resolve()

    assert artifact_path.parent == plans_dir
    assert artifact_path.exists()
    assert list(plans_dir.glob("*.json")) == [artifact_path]


def test_tool_action_harness_failed_disk_write_leaves_no_phantom_plan(tmp_path, monkeypatch):
    harness = ToolActionHarness(artifacts_dir=tmp_path)

    def fail_write(self, *args, **kwargs):
        raise OSError("disk unavailable")

    monkeypatch.setattr(Path, "write_text", fail_write)

    with pytest.raises(OSError, match="disk unavailable"):
        harness.plan_action(
            action_id="tool:browser:observe",
            tool_ref="browser",
            action_type="observe",
            requested_effect="browser",
            contains_private_data=False,
            sandbox_state="session-readonly",
            operator_approved=False,
            evidence_refs=["trace:observe"],
        )

    assert harness.summary()["plan_count"] == 0


def test_tool_action_harness_dedupes_disk_plans_and_in_memory_wins(tmp_path):
    harness = ToolActionHarness(artifacts_dir=tmp_path)
    disk_plan = harness.plan_action(
        action_id="tool:browser:observe",
        tool_ref="browser-disk",
        action_type="observe",
        requested_effect="browser",
        contains_private_data=False,
        sandbox_state="session-readonly",
        operator_approved=False,
        evidence_refs=["trace:observe"],
    )
    plans_dir = tmp_path / "tools" / "action-harness"
    duplicate = json.loads(Path(disk_plan["artifact_path"]).read_text(encoding="utf-8"))
    duplicate["tool_ref"] = "browser-disk-duplicate"
    (plans_dir / "zz-duplicate.json").write_text(json.dumps(duplicate), encoding="utf-8")

    fresh_summary = ToolActionHarness(artifacts_dir=tmp_path).summary()
    assert fresh_summary["plan_count"] == 1
    assert fresh_summary["latest_plan"]["tool_ref"] == "browser-disk-duplicate"

    memory_plan = harness.plan_action(
        action_id="tool:browser:observe",
        tool_ref="browser-memory",
        action_type="observe",
        requested_effect="browser",
        contains_private_data=False,
        sandbox_state="session-readonly",
        operator_approved=False,
        evidence_refs=["trace:observe"],
    )

    summary = harness.summary()

    assert summary["plan_count"] == 1
    assert summary["latest_plan"]["tool_ref"] == memory_plan["tool_ref"]

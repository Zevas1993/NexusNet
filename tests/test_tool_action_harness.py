import json
from pathlib import Path

import pytest

from nexusnet.tools.action_harness import ToolActionHarness


def _artifact_file(tmp_path, plan):
    return tmp_path / "tools" / "action-harness" / plan["artifact_path"]


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


def test_tool_action_harness_rejects_readonly_malformed_sandbox_state_without_persisting(tmp_path):
    harness = ToolActionHarness(artifacts_dir=tmp_path)

    with pytest.raises(ValueError, match="sandbox_state is not an allowed sandbox state"):
        harness.plan_action(
            action_id="tool:browser:observe:not-ready",
            tool_ref="browser",
            action_type="observe",
            requested_effect="browser",
            contains_private_data=False,
            sandbox_state="not-ready",
            operator_approved=False,
            evidence_refs=["trace:observe"],
        )

    summary = ToolActionHarness(artifacts_dir=tmp_path).summary()

    assert summary["plan_count"] == 0
    assert summary["latest_plan"] is None
    assert list((tmp_path / "tools" / "action-harness").glob("*.json")) == []


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


@pytest.mark.parametrize("action_id", ["tool:shell.exec", "action:filesystem.write"])
def test_tool_action_harness_blocks_elevated_mutating_action_ids(tmp_path, action_id):
    harness = ToolActionHarness(artifacts_dir=tmp_path)

    result = harness.plan_action(
        action_id=action_id,
        tool_ref="browser",
        action_type="observe",
        requested_effect="browser",
        contains_private_data=False,
        sandbox_state="none",
        operator_approved=False,
        evidence_refs=[f"trace:{action_id}"],
    )

    assert result["status"] == "blocked"
    assert result["operator_confirmation_required"] is True
    assert "mutating_tool_action_requires_sandbox" in result["findings"]
    assert "mutating_tool_action_requires_operator_confirmation" in result["findings"]


@pytest.mark.parametrize(
    "action_type",
    [
        "filesystem.rename",
        "filesystem.create",
        "filesystem.append",
        "filesystem.replace",
        "filesystem.edit",
        "git.rebase",
        "filesystem.remove",
        "filesystem.truncate",
        "filesystem.overwrite",
        "git.apply",
    ],
)
def test_tool_action_harness_blocks_common_write_capable_actions(tmp_path, action_type):
    harness = ToolActionHarness(artifacts_dir=tmp_path)

    result = harness.plan_action(
        action_id=f"tool:{action_type}",
        tool_ref=action_type.split(".", 1)[0],
        action_type=action_type,
        requested_effect=action_type.split(".", 1)[0],
        contains_private_data=False,
        sandbox_state="none",
        operator_approved=False,
        evidence_refs=[f"trace:{action_type}"],
    )

    assert result["status"] == "blocked"
    assert result["operator_confirmation_required"] is True
    assert "mutating_tool_action_requires_sandbox" in result["findings"]
    assert "mutating_tool_action_requires_operator_confirmation" in result["findings"]


@pytest.mark.parametrize("action_type", ["rm", "fs.rm", "mv", "cp", "unlink", "touch"])
def test_tool_action_harness_blocks_common_short_mutation_aliases(tmp_path, action_type):
    harness = ToolActionHarness(artifacts_dir=tmp_path)

    result = harness.plan_action(
        action_id=f"tool:{action_type}",
        tool_ref="fs",
        action_type=action_type,
        requested_effect="filesystem",
        contains_private_data=False,
        sandbox_state="session-readonly",
        operator_approved=False,
        evidence_refs=[f"trace:{action_type}"],
    )

    assert result["status"] == "blocked"
    assert result["operator_confirmation_required"] is True
    assert "mutating_tool_action_requires_sandbox" in result["findings"]
    assert "mutating_tool_action_requires_operator_confirmation" in result["findings"]


def test_tool_action_harness_blocks_mutation_with_malformed_sandbox_state(tmp_path):
    harness = ToolActionHarness(artifacts_dir=tmp_path)

    with pytest.raises(ValueError, match="sandbox_state is not an allowed sandbox state"):
        harness.plan_action(
            action_id="tool:shell:exec:not-ready",
            tool_ref="shell",
            action_type="shell.exec",
            requested_effect="shell",
            contains_private_data=False,
            sandbox_state="not-ready",
            operator_approved=True,
            evidence_refs=["trace:shell.exec"],
        )

    summary = ToolActionHarness(artifacts_dir=tmp_path).summary()

    assert summary["plan_count"] == 0
    assert summary["latest_plan"] is None


def test_tool_action_harness_allows_approved_mutation_with_ready_sandbox(tmp_path):
    harness = ToolActionHarness(artifacts_dir=tmp_path)

    result = harness.plan_action(
        action_id="tool:shell:exec:ready",
        tool_ref="shell",
        action_type="shell.exec",
        requested_effect="shell",
        contains_private_data=False,
        sandbox_state="sandbox-ready",
        operator_approved=True,
        evidence_refs=["trace:shell.exec"],
    )

    assert result["status"] == "planned-shadow"
    assert result["execution_allowed"] is False
    assert result["operator_confirmation_required"] is True
    assert result["findings"] == []


def test_tool_action_harness_allows_release_wrapper_shadow_observation(tmp_path):
    harness = ToolActionHarness(artifacts_dir=tmp_path)

    result = harness.plan_action(
        action_id="tool-action::release-wrapper::trace",
        tool_ref="release-wrapper-runtime",
        action_type="inspect",
        requested_effect="release-wrapper-forward-pass-governance-observation",
        contains_private_data=False,
        sandbox_state="release-wrapper-shadow-observation",
        operator_approved=False,
        evidence_refs=["trace::trace"],
    )

    assert result["status"] == "planned-shadow"
    assert result["execution_allowed"] is False
    assert result["operator_confirmation_required"] is False
    assert result["findings"] == []


def test_tool_action_harness_allows_release_wrapper_rollback_quarantine_write(tmp_path):
    harness = ToolActionHarness(artifacts_dir=tmp_path)

    result = harness.plan_action(
        action_id="tool-action::production-spine-lifecycle-rollback::run",
        tool_ref="release-wrapper-production-spine-lifecycle-rollback",
        action_type="write",
        requested_effect="quarantine-production-spine-lifecycle-shadow-artifacts",
        contains_private_data=False,
        sandbox_state="production-spine-lifecycle-rollback-quarantine",
        operator_approved=True,
        evidence_refs=["rollback::run"],
    )

    assert result["status"] == "planned-shadow"
    assert result["execution_allowed"] is False
    assert result["operator_confirmation_required"] is True
    assert result["findings"] == []


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


def test_tool_action_harness_persists_flat_artifact_ref(tmp_path):
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
    artifact_ref = result["artifact_path"]
    persisted_path = tmp_path / "tools" / "action-harness" / artifact_ref
    persisted = json.loads(persisted_path.read_text(encoding="utf-8"))

    assert artifact_ref == Path(artifact_ref).name
    assert not Path(artifact_ref).is_absolute()
    assert "/" not in artifact_ref
    assert "\\" not in artifact_ref
    assert persisted["artifact_path"] == artifact_ref
    assert persisted_path.exists()


def test_tool_action_harness_fresh_summary_preserves_latest_plan_order(tmp_path):
    harness = ToolActionHarness(artifacts_dir=tmp_path)
    old = harness.plan_action(
        action_id="z-old",
        tool_ref="browser",
        action_type="observe",
        requested_effect="browser",
        contains_private_data=False,
        sandbox_state="session-readonly",
        operator_approved=False,
        evidence_refs=["trace:old"],
    )
    new = harness.plan_action(
        action_id="a-new",
        tool_ref="browser",
        action_type="observe",
        requested_effect="browser",
        contains_private_data=False,
        sandbox_state="session-readonly",
        operator_approved=False,
        evidence_refs=["trace:new"],
    )

    assert harness.summary()["latest_plan"]["action_id"] == new["action_id"]
    assert ToolActionHarness(artifacts_dir=tmp_path).summary()["latest_plan"]["action_id"] == new["action_id"]
    assert old["action_id"] != new["action_id"]


def test_tool_action_harness_skips_sequence_tampering_on_fresh_reload(tmp_path):
    harness = ToolActionHarness(artifacts_dir=tmp_path)
    old = harness.plan_action(
        action_id="old",
        tool_ref="browser",
        action_type="observe",
        requested_effect="browser",
        contains_private_data=False,
        sandbox_state="session-readonly",
        operator_approved=False,
        evidence_refs=["trace:old"],
    )
    new = harness.plan_action(
        action_id="new",
        tool_ref="browser",
        action_type="observe",
        requested_effect="browser",
        contains_private_data=False,
        sandbox_state="session-readonly",
        operator_approved=False,
        evidence_refs=["trace:new"],
    )
    old_payload = json.loads(_artifact_file(tmp_path, old).read_text(encoding="utf-8"))
    old_payload["sequence"] = 999
    _artifact_file(tmp_path, old).write_text(json.dumps(old_payload), encoding="utf-8")

    summary = ToolActionHarness(artifacts_dir=tmp_path).summary()

    assert summary["plan_count"] == 1
    assert summary["latest_plan"]["action_id"] == new["action_id"]


def test_tool_action_harness_skips_recomputed_sequence_tampering_on_fresh_reload(tmp_path):
    harness = ToolActionHarness(artifacts_dir=tmp_path)
    old = harness.plan_action(
        action_id="old",
        tool_ref="browser",
        action_type="observe",
        requested_effect="browser",
        contains_private_data=False,
        sandbox_state="session-readonly",
        operator_approved=False,
        evidence_refs=["trace:old"],
    )
    new = harness.plan_action(
        action_id="new",
        tool_ref="browser",
        action_type="observe",
        requested_effect="browser",
        contains_private_data=False,
        sandbox_state="session-readonly",
        operator_approved=False,
        evidence_refs=["trace:new"],
    )
    old_payload = json.loads(_artifact_file(tmp_path, old).read_text(encoding="utf-8"))
    old_payload["sequence"] = 999
    old_payload["record_digest"] = harness._record_digest(old_payload)
    _artifact_file(tmp_path, old).write_text(json.dumps(old_payload), encoding="utf-8")

    summary = ToolActionHarness(artifacts_dir=tmp_path).summary()

    assert summary["latest_plan"]["action_id"] == new["action_id"]


@pytest.mark.parametrize("sequence", ["2", 0, -1, True, None])
def test_tool_action_harness_skips_malformed_persisted_sequence(tmp_path, sequence):
    harness = ToolActionHarness(artifacts_dir=tmp_path)
    plan = harness.plan_action(
        action_id="tool:browser:observe",
        tool_ref="browser",
        action_type="observe",
        requested_effect="browser",
        contains_private_data=False,
        sandbox_state="session-readonly",
        operator_approved=False,
        evidence_refs=["trace:observe"],
    )
    payload = json.loads(_artifact_file(tmp_path, plan).read_text(encoding="utf-8"))
    payload["sequence"] = sequence
    _artifact_file(tmp_path, plan).write_text(json.dumps(payload), encoding="utf-8")

    summary = ToolActionHarness(artifacts_dir=tmp_path).summary()

    assert summary["plan_count"] == 0
    assert summary["latest_plan"] is None


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
    semantic_invalid = json.loads(_artifact_file(tmp_path, valid).read_text(encoding="utf-8"))
    semantic_invalid["execution_allowed"] = True
    (plans_dir / "semantic-invalid.json").write_text(
        json.dumps(semantic_invalid),
        encoding="utf-8",
    )

    summary = ToolActionHarness(artifacts_dir=tmp_path).summary()

    assert summary["plan_count"] == 1
    assert summary["latest_plan"]["action_id"] == valid["action_id"]


def test_tool_action_harness_skips_valid_payload_with_invalid_filename(tmp_path):
    harness = ToolActionHarness(artifacts_dir=tmp_path)
    plan = harness.plan_action(
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
    payload = _artifact_file(tmp_path, plan).read_text(encoding="utf-8")
    _artifact_file(tmp_path, plan).unlink()
    (plans_dir / "zz-duplicate.json").write_text(payload, encoding="utf-8")

    summary = ToolActionHarness(artifacts_dir=tmp_path).summary()

    assert summary["plan_count"] == 0
    assert summary["latest_plan"] is None


@pytest.mark.parametrize(
    "artifact_path_value",
    [
        "..\\escape.json",
        "../escape.json",
        "other.json",
        "C:\\escape.json",
    ],
)
def test_tool_action_harness_skips_tampered_artifact_paths(tmp_path, artifact_path_value):
    harness = ToolActionHarness(artifacts_dir=tmp_path)
    plan = harness.plan_action(
        action_id="tool:browser:observe",
        tool_ref="browser",
        action_type="observe",
        requested_effect="browser",
        contains_private_data=False,
        sandbox_state="session-readonly",
        operator_approved=False,
        evidence_refs=["trace:observe"],
    )
    payload = json.loads(_artifact_file(tmp_path, plan).read_text(encoding="utf-8"))
    payload["artifact_path"] = artifact_path_value
    _artifact_file(tmp_path, plan).write_text(json.dumps(payload), encoding="utf-8")

    summary = ToolActionHarness(artifacts_dir=tmp_path).summary()

    assert summary["plan_count"] == 0
    assert summary["latest_plan"] is None


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

    artifact_ref = result["artifact_path"]
    artifact_path = tmp_path / "tools" / "action-harness" / artifact_ref
    plans_dir = (tmp_path / "tools" / "action-harness").resolve()

    assert artifact_ref == Path(artifact_ref).name
    assert not Path(artifact_ref).is_absolute()
    assert artifact_path.resolve().parent == plans_dir
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


def test_tool_action_harness_invalid_disk_duplicates_are_skipped_and_in_memory_wins(tmp_path):
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
    duplicate = json.loads(_artifact_file(tmp_path, disk_plan).read_text(encoding="utf-8"))
    duplicate["tool_ref"] = "browser-disk-duplicate"
    (plans_dir / "zz-duplicate.json").write_text(json.dumps(duplicate), encoding="utf-8")

    fresh_summary = ToolActionHarness(artifacts_dir=tmp_path).summary()
    assert fresh_summary["plan_count"] == 1
    assert fresh_summary["latest_plan"]["tool_ref"] == "browser-disk"

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

    summary = ToolActionHarness(artifacts_dir=tmp_path).summary()

    assert summary["plan_count"] == 1
    assert summary["latest_plan"]["tool_ref"] == memory_plan["tool_ref"]

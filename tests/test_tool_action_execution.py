"""Depth D2: real sandboxed read-only tool EXECUTION (mutating stays plan-only)."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest

from nexusnet.execution_authority.service import ExecutionAuthorityService
from nexusnet.tools.action_harness import MAX_READ_BYTES, SafeReadOnlyToolbox, ToolActionHarness


def _sandbox(tmp_path: Path) -> Path:
    (tmp_path / "doc.txt").write_text("hello nexus hive", encoding="utf-8")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "a.txt").write_text("nested", encoding="utf-8")
    return tmp_path


def _execute_with_lease(harness: ToolActionHarness, tmp_path: Path, *, action_id: str, tool_ref: str,
                        action_type: str, target: str, evidence_refs: list[str], sandbox_root: Path) -> dict:
    authority = ExecutionAuthorityService(artifacts_dir=tmp_path.parent / f"{tmp_path.name}-authority-artifacts")
    scope = {"tool_ref": tool_ref, "action_type": action_type, "target": target,
             "sandbox_root_digest": hashlib.sha256(str(sandbox_root.resolve()).encode("utf-8")).hexdigest()}
    lease = authority.request_lease(capability="deterministic_tool_boundary", scope=scope,
        expires_at="2099-01-01T00:00:00+00:00", budget={"max_usd": 0.0, "max_minutes": 1},
        rollback_plan={"strategy": "no-mutation-readonly"}, approval_id="approval::tool-readonly",
        approval_decision="approved", gateway_decision="allow", product_sweep_gate_ids=["tool-readonly"],
        product_sweep_decision="passed", requested_execution=True, requested_mutation=False)["lease"]
    assert lease["status"] == "granted"
    return harness.execute_action(action_id=action_id, tool_ref=tool_ref, action_type=action_type, target=target,
        evidence_refs=evidence_refs, sandbox_root=sandbox_root, execution_authority=authority, lease_id=lease["lease_id"])


def test_read_action_requires_matching_execution_authority_lease(tmp_path):
    root = _sandbox(tmp_path)
    rec = ToolActionHarness().execute_action(action_id="lease-required", tool_ref="fs", action_type="read",
        target="doc.txt", evidence_refs=["ev://1"], sandbox_root=root)
    assert rec["executed"] is False and rec["status"] == "blocked-authority"
    assert "execution_authority_lease_required" in rec["findings"]


def test_read_action_actually_reads(tmp_path):
    root = _sandbox(tmp_path)
    h = ToolActionHarness()
    rec = _execute_with_lease(h, tmp_path, action_id="r1", tool_ref="fs", action_type="read", target="doc.txt",
                              evidence_refs=["ev://1"], sandbox_root=root)
    assert rec["executed"] is True and rec["status"] == "executed-readonly"
    assert rec["result"]["text"] == "hello nexus hive"        # real content, not a stub
    assert rec["duration_ms"] >= 0.0


def test_list_and_hash_execute(tmp_path):
    root = _sandbox(tmp_path)
    h = ToolActionHarness()
    lst = _execute_with_lease(h, tmp_path, action_id="l1", tool_ref="fs", action_type="list", target=".",
                              evidence_refs=["ev://1"], sandbox_root=root)
    assert set(lst["result"]["entries"]) == {"doc.txt", "sub"}
    hsh = _execute_with_lease(h, tmp_path, action_id="h1", tool_ref="fs", action_type="hash", target="doc.txt",
                              evidence_refs=["ev://1"], sandbox_root=root)
    assert hsh["result"]["sha256"] == hashlib.sha256(b"hello nexus hive").hexdigest()


def test_mutating_action_is_refused_not_executed(tmp_path):
    h = ToolActionHarness()
    rec = h.execute_action(action_id="w1", tool_ref="fs", action_type="write", target="doc.txt",
                           evidence_refs=["ev://1"], sandbox_root=tmp_path)
    assert rec["executed"] is False and rec["execution_allowed"] is False
    assert "mutating_action_not_executable_plan_only" in rec["findings"]


def test_path_traversal_is_blocked(tmp_path):
    root = _sandbox(tmp_path)
    h = ToolActionHarness()
    rec = _execute_with_lease(h, tmp_path, action_id="t1", tool_ref="fs", action_type="read",
                              target="../../etc/passwd", evidence_refs=["ev://1"], sandbox_root=root)
    assert rec["executed"] is False and "execution_error" in rec["findings"]


def test_missing_evidence_blocks_execution(tmp_path):
    root = _sandbox(tmp_path)
    h = ToolActionHarness()
    rec = h.execute_action(action_id="n1", tool_ref="fs", action_type="read", target="doc.txt",
                           evidence_refs=[], sandbox_root=root)
    assert rec["executed"] is False
    assert "tool_action_requires_evidence_refs" in rec["findings"]


def test_toolbox_resolves_within_root_only(tmp_path):
    box = SafeReadOnlyToolbox(_sandbox(tmp_path))
    assert box.run("read", "sub/a.txt")["text"] == "nested"
    with pytest.raises(PermissionError):
        box.run("read", "../outside.txt")


def test_toolbox_rejects_absolute_missing_and_wrong_type_targets(tmp_path):
    root = _sandbox(tmp_path)
    box = SafeReadOnlyToolbox(root)

    with pytest.raises(PermissionError):
        box.run("read", str((root / "doc.txt").resolve()))
    with pytest.raises(OSError):
        box.run("read", "missing.txt")
    with pytest.raises((OSError, ValueError)):
        box.run("read", "sub")
    with pytest.raises((OSError, ValueError)):
        box.run("hash", "sub")


def test_execution_summary_redacts_read_results(tmp_path):
    root = _sandbox(tmp_path)
    harness = ToolActionHarness(artifacts_dir=tmp_path / "artifacts")
    result = _execute_with_lease(harness, tmp_path, action_id="private-read", tool_ref="fs", action_type="read",
                                 target="doc.txt", evidence_refs=["ev://1"], sandbox_root=root)
    latest = harness.summary()["latest_execution"]
    assert result["result"]["text"] == "hello nexus hive"
    assert latest["raw_content_included"] is False and latest["result_digest"].startswith("sha256:")
    assert "result" not in latest and "hello nexus hive" not in repr(latest)


def test_plan_only_path_still_works(tmp_path):
    # the original non-executing plan path is unchanged (regression guard)
    h = ToolActionHarness()
    plan = h.plan_action(action_id="p1", tool_ref="fs", action_type="click",
                         requested_effect="press", contains_private_data=False,
                         sandbox_state="none", operator_approved=False, evidence_refs=["e"])
    assert plan["execution_allowed"] is False and plan["status"] == "blocked"


def test_allowed_authority_decision_must_bind_exact_lease_capability_and_scope(tmp_path):
    root = _sandbox(tmp_path)

    class MalformedAuthority:
        def evaluate(self, **_kwargs):
            return {"decision": {"execution_allowed": True}}

    rec = ToolActionHarness().execute_action(
        action_id="malformed-authority",
        tool_ref="fs",
        action_type="read",
        target="doc.txt",
        evidence_refs=["ev://1"],
        sandbox_root=root,
        execution_authority=MalformedAuthority(),
        lease_id="lease::unbound",
    )

    assert rec["executed"] is False
    assert rec["status"] == "blocked-authority"
    assert rec["execution_authority_reason"] == "authority_invalid_response"
    assert "result" not in rec


def test_authority_failure_is_fail_closed_and_sanitized(tmp_path):
    root = _sandbox(tmp_path)
    secret = r"C:\secrets\lease-token"

    class ThrowingAuthority:
        def evaluate(self, **_kwargs):
            raise OSError(secret)

    rec = ToolActionHarness().execute_action(
        action_id="throwing-authority",
        tool_ref="fs",
        action_type="read",
        target="doc.txt",
        evidence_refs=["ev://1"],
        sandbox_root=root,
        execution_authority=ThrowingAuthority(),
        lease_id="lease::throwing",
    )

    assert rec["executed"] is False
    assert rec["execution_authority_reason"] == "authority_unavailable"
    assert secret not in repr(rec)


def test_authority_reason_is_mapped_to_closed_receipt_category(tmp_path):
    root = _sandbox(tmp_path)
    secret = r"C:\secrets\lease-token"

    class LeakyDeniedAuthority:
        def evaluate(self, **_kwargs):
            return {"decision": {"execution_allowed": False, "reason": secret}}

    harness = ToolActionHarness(artifacts_dir=tmp_path / "artifacts")
    rec = harness.execute_action(
        action_id="redacted-authority",
        tool_ref="fs",
        action_type="read",
        target="doc.txt",
        evidence_refs=["ev://1"],
        sandbox_root=root,
        execution_authority=LeakyDeniedAuthority(),
        lease_id="lease::denied",
    )

    assert rec["execution_authority_reason"] == "denied"
    assert rec["findings"] == ["execution_authority::denied"]
    assert secret not in repr(rec)
    assert secret not in repr(harness.summary())


def test_semantically_tampered_execution_receipt_is_excluded_from_summary(tmp_path):
    root = _sandbox(tmp_path)
    artifacts = tmp_path / "artifacts"
    harness = ToolActionHarness(artifacts_dir=artifacts)
    rec = _execute_with_lease(
        harness,
        tmp_path,
        action_id="tamper-receipt",
        tool_ref="fs",
        action_type="read",
        target="doc.txt",
        evidence_refs=["ev://1"],
        sandbox_root=root,
    )
    assert rec["receipt_digest"].startswith("sha256:")

    receipt_path = next((artifacts / "tools" / "action-harness" / "executions").glob("*.json"))
    payload = json.loads(receipt_path.read_text(encoding="utf-8"))
    payload["status"] = "blocked-authority"
    receipt_path.write_text(json.dumps(payload), encoding="utf-8")

    restarted = ToolActionHarness(artifacts_dir=artifacts)
    assert restarted.summary()["execution_count"] == 0
    assert restarted.summary()["latest_execution"] is None


def test_read_cap_is_enforced_from_open_descriptor_not_path_stat(tmp_path, monkeypatch):
    root = _sandbox(tmp_path)
    target = root / "large.txt"
    target.write_bytes(b"x" * (MAX_READ_BYTES + 1))
    toolbox = SafeReadOnlyToolbox(root)
    real_stat = Path.stat
    target_resolved = target.resolve()

    def misleading_path_stat(path, *args, **kwargs):
        value = real_stat(path, *args, **kwargs)
        if path == target_resolved:
            fields = list(value)
            fields[6] = 1
            return os.stat_result(fields)
        return value

    monkeypatch.setattr(Path, "stat", misleading_path_stat)

    with pytest.raises(ValueError, match="size limit"):
        toolbox.run("read", "large.txt")


def test_mutating_action_never_calls_supplied_authority_or_toolbox(tmp_path, monkeypatch):
    calls = {"authority": 0, "toolbox": 0}

    class CountingAuthority:
        def evaluate(self, **_kwargs):
            calls["authority"] += 1
            raise AssertionError("mutating action reached authority")

    def unexpected_toolbox_call(*_args, **_kwargs):
        calls["toolbox"] += 1
        raise AssertionError("mutating action reached toolbox")

    monkeypatch.setattr(SafeReadOnlyToolbox, "run", unexpected_toolbox_call)
    rec = ToolActionHarness().execute_action(
        action_id="mutation-short-circuit",
        tool_ref="fs",
        action_type="write",
        target="doc.txt",
        evidence_refs=["ev://1"],
        sandbox_root=tmp_path,
        execution_authority=CountingAuthority(),
        lease_id="lease::must-not-be-used",
    )

    assert rec["status"] == "blocked-plan-only"
    assert calls == {"authority": 0, "toolbox": 0}

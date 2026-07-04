"""Depth D2: real sandboxed read-only tool EXECUTION (mutating stays plan-only)."""
from __future__ import annotations

from pathlib import Path

import pytest

from nexusnet.tools.action_harness import ToolActionHarness, SafeReadOnlyToolbox


def _sandbox(tmp_path: Path) -> Path:
    (tmp_path / "doc.txt").write_text("hello nexus hive", encoding="utf-8")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "a.txt").write_text("nested", encoding="utf-8")
    return tmp_path


def test_read_action_actually_reads(tmp_path):
    root = _sandbox(tmp_path)
    h = ToolActionHarness()
    rec = h.execute_action(action_id="r1", tool_ref="fs", action_type="read", target="doc.txt",
                           evidence_refs=["ev://1"], sandbox_root=root)
    assert rec["executed"] is True and rec["status"] == "executed-readonly"
    assert rec["result"]["text"] == "hello nexus hive"        # real content, not a stub
    assert rec["duration_ms"] >= 0.0


def test_list_and_hash_execute(tmp_path):
    root = _sandbox(tmp_path)
    h = ToolActionHarness()
    lst = h.execute_action(action_id="l1", tool_ref="fs", action_type="list", target=".",
                           evidence_refs=["ev://1"], sandbox_root=root)
    assert set(lst["result"]["entries"]) == {"doc.txt", "sub"}
    hsh = h.execute_action(action_id="h1", tool_ref="fs", action_type="hash", target="doc.txt",
                           evidence_refs=["ev://1"], sandbox_root=root)
    import hashlib
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
    rec = h.execute_action(action_id="t1", tool_ref="fs", action_type="read",
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


def test_plan_only_path_still_works(tmp_path):
    # the original non-executing plan path is unchanged (regression guard)
    h = ToolActionHarness()
    plan = h.plan_action(action_id="p1", tool_ref="fs", action_type="click",
                         requested_effect="press", contains_private_data=False,
                         sandbox_state="none", operator_approved=False, evidence_refs=["e"])
    assert plan["execution_allowed"] is False and plan["status"] == "blocked"

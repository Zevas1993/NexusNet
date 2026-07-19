from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_project_conftest():
    path = Path(__file__).with_name("conftest.py")
    spec = importlib.util.spec_from_file_location("nexusnet_tests_conftest", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_bounded_node_label_is_stable_filesystem_safe_and_short():
    conftest = _load_project_conftest()
    nodeid = (
        "tests/test_sandbox_agent_factory.py::"
        "test_sandbox_agent_factory_creates_real_worktree_and_passes_executable_merge_gates"
    )

    first = conftest._bounded_node_label(nodeid)
    second = conftest._bounded_node_label(nodeid)

    assert first == second
    assert len(first) <= 64
    assert first.startswith("tests-test_sandbox_agent_factory.py-test_sandbox")
    assert first.rsplit("-", 1)[-1].isalnum()

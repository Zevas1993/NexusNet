from __future__ import annotations

import pytest

from nexusnet.operations.projection_engine import IncrementalProjectionEngine
from nexusnet.workflows.execution import TypedWorkflowExecutor


def test_typed_workflow_executes_dag_and_enforces_mutating_capability():
    executor = TypedWorkflowExecutor(
        handlers={
            "constant": lambda node, _inputs: node["config"]["value"],
            "sum": lambda _node, inputs: sum(inputs.values()),
            "write": lambda node, inputs: {"target": node["config"]["target"], "value": sum(inputs.values())},
        }
    )
    workflow = {
        "nodes": [
            {"node_id": "a", "kind": "constant", "effect": "read", "config": {"value": 2}},
            {"node_id": "b", "kind": "constant", "effect": "read", "config": {"value": 3}},
            {"node_id": "total", "kind": "sum", "effect": "compute", "config": {}},
            {"node_id": "save", "kind": "write", "effect": "write", "config": {"target": "artifact:sum"}},
        ],
        "edges": [["a", "total"], ["b", "total"], ["total", "save"]],
    }
    with pytest.raises(PermissionError):
        executor.execute(workflow, capability_effects={"read", "compute"})
    result = executor.execute(workflow, capability_effects={"read", "compute", "write"})

    assert result["status"] == "executed"
    assert result["outputs"]["save"] == {"target": "artifact:sum", "value": 5}
    assert result["execution_order"] == ["a", "b", "total", "save"]


def test_incremental_projection_replays_only_new_events_and_survives_restart(tmp_path):
    engine = IncrementalProjectionEngine(artifacts_dir=tmp_path)
    engine.register_reducer("counts", initial={"total": 0}, reducer=lambda state, event: {"total": state["total"] + event["delta"]})
    engine.append(event_id="event:1", event_type="increment", payload={"delta": 2}, source_refs=["trace:1"])
    first = engine.project("counts")
    engine.append(event_id="event:2", event_type="increment", payload={"delta": 3}, source_refs=["trace:2"])
    second = engine.project("counts")

    assert first["state"] == {"total": 2}
    assert second["state"] == {"total": 5}
    assert second["applied_event_count"] == 1

    restarted = IncrementalProjectionEngine(artifacts_dir=tmp_path)
    restarted.register_reducer("counts", initial={"total": 0}, reducer=lambda state, event: {"total": state["total"] + event["delta"]})
    replay = restarted.project("counts")
    assert replay["state"] == {"total": 5}
    assert replay["applied_event_count"] == 0

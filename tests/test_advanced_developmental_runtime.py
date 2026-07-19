from __future__ import annotations

from nexusnet.developmental.advanced import AdvancedDevelopmentalRuntime
from nexusnet.developmental.kernel import DevelopmentalCortexKernel


def test_advanced_developmental_runtime_executes_all_canon_mechanisms():
    runtime = AdvancedDevelopmentalRuntime(seed=7)
    result = runtime.assess(
        request_id="req:advanced",
        task_ref="improve gpu offload",
        trace_refs=["trace:latency", "trace:memory-pressure"],
        evidence_refs=["eval:baseline"],
        runtime_state={"latency_error": 0.8, "resource_pressure": 0.7, "policy_risk": 0.1},
        memory_state={"contradiction": 0.6, "uncertainty": 0.5},
        eval_state={"quality": 0.55, "failed": True},
    )

    assert result["homeostasis"]["selected_action"] in {"reduce-load", "seek-evidence", "repair-memory", "hold"}
    assert result["replay_consolidation"]["replay_count"] == 2
    assert result["world_model_rollout"]["rollout_count"] >= 2
    assert len(result["diverse_candidates"]["selected"]) >= 2
    assert result["cellular_growth"]["cell_count"] >= 3
    assert result["neuromorphic_events"]["processed_count"] >= 1
    assert result["continuous_controller"]["state"]
    assert result["combinatorial_search"]["combination_count"] >= 1
    assert result["symbolic_change"]["changes"]
    assert result["production_mutation_allowed"] is False


def test_developmental_kernel_includes_advanced_runtime_without_production_mutation(tmp_path):
    result = DevelopmentalCortexKernel(artifacts_dir=tmp_path).assess(
        request_id="req:kernel-advanced",
        task_ref="task:optimize",
        trace_refs=["trace:1"],
        evidence_refs=["evidence:1"],
        runtime_state={"latency_error": 0.2, "resource_pressure": 0.3},
        memory_state={"uncertainty": 0.2},
        authority_state={"decision": "allow-shadow"},
        eval_state={"quality": 0.8, "failed": False},
    )

    assert result["advanced_development"]["surface_id"] == "advanced-developmental-runtime"
    assert result["advanced_development"]["production_mutation_allowed"] is False
    assert result["production_mutation_allowed"] is False

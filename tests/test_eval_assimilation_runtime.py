from __future__ import annotations

from nexusnet.evals.assimilation_runtime import (
    BenchmarkHarnessFederation,
    DeterministicFailureFoundry,
    RuntimeMonitorSynthesizer,
)


def test_failure_foundry_replays_seeded_failures_deterministically():
    foundry = DeterministicFailureFoundry()
    first = foundry.run(
        scenario_id="network-flap",
        seed=42,
        components=["model", "network", "memory"],
        step_count=12,
        failure_probability=0.35,
    )
    second = foundry.run(
        scenario_id="network-flap",
        seed=42,
        components=["model", "network", "memory"],
        step_count=12,
        failure_probability=0.35,
    )

    assert first["schedule"] == second["schedule"]
    assert first["replay_digest"] == second["replay_digest"]
    assert first["failure_count"] > 0


def test_runtime_monitor_is_compiled_from_invariants_and_trips_actions():
    monitor = RuntimeMonitorSynthesizer().compile(
        monitor_id="runtime-slo",
        invariants=[
            {"metric": "error_rate", "operator": "<=", "threshold": 0.02, "action": "rollback"},
            {"metric": "free_vram_gib", "operator": ">=", "threshold": 1.0, "action": "reduce-load"},
        ],
    )
    result = monitor.evaluate({"error_rate": 0.08, "free_vram_gib": 0.5})

    assert result["status"] == "tripped"
    assert result["actions"] == ["reduce-load", "rollback"]
    assert len(result["violations"]) == 2


def test_benchmark_federation_executes_real_adapters_and_normalizes_results():
    federation = BenchmarkHarnessFederation()
    federation.register("swe-bench", lambda case: {"passed": case["patch_applies"], "score": 1.0 if case["patch_applies"] else 0.0})
    federation.register("browsergym", lambda case: {"passed": case["goal_reached"], "score": case["reward"]})

    suite = federation.run_suite(
        suite_id="agent-cert",
        cases=[
            {"adapter": "swe-bench", "case_id": "swe:1", "patch_applies": True},
            {"adapter": "browsergym", "case_id": "web:1", "goal_reached": False, "reward": 0.4},
        ],
        evidence_refs=["dataset:swe", "dataset:web"],
    )

    assert suite["case_count"] == 2
    assert suite["pass_count"] == 1
    assert suite["mean_score"] == 0.7
    assert suite["promotion_allowed"] is False

from __future__ import annotations

import math

from nexusnet.hive.collective import (
    PheromoneField,
    quorum_decision,
    pso_minimize,
    differential_evolution,
    kd_loss,
    kl_divergence,
    prioritized_replay,
    consolidate,
)


# --- stigmergy ---

def test_trails_decay_to_zero_without_deposits():
    field = PheromoneField(evaporation_rate=0.5)
    field.step({"a->b": 1.0})
    assert field.strength("a->b") == 1.0
    prev = field.strength("a->b")
    for _ in range(20):
        field.step()                       # no deposits
        assert field.strength("a->b") < prev
        prev = field.strength("a->b")
    assert field.strength("a->b") < 1e-5


def test_routing_affinity_is_a_distribution():
    field = PheromoneField(evaporation_rate=0.1)
    field.step({"x": 2.0, "y": 1.0, "z": 1.0})
    affinity = field.routing_affinity()
    assert abs(sum(affinity.values()) - 1.0) < 1e-9
    assert affinity["x"] > affinity["y"]


# --- quorum ---

def test_quorum_blocks_below_threshold():
    d = quorum_decision(support_votes=3, total_agents=10, quorum_threshold=0.66)
    assert d["committed"] is False
    assert d["reason"] == "below_quorum"


def test_stop_signal_vetoes_even_at_full_support():
    d = quorum_decision(support_votes=10, total_agents=10, quorum_threshold=0.66, stop_signal=True)
    assert d["committed"] is False
    assert d["reason"] == "stop_signal_active"


def test_quorum_commits_when_reached_and_no_stop():
    d = quorum_decision(support_votes=8, total_agents=10, quorum_threshold=0.66)
    assert d["committed"] is True
    assert d["reason"] == "quorum_reached"


# --- swarm (PSO) ---

def _sphere(v):
    return sum(x * x for x in v)


def test_pso_global_best_is_monotonically_nonincreasing():
    res = pso_minimize(_sphere, dim=3, iterations=25, seed=7)
    hist = res["score_history"]
    for earlier, later in zip(hist, hist[1:]):
        assert later <= earlier + 1e-12


def test_pso_converges_toward_optimum():
    res = pso_minimize(_sphere, dim=3, iterations=60, num_particles=20, seed=7)
    assert res["gbest_score"] < 0.5          # sphere optimum is 0


def test_pso_is_deterministic():
    a = pso_minimize(_sphere, dim=3, iterations=20, seed=11)["gbest_score"]
    b = pso_minimize(_sphere, dim=3, iterations=20, seed=11)["gbest_score"]
    assert a == b


# --- differential evolution ---

def test_de_best_score_never_worsens():
    res = differential_evolution(_sphere, dim=4, generations=30, seed=3)
    hist = res["best_history"]
    for earlier, later in zip(hist, hist[1:]):
        assert later <= earlier + 1e-12     # elitist


def test_de_finds_near_optimum():
    res = differential_evolution(_sphere, dim=4, generations=80, pop_size=24, seed=3)
    assert res["best_score"] < 0.1


# --- distillation ---

def test_kl_is_nonnegative_and_zero_iff_equal():
    p = [0.2, 0.3, 0.5]
    assert abs(kl_divergence(p, p)) < 1e-9
    assert kl_divergence([0.5, 0.5], [0.9, 0.1]) > 0.0


def test_kd_loss_components_present_and_finite():
    out = kd_loss(
        student_logits=[1.0, 2.0, 0.5],
        teacher_logits=[0.8, 2.2, 0.4],
        hard_labels=[0.0, 1.0, 0.0],
        alpha=0.5,
        temperature=2.0,
    )
    assert out["soft_kl"] >= 0.0
    assert math.isfinite(out["loss"])
    assert out["distill_term"] >= 0.0


# --- neural sleep ---

def test_replay_distribution_sums_to_one():
    res = prioritized_replay(saliences=[0.1, 0.9, 0.5, 0.3], replay_count=2)
    assert abs(sum(res["distribution"]) - 1.0) < 1e-9
    assert res["replayed_indices"] == [1, 2]      # top-2 by salience


def test_consolidation_promotes_stable_patterns():
    res = consolidate(
        strengths=[0.6, 0.1, 0.8],
        activations=[1.0, 0.0, 1.0],
        decay=0.5,
        promote_threshold=0.7,
    )
    # updated: [0.8, 0.05, 0.9] -> indices 0 and 2 promoted
    assert res["promoted_abstractions"] == [0, 2]
    assert res["production_mutation_allowed"] is False

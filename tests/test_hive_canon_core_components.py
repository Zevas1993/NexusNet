"""Canon C35 §6 components that had zero implementation - now real, behavior-verified."""
from __future__ import annotations

import random

import numpy as np

from nexusnet.hive.canon_core_components import (
    TensorNetworkCompression, QuantumInspiredEmbedding, NeuralDNA, FractalCompression,
    AdaptiveCreativity, EnergyManager, MultiAgentSimulation,
)


# --- 6.2 ---
def test_tensor_network_compression_reduces_size_and_reconstructs():
    rng = np.random.default_rng(0)
    low_rank = rng.standard_normal((40, 3)) @ rng.standard_normal((3, 40))   # rank-3 matrix
    res = TensorNetworkCompression().compress(low_rank, rank=3)
    assert res["compression_ratio"] > 1.0
    assert res["rel_error"] < 1e-6                       # rank-3 truncation is near-lossless


# --- 6.3 ---
def test_quantum_embedding_superpose_entangle_measure():
    q = QuantumInspiredEmbedding()
    a = q.embed([1.0, 0.0]); b = q.embed([0.0, 1.0])
    sup = q.superpose([a, b])
    assert abs(np.linalg.norm(sup) - 1.0) < 1e-6        # superposition stays unit-norm
    ent = q.entangle(a, b)
    assert ent.shape == (4,) and abs(np.linalg.norm(ent) - 1.0) < 1e-6  # tensor-product joint state
    probs = q.measure(sup)
    assert abs(probs.sum() - 1.0) < 1e-6                 # Born-rule probabilities
    assert q.interference(a, b)["measured_sums_to_one"] is True


# --- 6.6 ---
def test_neural_dna_id_mutate_crossover_express():
    pools = {"d_model": [32, 64], "layers": [1, 2, 3]}
    rng = random.Random(0)
    dna = NeuralDNA(genes={"d_model": 64, "layers": 2})
    assert dna.dna_id().startswith("dna:")
    child = dna.mutate(rng, pools=pools)
    assert child.dna_id() != dna.dna_id() or child.genes != dna.genes
    assert dna.dna_id() in child.lineage              # heritable lineage
    mate = NeuralDNA(genes={"d_model": 32, "layers": 3})
    cross = dna.crossover(mate, rng)
    assert set(cross.genes) == {"d_model", "layers"}
    assert cross.express() == cross.genes


# --- 6.7 ---
def test_fractal_compression_dedups_self_similar_blocks():
    seq = [1, 2, 3, 4] * 8                              # highly self-similar
    res = FractalCompression().compress(seq, block=4, tol=0.01)
    assert res["unique_blocks"] == 1 and res["total_blocks"] == 8
    assert res["compression_ratio"] == 8.0 and res["rel_error"] < 1e-6


# --- 6.12 ---
def test_adaptive_creativity_raises_temperature_when_stuck():
    ac = AdaptiveCreativity()
    calm = ac.creativity(uncertainty=0.0, repetition=0.0)
    stuck = ac.creativity(uncertainty=0.9, repetition=0.9, exploratory=True)
    assert stuck["temperature"] > calm["temperature"]
    assert stuck["mode"] == "explore" and calm["mode"] == "focus"
    assert stuck["novelty_bonus"] > calm["novelty_bonus"]


# --- 6.22 ---
def test_energy_manager_accounts_and_throttles():
    em = EnergyManager(budget_joules=100.0, joules_per_gflop=1.0)
    em.account(gflops=60)
    assert em.throttle_factor() < 1.0                   # budget partly spent -> throttle down
    r = em.account(gflops=60)
    assert r["over_budget"] is True                     # exceeded budget
    rep = em.report()
    assert rep["efficiency_gflops_per_joule"] > 0 and rep["throttle_factor"] >= 0.1


# --- 6.28 ---
def test_multi_agent_simulation_runs_and_scores():
    agents = {
        "cooperator": lambda s: True,
        "defector": lambda s: False,
        "tit_for_tat": lambda s: (s.get("last_actions", {}).get("cooperator", True)),
    }
    sim = MultiAgentSimulation(agents)
    res = sim.run(rounds=5)
    assert res["rounds"] == 5 and len(res["trace"]) == 5
    assert res["scores"]["cooperator"] == 5.0          # cooperates every round
    assert res["scores"]["defector"] == 0.0
    assert res["winner"] == "cooperator"

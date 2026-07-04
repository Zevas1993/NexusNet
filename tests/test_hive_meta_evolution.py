"""Canon Aspect 14: real meta-evolution - evolve the model genome against real training fitness."""
from __future__ import annotations

import random

import pytest

torch = pytest.importorskip("torch")

from nexusnet.hive.net import (
    ModelGenome, random_genome, mutate, crossover, genome_fitness, evolve_architecture,
    NexusNetLM, domain_corpus_for_capsule, make_corpus_windows, split_windows,
)


def _data(seed=0):
    corpus = domain_corpus_for_capsule("mathematician", n_sentences=140, seed=seed, rich=True)
    x, y = make_corpus_windows(corpus, seq_len=16)
    return split_windows(x, y, val_fraction=0.3, seed=seed)


def test_genomes_are_always_valid_after_repair():
    rng = random.Random(0)
    for _ in range(50):
        g = random_genome(rng)
        assert g.d_model % g.n_heads == 0
        assert g.n_heads % g.n_kv_heads == 0
        assert g.top_k <= g.num_experts
        # repaired genome builds a real model
        NexusNetLM(**g.to_config())


def test_mutate_and_crossover_stay_valid():
    rng = random.Random(1)
    a, b = random_genome(rng), random_genome(rng)
    for _ in range(30):
        m = mutate(a, rng)
        c = crossover(a, b, rng)
        for g in (m, c):
            assert g.d_model % g.n_heads == 0 and g.top_k <= g.num_experts
    # an intentionally-broken genome is repaired into validity
    broken = ModelGenome(d_model=48, n_heads=4, n_kv_heads=3, num_experts=4, top_k=9, num_layers=2)
    r = broken.repaired()
    assert r.n_heads % r.n_kv_heads == 0 and r.top_k <= r.num_experts


def test_genome_fitness_is_real_training():
    x_tr, y_tr, x_val, y_val = _data(0)
    g = ModelGenome(d_model=48, n_heads=4, n_kv_heads=2, num_experts=4, top_k=2, num_layers=2)
    fit = genome_fitness(g, x_tr, y_tr, x_val, y_val, epochs=15, seed=0)
    assert fit["val_loss"] > 0 and fit["params"] > 0
    assert fit["fitness"] == pytest.approx(-fit["val_loss"] - 1e-7 * fit["params"], abs=1e-6)


def test_evolution_searches_and_does_not_regress_best():
    x_tr, y_tr, x_val, y_val = _data(0)
    res = evolve_architecture(x_tr, y_tr, x_val, y_val, population=4, generations=3, elite=2,
                              epochs=12, seed=0)
    assert res["generations"] == 3 and len(res["history"]) == 3
    # elitism: best fitness is monotonically non-decreasing across generations
    best_seq = [h["best_fitness"] for h in res["history"]]
    assert all(best_seq[i + 1] >= best_seq[i] - 1e-9 for i in range(len(best_seq) - 1))
    assert res["improved"] is True
    # the winning genome is a real, buildable architecture
    NexusNetLM(**ModelGenome(**res["best_genome"]).to_config())
    assert res["best_val_loss"] > 0 and res["best_params"] > 0

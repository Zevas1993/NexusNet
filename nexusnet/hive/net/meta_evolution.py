"""Canon Aspect 14: real META-EVOLUTION - evolve the model GENOME against real training fitness.

`growth/engine.py` carries a `model_genome` as a YAML DESCRIPTOR; nothing evolves it. Canon (native
growth / meta-evolution, C04/C38) wants NexusNet to search its own architecture. This is a real
evolutionary search over a `ModelGenome` (architecture/hyperparameter genes) where FITNESS is an
actual short training run + held-out loss of a `NexusNetLM` built from that genome, with a small
parameter-efficiency penalty (canon: efficient). Population -> fitness -> elitist select ->
crossover + mutate -> repeat. Deterministic; tiny by default (CPU-runnable), scales up via config.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, asdict
from typing import Any

import torch

from .lm import NexusNetLM
from .birth import train_language_model
from .eval_gates import measure_language_model

_D_MODEL = [32, 48, 64]
_N_HEADS = [2, 4]
_NUM_EXPERTS = [4, 6, 8]
_TOP_K = [1, 2]
_NUM_LAYERS = [1, 2, 3]


@dataclass
class ModelGenome:
    d_model: int = 48
    n_heads: int = 4
    n_kv_heads: int = 2
    num_experts: int = 6
    top_k: int = 2
    num_layers: int = 2

    def repaired(self) -> "ModelGenome":
        """Enforce the validity constraints (divisibility, top_k <= experts) - genomes stay buildable."""
        d_model = self.d_model if self.d_model in _D_MODEL else 48
        n_heads = self.n_heads if (d_model % self.n_heads == 0) else 4
        n_kv = self.n_kv_heads if (n_heads % self.n_kv_heads == 0 and self.n_kv_heads >= 1) else 2
        if n_heads % n_kv != 0:
            n_kv = 1
        experts = self.num_experts if self.num_experts in _NUM_EXPERTS else 6
        top_k = min(self.top_k, experts)
        layers = self.num_layers if self.num_layers in _NUM_LAYERS else 2
        return ModelGenome(d_model, n_heads, n_kv, experts, max(1, top_k), layers)

    def to_config(self, *, vocab_size: int = 259) -> dict[str, Any]:
        g = self.repaired()
        return {"vocab_size": vocab_size, "d_model": g.d_model, "n_heads": g.n_heads,
                "n_kv_heads": g.n_kv_heads, "num_experts": g.num_experts, "top_k": g.top_k,
                "d_hidden": 2 * g.d_model, "num_layers": g.num_layers}


def random_genome(rng: random.Random) -> ModelGenome:
    d_model = rng.choice(_D_MODEL)
    n_heads = rng.choice([h for h in _N_HEADS if d_model % h == 0])
    return ModelGenome(
        d_model=d_model, n_heads=n_heads, n_kv_heads=rng.choice([h for h in (1, 2) if n_heads % h == 0]),
        num_experts=rng.choice(_NUM_EXPERTS), top_k=rng.choice(_TOP_K),
        num_layers=rng.choice(_NUM_LAYERS),
    ).repaired()


def mutate(genome: ModelGenome, rng: random.Random) -> ModelGenome:
    """Mutate one gene at random, then repair to a valid genome."""
    g = asdict(genome)
    gene = rng.choice(list(g))
    pool = {"d_model": _D_MODEL, "n_heads": _N_HEADS, "n_kv_heads": [1, 2],
            "num_experts": _NUM_EXPERTS, "top_k": _TOP_K, "num_layers": _NUM_LAYERS}[gene]
    g[gene] = rng.choice(pool)
    return ModelGenome(**g).repaired()


def crossover(a: ModelGenome, b: ModelGenome, rng: random.Random) -> ModelGenome:
    """Per-gene uniform crossover, then repair."""
    da, db = asdict(a), asdict(b)
    child = {k: (da[k] if rng.random() < 0.5 else db[k]) for k in da}
    return ModelGenome(**child).repaired()


def genome_fitness(
    genome: ModelGenome, x_tr, y_tr, x_val, y_val, *, epochs: int = 20, seed: int = 0,
    efficiency_penalty: float = 1e-7,
) -> dict[str, Any]:
    """REAL fitness: build the genome's NexusNetLM, train briefly, score held-out. Higher = better."""
    torch.manual_seed(seed)
    model = NexusNetLM(**genome.to_config())
    train_language_model(model, x_tr, y_tr, epochs=epochs, val_x=x_val, val_y=y_val)
    m = measure_language_model(model, x_val, y_val)
    params = model.num_parameters()
    fitness = -m["val_loss"] - efficiency_penalty * params       # accuracy with an efficiency pull
    return {"fitness": fitness, "val_loss": m["val_loss"], "params": params}


def evolve_architecture(
    x_tr, y_tr, x_val, y_val, *,
    population: int = 4, generations: int = 3, elite: int = 2, epochs: int = 18, seed: int = 0,
) -> dict[str, Any]:
    """Evolutionary architecture/hyperparameter search wired to real training fitness."""
    rng = random.Random(seed)
    pop = [random_genome(rng) for _ in range(population)]
    history: list[dict[str, Any]] = []
    best: tuple[float, ModelGenome, dict] | None = None
    cache: dict[tuple, dict] = {}                                 # genome -> fitness (deterministic)

    def _fit(g: ModelGenome) -> dict[str, Any]:
        key = tuple(sorted(asdict(g.repaired()).items()))
        if key not in cache:
            # seed is a STABLE function of the genome, so a genome's fitness never drifts -> true elitism
            gseed = seed + (abs(hash(key)) % 9973)
            cache[key] = genome_fitness(g, x_tr, y_tr, x_val, y_val, epochs=epochs, seed=gseed)
        return cache[key]

    for gen in range(generations):
        scored = []
        for g in pop:
            fit = _fit(g)
            scored.append((fit["fitness"], g, fit))
        scored.sort(key=lambda t: t[0], reverse=True)
        if best is None or scored[0][0] > best[0]:
            best = scored[0]
        history.append({"generation": gen, "best_fitness": scored[0][0],
                        "best_val_loss": scored[0][2]["val_loss"],
                        "mean_fitness": sum(s[0] for s in scored) / len(scored)})
        elites = [g for _, g, _ in scored[:elite]]
        children: list[ModelGenome] = []
        while len(children) < population - elite:
            pa, pb = rng.choice(elites), rng.choice(elites)
            children.append(mutate(crossover(pa, pb, rng), rng))
        pop = elites + children
    return {
        "best_genome": asdict(best[1]),
        "best_fitness": best[0],
        "best_val_loss": best[2]["val_loss"],
        "best_params": best[2]["params"],
        "generations": generations,
        "population": population,
        "history": history,
        "improved": history[-1]["best_fitness"] >= history[0]["best_fitness"],
    }

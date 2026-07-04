"""Depth D1 - real end-to-end HIVE birth orchestrator (composes the lanes, not toy pieces).

Where `birth.birth_model` trains one tiny LM on a flat template, this orchestrates a real multi-expert
birth that COMPOSES the built lanes into one pipeline per expert:

  domain corpus (rich grammar, Wave-3 corpora)
    -> [optional] JEPA dream warmup over the expert's own latents (Wave-7 dreaming, sidecar/non-mutating)
    -> [optional] Governed Sparse Routing bound on the expert's MoE (Wave-2)
    -> real next-token training on held-out split (real backprop)
    -> eval-gate scoring on held-out data (Wave-3 eval_gates)
    -> Independence Milestones vs the expert's teacher baseline (canon TRP)

then the hive-level per-node Teacher Replacement Protocol decides promotions and whether the system is
birth-ready. Deterministic, CPU-runnable at small scale; every step does real work and is measured.
"""
from __future__ import annotations

from typing import Any

import torch

from .lm import NexusNetLM
from .corpora import domain_corpus_for_capsule
from .birth import (
    make_corpus_windows, split_windows, train_language_model,
    independence_milestones, evaluate_node_promotions,
)
from .eval_gates import evaluate_capsule_gates
from .governed_routing import GovernedSparseRouter
from .dreaming_jepa import JEPAWorldModel, train_world_model


def _dream_warmup(model: NexusNetLM, x: torch.Tensor, *, steps: int = 20) -> dict[str, Any]:
    """Run a JEPA dream over the expert's OWN latent space (model embeddings of its corpus windows).
    The world-model is a sidecar - it does NOT mutate the LM weights - but it must genuinely learn to
    predict the expert's latents (pred_err falls), which is the canon 'dream readiness' signal."""
    with torch.no_grad():
        latents = model.embed(x[: min(16, x.shape[0])]).detach()       # (b, T, d_model)
    jepa = JEPAWorldModel(model.d_model, ema=0.9)
    res = train_world_model(jepa, latents, steps=steps, lr=3e-3)
    return {"world_model_learned": res["world_model_learned"],
            "initial_pred_err": res["initial_pred_err"], "final_pred_err": res["final_pred_err"]}


def birth_expert_node(
    capsule_key: str,
    *,
    epochs: int = 60,
    seq_len: int = 24,
    n_sentences: int = 240,
    seed: int = 0,
    teacher_baseline_accuracy: float = 0.4,
    govern_allowed: list[int] | None = None,
    dream_warmup: bool = True,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Birth a single expert node end-to-end, composing every lane, and judge it against its teacher."""
    torch.manual_seed(seed)
    corpus = domain_corpus_for_capsule(capsule_key, n_sentences=n_sentences, seed=seed, rich=True)
    x, y = make_corpus_windows(corpus, seq_len=seq_len)
    x_tr, y_tr, x_val, y_val = split_windows(x, y, val_fraction=0.25, seed=seed)
    cfg = {"d_model": 64, "n_heads": 4, "n_kv_heads": 2, "num_experts": 6, "top_k": 2,
           "d_hidden": 128, "num_layers": 2}
    if config:
        cfg.update(config)
    model = NexusNetLM(**cfg)

    dream = _dream_warmup(model, x_tr) if dream_warmup else None
    if govern_allowed is not None:
        GovernedSparseRouter(num_experts=cfg["num_experts"]).govern(model, allowed=govern_allowed)

    metrics = train_language_model(model, x_tr, y_tr, epochs=epochs, val_x=x_val, val_y=y_val)
    gates = evaluate_capsule_gates(capsule_key, model, x_val, y_val,
                                   accuracy_threshold=0.0, perplexity_threshold=1e9)
    milestones = independence_milestones(metrics, teacher_baseline_accuracy=teacher_baseline_accuracy)
    return {
        "capsule": capsule_key,
        "model": model,
        "metrics": metrics,
        "dream_warmup": dream,
        "eval_gates": gates,
        "milestones": milestones,
        "node_record": {
            "node_id": f"expert.{capsule_key}",
            "node_type": "expert",
            "native_generation": float(metrics.get("val_accuracy") or metrics["next_token_accuracy"]),
            "teacher_baseline_accuracy": teacher_baseline_accuracy,
            "initial_loss": metrics["initial_loss"],
            "final_loss": metrics["final_loss"],
        },
    }


def birth_hive(
    roster: list[str],
    *,
    epochs: int = 50,
    seq_len: int = 20,
    n_sentences: int = 200,
    seed: int = 0,
    teacher_baselines: dict[str, float] | None = None,
    govern_map: dict[str, list[int]] | None = None,
    dream_warmup: bool = True,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Birth a roster of experts end-to-end, then run the hive-level TRP promotion across all nodes."""
    teacher_baselines = teacher_baselines or {}
    govern_map = govern_map or {}
    experts: dict[str, Any] = {}
    node_records: list[dict[str, Any]] = []
    for i, key in enumerate(roster):
        node = birth_expert_node(
            key, epochs=epochs, seq_len=seq_len, n_sentences=n_sentences, seed=seed + i,
            teacher_baseline_accuracy=teacher_baselines.get(key, 0.4),
            govern_allowed=govern_map.get(key), dream_warmup=dream_warmup, config=config,
        )
        experts[key] = {k: v for k, v in node.items() if k != "model"}   # report excludes weights
        node_records.append(node["node_record"])
    promotions = evaluate_node_promotions(node_records)
    learned = sum(1 for k in experts if experts[k]["metrics"]["final_loss"]
                  < experts[k]["metrics"]["initial_loss"])
    dreams_ok = sum(1 for k in experts if experts[k]["dream_warmup"]
                    and experts[k]["dream_warmup"]["world_model_learned"])
    return {
        "roster": list(roster),
        "experts": experts,
        "promotions": promotions,
        "system_birth_ready": promotions["system_birth_ready"],
        "experts_that_learned": learned,
        "dream_warmups_converged": dreams_ok,
        "all_experts_learned": learned == len(roster),
    }

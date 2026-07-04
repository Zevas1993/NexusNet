"""Capstone: the COMPLETE birth pipeline composing every real lane built this session.

This is the womb's full process end-to-end, wiring the previously-standalone mechanisms together:

  1. META-EVOLUTION (Aspect 14): search the architecture genome against real training fitness on a
     probe of the roster's domain corpora -> the winning config.
  2. per-EXPERT BIRTH (D1 orchestrator): rich domain corpus -> JEPA dream warmup -> Governed Sparse
     Routing -> real training -> eval-gate scoring -> Independence Milestones, using the evolved config.
  3. RECURSIVE DREAM SELF-IMPROVEMENT (PB-034 loop): each expert dreams from its own failures and
     keeps the gated, eval-improving updates.
  4. hive-level per-node TRP PROMOTION (canon): decide which experts surpass their teachers.
  5. EXPORT (Aspect 4/12): write the best birthed expert to runtime formats (born artifact).

Deterministic, CPU-runnable at small scale; every step does real work. Flags let callers turn each
lane on/off. This is the single object that demonstrates "the womb runs its whole process."
"""
from __future__ import annotations

from typing import Any

import torch

from .corpora import domain_corpus_for_capsule
from .birth import make_corpus_windows, split_windows, evaluate_node_promotions
from .birth_orchestrator import birth_expert_node
from .recursive_dream_training import recursive_dream_cycles
from .meta_evolution import evolve_architecture
from .eval_gates import measure_language_model
from .quantize_export import export_birthed_model
from .expert_assimilation import assimilate_expert, make_swiglu_expert
from .base_model_attach import attach_base_model_adapters, inspect_base_model
from .efficiency_autopilot import EfficiencyAutopilot
from .absorption import absorb_wrapper


def _probe_data(roster: list[str], *, seq_len: int, n_sentences: int, seed: int):
    corpus = "".join(domain_corpus_for_capsule(k, n_sentences=n_sentences // max(1, len(roster)),
                                               seed=seed, rich=True) for k in roster)
    x, y = make_corpus_windows(corpus, seq_len=seq_len)
    return split_windows(x, y, val_fraction=0.3, seed=seed)


def full_birth(
    roster: list[str],
    *,
    evolve: bool = True,
    dream_self_improve: bool = True,
    export: bool = True,
    out_dir: str | None = None,
    epochs: int = 30,
    seq_len: int = 18,
    n_sentences: int = 160,
    dream_cycles: int = 2,
    evo_population: int = 4,
    evo_generations: int = 2,
    assimilate_extra_expert: bool = False,
    attach_adapters: bool = False,
    improve_efficiency: bool = True,
    teacher_baselines: dict[str, float] | None = None,
    govern_map: dict[str, list[int]] | None = None,
    seed: int = 0,
) -> dict[str, Any]:
    """Run the complete womb birth process over a roster and return a consolidated report."""
    teacher_baselines = teacher_baselines or {}
    govern_map = govern_map or {}

    # 1) META-EVOLUTION: search architecture on a probe of the roster's domains.
    evolution = None
    config = None
    if evolve:
        xt, yt, xv, yv = _probe_data(roster, seq_len=seq_len, n_sentences=n_sentences, seed=seed)
        evolution = evolve_architecture(xt, yt, xv, yv, population=evo_population,
                                        generations=evo_generations, elite=2,
                                        epochs=max(10, epochs // 2), seed=seed)
        g = evolution["best_genome"]
        config = {"d_model": g["d_model"], "n_heads": g["n_heads"], "n_kv_heads": g["n_kv_heads"],
                  "num_experts": g["num_experts"], "top_k": g["top_k"],
                  "d_hidden": 2 * g["d_model"], "num_layers": g["num_layers"]}

    # born experts carry ALL native wrapper features (so they can absorb/supersede the wrapper).
    config = {**(config or {}), "full_features": True}

    # 2-3) per-expert birth + recursive dream self-improvement.
    experts: dict[str, Any] = {}
    node_records: list[dict[str, Any]] = []
    models: dict[str, Any] = {}
    for i, key in enumerate(roster):
        node = birth_expert_node(
            key, epochs=epochs, seq_len=seq_len, n_sentences=n_sentences, seed=seed + i,
            teacher_baseline_accuracy=teacher_baselines.get(key, 0.35),
            govern_allowed=govern_map.get(key), dream_warmup=True, config=config,
        )
        model = node["model"]

        # ASSIMILATION (Aspect 2): grow the expert's MoE capacity by grafting a fresh capsule.
        assimilation = None
        if assimilate_extra_expert:
            moe = model.blocks[0].moe
            donor = make_swiglu_expert(model.d_model, 2 * model.d_model)
            assimilation = assimilate_expert(moe, donor)
        # BRAIN-FIRST ATTACH (Aspect 1): freeze the born base + inject trainable LoRA adapters so the
        # model can be further domain-adapted without disturbing the trained network.
        adapters = None
        if attach_adapters:
            before = inspect_base_model(model)
            adapters = attach_base_model_adapters(model, rank=4,
                                                  target_names=("q_proj", "k_proj", "v_proj"))
            adapters["base_linear_count"] = before["linear_count"]

        dream = None
        if dream_self_improve and not attach_adapters:   # adapters freeze the base; skip self-train then
            corpus = domain_corpus_for_capsule(key, n_sentences=n_sentences, seed=seed + i, rich=True)
            x, y = make_corpus_windows(corpus, seq_len=seq_len)
            x_tr, y_tr, x_val, y_val = split_windows(x, y, val_fraction=0.25, seed=seed + i)
            dream = recursive_dream_cycles(model, x_tr, y_tr, x_val, y_val, cycles=dream_cycles,
                                           dream_steps=15, shadow_epochs=10, seed=seed + i)
            node["metrics"]["val_loss"] = dream["final_val_loss"]
        models[key] = model
        experts[key] = {k: v for k, v in node.items() if k != "model"}
        experts[key]["recursive_dream"] = dream
        experts[key]["assimilation"] = assimilation
        experts[key]["adapters"] = adapters
        node_records.append(node["node_record"])

    # 4) hive-level TRP promotion.
    promotions = evaluate_node_promotions(node_records)

    # 4b) AUTONOMOUS EFFICIENCY self-improvement: search bit-models/quants for each born expert and
    #     keep the most efficient one that passes the quality gate (continuous self-optimization).
    efficiency = None
    if improve_efficiency:
        efficiency = {k: EfficiencyAutopilot(error_budget=0.08).run(models[k], cycles=3)
                      for k in models}
        for k in models:
            experts[k]["efficiency"] = efficiency[k]

    # 5) EXPORT the best (lowest val-loss) birthed expert as the born artifact.
    export_report = None
    best_key = min(models, key=lambda k: measure_language_model(
        models[k], *_one_val(roster, k, seq_len, n_sentences, seed))["val_loss"]) if models else None
    if export and out_dir and best_key is not None:
        example = torch.randint(0, 259, (1, min(8, seq_len)))
        export_report = export_birthed_model(models[best_key], out_dir, example_input=example,
                                             config={"capsule": best_key}, formats=("safetensors", "gguf"))

    return {
        "roster": list(roster),
        "evolution": evolution,
        "config_used": config,
        "experts": experts,
        "promotions": promotions,
        "system_birth_ready": promotions["system_birth_ready"],
        "best_expert": best_key,
        "export": export_report,
        "efficiency": efficiency,
        "wrapper_absorption": absorb_wrapper(models[best_key]) if best_key else None,
        "lanes": {"meta_evolution": evolve, "dream_self_improve": dream_self_improve, "export": export,
                  "assimilate_extra_expert": assimilate_extra_expert, "attach_adapters": attach_adapters,
                  "improve_efficiency": improve_efficiency},
    }


def _one_val(roster, key, seq_len, n_sentences, seed):
    i = roster.index(key)
    corpus = domain_corpus_for_capsule(key, n_sentences=n_sentences, seed=seed + i, rich=True)
    x, y = make_corpus_windows(corpus, seq_len=seq_len)
    _, _, x_val, y_val = split_windows(x, y, val_fraction=0.25, seed=seed + i)
    return x_val, y_val

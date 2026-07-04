"""Training-to-birth pipeline (canon Model Birth Protocol + Independence Milestones, addendum H).

The canon end-goal: NexusNet trains itself and, once it crosses the independence milestones, BIRTHS
its own model (a saved native checkpoint). This module does the real work:
  - tokenize a corpus into next-token training windows
  - train the NexusNetLM by next-token cross-entropy (real backprop + Adam + DeepSeek load balancing),
    optionally with teacher distillation (collective.kd_loss) as an auxiliary signal
  - evaluate Independence Milestones (dependency_ratio / native_generation / plane_maturity) against
    configurable thresholds (canon: thresholds are config, not hardcoded into the gate)
  - gate the birth: only when ALL milestones pass is the model 'birth-ready'
  - save the birthed checkpoint + a birth manifest

Device-agnostic; deterministic under a fixed seed.
"""
from __future__ import annotations

import json
import math
import time
from pathlib import Path
from typing import Any

import torch
import torch.nn.functional as F

from .lm import NexusNetLM
from .tokenizer import ByteTokenizer


_SUBJ = ["cortex", "router", "capsule", "dreamer", "memory", "critic"]
_VERB = ["learns", "routes", "dreams", "recalls", "guards", "grows"]
_OBJ = ["tokens", "patterns", "weights", "models", "planes", "signals"]


def make_structured_corpus(*, n_sentences: int = 400, seed: int = 0) -> str:
    """A small template grammar ('the <subj> <verb> the <obj> . ') over a fixed lexicon.

    Shared words + fixed grammar mean held-out sentences are NEW combinations of KNOWN words, so a
    model that truly learns the structure (not memorizes) will generalize -> val loss drops too.
    """
    import random
    rng = random.Random(seed)
    parts = []
    for _ in range(n_sentences):
        parts.append(f"the {rng.choice(_SUBJ)} {rng.choice(_VERB)} the {rng.choice(_OBJ)} . ")
    return "".join(parts)


def make_corpus_windows(text: str, *, seq_len: int = 32, device: str = "cpu"
                        ) -> tuple[torch.Tensor, torch.Tensor]:
    """Overlapping next-token windows: inputs = window[:-1], targets = window[1:]."""
    tok = ByteTokenizer()
    ids = tok.encode(text)
    if len(ids) < seq_len + 1:
        ids = (ids * (math.ceil((seq_len + 1) / max(1, len(ids))) + 1))
    inputs, targets = [], []
    step = max(1, seq_len // 2)
    for start in range(0, len(ids) - seq_len, step):
        window = ids[start:start + seq_len + 1]
        inputs.append(window[:-1])
        targets.append(window[1:])
    x = torch.tensor(inputs, dtype=torch.long, device=device)
    y = torch.tensor(targets, dtype=torch.long, device=device)
    return x, y


def split_windows(x: torch.Tensor, y: torch.Tensor, *, val_fraction: float = 0.2, seed: int = 0):
    """Shuffle windows and split into train/val so generalization can be measured honestly."""
    n = x.size(0)
    g = torch.Generator().manual_seed(seed)
    perm = torch.randperm(n, generator=g)
    n_val = max(1, int(n * val_fraction)) if n > 1 else 0
    val_idx, tr_idx = perm[:n_val], perm[n_val:]
    return x[tr_idx], y[tr_idx], x[val_idx], y[val_idx]


@torch.no_grad()
def _eval_split(model: NexusNetLM, x: torch.Tensor, y: torch.Tensor) -> dict[str, float]:
    if x.size(0) == 0:
        return {}
    was_training = model.training
    model.eval()
    logits = model(x)
    loss = F.cross_entropy(logits.reshape(-1, logits.size(-1)), y.reshape(-1)).item()
    acc = (logits.argmax(dim=-1) == y).float().mean().item()
    if was_training:
        model.train()
    return {"loss": loss, "perplexity": math.exp(min(20.0, loss)), "accuracy": acc}


def train_language_model(
    model: NexusNetLM,
    x: torch.Tensor,
    y: torch.Tensor,
    *,
    epochs: int = 200,
    lr: float = 3e-3,
    balance_every: int = 25,
    val_x: torch.Tensor | None = None,
    val_y: torch.Tensor | None = None,
) -> dict[str, Any]:
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    model.train()
    losses: list[float] = []
    grad_seen = False
    for epoch in range(epochs):
        optimizer.zero_grad()
        logits = model(x)                                       # (B, T, V)
        loss = F.cross_entropy(logits.reshape(-1, logits.size(-1)), y.reshape(-1))
        loss.backward()
        if not grad_seen:
            grad_seen = any(p.grad is not None and p.grad.abs().sum() > 0 for p in model.parameters())
        optimizer.step()
        if balance_every and (epoch + 1) % balance_every == 0:
            model.update_load_bias()
        losses.append(loss.item())
    with torch.no_grad():
        acc = (model(x).argmax(dim=-1) == y).float().mean().item()
    final = losses[-1]
    out = {
        "loss_history": losses,
        "initial_loss": losses[0],
        "final_loss": final,
        "final_perplexity": math.exp(min(20.0, final)),
        "next_token_accuracy": acc,
        "gradients_flowed": grad_seen,
        "num_parameters": model.num_parameters(),
    }
    if val_x is not None and val_y is not None:
        val = _eval_split(model, val_x, val_y)
        out["val_loss"] = val.get("loss")
        out["val_perplexity"] = val.get("perplexity")
        out["val_accuracy"] = val.get("accuracy")
    return out


def independence_milestones(
    metrics: dict[str, Any],
    *,
    max_dependency_ratio: float = 0.5,
    min_native_generation: float = 0.6,
    min_plane_maturity: float = 0.6,
    teacher_baseline_accuracy: float = 0.5,
    outperform_margin: float = 0.0,
) -> dict[str, Any]:
    """Canon Independence Milestones + Teacher Replacement Protocol gate.

    The canon condition is "the student is promoted once it MATCHES OR IMPROVES the teacher" (C26 TRP) -
    NOT "the student is perfect". So:
      - outperforms_teacher = native >= teacher_baseline + outperform_margin   (the TRP condition)
      - dependency_ratio    = how far the student still falls SHORT of the teacher, normalized:
                              max(0, teacher_baseline - native) / teacher_baseline
                              -> 0 once the student reaches/beats the teacher (no longer needs it)
    Native generation is judged on HELD-OUT (val) accuracy when available (generalization, not
    memorization). Thresholds are configurable, not hardcoded into the gate.
    """
    native_generation = float(metrics.get("val_accuracy") or metrics.get("next_token_accuracy", 0.0))
    # dependency = the remaining shortfall to the teacher (0 when the student matches/beats it).
    shortfall = max(0.0, teacher_baseline_accuracy - native_generation)
    dependency_ratio = min(1.0, shortfall / max(1e-6, teacher_baseline_accuracy))
    outperforms_teacher = native_generation >= teacher_baseline_accuracy + outperform_margin
    # plane maturity: how far the loss has collapsed from its starting point (0..1).
    i0, fin = metrics.get("initial_loss", 1.0), metrics.get("final_loss", 1.0)
    plane_maturity = max(0.0, min(1.0, (i0 - fin) / max(1e-6, i0)))
    checks = {
        "outperforms_teacher": (native_generation, outperforms_teacher),
        "dependency_ratio": (dependency_ratio, dependency_ratio <= max_dependency_ratio),
        "native_generation": (native_generation, native_generation >= min_native_generation),
        "plane_maturity": (plane_maturity, plane_maturity >= min_plane_maturity),
    }
    birth_ready = all(passed for _, passed in checks.values())
    return {
        "dependency_ratio": dependency_ratio,
        "native_generation": native_generation,
        "teacher_baseline_accuracy": teacher_baseline_accuracy,
        "outperforms_teacher": outperforms_teacher,
        "plane_maturity": plane_maturity,
        "milestone_checks": {k: {"value": v, "passed": p} for k, (v, p) in checks.items()},
        "birth_ready": birth_ready,
        "thresholds": {
            "max_dependency_ratio": max_dependency_ratio,
            "min_native_generation": min_native_generation,
            "min_plane_maturity": min_plane_maturity,
            "teacher_baseline_accuracy": teacher_baseline_accuracy,
            "outperform_margin": outperform_margin,
        },
    }


NODE_TYPES = ("core", "orchestrator", "assistant_orchestrator", "expert")


def evaluate_node_promotions(
    nodes: list[dict[str, Any]],
    *,
    min_native_generation: float = 0.6,
    min_plane_maturity: float = 0.6,
    outperform_margin: float = 0.0,
) -> dict[str, Any]:
    """Per-node Teacher Replacement Protocol gate (canon: teacher pairing is per EXPERT, per AO, and
    per ORCHESTRATOR, plus the core). Each node is judged against ITS OWN teacher baseline; a node is
    promoted only once it matches/beats its own teacher (and clears the competence/maturity floors).
    The system is birth-ready only when every node has surpassed its own teacher.

    Each node dict: {node_id, node_type, native_generation (held-out acc), teacher_baseline_accuracy,
                     [teacher_ids], [initial_loss], [final_loss]}.
    """
    results: dict[str, Any] = {}
    for node in nodes:
        node_type = node.get("node_type", "expert")
        if node_type not in NODE_TYPES:
            raise ValueError(f"unknown node_type {node_type!r}; allowed {NODE_TYPES}")
        ms = independence_milestones(
            {
                "val_accuracy": node["native_generation"],
                "initial_loss": node.get("initial_loss", 1.0),
                "final_loss": node.get("final_loss", node.get("initial_loss", 1.0)),
            },
            teacher_baseline_accuracy=float(node["teacher_baseline_accuracy"]),
            min_native_generation=min_native_generation,
            min_plane_maturity=min_plane_maturity,
            outperform_margin=outperform_margin,
        )
        ms["node_id"] = node["node_id"]
        ms["node_type"] = node_type
        ms["teacher_ids"] = list(node.get("teacher_ids", []))
        results[node["node_id"]] = ms

    promoted = sorted(nid for nid, m in results.items() if m["birth_ready"])
    blocked = sorted(nid for nid, m in results.items() if not m["birth_ready"])
    by_type = {t: {"total": 0, "promoted": 0} for t in NODE_TYPES}
    for m in results.values():
        by_type[m["node_type"]]["total"] += 1
        by_type[m["node_type"]]["promoted"] += 1 if m["birth_ready"] else 0
    system_birth_ready = bool(results) and all(m["birth_ready"] for m in results.values())
    return {
        "nodes": results,
        "promoted": promoted,
        "blocked": blocked,
        "by_type": by_type,
        "system_birth_ready": system_birth_ready,   # every expert/AO/orchestrator/core beat its teacher
    }


def save_checkpoint(model: NexusNetLM, metrics: dict[str, Any], milestones: dict[str, Any],
                    *, path: str, config: dict[str, Any]) -> dict[str, Any]:
    """Persist the birthed model weights + a birth manifest. The checkpoint IS the birthed artifact."""
    ckpt_path = Path(path)
    ckpt_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), ckpt_path)
    manifest = {
        "artifact": "birthed-nexusnet-model",
        "checkpoint_path": str(ckpt_path),
        "config": config,
        "training_metrics": {k: metrics[k] for k in
                             ("final_loss", "final_perplexity", "next_token_accuracy", "num_parameters")},
        "independence_milestones": milestones,
        "birth_ready": milestones["birth_ready"],
        "birthed_at": time.time(),
        "claim_boundary": "real-trained-weights-gated-by-model-birth-protocol",
    }
    manifest_path = ckpt_path.with_suffix(".birth.json")
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    manifest["manifest_path"] = str(manifest_path)
    return manifest


def birth_model(
    *,
    corpus: str,
    out_dir: str,
    seed: int = 0,
    epochs: int = 200,
    seq_len: int = 32,
    device: str = "cpu",
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Full pipeline: train -> evaluate independence milestones -> gate -> save the birthed checkpoint."""
    torch.manual_seed(seed)
    cfg = {"d_model": 96, "n_heads": 4, "n_kv_heads": 2, "num_experts": 4, "top_k": 2,
           "d_hidden": 192, "num_layers": 3}
    if config:
        cfg.update(config)
    x, y = make_corpus_windows(corpus, seq_len=seq_len, device=device)
    x_tr, y_tr, x_val, y_val = split_windows(x, y, val_fraction=0.2, seed=seed)
    model = NexusNetLM(**cfg).to(device)
    metrics = train_language_model(model, x_tr, y_tr, epochs=epochs, val_x=x_val, val_y=y_val)
    milestones = independence_milestones(metrics)   # native_generation uses held-out val accuracy
    manifest = save_checkpoint(model, metrics, milestones,
                               path=str(Path(out_dir) / "nexusnet_birth.pt"), config=cfg)
    return {"model": model, "metrics": metrics, "milestones": milestones, "manifest": manifest}


def load_checkpoint(path: str, *, config: dict[str, Any]) -> NexusNetLM:
    model = NexusNetLM(**config)
    model.load_state_dict(torch.load(path, map_location="cpu"))
    model.eval()
    return model

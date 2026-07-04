"""Wave-3: bind each capsule's eval_gates to a REAL held-out measurement (not a declared pass).

Canon Eval Center: a node is only promotable once it clears its eval gates on held-out tasks. The
curriculum lists each capsule's canonical benchmark gate NAMES (e.g. 'imagenet_topk', 'ocr_cer'); the
real benchmarks aren't runnable offline, so here each gate is evaluated against a measured held-out
PROXY (next-token accuracy / perplexity on the domain's held-out windows) and the result is honestly
labelled `measurement_basis="held_out_proxy"` with the canonical benchmark it stands in for. Swapping
in a real benchmark runner behind `measure_language_model` upgrades this to `measurement_basis="benchmark"`
without changing the gate logic.
"""
from __future__ import annotations

import math
from typing import Any

import torch
import torch.nn.functional as F

# gate-name suffixes that mean "lower is better" (error/loss/perplexity rates)
_LOWER_IS_BETTER = ("cer", "wer", "loss", "ppl", "perplexity", "error", "rate", "latency")


@torch.no_grad()
def measure_language_model(model: torch.nn.Module, x: torch.Tensor, y: torch.Tensor) -> dict[str, float]:
    """Real held-out measurement: cross-entropy, perplexity, next-token accuracy."""
    was_training = model.training
    model.eval()
    logits = model(x)
    loss = F.cross_entropy(logits.reshape(-1, logits.size(-1)), y.reshape(-1)).item()
    acc = (logits.argmax(dim=-1) == y).float().mean().item()
    if was_training:
        model.train()
    return {"val_loss": loss, "val_perplexity": math.exp(min(20.0, loss)), "val_accuracy": acc}


def _gate_is_lower_better(gate_name: str) -> bool:
    return any(gate_name.lower().endswith(sfx) or sfx in gate_name.lower() for sfx in _LOWER_IS_BETTER)


def evaluate_gate(
    gate_name: str,
    measurement: dict[str, float],
    *,
    accuracy_threshold: float = 0.6,
    perplexity_threshold: float = 8.0,
) -> dict[str, Any]:
    """Evaluate one named gate against the held-out measurement (proxy mapping, honestly labelled)."""
    if _gate_is_lower_better(gate_name):
        value = measurement["val_perplexity"]
        passed = value <= perplexity_threshold
        proxy_metric, threshold, comparator = "val_perplexity", perplexity_threshold, "<="
    else:
        value = measurement["val_accuracy"]
        passed = value >= accuracy_threshold
        proxy_metric, threshold, comparator = "val_accuracy", accuracy_threshold, ">="
    return {
        "gate": gate_name,
        "canonical_benchmark": gate_name,
        "proxy_metric": proxy_metric,
        "value": value,
        "threshold": threshold,
        "comparator": comparator,
        "passed": bool(passed),
        "measurement_basis": "held_out_proxy",
    }


def evaluate_capsule_gates(
    capsule_key: str,
    model: torch.nn.Module,
    x: torch.Tensor,
    y: torch.Tensor,
    *,
    accuracy_threshold: float = 0.6,
    perplexity_threshold: float = 8.0,
) -> dict[str, Any]:
    """Measure the student on held-out domain windows and evaluate ALL of a capsule's eval gates."""
    from ..curriculum import EXPERT_CAPSULES
    if capsule_key not in EXPERT_CAPSULES:
        raise KeyError(f"unknown capsule {capsule_key!r}")
    gates = EXPERT_CAPSULES[capsule_key].get("eval_gates", [])
    measurement = measure_language_model(model, x, y)
    results = [
        evaluate_gate(g, measurement, accuracy_threshold=accuracy_threshold,
                      perplexity_threshold=perplexity_threshold)
        for g in gates
    ]
    return {
        "capsule": capsule_key,
        "measurement": measurement,
        "gates": results,
        "gates_total": len(results),
        "gates_passed": sum(1 for r in results if r["passed"]),
        "all_gates_passed": bool(results) and all(r["passed"] for r in results),
    }

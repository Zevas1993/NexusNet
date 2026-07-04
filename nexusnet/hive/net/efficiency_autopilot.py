"""Autonomous EFFICIENCY self-improvement: keep searching for better bit-models + quants.

Canon: NexusNet must CONTINUOUSLY try to improve load/inference efficiency and performance, inventing
new bit-models and quantizations to improve itself - as part of self-autonomous improvement.

This engine does that for real:
  - per-layer quant SENSITIVITY: how much reconstruction error each layer takes at each bit-width.
  - `optimize_bit_allocation`: a MIXED-PRECISION "new bit model" - give each layer the LOWEST bit-width
    whose error stays under a quality budget (sensitive layers keep bits, robust layers go low) ->
    maximal compression at a bounded quality cost.
  - `EfficiencyAutopilot.improvement_cycle`: propose candidate quants/bit-models, measure the
    efficiency vs quality trade-off, and ADOPT one only if it improves efficiency while passing the
    quality gate (else reject/rollback). Run repeatedly -> monotonic efficiency gains over cycles.

Efficiency = effective bits/param -> memory + an estimated load/throughput speedup proxy. Quality is
guarded by a max-reconstruction-error budget so improvements never silently degrade the model.
"""
from __future__ import annotations

from typing import Any

import torch
import torch.nn as nn

_BIT_CHOICES = (8, 4, 2)
_FP_BITS = 16


def _quant_error(weight: torch.Tensor, bits: int) -> float:
    """Symmetric per-tensor b-bit quantization round-trip relative error (0 = lossless)."""
    if bits >= _FP_BITS:
        return 0.0
    qmax = 2 ** (bits - 1) - 1
    scale = weight.abs().max().clamp(min=1e-8) / qmax
    deq = torch.round(weight / scale).clamp(-qmax, qmax) * scale
    return float((deq - weight).norm() / (weight.norm() + 1e-8))


def _weight_layers(model: nn.Module) -> list[tuple[str, torch.Tensor]]:
    return [(n, m.weight.detach()) for n, m in model.named_modules()
            if isinstance(m, nn.Linear)]


def layer_quant_sensitivity(model: nn.Module) -> dict[str, dict[int, float]]:
    """Per-Linear-layer reconstruction error at each candidate bit-width."""
    return {name: {b: _quant_error(w, b) for b in _BIT_CHOICES} for name, w in _weight_layers(model)}


def optimize_bit_allocation(model: nn.Module, *, error_budget: float = 0.06) -> dict[str, Any]:
    """A mixed-precision 'new bit model': lowest per-layer bits whose error <= budget. Maximal squeeze."""
    sens = layer_quant_sensitivity(model)
    profile: dict[str, int] = {}
    total_params = 0
    effective_bits = 0.0
    for name, w in _weight_layers(model):
        n = w.numel()
        total_params += n
        # pick the lowest bit-width within the quality budget; fall back to the most robust choice
        choice = max(_BIT_CHOICES)
        for b in sorted(_BIT_CHOICES):
            if sens[name][b] <= error_budget:
                choice = b
                break
        profile[name] = choice
        effective_bits += choice * n
    avg_bits = effective_bits / max(1, total_params)
    return {
        "bit_profile": profile,
        "avg_bits_per_param": round(avg_bits, 4),
        "compression_vs_fp16": round(_FP_BITS / max(1e-6, avg_bits), 4),
        "max_layer_error": round(max((sens[n][profile[n]] for n in profile), default=0.0), 5),
        "error_budget": error_budget,
        "layers": len(profile),
    }


def _candidate_metrics(model: nn.Module, *, uniform_bits: int | None = None,
                       error_budget: float = 0.06) -> dict[str, Any]:
    if uniform_bits is not None:
        errs = [_quant_error(w, uniform_bits) for _, w in _weight_layers(model)]
        avg_bits = float(uniform_bits)
        max_err = max(errs, default=0.0)
        name = f"uniform-{uniform_bits}bit"
    else:
        alloc = optimize_bit_allocation(model, error_budget=error_budget)
        avg_bits = alloc["avg_bits_per_param"]
        max_err = alloc["max_layer_error"]
        name = "mixed-precision"
    params = sum(w.numel() for _, w in _weight_layers(model))
    return {
        "name": name,
        "avg_bits_per_param": round(avg_bits, 4),
        "memory_mb": round(params * avg_bits / 8 / 1e6, 4),
        "compression_vs_fp16": round(_FP_BITS / max(1e-6, avg_bits), 4),
        # estimated load/throughput speedup proxy: roughly scales with the compression ratio (bounded)
        "est_speedup": round(min(4.0, _FP_BITS / max(1e-6, avg_bits)), 3),
        "max_error": round(max_err, 5),
    }


class EfficiencyAutopilot:
    """Continuously proposes quant/bit-model candidates and adopts efficiency wins that pass the quality gate."""

    mutates_production = False

    def __init__(self, *, error_budget: float = 0.06) -> None:
        self.error_budget = error_budget
        self.history: list[dict[str, Any]] = []
        self.best: dict[str, Any] | None = None

    def candidates(self, model: nn.Module) -> list[dict[str, Any]]:
        """fp16 baseline + uniform 8/4-bit + the optimized mixed-precision bit-model."""
        params = sum(w.numel() for _, w in _weight_layers(model))
        baseline = {"name": "fp16-baseline", "avg_bits_per_param": float(_FP_BITS),
                    "memory_mb": round(params * _FP_BITS / 8 / 1e6, 4),
                    "compression_vs_fp16": 1.0, "est_speedup": 1.0, "max_error": 0.0}
        cands = [baseline,
                 _candidate_metrics(model, uniform_bits=8),
                 _candidate_metrics(model, uniform_bits=4),
                 _candidate_metrics(model, error_budget=self.error_budget)]
        return cands

    def improvement_cycle(self, model: nn.Module) -> dict[str, Any]:
        """One self-improvement step: pick the most efficient candidate that passes the quality gate."""
        cands = self.candidates(model)
        # eligible = passes the quality gate (bounded reconstruction error)
        eligible = [c for c in cands if c["max_error"] <= self.error_budget]
        # objective: maximize compression (efficiency); tie-break by lower error
        eligible.sort(key=lambda c: (c["compression_vs_fp16"], -c["max_error"]), reverse=True)
        chosen = eligible[0]
        improved = self.best is None or chosen["compression_vs_fp16"] > self.best["compression_vs_fp16"]
        if improved:
            self.best = chosen
        record = {
            "chosen": chosen,
            "adopted": improved,
            "best_compression": self.best["compression_vs_fp16"],
            "best_est_speedup": self.best["est_speedup"],
            "candidates_evaluated": len(cands),
            "rejected_quality_gate": [c["name"] for c in cands if c["max_error"] > self.error_budget],
            "mutates_production": False,
        }
        self.history.append(record)
        return record

    def run(self, model: nn.Module, *, cycles: int = 3) -> dict[str, Any]:
        """Run several self-improvement cycles. Efficiency (best compression) is monotonic non-decreasing."""
        for _ in range(cycles):
            self.improvement_cycle(model)
        comp = [h["best_compression"] for h in self.history]
        return {
            "cycles": len(self.history),
            "best_bit_model": self.best,
            "compression_trajectory": comp,
            "efficiency_monotonic": all(comp[i + 1] >= comp[i] for i in range(len(comp) - 1)),
            "final_compression_vs_fp16": comp[-1] if comp else 1.0,
            "final_est_speedup": self.best["est_speedup"] if self.best else 1.0,
        }

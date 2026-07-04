"""Canon Aspect 2: real expert ASSIMILATION + FUSION into the trainable MoE (Mixtral+Devstral theme).

`moe/fusion` and `moe/mixtral_devstral` are dict-returning scaffolds. Canon's core claim is fusing
models "at the neural-network level, not just orchestration" (C01M0044) and assimilating new experts
into the MoE (C01M0101). This is the real torch mechanism - parameter surgery on a live
`MoECapsuleLayer`:

  - assimilate_expert: graft a donor expert module into an MoE layer, growing the router by one row
    (new expert starts with a neutral gate logit so it doesn't disrupt the trained routing), and
    growing the load-balancing buffers - capacity added without retraining the existing experts.
  - fuse_moe_layers: build one MoE whose experts are the UNION of two layers' experts with a combined
    router - the network-level Mixtral+Devstral fusion (two models' experts under one routing fabric).
"""
from __future__ import annotations

from typing import Any

import torch
import torch.nn as nn

from .model import MoECapsuleLayer, SwiGLUExpert


def _grow_linear(gate: nn.Linear, extra: int, *, init: float = 0.0) -> nn.Linear:
    """Return a copy of `gate` with `extra` new output rows initialized to `init` (neutral logits)."""
    new = nn.Linear(gate.in_features, gate.out_features + extra, bias=gate.bias is not None)
    with torch.no_grad():
        new.weight[: gate.out_features] = gate.weight
        new.weight[gate.out_features:] = init
        if gate.bias is not None:
            new.bias[: gate.out_features] = gate.bias
            new.bias[gate.out_features:] = init
    return new


def assimilate_expert(layer: MoECapsuleLayer, donor: nn.Module, *, gate_init: float = 0.0,
                      trainable_donor: bool = True) -> dict[str, Any]:
    """Graft `donor` (a module mapping d_model -> d_model) into `layer` as a new expert. In place."""
    old_e = layer.num_experts
    pre_param_ids = {id(p) for e in layer.experts for p in e.parameters()}
    layer.experts.append(donor)
    layer.gate = _grow_linear(layer.gate, 1, init=gate_init)     # router grows by one neutral row
    layer.load_bias = torch.cat([layer.load_bias, torch.zeros(1, device=layer.load_bias.device)])
    layer.last_load = torch.cat([layer.last_load, torch.zeros(1, device=layer.last_load.device)])
    layer.num_experts = old_e + 1
    for p in donor.parameters():
        p.requires_grad_(trainable_donor)
    return {
        "num_experts": layer.num_experts,
        "grew_from": old_e,
        "donor_params": sum(p.numel() for p in donor.parameters()),
        "existing_experts_preserved": all(id(p) in pre_param_ids
                                          for e in layer.experts[:old_e] for p in e.parameters()),
    }


def make_swiglu_expert(d_model: int, d_hidden: int) -> SwiGLUExpert:
    """Convenience: a fresh donor expert capsule of the canon SwiGLU type."""
    return SwiGLUExpert(d_model, d_hidden)


def fuse_moe_layers(layer_a: MoECapsuleLayer, layer_b: MoECapsuleLayer, *,
                    top_k: int | None = None) -> MoECapsuleLayer:
    """Fuse two MoE layers into one whose experts are the union of both, under a combined router.

    Network-level fusion: the two donors' trained experts are transplanted (same module objects) and
    the router is the row-concatenation of both gates - the canon Mixtral+Devstral 'fuse at the neural
    level' realized on the trainable substrate.
    """
    if layer_a.gate.in_features != layer_b.gate.in_features:
        raise ValueError("MoE layers must share d_model to fuse")
    d_model = layer_a.gate.in_features
    total = layer_a.num_experts + layer_b.num_experts
    fused = MoECapsuleLayer(d_model, d_hidden=8, num_experts=1, top_k=1)   # minimal; overwritten below
    fused.experts = nn.ModuleList(list(layer_a.experts) + list(layer_b.experts))
    new_gate = nn.Linear(d_model, total, bias=layer_a.gate.bias is not None)
    with torch.no_grad():
        new_gate.weight[: layer_a.num_experts] = layer_a.gate.weight
        new_gate.weight[layer_a.num_experts:] = layer_b.gate.weight
        if layer_a.gate.bias is not None and layer_b.gate.bias is not None:
            new_gate.bias[: layer_a.num_experts] = layer_a.gate.bias
            new_gate.bias[layer_a.num_experts:] = layer_b.gate.bias
    fused.gate = new_gate
    fused.load_bias = torch.cat([layer_a.load_bias, layer_b.load_bias])
    fused.last_load = torch.zeros(total)
    fused.num_experts = total
    fused.top_k = min(top_k or max(layer_a.top_k, layer_b.top_k), total)
    return fused

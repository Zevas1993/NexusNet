"""Canon Aspect 1 (brain-first): the REAL attach_base_model mechanism - inspect + adapter injection.

`core/attach_base_model.py` only records attachment METADATA. Canon C05M0102 specifies the actual seam:
NexusNet "inspects the base model's layers (weights, shapes, module types) and injects adapters
(LoRA-style / projection shims) into each block, creating lightweight TRAINABLE sub-modules without
touching the base weights." This is that mechanism in real torch - NexusNet upgrading another network:

  - inspect_base_model: walk an nn.Module, report every Linear (name, in/out, params) + block count.
  - LoRAAdapter: a frozen base Linear + a trainable low-rank delta (B@A * scale); base weights frozen.
  - attach_base_model_adapters: replace target Linears in-place with LoRA wrappers, freeze the base,
    and return the trainable adapter parameter set - the brain-first upgrade with the base intact.
"""
from __future__ import annotations

from typing import Any

import torch
import torch.nn as nn


def inspect_base_model(model: nn.Module) -> dict[str, Any]:
    """Introspect a base model: enumerate Linear layers (shapes) + total/trainable params (canon inspect)."""
    linears: list[dict[str, Any]] = []
    for name, mod in model.named_modules():
        if isinstance(mod, nn.Linear):
            linears.append({"name": name, "in_features": mod.in_features,
                            "out_features": mod.out_features,
                            "params": mod.weight.numel() + (mod.bias.numel() if mod.bias is not None else 0)})
    total = sum(p.numel() for p in model.parameters())
    return {
        "linear_layers": linears,
        "linear_count": len(linears),
        "total_params": total,
        "hidden_sizes": sorted({l["out_features"] for l in linears}),
        "module_types": sorted({type(m).__name__ for _, m in model.named_modules()}),
    }


class LoRAAdapter(nn.Module):
    """Wrap a base Linear with a trainable low-rank delta: y = base(x) + scale * (x @ Aᵀ) @ Bᵀ.

    The base layer is FROZEN (requires_grad=False); only the low-rank A,B train. This is the canon
    'inject trainable shims without touching base weights' - NexusNet upgrading the base network.
    """

    def __init__(self, base: nn.Linear, *, rank: int = 4, alpha: float = 8.0) -> None:
        super().__init__()
        self.base = base
        for p in self.base.parameters():
            p.requires_grad_(False)                         # freeze the base network
        self.rank = rank
        self.scale = alpha / rank
        self.lora_a = nn.Parameter(torch.randn(rank, base.in_features) * 0.01)
        self.lora_b = nn.Parameter(torch.zeros(base.out_features, rank))   # zero-init: starts == base

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        delta = (x @ self.lora_a.t()) @ self.lora_b.t()
        return self.base(x) + self.scale * delta

    def merged_weight(self) -> torch.Tensor:
        """The effective weight (base + low-rank delta) - for export/merge of the upgraded network."""
        return self.base.weight + self.scale * (self.lora_b @ self.lora_a)


def _set_submodule(root: nn.Module, dotted: str, new: nn.Module) -> None:
    parts = dotted.split(".")
    parent = root
    for p in parts[:-1]:
        parent = parent[int(p)] if p.isdigit() else getattr(parent, p)
    last = parts[-1]
    if last.isdigit():
        parent[int(last)] = new
    else:
        setattr(parent, last, new)


def attach_base_model_adapters(
    model: nn.Module,
    *,
    rank: int = 4,
    alpha: float = 8.0,
    target_names: tuple[str, ...] | None = None,
    min_features: int = 0,
) -> dict[str, Any]:
    """Inject LoRA adapters into the base model's Linear layers in place; freeze the base, return stats.

    `target_names`: only inject into Linears whose qualified name contains one of these substrings
    (e.g. ('q_proj','v_proj')). Default = all Linears at/above `min_features`. Brain-first: the base
    network is preserved and frozen; the injected adapters are the only trainable parameters.
    """
    injected: list[str] = []
    targets = [(n, m) for n, m in model.named_modules()
               if isinstance(m, nn.Linear)
               and (target_names is None or any(t in n for t in target_names))
               and m.in_features >= min_features]
    for name, lin in targets:
        _set_submodule(model, name, LoRAAdapter(lin, rank=rank, alpha=alpha))
        injected.append(name)
    # freeze everything that is not a LoRA adapter parameter
    adapter_params = []
    for n, p in model.named_parameters():
        if "lora_a" in n or "lora_b" in n:
            p.requires_grad_(True)
            adapter_params.append(p)
        else:
            p.requires_grad_(False)
    trainable = sum(p.numel() for p in adapter_params)
    total = sum(p.numel() for p in model.parameters())
    return {
        "injected_layers": injected,
        "injected_count": len(injected),
        "trainable_params": trainable,
        "total_params": total,
        "trainable_fraction": (trainable / total) if total else 0.0,
        "base_frozen": all(not p.requires_grad for n, p in model.named_parameters()
                           if "lora_" not in n),
        "claim_boundary": "brain-first-adapter-injection-base-network-preserved-and-frozen",
    }

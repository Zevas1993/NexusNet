"""Governed Sparse Routing - the NexusNet patent claim, made real.

The sacred-geometry hive-mind FABRIC governs the learned MoE ROUTER. Two routers become one:

  - The hive fabric (Flower-of-Life topology, quorum, critical-mass, synapse-relay) decides which
    expert nodes are ELIGIBLE this step (the governed active set) and each one's PRIORITY
    (sacred-topology centrality + capsule pose strength).
  - The learned MoE router (DeepSeek loss-free top-k) then selects top-k experts WITHIN the governed
    set, with priority added to the *selection* logits only (never the gate weight, so balancing and
    governance carry no interference gradients).

Governance is deterministic and trains no weights - it gates and biases selection. This binds the
symbolic hive (governance) to the differentiable network (sparse routing): "Governed Sparse Routing".
"""
from __future__ import annotations

from typing import Iterable, Sequence

import torch

from .model import MoECapsuleLayer


class GovernedSparseRouter:
    """Maps hive-fabric governance to per-expert selection bias and binds it onto a model's MoE layers."""

    def __init__(self, num_experts: int, *, hard: bool = True, priority_scale: float = 1.0,
                 soft_penalty: float = 12.0) -> None:
        self.num_experts = num_experts
        self.hard = hard                    # hard governance forbids non-eligible experts (-inf)
        self.priority_scale = priority_scale
        self.soft_penalty = soft_penalty    # advisory penalty when hard gating would starve top_k

    def governance_bias(
        self,
        allowed: Iterable[int],
        *,
        priorities: Sequence[float] | None = None,
        top_k: int = 1,
        device=None,
    ) -> torch.Tensor:
        """Build a (num_experts,) bias: forbidden experts -> -inf (or -penalty), allowed -> +priority.

        If fewer than `top_k` experts are eligible, hard gating would make top-k impossible, so it
        degrades to an advisory penalty (the router can still fill the budget). This keeps governance
        from ever producing a NaN route while still strongly steering selection.
        """
        bias = torch.zeros(self.num_experts, device=device)
        allowed_set = {int(e) for e in allowed if 0 <= int(e) < self.num_experts}
        enforce_hard = self.hard and len(allowed_set) >= top_k and len(allowed_set) < self.num_experts
        for e in range(self.num_experts):
            if e not in allowed_set:
                bias[e] = float("-inf") if enforce_hard else -self.soft_penalty
        if priorities is not None:
            pri = torch.tensor([float(p) for p in priorities], dtype=torch.float32, device=device)
            if pri.numel() == self.num_experts and torch.isfinite(pri).any():
                lo, hi = pri.min(), pri.max()
                norm = (pri - lo) / (hi - lo + 1e-8)
                for e in allowed_set:
                    bias[e] = bias[e] + self.priority_scale * float(norm[e])
        return bias

    def _moe_layers(self, model: torch.nn.Module) -> list[MoECapsuleLayer]:
        return [m for m in model.modules() if isinstance(m, MoECapsuleLayer)]

    def govern(
        self,
        model: torch.nn.Module,
        allowed: Iterable[int],
        *,
        priorities: Sequence[float] | None = None,
    ) -> torch.Tensor:
        """Bind a governance bias derived from `allowed`/`priorities` onto every MoE layer in `model`."""
        layers = self._moe_layers(model)
        if not layers:
            raise ValueError("model has no MoECapsuleLayer to govern")
        top_k = min(layer.top_k for layer in layers)
        bias = self.governance_bias(allowed, priorities=priorities, top_k=top_k)
        for layer in layers:
            layer.set_governance(bias)
        return bias

    def release(self, model: torch.nn.Module) -> None:
        """Remove governance (return to free learned routing)."""
        for layer in self._moe_layers(model):
            layer.clear_governance()


def fabric_expert_governance(
    fabric_process: dict,
    expert_node_ids: Sequence[str],
) -> tuple[list[int], list[float]]:
    """Translate a HiveMindFabric.process() output into (allowed_expert_indices, priorities).

    `expert_node_ids` is the ordered list of fabric node ids that back the MoE experts (index i of the
    list == expert i). An expert is ELIGIBLE iff its node is in the fabric's active set; its priority
    is the node's sacred-topology weight if exposed, else uniform. Deterministic, read-only.
    """
    active = set(fabric_process.get("active_node_set") or [])
    positions = fabric_process.get("node_positions") or {}
    allowed: list[int] = []
    priorities: list[float] = []
    for i, node_id in enumerate(expert_node_ids):
        if node_id in active:
            allowed.append(i)
        # priority = radial centrality from the Flower-of-Life layout (closer to bindu = higher)
        pos = positions.get(node_id)
        if isinstance(pos, (list, tuple)) and len(pos) >= 2:
            r = (float(pos[0]) ** 2 + float(pos[1]) ** 2) ** 0.5
            priorities.append(1.0 / (1.0 + r))
        else:
            priorities.append(0.0)
    return allowed, priorities

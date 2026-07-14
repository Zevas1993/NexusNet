"""The actual trainable NexusNet neural network (PyTorch).

This is a REAL neural network: every weight is a learnable `nn.Parameter`, trained by backprop
(`loss.backward()` + optimizer step). It implements the canon architecture as trainable modules -
MoE capsule experts (each a SwiGLU "mini-brain"), a learned top-k router with DeepSeek auxiliary-
loss-free load balancing, capsule squash for pose/confidence, pre-norm residual stacking - the
substrate that can be trained and grown into the birthed MoE model.

Device-agnostic: `.to("cuda")` on a GPU box (e.g. the RTX 5070 Ti), trains on CPU otherwise.
"""
from __future__ import annotations

from typing import Protocol

import torch
import torch.nn as nn
import torch.nn.functional as F


class ExpertExecutionBackend(Protocol):
    def execute(self, expert_id: int, inputs: torch.Tensor) -> torch.Tensor: ...


def squash(x: torch.Tensor, dim: int = -1, eps: float = 1e-8) -> torch.Tensor:
    """Capsule squash: length -> [0,1) presence probability, direction preserved (Sabour/Hinton)."""
    sq = (x * x).sum(dim=dim, keepdim=True)
    scale = sq / (1.0 + sq)
    return scale * x / torch.sqrt(sq + eps)


class SwiGLUExpert(nn.Module):
    """One expert capsule's feed-forward 'mini-brain' (SwiGLU), all learnable."""

    def __init__(self, d_model: int, d_hidden: int) -> None:
        super().__init__()
        self.w_gate = nn.Linear(d_model, d_hidden)
        self.w_value = nn.Linear(d_model, d_hidden)
        self.w_out = nn.Linear(d_hidden, d_model)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.w_out(F.silu(self.w_gate(x)) * self.w_value(x))


class _MiniRMSNorm(nn.Module):
    def __init__(self, dim: int, eps: float = 1e-6) -> None:
        super().__init__()
        self.weight = nn.Parameter(torch.ones(dim))
        self.eps = eps

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        rms = torch.rsqrt(x.pow(2).mean(dim=-1, keepdim=True) + self.eps)
        return x * rms * self.weight


class MiniNexusNetExpert(nn.Module):
    """Each expert capsule is itself a small NexusNet 'mini-brain' - a real internal neural network
    (input -> internal pre-norm residual depth -> output), not a single labeled FFN.

    Canon C06M0091/C06M0123: every expert must render a *complete internal network* (Input -> Hidden
    -> Output with inter-node connections), drawn to the same fidelity as the main layers. Here each
    expert has its own input norm, `depth` internal SwiGLU residual blocks, and an output projection,
    plus a learned capsule pose readout (presence/confidence) exposed for routing-by-agreement.
    """

    def __init__(self, d_model: int, d_hidden: int, depth: int = 2) -> None:
        super().__init__()
        self.in_norm = _MiniRMSNorm(d_model)
        self.norms = nn.ModuleList([_MiniRMSNorm(d_model) for _ in range(depth)])
        self.ffns = nn.ModuleList([SwiGLUExpert(d_model, d_hidden) for _ in range(depth)])
        self.out = nn.Linear(d_model, d_model)
        self.pose_head = nn.Linear(d_model, d_model)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.in_norm(x)
        for norm, ffn in zip(self.norms, self.ffns):
            h = h + ffn(norm(h))                                 # internal residual depth
        return self.out(h)

    def pose(self, x: torch.Tensor) -> torch.Tensor:
        return squash(self.pose_head(self.forward(x)))          # capsule presence vector


class MoECapsuleLayer(nn.Module):
    """Sparse Mixture-of-Experts over capsule experts with a LEARNED top-k router.

    Selection uses biased logits (DeepSeek auxiliary-loss-free balancing): a per-expert load bias is
    added only to the routing decision, never to the gate weight, so balancing carries no interference
    gradients. The gate weight is the original-score softmax over the chosen experts.
    """

    def __init__(self, d_model: int, d_hidden: int, num_experts: int, top_k: int,
                 *, expert_kind: str = "swiglu", expert_depth: int = 2) -> None:
        super().__init__()
        if top_k > num_experts:
            raise ValueError("top_k cannot exceed num_experts")
        self.num_experts = num_experts
        self.top_k = top_k
        self.expert_kind = expert_kind
        if expert_kind == "mini":
            self.experts = nn.ModuleList(
                [MiniNexusNetExpert(d_model, d_hidden, depth=expert_depth) for _ in range(num_experts)]
            )
        else:
            self.experts = nn.ModuleList([SwiGLUExpert(d_model, d_hidden) for _ in range(num_experts)])
        self.gate = nn.Linear(d_model, num_experts)
        self.register_buffer("load_bias", torch.zeros(num_experts))
        self.register_buffer("last_load", torch.zeros(num_experts))
        # Governed Sparse Routing: hive governance bias over experts (0=allow, -inf=forbid, +=prio).
        # Set by GovernedSparseRouter from the sacred-geometry fabric; None = ungoverned (free routing).
        self.governance: torch.Tensor | None = None
        self._expert_execution_backend: ExpertExecutionBackend | None = None
        self._tiered_parameter_identity_changed = False

    def set_execution_backend(self, backend: ExpertExecutionBackend | None) -> None:
        """Select an inference-only expert executor; None restores resident execution."""
        if self.training and backend is not None:
            raise RuntimeError("tiered expert execution is inference-only")
        if (
            backend is None
            and self._expert_execution_backend is not None
            and getattr(self._expert_execution_backend, "resident_experts_released", False)
        ):
            raise RuntimeError("restore resident experts before detaching tiered execution")
        self._expert_execution_backend = backend

    def acknowledge_optimizer_rebind(self) -> None:
        """Confirm optimizers were rebuilt after materializing released experts."""
        if self._expert_execution_backend is not None:
            raise RuntimeError("cannot acknowledge optimizer rebind while tiered execution is attached")
        self._tiered_parameter_identity_changed = False

    def set_governance(self, governance: torch.Tensor | None) -> None:
        """Bind a per-expert governance bias (len == num_experts) from the hive fabric, or None."""
        if governance is not None and governance.numel() != self.num_experts:
            raise ValueError("governance must have one entry per expert")
        self.governance = governance

    def clear_governance(self) -> None:
        self.governance = None

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.training and self._expert_execution_backend is not None:
            raise RuntimeError("tiered expert execution is inference-only")
        if self.training and self._tiered_parameter_identity_changed:
            raise RuntimeError("optimizer rebind is required after restoring tiered experts")
        scores = self.gate(x)                                   # (N, E) learned routing scores
        biased = scores + self.load_bias                        # selection only
        if self.governance is not None:
            biased = biased + self.governance.to(biased.device)  # governed sparse routing
        topv, topi = torch.topk(biased, self.top_k, dim=-1)     # (N, k)
        if self._expert_execution_backend is not None:
            begin_route = getattr(self._expert_execution_backend, "begin_route", None)
            if begin_route is not None:
                selected = tuple(sorted(int(item) for item in torch.unique(topi).detach().cpu().tolist()))
                begin_route(selected, x.device)
        chosen_scores = torch.gather(scores, -1, topi)          # original scores for the gate weight
        gate_w = torch.softmax(chosen_scores, dim=-1)           # (N, k), sums to 1 per row

        out = torch.zeros_like(x)
        load = torch.zeros(self.num_experts, device=x.device)
        for e in range(self.num_experts):
            sel = (topi == e)                                   # (N, k) where expert e was chosen
            if not sel.any():
                continue
            token_mask = sel.any(dim=-1)                        # (N,) tokens routing to e
            # weight for expert e per token = sum of its gate weights across the matching slots
            w_e = (gate_w * sel).sum(dim=-1, keepdim=True)[token_mask]  # (M,1)
            expert_inputs = x[token_mask]
            expert_output = (
                self._expert_execution_backend.execute(e, expert_inputs)
                if self._expert_execution_backend is not None
                else self.experts[e](expert_inputs)
            )
            out[token_mask] = out[token_mask] + w_e * expert_output
            load[e] = token_mask.sum()
        self.last_load = load.detach()
        return out

    @torch.no_grad()
    def update_load_bias(self, update_rate: float = 0.001) -> None:
        """DeepSeek bias step: nudge under-loaded experts up, over-loaded down (deterministic)."""
        mean_load = self.last_load.mean()
        self.load_bias += update_rate * torch.sign(mean_load - self.last_load)


class NexusNetModel(nn.Module):
    """The trainable NexusNet core: embed -> stacked MoE capsule layers (pre-norm residual) -> head.

    `forward` returns class logits; `pose` returns the squashed capsule pose (presence/confidence).
    """

    def __init__(
        self,
        *,
        in_dim: int,
        d_model: int = 32,
        d_hidden: int = 64,
        num_experts: int = 6,
        top_k: int = 2,
        num_classes: int = 3,
        num_layers: int = 2,
    ) -> None:
        super().__init__()
        self.embed = nn.Linear(in_dim, d_model)
        self.layers = nn.ModuleList(
            [MoECapsuleLayer(d_model, d_hidden, num_experts, top_k) for _ in range(num_layers)]
        )
        self.norms = nn.ModuleList([nn.LayerNorm(d_model) for _ in range(num_layers)])
        self.out_norm = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, num_classes)

    def trunk(self, x: torch.Tensor) -> torch.Tensor:
        h = self.embed(x)
        for layer, norm in zip(self.layers, self.norms):
            h = h + layer(norm(h))                              # pre-norm residual
        return self.out_norm(h)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.head(self.trunk(x))

    def pose(self, x: torch.Tensor) -> torch.Tensor:
        return squash(self.trunk(x))

    def update_load_bias(self, update_rate: float = 0.001) -> None:
        for layer in self.layers:
            layer.update_load_bias(update_rate)

    def num_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)

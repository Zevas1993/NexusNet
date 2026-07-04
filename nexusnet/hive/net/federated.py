"""Wave-9: real federated weight aggregation (FedAvg) over trainable NexusNet weights.

Canon (Aspect 14; C04 mandatory-core): NexusNet learns across installs via federated adapter updates.
`nexusnet/federation/` is the transport + governance + review-gate layer (Flower packets); this module
is the missing piece that actually AVERAGES real torch weights:

  - fedavg                 sample-weighted average of client state_dicts (the FedAvg update).
  - divergence_guard       drop Byzantine/outlier clients whose update is far from the cohort median.
  - secure_aggregate       pairwise-canceling masks: individual updates are hidden, the mean is exact.
  - federated_train_round  clients train locally on their shard, then the server FedAvg-aggregates.

Deterministic under a fixed seed; integrates behind the existing federation review gate.
"""
from __future__ import annotations

from typing import Any, Callable

import torch
import torch.nn.functional as F


def _flatten(state: dict[str, torch.Tensor]) -> torch.Tensor:
    return torch.cat([v.float().reshape(-1) for v in state.values()])


def fedavg(state_dicts: list[dict[str, torch.Tensor]],
           weights: list[float] | None = None) -> dict[str, torch.Tensor]:
    """Sample-weighted FedAvg of client state_dicts -> one global state_dict."""
    if not state_dicts:
        raise ValueError("no client states to aggregate")
    n = len(state_dicts)
    w = weights if weights is not None else [1.0] * n
    s = sum(w)
    w = [wi / s for wi in w]
    keys = state_dicts[0].keys()
    avg: dict[str, torch.Tensor] = {}
    for k in keys:
        acc = sum(wi * sd[k].float() for wi, sd in zip(w, state_dicts))
        avg[k] = acc.to(state_dicts[0][k].dtype)
    return avg


def divergence_guard(state_dicts: list[dict[str, torch.Tensor]], *, tolerance: float = 2.5
                     ) -> dict[str, Any]:
    """Flag outlier clients: distance from the cohort mean > tolerance * median distance (robust agg)."""
    flats = [_flatten(sd) for sd in state_dicts]
    mean = torch.stack(flats).mean(dim=0)
    dists = torch.stack([(f - mean).norm() for f in flats])
    median = dists.median()
    threshold = tolerance * (median + 1e-8)
    kept = [i for i in range(len(state_dicts)) if dists[i] <= threshold]
    flagged = [i for i in range(len(state_dicts)) if dists[i] > threshold]
    return {"kept": kept, "flagged": flagged, "distances": dists.tolist(),
            "threshold": float(threshold)}


def secure_aggregate(updates: list[torch.Tensor], *, seed: int = 0) -> dict[str, Any]:
    """Secure-aggregation sketch: add pairwise-canceling masks so individual updates are hidden but
    the aggregate (sum/mean) is exactly preserved."""
    g = torch.Generator().manual_seed(seed)
    masks = [torch.randn(u.shape, generator=g) for u in updates]
    mean_mask = torch.stack(masks).mean(dim=0)
    masked = [u + (m - mean_mask) for u, m in zip(updates, masks)]   # masks sum to zero
    true_mean = torch.stack(updates).mean(dim=0)
    masked_mean = torch.stack(masked).mean(dim=0)
    return {"masked": masked, "true_mean": true_mean, "masked_mean": masked_mean}


def _local_fit(model: torch.nn.Module, x: torch.Tensor, y: torch.Tensor, *, steps: int, lr: float
               ) -> None:
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    model.train()
    for _ in range(steps):
        opt.zero_grad()
        logits = model(x)
        loss = F.cross_entropy(logits.reshape(-1, logits.size(-1)), y.reshape(-1))
        loss.backward()
        opt.step()


@torch.no_grad()
def _eval_ce(model: torch.nn.Module, x: torch.Tensor, y: torch.Tensor) -> float:
    model.eval()
    logits = model(x)
    return float(F.cross_entropy(logits.reshape(-1, logits.size(-1)), y.reshape(-1)))


def federated_train_round(
    make_model: Callable[[], torch.nn.Module],
    global_state: dict[str, torch.Tensor],
    client_shards: list[tuple[torch.Tensor, torch.Tensor]],
    *,
    local_steps: int = 20,
    lr: float = 3e-3,
    use_guard: bool = True,
) -> dict[str, Any]:
    """One federated round: each client trains locally from the global weights, server FedAvg-aggregates.

    Returns the new global state + the pooled-data loss before/after (should improve as clients learn).
    """
    client_states: list[dict[str, torch.Tensor]] = []
    counts: list[float] = []
    for x, y in client_shards:
        m = make_model()
        m.load_state_dict(global_state)
        _local_fit(m, x, y, steps=local_steps, lr=lr)
        client_states.append({k: v.detach().clone() for k, v in m.state_dict().items()})
        counts.append(float(x.shape[0]))

    guard = divergence_guard(client_states) if use_guard and len(client_states) > 2 else {
        "kept": list(range(len(client_states))), "flagged": []}
    kept = guard["kept"]
    new_global = fedavg([client_states[i] for i in kept], [counts[i] for i in kept])

    # pooled-data evaluation of the global model before vs after the round
    pooled_x = torch.cat([s[0] for s in client_shards], dim=0)
    pooled_y = torch.cat([s[1] for s in client_shards], dim=0)
    before_m = make_model(); before_m.load_state_dict(global_state)
    after_m = make_model(); after_m.load_state_dict(new_global)
    before = _eval_ce(before_m, pooled_x, pooled_y)
    after = _eval_ce(after_m, pooled_x, pooled_y)
    return {
        "global_state": new_global,
        "clients": len(client_states),
        "kept": kept,
        "flagged": guard["flagged"],
        "loss_before": before,
        "loss_after": after,
        "improved": after < before,
    }

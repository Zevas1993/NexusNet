"""Wave-3: Reinforcement-learning training lane for NexusNet (real torch policy gradients).

Canon Aspect 9 / C03 / C38: RL & agentic-RL (Verl, TRL, NeMo-RL, SkyRL, RAGEN) and R-Zero self-play
must drive real weight updates, not just supervised + distillation. This module implements:

  - grpo_step / train_grpo   Group-Relative Policy Optimization (DeepSeek-R1 style): for each input
                             sample G actions from the policy, score them, and use the group-relative
                             advantage A = (r - mean) / std as the REINFORCE weight, with an optional
                             KL leash to a reference policy (PPO-style trust region). Real backprop.
  - r_zero_self_play         R-Zero co-evolution: a CHALLENGER proposes the hardest items (where the
                             policy is most uncertain) and the SOLVER improves on them via GRPO. The
                             two roles co-adapt with no external labels beyond the task reward.

The policy here treats the classifier head as a categorical policy over classes; the reward is task
correctness (extendable to any scalar reward). Deterministic under a fixed seed.
"""
from __future__ import annotations

from typing import Any, Callable

import torch
import torch.nn as nn
import torch.nn.functional as F


def correctness_reward(actions: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    """+1 for a correct action, -1 otherwise (zero-mean-ish, dense)."""
    return torch.where(actions == y, 1.0, -1.0)


def grpo_step(
    model: nn.Module,
    X: torch.Tensor,
    y: torch.Tensor,
    optimizer: torch.optim.Optimizer,
    *,
    group_size: int = 8,
    reward_fn: Callable[[torch.Tensor, torch.Tensor], torch.Tensor] = correctness_reward,
    kl_coef: float = 0.01,
    ref_logits: torch.Tensor | None = None,
    generator: torch.Generator | None = None,
) -> dict[str, float]:
    """One GRPO update. Returns reward/loss stats. Group-relative advantage removes the value net."""
    model.train()
    optimizer.zero_grad()
    logits = model(X)                                          # (N, C)
    logp = F.log_softmax(logits, dim=-1)
    prob = logp.exp()

    # Sample G actions per input; build group-relative advantages.
    adv_terms = []
    chosen_logps = []
    rewards_all = []
    for _ in range(group_size):
        actions = torch.multinomial(prob, num_samples=1, generator=generator).squeeze(-1)  # (N,)
        r = reward_fn(actions, y).to(logits.dtype)            # (N,)
        rewards_all.append(r)
        chosen_logps.append(logp.gather(-1, actions.unsqueeze(-1)).squeeze(-1))
    rewards = torch.stack(rewards_all, dim=0)                 # (G, N)
    logps = torch.stack(chosen_logps, dim=0)                  # (G, N)
    baseline = rewards.mean(dim=0, keepdim=True)              # group mean per input
    std = rewards.std(dim=0, keepdim=True) + 1e-6
    advantage = (rewards - baseline) / std                    # group-relative advantage
    pg_loss = -(advantage.detach() * logps).mean()           # REINFORCE with GRPO advantage

    kl = torch.tensor(0.0, device=logits.device)
    if ref_logits is not None and kl_coef > 0.0:
        ref_logp = F.log_softmax(ref_logits.detach(), dim=-1)
        kl = F.kl_div(logp, ref_logp.exp(), reduction="batchmean")   # leash to reference policy
    loss = pg_loss + kl_coef * kl
    loss.backward()
    optimizer.step()
    return {
        "loss": float(loss),
        "pg_loss": float(pg_loss),
        "kl": float(kl),
        "mean_reward": float(rewards.mean()),
    }


def train_grpo(
    model: nn.Module,
    X: torch.Tensor,
    y: torch.Tensor,
    *,
    steps: int = 60,
    lr: float = 3e-3,
    group_size: int = 8,
    kl_coef: float = 0.01,
    seed: int = 0,
) -> dict[str, Any]:
    """Train a policy by GRPO; reward = task correctness. Mean reward should rise as the policy learns."""
    gen = torch.Generator(device="cpu").manual_seed(seed)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    with torch.no_grad():
        ref_logits = model(X).detach()                        # frozen reference policy (start)
    reward_hist: list[float] = []
    last = {}
    for _ in range(steps):
        last = grpo_step(model, X, y, optimizer, group_size=group_size, kl_coef=kl_coef,
                         ref_logits=ref_logits, generator=gen)
        reward_hist.append(last["mean_reward"])
    with torch.no_grad():
        model.eval()
        greedy_acc = (model(X).argmax(dim=-1) == y).float().mean().item()
    return {
        "reward_history": reward_hist,
        "initial_reward": reward_hist[0],
        "final_reward": reward_hist[-1],
        "reward_improved": reward_hist[-1] > reward_hist[0],
        "greedy_accuracy": greedy_acc,
        "last_step": last,
    }


def r_zero_self_play(
    model: nn.Module,
    X: torch.Tensor,
    y: torch.Tensor,
    *,
    rounds: int = 5,
    steps_per_round: int = 12,
    challenge_fraction: float = 0.5,
    lr: float = 3e-3,
    group_size: int = 8,
    seed: int = 0,
) -> dict[str, Any]:
    """R-Zero co-evolution: each round the CHALLENGER selects the items the policy is most uncertain
    about (highest predictive entropy), and the SOLVER trains on that harder subset via GRPO. No
    external supervision beyond the task reward; difficulty rises as competence rises (self-play)."""
    gen = torch.Generator(device="cpu").manual_seed(seed)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    k = max(1, int(challenge_fraction * X.shape[0]))
    round_rewards: list[float] = []
    challenge_entropy: list[float] = []
    for _ in range(rounds):
        # CHALLENGER: pick the hardest k items by current predictive entropy.
        with torch.no_grad():
            model.eval()
            probs = F.softmax(model(X), dim=-1)
            entropy = -(probs * (probs + 1e-9).log()).sum(dim=-1)     # (N,)
            hard_idx = torch.topk(entropy, k).indices
        challenge_entropy.append(float(entropy[hard_idx].mean()))
        Xc, yc = X[hard_idx], y[hard_idx]
        # SOLVER: GRPO on the challenge set.
        last_reward = 0.0
        for _ in range(steps_per_round):
            stats = grpo_step(model, Xc, yc, optimizer, group_size=group_size,
                              kl_coef=0.0, generator=gen)
            last_reward = stats["mean_reward"]
        round_rewards.append(last_reward)
    with torch.no_grad():
        model.eval()
        acc = (model(X).argmax(dim=-1) == y).float().mean().item()
    return {
        "round_rewards": round_rewards,
        "challenge_entropy": challenge_entropy,
        "final_accuracy": acc,
        # self-play health: solver reward trends up while challenger keeps finding hard items
        "solver_improved": round_rewards[-1] >= round_rewards[0],
    }

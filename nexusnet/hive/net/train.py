"""Real training loop for the NexusNet neural network: forward -> loss -> backward -> step.

Demonstrates genuine learning: gradients are computed by autograd, weights are updated by an
optimizer, and the loss measurably decreases while accuracy rises on a non-linear task. This is the
training machinery NexusNet uses to bootstrap (Ivy-League teachers / dreaming) and ultimately train
itself into its own model.
"""
from __future__ import annotations

from typing import Any

import torch
import torch.nn.functional as F

from .model import NexusNetModel


def make_nonlinear_dataset(
    *, n: int = 600, in_dim: int = 8, num_classes: int = 3, seed: int = 0, device: str = "cpu"
) -> tuple[torch.Tensor, torch.Tensor]:
    """A deterministic, non-linearly-separable classification task (a linear model can't ace it)."""
    g = torch.Generator(device="cpu").manual_seed(seed)
    X = torch.randn(n, in_dim, generator=g)
    # Non-linear label rule: interactions + a periodic term => needs hidden capacity to fit.
    feat = (
        torch.sin(1.5 * X[:, 0]) * X[:, 1]
        + (X[:, 2] * X[:, 3])
        - 0.7 * (X[:, 4] ** 2)
        + torch.tanh(X[:, 5] + X[:, 6])
    )
    y = torch.bucketize(
        feat, boundaries=torch.quantile(feat, torch.linspace(0, 1, num_classes + 1)[1:-1])
    ).clamp(max=num_classes - 1)
    return X.to(device), y.to(device)


def make_sequence_dataset(
    *, n: int = 600, seq_len: int = 12, vocab_size: int = 24, num_classes: int = 3,
    seed: int = 0, device: str = "cpu",
) -> tuple[torch.Tensor, torch.Tensor]:
    """Deterministic sequence-classification task: a token->value lookup + position weighting whose
    aggregate must be learned (embedding + attention + pooling). Not bag-of-words trivial."""
    g = torch.Generator(device="cpu").manual_seed(seed)
    tokens = torch.randint(0, vocab_size, (n, seq_len), generator=g)
    token_value = torch.randn(vocab_size, generator=g)          # fixed latent value per token id
    pos_weight = torch.linspace(0.5, 1.5, seq_len)              # position matters
    score = (token_value[tokens] * pos_weight).mean(dim=1)
    score = score + 0.4 * (token_value[tokens[:, 0]] * token_value[tokens[:, -1]])  # interaction
    bounds = torch.quantile(score, torch.linspace(0, 1, num_classes + 1)[1:-1])
    y = torch.bucketize(score, boundaries=bounds).clamp(max=num_classes - 1)
    return tokens.to(device), y.to(device)


def train_model(
    model: torch.nn.Module,
    X: torch.Tensor,
    y: torch.Tensor,
    *,
    epochs: int = 300,
    lr: float = 5e-3,
    balance_every: int = 25,
) -> dict[str, Any]:
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    model.train()
    loss_history: list[float] = []
    acc_history: list[float] = []
    grad_seen = False

    for epoch in range(epochs):
        optimizer.zero_grad()
        logits = model(X)
        loss = F.cross_entropy(logits, y)
        loss.backward()                                        # real autograd backprop
        # Confirm gradients actually flow to the parameters.
        if not grad_seen:
            grad_seen = any(p.grad is not None and p.grad.abs().sum() > 0 for p in model.parameters())
        optimizer.step()                                       # real weight update
        if balance_every and (epoch + 1) % balance_every == 0:
            model.update_load_bias()                           # DeepSeek load balancing
        with torch.no_grad():
            acc = (logits.argmax(dim=-1) == y).float().mean().item()
        loss_history.append(loss.item())
        acc_history.append(acc)

    return {
        "loss_history": loss_history,
        "acc_history": acc_history,
        "initial_loss": loss_history[0],
        "final_loss": loss_history[-1],
        "initial_accuracy": acc_history[0],
        "final_accuracy": acc_history[-1],
        "gradients_flowed": grad_seen,
        "num_parameters": model.num_parameters(),
    }


def train_demo(
    *,
    epochs: int = 300,
    seed: int = 0,
    device: str = "cpu",
    num_classes: int = 3,
    in_dim: int = 8,
) -> dict[str, Any]:
    """Build the model + data, train, and return the learning metrics."""
    torch.manual_seed(seed)
    X, y = make_nonlinear_dataset(in_dim=in_dim, num_classes=num_classes, seed=seed, device=device)
    model = NexusNetModel(
        in_dim=in_dim, d_model=32, d_hidden=64, num_experts=6, top_k=2,
        num_classes=num_classes, num_layers=2,
    ).to(device)
    metrics = train_model(model, X, y, epochs=epochs)
    metrics["device"] = device
    return metrics

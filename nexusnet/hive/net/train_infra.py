"""Wave-3: scaled-training infrastructure - checkpoint/resume, optimizer state, AMP, device.

`birth.train_language_model` trains from scratch on CPU. A real multi-session birth run on the GPU box
(RTX 5070 Ti) needs: resumable optimizer state, mixed-precision (AMP) autocast + GradScaler on CUDA,
and device placement. This module adds those without disturbing the simple birth path.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import torch
import torch.nn.functional as F


def save_training_state(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    step: int,
    *,
    path: str,
    meta: dict[str, Any] | None = None,
) -> str:
    """Persist a RESUMABLE training state (weights + optimizer moments + step), not just final weights."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_state": model.state_dict(),
            "optimizer_state": optimizer.state_dict(),
            "step": int(step),
            "meta": dict(meta or {}),
        },
        p,
    )
    return str(p)


def load_training_state(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None,
    *,
    path: str,
    map_location: str = "cpu",
) -> dict[str, Any]:
    """Restore weights (+ optimizer moments + step) to resume a run exactly where it stopped."""
    ckpt = torch.load(path, map_location=map_location)
    model.load_state_dict(ckpt["model_state"])
    if optimizer is not None and ckpt.get("optimizer_state") is not None:
        optimizer.load_state_dict(ckpt["optimizer_state"])
    return {"step": int(ckpt.get("step", 0)), "meta": ckpt.get("meta", {})}


def fit_lm(
    model: torch.nn.Module,
    x: torch.Tensor,
    y: torch.Tensor,
    *,
    steps: int = 100,
    lr: float = 3e-3,
    device: str | None = None,
    amp: bool = False,
    balance_every: int = 25,
    resume_from: str | None = None,
    checkpoint_path: str | None = None,
    checkpoint_every: int = 0,
) -> dict[str, Any]:
    """Resumable, device-aware, AMP-capable LM training loop.

    AMP autocast + GradScaler engage only on CUDA (no-op safe on CPU). Resumes optimizer state and
    step count from `resume_from`; periodically writes a resumable checkpoint to `checkpoint_path`.
    """
    dev = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
    model = model.to(dev)
    x, y = x.to(dev), y.to(dev)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    start_step = 0
    if resume_from is not None and Path(resume_from).exists():
        start_step = load_training_state(model, optimizer, path=resume_from,
                                         map_location=str(dev))["step"]

    use_amp = bool(amp and dev.type == "cuda")
    try:
        scaler = torch.amp.GradScaler("cuda", enabled=use_amp)
    except (AttributeError, TypeError):                          # older torch fallback
        scaler = torch.cuda.amp.GradScaler(enabled=use_amp)
    model.train()
    losses: list[float] = []
    grad_seen = False
    for i in range(start_step, start_step + steps):
        optimizer.zero_grad()
        with torch.autocast(device_type=dev.type, enabled=use_amp):
            logits = model(x)
            loss = F.cross_entropy(logits.reshape(-1, logits.size(-1)), y.reshape(-1))
        scaler.scale(loss).backward()
        if not grad_seen:
            grad_seen = any(p.grad is not None and p.grad.abs().sum() > 0 for p in model.parameters())
        scaler.step(optimizer)
        scaler.update()
        if balance_every and hasattr(model, "update_load_bias") and (i + 1) % balance_every == 0:
            model.update_load_bias()
        losses.append(float(loss))
        if checkpoint_path and checkpoint_every and (i + 1) % checkpoint_every == 0:
            save_training_state(model, optimizer, i + 1, path=checkpoint_path,
                                meta={"final_loss": losses[-1]})
    final_step = start_step + steps
    if checkpoint_path:
        save_training_state(model, optimizer, final_step, path=checkpoint_path,
                            meta={"final_loss": losses[-1] if losses else None})
    return {
        "device": str(dev),
        "amp": use_amp,
        "start_step": start_step,
        "final_step": final_step,
        "initial_loss": losses[0] if losses else None,
        "final_loss": losses[-1] if losses else None,
        "gradients_flowed": grad_seen,
        "resumed": resume_from is not None and Path(resume_from).exists() if resume_from else False,
    }

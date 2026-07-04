"""Wave-3: Teacher->student knowledge distillation as a REAL torch loss in the training graph.

The canon Ivy-League School distills external teacher models into expert students. The pure-Python
`collective.distillation.kd_loss` measures KD on given vectors but is not in the trainable graph;
this module wires distillation into actual backprop:

    L = alpha * CE(student, hard_labels) + (1 - alpha) * T^2 * KL(softmax(teacher/T) || softmax(student/T))

A `Teacher` here is any module/callable producing logits for the same task; its parameters are frozen
(no gradient) so only the student learns. `FrozenTeacher` wraps a trained student-shaped net as a
stand-in teacher for offline runs/tests; a real run binds an external-model adapter's logits instead.
"""
from __future__ import annotations

from typing import Any, Callable

import torch
import torch.nn as nn
import torch.nn.functional as F


def kd_loss_torch(
    student_logits: torch.Tensor,
    teacher_logits: torch.Tensor,
    hard_labels: torch.Tensor,
    *,
    alpha: float = 0.5,
    temperature: float = 2.0,
) -> dict[str, torch.Tensor]:
    """Differentiable KD loss. Forward KL(teacher||student) matches the teacher's soft targets."""
    if not 0.0 <= alpha <= 1.0:
        raise ValueError("alpha must be in [0, 1]")
    if temperature <= 0.0:
        raise ValueError("temperature must be positive")
    ce = F.cross_entropy(student_logits, hard_labels)
    t = temperature
    log_student = F.log_softmax(student_logits / t, dim=-1)
    teacher_prob = F.softmax(teacher_logits.detach() / t, dim=-1)   # detach: teacher is frozen
    kl = F.kl_div(log_student, teacher_prob, reduction="batchmean") * (t * t)
    total = alpha * ce + (1.0 - alpha) * kl
    return {"loss": total, "ce": ce.detach(), "kd": kl.detach()}


class FrozenTeacher(nn.Module):
    """Wrap a module as a frozen teacher: eval mode, params require_grad=False, logits detached."""

    def __init__(self, model: nn.Module) -> None:
        super().__init__()
        self.model = model
        self.model.eval()
        for p in self.model.parameters():
            p.requires_grad_(False)

    @torch.no_grad()
    def forward(self, *args, **kwargs) -> torch.Tensor:
        return self.model(*args, **kwargs)


def train_with_distillation(
    student: nn.Module,
    teacher: Callable[..., torch.Tensor],
    X: torch.Tensor,
    y: torch.Tensor,
    *,
    epochs: int = 60,
    lr: float = 3e-3,
    alpha: float = 0.5,
    temperature: float = 2.0,
    balance_every: int = 25,
) -> dict[str, Any]:
    """Train `student` against hard labels AND the (frozen) teacher's soft targets via real backprop."""
    optimizer = torch.optim.Adam((p for p in student.parameters() if p.requires_grad), lr=lr)
    student.train()
    with torch.no_grad():
        teacher_logits = teacher(X)
    history: list[float] = []
    kd_history: list[float] = []
    grad_seen = False
    for epoch in range(epochs):
        optimizer.zero_grad()
        student_logits = student(X)
        terms = kd_loss_torch(student_logits, teacher_logits, y, alpha=alpha, temperature=temperature)
        terms["loss"].backward()
        if not grad_seen:
            grad_seen = any(p.grad is not None and p.grad.abs().sum() > 0
                            for p in student.parameters() if p.requires_grad)
        optimizer.step()
        if balance_every and hasattr(student, "update_load_bias") and (epoch + 1) % balance_every == 0:
            student.update_load_bias()
        history.append(float(terms["loss"].detach()))
        kd_history.append(float(terms["kd"]))
    with torch.no_grad():
        student.eval()
        acc = (student(X).argmax(dim=-1) == y).float().mean().item()
        teacher_acc = (teacher_logits.argmax(dim=-1) == y).float().mean().item()
    return {
        "loss_history": history,
        "kd_history": kd_history,
        "initial_loss": history[0],
        "final_loss": history[-1],
        "gradients_flowed": grad_seen,
        "student_accuracy": acc,
        "teacher_accuracy": teacher_acc,
        # canon Teacher Replacement Protocol signal: student matched/surpassed the teacher
        "student_matches_teacher": acc >= teacher_acc - 1e-6,
    }

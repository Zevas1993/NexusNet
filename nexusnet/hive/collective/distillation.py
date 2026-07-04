"""Knowledge distillation (canon `knowledge_distillation`; Ivy-League teacher -> expert student).

Teacher(s) -> student via soft targets:

    L = alpha * CE(student, hard_labels) + (1 - alpha) * T^2 * KL(softmax(student/T) || softmax(teacher/T))

The Ivy-League School distills teacher models into expert students; parent-retirement review (PB-020)
is distillation-grade. Invariant: KL >= 0, and == 0 iff the two distributions are equal (Gibbs).
Pure-Python, deterministic, shadow-only.
"""
from __future__ import annotations

import math
from typing import Any

from ..kernel import tensor_ops as ops

Vector = list[float]
_EPS = 1e-12


def _temper(logits: Vector, temperature: float) -> Vector:
    return ops.softmax([z / temperature for z in logits])


def kl_divergence(p: Vector, q: Vector) -> float:
    """KL(p || q) = sum_i p_i * log(p_i / q_i). >= 0; == 0 iff p == q."""
    if len(p) != len(q):
        raise ValueError("distributions must match length")
    return sum(pi * math.log((pi + _EPS) / (qi + _EPS)) for pi, qi in zip(p, q) if pi > 0.0)


def kd_loss(
    *,
    student_logits: Vector,
    teacher_logits: Vector,
    hard_labels: Vector,
    alpha: float = 0.5,
    temperature: float = 2.0,
) -> dict[str, Any]:
    if not 0.0 <= alpha <= 1.0:
        raise ValueError("alpha must be in [0, 1]")
    if temperature <= 0.0:
        raise ValueError("temperature must be positive")
    student_probs = ops.softmax(student_logits)
    soft_student = _temper(student_logits, temperature)
    soft_teacher = _temper(teacher_logits, temperature)
    ce = ops.cross_entropy(student_probs, hard_labels)
    kl = kl_divergence(soft_teacher, soft_student)          # match teacher (forward KL)
    distill_term = (temperature ** 2) * kl
    loss = alpha * ce + (1.0 - alpha) * distill_term
    return {
        "loss": loss,
        "hard_ce": ce,
        "soft_kl": kl,
        "distill_term": distill_term,
        "temperature": temperature,
        "alpha": alpha,
        "production_mutation_allowed": False,
        "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
    }

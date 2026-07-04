"""B6 - Cortex dream-director (canon: Cortex is peer-to-router, the Dream Director).

Two roles, both shadow-only:
  1. Global-Workspace ignition gate (assimilation target 115 / Global Workspace Theory): only the
     top-salience capsule signals "ignite" and are broadcast hive-wide; sub-threshold signals stay
     local. This is the global-visibility bottleneck.
  2. Per-expert dream-task routing: the Cortex distributes individualized dream seeds per expert and
     supports individual / collaborative / competitive dream modes (canon addendum D).

Nothing here mutates production weights; dream artifacts are gated downstream.
"""
from __future__ import annotations

from typing import Any

from . import tensor_ops as ops

Vector = list[float]
DREAM_MODES = ("individual", "collaborative", "competitive")


class Cortex:
    def __init__(self, *, ignition_ratio: float = 0.5) -> None:
        if not 0.0 < ignition_ratio <= 1.0:
            raise ValueError("ignition_ratio must be in (0, 1]")
        self.ignition_ratio = ignition_ratio

    def ignite(self, *, saliences: list[float], poses: list[Vector]) -> dict[str, Any]:
        """Ignite only signals at or above ignition_ratio * max salience; broadcast their pose mix."""
        if not saliences:
            raise ValueError("need at least one salience")
        if len(saliences) != len(poses):
            raise ValueError("saliences and poses must align")
        threshold = self.ignition_ratio * max(saliences)
        ignited = [i for i, s in enumerate(saliences) if s >= threshold and s > 0.0]
        if not ignited:
            ignited = [max(range(len(saliences)), key=lambda i: saliences[i])]
        d = len(poses[0])
        weights = ops.softmax([saliences[i] for i in ignited])
        broadcast = [0.0] * d
        for w, i in zip(weights, ignited):
            for k in range(d):
                broadcast[k] += w * poses[i][k]
        return {
            "ignited_experts": ignited,
            "ignition_threshold": threshold,
            "broadcast": broadcast,
            "suppressed_experts": [i for i in range(len(saliences)) if i not in ignited],
        }

    def direct_dreams(
        self,
        *,
        poses: list[Vector],
        broadcast: Vector,
        mode: str = "individual",
    ) -> dict[str, Any]:
        """Assign each expert exactly one dream seed, shaped by the dream mode."""
        if mode not in DREAM_MODES:
            raise ValueError(f"unknown dream mode {mode!r}; allowed {DREAM_MODES}")
        assignments = []
        for e, pose in enumerate(poses):
            if mode == "individual":
                seed = list(pose)
            elif mode == "collaborative":
                seed = [0.5 * p + 0.5 * b for p, b in zip(pose, broadcast)]
            else:  # competitive: push away from the consensus broadcast
                seed = [p - b for p, b in zip(pose, broadcast)]
            assignments.append({
                "expert": e,
                "mode": mode,
                "dream_seed": ops.l2_normalize(seed),
            })
        return {
            "mode": mode,
            "assignments": assignments,
            "production_mutation_allowed": False,
            "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
        }

"""Quorum sensing (honeybee democracy) promotion gate.

A colony acts only after a critical density of agreement AND no active stop-signal (immune veto).

    support_fraction = support_votes / total_agents
    committed = (support_fraction >= quorum_threshold) AND (no active stop_signal)

Canon: this is the promotion quorum + stop-signal. Invariant: below quorum OR with an active
stop-signal, NO promotion. Pure-Python, deterministic, shadow-only - proposes, never bypasses gates.
"""
from __future__ import annotations

from typing import Any


def quorum_decision(
    *,
    support_votes: int,
    total_agents: int,
    quorum_threshold: float = 0.66,
    stop_signal: bool = False,
) -> dict[str, Any]:
    if total_agents <= 0:
        raise ValueError("total_agents must be positive")
    if not 0.0 < quorum_threshold <= 1.0:
        raise ValueError("quorum_threshold must be in (0, 1]")
    support_fraction = support_votes / total_agents
    quorum_reached = support_fraction >= quorum_threshold
    committed = quorum_reached and not stop_signal
    if stop_signal:
        reason = "stop_signal_active"
    elif not quorum_reached:
        reason = "below_quorum"
    else:
        reason = "quorum_reached"
    return {
        "committed": committed,
        "support_fraction": support_fraction,
        "quorum_threshold": quorum_threshold,
        "quorum_reached": quorum_reached,
        "stop_signal": stop_signal,
        "reason": reason,
        "production_mutation_allowed": False,
        "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
    }

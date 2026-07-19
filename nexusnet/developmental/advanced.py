from __future__ import annotations

import hashlib
import itertools
import math
import random
from copy import deepcopy
from typing import Any


class AdvancedDevelopmentalRuntime:
    """Executable shadow mechanisms for the Canon developmental target family."""

    def __init__(self, *, seed: int = 0) -> None:
        self.seed = int(seed)
        self._continuous_state: dict[str, float] = {}

    def assess(
        self,
        *,
        request_id: str,
        task_ref: str,
        trace_refs: list[str],
        evidence_refs: list[str],
        runtime_state: dict[str, Any],
        memory_state: dict[str, Any],
        eval_state: dict[str, Any],
    ) -> dict[str, Any]:
        signals = {
            "latency_error": self._unit(runtime_state.get("latency_error", 0.0)),
            "resource_pressure": self._unit(runtime_state.get("resource_pressure", 0.0)),
            "policy_risk": self._unit(runtime_state.get("policy_risk", 0.0)),
            "uncertainty": self._unit(memory_state.get("uncertainty", 0.0)),
            "contradiction": self._unit(memory_state.get("contradiction", 0.0)),
            "quality_gap": 1.0 - self._unit(eval_state.get("quality", 0.0)),
        }
        candidates = self._candidate_set(task_ref, signals)
        return {
            "surface_id": "advanced-developmental-runtime",
            "request_id": request_id,
            "homeostasis": self._homeostasis(signals),
            "replay_consolidation": self._replay(trace_refs, evidence_refs, signals),
            "world_model_rollout": self._rollout(signals),
            "diverse_candidates": self._sample_diverse(candidates),
            "cellular_growth": self._cellular_growth(signals),
            "neuromorphic_events": self._event_substrate(signals),
            "continuous_controller": self._continuous_control(signals),
            "combinatorial_search": self._combinations(candidates),
            "symbolic_change": self._symbolic_change(runtime_state, memory_state, eval_state),
            "memory_palace": self._memory_palace(task_ref, trace_refs, evidence_refs),
            "production_mutation_allowed": False,
        }

    def _homeostasis(self, signals: dict[str, float]) -> dict[str, Any]:
        action_scores = {
            "reduce-load": max(signals["resource_pressure"], signals["latency_error"]),
            "seek-evidence": max(signals["uncertainty"], signals["quality_gap"]),
            "repair-memory": signals["contradiction"],
            "hold": 1.0 - max(signals.values()),
        }
        selected = min(action_scores, key=lambda key: (-action_scores[key], key))
        return {
            "prediction_error": round(sum(signals.values()) / len(signals), 6),
            "action_scores": {key: round(value, 6) for key, value in action_scores.items()},
            "selected_action": selected,
            "viable": signals["policy_risk"] < 0.8 and signals["resource_pressure"] < 0.95,
        }

    def _replay(self, trace_refs: list[str], evidence_refs: list[str], signals: dict[str, float]) -> dict[str, Any]:
        episodes = [
            {
                "trace_ref": trace_ref,
                "priority": round(max(signals["quality_gap"], signals["contradiction"], 0.1) + index * 0.001, 6),
                "evidence_refs": list(evidence_refs),
            }
            for index, trace_ref in enumerate(trace_refs)
        ]
        episodes.sort(key=lambda item: (-item["priority"], item["trace_ref"]))
        return {
            "mode": "sleep-consolidation",
            "replay_count": len(episodes),
            "episodes": episodes,
            "proposed_abstractions": [f"abstraction:{self._digest(item['trace_ref'])}" for item in episodes],
            "promotion_required": True,
        }

    def _rollout(self, signals: dict[str, float]) -> dict[str, Any]:
        actions = ("prefetch", "compress", "reduce-parallelism", "hold")
        rollouts = []
        for action in actions:
            next_state = dict(signals)
            if action == "prefetch":
                next_state["latency_error"] *= 0.75
                next_state["resource_pressure"] = min(1.0, next_state["resource_pressure"] + 0.10)
            elif action == "compress":
                next_state["resource_pressure"] *= 0.70
                next_state["quality_gap"] = min(1.0, next_state["quality_gap"] + 0.05)
            elif action == "reduce-parallelism":
                next_state["resource_pressure"] *= 0.80
                next_state["latency_error"] = min(1.0, next_state["latency_error"] + 0.05)
            score = 1.0 - sum(next_state.values()) / len(next_state)
            rollouts.append({"action": action, "predicted_state": next_state, "score": round(score, 6)})
        rollouts.sort(key=lambda item: (-item["score"], item["action"]))
        return {"rollout_count": len(rollouts), "rollouts": rollouts, "selected": rollouts[0], "learned_model_claim": False}

    def _candidate_set(self, task_ref: str, signals: dict[str, float]) -> list[dict[str, Any]]:
        return [
            {"candidate_id": f"route:{self._digest(task_ref)}", "family": "route", "reward": 1.0 - signals["latency_error"]},
            {"candidate_id": f"memory:{self._digest(task_ref)}", "family": "memory", "reward": 1.0 - signals["contradiction"]},
            {"candidate_id": f"runtime:{self._digest(task_ref)}", "family": "runtime", "reward": 1.0 - signals["resource_pressure"]},
            {"candidate_id": f"evidence:{self._digest(task_ref)}", "family": "evidence", "reward": 1.0 - signals["uncertainty"]},
        ]

    def _sample_diverse(self, candidates: list[dict[str, Any]]) -> dict[str, Any]:
        rng = random.Random(self.seed)
        pool = deepcopy(candidates)
        selected = []
        while pool and len(selected) < 3:
            weights = [max(0.001, float(item["reward"])) for item in pool]
            chosen = rng.choices(pool, weights=weights, k=1)[0]
            selected.append(chosen)
            pool.remove(chosen)
        return {"sampling": "reward-proportional-without-replacement", "selected": selected, "ancestry_preserved": True}

    def _cellular_growth(self, signals: dict[str, float]) -> dict[str, Any]:
        cells = [
            {"cell_id": "perception", "neighbors": ["memory"], "health": 1.0 - signals["uncertainty"]},
            {"cell_id": "memory", "neighbors": ["perception", "control"], "health": 1.0 - signals["contradiction"]},
            {"cell_id": "control", "neighbors": ["memory"], "health": 1.0 - max(signals["policy_risk"], signals["resource_pressure"])},
        ]
        repairs = [item["cell_id"] for item in cells if item["health"] < 0.5]
        return {"cell_count": len(cells), "cells": cells, "repair_candidates": repairs, "local_rules_only": True}

    def _event_substrate(self, signals: dict[str, float]) -> dict[str, Any]:
        events = [
            {"event_id": f"signal:{key}", "salience": value, "sparse_route": key.split("_")[0]}
            for key, value in signals.items()
            if value >= 0.25
        ]
        events.sort(key=lambda item: (-item["salience"], item["event_id"]))
        return {"processed_count": len(events), "events": events, "dense_polling_required": False}

    def _continuous_control(self, signals: dict[str, float]) -> dict[str, Any]:
        for key, input_value in signals.items():
            previous = self._continuous_state.get(key, 0.0)
            derivative = -0.35 * previous + 0.65 * input_value
            self._continuous_state[key] = max(0.0, min(1.0, previous + 0.1 * derivative))
        return {"integration": "bounded-euler", "state": {key: round(value, 6) for key, value in self._continuous_state.items()}}

    @staticmethod
    def _combinations(candidates: list[dict[str, Any]]) -> dict[str, Any]:
        combinations = [
            {
                "left": left["candidate_id"],
                "right": right["candidate_id"],
                "joint_reward": round(math.sqrt(max(0.0, left["reward"] * right["reward"])), 6),
            }
            for left, right in itertools.combinations(candidates, 2)
        ]
        combinations.sort(key=lambda item: (-item["joint_reward"], item["left"], item["right"]))
        return {"combination_count": len(combinations), "combinations": combinations}

    @staticmethod
    def _symbolic_change(*states: dict[str, Any]) -> dict[str, Any]:
        changes = []
        for state_index, state in enumerate(states):
            for key, value in sorted(state.items()):
                if isinstance(value, (int, float, bool)):
                    changes.append({"symbol": f"s{state_index}.{key}", "operator": "observe", "value": value})
        return {"calculus": "typed-observation-delta", "changes": changes}

    def _memory_palace(self, task_ref: str, trace_refs: list[str], evidence_refs: list[str]) -> dict[str, Any]:
        rooms = {
            "goal": [task_ref],
            "episodes": list(trace_refs),
            "evidence": list(evidence_refs),
        }
        return {"palace_id": f"palace:{self._digest(task_ref)}", "rooms": rooms, "traversal_order": ["goal", "evidence", "episodes"]}

    @staticmethod
    def _unit(value: Any) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return 0.0
        if not math.isfinite(number):
            return 0.0
        return max(0.0, min(1.0, number))

    @staticmethod
    def _digest(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]

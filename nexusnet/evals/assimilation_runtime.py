from __future__ import annotations

import hashlib
import json
import operator
import random
from dataclasses import dataclass
from typing import Any, Callable


class DeterministicFailureFoundry:
    def run(
        self,
        *,
        scenario_id: str,
        seed: int,
        components: list[str],
        step_count: int,
        failure_probability: float,
    ) -> dict[str, Any]:
        if not scenario_id or not components or step_count <= 0:
            raise ValueError("scenario, components, and positive step_count are required")
        if not 0.0 <= failure_probability <= 1.0:
            raise ValueError("failure_probability must be between zero and one")
        rng = random.Random(seed)
        schedule = []
        for step in range(step_count):
            component = components[rng.randrange(len(components))]
            failed = rng.random() < failure_probability
            schedule.append({
                "step": step,
                "component": component,
                "event": "failure" if failed else "success",
                "latency_ticks": rng.randint(1, 9),
            })
        canonical = json.dumps(schedule, sort_keys=True, separators=(",", ":"))
        return {
            "scenario_id": scenario_id,
            "seed": seed,
            "schedule": schedule,
            "failure_count": sum(item["event"] == "failure" for item in schedule),
            "replay_digest": "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        }


@dataclass(frozen=True)
class CompiledRuntimeMonitor:
    monitor_id: str
    invariants: tuple[dict[str, Any], ...]

    def evaluate(self, event: dict[str, Any]) -> dict[str, Any]:
        operations = {
            "<=": operator.le,
            "<": operator.lt,
            ">=": operator.ge,
            ">": operator.gt,
            "==": operator.eq,
            "!=": operator.ne,
        }
        violations = []
        for invariant in self.invariants:
            metric = invariant["metric"]
            value = event.get(metric)
            passed = value is not None and operations[invariant["operator"]](float(value), float(invariant["threshold"]))
            if not passed:
                violations.append({**invariant, "observed": value})
        return {
            "monitor_id": self.monitor_id,
            "status": "tripped" if violations else "healthy",
            "violations": violations,
            "actions": sorted(set(item["action"] for item in violations)),
        }


class RuntimeMonitorSynthesizer:
    OPERATORS = {"<=", "<", ">=", ">", "==", "!="}

    def compile(self, *, monitor_id: str, invariants: list[dict[str, Any]]) -> CompiledRuntimeMonitor:
        if not monitor_id or not invariants:
            raise ValueError("monitor_id and invariants are required")
        normalized = []
        for invariant in invariants:
            if invariant.get("operator") not in self.OPERATORS:
                raise ValueError(f"unsupported monitor operator: {invariant.get('operator')}")
            if not all(key in invariant for key in ("metric", "threshold", "action")):
                raise ValueError("monitor invariant requires metric, operator, threshold, and action")
            normalized.append({
                "metric": str(invariant["metric"]),
                "operator": str(invariant["operator"]),
                "threshold": float(invariant["threshold"]),
                "action": str(invariant["action"]),
            })
        return CompiledRuntimeMonitor(monitor_id=monitor_id, invariants=tuple(normalized))


class BenchmarkHarnessFederation:
    def __init__(self) -> None:
        self._adapters: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {}

    def register(self, adapter_id: str, adapter: Callable[[dict[str, Any]], dict[str, Any]]) -> None:
        if not adapter_id or not callable(adapter):
            raise ValueError("benchmark adapter requires id and callable")
        self._adapters[adapter_id] = adapter

    def run_suite(self, *, suite_id: str, cases: list[dict[str, Any]], evidence_refs: list[str]) -> dict[str, Any]:
        if not suite_id or not cases or not evidence_refs:
            raise ValueError("benchmark suite requires id, cases, and evidence_refs")
        results = []
        for case in cases:
            adapter_id = str(case.get("adapter") or "")
            adapter = self._adapters.get(adapter_id)
            if adapter is None:
                raise KeyError(f"unregistered benchmark adapter: {adapter_id}")
            raw = adapter(dict(case))
            score = float(raw.get("score", 1.0 if raw.get("passed") else 0.0))
            results.append({
                "adapter": adapter_id,
                "case_id": str(case.get("case_id") or ""),
                "passed": bool(raw.get("passed")),
                "score": score,
                "details": {key: value for key, value in raw.items() if key not in {"passed", "score"}},
            })
        pass_count = sum(item["passed"] for item in results)
        mean_score = sum(item["score"] for item in results) / len(results)
        return {
            "suite_id": suite_id,
            "case_count": len(results),
            "pass_count": pass_count,
            "mean_score": round(mean_score, 6),
            "results": results,
            "evidence_refs": sorted(set(evidence_refs)),
            "promotion_allowed": pass_count == len(results),
        }

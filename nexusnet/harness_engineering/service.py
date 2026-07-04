from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import new_id, utcnow


class HarnessEngineeringService:
    """First-class governed records for agent harness design and optimization."""

    CONTRACT_ELEMENTS = ["required_outputs", "budgets", "permissions", "completion_conditions", "output_paths"]
    DEFAULT_PATTERNS = [
        "natural_language_agent_harness",
        "execution_contracts",
        "file_backed_durable_state",
        "module_ablation",
        "raw_trace_harness_optimization",
        "discipline_narrowing_self_evolution",
        "runtime_safety_constraints",
        "harness_lifecycle_security",
    ]

    def __init__(self, *, artifacts_dir: Path | str, events: Any | None = None):
        self.artifacts_dir = Path(artifacts_dir)
        self.output_dir = self.artifacts_dir / "harness-engineering"
        self.spec_dir = self.output_dir / "specs"
        self.ablation_dir = self.output_dir / "ablations"
        self.optimization_dir = self.output_dir / "optimizations"
        self.safety_dir = self.output_dir / "safety-rules"
        self.events = events

    def summary(self, *, limit: int = 100) -> dict[str, Any]:
        records = self._records(limit=limit)
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "record_count": len(records),
            "record_type_counts": self._counts(records, "record_type"),
            "status_counts": self._counts(records, "status"),
            "assimilated_patterns": list(self.DEFAULT_PATTERNS),
            "external_execution_allowed": False,
            "execution_allowed": False,
            "mutation_allowed": False,
            "optimization_runs_allowed": False,
            "latest_record": records[0] if records else None,
            "items": records,
        }

    def compact_summary(self, *, limit: int = 50) -> dict[str, Any]:
        payload = self.summary(limit=limit)
        return {
            "status_label": payload["status_label"],
            "record_count": payload["record_count"],
            "record_type_counts": payload["record_type_counts"],
            "status_counts": payload["status_counts"],
            "execution_allowed": False,
            "mutation_allowed": False,
            "optimization_runs_allowed": False,
            "latest_record": payload["latest_record"],
        }

    def register_spec(
        self,
        *,
        source: dict[str, Any] | None = None,
        harness_name: str,
        target_subsystem: str = "workflows",
        layers: dict[str, Any] | None = None,
        execution_contracts: list[dict[str, Any]] | None = None,
        durable_state_paths: list[str] | None = None,
        delegation_topology: str = "orchestrator_workers",
        module_inventory: list[str] | None = None,
        linked_trace_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        record = self._base_record(
            record_type="spec",
            status="registered_metadata_only",
            source=source,
            linked_trace_ids=linked_trace_ids,
        )
        record.update(
            {
                "harness_name": harness_name,
                "target_subsystem": target_subsystem,
                "layers": self._layers(layers),
                "execution_contracts": [self._contract(item) for item in (execution_contracts or [])],
                "durable_state": {
                    "file_backed": True,
                    "paths": [str(item) for item in (durable_state_paths or [])],
                    "survives_context_truncation": True,
                    "survives_restart": True,
                    "mutation_requires_execution_authority": True,
                },
                "delegation_topology": delegation_topology,
                "module_inventory": [str(item) for item in (module_inventory or [])],
                "execution_authority": self._execution_authority(["harness_spec_registration"]),
                "risk_flags": ["portable_harness_prompt_injection", "malicious_tool_binding", "contract_overreach"],
            }
        )
        self._finalize(record, self.spec_dir, "harness_engineering.spec_registered")
        return {"status_label": "STRONG ACCEPTED DIRECTION", "record": record}

    def record_ablation(
        self,
        *,
        harness_id: str,
        benchmark: str,
        baseline: dict[str, Any],
        variant: dict[str, Any],
        module_findings: list[dict[str, Any]] | None = None,
        linked_trace_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        record = self._base_record(record_type="ablation", status="ablation_recorded", linked_trace_ids=linked_trace_ids)
        record.update(
            {
                "harness_id": harness_id,
                "benchmark": benchmark,
                "baseline": baseline,
                "variant": variant,
                "module_findings": [dict(item) for item in (module_findings or [])],
                "efficiency": self._efficiency(baseline, variant),
                "recommendation": self._ablation_recommendation(module_findings or []),
                "execution_authority": self._execution_authority(["harness_optimization"]),
                "risk_flags": ["benchmark_overfit", "module_interaction_confound", "trace_privacy_review_required"],
            }
        )
        self._finalize(record, self.ablation_dir, "harness_engineering.ablation_recorded")
        return {"status_label": "STRONG ACCEPTED DIRECTION", "record": record}

    def propose_optimization(
        self,
        *,
        source: dict[str, Any] | None = None,
        target_harness_id: str,
        failure_trace_ids: list[str] | None = None,
        summary_trace_ids: list[str] | None = None,
        proposed_change_summary: str,
        candidate_changes: list[str] | None = None,
        transfer_eval_models: list[str] | None = None,
        linked_trace_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        record = self._base_record(
            record_type="optimization_proposal",
            status="optimization_proposed_metadata_only",
            source=source,
            linked_trace_ids=linked_trace_ids,
        )
        record.update(
            {
                "target_harness_id": target_harness_id,
                "proposed_change_summary": proposed_change_summary,
                "candidate_changes": [str(item) for item in (candidate_changes or [])],
                "raw_trace_policy": {
                    "raw_traces_required": True,
                    "raw_trace_ids": [str(item) for item in (failure_trace_ids or [])],
                    "summary_trace_ids": [str(item) for item in (summary_trace_ids or [])],
                    "summaries_alone_sufficient": False,
                    "privacy_review_required": True,
                },
                "self_evolution_loop": {
                    "enabled_as_proposal": True,
                    "attempt_scope": "narrow_until_failure_signal",
                    "broadening_requires_failed_acceptance_gate": True,
                },
                "acceptance_gate": {
                    "required": True,
                    "minimum_evidence": ["raw_trace", "score_delta", "cost_delta", "rollback_plan"],
                    "promotion_requires_product_sweep": True,
                },
                "transfer_eval": {
                    "required": True,
                    "models": [str(item) for item in (transfer_eval_models or [])],
                    "same_harness_cross_model": True,
                },
                "execution_authority": self._execution_authority(["harness_optimization", "autonomous_agent_execution"]),
                "risk_flags": ["optimizer_overfit", "raw_trace_sensitive_data", "autonomous_harness_mutation"],
            }
        )
        self._finalize(record, self.optimization_dir, "harness_engineering.optimization_proposed")
        return {"status_label": "STRONG ACCEPTED DIRECTION", "record": record}

    def record_safety_rule(
        self,
        *,
        source: dict[str, Any] | None = None,
        rule_id: str,
        phase: str,
        trigger: str,
        predicate: str,
        enforcement: str,
        defense_layers: list[str] | None = None,
        linked_trace_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        record = self._base_record(
            record_type="safety_rule",
            status="safety_rule_recorded_metadata_only",
            source=source,
            linked_trace_ids=linked_trace_ids,
        )
        record.update(
            {
                "rule_id": rule_id,
                "phase": phase,
                "rule": {
                    "trigger": trigger,
                    "predicate": predicate,
                    "enforcement": enforcement,
                    "dsl_shape": "trigger_predicate_enforcement",
                    "runtime_enforced": False,
                },
                "defense_layers": [str(item) for item in (defense_layers or [])],
                "execution_authority": self._execution_authority(["harness_safety_rule", "file_write"]),
                "risk_flags": ["safety_rule_bypass", "overblocking", "rule_prompt_injection"],
            }
        )
        self._finalize(record, self.safety_dir, "harness_engineering.safety_rule_recorded")
        return {"status_label": "STRONG ACCEPTED DIRECTION", "record": record}

    def _base_record(
        self,
        *,
        record_type: str,
        status: str,
        source: dict[str, Any] | None = None,
        linked_trace_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        record_id = new_id("harness")
        trace_ids = list(linked_trace_ids or []) or [f"trace_{record_id}"]
        return {
            "record_id": record_id,
            "record_type": record_type,
            "status": status,
            "source": {
                "source_name": "Harness Engineering",
                "source_url": "https://www.langchain.com/blog/the-anatomy-of-an-agent-harness",
                "observed_at": utcnow().isoformat(),
                **(source or {}),
            },
            "policy_path": [
                {
                    "stage": "harness-engineering",
                    "decision": "hold",
                    "reason": "harness specs, optimizers, and safety rules are metadata-only until eval/product-sweep/execution-authority gates pass",
                }
            ],
            "approval_path": {"decision": "not_requested", "human_approval_is_not_execution_authority": True},
            "product_sweep_gate_ids": [
                "harness-engineering-gate",
                "eval-gate",
                "promotion-provenance-gate",
                "product-sweep-security",
            ],
            "eval_suite_ids": ["harness_ablation", "workflow_completion", "prompt_security_red_team"],
            "telemetry_trace_ids": trace_ids,
            "execution_allowed": False,
            "mutation_allowed": False,
            "created_at": utcnow().isoformat(),
        }

    def _layers(self, layers: dict[str, Any] | None) -> dict[str, Any]:
        return {
            "backend_infrastructure": list((layers or {}).get("backend_infrastructure") or ["tools", "storage", "sandbox"]),
            "runtime_charter": list((layers or {}).get("runtime_charter") or ["contracts", "state", "delegation"]),
            "natural_language_harness": list((layers or {}).get("natural_language_harness") or ["roles", "stages", "failure_taxonomy"]),
        }

    def _contract(self, contract: dict[str, Any]) -> dict[str, Any]:
        missing = [key for key in self.CONTRACT_ELEMENTS if key not in contract]
        return {
            "contract_id": str(contract.get("contract_id") or new_id("contract")),
            "required_outputs": list(contract.get("required_outputs") or []),
            "budgets": dict(contract.get("budgets") or {}),
            "permissions": list(contract.get("permissions") or []),
            "completion_conditions": list(contract.get("completion_conditions") or []),
            "output_paths": list(contract.get("output_paths") or []),
            "contract_elements": list(self.CONTRACT_ELEMENTS),
            "missing_elements": missing,
            "valid": not missing,
        }

    def _efficiency(self, baseline: dict[str, Any], variant: dict[str, Any]) -> dict[str, Any]:
        return {
            "pass_rate_delta": self._number(variant, "pass_rate") - self._number(baseline, "pass_rate"),
            "prompt_token_reduction_ratio": self._ratio(self._number(baseline, "prompt_tokens"), self._number(variant, "prompt_tokens")),
            "tool_call_reduction_ratio": self._ratio(self._number(baseline, "tool_calls"), self._number(variant, "tool_calls")),
            "runtime_reduction_ratio": self._ratio(self._number(baseline, "runtime_minutes"), self._number(variant, "runtime_minutes")),
        }

    def _ablation_recommendation(self, module_findings: list[dict[str, Any]]) -> dict[str, Any]:
        positive = sorted(module_findings, key=lambda item: float(item.get("delta_pass_rate") or 0), reverse=True)
        prune = [
            str(item.get("module"))
            for item in module_findings
            if float(item.get("delta_pass_rate") or 0) < 0 and float(item.get("cost_delta") or 0) >= 0
        ]
        return {
            "preferred_module": str((positive[0] if positive else {}).get("module") or "none"),
            "prune_candidates": prune,
            "principle": "discipline_narrowing_before_expensive_broadening",
            "promotion_decision": "requires_repeat_ablation_and_product_sweep",
        }

    def _execution_authority(self, capabilities: list[str]) -> dict[str, Any]:
        return {
            "required": True,
            "service": "execution_authority",
            "lease_endpoint": "/ops/brain/execution-authority/leases/request",
            "required_capabilities": capabilities,
            "execution_allowed": False,
            "mutation_allowed": False,
            "reason": "Harness changes are portable high-impact control logic and require scoped expiring execution authority before execution or mutation.",
        }

    def _finalize(self, record: dict[str, Any], directory: Path, event_type: str) -> None:
        path = directory / f"{record['record_id']}.json"
        record["artifact_path"] = str(path)
        self._write(record, path)
        self._event(event_type, record)

    def _event(self, event_type: str, record: dict[str, Any]) -> None:
        if not self.events:
            return
        self.events.record(
            event_type=event_type,
            subject=f"harness_engineering:{record['record_id']}",
            trace_ids=record.get("telemetry_trace_ids") or [],
            payload={
                "record_id": record["record_id"],
                "record_type": record["record_type"],
                "status": record["status"],
                "decision": "hold",
                "execution_allowed": False,
                "mutation_allowed": False,
                "artifact_path": record.get("artifact_path"),
            },
        )

    def _records(self, *, limit: int) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for directory in [self.spec_dir, self.ablation_dir, self.optimization_dir, self.safety_dir]:
            if not directory.exists():
                continue
            for path in directory.glob("harness_*.json"):
                try:
                    items.append(json.loads(path.read_text(encoding="utf-8")))
                except (OSError, json.JSONDecodeError):
                    continue
        items.sort(key=lambda item: str(item.get("created_at") or ""), reverse=True)
        return items[:limit]

    def _write(self, payload: dict[str, Any], path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _counts(self, records: list[dict[str, Any]], key: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for record in records:
            value = str(record.get(key) or "unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts

    def _number(self, payload: dict[str, Any], key: str) -> float:
        try:
            return float(payload.get(key) or 0)
        except (TypeError, ValueError):
            return 0.0

    def _ratio(self, numerator: float, denominator: float) -> float:
        if denominator <= 0:
            return 0.0
        return numerator / denominator

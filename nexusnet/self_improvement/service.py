from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from nexus.schemas import new_id, utcnow


class SelfImprovementService:
    CATEGORIES = {
        "prompt_optimization",
        "workflow_improvement",
        "runtime_routing",
        "retrieval_policy",
        "memory_compaction",
        "eval_gap",
        "test_gap",
        "security_gate",
        "provider_fallback",
        "hardware_profile_rule",
        "operator_ux",
    }

    def __init__(self, *, artifacts_dir: Path | str, events: Any | None = None, product_sweep: Any | None = None):
        self.artifacts_dir = Path(artifacts_dir)
        self.output_dir = self.artifacts_dir / "self-improvement"
        self.validation_dir = self.output_dir / "validations"
        self.events = events
        self.product_sweep = product_sweep

    def summary(self, *, limit: int = 100) -> dict[str, Any]:
        items = self._records(limit=limit)
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "supported_categories": sorted(self.CATEGORIES),
            "proposal_count": len(items),
            "category_counts": self._counts(items, "category"),
            "status_counts": self._counts(items, "status"),
            "promotion_requires_eval_and_product_sweep": True,
            "execution_allowed": False,
            "mutation_allowed": False,
            "latest_proposal": items[0] if items else None,
            "items": items,
        }

    def compact_summary(self, *, limit: int = 50) -> dict[str, Any]:
        payload = self.summary(limit=limit)
        return {
            "status_label": payload["status_label"],
            "proposal_count": payload["proposal_count"],
            "category_counts": payload["category_counts"],
            "status_counts": payload["status_counts"],
            "promotion_ready_count": len([item for item in payload["items"] if item.get("status") == "validated"]),
            "execution_allowed": False,
            "mutation_allowed": False,
            "latest_proposal": payload["latest_proposal"],
        }

    def propose(
        self,
        *,
        category: str,
        target_subsystem: str,
        proposed_change_summary: str,
        evidence_links: list[str] | None = None,
        eval_suite_id: str = "regression_behavior",
        rollback_requirement: str = "restore_previous_governed_artifact",
        linked_trace_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        if category not in self.CATEGORIES:
            raise ValueError(f"unsupported self-improvement category: {category}")
        record_id = new_id("selfimprove")
        trace_ids = list(linked_trace_ids or []) or [f"trace_{record_id}"]
        path = self.output_dir / f"{record_id}.json"
        record = {
            "record_id": record_id,
            "status": "proposed",
            "tier": "tier_2_mainstream_local",
            "capability_family": "research",
            "source": {"source_type": "self_improvement", "evidence_links": list(evidence_links or []), "observed_at": utcnow().isoformat()},
            "target_subsystem": target_subsystem,
            "hardware_profile": {"state": "not_hardware_specific"},
            "runtime_candidates": [],
            "provider_candidates": [],
            "model_artifact_formats": [],
            "quantization_posture": {"state": "not_applicable"},
            "offline_posture": "local_metadata_only",
            "privacy_posture": "local_trace_metadata",
            "cost_posture": {"state": "not_metered"},
            "policy_path": [{"stage": "self-improvement", "decision": "hold", "reason": "eval-and-product-sweep-required"}],
            "approval_path": {"decision": "not_requested", "human_approval_is_not_execution_authority": True},
            "product_sweep_gate_ids": ["self-improvement-gate", "promotion-provenance-gate", "eval-gate"],
            "eval_suite_ids": [eval_suite_id],
            "telemetry_trace_ids": trace_ids,
            "provenance": {"metadata_only": True, "optimizer_inspiration": ["GEPA", "TextGrad"], "created_at": utcnow().isoformat()},
            "artifacts": [str(path).replace("\\", "/")],
            "execution_allowed": False,
            "mutation_allowed": False,
            "category": category,
            "proposed_change_summary": proposed_change_summary,
            "evidence_links": list(evidence_links or []),
            "rollback_requirement": rollback_requirement,
        }
        self._write(record)
        self._event("self_improvement.signal_detected", record)
        self._event("self_improvement.proposal_created", record)
        return {"status_label": "STRONG ACCEPTED DIRECTION", "proposal": record}

    def validate(self, *, proposal_id: str, eval_status: str, linked_trace_ids: list[str] | None = None) -> dict[str, Any]:
        proposal = self._require(proposal_id)
        validation_id = new_id("selfimprovevalidation")
        promotion_decision = "ready_for_product_sweep_review" if eval_status == "passed" else "not_promotable_without_passed_eval"
        validation = {
            "validation_id": validation_id,
            "proposal_id": proposal_id,
            "eval_status": eval_status,
            "promotion_decision": promotion_decision,
            "product_sweep_required": True,
            "gateway_required_for_mutation": True,
            "linked_trace_ids": list(linked_trace_ids or []),
            "created_at": utcnow().isoformat(),
            "execution_allowed": False,
            "mutation_allowed": False,
        }
        self.validation_dir.mkdir(parents=True, exist_ok=True)
        path = self.validation_dir / f"{validation_id}.json"
        validation["artifact_path"] = str(path).replace("\\", "/")
        path.write_text(json.dumps(validation, indent=2), encoding="utf-8")
        proposal["status"] = "validated" if eval_status == "passed" else "validation_blocked"
        proposal["latest_validation"] = validation
        self._write(proposal)
        self._event("self_improvement.validation_recorded", proposal, extra={"validation_id": validation_id, "eval_status": eval_status})
        return {"status_label": "STRONG ACCEPTED DIRECTION", "validation": validation, "proposal": proposal}

    def mine(self, *, source_limit: int = 100, max_proposals: int = 8, include_product_sweep: bool = True) -> dict[str, Any]:
        run_id = new_id("selfimprovemine")
        events = self.events.list(limit=max(1, min(int(source_limit or 1), 500))) if self.events else []
        event_signals = [signal for event in events if (signal := self._signal_from_event(event))]
        product_sweep_signals = self._product_sweep_signals() if include_product_sweep else []
        signals = [*event_signals, *product_sweep_signals]
        existing_signatures = {
            str((item.get("source") or {}).get("mined_signal_signature"))
            for item in self._records(limit=500)
            if (item.get("source") or {}).get("mined_signal_signature")
        }
        proposals: list[dict[str, Any]] = []
        deduped = 0
        for signal in signals:
            if len(proposals) >= max(0, min(int(max_proposals or 0), 50)):
                break
            if signal["signature"] in existing_signatures:
                deduped += 1
                continue
            proposal = self._proposal_from_signal(signal)
            self._write(proposal)
            self._event("self_improvement.signal_detected", proposal, extra={"signal": signal})
            self._event("self_improvement.proposal_created", proposal, extra={"mined": True, "signal": signal})
            proposals.append(proposal)
            existing_signatures.add(signal["signature"])
        mining_record = {
            "run_id": run_id,
            "created_at": utcnow().isoformat(),
            "status": "mined_metadata_only",
            "source_limit": source_limit,
            "max_proposals": max_proposals,
            "signal_count": len(signals),
            "event_signal_count": len(event_signals),
            "product_sweep_signal_count": len(product_sweep_signals),
            "created_proposal_count": len(proposals),
            "deduped_signal_count": deduped,
            "proposal_ids": [proposal["record_id"] for proposal in proposals],
            "execution_allowed": False,
            "mutation_allowed": False,
        }
        artifact_path = self._write_mining_record(mining_record)
        if self.events:
            self.events.record(
                event_type="self_improvement.mining_completed",
                subject=f"self-improvement-mining:{run_id}",
                payload={
                    "run_id": run_id,
                    "signal_count": len(signals),
                    "created_proposal_count": len(proposals),
                    "deduped_signal_count": deduped,
                    "execution_allowed": False,
                    "mutation_allowed": False,
                },
            )
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "run_id": run_id,
            "status": "mined_metadata_only",
            "signal_count": len(signals),
            "event_signal_count": len(event_signals),
            "product_sweep_signal_count": len(product_sweep_signals),
            "created_proposal_count": len(proposals),
            "deduped_signal_count": deduped,
            "signals": signals,
            "proposals": proposals,
            "artifact_path": artifact_path,
            "optimizer_pattern": "textual_feedback_to_governed_proposal",
            "optimizer_inspiration": ["GEPA", "TextGrad"],
            "promotion_requires_eval_and_product_sweep": True,
            "execution_allowed": False,
            "mutation_allowed": False,
        }

    def _records(self, *, limit: int) -> list[dict[str, Any]]:
        if not self.output_dir.exists():
            return []
        items = []
        for path in sorted(self.output_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
            if path.parent == self.validation_dir:
                continue
            try:
                items.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                continue
            if len(items) >= limit:
                break
        return items

    def _require(self, proposal_id: str) -> dict[str, Any]:
        path = self.output_dir / f"{proposal_id}.json"
        if not path.exists():
            raise KeyError(proposal_id)
        return json.loads(path.read_text(encoding="utf-8"))

    def _write(self, record: dict[str, Any]) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        path = self.output_dir / f"{record['record_id']}.json"
        record["artifacts"] = [str(path).replace("\\", "/")]
        path.write_text(json.dumps(record, indent=2), encoding="utf-8")

    def _signal_from_event(self, event: dict[str, Any]) -> dict[str, Any] | None:
        event_type = str(event.get("event_type") or "")
        subject = str(event.get("subject") or "")
        payload = event.get("payload") or {}
        category: str | None = None
        target = "workflow"
        eval_suite_id = "regression_behavior"
        summary = ""
        rollback = "restore_previous_governed_artifact"

        if event_type == "parallel_run.self_healing_signal_recorded":
            raw_category = str(payload.get("category") or "")
            category = self._parallel_signal_category(raw_category)
            target = str(payload.get("target") or self._target_for_category(category))
            eval_suite_id = self._eval_for_category(category)
            summary = f"Address parallel-run self-healing signal `{raw_category}` from {subject}."
            rollback = "restore_previous_parallel_workflow_or_validation_gate"
        elif event_type == "eval_suite.run_recorded" and str(payload.get("status") or "") in {"blocked", "failed"}:
            category = "eval_gap"
            target = "evals"
            eval_suite_id = str(payload.get("suite_type") or "regression_behavior")
            summary = f"Improve eval coverage or policy prerequisites after `{payload.get('status')}` result for {subject}."
            rollback = "restore_previous_eval_suite_metadata"
        elif "denied" in event_type or payload.get("decision") == "deny":
            category = "security_gate"
            target = "gate"
            eval_suite_id = "prompt_security_red_team"
            summary = f"Review denied action `{event_type}` for {subject}; improve gate messaging, policy, or tests."
            rollback = "restore_previous_gateway_policy"
        elif event_type.startswith("tier5.fallback_"):
            category = "provider_fallback"
            target = "runtime"
            eval_suite_id = "runtime_quality"
            summary = f"Refine governed Tier 5 fallback handling for {subject}."
            rollback = "restore_previous_runtime_routing_policy"

        if not category:
            return None
        signature_payload = {
            "event_type": event_type,
            "subject": subject,
            "category": category,
            "payload_category": payload.get("category"),
            "result_id": payload.get("result_id"),
            "decision": payload.get("decision"),
        }
        signature = hashlib.sha256(json.dumps(signature_payload, sort_keys=True).encode("utf-8")).hexdigest()[:16]
        return {
            "signature": signature,
            "event_id": event.get("event_id"),
            "event_type": event_type,
            "subject": subject,
            "category": category,
            "target_subsystem": target,
            "summary": summary,
            "eval_suite_id": eval_suite_id,
            "rollback_requirement": rollback,
            "trace_ids": [str(item) for item in (event.get("trace_ids") or [])],
            "evidence_links": [f"event:{event.get('event_id')}", subject],
            "payload": payload,
        }

    def _proposal_from_signal(self, signal: dict[str, Any]) -> dict[str, Any]:
        record_id = new_id("selfimprove")
        path = self.output_dir / f"{record_id}.json"
        trace_ids = list(signal.get("trace_ids") or []) or [f"trace_{record_id}"]
        return {
            "record_id": record_id,
            "status": "proposed",
            "tier": "tier_2_mainstream_local",
            "capability_family": "research",
            "source": {
                "source_type": "self_improvement_mining",
                "evidence_links": list(signal["evidence_links"]),
                "mined_signal_signature": signal["signature"],
                "observed_at": utcnow().isoformat(),
            },
            "target_subsystem": signal["target_subsystem"],
            "hardware_profile": {"state": "not_hardware_specific"},
            "runtime_candidates": [],
            "provider_candidates": [],
            "model_artifact_formats": [],
            "quantization_posture": {"state": "not_applicable"},
            "offline_posture": "local_metadata_only",
            "privacy_posture": "local_trace_metadata",
            "cost_posture": {"state": "not_metered"},
            "policy_path": [{"stage": "self-improvement", "decision": "hold", "reason": "eval-and-product-sweep-required"}],
            "approval_path": {"decision": "not_requested", "human_approval_is_not_execution_authority": True},
            "product_sweep_gate_ids": ["self-improvement-gate", "promotion-provenance-gate", "eval-gate"],
            "eval_suite_ids": [signal["eval_suite_id"]],
            "telemetry_trace_ids": trace_ids,
            "provenance": {
                "metadata_only": True,
                "optimizer_inspiration": ["GEPA", "TextGrad"],
                "mined_from_event": signal["event_id"],
                "created_at": utcnow().isoformat(),
            },
            "artifacts": [str(path).replace("\\", "/")],
            "execution_allowed": False,
            "mutation_allowed": False,
            "category": signal["category"],
            "proposed_change_summary": signal["summary"],
            "evidence_links": list(signal["evidence_links"]),
            "rollback_requirement": signal["rollback_requirement"],
            "mined_signals": [signal],
        }

    def _product_sweep_signals(self) -> list[dict[str, Any]]:
        if self.product_sweep is None:
            return []
        try:
            gates = self.product_sweep.gate_payload().get("phase_gates", [])
        except Exception:
            return []
        signals = []
        for gate in gates:
            for blocker in gate.get("blocked_by", []) or []:
                category = self._product_sweep_blocker_category(str(blocker))
                phase_id = str(gate.get("phase_id") or "unknown-phase")
                subject = f"product-sweep:{phase_id}:{blocker}"
                signature_payload = {
                    "event_type": "product_sweep.blocker",
                    "subject": subject,
                    "category": category,
                    "blocker": blocker,
                }
                signature = hashlib.sha256(json.dumps(signature_payload, sort_keys=True).encode("utf-8")).hexdigest()[:16]
                signals.append(
                    {
                        "signature": signature,
                        "event_id": None,
                        "event_type": "product_sweep.blocker",
                        "subject": subject,
                        "category": category,
                        "target_subsystem": self._target_for_category(category),
                        "summary": f"Resolve product-sweep blocker `{blocker}` in {phase_id} ({gate.get('title')}).",
                        "eval_suite_id": self._eval_for_category(category),
                        "rollback_requirement": "restore_previous_product_sweep_gate_mapping",
                        "trace_ids": [],
                        "evidence_links": [subject, f"product-sweep:{phase_id}"],
                        "payload": {
                            "phase_id": phase_id,
                            "phase_title": gate.get("title"),
                            "phase_status": gate.get("status"),
                            "blocker": blocker,
                            "acceptance_tests": gate.get("acceptance_tests", []),
                            "operator_surfaces": gate.get("operator_surfaces", []),
                        },
                    }
                )
        return signals

    def _product_sweep_blocker_category(self, blocker: str) -> str:
        normalized = blocker.lower()
        if any(token in normalized for token in ("runtime", "context", "model")):
            return "runtime_routing"
        if any(token in normalized for token in ("eval", "test")):
            return "eval_gap"
        if any(token in normalized for token in ("security", "license", "protocol", "policy")):
            return "security_gate"
        if "shadow" in normalized:
            return "workflow_improvement"
        return "workflow_improvement"

    def _parallel_signal_category(self, category: str) -> str:
        return {
            "missing_spec": "workflow_improvement",
            "weak_plan": "prompt_optimization",
            "unsafe_tool_request": "security_gate",
            "missing_validation": "test_gap",
            "model_mismatch": "runtime_routing",
            "environment_conflict": "hardware_profile_rule",
            "gate_gap": "security_gate",
            "review_gap": "workflow_improvement",
        }.get(category, "workflow_improvement")

    def _target_for_category(self, category: str) -> str:
        return {
            "prompt_optimization": "prompt",
            "workflow_improvement": "workflow",
            "runtime_routing": "runtime",
            "retrieval_policy": "retrieval",
            "memory_compaction": "memory",
            "eval_gap": "evals",
            "test_gap": "test",
            "security_gate": "gate",
            "provider_fallback": "runtime",
            "hardware_profile_rule": "adaptive_capabilities",
            "operator_ux": "operator_ux",
        }.get(category, "workflow")

    def _eval_for_category(self, category: str) -> str:
        return {
            "prompt_optimization": "workflow_completion",
            "workflow_improvement": "workflow_completion",
            "runtime_routing": "runtime_quality",
            "retrieval_policy": "rag_quality",
            "memory_compaction": "regression_behavior",
            "eval_gap": "regression_behavior",
            "test_gap": "regression_behavior",
            "security_gate": "prompt_security_red_team",
            "provider_fallback": "runtime_quality",
            "hardware_profile_rule": "runtime_quality",
            "operator_ux": "regression_behavior",
        }.get(category, "regression_behavior")

    def _write_mining_record(self, record: dict[str, Any]) -> str:
        path_dir = self.output_dir / "mining-runs"
        path_dir.mkdir(parents=True, exist_ok=True)
        path = path_dir / f"{record['run_id']}.json"
        path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        return str(path).replace("\\", "/")

    def _event(self, event_type: str, record: dict[str, Any], extra: dict[str, Any] | None = None) -> None:
        if not self.events:
            return
        self.events.record(
            event_type=event_type,
            subject=f"self-improvement:{record['record_id']}",
            trace_ids=record.get("telemetry_trace_ids", []),
            payload={
                "record_id": record["record_id"],
                "category": record["category"],
                "target_subsystem": record["target_subsystem"],
                "status": record["status"],
                "execution_allowed": False,
                "mutation_allowed": False,
                **(extra or {}),
            },
        )

    def _counts(self, items: list[dict[str, Any]], key: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in items:
            value = str(item.get(key) or "unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts

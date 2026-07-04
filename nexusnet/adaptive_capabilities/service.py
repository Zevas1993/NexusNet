from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import new_id, utcnow


class AdaptiveCapabilityService:
    HARDWARE_TIERS = [
        "tier_0_tiny_edge",
        "tier_1_constrained_edge",
        "tier_2_mainstream_local",
        "tier_3_premium_local",
        "tier_4_local_server",
        "tier_5_governed_cloud",
    ]
    CAPABILITY_FAMILIES = [
        "inference",
        "retrieval",
        "memory",
        "vision",
        "audio",
        "code_agent",
        "parallel_agent",
        "training",
        "eval",
        "research",
        "provider_fallback",
        "protocol_tooling",
    ]

    def __init__(self, *, artifacts_dir: Path | str, runtime_scorecards: Any | None = None, events: Any | None = None):
        self.artifacts_dir = Path(artifacts_dir)
        self.output_dir = self.artifacts_dir / "adaptive-capabilities"
        self.runtime_scorecards = runtime_scorecards
        self.events = events

    def summary(self, *, limit: int = 100) -> dict[str, Any]:
        items = self._records(limit=limit)
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "hardware_tiers": list(self.HARDWARE_TIERS),
            "capability_families": list(self.CAPABILITY_FAMILIES),
            "record_count": len(items),
            "tier_counts": self._counts(items, "tier"),
            "capability_family_counts": self._counts(items, "capability_family"),
            "local_first_default": True,
            "cloud_fallback_allowed_as_governed_tier": True,
            "execution_allowed": False,
            "mutation_allowed": False,
            "latest_record": items[0] if items else None,
            "items": items,
        }

    def compact_summary(self, *, limit: int = 50) -> dict[str, Any]:
        payload = self.summary(limit=limit)
        items = payload["items"]
        return {
            "status_label": payload["status_label"],
            "record_count": payload["record_count"],
            "tier_counts": payload["tier_counts"],
            "local_only_candidate_count": len([item for item in items if item.get("tier") != "tier_5_governed_cloud"]),
            "cloud_fallback_request_count": len([item for item in items if item.get("tier") == "tier_5_governed_cloud"]),
            "denied_provider_tool_actions": 0,
            "cloud_fallback_allowed_as_governed_tier": True,
            "execution_allowed": False,
            "mutation_allowed": False,
            "latest_record": payload["latest_record"],
        }

    def scorecards(self) -> dict[str, Any]:
        runtime_payload = self.runtime_scorecards.summary() if self.runtime_scorecards else {"items": []}
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "hardware_tiers": list(self.HARDWARE_TIERS),
            "scorecards": runtime_payload.get("items", []),
            "external_server_started": False,
            "execution_allowed": False,
            "mutation_allowed": False,
        }

    def profile(
        self,
        *,
        capability_family: str,
        source: dict[str, Any] | None = None,
        hardware_profile: dict[str, Any] | None = None,
        target_subsystem: str | None = None,
        requested_tier: str | None = None,
        privacy_posture: str | dict[str, Any] | None = None,
        cost_posture: dict[str, Any] | None = None,
        linked_trace_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        record = self._record(
            status="profiled",
            capability_family=capability_family,
            source=source or {"source_type": "operator", "source_ref": "manual-profile"},
            hardware_profile=hardware_profile or {},
            target_subsystem=target_subsystem,
            requested_tier=requested_tier,
            privacy_posture=privacy_posture,
            cost_posture=cost_posture,
            linked_trace_ids=linked_trace_ids,
        )
        self._write(record)
        self._event("adaptive.profile_recorded", record)
        self._event("adaptive.capability_scored", record)
        return {"status_label": "STRONG ACCEPTED DIRECTION", "record": record}

    def route(
        self,
        *,
        capability_family: str,
        source: dict[str, Any] | None = None,
        hardware_profile: dict[str, Any] | None = None,
        target_subsystem: str | None = None,
        allow_cloud_fallback: bool = False,
        local_satisfies_policy: bool = True,
        fallback_reason: str | None = None,
        privacy_posture: str | dict[str, Any] | None = None,
        cost_posture: dict[str, Any] | None = None,
        linked_trace_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        requested_tier = "tier_5_governed_cloud" if allow_cloud_fallback and not local_satisfies_policy else None
        status = "approval_required" if requested_tier == "tier_5_governed_cloud" else "routed_metadata_only"
        source_payload = source or {"source_type": "operator", "source_ref": "manual-route"}
        if fallback_reason:
            source_payload = {**source_payload, "fallback_reason": fallback_reason}
        record = self._record(
            status=status,
            capability_family=capability_family,
            source=source_payload,
            hardware_profile=hardware_profile or {},
            target_subsystem=target_subsystem,
            requested_tier=requested_tier,
            privacy_posture=privacy_posture,
            cost_posture=cost_posture,
            linked_trace_ids=linked_trace_ids,
        )
        self._write(record)
        self._event("adaptive.route_evaluated", record)
        return {"status_label": "STRONG ACCEPTED DIRECTION", "record": record}

    def _record(
        self,
        *,
        status: str,
        capability_family: str,
        source: dict[str, Any],
        hardware_profile: dict[str, Any],
        target_subsystem: str | None,
        requested_tier: str | None = None,
        privacy_posture: str | dict[str, Any] | None = None,
        cost_posture: dict[str, Any] | None = None,
        linked_trace_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        if capability_family not in self.CAPABILITY_FAMILIES:
            raise ValueError(f"unsupported capability_family: {capability_family}")
        tier = requested_tier or self._classify_tier(hardware_profile)
        if tier not in self.HARDWARE_TIERS:
            raise ValueError(f"unsupported hardware tier: {tier}")
        record_id = new_id("adaptive")
        trace_ids = list(linked_trace_ids or []) or [f"trace_{record_id}"]
        record = {
            "record_id": record_id,
            "status": status,
            "tier": tier,
            "capability_family": capability_family,
            "source": {**source, "observed_at": utcnow().isoformat()},
            "target_subsystem": target_subsystem or self._target_subsystem(capability_family),
            "hardware_profile": hardware_profile,
            "runtime_candidates": self._runtime_candidates(tier),
            "provider_candidates": self._provider_candidates(tier),
            "model_artifact_formats": self._model_artifact_formats(tier),
            "quantization_posture": self._quantization_posture(tier),
            "offline_posture": self._offline_posture(tier),
            "privacy_posture": privacy_posture or self._privacy_posture(tier),
            "cost_posture": cost_posture or self._cost_posture(tier),
            "policy_path": [{"stage": "adaptive-capability", "decision": "hold", "reason": "metadata-probe-first"}],
            "approval_path": {
                "decision": "approval_required" if tier == "tier_5_governed_cloud" else "not_requested",
                "human_approval_is_not_execution_authority": True,
            },
            "product_sweep_gate_ids": self._gate_ids(tier, capability_family),
            "eval_suite_ids": self._eval_suite_ids(capability_family),
            "telemetry_trace_ids": trace_ids,
            "provenance": {
                "service": "adaptive-capability-control-plane",
                "metadata_only": True,
                "created_at": utcnow().isoformat(),
            },
            "artifacts": [],
            "execution_allowed": False,
            "mutation_allowed": False,
        }
        return record

    def _classify_tier(self, hardware_profile: dict[str, Any]) -> str:
        if hardware_profile.get("cloud_fallback"):
            return "tier_5_governed_cloud"
        if hardware_profile.get("local_server"):
            return "tier_4_local_server"
        cpu_count = int(hardware_profile.get("cpu_count") or 1)
        ram_gb = self._float_or_zero(hardware_profile.get("ram_gb"))
        vram_gb = self._float_or_zero(hardware_profile.get("vram_gb"))
        if cpu_count <= 1 or (ram_gb and ram_gb <= 1.0):
            return "tier_0_tiny_edge"
        if ram_gb < 8.0 and vram_gb < 4.0:
            return "tier_1_constrained_edge"
        if ram_gb >= 128.0 or vram_gb >= 48.0:
            return "tier_4_local_server"
        if ram_gb >= 48.0 or vram_gb >= 16.0:
            return "tier_3_premium_local"
        return "tier_2_mainstream_local"

    def _runtime_candidates(self, tier: str) -> list[dict[str, Any]]:
        candidates = {
            "tier_0_tiny_edge": [("tiny-classifier", ["metadata_light", "short_context", "no_mutation"])],
            "tier_1_constrained_edge": [("onnxruntime-ep", ["short_context", "int8_or_int4", "no_autonomous_tools"]), ("llama-cpp", ["short_context", "gguf_small"])],
            "tier_2_mainstream_local": [("onnxruntime-ep", ["local_rag", "bounded_context"]), ("directml", ["windows_gpu_candidate"]), ("llama-cpp", ["gguf"])],
            "tier_3_premium_local": [("ollama", ["local_model_api"]), ("lm-studio", ["openai_compatible_local"]), ("mlc-llm", ["webgpu_or_native"])],
            "tier_4_local_server": [("vllm", ["high_throughput"]), ("sglang", ["local_server"]), ("tgi", ["batch_eval"])],
            "tier_5_governed_cloud": [("tier5-cloud-router", ["policy_required", "privacy_required", "budget_required"])],
        }[tier]
        return [{"runtime_id": runtime_id, "constraints": constraints, "execution_allowed": False} for runtime_id, constraints in candidates]

    def _provider_candidates(self, tier: str) -> list[dict[str, Any]]:
        return [
            {
                "provider_id": item["runtime_id"],
                "tier": tier,
                "registration_allowed": False,
                "execution_allowed": False,
            }
            for item in self._runtime_candidates(tier)
        ]

    def _model_artifact_formats(self, tier: str) -> list[str]:
        return {
            "tier_0_tiny_edge": ["tflite", "onnx-int8"],
            "tier_1_constrained_edge": ["onnx", "gguf-q4", "tflite"],
            "tier_2_mainstream_local": ["gguf", "onnx", "mlc"],
            "tier_3_premium_local": ["gguf", "onnx", "mlc", "mlx"],
            "tier_4_local_server": ["safetensors", "gguf", "onnx", "tensorrt"],
            "tier_5_governed_cloud": ["provider-native", "openai-compatible"],
        }[tier]

    def _quantization_posture(self, tier: str) -> dict[str, Any]:
        return {
            "tier": tier,
            "preferred": {
                "tier_0_tiny_edge": "int8",
                "tier_1_constrained_edge": "int4_or_int8",
                "tier_2_mainstream_local": "q4_or_q5",
                "tier_3_premium_local": "q5_or_q8",
                "tier_4_local_server": "fp16_or_quantized_batch",
                "tier_5_governed_cloud": "provider_declared",
            }[tier],
            "requires_validation": True,
        }

    def _offline_posture(self, tier: str) -> str:
        return "cloud_required_after_governance" if tier == "tier_5_governed_cloud" else "offline_capable_preferred"

    def _privacy_posture(self, tier: str) -> str:
        return "redaction_and_operator_approval_required" if tier == "tier_5_governed_cloud" else "local_first"

    def _cost_posture(self, tier: str) -> dict[str, Any]:
        return {"state": "operator_budget_required" if tier == "tier_5_governed_cloud" else "local_cost_only"}

    def _target_subsystem(self, capability_family: str) -> str:
        mapping = {
            "provider_fallback": "runtime",
            "parallel_agent": "parallel_runs",
            "protocol_tooling": "protocols",
            "code_agent": "parallel_runs",
            "eval": "evals",
        }
        return mapping.get(capability_family, capability_family)

    def _gate_ids(self, tier: str, capability_family: str) -> list[str]:
        gates = ["adaptive-capability-gate", "promotion-provenance-gate"]
        if tier == "tier_5_governed_cloud":
            gates.extend(["gateway-policy", "privacy-redaction-gate", "cost-budget-gate"])
        if capability_family in {"provider_fallback", "inference"}:
            gates.append("phase-7-runtime")
        if capability_family in {"training", "eval"}:
            gates.append("phase-8-training")
        return gates

    def _eval_suite_ids(self, capability_family: str) -> list[str]:
        mapping = {
            "inference": ["runtime_quality"],
            "provider_fallback": ["runtime_quality", "prompt_security_red_team"],
            "retrieval": ["rag_quality"],
            "code_agent": ["code_agent_issue_to_patch"],
            "parallel_agent": ["workflow_completion"],
            "training": ["regression_behavior"],
            "eval": ["regression_behavior"],
            "protocol_tooling": ["tool_call_accuracy", "prompt_security_red_team"],
        }
        return mapping.get(capability_family, ["regression_behavior"])

    def _records(self, *, limit: int) -> list[dict[str, Any]]:
        if not self.output_dir.exists():
            return []
        records = []
        for path in sorted(self.output_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
            try:
                records.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                continue
            if len(records) >= limit:
                break
        return records

    def _write(self, record: dict[str, Any]) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        path = self.output_dir / f"{record['record_id']}.json"
        record["artifacts"] = [str(path).replace("\\", "/")]
        path.write_text(json.dumps(record, indent=2), encoding="utf-8")

    def _event(self, event_type: str, record: dict[str, Any]) -> None:
        if not self.events:
            return
        self.events.record(
            event_type=event_type,
            subject=f"adaptive:{record['record_id']}",
            trace_ids=record.get("telemetry_trace_ids", []),
            payload={
                "record_id": record["record_id"],
                "tier": record["tier"],
                "capability_family": record["capability_family"],
                "status": record["status"],
                "execution_allowed": False,
                "mutation_allowed": False,
            },
        )

    def _counts(self, items: list[dict[str, Any]], key: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in items:
            value = str(item.get(key) or "unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts

    def _float_or_zero(self, value: Any) -> float:
        try:
            return float(value or 0.0)
        except (TypeError, ValueError):
            return 0.0

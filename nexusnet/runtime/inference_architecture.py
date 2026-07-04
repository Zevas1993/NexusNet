from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow
from nexusnet.policy import PolicyKernel


WorkloadType = Literal["chat", "research", "agentic", "coding", "multimodal", "batch"]
CacheScope = Literal["none", "session-local", "project-local", "remote-shared"]


class InferenceArchitectureRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan_id: str
    workload_type: WorkloadType
    runtime_targets: list[str] = Field(default_factory=list)
    context_tokens: int = 8192
    concurrent_sessions: int = 1
    latency_target_ms: int = 3000
    contains_private_data: bool = False
    cache_scope: CacheScope = "session-local"
    hardware_snapshot: dict[str, Any] = Field(default_factory=dict)
    upstream_cache_gate: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class InferenceArchitectureRegistry:
    def __init__(self, *, artifacts_dir: Path | None = None):
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.plans_dir = self.artifacts_dir / "runtime" / "inference-architecture" if self.artifacts_dir else None
        if self.plans_dir is not None:
            self.plans_dir.mkdir(parents=True, exist_ok=True)
        self._memory_plans: list[dict[str, Any]] = []
        self.policy_kernel = PolicyKernel.default()

    def plan(self, request: InferenceArchitectureRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = (
            request if isinstance(request, InferenceArchitectureRequest) else InferenceArchitectureRequest.model_validate(request)
        )
        selected_strategy = _strategy_for(normalized)
        upstream_cache_gate = _upstream_cache_gate(normalized.upstream_cache_gate)
        strategy_findings = _strategy_findings(normalized, selected_strategy, upstream_cache_gate=upstream_cache_gate)
        policy_scan = self.policy_kernel.scan(_policy_targets(normalized, strategy_findings))
        blocked = bool(strategy_findings) or policy_scan.summary.active_hard_fail_count > 0
        promotion_blockers = _inference_promotion_blockers(strategy_findings, upstream_cache_gate)
        plan = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "inference-architecture",
            "plan_id": normalized.plan_id,
            "workload_type": normalized.workload_type,
            "runtime_targets": normalized.runtime_targets,
            "status": "blocked" if blocked else "planned-shadow",
            "runtime_state": "degraded" if blocked else "live-bound",
            "created_at": utcnow().isoformat(),
            "selected_strategy": selected_strategy,
            "reason_codes": _reason_codes(normalized, selected_strategy),
            "expected_deltas": _expected_deltas(normalized, selected_strategy),
            "strategy_findings": strategy_findings,
            "policy_scan": policy_scan.model_dump(mode="json"),
            "upstream_cache_gate": upstream_cache_gate,
            "promotion_allowed": not blocked,
            "promotion_blockers": promotion_blockers,
            "promotion_boundary": "shadow-benchmark-before-runtime-architecture-promotion",
            "metadata": normalized.metadata,
        }
        self._persist(plan)
        return plan

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        plans = self._list_plans(limit=limit)
        latest = plans[0] if plans else None
        runtime_state = "static-canon"
        if latest:
            runtime_state = "degraded" if latest.get("status") == "blocked" else "live-bound"
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "inference-architecture",
            "authority": "NexusBrain",
            "runtime_state": runtime_state,
            "plan_count": len(plans),
            "shadow_count": sum(1 for plan in plans if plan.get("status") == "planned-shadow"),
            "blocked_count": sum(1 for plan in plans if plan.get("status") == "blocked"),
            "latest_plan": latest,
            "plans": plans,
            "strategy_catalog": _strategy_catalog(),
            "required_controls": _required_controls(),
            "operator_actions": _operator_actions(),
        }

    def scorecard(self) -> dict[str, Any]:
        summary = self.summary()
        return {
            **summary,
            "source_documents": [
                "docs/NEXUSNET_FORWARD_RESEARCH_RADAR_2026-04-28.md",
                "docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md",
                "docs/NEXUSNET_QUANTIZATION_AGENTIC_RESEARCH_EXPANSION_2026-04-28.md",
            ],
            "architecture_boundary": "inference-architecture-plans-are-shadow-only-until-benchmarked",
            "watch_items": [
                "speculative decoding",
                "disaggregated prefill/decode",
                "prefix caching",
                "KV reuse",
                "LMCache",
                "continuous batching",
            ],
        }

    def _persist(self, plan: dict[str, Any]) -> None:
        self._memory_plans.insert(0, plan)
        self._memory_plans = self._memory_plans[:50]
        if self.plans_dir is not None:
            safe_id = plan["plan_id"].replace(":", "_").replace("/", "_")
            path = self.plans_dir / f"{safe_id}.json"
            plan["artifact_path"] = str(path)
            path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

    def _list_plans(self, *, limit: int) -> list[dict[str, Any]]:
        plans = list(self._memory_plans)
        seen = {plan.get("plan_id") for plan in plans}
        if self.plans_dir is not None:
            for path in self.plans_dir.glob("*.json"):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if payload.get("plan_id") not in seen:
                    plans.append(payload)
        plans.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return plans[:limit]


def _strategy_for(request: InferenceArchitectureRequest) -> dict[str, Any]:
    long_context = request.context_tokens >= 32768
    high_concurrency = request.concurrent_sessions >= 8
    lmcache_target = any(target.lower() == "lmcache" for target in request.runtime_targets)
    supports_server_runtime = any(target.lower() in {"vllm", "sglang", "tensorrt-llm"} for target in request.runtime_targets)
    return {
        "speculative_decoding": supports_server_runtime and request.latency_target_ms <= 3000,
        "prefix_cache": long_context or request.workload_type in {"agentic", "research", "coding"},
        "continuous_batching": high_concurrency or supports_server_runtime,
        "disaggregated_prefill_decode": long_context and high_concurrency and supports_server_runtime,
        "kv_reuse": "lmcache-compatible" if lmcache_target or long_context else "session-cache",
        "cache_scope": request.cache_scope,
        "runtime_mode": "server-runtime" if supports_server_runtime else "local-runtime",
        "state": "shadow-plan",
    }


def _strategy_findings(
    request: InferenceArchitectureRequest,
    strategy: dict[str, Any],
    *,
    upstream_cache_gate: dict[str, Any],
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if request.contains_private_data and strategy["cache_scope"] == "remote-shared":
        findings.append(
            {
                "rule_id": "private_remote_cache_requires_sandbox_or_redaction",
                "severity": "hard_fail",
                "message": "Private workload context cannot use remote shared cache without sandbox/redaction proof.",
            }
        )
    if strategy["disaggregated_prefill_decode"] and not request.hardware_snapshot.get("local_gpu"):
        findings.append(
            {
                "rule_id": "disaggregated_prefill_decode_requires_gpu_capacity",
                "severity": "hard_fail",
                "message": "Disaggregated prefill/decode plans require GPU capacity evidence before shadow planning.",
            }
        )
    if _cache_gate_blocked(upstream_cache_gate):
        findings.append(
            {
                "rule_id": "inference_architecture_blocks_cache_gate",
                "severity": "hard_fail",
                "message": "Inference architecture plans cannot promote while upstream effective-context/cache evidence is blocked.",
            }
        )
    return findings


def _upstream_cache_gate(gate: dict[str, Any]) -> dict[str, Any]:
    blockers = sorted(
        {
            str(item)
            for item in [
                *(gate.get("blockers") or []),
                *(gate.get("promotion_blockers") or []),
            ]
            if str(item)
        }
    )
    return {
        "promotion_allowed": gate.get("promotion_allowed"),
        "status": gate.get("status") or ("blocked" if gate.get("promotion_allowed") is False or blockers else "not_provided"),
        "blockers": blockers,
        "source": gate.get("source") or "effective_context_cache_ledger",
    }


def _cache_gate_blocked(gate: dict[str, Any]) -> bool:
    return bool(gate.get("promotion_allowed") is False or gate.get("status") == "blocked" or gate.get("blockers"))


def _inference_promotion_blockers(findings: list[dict[str, Any]], upstream_cache_gate: dict[str, Any]) -> list[str]:
    blockers = [finding["rule_id"] for finding in findings if finding.get("severity") == "hard_fail"]
    blockers.extend(str(item) for item in upstream_cache_gate.get("blockers") or [])
    if upstream_cache_gate.get("promotion_allowed") is False:
        blockers.append("cache_promotion_not_allowed")
    return sorted(set(blockers))


def _policy_targets(request: InferenceArchitectureRequest, findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "target_id": f"inference-cache::{request.plan_id}",
            "target_type": "tool_execution",
            "metadata": {
                "write_enabled": bool(findings),
                "sandboxed": not findings,
                "tool_scope": request.cache_scope,
            },
        },
        {
            "target_id": f"inference-update::{request.plan_id}",
            "target_type": "autonomous_update",
            "metadata": {
                "promotion_requested": False,
                "rollback_plan": "runtime-architecture-shadow-rollback",
                "monitoring_plan": "latency-throughput-quality-cache-hit-monitor",
            },
        },
    ]


def _reason_codes(request: InferenceArchitectureRequest, strategy: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if request.context_tokens >= 32768:
        reasons.append("long_context_cache_economics")
    if request.concurrent_sessions >= 8:
        reasons.append("continuous_batching")
    if strategy["speculative_decoding"]:
        reasons.append("latency_speculative_decode")
    if strategy["disaggregated_prefill_decode"]:
        reasons.append("prefill_decode_split")
    if strategy["kv_reuse"] == "lmcache-compatible":
        reasons.append("kv_reuse_lmcache")
    return reasons or ["baseline_runtime_strategy"]


def _expected_deltas(request: InferenceArchitectureRequest, strategy: dict[str, Any]) -> dict[str, Any]:
    return {
        "latency": "lower" if strategy["speculative_decoding"] else "neutral",
        "throughput": "higher" if strategy["continuous_batching"] else "neutral",
        "cache_hit_rate": "higher" if strategy["prefix_cache"] else "neutral",
        "memory_pressure": "reduced" if strategy["kv_reuse"] == "lmcache-compatible" else "baseline",
        "requires_benchmark": True,
    }


def _strategy_catalog() -> list[dict[str, str]]:
    return [
        {"strategy_id": "speculative-decoding", "status": "shadow-capable"},
        {"strategy_id": "prefix-caching", "status": "shadow-capable"},
        {"strategy_id": "kv-reuse-lmcache", "status": "shadow-capable"},
        {"strategy_id": "continuous-batching", "status": "shadow-capable"},
        {"strategy_id": "disaggregated-prefill-decode", "status": "benchmark-required"},
    ]


def _required_controls() -> list[str]:
    return [
        "speculative_decoding",
        "prefix_caching",
        "kv_reuse",
        "lmcache_compatibility",
        "continuous_batching",
        "disaggregated_prefill_decode",
        "cache_privacy_boundary",
        "latency_throughput_quality_benchmarks",
    ]


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/inference-architecture"},
        "plan": {"method": "POST", "endpoint": "/ops/brain/inference-architecture/plan"},
        "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/inference-architecture"},
    }

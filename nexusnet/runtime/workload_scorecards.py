from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow
from nexusnet.policy import PolicyKernel


WorkloadFit = Literal["chat", "research", "coding", "agent_loop", "batch", "long_context", "multimodal"]
BatchingMode = Literal["none", "static", "continuous", "chunked_prefill", "disaggregated_pd"]
CachePrivacyBoundary = Literal["session", "project", "user", "shared", "remote-shared"]


class RuntimeWorkloadScorecardRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scorecard_id: str
    runtime_id: str
    backend: str
    model_id: str
    workload_type: WorkloadFit
    hardware_lane: str
    quantization_policy: str = ""
    context_tokens: int = 8192
    max_effective_context_tokens: int = 8192
    ttft_ms_p50: int = 0
    ttft_ms_p95: int = 0
    itl_ms_p50: int = 0
    itl_ms_p95: int = 0
    tokens_per_sec_decode: float = 0.0
    throughput_tokens_per_sec: float = 0.0
    vram_gb: float = 0.0
    ram_gb: float = 0.0
    cache_bytes_gpu: int = 0
    cache_bytes_cpu: int = 0
    cache_bytes_disk: int = 0
    prefix_cache_hit_rate: float = 0.0
    kv_cache_hit_rate: float = 0.0
    batching_mode: BatchingMode = "none"
    cache_privacy_boundary: CachePrivacyBoundary = "session"
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    fallback_used: bool = False
    fallback_reason: str = ""
    quality_delta: float = 0.0
    eval_refs: list[str] = Field(default_factory=list)
    trace_refs: list[str] = Field(default_factory=list)
    hardware_refs: list[str] = Field(default_factory=list)
    cache_refs: list[str] = Field(default_factory=list)
    contains_private_data: bool = False
    upstream_productization_gate: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RuntimeWorkloadScorecardRegistry:
    def __init__(self, *, artifacts_dir: Path | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.records_dir = self.artifacts_dir / "runtime" / "workload-scorecards" if self.artifacts_dir else None
        if self.records_dir is not None:
            self.records_dir.mkdir(parents=True, exist_ok=True)
        self._memory_records: list[dict[str, Any]] = []
        self.policy_kernel = PolicyKernel.default()

    def record(self, request: RuntimeWorkloadScorecardRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = (
            request
            if isinstance(request, RuntimeWorkloadScorecardRequest)
            else RuntimeWorkloadScorecardRequest.model_validate(request)
        )
        upstream_productization_gate = _upstream_productization_gate(normalized.upstream_productization_gate)
        findings = _scorecard_findings(normalized, upstream_productization_gate=upstream_productization_gate)
        policy_scan = self.policy_kernel.scan(_policy_targets(normalized, findings))
        blocked = _has_hard_fail(findings) or policy_scan.summary.active_hard_fail_count > 0
        warning = any(finding.get("severity") == "warning" for finding in findings)
        promotion_blockers = _runtime_promotion_blockers(findings, upstream_productization_gate)
        record = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "runtime-workload-scorecards",
            "scorecard_id": normalized.scorecard_id,
            "runtime_id": normalized.runtime_id,
            "backend": normalized.backend,
            "model_id": normalized.model_id,
            "workload_type": normalized.workload_type,
            "status": "blocked" if blocked else ("warning" if warning else "measured"),
            "runtime_state": "degraded" if blocked else "live-bound",
            "created_at": utcnow().isoformat(),
            "hardware": _hardware(normalized),
            "context": _context(normalized),
            "latency": _latency(normalized),
            "throughput": _throughput(normalized),
            "cache": _cache(normalized),
            "cost": _cost(normalized),
            "fallback": {
                "used": normalized.fallback_used,
                "reason": normalized.fallback_reason,
            },
            "quality": {
                "quality_delta": normalized.quality_delta,
                "requires_eval": True,
            },
            "eval_refs": normalized.eval_refs,
            "trace_refs": normalized.trace_refs,
            "hardware_refs": normalized.hardware_refs,
            "cache_refs": normalized.cache_refs,
            "contains_private_data": normalized.contains_private_data,
            "scorecard_findings": findings,
            "policy_scan": policy_scan.model_dump(mode="json"),
            "upstream_productization_gate": upstream_productization_gate,
            "promotion_allowed": not blocked,
            "promotion_blockers": promotion_blockers,
            "required_controls": _required_controls(),
            "promotion_boundary": "runtime-claims-require-latency-throughput-memory-cache-cost-eval-trace-and-hardware-evidence",
            "operator_actions": _operator_actions(),
            "metadata": normalized.metadata,
        }
        self._persist(record)
        return record

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        records = self._list_records(limit=limit)
        measured = [record for record in records if record.get("status") in {"measured", "warning"}]
        latest = records[0] if records else None
        runtime_state = "static-canon"
        if latest:
            runtime_state = "degraded" if latest.get("status") == "blocked" else "live-bound"
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "runtime-workload-scorecards",
            "authority": "NexusBrain",
            "runtime_state": runtime_state,
            "scorecard_count": len(records),
            "measured_count": len(measured),
            "warning_count": sum(1 for record in records if record.get("status") == "warning"),
            "blocked_count": sum(1 for record in records if record.get("status") == "blocked"),
            "average_ttft_ms_p95": _average(record.get("latency", {}).get("ttft_ms_p95", 0) for record in measured),
            "average_decode_tokens_per_sec": _average(
                record.get("throughput", {}).get("tokens_per_sec_decode", 0.0) for record in measured
            ),
            "average_cache_hit_rate": _average(record.get("cache", {}).get("kv_cache_hit_rate", 0.0) for record in measured),
            "latest_scorecard": latest,
            "scorecards": records,
            "required_controls": _required_controls(),
            "operator_actions": _operator_actions(),
            "runtime_truth_boundary": "runtime-fit-is-measured-per-workload-not-inferred-from-model-size-or-backend-name",
        }

    def scorecard(self) -> dict[str, Any]:
        summary = self.summary()
        return {
            **summary,
            "source_documents": [
                "docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md#runtime-workload-scorecard",
                "docs/NEXUSNET_QUANTIZATION_AGENTIC_RESEARCH_EXPANSION_2026-04-28.md",
                "docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md",
            ],
            "metrics": _required_controls(),
            "control_panel_label": "Runtime Workload Scorecards",
        }

    def _persist(self, record: dict[str, Any]) -> None:
        self._memory_records = [item for item in self._memory_records if item.get("scorecard_id") != record.get("scorecard_id")]
        self._memory_records.insert(0, record)
        self._memory_records = self._memory_records[:50]
        if self.records_dir is not None:
            safe_id = record["scorecard_id"].replace(":", "_").replace("/", "_")
            path = self.records_dir / f"{safe_id}.json"
            record["artifact_path"] = str(path)
            path.write_text(json.dumps(record, indent=2), encoding="utf-8")

    def _list_records(self, *, limit: int) -> list[dict[str, Any]]:
        records = list(self._memory_records)
        seen = {record.get("scorecard_id") for record in records}
        if self.records_dir is not None:
            for path in self.records_dir.glob("*.json"):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if payload.get("scorecard_id") not in seen:
                    records.append(payload)
        records.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return records[:limit]


def _hardware(request: RuntimeWorkloadScorecardRequest) -> dict[str, Any]:
    return {
        "hardware_lane": request.hardware_lane,
        "vram_gb": request.vram_gb,
        "ram_gb": request.ram_gb,
        "hardware_refs": request.hardware_refs,
    }


def _context(request: RuntimeWorkloadScorecardRequest) -> dict[str, Any]:
    raw = max(request.context_tokens, 1)
    return {
        "context_tokens": request.context_tokens,
        "max_effective_context_tokens": request.max_effective_context_tokens,
        "effective_context_ratio": round(request.max_effective_context_tokens / raw, 4),
    }


def _latency(request: RuntimeWorkloadScorecardRequest) -> dict[str, int]:
    return {
        "ttft_ms_p50": request.ttft_ms_p50,
        "ttft_ms_p95": request.ttft_ms_p95,
        "itl_ms_p50": request.itl_ms_p50,
        "itl_ms_p95": request.itl_ms_p95,
    }


def _throughput(request: RuntimeWorkloadScorecardRequest) -> dict[str, float]:
    return {
        "tokens_per_sec_decode": request.tokens_per_sec_decode,
        "throughput_tokens_per_sec": request.throughput_tokens_per_sec,
    }


def _cache(request: RuntimeWorkloadScorecardRequest) -> dict[str, Any]:
    return {
        "cache_privacy_boundary": request.cache_privacy_boundary,
        "prefix_cache_hit_rate": request.prefix_cache_hit_rate,
        "kv_cache_hit_rate": request.kv_cache_hit_rate,
        "cache_bytes_gpu": request.cache_bytes_gpu,
        "cache_bytes_cpu": request.cache_bytes_cpu,
        "cache_bytes_disk": request.cache_bytes_disk,
        "batching_mode": request.batching_mode,
        "cache_refs": request.cache_refs,
    }


def _cost(request: RuntimeWorkloadScorecardRequest) -> dict[str, Any]:
    return {
        "cost_per_1k_input": request.cost_per_1k_input,
        "cost_per_1k_output": request.cost_per_1k_output,
        "owned_hardware": request.cost_per_1k_input == 0.0 and request.cost_per_1k_output == 0.0,
    }


def _scorecard_findings(
    request: RuntimeWorkloadScorecardRequest,
    *,
    upstream_productization_gate: dict[str, Any],
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if request.contains_private_data and request.cache_privacy_boundary in {"shared", "remote-shared"}:
        findings.append(_finding("runtime_scorecard_private_shared_cache_blocked", "Private runtime context cannot use shared or remote-shared cache boundaries."))
    if not request.eval_refs:
        findings.append(_finding("runtime_scorecard_requires_eval_refs", "Runtime workload scorecards require eval evidence."))
    if not request.trace_refs:
        findings.append(_finding("runtime_scorecard_requires_trace_refs", "Runtime workload scorecards require trace evidence."))
    if not request.hardware_refs:
        findings.append(_finding("runtime_scorecard_requires_hardware_refs", "Runtime workload scorecards require hardware evidence."))
    if request.max_effective_context_tokens > request.context_tokens:
        findings.append(_finding("runtime_scorecard_effective_context_exceeds_raw", "Effective context cannot exceed raw context without an external memory expansion claim."))
    if request.fallback_used and not request.fallback_reason.strip():
        findings.append(_finding("runtime_scorecard_fallback_requires_reason", "Fallback runtime use must explain why the preferred lane was unavailable."))
    if request.ttft_ms_p95 <= 0 or request.tokens_per_sec_decode <= 0:
        findings.append(_finding("runtime_scorecard_requires_latency_and_decode_metrics", "Runtime workload scorecards require TTFT and decode speed metrics."))
    if abs(request.quality_delta) > 0.05:
        findings.append(_finding("runtime_scorecard_quality_delta_warning", "Runtime or quantization quality delta is large enough to require review.", severity="warning"))
    if _productization_gate_blocked(upstream_productization_gate):
        findings.append(
            _finding(
                "runtime_scorecard_blocks_productization_gate",
                "Runtime workload scorecards cannot promote runtime claims while productization readiness gates are blocked.",
            )
        )
    return findings


def _upstream_productization_gate(gate: dict[str, Any]) -> dict[str, Any]:
    open_gates = sorted(
        {
            str(item)
            for item in [
                *(gate.get("open_gates") or []),
                *(gate.get("blockers") or []),
            ]
            if str(item)
        }
    )
    return {
        "release_ready": gate.get("release_ready"),
        "status": gate.get("status") or ("blocked" if gate.get("release_ready") is False or open_gates else "not_provided"),
        "open_gates": open_gates,
        "source": gate.get("source") or "productization_readiness",
    }


def _productization_gate_blocked(gate: dict[str, Any]) -> bool:
    return bool(gate.get("release_ready") is False or gate.get("open_gates"))


def _runtime_promotion_blockers(findings: list[dict[str, str]], upstream_productization_gate: dict[str, Any]) -> list[str]:
    blockers = [finding["rule_id"] for finding in findings if finding.get("severity") == "hard_fail"]
    blockers.extend(str(item) for item in upstream_productization_gate.get("open_gates") or [])
    return sorted(set(blockers))


def _policy_targets(request: RuntimeWorkloadScorecardRequest, findings: list[dict[str, str]]) -> list[dict[str, Any]]:
    hard_findings = _has_hard_fail(findings)
    return [
        {
            "target_id": f"runtime-scorecard::{request.scorecard_id}",
            "target_type": "artifact",
            "metadata": {
                "promotion_requested": True,
                "license_state": "approved",
                "provenance_refs": [*request.eval_refs, *request.trace_refs, *request.hardware_refs],
            },
        },
        {
            "target_id": f"runtime-scorecard-cache::{request.scorecard_id}",
            "target_type": "tool_execution",
            "metadata": {
                "write_enabled": hard_findings,
                "sandboxed": not hard_findings,
                "tool_scope": request.cache_privacy_boundary,
            },
        },
    ]


def _finding(rule_id: str, message: str, severity: str = "hard_fail") -> dict[str, str]:
    return {"rule_id": rule_id, "severity": severity, "message": message}


def _has_hard_fail(findings: list[dict[str, str]]) -> bool:
    return any(finding.get("severity") == "hard_fail" for finding in findings)


def _average(values: Any) -> float:
    realized = [float(value or 0.0) for value in values]
    if not realized:
        return 0.0
    return round(sum(realized) / len(realized), 4)


def _required_controls() -> list[str]:
    return [
        "ttft_ms_p50",
        "ttft_ms_p95",
        "itl_ms_p50",
        "itl_ms_p95",
        "tokens_per_sec_decode",
        "throughput_tokens_per_sec",
        "max_effective_context_tokens",
        "kv_cache_hit_rate",
        "prefix_cache_hit_rate",
        "cache_privacy_boundary",
        "batching_mode",
        "hardware_lane",
        "quantization_policy",
        "cost_per_1k_tokens",
        "fallback_reason",
        "eval_trace_hardware_refs",
    ]


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/runtime-scorecards"},
        "record": {"method": "POST", "endpoint": "/ops/brain/runtime-scorecards/records"},
        "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/runtime-scorecards"},
        "cache_ledger": {"method": "GET", "endpoint": "/ops/brain/cache-ledger"},
        "inference_architecture": {"method": "GET", "endpoint": "/ops/brain/inference-architecture"},
    }

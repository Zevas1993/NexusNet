from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow
from nexusnet.policy import PolicyKernel


KVCachePolicy = Literal[
    "none",
    "fp16",
    "bf16",
    "fp8",
    "int8",
    "int4",
    "kivi-like",
    "kvquant-like",
    "turboquant-like",
    "lmcache",
    "eviction-only",
]
PrivacyScope = Literal["session", "project", "user", "shared", "remote-shared"]


class CacheLedgerEntryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entry_id: str
    runtime_id: str
    model_id: str
    workload_id: str
    raw_context_tokens: int
    effective_context_tokens: int
    cached_prefix_tokens: int = 0
    kv_cache_policy: KVCachePolicy = "none"
    kv_bit_width: float = 16.0
    prefix_cache_hit_rate: float = 0.0
    kv_cache_hit_rate: float = 0.0
    cache_bytes_gpu: int = 0
    cache_bytes_cpu: int = 0
    cache_bytes_disk: int = 0
    privacy_scope: PrivacyScope = "session"
    owner_ref: str = ""
    source_hashes: list[str] = Field(default_factory=list)
    recall_score: float = 0.0
    latency_ttft_ms: int = 0
    decode_tokens_per_sec: float = 0.0
    eviction_policy: str = ""
    eviction_reason: str = ""
    evidence_refs: list[str] = Field(default_factory=list)
    contains_private_data: bool = False
    redaction_verified: bool = False
    upstream_quantization_gate: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EffectiveContextCacheLedger:
    def __init__(self, *, artifacts_dir: Path | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.entries_dir = self.artifacts_dir / "runtime" / "cache-ledger" if self.artifacts_dir else None
        if self.entries_dir is not None:
            self.entries_dir.mkdir(parents=True, exist_ok=True)
        self._memory_entries: list[dict[str, Any]] = []
        self.policy_kernel = PolicyKernel.default()

    def record(self, request: CacheLedgerEntryRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, CacheLedgerEntryRequest) else CacheLedgerEntryRequest.model_validate(request)
        upstream_quantization_gate = _upstream_quantization_gate(normalized.upstream_quantization_gate)
        ledger_findings = _ledger_findings(normalized, upstream_quantization_gate=upstream_quantization_gate)
        policy_scan = self.policy_kernel.scan(_policy_targets(normalized, ledger_findings))
        hard_blocked = _has_hard_fail(ledger_findings) or policy_scan.summary.active_hard_fail_count > 0
        warning_only = any(finding.get("severity") == "warning" for finding in ledger_findings)
        promotion_blockers = _cache_promotion_blockers(ledger_findings, upstream_quantization_gate)
        entry = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "effective-context-cache-ledger",
            "entry_id": normalized.entry_id,
            "runtime_id": normalized.runtime_id,
            "model_id": normalized.model_id,
            "workload_id": normalized.workload_id,
            "status": "blocked" if hard_blocked else ("warning" if warning_only else "measured"),
            "runtime_state": "degraded" if hard_blocked else "live-bound",
            "created_at": utcnow().isoformat(),
            "context_economics": _context_economics(normalized),
            "kv_cache": _kv_cache(normalized),
            "privacy": {
                "privacy_scope": normalized.privacy_scope,
                "owner_ref": normalized.owner_ref,
                "contains_private_data": normalized.contains_private_data,
                "redaction_verified": normalized.redaction_verified,
            },
            "performance": {
                "recall_score": normalized.recall_score,
                "latency_ttft_ms": normalized.latency_ttft_ms,
                "decode_tokens_per_sec": normalized.decode_tokens_per_sec,
            },
            "eviction": {
                "policy": normalized.eviction_policy,
                "reason": normalized.eviction_reason,
            },
            "source_hashes": normalized.source_hashes,
            "evidence_refs": normalized.evidence_refs,
            "ledger_findings": ledger_findings,
            "policy_scan": policy_scan.model_dump(mode="json"),
            "upstream_quantization_gate": upstream_quantization_gate,
            "promotion_allowed": not hard_blocked,
            "promotion_blockers": promotion_blockers,
            "required_controls": _required_controls(),
            "promotion_boundary": "effective-context-claims-require-recall-cache-hit-privacy-and-eviction-evidence",
            "operator_actions": _operator_actions(),
            "metadata": normalized.metadata,
        }
        self._persist(entry)
        return entry

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        entries = self._list_entries(limit=limit)
        measured = [entry for entry in entries if entry.get("status") in {"measured", "warning"}]
        latest = entries[0] if entries else None
        runtime_state = "static-canon"
        if latest:
            runtime_state = "degraded" if latest.get("status") == "blocked" else "live-bound"
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "effective-context-cache-ledger",
            "authority": "NexusBrain",
            "runtime_state": runtime_state,
            "entry_count": len(entries),
            "measured_count": len(measured),
            "warning_count": sum(1 for entry in entries if entry.get("status") == "warning"),
            "blocked_count": sum(1 for entry in entries if entry.get("status") == "blocked"),
            "average_effective_context_ratio": _average(
                entry.get("context_economics", {}).get("effective_context_ratio", 0.0) for entry in measured
            ),
            "average_kv_cache_hit_rate": _average(entry.get("kv_cache", {}).get("kv_cache_hit_rate", 0.0) for entry in measured),
            "latest_entry": latest,
            "entries": entries,
            "required_controls": _required_controls(),
            "operator_actions": _operator_actions(),
            "runtime_truth_boundary": "advertised-context-is-not-effective-context-without-measurement",
        }

    def scorecard(self) -> dict[str, Any]:
        summary = self.summary()
        return {
            **summary,
            "source_documents": [
                "docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md",
                "docs/NEXUSNET_QUANTIZATION_AGENTIC_RESEARCH_EXPANSION_2026-04-28.md",
                "docs/NEXUSNET_OPEN_FIRST_RESEARCH_EXPANSION_2026-04-28.md",
            ],
            "watch_items": ["TurboQuant", "KIVI", "KVQuant", "LMCache", "prefix-cache", "disaggregated-prefill-decode"],
            "control_panel_label": "Effective Context and KV Cache",
        }

    def _persist(self, entry: dict[str, Any]) -> None:
        self._memory_entries.insert(0, entry)
        self._memory_entries = self._memory_entries[:50]
        if self.entries_dir is not None:
            safe_id = entry["entry_id"].replace(":", "_").replace("/", "_")
            path = self.entries_dir / f"{safe_id}.json"
            entry["artifact_path"] = str(path)
            path.write_text(json.dumps(entry, indent=2), encoding="utf-8")

    def _list_entries(self, *, limit: int) -> list[dict[str, Any]]:
        entries = list(self._memory_entries)
        seen = {entry.get("entry_id") for entry in entries}
        if self.entries_dir is not None:
            for path in self.entries_dir.glob("*.json"):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if payload.get("entry_id") not in seen:
                    entries.append(payload)
        entries.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return entries[:limit]


def _context_economics(request: CacheLedgerEntryRequest) -> dict[str, Any]:
    raw = max(request.raw_context_tokens, 1)
    return {
        "raw_context_tokens": request.raw_context_tokens,
        "effective_context_tokens": request.effective_context_tokens,
        "cached_prefix_tokens": request.cached_prefix_tokens,
        "effective_context_ratio": round(request.effective_context_tokens / raw, 4),
        "prefix_reuse_ratio": round(request.cached_prefix_tokens / raw, 4),
    }


def _kv_cache(request: CacheLedgerEntryRequest) -> dict[str, Any]:
    return {
        "policy": request.kv_cache_policy,
        "bit_width": request.kv_bit_width,
        "prefix_cache_hit_rate": request.prefix_cache_hit_rate,
        "kv_cache_hit_rate": request.kv_cache_hit_rate,
        "cache_bytes_gpu": request.cache_bytes_gpu,
        "cache_bytes_cpu": request.cache_bytes_cpu,
        "cache_bytes_disk": request.cache_bytes_disk,
    }


def _ledger_findings(
    request: CacheLedgerEntryRequest,
    *,
    upstream_quantization_gate: dict[str, Any],
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if request.contains_private_data and request.privacy_scope in {"shared", "remote-shared"} and not request.redaction_verified:
        findings.append(
            _finding(
                "cache_ledger_private_remote_scope_requires_redaction",
                "Private context cannot use shared or remote-shared cache without redaction verification.",
            )
        )
    if not request.evidence_refs:
        findings.append(_finding("cache_ledger_requires_evidence_refs", "Effective context claims require benchmark or trace evidence references."))
    if request.effective_context_tokens > request.raw_context_tokens:
        findings.append(
            _finding(
                "cache_ledger_effective_context_cannot_exceed_raw_without_explanation",
                "Effective context cannot exceed raw context without explicit retrieval or memory-expansion explanation.",
            )
        )
    if request.raw_context_tokens >= 32768 and request.recall_score and request.recall_score < 0.75:
        findings.append(
            _finding(
                "cache_ledger_long_context_recall_warning",
                "Long-context effective context claim has weak recall evidence.",
                severity="warning",
            )
        )
    if _quantization_gate_blocked(upstream_quantization_gate):
        findings.append(
            _finding(
                "cache_ledger_blocks_quantization_gate",
                "Effective-context and KV-cache claims cannot promote while upstream quantization evidence is blocked.",
            )
        )
    return findings


def _upstream_quantization_gate(gate: dict[str, Any]) -> dict[str, Any]:
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
        "source": gate.get("source") or "quantization_catalog",
    }


def _quantization_gate_blocked(gate: dict[str, Any]) -> bool:
    return bool(gate.get("promotion_allowed") is False or gate.get("status") == "blocked" or gate.get("blockers"))


def _cache_promotion_blockers(findings: list[dict[str, str]], upstream_quantization_gate: dict[str, Any]) -> list[str]:
    blockers = [finding["rule_id"] for finding in findings if finding.get("severity") == "hard_fail"]
    blockers.extend(str(item) for item in upstream_quantization_gate.get("blockers") or [])
    if upstream_quantization_gate.get("promotion_allowed") is False:
        blockers.append("quantization_promotion_not_allowed")
    return sorted(set(blockers))


def _finding(rule_id: str, message: str, severity: str = "hard_fail") -> dict[str, str]:
    return {"rule_id": rule_id, "severity": severity, "message": message}


def _has_hard_fail(findings: list[dict[str, str]]) -> bool:
    return any(finding.get("severity") == "hard_fail" for finding in findings)


def _policy_targets(request: CacheLedgerEntryRequest, findings: list[dict[str, str]]) -> list[dict[str, Any]]:
    hard_findings = _has_hard_fail(findings)
    return [
        {
            "target_id": f"cache-ledger::{request.entry_id}",
            "target_type": "tool_execution",
            "metadata": {
                "write_enabled": hard_findings,
                "sandboxed": not hard_findings,
                "tool_scope": request.privacy_scope,
            },
        },
        {
            "target_id": f"cache-artifact::{request.entry_id}",
            "target_type": "artifact",
            "metadata": {
                "promotion_requested": True,
                "license_state": "approved",
                "provenance_refs": request.evidence_refs,
            },
        },
    ]


def _average(values: Any) -> float:
    realized = [float(value or 0.0) for value in values]
    if not realized:
        return 0.0
    return round(sum(realized) / len(realized), 4)


def _required_controls() -> list[str]:
    return [
        "raw_context_tokens",
        "effective_context_tokens",
        "recall_score",
        "prefix_cache_hit_rate",
        "kv_cache_hit_rate",
        "kv_cache_policy",
        "kv_bit_width",
        "cache_privacy_scope",
        "cache_tier_bytes",
        "eviction_policy",
        "benchmark_evidence_refs",
    ]


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/cache-ledger"},
        "record": {"method": "POST", "endpoint": "/ops/brain/cache-ledger/entries"},
        "effective_context": {"method": "GET", "endpoint": "/ops/brain/runtime/effective-context"},
        "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/cache-ledger"},
        "inference_architecture": {"method": "GET", "endpoint": "/ops/brain/inference-architecture"},
        "quantization_catalog": {"method": "GET", "endpoint": "/ops/brain/canon/quantization-catalog"},
    }

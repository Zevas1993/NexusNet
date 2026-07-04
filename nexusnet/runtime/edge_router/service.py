from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import new_id, utcnow
from nexusnet.policy import PolicyKernel


WorkloadType = Literal[
    "transcription",
    "document_processing",
    "vision",
    "code_assistance",
    "frontier_reasoning",
    "chat",
    "embedding",
]
DataSensitivity = Literal["public", "internal", "private", "regulated"]
QualityPriority = Literal["cost", "latency", "balanced", "maximum"]


class EdgeWorkloadRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workload_id: str
    workload_type: WorkloadType
    input_modalities: list[str] = Field(default_factory=list)
    data_sensitivity: DataSensitivity = "internal"
    offline_required: bool = False
    latency_target_ms: int | None = None
    quality_priority: QualityPriority = "balanced"
    estimated_tokens: int | None = None
    hardware_snapshot: dict[str, Any] = Field(default_factory=dict)
    upstream_aitune_gate: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EdgeWorkloadRouter:
    def __init__(self, *, artifacts_dir: Path | None = None):
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.decisions_dir = self.artifacts_dir / "runtime" / "edge-workload-router" if self.artifacts_dir else None
        if self.decisions_dir is not None:
            self.decisions_dir.mkdir(parents=True, exist_ok=True)
        self._memory_decisions: list[dict[str, Any]] = []
        self.policy_kernel = PolicyKernel.default()

    def route(self, request: EdgeWorkloadRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, EdgeWorkloadRequest) else EdgeWorkloadRequest.model_validate(request)
        candidates = [_score_lane(lane, normalized) for lane in _lane_catalog()]
        eligible = [candidate for candidate in candidates if candidate["eligible"]]
        eligible.sort(key=lambda item: item["score"], reverse=True)
        selected = eligible[0] if eligible else next(candidate for candidate in candidates if candidate["lane_id"] == "local-cpu")
        reason_codes = _reason_codes(normalized, selected)
        upstream_aitune_gate = _upstream_aitune_gate(normalized.upstream_aitune_gate)
        route_blockers: list[str] = []
        if _upstream_aitune_gate_blocked(upstream_aitune_gate):
            reason_codes = list(dict.fromkeys(reason_codes + ["upstream_aitune_gate_blocked"]))
            route_blockers.append("router_alignment_blocks_upstream_aitune_gate")
        policy_scan = self.policy_kernel.scan(_policy_targets_for(selected))
        created_at = utcnow().isoformat()
        decision = {
            "status_label": "LOCKED CANON",
            "decision_id": new_id("edge_route"),
            "workload_id": normalized.workload_id,
            "authority": "NexusBrain",
            "created_at": created_at,
            "status": "blocked-upstream-gate" if route_blockers else "routed-shadow",
            "runtime_state": "degraded" if route_blockers else "live-bound",
            "selected_lane_id": selected["lane_id"],
            "selected_lane": selected,
            "reason_codes": reason_codes,
            "route_blockers": route_blockers,
            "upstream_aitune_gate": upstream_aitune_gate,
            "candidates": candidates,
            "policy_scan": policy_scan.model_dump(mode="json"),
            "explainability": {
                "privacy": normalized.data_sensitivity,
                "offline_required": normalized.offline_required,
                "quality_priority": normalized.quality_priority,
                "latency_target_ms": normalized.latency_target_ms,
                "hardware_snapshot": normalized.hardware_snapshot,
                "rule": "route private/offline/high-volume work local when hardware fits; use cloud only when sensitivity and offline gates permit.",
            },
            "operator_actions": _operator_actions(),
        }
        self._persist(decision)
        return decision

    def summary(self, *, limit: int = 20) -> dict[str, Any]:
        decisions = self._list_decisions(limit=limit)
        latest = decisions[0] if decisions else None
        runtime_state = "static-canon"
        if latest:
            runtime_state = "degraded" if latest.get("runtime_state") == "degraded" else "live-bound"
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "edge-workload-router",
            "authority": "NexusBrain",
            "runtime_state": runtime_state,
            "decision_count": len(decisions),
            "blocked_count": sum(1 for decision in decisions if str(decision.get("status", "")).startswith("blocked")),
            "latest_decision": latest,
            "recent_decisions": decisions,
            "lane_catalog": _lane_catalog(),
            "required_controls": _required_controls(),
            "operator_actions": _operator_actions(),
        }

    def scorecard(self) -> dict[str, Any]:
        summary = self.summary()
        return {
            **summary,
            "source_document": "docs/NEXUSNET_YOUTUBE_ASSIMILATION_INTAKE_2026-04-30.md",
            "research_source_ids": ["YT-06"],
            "routing_rule": "hybrid-local-first-routing-with-cloud-only-when-policy-fit-allows",
            "promotion_boundary": "routes-require-workload-classification-hardware-snapshot-cost-privacy-latency-score-and-policy-scan",
        }

    def _persist(self, decision: dict[str, Any]) -> None:
        self._memory_decisions.insert(0, decision)
        self._memory_decisions = self._memory_decisions[:20]
        if self.decisions_dir is not None:
            path = self.decisions_dir / f"{decision['decision_id']}.json"
            path.write_text(json.dumps(decision, indent=2), encoding="utf-8")
            decision["artifact_path"] = str(path)
            path.write_text(json.dumps(decision, indent=2), encoding="utf-8")

    def _list_decisions(self, *, limit: int) -> list[dict[str, Any]]:
        decisions = list(self._memory_decisions)
        if self.decisions_dir is not None:
            for path in self.decisions_dir.glob("*.json"):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if payload.get("decision_id") not in {item.get("decision_id") for item in decisions}:
                    decisions.append(payload)
        decisions.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return decisions[:limit]


def _lane_catalog() -> list[dict[str, Any]]:
    return [
        {
            "lane_id": "local-gpu",
            "label": "Local GPU",
            "privacy_posture": "local-private",
            "cost_posture": "owned-hardware",
            "latency_posture": "low",
            "quality_posture": "specialized-local",
            "hardware_key": "local_gpu",
            "best_for": ["transcription", "vision", "document_processing", "code_assistance", "embedding"],
        },
        {
            "lane_id": "browser-webgpu-webnn",
            "label": "Browser WebGPU/WebNN",
            "privacy_posture": "device-private",
            "cost_posture": "owned-device",
            "latency_posture": "low",
            "quality_posture": "edge-specialist",
            "hardware_key": "browser_webgpu",
            "best_for": ["vision", "embedding", "document_processing"],
        },
        {
            "lane_id": "android-npu",
            "label": "Android / Mobile NPU",
            "privacy_posture": "device-private",
            "cost_posture": "owned-device",
            "latency_posture": "very-low",
            "quality_posture": "edge-specialist",
            "hardware_key": "android_npu",
            "best_for": ["vision", "transcription", "embedding"],
        },
        {
            "lane_id": "wsl-gpu",
            "label": "WSL GPU",
            "privacy_posture": "local-private",
            "cost_posture": "owned-hardware",
            "latency_posture": "medium",
            "quality_posture": "specialized-local",
            "hardware_key": "wsl_gpu",
            "best_for": ["code_assistance", "document_processing", "transcription"],
        },
        {
            "lane_id": "local-cpu",
            "label": "Local CPU",
            "privacy_posture": "local-private",
            "cost_posture": "owned-hardware",
            "latency_posture": "medium-high",
            "quality_posture": "small-local",
            "hardware_key": "local_cpu",
            "best_for": ["transcription", "document_processing", "embedding"],
        },
        {
            "lane_id": "cloud-api",
            "label": "Cloud / API Frontier",
            "privacy_posture": "external-provider",
            "cost_posture": "metered",
            "latency_posture": "network-dependent",
            "quality_posture": "frontier",
            "hardware_key": None,
            "best_for": ["frontier_reasoning", "chat", "code_assistance"],
        },
    ]


def _score_lane(lane: dict[str, Any], request: EdgeWorkloadRequest) -> dict[str, Any]:
    candidate = dict(lane)
    hardware = request.hardware_snapshot or {}
    blockers: list[str] = []
    if lane["hardware_key"] and not hardware.get(lane["hardware_key"], False):
        blockers.append("hardware-unavailable")
    if lane["lane_id"] == "cloud-api" and request.offline_required:
        blockers.append("offline-required")
    if lane["lane_id"] == "cloud-api" and request.data_sensitivity in {"private", "regulated"}:
        blockers.append(f"{request.data_sensitivity}-data")
    score = 0
    if request.workload_type in lane["best_for"]:
        score += 12
    if request.data_sensitivity in {"private", "regulated"} and lane["privacy_posture"] in {"local-private", "device-private"}:
        score += 10
    if request.offline_required and lane["privacy_posture"] in {"local-private", "device-private"}:
        score += 8
    if request.quality_priority == "maximum" and lane["quality_posture"] == "frontier":
        score += 14
    if request.quality_priority == "latency" and lane["latency_posture"] in {"very-low", "low"}:
        score += 8
    if request.quality_priority == "cost" and lane["cost_posture"] != "metered":
        score += 7
    if lane["lane_id"] == "local-gpu" and float(hardware.get("local_gpu_vram_gb") or 0) >= 12:
        score += 5
    if lane["lane_id"] == "cloud-api" and request.data_sensitivity == "public" and not request.offline_required:
        score += 4
    if blockers:
        score -= 100
    candidate.update(
        {
            "eligible": not blockers,
            "blockers": blockers,
            "score": score,
            "estimated_latency_ms": _latency_estimate(lane, request),
        }
    )
    return candidate


def _latency_estimate(lane: dict[str, Any], request: EdgeWorkloadRequest) -> int:
    base = {
        "android-npu": 120,
        "browser-webgpu-webnn": 180,
        "local-gpu": 220,
        "wsl-gpu": 320,
        "local-cpu": 780,
        "cloud-api": 900,
    }.get(lane["lane_id"], 1000)
    if request.estimated_tokens:
        base += min(int(request.estimated_tokens / 100), 1200)
    return base


def _reason_codes(request: EdgeWorkloadRequest, selected: dict[str, Any]) -> list[str]:
    reasons: list[str] = [f"workload::{request.workload_type}", f"selected::{selected['lane_id']}"]
    if request.data_sensitivity in {"private", "regulated"}:
        reasons.append("privacy_sensitive" if request.data_sensitivity == "private" else "regulated_data")
    if request.offline_required:
        reasons.append("offline_required")
    if request.quality_priority == "maximum" and selected["quality_posture"] == "frontier":
        reasons.append("frontier_quality")
    if selected["cost_posture"] != "metered":
        reasons.append("cost_contained")
    return reasons


def _policy_targets_for(selected: dict[str, Any]) -> list[dict[str, Any]]:
    if selected["lane_id"] == "cloud-api":
        return [
            {
                "target_id": "edge-route::cloud-api",
                "target_type": "protocol_adapter",
                "metadata": {
                    "enabled": True,
                    "trust_envelope": {
                        "authority": "NexusBrain",
                        "provider": "cloud-api",
                        "route_boundary": "privacy-and-offline-gated",
                    },
                },
            }
        ]
    return [
        {
            "target_id": f"edge-route::{selected['lane_id']}",
            "target_type": "tool_execution",
            "metadata": {"write_enabled": False, "sandboxed": True},
        }
    ]


def _upstream_aitune_gate(gate: dict[str, Any]) -> dict[str, Any]:
    blockers = list(gate.get("blockers") or gate.get("readiness_blockers") or [])
    status = str(gate.get("status") or "not_provided")
    can_execute_here = gate.get("can_execute_here")
    if can_execute_here is False and not blockers:
        blockers.append("upstream_aitune_execution_not_ready")
    if status in {"blocked", "blocked-upstream-gate"} and not blockers:
        blockers.append("upstream_aitune_gate_blocked")
    return {
        **gate,
        "status": status,
        "can_execute_here": can_execute_here,
        "blockers": blockers,
    }


def _upstream_aitune_gate_blocked(gate: dict[str, Any]) -> bool:
    return bool(
        gate.get("can_execute_here") is False
        or gate.get("status") in {"blocked", "blocked-upstream-gate"}
        or gate.get("blockers")
    )


def _required_controls() -> list[str]:
    return [
        "workload_classification",
        "hardware_capability_snapshot",
        "privacy_scoring",
        "cost_latency_quality_scoring",
        "local_vs_cloud_explainability",
        "policy_scan",
        "route_regression_tests",
    ]


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/edge-workload-router"},
        "route": {"method": "POST", "endpoint": "/ops/brain/edge-workload-router/route"},
        "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/edge-workload-router"},
    }

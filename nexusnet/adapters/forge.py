from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow
from nexusnet.policy import PolicyKernel


AdapterStatus = Literal["candidate", "training", "evaluating", "shadow", "active", "rejected", "rolled_back", "blocked"]


class BaseModelRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model_id: str
    revision: str
    license: str
    source_url: str = ""


class AdapterMethod(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["lora", "qlora", "full", "dpo", "grpo"]
    framework: Literal["peft", "trl", "axolotl", "unsloth", "mlx-lm", "other"]
    precision: str
    target_modules: list[str] = Field(default_factory=list)


class DatasetManifestRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_manifest_id: str
    source_count: int = 0
    example_count: int = 0
    token_count: int = 0
    contains_private_data: bool = False
    license_status: Literal["approved", "blocked", "needs_review"] = "needs_review"
    provenance_refs: list[str] = Field(default_factory=list)


class AdapterEval(BaseModel):
    model_config = ConfigDict(extra="forbid")

    base_score: float = 0.0
    adapter_score: float = 0.0
    regression_failures: list[str] = Field(default_factory=list)
    style_gain: float = 0.0
    grounding_delta: float = 0.0
    tool_call_delta: float = 0.0


class AdapterDeployment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    adapter_artifact: str = ""
    merged_artifact: str = ""
    gguf_artifact: str = ""
    runtime_targets: list[str] = Field(default_factory=list)
    rollback_adapter_id: str = ""


class AdapterRecordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    adapter_id: str
    target_slot: str
    base_model: BaseModelRef
    method: AdapterMethod
    dataset: DatasetManifestRef
    eval: AdapterEval = Field(default_factory=AdapterEval)
    deployment: AdapterDeployment = Field(default_factory=AdapterDeployment)
    operator_approved: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class AdapterForgeRegistry:
    def __init__(self, *, artifacts_dir: Path | None = None):
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.records_dir = self.artifacts_dir / "adapters" / "forge-registry" if self.artifacts_dir else None
        if self.records_dir is not None:
            self.records_dir.mkdir(parents=True, exist_ok=True)
        self._memory_records: list[dict[str, Any]] = []
        self.policy_kernel = PolicyKernel.default()

    def register(self, request: AdapterRecordRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, AdapterRecordRequest) else AdapterRecordRequest.model_validate(request)
        policy_scan = self.policy_kernel.scan(_policy_targets(normalized))
        blocked = policy_scan.summary.active_hard_fail_count > 0
        promotion_state = _promotion_state(normalized, blocked=blocked)
        status: AdapterStatus = "blocked" if blocked else ("shadow" if promotion_state == "eval-passed-shadow" else "candidate")
        created_at = utcnow().isoformat()
        record = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "adapter_id": normalized.adapter_id,
            "target_slot": normalized.target_slot,
            "status": status,
            "promotion_state": promotion_state,
            "created_at": created_at,
            "base_model": normalized.base_model.model_dump(mode="json"),
            "method": normalized.method.model_dump(mode="json"),
            "dataset": normalized.dataset.model_dump(mode="json"),
            "eval": normalized.eval.model_dump(mode="json"),
            "deployment": normalized.deployment.model_dump(mode="json"),
            "operator_approved": normalized.operator_approved,
            "policy_scan": policy_scan.model_dump(mode="json"),
            "metadata": normalized.metadata,
        }
        self._persist(record)
        return record

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        records = self._list_records(limit=limit)
        blocked_count = sum(1 for record in records if record.get("status") == "blocked")
        latest_adapter = records[0] if records else None
        runtime_state = "static-canon"
        if records:
            runtime_state = "degraded" if blocked_count or latest_adapter.get("status") == "blocked" else "live-bound"
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "adapter-registry",
            "authority": "NexusBrain",
            "runtime_state": runtime_state,
            "adapter_count": len(records),
            "shadow_count": sum(1 for record in records if record.get("status") == "shadow"),
            "blocked_count": blocked_count,
            "latest_adapter": latest_adapter,
            "adapters": records,
            "required_controls": _required_controls(),
            "operator_actions": _operator_actions(),
        }

    def scorecard(self) -> dict[str, Any]:
        summary = self.summary()
        return {
            **summary,
            "source_document": "docs/NEXUSNET_YOUTUBE_ASSIMILATION_INTAKE_2026-04-30.md",
            "research_source_ids": ["YT-07"],
            "promotion_boundary": "no-adapter-activation-without-provenance-license-privacy-eval-regression-and-rollback",
            "training_boundary": "registry-only-no-training-or-weight-update",
        }

    def _persist(self, record: dict[str, Any]) -> None:
        self._memory_records.insert(0, record)
        self._memory_records = self._memory_records[:50]
        if self.records_dir is not None:
            safe_id = record["adapter_id"].replace(":", "_").replace("/", "_")
            path = self.records_dir / f"{safe_id}.json"
            record["artifact_path"] = str(path)
            path.write_text(json.dumps(record, indent=2), encoding="utf-8")

    def _list_records(self, *, limit: int) -> list[dict[str, Any]]:
        records = list(self._memory_records)
        seen = {record.get("adapter_id") for record in records}
        if self.records_dir is not None:
            for path in self.records_dir.glob("*.json"):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if payload.get("adapter_id") not in seen:
                    records.append(payload)
        records.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return records[:limit]


def _policy_targets(request: AdapterRecordRequest) -> list[dict[str, Any]]:
    eval_refs = ["adapter-eval-delta"] if request.eval.adapter_score or request.eval.base_score else []
    return [
        {
            "target_id": f"training::{request.adapter_id}",
            "target_type": "training_candidate",
            "metadata": {
                "contains_private_data": request.dataset.contains_private_data,
                "uses_user_data": request.dataset.source_count > 0,
                "operator_approved": request.operator_approved,
                "promotion_requested": True,
                "eval_refs": eval_refs,
            },
        },
        {
            "target_id": f"artifact::{request.adapter_id}",
            "target_type": "artifact",
            "metadata": {
                "promotion_requested": True,
                "license_state": "approved" if request.dataset.license_status == "approved" else None,
                "provenance_refs": request.dataset.provenance_refs,
            },
        },
        {
            "target_id": f"autonomous-update::{request.adapter_id}",
            "target_type": "autonomous_update",
            "metadata": {
                "promotion_requested": False,
                "rollback_plan": request.deployment.rollback_adapter_id,
                "monitoring_plan": "shadow-eval-before-activation",
            },
        },
    ]


def _promotion_state(request: AdapterRecordRequest, *, blocked: bool) -> str:
    if blocked:
        return "blocked-by-policy"
    if request.eval.regression_failures:
        return "eval-regression-blocked"
    if request.eval.adapter_score > request.eval.base_score:
        return "eval-passed-shadow"
    return "candidate-needs-eval"


def _required_controls() -> list[str]:
    return [
        "adapter_metadata_schema",
        "dataset_manifest_schema",
        "base_model_compatibility",
        "license_privacy_provenance",
        "eval_delta",
        "deployment_targets",
        "rollback_adapter",
        "policy_scan",
    ]


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/adapter-registry"},
        "register_candidate": {"method": "POST", "endpoint": "/ops/brain/adapter-registry/candidates"},
        "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/adapter-registry"},
    }

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow
from nexusnet.policy import PolicyKernel


TrainingMethod = Literal["lora", "qlora", "full", "dpo", "grpo"]
TrainingFramework = Literal["peft", "trl", "axolotl", "unsloth", "mlx-lm", "other"]
LicenseStatus = Literal["approved", "blocked", "needs_review"]
ExportTarget = Literal["adapter", "merged", "gguf"]
DatasetManifestStatus = Literal["ready", "needs_review", "blocked", "unknown"]


class AdapterTrainingPlanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan_id: str
    adapter_id: str
    dataset_manifest_id: str
    dataset_manifest_status: DatasetManifestStatus = "unknown"
    dataset_radar_training_review_gate: dict[str, Any] = Field(default_factory=dict)
    fine_tune_decision_status: str = "unknown"
    fine_tune_adapter_training_allowed: bool | None = None
    base_model_id: str
    model_size_billion: float
    method: TrainingMethod
    framework: TrainingFramework
    raw_token_count: int = 0
    transformed_example_count: int = 0
    contains_private_data: bool = False
    license_status: LicenseStatus = "needs_review"
    operator_approved: bool = False
    target_hardware: dict[str, Any] = Field(default_factory=dict)
    export_targets: list[ExportTarget] = Field(default_factory=list)
    eval_refs: list[str] = Field(default_factory=list)
    provenance_refs: list[str] = Field(default_factory=list)
    rollback_adapter_id: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class AdapterTrainingPlanner:
    def __init__(self, *, artifacts_dir: Path | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.plans_dir = self.artifacts_dir / "adapters" / "training-planner" if self.artifacts_dir else None
        if self.plans_dir is not None:
            self.plans_dir.mkdir(parents=True, exist_ok=True)
        self._memory_plans: list[dict[str, Any]] = []
        self.policy_kernel = PolicyKernel.default()

    def plan(self, request: AdapterTrainingPlanRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, AdapterTrainingPlanRequest) else AdapterTrainingPlanRequest.model_validate(request)
        hardware_posture = _hardware_posture(normalized)
        training_findings = _training_findings(normalized, hardware_posture)
        policy_scan = self.policy_kernel.scan(_policy_targets(normalized))
        blocked = _has_hard_fail(training_findings) or policy_scan.summary.active_hard_fail_count > 0
        plan = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "adapter-training",
            "plan_id": normalized.plan_id,
            "adapter_id": normalized.adapter_id,
            "dataset_manifest_id": normalized.dataset_manifest_id,
            "dataset_manifest_status": normalized.dataset_manifest_status,
            "dataset_radar_training_review_gate": normalized.dataset_radar_training_review_gate,
            "fine_tune_decision_status": normalized.fine_tune_decision_status,
            "fine_tune_adapter_training_allowed": normalized.fine_tune_adapter_training_allowed,
            "base_model_id": normalized.base_model_id,
            "status": "blocked" if blocked else "planned-shadow",
            "runtime_state": "degraded" if blocked else "live-bound",
            "created_at": utcnow().isoformat(),
            "method": normalized.method,
            "framework": normalized.framework,
            "model_size_billion": normalized.model_size_billion,
            "raw_token_count": normalized.raw_token_count,
            "transformed_example_count": normalized.transformed_example_count,
            "contains_private_data": normalized.contains_private_data,
            "license_status": normalized.license_status,
            "operator_approved": normalized.operator_approved,
            "target_hardware": normalized.target_hardware,
            "hardware_posture": hardware_posture,
            "export_targets": normalized.export_targets,
            "eval_refs": normalized.eval_refs,
            "provenance_refs": normalized.provenance_refs,
            "rollback_adapter_id": normalized.rollback_adapter_id,
            "stages": _stages(normalized),
            "training_findings": training_findings,
            "policy_scan": policy_scan.model_dump(mode="json"),
            "required_controls": _required_controls(),
            "training_boundary": "plan-only-no-weight-update-without-operator-run-command",
            "promotion_boundary": "adapter-training-requires-dataset-engineering-hardware-fit-eval-delta-gguf-export-proof-and-rollback",
            "operator_actions": _operator_actions(),
            "metadata": normalized.metadata,
        }
        self._persist(plan)
        return plan

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        plans = self._list_plans(limit=limit)
        blocked_count = sum(1 for plan in plans if plan.get("status") == "blocked")
        latest_plan = plans[0] if plans else None
        runtime_state = "static-canon"
        if plans:
            runtime_state = "degraded" if blocked_count or latest_plan.get("status") == "blocked" else "live-bound"
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "adapter-training",
            "authority": "NexusBrain",
            "runtime_state": runtime_state,
            "plan_count": len(plans),
            "shadow_count": sum(1 for plan in plans if plan.get("status") == "planned-shadow"),
            "blocked_count": blocked_count,
            "latest_plan": latest_plan,
            "plans": plans,
            "canonical_stages": _canonical_stages(),
            "required_controls": _required_controls(),
            "operator_actions": _operator_actions(),
        }

    def scorecard(self) -> dict[str, Any]:
        summary = self.summary()
        return {
            **summary,
            "source_documents": [
                "youtube-transcript::v7qMjy_RxOs",
                "docs/NEXUSNET_YOUTUBE_ASSIMILATION_INTAKE_2026-04-30.md",
                "docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md",
            ],
            "assimilation_pattern": "fine-tuning-as-governed-plan-data-collection-dataset-engineering-lora-eval-gguf-export",
            "training_boundary": "plan-only-no-weight-update-without-operator-run-command",
            "hardware_rule": "prefer-nvidia-cuda-for-training-amd-rocm-experimental-apple-mlx-limited-local-inference-first",
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


def _hardware_posture(request: AdapterTrainingPlanRequest) -> dict[str, Any]:
    hardware = request.target_hardware or {}
    vendor = str(hardware.get("vendor") or "unknown").lower()
    vram_gb = float(hardware.get("vram_gb") or 0)
    required_vram = _required_vram_gb(request)
    state = "hardware-insufficient"
    notes: list[str] = []
    if vendor == "nvidia" and hardware.get("cuda_available") and vram_gb >= required_vram:
        state = "nvidia-cuda-ready"
        notes.append("CUDA lane has first-class training compatibility for PEFT/TRL style workflows.")
    elif vendor == "amd" and hardware.get("rocm_available") and vram_gb >= required_vram:
        state = "amd-rocm-experimental"
        notes.append("ROCm can be attempted but remains compatibility-sensitive for training.")
    elif vendor == "apple" and hardware.get("mlx_available") and request.method in {"lora", "qlora"} and vram_gb >= required_vram:
        state = "apple-mlx-limited"
        notes.append("MLX lane is limited and should be treated as experimental for training.")
    else:
        notes.append("Target hardware does not satisfy the conservative local training fit rule.")
    return {
        "state": state,
        "vendor": vendor,
        "vram_gb": vram_gb,
        "required_vram_gb": required_vram,
        "notes": notes,
    }


def _required_vram_gb(request: AdapterTrainingPlanRequest) -> float:
    if request.method == "qlora":
        return max(8.0, round(request.model_size_billion * 0.5, 1))
    if request.method in {"lora", "dpo", "grpo"}:
        return max(10.0, round(request.model_size_billion * 0.75, 1))
    return max(24.0, round(request.model_size_billion * 2.0, 1))


def _training_findings(
    request: AdapterTrainingPlanRequest,
    hardware_posture: dict[str, Any],
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if request.contains_private_data and not request.operator_approved:
        findings.append(_finding("adapter_training_private_data_requires_operator_approval", "Private training data requires explicit operator approval."))
    if request.license_status != "approved":
        findings.append(_finding("adapter_training_requires_approved_license", "Adapter training requires approved dataset and base-model license status."))
    if not request.eval_refs:
        findings.append(_finding("adapter_training_requires_eval_refs", "Fine-tune plans require held-out eval references before shadow promotion."))
    if not request.provenance_refs:
        findings.append(_finding("adapter_training_requires_provenance_refs", "Fine-tune plans require dataset and source provenance references."))
    if request.raw_token_count < 500_000 or request.transformed_example_count < 1_000:
        findings.append(_finding("adapter_training_requires_more_dataset_examples", "Training plans need enough cleaned prompt-response examples before a run is useful."))
    if request.method == "full":
        findings.append(_finding("adapter_training_full_finetune_blocked_for_mvp", "Full fine-tuning remains blocked; use LoRA/QLoRA/DPO/GRPO candidates first."))
    if hardware_posture["state"] == "hardware-insufficient":
        findings.append(_finding("adapter_training_hardware_insufficient", "Target hardware is not sufficient for the requested local training plan."))
    if not request.rollback_adapter_id:
        findings.append(_finding("adapter_training_requires_rollback_adapter", "Adapter training plans require rollback adapter or previous behavior reference."))
    if request.dataset_manifest_status in {"needs_review", "blocked"}:
        findings.append(
            _finding(
                "adapter_training_requires_ready_dataset_manifest",
                "Adapter training plans require a DatasetForge manifest whose status is ready.",
            )
        )
    training_review_gate = request.dataset_radar_training_review_gate or {}
    if training_review_gate and not training_review_gate.get("allowed"):
        findings.append(
            _finding(
                "adapter_training_dataset_radar_training_review_blocked",
                "Dataset Radar training-review blockers must be cleared before adapter planning.",
            )
        )
    if request.fine_tune_decision_status == "blocked" or request.fine_tune_adapter_training_allowed is False:
        findings.append(
            _finding(
                "adapter_training_requires_fine_tune_decision_allowance",
                "Adapter training plans require an upstream fine-tune decision that allows adapter training.",
            )
        )
    return findings


def _finding(rule_id: str, message: str, severity: str = "hard_fail") -> dict[str, str]:
    return {"rule_id": rule_id, "severity": severity, "message": message}


def _has_hard_fail(findings: list[dict[str, str]]) -> bool:
    return any(finding.get("severity") == "hard_fail" for finding in findings)


def _policy_targets(request: AdapterTrainingPlanRequest) -> list[dict[str, Any]]:
    return [
        {
            "target_id": f"training::{request.plan_id}",
            "target_type": "training_candidate",
            "metadata": {
                "contains_private_data": request.contains_private_data,
                "uses_user_data": request.raw_token_count > 0,
                "operator_approved": request.operator_approved,
                "promotion_requested": True,
                "eval_refs": request.eval_refs,
            },
        },
        {
            "target_id": f"artifact::{request.plan_id}",
            "target_type": "artifact",
            "metadata": {
                "promotion_requested": True,
                "license_state": "approved" if request.license_status == "approved" else None,
                "provenance_refs": request.provenance_refs,
                "dataset_manifest_status": request.dataset_manifest_status,
                "dataset_radar_training_review_allowed": (request.dataset_radar_training_review_gate or {}).get("allowed"),
            },
        },
        {
            "target_id": f"autonomous-update::{request.plan_id}",
            "target_type": "autonomous_update",
            "metadata": {
                "promotion_requested": False,
                "rollback_plan": request.rollback_adapter_id,
                "monitoring_plan": "shadow-eval-before-activation",
            },
        },
    ]


def _stages(request: AdapterTrainingPlanRequest) -> list[dict[str, Any]]:
    stages = [dict(stage) for stage in _canonical_stages()]
    if "gguf" not in request.export_targets:
        stages = [stage for stage in stages if stage["stage_id"] != "gguf-export"]
    for stage in stages:
        if stage["stage_id"] == "data-collection":
            stage["evidence"] = [request.dataset_manifest_id, *request.provenance_refs]
        if stage["stage_id"] == "dataset-engineering":
            stage["evidence"] = [f"tokens::{request.raw_token_count}", f"examples::{request.transformed_example_count}"]
        if stage["stage_id"] == "lora-training":
            stage["evidence"] = [request.method, request.framework, request.base_model_id]
        if stage["stage_id"] == "evaluation":
            stage["evidence"] = list(request.eval_refs)
        if stage["stage_id"] == "gguf-export":
            stage["evidence"] = ["gguf" if "gguf" in request.export_targets else "not-requested"]
    return stages


def _canonical_stages() -> list[dict[str, str]]:
    return [
        {"stage_id": "data-collection", "label": "Collect transcripts, traces, docs, examples, and provenance.", "state": "required"},
        {"stage_id": "dataset-engineering", "label": "Clean data and transform it into chat-format prompt/response pairs.", "state": "required"},
        {"stage_id": "lora-training", "label": "Plan LoRA/QLoRA training parameters without executing weights by default.", "state": "shadow-only"},
        {"stage_id": "evaluation", "label": "Compare base vs adapter on held-out tasks and regression gates.", "state": "required"},
        {"stage_id": "gguf-export", "label": "Export local-runtime GGUF only after eval and artifact trust checks.", "state": "optional"},
    ]


def _required_controls() -> list[str]:
    return [
        "dataset_manifest",
        "prompt_response_pairs",
        "license_privacy_gate",
        "dataset_manifest_ready_gate",
        "dataset_radar_training_review_gate",
        "fine_tune_decision_allowance",
        "hardware_vram_fit",
        "lora_qlora_config",
        "eval_before_after",
        "gguf_export",
        "rollback_adapter",
        "artifact_trust",
    ]


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/adapter-training"},
        "plan": {"method": "POST", "endpoint": "/ops/brain/adapter-training/plans"},
        "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/adapter-training"},
        "adapter_registry": {"method": "GET", "endpoint": "/ops/brain/adapter-registry"},
        "dataset_forge": {"method": "GET", "endpoint": "/ops/brain/dataset-forge"},
    }

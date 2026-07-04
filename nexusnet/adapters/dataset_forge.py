from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow
from nexusnet.curriculum.dataset_radar import DatasetRadar
from nexusnet.policy import PolicyKernel


LicenseStatus = Literal["approved", "blocked", "needs_review"]
DatasetStatus = Literal["ready", "blocked", "needs_review"]


class DatasetSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str
    source_type: Literal["document", "transcript", "trace", "chat", "file", "web", "tool_output", "other"]
    text: str
    license_status: LicenseStatus = "needs_review"
    contains_private_data: bool = False
    provenance_ref: str = ""
    dataset_radar_source_id: str | None = None
    generator_model: str | None = None
    source_license_ref: str | None = None
    allowed_distillation_state: Literal["approved", "blocked", "unknown", "not_applicable"] = "not_applicable"
    contamination_risk: Literal["low", "medium", "high", "unknown"] = "unknown"
    metadata: dict[str, Any] = Field(default_factory=dict)


class DatasetForgeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_manifest_id: str
    purpose: str
    sources: list[DatasetSource]
    knowledge_artifact_refs: list[str] = Field(default_factory=list)
    knowledge_artifact_runtime_contexts: list[dict[str, Any]] = Field(default_factory=list)
    material_request_ref: str | None = None
    task_type: Literal["summarization", "style", "routing", "tool_use", "reasoning", "multimodal"] = "summarization"
    operator_approved: bool = False
    split_ratios: dict[str, float] = Field(default_factory=lambda: {"train": 0.8, "validation": 0.1, "test": 0.1})
    metadata: dict[str, Any] = Field(default_factory=dict)


class DatasetForge:
    def __init__(self, *, artifacts_dir: Path | None = None, dataset_radar: DatasetRadar | None = None):
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.manifests_dir = self.artifacts_dir / "adapters" / "dataset-forge" if self.artifacts_dir else None
        if self.manifests_dir is not None:
            self.manifests_dir.mkdir(parents=True, exist_ok=True)
        self._memory_manifests: list[dict[str, Any]] = []
        self.policy_kernel = PolicyKernel.default()
        self.dataset_radar = dataset_radar or DatasetRadar(artifacts_dir=artifacts_dir)

    def build(self, request: DatasetForgeRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, DatasetForgeRequest) else DatasetForgeRequest.model_validate(request)
        examples = [_example_from_source(normalized, source, index) for index, source in enumerate(normalized.sources)]
        eval_cases = [_eval_case_from_example(example) for example in examples]
        dataset = _dataset_summary(normalized, examples)
        material_request = (
            self.dataset_radar.material_request_record(normalized.material_request_ref)
            if normalized.material_request_ref
            else None
        )
        dataset_radar_gates = _dataset_radar_gates(self.dataset_radar, normalized, material_request=material_request)
        dataset_radar_review_packets = _dataset_radar_review_packets(self.dataset_radar, normalized)
        dataset_radar_lineage_split_policy = _dataset_radar_lineage_split_policy(self.dataset_radar)
        dataset_radar_training_review_gate = _dataset_radar_training_review_gate(
            dataset_radar_gates,
            dataset_radar_review_packets,
        )
        knowledge_artifact_runtime_gate = _knowledge_artifact_runtime_gate(normalized)
        policy_scan = self.policy_kernel.scan(_policy_targets(normalized, dataset, eval_cases))
        blocked = (
            policy_scan.summary.active_hard_fail_count > 0
            or any(not gate["allowed"] for gate in dataset_radar_gates)
            or not knowledge_artifact_runtime_gate.get("allowed", True)
        )
        status = "blocked" if blocked else ("needs_review" if not dataset_radar_training_review_gate["allowed"] else _status_for_dataset(dataset))
        manifest = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "dataset_manifest_id": normalized.dataset_manifest_id,
            "purpose": normalized.purpose,
            "task_type": normalized.task_type,
            "knowledge_artifact_refs": normalized.knowledge_artifact_refs,
            "material_request_ref": normalized.material_request_ref,
            "status": status,
            "created_at": utcnow().isoformat(),
            "dataset": dataset,
            "splits": _build_splits(
                examples,
                normalized.split_ratios,
                metadata=normalized.metadata,
                lineage_split_policy=dataset_radar_lineage_split_policy,
            ),
            "examples": examples,
            "eval_cases": eval_cases,
            "dataset_radar_gates": dataset_radar_gates,
            "dataset_radar_review_packets": dataset_radar_review_packets,
            "dataset_radar_lineage_split_policy": dataset_radar_lineage_split_policy,
            "dataset_radar_training_review_gate": dataset_radar_training_review_gate,
            "dataset_radar_material_request": _material_request_summary(normalized.material_request_ref, material_request),
            "knowledge_artifact_context_gate": "refs_only_no_prompt_or_weight_mutation",
            "knowledge_artifact_runtime_gate": knowledge_artifact_runtime_gate,
            "policy_scan": policy_scan.model_dump(mode="json"),
            "required_controls": _required_controls(),
            "metadata": normalized.metadata,
        }
        self._persist(manifest)
        return manifest

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        manifests = self._list_manifests(limit=limit)
        blocked_count = sum(1 for manifest in manifests if manifest.get("status") == "blocked")
        latest_manifest = manifests[0] if manifests else None
        runtime_state = "static-canon"
        if manifests:
            runtime_state = "degraded" if blocked_count or latest_manifest.get("status") == "blocked" else "live-bound"
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "dataset-forge",
            "authority": "NexusBrain",
            "runtime_state": runtime_state,
            "manifest_count": len(manifests),
            "ready_count": sum(1 for manifest in manifests if manifest.get("status") == "ready"),
            "blocked_count": blocked_count,
            "latest_manifest": latest_manifest,
            "manifests": manifests,
            "required_controls": _required_controls(),
            "operator_actions": _operator_actions(),
        }

    def scorecard(self) -> dict[str, Any]:
        summary = self.summary()
        return {
            **summary,
            "source_documents": [
                "docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md",
                "docs/NEXUSNET_YOUTUBE_ASSIMILATION_INTAKE_2026-04-30.md",
            ],
            "research_source_ids": ["YT-07"],
            "forge_boundary": "dataset-manifests-only-no-training-execution",
            "adapter_boundary": "ready-manifests-may-feed-adapter-registry-after-eval-and-rollback-gates",
        }

    def _persist(self, manifest: dict[str, Any]) -> None:
        self._memory_manifests.insert(0, manifest)
        self._memory_manifests = self._memory_manifests[:50]
        if self.manifests_dir is not None:
            safe_id = manifest["dataset_manifest_id"].replace(":", "_").replace("/", "_")
            path = self.manifests_dir / f"{safe_id}.json"
            manifest["artifact_path"] = str(path)
            path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    def _list_manifests(self, *, limit: int) -> list[dict[str, Any]]:
        manifests = list(self._memory_manifests)
        seen = {manifest.get("dataset_manifest_id") for manifest in manifests}
        if self.manifests_dir is not None:
            for path in self.manifests_dir.glob("*.json"):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if payload.get("dataset_manifest_id") not in seen:
                    manifests.append(payload)
        manifests.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return manifests[:limit]


def _example_from_source(request: DatasetForgeRequest, source: DatasetSource, index: int) -> dict[str, Any]:
    cleaned = _clean_text(source.text)
    return {
        "example_id": f"{request.dataset_manifest_id}::example::{index + 1}",
        "source_id": source.source_id,
        "source_type": source.source_type,
        "prompt": f"Summarize the NexusNet source {source.source_id} for {request.purpose}.",
        "response": cleaned,
        "contains_private_data": source.contains_private_data,
        "license_status": source.license_status,
        "provenance_ref": source.provenance_ref,
        "token_count": _estimate_tokens(cleaned),
        "metadata": source.metadata,
        "dataset_radar_source_id": source.dataset_radar_source_id,
        "generator_model": source.generator_model,
        "source_license_ref": source.source_license_ref,
        "allowed_distillation_state": source.allowed_distillation_state,
        "contamination_risk": source.contamination_risk,
        "knowledge_artifact_refs": request.knowledge_artifact_refs,
    }


def _eval_case_from_example(example: dict[str, Any]) -> dict[str, Any]:
    return {
        "eval_id": f"{example['example_id']}::eval",
        "prompt": example["prompt"],
        "expected_claim_refs": [example["provenance_ref"]] if example.get("provenance_ref") else [],
        "knowledge_artifact_refs": example.get("knowledge_artifact_refs") or [],
        "checks": ["source_grounding", "style_consistency", "privacy_redaction"],
    }


def _dataset_summary(request: DatasetForgeRequest, examples: list[dict[str, Any]]) -> dict[str, Any]:
    license_states = {example["license_status"] for example in examples}
    contains_private_data = any(example["contains_private_data"] for example in examples)
    provenance_refs = sorted({example["provenance_ref"] for example in examples if example.get("provenance_ref")})
    generator_models = sorted({example["generator_model"] for example in examples if example.get("generator_model")})
    contamination_risks = sorted({example["contamination_risk"] for example in examples if example.get("contamination_risk")})
    return {
        "dataset_manifest_id": request.dataset_manifest_id,
        "purpose": request.purpose,
        "source_count": len(request.sources),
        "example_count": len(examples),
        "token_count": sum(int(example["token_count"]) for example in examples),
        "contains_private_data": contains_private_data,
        "license_status": _combined_license_status(license_states),
        "provenance_refs": provenance_refs,
        "synthetic_generator_models": generator_models,
        "contamination_risks": contamination_risks,
        "knowledge_artifact_refs": request.knowledge_artifact_refs,
    }


def _policy_targets(
    request: DatasetForgeRequest,
    dataset: dict[str, Any],
    eval_cases: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    private_or_trace_sources = dataset["contains_private_data"] or any(
        source.source_type in {"trace", "chat"} for source in request.sources
    )
    return [
        {
            "target_id": f"training::{request.dataset_manifest_id}",
            "target_type": "training_candidate",
            "metadata": {
                "contains_private_data": dataset["contains_private_data"],
                "uses_user_data": private_or_trace_sources,
                "operator_approved": request.operator_approved,
                "promotion_requested": True,
                "eval_refs": [case["eval_id"] for case in eval_cases],
            },
        },
        {
            "target_id": f"artifact::{request.dataset_manifest_id}",
            "target_type": "artifact",
            "metadata": {
                "promotion_requested": True,
                "license_state": "approved" if dataset["license_status"] == "approved" else None,
                "provenance_refs": dataset["provenance_refs"],
            },
        },
    ]


def _build_splits(
    examples: list[dict[str, Any]],
    split_ratios: dict[str, float],
    *,
    metadata: dict[str, Any] | None = None,
    lineage_split_policy: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    sealed_source_ids = list(
        (metadata or {}).get("sealed_eval_source_ids")
        or (lineage_split_policy or {}).get("sealed_eval_source_ids")
        or []
    )
    count = len(examples)
    if count == 0:
        return {
            "train": {"example_count": 0, "example_ids": [], "blocked_source_ids": sealed_source_ids},
            "validation": {"example_count": 0, "example_ids": []},
            "test": {"example_count": 0, "example_ids": []},
            "heldout": {"example_count": 0, "example_ids": []},
            "adversarial": {"example_count": 0, "example_ids": []},
            "teacher_free_hidden": {
                "example_count": 0,
                "example_ids": [],
                "source_ids": sealed_source_ids,
                "sealed": True,
                "visible_to_training": False,
                "visible_to_teacher_council": False,
                "blocked_from_train": bool(sealed_source_ids),
            },
        }
    train_count = max(1, int(count * float(split_ratios.get("train", 0.8))))
    validation_count = int(count * float(split_ratios.get("validation", 0.1)))
    if count > 1 and validation_count == 0:
        validation_count = 1
    if train_count + validation_count > count:
        train_count = max(1, count - validation_count)
    test_count = max(0, count - train_count - validation_count)
    split_examples = {
        "train": examples[:train_count],
        "validation": examples[train_count : train_count + validation_count],
        "test": examples[train_count + validation_count : train_count + validation_count + test_count],
    }
    splits = {
        name: {
            "example_count": len(items),
            "example_ids": [item["example_id"] for item in items],
        }
        for name, items in split_examples.items()
    }
    splits["train"]["blocked_source_ids"] = sealed_source_ids
    splits["heldout"] = {
        "example_count": splits["test"]["example_count"],
        "example_ids": list(splits["test"]["example_ids"]),
    }
    splits["adversarial"] = {"example_count": 0, "example_ids": []}
    splits["teacher_free_hidden"] = {
        "example_count": 0,
        "example_ids": [],
        "source_ids": sealed_source_ids,
        "sealed": True,
        "visible_to_training": False,
        "visible_to_teacher_council": False,
        "blocked_from_train": bool(sealed_source_ids),
    }
    return splits


def _dataset_radar_lineage_split_policy(dataset_radar: DatasetRadar) -> dict[str, Any]:
    scorecard = dataset_radar.scorecard()
    return dict(scorecard.get("coder_expert_lineage_split_policy") or {})


def _dataset_radar_gates(
    dataset_radar: DatasetRadar,
    request: DatasetForgeRequest,
    *,
    material_request: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    gates: list[dict[str, Any]] = []
    approved_by_material_request = set((material_request or {}).get("approved_source_ids") or [])
    material_request_split = _normalize_dataset_split((material_request or {}).get("requested_split") or "")
    for source in request.sources:
        if not source.dataset_radar_source_id:
            continue
        requested_split = _source_requested_split(source, material_request_split)
        preview = dataset_radar.gate_preview({"dataset_id": source.dataset_radar_source_id, "splits": [requested_split]})
        preview_gates = preview.get("gates") or []
        gate = dict(preview_gates[0]) if preview_gates else {
            "source_id": source.dataset_radar_source_id,
            "split": requested_split,
            "allowed": False,
            "license_state": "blocked_unknown_license",
            "reason": "Dataset Radar did not return a split gate for this source.",
        }
        source_kind = str(preview.get("source_kind") or "unknown")
        gate["request_source_id"] = source.source_id
        gate["requested_split"] = requested_split
        gate["source_kind"] = source_kind
        gate["candidate_material"] = source_kind == "candidate"
        gate["dataset_radar_label"] = preview.get("label")
        gate["dataset_radar_source_url"] = preview.get("source_url")
        gate["provenance_state"] = preview.get("provenance_state")
        gate["material_request_ref"] = request.material_request_ref
        gate["material_request_requested_split"] = material_request_split or None
        gate["training_eligible"] = (
            source_kind == "canonical_source"
            and requested_split == "train"
            and bool(gate.get("allowed"))
        )
        if preview.get("latest_candidate_review"):
            gate["latest_candidate_review_id"] = preview["latest_candidate_review"].get("candidate_review_id")
        if request.material_request_ref:
            material_request_approved = source.dataset_radar_source_id in approved_by_material_request
            gate["material_request_approved"] = material_request_approved
            if material_request is None:
                gate["allowed"] = False
                gate["reason"] = "Dataset Radar material request artifact was not found."
                gate["training_eligible"] = False
            elif material_request_split and requested_split != material_request_split:
                gate["allowed"] = False
                gate["reason"] = "Dataset source intended split does not match the approved Dataset Radar material request split."
                gate["training_eligible"] = False
            elif not material_request_approved:
                gate["allowed"] = False
                gate["reason"] = "Dataset Radar material request did not approve this source for the requested teacher material split."
                gate["training_eligible"] = False
        if source.allowed_distillation_state == "blocked":
            gate["allowed"] = False
            gate["reason"] = "Synthetic/teacher-generated source has blocked distillation state."
            gate["training_eligible"] = False
        if source.contamination_risk == "high":
            gate["allowed"] = False
            gate["reason"] = "Source contamination risk is high."
            gate["training_eligible"] = False
        gates.append(gate)
    return gates


def _dataset_radar_review_packets(dataset_radar: DatasetRadar, request: DatasetForgeRequest) -> list[dict[str, Any]]:
    packets: list[dict[str, Any]] = []
    for source in request.sources:
        if not source.dataset_radar_source_id:
            continue
        detail = dataset_radar.source_detail(source.dataset_radar_source_id)
        if detail is None:
            packets.append(
                {
                    "source_id": source.source_id,
                    "dataset_radar_source_id": source.dataset_radar_source_id,
                    "source_kind": "missing",
                    "review_required_packet": {
                        "packet_id": f"review-required:{source.dataset_radar_source_id}",
                        "dataset_id": source.dataset_radar_source_id,
                        "source_kind": "missing",
                        "review_state": "review_required",
                        "training_promotion_allowed": False,
                        "teacher_context_allowed": False,
                        "validation_allowed": False,
                        "blocking_fields": ["source_detail"],
                        "fields": [],
                        "next_operator_action": "register or refresh the Dataset Radar source before forging the manifest",
                    },
                }
            )
            continue
        packet = detail.get("review_required_packet") or {}
        packets.append(
            {
                "source_id": source.source_id,
                "dataset_radar_source_id": source.dataset_radar_source_id,
                "source_kind": detail.get("source_kind"),
                "label": detail.get("label"),
                "source_url": detail.get("source_url"),
                "review_required_packet": packet,
            }
        )
    return packets


def _dataset_radar_training_review_gate(
    dataset_radar_gates: list[dict[str, Any]],
    dataset_radar_review_packets: list[dict[str, Any]],
) -> dict[str, Any]:
    review_packets = _review_packets_by_source(dataset_radar_review_packets)
    blockers: list[dict[str, Any]] = []
    for gate in dataset_radar_gates:
        requested_split = gate.get("requested_split") or gate.get("split")
        if requested_split != "train" or not gate.get("allowed"):
            continue
        source_id = str(gate.get("source_id") or "")
        review_packet = review_packets.get(source_id) or review_packets.get(str(gate.get("request_source_id") or ""))
        if not review_packet:
            blockers.append(
                {
                    "source_id": source_id,
                    "request_source_id": gate.get("request_source_id"),
                    "review_state": "missing",
                    "training_promotion_allowed": False,
                    "blocking_fields": ["source_review_packet"],
                    "reason": "Dataset Radar source review packet is required before train-split promotion.",
                }
            )
            continue
        if not bool(review_packet.get("training_promotion_allowed")):
            blockers.append(
                {
                    "source_id": source_id,
                    "request_source_id": gate.get("request_source_id"),
                    "review_packet_id": review_packet.get("packet_id"),
                    "review_state": review_packet.get("review_state"),
                    "training_promotion_allowed": False,
                    "blocking_fields": list(review_packet.get("blocking_fields") or []),
                    "reason": review_packet.get("next_operator_action")
                    or "Dataset Radar source review blockers must be cleared before training promotion.",
                }
            )
    return {
        "gate_id": "dataset_radar_training_review_gate",
        "allowed": not blockers,
        "checked_train_source_count": sum(
            1
            for gate in dataset_radar_gates
            if (gate.get("requested_split") or gate.get("split")) == "train" and gate.get("allowed")
        ),
        "blocked_source_ids": [blocker["source_id"] for blocker in blockers],
        "blockers": blockers,
    }


def _review_packets_by_source(dataset_radar_review_packets: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    packets: dict[str, dict[str, Any]] = {}
    for wrapper in dataset_radar_review_packets:
        review_packet = wrapper.get("review_required_packet") or {}
        for key in (
            wrapper.get("dataset_radar_source_id"),
            wrapper.get("source_id"),
            review_packet.get("dataset_id"),
        ):
            if key:
                packets[str(key)] = review_packet
    return packets


def _source_requested_split(source: DatasetSource, material_request_split: str) -> str:
    metadata_split = source.metadata.get("intended_split") or source.metadata.get("dataset_split") or source.metadata.get("split")
    if metadata_split:
        return _normalize_dataset_split(str(metadata_split))
    if material_request_split:
        return material_request_split
    return "train"


def _normalize_dataset_split(split: str) -> str:
    normalized = str(split or "").strip().lower().replace("-", "_")
    if not normalized:
        return ""
    if normalized in {"sealed_eval", "hidden_eval", "teacher_free_eval"}:
        return "teacher_free_hidden"
    if normalized == "teacher":
        return "teacher_context"
    if normalized == "eval":
        return "validation"
    return normalized


def _material_request_summary(material_request_ref: str | None, material_request: dict[str, Any] | None) -> dict[str, Any] | None:
    if not material_request_ref:
        return None
    if material_request is None:
        return {
            "material_request_id": material_request_ref,
            "status": "blocked_missing_artifact",
            "approved_source_ids": [],
            "blocked_source_ids": [],
        }
    return {
        "material_request_id": material_request.get("material_request_id"),
        "teacher_ref": material_request.get("teacher_ref"),
        "target_node": material_request.get("target_node"),
        "requested_split": material_request.get("requested_split"),
        "allowed_use": material_request.get("allowed_use"),
        "approved_source_ids": material_request.get("approved_source_ids") or [],
        "blocked_source_ids": material_request.get("blocked_source_ids") or [],
        "replay": material_request.get("replay") or {},
    }


def _combined_license_status(license_states: set[str]) -> LicenseStatus:
    if not license_states or "blocked" in license_states:
        return "blocked"
    if license_states == {"approved"}:
        return "approved"
    return "needs_review"


def _status_for_dataset(dataset: dict[str, Any]) -> DatasetStatus:
    if dataset["license_status"] != "approved" or not dataset["provenance_refs"]:
        return "needs_review"
    return "ready"


def _clean_text(text: str) -> str:
    return " ".join(text.strip().split())


def _estimate_tokens(text: str) -> int:
    return max(1, len(text.split()))


def _required_controls() -> list[str]:
    return [
        "source_manifest_schema",
        "privacy_license_filters",
        "provenance_refs",
        "prompt_response_examples",
        "train_validation_test_splits",
        "dataset_radar_gate",
        "dataset_radar_material_request_gate",
        "dataset_radar_source_review_packet",
        "dataset_radar_training_review_gate",
        "candidate_material_separation",
        "sealed_teacher_free_eval_split",
        "synthetic_teacher_distillation_metadata",
        "knowledge_artifact_context_gate",
        "knowledge_artifact_runtime_gate",
        "eval_case_generation",
        "policy_scan",
        "adapter_registry_handoff",
    ]


def _knowledge_artifact_runtime_gate(request: DatasetForgeRequest) -> dict[str, Any]:
    gate = {
        "requires_krc_runtime_context_allowed": True,
        "blocks_stale_or_quarantined_context": True,
        "blocks_raw_retrieval_fallback_context": True,
        "gate_source": "KnowledgeArtifactCompiler.query",
        "mutation_allowed": False,
    }
    if not request.knowledge_artifact_runtime_contexts:
        return gate

    blocked_refs: list[str] = []
    blocked_reasons: list[str] = []
    for context in request.knowledge_artifact_runtime_contexts:
        artifact_ref = str(context.get("artifact_id") or context.get("artifact_ref") or context.get("context") or "")
        fallback_state = str(context.get("fallback_state") or "")
        if context.get("runtime_context_allowed") is True and fallback_state == "compiled_artifact" and artifact_ref:
            continue
        if artifact_ref:
            blocked_refs.append(artifact_ref)
        reason = str(
            fallback_state
            or (context.get("quarantine_state") or {}).get("reason")
            or "krc_runtime_context_not_allowed"
        )
        blocked_reasons.append(reason)

    return {
        **gate,
        "allowed": not blocked_refs and not blocked_reasons,
        "runtime_context_evidence_count": len(request.knowledge_artifact_runtime_contexts),
        "blocked_artifact_refs": sorted(set(blocked_refs)),
        "blocked_reasons": sorted(set(blocked_reasons)),
    }


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/dataset-forge"},
        "build_manifest": {"method": "POST", "endpoint": "/ops/brain/dataset-forge/manifests"},
        "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/dataset-forge"},
    }

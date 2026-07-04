from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


NVIDIA_TECHNICAL_BLOG_URL = (
    "https://developer.nvidia.com/blog/"
    "nvidia-nemotron-3-nano-omni-powers-multimodal-agent-reasoning-in-a-single-efficient-open-model/"
)
HUGGINGFACE_MODEL_CARD_URL = "https://huggingface.co/nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16"

NemotronModality = Literal["text", "image", "video", "audio", "document", "gui", "mixed"]
NemotronLicenseStatus = Literal["unknown", "reviewed", "approved", "restricted"]


@dataclass(frozen=True)
class NemotronOmniTeacherAdapter:
    """Contract-only adapter for optional Nemotron Omni teacher evidence.

    This adapter deliberately does not launch inference. It lets NexusNet register
    and validate multimodal teacher evidence before any license, hardware, or
    runtime integration is production-approved.
    """

    teacher_resource_id: str = "nvidia_nemotron_3_nano_omni_2026_04"
    teacher_model_id: str = "nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16"
    precision_variants: tuple[str, ...] = ("BF16", "FP8", "NVFP4")
    roles: tuple[str, ...] = (
        "multimodal_perception_teacher",
        "document_intelligence_teacher",
        "video_audio_reasoning_teacher",
        "gui_reasoning_teacher",
    )
    modalities: tuple[NemotronModality, ...] = ("text", "image", "video", "audio", "document", "gui", "mixed")
    evidence_outputs: tuple[str, ...] = (
        "lesson_packet",
        "critique_packet",
        "multimodal_summary",
        "benchmark_observation",
        "dream_seed",
        "foundry_training_candidate",
    )
    source_refs: dict[str, str] = field(
        default_factory=lambda: {
            "nvidia_technical_blog": NVIDIA_TECHNICAL_BLOG_URL,
            "huggingface_model_card": HUGGINGFACE_MODEL_CARD_URL,
        }
    )

    def contract(self) -> dict[str, Any]:
        return {
            "teacher_resource": {
                "id": self.teacher_resource_id,
                "name": "NVIDIA Nemotron 3 Nano Omni",
                "model_id": self.teacher_model_id,
                "role": list(self.roles),
                "nexusnet_status": "assimilate_as_optional_adapter",
                "core_replacement": False,
            },
            "architecture": {
                "architecture_type": "Mamba2-Transformer Hybrid Mixture of Experts",
                "backbone": "Nemotron 3 Nano 30B-A3B",
                "total_parameters_b": 31,
                "active_parameters_b_per_token": 3,
                "context_window_tokens": 256000,
                "modalities": list(self.modalities),
                "vision_encoder": "C-RADIOv4-H",
                "audio_encoder": "Parakeet",
                "video_compression": "3D-convolution and efficient video sampling",
                "precision_variants": list(self.precision_variants),
            },
            "governance": {
                "license_name": "NVIDIA Open Model Agreement",
                "requires_license_review": True,
                "requires_gpu_profile": True,
                "requires_operator_approval": True,
                "production_allowed": False,
                "integration_mode": "shadow_teacher_evidence_only",
            },
            "evidence_output": list(self.evidence_outputs),
            "source_refs": dict(self.source_refs),
        }

    def build_evidence_packet(
        self,
        *,
        source_id: str,
        teacher_role: str,
        modality: NemotronModality,
        input_refs: list[str],
        task: str,
        output_summary: str,
        extracted_concepts: list[str],
        suggested_training_items: list[dict[str, Any]] | None = None,
        citations: list[str] | None = None,
        confidence: float = 0.0,
        license_status: NemotronLicenseStatus = "unknown",
        hardware_profile: dict[str, Any] | None = None,
        operator_approval_ref: str | None = None,
    ) -> dict[str, Any]:
        if teacher_role not in self.roles:
            raise ValueError(f"unsupported Nemotron Omni teacher role: {teacher_role}")
        if modality not in self.modalities:
            raise ValueError(f"unsupported Nemotron Omni modality: {modality}")

        hardware_profile = dict(hardware_profile or {})
        accepted_by_core = (
            license_status == "approved"
            and hardware_profile.get("profile_state") == "reviewed"
            and bool(operator_approval_ref)
        )
        governance_decision = (
            "accepted_for_shadow_teacher_evidence"
            if accepted_by_core
            else "blocked_pending_license_hardware_and_operator_review"
        )

        return {
            "source_id": source_id,
            "teacher_resource_id": self.teacher_resource_id,
            "teacher_model_id": self.teacher_model_id,
            "teacher_role": teacher_role,
            "modality": modality,
            "input_refs": list(input_refs),
            "task": task,
            "output_summary": output_summary,
            "extracted_concepts": list(extracted_concepts),
            "suggested_training_items": list(suggested_training_items or []),
            "citations": list(citations or []),
            "confidence": _bounded_confidence(confidence),
            "license_status": license_status,
            "hardware_profile": hardware_profile,
            "operator_approval_ref": operator_approval_ref,
            "accepted_by_core": accepted_by_core,
            "governance_decision": governance_decision,
            "raw_input_stored": False,
            "core_replacement": False,
            "evidence_output": list(self.evidence_outputs),
            "source_refs": dict(self.source_refs),
        }


def _bounded_confidence(value: float) -> float:
    return max(0.0, min(1.0, float(value)))

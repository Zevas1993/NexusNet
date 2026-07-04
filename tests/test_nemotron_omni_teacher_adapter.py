from __future__ import annotations

from nexus.services import build_services
from nexusnet.teachers.adapters.nemotron_omni_adapter import NemotronOmniTeacherAdapter
from tests.test_nexus_phase1_foundation import make_project


def test_nemotron_omni_adapter_contract_is_optional_multimodal_teacher_not_core_replacement():
    adapter = NemotronOmniTeacherAdapter()

    contract = adapter.contract()

    assert contract["teacher_resource"]["id"] == "nvidia_nemotron_3_nano_omni_2026_04"
    assert contract["teacher_resource"]["core_replacement"] is False
    assert contract["teacher_resource"]["nexusnet_status"] == "assimilate_as_optional_adapter"
    assert contract["teacher_resource"]["model_id"] == "nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16"
    assert set(contract["teacher_resource"]["role"]) >= {
        "multimodal_perception_teacher",
        "document_intelligence_teacher",
        "video_audio_reasoning_teacher",
        "gui_reasoning_teacher",
    }
    assert contract["architecture"]["total_parameters_b"] == 31
    assert contract["architecture"]["active_parameters_b_per_token"] == 3
    assert contract["architecture"]["context_window_tokens"] == 256000
    assert set(contract["architecture"]["modalities"]) >= {"text", "image", "video", "audio", "document", "gui"}
    assert contract["governance"]["requires_license_review"] is True
    assert contract["governance"]["requires_gpu_profile"] is True
    assert contract["governance"]["license_name"] == "NVIDIA Open Model Agreement"
    assert contract["governance"]["production_allowed"] is False
    assert contract["source_refs"]["nvidia_technical_blog"].startswith("https://developer.nvidia.com/")
    assert contract["source_refs"]["huggingface_model_card"].startswith("https://huggingface.co/nvidia/")


def test_nemotron_omni_adapter_builds_guarded_teacher_evidence_packet():
    adapter = NemotronOmniTeacherAdapter()

    packet = adapter.build_evidence_packet(
        source_id="source://lecture-video-001",
        teacher_role="multimodal_perception_teacher",
        modality="mixed",
        input_refs=["artifact://video/lecture-001", "artifact://slides/deck-001"],
        task="Summarize the multimodal lesson and produce dream seeds.",
        output_summary="Identified three routing failures and two multimodal lesson candidates.",
        extracted_concepts=["gui_reasoning", "audio_alignment", "long_context_video"],
        suggested_training_items=[
            {"item_id": "training-001", "kind": "synthetic_qa", "target": "vision-audio-alignment"}
        ],
        citations=["source://lecture-video-001#t=00:03:21"],
    )

    assert packet["teacher_model_id"] == "nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16"
    assert packet["teacher_role"] == "multimodal_perception_teacher"
    assert packet["modality"] == "mixed"
    assert packet["input_refs"] == ["artifact://video/lecture-001", "artifact://slides/deck-001"]
    assert packet["extracted_concepts"] == ["gui_reasoning", "audio_alignment", "long_context_video"]
    assert packet["license_status"] == "unknown"
    assert packet["accepted_by_core"] is False
    assert packet["governance_decision"] == "blocked_pending_license_hardware_and_operator_review"
    assert packet["raw_input_stored"] is False
    assert set(packet["evidence_output"]) == {
        "lesson_packet",
        "critique_packet",
        "multimodal_summary",
        "benchmark_observation",
        "dream_seed",
        "foundry_training_candidate",
    }

    approved_shadow_packet = adapter.build_evidence_packet(
        source_id="source://reviewed-doc-001",
        teacher_role="document_intelligence_teacher",
        modality="document",
        input_refs=["artifact://document/paper-001"],
        task="Extract a benchmark observation.",
        output_summary="Benchmark observation extracted.",
        extracted_concepts=["ocr_chart_reasoning"],
        license_status="approved",
        hardware_profile={"profile_state": "reviewed", "precision": "fp8"},
        operator_approval_ref="approval://operator/nemotron-shadow-001",
    )

    assert approved_shadow_packet["accepted_by_core"] is True
    assert approved_shadow_packet["governance_decision"] == "accepted_for_shadow_teacher_evidence"


def test_live_teacher_registry_registers_nemotron_as_auxiliary_optional_teacher(tmp_path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    profiles = {profile.teacher_id: profile for profile in services.brain_teachers.list_profiles()}
    profile = profiles["nvidia-nemotron-3-nano-omni"]
    card = profile.capability_card

    assert profile.status_label == "STRONG ACCEPTED DIRECTION"
    assert profile.role == "multimodal-professor"
    assert card is not None
    assert set(card.modalities) >= {"text", "image", "video", "audio", "document", "gui"}
    assert card.supports_tools is True
    assert card.supports_structured_output is True
    assert card.context_window == 256000
    assert card.locality == "mixed_local_then_remote"
    assert "local-gpu-profile-required" in card.hardware_targets

    assignment = services.brain_teachers.assignment_for("multimodal-professor", "v2026_live")
    assert assignment is not None
    assert assignment.auxiliary is True
    assert assignment.status_label == "STRONG ACCEPTED DIRECTION"
    assert assignment.primary_teacher_id == "nvidia-nemotron-3-nano-omni"
    assert assignment.secondary_teacher_id == "qwen3-vl"

    live_core = [
        candidate
        for candidate in services.brain_teachers.list_assignments()
        if candidate.registry_layer == "v2026_live"
        and candidate.subject != "core-brain"
        and not candidate.auxiliary
        and candidate.primary_teacher_id
        and candidate.secondary_teacher_id
    ]
    assert len(live_core) == 19

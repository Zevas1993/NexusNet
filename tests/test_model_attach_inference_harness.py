from __future__ import annotations

import json
from pathlib import Path

import pytest

from nexus.schemas import CapabilityCard, ModelRegistration, RuntimeProfile
from nexus.services import build_services
from nexusnet.runtime.model_attach_harness import ModelAttachInferenceHarness
from nexusnet.schemas import SessionContext
from tests.test_nexus_phase1_foundation import make_project


def test_live_generation_emits_complete_sanitized_layer11_harness_evidence(tmp_path: Path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))
    secret = "SECRET-LAYER11-MODEL-OUTPUT-EVIDENCE"

    result = services.brain.generate(
        session_context=SessionContext(
            session_id="layer11-live-session",
            trace_id="layer11-live-trace",
            expert="researcher",
            use_retrieval=False,
        ),
        prompt=f"Exercise the model attach harness without persisting {secret}.",
        model_hint="mock/default",
    )

    harness = result.runtime_selection["layer11_harness"]
    assert harness["status"] == "evidence-recorded"
    assert harness["authority"] == "NexusBrain"
    assert harness["route_envelope"]["trace_id"] == "layer11-live-trace"
    assert harness["route_envelope"]["runtime_ladder"] == ["mock"]
    assert harness["route_envelope"]["raw_content_included"] is False

    attach = harness["attach_contract"]
    assert attach["status"] == "authorized-inference-only"
    assert attach["model_provider_contract"]["requested_role"] == "inference-tool"
    assert attach["model_provider_contract"]["brain_replacement_allowed"] is False
    assert attach["provider_capability_passport"]["runtime_name"] == "mock"
    assert attach["model_passport"]["model_id"] == "mock/default"
    assert attach["model_passport"]["context_tokens"] >= 8192
    assert attach["quantization_profile"]["profile"] == "unquantized-or-runtime-managed"
    assert attach["context_hardware_posture"]["context_tokens"] >= 8192

    rights = attach["rights_gate"]
    assert rights["inference_use_authorized"] is True
    assert rights["training_use_authorized"] is False
    assert rights["teacher_or_distillation_use_authorized"] is False
    assert rights["boundary"] == "inference-only-no-training-or-teacher-use"

    output_evidence = harness["output_evidence"]
    assert output_evidence["status"] == "served"
    assert len(output_evidence["output_sha256"]) == 64
    assert output_evidence["output_chars"] == len(result.output)
    assert output_evidence["raw_output_included"] is False
    assert output_evidence["fallback_containment"]["fallback_used"] is False
    assert output_evidence["fallback_containment"]["contained"] is True

    persisted = json.dumps(services.brain.model_attach_harness.summary(trace_id="layer11-live-trace"))
    assert secret not in persisted
    assert result.output not in persisted
    full_harness_state = json.dumps(services.brain.model_attach_harness.summary()).replace("\\\\", "/")
    assert str(project_root).replace("\\", "/") not in full_harness_state


def test_layer11_harness_records_real_fallback_attempts_and_containment(tmp_path: Path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    result = services.brain.generate(
        session_context=SessionContext(
            session_id="layer11-fallback-session",
            trace_id="layer11-fallback-trace",
            use_retrieval=False,
        ),
        prompt="Exercise fallback containment.",
        model_hint="ollama/llama3.1",
    )

    harness = result.runtime_selection["layer11_harness"]
    evidence = harness["output_evidence"]
    assert result.runtime_name == "mock"
    assert harness["route_envelope"]["runtime_ladder"][0] == "ollama"
    assert evidence["fallback_containment"]["fallback_used"] is True
    assert evidence["fallback_containment"]["requested_runtime"] == "ollama"
    assert evidence["fallback_containment"]["served_runtime"] == "mock"
    assert evidence["fallback_containment"]["contained"] is True
    assert any(item["runtime_name"] == "ollama" for item in evidence["attempt_receipts"])
    assert all(item["raw_error_included"] is False for item in evidence["attempt_receipts"])


def test_model_ingestion_blocks_inference_when_model_rights_are_blocked(tmp_path: Path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))
    registration = services.model_registry.resolve_model("mock/default").model_copy(deep=True)
    registration.metadata.update(
        {
            "license_status": "blocked",
            "inference_use_authorized": False,
            "rights_refs": ["rights-review::blocked-model"],
        }
    )
    services.model_registry._upsert(registration)

    with pytest.raises(PermissionError, match="inference rights"):
        services.brain.model_ingestion.attach(
            model_hint="mock/default",
            role="inference-tool",
            runtime_name="mock",
            trace_id="layer11-rights-blocked-trace",
            runtime_ladder=["mock"],
        )


def test_layer11_harness_hashes_absolute_model_paths_in_public_receipts(tmp_path: Path):
    harness = ModelAttachInferenceHarness(artifacts_dir=tmp_path)
    private_model_id = "llama.cpp/F:/private/models/owner-only.gguf"
    registration = ModelRegistration(
        model_id=private_model_id,
        runtime_name="llama.cpp",
        display_name="Private GGUF",
        capability_card=CapabilityCard(
            model_id=private_model_id,
            model_family="gguf",
            runtime_name="llama.cpp",
        ),
    )

    contract = harness.authorize_attach(
        trace_id="absolute-path-redaction",
        registration=registration,
        runtime_name="llama.cpp",
        requested_role="inference-tool",
        runtime_ladder=["llama.cpp"],
        runtime_profile=RuntimeProfile(runtime_name="llama.cpp", backend_type="local"),
    )

    assert "F:/private" not in json.dumps(contract)
    assert contract["model_passport"]["model_id"].startswith("model::")

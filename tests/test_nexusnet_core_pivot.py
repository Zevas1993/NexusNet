from __future__ import annotations

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexus.services import build_services
from nexusnet.schemas import SessionContext
from tests.test_nexus_phase1_foundation import make_project


def test_core_summary_exposes_brain_first_attach_memory_and_fusion(tmp_path: Path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    summary = services.brain.core_summary(model_hint="mock/default", expert="researcher")

    assert summary["brain_first_execution"] is True
    assert summary["canonical_attach_seam"] == "nexusnet.core.attach_base_model.attach_base_model"
    assert summary["memory_node"]["plane_count"] >= 11
    assert summary["runtime_execution_plan"]["hardware_profile"]["max_context_tokens"] >= 32768
    assert summary["fusion_scaffold"]["backbone"] == "mixtral"
    assert summary["fusion_scaffold"]["devstral_integrated"] is True
    assert summary["fusion_scaffold"]["alignment"]["projection_required_count"] >= 1


def test_brain_generate_records_execution_order_and_qes_memory_fusion_context(tmp_path: Path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    result = services.brain.generate(
        session_context=SessionContext(session_id="pivot-session", expert="researcher", use_retrieval=False),
        prompt="Summarize the core NexusNet path.",
        model_hint="mock/default",
    )

    core_execution = result.inference_trace.metrics["core_execution"]
    stage_names = core_execution["stage_names"]
    assert stage_names.index("brain-execution-start") < stage_names.index("attach-base-model")
    assert stage_names.index("attach-base-model") < stage_names.index("runtime-generate")
    assert core_execution["qes_execution_plan"]["selected_runtime_name"]
    assert core_execution["memory_node"]["plane_count"] >= 11
    assert core_execution["fusion_scaffold"]["router"] == "mixtral-router"
    assert core_execution["fusion_scaffold"]["alignment"]["ready_for_shadow_fusion"] is True
    assert core_execution["artifact_id"].startswith("coreexec_")
    assert Path(core_execution["artifact_path"]).exists()

    stored_trace = services.store.get_trace(result.trace_id)
    stored_core_execution = ((stored_trace or {}).get("metrics") or {}).get("core_execution", {})
    assert stored_core_execution["artifact_id"] == core_execution["artifact_id"]
    assert stored_core_execution["artifact_path"] == core_execution["artifact_path"]


def test_memory_node_respects_root_config_and_has_no_frozen_plane_count(tmp_path: Path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    root_planes = project_root / "config" / "planes.yaml"
    payload = yaml.safe_load(root_planes.read_text(encoding="utf-8"))
    payload["planes"].append(
        {
            "plane_name": "attention_cache",
            "conceptual_plane": "metacognitive",
            "description": "Extra plane added by test to prove config-driven loading.",
            "aliases": ["kv-cache"],
            "projection_roles": ["semantic"],
            "token_budget_ratio": 0.02,
            "status_label": "UNRESOLVED CONFLICT",
        }
    )
    root_planes.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    updated_services = build_services(str(project_root))
    summary = updated_services.brain_memory_node.summary()

    assert summary["plane_count"] == 12
    assert any(item["plane_name"] == "attention_cache" for item in summary["planes"])


def test_ops_brain_core_endpoint_surfaces_core_execution_summary(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.get("/ops/brain/core", params={"model_hint": "mock/default", "expert": "researcher"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["brain_first_execution"] is True
    assert payload["memory_node"]["plane_count"] >= 11
    assert payload["fusion_scaffold"]["cortex_peer"]["peer_to_router"] is True
    assert payload["traceability"]["trace_detail_template"] == "/ops/traces/{trace_id}"


def test_wrapper_surface_exposes_core_execution_traceability(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    chat = client.post("/chat", json={"session_id": "pivot-ui", "message": "Explain the core pivot path.", "rag": False})
    assert chat.status_code == 200
    trace_id = chat.json()["trace_id"]

    response = client.get("/ops/brain/wrapper-surface", params={"session_id": "pivot-ui"})
    assert response.status_code == 200
    payload = response.json()
    core_execution = payload["core_execution"]

    assert core_execution["brain_first_execution"] is True
    assert core_execution["latest_trace_id"] == trace_id
    assert core_execution["latest_artifact_id"].startswith("coreexec_")
    assert Path(core_execution["latest_artifact_path"]).exists()
    assert core_execution["trace_detail_template"] == "/ops/traces/{trace_id}"
    assert core_execution["core_summary_ref"] == "/ops/brain/core"


def test_core_summary_and_wrapper_surface_absorb_teacher_dream_and_foundry_evidence(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    chat = client.post(
        "/chat",
        json={
            "session_id": "core-evidence",
            "message": "Explain why the brain path needs teacher-backed native growth evidence.",
            "teacher_id": "mixtral-8x7b",
            "rag": False,
        },
    )
    assert chat.status_code == 200
    trace_id = chat.json()["trace_id"]

    dream = client.post(
        "/ops/brain/dream",
        json={"trace_id": trace_id, "model_hint": "mock/default", "variant_count": 2},
    )
    assert dream.status_code == 200
    assert dream.json()["dream_id"]

    distill = client.post(
        "/ops/brain/distill-dataset",
        json={"name": "core-evidence-dataset", "trace_limit": 20, "include_dreams": True, "include_curriculum": True},
    )
    assert distill.status_code == 200
    native_takeover_candidate = distill.json()["native_takeover_candidate"]["candidate_id"]

    core = client.get("/ops/brain/core", params={"session_id": "core-evidence"})
    assert core.status_code == 200
    evidence = core.json()["evidence_feeds"]

    assert evidence["teacher_evidence"]["bundle_count"] >= 1
    assert evidence["teacher_evidence"]["latest_bundle_id"]
    assert evidence["dreaming"]["artifact_count"] >= 1
    assert evidence["dreaming"]["latest_dream_id"]
    assert evidence["foundry"]["lineage_artifact_count"] >= 1
    assert evidence["foundry"]["latest_distillation_artifact_id"]
    assert native_takeover_candidate in evidence["foundry"]["native_takeover_candidate_ids"]

    wrapper = client.get("/ops/brain/wrapper-surface", params={"session_id": "core-evidence"})
    assert wrapper.status_code == 200
    wrapper_evidence = wrapper.json()["core_execution"]["evidence_feeds"]

    assert wrapper_evidence["teacher_evidence"]["latest_bundle_id"] == evidence["teacher_evidence"]["latest_bundle_id"]
    assert wrapper_evidence["dreaming"]["latest_dream_id"] == evidence["dreaming"]["latest_dream_id"]
    assert wrapper_evidence["foundry"]["latest_distillation_artifact_id"] == evidence["foundry"]["latest_distillation_artifact_id"]

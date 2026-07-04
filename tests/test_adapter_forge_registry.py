from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.adapters.forge import AdapterForgeRegistry, AdapterRecordRequest
from tests.test_nexus_phase1_foundation import make_project


def clean_adapter_payload(**overrides):
    payload = {
        "adapter_id": "adapter::code-ao-style-v1",
        "target_slot": "ao::code",
        "base_model": {
            "model_id": "Qwen/Qwen3.5-27B",
            "revision": "pinned-test-revision",
            "license": "declared-compatible",
            "source_url": "https://huggingface.co/Qwen/Qwen3.5-27B",
        },
        "method": {
            "type": "lora",
            "framework": "peft",
            "precision": "bf16",
            "target_modules": ["q_proj", "v_proj"],
        },
        "dataset": {
            "dataset_manifest_id": "dataset::code-ao-style-v1",
            "source_count": 4,
            "example_count": 120,
            "token_count": 48000,
            "contains_private_data": False,
            "license_status": "approved",
            "provenance_refs": ["docs/NEXUSNET_YOUTUBE_ASSIMILATION_INTAKE_2026-04-30.md"],
        },
        "eval": {
            "base_score": 0.72,
            "adapter_score": 0.81,
            "regression_failures": [],
            "style_gain": 0.09,
            "grounding_delta": 0.02,
            "tool_call_delta": 0.04,
        },
        "deployment": {
            "adapter_artifact": "runtime/artifacts/adapters/code-ao-style-v1/adapter.safetensors",
            "merged_artifact": "",
            "gguf_artifact": "",
            "runtime_targets": ["vllm", "llama.cpp", "ollama"],
            "rollback_adapter_id": "adapter::code-ao-style-v0",
        },
        "operator_approved": True,
    }
    payload.update(overrides)
    return payload


def test_adapter_forge_registry_registers_shadow_candidate_with_policy_eval_and_rollback():
    registry = AdapterForgeRegistry()

    record = registry.register(AdapterRecordRequest.model_validate(clean_adapter_payload()))

    assert record["status_label"] == "LOCKED CANON"
    assert record["authority"] == "NexusBrain"
    assert record["adapter_id"] == "adapter::code-ao-style-v1"
    assert record["status"] == "shadow"
    assert record["promotion_state"] == "eval-passed-shadow"
    assert record["eval"]["adapter_score"] > record["eval"]["base_score"]
    assert record["deployment"]["rollback_adapter_id"] == "adapter::code-ao-style-v0"
    assert record["policy_scan"]["summary"]["allow_merge"] is True

    summary = registry.summary()
    assert summary["adapter_count"] == 1
    assert summary["shadow_count"] == 1
    assert summary["operator_actions"]["register_candidate"]["endpoint"] == "/ops/brain/adapter-registry/candidates"


def test_adapter_forge_registry_blocks_private_or_unlicensed_training_candidates():
    registry = AdapterForgeRegistry()

    record = registry.register(
        {
            **clean_adapter_payload(
                adapter_id="adapter::private-raw-log",
                operator_approved=False,
                dataset={
                    "dataset_manifest_id": "dataset::private-raw-log",
                    "source_count": 1,
                    "example_count": 8,
                    "token_count": 12000,
                    "contains_private_data": True,
                    "license_status": "needs_review",
                    "provenance_refs": [],
                },
            )
        }
    )

    assert record["status"] == "blocked"
    assert record["promotion_state"] == "blocked-by-policy"
    assert record["policy_scan"]["summary"]["allow_merge"] is False
    assert {
        "training_candidate_requires_operator_approval",
        "artifact_requires_license_and_provenance",
    }.issubset({finding["rule_id"] for finding in record["policy_scan"]["findings"]})

    scorecard = registry.scorecard()
    assert scorecard["runtime_state"] == "degraded"
    assert scorecard["blocked_count"] == 1
    assert scorecard["latest_adapter"]["status"] == "blocked"


def test_adapter_registry_api_blackbox_and_control_panel_surface(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post("/ops/brain/adapter-registry/candidates", json=clean_adapter_payload())
    assert response.status_code == 200
    record = response.json()
    assert record["status"] == "shadow"

    summary = client.get("/ops/brain/adapter-registry")
    assert summary.status_code == 200
    summary_payload = summary.json()
    assert summary_payload["adapter_count"] == 1
    assert summary_payload["latest_adapter"]["adapter_id"] == "adapter::code-ao-style-v1"

    scorecard = client.get("/ops/brain/canon/adapter-registry")
    assert scorecard.status_code == 200
    scorecard_payload = scorecard.json()
    assert scorecard_payload["runtime_state"] == "live-bound"
    assert "adapter_metadata_schema" in scorecard_payload["required_controls"]
    assert scorecard_payload["operator_actions"]["register_candidate"]["endpoint"] == "/ops/brain/adapter-registry/candidates"

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "adapter-registry-cockpit"})
    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    assert control_panel["adapter_registry_scorecard"]["adapter_count"] == 1

    blackbox = client.get("/ops/brain/canon/blackbox", params={"session_id": "adapter-registry-cockpit"}).json()
    assert blackbox["scorecard_refs"]["adapter_registry"] == "/ops/brain/canon/adapter-registry"

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Adapter Registry" in ui.text
    assert "adapterRegistryScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderAdapterRegistryScorecard" in app_js
    assert "/ops/brain/canon/adapter-registry" in app_js

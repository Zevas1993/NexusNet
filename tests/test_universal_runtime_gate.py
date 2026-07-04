from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexus.schemas import ChatRequest
from nexus.services import build_services
from nexusnet.schemas import DistillationExportRequest
from tests.test_nexus_phase1_foundation import make_project


def test_model_runtime_planner_routes_large_model_formats(tmp_path: Path):
    services = build_services(str(make_project(tmp_path)))

    capabilities = services.model_runtime_planner.capabilities()
    lane_names = {lane["lane"] for lane in capabilities["lanes"]}
    assert {
        "llama.cpp",
        "vllm",
        "sglang",
        "tgi",
        "tensorrt-llm",
        "transformers",
        "mlc",
        "onnx-genai",
    }.issubset(lane_names)

    gguf = services.model_runtime_planner.plan(
        {"model_id": "C:/models/Mixtral-8x7B-Instruct.Q4_K_M.gguf", "context_tokens": 8192}
    )
    assert gguf["model_format"] == "gguf"
    assert gguf["recommended_lane"] == "llama.cpp"
    assert gguf["quantization"] == "q4_k_m"
    assert "llama.cpp" in gguf["supported_runtime_lanes"]

    awq = services.model_runtime_planner.plan(
        {"model_id": "TheBloke/Mistral-7B-Instruct-AWQ", "context_tokens": 4096}
    )
    assert awq["model_format"] == "safetensors"
    assert awq["quantization"] == "awq"
    assert awq["recommended_lane"] in {"vllm", "sglang", "tgi"}

    gptq = services.model_runtime_planner.plan(
        {"model_id": "TheBloke/Llama-2-13B-chat-GPTQ", "context_tokens": 4096}
    )
    assert gptq["quantization"] == "gptq"
    assert "transformers" in gptq["fallback_lanes"]


def test_model_runtime_planner_api_and_validation(tmp_path: Path):
    client = TestClient(create_app(str(make_project(tmp_path))))

    capabilities = client.get("/ops/brain/runtimes/capabilities")
    assert capabilities.status_code == 200
    lanes = {lane["lane"] for lane in capabilities.json()["lanes"]}
    assert "vllm" in lanes
    assert "onnx-genai" in lanes

    plan = client.post(
        "/ops/brain/models/plan",
        json={"model_id": "D:/weights/qwen2.5-7b-instruct.Q5_K_M.gguf", "context_tokens": 8192},
    )
    assert plan.status_code == 200
    payload = plan.json()
    assert payload["recommended_lane"] == "llama.cpp"
    assert payload["compatibility_plan_id"]

    unsupported = client.post("/ops/brain/models/validate", json={"model_id": "unknown/model.foo"})
    assert unsupported.status_code == 200
    assert unsupported.json()["ok"] is False
    assert "unsupported-model-format" in unsupported.json()["blocked_reasons"]


def test_chat_exposes_requested_vs_served_runtime_on_dev_fallback(tmp_path: Path):
    client = TestClient(create_app(str(make_project(tmp_path))))

    response = client.post(
        "/chat",
        json={
            "session_id": "runtime-truth",
            "message": "hello from the runtime gate",
            "model_hint": "ollama/mistral-small:4",
            "rag": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["requested_model_id"] == "ollama/mistral-small:4"
    assert payload["requested_runtime"] == "ollama"
    assert payload["served_model_id"]
    assert payload["served_runtime"]
    assert payload["served_runtime"] != payload["requested_runtime"]
    assert payload["runtime_lane"] == payload["served_runtime"]
    assert payload["model_id"] == payload["served_model_id"]
    assert payload["runtime"] == payload["served_runtime"]
    assert payload["fallback_used"] is True
    assert payload["fallback_reason"]
    assert payload["compatibility_plan_id"]


def test_chat_exposes_core_attach_compatibility_provenance(tmp_path: Path):
    client = TestClient(create_app(str(make_project(tmp_path))))

    attach = client.post(
        "/ops/brain/core/attach",
        json={
            "mode": "product",
            "model_ref": "local/llama-product",
            "metadata": {"model_name": "local/llama-product", "model_family": "llama", "vocab_size": 32000},
            "router_hidden_dim": 4096,
            "expert_hidden_dim": 4096,
            "strict_product_mode": True,
        },
    )
    assert attach.status_code == 200
    attach_plan_id = attach.json()["compatibility_plan"]["compatibility_plan_id"]

    response = client.post(
        "/chat",
        json={
            "session_id": "runtime-attach-provenance",
            "message": "carry the attach-time compatibility plan into runtime provenance",
            "model_hint": "ollama/mistral-small:4",
            "rag": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    runtime_selection = payload["runtime_selection"]
    assert payload["compatibility_plan_id"] == attach_plan_id
    assert payload["compatibility_status"] == "COMPATIBLE"
    assert payload["attachment_mode"] == "product"
    assert payload["product_evidence"] is True
    assert runtime_selection["compatibility_plan_id"] == attach_plan_id
    assert runtime_selection["compatibility_status"] == "COMPATIBLE"
    assert runtime_selection["attachment_mode"] == "product"
    assert runtime_selection["product_evidence"] is True
    assert payload["trace"]["runtime_selection"]["compatibility_plan_id"] == attach_plan_id


def test_product_mode_fails_closed_instead_of_mock_fallback(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("NEXUSNET_PRODUCT_MODE", "1")
    monkeypatch.delenv("NEXUSNET_ALLOW_MOCK_RUNTIME", raising=False)

    client = TestClient(create_app(str(make_project(tmp_path))), raise_server_exceptions=False)
    response = client.post(
        "/chat",
        json={
            "session_id": "product-runtime-gate",
            "message": "this must not be served by mock",
            "model_hint": "ollama/mistral-small:4",
            "rag": False,
        },
    )

    assert response.status_code == 503
    detail = response.json()["detail"]
    assert detail["error"] == "runtime-unavailable"
    assert detail["requested_model_id"] == "ollama/mistral-small:4"
    assert detail["requested_runtime"] == "ollama"
    assert detail["served_runtime"] is None
    assert "mock-runtime-disabled" in detail["blocked_reasons"]
    assert "product-evidence-required" in detail["blocked_reasons"]


def test_qes_selector_never_selects_unregistered_or_unavailable_onnx(tmp_path: Path):
    services = build_services(str(make_project(tmp_path)))

    decision = services.brain_runtime_registry.selector.select("ollama/missing")

    assert decision.selected_runtime_name != "onnx-genai"
    if "onnx-genai" in decision.fallback_runtime_names:
        assert "onnx-genai" in services.runtime_registry.adapters


def test_distillation_export_excludes_mock_traces_by_default(tmp_path: Path):
    services = build_services(str(make_project(tmp_path)))
    services.operator.execute_chat(
        ChatRequest(
            session_id="distill-mock-filter",
            message="mock traces must not train the native student by default",
            model_hint="ollama/mistral-small:4",
            rag=False,
        )
    )

    filtered = services.brain_distillation.export(
        DistillationExportRequest(
            name="filtered-mock-traces",
            trace_limit=20,
            include_dreams=False,
            include_curriculum=False,
        )
    )
    assert filtered.sample_count == 0
    assert filtered.metadata["excluded_mock_trace_count"] >= 1

    synthetic = services.brain_distillation.export(
        DistillationExportRequest(
            name="synthetic-mock-traces",
            trace_limit=20,
            include_dreams=False,
            include_curriculum=False,
            include_mock_traces=True,
        )
    )
    assert synthetic.sample_count >= 1
    assert synthetic.metadata["included_mock_traces"] is True


def test_distillation_export_preserves_live_compatibility_provenance_and_excludes_dev(tmp_path: Path):
    services = build_services(str(make_project(tmp_path)))
    live_provenance = {
        "compatibility_plan_id": "attach_compat_live123",
        "compatibility_status": "COMPATIBLE",
        "attachment_mode": "product",
        "product_evidence": True,
    }
    dev_provenance = {
        "compatibility_plan_id": "attach_compat_dev123",
        "compatibility_status": "UNVERIFIED",
        "attachment_mode": "dev",
        "product_evidence": False,
    }
    services.store.save_trace(
        "trace-live-compat",
        "distill-compat",
        "ok",
        {
            "trace_id": "trace-live-compat",
            "session_id": "distill-compat",
            "status": "ok",
            "request": {"prompt": "live product trace"},
            "model_id": "local/llama-product",
            "runtime_name": "llama.cpp",
            "runtime_selection": {
                "served_runtime_name": "llama.cpp",
                **live_provenance,
            },
            "output_preview": "live target",
        },
        "2026-04-23T00:00:00+00:00",
    )
    services.store.save_trace(
        "trace-dev-compat",
        "distill-compat",
        "ok",
        {
            "trace_id": "trace-dev-compat",
            "session_id": "distill-compat",
            "status": "ok",
            "request": {"prompt": "dev trace"},
            "model_id": "local/dev",
            "runtime_name": "llama.cpp",
            "runtime_selection": {
                "served_runtime_name": "llama.cpp",
                **dev_provenance,
            },
            "output_preview": "dev target",
        },
        "2026-04-23T00:00:01+00:00",
    )

    filtered = services.brain_distillation.export(
        DistillationExportRequest(
            name="compat-filtered-live-traces",
            trace_limit=20,
            include_dreams=False,
            include_curriculum=False,
        )
    )

    assert filtered.sample_count == 1
    assert filtered.metadata["compatibility_plan_ids"] == ["attach_compat_live123"]
    assert filtered.metadata["compatibility_status_counts"] == {"COMPATIBLE": 1}
    assert filtered.metadata["excluded_mock_trace_count"] >= 1
    sample = json.loads(Path(filtered.artifact_path).read_text(encoding="utf-8").splitlines()[0])
    assert sample["metadata"]["compatibility_provenance"] == live_provenance


def test_product_docs_and_check_targets_do_not_overclaim_or_mask_failures():
    repo_root = Path(__file__).resolve().parents[1]
    summary = (repo_root / "PROJECT_SUMMARY.md").read_text(encoding="utf-8").lower()
    assert "complete and ready for deployment" not in summary
    assert "ready for deployment" not in summary
    assert "complete framework ready for production" not in summary
    assert "classified and routed through supported runtime lanes" in summary

    version = (repo_root / "VERSION").read_text(encoding="utf-8").strip()
    assert f'version = "{version}"' in (repo_root / "pyproject.toml").read_text(encoding="utf-8")
    assert f'VERSION = "{version}"' in (repo_root / "nexus" / "config.py").read_text(encoding="utf-8")
    assert f'__version__ = "{version}"' in (repo_root / "nexusnet" / "__init__.py").read_text(encoding="utf-8")
    assert f'version="{version}"' in (repo_root / "setup.py").read_text(encoding="utf-8")


def test_first_run_setup_and_chat_ui_use_canonical_routes(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    first_run = client.post(
        "/first-run/save",
        json={
            "env": {
                "OLLAMA_BASE_URL": "http://127.0.0.1:11434",
                "OLLAMA_MODEL": "llama3.1",
                "VLLM_BASE_URL": "http://127.0.0.1:8001",
                "VLLM_MODEL": "local",
                "LIVE_ENGINES": "0",
            },
            "rag": {"enabled": True, "top_k": 3, "corpus_dir": "data/corpus/sample"},
        },
    )
    assert first_run.status_code == 200
    assert first_run.json()["ok"] is True
    assert (project_root / ".env").read_text(encoding="utf-8").count("OLLAMA_BASE_URL=") == 1
    assert "top_k: 3" in (project_root / "runtime" / "config" / "rag.yaml").read_text(encoding="utf-8")

    first_run_ui = Path("ui/first_run.html").read_text(encoding="utf-8")
    assert "/first-run/save" in first_run_ui

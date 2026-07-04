from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.runtime.quantization.catalog import QuantizationCatalog, QuantizationRecommendationRequest
from tests.test_nexus_phase1_foundation import make_project


def test_quantization_catalog_recommends_gguf_for_local_cpu_buyer_friendly_lanes():
    catalog = QuantizationCatalog.default()

    recommendation = catalog.recommend(
        QuantizationRecommendationRequest(
            request_id="quant::local-cpu",
            model_id="Qwen/Qwen3.5-7B",
            runtime_targets=["llama.cpp", "ollama", "lm-studio"],
            hardware_snapshot={"local_cpu": True, "local_gpu": False, "ram_gb": 64},
            objective="local_cpu_privacy",
            context_tokens=8192,
        )
    )

    assert recommendation["status_label"] == "LOCKED CANON"
    assert recommendation["authority"] == "NexusBrain"
    assert recommendation["selected_method"]["format"] == "GGUF"
    assert recommendation["selected_method"]["runtime_fit"]["llama.cpp"] == "native"
    assert "buyer_friendly_single_file" in recommendation["reason_codes"]
    assert recommendation["policy_scan"]["summary"]["allow_merge"] is True


def test_quantization_catalog_tracks_turboquant_as_shadow_kv_cache_candidate_not_weight_format():
    catalog = QuantizationCatalog.default()

    recommendation = catalog.recommend(
        {
            "request_id": "quant::long-context",
            "model_id": "open-model::long-context",
            "runtime_targets": ["vllm", "sglang"],
            "hardware_snapshot": {"local_gpu": True, "gpu_arch": "blackwell", "vram_gb": 48},
            "objective": "long_context_throughput",
            "context_tokens": 128000,
        }
    )

    assert recommendation["kv_cache_plan"]["selected_policy"] in {"fp8-kv-cache", "int8-kv-cache"}
    turbo = next(item for item in recommendation["kv_cache_plan"]["shadow_candidates"] if item["method_id"] == "turboquant-kv")
    assert turbo["status"] == "research-candidate"
    assert turbo["method_family"] == "KV-cache quantization"
    assert "benchmark_required" in turbo["promotion_gates"]
    assert "kv_cache_quantization" in recommendation["reason_codes"]


def test_quantization_catalog_blocks_promotion_from_upstream_runtime_gate():
    catalog = QuantizationCatalog.default()

    recommendation = catalog.recommend(
        {
            "request_id": "quant::blocked-runtime-gate",
            "model_id": "model::candidate",
            "runtime_targets": ["llama.cpp"],
            "hardware_snapshot": {"local_cpu": True, "local_gpu": False, "ram_gb": 32},
            "objective": "local_cpu_privacy",
            "context_tokens": 8192,
            "upstream_runtime_scorecard_gate": {
                "promotion_allowed": False,
                "status": "blocked",
                "blockers": ["secret_scan_passed", "support_bundle"],
                "source": "runtime_workload_scorecards",
            },
        }
    )

    assert recommendation["status"] == "blocked"
    assert recommendation["runtime_state"] == "degraded"
    assert recommendation["promotion_allowed"] is False
    assert "secret_scan_passed" in recommendation["promotion_blockers"]
    assert recommendation["upstream_runtime_scorecard_gate"]["promotion_allowed"] is False
    assert "quantization_catalog_blocks_runtime_scorecard_gate" in recommendation["reason_codes"]

    summary = catalog.scorecard()
    assert summary["runtime_state"] == "degraded"
    assert summary["blocked_count"] == 1
    assert summary["latest_recommendation"]["promotion_allowed"] is False


def test_quantization_catalog_api_blackbox_and_control_panel_surface(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/quantization-catalog/recommend",
        json={
            "request_id": "quant::api-local-gpu",
            "model_id": "Qwen/Qwen3.5-14B",
            "runtime_targets": ["vllm", "transformers"],
            "hardware_snapshot": {"local_gpu": True, "gpu_arch": "ada", "vram_gb": 16},
            "objective": "balanced_quality_latency",
            "context_tokens": 32768,
        },
    )
    assert response.status_code == 200
    recommendation = response.json()
    assert recommendation["selected_method"]["method_id"] in {"awq-w4a16", "gptq-w4a16", "fp8-w8a8"}

    summary = client.get("/ops/brain/quantization-catalog")
    assert summary.status_code == 200
    assert summary.json()["recommendation_count"] == 1

    scorecard = client.get("/ops/brain/canon/quantization-catalog")
    assert scorecard.status_code == 200
    scorecard_payload = scorecard.json()
    assert scorecard_payload["runtime_state"] == "live-bound"
    assert "turboquant_kv_shadow_lane" in scorecard_payload["required_controls"]

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "quantization-catalog-cockpit"})
    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    assert control_panel["quantization_catalog_scorecard"]["recommendation_count"] == 1

    blackbox = client.get("/ops/brain/canon/blackbox", params={"session_id": "quantization-catalog-cockpit"}).json()
    assert blackbox["scorecard_refs"]["quantization_catalog"] == "/ops/brain/canon/quantization-catalog"

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Quantization Catalog" in ui.text
    assert "quantizationCatalogScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderQuantizationCatalogScorecard" in app_js
    assert "/ops/brain/canon/quantization-catalog" in app_js
    assert "Quantization upstream runtime gate" in app_js

from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.runtime.workload_scorecards import RuntimeWorkloadScorecardRegistry, RuntimeWorkloadScorecardRequest
from tests.test_nexus_phase1_foundation import make_project


def test_runtime_workload_scorecard_records_measured_latency_cache_memory_and_cost():
    registry = RuntimeWorkloadScorecardRegistry()

    record = registry.record(
        RuntimeWorkloadScorecardRequest(
            scorecard_id="runtime-score::vllm-agentic-long-context",
            runtime_id="runtime::vllm-local",
            backend="vllm",
            model_id="open-model::long-context",
            workload_type="agent_loop",
            hardware_lane="local-gpu",
            quantization_policy="awq-w4a16-fp8-kv",
            context_tokens=128000,
            max_effective_context_tokens=96000,
            ttft_ms_p50=780,
            ttft_ms_p95=1240,
            itl_ms_p50=22,
            itl_ms_p95=38,
            tokens_per_sec_decode=91.4,
            throughput_tokens_per_sec=710.0,
            vram_gb=24,
            ram_gb=64,
            cache_bytes_gpu=8_589_934_592,
            cache_bytes_cpu=17_179_869_184,
            prefix_cache_hit_rate=0.74,
            kv_cache_hit_rate=0.66,
            batching_mode="continuous",
            cache_privacy_boundary="project",
            cost_per_1k_input=0.0,
            cost_per_1k_output=0.0,
            fallback_used=False,
            quality_delta=0.01,
            eval_refs=["eval::long-context-heldout"],
            trace_refs=["trace::runtime-vllm-agentic"],
            hardware_refs=["hardware::local-rtx"],
            cache_refs=["cache::long-context-turboquant"],
        )
    )

    assert record["status_label"] == "LOCKED CANON"
    assert record["authority"] == "NexusBrain"
    assert record["surface_id"] == "runtime-workload-scorecards"
    assert record["status"] == "measured"
    assert record["latency"]["ttft_ms_p95"] == 1240
    assert record["context"]["effective_context_ratio"] == 0.75
    assert record["cache"]["kv_cache_hit_rate"] == 0.66
    assert record["cost"]["owned_hardware"] is True
    assert record["policy_scan"]["summary"]["allow_merge"] is True


def test_runtime_workload_scorecard_blocks_private_shared_cache_or_missing_evidence():
    registry = RuntimeWorkloadScorecardRegistry()

    record = registry.record(
        {
            "scorecard_id": "runtime-score::unsafe-private-remote",
            "runtime_id": "runtime::remote-shared",
            "backend": "cloud",
            "model_id": "model::private",
            "workload_type": "research",
            "hardware_lane": "cloud-api",
            "quantization_policy": "unknown",
            "context_tokens": 64000,
            "max_effective_context_tokens": 80000,
            "ttft_ms_p50": 0,
            "ttft_ms_p95": 0,
            "itl_ms_p50": 0,
            "itl_ms_p95": 0,
            "tokens_per_sec_decode": 0.0,
            "throughput_tokens_per_sec": 0.0,
            "prefix_cache_hit_rate": 0.8,
            "kv_cache_hit_rate": 0.7,
            "batching_mode": "continuous",
            "cache_privacy_boundary": "remote-shared",
            "contains_private_data": True,
            "fallback_used": True,
            "fallback_reason": "",
            "eval_refs": [],
            "trace_refs": [],
            "hardware_refs": [],
        }
    )

    assert record["status"] == "blocked"
    assert record["runtime_state"] == "degraded"
    assert record["policy_scan"]["summary"]["allow_merge"] is False
    assert {
        "runtime_scorecard_private_shared_cache_blocked",
        "runtime_scorecard_requires_eval_refs",
        "runtime_scorecard_requires_trace_refs",
        "runtime_scorecard_requires_hardware_refs",
        "runtime_scorecard_effective_context_exceeds_raw",
        "runtime_scorecard_fallback_requires_reason",
    }.issubset({finding["rule_id"] for finding in record["scorecard_findings"]})


def test_runtime_workload_scorecard_blocks_upstream_productization_gate():
    registry = RuntimeWorkloadScorecardRegistry()

    record = registry.record(
        {
            "scorecard_id": "runtime-score::blocked-by-productization",
            "runtime_id": "runtime::local-llama",
            "backend": "llama.cpp",
            "model_id": "model::candidate",
            "workload_type": "chat",
            "hardware_lane": "local-cpu",
            "quantization_policy": "gguf-q4_k_m",
            "context_tokens": 32768,
            "max_effective_context_tokens": 24000,
            "ttft_ms_p50": 900,
            "ttft_ms_p95": 1500,
            "itl_ms_p50": 32,
            "itl_ms_p95": 55,
            "tokens_per_sec_decode": 38.5,
            "throughput_tokens_per_sec": 38.5,
            "ram_gb": 32,
            "prefix_cache_hit_rate": 0.2,
            "kv_cache_hit_rate": 0.15,
            "batching_mode": "none",
            "cache_privacy_boundary": "session",
            "eval_refs": ["eval::runtime"],
            "trace_refs": ["trace::runtime"],
            "hardware_refs": ["hardware::local"],
            "upstream_productization_gate": {
                "release_ready": False,
                "open_gates": ["secret_scan_passed", "support_bundle"],
                "source": "productization_readiness",
            },
        }
    )

    assert record["status"] == "blocked"
    assert record["runtime_state"] == "degraded"
    assert record["promotion_allowed"] is False
    assert "secret_scan_passed" in record["promotion_blockers"]
    assert record["upstream_productization_gate"]["release_ready"] is False
    assert "runtime_scorecard_blocks_productization_gate" in {
        finding["rule_id"] for finding in record["scorecard_findings"]
    }

    summary = registry.scorecard()
    assert summary["runtime_state"] == "degraded"
    assert summary["blocked_count"] == 1
    assert summary["latest_scorecard"]["promotion_allowed"] is False


def test_runtime_workload_scorecards_api_visualizer_blackbox_and_control_panel_surface(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/runtime-scorecards/records",
        json={
            "scorecard_id": "runtime-score::api-local",
            "runtime_id": "runtime::api-local",
            "backend": "llama.cpp",
            "model_id": "model::api-local",
            "workload_type": "chat",
            "hardware_lane": "local-cpu",
            "quantization_policy": "gguf-q4_k_m",
            "context_tokens": 32768,
            "max_effective_context_tokens": 24000,
            "ttft_ms_p50": 1100,
            "ttft_ms_p95": 1800,
            "itl_ms_p50": 42,
            "itl_ms_p95": 70,
            "tokens_per_sec_decode": 31.5,
            "throughput_tokens_per_sec": 31.5,
            "ram_gb": 32,
            "prefix_cache_hit_rate": 0.18,
            "kv_cache_hit_rate": 0.12,
            "batching_mode": "none",
            "cache_privacy_boundary": "session",
            "cost_per_1k_input": 0.0,
            "cost_per_1k_output": 0.0,
            "eval_refs": ["eval::api-chat"],
            "trace_refs": ["trace::api-runtime"],
            "hardware_refs": ["hardware::api-local-cpu"],
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "measured"

    summary = client.get("/ops/brain/runtime-scorecards")
    assert summary.status_code == 200
    assert summary.json()["scorecard_count"] == 1

    scorecard = client.get("/ops/brain/canon/runtime-scorecards")
    assert scorecard.status_code == 200
    scorecard_payload = scorecard.json()
    assert scorecard_payload["runtime_state"] == "live-bound"
    assert scorecard_payload["operator_actions"]["record"]["endpoint"] == "/ops/brain/runtime-scorecards/records"

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "runtime-scorecards-cockpit"})
    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    assert control_panel["runtime_workload_scorecards"]["scorecard_count"] == 1

    blackbox = client.get("/ops/brain/canon/blackbox", params={"session_id": "runtime-scorecards-cockpit"}).json()
    assert blackbox["scorecard_refs"]["runtime_workload_scorecards"] == "/ops/brain/canon/runtime-scorecards"

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Runtime Workload Scorecards" in ui.text
    assert "runtimeWorkloadScorecards" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderRuntimeWorkloadScorecards" in app_js
    assert "/ops/brain/canon/runtime-scorecards" in app_js
    assert "Runtime upstream productization gate" in app_js

from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.runtime.inference_architecture import InferenceArchitectureRegistry, InferenceArchitectureRequest
from tests.test_nexus_phase1_foundation import make_project


def test_inference_architecture_registry_selects_cache_and_batching_for_long_context_workloads():
    registry = InferenceArchitectureRegistry()

    plan = registry.plan(
        InferenceArchitectureRequest(
            plan_id="inference::long-context-research",
            workload_type="research",
            runtime_targets=["vllm", "lmcache"],
            context_tokens=128000,
            concurrent_sessions=32,
            latency_target_ms=1800,
            contains_private_data=False,
            cache_scope="project-local",
            hardware_snapshot={"local_gpu": True, "vram_gb": 48},
        )
    )

    assert plan["status_label"] == "LOCKED CANON"
    assert plan["authority"] == "NexusBrain"
    assert plan["status"] == "planned-shadow"
    assert plan["selected_strategy"]["speculative_decoding"] is True
    assert plan["selected_strategy"]["prefix_cache"] is True
    assert plan["selected_strategy"]["continuous_batching"] is True
    assert plan["selected_strategy"]["disaggregated_prefill_decode"] is True
    assert plan["selected_strategy"]["kv_reuse"] == "lmcache-compatible"
    assert "long_context_cache_economics" in plan["reason_codes"]
    assert plan["policy_scan"]["summary"]["allow_merge"] is True


def test_inference_architecture_registry_blocks_private_remote_shared_cache_without_sandbox():
    registry = InferenceArchitectureRegistry()

    plan = registry.plan(
        {
            "plan_id": "inference::private-remote-cache",
            "workload_type": "agentic",
            "runtime_targets": ["vllm", "lmcache"],
            "context_tokens": 64000,
            "concurrent_sessions": 8,
            "latency_target_ms": 1200,
            "contains_private_data": True,
            "cache_scope": "remote-shared",
            "hardware_snapshot": {"local_gpu": True, "vram_gb": 24},
        }
    )

    assert plan["status"] == "blocked"
    assert plan["selected_strategy"]["cache_scope"] == "remote-shared"
    assert "private_remote_cache_requires_sandbox_or_redaction" in {
        finding["rule_id"] for finding in plan["strategy_findings"]
    }
    assert plan["policy_scan"]["summary"]["allow_merge"] is False


def test_inference_architecture_blocks_upstream_cache_gate():
    registry = InferenceArchitectureRegistry()

    plan = registry.plan(
        {
            "plan_id": "inference::blocked-cache-gate",
            "workload_type": "agentic",
            "runtime_targets": ["vllm", "lmcache"],
            "context_tokens": 32768,
            "concurrent_sessions": 8,
            "latency_target_ms": 1500,
            "contains_private_data": False,
            "cache_scope": "project-local",
            "hardware_snapshot": {"local_gpu": True, "vram_gb": 24},
            "upstream_cache_gate": {
                "promotion_allowed": False,
                "status": "blocked",
                "blockers": ["cache_ledger_blocks_quantization_gate"],
                "source": "effective_context_cache_ledger",
            },
        }
    )

    assert plan["status"] == "blocked"
    assert plan["runtime_state"] == "degraded"
    assert plan["promotion_allowed"] is False
    assert "cache_ledger_blocks_quantization_gate" in plan["promotion_blockers"]
    assert plan["upstream_cache_gate"]["promotion_allowed"] is False
    assert "inference_architecture_blocks_cache_gate" in {finding["rule_id"] for finding in plan["strategy_findings"]}

    summary = registry.scorecard()
    assert summary["runtime_state"] == "degraded"
    assert summary["blocked_count"] == 1
    assert summary["latest_plan"]["promotion_allowed"] is False


def test_inference_architecture_api_blackbox_and_control_panel_surface(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/inference-architecture/plan",
        json={
            "plan_id": "inference::api-agentic",
            "workload_type": "agentic",
            "runtime_targets": ["sglang", "vllm"],
            "context_tokens": 32768,
            "concurrent_sessions": 16,
            "latency_target_ms": 1500,
            "contains_private_data": False,
            "cache_scope": "session-local",
            "hardware_snapshot": {"local_gpu": True, "vram_gb": 16},
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "planned-shadow"

    summary = client.get("/ops/brain/inference-architecture")
    assert summary.status_code == 200
    assert summary.json()["plan_count"] == 1

    scorecard = client.get("/ops/brain/canon/inference-architecture")
    assert scorecard.status_code == 200
    scorecard_payload = scorecard.json()
    assert scorecard_payload["runtime_state"] == "live-bound"
    assert "disaggregated_prefill_decode" in scorecard_payload["required_controls"]
    assert scorecard_payload["operator_actions"]["plan"]["endpoint"] == "/ops/brain/inference-architecture/plan"

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "inference-architecture-cockpit"})
    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    assert control_panel["inference_architecture_scorecard"]["plan_count"] == 1

    blackbox = client.get("/ops/brain/canon/blackbox", params={"session_id": "inference-architecture-cockpit"}).json()
    assert blackbox["scorecard_refs"]["inference_architecture"] == "/ops/brain/canon/inference-architecture"

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Inference Architecture" in ui.text
    assert "inferenceArchitectureScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderInferenceArchitectureScorecard" in app_js
    assert "/ops/brain/canon/inference-architecture" in app_js
    assert "Inference upstream cache gate" in app_js


def test_evolutionary_inference_foundation_is_runtime_visible_and_restart_safe(tmp_path):
    project_root = make_project(tmp_path)
    first_client = TestClient(create_app(str(project_root)))

    first_response = first_client.get("/ops/brain/canon/inference-architecture")

    assert first_response.status_code == 200
    first = first_response.json()["evolutionary_inference_foundation"]
    assert first["runtime_state"] == "live-evidence"
    assert first["policy_mutation_allowed"] is False
    assert set(first["primitive_ids"]) == {"portable.cpu-reference", "moe.selective-residency"}
    assert first["feasibility"]["status"] == "shadow-feasible"
    assert first["artifact_ref"] == "runtime/evolutionary-inference/foundation-v1.json"

    restarted_client = TestClient(create_app(str(project_root)))
    restarted = restarted_client.get("/ops/brain/canon/inference-architecture").json()[
        "evolutionary_inference_foundation"
    ]
    assert restarted["evidence_id"] == first["evidence_id"]
    assert restarted["host_fingerprint"] == first["host_fingerprint"]

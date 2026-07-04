from __future__ import annotations

import importlib

import pytest
from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


def _router_module():
    try:
        return importlib.import_module("nexusnet.runtime.inference_economy_router")
    except ModuleNotFoundError as exc:
        pytest.fail(f"inference economy router module is missing: {exc}")


def test_inference_economy_router_routes_local_only_after_excluding_system_and_developer_prompts(tmp_path):
    module = _router_module()
    router = module.InferenceEconomyRouter(artifacts_dir=tmp_path)

    decision = router.route(
        {
            "trace_id": "trace::local-short",
            "agent_id": "ao::front-desk",
            "messages": [
                {"role": "system", "content": "reasoning code formal logic " * 500},
                {"role": "developer", "content": "complex tools benchmarks " * 500},
                {"role": "user", "content": "hi"},
            ],
            "privacy_class": "local_only",
            "risk_level": "low",
            "max_tokens": 64,
        }
    )

    assert decision["status_label"] == "LOCKED CANON"
    assert decision["surface_id"] == "inference-economy-router"
    assert decision["tier"] == "simple"
    assert decision["provider"]["provider_id"] in {"ollama", "lmstudio", "llamacpp"}
    assert decision["privacy_gate"]["allow_cloud"] is False
    assert decision["privacy_gate"]["policy_order"] == "privacy-safety-before-cost"
    assert decision["scoring"]["roles_scored"] == ["user"]
    assert decision["scoring"]["message_window"] == 1
    assert decision["cost_ledger"]["raw_prompt_exported"] is False
    assert decision["cost_ledger"]["baseline_cost_usd"] >= decision["cost_ledger"]["estimated_cost_usd"]


def test_inference_economy_router_uses_specificity_before_complexity_and_builds_fallback_chain(tmp_path):
    module = _router_module()
    router = module.InferenceEconomyRouter(artifacts_dir=tmp_path)

    decision = router.route(
        module.InferenceRouteRequest(
            trace_id="trace::coding",
            agent_id="expert::coder",
            task_type=None,
            messages=[
                {
                    "role": "user",
                    "content": "Refactor this Python function, inspect the traceback, and write regression tests.",
                }
            ],
            tools=[{"name": "python.exec"}, {"name": "filesystem.read"}],
            max_tokens=2048,
            privacy_class="allow_cloud",
            risk_level="medium",
        )
    )

    assert decision["routing_order"][:5] == [
        "privacy_policy",
        "explicit_override",
        "policy_route",
        "specificity_route",
        "complexity_route",
    ]
    assert decision["specificity_category"] == "coding"
    assert decision["tier"] in {"complex", "reasoning"}
    assert "specificity::coding" in decision["reason_codes"]
    assert decision["fallback_policy"]["retry_on"] == [
        "timeout",
        "transport_error",
        "rate_limit",
        "provider_unavailable",
        "model_unavailable",
        "upstream_5xx",
    ]
    assert "safety_block" in decision["fallback_policy"]["do_not_retry_on"]
    assert decision["fallback_routes"]
    assert all(route["provider_id"] != decision["provider"]["provider_id"] or route["model_id"] != decision["model"]["model_id"] for route in decision["fallback_routes"])


def test_inference_economy_router_marks_trading_reasoning_routes_for_human_approval(tmp_path):
    module = _router_module()
    router = module.InferenceEconomyRouter(artifacts_dir=tmp_path)

    decision = router.route(
        {
            "trace_id": "trace::trading",
            "agent_id": "ao::finance",
            "messages": [{"role": "user", "content": "Analyze this trading strategy and decide whether to execute."}],
            "tools": [{"name": "broker.place_order"}],
            "privacy_class": "allow_cloud",
            "risk_level": "high",
        }
    )

    assert decision["specificity_category"] == "trading"
    assert decision["tier"] == "reasoning"
    assert decision["governance_gate"]["requires_human_approval"] is True
    assert decision["status"] == "blocked-pending-human-approval"
    assert "high_risk_requires_human_approval" in {finding["rule_id"] for finding in decision["route_findings"]}


def test_inference_economy_router_blocks_route_from_upstream_aitune_gate(tmp_path):
    module = _router_module()
    router = module.InferenceEconomyRouter(artifacts_dir=tmp_path)

    decision = router.route(
        module.InferenceRouteRequest(
            trace_id="trace::blocked-upstream",
            agent_id="ao::runtime",
            messages=[{"role": "user", "content": "Summarize the runtime status in one sentence."}],
            privacy_class="local_only",
            risk_level="low",
            upstream_aitune_gate={
                "status": "blocked-upstream-gate",
                "can_execute_here": False,
                "readiness_blockers": ["qes_runtime_backend_not_validated"],
            },
        )
    )

    assert decision["status"] == "blocked-upstream-gate"
    assert decision["runtime_state"] == "degraded"
    assert decision["upstream_aitune_gate"]["blockers"] == ["qes_runtime_backend_not_validated"]
    assert "upstream_aitune_gate_blocked" in decision["reason_codes"]
    assert "router_alignment_blocks_upstream_aitune_gate" in {
        finding["rule_id"] for finding in decision["route_findings"]
    }

    summary = router.summary()
    assert summary["runtime_state"] == "degraded"
    assert summary["blocked_count"] == 1
    assert summary["latest_decision"]["status"] == "blocked-upstream-gate"


def test_inference_economy_router_api_visualizer_blackbox_and_control_panel_surface(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/inference-economy-router/route",
        json={
            "trace_id": "trace::api-route",
            "agent_id": "ao::runtime",
            "messages": [{"role": "user", "content": "Summarize the current runtime status in one sentence."}],
            "privacy_class": "local_only",
            "risk_level": "low",
        },
    )
    assert response.status_code == 200
    assert response.json()["provider"]["location"] == "local"

    summary = client.get("/ops/brain/inference-economy-router")
    assert summary.status_code == 200
    assert summary.json()["decision_count"] == 1

    scorecard = client.get("/ops/brain/canon/inference-economy-router")
    assert scorecard.status_code == 200
    scorecard_payload = scorecard.json()
    assert scorecard_payload["runtime_state"] == "live-bound"
    assert scorecard_payload["operator_actions"]["route"]["endpoint"] == "/ops/brain/inference-economy-router/route"
    assert "Manifest" in scorecard_payload["control_panel_label"]

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "manifest-router-cockpit"})
    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    assert control_panel["inference_economy_router_scorecard"]["decision_count"] == 1

    blackbox = client.get("/ops/brain/canon/blackbox", params={"session_id": "manifest-router-cockpit"}).json()
    assert blackbox["scorecard_refs"]["inference_economy_router"] == "/ops/brain/canon/inference-economy-router"

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Inference Economy Router" in ui.text
    assert "inferenceEconomyRouterScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderInferenceEconomyRouterScorecard" in app_js
    assert "/ops/brain/canon/inference-economy-router" in app_js

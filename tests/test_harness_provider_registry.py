from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.agents.harnesses import HarnessProviderRegistry
from tests.test_nexus_phase1_foundation import make_project


def test_harness_provider_registry_scores_control_memory_sandbox_and_lockin():
    registry = HarnessProviderRegistry.default()

    summary = registry.summary()
    assert summary["status_label"] == "LOCKED CANON"
    assert summary["authority"] == "NexusBrain"
    assert summary["provider_count"] >= 6
    assert summary["promotion_boundary"] == "external-harnesses-remain-adapters-not-brain-authority"
    assert {"custom-code", "openai-agents-sdk", "langgraph-deep-agents", "claude-managed-agents"}.issubset(
        {provider["provider_id"] for provider in summary["providers"]}
    )

    recommendation = registry.recommend(
        {
            "use_case": "private-code-and-memory",
            "requires_self_hosting": True,
            "requires_memory_portability": True,
            "requires_sandbox_choice": True,
        }
    )
    assert recommendation["selected_provider"]["provider_id"] == "custom-code"
    assert recommendation["selected_provider"]["lock_in_risk"] == "low"
    assert "memory_portability" in recommendation["reason_codes"]
    assert recommendation["policy_scan"]["summary"]["allow_merge"] is True

    managed = next(provider for provider in summary["providers"] if provider["provider_id"] == "claude-managed-agents")
    assert managed["lock_in_risk"] == "high"
    assert managed["memory_portability"] == "provider-managed"
    assert "research-preview-features" in managed["caveats"]


def test_harness_provider_registry_blocks_recommendation_from_upstream_aitune_gate():
    registry = HarnessProviderRegistry.default()

    recommendation = registry.recommend(
        {
            "use_case": "regulated-local-agent",
            "requires_self_hosting": True,
            "requires_memory_portability": True,
            "requires_sandbox_choice": True,
            "upstream_aitune_gate": {
                "status": "blocked-upstream-gate",
                "can_execute_here": False,
                "readiness_blockers": ["provider_runtime_not_validated"],
            },
        }
    )

    assert recommendation["selected_provider"]["provider_id"] == "custom-code"
    assert recommendation["decision"] == "blocked"
    assert recommendation["runtime_state"] == "degraded"
    assert recommendation["upstream_aitune_gate"]["blockers"] == ["provider_runtime_not_validated"]
    assert "upstream_aitune_gate_blocked" in recommendation["reason_codes"]
    assert "router_alignment_blocks_upstream_aitune_gate" in recommendation["blocked_reasons"]
    assert recommendation["policy_scan"]["summary"]["allow_merge"] is False


def test_harness_provider_api_blackbox_and_control_panel_surface(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    summary = client.get("/ops/brain/harness-providers")
    assert summary.status_code == 200
    payload = summary.json()
    assert payload["provider_count"] >= 6

    recommendation = client.post(
        "/ops/brain/harness-providers/recommend",
        json={
            "use_case": "regulated-local-agent",
            "requires_self_hosting": True,
            "requires_memory_portability": True,
            "requires_sandbox_choice": True,
        },
    )
    assert recommendation.status_code == 200
    recommendation_payload = recommendation.json()
    assert recommendation_payload["selected_provider"]["provider_id"] == "custom-code"
    assert recommendation_payload["policy_scan"]["summary"]["allow_merge"] is True

    scorecard = client.get("/ops/brain/canon/harness-providers")
    assert scorecard.status_code == 200
    scorecard_payload = scorecard.json()
    assert scorecard_payload["runtime_state"] == "live-bound"
    assert "brain_hands_separation" in scorecard_payload["required_controls"]
    assert scorecard_payload["operator_actions"]["recommend"]["endpoint"] == "/ops/brain/harness-providers/recommend"

    blocked = client.post(
        "/ops/brain/harness-providers/recommend",
        json={
            "use_case": "regulated-local-agent",
            "requires_self_hosting": True,
            "requires_memory_portability": True,
            "requires_sandbox_choice": True,
            "upstream_aitune_gate": {
                "status": "blocked-upstream-gate",
                "can_execute_here": False,
                "readiness_blockers": ["provider_runtime_not_validated"],
            },
        },
    )
    assert blocked.status_code == 200
    assert blocked.json()["decision"] == "blocked"

    degraded_scorecard = client.get("/ops/brain/canon/harness-providers")
    assert degraded_scorecard.status_code == 200
    degraded_payload = degraded_scorecard.json()
    assert degraded_payload["runtime_state"] == "degraded"
    assert degraded_payload["blocked_count"] == 1
    assert degraded_payload["latest_recommendation"]["decision"] == "blocked"

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "harness-provider-cockpit"})
    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    assert control_panel["harness_provider_scorecard"]["provider_count"] >= 6
    assert control_panel["harness_provider_scorecard"]["runtime_state"] == "degraded"

    blackbox = client.get("/ops/brain/canon/blackbox", params={"session_id": "harness-provider-cockpit"}).json()
    assert blackbox["scorecard_refs"]["harness_providers"] == "/ops/brain/canon/harness-providers"

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Harness Provider Registry" in ui.text
    assert "harnessProviderScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderHarnessProviderScorecard" in app_js
    assert "/ops/brain/canon/harness-providers" in app_js

from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.browser import BrowserProfilePolicy, BrowserProfilePolicyRequest
from nexusnet.vision import OperatorEventRegistry, OperatorEventRequest
from tests.test_nexus_phase1_foundation import make_project


def test_browser_profile_policy_blocks_real_profile_by_default():
    policy = BrowserProfilePolicy()

    decision = policy.evaluate(
        BrowserProfilePolicyRequest(
            request_id="browser-profile::default",
            profile_mode="real_user_profile",
            session_scoped_permission=False,
            contains_private_data=True,
            provenance_ref="",
        )
    )

    assert decision["status"] == "blocked"
    assert "real_browser_profile_requires_session_permission" in {
        finding["rule_id"] for finding in decision["findings"]
    }
    assert decision["recommended_profile_mode"] == "nexus_owned_ephemeral"


def test_operator_event_registry_blocks_cross_operator_escalation():
    registry = OperatorEventRegistry()

    event = registry.record(
        OperatorEventRequest(
            event_id="operator-event::browser-to-terminal",
            run_id="operator-run::1",
            operator_kind="browser_operator",
            action_kind="terminal_command",
            permission_scope="browser_only",
            target_confidence=0.92,
            evidence_refs=["screenshot::1"],
            stop_window_ms=1500,
        )
    )

    assert event["status"] == "blocked"
    assert "operator_event_blocks_permission_escalation" in {finding["rule_id"] for finding in event["findings"]}
    assert event["receipt"]["rollback_available"] is False


def test_operator_event_registry_records_safe_browser_action():
    registry = OperatorEventRegistry()

    event = registry.record(
        {
            "event_id": "operator-event::browser-click",
            "run_id": "operator-run::2",
            "operator_kind": "browser_operator",
            "action_kind": "browser_click",
            "permission_scope": "browser_only",
            "target_confidence": 0.91,
            "evidence_refs": ["screenshot::button"],
            "stop_window_ms": 1500,
            "rollback_ref": "browser-history-back",
        }
    )

    assert event["status"] == "recorded"
    assert event["receipt"]["rollback_available"] is True
    assert event["event_stream_contract"] == "observation-plan-action-result-correction"


def test_operator_events_api(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    profile = client.post(
        "/ops/brain/browser/profile-policy",
        json={
            "request_id": "browser-profile::api",
            "profile_mode": "nexus_owned_ephemeral",
            "session_scoped_permission": False,
            "contains_private_data": False,
            "provenance_ref": "operator::api",
        },
    )
    assert profile.status_code == 200
    assert profile.json()["status"] == "allowed"

    event = client.post(
        "/ops/brain/operator-events",
        json={
            "event_id": "operator-event::api",
            "run_id": "operator-run::api",
            "operator_kind": "desktop_operator",
            "action_kind": "desktop_observe",
            "permission_scope": "desktop_observe_only",
            "target_confidence": 0.8,
            "evidence_refs": ["screenshot::api"],
            "stop_window_ms": 1000,
        },
    )
    assert event.status_code == 200
    assert event.json()["status"] == "recorded"

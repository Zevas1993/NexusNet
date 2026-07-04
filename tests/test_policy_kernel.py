from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.policy import PolicyKernel, PolicyWaiver
from tests.test_nexus_phase1_foundation import make_project


def test_policy_kernel_blocks_unsafe_targets_and_reports_merge_boundary():
    kernel = PolicyKernel.default()

    report = kernel.scan(
        [
            {
                "target_id": "training::private-adapter",
                "target_type": "training_candidate",
                "metadata": {"contains_private_data": True, "operator_approved": False},
            },
            {
                "target_id": "memory::unproven",
                "target_type": "memory_update",
                "metadata": {"provenance_refs": []},
            },
            {
                "target_id": "tool::shell-write",
                "target_type": "tool_execution",
                "metadata": {"sandboxed": False, "write_enabled": True},
            },
            {
                "target_id": "code::policy-kernel",
                "target_type": "code_change",
                "metadata": {"tests_provided": False, "codegraph_manifest_ref": "gitnexus::manifest::policy-test"},
            },
        ]
    )

    assert report.status_label == "LOCKED CANON"
    assert report.summary.allow_merge is False
    assert report.summary.hard_fail_count == 3
    assert report.summary.warning_count == 1
    assert report.summary.active_hard_fail_count == 3
    assert report.summary.active_warning_count == 1
    assert {
        "training_candidate_requires_operator_approval",
        "memory_update_requires_provenance",
        "write_tool_requires_sandbox",
        "code_change_requires_tests",
    } == {finding.rule_id for finding in report.findings}


def test_policy_kernel_waivers_require_auditable_metadata_and_expiry():
    kernel = PolicyKernel.default()
    future = datetime.now(timezone.utc) + timedelta(days=1)

    report = kernel.scan(
        [
            {
                "target_id": "code::docs-only",
                "target_type": "code_change",
                "metadata": {"tests_provided": False, "codegraph_manifest_ref": "gitnexus::manifest::docs-test"},
            }
        ],
        waivers=[
            PolicyWaiver(
                rule_id="code_change_requires_tests",
                target_id="code::docs-only",
                approved_by="NexusBrain",
                reason="Documentation-only candidate intake has no runtime behavior.",
                expires_at=future,
            )
        ],
    )

    assert report.summary.warning_count == 1
    assert report.summary.active_warning_count == 0
    assert report.summary.waived_count == 1
    assert report.summary.allow_merge is True
    assert report.findings[0].waived is True
    assert report.findings[0].waiver_ref == "waiver::code_change_requires_tests::code::docs-only"


def test_policy_kernel_api_exposes_rules_scan_and_canon_scorecard(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    rules_response = client.get("/ops/brain/policy/rules")
    assert rules_response.status_code == 200
    rules_payload = rules_response.json()
    assert rules_payload["status_label"] == "LOCKED CANON"
    assert rules_payload["rule_count"] >= 6
    assert "policy_scan" in rules_payload["operator_actions"]

    scan_response = client.post(
        "/ops/brain/policy/scan",
        json={
            "targets": [
                {
                    "target_id": "adapter::raw-session",
                    "target_type": "training_candidate",
                    "metadata": {"contains_private_data": True, "operator_approved": False},
                }
            ]
        },
    )
    assert scan_response.status_code == 200
    scan_payload = scan_response.json()
    assert scan_payload["summary"]["allow_merge"] is False
    assert scan_payload["summary"]["active_hard_fail_count"] == 1
    assert scan_payload["findings"][0]["rule_id"] == "training_candidate_requires_operator_approval"

    scorecard_response = client.get("/ops/brain/canon/policy-kernel")
    assert scorecard_response.status_code == 200
    scorecard = scorecard_response.json()
    assert scorecard["surface_id"] == "governance-observability"
    assert scorecard["authority"] == "NexusBrain"
    assert scorecard["policy_kernel_state"] == "live-bound"
    assert "deterministic_floor_under_agentic_work" in scorecard["required_controls"]
    assert scorecard["operator_actions"]["scan"]["endpoint"] == "/ops/brain/policy/scan"


def test_policy_kernel_is_visible_in_control_panel_and_blackbox(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "policy-kernel-cockpit"})
    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    policy_scorecard = control_panel["policy_kernel_scorecard"]
    assert policy_scorecard["policy_kernel_state"] == "live-bound"
    assert policy_scorecard["operator_actions"]["rules"]["endpoint"] == "/ops/brain/policy/rules"
    assert policy_scorecard["operator_actions"]["scan"]["endpoint"] == "/ops/brain/policy/scan"

    blackbox = client.get("/ops/brain/canon/blackbox", params={"session_id": "policy-kernel-cockpit"}).json()
    assert blackbox["scorecard_refs"]["policy_kernel"] == "/ops/brain/canon/policy-kernel"

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Policy Kernel" in ui.text
    assert "policyKernelScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderPolicyKernelScorecard" in app_js
    assert "/ops/brain/canon/policy-kernel" in app_js

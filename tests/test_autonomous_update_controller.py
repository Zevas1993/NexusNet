from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.core.autonomous_updates import AutonomousUpdateController, AutonomousUpdateRequest
from tests.test_nexus_phase1_foundation import make_project


def test_autonomous_update_controller_approves_shadow_when_all_gates_have_evidence():
    controller = AutonomousUpdateController()

    proposal = controller.propose(
        AutonomousUpdateRequest(
            update_id="update::quantization-shadow-v1",
            update_type="quantization",
            target_ref="quant::local-gpu-shadow",
            requested_state="shadow",
            eval_refs=["eval::quantization-held-out"],
            artifact_trust_refs=["artifact::qwen-awq-safetensors-trusted"],
            rollback_plan="runtime-architecture-shadow-rollback",
            monitoring_plan="latency-throughput-quality-cache-hit-monitor",
            operator_approved=True,
            sandbox_ref="sandbox::shadow-runtime",
            metadata={"source": "NEXUSNET_QUANTIZATION_AGENTIC_RESEARCH_EXPANSION_2026-04-28"},
        )
    )

    assert proposal["status_label"] == "LOCKED CANON"
    assert proposal["authority"] == "NexusBrain"
    assert proposal["status"] == "shadow-approved"
    assert proposal["promotion_state"] == "shadow-ready"
    assert proposal["requested_state"] == "shadow"
    assert proposal["gate_summary"]["all_required_gates_present"] is True
    assert proposal["policy_scan"]["summary"]["allow_merge"] is True
    assert proposal["update_findings"] == []
    assert {
        "eval_gate",
        "artifact_trust_gate",
        "rollback",
        "monitoring",
        "operator_approval",
        "sandbox",
    }.issubset(set(proposal["required_controls"]))


def test_autonomous_update_controller_blocks_promotion_without_required_gates():
    controller = AutonomousUpdateController()

    proposal = controller.propose(
        {
            "update_id": "update::unsafe-direct-adapter",
            "update_type": "adapter",
            "target_ref": "adapter::direct-weight-change",
            "requested_state": "active",
            "eval_refs": [],
            "artifact_trust_refs": [],
            "rollback_plan": "",
            "monitoring_plan": "",
            "operator_approved": False,
            "sandbox_ref": "",
        }
    )

    assert proposal["status"] == "blocked"
    assert proposal["promotion_state"] == "blocked-by-policy"
    assert {
        "autonomous_update_requires_eval_evidence",
        "autonomous_update_requires_artifact_trust",
        "autonomous_update_requires_operator_approval",
        "autonomous_update_requires_sandbox",
    }.issubset({finding["rule_id"] for finding in proposal["update_findings"]})
    assert proposal["policy_scan"]["summary"]["allow_merge"] is False
    assert "autonomous_update_requires_rollback" in {
        finding["rule_id"] for finding in proposal["policy_scan"]["findings"]
    }


def test_autonomous_update_controller_blocks_blocked_eval_lifecycle_gate():
    controller = AutonomousUpdateController()

    proposal = controller.propose(
        {
            "update_id": "update::blocked-eval-shadow",
            "update_type": "adapter",
            "target_ref": "student:blocked_growth_candidate",
            "requested_state": "shadow",
            "eval_refs": ["shadow-run::blocked-growth-lifecycle"],
            "artifact_trust_refs": ["artifact-trust::blocked-growth-replay"],
            "rollback_plan": "adapter-shadow-rollback",
            "monitoring_plan": "adapter-shadow-watch",
            "operator_approved": True,
            "sandbox_ref": "sandbox::blocked-growth-candidate",
            "upstream_eval_gate": {
                "promotion_allowed": False,
                "blockers": ["shadow_eval_blocks_growth_engine_gate"],
                "upstream_lifecycle_gate": {
                    "lifecycle_status": "closed_loop_blocked",
                    "growth_engine_gate_allowed": False,
                    "artifact_trust_promotion_allowed": False,
                    "blockers": ["growth_engine_adapter_training_gate_blocked"],
                },
            },
        }
    )

    assert proposal["status"] == "blocked"
    assert proposal["promotion_state"] == "blocked-by-policy"
    assert proposal["gate_summary"]["eval_promotion_gate"] is False
    assert proposal["upstream_eval_gate"]["promotion_allowed"] is False
    assert "growth_engine_adapter_training_gate_blocked" in proposal["upstream_eval_gate"]["blockers"]
    assert {
        "autonomous_update_blocks_eval_promotion_gate",
        "autonomous_update_blocks_upstream_lifecycle_gate",
    }.issubset({finding["rule_id"] for finding in proposal["update_findings"]})

    scorecard = controller.scorecard()
    assert scorecard["runtime_state"] == "degraded"
    assert scorecard["blocked_count"] == 1
    assert scorecard["latest_proposal"]["status"] == "blocked"


def test_autonomous_update_apply_safe_requires_release_wrapper_ao_guard(tmp_path: Path):
    project_root = make_project(tmp_path)
    probe = project_root / "tests" / "direct_apply_guard_probe_test.py"
    probe.parent.mkdir(parents=True, exist_ok=True)
    probe.write_text("def test_direct_apply_guard_probe():\n    assert True\n", encoding="utf-8")
    controller = AutonomousUpdateController(artifacts_dir=project_root / "runtime" / "artifacts")
    update_id = "update::direct-safe-apply-guard"
    controller.propose(
        {
            "update_id": update_id,
            "update_type": "prompt_policy",
            "target_ref": "safe-artifact::direct-safe-apply-guard",
            "requested_state": "proposal",
            "eval_refs": ["pytest::tests/direct_apply_guard_probe_test.py"],
            "artifact_trust_refs": ["signed-manifest::direct-safe-apply-guard"],
            "rollback_plan": "restore-previous-direct-apply-policy",
            "monitoring_plan": "direct-safe-apply-regression-watch",
        }
    )
    controller.approve(update_id, approved_by="admin", approval_ref="operator-review::direct-apply-guard")
    evidence = controller.run_sandbox_tests(
        update_id,
        command="pytest tests/direct_apply_guard_probe_test.py -q",
        project_root=project_root,
        timeout_seconds=30,
    )

    try:
        controller.apply_safe(update_id, test_evidence_refs=[evidence["evidence_ref"]])
    except ValueError as exc:
        assert "AO guard receipts required before safe apply" in str(exc)
    else:
        raise AssertionError("direct apply_safe without release-wrapper AO guard should be rejected")

    required_aos = ["AdminAO", "GovernanceAO", "SecurityAO", "EvalsAO"]
    guard = {
        "surface_id": "release-wrapper-ao-guard",
        "action": "apply",
        "passed": True,
        "required_aos": required_aos,
        "received_aos": required_aos,
        "receipt_refs": [f"aoexec::direct-apply::{ao_name}" for ao_name in required_aos],
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "receipts": [
            {
                "surface_id": "ao-execution-receipt",
                "execution_id": f"aoexec::direct-apply::{ao_name}",
                "ao_name": ao_name,
                "session_ref_digest": "directapplydigest",
                "direct_local_state_reads": [],
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
            }
            for ao_name in required_aos
        ],
    }
    applied = controller.apply_safe(
        update_id,
        test_evidence_refs=[evidence["evidence_ref"]],
        ao_guard=guard,
    )

    assert applied["status"] == "applied-shadow-safe-file"
    assert applied["ao_guard_required"] is True
    assert applied["ao_guard_passed"] is True
    assert set(applied["ao_guard_aos"]) == set(required_aos)
    assert set(applied["ao_guard_receipt_refs"]) == set(guard["receipt_refs"])
    assert applied["active_production_mutated"] is False


def test_autonomous_update_apply_safe_rejects_unbound_artifact_eval_replay(tmp_path: Path):
    project_root = make_project(tmp_path)
    probe = project_root / "tests" / "artifact_replay_probe_test.py"
    probe.parent.mkdir(parents=True, exist_ok=True)
    probe.write_text("def test_artifact_replay_probe():\n    assert True\n", encoding="utf-8")
    controller = AutonomousUpdateController(artifacts_dir=project_root / "runtime" / "artifacts")
    update_id = "update::artifact-bound-replay"
    gate_ref = "evals-ao-artifact::release-wrapper::trace_artifact_bound"
    suite_ref = "eval::release-wrapper-runtime::trace_artifact_bound"
    controller.propose(
        {
            "update_id": update_id,
            "update_type": "prompt_policy",
            "target_ref": "safe-artifact::release-wrapper-runtime::artifact-bound-replay",
            "requested_state": "proposal",
            "eval_refs": [gate_ref, suite_ref],
            "artifact_trust_refs": ["signed-manifest::artifact-bound-replay"],
            "rollback_plan": "restore-previous-artifact-bound-policy",
            "monitoring_plan": "artifact-bound-regression-watch",
            "metadata": {
                "source": "release-wrapper-runtime",
                "evals_ao_artifact_gate_ref": gate_ref,
                "evals_ao_eval_suite_id": suite_ref,
            },
        }
    )
    controller.approve(update_id, approved_by="admin", approval_ref="operator-review::artifact-bound")
    evidence = controller.run_sandbox_tests(
        update_id,
        command="pytest tests/artifact_replay_probe_test.py -q",
        project_root=project_root,
        timeout_seconds=30,
    )
    controller.attach_eval_replay(
        update_id,
        {
            "run_id": "shadow-run::forged-artifact-bound",
            "suite_id": suite_ref,
            "status": "passed-shadow",
            "promotion_allowed": True,
            "operator_approved": True,
            "evidence_refs": ["trace::unbound"],
            "metadata": {"source": "forged-replay"},
        },
    )

    try:
        controller.apply_safe(update_id, test_evidence_refs=[evidence["evidence_ref"]])
    except ValueError as exc:
        assert "artifact-backed passed shadow eval replay evidence" in str(exc)
    else:
        raise AssertionError("unbound artifact eval replay should be rejected before safe apply")
    scorecard = controller.scorecard()
    artifact_gate = scorecard["artifact_bound_replay_gate"]
    assert artifact_gate["status"] == "blocked"
    assert artifact_gate["required_count"] == 1
    assert artifact_gate["bound_replay_count"] == 0
    assert artifact_gate["missing_bound_replay_count"] == 1
    assert artifact_gate["latest_required_proposal"]["update_id"] == update_id
    assert artifact_gate["latest_required_proposal"]["required_artifact_gate_refs"] == [gate_ref]
    assert artifact_gate["latest_required_proposal"]["latest_replay_bound"] is False


def test_autonomous_update_api_blackbox_and_control_panel_surface(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/autonomous-updates/proposals",
        json={
            "update_id": "update::api-runtime-shadow",
            "update_type": "runtime",
            "target_ref": "inference::api-agentic",
            "requested_state": "shadow",
            "eval_refs": ["eval::api-runtime-regression"],
            "artifact_trust_refs": ["artifact::runtime-manifest-trusted"],
            "rollback_plan": "runtime-shadow-rollback",
            "monitoring_plan": "latency-quality-cost-watch",
            "operator_approved": True,
            "sandbox_ref": "sandbox::runtime-shadow",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "shadow-approved"

    summary = client.get("/ops/brain/autonomous-updates")
    assert summary.status_code == 200
    assert summary.json()["proposal_count"] == 1

    scorecard = client.get("/ops/brain/canon/autonomous-updates")
    assert scorecard.status_code == 200
    scorecard_payload = scorecard.json()
    assert scorecard_payload["runtime_state"] == "live-bound"
    assert scorecard_payload["operator_actions"]["propose"]["endpoint"] == "/ops/brain/autonomous-updates/proposals"
    assert "shadow_promote_monitor_rollback" in scorecard_payload["required_controls"]

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "autonomous-update-cockpit"})
    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    assert control_panel["autonomous_update_scorecard"]["proposal_count"] == 1

    blackbox = client.get("/ops/brain/canon/blackbox", params={"session_id": "autonomous-update-cockpit"}).json()
    assert blackbox["scorecard_refs"]["autonomous_updates"] == "/ops/brain/canon/autonomous-updates"

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Autonomous Updates" in ui.text
    assert "autonomousUpdatesScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderAutonomousUpdatesScorecard" in app_js
    assert "/ops/brain/canon/autonomous-updates" in app_js
    assert "upstream eval gate" in app_js
    assert "upstream_eval_gate" in app_js
    assert "Shadow eval replay evidence" in app_js
    assert "latest_eval_replay" in app_js


def test_autonomous_update_sandbox_copy_excludes_heavy_local_state(tmp_path: Path):
    project_root = make_project(tmp_path)
    probe = project_root / "tests" / "sandbox_copy_probe_test.py"
    probe.parent.mkdir(parents=True, exist_ok=True)
    probe.write_text("def test_sandbox_copy_probe():\n    assert True\n", encoding="utf-8")
    (project_root / "nexus").mkdir(parents=True, exist_ok=True)
    (project_root / "nexusnet").mkdir(parents=True, exist_ok=True)
    nested_memory = project_root / "nexus" / "memory" / "__init__.py"
    nested_memory.parent.mkdir(parents=True, exist_ok=True)
    nested_memory.write_text("class MemoryService:\n    pass\n", encoding="utf-8")
    research_source = project_root / "research" / "interpretability" / "guardrail_analysis.py"
    research_source.parent.mkdir(parents=True, exist_ok=True)
    research_source.write_text("class GuardrailAnalysisService:\n    pass\n", encoding="utf-8")
    heavy_paths = [
        project_root / "runtime" / "large-state.txt",
        project_root / ".codex" / "cache" / "blob.txt",
        project_root / ".codex-remote-attachments" / "blob.txt",
        project_root / ".pytest-tmp" / "worker" / "tmp.txt",
        project_root / "pytest-cache-files-demo" / "tmp.txt",
        project_root / "docs" / "large-canon.md",
        project_root / "data" / "local-state.bin",
        project_root / "patent" / "draft.bin",
        project_root / "large-unneeded-tree" / "blob.bin",
    ]
    for path in heavy_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x" * 1024, encoding="utf-8")

    controller = AutonomousUpdateController(artifacts_dir=project_root / "runtime" / "artifacts")
    controller.propose(
        {
            "update_id": "update::sandbox-copy-ignore-heavy-state",
            "update_type": "prompt_policy",
            "target_ref": "safe-artifact::sandbox-copy-ignore-heavy-state",
            "requested_state": "proposal",
            "eval_refs": ["pytest::tests/sandbox_copy_probe_test.py"],
            "artifact_trust_refs": ["signed-manifest::sandbox-copy-ignore-heavy-state"],
            "rollback_plan": "restore-previous-sandbox-copy-policy",
            "monitoring_plan": "sandbox-copy-policy-regression",
        }
    )
    controller.approve(
        "update::sandbox-copy-ignore-heavy-state",
        approved_by="admin",
        approval_ref="operator-review::sandbox-copy-policy",
    )

    evidence = controller.run_sandbox_tests(
        "update::sandbox-copy-ignore-heavy-state",
        command="pytest tests/sandbox_copy_probe_test.py -q",
        project_root=project_root,
        timeout_seconds=30,
    )
    manifest = json.loads(Path(evidence["pre_manifest_path"]).read_text(encoding="utf-8"))
    manifest_paths = {record["path"] for record in manifest["files"]}

    assert evidence["status"] == "passed"
    assert {"copy_seconds", "pre_manifest_seconds", "active_pre_manifest_seconds", "pytest_seconds"}.issubset(
        set(evidence["phase_timings"])
    )
    assert Path(evidence["phase_status_path"]).exists()
    assert evidence["sandbox"]["active_manifest_scope"] == "source-root-dirs-and-root-files"
    assert "docs/" in evidence["sandbox"]["active_manifest_excluded_prefixes"]
    assert "runtime/" in evidence["sandbox"]["active_manifest_excluded_prefixes"]
    assert "runtime/large-state.txt" not in manifest_paths
    assert ".codex/cache/blob.txt" not in manifest_paths
    assert ".codex-remote-attachments/blob.txt" not in manifest_paths
    assert ".pytest-tmp/worker/tmp.txt" not in manifest_paths
    assert "pytest-cache-files-demo/tmp.txt" not in manifest_paths
    assert "docs/large-canon.md" not in manifest_paths
    assert "data/local-state.bin" not in manifest_paths
    assert "patent/draft.bin" not in manifest_paths
    assert "large-unneeded-tree/blob.bin" not in manifest_paths
    assert "nexus/memory/__init__.py" in manifest_paths
    assert "research/interpretability/guardrail_analysis.py" in manifest_paths

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.genesis.core_objectives import GenesisCoreObjectivesLedgerService
from tests.test_nexus_phase1_foundation import make_project


def _govern_candidate(client: TestClient, *, candidate_ref: str, candidate_kind: str) -> dict:
    evaluated = client.post(
        "/ops/brain/genesis-immune-governance/candidates/evaluate",
        json={
            "candidate_ref": candidate_ref,
            "candidate_kind": candidate_kind,
            "command": "python -m pytest tests/test_hive_final_waves.py::test_immune_gate_attenuates_anomalies -q",
            "baseline_ref": f"baseline::{candidate_kind}",
            "rollback_proof_ref": f"rollback-proof::{candidate_kind}",
            "artifact_trust_ref": f"artifact-trust::{candidate_kind}",
            "eval_case_refs": [f"eval-case::{candidate_kind}"],
            "regression_suite_ref": "regression-suite::genesis-layer10-mutation-bindings",
            "judge_policy": {
                "human_review_required": True,
                "domain_check_required": True,
                "calibrated_judge_refs": ["judge::held-out-mutation-regression"],
            },
        },
    )
    assert evaluated.status_code == 200
    assert evaluated.json()["closed_sandbox_evidence"]["passed"] is True
    decided = client.post(
        f"/ops/brain/genesis-immune-governance/candidates/{evaluated.json()['candidate_id']}/decide",
        json={
            "decision": "approve",
            "approved_by": "layer10-binding-admin@example.invalid",
            "human_review_ref": f"human-review::{candidate_kind}",
            "domain_check_ref": f"domain-check::{candidate_kind}",
            "governance_ref": f"governance::{candidate_kind}",
        },
    )
    assert decided.status_code == 200
    assert decided.json()["promotion_allowed"] is True
    return decided.json()


def _ao_guard() -> dict:
    aos = ["AdminAO", "GovernanceAO", "SecurityAO", "EvalsAO"]
    return {
        "surface_id": "release-wrapper-ao-guard",
        "action": "apply",
        "passed": True,
        "required_aos": aos,
        "received_aos": aos,
        "receipt_refs": [f"aoexec::layer10-binding::{ao}" for ao in aos],
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "receipts": [
            {
                "surface_id": "ao-execution-receipt",
                "execution_id": f"aoexec::layer10-binding::{ao}",
                "ao_name": ao,
                "session_ref_digest": "layer10bindingdigest",
                "direct_local_state_reads": [],
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
            }
            for ao in aos
        ],
    }


def test_genesis_layer10_runs_real_closed_eval_quarantine_governance_and_replay(tmp_path: Path):
    project_root = make_project(tmp_path)
    private_admin = "immune-admin@example.invalid"
    client = TestClient(create_app(str(project_root)))

    initial = client.get("/ops/brain/genesis-immune-governance")
    assert initial.status_code == 200
    assert initial.json()["status"] == "live-awaiting-candidate-evidence"
    assert initial.json()["deny_by_default"] is True

    failed = client.post(
        "/ops/brain/genesis-immune-governance/candidates/evaluate",
        json={
            "candidate_ref": "node-change::unsafe-child",
            "candidate_kind": "permanent-expert-birth",
            "command": "python -m pytest tests/does_not_exist_layer10.py -q",
            "baseline_ref": "baseline::active-parent",
            "rollback_proof_ref": "rollback-proof::restore-active-parent",
            "artifact_trust_ref": "artifact-trust::unsafe-child",
            "eval_case_refs": ["eval-case::node-contract-regression"],
            "regression_suite_ref": "regression-suite::genesis-layer10",
            "judge_policy": {
                "human_review_required": True,
                "domain_check_required": True,
                "calibrated_judge_refs": ["judge::held-out-regression"],
            },
        },
    )
    assert failed.status_code == 200
    failed_packet = failed.json()
    assert failed_packet["status"] == "quarantined"
    assert failed_packet["closed_sandbox_evidence"]["executed"] is True
    assert failed_packet["closed_sandbox_evidence"]["passed"] is False
    assert failed_packet["closed_sandbox_evidence"]["shell_used"] is False
    assert failed_packet["closed_sandbox_evidence"]["active_project_source_mutated"] is False
    assert failed_packet["quarantine_packet"]["quarantine_active"] is True
    assert failed_packet["promotion_gate_packet"]["promotion_allowed"] is False
    assert failed_packet["rollback_proof"]["rollback_ready"] is True
    assert failed_packet["red_team_finding_receipt"]["finding_count"] >= 1

    denied = client.post(
        f"/ops/brain/genesis-immune-governance/candidates/{failed_packet['candidate_id']}/decide",
        json={
            "decision": "approve",
            "approved_by": private_admin,
            "human_review_ref": "human-review::unsafe-child",
            "domain_check_ref": "domain-check::unsafe-child",
            "governance_ref": "governance::unsafe-child",
        },
    )
    assert denied.status_code == 200
    assert denied.json()["status"] == "denied-quarantined"
    assert denied.json()["promotion_allowed"] is False

    passing = client.post(
        "/ops/brain/genesis-immune-governance/candidates/evaluate",
        json={
            "candidate_ref": "node-change::bounded-child",
            "candidate_kind": "permanent-expert-birth",
            "command": "python -m pytest tests/test_hive_final_waves.py::test_immune_gate_attenuates_anomalies -q",
            "baseline_ref": "baseline::active-parent",
            "rollback_proof_ref": "rollback-proof::restore-active-parent",
            "artifact_trust_ref": "artifact-trust::bounded-child",
            "eval_case_refs": ["eval-case::immune-anomaly-attenuation"],
            "regression_suite_ref": "regression-suite::genesis-layer10",
            "judge_policy": {
                "human_review_required": True,
                "domain_check_required": True,
                "calibrated_judge_refs": ["judge::held-out-regression"],
            },
        },
    )
    assert passing.status_code == 200
    passing_packet = passing.json()
    assert passing_packet["status"] == "sandbox-evaluated-awaiting-governance"
    assert passing_packet["closed_sandbox_evidence"]["passed"] is True
    assert passing_packet["promotion_gate_packet"]["promotion_allowed"] is False
    assert passing_packet["promotion_gate_packet"]["sandbox_eval_passed"] is True

    approved = client.post(
        f"/ops/brain/genesis-immune-governance/candidates/{passing_packet['candidate_id']}/decide",
        json={
            "decision": "approve",
            "approved_by": private_admin,
            "human_review_ref": "human-review::bounded-child",
            "domain_check_ref": "domain-check::bounded-child",
            "governance_ref": "governance::bounded-child",
        },
    )
    assert approved.status_code == 200
    approved_packet = approved.json()
    assert approved_packet["status"] == "approved-for-governed-promotion"
    assert approved_packet["promotion_allowed"] is True
    assert approved_packet["active_production_mutation_allowed"] is False
    assert approved_packet["governance_decision_packet"]["approver_digest"].startswith("sha256:")

    restarted = TestClient(create_app(str(project_root)))
    replay = restarted.get("/ops/brain/genesis-immune-governance").json()
    assert replay["status"] == "live-with-eval-and-governance-evidence"
    assert replay["evaluation_count"] == 2
    assert replay["quarantine_count"] == 1
    assert replay["governance_decision_count"] == 2
    assert replay["approved_promotion_count"] == 1

    control = restarted.get(
        "/ops/brain/visualizer/state",
        params={"session_id": "private-control-session"},
    ).json()["overlay_state"]["control_panel"]
    eval_page = next(page for page in control["pages"] if page["page_id"] == "eval-center")
    assert eval_page["state"] == "live"
    assert eval_page["metrics"]["immune_governance_status"] == replay["status"]
    assert eval_page["metrics"]["closed_sandbox_evaluation_count"] == 2
    assert control["genesis_immune_governance_status"]["approved_promotion_count"] == 1

    sanitized = json.dumps(
        {
            "failed": failed_packet,
            "denied": denied.json(),
            "passing": passing_packet,
            "approved": approved_packet,
            "replay": replay,
            "eval_page": eval_page,
        },
        sort_keys=True,
    )
    assert private_admin not in sanitized
    assert str(project_root) not in sanitized
    assert "artifact_path" not in sanitized
    assert "sandbox_workspace" not in sanitized


def test_genesis_core_objectives_blocks_score_gain_with_robustness_regression_and_replays(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    evaluated = client.post(
        "/ops/brain/genesis-immune-governance/candidates/evaluate",
        json={
            "candidate_ref": "node-change::quality-gain-robustness-loss",
            "candidate_kind": "permanent-expert-birth",
            "command": "python -m pytest tests/test_hive_final_waves.py::test_immune_gate_attenuates_anomalies -q",
            "baseline_ref": "baseline::core-objectives",
            "rollback_proof_ref": "rollback-proof::core-objectives",
            "artifact_trust_ref": "artifact-trust::core-objectives",
            "eval_case_refs": ["eval-case::core-objectives-robustness"],
            "regression_suite_ref": "regression-suite::core-objectives",
            "judge_policy": {
                "human_review_required": True,
                "domain_check_required": True,
                "calibrated_judge_refs": ["judge::core-objectives"],
            },
            "objective_metrics": {
                "baseline": {
                    "quality_score": 0.72,
                    "robustness_score": 0.91,
                    "safety_score": 0.96,
                    "privacy_score": 0.95,
                    "authority_score": 0.97,
                    "traceability_score": 0.93,
                },
                "candidate": {
                    "quality_score": 0.88,
                    "robustness_score": 0.44,
                    "safety_score": 0.96,
                    "privacy_score": 0.95,
                    "authority_score": 0.97,
                    "traceability_score": 0.93,
                },
            },
        },
    )
    assert evaluated.status_code == 200
    evaluated_packet = evaluated.json()
    assert evaluated_packet["status"] == "sandbox-evaluated-awaiting-governance"
    assert evaluated_packet["closed_sandbox_evidence"]["passed"] is True
    assert evaluated_packet["core_objectives"]["status"] == "blocked-robustness-regression"
    assert evaluated_packet["core_objectives"]["quality_improved"] is True
    assert evaluated_packet["core_objectives"]["robustness_regressed"] is True
    assert evaluated_packet["core_objectives"]["raw_metric_values_included"] is False
    assert evaluated_packet["promotion_gate_packet"]["core_objectives_shadow_allowed"] is False
    assert evaluated_packet["promotion_gate_packet"]["promotion_allowed"] is False

    denied = client.post(
        f"/ops/brain/genesis-immune-governance/candidates/{evaluated_packet['candidate_id']}/decide",
        json={
            "decision": "approve",
            "approved_by": "core-objectives-admin@example.invalid",
            "human_review_ref": "human-review::core-objectives",
            "domain_check_ref": "domain-check::core-objectives",
            "governance_ref": "governance::core-objectives",
        },
    )
    assert denied.status_code == 200
    denied_packet = denied.json()
    assert denied_packet["status"] == "denied-quarantined"
    assert denied_packet["promotion_allowed"] is False
    assert denied_packet["controls"]["core_objectives"] is False
    assert "core_objectives" in denied_packet["blockers"]
    assert denied_packet["active_production_mutated"] is False

    restarted = TestClient(create_app(str(project_root)))
    replay = restarted.get("/ops/brain/genesis-immune-governance").json()
    objectives = replay["core_objectives"]
    assert objectives["status"] == "live-with-core-objective-evidence"
    assert objectives["integrity_status"] == "valid-local-hmac-chain"
    assert objectives["robustness_regression_count"] == 1
    assert objectives["latest_assessment"]["status"] == "blocked-robustness-regression"

    control = restarted.get(
        "/ops/brain/visualizer/state",
        params={"session_id": "core-objectives-control-session"},
    ).json()["overlay_state"]["control_panel"]
    control_objectives = control["genesis_immune_governance_status"]["core_objectives"]
    assert control_objectives["integrity_status"] == "valid-local-hmac-chain"
    assert control_objectives["honest_status_label"] == "core-objectives-ledger-live-with-local-integrity-evidence"
    assert "quality_score" not in json.dumps(control_objectives, sort_keys=True)
    assert "robustness_score" not in json.dumps(control_objectives, sort_keys=True)

    sanitized = json.dumps({"evaluation": evaluated_packet, "decision": denied_packet, "replay": replay}, sort_keys=True)
    assert "core-objectives-admin@example.invalid" not in sanitized
    assert str(project_root) not in sanitized
    assert "quality_score" not in sanitized
    assert "robustness_score" not in sanitized


def test_genesis_core_objectives_fails_closed_when_integrity_history_is_tampered(tmp_path: Path):
    ledger = GenesisCoreObjectivesLedgerService(artifacts_dir=tmp_path / "artifacts")
    objective_metrics = {
        "baseline": {"quality_score": 0.72, "robustness_score": 0.91},
        "candidate": {"quality_score": 0.88, "robustness_score": 0.91},
    }
    ledger.assess(
        candidate_ref="candidate::integrity-baseline",
        candidate_kind="governed-safe-update",
        objective_metrics=objective_metrics,
    )
    history = ledger.history_path.read_text(encoding="utf-8")
    ledger.history_path.write_text(history.replace("aligned-with-declared-objective-metrics", "tampered-objective-status"), encoding="utf-8")

    assert ledger.summary()["integrity_status"] == "invalid-local-hmac-chain"
    with pytest.raises(RuntimeError, match="integrity history is invalid"):
        ledger.assess(
            candidate_ref="candidate::integrity-after-tamper",
            candidate_kind="governed-safe-update",
            objective_metrics=objective_metrics,
        )


def test_layer10_decisions_are_mandatory_and_scope_bound_across_mutation_lanes(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    services = client.app.state.services

    source_event = client.app.state.genesis_event_spine.publish_event(
        event_type="genesis.test.layer10.binding",
        source_surface_id="genesis-layer10-binding-test",
        correlation_ref="layer10-binding-event",
        privacy_label="sanitized-test-event",
        artifact_refs=["artifact::layer10-binding"],
        planes=["self_repair", "governance"],
    )
    proposal = client.app.state.genesis_self_repair.propose_from_event(
        {
            "event_ref": source_event["event_ref"],
            "target_ref": "genesis/safe-files/self-repair/layer10-binding.json",
            "repair_objective": "bind self repair to the immune governance decision",
        }
    )
    client.app.state.genesis_self_repair.sandbox_eval(
        proposal["proposal_id"],
        {
            "eval_cases": [
                {"case_id": "source-event-is-sanitized", "expected": "sanitized-event"},
                {"case_id": "safe-file-boundary", "expected": "genesis-safe-file"},
                {"case_id": "rollback-boundary", "expected": "rollback-required"},
            ],
            "artifact_trust_ref": "artifact-trust::self-repair-binding",
            "rollback_proof_ref": "rollback-proof::self-repair-binding",
        },
    )
    client.app.state.genesis_self_repair.approve(
        proposal["proposal_id"],
        {"approved_by": "self-repair-admin", "approval_ref": "approval::self-repair-binding"},
    )
    self_repair_apply_payload = {
        "test_results": [
            {
                "command": "python -m pytest tests/test_hive_final_waves.py -q",
                "passed": True,
                "failure_count": 0,
                "evidence_ref": "pytest::layer10-self-repair-binding",
            }
        ]
    }
    with pytest.raises(ValueError, match="immune governance decision"):
        client.app.state.genesis_self_repair.apply(proposal["proposal_id"], self_repair_apply_payload)
    self_repair_decision = _govern_candidate(
        client,
        candidate_ref=proposal["proposal_id"],
        candidate_kind="self-repair-safe-apply",
    )
    self_repair_apply = client.app.state.genesis_self_repair.apply(
        proposal["proposal_id"],
        {
            **self_repair_apply_payload,
            "immune_governance_decision_id": self_repair_decision["decision_id"],
        },
    )
    assert self_repair_apply["immune_governance_decision"]["scope_validated"] is True

    probe = project_root / "tests" / "layer10_autonomous_update_probe_test.py"
    probe.parent.mkdir(parents=True, exist_ok=True)
    probe.write_text("def test_layer10_autonomous_update_probe():\n    assert True\n", encoding="utf-8")
    update_id = "update::layer10-bound-safe-apply"
    services.brain_autonomous_updates.propose(
        {
            "update_id": update_id,
            "update_type": "prompt_policy",
            "target_ref": "safe-artifact::layer10-bound-safe-apply",
            "eval_refs": ["eval::layer10-bound-safe-apply"],
            "artifact_trust_refs": ["artifact-trust::layer10-bound-safe-apply"],
            "rollback_plan": "restore-layer10-bound-safe-file",
            "monitoring_plan": "layer10-bound-regression-watch",
        }
    )
    services.brain_autonomous_updates.approve(
        update_id,
        approval_evidence={
            "status": "approved",
            "approval_ref": "approval::layer10-update",
            "approval_subject": "release-wrapper-autonomous-update",
            "decision": "approved",
            "approved_update_id": update_id,
            "approver_digest": "sha256:layer10-admin",
            "rationale_digest": "sha256:layer10-update-approval",
            "metadata_digest": "sha256:layer10-update-metadata",
        },
    )
    sandbox = services.brain_autonomous_updates.run_sandbox_tests(
        update_id,
        command="pytest tests/layer10_autonomous_update_probe_test.py -q",
        project_root=project_root,
        timeout_seconds=30,
    )
    with pytest.raises(ValueError, match="immune governance decision"):
        services.brain_autonomous_updates.apply_safe(
            update_id,
            test_evidence_refs=[sandbox["evidence_ref"]],
            ao_guard=_ao_guard(),
        )
    update_decision = _govern_candidate(
        client,
        candidate_ref=update_id,
        candidate_kind="autonomous-update-safe-apply",
    )
    update_apply = services.brain_autonomous_updates.apply_safe(
        update_id,
        test_evidence_refs=[sandbox["evidence_ref"]],
        ao_guard=_ao_guard(),
        immune_governance_decision_id=update_decision["decision_id"],
    )
    assert update_apply["immune_governance_decision"]["candidate_ref"] == update_id

    birth_teacher_ids = ["layer10-birth-generator", "layer10-birth-verifier"]
    for teacher_id, role in zip(birth_teacher_ids, ["generator", "verifier"], strict=True):
        client.app.state.genesis_node_contracts.register_teacher_candidate(
            {
                "candidate_id": teacher_id,
                "model_or_tool_id": f"internal/{teacher_id}",
                "provider": "nexusnet-test-provider",
                "source_url": f"https://example.invalid/{teacher_id}",
                "candidate_status": "shadow",
                "teacher_roles": [role],
                "license_gate": "approved",
                "privacy_gate": "approved",
                "hardware_gate": "approved",
                "cost_gate": "approved",
                "eval_family": ["layer10-node-birth"],
                "domain_scope": ["research"],
                "risk_scope": ["high"],
                "source_refs": [f"teacher-source::{teacher_id}"],
                "benchmark_refs": [f"teacher-benchmark::{teacher_id}"],
            }
        )

    child = client.app.state.genesis_node_contracts.register_temporary_child(
        {
            "child_id": "layer10-bound-child",
            "parent_contract_ref": "expert-contract::researcher",
            "domain": "research",
            "risk_tier": "high",
            "teacher_ids": birth_teacher_ids,
            "capability_refs": ["capability::layer10-binding"],
            "source_refs": ["source::layer10-binding"],
        }
    )
    review_payload = {
        "decision": "retain-shadow",
        "sandbox_eval_ref": "sandbox-eval::layer10-child",
        "eval_refs": ["eval::layer10-child"],
        "rollback_plan_ref": "rollback::layer10-child",
        "governance_approval_ref": "governance::layer10-child",
        "admin_approval_ref": "admin::layer10-child",
    }
    with pytest.raises(ValueError, match="immune governance decision"):
        client.app.state.genesis_node_contracts.review_temporary_child("layer10-bound-child", review_payload)
    child_decision = _govern_candidate(
        client,
        candidate_ref=child["contract_ref"],
        candidate_kind="temporary-expert-retention",
    )
    reviewed = client.app.state.genesis_node_contracts.review_temporary_child(
        "layer10-bound-child",
        {**review_payload, "immune_governance_decision_id": child_decision["decision_id"]},
    )
    assert reviewed["immune_governance_decision"]["scope_validated"] is True

    retirement_ref = f"node-retirement::expert-contract::researcher::{child['contract_ref']}"
    retirement_payload = {
        "parent_contract_ref": "expert-contract::researcher",
        "replacement_contract_ref": child["contract_ref"],
        "sandbox_eval_ref": "sandbox-eval::layer10-retirement",
        "eval_refs": ["eval::layer10-retirement"],
        "rollback_plan_ref": "rollback::layer10-retirement",
        "archive_ref": "archive::layer10-retirement",
        "governance_approval_ref": "governance::layer10-retirement",
        "admin_approval_ref": "admin::layer10-retirement",
    }
    with pytest.raises(ValueError, match="scope mismatch"):
        client.app.state.genesis_node_contracts.retire_parent(
            {**retirement_payload, "immune_governance_decision_id": child_decision["decision_id"]}
        )
    retirement_decision = _govern_candidate(
        client,
        candidate_ref=retirement_ref,
        candidate_kind="parent-expert-retirement",
    )
    retired = client.app.state.genesis_node_contracts.retire_parent(
        {**retirement_payload, "immune_governance_decision_id": retirement_decision["decision_id"]}
    )
    assert retired["immune_governance_decision"]["candidate_ref"] == retirement_ref
    assert retired["active_production_mutated"] is True

    replay = TestClient(create_app(str(project_root))).get("/ops/brain/genesis-immune-governance").json()
    assert replay["approved_promotion_count"] == 4

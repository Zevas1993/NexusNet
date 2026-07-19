from __future__ import annotations

import hashlib
import json
from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.schemas import SessionContext
from tests.test_nexus_phase1_foundation import make_project


def _approve_layer10_node_candidate(client: TestClient, *, candidate_ref: str, candidate_kind: str) -> dict:
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
            "regression_suite_ref": "regression-suite::genesis-node-contracts",
            "judge_policy": {
                "human_review_required": True,
                "domain_check_required": True,
                "calibrated_judge_refs": ["judge::genesis-node-contract-held-out"],
            },
        },
    ).json()
    return client.post(
        f"/ops/brain/genesis-immune-governance/candidates/{evaluated['candidate_id']}/decide",
        json={
            "decision": "approve",
            "approved_by": "genesis-node-contract-immune-admin",
            "human_review_ref": f"human-review::{candidate_kind}",
            "domain_check_ref": f"domain-check::{candidate_kind}",
            "governance_ref": f"governance::{candidate_kind}",
        },
    ).json()


def _register_layer13_birth_teachers(client: TestClient, *, domain: str, risk_tier: str) -> list[str]:
    teacher_ids = [f"{domain}-birth-generator", f"{domain}-birth-verifier"]
    for teacher_id, role in zip(teacher_ids, ["generator", "verifier"], strict=True):
        response = client.post(
            "/ops/brain/genesis-teacher-governance/candidates",
            json={
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
                "eval_family": [f"{domain}-birth"],
                "domain_scope": [domain],
                "risk_scope": [risk_tier],
                "source_refs": [f"teacher-source::{teacher_id}"],
                "benchmark_refs": [f"teacher-benchmark::{teacher_id}"],
            },
        )
        assert response.status_code == 200
    return teacher_ids


def test_genesis_node_contracts_gate_live_routes_and_replay_child_retirement_lifecycle(tmp_path: Path):
    project_root = make_project(tmp_path)
    session_id = "genesis-node-contract-private-session"
    admin_identity = "node-contract-admin@example.invalid"
    client = TestClient(create_app(str(project_root)))

    initial = client.get(
        "/ops/brain/genesis-node-contracts",
        params={"session_id": session_id},
    )
    assert initial.status_code == 200
    summary = initial.json()
    assert summary["status"] == "live-contract-registry"
    assert summary["mother_brain_authority"] == "NexusBrain"
    assert summary["node_kind_counts"]["core"] >= 1
    assert summary["node_kind_counts"]["orchestrator"] >= 1
    assert summary["node_kind_counts"]["assistant_orchestrator"] >= 28
    assert summary["node_kind_counts"]["expert"] >= 19
    assert summary["complete_contract_count"] == summary["contract_count"]
    assert summary["route_receipt_count"] == 0

    unknown = client.post(
        "/ops/brain/genesis-node-contracts/routes/authorize",
        json={
            "session_id": session_id,
            "trace_ref": "trace::unknown-expert",
            "selected_ao": "ResearchAO",
            "selected_expert": "unregistered-secret-expert",
        },
    )
    assert unknown.status_code == 200
    denied = unknown.json()
    assert denied["status"] == "blocked-uncontracted-node"
    assert denied["route_allowed"] is False
    assert denied["blockers"] == ["expert_contract_missing"]
    assert denied["raw_content_included"] is False

    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": "Research current source evidence."}],
            "user": session_id,
        },
    )
    assert response.status_code == 200
    runtime = client.get(
        "/ops/wrapper/release-runtime",
        params={"session_id": session_id},
    ).json()
    trace_ref = f"trace::{runtime['latest_interaction']['trace_id']}"
    aos = client.get("/ops/brain/aos").json()
    receipt = next(
        item
        for item in aos["execution_receipts"]
        if item.get("trace_ref") == trace_ref
    )
    route_receipt = receipt["node_contract_route_receipt"]
    assert route_receipt["status"] == "route-authorized"
    assert route_receipt["route_allowed"] is True
    assert route_receipt["ao_contract_ref"] == "ao-contract::ResearchAO"
    assert route_receipt["expert_contract_ref"] == "expert-contract::researcher"
    assert route_receipt["active_production_mutation_allowed"] is False
    assert "artifact_path" not in receipt
    assert receipt["artifact_ref"].startswith("aos/execution-receipts/")
    persisted_ao_receipt_path = client.app.state.services.paths.artifacts_dir / receipt["artifact_ref"]
    persisted_ao_receipt = json.loads(persisted_ao_receipt_path.read_text(encoding="utf-8"))
    assert "artifact_path" not in persisted_ao_receipt
    assert str(project_root) not in json.dumps(persisted_ao_receipt)

    birth_teacher_ids = _register_layer13_birth_teachers(
        client,
        domain="research",
        risk_tier="high",
    )

    child_response = client.post(
        "/ops/brain/genesis-node-contracts/temporary-children",
        json={
            "child_id": "runtime-research-child",
            "parent_contract_ref": "expert-contract::researcher",
            "domain": "research",
            "risk_tier": "high",
            "teacher_ids": birth_teacher_ids,
            "capability_refs": ["capability::source-contradiction-research"],
            "source_refs": ["source::governed-child-request"],
        },
    )
    assert child_response.status_code == 200
    child = child_response.json()
    assert child["status"] == "shadow-awaiting-retention-review"
    assert child["lifecycle_state"] == "shadow"
    assert child["production_route_allowed"] is False
    assert child["retention_review_required"] is True

    missing_review = client.post(
        "/ops/brain/genesis-node-contracts/temporary-children/runtime-research-child/review",
        json={"decision": "retain-shadow"},
    )
    assert missing_review.status_code == 400
    assert "required" in missing_review.json()["detail"]
    child_decision = _approve_layer10_node_candidate(
        client,
        candidate_ref=child["contract_ref"],
        candidate_kind="temporary-expert-retention",
    )

    review = client.post(
        "/ops/brain/genesis-node-contracts/temporary-children/runtime-research-child/review",
        json={
            "decision": "retain-shadow",
            "sandbox_eval_ref": "sandbox-eval::child-retention",
            "eval_refs": ["eval::child-vs-parent"],
            "rollback_plan_ref": "rollback::child-retention",
            "governance_approval_ref": "governance::child-retention",
            "admin_approval_ref": "admin::child-retention",
            "approved_by": admin_identity,
            "immune_governance_decision_id": child_decision["decision_id"],
        },
    )
    assert review.status_code == 200
    retained = review.json()
    assert retained["status"] == "retention-reviewed-shadow"
    assert retained["production_route_allowed"] is False
    assert retained["permanent_birth_allowed"] is False

    child_route = client.post(
        "/ops/brain/genesis-node-contracts/routes/authorize",
        json={
            "session_id": session_id,
            "trace_ref": "trace::shadow-child",
            "selected_ao": "ResearchAO",
            "selected_expert": child["contract_ref"],
        },
    ).json()
    assert child_route["route_allowed"] is False
    assert child_route["blockers"] == ["expert_contract_not_active"]
    retirement_candidate_ref = f"node-retirement::expert-contract::researcher::{child['contract_ref']}"
    retirement_decision = _approve_layer10_node_candidate(
        client,
        candidate_ref=retirement_candidate_ref,
        candidate_kind="parent-expert-retirement",
    )

    retirement = client.post(
        "/ops/brain/genesis-node-contracts/retirements",
        json={
            "parent_contract_ref": "expert-contract::researcher",
            "replacement_contract_ref": child["contract_ref"],
            "sandbox_eval_ref": "sandbox-eval::parent-retirement",
            "eval_refs": ["eval::repeated-child-outperformance"],
            "rollback_plan_ref": "rollback::restore-researcher-parent",
            "archive_ref": "archive::researcher-parent-lineage",
            "governance_approval_ref": "governance::parent-retirement",
            "admin_approval_ref": "admin::parent-retirement",
            "approved_by": admin_identity,
            "immune_governance_decision_id": retirement_decision["decision_id"],
        },
    )
    assert retirement.status_code == 200
    retired = retirement.json()
    assert retired["status"] == "parent-archived-retired"
    assert retired["archive_not_delete"] is True
    assert retired["parent_contract_preserved"] is True
    assert retired["active_production_mutated"] is True

    parent = client.get(
        "/ops/brain/genesis-node-contracts/contract",
        params={"contract_ref": "expert-contract::researcher"},
    )
    assert parent.status_code == 200
    assert parent.json()["lifecycle_state"] == "archived-retired"
    assert parent.json()["archive_not_delete"] is True
    retired_route = client.post(
        "/ops/brain/genesis-node-contracts/routes/authorize",
        json={
            "session_id": session_id,
            "trace_ref": "trace::retired-parent",
            "selected_ao": "ResearchAO",
            "selected_expert": "researcher",
        },
    ).json()
    assert retired_route["route_allowed"] is False
    assert retired_route["blockers"] == ["expert_contract_not_active"]

    restored = client.post(
        "/ops/brain/genesis-node-contracts/retirements/restore",
        json={
            "parent_contract_ref": "expert-contract::researcher",
            "retirement_id": retired["retirement_id"],
            "governance_approval_ref": "governance::parent-restore",
            "admin_approval_ref": "admin::parent-restore",
            "approved_by": admin_identity,
        },
    )
    assert restored.status_code == 200
    assert restored.json()["status"] == "parent-active-restored"
    assert restored.json()["active_production_mutated"] is True
    restored_route = client.post(
        "/ops/brain/genesis-node-contracts/routes/authorize",
        json={
            "session_id": session_id,
            "trace_ref": "trace::restored-parent",
            "selected_ao": "ResearchAO",
            "selected_expert": "researcher",
        },
    ).json()
    assert restored_route["route_allowed"] is True

    restarted = TestClient(create_app(str(project_root)))
    replayed = restarted.get(
        "/ops/brain/genesis-node-contracts",
        params={"session_id": session_id},
    ).json()
    assert replayed["status"] == "live-contract-registry-with-lifecycle-evidence"
    assert replayed["temporary_child_count"] == 1
    assert replayed["retention_review_count"] == 1
    assert replayed["retirement_event_count"] == 1
    assert replayed["restoration_event_count"] == 1
    assert replayed["route_receipt_count"] >= 6

    replayed_aos = restarted.get("/ops/brain/aos").json()
    unified = replayed_aos["replay"]["unified_node_contract_registry"]
    assert unified["status"] == "live-contract-registry-with-lifecycle-evidence"
    control = restarted.get(
        "/ops/brain/visualizer/state",
        params={"session_id": session_id},
    ).json()["overlay_state"]["control_panel"]
    ao_page = next(page for page in control["pages"] if page["page_id"] == "ao-hive")
    assert ao_page["state"] == "live"
    assert ao_page["metrics"]["node_contract_registry_status"] == unified["status"]
    assert ao_page["metrics"]["node_contract_count"] == unified["contract_count"]
    assert ao_page["metrics"]["temporary_child_count"] == 1

    sanitized = json.dumps(
        {
            "summary": summary,
            "denied": denied,
            "route_receipt": route_receipt,
            "child": child,
            "retained": retained,
            "retired": retired,
            "restored": restored.json(),
            "replayed": replayed,
            "control_page": ao_page,
        },
        sort_keys=True,
    )
    assert session_id not in sanitized
    assert admin_identity not in sanitized
    assert "Research current source evidence" not in sanitized
    assert str(project_root) not in sanitized
    assert "F:\\" not in sanitized


def test_core_internal_expert_runtime_requires_persistent_node_contract_authorization(tmp_path: Path):
    project_root = make_project(tmp_path)
    session_id = "private-core-contract-session"
    raw_prompt = "Private runtime prompt that must never enter node contract evidence."
    app = create_app(str(project_root))
    client = TestClient(app)

    preview_response = client.get(
        "/ops/brain/core",
        params={"session_id": session_id, "expert": "researcher"},
    )
    assert preview_response.status_code == 200
    preview = preview_response.json()["native_execution_preview"]
    assert preview["node_contract_enforcement"]["status"] == "enforced"
    assert preview["node_contract_route_receipt"]["route_allowed"] is True
    assert preview["node_contract_route_receipt"]["selected_ao"] == "RouterAO"
    assert preview["node_contract_route_receipt"]["expert_contract_ref"] == "expert-contract::researcher"

    allowed_result = app.state.services.brain.generate(
        session_context=SessionContext(
            session_id=session_id,
            expert="researcher",
            use_retrieval=False,
        ),
        prompt=raw_prompt,
        model_hint="mock/default",
    )
    allowed_native = allowed_result.inference_trace.metrics["core_execution"]["native_execution"]
    allowed_receipt = allowed_native["node_contract_route_receipt"]
    expected_session_digest = "sha256:" + hashlib.sha256(session_id.encode("utf-8")).hexdigest()[:16]
    assert allowed_native["node_contract_enforcement"]["status"] == "enforced"
    assert allowed_receipt["route_allowed"] is True
    assert allowed_receipt["session_ref_digest"] == expected_session_digest
    assert allowed_receipt["trace_ref"] == f"trace::{allowed_result.trace_id}"

    blocked_result = app.state.services.brain.generate(
        session_context=SessionContext(
            session_id=session_id,
            expert="unregistered-private-expert",
            use_retrieval=False,
        ),
        prompt=raw_prompt,
        model_hint="mock/default",
    )
    blocked_native = blocked_result.inference_trace.metrics["core_execution"]["native_execution"]
    blocked_receipt = blocked_native["node_contract_route_receipt"]
    assert blocked_native["status_label"] == "BLOCKED NODE CONTRACT"
    assert blocked_native["enabled"] is False
    assert blocked_native["output_count"] == 0
    assert blocked_native["fallback_triggered"] is True
    assert "node_contract_route_blocked" in blocked_native["runtime_fallback_triggers"]
    assert blocked_receipt["route_allowed"] is False
    assert blocked_receipt["blockers"] == ["expert_contract_missing"]

    receipt_dir = project_root / "runtime" / "artifacts" / "genesis" / "node-contracts" / "route-receipts"
    persisted_receipts = [json.loads(path.read_text(encoding="utf-8")) for path in receipt_dir.glob("*.json")]
    assert len(persisted_receipts) >= 3
    persisted = json.dumps(persisted_receipts, sort_keys=True)
    assert session_id not in persisted
    assert raw_prompt not in persisted
    assert str(project_root) not in persisted
    assert "artifact_path" not in persisted

    restarted = TestClient(create_app(str(project_root)))
    replay = restarted.get(
        "/ops/brain/genesis-node-contracts",
        params={"session_id": session_id},
    ).json()
    assert replay["route_receipt_count"] == 2
    assert replay["latest_route_receipt"]["session_ref_digest"] == expected_session_digest

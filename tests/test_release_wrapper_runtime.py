from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.release_wrapper import (
    ReleaseWrapperRuntime,
    _build_nexusbrain_runtime_cycle_receipt,
    _release_wrapper_sandbox_command_for_project,
)
from tests.test_growth_lifecycle_orchestrator import lifecycle_request
from tests.test_nexus_phase1_foundation import make_project


CANON_CONTRACT_SOURCE_REFS = [
    "docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md",
    "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md",
    "docs/research/CANON_DEEP_DETAIL_ADDENDUM_2026-05-31.md",
    "docs/research/CANON_VS_ASSIMILATION_IMPROVEMENTS_2026-05-31.md",
    "docs/research/CANON_IMPLEMENTATION_LEDGER.md",
    "docs/assimilation/NEXUSNET_ALL_ASSIMILATION_TARGETS_CONSOLIDATED_2026-05-31.md",
    "docs/assimilation/FULL_CHAT_SPEC_TO_CURRENT_STATE_GAP_REPORT_2026-05-06.md",
]


def _complete_nexusbrain_cycle_interaction() -> dict:
    return {
        "trace_id": "trace-cycle-strictness",
        "session_ref_digest": "session-ref-digest",
        "source_model": "nexusnet-offline",
        "expert_node": "expert.coding",
        "knowledge_ref": "sha256:knowledge",
        "native_hive_heartbeat_id": "native-hive-heartbeat::cycle",
        "continuous_assimilation_capture_ref": "continuous-assimilation::capture",
        "global_growth_receipt_id": "global-growth::receipt",
        "federated_packet_id": "fed::packet",
        "federated_prior_update_id": "fed-prior::update",
        "production_spine_packet_signature": "production-spine::signature",
        "developmental_cortex_assessment_ref": "developmental-cortex::assessment",
        "developmental_cortex_growth_candidate_ref": "developmental-cortex::growth-candidate",
        "developmental_cortex_promotion_case_ref": "developmental-cortex::promotion-case",
        "authority_evidence_tool_governance": {
            "authority_decision_id": "authority::decision",
            "evidence_record_id": "evidence::record",
            "eval_federation_event_id": "eval-federation::event",
            "tool_action_plan_id": "tool-action::plan",
        },
        "improvement_queue_id": "improveq::cycle",
        "dream_research_episode_id": "dream-research-episode::cycle",
        "selected_ao": "EvalsAO",
        "ao_execution_receipt_id": "aoexec::cycle",
        "ao_execution_trace_ref": "trace::cycle",
        "canonical_ao_coverage": {
            "coverage_id": "canonical-ao-coverage::cycle",
            "passed": True,
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
        },
        "autonomous_update_proposal_id": "autonomous-update::proposal",
        "autonomous_update_lifecycle_run_id": "autonomous-update-lifecycle::run",
        "autonomous_update_lifecycle_update_id": "autonomous-update::proposal",
        "self_repair_governance_ref": "autonomous-update-proposal::proposal",
        "forward_pass_receipt_id": "fwpass::cycle",
        "cache_ledger_entry_id": "cache-ledger::cycle",
        "project_heartbeat_replay_ref": "release-wrapper-runtime/project-heartbeats.jsonl",
        "project_heartbeat_replay_record_id": "project-heartbeat-record::cycle",
    }


def test_nexusbrain_runtime_cycle_requires_canon_critical_stage_refs():
    missing_dream_episode = _complete_nexusbrain_cycle_interaction()
    missing_dream_episode["dream_research_episode_id"] = ""

    dream_receipt = _build_nexusbrain_runtime_cycle_receipt(missing_dream_episode)
    dream_stages = {stage["stage_id"]: stage for stage in dream_receipt["stages"]}

    assert dream_stages["dream_research"]["status"] == "degraded"
    assert dream_stages["dream_research"]["blocker"] == "dream_research_refs_missing"
    assert dream_receipt["status"] == "degraded"
    assert "dream_research_refs_missing" in dream_receipt["blockers"]

    missing_self_repair_lifecycle = _complete_nexusbrain_cycle_interaction()
    missing_self_repair_lifecycle["autonomous_update_lifecycle_run_id"] = ""
    missing_self_repair_lifecycle["autonomous_update_lifecycle_update_id"] = ""

    self_repair_receipt = _build_nexusbrain_runtime_cycle_receipt(missing_self_repair_lifecycle)
    self_repair_stages = {stage["stage_id"]: stage for stage in self_repair_receipt["stages"]}

    assert self_repair_stages["self_repair_update_governance"]["status"] == "degraded"
    assert (
        self_repair_stages["self_repair_update_governance"]["blocker"]
        == "self_repair_update_governance_refs_missing"
    )
    assert self_repair_receipt["status"] == "degraded"
    assert "self_repair_update_governance_refs_missing" in self_repair_receipt["blockers"]

    missing_project_heartbeat_replay = _complete_nexusbrain_cycle_interaction()
    missing_project_heartbeat_replay["project_heartbeat_replay_ref"] = ""
    missing_project_heartbeat_replay["project_heartbeat_replay_record_id"] = ""

    replay_receipt = _build_nexusbrain_runtime_cycle_receipt(missing_project_heartbeat_replay)
    replay_stages = {stage["stage_id"]: stage for stage in replay_receipt["stages"]}

    assert replay_stages["storage_replay"]["status"] == "degraded"
    assert replay_stages["storage_replay"]["blocker"] == "storage_replay_refs_missing"
    assert replay_receipt["status"] == "degraded"
    assert "storage_replay_refs_missing" in replay_receipt["blockers"]

    covered_replay_receipt = _build_nexusbrain_runtime_cycle_receipt(
        _complete_nexusbrain_cycle_interaction()
    )
    covered_replay_stages = {
        stage["stage_id"]: stage
        for stage in covered_replay_receipt["stages"]
    }

    assert covered_replay_stages["storage_replay"]["status"] == "covered"
    assert (
        "release-wrapper-runtime/project-heartbeats.jsonl"
        in covered_replay_stages["storage_replay"]["evidence_refs"]
    )
    assert "ao_runtime_governance" in covered_replay_receipt["required_stages"]
    assert covered_replay_stages["ao_runtime_governance"]["status"] == "covered"
    assert (
        "canonical-ao-coverage::cycle"
        in covered_replay_stages["ao_runtime_governance"]["evidence_refs"]
    )
    assert (
        "aoexec::cycle"
        in covered_replay_stages["ao_runtime_governance"]["evidence_refs"]
    )
    assert covered_replay_receipt["evidence_refs"]["canonical_ao_coverage_id"] == "canonical-ao-coverage::cycle"
    assert covered_replay_receipt["evidence_refs"]["ao_execution_receipt_id"] == "aoexec::cycle"

    missing_ao_runtime_governance = _complete_nexusbrain_cycle_interaction()
    missing_ao_runtime_governance["canonical_ao_coverage"] = {}
    missing_ao_runtime_governance["ao_execution_receipt_id"] = ""

    ao_receipt = _build_nexusbrain_runtime_cycle_receipt(missing_ao_runtime_governance)
    ao_stages = {stage["stage_id"]: stage for stage in ao_receipt["stages"]}

    assert ao_stages["ao_runtime_governance"]["status"] == "degraded"
    assert ao_stages["ao_runtime_governance"]["blocker"] == "ao_runtime_governance_refs_missing"
    assert ao_receipt["status"] == "degraded"
    assert "ao_runtime_governance_refs_missing" in ao_receipt["blockers"]


def _assert_whole_project_canon_contract_ledger(ledger: dict, project_root: Path) -> None:
    assert ledger["schema_version"] == "nexusnet-whole-project-canon-contract-ledger-v1"
    assert ledger["surface_id"] == "whole-project-canon-contract-ledger"
    assert ledger["status_label"] == "LOCKED CANON"
    assert ledger["product_scope"] == "whole-system"
    assert ledger["source_manifest"]["source_refs"] == CANON_CONTRACT_SOURCE_REFS
    assert ledger["source_manifest"]["source_count"] == len(CANON_CONTRACT_SOURCE_REFS)
    assert ledger["source_manifest"]["ingested_source_count"] == len(CANON_CONTRACT_SOURCE_REFS)
    assert ledger["source_manifest"]["missing_source_count"] == 0
    assert ledger["contract_count"] >= 12
    assert ledger["evidence_present_count"] >= 8
    assert ledger["coverage_status"] in {"partial", "covered"}
    assert ledger["raw_content_included"] is False
    assert ledger["active_production_mutation_allowed"] is False
    assert all(source["sha256"].startswith("sha256:") for source in ledger["source_manifest"]["sources"])
    assert all(source["byte_count"] > 0 for source in ledger["source_manifest"]["sources"])
    assert all(source["source_ref"] in CANON_CONTRACT_SOURCE_REFS for source in ledger["source_manifest"]["sources"])
    assert {source["resolved_from"] for source in ledger["source_manifest"]["sources"]} <= {"project-root", "repo-root"}
    serialized = json.dumps(ledger, sort_keys=True)
    assert str(project_root) not in serialized
    assert "F:\\" not in serialized
    assert "SECRET" not in serialized


def test_wrapper_product_surface_asset_is_not_gitignored():
    repo_root = Path(__file__).resolve().parents[1]

    check = subprocess.run(
        ["git", "check-ignore", "-q", "ui/wrapper/index.html"],
        cwd=repo_root,
        check=False,
    )

    assert check.returncode != 0


def test_release_wrapper_sandbox_command_falls_back_to_project_local_probe(tmp_path: Path):
    project_root = tmp_path / "project"
    project_root.mkdir()

    command = _release_wrapper_sandbox_command_for_project(
        project_root,
        (
            "pytest tests/test_release_wrapper_runtime.py::"
            "test_release_wrapper_status_card_is_lightweight_control_panel_surface_after_restart -q"
        ),
    )

    assert command == "pytest tests/release_wrapper_auto_sandbox_probe_test.py -q"
    probe = project_root / "tests" / "release_wrapper_auto_sandbox_probe_test.py"
    assert probe.exists()
    assert "test_release_wrapper_auto_sandbox_probe" in probe.read_text(encoding="utf-8")


def test_root_boots_to_release_wrapper_entrypoint(tmp_path: Path):
    client = TestClient(create_app(str(make_project(tmp_path))))

    response = client.get("/", follow_redirects=False)

    assert response.status_code in {302, 307}
    assert response.headers["location"] == "/ui/wrapper/"


def test_chat_turn_updates_release_wrapper_growth_federation_and_update_proposal(tmp_path: Path):
    project = make_project(tmp_path)
    client = TestClient(create_app(str(project)))
    client.app.state.release_wrapper_runtime.hardware_scanner = _BoundedContextHardwareScanner()
    configured = client.post(
        "/ops/wrapper/release-health-heartbeat/supervisor/configure",
        json={
            "session_id": "release-user-a",
            "enabled": True,
            "interval_seconds": 1,
            "max_pulses_per_tick": 1,
            "schedule_immediately": True,
            "configured_by": "admin",
        },
    )
    assert configured.status_code == 200
    assert configured.json()["status"] == "enabled"

    chat = client.post(
        "/chat",
        json={
            "session_id": "release-user-a",
            "message": "Write a small Python function that adds two numbers.",
            "rag": False,
            "wrapper_mode": "standard-chat",
        },
    )

    assert chat.status_code == 200
    assert chat.json()["ok"] is True
    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": "release-user-a"})
    assert runtime.status_code == 200
    payload = runtime.json()
    assert payload["surface_id"] == "release-wrapper-runtime"
    assert payload["entrypoint"]["boot_target"] == "/ui/wrapper/"
    assert payload["entrypoint"]["runtime_state"] == "live-bound"
    assert payload["continuous_assimilation"]["nodes"]
    assert payload["global_growth"]["users"] >= 1
    assert payload["global_growth"]["global_captures"] >= 2
    assert payload["federated_packet_count"] == 1
    assert payload["latest_federated_packet"]["raw_content_included"] is False
    assert payload["latest_federated_packet"]["contains_personal_data"] is False
    assert payload["latest_federated_packet"]["security_envelope"]["signed_packet"]["raw_private_data_exported"] is False
    assert payload["production_spine"]["packet_count"] == 1
    production_packet = payload["production_spine"]["latest_packet"]
    assert production_packet["status"] == "accepted_sanitized_packet"
    assert production_packet["raw_content_included"] is False
    assert production_packet["contains_personal_data"] is False
    assert production_packet["packet_signature"].startswith("sha256:")
    assert production_packet["shadow_routing_influence"]["active_route_mutation_allowed"] is False
    assert payload["latest_interaction"]["production_spine_packet_signature"] == production_packet["packet_signature"]
    heartbeat = payload["native_hive_heartbeat"]
    assert heartbeat["surface_id"] == "release-wrapper-native-hive-heartbeat"
    assert heartbeat["status"] == "covered"
    assert heartbeat["session_ref_digest"] == payload["latest_interaction"]["session_ref_digest"]
    assert heartbeat["trace_ref"] == f"trace::{payload['latest_interaction']['trace_id']}"
    assert heartbeat["hive_run_ref"] == f"hive-forward::{payload['latest_interaction']['hive_run_id']}"
    assert heartbeat["raw_content_included"] is False
    assert heartbeat["active_production_mutation_allowed"] is False
    assert heartbeat["active_production_mutated"] is False
    assert set(heartbeat["required_organs"]) == {
        "neural_bus",
        "hive_blackboard",
        "plane_trace",
        "federated_learning_packet",
        "federated_prior_update",
        "runtime_growth_receipt",
        "dream_research_queue",
    }
    heartbeat_organs = {organ["organ_id"]: organ for organ in heartbeat["organs"]}
    assert heartbeat_organs["neural_bus"]["status"] == "covered"
    assert heartbeat_organs["hive_blackboard"]["status"] == "covered"
    assert heartbeat_organs["plane_trace"]["status"] == "covered"
    assert heartbeat_organs["federated_learning_packet"]["status"] == "covered"
    assert heartbeat_organs["federated_prior_update"]["status"] == "covered"
    assert heartbeat_organs["runtime_growth_receipt"]["status"] == "covered"
    assert heartbeat_organs["dream_research_queue"]["status"] == "covered"
    assert heartbeat["covered_count"] == len(heartbeat["required_organs"])
    assert heartbeat["degraded_count"] == 0
    assert payload["latest_interaction"]["native_hive_heartbeat_id"] == heartbeat["heartbeat_id"]
    project_heartbeat = payload["project_heartbeat"]
    assert project_heartbeat["surface_id"] == "nexusnet-project-heartbeat"
    assert project_heartbeat["status"] == "alive"
    assert project_heartbeat["raw_content_included"] is False
    assert project_heartbeat["active_production_mutation_allowed"] is False
    assert project_heartbeat["active_production_mutated"] is False
    assert payload["latest_interaction"]["project_heartbeat_id"] == project_heartbeat["heartbeat_id"]
    assert payload["latest_interaction"]["project_heartbeat_source_run_id"] == project_heartbeat["source_run_id"]
    coverage = payload["forward_pass_coverage"]
    assert coverage["surface_id"] == "release-wrapper-forward-pass-coverage"
    assert coverage["receipt_count"] == 1
    assert coverage["covered_count"] == 6
    assert coverage["degraded_count"] == 0
    receipt = coverage["latest_receipt"]
    assert receipt["surface_id"] == "release-wrapper-forward-pass-receipt"
    assert receipt["session_ref_digest"] == payload["latest_interaction"]["session_ref_digest"]
    assert receipt["trace_ref"] == f"trace::{payload['latest_interaction']['trace_id']}"
    assert receipt["raw_content_included"] is False
    assert receipt["active_production_mutation_allowed"] is False
    assert set(receipt["required_stages"]) == {
        "continuous_assimilation",
        "global_growth",
        "federated_packet",
        "production_spine",
        "developmental_cortex",
        "dream_research_queue",
    }
    stages = {stage["stage_id"]: stage for stage in receipt["stages"]}
    assert stages["developmental_cortex"]["status"] == "covered"
    assert stages["dream_research_queue"]["status"] == "covered"
    assert any(ref.startswith("developmental-cortex::") for ref in stages["developmental_cortex"]["evidence_refs"])
    assert any(ref.startswith("dream-research-queue::") for ref in stages["dream_research_queue"]["evidence_refs"])
    assert all(stage["status"] == "covered" for stage in receipt["stages"])
    assert payload["latest_interaction"]["forward_pass_receipt_id"] == receipt["receipt_id"]
    canon_receipts = payload["canon_contract_receipts"]
    assert canon_receipts["surface_id"] == "whole-project-canon-contract-receipts"
    assert canon_receipts["receipt_count"] == 1
    assert canon_receipts["latest_status"] in {"partial", "covered"}
    canon_receipt = canon_receipts["latest_receipt"]
    assert canon_receipt["schema_version"] == "nexusnet-whole-project-canon-contract-receipt-v1"
    assert canon_receipt["surface_id"] == "whole-project-canon-contract-receipt"
    assert canon_receipt["trace_ref"] == f"trace::{payload['latest_interaction']['trace_id']}"
    assert canon_receipt["forward_pass_receipt_id"] == receipt["receipt_id"]
    assert canon_receipt["ledger"]["source_count"] == len(CANON_CONTRACT_SOURCE_REFS)
    assert canon_receipt["ledger"]["ingested_source_count"] == len(CANON_CONTRACT_SOURCE_REFS)
    assert canon_receipt["contract_count"] == payload["canon_contract_ledger"]["contract_count"]
    canon_contracts = {contract["contract_id"]: contract for contract in payload["canon_contract_ledger"]["contracts"]}
    assert canon_contracts["context-cache-truth"]["status"] == "evidence-present"
    assert not [gap for gap in canon_receipt["gaps"] if gap["contract_id"] == "context-cache-truth"]
    assert canon_receipt["raw_content_included"] is False
    assert canon_receipt["active_production_mutation_allowed"] is False
    assert payload["latest_interaction"]["canon_contract_receipt_id"] == canon_receipt["receipt_id"]
    assert (
        payload["dream_research_queue"]["latest_item"]["metadata"]["canon_contract_receipt_id"]
        == canon_receipt["receipt_id"]
    )
    automatic_repair_plan = payload["latest_interaction"]["release_health_automatic_repair_plan"]
    assert automatic_repair_plan["status"] == "completed-heartbeat-supervisor-repair"
    assert automatic_repair_plan["lifecycle_status"] == "completed"
    assert automatic_repair_plan["actions"]["admin_approval"]["status"] == "admin-approved"
    assert automatic_repair_plan["actions"]["sandbox_tests"]["status"] == "passed"
    assert automatic_repair_plan["actions"]["apply"]["status"] == "applied-shadow-safe-file"
    assert automatic_repair_plan["actions"]["rollback"]["status"] == "rolled-back"
    assert automatic_repair_plan["subsystem_repair_envelope_count"] >= 1
    assert automatic_repair_plan["active_production_mutation_allowed"] is False
    assert automatic_repair_plan["active_production_mutated"] is False
    assert automatic_repair_plan["raw_content_included"] is False
    repair_history = payload["release_health_heartbeat_supervisor"]["repair_history"]
    assert repair_history["status"] == "recorded"
    assert repair_history["latest_status"] == "completed-heartbeat-supervisor-repair"
    assert repair_history["latest_run_id"] == automatic_repair_plan["run_id"]
    assert repair_history["latest_subsystem_repair_envelope_count"] == (
        automatic_repair_plan["subsystem_repair_envelope_count"]
    )
    latest_repair = repair_history["repairs"][-1]
    assert latest_repair["action_statuses"] == {
        "admin_approval": "admin-approved",
        "shadow_eval_replay": "passed-shadow",
        "sandbox_tests": "passed",
        "apply": "applied-shadow-safe-file",
        "rollback": "rolled-back",
    }
    latest_envelope = repair_history["latest_subsystem_repair_envelopes"][0]
    assert latest_envelope["honest_status_label"] == "completed-shadow-safe-file-rollback-verified"
    assert latest_envelope["admin_approval_ref"] == "operator-review::automatic-wrapper-interaction-repair"
    assert latest_envelope["raw_content_included"] is False
    assert latest_envelope["active_production_mutation_allowed"] is False
    assert latest_envelope["active_production_mutated"] is False
    matrix = payload["whole_system_forward_pass_enforcement_matrix"]
    wrapper_row = {
        row["entrypoint_id"]: row for row in matrix["entrypoints"]
    }["wrapper_model_interaction"]
    assert "dream_research_queue" in matrix["required_capability_columns"]
    assert wrapper_row["capabilities"]["developmental_release_contract"] == "covered"
    assert wrapper_row["capabilities"]["dream_research_queue"] == "covered"
    assert any(ref.startswith("dream-research-queue::") for ref in wrapper_row["evidence_refs"])
    assert payload["effective_context_cache"]["entry_count"] == 1
    latest_cache = payload["effective_context_cache"]["latest_entry"]
    assert latest_cache["surface_id"] == "effective-context-cache-ledger"
    assert latest_cache["status"] == "measured"
    assert latest_cache["promotion_allowed"] is True
    assert latest_cache["context_economics"]["raw_context_tokens"] > 0
    assert latest_cache["context_economics"]["effective_context_tokens"] > 0
    assert latest_cache["metadata"]["source"] == "release-wrapper-runtime"
    assert latest_cache["metadata"]["raw_content_included"] is False
    assert latest_cache["metadata"]["federated_packet_id"] == payload["latest_interaction"]["federated_packet_id"]
    assert payload["latest_interaction"]["cache_ledger_entry_id"] == latest_cache["entry_id"]
    context_posture = payload["context_window_posture"]
    assert context_posture["surface_id"] == "release-wrapper-context-window-posture"
    assert context_posture["canon_min_context_tokens"] == 1_000_000
    assert context_posture["status"] == "measured-below-canon-minimum"
    assert context_posture["achieved_canon_minimum"] is False
    assert context_posture["latest_cache_entry_id"] == latest_cache["entry_id"]
    assert context_posture["observed_effective_context_tokens"] == latest_cache["context_economics"]["effective_context_tokens"]
    assert context_posture["raw_content_included"] is False
    assert context_posture["active_production_mutation_allowed"] is False
    capability = payload["context_capability_envelope"]
    assert capability["surface_id"] == "release-wrapper-context-capability-envelope"
    assert capability["canon_min_context_tokens"] == 1_000_000
    assert capability["host_context_cap_tokens"] == 262_144
    assert capability["canon_target_status"] == "blocked-by-host-cap"
    assert capability["promotion_allowed"] is False
    assert capability["hardware_backed"] is True
    assert capability["latest_cache_entry_id"] == latest_cache["entry_id"]
    assert capability["latest_runtime_scorecard_id"] == payload["latest_interaction"]["runtime_scorecard_id"]
    assert "host_context_cap_below_canon_minimum" in capability["blockers"]
    assert capability["raw_content_included"] is False
    assert capability["active_production_mutation_allowed"] is False
    runtime_scorecards = client.get("/ops/brain/runtime-scorecards").json()
    latest_runtime_scorecard = runtime_scorecards["latest_scorecard"]
    assert runtime_scorecards["scorecard_count"] == 1
    assert latest_runtime_scorecard["scorecard_id"] == capability["latest_runtime_scorecard_id"]
    assert latest_runtime_scorecard["status"] == "measured"
    assert latest_runtime_scorecard["metadata"]["hardware_max_context_tokens"] == 262_144
    cache_summary = client.get("/ops/brain/cache-ledger").json()
    assert cache_summary["entry_count"] == 1
    assert cache_summary["latest_entry"]["entry_id"] == latest_cache["entry_id"]
    runtime_decisions = client.get("/ops/brain/canon/runtime-decision-ledger").json()
    assert runtime_decisions["decision_count"] == 1
    latest_runtime_decision = runtime_decisions["latest_decision"]
    assert latest_runtime_decision["surface_id"] == "runtime-decision-ledger"
    assert latest_runtime_decision["status"] == "ready-shadow"
    assert latest_runtime_decision["promotion_allowed"] is True
    assert latest_runtime_decision["route_decision"]["provider"]["provider_id"] == payload["latest_interaction"]["provider_id"]
    assert latest_runtime_decision["route_decision"]["selected_expert"] == payload["latest_interaction"]["expert_node"]
    assert latest_runtime_decision["cache_state"]["latest_cache_entry_id"] == latest_cache["entry_id"]
    assert latest_runtime_decision["cache_state"]["promotion_allowed"] is True
    assert latest_runtime_decision["eval_state"]["promotion_allowed"] is True
    eval_gate = latest_runtime_decision["eval_state"]["external_evals_ao_artifact_gate"]
    assert eval_gate["surface_id"] == "external-evals-ao-artifact-gate"
    assert eval_gate["ao"] == "EvalsAO"
    assert eval_gate["status"] == "passed-shadow"
    assert eval_gate["artifact_set_complete"] is True
    assert eval_gate["raw_content_included"] is False
    assert eval_gate["active_production_mutation_allowed"] is False
    assert set(eval_gate["artifact_refs"]) == {"decision", "metrics", "report", "scenarios"}
    artifact_root = project / "runtime" / "artifacts"
    for artifact_ref in eval_gate["artifact_refs"].values():
        assert not Path(artifact_ref).is_absolute()
        assert (artifact_root / artifact_ref).is_file()
    decision_artifact = json.loads((artifact_root / eval_gate["artifact_refs"]["decision"]).read_text(encoding="utf-8"))
    assert decision_artifact["surface_id"] == "external-evals-ao-artifact-gate"
    assert decision_artifact["decision"] == "passed-shadow"
    assert decision_artifact["raw_content_included"] is False
    assert decision_artifact["active_production_mutation_allowed"] is False
    assert decision_artifact["promotion_allowed"] is True
    metrics_artifact = json.loads((artifact_root / eval_gate["artifact_refs"]["metrics"]).read_text(encoding="utf-8"))
    assert metrics_artifact["trace_ref"] == latest_runtime_decision["metadata"]["trace_ref"]
    assert metrics_artifact["runtime_scorecard_id"] == capability["latest_runtime_scorecard_id"]
    scenarios_artifact = (artifact_root / eval_gate["artifact_refs"]["scenarios"]).read_text(encoding="utf-8")
    assert "Write a small Python" not in scenarios_artifact
    assert "release-user-a" not in scenarios_artifact
    eval_registry = client.get("/ops/brain/eval-registry").json()
    live_eval_ref = eval_gate["eval_registry_ref"]
    live_eval_suite = next(suite for suite in eval_registry["suites"] if suite["suite_id"] == live_eval_ref["suite_id"])
    assert live_eval_suite["suite_type"] == "runtime"
    assert live_eval_suite["promotion_gate"] == "passed"
    assert live_eval_suite["held_out"] is True
    assert live_eval_suite["metadata"]["source"] == "release-wrapper-runtime-evals-ao-artifact-gate"
    live_shadow_run = next(
        run for run in eval_registry["shadow_runs"] if run["run_id"] == live_eval_ref["shadow_run_id"]
    )
    assert live_shadow_run["status"] == "passed-shadow"
    assert live_shadow_run["operator_approved"] is True
    assert live_shadow_run["promotion_allowed"] is True
    assert live_shadow_run["shadow_findings"] == []
    assert live_shadow_run["metadata"]["raw_content_included"] is False
    assert live_shadow_run["metadata"]["active_production_mutation_allowed"] is False
    assert "active_production_mutation_allowed" in latest_runtime_decision["quantization_state"]
    assert latest_runtime_decision["quantization_state"]["active_production_mutation_allowed"] is False
    assert latest_runtime_decision["metadata"]["raw_content_included"] is False
    assert latest_runtime_decision["metadata"]["runtime_scorecard_id"] == capability["latest_runtime_scorecard_id"]
    assert latest_runtime_decision["metadata"]["evals_ao_artifact_gate_id"] == eval_gate["gate_id"]
    assert latest_runtime_decision["metadata"]["active_production_mutation_allowed"] is False
    assert payload["latest_interaction"]["runtime_decision_id"] == latest_runtime_decision["decision_id"]
    assert payload["runtime_decision_ledger"]["decision_count"] == 1
    assert payload["runtime_decision_ledger"]["latest_decision"]["decision_id"] == latest_runtime_decision["decision_id"]
    assert any(ref.startswith("cache::release-wrapper::") for ref in latest_runtime_decision["evidence_refs"])
    assert any(ref.startswith("evals-ao-artifact::") for ref in latest_runtime_decision["evidence_refs"])
    governance = payload["authority_evidence_tool_governance"]
    assert governance["surface_id"] == "authority-evidence-tool-governance-release-gate"
    assert governance["status"] == "pass"
    assert governance["authority_spine"]["surface_id"] == "authority-integrity-spine"
    assert governance["authority_spine"]["latest_action_id"] == payload["latest_interaction"]["authority_decision_id"]
    assert governance["authority_spine"]["production_action_allowed"] is False
    assert governance["evidence_store"]["surface_id"] == "content-addressed-evidence-store"
    assert governance["evidence_store"]["latest_record_id"] == payload["latest_interaction"]["evidence_store_record_id"]
    assert governance["evidence_store"]["latest_hash"].startswith("sha256:")
    assert governance["eval_federation"]["surface_id"] == "eval-federation"
    assert governance["eval_federation"]["latest_event_id"] == payload["latest_interaction"]["eval_federation_event_id"]
    assert governance["eval_federation"]["promotion_allowed"] is True
    assert governance["tool_action_harness"]["surface_id"] == "tool-action-harness"
    assert governance["tool_action_harness"]["latest_action_id"] == payload["latest_interaction"]["tool_action_plan_id"]
    assert governance["tool_action_harness"]["execution_allowed"] is False
    assert governance["runtime_decision_ledger"]["latest_decision_id"] == latest_runtime_decision["decision_id"]
    assert governance["raw_content_included"] is False
    assert governance["active_production_mutation_allowed"] is False
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "release-user-a"}).json()
    assert visualizer["overlay_state"]["control_panel"]["runtime_decision_ledger_scorecard"]["decision_count"] == 1
    visualizer_latest_decision = visualizer["overlay_state"]["control_panel"]["runtime_decision_ledger_scorecard"]["latest_decision"]
    assert (
        visualizer_latest_decision["eval_state"]["external_evals_ao_artifact_gate"]["gate_id"]
        == eval_gate["gate_id"]
    )
    restarted = TestClient(create_app(str(project)))
    replayed_decisions = restarted.get("/ops/brain/canon/runtime-decision-ledger").json()
    assert replayed_decisions["decision_count"] == 1
    assert replayed_decisions["latest_decision"]["decision_id"] == latest_runtime_decision["decision_id"]
    assert (
        replayed_decisions["latest_decision"]["eval_state"]["external_evals_ao_artifact_gate"]["gate_id"]
        == eval_gate["gate_id"]
    )
    replayed_runtime = restarted.get("/ops/wrapper/release-runtime", params={"session_id": "release-user-a"}).json()
    assert replayed_runtime["runtime_decision_ledger"]["decision_count"] == 1
    assert replayed_runtime["runtime_decision_ledger"]["latest_decision"]["decision_id"] == latest_runtime_decision["decision_id"]
    assert "Write a small Python" not in json.dumps(payload)
    assert "release-user-a" not in json.dumps(payload["effective_context_cache"])
    assert payload["autonomous_updates"]["proposal_count"] >= 1
    readiness = client.get("/ops/wrapper/release-readiness", params={"session_id": "release-user-a"}).json()
    readiness_checks = {check["check_id"]: check for check in readiness["readiness_checks"]}
    assert readiness_checks["context-window-truth-boundary"]["status"] == "pass"
    assert readiness_checks["context-capability-envelope"]["status"] == "pass"
    assert readiness_checks["runtime-decision-ledger"]["status"] == "pass"
    assert readiness_checks["evals-ao-artifact-gate"]["status"] == "pass"
    assert readiness_checks["authority-evidence-tool-governance"]["status"] == "pass"
    assert readiness_checks["canon-contract-receipt"]["status"] == "pass"
    assert readiness["evidence"]["canon_contract_receipts"]["latest_receipt"]["receipt_id"] == canon_receipt["receipt_id"]
    assert readiness["evidence"]["context_window_posture"]["latest_cache_entry_id"] == latest_cache["entry_id"]
    assert readiness["evidence"]["context_capability_envelope"]["latest_runtime_scorecard_id"] == capability["latest_runtime_scorecard_id"]
    assert readiness["evidence"]["runtime_decision_ledger"]["latest_decision"]["decision_id"] == latest_runtime_decision["decision_id"]
    assert (
        readiness["evidence"]["runtime_decision_ledger"]["latest_decision"]["eval_state"][
            "external_evals_ao_artifact_gate"
        ]["gate_id"]
        == eval_gate["gate_id"]
    )
    runtime_proposal = next(
        proposal
        for proposal in payload["autonomous_updates"]["proposals"]
        if proposal["metadata"].get("source") == "release-wrapper-runtime"
    )
    assert runtime_proposal["requested_state"] == "proposal"
    assert runtime_proposal["metadata"]["safe_file_scope"] == ["artifacts/autonomous-updates/safe-files"]
    assert eval_gate["gate_id"] in runtime_proposal["eval_refs"]
    assert eval_gate["eval_registry_ref"]["suite_id"] in runtime_proposal["eval_refs"]
    assert runtime_proposal["metadata"]["evals_ao_artifact_gate_ref"] == eval_gate["gate_id"]
    assert runtime_proposal["metadata"]["evals_ao_eval_suite_id"] == eval_gate["eval_registry_ref"]["suite_id"]
    assert runtime_proposal["metadata"]["canon_contract_receipt_id"] == canon_receipt["receipt_id"]
    assert runtime_proposal["metadata"]["canon_contract_coverage_status"] == canon_receipt["coverage_status"]
    assert runtime_proposal["metadata"]["canon_contract_gap_count"] == canon_receipt["gap_count"]
    assert runtime_proposal["metadata"]["safe_payload"]["canon_contract_receipt_id"] == canon_receipt["receipt_id"]
    dream_proposal = next(
        proposal
        for proposal in payload["autonomous_updates"]["proposals"]
        if proposal["metadata"].get("dream_research_queue") is True
    )
    assert dream_proposal["metadata"]["canon_contract_receipt_id"] == canon_receipt["receipt_id"]
    assert dream_proposal["metadata"]["safe_payload"]["canon_contract_gaps"] == canon_receipt["gaps"]
    assert payload["dream_research_queue"]["latest_item"]["metadata"]["canon_contract_receipt_id"] == canon_receipt["receipt_id"]


class _BoundedContextHardwareScanner:
    def scan(self):
        return {
            "profile_id": "device::bounded-context-test",
            "platform": "test-host",
            "python_version": "3.test",
            "cpu_count": 8,
            "ram_gb": 64.0,
            "vram_gb": 24.0,
            "gpu_summary": "test-gpu",
            "thermal_mode": "nominal",
            "ram_pressure": "stable",
            "vram_pressure": "stable",
            "safe_mode": False,
            "max_context_tokens": 262_144,
            "long_context_profile": {
                "ambition_tokens": 1_000_000,
                "host_cap_tokens": 262_144,
                "target_profile": "bounded-long-context",
            },
            "local_first": True,
            "status_label": "LOCKED CANON",
        }


def test_openai_chat_completion_product_path_emits_traceable_project_heartbeat(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    session_id = "product-path-project-heartbeat-user"
    prompt = "Route OpenAI-compatible chat through the project heartbeat without SECRET-PRODUCT-HEARTBEAT."

    chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
        },
    )

    assert chat.status_code == 200
    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    readiness = client.get("/ops/wrapper/release-readiness", params={"session_id": session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]

    heartbeat = runtime["project_heartbeat"]
    latest_interaction = runtime["latest_interaction"]
    cycle = runtime["nexusbrain_runtime_cycle"]
    cycle_receipt = cycle["latest_receipt"]
    cycle_stages = {
        stage["stage_id"]: stage
        for stage in cycle_receipt["stages"]
    }
    storage_replay_stage = cycle_stages["storage_replay"]
    assert heartbeat["surface_id"] == "nexusnet-project-heartbeat"
    assert heartbeat["status"] == "alive"
    assert heartbeat["raw_content_included"] is False
    assert heartbeat["active_production_mutation_allowed"] is False
    assert heartbeat["active_production_mutated"] is False
    assert heartbeat["native_replay_ref"] == "hive-substrate/project-heartbeats/_index.jsonl"
    assert heartbeat["native_replay_record_id"]
    assert runtime["project_heartbeat_replay"]["latest_heartbeat_id"] == heartbeat["heartbeat_id"]
    assert runtime["project_heartbeat_replay"]["latest_record_id"]
    assert runtime["project_heartbeat_replay"]["artifact_ref"] == "release-wrapper-runtime/project-heartbeats.jsonl"
    assert latest_interaction["project_heartbeat_replay_ref"] == heartbeat["native_replay_ref"]
    assert (
        latest_interaction["project_heartbeat_replay_record_id"]
        == heartbeat["native_replay_record_id"]
    )
    assert latest_interaction["project_heartbeat_wrapper_replay_ref"] == "release-wrapper-runtime/project-heartbeats.jsonl"
    assert (
        latest_interaction["project_heartbeat_wrapper_replay_record_id"]
        == runtime["project_heartbeat_replay"]["latest_record_id"]
    )
    assert cycle["latest_status"] == "covered"
    assert cycle_receipt["status"] == "covered"
    assert cycle_receipt["evidence_refs"]["project_heartbeat_replay_ref"] == (
        latest_interaction["project_heartbeat_replay_ref"]
    )
    assert cycle_receipt["evidence_refs"]["project_heartbeat_replay_record_id"] == (
        latest_interaction["project_heartbeat_replay_record_id"]
    )
    assert storage_replay_stage["status"] == "covered"
    assert latest_interaction["project_heartbeat_replay_ref"] in storage_replay_stage["evidence_refs"]
    assert latest_interaction["project_heartbeat_replay_record_id"] in storage_replay_stage["evidence_refs"]
    assert latest_interaction["hive_run_id"] == heartbeat["source_run_id"]
    assert latest_interaction["project_heartbeat_id"] == heartbeat["heartbeat_id"]
    assert latest_interaction["project_heartbeat_source_run_id"] == heartbeat["source_run_id"]
    assert latest_interaction["project_heartbeat_status"] == "alive"
    assert latest_interaction["project_heartbeat_lane_count"] == heartbeat["lane_count"]

    readiness_checks = {check["check_id"]: check for check in readiness["readiness_checks"]}
    assert readiness_checks["project-heartbeat"]["status"] == "pass"
    assert readiness["evidence"]["project_heartbeat"]["heartbeat_id"] == heartbeat["heartbeat_id"]
    assert status_card["project_heartbeat"]["heartbeat_id"] == heartbeat["heartbeat_id"]
    assert control_panel["project_heartbeat"]["heartbeat_id"] == heartbeat["heartbeat_id"]
    assert control_panel["release_wrapper_runtime"]["project_heartbeat"]["heartbeat_id"] == heartbeat["heartbeat_id"]
    native_replay_status = control_panel["project_heartbeat_native_replay_status"]
    assert native_replay_status["status"] == "covered"
    assert native_replay_status["native_replay_ref"] == heartbeat["native_replay_ref"]
    assert native_replay_status["native_replay_record_id"] == heartbeat["native_replay_record_id"]
    assert native_replay_status["wrapper_replay_ref"] == "release-wrapper-runtime/project-heartbeats.jsonl"
    assert native_replay_status["raw_content_included"] is False
    assert native_replay_status["active_production_mutation_allowed"] is False

    serialized = json.dumps(
        {
            "runtime": runtime["project_heartbeat"],
            "latest_interaction": latest_interaction,
            "readiness": readiness["evidence"]["project_heartbeat"],
            "status_card": status_card["project_heartbeat"],
            "control_panel": control_panel["project_heartbeat"],
            "native_replay_status": native_replay_status,
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-PRODUCT-HEARTBEAT" not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized


def test_openai_chat_completion_emits_replayable_whole_system_heartbeat_tick(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    session_id = "whole-system-heartbeat-user"
    prompt = "Make the whole NexusBrain heart beat without SECRET-WHOLE-SYSTEM-HEARTBEAT."

    chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
        },
    )

    assert chat.status_code == 200
    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    readiness = client.get("/ops/wrapper/release-readiness", params={"session_id": session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]

    tick = runtime["whole_system_heartbeat_tick"]
    latest_interaction = runtime["latest_interaction"]
    cycle = runtime["nexusbrain_runtime_cycle"]
    native = runtime["native_hive_heartbeat"]
    project_heartbeat = runtime["project_heartbeat"]

    assert tick["schema_version"] == "nexusnet-whole-system-heartbeat-tick-v1"
    assert tick["surface_id"] == "whole-system-heartbeat-tick"
    assert tick["status"] == "alive"
    assert tick["authority"] == "NexusBrain"
    assert tick["product_scope"] == "whole-system"
    assert tick["session_ref_digest"] == latest_interaction["session_ref_digest"]
    assert tick["trace_ref"] == f"trace::{latest_interaction['trace_id']}"
    assert tick["nexusbrain_runtime_cycle_receipt_id"] == cycle["latest_receipt_id"]
    assert tick["native_hive_heartbeat_id"] == native["heartbeat_id"]
    assert tick["project_heartbeat_id"] == project_heartbeat["heartbeat_id"]
    assert tick["forward_pass_receipt_id"] == latest_interaction["forward_pass_receipt_id"]
    assert tick["federated_packet_id"] == latest_interaction["federated_packet_id"]
    assert tick["runtime_growth_receipt_id"] == latest_interaction["runtime_growth_receipt_id"]
    assert tick["dream_research_episode_id"] == latest_interaction["dream_research_episode_id"]
    assert tick["autonomous_update_lifecycle_run_id"] == latest_interaction["autonomous_update_lifecycle_run_id"]
    assert tick["release_health_heartbeat_loop_id"] == latest_interaction["release_health_heartbeat_loop_id"]
    assert tick["release_run_history_run_id"] == ""
    assert latest_interaction["release_run_history_run_id"].startswith("release-run::live-product-path::")
    assert tick["canonical_ao_coverage_id"] == runtime["canonical_ao_coverage"]["latest_coverage_id"]
    assert tick["ao_execution_receipt_id"] == latest_interaction["ao_execution_receipt_id"]
    assert tick["raw_content_included"] is False
    assert tick["active_production_mutation_allowed"] is False
    assert tick["active_production_mutated"] is False
    tick_stages = {stage["stage_id"]: stage for stage in tick["stages"]}
    assert set(tick_stages) >= {
        "nexusbrain_runtime_cycle",
        "native_hive_heartbeat",
        "project_heartbeat",
        "continuous_assimilation",
        "global_growth",
        "federation",
        "dream_research",
        "authority_evals_tools",
        "ao_runtime_governance",
        "self_repair_update_governance",
        "storage_replay",
        "release_health_heartbeat",
    }
    assert tick_stages["ao_runtime_governance"]["status"] == "covered"
    assert runtime["canonical_ao_coverage"]["latest_coverage_id"] in tick_stages["ao_runtime_governance"]["evidence_refs"]
    assert latest_interaction["ao_execution_receipt_id"] in tick_stages["ao_runtime_governance"]["evidence_refs"]
    cycle_receipt = cycle["latest_receipt"]
    cycle_stages = {stage["stage_id"]: stage for stage in cycle_receipt["stages"]}
    assert "ao_runtime_governance" in cycle["required_stages"]
    assert "ao_runtime_governance" in cycle_receipt["required_stages"]
    assert cycle_stages["ao_runtime_governance"]["status"] == "covered"
    assert runtime["canonical_ao_coverage"]["latest_coverage_id"] in cycle_stages["ao_runtime_governance"]["evidence_refs"]
    assert latest_interaction["ao_execution_receipt_id"] in cycle_stages["ao_runtime_governance"]["evidence_refs"]
    assert all(stage["status"] == "covered" for stage in tick_stages.values())
    assert tick["covered_count"] == len(tick["stages"])
    assert tick["degraded_count"] == 0
    assert tick["tick_id"] == latest_interaction["whole_system_heartbeat_tick_id"]
    assert tick["artifact_ref"] == "release-wrapper-runtime/whole-system-heartbeat-ticks.jsonl"
    assert runtime["whole_system_heartbeat"]["latest_tick_id"] == tick["tick_id"]
    assert runtime["whole_system_heartbeat"]["status"] == "alive"
    assert runtime["whole_system_heartbeat"]["tick_count"] == 1
    assert runtime["whole_system_heartbeat"]["raw_content_included"] is False
    assert runtime["whole_system_heartbeat"]["active_production_mutation_allowed"] is False
    assert readiness["evidence"]["whole_system_heartbeat"]["latest_tick_id"] == tick["tick_id"]
    assert status_card["whole_system_heartbeat"]["latest_tick_id"] == tick["tick_id"]
    assert control_panel["release_wrapper_runtime"]["whole_system_heartbeat"]["latest_tick_id"] == tick["tick_id"]
    assert control_panel["release_wrapper_runtime"]["whole_system_heartbeat_tick"]["tick_id"] == tick["tick_id"]

    tick_log = project_root / "artifacts" / "release-wrapper-runtime" / "whole-system-heartbeat-ticks.jsonl"
    assert tick_log.exists()
    lines = [line for line in tick_log.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) == 1
    persisted_tick = json.loads(lines[0])
    assert persisted_tick["tick_id"] == tick["tick_id"]
    assert persisted_tick["raw_content_included"] is False

    restarted = TestClient(create_app(str(project_root)))
    replayed = restarted.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    assert replayed["whole_system_heartbeat"]["status"] == "replayed"
    assert replayed["whole_system_heartbeat"]["latest_tick_id"] == tick["tick_id"]
    assert replayed["whole_system_heartbeat_tick"]["tick_id"] == tick["tick_id"]
    assert replayed["whole_system_heartbeat_tick"]["status"] == "alive"

    serialized = json.dumps(
        {
            "tick": tick,
            "ao_coverage": runtime["canonical_ao_coverage"],
            "summary": runtime["whole_system_heartbeat"],
            "readiness": readiness["evidence"]["whole_system_heartbeat"],
            "status_card": status_card["whole_system_heartbeat"],
            "control_panel": control_panel["release_wrapper_runtime"]["whole_system_heartbeat"],
            "persisted": persisted_tick,
            "replayed": replayed["whole_system_heartbeat"],
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-WHOLE-SYSTEM-HEARTBEAT" not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized


def test_degraded_whole_system_heartbeat_runs_governed_repair_from_live_use(
    tmp_path: Path,
    monkeypatch,
):
    project_root = make_project(tmp_path)
    session_id = "whole-system-heartbeat-repair-user"
    prompt = "Exercise a degraded whole-system heartbeat without leaking SECRET-HEARTBEAT-REPAIR."
    original_record_automatic_loop = ReleaseWrapperRuntime.record_automatic_release_health_heartbeat_loop
    automatic_loop_calls = {"count": 0, "missing_wrapper_interaction": 0, "post_repair_probe": 0}

    def _missing_then_real_release_health_loop(
        self,
        *,
        session_id,
        trigger,
        base_url=None,
        host="127.0.0.1",
        port=0,
        pid=0,
    ):
        automatic_loop_calls["count"] += 1
        if trigger == "whole-system-heartbeat-post-repair-probe":
            automatic_loop_calls["post_repair_probe"] += 1
        if trigger != "wrapper-interaction-auto" or automatic_loop_calls["missing_wrapper_interaction"]:
            return original_record_automatic_loop(
                self,
                session_id=session_id,
                trigger=trigger,
                base_url=base_url,
                host=host,
                port=port,
                pid=pid,
            )
        automatic_loop_calls["missing_wrapper_interaction"] += 1
        return {
            "schema_version": "nexusnet-release-wrapper-health-heartbeat-loop-v1",
            "surface_id": "release-wrapper-health-heartbeat-loop",
            "status": "blocked-test-induced-release-health-gap",
            "loop_id": "",
            "trigger": trigger,
            "session_ref_digest": None,
            "repair_queue": {},
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }

    monkeypatch.setattr(
        ReleaseWrapperRuntime,
        "record_automatic_release_health_heartbeat_loop",
        _missing_then_real_release_health_loop,
    )

    client = TestClient(create_app(str(project_root)))
    chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
        },
    )

    assert chat.status_code == 200
    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    readiness = client.get("/ops/wrapper/release-readiness", params={"session_id": session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]

    latest_interaction = runtime["latest_interaction"]
    tick = latest_interaction["whole_system_heartbeat_tick"]
    stages = {stage["stage_id"]: stage for stage in tick["stages"]}

    assert tick["status"] == "degraded"
    assert stages["release_health_heartbeat"]["status"] == "degraded"
    assert stages["release_health_heartbeat"]["blocker"] == "release_health_heartbeat_refs_missing"
    assert "release_health_heartbeat_refs_missing" in tick["blockers"]

    repair_plan = latest_interaction["whole_system_heartbeat_repair_plan"]
    assert repair_plan["schema_version"] == "nexusnet-whole-system-heartbeat-repair-plan-v1"
    assert repair_plan["surface_id"] == "whole-system-heartbeat-repair-plan"
    assert repair_plan["status"] == "completed-whole-system-heartbeat-repair"
    assert repair_plan["source_tick_id"] == tick["tick_id"]
    assert repair_plan["source_tick_status"] == "degraded"
    assert repair_plan["degraded_stage_ids"] == ["release_health_heartbeat"]
    assert repair_plan["blockers"] == ["release_health_heartbeat_refs_missing"]
    assert repair_plan["stage_repair_candidate_count"] == 1
    stage_candidate = repair_plan["stage_repair_candidates"][0]
    assert stage_candidate["stage_id"] == "release_health_heartbeat"
    assert stage_candidate["repair_generator"] == "release-health-heartbeat-loop-repair-candidate"
    assert stage_candidate["target_ref"] == "safe-artifact::whole-system-heartbeat::release-health-heartbeat"
    assert stage_candidate["safe_file_scope"] == ["artifacts/autonomous-updates/safe-files"]
    assert stage_candidate["expected_next_evidence_refs"] == [
        "/ops/wrapper/release-health-heartbeat/run",
        "/ops/wrapper/release-health-heartbeat/supervisor/repair-run",
        "release-wrapper-runtime/release-health-heartbeat-loop.jsonl",
    ]
    assert stage_candidate["active_production_mutation_allowed"] is False
    assert stage_candidate["raw_content_included"] is False
    assert repair_plan["lifecycle_status"] == "completed"
    assert repair_plan["actions"]["admin_approval"]["status"] == "admin-approved"
    assert repair_plan["actions"]["sandbox_tests"]["status"] == "passed"
    assert repair_plan["actions"]["apply"]["status"] == "applied-shadow-safe-file"
    assert repair_plan["actions"]["rollback"]["status"] == "rolled-back"
    assert repair_plan["active_production_mutation_allowed"] is False
    assert repair_plan["active_production_mutated"] is False
    assert repair_plan["raw_content_included"] is False

    post_repair = repair_plan["post_repair_verification"]
    assert post_repair["schema_version"] == "nexusnet-whole-system-heartbeat-post-repair-verification-v1"
    assert post_repair["surface_id"] == "whole-system-heartbeat-post-repair-verification"
    assert post_repair["status"] == "verified-post-repair-live-stage-coverage"
    assert post_repair["source_tick_id"] == tick["tick_id"]
    assert post_repair["source_plan_id"] == repair_plan["plan_id"]
    assert post_repair["source_update_id"] == repair_plan["update_id"]
    assert post_repair["verified_stage_count"] == 1
    assert post_repair["candidate_consumption_count"] == 1
    assert post_repair["rollback_verified"] is True
    assert post_repair["raw_content_included"] is False
    assert post_repair["active_production_mutation_allowed"] is False
    assert post_repair["active_production_mutated"] is False
    assert automatic_loop_calls["missing_wrapper_interaction"] == 1
    assert automatic_loop_calls["post_repair_probe"] == 1
    real_probe = post_repair["real_heartbeat_probe"]
    assert real_probe["surface_id"] == "whole-system-heartbeat-post-repair-real-probe"
    assert real_probe["status"] == "completed-live-post-repair-heartbeat-probe"
    assert real_probe["stage_id"] == "release_health_heartbeat"
    assert real_probe["loop_id"]
    assert real_probe["loop_trigger"] == "whole-system-heartbeat-post-repair-probe"
    assert real_probe["loop_artifact_ref"] == "release-wrapper-runtime/release-health-heartbeat-loop.jsonl"
    assert real_probe["raw_content_included"] is False
    assert real_probe["active_production_mutation_allowed"] is False
    assert real_probe["active_production_mutated"] is False
    post_repair_tick = post_repair["post_repair_tick"]
    post_repair_stages = {stage["stage_id"]: stage for stage in post_repair_tick["stages"]}
    assert post_repair_tick["schema_version"] == "nexusnet-whole-system-heartbeat-tick-v1"
    assert post_repair_tick["surface_id"] == "whole-system-heartbeat-tick"
    assert post_repair_tick["status"] == "alive"
    assert post_repair_tick["tick_id"] != tick["tick_id"]
    assert post_repair_tick["source_tick_id"] == tick["tick_id"]
    assert post_repair_tick["source_repair_plan_id"] == repair_plan["plan_id"]
    assert post_repair_tick["source_repair_update_id"] == repair_plan["update_id"]
    assert post_repair_tick["post_repair_verification_id"] == post_repair["verification_id"]
    assert post_repair_tick["release_health_heartbeat_loop_id"] == real_probe["loop_id"]
    assert post_repair_stages["release_health_heartbeat"]["status"] == "covered"
    assert post_repair_tick["raw_content_included"] is False
    assert post_repair_tick["active_production_mutation_allowed"] is False
    assert post_repair_tick["active_production_mutated"] is False
    verified_stage = post_repair["verified_stages"][0]
    assert verified_stage["stage_id"] == "release_health_heartbeat"
    assert verified_stage["pre_repair_status"] == "degraded"
    assert verified_stage["post_repair_status"] == "covered"
    assert verified_stage["transition"] == "degraded-to-covered-by-admin-approved-live-post-repair-probe"
    assert verified_stage["candidate_id"] == stage_candidate["candidate_id"]
    assert verified_stage["repair_generator"] == "release-health-heartbeat-loop-repair-candidate"
    assert verified_stage["expected_next_evidence_refs"] == stage_candidate["expected_next_evidence_refs"]
    assert "/ops/wrapper/release-health-heartbeat/supervisor/repair-run" in verified_stage["observed_evidence_refs"]
    assert "release-wrapper-runtime/release-health-heartbeat-loop.jsonl" in verified_stage["observed_evidence_refs"]
    assert post_repair_tick["tick_id"] in verified_stage["observed_evidence_refs"]
    assert real_probe["loop_id"] in verified_stage["observed_evidence_refs"]
    assert verified_stage["admin_approval_status"] == "admin-approved"
    assert verified_stage["sandbox_status"] == "passed"
    assert verified_stage["apply_status"] == "applied-shadow-safe-file"
    assert verified_stage["rollback_status"] == "rolled-back"
    assert verified_stage["raw_content_included"] is False
    assert verified_stage["active_production_mutation_allowed"] is False

    safe_payload = repair_plan["safe_payload"]
    assert safe_payload["stage_repair_candidate_count"] == 1
    assert safe_payload["stage_repair_candidates"][0]["stage_id"] == "release_health_heartbeat"
    assert (
        safe_payload["stage_repair_candidates"][0]["repair_generator"]
        == "release-health-heartbeat-loop-repair-candidate"
    )
    assert safe_payload["raw_content_included"] is False

    assert latest_interaction["whole_system_heartbeat_repair_plan_id"] == repair_plan["plan_id"]
    assert latest_interaction["whole_system_heartbeat_repair_plan_status"] == repair_plan["status"]
    assert tick["repair_plan_id"] == repair_plan["plan_id"]
    assert tick["repair_plan_status"] == repair_plan["status"]
    assert runtime["whole_system_heartbeat"]["latest_repair_plan_id"] == repair_plan["plan_id"]
    assert runtime["whole_system_heartbeat"]["latest_repair_plan_status"] == repair_plan["status"]
    assert runtime["whole_system_heartbeat"]["status"] == "alive"
    assert runtime["whole_system_heartbeat"]["latest_tick_id"] == post_repair_tick["tick_id"]
    assert runtime["whole_system_heartbeat_tick"]["tick_id"] == post_repair_tick["tick_id"]
    assert runtime["whole_system_heartbeat_tick"]["status"] == "alive"
    assert runtime["whole_system_heartbeat"]["latest_post_repair_verification_id"] == (
        post_repair["verification_id"]
    )
    assert runtime["whole_system_heartbeat"]["post_repair_verification_count"] == 1
    assert runtime["release_readiness_evidence_runner"]["latest_whole_system_heartbeat_repair_status"] == (
        repair_plan["status"]
    )
    assert readiness["evidence"]["whole_system_heartbeat"]["latest_repair_plan_id"] == repair_plan["plan_id"]
    assert status_card["whole_system_heartbeat"]["latest_repair_plan_id"] == repair_plan["plan_id"]
    assert control_panel["release_wrapper_runtime"]["whole_system_heartbeat"]["latest_repair_plan_id"] == (
        repair_plan["plan_id"]
    )

    tick_log = project_root / "artifacts" / "release-wrapper-runtime" / "whole-system-heartbeat-ticks.jsonl"
    persisted_ticks = [
        json.loads(line)
        for line in tick_log.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    persisted_tick = next(record for record in persisted_ticks if record["tick_id"] == tick["tick_id"])
    persisted_post_repair_tick = next(
        record for record in persisted_ticks if record["tick_id"] == post_repair_tick["tick_id"]
    )
    assert persisted_tick["tick_id"] == tick["tick_id"]
    assert persisted_tick["repair_plan_id"] == repair_plan["plan_id"]
    assert persisted_tick["latest_repair_plan"]["status"] == repair_plan["status"]
    assert persisted_tick["latest_repair_plan"]["post_repair_verification"]["verification_id"] == (
        post_repair["verification_id"]
    )
    assert persisted_tick["latest_repair_plan"]["raw_content_included"] is False
    assert persisted_post_repair_tick["tick_id"] == post_repair_tick["tick_id"]
    assert persisted_post_repair_tick["status"] == "alive"
    assert persisted_post_repair_tick["source_tick_id"] == tick["tick_id"]
    assert persisted_post_repair_tick["source_repair_plan_id"] == repair_plan["plan_id"]
    assert persisted_post_repair_tick["post_repair_verification_id"] == post_repair["verification_id"]
    assert persisted_post_repair_tick["raw_content_included"] is False

    replay_client = TestClient(create_app(str(project_root)))
    replayed_runtime = replay_client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    replayed_heartbeat = replayed_runtime["whole_system_heartbeat"]
    assert replayed_heartbeat["status"] == "replayed"
    assert replayed_heartbeat["latest_tick_id"] == post_repair_tick["tick_id"]
    assert replayed_runtime["whole_system_heartbeat_tick"]["tick_id"] == post_repair_tick["tick_id"]
    assert replayed_runtime["whole_system_heartbeat_tick"]["status"] == "alive"
    assert replayed_heartbeat["latest_post_repair_verification_id"] == post_repair["verification_id"]
    assert replayed_heartbeat["post_repair_verification_count"] == 1

    serialized = json.dumps(
        {
            "repair_plan": repair_plan,
            "tick": tick,
            "summary": runtime["whole_system_heartbeat"],
            "replayed": replayed_heartbeat,
            "readiness": readiness["evidence"]["whole_system_heartbeat"],
            "status_card": status_card["whole_system_heartbeat"],
            "control_panel": control_panel["release_wrapper_runtime"]["whole_system_heartbeat"],
            "persisted_tick": persisted_tick,
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-HEARTBEAT-REPAIR" not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized


def test_degraded_whole_system_heartbeat_recovers_growth_and_federation_from_live_probe(
    tmp_path: Path,
    monkeypatch,
):
    project_root = make_project(tmp_path)
    session_id = "whole-system-growth-federation-repair-user"
    prompt = "Recover global growth and federation without leaking SECRET-GROWTH-FEDERATION-REPAIR."
    client = TestClient(create_app(str(project_root)))
    runtime_obj = client.app.state.release_wrapper_runtime

    original_record_growth = runtime_obj.global_growth.record_runtime_interaction
    original_growth_status = runtime_obj.global_growth.growth_status
    original_hive_forward = runtime_obj.hive_substrate.run_forward_pass
    growth_calls = {"count": 0, "post_repair_probe": 0}
    growth_status_calls = {"allow_latest_receipt": False, "hidden_latest_receipt": 0}
    hive_calls = {"count": 0, "post_repair_probe": 0}

    def _missing_then_real_growth(*args, **kwargs):
        growth_calls["count"] += 1
        if growth_calls["count"] == 1:
            raise RuntimeError("test-induced-global-growth-gap")
        if kwargs.get("task_family") == "whole-system-heartbeat-post-repair":
            growth_calls["post_repair_probe"] += 1
        return original_record_growth(*args, **kwargs)

    def _hide_first_background_growth_receipt(*args, **kwargs):
        status = original_growth_status(*args, **kwargs)
        if (
            kwargs.get("include_latest_receipt", True)
            and not growth_status_calls["allow_latest_receipt"]
            and isinstance(status, dict)
            and isinstance(status.get("latest_runtime_receipt"), dict)
        ):
            growth_status_calls["hidden_latest_receipt"] += 1
            status = dict(status)
            status["latest_runtime_receipt"] = None
        return status

    def _missing_then_real_hive_forward(request):
        hive_calls["count"] += 1
        result = original_hive_forward(request)
        task_id = str(getattr(request, "task_id", "") or "")
        if hive_calls["count"] == 1:
            degraded = dict(result)
            degraded["federated_learning_packet"] = {}
            degraded["runtime_growth_receipt"] = {}
            return degraded
        if "whole-system-heartbeat-post-repair" in task_id:
            hive_calls["post_repair_probe"] += 1
        return result

    monkeypatch.setattr(runtime_obj.global_growth, "record_runtime_interaction", _missing_then_real_growth)
    monkeypatch.setattr(runtime_obj.global_growth, "growth_status", _hide_first_background_growth_receipt)
    monkeypatch.setattr(runtime_obj.hive_substrate, "run_forward_pass", _missing_then_real_hive_forward)

    chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
        },
    )

    assert chat.status_code == 200
    growth_status_calls["allow_latest_receipt"] = True
    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    readiness = client.get("/ops/wrapper/release-readiness", params={"session_id": session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]

    latest_interaction = runtime["latest_interaction"]
    tick = latest_interaction["whole_system_heartbeat_tick"]
    stages = {stage["stage_id"]: stage for stage in tick["stages"]}

    assert tick["status"] == "degraded"
    assert tick["runtime_growth_receipt_id"] == ""
    assert tick["federated_packet_id"] == ""
    assert stages["global_growth"]["status"] == "degraded"
    assert stages["global_growth"]["blocker"] == "runtime_growth_receipt_missing"
    assert stages["federation"]["status"] == "degraded"
    assert stages["federation"]["blocker"] == "federated_packet_refs_missing"

    repair_plan = latest_interaction["whole_system_heartbeat_repair_plan"]
    assert repair_plan["status"] == "completed-whole-system-heartbeat-repair"
    assert repair_plan["degraded_stage_ids"] == ["global_growth", "federation"]
    assert repair_plan["blockers"] == ["runtime_growth_receipt_missing", "federated_packet_refs_missing"]
    assert repair_plan["stage_repair_candidate_count"] == 2
    assert repair_plan["lifecycle_status"] == "completed"
    assert repair_plan["actions"]["admin_approval"]["status"] == "admin-approved"
    assert repair_plan["actions"]["sandbox_tests"]["status"] == "passed"
    assert repair_plan["actions"]["apply"]["status"] == "applied-shadow-safe-file"
    assert repair_plan["actions"]["rollback"]["status"] == "rolled-back"
    assert repair_plan["raw_content_included"] is False
    assert repair_plan["active_production_mutation_allowed"] is False
    assert repair_plan["active_production_mutated"] is False

    post_repair = repair_plan["post_repair_verification"]
    assert post_repair["status"] == "verified-post-repair-live-stage-coverage"
    assert post_repair["verified_stage_count"] == 2
    assert post_repair["candidate_consumption_count"] == 2
    assert post_repair["rollback_verified"] is True
    real_probe = post_repair["real_heartbeat_probe"]
    assert real_probe["surface_id"] == "whole-system-heartbeat-post-repair-real-probe"
    assert real_probe["status"] == "completed-live-post-repair-heartbeat-probe"
    assert real_probe["stage_ids"] == ["global_growth", "federation"]
    assert real_probe["raw_content_included"] is False
    assert real_probe["active_production_mutation_allowed"] is False
    assert real_probe["active_production_mutated"] is False
    probe_stages = {stage["stage_id"]: stage for stage in real_probe["stage_probes"]}
    assert probe_stages["global_growth"]["status"] == "covered"
    assert probe_stages["global_growth"]["receipt_id"]
    assert probe_stages["global_growth"]["runtime_growth_federated_packet_id"]
    assert probe_stages["global_growth"]["raw_content_included"] is False
    assert probe_stages["federation"]["status"] == "covered"
    assert probe_stages["federation"]["packet_id"]
    assert probe_stages["federation"]["import_id"]
    assert probe_stages["federation"]["operation_receipt_id"]
    assert probe_stages["federation"]["whole_system_enforcement_receipt_id"]
    assert probe_stages["federation"]["raw_content_included"] is False
    assert growth_calls["post_repair_probe"] == 1
    assert hive_calls["post_repair_probe"] == 1

    post_repair_tick = post_repair["post_repair_tick"]
    post_repair_stages = {stage["stage_id"]: stage for stage in post_repair_tick["stages"]}
    assert post_repair_tick["schema_version"] == "nexusnet-whole-system-heartbeat-tick-v1"
    assert post_repair_tick["surface_id"] == "whole-system-heartbeat-tick"
    assert post_repair_tick["status"] == "alive"
    assert post_repair_tick["tick_id"] != tick["tick_id"]
    assert post_repair_tick["source_tick_id"] == tick["tick_id"]
    assert post_repair_tick["source_repair_plan_id"] == repair_plan["plan_id"]
    assert post_repair_tick["source_repair_update_id"] == repair_plan["update_id"]
    assert post_repair_tick["post_repair_verification_id"] == post_repair["verification_id"]
    assert post_repair_tick["runtime_growth_receipt_id"] == probe_stages["global_growth"]["receipt_id"]
    assert post_repair_tick["federated_packet_id"] == probe_stages["federation"]["packet_id"]
    assert post_repair_tick["federated_packet_import_id"] == probe_stages["federation"]["import_id"]
    assert post_repair_stages["global_growth"]["status"] == "covered"
    assert post_repair_stages["federation"]["status"] == "covered"
    assert post_repair_tick["raw_content_included"] is False
    assert post_repair_tick["active_production_mutation_allowed"] is False
    assert post_repair_tick["active_production_mutated"] is False

    verified_stages = {stage["stage_id"]: stage for stage in post_repair["verified_stages"]}
    assert verified_stages["global_growth"]["post_repair_status"] == "covered"
    assert verified_stages["federation"]["post_repair_status"] == "covered"
    assert probe_stages["global_growth"]["receipt_id"] in verified_stages["global_growth"]["observed_evidence_refs"]
    assert probe_stages["federation"]["packet_id"] in verified_stages["federation"]["observed_evidence_refs"]
    assert probe_stages["federation"]["import_id"] in verified_stages["federation"]["observed_evidence_refs"]

    assert latest_interaction["whole_system_heartbeat_repair_plan_id"] == repair_plan["plan_id"]
    assert runtime["whole_system_heartbeat"]["status"] == "alive"
    assert runtime["whole_system_heartbeat"]["latest_tick_id"] == post_repair_tick["tick_id"]
    assert runtime["whole_system_heartbeat_tick"]["tick_id"] == post_repair_tick["tick_id"]
    assert runtime["whole_system_heartbeat_tick"]["status"] == "alive"
    assert readiness["evidence"]["whole_system_heartbeat"]["latest_repair_plan_id"] == repair_plan["plan_id"]
    assert status_card["whole_system_heartbeat"]["latest_repair_plan_id"] == repair_plan["plan_id"]
    assert control_panel["release_wrapper_runtime"]["whole_system_heartbeat"]["latest_repair_plan_id"] == (
        repair_plan["plan_id"]
    )

    tick_log = project_root / "artifacts" / "release-wrapper-runtime" / "whole-system-heartbeat-ticks.jsonl"
    persisted_ticks = [
        json.loads(line)
        for line in tick_log.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    persisted_tick = next(record for record in persisted_ticks if record["tick_id"] == tick["tick_id"])
    persisted_post_repair_tick = next(
        record for record in persisted_ticks if record["tick_id"] == post_repair_tick["tick_id"]
    )
    assert persisted_tick["status"] == "degraded"
    assert persisted_tick["repair_plan_id"] == repair_plan["plan_id"]
    assert persisted_post_repair_tick["status"] == "alive"
    assert persisted_post_repair_tick["runtime_growth_receipt_id"] == post_repair_tick["runtime_growth_receipt_id"]
    assert persisted_post_repair_tick["federated_packet_id"] == post_repair_tick["federated_packet_id"]
    assert persisted_post_repair_tick["federated_packet_import_id"] == post_repair_tick["federated_packet_import_id"]
    assert persisted_post_repair_tick["raw_content_included"] is False

    replay_client = TestClient(create_app(str(project_root)))
    replayed_runtime = replay_client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    assert replayed_runtime["whole_system_heartbeat"]["status"] == "replayed"
    assert replayed_runtime["whole_system_heartbeat"]["latest_tick_id"] == post_repair_tick["tick_id"]
    assert replayed_runtime["whole_system_heartbeat_tick"]["tick_id"] == post_repair_tick["tick_id"]
    assert replayed_runtime["whole_system_heartbeat_tick"]["status"] == "alive"

    serialized = json.dumps(
        {
            "repair_plan": repair_plan,
            "tick": tick,
            "summary": runtime["whole_system_heartbeat"],
            "readiness": readiness["evidence"]["whole_system_heartbeat"],
            "status_card": status_card["whole_system_heartbeat"],
            "control_panel": control_panel["release_wrapper_runtime"]["whole_system_heartbeat"],
            "persisted_tick": persisted_tick,
            "persisted_post_repair_tick": persisted_post_repair_tick,
            "replayed": replayed_runtime["whole_system_heartbeat"],
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-GROWTH-FEDERATION-REPAIR" not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized


def test_degraded_whole_system_heartbeat_recovers_project_heartbeat_and_storage_replay_from_live_probe(
    tmp_path: Path,
    monkeypatch,
):
    project_root = make_project(tmp_path)
    session_id = "whole-system-project-storage-repair-user"
    prompt = "Recover project heartbeat and replay storage without SECRET-PROJECT-STORAGE-REPAIR."
    client = TestClient(create_app(str(project_root)))
    runtime_obj = client.app.state.release_wrapper_runtime

    original_hive_forward = runtime_obj.hive_substrate.run_forward_pass
    hive_calls = {"count": 0, "post_repair_probe": 0}

    def _missing_then_real_project_heartbeat(request):
        hive_calls["count"] += 1
        result = original_hive_forward(request)
        task_id = str(getattr(request, "task_id", "") or "")
        if hive_calls["count"] == 1:
            degraded = dict(result)
            degraded["project_heartbeat"] = {}
            degraded["project_heartbeat_replay_record"] = {}
            return degraded
        if "whole-system-heartbeat-post-repair" in task_id:
            hive_calls["post_repair_probe"] += 1
        return result

    monkeypatch.setattr(runtime_obj.hive_substrate, "run_forward_pass", _missing_then_real_project_heartbeat)

    chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
        },
    )

    assert chat.status_code == 200
    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    readiness = client.get("/ops/wrapper/release-readiness", params={"session_id": session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]

    latest_interaction = runtime["latest_interaction"]
    tick = latest_interaction["whole_system_heartbeat_tick"]
    stages = {stage["stage_id"]: stage for stage in tick["stages"]}

    assert tick["status"] == "degraded"
    assert tick["project_heartbeat_id"] == ""
    assert tick["evidence_refs"].get("project_heartbeat_replay_ref") is None
    assert stages["project_heartbeat"]["status"] == "degraded"
    assert stages["project_heartbeat"]["blocker"] == "project_heartbeat_missing"
    assert stages["storage_replay"]["status"] == "degraded"
    assert stages["storage_replay"]["blocker"] == "storage_replay_refs_missing"

    repair_plan = latest_interaction["whole_system_heartbeat_repair_plan"]
    assert repair_plan["status"] == "completed-whole-system-heartbeat-repair"
    assert repair_plan["degraded_stage_ids"] == ["project_heartbeat", "storage_replay"]
    assert repair_plan["blockers"] == ["project_heartbeat_missing", "storage_replay_refs_missing"]
    assert repair_plan["stage_repair_candidate_count"] == 2
    assert repair_plan["lifecycle_status"] == "completed"
    assert repair_plan["actions"]["admin_approval"]["status"] == "admin-approved"
    assert repair_plan["actions"]["sandbox_tests"]["status"] == "passed"
    assert repair_plan["actions"]["apply"]["status"] == "applied-shadow-safe-file"
    assert repair_plan["actions"]["rollback"]["status"] == "rolled-back"
    assert repair_plan["raw_content_included"] is False
    assert repair_plan["active_production_mutation_allowed"] is False
    assert repair_plan["active_production_mutated"] is False

    post_repair = repair_plan["post_repair_verification"]
    assert post_repair["status"] == "verified-post-repair-live-stage-coverage"
    assert post_repair["verified_stage_count"] == 2
    assert post_repair["candidate_consumption_count"] == 2
    assert post_repair["rollback_verified"] is True
    real_probe = post_repair["real_heartbeat_probe"]
    assert real_probe["surface_id"] == "whole-system-heartbeat-post-repair-real-probe"
    assert real_probe["status"] == "completed-live-post-repair-heartbeat-probe"
    assert real_probe["stage_ids"] == ["project_heartbeat", "storage_replay"]
    assert real_probe["raw_content_included"] is False
    assert real_probe["active_production_mutation_allowed"] is False
    assert real_probe["active_production_mutated"] is False
    probe_stages = {stage["stage_id"]: stage for stage in real_probe["stage_probes"]}
    assert probe_stages["project_heartbeat"]["status"] == "covered"
    assert probe_stages["project_heartbeat"]["heartbeat_id"]
    assert probe_stages["project_heartbeat"]["wrapper_replay_record_id"]
    assert probe_stages["project_heartbeat"]["raw_content_included"] is False
    assert probe_stages["storage_replay"]["status"] == "covered"
    assert probe_stages["storage_replay"]["forward_pass_receipt_id"]
    assert probe_stages["storage_replay"]["project_heartbeat_replay_ref"]
    assert probe_stages["storage_replay"]["project_heartbeat_replay_record_id"]
    assert probe_stages["storage_replay"]["raw_content_included"] is False
    assert hive_calls["post_repair_probe"] == 1

    post_repair_tick = post_repair["post_repair_tick"]
    post_repair_stages = {stage["stage_id"]: stage for stage in post_repair_tick["stages"]}
    assert post_repair_tick["schema_version"] == "nexusnet-whole-system-heartbeat-tick-v1"
    assert post_repair_tick["surface_id"] == "whole-system-heartbeat-tick"
    assert post_repair_tick["status"] == "alive"
    assert post_repair_tick["tick_id"] != tick["tick_id"]
    assert post_repair_tick["source_tick_id"] == tick["tick_id"]
    assert post_repair_tick["source_repair_plan_id"] == repair_plan["plan_id"]
    assert post_repair_tick["source_repair_update_id"] == repair_plan["update_id"]
    assert post_repair_tick["post_repair_verification_id"] == post_repair["verification_id"]
    assert post_repair_tick["project_heartbeat_id"] == probe_stages["project_heartbeat"]["heartbeat_id"]
    assert post_repair_tick["forward_pass_receipt_id"] == probe_stages["storage_replay"]["forward_pass_receipt_id"]
    assert (
        post_repair_tick["evidence_refs"]["project_heartbeat_replay_ref"]
        == probe_stages["storage_replay"]["project_heartbeat_replay_ref"]
    )
    assert (
        post_repair_tick["evidence_refs"]["project_heartbeat_replay_record_id"]
        == probe_stages["storage_replay"]["project_heartbeat_replay_record_id"]
    )
    assert post_repair_stages["project_heartbeat"]["status"] == "covered"
    assert post_repair_stages["storage_replay"]["status"] == "covered"
    assert post_repair_tick["raw_content_included"] is False
    assert post_repair_tick["active_production_mutation_allowed"] is False
    assert post_repair_tick["active_production_mutated"] is False

    verified_stages = {stage["stage_id"]: stage for stage in post_repair["verified_stages"]}
    assert verified_stages["project_heartbeat"]["post_repair_status"] == "covered"
    assert verified_stages["storage_replay"]["post_repair_status"] == "covered"
    assert (
        probe_stages["project_heartbeat"]["heartbeat_id"]
        in verified_stages["project_heartbeat"]["observed_evidence_refs"]
    )
    assert (
        probe_stages["storage_replay"]["project_heartbeat_replay_record_id"]
        in verified_stages["storage_replay"]["observed_evidence_refs"]
    )

    assert runtime["whole_system_heartbeat"]["status"] == "alive"
    assert runtime["whole_system_heartbeat"]["latest_tick_id"] == post_repair_tick["tick_id"]
    assert runtime["whole_system_heartbeat_tick"]["tick_id"] == post_repair_tick["tick_id"]
    assert runtime["whole_system_heartbeat_tick"]["status"] == "alive"
    assert readiness["evidence"]["whole_system_heartbeat"]["latest_repair_plan_id"] == repair_plan["plan_id"]
    assert status_card["whole_system_heartbeat"]["latest_repair_plan_id"] == repair_plan["plan_id"]
    assert control_panel["release_wrapper_runtime"]["whole_system_heartbeat"]["latest_repair_plan_id"] == (
        repair_plan["plan_id"]
    )

    tick_log = project_root / "artifacts" / "release-wrapper-runtime" / "whole-system-heartbeat-ticks.jsonl"
    persisted_ticks = [
        json.loads(line)
        for line in tick_log.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    persisted_tick = next(record for record in persisted_ticks if record["tick_id"] == tick["tick_id"])
    persisted_post_repair_tick = next(
        record for record in persisted_ticks if record["tick_id"] == post_repair_tick["tick_id"]
    )
    assert persisted_tick["status"] == "degraded"
    assert persisted_tick["repair_plan_id"] == repair_plan["plan_id"]
    assert persisted_post_repair_tick["status"] == "alive"
    assert persisted_post_repair_tick["project_heartbeat_id"] == post_repair_tick["project_heartbeat_id"]
    assert persisted_post_repair_tick["forward_pass_receipt_id"] == post_repair_tick["forward_pass_receipt_id"]
    assert persisted_post_repair_tick["raw_content_included"] is False

    replay_client = TestClient(create_app(str(project_root)))
    replayed_runtime = replay_client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    assert replayed_runtime["whole_system_heartbeat"]["status"] == "replayed"
    assert replayed_runtime["whole_system_heartbeat"]["latest_tick_id"] == post_repair_tick["tick_id"]
    assert replayed_runtime["whole_system_heartbeat_tick"]["tick_id"] == post_repair_tick["tick_id"]
    assert replayed_runtime["whole_system_heartbeat_tick"]["status"] == "alive"
    assert (
        replayed_runtime["project_heartbeat_replay"]["latest_record_id"]
        == probe_stages["project_heartbeat"]["wrapper_replay_record_id"]
    )

    serialized = json.dumps(
        {
            "repair_plan": repair_plan,
            "tick": tick,
            "summary": runtime["whole_system_heartbeat"],
            "readiness": readiness["evidence"]["whole_system_heartbeat"],
            "status_card": status_card["whole_system_heartbeat"],
            "control_panel": control_panel["release_wrapper_runtime"]["whole_system_heartbeat"],
            "persisted_tick": persisted_tick,
            "persisted_post_repair_tick": persisted_post_repair_tick,
            "replayed": replayed_runtime["whole_system_heartbeat"],
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-PROJECT-STORAGE-REPAIR" not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized


def test_degraded_whole_system_heartbeat_recovers_developmental_cortex_and_dream_research_from_live_probe(
    tmp_path: Path,
    monkeypatch,
):
    project_root = make_project(tmp_path)
    session_id = "whole-system-developmental-dream-repair-user"
    prompt = "Recover developmental cortex and dream research without SECRET-DEVELOPMENTAL-DREAM-REPAIR."
    client = TestClient(create_app(str(project_root)))
    runtime_obj = client.app.state.release_wrapper_runtime

    original_developmental_assessment = runtime_obj._record_developmental_cortex_assessment
    original_dream_queue = runtime_obj._queue_dream_research_improvement
    original_dream_episode = runtime_obj._run_dream_research_episode
    developmental_calls = {"count": 0, "post_repair_probe": 0}
    dream_queue_calls = {"count": 0, "post_repair_probe": 0}
    dream_episode_calls = {"count": 0, "post_repair_probe": 0}

    def _missing_then_real_developmental(*, session_id, interaction, stage_results):
        developmental_calls["count"] += 1
        if developmental_calls["count"] == 1:
            interaction["developmental_cortex_status"] = "degraded"
            stage_results["developmental_cortex"] = {
                "status": "degraded",
                "evidence_refs": [f"trace::{interaction.get('trace_id') or 'missing'}"],
                "blocker": "test_induced_developmental_cortex_gap",
            }
            return None
        developmental_calls["post_repair_probe"] += 1
        return original_developmental_assessment(
            session_id=session_id,
            interaction=interaction,
            stage_results=stage_results,
        )

    def _missing_then_real_dream_queue(*args, **kwargs):
        dream_queue_calls["count"] += 1
        if dream_queue_calls["count"] == 1:
            return None
        interaction = kwargs.get("interaction") if isinstance(kwargs.get("interaction"), dict) else {}
        if interaction.get("dream_research_source") == "whole-system-heartbeat-post-repair":
            dream_queue_calls["post_repair_probe"] += 1
        return original_dream_queue(*args, **kwargs)

    def _record_post_repair_dream_episode(*args, **kwargs):
        dream_episode_calls["count"] += 1
        interaction = kwargs.get("interaction") if isinstance(kwargs.get("interaction"), dict) else {}
        if interaction.get("dream_research_source") == "whole-system-heartbeat-post-repair":
            dream_episode_calls["post_repair_probe"] += 1
        return original_dream_episode(*args, **kwargs)

    monkeypatch.setattr(
        runtime_obj,
        "_record_developmental_cortex_assessment",
        _missing_then_real_developmental,
    )
    monkeypatch.setattr(runtime_obj, "_queue_dream_research_improvement", _missing_then_real_dream_queue)
    monkeypatch.setattr(runtime_obj, "_run_dream_research_episode", _record_post_repair_dream_episode)

    chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
        },
    )

    assert chat.status_code == 200
    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    readiness = client.get("/ops/wrapper/release-readiness", params={"session_id": session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]

    latest_interaction = runtime["latest_interaction"]
    tick = latest_interaction["whole_system_heartbeat_tick"]
    stages = {stage["stage_id"]: stage for stage in tick["stages"]}

    assert tick["status"] == "degraded"
    assert tick["developmental_cortex_assessment_ref"] == ""
    assert tick["dream_research_episode_id"] == ""
    assert stages["developmental_cortex"]["status"] == "degraded"
    assert stages["developmental_cortex"]["blocker"] == "developmental_cortex_runtime_refs_missing"
    assert stages["dream_research"]["status"] == "degraded"
    assert stages["dream_research"]["blocker"] == "dream_research_refs_missing"

    repair_plan = latest_interaction["whole_system_heartbeat_repair_plan"]
    assert repair_plan["status"] == "completed-whole-system-heartbeat-repair"
    assert repair_plan["degraded_stage_ids"] == ["developmental_cortex", "dream_research"]
    assert repair_plan["blockers"] == ["developmental_cortex_runtime_refs_missing", "dream_research_refs_missing"]
    assert repair_plan["stage_repair_candidate_count"] == 2
    assert repair_plan["lifecycle_status"] == "completed"
    assert repair_plan["actions"]["admin_approval"]["status"] == "admin-approved"
    assert repair_plan["actions"]["sandbox_tests"]["status"] == "passed"
    assert repair_plan["actions"]["apply"]["status"] == "applied-shadow-safe-file"
    assert repair_plan["actions"]["rollback"]["status"] == "rolled-back"
    assert repair_plan["raw_content_included"] is False
    assert repair_plan["active_production_mutation_allowed"] is False
    assert repair_plan["active_production_mutated"] is False

    post_repair = repair_plan["post_repair_verification"]
    assert post_repair["status"] == "verified-post-repair-live-stage-coverage"
    assert post_repair["verified_stage_count"] == 2
    assert post_repair["candidate_consumption_count"] == 2
    assert post_repair["rollback_verified"] is True
    real_probe = post_repair["real_heartbeat_probe"]
    assert real_probe["surface_id"] == "whole-system-heartbeat-post-repair-real-probe"
    assert real_probe["status"] == "completed-live-post-repair-heartbeat-probe"
    assert real_probe["stage_ids"] == ["developmental_cortex", "dream_research"]
    assert real_probe["raw_content_included"] is False
    assert real_probe["active_production_mutation_allowed"] is False
    assert real_probe["active_production_mutated"] is False
    probe_stages = {stage["stage_id"]: stage for stage in real_probe["stage_probes"]}
    assert probe_stages["developmental_cortex"]["status"] == "covered"
    assert probe_stages["developmental_cortex"]["assessment_ref"]
    assert probe_stages["developmental_cortex"]["growth_candidate_ref"]
    assert probe_stages["developmental_cortex"]["promotion_case_ref"]
    assert probe_stages["developmental_cortex"]["raw_content_included"] is False
    assert probe_stages["dream_research"]["status"] == "covered"
    assert probe_stages["dream_research"]["queue_id"]
    assert probe_stages["dream_research"]["episode_id"]
    assert probe_stages["dream_research"]["proposal_ref"]
    assert probe_stages["dream_research"]["eval_case_ref"]
    assert probe_stages["dream_research"]["raw_content_included"] is False
    assert developmental_calls["post_repair_probe"] == 1
    assert dream_queue_calls["post_repair_probe"] == 1
    assert dream_episode_calls["post_repair_probe"] == 1

    post_repair_tick = post_repair["post_repair_tick"]
    post_repair_stages = {stage["stage_id"]: stage for stage in post_repair_tick["stages"]}
    assert post_repair_tick["schema_version"] == "nexusnet-whole-system-heartbeat-tick-v1"
    assert post_repair_tick["surface_id"] == "whole-system-heartbeat-tick"
    assert post_repair_tick["status"] == "alive"
    assert post_repair_tick["tick_id"] != tick["tick_id"]
    assert post_repair_tick["source_tick_id"] == tick["tick_id"]
    assert post_repair_tick["source_repair_plan_id"] == repair_plan["plan_id"]
    assert post_repair_tick["source_repair_update_id"] == repair_plan["update_id"]
    assert post_repair_tick["post_repair_verification_id"] == post_repair["verification_id"]
    assert (
        post_repair_tick["developmental_cortex_assessment_ref"]
        == probe_stages["developmental_cortex"]["assessment_ref"]
    )
    assert post_repair_tick["dream_research_episode_id"] == probe_stages["dream_research"]["episode_id"]
    assert post_repair_stages["developmental_cortex"]["status"] == "covered"
    assert post_repair_stages["dream_research"]["status"] == "covered"
    assert post_repair_tick["raw_content_included"] is False
    assert post_repair_tick["active_production_mutation_allowed"] is False
    assert post_repair_tick["active_production_mutated"] is False

    verified_stages = {stage["stage_id"]: stage for stage in post_repair["verified_stages"]}
    assert verified_stages["developmental_cortex"]["post_repair_status"] == "covered"
    assert verified_stages["dream_research"]["post_repair_status"] == "covered"
    assert (
        probe_stages["developmental_cortex"]["assessment_ref"]
        in verified_stages["developmental_cortex"]["observed_evidence_refs"]
    )
    assert (
        probe_stages["dream_research"]["episode_id"]
        in verified_stages["dream_research"]["observed_evidence_refs"]
    )

    assert runtime["whole_system_heartbeat"]["status"] == "alive"
    assert runtime["whole_system_heartbeat"]["latest_tick_id"] == post_repair_tick["tick_id"]
    assert runtime["whole_system_heartbeat_tick"]["tick_id"] == post_repair_tick["tick_id"]
    assert runtime["whole_system_heartbeat_tick"]["status"] == "alive"
    assert readiness["evidence"]["whole_system_heartbeat"]["latest_repair_plan_id"] == repair_plan["plan_id"]
    assert status_card["whole_system_heartbeat"]["latest_repair_plan_id"] == repair_plan["plan_id"]
    assert control_panel["release_wrapper_runtime"]["whole_system_heartbeat"]["latest_repair_plan_id"] == (
        repair_plan["plan_id"]
    )

    tick_log = project_root / "artifacts" / "release-wrapper-runtime" / "whole-system-heartbeat-ticks.jsonl"
    persisted_ticks = [
        json.loads(line)
        for line in tick_log.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    persisted_tick = next(record for record in persisted_ticks if record["tick_id"] == tick["tick_id"])
    persisted_post_repair_tick = next(
        record for record in persisted_ticks if record["tick_id"] == post_repair_tick["tick_id"]
    )
    assert persisted_tick["status"] == "degraded"
    assert persisted_tick["repair_plan_id"] == repair_plan["plan_id"]
    assert persisted_post_repair_tick["status"] == "alive"
    assert persisted_post_repair_tick["developmental_cortex_assessment_ref"] == (
        post_repair_tick["developmental_cortex_assessment_ref"]
    )
    assert persisted_post_repair_tick["dream_research_episode_id"] == post_repair_tick["dream_research_episode_id"]
    assert persisted_post_repair_tick["raw_content_included"] is False

    replay_client = TestClient(create_app(str(project_root)))
    replayed_runtime = replay_client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    assert replayed_runtime["whole_system_heartbeat"]["status"] == "replayed"
    assert replayed_runtime["whole_system_heartbeat"]["latest_tick_id"] == post_repair_tick["tick_id"]
    assert replayed_runtime["whole_system_heartbeat_tick"]["tick_id"] == post_repair_tick["tick_id"]
    assert replayed_runtime["whole_system_heartbeat_tick"]["status"] == "alive"
    assert (
        replayed_runtime["dream_research_queue"]["latest_post_repair_episode"]["episode_id"]
        == probe_stages["dream_research"]["episode_id"]
    )
    assert replayed_runtime["dream_research_queue"]["post_repair_episode_count"] >= 1

    serialized = json.dumps(
        {
            "repair_plan": repair_plan,
            "tick": tick,
            "summary": runtime["whole_system_heartbeat"],
            "readiness": readiness["evidence"]["whole_system_heartbeat"],
            "status_card": status_card["whole_system_heartbeat"],
            "control_panel": control_panel["release_wrapper_runtime"]["whole_system_heartbeat"],
            "persisted_tick": persisted_tick,
            "persisted_post_repair_tick": persisted_post_repair_tick,
            "replayed": replayed_runtime["whole_system_heartbeat"],
            "dream_research_queue": replayed_runtime["dream_research_queue"],
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-DEVELOPMENTAL-DREAM-REPAIR" not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized


def test_degraded_whole_system_heartbeat_recovers_authority_evals_tools_from_live_probe(
    tmp_path: Path,
    monkeypatch,
):
    project_root = make_project(tmp_path)
    session_id = "whole-system-authority-evals-tools-repair-user"
    prompt = "Recover authority evals and tool governance without SECRET-AUTHORITY-EVALS-TOOLS-REPAIR."
    client = TestClient(create_app(str(project_root)))
    runtime_obj = client.app.state.release_wrapper_runtime

    original_forward_governance = runtime_obj._record_authority_evidence_tool_governance
    original_native_governance = runtime_obj._record_native_runtime_growth_capture_governance
    forward_governance_calls = {"count": 0, "suppressed": 0}
    native_governance_calls = {"blocked": 0, "post_repair_probe": 0}

    def _suppress_first_forward_governance(*args, **kwargs):
        forward_governance_calls["count"] += 1
        if forward_governance_calls["suppressed"] == 0:
            forward_governance_calls["suppressed"] += 1
            return None
        return original_forward_governance(*args, **kwargs)

    def _missing_until_post_repair_native_governance(
        *,
        interaction,
        runtime_growth_receipt,
        federated_packet,
    ):
        if interaction.get("authority_evals_tools_source") == "whole-system-heartbeat-post-repair":
            native_governance_calls["post_repair_probe"] += 1
            return original_native_governance(
                interaction=interaction,
                runtime_growth_receipt=runtime_growth_receipt,
                federated_packet=federated_packet,
            )
        native_governance_calls["blocked"] += 1
        return {}

    monkeypatch.setattr(
        runtime_obj,
        "_record_authority_evidence_tool_governance",
        _suppress_first_forward_governance,
    )
    monkeypatch.setattr(
        runtime_obj,
        "_record_native_runtime_growth_capture_governance",
        _missing_until_post_repair_native_governance,
    )

    chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
        },
    )

    assert chat.status_code == 200
    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    readiness = client.get("/ops/wrapper/release-readiness", params={"session_id": session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]

    latest_interaction = runtime["latest_interaction"]
    tick = latest_interaction["whole_system_heartbeat_tick"]
    stages = {stage["stage_id"]: stage for stage in tick["stages"]}

    assert tick["status"] == "degraded"
    assert tick["evidence_refs"].get("authority_decision_id") is None
    assert tick["evidence_refs"].get("evidence_record_id") is None
    assert tick["evidence_refs"].get("eval_federation_event_id") is None
    assert tick["evidence_refs"].get("tool_action_plan_id") is None
    assert stages["authority_evals_tools"]["status"] == "degraded"
    assert stages["authority_evals_tools"]["blocker"] == "authority_eval_tool_governance_refs_missing"
    assert "authority_eval_tool_governance_refs_missing" in tick["blockers"]

    repair_plan = latest_interaction["whole_system_heartbeat_repair_plan"]
    assert repair_plan["status"] == "completed-whole-system-heartbeat-repair"
    assert repair_plan["degraded_stage_ids"] == ["authority_evals_tools"]
    assert repair_plan["blockers"] == ["authority_eval_tool_governance_refs_missing"]
    assert repair_plan["stage_repair_candidate_count"] == 1
    stage_candidate = repair_plan["stage_repair_candidates"][0]
    assert stage_candidate["stage_id"] == "authority_evals_tools"
    assert stage_candidate["repair_generator"] == "authority-evals-tools-governance-repair-candidate"
    assert stage_candidate["expected_next_evidence_refs"] == [
        "/v1/chat/completions",
        "authority-decision",
        "eval-federation-event",
        "tool-action-plan",
    ]
    assert repair_plan["lifecycle_status"] == "completed"
    assert repair_plan["actions"]["admin_approval"]["status"] == "admin-approved"
    assert repair_plan["actions"]["sandbox_tests"]["status"] == "passed"
    assert repair_plan["actions"]["apply"]["status"] == "applied-shadow-safe-file"
    assert repair_plan["actions"]["rollback"]["status"] == "rolled-back"
    assert repair_plan["raw_content_included"] is False
    assert repair_plan["active_production_mutation_allowed"] is False
    assert repair_plan["active_production_mutated"] is False

    post_repair = repair_plan["post_repair_verification"]
    assert post_repair["status"] == "verified-post-repair-live-stage-coverage"
    assert post_repair["verified_stage_count"] == 1
    assert post_repair["candidate_consumption_count"] == 1
    assert post_repair["rollback_verified"] is True
    real_probe = post_repair["real_heartbeat_probe"]
    assert real_probe["surface_id"] == "whole-system-heartbeat-post-repair-real-probe"
    assert real_probe["status"] == "completed-live-post-repair-heartbeat-probe"
    assert real_probe["stage_ids"] == ["authority_evals_tools"]
    assert real_probe["raw_content_included"] is False
    assert real_probe["active_production_mutation_allowed"] is False
    assert real_probe["active_production_mutated"] is False
    probe_stages = {stage["stage_id"]: stage for stage in real_probe["stage_probes"]}
    assert probe_stages["authority_evals_tools"]["status"] == "covered"
    assert probe_stages["authority_evals_tools"]["authority_decision_id"]
    assert probe_stages["authority_evals_tools"]["evidence_record_id"]
    assert probe_stages["authority_evals_tools"]["eval_federation_event_id"]
    assert probe_stages["authority_evals_tools"]["tool_action_plan_id"]
    assert probe_stages["authority_evals_tools"]["raw_content_included"] is False
    assert real_probe["authority_decision_id"] == probe_stages["authority_evals_tools"]["authority_decision_id"]
    assert real_probe["evidence_record_id"] == probe_stages["authority_evals_tools"]["evidence_record_id"]
    assert real_probe["eval_federation_event_id"] == (
        probe_stages["authority_evals_tools"]["eval_federation_event_id"]
    )
    assert real_probe["tool_action_plan_id"] == probe_stages["authority_evals_tools"]["tool_action_plan_id"]
    assert forward_governance_calls["suppressed"] == 1
    assert native_governance_calls["blocked"] >= 1
    assert native_governance_calls["post_repair_probe"] == 1

    post_repair_tick = post_repair["post_repair_tick"]
    post_repair_stages = {stage["stage_id"]: stage for stage in post_repair_tick["stages"]}
    post_repair_refs = post_repair_tick["evidence_refs"]
    assert post_repair_tick["schema_version"] == "nexusnet-whole-system-heartbeat-tick-v1"
    assert post_repair_tick["surface_id"] == "whole-system-heartbeat-tick"
    assert post_repair_tick["status"] == "alive"
    assert post_repair_tick["tick_id"] != tick["tick_id"]
    assert post_repair_tick["source_tick_id"] == tick["tick_id"]
    assert post_repair_tick["source_repair_plan_id"] == repair_plan["plan_id"]
    assert post_repair_tick["source_repair_update_id"] == repair_plan["update_id"]
    assert post_repair_tick["post_repair_verification_id"] == post_repair["verification_id"]
    assert post_repair_refs["authority_decision_id"] == real_probe["authority_decision_id"]
    assert post_repair_refs["evidence_record_id"] == real_probe["evidence_record_id"]
    assert post_repair_refs["eval_federation_event_id"] == real_probe["eval_federation_event_id"]
    assert post_repair_refs["tool_action_plan_id"] == real_probe["tool_action_plan_id"]
    assert post_repair_stages["authority_evals_tools"]["status"] == "covered"
    assert post_repair_tick["raw_content_included"] is False
    assert post_repair_tick["active_production_mutation_allowed"] is False
    assert post_repair_tick["active_production_mutated"] is False

    verified_stage = post_repair["verified_stages"][0]
    assert verified_stage["stage_id"] == "authority_evals_tools"
    assert verified_stage["post_repair_status"] == "covered"
    assert real_probe["authority_decision_id"] in verified_stage["observed_evidence_refs"]
    assert real_probe["evidence_record_id"] in verified_stage["observed_evidence_refs"]
    assert real_probe["eval_federation_event_id"] in verified_stage["observed_evidence_refs"]
    assert real_probe["tool_action_plan_id"] in verified_stage["observed_evidence_refs"]

    assert runtime["whole_system_heartbeat"]["status"] == "alive"
    assert runtime["whole_system_heartbeat"]["latest_tick_id"] == post_repair_tick["tick_id"]
    assert runtime["whole_system_heartbeat_tick"]["tick_id"] == post_repair_tick["tick_id"]
    assert runtime["whole_system_heartbeat_tick"]["status"] == "alive"
    assert readiness["evidence"]["whole_system_heartbeat"]["latest_repair_plan_id"] == repair_plan["plan_id"]
    assert status_card["whole_system_heartbeat"]["latest_repair_plan_id"] == repair_plan["plan_id"]
    assert control_panel["release_wrapper_runtime"]["whole_system_heartbeat"]["latest_repair_plan_id"] == (
        repair_plan["plan_id"]
    )

    tick_log = project_root / "artifacts" / "release-wrapper-runtime" / "whole-system-heartbeat-ticks.jsonl"
    persisted_ticks = [
        json.loads(line)
        for line in tick_log.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    persisted_tick = next(record for record in persisted_ticks if record["tick_id"] == tick["tick_id"])
    persisted_post_repair_tick = next(
        record for record in persisted_ticks if record["tick_id"] == post_repair_tick["tick_id"]
    )
    assert persisted_tick["status"] == "degraded"
    assert persisted_tick["repair_plan_id"] == repair_plan["plan_id"]
    assert persisted_post_repair_tick["status"] == "alive"
    assert persisted_post_repair_tick["evidence_refs"]["authority_decision_id"] == real_probe["authority_decision_id"]
    assert persisted_post_repair_tick["evidence_refs"]["evidence_record_id"] == real_probe["evidence_record_id"]
    assert persisted_post_repair_tick["raw_content_included"] is False

    replay_client = TestClient(create_app(str(project_root)))
    replayed_runtime = replay_client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    assert replayed_runtime["whole_system_heartbeat"]["status"] == "replayed"
    assert replayed_runtime["whole_system_heartbeat"]["latest_tick_id"] == post_repair_tick["tick_id"]
    assert replayed_runtime["whole_system_heartbeat_tick"]["tick_id"] == post_repair_tick["tick_id"]
    assert replayed_runtime["whole_system_heartbeat_tick"]["status"] == "alive"

    serialized = json.dumps(
        {
            "repair_plan": repair_plan,
            "tick": tick,
            "summary": runtime["whole_system_heartbeat"],
            "readiness": readiness["evidence"]["whole_system_heartbeat"],
            "status_card": status_card["whole_system_heartbeat"],
            "control_panel": control_panel["release_wrapper_runtime"]["whole_system_heartbeat"],
            "persisted_tick": persisted_tick,
            "persisted_post_repair_tick": persisted_post_repair_tick,
            "replayed": replayed_runtime["whole_system_heartbeat"],
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-AUTHORITY-EVALS-TOOLS-REPAIR" not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized


def test_degraded_whole_system_heartbeat_recovers_self_repair_update_governance_from_live_probe(
    tmp_path: Path,
    monkeypatch,
):
    project_root = make_project(tmp_path)
    session_id = "whole-system-self-repair-governance-repair-user"
    prompt = "Recover self repair update governance without SECRET-SELF-REPAIR-GOVERNANCE-REPAIR."
    client = TestClient(create_app(str(project_root)))
    runtime_obj = client.app.state.release_wrapper_runtime

    original_lifecycle = runtime_obj._record_autonomous_update_governance_lifecycle
    lifecycle_calls = {"suppressed_runtime_auto": 0, "repair_plan": 0, "post_repair_probe": 0}

    def _missing_first_runtime_lifecycle(
        *,
        session_id,
        update_id,
        command="pytest -q tests/test_release_wrapper_runtime.py",
        timeout_seconds=60,
        approved_by="admin",
        approval_ref="operator-review::release-wrapper-runtime-auto-governance",
    ):
        if (
            approval_ref == "operator-review::release-wrapper-runtime-auto-governance"
            and lifecycle_calls["suppressed_runtime_auto"] == 0
        ):
            lifecycle_calls["suppressed_runtime_auto"] += 1
            return {
                "surface_id": "release-wrapper-readiness-evidence-run",
                "status": "blocked-test-induced-self-repair-governance-gap",
                "update_id": update_id,
                "run_id": "",
                "actions": {},
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
                "active_production_mutated": False,
            }
        if approval_ref == "operator-review::whole-system-heartbeat-degraded-stage-repair":
            lifecycle_calls["repair_plan"] += 1
        if approval_ref == "operator-review::whole-system-heartbeat-post-repair-self-repair-governance":
            lifecycle_calls["post_repair_probe"] += 1
        return original_lifecycle(
            session_id=session_id,
            update_id=update_id,
            command=command,
            timeout_seconds=timeout_seconds,
            approved_by=approved_by,
            approval_ref=approval_ref,
        )

    monkeypatch.setattr(
        runtime_obj,
        "_record_autonomous_update_governance_lifecycle",
        _missing_first_runtime_lifecycle,
    )

    chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
        },
    )

    assert chat.status_code == 200
    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    readiness = client.get("/ops/wrapper/release-readiness", params={"session_id": session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]

    latest_interaction = runtime["latest_interaction"]
    tick = latest_interaction["whole_system_heartbeat_tick"]
    stages = {stage["stage_id"]: stage for stage in tick["stages"]}

    assert tick["status"] == "degraded"
    assert tick["autonomous_update_lifecycle_run_id"] == ""
    assert tick["evidence_refs"].get("autonomous_update_lifecycle_update_id")
    assert stages["self_repair_update_governance"]["status"] == "degraded"
    assert (
        stages["self_repair_update_governance"]["blocker"]
        == "self_repair_update_governance_refs_missing"
    )
    assert "self_repair_update_governance_refs_missing" in tick["blockers"]

    repair_plan = latest_interaction["whole_system_heartbeat_repair_plan"]
    assert repair_plan["status"] == "completed-whole-system-heartbeat-repair"
    assert repair_plan["degraded_stage_ids"] == ["self_repair_update_governance"]
    assert repair_plan["blockers"] == ["self_repair_update_governance_refs_missing"]
    assert repair_plan["stage_repair_candidate_count"] == 1
    stage_candidate = repair_plan["stage_repair_candidates"][0]
    assert stage_candidate["stage_id"] == "self_repair_update_governance"
    assert stage_candidate["repair_generator"] == "self-repair-update-governance-lifecycle-repair-candidate"
    assert stage_candidate["expected_next_evidence_refs"] == [
        "/ops/brain/autonomous-updates/{update_id}/admin-approval",
        "/ops/brain/autonomous-updates/{update_id}/sandbox-tests",
        "/ops/brain/autonomous-updates/{update_id}/apply",
        "/ops/brain/autonomous-updates/{update_id}/rollback",
    ]
    assert repair_plan["lifecycle_status"] == "completed"
    assert repair_plan["actions"]["admin_approval"]["status"] == "admin-approved"
    assert repair_plan["actions"]["sandbox_tests"]["status"] == "passed"
    assert repair_plan["actions"]["apply"]["status"] == "applied-shadow-safe-file"
    assert repair_plan["actions"]["rollback"]["status"] == "rolled-back"
    assert repair_plan["raw_content_included"] is False
    assert repair_plan["active_production_mutation_allowed"] is False
    assert repair_plan["active_production_mutated"] is False

    post_repair = repair_plan["post_repair_verification"]
    assert post_repair["status"] == "verified-post-repair-live-stage-coverage"
    assert post_repair["verified_stage_count"] == 1
    assert post_repair["candidate_consumption_count"] == 1
    assert post_repair["rollback_verified"] is True
    real_probe = post_repair["real_heartbeat_probe"]
    assert real_probe["surface_id"] == "whole-system-heartbeat-post-repair-real-probe"
    assert real_probe["status"] == "completed-live-post-repair-heartbeat-probe"
    assert real_probe["stage_ids"] == ["self_repair_update_governance"]
    assert real_probe["raw_content_included"] is False
    assert real_probe["active_production_mutation_allowed"] is False
    assert real_probe["active_production_mutated"] is False
    probe_stages = {stage["stage_id"]: stage for stage in real_probe["stage_probes"]}
    assert probe_stages["self_repair_update_governance"]["status"] == "covered"
    assert probe_stages["self_repair_update_governance"]["lifecycle_run_id"]
    assert probe_stages["self_repair_update_governance"]["update_id"]
    assert probe_stages["self_repair_update_governance"]["lifecycle_status"] == "completed"
    assert probe_stages["self_repair_update_governance"]["admin_approval_status"] == "admin-approved"
    assert probe_stages["self_repair_update_governance"]["sandbox_status"] == "passed"
    assert probe_stages["self_repair_update_governance"]["apply_status"] == "applied-shadow-safe-file"
    assert probe_stages["self_repair_update_governance"]["rollback_status"] == "rolled-back"
    assert probe_stages["self_repair_update_governance"]["rollback_verified"] is True
    assert probe_stages["self_repair_update_governance"]["raw_content_included"] is False
    assert real_probe["autonomous_update_lifecycle_run_id"] == (
        probe_stages["self_repair_update_governance"]["lifecycle_run_id"]
    )
    assert real_probe["autonomous_update_lifecycle_update_id"] == (
        probe_stages["self_repair_update_governance"]["update_id"]
    )
    assert lifecycle_calls["suppressed_runtime_auto"] == 1
    assert lifecycle_calls["repair_plan"] == 1
    assert lifecycle_calls["post_repair_probe"] == 1

    post_repair_tick = post_repair["post_repair_tick"]
    post_repair_stages = {stage["stage_id"]: stage for stage in post_repair_tick["stages"]}
    post_repair_refs = post_repair_tick["evidence_refs"]
    assert post_repair_tick["schema_version"] == "nexusnet-whole-system-heartbeat-tick-v1"
    assert post_repair_tick["surface_id"] == "whole-system-heartbeat-tick"
    assert post_repair_tick["status"] == "alive"
    assert post_repair_tick["tick_id"] != tick["tick_id"]
    assert post_repair_tick["source_tick_id"] == tick["tick_id"]
    assert post_repair_tick["source_repair_plan_id"] == repair_plan["plan_id"]
    assert post_repair_tick["source_repair_update_id"] == repair_plan["update_id"]
    assert post_repair_tick["post_repair_verification_id"] == post_repair["verification_id"]
    assert post_repair_tick["autonomous_update_lifecycle_run_id"] == real_probe["autonomous_update_lifecycle_run_id"]
    assert post_repair_refs["autonomous_update_lifecycle_update_id"] == (
        real_probe["autonomous_update_lifecycle_update_id"]
    )
    assert post_repair_stages["self_repair_update_governance"]["status"] == "covered"
    assert post_repair_tick["raw_content_included"] is False
    assert post_repair_tick["active_production_mutation_allowed"] is False
    assert post_repair_tick["active_production_mutated"] is False

    verified_stage = post_repair["verified_stages"][0]
    assert verified_stage["stage_id"] == "self_repair_update_governance"
    assert verified_stage["post_repair_status"] == "covered"
    assert real_probe["autonomous_update_lifecycle_run_id"] in verified_stage["observed_evidence_refs"]
    assert real_probe["autonomous_update_lifecycle_update_id"] in verified_stage["observed_evidence_refs"]

    assert runtime["whole_system_heartbeat"]["status"] == "alive"
    assert runtime["whole_system_heartbeat"]["latest_tick_id"] == post_repair_tick["tick_id"]
    assert runtime["whole_system_heartbeat_tick"]["tick_id"] == post_repair_tick["tick_id"]
    assert runtime["whole_system_heartbeat_tick"]["status"] == "alive"
    assert runtime["release_readiness_evidence_runner"]["latest_autonomous_update_lifecycle_status"] == "completed"
    assert readiness["evidence"]["whole_system_heartbeat"]["latest_repair_plan_id"] == repair_plan["plan_id"]
    assert status_card["whole_system_heartbeat"]["latest_repair_plan_id"] == repair_plan["plan_id"]
    assert control_panel["release_wrapper_runtime"]["whole_system_heartbeat"]["latest_repair_plan_id"] == (
        repair_plan["plan_id"]
    )

    tick_log = project_root / "artifacts" / "release-wrapper-runtime" / "whole-system-heartbeat-ticks.jsonl"
    persisted_ticks = [
        json.loads(line)
        for line in tick_log.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    persisted_tick = next(record for record in persisted_ticks if record["tick_id"] == tick["tick_id"])
    persisted_post_repair_tick = next(
        record for record in persisted_ticks if record["tick_id"] == post_repair_tick["tick_id"]
    )
    assert persisted_tick["status"] == "degraded"
    assert persisted_tick["repair_plan_id"] == repair_plan["plan_id"]
    assert persisted_post_repair_tick["status"] == "alive"
    assert persisted_post_repair_tick["autonomous_update_lifecycle_run_id"] == (
        real_probe["autonomous_update_lifecycle_run_id"]
    )
    assert persisted_post_repair_tick["raw_content_included"] is False

    replay_client = TestClient(create_app(str(project_root)))
    replayed_runtime = replay_client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    assert replayed_runtime["whole_system_heartbeat"]["status"] == "replayed"
    assert replayed_runtime["whole_system_heartbeat"]["latest_tick_id"] == post_repair_tick["tick_id"]
    assert replayed_runtime["whole_system_heartbeat_tick"]["tick_id"] == post_repair_tick["tick_id"]
    assert replayed_runtime["whole_system_heartbeat_tick"]["status"] == "alive"

    serialized = json.dumps(
        {
            "repair_plan": repair_plan,
            "tick": tick,
            "summary": runtime["whole_system_heartbeat"],
            "readiness": readiness["evidence"]["whole_system_heartbeat"],
            "status_card": status_card["whole_system_heartbeat"],
            "control_panel": control_panel["release_wrapper_runtime"]["whole_system_heartbeat"],
            "persisted_tick": persisted_tick,
            "persisted_post_repair_tick": persisted_post_repair_tick,
            "replayed": replayed_runtime["whole_system_heartbeat"],
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-SELF-REPAIR-GOVERNANCE-REPAIR" not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized


def test_release_wrapper_live_use_records_default_off_privacy_consent_for_federation_and_dreaming(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    session_id = "privacy-consent-user"
    prompt = "Route learning through consent defaults without leaking SECRET-PRIVACY-CONSENT."

    response = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
        },
    )

    assert response.status_code == 200
    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]
    consent = runtime["privacy_consent"]
    latest_record = consent["latest_record"]

    assert consent["surface_id"] == "release-wrapper-privacy-consent-ledger"
    assert consent["status"] == "sanitized-metadata-enabled-personal-data-default-off"
    assert consent["personal_data_training_opt_in"] is False
    assert consent["personal_data_federation_allowed"] is False
    assert consent["personal_data_dream_training_allowed"] is False
    assert consent["sanitized_metadata_federation_allowed"] is True
    assert consent["sanitized_dream_research_allowed"] is True
    assert consent["latest_record_id"] == latest_record["record_id"]
    assert latest_record["session_ref_digest"] == runtime["session_ref_digest"]
    assert latest_record["session_id"] is None
    assert latest_record["raw_content_included"] is False
    assert latest_record["active_production_mutation_allowed"] is False
    assert consent["config_refs"] == {
        "consent": "runtime/config/consent.yaml",
        "privacy": "runtime/config/privacy.yaml",
    }
    assert (project_root / "runtime" / "config" / "consent.yaml").is_file()
    assert (project_root / "runtime" / "config" / "privacy.yaml").is_file()

    interaction = runtime["latest_interaction"]
    assert interaction["privacy_consent_record_id"] == latest_record["record_id"]
    assert interaction["personal_data_training_opt_in"] is False
    assert interaction["personal_data_federation_allowed"] is False
    assert interaction["personal_data_dream_training_allowed"] is False

    packet_policy = runtime["latest_federated_packet"]["consent_policy"]
    assert packet_policy["record_id"] == latest_record["record_id"]
    assert packet_policy["personal_data_training_opt_in"] is False
    assert packet_policy["personal_data_federation_allowed"] is False
    assert packet_policy["sanitized_metadata_federation_allowed"] is True
    assert packet_policy["federated_packet_scope"] == "sanitized-metadata-only"
    assert runtime["federated_packet_outbox"]["privacy_consent"]["latest_record_id"] == latest_record["record_id"]

    dream_item = runtime["dream_research_queue"]["latest_item"]
    assert dream_item["metadata"]["privacy_consent_record_id"] == latest_record["record_id"]
    assert dream_item["metadata"]["personal_data_training_opt_in"] is False
    assert dream_item["metadata"]["dream_training_personal_data_allowed"] is False
    assert dream_item["metadata"]["sanitized_dream_research_allowed"] is True

    production_packet = runtime["production_spine"]["latest_packet"]
    replay_evidence = production_packet["federated_influence_replay_evidence"]
    assert replay_evidence["consent_granted"] is True
    assert replay_evidence["consent_basis"] == "sanitized-metadata-only-no-personal-data"
    assert production_packet["consent_policy"]["record_id"] == latest_record["record_id"]

    assert status_card["privacy_consent"]["latest_record_id"] == latest_record["record_id"]
    assert control_panel["release_wrapper_runtime"]["privacy_consent"]["latest_record_id"] == latest_record["record_id"]
    assert control_panel["release_wrapper_privacy_consent"]["status"] == consent["status"]

    restarted = TestClient(create_app(str(project_root)))
    replayed = restarted.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    assert replayed["privacy_consent"]["replay"]["status"] == "replayed"
    assert replayed["privacy_consent"]["latest_record_id"] == latest_record["record_id"]
    assert replayed["latest_interaction"]["privacy_consent_record_id"] == latest_record["record_id"]

    serialized = json.dumps(
        {
            "runtime": runtime["privacy_consent"],
            "latest_interaction": interaction,
            "latest_federated_packet": runtime["latest_federated_packet"],
            "dream_research_queue": runtime["dream_research_queue"],
            "production_spine": runtime["production_spine"],
            "status_card": status_card["privacy_consent"],
            "control_panel": control_panel["release_wrapper_privacy_consent"],
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-PRIVACY-CONSENT" not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized


def test_release_wrapper_privacy_consent_opt_in_and_revocation_gate_live_learning_paths(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    session_id = "privacy-consent-governance-user"

    default_chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [
                {
                    "role": "user",
                    "content": "Use default consent gates without leaking SECRET-CONSENT-GOVERNANCE-DEFAULT.",
                }
            ],
        },
    )
    assert default_chat.status_code == 200

    opt_in = client.post(
        "/ops/wrapper/privacy-consent",
        json={
            "session_id": session_id,
            "decision": "opt-in",
            "personal_data_training_opt_in": True,
            "personal_data_federation_allowed": True,
            "personal_data_dream_training_allowed": True,
            "approved_by": "admin",
            "approval_ref": "operator-consent::privacy-consent-governance-user",
        },
    )
    assert opt_in.status_code == 200
    opt_in_payload = opt_in.json()
    assert opt_in_payload["status"] == "personal-data-training-opted-in"
    assert opt_in_payload["latest_record"]["consent_state"] == "explicit-opt-in-personal-data"
    assert opt_in_payload["latest_record"]["raw_content_included"] is False

    opted_in_chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [
                {
                    "role": "user",
                    "content": "Route learning through explicit consent without leaking SECRET-CONSENT-GOVERNANCE-OPTIN.",
                }
            ],
        },
    )
    assert opted_in_chat.status_code == 200

    opted_in_runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    opted_in_status_card = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    opted_in_visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    opted_in_control_panel = opted_in_visualizer["overlay_state"]["control_panel"]
    opted_in_consent = opted_in_runtime["privacy_consent"]
    opted_in_record = opted_in_consent["latest_record"]

    assert opted_in_consent["status"] == "personal-data-training-opted-in"
    assert opted_in_consent["personal_data_training_opt_in"] is True
    assert opted_in_consent["personal_data_federation_allowed"] is True
    assert opted_in_consent["personal_data_dream_training_allowed"] is True
    assert opted_in_consent["retention_enforcement"]["status"] == "enforced"
    assert opted_in_consent["retention_enforcement"]["raw_prompt_export"] == "forbidden"
    assert opted_in_consent["retention_enforcement"]["personal_data_training_gate"] == "explicit-opt-in"
    assert opted_in_record["approved_by_ref"] == "admin"
    assert opted_in_record["approval_ref"] == "approval-ref-redacted"
    assert opted_in_record["approval_ref_digest"].startswith("sha256:")
    assert opted_in_record["revoked_at"] is None

    opted_in_policy = opted_in_runtime["latest_federated_packet"]["consent_policy"]
    assert opted_in_policy["record_id"] == opted_in_record["record_id"]
    assert opted_in_policy["personal_data_training_opt_in"] is True
    assert opted_in_policy["personal_data_federation_allowed"] is True
    assert opted_in_policy["personal_data_dream_training_allowed"] is True
    assert opted_in_policy["federated_packet_scope"] == "sanitized-metadata-plus-consented-derived-features"
    assert opted_in_policy["raw_content_included"] is False
    assert opted_in_policy["contains_personal_data"] is False

    opted_in_dream_metadata = opted_in_runtime["dream_research_queue"]["latest_item"]["metadata"]
    assert opted_in_dream_metadata["privacy_consent_record_id"] == opted_in_record["record_id"]
    assert opted_in_dream_metadata["personal_data_training_opt_in"] is True
    assert opted_in_dream_metadata["dream_training_personal_data_allowed"] is True
    assert opted_in_dream_metadata["sanitized_dream_research_allowed"] is True
    assert opted_in_runtime["production_spine"]["latest_packet"]["consent_policy"]["record_id"] == opted_in_record["record_id"]
    assert (
        opted_in_runtime["production_spine"]["latest_packet"]["federated_influence_replay_evidence"]["consent_basis"]
        == "explicit-opt-in-personal-data-authorized-sanitized-derivatives-only"
    )
    assert opted_in_status_card["privacy_consent"]["latest_record_id"] == opted_in_record["record_id"]
    assert opted_in_status_card["endpoint_refs"]["privacy_consent"] == "/ops/wrapper/privacy-consent"
    assert opted_in_control_panel["release_wrapper_privacy_consent"]["latest_record_id"] == opted_in_record["record_id"]

    revoke = client.post(
        "/ops/wrapper/privacy-consent",
        json={
            "session_id": session_id,
            "decision": "revoke",
            "approved_by": "admin",
            "approval_ref": "operator-consent::privacy-consent-governance-user-revocation",
        },
    )
    assert revoke.status_code == 200
    revoke_payload = revoke.json()
    assert revoke_payload["status"] == "personal-data-training-revoked-default-off"
    assert revoke_payload["latest_record"]["revoked_at"] is not None

    revoked_chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [
                {
                    "role": "user",
                    "content": "Route learning after revocation without leaking SECRET-CONSENT-GOVERNANCE-REVOKED.",
                }
            ],
        },
    )
    assert revoked_chat.status_code == 200

    revoked_runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    revoked_consent = revoked_runtime["privacy_consent"]
    revoked_policy = revoked_runtime["latest_federated_packet"]["consent_policy"]
    assert revoked_consent["status"] == "personal-data-training-revoked-default-off"
    assert revoked_consent["personal_data_training_opt_in"] is False
    assert revoked_consent["personal_data_federation_allowed"] is False
    assert revoked_consent["personal_data_dream_training_allowed"] is False
    assert revoked_consent["retention_enforcement"]["personal_data_training_gate"] == "blocked-without-active-opt-in"
    assert revoked_policy["personal_data_training_opt_in"] is False
    assert revoked_policy["federated_packet_scope"] == "sanitized-metadata-only"
    assert revoked_runtime["dream_research_queue"]["latest_item"]["metadata"]["dream_training_personal_data_allowed"] is False
    assert revoked_runtime["privacy_consent"]["record_count"] >= 5

    restarted = TestClient(create_app(str(project_root)))
    replayed = restarted.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    assert replayed["privacy_consent"]["replay"]["status"] == "replayed"
    assert replayed["privacy_consent"]["status"] == "personal-data-training-revoked-default-off"
    assert replayed["privacy_consent"]["personal_data_training_opt_in"] is False

    serialized = json.dumps(
        {
            "opt_in": opt_in_payload,
            "opted_in_runtime": opted_in_runtime["privacy_consent"],
            "opted_in_packet": opted_in_runtime["latest_federated_packet"],
            "revoked_runtime": revoked_runtime["privacy_consent"],
            "revoked_packet": revoked_runtime["latest_federated_packet"],
            "status_card": opted_in_status_card["privacy_consent"],
            "control_panel": opted_in_control_panel["release_wrapper_privacy_consent"],
        },
        sort_keys=True,
    )
    assert "SECRET-CONSENT-GOVERNANCE-DEFAULT" not in serialized
    assert "SECRET-CONSENT-GOVERNANCE-OPTIN" not in serialized
    assert "SECRET-CONSENT-GOVERNANCE-REVOKED" not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized


def test_release_wrapper_privacy_revocation_quarantines_existing_personal_data_learning_artifacts(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    session_id = "privacy-consent-enforcement-user"
    prompt = "Queue consented learning artifacts without leaking SECRET-CONSENT-ENFORCEMENT-OPTIN."

    opt_in = client.post(
        "/ops/wrapper/privacy-consent",
        json={
            "session_id": session_id,
            "decision": "opt-in",
            "personal_data_training_opt_in": True,
            "personal_data_federation_allowed": True,
            "personal_data_dream_training_allowed": True,
            "approved_by": "admin",
            "approval_ref": "operator-consent::privacy-consent-enforcement-user",
        },
    )
    assert opt_in.status_code == 200

    opted_in_chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    assert opted_in_chat.status_code == 200

    opted_in_runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    opted_in_item = opted_in_runtime["dream_research_queue"]["latest_item"]
    opted_in_item_metadata = opted_in_item["metadata"]
    opted_in_packet = opted_in_runtime["latest_federated_packet"]
    opted_in_packet_id = opted_in_packet["packet_id"]
    assert opted_in_item_metadata["personal_data_training_opt_in"] is True
    assert opted_in_item_metadata["dream_training_personal_data_allowed"] is True
    assert opted_in_packet["consent_policy"]["personal_data_training_opt_in"] is True

    revoke = client.post(
        "/ops/wrapper/privacy-consent",
        json={
            "session_id": session_id,
            "decision": "revoke",
            "approved_by": "admin",
            "approval_ref": "operator-consent::privacy-consent-enforcement-user-revocation",
        },
    )
    assert revoke.status_code == 200
    revoke_payload = revoke.json()
    assert revoke_payload["status"] == "personal-data-training-revoked-default-off"

    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]

    enforcement = runtime["privacy_consent_enforcement"]
    assert enforcement["surface_id"] == "release-wrapper-privacy-consent-enforcement"
    assert enforcement["status"] == "revocation-enforced"
    assert enforcement["session_ref_digest"] == runtime["session_ref_digest"]
    assert enforcement["latest_record"]["revocation_consent_record_id"] == revoke_payload["latest_record_id"]
    assert enforcement["latest_record"]["decision_record_id"] == revoke_payload["latest_record_id"]
    assert enforcement["active_personal_data_training_allowed"] is False
    assert enforcement["active_production_mutation_allowed"] is False
    assert enforcement["raw_content_included"] is False
    assert enforcement["contains_personal_data"] is False
    assert enforcement["revoked_personal_data_queue_count"] >= 1
    assert enforcement["revoked_federated_packet_count"] >= 1
    assert "personal-data-dream-training" in enforcement["blocked_capabilities"]
    assert "personal-data-federation" in enforcement["blocked_capabilities"]

    queue_blocks = enforcement["latest_record"]["queue_blocks"]
    packet_blocks = enforcement["latest_record"]["federated_packet_blocks"]
    assert any(block["queue_id"] == opted_in_item["queue_id"] for block in queue_blocks)
    blocked_queue = next(block for block in queue_blocks if block["queue_id"] == opted_in_item["queue_id"])
    assert blocked_queue["quarantine_state"] == "blocked-by-revocation"
    assert blocked_queue["personal_data_training_opt_in"] is True
    assert blocked_queue["active_personal_data_training_allowed"] is False
    assert any(block["packet_id"] == opted_in_packet_id for block in packet_blocks)
    blocked_packet = next(block for block in packet_blocks if block["packet_id"] == opted_in_packet_id)
    assert blocked_packet["quarantine_state"] == "blocked-by-revocation"
    assert blocked_packet["federated_packet_scope"] == "sanitized-metadata-plus-consented-derived-features"

    assert runtime["privacy_consent"]["queue_enforcement"]["latest_record_id"] == enforcement["latest_record_id"]
    assert (
        runtime["dream_research_queue"]["privacy_consent_enforcement"]["latest_record_id"]
        == enforcement["latest_record_id"]
    )
    assert (
        runtime["federated_packet_outbox"]["privacy_consent_enforcement"]["latest_record_id"]
        == enforcement["latest_record_id"]
    )
    assert status_card["privacy_consent_enforcement"]["latest_record_id"] == enforcement["latest_record_id"]
    assert (
        control_panel["release_wrapper_privacy_consent_enforcement"]["latest_record_id"]
        == enforcement["latest_record_id"]
    )
    assert (
        control_panel["release_wrapper_runtime"]["privacy_consent_enforcement"]["latest_record_id"]
        == enforcement["latest_record_id"]
    )

    restarted = TestClient(create_app(str(project_root)))
    replayed = restarted.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    assert replayed["privacy_consent_enforcement"]["replay"]["status"] == "replayed"
    assert replayed["privacy_consent_enforcement"]["latest_record_id"] == enforcement["latest_record_id"]
    assert replayed["dream_research_queue"]["privacy_consent_enforcement"]["status"] == "revocation-enforced"

    serialized = json.dumps(
        {
            "revoke": revoke_payload,
            "runtime_enforcement": enforcement,
            "dream_research_queue": runtime["dream_research_queue"],
            "federated_packet_outbox": runtime["federated_packet_outbox"],
            "status_card": status_card["privacy_consent_enforcement"],
            "control_panel": control_panel["release_wrapper_privacy_consent_enforcement"],
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-CONSENT-ENFORCEMENT-OPTIN" not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized


def test_release_wrapper_revocation_blocks_personal_data_import_promotion_but_allows_sanitized_import(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    session_id = "privacy-consent-import-promotion-user"
    peer_node_id = "peer-node-secret-consent-import-promotion"
    opt_in_prompt = "Create an opted-in federated packet without leaking SECRET-CONSENT-IMPORT-OPTIN."
    revoked_prompt = "Create a metadata-only packet after revocation without leaking SECRET-CONSENT-IMPORT-REVOKED."

    opt_in = client.post(
        "/ops/wrapper/privacy-consent",
        json={
            "session_id": session_id,
            "decision": "opt-in",
            "personal_data_training_opt_in": True,
            "personal_data_federation_allowed": True,
            "personal_data_dream_training_allowed": True,
            "approved_by": "admin",
            "approval_ref": "operator-consent::privacy-consent-import-promotion-user",
        },
    )
    assert opt_in.status_code == 200

    opted_in_chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": opt_in_prompt}],
        },
    )
    assert opted_in_chat.status_code == 200
    opted_in_packet = client.get("/ops/wrapper/federated-packets", params={"session_id": session_id}).json()[
        "latest_packet"
    ]
    assert opted_in_packet["consent_policy"]["personal_data_training_opt_in"] is True

    accepted_before_revoke = client.post(
        "/ops/wrapper/federated-packets/import",
        json={"session_id": session_id, "peer_node_id": peer_node_id, "packet": opted_in_packet},
    ).json()
    assert accepted_before_revoke["status"] == "quarantined-shadow-accepted"
    assert accepted_before_revoke["global_growth_shadow_captured"] is True
    runtime_before_revoke = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    imported_item = runtime_before_revoke["dream_research_queue"]["latest_item"]
    imported_governance = imported_item["governance"]
    assert imported_item["metadata"]["federated_packet_import_id"] == accepted_before_revoke["import_id"]
    assert imported_item["metadata"]["personal_data_training_opt_in"] is True
    assert imported_governance["proposal_status"] == "proposed"

    revoke = client.post(
        "/ops/wrapper/privacy-consent",
        json={
            "session_id": session_id,
            "decision": "revoke",
            "approved_by": "admin",
            "approval_ref": "operator-consent::privacy-consent-import-promotion-user-revocation",
        },
    )
    assert revoke.status_code == 200
    runtime_after_revoke = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    enforcement = runtime_after_revoke["privacy_consent_enforcement"]
    assert enforcement["status"] == "revocation-enforced"
    assert any(block["queue_id"] == imported_item["queue_id"] for block in enforcement["queue_blocks"])

    blocked_admin = client.post(
        imported_governance["admin_approval_ref"],
        json={"approved_by": "admin", "approval_ref": "operator-review::revoked-personal-data-import"},
    )
    assert blocked_admin.status_code == 400
    blocked_admin_detail = blocked_admin.json()["detail"]
    assert blocked_admin_detail["status"] == "blocked-privacy-consent-revoked-personal-data-artifact"
    assert blocked_admin_detail["blocked_action"] == "admin_approval"
    assert blocked_admin_detail["queue_id"] == imported_item["queue_id"]
    assert blocked_admin_detail["federated_packet_import_id"] == accepted_before_revoke["import_id"]
    assert blocked_admin_detail["privacy_consent_enforcement"]["latest_record_id"] == enforcement["latest_record_id"]
    assert blocked_admin_detail["raw_content_included"] is False
    assert blocked_admin_detail["active_production_mutation_allowed"] is False

    blocked_apply = client.post(
        imported_governance["apply_ref"],
        json={"test_refs": [], "test_evidence_refs": []},
    )
    assert blocked_apply.status_code == 400
    blocked_apply_detail = blocked_apply.json()["detail"]
    assert blocked_apply_detail["status"] == "blocked-privacy-consent-revoked-personal-data-artifact"
    assert blocked_apply_detail["blocked_action"] == "apply"

    queue_after_blocks = client.get("/ops/brain/self-improvement/queue").json()
    blocked_queue_item = next(
        item for item in queue_after_blocks["items"] if item["queue_id"] == imported_item["queue_id"]
    )
    assert blocked_queue_item["status"] == "rejected"
    proposals_after_blocks = client.get("/ops/brain/autonomous-updates").json()["proposals"]
    blocked_proposal = next(
        proposal
        for proposal in proposals_after_blocks
        if (proposal["metadata"].get("safe_payload") or {}).get("federated_packet_import_id")
        == accepted_before_revoke["import_id"]
    )
    assert blocked_proposal["operator_approved"] is False
    assert blocked_proposal["status"] == "proposed"

    blocked_reimport = client.post(
        "/ops/wrapper/federated-packets/import",
        json={"session_id": session_id, "peer_node_id": peer_node_id, "packet": opted_in_packet},
    ).json()
    assert blocked_reimport["status"] == "quarantined-shadow-blocked-by-consent-revocation"
    assert blocked_reimport["security_envelope_verified"] is True
    assert blocked_reimport["assimilation_shadow_captured"] is False
    assert blocked_reimport["global_growth_shadow_captured"] is False
    assert blocked_reimport["quarantine_state"] == "blocked-by-revocation"
    assert blocked_reimport["privacy_consent_enforcement"]["latest_record_id"] == enforcement["latest_record_id"]
    assert "dream_research_queue_id" not in blocked_reimport
    assert "evals_ao_artifact_gate" not in blocked_reimport

    revoked_chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": revoked_prompt}],
        },
    )
    assert revoked_chat.status_code == 200
    sanitized_packet = client.get("/ops/wrapper/federated-packets", params={"session_id": session_id}).json()[
        "latest_packet"
    ]
    assert sanitized_packet["consent_policy"]["personal_data_training_opt_in"] is False
    sanitized_import = client.post(
        "/ops/wrapper/federated-packets/import",
        json={"session_id": session_id, "peer_node_id": peer_node_id, "packet": sanitized_packet},
    ).json()
    assert sanitized_import["status"] == "quarantined-shadow-accepted"
    assert sanitized_import["assimilation_shadow_captured"] is True
    assert sanitized_import["global_growth_shadow_captured"] is True
    assert sanitized_import["consent_policy"]["personal_data_training_opt_in"] is False
    assert sanitized_import["dream_research_queue_id"]

    runtime_after_sanitized = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    imports_by_id = {
        record["import_id"]: record for record in runtime_after_sanitized["federated_packet_inbox"]["imports"]
    }
    assert imports_by_id[blocked_reimport["import_id"]]["status"] == blocked_reimport["status"]
    assert imports_by_id[sanitized_import["import_id"]]["status"] == "quarantined-shadow-accepted"

    serialized = json.dumps(
        {
            "blocked_admin": blocked_admin_detail,
            "blocked_apply": blocked_apply_detail,
            "blocked_reimport": blocked_reimport,
            "sanitized_import": sanitized_import,
            "runtime_after_sanitized": runtime_after_sanitized["privacy_consent_enforcement"],
        },
        sort_keys=True,
    )
    assert opt_in_prompt not in serialized
    assert revoked_prompt not in serialized
    assert "SECRET-CONSENT-IMPORT-OPTIN" not in serialized
    assert "SECRET-CONSENT-IMPORT-REVOKED" not in serialized
    assert session_id not in serialized
    assert peer_node_id not in serialized
    assert str(project_root) not in serialized


def test_release_wrapper_privacy_retention_rejects_revoked_queue_items_and_replays_passivation(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    session_id = "privacy-retention-passivation-user"
    peer_node_id = "peer-node-retention-passivation-secret"
    prompt = "Grow a coding expert with opted-in data but never expose SECRET-RETENTION-PASSIVATION."

    opt_in = client.post(
        "/ops/wrapper/privacy-consent",
        json={
            "session_id": session_id,
            "decision": "opt-in",
            "personal_data_training_opt_in": True,
            "personal_data_federation_allowed": True,
            "personal_data_dream_training_allowed": True,
            "approved_by": "admin",
            "approval_ref": "operator-consent::privacy-retention-passivation-user",
        },
    )
    assert opt_in.status_code == 200

    chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    assert chat.status_code == 200
    opted_in_packet = client.get("/ops/wrapper/federated-packets", params={"session_id": session_id}).json()[
        "latest_packet"
    ]
    accepted = client.post(
        "/ops/wrapper/federated-packets/import",
        json={"session_id": session_id, "peer_node_id": peer_node_id, "packet": opted_in_packet},
    ).json()
    assert accepted["status"] == "quarantined-shadow-accepted"

    runtime_before_revoke = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    personal_item = runtime_before_revoke["dream_research_queue"]["latest_item"]
    assert personal_item["metadata"]["personal_data_training_opt_in"] is True
    assert personal_item["status"] == "proposed"
    assert runtime_before_revoke["global_growth"]["global_captures"] >= 1
    assert runtime_before_revoke["global_growth"]["active_global_captures"] >= 1
    assert runtime_before_revoke["global_growth"]["passivated_global_captures"] == 0

    revoke = client.post(
        "/ops/wrapper/privacy-consent",
        json={
            "session_id": session_id,
            "decision": "revoke",
            "approved_by": "admin",
            "approval_ref": "operator-consent::privacy-retention-passivation-user-revocation",
        },
    )
    assert revoke.status_code == 200

    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]
    queue_after_revoke = client.get("/ops/brain/self-improvement/queue").json()

    retention = runtime["privacy_retention_enforcement"]
    assert retention["surface_id"] == "release-wrapper-privacy-retention-enforcement"
    assert retention["status"] == "revoked-personal-data-retention-enforced"
    assert retention["session_ref_digest"] == runtime["session_ref_digest"]
    assert retention["latest_record"]["revocation_consent_record_id"] == revoke.json()["latest_record_id"]
    assert retention["expired_queue_count"] >= 1
    assert retention["passivated_global_growth_count"] >= 1
    assert retention["active_personal_data_training_allowed"] is False
    assert retention["active_production_mutation_allowed"] is False
    assert retention["raw_content_included"] is False
    assert retention["contains_personal_data"] is False
    assert retention["artifact_ref"] == "release-wrapper-runtime/privacy-retention-enforcement.jsonl"
    assert any(ref["queue_id"] == personal_item["queue_id"] for ref in retention["expired_queue_refs"])

    retained_queue_item = next(
        item for item in queue_after_revoke["items"] if item["queue_id"] == personal_item["queue_id"]
    )
    assert retained_queue_item["status"] == "rejected"
    assert runtime["dream_research_queue"]["status_counts"]["rejected"] >= 1
    assert (
        runtime["dream_research_queue"]["privacy_retention_enforcement"]["latest_record_id"]
        == retention["latest_record_id"]
    )
    assert (
        runtime["global_growth"]["privacy_retention_enforcement"]["latest_record_id"]
        == retention["latest_record_id"]
    )
    assert runtime["global_growth"]["active_personal_data_training_allowed"] is False
    assert runtime["global_growth"]["active_global_captures"] < runtime["global_growth"]["global_captures"]
    assert runtime["global_growth"]["passivated_global_captures"] >= 1
    assert runtime["global_growth"]["global_growth_passivation_mode"] == "native-growth-state-passivation"
    assert runtime["global_growth"]["native_privacy_passivation"]["inactive_capture_count"] >= 1
    assert (
        retention["latest_record"]["native_global_growth_passivation"]["status"]
        == "passivated"
    )
    passivation_governance = retention["latest_record"]["authority_evidence_tool_governance"]
    assert passivation_governance["surface_id"] == "native-growth-passivation-governance-record"
    assert passivation_governance["status"] == "pass"
    assert passivation_governance["governed_surface_id"] == "multi-user-runtime-growth-passivation"
    assert (
        passivation_governance["native_passivation_record_id"]
        == retention["latest_record"]["native_global_growth_passivation"]["record_id"]
    )
    assert passivation_governance["authority_decision_id"]
    assert passivation_governance["evidence_record_id"]
    assert str(passivation_governance["evidence_content_hash"]).startswith("sha256:")
    assert passivation_governance["eval_federation_event_id"]
    assert passivation_governance["eval_federation_promotion_allowed"] is True
    assert passivation_governance["tool_action_plan_id"]
    assert passivation_governance["tool_action_execution_allowed"] is False
    assert passivation_governance["raw_content_included"] is False
    assert passivation_governance["contains_personal_data"] is False
    assert passivation_governance["active_production_mutation_allowed"] is False
    assert (
        retention["latest_record"]["native_global_growth_passivation"]["authority_evidence_tool_governance"][
            "authority_decision_id"
        ]
        == passivation_governance["authority_decision_id"]
    )
    assert retention["authority_evidence_tool_governance"]["latest_record_id"] == retention["latest_record_id"]
    assert retention["authority_evidence_tool_governance"]["status"] == "pass"
    assert (
        retention["authority_evidence_tool_governance"]["latest_governance"]["authority_decision_id"]
        == passivation_governance["authority_decision_id"]
    )
    assert (
        runtime["authority_evidence_tool_governance"]["latest_native_passivation_governance"][
            "authority_decision_id"
        ]
        == passivation_governance["authority_decision_id"]
    )
    assert status_card["privacy_retention_enforcement"]["latest_record_id"] == retention["latest_record_id"]
    assert (
        status_card["privacy_retention_enforcement"]["authority_evidence_tool_governance"]["status"]
        == "pass"
    )
    assert (
        control_panel["release_wrapper_privacy_retention_enforcement"]["latest_record_id"]
        == retention["latest_record_id"]
    )
    assert (
        control_panel["release_wrapper_privacy_retention_enforcement"]["authority_evidence_tool_governance"][
            "latest_governance"
        ]["tool_action_plan_id"]
        == passivation_governance["tool_action_plan_id"]
    )

    replay_client = TestClient(create_app(str(project_root)))
    replayed = replay_client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    replayed_queue = replay_client.get("/ops/brain/self-improvement/queue").json()
    assert replayed["privacy_retention_enforcement"]["replay"]["status"] == "replayed"
    assert replayed["privacy_retention_enforcement"]["latest_record_id"] == retention["latest_record_id"]
    assert (
        replayed["privacy_retention_enforcement"]["authority_evidence_tool_governance"]["latest_governance"][
            "evidence_record_id"
        ]
        == passivation_governance["evidence_record_id"]
    )
    assert replayed["global_growth"]["passivated_global_captures"] >= 1
    assert replayed["global_growth"]["native_privacy_passivation"]["inactive_capture_count"] >= 1
    assert (
        replayed["global_growth"]["native_privacy_passivation"]["latest_record"][
            "authority_evidence_tool_governance"
        ]["eval_federation_event_id"]
        == passivation_governance["eval_federation_event_id"]
    )
    replayed_queue_item = next(
        item for item in replayed_queue["items"] if item["queue_id"] == personal_item["queue_id"]
    )
    assert replayed_queue_item["status"] == "rejected"

    serialized = json.dumps(
        {
            "revoke": revoke.json(),
            "retention": retention,
            "runtime_queue": runtime["dream_research_queue"],
            "global_growth": runtime["global_growth"],
            "status_card": status_card["privacy_retention_enforcement"],
            "control_panel": control_panel["release_wrapper_privacy_retention_enforcement"],
            "replayed": replayed["privacy_retention_enforcement"],
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-RETENTION-PASSIVATION" not in serialized
    assert session_id not in serialized
    assert peer_node_id not in serialized
    assert str(project_root) not in serialized


def test_successful_coding_chat_runs_domain_expert_growth_admin_replay_from_live_use(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    session_id = "successful-coding-domain-growth-user"
    prompt = "Write a Python JSON parser helper and explain it without SECRET-DOMAIN-GROWTH."

    chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    assert chat.status_code == 200
    admin_replay = client.post(
        "/ops/wrapper/domain-expert-growth/admin-replay",
        json={
            "session_id": session_id,
            "domain_ao": "CodingAO",
            "approved_by": "release-wrapper-test-admin",
            "approval_ref": "test-admin::successful-coding-domain-growth",
            "requested_decision": "approved",
        },
    )
    assert admin_replay.status_code == 200
    assert admin_replay.json()["status"] == "recorded"

    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    lifecycle = client.get("/ops/wrapper/session-lifecycle", params={"session_id": session_id}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]

    latest_interaction = runtime["latest_interaction"]
    handoff = runtime["domain_teacher_eval_handoff"]
    matrix_rows = {
        row["entrypoint_id"]: row
        for row in runtime["whole_system_forward_pass_enforcement_matrix"]["entrypoints"]
    }
    domain_replay_row = matrix_rows["domain_expert_growth_admin_replay"]

    assert latest_interaction["selected_ao"] == "CodingAO"
    assert latest_interaction["domain_ao_routing"]["domain_ao"] == "CodingAO"
    assert handoff["handoff_count"] == 1
    assert handoff["latest_domain_ao"] == "CodingAO"
    assert handoff["latest_teacher_subject"] == "coder"
    assert handoff["passed"] is True
    assert handoff["admin_eval_replay_count"] == 1
    assert handoff["latest_admin_eval_replay_status"] == "passed-shadow"
    assert handoff["latest_admin_eval_replay_id"]
    assert handoff["latest_admin_promotion_decision_id"]
    assert handoff["latest_admin_promotion_decision"] in {"approved", "shadow"}
    assert handoff["latest_sandbox_takeover_evidence_status"] == "recorded"
    assert handoff["latest_teacher_evidence_bundle_id"]
    assert handoff["latest_takeover_scorecard_id"]
    assert handoff["latest_growth_archive_candidate_id"]
    assert handoff["raw_content_included"] is False
    assert handoff["active_production_mutation_allowed"] is False

    assert latest_interaction["domain_teacher_eval_handoff"]["admin_replay_status"] == "passed-shadow"
    assert domain_replay_row["status"] == "covered"
    assert domain_replay_row["honest_status_label"] == "covered"
    assert any(
        ref == f"latest_admin_eval_replay_id::{handoff['latest_admin_eval_replay_id']}"
        for ref in domain_replay_row["evidence_refs"]
    )
    assert status_card["operator_action_lane"]["latest_action_statuses"][
        "domain_expert_growth_admin_replay"
    ] == "passed-shadow"
    assert lifecycle["domain_teacher_eval_handoff"]["latest_admin_eval_replay_id"] == (
        handoff["latest_admin_eval_replay_id"]
    )
    assert control_panel["release_wrapper_runtime"]["domain_teacher_eval_handoff"][
        "latest_admin_eval_replay_id"
    ] == handoff["latest_admin_eval_replay_id"]

    replay_client = TestClient(create_app(str(project_root)))
    replayed_runtime = replay_client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    assert replayed_runtime["domain_teacher_eval_handoff"]["latest_admin_eval_replay_id"] == (
        handoff["latest_admin_eval_replay_id"]
    )

    serialized = json.dumps(
        {
            "runtime": runtime,
            "status_card": status_card,
            "lifecycle": lifecycle,
            "control_panel": control_panel,
        },
        sort_keys=True,
    )
    assert session_id not in serialized
    assert prompt not in serialized
    assert "SECRET-DOMAIN-GROWTH" not in serialized
    assert str(project_root) not in serialized


def test_successful_chat_auto_imports_federated_packet_and_runs_readiness_evidence_from_live_use(tmp_path: Path):
    project_root = make_project(tmp_path)
    sandbox_probe = project_root / "tests" / "release_wrapper_auto_live_use_probe_test.py"
    sandbox_probe.parent.mkdir(parents=True, exist_ok=True)
    sandbox_probe.write_text("def test_release_wrapper_auto_live_use_probe():\n    assert True\n", encoding="utf-8")
    client = TestClient(create_app(str(project_root)))
    session_id = "successful-auto-federation-readiness-user"
    prompt = "Write a Python JSON helper while keeping SECRET-AUTO-FED-READINESS private."

    chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
        },
    )

    assert chat.status_code == 200
    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    readiness = client.get("/ops/wrapper/release-readiness", params={"session_id": session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    lifecycle = client.get("/ops/wrapper/session-lifecycle", params={"session_id": session_id}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    control_panel_runtime = visualizer["overlay_state"]["control_panel"]["release_wrapper_runtime"]

    inbox = runtime["federated_packet_inbox"]
    imported = inbox["latest_import"]
    import_receipt = imported["operation_receipt"]
    import_enforcement = imported["whole_system_enforcement_receipt"]
    runner = status_card["release_readiness_evidence_runner"]
    matrix_rows = {
        row["entrypoint_id"]: row
        for row in runtime["whole_system_forward_pass_enforcement_matrix"]["entrypoints"]
    }
    control_panel_rows = {
        row["entrypoint_id"]: row
        for row in control_panel_runtime["whole_system_forward_pass_enforcement_matrix"]["entrypoints"]
    }

    assert inbox["import_count"] == 1
    assert imported["status"] == "quarantined-shadow-accepted"
    assert imported["source_packet_ref"] == f"federated-packet::{runtime['latest_interaction']['federated_packet_id']}"
    assert imported["security_envelope_verified"] is True
    assert imported["assimilation_shadow_captured"] is True
    assert imported["global_growth_shadow_captured"] is True
    assert imported["raw_content_included"] is False
    assert imported["contains_personal_data"] is False
    assert imported["active_production_mutation_allowed"] is False
    assert runtime["latest_interaction"]["federated_packet_import_id"] == imported["import_id"]
    assert runtime["latest_interaction"]["federated_packet_import_status"] == "quarantined-shadow-accepted"
    runtime_growth_receipt = runtime["global_growth"]["latest_runtime_receipt"]
    growth_governance = runtime_growth_receipt["authority_evidence_tool_governance"]
    packet_governance = runtime["latest_federated_packet"]["authority_evidence_tool_governance"]
    assert growth_governance["surface_id"] == "native-runtime-growth-capture-governance-record"
    assert growth_governance["status"] == "pass"
    assert "multi-user-runtime-growth-receipt" in growth_governance["governed_surface_ids"]
    assert "multi-user-runtime-growth-federated-packet" in growth_governance["governed_surface_ids"]
    assert "hive-federated-learning-packet" in growth_governance["governed_surface_ids"]
    assert growth_governance["runtime_growth_receipt_id"] == runtime_growth_receipt["receipt_id"]
    assert growth_governance["federated_packet_id"] == runtime["latest_federated_packet"]["packet_id"]
    assert growth_governance["authority_decision_id"]
    assert growth_governance["evidence_record_id"]
    assert str(growth_governance["evidence_content_hash"]).startswith("sha256:")
    assert growth_governance["eval_federation_event_id"]
    assert growth_governance["eval_federation_promotion_allowed"] is True
    assert growth_governance["tool_action_plan_id"]
    assert growth_governance["tool_action_execution_allowed"] is False
    assert growth_governance["raw_content_included"] is False
    assert growth_governance["contains_personal_data"] is False
    assert growth_governance["active_production_mutation_allowed"] is False
    assert packet_governance["authority_decision_id"] == growth_governance["authority_decision_id"]
    assert runtime["latest_interaction"]["native_runtime_growth_governance"]["authority_decision_id"] == (
        growth_governance["authority_decision_id"]
    )
    assert (
        control_panel_runtime["global_growth"]["latest_runtime_receipt"]["authority_evidence_tool_governance"][
            "evidence_record_id"
        ]
        == growth_governance["evidence_record_id"]
    )

    assert import_receipt["operation_type"] == "federated_packet_import"
    assert import_receipt["status"] == "covered"
    assert import_enforcement["status"] == "covered"
    assert import_enforcement["coverage_status"] == "covered"
    assert import_enforcement["operation_receipt_id"] == import_receipt["receipt_id"]
    assert import_enforcement["active_production_mutated"] is False
    assert import_enforcement["governed_update_path"]["status"] == (
        "completed-admin-approved-sandbox-applied-rolled-back"
    )
    assert import_enforcement["governed_update_path"]["readiness_run_id"]

    assert runner["run_count"] >= 1
    assert runner["latest_autonomous_update_lifecycle_status"] == "completed"
    assert runner["latest_autonomous_update_lifecycle_run_id"] == (
        import_enforcement["governed_update_path"]["readiness_run_id"]
    )
    assert matrix_rows["federated_packet_import"]["status"] == "covered"
    assert matrix_rows["federated_packet_import"]["operation_receipt"]["receipt_id"] == import_receipt["receipt_id"]
    assert (
        matrix_rows["federated_packet_import"]["whole_system_enforcement_receipt"]["receipt_id"]
        == import_enforcement["receipt_id"]
    )
    assert matrix_rows["release_readiness_evidence_runner"]["status"] == "covered"
    assert any(
        ref == f"run_id::{import_enforcement['governed_update_path']['readiness_run_id']}"
        for ref in matrix_rows["release_readiness_evidence_runner"]["evidence_refs"]
    )
    assert (
        control_panel_rows["federated_packet_import"]["operation_receipt"]["receipt_id"]
        == import_receipt["receipt_id"]
    )
    assert control_panel_rows["release_readiness_evidence_runner"]["status"] == "covered"
    assert status_card["release_readiness_evidence_runner"]["latest_autonomous_update_lifecycle_status"] == "completed"
    assert lifecycle["release_readiness_evidence_runner"]["latest_autonomous_update_lifecycle_status"] == "completed"

    readiness_checks = {check["check_id"]: check for check in readiness["readiness_checks"]}
    assert readiness_checks["federated-packet-inbox"]["status"] == "pass"
    assert readiness_checks["peer-shadow-proposal"]["status"] == "pass"
    assert readiness["evidence"]["peer_shadow_proposal"]["federated_packet_import_id"] == imported["import_id"]

    replay_client = TestClient(create_app(str(project_root)))
    replay_runtime = replay_client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    replay_rows = {
        row["entrypoint_id"]: row
        for row in replay_runtime["whole_system_forward_pass_enforcement_matrix"]["entrypoints"]
    }
    assert replay_runtime["federated_packet_inbox"]["latest_import"]["import_id"] == imported["import_id"]
    assert (
        replay_runtime["global_growth"]["latest_runtime_receipt"]["authority_evidence_tool_governance"][
            "eval_federation_event_id"
        ]
        == growth_governance["eval_federation_event_id"]
    )
    assert (
        replay_runtime["latest_federated_packet"]["authority_evidence_tool_governance"]["tool_action_plan_id"]
        == growth_governance["tool_action_plan_id"]
    )
    assert replay_rows["federated_packet_import"]["status"] == "covered"
    assert replay_rows["release_readiness_evidence_runner"]["status"] == "covered"

    serialized = json.dumps(
        {
            "runtime": runtime,
            "readiness": readiness,
            "status_card": status_card,
            "lifecycle": lifecycle,
            "control_panel_runtime": control_panel_runtime,
            "replay_runtime": replay_runtime,
        },
        sort_keys=True,
    )
    assert session_id not in serialized
    assert prompt not in serialized
    assert "SECRET-AUTO-FED-READINESS" not in serialized
    assert str(project_root) not in serialized


def test_successful_chat_auto_runs_release_supervisor_and_production_spine_lifecycle_from_live_use(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    session_id = "successful-auto-release-supervisor-user"
    prompt = "Write a Python release lifecycle helper without leaking SECRET-AUTO-RELEASE-SUPERVISOR."

    chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
        },
    )

    assert chat.status_code == 200
    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    readiness = client.get("/ops/wrapper/release-readiness", params={"session_id": session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    lifecycle = client.get("/ops/wrapper/session-lifecycle", params={"session_id": session_id}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    control_panel_runtime = visualizer["overlay_state"]["control_panel"]["release_wrapper_runtime"]

    production_lifecycle = runtime["production_spine_release_lifecycle"]
    production_run = production_lifecycle["latest_run"]
    production_rollback = production_lifecycle["latest_rollback"]
    boot = runtime["boot_supervisor"]
    initial = runtime["initial_release_supervisor"]
    matrix = runtime["whole_system_forward_pass_enforcement_matrix"]
    release_run_history = runtime["release_run_history"]
    canon_receipts = runtime["canon_contract_receipts"]
    latest_canon_receipt = canon_receipts["latest_receipt"]
    rows = {row["entrypoint_id"]: row for row in matrix["entrypoints"]}

    assert production_run["status"] == "approved-shadow-release-lifecycle"
    assert production_run["admin_approval"]["status"] == "approved"
    assert production_run["authority_evidence_tool_governance"]["status"] == "pass"
    assert production_run["step_counts"]["blocked"] == 0
    assert production_run["release_mutation_allowed"] is False
    assert production_run["active_production_mutation_allowed"] is False
    assert production_run["raw_content_included"] is False
    assert production_rollback["status"] == "rolled-back"
    assert production_rollback["rollback_restored"] is True
    assert production_rollback["active_production_mutated"] is False
    assert production_rollback["raw_content_included"] is False

    assert boot["latest_status"] == "boot-smoke-passed"
    assert boot["runtime_state"] == "live-evidence"
    assert boot["failed_count"] == 0
    assert boot["raw_content_included"] is False
    assert boot["evidence"]["release_product_path"]["entrypoint_runtime_state"] == "live-bound"
    assert boot["evidence"]["release_product_path"]["federated_import_accepted_count"] >= 1
    assert boot["evidence"]["release_product_path"]["admin_action_statuses"]["rollback"] == "rolled-back"

    assert initial["latest_status"] == "initial-release-go"
    assert initial["runtime_state"] in {"replayed-evidence", "live-evidence"}
    assert initial["release_readiness"]["go_no_go"] == "go"
    assert initial["action_statuses"]["production_spine_release_lifecycle"] == "approved-shadow-release-lifecycle"
    assert initial["action_statuses"]["production_spine_release_lifecycle_rollback"] == "rolled-back"
    assert initial["action_statuses"]["boot_supervisor"] == "boot-smoke-passed"
    assert initial["actions"]["native_hive_heartbeat_history"]["status"] == "fresh"
    assert initial["raw_content_included"] is False
    assert initial["active_production_mutation_allowed"] is False
    assert initial["active_production_mutated"] is False

    assert matrix["coverage_status"] == "partial"
    assert rows["domain_expert_growth_admin_replay"]["status"] == "missing"
    assert rows["domain_expert_growth_admin_replay"]["blockers"] == [
        "domain_expert_growth_admin_replay_not_run"
    ]
    assert rows["boot_supervisor"]["status"] == "covered"
    assert rows["initial_release_supervisor"]["status"] == "covered"
    assert rows["production_spine_release_lifecycle"]["status"] == "covered"
    assert rows["production_spine_lifecycle_rollback"]["status"] == "covered"
    assert release_run_history["runtime_state"] == "live-evidence"
    assert release_run_history["latest_status"] == "release-wrapper-live-product-path-partial"
    assert release_run_history["run_count"] == 1
    assert release_run_history["latest_run"]["run_kind"] == "release-wrapper-live-product-path"
    assert release_run_history["latest_run"]["active_production_mutated"] is False
    assert release_run_history["latest_run"]["raw_content_included"] is False
    assert canon_receipts["latest_status"] == "covered"
    assert latest_canon_receipt["gap_count"] == 0
    assert latest_canon_receipt["coverage_status"] == "covered"
    assert runtime["latest_interaction"]["canon_contract_coverage_status"] == "covered"
    assert readiness["evidence"]["production_spine_release_lifecycle"]["latest_run"]["run_id"] == production_run["run_id"]
    assert readiness["evidence"]["canon_contract_receipts"]["latest_status"] == "covered"
    assert readiness["evidence"]["release_run_history"]["run_count"] == 1
    assert status_card["production_spine_release_lifecycle"]["latest_run"]["run_id"] == production_run["run_id"]
    assert status_card["canon_contract_receipts"]["latest_status"] == "covered"
    assert status_card["release_run_history"]["run_count"] == 1
    assert lifecycle["production_spine_release_lifecycle"]["latest_run"]["run_id"] == production_run["run_id"]
    assert lifecycle["canon_contract_receipts"]["latest_status"] == "covered"
    assert lifecycle["release_run_history"]["run_count"] == 1
    assert control_panel_runtime["production_spine_release_lifecycle"]["latest_run"]["run_id"] == production_run["run_id"]
    assert control_panel_runtime["canon_contract_receipts"]["latest_status"] == "covered"
    assert control_panel_runtime["release_run_history"]["run_count"] == 1
    assert status_card["boot_supervisor"]["latest_status"] == "boot-smoke-passed"
    assert lifecycle["initial_release_supervisor"]["latest_status"] == "initial-release-go"
    assert control_panel_runtime["initial_release_supervisor"]["latest_status"] == "initial-release-go"

    replay_client = TestClient(create_app(str(project_root)))
    replay_runtime = replay_client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    replay_rows = {
        row["entrypoint_id"]: row
        for row in replay_runtime["whole_system_forward_pass_enforcement_matrix"]["entrypoints"]
    }
    assert replay_runtime["production_spine_release_lifecycle"]["latest_run"]["run_id"] == production_run["run_id"]
    assert replay_runtime["production_spine_release_lifecycle"]["latest_rollback"]["rollback_id"] == (
        production_rollback["rollback_id"]
    )
    assert replay_runtime["release_run_history"]["latest_run"]["run_id"] == release_run_history["latest_run"]["run_id"]
    assert replay_runtime["canon_contract_receipts"]["latest_status"] == "covered"
    assert replay_runtime["boot_supervisor"]["latest_status"] == "boot-smoke-passed"
    assert replay_runtime["initial_release_supervisor"]["latest_status"] == "initial-release-go"
    assert replay_rows["production_spine_release_lifecycle"]["status"] == "covered"
    assert replay_rows["production_spine_lifecycle_rollback"]["status"] == "covered"

    serialized = json.dumps(
        {
            "runtime": runtime,
            "readiness": readiness,
            "status_card": status_card,
            "lifecycle": lifecycle,
            "control_panel_runtime": control_panel_runtime,
            "replay_runtime": replay_runtime,
        },
        sort_keys=True,
    )
    assert session_id not in serialized
    assert prompt not in serialized
    assert "SECRET-AUTO-RELEASE-SUPERVISOR" not in serialized
    assert str(project_root) not in serialized


def test_wrapper_chat_pending_repair_envelope_executes_through_admin_governed_repair_run(
    tmp_path: Path,
):
    project = make_project(tmp_path)
    sandbox_probe = project / "tests" / "automatic_repair_probe_test.py"
    sandbox_probe.parent.mkdir(parents=True, exist_ok=True)
    sandbox_probe.write_text("def test_automatic_repair_probe():\n    assert True\n", encoding="utf-8")
    client = TestClient(create_app(str(project)))
    client.app.state.release_wrapper_runtime.hardware_scanner = _BoundedContextHardwareScanner()
    raw_session_id = "release-user-auto-repair"
    prompt = "Trigger automatic release repair from wrapper chat SECRET-AUTO-REPAIR."
    sandbox_command = "pytest tests/automatic_repair_probe_test.py -q"

    chat = client.post(
        "/chat",
        json={
            "session_id": raw_session_id,
            "message": prompt,
            "rag": False,
            "wrapper_mode": "standard-chat",
        },
    )

    assert chat.status_code == 200
    runtime_before = client.get("/ops/wrapper/release-runtime", params={"session_id": raw_session_id}).json()
    pending_plan = runtime_before["latest_interaction"]["release_health_automatic_repair_plan"]
    pending_history = runtime_before["release_health_heartbeat_supervisor"]["repair_history"]

    assert pending_plan["status"] == "planned-admin-approval-required-heartbeat-supervisor-repair"
    assert pending_plan["update_id"].startswith("update::release-wrapper-health-heartbeat-loop::")
    assert pending_plan["subsystem_repair_envelope_count"] >= 1
    assert pending_history["latest_status"] == "planned-admin-approval-required-heartbeat-supervisor-repair"
    assert pending_history["latest_run_id"] == pending_plan["run_id"]

    repair = client.post(
        "/ops/wrapper/release-health-heartbeat/supervisor/repair-run",
        json={
            "session_id": raw_session_id,
            "update_id": pending_plan["update_id"],
            "command": sandbox_command,
            "timeout_seconds": 30,
            "approved_by": "admin",
            "approval_ref": "operator-review::automatic-wrapper-interaction-repair",
        },
    )

    assert repair.status_code == 200
    repair_payload = repair.json()
    actions = repair_payload["actions"]
    readiness_run = repair_payload["readiness_evidence_run"]
    subsystem_envelopes = repair_payload["subsystem_repair_envelopes"]

    assert repair_payload["surface_id"] == "release-health-heartbeat-supervisor-repair-run"
    assert repair_payload["status"] == "completed"
    assert repair_payload["update_id"] == pending_plan["update_id"]
    assert repair_payload["source_loop_id"] == pending_plan["source_loop_id"]
    assert repair_payload["source_heartbeat_id"] == pending_plan["source_heartbeat_id"]
    assert repair_payload["subsystem_repair_envelope_count"] == pending_plan["subsystem_repair_envelope_count"]
    assert repair_payload["raw_content_included"] is False
    assert repair_payload["active_production_mutated"] is False
    assert actions["admin_approval"]["status"] == "admin-approved"
    assert actions["shadow_eval_replay"]["status"] == "passed-shadow"
    assert actions["sandbox_tests"]["status"] == "passed"
    assert actions["sandbox_tests"]["passed"] is True
    assert actions["sandbox_tests"]["sandbox"]["active_project_root_mutated"] is False
    assert actions["apply"]["status"] == "applied-shadow-safe-file"
    assert actions["apply"]["active_production_mutated"] is False
    assert actions["rollback"]["status"] == "rolled-back"
    assert actions["rollback"]["rollback_restored"] is True
    assert readiness_run["status"] == "completed-heartbeat-supervisor-repair"
    assert readiness_run["run_id"] != pending_plan["run_id"]
    assert readiness_run["subsystem_repair_envelopes"] == subsystem_envelopes
    assert subsystem_envelopes
    assert all(
        envelope["honest_status_label"] == "completed-shadow-safe-file-rollback-verified"
        for envelope in subsystem_envelopes
    )
    assert all(envelope["action_statuses"]["admin_approval"] == "admin-approved" for envelope in subsystem_envelopes)
    assert all(envelope["action_statuses"]["shadow_eval_replay"] == "passed-shadow" for envelope in subsystem_envelopes)
    assert all(envelope["action_statuses"]["sandbox_tests"] == "passed" for envelope in subsystem_envelopes)
    assert all(envelope["action_statuses"]["apply"] == "applied-shadow-safe-file" for envelope in subsystem_envelopes)
    assert all(envelope["action_statuses"]["rollback"] == "rolled-back" for envelope in subsystem_envelopes)
    assert all(envelope["raw_content_included"] is False for envelope in subsystem_envelopes)
    assert all(envelope["active_production_mutation_allowed"] is False for envelope in subsystem_envelopes)
    assert all(envelope["active_production_mutated"] is False for envelope in subsystem_envelopes)

    runtime_after = client.get("/ops/wrapper/release-runtime", params={"session_id": raw_session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": raw_session_id}).json()
    lifecycle = client.get("/ops/wrapper/session-lifecycle", params={"session_id": raw_session_id}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": raw_session_id}).json()
    repair_history = runtime_after["release_health_heartbeat_supervisor"]["repair_history"]
    control_panel = visualizer["overlay_state"]["control_panel"]

    assert repair_history["latest_status"] == "completed-heartbeat-supervisor-repair"
    assert repair_history["latest_run_id"] == readiness_run["run_id"]
    assert repair_history["latest_update_id"] == pending_plan["update_id"]
    assert repair_history["latest_loop_id"] == pending_plan["source_loop_id"]
    assert repair_history["latest_heartbeat_id"] == pending_plan["source_heartbeat_id"]
    assert repair_history["latest_subsystem_repair_envelope_count"] == len(subsystem_envelopes)
    assert repair_history["latest_subsystem_repair_envelopes"] == subsystem_envelopes
    assert status_card["operator_action_lane"]["latest_action_statuses"][
        "release_health_heartbeat_supervisor_repair"
    ] == "completed-heartbeat-supervisor-repair"
    assert status_card["release_health_heartbeat_supervisor"]["repair_history"]["latest_run_id"] == (
        readiness_run["run_id"]
    )
    assert lifecycle["release_health_heartbeat_supervisor"]["repair_history"]["latest_run_id"] == (
        readiness_run["run_id"]
    )
    assert control_panel["release_wrapper_release_health_heartbeat_supervisor"]["repair_history"][
        "latest_run_id"
    ] == readiness_run["run_id"]

    replay_client = TestClient(create_app(str(project)))
    replayed_runtime = replay_client.get("/ops/wrapper/release-runtime", params={"session_id": raw_session_id}).json()
    replayed_history = replayed_runtime["release_health_heartbeat_supervisor"]["repair_history"]
    assert replayed_history["latest_run_id"] == readiness_run["run_id"]
    assert replayed_history["latest_update_id"] == pending_plan["update_id"]
    assert replayed_history["latest_subsystem_repair_envelope_count"] == len(subsystem_envelopes)

    serialized = json.dumps(
        {
            "repair": repair_payload,
            "repair_history": repair_history,
            "status_card": status_card,
            "control_panel": control_panel,
        },
        sort_keys=True,
    )
    assert raw_session_id not in serialized
    assert prompt not in serialized
    assert "SECRET-AUTO-REPAIR" not in serialized
    assert str(project) not in serialized


def test_release_wrapper_forward_pass_coverage_records_degraded_subsystem_without_raw_content(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    prompt = "Coverage receipt degraded path marker SECRET-COVERAGE-DEGRADED."
    runtime = client.app.state.release_wrapper_runtime
    runtime.production_spine = None

    chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": "release-forward-coverage-degraded",
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
        },
    )

    assert chat.status_code == 200
    payload = client.get(
        "/ops/wrapper/release-runtime",
        params={"session_id": "release-forward-coverage-degraded"},
    ).json()
    coverage = payload["forward_pass_coverage"]
    receipt = coverage["latest_receipt"]
    stage_statuses = {stage["stage_id"]: stage["status"] for stage in receipt["stages"]}
    assert coverage["receipt_count"] == 1
    assert coverage["covered_count"] == 5
    assert coverage["degraded_count"] == 1
    assert coverage["latest_status"] == "degraded"
    assert receipt["status"] == "degraded"
    assert stage_statuses["continuous_assimilation"] == "covered"
    assert stage_statuses["global_growth"] == "covered"
    assert stage_statuses["federated_packet"] == "covered"
    assert stage_statuses["production_spine"] == "degraded"
    assert stage_statuses["developmental_cortex"] == "covered"
    assert stage_statuses["dream_research_queue"] == "covered"
    assert any("production_spine" in blocker for blocker in receipt["blockers"])
    assert payload["production_spine"]["packet_count"] == 0
    assert payload["latest_interaction"]["forward_pass_receipt_id"] == receipt["receipt_id"]
    assert payload["live_wrapper_telemetry"]["forward_pass_coverage"]["latest_status"] == "degraded"
    serialized = json.dumps(
        {
            "coverage": coverage,
            "receipt": receipt,
            "telemetry_coverage": payload["live_wrapper_telemetry"]["forward_pass_coverage"],
        }
    )
    assert prompt not in serialized
    assert "release-forward-coverage-degraded" not in serialized
    assert "SECRET-COVERAGE-DEGRADED" not in serialized


def test_release_wrapper_federated_packet_outbox_exports_sanitized_replayable_packets(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    prompt = "Federated outbox should not leak SECRET-FED-OUTBOX."
    session_id = "federated-outbox-user"

    chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    assert chat.status_code == 200

    outbox = client.get("/ops/wrapper/federated-packets", params={"session_id": session_id}).json()
    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()

    assert outbox["surface_id"] == "release-wrapper-federated-packet-outbox"
    assert outbox["status"] == "live-bound"
    assert outbox["packet_count"] == 1
    assert outbox["latest_packet"]["packet_id"] == runtime["latest_federated_packet"]["packet_id"]
    assert outbox["latest_packet"]["raw_content_included"] is False
    assert outbox["latest_packet"]["contains_personal_data"] is False
    assert outbox["latest_packet"]["security_envelope"]["signed_packet"]["raw_private_data_exported"] is False
    assert outbox["latest_interaction_ref"] == f"trace::{runtime['latest_interaction']['trace_id']}"
    assert outbox["endpoint_ref"] == "/ops/wrapper/federated-packets"
    assert outbox["active_production_mutation_allowed"] is False
    assert status_card["endpoint_refs"]["federated_packet_outbox"] == "/ops/wrapper/federated-packets"

    restarted = TestClient(create_app(str(project_root)))
    replayed = restarted.get("/ops/wrapper/federated-packets", params={"session_id": session_id}).json()
    assert replayed["replay"]["status"] == "replayed"
    assert replayed["packet_count"] == 1
    assert replayed["latest_packet"]["packet_id"] == outbox["latest_packet"]["packet_id"]

    serialized = json.dumps({"outbox": outbox, "replayed": replayed, "status_card": status_card})
    assert prompt not in serialized
    assert "SECRET-FED-OUTBOX" not in serialized
    assert session_id not in serialized

    control_panel_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    visualizer_js = (project_root / "ui" / "visualizer" / "app.js").read_text(encoding="utf-8")
    wrapper_html = (project_root / "ui" / "wrapper" / "index.html").read_text(encoding="utf-8")
    assert "federated packet outbox" in control_panel_js
    assert "Federated Packet Outbox" in wrapper_html
    assert "Wrapper packet outbox" in visualizer_js


def test_release_wrapper_imports_federated_packets_as_quarantined_shadow_learning(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    prompt = "Federated inbox should quarantine SECRET-FED-INBOX."
    session_id = "federated-inbox-user"
    peer_node_id = "peer-node-secret-fed-inbox"

    chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    assert chat.status_code == 200
    outbox = client.get("/ops/wrapper/federated-packets", params={"session_id": session_id}).json()
    packet = outbox["latest_packet"]

    imported_response = client.post(
        "/ops/wrapper/federated-packets/import",
        json={
            "session_id": session_id,
            "peer_node_id": peer_node_id,
            "packet": packet,
        },
    )
    assert imported_response.status_code == 200
    imported = imported_response.json()

    assert imported["surface_id"] == "release-wrapper-federated-packet-import"
    assert imported["status"] == "quarantined-shadow-accepted"
    assert imported["quarantine_state"] == "shadow-only"
    assert imported["source_packet_ref"] == f"federated-packet::{packet['packet_id']}"
    assert imported["security_envelope_verified"] is True
    assert imported["assimilation_shadow_captured"] is True
    assert imported["global_growth_shadow_captured"] is True
    assert imported["raw_content_included"] is False
    assert imported["contains_personal_data"] is False
    assert imported["active_production_mutation_allowed"] is False

    inbox = client.get("/ops/wrapper/federated-packets/imports", params={"session_id": session_id}).json()
    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    readiness = client.get("/ops/wrapper/release-readiness", params={"session_id": session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()

    assert inbox["surface_id"] == "release-wrapper-federated-packet-inbox"
    assert inbox["status"] == "shadow-quarantine-active"
    assert inbox["import_count"] >= 2
    assert inbox["latest_import"]["import_id"] == imported["import_id"]
    assert inbox["latest_import"]["source_packet_ref"] == imported["source_packet_ref"]
    assert inbox["active_production_mutation_allowed"] is False
    assert runtime["federated_packet_inbox"]["import_count"] >= 2
    assert runtime["federated_packet_inbox"]["latest_import"]["import_id"] == imported["import_id"]
    assert status_card["endpoint_refs"]["federated_packet_inbox"] == "/ops/wrapper/federated-packets/imports"
    assert status_card["endpoint_refs"]["federated_packet_import"] == "/ops/wrapper/federated-packets/import"

    readiness_checks = {check["check_id"]: check for check in readiness["readiness_checks"]}
    assert readiness_checks["federated-packet-inbox"]["status"] == "pass"
    expert_node = imported["expert_node"]
    source_model = imported["source_model"]
    provenance = runtime["continuous_assimilation"]["provenance"][expert_node]
    assert any(record["source_model"] == source_model for record in provenance)
    assert runtime["global_growth"]["global_captures"] >= 2

    restarted = TestClient(create_app(str(project_root)))
    replayed = restarted.get("/ops/wrapper/federated-packets/imports", params={"session_id": session_id}).json()
    assert replayed["replay"]["status"] == "replayed"
    assert replayed["import_count"] >= 2
    assert replayed["latest_import"]["import_id"] == imported["import_id"]

    serialized = json.dumps(
        {
            "imported": imported,
            "inbox": inbox,
            "runtime": runtime,
            "readiness": readiness,
            "status_card": status_card,
            "replayed": replayed,
        }
    )
    assert prompt not in serialized
    assert "SECRET-FED-INBOX" not in serialized
    assert session_id not in serialized
    assert peer_node_id not in serialized

    control_panel_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    visualizer_js = (project_root / "ui" / "visualizer" / "app.js").read_text(encoding="utf-8")
    wrapper_html = (project_root / "ui" / "wrapper" / "index.html").read_text(encoding="utf-8")
    assert "federated packet inbox" in control_panel_js
    assert "Federated Packet Inbox" in wrapper_html
    assert "Wrapper packet inbox" in visualizer_js


def test_release_wrapper_imported_federated_packet_feeds_dream_research_proposal_shadow_only(tmp_path: Path):
    project_root = make_project(tmp_path)
    sandbox_probe = project_root / "tests" / "federated_import_apply_probe_test.py"
    sandbox_probe.parent.mkdir(parents=True, exist_ok=True)
    sandbox_probe.write_text(
        "def test_federated_import_apply_probe():\n"
        "    assert 'federated-import'.replace('-', '_') == 'federated_import'\n",
        encoding="utf-8",
    )
    client = TestClient(create_app(str(project_root)))
    prompt = "Imported federation should propose research without leaking SECRET-FED-DREAM."
    session_id = "federated-dream-user"
    peer_node_id = "peer-node-secret-fed-dream"

    chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    assert chat.status_code == 200
    packet = client.get("/ops/wrapper/federated-packets", params={"session_id": session_id}).json()["latest_packet"]
    imported = client.post(
        "/ops/wrapper/federated-packets/import",
        json={"session_id": session_id, "peer_node_id": peer_node_id, "packet": packet},
    ).json()
    import_eval_gate = imported["evals_ao_artifact_gate"]

    queue = client.get("/ops/brain/self-improvement/queue").json()
    import_items = [
        item
        for item in queue["items"]
        if item["event"]["metadata"].get("federated_import_shadow") is True
        and item["event"]["metadata"].get("federated_packet_import_id") == imported["import_id"]
    ]
    assert len(import_items) == 1
    item = import_items[0]
    event = item["event"]
    assert item["status"] == "proposed"
    assert event["metadata"]["source"] == "release-wrapper-runtime"
    assert event["metadata"]["dream_research_queue"] is True
    assert event["metadata"]["raw_content_included"] is False
    assert event["metadata"]["source_packet_ref"] == imported["source_packet_ref"]
    assert event["metadata"]["federated_packet_import_id"] == imported["import_id"]
    assert event["metadata"]["source_model"] == imported["source_model"]
    assert event["metadata"]["expert_node"] == imported["expert_node"]
    assert event["safety"]["contains_private_data"] is False
    assert event["safety"]["contains_secrets"] is False
    assert "federated-import" in " ".join(event["actions_taken"])

    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    dream_queue = runtime["dream_research_queue"]
    assert dream_queue["latest_item"]["queue_id"] == item["queue_id"]
    assert dream_queue["latest_item"]["metadata"]["federated_packet_import_id"] == imported["import_id"]
    assert dream_queue["latest_item"]["governance"]["proposal_status"] == "proposed"
    proposal = next(
        candidate
        for candidate in runtime["autonomous_updates"]["proposals"]
        if (candidate["metadata"].get("safe_payload") or {}).get("federated_packet_import_id")
        == imported["import_id"]
    )
    assert proposal["requested_state"] == "proposal"
    assert proposal["metadata"]["active_production_mutation_allowed"] is False
    assert proposal["metadata"]["safe_payload"]["source_packet_ref"] == imported["source_packet_ref"]
    assert proposal["metadata"]["safe_payload"]["peer_shadow_import"] is True
    assert import_eval_gate["surface_id"] == "external-evals-ao-artifact-gate"
    assert import_eval_gate["status"] == "passed-shadow"
    assert import_eval_gate["artifact_set_complete"] is True
    assert import_eval_gate["gate_id"] in proposal["eval_refs"]
    assert import_eval_gate["eval_registry_ref"]["suite_id"] in proposal["eval_refs"]
    assert proposal["metadata"]["evals_ao_artifact_gate_ref"] == import_eval_gate["gate_id"]
    assert proposal["metadata"]["evals_ao_eval_suite_id"] == import_eval_gate["eval_registry_ref"]["suite_id"]
    governance = dream_queue["latest_item"]["governance"]

    approval = client.post(
        governance["admin_approval_ref"],
        json={"approved_by": "admin", "approval_ref": "operator-review::federated-import"},
    )
    assert approval.status_code == 200
    approval_payload = approval.json()
    assert approval_payload["status"] == "admin-approved"
    assert approval_payload["linked_eval_replay"]["status"] == "passed-shadow"
    assert approval_payload["linked_eval_replay"]["suite_id"] == import_eval_gate["eval_registry_ref"]["suite_id"]
    assert import_eval_gate["gate_id"] in approval_payload["linked_eval_replay"]["evidence_refs"]
    assert (
        approval_payload["linked_eval_replay"]["metadata"]["evals_ao_artifact_gate_ref"]
        == import_eval_gate["gate_id"]
    )
    assert approval_payload["linked_improvement_queue"]["queue_status"] == "validated"
    visualized_replay_gate = client.get(
        "/ops/brain/visualizer/state", params={"session_id": session_id}
    ).json()["overlay_state"]["control_panel"]["autonomous_update_scorecard"]["artifact_bound_replay_gate"]
    assert visualized_replay_gate["surface_id"] == "artifact-bound-autonomous-update-replay-gate"
    assert visualized_replay_gate["bound_replay_count"] >= 1
    assert visualized_replay_gate["missing_bound_replay_count"] >= 1
    assert visualized_replay_gate["latest_required_proposal"]["update_id"] == proposal["update_id"]
    assert visualized_replay_gate["latest_required_proposal"]["latest_replay_bound"] is True
    assert import_eval_gate["gate_id"] in visualized_replay_gate["latest_required_proposal"]["required_artifact_gate_refs"]

    sandbox = client.post(
        governance["sandbox_tests_ref"],
        json={"command": "pytest tests/federated_import_apply_probe_test.py -q", "timeout_seconds": 30},
    )
    assert sandbox.status_code == 200
    sandbox_payload = sandbox.json()
    assert sandbox_payload["status"] == "passed"
    assert sandbox_payload["sandbox"]["active_project_root_mutated"] is False

    applied = client.post(
        governance["apply_ref"],
        json={
            "test_refs": ["pytest tests/federated_import_apply_probe_test.py -q"],
            "test_evidence_refs": [sandbox_payload["evidence_ref"]],
        },
    )
    assert applied.status_code == 200
    applied_payload = applied.json()
    assert applied_payload["status"] == "applied-shadow-safe-file"
    assert applied_payload["active_production_mutated"] is False
    safe_record = json.loads(Path(applied_payload["safe_file_path"]).read_text(encoding="utf-8"))
    assert safe_record["safe_payload"]["federated_packet_import_id"] == imported["import_id"]
    assert safe_record["safe_payload"]["source_packet_ref"] == imported["source_packet_ref"]
    assert safe_record["safe_payload"]["peer_shadow_import"] is True

    rollback = client.post(governance["rollback_ref"], json={"reason": "federated-import-regression"})
    assert rollback.status_code == 200
    rollback_payload = rollback.json()
    assert rollback_payload["status"] == "rolled-back"
    assert rollback_payload["rollback_restored"] is True

    expected_action_receipts = {
        "admin_approval": approval_payload["release_wrapper_self_repair"]["operation_receipt"]["receipt_id"],
        "sandbox_tests": sandbox_payload["release_wrapper_self_repair"]["operation_receipt"]["receipt_id"],
        "apply": applied_payload["release_wrapper_self_repair"]["operation_receipt"]["receipt_id"],
        "rollback": rollback_payload["release_wrapper_self_repair"]["operation_receipt"]["receipt_id"],
    }
    expected_action_statuses = {
        "admin_approval": "admin-approved",
        "sandbox_tests": "passed",
        "apply": "applied-shadow-safe-file",
        "rollback": "rolled-back",
    }
    runtime_after_manual_governance = client.get(
        "/ops/wrapper/release-runtime", params={"session_id": session_id}
    ).json()
    manual_receipt = runtime_after_manual_governance["federated_packet_inbox"]["latest_import"][
        "whole_system_enforcement_receipt"
    ]
    manual_governed_path = manual_receipt["governed_update_path"]
    assert manual_governed_path["status"] == "completed-admin-approved-sandbox-applied-rolled-back"
    assert manual_governed_path["manual_governance_recorded"] is True
    assert manual_governed_path["readiness_run_id"] is None
    assert manual_governed_path["action_statuses"] == expected_action_statuses
    assert manual_governed_path["action_operation_receipt_ids"] == expected_action_receipts
    assert manual_governed_path["active_production_mutation_allowed"] is False
    assert manual_governed_path["active_production_mutated"] is False
    assert manual_receipt["raw_content_included"] is False
    assert manual_receipt["active_production_mutated"] is False

    replay_client = TestClient(create_app(str(project_root)))
    replay_runtime = replay_client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    replay_receipt = replay_runtime["federated_packet_inbox"]["latest_import"]["whole_system_enforcement_receipt"]
    replay_governed_path = replay_receipt["governed_update_path"]
    assert replay_governed_path["status"] == "completed-admin-approved-sandbox-applied-rolled-back"
    assert replay_governed_path["manual_governance_recorded"] is True
    assert replay_governed_path["readiness_run_id"] is None
    assert replay_governed_path["action_statuses"] == expected_action_statuses
    assert replay_governed_path["action_operation_receipt_ids"] == expected_action_receipts
    assert replay_governed_path["active_production_mutation_allowed"] is False
    assert replay_governed_path["active_production_mutated"] is False
    assert replay_receipt["raw_content_included"] is False
    assert replay_receipt["active_production_mutated"] is False

    serialized = json.dumps(
        {
            "queue": queue,
            "runtime": runtime,
            "runtime_after_manual_governance": runtime_after_manual_governance,
            "replay_runtime": replay_runtime,
            "proposal": proposal,
            "imported": imported,
            "approval": approval_payload,
            "sandbox": sandbox_payload,
            "safe_record": safe_record,
            "rollback": rollback_payload,
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-FED-DREAM" not in serialized
    assert session_id not in serialized
    assert peer_node_id not in serialized


def test_release_wrapper_rejects_unsafe_federated_packet_without_learning_or_proposal(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    prompt = "Unsafe federation packet should not learn SECRET-FED-REJECT."
    session_id = "federated-reject-user"
    peer_node_id = "peer-node-secret-fed-reject"

    chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    assert chat.status_code == 200
    packet = client.get("/ops/wrapper/federated-packets", params={"session_id": session_id}).json()["latest_packet"]
    unsafe_packet = json.loads(json.dumps(packet))
    unsafe_packet["raw_content_included"] = True
    unsafe_packet["contains_personal_data"] = True
    unsafe_packet["security_envelope"]["signed_packet"]["raw_private_data_exported"] = True

    rejected = client.post(
        "/ops/wrapper/federated-packets/import",
        json={"session_id": session_id, "peer_node_id": peer_node_id, "packet": unsafe_packet},
    ).json()

    assert rejected["status"] == "quarantined-rejected"
    assert rejected["security_envelope_verified"] is False
    assert rejected["quarantine_state"] == "blocked"
    assert rejected["assimilation_shadow_captured"] is False
    assert rejected["global_growth_shadow_captured"] is False
    assert rejected["active_production_mutation_allowed"] is False
    assert rejected["raw_content_included"] is False
    assert rejected["contains_personal_data"] is False

    inbox = client.get("/ops/wrapper/federated-packets/imports", params={"session_id": session_id}).json()
    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    queue = client.get("/ops/brain/self-improvement/queue").json()

    assert inbox["import_count"] >= 2
    assert inbox["accepted_import_count"] >= 1
    assert inbox["rejected_import_count"] == 1
    assert inbox["latest_import"]["import_id"] == rejected["import_id"]
    assert runtime["federated_packet_inbox"]["rejected_import_count"] == 1
    assert rejected["source_model"] not in json.dumps(runtime["continuous_assimilation"]["provenance"])
    assert not [
        item
        for item in queue["items"]
        if item["event"]["metadata"].get("federated_packet_import_id") == rejected["import_id"]
    ]
    assert not [
        proposal
        for proposal in runtime["autonomous_updates"]["proposals"]
        if (proposal["metadata"].get("safe_payload") or {}).get("federated_packet_import_id")
        == rejected["import_id"]
    ]

    serialized = json.dumps({"rejected": rejected, "inbox": inbox, "runtime": runtime, "queue": queue})
    assert prompt not in serialized
    assert "SECRET-FED-REJECT" not in serialized
    assert session_id not in serialized
    assert peer_node_id not in serialized


def test_wrapper_chat_records_sanitized_ao_execution_receipt(tmp_path: Path):
    client = TestClient(create_app(str(make_project(tmp_path))))

    chat = client.post(
        "/chat",
        json={
            "session_id": "ao-runtime-user",
            "message": "Run an eval smoke gate for the wrapper before promotion.",
            "rag": False,
        },
    )

    assert chat.status_code == 200
    payload = chat.json()
    assert payload["ao"] == "EvalsAO"
    aos = client.get("/ops/brain/aos").json()
    assert aos["execution_count"] >= 1
    receipt = next(
        item
        for item in aos["execution_receipts"]
        if item.get("trace_ref") == f"trace::{payload['trace_id']}"
    )
    assert receipt["surface_id"] == "ao-execution-receipt"
    assert receipt["ao_name"] == "EvalsAO"
    assert receipt["trace_ref"] == f"trace::{payload['trace_id']}"
    assert receipt["input_contract"] == "nexusbrain-command-envelope-and-trace-only"
    assert receipt["direct_local_state_reads"] == []
    assert receipt["raw_content_included"] is False
    assert receipt["plan"]["risk_tier"] == "medium"
    eval_ao = next(ao for ao in aos["active_aos"] if ao["name"] == "EvalsAO")
    assert eval_ao["execution_count"] >= 1
    assert "Run an eval smoke gate" not in json.dumps(aos)
    assert "ao-runtime-user" not in json.dumps(aos)


def test_wrapper_chat_records_canonical_ao_coverage_for_live_forward_pass(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    session_id = "ao-canonical-live-user"
    prompt = "Run an eval smoke gate through the whole wrapper heart without SECRET-AO-CANON."

    chat = client.post(
        "/chat",
        json={
            "session_id": session_id,
            "message": prompt,
            "rag": False,
        },
    )

    assert chat.status_code == 200
    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    readiness = client.get("/ops/wrapper/release-readiness", params={"session_id": session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    aos = client.get("/ops/brain/aos").json()

    coverage = runtime["canonical_ao_coverage"]
    latest_interaction = runtime["latest_interaction"]
    required_aos = set(coverage["required_aos"])

    assert coverage["runtime_state"] == "live-bound"
    assert coverage["passed"] is True
    assert set(coverage["covered_aos"]) >= required_aos
    assert coverage["missing_aos"] == []
    assert coverage["receipt_count"] >= len(required_aos)
    assert coverage["raw_content_included"] is False
    assert coverage["active_production_mutation_allowed"] is False
    assert latest_interaction["canonical_ao_coverage"]["coverage_id"] == coverage["latest_coverage_id"]
    assert latest_interaction["selected_ao"] == "EvalsAO"
    assert latest_interaction["ao_execution_receipt_id"]

    selected_receipt = next(
        receipt
        for receipt in aos["execution_receipts"]
        if receipt["execution_id"] == latest_interaction["ao_execution_receipt_id"]
    )
    assert selected_receipt["ao_name"] == "EvalsAO"
    assert selected_receipt["trace_ref"] == f"trace::{latest_interaction['trace_id']}"
    assert selected_receipt["raw_content_included"] is False
    assert runtime["ao_execution_receipts"]["execution_count"] >= 1 + len(required_aos)
    assert readiness["evidence"]["canonical_ao_coverage"]["passed"] is True
    assert status_card["runtime"]["canonical_ao_coverage"]["passed"] is True

    restarted = TestClient(create_app(str(project_root)))
    replayed = restarted.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    assert replayed["ao_execution_receipts"]["replay"]["status"] == "replayed"
    assert replayed["canonical_ao_coverage"]["passed"] is True
    assert replayed["latest_interaction"]["ao_execution_receipt_id"] == latest_interaction["ao_execution_receipt_id"]

    serialized = json.dumps(
        {
            "runtime": runtime,
            "readiness": readiness["evidence"]["canonical_ao_coverage"],
            "status_card": status_card["runtime"]["canonical_ao_coverage"],
            "selected_receipt": {
                key: value
                for key, value in selected_receipt.items()
                if key != "artifact_path"
            },
            "replayed": replayed["canonical_ao_coverage"],
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-AO-CANON" not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized


def test_release_wrapper_chat_queues_dream_research_improvement_and_governed_proposal(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    chat = client.post(
        "/v1/chat",
        json={
            "session_id": "dream-queue-user",
            "model": "nexusnet-offline",
            "messages": [
                {
                    "role": "user",
                    "content": "Research a safer wrapper routing policy for Python debugging requests.",
                }
            ],
        },
    )

    assert chat.status_code == 200
    queue = client.get("/ops/brain/self-improvement/queue").json()
    assert queue["item_count"] >= 1
    item = next(
        candidate
        for candidate in queue["items"]
        if candidate["event"]["metadata"].get("source") == "release-wrapper-runtime"
        and candidate["event"]["metadata"].get("production_spine_packet_signature")
        and candidate["event"]["metadata"].get("federated_import_shadow") is not True
    )
    import_shadow_item = next(
        candidate
        for candidate in queue["items"]
        if candidate["event"]["metadata"].get("source") == "release-wrapper-runtime"
        and candidate["event"]["metadata"].get("federated_import_shadow") is True
        and candidate["event"]["metadata"].get("federated_packet_import_id")
    )
    event = item["event"]
    decision = item["decision"]
    assert item["status"] == "proposed"
    assert event["metadata"]["source"] == "release-wrapper-runtime"
    assert event["metadata"]["dream_research_queue"] is True
    assert event["metadata"]["raw_content_included"] is False
    assert event["metadata"]["federated_packet_id"]
    assert event["metadata"]["production_spine_packet_signature"].startswith("sha256:")
    assert event["safety"]["contains_private_data"] is False
    assert event["safety"]["contains_secrets"] is False
    assert {source["source_type"] for source in event["context_sources"]} >= {"runtime_trace", "artifact"}
    assert {"prompt_policy_candidate", "routing_policy_candidate"} <= set(decision["safe_optimization_modes"])
    assert {"create_eval_case", "human_review_required"} <= set(decision["labels"])
    assert "Research a safer wrapper" not in json.dumps(queue)
    event_growth_governance = event["metadata"]["authority_evidence_tool_governance"]
    assert event_growth_governance["status"] == "pass"
    assert event_growth_governance["runtime_growth_receipt_id"] == event["metadata"]["runtime_growth_receipt_id"]
    assert event_growth_governance["authority_decision_id"]
    assert event_growth_governance["evidence_record_id"]
    assert event_growth_governance["eval_federation_event_id"]
    assert event_growth_governance["tool_action_plan_id"]
    assert event_growth_governance["raw_content_included"] is False
    import_event = import_shadow_item["event"]
    import_growth_governance = import_event["metadata"]["authority_evidence_tool_governance"]
    assert import_event["metadata"]["raw_content_included"] is False
    assert import_event["metadata"]["federated_import_shadow"] is True
    assert import_growth_governance["status"] == "pass"
    assert import_growth_governance["runtime_growth_receipt_id"] == event_growth_governance["runtime_growth_receipt_id"]
    assert import_growth_governance["authority_decision_id"] == event_growth_governance["authority_decision_id"]
    assert import_growth_governance["raw_content_included"] is False

    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": "dream-queue-user"}).json()
    dream_queue = runtime["dream_research_queue"]
    assert dream_queue["status"] == "live-bound"
    assert dream_queue["item_count"] >= 1
    dream_growth_governance = dream_queue["latest_item"]["governance"]["authority_evidence_tool_governance"]
    assert dream_growth_governance["status"] == "pass"
    assert dream_growth_governance["runtime_growth_receipt_id"] == (
        dream_queue["latest_item"]["metadata"]["runtime_growth_receipt_id"]
    )
    assert dream_growth_governance["authority_decision_id"]
    assert dream_growth_governance["eval_federation_event_id"]
    assert dream_growth_governance["tool_action_plan_id"]
    assert dream_growth_governance["raw_content_included"] is False
    latest_admin_statuses = dream_queue["latest_item"]["governance"]["admin_action_statuses"]
    assert latest_admin_statuses["admin_approval"] in {"pending-admin-approval", "admin-approved"}
    assert latest_admin_statuses["shadow_eval_replay"] in {"not-run", "passed-shadow"}
    assert latest_admin_statuses["sandbox_tests"] in {"not-run", "passed"}
    assert latest_admin_statuses["apply"] in {"not-applied", "applied-shadow-safe-file"}
    assert latest_admin_statuses["rollback"] in {"not-rolled-back", "rolled-back"}
    proposals = runtime["autonomous_updates"]["proposals"]
    proposal = next(
        candidate
        for candidate in proposals
        if candidate["metadata"].get("source") == "release-wrapper-dream-research-queue"
        and candidate["metadata"].get("improvement_queue_id") == item["queue_id"]
    )
    import_proposal = next(
        candidate
        for candidate in proposals
        if candidate["metadata"].get("source") == "release-wrapper-dream-research-queue"
        and candidate["metadata"].get("improvement_queue_id") == import_shadow_item["queue_id"]
    )
    assert proposal["requested_state"] == "proposal"
    assert proposal["metadata"]["improvement_queue_id"] == item["queue_id"]
    assert proposal["metadata"]["active_production_mutation_allowed"] is False
    assert proposal["metadata"]["safe_file_scope"] == ["artifacts/autonomous-updates/safe-files"]
    assert proposal["metadata"]["authority_evidence_tool_governance"]["evidence_record_id"] == (
        event_growth_governance["evidence_record_id"]
    )
    assert proposal["metadata"]["safe_payload"]["authority_evidence_tool_governance"]["authority_decision_id"] == (
        event_growth_governance["authority_decision_id"]
    )
    assert import_proposal["metadata"]["safe_payload"]["federated_packet_import_id"] == (
        import_event["metadata"]["federated_packet_import_id"]
    )
    assert (
        import_proposal["metadata"]["safe_payload"]["authority_evidence_tool_governance"]["runtime_growth_receipt_id"]
        == event_growth_governance["runtime_growth_receipt_id"]
    )

    canon = client.get("/ops/brain/canon/self-improvement").json()
    assert canon["queue_summary"]["item_count"] >= 2
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "dream-queue-user"}).json()
    scorecard = visualizer["overlay_state"]["control_panel"]["self_improvement_scorecard"]
    assert scorecard["queue_summary"]["item_count"] >= 2


def test_release_wrapper_queue_item_runs_persisted_dream_research_episode_and_eval_case(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    chat = client.post(
        "/v1/chat",
        json={
            "session_id": "dream-episode-user",
            "model": "nexusnet-offline",
            "messages": [
                {
                    "role": "user",
                    "content": "Research a safer wrapper routing policy with dream evidence.",
                }
            ],
        },
    )

    assert chat.status_code == 200
    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": "dream-episode-user"}).json()
    dream_queue = runtime["dream_research_queue"]
    latest_item = dream_queue["latest_actionable_item"]

    assert dream_queue["status"] == "live-bound"
    assert dream_queue["episode_count"] >= 2
    assert latest_item["research_status"] == "researched"
    episode = dream_queue["latest_actionable_episode"]
    assert episode["queue_id"] == latest_item["queue_id"]
    assert episode["event_id"] == latest_item["event_id"]
    assert episode["status"] == "researched"
    assert episode["raw_content_included"] is False
    assert episode["dream_episode"]["surface_id"] == "rnd-v2-dream-episode"
    assert episode["dream_episode"]["observe_only"] is True
    assert episode["dream_episode"]["production_mutation_allowed"] is False
    assert episode["dream_episode"]["promotable_candidate"] is False
    assert episode["eval_case"]["eval_case_id"].startswith("eval-case::release-wrapper-dream-research::")
    assert episode["eval_case"]["queue_id"] == latest_item["queue_id"]
    assert episode["eval_case"]["raw_content_included"] is False
    assert episode["proposal_refinement"]["source"] == "release-wrapper-dream-research-episode"
    assert episode["proposal_refinement"]["proposal_update_id"] == latest_item["governance"]["proposal_update_id"]
    assert episode["proposal_refinement"]["active_production_mutation_allowed"] is False
    assert latest_item["governance"]["research_episode_id"] == episode["episode_id"]
    assert latest_item["governance"]["eval_case_ref"] == episode["eval_case"]["eval_case_id"]
    assert "Research a safer wrapper routing policy with dream evidence" not in json.dumps(runtime)

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "dream-episode-user"}).json()
    visualized = visualizer["overlay_state"]["control_panel"]["release_wrapper_runtime"]["dream_research_queue"]
    assert visualized["episode_count"] >= 2
    assert visualized["latest_actionable_episode"]["episode_id"] == episode["episode_id"]


def test_release_wrapper_dream_research_eval_case_registers_eval_suite_and_replay_template(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    chat = client.post(
        "/v1/chat",
        json={
            "session_id": "dream-eval-registry-user",
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": "Create wrapper eval evidence for a safe update."}],
        },
    )

    assert chat.status_code == 200
    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": "dream-eval-registry-user"}).json()
    episode = runtime["dream_research_queue"]["latest_episode"]
    eval_case = episode["eval_case"]
    eval_registry_ref = episode["eval_registry"]
    proposal = next(
        candidate
        for candidate in runtime["autonomous_updates"]["proposals"]
        if candidate["metadata"].get("improvement_queue_id") == episode["queue_id"]
    )

    registry = client.get("/ops/brain/eval-registry").json()
    suite = next(suite for suite in registry["suites"] if suite["suite_id"] == eval_registry_ref["suite_id"])
    assert registry["suite_count"] >= 1
    assert suite["status"] == "active"
    assert suite["held_out"] is True
    assert suite["promotion_target"] == "autonomous_update"
    assert suite["metadata"]["source"] == "release-wrapper-dream-research"
    assert suite["metadata"]["eval_case"]["eval_case_id"] == eval_case["eval_case_id"]
    assert suite["metadata"]["eval_case"]["raw_content_included"] is False
    assert suite["metadata"]["replay_template"]["endpoint"] == f"/ops/brain/eval-suites/{suite['suite_id']}/run-shadow"
    assert suite["metadata"]["replay_template"]["ready_for_operator_approval"] is False
    assert eval_case["eval_case_id"] in proposal["eval_refs"]
    assert eval_registry_ref["suite_id"] in proposal["eval_refs"]
    assert "Create wrapper eval evidence" not in json.dumps(registry)

    restarted = TestClient(create_app(str(project_root)))
    replayed_registry = restarted.get("/ops/brain/eval-registry").json()
    replayed_suite = next(
        suite for suite in replayed_registry["suites"] if suite["suite_id"] == eval_registry_ref["suite_id"]
    )
    assert replayed_suite["metadata"]["eval_case"]["eval_case_id"] == eval_case["eval_case_id"]


def test_release_wrapper_dream_research_proposal_exposes_safe_lifecycle_refs(tmp_path: Path):
    project_root = make_project(tmp_path)
    sandbox_probe = project_root / "tests" / "generated_dream_queue_probe_test.py"
    sandbox_probe.parent.mkdir(parents=True, exist_ok=True)
    sandbox_probe.write_text("def test_generated_dream_queue_probe():\n    assert 'wrapper'.upper() == 'WRAPPER'\n", encoding="utf-8")
    client = TestClient(create_app(str(project_root)))

    client.post(
        "/v1/chat",
        json={
            "session_id": "dream-lifecycle-user",
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": "Plan a safer wrapper dream lifecycle."}],
        },
    )
    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": "dream-lifecycle-user"}).json()
    latest_item = runtime["dream_research_queue"]["latest_actionable_item"]
    governance = latest_item["governance"]

    def linked_queue_status() -> str:
        queue_payload = client.get("/ops/brain/self-improvement/queue").json()
        linked = next(item for item in queue_payload["items"] if item["queue_id"] == latest_item["queue_id"])
        return linked["status"]

    assert linked_queue_status() == "proposed"
    assert governance["proposal_update_id"].startswith("update::release-wrapper-dream-research::")
    assert governance["queue_review_ref"] == f"/ops/brain/self-improvement/queue/{latest_item['queue_id']}/review"
    assert governance["admin_approval_ref"].endswith("/admin-approval")
    assert governance["sandbox_tests_ref"].endswith("/sandbox-tests")
    assert governance["apply_ref"].endswith("/apply")
    assert governance["rollback_ref"].endswith("/rollback")
    assert governance["active_production_mutation_allowed"] is False
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "dream-lifecycle-user"}).json()
    visualized = visualizer["overlay_state"]["control_panel"]["release_wrapper_runtime"]["dream_research_queue"]
    assert visualized["latest_actionable_item"]["governance"]["proposal_update_id"] == governance["proposal_update_id"]

    review = client.get(governance["queue_review_ref"])
    assert review.status_code == 200
    assert review.json()["queue_item"]["queue_id"] == latest_item["queue_id"]

    approval = client.post(
        governance["admin_approval_ref"],
        json={"approved_by": "admin", "approval_ref": "operator-review::dream-research-generated"},
    )
    assert approval.status_code == 200
    assert approval.json()["status"] == "admin-approved"
    eval_replay = approval.json()["linked_eval_replay"]
    assert eval_replay["status"] == "passed-shadow"
    assert eval_replay["promotion_allowed"] is True
    assert eval_replay["operator_approved"] is True
    assert eval_replay["metadata"]["queue_id"] == latest_item["queue_id"]
    proposal_after_approval = next(
        proposal
        for proposal in client.get("/ops/brain/autonomous-updates").json()["proposals"]
        if proposal["update_id"] == governance["proposal_update_id"]
    )
    assert proposal_after_approval["latest_eval_replay"]["run_id"] == eval_replay["run_id"]
    eval_registry = client.get("/ops/brain/eval-registry").json()
    shadow_run = next(run for run in eval_registry["shadow_runs"] if run["run_id"] == eval_replay["run_id"])
    assert shadow_run["status"] == "passed-shadow"
    assert linked_queue_status() == "validated"

    sandbox_run = client.post(
        governance["sandbox_tests_ref"],
        json={"command": "pytest tests/generated_dream_queue_probe_test.py -q", "timeout_seconds": 30},
    )
    assert sandbox_run.status_code == 200
    sandbox_payload = sandbox_run.json()
    assert sandbox_payload["status"] == "passed"
    assert sandbox_payload["sandbox"]["active_project_root_mutated"] is False
    assert sandbox_payload["diff_summary"]["unsafe_change_count"] == 0
    assert linked_queue_status() == "approved"

    applied = client.post(
        governance["apply_ref"],
        json={
            "test_refs": ["pytest tests/generated_dream_queue_probe_test.py -q"],
            "test_evidence_refs": [sandbox_payload["evidence_ref"]],
        },
    )
    assert applied.status_code == 200
    assert applied.json()["status"] == "applied-shadow-safe-file"
    assert applied.json()["active_production_mutated"] is False
    assert Path(applied.json()["safe_file_path"]).exists()
    assert linked_queue_status() == "deployed"

    rollback = client.post(governance["rollback_ref"], json={"reason": "release-wrapper-generated-lifecycle-test"})
    assert rollback.status_code == 200
    assert rollback.json()["status"] == "rolled-back"
    assert rollback.json()["rollback_restored"] is True
    assert linked_queue_status() == "reverted"


def test_release_readiness_manifest_starts_no_go_with_bootable_entrypoint(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.get("/ops/wrapper/release-readiness", params={"session_id": "readiness-empty"})

    assert response.status_code == 200
    manifest = response.json()
    assert manifest["surface_id"] == "release-wrapper-readiness"
    assert manifest["go_no_go"] == "no-go"
    assert manifest["status_label"] == "LOCKED CANON"
    assert manifest["product_surface"] == "wrapper"
    assert manifest["boot"]["boot_target"] == "/ui/wrapper/"
    assert manifest["boot"]["cli"] == "nexusnet-wrapper"
    checks = {check["check_id"]: check for check in manifest["readiness_checks"]}
    assert checks["bootable-entrypoint"]["status"] == "pass"
    assert checks["live-wrapper-interaction"]["status"] == "blocked"
    assert checks["continuous-assimilation"]["status"] == "blocked"
    assert checks["forward-pass-coverage"]["status"] == "blocked"
    assert checks["native-hive-heartbeat"]["status"] == "blocked"
    assert checks["effective-context-cache"]["status"] == "blocked"
    assert checks["ao-execution-receipt"]["status"] == "blocked"
    assert "live wrapper interaction evidence is missing" in manifest["blockers"]
    assert "forward-pass coverage receipt is missing or degraded" in manifest["blockers"]
    assert "native hive heartbeat receipt is stale or missing" in manifest["blockers"]
    assert "release-readiness.json" in manifest["artifact_path"]
    assert Path(manifest["artifact_path"]).exists()
    persisted = json.loads(Path(manifest["artifact_path"]).read_text(encoding="utf-8"))
    assert persisted["go_no_go"] == "no-go"
    assert "readiness-empty" not in json.dumps(manifest)
    assert manifest["privacy_boundary"].endswith("no-raw-prompts-outputs-session-ids")


def test_release_readiness_manifest_proves_live_wrapper_lifecycle_evidence(tmp_path: Path):
    project_root = make_project(tmp_path)
    sandbox_probe = project_root / "tests" / "readiness_manifest_probe_test.py"
    sandbox_probe.parent.mkdir(parents=True, exist_ok=True)
    sandbox_probe.write_text("def test_readiness_manifest_probe():\n    assert 'wrapper'.title() == 'Wrapper'\n", encoding="utf-8")
    client = TestClient(create_app(str(project_root)))
    session_id = "readiness-lifecycle-user"

    client.post(
        "/v1/chat",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": "Create release readiness evidence."}],
        },
    )
    packet = client.get("/ops/wrapper/federated-packets", params={"session_id": session_id}).json()["latest_packet"]
    imported = client.post(
        "/ops/wrapper/federated-packets/import",
        json={"session_id": session_id, "peer_node_id": "readiness-lifecycle-peer", "packet": packet},
    ).json()
    assert imported["status"] == "quarantined-shadow-accepted"

    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    governance = runtime["dream_research_queue"]["latest_item"]["governance"]
    approval = client.post(
        governance["admin_approval_ref"],
        json={"approved_by": "admin", "approval_ref": "operator-review::release-readiness"},
    )
    assert approval.status_code == 200
    sandbox_run = client.post(
        governance["sandbox_tests_ref"],
        json={"command": "pytest tests/readiness_manifest_probe_test.py -q", "timeout_seconds": 30},
    )
    assert sandbox_run.status_code == 200
    applied = client.post(
        governance["apply_ref"],
        json={
            "test_refs": ["pytest tests/readiness_manifest_probe_test.py -q"],
            "test_evidence_refs": [sandbox_run.json()["evidence_ref"]],
        },
    )
    assert applied.status_code == 200
    rollback = client.post(governance["rollback_ref"], json={"reason": "release-readiness-test"})
    assert rollback.status_code == 200

    response = client.get("/ops/wrapper/release-readiness", params={"session_id": session_id})

    assert response.status_code == 200
    manifest = response.json()
    checks = {check["check_id"]: check for check in manifest["readiness_checks"]}
    assert manifest["go_no_go"] == "go"
    assert manifest["blockers"] == []
    boot_contract = manifest["whole_system_boot_contract"]
    assert boot_contract["surface_id"] == "whole-system-release-boot-contract"
    assert boot_contract["product_scope"] == "whole-system"
    assert boot_contract["status"] == "passed"
    assert boot_contract["go_no_go_blocking"] is True
    subsystem_gates = {gate["gate_id"]: gate for gate in boot_contract["subsystem_gates"]}
    assert set(subsystem_gates) >= {
        "wrapper-product-entrypoint",
        "live-model-provider-path",
        "teacher-expert-birth-registry",
        "developmental-growth-promotion-governance",
        "authority-evidence-tool-governance",
        "native-hive-runtime-heartbeat",
        "assimilation-growth-expert-path",
        "federation-runtime-path",
        "eval-runtime-governance",
        "ao-runtime-governance",
        "sandboxed-self-repair-governance",
        "context-cache-truth-boundary",
        "production-spine-release-manifest",
        "visualizer-control-panel-surface",
    }
    assert all(gate["status"] == "pass" for gate in subsystem_gates.values())
    assert boot_contract["passed_count"] == len(subsystem_gates)
    assert boot_contract["blocked_count"] == 0
    for check_id in [
        "bootable-entrypoint",
        "live-wrapper-interaction",
        "continuous-assimilation",
        "global-growth",
        "federated-packet",
        "federated-packet-inbox",
        "peer-shadow-proposal",
        "production-spine-packet",
        "forward-pass-coverage",
        "native-hive-heartbeat",
        "effective-context-cache",
        "ao-execution-receipt",
        "dream-research-episode",
        "shadow-eval-replay",
        "sandbox-evidence",
        "safe-apply",
        "rollback",
        "expert-growth-routing",
        "teacher-expert-birth-registry",
        "developmental-growth-promotion-governance",
        "authority-evidence-tool-governance",
        "artifact-bound-replay-gate",
        "self-repair-ledger",
        "visualizer-control-panel-surface",
        "whole-system-release-boot-contract",
    ]:
        assert checks[check_id]["status"] == "pass"
    assert manifest["evidence"]["latest_interaction"]["raw_content_included"] is False
    assert manifest["evidence"]["forward_pass_coverage"]["latest_status"] == "covered"
    assert manifest["evidence"]["forward_pass_coverage"]["latest_receipt"]["raw_content_included"] is False
    heartbeat = manifest["evidence"]["native_hive_heartbeat"]
    assert heartbeat["surface_id"] == "release-wrapper-native-hive-heartbeat"
    assert heartbeat["status"] == "covered"
    assert heartbeat["covered_count"] == len(heartbeat["required_organs"])
    assert heartbeat["degraded_count"] == 0
    assert heartbeat["raw_content_included"] is False
    assert heartbeat["active_production_mutated"] is False
    assert manifest["evidence"]["latest_federated_packet"]["raw_content_included"] is False
    assert manifest["evidence"]["federated_packet_inbox"]["accepted_import_count"] >= 2
    assert manifest["evidence"]["peer_shadow_proposal"]["federated_packet_import_id"] == imported["import_id"]
    assert manifest["evidence"]["latest_eval_replay"]["status"] == "passed-shadow"
    assert manifest["evidence"]["latest_sandbox_test_evidence"]["status"] == "passed"
    assert manifest["evidence"]["latest_applied"]["status"] == "applied-shadow-safe-file"
    assert manifest["evidence"]["latest_rollback"]["status"] == "rolled-back"
    teacher_birth = manifest["evidence"]["teacher_expert_birth_registry"]
    assert teacher_birth["surface_id"] == "teacher-expert-birth-registry-release-gate"
    assert teacher_birth["teacher_registry"]["default_registry_layer"] == "v2026_live"
    assert teacher_birth["teacher_registry"]["schema_version"] == 2
    assert teacher_birth["teacher_registry"]["profile_count"] >= 19
    assert teacher_birth["teacher_registry"]["assignment_count"] >= 19
    assert teacher_birth["teacher_registry"]["live_core_expert_pair_count"] == 19
    assert teacher_birth["expert_roster"]["core_expert_count"] == 19
    assert teacher_birth["expert_roster"]["auxiliary_count"] >= 1
    assert teacher_birth["birth_stack"]["surface_id"] == "hive-neural-substrate-v0"
    assert teacher_birth["birth_stack"]["node_count"] >= 1
    assert teacher_birth["birth_stack"]["plane_count"] >= 1
    assert teacher_birth["birth_stack"]["birth_orchestrator_ref"] == "nexusnet.hive.net.birth_hive"
    assert teacher_birth["birth_stack"]["scorecard_ref"] == "/ops/brain/canon/hive-substrate"
    assert teacher_birth["raw_content_included"] is False
    assert teacher_birth["active_production_mutation_allowed"] is False
    assert any(ref == "/ops/brain/teachers" for ref in teacher_birth["evidence_refs"])
    assert any(ref == "/ops/brain/canon/hive-substrate" for ref in teacher_birth["evidence_refs"])
    developmental_growth = manifest["evidence"]["developmental_growth_promotion"]
    assert developmental_growth["surface_id"] == "developmental-growth-promotion-release-gate"
    assert developmental_growth["status"] == "pass"
    assert developmental_growth["developmental_cortex"]["surface_id"] == "developmental-cortex-kernel"
    assert developmental_growth["developmental_cortex"]["assessment_count"] >= 1
    assert developmental_growth["developmental_cortex"]["production_mutation_allowed"] is False
    assert developmental_growth["developmental_cortex"]["scorecard_ref"] == "/ops/brain/canon/developmental-cortex"
    assert developmental_growth["growth_archive"]["surface_id"] == "growth-archive"
    assert developmental_growth["growth_archive"]["candidate_count"] >= 1
    assert developmental_growth["growth_archive"]["production_mutation_allowed"] is False
    assert developmental_growth["growth_engine"]["surface_id"] == "hive-model-growth-engine"
    assert developmental_growth["growth_engine"]["mutation_boundary"] == "dry-run-no-weight-update"
    assert developmental_growth["promotion_tribunal"]["surface_id"] == "promotion-tribunal"
    assert developmental_growth["promotion_tribunal"]["decision_boundary"] == "active-promotion-requires-all-gates-and-operator-approval"
    assert developmental_growth["promotion_service"]["surface_id"] == "promotion-service"
    assert developmental_growth["raw_content_included"] is False
    assert developmental_growth["active_production_mutation_allowed"] is False
    assert any(ref == "/ops/brain/canon/developmental-cortex" for ref in developmental_growth["evidence_refs"])
    assert any(ref == "/ops/brain/canon/growth-engine" for ref in developmental_growth["evidence_refs"])
    assert any(ref == "/ops/brain/promotions" for ref in developmental_growth["evidence_refs"])
    authority_governance = manifest["evidence"]["authority_evidence_tool_governance"]
    assert authority_governance["surface_id"] == "authority-evidence-tool-governance-release-gate"
    assert authority_governance["status"] == "pass"
    assert authority_governance["authority_spine"]["surface_id"] == "authority-integrity-spine"
    assert authority_governance["evidence_store"]["surface_id"] == "content-addressed-evidence-store"
    assert authority_governance["eval_federation"]["surface_id"] == "eval-federation"
    assert authority_governance["tool_action_harness"]["surface_id"] == "tool-action-harness"
    assert authority_governance["runtime_decision_ledger"]["surface_id"] == "runtime-decision-ledger"
    assert authority_governance["raw_content_included"] is False
    assert authority_governance["active_production_mutation_allowed"] is False
    assert any(ref == "/ops/brain/canon/authority-spine" for ref in authority_governance["evidence_refs"])
    assert any(ref == "/ops/brain/canon/evidence-store" for ref in authority_governance["evidence_refs"])
    assert any(ref == "/ops/brain/canon/eval-federation" for ref in authority_governance["evidence_refs"])
    assert any(ref == "/ops/brain/canon/tool-action-harness" for ref in authority_governance["evidence_refs"])
    assert Path(manifest["artifact_path"]).exists()
    persisted = json.loads(Path(manifest["artifact_path"]).read_text(encoding="utf-8"))
    assert persisted["manifest_id"] == manifest["manifest_id"]
    assert persisted["go_no_go"] == "go"
    assert persisted["whole_system_boot_contract"]["status"] == "passed"
    assert "Create release readiness evidence" not in json.dumps(manifest)
    assert session_id not in json.dumps(manifest)


def test_release_readiness_runner_drives_governed_evidence_path(tmp_path: Path):
    project_root = make_project(tmp_path)
    sandbox_probe = project_root / "tests" / "release_wrapper_readiness_runner_probe_test.py"
    sandbox_probe.parent.mkdir(parents=True, exist_ok=True)
    sandbox_probe.write_text("def test_release_wrapper_readiness_runner_probe():\n    assert True\n", encoding="utf-8")
    client = TestClient(create_app(str(project_root)))
    session_id = "release-readiness-runner-user"
    prompt = "Run the release readiness runner without leaking SECRET-RUNNER-123."

    chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    assert chat.status_code == 200
    packet = client.get("/ops/wrapper/federated-packets", params={"session_id": session_id}).json()["latest_packet"]
    imported = client.post(
        "/ops/wrapper/federated-packets/import",
        json={"session_id": session_id, "peer_node_id": "readiness-runner-peer", "packet": packet},
    ).json()
    assert imported["status"] == "quarantined-shadow-accepted"
    import_receipt = imported["operation_receipt"]
    assert import_receipt["surface_id"] == "release-wrapper-runtime-operation-receipt"
    assert import_receipt["operation_type"] == "federated_packet_import"
    assert import_receipt["status"] == "covered"
    assert import_receipt["active_production_mutation_allowed"] is False
    assert import_receipt["active_production_mutated"] is False
    assert {stage["stage_id"]: stage["status"] for stage in import_receipt["stages"]} == {
        "security_envelope": "covered",
        "privacy_consent_enforcement": "covered",
        "shadow_quarantine": "covered",
        "continuous_assimilation": "covered",
        "global_growth": "covered",
        "evals_ao_artifact_gate": "covered",
        "dream_research_queue": "covered",
    }
    import_whole_system_receipt = imported["whole_system_enforcement_receipt"]
    assert imported["whole_system_enforcement_receipt_id"] == import_whole_system_receipt["receipt_id"]
    assert import_whole_system_receipt["surface_id"] == (
        "federated-packet-import-whole-system-enforcement-receipt"
    )
    assert import_whole_system_receipt["source_import_id"] == imported["import_id"]
    assert import_whole_system_receipt["source_packet_ref"] == imported["source_packet_ref"]
    assert import_whole_system_receipt["operation_receipt_id"] == import_receipt["receipt_id"]
    assert import_whole_system_receipt["status"] == "covered"
    assert import_whole_system_receipt["coverage_status"] == "covered"
    assert import_whole_system_receipt["raw_content_included"] is False
    assert import_whole_system_receipt["active_production_mutation_allowed"] is False
    assert import_whole_system_receipt["active_production_mutated"] is False
    assert {stage["stage_id"]: stage["status"] for stage in import_whole_system_receipt["stages"]} == {
        "security_envelope": "covered",
        "shadow_quarantine": "covered",
        "continuous_assimilation": "covered",
        "global_growth": "covered",
        "evals_ao_artifact_gate": "covered",
        "dream_research_queue": "covered",
    }
    assert any(
        ref == f"operation-receipt::{import_receipt['receipt_id']}"
        for ref in import_whole_system_receipt["evidence_refs"]
    )

    response = client.post(
        "/ops/wrapper/release-readiness/run",
        json={
            "session_id": session_id,
            "command": "pytest tests/release_wrapper_readiness_runner_probe_test.py -q",
            "timeout_seconds": 30,
            "approved_by": "admin",
            "approval_ref": "operator-review::release-readiness-runner",
        },
    )

    assert response.status_code == 200
    run = response.json()
    assert run["surface_id"] == "release-wrapper-readiness-evidence-run"
    assert run["status"] == "completed"
    assert run["session_ref_digest"] != session_id
    assert run["active_production_mutated"] is False
    assert run["actions"]["admin_approval"]["status"] == "admin-approved"
    assert run["actions"]["admin_approval"]["linked_eval_replay"]["status"] == "passed-shadow"
    assert run["actions"]["sandbox_tests"]["status"] == "passed"
    assert run["actions"]["apply"]["status"] == "applied-shadow-safe-file"
    assert run["actions"]["rollback"]["status"] == "rolled-back"
    for action_id, expected_status in {
        "admin_approval": "admin-approved",
        "sandbox_tests": "passed",
        "apply": "applied-shadow-safe-file",
        "rollback": "rolled-back",
    }.items():
        repair = run["actions"][action_id]["release_wrapper_self_repair"]
        receipt = repair["operation_receipt"]
        assert receipt["surface_id"] == "release-wrapper-runtime-operation-receipt"
        assert receipt["operation_type"] == "self_repair_action"
        assert receipt["action"] == action_id
        assert receipt["status"] == "covered"
        assert receipt["observed_status"] == expected_status
        assert receipt["raw_content_included"] is False
        assert receipt["active_production_mutated"] is False
        stage_statuses = {stage["stage_id"]: stage["status"] for stage in receipt["stages"]}
        assert stage_statuses["ao_guard"] == "covered"
        assert stage_statuses["authority_decision"] == "covered"
        assert stage_statuses["active_production_mutation"] == "covered"
    assert run["readiness_after"]["go_no_go"] == "go"
    assert Path(run["artifact_path"]).exists()

    readiness = client.get("/ops/wrapper/release-readiness", params={"session_id": session_id}).json()
    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    lifecycle = client.get("/ops/wrapper/session-lifecycle", params={"session_id": session_id}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]
    runner_summary = readiness["evidence"]["release_readiness_evidence_runner"]
    inbox = runtime["federated_packet_inbox"]
    matrix = runtime["whole_system_forward_pass_enforcement_matrix"]
    rows = {row["entrypoint_id"]: row for row in matrix["entrypoints"]}
    self_repair_actions = {
        action["action"]: action
        for action in runtime["self_repair_ledger"]["actions"]
    }
    control_panel_runtime = control_panel["release_wrapper_runtime"]
    control_panel_rows = {
        row["entrypoint_id"]: row
        for row in control_panel_runtime["whole_system_forward_pass_enforcement_matrix"]["entrypoints"]
    }
    control_panel_self_repair_actions = {
        action["action"]: action
        for action in control_panel_runtime["self_repair_ledger"]["actions"]
    }
    checks = {check["check_id"]: check for check in readiness["readiness_checks"]}

    assert readiness["go_no_go"] == "go"
    assert checks["federated-packet-inbox"]["status"] == "pass"
    assert checks["peer-shadow-proposal"]["status"] == "pass"
    assert readiness["evidence"]["peer_shadow_proposal"]["federated_packet_import_id"] == imported["import_id"]
    assert inbox["latest_import"]["operation_receipt"]["receipt_id"] == import_receipt["receipt_id"]
    governed_import_receipt = inbox["latest_import"]["whole_system_enforcement_receipt"]
    governed_update_path = governed_import_receipt["governed_update_path"]
    assert governed_update_path["status"] == "completed-admin-approved-sandbox-applied-rolled-back"
    assert governed_update_path["readiness_run_id"] == run["run_id"]
    assert governed_update_path["update_id"] == run["update_id"]
    assert governed_update_path["action_statuses"] == {
        "admin_approval": "admin-approved",
        "sandbox_tests": "passed",
        "apply": "applied-shadow-safe-file",
        "rollback": "rolled-back",
    }
    assert governed_update_path["action_operation_receipt_ids"] == {
        action_id: run["actions"][action_id]["release_wrapper_self_repair"]["operation_receipt"]["receipt_id"]
        for action_id in ("admin_approval", "sandbox_tests", "apply", "rollback")
    }
    assert governed_import_receipt["replay"]["latest_readiness_run_id"] == run["run_id"]
    assert governed_import_receipt["replay"]["latest_readiness_run_status"] == "completed"
    assert governed_import_receipt["active_production_mutated"] is False
    assert (
        inbox["latest_import"]["whole_system_enforcement_receipt"]["receipt_id"]
        == import_whole_system_receipt["receipt_id"]
    )
    assert rows["federated_packet_import"]["operation_receipt"]["receipt_id"] == import_receipt["receipt_id"]
    assert (
        rows["federated_packet_import"]["whole_system_enforcement_receipt"]["receipt_id"]
        == import_whole_system_receipt["receipt_id"]
    )
    assert any(ref.startswith("operation-receipt::") for ref in rows["federated_packet_import"]["evidence_refs"])
    assert any(
        ref == f"whole-system-import-receipt::{import_whole_system_receipt['receipt_id']}"
        for ref in rows["federated_packet_import"]["evidence_refs"]
    )
    assert (
        control_panel_runtime["federated_packet_inbox"]["latest_import"]["operation_receipt"]["receipt_id"]
        == import_receipt["receipt_id"]
    )
    assert (
        control_panel_runtime["federated_packet_inbox"]["latest_import"]["whole_system_enforcement_receipt"]["receipt_id"]
        == import_whole_system_receipt["receipt_id"]
    )
    assert (
        control_panel_runtime["federated_packet_inbox"]["latest_import"]["whole_system_enforcement_receipt"]
        ["governed_update_path"]["status"]
        == "completed-admin-approved-sandbox-applied-rolled-back"
    )
    assert (
        control_panel_rows["federated_packet_import"]["operation_receipt"]["receipt_id"]
        == import_receipt["receipt_id"]
    )
    assert (
        control_panel_rows["federated_packet_import"]["whole_system_enforcement_receipt"]["receipt_id"]
        == import_whole_system_receipt["receipt_id"]
    )
    assert (
        control_panel_rows["federated_packet_import"]["whole_system_enforcement_receipt"]
        ["governed_update_path"]["readiness_run_id"]
        == run["run_id"]
    )
    for action_id in ("admin_approval", "sandbox_tests", "apply", "rollback"):
        row_id = "safe_apply" if action_id == "apply" else action_id
        assert rows[row_id]["operation_receipt"]["receipt_id"] == self_repair_actions[action_id]["operation_receipt"]["receipt_id"]
        assert any(ref.startswith("operation-receipt::") for ref in rows[row_id]["evidence_refs"])
        assert (
            control_panel_self_repair_actions[action_id]["operation_receipt"]["receipt_id"]
            == self_repair_actions[action_id]["operation_receipt"]["receipt_id"]
        )
        assert (
            control_panel_rows[row_id]["operation_receipt"]["receipt_id"]
            == self_repair_actions[action_id]["operation_receipt"]["receipt_id"]
        )
    assert runner_summary["latest_status"] == "completed"
    assert runner_summary["latest_run"]["run_id"] == run["run_id"]
    assert status_card["release_readiness_evidence_runner"]["latest_run"]["run_id"] == run["run_id"]
    assert status_card["operator_action_lane"]["run_readiness_evidence_ref"] == "/ops/wrapper/release-readiness/run"
    assert lifecycle["readiness"]["go_no_go"] == "go"

    replay_client = TestClient(create_app(str(project_root)))
    replay_runtime = replay_client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    replay_import = replay_runtime["federated_packet_inbox"]["latest_import"]
    replay_receipt = replay_import["whole_system_enforcement_receipt"]
    assert replay_import["import_id"] == imported["import_id"]
    assert replay_receipt["receipt_id"] == import_whole_system_receipt["receipt_id"]
    assert replay_receipt["governed_update_path"]["status"] == "completed-admin-approved-sandbox-applied-rolled-back"
    assert replay_receipt["governed_update_path"]["readiness_run_id"] == run["run_id"]
    assert replay_receipt["replay"]["latest_readiness_run_id"] == run["run_id"]
    assert replay_receipt["raw_content_included"] is False
    assert replay_receipt["active_production_mutation_allowed"] is False
    assert replay_receipt["active_production_mutated"] is False

    serialized = json.dumps({"run": run, "readiness": readiness, "status_card": status_card, "lifecycle": lifecycle})
    assert prompt not in serialized
    assert session_id not in serialized
    assert "SECRET-RUNNER-123" not in serialized
    assert "run_readiness_evidence_ref" in serialized

    control_panel_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    visualizer_js = (project_root / "ui" / "visualizer" / "app.js").read_text(encoding="utf-8")
    assert "Release Harness operation receipts" in control_panel_js
    assert "operation receipt refs" in control_panel_js
    assert "federated import receipt" in control_panel_js
    assert "self-repair operation receipt" in control_panel_js
    assert "renderReleaseWrapperStatusFallback" in control_panel_js
    assert "release-wrapper-status-card-fallback" in control_panel_js
    assert "Loading full visualizer state" in control_panel_js
    assert "Universal Evolution" in control_panel_js
    assert "legacy-lane-coverage-is-not-universal-organism-coverage" in control_panel_js
    assert "universal_coverage_complete" in control_panel_js
    assert "evolution-prerequisite-gaps" in control_panel_js
    assert "Harness operation receipts" in visualizer_js
    assert "Harness import receipt" in visualizer_js


def test_control_panel_evolution_projection_distinguishes_unavailable_telemetry():
    control_panel_js = (Path(__file__).parents[1] / "ui" / "control-panel" / "app.js").read_text(
        encoding="utf-8"
    )
    assert "function renderUniversalEvolutionCard" in control_panel_js
    helper_start = control_panel_js.index("function isUniversalEvolutionStatusAvailable")
    helper_end = control_panel_js.index("function renderAutonomousUpdatesScorecard", helper_start)
    helper_source = control_panel_js[helper_start:helper_end]
    node_script = (
        """
function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
"""
        + helper_source
        + """
const unavailable = [
  renderUniversalEvolutionCard(undefined),
  renderUniversalEvolutionCard({}),
  renderUniversalEvolutionCard({ authority: "NexusBrain", coverage: {} }),
  renderUniversalEvolutionCard({
    authority: "NexusBrain",
    open_pressure_count: 0,
    coverage: {
      registered_unit_total: -1,
      covered_unit_total: 0,
      uncovered_unit_refs: [],
      universal_coverage_complete: false,
    },
    top_pressures: [],
    missing_or_unverified_prerequisites: [],
    last_event_sha256: null,
    claim_boundary: "legacy-lane-coverage-is-not-universal-organism-coverage",
    mutation_boundary: "read-only-no-protected-state-mutation",
  }),
  renderUniversalEvolutionCard({
    authority: "NexusBrain",
    open_pressure_count: 0,
    coverage: {
      registered_unit_total: 3,
      covered_unit_total: 2,
      uncovered_unit_refs: [],
      universal_coverage_complete: false,
    },
    top_pressures: [],
    missing_or_unverified_prerequisites: [],
    last_event_sha256: null,
    claim_boundary: "legacy-lane-coverage-is-not-universal-organism-coverage",
    mutation_boundary: "read-only-no-protected-state-mutation",
  }),
  renderUniversalEvolutionCard({
    authority: "NexusBrain",
    open_pressure_count: 6,
    coverage: {
      registered_unit_total: 3,
      covered_unit_total: 2,
      uncovered_unit_refs: ["unit:uncovered"],
      universal_coverage_complete: false,
    },
    top_pressures: [{ pressure_id: "pressure:only-one-of-five" }],
    missing_or_unverified_prerequisites: [],
    last_event_sha256: null,
    claim_boundary: "legacy-lane-coverage-is-not-universal-organism-coverage",
    mutation_boundary: "read-only-no-protected-state-mutation",
  }),
  renderUniversalEvolutionCard({
    authority: "NexusBrain",
    open_pressure_count: 0,
    coverage: {
      registered_unit_total: 0,
      covered_unit_total: 0,
      uncovered_unit_refs: [],
      universal_coverage_complete: false,
      claim_boundary: "legacy-lane-coverage-is-not-universal-organism-coverage",
    },
    top_pressures: [],
    missing_or_unverified_prerequisites: [],
    last_event_sha256: null,
    claim_boundary: "wrong-service-boundary",
    mutation_boundary: "read-only-no-protected-state-mutation",
  }),
  renderUniversalEvolutionCard({
    authority: "NexusBrain",
    open_pressure_count: 0,
    coverage: {
      registered_unit_total: 0,
      covered_unit_total: 0,
      uncovered_unit_refs: [],
      universal_coverage_complete: false,
      claim_boundary: "legacy-lane-coverage-is-not-universal-organism-coverage",
    },
    top_pressures: [],
    missing_or_unverified_prerequisites: [],
    last_event_sha256: null,
    claim_boundary: "registry-and-evidence-state-only; no candidate, experiment, promotion, native-model-birth, or frontier-superiority claim",
  }),
  renderUniversalEvolutionCard({
    authority: "NexusBrain",
    open_pressure_count: 0,
    coverage: {
      registered_unit_total: 0,
      covered_unit_total: 0,
      uncovered_unit_refs: [],
      universal_coverage_complete: false,
      claim_boundary: "wrong-coverage-boundary",
    },
    top_pressures: [],
    missing_or_unverified_prerequisites: [],
    last_event_sha256: null,
    claim_boundary: "registry-and-evidence-state-only; no candidate, experiment, promotion, native-model-birth, or frontier-superiority claim",
    mutation_boundary: "read-only-no-protected-state-mutation",
  }),
];
const available = renderUniversalEvolutionCard({
  authority: "NexusBrain",
  unit_count: 3,
  open_pressure_count: 1,
  coverage: {
    registered_unit_total: 3,
    covered_unit_total: 2,
    uncovered_unit_refs: ["unit:<script>"],
    universal_coverage_complete: false,
    claim_boundary: "legacy-lane-coverage-is-not-universal-organism-coverage",
  },
  top_pressures: [{ pressure_id: "pressure:<script>" }],
  missing_or_unverified_prerequisites: ["neural_<script>"],
  last_event_sha256: "sha256:<script>",
  claim_boundary: "registry-and-evidence-state-only; no candidate, experiment, promotion, native-model-birth, or frontier-superiority claim",
  mutation_boundary: "read-only-no-protected-state-mutation",
});
process.stdout.write(JSON.stringify({ unavailable, available }));
"""
    )
    rendered = subprocess.run(
        ["node", "-e", node_script],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(rendered.stdout)

    for unavailable in payload["unavailable"]:
        assert "evolution-status-unavailable" in unavailable
        assert "telemetry is unavailable/unverified" in unavailable
        assert "coverage, pressure, and prerequisite state was not observed" in unavailable
        assert "legacy-lane-coverage-is-not-universal-organism-coverage" in unavailable
        assert "registered_unit_count" not in unavailable
        assert "<strong>0</strong>" not in unavailable
        assert "none-reported" not in unavailable
        assert "no-open-pressure" not in unavailable
        assert "no-event-hash" not in unavailable
        assert "none-observed-in-loaded-status" not in unavailable
        assert "not-applicable-no-open-pressures" not in unavailable
        assert "not-recorded-in-loaded-status" not in unavailable

    available = payload["available"]
    assert "universal-evolution-card" in available
    assert "evolution-status-unavailable" not in available
    assert "open pressure count" in available
    assert "top pressure ID" in available
    assert "legacy-lane-coverage-is-not-universal-organism-coverage" in available
    assert "&lt;script&gt;" in available
    assert "<script>" not in available
    assert "data-release-wrapper-action" not in available


def test_release_readiness_blocks_go_without_accepted_peer_federation_import(tmp_path: Path):
    project_root = make_project(tmp_path)
    sandbox_probe = project_root / "tests" / "release_wrapper_readiness_requires_peer_import_probe_test.py"
    sandbox_probe.parent.mkdir(parents=True, exist_ok=True)
    sandbox_probe.write_text(
        "def test_release_wrapper_readiness_requires_peer_import_probe():\n    assert True\n",
        encoding="utf-8",
    )
    client = TestClient(create_app(str(project_root)))
    session_id = "release-readiness-requires-peer-import-user"

    chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "mock/default",
            "messages": [{"role": "user", "content": "Readiness must require inbound peer federation."}],
        },
    )
    assert chat.status_code == 200

    run = client.post(
        "/ops/wrapper/release-readiness/run",
        json={
            "session_id": session_id,
            "command": "pytest tests/release_wrapper_readiness_requires_peer_import_probe_test.py -q",
            "timeout_seconds": 30,
            "approved_by": "admin",
            "approval_ref": "operator-review::readiness-requires-peer-import",
        },
    ).json()
    readiness = client.get("/ops/wrapper/release-readiness", params={"session_id": session_id}).json()
    checks = {check["check_id"]: check for check in readiness["readiness_checks"]}

    assert run["readiness_after"]["go_no_go"] == "no-go"
    assert readiness["go_no_go"] == "no-go"
    assert checks["federated-packet-inbox"]["status"] == "blocked"
    assert checks["peer-shadow-proposal"]["status"] == "blocked"
    assert readiness["evidence"]["federated_packet_inbox"]["import_count"] == 0
    serialized = json.dumps({"run": run, "readiness": readiness})
    assert session_id not in serialized
    assert "Readiness must require inbound peer federation" not in serialized


def test_release_readiness_blocks_stale_native_hive_heartbeat_history(tmp_path: Path):
    project_root = make_project(tmp_path)
    sandbox_probe = project_root / "tests" / "stale_native_hive_heartbeat_probe_test.py"
    sandbox_probe.parent.mkdir(parents=True, exist_ok=True)
    sandbox_probe.write_text(
        "def test_stale_native_hive_heartbeat_probe():\n    assert 'heartbeat'.upper() == 'HEARTBEAT'\n",
        encoding="utf-8",
    )
    client = TestClient(create_app(str(project_root)))
    session_id = "stale-native-heartbeat-user"

    chat = client.post(
        "/v1/chat",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": "Prove fresh native hive heartbeat history."}],
        },
    )
    assert chat.status_code == 200
    packet = client.get("/ops/wrapper/federated-packets", params={"session_id": session_id}).json()["latest_packet"]
    imported = client.post(
        "/ops/wrapper/federated-packets/import",
        json={"session_id": session_id, "peer_node_id": "stale-heartbeat-peer", "packet": packet},
    ).json()
    assert imported["status"] == "quarantined-shadow-accepted"

    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    governance = runtime["dream_research_queue"]["latest_item"]["governance"]
    approval = client.post(
        governance["admin_approval_ref"],
        json={"approved_by": "admin", "approval_ref": "operator-review::native-heartbeat-freshness"},
    )
    assert approval.status_code == 200
    sandbox = client.post(
        governance["sandbox_tests_ref"],
        json={"command": "pytest tests/stale_native_hive_heartbeat_probe_test.py -q", "timeout_seconds": 30},
    )
    assert sandbox.status_code == 200
    applied = client.post(
        governance["apply_ref"],
        json={
            "test_refs": ["pytest tests/stale_native_hive_heartbeat_probe_test.py -q"],
            "test_evidence_refs": [sandbox.json()["evidence_ref"]],
        },
    )
    assert applied.status_code == 200
    rollback = client.post(governance["rollback_ref"], json={"reason": "native-heartbeat-freshness-test"})
    assert rollback.status_code == 200

    fresh_readiness = client.get("/ops/wrapper/release-readiness", params={"session_id": session_id}).json()
    fresh_runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    fresh_heartbeat = fresh_runtime["native_hive_heartbeat"]
    history = fresh_heartbeat["heartbeat_history"]
    history_path = project_root / "artifacts" / "release-wrapper-runtime" / "native-hive-heartbeats.jsonl"

    assert fresh_readiness["go_no_go"] == "go"
    assert fresh_heartbeat["latest_fresh"] is True
    assert fresh_heartbeat["freshness_status"] == "fresh"
    assert fresh_heartbeat["freshness_window_seconds"] == 300
    assert history["surface_id"] == "release-wrapper-native-hive-heartbeat-history"
    assert history["artifact_ref"] == "release-wrapper-runtime/native-hive-heartbeats.jsonl"
    assert history["latest_heartbeat_id"] == fresh_heartbeat["heartbeat_id"]
    assert history["latest_fresh"] is True
    assert history["raw_content_included"] is False
    assert history_path.exists()
    history_lines = [json.loads(line) for line in history_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert history_lines[-1]["heartbeat_id"] == fresh_heartbeat["heartbeat_id"]
    assert history_lines[-1]["raw_content_included"] is False
    assert "Prove fresh native hive heartbeat history" not in json.dumps(history_lines)
    assert session_id not in json.dumps(history_lines)

    runtime_obj = client.app.state.release_wrapper_runtime
    stale_created_at = "2020-01-01T00:00:00Z"
    runtime_obj._interactions[0]["native_hive_heartbeat"]["created_at"] = stale_created_at
    runtime_obj._native_hive_heartbeats[0]["created_at"] = stale_created_at

    stale_readiness = client.get("/ops/wrapper/release-readiness", params={"session_id": session_id}).json()
    stale_runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    stale_checks = {check["check_id"]: check for check in stale_readiness["readiness_checks"]}

    assert stale_runtime["native_hive_heartbeat"]["latest_fresh"] is False
    assert stale_runtime["native_hive_heartbeat"]["freshness_status"] == "stale"
    assert stale_runtime["native_hive_heartbeat"]["heartbeat_history"]["latest_fresh"] is False
    assert stale_readiness["go_no_go"] == "no-go"
    assert stale_checks["native-hive-heartbeat"]["status"] == "blocked"
    assert "native hive heartbeat receipt is stale or missing" in stale_readiness["blockers"]


def test_release_wrapper_native_hive_heartbeat_watchdog_replays_startup_status(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    session_id = "native-heartbeat-watchdog-user"
    prompt = "Trigger native hive heartbeat watchdog with marker SECRET-WATCHDOG."

    before_runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    before_readiness = client.get("/ops/wrapper/release-readiness", params={"session_id": session_id}).json()
    before_checks = {check["check_id"]: check for check in before_readiness["readiness_checks"]}

    assert before_runtime["native_hive_heartbeat_watchdog"]["surface_id"] == "release-wrapper-native-hive-heartbeat-watchdog"
    assert before_runtime["native_hive_heartbeat_watchdog"]["status"] == "blocked"
    assert before_runtime["native_hive_heartbeat_watchdog"]["latest_fresh"] is False
    assert before_runtime["native_hive_heartbeat_watchdog"]["raw_content_included"] is False
    assert before_checks["native-hive-heartbeat-watchdog"]["status"] == "blocked"
    assert before_readiness["go_no_go"] == "no-go"

    response = client.post(
        "/v1/chat",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    assert response.status_code == 200

    fresh_runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    assert fresh_runtime["native_hive_heartbeat"]["runtime_state"] == "live-bound"
    assert fresh_runtime["native_hive_heartbeat"]["heartbeat_history"]["latest_fresh"] is True
    assert fresh_runtime["native_hive_heartbeat_watchdog"]["status"] == "fresh"
    assert fresh_runtime["native_hive_heartbeat_watchdog"]["runtime_state"] == "live-bound"

    restarted = TestClient(create_app(str(project_root)))
    runtime = restarted.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    readiness = restarted.get("/ops/wrapper/release-readiness", params={"session_id": session_id}).json()
    status_card = restarted.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    lifecycle = restarted.get("/ops/wrapper/session-lifecycle", params={"session_id": session_id}).json()
    visualizer = restarted.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    checks = {check["check_id"]: check for check in readiness["readiness_checks"]}
    watchdog = runtime["native_hive_heartbeat_watchdog"]
    watchdog_path = project_root / "artifacts" / "release-wrapper-runtime" / "native-hive-heartbeat-watchdog.json"
    watchdog_artifact = json.loads(watchdog_path.read_text(encoding="utf-8"))

    assert watchdog["surface_id"] == "release-wrapper-native-hive-heartbeat-watchdog"
    assert watchdog["status"] == "fresh"
    assert watchdog["runtime_state"] == "replayed-history"
    assert watchdog["latest_fresh"] is True
    assert watchdog["freshness_status"] == "fresh"
    assert watchdog["artifact_ref"] == "release-wrapper-runtime/native-hive-heartbeats.jsonl"
    assert watchdog["watchdog_ref"] == "release-wrapper-runtime/native-hive-heartbeat-watchdog.json"
    assert watchdog["heartbeat_count"] >= 1
    assert watchdog["latest_heartbeat_id"] == runtime["native_hive_heartbeat"]["heartbeat_id"]
    assert watchdog["raw_content_included"] is False
    assert watchdog["active_production_mutation_allowed"] is False
    assert checks["native-hive-heartbeat-watchdog"]["status"] == "pass"
    assert checks["native-hive-heartbeat-watchdog"]["go_no_go_blocking"] is True
    assert status_card["native_hive_heartbeat_watchdog"]["status"] == "fresh"
    assert status_card["runtime"]["native_hive_heartbeat_watchdog"]["status"] == "fresh"
    assert lifecycle["native_hive_heartbeat_watchdog"]["status"] == "fresh"
    assert (
        visualizer["overlay_state"]["control_panel"]["release_wrapper_native_hive_heartbeat_watchdog"]["status"]
        == "fresh"
    )
    assert watchdog_artifact["status"] == "fresh"
    assert watchdog_artifact["raw_content_included"] is False
    assert prompt not in json.dumps(watchdog_artifact)
    assert session_id not in json.dumps(watchdog_artifact)

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    visualizer_js = (project_root / "ui" / "visualizer" / "app.js").read_text(encoding="utf-8")
    assert "native_hive_heartbeat_watchdog" in app_js
    assert "Heartbeat watchdog" in app_js
    assert "release_wrapper_native_hive_heartbeat_watchdog" in visualizer_js
    assert "heartbeat watchdog" in visualizer_js


def test_release_wrapper_dream_research_episode_replays_after_app_restart(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    client.post(
        "/v1/chat",
        json={
            "session_id": "dream-replay-user",
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": "Persist a dream research episode."}],
        },
    )
    before = client.get("/ops/wrapper/release-runtime", params={"session_id": "dream-replay-user"}).json()
    before_episode = before["dream_research_queue"]["latest_actionable_episode"]

    restarted = TestClient(create_app(str(project_root)))
    after = restarted.get("/ops/wrapper/release-runtime", params={"session_id": "dream-replay-user"}).json()
    visualizer = restarted.get("/ops/brain/visualizer/state", params={"session_id": "dream-replay-user"}).json()

    assert after["replay"]["status"] == "replayed"
    assert after["dream_research_queue"]["episode_count"] >= 2
    assert after["dream_research_queue"]["latest_actionable_episode"]["episode_id"] == before_episode["episode_id"]
    assert after["dream_research_queue"]["latest_actionable_item"]["research_status"] == "researched"
    assert after["dream_research_queue"]["latest_actionable_episode"]["raw_content_included"] is False
    assert "Persist a dream research episode" not in json.dumps(after)
    visualized = visualizer["overlay_state"]["control_panel"]["release_wrapper_runtime"]["dream_research_queue"]
    assert visualized["latest_actionable_episode"]["episode_id"] == before_episode["episode_id"]


def test_release_wrapper_dream_research_proposal_lifecycle_replays_after_app_restart(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    client.post(
        "/v1/chat",
        json={
            "session_id": "dream-proposal-replay-user",
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": "Persist dream proposal approval replay."}],
        },
    )
    before = client.get("/ops/wrapper/release-runtime", params={"session_id": "dream-proposal-replay-user"}).json()
    latest_item = before["dream_research_queue"]["latest_actionable_item"]
    governance = latest_item["governance"]
    proposal_update_id = governance["proposal_update_id"]

    approval = client.post(
        governance["admin_approval_ref"],
        json={"approved_by": "admin", "approval_ref": "operator-review::dream-proposal-replay"},
    )
    assert approval.status_code == 200
    eval_replay = approval.json()["linked_eval_replay"]

    restarted = TestClient(create_app(str(project_root)))
    after = restarted.get(
        "/ops/wrapper/release-runtime",
        params={"session_id": "dream-proposal-replay-user"},
    ).json()
    readiness = restarted.get(
        "/ops/wrapper/release-readiness",
        params={"session_id": "dream-proposal-replay-user"},
    ).json()
    visualizer = restarted.get(
        "/ops/brain/visualizer/state",
        params={"session_id": "dream-proposal-replay-user"},
    ).json()

    replayed_proposal = next(
        proposal
        for proposal in after["autonomous_updates"]["proposals"]
        if proposal["update_id"] == proposal_update_id
    )
    assert after["dream_research_queue"]["replay"]["status"] == "replayed"
    assert after["dream_research_queue"]["replay"]["episode_count"] >= 2
    assert after["dream_research_queue"]["latest_actionable_item"]["governance"]["proposal_status"] == "admin-approved"
    assert replayed_proposal["operator_approved"] is True
    assert replayed_proposal["latest_eval_replay"]["run_id"] == eval_replay["run_id"]
    assert readiness["evidence"]["dream_research_queue"]["replay"]["status"] == "replayed"
    visualized = visualizer["overlay_state"]["control_panel"]["release_wrapper_runtime"]["dream_research_queue"]
    assert visualized["replay"]["status"] == "replayed"
    assert "Persist dream proposal approval replay" not in json.dumps(after)
    assert "dream-proposal-replay-user" not in json.dumps(readiness)


def test_release_wrapper_status_card_is_lightweight_control_panel_surface_after_restart(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    client.post(
        "/v1/chat",
        json={
            "session_id": "release-status-card-user",
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": "Load compact wrapper status card evidence."}],
        },
    )
    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": "release-status-card-user"}).json()
    governance = runtime["dream_research_queue"]["latest_item"]["governance"]
    approval = client.post(
        governance["admin_approval_ref"],
        json={"approved_by": "admin", "approval_ref": "operator-review::release-status-card"},
    )
    assert approval.status_code == 200

    restarted = TestClient(create_app(str(project_root)))
    response = restarted.get("/ops/wrapper/status-card", params={"session_id": "release-status-card-user"})

    assert response.status_code == 200
    card = response.json()
    assert card["surface_id"] == "release-wrapper-status-card"
    assert card["status_label"] == "LOCKED CANON"
    assert card["product_surface"] == "wrapper"
    assert card["endpoint_refs"]["status_card"] == "/ops/wrapper/status-card"
    assert card["endpoint_refs"]["runtime"] == "/ops/wrapper/release-runtime"
    assert card["endpoint_refs"]["readiness"] == "/ops/wrapper/release-readiness"
    assert card["runtime"]["entrypoint"]["boot_target"] == "/ui/wrapper/"
    assert card["readiness"]["surface_id"] == "release-wrapper-readiness"
    assert card["readiness"]["passed_check_count"] >= 1
    assert card["ao_execution_receipts"]["latest_execution"]["raw_content_included"] is False
    assert card["dream_research_queue"]["replay"]["status"] == "replayed"
    assert card["dream_research_queue"]["latest_item"]["governance"]["proposal_status"] == "admin-approved"
    assert (
        card["autonomous_updates"]["latest_dream_research_proposal"]["latest_eval_replay"]["run_id"]
        == approval.json()["linked_eval_replay"]["run_id"]
    )
    assert card["autonomous_updates"]["latest_dream_research_proposal"]["operator_approved"] is True
    assert card["privacy_boundary"].endswith("no-raw-prompts-outputs-session-ids")
    assert "Load compact wrapper status card evidence" not in json.dumps(card)
    assert "release-status-card-user" not in json.dumps(card)

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "/ops/wrapper/status-card" in app_js
    assert "releaseWrapperStatus" in app_js
    assert "loadReleaseWrapperStatusCard" in app_js


def test_release_wrapper_status_card_exposes_admin_action_lane_for_control_panel(tmp_path: Path):
    project_root = make_project(tmp_path)
    sandbox_probe = project_root / "tests" / "release_wrapper_action_lane_probe_test.py"
    sandbox_probe.parent.mkdir(parents=True, exist_ok=True)
    sandbox_probe.write_text("def test_release_wrapper_action_lane_probe():\n    assert True\n", encoding="utf-8")
    client = TestClient(create_app(str(project_root)))

    client.post(
        "/v1/chat",
        json={
            "session_id": "release-action-lane-user",
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": "Expose release wrapper admin action lane."}],
        },
    )
    card = client.get("/ops/wrapper/status-card", params={"session_id": "release-action-lane-user"}).json()
    governance = card["dream_research_queue"]["latest_item"]["governance"]
    action_lane = card["operator_action_lane"]

    assert action_lane["surface_id"] == "release-wrapper-admin-action-lane"
    assert action_lane["proposal_update_id"] == governance["proposal_update_id"]
    assert action_lane["admin_approval_ref"] == governance["admin_approval_ref"]
    assert action_lane["sandbox_tests_ref"] == governance["sandbox_tests_ref"]
    assert action_lane["apply_ref"] == governance["apply_ref"]
    assert action_lane["rollback_ref"] == governance["rollback_ref"]
    assert action_lane["run_readiness_evidence_ref"] == "/ops/wrapper/release-readiness/run"
    assert action_lane["status_card_ref"] == "/ops/wrapper/status-card"
    assert action_lane["default_sandbox_command"].startswith("pytest tests/")
    assert action_lane["active_production_mutation_allowed"] is False
    assert action_lane["safe_file_scope"] == ["artifacts/autonomous-updates/safe-files"]

    approval = client.post(
        action_lane["admin_approval_ref"],
        json={"approved_by": "admin", "approval_ref": "operator-review::release-action-lane"},
    )
    assert approval.status_code == 200
    sandbox_run = client.post(
        action_lane["sandbox_tests_ref"],
        json={"command": "pytest tests/release_wrapper_action_lane_probe_test.py -q", "timeout_seconds": 30},
    )
    assert sandbox_run.status_code == 200
    assert sandbox_run.json()["status"] == "passed"
    applied = client.post(
        action_lane["apply_ref"],
        json={
            "test_refs": ["pytest tests/release_wrapper_action_lane_probe_test.py -q"],
            "test_evidence_refs": [sandbox_run.json()["evidence_ref"]],
        },
    )
    assert applied.status_code == 200
    rollback = client.post(action_lane["rollback_ref"], json={"reason": "release-wrapper-action-lane-test"})
    assert rollback.status_code == 200

    refreshed = client.get("/ops/wrapper/status-card", params={"session_id": "release-action-lane-user"}).json()
    statuses = refreshed["operator_action_lane"]["latest_action_statuses"]
    assert statuses["admin_approval"] == "admin-approved"
    assert statuses["sandbox_tests"] == "passed"
    assert statuses["apply"] == "applied-shadow-safe-file"
    assert statuses["rollback"] == "rolled-back"
    assert "Expose release wrapper admin action lane" not in json.dumps(refreshed)
    assert "release-action-lane-user" not in json.dumps(refreshed)

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "release-wrapper-admin-action-lane" in app_js
    assert "data-release-wrapper-action" in app_js
    assert "runReleaseWrapperAdminAction" in app_js
    assert "refreshReleaseWrapperStatusCard" in app_js
    assert "default_sandbox_command" in app_js
    assert "admin_approval_ref" in app_js
    assert "sandbox_tests_ref" in app_js
    assert "apply_ref" in app_js
    assert "rollback_ref" in app_js
    assert "run_readiness_evidence_ref" in app_js
    assert "run_release_readiness_evidence" in app_js


def test_wrapper_product_surface_uses_openai_compatible_chat_models_and_status_card(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    wrapper = client.get("/ui/wrapper/")
    models = client.get("/v1/models")

    assert wrapper.status_code == 200
    assert models.status_code == 200
    assert any(item["id"] == "nexusnet-offline" for item in models.json()["data"])
    html = wrapper.text
    assert "id=\"wrapperModelSelect\"" in html
    assert "id=\"wrapperSessionInput\"" in html
    assert "id=\"wrapperStatusCard\"" in html
    assert "id=\"wrapperChatLog\"" in html
    assert "id=\"wrapperComposer\"" in html
    assert "id=\"wrapperSend\"" in html
    assert "/v1/models" in html
    assert "/v1/chat/completions" in html
    assert "/ops/wrapper/status-card" in html
    assert "/ops/wrapper/release-runtime" in html
    assert "/ui/control-panel/" in html
    assert "release-wrapper-admin-action-lane" in html
    assert "release-runtime-summary" in html
    assert "wrapper-product-status-card" in html
    assert "live-wrapper-model-select" in html
    assert "operator_action_lane" in html
    assert "endpoint_refs" in html
    assert "runtime.continuous_assimilation" in html
    assert "runtime.federated_packet_count" in html
    assert "runtime.global_growth" in html
    assert "Forward Pass Coverage" in html
    assert "forward_pass_coverage" in html
    assert "Release Harness boot supervisor" in html
    assert "release-wrapper-boot-supervisor" in html
    assert "boot_supervisor" in html
    assert "boot_manifest" in html
    assert "Send Through Harness" in html
    assert "/chat\"" not in html

    response = client.post(
        "/v1/chat/completions",
        json={
            "session_id": "wrapper-product-surface-user",
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": "Wrapper product surface proof."}],
        },
    )
    assert response.status_code == 200
    assert response.json()["nexusnet"]["release_runtime_ref"] == "/ops/wrapper/release-runtime"
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": "wrapper-product-surface-user"})
    assert status_card.status_code == 200
    assert status_card.json()["surface_id"] == "release-wrapper-status-card"
    assert "Wrapper product surface proof" not in json.dumps(status_card.json())


def test_wrapper_product_surface_executes_admin_action_lane_from_ui_contract(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    wrapper = client.get("/ui/wrapper/")

    assert wrapper.status_code == 200
    html = wrapper.text
    assert "function performAdminAction" in html
    assert "latestOperatorActionLane" in html
    assert "latestSandboxEvidenceRef" in html
    assert 'data-admin-action="admin_approval"' in html
    assert 'data-admin-action="sandbox_tests"' in html
    assert 'data-admin-action="apply"' in html
    assert 'data-admin-action="rollback"' in html
    assert "admin_approval_ref" in html
    assert "sandbox_tests_ref" in html
    assert "apply_ref" in html
    assert "rollback_ref" in html
    assert "/ops/wrapper/release-readiness/run" in html
    assert "Run readiness evidence" in html
    assert "default_sandbox_command" in html
    assert "test_evidence_refs" in html
    assert "release-wrapper-ui" in html
    assert 'method: "POST"' in html
    assert 'document.addEventListener("click"' in html
    assert "await loadStatusCard()" in html


def test_release_runtime_surfaces_in_wrapper_and_visualizer_control_panel(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    client.post(
        "/chat",
        json={"session_id": "release-surface", "message": "Explain recursion briefly.", "rag": False},
    )

    wrapper = client.get("/ops/brain/wrapper-surface", params={"session_id": "release-surface"}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "release-surface"}).json()

    assert wrapper["release_runtime"]["surface_id"] == "release-wrapper-runtime"
    assert wrapper["release_runtime"]["federated_packet_count"] == 1
    assert wrapper["release_readiness"]["surface_id"] == "release-wrapper-readiness"
    assert wrapper["release_readiness"]["go_no_go"] == "no-go"
    assert wrapper["release_readiness"]["boot"]["readiness_ref"] == "/ops/wrapper/release-readiness"
    control_panel = visualizer["overlay_state"]["control_panel"]
    assert control_panel["release_wrapper_runtime"]["surface_id"] == "release-wrapper-runtime"
    assert control_panel["release_wrapper_readiness"]["surface_id"] == "release-wrapper-readiness"
    assert control_panel["release_wrapper_readiness"]["go_no_go"] == "no-go"
    assert (
        control_panel["release_wrapper_readiness"]["whole_system_boot_contract"]["surface_id"]
        == "whole-system-release-boot-contract"
    )
    assert control_panel["release_wrapper_readiness"]["whole_system_boot_contract"]["status"] == "blocked"
    assert control_panel["release_wrapper_readiness"]["whole_system_boot_contract"]["blocked_count"] == 1
    readiness_checks = {
        check["check_id"]: check
        for check in control_panel["release_wrapper_readiness"]["readiness_checks"]
    }
    nonblocking_degraded_checks = {
        check_id
        for check_id, check in readiness_checks.items()
        if check["status"] != "pass" and check.get("go_no_go_blocking") is False
    }
    blocking_degraded_checks = {
        check_id
        for check_id, check in readiness_checks.items()
        if check["status"] != "pass" and check.get("go_no_go_blocking") is not False
    }
    assert {
        "federated-packet-inbox",
        "peer-shadow-proposal",
        "whole-system-release-boot-contract",
    } <= blocking_degraded_checks
    assert nonblocking_degraded_checks >= {
        "release-health-heartbeat",
        "release-health-heartbeat-loop",
        "release-health-heartbeat-supervisor",
        "release-product-smoke",
        "domain-ao-routing",
        "domain-teacher-eval-handoff",
        "domain-expert-growth-admin-replay",
        "domain-expert-growth-sandbox-takeover-evidence",
    }
    assert readiness_checks["teacher-expert-birth-registry"]["status"] == "pass"
    assert readiness_checks["developmental-growth-promotion-governance"]["status"] == "pass"
    contract_gates = {
        gate["gate_id"]: gate
        for gate in control_panel["release_wrapper_readiness"]["whole_system_boot_contract"]["subsystem_gates"]
    }
    assert contract_gates["teacher-expert-birth-registry"]["status"] == "pass"
    assert contract_gates["developmental-growth-promotion-governance"]["status"] == "pass"
    assert contract_gates["authority-evidence-tool-governance"]["status"] == "pass"
    teacher_birth = control_panel["release_wrapper_readiness"]["evidence"]["teacher_expert_birth_registry"]
    assert teacher_birth["surface_id"] == "teacher-expert-birth-registry-release-gate"
    assert teacher_birth["teacher_registry"]["live_core_expert_pair_count"] == 19
    assert teacher_birth["expert_roster"]["core_expert_count"] == 19
    assert teacher_birth["birth_stack"]["birth_orchestrator_ref"] == "nexusnet.hive.net.birth_hive"
    assert teacher_birth["raw_content_included"] is False
    developmental_growth = control_panel["release_wrapper_readiness"]["evidence"]["developmental_growth_promotion"]
    assert developmental_growth["surface_id"] == "developmental-growth-promotion-release-gate"
    assert developmental_growth["status"] == "pass"
    assert developmental_growth["developmental_cortex"]["surface_id"] == "developmental-cortex-kernel"
    assert developmental_growth["developmental_cortex"]["assessment_count"] >= 1
    assert developmental_growth["growth_archive"]["surface_id"] == "growth-archive"
    assert developmental_growth["growth_archive"]["candidate_count"] >= 1
    assert developmental_growth["growth_engine"]["surface_id"] == "hive-model-growth-engine"
    assert developmental_growth["promotion_tribunal"]["surface_id"] == "promotion-tribunal"
    assert developmental_growth["promotion_service"]["surface_id"] == "promotion-service"
    assert developmental_growth["raw_content_included"] is False
    assert developmental_growth["active_production_mutation_allowed"] is False
    authority_governance = control_panel["release_wrapper_readiness"]["evidence"]["authority_evidence_tool_governance"]
    assert authority_governance["surface_id"] == "authority-evidence-tool-governance-release-gate"
    assert authority_governance["status"] == "pass"
    assert authority_governance["authority_spine"]["surface_id"] == "authority-integrity-spine"
    assert authority_governance["evidence_store"]["surface_id"] == "content-addressed-evidence-store"
    assert authority_governance["eval_federation"]["surface_id"] == "eval-federation"
    assert authority_governance["tool_action_harness"]["surface_id"] == "tool-action-harness"
    assert authority_governance["raw_content_included"] is False
    assert authority_governance["active_production_mutation_allowed"] is False
    assert control_panel["release_wrapper_runtime"]["honest_status_label"] == "live-wrapper-path-with-shadow-only-updates"
    assert control_panel["release_wrapper_runtime"]["context_window_posture"]["status"] == "measured-below-canon-minimum"
    assert control_panel["release_wrapper_runtime"]["context_capability_envelope"]["surface_id"] == "release-wrapper-context-capability-envelope"
    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    wrapper_html = (project_root / "ui" / "wrapper" / "index.html").read_text(encoding="utf-8")
    visualizer_js = (project_root / "ui" / "visualizer" / "app.js").read_text(encoding="utf-8")
    assert "Release Harness runtime" in app_js
    assert "context window posture" in app_js
    assert "context capability" in app_js
    assert "Release readiness" in app_js
    assert "release_wrapper_readiness" in app_js
    assert "release_wrapper_runtime" in app_js
    assert "Context Window Posture" in wrapper_html
    assert "Context Capability" in wrapper_html
    assert "Harness effective ctx tokens" in visualizer_js
    assert "Harness context cap" in visualizer_js


def test_visible_release_surfaces_use_harness_copy_without_renaming_legacy_routes(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    wrapper = client.get("/ui/wrapper/")

    assert wrapper.status_code == 200
    wrapper_html = wrapper.text
    control_panel_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    visualizer_js = (project_root / "ui" / "visualizer" / "app.js").read_text(encoding="utf-8")
    visualizer_html = (project_root / "ui" / "visualizer" / "index.html").read_text(encoding="utf-8")

    for expected in [
        "NexusNet Harness Surface",
        "Chat Through The Harness",
        "Harness navigation",
        "Harness runtime status",
        "Send Through Harness",
        "Ask through the release harness",
        "Loading harness status card",
        "Release Harness boot supervisor",
        "Harness Entrypoint",
        "Harness First Run",
    ]:
        assert expected in wrapper_html
    for stale in [
        "NexusNet Wrapper Surface",
        "Chat Through The Wrapper",
        "Wrapper navigation",
        "Wrapper runtime status",
        "Send Through Wrapper",
        "Ask through the release wrapper",
        "Loading wrapper status card",
        "Release wrapper boot supervisor",
        "Wrapper Entrypoint",
        "Wrapper First Run",
    ]:
        assert stale not in wrapper_html

    for expected in [
        "Release Harness runtime",
        "Release Harness boot supervisor",
        "Release Harness live telemetry",
        "Release Harness session lifecycle",
        "Release Harness self repair ledger",
        "Release Harness admin lane",
        "Release Harness status-card fallback",
        "Running Release Harness",
    ]:
        assert expected in control_panel_js
    for stale in [
        "Release wrapper boot supervisor",
        "Release wrapper live telemetry",
        "Release wrapper session lifecycle",
        "Release wrapper self repair ledger",
        "Release wrapper admin lane",
        "Release wrapper status-card fallback",
        "Running release wrapper",
    ]:
        assert stale not in control_panel_js

    for expected in [
        "Release Harness telemetry",
        "Harness forward coverage receipts",
        "Harness effective ctx tokens",
        "Harness context cap",
        "Harness developmental release contract",
        "Harness first-run readiness",
        "Harness release manifest rollup",
        "Harness developmental cortex",
        "Harness boot supervisor",
        "Harness product path",
        "Release Harness self repair actions",
        "Harness AO guard receipts",
        "Harness authority receipts",
        "Harness federated packets",
        "Wrapper packet outbox",
        "Wrapper packet inbox",
        "Harness growth captures",
    ]:
        assert expected in visualizer_js
    for stale in [
        "Release wrapper telemetry",
        "Wrapper forward coverage receipts",
        "Wrapper effective ctx tokens",
        "Wrapper context cap",
        "Wrapper developmental release contract",
        "Wrapper first-run readiness",
        "Wrapper release manifest rollup",
        "Wrapper developmental cortex",
        "Wrapper boot supervisor",
        "Wrapper product path",
        "Release wrapper self repair actions",
        "Wrapper AO guard receipts",
        "Wrapper authority receipts",
        "Wrapper federated packets",
        "Harness packet outbox",
        "Harness packet inbox",
        "Wrapper growth captures",
    ]:
        assert stale not in visualizer_js

    assert "Return To Harness Surface" in visualizer_html
    assert "Return To Wrapper Surface" not in visualizer_html

    for legacy_contract in [
        "/ops/wrapper/status-card",
        "/ops/wrapper/release-runtime",
        "/ops/wrapper/session-lifecycle",
    ]:
        assert legacy_contract in wrapper_html
    assert "/ops/wrapper/status-card" in control_panel_js
    assert "/ops/wrapper/session-lifecycle" in control_panel_js
    assert "release_wrapper_runtime" in control_panel_js
    assert "release_wrapper_runtime" in visualizer_js


def test_cluster9_teacher_reconciliation_and_harness_aliases_reach_release_surfaces(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    session_id = "cluster9-harness-surface"

    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    wrapper = client.get("/ops/brain/wrapper-surface", params={"session_id": session_id}).json()

    cluster9 = runtime["cluster9_teacher_reconciliation"]
    assert cluster9["surface_id"] == "cluster9-teacher-expert-reconciliation"
    assert cluster9["node_count"] >= 30
    assert cluster9["pairing_gap_count"] == 0
    assert cluster9["birth_blocking_issue_count"] == 0
    assert cluster9["mother_brain_authority"] == "NexusBrain"
    assert cluster9["raw_content_included"] is False
    assert cluster9["active_production_mutation_allowed"] is False
    assert cluster9["live_problem_temporary_experts"]["shadow_only"] is True

    harness = runtime["release_harness"]
    assert harness["surface_id"] == "release-harness-runtime"
    assert harness["legacy_surface_id"] == "release-wrapper-runtime"
    assert harness["product_surface"] == "harness"
    assert harness["legacy_product_surface"] == "wrapper"
    assert harness["runtime_ref"] == "/ops/wrapper/release-runtime"
    assert harness["control_panel_ref"] == "/ui/control-panel/"

    assert status_card["product_surface"] == "wrapper"
    assert status_card["harness_product_surface"] == "harness"
    assert status_card["legacy_product_surface"] == "wrapper"
    assert status_card["runtime"]["release_harness"] == harness
    assert status_card["runtime"]["cluster9_teacher_reconciliation"] == cluster9
    assert status_card["cluster9_teacher_reconciliation"] == cluster9

    control_panel = visualizer["overlay_state"]["control_panel"]
    assert control_panel["release_harness_runtime"] == control_panel["release_wrapper_runtime"]
    assert control_panel["release_harness_runtime"]["release_harness"] == harness
    assert control_panel["cluster9_teacher_reconciliation"] == cluster9
    assert (
        control_panel["live_refs"]["cluster9_teacher_reconciliation"]
        == "overlay.control_panel.cluster9_teacher_reconciliation"
    )
    assert (
        control_panel["live_refs"]["release_harness_runtime"]
        == "overlay.control_panel.release_harness_runtime"
    )

    labels = {mode["mode_id"]: mode["label"] for mode in wrapper["state"]["modes"]}
    assert labels["standard-chat"] == "Standard Harness"
    assert labels["openclaw"] == "OpenClaw Harness"

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    index_html = (project_root / "ui" / "control-panel" / "index.html").read_text(encoding="utf-8")
    assert "Release Harness runtime" in app_js
    assert "Cluster 9 teacher reconciliation" in app_js
    assert "Release wrapper runtime" not in app_js
    assert ">Harness<" in index_html


def test_project_heartbeat_drives_release_runtime_readiness_status_and_control_panel(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    session_id = "project-heartbeat-release-surface"
    prompt = "Beat the whole NexusNet heart without leaking SECRET-RELEASE-PROJECT-HEARTBEAT."

    forward_pass = client.post(
        "/ops/brain/hive-substrate/forward-pass",
        json={
            "session_id": session_id,
            "task_id": "release-surface-project-heartbeat",
            "intent": prompt,
            "source_ref": "operator::release-surface-project-heartbeat",
            "requested_capabilities": [
                "runtime",
                "memory",
                "evaluation",
                "federation",
                "dreaming",
            ],
            "memory_refs": ["memory::canon"],
            "requested_actions": [
                {
                    "action_id": "inspect-release-project-heartbeat",
                    "action_type": "read",
                    "target_ref": "hive-heartbeat",
                }
            ],
            "max_loops": 2,
        },
    )

    assert forward_pass.status_code == 200
    heartbeat = forward_pass.json()["project_heartbeat"]

    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    readiness = client.get("/ops/wrapper/release-readiness", params={"session_id": session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    lifecycle = client.get("/ops/wrapper/session-lifecycle", params={"session_id": session_id}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]

    assert runtime["project_heartbeat"]["heartbeat_id"] == heartbeat["heartbeat_id"]
    assert runtime["project_heartbeat"]["surface_id"] == "nexusnet-project-heartbeat"
    assert runtime["project_heartbeat"]["status"] == "alive"
    assert runtime["project_heartbeat"]["raw_content_included"] is False
    assert runtime["project_heartbeat"]["active_production_mutation_allowed"] is False

    readiness_checks = {
        check["check_id"]: check
        for check in readiness["readiness_checks"]
    }
    assert readiness["evidence"]["project_heartbeat"]["heartbeat_id"] == heartbeat["heartbeat_id"]
    assert readiness_checks["project-heartbeat"]["status"] == "pass"
    assert "project-heartbeat" in {
        check_id
        for gate in readiness["whole_system_boot_contract"]["subsystem_gates"]
        if gate["gate_id"] == "native-hive-project-heartbeat"
        for check_id in gate["check_ids"]
    }

    assert status_card["project_heartbeat"]["heartbeat_id"] == heartbeat["heartbeat_id"]
    assert status_card["runtime"]["project_heartbeat"]["heartbeat_id"] == heartbeat["heartbeat_id"]
    assert lifecycle["project_heartbeat"]["heartbeat_id"] == heartbeat["heartbeat_id"]
    assert control_panel["project_heartbeat"]["heartbeat_id"] == heartbeat["heartbeat_id"]
    assert control_panel["release_wrapper_runtime"]["project_heartbeat"]["heartbeat_id"] == heartbeat["heartbeat_id"]
    assert control_panel["live_refs"]["project_heartbeat"] == "overlay.control_panel.project_heartbeat"

    serialized = json.dumps(
        {
            "runtime": runtime["project_heartbeat"],
            "readiness": readiness["evidence"]["project_heartbeat"],
            "status_card": status_card["project_heartbeat"],
            "lifecycle": lifecycle["project_heartbeat"],
            "control_panel": control_panel["project_heartbeat"],
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-RELEASE-PROJECT-HEARTBEAT" not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized


def test_project_heartbeat_records_sanitized_replay_history_after_restart(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    session_id = "project-heartbeat-replay-session"
    prompt = "Persist project heartbeat without leaking SECRET-PROJECT-HEARTBEAT-REPLAY."

    forward_pass = client.post(
        "/ops/brain/hive-substrate/forward-pass",
        json={
            "session_id": session_id,
            "task_id": "release-surface-project-heartbeat-replay",
            "intent": prompt,
            "source_ref": "operator::release-surface-project-heartbeat-replay",
            "requested_capabilities": [
                "runtime",
                "memory",
                "evaluation",
                "federation",
                "dreaming",
            ],
            "memory_refs": ["memory::canon"],
            "requested_actions": [
                {
                    "action_id": "inspect-release-project-heartbeat-replay",
                    "action_type": "read",
                    "target_ref": "hive-heartbeat",
                }
            ],
            "max_loops": 2,
        },
    )

    assert forward_pass.status_code == 200
    heartbeat = forward_pass.json()["project_heartbeat"]

    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    readiness = client.get("/ops/wrapper/release-readiness", params={"session_id": session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]

    replay = runtime["project_heartbeat_replay"]
    assert replay["schema_version"] == "nexusnet-release-wrapper-project-heartbeat-replay-v1"
    assert replay["surface_id"] == "release-wrapper-project-heartbeat-replay"
    assert replay["status"] == "recording-live"
    assert replay["latest_heartbeat_id"] == heartbeat["heartbeat_id"]
    assert replay["heartbeat_count"] == 1
    assert replay["artifact_ref"] == "release-wrapper-runtime/project-heartbeats.jsonl"
    assert replay["raw_content_included"] is False
    assert replay["active_production_mutation_allowed"] is False
    assert runtime["project_heartbeat"]["wrapper_replay_ref"] == replay["artifact_ref"]
    assert runtime["project_heartbeat"]["replay_ref"] == "hive-substrate/project-heartbeats/_index.jsonl"
    assert readiness["evidence"]["project_heartbeat_replay"]["latest_heartbeat_id"] == heartbeat["heartbeat_id"]
    assert status_card["project_heartbeat_replay"]["latest_heartbeat_id"] == heartbeat["heartbeat_id"]
    assert control_panel["release_wrapper_runtime"]["project_heartbeat_replay"]["latest_heartbeat_id"] == heartbeat[
        "heartbeat_id"
    ]

    history_path = project_root / "artifacts" / "release-wrapper-runtime" / "project-heartbeats.jsonl"
    assert history_path.exists()
    history_lines = [line for line in history_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(history_lines) == 1
    history_record = json.loads(history_lines[0])
    assert history_record["heartbeat_id"] == heartbeat["heartbeat_id"]
    assert history_record["session_ref_digest"] == runtime["session_ref_digest"]
    assert history_record["raw_content_included"] is False
    assert history_record["active_production_mutation_allowed"] is False
    assert history_record["active_production_mutated"] is False

    restarted = TestClient(create_app(str(project_root)))
    replayed_runtime = restarted.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    replayed_status = restarted.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    replayed_visualizer = restarted.get(
        "/ops/brain/visualizer/state",
        params={"session_id": session_id},
    ).json()

    assert replayed_runtime["project_heartbeat_replay"]["status"] == "replayed"
    assert replayed_runtime["project_heartbeat_replay"]["latest_heartbeat_id"] == heartbeat["heartbeat_id"]
    assert replayed_runtime["project_heartbeat"]["heartbeat_id"] == heartbeat["heartbeat_id"]
    assert replayed_runtime["project_heartbeat"]["runtime_state"] == "replayed-history"
    assert replayed_status["project_heartbeat_replay"]["latest_heartbeat_id"] == heartbeat["heartbeat_id"]
    assert (
        replayed_visualizer["overlay_state"]["control_panel"]["release_wrapper_runtime"]["project_heartbeat_replay"][
            "latest_heartbeat_id"
        ]
        == heartbeat["heartbeat_id"]
    )

    serialized = json.dumps(
        {
            "runtime": runtime["project_heartbeat_replay"],
            "readiness": readiness["evidence"]["project_heartbeat_replay"],
            "status_card": status_card["project_heartbeat_replay"],
            "control_panel": control_panel["release_wrapper_runtime"]["project_heartbeat_replay"],
            "history_record": history_record,
            "replayed": replayed_runtime["project_heartbeat_replay"],
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-PROJECT-HEARTBEAT-REPLAY" not in serialized
    assert session_id not in serialized
    assert str(project_root) not in serialized


def test_release_wrapper_live_telemetry_surfaces_in_control_panel_and_visualizer(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    prompt = "Live telemetry surface proof with marker SECRET-LIVE-TELEMETRY."

    chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": "release-live-telemetry-user",
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    assert chat.status_code == 200

    runtime = client.get(
        "/ops/wrapper/release-runtime",
        params={"session_id": "release-live-telemetry-user"},
    ).json()
    visualizer = client.get(
        "/ops/brain/visualizer/state",
        params={"session_id": "release-live-telemetry-user"},
    ).json()
    control_panel = visualizer["overlay_state"]["control_panel"]

    telemetry = runtime["live_wrapper_telemetry"]
    assert telemetry["surface_id"] == "release-wrapper-live-telemetry"
    assert telemetry["runtime_state"] == "live-bound"
    assert telemetry["event_count"] == 1
    assert telemetry["source"] == "release-wrapper-runtime-events"
    assert telemetry["continuous_assimilation"]["node_count"] >= 1
    assert telemetry["continuous_assimilation"]["capture_count"] >= 1
    assert telemetry["global_growth"]["global_captures"] >= 2
    assert telemetry["federation"]["packet_count"] == 1
    assert telemetry["federation"]["latest_packet_id"] == runtime["latest_federated_packet"]["packet_id"]
    assert telemetry["production_spine"]["packet_count"] == 1
    assert telemetry["forward_pass_coverage"]["surface_id"] == "release-wrapper-forward-pass-coverage"
    assert telemetry["forward_pass_coverage"]["receipt_count"] == 1
    assert telemetry["forward_pass_coverage"]["latest_status"] == "covered"
    assert telemetry["recent_events"][0]["raw_content_included"] is False
    assert telemetry["recent_events"][0]["federated_packet_id"] == runtime["latest_interaction"]["federated_packet_id"]
    assert telemetry["recent_events"][0]["knowledge_ref"].startswith("sha256:")
    assert telemetry["privacy_boundary"].endswith("no-raw-prompts-outputs-session-ids")

    visualizer_telemetry = control_panel["release_wrapper_telemetry"]
    assert visualizer_telemetry["surface_id"] == "release-wrapper-live-telemetry"
    assert visualizer_telemetry["event_count"] == 1
    assert visualizer_telemetry["federation"]["packet_count"] == 1
    assert visualizer_telemetry["global_growth"]["global_captures"] >= 2
    assert visualizer_telemetry["forward_pass_coverage"]["receipt_count"] == 1
    assert control_panel["release_wrapper_runtime"]["forward_pass_coverage"]["latest_status"] == "covered"
    assert control_panel["release_wrapper_runtime"]["live_wrapper_telemetry"]["event_count"] == 1
    assert control_panel["release_wrapper_runtime"]["live_wrapper_telemetry"]["recent_events"][0]["raw_content_included"] is False

    serialized = json.dumps(
        {
            "runtime_telemetry": telemetry,
            "control_panel_telemetry": visualizer_telemetry,
            "embedded_runtime_telemetry": control_panel["release_wrapper_runtime"]["live_wrapper_telemetry"],
            "embedded_runtime_coverage": control_panel["release_wrapper_runtime"]["forward_pass_coverage"],
        }
    )
    assert prompt not in serialized
    assert "release-live-telemetry-user" not in serialized
    assert "SECRET-LIVE-TELEMETRY" not in serialized

    control_panel_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    visualizer_js = (project_root / "ui" / "visualizer" / "app.js").read_text(encoding="utf-8")
    assert "Release Harness live telemetry" in control_panel_js
    assert "release-wrapper-live-telemetry" in control_panel_js
    assert "live_wrapper_telemetry" in control_panel_js
    assert "forward coverage" in control_panel_js
    assert "forward_pass_coverage" in control_panel_js
    assert "recent_events" in control_panel_js
    assert "Release Harness telemetry" in visualizer_js
    assert "Harness forward coverage receipts" in visualizer_js
    assert "live_wrapper_telemetry" in visualizer_js
    assert "release-wrapper-live-telemetry" in visualizer_js


def test_release_wrapper_first_run_readiness_is_sanitized_product_manifest_template(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    session_id = "release-first-run-user"
    prompt = "First-run readiness must not leak SECRET-FIRST-RUN."

    chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    assert chat.status_code == 200

    readiness_response = client.get("/ops/wrapper/first-run-readiness", params={"session_id": session_id})
    assert readiness_response.status_code == 200
    readiness = readiness_response.json()
    template = readiness["request_template"]
    request = template["template"]

    assert readiness["surface_id"] == "release-wrapper-first-run-readiness"
    assert readiness["product_surface"] == "wrapper"
    assert readiness["runtime_state"] == "live-bound"
    assert readiness["endpoint_refs"]["first_run_readiness"] == "/ops/wrapper/first-run-readiness"
    assert readiness["endpoint_refs"]["first_run_readiness_run"] == "/ops/wrapper/first-run-readiness/run"
    assert readiness["entrypoint"]["wrapper_ui_ref"] == "/ui/wrapper/"
    assert readiness["entrypoint"]["legacy_first_run_ui_ref"] == "/ui/first_run.html"
    assert readiness["gates"]["wrapper_entrypoint_ready"] is True
    assert readiness["gates"]["provider_pool_visible"] is True
    assert readiness["gates"]["local_provider_usable"] is True
    assert readiness["gates"]["live_interaction_seen"] is True
    assert readiness["gates"]["continuous_assimilation_ready"] is True
    assert readiness["gates"]["global_growth_ready"] is True
    assert readiness["gates"]["federated_packet_ready"] is True
    assert readiness["gates"]["release_readiness_visible"] is True
    assert readiness["gates"]["operator_approved"] is False
    assert readiness["decision"] == "blocked-first-run-proofs-missing"
    assert "operator_approved" in readiness["missing_proof_fields"]
    assert template["endpoint"] == "/ops/brain/production-spine/first-run-readiness"
    assert request["cycle_id"].startswith("release-wrapper-first-run::")
    assert request["readiness_id"].startswith("first-run:release-wrapper::")
    assert request["student_id"] == "release-wrapper"
    assert request["target_node_ref"].startswith("expert.")
    assert request["local_cache_controls_ready"] is True
    assert request["model_download_manager_ready"] is True
    assert request["buyer_launcher_ready"] is True
    assert request["buyer_safe_defaults"] is True
    assert request["support_bundle_ready"] is False
    assert request["project_local_signing_key_ready"] is False
    assert request["operator_approved"] is False
    assert request["include_raw_private_data"] is False
    assert request["workspace_paths_redacted"] is True
    assert request["redact_secrets"] is True
    assert readiness["raw_content_included"] is False
    assert readiness["active_production_mutation_allowed"] is False

    run_response = client.post(
        "/ops/wrapper/first-run-readiness/run",
        json={"session_id": session_id},
    )
    assert run_response.status_code == 200
    run = run_response.json()
    manifest = run["manifest"]
    assert run["surface_id"] == "release-wrapper-first-run-readiness-run"
    assert run["status"] == "manifest-preview-recorded"
    assert run["raw_content_included"] is False
    assert run["active_production_mutation_allowed"] is False
    assert manifest["schema_version"] == "first_run_readiness_manifest_preview.v0.1"
    assert manifest["decision"] == "blocked"
    assert manifest["installer_mutation_allowed"] is False
    assert manifest["cache_mutation_allowed"] is False
    assert manifest["readiness_bundle_created"] is False
    assert "operator_approved" in manifest["readiness_blockers"]

    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]

    assert runtime["first_run_readiness"]["surface_id"] == "release-wrapper-first-run-readiness"
    assert runtime["first_run_readiness"]["latest_run"]["status"] == "manifest-preview-recorded"
    assert status_card["first_run_readiness"]["latest_run"]["manifest"]["decision"] == "blocked"
    assert status_card["endpoint_refs"]["first_run_readiness"] == "/ops/wrapper/first-run-readiness"
    assert control_panel["release_wrapper_runtime"]["first_run_readiness"]["latest_run"]["status"] == "manifest-preview-recorded"

    wrapper_html = (project_root / "ui" / "wrapper" / "index.html").read_text(encoding="utf-8")
    control_panel_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    visualizer_js = (project_root / "ui" / "visualizer" / "app.js").read_text(encoding="utf-8")
    assert "First Run Readiness" in wrapper_html
    assert "first-run readiness" in control_panel_js
    assert "Wrapper first-run readiness" in visualizer_js

    serialized = json.dumps(
        {
            "readiness": readiness,
            "run": run,
            "runtime_first_run_readiness": runtime["first_run_readiness"],
            "status_card_first_run_readiness": status_card["first_run_readiness"],
            "control_panel_first_run_readiness": control_panel["release_wrapper_runtime"]["first_run_readiness"],
        }
    )
    assert prompt not in serialized
    assert "SECRET-FIRST-RUN" not in serialized
    assert session_id not in serialized


def test_release_wrapper_first_run_readiness_uses_whole_system_production_spine_proofs(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    session_id = "release-first-run-system-user"
    seed_hex = "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60"
    passphrase = "system-first-run-passphrase"
    prompt = "Whole-system first-run gate must not leak SECRET-SYSTEM-FIRST-RUN."

    signing_key = client.post(
        "/ops/brain/production-spine/signing-keys/project-local",
        json={"key_id": "artifact_signing_key", "seed_hex": seed_hex, "passphrase": passphrase},
    )
    assert signing_key.status_code == 200
    assert signing_key.json()["status"] == "created"

    lifecycle = client.post(
        "/ops/brain/production-spine/growth-lifecycles",
        json={
            "lifecycle_id": "lifecycle:wrapper_system_first_run",
            "cycle_id": "cycle:wrapper_system_first_run",
            "target_node_ref": "node:expert_coder",
            "student_id": "student:system_first_run",
            "student_kind": "child_expert",
            "capabilities": ["multi_file_patch", "test_repair"],
            "operator_approved": True,
            "human_approved": False,
            "teacher_outputs": [
                {"teacher_ref": "teacher:qwen3-coder-next", "license_state": "approved_train", "score": 0.88, "output_ref": "out:qwen"},
                {"teacher_ref": "node:expert_critique", "license_state": "internal", "score": 0.91, "output_ref": "out:critique"},
            ],
            "validator_results": [{"validator_ref": "validator:unit_tests", "passed": True, "score": 1.0}],
            "training_dataset": [
                {"x": 0.0, "y": 1.0},
                {"x": 1.0, "y": 3.0},
                {"x": 2.0, "y": 5.0},
            ],
            "shadow_input": {"x": 4.0},
            "route_features": {"coding": 0.8, "reasoning": 0.5, "risk": 0.2},
            "route_candidates": [
                {"node_ref": "node:expert_coder", "weights": {"coding": 0.7, "reasoning": 0.1, "risk": -0.2}},
                {"node_ref": "student:system_first_run", "weights": {"coding": 0.6, "reasoning": 0.5, "risk": -0.1}},
            ],
            "hidden_eval_cases": [
                {"x": 4.0, "y": 9.0, "parent_prediction": 7.5, "teacher_prediction": 8.0},
                {"x": 5.0, "y": 11.0, "parent_prediction": 9.0, "teacher_prediction": 10.0},
            ],
            "hidden_eval_attestation": {
                "sealed": True,
                "visible_to_training": False,
                "visible_to_teacher_council": False,
                "leakage_scan": {"status": "passed", "train_overlap": 0, "teacher_output_overlap": 0},
            },
            "federation": {
                "consent_granted": True,
                "local_metrics": {"success_rate": 0.84, "failure_rate": 0.05, "latency_ms": 120.0, "sample_count": 50},
            },
            "runtime_benchmarks": [
                {"method": "q4_k_m", "backend": "llama.cpp", "tokens_per_second": 45.0, "memory_gb": 4.8, "quality_score": 0.91}
            ],
            "signing_key_file": signing_key.json()["key_file_path"],
            "signing_key_passphrase": passphrase,
            "productization_readiness": {
                "local_cache_controls": True,
                "secret_scan_passed": True,
                "model_download_manager": True,
                "support_bundle": True,
                "crash_diagnostics": True,
                "ci_packaging": False,
                "buyer_launcher": True,
                "docs_complete": True,
                "buyer_safe_defaults": True,
                "runtime_gates_clear": False,
                "artifact_signing_ready": True,
                "artifact_trust_clear": False,
                "adapter_artifact_trust_clear": False,
            },
            "raw_private_data": "SECRET-SYSTEM-FIRST-RUN private text",
        },
    )
    assert lifecycle.status_code == 200

    chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    assert chat.status_code == 200

    production_scorecard = client.get("/ops/brain/canon/production-spine").json()
    production_template = production_scorecard["first_run_readiness_request_template"]
    readiness = client.get("/ops/wrapper/first-run-readiness", params={"session_id": session_id}).json()
    wrapper_template = readiness["request_template"]
    request = wrapper_template["template"]

    assert production_template["template"]["cycle_id"] == "cycle:wrapper_system_first_run"
    assert production_template["template"]["student_id"] == "student:system_first_run"
    assert production_template["template"]["support_bundle_ready"] is True
    assert production_template["template"]["crash_diagnostics_ready"] is True
    assert production_template["template"]["project_local_signing_key_ready"] is True

    assert readiness["product_scope"] == "whole-system"
    assert readiness["production_spine"]["cycle_id"] == "cycle:wrapper_system_first_run"
    assert readiness["production_spine"]["student_id"] == "student:system_first_run"
    assert readiness["production_spine"]["runtime_state"] in {"live-bound", "degraded"}
    assert wrapper_template["source"] == "production-spine-scorecard-first-run-template"
    assert request["cycle_id"] == "cycle:wrapper_system_first_run"
    assert request["readiness_id"] == "first-run:cycle:wrapper_system_first_run"
    assert request["student_id"] == "student:system_first_run"
    assert request["target_node_ref"] == "node:expert_coder"
    assert request["local_cache_controls_ready"] is True
    assert request["model_download_manager_ready"] is True
    assert request["buyer_launcher_ready"] is True
    assert request["buyer_safe_defaults"] is True
    assert request["support_bundle_ready"] is True
    assert request["crash_diagnostics_ready"] is True
    assert request["project_local_signing_key_ready"] is True
    assert request["key_file_path"].endswith("artifact_signing_key.enc.json")
    assert request["adapter_artifact_trust_status"] in {"not_recorded", "quarantined", "trusted"}
    assert request["adapter_artifact_trust_clear"] is False
    assert readiness["gates"]["support_bundle_ready"] is True
    assert readiness["gates"]["crash_diagnostics_ready"] is True
    assert readiness["gates"]["project_local_signing_key_ready"] is True
    assert "support_bundle_ready" not in readiness["missing_proof_fields"]
    assert "crash_diagnostics_ready" not in readiness["missing_proof_fields"]
    assert "project_local_signing_key_ready" not in readiness["missing_proof_fields"]
    assert "adapter_artifact_trust_clear" in readiness["missing_proof_fields"]
    assert "operator_approved" in readiness["missing_proof_fields"]
    assert readiness["decision"] == "blocked-first-run-proofs-missing"

    run = client.post(
        "/ops/wrapper/first-run-readiness/run",
        json={"session_id": session_id},
    ).json()
    manifest = run["manifest"]
    assert manifest["cycle_id"] == "cycle:wrapper_system_first_run"
    assert manifest["student_id"] == "student:system_first_run"
    assert manifest["support_bundle_ready"] is True
    assert manifest["crash_diagnostics_ready"] is True
    assert manifest["project_local_signing_key_ready"] is True
    assert "adapter_artifact_trust_clear" in manifest["readiness_blockers"]
    assert "operator_approved" in manifest["readiness_blockers"]

    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]
    assert runtime["first_run_readiness"]["product_scope"] == "whole-system"
    assert runtime["first_run_readiness"]["production_spine"]["cycle_id"] == "cycle:wrapper_system_first_run"
    assert control_panel["release_wrapper_runtime"]["first_run_readiness"]["product_scope"] == "whole-system"
    assert control_panel["release_wrapper_runtime"]["first_run_readiness"]["production_spine"]["student_id"] == "student:system_first_run"

    wrapper_html = (project_root / "ui" / "wrapper" / "index.html").read_text(encoding="utf-8")
    control_panel_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    visualizer_js = (project_root / "ui" / "visualizer" / "app.js").read_text(encoding="utf-8")
    assert "Whole-System First Run" in wrapper_html
    assert "whole-system first-run" in control_panel_js
    assert "Whole-system first-run scope" in visualizer_js

    serialized = json.dumps({"readiness": readiness, "run": run})
    assert prompt not in serialized
    assert "SECRET-SYSTEM-FIRST-RUN" not in serialized
    assert session_id not in serialized
    assert seed_hex not in serialized
    assert passphrase not in serialized


def test_release_wrapper_surfaces_production_release_manifest_rollup_in_status_surfaces(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    session_id = "release-manifest-rollup-user"
    passphrase = "project-local-wrapper-rollup-passphrase"

    lifecycle = client.post("/ops/brain/production-spine/growth-lifecycles", json=lifecycle_request())
    assert lifecycle.status_code == 200

    scorecard = client.get("/ops/brain/canon/production-spine").json()
    key_template = scorecard["project_local_signing_key_request_template"]["template"]
    key_created = client.post(
        "/ops/brain/production-spine/signing-keys/project-local",
        json={
            "key_id": key_template["key_id"],
            "key_file_path": key_template["key_file_path"],
            "passphrase": passphrase,
            "seed_hex": "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60",
        },
    )
    assert key_created.status_code == 200

    signed_request = client.get("/ops/brain/canon/production-spine").json()[
        "signed_deep_replay_handoff_request_template"
    ]["template"]
    signed_request["signing_key_passphrase"] = passphrase
    signed_replay = client.post("/ops/brain/production-spine/deep-replay", json=signed_request)
    assert signed_replay.status_code == 200

    signed_rescan_template = client.get("/ops/brain/canon/production-spine").json()[
        "signed_replay_artifact_trust_rescan_request_template"
    ]
    rescan = client.post(
        "/ops/brain/production-spine/signed-replay-artifact-trust-rescans",
        json=signed_rescan_template["template"],
    )
    assert rescan.status_code == 200
    assert rescan.json()["adapter_artifact_trust_clear"] is True

    reviewer_request = client.get("/ops/brain/canon/production-spine").json()["reviewer_window_request_template"][
        "template"
    ]
    reviewer_request.update(
        {
            "advancement_id": "reviewer-window:wrapper_rollup_all_windows",
            "window": "post_promotion",
            "window_status": "passed",
            "passed_windows": ["initial_eval", "shadow_runtime", "canary"],
            "lower_confidence_surpass_bound": 0.08,
            "required_lower_confidence_margin": 0.01,
            "teacher_ejection_review_requested": True,
            "parent_retirement_review_requested": True,
            "human_approved": True,
            "governance_approved": True,
        }
    )
    reviewer = client.post("/ops/brain/production-spine/reviewer-windows", json=reviewer_request)
    assert reviewer.status_code == 200

    productization_request = client.get("/ops/brain/canon/production-spine").json()[
        "productization_readiness_request_template"
    ]["template"]
    for gate in (
        "local_cache_controls",
        "secret_scan_passed",
        "model_download_manager",
        "support_bundle",
        "crash_diagnostics",
        "ci_packaging",
        "buyer_launcher",
        "docs_complete",
        "buyer_safe_defaults",
        "runtime_gates_clear",
        "artifact_signing_ready",
        "artifact_trust_clear",
        "adapter_artifact_trust_clear",
    ):
        productization_request[gate] = True
    productization = client.post(
        "/ops/brain/production-spine/productization-readiness",
        json=productization_request,
    )
    assert productization.status_code == 200
    assert productization.json()["release_ready"] is True

    after_productization = client.get("/ops/brain/canon/production-spine").json()
    support_request = after_productization["production_support_bundle_export_request_template"]["template"]
    support_request["support_bundle_destination"] = str(tmp_path / "operator-exports" / "support_bundle.zip")
    support = client.post("/ops/brain/production-spine/support-bundles", json=support_request)
    assert support.status_code == 200
    assert support.json()["zip_created"] is True

    first_run_request = client.get("/ops/brain/canon/production-spine").json()["first_run_readiness_request_template"][
        "template"
    ]
    first_run_request["operator_approved"] = True
    first_run = client.post("/ops/brain/production-spine/first-run-readiness", json=first_run_request)
    assert first_run.status_code == 200
    assert first_run.json()["decision"] == "ready"

    diagnostics_request = client.get("/ops/brain/canon/production-spine").json()[
        "crash_diagnostics_export_request_template"
    ]["template"]
    diagnostics_request["diagnostics_destination"] = str(tmp_path / "operator-exports" / "crash_diagnostics.json")
    diagnostics = client.post("/ops/brain/production-spine/crash-diagnostics", json=diagnostics_request)
    assert diagnostics.status_code == 200
    assert diagnostics.json()["logs_packaged"] is True

    release_request = client.get("/ops/brain/canon/production-spine").json()["release_packaging_handoff_request_template"][
        "template"
    ]
    release_request["release_destination"] = str(tmp_path / "operator-exports" / "release_package.zip")
    release_package = client.post("/ops/brain/production-spine/release-packages", json=release_request)
    assert release_package.status_code == 200
    assert release_package.json()["package_created"] is True

    go_no_go_request = client.get("/ops/brain/canon/production-spine").json()["release_go_no_go_review_request_template"][
        "template"
    ]
    go_no_go_request.update(
        {
            "operator_approved": True,
            "human_approved": True,
            "buyer_release_allowed": True,
        }
    )
    go_no_go = client.post("/ops/brain/production-spine/release-go-no-go", json=go_no_go_request)
    assert go_no_go.status_code == 200
    assert go_no_go.json()["decision"] == "approved"
    assert go_no_go.json()["release_mutation_allowed"] is False

    production_rollup = client.get("/ops/brain/canon/production-spine").json()["release_manifest_status_rollup"]
    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    readiness = client.get("/ops/wrapper/release-readiness", params={"session_id": session_id}).json()
    lifecycle = client.get("/ops/wrapper/session-lifecycle", params={"session_id": session_id}).json()
    wrapper_surface = client.get("/ops/brain/wrapper-surface", params={"session_id": session_id}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]
    readiness_checks = {check["check_id"]: check for check in readiness["readiness_checks"]}
    lifecycle_steps = {step["step_id"]: step for step in lifecycle["lifecycle_steps"]}

    assert production_rollup["status"] == "approved"
    assert runtime["release_manifest_status_rollup"]["status"] == "approved"
    assert runtime["release_manifest_status_rollup"]["release_mutation_allowed"] is False
    assert runtime["release_manifest_status_rollup"]["mutation_boundary"] == "release-status-rollup-read-only-no-release-mutation"
    assert runtime["release_manifest_status_rollup"]["control_panel_label"] == "Release go/no-go approved"
    assert readiness["evidence"]["release_manifest_status_rollup"] == runtime["release_manifest_status_rollup"]
    assert readiness_checks["release-manifest-rollup"]["status"] == "pass"
    assert readiness_checks["release-manifest-rollup"]["evidence_refs"] == [
        "release_manifest_status::approved",
        "cycle::cycle:cyc_lifecycle_001",
        "lifecycle::lifecycle:coder_birth_001",
    ]
    assert lifecycle["release_manifest_status_rollup"] == runtime["release_manifest_status_rollup"]
    assert lifecycle_steps["release-manifest-rollup"]["status"] == "pass"
    assert lifecycle_steps["release-manifest-rollup"]["release_mutation_allowed"] is False
    assert status_card["release_manifest_status_rollup"] == runtime["release_manifest_status_rollup"]
    assert status_card["runtime"]["release_manifest_status_rollup"] == runtime["release_manifest_status_rollup"]
    assert wrapper_surface["release_runtime"]["release_manifest_status_rollup"] == runtime["release_manifest_status_rollup"]
    assert control_panel["release_wrapper_runtime"]["release_manifest_status_rollup"] == runtime[
        "release_manifest_status_rollup"
    ]
    assert control_panel["release_wrapper_session_lifecycle"]["release_manifest_status_rollup"] == runtime[
        "release_manifest_status_rollup"
    ]
    control_lifecycle_steps = {
        step["step_id"]: step for step in control_panel["release_wrapper_session_lifecycle"]["lifecycle_steps"]
    }
    assert control_lifecycle_steps["release-manifest-rollup"]["status"] == "pass"
    assert control_lifecycle_steps["release-manifest-rollup"]["release_mutation_allowed"] is False

    wrapper_html = (project_root / "ui" / "wrapper" / "index.html").read_text(encoding="utf-8")
    control_panel_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    visualizer_js = (project_root / "ui" / "visualizer" / "app.js").read_text(encoding="utf-8")
    assert "Release Manifest Rollup" in wrapper_html
    assert "release manifest rollup" in control_panel_js
    assert "release-manifest-rollup" in control_panel_js
    assert "active mutation blocked" in control_panel_js
    assert "Wrapper release manifest rollup" in visualizer_js
    assert "release-wrapper-release-manifest-rollup" in visualizer_js
    assert "active mutation blocked" in visualizer_js

    serialized = json.dumps(
        {
            "runtime": runtime["release_manifest_status_rollup"],
            "readiness": readiness["evidence"]["release_manifest_status_rollup"],
            "lifecycle": lifecycle["release_manifest_status_rollup"],
            "status_card": status_card["release_manifest_status_rollup"],
            "wrapper_surface": wrapper_surface["release_runtime"]["release_manifest_status_rollup"],
            "control_panel": control_panel["release_wrapper_runtime"]["release_manifest_status_rollup"],
            "control_panel_session_lifecycle": control_panel["release_wrapper_session_lifecycle"][
                "release_manifest_status_rollup"
            ],
        },
        sort_keys=True,
    )
    assert passphrase not in serialized
    assert session_id not in serialized
    assert str(tmp_path) not in serialized
    assert "operator-exports" not in serialized


def test_release_wrapper_runs_sanitized_production_spine_release_lifecycle(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    session_id = "production-spine-lifecycle-user"
    prompt = "Run the whole production spine lifecycle without leaking SECRET-PRODUCTION-SPINE."

    chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    assert chat.status_code == 200

    blocked_without_approval = client.post(
        "/ops/wrapper/production-spine-release-lifecycle/run",
        json={"session_id": session_id, "operator_approved": True, "human_approved": True},
    )
    assert blocked_without_approval.status_code == 400
    assert "admin approval" in blocked_without_approval.json()["detail"].lower()

    approval = client.post(
        "/ops/approvals",
        json={
            "subject": "release-wrapper-production-spine-release-lifecycle",
            "decision": "approved",
            "approver": "operator@example.invalid",
            "rationale": "Approve the whole-system shadow release lifecycle for this test.",
            "metadata": {
                "session_id": session_id,
                "raw_private_data": "SECRET-PRODUCTION-SPINE",
                "release_surface": "wrapper",
            },
        },
    )
    assert approval.status_code == 200
    approval_decision = approval.json()
    assert approval_decision["decision"] == "approved"

    run_response = client.post(
        "/ops/wrapper/production-spine-release-lifecycle/run",
        json={
            "session_id": session_id,
            "approval_decision_id": approval_decision["decision_id"],
            "operator_approved": True,
            "human_approved": True,
        },
    )
    assert run_response.status_code == 200
    run = run_response.json()
    step_ids = [step["step_id"] for step in run["steps"]]

    assert run["surface_id"] == "release-wrapper-production-spine-release-lifecycle-run"
    assert run["status"] == "approved-shadow-release-lifecycle"
    assert run["product_scope"] == "whole-system"
    assert run["raw_content_included"] is False
    assert run["active_production_mutation_allowed"] is False
    assert run["release_mutation_allowed"] is False
    assert run["admin_approval"]["status"] == "approved"
    assert run["admin_approval"]["approval_ref"] == approval_decision["decision_id"]
    assert run["admin_approval"]["raw_content_included"] is False
    assert run["admin_approval"]["active_production_mutation_allowed"] is False
    lifecycle_governance = run["authority_evidence_tool_governance"]
    assert lifecycle_governance["surface_id"] == "production-spine-release-lifecycle-governance-record"
    assert lifecycle_governance["status"] == "pass"
    assert lifecycle_governance["authority_status"] == "allowed-shadow"
    assert lifecycle_governance["authority_production_action_allowed"] is False
    assert lifecycle_governance["authority_rollback_available"] is True
    assert lifecycle_governance["evidence_record_id"].startswith("evidence::release-wrapper-production-spine-lifecycle-governance::")
    assert lifecycle_governance["evidence_content_hash"].startswith("sha256:")
    assert lifecycle_governance["eval_federation_status"] == "recorded"
    assert lifecycle_governance["eval_federation_promotion_allowed"] is True
    assert lifecycle_governance["tool_action_status"] == "planned-shadow"
    assert lifecycle_governance["tool_action_execution_allowed"] is False
    assert lifecycle_governance["raw_content_included"] is False
    assert lifecycle_governance["active_production_mutation_allowed"] is False
    assert f"approval::{approval_decision['decision_id']}" in lifecycle_governance["evidence_refs"]
    assert run["step_counts"]["blocked"] == 0
    assert step_ids == [
        "growth_lifecycle",
        "project_local_signing_key",
        "signed_deep_replay",
        "signed_replay_artifact_trust_rescan",
        "reviewer_window_advancement",
        "productization_readiness",
        "support_bundle_manifest",
        "first_run_readiness",
        "crash_diagnostics",
        "runtime_health_monitor",
        "release_package",
        "release_go_no_go",
    ]
    assert all(step["raw_content_included"] is False for step in run["steps"])
    assert all(step["active_production_mutation_allowed"] is False for step in run["steps"])
    assert all(
        digest.startswith("sha256:")
        for step in run["steps"]
        for digest in (step.get("artifact_path_digests") or {}).values()
        if digest
    )
    rollup = run["release_manifest_status_rollup"]
    assert rollup["status"] == "approved"
    assert rollup["buyer_release_allowed"] is True
    assert rollup["release_mutation_allowed"] is False
    assert all(ref.startswith("sha256:") for ref in rollup["latest_ref_digests"].values() if ref)

    lifecycle_surface = client.get(
        "/ops/wrapper/production-spine-release-lifecycle",
        params={"session_id": session_id},
    )
    assert lifecycle_surface.status_code == 200
    lifecycle_summary = lifecycle_surface.json()
    assert lifecycle_summary["latest_run"]["run_id"] == run["run_id"]
    assert lifecycle_summary["latest_run"]["status"] == "approved-shadow-release-lifecycle"
    assert lifecycle_summary["admin_approval"]["approval_ref"] == approval_decision["decision_id"]

    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    readiness = client.get("/ops/wrapper/release-readiness", params={"session_id": session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    lifecycle = client.get("/ops/wrapper/session-lifecycle", params={"session_id": session_id}).json()
    wrapper_surface = client.get("/ops/brain/wrapper-surface", params={"session_id": session_id}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]
    readiness_checks = {check["check_id"]: check for check in readiness["readiness_checks"]}
    lifecycle_steps = {step["step_id"]: step for step in lifecycle["lifecycle_steps"]}

    runtime_lifecycle = runtime["production_spine_release_lifecycle"]
    assert runtime_lifecycle["latest_run"]["run_id"] == run["run_id"]
    assert status_card["production_spine_release_lifecycle"]["latest_run"]["run_id"] == run["run_id"]
    assert wrapper_surface["release_runtime"]["production_spine_release_lifecycle"]["latest_run"]["run_id"] == run["run_id"]
    assert control_panel["release_wrapper_runtime"]["production_spine_release_lifecycle"]["latest_run"]["run_id"] == run["run_id"]
    assert readiness["evidence"]["production_spine_release_lifecycle"]["latest_run"]["run_id"] == run["run_id"]
    assert readiness_checks["production-spine-release-lifecycle"]["status"] == "pass"
    assert readiness_checks["production-spine-release-lifecycle"]["admin_approval_status"] == "approved"
    assert readiness_checks["production-spine-release-lifecycle"]["governance_status"] == "pass"
    assert readiness_checks["production-spine-release-lifecycle"]["authority_decision_id"] == lifecycle_governance["authority_decision_id"]
    assert lifecycle_steps["production-spine-release-lifecycle"]["status"] == "pass"
    assert lifecycle["production_spine_release_lifecycle"]["latest_run"]["status"] == "approved-shadow-release-lifecycle"

    wrapper_html = (project_root / "ui" / "wrapper" / "index.html").read_text(encoding="utf-8")
    control_panel_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    visualizer_js = (project_root / "ui" / "visualizer" / "app.js").read_text(encoding="utf-8")
    assert "Production Spine Lifecycle" in wrapper_html
    assert "approval" in wrapper_html
    assert "governance" in wrapper_html
    assert "production-spine-release-lifecycle" in control_panel_js
    assert "production spine lifecycle approval" in control_panel_js
    assert "production spine lifecycle governance" in control_panel_js
    assert "production-spine-release-lifecycle" in visualizer_js
    assert "production spine lifecycle approval" in visualizer_js
    assert "production spine lifecycle governance" in visualizer_js

    serialized = json.dumps(
        {
            "run": run,
            "summary": lifecycle_summary,
            "runtime": runtime_lifecycle,
            "readiness": readiness["evidence"]["production_spine_release_lifecycle"],
            "status_card": status_card["production_spine_release_lifecycle"],
            "session_lifecycle": lifecycle["production_spine_release_lifecycle"],
            "wrapper_surface": wrapper_surface["release_runtime"]["production_spine_release_lifecycle"],
            "control_panel": control_panel["release_wrapper_runtime"]["production_spine_release_lifecycle"],
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-PRODUCTION-SPINE" not in serialized
    assert "operator@example.invalid" not in serialized
    assert "Approve the whole-system shadow release lifecycle for this test." not in serialized
    assert session_id not in serialized
    assert str(tmp_path) not in serialized


def test_production_spine_lifecycle_uses_absolute_signing_paths_for_relative_project_root(tmp_path: Path):
    project_root = make_project(tmp_path)
    relative_project_root = Path(os.path.relpath(project_root, Path.cwd()))
    client = TestClient(create_app(str(relative_project_root)))
    session_id = "relative-root-production-spine-user"

    chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": "Exercise production spine signing from a relative root."}],
        },
    )
    assert chat.status_code == 200

    approval = client.post(
        "/ops/approvals",
        json={
            "subject": "release-wrapper-production-spine-release-lifecycle",
            "decision": "approved",
            "approver": "relative-root-operator@example.invalid",
            "rationale": "Approve relative-root shadow lifecycle.",
            "metadata": {"session_id": session_id},
        },
    )
    assert approval.status_code == 200

    run_response = client.post(
        "/ops/wrapper/production-spine-release-lifecycle/run",
        json={
            "session_id": session_id,
            "approval_decision_id": approval.json()["decision_id"],
            "operator_approved": True,
            "human_approved": True,
        },
    )
    assert run_response.status_code == 200
    run = run_response.json()
    trust_step = next(step for step in run["steps"] if step["step_id"] == "signed_replay_artifact_trust_rescan")

    assert run["status"] == "approved-shadow-release-lifecycle"
    assert run["step_counts"]["blocked"] == 0
    assert trust_step["status"] == "pass"
    assert client.app.state.services.brain_production_spine.root.is_absolute()

    signed_indices = sorted(client.app.state.services.brain_production_spine.root.rglob("*_signed/artifact_index.jsonl"))
    assert signed_indices
    signed_records = [
        json.loads(line)
        for line in signed_indices[-1].read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert signed_records
    assert {record.get("signature_state") for record in signed_records} == {"signed_ed25519"}


def test_release_wrapper_rolls_back_production_spine_lifecycle_artifacts_safely(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    session_id = "production-spine-lifecycle-rollback-user"
    prompt = "Rollback the production spine lifecycle without leaking SECRET-ROLLBACK-SPINE."

    chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    assert chat.status_code == 200

    approval = client.post(
        "/ops/approvals",
        json={
            "subject": "release-wrapper-production-spine-release-lifecycle",
            "decision": "approved",
            "approver": "rollback-operator@example.invalid",
            "rationale": "Approve lifecycle rollback test.",
            "metadata": {
                "session_id": session_id,
                "raw_private_data": "SECRET-ROLLBACK-SPINE",
                "release_surface": "wrapper",
            },
        },
    )
    assert approval.status_code == 200
    approval_decision = approval.json()

    run_response = client.post(
        "/ops/wrapper/production-spine-release-lifecycle/run",
        json={
            "session_id": session_id,
            "approval_decision_id": approval_decision["decision_id"],
            "operator_approved": True,
            "human_approved": True,
        },
    )
    assert run_response.status_code == 200
    run = run_response.json()
    assert run["status"] == "approved-shadow-release-lifecycle"

    lifecycle_artifact_root = client.app.state.release_wrapper_runtime.runtime_dir / "ps-release-lifecycle"
    rollback_quarantine_root = client.app.state.release_wrapper_runtime.runtime_dir / "ps-release-lifecycle-rollbacks"
    assert lifecycle_artifact_root.exists()
    assert any(lifecycle_artifact_root.iterdir())

    rollback_response = client.post(
        f"/ops/wrapper/production-spine-release-lifecycle/{run['run_id']}/rollback",
        json={"reason": "release-wrapper-lifecycle-rollback-test"},
    )
    assert rollback_response.status_code == 200
    rollback = rollback_response.json()

    assert rollback["surface_id"] == "release-wrapper-production-spine-release-lifecycle-rollback"
    assert rollback["status"] == "rolled-back"
    assert rollback["run_id"] == run["run_id"]
    assert rollback["rollback_restored"] is True
    assert rollback["active_production_mutated"] is False
    assert rollback["release_mutation_allowed"] is False
    assert rollback["raw_content_included"] is False
    assert rollback["artifact_cleanup"]["status"] == "quarantined"
    assert rollback["artifact_cleanup"]["source_ref_digest"].startswith("sha256:")
    assert rollback["artifact_cleanup"]["quarantine_ref_digest"].startswith("sha256:")
    assert rollback["artifact_cleanup"]["entry_count"] >= 1
    assert rollback["artifact_cleanup"]["file_count"] >= 0
    assert rollback["artifact_cleanup"]["active_production_mutated"] is False
    assert rollback["authority_evidence_tool_governance"]["status"] == "pass"
    assert rollback["authority_evidence_tool_governance"]["authority_status"] == "allowed-shadow"
    assert rollback["authority_evidence_tool_governance"]["tool_action_status"] == "planned-shadow"
    assert rollback["authority_evidence_tool_governance"]["tool_action_execution_allowed"] is False
    assert rollback["authority_evidence_tool_governance"]["raw_content_included"] is False
    assert rollback_quarantine_root.exists()
    assert any(rollback_quarantine_root.iterdir())

    lifecycle_summary = client.get(
        "/ops/wrapper/production-spine-release-lifecycle",
        params={"session_id": session_id},
    ).json()
    readiness = client.get("/ops/wrapper/release-readiness", params={"session_id": session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    session_lifecycle = client.get("/ops/wrapper/session-lifecycle", params={"session_id": session_id}).json()
    wrapper_surface = client.get("/ops/brain/wrapper-surface", params={"session_id": session_id}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]
    readiness_checks = {check["check_id"]: check for check in readiness["readiness_checks"]}

    assert lifecycle_summary["latest_rollback"]["rollback_id"] == rollback["rollback_id"]
    assert lifecycle_summary["latest_rollback"]["status"] == "rolled-back"
    assert readiness["evidence"]["production_spine_release_lifecycle"]["latest_rollback"]["rollback_id"] == rollback["rollback_id"]
    assert readiness_checks["production-spine-release-lifecycle"]["rollback_status"] == "rolled-back"
    assert status_card["production_spine_release_lifecycle"]["latest_rollback"]["rollback_id"] == rollback["rollback_id"]
    assert session_lifecycle["production_spine_release_lifecycle"]["latest_rollback"]["rollback_id"] == rollback["rollback_id"]
    assert wrapper_surface["release_runtime"]["production_spine_release_lifecycle"]["latest_rollback"]["rollback_id"] == rollback["rollback_id"]
    assert control_panel["release_wrapper_runtime"]["production_spine_release_lifecycle"]["latest_rollback"]["rollback_id"] == rollback["rollback_id"]

    wrapper_html = (project_root / "ui" / "wrapper" / "index.html").read_text(encoding="utf-8")
    control_panel_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    visualizer_js = (project_root / "ui" / "visualizer" / "app.js").read_text(encoding="utf-8")
    assert "lifecycle rollback" in wrapper_html
    assert "production spine lifecycle rollback" in control_panel_js
    assert "production spine lifecycle rollback" in visualizer_js

    serialized = json.dumps(
        {
            "rollback": rollback,
            "summary": lifecycle_summary,
            "readiness": readiness["evidence"]["production_spine_release_lifecycle"],
            "status_card": status_card["production_spine_release_lifecycle"],
            "session_lifecycle": session_lifecycle["production_spine_release_lifecycle"],
            "wrapper_surface": wrapper_surface["release_runtime"]["production_spine_release_lifecycle"],
            "control_panel": control_panel["release_wrapper_runtime"]["production_spine_release_lifecycle"],
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-ROLLBACK-SPINE" not in serialized
    assert "rollback-operator@example.invalid" not in serialized
    assert "Approve lifecycle rollback test." not in serialized
    assert session_id not in serialized
    assert str(tmp_path) not in serialized


def test_release_wrapper_turn_records_sanitized_developmental_cortex_packet(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    session_id = "developmental-wrapper-user"
    prompt = "Developmental cortex wrapper bridge SECRET-DEVELOPMENTAL-PROMPT"

    before = client.get("/ops/brain/canon/developmental-cortex").json()
    assert before["assessment_count"] == 0

    chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    assert chat.status_code == 200

    scorecard = client.get("/ops/brain/canon/developmental-cortex").json()
    assert scorecard["assessment_count"] == 1
    latest = scorecard["latest_assessment"]
    assert latest["status"] == "shadow-ready"
    assert latest["task_ref"] == "release-wrapper-interaction"
    assert latest["production_mutation_allowed"] is False
    assert latest["body_schema_snapshot"]["surface_id"] == "nexus-body-schema"
    assert latest["reference_frame"]["subject_ref"] == "release-wrapper-interaction"
    assert latest["growth_candidate"]["promotion_state"] == "archived-shadow"
    assert latest["promotion_case"]["decision"] == "accepted-shadow"

    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    latest_interaction = runtime["latest_interaction"]
    assert latest_interaction["developmental_cortex_assessment_ref"] == latest["request_id"]

    serialized = json.dumps({"scorecard": scorecard, "runtime": runtime}, sort_keys=True)
    assert prompt not in serialized
    assert "SECRET-DEVELOPMENTAL-PROMPT" not in serialized
    assert session_id not in serialized


def test_release_wrapper_developmental_release_contract_replays_canonical_outputs(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    session_id = "developmental-release-contract-user"
    prompt = "Project-wide developmental release contract SECRET-DEVELOPMENTAL-CONTRACT"

    chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    assert chat.status_code == 200

    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    readiness = client.get("/ops/wrapper/release-readiness", params={"session_id": session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    lifecycle = client.get("/ops/wrapper/session-lifecycle", params={"session_id": session_id}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]

    restarted = TestClient(create_app(str(project_root)))
    replayed_runtime = restarted.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()

    contract = runtime["developmental_release_contract"]
    assert contract["surface_id"] == "developmental-release-contract"
    assert contract["runtime_state"] == "live-bound"
    assert contract["latest_status"] == "shadow-ready"
    assert contract["canonical_output_names"] == [
        "body_schema_snapshot",
        "reference_frame_updates",
        "dream_request",
        "causal_test_request",
        "growth_archive_candidate",
        "promotion_tribunal_case",
    ]
    assert contract["body_schema_snapshot"]["surface_id"] == "nexus-body-schema"
    assert contract["reference_frame_updates"][0]["subject_ref"] == "release-wrapper-interaction"
    assert contract["dream_request"]["surface_id"] == "developmental-dream-request"
    assert contract["dream_request"]["production_action_allowed"] is False
    assert contract["causal_test_request"]["surface_id"] == "developmental-causal-test-request"
    assert contract["causal_test_request"]["production_action_allowed"] is False
    assert contract["growth_archive_candidate"]["promotion_state"] == "archived-shadow"
    assert contract["promotion_tribunal_case"]["decision"] == "accepted-shadow"
    assert contract["raw_content_included"] is False
    assert contract["active_production_mutation_allowed"] is False

    assert readiness["evidence"]["developmental_release_contract"]["latest_status"] == "shadow-ready"
    assert status_card["developmental_release_contract"]["surface_id"] == "developmental-release-contract"
    assert lifecycle["developmental_release_contract"]["canonical_output_count"] == 6
    assert control_panel["release_wrapper_runtime"]["developmental_release_contract"]["latest_status"] == "shadow-ready"
    assert control_panel["release_wrapper_developmental_release_contract"]["surface_id"] == "developmental-release-contract"
    assert replayed_runtime["developmental_release_contract"]["latest_assessment_ref"] == contract["latest_assessment_ref"]
    assert replayed_runtime["developmental_release_contract"]["latest_status"] == "shadow-ready"

    control_panel_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    visualizer_js = (project_root / "ui" / "visualizer" / "app.js").read_text(encoding="utf-8")
    assert "Developmental release contract" in control_panel_js
    assert "developmental release contract" in visualizer_js

    serialized = json.dumps(
        {
            "runtime": runtime,
            "readiness": readiness,
            "status_card": status_card,
            "lifecycle": lifecycle,
            "control_panel": control_panel,
            "replayed_runtime": replayed_runtime,
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-DEVELOPMENTAL-CONTRACT" not in serialized
    assert session_id not in serialized
    assert str(tmp_path) not in serialized


def test_release_wrapper_forward_pass_enforcement_matrix_tracks_product_admin_and_missing_paths(tmp_path: Path):
    project_root = make_project(tmp_path)
    sandbox_probe = project_root / "tests" / "forward_pass_matrix_probe_test.py"
    sandbox_probe.parent.mkdir(parents=True, exist_ok=True)
    sandbox_probe.write_text(
        "def test_forward_pass_matrix_probe():\n"
        "    assert 'forward-pass-matrix'.replace('-', '_') == 'forward_pass_matrix'\n",
        encoding="utf-8",
    )
    client = TestClient(create_app(str(project_root)))
    session_id = "forward-pass-matrix-user"
    prompt = "Exercise the whole-system forward pass matrix SECRET-FORWARD-MATRIX"

    chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    assert chat.status_code == 200
    packet = client.get("/ops/wrapper/federated-packets", params={"session_id": session_id}).json()["latest_packet"]
    imported = client.post(
        "/ops/wrapper/federated-packets/import",
        json={"session_id": session_id, "peer_node_id": "forward-pass-matrix-peer", "packet": packet},
    )
    assert imported.status_code == 200

    runner = client.post(
        "/ops/wrapper/release-readiness/run",
        json={
            "session_id": session_id,
            "command": "pytest tests/forward_pass_matrix_probe_test.py -q",
            "timeout_seconds": 30,
            "approved_by": "admin",
            "approval_ref": "operator-review::forward-pass-matrix",
        },
    )
    assert runner.status_code == 200

    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    readiness = client.get("/ops/wrapper/release-readiness", params={"session_id": session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    lifecycle = client.get("/ops/wrapper/session-lifecycle", params={"session_id": session_id}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]

    matrix = runtime["whole_system_forward_pass_enforcement_matrix"]
    rows = {row["entrypoint_id"]: row for row in matrix["entrypoints"]}
    checks = {check["check_id"]: check for check in readiness["readiness_checks"]}

    assert matrix["surface_id"] == "whole-system-forward-pass-enforcement-matrix"
    assert matrix["coverage_status"] == "partial"
    assert matrix["missing_entrypoint_ids"] == ["domain_expert_growth_admin_replay"]
    assert matrix["raw_content_included"] is False
    assert matrix["active_production_mutation_allowed"] is False
    receipt = matrix["latest_receipt"]
    assert receipt["surface_id"] == "whole-system-forward-pass-enforcement-receipt"
    assert receipt["receipt_id"] == matrix["latest_receipt_id"]
    assert receipt["trace_ref"] == f"trace::{runtime['latest_interaction']['trace_id']}"
    assert receipt["coverage_status"] == matrix["coverage_status"]
    assert receipt["entrypoint_count"] == matrix["entrypoint_count"]
    assert receipt["covered_entrypoint_count"] == matrix["covered_entrypoint_count"]
    assert receipt["missing_entrypoint_count"] == matrix["missing_entrypoint_count"]
    assert receipt["required_entrypoint_ids"] == matrix["required_entrypoint_ids"]
    assert receipt["raw_content_included"] is False
    assert receipt["active_production_mutation_allowed"] is False
    assert receipt["active_production_mutated"] is False
    assert runtime["latest_interaction"]["whole_system_forward_pass_enforcement_receipt_id"] == receipt["receipt_id"]
    assert matrix["required_capability_columns"] == [
        "continuous_assimilation",
        "global_growth",
        "federated_packet",
        "production_spine",
        "ao_eval_tool_governance",
        "developmental_release_contract",
        "dream_research_queue",
        "cache_context_truth",
        "rollback_safe_updates",
    ]
    assert set(rows) >= {
        "wrapper_model_interaction",
        "nexusbrain_runtime_cycle",
        "federated_packet_import",
        "release_readiness_evidence_runner",
        "admin_approval",
        "sandbox_tests",
        "safe_apply",
        "rollback",
        "native_hive_heartbeat",
        "domain_expert_growth_admin_replay",
        "boot_supervisor",
        "initial_release_supervisor",
        "production_spine_release_lifecycle",
        "production_spine_lifecycle_rollback",
    }
    assert rows["wrapper_model_interaction"]["status"] == "covered"
    assert rows["wrapper_model_interaction"]["capabilities"]["continuous_assimilation"] == "covered"
    assert rows["wrapper_model_interaction"]["capabilities"]["developmental_release_contract"] == "covered"
    cycle = runtime["nexusbrain_runtime_cycle"]
    assert cycle["latest_status"] == "covered"
    assert rows["nexusbrain_runtime_cycle"]["status"] == "covered"
    assert rows["nexusbrain_runtime_cycle"]["honest_status_label"] == "covered"
    assert rows["nexusbrain_runtime_cycle"]["category"] == "nexusbrain"
    assert rows["nexusbrain_runtime_cycle"]["operation_receipt"]["receipt_id"] == cycle["latest_receipt_id"]
    assert rows["nexusbrain_runtime_cycle"]["operation_receipt"]["status"] == "covered"
    assert rows["nexusbrain_runtime_cycle"]["operation_receipt"]["raw_content_included"] is False
    assert rows["nexusbrain_runtime_cycle"]["operation_receipt"]["active_production_mutated"] is False
    assert rows["nexusbrain_runtime_cycle"]["blockers"] == []
    assert (
        f"nexusbrain-cycle::{cycle['latest_receipt_id']}"
        in rows["nexusbrain_runtime_cycle"]["evidence_refs"]
    )
    assert rows["nexusbrain_runtime_cycle"]["capabilities"] == {
        column: "covered" for column in matrix["required_capability_columns"]
    }
    assert rows["release_readiness_evidence_runner"]["status"] == "covered"
    assert rows["admin_approval"]["status"] == "covered"
    assert rows["sandbox_tests"]["status"] == "covered"
    assert rows["safe_apply"]["status"] == "covered"
    assert rows["rollback"]["status"] == "covered"
    assert rows["native_hive_heartbeat"]["status"] == "covered"
    assert rows["native_hive_heartbeat"]["category"] == "native-hive"
    assert any(ref.startswith("native-hive-heartbeat::") for ref in rows["native_hive_heartbeat"]["evidence_refs"])
    assert rows["federated_packet_import"]["status"] == "covered"
    assert rows["boot_supervisor"]["status"] == "covered"
    assert rows["boot_supervisor"]["honest_status_label"] == "covered"
    assert rows["initial_release_supervisor"]["status"] == "covered"
    assert rows["production_spine_release_lifecycle"]["status"] == "covered"
    assert rows["production_spine_lifecycle_rollback"]["status"] == "covered"
    assert rows["domain_expert_growth_admin_replay"]["status"] == "missing"

    assert readiness["evidence"]["whole_system_forward_pass_enforcement_matrix"]["coverage_status"] == "partial"
    assert (
        readiness["evidence"]["whole_system_forward_pass_enforcement_matrix"]["latest_receipt_id"]
        == receipt["receipt_id"]
    )
    assert checks["whole-system-forward-pass-enforcement-matrix"]["status"] == "pass"
    assert status_card["whole_system_forward_pass_enforcement_matrix"]["entrypoint_count"] == matrix["entrypoint_count"]
    assert status_card["whole_system_forward_pass_enforcement_matrix"]["latest_receipt_id"] == receipt["receipt_id"]
    assert lifecycle["whole_system_forward_pass_enforcement_matrix"]["coverage_status"] == "partial"
    assert lifecycle["whole_system_forward_pass_enforcement_matrix"]["latest_receipt_id"] == receipt["receipt_id"]
    assert control_panel["release_wrapper_runtime"]["whole_system_forward_pass_enforcement_matrix"]["coverage_status"] == "partial"
    assert (
        control_panel["release_wrapper_runtime"]["whole_system_forward_pass_enforcement_matrix"]["latest_receipt_id"]
        == receipt["receipt_id"]
    )
    assert control_panel["release_wrapper_forward_pass_enforcement_matrix"]["surface_id"] == "whole-system-forward-pass-enforcement-matrix"
    assert control_panel["release_wrapper_forward_pass_enforcement_matrix"]["latest_receipt_id"] == receipt["receipt_id"]

    control_panel_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    visualizer_js = (project_root / "ui" / "visualizer" / "app.js").read_text(encoding="utf-8")
    assert "Whole-system forward-pass matrix" in control_panel_js
    assert "forward-pass matrix" in visualizer_js

    serialized = json.dumps(
        {
            "runtime": runtime,
            "readiness": readiness,
            "status_card": status_card,
            "lifecycle": lifecycle,
            "control_panel": control_panel,
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-FORWARD-MATRIX" not in serialized
    assert session_id not in serialized
    assert str(tmp_path) not in serialized


def test_release_wrapper_developmental_packet_feeds_governed_update_surfaces(tmp_path: Path):
    project_root = make_project(tmp_path)
    sandbox_probe = project_root / "tests" / "developmental_update_apply_probe_test.py"
    sandbox_probe.parent.mkdir(parents=True, exist_ok=True)
    sandbox_probe.write_text(
        "def test_developmental_update_apply_probe():\n"
        "    assert 'developmental-cortex'.split('-')[0] == 'developmental'\n",
        encoding="utf-8",
    )
    client = TestClient(create_app(str(project_root)))
    session_id = "developmental-update-user"
    prompt = "Use developmental cortex to govern wrapper self-improvement SECRET-DEVELOPMENTAL-UPDATE"

    chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    assert chat.status_code == 200

    developmental = client.get("/ops/brain/canon/developmental-cortex").json()
    latest_assessment = developmental["latest_assessment"]
    growth_candidate_ref = latest_assessment["growth_candidate"]["candidate_id"]
    promotion_case_ref = latest_assessment["promotion_case"]["case_id"]

    queue = client.get("/ops/brain/self-improvement/queue").json()
    item = queue["items"][0]
    event = item["event"]
    assert event["metadata"]["developmental_cortex_assessment_ref"] == latest_assessment["request_id"]
    assert event["metadata"]["developmental_cortex_growth_candidate_ref"] == growth_candidate_ref
    assert event["metadata"]["developmental_cortex_promotion_case_ref"] == promotion_case_ref
    assert f"developmental-cortex::{latest_assessment['request_id']}" in event["evidence_refs"]

    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    dream_queue = runtime["dream_research_queue"]
    latest_item = dream_queue["latest_item"]
    proposal = next(
        candidate
        for candidate in runtime["autonomous_updates"]["proposals"]
        if candidate["metadata"].get("improvement_queue_id") == latest_item["queue_id"]
    )
    assert latest_item["metadata"]["developmental_cortex_assessment_ref"] == latest_assessment["request_id"]
    assert latest_item["governance"]["developmental_cortex_assessment_ref"] == latest_assessment["request_id"]
    assert latest_item["governance"]["developmental_growth_candidate_ref"] == growth_candidate_ref
    assert latest_item["governance"]["developmental_promotion_case_ref"] == promotion_case_ref
    assert latest_item["governance"]["active_production_mutation_allowed"] is False
    assert proposal["metadata"]["developmental_cortex_assessment_ref"] == latest_assessment["request_id"]
    assert proposal["metadata"]["safe_payload"]["developmental_growth_candidate_ref"] == growth_candidate_ref
    assert proposal["metadata"]["safe_payload"]["developmental_promotion_case_ref"] == promotion_case_ref
    assert f"developmental-cortex::{latest_assessment['request_id']}" in proposal["eval_refs"]

    status_card = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    action_lane = status_card["operator_action_lane"]
    assert action_lane["developmental_cortex_assessment_ref"] == latest_assessment["request_id"]
    assert action_lane["developmental_promotion_case_ref"] == promotion_case_ref

    lifecycle = client.get("/ops/wrapper/session-lifecycle", params={"session_id": session_id}).json()
    assert lifecycle["autonomous_update_path"]["developmental_cortex_assessment_ref"] == latest_assessment["request_id"]
    assert lifecycle["operator_action_lane"]["developmental_growth_candidate_ref"] == growth_candidate_ref

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]
    visualized_queue = control_panel["release_wrapper_runtime"]["dream_research_queue"]
    assert visualized_queue["latest_item"]["governance"]["developmental_promotion_case_ref"] == promotion_case_ref
    assert control_panel["developmental_cortex_scorecard"]["latest_assessment"]["request_id"] == latest_assessment["request_id"]

    approval = client.post(
        action_lane["admin_approval_ref"],
        json={"approved_by": "admin", "approval_ref": "operator-review::developmental-update"},
    )
    assert approval.status_code == 200
    approval_payload = approval.json()
    assert approval_payload["status"] == "admin-approved"
    assert approval_payload["linked_eval_replay"]["status"] == "passed-shadow"
    assert approval_payload["linked_eval_replay"]["promotion_allowed"] is True
    assert approval_payload["linked_improvement_queue"]["queue_status"] == "validated"
    assert approval_payload["release_wrapper_ao_guard"]["passed"] is True

    sandbox = client.post(
        action_lane["sandbox_tests_ref"],
        json={"command": "pytest tests/developmental_update_apply_probe_test.py -q", "timeout_seconds": 30},
    )
    assert sandbox.status_code == 200
    sandbox_payload = sandbox.json()
    assert sandbox_payload["status"] == "passed"
    assert sandbox_payload["sandbox"]["active_project_root_mutated"] is False
    assert sandbox_payload["diff_summary"]["unsafe_change_count"] == 0

    applied = client.post(
        action_lane["apply_ref"],
        json={
            "test_refs": ["pytest tests/developmental_update_apply_probe_test.py -q"],
            "test_evidence_refs": [sandbox_payload["evidence_ref"]],
        },
    )
    assert applied.status_code == 200
    applied_payload = applied.json()
    assert applied_payload["status"] == "applied-shadow-safe-file"
    assert applied_payload["active_production_mutated"] is False
    safe_record = json.loads(Path(applied_payload["safe_file_path"]).read_text(encoding="utf-8"))
    assert safe_record["safe_payload"]["developmental_cortex_assessment_ref"] == latest_assessment["request_id"]
    assert safe_record["safe_payload"]["developmental_growth_candidate_ref"] == growth_candidate_ref
    assert safe_record["safe_payload"]["developmental_promotion_case_ref"] == promotion_case_ref

    rollback = client.post(action_lane["rollback_ref"], json={"reason": "developmental-update-regression"})
    assert rollback.status_code == 200
    assert rollback.json()["status"] == "rolled-back"
    assert rollback.json()["rollback_restored"] is True

    refreshed_lifecycle = client.get("/ops/wrapper/session-lifecycle", params={"session_id": session_id}).json()
    assert (
        refreshed_lifecycle["autonomous_update_path"]["developmental_cortex_assessment_ref"]
        == latest_assessment["request_id"]
    )
    assert refreshed_lifecycle["autonomous_update_path"]["latest_applied"]["active_production_mutated"] is False
    assert refreshed_lifecycle["autonomous_update_path"]["latest_rollback"]["rollback_restored"] is True

    control_panel_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    visualizer_js = (project_root / "ui" / "visualizer" / "app.js").read_text(encoding="utf-8")
    assert "developmental cortex assessment" in control_panel_js
    assert "developmental promotion case" in control_panel_js
    assert "Harness developmental cortex" in visualizer_js

    serialized = json.dumps(
        {
            "developmental": developmental,
            "queue_item": item,
            "runtime_latest_interaction": runtime["latest_interaction"],
            "dream_research_queue": runtime["dream_research_queue"],
            "status_card_lane": action_lane,
            "lifecycle_update_path": lifecycle["autonomous_update_path"],
            "lifecycle_lane": lifecycle["operator_action_lane"],
            "visualized_queue": visualized_queue,
            "proposal": proposal,
            "approval": approval_payload,
            "sandbox": sandbox_payload,
            "safe_record": safe_record,
            "rollback": rollback.json(),
            "refreshed_lifecycle": refreshed_lifecycle,
        },
        sort_keys=True,
    )
    assert prompt not in serialized
    assert "SECRET-DEVELOPMENTAL-UPDATE" not in serialized
    assert session_id not in serialized


def test_release_wrapper_startup_supervisor_records_release_health_heartbeat_and_repair_proposal(
    tmp_path: Path,
):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    startup_session_id = "startup-health-raw-session"

    runtime = client.get("/ops/wrapper/release-runtime").json()
    readiness = client.get("/ops/wrapper/release-readiness").json()
    status_card = client.get("/ops/wrapper/status-card").json()
    lifecycle = client.get("/ops/wrapper/session-lifecycle").json()
    visualizer = client.get("/ops/brain/visualizer/state").json()
    control_panel = visualizer["overlay_state"]["control_panel"]
    checks = {check["check_id"]: check for check in readiness["readiness_checks"]}

    heartbeat = runtime["release_health_heartbeat"]
    heartbeat_path = project_root / "artifacts" / "release-wrapper-runtime" / "release-health-heartbeat.jsonl"
    heartbeat_records = [
        json.loads(line)
        for line in heartbeat_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert heartbeat["surface_id"] == "release-wrapper-health-heartbeat"
    assert heartbeat["trigger"] == "startup"
    assert heartbeat["status"] == "blocked"
    assert heartbeat["product_surface"] == "wrapper"
    assert heartbeat["release_readiness"]["go_no_go"] == "no-go"
    assert heartbeat["boot_supervisor"]["latest_status"] in {"not-run", "boot-smoke-blocked"}
    assert heartbeat["release_product_smoke"]["latest_status"] == "not-run"
    assert heartbeat["self_repair_proposal"]["status"] == "proposed"
    assert heartbeat["self_repair_proposal"]["update_id"].startswith("update::release-wrapper-startup-supervisor::")
    assert heartbeat["self_repair_proposal"]["active_production_mutation_allowed"] is False
    assert heartbeat["active_production_mutation_allowed"] is False
    assert heartbeat["active_production_mutated"] is False
    assert heartbeat["raw_content_included"] is False
    assert heartbeat["artifact_ref"] == "release-wrapper-runtime/release-health-heartbeat.jsonl"
    assert heartbeat_records[-1]["heartbeat_id"] == heartbeat["heartbeat_id"]
    assert heartbeat_records[-1]["raw_content_included"] is False

    assert checks["release-health-heartbeat"]["status"] == "blocked"
    assert checks["release-health-heartbeat"]["go_no_go_blocking"] is False
    assert readiness["evidence"]["release_health_heartbeat"]["status"] == "blocked"
    assert status_card["release_health_heartbeat"]["status"] == "blocked"
    assert status_card["runtime"]["release_health_heartbeat"]["status"] == "blocked"
    assert lifecycle["release_health_heartbeat"]["status"] == "blocked"
    assert control_panel["release_wrapper_release_health_heartbeat"]["status"] == "blocked"

    startup_proposals = [
        proposal
        for proposal in status_card["autonomous_updates"]["proposals"]
        if (proposal.get("metadata") or {}).get("source") == "release-wrapper-startup-supervisor"
    ]
    assert startup_proposals
    proposal = startup_proposals[0]
    assert proposal["update_type"] == "runtime"
    assert proposal["target_ref"] == "safe-artifact::release-wrapper-startup-supervisor"
    assert proposal["operator_approved"] is False
    assert proposal["metadata"]["release_health_heartbeat_id"] == heartbeat["heartbeat_id"]
    assert proposal["metadata"]["active_production_mutation_allowed"] is False

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    visualizer_js = (project_root / "ui" / "visualizer" / "app.js").read_text(encoding="utf-8")
    assert "Release health heartbeat" in app_js
    assert "release_health_heartbeat" in app_js
    assert "release_wrapper_release_health_heartbeat" in visualizer_js
    assert "release health heartbeat" in visualizer_js

    serialized = json.dumps(
        {
            "heartbeat": heartbeat,
            "records": heartbeat_records,
            "readiness_evidence": readiness["evidence"]["release_health_heartbeat"],
            "status_card": status_card["release_health_heartbeat"],
            "lifecycle": lifecycle["release_health_heartbeat"],
            "control_panel": control_panel["release_wrapper_release_health_heartbeat"],
            "proposal": proposal,
        },
        sort_keys=True,
    )
    assert startup_session_id not in serialized
    assert str(project_root) not in serialized
    assert "SECRET" not in serialized


def test_release_wrapper_health_heartbeat_loop_runs_bounded_self_checks_with_backoff_and_repair_queue(
    tmp_path: Path,
):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    raw_session_id = "release-health-loop-raw-session"

    response = client.post(
        "/ops/wrapper/release-health-heartbeat/run",
        json={
            "session_id": raw_session_id,
            "trigger": "operator-request",
            "max_cycles": 3,
            "interval_seconds": 30,
            "max_retry_attempts": 3,
            "retry_backoff_seconds": 2,
            "base_url": "http://127.0.0.1:8777",
            "host": "127.0.0.1",
            "port": 8777,
            "pid": 4242,
        },
    )

    assert response.status_code == 200
    loop = response.json()
    loop_path = project_root / "artifacts" / "release-wrapper-runtime" / "release-health-heartbeat-loop.jsonl"
    loop_records = [
        json.loads(line)
        for line in loop_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert loop["schema_version"] == "nexusnet-release-wrapper-health-heartbeat-loop-v1"
    assert loop["surface_id"] == "release-wrapper-health-heartbeat-loop"
    assert loop["status"] == "blocked"
    assert loop["trigger"] == "operator-request"
    assert loop["max_cycles"] == 3
    assert loop["cycle_count"] == 3
    assert loop["timer"]["interval_seconds"] == 30
    assert loop["timer"]["sleep_performed"] is False
    assert loop["timer"]["background_thread_started"] is False
    assert loop["bounded_retry"]["max_retry_attempts"] == 3
    assert loop["bounded_retry"]["attempt_count"] == 3
    assert loop["bounded_retry"]["backoff_seconds"] == [2, 4, 8]
    assert loop["bounded_retry"]["bounded"] is True
    assert loop["latest_heartbeat_id"] == loop["cycles"][-1]["heartbeat_id"]
    assert [cycle["cycle_index"] for cycle in loop["cycles"]] == [1, 2, 3]
    assert all(cycle["status"] == "blocked" for cycle in loop["cycles"])
    assert all(cycle["raw_content_included"] is False for cycle in loop["cycles"])
    assert loop["repair_queue"]["status"] == "proposal-routed"
    assert loop["repair_queue"]["latest_update_id"].startswith("update::release-wrapper-health-heartbeat-loop::")
    whole_system_candidates = loop["whole_system_repair_candidates"]
    whole_system_gate_ids = {candidate["gate_id"] for candidate in whole_system_candidates}
    whole_system_target_surfaces = set(loop["repair_queue"]["target_surfaces"])
    assert {
        "production-spine-release-manifest",
        "native-hive-runtime-heartbeat",
        "federation-runtime-path",
        "authority-evidence-tool-governance",
    }.issubset(whole_system_gate_ids)
    assert {
        "production-spine",
        "native-hive-runtime",
        "growth-engine",
        "federation-runtime",
        "authority-spine",
        "eval-runtime-governance",
        "tool-action-harness",
    }.issubset(whole_system_target_surfaces)
    assert loop["repair_queue"]["whole_system_candidate_count"] == len(whole_system_candidates)
    assert all(candidate["raw_content_included"] is False for candidate in whole_system_candidates)
    assert all(candidate["active_production_mutation_allowed"] is False for candidate in whole_system_candidates)
    assert loop["active_production_mutation_allowed"] is False
    assert loop["active_production_mutated"] is False
    assert loop["raw_content_included"] is False
    assert loop["artifact_ref"] == "release-wrapper-runtime/release-health-heartbeat-loop.jsonl"
    assert loop_records[-1]["loop_id"] == loop["loop_id"]
    assert loop_records[-1]["raw_content_included"] is False

    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": raw_session_id}).json()
    readiness = client.get("/ops/wrapper/release-readiness", params={"session_id": raw_session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": raw_session_id}).json()
    lifecycle = client.get("/ops/wrapper/session-lifecycle", params={"session_id": raw_session_id}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": raw_session_id}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]
    checks = {check["check_id"]: check for check in readiness["readiness_checks"]}

    assert runtime["release_health_heartbeat_loop"]["latest_loop_id"] == loop["loop_id"]
    assert runtime["release_health_heartbeat_loop"]["latest_heartbeat_id"] == loop["latest_heartbeat_id"]
    assert readiness["evidence"]["release_health_heartbeat_loop"]["latest_loop_id"] == loop["loop_id"]
    assert checks["release-health-heartbeat-loop"]["status"] == "blocked"
    assert checks["release-health-heartbeat-loop"]["go_no_go_blocking"] is False
    assert status_card["release_health_heartbeat_loop"]["latest_loop_id"] == loop["loop_id"]
    assert lifecycle["release_health_heartbeat_loop"]["latest_loop_id"] == loop["loop_id"]
    assert control_panel["release_wrapper_release_health_heartbeat_loop"]["latest_loop_id"] == loop["loop_id"]
    assert status_card["operator_action_lane"]["run_release_health_heartbeat_loop_ref"] == (
        "/ops/wrapper/release-health-heartbeat/run"
    )

    loop_proposals = [
        proposal
        for proposal in status_card["autonomous_updates"]["proposals"]
        if (proposal.get("metadata") or {}).get("source") == "release-wrapper-health-heartbeat-loop"
    ]
    assert loop_proposals
    proposal = loop_proposals[0]
    assert proposal["target_ref"] == "safe-artifact::release-wrapper-health-heartbeat-loop"
    assert proposal["metadata"]["loop_id"] == loop["loop_id"]
    assert proposal["metadata"]["heartbeat_ids"] == [cycle["heartbeat_id"] for cycle in loop["cycles"]]
    assert proposal["metadata"]["active_production_mutation_allowed"] is False
    assert {
        "production-spine",
        "native-hive-runtime",
        "growth-engine",
        "federation-runtime",
        "authority-spine",
        "eval-runtime-governance",
        "tool-action-harness",
    }.issubset(set(proposal["target_surfaces"]))
    assert proposal["metadata"]["safe_payload"]["whole_system_candidate_count"] == len(whole_system_candidates)
    assert proposal["metadata"]["safe_payload"]["target_surfaces"] == proposal["target_surfaces"]

    control_panel_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    visualizer_js = (project_root / "ui" / "visualizer" / "app.js").read_text(encoding="utf-8")
    assert "Release health loop" in control_panel_js
    assert "run_release_health_heartbeat_loop" in control_panel_js
    assert "release_wrapper_release_health_heartbeat_loop" in visualizer_js
    assert "release health loop" in visualizer_js

    serialized = json.dumps(
        {
            "loop": loop,
            "records": loop_records,
            "runtime": runtime["release_health_heartbeat_loop"],
            "readiness": readiness["evidence"]["release_health_heartbeat_loop"],
            "status_card": status_card["release_health_heartbeat_loop"],
            "lifecycle": lifecycle["release_health_heartbeat_loop"],
            "control_panel": control_panel["release_wrapper_release_health_heartbeat_loop"],
            "proposal": proposal,
        },
        sort_keys=True,
    )
    assert raw_session_id not in serialized
    assert str(project_root) not in serialized
    assert "SECRET" not in serialized


def test_release_wrapper_boot_auto_runs_health_heartbeat_loop_without_manual_call(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    runtime = client.get("/ops/wrapper/release-runtime").json()
    readiness = client.get("/ops/wrapper/release-readiness").json()
    status_card = client.get("/ops/wrapper/status-card").json()
    lifecycle = client.get("/ops/wrapper/session-lifecycle").json()
    visualizer = client.get("/ops/brain/visualizer/state").json()
    control_panel = visualizer["overlay_state"]["control_panel"]
    loop_path = project_root / "artifacts" / "release-wrapper-runtime" / "release-health-heartbeat-loop.jsonl"
    loop_records = [
        json.loads(line)
        for line in loop_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    loop = runtime["release_health_heartbeat_loop"]
    checks = {check["check_id"]: check for check in readiness["readiness_checks"]}

    assert loop["schema_version"] == "nexusnet-release-wrapper-health-heartbeat-loop-v1"
    assert loop["surface_id"] == "release-wrapper-health-heartbeat-loop"
    assert loop["trigger"] == "startup-auto"
    assert loop["cycle_count"] == 1
    assert loop["max_cycles"] == 1
    assert loop["bounded_retry"]["max_retry_attempts"] == 1
    assert loop["timer"]["sleep_performed"] is False
    assert loop["timer"]["background_thread_started"] is False
    assert loop["raw_content_included"] is False
    assert loop["active_production_mutation_allowed"] is False
    assert loop["active_production_mutated"] is False
    assert loop["repair_queue"]["status"] in {"proposal-routed", "not-required"}
    assert loop["failure_learning_signal"]["surface_id"] == "release-wrapper-failure-learning-signal"
    assert loop["failure_learning_signal"]["failure_stage"] == "release_health_heartbeat_loop_blocked"
    assert loop["failure_learning_signal"]["raw_content_included"] is False
    assert loop_records[-1]["loop_id"] == loop["loop_id"]
    assert loop_records[-1]["failure_learning_signal"]["raw_content_included"] is False
    assert readiness["evidence"]["release_health_heartbeat_loop"]["latest_loop_id"] == loop["loop_id"]
    assert checks["release-health-heartbeat-loop"]["go_no_go_blocking"] is False
    assert status_card["release_health_heartbeat_loop"]["latest_loop_id"] == loop["loop_id"]
    assert lifecycle["release_health_heartbeat_loop"]["latest_loop_id"] == loop["loop_id"]
    assert control_panel["release_wrapper_release_health_heartbeat_loop"]["latest_loop_id"] == loop["loop_id"]

    serialized = json.dumps(
        {
            "runtime": runtime["release_health_heartbeat_loop"],
            "readiness": readiness["evidence"]["release_health_heartbeat_loop"],
            "status_card": status_card["release_health_heartbeat_loop"],
            "lifecycle": lifecycle["release_health_heartbeat_loop"],
            "control_panel": control_panel["release_wrapper_release_health_heartbeat_loop"],
        },
        sort_keys=True,
    )
    assert str(project_root) not in serialized
    assert "SECRET" not in serialized


def test_wrapper_model_interaction_auto_pulses_release_health_loop_and_failure_learning(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    raw_session_id = "auto-heartbeat-user"

    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": "Pulse the release wrapper heartbeat."}],
            "user": raw_session_id,
        },
    )

    assert response.status_code == 200
    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": raw_session_id}).json()
    readiness = client.get("/ops/wrapper/release-readiness", params={"session_id": raw_session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": raw_session_id}).json()
    loop_path = project_root / "artifacts" / "release-wrapper-runtime" / "release-health-heartbeat-loop.jsonl"
    loop_records = [
        json.loads(line)
        for line in loop_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    loop = runtime["release_health_heartbeat_loop"]
    latest_interaction = runtime["latest_interaction"]
    failure_signal = loop["failure_learning_signal"]

    assert loop["trigger"] == "wrapper-interaction-auto"
    assert loop["cycle_count"] == 1
    assert loop["max_cycles"] == 1
    assert loop["latest_heartbeat_id"] == loop["cycles"][-1]["heartbeat_id"]
    assert loop["raw_content_included"] is False
    assert loop["active_production_mutation_allowed"] is False
    assert failure_signal["surface_id"] == "release-wrapper-failure-learning-signal"
    assert failure_signal["failure_stage"] == "release_health_heartbeat_loop_blocked"
    assert failure_signal["continuous_assimilation_captured"] is True
    assert failure_signal["global_growth_captured"] is True
    assert latest_interaction["release_health_heartbeat_loop_id"] == loop["loop_id"]
    assert latest_interaction["release_health_failure_learning_signal"]["signal_id"] == failure_signal["signal_id"]
    assert latest_interaction["release_health_failure_learning_signal"]["raw_content_included"] is False
    assert readiness["evidence"]["release_health_heartbeat_loop"]["latest_loop_id"] == loop["loop_id"]
    assert status_card["operator_action_lane"]["latest_action_statuses"]["release_health_heartbeat_loop"] == loop["status"]
    assert loop_records[-1]["loop_id"] == loop["loop_id"]
    assert raw_session_id not in json.dumps(runtime)
    assert "Pulse the release wrapper heartbeat" not in json.dumps(runtime)


def test_release_wrapper_periodic_heartbeat_supervisor_pulses_from_live_wrapper_use_without_manual_loop(
    tmp_path: Path,
):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    raw_session_id = "periodic-heartbeat-user"
    prompt = "Trigger periodic heartbeat without manual loop SECRET-PERIODIC."

    configured = client.post(
        "/ops/wrapper/release-health-heartbeat/supervisor/configure",
        json={
            "session_id": raw_session_id,
            "enabled": True,
            "interval_seconds": 1,
            "max_pulses_per_tick": 1,
            "schedule_immediately": True,
            "configured_by": "admin",
        },
    )

    assert configured.status_code == 200
    config_payload = configured.json()
    assert config_payload["surface_id"] == "release-wrapper-health-heartbeat-supervisor"
    assert config_payload["status"] == "enabled"
    assert config_payload["next_due_status"] == "due"
    assert config_payload["active_production_mutation_allowed"] is False
    assert config_payload["raw_content_included"] is False

    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
            "user": raw_session_id,
        },
    )

    assert response.status_code == 200
    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": raw_session_id}).json()
    readiness = client.get("/ops/wrapper/release-readiness", params={"session_id": raw_session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": raw_session_id}).json()
    lifecycle = client.get("/ops/wrapper/session-lifecycle", params={"session_id": raw_session_id}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": raw_session_id}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]
    pulse_path = project_root / "artifacts" / "release-wrapper-runtime" / "release-health-heartbeat-supervisor.jsonl"
    pulse_records = [
        json.loads(line)
        for line in pulse_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    supervisor = runtime["release_health_heartbeat_supervisor"]
    pulse = supervisor["latest_pulse"]
    pulse_loop = pulse["loop"]
    failure_signal = pulse_loop["failure_learning_signal"]
    checks = {check["check_id"]: check for check in readiness["readiness_checks"]}

    assert supervisor["schema_version"] == "nexusnet-release-wrapper-health-heartbeat-supervisor-v1"
    assert supervisor["status"] == "enabled"
    assert supervisor["runtime_state"] == "live-evidence"
    assert supervisor["pulse_count"] >= 1
    assert supervisor["latest_loop_id"] == pulse_loop["loop_id"]
    assert supervisor["timer"]["interval_seconds"] == 1
    assert supervisor["timer"]["sleep_performed"] is False
    assert supervisor["timer"]["background_thread_started"] is False
    assert pulse["trigger"] == "wrapper-interaction-periodic"
    assert pulse["manual_endpoint_used"] is False
    assert pulse["raw_content_included"] is False
    assert pulse["active_production_mutation_allowed"] is False
    assert pulse_loop["trigger"] == "periodic-wrapper-interaction-auto"
    assert pulse_loop["cycle_count"] == 1
    assert pulse_loop["repair_queue"]["status"] in {"proposal-routed", "not-required"}
    assert failure_signal["surface_id"] == "release-wrapper-failure-learning-signal"
    assert failure_signal["continuous_assimilation_captured"] is True
    assert failure_signal["global_growth_captured"] is True
    assert pulse_records[-1]["pulse_id"] == pulse["pulse_id"]
    assert pulse_records[-1]["manual_endpoint_used"] is False
    assert pulse_records[-1]["loop"]["failure_learning_signal"]["raw_content_included"] is False

    assert runtime["latest_interaction"]["release_health_heartbeat_supervisor_pulse_id"] == pulse["pulse_id"]
    assert readiness["evidence"]["release_health_heartbeat_supervisor"]["latest_pulse_id"] == pulse["pulse_id"]
    assert checks["release-health-heartbeat-supervisor"]["go_no_go_blocking"] is False
    assert status_card["release_health_heartbeat_supervisor"]["latest_pulse_id"] == pulse["pulse_id"]
    assert status_card["operator_action_lane"]["configure_release_health_heartbeat_supervisor_ref"] == (
        "/ops/wrapper/release-health-heartbeat/supervisor/configure"
    )
    assert (
        status_card["operator_action_lane"]["latest_action_statuses"]["release_health_heartbeat_supervisor"]
        == "enabled"
    )
    assert lifecycle["release_health_heartbeat_supervisor"]["latest_pulse_id"] == pulse["pulse_id"]
    assert control_panel["release_wrapper_release_health_heartbeat_supervisor"]["latest_pulse_id"] == pulse["pulse_id"]

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    visualizer_js = (project_root / "ui" / "visualizer" / "app.js").read_text(encoding="utf-8")
    assert "Release heartbeat supervisor" in app_js
    assert "configure_release_health_heartbeat_supervisor" in app_js
    assert "release_wrapper_release_health_heartbeat_supervisor" in visualizer_js
    assert "release health supervisor" in visualizer_js

    disabled = client.post(
        "/ops/wrapper/release-health-heartbeat/supervisor/configure",
        json={"session_id": raw_session_id, "enabled": False, "configured_by": "admin"},
    )
    assert disabled.status_code == 200
    assert disabled.json()["status"] == "disabled"

    serialized = json.dumps(
        {
            "configured": config_payload,
            "runtime": runtime["release_health_heartbeat_supervisor"],
            "readiness": readiness["evidence"]["release_health_heartbeat_supervisor"],
            "status_card": status_card["release_health_heartbeat_supervisor"],
            "lifecycle": lifecycle["release_health_heartbeat_supervisor"],
            "control_panel": control_panel["release_wrapper_release_health_heartbeat_supervisor"],
            "records": pulse_records,
        },
        sort_keys=True,
    )
    assert raw_session_id not in serialized
    assert prompt not in serialized
    assert "SECRET-PERIODIC" not in serialized
    assert str(project_root) not in serialized


def test_native_project_heartbeat_recovery_governance_is_visible_in_release_surfaces(
    tmp_path: Path,
):
    project_root = make_project(tmp_path)
    TestClient(create_app(str(project_root)))

    control_panel_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    visualizer_js = (project_root / "ui" / "visualizer" / "app.js").read_text(encoding="utf-8")

    assert "native-heartbeat-recovery-governance" in control_panel_js
    assert "native heartbeat recovery governance" in control_panel_js
    assert "failure_recovery_governance" in control_panel_js
    assert "release-wrapper-native-heartbeat-recovery-governance" in visualizer_js
    assert "native heartbeat recovery governance" in visualizer_js


class _InstantFailingProvider:
    provider_id = "instant-failing-provider"
    is_local = True

    def complete(self, messages):
        return {
            "ok": False,
            "text": "",
            "model": self.provider_id,
            "local": True,
            "error": "RuntimeError: simulated provider unavailable",
        }


def test_wrapper_provider_failure_routes_native_recovery_governance_through_auto_repair(
    tmp_path: Path,
):
    project_root = make_project(tmp_path)
    sandbox_probe = project_root / "tests" / "heartbeat_supervisor_repair_auto_probe_test.py"
    sandbox_probe.parent.mkdir(parents=True, exist_ok=True)
    sandbox_probe.write_text("def test_heartbeat_supervisor_repair_auto_probe():\n    assert True\n", encoding="utf-8")
    client = TestClient(create_app(str(project_root)))
    provider = _InstantFailingProvider()
    client.app.state.provider_registry.register(provider)
    client.app.state.release_wrapper_runtime.hardware_scanner = _BoundedContextHardwareScanner()
    raw_session_id = "provider-failure-native-recovery-user"
    prompt = "Wrapped provider failure should route native recovery governance SECRET-NATIVE-RECOVERY."

    configured = client.post(
        "/ops/wrapper/release-health-heartbeat/supervisor/configure",
        json={
            "session_id": raw_session_id,
            "enabled": True,
            "interval_seconds": 1,
            "max_pulses_per_tick": 1,
            "schedule_immediately": True,
            "configured_by": "admin",
        },
    )
    assert configured.status_code == 200

    chat = client.post(
        "/v1/chat/completions",
        json={
            "model": provider.provider_id,
            "messages": [{"role": "user", "content": prompt}],
            "user": raw_session_id,
        },
    )
    assert chat.status_code == 502

    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": raw_session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": raw_session_id}).json()
    lifecycle = client.get("/ops/wrapper/session-lifecycle", params={"session_id": raw_session_id}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": raw_session_id}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]

    latest_interaction = runtime["latest_interaction"]
    project_heartbeat = runtime["project_heartbeat"]
    project_heartbeat_replay = runtime["project_heartbeat_replay"]
    replay_record = project_heartbeat_replay["latest_record"]
    recovery_governance = project_heartbeat["failure_recovery_governance"]

    assert project_heartbeat["status"] == "degraded"
    assert recovery_governance["status"] == "degraded-recovery-governed"
    assert recovery_governance["blocked_forward_pass"] is True
    assert recovery_governance["self_healing_route_available"] is True
    assert recovery_governance["admin_governance_required"] is True
    assert recovery_governance["sandbox_eval_required"] is True
    assert recovery_governance["rollback_required"] is True
    assert replay_record["failure_recovery_governance"]["blocked_forward_pass"] is True

    supervisor = runtime["release_health_heartbeat_supervisor"]
    pulse_loop = supervisor["latest_pulse"]["loop"]
    candidates = {
        candidate["gate_id"]: candidate
        for candidate in pulse_loop["whole_system_repair_candidates"]
    }
    native_candidate = candidates["native-project-heartbeat-recovery-governance"]
    assert native_candidate["status"] == "degraded-recovery-governed"
    assert native_candidate["recovery_governance"]["blocked_forward_pass"] is True
    assert "native-project-heartbeat-failure-recovery-governance" in native_candidate["target_surfaces"]

    repair_plan = latest_interaction["release_health_automatic_repair_plan"]
    envelopes = {
        envelope["gate_id"]: envelope
        for envelope in repair_plan["subsystem_repair_envelopes"]
    }
    native_envelope = envelopes["native-project-heartbeat-recovery-governance"]
    assert repair_plan["status"] == "completed-heartbeat-supervisor-repair"
    assert repair_plan["source_loop_id"] == pulse_loop["loop_id"]
    assert repair_plan["source_heartbeat_id"] == pulse_loop["latest_heartbeat_id"]
    assert repair_plan["readiness_evidence_run"]["command"] == (
        "pytest tests/heartbeat_supervisor_repair_auto_probe_test.py -q"
    )
    assert repair_plan["actions"]["admin_approval"]["status"] == "admin-approved"
    assert repair_plan["actions"]["shadow_eval_replay"]["status"] == "passed-shadow"
    assert repair_plan["actions"]["sandbox_tests"]["status"] == "passed"
    assert repair_plan["actions"]["apply"]["status"] == "applied-shadow-safe-file"
    assert repair_plan["actions"]["rollback"]["status"] == "rolled-back"
    assert native_envelope["honest_status_label"] == "completed-shadow-safe-file-rollback-verified"
    assert native_envelope["recovery_governance"]["blocked_forward_pass"] is True
    assert native_envelope["action_statuses"]["admin_approval"] == "admin-approved"
    assert native_envelope["action_statuses"]["shadow_eval_replay"] == "passed-shadow"
    assert native_envelope["action_statuses"]["sandbox_tests"] == "passed"
    assert native_envelope["action_statuses"]["apply"] == "applied-shadow-safe-file"
    assert native_envelope["action_statuses"]["rollback"] == "rolled-back"
    assert native_envelope["raw_content_included"] is False
    assert native_envelope["active_production_mutation_allowed"] is False
    assert native_envelope["active_production_mutated"] is False

    repair_history = supervisor["repair_history"]
    assert repair_history["latest_run_id"] == repair_plan["readiness_evidence_run"]["run_id"]
    assert repair_history["latest_subsystem_repair_envelopes"] == repair_plan["subsystem_repair_envelopes"]
    assert status_card["release_health_heartbeat_supervisor"]["repair_history"]["latest_run_id"] == (
        repair_plan["readiness_evidence_run"]["run_id"]
    )
    assert lifecycle["release_health_heartbeat_supervisor"]["repair_history"]["latest_run_id"] == (
        repair_plan["readiness_evidence_run"]["run_id"]
    )
    assert control_panel["release_wrapper_release_health_heartbeat_supervisor"]["repair_history"][
        "latest_subsystem_repair_envelopes"
    ] == repair_plan["subsystem_repair_envelopes"]

    replay_client = TestClient(create_app(str(project_root)))
    replayed_runtime = replay_client.get("/ops/wrapper/release-runtime", params={"session_id": raw_session_id}).json()
    assert replayed_runtime["project_heartbeat_replay"]["latest_record"]["failure_recovery_governance"][
        "blocked_forward_pass"
    ] is True
    assert replayed_runtime["release_health_heartbeat_supervisor"]["repair_history"]["latest_run_id"] == (
        repair_plan["readiness_evidence_run"]["run_id"]
    )

    serialized = json.dumps(
        {
            "runtime": runtime,
            "status_card": status_card,
            "lifecycle": lifecycle,
            "control_panel": control_panel,
        },
        sort_keys=True,
    )
    assert raw_session_id not in serialized
    assert prompt not in serialized
    assert "SECRET-NATIVE-RECOVERY" not in serialized
    assert str(project_root) not in serialized


def test_release_wrapper_live_use_executes_heartbeat_supervisor_repair_without_manual_endpoint(
    tmp_path: Path,
):
    project_root = make_project(tmp_path)
    sandbox_probe = project_root / "tests" / "heartbeat_supervisor_repair_auto_probe_test.py"
    sandbox_probe.parent.mkdir(parents=True, exist_ok=True)
    sandbox_probe.write_text("def test_heartbeat_supervisor_repair_auto_probe():\n    assert True\n", encoding="utf-8")
    client = TestClient(create_app(str(project_root)))
    raw_session_id = "heartbeat-supervisor-auto-repair-user"
    prompt = "Trigger automatic heartbeat supervisor repair SECRET-AUTO-HEALTH-REPAIR."

    configured = client.post(
        "/ops/wrapper/release-health-heartbeat/supervisor/configure",
        json={
            "session_id": raw_session_id,
            "enabled": True,
            "interval_seconds": 1,
            "max_pulses_per_tick": 1,
            "schedule_immediately": True,
            "configured_by": "admin",
        },
    )
    assert configured.status_code == 200

    chat = client.post(
        "/v1/chat/completions",
        json={
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
            "user": raw_session_id,
        },
    )
    assert chat.status_code == 200

    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": raw_session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": raw_session_id}).json()
    lifecycle = client.get("/ops/wrapper/session-lifecycle", params={"session_id": raw_session_id}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": raw_session_id}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]

    latest_interaction = runtime["latest_interaction"]
    supervisor = runtime["release_health_heartbeat_supervisor"]
    pulse = supervisor["latest_pulse"]
    pulse_loop = pulse["loop"]
    repair_queue = pulse_loop["repair_queue"]
    repair_plan = latest_interaction["release_health_automatic_repair_plan"]
    repair_history = supervisor["repair_history"]
    readiness_runner = status_card["release_readiness_evidence_runner"]
    action_lane = status_card["operator_action_lane"]
    self_repair = status_card["self_repair_ledger"]

    assert repair_queue["status"] == "proposal-routed"
    assert repair_plan["surface_id"] == "release-health-automatic-repair-envelope-plan"
    assert repair_plan["status"] == "completed-heartbeat-supervisor-repair"
    assert repair_plan["update_id"] == repair_queue["latest_update_id"]
    assert repair_plan["source_loop_id"] == pulse_loop["loop_id"]
    assert repair_plan["source_heartbeat_id"] == pulse_loop["latest_heartbeat_id"]
    assert repair_plan["readiness_evidence_run"]["status"] == "completed-heartbeat-supervisor-repair"
    assert repair_plan["readiness_evidence_run"]["command"] == (
        "pytest tests/heartbeat_supervisor_repair_auto_probe_test.py -q"
    )
    assert repair_plan["actions"]["admin_approval"]["status"] == "admin-approved"
    assert repair_plan["actions"]["shadow_eval_replay"]["status"] == "passed-shadow"
    assert repair_plan["actions"]["sandbox_tests"]["status"] == "passed"
    assert repair_plan["actions"]["sandbox_tests"]["passed"] is True
    assert repair_plan["actions"]["apply"]["status"] == "applied-shadow-safe-file"
    assert repair_plan["actions"]["rollback"]["status"] == "rolled-back"
    assert repair_plan["active_production_mutated"] is False
    assert repair_plan["raw_content_included"] is False
    assert repair_plan["subsystem_repair_envelope_count"] >= 1
    assert all(
        envelope["honest_status_label"] == "completed-shadow-safe-file-rollback-verified"
        for envelope in repair_plan["subsystem_repair_envelopes"]
    )

    assert repair_history["latest_run_id"] == repair_plan["readiness_evidence_run"]["run_id"]
    assert repair_history["latest_status"] == "completed-heartbeat-supervisor-repair"
    assert readiness_runner["latest_heartbeat_supervisor_repair_status"] == "completed-heartbeat-supervisor-repair"
    assert readiness_runner["latest_heartbeat_supervisor_repair_run_id"] == repair_plan["readiness_evidence_run"]["run_id"]
    assert action_lane["latest_action_statuses"]["release_health_heartbeat_supervisor_repair"] == (
        "completed-heartbeat-supervisor-repair"
    )
    assert action_lane["latest_action_statuses"]["admin_approval"] == "admin-approved"
    assert action_lane["latest_action_statuses"]["sandbox_tests"] == "passed"
    assert action_lane["latest_action_statuses"]["apply"] == "applied-shadow-safe-file"
    assert action_lane["latest_action_statuses"]["rollback"] == "rolled-back"
    assert self_repair["latest_action"] == "rollback"
    assert lifecycle["release_health_heartbeat_supervisor"]["repair_history"]["latest_run_id"] == (
        repair_plan["readiness_evidence_run"]["run_id"]
    )
    assert control_panel["release_wrapper_release_health_heartbeat_supervisor"]["repair_history"]["latest_run_id"] == (
        repair_plan["readiness_evidence_run"]["run_id"]
    )

    replay_client = TestClient(create_app(str(project_root)))
    replayed_runtime = replay_client.get("/ops/wrapper/release-runtime", params={"session_id": raw_session_id}).json()
    replayed_repair_history = replayed_runtime["release_health_heartbeat_supervisor"]["repair_history"]
    assert replayed_repair_history["latest_run_id"] == repair_plan["readiness_evidence_run"]["run_id"]
    assert replayed_repair_history["latest_status"] == "completed-heartbeat-supervisor-repair"

    serialized = json.dumps(
        {
            "runtime": runtime,
            "status_card": status_card,
            "lifecycle": lifecycle,
            "control_panel": control_panel,
        },
        sort_keys=True,
    )
    assert raw_session_id not in serialized
    assert prompt not in serialized
    assert "SECRET-AUTO-HEALTH-REPAIR" not in serialized
    assert str(project_root) not in serialized


def test_release_wrapper_heartbeat_supervisor_repair_run_uses_admin_eval_sandbox_apply_and_rollback(
    tmp_path: Path,
):
    project_root = make_project(tmp_path)
    sandbox_probe = project_root / "tests" / "heartbeat_supervisor_repair_probe_test.py"
    sandbox_probe.parent.mkdir(parents=True, exist_ok=True)
    sandbox_probe.write_text("def test_heartbeat_supervisor_repair_probe():\n    assert True\n", encoding="utf-8")
    client = TestClient(create_app(str(project_root)))
    raw_session_id = "heartbeat-supervisor-repair-user"
    prompt = "Trigger heartbeat repair from wrapper use SECRET-HEALTH-REPAIR."
    sandbox_command = "pytest tests/heartbeat_supervisor_repair_probe_test.py -q"

    configured = client.post(
        "/ops/wrapper/release-health-heartbeat/supervisor/configure",
        json={
            "session_id": raw_session_id,
            "enabled": True,
            "interval_seconds": 1,
            "max_pulses_per_tick": 1,
            "schedule_immediately": True,
            "configured_by": "admin",
        },
    )
    assert configured.status_code == 200

    chat = client.post(
        "/v1/chat/completions",
        json={
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
            "user": raw_session_id,
        },
    )
    assert chat.status_code == 200

    runtime_before = client.get("/ops/wrapper/release-runtime", params={"session_id": raw_session_id}).json()
    supervisor = runtime_before["release_health_heartbeat_supervisor"]
    pulse = supervisor["latest_pulse"]
    repair_queue = pulse["loop"]["repair_queue"]
    update_id = repair_queue["latest_update_id"]
    queued_target_surfaces = set(repair_queue["target_surfaces"])

    assert repair_queue["status"] == "proposal-routed"
    assert update_id.startswith("update::release-wrapper-health-heartbeat-loop::")
    assert {
        "federation-runtime",
        "shadow-learning",
    }.issubset(queued_target_surfaces)

    repair = client.post(
        "/ops/wrapper/release-health-heartbeat/supervisor/repair-run",
        json={
            "session_id": raw_session_id,
            "command": sandbox_command,
            "timeout_seconds": 30,
            "approved_by": "admin",
            "approval_ref": "operator-review::heartbeat-supervisor-repair",
        },
    )

    assert repair.status_code == 200
    repair_payload = repair.json()
    actions = repair_payload["actions"]
    readiness_run = repair_payload["readiness_evidence_run"]
    subsystem_envelopes = repair_payload["subsystem_repair_envelopes"]

    assert repair_payload["surface_id"] == "release-health-heartbeat-supervisor-repair-run"
    assert repair_payload["status"] == "completed"
    assert repair_payload["update_id"] == update_id
    assert repair_payload["source_pulse_id"] == pulse["pulse_id"]
    assert repair_payload["source_loop_id"] == pulse["loop_id"]
    assert repair_payload["raw_content_included"] is False
    assert repair_payload["active_production_mutated"] is False
    assert actions["admin_approval"]["status"] == "admin-approved"
    assert actions["shadow_eval_replay"]["status"] == "passed-shadow"
    assert actions["shadow_eval_replay"]["promotion_allowed"] is True
    assert actions["sandbox_tests"]["status"] == "passed"
    assert actions["sandbox_tests"]["passed"] is True
    assert actions["sandbox_tests"]["sandbox"]["active_project_root_mutated"] is False
    assert actions["apply"]["status"] == "applied-shadow-safe-file"
    assert actions["apply"]["active_production_mutated"] is False
    assert actions["apply"]["test_results"][0]["evidence_ref"] == actions["sandbox_tests"]["evidence_ref"]
    assert actions["rollback"]["status"] == "rolled-back"
    assert actions["rollback"]["rollback_restored"] is True
    assert readiness_run["status"] == "completed-heartbeat-supervisor-repair"
    assert readiness_run["active_production_mutated"] is False
    assert repair_payload["subsystem_repair_envelope_count"] == len(subsystem_envelopes)
    assert subsystem_envelopes
    assert {
        "federation-runtime",
        "shadow-learning",
    }.issubset({surface for envelope in subsystem_envelopes for surface in envelope["target_surfaces"]})
    assert all(envelope["honest_status_label"] == "completed-shadow-safe-file-rollback-verified" for envelope in subsystem_envelopes)
    assert all(envelope["action_statuses"]["admin_approval"] == "admin-approved" for envelope in subsystem_envelopes)
    assert all(envelope["action_statuses"]["shadow_eval_replay"] == "passed-shadow" for envelope in subsystem_envelopes)
    assert all(envelope["action_statuses"]["sandbox_tests"] == "passed" for envelope in subsystem_envelopes)
    assert all(envelope["action_statuses"]["apply"] == "applied-shadow-safe-file" for envelope in subsystem_envelopes)
    assert all(envelope["action_statuses"]["rollback"] == "rolled-back" for envelope in subsystem_envelopes)
    assert all(envelope["raw_content_included"] is False for envelope in subsystem_envelopes)
    assert all(envelope["active_production_mutation_allowed"] is False for envelope in subsystem_envelopes)
    assert all(envelope["active_production_mutated"] is False for envelope in subsystem_envelopes)
    assert readiness_run["subsystem_repair_envelopes"] == subsystem_envelopes
    assert readiness_run["subsystem_repair_envelope_count"] == len(subsystem_envelopes)

    proposal_summary = client.get("/ops/brain/autonomous-updates").json()
    proposal = next(item for item in proposal_summary["proposals"] if item["update_id"] == update_id)
    assert any(ref.startswith("eval::release-wrapper-runtime::") for ref in proposal["eval_refs"])
    assert any(ref.startswith("evals-ao-artifact::release-wrapper::") for ref in proposal["eval_refs"])
    assert proposal["latest_eval_replay"]["status"] == "passed-shadow"
    assert queued_target_surfaces.issubset(set(proposal["target_surfaces"]))
    registry = client.get("/ops/brain/eval-registry", params={"limit": 500}).json()
    repair_suite = next(
        suite
        for suite in registry["suites"]
        if suite["suite_id"] == next(ref for ref in proposal["eval_refs"] if ref.startswith("eval::release-wrapper-runtime::"))
    )
    assert queued_target_surfaces.issubset(set(repair_suite["target_surfaces"]))

    status_card = client.get("/ops/wrapper/status-card", params={"session_id": raw_session_id}).json()
    action_lane = status_card["operator_action_lane"]
    self_repair = status_card["self_repair_ledger"]
    assert action_lane["run_release_health_heartbeat_supervisor_repair_ref"] == (
        "/ops/wrapper/release-health-heartbeat/supervisor/repair-run"
    )
    assert (
        action_lane["latest_action_statuses"]["release_health_heartbeat_supervisor_repair"]
        == "completed-heartbeat-supervisor-repair"
    )
    assert action_lane["latest_action_statuses"]["admin_approval"] == "admin-approved"
    assert action_lane["latest_action_statuses"]["sandbox_tests"] == "passed"
    assert action_lane["latest_action_statuses"]["apply"] == "applied-shadow-safe-file"
    assert action_lane["latest_action_statuses"]["rollback"] == "rolled-back"
    assert self_repair["action_counts"]["admin_approval"] >= 1
    assert self_repair["action_counts"]["sandbox_tests"] >= 1
    assert self_repair["action_counts"]["apply"] >= 1
    assert self_repair["action_counts"]["rollback"] >= 1
    assert self_repair["latest_action"] == "rollback"
    assert self_repair["latest_status"] == "rolled-back"
    runtime_after_repair = client.get("/ops/wrapper/release-runtime", params={"session_id": raw_session_id}).json()
    lifecycle_after_repair = client.get("/ops/wrapper/session-lifecycle", params={"session_id": raw_session_id}).json()
    visualizer_after_repair = client.get("/ops/brain/visualizer/state", params={"session_id": raw_session_id}).json()
    control_panel_after_repair = visualizer_after_repair["overlay_state"]["control_panel"]
    repair_history = runtime_after_repair["release_health_heartbeat_supervisor"]["repair_history"]

    assert repair_history["repair_count"] >= 1
    assert repair_history["latest_status"] == "completed-heartbeat-supervisor-repair"
    assert repair_history["latest_run_id"] == readiness_run["run_id"]
    assert repair_history["latest_update_id"] == update_id
    assert repair_history["latest_pulse_id"] == pulse["pulse_id"]
    assert repair_history["latest_loop_id"] == pulse["loop_id"]
    assert repair_history["latest_heartbeat_id"] == pulse["heartbeat_id"]
    assert repair_history["latest_subsystem_repair_envelope_count"] == len(subsystem_envelopes)
    assert repair_history["latest_subsystem_repair_envelopes"] == subsystem_envelopes
    assert repair_history["active_production_mutated"] is False
    assert repair_history["raw_content_included"] is False
    assert repair_history["active_production_mutation_allowed"] is False
    assert status_card["release_health_heartbeat_supervisor"]["repair_history"]["latest_run_id"] == (
        readiness_run["run_id"]
    )
    assert lifecycle_after_repair["release_health_heartbeat_supervisor"]["repair_history"]["latest_run_id"] == (
        readiness_run["run_id"]
    )
    assert control_panel_after_repair["release_wrapper_release_health_heartbeat_supervisor"]["repair_history"][
        "latest_run_id"
    ] == readiness_run["run_id"]
    assert control_panel_after_repair["release_wrapper_release_health_heartbeat_supervisor"]["repair_history"][
        "latest_subsystem_repair_envelope_count"
    ] == len(subsystem_envelopes)
    assert control_panel_after_repair["release_wrapper_release_health_heartbeat_supervisor"]["repair_history"][
        "latest_subsystem_repair_envelopes"
    ] == subsystem_envelopes

    replay_client = TestClient(create_app(str(project_root)))
    replayed_runtime = replay_client.get("/ops/wrapper/release-runtime", params={"session_id": raw_session_id}).json()
    replayed_history = replayed_runtime["release_health_heartbeat_supervisor"]["repair_history"]
    assert replayed_history["latest_run_id"] == readiness_run["run_id"]
    assert replayed_history["latest_update_id"] == update_id
    assert replayed_history["latest_pulse_id"] == pulse["pulse_id"]
    assert replayed_history["latest_subsystem_repair_envelope_count"] == len(subsystem_envelopes)

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    visualizer_js = (project_root / "ui" / "visualizer" / "app.js").read_text(encoding="utf-8")
    assert "run_release_health_heartbeat_supervisor_repair" in app_js
    assert "Run Health Repair" in app_js
    assert "subsystem repair envelopes" in app_js
    assert "health repair envelopes" in visualizer_js

    serialized = json.dumps(
        {
            "repair": repair_payload,
            "repair_history": repair_history,
            "status_card": status_card,
            "self_repair": self_repair,
        },
        sort_keys=True,
    )
    assert raw_session_id not in serialized
    assert prompt not in serialized
    assert "SECRET-HEALTH-REPAIR" not in serialized
    assert str(project_root) not in serialized


def test_release_wrapper_boot_supervisor_manifest_replays_in_runtime_status_and_control_surfaces(tmp_path: Path):
    project_root = make_project(tmp_path)
    boot_manifest_path = project_root / "artifacts" / "release-wrapper-runtime" / "boot-manifest.json"
    boot_manifest_path.parent.mkdir(parents=True, exist_ok=True)
    boot_manifest_path.write_text(
        json.dumps(
            {
                "schema_version": "nexusnet-release-wrapper-boot-manifest-v1",
                "surface_id": "release-wrapper-boot-supervisor",
                "manifest_id": "release-wrapper-boot::manifest-digest",
                "generated_at": "2026-06-30T12:00:00+00:00",
                "authority": "NexusBrain",
                "status_label": "LOCKED CANON",
                "status": "boot-smoke-passed",
                "product_surface": "wrapper",
                "base_url": "http://127.0.0.1:8777",
                "server": {
                    "host": "127.0.0.1",
                    "port": 8777,
                    "pid": 4242,
                    "app_target": "nexus.api.app:app",
                },
                "session_id": "release-wrapper-boot-raw-session",
                "session_ref_digest": "sha256:boot-session-digest",
                "readiness_command": "pytest SECRET-BOOT-COMMAND tests/test_release_wrapper_cli.py -q",
                "readiness_command_ref": "sha256:readiness-command-digest",
                "endpoints": {
                    "release_runtime": "http://127.0.0.1:8777/ops/wrapper/release-runtime",
                    "release_readiness": "http://127.0.0.1:8777/ops/wrapper/release-readiness",
                    "status_card": "http://127.0.0.1:8777/ops/wrapper/status-card",
                },
                "checks": [
                    {
                        "check_id": "api-health",
                        "status": "pass",
                        "endpoint": "/health",
                        "detail": "SECRET-BOOT-CHECK should be redacted",
                        "raw_content_included": False,
                    },
                    {
                        "check_id": "wrapper-chat",
                        "status": "pass",
                        "endpoint": "/v1/chat/completions",
                        "raw_content_included": False,
                    },
                    {
                        "check_id": "forward-pass-coverage",
                        "status": "pass",
                        "endpoint": "/ops/wrapper/release-runtime",
                        "raw_content_included": False,
                    },
                    {
                        "check_id": "federated-peer-import",
                        "status": "pass",
                        "endpoint": "/ops/wrapper/federated-packets/import",
                        "raw_content_included": False,
                    },
                    {
                        "check_id": "federated-peer-inbox",
                        "status": "pass",
                        "endpoint": "/ops/wrapper/federated-packets/imports",
                        "raw_content_included": False,
                    },
                    {
                        "check_id": "readiness-runner",
                        "status": "pass",
                        "endpoint": "/ops/wrapper/release-readiness/run",
                        "raw_content_included": False,
                    },
                    {
                        "check_id": "release-product-path",
                        "status": "pass",
                        "endpoint": "/ops/wrapper/status-card",
                        "raw_content_included": False,
                    },
                ],
                "evidence": {
                    "forward_pass_coverage": {
                        "latest_status": "covered",
                        "receipt_count": 1,
                        "latest_receipt_id": "fpr::boot",
                        "raw_content_included": False,
                    },
                    "release_readiness_evidence_runner": {
                        "latest_status": "completed",
                        "active_production_mutated": False,
                        "latest_run_id": "run::boot",
                    },
                    "release_readiness": {"go_no_go": "go", "blocker_count": 0},
                    "peer_federation_reject": {
                        "status": "quarantined-rejected",
                        "import_id": "fed-import::rejected-boot",
                        "security_envelope_verified": False,
                        "assimilation_shadow_captured": False,
                        "global_growth_shadow_captured": False,
                        "active_production_mutation_allowed": False,
                        "raw_content_included": False,
                        "contains_personal_data": False,
                    },
                    "peer_federation_import": {
                        "status": "quarantined-shadow-accepted",
                        "import_id": "fed-import::boot",
                        "security_envelope_verified": True,
                        "assimilation_shadow_captured": True,
                        "global_growth_shadow_captured": True,
                        "active_production_mutation_allowed": False,
                        "raw_content_included": False,
                        "contains_personal_data": False,
                    },
                    "release_product_path": {
                        "entrypoint_runtime_state": "live-bound",
                        "global_growth_users": 1,
                        "training_ready_node_count": 1,
                        "federated_packet_count": 1,
                        "federated_import_count": 2,
                        "federated_import_accepted_count": 1,
                        "federated_import_rejected_count": 1,
                        "federated_import_degraded_count": 0,
                        "peer_shadow_proposal_count": 1,
                        "production_spine_packet_count": 1,
                        "dream_research_item_count": 1,
                        "dream_research_episode_count": 1,
                        "autonomous_update_proposal_count": 2,
                        "self_repair_action_count": 4,
                        "latest_self_repair_action": "rollback",
                        "admin_action_statuses": {
                            "admin_approval": "admin-approved",
                            "sandbox_tests": "passed",
                            "apply": "applied-shadow-safe-file",
                            "rollback": "rolled-back",
                        },
                        "native_runtime_growth_governance": {
                            "surface_id": "native-runtime-growth-governance",
                            "status_label": "LOCKED CANON",
                            "status": "rolled-back",
                            "native_hive_runtime_growth": True,
                            "proposal_update_id": "update::boot-native-growth",
                            "runtime_growth_receipt_id": "runtime-growth::boot-native-growth",
                            "latest_action_statuses": {
                                "proposal": "proposed",
                                "admin_approval": "admin-approved",
                                "shadow_eval_replay": "passed-shadow",
                                "sandbox_tests": "passed",
                                "apply": "applied-shadow-safe-file",
                                "rollback": "rolled-back",
                                "readiness_runner": "completed",
                            },
                            "latest_runner_status": "completed",
                            "latest_runner_run_id": "run::boot",
                            "active_production_mutated": False,
                            "active_production_mutation_allowed": False,
                            "raw_content_included": False,
                        },
                        "failure_learning": {
                            "captured_count": 0,
                            "degraded_count": 0,
                            "latest_status": "not-run",
                        },
                        "active_production_mutation_allowed": False,
                        "raw_content_included": False,
                    },
                },
                "raw_content_included": False,
                "privacy_boundary": "sanitized-boot-refs-status-counts-digests-only-no-raw-prompts-outputs-session-ids",
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    client = TestClient(create_app(str(project_root)))

    runtime = client.get("/ops/wrapper/release-runtime").json()
    readiness = client.get("/ops/wrapper/release-readiness").json()
    status_card = client.get("/ops/wrapper/status-card").json()
    lifecycle = client.get("/ops/wrapper/session-lifecycle").json()
    visualizer = client.get("/ops/brain/visualizer/state").json()
    control_panel = visualizer["overlay_state"]["control_panel"]

    boot = runtime["boot_supervisor"]
    assert boot["surface_id"] == "release-wrapper-boot-supervisor"
    assert boot["runtime_state"] == "live-evidence"
    assert boot["latest_status"] == "boot-smoke-passed"
    assert boot["pass_count"] == 7
    assert boot["failed_count"] == 0
    assert boot["manifest_ref"] == "artifacts/release-wrapper-runtime/boot-manifest.json"
    assert boot["server"] == {
        "host": "127.0.0.1",
        "port": 8777,
        "app_target": "nexus.api.app:app",
    }
    assert boot["evidence"]["release_readiness"]["go_no_go"] == "go"
    assert boot["evidence"]["forward_pass_coverage"]["latest_status"] == "covered"
    assert boot["evidence"]["release_readiness_evidence_runner"]["active_production_mutated"] is False
    assert boot["evidence"]["peer_federation_reject"]["status"] == "quarantined-rejected"
    assert boot["evidence"]["peer_federation_reject"]["security_envelope_verified"] is False
    assert boot["evidence"]["peer_federation_import"]["status"] == "quarantined-shadow-accepted"
    assert boot["evidence"]["peer_federation_import"]["security_envelope_verified"] is True
    assert boot["evidence"]["release_product_path"]["global_growth_users"] == 1
    assert boot["evidence"]["release_product_path"]["federated_packet_count"] == 1
    assert boot["evidence"]["release_product_path"]["federated_import_count"] == 2
    assert boot["evidence"]["release_product_path"]["federated_import_accepted_count"] == 1
    assert boot["evidence"]["release_product_path"]["federated_import_rejected_count"] == 1
    assert boot["evidence"]["release_product_path"]["peer_shadow_proposal_count"] == 1
    assert boot["evidence"]["release_product_path"]["dream_research_item_count"] == 1
    assert boot["evidence"]["release_product_path"]["admin_action_statuses"]["apply"] == "applied-shadow-safe-file"
    assert boot["evidence"]["release_product_path"]["native_runtime_growth_governance"]["status"] == "rolled-back"
    assert (
        boot["evidence"]["release_product_path"]["native_runtime_growth_governance"]["latest_action_statuses"][
            "readiness_runner"
        ]
        == "completed"
    )
    assert (
        boot["evidence"]["release_product_path"]["native_runtime_growth_governance"]["latest_runner_run_id"]
        == "run::boot"
    )
    assert boot["evidence"]["release_product_path"]["native_runtime_growth_governance"]["raw_content_included"] is False
    assert boot["evidence"]["release_product_path"]["failure_learning"]["latest_status"] == "not-run"
    assert boot["evidence"]["release_product_path"]["raw_content_included"] is False
    assert boot["raw_content_included"] is False

    assert readiness["boot"]["boot_supervisor_ref"] == "artifacts/release-wrapper-runtime/boot-manifest.json"
    assert readiness["evidence"]["boot_supervisor"]["latest_status"] == "boot-smoke-passed"
    assert status_card["boot_supervisor"]["pass_count"] == 7
    assert status_card["endpoint_refs"]["boot_manifest"] == "artifacts/release-wrapper-runtime/boot-manifest.json"
    assert lifecycle["boot_supervisor"]["latest_status"] == "boot-smoke-passed"
    assert control_panel["release_wrapper_runtime"]["boot_supervisor"]["latest_status"] == "boot-smoke-passed"
    assert control_panel["release_wrapper_boot_supervisor"]["pass_count"] == 7

    control_panel_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    visualizer_js = (project_root / "ui" / "visualizer" / "app.js").read_text(encoding="utf-8")
    assert "Release Harness boot supervisor" in control_panel_js
    assert "release-wrapper-boot-supervisor" in control_panel_js
    assert "boot_supervisor" in control_panel_js
    assert "release product path" in control_panel_js
    assert "product-path federation" in control_panel_js
    assert "Harness boot supervisor" in visualizer_js
    assert "release-wrapper-boot-supervisor" in visualizer_js
    assert "Harness product path" in visualizer_js

    serialized = json.dumps(
        {
            "runtime": runtime,
            "readiness": readiness,
            "status_card": status_card,
            "lifecycle": lifecycle,
            "visualizer_control_panel": control_panel,
        }
    )
    assert "release-wrapper-boot-raw-session" not in serialized
    assert "SECRET-BOOT-COMMAND" not in serialized
    assert "SECRET-BOOT-CHECK" not in serialized


def test_release_wrapper_boot_supervisor_run_generates_manifest_from_live_product_path(tmp_path: Path):
    project_root = make_project(tmp_path)
    sandbox_probe = project_root / "tests" / "release_wrapper_boot_supervisor_run_probe_test.py"
    sandbox_probe.parent.mkdir(parents=True, exist_ok=True)
    sandbox_probe.write_text(
        "def test_release_wrapper_boot_supervisor_run_probe():\n    assert True\n",
        encoding="utf-8",
    )
    client = TestClient(create_app(str(project_root)))
    session_id = "release-wrapper-boot-run-raw-session"
    prompt = "Generate live boot supervisor evidence without leaking SECRET-BOOT-RUN."

    chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    assert chat.status_code == 200
    packet = client.get("/ops/wrapper/federated-packets", params={"session_id": session_id}).json()["latest_packet"]
    imported = client.post(
        "/ops/wrapper/federated-packets/import",
        json={"session_id": session_id, "peer_node_id": "boot-supervisor-run-peer", "packet": packet},
    ).json()
    assert imported["status"] == "quarantined-shadow-accepted"
    runner = client.post(
        "/ops/wrapper/release-readiness/run",
        json={
            "session_id": session_id,
            "command": "pytest tests/release_wrapper_boot_supervisor_run_probe_test.py -q",
            "timeout_seconds": 30,
            "approved_by": "admin",
            "approval_ref": "operator-review::boot-supervisor-run",
        },
    )
    assert runner.status_code == 200
    assert runner.json()["status"] == "completed"

    before = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    assert before["boot_supervisor"]["latest_status"] == "boot-smoke-passed"
    assert before["initial_release_supervisor"]["latest_status"] == "initial-release-go"
    assert before["production_spine_release_lifecycle"]["latest_run"]["status"] == (
        "approved-shadow-release-lifecycle"
    )

    run_response = client.post(
        "/ops/wrapper/boot-supervisor/run",
        json={
            "session_id": session_id,
            "base_url": "http://127.0.0.1:0",
            "host": "127.0.0.1",
            "port": 0,
            "pid": 12345,
            "readiness_command": "pytest tests/release_wrapper_boot_supervisor_run_probe_test.py -q SECRET-BOOT-COMMAND",
        },
    )

    assert run_response.status_code == 200
    manifest = run_response.json()
    assert manifest["schema_version"] == "nexusnet-release-wrapper-boot-manifest-v1"
    assert manifest["surface_id"] == "release-wrapper-boot-supervisor"
    assert manifest["status"] == "boot-smoke-passed"
    assert manifest["manifest_ref"] == "artifacts/release-wrapper-runtime/boot-manifest.json"
    assert manifest["server"] == {
        "host": "127.0.0.1",
        "port": 0,
        "pid": 12345,
        "app_target": "nexus.api.app:app",
    }
    assert manifest["session_ref_digest"].startswith("sha256:")
    checks = {check["check_id"]: check for check in manifest["checks"]}
    assert {
        "api-health",
        "release-runtime",
        "forward-pass-coverage",
        "federated-peer-import",
        "readiness-runner",
        "release-readiness",
        "status-card",
        "release-product-path",
        "boot-manifest-persisted",
    }.issubset(checks)
    assert all(check["status"] == "pass" for check in checks.values())

    evidence = manifest["evidence"]
    assert evidence["forward_pass_coverage"]["latest_status"] == "covered"
    assert evidence["release_readiness_evidence_runner"]["latest_status"] == "completed"
    assert evidence["release_readiness"]["go_no_go"] == "go"
    assert evidence["peer_federation_import"]["status"] == "quarantined-shadow-accepted"
    assert evidence["release_product_path"]["entrypoint_runtime_state"] == "live-bound"
    assert evidence["release_product_path"]["federated_import_accepted_count"] >= 1
    assert evidence["release_product_path"]["admin_action_statuses"]["apply"] == "applied-shadow-safe-file"
    assert evidence["release_product_path"]["admin_action_statuses"]["rollback"] == "rolled-back"
    assert evidence["release_product_path"]["active_production_mutation_allowed"] is False
    assert evidence["release_product_path"]["raw_content_included"] is False
    assert manifest["active_production_mutation_allowed"] is False
    assert manifest["raw_content_included"] is False
    assert Path(manifest["artifact_path"]).exists()

    restarted = TestClient(create_app(str(project_root)))
    runtime = restarted.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    readiness = restarted.get("/ops/wrapper/release-readiness", params={"session_id": session_id}).json()
    status_card = restarted.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    lifecycle = restarted.get("/ops/wrapper/session-lifecycle", params={"session_id": session_id}).json()
    visualizer = restarted.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]

    assert runtime["boot_supervisor"]["latest_status"] == "boot-smoke-passed"
    assert runtime["boot_supervisor"]["runtime_state"] == "live-evidence"
    assert runtime["boot_supervisor"]["evidence"]["release_product_path"]["federated_import_accepted_count"] >= 1
    assert readiness["boot"]["boot_supervisor_status"] == "boot-smoke-passed"
    assert readiness["evidence"]["boot_supervisor"]["latest_status"] == "boot-smoke-passed"
    assert status_card["endpoint_refs"]["boot_supervisor_run"] == "/ops/wrapper/boot-supervisor/run"
    assert status_card["operator_action_lane"]["run_boot_supervisor_ref"] == "/ops/wrapper/boot-supervisor/run"
    assert lifecycle["endpoint_refs"]["boot_supervisor_run"] == "/ops/wrapper/boot-supervisor/run"
    assert lifecycle["boot_supervisor"]["latest_status"] == "boot-smoke-passed"
    assert control_panel["release_wrapper_runtime"]["boot_supervisor"]["latest_status"] == "boot-smoke-passed"

    control_panel_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "/ops/wrapper/boot-supervisor/run" in control_panel_js
    assert "Run Boot Supervisor" in control_panel_js

    serialized = json.dumps(
        {
            "manifest": manifest,
            "runtime": runtime,
            "readiness": readiness,
            "status_card": status_card,
            "lifecycle": lifecycle,
            "control_panel": control_panel,
        },
        sort_keys=True,
    )
    assert session_id not in serialized
    assert prompt not in serialized
    assert "SECRET-BOOT-RUN" not in serialized
    assert "SECRET-BOOT-COMMAND" not in serialized


def test_initial_release_supervisor_runs_whole_project_release_path(tmp_path: Path):
    project_root = make_project(tmp_path)
    sandbox_probe = project_root / "tests" / "initial_release_supervisor_probe_test.py"
    sandbox_probe.parent.mkdir(parents=True, exist_ok=True)
    sandbox_probe.write_text("def test_initial_release_supervisor_probe():\n    assert True\n", encoding="utf-8")
    stale_smoke_path = project_root / "runtime" / "artifacts" / "release-wrapper-runtime" / "release-product-smoke.json"
    stale_smoke_path.parent.mkdir(parents=True, exist_ok=True)
    stale_smoke_path.write_text(
        json.dumps(
            {
                "schema_version": "nexusnet-release-wrapper-product-smoke-v1",
                "surface_id": "release-wrapper-product-smoke",
                "status": "release-product-smoke-blocked",
                "honest_status_label": "release-product-smoke-blocked",
                "runtime_state": "blocked-evidence",
                "failed_count": 1,
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
                "active_production_mutated": False,
                "checks": [
                    {
                        "check_id": "release-readiness",
                        "status": "blocked",
                        "raw_content_included": False,
                    }
                ],
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    relative_project_root = Path(os.path.relpath(project_root, Path.cwd()))
    client = TestClient(create_app(str(relative_project_root)))
    session_id = "initial-release-supervisor-user"

    response = client.post(
        "/ops/wrapper/initial-release-supervisor/run",
        json={
            "session_id": session_id,
            "base_url": "http://127.0.0.1:0",
            "host": "127.0.0.1",
            "port": 0,
            "pid": 24680,
            "readiness_command": "pytest tests/initial_release_supervisor_probe_test.py -q",
            "timeout_seconds": 30,
            "approved_by": "initial-release-admin",
            "approval_ref": "operator-review::initial-release-supervisor",
        },
    )

    assert response.status_code == 200
    manifest = response.json()
    actions = manifest["actions"]

    assert manifest["surface_id"] == "release-wrapper-initial-release-supervisor"
    assert manifest["status"] == "initial-release-go"
    assert manifest["product_scope"] == "whole-system"
    assert manifest["raw_content_included"] is False
    assert manifest["active_production_mutation_allowed"] is False
    assert manifest["release_readiness"]["go_no_go"] == "go"
    assert manifest["boot_supervisor"]["status"] == "boot-smoke-passed"
    assert manifest["boot_supervisor"]["failed_count"] == 0
    assert actions["wrapper_interactions"]["status"] == "recorded"
    assert actions["wrapper_interactions"]["interaction_count"] == 3
    assert actions["federated_packet_import"]["status"] == "quarantined-shadow-accepted"
    assert actions["domain_expert_growth_admin_replay"]["status"] == "recorded"
    assert actions["release_readiness_runner"]["status"] == "completed"
    assert actions["release_health_heartbeat_supervisor"]["status"] == "enabled"
    assert actions["release_health_heartbeat_supervisor"]["pulse_count"] >= 1
    assert actions["release_health_heartbeat_supervisor"]["latest_pulse_id"]
    heartbeat_repair = actions["release_health_heartbeat_supervisor_repair"]
    assert heartbeat_repair["status"] == "completed"
    assert heartbeat_repair["source_pulse_id"] == actions["release_health_heartbeat_supervisor"]["latest_pulse_id"]
    assert heartbeat_repair["readiness_evidence_status"] == "completed-heartbeat-supervisor-repair"
    assert heartbeat_repair["active_production_mutated"] is False
    assert heartbeat_repair["raw_content_included"] is False
    assert heartbeat_repair["active_production_mutation_allowed"] is False
    assert heartbeat_repair["action_statuses"]["admin_approval"] == "admin-approved"
    assert heartbeat_repair["action_statuses"]["shadow_eval_replay"] == "passed-shadow"
    assert heartbeat_repair["action_statuses"]["sandbox_tests"] == "passed"
    assert heartbeat_repair["action_statuses"]["apply"] == "applied-shadow-safe-file"
    assert heartbeat_repair["action_statuses"]["rollback"] == "rolled-back"
    assert manifest["action_statuses"]["release_health_heartbeat_supervisor_repair"] == "completed"
    assert actions["production_spine_release_lifecycle"]["status"] == "approved-shadow-release-lifecycle"
    assert actions["production_spine_release_lifecycle"]["step_counts"]["blocked"] == 0
    assert actions["production_spine_release_lifecycle_rollback"]["status"] == "rolled-back"
    assert actions["boot_supervisor"]["status"] == "boot-smoke-passed"
    assert actions["native_hive_heartbeat_history"]["status"] == "fresh"
    assert actions["native_hive_heartbeat_history"]["latest_fresh"] is True
    assert actions["native_hive_heartbeat_history"]["artifact_ref"] == (
        "release-wrapper-runtime/native-hive-heartbeats.jsonl"
    )
    assert actions["native_hive_heartbeat_history"]["raw_content_included"] is False
    assert Path(manifest["artifact_path"]).exists()

    readiness = client.get("/ops/wrapper/release-readiness", params={"session_id": session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    lifecycle = client.get("/ops/wrapper/session-lifecycle", params={"session_id": session_id}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]
    matrix = runtime["whole_system_forward_pass_enforcement_matrix"]
    rows = {row["entrypoint_id"]: row for row in matrix["entrypoints"]}
    readiness_checks = {check["check_id"]: check for check in readiness["readiness_checks"]}
    handoff = runtime["domain_teacher_eval_handoff"]

    assert readiness["go_no_go"] == "go"
    assert handoff["latest_admin_eval_replay_status"] == "passed-shadow"
    assert handoff["latest_admin_promotion_decision"] in {"approved", "shadow"}
    assert handoff["latest_sandbox_takeover_evidence_status"] == "recorded"
    assert handoff["latest_teacher_evidence_bundle_id"]
    assert handoff["latest_takeover_scorecard_id"]
    assert handoff["latest_growth_archive_candidate_id"]
    assert readiness_checks["domain-expert-growth-sandbox-takeover-evidence"]["status"] == "pass"
    assert readiness_checks["domain-expert-growth-sandbox-takeover-evidence"]["promotion_decision"] in {
        "approved",
        "shadow",
    }
    assert status_card["operator_action_lane"]["run_initial_release_supervisor_ref"] == (
        "/ops/wrapper/initial-release-supervisor/run"
    )
    assert (
        status_card["operator_action_lane"]["latest_action_statuses"][
            "release_health_heartbeat_supervisor_repair"
        ]
        == "completed-heartbeat-supervisor-repair"
    )
    assert matrix["coverage_status"] == "covered"
    assert rows["boot_supervisor"]["status"] == "covered"
    assert rows["boot_supervisor"]["honest_status_label"] == "covered"
    assert rows["initial_release_supervisor"]["status"] == "covered"
    assert rows["initial_release_supervisor"]["honest_status_label"] == "covered"
    assert rows["production_spine_release_lifecycle"]["status"] == "covered"
    assert rows["production_spine_release_lifecycle"]["honest_status_label"] == "covered"
    assert rows["production_spine_lifecycle_rollback"]["status"] == "covered"
    assert rows["production_spine_lifecycle_rollback"]["honest_status_label"] == "covered"
    assert readiness_checks["whole-system-forward-pass-enforcement-matrix"]["coverage_status"] == "covered"
    assert status_card["whole_system_forward_pass_enforcement_matrix"]["coverage_status"] == "covered"
    assert lifecycle["whole_system_forward_pass_enforcement_matrix"]["coverage_status"] == "covered"
    assert control_panel["release_wrapper_forward_pass_enforcement_matrix"]["coverage_status"] == "covered"
    assert runtime["initial_release_supervisor"]["action_statuses"]["native_hive_heartbeat_history"] == "fresh"
    assert runtime["initial_release_supervisor"]["action_statuses"][
        "release_health_heartbeat_supervisor_repair"
    ] == "completed"
    assert runtime["initial_release_supervisor"]["actions"][
        "release_health_heartbeat_supervisor_repair"
    ]["action_statuses"]["rollback"] == "rolled-back"
    assert runtime["native_hive_heartbeat"]["heartbeat_history"]["latest_fresh"] is True

    control_panel_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    serialized = json.dumps(manifest, sort_keys=True)
    assert "initial-release-supervisor" in control_panel_js
    assert "Run Health Repair" in control_panel_js
    assert session_id not in serialized
    assert "initial-release-admin" not in serialized


def test_release_product_smoke_runner_records_sanitized_initial_release_gate_artifact(tmp_path: Path):
    project_root = make_project(tmp_path)
    sandbox_probe = project_root / "tests" / "release_product_smoke_probe_test.py"
    sandbox_probe.parent.mkdir(parents=True, exist_ok=True)
    sandbox_probe.write_text("def test_release_product_smoke_probe():\n    assert True\n", encoding="utf-8")
    relative_project_root = Path(os.path.relpath(project_root, Path.cwd()))
    client = TestClient(create_app(str(relative_project_root)))
    session_id = "release-product-smoke-raw-session"
    raw_prompt = "Exercise product smoke without leaking SECRET-PRODUCT-SMOKE."

    response = client.post(
        "/ops/wrapper/release-product-smoke/run",
        json={
            "session_id": session_id,
            "base_url": "http://127.0.0.1:0",
            "host": "127.0.0.1",
            "port": 0,
            "pid": 13579,
            "readiness_command": "pytest tests/release_product_smoke_probe_test.py -q",
            "timeout_seconds": 30,
            "approved_by": "release-product-smoke-admin@example.invalid",
            "approval_ref": "operator-review::release-product-smoke",
            "prompts": [raw_prompt],
        },
    )

    assert response.status_code == 200
    smoke = response.json()
    checks = {check["check_id"]: check for check in smoke["checks"]}

    assert smoke["schema_version"] == "nexusnet-release-wrapper-product-smoke-v1"
    assert smoke["surface_id"] == "release-wrapper-product-smoke"
    assert smoke["status"] == "release-product-smoke-passed"
    assert smoke["product_surface"] == "wrapper"
    assert smoke["product_scope"] == "whole-system"
    assert smoke["session_ref_digest"].startswith("sha256:")
    assert smoke["raw_content_included"] is False
    assert smoke["active_production_mutation_allowed"] is False
    assert smoke["active_production_mutated"] is False
    assert smoke["artifact_ref"] == "artifacts/release-wrapper-runtime/release-product-smoke.json"
    assert smoke["artifact_path_digest"].startswith("sha256:")
    assert (project_root / "artifacts" / "release-wrapper-runtime" / "release-product-smoke.json").exists()
    assert {
        "initial-release-supervisor",
        "release-runtime",
        "release-readiness",
        "status-card",
        "session-lifecycle",
        "control-panel",
        "forward-pass-matrix",
        "native-hive-heartbeat-history",
        "canon-contract-receipts",
    }.issubset(checks)
    assert all(check["status"] == "pass" for check in checks.values())

    evidence = smoke["evidence"]
    assert evidence["initial_release_supervisor"]["latest_status"] == "initial-release-go"
    assert evidence["initial_release_supervisor"]["runtime_state"] == "replayed-evidence"
    assert evidence["runtime"]["runtime_state"] == "live-bound"
    assert evidence["runtime"]["matrix_coverage_status"] == "covered"
    assert evidence["runtime"]["native_hive_heartbeat_freshness_status"] == "fresh"
    assert evidence["runtime"]["native_hive_heartbeat_history_artifact_ref"] == (
        "release-wrapper-runtime/native-hive-heartbeats.jsonl"
    )
    assert evidence["release_readiness"]["go_no_go"] == "go"
    assert evidence["release_readiness"]["blocked_check_count"] == 0
    assert evidence["status_card"]["product_surface"] == "wrapper"
    assert evidence["session_lifecycle"]["runtime_state"] == "live-bound"
    assert evidence["control_panel"]["matrix_coverage_status"] == "covered"
    assert evidence["control_panel"]["product_smoke_status"] == "release-product-smoke-passed"
    assert evidence["canon_contract_receipts"]["surface_id"] == "whole-project-canon-contract-receipts"
    assert evidence["canon_contract_receipts"]["receipt_count"] >= 1
    assert evidence["canon_contract_receipts"]["latest_status"] == "covered"
    assert evidence["canon_contract_receipts"]["latest_receipt"]["gap_count"] == 0
    assert evidence["canon_contract_receipts"]["raw_content_included"] is False
    assert evidence["canon_contract_receipts"]["active_production_mutation_allowed"] is False

    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    readiness = client.get("/ops/wrapper/release-readiness", params={"session_id": session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    lifecycle = client.get("/ops/wrapper/session-lifecycle", params={"session_id": session_id}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]
    readiness_checks = {check["check_id"]: check for check in readiness["readiness_checks"]}

    assert runtime["canon_contract_ledger"]["coverage_status"] == "covered"
    assert runtime["canon_contract_ledger"]["partial_count"] == 0
    assert runtime["canon_contract_receipts"]["latest_status"] == "covered"
    assert runtime["canon_contract_receipts"]["latest_receipt"]["gap_count"] == 0
    assert runtime["release_product_smoke"]["latest_status"] == "release-product-smoke-passed"
    assert readiness["evidence"]["release_product_smoke"]["latest_status"] == "release-product-smoke-passed"
    assert readiness_checks["release-product-smoke"]["status"] == "pass"
    assert readiness_checks["canon-contract-receipt"]["status"] == "pass"
    assert status_card["release_product_smoke"]["latest_status"] == "release-product-smoke-passed"
    assert status_card["endpoint_refs"]["release_product_smoke_run"] == "/ops/wrapper/release-product-smoke/run"
    assert status_card["operator_action_lane"]["run_release_product_smoke_ref"] == "/ops/wrapper/release-product-smoke/run"
    assert lifecycle["release_product_smoke"]["latest_status"] == "release-product-smoke-passed"
    assert lifecycle["endpoint_refs"]["release_product_smoke_run"] == "/ops/wrapper/release-product-smoke/run"
    assert control_panel["release_wrapper_release_product_smoke"]["latest_status"] == "release-product-smoke-passed"

    control_panel_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    visualizer_js = (project_root / "ui" / "visualizer" / "app.js").read_text(encoding="utf-8")
    assert "Run Product Smoke" in control_panel_js
    assert "release product smoke" in visualizer_js

    serialized = json.dumps(
        {
            "smoke": smoke,
            "runtime": runtime["release_product_smoke"],
            "readiness": readiness["evidence"]["release_product_smoke"],
            "status_card": status_card["release_product_smoke"],
            "lifecycle": lifecycle["release_product_smoke"],
            "control_panel": control_panel["release_wrapper_release_product_smoke"],
        },
        sort_keys=True,
    )
    assert session_id not in serialized
    assert raw_prompt not in serialized
    assert "SECRET-PRODUCT-SMOKE" not in serialized
    assert "release-product-smoke-admin@example.invalid" not in serialized
    assert str(project_root) not in serialized


def test_release_product_smoke_records_sanitized_release_run_history_and_replays_after_restart(tmp_path: Path):
    short_base = tmp_path.parent / f"rrh-{hashlib.sha256(str(tmp_path).encode('utf-8')).hexdigest()[:8]}"
    project_root = make_project(short_base)
    sandbox_probe = project_root / "tests" / "release_run_history_probe_test.py"
    sandbox_probe.parent.mkdir(parents=True, exist_ok=True)
    sandbox_probe.write_text("def test_release_run_history_probe():\n    assert True\n", encoding="utf-8")
    relative_project_root = Path(os.path.relpath(project_root, Path.cwd()))
    client = TestClient(create_app(str(relative_project_root)))
    session_id = "release-run-history-raw-session"
    raw_prompt = "Record release history without leaking SECRET-RELEASE-RUN-HISTORY."

    latest_smoke: dict[str, object] = {}
    for index in range(2):
        response = client.post(
            "/ops/wrapper/release-product-smoke/run",
            json={
                "session_id": session_id,
                "base_url": "http://127.0.0.1:0",
                "host": "127.0.0.1",
                "port": 0,
                "pid": 24680 + index,
                "readiness_command": "pytest tests/release_run_history_probe_test.py -q",
                "timeout_seconds": 30,
                "approved_by": f"release-run-history-admin-{index}@example.invalid",
                "approval_ref": f"operator-review::release-run-history::{index}",
                "prompts": [raw_prompt],
            },
        )
        assert response.status_code == 200
        latest_smoke = response.json()

    assert latest_smoke["release_run"]["surface_id"] == "release-wrapper-release-run"
    assert latest_smoke["release_run"]["run_kind"] == "release-product-smoke"
    assert latest_smoke["release_run"]["product_scope"] == "whole-system"
    assert latest_smoke["release_run"]["raw_content_included"] is False
    assert latest_smoke["release_run"]["active_production_mutation_allowed"] is False
    _assert_whole_project_canon_contract_ledger(latest_smoke["evidence"]["canon_contract_ledger"], project_root)
    assert latest_smoke["release_run"]["canon_contract_ledger"]["surface_id"] == "whole-project-canon-contract-ledger"
    assert latest_smoke["release_run"]["canon_contract_ledger"]["source_count"] == len(CANON_CONTRACT_SOURCE_REFS)
    assert latest_smoke["release_run"]["canon_contract_ledger"]["ingested_source_count"] == len(CANON_CONTRACT_SOURCE_REFS)
    assert latest_smoke["release_run"]["canon_contract_ledger"]["raw_content_included"] is False
    assert latest_smoke["release_run"]["canon_contract_ledger"]["active_production_mutation_allowed"] is False
    assert latest_smoke["release_run"]["whole_system_evidence"]["native_hive_heartbeat_freshness_status"] == "fresh"
    assert latest_smoke["release_run"]["whole_system_evidence"]["native_hive_heartbeat_history_artifact_ref"] == (
        "release-wrapper-runtime/native-hive-heartbeats.jsonl"
    )

    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    readiness = client.get("/ops/wrapper/release-readiness", params={"session_id": session_id}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    lifecycle = client.get("/ops/wrapper/session-lifecycle", params={"session_id": session_id}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]
    readiness_checks = {check["check_id"]: check for check in readiness["readiness_checks"]}

    history = runtime["release_run_history"]
    latest_run = history["latest_run"]
    canon_ledger = runtime["canon_contract_ledger"]
    _assert_whole_project_canon_contract_ledger(canon_ledger, project_root)
    assert history["schema_version"] == "nexusnet-release-wrapper-release-run-history-v1"
    assert history["surface_id"] == "release-wrapper-release-run-history"
    assert history["latest_status"] == "release-product-smoke-passed"
    product_smoke_runs = [run for run in history["runs"] if run["run_kind"] == "release-product-smoke"]
    live_product_path_runs = [
        run for run in history["runs"] if run["run_kind"] == "release-wrapper-live-product-path"
    ]
    assert history["run_count"] >= 2
    assert history["global_run_count"] >= history["run_count"]
    assert len(product_smoke_runs) == 2
    assert live_product_path_runs
    assert history["product_scope"] == "whole-system"
    assert history["manifest_ref"] == "artifacts/release-wrapper-runtime/release-run-history.jsonl"
    assert latest_run["run_kind"] == "release-product-smoke"
    assert latest_run["product_scope"] == "whole-system"
    assert latest_run["status"] == "release-product-smoke-passed"
    assert latest_run["run_sequence"] == latest_smoke["release_run"]["run_sequence"]
    assert latest_run["raw_content_included"] is False
    assert latest_run["active_production_mutation_allowed"] is False
    assert latest_run["canon_contract_ledger"]["coverage_status"] == canon_ledger["coverage_status"]
    assert latest_run["canon_contract_ledger"]["contract_count"] == canon_ledger["contract_count"]
    assert latest_run["canon_contract_ledger"]["source_refs"] == CANON_CONTRACT_SOURCE_REFS
    assert latest_run["whole_system_evidence"]["native_hive_heartbeat_freshness_status"] == "fresh"
    assert latest_run["whole_system_evidence"]["native_hive_heartbeat_history_artifact_ref"] == (
        "release-wrapper-runtime/native-hive-heartbeats.jsonl"
    )
    assert all(run["raw_content_included"] is False for run in history["runs"])
    assert all(run["active_production_mutation_allowed"] is False for run in history["runs"])

    assert readiness_checks["canon-contract-ledger"]["status"] == "pass"
    _assert_whole_project_canon_contract_ledger(readiness["evidence"]["canon_contract_ledger"], project_root)
    assert readiness["evidence"]["release_run_history"]["latest_status"] == "release-product-smoke-passed"
    assert readiness["evidence"]["release_run_history"]["run_count"] == history["run_count"]
    assert status_card["canon_contract_ledger"]["source_manifest"]["ingested_source_count"] == len(CANON_CONTRACT_SOURCE_REFS)
    assert status_card["release_run_history"]["run_count"] == history["run_count"]
    assert status_card["endpoint_refs"]["release_run_history"] == "/ops/wrapper/release-runtime"
    assert lifecycle["canon_contract_ledger"]["contract_count"] == canon_ledger["contract_count"]
    assert lifecycle["release_run_history"]["latest_status"] == "release-product-smoke-passed"
    assert control_panel["release_wrapper_canon_contract_ledger"]["source_manifest"]["ingested_source_count"] == len(
        CANON_CONTRACT_SOURCE_REFS
    )
    assert control_panel["release_wrapper_runtime"]["canon_contract_ledger"]["contract_count"] == canon_ledger["contract_count"]
    assert control_panel["release_wrapper_release_run_history"]["run_count"] == history["run_count"]
    assert control_panel["release_wrapper_runtime"]["release_run_history"]["run_count"] == history["run_count"]

    history_path = project_root / "artifacts" / "release-wrapper-runtime" / "release-run-history.jsonl"
    assert history_path.exists()
    assert len([line for line in history_path.read_text(encoding="utf-8").splitlines() if line.strip()]) == (
        history["global_run_count"]
    )

    restarted = TestClient(create_app(str(relative_project_root)))
    replayed_runtime = restarted.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    replayed_status = restarted.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    replayed_visualizer = restarted.get(
        "/ops/brain/visualizer/state",
        params={"session_id": session_id},
    ).json()
    replayed_history = replayed_runtime["release_run_history"]
    replayed_ledger = replayed_runtime["canon_contract_ledger"]
    _assert_whole_project_canon_contract_ledger(replayed_ledger, project_root)
    assert replayed_history["run_count"] == history["run_count"]
    assert replayed_history["latest_run"]["run_id"] == latest_run["run_id"]
    assert replayed_history["latest_run"]["whole_system_evidence"]["native_hive_heartbeat_freshness_status"] == "fresh"
    assert replayed_runtime["native_hive_heartbeat"]["heartbeat_history"]["latest_fresh"] is True
    assert replayed_status["release_run_history"]["latest_run"]["run_id"] == latest_run["run_id"]
    assert replayed_status["canon_contract_ledger"]["source_manifest"]["source_refs"] == CANON_CONTRACT_SOURCE_REFS
    assert (
        replayed_visualizer["overlay_state"]["control_panel"]["release_wrapper_release_run_history"]["latest_run"][
            "run_id"
        ]
        == latest_run["run_id"]
    )
    assert (
        replayed_visualizer["overlay_state"]["control_panel"]["release_wrapper_canon_contract_ledger"][
            "source_manifest"
        ]["source_refs"]
        == CANON_CONTRACT_SOURCE_REFS
    )

    control_panel_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    visualizer_js = (project_root / "ui" / "visualizer" / "app.js").read_text(encoding="utf-8")
    assert "Canon contract ledger" in control_panel_js
    assert "canon contract ledger" in visualizer_js
    assert "release run history" in control_panel_js
    assert "release run history" in visualizer_js

    serialized = json.dumps(
        {
            "latest_smoke": latest_smoke["release_run"],
            "runtime": runtime["release_run_history"],
            "readiness": readiness["evidence"]["release_run_history"],
            "status_card": status_card["release_run_history"],
            "status_card_canon": status_card["canon_contract_ledger"],
            "lifecycle": lifecycle["release_run_history"],
            "lifecycle_canon": lifecycle["canon_contract_ledger"],
            "control_panel": control_panel["release_wrapper_release_run_history"],
            "control_panel_canon": control_panel["release_wrapper_canon_contract_ledger"],
            "canon_contract_ledger": canon_ledger,
            "replayed": replayed_history,
            "replayed_canon": replayed_ledger,
        },
        sort_keys=True,
    )
    assert session_id not in serialized
    assert raw_prompt not in serialized
    assert "SECRET-RELEASE-RUN-HISTORY" not in serialized
    assert "release-run-history-admin" not in serialized
    assert str(project_root) not in serialized


def test_initial_release_supervisor_manifest_replays_after_restart(tmp_path: Path):
    project_root = make_project(tmp_path)
    supervisor_path = project_root / "artifacts" / "release-wrapper-runtime" / "initial-release-supervisor.json"
    supervisor_path.parent.mkdir(parents=True, exist_ok=True)
    supervisor_path.write_text(
        json.dumps(
            {
                "schema_version": "nexusnet-release-wrapper-initial-release-supervisor-v1",
                "surface_id": "release-wrapper-initial-release-supervisor",
                "manifest_id": "initial-release-supervisor::manifest-digest",
                "generated_at": "2026-07-02T20:00:00Z",
                "authority": "NexusBrain",
                "status_label": "LOCKED CANON",
                "status": "initial-release-go",
                "honest_status_label": "initial-release-go",
                "product_surface": "wrapper",
                "product_scope": "whole-system",
                "session_id": "raw-initial-release-session",
                "session_ref_digest": "sha256:initial-release-session-digest",
                "actions": {
                    "wrapper_interactions": {
                        "status": "recorded",
                        "interaction_count": 3,
                        "raw_content_included": False,
                    },
                    "native_hive_heartbeat_history": {
                        "surface_id": "release-wrapper-native-hive-heartbeat-history",
                        "status": "fresh",
                        "freshness_status": "fresh",
                        "latest_fresh": True,
                        "latest_heartbeat_id": "native-hive-heartbeat::initial-release",
                        "artifact_ref": "release-wrapper-runtime/native-hive-heartbeats.jsonl",
                        "raw_content_included": False,
                        "active_production_mutation_allowed": False,
                        "active_production_mutated": False,
                    },
                    "federated_packet_import": {
                        "status": "quarantined-shadow-accepted",
                        "import_id": "fed-import::initial-release",
                        "raw_content_included": False,
                        "active_production_mutation_allowed": False,
                    },
                    "domain_expert_growth_admin_replay": {
                        "status": "recorded",
                        "run_id": "admin-replay::initial-release",
                        "raw_content_included": False,
                        "active_production_mutation_allowed": False,
                    },
                    "release_readiness_runner": {
                        "status": "completed",
                        "run_id": "release-readiness-run::initial-release",
                        "active_production_mutated": False,
                        "raw_content_included": False,
                    },
                    "production_spine_release_lifecycle": {
                        "status": "approved-shadow-release-lifecycle",
                        "run_id": "production-spine-release-lifecycle::initial-release",
                        "step_counts": {"total": 12, "passed": 12, "blocked": 0},
                        "raw_content_included": False,
                        "active_production_mutation_allowed": False,
                    },
                    "production_spine_release_lifecycle_rollback": {
                        "status": "rolled-back",
                        "rollback_id": "rollback::initial-release",
                        "rollback_restored": True,
                        "raw_content_included": False,
                        "active_production_mutation_allowed": False,
                    },
                    "boot_supervisor": {
                        "status": "boot-smoke-passed",
                        "manifest_id": "release-wrapper-boot::initial-release",
                        "pass_count": 9,
                        "failed_count": 0,
                        "raw_content_included": False,
                        "active_production_mutation_allowed": False,
                    },
                },
                "action_statuses": {
                    "wrapper_interactions": "recorded",
                    "native_hive_heartbeat_history": "fresh",
                    "federated_packet_import": "quarantined-shadow-accepted",
                    "domain_expert_growth_admin_replay": "recorded",
                    "release_readiness_runner": "completed",
                    "production_spine_release_lifecycle": "approved-shadow-release-lifecycle",
                    "production_spine_release_lifecycle_rollback": "rolled-back",
                    "boot_supervisor": "boot-smoke-passed",
                },
                "release_readiness": {
                    "surface_id": "release-wrapper-readiness",
                    "go_no_go": "go",
                    "passed_check_count": 24,
                    "blocked_check_count": 0,
                    "blockers": [],
                },
                "boot_supervisor": {
                    "surface_id": "release-wrapper-boot-supervisor",
                    "status": "boot-smoke-passed",
                    "manifest_id": "release-wrapper-boot::initial-release",
                    "pass_count": 9,
                    "failed_count": 0,
                },
                "endpoint_refs": {
                    "initial_release_supervisor_run": "/ops/wrapper/initial-release-supervisor/run",
                    "release_runtime": "/ops/wrapper/release-runtime",
                    "release_readiness": "/ops/wrapper/release-readiness",
                    "boot_supervisor_run": "/ops/wrapper/boot-supervisor/run",
                },
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
                "active_production_mutated": False,
                "privacy_boundary": "sanitized-status-ids-counts-digests-only-no-raw-prompts-outputs-session-ids",
                "mutation_boundary": "admin-approved-shadow-safe-file-production-spine-and-boot-evidence-only",
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    client = TestClient(create_app(str(project_root)))
    runtime = client.get("/ops/wrapper/release-runtime").json()
    readiness = client.get("/ops/wrapper/release-readiness").json()
    status_card = client.get("/ops/wrapper/status-card").json()
    lifecycle = client.get("/ops/wrapper/session-lifecycle").json()
    visualizer = client.get("/ops/brain/visualizer/state").json()
    control_panel = visualizer["overlay_state"]["control_panel"]

    supervisor = runtime["initial_release_supervisor"]
    assert supervisor["surface_id"] == "release-wrapper-initial-release-supervisor"
    assert supervisor["runtime_state"] == "replayed-evidence"
    assert supervisor["latest_status"] == "initial-release-go"
    assert supervisor["manifest_ref"] == "artifacts/release-wrapper-runtime/initial-release-supervisor.json"
    assert supervisor["action_statuses"]["release_readiness_runner"] == "completed"
    assert supervisor["action_statuses"]["native_hive_heartbeat_history"] == "fresh"
    assert supervisor["actions"]["native_hive_heartbeat_history"]["latest_fresh"] is True
    assert supervisor["action_statuses"]["production_spine_release_lifecycle"] == "approved-shadow-release-lifecycle"
    assert supervisor["action_statuses"]["production_spine_release_lifecycle_rollback"] == "rolled-back"
    assert supervisor["boot_supervisor"]["status"] == "boot-smoke-passed"
    assert supervisor["raw_content_included"] is False
    assert supervisor["active_production_mutation_allowed"] is False

    assert readiness["evidence"]["initial_release_supervisor"]["latest_status"] == "initial-release-go"
    assert readiness["evidence"]["initial_release_supervisor"]["runtime_state"] == "replayed-evidence"
    assert status_card["initial_release_supervisor"]["latest_status"] == "initial-release-go"
    assert lifecycle["initial_release_supervisor"]["latest_status"] == "initial-release-go"
    assert lifecycle["endpoint_refs"]["initial_release_supervisor_run"] == "/ops/wrapper/initial-release-supervisor/run"
    assert control_panel["release_wrapper_runtime"]["initial_release_supervisor"]["latest_status"] == "initial-release-go"
    assert control_panel["release_wrapper_initial_release_supervisor"]["latest_status"] == "initial-release-go"

    serialized = json.dumps(
        {
            "runtime": runtime,
            "readiness": readiness,
            "status_card": status_card,
            "lifecycle": lifecycle,
            "control_panel": control_panel,
        },
        sort_keys=True,
    )
    assert "raw-initial-release-session" not in serialized


def test_release_wrapper_session_lifecycle_proves_live_use_and_admin_update_path(tmp_path: Path):
    project_root = make_project(tmp_path)
    sandbox_probe = project_root / "tests" / "release_wrapper_session_lifecycle_probe_test.py"
    sandbox_probe.parent.mkdir(parents=True, exist_ok=True)
    sandbox_probe.write_text(
        "def test_release_wrapper_session_lifecycle_probe():\n"
        "    assert 'wrapper'.upper() == 'WRAPPER'\n",
        encoding="utf-8",
    )
    client = TestClient(create_app(str(project_root)))
    prompt = "Session lifecycle proof marker SECRET-SESSION-LIFECYCLE."
    session_id = "release-session-lifecycle-user"

    chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    assert chat.status_code == 200
    packet = client.get("/ops/wrapper/federated-packets", params={"session_id": session_id}).json()["latest_packet"]
    imported = client.post(
        "/ops/wrapper/federated-packets/import",
        json={"session_id": session_id, "peer_node_id": "release-session-lifecycle-peer", "packet": packet},
    ).json()
    assert imported["status"] == "quarantined-shadow-accepted"

    initial = client.get("/ops/wrapper/session-lifecycle", params={"session_id": session_id})
    assert initial.status_code == 200
    lifecycle = initial.json()
    assert lifecycle["surface_id"] == "release-wrapper-session-lifecycle"
    assert lifecycle["status_label"] == "LOCKED CANON"
    assert lifecycle["product_surface"] == "wrapper"
    assert lifecycle["runtime_state"] == "live-bound"
    assert lifecycle["session_ref_digest"]
    assert lifecycle["session_ref_digest"] != session_id
    assert lifecycle["session_lifecycle_ref"] == "/ops/wrapper/session-lifecycle"
    assert lifecycle["endpoint_refs"]["session_lifecycle"] == "/ops/wrapper/session-lifecycle"
    assert lifecycle["telemetry"]["surface_id"] == "release-wrapper-live-telemetry"
    assert lifecycle["telemetry"]["event_count"] == 1
    assert lifecycle["latest_interaction"]["raw_content_included"] is False
    assert lifecycle["latest_interaction"]["session_ref_digest"] == lifecycle["session_ref_digest"]
    step_statuses = {step["step_id"]: step["status"] for step in lifecycle["lifecycle_steps"]}
    assert step_statuses["bootable-entrypoint"] == "pass"
    assert step_statuses["live-wrapper-interaction"] == "pass"
    assert step_statuses["continuous-assimilation"] == "pass"
    assert step_statuses["global-growth"] == "pass"
    assert step_statuses["federated-packet"] == "pass"
    assert step_statuses["federated-packet-inbox"] == "pass"
    assert step_statuses["peer-shadow-proposal"] == "pass"
    assert step_statuses["production-spine-packet"] == "pass"
    assert step_statuses["effective-context-cache"] == "pass"
    assert step_statuses["ao-execution-receipt"] == "pass"
    assert step_statuses["dream-research-episode"] == "pass"

    action_lane = lifecycle["operator_action_lane"]
    approval = client.post(
        action_lane["admin_approval_ref"],
        json={"approved_by": "admin", "approval_ref": "operator-review::release-session-lifecycle"},
    )
    assert approval.status_code == 200
    sandbox = client.post(
        action_lane["sandbox_tests_ref"],
        json={"command": "pytest tests/release_wrapper_session_lifecycle_probe_test.py -q", "timeout_seconds": 30},
    )
    assert sandbox.status_code == 200
    apply = client.post(
        action_lane["apply_ref"],
        json={
            "test_refs": ["pytest tests/release_wrapper_session_lifecycle_probe_test.py -q"],
            "test_evidence_refs": [sandbox.json()["evidence_ref"]],
        },
    )
    assert apply.status_code == 200
    rollback = client.post(action_lane["rollback_ref"], json={"reason": "release-session-lifecycle-test"})
    assert rollback.status_code == 200

    refreshed = client.get("/ops/wrapper/session-lifecycle", params={"session_id": session_id})
    assert refreshed.status_code == 200
    lifecycle = refreshed.json()
    step_statuses = {step["step_id"]: step["status"] for step in lifecycle["lifecycle_steps"]}
    assert step_statuses["shadow-eval-replay"] == "pass"
    assert step_statuses["sandbox-evidence"] == "pass"
    assert step_statuses["safe-apply"] == "pass"
    assert step_statuses["rollback"] == "pass"
    assert lifecycle["readiness"]["go_no_go"] == "go"
    statuses = lifecycle["admin_actions"]["latest_action_statuses"]
    assert statuses["admin_approval"] == "admin-approved"
    assert statuses["shadow_eval_replay"] == "passed-shadow"
    assert statuses["sandbox_tests"] == "passed"
    assert statuses["apply"] == "applied-shadow-safe-file"
    assert statuses["rollback"] == "rolled-back"
    assert lifecycle["autonomous_update_path"]["latest_sandbox_test_evidence"]["status"] == "passed"
    assert lifecycle["autonomous_update_path"]["latest_applied"]["active_production_mutated"] is False
    assert lifecycle["autonomous_update_path"]["latest_rollback"]["rollback_restored"] is True
    assert lifecycle["privacy_boundary"].endswith("no-raw-prompts-outputs-session-ids")
    serialized = json.dumps(lifecycle)
    assert prompt not in serialized
    assert session_id not in serialized
    assert "SECRET-SESSION-LIFECYCLE" not in serialized

    html = client.get("/ui/wrapper/").text
    control_panel_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "/ops/wrapper/session-lifecycle" in html
    assert "release-wrapper-session-lifecycle" in html
    assert "/ops/wrapper/session-lifecycle" in control_panel_js
    assert "releaseWrapperSessionLifecycle" in control_panel_js
    assert "Release Harness session lifecycle" in control_panel_js


def test_release_wrapper_self_repair_ledger_records_admin_path_and_replays_by_session(tmp_path: Path):
    project_root = make_project(tmp_path)
    sandbox_probe = project_root / "tests" / "release_wrapper_self_repair_ledger_probe_test.py"
    sandbox_probe.parent.mkdir(parents=True, exist_ok=True)
    sandbox_probe.write_text(
        "def test_release_wrapper_self_repair_ledger_probe():\n"
        "    assert 'repair-ledger'.replace('-', '_') == 'repair_ledger'\n",
        encoding="utf-8",
    )
    client = TestClient(create_app(str(project_root)))
    session_a = "release-self-repair-ledger-a"
    session_b = "release-self-repair-ledger-b"
    prompt_a = "Self repair ledger marker SECRET-SELF-REPAIR-A."
    prompt_b = "Self repair ledger marker SECRET-SELF-REPAIR-B."
    digest_a = hashlib.sha256(session_a.encode("utf-8")).hexdigest()[:16]
    digest_b = hashlib.sha256(session_b.encode("utf-8")).hexdigest()[:16]

    first_chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_a,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt_a}],
        },
    )
    assert first_chat.status_code == 200
    second_chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_b,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt_b}],
        },
    )
    assert second_chat.status_code == 200

    first_lifecycle = client.get("/ops/wrapper/session-lifecycle", params={"session_id": session_a}).json()
    assert first_lifecycle["session_ref_digest"] == digest_a
    action_lane = first_lifecycle["operator_action_lane"]
    proposal_update_id = action_lane["proposal_update_id"]
    assert proposal_update_id

    approval = client.post(
        action_lane["admin_approval_ref"],
        json={"approved_by": "admin", "approval_ref": "operator-review::release-self-repair-ledger"},
    )
    assert approval.status_code == 200
    sandbox = client.post(
        action_lane["sandbox_tests_ref"],
        json={"command": "pytest tests/release_wrapper_self_repair_ledger_probe_test.py -q", "timeout_seconds": 30},
    )
    assert sandbox.status_code == 200
    assert sandbox.json()["status"] == "passed"
    applied = client.post(
        action_lane["apply_ref"],
        json={
            "test_refs": ["pytest tests/release_wrapper_self_repair_ledger_probe_test.py -q"],
            "test_evidence_refs": [sandbox.json()["evidence_ref"]],
        },
    )
    assert applied.status_code == 200
    rolled_back = client.post(action_lane["rollback_ref"], json={"reason": "release-self-repair-ledger-test"})
    assert rolled_back.status_code == 200

    session_a_lifecycle = client.get("/ops/wrapper/session-lifecycle", params={"session_id": session_a}).json()
    session_b_lifecycle = client.get("/ops/wrapper/session-lifecycle", params={"session_id": session_b}).json()
    ledger = session_a_lifecycle["self_repair_ledger"]
    assert ledger["surface_id"] == "release-wrapper-self-repair-ledger"
    assert ledger["session_ref_digest"] == digest_a
    assert ledger["repair_count"] == 4
    assert ledger["global_repair_count"] == 4
    assert ledger["latest_action"] == "rollback"
    assert ledger["latest_status"] == "rolled-back"
    assert [action["action"] for action in ledger["actions"]] == [
        "admin_approval",
        "sandbox_tests",
        "apply",
        "rollback",
    ]
    assert [action["status"] for action in ledger["actions"]] == [
        "admin-approved",
        "passed",
        "applied-shadow-safe-file",
        "rolled-back",
    ]
    assert all(action["update_id"] == proposal_update_id for action in ledger["actions"])
    assert all(action["session_ref_digest"] == digest_a for action in ledger["actions"])
    assert all(action["active_production_mutated"] is False for action in ledger["actions"])
    assert all(action["raw_content_included"] is False for action in ledger["actions"])
    assert ledger["authority_decision_count"] == 4
    assert ledger["latest_authority_decision"]["status"] == "allowed-shadow"
    assert ledger["latest_authority_decision"]["observed_effect_receipt"]["observed_effect_type"] == "filesystem_write"
    assert ledger["latest_authority_decision"]["rollback_record"]["rollback_available"] is True
    required_guard_aos = {"AdminAO", "GovernanceAO", "SecurityAO", "EvalsAO"}
    expected_sandbox_states = {
        "admin_approval": "ao-guarded-admin-control-plane",
        "sandbox_tests": "isolated-filesystem-copy-allowlisted-pytest",
        "apply": "isolated-filesystem-copy-allowlisted-pytest",
        "rollback": "safe-file-rollback",
    }
    for action in ledger["actions"]:
        guard = action["ao_guard"]
        assert guard["surface_id"] == "release-wrapper-ao-guard"
        assert guard["action"] == action["action"]
        assert guard["passed"] is True
        assert set(guard["required_aos"]) == required_guard_aos
        assert set(guard["received_aos"]) >= required_guard_aos
        assert guard["missing_aos"] == []
        receipts = action["ao_guard_receipts"]
        assert {receipt["ao_name"] for receipt in receipts} >= required_guard_aos
        assert all(receipt["session_ref_digest"] == digest_a for receipt in receipts)
        assert all(receipt["raw_content_included"] is False for receipt in receipts)
        assert all(receipt["direct_local_state_reads"] == [] for receipt in receipts)
        assert all(receipt["active_production_mutation_allowed"] is False for receipt in receipts)
        assert "artifact_path" not in json.dumps(receipts)
        authority_decision = action["authority_decision"]
        assert authority_decision["surface_id"] == "authority-integrity-spine"
        assert authority_decision["actor_ref"] == "release-wrapper-self-repair"
        assert authority_decision["effect_type"] == "filesystem_write"
        assert authority_decision["status"] == "allowed-shadow"
        assert authority_decision["production_action_allowed"] is False
        assert authority_decision["operator_approved"] is True
        assert authority_decision["sandbox_state"] == expected_sandbox_states[action["action"]]
        assert "capability::release-wrapper-self-repair" in authority_decision["capability_refs"]
        assert action["authority_effect_receipt"]["receipt_id"] == authority_decision["observed_effect_receipt"]["receipt_id"]
        assert action["authority_rollback_record"]["rollback_available"] is True
    assert any("sandbox-test::" in ref for action in ledger["actions"] for ref in action["evidence_refs"])
    assert any("ao_guard::" in ref for action in ledger["actions"] for ref in action["evidence_refs"])
    assert any("authority_decision::" in ref for action in ledger["actions"] for ref in action["evidence_refs"])
    assert any(ref.endswith("/apply") for action in ledger["actions"] for ref in action["evidence_refs"])
    assert session_b_lifecycle["session_ref_digest"] == digest_b
    assert session_b_lifecycle["self_repair_ledger"]["repair_count"] == 0
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": session_a}).json()
    visualizer_ledger = visualizer["overlay_state"]["control_panel"]["release_wrapper_self_repair_ledger"]
    assert visualizer_ledger["surface_id"] == "release-wrapper-self-repair-ledger"
    assert visualizer_ledger["session_ref_digest"] == digest_a
    assert visualizer_ledger["repair_count"] == 4
    assert visualizer_ledger["latest_action"] == "rollback"
    assert visualizer_ledger["ao_guard_passed_count"] == 4
    assert visualizer_ledger["authority_decision_count"] == 4
    assert visualizer_ledger["latest_authority_decision"]["rollback_record"]["rollback_available"] is True
    assert visualizer_ledger["latest_ao_guard"]["passed"] is True
    assert visualizer_ledger["raw_content_included"] is False
    aos = client.get("/ops/brain/aos").json()
    active_ao_names = {ao["name"] for ao in aos["active_aos"]}
    assert {"AdminAO", "SecurityAO"} <= active_ao_names

    restarted = TestClient(create_app(str(project_root)))
    replayed_a = restarted.get("/ops/wrapper/session-lifecycle", params={"session_id": session_a}).json()
    replayed_b = restarted.get("/ops/wrapper/session-lifecycle", params={"session_id": session_b}).json()
    assert replayed_a["self_repair_ledger"]["repair_count"] == 4
    assert replayed_a["self_repair_ledger"]["replay"]["status"] == "replayed"
    assert replayed_b["self_repair_ledger"]["repair_count"] == 0

    serialized = json.dumps({"a": replayed_a, "b": replayed_b})
    assert prompt_a not in serialized
    assert prompt_b not in serialized
    assert session_a not in serialized
    assert session_b not in serialized
    assert "SECRET-SELF-REPAIR-A" not in serialized
    assert "SECRET-SELF-REPAIR-B" not in serialized

    html = client.get("/ui/wrapper/").text
    control_panel_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    visualizer_js = (project_root / "ui" / "visualizer" / "app.js").read_text(encoding="utf-8")
    assert "release-wrapper-self-repair-ledger" in html
    assert "AO Guard Receipts" in html
    assert "release-wrapper-self-repair-ledger" in control_panel_js
    assert "self_repair_ledger" in control_panel_js
    assert "ao_guard_passed_count" in control_panel_js
    assert "authority effect receipts" in control_panel_js
    assert "Release Harness self repair" in visualizer_js
    assert "release-wrapper-self-repair-ledger" in visualizer_js
    assert "Harness AO guard receipts" in visualizer_js
    assert "Harness authority receipts" in visualizer_js


def test_release_wrapper_safe_apply_requires_ao_guard_receipts(tmp_path: Path):
    project_root = make_project(tmp_path)
    sandbox_probe = project_root / "tests" / "release_wrapper_guard_required_probe_test.py"
    sandbox_probe.parent.mkdir(parents=True, exist_ok=True)
    sandbox_probe.write_text("def test_release_wrapper_guard_required_probe():\n    assert True\n", encoding="utf-8")
    client = TestClient(create_app(str(project_root)))
    session_id = "release-guard-required-user"

    chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_id,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": "Prove guarded self repair apply."}],
        },
    )
    assert chat.status_code == 200
    lifecycle = client.get("/ops/wrapper/session-lifecycle", params={"session_id": session_id}).json()
    action_lane = lifecycle["operator_action_lane"]
    approval = client.post(
        action_lane["admin_approval_ref"],
        json={"approved_by": "admin", "approval_ref": "operator-review::guard-required"},
    )
    assert approval.status_code == 200
    sandbox = client.post(
        action_lane["sandbox_tests_ref"],
        json={"command": "pytest tests/release_wrapper_guard_required_probe_test.py -q", "timeout_seconds": 30},
    )
    assert sandbox.status_code == 200

    runtime = client.app.state.release_wrapper_runtime
    original_ao_registry = runtime.ao_registry
    runtime.ao_registry = None
    try:
        rejected = client.post(
            action_lane["apply_ref"],
            json={
                "test_refs": ["pytest tests/release_wrapper_guard_required_probe_test.py -q"],
                "test_evidence_refs": [sandbox.json()["evidence_ref"]],
            },
        )
    finally:
        runtime.ao_registry = original_ao_registry

    assert rejected.status_code == 400
    assert "AO guard receipts required before safe apply" in rejected.json()["detail"]

    applied = client.post(
        action_lane["apply_ref"],
        json={
            "test_refs": ["pytest tests/release_wrapper_guard_required_probe_test.py -q"],
            "test_evidence_refs": [sandbox.json()["evidence_ref"]],
        },
    )
    assert applied.status_code == 200
    payload = applied.json()
    assert payload["release_wrapper_ao_guard"]["passed"] is True
    assert set(payload["release_wrapper_ao_guard"]["required_aos"]) == {"AdminAO", "GovernanceAO", "SecurityAO", "EvalsAO"}
    assert {receipt["ao_name"] for receipt in payload["release_wrapper_ao_guard"]["receipts"]} >= {
        "AdminAO",
        "GovernanceAO",
        "SecurityAO",
        "EvalsAO",
    }


def test_release_wrapper_session_lifecycle_is_filtered_by_session_and_replays_after_restart(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    session_a = "release-session-filter-a"
    session_b = "release-session-filter-b"
    digest_a = hashlib.sha256(session_a.encode("utf-8")).hexdigest()[:16]
    digest_b = hashlib.sha256(session_b.encode("utf-8")).hexdigest()[:16]
    prompt_a = "Session A lifecycle filter marker SECRET-FILTER-A."
    prompt_b = "Session B lifecycle filter marker SECRET-FILTER-B."

    first_chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_a,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt_a}],
        },
    )
    assert first_chat.status_code == 200
    first_lifecycle = client.get("/ops/wrapper/session-lifecycle", params={"session_id": session_a}).json()
    first_trace = first_lifecycle["latest_interaction"]["trace_id"]
    assert first_lifecycle["session_ref_digest"] == digest_a
    assert first_lifecycle["session_history"]["surface_id"] == "release-wrapper-session-history"
    assert first_lifecycle["session_history"]["event_count"] == 1
    assert first_lifecycle["session_history"]["global_event_count"] == 1
    assert first_lifecycle["telemetry"]["event_count"] == 1

    second_chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": session_b,
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": prompt_b}],
        },
    )
    assert second_chat.status_code == 200

    session_a_runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_a}).json()
    session_a_lifecycle = client.get("/ops/wrapper/session-lifecycle", params={"session_id": session_a}).json()
    session_b_lifecycle = client.get("/ops/wrapper/session-lifecycle", params={"session_id": session_b}).json()

    assert session_a_runtime["session_history"]["event_count"] == 1
    assert session_a_runtime["session_history"]["global_event_count"] == 2
    assert session_a_runtime["latest_interaction"]["session_ref_digest"] == digest_a
    assert session_a_runtime["latest_interaction"]["trace_id"] == first_trace
    assert session_a_runtime["live_wrapper_telemetry"]["event_count"] == 1
    assert {event["session_ref_digest"] for event in session_a_runtime["live_wrapper_telemetry"]["recent_events"]} == {digest_a}
    assert session_a_runtime["latest_interaction"]["session_ref_digest"] != digest_b

    assert session_a_lifecycle["session_ref_digest"] == digest_a
    assert session_a_lifecycle["latest_interaction"]["trace_id"] == first_trace
    assert session_a_lifecycle["latest_interaction"]["session_ref_digest"] == digest_a
    assert session_a_lifecycle["session_history"]["event_count"] == 1
    assert session_a_lifecycle["session_history"]["global_event_count"] == 2
    assert session_a_lifecycle["session_history"]["latest_trace_id"] == first_trace
    assert session_a_lifecycle["telemetry"]["event_count"] == 1
    assert {event["session_ref_digest"] for event in session_a_lifecycle["telemetry"]["recent_events"]} == {digest_a}
    assert session_b_lifecycle["session_ref_digest"] == digest_b
    assert session_b_lifecycle["latest_interaction"]["session_ref_digest"] == digest_b
    assert session_b_lifecycle["latest_interaction"]["trace_id"] != first_trace

    restarted = TestClient(create_app(str(project_root)))
    replayed_a = restarted.get("/ops/wrapper/session-lifecycle", params={"session_id": session_a}).json()
    replayed_b = restarted.get("/ops/wrapper/session-lifecycle", params={"session_id": session_b}).json()

    assert replayed_a["session_ref_digest"] == digest_a
    assert replayed_a["session_history"]["event_count"] == 1
    assert replayed_a["session_history"]["global_event_count"] == 2
    assert replayed_a["latest_interaction"]["trace_id"] == first_trace
    assert replayed_a["latest_interaction"]["session_ref_digest"] == digest_a
    assert replayed_a["telemetry"]["event_count"] == 1
    assert {event["session_ref_digest"] for event in replayed_a["telemetry"]["recent_events"]} == {digest_a}
    assert replayed_b["session_ref_digest"] == digest_b
    assert replayed_b["latest_interaction"]["session_ref_digest"] == digest_b

    serialized = json.dumps({"a": replayed_a, "b": replayed_b})
    assert prompt_a not in serialized
    assert prompt_b not in serialized
    assert session_a not in serialized
    assert session_b not in serialized
    assert "SECRET-FILTER-A" not in serialized
    assert "SECRET-FILTER-B" not in serialized

    html = client.get("/ui/wrapper/").text
    control_panel_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "release-wrapper-session-history" in html
    assert "release-wrapper-session-history" in control_panel_js
    assert "session_history" in control_panel_js


def test_release_runtime_recovers_persisted_summary_after_app_restart(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    client.post(
        "/v1/chat",
        json={
            "session_id": "restart-user",
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": "Persist this wrapper signal."}],
        },
    )
    before = client.get("/ops/wrapper/release-runtime", params={"session_id": "restart-user"}).json()
    assert before["entrypoint"]["runtime_state"] == "live-bound"
    assert before["federated_packet_count"] == 1
    assert before["production_spine"]["packet_count"] == 1

    restarted = TestClient(create_app(str(project_root)))
    after = restarted.get("/ops/wrapper/release-runtime", params={"session_id": "restart-user"}).json()
    replayed_assimilation = restarted.get("/ops/brain/canon/continuous-assimilation").json()

    assert after["entrypoint"]["runtime_state"] == "live-bound"
    assert after["status_source"] == "live-memory"
    assert after["replay"]["status"] == "replayed"
    assert after["replay"]["event_count"] == 1
    assert after["global_growth"]["global_captures"] >= 2
    assert after["global_growth"]["runtime_interaction_count"] >= 2
    assert after["global_growth"]["latest_runtime_receipt"]["raw_content_included"] is False
    assert after["federated_packet_count"] == 1
    assert after["production_spine"]["packet_count"] == 1
    assert after["latest_interaction"]["source_model"] == "nexusnet-offline"
    assert "expert.conversationalist" in replayed_assimilation["nodes"]
    assert replayed_assimilation["nodes"]["expert.conversationalist"]["captures"] == 1
    assert replayed_assimilation["provenance"]["expert.conversationalist"][0]["source_model"] == "nexusnet-offline"
    assert "Persist this wrapper signal" not in json.dumps(after)
    assert "Persist this wrapper signal" not in json.dumps(replayed_assimilation)


def test_autonomous_update_admin_approval_safe_apply_and_rollback(tmp_path: Path):
    project_root = make_project(tmp_path)
    sandbox_probe = project_root / "tests" / "sandbox_probe_test.py"
    sandbox_probe.parent.mkdir(parents=True, exist_ok=True)
    sandbox_probe.write_text("def test_sandbox_probe():\n    assert 1 + 1 == 2\n", encoding="utf-8")
    client = TestClient(create_app(str(project_root)))

    proposed = client.post(
        "/ops/brain/autonomous-updates/proposals",
        json={
            "update_id": "update::safe-wrapper-policy",
            "update_type": "prompt_policy",
            "target_ref": "safe-artifact::wrapper-policy",
            "requested_state": "proposal",
            "eval_refs": ["pytest::tests/test_release_wrapper_runtime.py"],
            "artifact_trust_refs": ["signed-manifest::safe-wrapper-policy"],
            "rollback_plan": "restore-previous-safe-wrapper-policy-json",
            "monitoring_plan": "focused-pytest-and-wrapper-runtime-status",
            "metadata": {
                "safe_payload": {"policy": "prefer-wrapper-entrypoint"},
                "safe_file_scope": ["artifacts/autonomous-updates/safe-files"],
            },
        },
    )
    assert proposed.status_code == 200

    approval = client.post(
        "/ops/brain/autonomous-updates/update::safe-wrapper-policy/admin-approval",
        json={"approved_by": "admin", "approval_ref": "operator-review::release-wrapper"},
    )
    assert approval.status_code == 200
    assert approval.json()["status"] == "admin-approved"
    assert approval.json()["evidence_gate"]["all_required_refs_present"] is True
    assert approval.json()["evidence_gate"]["eval_refs"] == ["pytest::tests/test_release_wrapper_runtime.py"]
    assert approval.json()["evidence_gate"]["artifact_trust_refs"] == ["signed-manifest::safe-wrapper-policy"]

    rejected_sandbox = client.post(
        "/ops/brain/autonomous-updates/update::safe-wrapper-policy/sandbox-tests",
        json={"command": "python -c print(1)"},
    )
    assert rejected_sandbox.status_code == 400
    assert "allowlisted pytest" in rejected_sandbox.json()["detail"]

    sandbox_run = client.post(
        "/ops/brain/autonomous-updates/update::safe-wrapper-policy/sandbox-tests",
        json={"command": "pytest tests/sandbox_probe_test.py -q", "timeout_seconds": 30},
    )
    assert sandbox_run.status_code == 200
    sandbox_payload = sandbox_run.json()
    assert sandbox_payload["status"] == "passed"
    assert sandbox_payload["passed"] is True
    assert sandbox_payload["sandbox"]["shell_used"] is False
    assert sandbox_payload["sandbox"]["active_production_mutated"] is False
    assert sandbox_payload["sandbox"]["mode"] == "isolated-filesystem-copy-allowlisted-pytest"
    assert sandbox_payload["sandbox"]["active_project_root_mutated"] is False
    assert sandbox_payload["sandbox"]["sandbox_root_digest"] != sandbox_payload["sandbox"]["active_project_root_digest"]
    assert sandbox_payload["diff_summary"]["unsafe_change_count"] == 0
    assert sandbox_payload["diff_summary"]["changed_file_count"] >= 0
    assert Path(sandbox_payload["pre_manifest_path"]).exists()
    assert Path(sandbox_payload["post_manifest_path"]).exists()
    assert Path(sandbox_payload["diff_path"]).exists()
    assert sandbox_payload["evidence_ref"].startswith("sandbox-test::")
    assert Path(sandbox_payload["artifact_path"]).exists()

    rejected_apply = client.post(
        "/ops/brain/autonomous-updates/update::safe-wrapper-policy/apply",
        json={
            "test_refs": ["pytest tests/sandbox_probe_test.py -q"],
            "test_results": [
                {
                    "command": "pytest tests/sandbox_probe_test.py -q",
                    "passed": True,
                    "failure_count": 0,
                }
            ],
        },
    )
    assert rejected_apply.status_code == 400
    assert "sandbox test evidence" in rejected_apply.json()["detail"]

    applied = client.post(
        "/ops/brain/autonomous-updates/update::safe-wrapper-policy/apply",
        json={
            "test_refs": ["pytest tests/sandbox_probe_test.py -q"],
            "test_evidence_refs": [sandbox_payload["evidence_ref"]],
        },
    )
    assert applied.status_code == 200
    applied_payload = applied.json()
    assert applied_payload["status"] == "applied-shadow-safe-file"
    assert applied_payload["active_production_mutated"] is False
    assert applied_payload["test_results"][0]["passed"] is True
    assert applied_payload["test_results"][0]["evidence_ref"] == sandbox_payload["evidence_ref"]
    assert applied_payload["test_results"][0]["sandbox_mode"] == "isolated-filesystem-copy-allowlisted-pytest"
    assert applied_payload["test_results"][0]["diff_summary"]["unsafe_change_count"] == 0
    assert Path(applied_payload["safe_file_path"]).exists()

    summary = client.get("/ops/brain/autonomous-updates").json()
    assert summary["sandbox_test_evidence_count"] == 1
    assert summary["latest_sandbox_test_evidence"]["evidence_ref"] == sandbox_payload["evidence_ref"]

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "release-update-sandbox"}).json()
    scorecard = visualizer["overlay_state"]["control_panel"]["autonomous_update_scorecard"]
    assert scorecard["latest_sandbox_test_evidence"]["evidence_ref"] == sandbox_payload["evidence_ref"]

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "Sandbox test evidence" in app_js
    assert "latest_sandbox_test_evidence" in app_js
    assert "unsafe_change_count" in app_js
    assert "isolated filesystem" in app_js

    rolled_back = client.post(
        "/ops/brain/autonomous-updates/update::safe-wrapper-policy/rollback",
        json={"reason": "release-wrapper-test-rollback"},
    )
    assert rolled_back.status_code == 200
    assert rolled_back.json()["status"] == "rolled-back"
    assert rolled_back.json()["rollback_restored"] is True


def test_release_wrapper_safe_apply_requires_passed_shadow_eval_replay(tmp_path: Path):
    project_root = make_project(tmp_path)
    sandbox_probe = project_root / "tests" / "wrapper_eval_replay_gate_probe_test.py"
    sandbox_probe.parent.mkdir(parents=True, exist_ok=True)
    sandbox_probe.write_text("def test_wrapper_eval_replay_gate_probe():\n    assert True\n", encoding="utf-8")
    client = TestClient(create_app(str(project_root)))

    proposed = client.post(
        "/ops/brain/autonomous-updates/proposals",
        json={
            "update_id": "update::release-wrapper-missing-eval-replay",
            "update_type": "prompt_policy",
            "target_ref": "safe-artifact::release-wrapper-dream-research::expert.coder",
            "requested_state": "proposal",
            "eval_refs": [
                "eval-case::release-wrapper-dream-research::manual",
                "eval::release-wrapper-dream-research::manual",
            ],
            "artifact_trust_refs": ["signed-manifest::release-wrapper-manual"],
            "rollback_plan": "restore-previous-release-wrapper-policy-json",
            "monitoring_plan": "focused-pytest-release-wrapper-eval-replay-gate",
            "operator_approved": True,
            "metadata": {
                "source": "release-wrapper-dream-research-queue",
                "dream_research_queue": True,
                "safe_payload": {"policy": "manual-without-eval-replay"},
                "active_production_mutation_allowed": False,
            },
        },
    )
    assert proposed.status_code == 200

    sandbox_run = client.post(
        "/ops/brain/autonomous-updates/update::release-wrapper-missing-eval-replay/sandbox-tests",
        json={"command": "pytest tests/wrapper_eval_replay_gate_probe_test.py -q", "timeout_seconds": 30},
    )
    assert sandbox_run.status_code == 200
    assert sandbox_run.json()["status"] == "passed"

    rejected_apply = client.post(
        "/ops/brain/autonomous-updates/update::release-wrapper-missing-eval-replay/apply",
        json={
            "test_refs": ["pytest tests/wrapper_eval_replay_gate_probe_test.py -q"],
            "test_evidence_refs": [sandbox_run.json()["evidence_ref"]],
        },
    )

    assert rejected_apply.status_code == 400
    assert "passed shadow eval replay evidence" in rejected_apply.json()["detail"]


def test_autonomous_update_sandbox_rejects_out_of_scope_file_mutation(tmp_path: Path):
    project_root = make_project(tmp_path)
    unsafe_probe = project_root / "tests" / "sandbox_unsafe_mutation_test.py"
    unsafe_probe.parent.mkdir(parents=True, exist_ok=True)
    unsafe_probe.write_text(
        "from pathlib import Path\n\n"
        "def test_sandbox_scope_violation():\n"
        "    Path('unsafe_mutation.txt').write_text('not allowed', encoding='utf-8')\n"
        "    assert True\n",
        encoding="utf-8",
    )
    client = TestClient(create_app(str(project_root)))

    proposed = client.post(
        "/ops/brain/autonomous-updates/proposals",
        json={
            "update_id": "update::unsafe-sandbox-mutation",
            "update_type": "prompt_policy",
            "target_ref": "safe-artifact::unsafe-sandbox-mutation",
            "requested_state": "proposal",
            "eval_refs": ["pytest::tests/sandbox_unsafe_mutation_test.py"],
            "artifact_trust_refs": ["signed-manifest::unsafe-sandbox-mutation"],
            "rollback_plan": "restore-previous-safe-json",
            "monitoring_plan": "focused-pytest-wrapper-runtime-status",
            "metadata": {"safe_payload": {"policy": "reject-unsafe-sandbox-mutation"}},
        },
    )
    assert proposed.status_code == 200
    approval = client.post(
        "/ops/brain/autonomous-updates/update::unsafe-sandbox-mutation/admin-approval",
        json={"approved_by": "admin", "approval_ref": "operator-review::unsafe-mutation"},
    )
    assert approval.status_code == 200

    sandbox_run = client.post(
        "/ops/brain/autonomous-updates/update::unsafe-sandbox-mutation/sandbox-tests",
        json={"command": "pytest tests/sandbox_unsafe_mutation_test.py -q", "timeout_seconds": 30},
    )

    assert sandbox_run.status_code == 200
    sandbox_payload = sandbox_run.json()
    assert sandbox_payload["status"] == "failed"
    assert sandbox_payload["passed"] is False
    assert sandbox_payload["returncode"] == 0
    assert sandbox_payload["diff_summary"]["unsafe_change_count"] == 1
    assert sandbox_payload["diff_summary"]["unsafe_changes"][0]["path"] == "unsafe_mutation.txt"
    assert sandbox_payload["sandbox"]["active_project_root_mutated"] is False
    assert not (project_root / "unsafe_mutation.txt").exists()

    rejected_apply = client.post(
        "/ops/brain/autonomous-updates/update::unsafe-sandbox-mutation/apply",
        json={
            "test_refs": ["pytest tests/sandbox_unsafe_mutation_test.py -q"],
            "test_evidence_refs": [sandbox_payload["evidence_ref"]],
        },
    )
    assert rejected_apply.status_code == 400
    assert "isolated sandbox test evidence" in rejected_apply.json()["detail"]

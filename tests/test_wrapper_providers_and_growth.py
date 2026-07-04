"""Long-road wrapper mechanisms: provider wrapping, dual-runtime co-execution, multi-user growth."""
from __future__ import annotations

import json
import importlib
from pathlib import Path

import pytest

from fastapi.testclient import TestClient

from nexus.schemas import OperatorRequest
from nexusnet.providers.model_providers import (
    EchoProvider, OpenAICompatibleProvider, ProviderRegistry, default_provider_registry,
    openrouter, requesty, lmstudio, vllm,
)
from nexusnet.providers.dual_runtime import DualRuntimeCoordinator
from nexusnet.hive.multi_user_growth import MultiUserGrowthCoordinator
from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project

nexus_api_app = importlib.import_module("nexus.api.app")

REQUIRED_CANONICAL_AOS = {
    "OperatorAO",
    "RouterAO",
    "CritiqueAO",
    "MemoryAO",
    "MaintenanceAO",
    "HardwareMonitorAO",
    "EvaluationAO",
    "ReleaseAO",
    "SecurityAO",
    "EvalsAO",
}
REQUIRED_DOMAIN_ROUTED_AOS = {"CodingAO", "ResearchAO", "FederationAO"}
CONSOLIDATED_CANONICAL_AOS = {
    "PlanningAO",
    "OperatorAO",
    "RouterAO",
    "MemoryAO",
    "DreamAO",
    "CritiqueAO",
    "SelfTrainingAO",
    "MaintenanceAO",
    "ReleaseAO",
    "HardwareMonitorAO",
    "GovernanceAO",
    "AdminAO",
    "SecurityAO",
    "SafetyAO",
    "RuntimeAO",
    "EvalsAO",
    "EvaluationAO",
    "ResearchAO",
    "DataIngestAO",
    "ProtocolAO",
    "VisualOpsAO",
    "FederationAO",
    "PackagingAO",
    "TrainingAO",
    "EvolutionAO",
    "MathAO",
    "CodingAO",
    "MedicalAO",
}


def _write_release_wrapper_auto_governance_probe(project_root: Path) -> str:
    probe = project_root / "tests" / "test_release_wrapper_runtime.py"
    probe.parent.mkdir(parents=True, exist_ok=True)
    probe.write_text(
        "def test_release_wrapper_status_card_is_lightweight_control_panel_surface_after_restart():\n"
        "    assert 'wrapper'.upper() == 'WRAPPER'\n",
        encoding="utf-8",
    )
    return (
        "pytest tests/test_release_wrapper_runtime.py::"
        "test_release_wrapper_status_card_is_lightweight_control_panel_surface_after_restart -q"
    )


def _ao_receipt_for_trace(aos: dict, trace_id: str) -> dict:
    trace_ref = f"trace::{trace_id}"
    return next(receipt for receipt in aos["execution_receipts"] if receipt.get("trace_ref") == trace_ref)


# --- provider wrapping ---

def test_app_ao_registry_exposes_consolidated_canon_roster_and_routes_domains(tmp_path: Path):
    client = TestClient(create_app(str(make_project(tmp_path))))

    aos = client.get("/ops/brain/aos").json()
    active_names = {ao["name"] for ao in aos["active_aos"]}
    registry = client.app.state.services.brain_aos

    assert CONSOLIDATED_CANONICAL_AOS <= active_names
    assert registry.select_request(OperatorRequest(prompt="Research assimilation targets and cite source evidence.")).ao_name == "ResearchAO"
    assert registry.select_request(OperatorRequest(prompt="Import federated peer packet and check poisoning risk.")).ao_name == "FederationAO"
    assert registry.select_request(OperatorRequest(prompt="Audit MCP protocol bridge and tool handshake policy.")).ao_name == "ProtocolAO"
    assert registry.select_request(OperatorRequest(prompt="Prepare packaging bundle and buyer release evidence.")).ao_name == "PackagingAO"

def test_echo_provider_is_deterministic_offline():
    p = EchoProvider(provider_id="local-echo")
    out = p.complete([{"role": "user", "content": "hello world"}])
    assert out["ok"] is True and "hello world" in out["text"] and out["local"] is True


def test_openai_compatible_degrades_safely_offline():
    # no network/key in sandbox -> graceful ok:False, never raises (skip-safe wrapping)
    p = openrouter("anthropic/claude-opus", api_key="")
    out = p.complete([{"role": "user", "content": "hi"}])
    assert out["ok"] is False and "error" in out and out["text"] == ""


def test_canon_provider_factories_have_right_locality():
    assert openrouter("m").is_local is False and requesty("m").is_local is False
    assert lmstudio().is_local is True and vllm("m").is_local is True
    assert "openrouter.ai" in openrouter("m").base_url
    assert "localhost:1234" in lmstudio().base_url


def test_registry_lists_local_and_cloud():
    reg = default_provider_registry()
    assert "lmstudio" in reg.local_providers() and "vllm" in reg.local_providers()
    assert "openrouter" in reg.cloud_providers() and "requesty" in reg.cloud_providers()
    assert reg.complete("nexusnet-offline", [{"role": "user", "content": "x"}])["ok"] is True


# --- dual-runtime co-execution (CPU + GPU through NexusNet) ---

def test_dual_runtime_co_executes_and_merges():
    reg = ProviderRegistry()
    reg.register(EchoProvider(provider_id="cpu-lmstudio", is_local=True))
    reg.register(EchoProvider(provider_id="gpu-vllm", is_local=False))
    coord = DualRuntimeCoordinator(reg, cpu_provider="cpu-lmstudio", gpu_provider="gpu-vllm",
                                   merge="prefer_gpu")
    res = coord.co_execute([{"role": "user", "content": "compute"}])
    assert res["ran_simultaneously"] is True and res["through_nexusnet"] is True
    assert res["cpu"]["ok"] and res["gpu"]["ok"]
    assert set(res["contributors"]) == {"cpu-lmstudio", "gpu-vllm"}     # both feed assimilation
    assert res["merged_from"] == "gpu-vllm"                             # prefer_gpu policy
    both = DualRuntimeCoordinator(reg, cpu_provider="cpu-lmstudio", gpu_provider="gpu-vllm",
                                  merge="both").co_execute([{"role": "user", "content": "x"}])
    assert "---" in both["merged_text"]


def test_dual_runtime_falls_back_when_one_runtime_down():
    reg = ProviderRegistry()
    reg.register(EchoProvider(provider_id="cpu", is_local=True))
    reg.register(openrouter("down", api_key=""))           # cloud GPU side is offline here
    coord = DualRuntimeCoordinator(reg, cpu_provider="cpu", gpu_provider="openrouter",
                                   merge="prefer_gpu")
    res = coord.co_execute([{"role": "user", "content": "x"}])
    assert res["merged_from"] == "cpu"                     # falls back to the working runtime


# --- multi-user growth (federated across users over time) ---

def test_multi_user_growth_aggregates_across_users():
    g = MultiUserGrowthCoordinator(global_train_threshold=4, federate_min_users=2)
    # 4 users each assimilate a different source model into the same expert node
    for i, model in enumerate(("gpt-5.2", "claude-opus", "qwen3", "gemini")):
        g.assimilate_for_user(f"user{i}", source_model=model, expert_node="expert.coder", quality=0.9)
    assert len(g.global_sources("expert.coder")) == 4
    assert g.global_ready_to_train("expert.coder") is True   # global threshold met across users
    assert g.federation_ready() is True                      # enough users to federate
    st = g.growth_status()
    assert st["users"] == 4 and "expert.coder" in st["training_ready_nodes"]
    assert st["birth_progress"] == 1.0 and st["fully_grown"] is True


def test_multi_user_growth_not_ready_with_one_user():
    g = MultiUserGrowthCoordinator(global_train_threshold=3, federate_min_users=2)
    g.assimilate_for_user("solo", source_model="gpt-5.2", expert_node="expert.x")
    assert g.federation_ready() is False
    assert g.growth_status()["fully_grown"] is False


# --- providers endpoint in the live wrapper service ---

def test_providers_endpoint_lists_the_pool(tmp_path: Path):
    client = TestClient(create_app(str(make_project(tmp_path))))
    j = client.get("/ops/wrapper/providers").json()
    assert j["surface_id"] == "wrapper-providers"
    ids = {p["provider_id"] for p in j["providers"]}
    assert {"nexusnet-offline", "openrouter", "requesty", "lmstudio", "vllm"} <= ids
    assert "lmstudio" in j["local"] and "openrouter" in j["cloud"]


def test_wrapper_provider_readiness_is_honest_sanitized_and_release_visible(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    providers = client.get("/ops/wrapper/providers").json()
    provider_readiness = providers["provider_readiness"]
    readiness_by_id = {item["provider_id"]: item for item in provider_readiness["providers"]}

    assert provider_readiness["surface_id"] == "release-wrapper-provider-readiness"
    assert provider_readiness["default_provider_id"] == "nexusnet-offline"
    assert provider_readiness["usable_provider_count"] >= 1
    assert provider_readiness["raw_content_included"] is False
    assert provider_readiness["active_production_mutation_allowed"] is False
    assert readiness_by_id["nexusnet-offline"]["status"] == "usable"
    assert readiness_by_id["nexusnet-offline"]["external_dependency"] is False
    assert readiness_by_id["openrouter"]["status"] == "missing-credentials"
    assert readiness_by_id["requesty"]["status"] == "missing-credentials"
    assert readiness_by_id["lmstudio"]["status"] == "configured-unverified"
    assert readiness_by_id["vllm"]["status"] == "configured-unverified"
    assert "OPENROUTER_API_KEY" not in json.dumps(provider_readiness)
    assert "REQUESTY_API_KEY" not in json.dumps(provider_readiness)
    assert "sk-" not in json.dumps(provider_readiness)

    chat = client.post(
        "/v1/chat/completions",
        json={
            "session_id": "provider-readiness-user",
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": "Provider readiness should be visible."}],
        },
    )
    assert chat.status_code == 200
    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": "provider-readiness-user"}).json()
    release_readiness = client.get(
        "/ops/wrapper/release-readiness",
        params={"session_id": "provider-readiness-user"},
    ).json()
    checks = {check["check_id"]: check for check in release_readiness["readiness_checks"]}

    assert runtime["provider_readiness"]["surface_id"] == "release-wrapper-provider-readiness"
    assert runtime["provider_readiness"]["latest_active_provider_id"] == "nexusnet-offline"
    assert runtime["latest_interaction"]["provider_readiness_status"] == "usable"
    assert checks["provider-readiness"]["status"] == "pass"
    assert release_readiness["evidence"]["provider_readiness"]["usable_provider_count"] >= 1
    assert release_readiness["evidence"]["provider_readiness"]["raw_content_included"] is False
    assert "Provider readiness should be visible" not in json.dumps(
        {
            "providers": providers,
            "runtime": runtime,
            "release_readiness": release_readiness,
        }
    )

    control_panel_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    visualizer_js = (project_root / "ui" / "visualizer" / "app.js").read_text(encoding="utf-8")
    wrapper_html = (project_root / "ui" / "wrapper" / "index.html").read_text(encoding="utf-8")
    assert "provider readiness" in control_panel_js
    assert "Provider Readiness" in wrapper_html
    assert "Wrapper usable providers" in visualizer_js


def test_openai_compatible_chat_completions_feeds_release_runtime(tmp_path: Path):
    project_root = make_project(tmp_path)
    sandbox_command = _write_release_wrapper_auto_governance_probe(project_root)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "mock/default",
            "messages": [
                {"role": "system", "content": "Keep answers short."},
                {"role": "user", "content": "Say hello through the wrapper."},
            ],
            "user": "openai-compat-user",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["object"] == "chat.completion"
    assert payload["id"].startswith("chatcmpl-")
    assert payload["model"]
    assert payload["choices"][0]["message"]["role"] == "assistant"
    assert payload["choices"][0]["message"]["content"]
    assert payload["choices"][0]["finish_reason"] == "stop"
    assert payload["usage"]["total_tokens"] >= payload["usage"]["completion_tokens"]
    assert payload["nexusnet"]["wrapper_mode"] == "openai-compatible"
    assert payload["nexusnet"]["release_runtime_ref"] == "/ops/wrapper/release-runtime"

    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": "openai-compat-user"}).json()
    assert runtime["entrypoint"]["runtime_state"] == "live-bound"
    assert runtime["global_growth"]["users"] >= 1
    assert runtime["global_growth"]["runtime_interaction_count"] >= 2
    growth_receipt = runtime["global_growth"]["latest_runtime_receipt"]
    assert growth_receipt["surface_id"] == "multi-user-runtime-growth-receipt"
    assert growth_receipt["user_ref"] != "openai-compat-user"
    assert growth_receipt["raw_content_included"] is False
    assert growth_receipt["federated_packet"]["raw_content_included"] is False
    assert runtime["latest_interaction"]["runtime_growth_receipt_id"].startswith("runtime-growth::")
    assert runtime["federated_packet_count"] == 1
    assert runtime["production_spine"]["packet_count"] == 1
    interaction = runtime["latest_interaction"]
    dream_queue = runtime["dream_research_queue"]
    cycle = runtime["nexusbrain_runtime_cycle"]
    cycle_receipt = cycle["latest_receipt"]
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": "openai-compat-user"}).json()
    readiness_runner = status_card["release_readiness_evidence_runner"]
    assert interaction["improvement_queue_id"] == dream_queue["latest_item"]["queue_id"]
    assert interaction["dream_research_episode_id"] == dream_queue["latest_item"]["research_episode_id"]
    assert interaction["autonomous_update_lifecycle_status"] == "completed"
    assert interaction["autonomous_update_lifecycle_update_id"] == interaction["autonomous_update_proposal_id"]
    lifecycle_run = readiness_runner["latest_autonomous_update_lifecycle_run"]
    assert readiness_runner["latest_autonomous_update_lifecycle_status"] == "completed"
    assert readiness_runner["latest_autonomous_update_lifecycle_run_id"] == (
        interaction["autonomous_update_lifecycle_run_id"]
    )
    assert readiness_runner["latest_autonomous_update_lifecycle_update_id"] == (
        interaction["autonomous_update_lifecycle_update_id"].replace(":", "_")
    )
    assert lifecycle_run["command"] == sandbox_command
    assert lifecycle_run["actions"]["rollback"]["status"] == "rolled-back"
    assert lifecycle_run["active_production_mutated"] is False
    cycle_stage_statuses = {stage["stage_id"]: stage["status"] for stage in cycle_receipt["stages"]}
    assert cycle["latest_status"] == "covered"
    assert cycle_stage_statuses["self_repair_update_governance"] == "covered"
    assert cycle_receipt["evidence_refs"]["dream_research_episode_id"] == interaction["dream_research_episode_id"]
    assert cycle_receipt["evidence_refs"]["autonomous_update_lifecycle_run_id"] == (
        interaction["autonomous_update_lifecycle_run_id"]
    )
    restarted = TestClient(create_app(str(project_root)))
    replayed = restarted.get("/ops/wrapper/release-runtime", params={"session_id": "openai-compat-user"}).json()
    replayed_interaction = replayed["latest_interaction"]
    replayed_cycle_receipt = replayed["nexusbrain_runtime_cycle"]["latest_receipt"]
    assert replayed_interaction["dream_research_episode_id"] == interaction["dream_research_episode_id"]
    assert replayed_interaction["autonomous_update_lifecycle_run_id"] == (
        interaction["autonomous_update_lifecycle_run_id"]
    )
    assert replayed["nexusbrain_runtime_cycle"]["latest_status"] == "covered"
    assert replayed_cycle_receipt["evidence_refs"]["dream_research_episode_id"] == interaction["dream_research_episode_id"]
    assert replayed_cycle_receipt["evidence_refs"]["autonomous_update_lifecycle_run_id"] == (
        interaction["autonomous_update_lifecycle_run_id"]
    )
    assert "Say hello through the wrapper" not in str(runtime)
    control_panel_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "runtime growth bridge" in control_panel_js
    assert "latest runtime growth receipt" in control_panel_js
    assert "shared growth fed packet" in control_panel_js


def test_openai_compatible_chat_completions_can_use_wrapper_provider_pool(tmp_path: Path):
    client = TestClient(create_app(str(make_project(tmp_path))))

    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": "Provider pool smoke."}],
            "user": "provider-pool-user",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["model"] == "nexusnet-offline"
    assert "[nexusnet-offline] Provider pool smoke." in payload["choices"][0]["message"]["content"]
    assert payload["nexusnet"]["provider_id"] == "nexusnet-offline"
    assert payload["nexusnet"]["provider_local"] is True
    assert payload["nexusnet"]["wrapper_mode"] == "openai-compatible"

    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": "provider-pool-user"}).json()
    assert runtime["entrypoint"]["runtime_state"] == "live-bound"
    assert runtime["latest_interaction"]["source_model"] == "nexusnet-offline"
    assert runtime["federated_packet_count"] == 1
    assert runtime["production_spine"]["packet_count"] == 1
    heartbeat = runtime["project_heartbeat"]
    assert heartbeat["surface_id"] == "nexusnet-project-heartbeat"
    assert heartbeat["status"] == "alive"
    assert heartbeat["raw_content_included"] is False
    assert heartbeat["active_production_mutation_allowed"] is False
    assert heartbeat["active_production_mutated"] is False
    assert runtime["latest_interaction"]["project_heartbeat_id"] == heartbeat["heartbeat_id"]
    assert runtime["latest_interaction"]["project_heartbeat_source_run_id"] == heartbeat["source_run_id"]


def test_openai_compatible_provider_chat_records_sanitized_ao_receipt(tmp_path: Path):
    client = TestClient(create_app(str(make_project(tmp_path))))

    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": "Run an eval smoke gate through the provider pool."}],
            "user": "provider-ao-user",
        },
    )

    assert response.status_code == 200
    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": "provider-ao-user"}).json()
    aos = client.get("/ops/brain/aos").json()

    assert aos["execution_count"] >= 1 + len(REQUIRED_CANONICAL_AOS)
    receipt = _ao_receipt_for_trace(aos, runtime["latest_interaction"]["trace_id"])
    assert receipt["surface_id"] == "ao-execution-receipt"
    assert receipt["ao_name"] == "EvalsAO"
    assert receipt["trace_ref"] == f"trace::{runtime['latest_interaction']['trace_id']}"
    assert receipt["input_contract"] == "nexusbrain-command-envelope-and-trace-only"
    assert receipt["direct_local_state_reads"] == []
    assert receipt["raw_content_included"] is False
    assert receipt["wrapper_mode"] == "openai-compatible"
    assert runtime["canonical_ao_coverage"]["passed"] is True
    assert set(runtime["canonical_ao_coverage"]["covered_aos"]) >= REQUIRED_CANONICAL_AOS
    assert runtime["latest_interaction"]["selected_ao"] == "EvalsAO"
    assert runtime["latest_interaction"]["ao_execution_receipt_id"] == receipt["execution_id"]
    assert "Run an eval smoke gate" not in json.dumps(aos)
    assert "provider-ao-user" not in json.dumps(aos)


def test_provider_domain_ao_routing_surfaces_real_prompt_receipts_without_raw_content(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    prompts = [
        "Write Python code to fix a traceback in the repo.",
        "Research assimilation targets and cite source evidence.",
        "Import federated peer packet and check poisoning risk.",
    ]
    for prompt in prompts:
        response = client.post(
            "/v1/chat/completions",
            json={
                "model": "nexusnet-offline",
                "messages": [{"role": "user", "content": prompt}],
                "user": "provider-domain-ao-user",
            },
        )
        assert response.status_code == 200

    replay_response = client.post(
        "/ops/wrapper/domain-expert-growth/admin-replay",
        json={
            "session_id": "provider-domain-ao-user",
            "domain_ao": "FederationAO",
            "approved_by": "release-wrapper-test-admin",
            "approval_ref": "test-admin::domain-expert-growth-replay",
            "requested_decision": "approved",
        },
    )
    assert replay_response.status_code == 200
    admin_replay = replay_response.json()
    assert admin_replay["surface_id"] == "release-wrapper-domain-expert-growth-admin-replay"
    assert admin_replay["status"] == "recorded"
    assert admin_replay["approval_ref"]["status"] == "approved"
    assert admin_replay["admin_eval_replay_ref"]["status"] == "passed-shadow"
    assert admin_replay["admin_eval_replay_ref"]["operator_approved"] is True
    assert admin_replay["admin_eval_replay_ref"]["promotion_allowed"] is True
    assert admin_replay["admin_eval_replay_ref"]["active_production_mutation_allowed"] is False
    assert admin_replay["admin_promotion_decision_ref"]["status"] == "recorded"
    assert admin_replay["admin_promotion_decision_ref"]["requested_decision"] == "approved"
    assert admin_replay["admin_promotion_decision_ref"]["decision"] == "approved"
    assert admin_replay["admin_promotion_decision_ref"]["governance_decision"] == "approved"
    assert admin_replay["admin_promotion_decision_ref"]["rollback_reference"]
    sandbox_takeover_evidence_ref = admin_replay["sandbox_takeover_evidence_ref"]
    assert sandbox_takeover_evidence_ref["surface_id"] == "domain-expert-growth-sandbox-takeover-evidence-ref"
    assert sandbox_takeover_evidence_ref["status"] == "recorded"
    assert sandbox_takeover_evidence_ref["teacher_evidence_bundle_id"]
    assert sandbox_takeover_evidence_ref["takeover_scorecard_id"]
    assert sandbox_takeover_evidence_ref["evidence_run_count"] >= 5
    assert sandbox_takeover_evidence_ref["active_production_mutation_allowed"] is False
    assert sandbox_takeover_evidence_ref["raw_content_included"] is False
    assert sandbox_takeover_evidence_ref["growth_archive_candidate_ref"]["status"] == "recorded"
    assert sandbox_takeover_evidence_ref["growth_archive_candidate_ref"]["candidate_type"] == "model"
    assert sandbox_takeover_evidence_ref["growth_archive_candidate_ref"]["promotion_state"] == "archived-shadow"
    assert admin_replay["promotion_evaluation_ref"]["status"] == "recorded"
    assert admin_replay["promotion_evaluation_ref"]["decision"] == "approved"
    assert admin_replay["promotion_evaluation_ref"]["teacher_evidence_bundle_id"] == sandbox_takeover_evidence_ref["teacher_evidence_bundle_id"]
    assert admin_replay["active_production_mutation_allowed"] is False

    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": "provider-domain-ao-user"}).json()
    readiness = client.get("/ops/wrapper/release-readiness", params={"session_id": "provider-domain-ao-user"}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": "provider-domain-ao-user"}).json()
    visualizer = client.get(
        "/ops/brain/visualizer/state",
        params={"session_id": "provider-domain-ao-user"},
    ).json()
    aos = client.get("/ops/brain/aos").json()
    checks = {check["check_id"]: check for check in readiness["readiness_checks"]}

    domain_routing = runtime["domain_ao_routing"]
    domain_teacher_eval = runtime["domain_teacher_eval_handoff"]
    readiness_routing = readiness["evidence"]["domain_ao_routing"]
    readiness_teacher_eval = readiness["evidence"]["domain_teacher_eval_handoff"]
    selected_domain_aos = set(domain_routing["selected_domain_aos"])
    handoff_by_ao = {handoff["domain_ao"]: handoff for handoff in domain_teacher_eval["handoffs"]}
    assert REQUIRED_DOMAIN_ROUTED_AOS <= selected_domain_aos
    assert domain_routing["surface_id"] == "release-wrapper-domain-ao-routing"
    assert domain_routing["status_label"] == "STRONG ACCEPTED DIRECTION"
    assert domain_routing["passed"] is True
    assert domain_routing["route_count"] >= len(REQUIRED_DOMAIN_ROUTED_AOS)
    assert domain_routing["latest_domain_ao"] == "FederationAO"
    assert domain_routing["raw_content_included"] is False
    assert domain_routing["active_production_mutation_allowed"] is False
    assert all(route["raw_content_included"] is False for route in domain_routing["routes"])
    assert all(route["active_production_mutation_allowed"] is False for route in domain_routing["routes"])
    assert readiness_routing["passed"] is True
    assert set(readiness_routing["selected_domain_aos"]) >= REQUIRED_DOMAIN_ROUTED_AOS
    assert checks["domain-ao-routing"]["status"] == "pass"
    assert domain_teacher_eval["surface_id"] == "release-wrapper-domain-teacher-eval-handoff"
    assert domain_teacher_eval["status_label"] == "STRONG ACCEPTED DIRECTION"
    assert domain_teacher_eval["passed"] is True
    assert domain_teacher_eval["handoff_count"] >= len(REQUIRED_DOMAIN_ROUTED_AOS)
    assert set(domain_teacher_eval["selected_domain_aos"]) >= REQUIRED_DOMAIN_ROUTED_AOS
    assert domain_teacher_eval["latest_domain_ao"] == "FederationAO"
    assert domain_teacher_eval["expert_growth_candidate_count"] >= len(REQUIRED_DOMAIN_ROUTED_AOS)
    assert domain_teacher_eval["latest_growth_cycle_id"]
    assert domain_teacher_eval["latest_promotion_candidate_id"]
    assert domain_teacher_eval["admin_eval_replay_count"] >= 1
    assert domain_teacher_eval["latest_admin_eval_replay_id"] == admin_replay["admin_eval_replay_ref"]["run_id"]
    assert domain_teacher_eval["latest_admin_promotion_decision_id"] == admin_replay["admin_promotion_decision_ref"]["decision_id"]
    assert domain_teacher_eval["latest_admin_promotion_decision"] == "approved"
    assert domain_teacher_eval["latest_sandbox_takeover_evidence_id"] == sandbox_takeover_evidence_ref["evidence_id"]
    assert domain_teacher_eval["latest_teacher_evidence_bundle_id"] == sandbox_takeover_evidence_ref["teacher_evidence_bundle_id"]
    assert domain_teacher_eval["latest_takeover_scorecard_id"] == sandbox_takeover_evidence_ref["takeover_scorecard_id"]
    assert domain_teacher_eval["latest_growth_archive_candidate_id"] == sandbox_takeover_evidence_ref["growth_archive_candidate_ref"]["candidate_id"]
    assert domain_teacher_eval["raw_content_included"] is False
    assert domain_teacher_eval["active_production_mutation_allowed"] is False
    assert readiness_teacher_eval["passed"] is True
    assert checks["domain-teacher-eval-handoff"]["status"] == "pass"
    assert checks["domain-expert-growth-admin-replay"]["status"] == "pass"
    assert checks["domain-expert-growth-sandbox-takeover-evidence"]["status"] == "pass"
    assert set(readiness_teacher_eval["selected_domain_aos"]) >= REQUIRED_DOMAIN_ROUTED_AOS
    assert handoff_by_ao["CodingAO"]["teacher_subject"] == "coder"
    assert handoff_by_ao["ResearchAO"]["teacher_subject"] == "researcher"
    assert handoff_by_ao["FederationAO"]["teacher_subject"] == "strategist"
    for handoff in handoff_by_ao.values():
        assert handoff["teacher_registry"]["status"] == "linked"
        assert handoff["teacher_registry"]["selected_teacher_roles"]["primary"]
        assert handoff["teacher_registry"]["selected_teachers"]
        assert handoff["eval_registry_ref"]["status"] == "registered"
        assert handoff["eval_registry_ref"]["suite_status"] == "active"
        assert handoff["eval_registry_ref"]["suite_promotion_gate"] == "passed"
        assert handoff["eval_registry_ref"]["shadow_run_status"] == "blocked"
        growth_candidate = handoff["expert_growth_candidate"]
        assert growth_candidate["status"] == "recorded-shadow"
        assert growth_candidate["teacher_subject"] == handoff["teacher_subject"]
        assert growth_candidate["growth_cycle_ref"]["status"] in {"shadow_specialist", "blocked"}
        assert growth_candidate["growth_cycle_ref"]["actual_weight_mutation_allowed"] is False
        assert growth_candidate["promotion_candidate_ref"]["candidate_kind"] == "native-takeover"
        if handoff["domain_ao"] == "FederationAO":
            assert growth_candidate["promotion_candidate_ref"]["review_status"] == "approved"
        else:
            assert growth_candidate["promotion_candidate_ref"]["review_status"] in {"shadow", "review"}
        assert growth_candidate["promotion_candidate_ref"]["active_production_mutation_allowed"] is False
        assert growth_candidate["promotion_evaluation_ref"]["decision"] in {"shadow", "rejected", "approved"}
        assert growth_candidate["promotion_decision_ref"]["decision"] == "shadow"
        assert growth_candidate["promotion_decision_ref"]["governance_decision"] == "shadow"
        assert growth_candidate["raw_content_included"] is False
        assert growth_candidate["active_production_mutation_allowed"] is False
        assert handoff["raw_content_included"] is False
        assert handoff["active_production_mutation_allowed"] is False
    federation_growth_candidate = handoff_by_ao["FederationAO"]["expert_growth_candidate"]
    assert federation_growth_candidate["admin_eval_replay_ref"]["status"] == "passed-shadow"
    assert federation_growth_candidate["admin_eval_replay_ref"]["operator_approved"] is True
    assert federation_growth_candidate["admin_eval_replay_ref"]["promotion_allowed"] is True
    assert federation_growth_candidate["sandbox_takeover_evidence_ref"]["evidence_id"] == sandbox_takeover_evidence_ref["evidence_id"]
    assert federation_growth_candidate["sandbox_takeover_evidence_ref"]["takeover_scorecard_id"] == sandbox_takeover_evidence_ref["takeover_scorecard_id"]
    assert federation_growth_candidate["promotion_evaluation_ref"]["decision"] == "approved"
    assert federation_growth_candidate["admin_promotion_decision_ref"]["decision"] == "approved"
    assert federation_growth_candidate["admin_promotion_decision_ref"]["rollback_reference"]
    assert federation_growth_candidate["admin_promotion_decision_ref"]["active_production_mutation_allowed"] is False
    assert status_card["runtime"]["domain_ao_routing"]["latest_domain_ao"] == "FederationAO"
    assert status_card["runtime"]["domain_teacher_eval_handoff"]["latest_domain_ao"] == "FederationAO"
    assert status_card["runtime"]["domain_teacher_eval_handoff"]["latest_admin_eval_replay_id"] == admin_replay["admin_eval_replay_ref"]["run_id"]
    assert status_card["runtime"]["domain_teacher_eval_handoff"]["latest_sandbox_takeover_evidence_id"] == sandbox_takeover_evidence_ref["evidence_id"]
    assert (
        status_card["operator_action_lane"]["latest_action_statuses"]["domain_expert_growth_admin_replay"]
        == "passed-shadow"
    )
    assert (
        status_card["operator_action_lane"]["latest_action_statuses"]["domain_expert_growth_sandbox_takeover_evidence"]
        == "recorded"
    )
    assert (
        visualizer["overlay_state"]["control_panel"]["release_wrapper_runtime"]["domain_ao_routing"][
            "latest_domain_ao"
        ]
        == "FederationAO"
    )
    assert (
        visualizer["overlay_state"]["control_panel"]["release_wrapper_runtime"]["domain_teacher_eval_handoff"][
            "latest_domain_ao"
        ]
        == "FederationAO"
    )
    assert (
        visualizer["overlay_state"]["control_panel"]["release_wrapper_runtime"]["domain_teacher_eval_handoff"][
            "latest_admin_eval_replay_id"
        ]
        == admin_replay["admin_eval_replay_ref"]["run_id"]
    )
    assert (
        visualizer["overlay_state"]["control_panel"]["release_wrapper_runtime"]["domain_teacher_eval_handoff"][
            "latest_sandbox_takeover_evidence_id"
        ]
        == sandbox_takeover_evidence_ref["evidence_id"]
    )
    assert _ao_receipt_for_trace(aos, runtime["latest_interaction"]["trace_id"])["ao_name"] == "FederationAO"

    restarted = TestClient(create_app(str(project_root)))
    restarted_runtime = restarted.get(
        "/ops/wrapper/release-runtime",
        params={"session_id": "provider-domain-ao-user"},
    ).json()
    restarted_teacher_eval = restarted_runtime["domain_teacher_eval_handoff"]
    assert restarted_teacher_eval["latest_admin_eval_replay_id"] == admin_replay["admin_eval_replay_ref"]["run_id"]
    assert restarted_teacher_eval["latest_sandbox_takeover_evidence_id"] == sandbox_takeover_evidence_ref["evidence_id"]
    assert restarted_teacher_eval["latest_takeover_scorecard_id"] == sandbox_takeover_evidence_ref["takeover_scorecard_id"]
    assert restarted_teacher_eval["latest_admin_promotion_decision"] == "approved"

    control_panel_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    visualizer_js = (project_root / "ui" / "visualizer" / "app.js").read_text(encoding="utf-8")
    wrapper_html = (project_root / "ui" / "wrapper" / "index.html").read_text(encoding="utf-8")
    assert "domain AO routing" in control_panel_js
    assert "domain teacher/eval" in control_panel_js
    assert "expert growth candidates" in control_panel_js
    assert "expert growth admin replay" in control_panel_js
    assert "expert takeover evidence" in control_panel_js
    assert "Wrapper domain AO" in visualizer_js
    assert "Wrapper domain teacher/eval" in visualizer_js
    assert "Wrapper expert growth" in visualizer_js
    assert "Wrapper expert replay" in visualizer_js
    assert "Wrapper takeover evidence" in visualizer_js
    assert "Domain AO Routing" in wrapper_html
    assert "Domain Teacher/Eval Handoff" in wrapper_html
    assert "Expert Growth Candidates" in wrapper_html
    assert "Expert Growth Admin Replay" in wrapper_html
    assert "Expert Takeover Evidence" in wrapper_html
    assert "Write Python code" not in json.dumps(runtime)
    assert "Research assimilation targets" not in json.dumps(readiness)
    assert "provider-domain-ao-user" not in json.dumps(status_card)
    assert "release-wrapper-test-admin" not in json.dumps(status_card)
    assert "Import federated peer packet" not in json.dumps(visualizer)


def test_domain_expert_growth_admin_replay_approves_research_and_coding_takeover_evidence(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    session_id = "provider-domain-multi-ao-user"

    prompts = [
        "Research assimilation targets and cite source evidence.",
        "Write Python code to fix a traceback in the repo.",
    ]
    for prompt in prompts:
        response = client.post(
            "/v1/chat/completions",
            json={
                "model": "nexusnet-offline",
                "messages": [{"role": "user", "content": prompt}],
                "user": session_id,
            },
        )
        assert response.status_code == 200

    cases = [
        {
            "domain_ao": "ResearchAO",
            "teacher_subject": "researcher",
            "benchmark_family": "long-context study tasks",
            "preferred_fleet_id": "long_context_fleet",
            "budget_class": "LONG_CONTEXT",
            "output_form": "STRUCTURED_PLAN",
        },
        {
            "domain_ao": "CodingAO",
            "teacher_subject": "coder",
            "benchmark_family": "tests green after edits",
            "preferred_fleet_id": "coding_agent_fleet",
            "budget_class": "STANDARD",
            "output_form": "STRUCTURED_PLAN",
        },
    ]
    replay_payloads = {}
    for case in cases:
        response = client.post(
            "/ops/wrapper/domain-expert-growth/admin-replay",
            json={
                "session_id": session_id,
                "domain_ao": case["domain_ao"],
                "approved_by": "release-wrapper-test-admin",
                "approval_ref": f"test-admin::{case['domain_ao']}-expert-growth-replay",
                "requested_decision": "approved",
            },
        )
        assert response.status_code == 200
        payload = response.json()
        replay_payloads[case["domain_ao"]] = payload
        sandbox_ref = payload["sandbox_takeover_evidence_ref"]
        assert payload["status"] == "recorded"
        assert payload["teacher_subject"] == case["teacher_subject"]
        assert payload["promotion_evaluation_ref"]["decision"] == "approved"
        assert payload["admin_promotion_decision_ref"]["decision"] == "approved"
        assert payload["admin_promotion_decision_ref"]["rollback_reference"]
        assert sandbox_ref["status"] == "recorded"
        assert sandbox_ref["teacher_subject"] == case["teacher_subject"]
        assert sandbox_ref["benchmark_family"] == case["benchmark_family"]
        assert sandbox_ref["fleet_profile"]["preferred_fleet_id"] == case["preferred_fleet_id"]
        assert sandbox_ref["fleet_profile"]["budget_class"] == case["budget_class"]
        assert sandbox_ref["fleet_profile"]["output_form"] == case["output_form"]
        assert sandbox_ref["evidence_run_count"] >= 5
        assert sandbox_ref["teacher_evidence_bundle_id"]
        assert sandbox_ref["takeover_scorecard_id"]
        assert sandbox_ref["growth_archive_candidate_ref"]["promotion_state"] == "archived-shadow"
        assert sandbox_ref["active_production_mutation_allowed"] is False
        assert sandbox_ref["raw_content_included"] is False

    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    handoff_by_ao = {
        handoff["domain_ao"]: handoff
        for handoff in runtime["domain_teacher_eval_handoff"]["handoffs"]
    }
    for case in cases:
        growth_candidate = handoff_by_ao[case["domain_ao"]]["expert_growth_candidate"]
        sandbox_ref = growth_candidate["sandbox_takeover_evidence_ref"]
        assert growth_candidate["promotion_evaluation_ref"]["decision"] == "approved"
        assert growth_candidate["admin_promotion_decision_ref"]["decision"] == "approved"
        assert sandbox_ref["benchmark_family"] == case["benchmark_family"]
        assert sandbox_ref["fleet_profile"]["preferred_fleet_id"] == case["preferred_fleet_id"]
        assert sandbox_ref["evidence_id"] == replay_payloads[case["domain_ao"]]["sandbox_takeover_evidence_ref"]["evidence_id"]


def test_provider_ao_execution_receipts_persist_replay_and_feed_release_readiness(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": "Replay AO receipt after restart."}],
            "user": "provider-ao-replay-user",
        },
    )

    assert response.status_code == 200
    before_aos = client.get("/ops/brain/aos").json()
    runtime_before = client.get(
        "/ops/wrapper/release-runtime",
        params={"session_id": "provider-ao-replay-user"},
    ).json()
    before_receipt = _ao_receipt_for_trace(
        before_aos,
        runtime_before["latest_interaction"]["trace_id"],
    )
    active_ao_names = {ao["name"] for ao in before_aos["active_aos"]}
    assert REQUIRED_CANONICAL_AOS <= active_ao_names
    assert before_aos["execution_count"] >= 1 + len(REQUIRED_CANONICAL_AOS)
    assert before_receipt["artifact_path"].endswith(".json")
    assert Path(before_receipt["artifact_path"]).exists()

    restarted = TestClient(create_app(str(project_root)))
    after_aos = restarted.get("/ops/brain/aos").json()
    after_receipt = next(
        receipt
        for receipt in after_aos["execution_receipts"]
        if receipt["execution_id"] == before_receipt["execution_id"]
    )
    runtime = restarted.get(
        "/ops/wrapper/release-runtime",
        params={"session_id": "provider-ao-replay-user"},
    ).json()
    readiness = restarted.get(
        "/ops/wrapper/release-readiness",
        params={"session_id": "provider-ao-replay-user"},
    ).json()
    checks = {check["check_id"]: check for check in readiness["readiness_checks"]}

    assert after_aos["execution_count"] >= 1 + len(REQUIRED_CANONICAL_AOS)
    assert after_aos["replay"]["status"] == "replayed"
    assert after_receipt["execution_id"] == before_receipt["execution_id"]
    assert after_receipt["raw_content_included"] is False
    assert after_receipt["direct_local_state_reads"] == []
    canonical_coverage = runtime["canonical_ao_coverage"]
    readiness_coverage = readiness["evidence"]["canonical_ao_coverage"]
    assert canonical_coverage["surface_id"] == "release-wrapper-canonical-ao-coverage"
    assert canonical_coverage["passed"] is True
    assert set(canonical_coverage["required_aos"]) == REQUIRED_CANONICAL_AOS
    assert set(canonical_coverage["covered_aos"]) >= REQUIRED_CANONICAL_AOS
    assert canonical_coverage["missing_aos"] == []
    assert canonical_coverage["receipt_count"] >= len(REQUIRED_CANONICAL_AOS)
    assert canonical_coverage["raw_content_included"] is False
    assert canonical_coverage["active_production_mutation_allowed"] is False
    assert readiness_coverage["passed"] is True
    assert set(readiness_coverage["covered_aos"]) >= REQUIRED_CANONICAL_AOS
    replayed_runtime_receipts = {
        receipt["execution_id"] for receipt in runtime["ao_execution_receipts"]["execution_receipts"]
    }
    assert before_receipt["execution_id"] in replayed_runtime_receipts
    assert runtime["ao_execution_receipts"]["replay"]["status"] == "replayed"
    assert checks["ao-execution-receipt"]["status"] == "pass"
    assert checks["canonical-ao-coverage"]["status"] == "pass"
    replayed_readiness_receipts = {
        receipt["execution_id"]
        for receipt in readiness["evidence"]["ao_execution_receipts"]["execution_receipts"]
    }
    assert before_receipt["execution_id"] in replayed_readiness_receipts
    assert readiness["evidence"]["ao_execution_receipts"]["replay"]["status"] == "replayed"
    status_card = restarted.get(
        "/ops/wrapper/status-card",
        params={"session_id": "provider-ao-replay-user"},
    ).json()
    visualizer = restarted.get(
        "/ops/brain/visualizer/state",
        params={"session_id": "provider-ao-replay-user"},
    ).json()
    assert status_card["runtime"]["canonical_ao_coverage"]["passed"] is True
    assert visualizer["overlay_state"]["control_panel"]["release_wrapper_runtime"]["canonical_ao_coverage"]["passed"] is True
    control_panel_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    visualizer_js = (project_root / "ui" / "visualizer" / "app.js").read_text(encoding="utf-8")
    wrapper_html = (project_root / "ui" / "wrapper" / "index.html").read_text(encoding="utf-8")
    assert "canonical AO coverage" in control_panel_js
    assert "Wrapper canonical AOs" in visualizer_js
    assert "Canonical AO Coverage" in wrapper_html
    assert "Replay AO receipt after restart" not in json.dumps(after_aos)
    assert "provider-ao-replay-user" not in json.dumps(after_aos)
    assert "Replay AO receipt after restart" not in json.dumps(readiness)
    assert "provider-ao-replay-user" not in json.dumps(readiness)


def test_openai_compatible_provider_failure_records_degraded_forward_pass_receipt(monkeypatch, tmp_path: Path):
    class FailingProvider:
        provider_id = "deterministic-failing-provider"
        is_local = True

        def complete(self, messages):
            return {
                "ok": False,
                "text": "",
                "model": "deterministic-failing-model",
                "local": True,
                "error": "simulated provider failure",
            }

    registry = ProviderRegistry()
    registry.register(FailingProvider())
    monkeypatch.setattr(nexus_api_app, "_default_provider_registry", lambda **_: registry)
    project_root = make_project(tmp_path)
    sandbox_command = _write_release_wrapper_auto_governance_probe(project_root)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "deterministic-failing-provider",
            "messages": [{"role": "user", "content": "Provider failure should not leak raw prompt secret-123."}],
            "user": "provider-failure-user",
        },
    )

    assert response.status_code == 502
    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": "provider-failure-user"}).json()
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": "provider-failure-user"}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "provider-failure-user"}).json()
    readiness = client.get("/ops/wrapper/release-readiness", params={"session_id": "provider-failure-user"}).json()
    checks = {check["check_id"]: check for check in readiness["readiness_checks"]}
    control_panel = visualizer["overlay_state"]["control_panel"]
    coverage = runtime["forward_pass_coverage"]
    receipt = coverage["latest_receipt"]
    cycle = runtime["nexusbrain_runtime_cycle"]
    heartbeat = runtime["project_heartbeat"]
    native_heartbeat = runtime["native_hive_heartbeat"]
    native_watchdog = runtime["native_hive_heartbeat_watchdog"]
    dream_queue = runtime["dream_research_queue"]
    autonomous_updates = runtime["autonomous_updates"]
    self_repair = runtime["self_repair_ledger"]
    readiness_runner = status_card["release_readiness_evidence_runner"]
    action_lane = status_card["operator_action_lane"]
    expert_node = runtime["latest_interaction"]["expert_node"]
    failure_learning = runtime["latest_interaction"]["failure_learning_signal"]
    runtime_failure_learning = runtime["live_wrapper_telemetry"]["failure_learning"]
    status_failure_learning = status_card["runtime"]["live_wrapper_telemetry"]["failure_learning"]
    visualizer_failure_learning = visualizer["overlay_state"]["control_panel"]["release_wrapper_telemetry"]["failure_learning"]

    assert coverage["receipt_count"] == 1
    assert coverage["latest_status"] == "covered"
    assert receipt["surface_id"] == "release-wrapper-forward-pass-receipt"
    assert heartbeat["surface_id"] == "nexusnet-project-heartbeat"
    assert heartbeat["status"] == "alive"
    assert heartbeat["raw_content_included"] is False
    assert heartbeat["active_production_mutation_allowed"] is False
    assert heartbeat["active_production_mutated"] is False
    assert runtime["latest_interaction"]["hive_run_id"] == heartbeat["source_run_id"]
    assert runtime["latest_interaction"]["project_heartbeat_id"] == heartbeat["heartbeat_id"]
    assert runtime["latest_interaction"]["project_heartbeat_source_run_id"] == heartbeat["source_run_id"]
    assert runtime["latest_interaction"]["project_heartbeat_status"] == "alive"
    assert status_card["project_heartbeat"]["heartbeat_id"] == heartbeat["heartbeat_id"]
    assert control_panel["project_heartbeat"]["heartbeat_id"] == heartbeat["heartbeat_id"]
    assert native_heartbeat["surface_id"] == "release-wrapper-native-hive-heartbeat"
    assert native_heartbeat["status"] == "covered"
    assert native_heartbeat["runtime_state"] == "live-bound"
    assert native_heartbeat["session_ref_digest"] == runtime["latest_interaction"]["session_ref_digest"]
    assert native_heartbeat["trace_ref"] == f"trace::{runtime['latest_interaction']['trace_id']}"
    assert native_heartbeat["hive_run_ref"] == f"hive-forward::{runtime['latest_interaction']['hive_run_id']}"
    assert native_heartbeat["heartbeat_id"].startswith("native-hive-heartbeat::")
    assert native_heartbeat["heartbeat_count"] == 1
    assert native_heartbeat["latest_fresh"] is True
    assert native_heartbeat["freshness_status"] == "fresh"
    assert native_heartbeat["covered_count"] == len(native_heartbeat["required_organs"])
    assert native_heartbeat["degraded_count"] == 0
    assert native_heartbeat["raw_content_included"] is False
    assert native_heartbeat["active_production_mutation_allowed"] is False
    assert native_heartbeat["active_production_mutated"] is False
    native_organs = {organ["organ_id"]: organ for organ in native_heartbeat["organs"]}
    assert native_organs["neural_bus"]["status"] == "covered"
    assert native_organs["hive_blackboard"]["status"] == "covered"
    assert native_organs["plane_trace"]["status"] == "covered"
    assert native_organs["federated_learning_packet"]["status"] == "covered"
    assert native_organs["federated_prior_update"]["status"] == "covered"
    assert native_organs["runtime_growth_receipt"]["status"] == "covered"
    assert native_organs["dream_research_queue"]["status"] == "covered"
    assert "dream_research_queue_missing" not in native_heartbeat["blockers"]
    assert runtime["latest_interaction"]["native_hive_heartbeat_id"] == native_heartbeat["heartbeat_id"]
    assert runtime["latest_interaction"]["improvement_queue_id"] == dream_queue["latest_item"]["queue_id"]
    assert runtime["latest_interaction"]["dream_research_episode_id"] == dream_queue["latest_item"]["research_episode_id"]
    assert native_heartbeat["heartbeat_history"]["latest_heartbeat_id"] == native_heartbeat["heartbeat_id"]
    assert native_heartbeat["heartbeat_history"]["latest_fresh"] is True
    assert native_heartbeat["heartbeat_history"]["raw_content_included"] is False
    assert native_watchdog["surface_id"] == "release-wrapper-native-hive-heartbeat-watchdog"
    assert native_watchdog["status"] == "fresh"
    assert native_watchdog["latest_fresh"] is True
    assert native_watchdog["latest_heartbeat_id"] == native_heartbeat["heartbeat_id"]
    assert native_watchdog["artifact_ref"] == "release-wrapper-runtime/native-hive-heartbeats.jsonl"
    assert native_watchdog["raw_content_included"] is False
    assert status_card["runtime"]["native_hive_heartbeat"]["heartbeat_id"] == native_heartbeat["heartbeat_id"]
    assert control_panel["release_wrapper_runtime"]["native_hive_heartbeat"]["heartbeat_id"] == native_heartbeat["heartbeat_id"]
    assert receipt["covered_count"] == len(receipt["required_stages"])
    assert receipt["degraded_count"] == 0
    assert receipt["raw_content_included"] is False
    assert receipt["active_production_mutation_allowed"] is False
    stage_statuses = {stage["stage_id"]: stage["status"] for stage in receipt["stages"]}
    assert stage_statuses["continuous_assimilation"] == "covered"
    assert stage_statuses["global_growth"] == "covered"
    assert stage_statuses["federated_packet"] == "covered"
    assert stage_statuses["production_spine"] == "covered"
    assert stage_statuses["developmental_cortex"] == "covered"
    assert stage_statuses["dream_research_queue"] == "covered"
    assert runtime["latest_interaction"]["status"] == "error"
    assert runtime["continuous_assimilation"]["nodes"][expert_node]["captures"] == 1
    assert runtime["continuous_assimilation"]["nodes"][expert_node]["ready_to_train"] is False
    assert runtime["continuous_assimilation"]["provenance"][expert_node][0]["source_model"] == "deterministic-failing-model"
    assert runtime["global_growth"]["users"] >= 1
    assert runtime["global_growth"]["global_captures"] >= 2
    assert runtime["global_growth"]["session_captures"] >= 1
    assert failure_learning["surface_id"] == "release-wrapper-failure-learning-signal"
    assert failure_learning["status"] == "captured"
    assert failure_learning["continuous_assimilation_captured"] is True
    assert failure_learning["global_growth_captured"] is True
    assert failure_learning["continuous_assimilation_capture_ref"] == f"assimilation-node::{expert_node}"
    assert failure_learning["global_growth_receipt_id"].startswith("runtime-growth::")
    assert runtime["latest_interaction"]["continuous_assimilation_capture_ref"] == (
        failure_learning["continuous_assimilation_capture_ref"]
    )
    assert runtime["latest_interaction"]["global_growth_receipt_id"] == failure_learning["global_growth_receipt_id"]
    assert runtime["latest_interaction"]["developmental_cortex_assessment_ref"].startswith(
        "release-wrapper-developmental::"
    )
    assert runtime["latest_interaction"]["developmental_cortex_status"] in {"blocked", "shadow-ready"}
    assert runtime["latest_interaction"]["developmental_cortex_growth_candidate_ref"].startswith(
        "growth:release-wrapper-developmental"
    )
    assert runtime["latest_interaction"]["developmental_cortex_promotion_case_ref"].startswith(
        "case:release-wrapper-developmental"
    )
    stage_rows = {stage["stage_id"]: stage for stage in receipt["stages"]}
    assert failure_learning["continuous_assimilation_capture_ref"] in stage_rows["continuous_assimilation"]["evidence_refs"]
    assert failure_learning["global_growth_receipt_id"] in stage_rows["global_growth"]["evidence_refs"]
    assert any(
        ref.startswith("developmental-cortex::")
        for ref in stage_rows["developmental_cortex"]["evidence_refs"]
    )
    assert any(ref.startswith("growth-candidate::") for ref in stage_rows["developmental_cortex"]["evidence_refs"])
    assert any(ref.startswith("promotion-case::") for ref in stage_rows["developmental_cortex"]["evidence_refs"])
    assert failure_learning["raw_content_included"] is False
    assert failure_learning["active_production_mutation_allowed"] is False
    assert runtime_failure_learning["captured_count"] == 1
    assert runtime_failure_learning["latest_status"] == "captured"
    assert status_failure_learning["captured_count"] == 1
    assert visualizer_failure_learning["captured_count"] == 1
    assert runtime["federated_packet_count"] == 1
    assert runtime["latest_federated_packet"]["status"] == "degraded"
    assert runtime["latest_federated_packet"]["raw_content_included"] is False
    assert runtime["production_spine"]["packet_count"] == 1
    assert runtime["production_spine"]["latest_packet"]["shadow_routing_influence"]["active_route_mutation_allowed"] is False
    assert runtime["production_spine"]["latest_packet"]["raw_content_included"] is False
    assert dream_queue["surface_id"] == "release-wrapper-dream-research-queue"
    assert dream_queue["status"] == "live-bound"
    assert dream_queue["item_count"] == 1
    assert dream_queue["episode_count"] == 1
    assert dream_queue["latest_item"]["research_status"] == "researched"
    assert dream_queue["latest_item"]["metadata"]["source_model"] == "deterministic-failing-model"
    assert dream_queue["latest_item"]["metadata"]["expert_node"] == expert_node
    assert dream_queue["latest_item"]["metadata"]["failure_class"] == "model_interaction_failed"
    assert dream_queue["latest_item"]["metadata"]["raw_content_included"] is False
    assert dream_queue["latest_item"]["status"] == "reverted"
    assert dream_queue["latest_item"]["governance"]["proposal_status"] == "rolled-back"
    assert dream_queue["latest_item"]["governance"]["active_production_mutation_allowed"] is False
    proposal_id = dream_queue["latest_item"]["governance"]["proposal_update_id"]
    dream_proposal = next(
        proposal
        for proposal in autonomous_updates["proposals"]
        if proposal["update_id"] == proposal_id
    )
    assert dream_proposal["metadata"]["dream_research_queue"] is True
    assert dream_proposal["metadata"]["safe_payload"]["failure_class"] == "model_interaction_failed"
    assert dream_proposal["operator_approved"] is True
    assert dream_proposal["status"] == "rolled-back"
    assert dream_proposal["latest_eval_replay"]["status"] == "passed-shadow"
    assert dream_proposal["latest_eval_replay"]["operator_approved"] is True
    assert dream_proposal["latest_sandbox_test_evidence"]["status"] == "passed"
    assert dream_proposal["latest_sandbox_test_evidence"]["sandbox"]["active_project_root_mutated"] is False
    assert dream_proposal["latest_sandbox_test_evidence"]["diff_summary"]["unsafe_change_count"] == 0
    assert dream_proposal["metadata"]["active_production_mutation_allowed"] is False
    assert autonomous_updates["latest_applied"]["update_id"] == proposal_id
    assert autonomous_updates["latest_applied"]["status"] == "applied-shadow-safe-file"
    assert autonomous_updates["latest_applied"]["active_production_mutated"] is False
    assert autonomous_updates["latest_applied"]["test_evidence_refs"] == [
        dream_proposal["latest_sandbox_test_evidence"]["evidence_ref"]
    ]
    assert autonomous_updates["latest_rollback"]["update_id"] == proposal_id
    assert autonomous_updates["latest_rollback"]["status"] == "rolled-back"
    assert autonomous_updates["latest_rollback"]["rollback_restored"] is True
    assert autonomous_updates["latest_rollback"]["active_production_mutated"] is False
    assert not Path(autonomous_updates["latest_applied"]["safe_file_path"]).exists()
    assert readiness_runner["latest_status"] == "completed"
    assert readiness_runner["latest_run"]["update_id"] == proposal_id.replace(":", "_")
    assert readiness_runner["latest_run"]["command"] == sandbox_command
    assert readiness_runner["latest_run"]["active_production_mutated"] is False
    runner_actions = readiness_runner["latest_run"]["actions"]
    assert runner_actions["admin_approval"]["status"] == "admin-approved"
    assert runner_actions["admin_approval"]["linked_eval_replay"]["status"] == "passed-shadow"
    assert runner_actions["sandbox_tests"]["status"] == "passed"
    assert runner_actions["sandbox_tests"]["sandbox"]["active_project_root_mutated"] is False
    assert runner_actions["apply"]["status"] == "applied-shadow-safe-file"
    assert runner_actions["apply"]["active_production_mutated"] is False
    assert runner_actions["rollback"]["status"] == "rolled-back"
    assert runner_actions["rollback"]["rollback_restored"] is True
    assert runner_actions["rollback"]["active_production_mutated"] is False
    assert self_repair["repair_count"] >= 4
    assert self_repair["active_production_mutated"] is False
    assert self_repair["latest_action"] == "rollback"
    assert self_repair["latest_status"] == "rolled-back"
    assert self_repair["action_counts"]["admin_approval"] == 1
    assert self_repair["action_counts"]["sandbox_tests"] == 1
    assert self_repair["action_counts"]["apply"] == 1
    assert self_repair["action_counts"]["rollback"] == 1
    assert self_repair["ao_guard_passed_count"] >= 4
    assert action_lane["proposal_update_id"] == proposal_id
    assert action_lane["latest_action_statuses"]["admin_approval"] == "admin-approved"
    assert action_lane["latest_action_statuses"]["shadow_eval_replay"] == "passed-shadow"
    assert action_lane["latest_action_statuses"]["sandbox_tests"] == "passed"
    assert action_lane["latest_action_statuses"]["apply"] == "applied-shadow-safe-file"
    assert action_lane["latest_action_statuses"]["rollback"] == "rolled-back"
    assert action_lane["latest_action_statuses"]["readiness_runner"] == "completed"
    assert checks["project-heartbeat"]["status"] == "pass"
    assert readiness["evidence"]["project_heartbeat"]["heartbeat_id"] == heartbeat["heartbeat_id"]
    assert checks["native-hive-heartbeat"]["status"] == "pass"
    assert checks["native-hive-heartbeat-watchdog"]["status"] == "pass"
    assert checks["native-hive-heartbeat-watchdog"]["latest_fresh"] is True
    assert checks["native-hive-heartbeat-watchdog"]["watchdog_ref"] == (
        "release-wrapper-runtime/native-hive-heartbeat-watchdog.json"
    )
    assert readiness["evidence"]["native_hive_heartbeat"]["heartbeat_id"] == native_heartbeat["heartbeat_id"]
    assert checks["forward-pass-coverage"]["status"] == "pass"
    assert checks["nexusbrain-runtime-cycle"]["status"] == "pass"
    assert checks["nexusbrain-runtime-cycle"]["go_no_go_blocking"] is True
    assert checks["nexusbrain-runtime-cycle"]["latest_receipt_id"] == cycle["latest_receipt_id"]
    assert readiness["evidence"]["nexusbrain_runtime_cycle"]["latest_receipt_id"] == cycle["latest_receipt_id"]
    assert "forward-pass coverage receipt is missing or degraded" not in readiness["blockers"]
    sanitized_payload = json.dumps(
        {
            "coverage": coverage,
            "heartbeat": heartbeat,
            "native_heartbeat": native_heartbeat,
            "native_watchdog": native_watchdog,
            "dream_queue": dream_queue,
            "dream_proposal": dream_proposal,
            "interaction": runtime["latest_interaction"],
            "continuous_assimilation": runtime["continuous_assimilation"],
            "global_growth": runtime["global_growth"],
            "runtime_failure_learning": runtime_failure_learning,
            "self_repair": self_repair,
            "readiness_runner": readiness_runner,
            "action_lane": action_lane,
            "status_failure_learning": status_failure_learning,
            "visualizer_failure_learning": visualizer_failure_learning,
            "control_panel_heartbeat": control_panel["project_heartbeat"],
            "status_card_heartbeat": status_card["project_heartbeat"],
            "readiness_heartbeat": readiness["evidence"]["project_heartbeat"],
            "readiness_native_heartbeat": readiness["evidence"]["native_hive_heartbeat"],
            "readiness_native_watchdog_check": checks["native-hive-heartbeat-watchdog"],
            "readiness_dream_queue": readiness["evidence"]["dream_research_queue"],
            "readiness_coverage": readiness["evidence"]["forward_pass_coverage"],
            "readiness_nexusbrain_cycle": readiness["evidence"]["nexusbrain_runtime_cycle"],
        }
    )
    assert "Provider failure should not leak" not in sanitized_payload
    assert "secret-123" not in sanitized_payload
    assert "provider-failure-user" not in sanitized_payload

    control_panel_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    visualizer_js = (project_root / "ui" / "visualizer" / "app.js").read_text(encoding="utf-8")
    wrapper_html = (project_root / "ui" / "wrapper" / "index.html").read_text(encoding="utf-8")
    assert "failure learning captures" in control_panel_js
    assert "release-wrapper-failure-learning" in control_panel_js
    assert "failure learning captures" in visualizer_js
    assert "failure learning captures" in wrapper_html


def test_degraded_provider_forward_pass_records_cache_evidence_and_replays_after_restart(monkeypatch, tmp_path: Path):
    class FailingProvider:
        provider_id = "deterministic-cache-failing-provider"
        is_local = True

        def complete(self, messages):
            return {
                "ok": False,
                "text": "",
                "model": "deterministic-cache-failing-model",
                "local": True,
                "error": "simulated provider cache failure",
            }

    registry = ProviderRegistry()
    registry.register(FailingProvider())
    monkeypatch.setattr(nexus_api_app, "_default_provider_registry", lambda **_: registry)
    project_root = make_project(tmp_path)
    sandbox_command = _write_release_wrapper_auto_governance_probe(project_root)
    client = TestClient(create_app(str(project_root)))
    session_id = "provider-failure-cache-user"
    prompt = "Provider failure cache evidence must not leak SECRET-CACHE-FAIL."

    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "deterministic-cache-failing-provider",
            "messages": [{"role": "user", "content": prompt}],
            "user": session_id,
        },
    )

    assert response.status_code == 502
    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    cache = runtime["effective_context_cache"]
    interaction = runtime["latest_interaction"]
    heartbeat = runtime["project_heartbeat"]
    native_heartbeat = runtime["native_hive_heartbeat"]
    native_watchdog = runtime["native_hive_heartbeat_watchdog"]
    dream_queue = runtime["dream_research_queue"]
    autonomous_updates = runtime["autonomous_updates"]
    self_repair = runtime["self_repair_ledger"]
    status_card = client.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]
    readiness_runner = status_card["release_readiness_evidence_runner"]
    cycle = runtime["nexusbrain_runtime_cycle"]
    cycle_receipt = cycle["latest_receipt"]

    assert "session_id" not in runtime
    assert runtime["session_ref_digest"] == interaction["session_ref_digest"]
    assert runtime["session_ref_digest"] != session_id
    assert runtime["session_scope"] == "session-filtered"
    assert runtime["forward_pass_coverage"]["latest_status"] == "covered"
    assert heartbeat["surface_id"] == "nexusnet-project-heartbeat"
    assert heartbeat["status"] == "alive"
    assert interaction["project_heartbeat_id"] == heartbeat["heartbeat_id"]
    assert interaction["project_heartbeat_source_run_id"] == heartbeat["source_run_id"]
    assert heartbeat["raw_content_included"] is False
    assert heartbeat["active_production_mutation_allowed"] is False
    assert native_heartbeat["surface_id"] == "release-wrapper-native-hive-heartbeat"
    assert native_heartbeat["status"] == "covered"
    assert native_heartbeat["runtime_state"] == "live-bound"
    assert native_heartbeat["hive_run_ref"] == f"hive-forward::{interaction['hive_run_id']}"
    assert native_heartbeat["heartbeat_id"] == interaction["native_hive_heartbeat_id"]
    assert interaction["improvement_queue_id"] == dream_queue["latest_item"]["queue_id"]
    assert interaction["dream_research_episode_id"] == dream_queue["latest_item"]["research_episode_id"]
    assert interaction["continuous_assimilation_capture_ref"].startswith("assimilation-node::")
    assert interaction["global_growth_receipt_id"].startswith("runtime-growth::")
    assert interaction["developmental_cortex_assessment_ref"].startswith("release-wrapper-developmental::")
    assert interaction["developmental_cortex_growth_candidate_ref"].startswith("growth:release-wrapper-developmental")
    assert interaction["developmental_cortex_promotion_case_ref"].startswith("case:release-wrapper-developmental")
    assert native_heartbeat["heartbeat_history"]["latest_heartbeat_id"] == native_heartbeat["heartbeat_id"]
    assert native_heartbeat["heartbeat_history"]["latest_fresh"] is True
    assert native_watchdog["status"] == "fresh"
    assert native_watchdog["latest_heartbeat_id"] == native_heartbeat["heartbeat_id"]
    assert native_watchdog["raw_content_included"] is False
    assert dream_queue["status"] == "live-bound"
    assert dream_queue["latest_item"]["metadata"]["failure_class"] == "model_interaction_failed"
    assert dream_queue["latest_item"]["status"] == "reverted"
    assert dream_queue["latest_item"]["governance"]["proposal_status"] == "rolled-back"
    assert dream_queue["latest_item"]["governance"]["active_production_mutation_allowed"] is False
    proposal_id = dream_queue["latest_item"]["governance"]["proposal_update_id"]
    assert autonomous_updates["latest_applied"]["status"] == "applied-shadow-safe-file"
    assert autonomous_updates["latest_rollback"]["status"] == "rolled-back"
    assert not Path(autonomous_updates["latest_applied"]["safe_file_path"]).exists()
    assert readiness_runner["latest_status"] == "completed"
    assert readiness_runner["latest_run"]["command"] == sandbox_command
    assert readiness_runner["latest_run"]["actions"]["rollback"]["status"] == "rolled-back"
    assert self_repair["action_counts"]["admin_approval"] == 1
    assert self_repair["action_counts"]["sandbox_tests"] == 1
    assert self_repair["action_counts"]["apply"] == 1
    assert self_repair["action_counts"]["rollback"] == 1
    assert self_repair["active_production_mutated"] is False
    assert cache["surface_id"] == "effective-context-cache-ledger"
    assert cache["entry_count"] == 1
    assert cache["latest_entry"]["entry_id"] == interaction["cache_ledger_entry_id"]
    assert cache["latest_entry"]["metadata"]["raw_content_included"] is False
    assert cache["latest_entry"]["metadata"]["active_production_mutation_allowed"] is False
    assert "forward-pass-degraded" not in json.dumps(cache)
    assert cycle["surface_id"] == "nexusbrain-runtime-cycle"
    assert cycle["latest_status"] == "covered"
    assert cycle["receipt_count"] == 1
    assert cycle["covered_count"] == 1
    assert cycle["degraded_count"] == 0
    assert cycle["raw_content_included"] is False
    assert cycle["active_production_mutation_allowed"] is False
    assert cycle["active_production_mutated"] is False
    assert cycle_receipt["surface_id"] == "nexusbrain-runtime-cycle-receipt"
    assert cycle_receipt["status"] == "covered"
    assert cycle_receipt["raw_content_included"] is False
    assert cycle_receipt["active_production_mutation_allowed"] is False
    assert cycle_receipt["active_production_mutated"] is False
    assert interaction["nexusbrain_runtime_cycle_receipt_id"] == cycle_receipt["receipt_id"]
    assert interaction["nexusbrain_runtime_cycle_status"] == "covered"
    assert interaction["nexusbrain_runtime_cycle_receipt"]["receipt_id"] == cycle_receipt["receipt_id"]
    cycle_stage_statuses = {stage["stage_id"]: stage["status"] for stage in cycle_receipt["stages"]}
    assert cycle_stage_statuses == {
        "native_hive_heartbeat": "covered",
        "continuous_assimilation": "covered",
        "global_growth": "covered",
        "federation": "covered",
        "production_spine": "covered",
        "developmental_cortex": "covered",
        "authority_evals_tools": "covered",
        "dream_research": "covered",
        "self_repair_update_governance": "covered",
        "storage_replay": "covered",
    }
    assert cycle_receipt["covered_stage_count"] == len(cycle_receipt["required_stages"])
    assert cycle_receipt["degraded_stage_count"] == 0
    assert cycle_receipt["evidence_refs"]["native_hive_heartbeat_id"] == native_heartbeat["heartbeat_id"]
    assert cycle_receipt["evidence_refs"]["continuous_assimilation_capture_ref"] == (
        interaction["continuous_assimilation_capture_ref"]
    )
    assert cycle_receipt["evidence_refs"]["global_growth_receipt_id"] == interaction["global_growth_receipt_id"]
    assert cycle_receipt["evidence_refs"]["federated_packet_id"] == interaction["federated_packet_id"]
    assert cycle_receipt["evidence_refs"]["production_spine_packet_signature"] == (
        interaction["production_spine_packet_signature"]
    )
    assert cycle_receipt["evidence_refs"]["developmental_cortex_assessment_ref"] == (
        interaction["developmental_cortex_assessment_ref"]
    )
    assert cycle_receipt["evidence_refs"]["dream_research_episode_id"] == interaction["dream_research_episode_id"]
    assert cycle_receipt["evidence_refs"]["autonomous_update_lifecycle_run_id"] == (
        interaction["autonomous_update_lifecycle_run_id"]
    )
    assert cycle_receipt["evidence_refs"]["storage_event_log_ref"] == "release-wrapper-runtime/events.jsonl"
    assert status_card["runtime"]["nexusbrain_runtime_cycle"]["latest_receipt_id"] == cycle_receipt["receipt_id"]
    assert control_panel["release_wrapper_runtime"]["nexusbrain_runtime_cycle"]["latest_receipt_id"] == (
        cycle_receipt["receipt_id"]
    )

    restarted = TestClient(create_app(str(project_root)))
    replayed = restarted.get("/ops/wrapper/release-runtime", params={"session_id": session_id}).json()
    replayed_status_card = restarted.get("/ops/wrapper/status-card", params={"session_id": session_id}).json()
    replayed_visualizer = restarted.get("/ops/brain/visualizer/state", params={"session_id": session_id}).json()
    replayed_cache = replayed["effective_context_cache"]
    replayed_heartbeat = replayed["project_heartbeat"]
    replayed_native_heartbeat = replayed["native_hive_heartbeat"]
    replayed_native_watchdog = replayed["native_hive_heartbeat_watchdog"]
    replayed_dream_queue = replayed["dream_research_queue"]
    replayed_updates = replayed["autonomous_updates"]
    replayed_self_repair = replayed["self_repair_ledger"]
    replayed_runner = replayed_status_card["release_readiness_evidence_runner"]
    replayed_cycle = replayed["nexusbrain_runtime_cycle"]
    assert "session_id" not in replayed
    assert replayed["session_ref_digest"] == runtime["session_ref_digest"]
    assert replayed["session_scope"] == "session-filtered"
    assert replayed_heartbeat["heartbeat_id"] == heartbeat["heartbeat_id"]
    assert replayed_heartbeat["status"] == "alive"
    assert replayed_heartbeat["raw_content_included"] is False
    assert replayed["latest_interaction"]["project_heartbeat_id"] == heartbeat["heartbeat_id"]
    assert replayed_native_heartbeat["heartbeat_id"] == native_heartbeat["heartbeat_id"]
    assert replayed_native_heartbeat["runtime_state"] in {"live-bound", "replayed-history"}
    assert replayed_native_heartbeat["status"] == "covered"
    assert replayed_native_heartbeat["heartbeat_history"]["latest_fresh"] is True
    assert replayed["latest_interaction"]["native_hive_heartbeat_id"] == native_heartbeat["heartbeat_id"]
    assert replayed["latest_interaction"]["improvement_queue_id"] == dream_queue["latest_item"]["queue_id"]
    assert replayed["latest_interaction"]["dream_research_episode_id"] == dream_queue["latest_item"]["research_episode_id"]
    assert replayed["latest_interaction"]["autonomous_update_lifecycle_run_id"] == readiness_runner["latest_run"]["run_id"]
    assert replayed["latest_interaction"]["autonomous_update_lifecycle_status"] == "completed"
    assert replayed["latest_interaction"]["continuous_assimilation_capture_ref"] == (
        interaction["continuous_assimilation_capture_ref"]
    )
    assert replayed["latest_interaction"]["global_growth_receipt_id"] == interaction["global_growth_receipt_id"]
    assert replayed["latest_interaction"]["developmental_cortex_assessment_ref"] == (
        interaction["developmental_cortex_assessment_ref"]
    )
    assert replayed["latest_interaction"]["developmental_cortex_growth_candidate_ref"] == (
        interaction["developmental_cortex_growth_candidate_ref"]
    )
    assert replayed["latest_interaction"]["developmental_cortex_promotion_case_ref"] == (
        interaction["developmental_cortex_promotion_case_ref"]
    )
    assert replayed_native_watchdog["status"] == "fresh"
    assert replayed_native_watchdog["latest_heartbeat_id"] == native_heartbeat["heartbeat_id"]
    assert replayed_dream_queue["latest_item"]["queue_id"] == dream_queue["latest_item"]["queue_id"]
    assert replayed_dream_queue["latest_item"]["research_status"] == "researched"
    assert replayed_dream_queue["latest_item"]["status"] == "reverted"
    assert replayed_dream_queue["latest_item"]["governance"]["proposal_status"] == "rolled-back"
    assert replayed_updates["latest_applied"]["update_id"] == proposal_id
    assert replayed_updates["latest_applied"]["status"] == "applied-shadow-safe-file"
    assert replayed_updates["latest_rollback"]["update_id"] == proposal_id
    assert replayed_updates["latest_rollback"]["status"] == "rolled-back"
    assert replayed_runner["latest_status"] == "completed"
    assert replayed_runner["latest_run"]["run_id"] == readiness_runner["latest_run"]["run_id"]
    assert replayed_runner["latest_run"]["active_production_mutated"] is False
    assert replayed_self_repair["action_counts"]["admin_approval"] == 1
    assert replayed_self_repair["action_counts"]["sandbox_tests"] == 1
    assert replayed_self_repair["action_counts"]["apply"] == 1
    assert replayed_self_repair["action_counts"]["rollback"] == 1
    assert replayed_self_repair["active_production_mutated"] is False
    assert replayed_cache["entry_count"] == 1
    assert replayed_cache["latest_entry"]["entry_id"] == cache["latest_entry"]["entry_id"]
    assert replayed["latest_interaction"]["cache_ledger_entry_id"] == cache["latest_entry"]["entry_id"]
    assert replayed["latest_interaction"]["failure_learning_signal"]["status"] == "captured"
    assert replayed["continuous_assimilation"]["nodes"][replayed["latest_interaction"]["expert_node"]]["captures"] == 1
    assert replayed["global_growth"]["global_captures"] >= 2
    assert replayed["live_wrapper_telemetry"]["failure_learning"]["captured_count"] == 1
    assert replayed["federated_packet_count"] == 1
    assert replayed["latest_federated_packet"]["raw_content_included"] is False
    assert replayed["production_spine"]["packet_count"] == 1
    assert replayed["production_spine"]["latest_packet"]["raw_content_included"] is False
    assert replayed["replay"]["status"] == "replayed"
    assert replayed["forward_pass_coverage"]["latest_status"] == "covered"
    assert replayed_cycle["latest_status"] == "covered"
    assert replayed_cycle["latest_receipt_id"] == cycle_receipt["receipt_id"]
    assert replayed_cycle["latest_receipt"]["receipt_id"] == cycle_receipt["receipt_id"]
    assert replayed_cycle["replay"]["status"] == "replayed"
    assert replayed["latest_interaction"]["nexusbrain_runtime_cycle_receipt_id"] == cycle_receipt["receipt_id"]
    assert replayed_status_card["runtime"]["nexusbrain_runtime_cycle"]["latest_receipt_id"] == (
        cycle_receipt["receipt_id"]
    )
    assert (
        replayed_visualizer["overlay_state"]["control_panel"]["release_wrapper_runtime"]["nexusbrain_runtime_cycle"][
            "latest_receipt_id"
        ]
        == cycle_receipt["receipt_id"]
    )

    serialized = json.dumps(
        {
            "cache": cache,
            "interaction": interaction,
            "replayed_cache": replayed_cache,
            "replayed_interaction": replayed["latest_interaction"],
            "heartbeat": heartbeat,
            "replayed_heartbeat": replayed_heartbeat,
            "native_heartbeat": native_heartbeat,
            "native_watchdog": native_watchdog,
            "dream_queue": dream_queue,
            "autonomous_updates": autonomous_updates,
            "self_repair": self_repair,
            "readiness_runner": readiness_runner,
            "replayed_native_heartbeat": replayed_native_heartbeat,
            "replayed_native_watchdog": replayed_native_watchdog,
            "replayed_dream_queue": replayed_dream_queue,
            "replayed_updates": replayed_updates,
            "replayed_self_repair": replayed_self_repair,
            "replayed_runner": replayed_runner,
            "coverage": runtime["forward_pass_coverage"],
            "replayed_coverage": replayed["forward_pass_coverage"],
            "nexusbrain_cycle": cycle,
            "replayed_nexusbrain_cycle": replayed_cycle,
        }
    )
    assert prompt not in serialized
    assert "SECRET-CACHE-FAIL" not in serialized
    assert session_id not in serialized

    control_panel_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    visualizer_js = (project_root / "ui" / "visualizer" / "app.js").read_text(encoding="utf-8")
    wrapper_html = (project_root / "ui" / "wrapper" / "index.html").read_text(encoding="utf-8")
    assert "NexusBrain runtime cycle" in control_panel_js
    assert "NexusBrain cycle" in visualizer_js
    assert "NexusBrain Cycle" in wrapper_html


def test_openai_compatible_streaming_chat_completions_feeds_release_runtime(tmp_path: Path):
    client = TestClient(create_app(str(make_project(tmp_path))))

    with client.stream(
        "POST",
        "/v1/chat/completions",
        json={
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": "Stream provider smoke."}],
            "user": "stream-provider-user",
            "stream": True,
        },
    ) as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        body = "".join(response.iter_text())

    data_lines = [line.removeprefix("data: ") for line in body.splitlines() if line.startswith("data: ")]
    assert data_lines[-1] == "[DONE]"
    chunks = [json.loads(line) for line in data_lines[:-1]]
    assert all(chunk["object"] == "chat.completion.chunk" for chunk in chunks)
    streamed_text = "".join((chunk["choices"][0]["delta"] or {}).get("content", "") for chunk in chunks)
    assert streamed_text == "[nexusnet-offline] Stream provider smoke."

    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": "stream-provider-user"}).json()
    assert runtime["entrypoint"]["runtime_state"] == "live-bound"
    assert runtime["latest_interaction"]["source_model"] == "nexusnet-offline"
    assert runtime["federated_packet_count"] == 1
    assert runtime["production_spine"]["packet_count"] == 1
    aos = client.get("/ops/brain/aos").json()
    assert aos["execution_count"] >= 1 + len(REQUIRED_CANONICAL_AOS)
    receipt = _ao_receipt_for_trace(aos, runtime["latest_interaction"]["trace_id"])
    assert receipt["trace_ref"] == f"trace::{runtime['latest_interaction']['trace_id']}"
    assert receipt["raw_content_included"] is False
    assert runtime["canonical_ao_coverage"]["passed"] is True
    assert set(runtime["canonical_ao_coverage"]["covered_aos"]) >= REQUIRED_CANONICAL_AOS


def test_v1_models_and_native_chat_are_release_wrapper_entrypoints(tmp_path: Path):
    client = TestClient(create_app(str(make_project(tmp_path))))

    models = client.get("/v1/models")
    assert models.status_code == 200
    model_payload = models.json()
    assert model_payload["object"] == "list"
    ids = {item["id"] for item in model_payload["data"]}
    assert "mock/default" in ids
    assert "nexusnet-offline" in ids
    offline = next(item for item in model_payload["data"] if item["id"] == "nexusnet-offline")
    assert offline["nexusnet"]["source"] == "wrapper-provider"
    assert offline["nexusnet"]["local"] is True

    chat = client.post(
        "/v1/chat",
        json={
            "model": "nexusnet-offline",
            "messages": [{"role": "user", "content": "Native chat smoke."}],
            "session_id": "native-v1-user",
        },
    )
    assert chat.status_code == 200
    chat_payload = chat.json()
    assert chat_payload["ok"] is True
    assert chat_payload["reply"].startswith("[nexusnet-offline]")
    assert chat_payload["model"] == "nexusnet-offline"
    assert chat_payload["nexusnet"]["release_runtime_ref"] == "/ops/wrapper/release-runtime"

    runtime = client.get("/ops/wrapper/release-runtime", params={"session_id": "native-v1-user"}).json()
    assert runtime["entrypoint"]["runtime_state"] == "live-bound"
    assert runtime["latest_interaction"]["source_model"] == "nexusnet-offline"
    aos = client.get("/ops/brain/aos").json()
    assert aos["execution_count"] >= 1 + len(REQUIRED_CANONICAL_AOS)
    receipt = _ao_receipt_for_trace(aos, runtime["latest_interaction"]["trace_id"])
    assert receipt["trace_ref"] == f"trace::{runtime['latest_interaction']['trace_id']}"
    assert receipt["raw_content_included"] is False
    assert runtime["canonical_ao_coverage"]["passed"] is True
    assert set(runtime["canonical_ao_coverage"]["covered_aos"]) >= REQUIRED_CANONICAL_AOS

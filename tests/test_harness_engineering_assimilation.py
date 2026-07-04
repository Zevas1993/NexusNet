from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


NLAH_URL = "https://arxiv.org/abs/2603.25723"
META_HARNESS_URL = "https://arxiv.org/abs/2603.28052"
AGENTSPEC_URL = "https://arxiv.org/abs/2503.18666"
SAFEHARNESS_URL = "https://arxiv.org/abs/2604.13630"


def test_harness_spec_registration_records_nlah_contracts_and_durable_state(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/harness-engineering/specs/register",
        json={
            "source": {"source_name": "Natural-Language Agent Harnesses", "source_url": NLAH_URL},
            "harness_name": "nexus-issue-to-validation-nlah",
            "target_subsystem": "workflows",
            "layers": {
                "backend_infrastructure": ["workspace", "tool adapters", "sandbox"],
                "runtime_charter": ["contract binding", "state persistence", "child agent management"],
                "natural_language_harness": ["roles", "stage structure", "failure taxonomy"],
            },
            "execution_contracts": [
                {
                    "contract_id": "plan-step",
                    "required_outputs": ["plan.md", "risk_register.json"],
                    "budgets": {"max_tool_calls": 40, "max_prompt_tokens": 250000},
                    "permissions": ["filesystem.readonly"],
                    "completion_conditions": ["plan reviewed", "risks classified"],
                    "output_paths": ["artifacts/harness/plan.md"],
                }
            ],
            "durable_state_paths": ["artifacts/harness/state.json", "artifacts/harness/progress.md"],
            "delegation_topology": "orchestrator_workers",
            "module_inventory": ["planner", "generator", "evaluator", "self_evolution"],
        },
    )

    assert response.status_code == 200
    record = response.json()["record"]
    assert record["record_id"].startswith("harness_")
    assert record["status"] == "registered_metadata_only"
    assert record["source"]["source_url"] == NLAH_URL
    assert record["layers"]["runtime_charter"]
    assert record["execution_contracts"][0]["contract_elements"] == [
        "required_outputs",
        "budgets",
        "permissions",
        "completion_conditions",
        "output_paths",
    ]
    assert record["durable_state"]["file_backed"] is True
    assert record["durable_state"]["paths"] == ["artifacts/harness/state.json", "artifacts/harness/progress.md"]
    assert record["delegation_topology"] == "orchestrator_workers"
    assert record["execution_authority"]["required"] is True
    assert "harness_spec_registration" in record["execution_authority"]["required_capabilities"]
    assert record["execution_allowed"] is False
    assert record["mutation_allowed"] is False
    assert Path(record["artifact_path"]).exists()


def test_harness_ablation_records_efficiency_and_pruning_signal(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/harness-engineering/ablations/record",
        json={
            "harness_id": "nexus-issue-to-validation-nlah",
            "benchmark": "internal-issue-validation",
            "baseline": {
                "label": "full_harness",
                "pass_rate": 0.76,
                "prompt_tokens": 16300000,
                "tool_calls": 642,
                "runtime_minutes": 32,
                "modules": ["planner", "generator", "evaluator", "multi_candidate_search", "verifier"],
            },
            "variant": {
                "label": "narrow_self_evolution",
                "pass_rate": 0.75,
                "prompt_tokens": 1220000,
                "tool_calls": 51,
                "runtime_minutes": 7,
                "modules": ["planner", "generator", "self_evolution"],
            },
            "module_findings": [
                {"module": "self_evolution", "delta_pass_rate": 0.048, "cost_delta": -0.2},
                {"module": "verifier", "delta_pass_rate": -0.084, "cost_delta": 0.3},
                {"module": "multi_candidate_search", "delta_pass_rate": -0.056, "cost_delta": 0.4},
            ],
        },
    )

    assert response.status_code == 200
    record = response.json()["record"]
    assert record["status"] == "ablation_recorded"
    assert record["efficiency"]["prompt_token_reduction_ratio"] > 10
    assert record["efficiency"]["tool_call_reduction_ratio"] > 10
    assert record["efficiency"]["runtime_reduction_ratio"] > 4
    assert record["recommendation"]["preferred_module"] == "self_evolution"
    assert set(record["recommendation"]["prune_candidates"]) == {"verifier", "multi_candidate_search"}
    assert record["recommendation"]["principle"] == "discipline_narrowing_before_expensive_broadening"
    assert record["execution_allowed"] is False


def test_harness_optimization_proposal_requires_raw_traces_and_transfer_eval(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/harness-engineering/optimization/propose",
        json={
            "source": {"source_name": "Meta-Harness", "source_url": META_HARNESS_URL},
            "target_harness_id": "nexus-issue-to-validation-nlah",
            "failure_trace_ids": ["trace-raw-001", "trace-raw-002", "trace-raw-003"],
            "summary_trace_ids": ["summary-001"],
            "proposed_change_summary": "Add sandbox environment bootstrap and narrow self-evolution attempt loop before broad search.",
            "candidate_changes": [
                "snapshot working directory and available tools before first model call",
                "preserve raw failed traces as optimizer context",
                "run acceptance-gated attempts before adding verifier modules",
            ],
            "transfer_eval_models": ["gpt-5.4", "claude-opus-4.6", "haiku-4.6", "qwen3.6"],
        },
    )

    assert response.status_code == 200
    record = response.json()["record"]
    assert record["status"] == "optimization_proposed_metadata_only"
    assert record["raw_trace_policy"]["raw_traces_required"] is True
    assert record["raw_trace_policy"]["summaries_alone_sufficient"] is False
    assert record["self_evolution_loop"]["attempt_scope"] == "narrow_until_failure_signal"
    assert record["acceptance_gate"]["required"] is True
    assert record["transfer_eval"]["required"] is True
    assert set(record["transfer_eval"]["models"]) == {"gpt-5.4", "claude-opus-4.6", "haiku-4.6", "qwen3.6"}
    assert "harness_optimization" in record["execution_authority"]["required_capabilities"]
    assert record["execution_allowed"] is False
    assert record["mutation_allowed"] is False


def test_harness_safety_rule_records_runtime_enforcement_without_execution(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/harness-engineering/safety-rules/record",
        json={
            "source": {"source_name": "AgentSpec + SafeHarness", "source_url": AGENTSPEC_URL, "secondary_url": SAFEHARNESS_URL},
            "rule_id": "deny-unguarded-network-write",
            "phase": "action_execution",
            "trigger": "tool.requested",
            "predicate": "tool.network_write == true and lease.execution_allowed != true",
            "enforcement": "deny_and_request_execution_authority_lease",
            "defense_layers": [
                "adversarial_context_filtering",
                "tiered_causal_verification",
                "privilege_separated_tool_control",
                "safe_rollback_adaptive_degradation",
            ],
        },
    )

    assert response.status_code == 200
    record = response.json()["record"]
    assert record["status"] == "safety_rule_recorded_metadata_only"
    assert record["rule"]["trigger"] == "tool.requested"
    assert record["rule"]["enforcement"] == "deny_and_request_execution_authority_lease"
    assert record["phase"] == "action_execution"
    assert "privilege_separated_tool_control" in record["defense_layers"]
    assert "harness_safety_rule" in record["execution_authority"]["required_capabilities"]
    assert record["execution_allowed"] is False
    assert record["mutation_allowed"] is False


def test_harness_engineering_status_surfaces_and_telemetry(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    client.post(
        "/ops/brain/harness-engineering/specs/register",
        json={
            "harness_name": "status-surface-harness",
            "execution_contracts": [
                {
                    "contract_id": "status",
                    "required_outputs": ["status.json"],
                    "budgets": {"max_tool_calls": 10},
                    "permissions": ["filesystem.readonly"],
                    "completion_conditions": ["status visible"],
                    "output_paths": ["artifacts/status.json"],
                }
            ],
        },
    )

    summary = client.get("/ops/brain/harness-engineering")
    assert summary.status_code == 200
    assert summary.json()["record_count"] == 1
    assert summary.json()["execution_allowed"] is False
    assert "natural_language_agent_harness" in summary.json()["assimilated_patterns"]

    product = client.get("/ops/brain/product-sweep/status")
    assert product.status_code == 200
    assert "harness_engineering" in product.json()["status_surfaces"]

    assimilation = client.get("/ops/brain/assimilation/status")
    assert assimilation.status_code == 200
    assert "harness_engineering" in assimilation.json()

    telemetry = client.get("/ops/brain/telemetry/normalized")
    assert telemetry.status_code == 200
    assert telemetry.json()["span_kind_counts"]["harness_engineering"] >= 1

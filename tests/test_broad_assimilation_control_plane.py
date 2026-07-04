from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexus.services import build_services
from tests.test_nexus_phase1_foundation import make_project


def test_assimilation_candidates_classify_all_categories_and_reject_unknown(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    summary = client.get("/ops/brain/assimilation/status")
    assert summary.status_code == 200
    payload = summary.json()
    expected_categories = {
        "durable_execution",
        "telemetry",
        "eval_gate",
        "retrieval",
        "memory",
        "runtime",
        "provider_router",
        "security",
        "protocol",
        "code_agent",
        "training",
        "operator_ux",
    }
    assert expected_categories <= set(payload["assimilation_candidates"]["category_counts"])
    assert payload["assimilation_candidates"]["external_execution_allowed"] is False
    assert payload["assimilation_candidates"]["remote_agent_spawning_allowed"] is False
    assert payload["assimilation_candidates"]["candidate_count"] >= 12

    candidate = client.post(
        "/ops/brain/assimilation/candidates/ingest",
        json={
            "category": "runtime",
            "source_name": "Unit Test Runtime",
            "source_url": "https://example.invalid/runtime",
            "license_posture": "requires_review",
            "target_subsystem": "runtime",
        },
    )
    assert candidate.status_code == 200
    candidate_json = candidate.json()
    record = candidate_json["candidate"]
    assert record["candidate_id"].startswith("asim_runtime_unit-test-runtime")
    assert record["governance_status"] == "gated"
    assert record["product_sweep_gate_ids"]
    assert record["policy_path"][0]["decision"] == "hold"
    assert record["approval_path"]["decision"] == "not_requested"
    assert record["implementation_readiness"]["external_dependency_required"] is False
    assert record["scorecard"]["metadata_only_v1"] is True
    assert record["artifacts"]

    bad = client.post(
        "/ops/brain/assimilation/candidates/ingest",
        json={
            "category": "unbounded_autonomy",
            "source_name": "Unsafe",
            "source_url": "https://example.invalid/unsafe",
        },
    )
    assert bad.status_code == 400
    assert "unsupported assimilation category" in bad.json()["detail"]


def test_durable_run_ledger_metadata_is_recorded_without_mutation(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    workflow_ids = {item["workflow_id"] for item in client.get("/ops/brain/workflows").json()["items"]}
    assert {"nexus-durable-agent-run", "nexus-eval-gated-assimilation", "nexus-runtime-scorecard-review"} <= workflow_ids

    executed = client.post(
        "/ops/brain/workflows/execute",
        json={
            "workflow_id": "nexus-durable-agent-run",
            "requested_tools": ["filesystem.write"],
            "linked_trace_ids": ["trace-durable-001"],
        },
    )
    assert executed.status_code == 200
    workflow = executed.json()
    ledger = workflow["durable_ledger"]
    assert ledger["metadata_only"] is True
    assert ledger["mutation_allowed"] is False
    assert ledger["checkpoint_count"] == len(workflow["node_states"])
    assert ledger["resume"]["state"] == "available_after_policy_grant"
    assert ledger["interrupts"][0]["reason"] == "human_state_edit_requires_policy"
    assert ledger["replay"]["deterministic_replay_supported"] is True

    prepared = client.post(
        "/ops/brain/parallel-runs/prepare",
        json={"source_type": "manual", "source_ref": "durable ledger check"},
    )
    assert prepared.status_code == 200
    parallel = prepared.json()
    assert parallel["durable_ledger"]["metadata_only"] is True
    assert parallel["durable_ledger"]["mutation_allowed"] is False
    assert parallel["durable_ledger"]["resume"]["state"] == "planned_only"
    assert parallel["durable_ledger"]["replay"]["source_ref"] == "durable ledger check"


def test_normalized_telemetry_spans_cover_core_event_families(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    client.post(
        "/ops/brain/workflows/execute",
        json={"workflow_id": "nexus-eval-gated-assimilation", "requested_tools": ["network.external"]},
    )
    client.post(
        "/ops/brain/parallel-runs/prepare",
        json={"source_type": "github_issue", "source_ref": "nexusnet/test#1"},
    )

    response = client.get("/ops/brain/telemetry/normalized")
    assert response.status_code == 200
    payload = response.json()
    assert payload["span_count"] >= 1
    assert payload["trace_health"]["status"] in {"ok", "no_spans"}
    required = {
        "trace_id",
        "span_id",
        "parent_span_id",
        "span_kind",
        "subject",
        "started_at",
        "ended_at",
        "status",
        "model_or_tool",
        "workflow_execution_id",
        "policy_decision",
        "approval_decision",
        "redaction_state",
        "token_usage",
        "cost_estimate",
        "linked_artifact_ids",
    }
    assert required <= set(payload["spans"][0])
    assert {"workflow", "parallel_run"} <= set(payload["span_kind_counts"])


def test_eval_suites_and_runtime_scorecards_are_gated_metadata_records(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    suites = client.get("/ops/brain/evals/suites")
    assert suites.status_code == 200
    suite_payload = suites.json()
    assert {
        "rag_quality",
        "tool_call_accuracy",
        "workflow_completion",
        "code_agent_issue_to_patch",
        "prompt_security_red_team",
        "runtime_quality",
        "regression_behavior",
    } <= {item["suite_type"] for item in suite_payload["suites"]}
    assert suite_payload["promotion_requires_eval_pass"] is True

    run = client.post(
        "/ops/brain/evals/run",
        json={"suite_type": "prompt_security_red_team", "subject": "mcp-package-candidate"},
    )
    assert run.status_code == 200
    run_json = run.json()
    assert run_json["result"]["status"] == "blocked"
    assert run_json["result"]["mutation_allowed"] is False
    assert Path(run_json["result"]["artifact_path"]).exists()

    scorecards = client.get("/ops/brain/runtime/scorecards")
    assert scorecards.status_code == 200
    scorecard_payload = scorecards.json()
    assert {"vllm", "sglang", "tgi", "tensorrt-llm", "litellm", "ollama", "lm-studio"} <= {
        item["provider_id"] for item in scorecard_payload["items"]
    }

    evaluated = client.post(
        "/ops/brain/runtime/scorecards/evaluate",
        json={"provider_id": "ollama", "endpoint_url": "http://127.0.0.1:11434/v1"},
    )
    assert evaluated.status_code == 200
    evaluated_json = evaluated.json()
    assert evaluated_json["scorecard"]["provider_id"] == "ollama"
    assert evaluated_json["scorecard"]["openai_compatible_probe"]["state"] == "metadata_only"
    assert evaluated_json["scorecard"]["external_server_started"] is False
    assert evaluated_json["scorecard"]["execution_allowed"] is False


def test_protocol_capability_registry_and_memory_governance_are_deny_by_default(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    capabilities = client.get("/ops/brain/protocol/capabilities")
    assert capabilities.status_code == 200
    cap_payload = capabilities.json()
    assert {"mcp", "a2a", "ag-ui", "openapi-action", "local-provider"} <= {
        item["protocol_id"] for item in cap_payload["capabilities"]
    }
    assert cap_payload["provider_registration_allowed"] is False
    assert cap_payload["external_protocol_execution_allowed"] is False
    assert all(item["mutation_allowed"] is False for item in cap_payload["capabilities"])

    memory = client.post(
        "/ops/brain/memory-os/proposals",
        json={
            "fact_id": "assimilation-memory-1",
            "content": "Store memory only after provenance review.",
            "source": "broad-assimilation-test",
            "operation": "store",
        },
    )
    assert memory.status_code == 200
    memory_json = memory.json()
    assert memory_json["proposal"]["status"] == "approval_required"
    assert memory_json["proposal"]["mutation_allowed"] is False
    assert memory_json["summary"]["proposal_count"] == 1
    assert memory_json["summary"]["compaction"]["status"] == "available"
    assert memory_json["summary"]["archival_memory"]["status"] == "governed"
    assert memory_json["summary"]["shared_memory"]["mutation_allowed"] is False


def test_product_sweep_status_includes_broad_assimilation_surfaces(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.get("/ops/brain/product-sweep/status")
    assert response.status_code == 200
    surfaces = response.json()["status_surfaces"]
    assert {
        "assimilation_candidates",
        "normalized_telemetry",
        "eval_suites",
        "runtime_scorecards",
        "protocol_capabilities",
        "memory_governance",
        "security_red_team",
    } <= set(surfaces)
    assert surfaces["assimilation_candidates"]["external_execution_allowed"] is False
    assert surfaces["runtime_scorecards"]["external_server_started"] is False
    assert surfaces["protocol_capabilities"]["external_protocol_execution_allowed"] is False
    assert surfaces["memory_governance"]["shared_memory"]["mutation_allowed"] is False

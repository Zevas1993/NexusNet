from __future__ import annotations

"""Regression coverage for adaptive capability control-plane APIs."""

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


REQUIRED_RECORD_FIELDS = {
    "record_id",
    "status",
    "tier",
    "capability_family",
    "source",
    "target_subsystem",
    "hardware_profile",
    "runtime_candidates",
    "provider_candidates",
    "model_artifact_formats",
    "quantization_posture",
    "offline_posture",
    "privacy_posture",
    "cost_posture",
    "policy_path",
    "approval_path",
    "product_sweep_gate_ids",
    "eval_suite_ids",
    "telemetry_trace_ids",
    "provenance",
    "artifacts",
    "execution_allowed",
    "mutation_allowed",
}


def _client(tmp_path: Path) -> TestClient:
    return TestClient(create_app(str(make_project(tmp_path))))


def test_adaptive_capability_profiles_hardware_tiers_and_routes_without_mutation(tmp_path: Path):
    client = _client(tmp_path)

    summary = client.get("/ops/brain/adaptive-capabilities")
    assert summary.status_code == 200
    summary_json = summary.json()
    assert {
        "tier_0_tiny_edge",
        "tier_1_constrained_edge",
        "tier_2_mainstream_local",
        "tier_3_premium_local",
        "tier_4_local_server",
        "tier_5_governed_cloud",
    } <= set(summary_json["hardware_tiers"])
    assert summary_json["execution_allowed"] is False
    assert summary_json["mutation_allowed"] is False

    low = client.post(
        "/ops/brain/adaptive-capabilities/profile",
        json={
            "capability_family": "inference",
            "source": {"source_type": "unit-test", "source_ref": "low-memory-profile"},
            "hardware_profile": {"cpu_count": 2, "ram_gb": 4, "vram_gb": None, "gpu_summary": "none"},
        },
    )
    assert low.status_code == 200
    low_record = low.json()["record"]
    assert REQUIRED_RECORD_FIELDS <= set(low_record)
    assert low_record["tier"] == "tier_1_constrained_edge"
    assert low_record["execution_allowed"] is False
    assert low_record["mutation_allowed"] is False
    assert "short_context" in low_record["runtime_candidates"][0]["constraints"]

    premium = client.post(
        "/ops/brain/adaptive-capabilities/profile",
        json={
            "capability_family": "parallel_agent",
            "source": {"source_type": "unit-test", "source_ref": "premium-profile"},
            "hardware_profile": {"cpu_count": 16, "ram_gb": 64, "vram_gb": 24, "gpu_summary": "premium-gpu"},
        },
    )
    assert premium.status_code == 200
    assert premium.json()["record"]["tier"] == "tier_3_premium_local"

    route = client.post(
        "/ops/brain/adaptive-capabilities/route",
        json={
            "capability_family": "provider_fallback",
            "source": {"source_type": "unit-test", "source_ref": "fallback-needed"},
            "hardware_profile": {"cpu_count": 4, "ram_gb": 8, "vram_gb": 0, "gpu_summary": "none"},
            "allow_cloud_fallback": True,
            "local_satisfies_policy": False,
            "fallback_reason": "local runtime lacks requested context window",
            "privacy_posture": "redacted_operator_visible",
            "cost_posture": {"budget": "operator-approved-test-budget"},
        },
    )
    assert route.status_code == 200
    route_record = route.json()["record"]
    assert route_record["tier"] == "tier_5_governed_cloud"
    assert route_record["status"] == "approval_required"
    assert route_record["policy_path"][0]["decision"] == "hold"


def test_runtime_scorecards_include_hardware_continuum_candidates(tmp_path: Path):
    client = _client(tmp_path)

    response = client.get("/ops/brain/runtime/scorecards")
    assert response.status_code == 200
    payload = response.json()
    expected = {
        "onnxruntime-ep",
        "executorch",
        "litert",
        "mlc-llm",
        "webllm",
        "llama-cpp",
        "openvino-genai",
        "qnn",
        "coreml",
        "directml",
        "vllm",
        "sglang",
        "tgi",
        "tensorrt-llm",
        "ollama",
        "lm-studio",
        "litellm",
        "tier5-cloud-router",
    }
    items = {item["provider_id"]: item for item in payload["items"]}
    assert expected <= set(items)
    assert all("hardware_tier_fit" in item for item in items.values())
    assert all("cloud_local_mode" in item for item in items.values())
    assert items["tier5-cloud-router"]["cloud_local_mode"] == "governed_cloud"
    assert payload["external_server_started"] is False

    evaluated = client.post(
        "/ops/brain/runtime/scorecards/evaluate",
        json={"provider_id": "tier5-cloud-router", "endpoint_url": "https://api.example.invalid/v1"},
    )
    assert evaluated.status_code == 200
    scorecard = evaluated.json()["scorecard"]
    assert scorecard["provider_id"] == "tier5-cloud-router"
    assert scorecard["hardware_tier_fit"] == ["tier_5_governed_cloud"]
    assert scorecard["execution_allowed"] is False


def test_research_scout_ingests_metadata_candidates_and_rejects_unknown_sources(tmp_path: Path):
    client = _client(tmp_path)

    summary = client.get("/ops/brain/research-scout/candidates")
    assert summary.status_code == 200
    assert {"github", "hugging_face", "arxiv", "npm", "vendor_doc", "benchmark", "security_advisory"} <= set(
        summary.json()["supported_source_types"]
    )

    ingested = client.post(
        "/ops/brain/research-scout/ingest",
        json={
            "source_type": "github",
            "source_name": "ONNX Runtime EP",
            "source_url": "https://onnxruntime.ai/docs/execution-providers/",
            "claimed_capability": "portable hardware execution providers",
            "capability_family": "inference",
            "hardware_tier_fit": ["tier_1_constrained_edge", "tier_3_premium_local"],
            "license_posture": "requires_review",
            "risk_flags": ["native_runtime"],
            "dependency_posture": "candidate_only",
            "confidence": 0.82,
            "required_eval_suite": "runtime_quality",
        },
    )
    assert ingested.status_code == 200
    candidate = ingested.json()["candidate"]
    assert REQUIRED_RECORD_FIELDS <= set(candidate)
    assert candidate["source"]["source_type"] == "github"
    assert candidate["license_posture"] == "requires_review"
    assert candidate["dependency_posture"] == "candidate_only"
    assert candidate["execution_allowed"] is False
    assert candidate["mutation_allowed"] is False

    bad = client.post(
        "/ops/brain/research-scout/ingest",
        json={
            "source_type": "untrusted-binary-drop",
            "source_name": "Unsafe",
            "source_url": "https://example.invalid/unsafe",
        },
    )
    assert bad.status_code == 400
    assert "unsupported research source_type" in bad.json()["detail"]

    run = client.post("/ops/brain/research-scout/run", json={"query": "edge runtime updates", "source_types": ["github", "arxiv"]})
    assert run.status_code == 200
    run_json = run.json()
    assert run_json["status"] == "completed_metadata_only"
    assert run_json["execution_allowed"] is False
    assert run_json["candidate_count"] == 0


def test_research_scout_run_fetches_public_api_metadata_as_candidates_without_execution(tmp_path: Path):
    client = _client(tmp_path)
    fetched_urls: list[str] = []

    def fake_fetcher(url: str, headers: dict[str, str], timeout: float) -> tuple[int, str]:
        fetched_urls.append(url)
        if "api.github.com/search/repositories" in url:
            return (
                200,
                """
                {
                  "items": [
                    {
                      "full_name": "example/edge-runtime",
                      "html_url": "https://github.com/example/edge-runtime",
                      "description": "Portable edge runtime for local inference",
                      "license": {"spdx_id": "Apache-2.0"},
                      "topics": ["edge", "inference"],
                      "stargazers_count": 1200,
                      "language": "Python"
                    }
                  ]
                }
                """,
            )
        if "huggingface.co/api/models" in url:
            return (
                200,
                """
                [
                  {
                    "modelId": "example/tiny-local-model",
                    "pipeline_tag": "text-generation",
                    "tags": ["gguf", "license:mit"],
                    "downloads": 25000
                  }
                ]
                """,
            )
        if "registry.npmjs.org/-/v1/search" in url:
            return (
                200,
                """
                {
                  "objects": [
                    {
                      "package": {
                        "name": "@example/agent-plugin",
                        "version": "1.2.3",
                        "description": "Agent plugin metadata package",
                        "keywords": ["agent", "local"],
                        "license": "MIT",
                        "links": {"npm": "https://www.npmjs.com/package/@example/agent-plugin"}
                      },
                      "score": {"final": 0.92}
                    }
                  ]
                }
                """,
            )
        if "export.arxiv.org/api/query" in url:
            return (
                200,
                """
                <feed xmlns="http://www.w3.org/2005/Atom"
                      xmlns:arxiv="http://arxiv.org/schemas/atom">
                  <entry>
                    <id>http://arxiv.org/abs/2601.00001v1</id>
                    <title>Efficient Local Agent Routing</title>
                    <summary>Methods for routing agent workloads across edge and cloud tiers.</summary>
                    <published>2026-01-01T00:00:00Z</published>
                    <updated>2026-01-02T00:00:00Z</updated>
                    <author><name>Researcher One</name></author>
                    <category term="cs.AI"/>
                  </entry>
                </feed>
                """,
            )
        raise AssertionError(f"unexpected URL: {url}")

    client.app.state.services.brain_research_scout.metadata_fetcher = fake_fetcher
    response = client.post(
        "/ops/brain/research-scout/run",
        json={
            "query": "edge local inference agent routing",
            "source_types": ["github", "hugging_face", "npm", "arxiv"],
            "live_fetch": True,
            "max_candidates_per_source": 1,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "completed_metadata_only"
    assert payload["execution_allowed"] is False
    assert payload["mutation_allowed"] is False
    assert payload["network_execution_allowed"] is True
    assert payload["candidate_count"] == 4
    assert payload["candidate_ingestion_count"] == 4
    assert {item["source_type"] for item in payload["source_checks"]} == {"github", "hugging_face", "npm", "arxiv"}
    assert len(fetched_urls) == 4

    candidates = client.get("/ops/brain/research-scout/candidates").json()["items"]
    names = {candidate["source"]["source_name"] for candidate in candidates}
    assert {
        "example/edge-runtime",
        "example/tiny-local-model",
        "@example/agent-plugin",
        "Efficient Local Agent Routing",
    } <= names
    assert all(candidate["execution_allowed"] is False for candidate in candidates)
    assert all(candidate["mutation_allowed"] is False for candidate in candidates)

    events = client.get("/ops/brain/events", params={"subject_prefix": "research-scout:", "limit": 50})
    assert events.status_code == 200
    assert events.json()["event_type_counts"]["research_scout.candidate_ingested"] >= 4


def test_self_improvement_proposals_are_eval_gated_and_non_mutating(tmp_path: Path):
    client = _client(tmp_path)

    proposal = client.post(
        "/ops/brain/self-improvement/propose",
        json={
            "category": "prompt_optimization",
            "target_subsystem": "workflow",
            "proposed_change_summary": "Tighten planning prompt after weak-plan review failures.",
            "evidence_links": ["parallel-run:abc", "eval-suite:workflow_completion"],
            "eval_suite_id": "workflow_completion",
            "rollback_requirement": "restore_previous_prompt_version",
        },
    )
    assert proposal.status_code == 200
    record = proposal.json()["proposal"]
    assert REQUIRED_RECORD_FIELDS <= set(record)
    assert record["category"] == "prompt_optimization"
    assert record["status"] == "proposed"
    assert record["mutation_allowed"] is False
    assert record["approval_path"]["decision"] == "not_requested"

    validated = client.post(
        "/ops/brain/self-improvement/validate",
        json={"proposal_id": record["record_id"], "eval_status": "blocked", "linked_trace_ids": ["trace-self-improve-001"]},
    )
    assert validated.status_code == 200
    validation = validated.json()["validation"]
    assert validation["proposal_id"] == record["record_id"]
    assert validation["promotion_decision"] == "not_promotable_without_passed_eval"
    assert validation["mutation_allowed"] is False

    bad = client.post(
        "/ops/brain/self-improvement/propose",
        json={"category": "self_rewrite_core", "target_subsystem": "core", "proposed_change_summary": "unsafe"},
    )
    assert bad.status_code == 400
    assert "unsupported self-improvement category" in bad.json()["detail"]


def test_self_improvement_mining_turns_failure_events_into_gated_proposals(tmp_path: Path):
    client = _client(tmp_path)
    services = client.app.state.services
    services.brain_lifecycle_events.record(
        event_type="eval_suite.run_recorded",
        subject="eval-suite:workflow_completion:parallel-run:42",
        payload={"status": "blocked", "result_id": "eval-blocked-42", "execution_allowed": False},
        trace_ids=["trace-eval-blocked"],
    )
    services.brain_lifecycle_events.record(
        event_type="parallel_run.self_healing_signal_recorded",
        subject="parallel-run:run-42",
        payload={
            "category": "missing_validation",
            "target": "test",
            "run_id": "run-42",
            "execution_allowed": False,
        },
        trace_ids=["trace-parallel-missing-validation"],
    )
    services.brain_lifecycle_events.record(
        event_type="tool.execution_denied",
        subject="tool:filesystem.write",
        payload={"decision": "deny", "tool": "filesystem.write", "reason": "protected-path"},
        trace_ids=["trace-denied-tool"],
    )
    services.brain_lifecycle_events.record(
        event_type="tier5.fallback_approval_required",
        subject="tier5:request-123",
        payload={"provider_id": "cloud-model", "status": "approval_required", "decision": "hold"},
        trace_ids=["trace-tier5"],
    )

    mined = client.post(
        "/ops/brain/self-improvement/mine",
        json={"source_limit": 50, "max_proposals": 10, "include_product_sweep": False},
    )
    assert mined.status_code == 200
    payload = mined.json()
    assert payload["status"] == "mined_metadata_only"
    assert payload["execution_allowed"] is False
    assert payload["mutation_allowed"] is False
    assert payload["signal_count"] >= 4
    assert payload["created_proposal_count"] >= 4
    categories = {proposal["category"] for proposal in payload["proposals"]}
    assert {"eval_gap", "test_gap", "security_gate", "provider_fallback"} <= categories
    assert all(REQUIRED_RECORD_FIELDS <= set(proposal) for proposal in payload["proposals"])
    assert all(proposal["mutation_allowed"] is False for proposal in payload["proposals"])
    assert all(proposal["source"]["source_type"] == "self_improvement_mining" for proposal in payload["proposals"])
    assert all(proposal["approval_path"]["decision"] == "not_requested" for proposal in payload["proposals"])
    assert all("rollback_requirement" in proposal for proposal in payload["proposals"])

    second = client.post(
        "/ops/brain/self-improvement/mine",
        json={"source_limit": 50, "max_proposals": 10, "include_product_sweep": False},
    )
    assert second.status_code == 200
    assert second.json()["created_proposal_count"] == 0
    assert second.json()["deduped_signal_count"] >= payload["created_proposal_count"]


def test_self_improvement_mining_includes_product_sweep_blockers(tmp_path: Path):
    client = _client(tmp_path)

    mined = client.post(
        "/ops/brain/self-improvement/mine",
        json={"source_limit": 10, "max_proposals": 20, "include_product_sweep": True},
    )
    assert mined.status_code == 200
    payload = mined.json()
    assert payload["status"] == "mined_metadata_only"
    assert payload["product_sweep_signal_count"] >= 1
    product_sweep_signals = [signal for signal in payload["signals"] if signal["event_type"] == "product_sweep.blocker"]
    assert product_sweep_signals
    assert any(signal["payload"]["blocker"] == "runtime_health_required" for signal in product_sweep_signals)
    assert any(signal["payload"]["blocker"] == "security_gate_pass_required" for signal in product_sweep_signals)
    categories = {proposal["category"] for proposal in payload["proposals"]}
    assert {"runtime_routing", "security_gate", "eval_gap"} <= categories
    assert all(proposal["source"]["source_type"] == "self_improvement_mining" for proposal in payload["proposals"])
    assert all(proposal["execution_allowed"] is False for proposal in payload["proposals"])
    assert all(proposal["mutation_allowed"] is False for proposal in payload["proposals"])


def test_tier5_cloud_fallback_requires_governed_posture_and_records_events(tmp_path: Path):
    client = _client(tmp_path)

    missing_posture = client.post(
        "/ops/brain/tier5/fallback/evaluate",
        json={"provider_id": "openai", "fallback_reason": "local model unavailable"},
    )
    assert missing_posture.status_code == 400
    assert "privacy_posture is required" in missing_posture.json()["detail"]

    response = client.post(
        "/ops/brain/tier5/fallback/evaluate",
        json={
            "provider_id": "openai-compatible-cloud",
            "fallback_reason": "local context window cannot satisfy requested validation",
            "privacy_posture": "redacted_operator_visible",
            "cost_posture": {"budget": "daily-test-budget", "max_usd": 1.25},
            "approval_decision": "not_requested",
            "gateway_decision": "hold",
        },
    )
    assert response.status_code == 200
    record = response.json()["record"]
    assert REQUIRED_RECORD_FIELDS <= set(record)
    assert record["tier"] == "tier_5_governed_cloud"
    assert record["status"] == "approval_required"
    assert record["telemetry_trace_ids"]
    assert record["execution_allowed"] is False

    events = client.get("/ops/brain/events", params={"subject_prefix": "tier5:", "limit": 20})
    assert events.status_code == 200
    event_counts = events.json()["event_type_counts"]
    assert event_counts["tier5.fallback_requested"] >= 1
    assert event_counts["tier5.fallback_approval_required"] >= 1


def test_status_payloads_include_adaptive_research_self_improvement_and_tier5(tmp_path: Path):
    client = _client(tmp_path)
    client.post(
        "/ops/brain/adaptive-capabilities/profile",
        json={
            "capability_family": "eval",
            "source": {"source_type": "unit-test", "source_ref": "status-surface"},
            "hardware_profile": {"cpu_count": 8, "ram_gb": 32, "vram_gb": 12, "gpu_summary": "mid-gpu"},
        },
    )
    client.post(
        "/ops/brain/self-improvement/propose",
        json={
            "category": "eval_gap",
            "target_subsystem": "evals",
            "proposed_change_summary": "Add regression coverage for adaptive routing.",
            "eval_suite_id": "regression_behavior",
        },
    )

    assimilation = client.get("/ops/brain/assimilation/status")
    assert assimilation.status_code == 200
    assimilation_json = assimilation.json()
    assert {"adaptive_capabilities", "research_scout", "self_improvement", "tier5_cloud_fallback"} <= set(assimilation_json)
    assert assimilation_json["adaptive_capabilities"]["mutation_allowed"] is False

    product = client.get("/ops/brain/product-sweep/status")
    assert product.status_code == 200
    surfaces = product.json()["status_surfaces"]
    assert {"adaptive_capabilities", "research_scout", "self_improvement", "tier5_cloud_fallback"} <= set(surfaces)
    assert surfaces["tier5_cloud_fallback"]["cloud_fallback_allowed_as_governed_tier"] is True

    telemetry = client.get("/ops/brain/telemetry/normalized")
    assert telemetry.status_code == 200
    kinds = telemetry.json()["span_kind_counts"]
    assert "adaptive" in kinds
    assert "self_improvement" in kinds

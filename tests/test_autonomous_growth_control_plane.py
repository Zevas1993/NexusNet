from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


EXPECTED_TARGETS = {
    "sandbox_manifest_execution",
    "deterministic_tool_boundary_security",
    "otel_openinference_trace_export",
    "raw_trace_optimizer_shadow",
    "paired_eval_skill_harness_utility",
    "edge_runtime_pack_certification",
    "serving_gateway_performance",
    "protocol_trust_registry",
    "stateful_memory_hierarchy",
    "citation_grounded_research_scout",
}


def test_growth_control_plane_activates_all_three_waves_without_execution(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/growth-control/activate",
        json={
            "wave_ids": [
                "wave_1_execution_security",
                "wave_2_measurement",
                "wave_3_capability_expansion",
            ],
            "operator_goal": "make NexusNet grow its own models and outperform other agents",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "activated_metadata_only"
    assert payload["target_count"] == 10
    assert payload["execution_allowed"] is False
    assert payload["mutation_allowed"] is False
    assert set(payload["target_ids"]) == EXPECTED_TARGETS
    assert payload["wave_counts"] == {
        "wave_1_execution_security": 3,
        "wave_2_measurement": 3,
        "wave_3_capability_expansion": 4,
    }
    assert all(item["execution_allowed"] is False for item in payload["records"])
    assert all(item["mutation_allowed"] is False for item in payload["records"])
    assert all(item["approval_path"]["human_approval_is_not_execution_authority"] for item in payload["records"])

    summary = client.get("/ops/brain/growth-control")
    assert summary.status_code == 200
    summary_json = summary.json()
    assert summary_json["blueprint_target_count"] == 10
    assert summary_json["record_count"] == 10
    assert summary_json["execution_allowed"] is False
    assert summary_json["mutation_allowed"] is False

    product = client.get("/ops/brain/product-sweep/status")
    assert product.status_code == 200
    assert "autonomous_growth" in product.json()["status_surfaces"]
    assert product.json()["status_surfaces"]["autonomous_growth"]["record_count"] == 10

    assimilation = client.get("/ops/brain/assimilation/status")
    assert assimilation.status_code == 200
    assert "autonomous_growth" in assimilation.json()


def test_wave_one_records_sandbox_manifest_security_boundary_and_protocol_trust(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    sandbox = client.post(
        "/ops/brain/growth-control/sandbox-manifests",
        json={
            "workspace_ref": "nexusnet-agent-run",
            "manifest": {
                "root": "workspace",
                "files": ["AGENTS.md", "docs/spec.md"],
                "dirs": ["artifacts", "tmp"],
                "git_repos": [{"url": "https://github.com/example/repo", "path": "repo"}],
                "env": {"NEXUSNET_MODE": "metadata-only", "SECRET_TOKEN": "must-not-leak"},
            },
            "sandbox_providers": ["local", "docker", "daytona", "e2b"],
            "requested_capabilities": ["filesystem.read", "shell.exec"],
        },
    )
    assert sandbox.status_code == 200
    sandbox_record = sandbox.json()["record"]
    assert sandbox_record["target_id"] == "sandbox_manifest_execution"
    assert sandbox_record["manifest"]["portable_workspace_contract"] is True
    assert sandbox_record["manifest"]["absolute_paths_allowed"] is False
    assert sandbox_record["manifest"]["path_escape_allowed"] is False
    assert sandbox_record["manifest"]["redacted_env"]["SECRET_TOKEN"] == "<redacted>"
    assert "sandbox_workspace_execution" in sandbox_record["execution_authority"]["required_capabilities"]
    assert sandbox_record["execution_allowed"] is False
    assert Path(sandbox_record["artifact_path"]).exists()

    security = client.post(
        "/ops/brain/growth-control/security-boundaries/derive",
        json={
            "objective": "review a GitHub issue and run tests only",
            "tool_requests": [
                {"tool": "git.read", "action": "read"},
                {"tool": "shell", "action": "npm install"},
                {"tool": "network", "action": "post"},
            ],
            "content_channels": ["web", "local_file", "mcp", "skill"],
        },
    )
    assert security.status_code == 200
    security_record = security.json()["record"]
    assert security_record["target_id"] == "deterministic_tool_boundary_security"
    assert security_record["boundary_policy"]["deterministic_tool_boundary"] is True
    assert security_record["boundary_policy"]["default_decision"] == "deny"
    assert {"web", "local_file", "mcp", "skill"} <= set(security_record["attack_channels"])
    assert any(decision["decision"] == "deny" for decision in security_record["tool_decisions"])
    assert "deterministic_tool_boundary" in security_record["execution_authority"]["required_capabilities"]

    protocol = client.post(
        "/ops/brain/growth-control/protocol-trust/record",
        json={
            "protocol_id": "mcp",
            "server_ref": "registry.modelcontextprotocol.io/example",
            "auth": {
                "oauth_2_1": True,
                "resource_metadata": True,
                "audience_bound_tokens": True,
                "pkce": True,
                "token_passthrough": False,
            },
            "capability_manifest": {"tools": ["read_issue", "list_files"], "mutating_tools": ["write_file"]},
        },
    )
    assert protocol.status_code == 200
    protocol_record = protocol.json()["record"]
    assert protocol_record["target_id"] == "protocol_trust_registry"
    assert protocol_record["trust_requirements"]["oauth_2_1"] is True
    assert protocol_record["trust_requirements"]["token_passthrough_allowed"] is False
    assert protocol_record["risk_posture"]["provider_registration_allowed"] is False
    assert protocol_record["risk_posture"]["external_protocol_execution_allowed"] is False


def test_wave_two_records_trace_export_optimizer_and_paired_eval(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    telemetry = client.post(
        "/ops/brain/growth-control/telemetry/export-plan",
        json={
            "trace_ids": ["trace-raw-1", "trace-raw-2"],
            "destination": "phoenix-local",
            "formats": ["otel_genai", "openinference"],
            "redaction_policy": {"mode": "metadata_plus_refs", "raw_content_export": False},
        },
    )
    assert telemetry.status_code == 200
    telemetry_record = telemetry.json()["record"]
    assert telemetry_record["target_id"] == "otel_openinference_trace_export"
    assert telemetry_record["export_plan"]["otel_genai_shape"] is True
    assert telemetry_record["export_plan"]["openinference_shape"] is True
    assert telemetry_record["redaction_policy"]["raw_content_export"] is False
    assert telemetry_record["execution_allowed"] is False

    optimizer = client.post(
        "/ops/brain/growth-control/optimizer/shadow-run",
        json={
            "target_subsystem": "workflows",
            "raw_trace_ids": ["trace-failed-1", "trace-failed-2", "trace-failed-3"],
            "summary_trace_ids": ["summary-1"],
            "candidate_change": "narrow retry loop before spawning verifier",
            "transfer_models": ["gpt-5.4", "haiku-4.6", "qwen3.6"],
        },
    )
    assert optimizer.status_code == 200
    optimizer_record = optimizer.json()["record"]
    assert optimizer_record["target_id"] == "raw_trace_optimizer_shadow"
    assert optimizer_record["optimizer_loop"]["raw_traces_required"] is True
    assert optimizer_record["optimizer_loop"]["summaries_alone_sufficient"] is False
    assert optimizer_record["optimizer_loop"]["promotion_requires_product_sweep"] is True
    assert "model_growth_cycle" in optimizer_record["execution_authority"]["required_capabilities"]

    paired_eval = client.post(
        "/ops/brain/growth-control/evals/paired",
        json={
            "subject": "skill:graph-context",
            "baseline": {"pass_rate": 0.61, "tokens": 100000, "latency_ms": 30000},
            "variant": {"pass_rate": 0.68, "tokens": 75000, "latency_ms": 25000},
            "acceptance_criteria": {"min_pass_delta": 0.03, "max_token_delta_ratio": 0.25},
        },
    )
    assert paired_eval.status_code == 200
    eval_record = paired_eval.json()["record"]
    assert eval_record["target_id"] == "paired_eval_skill_harness_utility"
    assert eval_record["paired_eval"]["pass_delta"] == 0.07
    assert eval_record["paired_eval"]["token_delta_ratio"] == -0.25
    assert eval_record["paired_eval"]["decision"] == "promote_to_validation"
    assert eval_record["promotion_allowed"] is False

    spans = client.get("/ops/brain/telemetry/normalized").json()["span_kind_counts"]
    assert spans["autonomous_growth"] >= 3


def test_wave_three_records_runtime_serving_memory_and_research_evidence(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    runtime = client.post(
        "/ops/brain/growth-control/runtime-pack-certifications",
        json={
            "runtime_id": "executorch-qnn",
            "hardware_tier": "tier_1_constrained_edge",
            "model_formats": ["pte", "onnx", "gguf"],
            "accelerators": ["cpu", "gpu", "npu"],
            "measurements": {"cold_start_ms": 1800, "ram_mb": 2800, "tokens_per_second": 12.5},
        },
    )
    assert runtime.status_code == 200
    runtime_record = runtime.json()["record"]
    assert runtime_record["target_id"] == "edge_runtime_pack_certification"
    assert runtime_record["certification"]["runtime_id"] == "executorch-qnn"
    assert runtime_record["certification"]["hardware_tier"] == "tier_1_constrained_edge"
    assert runtime_record["certification"]["status"] == "certification_candidate"
    assert runtime_record["execution_allowed"] is False

    serving = client.post(
        "/ops/brain/growth-control/serving-scorecards",
        json={
            "provider_id": "vllm-local",
            "features": {
                "prefix_cache": True,
                "structured_outputs": True,
                "tool_calling": True,
                "disaggregated_prefill_decode": True,
            },
            "measurements": {"ttft_ms": 210, "throughput_tps": 145, "cache_hit_rate": 0.72},
        },
    )
    assert serving.status_code == 200
    serving_record = serving.json()["record"]
    assert serving_record["target_id"] == "serving_gateway_performance"
    assert serving_record["serving_scorecard"]["prefix_cache_probe"]["state"] == "supported_metadata"
    assert serving_record["serving_scorecard"]["routing_mode"] == "governed_local_or_tier5"
    assert serving_record["serving_scorecard"]["external_server_started"] is False

    memory = client.post(
        "/ops/brain/growth-control/memory-hierarchy/record",
        json={
            "agent_ref": "nexus-growth-agent",
            "core_blocks": [{"label": "mission", "content": "Improve only through governed proposals."}],
            "archival_refs": ["memory://archive/1"],
            "shared_blocks": [{"label": "team-rules", "attached_agents": ["planner", "reviewer"]}],
            "contradictions": [{"fact_id": "runtime-speed", "reason": "stale measurement"}],
        },
    )
    assert memory.status_code == 200
    memory_record = memory.json()["record"]
    assert memory_record["target_id"] == "stateful_memory_hierarchy"
    assert memory_record["memory_hierarchy"]["core_memory"]["block_count"] == 1
    assert memory_record["memory_hierarchy"]["archival_memory"]["ref_count"] == 1
    assert memory_record["memory_hierarchy"]["shared_memory"]["mutation_allowed"] is False
    assert memory_record["memory_hierarchy"]["contradiction_count"] == 1

    research = client.post(
        "/ops/brain/growth-control/research-evidence/ingest",
        json={
            "source_name": "PaperQA2",
            "source_url": "https://github.com/Future-House/paper-qa",
            "claim": "Citation-grounded research agents should preserve source metadata.",
            "citations": [
                {"url": "https://github.com/Future-House/paper-qa", "title": "PaperQA2"},
                {"url": "https://developers.openai.com/api/docs/guides/deep-research", "title": "Deep Research API"},
            ],
            "credibility": {"source_type": "official_or_primary", "score": 0.91},
        },
    )
    assert research.status_code == 200
    research_record = research.json()["record"]
    assert research_record["target_id"] == "citation_grounded_research_scout"
    assert research_record["research_evidence"]["citation_count"] == 2
    assert research_record["research_evidence"]["source_metadata_required"] is True
    assert research_record["research_evidence"]["candidate_ingestion_status"] == "metadata_only"


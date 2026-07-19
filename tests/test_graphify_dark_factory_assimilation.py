from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


GRAPHIFY_REPO = "https://github.com/safishamsi/graphify"
GRAPHIFY_PYPI = "https://pypi.org/project/graphifyy/"
ARCHON_REPO = "https://github.com/coleam00/Archon"


def test_context_graph_index_plan_records_graphify_patterns_without_execution(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/context-graph/index-plan",
        json={
            "source": {
                "source_name": "Graphify",
                "source_url": GRAPHIFY_REPO,
                "package_url": GRAPHIFY_PYPI,
                "license_posture": "declared:MIT_requires_review",
            },
            "corpus_root": str(project_root),
            "content_kinds": ["code", "docs", "pdf", "image", "audio", "video", "youtube"],
            "assistant_platforms": ["codex", "opencode", "claude-code"],
            "graph_ignore_patterns": ["AGENTS.md", ".opencode/", "node_modules/", "dist/"],
            "changed_files": ["nexus/api/app.py", "docs/research/graphify.md"],
            "update_mode": "changed_files_only",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    record = payload["record"]

    assert record["record_id"].startswith("ctxgraph_")
    assert record["status"] == "planned_metadata_only"
    assert record["source"]["source_url"] == GRAPHIFY_REPO
    assert record["source"]["package_name"] == "graphifyy"
    assert record["corpus"]["content_kinds"] == ["code", "docs", "pdf", "image", "audio", "video", "youtube"]
    assert record["corpus"]["update_mode"] == "changed_files_only"
    assert record["execution_allowed"] is False
    assert record["mutation_allowed"] is False
    assert record["policy_path"][0]["decision"] == "hold"
    assert record["approval_path"]["decision"] == "not_requested"
    assert "artifact_path" not in record
    assert (project_root / "runtime" / "artifacts" / record["artifact_storage_ref"]).exists()

    passes = {item["pass_id"]: item for item in record["extraction_passes"]}
    assert passes["tree_sitter_code_graph"]["execution_location"] == "local"
    assert passes["tree_sitter_code_graph"]["network_required"] is False
    assert passes["local_media_transcription"]["execution_location"] == "local"
    assert passes["semantic_concept_extraction"]["policy_decision"] == "approval_required"
    assert passes["semantic_concept_extraction"]["cost_posture"]["metered"] is True

    outputs = {item["artifact_type"] for item in record["graph_outputs"]}
    assert {"graph_report", "graph_json", "graph_html", "cache", "manifest"} <= outputs
    hooks = {item["platform"] for item in record["assistant_hooks"]}
    assert {"codex", "opencode", "claude-code"} <= hooks
    assert all(item["governance_state"] == "planned_review_required" for item in record["assistant_hooks"])
    assert record["staleness_policy"]["incremental_update_supported"] is True
    assert "graph_context_regression" in record["eval_suite_ids"]
    assert "external_package_execution" in record["risk_flags"]

    query = client.post(
        "/ops/brain/context-graph/query",
        json={
            "graph_record_id": record["record_id"],
            "question": "what connects workflow validation to assistant hooks?",
            "mode": "path",
        },
    )
    assert query.status_code == 200
    query_record = query.json()["record"]
    assert query_record["mode"] == "path"
    assert query_record["status"] == "recorded_metadata_only"
    assert query_record["execution_allowed"] is False
    assert query_record["query_interfaces"]["mcp"]["policy_decision"] == "approval_required"


def test_factory_orchestration_triage_reproduction_and_pr_validation_are_hard_gated(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    triage = client.post(
        "/ops/brain/factory-orchestration/triage",
        json={
            "source": {"source_name": "Dark Factory transcript", "source_url": ARCHON_REPO},
            "issues": [
                {"issue_ref": "repo#10", "title": "chat autoscroll broken", "labels": ["bug", "ux"]},
                {"issue_ref": "repo#11", "title": "conversation auto naming delayed", "labels": ["bug"]},
                {"issue_ref": "repo#12", "title": "export button contrast low", "labels": ["ux"]},
                {"issue_ref": "repo#13", "title": "dependency upgrade request", "labels": ["maintenance"]},
            ],
            "cadence": "scheduled_batch_30m",
            "max_parallel": 2,
            "protected_paths": ["infra/**", "database/schema.sql", ".github/workflows/**"],
            "token_budget": {"max_usd_per_batch": 5.0, "model_candidates": ["minimax-m2.7", "glm-5.1", "qwen3.6"]},
            "priority_rules": {"bug": 90, "ux": 40, "maintenance": 20},
        },
    )
    assert triage.status_code == 200
    triage_record = triage.json()["record"]
    assert triage_record["record_id"].startswith("factory_")
    assert triage_record["status"] == "triaged_metadata_only"
    assert triage_record["queue"]["issue_count"] == 4
    assert triage_record["queue"]["max_parallel"] == 2
    assert triage_record["priority_decision"]["ordered_issue_refs"][0] in {"repo#10", "repo#11"}
    assert triage_record["protected_paths"]["mutation_requires_human"] is True
    assert triage_record["execution_allowed"] is False
    assert triage_record["mutation_allowed"] is False
    assert "autonomous_merge" in triage_record["risk_flags"]

    reproduction = client.post(
        "/ops/brain/factory-orchestration/reproduction-check",
        json={
            "issue_ref": "repo#77",
            "reproduction_surface": "cli",
            "required_tools": ["archon-cli", "api", "agent-browser"],
            "comment_policy": "draft_evidence_only",
            "e2e_required": True,
            "static_analysis_only": True,
        },
    )
    assert reproduction.status_code == 200
    reproduction_record = reproduction.json()["record"]
    assert reproduction_record["status"] == "blocked_real_reproduction_required"
    assert reproduction_record["validation_requirements"]["real_reproduction_required"] is True
    assert reproduction_record["validation_requirements"]["static_analysis_sufficient"] is False
    assert reproduction_record["validation_requirements"]["issue_comment_allowed"] == "draft_only_after_evidence"
    assert reproduction_record["execution_allowed"] is False

    pr_validation = client.post(
        "/ops/brain/factory-orchestration/pr-validation",
        json={
            "pr_ref": "repo#80",
            "required_validation_profiles": ["unit", "static", "agent_browser_e2e"],
            "browser_validation_required": True,
            "start_service_status": "failed",
            "deployment_target": "production",
            "merge_policy": "autonomous_merge_requested",
        },
    )
    assert pr_validation.status_code == 200
    pr_record = pr_validation.json()["record"]
    assert pr_record["status"] == "blocked_validation_failed"
    assert pr_record["validation_requirements"]["browser_validation_required"] is True
    assert pr_record["validation_requirements"]["browser_validation_hard_gate"] is True
    assert pr_record["validation_requirements"]["start_service_status"] == "failed"
    assert pr_record["deployment_gate"]["merge_allowed"] is False
    assert pr_record["deployment_gate"]["deployment_allowed"] is False
    assert pr_record["deployment_gate"]["reopen_or_rollback_required"] is True


def test_graphify_dark_factory_status_surfaces_and_telemetry(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    client.post(
        "/ops/brain/context-graph/index-plan",
        json={
            "source": {"source_name": "Graphify", "source_url": GRAPHIFY_REPO},
            "corpus_root": str(project_root),
            "content_kinds": ["code", "docs"],
            "assistant_platforms": ["codex"],
        },
    )
    client.post(
        "/ops/brain/factory-orchestration/triage",
        json={"issues": [{"issue_ref": "repo#1", "title": "bug"}], "max_parallel": 1},
    )

    assimilation = client.get("/ops/brain/assimilation/status")
    assert assimilation.status_code == 200
    assimilation_payload = assimilation.json()
    assert "context_graph" in assimilation_payload
    assert "factory_orchestration" in assimilation_payload
    assert assimilation_payload["context_graph"]["record_count"] == 1
    assert assimilation_payload["factory_orchestration"]["record_count"] == 1

    product = client.get("/ops/brain/product-sweep/status")
    assert product.status_code == 200
    surfaces = product.json()["status_surfaces"]
    assert "context_graph" in surfaces
    assert "factory_orchestration" in surfaces
    assert surfaces["context_graph"]["execution_allowed"] is False
    assert surfaces["factory_orchestration"]["autonomous_merge_allowed"] is False

    telemetry = client.get("/ops/brain/telemetry/normalized")
    assert telemetry.status_code == 200
    counts = telemetry.json()["span_kind_counts"]
    assert counts["context_graph"] >= 1
    assert counts["factory_orchestration"] >= 1

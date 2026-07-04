from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexus.services import build_services
from nexusnet.adapters.dataset_forge import DatasetForge
from nexusnet.curriculum.dataset_radar import DatasetRadar
from nexusnet.growth import HiveModelGrowthEngine
from nexusnet.knowledge import KnowledgeArtifact, KnowledgeArtifactCompiler
from nexusnet.schemas import DreamCycleRequest
from tests.test_nexus_phase1_foundation import make_project


def test_knowledge_artifact_compiler_docs_and_ledger_entry_are_present():
    ledger = Path("docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md").read_text(encoding="utf-8")
    assert "PB-2026-05-05-080" in ledger
    assert "Compiled Knowledge Artifact Layer" in ledger
    compiled_doc = Path("docs/compiled_knowledge_artifact_layer.md").read_text(encoding="utf-8")
    assert "Knowledge Artifact Compiler" in compiled_doc
    assert "source-ref security gate" in compiled_doc
    assert "artifact-trust preview" in compiled_doc
    assert "downstream KRC runtime gate" in compiled_doc
    assert "VentureBeat" in Path("docs/research/compiled_knowledge_layer_review_2026-05-05.md").read_text(encoding="utf-8")
    assert "ADR-2026-05-05" in Path("docs/decisions/ADR-2026-05-05-compiled-knowledge-artifacts.md").read_text(
        encoding="utf-8"
    )


def _source(source_ref: str, text: str, **overrides):
    payload = {
        "source_ref": source_ref,
        "title": source_ref,
        "text": text,
        "source_url": f"https://example.test/{source_ref.replace(':', '/')}",
        "permission_state": "allowed",
        "privacy_class": "public",
        "license_state": "approved_train",
        "rbac_scope": ["operator"],
        "claims": [],
    }
    payload.update(overrides)
    return payload


def test_knowledge_artifact_schema_requires_citations_for_factual_fields():
    artifact = KnowledgeArtifact.model_validate(
        {
            "artifact_id": "kac://artifact/test",
            "artifact_type": "task_context",
            "task_family": "architecture_review",
            "scope": {"rbac_scope": ["operator"]},
            "content": {
                "summary": "NexusNet keeps raw retrieval as a fallback.",
                "facts": [
                    {
                        "field": "retrieval_boundary",
                        "value": "raw retrieval remains fallback",
                    }
                ],
                "relationships": [],
                "open_questions": [],
                "recommended_actions": [],
            },
            "field_citations": {
                "content.summary": ["source:doc-a"],
                "content.facts.0": ["source:doc-a"],
            },
            "source_digests": [{"source_ref": "source:doc-a", "digest": "sha256:abc"}],
            "confidence": {"overall": 0.9, "per_field": {"content.summary": 0.9, "content.facts.0": 0.9}},
            "conflict_objects": [],
            "governance": {"rbac_scope": ["operator"], "status": "candidate"},
            "freshness": {"compiled_at": "2026-05-05T00:00:00Z", "ttl_policy": "source_digest"},
            "status": "candidate",
            "artifact_hash": "sha256:placeholder",
        }
    )
    assert artifact.validation_report()["valid"] is True

    missing_fact_citation = artifact.model_copy(update={"field_citations": {"content.summary": ["source:doc-a"]}})
    report = missing_fact_citation.validation_report()
    assert report["valid"] is False
    assert "content.facts.0" in report["missing_citation_fields"]


def test_knowledge_compiler_is_deterministic_and_detects_source_staleness(tmp_path):
    compiler = KnowledgeArtifactCompiler(artifacts_dir=tmp_path)
    request = {
        "task_family": "architecture_review",
        "scope": {"rbac_scope": ["operator"], "allowed_sources": ["docs", "ledger"]},
        "artifact_shape": {"fields": ["summary", "facts", "recommended_actions"]},
        "freshness_policy": {"ttl_policy": "recompile_on_source_change_or_7d"},
        "sources": [
            _source(
                "doc:compiled-knowledge",
                "KAC compiles typed cited task artifacts. Raw retrieval remains a fallback lane.",
                claims=[
                    {"field": "dependency_policy", "value": "no_pinecone_dependency"},
                    {"field": "retrieval_policy", "value": "raw_retrieval_fallback"},
                ],
            ),
            _source(
                "ledger:pb-2026-05-05-080",
                "PB-2026-05-05-080 starts as candidate until code-backed tests and replay pass.",
                claims=[
                    {"field": "ledger_state", "value": "candidate"},
                    {"field": "promotion_gate", "value": "code_backed_after_tests"},
                ],
            ),
        ],
    }

    first = compiler.compile(request)
    second = compiler.compile(request)

    assert first["artifact_id"].startswith("kac://architecture_review/")
    assert first["artifact_hash"] == second["artifact_hash"]
    assert first["validation"]["valid"] is True
    assert first["status"] == "candidate"
    assert first["fallback_policy"]["raw_retrieval_available"] is True
    assert first["field_citations"]["content.summary"]
    assert {digest["source_ref"] for digest in first["source_digests"]} == {
        "doc:compiled-knowledge",
        "ledger:pb-2026-05-05-080",
    }

    stale = compiler.freshness_report(
        first["artifact_id"],
        [
            _source(
                "doc:compiled-knowledge",
                "KAC compiles typed cited task artifacts. This source changed.",
            ),
            request["sources"][1],
        ],
    )
    assert stale["freshness_state"] == "stale"
    assert stale["changed_source_refs"] == ["doc:compiled-knowledge"]


def test_knowledge_compiler_records_conflicts_and_excludes_unauthorized_sources(tmp_path):
    compiler = KnowledgeArtifactCompiler(artifacts_dir=tmp_path)

    artifact = compiler.compile(
        {
            "task_family": "assimilation_review",
            "scope": {"rbac_scope": ["operator"]},
            "sources": [
                _source(
                    "source:public-a",
                    "KAC should stay local-first.",
                    claims=[{"field": "runtime_dependency", "value": "local_first"}],
                ),
                _source(
                    "source:public-b",
                    "Some vendor material suggests a managed service.",
                    claims=[{"field": "runtime_dependency", "value": "managed_vendor_service"}],
                ),
                _source(
                    "source:restricted",
                    "Private operator-only material should not leak.",
                    permission_state="restricted",
                    privacy_class="private_local",
                    rbac_scope=["private-reviewer"],
                    claims=[{"field": "secret", "value": "do-not-include"}],
                ),
            ],
        }
    )

    assert artifact["excluded_sources"][0]["source_ref"] == "source:restricted"
    assert "do-not-include" not in str(artifact["content"])
    assert artifact["conflict_objects"][0]["field"] == "runtime_dependency"
    assert artifact["conflict_objects"][0]["resolution"] == "conflict_requires_review"
    assert artifact["governance"]["permission_filtered_source_count"] == 1


def test_knowledge_request_contract_prefers_compiled_artifacts_and_records_fallback(tmp_path):
    compiler = KnowledgeArtifactCompiler(artifacts_dir=tmp_path)
    artifact = compiler.compile(
        {
            "task_family": "architecture_review",
            "scope": {"rbac_scope": ["operator"]},
            "sources": [
                _source(
                    "source:docs",
                    "NexusNet Knowledge Artifact Compiler produces typed cited artifacts.",
                    claims=[{"field": "artifact_layer", "value": "typed_cited_context"}],
                )
            ],
        }
    )

    compiled = compiler.query(
        {
            "intent": "produce_assimilation_review",
            "contexts": [artifact["artifact_id"]],
            "filters": {"task_family": "architecture_review"},
            "provenance": {
                "require_field_citations": True,
                "include_confidence": True,
                "include_conflict_notes": True,
            },
            "output_shape": {"type": "assimilation_decision"},
            "budget": {"prefer_compiled_artifacts": True, "fallback_to_raw_retrieval": True},
        }
    )

    assert compiled["fallback_state"] == "compiled_artifact"
    assert compiled["runtime_context_role"] == "compiled_artifact_context"
    assert compiled["mutation_allowed"] is False
    assert compiled["runtime_boundary"] == "compiled_context_refs_only_no_prompt_weight_node_or_promotion_mutation"
    assert "model_weight_mutation" in compiled["blocked_runtime_uses"]
    assert compiled["query_event_ref"].startswith("kac-query:")
    assert compiled["artifact_refs"] == [artifact["artifact_id"]]
    assert compiled["citations"]
    assert compiled["confidence"]["overall"] > 0

    fallback = compiler.query(
        {
            "intent": "missing_context",
            "contexts": ["kac://missing/artifact"],
            "filters": {"task_family": "unknown"},
            "provenance": {"require_field_citations": True},
            "output_shape": {"type": "summary"},
            "budget": {"prefer_compiled_artifacts": True, "fallback_to_raw_retrieval": True},
        }
    )
    assert fallback["fallback_state"] == "raw_retrieval_fallback"
    assert fallback["runtime_context_allowed"] is False
    assert fallback["runtime_context_role"] == "raw_retrieval_recall_only"
    assert fallback["mutation_allowed"] is False
    assert "growth_cycle_context" in fallback["blocked_runtime_uses"]
    assert fallback["query_event_ref"].startswith("kac-query:")
    assert fallback["raw_retrieval_fallback"]["enabled"] is True
    assert fallback["raw_retrieval_fallback"]["query"] == "missing_context"
    summary = compiler.summary()
    assert summary["query_event_count"] == 2
    assert summary["latest_query_event"]["fallback_state"] == "raw_retrieval_fallback"
    events = compiler.query_events()["query_events"]
    assert [event["event_sequence"] for event in events] == [2, 1]
    assert len({event["event_id"] for event in events}) == 2
    assert events[1]["previous_event_hash"] == "genesis"
    assert events[0]["previous_event_hash"] == events[1]["event_hash"]
    reloaded = KnowledgeArtifactCompiler(artifacts_dir=tmp_path)
    reloaded_fallback = reloaded.query(
        {
            "intent": "missing_context_after_restart",
            "contexts": ["kac://missing/again"],
            "filters": {"task_family": "unknown"},
            "provenance": {"require_field_citations": True},
            "output_shape": {"type": "summary"},
            "budget": {"prefer_compiled_artifacts": True, "fallback_to_raw_retrieval": True},
        }
    )
    assert reloaded_fallback["query_event_ref"].startswith("kac-query:")
    reloaded_events = reloaded.query_events()["query_events"]
    assert reloaded_events[0]["event_sequence"] == 3
    assert reloaded_events[0]["previous_event_hash"] == reloaded_events[1]["event_hash"]


def test_knowledge_artifact_api_control_panel_and_blackbox_visibility(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    compiled = client.post(
        "/ops/brain/knowledge-artifacts/compile",
        json={
            "task_family": "architecture_review",
            "scope": {"rbac_scope": ["operator"]},
            "sources": [
                _source(
                    "doc:kac-plan",
                    "KAC compiles task-specific artifacts and keeps Pinecone out of runtime dependencies.",
                    claims=[{"field": "dependency_policy", "value": "no_pinecone_dependency"}],
                )
            ],
        },
    )
    assert compiled.status_code == 200
    artifact = compiled.json()
    assert artifact["artifact_id"].startswith("kac://architecture_review/")

    listing = client.get("/ops/brain/knowledge-artifacts")
    assert listing.status_code == 200
    assert listing.json()["artifact_count"] == 1
    assert listing.json()["latest_artifact"]["artifact_id"] == artifact["artifact_id"]

    detail = client.get(f"/ops/brain/knowledge-artifacts/{artifact['artifact_id'].replace('/', '%2F')}")
    assert detail.status_code == 200
    assert detail.json()["artifact_hash"] == artifact["artifact_hash"]

    query = client.post(
        "/ops/brain/knowledge-artifacts/query",
        json={
            "intent": "produce_assimilation_review",
            "contexts": [artifact["artifact_id"]],
            "filters": {"task_family": "architecture_review"},
            "provenance": {"require_field_citations": True},
            "output_shape": {"type": "assimilation_decision"},
            "budget": {"prefer_compiled_artifacts": True, "fallback_to_raw_retrieval": True},
        },
    )
    assert query.status_code == 200
    assert query.json()["fallback_state"] == "compiled_artifact"
    assert query.json()["query_event_ref"].startswith("kac-query:")
    query_events = client.get("/ops/brain/knowledge-artifacts/query-events")
    assert query_events.status_code == 200
    assert query_events.json()["query_event_count"] == 1
    assert query_events.json()["query_events"][0]["event_id"] == query.json()["query_event_ref"]

    canon = client.get("/ops/brain/canon/knowledge-artifacts")
    assert canon.status_code == 200
    assert canon.json()["status"] == "candidate"
    assert canon.json()["query_event_count"] >= 1
    assert canon.json()["latest_query_event"]["event_id"].startswith("kac-query:")
    assert canon.json()["promotion_readiness"]["code_backed_candidate"] is True
    assert canon.json()["promotion_readiness"]["live_control_plane"] is True
    assert canon.json()["promotion_readiness"]["promoted"] is False
    assert "query_mutation_boundary" in canon.json()["required_controls"]
    consumers = {consumer["consumer_id"] for consumer in canon.json()["code_backed_consumers"]}
    assert {
        "dataset_forge",
        "hive_model_growth_engine",
        "teacher_council_review",
        "recursive_dreaming",
        "deep_replay",
    }.issubset(consumers)
    runtime_gate_coverage = canon.json()["downstream_runtime_gate_coverage"]
    assert runtime_gate_coverage["all_runtime_consumers_gated"] is True
    assert runtime_gate_coverage["gated_consumer_count"] == runtime_gate_coverage["required_consumer_count"]
    assert runtime_gate_coverage["enforced_consumer_count"] == runtime_gate_coverage["required_consumer_count"]
    assert runtime_gate_coverage["all_runtime_consumers_enforced"] is True
    assert runtime_gate_coverage["gate_source"] == "KnowledgeArtifactCompiler.query"
    assert runtime_gate_coverage["proof_ref_count"] >= 8
    assert "tests/test_dataset_forge.py::test_dataset_forge_blocks_kac_refs_when_runtime_context_evidence_is_disallowed" in runtime_gate_coverage["proof_refs"]
    assert "tests/test_nexusnet_brain.py::test_recursive_dream_engine_rejects_disallowed_kac_runtime_context" in runtime_gate_coverage["proof_refs"]
    runtime_consumers = [
        consumer
        for consumer in canon.json()["code_backed_consumers"]
        if consumer.get("runtime_context_consumer")
    ]
    assert runtime_consumers
    assert all(consumer["requires_krc_runtime_context_allowed"] for consumer in runtime_consumers)
    assert all(consumer["blocks_stale_or_quarantined_context"] for consumer in runtime_consumers)
    assert all(consumer["blocks_raw_retrieval_fallback_context"] for consumer in runtime_consumers)
    assert all(consumer["enforcement_state"] == "blocks_disallowed_krc_evidence" for consumer in runtime_consumers)
    assert all(consumer["proof_refs"] for consumer in runtime_consumers)

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "knowledge-artifacts-cockpit"})
    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    assert control_panel["knowledge_artifacts_scorecard"]["artifact_count"] == 1
    assert control_panel["live_refs"]["knowledge_artifacts"] == "/ops/brain/knowledge-artifacts"

    blackbox = client.get("/ops/brain/canon/blackbox", params={"session_id": "knowledge-artifacts-cockpit"}).json()
    assert blackbox["scorecard_refs"]["knowledge_artifacts"] == "/ops/brain/canon/knowledge-artifacts"
    frame = next(frame for frame in blackbox["frames"] if frame["frame_id"] == "knowledge-artifacts")
    assert "/ops/brain/knowledge-artifacts/compile" in frame["evidence_refs"]
    assert "/ops/brain/knowledge-artifacts/query-events" in frame["evidence_refs"]
    assert "/ops/brain/knowledge-artifacts/freshness" in frame["evidence_refs"]
    assert "/ops/brain/knowledge-artifacts/{artifact_id}" in frame["replay_refs"]
    assert "field_level_citations" in frame["compliance_controls"]
    assert "raw_retrieval_fallback" in frame["compliance_controls"]
    assert "raw_retrieval_recall_only_boundary" in frame["compliance_controls"]
    assert "query_mutation_boundary" in frame["compliance_controls"]
    assert "source_ref_security_gate" in frame["compliance_controls"]
    assert "blocked_source_ref_replay" in frame["compliance_controls"]
    assert "artifact_trust_preview" in frame["compliance_controls"]
    assert "artifact_trust_scan" in frame["compliance_controls"]
    assert "downstream_krc_runtime_gate_coverage" in frame["compliance_controls"]

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Knowledge Artifact Compiler" in ui.text
    assert "knowledgeArtifactsScorecard" in ui.text
    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderKnowledgeArtifactsScorecard" in app_js
    assert "KAC code-backed consumers" in app_js
    assert "KAC downstream runtime gate coverage" in app_js
    assert "requires KRC runtime context allowed" in app_js
    assert "blocks raw fallback" in app_js
    assert "proofs" in app_js
    assert "code-enforced" in app_js
    assert "/ops/brain/canon/knowledge-artifacts" in app_js


def test_knowledge_artifact_api_reports_freshness_against_current_sources(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    compiled = client.post(
        "/ops/brain/knowledge-artifacts/compile",
        json={
            "task_family": "architecture_review",
            "sources": [
                _source(
                    "doc:freshness",
                    "KAC freshness starts current.",
                    claims=[{"field": "freshness_policy", "value": "digest"}],
                )
            ],
        },
    ).json()

    freshness = client.post(
        "/ops/brain/knowledge-artifacts/freshness",
        json={
            "artifact_id": compiled["artifact_id"],
            "sources": [
                _source(
                    "doc:freshness",
                    "KAC freshness changed.",
                    claims=[{"field": "freshness_policy", "value": "digest"}],
                )
            ],
        },
    )

    assert freshness.status_code == 200
    report = freshness.json()
    assert report["artifact_id"] == compiled["artifact_id"]
    assert report["freshness_state"] == "stale"
    assert report["changed_source_refs"] == ["doc:freshness"]
    listing = client.get("/ops/brain/knowledge-artifacts")
    assert listing.status_code == 200
    assert listing.json()["stale_count"] == 1
    assert listing.json()["latest_artifact"]["freshness"]["freshness_state"] == "stale"
    canon = client.get("/ops/brain/canon/knowledge-artifacts")
    assert "kac_latest_artifact_stale" in canon.json()["active_runtime_blockers"]
    query = client.post(
        "/ops/brain/knowledge-artifacts/query",
        json={
            "intent": "produce_assimilation_review",
            "contexts": [compiled["artifact_id"]],
            "filters": {"task_family": "architecture_review"},
            "provenance": {"require_field_citations": True},
            "output_shape": {"type": "assimilation_decision"},
            "budget": {"prefer_compiled_artifacts": True, "fallback_to_raw_retrieval": True},
        },
    )
    assert query.status_code == 200
    assert query.json()["fallback_state"] == "compiled_artifact_stale"
    assert query.json()["runtime_context_allowed"] is False
    assert query.json()["freshness_state"]["freshness_state"] == "stale"


def test_knowledge_artifact_compile_resolves_project_local_source_refs(tmp_path):
    project_root = make_project(tmp_path)
    source_path = project_root / "docs" / "kac-source.md"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_text(
        "Project-local KAC source refs let operators compile approved NexusNet docs without pasting raw text.",
        encoding="utf-8",
    )
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/knowledge-artifacts/compile",
        json={
            "task_family": "architecture_review",
            "source_refs": ["docs/kac-source.md"],
            "scope": {"rbac_scope": ["operator"]},
            "governance": {"status": "candidate"},
        },
    )

    assert response.status_code == 200
    artifact = response.json()
    assert artifact["validation"]["valid"] is True
    assert artifact["source_digests"][0]["source_ref"] == "docs/kac-source.md"
    assert artifact["field_citations"]["content.summary"] == ["docs/kac-source.md"]
    assert artifact["excluded_sources"] == []


def test_knowledge_artifact_source_ref_security_gate_blocks_missing_out_of_root_and_private_refs(tmp_path):
    project_root = make_project(tmp_path)
    allowed_path = project_root / "docs" / "kac-allowed.md"
    private_path = project_root / "private" / "operator-secret.md"
    outside_path = tmp_path / "outside.md"
    allowed_path.parent.mkdir(parents=True, exist_ok=True)
    private_path.parent.mkdir(parents=True, exist_ok=True)
    allowed_path.write_text("Allowed KAC source refs stay project-local and replayable.", encoding="utf-8")
    private_path.write_text("raw private operator note must not enter compiled artifacts", encoding="utf-8")
    outside_path.write_text("out-of-root material must not enter compiled artifacts", encoding="utf-8")
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/knowledge-artifacts/compile",
        json={
            "task_family": "architecture_review",
            "source_refs": [
                "docs/kac-allowed.md",
                "docs/missing-kac.md",
                "../outside.md",
                "private/operator-secret.md",
            ],
            "scope": {"rbac_scope": ["operator"]},
        },
    )

    assert response.status_code == 200
    artifact = response.json()
    gate = artifact["source_ref_security_gate"]
    blocked_reasons = {blocked["reason"] for blocked in gate["blocked_source_refs"]}
    assert gate["allowed"] is False
    assert gate["requested_count"] == 4
    assert gate["allowed_count"] == 1
    assert gate["blocked_count"] == 3
    assert {
        "source_ref_not_found",
        "source_ref_outside_project_root",
        "source_ref_private_path_blocked",
    }.issubset(blocked_reasons)
    assert artifact["blocked_source_refs"] == gate["blocked_source_refs"]
    assert artifact["source_digests"][0]["source_ref"] == "docs/kac-allowed.md"
    assert "raw private operator note" not in str(artifact["content"])
    assert "out-of-root material" not in str(artifact["content"])
    assert artifact["artifact_trust_preview"]["status"] == "quarantined"
    assert "kac_source_ref_security_gate_blocked" in artifact["artifact_trust_preview"]["reason_codes"]
    assert artifact["control_panel_replay"]["source_ref_security_gate"]["blocked_count"] == 3
    assert artifact["control_panel_replay"]["artifact_trust_preview"]["status"] == "quarantined"

    canon = client.get("/ops/brain/canon/knowledge-artifacts")
    assert canon.status_code == 200
    canon_payload = canon.json()
    latest = canon_payload["latest_artifact"]
    assert latest["source_ref_security_gate"]["blocked_count"] == 3
    assert latest["artifact_trust_preview"]["status"] == "quarantined"
    assert canon_payload["source_ref_gate_summary"]["latest_blocked_count"] == 3
    assert canon_payload["artifact_trust_preview_summary"]["latest_status"] == "quarantined"
    assert "artifact_trust_preview" in canon_payload["required_controls"]
    assert "artifact_trust_scan" in canon_payload["required_controls"]
    assert canon_payload["operator_actions"]["freshness"]["endpoint"] == "/ops/brain/knowledge-artifacts/freshness"
    assert "kac_latest_artifact_quarantined" in canon_payload["active_runtime_blockers"]
    assert latest["blocked_source_refs"][0]["source_ref"] in {
        "docs/missing-kac.md",
        "../outside.md",
        "private/operator-secret.md",
    }

    query = client.post(
        "/ops/brain/knowledge-artifacts/query",
        json={
            "intent": "produce_assimilation_review",
            "contexts": [artifact["artifact_id"]],
            "filters": {"task_family": "architecture_review"},
            "provenance": {"require_field_citations": True},
            "output_shape": {"type": "assimilation_decision"},
            "budget": {"prefer_compiled_artifacts": True, "fallback_to_raw_retrieval": True},
        },
    )
    assert query.status_code == 200
    queried = query.json()
    assert queried["fallback_state"] == "compiled_artifact_quarantined"
    assert queried["runtime_context_allowed"] is False
    assert queried["quarantine_state"]["reason"] == "artifact_trust_preview_quarantined"
    assert queried["source_ref_security_gate"]["blocked_count"] == 3
    assert queried["artifact_trust_preview"]["status"] == "quarantined"
    assert "kac_source_ref_security_gate_blocked" in queried["artifact_trust_preview"]["reason_codes"]
    assert queried["blocked_source_refs"] == artifact["blocked_source_refs"]

    trust_scan = client.post(
        "/ops/brain/artifact-trust/knowledge-artifacts/scan",
        json={"artifact_id": artifact["artifact_id"]},
    )
    assert trust_scan.status_code == 200
    assert trust_scan.json()["status"] == "quarantined"
    assert trust_scan.json()["metadata"]["source_ref_security_gate"]["blocked_count"] == 3

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "kac-source-ref-gates"})
    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    scorecard = control_panel["knowledge_artifacts_scorecard"]
    assert scorecard["latest_artifact"]["source_ref_security_gate"]["blocked_count"] == 3
    page = next(page for page in control_panel["pages"] if page["page_id"] == "knowledge-artifacts")
    assert page["metrics"]["query_event_count"] >= 1
    assert page["metrics"]["blocked_source_ref_count"] == 3
    assert page["metrics"]["artifact_trust_preview_status"] == "quarantined"
    assert page["metrics"]["active_runtime_blocker_count"] >= 1
    assert page["metrics"]["downstream_runtime_gate_gated_count"] == 4
    assert page["metrics"]["downstream_runtime_gate_required_count"] == 4
    assert page["metrics"]["downstream_runtime_gate_enforced_count"] == 4
    assert page["metrics"]["downstream_runtime_gate_all_gated"] is True
    assert page["metrics"]["downstream_runtime_gate_proof_ref_count"] >= 8
    assert "/ops/brain/artifact-trust/knowledge-artifacts/scan" in page["evidence_refs"]
    assert "/ops/brain/knowledge-artifacts/query-events" in page["evidence_refs"]
    assert "tests/test_dataset_forge.py::test_dataset_forge_blocks_kac_refs_when_runtime_context_evidence_is_disallowed" in page["evidence_refs"]
    assert "source-ref security gate" in page["required_surfaces"]
    assert "artifact trust preview" in page["required_surfaces"]
    assert "runtime gate proof refs" in page["required_surfaces"]

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "KAC source-ref security gate" in app_js
    assert "KAC source-ref gate summary" in app_js
    assert "KAC trust-preview summary" in app_js
    assert "KAC active runtime blockers" in app_js
    assert "KAC query history" in app_js
    assert "blocked source refs" in app_js
    assert "scanLatestKnowledgeArtifactTrust" in app_js
    assert "data-kac-artifact-trust-scan" in app_js
    assert "/ops/brain/artifact-trust/knowledge-artifacts/scan" in app_js


def test_kac_disallowed_query_payload_is_rejected_by_runtime_consumers(tmp_path):
    compiler = KnowledgeArtifactCompiler(artifacts_dir=tmp_path / "artifacts", source_root=tmp_path)
    artifact = compiler.compile(
        {
            "task_family": "architecture_review",
            "source_refs": [".env"],
            "scope": {"rbac_scope": ["operator"]},
            "freshness_policy": {"ttl_policy": "recompile_on_source_change_or_7d"},
            "governance": {},
        }
    )
    queried = compiler.query(
        {
            "intent": "seed_training_material",
            "contexts": [artifact["artifact_id"]],
            "filters": {"task_family": "architecture_review"},
            "provenance": {"require_field_citations": True},
            "output_shape": {"type": "runtime_context"},
            "budget": {"prefer_compiled_artifacts": True, "fallback_to_raw_retrieval": True},
        }
    )

    assert queried["runtime_context_allowed"] is False
    assert queried["artifact_id"] == artifact["artifact_id"]
    assert queried["artifact_ref"] == artifact["artifact_id"]

    forge = DatasetForge(dataset_radar=DatasetRadar())
    manifest = forge.build(
        {
            "dataset_manifest_id": "dataset::kac-query-payload-blocked",
            "purpose": "Direct KRC result must be blocked before DatasetForge training use.",
            "knowledge_artifact_refs": queried["artifact_refs"],
            "knowledge_artifact_runtime_contexts": [queried],
            "sources": [
                {
                    "source_id": "doc::compiled-context-seed",
                    "source_type": "document",
                    "text": "A quarantined compiled artifact cannot become training context.",
                    "license_status": "approved",
                    "contains_private_data": False,
                    "provenance_ref": "docs/compiled_knowledge_artifact_layer.md",
                }
            ],
        }
    )
    assert manifest["status"] == "blocked"
    assert manifest["knowledge_artifact_runtime_gate"]["blocked_artifact_refs"] == [artifact["artifact_id"]]

    growth = HiveModelGrowthEngine(artifacts_dir=tmp_path / "growth")
    cycle = growth.start_dry_run(
        {
            "cycle_id": "cycle:cyc_kac_query_payload_blocked",
            "target_node_id": "node:expert_coder",
            "target_node_type": "Expert",
            "target_capabilities": ["multi_file_patch", "test_repair"],
            "student_kind": "child_expert",
            "birth_reason": "Direct KRC result must be blocked before growth use.",
            "teacher_pairing_refs": ["teacher:qwen3-coder-next", "node:expert_critique"],
            "knowledge_artifact_refs": queried["artifact_refs"],
            "knowledge_artifact_runtime_contexts": [queried],
        }
    )
    assert cycle["status"] == "blocked"
    growth_gate = cycle["growth_gate"]["knowledge_artifact_runtime_gate"]
    assert growth_gate["blocked_artifact_refs"] == [artifact["artifact_id"]]
    blocker = next(blocker for blocker in cycle["growth_gate"]["blockers"] if blocker["rule_id"] == "growth_engine_kac_runtime_context_blocked")
    assert blocker["blocked_artifact_refs"] == [artifact["artifact_id"]]

    services = build_services(str(make_project(tmp_path)))
    dream = services.brain_dreaming.run_cycle(
        brain=services.brain,
        request=DreamCycleRequest(
            seed="Direct KRC result must be blocked before dream use.",
            model_hint="mock/default",
            variant_count=2,
            knowledge_artifact_refs=queried["artifact_refs"],
            knowledge_artifact_runtime_contexts=[queried],
        ),
    )
    assert dream.status == "rejected"
    assert dream.compiled_knowledge_context["blocked_artifact_refs"] == [artifact["artifact_id"]]


def test_kac_raw_retrieval_fallback_payload_is_recall_only_not_growth_context(tmp_path):
    compiler = KnowledgeArtifactCompiler(artifacts_dir=tmp_path / "artifacts", source_root=tmp_path)
    fallback = compiler.query(
        {
            "intent": "missing_context",
            "contexts": ["kac://missing/artifact"],
            "filters": {"task_family": "unknown"},
            "provenance": {"require_field_citations": True},
            "output_shape": {"type": "runtime_context"},
            "budget": {"prefer_compiled_artifacts": True, "fallback_to_raw_retrieval": True},
        }
    )
    assert fallback["fallback_state"] == "raw_retrieval_fallback"
    assert fallback["runtime_context_allowed"] is False
    assert fallback["runtime_context_role"] == "raw_retrieval_recall_only"

    forge = DatasetForge(dataset_radar=DatasetRadar())
    manifest = forge.build(
        {
            "dataset_manifest_id": "dataset::kac-raw-fallback-blocked",
            "purpose": "Raw retrieval fallback cannot seed DatasetForge training use.",
            "knowledge_artifact_refs": [],
            "knowledge_artifact_runtime_contexts": [fallback],
            "sources": [
                {
                    "source_id": "doc::compiled-context-seed",
                    "source_type": "document",
                    "text": "Raw retrieval fallback is a recall lane, not a compiled training artifact.",
                    "license_status": "approved",
                    "contains_private_data": False,
                    "provenance_ref": "docs/compiled_knowledge_artifact_layer.md",
                }
            ],
        }
    )
    assert manifest["status"] == "blocked"
    assert manifest["knowledge_artifact_runtime_gate"]["blocked_reasons"] == ["raw_retrieval_fallback"]

    growth = HiveModelGrowthEngine(artifacts_dir=tmp_path / "growth")
    cycle = growth.start_dry_run(
        {
            "cycle_id": "cycle:cyc_kac_raw_fallback_blocked",
            "target_node_id": "node:expert_coder",
            "target_node_type": "Expert",
            "target_capabilities": ["multi_file_patch", "test_repair"],
            "student_kind": "child_expert",
            "birth_reason": "Raw retrieval fallback cannot seed growth context.",
            "teacher_pairing_refs": ["teacher:qwen3-coder-next", "node:expert_critique"],
            "knowledge_artifact_refs": [],
            "knowledge_artifact_runtime_contexts": [fallback],
        }
    )
    assert cycle["status"] == "blocked"
    assert cycle["growth_gate"]["knowledge_artifact_runtime_gate"]["blocked_reasons"] == ["raw_retrieval_fallback"]

    services = build_services(str(make_project(tmp_path)))
    dream = services.brain_dreaming.run_cycle(
        brain=services.brain,
        request=DreamCycleRequest(
            seed="Raw retrieval fallback cannot seed dream context.",
            model_hint="mock/default",
            variant_count=2,
            knowledge_artifact_refs=[],
            knowledge_artifact_runtime_contexts=[fallback],
        ),
    )
    assert dream.status == "rejected"
    assert dream.compiled_knowledge_context["blocked_reasons"] == ["raw_retrieval_fallback"]


def test_kac_disallowed_query_payload_is_rejected_by_operator_apis(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    artifact = client.post(
        "/ops/brain/knowledge-artifacts/compile",
        json={
            "task_family": "architecture_review",
            "source_refs": ["private/operator-secret.md"],
            "scope": {"rbac_scope": ["operator"]},
            "freshness_policy": {"ttl_policy": "recompile_on_source_change_or_7d"},
            "governance": {},
        },
    )
    assert artifact.status_code == 200
    artifact_payload = artifact.json()

    query = client.post(
        "/ops/brain/knowledge-artifacts/query",
        json={
            "intent": "seed_training_material",
            "contexts": [artifact_payload["artifact_id"]],
            "filters": {"task_family": "architecture_review"},
            "provenance": {"require_field_citations": True},
            "output_shape": {"type": "runtime_context"},
            "budget": {"prefer_compiled_artifacts": True, "fallback_to_raw_retrieval": True},
        },
    )
    assert query.status_code == 200
    queried = query.json()
    assert queried["runtime_context_allowed"] is False
    assert queried["artifact_id"] == artifact_payload["artifact_id"]

    manifest = client.post(
        "/ops/brain/dataset-forge/manifests",
        json={
            "dataset_manifest_id": "dataset::kac-api-query-payload-blocked",
            "purpose": "Direct KRC result must be blocked before DatasetForge API training use.",
            "knowledge_artifact_refs": queried["artifact_refs"],
            "knowledge_artifact_runtime_contexts": [queried],
            "sources": [
                {
                    "source_id": "doc::compiled-context-seed",
                    "source_type": "document",
                    "text": "A quarantined compiled artifact cannot become training context.",
                    "license_status": "approved",
                    "contains_private_data": False,
                    "provenance_ref": "docs/compiled_knowledge_artifact_layer.md",
                }
            ],
        },
    )
    assert manifest.status_code == 200
    assert manifest.json()["status"] == "blocked"
    assert manifest.json()["knowledge_artifact_runtime_gate"]["blocked_artifact_refs"] == [artifact_payload["artifact_id"]]

    cycle = client.post(
        "/ops/brain/growth-engine/cycles",
        json={
            "cycle_id": "cycle:cyc_kac_api_query_payload_blocked",
            "target_node_id": "node:expert_coder",
            "target_node_type": "Expert",
            "target_capabilities": ["multi_file_patch", "test_repair"],
            "student_kind": "child_expert",
            "birth_reason": "Direct KRC result must be blocked before API growth use.",
            "teacher_pairing_refs": ["teacher:qwen3-coder-next", "node:expert_critique"],
            "knowledge_artifact_refs": queried["artifact_refs"],
            "knowledge_artifact_runtime_contexts": [queried],
        },
    )
    assert cycle.status_code == 200
    assert cycle.json()["status"] == "blocked"
    assert cycle.json()["growth_gate"]["knowledge_artifact_runtime_gate"]["blocked_artifact_refs"] == [
        artifact_payload["artifact_id"]
    ]

    dream = client.post(
        "/ops/brain/dream",
        json={
            "seed": "Direct KRC result must be blocked before API dream use.",
            "model_hint": "mock/default",
            "variant_count": 2,
            "knowledge_artifact_refs": queried["artifact_refs"],
            "knowledge_artifact_runtime_contexts": [queried],
        },
    )
    assert dream.status_code == 200
    assert dream.json()["status"] == "rejected"
    assert dream.json()["compiled_knowledge_context"]["blocked_artifact_refs"] == [artifact_payload["artifact_id"]]


def test_knowledge_artifact_source_ref_security_gate_blocks_absolute_refs(tmp_path):
    project_root = make_project(tmp_path)
    source_path = project_root / "docs" / "absolute-source.md"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_text("Absolute workstation paths must not become portable KAC source refs.", encoding="utf-8")
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/knowledge-artifacts/compile",
        json={
            "task_family": "architecture_review",
            "source_refs": [str(source_path)],
            "scope": {"rbac_scope": ["operator"]},
        },
    )

    assert response.status_code == 200
    artifact = response.json()
    gate = artifact["source_ref_security_gate"]
    assert gate["allowed"] is False
    assert gate["requested_count"] == 1
    assert gate["allowed_count"] == 0
    assert gate["blocked_count"] == 1
    assert artifact["blocked_source_refs"][0]["reason"] == "source_ref_absolute_path_blocked"
    assert artifact["source_digests"] == []
    assert "Absolute workstation paths" not in str(artifact["content"])


def test_knowledge_artifact_source_ref_security_gate_blocks_directory_refs(tmp_path):
    project_root = make_project(tmp_path)
    docs_dir = project_root / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir / "inside.md").write_text("Directory refs must not trigger bulk reads.", encoding="utf-8")
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/knowledge-artifacts/compile",
        json={
            "task_family": "architecture_review",
            "source_refs": ["docs"],
            "scope": {"rbac_scope": ["operator"]},
        },
    )

    assert response.status_code == 200
    artifact = response.json()
    assert artifact["source_ref_security_gate"]["blocked_count"] == 1
    assert artifact["blocked_source_refs"][0]["reason"] == "source_ref_directory_blocked"
    assert artifact["source_digests"] == []
    assert "Directory refs must not trigger bulk reads" not in str(artifact["content"])


def test_knowledge_artifact_store_index_records_source_ref_and_trust_replay(tmp_path):
    project_root = make_project(tmp_path)
    source_path = project_root / "docs" / "indexed-source.md"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_text("Indexed KAC source refs stay replayable.", encoding="utf-8")
    compiler = KnowledgeArtifactCompiler(artifacts_dir=tmp_path / "artifacts", source_root=project_root)

    artifact = compiler.compile(
        {
            "task_family": "architecture_review",
            "source_refs": ["docs/indexed-source.md", "private/not-readable.md"],
            "scope": {"rbac_scope": ["operator"]},
        }
    )

    index_path = tmp_path / "artifacts" / "knowledge" / "index.jsonl"
    entries = [json.loads(line) for line in index_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert entries[-1]["artifact_id"] == artifact["artifact_id"]
    assert entries[-1]["source_ref_gate"]["blocked_count"] == 1
    assert entries[-1]["source_ref_gate"]["blocked_reason_counts"]["source_ref_private_path_blocked"] == 1
    assert entries[-1]["artifact_trust_preview"]["status"] == "quarantined"

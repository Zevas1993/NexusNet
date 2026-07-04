from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from nexus.api.app import create_app
from nexusnet.canon import NexusNetCanonRegistry, ResearchCandidate
from nexusnet.experts.council import ExpertCouncil
from nexusnet.memory.operating_system import MemoryOperatingSystem
from nexusnet.protocols.security import ProtocolSecurityLayer, ToolAttempt
from nexusnet.runtime.product_profiles import ProductRuntimeProfileRegistry
from nexusnet.schemas import SessionContext
from nexusnet.training.contracts import TrainingDataExportRecord
from tests.test_nexus_phase1_foundation import make_project


def test_canon_registry_locks_decisions_and_candidate_metadata():
    registry = NexusNetCanonRegistry()

    validation = registry.validate()
    assert validation["ok"] is True
    assert validation["locked_decision_count"] >= 5
    assert validation["unresolved_decision_count"] >= 1
    assert len(registry.expert_roster()) == 19
    assert {expert.status for expert in registry.expert_roster()} == {"locked"}

    candidates = {candidate.id: candidate for candidate in registry.research_candidates()}
    assert candidates["openrlhf"].integration_status == "candidate_requires_pin"
    assert candidates["graphiti-zep"].source_url.startswith("https://")
    assert all(candidate.verified_at for candidate in candidates.values())
    assert all(candidate.license for candidate in candidates.values())

    with pytest.raises(ValidationError):
        ResearchCandidate(
            id="bad",
            name="Bad Candidate",
            category="memory",
            source_url="",
            verified_at="",
            license="",
            evidence_level="",
            integration_status="candidate",
            replacement_target="",
            notes="",
        )


def test_canon_status_api_exposes_product_sweep_surfaces(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    canon = client.get("/ops/brain/canon")
    assert canon.status_code == 200
    canon_payload = canon.json()
    assert canon_payload["status"] == "locked_with_candidates"
    assert canon_payload["repo_split"]["brain_core"] == "nexusnet/"
    assert canon_payload["expert_roster"]["locked_count"] == 19

    candidates = client.get("/ops/brain/research-candidates")
    assert candidates.status_code == 200
    assert any(item["id"] == "deep-eval" for item in candidates.json()["candidates"])

    product_status = client.get("/ops/brain/product-status")
    assert product_status.status_code == 200
    payload = product_status.json()
    assert payload["security"]["external_tools_default"] == "deny_until_policy_allows"
    assert payload["training"]["real_training_status"] == "gated"
    roadmap = Path(__file__).resolve().parents[1] / "docs" / "NEXUSNET_FULL_PRODUCT_SWEEP_ROADMAP.md"
    roadmap_text = roadmap.read_text(encoding="utf-8")
    assert "Status source of truth" in roadmap_text
    assert "`candidate_requires_pin`" in roadmap_text


def test_memory_operating_system_tracks_current_historical_and_evidence_truth():
    memory = MemoryOperatingSystem()
    first_time = datetime(2026, 4, 20, tzinfo=timezone.utc)
    second_time = first_time + timedelta(days=2)

    first = memory.store(
        fact_id="nexusnet.goal",
        content="NexusNet is a neural-core brain with wrapper surfaces.",
        source="38-chat-synthesis",
        evidence={"chat": "NEXUSNET_38_CHAT_IDEA_SYNTHESIS.md", "lineage": "historical"},
        effective_at=first_time,
    )
    second = memory.update(
        fact_id="nexusnet.goal",
        content="NexusNet is a neural-core brain with trace-first evals and governed protocol tools.",
        source="april-2026-research-refresh",
        evidence={"registry": "assimilation", "lineage": "research-refresh"},
        effective_at=second_time,
    )

    assert memory.retrieve("nexusnet.goal").content == second.content
    assert memory.retrieve("nexusnet.goal", as_of=first_time + timedelta(hours=1)).content == first.content
    assert memory.dereference(second.memory_id)["evidence"]["registry"] == "assimilation"
    assert memory.provenance_lookup("nexusnet.goal")["version_count"] == 2

    memory.archive("nexusnet.goal")
    assert memory.retrieve("nexusnet.goal") is None
    assert memory.retrieve("nexusnet.goal", include_archived=True).archived is True


def test_secure_protocol_layer_rejects_untrusted_secret_and_unsandboxed_tools():
    layer = ProtocolSecurityLayer()

    untrusted = layer.evaluate(
        ToolAttempt(
            tool_id="browsermcp.navigate",
            protocol="mcp",
            server_signed=False,
            server_allowlisted=True,
            sandboxed=True,
            permissions=["read"],
            approval_granted=True,
            identity_metadata={"user": "operator"},
        )
    )
    assert untrusted.status == "denied"
    assert "signed" in untrusted.reason

    secret_form = layer.evaluate(
        ToolAttempt(
            tool_id="browsermcp.login",
            protocol="mcp",
            server_signed=True,
            server_allowlisted=True,
            sandboxed=True,
            permissions=["read"],
            elicitation_mode="form",
            handles_secret=True,
            approval_granted=True,
            identity_metadata={"user": "operator"},
        )
    )
    assert secret_form.status == "denied"
    assert secret_form.reason == "secret_elicitation_requires_url_or_out_of_band"

    consent_needed = layer.evaluate(
        ToolAttempt(
            tool_id="browsermcp.navigate",
            protocol="mcp",
            server_signed=True,
            server_allowlisted=True,
            sandboxed=True,
            permissions=["read"],
            approval_granted=False,
            identity_metadata={"user": "operator"},
        )
    )
    assert consent_needed.status == "hold"
    assert len(layer.audit_log()) == 3


def test_runtime_training_council_and_trace_contracts_are_gated():
    runtime_registry = ProductRuntimeProfileRegistry()
    cloud = runtime_registry.select_profile("cloud", requested_adapter="vllm")
    unsupported = runtime_registry.select_profile("local", requested_adapter="ui-tars")
    assert cloud.runnable is False
    assert cloud.status == "candidate"
    assert unsupported.runnable is False
    assert unsupported.fallback_profile == "local"

    training_record = TrainingDataExportRecord(
        trace_id="trace-1",
        prompt="Explain NexusNet.",
        output="NexusNet is a neural-core brain.",
        provenance=[{"source": "trace", "id": "trace-1"}],
        teacher_source={"teacher_id": "qwen3-30b-a3b", "registry_layer": "v2026_live"},
        capsule_source={"capsule_id": "researcher", "status": "locked"},
        safety_labels=["policy_checked"],
        eval_target="trace-first-evals",
        license_metadata={"status": "candidate_requires_review", "source": "assimilation-registry"},
    )
    assert training_record.ready_for_checkpoint() is False

    council = ExpertCouncil()
    decision = council.deliberate(
        prompt="Should dream outputs mutate production memory?",
        selected_experts=["memory-weaver", "security", "critique"],
    )
    assert decision.status == "shadow_only"
    assert decision.can_mutate_production is False
    assert decision.policy_bypass_allowed is False


def test_brain_generate_emits_product_trace_contract(tmp_path):
    project_root = make_project(tmp_path)
    app = create_app(str(project_root))
    services = app.state.services
    result = services.brain.generate(
        session_context=SessionContext(
            session_id="trace-contract",
            expert="researcher",
            use_retrieval=False,
        ),
        prompt="Summarize NexusNet in one sentence.",
        model_hint="mock/default",
    )
    product_trace = result.inference_trace.metrics["product_trace"]

    assert product_trace["trace_id"] == result.trace_id
    assert product_trace["brain_path"] == "NexusBrain.generate"
    assert product_trace["capsule_routes"][0]["capsule_id"] == "researcher"
    assert product_trace["memory_operations"]
    assert product_trace["security_decisions"][0]["status"] == "brain_internal_only"
    assert product_trace["critique_events"][0]["critique_id"] == result.critique.critique_id
    assert product_trace["eval_labels"] == ["trace_first", "diagnostic_only"]

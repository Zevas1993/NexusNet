from __future__ import annotations

from pathlib import Path

import pytest

from nexusnet.graph.intelligence import NexusGraphIntelligenceFabric
from nexusnet.context_graph import ContextGraphService
from nexusnet.operations.change_passport import OperationalChangeRegistry
from nexus.services import build_services
from tests.test_nexus_phase1_foundation import make_project


def test_nexusgraph_fact_query_and_evolution_passports_are_durable(tmp_path: Path) -> None:
    graph = NexusGraphIntelligenceFabric(artifacts_dir=tmp_path)
    fact = graph.record_fact(
        fact_id="fact:router-owner",
        subject_ref="component:router",
        predicate="owned_by",
        object_ref="brain:NexusBrain",
        source_refs=["canon:router", "code:router"],
        confidence=0.95,
        privacy_class="internal",
        owner="NexusBrain",
        mutability="governed",
    )
    graph.record_fact(
        fact_id="fact:router-provider",
        subject_ref="component:router",
        predicate="selects",
        object_ref="provider:local",
        source_refs=["code:provider-registry"],
        confidence=0.9,
        privacy_class="internal",
        owner="NexusBrain",
        mutability="governed",
    )

    query = graph.query(
        query_id="query:router",
        terms=["router"],
        purpose="impact-review",
        requester="GovernanceAO",
        allowed_privacy_classes=["public", "internal"],
        top_k=10,
    )
    assert fact["passport_kind"] == "GraphFactPassport"
    assert query["passport_kind"] == "GraphQueryPassport"
    assert {item["fact_id"] for item in query["hits"]} == {
        "fact:router-owner",
        "fact:router-provider",
    }
    assert query["raw_private_content_included"] is False

    proposal = graph.propose_evolution(
        proposal_id="evolution:add-edge",
        operations=[
            {
                "operation": "add_fact",
                "fact": {
                    "fact_id": "fact:router-policy",
                    "subject_ref": "component:router",
                    "predicate": "governed_by",
                    "object_ref": "policy:kernel",
                    "source_refs": ["code:policy-kernel"],
                    "confidence": 0.92,
                    "privacy_class": "internal",
                    "owner": "NexusBrain",
                    "mutability": "governed",
                },
            }
        ],
        evidence_refs=["test:graph-evolution"],
        rollback_plan={"remove_fact_ids": ["fact:router-policy"]},
        eval_passed=True,
        operator_approved=True,
    )
    applied = graph.apply_evolution(proposal["proposal_id"])
    assert proposal["passport_kind"] == "GraphEvolutionPassport"
    assert applied["status"] == "applied"
    assert graph.fact("fact:router-policy") is not None

    restarted = NexusGraphIntelligenceFabric(artifacts_dir=tmp_path)
    assert restarted.fact("fact:router-policy") is not None
    rolled_back = restarted.rollback_evolution(proposal["proposal_id"])
    assert rolled_back["status"] == "rolled-back"
    assert restarted.fact("fact:router-policy") is None


def test_nexusgraph_rejects_uncited_facts_and_ungated_evolution(tmp_path: Path) -> None:
    graph = NexusGraphIntelligenceFabric(artifacts_dir=tmp_path)
    with pytest.raises(ValueError, match="source_refs"):
        graph.record_fact(
            fact_id="fact:uncited",
            subject_ref="a",
            predicate="b",
            object_ref="c",
            source_refs=[],
            confidence=1.0,
            privacy_class="internal",
            owner="NexusBrain",
            mutability="governed",
        )
    proposal = graph.propose_evolution(
        proposal_id="evolution:blocked",
        operations=[],
        evidence_refs=["eval:missing"],
        rollback_plan={},
        eval_passed=False,
        operator_approved=False,
    )
    assert proposal["status"] == "blocked"
    with pytest.raises(PermissionError):
        graph.apply_evolution(proposal["proposal_id"])


def test_operational_change_passport_gates_and_tracks_rollout(tmp_path: Path) -> None:
    registry = OperationalChangeRegistry(artifacts_dir=tmp_path)
    passport = registry.create(
        change_id="change:runtime-router",
        owner="RuntimeAO",
        goal="Improve local routing",
        source_refs=["ledger:PB-2026-04-30-006"],
        base_state_ref="git:abc123",
        worktree_ref="worktree:router",
        affected_surfaces=["runtime-router", "provider-health"],
        permissions=["read-runtime", "write-shadow-artifact"],
        feature_flag="router-v2",
        evidence_refs=["pytest:router"],
        telemetry_refs=["trace:router"],
        rollback_ref="checkpoint:router-v1",
        approval_refs=["operator:approved"],
    )
    assert passport["passport_kind"] == "OperationalChangePassport"
    assert passport["status"] == "ready-for-shadow"

    shadow = registry.transition(
        passport["change_id"],
        target_stage="shadow",
        monitoring_ref="monitor:shadow",
        rollback_rehearsed=True,
    )
    assert shadow["rollout_stage"] == "shadow"
    canary = registry.transition(
        passport["change_id"],
        target_stage="canary",
        monitoring_ref="monitor:canary",
        rollback_rehearsed=True,
    )
    assert canary["rollout_stage"] == "canary"

    restarted = OperationalChangeRegistry(artifacts_dir=tmp_path)
    assert restarted.get(passport["change_id"])["rollout_stage"] == "canary"


def test_context_graph_and_workflow_live_surfaces_include_passports(tmp_path: Path) -> None:
    context_graph = ContextGraphService(artifacts_dir=tmp_path)
    fact = context_graph.record_graph_fact(
        fact_id="fact:context-live",
        subject_ref="component:context-graph",
        predicate="owned_by",
        object_ref="brain:NexusBrain",
        source_refs=["code:context-graph"],
        confidence=1.0,
        privacy_class="internal",
        owner="NexusBrain",
        mutability="governed",
    )
    assert fact["passport_kind"] == "GraphFactPassport"
    assert context_graph.summary()["nexusgraph_intelligence"]["fact_count"] == 1

    project_root = make_project(tmp_path / "project")
    services = build_services(str(project_root))
    result = services.brain_workflows.execute(
        workflow_id="nexus-package-candidate-review",
        linked_trace_ids=["trace:workflow-passport"],
        approval_path={"decision": "ask"},
    )
    passport = result["operational_change_passport"]
    assert passport["passport_kind"] == "OperationalChangePassport"
    assert passport["status"] == "blocked"
    assert "operator-approval-required" in passport["blockers"]

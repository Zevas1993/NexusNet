from __future__ import annotations

from nexusnet.experts import (
    Cluster9RoleNode,
    Cluster9TeacherReconciliationRegistry,
    build_default_cluster9_teacher_reconciliation_registry,
)


def test_default_cluster9_registry_seeds_memory_graph_and_domain_nodes_with_two_teachers():
    registry = build_default_cluster9_teacher_reconciliation_registry()

    required_nodes = {
        "core.nexus-brain",
        "orchestrator.teacher-lifecycle",
        "orchestrator.expert-evolution",
        "orchestrator.agent-native-memory",
        "orchestrator.nexus-graph",
        "ao.memory-quality",
        "ao.graph-evolution",
        "ao.medical",
        "expert.formal-methods-verifier",
        "expert.medical-safety-reviewer",
        "expert.world-model-researcher",
        "temporary.runtime-crypto-risk-taskforce",
    }
    actual_nodes = {node.node_id for node in registry.list_nodes()}

    assert required_nodes.issubset(actual_nodes)
    assert registry.nodes_missing_teacher_pairing() == []

    summary = registry.summary()
    assert summary["surface_id"] == "cluster9-teacher-expert-reconciliation"
    assert summary["node_count"] >= len(required_nodes)
    assert summary["pairing_gap_count"] == 0
    assert summary["final_roster_claimed"] is False
    assert summary["mother_brain_authority"] == "NexusBrain"


def test_reconciliation_flags_nodes_with_less_than_two_teachers_as_birth_blocking():
    registry = build_default_cluster9_teacher_reconciliation_registry()
    registry.register(
        Cluster9RoleNode(
            node_id="ao.undercovered",
            display_name="Undercovered AO",
            node_type="assistant_orchestrator",
            domain="general",
            teacher_ids=["qwen3-coder-next"],
            source_refs=["test::undercovered"],
        )
    )

    gaps = registry.nodes_missing_teacher_pairing()
    issues = registry.validate()

    assert [gap.node_id for gap in gaps] == ["ao.undercovered"]
    assert any(issue.code == "teacher_pairing_below_minimum" for issue in issues)
    assert registry.summary()["pairing_gap_count"] == 1
    assert registry.summary()["birth_blocking_issue_count"] >= 1


def test_temporary_live_problem_experts_are_shadow_only_and_non_mutating():
    registry = build_default_cluster9_teacher_reconciliation_registry()
    temporary = registry.get("temporary.runtime-crypto-risk-taskforce")

    assert temporary is not None
    assert temporary.node_type == "temporary_expert"
    assert temporary.lifecycle_state == "shadow"
    assert temporary.production_mutation_allowed is False
    assert "ttl_expiry_or_failed_eval" in temporary.retirement_policy

    registry.register(
        Cluster9RoleNode(
            node_id="temporary.unsafe-live-expert",
            display_name="Unsafe Live Expert",
            node_type="temporary_expert",
            domain="security",
            teacher_ids=["qwen3-coder-next", "leanstral-1-5"],
            lifecycle_state="active",
            production_mutation_allowed=True,
            source_refs=["test::unsafe-live-expert"],
        )
    )
    issue_codes = [issue.code for issue in registry.validate()]

    assert "temporary_expert_not_shadow" in issue_codes
    assert "temporary_expert_can_mutate_production" in issue_codes


def test_expert_domain_passport_links_ontology_and_teacher_capability_passports():
    registry = build_default_cluster9_teacher_reconciliation_registry()

    passport = registry.expert_domain_passport("expert.formal-methods-verifier")

    assert passport.node_id == "expert.formal-methods-verifier"
    assert passport.expert_ref == "formal:methods-verifier"
    assert passport.domain == "software"
    assert passport.risk_tier == "medium"
    assert passport.required_teacher_count == 2
    assert [teacher.teacher_id for teacher in passport.teacher_capabilities] == [
        "leanstral-1-5",
        "qwen3-coder-next",
    ]
    leanstral = passport.teacher_capabilities[0]
    assert leanstral.candidate_status == "watchlist"
    assert "formal_methods" in leanstral.domain_scope
    assert "verifier" in leanstral.teacher_roles
    assert "hf::mistralai/Leanstral-1.5-119B-A6B" in leanstral.source_refs


def test_register_rejects_duplicate_nodes_without_explicit_replace_and_returns_copies():
    registry = build_default_cluster9_teacher_reconciliation_registry()
    original = registry.get("ao.memory-quality")
    assert original is not None

    duplicate = original.model_copy(update={"display_name": "Mutated Memory Quality AO"})
    mutable = registry.get("ao.memory-quality")
    assert mutable is not None
    mutable.teacher_ids.clear()

    assert len(registry.get("ao.memory-quality").teacher_ids) == 2
    try:
        registry.register(duplicate)
    except ValueError as exc:
        assert "already registered" in str(exc)
    else:
        raise AssertionError("duplicate Cluster 9 node registration should fail")

    replacement = registry.register(duplicate, replace=True)

    assert replacement.display_name == "Mutated Memory Quality AO"
    assert registry.get("ao.memory-quality").display_name == "Mutated Memory Quality AO"

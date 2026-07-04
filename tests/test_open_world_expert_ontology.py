from __future__ import annotations

import pytest

from nexusnet.experts import ExpertOntologyEntry, OpenWorldExpertOntology, build_default_expert_ontology


def test_bootstrap_ontology_covers_high_risk_domains_with_required_panels():
    ontology = build_default_expert_ontology()

    expected_domains = {"crypto", "finance", "medical", "holistic_medicine", "legal", "security"}
    actual_domains = {entry.domain for entry in ontology.list_entries()}
    assert len(ontology.list_entries()) == 8
    assert expected_domains.issubset(actual_domains)

    crypto_panel = ontology.panel_for_domain("crypto")
    assert crypto_panel.risk_tier == "high"
    assert crypto_panel.required_roles == [
        "domain_expert",
        "risk_compliance_expert",
        "evidence_verifier",
        "critic",
        "source_retriever",
    ]

    holistic = ontology.get("holistic:evidence-reviewer")
    assert holistic is not None
    assert holistic.risk_tier == "high"
    assert "contraindication_screening" in holistic.forbidden_actions
    assert "peer_reviewed" in holistic.evidence_standard
    assert "medical-safety-reviewer" in holistic.verifier_pool

    formal = ontology.get("formal:methods-verifier")
    assert formal is not None
    assert formal.domain == "software"

    security = ontology.get("security:threat-modeler")
    assert security is not None
    assert security.domain == "security"
    assert security.risk_tier == "high"
    assert "threat_modeling" in security.capability_traits

    security_panel = ontology.panel_for_domain("security")
    assert security_panel.risk_tier == "high"
    assert security_panel.blocked_without_panel is True


def test_domain_classifier_routes_crypto_finance_and_holistic_queries_to_high_risk_panels():
    ontology = build_default_expert_ontology()

    crypto = ontology.classify_domain("Audit this Solidity bridge contract and tokenomics risk.")
    assert crypto.domain == "crypto"
    assert crypto.risk_tier == "high"
    assert "risk_compliance_expert" in crypto.required_roles

    finance = ontology.classify_domain("Build a portfolio risk model for taxable brokerage allocation.")
    assert finance.domain == "finance"
    assert finance.risk_tier == "high"
    assert "evidence_verifier" in finance.required_roles

    holistic = ontology.classify_domain("Check supplement and herbal interactions with sleep medication.")
    assert holistic.domain == "holistic_medicine"
    assert holistic.risk_tier == "high"
    assert "source_retriever" in holistic.required_roles


def test_domain_classifier_routes_obvious_high_risk_prompts_to_blocked_panels():
    ontology = build_default_expert_ontology()

    cases = [
        ("Give medical treatment advice.", "medical"),
        ("Give financial advice about stocks and investment risk.", "finance"),
        ("Review HIPAA privacy compliance for patient data.", "medical"),
        ("Find a credential vulnerability in this service.", "security"),
        ("Review legal jurisdiction risk for this contract.", "legal"),
    ]

    for prompt, expected_domain in cases:
        panel = ontology.classify_domain(prompt)

        assert panel.domain == expected_domain
        assert panel.risk_tier == "high"
        assert panel.blocked_without_panel is True


def test_capability_lookup_finds_formal_methods_and_world_model_experts():
    ontology = build_default_expert_ontology()

    formal = ontology.coverage_for(["formal_methods", "proof"])
    assert [entry.expert_id for entry in formal] == ["formal:methods-verifier"]

    world = ontology.coverage_for(["simulation", "world_model"])
    assert [entry.expert_id for entry in world] == ["world:world-model-researcher"]


def test_temporary_expert_registration_is_shadow_scoped_and_does_not_replace_bootstrap():
    ontology = build_default_expert_ontology()
    before_count = len(ontology.list_entries())

    temporary = ExpertOntologyEntry(
        expert_id="temporary:runtime-crypto-risk-taskforce",
        display_name="Runtime Crypto Risk Task Force",
        domain="crypto",
        subdomain="runtime-risk",
        capability_traits=["runtime", "crypto", "risk"],
        risk_tier="high",
        regulated_status="regulated",
        evidence_standard=["official_docs", "benchmark_result"],
        allowed_actions=["analysis", "sandbox_recommendation"],
        forbidden_actions=["asset_transfer", "private_key_handling"],
        source_requirements=["official_protocol_docs", "security_audit_refs"],
        teacher_pool=["qwen3-coder-next", "deepseek-v4-pro"],
        critic_pool=["critique"],
        verifier_pool=["security", "legal-risk", "finance-risk"],
        retriever_pool=["retrieval"],
        eval_family=["smart-contract-security", "financial-risk"],
        update_cadence="live_problem_ttl",
        promotion_gates=["sandbox_eval", "security_review", "operator_approval"],
        fallback_experts=["security:smart-contract-auditor"],
        merge_candidates=["security:smart-contract-auditor"],
        retirement_policy="ttl_expiry_or_failed_eval",
        metadata={"temporary": True, "production_mutation_allowed": False},
    )

    ontology.register(temporary)

    assert len(ontology.list_entries()) == before_count + 1
    assert ontology.get("temporary:runtime-crypto-risk-taskforce") == temporary
    assert ontology.get("security:smart-contract-auditor") is not None
    assert ontology.get("temporary:runtime-crypto-risk-taskforce").metadata["production_mutation_allowed"] is False


def test_register_rejects_duplicate_entries_by_default_without_replacing_original():
    original = ExpertOntologyEntry(
        expert_id="custom:duplicate",
        display_name="Original Duplicate Expert",
        domain="general",
        subdomain="original",
        risk_tier="low",
    )
    replacement = ExpertOntologyEntry(
        expert_id="custom:duplicate",
        display_name="Replacement Duplicate Expert",
        domain="security",
        subdomain="replacement",
        risk_tier="high",
    )
    ontology = OpenWorldExpertOntology([original])

    with pytest.raises(ValueError, match="already registered"):
        ontology.register(replacement)

    assert ontology.get("custom:duplicate") == original


def test_register_allows_explicit_replacement():
    original = ExpertOntologyEntry(
        expert_id="custom:replaceable",
        display_name="Original Replaceable Expert",
        domain="general",
        subdomain="original",
        risk_tier="low",
    )
    replacement = ExpertOntologyEntry(
        expert_id="custom:replaceable",
        display_name="Replacement Replaceable Expert",
        domain="security",
        subdomain="replacement",
        risk_tier="high",
    )
    ontology = OpenWorldExpertOntology([original])

    registered = ontology.register(replacement, replace=True)

    assert registered == replacement
    assert ontology.get("custom:replaceable") == replacement


def test_panel_for_domain_uses_max_risk_ordering():
    ontology = OpenWorldExpertOntology(
        [
            ExpertOntologyEntry(
                expert_id="mixed:low",
                display_name="Mixed Low",
                domain="mixed",
                subdomain="low",
                risk_tier="low",
            ),
            ExpertOntologyEntry(
                expert_id="mixed:medium",
                display_name="Mixed Medium",
                domain="mixed",
                subdomain="medium",
                risk_tier="medium",
            ),
        ]
    )

    panel = ontology.panel_for_domain("mixed")

    assert panel.risk_tier == "medium"

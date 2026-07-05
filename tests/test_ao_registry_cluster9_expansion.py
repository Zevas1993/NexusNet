from __future__ import annotations

from nexusnet.aos import build_default_ao_registry


def test_ao_registry_includes_cluster9_memory_graph_dream_and_expert_evolution_lanes():
    registry = build_default_ao_registry()
    names = {ao.name for ao in registry.list()}
    expected = {
        "MemoryQualityAO",
        "MemoryExtractionAO",
        "MemoryRoutingAO",
        "TemporalMemoryAO",
        "MemoryMaintenanceAO",
        "MultimodalMemoryAO",
        "SleepConsolidationAO",
        "MemoryPrivacyAO",
        "MemoryEvalAO",
        "GraphRegistryAO",
        "GraphQueryAO",
        "GraphEvolutionAO",
        "GraphSafetyAO",
        "GraphPrivacyAO",
        "GraphReplayAO",
        "GraphEvalAO",
        "DreamReviewAO",
        "ExpertForgeAO",
        "ExpertMergeAO",
        "ExpertSplitAO",
        "ExpertRetirementAO",
    }

    assert expected.issubset(names)

    graph = registry.get("GraphEvolutionAO")
    assert graph is not None
    assert graph.risk_tier == "high"
    assert "GraphEvolutionPassport" in graph.responsibilities
    assert "graph delta review" in graph.keywords

    memory = registry.get("MemoryPrivacyAO")
    assert memory is not None
    assert memory.risk_tier == "high"
    assert "privacy review" in memory.responsibilities

    dream_review = registry.get("DreamReviewAO")
    assert dream_review is not None
    assert dream_review.risk_tier == "high"
    assert "dream reviewer" in dream_review.keywords

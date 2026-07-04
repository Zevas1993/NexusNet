"""Does the wrapper have EVERY capability needed to birth the best MoE model? (verified, not claimed)."""
from __future__ import annotations

from nexusnet.hive.birth_capability_manifest import birth_capability_manifest, BIRTH_CAPABILITIES
from nexusnet.hive.continuous_assimilation import ContinuousAssimilationLoop


def test_every_birth_capability_mechanism_is_present():
    m = birth_capability_manifest()
    assert m["total"] >= 18
    # each capability's real mechanism imports successfully (verified, not asserted)
    assert m["all_capabilities_present"] is True
    assert m["missing"] == []
    assert m["capability_presence_ratio"] == 1.0


def test_manifest_covers_the_canon_critical_capabilities():
    keys = {c["key"] for c in BIRTH_CAPABILITIES}
    for required in ("wrap_and_capture", "best_output_curation", "quality_scoring",
                     "continuous_training", "federated_learning", "recursive_dreaming",
                     "moe_composition", "birth_gating", "wrapper_absorption", "real_data_birth"):
        assert required in keys


def test_manifest_is_honest_about_product_vs_capability():
    m = birth_capability_manifest()
    # the manifest does NOT overclaim product completeness - only capability presence
    assert "capability-presence-only" in m["claim_boundary"]


def test_best_output_curation_takes_the_best_over_time():
    loop = ContinuousAssimilationLoop(train_threshold=2)
    loop.assimilate(source_model="weak", expert_node="expert.coder", quality=0.3, knowledge_ref="k1")
    loop.assimilate(source_model="strong", expert_node="expert.coder", quality=0.95, knowledge_ref="k2")
    loop.assimilate(source_model="mid", expert_node="expert.coder", quality=0.6, knowledge_ref="k3")
    best = loop.best_outputs("expert.coder", top_k=2)
    assert [r.source_model for r in best] == ["strong", "mid"]      # best-quality first
    curated = loop.curated_training_set("expert.coder", top_k=2, min_quality=0.5)
    assert all(c["quality"] >= 0.5 for c in curated)               # quality-filtered training set
    assert loop.best_source_for("expert.coder") == "strong"       # the best source wins

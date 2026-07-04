from nexusnet.developmental.growth_archive import GrowthArchive
from nexusnet.developmental.promotion_tribunal import PromotionTribunal


def test_growth_archive_preserves_diverse_shadow_candidates(tmp_path):
    archive = GrowthArchive(artifacts_dir=tmp_path)

    first = archive.record_candidate(
        candidate_id="growth:route-cache",
        candidate_type="runtime",
        diversity_key="runtime-cache",
        scores={"quality": 0.78, "safety": 0.95},
        evidence_refs=["eval:shadow-route"],
    )
    second = archive.record_candidate(
        candidate_id="growth:memory-frame",
        candidate_type="memory",
        diversity_key="reference-frame",
        scores={"quality": 0.74, "safety": 0.98},
        evidence_refs=["memory:quality"],
    )

    summary = archive.summary()
    assert first["promotion_state"] == "archived-shadow"
    assert second["promotion_state"] == "archived-shadow"
    assert summary["diversity_key_count"] == 2
    assert summary["production_mutation_allowed"] is False


def test_promotion_tribunal_requires_all_gates_for_active_request():
    tribunal = PromotionTribunal()

    decision = tribunal.decide(
        case_id="case:growth:route-cache",
        candidate_ref="growth:route-cache",
        requested_state="active",
        policy_scan={"summary": {"active_hard_fail_count": 0}},
        eval_gate={"promotion_allowed": True},
        artifact_trust={"promotion_allowed": False, "promotion_blockers": ["signature_missing"]},
        self_review={"status": "accepted-shadow"},
        memory_quality={"status": "verified"},
        rollback={"rollback_restorable": True},
        operator_approved=True,
    )

    assert decision["decision"] == "rejected"
    assert "artifact_trust_not_clear" in decision["blockers"]
    assert decision["active_promotion_allowed"] is False

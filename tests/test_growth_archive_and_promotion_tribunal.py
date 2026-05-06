import json

import pytest
from pydantic import ValidationError

from nexusnet.developmental.contracts import GrowthArchiveCandidate
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


def test_growth_archive_summary_sees_persisted_valid_candidates_after_restart(tmp_path):
    archive = GrowthArchive(artifacts_dir=tmp_path)
    candidate = archive.record_candidate(
        candidate_id="growth:restart-visible",
        candidate_type="research",
        diversity_key="restart",
        scores={"quality": 0.8},
        evidence_refs=["eval:restart"],
    )

    summary = GrowthArchive(artifacts_dir=tmp_path).summary()

    assert summary["candidate_count"] == 1
    assert summary["latest_candidate"]["candidate_id"] == candidate["candidate_id"]


def test_growth_archive_safely_persists_unsafe_ids_inside_root(tmp_path):
    archive = GrowthArchive(artifacts_dir=tmp_path)

    candidate = archive.record_candidate(
        candidate_id="..\\escaped/growth",
        candidate_type="runtime",
        diversity_key="unsafe-path",
        scores={"quality": 0.7},
        evidence_refs=["eval:unsafe"],
    )

    archive_dir = tmp_path / "developmental" / "growth-archive"
    artifact_path = type(tmp_path)(candidate["artifact_path"]).resolve()

    assert artifact_path.parent == archive_dir.resolve()
    assert artifact_path.exists()
    assert not (archive_dir / ".." / "escaped").exists()


def test_growth_archive_does_not_record_phantoms_after_write_failure(tmp_path, monkeypatch):
    archive = GrowthArchive(artifacts_dir=tmp_path)

    def fail_write(*args, **kwargs):
        raise OSError("simulated write failure")

    monkeypatch.setattr(type(tmp_path), "write_text", fail_write)

    with pytest.raises(OSError):
        archive.record_candidate(
            candidate_id="growth:write-failure",
            candidate_type="runtime",
            diversity_key="write-failure",
            scores={"quality": 0.7},
            evidence_refs=["eval:write-failure"],
        )

    assert archive.summary()["candidate_count"] == 0


def test_growth_archive_skips_invalid_disk_files_without_hiding_valid_records(tmp_path):
    archive = GrowthArchive(artifacts_dir=tmp_path)
    valid = archive.record_candidate(
        candidate_id="growth:valid-disk",
        candidate_type="memory",
        diversity_key="valid",
        scores={"quality": 0.9},
        evidence_refs=["eval:valid"],
    )
    archive_dir = tmp_path / "developmental" / "growth-archive"
    (archive_dir / "corrupt.json").write_text("{", encoding="utf-8")
    (archive_dir / "non-object.json").write_text(json.dumps([]), encoding="utf-8")
    (archive_dir / "invalid-model.json").write_text(json.dumps({"candidate_id": "missing-required"}), encoding="utf-8")

    summary = GrowthArchive(artifacts_dir=tmp_path).summary()

    assert summary["candidate_count"] == 1
    assert summary["latest_candidate"]["candidate_id"] == valid["candidate_id"]


def test_growth_archive_dedupes_duplicate_disk_candidates_deterministically(tmp_path):
    archive_dir = tmp_path / "developmental" / "growth-archive"
    archive_dir.mkdir(parents=True)
    first = GrowthArchiveCandidate(
        candidate_id="growth:duplicate",
        candidate_type="tool",
        diversity_key="first",
        evidence_refs=["eval:first"],
        created_at="2026-05-06T00:00:01+00:00",
    ).model_dump(mode="json")
    second = GrowthArchiveCandidate(
        candidate_id="growth:duplicate",
        candidate_type="tool",
        diversity_key="second",
        evidence_refs=["eval:second"],
        created_at="2026-05-06T00:00:02+00:00",
    ).model_dump(mode="json")
    (archive_dir / "a.json").write_text(json.dumps(first), encoding="utf-8")
    (archive_dir / "b.json").write_text(json.dumps(second), encoding="utf-8")

    summary = GrowthArchive(artifacts_dir=tmp_path).summary()

    assert summary["candidate_count"] == 1
    assert summary["latest_candidate"]["candidate_id"] == "growth:duplicate"
    assert summary["latest_candidate"]["diversity_key"] == "second"


def test_growth_archive_rejects_non_finite_scores_without_persisting(tmp_path):
    archive = GrowthArchive(artifacts_dir=tmp_path)

    with pytest.raises(ValidationError):
        archive.record_candidate(
            candidate_id="growth:non-finite",
            candidate_type="runtime",
            diversity_key="score-validation",
            scores={"quality": float("nan")},
            evidence_refs=["eval:score-validation"],
        )

    assert archive.summary()["candidate_count"] == 0
    assert not any((tmp_path / "developmental" / "growth-archive").glob("*.json"))


def test_promotion_tribunal_malformed_policy_counts_do_not_crash():
    decision = PromotionTribunal().decide(
        case_id="case:growth:malformed-policy",
        candidate_ref="growth:malformed-policy",
        requested_state="shadow",
        policy_scan={"summary": {"active_hard_fail_count": "not-an-int"}},
        eval_gate={"promotion_allowed": True},
        artifact_trust={"promotion_allowed": True},
        self_review={"status": "passed"},
        memory_quality={"status": "not_required"},
        rollback={"rollback_restorable": True},
        operator_approved=False,
    )

    assert decision["decision"] == "rejected"
    assert decision["blockers"] == ["policy_scan_not_clear"]


def test_promotion_tribunal_non_finite_policy_counts_do_not_crash():
    decision = PromotionTribunal().decide(
        case_id="case:growth:non-finite-policy",
        candidate_ref="growth:non-finite-policy",
        requested_state="shadow",
        policy_scan={"summary": {"active_hard_fail_count": float("inf")}},
        eval_gate={"promotion_allowed": True},
        artifact_trust={"promotion_allowed": True},
        self_review={"status": "passed"},
        memory_quality={"status": "not_required"},
        rollback={"rollback_restorable": True},
        operator_approved=False,
    )

    assert decision["case_id"] == "case:growth:non-finite-policy"
    assert decision["decision"] == "rejected"
    assert decision["blockers"] == ["policy_scan_not_clear"]
    assert decision["active_promotion_allowed"] is False


@pytest.mark.parametrize(
    "hard_fail_count",
    [float("inf"), float("nan"), "Infinity", "nan", "not-an-int", [], {}],
)
def test_promotion_tribunal_rejects_active_on_malformed_policy_counts(hard_fail_count):
    decision = PromotionTribunal().decide(
        case_id="case:growth:malformed-active-policy",
        candidate_ref="growth:malformed-active-policy",
        requested_state="active",
        policy_scan={"summary": {"active_hard_fail_count": hard_fail_count}},
        eval_gate={"promotion_allowed": True},
        artifact_trust={"promotion_allowed": True},
        self_review={"status": "passed"},
        memory_quality={"status": "verified"},
        rollback={"rollback_restorable": True},
        operator_approved=True,
    )

    assert decision["decision"] == "rejected"
    assert "policy_scan_not_clear" in decision["blockers"]
    assert decision["active_promotion_allowed"] is False


@pytest.mark.parametrize("hard_fail_count", [0, "0"])
def test_promotion_tribunal_accepts_active_when_policy_count_valid_zero(hard_fail_count):
    decision = PromotionTribunal().decide(
        case_id="case:growth:valid-active-policy",
        candidate_ref="growth:valid-active-policy",
        requested_state="active",
        policy_scan={"summary": {"active_hard_fail_count": hard_fail_count}},
        eval_gate={"promotion_allowed": True},
        artifact_trust={"promotion_allowed": True},
        self_review={"status": "passed"},
        memory_quality={"status": "verified"},
        rollback={"rollback_restorable": True},
        operator_approved=True,
    )

    assert decision["decision"] == "accepted-active-request"
    assert decision["blockers"] == []
    assert decision["active_promotion_allowed"] is True


@pytest.mark.parametrize("hard_fail_count", [1, "2"])
def test_promotion_tribunal_blocks_positive_policy_counts(hard_fail_count):
    decision = PromotionTribunal().decide(
        case_id="case:growth:positive-policy",
        candidate_ref="growth:positive-policy",
        requested_state="active",
        policy_scan={"summary": {"active_hard_fail_count": hard_fail_count}},
        eval_gate={"promotion_allowed": True},
        artifact_trust={"promotion_allowed": True},
        self_review={"status": "passed"},
        memory_quality={"status": "verified"},
        rollback={"rollback_restorable": True},
        operator_approved=True,
    )

    assert decision["decision"] == "rejected"
    assert "policy_scan_not_clear" in decision["blockers"]
    assert decision["active_promotion_allowed"] is False

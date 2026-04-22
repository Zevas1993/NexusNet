from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexus.services import build_services
from tests.test_nexus_phase1_foundation import make_project


def _toolsmith_metrics(score: float, *, disagreement: float = 0.12) -> dict[str, float]:
    return {
        "correctness": score,
        "groundedness": score,
        "safety": max(0.75, score),
        "tool_discipline": score,
        "structured_output_conformance": score,
        "efficiency_latency_budget": max(0.68, score),
        "disagreement_severity": disagreement,
        "dream_contamination_sensitivity": max(0.75, score),
        "native_vs_teacher_delta": max(0.0, round(score - 0.75, 3)),
        "rollbackability": 1.0,
    }


def test_teacher_schema_manifest_and_scorecard_versions_are_explicit(tmp_path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    metadata = services.brain_teachers.schema_registry.metadata()
    assert "teacher-scorecard" in metadata["families"]
    assert "teacher-trend-scorecard" in metadata["families"]
    assert Path(services.brain_teachers.schema_manifest_path).exists()

    scorecard = services.brain_teacher_evidence.create_scorecard(
        subject="toolsmith",
        benchmark_family="strict JSON / tool schemas",
        metrics=_toolsmith_metrics(0.90),
    )
    assert scorecard.schema_family == "teacher-scorecard"
    assert scorecard.schema_version == 1
    assert scorecard.schema_compatibility["current_writer_version"] == 1


def test_teacher_trend_scorecard_tracks_repeated_runs_and_disagreement_history(tmp_path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    for score, disagreement in [(0.88, 0.16), (0.90, 0.14), (0.93, 0.12)]:
        services.brain_teacher_evidence.create_scorecard(
            subject="toolsmith",
            benchmark_family="strict JSON / tool schemas",
            metrics=_toolsmith_metrics(score, disagreement=disagreement),
        )
        services.brain_teacher_evidence.create_disagreement(
            subject="toolsmith",
            registry_layer="v2026_live",
            primary_teacher_id="devstral-2",
            secondary_teacher_id="qwen3-coder-next",
            critique_teacher_id="deepseek-r1-distill-qwen-32b",
            efficiency_teacher_id="lfm2",
            arbitration_result="PATCH_DOMAIN_WITH_LFM2_EDITS_THEN_VERIFY",
            rationale="Trend capture test disagreement.",
            benchmark_family="strict JSON / tool schemas",
            primary_output='{"tool":"apply_patch"}',
            secondary_output='{"tool":"shell_command"}',
            threshold_set_id="teacher-v2026-r1",
            teacher_confidence=0.82,
            lfm2_lane="toolsmith",
            lfm2_bounded_ok=True,
        )

    trend = services.brain_teacher_trends.build(
        subject="toolsmith",
        benchmark_family="strict JSON / tool schemas",
        threshold_set_id="teacher-v2026-r1",
        threshold_version=1,
    )

    assert trend.run_count == 3
    assert trend.valid_run_count == 3
    assert trend.recent_artifact_ids
    assert trend.metrics["passing_run_ratio"] >= 0.667
    assert services.store.list_teacher_trend_scorecards(subject="toolsmith", benchmark_family_id="strict JSON / tool schemas", limit=10)


def test_promotion_rejects_unstable_teacher_trends(tmp_path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    scorecards = []
    for score in [0.95, 0.45, 0.92]:
        scorecards.append(
            services.brain_teacher_evidence.create_scorecard(
                subject="toolsmith",
                benchmark_family="strict JSON / tool schemas",
                metrics=_toolsmith_metrics(score, disagreement=0.20),
            )
        )

    bundle = services.brain_teacher_evidence.create_bundle(
        subject="toolsmith",
        registry_layer="v2026_live",
        selected_teacher_roles={
            "primary": "devstral-2",
            "secondary": "qwen3-coder-next",
            "critique": "deepseek-r1-distill-qwen-32b",
            "efficiency": "lfm2",
        },
        arbitration_result="SELECT_BEST",
        benchmark_families=["strict JSON / tool schemas"],
        metrics={"teacher_disagreement_delta": 0.20, "lfm2_bounded_ok": True, "teacher_confidence": 0.81},
        scorecards=[scorecards[-1]],
        threshold_set_id="teacher-v2026-r1",
        benchmark_family="strict JSON / tool schemas",
        lfm2_lane="toolsmith",
    )
    candidate = services.brain_promotions.create_candidate(
        candidate_kind="retrieval-policy",
        subject_id="retrieval-policy::toolsmith",
        baseline_reference="retrieval-policy::baseline",
        challenger_reference="retrieval-policy::candidate",
        lineage="live-derived",
        traceability={
            "teacher_evidence_bundle_id": bundle.bundle_id,
            "teacher_evidence": services.brain_teacher_evidence.bundle_payload(bundle.bundle_id),
            "threshold_set_id": "teacher-v2026-r1",
        },
    )
    evaluation = services.brain_promotions.evaluate_candidate(
        candidate_id=candidate.candidate_id,
        scenario_set=["teacher-backed-output-quality"],
    )

    assert evaluation.decision == "rejected"
    assert evaluation.metrics["trend_report"]["passed"] is False
    assert Path(evaluation.artifacts["trend_report"]).exists()


def test_takeover_requires_repeated_history_and_retirement_shadow_holds_without_it(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    curriculum = client.post(
        "/ops/brain/curriculum/assess",
        json={"phase": "graduate", "subject": "toolsmith", "model_hint": "mock/default"},
    )
    assert curriculum.status_code == 200

    distill = client.post(
        "/ops/brain/distill-dataset",
        json={"name": "teacher-trend-takeover", "trace_limit": 20, "include_dreams": True, "include_curriculum": True},
    )
    assert distill.status_code == 200
    payload = distill.json()

    assert payload["benchmark"]["takeover_trend_report"]["run_count"] == 1
    assert payload["benchmark"]["takeover_trend_report"]["ready"] is False
    assert payload["takeover"]["decision"] == "shadow"
    assert payload["takeover"]["evidence"]["retirement_shadow_record"]["decision"] == "hold"


def test_wrapper_and_ops_expose_schema_and_trend_artifacts(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    for _ in range(3):
        curriculum = client.post(
            "/ops/brain/curriculum/assess",
            json={"phase": "graduate", "subject": "toolsmith", "model_hint": "mock/default"},
        )
        assert curriculum.status_code == 200

    distill = client.post(
        "/ops/brain/distill-dataset",
        json={"name": "teacher-trend-ops", "trace_limit": 20, "include_dreams": True, "include_curriculum": True},
    )
    assert distill.status_code == 200
    candidate = distill.json()["native_takeover_candidate"]
    evaluation = client.post(
        "/ops/brain/promotions/evaluate",
        json={"candidate_id": candidate["candidate_id"], "scenario_set": ["teacher-backed-output-quality"]},
    )
    assert evaluation.status_code == 200

    schema = client.get("/ops/brain/teachers/schema")
    assert schema.status_code == 200
    assert Path(schema.json()["schema_manifest_path"]).exists()

    trends = client.get("/ops/brain/teachers/trends")
    assert trends.status_code == 200
    assert trends.json()["teacher_trends"]
    assert trends.json()["takeover_trends"]

    wrapper = client.get("/ops/brain/wrapper-surface")
    assert wrapper.status_code == 200
    visibility = wrapper.json()["teachers"]["visibility"]
    assert visibility["schema_metadata"]["families"]["teacher-scorecard"]["version"] == 1
    assert visibility["trend_scorecards"]
    assert visibility["takeover_trends"]

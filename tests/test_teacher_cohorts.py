from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexus.services import build_services
from nexusnet.schemas import DistillationArtifactRecord
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


def _seed_toolsmith_history(services, scores: list[float], *, lineage: str = "live-derived") -> list[dict]:
    bundles = []
    for score in scores:
        scorecard = services.brain_teacher_evidence.create_scorecard(
            subject="toolsmith",
            benchmark_family="strict JSON / tool schemas",
            metrics=_toolsmith_metrics(score),
        )
        disagreement = services.brain_teacher_evidence.create_disagreement(
            subject="toolsmith",
            registry_layer="v2026_live",
            primary_teacher_id="devstral-2",
            secondary_teacher_id="qwen3-coder-next",
            critique_teacher_id="deepseek-r1-distill-qwen-32b",
            efficiency_teacher_id="lfm2",
            arbitration_result="PATCH_DOMAIN_WITH_LFM2_EDITS_THEN_VERIFY",
            rationale="Teacher cohort hardening disagreement.",
            benchmark_family="strict JSON / tool schemas",
            primary_output='{"tool":"apply_patch","status":"ok"}',
            secondary_output='{"tool":"apply_patch","status":"ok"}',
            threshold_set_id="teacher-v2026-r1",
            teacher_confidence=0.84,
            lfm2_lane="toolsmith",
            lfm2_bounded_ok=True,
            dream_derived=lineage == "dream-derived",
            live_derived=lineage != "dream-derived",
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
            arbitration_result="PATCH_DOMAIN_WITH_LFM2_EDITS_THEN_VERIFY",
            benchmark_families=["strict JSON / tool schemas"],
            metrics={
                "teacher_disagreement_delta": 0.12,
                "lfm2_bounded_ok": True,
                "teacher_confidence": 0.84,
                "budget_class": "STANDARD",
                "output_form": "TOOL_CALL_STRICT_JSON",
                "risk_tier": "medium",
                "locality": "local_first",
                "hardware_class": "desktop_gpu",
            },
            disagreement_artifacts=[disagreement],
            scorecards=[scorecard],
            threshold_set_id="teacher-v2026-r1",
            benchmark_family="strict JSON / tool schemas",
            lfm2_lane="toolsmith",
            dream_derived=lineage == "dream-derived",
            live_derived=lineage != "dream-derived",
        )
        bundles.append(services.brain_teacher_evidence.bundle_payload(bundle.bundle_id))
    return bundles


def test_fleet_registry_loading_and_auxiliary_roster_preservation(tmp_path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    metadata = services.brain_teachers.metadata()
    assert "coding_agent_fleet" in metadata["fleets"]["fleets"]
    assert "medium" in metadata["fleet_windows"]["windows"]
    assert metadata["cohort_thresholds"]["threshold_set_id"] == "teacher-cohort-v2026-r1"

    assignments = services.brain_teachers.list_assignments()
    curriculum = next(item for item in assignments if item.subject == "curriculum-architect")
    toolsmith = next(item for item in assignments if item.subject == "toolsmith")
    assert curriculum.auxiliary is True
    assert curriculum.roster_position is None
    assert toolsmith.roster_position == 7


def test_fleet_and_cohort_artifacts_persist_with_traceable_dimensions(tmp_path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))
    _seed_toolsmith_history(services, [0.84, 0.86, 0.88, 0.90, 0.91])

    fleet = services.brain_teacher_fleets.build(
        fleet_id="coding_agent_fleet",
        window_id="medium",
        subject="toolsmith",
        teacher_pair_id="devstral-2::qwen3-coder-next",
        budget_class="STANDARD",
        output_form="TOOL_CALL_STRICT_JSON",
        risk_tier="medium",
        locality="local_first",
        hardware_class="desktop_gpu",
    )
    cohort = services.brain_teacher_cohorts.build(
        fleet_id="coding_agent_fleet",
        window_id="medium",
        subject="toolsmith",
        teacher_pair_id="devstral-2::qwen3-coder-next",
        budget_class="STANDARD",
        output_form="TOOL_CALL_STRICT_JSON",
        risk_tier="medium",
        locality="local_first",
        hardware_class="desktop_gpu",
    )

    assert fleet.ready is True
    assert fleet.run_count >= 5
    assert cohort.ready is True
    assert cohort.threshold_set_id == "teacher-cohort-v2026-r1"
    assert Path(fleet.artifact_path).exists()
    assert Path(cohort.artifact_path).exists()
    assert services.store.list_teacher_benchmark_fleet_summaries(fleet_id="coding_agent_fleet", subject="toolsmith", limit=10)
    assert services.store.list_teacher_cohort_scorecards(fleet_id="coding_agent_fleet", subject="toolsmith", limit=10)


def test_promotion_rejects_when_cohort_history_is_insufficient_even_if_trends_exist(tmp_path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))
    bundles = _seed_toolsmith_history(services, [0.88, 0.89, 0.90])
    latest = bundles[-1]

    candidate = services.brain_promotions.create_candidate(
        candidate_kind="retrieval-policy",
        subject_id="retrieval-policy::toolsmith",
        baseline_reference="retrieval-policy::baseline",
        challenger_reference="retrieval-policy::candidate",
        lineage="live-derived",
        traceability={
            "teacher_evidence_bundle_id": latest["bundle_id"],
            "teacher_evidence": latest,
            "threshold_set_id": latest["threshold_set_id"],
        },
    )
    evaluation = services.brain_promotions.evaluate_candidate(
        candidate_id=candidate.candidate_id,
        scenario_set=["teacher-backed-output-quality"],
    )

    assert evaluation.decision == "rejected"
    assert evaluation.metrics["trend_report"]["passed"] is True
    assert evaluation.metrics["cohort_report"]["passed"] is False
    assert Path(evaluation.artifacts["cohort_report"]).exists()


def test_native_takeover_stays_shadow_when_cohort_evidence_is_not_ready(tmp_path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))
    bundles = _seed_toolsmith_history(services, [0.89, 0.90, 0.91])
    latest = bundles[-1]

    artifact = DistillationArtifactRecord(
        name="cohort-takeover-shadow",
        artifact_path=str(Path(project_root) / "runtime" / "artifacts" / "foundry" / "cohort-takeover-shadow.jsonl"),
        source_kinds=["curriculum", "trace"],
        sample_count=48,
        lineage="blended-derived",
        metadata={"teacher_evidence": latest},
    )
    benchmark = services.brain_foundry_benchmarks.evaluate(artifact=artifact)
    teacher_decision = next(item for item in services.brain_teachers.retirement_decisions() if item.teacher_id == "devstral-2")
    takeover = services.brain_foundry_retirement.takeover_candidate(
        teacher_decision,
        benchmark_summary=benchmark,
        teacher_evidence=latest,
    )

    assert benchmark["cohort_gate_ready"] is False
    assert benchmark["replacement_readiness"]["replacement_mode"] in {"hold", "shadow"}
    assert takeover.decision == "shadow"
    assert takeover.evidence["retirement_shadow_record"]["decision"] == "hold"


def test_ops_surfaces_expose_fleet_cohort_and_diff_controls(tmp_path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))
    bundles = _seed_toolsmith_history(services, [0.84, 0.86, 0.88, 0.90, 0.91])
    assert len(bundles) >= 2
    artifact = DistillationArtifactRecord(
        name="wrapper-cohort-visibility",
        artifact_path=str(Path(project_root) / "runtime" / "artifacts" / "foundry" / "wrapper-cohort-visibility.jsonl"),
        source_kinds=["curriculum", "trace"],
        sample_count=64,
        lineage="blended-derived",
        metadata={"teacher_evidence": bundles[-1]},
    )
    services.brain_foundry_benchmarks.evaluate(artifact=artifact)

    client = TestClient(create_app(str(project_root)))

    fleets = client.get(
        "/ops/brain/teachers/fleets",
        params={
            "fleet_id": "coding_agent_fleet",
            "subject": "toolsmith",
            "window_id": "medium",
            "teacher_pair_id": "devstral-2::qwen3-coder-next",
            "budget_class": "STANDARD",
            "output_form": "TOOL_CALL_STRICT_JSON",
            "risk_tier": "medium",
            "locality": "local_first",
            "hardware_class": "desktop_gpu",
        },
    )
    assert fleets.status_code == 200
    assert fleets.json()["items"][0]["fleet_id"] == "coding_agent_fleet"

    cohorts = client.get(
        "/ops/brain/teachers/cohorts",
        params={
            "fleet_id": "coding_agent_fleet",
            "subject": "toolsmith",
            "window_id": "medium",
            "teacher_pair_id": "devstral-2::qwen3-coder-next",
            "budget_class": "STANDARD",
            "output_form": "TOOL_CALL_STRICT_JSON",
            "risk_tier": "medium",
            "locality": "local_first",
            "hardware_class": "desktop_gpu",
        },
    )
    assert cohorts.status_code == 200
    assert cohorts.json()["items"][0]["fleet_id"] == "coding_agent_fleet"

    diff = client.get(
        "/ops/brain/teachers/evidence/diff",
        params={"left_bundle_id": bundles[0]["bundle_id"], "right_bundle_id": bundles[1]["bundle_id"]},
    )
    assert diff.status_code == 200
    assert "trend_refs" in diff.json()["diff"]

    compare = client.get(
        "/ops/brain/teachers/cohorts/compare",
        params={"fleet_id": "coding_agent_fleet", "subject": "toolsmith", "left_window": "short", "right_window": "long"},
    )
    assert compare.status_code == 200
    assert "stability_score_delta" in compare.json()["diff"]

    wrapper = client.get("/ops/brain/wrapper-surface")
    assert wrapper.status_code == 200
    visibility = wrapper.json()["teachers"]["visibility"]
    assert visibility["fleet_summaries"]
    assert visibility["cohort_scorecards"]
    assert visibility["replacement_readiness_reports"]
    assert visibility["inspection_controls"]["compare_refs"]["bundle_diff"] == "/ops/brain/teachers/evidence/diff"

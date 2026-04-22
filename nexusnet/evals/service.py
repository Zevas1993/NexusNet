from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.experiments import ExperimentService
from nexus.schemas import ExperimentRecord, new_id, utcnow
from nexus.storage import NexusStore

from .assimilation_artifacts import build_assimilation_artifact_catalog
from .assimilation_scorecards import build_assimilation_scorecards
from ..retrieval.rerank.reports import build_retrieval_rerank_review_report, render_retrieval_rerank_review_markdown


class ExternalBehaviorEvaluator:
    def __init__(
        self,
        *,
        store: NexusStore,
        experiments: ExperimentService,
        artifacts_dir: Path,
        teacher_evidence_service: Any | None = None,
        trend_gate: Any | None = None,
        cohort_gate: Any | None = None,
        retrieval_bench: Any | None = None,
        retrieval_operational_bench: Any | None = None,
        cost_energy_service: Any | None = None,
    ):
        self.store = store
        self.experiments = experiments
        self.artifacts_dir = artifacts_dir
        self.teacher_evidence_service = teacher_evidence_service
        self.trend_gate = trend_gate
        self.cohort_gate = cohort_gate
        self.retrieval_bench = retrieval_bench
        self.retrieval_operational_bench = retrieval_operational_bench
        self.cost_energy_service = cost_energy_service

    def run_recent(self, limit: int = 25) -> dict:
        traces = self.store.list_traces(limit=limit)
        report_id = new_id("eval")
        warning_count = sum(1 for trace in traces if trace.get("status") == "warning")
        error_count = sum(1 for trace in traces if trace.get("status") == "error")
        latencies = [
            trace.get("metrics", {}).get("brain_latency_ms", 0)
            for trace in traces
            if trace.get("metrics", {}).get("brain_latency_ms") is not None
        ]
        avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else 0.0
        metrics = {
            "trace_count": len(traces),
            "warning_count": warning_count,
            "error_count": error_count,
            "avg_brain_latency_ms": avg_latency,
        }
        decision = {
            "report_id": report_id,
            "decision": "shadow" if error_count or warning_count else "approved",
            "rationale": "External evaluator trace baseline; candidate-specific scenario and scorecard gates refine this result.",
            "generated_at": utcnow().isoformat(),
        }
        retrieval_report = self._retrieval_rerank_report(traces)
        if retrieval_report is not None:
            metrics["retrieval_rerank"] = retrieval_report["metrics"]["delta"]
        retrieval_scorecard = self._retrieval_rerank_scorecard()
        if retrieval_scorecard is not None:
            metrics["retrieval_rerank_scorecard"] = retrieval_scorecard["summary"]
        cost_energy = self.cost_energy_service.summarize(traces) if self.cost_energy_service is not None else None
        if cost_energy is not None:
            metrics["cost_energy"] = cost_energy["summary"]

        destination = self.artifacts_dir / "evals" / report_id
        destination.mkdir(parents=True, exist_ok=True)
        metrics_path = destination / "metrics.json"
        decision_path = destination / "decision.json"
        report_path = destination / "report.md"
        scenarios_path = destination / "scenarios.jsonl"
        retrieval_path = destination / "retrieval_rerank.json"
        retrieval_scorecard_path = destination / "retrieval_rerank_scorecard.json"
        cost_energy_path = destination / "cost_energy.json"

        metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        decision_path.write_text(json.dumps(decision, indent=2), encoding="utf-8")
        report_path.write_text(
            "\n".join(
                [
                    f"# External Evaluator Report {report_id}",
                    "",
                    "Status Label: STRONG ACCEPTED DIRECTION",
                    "",
                    f"- Traces reviewed: {metrics['trace_count']}",
                    f"- Warning traces: {metrics['warning_count']}",
                    f"- Error traces: {metrics['error_count']}",
                    f"- Average brain latency: {metrics['avg_brain_latency_ms']} ms",
                    *(
                        [
                            f"- Estimated energy: {metrics['cost_energy']['energy_wh']} Wh",
                            f"- Estimated FLOPs: {metrics['cost_energy']['estimated_flops']}",
                            f"- Estimated dollar cost: ${metrics['cost_energy']['dollar_cost']}",
                        ]
                        if cost_energy is not None
                        else []
                    ),
                    "",
                    "This remains an external-style evaluator and not a self-grading cognition shortcut.",
                ]
            ),
            encoding="utf-8",
        )
        with scenarios_path.open("w", encoding="utf-8") as handle:
            for trace in traces:
                handle.write(json.dumps(trace) + "\n")
        if retrieval_report is not None:
            retrieval_path.write_text(json.dumps(retrieval_report, indent=2), encoding="utf-8")
        if retrieval_scorecard is not None:
            retrieval_scorecard_path.write_text(json.dumps(retrieval_scorecard, indent=2), encoding="utf-8")
        if cost_energy is not None:
            cost_energy_path.write_text(json.dumps(cost_energy, indent=2), encoding="utf-8")

        record = ExperimentRecord(
            kind="external-eval",
            name=f"external-eval::{report_id}",
            status=decision["decision"],
            lineage={"report_id": report_id, "status_label": "STRONG ACCEPTED DIRECTION"},
            metrics=metrics,
            artifacts=[str(metrics_path), str(decision_path), str(report_path), str(scenarios_path)]
            + ([str(retrieval_path)] if retrieval_report is not None else [])
            + ([str(retrieval_scorecard_path)] if retrieval_scorecard is not None else [])
            + ([str(cost_energy_path)] if cost_energy is not None else []),
        )
        self.experiments.record(record)

        artifacts = {
            "metrics": str(metrics_path),
            "decision": str(decision_path),
            "report": str(report_path),
            "scenarios": str(scenarios_path),
        }
        if retrieval_report is not None:
            artifacts["retrieval_rerank"] = str(retrieval_path)
        if retrieval_scorecard is not None:
            artifacts["retrieval_rerank_scorecard"] = str(retrieval_scorecard_path)
        if cost_energy is not None:
            artifacts["cost_energy"] = str(cost_energy_path)

        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "report_id": report_id,
            "metrics": metrics,
            "decision": decision,
            "artifacts": artifacts,
        }

    def gate_candidate(self, *, subject: str, metrics: dict[str, float] | None = None, limit: int = 25) -> dict:
        return self.evaluate_candidate(
            subject=subject,
            baseline_reference="shadow-baseline",
            challenger_reference="shadow-challenger",
            scenario_set=[],
            candidate_metrics=metrics or {},
            candidate_kind="native-takeover",
            candidate_traceability={},
            limit=limit,
        )

    def evaluate_candidate(
        self,
        *,
        subject: str,
        baseline_reference: str,
        challenger_reference: str,
        scenario_set: list[str],
        candidate_metrics: dict[str, float] | None = None,
        candidate_kind: str | None = None,
        candidate_traceability: dict | None = None,
        limit: int = 25,
    ) -> dict:
        report = self.run_recent(limit=limit)
        candidate_traceability = candidate_traceability or {}
        teacher_evidence = self._resolve_teacher_evidence(candidate_traceability)
        scenario_results = self._evaluate_scenarios(
            scenario_set=scenario_set,
            candidate_kind=candidate_kind,
            teacher_evidence=teacher_evidence,
            candidate_traceability=candidate_traceability,
        )
        trend_report = (
            self.trend_gate.evaluate(
                candidate_kind=candidate_kind,
                candidate_traceability=candidate_traceability,
                teacher_evidence=teacher_evidence,
            )
            if self.trend_gate is not None
            else {
                "applicable": False,
                "passed": True,
                "rationale": "No trend gate applied.",
                "teacher_trends": [],
                "takeover_trend": None,
            }
        )
        cohort_report = (
            self.cohort_gate.evaluate(
                candidate_kind=candidate_kind,
                candidate_traceability=candidate_traceability,
                teacher_evidence=teacher_evidence,
                trend_report=trend_report,
            )
            if self.cohort_gate is not None
            else {
                "applicable": False,
                "passed": True,
                "rationale": "No cohort gate applied.",
                "fleet_summaries": [],
                "cohort_scorecards": [],
                "replacement_readiness": None,
            }
        )
        scenario_failures = [result for result in scenario_results if not result["passed"] and not result.get("advisory", False)]
        scorecard_payload = self._teacher_scorecard_payload(teacher_evidence)
        disagreement_metrics = self._disagreement_metrics_payload(teacher_evidence)
        takeover_payload = self._takeover_payload(teacher_evidence, candidate_traceability, trend_report)
        scorecard_failures = scorecard_payload["summary"]["failing_scorecard_count"]
        takeover_failed = candidate_kind == "native-takeover" and not takeover_payload["passed"]
        trend_failed = trend_report["applicable"] and not trend_report["passed"]
        cohort_failed = cohort_report["applicable"] and not cohort_report["passed"]
        retrieval_rerank_evidence = dict(candidate_traceability.get("retrieval_rerank_evidence", {}))
        assimilation_artifacts = build_assimilation_artifact_catalog(
            retrieval_rerank_evidence=retrieval_rerank_evidence,
            retrieval_rerank_review=dict(candidate_traceability.get("retrieval_rerank_review", {})),
            gateway_provenance=dict(candidate_traceability.get("gateway_provenance", {})),
            edge_vision_benchmark=dict(candidate_traceability.get("edge_vision_benchmark", {})),
            aitune_validation=dict(candidate_traceability.get("aitune_validation", {})),
            triattention_comparison=dict(candidate_traceability.get("triattention_comparison", {})),
        )
        assimilation_scorecards = build_assimilation_scorecards(
            retrieval_rerank_evidence=retrieval_rerank_evidence,
            retrieval_rerank_review=dict(candidate_traceability.get("retrieval_rerank_review", {})),
            aitune_validation=dict(candidate_traceability.get("aitune_validation", {})),
            triattention_comparison=dict(candidate_traceability.get("triattention_comparison", {})),
        )
        retrieval_rerank_failed = (
            candidate_kind == "retrieval-policy"
            and (
                not retrieval_rerank_evidence.get("bundle_id")
                or not retrieval_rerank_evidence.get("scorecard_passed")
                or not retrieval_rerank_evidence.get("reranker_provider")
            )
        )

        report["candidate_subject"] = subject
        report["candidate_metrics"] = candidate_metrics or {}
        report["baseline_reference"] = baseline_reference
        report["challenger_reference"] = challenger_reference
        report["scenario_set"] = scenario_set
        report["scenario_results"] = scenario_results
        report["candidate_kind"] = candidate_kind
        report["candidate_traceability"] = candidate_traceability
        report["metrics"]["scenario_results"] = scenario_results
        report["metrics"]["teacher_evidence_present"] = bool(teacher_evidence)
        report["metrics"]["scenario_failure_count"] = len(scenario_failures)
        report["metrics"]["scorecard_summary"] = scorecard_payload["summary"]
        report["metrics"]["disagreement_metrics"] = disagreement_metrics
        report["metrics"]["takeover_readiness"] = takeover_payload
        report["metrics"]["trend_report"] = trend_report
        report["metrics"]["cohort_report"] = cohort_report
        report["metrics"]["assimilation_artifacts"] = assimilation_artifacts
        report["metrics"]["assimilation_scorecards"] = assimilation_scorecards

        decision = dict(report["decision"])
        if scenario_failures or scorecard_failures or takeover_failed or trend_failed or cohort_failed or retrieval_rerank_failed:
            decision["decision"] = "rejected"
        elif decision["decision"] == "shadow":
            decision["decision"] = "shadow"
        else:
            decision["decision"] = "approved"
        decision["rationale"] = (
            "Candidate-specific external evaluator review over recent traces, scenario families, teacher scorecards, disagreement metrics, and takeover readiness."
        )
        report["decision"] = decision

        report_dir = Path(report["artifacts"]["report"]).parent
        scorecard_path = report_dir / "scorecard.json"
        disagreement_path = report_dir / "disagreement_metrics.json"
        takeover_path = report_dir / "takeover_readiness.json"
        trend_path = report_dir / "trend_report.json"
        cohort_path = report_dir / "cohort_report.json"
        teacher_report_path = report_dir / "teacher_eval_report.md"
        retrieval_rerank_path = report_dir / "retrieval_rerank_evidence.json"
        retrieval_rerank_review_path = report_dir / "retrieval_rerank_review.json"
        retrieval_rerank_review_md_path = report_dir / "retrieval_rerank_review.md"
        assimilation_artifacts_path = report_dir / "assimilation_artifacts.json"
        assimilation_scorecards_path = report_dir / "assimilation_scorecards.json"
        retrieval_rerank_review = build_retrieval_rerank_review_report(
            bundle=retrieval_rerank_evidence,
            evaluation_artifact_refs={
                "eval_metrics": str(Path(report["artifacts"]["metrics"])),
                "eval_report": str(Path(report["artifacts"]["report"])),
            },
        )

        scorecard_path.write_text(json.dumps(scorecard_payload, indent=2), encoding="utf-8")
        disagreement_path.write_text(json.dumps(disagreement_metrics, indent=2), encoding="utf-8")
        takeover_path.write_text(json.dumps(takeover_payload, indent=2), encoding="utf-8")
        trend_path.write_text(json.dumps(trend_report, indent=2), encoding="utf-8")
        cohort_path.write_text(json.dumps(cohort_report, indent=2), encoding="utf-8")
        retrieval_rerank_path.write_text(json.dumps(retrieval_rerank_evidence, indent=2), encoding="utf-8")
        retrieval_rerank_review_path.write_text(json.dumps(retrieval_rerank_review, indent=2), encoding="utf-8")
        retrieval_rerank_review_md_path.write_text(render_retrieval_rerank_review_markdown(retrieval_rerank_review), encoding="utf-8")
        assimilation_artifacts_path.write_text(json.dumps(assimilation_artifacts, indent=2), encoding="utf-8")
        assimilation_scorecards_path.write_text(json.dumps(assimilation_scorecards, indent=2), encoding="utf-8")
        teacher_report_path.write_text(
            "\n".join(
                [
                    f"# Teacher Evaluation Report {report['report_id']}",
                    "",
                    f"- Subject: {subject}",
                    f"- Candidate kind: {candidate_kind or 'unspecified'}",
                    f"- Teacher evidence bundle: {teacher_evidence.get('bundle_id')}",
                    f"- Scorecards passing: {scorecard_payload['summary']['passing_scorecard_count']}/{scorecard_payload['summary']['scorecard_count']}",
                    f"- Scenario failures: {len(scenario_failures)}",
                    f"- Takeover gate passed: {takeover_payload['passed']}",
                    f"- Trend gate passed: {trend_report['passed']}",
                    f"- Cohort gate passed: {cohort_report['passed']}",
                    f"- Retrieval rerank evidence passed: {not retrieval_rerank_failed}",
                    "",
                    "## Scenario Results",
                    *[
                        f"- {item['scenario_id']}: {'PASS' if item['passed'] else 'FAIL'} - {item['detail']}"
                        for item in scenario_results
                    ],
                ]
            ),
            encoding="utf-8",
        )
        report["artifacts"].update(
            {
                "scorecard": str(scorecard_path),
                "disagreement_metrics": str(disagreement_path),
                "takeover_readiness": str(takeover_path),
                "trend_report": str(trend_path),
                "cohort_report": str(cohort_path),
                "teacher_eval_report": str(teacher_report_path),
                "retrieval_rerank_evidence": str(retrieval_rerank_path),
                "retrieval_rerank_review": str(retrieval_rerank_review_path),
                "retrieval_rerank_review_md": str(retrieval_rerank_review_md_path),
                "assimilation_artifacts": str(assimilation_artifacts_path),
                "assimilation_scorecards": str(assimilation_scorecards_path),
            }
        )
        Path(report["artifacts"]["metrics"]).write_text(json.dumps(report["metrics"], indent=2), encoding="utf-8")
        Path(report["artifacts"]["decision"]).write_text(json.dumps(report["decision"], indent=2), encoding="utf-8")

        report_path = Path(report["artifacts"]["report"])
        report_path.write_text(
            "\n".join(
                [
                    report_path.read_text(encoding="utf-8"),
                    "",
                    "## Candidate Gate",
                    "",
                    f"- Subject: {subject}",
                    f"- Candidate kind: {candidate_kind or 'unspecified'}",
                    f"- Baseline: {baseline_reference}",
                    f"- Challenger: {challenger_reference}",
                    f"- Scenario count: {len(scenario_set)}",
                    f"- Teacher-aware checks failed: {len(scenario_failures)}",
                    f"- Scorecard failures: {scorecard_failures}",
                    f"- Takeover gate passed: {takeover_payload['passed']}",
                    f"- Trend gate passed: {trend_report['passed']}",
                    f"- Cohort gate passed: {cohort_report['passed']}",
                    f"- Retrieval rerank evidence passed: {not retrieval_rerank_failed}",
                    "",
                    "### Scenario Results",
                    *[
                        f"- {item['scenario_id']}: {'PASS' if item['passed'] else 'FAIL'} - {item['detail']}"
                        for item in scenario_results
                    ],
                ]
            ),
            encoding="utf-8",
        )
        scenarios_path = Path(report["artifacts"]["scenarios"])
        with scenarios_path.open("a", encoding="utf-8") as handle:
            for result in scenario_results:
                handle.write(json.dumps({"scenario_result": result, "candidate_subject": subject}) + "\n")

        return report

    def evaluate_teacher_bundle(
        self,
        *,
        subject: str,
        baseline_reference: str,
        challenger_reference: str,
        teacher_evidence: dict,
        scenario_set: list[str],
        limit: int = 25,
    ) -> dict:
        candidate_metrics = {
            "dependency_ratio": teacher_evidence.get("dependency_ratio") or 0.0,
            "native_generation": teacher_evidence.get("native_generation") or 0.0,
            "takeover_readiness": teacher_evidence.get("takeover_readiness") or 0.0,
            "teacher_disagreement_delta": teacher_evidence.get("teacher_disagreement_delta") or 0.0,
        }
        return self.evaluate_candidate(
            subject=subject,
            baseline_reference=baseline_reference,
            challenger_reference=challenger_reference,
            scenario_set=scenario_set,
            candidate_metrics=candidate_metrics,
            candidate_kind="native-takeover",
            candidate_traceability={
                "teacher_evidence": teacher_evidence,
                "teacher_evidence_bundle_id": teacher_evidence.get("bundle_id"),
            },
            limit=limit,
        )

    def _resolve_teacher_evidence(self, candidate_traceability: dict[str, Any]) -> dict[str, Any]:
        teacher_evidence = dict(candidate_traceability.get("teacher_evidence", {}))
        bundle_id = candidate_traceability.get("teacher_evidence_bundle_id") or teacher_evidence.get("bundle_id")
        if bundle_id and self.teacher_evidence_service is not None:
            try:
                teacher_evidence = self.teacher_evidence_service.bundle_payload(bundle_id)
            except Exception:
                pass
        return teacher_evidence

    def _retrieval_rerank_report(self, traces: list[dict[str, Any]]) -> dict[str, Any] | None:
        if self.retrieval_bench is None:
            return None
        for trace in traces:
            prompt = (trace.get("request") or {}).get("prompt")
            if prompt:
                return self.retrieval_bench.run(
                    query=prompt,
                    session_id=trace.get("session_id"),
                    top_k=6,
                    policy_mode=trace.get("retrieval_policy") or "lexical+graph-memory-temporal-rerank",
                )
        return None

    def _retrieval_rerank_scorecard(self) -> dict[str, Any] | None:
        if self.retrieval_operational_bench is None:
            return None
        report = self.retrieval_operational_bench.run()
        if not report.get("scorecard"):
            return None
        return report

    def _evaluate_scenarios(
        self,
        *,
        scenario_set: list[str],
        candidate_kind: str | None,
        teacher_evidence: dict,
        candidate_traceability: dict,
    ) -> list[dict]:
        scenarios = list(scenario_set)
        if teacher_evidence:
            scenarios.extend(
                [
                    "primary-vs-secondary-disagreement",
                    "critique-arbitration-validation",
                    "lfm2-bounded-lane-enforcement",
                    "teacher-backed-output-quality",
                    "dream-derived-trace-contamination",
                ]
            )
        if candidate_kind == "native-takeover":
            scenarios.append("native-takeover-vs-teacher-fallback")
        if candidate_kind == "retrieval-policy" or candidate_traceability.get("retrieval_rerank_evidence"):
            scenarios.append("retrieval-rerank-scorecard-validation")
        seen: set[str] = set()
        results: list[dict] = []
        for scenario_id in scenarios:
            if scenario_id in seen:
                continue
            seen.add(scenario_id)
            results.append(
                self._scenario_result(
                    scenario_id=scenario_id,
                    teacher_evidence=teacher_evidence,
                    candidate_traceability=candidate_traceability,
                )
            )
        return results

    def _scenario_result(self, *, scenario_id: str, teacher_evidence: dict, candidate_traceability: dict) -> dict:
        scorecards = teacher_evidence.get("scorecards", [])
        if scenario_id == "primary-vs-secondary-disagreement":
            selected_roles = teacher_evidence.get("selected_teacher_roles", {})
            artifacts = teacher_evidence.get("disagreement_artifacts", [])
            passed = bool(selected_roles.get("primary")) and (bool(selected_roles.get("secondary")) or bool(artifacts))
            detail = "Teacher evidence preserves both primary and secondary comparison lanes." if passed else "Missing primary/secondary disagreement evidence."
        elif scenario_id == "critique-arbitration-validation":
            passed = bool(teacher_evidence.get("selected_teacher_roles", {}).get("critique")) and bool(teacher_evidence.get("arbitration_result"))
            detail = "Critique Expert arbitration is recorded." if passed else "Critique arbitration is missing from teacher evidence."
        elif scenario_id == "lfm2-bounded-lane-enforcement":
            selected_roles = teacher_evidence.get("selected_teacher_roles", {})
            lfm2_present = bool(selected_roles.get("efficiency"))
            passed = bool(teacher_evidence.get("lfm2_bounded_ok", True)) if lfm2_present else True
            detail = "LFM2 remains bounded to allowed lanes." if passed else "LFM2 appears outside bounded lanes."
        elif scenario_id == "teacher-backed-output-quality":
            passed = bool(scorecards) and all(item.get("passed") for item in scorecards)
            detail = "Teacher-backed scorecards all pass thresholds." if passed else "One or more teacher-backed scorecards failed threshold checks."
        elif scenario_id == "native-takeover-vs-teacher-fallback":
            takeover_scorecard = candidate_traceability.get("takeover_scorecard") or teacher_evidence.get("takeover_scorecard") or {}
            passed = bool(takeover_scorecard.get("passed")) and bool(teacher_evidence.get("takeover_rollbackability"))
            detail = "Native takeover candidate clears teacher-fallback comparison and rollbackability." if passed else "Native takeover evidence or rollbackability is incomplete."
        elif scenario_id == "dream-derived-trace-contamination":
            if not teacher_evidence.get("dream_derived"):
                passed = True
                detail = "No dream-derived contamination risk in this candidate."
            else:
                passed = bool(teacher_evidence.get("arbitration_result")) and bool(teacher_evidence.get("selected_teacher_roles", {}).get("critique"))
                detail = "Dream-derived traces remain critique-audited." if passed else "Dream-derived traces lack critique containment."
        elif scenario_id == "retrieval-rerank-scorecard-validation":
            rerank_evidence = candidate_traceability.get("retrieval_rerank_evidence", {})
            passed = bool(rerank_evidence.get("bundle_id")) and bool(rerank_evidence.get("scorecard_passed")) and bool(rerank_evidence.get("reranker_provider"))
            detail = "Retrieval policy candidate carries benchmarked rerank evidence bundle." if passed else "Retrieval policy candidate is missing rerank evidence, passing scorecard, or reranker provider."
        else:
            passed = True
            detail = f"Scenario '{scenario_id}' recorded for manual follow-up."
        return {
            "scenario_id": scenario_id,
            "passed": passed,
            "detail": detail,
            "advisory": scenario_id not in {
                "primary-vs-secondary-disagreement",
                "critique-arbitration-validation",
                "lfm2-bounded-lane-enforcement",
                "teacher-backed-output-quality",
                "native-takeover-vs-teacher-fallback",
                "dream-derived-trace-contamination",
                "retrieval-rerank-scorecard-validation",
            },
            "teacher_evidence_present": bool(teacher_evidence),
            "traceability_keys": sorted(candidate_traceability.keys()),
        }

    def _teacher_scorecard_payload(self, teacher_evidence: dict[str, Any]) -> dict[str, Any]:
        scorecards = list(teacher_evidence.get("scorecards", []))
        failing = [item for item in scorecards if not item.get("passed")]
        avg_weighted = round(
            sum(float(item.get("weighted_score", 0.0)) for item in scorecards) / len(scorecards),
            3,
        ) if scorecards else 0.0
        return {
            "bundle_id": teacher_evidence.get("bundle_id"),
            "threshold_set_id": teacher_evidence.get("threshold_set_id"),
            "scorecards": scorecards,
            "summary": {
                "scorecard_count": len(scorecards),
                "passing_scorecard_count": len(scorecards) - len(failing),
                "failing_scorecard_count": len(failing),
                "avg_weighted_score": avg_weighted,
            },
        }

    def _disagreement_metrics_payload(self, teacher_evidence: dict[str, Any]) -> dict[str, Any]:
        artifacts = list(teacher_evidence.get("disagreement_artifacts", []))
        severities = [
            float(item.get("disagreement_delta", item.get("disagreement_severity", 0.0)) or 0.0)
            for item in artifacts
        ]
        return {
            "artifact_count": len(artifacts),
            "avg_disagreement_severity": round(sum(severities) / len(severities), 3) if severities else 0.0,
            "critique_present": bool(teacher_evidence.get("selected_teacher_roles", {}).get("critique")),
            "lfm2_bounded_ok": bool(teacher_evidence.get("lfm2_bounded_ok", True)),
        }

    def _takeover_payload(self, teacher_evidence: dict[str, Any], candidate_traceability: dict[str, Any], trend_report: dict[str, Any]) -> dict[str, Any]:
        takeover_scorecard = candidate_traceability.get("takeover_scorecard") or teacher_evidence.get("takeover_scorecard") or {}
        takeover_trend = trend_report.get("takeover_trend") or {}
        return {
            "takeover_readiness": teacher_evidence.get("takeover_readiness"),
            "teacher_replacement_candidate": teacher_evidence.get("teacher_replacement_candidate"),
            "takeover_rollbackability": teacher_evidence.get("takeover_rollbackability"),
            "scorecard_id": takeover_scorecard.get("scorecard_id"),
            "takeover_trend_report_id": takeover_trend.get("trend_id"),
            "trend_ready": bool(takeover_trend.get("ready", True)),
            "passed": bool(takeover_scorecard.get("passed", teacher_evidence.get("takeover_rollbackability"))) and bool(takeover_trend.get("ready", True)),
        }

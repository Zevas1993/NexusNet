from __future__ import annotations

import re
from typing import Any

from nexus.schemas import utcnow


def _stable_review_id(bundle: dict[str, Any]) -> str:
    existing = bundle.get("review_report_id")
    if existing:
        return str(existing)
    bundle_id = str(bundle.get("bundle_id") or "unbound")
    safe = re.sub(r"[^a-zA-Z0-9._-]+", "-", bundle_id).strip("-").lower() or "unbound"
    return f"retrievalreview-{safe}"


def _candidate_preview(items: list[dict[str, Any]], *, limit: int = 3) -> list[dict[str, Any]]:
    preview: list[dict[str, Any]] = []
    for item in items[:limit]:
        preview.append(
            {
                "chunk_id": item.get("chunk_id"),
                "source": item.get("source"),
                "score": item.get("score"),
                "rerank_score": item.get("rerank_score"),
                "candidate_sources": item.get("candidate_sources", []),
            }
        )
    return preview


def _candidate_shift_summary(before: list[dict[str, Any]], after: list[dict[str, Any]]) -> dict[str, Any]:
    before_positions = {item.get("chunk_id"): index for index, item in enumerate(before) if item.get("chunk_id")}
    shifts = []
    for after_index, item in enumerate(after):
        chunk_id = item.get("chunk_id")
        if chunk_id not in before_positions:
            continue
        before_index = before_positions[chunk_id]
        delta = before_index - after_index
        if delta == 0:
            continue
        shifts.append(
            {
                "chunk_id": chunk_id,
                "before_index": before_index,
                "after_index": after_index,
                "rank_delta": delta,
            }
        )
    shifts.sort(key=lambda item: abs(item["rank_delta"]), reverse=True)
    return {
        "changed_count": len(shifts),
        "top_shift": shifts[0] if shifts else None,
        "shifts": shifts[:8],
    }


def _delta_rows(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"label": "rerank_score", "value": bundle.get("rerank_score", 0.0), "unit": "score"},
        {"label": "latency_delta_ms", "value": bundle.get("latency_delta_ms", 0.0), "unit": "ms"},
        {"label": "relevance_delta", "value": bundle.get("relevance_delta", 0.0), "unit": "score"},
        {"label": "groundedness_delta", "value": bundle.get("groundedness_delta", 0.0), "unit": "score"},
        {"label": "provenance_delta", "value": bundle.get("provenance_delta", 0.0), "unit": "score"},
    ]


def _threshold_summary(bundle: dict[str, Any], *, passed: bool) -> dict[str, Any]:
    threshold_report = dict(bundle.get("threshold_report") or {})
    return {
        "threshold_set_id": bundle.get("threshold_set_id"),
        "decision": threshold_report.get("decision") or ("pass" if passed else "fail"),
        "passing_checks": list(threshold_report.get("passing_checks", [])),
        "failing_checks": list(threshold_report.get("failing_checks", [])),
    }


def _evaluator_artifact_summary(refs: dict[str, str]) -> dict[str, Any]:
    return {
        "artifact_count": len(refs),
        "artifact_ids": sorted(refs.keys()),
    }


def build_retrieval_rerank_review_report(
    *,
    bundle: dict[str, Any],
    evaluation_artifact_refs: dict[str, str] | None = None,
) -> dict[str, Any]:
    passed = bool(bundle.get("scorecard_passed", False))
    verdict = "promotion-ready" if passed else "needs-review"
    report_id = _stable_review_id(bundle)
    candidate_shift_summary = _candidate_shift_summary(bundle.get("stage_1_candidates", []), bundle.get("stage_2_candidates", []))
    evaluator_artifact_refs = dict(evaluation_artifact_refs or bundle.get("evaluator_artifact_refs", {}))
    review_badges = {
        "provider": bundle.get("reranker_provider") or "unbound",
        "benchmark_family_id": bundle.get("benchmark_family_id"),
        "threshold_set_id": bundle.get("threshold_set_id"),
        "scorecard_id": bundle.get("scorecard_id"),
        "passed": passed,
    }
    operator_summary = [
        f"policy={bundle.get('policy_mode')}",
        f"provider={bundle.get('reranker_provider') or 'unbound'}",
        f"relevance={bundle.get('relevance_delta', 0.0):.4f}",
        f"groundedness={bundle.get('groundedness_delta', 0.0):.4f}",
        f"provenance={bundle.get('provenance_delta', 0.0):.4f}",
        f"latency_ms={bundle.get('latency_delta_ms', 0.0):.3f}",
    ]
    human_summary = (
        f"{verdict}: provider={review_badges['provider']} "
        f"relevance={bundle.get('relevance_delta', 0.0):.4f} "
        f"groundedness={bundle.get('groundedness_delta', 0.0):.4f} "
        f"latency_ms={bundle.get('latency_delta_ms', 0.0):.3f} "
        f"candidate_shifts={candidate_shift_summary.get('changed_count', 0)}"
    )
    return {
        "report_id": report_id,
        "status_label": "STRONG ACCEPTED DIRECTION",
        "created_at": utcnow().isoformat(),
        "bundle_id": bundle.get("bundle_id"),
        "subject_id": bundle.get("subject_id"),
        "policy_mode": bundle.get("policy_mode"),
        "verdict": verdict,
        "headline": f"Retrieval rerank review for {bundle.get('subject_id')}",
        "benchmark_family_id": bundle.get("benchmark_family_id"),
        "threshold_set_id": bundle.get("threshold_set_id"),
        "scorecard_id": bundle.get("scorecard_id"),
        "scorecard_passed": passed,
        "stage_top_k": {
            "before_rerank": bundle.get("stage_1_top_k"),
            "after_rerank": bundle.get("stage_2_top_k_after_rerank"),
        },
        "delta_summary": {
            "rerank_score": bundle.get("rerank_score", 0.0),
            "latency_delta_ms": bundle.get("latency_delta_ms", 0.0),
            "relevance_delta": bundle.get("relevance_delta", 0.0),
            "groundedness_delta": bundle.get("groundedness_delta", 0.0),
            "provenance_delta": bundle.get("provenance_delta", 0.0),
        },
        "human_summary": human_summary,
        "review_badges": review_badges,
        "delta_rows": _delta_rows(bundle),
        "candidate_shift_summary": candidate_shift_summary,
        "top_shift_preview": candidate_shift_summary.get("top_shift"),
        "candidate_source_counts": dict(bundle.get("candidate_source_counts", {})),
        "threshold_summary": _threshold_summary(bundle, passed=passed),
        "top_candidates_before": _candidate_preview(bundle.get("stage_1_candidates", [])),
        "top_candidates_after": _candidate_preview(bundle.get("stage_2_candidates", [])),
        "operator_summary": operator_summary,
        "evaluator_artifact_refs": evaluator_artifact_refs,
        "evaluator_artifact_summary": _evaluator_artifact_summary(evaluator_artifact_refs),
    }


def render_retrieval_rerank_review_markdown(report: dict[str, Any]) -> str:
    delta = report.get("delta_summary", {})
    before = report.get("top_candidates_before", [])
    after = report.get("top_candidates_after", [])
    return "\n".join(
        [
            f"# Retrieval Rerank Review {report.get('report_id')}",
            "",
            f"- Subject: {report.get('subject_id')}",
            f"- Policy mode: {report.get('policy_mode')}",
            f"- Verdict: {report.get('verdict')}",
            f"- Scorecard: {report.get('scorecard_id')} (passed={report.get('scorecard_passed')})",
            f"- Benchmark family: {report.get('benchmark_family_id')}",
            f"- Threshold set: {report.get('threshold_set_id')}",
            f"- Stage-1 top-k: {(report.get('stage_top_k') or {}).get('before_rerank')}",
            f"- Stage-2 top-k: {(report.get('stage_top_k') or {}).get('after_rerank')}",
            f"- Human summary: {report.get('human_summary')}",
            f"- Review badges: provider={((report.get('review_badges') or {}).get('provider'))} | scorecard={((report.get('review_badges') or {}).get('scorecard_id'))} | passed={((report.get('review_badges') or {}).get('passed'))}",
            f"- Rerank score: {delta.get('rerank_score', 0.0)}",
            f"- Latency delta ms: {delta.get('latency_delta_ms', 0.0)}",
            f"- Relevance delta: {delta.get('relevance_delta', 0.0)}",
            f"- Groundedness delta: {delta.get('groundedness_delta', 0.0)}",
            f"- Provenance delta: {delta.get('provenance_delta', 0.0)}",
            f"- Candidate shifts: {(report.get('candidate_shift_summary') or {}).get('changed_count', 0)}",
            f"- Evaluator artifacts: {((report.get('evaluator_artifact_summary') or {}).get('artifact_count', 0))}",
            "",
            "## Threshold Summary",
            f"- Decision: {(report.get('threshold_summary') or {}).get('decision')}",
            f"- Passing checks: {', '.join((report.get('threshold_summary') or {}).get('passing_checks', [])) or 'none'}",
            f"- Failing checks: {', '.join((report.get('threshold_summary') or {}).get('failing_checks', [])) or 'none'}",
            "",
            "## Candidate Shift Summary",
            f"- Top shift: {((report.get('top_shift_preview') or {}).get('chunk_id')) or 'none'}",
            f"- Rank delta: {((report.get('top_shift_preview') or {}).get('rank_delta')) if report.get('top_shift_preview') else 'none'}",
            "",
            "## Stage-1 Candidates",
            *[
                f"- {item.get('chunk_id')} | {item.get('source')} | score={item.get('score')} | sources={','.join(item.get('candidate_sources', [])) or 'none'}"
                for item in before
            ],
            "",
            "## Stage-2 Candidates",
            *[
                f"- {item.get('chunk_id')} | {item.get('source')} | score={item.get('score')} | rerank={item.get('rerank_score')}"
                for item in after
            ],
            "",
            "## Operator Summary",
            *[f"- {line}" for line in report.get("operator_summary", [])],
            "",
            "## Evaluator Artifacts",
            *[
                f"- {key}: {value}"
                for key, value in (report.get("evaluator_artifact_refs") or {}).items()
            ],
        ]
    )

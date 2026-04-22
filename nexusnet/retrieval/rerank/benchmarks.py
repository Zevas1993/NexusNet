from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import RetrievalRequest, new_id, utcnow

from .corpora import ensure_corpora_ingested, flatten_rerank_cases, load_rerank_corpora
from .score_fusion import average_groundedness, average_relevance, average_provenance
from .scorecards import build_rerank_scorecard
from .thresholds import evaluate_rerank_thresholds, load_rerank_thresholds


def _hit_excerpt(hit: dict[str, Any] | Any) -> dict[str, Any]:
    if isinstance(hit, dict):
        metadata = hit.get("metadata", {})
        chunk_id = hit.get("chunk_id")
        source = hit.get("source")
        score = hit.get("score", 0.0)
    else:
        metadata = getattr(hit, "metadata", {})
        chunk_id = getattr(hit, "chunk_id", None)
        source = getattr(hit, "source", None)
        score = getattr(hit, "score", 0.0)
    return {
        "chunk_id": chunk_id,
        "source": source,
        "score": float(score or 0.0),
        "rerank_score": metadata.get("rerank_score"),
        "candidate_sources": metadata.get("candidate_sources", []),
        "retrieval_stage": metadata.get("retrieval_stage"),
    }


class RetrievalRerankOperationalBenchmarkSuite:
    def __init__(self, *, artifacts_dir: Path, retrieval_service: Any, retrieval_config: dict[str, Any]):
        self.artifacts_dir = artifacts_dir
        self.retrieval_service = retrieval_service
        self.retrieval_config = retrieval_config

    def run(self, *, session_id: str | None = None, top_k: int | None = None, policy_mode: str | None = None) -> dict[str, Any]:
        corpora = load_rerank_corpora(self.retrieval_config)
        ensure_corpora_ingested(self.retrieval_service, corpora)
        cases = flatten_rerank_cases(corpora)
        if not cases:
            return {
                "status_label": "IMPLEMENTATION BRANCH",
                "report_id": None,
                "summary": {"case_count": 0, "reason": "No rerank operational corpora configured."},
                "artifacts": {},
            }

        top_k = int(top_k or ((self.retrieval_config.get("operationalization") or {}).get("default_top_k", 6)))
        policy_mode = policy_mode or str(self.retrieval_config.get("policy_mode_default", "lexical+graph-memory-temporal-rerank"))
        case_results: list[dict[str, Any]] = []
        for case in cases:
            request = RetrievalRequest(query=case["query"], top_k=top_k, session_id=session_id)
            before = self.retrieval_service.query_with_policy(request, policy_mode=policy_mode, rerank_enabled=False)
            after = self.retrieval_service.query_with_policy(request, policy_mode=policy_mode, rerank_enabled=True)
            before_hits = before.get("hits", [])
            after_hits = after.get("hits", [])
            expected_sources = {value.lower() for value in case.get("expected_sources", [])}
            expected_terms = {value.lower() for value in case.get("expected_terms", [])}
            after_sources = {str(getattr(hit, "source", "")).lower() for hit in after_hits}
            after_text = " ".join(str(getattr(hit, "content", "")).lower() for hit in after_hits)
            source_pass = not expected_sources or bool(expected_sources & after_sources)
            term_pass = not expected_terms or all(term in after_text for term in expected_terms)
            quality = after.get("reranker") or {}
            case_results.append(
                {
                    "case_id": case["case_id"],
                    "corpus_id": case["corpus_id"],
                    "family_id": case["family_id"],
                    "family_label": case.get("family_label"),
                    "query": case["query"],
                    "passed": source_pass and term_pass,
                    "expected_sources": sorted(expected_sources),
                    "expected_terms": sorted(expected_terms),
                    "top_k_before_rerank": before.get("top_k_before_rerank", len(before_hits)),
                    "top_k_after_rerank": after.get("top_k_after_rerank", len(after_hits)),
                    "reranker_provider": quality.get("provider"),
                    "latency_delta_ms": quality.get("latency_delta_ms", 0),
                    "relevance_delta": quality.get("relevance_delta", 0.0),
                    "groundedness_delta": quality.get("groundedness_delta", 0.0),
                    "provenance_delta": quality.get("provenance_delta", 0.0),
                    "candidate_source_counts": after.get("candidate_source_counts", {}),
                    "before_hits": [_hit_excerpt(hit) for hit in before_hits],
                    "after_hits": [_hit_excerpt(hit) for hit in after_hits],
                    "average_relevance_before": average_relevance(before_hits),
                    "average_relevance_after": average_relevance(after_hits),
                    "average_groundedness_before": average_groundedness(before_hits),
                    "average_groundedness_after": average_groundedness(after_hits),
                    "average_provenance_before": average_provenance(before_hits),
                    "average_provenance_after": average_provenance(after_hits),
                }
            )

        provider_hits = sum(1 for item in case_results if item.get("reranker_provider"))
        metrics = {
            "case_count": len(case_results),
            "pass_rate": round(sum(1 for item in case_results if item["passed"]) / max(len(case_results), 1), 4),
            "avg_latency_delta_ms": round(sum(float(item["latency_delta_ms"]) for item in case_results) / max(len(case_results), 1), 3),
            "avg_relevance_delta": round(sum(float(item["relevance_delta"]) for item in case_results) / max(len(case_results), 1), 4),
            "avg_groundedness_delta": round(sum(float(item["groundedness_delta"]) for item in case_results) / max(len(case_results), 1), 4),
            "avg_provenance_delta": round(sum(float(item["provenance_delta"]) for item in case_results) / max(len(case_results), 1), 4),
            "provider_coverage": round(provider_hits / max(len(case_results), 1), 4),
            "policy_mode": policy_mode,
            "top_k": top_k,
            "generated_at": utcnow().isoformat(),
        }
        thresholds = load_rerank_thresholds(self.retrieval_config)
        operational_cfg = self.retrieval_config.get("operationalization", {}) or {}
        threshold_report = evaluate_rerank_thresholds(metrics, thresholds)
        scorecard = build_rerank_scorecard(
            metrics=metrics,
            thresholds=thresholds,
            threshold_report=threshold_report,
            cases=case_results,
            policy_mode=policy_mode,
            benchmark_family_id=str(operational_cfg.get("benchmark_family_id", "retrieval-rerank-operational")),
            threshold_set_id=str(operational_cfg.get("threshold_set_id", "retrieval-rerank-v2026-r1")),
        )
        report_id = new_id("retrievalops")
        destination = self.artifacts_dir / "retrieval" / "rerank-operational" / report_id
        destination.mkdir(parents=True, exist_ok=True)
        metrics_path = destination / "metrics.json"
        scorecard_path = destination / "scorecard.json"
        cases_path = destination / "cases.json"
        report_path = destination / "report.md"
        scorecard["artifact_path"] = str(scorecard_path)
        scorecard["report_id"] = report_id
        metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
        cases_path.write_text(json.dumps(case_results, indent=2), encoding="utf-8")
        report_path.write_text(
            "\n".join(
                [
                    f"# Retrieval Rerank Operationalization {report_id}",
                    "",
                    f"- Policy mode: {policy_mode}",
                    f"- Case count: {metrics['case_count']}",
                    f"- Pass rate: {metrics['pass_rate']}",
                    f"- Average relevance delta: {metrics['avg_relevance_delta']}",
                    f"- Average groundedness delta: {metrics['avg_groundedness_delta']}",
                    f"- Average provenance delta: {metrics['avg_provenance_delta']}",
                    f"- Average latency delta ms: {metrics['avg_latency_delta_ms']}",
                    f"- Provider coverage: {metrics['provider_coverage']}",
                    f"- Thresholds passed: {threshold_report['passed']}",
                ]
            ),
            encoding="utf-8",
        )
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "report_id": report_id,
            "summary": metrics,
            "scorecard": scorecard,
            "artifacts": {
                "metrics": str(metrics_path),
                "scorecard": str(scorecard_path),
                "cases": str(cases_path),
                "report": str(report_path),
            },
        }

    def summary(self) -> dict[str, Any]:
        base = self.artifacts_dir / "retrieval" / "rerank-operational"
        latest = None
        latest_artifacts: dict[str, str] = {}
        if base.exists():
            candidates = sorted([path for path in base.iterdir() if path.is_dir()], key=lambda item: item.name, reverse=True)
            for candidate in candidates:
                scorecard_path = candidate / "scorecard.json"
                if scorecard_path.exists():
                    latest = json.loads(scorecard_path.read_text(encoding="utf-8"))
                    latest_artifacts = {
                        "metrics": str(candidate / "metrics.json"),
                        "scorecard": str(scorecard_path),
                        "cases": str(candidate / "cases.json"),
                        "report": str(candidate / "report.md"),
                    }
                    break
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "configured_corpora": [item.get("corpus_id") for item in load_rerank_corpora(self.retrieval_config)],
            "thresholds": load_rerank_thresholds(self.retrieval_config),
            "latest_scorecard": latest,
            "latest_artifacts": latest_artifacts,
        }

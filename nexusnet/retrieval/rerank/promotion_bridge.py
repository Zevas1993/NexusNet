from __future__ import annotations

from typing import Any

from nexusnet.promotions.retrieval_rerank_evidence import build_retrieval_rerank_evidence_bundle

from .artifacts import RetrievalRerankArtifactStore
from .reports import build_retrieval_rerank_review_report, render_retrieval_rerank_review_markdown


class RetrievalRerankPromotionBridge:
    def __init__(self, *, artifacts_dir, retrieval_operational_bench: Any):
        self.artifacts = RetrievalRerankArtifactStore(artifacts_dir)
        self.retrieval_operational_bench = retrieval_operational_bench

    def enrich_traceability(
        self,
        *,
        subject_id: str,
        challenger_reference: str,
        traceability: dict[str, Any] | None,
    ) -> dict[str, Any]:
        traceability = dict(traceability or {})
        policy_mode = str(traceability.get("policy_mode") or challenger_reference or "lexical+graph-memory-temporal-rerank")
        session_id = traceability.get("session_id")
        report = self.retrieval_operational_bench.run(session_id=session_id, policy_mode=policy_mode)
        scorecard = dict(report.get("scorecard") or {})
        bundle = build_retrieval_rerank_evidence_bundle(
            subject_id=subject_id,
            policy_mode=policy_mode,
            challenger_reference=challenger_reference,
            traceability=traceability,
            scorecard=scorecard,
            scorecard_artifacts=report.get("artifacts", {}),
        )
        review_report = build_retrieval_rerank_review_report(bundle=bundle)
        review_payload_path = self.artifacts.write_review_payload(policy_mode=policy_mode, payload=review_report)
        review_markdown_path = self.artifacts.write_review_markdown(
            policy_mode=policy_mode,
            report_id=review_report["report_id"],
            markdown=render_retrieval_rerank_review_markdown(review_report),
        )
        bundle["review_report_id"] = review_report["report_id"]
        bundle["review_headline"] = review_report["headline"]
        bundle["review_summary"] = list(review_report.get("operator_summary", []))
        bundle["review_artifacts"] = {
            "payload": review_payload_path,
            "markdown": review_markdown_path,
        }
        artifact_path = self.artifacts.write_evidence_bundle(policy_mode=policy_mode, payload=bundle)
        bundle["artifact_path"] = artifact_path
        benchmark_payload = dict(traceability.get("benchmark", {}))
        benchmark_payload.update(
            {
                "retrieval_rerank_scorecard": scorecard,
                "retrieval_rerank_artifacts": dict(report.get("artifacts", {})),
                "retrieval_rerank_report_id": report.get("report_id"),
                "retrieval_rerank_review": review_report,
            }
        )
        traceability.update(
            {
                "policy_mode": policy_mode,
                "retrieval_rerank_evidence": bundle,
                "retrieval_rerank_review": review_report,
                "retrieval_rerank_evidence_bundle_id": bundle["bundle_id"],
                "benchmark_family_id": bundle.get("benchmark_family_id"),
                "threshold_set_id": traceability.get("threshold_set_id") or bundle.get("threshold_set_id"),
                "benchmark": benchmark_payload,
            }
        )
        return traceability

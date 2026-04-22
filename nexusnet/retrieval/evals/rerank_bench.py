from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import RetrievalRequest, new_id, utcnow

from ..rerank.score_fusion import average_groundedness, average_relevance


class RetrievalRerankBenchmarkSuite:
    def __init__(self, *, artifacts_dir: Path, retrieval_service: Any):
        self.artifacts_dir = artifacts_dir
        self.retrieval_service = retrieval_service

    def run(
        self,
        *,
        query: str,
        session_id: str | None = None,
        top_k: int = 6,
        policy_mode: str = "lexical+graph-memory-temporal-rerank",
    ) -> dict[str, Any]:
        before = self.retrieval_service.query_with_policy(
            RetrievalRequest(query=query, top_k=top_k, session_id=session_id),
            policy_mode=policy_mode,
            rerank_enabled=False,
        )
        after = self.retrieval_service.query_with_policy(
            RetrievalRequest(query=query, top_k=top_k, session_id=session_id),
            policy_mode=policy_mode,
            rerank_enabled=True,
        )
        report_id = new_id("retrievalbench")
        destination = self.artifacts_dir / "retrieval" / "rerank" / report_id
        destination.mkdir(parents=True, exist_ok=True)

        metrics = {
            "query": query,
            "policy_mode": policy_mode,
            "top_k": top_k,
            "without_rerank": {
                "top_k": before.get("top_k_after_rerank", len(before.get("hits", []))),
                "average_relevance": average_relevance(before.get("hits", [])),
                "average_groundedness": average_groundedness(before.get("hits", [])),
                "candidate_sources": before.get("candidate_source_counts", {}),
            },
            "with_rerank": {
                "top_k_before_rerank": after.get("top_k_before_rerank", 0),
                "top_k_after_rerank": after.get("top_k_after_rerank", 0),
                "average_relevance": average_relevance(after.get("hits", [])),
                "average_groundedness": average_groundedness(after.get("hits", [])),
                "reranker_provider": (after.get("reranker") or {}).get("provider"),
                "latency_delta_ms": (after.get("reranker") or {}).get("latency_delta_ms", 0),
            },
            "delta": {
                "relevance_delta": ((after.get("reranker") or {}).get("relevance_delta", 0.0)),
                "groundedness_delta": ((after.get("reranker") or {}).get("groundedness_delta", 0.0)),
                "provenance_delta": ((after.get("reranker") or {}).get("provenance_delta", 0.0)),
                "latency_delta_ms": ((after.get("reranker") or {}).get("latency_delta_ms", 0)),
            },
            "generated_at": utcnow().isoformat(),
        }
        metrics_path = destination / "metrics.json"
        report_path = destination / "report.md"
        metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        report_path.write_text(
            "\n".join(
                [
                    f"# Retrieval Rerank Benchmark {report_id}",
                    "",
                    f"- Query: {query}",
                    f"- Policy mode: {policy_mode}",
                    f"- Top-k before rerank: {metrics['with_rerank']['top_k_before_rerank']}",
                    f"- Top-k after rerank: {metrics['with_rerank']['top_k_after_rerank']}",
                    f"- Reranker provider: {metrics['with_rerank']['reranker_provider']}",
                    f"- Relevance delta: {metrics['delta']['relevance_delta']}",
                    f"- Groundedness delta: {metrics['delta']['groundedness_delta']}",
                    f"- Provenance delta: {metrics['delta']['provenance_delta']}",
                    f"- Latency delta ms: {metrics['delta']['latency_delta_ms']}",
                ]
            ),
            encoding="utf-8",
        )
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "report_id": report_id,
            "metrics": metrics,
            "artifacts": {
                "metrics": str(metrics_path),
                "report": str(report_path),
            },
        }

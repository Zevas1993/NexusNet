from __future__ import annotations


class GraphRAGEvaluator:
    def evaluate(self, *, query: str, hits: list[dict]) -> dict:
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "query": query,
            "hit_count": len(hits),
            "avg_score": round(sum(hit.get("score", 0.0) for hit in hits) / len(hits), 3) if hits else 0.0,
            "plane_coverage": sorted({plane for hit in hits for plane in hit.get("plane_tags", [])}),
        }

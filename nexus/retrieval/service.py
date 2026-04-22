from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any

from ..config import NexusPaths
from ..schemas import MemoryQuery, RetrievalDocumentInput, RetrievalHit, RetrievalIngestRequest, RetrievalRequest
from ..storage import NexusStore
from nexusnet.retrieval.rerank import CrossEncoderStageTwoReranker, weighted_reciprocal_rank_fusion


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize(text: str) -> list[str]:
    return [token for token in re.findall(r"[a-zA-Z0-9_]+", text.lower()) if token]


def _chunk_text(text: str, max_chars: int = 450, overlap: int = 60) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + max_chars)
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = max(0, end - overlap)
    return chunks


def _hit_summary(hit: RetrievalHit) -> dict[str, Any]:
    metadata = hit.metadata or {}
    return {
        "chunk_id": hit.chunk_id,
        "source": hit.source,
        "score": round(float(hit.score), 6),
        "retrieval_stage": metadata.get("retrieval_stage"),
        "rerank_score": metadata.get("rerank_score"),
        "candidate_sources": metadata.get("candidate_sources", []),
        "backend": metadata.get("backend"),
    }


class RetrievalService:
    def __init__(
        self,
        paths: NexusPaths,
        store: NexusStore,
        *,
        graph_retriever: Any | None = None,
        graph_service: Any | None = None,
        memory_service: Any | None = None,
        temporal_retriever: Any | None = None,
        retrieval_config: dict[str, Any] | None = None,
    ):
        self.paths = paths
        self.store = store
        self.graph_retriever = graph_retriever
        self.graph_service = graph_service
        self.memory_service = memory_service
        self.temporal_retriever = temporal_retriever
        self.retrieval_config = retrieval_config or {}
        stage2 = self.retrieval_config.get("stage2", {}) or {}
        self.reranker = CrossEncoderStageTwoReranker(
            model_name=str(stage2.get("provider", "cross-encoder/ms-marco-MiniLM-L6-v2")),
            device=str(stage2.get("device", "cpu")),
            fallback_provider=str(stage2.get("fallback_provider", "heuristic-cross-encoder")),
        )

    def ingest(self, request: RetrievalIngestRequest) -> list[str]:
        doc_ids = []
        for document in request.documents:
            doc_ids.append(self._ingest_document(document))
        return doc_ids

    def query(self, request: RetrievalRequest) -> list[RetrievalHit]:
        return self.query_with_policy(request)["hits"]

    def query_with_policy(
        self,
        request: RetrievalRequest,
        *,
        policy_mode: str = "lexical+graph-merged",
        plane_tags: list[str] | None = None,
        rerank_enabled: bool | None = None,
    ) -> dict[str, Any]:
        stage1 = self.retrieval_config.get("stage1", {}) or {}
        sources_cfg = stage1.get("sources", {}) or {}
        candidate_limit = int(stage1.get("top_k", max(request.top_k, 12)))
        effective_policy = policy_mode

        lexical_hits = self._lexical_hits(request.query, candidate_limit)
        if request.use_pgvector or bool(sources_cfg.get("pgvector", False)):
            lexical_hits = self._merge_pgvector_hits(request.query, candidate_limit, lexical_hits)

        graph_store_health = self.graph_service.status() if self.graph_service is not None else {
            "provider_name": "unconfigured",
            "status_label": "IMPLEMENTATION BRANCH",
            "node_count": 0,
            "edge_count": 0,
            "source_count": 0,
        }
        graph_hits = self._graph_hits(query=request.query, top_k=candidate_limit, plane_tags=plane_tags) if bool(sources_cfg.get("graph", True)) else []
        memory_hits = self._memory_hits(query=request.query, session_id=request.session_id, top_k=candidate_limit) if bool(sources_cfg.get("memory", True)) else []
        temporal_hits = self._temporal_hits(query=request.query, top_k=candidate_limit) if bool(sources_cfg.get("temporal", True)) else []

        if effective_policy == "lexical-baseline":
            fused_hits = lexical_hits
        elif effective_policy == "graph-priority-experimental":
            fused_hits = self._merge_hits(graph_hits, lexical_hits, candidate_limit)
        else:
            effective_policy = "lexical+graph-memory-temporal-rerank"
            fusion_cfg = stage1.get("fusion", {}) or {}
            fused_hits = weighted_reciprocal_rank_fusion(
                runs={
                    "lexical": lexical_hits,
                    "graph": graph_hits,
                    "memory": memory_hits,
                    "temporal": temporal_hits,
                },
                weights={
                    "lexical": float(fusion_cfg.get("lexical_weight", 1.0)),
                    "graph": float(fusion_cfg.get("graph_weight", 1.15)),
                    "memory": float(fusion_cfg.get("memory_weight", 0.95)),
                    "temporal": float(fusion_cfg.get("temporal_weight", 1.0)),
                },
                rrf_k=int(fusion_cfg.get("rrf_k", 60)),
                limit=candidate_limit,
            )

        stage2_cfg = self.retrieval_config.get("stage2", {}) or {}
        should_rerank = bool(stage2_cfg.get("enabled", True)) if rerank_enabled is None else bool(rerank_enabled)
        rerank_top_k = min(int(stage2_cfg.get("rerank_top_k", request.top_k)), len(fused_hits), request.top_k)
        before_rerank_hits = list(fused_hits[: max(rerank_top_k, request.top_k)])
        rerank_result = self.reranker.rerank(
            query=request.query,
            candidates=fused_hits,
            top_k=rerank_top_k,
        ) if should_rerank else None
        merged_hits = rerank_result.hits if rerank_result is not None and rerank_result.applied else before_rerank_hits[:request.top_k]

        graph_contribution_count = sum(1 for hit in merged_hits if hit.metadata.get("backend") == "graphrag")
        memory_contribution_count = sum(1 for hit in merged_hits if hit.metadata.get("backend") == "memory")
        temporal_contribution_count = sum(1 for hit in merged_hits if hit.metadata.get("backend") == "temporal")
        graph_provenance = [
            {
                "node_id": hit.metadata.get("graph_node_id"),
                "source": hit.metadata.get("graph_source"),
                "plane_tags": hit.metadata.get("plane_tags", []),
            }
            for hit in merged_hits
            if hit.metadata.get("backend") == "graphrag"
        ]
        quality_delta = rerank_result.diagnostics if rerank_result is not None else {"relevance_delta": 0.0, "groundedness_delta": 0.0}
        requested_top_k = request.top_k
        telemetry_cfg = self.retrieval_config.get("telemetry", {}) or {}
        return {
            "hits": merged_hits[: request.top_k],
            "policy_mode": policy_mode,
            "effective_policy_mode": effective_policy,
            "graph_store_health": graph_store_health,
            "graph_contribution_count": graph_contribution_count,
            "memory_contribution_count": memory_contribution_count,
            "temporal_contribution_count": temporal_contribution_count,
            "plane_tags": plane_tags or [],
            "graph_provenance": graph_provenance,
            "candidate_source_counts": {
                "lexical": len(lexical_hits),
                "graph": len(graph_hits),
                "memory": len(memory_hits),
                "temporal": len(temporal_hits),
            },
            "top_k_before_rerank": len(before_rerank_hits[:requested_top_k]),
            "top_k_after_rerank": len(merged_hits[: requested_top_k]),
            "reranker": {
                "provider": rerank_result.provider_name if rerank_result is not None else None,
                "applied": bool(rerank_result and rerank_result.applied),
                "requested_top_k": requested_top_k,
                "top_k_before_rerank": len(before_rerank_hits[:requested_top_k]),
                "top_k_after_rerank": len(merged_hits[: requested_top_k]),
                "latency_delta_ms": rerank_result.latency_ms if rerank_result is not None else 0,
                "relevance_delta": round(float(quality_delta.get("relevance_delta", 0.0)), 4),
                "groundedness_delta": round(float(quality_delta.get("groundedness_delta", 0.0)), 4),
                "provenance_delta": round(float(quality_delta.get("provenance_delta", 0.0)), 4),
            },
            "candidate_list_before_rerank": [_hit_summary(hit) for hit in before_rerank_hits[:requested_top_k]]
            if telemetry_cfg.get("persist_candidate_lists", True)
            else [],
            "candidate_list_after_rerank": [_hit_summary(hit) for hit in merged_hits[:requested_top_k]]
            if telemetry_cfg.get("persist_candidate_lists", True)
            else [],
        }

    def _ingest_document(self, document: RetrievalDocumentInput) -> str:
        doc_id = hashlib.sha256(f"{document.source}|{document.title}|{document.text}".encode("utf-8")).hexdigest()[:16]
        created_at = _utcnow()
        payload = {
            "doc_id": doc_id,
            "source": document.source,
            "title": document.title,
            "content": document.text,
            "metadata": document.metadata,
            "created_at": created_at,
        }
        self.store.save_retrieval_document(payload)
        self.store.write_artifact(f"retrieval/docs/{doc_id}.txt", document.text)
        chunks = []
        for index, chunk in enumerate(_chunk_text(document.text)):
            chunks.append(
                {
                    "chunk_id": hashlib.sha256(f"{doc_id}:{index}:{chunk}".encode("utf-8")).hexdigest()[:16],
                    "doc_id": doc_id,
                    "chunk_index": index,
                    "source": document.source,
                    "content": chunk,
                    "metadata": {"title": document.title, **document.metadata},
                    "created_at": created_at,
                }
            )
        self.store.replace_retrieval_chunks(doc_id, chunks)
        return doc_id

    def _lexical_hits(self, query: str, top_k: int) -> list[RetrievalHit]:
        query_terms = _normalize(query)
        if not query_terms:
            return []
        candidates = []
        for chunk in self.store.list_retrieval_chunks():
            haystack_terms = _normalize(chunk["content"])
            overlap = sum(haystack_terms.count(term) for term in query_terms)
            if overlap <= 0:
                continue
            score = float(overlap) / max(len(query_terms), 1)
            candidates.append(
                RetrievalHit(
                    chunk_id=chunk["chunk_id"],
                    doc_id=chunk["doc_id"],
                    source=chunk["source"],
                    content=chunk["content"],
                    score=score,
                    metadata=chunk.get("metadata", {}),
                )
            )
        candidates.sort(key=lambda hit: hit.score, reverse=True)
        return candidates[:top_k]

    def _merge_pgvector_hits(self, query: str, top_k: int, lexical_hits: list[RetrievalHit]) -> list[RetrievalHit]:
        try:
            from core.rag.pgvector_adapter import available, search  # type: ignore

            if not available():
                return lexical_hits
            rows = search(query, top_k=top_k)
        except Exception:
            return lexical_hits
        merged = {hit.chunk_id: hit for hit in lexical_hits}
        for row in rows:
            row_id = row.get("doc_id") or row.get("chunk_id")
            if not row_id:
                continue
            merged[row_id] = RetrievalHit(
                chunk_id=row_id,
                doc_id=row.get("doc_id", row_id),
                source="pgvector",
                content=row.get("snippet", ""),
                score=float(row.get("score", 0.0) or 0.0),
                metadata={"backend": "pgvector"},
            )
        output = list(merged.values())
        output.sort(key=lambda hit: hit.score, reverse=True)
        return output[:top_k]

    def _graph_hits(self, *, query: str, top_k: int, plane_tags: list[str] | None = None) -> list[RetrievalHit]:
        if self.graph_retriever is None:
            return []
        try:
            rows = self.graph_retriever.query(query=query, top_k=top_k, plane_tags=plane_tags)
        except Exception:
            return []
        hits = []
        for row in rows:
            provenance = row.get("provenance") or {}
            node_id = row.get("node_id")
            if not node_id:
                continue
            hits.append(
                RetrievalHit(
                    chunk_id=f"graph::{node_id}",
                    doc_id=node_id,
                    source=f"graphrag::{provenance.get('source', 'graph')}",
                    content=row.get("content", ""),
                    score=float(row.get("score", 0.0) or 0.0),
                    metadata={
                        "backend": "graphrag",
                        "graph_node_id": node_id,
                        "graph_source": provenance.get("source"),
                        "plane_tags": row.get("plane_tags", []),
                        "provenance": provenance,
                    },
                )
            )
        return hits

    def _memory_hits(self, *, query: str, session_id: str | None, top_k: int) -> list[RetrievalHit]:
        if self.memory_service is None or not session_id:
            return []
        try:
            records = self.memory_service.query(MemoryQuery(session_id=session_id, plane=None, limit=max(top_k * 4, 20)))
        except Exception:
            return []
        query_terms = _normalize(query)
        hits: list[RetrievalHit] = []
        for record in records:
            text = json.dumps(record.content, sort_keys=True)
            haystack_terms = _normalize(text)
            overlap = sum(haystack_terms.count(term) for term in query_terms)
            if overlap <= 0:
                continue
            score = round(float(overlap) / max(len(query_terms), 1), 6)
            hits.append(
                RetrievalHit(
                    chunk_id=f"memory::{record.memory_id}",
                    doc_id=record.memory_id,
                    source=f"memory::{record.plane}",
                    content=text,
                    score=score,
                    metadata={
                        "backend": "memory",
                        "memory_plane": record.plane,
                        "memory_role": record.role,
                        "tags": record.tags,
                        "provenance": {"session_id": record.session_id, "memory_id": record.memory_id},
                    },
                )
            )
        hits.sort(key=lambda hit: hit.score, reverse=True)
        return hits[:top_k]

    def _temporal_hits(self, *, query: str, top_k: int) -> list[RetrievalHit]:
        if self.temporal_retriever is None:
            return []
        try:
            rows = self.temporal_retriever.retrieve_as_of(query, datetime.now(timezone.utc).date().isoformat(), limit=top_k)
        except Exception:
            return []
        hits: list[RetrievalHit] = []
        for index, row in enumerate(rows):
            content = " ".join(str(row.get(key, "")) for key in ["subject", "predicate", "object"] if row.get(key))
            confidence = float(row.get("confidence", 0.5) or 0.5)
            hits.append(
                RetrievalHit(
                    chunk_id=f"temporal::{index}::{row.get('subject', 'fact')}",
                    doc_id=f"temporal::{row.get('subject', 'fact')}",
                    source=f"temporal::{row.get('source', 'timeline')}",
                    content=content,
                    score=confidence,
                    metadata={
                        "backend": "temporal",
                        "temporal_start": row.get("start"),
                        "temporal_end": row.get("end"),
                        "provenance": row,
                    },
                )
            )
        return hits[:top_k]

    def _merge_hits(self, primary: list[RetrievalHit], secondary: list[RetrievalHit], top_k: int) -> list[RetrievalHit]:
        merged = {hit.chunk_id: hit for hit in primary}
        for hit in secondary:
            merged.setdefault(hit.chunk_id, hit)
        output = list(merged.values())
        output.sort(key=lambda hit: hit.score, reverse=True)
        return output[:top_k]

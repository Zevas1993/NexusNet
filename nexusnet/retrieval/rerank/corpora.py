from __future__ import annotations

from typing import Any

from nexus.schemas import RetrievalDocumentInput, RetrievalIngestRequest


def load_rerank_corpora(config: dict[str, Any]) -> list[dict[str, Any]]:
    operational = (config.get("operationalization") or {})
    corpora = list(operational.get("corpora", []))
    return corpora


def flatten_rerank_cases(corpora: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for corpus in corpora:
        for family in corpus.get("query_families", []):
            for case in family.get("cases", []):
                cases.append(
                    {
                        "corpus_id": corpus.get("corpus_id"),
                        "family_id": family.get("family_id"),
                        "family_label": family.get("label"),
                        **case,
                    }
                )
    return cases


def ensure_corpora_ingested(retrieval_service: Any, corpora: list[dict[str, Any]]) -> list[str]:
    existing = {
        chunk.get("source")
        for chunk in retrieval_service.store.list_retrieval_chunks()
        if str(chunk.get("source", "")).startswith("rerank-bench::")
    }
    ingested: list[str] = []
    for corpus in corpora:
        documents = []
        for document in corpus.get("documents", []):
            source = str(document.get("source") or f"rerank-bench::{corpus.get('corpus_id', 'default')}")
            if source in existing:
                continue
            documents.append(
                RetrievalDocumentInput(
                    source=source,
                    title=str(document.get("title", source)),
                    text=str(document.get("text", "")),
                    metadata=dict(document.get("metadata", {})),
                )
            )
        if documents:
            ingested.extend(retrieval_service.ingest(RetrievalIngestRequest(documents=documents)))
    return ingested

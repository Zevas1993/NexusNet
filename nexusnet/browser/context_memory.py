from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow
from nexusnet.policy import PolicyKernel


BrowserContextType = Literal["tab", "page", "history", "bookmark", "download", "note"]
SourcePermission = Literal["operator_provided", "public", "unknown"]


class BrowserContextIngestRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    context_id: str
    context_type: BrowserContextType
    title: str
    url: str = ""
    text: str
    local_only: bool = True
    contains_private_data: bool = False
    source_permission: SourcePermission = "unknown"
    provenance_ref: str = ""
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class BrowserContextQueryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query_id: str
    question: str
    limit: int = 5
    include_private: bool = True
    tags: list[str] = Field(default_factory=list)


class BrowserContextMemory:
    def __init__(self, *, artifacts_dir: Path | None = None):
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.context_dir = self.artifacts_dir / "browser" / "context-memory" if self.artifacts_dir else None
        if self.context_dir is not None:
            self.context_dir.mkdir(parents=True, exist_ok=True)
        self._memory_records: list[dict[str, Any]] = []
        self._memory_queries: list[dict[str, Any]] = []
        self.policy_kernel = PolicyKernel.default()

    def ingest(self, request: BrowserContextIngestRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, BrowserContextIngestRequest) else BrowserContextIngestRequest.model_validate(request)
        privacy_findings = _privacy_findings(normalized)
        policy_scan = self.policy_kernel.scan(_policy_targets(normalized))
        blocked = bool(privacy_findings) or policy_scan.summary.active_hard_fail_count > 0
        text = _clean_text(normalized.text)
        record = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "browser-context",
            "context_id": normalized.context_id,
            "context_type": normalized.context_type,
            "title": normalized.title,
            "url": normalized.url,
            "status": "blocked" if blocked else "indexed",
            "created_at": utcnow().isoformat(),
            "privacy_boundary": "local-context-index",
            "local_only": normalized.local_only,
            "contains_private_data": normalized.contains_private_data,
            "source_permission": normalized.source_permission,
            "provenance_ref": normalized.provenance_ref,
            "tags": normalized.tags,
            "text_excerpt": text[:500],
            "token_count": _estimate_tokens(text),
            "terms": sorted(_terms(f"{normalized.title} {text}")),
            "privacy_findings": privacy_findings,
            "policy_scan": policy_scan.model_dump(mode="json"),
            "metadata": normalized.metadata,
        }
        self._persist_record(record)
        return record

    def query(self, request: BrowserContextQueryRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, BrowserContextQueryRequest) else BrowserContextQueryRequest.model_validate(request)
        question_terms = _terms(normalized.question)
        records = [
            record
            for record in self._list_records(limit=200)
            if record.get("status") == "indexed"
            and (normalized.include_private or not record.get("contains_private_data"))
            and (not normalized.tags or set(normalized.tags).issubset(set(record.get("tags") or [])))
        ]
        scored = []
        for record in records:
            record_terms = set(record.get("terms") or [])
            overlap = sorted(question_terms & record_terms)
            if not overlap:
                continue
            scored.append(
                {
                    "context_id": record["context_id"],
                    "title": record["title"],
                    "url": record["url"],
                    "context_type": record["context_type"],
                    "score": len(overlap),
                    "matched_terms": overlap,
                    "provenance_ref": record.get("provenance_ref") or "",
                    "text_excerpt": record.get("text_excerpt") or "",
                }
            )
        scored.sort(key=lambda item: (item["score"], item["title"]), reverse=True)
        top_results = scored[: max(1, normalized.limit)]
        query = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "query_id": normalized.query_id,
            "question": normalized.question,
            "result_count": len(top_results),
            "top_results": top_results,
            "answer_summary": _answer_summary(top_results),
            "privacy_boundary": "local-query-over-operator-provided-context",
            "operator_actions": _operator_actions(),
        }
        self._memory_queries.insert(0, query)
        self._memory_queries = self._memory_queries[:50]
        return query

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        records = self._list_records(limit=limit)
        queries = list(self._memory_queries[:limit])
        latest = records[0] if records else None
        runtime_state = "static-canon"
        if latest:
            runtime_state = "degraded" if latest.get("status") == "blocked" else "live-bound"
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "browser-context",
            "authority": "NexusBrain",
            "runtime_state": runtime_state,
            "context_count": len(records),
            "indexed_count": sum(1 for record in records if record.get("status") == "indexed"),
            "blocked_count": sum(1 for record in records if record.get("status") == "blocked"),
            "latest_context": latest,
            "latest_query": queries[0] if queries else None,
            "contexts": records,
            "queries": queries,
            "required_controls": _required_controls(),
            "operator_actions": _operator_actions(),
        }

    def scorecard(self) -> dict[str, Any]:
        summary = self.summary()
        return {
            **summary,
            "source_documents": [
                "youtube-transcript::jB3yKR6bOjQ",
                "docs/NEXUSNET_YOUTUBE_ASSIMILATION_INTAKE_2026-04-30.md",
            ],
            "assimilation_pattern": "local-browser-agent-context-search",
            "privacy_boundary": "no-browser-context-leaves-local-index-by-default",
        }

    def _persist_record(self, record: dict[str, Any]) -> None:
        self._memory_records.insert(0, record)
        self._memory_records = self._memory_records[:50]
        if self.context_dir is not None:
            safe_id = record["context_id"].replace(":", "_").replace("/", "_")
            path = self.context_dir / f"{safe_id}.json"
            record["artifact_path"] = str(path)
            path.write_text(json.dumps(record, indent=2), encoding="utf-8")

    def _list_records(self, *, limit: int) -> list[dict[str, Any]]:
        records = list(self._memory_records)
        seen = {record.get("context_id") for record in records}
        if self.context_dir is not None:
            for path in self.context_dir.glob("*.json"):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if payload.get("context_id") not in seen:
                    records.append(payload)
        records.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return records[:limit]


def _policy_targets(request: BrowserContextIngestRequest) -> list[dict[str, Any]]:
    return [
        {
            "target_id": f"browser-memory::{request.context_id}",
            "target_type": "memory_update",
            "metadata": {
                "provenance_refs": [request.provenance_ref] if request.provenance_ref else [],
                "retention_policy": "project" if request.local_only else "needs_review",
                "requires_review": request.contains_private_data or request.source_permission == "unknown",
            },
        }
    ]


def _privacy_findings(request: BrowserContextIngestRequest) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if request.source_permission == "unknown":
        findings.append(
            {
                "rule_id": "browser_context_requires_operator_permission",
                "severity": "hard_fail",
                "message": "Browser context must be explicitly operator-provided or public before indexing.",
            }
        )
    if request.contains_private_data and not request.local_only:
        findings.append(
            {
                "rule_id": "private_browser_context_requires_local_only",
                "severity": "hard_fail",
                "message": "Private browser context cannot be indexed without a local-only boundary.",
            }
        )
    return findings


def _required_controls() -> list[str]:
    return [
        "local_only_browser_context",
        "operator_permission",
        "tab_page_history_schema",
        "provenance_refs",
        "private_context_filter",
        "natural_language_query",
        "citation_results",
        "no_cloud_export_by_default",
    ]


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/browser-context"},
        "ingest": {"method": "POST", "endpoint": "/ops/brain/browser-context/ingest"},
        "query": {"method": "POST", "endpoint": "/ops/brain/browser-context/query"},
        "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/browser-context"},
    }


def _answer_summary(results: list[dict[str, Any]]) -> str:
    if not results:
        return "No indexed browser context matched the question."
    titles = ", ".join(result["title"] for result in results[:3])
    return f"Matched local browser context: {titles}."


def _clean_text(text: str) -> str:
    return " ".join(text.strip().split())


def _estimate_tokens(text: str) -> int:
    return max(1, len(text.split()))


def _terms(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) > 2 and token not in {"the", "and", "for", "with", "can", "that", "this", "from"}
    }

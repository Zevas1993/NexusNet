from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .artifact_schema import KnowledgeArtifact, KnowledgeCompileRequest, KnowledgeRequestContract
from .artifact_store import KnowledgeArtifactStore
from .conflict_resolution import resolve_claim_conflicts
from .evals import compiled_vs_raw_eval
from .freshness import freshness_report_for
from .provenance import sha256_ref, source_digest


_PRIVATE_SOURCE_REF_SEGMENTS = {
    ".credentials",
    ".keys",
    ".secrets",
    "credentials",
    "keys",
    "private",
    "private_data",
    "private-data",
    "secrets",
}
_PRIVATE_SOURCE_REF_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    "id_ed25519",
    "id_rsa",
}


class KnowledgeArtifactCompiler:
    def __init__(self, *, artifacts_dir: Path | str | None = None, source_root: Path | str | None = None):
        self.store = KnowledgeArtifactStore(artifacts_dir)
        self.source_root = Path(source_root).resolve() if source_root is not None else Path.cwd().resolve()

    def compile(self, request: KnowledgeCompileRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, KnowledgeCompileRequest) else KnowledgeCompileRequest.model_validate(request)
        resolved_sources, source_ref_exclusions = _resolve_source_refs(normalized.source_refs, self.source_root)
        normalized_sources = [*normalized.sources, *resolved_sources]
        allowed_sources, excluded_sources = _filter_sources(normalized, normalized_sources)
        excluded_sources = [*excluded_sources, *source_ref_exclusions]
        source_ref_security_gate = _source_ref_security_gate(normalized.source_refs, resolved_sources, source_ref_exclusions)
        blocked_source_refs = source_ref_security_gate["blocked_source_refs"]
        source_payloads = [source.model_dump(mode="json") for source in allowed_sources]
        source_digests = [
            {
                "source_ref": source["source_ref"],
                "digest": source_digest(source),
                "source_url": source.get("source_url", ""),
                "license_state": source.get("license_state", "pending_review"),
                "privacy_class": source.get("privacy_class", "public"),
            }
            for source in source_payloads
        ]
        claims = _claims_from_sources(source_payloads)
        facts, conflicts = resolve_claim_conflicts(claims)
        summary = _summary_for(normalized.task_family, source_payloads, conflicts)
        content = {
            "summary": summary,
            "facts": facts,
            "relationships": _relationships_for(normalized.task_family, source_payloads),
            "open_questions": _open_questions_for(conflicts, excluded_sources),
            "recommended_actions": _recommended_actions_for(normalized.task_family),
        }
        citations = _field_citations(content=content, source_refs=[source["source_ref"] for source in source_payloads], facts=facts)
        confidence = {
            "overall": 0.72 if conflicts else (0.92 if source_payloads else 0.0),
            "per_field": {field: 0.72 if field.startswith("content.facts") and conflicts else 0.9 for field in citations},
        }
        compiled_at = _utcnow()
        core_payload = {
            "artifact_type": "task_context",
            "task_family": normalized.task_family,
            "scope": normalized.scope,
            "content": content,
            "field_citations": citations,
            "source_digests": source_digests,
            "confidence": confidence,
            "conflict_objects": conflicts,
            "governance": {
                **normalized.governance,
                "rbac_scope": normalized.scope.get("rbac_scope", []),
                "status": "candidate",
                "permission_filtered_source_count": len(excluded_sources),
                "blocked_source_ref_count": len(blocked_source_refs),
                "mutation_allowed": False,
                "pinecone_runtime_dependency": False,
                "promotion_boundary": "candidate-until-code-backed-tests-control-panel-replay",
            },
            "freshness": {
                "compiled_at": compiled_at,
                "ttl_policy": normalized.freshness_policy.get("ttl_policy", "recompile_on_source_change_or_7d"),
                "source_versions": source_digests,
            },
            "status": "candidate",
            "excluded_sources": excluded_sources,
            "blocked_source_refs": blocked_source_refs,
            "source_ref_security_gate": source_ref_security_gate,
            "control_panel_replay": {
                "surface_id": "knowledge-artifact-compiler",
                "source_ref_security_gate": {
                    "allowed": source_ref_security_gate["allowed"],
                    "requested_count": source_ref_security_gate["requested_count"],
                    "allowed_count": source_ref_security_gate["allowed_count"],
                    "blocked_count": source_ref_security_gate["blocked_count"],
                    "blocked_reason_counts": source_ref_security_gate["blocked_reason_counts"],
                },
                "blocked_source_refs": blocked_source_refs,
                "artifact_trust_replay": {
                    "recommended_scanner": "ArtifactTrustRegistry.scan_knowledge_artifact",
                    "blocked_source_ref_count": len(blocked_source_refs),
                    "mutation_allowed": False,
                },
            },
            "fallback_policy": {
                "raw_retrieval_available": True,
                "raw_retrieval_boundary": "fallback-lane-only",
            },
        }
        digest = sha256_ref(_stable_artifact_hash_payload(core_payload)).removeprefix("sha256:")
        artifact_payload = {
            "artifact_id": f"kac://{_slug(normalized.task_family)}/{digest[:16]}",
            **core_payload,
            "artifact_hash": f"sha256:{digest}",
        }
        artifact_trust_preview = _artifact_trust_preview(artifact_payload)
        artifact_payload["artifact_trust_preview"] = artifact_trust_preview
        artifact_payload["control_panel_replay"]["artifact_trust_preview"] = artifact_trust_preview
        artifact = KnowledgeArtifact.model_validate(artifact_payload)
        artifact_payload["validation"] = artifact.validation_report()
        artifact_payload["eval"] = compiled_vs_raw_eval(artifact=artifact_payload, raw_source_count=len(source_payloads))
        return self.store.save(artifact_payload)

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        artifacts = self.store.list(limit=limit)
        latest = artifacts[0] if artifacts else None
        stale_count = sum(1 for artifact in artifacts if (artifact.get("freshness") or {}).get("freshness_state") == "stale")
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "knowledge-artifact-compiler",
            "authority": "NexusBrain",
            "status": "candidate",
            "runtime_state": "live-bound" if artifacts else "static-canon",
            "artifact_count": len(artifacts),
            "stale_count": stale_count,
            "query_event_count": len(self.store.query_events(limit=500)),
            "latest_query_event": self.store.query_events(limit=1)[0] if self.store.query_events(limit=1) else None,
            "latest_artifact": _artifact_summary(latest) if latest else None,
            "artifacts": [_artifact_summary(artifact) for artifact in artifacts],
            "boundary": "compiled-context-artifacts-only-no-prompt-model-weight-or-runtime-mutation",
            "raw_retrieval_boundary": "raw retrieval remains a fallback recall lane",
            "required_controls": [
                "field_level_citations",
                "source_digests",
                "freshness_invalidation",
                "rbac_privacy_filter",
                "source_ref_security_gate",
                "artifact_trust_preview",
                "artifact_trust_scan",
                "query_mutation_boundary",
                "conflict_objects",
                "raw_retrieval_fallback",
                "candidate_ledger_gate",
            ],
            "operator_actions": {
                "compile": {"method": "POST", "endpoint": "/ops/brain/knowledge-artifacts/compile"},
                "query": {"method": "POST", "endpoint": "/ops/brain/knowledge-artifacts/query"},
                "query_events": {"method": "GET", "endpoint": "/ops/brain/knowledge-artifacts/query-events"},
                "freshness": {"method": "POST", "endpoint": "/ops/brain/knowledge-artifacts/freshness"},
                "list": {"method": "GET", "endpoint": "/ops/brain/knowledge-artifacts"},
                "detail": {"method": "GET", "endpoint_template": "/ops/brain/knowledge-artifacts/{artifact_id}"},
                "artifact_trust_scan": {"method": "POST", "endpoint": "/ops/brain/artifact-trust/knowledge-artifacts/scan"},
                "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/knowledge-artifacts"},
            },
        }

    def scorecard(self, *, limit: int = 50) -> dict[str, Any]:
        summary = self.summary(limit=limit)
        latest = summary.get("latest_artifact") or {}
        source_gate = latest.get("source_ref_security_gate") or {}
        artifact_trust_preview = latest.get("artifact_trust_preview") or {}
        freshness = latest.get("freshness") or {}
        code_backed_consumers = _code_backed_consumers()
        active_runtime_blockers: list[str] = []
        if int(source_gate.get("blocked_count") or 0) > 0:
            active_runtime_blockers.append("kac_source_ref_security_gate_blocked")
        if artifact_trust_preview.get("status") == "quarantined":
            active_runtime_blockers.append("kac_latest_artifact_quarantined")
        if freshness.get("freshness_state") == "stale":
            active_runtime_blockers.append("kac_latest_artifact_stale")
        return {
            **summary,
            "scorecard_id": "knowledge-artifact-compiler.v0.1",
            "ledger_ref": "PB-2026-05-05-080",
            "source_ref_gate_summary": {
                "latest_allowed": source_gate.get("allowed", True),
                "latest_requested_count": source_gate.get("requested_count", 0),
                "latest_allowed_count": source_gate.get("allowed_count", 0),
                "latest_blocked_count": source_gate.get("blocked_count", 0),
                "latest_blocked_reasons": sorted(
                    {
                        blocked.get("reason")
                        for blocked in (latest.get("blocked_source_refs") or [])
                        if blocked.get("reason")
                    }
                ),
            },
            "artifact_trust_preview_summary": {
                "latest_status": artifact_trust_preview.get("status", "not_scanned"),
                "latest_decision": artifact_trust_preview.get("trust_decision", "not_scanned"),
                "latest_reason_codes": artifact_trust_preview.get("reason_codes", []),
                "persisted": bool(artifact_trust_preview.get("persisted", False)),
            },
            "active_runtime_blockers": active_runtime_blockers,
            "source_documents": [
                "https://venturebeat.com/data/the-rag-era-is-ending-for-agentic-ai-a-new-compilation-stage-knowledge-layer-is-what-comes-next/",
                "https://www.pinecone.io/product/nexus/",
                "docs/compiled_knowledge_artifact_layer.md",
                "docs/research/compiled_knowledge_layer_review_2026-05-05.md",
            ],
            "promotion_readiness": {
                "candidate": True,
                "code_backed_candidate": True,
                "live_control_plane": True,
                "promoted": False,
            },
            "downstream_runtime_gate_coverage": _downstream_runtime_gate_coverage(code_backed_consumers),
            "code_backed_consumers": code_backed_consumers,
            "promotion_blockers": [
                "local eval corpus must prove compiled-vs-raw benefit before promoted canon",
                "RBAC/PII policy must be expanded before enterprise source ingestion",
                "SQLite/indexed storage remains a future upgrade",
            ],
        }

    def artifact(self, artifact_id: str) -> dict[str, Any] | None:
        return self.store.get(artifact_id)

    def artifacts(self, *, limit: int = 50, task_family: str | None = None) -> list[dict[str, Any]]:
        return self.store.list(limit=limit, task_family=task_family)

    def freshness_report(self, artifact_id: str, sources: list[dict[str, Any]]) -> dict[str, Any]:
        artifact = self.artifact(artifact_id)
        report = freshness_report_for(artifact, sources)
        return {
            "artifact_id": artifact_id,
            **report,
        }

    def refresh_freshness(self, artifact_id: str, sources: list[dict[str, Any]]) -> dict[str, Any]:
        artifact = self.artifact(artifact_id)
        report = freshness_report_for(artifact, sources)
        if artifact is not None:
            artifact["freshness"] = {
                **(artifact.get("freshness") or {}),
                **report,
            }
            self.store.save(artifact)
        return {
            "artifact_id": artifact_id,
            **report,
        }

    def query(self, request: KnowledgeRequestContract | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, KnowledgeRequestContract) else KnowledgeRequestContract.model_validate(request)
        artifacts = [artifact for artifact in (self.artifact(context) for context in normalized.contexts) if artifact]
        task_family = normalized.filters.get("task_family")
        if not artifacts and task_family:
            artifacts = self.artifacts(task_family=task_family, limit=3)
        prefer_compiled = bool(normalized.budget.get("prefer_compiled_artifacts", True))
        if artifacts and prefer_compiled:
            selected = artifacts[0]
            source_ref_security_gate = selected.get("source_ref_security_gate") or {}
            artifact_trust_preview = selected.get("artifact_trust_preview") or {}
            freshness_state = selected.get("freshness") or {}
            quarantined = (
                artifact_trust_preview.get("status") == "quarantined"
                or source_ref_security_gate.get("allowed") is False
            )
            stale = freshness_state.get("freshness_state") == "stale"
            response = {
                "status_label": "LOCKED CANON",
                "surface_id": "knowledge-artifact-compiler",
                "intent": normalized.intent,
                "fallback_state": (
                    "compiled_artifact_quarantined"
                    if quarantined
                    else "compiled_artifact_stale"
                    if stale
                    else "compiled_artifact"
                ),
                "runtime_context_allowed": not quarantined and not stale,
                "runtime_context_role": "compiled_artifact_context",
                "mutation_allowed": False,
                "runtime_boundary": "compiled_context_refs_only_no_prompt_weight_node_or_promotion_mutation",
                "allowed_runtime_uses": [
                    "answer_context",
                    "teacher_council_context",
                    "dataset_forge_context",
                    "growth_cycle_context",
                    "recursive_dream_seed_context",
                ],
                "blocked_runtime_uses": [
                    "prompt_mutation",
                    "model_weight_mutation",
                    "node_registry_mutation",
                    "promotion_state_mutation",
                ],
                "artifact_id": selected["artifact_id"],
                "artifact_ref": selected["artifact_id"],
                "quarantine_state": {
                    "quarantined": quarantined,
                    "reason": "artifact_trust_preview_quarantined" if quarantined else "none",
                },
                "freshness_state": freshness_state,
                "artifact_refs": [artifact["artifact_id"] for artifact in artifacts],
                "answer": selected.get("content", {}),
                "citations": _flatten_citations(selected.get("field_citations", {})),
                "confidence": selected.get("confidence", {"overall": 0.0}),
                "conflict_notes": selected.get("conflict_objects", []) if normalized.provenance.get("include_conflict_notes", True) else [],
                "source_ref_security_gate": source_ref_security_gate,
                "blocked_source_refs": selected.get("blocked_source_refs", []),
                "artifact_trust_preview": artifact_trust_preview,
                "raw_retrieval_fallback": {"enabled": False, "reason": "compiled artifact satisfied KRC"},
                "budget": normalized.budget,
                "output_shape": normalized.output_shape,
            }
            return self._record_query(normalized, response)
        fallback_allowed = bool(normalized.budget.get("fallback_to_raw_retrieval", True))
        response = {
            "status_label": "LOCKED CANON",
            "surface_id": "knowledge-artifact-compiler",
            "intent": normalized.intent,
            "fallback_state": "raw_retrieval_fallback" if fallback_allowed else "blocked_missing_compiled_artifact",
            "runtime_context_allowed": False,
            "runtime_context_role": "raw_retrieval_recall_only",
            "mutation_allowed": False,
            "runtime_boundary": "raw_retrieval_recall_only_no_training_growth_dream_or_promotion_use",
            "allowed_runtime_uses": ["answer_recall_fallback"],
            "blocked_runtime_uses": [
                "teacher_council_context",
                "dataset_forge_context",
                "growth_cycle_context",
                "recursive_dream_seed_context",
                "prompt_mutation",
                "model_weight_mutation",
                "node_registry_mutation",
                "promotion_state_mutation",
            ],
            "quarantine_state": {"quarantined": False, "reason": "none"},
            "freshness_state": {"freshness_state": "missing"},
            "artifact_refs": [],
            "answer": {},
            "citations": [],
            "confidence": {"overall": 0.0},
            "conflict_notes": [],
            "raw_retrieval_fallback": {
                "enabled": fallback_allowed,
                "query": normalized.intent,
                "reason": "No compiled artifact matched the KRC contexts or filters.",
            },
            "budget": normalized.budget,
            "output_shape": normalized.output_shape,
        }
        return self._record_query(normalized, response)

    def _record_query(self, request: KnowledgeRequestContract, response: dict[str, Any]) -> dict[str, Any]:
        event = self.store.record_query(
            {
                "schema_version": "kac_query_event.v0.1",
                "intent": request.intent,
                "contexts": request.contexts,
                "filters": request.filters,
                "fallback_state": response.get("fallback_state"),
                "runtime_context_allowed": response.get("runtime_context_allowed"),
                "runtime_context_role": response.get("runtime_context_role"),
                "mutation_allowed": response.get("mutation_allowed", False),
                "artifact_refs": response.get("artifact_refs", []),
                "blocked_source_ref_count": len(response.get("blocked_source_refs", [])),
                "conflict_count": len(response.get("conflict_notes", [])),
                "raw_retrieval_fallback_enabled": bool((response.get("raw_retrieval_fallback") or {}).get("enabled")),
            }
        )
        return {
            **response,
            "query_event_ref": event["event_id"],
            "query_recorded_at": event["recorded_at"],
        }

    def query_events(self, *, limit: int = 50) -> dict[str, Any]:
        events = self.store.query_events(limit=limit)
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "knowledge-artifact-compiler",
            "event_stream": "kac-query-events",
            "query_event_count": len(events),
            "query_events": events,
            "replay_boundary": "query-events-are-append-only-evidence-no-context-mutation",
        }


def _filter_sources(request: KnowledgeCompileRequest, sources: list[Any] | None = None) -> tuple[list[Any], list[dict[str, Any]]]:
    requested_scopes = set(request.scope.get("rbac_scope") or [])
    allowed = []
    excluded = []
    for source in (sources if sources is not None else request.sources):
        source_scopes = set(source.rbac_scope or [])
        if source.permission_state == "blocked":
            excluded.append({"source_ref": source.source_ref, "reason": "permission_state_blocked"})
            continue
        if source.permission_state == "restricted" and not (requested_scopes & source_scopes):
            excluded.append({"source_ref": source.source_ref, "reason": "rbac_scope_not_allowed"})
            continue
        allowed.append(source)
    return allowed, excluded


def _resolve_source_refs(source_refs: list[str], source_root: Path) -> tuple[list[Any], list[dict[str, Any]]]:
    from .artifact_schema import KnowledgeSource

    resolved = []
    excluded = []
    for source_ref in source_refs:
        ref = str(source_ref).replace("\\", "/").lstrip("/")
        if _is_absolute_source_ref(str(source_ref)):
            excluded.append(_blocked_source_ref(source_ref, "source_ref_absolute_path_blocked"))
            continue
        if _is_private_source_ref(ref):
            excluded.append(_blocked_source_ref(source_ref, "source_ref_private_path_blocked"))
            continue
        try:
            path = (source_root / ref).resolve()
        except OSError:
            excluded.append(_blocked_source_ref(source_ref, "source_ref_invalid"))
            continue
        if source_root not in path.parents and path != source_root:
            excluded.append(_blocked_source_ref(source_ref, "source_ref_outside_project_root"))
            continue
        if path.is_dir():
            excluded.append(_blocked_source_ref(source_ref, "source_ref_directory_blocked"))
            continue
        if not path.is_file():
            excluded.append(_blocked_source_ref(source_ref, "source_ref_not_found"))
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            excluded.append(_blocked_source_ref(source_ref, "source_ref_not_utf8_text"))
            continue
        resolved.append(
            KnowledgeSource(
                source_ref=source_ref,
                title=path.name,
                text=text,
                source_url=path.relative_to(source_root).as_posix(),
                permission_state="allowed",
                privacy_class="internal",
                license_state="internal_project_source",
                claims=[{"field": "source_summary", "value": _clip(text, 160)}] if text.strip() else [],
                metadata={"source_kind": "project_local_file"},
            )
        )
    return resolved, excluded


def _source_ref_security_gate(
    requested_refs: list[str], resolved_sources: list[Any], blocked_source_refs: list[dict[str, Any]]
) -> dict[str, Any]:
    blocked_reason_counts: dict[str, int] = {}
    for blocked in blocked_source_refs:
        reason = str(blocked.get("reason") or "source_ref_blocked")
        blocked_reason_counts[reason] = blocked_reason_counts.get(reason, 0) + 1
    return {
        "allowed": not blocked_source_refs,
        "requested_count": len(requested_refs),
        "allowed_count": len(resolved_sources),
        "blocked_count": len(blocked_source_refs),
        "allowed_source_refs": [source.source_ref for source in resolved_sources],
        "blocked_source_refs": blocked_source_refs,
        "blocked_reason_counts": blocked_reason_counts,
        "boundary": "project-local-source-refs-only; private, missing, absolute, and out-of-root refs are blocked before read",
    }


def _blocked_source_ref(source_ref: str, reason: str) -> dict[str, Any]:
    return {
        "source_ref": str(source_ref),
        "reason": reason,
        "source_ref_gate": "blocked_before_read",
    }


def _is_absolute_source_ref(source_ref: str) -> bool:
    candidate = str(source_ref)
    return Path(candidate).is_absolute() or (len(candidate) >= 2 and candidate[1] == ":")


def _is_private_source_ref(source_ref: str) -> bool:
    parts = [part.lower() for part in str(source_ref).replace("\\", "/").split("/") if part]
    return any(part in _PRIVATE_SOURCE_REF_SEGMENTS or part in _PRIVATE_SOURCE_REF_NAMES for part in parts)


def _claims_from_sources(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    claims: list[dict[str, Any]] = []
    for source in sources:
        source_claims = source.get("claims") or []
        if not source_claims and source.get("text"):
            source_claims = [{"field": "source_summary", "value": _clip(source["text"], 160)}]
        for claim in source_claims:
            claims.append({**claim, "source_ref": source["source_ref"]})
    return claims


def _summary_for(task_family: str, sources: list[dict[str, Any]], conflicts: list[dict[str, Any]]) -> str:
    boundary = "Raw retrieval remains available as a lower-level fallback lane."
    conflict_note = f" {len(conflicts)} conflict object(s) require review." if conflicts else ""
    if not sources:
        return f"No authorized sources were available for {task_family}. {boundary}{conflict_note}"
    return f"Compiled {task_family} context from {len(sources)} authorized source(s). {boundary}{conflict_note}"


def _relationships_for(task_family: str, sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "relationship": "compiled_from",
            "from": f"kac:{task_family}",
            "to": source["source_ref"],
        }
        for source in sources
    ]


def _open_questions_for(conflicts: list[dict[str, Any]], excluded_sources: list[dict[str, Any]]) -> list[str]:
    questions = []
    if conflicts:
        questions.append("Resolve deterministic conflict objects before promotion.")
    if excluded_sources:
        questions.append("Review excluded source permissions before widening artifact scope.")
    return questions


def _recommended_actions_for(task_family: str) -> list[dict[str, Any]]:
    return [
        {
            "action": "use_compiled_artifact_for_repeated_agentic_context",
            "task_family": task_family,
            "promotion_state": "candidate",
        },
        {
            "action": "fallback_to_raw_retrieval_when_artifact_missing_or_stale",
            "promotion_state": "allowed_fallback",
        },
    ]


def _field_citations(*, content: dict[str, Any], source_refs: list[str], facts: list[dict[str, Any]]) -> dict[str, list[str]]:
    citations = {"content.summary": list(source_refs)}
    for index, fact in enumerate(facts):
        citations[f"content.facts.{index}"] = list(fact.get("source_refs") or source_refs)
    for index, relationship in enumerate(content.get("relationships") or []):
        citations[f"content.relationships.{index}"] = [relationship["to"]]
    return citations


def _flatten_citations(citations: dict[str, list[str]]) -> list[dict[str, Any]]:
    return [{"field": field, "source_refs": refs} for field, refs in sorted(citations.items())]


def _artifact_summary(artifact: dict[str, Any] | None) -> dict[str, Any] | None:
    if artifact is None:
        return None
    return {
        "artifact_id": artifact.get("artifact_id"),
        "artifact_hash": artifact.get("artifact_hash"),
        "task_family": artifact.get("task_family"),
        "status": artifact.get("status"),
        "source_count": len(artifact.get("source_digests") or []),
        "conflict_count": len(artifact.get("conflict_objects") or []),
        "excluded_source_count": len(artifact.get("excluded_sources") or []),
        "blocked_source_ref_count": len(artifact.get("blocked_source_refs") or []),
        "blocked_source_refs": artifact.get("blocked_source_refs") or [],
        "source_ref_security_gate": artifact.get("source_ref_security_gate") or {},
        "artifact_trust_preview": artifact.get("artifact_trust_preview") or {},
        "control_panel_replay": artifact.get("control_panel_replay") or {},
        "validation": artifact.get("validation"),
        "freshness": artifact.get("freshness"),
    }


def _runtime_context_consumer(consumer_id: str, boundary: str, proof_refs: list[str]) -> dict[str, Any]:
    return {
        "consumer_id": consumer_id,
        "boundary": boundary,
        "mutation_allowed": False,
        "runtime_context_consumer": True,
        "requires_krc_runtime_context_allowed": True,
        "blocks_stale_or_quarantined_context": True,
        "blocks_raw_retrieval_fallback_context": True,
        "enforcement_state": "blocks_disallowed_krc_evidence",
        "runtime_gate_source": "KnowledgeArtifactCompiler.query",
        "proof_refs": proof_refs,
    }


def _code_backed_consumers() -> list[dict[str, Any]]:
    return [
        _runtime_context_consumer(
            "dataset_forge",
            "manifest-example-eval-lineage-refs-only",
            [
                "nexusnet/adapters/dataset_forge.py::_knowledge_artifact_runtime_gate",
                "tests/test_dataset_forge.py::test_dataset_forge_blocks_kac_refs_when_runtime_context_evidence_is_disallowed",
            ],
        ),
        _runtime_context_consumer(
            "hive_model_growth_engine",
            "growth-cycle-teacher-council-dataset-student-genome-lineage",
            [
                "nexusnet/growth/engine.py::_knowledge_artifact_runtime_gate",
                "tests/test_hive_model_growth_engine.py::test_growth_engine_blocks_kac_refs_when_runtime_context_evidence_is_disallowed",
            ],
        ),
        _runtime_context_consumer(
            "teacher_council_review",
            "production-spine-review-context-refs-only",
            [
                "nexusnet/growth/production_spine.py::TeacherCouncilReviewer.review",
                "tests/test_nexusnet_production_spine.py::test_teacher_council_review_blocks_disallowed_kac_runtime_context",
            ],
        ),
        _runtime_context_consumer(
            "recursive_dreaming",
            "dream-scenario-candidate-growth-seed-lineage",
            [
                "nexusnet/growth/production_spine.py::RecursiveDreamCycleRunner.run",
                "nexusnet/dreaming/engine.py::RecursiveDreamEngine.run_cycle",
                "tests/test_nexusnet_production_spine.py::test_recursive_dream_cycle_blocks_disallowed_kac_runtime_context",
                "tests/test_nexusnet_brain.py::test_recursive_dream_engine_rejects_disallowed_kac_runtime_context",
            ],
        ),
        {
            "consumer_id": "deep_replay",
            "boundary": "developer-drilldown-ref-index-only",
            "mutation_allowed": False,
            "runtime_context_consumer": False,
            "replay_only": True,
            "runtime_gate_source": "read-only replay; not runtime context",
            "proof_refs": [
                "nexusnet/growth/production_spine.py::_knowledge_artifact_records",
                "tests/test_nexusnet_production_spine.py::test_deep_replay_bundle_indexes_cycle_artifacts_for_developer_drilldown",
            ],
        },
    ]


def _downstream_runtime_gate_coverage(consumers: list[dict[str, Any]]) -> dict[str, Any]:
    runtime_consumers = [consumer for consumer in consumers if consumer.get("runtime_context_consumer")]
    gated_consumers = [
        consumer
        for consumer in runtime_consumers
        if consumer.get("requires_krc_runtime_context_allowed")
        and consumer.get("blocks_stale_or_quarantined_context")
        and consumer.get("blocks_raw_retrieval_fallback_context")
        and consumer.get("mutation_allowed") is False
    ]
    enforced_consumers = [
        consumer
        for consumer in gated_consumers
        if consumer.get("enforcement_state") == "blocks_disallowed_krc_evidence"
    ]
    proof_refs = sorted(
        {
            str(proof_ref)
            for consumer in enforced_consumers
            for proof_ref in consumer.get("proof_refs", [])
            if proof_ref
        }
    )
    return {
        "required_consumer_count": len(runtime_consumers),
        "gated_consumer_count": len(gated_consumers),
        "enforced_consumer_count": len(enforced_consumers),
        "replay_only_consumer_count": sum(1 for consumer in consumers if consumer.get("replay_only")),
        "all_runtime_consumers_gated": len(runtime_consumers) == len(gated_consumers),
        "all_runtime_consumers_enforced": len(runtime_consumers) == len(enforced_consumers),
        "gate_source": "KnowledgeArtifactCompiler.query",
        "proof_ref_count": len(proof_refs),
        "proof_refs": proof_refs,
    }


def _artifact_trust_preview(artifact_payload: dict[str, Any]) -> dict[str, Any]:
    from nexusnet.security.artifact_trust import ArtifactTrustRegistry

    preview = ArtifactTrustRegistry().preview_knowledge_artifact(artifact_payload)
    return {
        "status": preview.get("status"),
        "trust_decision": preview.get("trust_decision"),
        "reason_codes": preview.get("reason_codes") or [],
        "trust_findings": preview.get("trust_findings") or [],
        "persisted": False,
        "source": "ArtifactTrustRegistry.preview_knowledge_artifact",
    }


def _stable_artifact_hash_payload(payload: dict[str, Any]) -> dict[str, Any]:
    freshness = payload.get("freshness") or {}
    return {
        **payload,
        "freshness": {
            **freshness,
            "compiled_at": "stable_compile_time_excluded_from_artifact_hash",
        },
    }


def _slug(value: str) -> str:
    return "".join(char if char.isalnum() else "_" for char in value.lower()).strip("_") or "task"


def _clip(value: str, limit: int) -> str:
    normalized = " ".join(str(value).split())
    return normalized if len(normalized) <= limit else f"{normalized[: limit - 3]}..."


def _utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

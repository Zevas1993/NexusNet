from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import new_id, utcnow


class ContextGraphService:
    """Governed persistent-context graph records inspired by Graphify.

    V1 is metadata-first: NexusNet plans and tracks graph extraction and assistant
    hooks without installing graphifyy, running model extraction, writing hooks, or
    mutating project files.
    """

    SUPPORTED_CONTENT_KINDS = {"code", "docs", "markdown", "pdf", "image", "audio", "video", "youtube", "office"}
    SUPPORTED_QUERY_MODES = {"query", "path", "explain"}

    def __init__(self, *, artifacts_dir: Path | str, events: Any | None = None):
        self.artifacts_dir = Path(artifacts_dir)
        self.output_dir = self.artifacts_dir / "context-graphs"
        self.query_dir = self.output_dir / "queries"
        self.events = events

    def summary(self, *, limit: int = 100) -> dict[str, Any]:
        records = self._records(limit=limit)
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "record_count": len(records),
            "source_counts": self._counts(records, ("source", "source_name")),
            "content_kind_counts": self._content_kind_counts(records),
            "assistant_platform_counts": self._assistant_platform_counts(records),
            "graphify_patterns_assimilated": [
                "persistent_graph_report_first_context",
                "local_tree_sitter_code_graph",
                "local_media_transcription_candidate",
                "gated_semantic_extraction",
                "incremental_changed_file_updates",
                "assistant_pre_tool_hooks",
                "query_path_explain_interfaces",
            ],
            "execution_allowed": False,
            "mutation_allowed": False,
            "external_package_execution_allowed": False,
            "latest_record": records[0] if records else None,
            "items": records,
        }

    def compact_summary(self, *, limit: int = 50) -> dict[str, Any]:
        payload = self.summary(limit=limit)
        return {
            "status_label": payload["status_label"],
            "record_count": payload["record_count"],
            "content_kind_counts": payload["content_kind_counts"],
            "assistant_platform_counts": payload["assistant_platform_counts"],
            "execution_allowed": False,
            "mutation_allowed": False,
            "external_package_execution_allowed": False,
            "latest_record": payload["latest_record"],
        }

    def plan_index(
        self,
        *,
        source: dict[str, Any] | None = None,
        corpus_root: str,
        content_kinds: list[str] | None = None,
        assistant_platforms: list[str] | None = None,
        graph_ignore_patterns: list[str] | None = None,
        changed_files: list[str] | None = None,
        update_mode: str = "full",
        linked_trace_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        source_payload = self._source(source)
        kinds = self._content_kinds(content_kinds)
        record_id = new_id("ctxgraph")
        trace_ids = list(linked_trace_ids or []) or [f"trace_{record_id}"]
        artifact_path = self.output_dir / f"{record_id}.json"
        record = {
            "record_id": record_id,
            "status": "planned_metadata_only",
            "source": source_payload,
            "corpus": {
                "root": corpus_root,
                "content_kinds": kinds,
                "changed_files": [str(item) for item in (changed_files or [])],
                "update_mode": update_mode,
                "graph_ignore_patterns": [str(item) for item in (graph_ignore_patterns or [])],
                "commit_outputs_recommended": True,
            },
            "extraction_passes": self._extraction_passes(kinds),
            "graph_outputs": self._graph_outputs(corpus_root),
            "cache_policy": {
                "changed_file_cache_supported": True,
                "semantic_extraction_cache_required": True,
                "token_cost_tracking": "planned_metadata_only",
                "cache_artifacts_committable": ["graph_report", "graph_json", "graph_html"],
                "cache_artifacts_local_only": ["cache", "manifest", "cost"],
            },
            "assistant_hooks": self._assistant_hooks(assistant_platforms or ["codex"]),
            "staleness_policy": {
                "incremental_update_supported": True,
                "hook_update_mode": "post_commit_or_branch_switch_candidate",
                "stale_graph_action": "warn_and_require_refresh_plan",
                "changed_files_reprocess_only": update_mode in {"changed_files_only", "incremental", "update"},
            },
            "query_interfaces": self._query_interfaces(),
            "execution_authority": {
                "required": True,
                "service": "execution_authority",
                "lease_endpoint": "/ops/brain/execution-authority/leases/request",
                "required_capabilities": [
                    "external_package_install",
                    "hook_write",
                    "context_graph_semantic_extraction",
                    "context_graph_query",
                ],
                "execution_allowed": False,
                "mutation_allowed": False,
                "reason": "Phase 0 requires a scoped expiring lease before installing graphifyy, writing hooks, invoking semantic extraction, or querying a live graph server.",
            },
            "policy_path": [
                {
                    "stage": "context-graph-assimilation",
                    "decision": "hold",
                    "reason": "plan graph context only; package install, hooks, model extraction, and MCP serving require policy approval",
                }
            ],
            "approval_path": {
                "decision": "not_requested",
                "human_approval_is_not_execution_authority": True,
            },
            "product_sweep_gate_ids": [
                "phase-6-context-assembly",
                "phase-4-security",
                "extension-provenance-gate",
                "operator-surface-truthfulness",
                "license-review",
            ],
            "eval_suite_ids": ["graph_context_regression", "retrieval_provenance", "prompt_injection_red_team"],
            "telemetry_trace_ids": trace_ids,
            "risk_flags": [
                "external_package_execution",
                "assistant_hook_mutation",
                "model_api_data_egress",
                "large_media_transcription_cost",
                "stale_graph_context",
            ],
            "execution_allowed": False,
            "mutation_allowed": False,
            "artifact_path": str(artifact_path),
            "created_at": utcnow().isoformat(),
        }
        self._write(record, artifact_path)
        self._event("context_graph.index_planned", record)
        return {"status_label": "STRONG ACCEPTED DIRECTION", "record": record}

    def query(
        self,
        *,
        graph_record_id: str,
        question: str,
        mode: str = "query",
        linked_trace_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        if mode not in self.SUPPORTED_QUERY_MODES:
            raise ValueError(f"unsupported context graph query mode: {mode}")
        record_id = new_id("ctxgraphq")
        trace_ids = list(linked_trace_ids or []) or [f"trace_{record_id}"]
        artifact_path = self.query_dir / f"{record_id}.json"
        record = {
            "record_id": record_id,
            "graph_record_id": graph_record_id,
            "status": "recorded_metadata_only",
            "mode": mode,
            "question": question,
            "query_interfaces": self._query_interfaces(),
            "execution_authority": {
                "required": True,
                "service": "execution_authority",
                "lease_endpoint": "/ops/brain/execution-authority/leases/request",
                "required_capabilities": ["context_graph_query"],
                "execution_allowed": False,
                "mutation_allowed": False,
                "reason": "Graph traversal remains metadata-only until a scoped query lease is granted.",
            },
            "result": {
                "state": "not_executed",
                "reason": "graph traversal is a governed operation in v1",
                "expected_sources": ["graph_report", "graph_json"],
            },
            "policy_path": [
                {
                    "stage": "context-graph-query",
                    "decision": "hold",
                    "reason": "operator-visible query request recorded without invoking graphify or MCP server",
                }
            ],
            "approval_path": {"decision": "not_requested", "human_approval_is_not_execution_authority": True},
            "product_sweep_gate_ids": ["phase-6-context-assembly", "operator-surface-truthfulness"],
            "eval_suite_ids": ["graph_context_regression"],
            "telemetry_trace_ids": trace_ids,
            "execution_allowed": False,
            "mutation_allowed": False,
            "artifact_path": str(artifact_path),
            "created_at": utcnow().isoformat(),
        }
        self._write(record, artifact_path)
        self._event("context_graph.query_recorded", record)
        return {"status_label": "STRONG ACCEPTED DIRECTION", "record": record}

    def _source(self, source: dict[str, Any] | None) -> dict[str, Any]:
        payload = dict(source or {})
        payload.setdefault("source_name", "Graphify-inspired persistent context graph")
        payload.setdefault("source_url", "https://github.com/safishamsi/graphify")
        payload.setdefault("package_url", "https://pypi.org/project/graphifyy/")
        payload.setdefault("package_name", "graphifyy")
        payload.setdefault("license_posture", "requires_review")
        payload.setdefault("observed_at", utcnow().isoformat())
        return payload

    def _content_kinds(self, content_kinds: list[str] | None) -> list[str]:
        kinds = [str(kind).lower() for kind in (content_kinds or ["code", "docs"])]
        unsupported = [kind for kind in kinds if kind not in self.SUPPORTED_CONTENT_KINDS]
        if unsupported:
            raise ValueError(f"unsupported context graph content kind: {unsupported[0]}")
        return kinds

    def _extraction_passes(self, content_kinds: list[str]) -> list[dict[str, Any]]:
        non_code = [kind for kind in content_kinds if kind not in {"code"}]
        media = [kind for kind in content_kinds if kind in {"audio", "video", "youtube"}]
        return [
            {
                "pass_id": "tree_sitter_code_graph",
                "input_kinds": ["code"] if "code" in content_kinds else [],
                "extracts": ["classes", "functions", "imports", "calls", "docstrings", "rationale_comments"],
                "execution_location": "local",
                "network_required": False,
                "model_required": False,
                "policy_decision": "metadata_only_planned",
                "cost_posture": {"metered": False, "tokens": 0},
            },
            {
                "pass_id": "local_media_transcription",
                "input_kinds": media,
                "extracts": ["transcripts", "timecoded_segments"],
                "execution_location": "local",
                "network_required": False,
                "model_required": "faster_whisper_candidate",
                "policy_decision": "approval_required_for_runtime_install_or_media_download",
                "cost_posture": {"metered": False, "hardware_cost": "local_compute"},
            },
            {
                "pass_id": "semantic_concept_extraction",
                "input_kinds": non_code,
                "extracts": ["concepts", "relationships", "design_rationale", "confidence_tags"],
                "execution_location": "model_provider_when_approved",
                "network_required": True,
                "model_required": True,
                "policy_decision": "approval_required",
                "cost_posture": {"metered": True, "state": "not_started"},
            },
            {
                "pass_id": "community_detection",
                "input_kinds": ["graph_json"],
                "extracts": ["communities", "god_nodes", "surprising_connections"],
                "execution_location": "local",
                "network_required": False,
                "model_required": False,
                "policy_decision": "metadata_only_planned",
                "cost_posture": {"metered": False, "tokens": 0},
            },
        ]

    def _graph_outputs(self, corpus_root: str) -> list[dict[str, Any]]:
        root = str(Path(corpus_root) / "graphify-out")
        return [
            {"artifact_type": "graph_report", "planned_path": str(Path(root) / "GRAPH_REPORT.md"), "committable": True},
            {"artifact_type": "graph_json", "planned_path": str(Path(root) / "graph.json"), "committable": True},
            {"artifact_type": "graph_html", "planned_path": str(Path(root) / "graph.html"), "committable": True},
            {"artifact_type": "cache", "planned_path": str(Path(root) / "cache"), "committable": False},
            {"artifact_type": "manifest", "planned_path": str(Path(root) / "manifest.json"), "committable": False},
        ]

    def _assistant_hooks(self, platforms: list[str]) -> list[dict[str, Any]]:
        items = []
        for platform in [str(item).lower() for item in platforms]:
            if platform == "opencode":
                hook = {
                    "platform": platform,
                    "instruction_files": ["AGENTS.md"],
                    "hook_files": [".opencode/plugins/graphify.js", "opencode.json"],
                    "hook_kind": "tool.execute.before",
                }
            elif platform == "claude-code":
                hook = {
                    "platform": platform,
                    "instruction_files": ["CLAUDE.md"],
                    "hook_files": ["settings.json"],
                    "hook_kind": "PreToolUse",
                }
            elif platform == "codex":
                hook = {
                    "platform": platform,
                    "instruction_files": ["AGENTS.md"],
                    "hook_files": [".codex/hooks.json"],
                    "hook_kind": "PreToolUse",
                }
            else:
                hook = {
                    "platform": platform,
                    "instruction_files": ["AGENTS.md"],
                    "hook_files": [],
                    "hook_kind": "instruction_only",
                }
            hook.update(
                {
                    "purpose": "remind assistant to inspect graph report before broad raw-file search",
                    "governance_state": "planned_review_required",
                    "execution_allowed": False,
                    "mutation_allowed": False,
                }
            )
            items.append(hook)
        return items

    def _query_interfaces(self) -> dict[str, Any]:
        return {
            "cli": {
                "commands": ["graphify query", "graphify path", "graphify explain"],
                "policy_decision": "approval_required",
                "execution_allowed": False,
            },
            "mcp": {
                "tools": ["query_graph", "get_node", "get_neighbors", "shortest_path"],
                "policy_decision": "approval_required",
                "execution_allowed": False,
            },
        }

    def _event(self, event_type: str, record: dict[str, Any]) -> None:
        if not self.events:
            return
        self.events.record(
            event_type=event_type,
            subject=f"context_graph:{record['record_id']}",
            trace_ids=record.get("telemetry_trace_ids") or [],
            payload={
                "record_id": record["record_id"],
                "status": record["status"],
                "execution_allowed": False,
                "mutation_allowed": False,
                "artifact_path": record.get("artifact_path"),
            },
        )

    def _records(self, *, limit: int) -> list[dict[str, Any]]:
        if not self.output_dir.exists():
            return []
        records: list[dict[str, Any]] = []
        paths = [
            path
            for path in self.output_dir.glob("ctxgraph_*.json")
            if path.parent == self.output_dir and not path.name.startswith("ctxgraphq_")
        ]
        for path in sorted(paths, key=lambda item: item.stat().st_mtime, reverse=True):
            try:
                records.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                continue
            if len(records) >= limit:
                break
        return records

    def _write(self, record: dict[str, Any], path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record, indent=2), encoding="utf-8")

    def _counts(self, records: list[dict[str, Any]], path: tuple[str, str]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for record in records:
            value = record.get(path[0], {}).get(path[1]) if isinstance(record.get(path[0]), dict) else None
            key = str(value or "unknown")
            counts[key] = counts.get(key, 0) + 1
        return counts

    def _content_kind_counts(self, records: list[dict[str, Any]]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for record in records:
            for kind in (record.get("corpus") or {}).get("content_kinds", []):
                counts[str(kind)] = counts.get(str(kind), 0) + 1
        return counts

    def _assistant_platform_counts(self, records: list[dict[str, Any]]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for record in records:
            for hook in record.get("assistant_hooks", []):
                platform = str(hook.get("platform") or "unknown")
                counts[platform] = counts.get(platform, 0) + 1
        return counts

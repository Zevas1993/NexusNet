from __future__ import annotations

import hashlib
import json
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

from nexus.schemas import new_id, utcnow
from nexusnet.graph.intelligence import NexusGraphIntelligenceFabric


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
        self.nexusgraph = NexusGraphIntelligenceFabric(artifacts_dir=self.artifacts_dir)
        self.events = events
        self.genesis_memory_admission = None
        self.genesis_federated_outcomes = None

    def summary(self, *, limit: int = 100) -> dict[str, Any]:
        records = self._records(limit=limit)
        query_records = self._query_records(limit=limit)
        nexusgraph_foundation_projection = self._nexusgraph_foundation_projection(limit=limit)
        nexusgraph_impact_receipts = self._nexusgraph_impact_receipts(limit=limit)
        genesis_memory_admission_gate = _aggregate_genesis_memory_admission_gates(records + query_records)
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "record_count": len(records),
            "query_record_count": len(query_records),
            "source_counts": self._counts(records, ("source", "source_name")),
            "content_kind_counts": self._content_kind_counts(records),
            "assistant_platform_counts": self._assistant_platform_counts(records),
            "genesis_memory_admission_gate": genesis_memory_admission_gate,
            "nexusgraph_foundation_projection": nexusgraph_foundation_projection,
            "nexusgraph_impact_receipts": nexusgraph_impact_receipts,
            "nexusgraph_intelligence": self.nexusgraph.summary(),
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
            "latest_query_record": query_records[0] if query_records else None,
            "items": records,
            "query_items": query_records,
        }

    def record_graph_fact(self, **fields: Any) -> dict[str, Any]:
        return self.nexusgraph.record_fact(**fields)

    def query_nexusgraph(self, **fields: Any) -> dict[str, Any]:
        return self.nexusgraph.query(**fields)

    def propose_graph_evolution(self, **fields: Any) -> dict[str, Any]:
        return self.nexusgraph.propose_evolution(**fields)

    def apply_graph_evolution(self, proposal_id: str) -> dict[str, Any]:
        return self.nexusgraph.apply_evolution(proposal_id)

    def rollback_graph_evolution(self, proposal_id: str) -> dict[str, Any]:
        return self.nexusgraph.rollback_evolution(proposal_id)

    def compact_summary(self, *, limit: int = 50) -> dict[str, Any]:
        payload = self.summary(limit=limit)
        return {
            "status_label": payload["status_label"],
            "record_count": payload["record_count"],
            "query_record_count": payload["query_record_count"],
            "content_kind_counts": payload["content_kind_counts"],
            "assistant_platform_counts": payload["assistant_platform_counts"],
            "genesis_memory_admission_gate": payload["genesis_memory_admission_gate"],
            "nexusgraph_foundation_projection": payload["nexusgraph_foundation_projection"],
            "nexusgraph_impact_receipts": payload["nexusgraph_impact_receipts"],
            "execution_allowed": False,
            "mutation_allowed": False,
            "external_package_execution_allowed": False,
            "latest_record": payload["latest_record"],
            "latest_query_record": payload["latest_query_record"],
        }

    def record_genesis_foundation_projection(
        self,
        foundation_status: dict[str, Any],
        *,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        artifact_ref = _safe_graph_ref(
            (foundation_status.get("replay") or {}).get("latest_artifact_ref")
            or _first_ref(foundation_status.get("evidence_refs") or [])
        )
        authority_receipt = (
            foundation_status.get("authority_receipt")
            if isinstance(foundation_status.get("authority_receipt"), dict)
            else {}
        )
        isolation_receipt = (
            foundation_status.get("permission_isolation_receipt")
            if isinstance(foundation_status.get("permission_isolation_receipt"), dict)
            else {}
        )
        neural_projection = (
            foundation_status.get("neural_bus_hive_blackboard_projection")
            if isinstance(foundation_status.get("neural_bus_hive_blackboard_projection"), dict)
            else {}
        )
        typed_event = (
            neural_projection.get("typed_event_envelope")
            if isinstance(neural_projection.get("typed_event_envelope"), dict)
            else {}
        )
        blackboard = (
            neural_projection.get("hive_blackboard_snapshot")
            if isinstance(neural_projection.get("hive_blackboard_snapshot"), dict)
            else {}
        )
        plane_trace = (
            neural_projection.get("plane_trace")
            if isinstance(neural_projection.get("plane_trace"), dict)
            else {}
        )
        layer4 = (
            foundation_status.get("layer4_neural_substrate_ledger_spine")
            if isinstance(foundation_status.get("layer4_neural_substrate_ledger_spine"), dict)
            else {}
        )
        source_refs = _sanitized_graph_refs(
            [
                source.get("source_ref")
                for source in foundation_status.get("source_authority_chain") or []
                if isinstance(source, dict)
            ]
        )
        layer_nodes = [
            {
                "node_ref": _safe_graph_ref(layer.get("layer_id")),
                "label": _safe_graph_ref(layer.get("label")),
                "status": _safe_graph_ref(layer.get("status")),
                "production_approved": layer.get("production_approved") is True,
                "raw_content_included": False,
            }
            for layer in (foundation_status.get("build_layers") or [])
            if isinstance(layer, dict)
        ]
        seed = "|".join(
            _sanitized_graph_refs(
                [
                    artifact_ref,
                    authority_receipt.get("receipt_id"),
                    isolation_receipt.get("receipt_id"),
                    typed_event.get("event_ref"),
                    blackboard.get("snapshot_ref"),
                    plane_trace.get("trace_ref"),
                    layer4.get("source_hive_run_ref"),
                ]
            )
        )
        digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:24]
        projection_id = f"ctxgraph-genesis-foundation::{digest}"
        projection = {
            "schema_version": "nexusnet-context-graph-genesis-foundation-projection-v1",
            "surface_id": "context-graph-genesis-foundation-projection",
            "record_id": projection_id,
            "projection_id": projection_id,
            "status": "live-control-plane",
            "runtime_status": "graph-evidence-captured",
            "source": "genesis-foundation",
            "mother_brain_authority": "NexusBrain",
            "nexusgraph_ownership": "NexusBrain",
            "gitnexus_provider_role": "external-codegraph-provider-not-final-brain",
            "session_ref_digest": _safe_ref(session_id) if session_id else None,
            "foundation_artifact_ref": artifact_ref,
            "authority_receipt_id": _safe_graph_ref(authority_receipt.get("receipt_id")),
            "permission_isolation_receipt_id": _safe_graph_ref(isolation_receipt.get("receipt_id")),
            "neural_bus_event_ref": _safe_graph_ref(typed_event.get("event_ref")),
            "hive_blackboard_snapshot_ref": _safe_graph_ref(blackboard.get("snapshot_ref")),
            "plane_trace_ref": _safe_graph_ref(plane_trace.get("trace_ref")),
            "layer4_substrate_ref": _safe_graph_ref(layer4.get("source_hive_run_ref")),
            "layer4_status": _safe_graph_ref(layer4.get("status")),
            "source_refs": source_refs,
            "build_layer_nodes": layer_nodes,
            "graph_nodes": _sanitized_graph_refs(
                [
                    "NexusBrain",
                    artifact_ref,
                    authority_receipt.get("receipt_id"),
                    isolation_receipt.get("receipt_id"),
                    typed_event.get("event_ref"),
                    blackboard.get("snapshot_ref"),
                    plane_trace.get("trace_ref"),
                    layer4.get("source_hive_run_ref"),
                    *[node.get("node_ref") for node in layer_nodes],
                ]
            ),
            "graph_edges": [
                {
                    "edge_type": "owns",
                    "from_ref": "NexusBrain",
                    "to_ref": artifact_ref,
                    "raw_content_included": False,
                },
                {
                    "edge_type": "authorizes",
                    "from_ref": _safe_graph_ref(authority_receipt.get("receipt_id")),
                    "to_ref": artifact_ref,
                    "raw_content_included": False,
                },
                {
                    "edge_type": "isolates",
                    "from_ref": _safe_graph_ref(isolation_receipt.get("receipt_id")),
                    "to_ref": artifact_ref,
                    "raw_content_included": False,
                },
                {
                    "edge_type": "projects",
                    "from_ref": _safe_graph_ref(typed_event.get("event_ref")),
                    "to_ref": _safe_graph_ref(blackboard.get("snapshot_ref")),
                    "raw_content_included": False,
                },
            ],
            "evidence_refs": _sanitized_graph_refs(
                [
                    artifact_ref,
                    authority_receipt.get("receipt_id"),
                    isolation_receipt.get("receipt_id"),
                    typed_event.get("event_ref"),
                    blackboard.get("snapshot_ref"),
                    plane_trace.get("trace_ref"),
                    layer4.get("source_hive_run_ref"),
                    *(foundation_status.get("evidence_refs") or []),
                ]
            )[:80],
            "created_at": utcnow().isoformat(),
            "execution_allowed": False,
            "mutation_allowed": False,
            "external_package_execution_allowed": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "raw_content_included": False,
            "contains_personal_data": False,
            "privacy_boundary": (
                "sanitized-genesis-foundation-graph-refs-digests-layer-statuses-and-receipt-ids-only-"
                "no-prompts-outputs-session-ids-local-paths-or-raw-canon-text"
            ),
        }
        projection["graph_node_count"] = len(projection["graph_nodes"])
        projection["graph_edge_count"] = len(projection["graph_edges"])
        self._write_genesis_foundation_projection(projection, digest)
        self._event("context_graph.genesis_foundation_projected", projection)
        return projection

    def record_impact_receipt(
        self,
        *,
        source_projection_id: str,
        proposed_change: dict[str, Any],
        gitnexus_evidence: dict[str, Any] | None = None,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        projection = self._find_genesis_foundation_projection(source_projection_id)
        evidence = dict(gitnexus_evidence or {})
        target_refs = _sanitized_graph_refs(proposed_change.get("target_refs") or [])
        changed_file_refs = _sanitized_graph_refs(proposed_change.get("changed_file_refs") or [])
        rollback_plan_ref = _safe_graph_ref(proposed_change.get("rollback_plan"))
        blockers = ["sandbox_eval_required", "admin_approval_required", "rollback_plan_required"]
        affected_graph_refs = _sanitized_graph_refs(
            [
                projection.get("foundation_artifact_ref"),
                projection.get("authority_receipt_id"),
                projection.get("permission_isolation_receipt_id"),
                projection.get("neural_bus_event_ref"),
                projection.get("hive_blackboard_snapshot_ref"),
                projection.get("plane_trace_ref"),
                projection.get("layer4_substrate_ref"),
                *target_refs,
                *changed_file_refs,
            ]
        )
        evidence_refs = _sanitized_graph_refs(
            [
                source_projection_id,
                projection.get("foundation_artifact_ref"),
                evidence.get("target_symbol"),
                *target_refs,
                *changed_file_refs,
            ]
        )[:80]
        seed = json.dumps(
            {
                "source_projection_id": source_projection_id,
                "target_refs": target_refs,
                "changed_file_refs": changed_file_refs,
                "effect_type": _safe_graph_ref(proposed_change.get("effect_type") or "unspecified"),
                "target_symbol": _safe_graph_ref(evidence.get("target_symbol")),
                "impact_risk": _safe_graph_ref(evidence.get("impact_risk") or "missing"),
                "session_ref_digest": _safe_ref(session_id) if session_id else None,
            },
            sort_keys=True,
        )
        digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:24]
        receipt_id = f"ctxgraph-impact::{digest}"
        receipt = {
            "schema_version": "nexusnet-context-graph-impact-receipt-v1",
            "surface_id": "context-graph-impact-receipt",
            "record_id": receipt_id,
            "receipt_id": receipt_id,
            "status": "blocked-review-required",
            "runtime_status": "impact-evidence-captured",
            "source": "context-graph-impact-receipt",
            "source_projection_id": source_projection_id,
            "mother_brain_authority": "NexusBrain",
            "nexusgraph_ownership": "NexusBrain",
            "session_ref_digest": _safe_ref(session_id) if session_id else None,
            "proposed_change": {
                "effect_type": _safe_graph_ref(proposed_change.get("effect_type") or "unspecified"),
                "target_refs": target_refs,
                "changed_file_refs": changed_file_refs,
                "change_summary_ref": _safe_graph_ref(proposed_change.get("change_summary")),
                "rollback_plan_ref": rollback_plan_ref,
                "sandbox_command_ref": _safe_graph_ref(proposed_change.get("sandbox_command")),
                "raw_content_included": False,
            },
            "gitnexus_provider_evidence": {
                "provider": _safe_graph_ref(evidence.get("provider") or "GitNexus"),
                "provider_role": "external-codegraph-provider-not-final-brain",
                "provider_status": "provided" if evidence else "not-provided",
                "indexed_repo": _safe_graph_ref(evidence.get("indexed_repo") or "NexusNet"),
                "target_symbol": _safe_graph_ref(evidence.get("target_symbol")),
                "impact_risk": _safe_graph_ref(evidence.get("impact_risk") or "missing"),
                "direct_callers": _safe_int(evidence.get("direct_callers")),
                "affected_process_count": len(evidence.get("affected_processes") or []),
                "raw_content_included": False,
            },
            "authority_gate": {
                "decision_authority": "NexusBrain",
                "decision": "review-required",
                "admin_approval_required": True,
                "production_action_allowed": False,
                "blockers": blockers,
                "raw_content_included": False,
            },
            "sandbox_governance": {
                "closed_sandbox_required": True,
                "sandbox_eval_status": "not-run",
                "sandbox_required_before_mutation": True,
                "raw_content_included": False,
            },
            "rollback_governance": {
                "rollback_required": True,
                "rollback_plan_ref": rollback_plan_ref,
                "rollback_verified": False,
                "raw_content_included": False,
            },
            "graph_impact": {
                "source_projection_id": source_projection_id,
                "foundation_artifact_ref": projection.get("foundation_artifact_ref"),
                "affected_graph_refs": affected_graph_refs,
                "affected_node_count": len(affected_graph_refs),
                "affected_edge_count": _safe_int(projection.get("graph_edge_count")),
                "raw_content_included": False,
            },
            "blockers": blockers,
            "evidence_refs": evidence_refs,
            "artifact_storage_ref": f"context-graphs/impact-receipts/{digest}.json",
            "created_at": utcnow().isoformat(),
            "execution_allowed": False,
            "mutation_allowed": False,
            "external_package_execution_allowed": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "raw_content_included": False,
            "contains_personal_data": False,
            "privacy_boundary": (
                "sanitized-context-graph-impact-receipt-digests-statuses-target-refs-and-provider-metadata-only-"
                "no-prompts-session-ids-local-paths-raw-diffs-or-raw-canon-text"
            ),
        }
        self._write_impact_receipt(receipt, digest)
        self._event("context_graph.impact_receipt_recorded", receipt)
        return receipt

    def run_impact_receipt_sandbox_eval(
        self,
        receipt_id: str,
        *,
        command: str,
        project_root: Path | str,
        timeout_seconds: int = 60,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        receipt, receipt_path = self._find_impact_receipt(receipt_id)
        root = Path(project_root).resolve()
        argv = _allowlisted_context_graph_pytest_argv(command)
        bounded_timeout = max(1, min(int(timeout_seconds or 60), 120))
        started_at = utcnow().isoformat()
        run_id = hashlib.sha256(f"{receipt_id}|{command}|{started_at}".encode("utf-8")).hexdigest()[:16]
        artifact_ref = f"context-graphs/sandbox-evals/{run_id}.json"
        artifact_path = self.artifacts_dir / artifact_ref
        sandbox_workspace = _context_graph_sandbox_workspace(receipt_id, run_id)
        if sandbox_workspace.exists():
            shutil.rmtree(sandbox_workspace)
        artifact_path.parent.mkdir(parents=True, exist_ok=True)

        active_pre_manifest = _context_graph_manifest(root)
        phase_timings: dict[str, float] = {}
        phase_started = time.perf_counter()
        shutil.copytree(root, sandbox_workspace, ignore=_context_graph_sandbox_copy_ignore)
        phase_timings["copy_seconds"] = round(time.perf_counter() - phase_started, 4)

        sandbox_pre_manifest = _context_graph_manifest(sandbox_workspace)
        sandbox_argv = [sys.executable, "-m", "pytest", *argv[3:]]
        phase_started = time.perf_counter()
        try:
            completed = subprocess.run(
                sandbox_argv,
                cwd=sandbox_workspace,
                capture_output=True,
                text=True,
                timeout=bounded_timeout,
                shell=False,
            )
            returncode = int(completed.returncode)
            stdout = completed.stdout or ""
            stderr = completed.stderr or ""
            timed_out = False
        except subprocess.TimeoutExpired as exc:
            returncode = 124
            stdout = str(exc.stdout or "")
            stderr = str(exc.stderr or "")
            timed_out = True
        phase_timings["pytest_seconds"] = round(time.perf_counter() - phase_started, 4)

        sandbox_post_manifest = _context_graph_manifest(sandbox_workspace)
        active_post_manifest = _context_graph_manifest(root)
        sandbox_diff = _context_graph_manifest_diff(sandbox_pre_manifest, sandbox_post_manifest)
        active_diff = _context_graph_manifest_diff(active_pre_manifest, active_post_manifest)
        unsafe_sandbox_changes = [
            path for path in sandbox_diff["changed_paths"] if not _context_graph_allowed_sandbox_change(path)
        ]
        active_project_source_mutated = bool(active_diff["changed_paths"])
        passed = returncode == 0 and not timed_out and not unsafe_sandbox_changes and not active_project_source_mutated
        completed_at = utcnow().isoformat()
        eval_run_id = f"ctxgraph-impact-sandbox::{run_id}"
        sandbox_eval = {
            "schema_version": "nexusnet-context-graph-impact-sandbox-eval-v1",
            "surface_id": "context-graph-impact-sandbox-eval",
            "record_id": eval_run_id,
            "eval_run_id": eval_run_id,
            "receipt_id": receipt_id,
            "status": "passed" if passed else "failed",
            "passed": passed,
            "returncode": returncode,
            "failure_count": 0 if passed else 1,
            "timed_out": timed_out,
            "command_ref": _safe_graph_ref(command),
            "argv_refs": _sanitized_graph_refs(sandbox_argv),
            "stdout_ref": _safe_ref(stdout),
            "stderr_ref": _safe_ref(stderr),
            "started_at": started_at,
            "completed_at": completed_at,
            "phase_timings": phase_timings,
            "sandbox": {
                "mode": "isolated-filesystem-copy-allowlisted-pytest",
                "shell_used": False,
                "active_project_root_digest": _safe_ref(root),
                "sandbox_workspace_ref": _safe_ref(sandbox_workspace),
                "active_project_source_mutated": active_project_source_mutated,
                "active_project_source_change_count": active_diff["changed_file_count"],
                "active_production_mutated": False,
                "write_scope": "sandbox-copy-only-with-active-source-manifest-check",
                "network_required": False,
            },
            "allowlist": {
                "runner": "pytest",
                "allowed_command_prefix": "python -m pytest",
                "allowed_targets": ["tests/*.py", "tests/**/*.py"],
                "allowed_options": ["-q", "--quiet", "--maxfail=1"],
                "allowed_write_scopes": [".pytest_cache/", "**/__pycache__/", "runtime/", "artifacts/"],
            },
            "sandbox_diff": {
                "changed_file_count": sandbox_diff["changed_file_count"],
                "unsafe_change_count": len(unsafe_sandbox_changes),
                "unsafe_change_refs": _sanitized_graph_refs(unsafe_sandbox_changes[:20]),
            },
            "active_project_diff": {
                "changed_file_count": active_diff["changed_file_count"],
                "changed_refs": _sanitized_graph_refs(active_diff["changed_paths"][:20]),
            },
            "artifact_storage_ref": artifact_ref,
            "raw_content_included": False,
            "contains_personal_data": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "privacy_boundary": (
                "sanitized-context-graph-sandbox-eval-command-status-digests-and-manifest-counts-only-"
                "no-stdout-stderr-local-paths-session-ids-prompts-or-raw-diffs"
            ),
        }
        sandbox_eval["federated_outcome_packet"] = self._record_federated_outcome(
            outcome_type=(
                "context_graph_impact_sandbox_eval_passed"
                if passed
                else "context_graph_impact_sandbox_eval_failed"
            ),
            session_id=session_id,
            receipt=receipt,
            sandbox_eval_run_id=eval_run_id,
            evidence_refs=[
                receipt_id,
                eval_run_id,
                receipt.get("source_projection_id"),
                receipt.get("artifact_storage_ref"),
            ],
        )
        artifact_path.write_text(json.dumps(_public_record(sandbox_eval), indent=2), encoding="utf-8")

        receipt["latest_sandbox_eval_run"] = _public_record(sandbox_eval)
        receipt["sandbox_eval_history"] = [_public_record(sandbox_eval), *(receipt.get("sandbox_eval_history") or [])][
            :20
        ]
        blockers = list(receipt.get("blockers") or [])
        if passed:
            blockers = [blocker for blocker in blockers if blocker != "sandbox_eval_required"]
        elif "sandbox_eval_required" not in blockers:
            blockers.insert(0, "sandbox_eval_required")
        receipt["blockers"] = blockers
        if isinstance(receipt.get("authority_gate"), dict):
            receipt["authority_gate"]["blockers"] = blockers
        if isinstance(receipt.get("sandbox_governance"), dict):
            receipt["sandbox_governance"].update(
                {
                    "sandbox_eval_status": sandbox_eval["status"],
                    "latest_eval_run_id": eval_run_id,
                    "closed_sandbox_required": True,
                    "sandbox_required_before_mutation": True,
                    "raw_content_included": False,
                }
            )
        receipt["runtime_status"] = "sandbox-evaluated" if passed else "sandbox-eval-failed"
        receipt["updated_at"] = completed_at
        receipt_path.write_text(json.dumps(_public_record(receipt), indent=2), encoding="utf-8")
        self._event("context_graph.impact_receipt_sandbox_evaluated", receipt)
        return {"receipt": _public_record(receipt), "sandbox_eval": _public_record(sandbox_eval)}

    def approve_impact_receipt(
        self,
        receipt_id: str,
        *,
        approved_by: str,
        approval_ref: str | None = None,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        receipt, receipt_path = self._find_impact_receipt(receipt_id)
        latest_eval = (
            receipt.get("latest_sandbox_eval_run")
            if isinstance(receipt.get("latest_sandbox_eval_run"), dict)
            else {}
        )
        if latest_eval.get("passed") is not True:
            raise ValueError("passing sandbox eval is required before context graph impact admin approval")
        approved_at = utcnow().isoformat()
        safe_approval_ref = _safe_graph_ref(approval_ref) or f"context-graph-approval::{_digest_ref(receipt_id, approved_at)}"
        approval = {
            "schema_version": "nexusnet-context-graph-impact-admin-approval-v1",
            "surface_id": "context-graph-impact-admin-approval",
            "record_id": safe_approval_ref,
            "approval_ref": safe_approval_ref,
            "receipt_id": receipt_id,
            "status": "admin-approved",
            "operator_approved": True,
            "approver_digest": "sha256:" + hashlib.sha256(str(approved_by or "").encode("utf-8")).hexdigest()[:16],
            "approved_at": approved_at,
            "safe_apply_allowed": True,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "raw_content_included": False,
            "contains_personal_data": False,
            "privacy_boundary": (
                "sanitized-context-graph-admin-approval-ref-and-approver-digest-only-"
                "no-admin-identity-session-id-or-raw-content"
            ),
        }
        blockers = [
            blocker
            for blocker in list(receipt.get("blockers") or [])
            if blocker not in {"admin_approval_required", "rollback_plan_required"}
        ]
        receipt["blockers"] = blockers
        receipt["latest_approval"] = approval
        if isinstance(receipt.get("authority_gate"), dict):
            receipt["authority_gate"].update(
                {
                    "decision": "admin-approved-shadow-apply-authorized",
                    "operator_approved": True,
                    "admin_approval_required": False,
                    "safe_apply_allowed": True,
                    "production_action_allowed": False,
                    "blockers": blockers,
                    "raw_content_included": False,
                }
            )
        receipt["status"] = "admin-approved"
        receipt["runtime_status"] = "admin-approved-pending-shadow-apply"
        receipt["updated_at"] = approved_at
        receipt_path.write_text(json.dumps(_public_record(receipt), indent=2), encoding="utf-8")
        self._event("context_graph.impact_receipt_admin_approved", receipt)
        return _public_record(approval)

    def apply_impact_receipt(self, receipt_id: str, *, session_id: str | None = None) -> dict[str, Any]:
        receipt, receipt_path = self._find_impact_receipt(receipt_id)
        latest_eval = (
            receipt.get("latest_sandbox_eval_run")
            if isinstance(receipt.get("latest_sandbox_eval_run"), dict)
            else {}
        )
        if latest_eval.get("passed") is not True:
            raise ValueError("passing sandbox eval is required before context graph impact apply")
        authority_gate = receipt.get("authority_gate") if isinstance(receipt.get("authority_gate"), dict) else {}
        if authority_gate.get("operator_approved") is not True:
            raise ValueError("admin approval is required before context graph impact apply")
        rollback_plan_ref = (receipt.get("rollback_governance") or {}).get("rollback_plan_ref")
        if not rollback_plan_ref:
            raise ValueError("rollback plan is required before context graph impact apply")
        applied_at = utcnow().isoformat()
        apply_id = f"ctxgraph-impact-apply::{_digest_ref(receipt_id, applied_at)}"
        safe_file_ref = f"context-graphs/safe-files/{_safe_filename(receipt_id)}.json"
        safe_file_path = self.artifacts_dir / safe_file_ref
        safe_file_path.parent.mkdir(parents=True, exist_ok=True)
        previous_exists = safe_file_path.exists()
        backup_ref = ""
        if previous_exists:
            backup_ref = f"context-graphs/rollbacks/{_safe_filename(apply_id)}-previous.json"
            backup_path = self.artifacts_dir / backup_ref
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            backup_path.write_text(safe_file_path.read_text(encoding="utf-8"), encoding="utf-8")
        safe_payload = {
            "schema_version": "nexusnet-context-graph-impact-shadow-safe-file-v1",
            "surface_id": "context-graph-impact-shadow-safe-file",
            "receipt_id": receipt_id,
            "source_projection_id": receipt.get("source_projection_id"),
            "apply_id": apply_id,
            "status": "applied-shadow-safe-file",
            "target_refs": (receipt.get("proposed_change") or {}).get("target_refs") or [],
            "changed_file_refs": (receipt.get("proposed_change") or {}).get("changed_file_refs") or [],
            "sandbox_eval_run_id": latest_eval.get("eval_run_id"),
            "approval_ref": (receipt.get("latest_approval") or {}).get("approval_ref")
            if isinstance(receipt.get("latest_approval"), dict)
            else None,
            "rollback_plan_ref": rollback_plan_ref,
            "applied_at": applied_at,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "raw_content_included": False,
            "contains_personal_data": False,
        }
        safe_file_path.write_text(json.dumps(_public_record(safe_payload), indent=2), encoding="utf-8")
        application = {
            "schema_version": "nexusnet-context-graph-impact-application-v1",
            "surface_id": "context-graph-impact-application",
            "record_id": apply_id,
            "apply_id": apply_id,
            "receipt_id": receipt_id,
            "status": "applied-shadow-safe-file",
            "safe_file_ref": safe_file_ref,
            "previous_safe_file_existed": previous_exists,
            "previous_safe_file_backup_ref": backup_ref,
            "sandbox_eval_run_id": latest_eval.get("eval_run_id"),
            "approval_ref": (receipt.get("latest_approval") or {}).get("approval_ref")
            if isinstance(receipt.get("latest_approval"), dict)
            else None,
            "rollback_ref": f"context-graph-rollback::{_digest_ref(apply_id, receipt_id)}",
            "applied_at": applied_at,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "raw_content_included": False,
            "contains_personal_data": False,
            "privacy_boundary": (
                "sanitized-context-graph-shadow-safe-file-apply-ids-and-artifact-refs-only-"
                "no-source-mutation-local-paths-session-ids-or-raw-diffs"
            ),
        }
        application["federated_outcome_packet"] = self._record_federated_outcome(
            outcome_type="context_graph_impact_applied",
            session_id=session_id,
            receipt=receipt,
            sandbox_eval_run_id=latest_eval.get("eval_run_id"),
            apply_id=apply_id,
            evidence_refs=[
                receipt_id,
                apply_id,
                safe_file_ref,
                latest_eval.get("eval_run_id"),
                application.get("approval_ref"),
            ],
        )
        receipt["latest_application"] = _public_record(application)
        receipt["application_history"] = [_public_record(application), *(receipt.get("application_history") or [])][:20]
        receipt["status"] = "applied-shadow-safe-file"
        receipt["runtime_status"] = "shadow-safe-file-applied"
        receipt["blockers"] = []
        if isinstance(receipt.get("authority_gate"), dict):
            receipt["authority_gate"]["blockers"] = []
        receipt["updated_at"] = applied_at
        receipt_path.write_text(json.dumps(_public_record(receipt), indent=2), encoding="utf-8")
        self._event("context_graph.impact_receipt_shadow_applied", receipt)
        return _public_record(application)

    def rollback_impact_receipt(
        self,
        receipt_id: str,
        *,
        reason: str | None = None,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        receipt, receipt_path = self._find_impact_receipt(receipt_id)
        application = (
            receipt.get("latest_application")
            if isinstance(receipt.get("latest_application"), dict)
            else {}
        )
        if not application:
            raise ValueError("context graph impact apply is required before rollback")
        safe_file_ref = str(application.get("safe_file_ref") or "")
        safe_file_path = self.artifacts_dir / safe_file_ref
        backup_ref = str(application.get("previous_safe_file_backup_ref") or "")
        if application.get("previous_safe_file_existed") is True and backup_ref:
            backup_path = self.artifacts_dir / backup_ref
            if backup_path.exists():
                safe_file_path.parent.mkdir(parents=True, exist_ok=True)
                safe_file_path.write_text(backup_path.read_text(encoding="utf-8"), encoding="utf-8")
                rollback_restored = True
            else:
                rollback_restored = False
        else:
            if safe_file_path.exists():
                safe_file_path.unlink()
            rollback_restored = True
        rolled_back_at = utcnow().isoformat()
        rollback_id = f"ctxgraph-impact-rollback::{_digest_ref(receipt_id, rolled_back_at)}"
        rollback = {
            "schema_version": "nexusnet-context-graph-impact-rollback-v1",
            "surface_id": "context-graph-impact-rollback",
            "record_id": rollback_id,
            "rollback_id": rollback_id,
            "receipt_id": receipt_id,
            "apply_id": application.get("apply_id"),
            "status": "rolled-back" if rollback_restored else "rollback-blocked",
            "reason_ref": _safe_graph_ref(reason),
            "safe_file_ref": safe_file_ref,
            "rollback_restored": rollback_restored,
            "rolled_back_at": rolled_back_at,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "raw_content_included": False,
            "contains_personal_data": False,
            "privacy_boundary": (
                "sanitized-context-graph-rollback-ids-statuses-and-safe-file-refs-only-"
                "no-reason-text-session-id-local-paths-or-raw-content"
            ),
        }
        rollback["federated_outcome_packet"] = self._record_federated_outcome(
            outcome_type="context_graph_impact_rolled_back",
            session_id=session_id,
            receipt=receipt,
            apply_id=application.get("apply_id"),
            rollback_id=rollback_id,
            evidence_refs=[
                receipt_id,
                application.get("apply_id"),
                rollback_id,
                safe_file_ref,
            ],
        )
        receipt["latest_rollback"] = _public_record(rollback)
        receipt["rollback_history"] = [_public_record(rollback), *(receipt.get("rollback_history") or [])][:20]
        receipt["status"] = rollback["status"]
        receipt["runtime_status"] = "shadow-safe-file-rolled-back" if rollback_restored else "rollback-blocked"
        receipt["active_production_mutated"] = False
        receipt["updated_at"] = rolled_back_at
        receipt_path.write_text(json.dumps(_public_record(receipt), indent=2), encoding="utf-8")
        self._event("context_graph.impact_receipt_rolled_back", receipt)
        return _public_record(rollback)

    def _record_federated_outcome(
        self,
        *,
        outcome_type: str,
        receipt: dict[str, Any],
        session_id: str | None = None,
        sandbox_eval_run_id: str | None = None,
        apply_id: str | None = None,
        rollback_id: str | None = None,
        evidence_refs: list[Any] | None = None,
    ) -> dict[str, Any]:
        recorder = getattr(self.genesis_federated_outcomes, "record_outcome", None)
        if not callable(recorder):
            return {
                "schema_version": "nexusnet-genesis-federated-outcome-packet-v1",
                "surface_id": "genesis-federated-outcome-packet",
                "status": "not-configured",
                "outcome_type": outcome_type,
                "raw_content_included": False,
                "contains_personal_data": False,
                "active_production_mutation_allowed": False,
                "active_production_mutated": False,
            }
        return recorder(
            outcome_type=outcome_type,
            source_surface_id="context-graph-impact-receipts",
            source_event_ref=str(receipt.get("receipt_id") or ""),
            source_event_type="context_graph.impact_receipt",
            session_id=session_id,
            sandbox_eval_run_id=sandbox_eval_run_id,
            apply_id=apply_id,
            rollback_id=rollback_id,
            evidence_refs=_sanitized_graph_refs(
                [
                    receipt.get("receipt_id"),
                    receipt.get("source_projection_id"),
                    receipt.get("artifact_storage_ref"),
                    sandbox_eval_run_id,
                    apply_id,
                    rollback_id,
                    *(evidence_refs or []),
                ]
            ),
            status="context-graph-impact-outcome-recorded",
        )

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
        session_id: str | None = None,
    ) -> dict[str, Any]:
        raw_source = dict(source or {})
        source_payload = self._source(raw_source)
        kinds = self._content_kinds(content_kinds)
        record_id = new_id("ctxgraph")
        trace_ids = _sanitized_ref_list(list(linked_trace_ids or []) or [f"trace_{record_id}"])
        artifact_ref = f"context-graphs/{record_id}.json"
        artifact_path = self.artifacts_dir / artifact_ref
        genesis_admission = _record_genesis_context_graph_admission(
            self,
            session_id=session_id or _context_graph_session_id(raw_source, linked_trace_ids),
            ingress_route="context-graph-index-plan",
            content=_context_graph_plan_content(
                source=raw_source,
                corpus_root=corpus_root,
                changed_files=changed_files or [],
                graph_ignore_patterns=graph_ignore_patterns or [],
                content_kinds=kinds,
            ),
            metadata=_context_graph_plan_admission_metadata(raw_source),
        )
        genesis_gate = _genesis_memory_admission_gate(
            ingress_route="context-graph-index-plan",
            decisions=[genesis_admission] if genesis_admission else [],
        )
        blocked_by_genesis = bool(genesis_admission) and genesis_admission.get("memory_write_allowed") is not True
        record = {
            "record_id": record_id,
            "status": "blocked_by_genesis_memory_admission" if blocked_by_genesis else "planned_metadata_only",
            "source": source_payload,
            "corpus": {
                "root_ref": _safe_ref(corpus_root),
                "root_sanitized": True,
                "content_kinds": kinds,
                "changed_file_refs": _sanitized_ref_list(changed_files or []),
                "update_mode": update_mode,
                "graph_ignore_pattern_refs": _sanitized_ref_list(graph_ignore_patterns or []),
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
            "genesis_memory_admission": genesis_admission,
            "genesis_memory_admission_gate": genesis_gate,
            "execution_allowed": False,
            "mutation_allowed": False,
            "artifact_storage_ref": artifact_ref,
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
        session_id: str | None = None,
    ) -> dict[str, Any]:
        if mode not in self.SUPPORTED_QUERY_MODES:
            raise ValueError(f"unsupported context graph query mode: {mode}")
        record_id = new_id("ctxgraphq")
        trace_ids = _sanitized_ref_list(list(linked_trace_ids or []) or [f"trace_{record_id}"])
        artifact_ref = f"context-graphs/queries/{record_id}.json"
        artifact_path = self.artifacts_dir / artifact_ref
        genesis_admission = _record_genesis_context_graph_admission(
            self,
            session_id=session_id or _context_graph_session_id({}, linked_trace_ids),
            ingress_route="context-graph-query",
            content=question,
            metadata={"source_kind": "context-graph-query", "privacy_class": "unspecified"},
        )
        genesis_gate = _genesis_memory_admission_gate(
            ingress_route="context-graph-query",
            decisions=[genesis_admission] if genesis_admission else [],
        )
        blocked_by_genesis = bool(genesis_admission) and genesis_admission.get("memory_write_allowed") is not True
        record = {
            "record_id": record_id,
            "graph_record_id": graph_record_id,
            "status": "blocked_by_genesis_memory_admission" if blocked_by_genesis else "recorded_metadata_only",
            "mode": mode,
            "question_ref": _safe_ref(question),
            "question_sanitized": True,
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
            "genesis_memory_admission": genesis_admission,
            "genesis_memory_admission_gate": genesis_gate,
            "execution_allowed": False,
            "mutation_allowed": False,
            "artifact_storage_ref": artifact_ref,
            "created_at": utcnow().isoformat(),
        }
        self._write(record, artifact_path)
        self._event("context_graph.query_recorded", record)
        return {"status_label": "STRONG ACCEPTED DIRECTION", "record": record}

    def _source(self, source: dict[str, Any] | None) -> dict[str, Any]:
        payload = _sanitize_public_mapping(dict(source or {}))
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
        return [
            {"artifact_type": "graph_report", "planned_artifact_ref": "graphify-out/GRAPH_REPORT.md", "committable": True},
            {"artifact_type": "graph_json", "planned_artifact_ref": "graphify-out/graph.json", "committable": True},
            {"artifact_type": "graph_html", "planned_artifact_ref": "graphify-out/graph.html", "committable": True},
            {"artifact_type": "cache", "planned_artifact_ref": "graphify-out/cache", "committable": False},
            {"artifact_type": "manifest", "planned_artifact_ref": "graphify-out/manifest.json", "committable": False},
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
                "artifact_storage_ref": record.get("artifact_storage_ref"),
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
                records.append(_public_record(json.loads(path.read_text(encoding="utf-8"))))
            except (OSError, json.JSONDecodeError):
                continue
            if len(records) >= limit:
                break
        return records

    def _query_records(self, *, limit: int) -> list[dict[str, Any]]:
        if not self.query_dir.exists():
            return []
        records: list[dict[str, Any]] = []
        for path in sorted(self.query_dir.glob("ctxgraphq_*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
            try:
                records.append(_public_record(json.loads(path.read_text(encoding="utf-8"))))
            except (OSError, json.JSONDecodeError):
                continue
            if len(records) >= limit:
                break
        return records

    def _nexusgraph_foundation_projection(self, *, limit: int) -> dict[str, Any]:
        records = self._genesis_foundation_projection_records(limit=limit)
        latest = records[0] if records else None
        return {
            "schema_version": "nexusnet-context-graph-genesis-foundation-projections-v1",
            "surface_id": "context-graph-genesis-foundation-projections",
            "status": "live-control-plane" if latest else "not-observed",
            "honest_status_label": (
                "nexusbrain-owned-genesis-foundation-graph-projection-live-control-plane"
                if latest
                else "nexusbrain-owned-genesis-foundation-graph-projection-not-observed"
            ),
            "source": "genesis-foundation" if latest else None,
            "mother_brain_authority": "NexusBrain",
            "nexusgraph_ownership": "NexusBrain",
            "gitnexus_provider_role": "external-codegraph-provider-not-final-brain",
            "projection_count": len(records),
            "latest_projection_id": latest.get("projection_id") if latest else None,
            "latest_projection": latest,
            "recent_projections": records[:20],
            "execution_allowed": False,
            "mutation_allowed": False,
            "external_package_execution_allowed": False,
            "active_production_mutation_allowed": False,
            "raw_content_included": False,
            "contains_personal_data": False,
        }

    def _genesis_foundation_projection_records(self, *, limit: int) -> list[dict[str, Any]]:
        projection_dir = self.output_dir / "genesis-foundation"
        if not projection_dir.exists():
            return []
        records: list[dict[str, Any]] = []
        for path in sorted(projection_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
            try:
                record = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(record, dict) and record.get("surface_id") == "context-graph-genesis-foundation-projection":
                records.append(_public_record(record))
            if len(records) >= limit:
                break
        return records

    def _find_genesis_foundation_projection(self, projection_id: str) -> dict[str, Any]:
        for record in self._genesis_foundation_projection_records(limit=1000):
            if record.get("projection_id") == projection_id:
                return record
        raise KeyError(projection_id)

    def _find_impact_receipt(self, receipt_id: str) -> tuple[dict[str, Any], Path]:
        receipt_dir = self.output_dir / "impact-receipts"
        if not receipt_dir.exists():
            raise KeyError(receipt_id)
        for path in receipt_dir.glob("*.json"):
            try:
                record = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(record, dict) and record.get("receipt_id") == receipt_id:
                return _public_record(record), path
        raise KeyError(receipt_id)

    def _nexusgraph_impact_receipts(self, *, limit: int) -> dict[str, Any]:
        records = self._impact_receipt_records(limit=limit)
        latest = records[0] if records else None
        sandbox_evals = [
            record.get("latest_sandbox_eval_run")
            for record in records
            if isinstance(record.get("latest_sandbox_eval_run"), dict)
        ]
        latest_sandbox_eval = sandbox_evals[0] if sandbox_evals else None
        approvals = [
            record.get("latest_approval")
            for record in records
            if isinstance(record.get("latest_approval"), dict)
        ]
        applications = [
            record.get("latest_application")
            for record in records
            if isinstance(record.get("latest_application"), dict)
        ]
        rollbacks = [
            record.get("latest_rollback")
            for record in records
            if isinstance(record.get("latest_rollback"), dict)
        ]
        return {
            "schema_version": "nexusnet-context-graph-impact-receipts-v1",
            "surface_id": "context-graph-impact-receipts",
            "status": "live-control-plane" if latest else "not-observed",
            "honest_status_label": (
                "nexusbrain-owned-context-graph-impact-receipts-live-control-plane"
                if latest
                else "nexusbrain-owned-context-graph-impact-receipts-not-observed"
            ),
            "mother_brain_authority": "NexusBrain",
            "nexusgraph_ownership": "NexusBrain",
            "gitnexus_provider_role": "external-codegraph-provider-not-final-brain",
            "receipt_count": len(records),
            "latest_receipt_id": latest.get("receipt_id") if latest else None,
            "latest_receipt": latest,
            "recent_receipts": records[:20],
            "sandbox_eval_count": len(sandbox_evals),
            "latest_sandbox_eval_run": latest_sandbox_eval,
            "approval_count": len(approvals),
            "latest_approval": approvals[0] if approvals else None,
            "application_count": len(applications),
            "latest_application": applications[0] if applications else None,
            "rollback_count": len(rollbacks),
            "latest_rollback": rollbacks[0] if rollbacks else None,
            "admin_approval_required": True,
            "closed_sandbox_required": True,
            "rollback_required": True,
            "execution_allowed": False,
            "mutation_allowed": False,
            "external_package_execution_allowed": False,
            "active_production_mutation_allowed": False,
            "raw_content_included": False,
            "contains_personal_data": False,
        }

    def _impact_receipt_records(self, *, limit: int) -> list[dict[str, Any]]:
        receipt_dir = self.output_dir / "impact-receipts"
        if not receipt_dir.exists():
            return []
        records: list[dict[str, Any]] = []
        for path in sorted(receipt_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
            try:
                record = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(record, dict) and record.get("surface_id") == "context-graph-impact-receipt":
                records.append(_public_record(record))
            if len(records) >= limit:
                break
        return records

    def _write(self, record: dict[str, Any], path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(_public_record(record), indent=2), encoding="utf-8")

    def _write_genesis_foundation_projection(self, record: dict[str, Any], digest: str) -> None:
        projection_dir = self.output_dir / "genesis-foundation"
        projection_dir.mkdir(parents=True, exist_ok=True)
        path = projection_dir / f"{digest}.json"
        path.write_text(json.dumps(_public_record(record), indent=2), encoding="utf-8")

    def _write_impact_receipt(self, record: dict[str, Any], digest: str) -> None:
        receipt_dir = self.output_dir / "impact-receipts"
        receipt_dir.mkdir(parents=True, exist_ok=True)
        path = receipt_dir / f"{digest}.json"
        path.write_text(json.dumps(_public_record(record), indent=2), encoding="utf-8")

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


_UNSAFE_MARKERS = (
    "secret",
    "token",
    "password",
    "api-key",
    "apikey",
    ":\\",
    "runtime/test-fixtures",
)


def _public_record(record: dict[str, Any]) -> dict[str, Any]:
    payload = dict(record)
    if "artifact_path" in payload and "artifact_storage_ref" not in payload:
        payload["artifact_storage_ref"] = _path_storage_ref(payload["artifact_path"])
    payload.pop("artifact_path", None)
    if "question" in payload:
        payload["question_ref"] = _safe_ref(payload["question"])
        payload["question_sanitized"] = True
        payload.pop("question", None)
    if isinstance(payload.get("source"), dict):
        payload["source"] = _sanitize_public_mapping(payload["source"])
    if isinstance(payload.get("corpus"), dict):
        payload["corpus"] = _public_corpus(payload["corpus"])
    if isinstance(payload.get("graph_outputs"), list):
        payload["graph_outputs"] = [_public_graph_output(output) for output in payload["graph_outputs"]]
    if isinstance(payload.get("telemetry_trace_ids"), list):
        payload["telemetry_trace_ids"] = _sanitized_ref_list(payload["telemetry_trace_ids"])
    return payload


def _public_corpus(corpus: dict[str, Any]) -> dict[str, Any]:
    payload = dict(corpus)
    if "root" in payload:
        payload["root_ref"] = _safe_ref(payload["root"])
        payload["root_sanitized"] = True
        payload.pop("root", None)
    if "changed_files" in payload:
        payload["changed_file_refs"] = _sanitized_ref_list(payload["changed_files"])
        payload.pop("changed_files", None)
    if "graph_ignore_patterns" in payload:
        payload["graph_ignore_pattern_refs"] = _sanitized_ref_list(payload["graph_ignore_patterns"])
        payload.pop("graph_ignore_patterns", None)
    payload.setdefault("root_sanitized", True)
    payload.setdefault("changed_file_refs", [])
    payload.setdefault("graph_ignore_pattern_refs", [])
    return payload


def _public_graph_output(output: dict[str, Any]) -> dict[str, Any]:
    payload = dict(output)
    planned_path = payload.pop("planned_path", None)
    if planned_path and "planned_artifact_ref" not in payload:
        payload["planned_artifact_ref"] = _planned_artifact_ref(planned_path)
    return payload


def _sanitize_public_mapping(payload: dict[str, Any]) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    for key, value in payload.items():
        key_text = str(key)
        if key_text in {"session_id", "session_ref"}:
            sanitized["session_ref_digest"] = _safe_ref(value)
            continue
        if isinstance(value, str):
            sanitized[key_text] = _safe_public_string(value)
        elif isinstance(value, (int, float, bool)) or value is None:
            sanitized[key_text] = value
        else:
            sanitized[f"{key_text}_ref"] = _safe_ref(value)
    return sanitized


def _safe_public_string(value: str) -> str:
    text = str(value)
    return f"redacted::{_safe_ref(text)}" if _is_unsafe_text(text) else text


def _sanitized_ref_list(values: list[Any]) -> list[str]:
    return [_safe_ref(value) if _is_unsafe_text(str(value)) else str(value) for value in values]


def _safe_ref(value: Any) -> str:
    return f"sha256:{hashlib.sha256(str(value).encode('utf-8')).hexdigest()}"


def _digest_ref(*values: Any) -> str:
    return hashlib.sha256("|".join(str(value or "") for value in values).encode("utf-8")).hexdigest()[:24]


def _safe_int(value: Any) -> int:
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0


def _safe_graph_ref(value: Any) -> str:
    text = str(value or "").strip().replace("\\", "/")
    if not text:
        return ""
    lowered = text.lower()
    if (
        ".." in text
        or ":/" in text
        or lowered.startswith("file:")
        or any(marker in lowered for marker in _UNSAFE_MARKERS)
    ):
        return _safe_ref(text)
    return text[:220]


def _sanitized_graph_refs(values: list[Any]) -> list[str]:
    return _dedupe_refs([_safe_graph_ref(value) for value in values if str(value or "").strip()])


def _first_ref(values: list[Any]) -> str:
    for value in values:
        ref = _safe_graph_ref(value)
        if ref:
            return ref
    return ""


def _allowlisted_context_graph_pytest_argv(command: str) -> list[str]:
    parts = shlex.split(str(command or ""))
    if len(parts) < 4 or parts[:3] != ["python", "-m", "pytest"]:
        raise ValueError("context graph sandbox eval only allows: python -m pytest tests/*.py ...")
    allowed_options = {"-q", "--quiet", "--maxfail=1"}
    targets: list[str] = []
    for part in parts[3:]:
        if part.startswith("-"):
            if part not in allowed_options:
                raise ValueError(f"context graph sandbox pytest option is not allowed: {part}")
            continue
        target = part.split("::", 1)[0].replace("\\", "/")
        if (
            not target.startswith("tests/")
            or not target.endswith(".py")
            or ".." in target
            or ":/" in target
            or target.startswith("/")
        ):
            raise ValueError("context graph sandbox pytest targets must be tests/*.py or tests/**/*.py")
        targets.append(target)
    if not targets:
        raise ValueError("context graph sandbox eval requires at least one tests/*.py target")
    return [sys.executable, "-m", "pytest", *parts[3:]]


def _context_graph_sandbox_workspace(receipt_id: str, run_id: str) -> Path:
    root = Path(tempfile.gettempdir()) / "nexusnet-context-graph-sandboxes"
    return root / f"{_safe_filename(receipt_id)}-{_safe_filename(run_id)}"


def _context_graph_sandbox_copy_ignore(directory: str, names: list[str]) -> set[str]:
    blocked = {".git", ".hg", ".svn", ".pytest_cache", "__pycache__", ".mypy_cache", ".ruff_cache"}
    if Path(directory).name in {"artifacts"}:
        return set(names)
    return {name for name in names if name in blocked}


def _context_graph_manifest(root: Path) -> dict[str, str]:
    manifest: dict[str, str] = {}
    if not root.exists():
        return manifest
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        try:
            rel = path.relative_to(root).as_posix()
        except ValueError:
            continue
        if _context_graph_manifest_excluded(rel):
            continue
        try:
            manifest[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError:
            continue
    return manifest


def _context_graph_manifest_excluded(path_ref: str) -> bool:
    normalized = path_ref.replace("\\", "/")
    parts = set(normalized.split("/"))
    return (
        normalized.startswith("artifacts/")
        or ".git" in parts
        or ".pytest_cache" in parts
        or "__pycache__" in parts
        or normalized.endswith(".pyc")
    )


def _context_graph_manifest_diff(before: dict[str, str], after: dict[str, str]) -> dict[str, Any]:
    before_keys = set(before)
    after_keys = set(after)
    added = sorted(after_keys - before_keys)
    removed = sorted(before_keys - after_keys)
    changed = sorted(key for key in before_keys & after_keys if before[key] != after[key])
    changed_paths = [*added, *removed, *changed]
    return {
        "added_count": len(added),
        "removed_count": len(removed),
        "modified_count": len(changed),
        "changed_file_count": len(changed_paths),
        "changed_paths": changed_paths,
    }


def _context_graph_allowed_sandbox_change(path_ref: str) -> bool:
    normalized = path_ref.replace("\\", "/")
    return (
        normalized.startswith(".pytest_cache/")
        or "/__pycache__/" in normalized
        or normalized.startswith("runtime/")
        or normalized.startswith("artifacts/")
        or normalized.endswith(".pyc")
    )


def _safe_filename(value: Any) -> str:
    text = str(value or "").strip().replace("\\", "-").replace("/", "-").replace(":", "-")
    safe = "".join(ch if ch.isalnum() or ch in {"-", "_", "."} else "-" for ch in text)
    return safe[:96] or hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:24]


def _is_unsafe_text(value: str) -> bool:
    lowered = value.lower().replace("\\", "/")
    return any(marker in lowered for marker in _UNSAFE_MARKERS) or ":\\" in value


def _path_storage_ref(value: Any) -> str:
    try:
        path = Path(str(value))
        name = path.name or "context-graph-record.json"
        parent = path.parent.name
        if parent == "queries":
            return f"context-graphs/queries/{name}"
        return f"context-graphs/{name}"
    except (OSError, ValueError):
        return f"context-graphs/{_safe_ref(value)}.json"


def _planned_artifact_ref(value: Any) -> str:
    parts = Path(str(value).replace("\\", "/")).parts
    if len(parts) >= 2:
        return "/".join(parts[-2:])
    return str(value)


def _record_genesis_context_graph_admission(
    service: ContextGraphService,
    *,
    session_id: str | None,
    ingress_route: str,
    content: str,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    admission = getattr(service, "genesis_memory_admission", None)
    record_manual_ingress = getattr(admission, "record_manual_ingress", None)
    if not callable(record_manual_ingress):
        return {}
    decision = record_manual_ingress(
        session_id=session_id,
        ingress_route=ingress_route,
        content=content,
        metadata=metadata,
    )
    return decision if isinstance(decision, dict) else {}


def _context_graph_session_id(source: dict[str, Any], linked_trace_ids: list[str] | None) -> str | None:
    for value in (
        source.get("session_id"),
        source.get("session_ref"),
        (source.get("metadata") or {}).get("session_id") if isinstance(source.get("metadata"), dict) else None,
    ):
        if value:
            return str(value)
    for trace_id in linked_trace_ids or []:
        text = str(trace_id or "")
        if text and _is_unsafe_text(text):
            return text
    return None


def _context_graph_plan_content(
    *,
    source: dict[str, Any],
    corpus_root: str,
    changed_files: list[str],
    graph_ignore_patterns: list[str],
    content_kinds: list[str],
) -> str:
    payload = {
        "source": source,
        "corpus_root": corpus_root,
        "changed_files": changed_files,
        "graph_ignore_patterns": graph_ignore_patterns,
        "content_kinds": content_kinds,
    }
    return json.dumps(payload, sort_keys=True, default=str)


def _context_graph_plan_admission_metadata(source: dict[str, Any]) -> dict[str, Any]:
    metadata = dict(source.get("metadata") or {}) if isinstance(source.get("metadata"), dict) else {}
    return {
        "source_kind": source.get("source_kind") or metadata.get("source_kind") or "context-graph-index-plan",
        "privacy_class": source.get("privacy_class") or metadata.get("privacy_class") or "unspecified",
        "consent_status": source.get("consent_status") or metadata.get("consent_status") or "not-declared",
        "rights_license_status": (
            source.get("rights_license_status")
            or source.get("license_status")
            or source.get("license_posture")
            or metadata.get("rights_license_status")
            or metadata.get("license_status")
            or "not-declared"
        ),
    }


def _genesis_memory_admission_gate(
    *,
    ingress_route: str,
    decisions: list[dict[str, Any]],
) -> dict[str, Any]:
    valid_decisions = [decision for decision in decisions if decision]
    blocked = [
        decision
        for decision in valid_decisions
        if decision.get("memory_write_allowed") is not True
    ]
    return {
        "surface_id": "genesis-memory-admission-gate",
        "ingress_route": ingress_route,
        "decision_count": len(valid_decisions),
        "blocked_count": len(blocked),
        "allowed_count": len(valid_decisions) - len(blocked),
        "decision_refs": [
            str(decision.get("decision_id"))
            for decision in valid_decisions
            if decision.get("decision_id")
        ],
        "blocked_decision_refs": [
            str(decision.get("decision_id"))
            for decision in blocked
            if decision.get("decision_id")
        ],
        "memory_write_allowed": bool(valid_decisions) and not blocked,
        "retrieval_truth_allowed": bool(valid_decisions)
        and not blocked
        and any(decision.get("retrieval_truth_allowed") is True for decision in valid_decisions),
        "training_allowed": bool(valid_decisions)
        and not blocked
        and any(decision.get("training_allowed") is True for decision in valid_decisions),
        "raw_content_included": False,
    }


def _aggregate_genesis_memory_admission_gates(records: list[dict[str, Any]]) -> dict[str, Any]:
    gates = [
        record.get("genesis_memory_admission_gate")
        for record in records
        if isinstance(record.get("genesis_memory_admission_gate"), dict)
    ]
    decision_refs = _dedupe_refs(
        [
            ref
            for gate in gates
            for ref in gate.get("decision_refs", [])
        ]
    )
    blocked_refs = _dedupe_refs(
        [
            ref
            for gate in gates
            for ref in gate.get("blocked_decision_refs", [])
        ]
    )
    decision_count = sum(int(gate.get("decision_count") or 0) for gate in gates)
    blocked_count = sum(int(gate.get("blocked_count") or 0) for gate in gates)
    allowed_count = sum(int(gate.get("allowed_count") or 0) for gate in gates)
    return {
        "surface_id": "genesis-memory-admission-gate",
        "ingress_route": "context-graph",
        "decision_count": decision_count,
        "blocked_count": blocked_count,
        "allowed_count": allowed_count,
        "decision_refs": decision_refs,
        "blocked_decision_refs": blocked_refs,
        "memory_write_allowed": decision_count > 0 and blocked_count == 0,
        "retrieval_truth_allowed": False,
        "training_allowed": False,
        "raw_content_included": False,
    }


def _dedupe_refs(values: list[Any]) -> list[str]:
    seen: set[str] = set()
    refs: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if text and text not in seen and not _is_unsafe_text(text):
            seen.add(text)
            refs.append(text)
    return refs

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow


RunKind = Literal["code_edit", "docs_only", "research_only"]
ImpactRisk = Literal["missing", "not_required", "LOW", "MEDIUM", "HIGH", "CRITICAL"]


class CodegraphRunManifestRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    manifest_id: str
    run_kind: RunKind
    indexed_repo: str
    indexed_commit: str
    worktree_commit: str
    graph_query_ref: str = ""
    impact_target: str = ""
    impact_risk: ImpactRisk = "missing"
    affected_processes: list[str] = Field(default_factory=list)
    detect_changes_ref: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class CodegraphGate:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.records_dir = self.artifacts_dir / "operations" / "codegraph-gate" if self.artifacts_dir else None
        if self.records_dir is not None:
            self.records_dir.mkdir(parents=True, exist_ok=True)
        self._records: list[dict[str, Any]] = []

    def evaluate(self, request: CodegraphRunManifestRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, CodegraphRunManifestRequest) else CodegraphRunManifestRequest.model_validate(request)
        findings = _findings(normalized)
        report = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "codegraph-gate",
            "manifest_id": normalized.manifest_id,
            "run_kind": normalized.run_kind,
            "indexed_repo": normalized.indexed_repo,
            "indexed_commit": normalized.indexed_commit,
            "worktree_commit": normalized.worktree_commit,
            "status": "blocked" if findings else "allowed",
            "runtime_state": "degraded" if findings else "live-bound",
            "created_at": utcnow().isoformat(),
            "graph_query_ref": normalized.graph_query_ref,
            "impact_target": normalized.impact_target,
            "impact_risk": normalized.impact_risk,
            "affected_processes": normalized.affected_processes,
            "detect_changes_ref": normalized.detect_changes_ref,
            "findings": findings,
            "policy_boundary": "code-affecting-runs-require-current-graph-impact-and-detect-changes",
            "metadata": normalized.metadata,
            "operator_actions": _operator_actions(),
        }
        self._persist(report)
        return report

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        records = self._records[:limit]
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "codegraph-gate",
            "authority": "NexusBrain",
            "runtime_state": "degraded"
            if any(record.get("status") == "blocked" for record in records)
            else ("live-bound" if records else "static-canon"),
            "manifest_count": len(records),
            "latest_manifest": records[0] if records else None,
            "manifests": records,
            "operator_actions": _operator_actions(),
        }

    def _persist(self, report: dict[str, Any]) -> None:
        self._records.insert(0, report)
        self._records = self._records[:50]
        if self.records_dir is not None:
            path = self.records_dir / f"{report['manifest_id'].replace(':', '_')}.json"
            report["artifact_path"] = str(path)
            path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def _findings(request: CodegraphRunManifestRequest) -> list[dict[str, str]]:
    findings = []
    if request.run_kind == "code_edit" and request.impact_risk == "missing":
        findings.append(
            {
                "rule_id": "codegraph_gate_requires_impact_evidence",
                "severity": "hard_fail",
                "message": "Code edits require GitNexus impact evidence.",
            }
        )
    if request.run_kind == "code_edit" and request.indexed_commit != request.worktree_commit:
        findings.append(
            {
                "rule_id": "codegraph_gate_blocks_stale_index",
                "severity": "hard_fail",
                "message": "Codegraph index commit differs from worktree commit.",
            }
        )
    if request.run_kind == "code_edit" and not request.detect_changes_ref:
        findings.append(
            {
                "rule_id": "codegraph_gate_requires_detect_changes",
                "severity": "hard_fail",
                "message": "Code edits require detect-changes evidence before commit.",
            }
        )
    if request.impact_risk in {"HIGH", "CRITICAL"}:
        findings.append(
            {
                "rule_id": "codegraph_gate_requires_manual_review_for_high_risk",
                "severity": "hard_fail",
                "message": "High or critical impact changes require manual review.",
            }
        )
    return findings


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/codegraph-gate"},
        "evaluate": {"method": "POST", "endpoint": "/ops/brain/codegraph-gate/manifests"},
    }

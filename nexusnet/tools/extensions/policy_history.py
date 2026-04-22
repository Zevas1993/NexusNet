from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .policy_reports import build_policy_lifecycle_report


def _policy_slug(*parts: str) -> str:
    return "_".join(
        "".join(ch if ch.isalnum() else "_" for ch in str(part or "").lower()).strip("_")
        for part in parts
        if str(part or "").strip()
    )


class PolicyHistoryService:
    def __init__(self, *, artifacts_dir: Path | str):
        self.artifacts_dir = Path(artifacts_dir)
        self.output_dir = self.artifacts_dir / "extensions" / "policy_history"

    def record(self, *, policy_set: dict[str, Any]) -> dict[str, Any]:
        policy_set_id = str(policy_set.get("policy_set_id") or "unknown-policy-set")
        version = str(policy_set.get("version") or "unknown")
        artifact_id = f"policyhist_{_policy_slug(policy_set_id, version)}"
        snapshot_signature = json.dumps(
            {
                "policy_set_id": policy_set_id,
                "version": version,
                "status": policy_set.get("status"),
                "created_from": policy_set.get("created_from"),
                "supersedes": policy_set.get("supersedes", []),
                "rollback_reference": policy_set.get("rollback_reference"),
                "linked_evidence_ids": policy_set.get("linked_evidence_ids", []),
                "effective_scope": policy_set.get("effective_scope", {}),
                "status_history": policy_set.get("status_history", []),
            },
            sort_keys=True,
        )
        record = {
            "artifact_id": artifact_id,
            "lineage_anchor_id": f"policylineage_{_policy_slug(policy_set_id)}",
            "stable_policy_version_id": f"{policy_set_id}@{version}",
            "policy_set_id": policy_set_id,
            "version": version,
            "label": policy_set.get("label"),
            "bundle_family": policy_set.get("bundle_family"),
            "bundle_ids": list(policy_set.get("bundle_ids", []) or []),
            "allowed_tools": list(policy_set.get("allowed_tools", []) or []),
            "inherited_permissions": list(policy_set.get("inherited_permissions", []) or []),
            "approval_mode": policy_set.get("approval_mode"),
            "sandbox_posture": policy_set.get("sandbox_posture"),
            "recommended_provider_kinds": list(policy_set.get("recommended_provider_kinds", []) or []),
            "risk_flags": list(policy_set.get("risk_flags", []) or []),
            "author": policy_set.get("author"),
            "origin": policy_set.get("origin"),
            "effective_scope": policy_set.get("effective_scope", {}),
            "status": policy_set.get("status", "draft"),
            "created_from": policy_set.get("created_from"),
            "supersedes": list(policy_set.get("supersedes", []) or []),
            "created_at": policy_set.get("created_at"),
            "activated_at": policy_set.get("activated_at"),
            "retired_at": policy_set.get("retired_at"),
            "rollback_reference": policy_set.get("rollback_reference"),
            "linked_evidence_ids": list(policy_set.get("linked_evidence_ids", []) or []),
            "linked_report_ids": list(policy_set.get("linked_report_ids", []) or []),
            "status_history": list(policy_set.get("status_history", []) or []),
            "notes": list(policy_set.get("notes", []) or []),
            "snapshot_signature": snapshot_signature,
        }
        path = self.output_dir / f"{artifact_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        report = build_policy_lifecycle_report(artifacts_dir=self.artifacts_dir, record=record)
        record["artifact_path"] = str(path)
        record["report"] = report
        record["linked_report_ids"] = sorted(set([*record.get("linked_report_ids", []), report["report_id"]]))
        path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        return record

    def list(self, *, limit: int = 50) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        if not self.output_dir.exists():
            return items
        for path in sorted(self.output_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
            try:
                items.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                continue
            if len(items) >= limit:
                break
        return items

    def detail(self, *, policy_set_id: str, version: str | None = None) -> dict[str, Any] | None:
        lineage = self._lineage(policy_set_id=policy_set_id)
        if version:
            artifact_id = f"policyhist_{_policy_slug(policy_set_id, version)}"
            path = self.output_dir / f"{artifact_id}.json"
            if not path.exists():
                return None
            try:
                item = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                return None
        else:
            item = lineage[0] if lineage else None
            if item is None:
                return None
        report = item.get("report") or {}
        payload = None
        markdown = None
        if report.get("payload_path"):
            try:
                payload = json.loads(Path(report["payload_path"]).read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                payload = None
        if report.get("markdown_path"):
            try:
                markdown = Path(report["markdown_path"]).read_text(encoding="utf-8")
            except OSError:
                markdown = None
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "item": item,
            "lineage": lineage,
            "lineage_depth": len(lineage),
            "latest_status_transition": (item.get("status_history") or [{}])[-1],
            "report_payload": payload,
            "report_markdown": markdown,
        }

    def _lineage(self, *, policy_set_id: str) -> list[dict[str, Any]]:
        matches = [entry for entry in self.list(limit=500) if entry.get("policy_set_id") == policy_set_id]
        return sorted(
            matches,
            key=lambda item: (
                str(item.get("activated_at") or item.get("created_at") or ""),
                str(item.get("created_at") or ""),
                str(item.get("version") or ""),
            ),
            reverse=True,
        )

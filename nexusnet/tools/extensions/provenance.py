from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import new_id, utcnow

from .reports import build_extension_bundle_report


class ExtensionBundleProvenanceService:
    def __init__(self, *, artifacts_dir: Path):
        self.artifacts_dir = Path(artifacts_dir)
        self.output_dir = self.artifacts_dir / "extensions" / "provenance"

    def record(self, *, bundle: dict[str, Any]) -> dict[str, Any]:
        latest = self.latest_for(bundle_id=str(bundle.get("bundle_id")), workspace_id=str(bundle.get("workspace_id")))
        snapshot_signature = json.dumps(
            {
                "bundle_id": bundle.get("bundle_id"),
                "workspace_id": bundle.get("workspace_id"),
                "enabled_state": bundle.get("enabled_state"),
                "policy_set_id": bundle.get("policy_set_id"),
                "policy_set_version": bundle.get("policy_set_version"),
                "bundle_family": bundle.get("bundle_family"),
                "allowed_tools": bundle.get("allowed_tools", []),
                "risk_flags": bundle.get("risk_flags", []),
                "approval_path": bundle.get("approval_path", {}),
                "permission_mode": bundle.get("permission_mode"),
                "sandbox_posture": bundle.get("sandbox_posture"),
                "compatible_provider_ids": ((bundle.get("acp_compatibility") or {}).get("compatible_provider_ids", [])),
                "policy_status": (((bundle.get("policy_lifecycle") or {}).get("status"))),
                "policy_history_artifact_id": (((bundle.get("policy_lifecycle") or {}).get("artifact_id"))),
                "certification_status": bundle.get("certification_status"),
                "certification_artifact_id": bundle.get("certification_artifact_id"),
                "stable_certification_id": bundle.get("stable_certification_id"),
                "certification_lineage_depth": bundle.get("certification_lineage_depth"),
                "certification_lineage_statuses": bundle.get("certification_lineage_statuses", []),
                "historical_certification_artifact_ids": bundle.get("historical_certification_artifact_ids", []),
                "restoration_detected": bundle.get("restoration_detected", False),
            },
            sort_keys=True,
        )
        if latest and latest.get("snapshot_signature") == snapshot_signature:
            return latest

        artifact_id = new_id("extbundle")
        record = {
            "artifact_id": artifact_id,
            "lineage_anchor_id": f"bundlelineage::{bundle.get('workspace_id')}::{bundle.get('bundle_id')}",
            "supersedes_artifact_id": latest.get("artifact_id") if latest else None,
            "bundle_id": bundle.get("bundle_id"),
            "label": bundle.get("label"),
            "workspace_id": bundle.get("workspace_id"),
            "created_at": utcnow().isoformat(),
            "snapshot_signature": snapshot_signature,
            "permission_delta_from_previous": self._list_delta(
                previous=(latest or {}).get("inherited_permissions", []),
                current=bundle.get("inherited_permissions", []),
            ),
            "risk_flag_delta_from_previous": self._list_delta(
                previous=(latest or {}).get("risk_flags", []),
                current=bundle.get("risk_flags", []),
            ),
            **bundle,
        }
        path = self.output_dir / f"{artifact_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        record["artifact_path"] = str(path)
        report = build_extension_bundle_report(artifacts_dir=self.artifacts_dir, record=record)
        record["report"] = report
        record["linked_report_ids"] = sorted(
            set(
                [
                    report["report_id"],
                    *record.get("linked_report_ids", []),
                    *([record.get("certification_report_id")] if record.get("certification_report_id") else []),
                    *(
                        [(((record.get("policy_lifecycle") or {}).get("report")) or {}).get("report_id")]
                        if (((record.get("policy_lifecycle") or {}).get("report")) or {}).get("report_id")
                        else []
                    ),
                ]
            )
        )
        path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        return record

    def list(self, *, workspace_id: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        if not self.output_dir.exists():
            return items
        for path in self.output_dir.glob("*.json"):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if workspace_id and payload.get("workspace_id") != workspace_id:
                continue
            items.append(payload)
        return self._sort_items(items)[:limit]

    def latest_for(self, *, bundle_id: str, workspace_id: str | None = None) -> dict[str, Any] | None:
        for item in self.list(workspace_id=workspace_id, limit=200):
            if item.get("bundle_id") == bundle_id:
                return item
        return None

    def detail(self, artifact_id: str) -> dict[str, Any] | None:
        path = self.output_dir / f"{artifact_id}.json"
        if not path.exists():
            return None
        try:
            item = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
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
        lineage = [
            entry
            for entry in self.list(workspace_id=str(item.get("workspace_id") or ""), limit=200)
            if entry.get("bundle_id") == item.get("bundle_id")
        ]
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "item": item,
            "lineage": lineage,
            "lineage_depth": len(lineage),
            "report_payload": payload,
            "report_markdown": markdown,
        }

    def _list_delta(self, *, previous: list[str], current: list[str]) -> dict[str, list[str]]:
        previous_set = set(previous or [])
        current_set = set(current or [])
        return {
            "added": sorted(current_set - previous_set),
            "removed": sorted(previous_set - current_set),
        }

    def _sort_items(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted(
            items,
            key=lambda item: (
                str(item.get("created_at") or ""),
                str(item.get("policy_set_version") or ""),
                str(item.get("artifact_id") or ""),
            ),
            reverse=True,
        )

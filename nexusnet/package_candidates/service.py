from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import new_id, utcnow


class PackageCandidateService:
    SUPPORTED_SOURCES = {"npm", "git", "local"}

    def __init__(self, *, artifacts_dir: Path | str, events: Any | None = None):
        self.artifacts_dir = Path(artifacts_dir)
        self.output_dir = self.artifacts_dir / "package-candidates"
        self.events = events

    def ingest(
        self,
        *,
        source_type: str,
        source_ref: str,
        manifest: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        workspace_id: str = "default",
    ) -> dict[str, Any]:
        manifest = manifest or {}
        metadata = metadata or {}
        candidate_id = self._candidate_id(source_type=source_type, source_ref=source_ref)
        nexus_manifest = manifest.get("nexusnet_package") or manifest.get("pi") or {}
        requested_permissions = sorted(
            {
                *[str(item) for item in nexus_manifest.get("permissions", []) or []],
                *[str(item) for item in nexus_manifest.get("tools", []) or [] if str(item) in {"shell.exec", "filesystem.write", "network.external"}],
            }
        )
        risk_flags = self._risk_flags(source_type=source_type, permissions=requested_permissions, nexus_manifest=nexus_manifest)
        rejected = source_type not in self.SUPPORTED_SOURCES
        record = {
            "candidate_id": candidate_id,
            "source_type": source_type,
            "source_ref": source_ref,
            "workspace_id": workspace_id,
            "created_at": utcnow().isoformat(),
            "candidate_state": "rejected" if rejected else "candidate_only",
            "enablement_state": "disabled" if rejected else "disabled_until_certified",
            "execution_allowed": False,
            "mutation_allowed": False,
            "sandbox_posture": "deny_execution_until_review",
            "requested_permissions": requested_permissions,
            "risk_flags": risk_flags,
            "classification": {
                "resource_types": {
                    "tools": list(nexus_manifest.get("tools", []) or []),
                    "skills": list(nexus_manifest.get("skills", []) or []),
                    "prompts": list(nexus_manifest.get("prompts", []) or []),
                    "themes": list(nexus_manifest.get("themes", []) or []),
                    "providers": list(nexus_manifest.get("providers", []) or []),
                    "workflow_templates": list(nexus_manifest.get("workflow_templates", []) or []),
                    "plan_review_plugins": list(nexus_manifest.get("plan_review_plugins", []) or []),
                },
                "metadata_only": True,
                "external_code_loaded": False,
            },
            "license_review": {
                "status": "requires_review",
                "declared_license": manifest.get("license") or metadata.get("license"),
                "review_required_before_enablement": True,
            },
            "policy": {
                "decision": "deny" if rejected else "hold",
                "mutation_requires_policy_grant": True,
                "gateway_required": True,
                "product_sweep_required": True,
                "reason": "unsupported-source-type" if rejected else "candidate-intake-only",
            },
            "manifest": manifest,
            "metadata": metadata,
        }
        path = self.output_dir / f"{candidate_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        record["artifact_path"] = str(path)
        path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        if self.events:
            self.events.record(
                event_type="package_candidate.ingested",
                subject=f"package-candidate:{candidate_id}",
                payload={
                    "source_type": source_type,
                    "source_ref": source_ref,
                    "candidate_state": record["candidate_state"],
                    "risk_flags": risk_flags,
                },
            )
            for provider in nexus_manifest.get("providers", []) or []:
                self.events.record(
                    event_type="provider.requested",
                    subject=f"package-candidate:{candidate_id}",
                    payload={"provider": provider, "execution_allowed": False, "candidate_state": record["candidate_state"]},
                )
        return record

    def summary(self, *, workspace_id: str | None = None, limit: int = 50) -> dict[str, Any]:
        items = self.list(workspace_id=workspace_id, limit=limit)
        state_counts: dict[str, int] = {}
        risk_counts: dict[str, int] = {}
        for item in items:
            state = str(item.get("candidate_state") or "unknown")
            state_counts[state] = state_counts.get(state, 0) + 1
            for risk in item.get("risk_flags", []):
                risk_counts[str(risk)] = risk_counts.get(str(risk), 0) + 1
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "candidate_count": len(items),
            "workspace_id": workspace_id,
            "state_counts": state_counts,
            "risk_flag_counts": risk_counts,
            "latest_candidate": items[0] if items else None,
            "event_log": self.events.summary(subject_prefix="package-candidate:", limit=100) if self.events else {},
            "items": items,
        }

    def list(self, *, workspace_id: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        if not self.output_dir.exists():
            return items
        for path in sorted(self.output_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if workspace_id and payload.get("workspace_id") != workspace_id:
                continue
            items.append(payload)
            if len(items) >= limit:
                break
        return items

    def _candidate_id(self, *, source_type: str, source_ref: str) -> str:
        slug = "".join(ch if ch.isalnum() else "-" for ch in f"{source_type}-{source_ref}".lower()).strip("-")
        return f"pkgcand_{slug[:80]}_{new_id('cand').split('_', 1)[1]}"

    def _risk_flags(self, *, source_type: str, permissions: list[str], nexus_manifest: dict[str, Any]) -> list[str]:
        flags: set[str] = set()
        if source_type not in self.SUPPORTED_SOURCES:
            flags.add("unsupported-source-type")
        if "shell.exec" in permissions or "shell.exec" in set(nexus_manifest.get("tools", []) or []):
            flags.add("shell-exec-risk")
        if "filesystem.write" in permissions:
            flags.add("filesystem-write-risk")
        if "network.external" in permissions:
            flags.add("network-egress-risk")
        if nexus_manifest.get("providers"):
            flags.add("provider-registration-risk")
        if nexus_manifest.get("plan_review_plugins"):
            flags.add("plan-review-plugin-review-required")
        return sorted(flags)

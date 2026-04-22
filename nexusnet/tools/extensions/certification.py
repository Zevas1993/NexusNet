from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import new_id, utcnow

from .reports import build_extension_bundle_certification_report


class ExtensionBundleCertificationService:
    def __init__(self, *, artifacts_dir: Path | str):
        self.artifacts_dir = Path(artifacts_dir)
        self.output_dir = self.artifacts_dir / "extensions" / "certifications"

    def record(self, *, bundle: dict[str, Any], recent_reviews: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        recent_reviews = list(recent_reviews or [])
        self._ensure_historical_lineage(bundle=bundle, recent_reviews=recent_reviews)
        relevant_reviews = self._relevant_reviews(bundle=bundle, recent_reviews=recent_reviews)
        existing_lineage = self._lineage(
            bundle_id=str(bundle.get("bundle_id") or ""),
            workspace_id=str(bundle.get("workspace_id") or ""),
        )
        latest = existing_lineage[0] if existing_lineage else None
        payload = self._build_record(
            artifact_id=new_id("bundlecert"),
            created_at=utcnow().isoformat(),
            bundle=bundle,
            relevant_reviews=relevant_reviews,
            latest=latest,
            existing_lineage=existing_lineage,
            historical_fixture=False,
        )
        if latest and latest.get("snapshot_signature") == payload.get("snapshot_signature"):
            return latest
        return self._write_record(payload)

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
        return self._sort_items(items)[:limit]

    def latest_for(self, *, bundle_id: str, workspace_id: str | None = None) -> dict[str, Any] | None:
        return next((item for item in self.list(workspace_id=workspace_id, limit=200) if item.get("bundle_id") == bundle_id), None)

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
        lineage = self._lineage(
            bundle_id=str(item.get("bundle_id") or ""),
            workspace_id=str(item.get("workspace_id") or ""),
        )
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "item": item,
            "lineage": lineage,
            "lineage_depth": len(lineage),
            "lineage_summary": {
                "historical_artifact_count": max(0, len(lineage) - 1),
                "historical_fixture_count": sum(1 for entry in lineage if entry.get("historical_fixture")),
                "certification_statuses": [
                    entry.get("certification_status")
                    for entry in lineage
                    if entry.get("certification_status")
                ],
                "policy_versions": [
                    f"{entry.get('policy_set_id')}@{entry.get('policy_set_version')}"
                    for entry in lineage
                    if entry.get("policy_set_id") and entry.get("policy_set_version")
                ],
                "restoration_detected": bool(item.get("restoration_detected", False)),
                "restored_from_certification_artifact_ids": item.get("restored_from_certification_artifact_ids", []),
                "restored_from_policy_versions": item.get("restored_from_policy_versions", []),
            },
            "report_payload": payload,
            "report_markdown": markdown,
        }

    def _relevant_reviews(self, *, bundle: dict[str, Any], recent_reviews: list[dict[str, Any]]) -> list[dict[str, Any]]:
        bundle_id = str(bundle.get("bundle_id") or "")
        bundle_risks = set(bundle.get("risk_flags", []) or [])
        matches: list[dict[str, Any]] = []
        for review in recent_reviews:
            requested_extensions = set(review.get("requested_extensions", []) or [])
            allowed_extensions = set(review.get("allowed_extensions", []) or [])
            risk_families = set(review.get("risk_families", []) or [])
            if bundle_id and bundle_id in requested_extensions.union(allowed_extensions):
                matches.append(review)
                continue
            if bundle_risks and bundle_risks.intersection(risk_families):
                matches.append(review)
        return matches[:10]

    def _privilege_inheritance_confusion(self, *, bundle: dict[str, Any]) -> bool:
        risk_flags = set(bundle.get("risk_flags", []) or [])
        acp_compatibility = bundle.get("acp_compatibility") or {}
        compatible_provider_ids = list(acp_compatibility.get("compatible_provider_ids", []) or [])
        recommended_provider_kinds = list(acp_compatibility.get("recommended_provider_kinds", []) or [])
        return (
            "extension-acp-privilege-inheritance-confusion-risk" in risk_flags
            or ("provider.acp" in set(bundle.get("allowed_tools", []) or []) and not compatible_provider_ids)
            or (bool(recommended_provider_kinds) and not compatible_provider_ids and bundle.get("bundle_family") == "acp-provider-lane")
        )

    def _recommended_actions(self, *, bundle: dict[str, Any], privilege_inheritance_confusion: bool) -> list[str]:
        actions: list[str] = []
        if privilege_inheritance_confusion:
            actions.append("review-extension-acp-permission-inheritance")
        if ((bundle.get("approval_path") or {}).get("decision")) in {"ask", "allow-if-approved"}:
            actions.append("hold-bundle-behind-explicit-approval")
        if ((bundle.get("policy_lifecycle") or {}).get("status")) == "shadow":
            actions.append("keep-policy-set-in-shadow-rollout")
        return sorted(set(actions))

    def _status(
        self,
        *,
        bundle: dict[str, Any],
        privilege_inheritance_confusion: bool,
        relevant_reviews: list[dict[str, Any]],
    ) -> str:
        review_decisions = {review.get("decision") for review in relevant_reviews}
        policy_status = str(((bundle.get("policy_lifecycle") or {}).get("status")) or "draft")
        approval_decision = str(((bundle.get("approval_path") or {}).get("decision")) or "allow")
        if "deny" in review_decisions:
            return "held"
        if policy_status == "held":
            return "held"
        if policy_status == "revoked":
            return "revoked"
        if policy_status == "rolled_back":
            return "rolled_back"
        if policy_status == "superseded":
            return "revoked"
        if privilege_inheritance_confusion or approval_decision in {"ask", "allow-if-approved"} or policy_status == "shadow":
            return "shadow-approved"
        if str(bundle.get("enabled_state")) != "enabled":
            return "draft"
        if policy_status == "approved" or relevant_reviews:
            return "reviewed"
        return "active"

    def _lineage(self, *, bundle_id: str, workspace_id: str) -> list[dict[str, Any]]:
        return [
            item
            for item in self.list(workspace_id=workspace_id, limit=200)
            if item.get("bundle_id") == bundle_id
        ]

    def _list_delta(self, *, previous: list[str], current: list[str]) -> dict[str, list[str]]:
        previous_set = set(previous or [])
        current_set = set(current or [])
        return {
            "added": sorted(current_set - previous_set),
            "removed": sorted(previous_set - current_set),
        }

    def _build_record(
        self,
        *,
        artifact_id: str,
        created_at: str,
        bundle: dict[str, Any],
        relevant_reviews: list[dict[str, Any]],
        latest: dict[str, Any] | None,
        existing_lineage: list[dict[str, Any]] | None,
        historical_fixture: bool,
    ) -> dict[str, Any]:
        historical_lineage = [
            item
            for item in list(existing_lineage or [])
            if item.get("artifact_id") != artifact_id
        ]
        privilege_inheritance_confusion = self._privilege_inheritance_confusion(bundle=bundle)
        certification_status = self._status(
            bundle=bundle,
            privilege_inheritance_confusion=privilege_inheritance_confusion,
            relevant_reviews=relevant_reviews,
        )
        restoration_targets = self._restoration_targets(
            bundle=bundle,
            relevant_reviews=relevant_reviews,
            historical_lineage=historical_lineage,
        )
        certification_policy_version = f"{bundle.get('policy_set_id')}@{bundle.get('policy_set_version')}"
        historical_policy_versions = [
            f"{item.get('policy_set_id')}@{item.get('policy_set_version')}"
            for item in historical_lineage
            if item.get("policy_set_id") and item.get("policy_set_version")
        ]
        record = {
            "artifact_id": artifact_id,
            "created_at": created_at,
            "historical_fixture": historical_fixture,
            "lineage_anchor_id": f"certlineage::{bundle.get('workspace_id')}::{bundle.get('bundle_id')}",
            "stable_certification_id": (
                f"{bundle.get('bundle_id')}::{bundle.get('policy_set_id')}::{bundle.get('policy_set_version')}"
            ),
            "supersedes_artifact_id": latest.get("artifact_id") if latest else None,
            "bundle_id": bundle.get("bundle_id"),
            "bundle_family": bundle.get("bundle_family"),
            "policy_set_id": bundle.get("policy_set_id"),
            "policy_set_version": bundle.get("policy_set_version"),
            "policy_status": (((bundle.get("policy_lifecycle") or {}).get("status"))),
            "policy_history_artifact_id": (((bundle.get("policy_lifecycle") or {}).get("artifact_id"))),
            "policy_history_report_id": ((((bundle.get("policy_lifecycle") or {}).get("report")) or {}).get("report_id")),
            "workspace_id": bundle.get("workspace_id"),
            "enabled_state": bundle.get("enabled_state"),
            "workspace_scopes": list(bundle.get("workspace_scopes", []) or []),
            "roots": list(bundle.get("roots", []) or []),
            "inherited_permissions": list(bundle.get("inherited_permissions", []) or []),
            "allowed_tools": list(bundle.get("allowed_tools", []) or []),
            "acp_compatibility": bundle.get("acp_compatibility", {}),
            "approval_path": bundle.get("approval_path", {}),
            "sandbox_posture": bundle.get("sandbox_posture"),
            "permission_mode": bundle.get("permission_mode"),
            "risk_flags": list(bundle.get("risk_flags", []) or []),
            "adversary_review_report_ids": [((item.get("report") or {}).get("report_id")) for item in relevant_reviews if (item.get("report") or {}).get("report_id")],
            "adversary_review_ids": [item.get("review_id") for item in relevant_reviews if item.get("review_id")],
            "privilege_inheritance_confusion": privilege_inheritance_confusion,
            "recommended_remediation_actions": self._recommended_actions(bundle=bundle, privilege_inheritance_confusion=privilege_inheritance_confusion),
            "certification_status": certification_status,
            "policy_lineage": list(((bundle.get("policy_lifecycle") or {}).get("lineage")) or []),
            "policy_lineage_statuses": [
                item.get("status")
                for item in (((bundle.get("policy_lifecycle") or {}).get("lineage")) or [])
                if item.get("status")
            ],
            "restored_from_policy_versions": [
                f"{item.get('policy_set_id')}@{item.get('version')}"
                for item in (((bundle.get("policy_lifecycle") or {}).get("lineage")) or [])[1:]
                if item.get("status") in {"held", "rolled_back", "revoked", "superseded"}
            ],
            "restored_from_certification_artifact_ids": restoration_targets["artifact_ids"],
            "restored_from_certification_statuses": restoration_targets["statuses"],
            "restoration_detected": bool(
                certification_status in {"active", "reviewed", "shadow-approved"}
                and bool(restoration_targets["artifact_ids"])
            ),
            "historical_certification_artifact_ids": [
                item.get("artifact_id")
                for item in historical_lineage
                if item.get("artifact_id")
            ],
            "historical_certification_statuses": [
                item.get("certification_status")
                for item in historical_lineage
                if item.get("certification_status")
            ],
            "historical_certification_policy_versions": historical_policy_versions,
            "historical_fixture_count": sum(1 for item in historical_lineage if item.get("historical_fixture")),
            "certification_lineage_depth": 1 + len(historical_lineage),
            "certification_lineage_artifact_ids": [
                artifact_id,
                *[
                    item.get("artifact_id")
                    for item in historical_lineage
                    if item.get("artifact_id")
                ],
            ],
            "certification_lineage_policy_versions": [
                certification_policy_version,
                *historical_policy_versions,
            ],
            "certification_lineage_statuses": [
                certification_status,
                *[
                    item.get("certification_status")
                    for item in historical_lineage
                    if item.get("certification_status")
                ],
            ],
            "revoked_or_held_ancestor_artifact_ids": [
                item.get("artifact_id")
                for item in historical_lineage
                if item.get("artifact_id") and item.get("certification_status") in {"held", "revoked", "rolled_back"}
            ],
            "lineage_continuity_preserved": bool(
                not latest
                or latest.get("lineage_anchor_id")
                == f"certlineage::{bundle.get('workspace_id')}::{bundle.get('bundle_id')}"
            ),
            "latest_certification_transition": {
                "from_artifact_id": latest.get("artifact_id") if latest else None,
                "from_status": latest.get("certification_status") if latest else None,
                "to_artifact_id": artifact_id,
                "to_status": certification_status,
            },
            "permission_delta_from_previous": self._list_delta(
                previous=(latest or {}).get("inherited_permissions", []),
                current=bundle.get("inherited_permissions", []),
            ),
            "risk_flag_delta_from_previous": self._list_delta(
                previous=(latest or {}).get("risk_flags", []),
                current=bundle.get("risk_flags", []),
            ),
        }
        record["snapshot_signature"] = json.dumps(
            {
                key: value
                for key, value in record.items()
                if key not in {"artifact_id", "created_at", "snapshot_signature", "artifact_path", "report", "linked_report_ids"}
            },
            sort_keys=True,
        )
        return record

    def _write_record(self, payload: dict[str, Any]) -> dict[str, Any]:
        path = self.output_dir / f"{payload['artifact_id']}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        payload["artifact_path"] = str(path)
        report = build_extension_bundle_certification_report(artifacts_dir=self.artifacts_dir, record=payload)
        payload["report"] = report
        payload["linked_report_ids"] = sorted(set([*payload.get("adversary_review_report_ids", []), report["report_id"]]))
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload

    def _load_artifact(self, artifact_id: str) -> dict[str, Any] | None:
        path = self.output_dir / f"{artifact_id}.json"
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

    def _ensure_historical_lineage(self, *, bundle: dict[str, Any], recent_reviews: list[dict[str, Any]]) -> None:
        policy_lineage = list(((bundle.get("policy_lifecycle") or {}).get("lineage")) or [])
        if len(policy_lineage) <= 1:
            return
        relevant_reviews = self._relevant_reviews(bundle=bundle, recent_reviews=recent_reviews)
        previous: dict[str, Any] | None = None
        for index in range(len(policy_lineage) - 1, 0, -1):
            policy_item = policy_lineage[index]
            artifact_id = self._historical_artifact_id(
                bundle_id=str(bundle.get("bundle_id") or "unknown-bundle"),
                policy_set_id=str(policy_item.get("policy_set_id") or bundle.get("policy_set_id") or "unknown-policy"),
                policy_set_version=str(policy_item.get("version") or "unknown"),
            )
            visible_lineage = policy_lineage[index:]
            historical_bundle = self._historical_bundle(
                bundle=bundle,
                policy_item=policy_item,
                visible_lineage=visible_lineage,
            )
            payload = self._build_record(
                artifact_id=artifact_id,
                created_at=str(policy_item.get("retired_at") or policy_item.get("activated_at") or policy_item.get("created_at") or utcnow().isoformat()),
                bundle=historical_bundle,
                relevant_reviews=relevant_reviews,
                latest=previous,
                existing_lineage=[previous] if previous else [],
                historical_fixture=True,
            )
            existing = self._load_artifact(artifact_id)
            if existing and existing.get("snapshot_signature") == payload.get("snapshot_signature"):
                previous = existing
                continue
            previous = self._write_record(payload)

    def _historical_bundle(
        self,
        *,
        bundle: dict[str, Any],
        policy_item: dict[str, Any],
        visible_lineage: list[dict[str, Any]],
    ) -> dict[str, Any]:
        approval_decision = str(policy_item.get("approval_mode") or ((bundle.get("approval_path") or {}).get("decision")) or "allow")
        enabled_state = "disabled" if str(policy_item.get("status") or "") in {"held", "revoked"} else str(bundle.get("enabled_state") or "enabled")
        return {
            **bundle,
            "enabled_state": enabled_state,
            "bundle_family": policy_item.get("bundle_family") or bundle.get("bundle_family"),
            "policy_set_id": policy_item.get("policy_set_id") or bundle.get("policy_set_id"),
            "policy_set_version": policy_item.get("version") or bundle.get("policy_set_version"),
            "allowed_tools": list(policy_item.get("allowed_tools", bundle.get("allowed_tools", [])) or []),
            "inherited_permissions": list(policy_item.get("inherited_permissions", bundle.get("inherited_permissions", [])) or []),
            "risk_flags": list(policy_item.get("risk_flags", bundle.get("risk_flags", [])) or []),
            "approval_path": {"decision": approval_decision},
            "sandbox_posture": policy_item.get("sandbox_posture") or bundle.get("sandbox_posture"),
            "policy_lifecycle": {
                "status": policy_item.get("status"),
                "artifact_id": policy_item.get("artifact_id"),
                "report": policy_item.get("report"),
                "lineage": visible_lineage,
            },
        }

    def _restoration_targets(
        self,
        *,
        bundle: dict[str, Any],
        relevant_reviews: list[dict[str, Any]],
        historical_lineage: list[dict[str, Any]] | None = None,
    ) -> dict[str, list[str]]:
        if historical_lineage:
            blocked_or_revoked = [
                item
                for item in historical_lineage
                if item.get("artifact_id") and item.get("certification_status") in {"held", "revoked", "rolled_back"}
            ]
            return {
                "artifact_ids": [item.get("artifact_id") for item in blocked_or_revoked if item.get("artifact_id")],
                "statuses": [
                    item.get("certification_status")
                    for item in blocked_or_revoked
                    if item.get("certification_status")
                ],
            }
        artifact_ids: list[str] = []
        statuses: list[str] = []
        policy_lineage = list(((bundle.get("policy_lifecycle") or {}).get("lineage")) or [])
        for policy_item in policy_lineage[1:]:
            preview_bundle = self._historical_bundle(bundle=bundle, policy_item=policy_item, visible_lineage=[policy_item])
            preview_status = self._certification_status_preview(bundle=preview_bundle, relevant_reviews=relevant_reviews)
            if preview_status in {"held", "revoked", "rolled_back"}:
                artifact_ids.append(
                    self._historical_artifact_id(
                        bundle_id=str(bundle.get("bundle_id") or "unknown-bundle"),
                        policy_set_id=str(policy_item.get("policy_set_id") or bundle.get("policy_set_id") or "unknown-policy"),
                        policy_set_version=str(policy_item.get("version") or "unknown"),
                    )
                )
                statuses.append(preview_status)
        return {
            "artifact_ids": artifact_ids,
            "statuses": statuses,
        }

    def _certification_status_preview(self, *, bundle: dict[str, Any], relevant_reviews: list[dict[str, Any]]) -> str:
        privilege_inheritance_confusion = self._privilege_inheritance_confusion(bundle=bundle)
        return self._status(
            bundle=bundle,
            privilege_inheritance_confusion=privilege_inheritance_confusion,
            relevant_reviews=relevant_reviews,
        )

    def _historical_artifact_id(self, *, bundle_id: str, policy_set_id: str, policy_set_version: str) -> str:
        return (
            "bundlecerthist_"
            f"{self._slug(bundle_id)}_{self._slug(policy_set_id)}_{self._slug(policy_set_version)}"
        )

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

    def _slug(self, value: Any) -> str:
        return "".join(ch if str(ch).isalnum() else "_" for ch in str(value or "unknown")).strip("_").lower()

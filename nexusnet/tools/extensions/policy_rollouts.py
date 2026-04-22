from __future__ import annotations

from typing import Any


class PolicyRolloutService:
    def summary(self, *, records: list[dict[str, Any]]) -> dict[str, Any]:
        families: dict[str, list[dict[str, Any]]] = {}
        status_counts: dict[str, int] = {}
        for record in records:
            family = str(record.get("bundle_family") or "unknown-family")
            families.setdefault(family, []).append(record)
            status = str(record.get("status") or "draft")
            status_counts[status] = status_counts.get(status, 0) + 1
        items = [self._family_rollout(bundle_family=family, records=family_records) for family, family_records in sorted(families.items())]
        latest = items[0] if items else {}
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "family_count": len(items),
            "status_counts": status_counts,
            "latest_bundle_family": latest.get("bundle_family"),
            "latest_active_policy_set_id": latest.get("active_policy_set_id"),
            "latest_active_version": latest.get("active_version"),
            "items": items,
        }

    def detail(self, *, bundle_family: str, records: list[dict[str, Any]]) -> dict[str, Any] | None:
        family_records = [record for record in records if str(record.get("bundle_family")) == str(bundle_family)]
        if not family_records:
            return None
        return self._family_rollout(bundle_family=bundle_family, records=family_records)

    def _family_rollout(self, *, bundle_family: str, records: list[dict[str, Any]]) -> dict[str, Any]:
        ordered = sorted(
            records,
            key=lambda item: (
                str(item.get("activated_at") or item.get("created_at") or ""),
                str(item.get("created_at") or ""),
                str(item.get("version") or ""),
            ),
            reverse=True,
        )
        active = next((item for item in ordered if item.get("status") == "active"), None)
        shadow = [self._policy_ref(item) for item in ordered if item.get("status") == "shadow"]
        approved = [self._policy_ref(item) for item in ordered if item.get("status") == "approved"]
        rolled_back = [self._policy_ref(item) for item in ordered if item.get("status") == "rolled_back"]
        superseded = [self._policy_ref(item) for item in ordered if item.get("status") == "superseded"]
        held = [self._policy_ref(item) for item in ordered if item.get("status") == "held"]
        revoked = [self._policy_ref(item) for item in ordered if item.get("status") == "revoked"]
        latest = ordered[0] if ordered else {}
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "bundle_family": bundle_family,
            "policy_count": len(ordered),
            "active_policy_set_id": active.get("policy_set_id") if active else None,
            "active_version": active.get("version") if active else None,
            "active_artifact_id": active.get("artifact_id") if active else None,
            "latest_policy_set_id": latest.get("policy_set_id"),
            "latest_version": latest.get("version"),
            "latest_status": latest.get("status"),
            "shadow_candidates": shadow,
            "approved_candidates": approved,
            "rolled_back_versions": rolled_back,
            "superseded_versions": superseded,
            "held_versions": held,
            "revoked_versions": revoked,
            "lineage": [self._policy_ref(item) for item in ordered],
        }

    def _policy_ref(self, item: dict[str, Any]) -> dict[str, Any]:
        return {
            "policy_set_id": item.get("policy_set_id"),
            "version": item.get("version"),
            "status": item.get("status"),
            "artifact_id": item.get("artifact_id"),
            "report_id": ((item.get("report") or {}).get("report_id")),
            "rollback_reference": item.get("rollback_reference"),
        }

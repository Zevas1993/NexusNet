from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import new_id, utcnow
from .reports import build_execution_compare_report


class RecipeExecutionStore:
    def __init__(self, *, artifacts_dir: Path):
        self.artifacts_dir = Path(artifacts_dir)
        self.execution_dir = self.artifacts_dir / "recipes" / "executions"

    def record(
        self,
        *,
        recipe_id: str,
        execution_kind: str,
        ao_association: list[str] | None = None,
        trigger_source: str = "manual",
        parameter_set: dict[str, Any] | None = None,
        linked_trace_ids: list[str] | None = None,
        linked_subagent_ids: list[str] | None = None,
        policy_path: list[dict[str, Any]] | None = None,
        approval_path: dict[str, Any] | None = None,
        gateway_decision_path: list[dict[str, Any]] | None = None,
        gateway_resolution_id: str | None = None,
        gateway_execution_id: str | None = None,
        gateway_report_id: str | None = None,
        execution_path: list[dict[str, Any]] | None = None,
        approval_fallback_chain: list[dict[str, Any]] | None = None,
        adversary_review_report_ids: list[str] | None = None,
        linked_report_ids: list[str] | None = None,
        extension_bundle_ids: list[str] | None = None,
        extension_policy_set_ids: list[str] | None = None,
        extension_bundle_families: list[str] | None = None,
        extension_provenance: list[dict[str, Any]] | None = None,
        artifacts_produced: list[str] | None = None,
        status: str = "success",
        started_at: str | None = None,
        ended_at: str | None = None,
        schedule_id: str | None = None,
        report: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        execution_id = new_id("recipeexec")
        payload = {
            "execution_id": execution_id,
            "recipe_id": recipe_id,
            "execution_kind": execution_kind,
            "ao_association": list(ao_association or []),
            "trigger_source": trigger_source,
            "schedule_id": schedule_id,
            "parameter_set": parameter_set or {},
            "started_at": started_at or utcnow().isoformat(),
            "ended_at": ended_at or utcnow().isoformat(),
            "status": status,
            "linked_trace_ids": list(linked_trace_ids or []),
            "linked_subagent_ids": list(linked_subagent_ids or []),
            "policy_path": list(policy_path or []),
            "approval_path": approval_path or {},
            "gateway_decision_path": list(gateway_decision_path or []),
            "gateway_resolution_id": gateway_resolution_id,
            "gateway_execution_id": gateway_execution_id,
            "gateway_report_id": gateway_report_id,
            "execution_path": list(execution_path or []),
            "approval_fallback_chain": list(approval_fallback_chain or []),
            "adversary_review_report_ids": list(adversary_review_report_ids or []),
            "linked_report_ids": list(linked_report_ids or []),
            "extension_bundle_ids": list(extension_bundle_ids or []),
            "extension_policy_set_ids": list(extension_policy_set_ids or []),
            "extension_bundle_families": list(extension_bundle_families or []),
            "extension_provenance": list(extension_provenance or []),
            "artifacts_produced": list(artifacts_produced or []),
            "report": report or {},
            "metadata": metadata or {},
        }
        payload["flow_families"] = self._classify_flow_families(payload)
        payload["metadata"] = {
            **payload["metadata"],
            "flow_families": payload["flow_families"],
            "flow_family_count": len(payload["flow_families"]),
        }
        path = self.execution_dir / f"{execution_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        payload["artifact_path"] = str(path)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload

    def list_executions(
        self,
        *,
        execution_kind: str | None = None,
        recipe_id: str | None = None,
        schedule_id: str | None = None,
        trigger_source: str | None = None,
        status: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        if not self.execution_dir.exists():
            return records
        for path in sorted(self.execution_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if "flow_families" not in payload:
                payload["flow_families"] = self._classify_flow_families(payload)
            if execution_kind and payload.get("execution_kind") != execution_kind:
                continue
            if recipe_id and payload.get("recipe_id") != recipe_id:
                continue
            if schedule_id and payload.get("schedule_id") != schedule_id:
                continue
            if trigger_source and payload.get("trigger_source") != trigger_source:
                continue
            if status and payload.get("status") != status:
                continue
            records.append(payload)
            if len(records) >= limit:
                break
        return records

    def get(self, execution_id: str) -> dict[str, Any] | None:
        path = self.execution_dir / f"{execution_id}.json"
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        if "flow_families" not in payload:
            payload["flow_families"] = self._classify_flow_families(payload)
        return payload

    def compare(self, left_execution_id: str, right_execution_id: str) -> dict[str, Any] | None:
        left = self.get(left_execution_id)
        right = self.get(right_execution_id)
        if left is None or right is None:
            return None
        left_families = set(left.get("flow_families", []))
        right_families = set(right.get("flow_families", []))
        family_delta = [
            {
                "subject": family,
                "delta": (1 if family in right_families else 0) - (1 if family in left_families else 0),
            }
            for family in sorted(left_families | right_families)
            if family in left_families.symmetric_difference(right_families)
        ]
        left_bundle_ids = set(left.get("extension_bundle_ids", []))
        right_bundle_ids = set(right.get("extension_bundle_ids", []))
        left_policy_set_ids = set(left.get("extension_policy_set_ids", []))
        right_policy_set_ids = set(right.get("extension_policy_set_ids", []))
        left_bundle_families = set(left.get("extension_bundle_families", []))
        right_bundle_families = set(right.get("extension_bundle_families", []))
        left_adversary_ids = set(left.get("adversary_review_report_ids", []))
        right_adversary_ids = set(right.get("adversary_review_report_ids", []))
        left_artifacts = set(left.get("artifacts_produced", []))
        right_artifacts = set(right.get("artifacts_produced", []))
        left_traces = set(left.get("linked_trace_ids", []))
        right_traces = set(right.get("linked_trace_ids", []))
        left_reports = set(left.get("linked_report_ids", []))
        right_reports = set(right.get("linked_report_ids", []))
        metric_delta = {
            "artifact_count_delta": len(right_artifacts) - len(left_artifacts),
            "trace_count_delta": len(right_traces) - len(left_traces),
            "linked_report_count_delta": len(right_reports) - len(left_reports),
            "approval_chain_length_delta": len(right.get("approval_fallback_chain", [])) - len(left.get("approval_fallback_chain", [])),
        }
        diff = {
            "execution_kind_changed": left.get("execution_kind") != right.get("execution_kind"),
            "status_changed": left.get("status") != right.get("status"),
            "trigger_source_changed": left.get("trigger_source") != right.get("trigger_source"),
            "gateway_resolution_changed": left.get("gateway_resolution_id") != right.get("gateway_resolution_id"),
            "flow_families_added": sorted(right_families - left_families),
            "flow_families_removed": sorted(left_families - right_families),
            "extension_bundle_ids_added": sorted(right_bundle_ids - left_bundle_ids),
            "extension_bundle_ids_removed": sorted(left_bundle_ids - right_bundle_ids),
            "extension_policy_set_ids_added": sorted(right_policy_set_ids - left_policy_set_ids),
            "extension_policy_set_ids_removed": sorted(left_policy_set_ids - right_policy_set_ids),
            "extension_bundle_families_added": sorted(right_bundle_families - left_bundle_families),
            "extension_bundle_families_removed": sorted(left_bundle_families - right_bundle_families),
            "adversary_report_ids_added": sorted(right_adversary_ids - left_adversary_ids),
            "adversary_report_ids_removed": sorted(left_adversary_ids - right_adversary_ids),
            "artifacts_added": sorted(right_artifacts - left_artifacts),
            "artifacts_removed": sorted(left_artifacts - right_artifacts),
            "linked_trace_ids_added": sorted(right_traces - left_traces),
            "linked_trace_ids_removed": sorted(left_traces - right_traces),
            "linked_report_ids_added": sorted(right_reports - left_reports),
            "linked_report_ids_removed": sorted(left_reports - right_reports),
            **metric_delta,
        }
        export = build_execution_compare_report(
            artifacts_dir=self.artifacts_dir,
            left=self._compare_card(left),
            right=self._compare_card(right),
            diff=diff,
        )
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "left": self._compare_card(left),
            "right": self._compare_card(right),
            "scene_delta": {
                "refs": {
                    "left": left_execution_id,
                    "right": right_execution_id,
                },
                "hot_subjects": family_delta,
                "hot_links": [
                    {"link_id": key, "delta": value}
                    for key, value in metric_delta.items()
                    if value
                ],
            },
            "diff": diff,
            "export": export,
        }

    def _compare_card(self, payload: dict[str, Any]) -> dict[str, Any]:
        report = payload.get("report") or {}
        return {
            "execution_id": payload.get("execution_id"),
            "execution_kind": payload.get("execution_kind"),
            "recipe_id": payload.get("recipe_id"),
            "status": payload.get("status"),
            "trigger_source": payload.get("trigger_source"),
            "gateway_resolution_id": payload.get("gateway_resolution_id"),
            "gateway_report_id": payload.get("gateway_report_id") or report.get("report_id"),
            "flow_families": payload.get("flow_families", []),
            "extension_bundle_ids": payload.get("extension_bundle_ids", []),
            "extension_policy_set_ids": payload.get("extension_policy_set_ids", []),
            "extension_bundle_families": payload.get("extension_bundle_families", []),
            "linked_trace_ids": payload.get("linked_trace_ids", []),
            "linked_report_ids": payload.get("linked_report_ids", []),
            "adversary_review_report_ids": payload.get("adversary_review_report_ids", []),
            "artifacts_produced": payload.get("artifacts_produced", []),
            "report_id": report.get("report_id"),
        }

    def _classify_flow_families(self, payload: dict[str, Any]) -> list[str]:
        families: set[str] = set()
        execution_kind = str(payload.get("execution_kind") or "")
        trigger_source = str(payload.get("trigger_source") or "")
        parameter_set = payload.get("parameter_set") or {}
        metadata = payload.get("metadata") or {}
        requested_tools = list(parameter_set.get("requested_tools") or [])
        effective_requested_tools = list(parameter_set.get("effective_requested_tools") or [])
        requested_extensions = list(parameter_set.get("requested_extensions") or metadata.get("requested_extensions") or [])
        bundle_families = {
            str(item)
            for item in [*(payload.get("extension_bundle_families") or []), *(metadata.get("extension_bundle_families") or [])]
            if item
        }
        approval_path = payload.get("approval_path") or {}
        approval_fallback_chain = payload.get("approval_fallback_chain") or []
        if execution_kind == "recipe":
            families.add("recipe-driven")
        elif execution_kind == "runbook":
            families.add("runbook-driven")
        elif execution_kind == "gateway":
            families.update({"gateway-controlled", "gateway-only"})
        if payload.get("gateway_resolution_id") or payload.get("gateway_decision_path"):
            families.add("gateway-controlled")
        if (
            payload.get("linked_subagent_ids")
            or trigger_source.startswith("subagent-plan:")
            or trigger_source.startswith("delegation:")
            or trigger_source.startswith("parallel:")
        ):
            families.add("subagent-delegation")
        if requested_extensions and not requested_tools:
            families.add("extension-only")
        if payload.get("schedule_id") or trigger_source.startswith("schedule:") or trigger_source.startswith("scheduled:"):
            families.add("scheduled")
        if (
            "provider.acp" in set([*requested_tools, *effective_requested_tools])
            or "acp-provider-lane" in bundle_families
            or any(str(extension_id).startswith("acp-") for extension_id in requested_extensions)
            or "acp" in trigger_source
        ):
            families.add("acp-bridged")
        if (
            approval_path.get("decision") in {"ask", "allow-if-approved"}
            or payload.get("status") == "approval-pending"
            or payload.get("adversary_review_report_ids")
            or any(
                step.get("decision") not in {None, "allow"}
                for step in approval_fallback_chain
                if step.get("stage") in {"permission", "adversary-review"}
            )
        ):
            families.add("approval-heavy")
        return sorted(families)
